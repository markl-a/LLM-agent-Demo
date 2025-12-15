"""速率限制模組 - 實現令牌桶和滑動窗口算法

本模組提供了兩種主要的速率限制算法：
1. Token Bucket（令牌桶）：適合處理突發流量
2. Sliding Window（滑動窗口）：提供更精確的速率限制

使用方式：
    from llm_agent_demo.utils.rate_limiter import rate_limit, RateLimiter

    # 使用裝飾器
    @rate_limit(max_calls=10, window_seconds=60, strategy="token_bucket")
    def my_api_call():
        pass

    # 直接使用類
    limiter = RateLimiter(max_calls=10, window_seconds=60)
    if limiter.allow_request("user_123"):
        # 執行請求
        pass
"""

import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
from typing import Any, Callable, Deque, Dict, Optional, Union

from .exceptions import RateLimitError
from .logger import get_logger

logger = get_logger(__name__)


class RateLimitStrategy(str, Enum):
    """速率限制策略枚舉"""

    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"


@dataclass
class TokenBucket:
    """令牌桶實現

    令牌桶算法允許一定程度的突發流量，同時保證平均速率不超過限制。

    Attributes:
        capacity: 桶的容量（最大令牌數）
        refill_rate: 令牌補充速率（每秒補充的令牌數）
        tokens: 當前令牌數
        last_refill_time: 上次補充令牌的時間
        lock: 線程鎖
    """

    capacity: float
    refill_rate: float
    tokens: float = field(init=False)
    last_refill_time: float = field(init=False)
    lock: threading.Lock = field(default_factory=threading.Lock)

    def __post_init__(self):
        """初始化時桶是滿的"""
        self.tokens = self.capacity
        self.last_refill_time = time.time()

    def _refill(self) -> None:
        """補充令牌"""
        now = time.time()
        time_passed = now - self.last_refill_time
        new_tokens = time_passed * self.refill_rate

        # 更新令牌數，不超過容量
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_refill_time = now

    def consume(self, tokens: float = 1.0) -> bool:
        """消費令牌

        Args:
            tokens: 要消費的令牌數

        Returns:
            如果成功消費返回 True，否則返回 False
        """
        with self.lock:
            self._refill()

            if self.tokens >= tokens:
                self.tokens -= tokens
                logger.debug(f"Token consumed. Remaining tokens: {self.tokens:.2f}")
                return True

            logger.debug(f"Insufficient tokens. Required: {tokens}, Available: {self.tokens:.2f}")
            return False

    def get_wait_time(self, tokens: float = 1.0) -> float:
        """獲取需要等待的時間

        Args:
            tokens: 需要的令牌數

        Returns:
            需要等待的秒數
        """
        with self.lock:
            self._refill()

            if self.tokens >= tokens:
                return 0.0

            # 計算需要等待多久才能獲得足夠的令牌
            tokens_needed = tokens - self.tokens
            wait_time = tokens_needed / self.refill_rate
            return wait_time

    def reset(self) -> None:
        """重置令牌桶"""
        with self.lock:
            self.tokens = self.capacity
            self.last_refill_time = time.time()


@dataclass
class SlidingWindow:
    """滑動窗口實現

    滑動窗口算法提供更精確的速率限制，記錄每次請求的時間戳。

    Attributes:
        max_requests: 時間窗口內允許的最大請求數
        window_seconds: 時間窗口大小（秒）
        requests: 請求時間戳隊列
        lock: 線程鎖
    """

    max_requests: int
    window_seconds: float
    requests: Deque[float] = field(default_factory=deque)
    lock: threading.Lock = field(default_factory=threading.Lock)

    def _clean_old_requests(self) -> None:
        """清除時間窗口外的舊請求"""
        now = time.time()
        window_start = now - self.window_seconds

        while self.requests and self.requests[0] < window_start:
            self.requests.popleft()

    def allow_request(self) -> bool:
        """檢查是否允許請求

        Returns:
            如果允許請求返回 True，否則返回 False
        """
        with self.lock:
            self._clean_old_requests()

            if len(self.requests) < self.max_requests:
                self.requests.append(time.time())
                logger.debug(f"Request allowed. Count: {len(self.requests)}/{self.max_requests}")
                return True

            logger.debug(f"Request denied. Limit reached: {len(self.requests)}/{self.max_requests}")
            return False

    def get_wait_time(self) -> float:
        """獲取需要等待的時間

        Returns:
            需要等待的秒數
        """
        with self.lock:
            self._clean_old_requests()

            if len(self.requests) < self.max_requests:
                return 0.0

            # 計算最早的請求何時過期
            oldest_request = self.requests[0]
            wait_time = (oldest_request + self.window_seconds) - time.time()
            return max(0.0, wait_time)

    def get_current_count(self) -> int:
        """獲取當前時間窗口內的請求數"""
        with self.lock:
            self._clean_old_requests()
            return len(self.requests)

    def reset(self) -> None:
        """重置滑動窗口"""
        with self.lock:
            self.requests.clear()


class RateLimiter:
    """速率限制器

    支援多種限制策略和按用戶/API key 分組限制。

    Args:
        max_calls: 時間窗口內允許的最大調用次數
        window_seconds: 時間窗口大小（秒）
        strategy: 限制策略（token_bucket 或 sliding_window）

    Example:
        >>> limiter = RateLimiter(max_calls=10, window_seconds=60)
        >>> if limiter.allow_request("user_123"):
        ...     # 執行請求
        ...     pass
    """

    def __init__(
        self,
        max_calls: int,
        window_seconds: float,
        strategy: Union[RateLimitStrategy, str] = RateLimitStrategy.TOKEN_BUCKET,
    ):
        self.max_calls = max_calls
        self.window_seconds = window_seconds

        # 轉換策略為枚舉
        if isinstance(strategy, str):
            strategy = RateLimitStrategy(strategy.lower())
        self.strategy = strategy

        # 存儲每個標識符（用戶/API key）的限制器
        self._limiters: Dict[str, Union[TokenBucket, SlidingWindow]] = {}
        self._lock = threading.Lock()

        logger.info(
            f"RateLimiter initialized: {max_calls} calls per {window_seconds}s "
            f"using {strategy.value} strategy"
        )

    def _get_limiter(self, identifier: str) -> Union[TokenBucket, SlidingWindow]:
        """獲取或創建指定標識符的限制器

        Args:
            identifier: 用戶 ID 或 API key

        Returns:
            對應的限制器實例
        """
        if identifier not in self._limiters:
            with self._lock:
                # 雙重檢查鎖
                if identifier not in self._limiters:
                    if self.strategy == RateLimitStrategy.TOKEN_BUCKET:
                        # 令牌桶：refill_rate = max_calls / window_seconds
                        refill_rate = self.max_calls / self.window_seconds
                        self._limiters[identifier] = TokenBucket(
                            capacity=self.max_calls,
                            refill_rate=refill_rate,
                        )
                    else:  # SLIDING_WINDOW
                        self._limiters[identifier] = SlidingWindow(
                            max_requests=self.max_calls,
                            window_seconds=self.window_seconds,
                        )

                    logger.debug(f"Created new {self.strategy.value} limiter for: {identifier}")

        return self._limiters[identifier]

    def allow_request(
        self,
        identifier: str,
        tokens: float = 1.0,
        raise_on_limit: bool = False,
    ) -> bool:
        """檢查是否允許請求

        Args:
            identifier: 用戶 ID 或 API key
            tokens: 要消費的令牌數（僅用於令牌桶策略）
            raise_on_limit: 如果達到限制是否拋出異常

        Returns:
            如果允許請求返回 True，否則返回 False

        Raises:
            RateLimitError: 如果 raise_on_limit=True 且達到限制
        """
        limiter = self._get_limiter(identifier)

        if self.strategy == RateLimitStrategy.TOKEN_BUCKET:
            allowed = limiter.consume(tokens)
        else:  # SLIDING_WINDOW
            allowed = limiter.allow_request()

        if not allowed:
            wait_time = self.get_wait_time(identifier, tokens)
            retry_after = datetime.now() + timedelta(seconds=wait_time)

            logger.warning(
                f"Rate limit exceeded for {identifier}. "
                f"Retry after {wait_time:.2f}s ({retry_after.isoformat()})"
            )

            if raise_on_limit:
                raise RateLimitError(
                    f"Rate limit exceeded. Retry after {wait_time:.2f} seconds",
                    retry_after=retry_after,
                )

        return allowed

    def get_wait_time(self, identifier: str, tokens: float = 1.0) -> float:
        """獲取需要等待的時間

        Args:
            identifier: 用戶 ID 或 API key
            tokens: 需要的令牌數（僅用於令牌桶策略）

        Returns:
            需要等待的秒數
        """
        limiter = self._get_limiter(identifier)

        if self.strategy == RateLimitStrategy.TOKEN_BUCKET:
            return limiter.get_wait_time(tokens)
        else:  # SLIDING_WINDOW
            return limiter.get_wait_time()

    def get_status(self, identifier: str) -> Dict[str, Any]:
        """獲取限制器狀態

        Args:
            identifier: 用戶 ID 或 API key

        Returns:
            包含狀態信息的字典
        """
        limiter = self._get_limiter(identifier)

        status = {
            "identifier": identifier,
            "strategy": self.strategy.value,
            "max_calls": self.max_calls,
            "window_seconds": self.window_seconds,
        }

        if self.strategy == RateLimitStrategy.TOKEN_BUCKET:
            with limiter.lock:
                limiter._refill()
                status["available_tokens"] = limiter.tokens
                status["capacity"] = limiter.capacity
                status["refill_rate"] = limiter.refill_rate
        else:  # SLIDING_WINDOW
            current_count = limiter.get_current_count()
            status["current_requests"] = current_count
            status["remaining_requests"] = self.max_calls - current_count

        return status

    def reset(self, identifier: Optional[str] = None) -> None:
        """重置限制器

        Args:
            identifier: 如果指定，只重置該標識符的限制器；否則重置所有
        """
        if identifier:
            if identifier in self._limiters:
                self._limiters[identifier].reset()
                logger.info(f"Reset limiter for: {identifier}")
        else:
            with self._lock:
                for limiter in self._limiters.values():
                    limiter.reset()
                logger.info("Reset all limiters")

    def cleanup_expired(self, inactive_seconds: float = 3600) -> int:
        """清理不活躍的限制器

        Args:
            inactive_seconds: 不活躍時間閾值（秒）

        Returns:
            清理的限制器數量
        """
        with self._lock:
            now = time.time()
            to_remove = []

            for identifier, limiter in self._limiters.items():
                if self.strategy == RateLimitStrategy.TOKEN_BUCKET:
                    # 檢查令牌桶的最後更新時間
                    if now - limiter.last_refill_time > inactive_seconds:
                        to_remove.append(identifier)
                else:  # SLIDING_WINDOW
                    # 檢查滑動窗口是否有最近的請求
                    if not limiter.requests or (now - limiter.requests[-1] > inactive_seconds):
                        to_remove.append(identifier)

            for identifier in to_remove:
                del self._limiters[identifier]

            if to_remove:
                logger.info(f"Cleaned up {len(to_remove)} inactive limiters")

            return len(to_remove)


def rate_limit(
    max_calls: int,
    window_seconds: float,
    strategy: Union[RateLimitStrategy, str] = RateLimitStrategy.TOKEN_BUCKET,
    identifier_key: Optional[str] = None,
    tokens_key: Optional[str] = None,
    raise_on_limit: bool = True,
) -> Callable:
    """速率限制裝飾器

    可以應用於函數或方法，自動進行速率限制檢查。

    Args:
        max_calls: 時間窗口內允許的最大調用次數
        window_seconds: 時間窗口大小（秒）
        strategy: 限制策略
        identifier_key: 從函數參數中提取標識符的鍵名（如 "user_id", "api_key"）
        tokens_key: 從函數參數中提取令牌數的鍵名（僅用於令牌桶策略）
        raise_on_limit: 如果達到限制是否拋出異常

    Example:
        >>> @rate_limit(max_calls=10, window_seconds=60, identifier_key="user_id")
        ... def api_call(user_id: str, data: dict):
        ...     return process_data(data)

        >>> @rate_limit(
        ...     max_calls=100,
        ...     window_seconds=60,
        ...     strategy="sliding_window",
        ...     identifier_key="api_key"
        ... )
        ... def expensive_operation(api_key: str, query: str):
        ...     return search(query)
    """
    limiter = RateLimiter(max_calls, window_seconds, strategy)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # 提取標識符
            identifier = "default"
            if identifier_key:
                identifier = kwargs.get(identifier_key)
                if identifier is None and args:
                    # 嘗試從位置參數中獲取
                    # 這需要知道參數順序，簡單起見只檢查 kwargs
                    pass

            # 提取令牌數
            tokens = 1.0
            if tokens_key:
                tokens = kwargs.get(tokens_key, 1.0)

            # 檢查速率限制
            if not limiter.allow_request(
                identifier=identifier,
                tokens=tokens,
                raise_on_limit=raise_on_limit,
            ):
                wait_time = limiter.get_wait_time(identifier, tokens)
                logger.warning(
                    f"Rate limit exceeded for {func.__name__}. "
                    f"Wait {wait_time:.2f}s before retry."
                )

                if not raise_on_limit:
                    return None

            # 執行原函數
            return func(*args, **kwargs)

        # 添加速率限制器的引用，方便測試和管理
        wrapper.rate_limiter = limiter
        return wrapper

    return decorator


class GlobalRateLimiter:
    """全局速率限制器

    管理多個不同的速率限制器，用於不同的 API 端點或資源。

    Example:
        >>> global_limiter = GlobalRateLimiter()
        >>> global_limiter.add_limiter(
        ...     "api_v1",
        ...     max_calls=100,
        ...     window_seconds=60
        ... )
        >>> if global_limiter.allow_request("api_v1", "user_123"):
        ...     # 執行請求
        ...     pass
    """

    def __init__(self):
        self._limiters: Dict[str, RateLimiter] = {}
        self._lock = threading.Lock()

    def add_limiter(
        self,
        name: str,
        max_calls: int,
        window_seconds: float,
        strategy: Union[RateLimitStrategy, str] = RateLimitStrategy.TOKEN_BUCKET,
    ) -> RateLimiter:
        """添加一個命名的限制器

        Args:
            name: 限制器名稱
            max_calls: 時間窗口內允許的最大調用次數
            window_seconds: 時間窗口大小（秒）
            strategy: 限制策略

        Returns:
            創建的 RateLimiter 實例
        """
        with self._lock:
            limiter = RateLimiter(max_calls, window_seconds, strategy)
            self._limiters[name] = limiter
            logger.info(f"Added rate limiter: {name}")
            return limiter

    def get_limiter(self, name: str) -> Optional[RateLimiter]:
        """獲取指定名稱的限制器

        Args:
            name: 限制器名稱

        Returns:
            RateLimiter 實例或 None
        """
        return self._limiters.get(name)

    def allow_request(
        self,
        limiter_name: str,
        identifier: str,
        tokens: float = 1.0,
        raise_on_limit: bool = False,
    ) -> bool:
        """檢查是否允許請求

        Args:
            limiter_name: 限制器名稱
            identifier: 用戶 ID 或 API key
            tokens: 要消費的令牌數
            raise_on_limit: 如果達到限制是否拋出異常

        Returns:
            如果允許請求返回 True，否則返回 False
        """
        limiter = self._limiters.get(limiter_name)
        if not limiter:
            logger.warning(f"Rate limiter not found: {limiter_name}")
            return True  # 如果沒有配置限制器，允許請求

        return limiter.allow_request(identifier, tokens, raise_on_limit)

    def get_status(self, limiter_name: str, identifier: str) -> Optional[Dict[str, Any]]:
        """獲取限制器狀態

        Args:
            limiter_name: 限制器名稱
            identifier: 用戶 ID 或 API key

        Returns:
            狀態信息字典或 None
        """
        limiter = self._limiters.get(limiter_name)
        if not limiter:
            return None

        return limiter.get_status(identifier)

    def reset(self, limiter_name: Optional[str] = None, identifier: Optional[str] = None) -> None:
        """重置限制器

        Args:
            limiter_name: 如果指定，只重置該限制器；否則重置所有
            identifier: 如果指定，只重置該標識符；否則重置所有標識符
        """
        if limiter_name:
            limiter = self._limiters.get(limiter_name)
            if limiter:
                limiter.reset(identifier)
        else:
            for limiter in self._limiters.values():
                limiter.reset(identifier)

    def cleanup_all(self, inactive_seconds: float = 3600) -> int:
        """清理所有限制器中不活躍的條目

        Args:
            inactive_seconds: 不活躍時間閾值（秒）

        Returns:
            總共清理的條目數量
        """
        total_cleaned = 0
        for limiter in self._limiters.values():
            total_cleaned += limiter.cleanup_expired(inactive_seconds)

        return total_cleaned


# 創建全局實例
_global_rate_limiter = GlobalRateLimiter()


def get_global_limiter() -> GlobalRateLimiter:
    """獲取全局速率限制器實例

    Returns:
        GlobalRateLimiter 實例
    """
    return _global_rate_limiter

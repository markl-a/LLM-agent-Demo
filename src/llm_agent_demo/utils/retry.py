"""重試機制模組 - 提供指數退避重試功能"""

import time
import functools
from typing import Callable, Type, Tuple, Optional, Any
import logging

logger = logging.getLogger(__name__)


def retry_with_exponential_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    exponential_base: float = 2.0,
    max_delay: float = 60.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable[[Exception, int], None]] = None,
):
    """
    指數退避重試裝飾器

    當函數因指定的異常失敗時，會使用指數退避策略自動重試。

    Args:
        max_retries: 最大重試次數
        initial_delay: 初始延遲時間（秒）
        exponential_base: 指數基數
        max_delay: 最大延遲時間（秒）
        exceptions: 需要重試的異常類型元組
        on_retry: 重試時的回調函數，接收 (exception, retry_count) 參數

    Returns:
        裝飾器函數

    使用示例:
        @retry_with_exponential_backoff(max_retries=3, initial_delay=1.0)
        def call_api():
            # API 調用代碼
            pass
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            delay = initial_delay
            last_exception = None

            for retry_count in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if retry_count == max_retries:
                        logger.error(
                            f"函數 {func.__name__} 在 {max_retries} 次重試後仍然失敗: {e}"
                        )
                        raise

                    # 調用回調函數
                    if on_retry:
                        on_retry(e, retry_count + 1)
                    else:
                        logger.warning(
                            f"函數 {func.__name__} 失敗 (嘗試 {retry_count + 1}/{max_retries}): {e}. "
                            f"將在 {delay:.2f} 秒後重試..."
                        )

                    # 等待
                    time.sleep(delay)

                    # 計算下次延遲（指數退避）
                    delay = min(delay * exponential_base, max_delay)

            # 不應該到達這裡，但以防萬一
            if last_exception:
                raise last_exception

        return wrapper

    return decorator


def retry_on_rate_limit(
    max_retries: int = 5, initial_delay: float = 1.0, exponential_base: float = 2.0
):
    """
    專門用於處理 API 速率限制的重試裝飾器

    Args:
        max_retries: 最大重試次數
        initial_delay: 初始延遲時間（秒）
        exponential_base: 指數基數

    Returns:
        裝飾器函數
    """

    def on_retry_callback(exception: Exception, retry_count: int):
        """重試回調，提供更詳細的速率限制信息"""
        logger.warning(
            f"遇到速率限制錯誤 (嘗試 {retry_count}/{max_retries}): {exception}. "
            f"建議降低請求頻率或升級 API 方案。"
        )

    # 常見的速率限制異常
    rate_limit_exceptions = (
        Exception,  # 基礎異常，實際使用時應該更具體
    )

    # 嘗試導入具體的異常類型
    try:
        from openai import RateLimitError as OpenAIRateLimitError

        rate_limit_exceptions += (OpenAIRateLimitError,)
    except ImportError:
        pass

    try:
        from anthropic import RateLimitError as AnthropicRateLimitError

        rate_limit_exceptions += (AnthropicRateLimitError,)
    except ImportError:
        pass

    return retry_with_exponential_backoff(
        max_retries=max_retries,
        initial_delay=initial_delay,
        exponential_base=exponential_base,
        max_delay=300.0,  # 最多等待 5 分鐘
        exceptions=rate_limit_exceptions,
        on_retry=on_retry_callback,
    )


def retry_on_network_error(max_retries: int = 3, initial_delay: float = 0.5):
    """
    專門用於處理網絡錯誤的重試裝飾器

    Args:
        max_retries: 最大重試次數
        initial_delay: 初始延遲時間（秒）

    Returns:
        裝飾器函數
    """
    import socket
    from urllib.error import URLError

    network_exceptions = (
        ConnectionError,
        TimeoutError,
        socket.timeout,
        URLError,
    )

    # 嘗試導入 requests 異常
    try:
        import requests

        network_exceptions += (
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
        )
    except ImportError:
        pass

    # 嘗試導入 httpx 異常
    try:
        import httpx

        network_exceptions += (
            httpx.ConnectError,
            httpx.TimeoutException,
        )
    except ImportError:
        pass

    def on_retry_callback(exception: Exception, retry_count: int):
        """重試回調"""
        logger.warning(
            f"網絡錯誤 (嘗試 {retry_count}/{max_retries}): {exception}. " f"檢查網絡連接..."
        )

    return retry_with_exponential_backoff(
        max_retries=max_retries,
        initial_delay=initial_delay,
        exponential_base=2.0,
        max_delay=30.0,
        exceptions=network_exceptions,
        on_retry=on_retry_callback,
    )


class RetryContext:
    """
    重試上下文管理器 - 用於更靈活的重試控制

    使用示例:
        retry_ctx = RetryContext(max_retries=3, initial_delay=1.0)

        for attempt in retry_ctx:
            try:
                result = call_api()
                break  # 成功，退出重試
            except Exception as e:
                retry_ctx.handle_exception(e)

        # 檢查是否成功
        if retry_ctx.succeeded:
            print(f"成功！結果: {result}")
        else:
            print(f"失敗！最後的錯誤: {retry_ctx.last_exception}")
    """

    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        exponential_base: float = 2.0,
        max_delay: float = 60.0,
    ):
        """
        初始化重試上下文

        Args:
            max_retries: 最大重試次數
            initial_delay: 初始延遲時間（秒）
            exponential_base: 指數基數
            max_delay: 最大延遲時間（秒）
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.exponential_base = exponential_base
        self.max_delay = max_delay

        self.current_retry = 0
        self.delay = initial_delay
        self.last_exception: Optional[Exception] = None
        self.succeeded = False

    def __iter__(self):
        """迭代器初始化"""
        self.current_retry = 0
        self.delay = self.initial_delay
        return self

    def __next__(self):
        """獲取下一次重試"""
        if self.current_retry > self.max_retries:
            raise StopIteration

        attempt = self.current_retry
        self.current_retry += 1

        return attempt

    def handle_exception(self, exception: Exception) -> None:
        """
        處理異常

        Args:
            exception: 捕獲的異常

        Raises:
            Exception: 如果已達到最大重試次數，重新拋出異常
        """
        self.last_exception = exception

        if self.current_retry > self.max_retries:
            logger.error(f"達到最大重試次數 ({self.max_retries})，放棄重試: {exception}")
            raise exception

        logger.warning(
            f"重試 {self.current_retry}/{self.max_retries} 失敗: {exception}. "
            f"將在 {self.delay:.2f} 秒後重試..."
        )

        time.sleep(self.delay)
        self.delay = min(self.delay * self.exponential_base, self.max_delay)

    def mark_success(self) -> None:
        """標記為成功"""
        self.succeeded = True

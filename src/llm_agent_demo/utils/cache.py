"""快取系統模組 - 提供記憶體和檔案快取功能"""

import functools
import hashlib
import json
import pickle
import time
from pathlib import Path
from threading import Lock
from typing import Any, Callable, Dict, Optional, Union
from abc import ABC, abstractmethod
from collections import OrderedDict

from .logger import get_logger
from .exceptions import DataError

logger = get_logger(__name__)


class CacheEntry:
    """快取項目，包含數據和過期時間"""

    def __init__(self, value: Any, ttl: Optional[float] = None):
        """
        初始化快取項目

        Args:
            value: 快取的值
            ttl: 過期時間（秒），None 表示永不過期
        """
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl

    def is_expired(self) -> bool:
        """檢查是否過期"""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl

    def remaining_ttl(self) -> Optional[float]:
        """返回剩餘的TTL時間"""
        if self.ttl is None:
            return None
        remaining = self.ttl - (time.time() - self.created_at)
        return max(0, remaining)


class BaseCache(ABC):
    """快取基礎類別"""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """獲取快取值"""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """設置快取值"""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """刪除快取值"""
        pass

    @abstractmethod
    def clear(self) -> None:
        """清空所有快取"""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """檢查鍵是否存在"""
        pass


class MemoryCache(BaseCache):
    """記憶體快取實現

    使用 OrderedDict 存儲快取數據，支援 TTL 過期機制和容量限制。
    實現了高效的 LRU (Least Recently Used) 驅逐策略，時間複雜度 O(1)。
    線程安全，適合單機應用的快取需求。

    Example:
        >>> cache = MemoryCache(default_ttl=300, max_size=1000)
        >>> cache.set("user:123", {"name": "Alice"}, ttl=60)
        >>> user = cache.get("user:123")
        >>> print(user)  # {"name": "Alice"}
    """

    def __init__(self, default_ttl: Optional[float] = None, max_size: Optional[int] = None):
        """
        初始化記憶體快取

        Args:
            default_ttl: 預設過期時間（秒），None 表示永不過期
            max_size: 最大快取項目數量，None 表示無限制
        """
        # 使用 OrderedDict 實現 O(1) 的 LRU 驅逐策略
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = Lock()
        self.default_ttl = default_ttl
        self.max_size = max_size
        self._hits = 0
        self._misses = 0

        logger.info(f"初始化記憶體快取 - TTL: {default_ttl}, Max Size: {max_size}")

    def get(self, key: str) -> Optional[Any]:
        """
        獲取快取值

        Args:
            key: 快取鍵

        Returns:
            快取的值，如果不存在或已過期則返回 None
        """
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                logger.debug(f"快取未命中: {key}")
                return None

            entry = self._cache[key]

            # 檢查是否過期
            if entry.is_expired():
                del self._cache[key]
                self._misses += 1
                logger.debug(f"快取已過期: {key}")
                return None

            # LRU 策略：將最近訪問的項目移到末尾（O(1) 操作）
            self._cache.move_to_end(key)

            self._hits += 1
            logger.debug(f"快取命中: {key}")
            return entry.value

    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """
        設置快取值

        Args:
            key: 快取鍵
            value: 要快取的值
            ttl: 過期時間（秒），覆蓋預設 TTL
        """
        with self._lock:
            # 如果達到最大容量且是新鍵，移除最舊的項目
            if self.max_size and len(self._cache) >= self.max_size and key not in self._cache:
                self._evict_oldest()

            ttl = ttl if ttl is not None else self.default_ttl
            self._cache[key] = CacheEntry(value, ttl)

            # LRU 策略：將新設置或更新的項目移到末尾（O(1) 操作）
            self._cache.move_to_end(key)

            logger.debug(f"設置快取: {key}, TTL: {ttl}")

    def delete(self, key: str) -> bool:
        """
        刪除快取值

        Args:
            key: 快取鍵

        Returns:
            如果鍵存在並被刪除返回 True，否則返回 False
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                logger.debug(f"刪除快取: {key}")
                return True
            return False

    def clear(self) -> None:
        """清空所有快取"""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            self._hits = 0
            self._misses = 0
            logger.info(f"清空快取 - 刪除 {count} 個項目")

    def exists(self, key: str) -> bool:
        """
        檢查鍵是否存在且未過期

        Args:
            key: 快取鍵

        Returns:
            如果鍵存在且未過期返回 True，否則返回 False
        """
        with self._lock:
            if key not in self._cache:
                return False

            entry = self._cache[key]
            if entry.is_expired():
                del self._cache[key]
                return False

            return True

    def _evict_oldest(self) -> None:
        """
        移除最舊的快取項目（LRU 策略）- O(1) 時間複雜度

        使用 OrderedDict.popitem(last=False) 直接移除最舊（最前面）的項目，
        相比之前的 O(n) min() 操作，性能顯著提升。
        """
        if not self._cache:
            return

        # O(1) 操作：移除最舊（最前面）的項目
        oldest_key, _ = self._cache.popitem(last=False)
        logger.debug(f"移除最舊快取項目: {oldest_key}")

    def cleanup_expired(self) -> int:
        """
        清理所有過期的快取項目

        Returns:
            清理的項目數量
        """
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]

            for key in expired_keys:
                del self._cache[key]

            if expired_keys:
                logger.info(f"清理 {len(expired_keys)} 個過期快取項目")

            return len(expired_keys)

    def get_stats(self) -> Dict[str, Any]:
        """
        獲取快取統計資訊

        Returns:
            包含統計數據的字典
        """
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests > 0 else 0

            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": hit_rate,
                "total_requests": total_requests,
            }


class FileCache(BaseCache):
    """檔案快取實現

    將快取數據序列化到檔案系統，支援 JSON 序列化方式（推薦）。
    pickle 已棄用（安全風險：RCE 漏洞）。
    適合需要持久化或跨進程共享的快取場景。

    Example:
        >>> cache = FileCache("/tmp/cache", default_ttl=3600, serializer="json")
        >>> cache.set("result", {"data": [1, 2, 3]})
        >>> result = cache.get("result")
    """

    def __init__(
        self,
        cache_dir: Union[str, Path],
        default_ttl: Optional[float] = None,
        serializer: str = "json"
    ):
        """
        初始化檔案快取

        Args:
            cache_dir: 快取目錄路徑
            default_ttl: 預設過期時間（秒）
            serializer: 序列化方式（推薦使用 "json"，"pickle" 已棄用）
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_ttl = default_ttl
        self._lock = Lock()

        if serializer not in ["pickle", "json"]:
            raise ValueError(f"不支援的序列化方式: {serializer}")

        # 安全警告：pickle 已棄用
        if serializer == "pickle":
            logger.warning(
                "WARNING: pickle serialization is deprecated due to RCE security risks. "
                "Please migrate to 'json' serializer. "
                "Automatically using 'json' instead for security."
            )
            self.serializer = "json"
        else:
            self.serializer = serializer

        logger.info(f"初始化檔案快取 - 目錄: {self.cache_dir}, 序列化: {self.serializer}")

    def _get_cache_path(self, key: str) -> Path:
        """根據鍵生成快取檔案路徑"""
        # 使用 SHA256 hash 作為檔案名，避免非法字符
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"

    def _serialize(self, data: Any) -> bytes:
        """序列化數據（僅支援 JSON）"""
        try:
            return json.dumps(data).encode('utf-8')
        except (TypeError, ValueError) as e:
            logger.error(f"JSON 序列化失敗: {e}")
            raise DataError(f"序列化失敗: {e}") from e

    def _deserialize(self, data: bytes) -> Any:
        """反序列化數據（僅支援 JSON）"""
        try:
            return json.loads(data.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.error(f"JSON 反序列化失敗: {e}")
            raise DataError(f"反序列化失敗: {e}") from e

    def get(self, key: str) -> Optional[Any]:
        """
        獲取快取值

        Args:
            key: 快取鍵

        Returns:
            快取的值，如果不存在或已過期則返回 None
        """
        cache_path = self._get_cache_path(key)

        with self._lock:
            if not cache_path.exists():
                logger.debug(f"快取檔案不存在: {key}")
                return None

            try:
                with open(cache_path, 'rb') as f:
                    cache_data = self._deserialize(f.read())

                entry = CacheEntry(
                    value=cache_data['value'],
                    ttl=cache_data.get('ttl')
                )
                entry.created_at = cache_data['created_at']

                # 檢查是否過期
                if entry.is_expired():
                    cache_path.unlink()
                    logger.debug(f"快取已過期: {key}")
                    return None

                logger.debug(f"快取命中: {key}")
                return entry.value

            except Exception as e:
                logger.error(f"讀取快取失敗 {key}: {e}")
                return None

    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """
        設置快取值

        Args:
            key: 快取鍵
            value: 要快取的值
            ttl: 過期時間（秒），覆蓋預設 TTL
        """
        cache_path = self._get_cache_path(key)
        ttl = ttl if ttl is not None else self.default_ttl

        cache_data = {
            'value': value,
            'created_at': time.time(),
            'ttl': ttl
        }

        with self._lock:
            try:
                with open(cache_path, 'wb') as f:
                    f.write(self._serialize(cache_data))
                logger.debug(f"設置快取: {key}, TTL: {ttl}")
            except Exception as e:
                logger.error(f"寫入快取失敗 {key}: {e}")
                raise DataError(f"快取寫入失敗: {e}")

    def delete(self, key: str) -> bool:
        """
        刪除快取值

        Args:
            key: 快取鍵

        Returns:
            如果鍵存在並被刪除返回 True，否則返回 False
        """
        cache_path = self._get_cache_path(key)

        with self._lock:
            if cache_path.exists():
                try:
                    cache_path.unlink()
                    logger.debug(f"刪除快取: {key}")
                    return True
                except Exception as e:
                    logger.error(f"刪除快取失敗 {key}: {e}")
                    return False
            return False

    def clear(self) -> None:
        """清空所有快取"""
        with self._lock:
            count = 0
            for cache_file in self.cache_dir.glob("*.cache"):
                try:
                    cache_file.unlink()
                    count += 1
                except Exception as e:
                    logger.error(f"刪除快取檔案失敗 {cache_file}: {e}")

            logger.info(f"清空快取 - 刪除 {count} 個檔案")

    def exists(self, key: str) -> bool:
        """
        檢查鍵是否存在且未過期

        Args:
            key: 快取鍵

        Returns:
            如果鍵存在且未過期返回 True，否則返回 False
        """
        cache_path = self._get_cache_path(key)

        if not cache_path.exists():
            return False

        # 檢查是否過期
        value = self.get(key)
        return value is not None

    def cleanup_expired(self) -> int:
        """
        清理所有過期的快取檔案

        Returns:
            清理的檔案數量
        """
        count = 0

        with self._lock:
            for cache_file in self.cache_dir.glob("*.cache"):
                try:
                    with open(cache_file, 'rb') as f:
                        cache_data = self._deserialize(f.read())

                    entry = CacheEntry(
                        value=cache_data['value'],
                        ttl=cache_data.get('ttl')
                    )
                    entry.created_at = cache_data['created_at']

                    if entry.is_expired():
                        cache_file.unlink()
                        count += 1

                except Exception as e:
                    logger.error(f"處理快取檔案失敗 {cache_file}: {e}")

            if count > 0:
                logger.info(f"清理 {count} 個過期快取檔案")

        return count

    def get_stats(self) -> Dict[str, Any]:
        """
        獲取快取統計資訊

        Returns:
            包含統計數據的字典
        """
        with self._lock:
            cache_files = list(self.cache_dir.glob("*.cache"))
            total_size = sum(f.stat().st_size for f in cache_files)

            return {
                "file_count": len(cache_files),
                "total_size_bytes": total_size,
                "total_size_mb": total_size / (1024 * 1024),
                "cache_dir": str(self.cache_dir),
            }


def _generate_cache_key(func: Callable, args: tuple, kwargs: dict) -> str:
    """生成快取鍵"""
    # 將函數名、參數組合成唯一的鍵
    key_parts = [
        func.__module__,
        func.__qualname__,
        str(args),
        str(sorted(kwargs.items()))
    ]
    key_string = "|".join(key_parts)
    return hashlib.sha256(key_string.encode()).hexdigest()


def cached(
    cache: Optional[BaseCache] = None,
    ttl: Optional[float] = None,
    key_prefix: str = ""
) -> Callable:
    """
    快取裝飾器 - 自動快取函數結果

    使用此裝飾器可以自動快取函數的返回值，避免重複計算。
    支援自定義快取實例、過期時間和鍵前綴。

    Args:
        cache: 快取實例（預設使用全局記憶體快取）
        ttl: 過期時間（秒）
        key_prefix: 快取鍵前綴，用於區分不同的快取命名空間

    Example:
        >>> memory_cache = MemoryCache(default_ttl=300)
        >>>
        >>> @cached(cache=memory_cache, ttl=60)
        ... def expensive_function(x, y):
        ...     time.sleep(2)  # 模擬耗時操作
        ...     return x + y
        >>>
        >>> result = expensive_function(1, 2)  # 執行並快取
        >>> result = expensive_function(1, 2)  # 從快取讀取
    """
    # 如果沒有提供快取實例，使用全局預設快取
    if cache is None:
        cache = _default_cache

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 生成快取鍵
            cache_key = key_prefix + _generate_cache_key(func, args, kwargs)

            # 嘗試從快取獲取
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"使用快取結果: {func.__name__}")
                return cached_value

            # 執行函數
            result = func(*args, **kwargs)

            # 存入快取
            cache.set(cache_key, result, ttl=ttl)
            logger.debug(f"快取函數結果: {func.__name__}")

            return result

        # 添加清除快取的方法
        def clear_cache():
            """清除此函數的所有快取"""
            cache.clear()

        wrapper.clear_cache = clear_cache
        return wrapper

    return decorator


# 全局預設快取實例
_default_cache = MemoryCache(default_ttl=3600, max_size=1000)


def get_default_cache() -> MemoryCache:
    """
    獲取全局預設快取實例

    Returns:
        全局記憶體快取實例
    """
    return _default_cache


__all__ = [
    "BaseCache",
    "MemoryCache",
    "FileCache",
    "CacheEntry",
    "cached",
    "get_default_cache",
]

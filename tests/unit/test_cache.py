"""快取系統模組測試

測試 cache.py 模組的功能：
- CacheEntry 快取項目
- MemoryCache 記憶體快取
- FileCache 檔案快取
- cached 裝飾器
"""

import pytest
import time
import tempfile
import threading
from pathlib import Path
from unittest.mock import Mock, patch

from llm_agent_demo.utils.cache import (
    CacheEntry,
    MemoryCache,
    FileCache,
    cached,
    get_default_cache,
)


class TestCacheEntry:
    """測試 CacheEntry 快取項目"""

    def test_create_cache_entry(self):
        """測試創建快取項目"""
        entry = CacheEntry(value="test_value", ttl=60.0)
        assert entry.value == "test_value"
        assert entry.ttl == 60.0

    def test_cache_entry_without_ttl(self):
        """測試創建不過期的快取項目"""
        entry = CacheEntry(value="test", ttl=None)
        assert entry.ttl is None
        assert entry.is_expired() is False

    def test_cache_entry_not_expired(self):
        """測試未過期的快取項目"""
        entry = CacheEntry(value="test", ttl=60.0)
        assert entry.is_expired() is False

    def test_cache_entry_expired(self):
        """測試已過期的快取項目"""
        entry = CacheEntry(value="test", ttl=0.01)
        time.sleep(0.02)
        assert entry.is_expired() is True

    def test_remaining_ttl(self):
        """測試剩餘 TTL 時間"""
        entry = CacheEntry(value="test", ttl=60.0)
        remaining = entry.remaining_ttl()
        assert remaining is not None
        assert remaining > 59.0
        assert remaining <= 60.0

    def test_remaining_ttl_when_no_ttl(self):
        """測試無 TTL 時的剩餘時間"""
        entry = CacheEntry(value="test", ttl=None)
        assert entry.remaining_ttl() is None


class TestMemoryCache:
    """測試 MemoryCache 記憶體快取"""

    @pytest.fixture
    def cache(self):
        """創建 MemoryCache 實例"""
        return MemoryCache(default_ttl=60.0, max_size=100)

    def test_create_memory_cache(self, cache):
        """測試創建記憶體快取"""
        assert cache is not None
        assert cache.default_ttl == 60.0
        assert cache.max_size == 100

    def test_set_and_get(self, cache):
        """測試設置和獲取快取值"""
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_get_nonexistent_key(self, cache):
        """測試獲取不存在的鍵"""
        assert cache.get("nonexistent") is None

    def test_set_with_custom_ttl(self, cache):
        """測試設置自定義 TTL"""
        cache.set("key1", "value1", ttl=0.01)
        assert cache.get("key1") == "value1"
        time.sleep(0.02)
        assert cache.get("key1") is None

    def test_delete(self, cache):
        """測試刪除快取值"""
        cache.set("key1", "value1")
        result = cache.delete("key1")
        assert result is True
        assert cache.get("key1") is None

    def test_delete_nonexistent_key(self, cache):
        """測試刪除不存在的鍵"""
        result = cache.delete("nonexistent")
        assert result is False

    def test_clear(self, cache):
        """測試清空快取"""
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.clear()
        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_exists(self, cache):
        """測試檢查鍵是否存在"""
        cache.set("key1", "value1")
        assert cache.exists("key1") is True
        assert cache.exists("nonexistent") is False

    def test_exists_with_expired_key(self, cache):
        """測試過期鍵的存在檢查"""
        cache.set("key1", "value1", ttl=0.01)
        assert cache.exists("key1") is True
        time.sleep(0.02)
        assert cache.exists("key1") is False

    def test_max_size_eviction(self):
        """測試達到最大容量時的驅逐"""
        cache = MemoryCache(max_size=3)
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        cache.set("key4", "value4")  # 應該驅逐 key1

        assert cache.get("key1") is None  # 被驅逐
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
        assert cache.get("key4") == "value4"

    def test_lru_eviction_order(self):
        """測試 LRU 驅逐順序"""
        cache = MemoryCache(max_size=3)
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        # 訪問 key1，使其成為最近使用的
        cache.get("key1")

        # 添加 key4，應該驅逐 key2（最久未使用）
        cache.set("key4", "value4")

        assert cache.get("key1") == "value1"  # 最近訪問，不應被驅逐
        assert cache.get("key2") is None  # 被驅逐
        assert cache.get("key3") == "value3"
        assert cache.get("key4") == "value4"

    def test_cleanup_expired(self):
        """測試清理過期項目"""
        cache = MemoryCache()
        cache.set("key1", "value1", ttl=0.01)
        cache.set("key2", "value2", ttl=60.0)
        cache.set("key3", "value3", ttl=0.01)

        time.sleep(0.02)
        cleaned = cache.cleanup_expired()

        assert cleaned == 2
        assert cache.get("key2") == "value2"

    def test_get_stats(self, cache):
        """測試獲取統計資訊"""
        cache.set("key1", "value1")
        cache.get("key1")  # hit
        cache.get("key2")  # miss

        stats = cache.get_stats()

        assert stats["size"] == 1
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 0.5

    def test_thread_safety(self):
        """測試線程安全"""
        cache = MemoryCache(max_size=1000)
        threads = []
        errors = []

        def worker(worker_id):
            try:
                for i in range(100):
                    key = f"worker_{worker_id}_key_{i}"
                    cache.set(key, f"value_{i}")
                    cache.get(key)
            except Exception as e:
                errors.append(e)

        for i in range(10):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        assert len(errors) == 0


class TestFileCache:
    """測試 FileCache 檔案快取"""

    @pytest.fixture
    def cache_dir(self):
        """創建臨時快取目錄"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def cache(self, cache_dir):
        """創建 FileCache 實例"""
        return FileCache(cache_dir=cache_dir, default_ttl=60.0)

    def test_create_file_cache(self, cache_dir):
        """測試創建檔案快取"""
        cache = FileCache(cache_dir=cache_dir)
        assert cache is not None
        assert cache.cache_dir == Path(cache_dir)

    def test_set_and_get(self, cache):
        """測試設置和獲取快取值"""
        cache.set("key1", {"data": "value1"})
        result = cache.get("key1")
        assert result == {"data": "value1"}

    def test_get_nonexistent_key(self, cache):
        """測試獲取不存在的鍵"""
        assert cache.get("nonexistent") is None

    def test_set_with_custom_ttl(self, cache):
        """測試設置自定義 TTL"""
        cache.set("key1", "value1", ttl=0.01)
        assert cache.get("key1") == "value1"
        time.sleep(0.02)
        assert cache.get("key1") is None

    def test_delete(self, cache):
        """測試刪除快取值"""
        cache.set("key1", "value1")
        result = cache.delete("key1")
        assert result is True
        assert cache.get("key1") is None

    def test_clear(self, cache):
        """測試清空快取"""
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.clear()
        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_exists(self, cache):
        """測試檢查鍵是否存在"""
        cache.set("key1", "value1")
        assert cache.exists("key1") is True
        assert cache.exists("nonexistent") is False

    def test_cleanup_expired(self, cache):
        """測試清理過期項目"""
        cache.set("key1", "value1", ttl=0.01)
        cache.set("key2", "value2", ttl=60.0)

        time.sleep(0.02)
        cleaned = cache.cleanup_expired()

        assert cleaned == 1

    def test_get_stats(self, cache):
        """測試獲取統計資訊"""
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        stats = cache.get_stats()

        assert stats["file_count"] == 2
        assert stats["total_size_bytes"] > 0

    def test_serializer_defaults_to_json(self, cache_dir):
        """測試序列化器默認使用 JSON"""
        cache = FileCache(cache_dir=cache_dir, serializer="json")
        assert cache.serializer == "json"

    def test_pickle_serializer_warning(self, cache_dir):
        """測試 pickle 序列化器會被替換為 JSON 並產生警告"""
        # pickle 已被棄用，應該自動使用 json
        cache = FileCache(cache_dir=cache_dir, serializer="pickle")
        # 應該自動切換為 json
        assert cache.serializer == "json"


class TestCachedDecorator:
    """測試 cached 裝飾器"""

    def test_cached_function(self):
        """測試快取函數結果"""
        cache = MemoryCache()
        call_count = 0

        @cached(cache=cache, ttl=60.0)
        def expensive_function(x, y):
            nonlocal call_count
            call_count += 1
            return x + y

        # 第一次調用
        result1 = expensive_function(1, 2)
        assert result1 == 3
        assert call_count == 1

        # 第二次調用，應該使用快取
        result2 = expensive_function(1, 2)
        assert result2 == 3
        assert call_count == 1  # 沒有再次調用

    def test_cached_with_different_args(self):
        """測試不同參數的快取"""
        cache = MemoryCache()
        call_count = 0

        @cached(cache=cache)
        def add(x, y):
            nonlocal call_count
            call_count += 1
            return x + y

        result1 = add(1, 2)
        result2 = add(3, 4)
        result3 = add(1, 2)  # 使用快取

        assert result1 == 3
        assert result2 == 7
        assert result3 == 3
        assert call_count == 2  # 只調用了兩次

    def test_cached_with_key_prefix(self):
        """測試帶前綴的快取鍵"""
        cache = MemoryCache()

        @cached(cache=cache, key_prefix="test_")
        def func(x):
            return x * 2

        result = func(5)
        assert result == 10

    def test_cached_preserves_function_metadata(self):
        """測試裝飾器保留函數元數據"""
        cache = MemoryCache()

        @cached(cache=cache)
        def documented_function():
            """這是一個有文檔的函數"""
            pass

        assert documented_function.__doc__ == "這是一個有文檔的函數"
        assert documented_function.__name__ == "documented_function"

    def test_cached_clear_cache(self):
        """測試清除快取"""
        cache = MemoryCache()
        call_count = 0

        @cached(cache=cache)
        def func(x):
            nonlocal call_count
            call_count += 1
            return x

        func(1)
        func(1)  # 使用快取
        assert call_count == 1

        func.clear_cache()
        func(1)  # 重新計算
        assert call_count == 2


class TestGetDefaultCache:
    """測試 get_default_cache 函數"""

    def test_get_default_cache(self):
        """測試獲取默認快取"""
        cache = get_default_cache()
        assert cache is not None
        assert isinstance(cache, MemoryCache)

    def test_default_cache_is_singleton(self):
        """測試默認快取是單例"""
        cache1 = get_default_cache()
        cache2 = get_default_cache()
        assert cache1 is cache2

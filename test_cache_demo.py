"""快取系統測試腳本"""

import time
from pathlib import Path
from src.llm_agent_demo.utils.cache import MemoryCache, FileCache, cached

print("=" * 60)
print("快取系統測試")
print("=" * 60)

# 測試 1: 記憶體快取
print("\n1. 測試記憶體快取 (MemoryCache)")
print("-" * 60)
memory_cache = MemoryCache(default_ttl=5, max_size=100)

# 設置快取
memory_cache.set("user:123", {"name": "Alice", "age": 30})
memory_cache.set("user:456", {"name": "Bob", "age": 25}, ttl=2)

# 獲取快取
user1 = memory_cache.get("user:123")
print(f"獲取 user:123: {user1}")

user2 = memory_cache.get("user:456")
print(f"獲取 user:456: {user2}")

# 檢查是否存在
print(f"user:123 存在: {memory_cache.exists('user:123')}")
print(f"user:999 存在: {memory_cache.exists('user:999')}")

# 測試 TTL 過期
print("\n等待 3 秒後測試 TTL...")
time.sleep(3)
user2_expired = memory_cache.get("user:456")
print(f"user:456 (TTL=2秒) 已過期: {user2_expired is None}")
print(f"user:123 (TTL=5秒) 仍有效: {memory_cache.get('user:123') is not None}")

# 查看統計
stats = memory_cache.get_stats()
print(f"\n快取統計: {stats}")

# 測試 2: 檔案快取
print("\n\n2. 測試檔案快取 (FileCache)")
print("-" * 60)
cache_dir = Path("/tmp/test_cache")
file_cache = FileCache(cache_dir, default_ttl=10, serializer="pickle")

# 設置快取
file_cache.set("config", {"debug": True, "timeout": 30})
file_cache.set("data", [1, 2, 3, 4, 5])

# 獲取快取
config = file_cache.get("config")
print(f"獲取 config: {config}")

data = file_cache.get("data")
print(f"獲取 data: {data}")

# 查看統計
file_stats = file_cache.get_stats()
print(f"檔案快取統計: {file_stats}")

# 測試 3: 快取裝飾器
print("\n\n3. 測試快取裝飾器 (@cached)")
print("-" * 60)

cache_instance = MemoryCache(default_ttl=60)

@cached(cache=cache_instance, ttl=30)
def expensive_function(x, y):
    """模擬耗時運算"""
    print(f"  執行函數: expensive_function({x}, {y})")
    time.sleep(0.5)  # 模擬耗時操作
    return x + y

# 第一次調用 - 會執行函數
print("第一次調用 expensive_function(10, 20):")
start = time.time()
result1 = expensive_function(10, 20)
time1 = time.time() - start
print(f"  結果: {result1}, 耗時: {time1:.3f}秒")

# 第二次調用 - 從快取讀取
print("\n第二次調用 expensive_function(10, 20):")
start = time.time()
result2 = expensive_function(10, 20)
time2 = time.time() - start
print(f"  結果: {result2}, 耗時: {time2:.3f}秒 (從快取讀取)")

# 不同參數 - 會執行函數
print("\n調用 expensive_function(5, 15):")
start = time.time()
result3 = expensive_function(5, 15)
time3 = time.time() - start
print(f"  結果: {result3}, 耗時: {time3:.3f}秒")

# 測試 4: 清理過期快取
print("\n\n4. 測試清理過期快取")
print("-" * 60)
test_cache = MemoryCache()
test_cache.set("temp1", "data1", ttl=1)
test_cache.set("temp2", "data2", ttl=1)
test_cache.set("permanent", "data3", ttl=None)

print(f"設置 3 個快取項目，快取大小: {test_cache.get_stats()['size']}")
time.sleep(1.5)
cleaned = test_cache.cleanup_expired()
print(f"清理後: 移除 {cleaned} 個過期項目，剩餘: {test_cache.get_stats()['size']}")

# 測試 5: 容量限制
print("\n\n5. 測試容量限制")
print("-" * 60)
limited_cache = MemoryCache(max_size=3)
for i in range(5):
    limited_cache.set(f"item{i}", f"value{i}")
    print(f"添加 item{i}, 當前大小: {limited_cache.get_stats()['size']}")

print(f"最終快取大小: {limited_cache.get_stats()['size']} (最大容量: 3)")

# 清理測試檔案
print("\n\n清理測試資源...")
file_cache.clear()
if cache_dir.exists():
    cache_dir.rmdir()
print("測試完成！")

print("\n" + "=" * 60)
print("所有測試通過！")
print("=" * 60)

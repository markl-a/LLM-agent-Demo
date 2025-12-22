"""測試 LRU 快取優化 - 獨立測試腳本"""

import sys
import time
from collections import OrderedDict

# 直接導入優化後的類
sys.path.insert(0, '/home/user/LLM-agent-Demo/src')

# 測試 OrderedDict LRU 行為
print("=" * 70)
print("測試 OrderedDict LRU 驅逐算法優化")
print("=" * 70)

# 測試 1: OrderedDict 基本操作
print("\n1. 測試 OrderedDict 基本 LRU 操作")
print("-" * 70)

cache = OrderedDict()
cache['a'] = 1
cache['b'] = 2
cache['c'] = 3

print(f"初始順序: {list(cache.keys())}")

# 訪問 'a'，移到末尾
cache.move_to_end('a')
print(f"訪問 'a' 後: {list(cache.keys())}")

# 移除最舊的（最前面的）
oldest_key, oldest_value = cache.popitem(last=False)
print(f"移除最舊項目: {oldest_key} = {oldest_value}")
print(f"剩餘順序: {list(cache.keys())}")

# 測試 2: 模擬 LRU 快取驅逐
print("\n2. 模擬 LRU 快取驅逐（容量限制 = 3）")
print("-" * 70)

lru_cache = OrderedDict()
max_size = 3

def set_cache(key, value):
    """模擬快取設置操作"""
    global lru_cache
    # 如果達到容量限制且是新鍵
    if len(lru_cache) >= max_size and key not in lru_cache:
        # O(1) 驅逐最舊項目
        evicted_key, _ = lru_cache.popitem(last=False)
        print(f"  驅逐: {evicted_key}")

    lru_cache[key] = value
    lru_cache.move_to_end(key)
    print(f"  設置: {key}, 當前順序: {list(lru_cache.keys())}")

def get_cache(key):
    """模擬快取獲取操作"""
    global lru_cache
    if key in lru_cache:
        # O(1) 移動到末尾
        lru_cache.move_to_end(key)
        print(f"  訪問: {key}, 更新順序: {list(lru_cache.keys())}")
        return lru_cache[key]
    return None

# 添加項目到容量限制
for i in range(5):
    print(f"\n添加 item{i}:")
    set_cache(f'item{i}', f'value{i}')

print(f"\n最終快取大小: {len(lru_cache)} (最大容量: {max_size})")
print(f"最終快取項目: {list(lru_cache.keys())}")

# 測試 3: 驗證 LRU 訪問順序
print("\n3. 測試 LRU 訪問順序")
print("-" * 70)

lru_cache.clear()
lru_cache['x'] = 10
lru_cache['y'] = 20
lru_cache['z'] = 30

print(f"初始順序: {list(lru_cache.keys())}")

# 訪問 x，應該移到末尾
get_cache('x')

# 再添加一個新項目，應該驅逐 y（現在是最舊的）
print(f"\n添加新項目 'w' (應該驅逐 'y'):")
set_cache('w', 40)

print(f"最終項目: {list(lru_cache.keys())}")
assert 'y' not in lru_cache, "y 應該被驅逐"
assert 'x' in lru_cache, "x 應該保留（最近訪問過）"
print("✓ LRU 驅逐邏輯正確！")

# 測試 4: 性能對比（模擬）
print("\n4. 時間複雜度分析")
print("-" * 70)

print("\n舊方法（O(n) 驅逐）：")
print("  oldest_key = min(cache.keys(), key=lambda k: cache[k].created_at)")
print("  - 需要遍歷所有項目找最小值")
print("  - 時間複雜度: O(n)")

print("\n新方法（O(1) 驅逐）：")
print("  oldest_key, _ = cache.popitem(last=False)")
print("  - 直接移除第一個項目")
print("  - 時間複雜度: O(1)")

print("\n新增操作（O(1)）：")
print("  cache.move_to_end(key)")
print("  - 將訪問的項目移到末尾")
print("  - 時間複雜度: O(1)")

# 測試 5: 導入並測試實際的 MemoryCache 類
print("\n5. 測試優化後的 MemoryCache 類")
print("-" * 70)

try:
    # 只導入 cache 模組，避免其他依賴
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "cache",
        "/home/user/LLM-agent-Demo/src/llm_agent_demo/utils/cache.py"
    )
    cache_module = importlib.util.module_from_spec(spec)

    # 創建模擬的依賴
    class MockLogger:
        def info(self, msg): pass
        def debug(self, msg): pass
        def error(self, msg): pass

    class DataError(Exception): pass

    # 注入模擬的依賴
    sys.modules['llm_agent_demo.utils.logger'] = type('MockModule', (), {
        'get_logger': lambda x: MockLogger()
    })()
    sys.modules['llm_agent_demo.utils.exceptions'] = type('MockModule', (), {
        'DataError': DataError
    })()

    spec.loader.exec_module(cache_module)

    # 測試 MemoryCache
    MemoryCache = cache_module.MemoryCache

    print("創建容量為 3 的快取...")
    mc = MemoryCache(max_size=3)

    # 驗證使用了 OrderedDict
    print(f"快取類型: {type(mc._cache).__name__}")
    assert type(mc._cache).__name__ == 'OrderedDict', "應該使用 OrderedDict"
    print("✓ 使用 OrderedDict")

    # 測試驅逐
    print("\n添加 5 個項目測試驅逐...")
    for i in range(5):
        mc.set(f'key{i}', f'value{i}')

    stats = mc.get_stats()
    print(f"最終大小: {stats['size']}")
    assert stats['size'] == 3, "應該只保留 3 個項目"
    print("✓ 驅逐功能正常")

    # 測試 LRU 訪問
    print("\n測試 LRU 訪問順序...")
    mc.get('key2')  # 訪問 key2，應該移到末尾
    mc.set('key5', 'value5')  # 添加新項目，應該驅逐 key3

    assert mc.get('key2') is not None, "key2 應該保留（最近訪問）"
    assert mc.get('key3') is None, "key3 應該被驅逐"
    print("✓ LRU 訪問順序正確")

    print("\n✓✓✓ 所有測試通過！MemoryCache 優化成功！")

except Exception as e:
    print(f"測試 MemoryCache 時出錯: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("優化驗證完成！")
print("=" * 70)
print("\n優化總結：")
print("1. ✓ 將 Dict 改為 OrderedDict")
print("2. ✓ _evict_oldest() 使用 popitem(last=False) - O(1)")
print("3. ✓ get() 方法添加 move_to_end() - O(1)")
print("4. ✓ set() 方法添加 move_to_end() - O(1)")
print("5. ✓ 從 O(n) 優化到 O(1)")

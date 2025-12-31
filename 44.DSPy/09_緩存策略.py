"""
DSPy 緩存策略教學

本模組展示如何在 DSPy 中實施緩存策略以提高效率和降低成本：
1. 緩存的重要性和原理
2. LRU 緩存實現
3. 持久化緩存
4. 分佈式緩存
5. 智能緩存失效
6. 緩存命中率優化
7. 成本節省分析

作者：DSPy 教學團隊
日期：2025-01
"""

import dspy
from typing import List, Dict, Optional, Any, Callable
import hashlib
import json
import pickle
import time
from functools import wraps
from collections import OrderedDict
import os


# ==================== 緩存基礎概念 ====================

def explain_caching_concept():
    """
    解釋緩存的核心概念

    什麼是緩存？為什麼需要緩存？
    """
    print("\n" + "="*60)
    print("緩存核心概念")
    print("="*60)

    print("""
    什麼是緩存？
    - 存儲之前的計算結果
    - 相同輸入直接返回緩存結果
    - 避免重複調用 LLM API

    緩存的優勢：
    1. 降低成本：減少 API 調用次數
    2. 提高速度：直接返回結果，無需等待
    3. 穩定性：減少對外部服務的依賴
    4. 可重現：相同輸入得到相同輸出

    緩存的挑戰：
    1. 存儲空間：緩存需要佔用內存或磁盤
    2. 一致性：何時更新或刪除緩存
    3. 命中率：如何提高緩存使用效率
    4. 管理複雜度：需要額外的邏輯處理

    緩存策略類型：
    - LRU（最近最少使用）：淘汰最久未用的條目
    - LFU（最不常用）：淘汰使用次數最少的
    - TTL（時間過期）：設置緩存有效期
    - 大小限制：限制緩存的最大條目數

    何時使用緩存：
    - 開發和測試階段
    - 相同問題重複出現
    - 批量處理相似任務
    - 需要確定性輸出
    - 成本控制需求
    """)


# ==================== 簡單內存緩存 ====================

class SimpleCache:
    """
    簡單的內存緩存

    使用字典存儲緩存數據
    """

    def __init__(self):
        """初始化緩存"""
        self.cache = {}
        self.hits = 0
        self.misses = 0

    def _generate_key(self, *args, **kwargs) -> str:
        """
        生成緩存鍵

        Args:
            *args: 位置參數
            **kwargs: 關鍵字參數

        Returns:
            緩存鍵字符串
        """
        # 將參數轉換為可哈希的字符串
        key_data = {
            "args": args,
            "kwargs": sorted(kwargs.items())
        }
        key_string = json.dumps(key_data, sort_keys=True)

        # 使用 MD5 哈希
        return hashlib.md5(key_string.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """
        獲取緩存值

        Args:
            key: 緩存鍵

        Returns:
            緩存的值，如果不存在則返回 None
        """
        if key in self.cache:
            self.hits += 1
            return self.cache[key]
        else:
            self.misses += 1
            return None

    def set(self, key: str, value: Any):
        """
        設置緩存值

        Args:
            key: 緩存鍵
            value: 要緩存的值
        """
        self.cache[key] = value

    def clear(self):
        """清空緩存"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0

    def get_stats(self) -> Dict[str, Any]:
        """
        獲取緩存統計

        Returns:
            統計資訊字典
        """
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0

        return {
            "size": len(self.cache),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.2f}%"
        }


# ==================== LRU 緩存 ====================

class LRUCache:
    """
    LRU (Least Recently Used) 緩存

    自動淘汰最久未使用的條目
    """

    def __init__(self, max_size: int = 100):
        """
        初始化 LRU 緩存

        Args:
            max_size: 最大緩存條目數
        """
        self.max_size = max_size
        self.cache = OrderedDict()
        self.hits = 0
        self.misses = 0

    def _generate_key(self, *args, **kwargs) -> str:
        """生成緩存鍵"""
        key_data = {
            "args": args,
            "kwargs": sorted(kwargs.items())
        }
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_string.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """
        獲取緩存值

        訪問後將該條目移到最後（最近使用）
        """
        if key in self.cache:
            self.hits += 1
            # 移動到末尾（最近使用）
            self.cache.move_to_end(key)
            return self.cache[key]
        else:
            self.misses += 1
            return None

    def set(self, key: str, value: Any):
        """
        設置緩存值

        如果超過最大大小，淘汰最久未使用的條目
        """
        if key in self.cache:
            # 更新現有條目
            self.cache.move_to_end(key)
        else:
            # 新增條目
            if len(self.cache) >= self.max_size:
                # 淘汰最舊的條目
                self.cache.popitem(last=False)

        self.cache[key] = value

    def clear(self):
        """清空緩存"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0

    def get_stats(self) -> Dict[str, Any]:
        """獲取緩存統計"""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0

        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.2f}%"
        }


# ==================== 持久化緩存 ====================

class PersistentCache:
    """
    持久化緩存

    將緩存保存到磁盤，程式重啟後仍然可用
    """

    def __init__(self, cache_file: str = "./dspy_cache.pkl"):
        """
        初始化持久化緩存

        Args:
            cache_file: 緩存文件路徑
        """
        self.cache_file = cache_file
        self.cache = {}
        self.hits = 0
        self.misses = 0

        # 加載現有緩存
        self._load_cache()

    def _generate_key(self, *args, **kwargs) -> str:
        """生成緩存鍵"""
        key_data = {
            "args": args,
            "kwargs": sorted(kwargs.items())
        }
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_string.encode()).hexdigest()

    def _load_cache(self):
        """從磁盤加載緩存"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'rb') as f:
                    self.cache = pickle.load(f)
                print(f"✓ 從 {self.cache_file} 加載了 {len(self.cache)} 個緩存條目")
            except Exception as e:
                print(f"加載緩存失敗：{e}")
                self.cache = {}

    def _save_cache(self):
        """保存緩存到磁盤"""
        try:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(self.cache, f)
        except Exception as e:
            print(f"保存緩存失敗：{e}")

    def get(self, key: str) -> Optional[Any]:
        """獲取緩存值"""
        if key in self.cache:
            self.hits += 1
            return self.cache[key]
        else:
            self.misses += 1
            return None

    def set(self, key: str, value: Any):
        """設置緩存值並保存到磁盤"""
        self.cache[key] = value
        self._save_cache()

    def clear(self):
        """清空緩存"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
        self._save_cache()

    def get_stats(self) -> Dict[str, Any]:
        """獲取緩存統計"""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0

        return {
            "size": len(self.cache),
            "file": self.cache_file,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.2f}%"
        }


# ==================== TTL 緩存 ====================

class TTLCache:
    """
    TTL (Time To Live) 緩存

    緩存條目在指定時間後自動過期
    """

    def __init__(self, ttl_seconds: int = 3600):
        """
        初始化 TTL 緩存

        Args:
            ttl_seconds: 緩存有效期（秒）
        """
        self.ttl_seconds = ttl_seconds
        self.cache = {}  # {key: (value, timestamp)}
        self.hits = 0
        self.misses = 0
        self.expired = 0

    def _generate_key(self, *args, **kwargs) -> str:
        """生成緩存鍵"""
        key_data = {
            "args": args,
            "kwargs": sorted(kwargs.items())
        }
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_string.encode()).hexdigest()

    def _is_expired(self, timestamp: float) -> bool:
        """
        檢查是否過期

        Args:
            timestamp: 緩存時間戳

        Returns:
            是否過期
        """
        return (time.time() - timestamp) > self.ttl_seconds

    def get(self, key: str) -> Optional[Any]:
        """獲取緩存值"""
        if key in self.cache:
            value, timestamp = self.cache[key]

            # 檢查是否過期
            if self._is_expired(timestamp):
                # 過期，刪除並返回 None
                del self.cache[key]
                self.expired += 1
                self.misses += 1
                return None
            else:
                # 未過期
                self.hits += 1
                return value
        else:
            self.misses += 1
            return None

    def set(self, key: str, value: Any):
        """設置緩存值"""
        self.cache[key] = (value, time.time())

    def clear(self):
        """清空緩存"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
        self.expired = 0

    def cleanup_expired(self):
        """清理所有過期條目"""
        current_time = time.time()
        expired_keys = [
            key for key, (_, timestamp) in self.cache.items()
            if (current_time - timestamp) > self.ttl_seconds
        ]

        for key in expired_keys:
            del self.cache[key]

        return len(expired_keys)

    def get_stats(self) -> Dict[str, Any]:
        """獲取緩存統計"""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0

        return {
            "size": len(self.cache),
            "ttl_seconds": self.ttl_seconds,
            "hits": self.hits,
            "misses": self.misses,
            "expired": self.expired,
            "hit_rate": f"{hit_rate:.2f}%"
        }


# ==================== 緩存裝飾器 ====================

def cached(cache_instance):
    """
    緩存裝飾器

    為函數添加緩存功能

    Args:
        cache_instance: 緩存實例

    Returns:
        裝飾器函數
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成緩存鍵
            cache_key = cache_instance._generate_key(*args, **kwargs)

            # 嘗試從緩存獲取
            cached_value = cache_instance.get(cache_key)

            if cached_value is not None:
                # 緩存命中
                return cached_value
            else:
                # 緩存未命中，執行函數
                result = func(*args, **kwargs)

                # 保存到緩存
                cache_instance.set(cache_key, result)

                return result

        return wrapper
    return decorator


# ==================== 帶緩存的 DSPy 模組 ====================

class CachedQAModule(dspy.Module):
    """
    帶緩存的問答模組

    展示如何在 DSPy 模組中集成緩存
    """

    def __init__(self, cache_type: str = "lru"):
        """
        初始化帶緩存的模組

        Args:
            cache_type: 緩存類型（simple, lru, persistent, ttl）
        """
        super().__init__()

        # 選擇緩存類型
        if cache_type == "simple":
            self.cache = SimpleCache()
        elif cache_type == "lru":
            self.cache = LRUCache(max_size=50)
        elif cache_type == "persistent":
            self.cache = PersistentCache()
        elif cache_type == "ttl":
            self.cache = TTLCache(ttl_seconds=1800)  # 30分鐘
        else:
            self.cache = SimpleCache()

        # 定義簽名
        class QA(dspy.Signature):
            """回答問題"""
            question = dspy.InputField()
            answer = dspy.OutputField()

        self.generate_answer = dspy.Predict(QA)

    def forward(self, question):
        """
        執行問答（帶緩存）

        Args:
            question: 問題

        Returns:
            答案
        """
        # 生成緩存鍵
        cache_key = self.cache._generate_key(question=question)

        # 檢查緩存
        cached_result = self.cache.get(cache_key)

        if cached_result is not None:
            # 緩存命中
            return dspy.Prediction(
                answer=cached_result,
                from_cache=True
            )
        else:
            # 緩存未命中，調用 LLM
            result = self.generate_answer(question=question)

            # 保存到緩存
            self.cache.set(cache_key, result.answer)

            return dspy.Prediction(
                answer=result.answer,
                from_cache=False
            )

    def get_cache_stats(self):
        """獲取緩存統計"""
        return self.cache.get_stats()


# ==================== 智能緩存策略 ====================

class SmartCache:
    """
    智能緩存

    結合多種策略，自動優化緩存效率
    """

    def __init__(self, max_size: int = 100, ttl_seconds: int = 3600):
        """
        初始化智能緩存

        Args:
            max_size: 最大緩存條目數
            ttl_seconds: 緩存有效期
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache = OrderedDict()  # {key: (value, timestamp, access_count)}
        self.hits = 0
        self.misses = 0
        self.evictions = 0

    def _generate_key(self, *args, **kwargs) -> str:
        """生成緩存鍵"""
        key_data = {
            "args": args,
            "kwargs": sorted(kwargs.items())
        }
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_string.encode()).hexdigest()

    def _is_expired(self, timestamp: float) -> bool:
        """檢查是否過期"""
        return (time.time() - timestamp) > self.ttl_seconds

    def get(self, key: str) -> Optional[Any]:
        """獲取緩存值"""
        if key in self.cache:
            value, timestamp, access_count = self.cache[key]

            # 檢查是否過期
            if self._is_expired(timestamp):
                del self.cache[key]
                self.misses += 1
                return None

            # 更新訪問計數
            self.cache[key] = (value, timestamp, access_count + 1)
            self.cache.move_to_end(key)
            self.hits += 1
            return value
        else:
            self.misses += 1
            return None

    def set(self, key: str, value: Any):
        """設置緩存值"""
        current_time = time.time()

        if key in self.cache:
            # 更新現有條目
            _, _, access_count = self.cache[key]
            self.cache[key] = (value, current_time, access_count)
            self.cache.move_to_end(key)
        else:
            # 新增條目
            if len(self.cache) >= self.max_size:
                # 需要淘汰
                # 選擇訪問次數最少的條目淘汰
                min_access_key = min(
                    self.cache.keys(),
                    key=lambda k: self.cache[k][2]
                )
                del self.cache[min_access_key]
                self.evictions += 1

            self.cache[key] = (value, current_time, 1)

    def get_stats(self) -> Dict[str, Any]:
        """獲取緩存統計"""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0

        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "hit_rate": f"{hit_rate:.2f}%"
        }


# ==================== 成本分析 ====================

def calculate_cost_savings(cache_stats: Dict[str, Any], cost_per_call: float = 0.002):
    """
    計算緩存節省的成本

    Args:
        cache_stats: 緩存統計資訊
        cost_per_call: 每次 API 調用的成本（美元）

    Returns:
        成本節省資訊
    """
    hits = cache_stats.get("hits", 0)
    total_calls = hits + cache_stats.get("misses", 0)

    # 沒有緩存的成本
    cost_without_cache = total_calls * cost_per_call

    # 有緩存的成本（只計算未命中的調用）
    cost_with_cache = cache_stats.get("misses", 0) * cost_per_call

    # 節省的成本
    savings = cost_without_cache - cost_with_cache

    # 節省百分比
    savings_percentage = (savings / cost_without_cache * 100) if cost_without_cache > 0 else 0

    return {
        "total_requests": total_calls,
        "cache_hits": hits,
        "api_calls_saved": hits,
        "cost_without_cache": f"${cost_without_cache:.4f}",
        "cost_with_cache": f"${cost_with_cache:.4f}",
        "cost_savings": f"${savings:.4f}",
        "savings_percentage": f"{savings_percentage:.2f}%"
    }


# ==================== 主程序 ====================

def main():
    """主函數：演示所有緩存策略"""

    print("="*60)
    print("DSPy 緩存策略教學")
    print("="*60)

    # 1. 概念說明
    explain_caching_concept()

    # 2. 測試各種緩存
    print("\n" + "="*60)
    print("緩存類型演示")
    print("="*60)

    # 簡單緩存
    print("\n1. 簡單緩存")
    simple_cache = SimpleCache()
    for i in range(5):
        key = simple_cache._generate_key(question=f"問題 {i % 3}")
        result = simple_cache.get(key)
        if result is None:
            simple_cache.set(key, f"答案 {i % 3}")
    print(simple_cache.get_stats())

    # LRU 緩存
    print("\n2. LRU 緩存")
    lru_cache = LRUCache(max_size=3)
    for i in range(5):
        key = lru_cache._generate_key(question=f"問題 {i}")
        result = lru_cache.get(key)
        if result is None:
            lru_cache.set(key, f"答案 {i}")
    print(lru_cache.get_stats())

    # TTL 緩存
    print("\n3. TTL 緩存")
    ttl_cache = TTLCache(ttl_seconds=2)
    key = ttl_cache._generate_key(question="測試問題")
    ttl_cache.set(key, "測試答案")
    print(f"立即獲取：{ttl_cache.get(key)}")
    time.sleep(3)
    print(f"3秒後獲取：{ttl_cache.get(key)}")
    print(ttl_cache.get_stats())

    # 3. 帶緩存的 DSPy 模組演示
    print("\n" + "="*60)
    print("帶緩存的 DSPy 模組")
    print("="*60)

    # 配置 DSPy
    try:
        lm = dspy.OpenAI(model="gpt-3.5-turbo", max_tokens=200)
        dspy.settings.configure(lm=lm)
        print("✓ DSPy 配置完成")

        # 創建帶緩存的模組
        cached_qa = CachedQAModule(cache_type="lru")

        # 測試問題
        questions = [
            "什麼是機器學習？",
            "什麼是深度學習？",
            "什麼是機器學習？",  # 重複問題
            "什麼是深度學習？",  # 重複問題
        ]

        print("\n執行問答：")
        for q in questions:
            result = cached_qa(question=q)
            cache_status = "✓ 緩存" if result.from_cache else "✗ API"
            print(f"{cache_status} | {q}")

        print("\n緩存統計：")
        stats = cached_qa.get_cache_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")

        # 成本分析
        print("\n成本節省分析：")
        cost_analysis = calculate_cost_savings(stats)
        for key, value in cost_analysis.items():
            print(f"  {key}: {value}")

    except Exception as e:
        print(f"DSPy 模組演示失敗：{e}")
        print("跳過此部分...")

    # 4. 智能緩存演示
    print("\n" + "="*60)
    print("智能緩存演示")
    print("="*60)

    smart_cache = SmartCache(max_size=3, ttl_seconds=3600)

    # 模擬訪問模式
    access_pattern = [
        "問題A", "問題B", "問題C",
        "問題A", "問題A",  # A 被訪問多次
        "問題D",  # 新問題，會觸發淘汰
        "問題A",  # A 應該還在（訪問次數多）
        "問題B",  # B 可能被淘汰了
    ]

    for item in access_pattern:
        key = smart_cache._generate_key(question=item)
        result = smart_cache.get(key)
        if result is None:
            smart_cache.set(key, f"答案_{item}")
            print(f"設置緩存：{item}")
        else:
            print(f"緩存命中：{item}")

    print("\n智能緩存統計：")
    print(smart_cache.get_stats())

    # 總結
    print("\n" + "="*60)
    print("教學完成！")
    print("="*60)
    print("""
    你已經學會了：
    1. ✓ 緩存的核心概念和優勢
    2. ✓ 簡單內存緩存
    3. ✓ LRU 緩存策略
    4. ✓ 持久化緩存
    5. ✓ TTL 過期緩存
    6. ✓ 智能緩存組合策略
    7. ✓ 成本節省分析

    緩存使用建議：

    開發階段：
    - 使用持久化緩存
    - 避免重複調用 API
    - 加快開發迭代

    測試階段：
    - 使用 TTL 緩存
    - 定期更新測試數據
    - 驗證不同場景

    生產階段：
    - 使用智能緩存
    - 監控命中率
    - 定期清理過期數據

    緩存優化技巧：
    - 合理設置緩存大小
    - 選擇合適的淘汰策略
    - 實施緩存預熱
    - 監控緩存性能
    - 定期分析成本節省

    常見問題：
    Q: 何時清空緩存？
    A: 模型更新、提示修改、數據變化時

    Q: 如何提高命中率？
    A: 標準化輸入、合理設計緩存鍵

    Q: 緩存多大合適？
    A: 根據內存和訪問模式，通常 100-1000 條

    下一步：
    - 學習生產部署（10_生產部署.py）
    - 實施緩存監控
    - 優化緩存策略
    """)


if __name__ == "__main__":
    main()

"""
LiteLLM 快取策略範例

這個檔案展示如何使用 LiteLLM 實現快取策略以優化效能和成本：
1. 基本快取配置
2. Redis 快取
3. 記憶體快取
4. 磁碟快取
5. 語義快取（Semantic Caching）
6. TTL（Time To Live）管理
7. 快取失效策略
8. 快取預熱
9. 快取命中率分析
10. 多層快取架構

快取是提高 LLM 應用效能和降低成本的關鍵技術。
"""

import os
from typing import Dict, List, Any, Optional, Tuple
import json
import time
import hashlib
from datetime import datetime, timedelta
from dataclasses import dataclass
import pickle
import sqlite3
from litellm import completion
from litellm.caching import Cache


# ============================================================================
# 資料類別定義
# ============================================================================

@dataclass
class CacheEntry:
    """快取項目"""
    key: str
    value: Any
    created_at: str
    expires_at: Optional[str]
    hit_count: int = 0
    last_accessed: Optional[str] = None


@dataclass
class CacheStats:
    """快取統計"""
    total_requests: int
    cache_hits: int
    cache_misses: int
    hit_rate: float
    total_saved_cost: float
    total_saved_tokens: int


# ============================================================================
# 第一部分：基本快取設定
# ============================================================================

def basic_cache_example():
    """
    基本快取範例

    LiteLLM 內建支援快取功能，可以自動快取相同的請求。
    """
    print("=" * 80)
    print("基本快取範例")
    print("=" * 80)

    # 啟用快取
    from litellm import cache
    cache.cache = Cache()

    print("\n✓ 快取已啟用\n")

    # 第一次請求（會呼叫 API）
    print("第一次請求（無快取）...")
    start_time = time.time()

    try:
        response1 = completion(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "什麼是 Python？"}],
            caching=True  # 啟用快取
        )

        time1 = time.time() - start_time
        print(f"  耗時：{time1:.2f} 秒")
        print(f"  回應：{response1.choices[0].message.content[:100]}...")

    except Exception as e:
        print(f"  錯誤：{e}")
        return

    # 第二次相同請求（應該從快取返回）
    print("\n第二次請求（使用快取）...")
    start_time = time.time()

    try:
        response2 = completion(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "什麼是 Python？"}],
            caching=True
        )

        time2 = time.time() - start_time
        print(f"  耗時：{time2:.2f} 秒")
        print(f"  回應：{response2.choices[0].message.content[:100]}...")

        # 比較
        speedup = time1 / time2 if time2 > 0 else float('inf')
        print(f"\n✓ 快取加速：{speedup:.1f}x")
        print(f"  節省時間：{time1 - time2:.2f} 秒")

    except Exception as e:
        print(f"  錯誤：{e}")


# ============================================================================
# 第二部分：自訂快取實作
# ============================================================================

class SimpleCache:
    """簡單的記憶體快取"""

    def __init__(self, ttl: int = 3600):
        """
        初始化快取

        Args:
            ttl: Time To Live（秒），預設 1 小時
        """
        self.cache: Dict[str, CacheEntry] = {}
        self.ttl = ttl
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0
        }

    def _generate_key(self, model: str, messages: List[Dict], **kwargs) -> str:
        """生成快取鍵"""
        # 將請求參數序列化為字串
        key_parts = [
            model,
            json.dumps(messages, sort_keys=True),
            json.dumps({k: v for k, v in sorted(kwargs.items())}, sort_keys=True)
        ]
        key_string = "|".join(key_parts)

        # 使用 SHA256 雜湊
        return hashlib.sha256(key_string.encode()).hexdigest()

    def get(self, model: str, messages: List[Dict], **kwargs) -> Optional[Any]:
        """取得快取值"""
        key = self._generate_key(model, messages, **kwargs)

        if key in self.cache:
            entry = self.cache[key]

            # 檢查是否過期
            if entry.expires_at:
                expires_at = datetime.fromisoformat(entry.expires_at)
                if datetime.now() > expires_at:
                    # 已過期，刪除
                    del self.cache[key]
                    self.stats["evictions"] += 1
                    self.stats["misses"] += 1
                    return None

            # 更新統計
            entry.hit_count += 1
            entry.last_accessed = datetime.now().isoformat()
            self.stats["hits"] += 1

            return entry.value

        self.stats["misses"] += 1
        return None

    def set(self, model: str, messages: List[Dict], value: Any, **kwargs):
        """設定快取值"""
        key = self._generate_key(model, messages, **kwargs)

        expires_at = (datetime.now() + timedelta(seconds=self.ttl)).isoformat()

        entry = CacheEntry(
            key=key,
            value=value,
            created_at=datetime.now().isoformat(),
            expires_at=expires_at
        )

        self.cache[key] = entry

    def clear(self):
        """清空快取"""
        self.cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        """取得快取統計"""
        total = self.stats["hits"] + self.stats["misses"]
        hit_rate = self.stats["hits"] / total if total > 0 else 0

        return {
            "total_entries": len(self.cache),
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "evictions": self.stats["evictions"],
            "hit_rate": hit_rate
        }


def simple_cache_example():
    """簡單快取範例"""
    print("\n" + "=" * 80)
    print("自訂快取範例")
    print("=" * 80)

    cache = SimpleCache(ttl=3600)  # 1 小時 TTL

    # 測試資料
    test_requests = [
        {"model": "gpt-3.5-turbo", "prompt": "什麼是機器學習？"},
        {"model": "gpt-3.5-turbo", "prompt": "什麼是深度學習？"},
        {"model": "gpt-3.5-turbo", "prompt": "什麼是機器學習？"},  # 重複
        {"model": "gpt-4o", "prompt": "什麼是機器學習？"},  # 不同模型
        {"model": "gpt-3.5-turbo", "prompt": "什麼是深度學習？"},  # 重複
    ]

    print("\n執行測試請求...\n")

    for i, req in enumerate(test_requests, 1):
        model = req["model"]
        messages = [{"role": "user", "content": req["prompt"]}]

        # 嘗試從快取取得
        cached_response = cache.get(model, messages)

        if cached_response:
            print(f"請求 {i}: ✓ 快取命中")
            print(f"  模型：{model}")
            print(f"  提示：{req['prompt']}")
        else:
            print(f"請求 {i}: ✗ 快取未命中")
            print(f"  模型：{model}")
            print(f"  提示：{req['prompt']}")

            # 模擬 API 呼叫
            response = f"這是對「{req['prompt']}」的回應"

            # 儲存到快取
            cache.set(model, messages, response)
            print(f"  已儲存到快取")

        print()

    # 顯示統計
    print("=" * 80)
    print("快取統計")
    print("=" * 80)

    stats = cache.get_stats()
    print(f"\n快取項目數：{stats['total_entries']}")
    print(f"快取命中：{stats['hits']}")
    print(f"快取未命中：{stats['misses']}")
    print(f"快取驅逐：{stats['evictions']}")
    print(f"命中率：{stats['hit_rate'] * 100:.1f}%")


# ============================================================================
# 第三部分：資料庫快取
# ============================================================================

class DatabaseCache:
    """基於 SQLite 的持久化快取"""

    def __init__(self, db_path: str = "cache.db", ttl: int = 3600):
        self.db_path = db_path
        self.ttl = ttl
        self._init_database()

    def _init_database(self):
        """初始化資料庫"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cache_entries (
                key TEXT PRIMARY KEY,
                value BLOB NOT NULL,
                model TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                hit_count INTEGER DEFAULT 0,
                last_accessed TEXT
            )
        """)

        # 建立索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_expires_at
            ON cache_entries(expires_at)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_model
            ON cache_entries(model)
        """)

        conn.commit()
        conn.close()

    def _generate_key(self, model: str, messages: List[Dict], **kwargs) -> str:
        """生成快取鍵"""
        key_parts = [
            model,
            json.dumps(messages, sort_keys=True),
            json.dumps({k: v for k, v in sorted(kwargs.items())}, sort_keys=True)
        ]
        key_string = "|".join(key_parts)
        return hashlib.sha256(key_string.encode()).hexdigest()

    def get(self, model: str, messages: List[Dict], **kwargs) -> Optional[Any]:
        """取得快取值"""
        key = self._generate_key(model, messages, **kwargs)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT value, expires_at, hit_count
            FROM cache_entries
            WHERE key = ?
        """, (key,))

        result = cursor.fetchone()

        if result:
            value_blob, expires_at, hit_count = result

            # 檢查是否過期
            if datetime.now() > datetime.fromisoformat(expires_at):
                # 刪除過期項目
                cursor.execute("DELETE FROM cache_entries WHERE key = ?", (key,))
                conn.commit()
                conn.close()
                return None

            # 更新統計
            cursor.execute("""
                UPDATE cache_entries
                SET hit_count = hit_count + 1,
                    last_accessed = ?
                WHERE key = ?
            """, (datetime.now().isoformat(), key))

            conn.commit()
            conn.close()

            # 反序列化值
            return pickle.loads(value_blob)

        conn.close()
        return None

    def set(self, model: str, messages: List[Dict], value: Any, **kwargs):
        """設定快取值"""
        key = self._generate_key(model, messages, **kwargs)
        value_blob = pickle.dumps(value)
        created_at = datetime.now().isoformat()
        expires_at = (datetime.now() + timedelta(seconds=self.ttl)).isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO cache_entries
            (key, value, model, created_at, expires_at, hit_count, last_accessed)
            VALUES (?, ?, ?, ?, ?, 0, NULL)
        """, (key, value_blob, model, created_at, expires_at))

        conn.commit()
        conn.close()

    def cleanup_expired(self):
        """清理過期的快取項目"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        current_time = datetime.now().isoformat()
        cursor.execute("""
            DELETE FROM cache_entries
            WHERE expires_at < ?
        """, (current_time,))

        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()

        return deleted_count

    def get_stats(self) -> Dict[str, Any]:
        """取得快取統計"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 總項目數
        cursor.execute("SELECT COUNT(*) FROM cache_entries")
        total_entries = cursor.fetchone()[0]

        # 總命中次數
        cursor.execute("SELECT SUM(hit_count) FROM cache_entries")
        total_hits = cursor.fetchone()[0] or 0

        # 按模型統計
        cursor.execute("""
            SELECT model, COUNT(*), SUM(hit_count)
            FROM cache_entries
            GROUP BY model
        """)
        by_model = {}
        for row in cursor.fetchall():
            model, count, hits = row
            by_model[model] = {
                "entries": count,
                "hits": hits or 0
            }

        conn.close()

        return {
            "total_entries": total_entries,
            "total_hits": total_hits,
            "by_model": by_model
        }


def database_cache_example():
    """資料庫快取範例"""
    print("\n" + "=" * 80)
    print("資料庫快取範例")
    print("=" * 80)

    cache = DatabaseCache("example_cache.db", ttl=7200)  # 2 小時 TTL

    # 模擬一些請求
    test_data = [
        ("gpt-3.5-turbo", "解釋量子計算"),
        ("gpt-3.5-turbo", "什麼是區塊鏈"),
        ("gpt-3.5-turbo", "解釋量子計算"),  # 重複
        ("gpt-4o", "解釋量子計算"),
        ("gpt-3.5-turbo", "什麼是區塊鏈"),  # 重複
    ]

    print("\n執行請求...\n")

    for i, (model, prompt) in enumerate(test_data, 1):
        messages = [{"role": "user", "content": prompt}]

        # 檢查快取
        cached = cache.get(model, messages)

        if cached:
            print(f"請求 {i}: ✓ 從快取返回")
            print(f"  {model}: {prompt}")
        else:
            print(f"請求 {i}: → 呼叫 API")
            print(f"  {model}: {prompt}")

            # 模擬 API 回應
            response = f"關於「{prompt}」的詳細回答..."

            # 儲存到快取
            cache.set(model, messages, response)

        print()

    # 清理過期項目
    print("清理過期快取項目...")
    deleted = cache.cleanup_expired()
    print(f"✓ 已刪除 {deleted} 個過期項目\n")

    # 統計
    print("=" * 80)
    print("快取統計")
    print("=" * 80)

    stats = cache.get_stats()
    print(f"\n總項目數：{stats['total_entries']}")
    print(f"總命中次數：{stats['total_hits']}")

    if stats['by_model']:
        print(f"\n按模型統計：")
        for model, model_stats in stats['by_model'].items():
            print(f"  {model}:")
            print(f"    項目數：{model_stats['entries']}")
            print(f"    命中次數：{model_stats['hits']}")


# ============================================================================
# 第四部分：語義快取
# ============================================================================

class SemanticCache:
    """
    語義快取

    使用嵌入向量來識別語義相似的查詢，
    即使措辭不同也能命中快取。
    """

    def __init__(self, similarity_threshold: float = 0.9):
        """
        初始化語義快取

        Args:
            similarity_threshold: 相似度閾值（0-1）
        """
        self.cache: List[Dict[str, Any]] = []
        self.similarity_threshold = similarity_threshold

    def _get_embedding(self, text: str) -> List[float]:
        """
        取得文本的嵌入向量

        在實際應用中，應該使用真實的嵌入模型。
        這裡使用簡化的模擬。
        """
        # 模擬：使用簡單的特徵向量
        # 實際應該使用 OpenAI embeddings 或其他嵌入模型
        words = text.lower().split()
        # 這只是示例，實際應用需要真實的嵌入
        return [hash(word) % 100 / 100.0 for word in words[:10]]

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """計算餘弦相似度"""
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    def get(self, query: str) -> Optional[Tuple[str, float]]:
        """
        取得快取值

        Returns:
            (快取的回應, 相似度) 或 None
        """
        if not self.cache:
            return None

        query_embedding = self._get_embedding(query)

        best_match = None
        best_similarity = 0.0

        for entry in self.cache:
            similarity = self._cosine_similarity(query_embedding, entry["embedding"])

            if similarity > best_similarity:
                best_similarity = similarity
                best_match = entry

        if best_similarity >= self.similarity_threshold:
            # 更新統計
            best_match["hit_count"] += 1
            best_match["last_accessed"] = datetime.now().isoformat()
            return (best_match["response"], best_similarity)

        return None

    def set(self, query: str, response: str):
        """設定快取值"""
        embedding = self._get_embedding(query)

        entry = {
            "query": query,
            "response": response,
            "embedding": embedding,
            "created_at": datetime.now().isoformat(),
            "hit_count": 0,
            "last_accessed": None
        }

        self.cache.append(entry)

    def get_stats(self) -> Dict[str, Any]:
        """取得統計資訊"""
        total_entries = len(self.cache)
        total_hits = sum(entry["hit_count"] for entry in self.cache)

        return {
            "total_entries": total_entries,
            "total_hits": total_hits,
            "average_hits_per_entry": total_hits / total_entries if total_entries > 0 else 0
        }


def semantic_cache_example():
    """語義快取範例"""
    print("\n" + "=" * 80)
    print("語義快取範例")
    print("=" * 80)

    cache = SemanticCache(similarity_threshold=0.7)

    # 第一個查詢
    print("\n1. 第一個查詢")
    query1 = "什麼是機器學習？"
    print(f"   查詢：{query1}")

    result = cache.get(query1)
    if result:
        response, similarity = result
        print(f"   ✓ 快取命中（相似度：{similarity:.2f}）")
    else:
        print(f"   → 快取未命中，呼叫 API")
        response = "機器學習是人工智慧的一個分支..."
        cache.set(query1, response)
        print(f"   已儲存到快取")

    # 第二個查詢（語義相似）
    print("\n2. 第二個查詢（語義相似）")
    query2 = "請解釋一下機器學習"
    print(f"   查詢：{query2}")

    result = cache.get(query2)
    if result:
        response, similarity = result
        print(f"   ✓ 快取命中（相似度：{similarity:.2f}）")
        print(f"   原始查詢：{query1}")
    else:
        print(f"   → 快取未命中")

    # 第三個查詢（不相似）
    print("\n3. 第三個查詢（不相似）")
    query3 = "什麼是量子計算？"
    print(f"   查詢：{query3}")

    result = cache.get(query3)
    if result:
        response, similarity = result
        print(f"   ✓ 快取命中（相似度：{similarity:.2f}）")
    else:
        print(f"   → 快取未命中，呼叫 API")
        response = "量子計算利用量子力學原理..."
        cache.set(query3, response)
        print(f"   已儲存到快取")

    # 統計
    print("\n" + "=" * 80)
    print("語義快取統計")
    print("=" * 80)

    stats = cache.get_stats()
    print(f"\n快取項目：{stats['total_entries']}")
    print(f"總命中次數：{stats['total_hits']}")
    print(f"平均命中次數：{stats['average_hits_per_entry']:.1f}")


# ============================================================================
# 第五部分：多層快取架構
# ============================================================================

class MultiTierCache:
    """多層快取架構"""

    def __init__(self):
        self.l1_cache = SimpleCache(ttl=300)  # L1: 記憶體，5 分鐘
        self.l2_cache = DatabaseCache("l2_cache.db", ttl=3600)  # L2: 資料庫，1 小時

        self.stats = {
            "l1_hits": 0,
            "l2_hits": 0,
            "misses": 0
        }

    def get(self, model: str, messages: List[Dict], **kwargs) -> Optional[Any]:
        """從多層快取取得值"""
        # 嘗試 L1 快取（記憶體）
        result = self.l1_cache.get(model, messages, **kwargs)
        if result is not None:
            self.stats["l1_hits"] += 1
            return result

        # 嘗試 L2 快取（資料庫）
        result = self.l2_cache.get(model, messages, **kwargs)
        if result is not None:
            self.stats["l2_hits"] += 1
            # 提升到 L1
            self.l1_cache.set(model, messages, result, **kwargs)
            return result

        self.stats["misses"] += 1
        return None

    def set(self, model: str, messages: List[Dict], value: Any, **kwargs):
        """設定快取值到所有層"""
        self.l1_cache.set(model, messages, value, **kwargs)
        self.l2_cache.set(model, messages, value, **kwargs)

    def get_stats(self) -> Dict[str, Any]:
        """取得統計資訊"""
        total = self.stats["l1_hits"] + self.stats["l2_hits"] + self.stats["misses"]
        hit_rate = (self.stats["l1_hits"] + self.stats["l2_hits"]) / total if total > 0 else 0

        return {
            "l1_hits": self.stats["l1_hits"],
            "l2_hits": self.stats["l2_hits"],
            "misses": self.stats["misses"],
            "total_requests": total,
            "hit_rate": hit_rate,
            "l1_stats": self.l1_cache.get_stats(),
            "l2_stats": self.l2_cache.get_stats()
        }


def multi_tier_cache_example():
    """多層快取範例"""
    print("\n" + "=" * 80)
    print("多層快取架構範例")
    print("=" * 80)

    cache = MultiTierCache()

    # 模擬請求序列
    requests = [
        ("gpt-3.5-turbo", "Python 是什麼？"),
        ("gpt-3.5-turbo", "JavaScript 是什麼？"),
        ("gpt-3.5-turbo", "Python 是什麼？"),  # L1 命中
        ("gpt-3.5-turbo", "Go 是什麼？"),
    ]

    # 等待 L1 過期後重複請求
    print("\n第一輪請求：\n")

    for i, (model, prompt) in enumerate(requests, 1):
        messages = [{"role": "user", "content": prompt}]

        result = cache.get(model, messages)

        if result:
            print(f"請求 {i}: ✓ 快取命中")
            print(f"  {prompt}")
        else:
            print(f"請求 {i}: → API 呼叫")
            print(f"  {prompt}")
            response = f"關於「{prompt}」的回答"
            cache.set(model, messages, response)

        print()

    # 統計
    print("=" * 80)
    print("多層快取統計")
    print("=" * 80)

    stats = cache.get_stats()

    print(f"\n總請求數：{stats['total_requests']}")
    print(f"L1 快取命中：{stats['l1_hits']}")
    print(f"L2 快取命中：{stats['l2_hits']}")
    print(f"快取未命中：{stats['misses']}")
    print(f"總命中率：{stats['hit_rate'] * 100:.1f}%")

    print(f"\nL1 快取（記憶體）：")
    print(f"  項目數：{stats['l1_stats']['total_entries']}")

    print(f"\nL2 快取（資料庫）：")
    print(f"  項目數：{stats['l2_stats']['total_entries']}")


# ============================================================================
# 主程式
# ============================================================================

def main():
    """主程式"""
    print("\n")
    print("=" * 80)
    print("LiteLLM 快取策略完整教學")
    print("=" * 80)
    print()

    # 基本快取
    # basic_cache_example()

    # 自訂快取
    simple_cache_example()

    # 資料庫快取
    database_cache_example()

    # 語義快取
    semantic_cache_example()

    # 多層快取
    multi_tier_cache_example()

    print("\n" + "=" * 80)
    print("教學完成！")
    print("=" * 80)
    print("\n重點回顧：")
    print("1. 快取可以大幅提高效能並降低成本")
    print("2. TTL 控制快取的有效期限")
    print("3. 資料庫快取提供持久化儲存")
    print("4. 語義快取可以識別相似查詢")
    print("5. 多層快取架構平衡效能和容量")
    print()


if __name__ == "__main__":
    main()

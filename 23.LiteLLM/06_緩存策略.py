"""
LiteLLM 緩存策略範例
===================

本範例展示如何在 LiteLLM 中配置和使用緩存。

緩存類型：
1. 內存緩存
2. Redis 緩存
3. 磁盤緩存
4. 自定義緩存

安裝依賴：
pip install litellm redis diskcache
"""

import litellm
from litellm import completion
from litellm.caching import Cache
from typing import Dict, Any, Optional, List
import hashlib
import json
import time
from dataclasses import dataclass

# ============================================================
# 1. 內存緩存配置
# ============================================================

def setup_memory_cache():
    """設置內存緩存"""
    # 啟用內存緩存
    litellm.cache = Cache(type="local")

    print("內存緩存已啟用")
    return litellm.cache


MEMORY_CACHE_EXAMPLE = '''
import litellm
from litellm.caching import Cache

# 設置內存緩存
litellm.cache = Cache(type="local")

# 第一次調用（無緩存）
response1 = litellm.completion(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "什麼是人工智能？"}],
    caching=True
)
print("第一次調用完成")

# 第二次調用（使用緩存）
response2 = litellm.completion(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "什麼是人工智能？"}],
    caching=True
)
print("第二次調用完成（來自緩存）")
'''


# ============================================================
# 2. Redis 緩存配置
# ============================================================

REDIS_CACHE_EXAMPLE = '''
import litellm
from litellm.caching import Cache

# Redis 緩存配置
litellm.cache = Cache(
    type="redis",
    host="localhost",
    port=6379,
    password="your-password",  # 可選
    ttl=3600  # 緩存過期時間（秒）
)

# 使用 Redis URL
litellm.cache = Cache(
    type="redis",
    url="redis://localhost:6379"
)

# 帶認證的 Redis
litellm.cache = Cache(
    type="redis",
    url="redis://:password@localhost:6379/0"
)

# 使用緩存
response = litellm.completion(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello"}],
    caching=True
)
'''


# ============================================================
# 3. 磁盤緩存配置
# ============================================================

DISK_CACHE_EXAMPLE = '''
import litellm
from litellm.caching import Cache

# 磁盤緩存配置
litellm.cache = Cache(
    type="disk",
    disk_cache_dir="./cache",  # 緩存目錄
    ttl=86400  # 24 小時過期
)

# 使用
response = litellm.completion(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello"}],
    caching=True
)
'''


# ============================================================
# 4. 自定義緩存實現
# ============================================================

class CustomCache:
    """自定義緩存實現"""

    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.cache: Dict[str, Any] = {}
        self.timestamps: Dict[str, float] = {}
        self.max_size = max_size
        self.ttl = ttl
        self.hits = 0
        self.misses = 0

    def _generate_key(self, model: str, messages: List[Dict]) -> str:
        """生成緩存鍵"""
        content = f"{model}:{json.dumps(messages, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()

    def _is_expired(self, key: str) -> bool:
        """檢查是否過期"""
        if key not in self.timestamps:
            return True
        return time.time() - self.timestamps[key] > self.ttl

    def _evict_if_needed(self):
        """必要時清理緩存"""
        if len(self.cache) >= self.max_size:
            # 清理過期項
            expired = [k for k in self.cache if self._is_expired(k)]
            for key in expired:
                del self.cache[key]
                del self.timestamps[key]

            # 如果仍然滿，刪除最舊的
            if len(self.cache) >= self.max_size:
                oldest = min(self.timestamps, key=self.timestamps.get)
                del self.cache[oldest]
                del self.timestamps[oldest]

    def get(self, model: str, messages: List[Dict]) -> Optional[Any]:
        """獲取緩存"""
        key = self._generate_key(model, messages)

        if key in self.cache and not self._is_expired(key):
            self.hits += 1
            return self.cache[key]

        self.misses += 1
        return None

    def set(self, model: str, messages: List[Dict], response: Any):
        """設置緩存"""
        self._evict_if_needed()
        key = self._generate_key(model, messages)
        self.cache[key] = response
        self.timestamps[key] = time.time()

    def clear(self):
        """清空緩存"""
        self.cache.clear()
        self.timestamps.clear()

    def get_stats(self) -> Dict[str, Any]:
        """獲取統計信息"""
        total = self.hits + self.misses
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": self.hits / total if total > 0 else 0,
            "size": len(self.cache),
            "max_size": self.max_size
        }


# ============================================================
# 5. 緩存策略管理器
# ============================================================

@dataclass
class CacheConfig:
    """緩存配置"""
    enabled: bool = True
    type: str = "local"
    ttl: int = 3600
    max_size: int = 1000
    redis_url: Optional[str] = None
    disk_dir: Optional[str] = None


class CacheManager:
    """緩存管理器"""

    def __init__(self, config: CacheConfig):
        self.config = config
        self.cache = None
        self._setup_cache()

    def _setup_cache(self):
        """設置緩存"""
        if not self.config.enabled:
            return

        if self.config.type == "local":
            self.cache = Cache(type="local")
        elif self.config.type == "redis":
            self.cache = Cache(
                type="redis",
                url=self.config.redis_url or "redis://localhost:6379"
            )
        elif self.config.type == "disk":
            self.cache = Cache(
                type="disk",
                disk_cache_dir=self.config.disk_dir or "./cache"
            )
        elif self.config.type == "custom":
            self.cache = CustomCache(
                max_size=self.config.max_size,
                ttl=self.config.ttl
            )

        litellm.cache = self.cache

    def completion_with_cache(
        self,
        model: str,
        messages: List[Dict],
        **kwargs
    ) -> Any:
        """帶緩存的完成調用"""
        if not self.config.enabled:
            return completion(model=model, messages=messages, **kwargs)

        # 如果是自定義緩存
        if isinstance(self.cache, CustomCache):
            cached = self.cache.get(model, messages)
            if cached:
                return cached

            response = completion(model=model, messages=messages, **kwargs)
            self.cache.set(model, messages, response)
            return response

        # 使用 LiteLLM 內置緩存
        return completion(
            model=model,
            messages=messages,
            caching=True,
            **kwargs
        )

    def clear_cache(self):
        """清空緩存"""
        if isinstance(self.cache, CustomCache):
            self.cache.clear()
        elif self.cache:
            # LiteLLM 緩存清理
            pass

    def get_stats(self) -> Dict[str, Any]:
        """獲取緩存統計"""
        if isinstance(self.cache, CustomCache):
            return self.cache.get_stats()
        return {"type": self.config.type, "enabled": self.config.enabled}


# ============================================================
# 6. 緩存預熱
# ============================================================

class CacheWarmer:
    """緩存預熱器"""

    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager

    def warm_up(self, prompts: List[Dict[str, Any]], model: str = "gpt-3.5-turbo"):
        """預熱緩存"""
        print(f"開始預熱 {len(prompts)} 個提示...")

        for i, prompt in enumerate(prompts):
            messages = prompt.get("messages", [])
            try:
                self.cache_manager.completion_with_cache(
                    model=model,
                    messages=messages
                )
                print(f"  預熱 {i+1}/{len(prompts)} 完成")
            except Exception as e:
                print(f"  預熱 {i+1}/{len(prompts)} 失敗: {e}")

        print("預熱完成")


# ============================================================
# 7. 語義緩存
# ============================================================

SEMANTIC_CACHE_EXAMPLE = '''
# 語義緩存 - 基於語義相似度而非精確匹配

import litellm
from litellm.caching import Cache
import numpy as np

class SemanticCache:
    """語義緩存"""

    def __init__(self, similarity_threshold: float = 0.95):
        self.cache = {}
        self.embeddings = {}
        self.threshold = similarity_threshold

    def _get_embedding(self, text: str) -> np.ndarray:
        """獲取文本嵌入"""
        # 使用 OpenAI 嵌入 API
        response = litellm.embedding(
            model="text-embedding-ada-002",
            input=text
        )
        return np.array(response.data[0]["embedding"])

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """計算餘弦相似度"""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def get(self, query: str):
        """語義查找"""
        query_embedding = self._get_embedding(query)

        for cached_query, embedding in self.embeddings.items():
            similarity = self._cosine_similarity(query_embedding, embedding)
            if similarity >= self.threshold:
                return self.cache[cached_query]

        return None

    def set(self, query: str, response):
        """存儲結果"""
        self.cache[query] = response
        self.embeddings[query] = self._get_embedding(query)
'''


# ============================================================
# 使用範例
# ============================================================

def example_memory_cache():
    """範例 1: 內存緩存"""
    print("=" * 50)
    print("範例 1: 內存緩存")
    print("=" * 50)
    print(MEMORY_CACHE_EXAMPLE)


def example_redis_cache():
    """範例 2: Redis 緩存"""
    print("\n" + "=" * 50)
    print("範例 2: Redis 緩存")
    print("=" * 50)
    print(REDIS_CACHE_EXAMPLE)


def example_disk_cache():
    """範例 3: 磁盤緩存"""
    print("\n" + "=" * 50)
    print("範例 3: 磁盤緩存")
    print("=" * 50)
    print(DISK_CACHE_EXAMPLE)


def example_custom_cache():
    """範例 4: 自定義緩存"""
    print("\n" + "=" * 50)
    print("範例 4: 自定義緩存")
    print("=" * 50)

    cache = CustomCache(max_size=100, ttl=3600)

    # 模擬緩存操作
    messages = [{"role": "user", "content": "Hello"}]

    # 第一次獲取（未命中）
    result = cache.get("gpt-3.5-turbo", messages)
    print(f"第一次獲取: {result}")

    # 設置緩存
    cache.set("gpt-3.5-turbo", messages, {"response": "Hi!"})
    print("已設置緩存")

    # 第二次獲取（命中）
    result = cache.get("gpt-3.5-turbo", messages)
    print(f"第二次獲取: {result}")

    # 統計
    print(f"\n緩存統計: {cache.get_stats()}")


def example_cache_manager():
    """範例 5: 緩存管理器"""
    print("\n" + "=" * 50)
    print("範例 5: 緩存管理器")
    print("=" * 50)

    config = CacheConfig(
        enabled=True,
        type="custom",
        ttl=3600,
        max_size=1000
    )

    manager = CacheManager(config)
    print(f"緩存配置: {config}")
    print(f"緩存統計: {manager.get_stats()}")


def example_semantic_cache():
    """範例 6: 語義緩存"""
    print("\n" + "=" * 50)
    print("範例 6: 語義緩存")
    print("=" * 50)
    print(SEMANTIC_CACHE_EXAMPLE)


if __name__ == "__main__":
    print("LiteLLM 緩存策略範例\n")
    example_memory_cache()
    example_redis_cache()
    example_disk_cache()
    example_custom_cache()
    example_cache_manager()
    example_semantic_cache()

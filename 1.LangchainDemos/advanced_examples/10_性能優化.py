"""
LangChain 性能優化範例
=====================

本範例展示如何優化 LangChain 應用的性能。

優化類型：
1. 緩存策略
2. 批量處理
3. 異步執行
4. 資源管理

安裝依賴：
pip install langchain langchain-openai redis
"""

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from langchain.globals import set_llm_cache
from langchain.cache import InMemoryCache
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json

# ============================================================
# 1. 緩存策略
# ============================================================

CACHE_EXAMPLE = '''
from langchain.globals import set_llm_cache
from langchain.cache import InMemoryCache, SQLiteCache

# 方法 1: 內存緩存
set_llm_cache(InMemoryCache())

# 方法 2: SQLite 緩存（持久化）
set_llm_cache(SQLiteCache(database_path=".langchain.db"))

# 方法 3: Redis 緩存（分布式）
from langchain.cache import RedisCache
import redis
set_llm_cache(RedisCache(redis_=redis.Redis()))

# 使用（自動緩存）
llm = ChatOpenAI()
response1 = llm.invoke("Hello!")  # 調用 API
response2 = llm.invoke("Hello!")  # 從緩存返回
'''


class SmartCache:
    """智能緩存"""

    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.cache: Dict[str, Dict] = {}
        self.max_size = max_size
        self.ttl = ttl

    def _generate_key(self, prompt: str, model: str) -> str:
        """生成緩存鍵"""
        content = f"{model}:{prompt}"
        return hashlib.md5(content.encode()).hexdigest()

    def get(self, prompt: str, model: str) -> Optional[str]:
        """獲取緩存"""
        key = self._generate_key(prompt, model)
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry["time"] < self.ttl:
                return entry["response"]
            else:
                del self.cache[key]
        return None

    def set(self, prompt: str, model: str, response: str):
        """設置緩存"""
        if len(self.cache) >= self.max_size:
            # 清除最舊的條目
            oldest = min(self.cache.keys(), key=lambda k: self.cache[k]["time"])
            del self.cache[oldest]

        key = self._generate_key(prompt, model)
        self.cache[key] = {
            "response": response,
            "time": time.time()
        }

    def clear(self):
        """清空緩存"""
        self.cache.clear()


class CachedLLM:
    """帶緩存的 LLM"""

    def __init__(self, llm=None, cache: SmartCache = None):
        self.llm = llm or ChatOpenAI()
        self.cache = cache or SmartCache()
        self.stats = {"hits": 0, "misses": 0}

    def invoke(self, prompt: str) -> str:
        """帶緩存的調用"""
        model = self.llm.model_name

        # 檢查緩存
        cached = self.cache.get(prompt, model)
        if cached:
            self.stats["hits"] += 1
            return cached

        # 調用 LLM
        self.stats["misses"] += 1
        response = self.llm.invoke(prompt).content

        # 存入緩存
        self.cache.set(prompt, model, response)

        return response

    def get_stats(self) -> Dict[str, Any]:
        """獲取統計"""
        total = self.stats["hits"] + self.stats["misses"]
        return {
            **self.stats,
            "hit_rate": self.stats["hits"] / total if total > 0 else 0
        }


# ============================================================
# 2. 批量處理
# ============================================================

class BatchProcessor:
    """批量處理器"""

    def __init__(self, llm=None, batch_size: int = 10):
        self.llm = llm or ChatOpenAI()
        self.batch_size = batch_size

    def process_batch(self, prompts: List[str]) -> List[str]:
        """批量處理"""
        results = []

        for i in range(0, len(prompts), self.batch_size):
            batch = prompts[i:i + self.batch_size]
            batch_results = self.llm.batch(batch)
            results.extend([r.content for r in batch_results])

            print(f"處理進度: {min(i + self.batch_size, len(prompts))}/{len(prompts)}")

        return results

    async def process_batch_async(self, prompts: List[str]) -> List[str]:
        """異步批量處理"""
        tasks = [self.llm.ainvoke(p) for p in prompts]
        results = await asyncio.gather(*tasks)
        return [r.content for r in results]


BATCH_EXAMPLE = '''
# 批量處理

processor = BatchProcessor(batch_size=10)

prompts = [f"總結第 {i} 章" for i in range(50)]

# 同步批量
results = processor.process_batch(prompts)

# 異步批量
async def main():
    results = await processor.process_batch_async(prompts)
    return results

results = asyncio.run(main())
'''


# ============================================================
# 3. 異步優化
# ============================================================

class AsyncOptimizer:
    """異步優化器"""

    def __init__(self, llm=None, max_concurrent: int = 10):
        self.llm = llm or ChatOpenAI()
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def process_single(self, prompt: str) -> str:
        """處理單個請求"""
        async with self.semaphore:
            result = await self.llm.ainvoke(prompt)
            return result.content

    async def process_many(self, prompts: List[str]) -> List[str]:
        """處理多個請求"""
        tasks = [self.process_single(p) for p in prompts]
        return await asyncio.gather(*tasks)


ASYNC_EXAMPLE = '''
# 異步優化

optimizer = AsyncOptimizer(max_concurrent=10)

async def main():
    prompts = ["問題 " + str(i) for i in range(20)]

    start = time.time()
    results = await optimizer.process_many(prompts)
    elapsed = time.time() - start

    print(f"處理 {len(prompts)} 個請求，耗時: {elapsed:.2f}s")
    print(f"平均每個: {elapsed / len(prompts):.2f}s")

asyncio.run(main())
'''


# ============================================================
# 4. 連接池
# ============================================================

class LLMPool:
    """LLM 連接池"""

    def __init__(self, pool_size: int = 5, model: str = "gpt-3.5-turbo"):
        self.pool_size = pool_size
        self.model = model
        self.pool: List[ChatOpenAI] = []
        self.available: List[bool] = []
        self._initialize_pool()

    def _initialize_pool(self):
        """初始化連接池"""
        for _ in range(self.pool_size):
            self.pool.append(ChatOpenAI(model=self.model))
            self.available.append(True)

    def acquire(self) -> Optional[ChatOpenAI]:
        """獲取連接"""
        for i, is_available in enumerate(self.available):
            if is_available:
                self.available[i] = False
                return self.pool[i]
        return None

    def release(self, llm: ChatOpenAI):
        """釋放連接"""
        for i, pool_llm in enumerate(self.pool):
            if pool_llm is llm:
                self.available[i] = True
                break

    def execute(self, prompt: str) -> str:
        """使用連接池執行"""
        llm = self.acquire()
        if llm is None:
            raise Exception("無可用連接")

        try:
            result = llm.invoke(prompt)
            return result.content
        finally:
            self.release(llm)


POOL_EXAMPLE = '''
# 連接池使用

pool = LLMPool(pool_size=5)

# 使用連接池
result = pool.execute("Hello!")

# 並行使用
with ThreadPoolExecutor(max_workers=5) as executor:
    prompts = ["問題 " + str(i) for i in range(10)]
    results = list(executor.map(pool.execute, prompts))
'''


# ============================================================
# 5. 流式處理優化
# ============================================================

class StreamOptimizer:
    """流式處理優化器"""

    def __init__(self, llm=None):
        self.llm = llm or ChatOpenAI(streaming=True)
        self.total_tokens = 0

    def stream(self, prompt: str) -> str:
        """流式處理"""
        chunks = []
        for chunk in self.llm.stream(prompt):
            chunks.append(chunk.content)
            # 可以在這裡處理每個 chunk

        return "".join(chunks)

    async def stream_async(self, prompt: str) -> str:
        """異步流式處理"""
        chunks = []
        async for chunk in self.llm.astream(prompt):
            chunks.append(chunk.content)

        return "".join(chunks)


# ============================================================
# 6. 性能監控
# ============================================================

@dataclass
class PerformanceMetrics:
    """性能指標"""
    total_calls: int = 0
    total_time: float = 0.0
    total_tokens: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    errors: int = 0


class PerformanceMonitor:
    """性能監控器"""

    def __init__(self):
        self.metrics = PerformanceMetrics()
        self._start_times: Dict[str, float] = {}

    def start_call(self, call_id: str):
        """開始調用"""
        self._start_times[call_id] = time.time()

    def end_call(self, call_id: str, tokens: int = 0, from_cache: bool = False):
        """結束調用"""
        if call_id in self._start_times:
            elapsed = time.time() - self._start_times[call_id]
            self.metrics.total_time += elapsed
            self.metrics.total_calls += 1
            self.metrics.total_tokens += tokens

            if from_cache:
                self.metrics.cache_hits += 1
            else:
                self.metrics.cache_misses += 1

            del self._start_times[call_id]

    def record_error(self):
        """記錄錯誤"""
        self.metrics.errors += 1

    def get_report(self) -> Dict[str, Any]:
        """獲取報告"""
        total = self.metrics.cache_hits + self.metrics.cache_misses
        return {
            "total_calls": self.metrics.total_calls,
            "total_time": f"{self.metrics.total_time:.2f}s",
            "avg_time": f"{self.metrics.total_time / max(self.metrics.total_calls, 1):.3f}s",
            "total_tokens": self.metrics.total_tokens,
            "cache_hit_rate": self.metrics.cache_hits / total if total > 0 else 0,
            "error_rate": self.metrics.errors / max(self.metrics.total_calls, 1)
        }


# ============================================================
# 7. 優化建議生成器
# ============================================================

class OptimizationAdvisor:
    """優化建議生成器"""

    def __init__(self, monitor: PerformanceMonitor):
        self.monitor = monitor

    def get_recommendations(self) -> List[str]:
        """獲取優化建議"""
        recommendations = []
        report = self.monitor.get_report()

        # 分析緩存命中率
        cache_hit_rate = report["cache_hit_rate"]
        if cache_hit_rate < 0.3:
            recommendations.append("緩存命中率低，考慮啟用或調整緩存策略")

        # 分析平均響應時間
        avg_time = float(report["avg_time"].replace("s", ""))
        if avg_time > 2.0:
            recommendations.append("平均響應時間較長，考慮使用並行處理或更快的模型")

        # 分析錯誤率
        error_rate = report["error_rate"]
        if error_rate > 0.1:
            recommendations.append("錯誤率較高，考慮實現重試機制和錯誤處理")

        # 分析 token 使用
        if report["total_tokens"] > 100000:
            recommendations.append("Token 使用量大，考慮優化提示或使用摘要技術")

        if not recommendations:
            recommendations.append("目前性能良好，無需特別優化")

        return recommendations


# ============================================================
# 使用範例
# ============================================================

def example_cache():
    """範例 1: 緩存策略"""
    print("=" * 50)
    print("範例 1: 緩存策略")
    print("=" * 50)
    print(CACHE_EXAMPLE)


def example_smart_cache():
    """範例 2: 智能緩存"""
    print("\n" + "=" * 50)
    print("範例 2: 智能緩存")
    print("=" * 50)

    cache = SmartCache(max_size=100, ttl=3600)
    cached_llm = CachedLLM(cache=cache)

    # 模擬使用
    print("緩存配置:")
    print(f"  最大大小: {cache.max_size}")
    print(f"  TTL: {cache.ttl}s")


def example_batch():
    """範例 3: 批量處理"""
    print("\n" + "=" * 50)
    print("範例 3: 批量處理")
    print("=" * 50)
    print(BATCH_EXAMPLE)


def example_async():
    """範例 4: 異步優化"""
    print("\n" + "=" * 50)
    print("範例 4: 異步優化")
    print("=" * 50)
    print(ASYNC_EXAMPLE)


def example_pool():
    """範例 5: 連接池"""
    print("\n" + "=" * 50)
    print("範例 5: 連接池")
    print("=" * 50)
    print(POOL_EXAMPLE)


def example_monitoring():
    """範例 6: 性能監控"""
    print("\n" + "=" * 50)
    print("範例 6: 性能監控")
    print("=" * 50)

    monitor = PerformanceMonitor()

    # 模擬調用
    for i in range(10):
        monitor.start_call(f"call_{i}")
        time.sleep(0.01)  # 模擬延遲
        monitor.end_call(f"call_{i}", tokens=100, from_cache=i % 3 == 0)

    report = monitor.get_report()
    print(f"性能報告: {json.dumps(report, indent=2)}")


def example_advisor():
    """範例 7: 優化建議"""
    print("\n" + "=" * 50)
    print("範例 7: 優化建議")
    print("=" * 50)

    monitor = PerformanceMonitor()

    # 模擬數據
    for i in range(20):
        monitor.start_call(f"call_{i}")
        monitor.end_call(f"call_{i}", tokens=500, from_cache=False)

    advisor = OptimizationAdvisor(monitor)
    recommendations = advisor.get_recommendations()

    print("優化建議:")
    for rec in recommendations:
        print(f"  - {rec}")


if __name__ == "__main__":
    print("LangChain 性能優化範例\n")
    example_cache()
    example_smart_cache()
    example_batch()
    example_async()
    example_pool()
    example_monitoring()
    example_advisor()

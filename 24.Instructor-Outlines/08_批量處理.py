"""
Instructor/Outlines 批量處理範例
================================

本範例展示如何進行批量數據處理和並行生成。

功能：
1. 批量 API 調用
2. 並行處理
3. 錯誤處理和重試
4. 進度追蹤

安裝依賴：
pip install instructor outlines asyncio tqdm
"""

import instructor
from openai import OpenAI, AsyncOpenAI
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import asyncio
from dataclasses import dataclass
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# ============================================================
# 1. 定義數據模型
# ============================================================

class SentimentResult(BaseModel):
    """情感分析結果"""
    text: str = Field(description="原始文本")
    sentiment: str = Field(description="情感: positive/negative/neutral")
    confidence: float = Field(ge=0, le=1, description="置信度")
    keywords: List[str] = Field(default_factory=list, description="關鍵詞")


class ClassificationResult(BaseModel):
    """分類結果"""
    text: str
    category: str
    sub_category: Optional[str] = None
    confidence: float


class EntityExtractionResult(BaseModel):
    """實體提取結果"""
    text: str
    entities: List[Dict[str, str]]
    summary: str


# ============================================================
# 2. 同步批量處理
# ============================================================

class BatchProcessor:
    """同步批量處理器"""

    def __init__(self, model: str = "gpt-3.5-turbo"):
        self.client = instructor.from_openai(OpenAI())
        self.model = model
        self.results = []
        self.errors = []

    def process_single(
        self,
        text: str,
        response_model: type,
        system_prompt: str = None
    ) -> Any:
        """處理單個項目"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": text})

        return self.client.chat.completions.create(
            model=self.model,
            response_model=response_model,
            messages=messages
        )

    def process_batch(
        self,
        items: List[str],
        response_model: type,
        system_prompt: str = None,
        max_retries: int = 3
    ) -> List[Any]:
        """批量處理"""
        results = []

        for i, item in enumerate(items):
            print(f"處理 {i+1}/{len(items)}...")

            for attempt in range(max_retries):
                try:
                    result = self.process_single(item, response_model, system_prompt)
                    results.append(result)
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        self.errors.append({"item": item, "error": str(e)})
                        results.append(None)
                    else:
                        time.sleep(1 * (attempt + 1))

        self.results = results
        return results

    def get_successful_results(self) -> List[Any]:
        """獲取成功的結果"""
        return [r for r in self.results if r is not None]


SYNC_BATCH_EXAMPLE = '''
# 同步批量處理範例
processor = BatchProcessor(model="gpt-3.5-turbo")

texts = [
    "這個產品非常棒！",
    "服務太差了，不推薦",
    "還可以，一般般"
]

results = processor.process_batch(
    items=texts,
    response_model=SentimentResult,
    system_prompt="分析文本情感"
)

for result in results:
    if result:
        print(f"{result.text}: {result.sentiment}")
'''


# ============================================================
# 3. 異步批量處理
# ============================================================

class AsyncBatchProcessor:
    """異步批量處理器"""

    def __init__(self, model: str = "gpt-3.5-turbo", max_concurrent: int = 5):
        self.client = instructor.from_openai(AsyncOpenAI())
        self.model = model
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def process_single(
        self,
        text: str,
        response_model: type,
        system_prompt: str = None
    ) -> Any:
        """異步處理單個項目"""
        async with self.semaphore:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": text})

            return await self.client.chat.completions.create(
                model=self.model,
                response_model=response_model,
                messages=messages
            )

    async def process_batch(
        self,
        items: List[str],
        response_model: type,
        system_prompt: str = None
    ) -> List[Any]:
        """異步批量處理"""
        tasks = [
            self.process_single(item, response_model, system_prompt)
            for item in items
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 處理結果
        processed = []
        for item, result in zip(items, results):
            if isinstance(result, Exception):
                processed.append({"item": item, "error": str(result), "result": None})
            else:
                processed.append({"item": item, "error": None, "result": result})

        return processed


ASYNC_BATCH_EXAMPLE = '''
import asyncio

# 異步批量處理範例
async def main():
    processor = AsyncBatchProcessor(max_concurrent=5)

    texts = [f"文本 {i}" for i in range(20)]

    results = await processor.process_batch(
        items=texts,
        response_model=SentimentResult,
        system_prompt="分析情感"
    )

    for r in results:
        if r["result"]:
            print(f"{r['item']}: {r['result'].sentiment}")

asyncio.run(main())
'''


# ============================================================
# 4. 線程池批量處理
# ============================================================

class ThreadPoolBatchProcessor:
    """線程池批量處理器"""

    def __init__(self, model: str = "gpt-3.5-turbo", max_workers: int = 5):
        self.model = model
        self.max_workers = max_workers

    def _process_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """處理單個項目（在線程中執行）"""
        client = instructor.from_openai(OpenAI())

        try:
            result = client.chat.completions.create(
                model=self.model,
                response_model=item["response_model"],
                messages=item["messages"]
            )
            return {"item": item["text"], "result": result, "error": None}
        except Exception as e:
            return {"item": item["text"], "result": None, "error": str(e)}

    def process_batch(
        self,
        items: List[str],
        response_model: type,
        system_prompt: str = None
    ) -> List[Dict[str, Any]]:
        """使用線程池批量處理"""
        # 準備任務
        tasks = []
        for text in items:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": text})

            tasks.append({
                "text": text,
                "response_model": response_model,
                "messages": messages
            })

        # 執行
        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self._process_item, task): task for task in tasks}

            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                print(f"完成: {result['item'][:30]}...")

        return results


# ============================================================
# 5. 帶進度追蹤的處理器
# ============================================================

@dataclass
class ProcessingStats:
    """處理統計"""
    total: int = 0
    completed: int = 0
    successful: int = 0
    failed: int = 0
    start_time: float = 0
    end_time: float = 0

    @property
    def success_rate(self) -> float:
        return self.successful / self.completed if self.completed > 0 else 0

    @property
    def elapsed_time(self) -> float:
        return self.end_time - self.start_time if self.end_time else time.time() - self.start_time

    @property
    def avg_time_per_item(self) -> float:
        return self.elapsed_time / self.completed if self.completed > 0 else 0


class TrackedBatchProcessor:
    """帶追蹤的批量處理器"""

    def __init__(self, model: str = "gpt-3.5-turbo"):
        self.client = instructor.from_openai(OpenAI())
        self.model = model
        self.stats = ProcessingStats()
        self.progress_callback = None

    def set_progress_callback(self, callback):
        """設置進度回調"""
        self.progress_callback = callback

    def process_batch(
        self,
        items: List[str],
        response_model: type,
        system_prompt: str = None
    ) -> List[Any]:
        """帶進度追蹤的批量處理"""
        self.stats = ProcessingStats(total=len(items))
        self.stats.start_time = time.time()

        results = []

        for i, item in enumerate(items):
            try:
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": item})

                result = self.client.chat.completions.create(
                    model=self.model,
                    response_model=response_model,
                    messages=messages
                )
                results.append(result)
                self.stats.successful += 1

            except Exception as e:
                results.append(None)
                self.stats.failed += 1

            self.stats.completed += 1

            # 調用進度回調
            if self.progress_callback:
                self.progress_callback(self.stats)

        self.stats.end_time = time.time()
        return results


TRACKED_EXAMPLE = '''
# 帶進度追蹤的處理
def progress_callback(stats):
    pct = stats.completed / stats.total * 100
    print(f"進度: {pct:.1f}% ({stats.completed}/{stats.total})")
    print(f"  成功率: {stats.success_rate:.1%}")
    print(f"  平均耗時: {stats.avg_time_per_item:.2f}s")

processor = TrackedBatchProcessor()
processor.set_progress_callback(progress_callback)

results = processor.process_batch(
    items=texts,
    response_model=SentimentResult,
    system_prompt="分析情感"
)
'''


# ============================================================
# 6. 批量分塊處理
# ============================================================

class ChunkedBatchProcessor:
    """分塊批量處理器"""

    def __init__(self, model: str = "gpt-3.5-turbo", chunk_size: int = 10):
        self.client = instructor.from_openai(OpenAI())
        self.model = model
        self.chunk_size = chunk_size

    def _chunk_items(self, items: List[Any]) -> List[List[Any]]:
        """將項目分塊"""
        return [items[i:i + self.chunk_size] for i in range(0, len(items), self.chunk_size)]

    def process_batch(
        self,
        items: List[str],
        response_model: type,
        system_prompt: str = None,
        delay_between_chunks: float = 1.0
    ) -> List[Any]:
        """分塊批量處理"""
        chunks = self._chunk_items(items)
        all_results = []

        for i, chunk in enumerate(chunks):
            print(f"處理塊 {i+1}/{len(chunks)} ({len(chunk)} 項)...")

            for item in chunk:
                try:
                    messages = []
                    if system_prompt:
                        messages.append({"role": "system", "content": system_prompt})
                    messages.append({"role": "user", "content": item})

                    result = self.client.chat.completions.create(
                        model=self.model,
                        response_model=response_model,
                        messages=messages
                    )
                    all_results.append(result)
                except Exception as e:
                    all_results.append(None)

            # 塊之間延遲（避免速率限制）
            if i < len(chunks) - 1:
                time.sleep(delay_between_chunks)

        return all_results


# ============================================================
# 7. 結果聚合
# ============================================================

class ResultAggregator:
    """結果聚合器"""

    def __init__(self, results: List[Any]):
        self.results = [r for r in results if r is not None]

    def count_by_field(self, field: str) -> Dict[str, int]:
        """按字段統計"""
        counts = {}
        for r in self.results:
            value = getattr(r, field, None)
            if value:
                counts[value] = counts.get(value, 0) + 1
        return counts

    def average_field(self, field: str) -> float:
        """計算字段平均值"""
        values = [getattr(r, field, 0) for r in self.results]
        return sum(values) / len(values) if values else 0

    def filter_by(self, field: str, value: Any) -> List[Any]:
        """按字段過濾"""
        return [r for r in self.results if getattr(r, field, None) == value]

    def to_dict_list(self) -> List[Dict]:
        """轉換為字典列表"""
        return [r.model_dump() if hasattr(r, 'model_dump') else dict(r) for r in self.results]


# ============================================================
# 使用範例
# ============================================================

def example_sync_batch():
    """範例 1: 同步批量"""
    print("=" * 50)
    print("範例 1: 同步批量處理")
    print("=" * 50)
    print(SYNC_BATCH_EXAMPLE)


def example_async_batch():
    """範例 2: 異步批量"""
    print("\n" + "=" * 50)
    print("範例 2: 異步批量處理")
    print("=" * 50)
    print(ASYNC_BATCH_EXAMPLE)


def example_threadpool():
    """範例 3: 線程池"""
    print("\n" + "=" * 50)
    print("範例 3: 線程池批量處理")
    print("=" * 50)

    print("""
processor = ThreadPoolBatchProcessor(max_workers=5)

results = processor.process_batch(
    items=texts,
    response_model=SentimentResult,
    system_prompt="分析情感"
)

for r in results:
    if r['result']:
        print(f"{r['item']}: {r['result'].sentiment}")
""")


def example_tracked():
    """範例 4: 進度追蹤"""
    print("\n" + "=" * 50)
    print("範例 4: 帶進度追蹤的處理")
    print("=" * 50)
    print(TRACKED_EXAMPLE)


def example_chunked():
    """範例 5: 分塊處理"""
    print("\n" + "=" * 50)
    print("範例 5: 分塊批量處理")
    print("=" * 50)

    print("""
processor = ChunkedBatchProcessor(chunk_size=10)

results = processor.process_batch(
    items=large_text_list,
    response_model=SentimentResult,
    delay_between_chunks=2.0  # 塊之間等待 2 秒
)
""")


def example_aggregation():
    """範例 6: 結果聚合"""
    print("\n" + "=" * 50)
    print("範例 6: 結果聚合分析")
    print("=" * 50)

    print("""
aggregator = ResultAggregator(results)

# 統計情感分布
sentiment_counts = aggregator.count_by_field("sentiment")
print(f"情感分布: {sentiment_counts}")

# 計算平均置信度
avg_confidence = aggregator.average_field("confidence")
print(f"平均置信度: {avg_confidence:.2f}")

# 過濾正面評論
positive = aggregator.filter_by("sentiment", "positive")
print(f"正面評論數: {len(positive)}")
""")


if __name__ == "__main__":
    print("Instructor/Outlines 批量處理範例\n")
    example_sync_batch()
    example_async_batch()
    example_threadpool()
    example_tracked()
    example_chunked()
    example_aggregation()

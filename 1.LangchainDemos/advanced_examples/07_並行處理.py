"""
LangChain 並行處理範例
=====================

本範例展示如何在 LangChain 中實現並行處理。

並行方式：
1. RunnableParallel
2. 異步並行
3. 批量處理
4. Map-Reduce 模式

安裝依賴：
pip install langchain langchain-openai
"""

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnableLambda, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from typing import List, Dict, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# ============================================================
# 1. RunnableParallel 基礎
# ============================================================

PARALLEL_BASIC_EXAMPLE = '''
from langchain_core.runnables import RunnableParallel
from langchain_openai import ChatOpenAI

llm = ChatOpenAI()

# 定義多個處理鏈
summarize_prompt = ChatPromptTemplate.from_template("總結: {text}")
translate_prompt = ChatPromptTemplate.from_template("翻譯成英文: {text}")
keywords_prompt = ChatPromptTemplate.from_template("提取關鍵詞: {text}")

# 並行執行
parallel_chain = RunnableParallel(
    summary=summarize_prompt | llm | StrOutputParser(),
    translation=translate_prompt | llm | StrOutputParser(),
    keywords=keywords_prompt | llm | StrOutputParser()
)

# 使用
result = parallel_chain.invoke({"text": "人工智能正在改變世界..."})

print(f"摘要: {result['summary']}")
print(f"翻譯: {result['translation']}")
print(f"關鍵詞: {result['keywords']}")
'''


# ============================================================
# 2. 並行處理器類
# ============================================================

class ParallelProcessor:
    """並行處理器"""

    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self.tasks: Dict[str, callable] = {}

    def add_task(self, name: str, func: callable):
        """添加任務"""
        self.tasks[name] = func

    def execute_sync(self, input_data: Any) -> Dict[str, Any]:
        """同步並行執行（使用線程池）"""
        results = {}

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(func, input_data): name
                for name, func in self.tasks.items()
            }

            for future in as_completed(futures):
                name = futures[future]
                try:
                    results[name] = future.result()
                except Exception as e:
                    results[name] = {"error": str(e)}

        return results

    async def execute_async(self, input_data: Any) -> Dict[str, Any]:
        """異步並行執行"""
        async def run_task(name: str, func: callable):
            try:
                if asyncio.iscoroutinefunction(func):
                    return name, await func(input_data)
                else:
                    return name, func(input_data)
            except Exception as e:
                return name, {"error": str(e)}

        tasks = [run_task(name, func) for name, func in self.tasks.items()]
        results = await asyncio.gather(*tasks)

        return dict(results)


PARALLEL_PROCESSOR_EXAMPLE = '''
# 並行處理器使用

processor = ParallelProcessor(max_workers=5)

# 添加任務
processor.add_task("task1", lambda x: f"Task 1 處理: {x}")
processor.add_task("task2", lambda x: f"Task 2 處理: {x}")
processor.add_task("task3", lambda x: f"Task 3 處理: {x}")

# 同步執行
results = processor.execute_sync("輸入數據")

# 異步執行
async def main():
    results = await processor.execute_async("輸入數據")
    return results

results = asyncio.run(main())
'''


# ============================================================
# 3. 批量並行處理
# ============================================================

class BatchParallelProcessor:
    """批量並行處理器"""

    def __init__(self, llm=None, batch_size: int = 10, max_workers: int = 5):
        self.llm = llm or ChatOpenAI()
        self.batch_size = batch_size
        self.max_workers = max_workers

    def _process_single(self, item: str, prompt_template: str) -> str:
        """處理單個項目"""
        prompt = ChatPromptTemplate.from_template(prompt_template)
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({"input": item})

    def process_batch(
        self,
        items: List[str],
        prompt_template: str
    ) -> List[str]:
        """批量處理"""
        results = [None] * len(items)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._process_single, item, prompt_template): i
                for i, item in enumerate(items)
            }

            for future in as_completed(futures):
                idx = futures[future]
                try:
                    results[idx] = future.result()
                except Exception as e:
                    results[idx] = f"Error: {e}"

        return results

    async def process_batch_async(
        self,
        items: List[str],
        prompt_template: str
    ) -> List[str]:
        """異步批量處理"""
        prompt = ChatPromptTemplate.from_template(prompt_template)
        chain = prompt | self.llm | StrOutputParser()

        tasks = [chain.ainvoke({"input": item}) for item in items]
        return await asyncio.gather(*tasks, return_exceptions=True)


BATCH_EXAMPLE = '''
# 批量並行處理

processor = BatchParallelProcessor(batch_size=10, max_workers=5)

texts = [
    "文本 1",
    "文本 2",
    "文本 3",
    # ...更多文本
]

# 同步批量處理
results = processor.process_batch(
    items=texts,
    prompt_template="總結以下內容: {input}"
)

# 異步批量處理
async def main():
    results = await processor.process_batch_async(
        items=texts,
        prompt_template="總結以下內容: {input}"
    )
    return results

results = asyncio.run(main())
'''


# ============================================================
# 4. Map-Reduce 模式
# ============================================================

class MapReduceProcessor:
    """Map-Reduce 處理器"""

    def __init__(self, llm=None):
        self.llm = llm or ChatOpenAI()

    def map_process(
        self,
        items: List[str],
        map_prompt: str,
        max_workers: int = 5
    ) -> List[str]:
        """Map 階段"""
        prompt = ChatPromptTemplate.from_template(map_prompt)
        chain = prompt | self.llm | StrOutputParser()

        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(chain.invoke, {"input": item}) for item in items]
            for future in as_completed(futures):
                results.append(future.result())

        return results

    def reduce_process(
        self,
        items: List[str],
        reduce_prompt: str
    ) -> str:
        """Reduce 階段"""
        combined = "\n---\n".join(items)
        prompt = ChatPromptTemplate.from_template(reduce_prompt)
        chain = prompt | self.llm | StrOutputParser()

        return chain.invoke({"input": combined})

    def map_reduce(
        self,
        items: List[str],
        map_prompt: str,
        reduce_prompt: str
    ) -> str:
        """完整 Map-Reduce"""
        # Map
        mapped_results = self.map_process(items, map_prompt)

        # Reduce
        final_result = self.reduce_process(mapped_results, reduce_prompt)

        return final_result


MAP_REDUCE_EXAMPLE = '''
# Map-Reduce 模式

processor = MapReduceProcessor()

# 文檔列表
documents = [
    "第一章內容...",
    "第二章內容...",
    "第三章內容...",
]

# Map: 總結每個文檔
# Reduce: 合併所有摘要

result = processor.map_reduce(
    items=documents,
    map_prompt="總結以下內容: {input}",
    reduce_prompt="整合以下摘要成為一份完整報告: {input}"
)

print(result)
'''


# ============================================================
# 5. 扇出-扇入模式
# ============================================================

class FanOutFanInProcessor:
    """扇出-扇入處理器"""

    def __init__(self, llm=None):
        self.llm = llm or ChatOpenAI()
        self.processors: Dict[str, callable] = {}

    def add_processor(self, name: str, func: callable):
        """添加處理器"""
        self.processors[name] = func

    def fan_out(self, input_data: Any) -> Dict[str, Any]:
        """扇出：發送到所有處理器"""
        results = {}

        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(func, input_data): name
                for name, func in self.processors.items()
            }

            for future in as_completed(futures):
                name = futures[future]
                results[name] = future.result()

        return results

    def fan_in(self, results: Dict[str, Any], aggregator: callable) -> Any:
        """扇入：聚合結果"""
        return aggregator(results)

    def process(self, input_data: Any, aggregator: callable) -> Any:
        """完整處理"""
        # 扇出
        intermediate = self.fan_out(input_data)

        # 扇入
        final = self.fan_in(intermediate, aggregator)

        return final


FAN_EXAMPLE = '''
# 扇出-扇入模式

processor = FanOutFanInProcessor()

# 添加多個分析器
processor.add_processor("sentiment", analyze_sentiment)
processor.add_processor("topics", extract_topics)
processor.add_processor("entities", extract_entities)

# 聚合函數
def aggregate(results):
    return {
        "sentiment": results["sentiment"],
        "topics": results["topics"],
        "entities": results["entities"],
        "combined_score": calculate_score(results)
    }

# 處理
result = processor.process(
    input_data="分析這段文本...",
    aggregator=aggregate
)
'''


# ============================================================
# 6. 流水線並行
# ============================================================

class PipelineParallel:
    """流水線並行處理器"""

    def __init__(self):
        self.stages: List[List[callable]] = []

    def add_stage(self, processors: List[callable]):
        """添加並行階段"""
        self.stages.append(processors)

    def process(self, input_data: Any) -> List[Any]:
        """處理數據"""
        current_data = [input_data]

        for stage in self.stages:
            next_data = []

            with ThreadPoolExecutor() as executor:
                for data in current_data:
                    futures = [executor.submit(proc, data) for proc in stage]
                    for future in as_completed(futures):
                        result = future.result()
                        if isinstance(result, list):
                            next_data.extend(result)
                        else:
                            next_data.append(result)

            current_data = next_data

        return current_data


# ============================================================
# 使用範例
# ============================================================

def example_basic_parallel():
    """範例 1: 基礎並行"""
    print("=" * 50)
    print("範例 1: RunnableParallel 基礎")
    print("=" * 50)
    print(PARALLEL_BASIC_EXAMPLE)


def example_processor():
    """範例 2: 並行處理器"""
    print("\n" + "=" * 50)
    print("範例 2: 並行處理器")
    print("=" * 50)
    print(PARALLEL_PROCESSOR_EXAMPLE)


def example_batch():
    """範例 3: 批量處理"""
    print("\n" + "=" * 50)
    print("範例 3: 批量並行處理")
    print("=" * 50)
    print(BATCH_EXAMPLE)


def example_map_reduce():
    """範例 4: Map-Reduce"""
    print("\n" + "=" * 50)
    print("範例 4: Map-Reduce 模式")
    print("=" * 50)
    print(MAP_REDUCE_EXAMPLE)


def example_fan():
    """範例 5: 扇出-扇入"""
    print("\n" + "=" * 50)
    print("範例 5: 扇出-扇入模式")
    print("=" * 50)
    print(FAN_EXAMPLE)


def example_pipeline():
    """範例 6: 流水線並行"""
    print("\n" + "=" * 50)
    print("範例 6: 流水線並行")
    print("=" * 50)

    print("""
# 流水線並行處理

pipeline = PipelineParallel()

# 第一階段：並行預處理
pipeline.add_stage([clean_text, normalize_text])

# 第二階段：並行分析
pipeline.add_stage([analyze_sentiment, extract_keywords])

# 處理
results = pipeline.process("輸入文本...")
""")


def example_timing():
    """範例 7: 性能比較"""
    print("\n" + "=" * 50)
    print("範例 7: 並行 vs 順序性能比較")
    print("=" * 50)

    def slow_task(x):
        time.sleep(0.1)
        return x

    items = list(range(10))

    # 順序執行
    start = time.time()
    _ = [slow_task(i) for i in items]
    sequential_time = time.time() - start

    # 並行執行
    start = time.time()
    with ThreadPoolExecutor(max_workers=5) as executor:
        _ = list(executor.map(slow_task, items))
    parallel_time = time.time() - start

    print(f"順序執行: {sequential_time:.2f}s")
    print(f"並行執行: {parallel_time:.2f}s")
    print(f"加速比: {sequential_time / parallel_time:.2f}x")


if __name__ == "__main__":
    print("LangChain 並行處理範例\n")
    example_basic_parallel()
    example_processor()
    example_batch()
    example_map_reduce()
    example_fan()
    example_pipeline()
    example_timing()

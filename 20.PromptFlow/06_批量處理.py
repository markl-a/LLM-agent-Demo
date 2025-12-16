"""
PromptFlow 批量處理範例
======================

本範例展示如何在 PromptFlow 中進行批量數據處理。

批量處理功能：
1. 批量運行 Flow
2. 並行處理
3. 錯誤處理
4. 結果收集
5. 進度追蹤

安裝依賴：
pip install promptflow promptflow-tools pandas
"""

import os
import json
import time
from typing import Dict, Any, List, Optional, Callable, Generator
from dataclasses import dataclass, field
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# ============================================================
# 批量處理數據結構
# ============================================================

@dataclass
class BatchInput:
    """批量輸入項"""
    id: str
    data: Dict[str, Any]


@dataclass
class BatchOutput:
    """批量輸出項"""
    id: str
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    status: str = "pending"  # pending, running, success, failed
    error: Optional[str] = None
    latency_ms: float = 0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class BatchRunResult:
    """批量運行結果"""
    total: int
    succeeded: int
    failed: int
    outputs: List[BatchOutput]
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: float = 0


# ============================================================
# 批量處理器
# ============================================================

class BatchProcessor:
    """
    批量處理器

    管理和執行批量數據處理
    """

    def __init__(
        self,
        max_workers: int = 5,
        retry_count: int = 3,
        retry_delay: float = 1.0
    ):
        self.max_workers = max_workers
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        self._progress_lock = threading.Lock()
        self._processed_count = 0

    def process_batch(
        self,
        inputs: List[BatchInput],
        processor_func: Callable[[Dict[str, Any]], Dict[str, Any]],
        on_progress: Optional[Callable[[int, int], None]] = None
    ) -> BatchRunResult:
        """
        處理批量數據

        Args:
            inputs: 輸入數據列表
            processor_func: 處理函數
            on_progress: 進度回調

        Returns:
            批量運行結果
        """
        start_time = datetime.now()
        outputs: List[BatchOutput] = []
        self._processed_count = 0

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(
                    self._process_single,
                    item,
                    processor_func
                ): item
                for item in inputs
            }

            for future in as_completed(futures):
                output = future.result()
                outputs.append(output)

                with self._progress_lock:
                    self._processed_count += 1
                    if on_progress:
                        on_progress(self._processed_count, len(inputs))

        end_time = datetime.now()

        # 統計結果
        succeeded = sum(1 for o in outputs if o.status == "success")
        failed = sum(1 for o in outputs if o.status == "failed")

        return BatchRunResult(
            total=len(inputs),
            succeeded=succeeded,
            failed=failed,
            outputs=outputs,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=(end_time - start_time).total_seconds()
        )

    def _process_single(
        self,
        item: BatchInput,
        processor_func: Callable[[Dict[str, Any]], Dict[str, Any]]
    ) -> BatchOutput:
        """處理單個項目"""
        output = BatchOutput(
            id=item.id,
            input_data=item.data,
            status="running"
        )

        start_time = time.time()

        for attempt in range(self.retry_count + 1):
            try:
                result = processor_func(item.data)
                output.output_data = result
                output.status = "success"
                break
            except Exception as e:
                if attempt < self.retry_count:
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    output.status = "failed"
                    output.error = str(e)

        output.latency_ms = (time.time() - start_time) * 1000
        output.timestamp = datetime.now()

        return output

    def process_stream(
        self,
        inputs: Generator[BatchInput, None, None],
        processor_func: Callable[[Dict[str, Any]], Dict[str, Any]],
        batch_size: int = 10
    ) -> Generator[BatchOutput, None, None]:
        """
        流式處理批量數據

        Args:
            inputs: 輸入數據生成器
            processor_func: 處理函數
            batch_size: 批次大小

        Yields:
            處理結果
        """
        batch = []

        for item in inputs:
            batch.append(item)

            if len(batch) >= batch_size:
                results = self.process_batch(batch, processor_func)
                for output in results.outputs:
                    yield output
                batch = []

        # 處理剩餘的項目
        if batch:
            results = self.process_batch(batch, processor_func)
            for output in results.outputs:
                yield output


# ============================================================
# 數據加載器
# ============================================================

class DataLoader:
    """
    數據加載器

    從各種來源加載批量數據
    """

    @staticmethod
    def from_json_file(file_path: str) -> List[BatchInput]:
        """從 JSON 文件加載"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return [
            BatchInput(id=str(i), data=item)
            for i, item in enumerate(data)
        ]

    @staticmethod
    def from_jsonl_file(file_path: str) -> Generator[BatchInput, None, None]:
        """從 JSONL 文件流式加載"""
        with open(file_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if line.strip():
                    yield BatchInput(id=str(i), data=json.loads(line))

    @staticmethod
    def from_csv_file(file_path: str) -> List[BatchInput]:
        """從 CSV 文件加載"""
        import csv
        results = []

        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                results.append(BatchInput(id=str(i), data=dict(row)))

        return results

    @staticmethod
    def from_list(data_list: List[Dict[str, Any]]) -> List[BatchInput]:
        """從列表加載"""
        return [
            BatchInput(id=str(i), data=item)
            for i, item in enumerate(data_list)
        ]


# ============================================================
# 結果導出器
# ============================================================

class ResultExporter:
    """
    結果導出器

    將批量處理結果導出到各種格式
    """

    @staticmethod
    def to_json_file(result: BatchRunResult, file_path: str):
        """導出到 JSON 文件"""
        data = {
            "summary": {
                "total": result.total,
                "succeeded": result.succeeded,
                "failed": result.failed,
                "duration_seconds": result.duration_seconds,
                "start_time": result.start_time.isoformat(),
                "end_time": result.end_time.isoformat() if result.end_time else None
            },
            "outputs": [
                {
                    "id": o.id,
                    "status": o.status,
                    "input": o.input_data,
                    "output": o.output_data,
                    "error": o.error,
                    "latency_ms": o.latency_ms
                }
                for o in result.outputs
            ]
        }

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def to_jsonl_file(result: BatchRunResult, file_path: str):
        """導出到 JSONL 文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            for o in result.outputs:
                line = json.dumps({
                    "id": o.id,
                    "status": o.status,
                    "input": o.input_data,
                    "output": o.output_data,
                    "error": o.error
                }, ensure_ascii=False)
                f.write(line + '\n')

    @staticmethod
    def to_csv_file(result: BatchRunResult, file_path: str):
        """導出到 CSV 文件"""
        import csv

        with open(file_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'status', 'input', 'output', 'error', 'latency_ms'])

            for o in result.outputs:
                writer.writerow([
                    o.id,
                    o.status,
                    json.dumps(o.input_data, ensure_ascii=False),
                    json.dumps(o.output_data, ensure_ascii=False) if o.output_data else '',
                    o.error or '',
                    o.latency_ms
                ])


# ============================================================
# 模擬 Flow 處理函數
# ============================================================

def mock_qa_flow(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    模擬問答 Flow

    Args:
        inputs: 包含 question 字段

    Returns:
        包含 answer 字段的結果
    """
    time.sleep(0.1)  # 模擬處理延遲

    question = inputs.get("question", "")

    # 模擬回答
    return {
        "answer": f"這是對「{question}」的回答",
        "confidence": 0.95
    }


def mock_classification_flow(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    模擬分類 Flow

    Args:
        inputs: 包含 text 字段

    Returns:
        包含 category 字段的結果
    """
    time.sleep(0.1)

    text = inputs.get("text", "")

    # 簡單分類邏輯
    categories = ["科技", "體育", "娛樂", "財經"]
    import hashlib
    idx = int(hashlib.md5(text.encode()).hexdigest(), 16) % len(categories)

    return {
        "category": categories[idx],
        "score": 0.85 + (idx * 0.03)
    }


# ============================================================
# 使用範例
# ============================================================

def example_basic_batch():
    """
    範例 1: 基礎批量處理

    展示簡單的批量處理
    """
    print("=" * 50)
    print("範例 1: 基礎批量處理")
    print("=" * 50)

    # 準備數據
    data = [
        {"question": "什麼是人工智能？"},
        {"question": "Python 有什麼特點？"},
        {"question": "機器學習和深度學習有什麼區別？"},
    ]

    inputs = DataLoader.from_list(data)

    # 創建處理器
    processor = BatchProcessor(max_workers=3)

    # 進度回調
    def on_progress(current: int, total: int):
        print(f"\r處理進度: {current}/{total}", end="")

    # 執行批量處理
    result = processor.process_batch(
        inputs=inputs,
        processor_func=mock_qa_flow,
        on_progress=on_progress
    )

    print(f"\n\n處理完成:")
    print(f"  總數: {result.total}")
    print(f"  成功: {result.succeeded}")
    print(f"  失敗: {result.failed}")
    print(f"  耗時: {result.duration_seconds:.2f}s")


def example_parallel_processing():
    """
    範例 2: 並行處理

    展示多線程並行處理
    """
    print("\n" + "=" * 50)
    print("範例 2: 並行處理")
    print("=" * 50)

    # 準備更多數據
    data = [{"text": f"這是第 {i} 條測試文本"} for i in range(10)]
    inputs = DataLoader.from_list(data)

    # 不同並行度測試
    for workers in [1, 3, 5]:
        processor = BatchProcessor(max_workers=workers)

        start = time.time()
        result = processor.process_batch(inputs, mock_classification_flow)
        elapsed = time.time() - start

        print(f"並行度 {workers}: 耗時 {elapsed:.2f}s, 成功 {result.succeeded}/{result.total}")


def example_error_handling():
    """
    範例 3: 錯誤處理

    展示批量處理中的錯誤處理
    """
    print("\n" + "=" * 50)
    print("範例 3: 錯誤處理")
    print("=" * 50)

    def flaky_processor(inputs: Dict[str, Any]) -> Dict[str, Any]:
        """可能失敗的處理函數"""
        import random
        if random.random() < 0.3:
            raise Exception("隨機錯誤")
        return {"result": "success"}

    data = [{"id": i} for i in range(10)]
    inputs = DataLoader.from_list(data)

    processor = BatchProcessor(max_workers=3, retry_count=2)
    result = processor.process_batch(inputs, flaky_processor)

    print(f"總數: {result.total}")
    print(f"成功: {result.succeeded}")
    print(f"失敗: {result.failed}")

    # 顯示失敗的項目
    failed = [o for o in result.outputs if o.status == "failed"]
    if failed:
        print(f"\n失敗的項目:")
        for o in failed:
            print(f"  ID: {o.id}, 錯誤: {o.error}")


def example_stream_processing():
    """
    範例 4: 流式處理

    展示流式批量處理
    """
    print("\n" + "=" * 50)
    print("範例 4: 流式處理")
    print("=" * 50)

    def data_generator():
        """模擬數據流"""
        for i in range(15):
            yield BatchInput(id=str(i), data={"text": f"文本 {i}"})

    processor = BatchProcessor(max_workers=3)

    print("流式處理結果:")
    count = 0
    for output in processor.process_stream(
        data_generator(),
        mock_classification_flow,
        batch_size=5
    ):
        count += 1
        print(f"  {output.id}: {output.status} - {output.output_data}")

    print(f"\n共處理 {count} 項")


def example_result_export():
    """
    範例 5: 結果導出

    展示如何導出處理結果
    """
    print("\n" + "=" * 50)
    print("範例 5: 結果導出")
    print("=" * 50)

    data = [
        {"question": "問題1"},
        {"question": "問題2"},
        {"question": "問題3"},
    ]
    inputs = DataLoader.from_list(data)

    processor = BatchProcessor()
    result = processor.process_batch(inputs, mock_qa_flow)

    # 導出為不同格式（模擬）
    print("導出格式:")
    print("  - JSON: batch_result.json")
    print("  - JSONL: batch_result.jsonl")
    print("  - CSV: batch_result.csv")

    # 顯示 JSON 格式示例
    sample_output = {
        "id": result.outputs[0].id,
        "status": result.outputs[0].status,
        "input": result.outputs[0].input_data,
        "output": result.outputs[0].output_data
    }
    print(f"\nJSON 輸出示例:")
    print(json.dumps(sample_output, indent=2, ensure_ascii=False))


def example_cli_commands():
    """
    範例 6: CLI 命令

    展示 PromptFlow 批量運行的 CLI 命令
    """
    print("\n" + "=" * 50)
    print("範例 6: CLI 命令")
    print("=" * 50)

    cli_examples = """
# PromptFlow 批量運行 CLI 命令

# 基礎批量運行
pf run create --flow ./my_flow --data ./data.jsonl

# 指定列映射
pf run create --flow ./my_flow --data ./data.jsonl \\
    --column-mapping question='${data.question}'

# 使用連接
pf run create --flow ./my_flow --data ./data.jsonl \\
    --connection azure_openai

# 指定並行度
pf run create --flow ./my_flow --data ./data.jsonl \\
    --workers 10

# 查看運行狀態
pf run show --name <run_name>

# 獲取運行結果
pf run show-details --name <run_name>

# 導出結果
pf run export --name <run_name> --output ./results.json
"""

    print(cli_examples)


def example_batch_config():
    """
    範例 7: 批量運行配置

    展示批量運行的 YAML 配置
    """
    print("\n" + "=" * 50)
    print("範例 7: 批量運行配置")
    print("=" * 50)

    yaml_config = """
# batch_run.yaml - 批量運行配置

name: my_batch_run
flow: ./my_flow
data: ./data.jsonl

# 列映射
column_mapping:
  question: ${data.question}
  context: ${data.context}

# 連接配置
connections:
  llm: azure_openai

# 運行設置
run_settings:
  workers: 10
  timeout_seconds: 300
  retry_count: 3

# 輸出設置
output:
  format: jsonl
  path: ./results.jsonl

# 評估（可選）
evaluation:
  enabled: true
  metrics:
    - accuracy
    - latency
"""

    print("批量運行配置示例:")
    print(yaml_config)


# ============================================================
# 主程序
# ============================================================

if __name__ == "__main__":
    print("PromptFlow 批量處理範例")
    print()

    example_basic_batch()
    example_parallel_processing()
    example_error_handling()
    example_stream_processing()
    example_result_export()
    example_cli_commands()
    example_batch_config()

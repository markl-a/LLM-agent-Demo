"""
Atomic Agents 流式輸出
======================

本文件展示如何實現流式響應輸出。
流式輸出能提供更好的用戶體驗，特別是對於長時間運行的任務。

主要內容：
1. 基礎流式生成
2. 異步流式處理
3. 流式管道
4. 進度追蹤
5. 流式緩衝
6. 錯誤處理

作者：Atomic Agents 團隊
日期：2025-12-31
"""

from typing import Generator, AsyncIterator, Iterator, Optional, Callable, Any, Dict, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
import time
from dataclasses import dataclass


# ============================================================================
# 第一部分：流式輸出基礎
# ============================================================================

class StreamChunk(BaseModel):
    """流式數據塊"""
    content: str = Field(..., description="內容")
    chunk_index: int = Field(..., description="塊索引")
    is_final: bool = Field(default=False, description="是否為最後一塊")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)


class StreamStatus(str, Enum):
    """流狀態"""
    STARTED = "started"
    STREAMING = "streaming"
    COMPLETED = "completed"
    ERROR = "error"


class StreamMetrics(BaseModel):
    """流式指標"""
    total_chunks: int = Field(default=0)
    total_bytes: int = Field(default=0)
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: Optional[datetime] = Field(None)
    duration: Optional[float] = Field(None)

    def complete(self) -> None:
        """標記為完成"""
        self.end_time = datetime.now()
        self.duration = (self.end_time - self.start_time).total_seconds()


class StreamGenerator:
    """
    流式生成器

    基礎的流式輸出生成器。
    """

    def __init__(self, content: str, chunk_size: int = 10):
        """
        初始化生成器

        Args:
            content: 要流式輸出的內容
            chunk_size: 每塊的大小
        """
        self.content = content
        self.chunk_size = chunk_size
        self.metrics = StreamMetrics()

    def generate(self) -> Generator[StreamChunk, None, None]:
        """
        生成流式數據塊

        Yields:
            StreamChunk: 數據塊
        """
        words = self.content.split()
        total_chunks = (len(words) + self.chunk_size - 1) // self.chunk_size

        for i in range(0, len(words), self.chunk_size):
            chunk_words = words[i:i + self.chunk_size]
            chunk_content = " ".join(chunk_words)

            chunk_index = i // self.chunk_size
            is_final = chunk_index == total_chunks - 1

            chunk = StreamChunk(
                content=chunk_content,
                chunk_index=chunk_index,
                is_final=is_final
            )

            # 更新指標
            self.metrics.total_chunks += 1
            self.metrics.total_bytes += len(chunk_content.encode('utf-8'))

            # 模擬網絡延遲
            time.sleep(0.1)

            yield chunk

        # 完成指標
        self.metrics.complete()


# ============================================================================
# 第二部分：LLM 流式客戶端
# ============================================================================

class StreamingLLMClient:
    """
    流式 LLM 客戶端

    模擬 LLM 的流式響應。
    """

    def __init__(self, model: str = "gpt-4"):
        self.model = model

    def stream_complete(
        self,
        prompt: str,
        max_tokens: int = 100
    ) -> Generator[str, None, None]:
        """
        流式生成完成

        Args:
            prompt: 提示詞
            max_tokens: 最大 token 數

        Yields:
            生成的文本塊
        """
        # 模擬 LLM 逐字生成
        response = self._generate_response(prompt, max_tokens)

        for word in response.split():
            # 模擬生成延遲
            time.sleep(0.05)
            yield word + " "

    def _generate_response(self, prompt: str, max_tokens: int) -> str:
        """生成響應（模擬）"""
        # 實際使用時會調用 LLM API
        return f"基於提示「{prompt[:20]}...」生成的響應內容。這是一個模擬的流式輸出示例。"


# ============================================================================
# 第三部分：流式處理器
# ============================================================================

class StreamProcessor:
    """
    流式處理器

    處理流式數據。
    """

    def __init__(self):
        self.handlers: List[Callable[[str], str]] = []

    def add_handler(self, handler: Callable[[str], str]) -> 'StreamProcessor':
        """添加處理器"""
        self.handlers.append(handler)
        return self

    def process_stream(
        self,
        stream: Iterator[str]
    ) -> Generator[str, None, None]:
        """
        處理流

        Args:
            stream: 輸入流

        Yields:
            處理後的數據
        """
        for chunk in stream:
            processed = chunk

            # 應用所有處理器
            for handler in self.handlers:
                processed = handler(processed)

            yield processed


# ============================================================================
# 第四部分：流式緩衝
# ============================================================================

class StreamBuffer:
    """
    流式緩衝區

    緩衝流式數據以便批量處理。
    """

    def __init__(self, buffer_size: int = 5):
        """
        初始化緩衝區

        Args:
            buffer_size: 緩衝區大小
        """
        self.buffer_size = buffer_size
        self.buffer: List[str] = []

    def add(self, chunk: str) -> Optional[str]:
        """
        添加數據塊

        Args:
            chunk: 數據塊

        Returns:
            如果緩衝區已滿，返回合併的內容
        """
        self.buffer.append(chunk)

        if len(self.buffer) >= self.buffer_size:
            return self.flush()

        return None

    def flush(self) -> str:
        """刷新緩衝區"""
        content = "".join(self.buffer)
        self.buffer.clear()
        return content

    def stream_with_buffer(
        self,
        stream: Iterator[str]
    ) -> Generator[str, None, None]:
        """
        帶緩衝的流式處理

        Args:
            stream: 輸入流

        Yields:
            緩衝後的數據
        """
        for chunk in stream:
            buffered = self.add(chunk)
            if buffered:
                yield buffered

        # 刷新剩餘內容
        if self.buffer:
            yield self.flush()


# ============================================================================
# 第五部分：進度追蹤
# ============================================================================

class ProgressTracker:
    """
    進度追蹤器

    追蹤流式處理的進度。
    """

    def __init__(self, total_items: Optional[int] = None):
        """
        初始化追蹤器

        Args:
            total_items: 總項目數（如果已知）
        """
        self.total_items = total_items
        self.processed_items = 0
        self.start_time = datetime.now()
        self.current_item: Optional[str] = None

    def update(self, item: str) -> None:
        """更新進度"""
        self.processed_items += 1
        self.current_item = item

    def get_progress(self) -> Dict[str, Any]:
        """獲取進度信息"""
        elapsed = (datetime.now() - self.start_time).total_seconds()

        progress = {
            'processed': self.processed_items,
            'elapsed_time': elapsed,
            'current_item': self.current_item
        }

        if self.total_items:
            progress['total'] = self.total_items
            progress['percentage'] = (self.processed_items / self.total_items) * 100

            # 估算剩餘時間
            if self.processed_items > 0:
                avg_time_per_item = elapsed / self.processed_items
                remaining_items = self.total_items - self.processed_items
                progress['estimated_remaining'] = avg_time_per_item * remaining_items

        return progress

    def print_progress(self) -> None:
        """打印進度"""
        progress = self.get_progress()

        if self.total_items:
            percentage = progress['percentage']
            remaining = progress.get('estimated_remaining', 0)
            print(
                f"\r進度: {self.processed_items}/{self.total_items} "
                f"({percentage:.1f}%) - "
                f"預計剩餘: {remaining:.1f}秒",
                end=""
            )
        else:
            print(
                f"\r已處理: {self.processed_items} - "
                f"耗時: {progress['elapsed_time']:.1f}秒",
                end=""
            )


# ============================================================================
# 第六部分：流式管道
# ============================================================================

class StreamPipeline:
    """
    流式管道

    連接多個流式處理階段。
    """

    def __init__(self, name: str):
        self.name = name
        self.stages: List[Callable] = []

    def add_stage(self, stage: Callable) -> 'StreamPipeline':
        """添加處理階段"""
        self.stages.append(stage)
        return self

    def process(self, stream: Iterator[str]) -> Generator[str, None, None]:
        """
        處理流

        Args:
            stream: 輸入流

        Yields:
            處理後的數據
        """
        print(f"\n開始流式管道: {self.name}")
        current_stream = stream

        # 依次通過各個階段
        for i, stage in enumerate(self.stages):
            print(f"  → 階段 {i+1}: {stage.__name__}")
            current_stream = stage(current_stream)

        # 輸出最終結果
        for item in current_stream:
            yield item


# ============================================================================
# 第七部分：流式聚合
# ============================================================================

class StreamAggregator:
    """
    流式聚合器

    在流式處理時收集和聚合數據。
    """

    def __init__(self):
        self.accumulated: List[str] = []
        self.statistics = {
            'total_chunks': 0,
            'total_length': 0,
            'unique_words': set()
        }

    def aggregate(
        self,
        stream: Iterator[str]
    ) -> Generator[tuple[str, Dict], None, None]:
        """
        聚合流

        Args:
            stream: 輸入流

        Yields:
            (數據塊, 當前統計) 元組
        """
        for chunk in stream:
            # 累積內容
            self.accumulated.append(chunk)

            # 更新統計
            self.statistics['total_chunks'] += 1
            self.statistics['total_length'] += len(chunk)

            # 提取單詞
            words = chunk.split()
            self.statistics['unique_words'].update(words)

            # 生成當前狀態
            yield chunk, self.get_stats()

    def get_stats(self) -> Dict[str, Any]:
        """獲取統計信息"""
        return {
            'total_chunks': self.statistics['total_chunks'],
            'total_length': self.statistics['total_length'],
            'unique_words': len(self.statistics['unique_words']),
            'accumulated_length': sum(len(c) for c in self.accumulated)
        }

    def get_full_content(self) -> str:
        """獲取完整內容"""
        return "".join(self.accumulated)


# ============================================================================
# 第八部分：錯誤處理
# ============================================================================

class StreamErrorHandler:
    """
    流式錯誤處理器

    處理流式傳輸中的錯誤。
    """

    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.error_count = 0

    def handle_stream(
        self,
        stream_func: Callable,
        *args,
        **kwargs
    ) -> Generator[str, None, None]:
        """
        處理帶錯誤恢復的流

        Args:
            stream_func: 生成流的函數
            *args, **kwargs: 函數參數

        Yields:
            數據塊
        """
        retry_count = 0

        while retry_count <= self.max_retries:
            try:
                stream = stream_func(*args, **kwargs)

                for chunk in stream:
                    yield chunk

                # 成功完成
                break

            except Exception as e:
                retry_count += 1
                self.error_count += 1

                print(f"\n流式錯誤 (嘗試 {retry_count}/{self.max_retries}): {str(e)}")

                if retry_count > self.max_retries:
                    print("已達到最大重試次數")
                    raise

                # 等待後重試
                time.sleep(1 * retry_count)


# ============================================================================
# 第九部分：使用示例
# ============================================================================

def example_basic_streaming():
    """基礎流式輸出示例"""
    print("\n" + "="*60)
    print("示例 1: 基礎流式輸出")
    print("="*60)

    content = "這是一個流式輸出的示例 展示如何逐塊生成和傳輸數據 提供更好的用戶體驗"
    generator = StreamGenerator(content, chunk_size=3)

    print("\n開始流式輸出:")
    for chunk in generator.generate():
        print(f"[塊 {chunk.chunk_index}] {chunk.content}")
        if chunk.is_final:
            print("\n✓ 流式輸出完成")

    print(f"\n指標:")
    print(f"  總塊數: {generator.metrics.total_chunks}")
    print(f"  總字節: {generator.metrics.total_bytes}")
    print(f"  耗時: {generator.metrics.duration:.2f}秒")


def example_llm_streaming():
    """LLM 流式輸出示例"""
    print("\n" + "="*60)
    print("示例 2: LLM 流式生成")
    print("="*60)

    client = StreamingLLMClient()

    print("\n流式響應:")
    accumulated = ""

    for chunk in client.stream_complete("請介紹 Atomic Agents"):
        print(chunk, end="", flush=True)
        accumulated += chunk

    print(f"\n\n完整響應長度: {len(accumulated)} 字符")


def example_stream_processing():
    """流式處理示例"""
    print("\n" + "="*60)
    print("示例 3: 流式數據處理")
    print("="*60)

    # 創建處理器
    processor = StreamProcessor()

    # 添加處理函數
    processor.add_handler(lambda x: x.upper())  # 轉大寫
    processor.add_handler(lambda x: f"[{x.strip()}]")  # 添加括號

    # 創建流
    client = StreamingLLMClient()
    stream = client.stream_complete("測試", max_tokens=50)

    # 處理流
    print("\n處理後的輸出:")
    for processed in processor.process_stream(stream):
        print(processed, end="", flush=True)
    print()


def example_buffered_streaming():
    """緩衝流式輸出示例"""
    print("\n" + "="*60)
    print("示例 4: 緩衝流式輸出")
    print("="*60)

    buffer = StreamBuffer(buffer_size=5)
    client = StreamingLLMClient()
    stream = client.stream_complete("測試緩衝", max_tokens=50)

    print("\n緩衝輸出（每5個詞一組）:")
    for buffered in buffer.stream_with_buffer(stream):
        print(f"\n[緩衝塊] {buffered}")
        print("-" * 40)


def example_progress_tracking():
    """進度追蹤示例"""
    print("\n" + "="*60)
    print("示例 5: 進度追蹤")
    print("="*60)

    content = "進度 追蹤 示例 " * 10
    words = content.split()

    tracker = ProgressTracker(total_items=len(words))

    print("\n處理中:")
    for word in words:
        tracker.update(word)
        tracker.print_progress()
        time.sleep(0.1)

    print("\n\n✓ 處理完成")


def example_stream_pipeline():
    """流式管道示例"""
    print("\n" + "="*60)
    print("示例 6: 流式管道")
    print("="*60)

    # 定義處理階段
    def uppercase_stage(stream):
        for item in stream:
            yield item.upper()

    def add_prefix_stage(stream):
        for item in stream:
            yield f">>> {item}"

    def filter_stage(stream):
        for item in stream:
            if len(item) > 5:
                yield item

    # 創建管道
    pipeline = StreamPipeline("數據處理管道")
    pipeline.add_stage(uppercase_stage)
    pipeline.add_stage(add_prefix_stage)
    pipeline.add_stage(filter_stage)

    # 創建輸入流
    client = StreamingLLMClient()
    stream = client.stream_complete("測試管道", max_tokens=30)

    # 處理
    print("\n管道輸出:")
    for result in pipeline.process(stream):
        print(result)


def example_stream_aggregation():
    """流式聚合示例"""
    print("\n" + "="*60)
    print("示例 7: 流式聚合")
    print("="*60)

    aggregator = StreamAggregator()
    client = StreamingLLMClient()
    stream = client.stream_complete("聚合測試", max_tokens=50)

    print("\n流式聚合:")
    for chunk, stats in aggregator.aggregate(stream):
        print(f"\r塊數: {stats['total_chunks']}, "
              f"總長度: {stats['total_length']}, "
              f"唯一詞: {stats['unique_words']}", end="")

    print(f"\n\n完整內容:\n{aggregator.get_full_content()}")


def example_error_handling():
    """錯誤處理示例"""
    print("\n" + "="*60)
    print("示例 8: 流式錯誤處理")
    print("="*60)

    error_handler = StreamErrorHandler(max_retries=3)

    attempt = 0

    def unreliable_stream():
        nonlocal attempt
        attempt += 1

        if attempt < 3:
            # 模擬前兩次失敗
            yield "部分數據..."
            raise Exception(f"模擬錯誤 (嘗試 {attempt})")

        # 第三次成功
        yield "成功的數據流"
        yield "更多數據"

    print("\n處理不穩定的流:")
    try:
        for chunk in error_handler.handle_stream(unreliable_stream):
            print(f"收到: {chunk}")
    except Exception as e:
        print(f"最終失敗: {str(e)}")


def main():
    """主函數"""
    print("\n" + "="*60)
    print("Atomic Agents 流式輸出")
    print("="*60)

    # 運行示例
    example_basic_streaming()
    example_llm_streaming()
    example_stream_processing()
    example_buffered_streaming()
    example_progress_tracking()
    example_stream_pipeline()
    example_stream_aggregation()
    example_error_handling()

    print("\n" + "="*60)
    print("所有示例運行完成！")
    print("="*60)


if __name__ == "__main__":
    main()

"""
Google ADK - 流式輸出範例

這個範例展示流式響應處理：
- 基礎流式輸出
- 串流事件處理
- 中斷和恢復
- 流式數據處理
- 性能優化
"""

import os
import asyncio
from typing import Optional, AsyncIterator, Iterator
from datetime import datetime
import json
from google_adk import Agent
from google_adk.models import GeminiPro
from google_adk.streaming import StreamHandler, StreamEvent


class StreamingExample:
    """流式輸出範例類"""

    def __init__(self, api_key: Optional[str] = None):
        """初始化流式輸出範例"""
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("請設置 GOOGLE_API_KEY 環境變量")

    def example_1_basic_streaming(self):
        """範例 1: 基礎流式輸出"""
        print("\n" + "="*60)
        print("範例 1: 基礎流式輸出")
        print("="*60)

        # 創建支持流式輸出的 Agent
        agent = Agent(
            model=GeminiPro(),
            name="streaming-agent",
            streaming=True  # 啟用流式輸出
        )

        prompt = "請詳細解釋什麼是機器學習。"
        print(f"\n問題: {prompt}")
        print("\n流式回答: ", end="", flush=True)

        # 模擬流式輸出
        """
        for chunk in agent.stream(prompt):
            print(chunk.content, end="", flush=True)
        print()
        """

        # 演示流式輸出概念
        demo_text = "機器學習是人工智能的一個分支，它讓計算機能夠從數據中學習..."
        for char in demo_text:
            print(char, end="", flush=True)
            import time
            time.sleep(0.05)

        print("\n\n✓ 流式輸出演示完成")
        return agent

    def example_2_async_streaming(self):
        """範例 2: 異步流式輸出"""
        print("\n" + "="*60)
        print("範例 2: 異步流式輸出")
        print("="*60)

        async def stream_response(prompt: str) -> AsyncIterator[str]:
            """
            異步流式生成響應

            Args:
                prompt: 用戶提示

            Yields:
                響應片段
            """
            # 模擬異步流式生成
            response_parts = [
                "這是",
                "一個",
                "異步",
                "流式",
                "響應",
                "的",
                "示例"
            ]

            for part in response_parts:
                await asyncio.sleep(0.1)  # 模擬延遲
                yield part

        async def process_stream():
            """處理流式響應"""
            prompt = "測試異步流式輸出"
            print(f"\n問題: {prompt}")
            print("異步流式回答: ", end="", flush=True)

            async for chunk in stream_response(prompt):
                print(chunk, end=" ", flush=True)

            print("\n\n✓ 異步流式輸出完成")

        # 運行異步任務
        """
        asyncio.run(process_stream())
        """

        print("\n異步流式輸出配置完成")
        print("（實際運行需要異步環境）")

    def example_3_stream_events(self):
        """範例 3: 流式事件處理"""
        print("\n" + "="*60)
        print("範例 3: 流式事件處理")
        print("="*60)

        from google_adk.streaming import StreamEventType

        class CustomStreamHandler(StreamHandler):
            """自定義流式處理器"""

            def __init__(self):
                self.events = []

            def on_start(self, event: StreamEvent):
                """流開始事件"""
                print(f"[START] 開始生成響應")
                self.events.append(("start", event.timestamp))

            def on_chunk(self, event: StreamEvent):
                """接收到數據塊"""
                print(f"[CHUNK] {event.content}", end="", flush=True)
                self.events.append(("chunk", event.content))

            def on_complete(self, event: StreamEvent):
                """流完成事件"""
                print(f"\n[COMPLETE] 響應生成完成")
                self.events.append(("complete", event.timestamp))

            def on_error(self, event: StreamEvent):
                """錯誤事件"""
                print(f"\n[ERROR] {event.error}")
                self.events.append(("error", event.error))

        # 創建處理器
        handler = CustomStreamHandler()

        # 模擬事件序列
        print("\n模擬流式事件:")
        handler.on_start(StreamEvent(type="start", timestamp=datetime.now()))

        content_chunks = ["這是", "流式", "輸出", "的", "示例"]
        for chunk in content_chunks:
            import time
            time.sleep(0.1)
            handler.on_chunk(StreamEvent(type="chunk", content=chunk))

        handler.on_complete(StreamEvent(type="complete", timestamp=datetime.now()))

        print(f"\n總事件數: {len(handler.events)}")

        return handler

    def example_4_stream_interruption(self):
        """範例 4: 流式中斷和恢復"""
        print("\n" + "="*60)
        print("範例 4: 流式中斷和恢復")
        print("="*60)

        class InterruptibleStream:
            """可中斷的流"""

            def __init__(self):
                self.paused = False
                self.stopped = False
                self.checkpoint = None

            def stream(self, data: list):
                """
                流式處理數據

                Args:
                    data: 要流式處理的數據
                """
                for i, item in enumerate(data):
                    if self.stopped:
                        print("\n[STOPPED] 流已停止")
                        break

                    while self.paused:
                        print("\n[PAUSED] 流已暫停...")
                        import time
                        time.sleep(0.5)

                    print(item, end=" ", flush=True)
                    self.checkpoint = i

                print("\n[DONE] 流處理完成")

            def pause(self):
                """暫停流"""
                self.paused = True
                print("\n[PAUSE] 暫停流")

            def resume(self):
                """恢復流"""
                self.paused = False
                print("[RESUME] 恢復流")

            def stop(self):
                """停止流"""
                self.stopped = True

            def get_checkpoint(self):
                """獲取檢查點"""
                return self.checkpoint

        # 測試可中斷流
        stream = InterruptibleStream()
        data = list(range(1, 21))

        print("\n流式處理數據:")
        print("數據:", data)

        # 模擬中斷場景
        print("\n開始流式處理:")
        print("（演示概念，實際需要多線程）")

        """
        import threading

        # 在線程中運行流
        thread = threading.Thread(target=stream.stream, args=(data,))
        thread.start()

        # 模擬中斷
        time.sleep(2)
        stream.pause()

        time.sleep(1)
        stream.resume()

        thread.join()
        """

        print("✓ 中斷和恢復機制配置完成")

    def example_5_buffered_streaming(self):
        """範例 5: 緩衝流式輸出"""
        print("\n" + "="*60)
        print("範例 5: 緩衝流式輸出")
        print("="*60)

        from collections import deque

        class BufferedStream:
            """緩衝流"""

            def __init__(self, buffer_size: int = 10):
                self.buffer = deque(maxlen=buffer_size)
                self.buffer_size = buffer_size

            def add(self, item: str):
                """添加到緩衝區"""
                self.buffer.append(item)

                # 緩衝區滿時輸出
                if len(self.buffer) >= self.buffer_size:
                    self.flush()

            def flush(self):
                """刷新緩衝區"""
                if self.buffer:
                    output = " ".join(self.buffer)
                    print(output, end=" ", flush=True)
                    self.buffer.clear()

            def close(self):
                """關閉流，輸出剩餘內容"""
                self.flush()
                print()  # 換行

        # 測試緩衝流
        stream = BufferedStream(buffer_size=5)

        print("\n緩衝流式輸出 (緩衝大小: 5):")
        words = "這是一個測試緩衝流式輸出的長句子包含很多單詞用來演示緩衝機制".split()

        for word in words:
            stream.add(word)
            import time
            time.sleep(0.1)

        stream.close()

        print("\n✓ 緩衝流式輸出完成")

    def example_6_token_streaming(self):
        """範例 6: Token 級別流式輸出"""
        print("\n" + "="*60)
        print("範例 6: Token 級別流式輸出")
        print("="*60)

        class TokenStream:
            """Token 流"""

            def __init__(self):
                self.token_count = 0
                self.total_tokens = 0

            def stream_tokens(self, text: str):
                """
                流式輸出 token

                Args:
                    text: 要流式輸出的文本
                """
                # 簡單的 token 化（按字符）
                tokens = list(text)
                self.total_tokens = len(tokens)

                print(f"總 tokens: {self.total_tokens}\n")
                print("Token 流: ", end="", flush=True)

                for token in tokens:
                    print(token, end="", flush=True)
                    self.token_count += 1

                    # 每 10 個 token 顯示進度
                    if self.token_count % 10 == 0:
                        progress = (self.token_count / self.total_tokens) * 100
                        print(f" [{progress:.0f}%]", end="", flush=True)

                    import time
                    time.sleep(0.02)

                print(f"\n\n✓ 完成: {self.token_count}/{self.total_tokens} tokens")

        # 測試 token 流
        token_stream = TokenStream()
        text = "這是一個測試 Token 級別流式輸出的示例文本。"

        print("\nToken 流式輸出:")
        token_stream.stream_tokens(text)

    def example_7_multi_stream(self):
        """範例 7: 多流並行處理"""
        print("\n" + "="*60)
        print("範例 7: 多流並行處理")
        print("="*60)

        async def stream_a():
            """流 A"""
            for i in range(5):
                await asyncio.sleep(0.2)
                yield f"A{i}"

        async def stream_b():
            """流 B"""
            for i in range(5):
                await asyncio.sleep(0.15)
                yield f"B{i}"

        async def stream_c():
            """流 C"""
            for i in range(5):
                await asyncio.sleep(0.25)
                yield f"C{i}"

        async def merge_streams():
            """合併多個流"""
            print("\n並行處理多個流:")

            # 創建任務
            tasks = [
                stream_a(),
                stream_b(),
                stream_c()
            ]

            # 模擬並行處理
            print("流 A, B, C 並行輸出:")
            print("（實際需要 async 環境）")

            """
            async for item in merge_async_iters(*tasks):
                print(item, end=" ", flush=True)
            """

        print("\n多流並行處理配置完成")

    def example_8_stream_transformation(self):
        """範例 8: 流式數據轉換"""
        print("\n" + "="*60)
        print("範例 8: 流式數據轉換")
        print("="*60)

        class StreamTransformer:
            """流式轉換器"""

            @staticmethod
            def uppercase_stream(stream: Iterator[str]) -> Iterator[str]:
                """轉換為大寫"""
                for item in stream:
                    yield item.upper()

            @staticmethod
            def filter_stream(stream: Iterator[str], condition) -> Iterator[str]:
                """過濾流"""
                for item in stream:
                    if condition(item):
                        yield item

            @staticmethod
            def map_stream(stream: Iterator[str], func) -> Iterator[str]:
                """映射流"""
                for item in stream:
                    yield func(item)

        # 創建源流
        def source_stream():
            """源數據流"""
            words = ["hello", "world", "python", "streaming", "data"]
            for word in words:
                yield word

        # 應用轉換
        print("\n流式轉換演示:")

        print("\n1. 原始流:")
        for item in source_stream():
            print(item, end=" ")

        print("\n\n2. 大寫轉換:")
        transformer = StreamTransformer()
        for item in transformer.uppercase_stream(source_stream()):
            print(item, end=" ")

        print("\n\n3. 過濾 (長度 > 5):")
        for item in transformer.filter_stream(
            source_stream(),
            lambda x: len(x) > 5
        ):
            print(item, end=" ")

        print("\n\n4. 映射 (添加前綴):")
        for item in transformer.map_stream(
            source_stream(),
            lambda x: f"[{x}]"
        ):
            print(item, end=" ")

        print("\n\n✓ 流式轉換演示完成")

    def example_9_stream_monitoring(self):
        """範例 9: 流式監控"""
        print("\n" + "="*60)
        print("範例 9: 流式監控")
        print("="*60)

        class StreamMonitor:
            """流式監控器"""

            def __init__(self):
                self.stats = {
                    "chunks_received": 0,
                    "bytes_received": 0,
                    "start_time": None,
                    "end_time": None,
                    "errors": 0
                }

            def start(self):
                """開始監控"""
                self.stats["start_time"] = datetime.now()
                print(f"[MONITOR] 開始監控: {self.stats['start_time']}")

            def record_chunk(self, chunk: str):
                """記錄數據塊"""
                self.stats["chunks_received"] += 1
                self.stats["bytes_received"] += len(chunk.encode('utf-8'))

            def record_error(self):
                """記錄錯誤"""
                self.stats["errors"] += 1

            def stop(self):
                """停止監控"""
                self.stats["end_time"] = datetime.now()

            def get_report(self) -> dict:
                """生成報告"""
                if self.stats["start_time"] and self.stats["end_time"]:
                    duration = (
                        self.stats["end_time"] - self.stats["start_time"]
                    ).total_seconds()
                else:
                    duration = 0

                return {
                    "總數據塊": self.stats["chunks_received"],
                    "總字節數": self.stats["bytes_received"],
                    "持續時間": f"{duration:.2f}秒",
                    "錯誤數": self.stats["errors"],
                    "平均速率": f"{self.stats['chunks_received']/duration:.2f} 塊/秒" if duration > 0 else "N/A"
                }

        # 測試監控
        monitor = StreamMonitor()
        monitor.start()

        print("\n模擬流式處理:")
        chunks = ["chunk1", "chunk2", "chunk3", "chunk4", "chunk5"]

        for chunk in chunks:
            print(f"  處理: {chunk}")
            monitor.record_chunk(chunk)
            import time
            time.sleep(0.1)

        monitor.stop()

        print("\n監控報告:")
        report = monitor.get_report()
        for key, value in report.items():
            print(f"  {key}: {value}")

    def example_10_production_streaming(self):
        """範例 10: 生產級流式配置"""
        print("\n" + "="*60)
        print("範例 10: 生產級流式配置")
        print("="*60)

        from google_adk.streaming import ProductionStreamConfig

        # 生產級配置
        config = ProductionStreamConfig(
            # 性能配置
            buffer_size=1024,
            chunk_size=256,
            max_concurrent_streams=10,

            # 可靠性配置
            enable_retry=True,
            max_retries=3,
            timeout=30,

            # 監控配置
            enable_monitoring=True,
            log_chunks=False,
            metrics_interval=10,

            # 優化配置
            enable_compression=True,
            compression_level=6,
            enable_caching=True,
            cache_ttl=300
        )

        print("生產級流式配置:")
        print(f"  緩衝大小: {config.buffer_size}")
        print(f"  數據塊大小: {config.chunk_size}")
        print(f"  最大並發流: {config.max_concurrent_streams}")
        print(f"  啟用重試: {config.enable_retry}")
        print(f"  超時: {config.timeout}秒")
        print(f"  啟用監控: {config.enable_monitoring}")
        print(f"  啟用壓縮: {config.enable_compression}")
        print(f"  啟用緩存: {config.enable_caching}")

        # 創建生產級 Agent
        agent = Agent(
            model=GeminiPro(),
            streaming=True,
            stream_config=config,
            name="production-streaming-agent"
        )

        print("\n✓ 生產級流式 Agent 配置完成")

        # 最佳實踐
        best_practices = [
            "1. 始終處理流式錯誤和超時",
            "2. 使用適當的緩衝大小優化性能",
            "3. 實現流式進度反饋給用戶",
            "4. 監控流式性能指標",
            "5. 支持暫停/恢復/取消操作",
            "6. 處理網絡中斷和重連",
            "7. 使用背壓機制避免內存溢出",
            "8. 記錄流式事件用於調試"
        ]

        print("\n流式輸出最佳實踐:")
        for practice in best_practices:
            print(f"  {practice}")

        return agent


def main():
    """主函數"""
    print("="*60)
    print("Google ADK - 流式輸出範例")
    print("="*60)

    # 檢查 API 密鑰
    if not os.getenv("GOOGLE_API_KEY"):
        print("\n⚠️  請先設置 GOOGLE_API_KEY 環境變量")
        print("export GOOGLE_API_KEY='your-api-key-here'")
        return

    # 創建範例實例
    example = StreamingExample()

    try:
        # 運行所有範例
        example.example_1_basic_streaming()
        example.example_2_async_streaming()
        example.example_3_stream_events()
        example.example_4_stream_interruption()
        example.example_5_buffered_streaming()
        example.example_6_token_streaming()
        example.example_7_multi_stream()
        example.example_8_stream_transformation()
        example.example_9_stream_monitoring()
        example.example_10_production_streaming()

        print("\n" + "="*60)
        print("所有流式輸出範例執行完成！")
        print("="*60)

    except Exception as e:
        print(f"\n❌ 執行錯誤: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

"""
LiteLLM 流式輸出範例

這個檔案展示如何使用 LiteLLM 實現流式輸出（Streaming）：
1. 基本流式輸出
2. 流式回應處理
3. 進度追蹤
4. 錯誤處理
5. 取消流式請求
6. 非同步流式輸出
7. 流式輸出快取
8. 多模型流式比較
9. 串流資料解析
10. WebSocket 整合

流式輸出可以提供更好的使用者體驗，讓使用者即時看到回應。
"""

import os
from typing import Dict, List, Any, Optional, Generator
import time
import asyncio
from datetime import datetime
from litellm import completion, acompletion
import sys
from dataclasses import dataclass


# ============================================================================
# 資料類別定義
# ============================================================================

@dataclass
class StreamMetrics:
    """流式輸出指標"""
    total_chunks: int
    total_tokens: int
    start_time: float
    end_time: Optional[float]
    first_chunk_time: Optional[float]
    average_chunk_time: float


# ============================================================================
# 第一部分：基本流式輸出
# ============================================================================

def basic_streaming_example():
    """
    基本流式輸出範例

    展示最簡單的流式輸出使用方法。
    """
    print("=" * 80)
    print("基本流式輸出範例")
    print("=" * 80)

    prompt = "寫一首關於人工智慧的短詩"

    print(f"\n提示：{prompt}")
    print("\n回應（流式）：")
    print("-" * 40)

    try:
        # 啟用流式輸出
        response = completion(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            stream=True  # 啟用流式輸出
        )

        # 處理流式回應
        full_response = ""
        for chunk in response:
            # 取得當前 chunk 的內容
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                full_response += content

        print("\n" + "-" * 40)
        print(f"完整回應長度：{len(full_response)} 字元")

    except Exception as e:
        print(f"\n錯誤：{e}")


def streaming_with_metrics():
    """
    帶指標的流式輸出

    追蹤流式輸出的各種指標。
    """
    print("\n" + "=" * 80)
    print("流式輸出指標追蹤")
    print("=" * 80)

    prompt = "詳細解釋什麼是深度學習，包括其歷史、原理和應用"

    print(f"\n提示：{prompt}")
    print("\n回應（流式）：")
    print("-" * 40)

    try:
        response = completion(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            max_tokens=500
        )

        # 初始化指標
        start_time = time.time()
        first_chunk_time = None
        chunk_count = 0
        chunk_times = []
        full_response = ""

        # 處理流式回應
        for chunk in response:
            chunk_time = time.time()

            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                full_response += content

                chunk_count += 1

                # 記錄第一個 chunk 的時間
                if first_chunk_time is None:
                    first_chunk_time = chunk_time
                    chunk_times.append(chunk_time - start_time)
                else:
                    chunk_times.append(chunk_time - chunk_times[-1] if chunk_times else 0)

        end_time = time.time()

        # 計算指標
        total_time = end_time - start_time
        time_to_first_chunk = first_chunk_time - start_time if first_chunk_time else 0
        avg_chunk_time = sum(chunk_times) / len(chunk_times) if chunk_times else 0

        print("\n" + "-" * 40)
        print("\n指標：")
        print(f"  總耗時：{total_time:.2f} 秒")
        print(f"  第一個 chunk 延遲：{time_to_first_chunk:.2f} 秒")
        print(f"  Chunk 數量：{chunk_count}")
        print(f"  平均 chunk 間隔：{avg_chunk_time:.3f} 秒")
        print(f"  總字元數：{len(full_response)}")
        print(f"  輸出速度：{len(full_response) / total_time:.1f} 字元/秒")

    except Exception as e:
        print(f"\n錯誤：{e}")


# ============================================================================
# 第二部分：流式輸出處理器
# ============================================================================

class StreamingHandler:
    """流式輸出處理器"""

    def __init__(self):
        self.buffer = ""
        self.metrics = {
            "chunks": 0,
            "tokens": 0,
            "start_time": None,
            "first_chunk_time": None
        }

    def on_start(self):
        """流開始時呼叫"""
        self.metrics["start_time"] = time.time()
        print("\n[流式輸出開始]")

    def on_chunk(self, content: str):
        """接收到新 chunk 時呼叫"""
        if self.metrics["chunks"] == 0:
            self.metrics["first_chunk_time"] = time.time()

        self.buffer += content
        self.metrics["chunks"] += 1

        # 輸出到控制台
        print(content, end="", flush=True)

    def on_complete(self):
        """流完成時呼叫"""
        end_time = time.time()

        print("\n\n[流式輸出完成]")
        print(f"總 chunks：{self.metrics['chunks']}")
        print(f"總字元數：{len(self.buffer)}")

        if self.metrics["start_time"] and self.metrics["first_chunk_time"]:
            ttfb = self.metrics["first_chunk_time"] - self.metrics["start_time"]
            total_time = end_time - self.metrics["start_time"]
            print(f"首字節延遲（TTFB）：{ttfb:.2f} 秒")
            print(f"總耗時：{total_time:.2f} 秒")

    def on_error(self, error: Exception):
        """發生錯誤時呼叫"""
        print(f"\n\n[錯誤]：{error}")

    def get_full_response(self) -> str:
        """取得完整回應"""
        return self.buffer


def streaming_handler_example():
    """流式處理器範例"""
    print("\n" + "=" * 80)
    print("流式處理器範例")
    print("=" * 80)

    handler = StreamingHandler()

    prompt = "寫一個關於機器學習的故事，包含開頭、發展和結局"

    print(f"\n提示：{prompt}")

    try:
        handler.on_start()

        response = completion(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            max_tokens=500
        )

        for chunk in response:
            if chunk.choices[0].delta.content:
                handler.on_chunk(chunk.choices[0].delta.content)

        handler.on_complete()

    except Exception as e:
        handler.on_error(e)


# ============================================================================
# 第三部分：非同步流式輸出
# ============================================================================

async def async_streaming_example():
    """
    非同步流式輸出範例

    使用 async/await 進行流式輸出。
    """
    print("\n" + "=" * 80)
    print("非同步流式輸出範例")
    print("=" * 80)

    prompt = "解釋量子計算的基本原理"

    print(f"\n提示：{prompt}")
    print("\n回應（非同步流式）：")
    print("-" * 40)

    try:
        response = await acompletion(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            max_tokens=300
        )

        full_response = ""
        async for chunk in response:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                full_response += content

        print("\n" + "-" * 40)
        print(f"完成！總計 {len(full_response)} 字元")

    except Exception as e:
        print(f"\n錯誤：{e}")


async def parallel_streaming():
    """
    並行流式輸出

    同時執行多個流式請求。
    """
    print("\n" + "=" * 80)
    print("並行流式輸出範例")
    print("=" * 80)

    prompts = [
        "什麼是 Python？",
        "什麼是 JavaScript？",
        "什麼是 Go？"
    ]

    async def stream_single(prompt: str, index: int):
        """單個流式請求"""
        print(f"\n[流 {index + 1}] 提示：{prompt}")
        print(f"[流 {index + 1}] 回應：", end="")

        try:
            response = await acompletion(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                stream=True,
                max_tokens=100
            )

            full_response = ""
            async for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content

            print(f"\n[流 {index + 1}] 完成（{len(full_response)} 字元）")

        except Exception as e:
            print(f"\n[流 {index + 1}] 錯誤：{e}")

    # 並行執行所有流
    tasks = [stream_single(prompt, i) for i, prompt in enumerate(prompts)]
    await asyncio.gather(*tasks)


def run_async_streaming():
    """執行非同步流式範例"""
    asyncio.run(async_streaming_example())


def run_parallel_streaming():
    """執行並行流式範例"""
    asyncio.run(parallel_streaming())


# ============================================================================
# 第四部分：流式輸出比較
# ============================================================================

class StreamingComparator:
    """流式輸出比較器"""

    def __init__(self):
        self.results = {}

    def compare_models(self, prompt: str, models: List[str]):
        """
        比較不同模型的流式輸出

        Args:
            prompt: 提示詞
            models: 要比較的模型列表
        """
        print(f"\n提示：{prompt}\n")

        for model in models:
            print(f"\n{model}")
            print("=" * 80)

            try:
                start_time = time.time()
                first_chunk_time = None
                chunks = []

                response = completion(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    stream=True,
                    max_tokens=200
                )

                full_response = ""
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        print(content, end="", flush=True)
                        full_response += content

                        if first_chunk_time is None:
                            first_chunk_time = time.time()

                        chunks.append({
                            "time": time.time(),
                            "content": content
                        })

                end_time = time.time()

                # 記錄結果
                self.results[model] = {
                    "total_time": end_time - start_time,
                    "ttfb": first_chunk_time - start_time if first_chunk_time else 0,
                    "chunks": len(chunks),
                    "length": len(full_response),
                    "response": full_response
                }

                print(f"\n\n統計：")
                print(f"  總耗時：{self.results[model]['total_time']:.2f}s")
                print(f"  TTFB：{self.results[model]['ttfb']:.2f}s")
                print(f"  Chunks：{self.results[model]['chunks']}")

            except Exception as e:
                print(f"\n錯誤：{e}")

    def print_comparison(self):
        """列印比較結果"""
        print("\n" + "=" * 80)
        print("比較結果")
        print("=" * 80)

        if not self.results:
            print("沒有可比較的結果")
            return

        print(f"\n{'模型':<30} {'總耗時(s)':<12} {'TTFB(s)':<12} {'Chunks':<10} {'長度':<10}")
        print("-" * 80)

        for model, data in self.results.items():
            print(f"{model:<30} {data['total_time']:<12.2f} {data['ttfb']:<12.2f} {data['chunks']:<10} {data['length']:<10}")

        # 找出最快的模型
        fastest_total = min(self.results.items(), key=lambda x: x[1]['total_time'])
        fastest_ttfb = min(self.results.items(), key=lambda x: x[1]['ttfb'])

        print(f"\n最快完成：{fastest_total[0]} ({fastest_total[1]['total_time']:.2f}s)")
        print(f"最快首字節：{fastest_ttfb[0]} ({fastest_ttfb[1]['ttfb']:.2f}s)")


def streaming_comparison_example():
    """流式輸出比較範例"""
    print("\n" + "=" * 80)
    print("流式輸出比較範例")
    print("=" * 80)

    comparator = StreamingComparator()

    prompt = "用 50 字以內解釋什麼是雲端運算"
    models = [
        "gpt-3.5-turbo",
        "gpt-4o",
        # "claude-3-haiku-20240307",
    ]

    comparator.compare_models(prompt, models)
    comparator.print_comparison()


# ============================================================================
# 第五部分：流式輸出的進階應用
# ============================================================================

class StreamingChatbot:
    """流式聊天機器人"""

    def __init__(self, model: str = "gpt-3.5-turbo"):
        self.model = model
        self.messages = []

    def add_system_message(self, content: str):
        """新增系統訊息"""
        self.messages.append({
            "role": "system",
            "content": content
        })

    def chat(self, user_input: str) -> str:
        """
        進行對話（流式輸出）

        Args:
            user_input: 使用者輸入

        Returns:
            助手的完整回應
        """
        # 新增使用者訊息
        self.messages.append({
            "role": "user",
            "content": user_input
        })

        print(f"\n使用者：{user_input}")
        print(f"助手：", end="")

        try:
            response = completion(
                model=self.model,
                messages=self.messages,
                stream=True,
                max_tokens=500
            )

            full_response = ""
            for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    full_response += content

            print()  # 換行

            # 新增助手回應到歷史
            self.messages.append({
                "role": "assistant",
                "content": full_response
            })

            return full_response

        except Exception as e:
            print(f"\n錯誤：{e}")
            return ""

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """取得對話歷史"""
        return self.messages.copy()


def streaming_chatbot_example():
    """流式聊天機器人範例"""
    print("\n" + "=" * 80)
    print("流式聊天機器人範例")
    print("=" * 80)

    # 建立聊天機器人
    bot = StreamingChatbot()
    bot.add_system_message("你是一個友善的 AI 助手，專門回答關於程式設計的問題。")

    # 模擬對話
    conversations = [
        "什麼是 Python？",
        "它有哪些主要特點？",
        "給我一個簡單的範例"
    ]

    for user_input in conversations:
        bot.chat(user_input)
        time.sleep(0.5)  # 模擬使用者思考時間

    print("\n" + "=" * 80)
    print(f"對話歷史（共 {len(bot.get_conversation_history())} 條訊息）")
    print("=" * 80)


# ============================================================================
# 第六部分：流式輸出與進度顯示
# ============================================================================

def streaming_with_progress():
    """
    帶進度顯示的流式輸出

    在終端顯示一個簡單的進度指示器。
    """
    print("\n" + "=" * 80)
    print("流式輸出 + 進度顯示")
    print("=" * 80)

    prompt = "寫一篇關於人工智慧未來發展的短文，約 300 字"

    print(f"\n提示：{prompt}")
    print("\n生成中", end="")

    try:
        response = completion(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            max_tokens=500
        )

        full_response = ""
        spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        spinner_idx = 0

        for i, chunk in enumerate(response):
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content

                # 更新進度指示器
                if i % 3 == 0:
                    print(f"\r生成中 {spinner[spinner_idx % len(spinner)]} {len(full_response)} 字元",
                          end="", flush=True)
                    spinner_idx += 1

        print(f"\r✓ 生成完成！總計 {len(full_response)} 字元")
        print("\n" + "-" * 40)
        print(full_response)
        print("-" * 40)

    except Exception as e:
        print(f"\n錯誤：{e}")


# ============================================================================
# 第七部分：錯誤處理和重試
# ============================================================================

def streaming_with_retry(max_retries: int = 3):
    """
    帶重試機制的流式輸出

    Args:
        max_retries: 最大重試次數
    """
    print("\n" + "=" * 80)
    print("流式輸出 + 重試機制")
    print("=" * 80)

    prompt = "解釋什麼是神經網路"

    for attempt in range(max_retries):
        try:
            print(f"\n嘗試 {attempt + 1}/{max_retries}...")

            response = completion(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                stream=True,
                max_tokens=200,
                timeout=30
            )

            full_response = ""
            for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    full_response += content

            print("\n\n✓ 成功完成")
            return full_response

        except Exception as e:
            print(f"\n✗ 錯誤：{e}")

            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 指數退避
                print(f"等待 {wait_time} 秒後重試...")
                time.sleep(wait_time)
            else:
                print("已達最大重試次數，放棄")
                return None


# ============================================================================
# 主程式
# ============================================================================

def main():
    """主程式"""
    print("\n")
    print("=" * 80)
    print("LiteLLM 流式輸出完整教學")
    print("=" * 80)
    print()

    # 基本流式輸出
    # basic_streaming_example()
    # streaming_with_metrics()

    # 流式處理器
    # streaming_handler_example()

    # 非同步流式輸出
    # run_async_streaming()
    # run_parallel_streaming()

    # 流式比較
    # streaming_comparison_example()

    # 聊天機器人
    # streaming_chatbot_example()

    # 進度顯示
    streaming_with_progress()

    # 重試機制
    # streaming_with_retry()

    print("\n" + "=" * 80)
    print("教學完成！")
    print("=" * 80)
    print("\n重點回顧：")
    print("1. 流式輸出提供更好的使用者體驗")
    print("2. 使用 stream=True 參數啟用流式輸出")
    print("3. 追蹤 TTFB 和其他指標優化效能")
    print("4. 非同步流式輸出支援並行處理")
    print("5. 適當的錯誤處理和重試機制很重要")
    print()


if __name__ == "__main__":
    main()

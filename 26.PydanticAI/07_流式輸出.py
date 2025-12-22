"""
Pydantic AI - 流式輸出範例

本範例展示：
1. 流式響應處理
2. 實時輸出展示
3. 流式工具調用
4. 流式結構化輸出
5. 錯誤處理

流式輸出提供更好的用戶體驗
"""

import asyncio
import sys
from typing import AsyncIterator
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext


# ============================================================================
# 範例 1: 基本流式輸出
# ============================================================================

async def example_1_basic_streaming():
    """最基本的流式輸出"""
    print("\n" + "="*60)
    print("範例 1: 基本流式輸出")
    print("="*60)

    agent = Agent('openai:gpt-4')

    print("用戶：講一個關於 AI 的故事\n")
    print("AI 回應：", end='', flush=True)

    # 使用 run_stream 獲取流式響應
    async with agent.run_stream('講一個關於 AI 的簡短故事') as response:
        # 逐個輸出文本塊
        async for chunk in response.stream_text():
            print(chunk, end='', flush=True)
            await asyncio.sleep(0.01)  # 模擬打字效果

    print("\n")


# ============================================================================
# 範例 2: 流式輸出與完整結果
# ============================================================================

async def example_2_streaming_with_result():
    """流式輸出並獲取完整結果"""
    print("\n" + "="*60)
    print("範例 2: 流式輸出與完整結果")
    print("="*60)

    agent = Agent('openai:gpt-4')

    print("AI 回應：", end='', flush=True)

    full_text = ""

    async with agent.run_stream('用三句話解釋機器學習') as response:
        # 收集所有文本塊
        async for chunk in response.stream_text():
            print(chunk, end='', flush=True)
            full_text += chunk

    print("\n")

    # 也可以獲取完整結果
    result = await response.get_data()

    print(f"完整回應長度：{len(result)} 字符")
    print(f"收集到的長度：{len(full_text)} 字符")


# ============================================================================
# 範例 3: 帶進度指示的流式輸出
# ============================================================================

async def example_3_streaming_with_progress():
    """顯示進度的流式輸出"""
    print("\n" + "="*60)
    print("範例 3: 帶進度指示的流式輸出")
    print("="*60)

    agent = Agent('openai:gpt-4')

    print("正在生成內容", end='', flush=True)

    char_count = 0
    async with agent.run_stream('寫一段關於 Python 的介紹') as response:
        async for chunk in response.stream_text():
            char_count += len(chunk)

            # 每收到 20 個字符顯示一個點
            if char_count % 20 == 0:
                print('.', end='', flush=True)

    print(f"\n\n✓ 完成！共生成 {char_count} 字符")

    # 獲取完整內容
    result = await response.get_data()
    print(f"\n內容：\n{result[:200]}...")


# ============================================================================
# 範例 4: 流式工具調用
# ============================================================================

async def example_4_streaming_with_tools():
    """流式輸出時調用工具"""
    print("\n" + "="*60)
    print("範例 4: 流式工具調用")
    print("="*60)

    agent = Agent('openai:gpt-4')

    @agent.tool
    async def get_weather(city: str) -> dict:
        """獲取天氣（模擬）"""
        print(f"\n[調用工具: get_weather({city})]", end='', flush=True)
        await asyncio.sleep(0.5)  # 模擬 API 延遲

        return {
            "city": city,
            "temperature": 28,
            "condition": "晴天"
        }

    @agent.tool
    async def get_air_quality(city: str) -> dict:
        """獲取空氣質量（模擬）"""
        print(f"\n[調用工具: get_air_quality({city})]", end='', flush=True)
        await asyncio.sleep(0.3)

        return {
            "city": city,
            "aqi": 45,
            "level": "良好"
        }

    print("\nAI 回應：", end='', flush=True)

    async with agent.run_stream('台北現在的天氣和空氣質量如何？') as response:
        async for chunk in response.stream_text():
            print(chunk, end='', flush=True)
            await asyncio.sleep(0.02)

    print("\n")


# ============================================================================
# 範例 5: 流式結構化輸出
# ============================================================================

class StoryOutline(BaseModel):
    """故事大綱"""
    title: str = Field(description="標題")
    characters: list[str] = Field(description="角色列表")
    plot_points: list[str] = Field(description="情節要點")
    conclusion: str = Field(description="結局")


async def example_5_streaming_structured():
    """流式結構化輸出"""
    print("\n" + "="*60)
    print("範例 5: 流式結構化輸出")
    print("="*60)

    agent: Agent[None, StoryOutline] = Agent(
        'openai:gpt-4',
        result_type=StoryOutline,
    )

    print("正在生成故事大綱...\n")

    async with agent.run_stream('創建一個科幻故事的大綱') as response:
        # 流式輸出（如果模型支持）
        async for text in response.stream_text(delta=True):
            if text:
                print(text, end='', flush=True)

    print("\n\n獲取結構化數據...")

    # 獲取結構化結果
    outline: StoryOutline = await response.get_data()

    print(f"\n標題：{outline.title}")
    print(f"\n角色：")
    for char in outline.characters:
        print(f"  - {char}")

    print(f"\n情節要點：")
    for i, point in enumerate(outline.plot_points, 1):
        print(f"  {i}. {point}")

    print(f"\n結局：{outline.conclusion}")


# ============================================================================
# 範例 6: 實時處理流式數據
# ============================================================================

class TokenCounter:
    """Token 計數器"""

    def __init__(self):
        self.token_count = 0
        self.char_count = 0

    def add_chunk(self, chunk: str):
        """添加文本塊"""
        # 簡單估算：平均 4 字符 = 1 token
        self.char_count += len(chunk)
        self.token_count = self.char_count // 4

    def get_stats(self) -> dict:
        """獲取統計"""
        return {
            "characters": self.char_count,
            "estimated_tokens": self.token_count
        }


async def example_6_real_time_processing():
    """實時處理流式數據"""
    print("\n" + "="*60)
    print("範例 6: 實時處理流式數據")
    print("="*60)

    agent = Agent('openai:gpt-4')
    counter = TokenCounter()

    print("AI 回應：\n")

    async with agent.run_stream('解釋量子計算的基本原理') as response:
        async for chunk in response.stream_text():
            # 實時處理每個塊
            counter.add_chunk(chunk)

            print(chunk, end='', flush=True)

            # 每 50 個字符顯示統計
            if counter.char_count % 50 < len(chunk):
                stats = counter.get_stats()
                print(f"\n[統計: {stats['characters']} 字符, ~{stats['estimated_tokens']} tokens]",
                      end='', flush=True)

    print("\n")

    # 最終統計
    final_stats = counter.get_stats()
    print(f"\n最終統計：")
    print(f"  字符數：{final_stats['characters']}")
    print(f"  估計 tokens：{final_stats['estimated_tokens']}")


# ============================================================================
# 範例 7: 流式輸出錯誤處理
# ============================================================================

async def example_7_streaming_error_handling():
    """處理流式輸出中的錯誤"""
    print("\n" + "="*60)
    print("範例 7: 流式錯誤處理")
    print("="*60)

    agent = Agent('openai:gpt-4')

    try:
        print("AI 回應：", end='', flush=True)

        async with agent.run_stream('給我一些建議') as response:
            chunk_count = 0

            async for chunk in response.stream_text():
                print(chunk, end='', flush=True)
                chunk_count += 1

                # 模擬某種條件下的錯誤
                # if chunk_count > 100:
                #     raise Exception("處理錯誤")

        print("\n\n✓ 流式輸出完成")

    except Exception as e:
        print(f"\n\n✗ 錯誤：{e}")


# ============================================================================
# 範例 8: 並行流式輸出
# ============================================================================

async def stream_response(
    agent: Agent,
    prompt: str,
    label: str
) -> str:
    """流式輸出單個響應"""
    print(f"\n{label}：", end='', flush=True)

    full_text = ""

    async with agent.run_stream(prompt) as response:
        async for chunk in response.stream_text():
            print(chunk, end='', flush=True)
            full_text += chunk
            await asyncio.sleep(0.01)

    print()  # 換行
    return full_text


async def example_8_parallel_streaming():
    """並行處理多個流式輸出"""
    print("\n" + "="*60)
    print("範例 8: 並行流式輸出")
    print("="*60)

    agent = Agent('openai:gpt-4')

    # 注意：真正的並行流式顯示在終端會混亂
    # 這裡我們順序執行但展示概念

    tasks = [
        ("問題 1", "用一句話解釋 AI"),
        ("問題 2", "用一句話解釋機器學習"),
        ("問題 3", "用一句話解釋深度學習"),
    ]

    # 順序執行（實際並行會導致輸出混亂）
    for label, prompt in tasks:
        await stream_response(agent, prompt, label)


# ============================================================================
# 範例 9: 自定義流式輸出格式
# ============================================================================

class StreamFormatter:
    """流式輸出格式化器"""

    def __init__(self, width: int = 60):
        self.width = width
        self.current_line_length = 0

    async def format_stream(
        self,
        stream: AsyncIterator[str]
    ) -> AsyncIterator[str]:
        """格式化流式輸出"""
        async for chunk in stream:
            for char in chunk:
                yield char

                self.current_line_length += 1

                # 自動換行
                if char == ' ' and self.current_line_length > self.width:
                    yield '\n'
                    self.current_line_length = 0


async def example_9_custom_formatting():
    """自定義流式輸出格式"""
    print("\n" + "="*60)
    print("範例 9: 自定義格式化")
    print("="*60)

    agent = Agent('openai:gpt-4')
    formatter = StreamFormatter(width=50)

    print("AI 回應（自動換行）：\n")

    async with agent.run_stream('解釋什麼是雲端計算') as response:
        formatted = formatter.format_stream(response.stream_text())

        async for char in formatted:
            print(char, end='', flush=True)
            await asyncio.sleep(0.01)

    print("\n")


# ============================================================================
# 主程式
# ============================================================================

async def main():
    """運行所有範例"""
    print("\n" + "⚡ " + "="*58)
    print("Pydantic AI - 流式輸出範例")
    print("="*60)

    await example_1_basic_streaming()
    await example_2_streaming_with_result()
    await example_3_streaming_with_progress()
    await example_4_streaming_with_tools()
    await example_5_streaming_structured()
    await example_6_real_time_processing()
    await example_7_streaming_error_handling()
    await example_8_parallel_streaming()
    await example_9_custom_formatting()

    print("\n" + "="*60)
    print("✓ 流式輸出範例完成！")
    print("💡 流式輸出的優勢：")
    print("   1. 更好的用戶體驗")
    print("   2. 實時反饋")
    print("   3. 降低感知延遲")
    print("   4. 支持長文本生成")
    print("="*60)


if __name__ == '__main__':
    import os
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  請設置 OPENAI_API_KEY 環境變量")
    else:
        asyncio.run(main())

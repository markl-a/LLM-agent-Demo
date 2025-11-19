#!/usr/bin/env python3
"""
Semantic Kernel 快速開始示例

本示例展示：
1. Kernel 初始化
2. 添加 LLM 服務
3. 創建和執行插件
4. 基本的 Agent 使用
"""

import asyncio
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

try:
    import semantic_kernel as sk
    from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
    from semantic_kernel.functions import kernel_function
    from semantic_kernel.contents import ChatHistory
except ImportError:
    print("❌ 請安裝 Semantic Kernel:")
    print("   pip install semantic-kernel")
    exit(1)


class MathPlugin:
    """數學運算插件"""

    @kernel_function(name="add", description="將兩個數字相加")
    def add(self, number1: float, number2: float) -> float:
        """加法運算"""
        return number1 + number2

    @kernel_function(name="multiply", description="將兩個數字相乘")
    def multiply(self, number1: float, number2: float) -> float:
        """乘法運算"""
        return number1 * number2


class WeatherPlugin:
    """天氣查詢插件（模擬）"""

    @kernel_function(name="get_weather", description="獲取指定城市的天氣信息")
    def get_weather(self, city: str) -> str:
        """獲取天氣（模擬數據）"""
        # 實際應用中，這裡應該調用真實的天氣 API
        weather_data = {
            "台北": "晴天，溫度 25°C",
            "東京": "多雲，溫度 18°C",
            "紐約": "雨天，溫度 15°C",
            "倫敦": "陰天，溫度 12°C",
        }
        return weather_data.get(city, f"{city} 的天氣信息暫時無法獲取")


async def example_1_basic_kernel():
    """示例 1: 基本 Kernel 使用"""
    print("\n" + "=" * 60)
    print("示例 1: 基本 Kernel 使用")
    print("=" * 60)

    # 創建 Kernel
    kernel = sk.Kernel()

    # 檢查 API Key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  未設置 OPENAI_API_KEY")
        print("   請在 .env 文件中設置 OPENAI_API_KEY")
        return

    # 添加 OpenAI 服務
    service = OpenAIChatCompletion(
        service_id="chat-gpt",
        ai_model_id="gpt-4o-mini",
        api_key=api_key,
    )
    kernel.add_service(service)

    print("✅ Kernel 初始化完成")
    print(f"   服務數量: {len(kernel.services)}")

    # 創建簡單的提示函數
    prompt = """
    你是一個有幫助的助手。請用簡潔的方式回答問題。

    問題: {{$input}}

    答案:
    """

    # 創建函數
    answer_function = kernel.add_function(
        function_name="answer_question",
        plugin_name="QA",
        prompt=prompt,
        description="回答用戶問題",
    )

    # 調用函數
    question = "什麼是 Semantic Kernel?"
    print(f"\n💬 問題: {question}")

    result = await kernel.invoke(answer_function, input=question)

    print(f"🤖 回答: {result}")


async def example_2_plugins():
    """示例 2: 使用插件"""
    print("\n" + "=" * 60)
    print("示例 2: 使用插件")
    print("=" * 60)

    # 創建 Kernel
    kernel = sk.Kernel()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  未設置 OPENAI_API_KEY，跳過此示例")
        return

    service = OpenAIChatCompletion(
        service_id="chat-gpt", ai_model_id="gpt-4o-mini", api_key=api_key
    )
    kernel.add_service(service)

    # 添加插件
    math_plugin = kernel.add_plugin(MathPlugin(), plugin_name="Math")
    weather_plugin = kernel.add_plugin(WeatherPlugin(), plugin_name="Weather")

    print("✅ 已添加插件:")
    print("   - Math (數學運算)")
    print("   - Weather (天氣查詢)")

    # 使用數學插件
    print("\n📊 使用數學插件:")
    result = await kernel.invoke(math_plugin["add"], number1=5, number2=3)
    print(f"   5 + 3 = {result}")

    result = await kernel.invoke(math_plugin["multiply"], number1=4, number2=7)
    print(f"   4 × 7 = {result}")

    # 使用天氣插件
    print("\n🌤️  使用天氣插件:")
    cities = ["台北", "東京", "紐約"]
    for city in cities:
        result = await kernel.invoke(weather_plugin["get_weather"], city=city)
        print(f"   {city}: {result}")


async def example_3_agent_with_plugins():
    """示例 3: Agent 使用插件"""
    print("\n" + "=" * 60)
    print("示例 3: Agent 使用插件")
    print("=" * 60)

    from semantic_kernel.agents import ChatCompletionAgent

    # 創建 Kernel
    kernel = sk.Kernel()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  未設置 OPENAI_API_KEY，跳過此示例")
        return

    service = OpenAIChatCompletion(
        service_id="chat-gpt", ai_model_id="gpt-4o-mini", api_key=api_key
    )
    kernel.add_service(service)

    # 添加插件
    kernel.add_plugin(MathPlugin(), plugin_name="Math")
    kernel.add_plugin(WeatherPlugin(), plugin_name="Weather")

    # 創建 Agent
    agent = ChatCompletionAgent(
        service_id="chat-gpt",
        kernel=kernel,
        name="AssistantAgent",
        instructions="""
        你是一個有幫助的助手，可以執行數學運算和查詢天氣。

        可用的工具：
        - Math.add: 加法運算
        - Math.multiply: 乘法運算
        - Weather.get_weather: 查詢天氣

        請根據用戶的需求調用適當的工具。
        """,
    )

    print("✅ Agent 創建完成")
    print(f"   名稱: {agent.name}")
    print(f"   可用插件: Math, Weather")

    # 創建對話歷史
    chat_history = ChatHistory()

    # 測試對話
    questions = [
        "計算 15 加 27 等於多少？",
        "台北今天的天氣如何？",
        "如果一個蘋果 25 元，我買 8 個要多少錢？",
    ]

    for question in questions:
        print(f"\n💬 用戶: {question}")

        # 添加用戶消息到歷史
        chat_history.add_user_message(question)

        # Agent 處理
        response = await agent.invoke(chat_history)

        # 添加回應到歷史
        chat_history.add_message(response.messages[-1])

        print(f"🤖 Assistant: {response.messages[-1].content}")


async def example_4_chat_with_history():
    """示例 4: 帶歷史記錄的對話"""
    print("\n" + "=" * 60)
    print("示例 4: 帶歷史記錄的對話")
    print("=" * 60)

    # 創建 Kernel
    kernel = sk.Kernel()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  未設置 OPENAI_API_KEY，跳過此示例")
        return

    service = OpenAIChatCompletion(
        service_id="chat-gpt", ai_model_id="gpt-4o-mini", api_key=api_key
    )
    kernel.add_service(service)

    # 創建對話歷史
    chat_history = ChatHistory()
    chat_history.add_system_message("你是一個友善的助手，記得上下文並提供有幫助的回答。")

    print("✅ 對話系統已啟動")
    print("   輸入 'quit' 退出\n")

    # 模擬對話
    conversations = [
        "我叫張三，很高興認識你",
        "我喜歡吃披薩",
        "你還記得我叫什麼名字嗎？",
        "我喜歡吃什麼？",
    ]

    for user_input in conversations:
        # 添加用戶消息
        chat_history.add_user_message(user_input)
        print(f"💬 用戶: {user_input}")

        # 獲取回應
        response = await service.get_chat_message_content(
            chat_history=chat_history, settings=None
        )

        # 添加助手回應
        chat_history.add_message(response)
        print(f"🤖 Assistant: {response.content}\n")


async def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("🚀 Semantic Kernel 快速開始示例")
    print("=" * 60)

    try:
        # 運行所有示例
        await example_1_basic_kernel()
        await example_2_plugins()
        await example_3_agent_with_plugins()
        await example_4_chat_with_history()

    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        import traceback

        traceback.print_exc()

    print("\n" + "=" * 60)
    print("✅ 所有示例運行完成")
    print("=" * 60)


if __name__ == "__main__":
    # 運行示例
    asyncio.run(main())

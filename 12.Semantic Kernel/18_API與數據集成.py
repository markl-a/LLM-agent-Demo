#!/usr/bin/env python3
"""
Semantic Kernel - API 與數據集成示例

本示例展示：
1. API 調用封裝
2. 數據提取與轉換
3. 多數據源整合
4. 實時數據處理
5. 數據驗證
"""

import asyncio
import os
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()

try:
    import semantic_kernel as sk
    from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
    from semantic_kernel.functions import kernel_function
    from typing import Annotated
except ImportError:
    print("❌ 請安裝 Semantic Kernel:")
    print("   pip install semantic-kernel")
    exit(1)


class APIIntegrationPlugin:
    """API 集成插件（模擬）"""

    @kernel_function(name="fetch_weather", description="獲取天氣數據")
    def fetch_weather(
        self, city: Annotated[str, "城市名稱"]
    ) -> Annotated[str, "天氣數據"]:
        """獲取天氣（模擬）"""
        # 實際應該調用真實的天氣 API
        weather_data = {
            "台北": {"temp": 25, "condition": "晴天", "humidity": 65},
            "東京": {"temp": 18, "condition": "多雲", "humidity": 70},
            "紐約": {"temp": 15, "condition": "雨天", "humidity": 80},
        }

        data = weather_data.get(city, {"temp": 20, "condition": "未知", "humidity": 60})
        result = f"城市：{city}，溫度：{data['temp']}°C，天氣：{data['condition']}，濕度：{data['humidity']}%"
        print(f"  🌤️  {result}")
        return result

    @kernel_function(name="fetch_stock_price", description="獲取股票價格")
    def fetch_stock_price(
        self, symbol: Annotated[str, "股票代碼"]
    ) -> Annotated[str, "股票數據"]:
        """獲取股價（模擬）"""
        stock_data = {
            "AAPL": {"price": 175.50, "change": +2.3},
            "GOOGL": {"price": 142.20, "change": -1.5},
            "TSLA": {"price": 252.80, "change": +5.7},
        }

        data = stock_data.get(symbol, {"price": 100.0, "change": 0.0})
        result = f"股票：{symbol}，價格：${data['price']}，漲跌：{data['change']:+.1f}%"
        print(f"  📈 {result}")
        return result

    @kernel_function(name="fetch_news", description="獲取新聞")
    def fetch_news(
        self, topic: Annotated[str, "新聞主題"]
    ) -> Annotated[str, "新聞列表"]:
        """獲取新聞（模擬）"""
        news_db = {
            "科技": [
                "蘋果發布新款 iPhone",
                "AI 技術突破性進展",
                "量子計算新里程碑",
            ],
            "財經": [
                "央行宣布降息",
                "股市創新高",
                "加密貨幣監管加強",
            ],
        }

        news = news_db.get(topic, ["暫無相關新聞"])
        result = "\n".join([f"- {n}" for n in news])
        print(f"  📰 新聞 ({topic}):\n{result}")
        return result


async def example_basic_api_call():
    """示例 1: 基本 API 調用"""
    print("\n" + "=" * 60)
    print("示例 1: 基本 API 調用")
    print("=" * 60)

    kernel = sk.Kernel()

    # 添加 API 插件
    api_plugin = kernel.add_plugin(
        APIIntegrationPlugin(), plugin_name="APIIntegration"
    )

    print("✅ 已添加 API 集成插件\n")

    # 調用 API
    print("📡 調用天氣 API:")
    weather = await kernel.invoke(api_plugin["fetch_weather"], city="台北")

    print("\n📡 調用股票 API:")
    stock = await kernel.invoke(api_plugin["fetch_stock_price"], symbol="AAPL")

    print("\n📡 調用新聞 API:")
    news = await kernel.invoke(api_plugin["fetch_news"], topic="科技")


async def example_ai_with_api():
    """示例 2: AI + API 集成"""
    print("\n" + "=" * 60)
    print("示例 2: AI + API 集成")
    print("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  未設置 OPENAI_API_KEY")
        return

    kernel = sk.Kernel()
    service = OpenAIChatCompletion(
        service_id="chat-gpt",
        ai_model_id="gpt-4o-mini",
        api_key=api_key,
    )
    kernel.add_service(service)

    # 添加 API 插件
    kernel.add_plugin(APIIntegrationPlugin(), plugin_name="API")

    # 使用函數調用
    from semantic_kernel.connectors.ai.function_choice_behavior import (
        FunctionChoiceBehavior,
    )
    from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings import (
        OpenAIChatPromptExecutionSettings,
    )
    from semantic_kernel.contents import ChatHistory

    execution_settings = OpenAIChatPromptExecutionSettings(
        function_choice_behavior=FunctionChoiceBehavior.Auto()
    )

    chat_history = ChatHistory()
    chat_history.add_system_message(
        "你是一個有幫助的助手，可以調用 API 獲取實時數據。"
    )

    queries = [
        "台北今天天氣如何？",
        "AAPL 股票現在多少錢？",
        "有什麼科技新聞？",
    ]

    for query in queries:
        print(f"\n💬 用戶: {query}")

        chat_history.add_user_message(query)

        result = await service.get_chat_message_content(
            chat_history=chat_history,
            settings=execution_settings,
            kernel=kernel,
        )

        chat_history.add_message(result)
        print(f"🤖 助手: {result.content}")


async def example_data_transformation():
    """示例 3: 數據轉換"""
    print("\n" + "=" * 60)
    print("示例 3: 數據轉換")
    print("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  未設置 OPENAI_API_KEY")
        return

    kernel = sk.Kernel()
    service = OpenAIChatCompletion(
        service_id="chat-gpt",
        ai_model_id="gpt-4o-mini",
        api_key=api_key,
    )
    kernel.add_service(service)

    transform_prompt = """
    將以下 API 響應數據轉換為用戶友好的格式：

    原始數據：
    {{$raw_data}}

    轉換後的格式：{{$target_format}}

    轉換：
    """

    transform_function = kernel.add_function(
        function_name="transform_data",
        plugin_name="DataTransform",
        prompt=transform_prompt,
        description="數據轉換",
    )

    # 原始 API 數據
    raw_api_data = """
    {
        "userId": 123,
        "items": [
            {"id": "P001", "qty": 2, "price": 19.99},
            {"id": "P002", "qty": 1, "price": 49.99}
        ],
        "total": 89.97,
        "status": "pending"
    }
    """

    target_formats = ["清單格式", "表格", "摘要文字"]

    for fmt in target_formats:
        print(f"\n🔄 目標格式: {fmt}")

        result = await kernel.invoke(
            transform_function,
            raw_data=raw_api_data,
            target_format=fmt,
        )

        print(f"✅ 轉換結果:\n{result}\n")
        print("-" * 60)


async def example_multi_source_integration():
    """示例 4: 多數據源整合"""
    print("\n" + "=" * 60)
    print("示例 4: 多數據源整合")
    print("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  未設置 OPENAI_API_KEY")
        return

    kernel = sk.Kernel()
    service = OpenAIChatCompletion(
        service_id="chat-gpt",
        ai_model_id="gpt-4o-mini",
        api_key=api_key,
    )
    kernel.add_service(service)

    api_plugin = kernel.add_plugin(
        APIIntegrationPlugin(), plugin_name="API"
    )

    print("🔄 從多個 API 獲取數據...\n")

    # 獲取多個數據源
    weather = await kernel.invoke(api_plugin["fetch_weather"], city="台北")
    stock = await kernel.invoke(api_plugin["fetch_stock_price"], symbol="AAPL")
    news = await kernel.invoke(api_plugin["fetch_news"], topic="財經")

    # 整合數據
    integrate_prompt = """
    整合以下來自不同數據源的信息，生成一份每日簡報：

    天氣：{{$weather}}
    股市：{{$stock}}
    新聞：{{$news}}

    簡報格式：
    - 簡潔明瞭
    - 突出重點
    - 包含建議

    每日簡報：
    """

    integrate_function = kernel.add_function(
        function_name="integrate_data",
        plugin_name="DataIntegration",
        prompt=integrate_prompt,
        description="整合數據",
    )

    print("\n📊 整合數據生成簡報...\n")

    report = await kernel.invoke(
        integrate_function,
        weather=str(weather),
        stock=str(stock),
        news=str(news),
    )

    print(f"📋 每日簡報:\n{report}")


async def example_data_validation():
    """示例 5: 數據驗證"""
    print("\n" + "=" * 60)
    print("示例 5: 數據驗證")
    print("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  未設置 OPENAI_API_KEY")
        return

    kernel = sk.Kernel()
    service = OpenAIChatCompletion(
        service_id="chat-gpt",
        ai_model_id="gpt-4o-mini",
        api_key=api_key,
    )
    kernel.add_service(service)

    validate_prompt = """
    驗證以下 API 響應數據的完整性和正確性：

    {{$data}}

    檢查：
    - 必需字段是否存在
    - 數據類型是否正確
    - 數值是否在合理範圍內
    - 是否有異常值

    返回 JSON 格式：
    {
        "valid": true/false,
        "errors": ["錯誤列表"],
        "warnings": ["警告列表"],
        "suggestions": ["改進建議"]
    }

    驗證結果：
    """

    validate_function = kernel.add_function(
        function_name="validate_data",
        plugin_name="DataValidation",
        prompt=validate_prompt,
        description="驗證數據",
    )

    # 測試數據
    test_data = [
        '{"name": "John", "age": 25, "email": "john@example.com"}',
        '{"name": "Mary", "age": -5, "email": "invalid-email"}',
        '{"name": "", "age": 999, "email": "mary@example.com"}',
    ]

    for data in test_data:
        print(f"\n🔍 驗證數據: {data}")

        result = await kernel.invoke(validate_function, data=data)

        print(f"✅ 驗證結果:\n{result}\n")
        print("-" * 60)


async def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("🚀 Semantic Kernel - API 與數據集成示例")
    print("=" * 60)

    try:
        await example_basic_api_call()
        await example_ai_with_api()
        await example_data_transformation()
        await example_multi_source_integration()
        await example_data_validation()

    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("✅ 所有示例運行完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
Semantic Kernel - 函數調用示例

本示例展示：
1. 原生函數（Native Functions）
2. 自動函數調用
3. 函數參數和返回值
4. 並行函數調用
5. 函數組合
"""

import asyncio
import os
import math
from datetime import datetime
from typing import Annotated
from dotenv import load_dotenv

load_dotenv()

try:
    import semantic_kernel as sk
    from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
    from semantic_kernel.functions import kernel_function
    from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
    from semantic_kernel.contents import ChatHistory
    from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings import (
        OpenAIChatPromptExecutionSettings,
    )
except ImportError:
    print("❌ 請安裝 Semantic Kernel:")
    print("   pip install semantic-kernel")
    exit(1)


# 定義工具插件
class MathToolsPlugin:
    """數學工具插件"""

    @kernel_function(name="add", description="將兩個數字相加")
    def add(
        self,
        number1: Annotated[float, "第一個數字"],
        number2: Annotated[float, "第二個數字"],
    ) -> Annotated[float, "兩數之和"]:
        """加法"""
        result = number1 + number2
        print(f"  🔢 計算: {number1} + {number2} = {result}")
        return result

    @kernel_function(name="multiply", description="將兩個數字相乘")
    def multiply(
        self,
        number1: Annotated[float, "第一個數字"],
        number2: Annotated[float, "第二個數字"],
    ) -> Annotated[float, "兩數之積"]:
        """乘法"""
        result = number1 * number2
        print(f"  🔢 計算: {number1} × {number2} = {result}")
        return result

    @kernel_function(name="sqrt", description="計算數字的平方根")
    def sqrt(
        self, number: Annotated[float, "要計算平方根的數字"]
    ) -> Annotated[float, "平方根"]:
        """平方根"""
        result = math.sqrt(number)
        print(f"  🔢 計算: √{number} = {result}")
        return result

    @kernel_function(name="power", description="計算數字的冪")
    def power(
        self,
        base: Annotated[float, "底數"],
        exponent: Annotated[float, "指數"],
    ) -> Annotated[float, "冪運算結果"]:
        """冪運算"""
        result = base ** exponent
        print(f"  🔢 計算: {base}^{exponent} = {result}")
        return result


class TimeToolsPlugin:
    """時間工具插件"""

    @kernel_function(name="get_current_time", description="獲取當前時間")
    def get_current_time(self) -> Annotated[str, "當前時間"]:
        """獲取當前時間"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"  🕐 當前時間: {now}")
        return now

    @kernel_function(name="get_day_of_week", description="獲取今天是星期幾")
    def get_day_of_week(self) -> Annotated[str, "星期幾"]:
        """獲取星期幾"""
        days = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        today = days[datetime.now().weekday()]
        print(f"  📅 今天是: {today}")
        return today


class StringToolsPlugin:
    """字符串工具插件"""

    @kernel_function(name="to_uppercase", description="將文本轉換為大寫")
    def to_uppercase(
        self, text: Annotated[str, "要轉換的文本"]
    ) -> Annotated[str, "大寫文本"]:
        """轉大寫"""
        result = text.upper()
        print(f"  📝 轉換: '{text}' → '{result}'")
        return result

    @kernel_function(name="reverse_string", description="反轉字符串")
    def reverse_string(
        self, text: Annotated[str, "要反轉的文本"]
    ) -> Annotated[str, "反轉後的文本"]:
        """反轉字符串"""
        result = text[::-1]
        print(f"  📝 反轉: '{text}' → '{result}'")
        return result

    @kernel_function(name="count_words", description="計算文本中的單詞數")
    def count_words(
        self, text: Annotated[str, "要計算的文本"]
    ) -> Annotated[int, "單詞數"]:
        """計算單詞數"""
        count = len(text.split())
        print(f"  📝 單詞數: {count}")
        return count


async def example_basic_function_calling():
    """示例 1: 基本函數調用"""
    print("\n" + "=" * 60)
    print("示例 1: 基本函數調用")
    print("=" * 60)

    kernel = sk.Kernel()

    # 添加插件
    math_plugin = kernel.add_plugin(MathToolsPlugin(), plugin_name="Math")

    print("✅ 已添加數學工具插件\n")

    # 直接調用函數
    print("🔧 直接調用函數:")
    result1 = await kernel.invoke(math_plugin["add"], number1=10, number2=5)
    result2 = await kernel.invoke(math_plugin["multiply"], number1=7, number2=8)
    result3 = await kernel.invoke(math_plugin["sqrt"], number=16)

    print(f"\n📊 結果: {result1}, {result2}, {result3}")


async def example_auto_function_calling():
    """示例 2: 自動函數調用"""
    print("\n" + "=" * 60)
    print("示例 2: 自動函數調用（Function Calling）")
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

    # 添加插件
    kernel.add_plugin(MathToolsPlugin(), plugin_name="Math")
    kernel.add_plugin(TimeToolsPlugin(), plugin_name="Time")
    kernel.add_plugin(StringToolsPlugin(), plugin_name="String")

    print("✅ 已添加所有工具插件\n")

    # 啟用自動函數調用
    execution_settings = OpenAIChatPromptExecutionSettings(
        function_choice_behavior=FunctionChoiceBehavior.Auto()
    )

    chat_history = ChatHistory()
    chat_history.add_system_message(
        "你是一個有幫助的助手，可以使用各種工具來完成任務。"
    )

    tasks = [
        "計算 25 加 17",
        "現在幾點？",
        "將 'hello world' 轉換為大寫",
        "計算 5 的平方根",
        "今天星期幾？",
    ]

    for task in tasks:
        print(f"💬 用戶: {task}")

        chat_history.add_user_message(task)

        result = await service.get_chat_message_content(
            chat_history=chat_history,
            settings=execution_settings,
            kernel=kernel,
        )

        chat_history.add_message(result)
        print(f"🤖 助手: {result.content}\n")


async def example_complex_function_calling():
    """示例 3: 複雜函數調用"""
    print("\n" + "=" * 60)
    print("示例 3: 複雜函數調用")
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

    kernel.add_plugin(MathToolsPlugin(), plugin_name="Math")

    execution_settings = OpenAIChatPromptExecutionSettings(
        function_choice_behavior=FunctionChoiceBehavior.Auto()
    )

    chat_history = ChatHistory()
    chat_history.add_system_message(
        "你是一個數學助手，可以執行複雜的計算。"
    )

    # 需要多步計算的任務
    complex_tasks = [
        "計算 (15 + 25) 的平方根",
        "計算 3 的 4 次方，然後加上 10",
        "如果一個正方形的面積是 64，它的邊長是多少？",
    ]

    for task in complex_tasks:
        print(f"💬 用戶: {task}")

        chat_history.add_user_message(task)

        result = await service.get_chat_message_content(
            chat_history=chat_history,
            settings=execution_settings,
            kernel=kernel,
        )

        chat_history.add_message(result)
        print(f"🤖 助手: {result.content}\n")


async def example_function_composition():
    """示例 4: 函數組合"""
    print("\n" + "=" * 60)
    print("示例 4: 函數組合")
    print("=" * 60)

    kernel = sk.Kernel()

    math_plugin = kernel.add_plugin(MathToolsPlugin(), plugin_name="Math")
    string_plugin = kernel.add_plugin(StringToolsPlugin(), plugin_name="String")

    print("✅ 測試函數組合\n")

    # 組合多個函數調用
    print("🔗 步驟 1: 數學計算")
    step1 = await kernel.invoke(math_plugin["add"], number1=10, number2=20)
    print(f"   結果: {step1}")

    print("\n🔗 步驟 2: 轉換為字符串並反轉")
    step2 = await kernel.invoke(
        string_plugin["reverse_string"], text=str(step1)
    )
    print(f"   結果: {step2}")

    print("\n✅ 最終結果:", step2)


async def example_parallel_function_calling():
    """示例 5: 並行函數調用"""
    print("\n" + "=" * 60)
    print("示例 5: 並行函數調用")
    print("=" * 60)

    kernel = sk.Kernel()

    math_plugin = kernel.add_plugin(MathToolsPlugin(), plugin_name="Math")
    time_plugin = kernel.add_plugin(TimeToolsPlugin(), plugin_name="Time")

    print("🔄 並行執行多個函數...\n")

    # 並行調用
    results = await asyncio.gather(
        kernel.invoke(math_plugin["add"], number1=5, number2=10),
        kernel.invoke(math_plugin["multiply"], number1=3, number2=7),
        kernel.invoke(math_plugin["sqrt"], number=25),
        kernel.invoke(time_plugin["get_current_time"]),
        kernel.invoke(time_plugin["get_day_of_week"]),
    )

    print(f"\n✅ 所有函數執行完成")
    print(f"📊 結果: {results}")


async def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("🚀 Semantic Kernel - 函數調用示例")
    print("=" * 60)

    try:
        await example_basic_function_calling()
        await example_auto_function_calling()
        await example_complex_function_calling()
        await example_function_composition()
        await example_parallel_function_calling()

    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("✅ 所有示例運行完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
Semantic Kernel - 規劃器（Planner）示例

本示例展示：
1. 基本規劃功能
2. 多步驟計劃執行
3. 動態規劃調整
4. 計劃驗證
"""

import asyncio
import os
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


class TaskPlannerPlugin:
    """任務規劃插件"""

    @kernel_function(name="break_down_task", description="將複雜任務分解為步驟")
    def break_down_task(self, task: str) -> str:
        """分解任務"""
        steps = f"""
任務: {task}

分解步驟:
1. 分析任務需求
2. 識別所需資源
3. 制定執行計劃
4. 執行並驗證
5. 總結和優化
"""
        print(f"📋 任務已分解:\n{steps}")
        return steps

    @kernel_function(name="estimate_time", description="估算任務所需時間")
    def estimate_time(self, task: str) -> str:
        """估算時間"""
        # 簡化的時間估算
        word_count = len(task.split())
        estimated_hours = max(1, word_count // 10)
        result = f"估計需要 {estimated_hours} 小時完成"
        print(f"⏱️  {result}")
        return result

    @kernel_function(name="prioritize_tasks", description="為任務列表排定優先級")
    def prioritize_tasks(self, tasks: str) -> str:
        """任務優先級排序"""
        task_list = tasks.split(",")
        result = "優先級排序:\n"
        for i, task in enumerate(task_list, 1):
            result += f"{i}. {task.strip()}\n"
        print(f"🎯 {result}")
        return result


class ResearchPlugin:
    """研究工具插件"""

    @kernel_function(name="gather_info", description="收集資訊")
    def gather_info(self, topic: str) -> str:
        """收集資訊（模擬）"""
        result = f"已收集關於 '{topic}' 的資訊"
        print(f"📚 {result}")
        return result

    @kernel_function(name="analyze_data", description="分析數據")
    def analyze_data(self, data: str) -> str:
        """分析數據（模擬）"""
        result = f"已分析數據: {data[:50]}..."
        print(f"📊 {result}")
        return result


async def example_basic_planning():
    """示例 1: 基本規劃"""
    print("\n" + "=" * 60)
    print("示例 1: 基本規劃")
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

    kernel.add_plugin(TaskPlannerPlugin(), plugin_name="Planner")

    execution_settings = OpenAIChatPromptExecutionSettings(
        function_choice_behavior=FunctionChoiceBehavior.Auto()
    )

    chat_history = ChatHistory()
    chat_history.add_system_message(
        "你是一個專業的任務規劃助手，幫助用戶分解和規劃任務。"
    )

    task = "創建一個 AI 驅動的客服系統"
    print(f"💬 用戶任務: {task}\n")

    chat_history.add_user_message(f"請幫我規劃這個任務: {task}")

    result = await service.get_chat_message_content(
        chat_history=chat_history,
        settings=execution_settings,
        kernel=kernel,
    )

    print(f"\n🤖 規劃結果:\n{result.content}")


async def example_multi_step_plan():
    """示例 2: 多步驟計劃執行"""
    print("\n" + "=" * 60)
    print("示例 2: 多步驟計劃執行")
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

    kernel.add_plugin(TaskPlannerPlugin(), plugin_name="Planner")
    kernel.add_plugin(ResearchPlugin(), plugin_name="Research")

    execution_settings = OpenAIChatPromptExecutionSettings(
        function_choice_behavior=FunctionChoiceBehavior.Auto()
    )

    chat_history = ChatHistory()
    chat_history.add_system_message(
        "你是一個研究助手，可以規劃和執行研究任務。"
    )

    goal = "研究機器學習在醫療診斷中的應用"
    print(f"🎯 研究目標: {goal}\n")

    steps = [
        "請分解這個研究任務的步驟",
        "估算完成這個研究需要多少時間",
        "開始收集相關資訊",
    ]

    for step in steps:
        print(f"💬 用戶: {step}")

        chat_history.add_user_message(f"{goal}。{step}")

        result = await service.get_chat_message_content(
            chat_history=chat_history,
            settings=execution_settings,
            kernel=kernel,
        )

        chat_history.add_message(result)
        print(f"🤖 助手: {result.content}\n")


async def example_dynamic_planning():
    """示例 3: 動態規劃調整"""
    print("\n" + "=" * 60)
    print("示例 3: 動態規劃調整")
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

    kernel.add_plugin(TaskPlannerPlugin(), plugin_name="Planner")

    execution_settings = OpenAIChatPromptExecutionSettings(
        function_choice_behavior=FunctionChoiceBehavior.Auto()
    )

    chat_history = ChatHistory()
    chat_history.add_system_message(
        "你是一個靈活的規劃助手，可以根據情況調整計劃。"
    )

    # 初始計劃
    initial_task = "組織一個團隊建設活動"
    print(f"📝 初始任務: {initial_task}")

    chat_history.add_user_message(f"請為以下任務制定計劃: {initial_task}")

    result = await service.get_chat_message_content(
        chat_history=chat_history,
        settings=execution_settings,
        kernel=kernel,
    )

    chat_history.add_message(result)
    print(f"🤖 初始計劃:\n{result.content}\n")

    # 調整計劃
    adjustment = "預算減少了 30%，請調整計劃"
    print(f"⚠️  變更: {adjustment}")

    chat_history.add_user_message(adjustment)

    adjusted_result = await service.get_chat_message_content(
        chat_history=chat_history,
        settings=execution_settings,
        kernel=kernel,
    )

    print(f"🤖 調整後的計劃:\n{adjusted_result.content}")


async def example_priority_planning():
    """示例 4: 優先級規劃"""
    print("\n" + "=" * 60)
    print("示例 4: 優先級規劃")
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

    kernel.add_plugin(TaskPlannerPlugin(), plugin_name="Planner")

    execution_settings = OpenAIChatPromptExecutionSettings(
        function_choice_behavior=FunctionChoiceBehavior.Auto()
    )

    chat_history = ChatHistory()
    chat_history.add_system_message(
        "你是一個時間管理專家，幫助用戶排定任務優先級。"
    )

    tasks = "寫項目報告, 回覆郵件, 準備明天的會議, 代碼審查, 團隊一對一"
    print(f"📋 待辦任務: {tasks}\n")

    chat_history.add_user_message(
        f"我有以下任務需要完成，請幫我排定優先級: {tasks}"
    )

    result = await service.get_chat_message_content(
        chat_history=chat_history,
        settings=execution_settings,
        kernel=kernel,
    )

    print(f"🤖 優先級建議:\n{result.content}")


async def example_goal_oriented_planning():
    """示例 5: 目標導向規劃"""
    print("\n" + "=" * 60)
    print("示例 5: 目標導向規劃")
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

    chat_history = ChatHistory()
    chat_history.add_system_message(
        """你是一個目標規劃專家，幫助用戶達成目標。
        請使用 SMART 原則（具體、可衡量、可達成、相關、有時限）來規劃。"""
    )

    goal = "在 6 個月內學會使用 Python 進行數據分析"
    print(f"🎯 目標: {goal}\n")

    chat_history.add_user_message(
        f"請幫我制定一個達成以下目標的詳細計劃: {goal}"
    )

    result = await service.get_chat_message_content(
        chat_history=chat_history, settings=None
    )

    print(f"🤖 規劃建議:\n{result.content}")


async def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("🚀 Semantic Kernel - 規劃器示例")
    print("=" * 60)

    try:
        await example_basic_planning()
        await example_multi_step_plan()
        await example_dynamic_planning()
        await example_priority_planning()
        await example_goal_oriented_planning()

    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("✅ 所有示例運行完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

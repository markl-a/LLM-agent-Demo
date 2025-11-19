#!/usr/bin/env python3
"""
Semantic Kernel - 多 LLM 提供商示例

本示例展示如何在 Semantic Kernel 中使用不同的 LLM 提供商：
1. OpenAI GPT-4
2. Anthropic Claude
3. Google Gemini
4. 在同一個應用中切換使用
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

try:
    import semantic_kernel as sk
    from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
    from semantic_kernel.connectors.ai.anthropic import AnthropicChatCompletion
    from semantic_kernel.connectors.ai.google import GoogleAIChatCompletion
    from semantic_kernel.contents import ChatHistory
except ImportError:
    print("❌ 請安裝所需套件:")
    print("   pip install semantic-kernel anthropic google-generativeai")
    exit(1)


async def example_openai():
    """示例 1: 使用 OpenAI"""
    print("\n" + "=" * 60)
    print("示例 1: OpenAI GPT-4")
    print("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  未設置 OPENAI_API_KEY")
        return

    kernel = sk.Kernel()
    service = OpenAIChatCompletion(
        service_id="openai-gpt4",
        ai_model_id="gpt-4o-mini",
        api_key=api_key,
    )
    kernel.add_service(service)

    prompt = "用一句話解釋什麼是量子計算"
    print(f"💬 提示: {prompt}")

    chat_history = ChatHistory()
    chat_history.add_user_message(prompt)

    response = await service.get_chat_message_content(
        chat_history=chat_history, settings=None
    )

    print(f"🤖 OpenAI 回應: {response.content}")
    print(f"📊 模型: {service.ai_model_id}")


async def example_anthropic():
    """示例 2: 使用 Anthropic Claude"""
    print("\n" + "=" * 60)
    print("示例 2: Anthropic Claude")
    print("=" * 60)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("⚠️  未設置 ANTHROPIC_API_KEY")
        return

    kernel = sk.Kernel()
    service = AnthropicChatCompletion(
        service_id="claude",
        ai_model_id="claude-3-5-sonnet-20241022",
        api_key=api_key,
    )
    kernel.add_service(service)

    prompt = "用一句話解釋什麼是量子計算"
    print(f"💬 提示: {prompt}")

    chat_history = ChatHistory()
    chat_history.add_user_message(prompt)

    response = await service.get_chat_message_content(
        chat_history=chat_history, settings=None
    )

    print(f"🤖 Claude 回應: {response.content}")
    print(f"📊 模型: {service.ai_model_id}")


async def example_google():
    """示例 3: 使用 Google Gemini"""
    print("\n" + "=" * 60)
    print("示例 3: Google Gemini")
    print("=" * 60)

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("⚠️  未設置 GOOGLE_API_KEY")
        return

    kernel = sk.Kernel()
    service = GoogleAIChatCompletion(
        service_id="gemini",
        ai_model_id="gemini-2.0-flash-exp",
        api_key=api_key,
    )
    kernel.add_service(service)

    prompt = "用一句話解釋什麼是量子計算"
    print(f"💬 提示: {prompt}")

    chat_history = ChatHistory()
    chat_history.add_user_message(prompt)

    response = await service.get_chat_message_content(
        chat_history=chat_history, settings=None
    )

    print(f"🤖 Gemini 回應: {response.content}")
    print(f"📊 模型: {service.ai_model_id}")


async def example_multi_provider_comparison():
    """示例 4: 多提供商比較"""
    print("\n" + "=" * 60)
    print("示例 4: 多提供商結果比較")
    print("=" * 60)

    kernel = sk.Kernel()

    # 添加所有可用的服務
    providers = []

    if os.getenv("OPENAI_API_KEY"):
        openai_service = OpenAIChatCompletion(
            service_id="openai",
            ai_model_id="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        kernel.add_service(openai_service)
        providers.append(("OpenAI GPT-4", openai_service))

    if os.getenv("ANTHROPIC_API_KEY"):
        claude_service = AnthropicChatCompletion(
            service_id="claude",
            ai_model_id="claude-3-5-sonnet-20241022",
            api_key=os.getenv("ANTHROPIC_API_KEY"),
        )
        kernel.add_service(claude_service)
        providers.append(("Anthropic Claude", claude_service))

    if os.getenv("GOOGLE_API_KEY"):
        gemini_service = GoogleAIChatCompletion(
            service_id="gemini",
            ai_model_id="gemini-2.0-flash-exp",
            api_key=os.getenv("GOOGLE_API_KEY"),
        )
        kernel.add_service(gemini_service)
        providers.append(("Google Gemini", gemini_service))

    if not providers:
        print("⚠️  請至少設置一個 API Key")
        return

    prompt = "給我 3 個提高生產力的建議"
    print(f"💬 提示: {prompt}\n")

    for name, service in providers:
        print(f"🤖 {name}:")

        chat_history = ChatHistory()
        chat_history.add_user_message(prompt)

        response = await service.get_chat_message_content(
            chat_history=chat_history, settings=None
        )

        print(f"{response.content}\n")


async def example_provider_selection():
    """示例 5: 根據任務選擇提供商"""
    print("\n" + "=" * 60)
    print("示例 5: 智能選擇 LLM 提供商")
    print("=" * 60)

    kernel = sk.Kernel()

    # 根據任務類型選擇最佳提供商
    tasks = {
        "creative_writing": {
            "task": "寫一首關於秋天的短詩",
            "best_provider": "claude",  # Claude 擅長創意寫作
        },
        "code_generation": {
            "task": "寫一個 Python 快速排序函數",
            "best_provider": "openai",  # GPT-4 擅長代碼
        },
        "data_analysis": {
            "task": "分析這組數據的趨勢: [1, 3, 7, 15, 31]",
            "best_provider": "gemini",  # Gemini 擅長分析
        },
    }

    # 添加服務
    if os.getenv("OPENAI_API_KEY"):
        kernel.add_service(
            OpenAIChatCompletion(
                service_id="openai",
                ai_model_id="gpt-4o-mini",
                api_key=os.getenv("OPENAI_API_KEY"),
            )
        )

    if os.getenv("ANTHROPIC_API_KEY"):
        kernel.add_service(
            AnthropicChatCompletion(
                service_id="claude",
                ai_model_id="claude-3-5-sonnet-20241022",
                api_key=os.getenv("ANTHROPIC_API_KEY"),
            )
        )

    if os.getenv("GOOGLE_API_KEY"):
        kernel.add_service(
            GoogleAIChatCompletion(
                service_id="gemini",
                ai_model_id="gemini-2.0-flash-exp",
                api_key=os.getenv("GOOGLE_API_KEY"),
            )
        )

    for task_type, task_info in tasks.items():
        service_id = task_info["best_provider"]
        task = task_info["task"]

        # 檢查服務是否可用
        try:
            service = kernel.get_service(service_id)
        except:
            print(f"⚠️  {service_id} 服務不可用，跳過任務: {task_type}")
            continue

        print(f"\n📋 任務類型: {task_type}")
        print(f"🎯 選擇提供商: {service_id}")
        print(f"💬 任務: {task}")

        chat_history = ChatHistory()
        chat_history.add_user_message(task)

        response = await service.get_chat_message_content(
            chat_history=chat_history, settings=None
        )

        print(f"🤖 回應: {response.content}")


async def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("🚀 Semantic Kernel - 多 LLM 提供商示例")
    print("=" * 60)

    try:
        await example_openai()
        await example_anthropic()
        await example_google()
        await example_multi_provider_comparison()
        await example_provider_selection()

    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("✅ 示例運行完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

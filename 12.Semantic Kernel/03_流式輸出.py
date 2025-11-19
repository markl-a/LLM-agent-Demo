#!/usr/bin/env python3
"""
Semantic Kernel - 流式輸出示例

本示例展示如何使用流式輸出：
1. 基本流式響應
2. 流式 Token 計數
3. 流式處理中的錯誤處理
4. 並行流式請求
"""

import asyncio
import os
from dotenv import load_dotenv
from typing import AsyncIterable

load_dotenv()

try:
    import semantic_kernel as sk
    from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
    from semantic_kernel.contents import ChatHistory, StreamingChatMessageContent
except ImportError:
    print("❌ 請安裝 Semantic Kernel:")
    print("   pip install semantic-kernel")
    exit(1)


async def example_basic_streaming():
    """示例 1: 基本流式輸出"""
    print("\n" + "=" * 60)
    print("示例 1: 基本流式輸出")
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

    prompt = "請詳細解釋機器學習的基本概念"
    print(f"💬 提示: {prompt}")
    print("🔄 流式輸出:\n")

    chat_history = ChatHistory()
    chat_history.add_user_message(prompt)

    # 流式獲取響應
    response_stream = service.get_streaming_chat_message_content(
        chat_history=chat_history, settings=None
    )

    full_response = ""
    async for chunk in response_stream:
        if chunk:
            content = str(chunk)
            print(content, end="", flush=True)
            full_response += content

    print("\n\n✅ 流式輸出完成")
    print(f"📏 總字符數: {len(full_response)}")


async def example_streaming_with_token_count():
    """示例 2: 流式輸出 + Token 計數"""
    print("\n" + "=" * 60)
    print("示例 2: 流式輸出 + Token 計數")
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

    prompt = "列出 5 個著名的 AI 研究機構"
    print(f"💬 提示: {prompt}")
    print("🔄 流式輸出:\n")

    chat_history = ChatHistory()
    chat_history.add_user_message(prompt)

    response_stream = service.get_streaming_chat_message_content(
        chat_history=chat_history, settings=None
    )

    chunk_count = 0
    full_response = ""

    async for chunk in response_stream:
        if chunk:
            content = str(chunk)
            print(content, end="", flush=True)
            full_response += content
            chunk_count += 1

    print(f"\n\n✅ 流式輸出完成")
    print(f"📦 Chunk 數量: {chunk_count}")
    print(f"📏 總字符數: {len(full_response)}")
    print(f"📊 平均每個 Chunk: {len(full_response) / chunk_count:.1f} 字符")


async def example_streaming_with_progress():
    """示例 3: 帶進度指示器的流式輸出"""
    print("\n" + "=" * 60)
    print("示例 3: 帶進度指示器的流式輸出")
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

    prompt = "寫一個關於春天的 100 字短文"
    print(f"💬 提示: {prompt}")
    print("🔄 流式輸出:\n")

    chat_history = ChatHistory()
    chat_history.add_user_message(prompt)

    response_stream = service.get_streaming_chat_message_content(
        chat_history=chat_history, settings=None
    )

    full_response = ""
    char_count = 0
    target_length = 100

    async for chunk in response_stream:
        if chunk:
            content = str(chunk)
            print(content, end="", flush=True)
            full_response += content
            char_count = len(full_response)

            # 顯示進度
            if char_count % 10 == 0:
                progress = min(100, (char_count / target_length) * 100)
                # 在新行顯示進度
                # print(f"\n[進度: {progress:.0f}%]", end="", flush=True)

    print(f"\n\n✅ 流式輸出完成")
    print(f"📏 最終字符數: {char_count}")


async def example_parallel_streaming():
    """示例 4: 並行流式請求"""
    print("\n" + "=" * 60)
    print("示例 4: 並行流式請求")
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

    prompts = [
        "用一句話介紹 Python",
        "用一句話介紹 JavaScript",
        "用一句話介紹 Rust",
    ]

    async def stream_response(prompt: str, index: int):
        """流式處理單個響應"""
        print(f"\n🔄 請求 {index + 1}: {prompt}")

        chat_history = ChatHistory()
        chat_history.add_user_message(prompt)

        response_stream = service.get_streaming_chat_message_content(
            chat_history=chat_history, settings=None
        )

        full_response = ""
        async for chunk in response_stream:
            if chunk:
                full_response += str(chunk)

        print(f"✅ 響應 {index + 1}: {full_response}")
        return full_response

    # 並行執行所有請求
    tasks = [stream_response(prompt, i) for i, prompt in enumerate(prompts)]
    results = await asyncio.gather(*tasks)

    print(f"\n✅ 完成 {len(results)} 個並行流式請求")


async def example_streaming_chat():
    """示例 5: 流式多輪對話"""
    print("\n" + "=" * 60)
    print("示例 5: 流式多輪對話")
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
    chat_history.add_system_message("你是一個友善的助手，回答要簡潔。")

    conversations = [
        "你好！我想學習 Python",
        "我應該從哪裡開始？",
        "謝謝你的建議！",
    ]

    for user_message in conversations:
        print(f"\n💬 用戶: {user_message}")
        print("🤖 助手: ", end="", flush=True)

        chat_history.add_user_message(user_message)

        response_stream = service.get_streaming_chat_message_content(
            chat_history=chat_history, settings=None
        )

        full_response = ""
        async for chunk in response_stream:
            if chunk:
                content = str(chunk)
                print(content, end="", flush=True)
                full_response += content

        # 將助手回應添加到歷史
        chat_history.add_assistant_message(full_response)
        print()  # 換行

    print("\n✅ 對話完成")


async def example_streaming_with_error_handling():
    """示例 6: 流式輸出的錯誤處理"""
    print("\n" + "=" * 60)
    print("示例 6: 流式輸出的錯誤處理")
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

    prompt = "解釋什麼是深度學習"
    print(f"💬 提示: {prompt}")
    print("🔄 流式輸出（含錯誤處理）:\n")

    chat_history = ChatHistory()
    chat_history.add_user_message(prompt)

    try:
        response_stream = service.get_streaming_chat_message_content(
            chat_history=chat_history, settings=None
        )

        full_response = ""
        async for chunk in response_stream:
            if chunk:
                content = str(chunk)
                print(content, end="", flush=True)
                full_response += content

        print(f"\n\n✅ 成功完成流式輸出")

    except Exception as e:
        print(f"\n\n❌ 流式輸出過程中發生錯誤: {e}")
        print("💡 建議：檢查 API Key 和網絡連接")


async def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("🚀 Semantic Kernel - 流式輸出示例")
    print("=" * 60)

    try:
        await example_basic_streaming()
        await example_streaming_with_token_count()
        await example_streaming_with_progress()
        await example_parallel_streaming()
        await example_streaming_chat()
        await example_streaming_with_error_handling()

    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("✅ 所有示例運行完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

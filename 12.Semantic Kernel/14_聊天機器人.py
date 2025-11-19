#!/usr/bin/env python3
"""
Semantic Kernel - 聊天機器人開發示例

本示例展示：
1. 基本聊天機器人
2. 客服機器人
3. 多輪對話管理
4. 個性化回覆
5. 意圖識別
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

try:
    import semantic_kernel as sk
    from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
    from semantic_kernel.contents import ChatHistory
except ImportError:
    print("❌ 請安裝 Semantic Kernel:")
    print("   pip install semantic-kernel")
    exit(1)


async def example_basic_chatbot():
    """示例 1: 基本聊天機器人"""
    print("\n" + "=" * 60)
    print("示例 1: 基本聊天機器人")
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
        """你是一個友善的AI助手。
        - 回答要簡潔明瞭
        - 保持禮貌和專業
        - 如果不知道答案，誠實地說出來"""
    )

    print("🤖 聊天機器人已啟動！\n")

    # 模擬對話
    messages = [
        "你好！",
        "今天天氣怎麼樣？",
        "你能幫我什麼？",
        "謝謝你！",
    ]

    for msg in messages:
        print(f"👤 用戶: {msg}")

        chat_history.add_user_message(msg)

        response = await service.get_chat_message_content(
            chat_history=chat_history, settings=None
        )

        chat_history.add_message(response)
        print(f"🤖 機器人: {response.content}\n")


async def example_customer_service_bot():
    """示例 2: 客服機器人"""
    print("\n" + "=" * 60)
    print("示例 2: 客服機器人")
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
        """你是 ABC 公司的客服機器人。

公司信息：
- 營業時間：週一至週五 9:00-18:00
- 客服電話：0800-123-456
- Email：support@abc.com
- 退貨政策：30天內可無條件退貨

你的職責：
1. 回答產品相關問題
2. 處理訂單查詢
3. 協助退換貨
4. 收集客戶反饋

保持專業、友善、有幫助的態度。"""
    )

    print("🎧 客服機器人已啟動！\n")

    # 模擬客服對話
    conversations = [
        "我想查詢訂單狀態",
        "訂單號是 #12345",
        "我想退貨，怎麼辦理？",
        "你們的營業時間是？",
    ]

    for msg in conversations:
        print(f"👤 客戶: {msg}")

        chat_history.add_user_message(msg)

        response = await service.get_chat_message_content(
            chat_history=chat_history, settings=None
        )

        chat_history.add_message(response)
        print(f"🤖 客服: {response.content}\n")


async def example_context_aware_chatbot():
    """示例 3: 上下文感知聊天機器人"""
    print("\n" + "=" * 60)
    print("示例 3: 上下文感知聊天機器人")
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

    # 用戶檔案
    user_profile = {
        "name": "張小明",
        "age": 28,
        "interests": ["編程", "閱讀", "旅行"],
        "occupation": "軟件工程師",
    }

    chat_history = ChatHistory()
    chat_history.add_system_message(
        f"""你是個性化助手，為用戶提供定制化服務。

用戶檔案：
- 姓名：{user_profile['name']}
- 年齡：{user_profile['age']}
- 興趣：{', '.join(user_profile['interests'])}
- 職業：{user_profile['occupation']}

根據用戶檔案提供個性化建議和回答。"""
    )

    print(f"👤 用戶檔案: {user_profile['name']}, {user_profile['occupation']}\n")

    # 個性化對話
    messages = [
        "推薦一些適合我的書",
        "週末有什麼活動建議？",
        "我想學習新技能",
    ]

    for msg in messages:
        print(f"👤 {user_profile['name']}: {msg}")

        chat_history.add_user_message(msg)

        response = await service.get_chat_message_content(
            chat_history=chat_history, settings=None
        )

        chat_history.add_message(response)
        print(f"🤖 助手: {response.content}\n")


async def example_intent_detection():
    """示例 4: 意圖識別聊天機器人"""
    print("\n" + "=" * 60)
    print("示例 4: 意圖識別聊天機器人")
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

    # 意圖識別提示
    intent_prompt = """
    識別用戶消息的意圖，並分類為以下之一：
    - greeting（問候）
    - question（詢問）
    - complaint（投訴）
    - thanks（感謝）
    - goodbye（告別）
    - other（其他）

    用戶消息：{{$message}}

    只返回意圖類別：
    """

    intent_function = kernel.add_function(
        function_name="detect_intent",
        plugin_name="NLU",
        prompt=intent_prompt,
        description="識別用戶意圖",
    )

    # 測試消息
    test_messages = [
        "你好！",
        "你們的產品質量太差了！",
        "請問你們支持貨到付款嗎？",
        "非常感謝你的幫助！",
        "再見",
    ]

    for msg in test_messages:
        print(f"💬 消息: {msg}")

        # 識別意圖
        intent = await kernel.invoke(intent_function, message=msg)
        intent_type = str(intent).strip()

        print(f"🎯 意圖: {intent_type}")

        # 根據意圖生成回覆
        chat_history = ChatHistory()

        if "greeting" in intent_type.lower():
            system_msg = "用友善的方式問候用戶"
        elif "complaint" in intent_type.lower():
            system_msg = "表達歉意並提供解決方案"
        elif "question" in intent_type.lower():
            system_msg = "專業地回答用戶問題"
        elif "thanks" in intent_type.lower():
            system_msg = "禮貌地回應感謝"
        elif "goodbye" in intent_type.lower():
            system_msg = "友善地道別"
        else:
            system_msg = "提供有幫助的回應"

        chat_history.add_system_message(system_msg)
        chat_history.add_user_message(msg)

        response = await service.get_chat_message_content(
            chat_history=chat_history, settings=None
        )

        print(f"🤖 回覆: {response.content}\n")


async def example_multilingual_chatbot():
    """示例 5: 多語言聊天機器人"""
    print("\n" + "=" * 60)
    print("示例 5: 多語言聊天機器人")
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
        """你是一個多語言AI助手。
        - 自動檢測用戶使用的語言
        - 用相同的語言回覆用戶
        - 支持中文、英文、日文、韓文等多種語言"""
    )

    print("🌍 多語言機器人已啟動！\n")

    # 多語言對話
    multilingual_messages = [
        ("繁體中文", "你好，請介紹一下你自己"),
        ("English", "What services do you provide?"),
        ("日本語", "ありがとうございます"),
        ("한국어", "안녕하세요"),
    ]

    for lang, msg in multilingual_messages:
        print(f"👤 用戶 ({lang}): {msg}")

        chat_history.add_user_message(msg)

        response = await service.get_chat_message_content(
            chat_history=chat_history, settings=None
        )

        chat_history.add_message(response)
        print(f"🤖 機器人: {response.content}\n")


async def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("🚀 Semantic Kernel - 聊天機器人開發示例")
    print("=" * 60)

    try:
        await example_basic_chatbot()
        await example_customer_service_bot()
        await example_context_aware_chatbot()
        await example_intent_detection()
        await example_multilingual_chatbot()

    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("✅ 所有示例運行完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

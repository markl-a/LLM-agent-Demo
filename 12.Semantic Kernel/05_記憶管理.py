#!/usr/bin/env python3
"""
Semantic Kernel - 記憶管理示例

本示例展示：
1. 對話歷史管理
2. 語義記憶
3. 長期記憶存儲
4. 記憶檢索和搜索
5. 上下文窗口管理
"""

import asyncio
import os
from dotenv import load_dotenv
from typing import List

load_dotenv()

try:
    import semantic_kernel as sk
    from semantic_kernel.connectors.ai.open_ai import (
        OpenAIChatCompletion,
        OpenAITextEmbedding,
    )
    from semantic_kernel.contents import ChatHistory
    from semantic_kernel.memory import SemanticTextMemory, VolatileMemoryStore
except ImportError:
    print("❌ 請安裝 Semantic Kernel:")
    print("   pip install semantic-kernel")
    exit(1)


async def example_chat_history():
    """示例 1: 對話歷史管理"""
    print("\n" + "=" * 60)
    print("示例 1: 對話歷史管理")
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

    # 創建對話歷史
    chat_history = ChatHistory()
    chat_history.add_system_message(
        "你是一個友善的助手，會記住之前的對話內容。"
    )

    print("✅ 對話系統啟動\n")

    # 模擬多輪對話
    conversations = [
        "我叫王小明，今年25歲",
        "我在台北工作，是一名軟件工程師",
        "請問你還記得我叫什麼名字嗎？",
        "我在哪裡工作？",
        "我的職業是什麼？",
    ]

    for user_msg in conversations:
        print(f"💬 用戶: {user_msg}")

        chat_history.add_user_message(user_msg)

        response = await service.get_chat_message_content(
            chat_history=chat_history, settings=None
        )

        chat_history.add_message(response)
        print(f"🤖 助手: {response.content}\n")

    print(f"📊 對話歷史長度: {len(chat_history.messages)} 條消息")


async def example_semantic_memory():
    """示例 2: 語義記憶"""
    print("\n" + "=" * 60)
    print("示例 2: 語義記憶")
    print("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  未設置 OPENAI_API_KEY")
        return

    kernel = sk.Kernel()

    # 添加嵌入服務
    embedding_service = OpenAITextEmbedding(
        service_id="text-embedding",
        ai_model_id="text-embedding-3-small",
        api_key=api_key,
    )
    kernel.add_service(embedding_service)

    # 創建語義記憶
    memory_store = VolatileMemoryStore()
    memory = SemanticTextMemory(storage=memory_store, embeddings_generator=embedding_service)

    # 存儲一些事實
    facts = [
        "Python 是一種高級編程語言，由 Guido van Rossum 創建於 1991 年。",
        "機器學習是人工智能的一個分支，讓計算機能從數據中學習。",
        "深度學習使用神經網絡來處理複雜的模式識別任務。",
        "自然語言處理（NLP）幫助計算機理解和生成人類語言。",
        "強化學習通過獎勵和懲罰來訓練 AI 代理。",
    ]

    print("💾 存儲事實到語義記憶...")
    collection = "ai_knowledge"

    for i, fact in enumerate(facts):
        await memory.save_information(
            collection=collection, id=f"fact_{i}", text=fact
        )
        print(f"  ✓ 已存儲: {fact[:50]}...")

    print("\n🔍 查詢語義記憶...")

    queries = [
        "Python 是誰創建的？",
        "什麼是機器學習？",
        "神經網絡用於什麼？",
    ]

    for query in queries:
        print(f"\n❓ 查詢: {query}")

        results = await memory.search(
            collection=collection, query=query, limit=2, min_relevance_score=0.5
        )

        for i, result in enumerate(results):
            print(f"  📄 結果 {i + 1} (相關度: {result.relevance:.2f})")
            print(f"     {result.text}")


async def example_memory_with_chat():
    """示例 3: 結合記憶的對話"""
    print("\n" + "=" * 60)
    print("示例 3: 結合記憶的對話")
    print("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  未設置 OPENAI_API_KEY")
        return

    kernel = sk.Kernel()

    # 添加服務
    chat_service = OpenAIChatCompletion(
        service_id="chat-gpt",
        ai_model_id="gpt-4o-mini",
        api_key=api_key,
    )
    embedding_service = OpenAITextEmbedding(
        service_id="text-embedding",
        ai_model_id="text-embedding-3-small",
        api_key=api_key,
    )

    kernel.add_service(chat_service)
    kernel.add_service(embedding_service)

    # 創建記憶
    memory_store = VolatileMemoryStore()
    memory = SemanticTextMemory(storage=memory_store, embeddings_generator=embedding_service)

    # 存儲用戶信息
    print("💾 存儲用戶信息...")
    user_info = [
        "用戶名: 張三",
        "年齡: 30 歲",
        "職業: 數據科學家",
        "興趣: 機器學習、閱讀、登山",
        "居住地: 台北",
        "公司: ABC 科技公司",
    ]

    collection = "user_profile"
    for i, info in enumerate(user_info):
        await memory.save_information(
            collection=collection, id=f"info_{i}", text=info
        )

    print("✅ 用戶信息已存儲\n")

    # 對話時查詢相關記憶
    chat_history = ChatHistory()
    chat_history.add_system_message(
        "你是一個個性化助手，可以根據用戶信息提供定制化回答。"
    )

    questions = [
        "我的職業是什麼？",
        "推薦一些適合我的活動",
        "我住在哪裡？",
    ]

    for question in questions:
        print(f"💬 用戶: {question}")

        # 從記憶中檢索相關信息
        relevant_memories = await memory.search(
            collection=collection, query=question, limit=3, min_relevance_score=0.3
        )

        # 構建上下文
        context = "相關用戶信息:\n"
        for mem in relevant_memories:
            context += f"- {mem.text}\n"

        # 添加上下文到提示
        prompt = f"{context}\n用戶問題: {question}\n\n請根據上述信息回答："

        chat_history.add_user_message(prompt)

        response = await chat_service.get_chat_message_content(
            chat_history=chat_history, settings=None
        )

        print(f"🤖 助手: {response.content}\n")

        # 清理歷史以節省 token
        chat_history = ChatHistory()
        chat_history.add_system_message(
            "你是一個個性化助手，可以根據用戶信息提供定制化回答。"
        )


async def example_context_window_management():
    """示例 4: 上下文窗口管理"""
    print("\n" + "=" * 60)
    print("示例 4: 上下文窗口管理")
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
    chat_history.add_system_message("你是一個助手。")

    max_history_messages = 6  # 保留最近的 6 條消息

    print(f"✅ 上下文窗口大小: {max_history_messages} 條消息\n")

    # 模擬長對話
    for i in range(10):
        user_msg = f"這是第 {i + 1} 條消息"
        print(f"💬 用戶: {user_msg}")

        chat_history.add_user_message(user_msg)

        response = await service.get_chat_message_content(
            chat_history=chat_history, settings=None
        )

        chat_history.add_message(response)
        print(f"🤖 助手: {response.content}")

        # 管理上下文窗口 - 保留系統消息和最近的 N 條消息
        if len(chat_history.messages) > max_history_messages + 1:  # +1 for system message
            # 保留系統消息
            system_msg = chat_history.messages[0]
            # 保留最近的消息
            recent_msgs = chat_history.messages[-(max_history_messages):]

            # 重建歷史
            chat_history = ChatHistory()
            chat_history.messages.append(system_msg)
            chat_history.messages.extend(recent_msgs)

            print(f"  🗑️  修剪歷史，保留最近 {max_history_messages} 條")

        print(f"  📊 當前歷史長度: {len(chat_history.messages)} 條\n")


async def example_persistent_memory():
    """示例 5: 持久化記憶（模擬）"""
    print("\n" + "=" * 60)
    print("示例 5: 持久化記憶（模擬）")
    print("=" * 60)

    print("💾 模擬持久化記憶系統...")

    # 模擬用戶偏好存儲
    user_preferences = {
        "language": "繁體中文",
        "response_style": "簡潔",
        "topics_of_interest": ["AI", "編程", "科技"],
        "conversation_history": [],
    }

    print("\n📋 用戶偏好:")
    for key, value in user_preferences.items():
        if key != "conversation_history":
            print(f"  - {key}: {value}")

    # 模擬對話並記錄
    conversations = [
        "介紹一下最新的 AI 技術",
        "Python 和 JavaScript 哪個更適合初學者？",
    ]

    print("\n💬 開始對話...")
    for conv in conversations:
        print(f"\n用戶: {conv}")

        # 記錄到歷史
        user_preferences["conversation_history"].append({
            "role": "user",
            "content": conv,
        })

        # 模擬回應
        response = f"根據您對 {', '.join(user_preferences['topics_of_interest'])} 的興趣，這裡是{user_preferences['response_style']}的回答..."

        print(f"助手: {response}")

        user_preferences["conversation_history"].append({
            "role": "assistant",
            "content": response,
        })

    print(f"\n📊 已記錄 {len(user_preferences['conversation_history'])} 條對話")
    print("💡 在實際應用中，可以將這些數據存儲到數據庫或文件系統")


async def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("🚀 Semantic Kernel - 記憶管理示例")
    print("=" * 60)

    try:
        await example_chat_history()
        await example_semantic_memory()
        await example_memory_with_chat()
        await example_context_window_management()
        await example_persistent_memory()

    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("✅ 所有示例運行完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

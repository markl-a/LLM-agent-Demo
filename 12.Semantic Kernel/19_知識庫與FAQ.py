#!/usr/bin/env python3
"""
Semantic Kernel - 知識庫與 FAQ 系統示例

本示例展示：
1. 知識庫構建
2. FAQ 自動回答
3. 知識檢索
4. 相似問題匹配
5. 知識更新
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

try:
    import semantic_kernel as sk
    from semantic_kernel.connectors.ai.open_ai import (
        OpenAIChatCompletion,
        OpenAITextEmbedding,
    )
    from semantic_kernel.memory import SemanticTextMemory, VolatileMemoryStore
    from semantic_kernel.contents import ChatHistory
except ImportError:
    print("❌ 請安裝 Semantic Kernel:")
    print("   pip install semantic-kernel")
    exit(1)


async def example_knowledge_base_build():
    """示例 1: 知識庫構建"""
    print("\n" + "=" * 60)
    print("示例 1: 知識庫構建")
    print("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  未設置 OPENAI_API_KEY")
        return

    kernel = sk.Kernel()

    embedding_service = OpenAITextEmbedding(
        service_id="text-embedding",
        ai_model_id="text-embedding-3-small",
        api_key=api_key,
    )
    kernel.add_service(embedding_service)

    memory_store = VolatileMemoryStore()
    memory = SemanticTextMemory(storage=memory_store, embeddings_generator=embedding_service)

    # 構建產品知識庫
    product_knowledge = [
        {
            "category": "產品功能",
            "question": "產品支持哪些操作系統？",
            "answer": "我們的產品支持 Windows 10/11、macOS 12 以上版本，以及主流 Linux 發行版（Ubuntu、Fedora）。",
        },
        {
            "category": "價格與方案",
            "question": "有哪些訂閱方案？",
            "answer": "我們提供三種方案：基礎版（$9.99/月）、專業版（$19.99/月）和企業版（$49.99/月）。所有方案都提供 14 天免費試用。",
        },
        {
            "category": "技術支持",
            "question": "如何獲得技術支持？",
            "answer": "您可以通過以下方式獲得支持：1) 在線文檔和教程 2) 郵件support@company.com 3) 即時聊天（工作時間）4) 電話支持（企業版）。",
        },
        {
            "category": "數據安全",
            "question": "數據如何保護？",
            "answer": "我們使用 AES-256 加密存儲數據，支持 SSO 單點登錄，通過 ISO 27001 和 SOC 2 認證，並提供完整的審計日誌。",
        },
        {
            "category": "集成",
            "question": "支持哪些第三方集成？",
            "answer": "支持 Slack、Microsoft Teams、Salesforce、Jira、GitHub、GitLab 等 100+ 種第三方工具的集成。",
        },
    ]

    print("💾 構建知識庫...\n")
    collection = "product_kb"

    for item in product_knowledge:
        kb_entry = f"分類：{item['category']}\n問題：{item['question']}\n答案：{item['answer']}"
        await memory.save_information(
            collection=collection,
            id=f"{item['category']}_{product_knowledge.index(item)}",
            text=kb_entry,
        )
        print(f"  ✓ 已添加: {item['category']} - {item['question']}")

    print(f"\n✅ 知識庫已構建，共 {len(product_knowledge)} 條記錄")
    return memory, collection


async def example_faq_auto_answer():
    """示例 2: FAQ 自動回答"""
    print("\n" + "=" * 60)
    print("示例 2: FAQ 自動回答")
    print("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  未設置 OPENAI_API_KEY")
        return

    # 構建知識庫
    memory, collection = await example_knowledge_base_build()

    kernel = sk.Kernel()
    chat_service = OpenAIChatCompletion(
        service_id="chat-gpt",
        ai_model_id="gpt-4o-mini",
        api_key=api_key,
    )
    kernel.add_service(chat_service)

    # FAQ 系統
    async def answer_faq(question: str):
        """FAQ 自動回答"""
        print(f"\n❓ 用戶問題: {question}")

        # 從知識庫檢索相關信息
        results = await memory.search(
            collection=collection,
            query=question,
            limit=2,
            min_relevance_score=0.5,
        )

        if not results:
            print("⚠️  未找到相關答案")
            return "抱歉，我沒有找到相關信息。請聯繫客服：support@company.com"

        # 使用檢索到的信息生成回答
        context = "\n\n".join([f"相關信息 {i+1}:\n{r.text}" for i, r in enumerate(results)])

        prompt = f"""基於以下知識庫信息回答用戶問題：

{context}

用戶問題：{question}

請提供：
1. 直接回答
2. 如果有補充信息，一併說明
3. 保持友好和專業的語氣

回答："""

        chat_history = ChatHistory()
        chat_history.add_user_message(prompt)

        response = await chat_service.get_chat_message_content(
            chat_history=chat_history, settings=None
        )

        print(f"🤖 自動回答: {response.content}")
        return response.content

    # 測試問題
    test_questions = [
        "你們支持 Mac 嗎？",
        "我想試用，有免費期嗎？",
        "如果遇到問題怎麼辦？",
        "你們的產品安全嗎？",
        "能不能和 Slack 整合？",
    ]

    for q in test_questions:
        await answer_faq(q)


async def example_similar_question_matching():
    """示例 3: 相似問題匹配"""
    print("\n" + "=" * 60)
    print("示例 3: 相似問題匹配")
    print("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  未設置 OPENAI_API_KEY")
        return

    kernel = sk.Kernel()

    embedding_service = OpenAITextEmbedding(
        service_id="text-embedding",
        ai_model_id="text-embedding-3-small",
        api_key=api_key,
    )
    kernel.add_service(embedding_service)

    memory_store = VolatileMemoryStore()
    memory = SemanticTextMemory(storage=memory_store, embeddings_generator=embedding_service)

    # 標準問題庫
    standard_questions = [
        "如何重置密碼？",
        "怎麼升級我的訂閱？",
        "支持哪些支付方式？",
        "如何導出數據？",
        "可以取消訂閱嗎？",
    ]

    print("💾 建立標準問題庫...\n")
    collection = "standard_questions"

    for i, q in enumerate(standard_questions):
        await memory.save_information(
            collection=collection,
            id=f"sq_{i}",
            text=q,
        )

    # 用戶問題（不同表述）
    user_questions = [
        "忘記密碼了怎麼辦？",  # 對應 "如何重置密碼？"
        "我想換更好的套餐",  # 對應 "怎麼升級我的訂閱？"
        "接受什麼付款方式？",  # 對應 "支持哪些支付方式？"
        "能把我的資料下載下來嗎？",  # 對應 "如何導出數據？"
        "不想用了可以退嗎？",  # 對應 "可以取消訂閱嗎？"
    ]

    print("🔍 匹配相似問題...\n")

    for uq in user_questions:
        print(f"用戶問題: {uq}")

        # 找到最相似的標準問題
        results = await memory.search(
            collection=collection,
            query=uq,
            limit=1,
            min_relevance_score=0.5,
        )

        if results:
            match = results[0]
            print(f"  ✓ 匹配到: {match.text} (相似度: {match.relevance:.2f})")
        else:
            print(f"  ✗ 未找到匹配")

        print()


async def example_knowledge_update():
    """示例 4: 知識更新"""
    print("\n" + "=" * 60)
    print("示例 4: 知識更新")
    print("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  未設置 OPENAI_API_KEY")
        return

    kernel = sk.Kernel()

    chat_service = OpenAIChatCompletion(
        service_id="chat-gpt",
        ai_model_id="gpt-4o-mini",
        api_key=api_key,
    )
    kernel.add_service(chat_service)

    # 識別需要更新的知識
    identify_prompt = """
    分析以下對話，判斷是否需要更新知識庫：

    {{$conversation}}

    判斷標準：
    - 是否有新信息
    - 是否有糾正錯誤
    - 是否有常見問題

    返回 JSON：
    {
        "needs_update": true/false,
        "reason": "原因",
        "suggested_entry": "建議的知識條目（如果需要更新）"
    }

    分析：
    """

    identify_function = kernel.add_function(
        function_name="identify_update",
        plugin_name="KBManagement",
        prompt=identify_prompt,
        description="識別知識更新",
    )

    # 測試對話
    conversations = [
        """用戶：你們支持比特幣支付嗎？
客服：是的，我們現在支持比特幣和以太坊支付。
用戶：太好了！""",
        """用戶：之前的答案說不支持 Linux，但我看到現在支持了？
客服：是的，從 2.0 版本開始我們已經支持 Linux 了。抱歉之前的信息過時了。""",
    ]

    for i, conv in enumerate(conversations, 1):
        print(f"\n📝 對話 {i}:")
        print(conv)

        result = await kernel.invoke(identify_function, conversation=conv)

        print(f"\n🔍 分析結果:\n{result}\n")
        print("-" * 60)


async def example_contextual_faq():
    """示例 5: 上下文感知 FAQ"""
    print("\n" + "=" * 60)
    print("示例 5: 上下文感知 FAQ")
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

    # 用戶上下文
    user_context = {
        "plan": "基礎版",
        "usage_duration": "3 個月",
        "feature_interest": "數據導出",
    }

    print(f"👤 用戶上下文: {user_context}\n")

    chat_history = ChatHistory()
    chat_history.add_system_message(
        f"""你是一個智能客服助手，根據用戶上下文提供個性化回答。

用戶信息：
- 當前方案：{user_context['plan']}
- 使用時長：{user_context['usage_duration']}
- 關注功能：{user_context['feature_interest']}

根據用戶情況提供針對性的回答和建議。"""
    )

    # 用戶問題
    questions = [
        "我可以導出數據嗎？",  # 基礎版可能有限制
        "我想要更多功能",  # 可能建議升級
        "你們的服務怎麼樣？",  # 根據使用時長提供個性化回答
    ]

    for q in questions:
        print(f"💬 用戶: {q}")

        chat_history.add_user_message(q)

        response = await service.get_chat_message_content(
            chat_history=chat_history, settings=None
        )

        chat_history.add_message(response)
        print(f"🤖 助手: {response.content}\n")


async def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("🚀 Semantic Kernel - 知識庫與 FAQ 系統示例")
    print("=" * 60)

    try:
        # await example_knowledge_base_build()  # 在 example_2 中調用
        await example_faq_auto_answer()
        await example_similar_question_matching()
        await example_knowledge_update()
        await example_contextual_faq()

    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("✅ 所有示例運行完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

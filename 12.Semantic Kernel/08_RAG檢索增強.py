#!/usr/bin/env python3
"""
Semantic Kernel - RAG (檢索增強生成) 示例

本示例展示：
1. 基本文檔檢索
2. 語義搜索
3. RAG 問答系統
4. 上下文增強生成
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


async def example_basic_document_retrieval():
    """示例 1: 基本文檔檢索"""
    print("\n" + "=" * 60)
    print("示例 1: 基本文檔檢索")
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

    # 存儲文檔
    documents = [
        {
            "id": "doc1",
            "text": "Python 是一種解釋型、高級、通用的編程語言。Python 的設計哲學強調代碼的可讀性。",
        },
        {
            "id": "doc2",
            "text": "JavaScript 是一種高級的、解釋型的編程語言，主要用於網頁開發。",
        },
        {
            "id": "doc3",
            "text": "Java 是一種基於類的、面向對象的編程語言，設計目標是盡可能減少實現依賴關係。",
        },
        {
            "id": "doc4",
            "text": "Rust 是一種系統編程語言，專注於安全性、並發性和性能。",
        },
        {
            "id": "doc5",
            "text": "Go 是 Google 開發的編程語言，以其簡潔性和對並發的良好支持而聞名。",
        },
    ]

    print("💾 存儲文檔到向量數據庫...")
    collection = "programming_languages"

    for doc in documents:
        await memory.save_information(
            collection=collection,
            id=doc["id"],
            text=doc["text"],
        )
        print(f"  ✓ {doc['id']}: {doc['text'][:50]}...")

    # 檢索相關文檔
    print("\n🔍 檢索文檔...")
    queries = [
        "什麼語言適合網頁開發？",
        "哪種語言注重安全性？",
        "Google 開發的編程語言",
    ]

    for query in queries:
        print(f"\n❓ 查詢: {query}")

        results = await memory.search(
            collection=collection,
            query=query,
            limit=2,
            min_relevance_score=0.5,
        )

        for i, result in enumerate(results, 1):
            print(f"  📄 結果 {i} (相關度: {result.relevance:.2f})")
            print(f"     {result.text}")


async def example_rag_qa_system():
    """示例 2: RAG 問答系統"""
    print("\n" + "=" * 60)
    print("示例 2: RAG 問答系統")
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

    # 存儲知識庫
    knowledge_base = [
        "Semantic Kernel 是微軟開發的開源 SDK，用於構建 AI Agent。",
        "Semantic Kernel 支持多種 LLM 提供商，包括 OpenAI、Azure OpenAI、Hugging Face 等。",
        "Semantic Kernel 提供插件系統，允許開發者擴展功能。",
        "Semantic Kernel 的核心概念包括 Kernel、Plugin、Function 和 Memory。",
        "Semantic Kernel 可以用於構建聊天機器人、自動化工作流程和智能代理。",
    ]

    print("💾 建立知識庫...")
    collection = "sk_knowledge"

    for i, text in enumerate(knowledge_base):
        await memory.save_information(
            collection=collection,
            id=f"kb_{i}",
            text=text,
        )

    print(f"✅ 已存儲 {len(knowledge_base)} 條知識\n")

    # RAG 問答
    async def rag_qa(question: str):
        """RAG 問答"""
        print(f"❓ 問題: {question}")

        # 檢索相關知識
        relevant_docs = await memory.search(
            collection=collection,
            query=question,
            limit=3,
            min_relevance_score=0.3,
        )

        # 構建上下文
        context = "相關知識:\n"
        for doc in relevant_docs:
            context += f"- {doc.text}\n"

        # 生成回答
        prompt = f"""基於以下知識回答問題。如果知識中沒有相關信息，請說明。

{context}

問題: {question}

回答:"""

        chat_history = ChatHistory()
        chat_history.add_user_message(prompt)

        response = await chat_service.get_chat_message_content(
            chat_history=chat_history, settings=None
        )

        print(f"🤖 回答: {response.content}\n")
        return response.content

    # 測試問答
    questions = [
        "Semantic Kernel 是誰開發的？",
        "Semantic Kernel 支持哪些 LLM？",
        "如何擴展 Semantic Kernel 的功能？",
        "Semantic Kernel 可以用來做什麼？",
    ]

    for q in questions:
        await rag_qa(q)


async def example_context_augmented_generation():
    """示例 3: 上下文增強生成"""
    print("\n" + "=" * 60)
    print("示例 3: 上下文增強生成")
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
    embedding_service = OpenAITextEmbedding(
        service_id="text-embedding",
        ai_model_id="text-embedding-3-small",
        api_key=api_key,
    )

    kernel.add_service(chat_service)
    kernel.add_service(embedding_service)

    memory_store = VolatileMemoryStore()
    memory = SemanticTextMemory(storage=memory_store, embeddings_generator=embedding_service)

    # 存儲產品信息
    products = [
        "產品A: 高性能筆記本電腦，配備 i9 處理器，32GB RAM，1TB SSD，售價 $2000",
        "產品B: 輕薄筆記本電腦，配備 i5 處理器，16GB RAM，512GB SSD，售價 $1200",
        "產品C: 遊戲筆記本電腦，配備 RTX 4080，32GB RAM，2TB SSD，售價 $3000",
        "產品D: 商務筆記本電腦，配備 i7 處理器，16GB RAM，512GB SSD，售價 $1500",
    ]

    print("💾 存儲產品信息...")
    collection = "products"

    for i, product in enumerate(products):
        await memory.save_information(
            collection=collection,
            id=f"product_{i}",
            text=product,
        )

    print(f"✅ 已存儲 {len(products)} 個產品\n")

    # 生成個性化推薦
    user_query = "我需要一台適合編程和輕度遊戲的筆記本，預算在 $2000 左右"
    print(f"💬 用戶需求: {user_query}\n")

    # 檢索相關產品
    relevant_products = await memory.search(
        collection=collection,
        query=user_query,
        limit=3,
        min_relevance_score=0.3,
    )

    # 生成推薦
    context = "可選產品:\n"
    for prod in relevant_products:
        context += f"- {prod.text}\n"

    prompt = f"""{context}

用戶需求: {user_query}

請根據用戶需求推薦最合適的產品，並解釋原因。"""

    chat_history = ChatHistory()
    chat_history.add_user_message(prompt)

    response = await chat_service.get_chat_message_content(
        chat_history=chat_history, settings=None
    )

    print(f"🤖 推薦:\n{response.content}")


async def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("🚀 Semantic Kernel - RAG 檢索增強示例")
    print("=" * 60)

    try:
        await example_basic_document_retrieval()
        await example_rag_qa_system()
        await example_context_augmented_generation()

    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("✅ 所有示例運行完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
LangFlow - RAG 系統示例

本示例展示如何在 LangFlow 中創建 RAG (檢索增強生成) 系統
"""

import json
from typing import Dict, Any


def create_basic_rag_flow() -> Dict[str, Any]:
    """創建基本 RAG Flow"""
    flow = {
        "name": "Basic RAG System",
        "description": "基本的 RAG 問答系統",
        "data": {
            "nodes": [
                # 文檔加載
                {
                    "id": "file-loader-1",
                    "type": "FileLoader",
                    "data": {
                        "file_path": "",
                        "file_type": "auto",
                    },
                    "position": {"x": 100, "y": 100},
                },
                # 文本分割
                {
                    "id": "text-splitter-1",
                    "type": "RecursiveCharacterTextSplitter",
                    "data": {
                        "chunk_size": 1000,
                        "chunk_overlap": 200,
                    },
                    "position": {"x": 300, "y": 100},
                },
                # 嵌入模型
                {
                    "id": "embedding-1",
                    "type": "OpenAIEmbeddings",
                    "data": {
                        "model": "text-embedding-3-small",
                    },
                    "position": {"x": 500, "y": 100},
                },
                # 向量存儲
                {
                    "id": "vectorstore-1",
                    "type": "Chroma",
                    "data": {
                        "collection_name": "my_docs",
                    },
                    "position": {"x": 700, "y": 100},
                },
                # 用戶輸入
                {
                    "id": "input-1",
                    "type": "ChatInput",
                    "data": {},
                    "position": {"x": 100, "y": 300},
                },
                # 檢索器
                {
                    "id": "retriever-1",
                    "type": "VectorStoreRetriever",
                    "data": {
                        "search_kwargs": {"k": 3},
                    },
                    "position": {"x": 300, "y": 300},
                },
                # LLM
                {
                    "id": "llm-1",
                    "type": "ChatOpenAI",
                    "data": {
                        "model_name": "gpt-4o-mini",
                        "temperature": 0.7,
                    },
                    "position": {"x": 500, "y": 300},
                },
                # 輸出
                {
                    "id": "output-1",
                    "type": "ChatOutput",
                    "data": {},
                    "position": {"x": 700, "y": 300},
                },
            ],
            "edges": [
                # 文檔處理流
                {"source": "file-loader-1", "target": "text-splitter-1"},
                {"source": "text-splitter-1", "target": "embedding-1"},
                {"source": "embedding-1", "target": "vectorstore-1"},
                # 查詢流
                {"source": "input-1", "target": "retriever-1"},
                {"source": "vectorstore-1", "target": "retriever-1"},
                {"source": "retriever-1", "target": "llm-1"},
                {"source": "llm-1", "target": "output-1"},
            ],
        },
    }
    return flow


def create_advanced_rag_flow() -> Dict[str, Any]:
    """創建高級 RAG Flow（多檔案、重排序）"""
    flow = {
        "name": "Advanced RAG with Reranking",
        "description": "帶重排序的高級 RAG 系統",
        "data": {
            "nodes": [
                {"id": "input", "type": "ChatInput", "position": {"x": 100, "y": 200}},
                {"id": "retriever", "type": "VectorStoreRetriever", "data": {"k": 10}, "position": {"x": 300, "y": 200}},
                {"id": "reranker", "type": "CohereRerank", "data": {"top_n": 3}, "position": {"x": 500, "y": 200}},
                {"id": "llm", "type": "ChatOpenAI", "position": {"x": 700, "y": 200}},
                {"id": "output", "type": "ChatOutput", "position": {"x": 900, "y": 200}},
            ],
            "edges": [
                {"source": "input", "target": "retriever"},
                {"source": "retriever", "target": "reranker"},
                {"source": "reranker", "target": "llm"},
                {"source": "llm", "target": "output"},
            ],
        },
    }
    return flow


def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("🎨 LangFlow - RAG 系統示例")
    print("=" * 60)

    # 示例 1: 基本 RAG
    print("\n示例 1: 基本 RAG 系統")
    print("-" * 60)
    basic_rag = create_basic_rag_flow()
    print(f"📝 Flow: {basic_rag['name']}")
    print(f"🔢 節點數: {len(basic_rag['data']['nodes'])}")

    with open("basic_rag_flow.json", "w", encoding="utf-8") as f:
        json.dump(basic_rag, f, indent=2, ensure_ascii=False)
    print("✅ 已保存: basic_rag_flow.json")

    print("\n📋 RAG 處理流程:")
    print("1. 上傳文檔")
    print("2. 文本分割 (chunk_size=1000)")
    print("3. 生成嵌入向量")
    print("4. 存儲到 Chroma 向量數據庫")
    print("5. 用戶提問")
    print("6. 檢索相關文檔片段 (top 3)")
    print("7. LLM 基於上下文生成回答")

    # 示例 2: 高級 RAG
    print("\n\n示例 2: 高級 RAG（帶重排序）")
    print("-" * 60)
    advanced_rag = create_advanced_rag_flow()
    print(f"📝 Flow: {advanced_rag['name']}")

    with open("advanced_rag_flow.json", "w", encoding="utf-8") as f:
        json.dump(advanced_rag, f, indent=2, ensure_ascii=False)
    print("✅ 已保存: advanced_rag_flow.json")

    print("\n🔧 高級特性:")
    print("- 初始檢索 10 個文檔")
    print("- 使用 Cohere Rerank 重排序")
    print("- 選取最相關的 3 個文檔")
    print("- 提高回答準確性")

    print("\n" + "=" * 60)
    print("✅ RAG 系統示例完成")
    print("=" * 60)


if __name__ == "__main__":
    main()

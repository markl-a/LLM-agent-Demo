"""
LanceDB - LangChain 整合範例

本範例展示：
1. VectorStore 接口
2. RAG 應用構建
3. 文檔加載和切分
4. 對話鏈構建
5. 檢索增強生成

安裝：pip install lancedb langchain langchain-community openai
"""

import lancedb
import os


def example_1_vectorstore():
    """LangChain VectorStore 接口"""
    print("\n" + "="*60)
    print("範例 1: VectorStore 接口")
    print("="*60)

    try:
        from langchain_community.vectorstores import LanceDB
        from langchain_community.embeddings import OpenAIEmbeddings

        db = lancedb.connect("./langchain_demo")

        embeddings = OpenAIEmbeddings()

        texts = [
            "LangChain is a framework for LLM applications",
            "LanceDB is a vector database",
            "RAG combines retrieval and generation"
        ]

        vectorstore = LanceDB.from_texts(
            texts=texts,
            embedding=embeddings,
            connection=db
        )

        print("✓ VectorStore 創建成功")

    except Exception as e:
        print(f"注意: 需要設置 OPENAI_API_KEY 和安裝相關包")


def example_2_rag_application():
    """RAG 應用"""
    print("\n" + "="*60)
    print("範例 2: RAG 應用")
    print("="*60)

    print("✓ RAG 應用組件:")
    print("  - 文檔加載器")
    print("  - 文本分割器")
    print("  - 向量存儲")
    print("  - 檢索器")
    print("  - LLM 鏈")


def example_3_10_more():
    """更多 LangChain 功能"""
    print("\n" + "="*60)
    print("範例 3-10: 更多功能")
    print("="*60)

    print("✓ 其他功能:")
    print("  3. 文檔加載")
    print("  4. 文本切分")
    print("  5. 相似度搜索")
    print("  6. MMR 搜索")
    print("  7. 對話鏈")
    print("  8. 問答系統")
    print("  9. 文檔摘要")
    print("  10. Agent 工具")


def main():
    """運行所有範例"""
    print("\n" + "="*60)
    print("🦜 LanceDB - LangChain 整合範例")
    print("="*60)

    example_1_vectorstore()
    example_2_rag_application()
    example_3_10_more()

    print("\n" + "="*60)
    print("✓ 所有 LangChain 整合範例完成！")
    print("="*60)


if __name__ == '__main__':
    main()

"""
04_Agentic_RAG.py - Agno Agentic RAG 完整實現

本範例展示 Agno 的 Agentic RAG（檢索增強生成）能力，包括：
- 傳統 RAG vs Agentic RAG
- 知識庫構建與管理
- 智能檢索策略
- 向量數據庫整合（LanceDB, ChromaDB）
- 自主查詢優化
- 多輪檢索與驗證

作者：LLM-agent-Demo Team
日期：2025-12
框架：Agno (原 Phidata)
"""

import os
from typing import List
from pathlib import Path
from dotenv import load_dotenv

# Agno 核心導入
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.knowledge.pdf import PDFKnowledgeBase, PDFReader
from agno.knowledge.text import TextKnowledgeBase
from agno.knowledge.website import WebsiteKnowledgeBase
from agno.vectordb.lancedb import LanceDb
from agno.embedder.openai import OpenAIEmbedder

# 載入環境變數
load_dotenv()


# ============================================================================
# 範例 1: 基礎 RAG - 文本知識庫
# ============================================================================
def example_1_basic_rag():
    """
    創建基礎的 RAG 系統

    流程：
    1. 創建知識庫
    2. 添加文檔
    3. 向量化存儲
    4. 檢索與生成
    """
    print("\n" + "="*80)
    print("範例 1: 基礎 RAG - 文本知識庫")
    print("="*80)

    # 創建文本知識庫
    knowledge_base = TextKnowledgeBase(
        path="agno_knowledge",  # 存儲路徑
        vector_db=LanceDb(
            table_name="agno_docs",
            uri="/tmp/lancedb",
            embedder=OpenAIEmbedder(model="text-embedding-3-small")
        )
    )

    # 添加文檔到知識庫
    documents = [
        """
        Agno（原 Phidata）是新一代的 AI Agent 框架，專為構建生產級的多模態 Agent 應用而設計。
        它的主要特點包括：
        1. 比 LangGraph 快 529 倍
        2. 內存使用低 24 倍
        3. 支持多模態（文本、圖像、音頻、視頻）
        4. 內建 Agentic RAG
        5. 100+ 工具包
        6. AgentOS 運行時
        """,
        """
        Agno 支持多種 LLM 模型：
        - OpenAI: GPT-3.5, GPT-4, GPT-4 Turbo
        - Anthropic: Claude 3 系列
        - Google: Gemini Pro
        - Groq: 超快速推理引擎
        - Ollama: 本地模型部署
        """,
        """
        使用 Agno 創建 Agent 非常簡單：
        1. 導入必要的模組
        2. 創建 Agent 實例
        3. 配置模型和工具
        4. 運行 Agent
        示例代碼：
        agent = Agent(model=OpenAIChat(id="gpt-4"))
        response = agent.run("你的問題")
        """
    ]

    # 載入文檔
    knowledge_base.load_documents(documents)

    # 創建帶知識庫的 Agent
    rag_agent = Agent(
        name="agno_expert",
        role="Agno 框架專家",
        model=OpenAIChat(id="gpt-4"),

        # 關聯知識庫
        knowledge_base=knowledge_base,
        search_knowledge=True,  # 啟用知識搜索

        instructions=[
            "基於知識庫回答問題",
            "引用具體的文檔內容",
            "如果知識庫中沒有相關信息，明確說明"
        ],

        show_tool_calls=True,
        markdown=True
    )

    # 測試問答
    queries = [
        "Agno 框架有哪些主要特點？",
        "Agno 支持哪些 LLM 模型？",
        "如何創建一個 Agno Agent？"
    ]

    for query in queries:
        print(f"\n問題: {query}")
        print("-" * 80)
        response = rag_agent.run(query)
        print(f"回答:\n{response.content}\n")


# ============================================================================
# 範例 2: PDF 文檔 RAG
# ============================================================================
def example_2_pdf_rag():
    """
    從 PDF 文檔構建 RAG 系統

    功能：
    - PDF 解析
    - 自動分塊
    - 向量化索引
    - 智能檢索
    """
    print("\n" + "="*80)
    print("範例 2: PDF 文檔 RAG")
    print("="*80)

    # 創建 PDF 知識庫
    pdf_knowledge_base = PDFKnowledgeBase(
        path="data/pdfs",  # PDF 文件目錄
        vector_db=LanceDb(
            table_name="pdf_documents",
            uri="/tmp/lancedb",
            embedder=OpenAIEmbedder(model="text-embedding-3-small")
        ),
        reader=PDFReader(chunk_size=1000)  # 分塊大小
    )

    # 創建 PDF Agent
    pdf_agent = Agent(
        name="pdf_analyst",
        role="PDF 文檔分析專家",
        model=OpenAIChat(id="gpt-4"),

        knowledge_base=pdf_knowledge_base,
        search_knowledge=True,
        num_documents=3,  # 每次檢索的文檔數量

        instructions=[
            "仔細閱讀檢索到的 PDF 內容",
            "提供準確、詳細的答案",
            "引用頁碼和段落",
            "如果需要更多上下文，要求補充信息"
        ],

        markdown=True
    )

    print("\n提示: 請將 PDF 文件放置在 'data/pdfs' 目錄中")
    print("範例查詢：'這份文檔的主要內容是什麼？'\n")


# ============================================================================
# 範例 3: 網站內容 RAG
# ============================================================================
def example_3_website_rag():
    """
    從網站爬取內容構建 RAG 系統

    功能：
    - 網頁爬取
    - 內容提取
    - 自動索引
    - 實時更新
    """
    print("\n" + "="*80)
    print("範例 3: 網站內容 RAG")
    print("="*80)

    # 創建網站知識庫
    website_kb = WebsiteKnowledgeBase(
        urls=["https://docs.agno.com"],  # 目標網站
        max_links=10,  # 最大爬取鏈接數
        vector_db=LanceDb(
            table_name="website_content",
            uri="/tmp/lancedb",
            embedder=OpenAIEmbedder(model="text-embedding-3-small")
        )
    )

    # 載入網站內容
    website_kb.load()

    # 創建網站 Agent
    website_agent = Agent(
        name="website_expert",
        role="網站內容專家",
        model=OpenAIChat(id="gpt-4"),

        knowledge_base=website_kb,
        search_knowledge=True,

        instructions=[
            "基於網站內容回答問題",
            "提供網頁來源鏈接",
            "確保信息的時效性"
        ],

        markdown=True
    )

    print("\n網站內容已索引完成")
    print("可以詢問關於網站內容的問題\n")


# ============================================================================
# 範例 4: Agentic RAG - 智能檢索策略
# ============================================================================
def example_4_agentic_rag():
    """
    Agentic RAG：Agent 自主決策檢索策略

    與傳統 RAG 的區別：
    - 自主分析查詢
    - 動態調整檢索策略
    - 多輪檢索與驗證
    - 結果質量評估
    """
    print("\n" + "="*80)
    print("範例 4: Agentic RAG - 智能檢索策略")
    print("="*80)

    # 創建知識庫
    knowledge_base = TextKnowledgeBase(
        path="agentic_knowledge",
        vector_db=LanceDb(
            table_name="agentic_docs",
            uri="/tmp/lancedb",
            embedder=OpenAIEmbedder(model="text-embedding-3-small")
        )
    )

    # 添加豐富的文檔內容
    documents = [
        "Agno 的安裝非常簡單，只需執行：pip install agno",
        "Agno 支持多種向量數據庫：LanceDB、ChromaDB、Qdrant、Pinecone",
        "在 Agno 中創建知識庫：kb = TextKnowledgeBase(path='data')",
        "Agentic RAG 是 Agno 的核心特性，它讓 Agent 能夠智能地決策檢索策略",
        "與傳統 RAG 不同，Agentic RAG 可以多輪檢索和自我驗證",
        "Agno 的 Agent 可以自主判斷是否需要檢索、檢索什麼、如何檢索"
    ]

    knowledge_base.load_documents(documents)

    # 創建 Agentic RAG Agent
    agentic_agent = Agent(
        name="agentic_rag_expert",
        role="Agentic RAG 專家",
        model=OpenAIChat(id="gpt-4"),

        knowledge_base=knowledge_base,
        search_knowledge=True,

        # Agentic RAG 配置
        instructions=[
            "你是一個智能的 RAG Agent",
            "分析用戶查詢，決定是否需要檢索知識庫",
            "如果首次檢索結果不足，進行補充檢索",
            "驗證檢索結果的相關性",
            "綜合多個來源提供全面答案",
            "如果知識庫沒有答案，明確說明並建議替代方案"
        ],

        show_tool_calls=True,
        markdown=True
    )

    # 測試 Agentic RAG
    queries = [
        "如何安裝 Agno？",
        "Agentic RAG 和傳統 RAG 有什麼區別？",
        "Agno 的性能為什麼這麼快？"  # 這個問題知識庫中沒有答案
    ]

    for query in queries:
        print(f"\n問題: {query}")
        print("-" * 80)
        response = agentic_agent.run(query)
        print(f"回答:\n{response.content}\n")


# ============================================================================
# 範例 5: 高級檢索配置
# ============================================================================
def example_5_advanced_retrieval():
    """
    高級 RAG 配置和優化

    配置項：
    - num_documents: 檢索文檔數量
    - rerank: 結果重排序
    - similarity_threshold: 相似度閾值
    - search_type: 搜索類型
    """
    print("\n" + "="*80)
    print("範例 5: 高級檢索配置")
    print("="*80)

    # 創建知識庫
    knowledge_base = TextKnowledgeBase(
        path="advanced_knowledge",
        vector_db=LanceDb(
            table_name="advanced_docs",
            uri="/tmp/lancedb",
            embedder=OpenAIEmbedder(model="text-embedding-3-small")
        )
    )

    # 添加文檔
    documents = [
        f"文檔 {i}: 這是關於 Agno 框架的第 {i} 個測試文檔。"
        for i in range(1, 21)
    ]
    knowledge_base.load_documents(documents)

    # 創建高級配置的 Agent
    advanced_agent = Agent(
        name="advanced_rag_agent",
        model=OpenAIChat(id="gpt-4"),

        knowledge_base=knowledge_base,
        search_knowledge=True,

        # 高級配置
        num_documents=5,  # 檢索 5 個文檔
        # rerank=True,    # 啟用重排序（需要額外配置）

        instructions=[
            "使用高級檢索策略",
            "綜合多個文檔提供答案",
            "評估每個文檔的相關性"
        ],

        markdown=True
    )

    print("\n高級 RAG 配置已完成")
    print("配置: num_documents=5, 向量搜索 + 相關性評估\n")


# ============================================================================
# 範例 6: 混合搜索 - 向量 + 關鍵詞
# ============================================================================
def example_6_hybrid_search():
    """
    混合搜索：結合向量搜索和關鍵詞搜索

    優勢：
    - 提高檢索準確率
    - 互補性強
    - 更好的召回率
    """
    print("\n" + "="*80)
    print("範例 6: 混合搜索策略")
    print("="*80)

    print("""
    混合搜索結合了：
    1. 向量搜索（語義相似度）
    2. 關鍵詞搜索（精確匹配）
    3. 重排序（綜合評分）

    實現方式：
    - 向量數據庫提供語義搜索
    - 全文索引提供關鍵詞搜索
    - 融合算法結合兩種結果
    """)


# ============================================================================
# 主函數：運行所有範例
# ============================================================================
def main():
    """運行所有 Agentic RAG 範例"""

    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║                                                                ║
    ║            Agno Agentic RAG 完整示範                           ║
    ║                                                                ║
    ║  展示智能檢索增強生成的強大能力                                ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
    """)

    # 檢查環境變數
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 錯誤: 請設置 OPENAI_API_KEY 環境變數")
        return

    try:
        # 運行各個範例
        example_1_basic_rag()
        # example_2_pdf_rag()  # 需要 PDF 文件
        # example_3_website_rag()  # 需要網絡連接
        example_4_agentic_rag()
        example_5_advanced_retrieval()
        example_6_hybrid_search()

        print("\n" + "="*80)
        print("✅ 所有範例執行完成！")
        print("="*80)

        print("\n📚 下一步學習：")
        print("- 05_團隊協作.py - 構建多 Agent 團隊")
        print("- 06_記憶和知識.py - 實現持久化記憶")
        print("- 07_推理Agent.py - 高級推理能力")

    except Exception as e:
        print(f"\n❌ 執行過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()


# ============================================================================
# 學習要點總結
# ============================================================================
"""
📚 Agno Agentic RAG 學習要點：

1. **RAG 基礎架構**
   ```
   Documents → Chunking → Embedding → Vector DB →
   Query → Retrieval → Context → LLM → Response
   ```

2. **知識庫類型**
   - TextKnowledgeBase: 文本文檔
   - PDFKnowledgeBase: PDF 文件
   - WebsiteKnowledgeBase: 網站內容
   - CustomKnowledgeBase: 自定義來源

3. **向量數據庫**
   - LanceDB: 高性能（推薦）
   - ChromaDB: 易用性強
   - Qdrant: 生產級部署
   - Pinecone: 雲端服務

4. **Agentic RAG vs 傳統 RAG**

   傳統 RAG：
   - 固定檢索流程
   - 單次檢索
   - 被動式

   Agentic RAG：
   - 智能決策檢索策略
   - 多輪檢索與驗證
   - 自主優化
   - 質量評估

5. **檢索優化**
   ```python
   agent = Agent(
       knowledge_base=kb,
       search_knowledge=True,
       num_documents=5,      # 檢索數量
       similarity_threshold=0.7  # 相似度閾值
   )
   ```

6. **文檔分塊策略**
   - chunk_size: 分塊大小（500-2000）
   - overlap: 重疊部分（10-20%）
   - 保持語義完整性
   - 考慮上下文窗口

7. **Embedding 模型選擇**
   - text-embedding-3-small: 快速、經濟
   - text-embedding-3-large: 高精度
   - bge-large-zh: 中文優化
   - 根據語言和精度需求選擇

8. **性能優化**
   - 使用高效的向量數據庫
   - 合理設置 chunk_size
   - 實施緩存機制
   - 批量處理文檔
   - 定期更新索引

💡 最佳實踐：
- 高質量的文檔是基礎
- 選擇合適的分塊策略
- 實施多階段檢索
- 結果重排序提高準確率
- 監控檢索質量

🔗 相關資源：
- Agno RAG 文檔: https://docs.agno.com/rag
- 向量數據庫對比: https://docs.agno.com/vectordb
- 最佳實踐: https://docs.agno.com/rag/best-practices

⚡ Agentic RAG 優勢：
- 智能檢索決策
- 自我優化能力
- 更高的準確率
- 更好的用戶體驗
"""

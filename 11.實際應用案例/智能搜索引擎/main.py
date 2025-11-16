"""
智能搜索引擎
結合傳統關鍵詞搜索和 AI 語義搜索的混合搜索系統

功能特點:
- 關鍵詞 + 語義搜索
- 搜索結果重排序（Reranking）
- 自動摘要生成
- 相關問題推薦
- 搜索歷史分析
"""

import os
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import numpy as np
from datetime import datetime

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


# ============ 數據模型 ============
@dataclass
class SearchResult:
    """搜索結果"""
    id: str
    title: str
    content: str
    url: str
    score: float  # 相關性分數
    source: str  # 來源：keyword, semantic, hybrid


@dataclass
class SearchResponse:
    """搜索響應"""
    query: str
    results: List[SearchResult]
    summary: str
    related_queries: List[str]
    search_time: float


# ============ 模擬文檔數據庫 ============
SAMPLE_DOCUMENTS = [
    {
        "id": "doc_1",
        "title": "Python 入門教程 - 基礎語法",
        "content": "Python 是一種直譯式、高階、通用的程式語言。Python 的設計哲學強調代碼的可讀性，並使用大量的縮排。Python 支援多種程式設計範式，包括物件導向、指令式、函數式和程序式編程。",
        "url": "https://example.com/python-basics"
    },
    {
        "id": "doc_2",
        "title": "Python 數據分析 - Pandas 教程",
        "content": "Pandas 是 Python 中最流行的數據分析庫。它提供了高性能、易於使用的數據結構和數據分析工具。Pandas 的核心數據結構是 DataFrame，這是一個二維表格型數據結構。",
        "url": "https://example.com/pandas-tutorial"
    },
    {
        "id": "doc_3",
        "title": "機器學習入門 - 監督式學習",
        "content": "監督式學習是機器學習的一種方法，通過標記的訓練數據來學習輸入到輸出的映射。常見的監督式學習算法包括線性回歸、邏輯回歸、決策樹、隨機森林和神經網絡。",
        "url": "https://example.com/ml-supervised"
    },
    {
        "id": "doc_4",
        "title": "深度學習 - 神經網絡基礎",
        "content": "神經網絡是深度學習的基礎。人工神經網絡由多個層組成，包括輸入層、隱藏層和輸出層。每一層都包含多個神經元，神經元之間通過權重連接。深度學習使用反向傳播算法來訓練神經網絡。",
        "url": "https://example.com/deep-learning"
    },
    {
        "id": "doc_5",
        "title": "自然語言處理 - Transformer 架構",
        "content": "Transformer 是一種基於注意力機制的神經網絡架構，在自然語言處理領域取得了巨大成功。BERT、GPT 等模型都基於 Transformer 架構。Transformer 使用自注意力機制來處理序列數據。",
        "url": "https://example.com/nlp-transformer"
    },
    {
        "id": "doc_6",
        "title": "LangChain 開發指南",
        "content": "LangChain 是一個用於開發 LLM 應用的框架。它提供了許多工具和組件，如提示模板、鏈、代理等。LangChain 支援多種 LLM 提供商，包括 OpenAI、Anthropic、Google 等。",
        "url": "https://example.com/langchain-guide"
    },
    {
        "id": "doc_7",
        "title": "RAG 技術詳解",
        "content": "RAG（Retrieval-Augmented Generation）是一種結合檢索和生成的技術。它首先從知識庫中檢索相關文檔，然後將檢索結果作為上下文提供給 LLM 生成回答。RAG 可以有效減少幻覺問題。",
        "url": "https://example.com/rag-explained"
    },
    {
        "id": "doc_8",
        "title": "向量數據庫比較 - Pinecone vs Chroma",
        "content": "向量數據庫用於存儲和檢索高維向量。Pinecone 是一個托管的向量數據庫服務，提供高性能和可擴展性。Chroma 是一個開源的向量數據庫，易於使用和部署。選擇取決於具體需求和預算。",
        "url": "https://example.com/vector-db-comparison"
    },
    {
        "id": "doc_9",
        "title": "提示工程最佳實踐",
        "content": "提示工程是與 LLM 有效交互的藝術。好的提示應該清晰、具體、包含上下文。常用技巧包括：零樣本提示、少樣本提示、思維鏈提示、角色扮演等。優化提示可以顯著提高 LLM 的輸出質量。",
        "url": "https://example.com/prompt-engineering"
    },
    {
        "id": "doc_10",
        "title": "AI Agent 設計模式",
        "content": "AI Agent 是能夠自主決策和行動的智能系統。常見的 Agent 設計模式包括：ReAct（推理-行動）、Plan-and-Execute（計劃-執行）、Reflection（反思）等。選擇合適的設計模式取決於任務複雜度。",
        "url": "https://example.com/ai-agent-patterns"
    },
]


# ============ 搜索引擎類 ============
class IntelligentSearchEngine:
    """智能搜索引擎"""

    def __init__(self):
        """初始化搜索引擎"""
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
        self.documents = SAMPLE_DOCUMENTS

        # 初始化向量存儲
        self._initialize_vector_store()

    def _initialize_vector_store(self):
        """初始化向量存儲"""
        print("📚 正在初始化向量存儲...")

        # 創建文檔對象
        docs = []
        for doc in self.documents:
            content = f"標題: {doc['title']}\n內容: {doc['content']}"
            docs.append(Document(
                page_content=content,
                metadata={
                    "id": doc["id"],
                    "title": doc["title"],
                    "url": doc["url"]
                }
            ))

        # 創建向量存儲
        self.vectorstore = FAISS.from_documents(docs, self.embeddings)
        print("✅ 向量存儲初始化完成")

    def keyword_search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """
        關鍵詞搜索（基於簡單的詞匹配）

        Args:
            query: 搜索查詢
            top_k: 返回結果數量

        Returns:
            搜索結果列表
        """
        results = []
        query_lower = query.lower()

        for doc in self.documents:
            # 計算簡單的匹配分數
            score = 0
            title_lower = doc["title"].lower()
            content_lower = doc["content"].lower()

            # 標題匹配權重更高
            if query_lower in title_lower:
                score += 2.0

            # 內容匹配
            if query_lower in content_lower:
                score += 1.0

            # 計算詞重疊
            query_words = set(query_lower.split())
            title_words = set(title_lower.split())
            content_words = set(content_lower.split())

            title_overlap = len(query_words & title_words) / max(len(query_words), 1)
            content_overlap = len(query_words & content_words) / max(len(query_words), 1)

            score += title_overlap * 1.5
            score += content_overlap * 0.5

            if score > 0:
                results.append(SearchResult(
                    id=doc["id"],
                    title=doc["title"],
                    content=doc["content"],
                    url=doc["url"],
                    score=score,
                    source="keyword"
                ))

        # 排序並返回 top_k
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]

    def semantic_search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """
        語義搜索（基於向量相似度）

        Args:
            query: 搜索查詢
            top_k: 返回結果數量

        Returns:
            搜索結果列表
        """
        # 使用向量存儲進行相似度搜索
        docs_and_scores = self.vectorstore.similarity_search_with_score(query, k=top_k)

        results = []
        for doc, score in docs_and_scores:
            # FAISS 的分數越小越相似，轉換為相似度分數
            similarity = 1 / (1 + score)

            # 找到原始文檔
            original_doc = next(
                (d for d in self.documents if d["id"] == doc.metadata["id"]),
                None
            )

            if original_doc:
                results.append(SearchResult(
                    id=original_doc["id"],
                    title=original_doc["title"],
                    content=original_doc["content"],
                    url=original_doc["url"],
                    score=similarity,
                    source="semantic"
                ))

        return results

    def hybrid_search(
        self,
        query: str,
        top_k: int = 5,
        keyword_weight: float = 0.3,
        semantic_weight: float = 0.7
    ) -> List[SearchResult]:
        """
        混合搜索（結合關鍵詞和語義搜索）

        Args:
            query: 搜索查詢
            top_k: 返回結果數量
            keyword_weight: 關鍵詞搜索權重
            semantic_weight: 語義搜索權重

        Returns:
            搜索結果列表
        """
        # 獲取關鍵詞搜索結果
        keyword_results = self.keyword_search(query, top_k=top_k * 2)

        # 獲取語義搜索結果
        semantic_results = self.semantic_search(query, top_k=top_k * 2)

        # 合併結果
        all_results = {}

        # 添加關鍵詞搜索結果
        for result in keyword_results:
            all_results[result.id] = result
            result.score *= keyword_weight

        # 合併語義搜索結果
        for result in semantic_results:
            if result.id in all_results:
                # 已存在，合併分數
                all_results[result.id].score += result.score * semantic_weight
                all_results[result.id].source = "hybrid"
            else:
                result.score *= semantic_weight
                all_results[result.id] = result

        # 轉換為列表並排序
        results = list(all_results.values())
        results.sort(key=lambda x: x.score, reverse=True)

        return results[:top_k]

    def rerank_results(self, query: str, results: List[SearchResult]) -> List[SearchResult]:
        """
        重排序搜索結果（使用 LLM）

        Args:
            query: 搜索查詢
            results: 初始搜索結果

        Returns:
            重排序後的結果
        """
        if not results:
            return results

        # 構建提示
        results_text = "\n\n".join([
            f"{i+1}. [{result.id}] {result.title}\n{result.content[:200]}..."
            for i, result in enumerate(results)
        ])

        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一個搜索結果排序專家。

            根據用戶查詢的相關性對以下搜索結果重新排序。
            只返回文檔ID的排序列表，用逗號分隔，不要其他說明。

            例如：doc_3, doc_1, doc_5"""),
            ("human", "查詢: {query}\n\n搜索結果:\n{results}\n\n請重新排序（只返回ID，逗號分隔）:")
        ])

        chain = prompt | self.llm | StrOutputParser()

        try:
            reranked_ids = chain.invoke({
                "query": query,
                "results": results_text
            }).strip().split(",")

            # 清理ID
            reranked_ids = [id.strip() for id in reranked_ids]

            # 根據新順序重排
            reranked = []
            for doc_id in reranked_ids:
                for result in results:
                    if result.id == doc_id:
                        reranked.append(result)
                        break

            # 添加任何遺漏的結果
            for result in results:
                if result not in reranked:
                    reranked.append(result)

            return reranked

        except Exception as e:
            print(f"重排序失敗: {e}，返回原始順序")
            return results

    def generate_summary(self, query: str, results: List[SearchResult]) -> str:
        """
        生成搜索結果摘要

        Args:
            query: 搜索查詢
            results: 搜索結果

        Returns:
            摘要文本
        """
        if not results:
            return "未找到相關結果。"

        # 合併結果內容
        context = "\n\n".join([
            f"來源 {i+1}: {result.title}\n{result.content}"
            for i, result in enumerate(results[:3])  # 只使用前3個結果
        ])

        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一個專業的內容摘要專家。

            基於以下搜索結果，為用戶查詢生成一個簡潔、信息豐富的摘要。

            要求：
            1. 直接回答用戶的查詢
            2. 整合多個來源的信息
            3. 保持簡潔（2-3 段）
            4. 使用友好的語氣
            """),
            ("human", "查詢: {query}\n\n搜索結果:\n{context}\n\n請生成摘要:")
        ])

        chain = prompt | self.llm | StrOutputParser()

        summary = chain.invoke({
            "query": query,
            "context": context
        })

        return summary

    def generate_related_queries(self, query: str) -> List[str]:
        """
        生成相關搜索建議

        Args:
            query: 原始查詢

        Returns:
            相關查詢列表
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一個搜索建議專家。

            基於用戶的搜索查詢，生成 3 個相關的搜索建議。

            要求：
            1. 建議應該相關但有所延伸
            2. 建議應該實用和有意義
            3. 每行一個建議
            4. 不要編號

            只返回建議，不要其他說明。"""),
            ("human", "原始查詢: {query}\n\n請生成相關搜索建議:")
        ])

        chain = prompt | self.llm | StrOutputParser()

        suggestions_text = chain.invoke({"query": query})

        # 解析建議
        suggestions = [
            s.strip()
            for s in suggestions_text.strip().split("\n")
            if s.strip()
        ]

        return suggestions[:3]

    def search(
        self,
        query: str,
        top_k: int = 5,
        use_rerank: bool = True
    ) -> SearchResponse:
        """
        執行完整搜索

        Args:
            query: 搜索查詢
            top_k: 返回結果數量
            use_rerank: 是否使用重排序

        Returns:
            搜索響應
        """
        start_time = datetime.now()

        print(f"\n{'='*60}")
        print(f"🔍 搜索查詢: {query}")
        print(f"{'='*60}\n")

        # 1. 混合搜索
        print("📊 執行混合搜索...")
        results = self.hybrid_search(query, top_k=top_k)

        # 2. 重排序（可選）
        if use_rerank and len(results) > 1:
            print("🔄 重排序結果...")
            results = self.rerank_results(query, results)

        # 3. 生成摘要
        print("📝 生成摘要...")
        summary = self.generate_summary(query, results)

        # 4. 生成相關查詢
        print("💡 生成相關查詢...")
        related_queries = self.generate_related_queries(query)

        # 計算搜索時間
        search_time = (datetime.now() - start_time).total_seconds()

        return SearchResponse(
            query=query,
            results=results,
            summary=summary,
            related_queries=related_queries,
            search_time=search_time
        )

    def display_results(self, response: SearchResponse):
        """
        顯示搜索結果

        Args:
            response: 搜索響應
        """
        print(f"\n{'='*60}")
        print(f"搜索時間: {response.search_time:.2f} 秒")
        print(f"{'='*60}\n")

        # 顯示摘要
        print("📋 摘要:")
        print("-" * 60)
        print(response.summary)
        print()

        # 顯示搜索結果
        print("📚 搜索結果:")
        print("-" * 60)
        for i, result in enumerate(response.results, 1):
            print(f"\n{i}. {result.title}")
            print(f"   相關性: {result.score:.3f} | 來源: {result.source}")
            print(f"   連結: {result.url}")
            print(f"   {result.content[:150]}...")

        # 顯示相關查詢
        if response.related_queries:
            print(f"\n\n💡 相關搜索:")
            print("-" * 60)
            for i, query in enumerate(response.related_queries, 1):
                print(f"{i}. {query}")

        print(f"\n{'='*60}\n")


# ============ 主程序 ============
def main():
    """主程序"""

    print("🚀 智能搜索引擎")
    print("=" * 60)

    # 初始化搜索引擎
    search_engine = IntelligentSearchEngine()

    print("\n輸入 'quit' 或 'exit' 結束搜索\n")

    while True:
        # 獲取用戶查詢
        query = input("🔍 請輸入搜索查詢: ").strip()

        if not query:
            continue

        if query.lower() in ['quit', 'exit', '退出']:
            print("\n感謝使用！👋")
            break

        # 執行搜索
        try:
            response = search_engine.search(query, top_k=5, use_rerank=True)
            search_engine.display_results(response)

        except Exception as e:
            print(f"\n❌ 搜索失敗: {str(e)}\n")


if __name__ == "__main__":
    # 檢查環境變數
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 錯誤: 請設置 OPENAI_API_KEY 環境變數")
        print("   export OPENAI_API_KEY='your-api-key'")
        exit(1)

    main()

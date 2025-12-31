"""
Julep 文檔處理和 RAG 示例

這個模塊展示了 Julep 平台的文檔處理和 RAG（檢索增強生成）功能。
包括文檔索引、向量存儲、語義檢索和上下文注入。

主要功能：
1. 文檔上傳和索引
2. 向量嵌入和存儲
3. 語義搜索和檢索
4. RAG 問答系統
5. 文檔分塊策略
6. 多文檔管理

作者：Julep 示例
日期：2025-12-31
"""

import os
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import hashlib
import math


class DocumentType(Enum):
    """文檔類型枚舉"""
    TEXT = "text"
    PDF = "pdf"
    MARKDOWN = "markdown"
    HTML = "html"
    CODE = "code"


@dataclass
class Document:
    """文檔類

    表示一個可被索引和檢索的文檔。
    """
    id: str
    title: str
    content: str
    doc_type: DocumentType
    metadata: Dict[str, Any]
    created_at: datetime
    embedding: Optional[List[float]] = None

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "type": self.doc_type.value,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "has_embedding": self.embedding is not None
        }

    def __repr__(self) -> str:
        return f"Document(id={self.id}, title={self.title})"


@dataclass
class DocumentChunk:
    """文檔分塊

    將大文檔分割成小塊以便處理。
    """
    chunk_id: str
    document_id: str
    content: str
    chunk_index: int
    start_pos: int
    end_pos: int
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def __repr__(self) -> str:
        return f"Chunk(doc={self.document_id}, index={self.chunk_index})"


class ChunkingStrategy:
    """文檔分塊策略

    定義如何將文檔分割成小塊。
    """

    @staticmethod
    def fixed_size(
        content: str,
        chunk_size: int = 500,
        overlap: int = 50
    ) -> List[Tuple[int, int, str]]:
        """固定大小分塊

        Args:
            content: 文檔內容
            chunk_size: 塊大小（字符數）
            overlap: 重疊大小

        Returns:
            (開始位置, 結束位置, 內容) 列表
        """
        chunks = []
        start = 0

        while start < len(content):
            end = min(start + chunk_size, len(content))
            chunk_content = content[start:end]
            chunks.append((start, end, chunk_content))
            start = end - overlap

        return chunks

    @staticmethod
    def sentence_based(content: str, max_sentences: int = 5) -> List[Tuple[int, int, str]]:
        """基於句子分塊

        Args:
            content: 文檔內容
            max_sentences: 每塊最大句子數

        Returns:
            分塊列表
        """
        # 簡單的句子分割（實際應用中應使用更複雜的 NLP 方法）
        sentences = content.replace('。', '。\n').replace('！', '！\n').replace('？', '？\n').split('\n')
        sentences = [s.strip() for s in sentences if s.strip()]

        chunks = []
        current_chunk = []
        start_pos = 0

        for sentence in sentences:
            current_chunk.append(sentence)

            if len(current_chunk) >= max_sentences:
                chunk_content = ''.join(current_chunk)
                end_pos = start_pos + len(chunk_content)
                chunks.append((start_pos, end_pos, chunk_content))

                start_pos = end_pos
                current_chunk = []

        # 處理剩餘句子
        if current_chunk:
            chunk_content = ''.join(current_chunk)
            end_pos = start_pos + len(chunk_content)
            chunks.append((start_pos, end_pos, chunk_content))

        return chunks

    @staticmethod
    def paragraph_based(content: str) -> List[Tuple[int, int, str]]:
        """基於段落分塊

        Args:
            content: 文檔內容

        Returns:
            分塊列表
        """
        paragraphs = content.split('\n\n')
        chunks = []
        current_pos = 0

        for para in paragraphs:
            if para.strip():
                start = current_pos
                end = start + len(para)
                chunks.append((start, end, para.strip()))
                current_pos = end + 2  # +2 for \n\n

        return chunks


class EmbeddingModel:
    """嵌入模型

    將文本轉換為向量嵌入。
    """

    def __init__(self, model_name: str = "text-embedding-ada-002", dimension: int = 1536):
        """初始化嵌入模型

        Args:
            model_name: 模型名稱
            dimension: 向量維度
        """
        self.model_name = model_name
        self.dimension = dimension

    def embed_text(self, text: str) -> List[float]:
        """將文本轉換為嵌入向量

        Args:
            text: 輸入文本

        Returns:
            嵌入向量
        """
        # 模擬嵌入生成（實際應用中應調用真實的嵌入 API）
        # 這裡使用簡單的哈希和歸一化來模擬
        hash_value = int(hashlib.md5(text.encode()).hexdigest(), 16)

        # 生成偽隨機向量
        embedding = []
        for i in range(self.dimension):
            value = math.sin(hash_value * (i + 1) / 1000.0)
            embedding.append(value)

        # 歸一化
        magnitude = math.sqrt(sum(x * x for x in embedding))
        embedding = [x / magnitude for x in embedding]

        return embedding

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """批量嵌入

        Args:
            texts: 文本列表

        Returns:
            嵌入向量列表
        """
        return [self.embed_text(text) for text in texts]


class VectorStore:
    """向量存儲

    存儲和檢索文檔的向量嵌入。
    """

    def __init__(self, dimension: int = 1536):
        """初始化向量存儲

        Args:
            dimension: 向量維度
        """
        self.dimension = dimension
        self.vectors: Dict[str, List[float]] = {}
        self.metadata: Dict[str, Dict[str, Any]] = {}

    def add_vector(self, id: str, vector: List[float], metadata: Optional[Dict] = None):
        """添加向量

        Args:
            id: 向量 ID
            vector: 向量數據
            metadata: 元數據
        """
        if len(vector) != self.dimension:
            raise ValueError(f"向量維度不匹配: 期望 {self.dimension}, 得到 {len(vector)}")

        self.vectors[id] = vector
        self.metadata[id] = metadata or {}

    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """計算餘弦相似度

        Args:
            vec1: 向量1
            vec2: 向量2

        Returns:
            相似度分數（0-1）
        """
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(x * x for x in vec1))
        magnitude2 = math.sqrt(sum(x * x for x in vec2))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        threshold: float = 0.0
    ) -> List[Tuple[str, float, Dict]]:
        """搜索最相似的向量

        Args:
            query_vector: 查詢向量
            top_k: 返回前 K 個結果
            threshold: 最小相似度閾值

        Returns:
            (ID, 相似度, 元數據) 列表
        """
        results = []

        for vec_id, vector in self.vectors.items():
            similarity = self.cosine_similarity(query_vector, vector)

            if similarity >= threshold:
                results.append((vec_id, similarity, self.metadata[vec_id]))

        # 按相似度排序
        results.sort(key=lambda x: x[1], reverse=True)

        return results[:top_k]

    def delete_vector(self, id: str):
        """刪除向量"""
        if id in self.vectors:
            del self.vectors[id]
            del self.metadata[id]

    def get_stats(self) -> Dict[str, Any]:
        """獲取統計信息"""
        return {
            "total_vectors": len(self.vectors),
            "dimension": self.dimension
        }


class DocumentStore:
    """文檔存儲

    管理文檔的完整生命週期。
    """

    def __init__(
        self,
        embedding_model: EmbeddingModel,
        vector_store: VectorStore,
        chunking_strategy: str = "fixed_size"
    ):
        """初始化文檔存儲

        Args:
            embedding_model: 嵌入模型
            vector_store: 向量存儲
            chunking_strategy: 分塊策略
        """
        self.embedding_model = embedding_model
        self.vector_store = vector_store
        self.chunking_strategy = chunking_strategy
        self.documents: Dict[str, Document] = {}
        self.chunks: Dict[str, DocumentChunk] = {}

    def add_document(
        self,
        title: str,
        content: str,
        doc_type: DocumentType = DocumentType.TEXT,
        metadata: Optional[Dict] = None
    ) -> Document:
        """添加文檔

        Args:
            title: 文檔標題
            content: 文檔內容
            doc_type: 文檔類型
            metadata: 元數據

        Returns:
            創建的文檔對象
        """
        # 生成文檔 ID
        doc_id = f"doc_{int(time.time())}_{hashlib.md5(title.encode()).hexdigest()[:8]}"

        # 創建文檔
        document = Document(
            id=doc_id,
            title=title,
            content=content,
            doc_type=doc_type,
            metadata=metadata or {},
            created_at=datetime.now()
        )

        # 生成文檔嵌入
        print(f"[INFO] 為文檔生成嵌入: {title}")
        document.embedding = self.embedding_model.embed_text(content[:500])  # 使用前500字符

        # 存儲文檔
        self.documents[doc_id] = document

        # 分塊處理
        self._chunk_and_index_document(document)

        print(f"[SUCCESS] 文檔已添加: {doc_id}")
        return document

    def _chunk_and_index_document(self, document: Document):
        """分塊並索引文檔

        Args:
            document: 文檔對象
        """
        print(f"[INFO] 分塊文檔: {document.title}")

        # 根據策略分塊
        if self.chunking_strategy == "fixed_size":
            chunk_data = ChunkingStrategy.fixed_size(document.content)
        elif self.chunking_strategy == "sentence":
            chunk_data = ChunkingStrategy.sentence_based(document.content)
        elif self.chunking_strategy == "paragraph":
            chunk_data = ChunkingStrategy.paragraph_based(document.content)
        else:
            chunk_data = ChunkingStrategy.fixed_size(document.content)

        # 創建並索引分塊
        for idx, (start, end, content) in enumerate(chunk_data):
            chunk_id = f"{document.id}_chunk_{idx}"

            # 創建分塊
            chunk = DocumentChunk(
                chunk_id=chunk_id,
                document_id=document.id,
                content=content,
                chunk_index=idx,
                start_pos=start,
                end_pos=end,
                metadata={
                    "doc_title": document.title,
                    "doc_type": document.doc_type.value
                }
            )

            # 生成嵌入
            chunk.embedding = self.embedding_model.embed_text(content)

            # 存儲分塊
            self.chunks[chunk_id] = chunk

            # 添加到向量存儲
            self.vector_store.add_vector(
                chunk_id,
                chunk.embedding,
                chunk.metadata
            )

        print(f"[INFO] 創建了 {len(chunk_data)} 個分塊")

    def search(
        self,
        query: str,
        top_k: int = 5,
        threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """搜索相關文檔

        Args:
            query: 查詢文本
            top_k: 返回數量
            threshold: 相似度閾值

        Returns:
            搜索結果列表
        """
        print(f"\n[SEARCH] 查詢: {query}")

        # 生成查詢嵌入
        query_embedding = self.embedding_model.embed_text(query)

        # 向量搜索
        vector_results = self.vector_store.search(
            query_embedding,
            top_k=top_k,
            threshold=threshold
        )

        # 整理結果
        results = []
        for chunk_id, similarity, metadata in vector_results:
            chunk = self.chunks.get(chunk_id)
            if chunk:
                results.append({
                    "chunk_id": chunk_id,
                    "document_id": chunk.document_id,
                    "content": chunk.content,
                    "similarity": similarity,
                    "metadata": metadata
                })

        print(f"[INFO] 找到 {len(results)} 個相關結果")
        return results

    def get_document(self, doc_id: str) -> Optional[Document]:
        """獲取文檔"""
        return self.documents.get(doc_id)

    def list_documents(self) -> List[Document]:
        """列出所有文檔"""
        return list(self.documents.values())


class RAGSystem:
    """RAG（檢索增強生成）系統

    結合文檔檢索和 LLM 生成的完整系統。
    """

    def __init__(self, document_store: DocumentStore):
        """初始化 RAG 系統

        Args:
            document_store: 文檔存儲
        """
        self.document_store = document_store

    def answer_question(
        self,
        question: str,
        top_k: int = 3,
        include_sources: bool = True
    ) -> Dict[str, Any]:
        """回答問題

        Args:
            question: 用戶問題
            top_k: 檢索文檔數量
            include_sources: 是否包含來源

        Returns:
            回答結果
        """
        print(f"\n{'='*60}")
        print(f"RAG 問答")
        print(f"{'='*60}")
        print(f"問題: {question}")

        # 檢索相關文檔
        relevant_docs = self.document_store.search(
            query=question,
            top_k=top_k,
            threshold=0.3
        )

        if not relevant_docs:
            return {
                "question": question,
                "answer": "抱歉，我在知識庫中沒有找到相關信息。",
                "sources": []
            }

        # 構建上下文
        context_parts = []
        sources = []

        for i, doc in enumerate(relevant_docs, 1):
            context_parts.append(f"文檔片段 {i}:\n{doc['content']}\n")
            sources.append({
                "document_id": doc["document_id"],
                "similarity": doc["similarity"],
                "content_preview": doc["content"][:100] + "..."
            })

        context = "\n".join(context_parts)

        # 生成回答（模擬 LLM 調用）
        print(f"\n[INFO] 基於 {len(relevant_docs)} 個相關片段生成回答")
        time.sleep(0.5)

        # 模擬回答
        answer = f"基於檢索到的文檔，{question}的回答是：[這裡是基於上下文生成的詳細回答]"

        result = {
            "question": question,
            "answer": answer,
            "context_used": context,
            "num_sources": len(sources)
        }

        if include_sources:
            result["sources"] = sources

        print(f"\n回答: {answer}")
        print(f"使用了 {len(sources)} 個來源")

        return result

    def batch_qa(self, questions: List[str]) -> List[Dict[str, Any]]:
        """批量問答

        Args:
            questions: 問題列表

        Returns:
            回答列表
        """
        results = []
        for question in questions:
            result = self.answer_question(question)
            results.append(result)
        return results


def demo_document_indexing():
    """文檔索引示例"""
    print("\n" + "="*60)
    print("示例 1: 文檔索引")
    print("="*60)

    # 初始化組件
    embedding_model = EmbeddingModel()
    vector_store = VectorStore()
    doc_store = DocumentStore(embedding_model, vector_store, chunking_strategy="fixed_size")

    # 添加示例文檔
    docs = [
        {
            "title": "Python 入門指南",
            "content": "Python 是一種高級編程語言。它簡單易學，適合初學者。Python 支持多種編程範式，包括面向對象、函數式和過程式編程。"
        },
        {
            "title": "機器學習基礎",
            "content": "機器學習是人工智能的一個分支。它使用算法從數據中學習模式。常見的機器學習算法包括線性回歸、決策樹和神經網絡。"
        },
        {
            "title": "Web 開發教程",
            "content": "Web 開發包括前端和後端開發。前端使用 HTML、CSS 和 JavaScript。後端可以使用 Python、Node.js 或其他語言。"
        }
    ]

    for doc_data in docs:
        doc_store.add_document(
            title=doc_data["title"],
            content=doc_data["content"],
            doc_type=DocumentType.TEXT
        )

    # 顯示統計
    print(f"\n文檔存儲統計:")
    print(f"  總文檔數: {len(doc_store.documents)}")
    print(f"  總分塊數: {len(doc_store.chunks)}")
    print(f"  向量存儲: {doc_store.vector_store.get_stats()}")


def demo_semantic_search():
    """語義搜索示例"""
    print("\n" + "="*60)
    print("示例 2: 語義搜索")
    print("="*60)

    # 初始化
    embedding_model = EmbeddingModel()
    vector_store = VectorStore()
    doc_store = DocumentStore(embedding_model, vector_store)

    # 添加技術文檔
    doc_store.add_document(
        "數據庫設計原則",
        "數據庫設計需要遵循規範化原則。第一範式要求數據原子性，第二範式消除部分依賴，第三範式消除傳遞依賴。良好的數據庫設計能提高查詢效率。",
        DocumentType.TEXT
    )

    doc_store.add_document(
        "API 設計最佳實踐",
        "RESTful API 設計應遵循統一接口原則。使用標準 HTTP 方法，資源命名清晰，返回適當的狀態碼。API 版本控制也很重要。",
        DocumentType.TEXT
    )

    # 執行搜索
    queries = [
        "如何設計數據庫？",
        "API 開發的建議",
        "什麼是範式？"
    ]

    for query in queries:
        results = doc_store.search(query, top_k=2)
        print(f"\n查詢: {query}")
        print(f"結果數: {len(results)}")
        for i, result in enumerate(results, 1):
            print(f"\n  結果 {i}:")
            print(f"    相似度: {result['similarity']:.3f}")
            print(f"    內容: {result['content'][:80]}...")


def demo_rag_qa():
    """RAG 問答示例"""
    print("\n" + "="*60)
    print("示例 3: RAG 問答系統")
    print("="*60)

    # 初始化系統
    embedding_model = EmbeddingModel()
    vector_store = VectorStore()
    doc_store = DocumentStore(embedding_model, vector_store)

    # 添加知識庫
    knowledge_base = [
        ("公司產品介紹", "我們的主要產品是智能客服系統。它使用先進的 NLP 技術，可以自動回答客戶問題，提高客服效率。系統支持多語言，24/7 運行。"),
        ("定價方案", "我們提供三種定價方案：基礎版每月 99 元，專業版每月 299 元，企業版需要定制報價。所有方案都包含 14 天免費試用。"),
        ("技術支持", "我們提供全天候技術支持。基礎版用戶可以通過郵件聯繫，專業版和企業版用戶可以獲得電話支持和專屬客戶經理。")
    ]

    for title, content in knowledge_base:
        doc_store.add_document(title, content)

    # 創建 RAG 系統
    rag = RAGSystem(doc_store)

    # 問答
    questions = [
        "你們的產品是什麼？",
        "價格是多少？",
        "如何獲得技術支持？"
    ]

    for question in questions:
        answer = rag.answer_question(question, top_k=2)
        print(f"\n{'='*40}")
        print(f"Q: {answer['question']}")
        print(f"A: {answer['answer']}")
        print(f"來源數: {answer['num_sources']}")


def main():
    """主函數"""
    print("="*60)
    print("Julep 文檔處理和 RAG 示例")
    print("="*60)

    try:
        demo_document_indexing()
        demo_semantic_search()
        demo_rag_qa()

        print("\n" + "="*60)
        print("所有示例執行完成！")
        print("="*60)

    except Exception as e:
        print(f"\n[ERROR] 執行出錯: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

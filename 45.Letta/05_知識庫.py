"""
Letta 知識庫系統

本模組展示如何為 Letta Agent 構建知識庫：
1. 文檔向量化和存儲
2. 語義搜索和檢索
3. 知識圖譜構建
4. RAG（檢索增強生成）實現
5. 知識更新和維護
6. 多源知識整合

讓 Agent 能夠基於大量文檔和知識進行問答。

作者：Letta 框架示例
日期：2025-01
"""

import os
import json
import time
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from collections import defaultdict
import numpy as np


@dataclass
class Document:
    """文檔數據結構"""
    doc_id: str
    title: str
    content: str
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    embedding: Optional[List[float]] = None


@dataclass
class KnowledgeNode:
    """知識圖譜節點"""
    node_id: str
    label: str
    node_type: str
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgeRelation:
    """知識圖譜關係"""
    source_id: str
    target_id: str
    relation_type: str
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchResult:
    """搜索結果"""
    doc_id: str
    title: str
    content: str
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class EmbeddingGenerator:
    """
    嵌入向量生成器

    將文本轉換為向量表示。
    """

    def __init__(self, model_name: str = "text-embedding-ada-002"):
        """
        初始化嵌入生成器

        參數:
            model_name: 嵌入模型名稱
        """
        self.model_name = model_name
        self.dimension = 1536  # OpenAI embedding 的維度

        print(f"嵌入生成器初始化完成（模型: {model_name}）")

    def generate_embedding(self, text: str) -> List[float]:
        """
        生成文本的嵌入向量

        參數:
            text: 輸入文本

        返回:
            嵌入向量
        """
        # 在實際應用中，這裡會調用 OpenAI API
        # 這裡使用簡單的模擬向量
        np.random.seed(hash(text) % (2**32))
        embedding = np.random.randn(self.dimension).tolist()

        print(f"[嵌入生成] 文本長度: {len(text)}, 向量維度: {len(embedding)}")

        return embedding

    def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        批量生成嵌入向量

        參數:
            texts: 文本列表

        返回:
            嵌入向量列表
        """
        print(f"\n[批量嵌入] 處理 {len(texts)} 個文本...")

        embeddings = [self.generate_embedding(text) for text in texts]

        print(f"✓ 完成 {len(embeddings)} 個向量的生成")

        return embeddings


class VectorStore:
    """
    向量存儲

    存儲和檢索文檔向量。
    """

    def __init__(self, dimension: int = 1536):
        """
        初始化向量存儲

        參數:
            dimension: 向量維度
        """
        self.dimension = dimension
        self.documents: Dict[str, Document] = {}
        self.vectors: Dict[str, np.ndarray] = {}

        print(f"向量存儲初始化完成（維度: {dimension}）")

    def add_document(self, document: Document) -> None:
        """
        添加文檔

        參數:
            document: 文檔對象
        """
        if document.embedding is None:
            raise ValueError("文檔必須包含嵌入向量")

        self.documents[document.doc_id] = document
        self.vectors[document.doc_id] = np.array(document.embedding)

        print(f"[添加文檔] {document.title} (ID: {document.doc_id})")

    def search(self, query_embedding: List[float], top_k: int = 5,
              filter_metadata: Optional[Dict] = None) -> List[SearchResult]:
        """
        搜索相似文檔

        參數:
            query_embedding: 查詢向量
            top_k: 返回結果數量
            filter_metadata: 元數據過濾條件

        返回:
            搜索結果列表
        """
        if not self.vectors:
            return []

        query_vector = np.array(query_embedding)

        # 計算餘弦相似度
        similarities = {}
        for doc_id, doc_vector in self.vectors.items():
            # 應用元數據過濾
            if filter_metadata:
                doc = self.documents[doc_id]
                if not all(doc.metadata.get(k) == v for k, v in filter_metadata.items()):
                    continue

            similarity = self._cosine_similarity(query_vector, doc_vector)
            similarities[doc_id] = similarity

        # 排序並返回 top_k
        sorted_docs = sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:top_k]

        results = [
            SearchResult(
                doc_id=doc_id,
                title=self.documents[doc_id].title,
                content=self.documents[doc_id].content,
                score=score,
                metadata=self.documents[doc_id].metadata
            )
            for doc_id, score in sorted_docs
        ]

        print(f"\n[向量搜索] 找到 {len(results)} 個相關文檔:")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result.title} (相似度: {result.score:.3f})")

        return results

    def _cosine_similarity(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """計算餘弦相似度"""
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

    def get_statistics(self) -> Dict[str, Any]:
        """獲取統計信息"""
        stats = {
            "total_documents": len(self.documents),
            "vector_dimension": self.dimension,
            "storage_size_mb": len(self.vectors) * self.dimension * 4 / (1024 * 1024)
        }

        print(f"\n[存儲統計]")
        print(f"  文檔總數: {stats['total_documents']}")
        print(f"  向量維度: {stats['vector_dimension']}")
        print(f"  存儲大小: {stats['storage_size_mb']:.2f} MB")

        return stats


class KnowledgeGraph:
    """
    知識圖譜

    構建和查詢知識圖譜。
    """

    def __init__(self):
        """初始化知識圖譜"""
        self.nodes: Dict[str, KnowledgeNode] = {}
        self.relations: List[KnowledgeRelation] = []
        self.adjacency_list: Dict[str, List[str]] = defaultdict(list)

        print("知識圖譜初始化完成")

    def add_node(self, node: KnowledgeNode) -> None:
        """
        添加節點

        參數:
            node: 知識節點
        """
        self.nodes[node.node_id] = node
        print(f"[添加節點] {node.label} (類型: {node.node_type})")

    def add_relation(self, relation: KnowledgeRelation) -> None:
        """
        添加關係

        參數:
            relation: 知識關係
        """
        self.relations.append(relation)
        self.adjacency_list[relation.source_id].append(relation.target_id)

        print(f"[添加關係] {relation.source_id} --[{relation.relation_type}]--> {relation.target_id}")

    def find_neighbors(self, node_id: str, max_depth: int = 1) -> List[KnowledgeNode]:
        """
        查找鄰居節點

        參數:
            node_id: 節點 ID
            max_depth: 最大深度

        返回:
            鄰居節點列表
        """
        neighbors = set()
        queue = [(node_id, 0)]
        visited = {node_id}

        while queue:
            current_id, depth = queue.pop(0)

            if depth >= max_depth:
                continue

            for neighbor_id in self.adjacency_list[current_id]:
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    neighbors.add(neighbor_id)
                    queue.append((neighbor_id, depth + 1))

        neighbor_nodes = [self.nodes[nid] for nid in neighbors if nid in self.nodes]

        print(f"\n[鄰居查詢] 節點 {node_id} 的 {max_depth} 層鄰居: {len(neighbor_nodes)} 個")

        return neighbor_nodes

    def find_path(self, start_id: str, end_id: str) -> Optional[List[str]]:
        """
        查找兩個節點之間的路徑

        參數:
            start_id: 起始節點 ID
            end_id: 目標節點 ID

        返回:
            路徑（節點 ID 列表），如果不存在則返回 None
        """
        queue = [(start_id, [start_id])]
        visited = {start_id}

        while queue:
            current_id, path = queue.pop(0)

            if current_id == end_id:
                print(f"\n[路徑查詢] {start_id} -> {end_id}: {' -> '.join(path)}")
                return path

            for neighbor_id in self.adjacency_list[current_id]:
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    queue.append((neighbor_id, path + [neighbor_id]))

        print(f"\n[路徑查詢] {start_id} 到 {end_id} 不存在路徑")
        return None

    def get_subgraph(self, node_ids: List[str]) -> Tuple[List[KnowledgeNode], List[KnowledgeRelation]]:
        """
        獲取子圖

        參數:
            node_ids: 節點 ID 列表

        返回:
            (節點列表, 關係列表)
        """
        nodes = [self.nodes[nid] for nid in node_ids if nid in self.nodes]

        relations = [
            rel for rel in self.relations
            if rel.source_id in node_ids and rel.target_id in node_ids
        ]

        print(f"\n[子圖] 節點數: {len(nodes)}, 關係數: {len(relations)}")

        return nodes, relations


class KnowledgeBase:
    """
    知識庫

    整合向量存儲和知識圖譜。
    """

    def __init__(self, name: str = "default"):
        """
        初始化知識庫

        參數:
            name: 知識庫名稱
        """
        self.name = name
        self.embedding_generator = EmbeddingGenerator()
        self.vector_store = VectorStore()
        self.knowledge_graph = KnowledgeGraph()

        print(f"\n知識庫 '{name}' 初始化完成")

    def add_document(self, title: str, content: str, source: str = "manual",
                    metadata: Optional[Dict] = None) -> str:
        """
        添加文檔到知識庫

        參數:
            title: 文檔標題
            content: 文檔內容
            source: 來源
            metadata: 元數據

        返回:
            文檔 ID
        """
        # 生成文檔 ID
        doc_id = self._generate_doc_id(title, content)

        # 生成嵌入向量
        embedding = self.embedding_generator.generate_embedding(content)

        # 創建文檔
        document = Document(
            doc_id=doc_id,
            title=title,
            content=content,
            source=source,
            metadata=metadata or {},
            embedding=embedding
        )

        # 添加到向量存儲
        self.vector_store.add_document(document)

        # 添加到知識圖譜
        node = KnowledgeNode(
            node_id=doc_id,
            label=title,
            node_type="document",
            properties={"source": source}
        )
        self.knowledge_graph.add_node(node)

        print(f"\n✓ 文檔已添加到知識庫: {title}")

        return doc_id

    def add_batch_documents(self, documents: List[Dict[str, str]]) -> List[str]:
        """
        批量添加文檔

        參數:
            documents: 文檔列表，每個元素包含 title, content, source

        返回:
            文檔 ID 列表
        """
        print(f"\n[批量添加] 處理 {len(documents)} 個文檔...")

        doc_ids = []
        for doc in documents:
            doc_id = self.add_document(
                title=doc['title'],
                content=doc['content'],
                source=doc.get('source', 'batch'),
                metadata=doc.get('metadata')
            )
            doc_ids.append(doc_id)

        print(f"✓ 批量添加完成，共 {len(doc_ids)} 個文檔")

        return doc_ids

    def search(self, query: str, top_k: int = 5,
              use_graph: bool = False) -> List[SearchResult]:
        """
        搜索知識庫

        參數:
            query: 查詢文本
            top_k: 返回結果數量
            use_graph: 是否使用知識圖譜擴展結果

        返回:
            搜索結果列表
        """
        print(f"\n[知識庫搜索] 查詢: '{query}'")

        # 生成查詢向量
        query_embedding = self.embedding_generator.generate_embedding(query)

        # 向量搜索
        results = self.vector_store.search(query_embedding, top_k)

        # 如果使用知識圖譜，擴展結果
        if use_graph and results:
            print("\n[圖譜擴展] 使用知識圖譜擴展結果...")
            expanded_results = self._expand_with_graph(results)
            return expanded_results

        return results

    def _expand_with_graph(self, results: List[SearchResult]) -> List[SearchResult]:
        """使用知識圖譜擴展搜索結果"""
        expanded_doc_ids = set(r.doc_id for r in results)

        # 查找相關節點
        for result in results:
            neighbors = self.knowledge_graph.find_neighbors(result.doc_id, max_depth=1)
            for neighbor in neighbors:
                expanded_doc_ids.add(neighbor.node_id)

        # 獲取擴展的文檔
        expanded_results = list(results)  # 保留原始結果

        for doc_id in expanded_doc_ids:
            if doc_id not in [r.doc_id for r in results]:
                if doc_id in self.vector_store.documents:
                    doc = self.vector_store.documents[doc_id]
                    expanded_results.append(
                        SearchResult(
                            doc_id=doc.doc_id,
                            title=doc.title,
                            content=doc.content,
                            score=0.5,  # 降低擴展結果的分數
                            metadata={**doc.metadata, "expanded": True}
                        )
                    )

        print(f"✓ 擴展後結果數: {len(expanded_results)}")

        return expanded_results

    def create_relation(self, doc_id1: str, doc_id2: str,
                       relation_type: str = "related") -> None:
        """
        創建文檔之間的關係

        參數:
            doc_id1: 文檔1 ID
            doc_id2: 文檔2 ID
            relation_type: 關係類型
        """
        relation = KnowledgeRelation(
            source_id=doc_id1,
            target_id=doc_id2,
            relation_type=relation_type
        )
        self.knowledge_graph.add_relation(relation)

    def get_related_documents(self, doc_id: str) -> List[Document]:
        """
        獲取相關文檔

        參數:
            doc_id: 文檔 ID

        返回:
            相關文檔列表
        """
        neighbors = self.knowledge_graph.find_neighbors(doc_id)
        related_docs = [
            self.vector_store.documents[n.node_id]
            for n in neighbors
            if n.node_id in self.vector_store.documents
        ]

        print(f"\n[相關文檔] 文檔 {doc_id} 有 {len(related_docs)} 個相關文檔")

        return related_docs

    def _generate_doc_id(self, title: str, content: str) -> str:
        """生成文檔 ID"""
        data = f"{title}_{content}_{datetime.now().isoformat()}"
        return hashlib.md5(data.encode()).hexdigest()[:16]


class RAGSystem:
    """
    檢索增強生成（RAG）系統

    結合知識檢索和 LLM 生成。
    """

    def __init__(self, knowledge_base: KnowledgeBase):
        """
        初始化 RAG 系統

        參數:
            knowledge_base: 知識庫實例
        """
        self.knowledge_base = knowledge_base
        print("\nRAG 系統初始化完成")

    def answer_question(self, question: str, max_context_docs: int = 3) -> Dict[str, Any]:
        """
        回答問題

        參數:
            question: 問題
            max_context_docs: 最大上下文文檔數

        返回:
            包含答案和來源的字典
        """
        print(f"\n[RAG 問答] 問題: {question}")

        # 1. 檢索相關文檔
        print("\n[步驟 1/3] 檢索相關文檔...")
        search_results = self.knowledge_base.search(question, top_k=max_context_docs)

        # 2. 構建上下文
        print("\n[步驟 2/3] 構建上下文...")
        context = self._build_context(search_results)

        # 3. 生成答案
        print("\n[步驟 3/3] 生成答案...")
        answer = self._generate_answer(question, context)

        result = {
            "question": question,
            "answer": answer,
            "sources": [
                {
                    "title": r.title,
                    "score": r.score,
                    "content": r.content[:200] + "..."
                }
                for r in search_results
            ],
            "context_docs": len(search_results)
        }

        print(f"\n[答案] {answer}")
        print(f"\n[來源] {len(result['sources'])} 個文檔")

        return result

    def _build_context(self, search_results: List[SearchResult]) -> str:
        """構建上下文"""
        context_parts = []

        for i, result in enumerate(search_results, 1):
            context_parts.append(f"文檔 {i}: {result.title}\n{result.content}")

        context = "\n\n".join(context_parts)
        print(f"上下文長度: {len(context)} 字符")

        return context

    def _generate_answer(self, question: str, context: str) -> str:
        """生成答案（模擬）"""
        # 在實際應用中，這裡會調用 LLM
        # 這裡使用簡單的模擬

        answer = f"根據提供的文檔，關於「{question}」的回答是：\n\n"
        answer += "基於檢索到的相關文檔，我們可以得出以下結論... "
        answer += "（實際應用中，這裡會是 LLM 基於上下文生成的詳細答案）"

        return answer


def demonstrate_basic_knowledge_base():
    """演示基本知識庫功能"""
    print("\n" + "=" * 60)
    print("基本知識庫演示")
    print("=" * 60)

    kb = KnowledgeBase("技術文檔庫")

    # 添加文檔
    doc1_id = kb.add_document(
        title="Python 入門教程",
        content="Python 是一種高級編程語言，易於學習且功能強大。它廣泛應用於 Web 開發、數據科學、人工智能等領域。",
        source="tutorial"
    )

    doc2_id = kb.add_document(
        title="機器學習基礎",
        content="機器學習是人工智能的一個分支，它使計算機能夠從數據中學習。常見的算法包括線性回歸、決策樹和神經網絡。",
        source="tutorial"
    )

    doc3_id = kb.add_document(
        title="深度學習框架",
        content="深度學習框架如 TensorFlow 和 PyTorch 提供了構建神經網絡的工具。Python 是使用這些框架的首選語言。",
        source="tutorial"
    )

    # 創建關係
    kb.create_relation(doc1_id, doc3_id, "prerequisite")
    kb.create_relation(doc2_id, doc3_id, "related")

    # 搜索
    kb.search("Python 機器學習", top_k=3)


def demonstrate_batch_operations():
    """演示批量操作"""
    print("\n" + "=" * 60)
    print("批量操作演示")
    print("=" * 60)

    kb = KnowledgeBase("批量測試庫")

    # 批量添加文檔
    documents = [
        {
            "title": "數據結構：數組",
            "content": "數組是最基本的數據結構，用於存儲相同類型的元素。",
            "source": "course"
        },
        {
            "title": "數據結構：鏈表",
            "content": "鏈表是一種動態數據結構，每個節點包含數據和指向下一個節點的指針。",
            "source": "course"
        },
        {
            "title": "數據結構：樹",
            "content": "樹是一種分層數據結構，具有根節點和子節點。二叉樹是最常見的樹結構。",
            "source": "course"
        },
        {
            "title": "算法：排序",
            "content": "排序算法包括冒泡排序、快速排序、歸併排序等。",
            "source": "course"
        },
        {
            "title": "算法：搜索",
            "content": "搜索算法包括線性搜索和二分搜索。",
            "source": "course"
        }
    ]

    kb.add_batch_documents(documents)

    # 統計
    kb.vector_store.get_statistics()


def demonstrate_rag_system():
    """演示 RAG 系統"""
    print("\n" + "=" * 60)
    print("RAG 系統演示")
    print("=" * 60)

    # 創建知識庫
    kb = KnowledgeBase("問答知識庫")

    # 添加知識
    kb.add_document(
        title="Letta 框架介紹",
        content="Letta（原 MemGPT）是一個有狀態的 AI Agent 框架，提供持久記憶功能。它實現了三層記憶架構：核心記憶、歸檔記憶和回憶記憶。",
        source="docs"
    )

    kb.add_document(
        title="Letta 記憶管理",
        content="Letta 的記憶管理類似操作系統的內存管理。核心記憶像 CPU 緩存，容量有限但訪問快速。歸檔記憶像硬碟，容量大但需要搜索。",
        source="docs"
    )

    kb.add_document(
        title="Letta 工具系統",
        content="Letta 支持自定義工具，讓 Agent 能夠執行實際操作。工具可以是搜索、計算、數據庫查詢等任何函數。",
        source="docs"
    )

    # 創建 RAG 系統
    rag = RAGSystem(kb)

    # 問答
    rag.answer_question("什麼是 Letta 的記憶架構？")
    time.sleep(1)
    rag.answer_question("Letta 如何支持工具調用？")


def demonstrate_knowledge_graph():
    """演示知識圖譜功能"""
    print("\n" + "=" * 60)
    print("知識圖譜演示")
    print("=" * 60)

    kb = KnowledgeBase("圖譜測試庫")

    # 添加文檔並創建複雜的關係網絡
    python_id = kb.add_document("Python", "編程語言", "manual")
    django_id = kb.add_document("Django", "Web 框架", "manual")
    flask_id = kb.add_document("Flask", "Web 框架", "manual")
    ml_id = kb.add_document("機器學習", "AI 技術", "manual")
    tf_id = kb.add_document("TensorFlow", "ML 框架", "manual")

    # 創建關係
    kb.create_relation(python_id, django_id, "has_framework")
    kb.create_relation(python_id, flask_id, "has_framework")
    kb.create_relation(python_id, ml_id, "used_for")
    kb.create_relation(ml_id, tf_id, "uses_framework")
    kb.create_relation(python_id, tf_id, "implements")

    # 查找路徑
    kb.knowledge_graph.find_path(django_id, tf_id)

    # 查找鄰居
    kb.get_related_documents(python_id)


def main():
    """主函數：運行所有演示"""
    print("\n" + "=" * 70)
    print(" " * 20 + "Letta 知識庫系統")
    print("=" * 70)

    # 基本知識庫
    demonstrate_basic_knowledge_base()

    # 批量操作
    demonstrate_batch_operations()

    # RAG 系統
    demonstrate_rag_system()

    # 知識圖譜
    demonstrate_knowledge_graph()

    print("\n" + "=" * 70)
    print("知識庫系統演示完成！")
    print("=" * 70)
    print("\n關鍵要點：")
    print("  1. 向量化存儲支持語義搜索")
    print("  2. 知識圖譜捕捉實體間的關係")
    print("  3. RAG 系統結合檢索和生成")
    print("  4. 支持批量文檔處理")
    print("  5. 多源知識可以整合到統一知識庫")
    print("\n下一步：查看 06_多Agent.py")
    print("=" * 70)


if __name__ == "__main__":
    main()

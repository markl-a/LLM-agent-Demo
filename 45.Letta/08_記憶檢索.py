"""
Letta 記憶檢索策略

本模組展示高級記憶檢索技術：
1. 向量相似度搜索
2. 關鍵詞檢索
3. 混合檢索策略
4. 時間加權檢索
5. 重要性加權
6. 上下文感知檢索
7. 檢索優化技術

提升 Agent 的記憶檢索效率和準確性。

作者：Letta 框架示例
日期：2025-01
"""

import os
import json
import time
import math
from typing import Dict, List, Optional, Any, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict
import numpy as np
import heapq


@dataclass
class MemoryItem:
    """記憶項"""
    memory_id: str
    content: str
    embedding: Optional[List[float]] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    importance: float = 0.5
    access_count: int = 0
    last_accessed: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RetrievalResult:
    """檢索結果"""
    memory_item: MemoryItem
    score: float
    retrieval_reason: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class VectorRetriever:
    """
    向量檢索器

    基於向量相似度檢索記憶。
    """

    def __init__(self, dimension: int = 1536):
        """
        初始化向量檢索器

        參數:
            dimension: 向量維度
        """
        self.dimension = dimension
        self.memories: Dict[str, MemoryItem] = {}

        print(f"向量檢索器初始化完成（維度: {dimension}）")

    def add_memory(self, memory: MemoryItem) -> None:
        """
        添加記憶

        參數:
            memory: 記憶項
        """
        if memory.embedding is None:
            # 生成模擬向量
            np.random.seed(hash(memory.content) % (2**32))
            memory.embedding = np.random.randn(self.dimension).tolist()

        self.memories[memory.memory_id] = memory
        print(f"[向量檢索器] 添加記憶: {memory.memory_id}")

    def search(self, query_embedding: List[float], top_k: int = 5,
              min_score: float = 0.0) -> List[RetrievalResult]:
        """
        搜索相似記憶

        參數:
            query_embedding: 查詢向量
            top_k: 返回結果數量
            min_score: 最小相似度分數

        返回:
            檢索結果列表
        """
        if not self.memories:
            return []

        query_vector = np.array(query_embedding)
        results = []

        for memory_id, memory in self.memories.items():
            if memory.embedding is None:
                continue

            memory_vector = np.array(memory.embedding)
            similarity = self._cosine_similarity(query_vector, memory_vector)

            if similarity >= min_score:
                result = RetrievalResult(
                    memory_item=memory,
                    score=similarity,
                    retrieval_reason="向量相似度"
                )
                results.append(result)

        # 按相似度排序
        results.sort(key=lambda r: r.score, reverse=True)

        print(f"\n[向量檢索] 找到 {len(results)} 個相關記憶")
        for i, result in enumerate(results[:top_k], 1):
            print(f"  {i}. {result.memory_item.content[:50]}... (分數: {result.score:.3f})")

        return results[:top_k]

    def _cosine_similarity(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """計算餘弦相似度"""
        dot_product = np.dot(v1, v2)
        norm_product = np.linalg.norm(v1) * np.linalg.norm(v2)
        return dot_product / norm_product if norm_product > 0 else 0.0


class KeywordRetriever:
    """
    關鍵詞檢索器

    基於關鍵詞匹配檢索記憶。
    """

    def __init__(self):
        """初始化關鍵詞檢索器"""
        self.memories: Dict[str, MemoryItem] = {}
        self.inverted_index: Dict[str, List[str]] = defaultdict(list)

        print("關鍵詞檢索器初始化完成")

    def add_memory(self, memory: MemoryItem) -> None:
        """
        添加記憶並建立索引

        參數:
            memory: 記憶項
        """
        self.memories[memory.memory_id] = memory

        # 建立倒排索引
        keywords = self._extract_keywords(memory.content)
        for keyword in keywords:
            if memory.memory_id not in self.inverted_index[keyword]:
                self.inverted_index[keyword].append(memory.memory_id)

        print(f"[關鍵詞檢索器] 添加記憶: {memory.memory_id} ({len(keywords)} 個關鍵詞)")

    def search(self, query: str, top_k: int = 5) -> List[RetrievalResult]:
        """
        搜索包含關鍵詞的記憶

        參數:
            query: 查詢文本
            top_k: 返回結果數量

        返回:
            檢索結果列表
        """
        query_keywords = self._extract_keywords(query)

        # 計算每個記憶的匹配分數
        memory_scores: Dict[str, float] = defaultdict(float)

        for keyword in query_keywords:
            if keyword in self.inverted_index:
                for memory_id in self.inverted_index[keyword]:
                    # TF-IDF 風格的評分
                    idf = math.log(len(self.memories) / len(self.inverted_index[keyword]))
                    memory_scores[memory_id] += idf

        # 轉換為結果列表
        results = []
        for memory_id, score in memory_scores.items():
            if memory_id in self.memories:
                result = RetrievalResult(
                    memory_item=self.memories[memory_id],
                    score=score,
                    retrieval_reason="關鍵詞匹配"
                )
                results.append(result)

        # 排序並返回 top_k
        results.sort(key=lambda r: r.score, reverse=True)

        print(f"\n[關鍵詞檢索] 查詢: '{query}'")
        print(f"找到 {len(results)} 個相關記憶")
        for i, result in enumerate(results[:top_k], 1):
            print(f"  {i}. {result.memory_item.content[:50]}... (分數: {result.score:.3f})")

        return results[:top_k]

    def _extract_keywords(self, text: str) -> List[str]:
        """提取關鍵詞"""
        # 簡化版關鍵詞提取
        # 實際應用中應該使用更複雜的 NLP 技術
        import re

        # 移除標點，轉小寫，分詞
        text = text.lower()
        words = re.findall(r'\w+', text)

        # 過濾停用詞（簡化版）
        stop_words = {"的", "是", "在", "和", "有", "了", "我", "你", "他", "她", "它"}
        keywords = [w for w in words if w not in stop_words and len(w) > 1]

        return keywords


class TimeWeightedRetriever:
    """
    時間加權檢索器

    考慮記憶的時間因素進行檢索。
    """

    def __init__(self, decay_rate: float = 0.1):
        """
        初始化時間加權檢索器

        參數:
            decay_rate: 時間衰減率（每天）
        """
        self.decay_rate = decay_rate
        self.memories: Dict[str, MemoryItem] = {}

        print(f"時間加權檢索器初始化完成（衰減率: {decay_rate}）")

    def add_memory(self, memory: MemoryItem) -> None:
        """添加記憶"""
        self.memories[memory.memory_id] = memory

    def search(self, base_scores: Dict[str, float], top_k: int = 5) -> List[RetrievalResult]:
        """
        應用時間加權檢索

        參數:
            base_scores: 基礎分數字典（memory_id -> score）
            top_k: 返回結果數量

        返回:
            檢索結果列表
        """
        results = []
        current_time = datetime.now()

        for memory_id, base_score in base_scores.items():
            if memory_id not in self.memories:
                continue

            memory = self.memories[memory_id]

            # 計算時間衰減
            memory_time = datetime.fromisoformat(memory.timestamp)
            days_elapsed = (current_time - memory_time).days
            time_weight = math.exp(-self.decay_rate * days_elapsed)

            # 最終分數 = 基礎分數 * 時間權重
            final_score = base_score * time_weight

            result = RetrievalResult(
                memory_item=memory,
                score=final_score,
                retrieval_reason="時間加權",
                metadata={
                    "base_score": base_score,
                    "time_weight": time_weight,
                    "days_elapsed": days_elapsed
                }
            )
            results.append(result)

        results.sort(key=lambda r: r.score, reverse=True)

        print(f"\n[時間加權檢索] 應用時間衰減")
        for i, result in enumerate(results[:top_k], 1):
            meta = result.metadata
            print(f"  {i}. 基礎: {meta['base_score']:.3f}, "
                  f"時間權重: {meta['time_weight']:.3f}, "
                  f"最終: {result.score:.3f}")

        return results[:top_k]


class ImportanceWeightedRetriever:
    """
    重要性加權檢索器

    基於記憶的重要性調整檢索結果。
    """

    def __init__(self):
        """初始化重要性加權檢索器"""
        self.memories: Dict[str, MemoryItem] = {}
        print("重要性加權檢索器初始化完成")

    def add_memory(self, memory: MemoryItem) -> None:
        """添加記憶"""
        self.memories[memory.memory_id] = memory

    def search(self, base_scores: Dict[str, float],
              importance_weight: float = 0.3, top_k: int = 5) -> List[RetrievalResult]:
        """
        應用重要性加權

        參數:
            base_scores: 基礎分數字典
            importance_weight: 重要性權重（0-1）
            top_k: 返回結果數量

        返回:
            檢索結果列表
        """
        results = []

        for memory_id, base_score in base_scores.items():
            if memory_id not in self.memories:
                continue

            memory = self.memories[memory_id]

            # 綜合分數 = 基礎分數 * (1 - weight) + 重要性 * weight
            final_score = (base_score * (1 - importance_weight) +
                          memory.importance * importance_weight)

            result = RetrievalResult(
                memory_item=memory,
                score=final_score,
                retrieval_reason="重要性加權",
                metadata={
                    "base_score": base_score,
                    "importance": memory.importance,
                    "final_score": final_score
                }
            )
            results.append(result)

        results.sort(key=lambda r: r.score, reverse=True)

        print(f"\n[重要性加權] 應用重要性因子（權重: {importance_weight}）")
        for i, result in enumerate(results[:top_k], 1):
            meta = result.metadata
            print(f"  {i}. 基礎: {meta['base_score']:.3f}, "
                  f"重要性: {meta['importance']:.3f}, "
                  f"最終: {result.score:.3f}")

        return results[:top_k]


class HybridRetriever:
    """
    混合檢索器

    結合多種檢索策略。
    """

    def __init__(self):
        """初始化混合檢索器"""
        self.vector_retriever = VectorRetriever()
        self.keyword_retriever = KeywordRetriever()
        self.time_retriever = TimeWeightedRetriever()
        self.importance_retriever = ImportanceWeightedRetriever()

        print("\n混合檢索器初始化完成")

    def add_memory(self, memory: MemoryItem) -> None:
        """
        添加記憶到所有檢索器

        參數:
            memory: 記憶項
        """
        self.vector_retriever.add_memory(memory)
        self.keyword_retriever.add_memory(memory)
        self.time_retriever.add_memory(memory)
        self.importance_retriever.add_memory(memory)

    def search(self, query: str, query_embedding: Optional[List[float]] = None,
              strategy: str = "fusion", top_k: int = 5) -> List[RetrievalResult]:
        """
        混合檢索

        參數:
            query: 查詢文本
            query_embedding: 查詢向量（可選）
            strategy: 策略（'fusion', 'cascade', 'parallel'）
            top_k: 返回結果數量

        返回:
            檢索結果列表
        """
        print(f"\n[混合檢索] 策略: {strategy}, 查詢: '{query}'")

        if strategy == "fusion":
            return self._fusion_search(query, query_embedding, top_k)
        elif strategy == "cascade":
            return self._cascade_search(query, query_embedding, top_k)
        elif strategy == "parallel":
            return self._parallel_search(query, query_embedding, top_k)
        else:
            raise ValueError(f"不支持的策略: {strategy}")

    def _fusion_search(self, query: str, query_embedding: Optional[List[float]],
                      top_k: int) -> List[RetrievalResult]:
        """融合檢索：合併多個檢索器的結果"""
        print("\n[融合檢索] 合併多個檢索源...")

        all_scores: Dict[str, List[float]] = defaultdict(list)

        # 1. 關鍵詞檢索
        keyword_results = self.keyword_retriever.search(query, top_k=top_k * 2)
        for result in keyword_results:
            all_scores[result.memory_item.memory_id].append(result.score)

        # 2. 向量檢索（如果提供了向量）
        if query_embedding:
            vector_results = self.vector_retriever.search(query_embedding, top_k=top_k * 2)
            for result in vector_results:
                all_scores[result.memory_item.memory_id].append(result.score)

        # 3. 融合分數（平均）
        fused_scores = {
            memory_id: sum(scores) / len(scores)
            for memory_id, scores in all_scores.items()
        }

        # 4. 應用時間和重要性權重
        time_weighted = self.time_retriever.search(fused_scores, top_k=top_k * 2)
        final_scores = {r.memory_item.memory_id: r.score for r in time_weighted}

        importance_weighted = self.importance_retriever.search(final_scores, top_k=top_k)

        print(f"✓ 融合檢索完成，返回 {len(importance_weighted)} 個結果")

        return importance_weighted

    def _cascade_search(self, query: str, query_embedding: Optional[List[float]],
                       top_k: int) -> List[RetrievalResult]:
        """級聯檢索：依次應用檢索器，逐步篩選"""
        print("\n[級聯檢索] 多階段過濾...")

        # 階段 1：關鍵詞初篩
        candidates = self.keyword_retriever.search(query, top_k=top_k * 3)

        if not candidates:
            return []

        # 階段 2：向量精排
        if query_embedding:
            candidate_scores = {r.memory_item.memory_id: r.score for r in candidates}
            # 只對候選項進行向量檢索
            # 這裡簡化處理，實際應該只計算候選項的相似度
            candidates = self.vector_retriever.search(query_embedding, top_k=top_k * 2)

        # 階段 3：時間過濾
        candidate_scores = {r.memory_item.memory_id: r.score for r in candidates}
        candidates = self.time_retriever.search(candidate_scores, top_k=top_k)

        print(f"✓ 級聯檢索完成，返回 {len(candidates)} 個結果")

        return candidates

    def _parallel_search(self, query: str, query_embedding: Optional[List[float]],
                        top_k: int) -> List[RetrievalResult]:
        """並行檢索：同時運行多個檢索器，取並集"""
        print("\n[並行檢索] 同時運行多個檢索器...")

        all_results = []

        # 關鍵詞檢索
        keyword_results = self.keyword_retriever.search(query, top_k=top_k)
        all_results.extend(keyword_results)

        # 向量檢索
        if query_embedding:
            vector_results = self.vector_retriever.search(query_embedding, top_k=top_k)
            all_results.extend(vector_results)

        # 去重並排序
        seen_ids = set()
        unique_results = []

        for result in all_results:
            if result.memory_item.memory_id not in seen_ids:
                seen_ids.add(result.memory_item.memory_id)
                unique_results.append(result)

        unique_results.sort(key=lambda r: r.score, reverse=True)

        print(f"✓ 並行檢索完成，返回 {len(unique_results[:top_k])} 個結果")

        return unique_results[:top_k]


class ContextAwareRetriever:
    """
    上下文感知檢索器

    根據當前對話上下文調整檢索策略。
    """

    def __init__(self, hybrid_retriever: HybridRetriever):
        """
        初始化上下文感知檢索器

        參數:
            hybrid_retriever: 混合檢索器實例
        """
        self.hybrid_retriever = hybrid_retriever
        self.context_history: List[str] = []
        self.max_context_length = 10

        print("上下文感知檢索器初始化完成")

    def update_context(self, message: str) -> None:
        """
        更新上下文

        參數:
            message: 新消息
        """
        self.context_history.append(message)

        # 保持上下文長度
        if len(self.context_history) > self.max_context_length:
            self.context_history.pop(0)

        print(f"[上下文更新] 當前上下文長度: {len(self.context_history)}")

    def search(self, query: str, query_embedding: Optional[List[float]] = None,
              top_k: int = 5) -> List[RetrievalResult]:
        """
        上下文感知檢索

        參數:
            query: 查詢文本
            query_embedding: 查詢向量
            top_k: 返回結果數量

        返回:
            檢索結果列表
        """
        print(f"\n[上下文感知檢索] 查詢: '{query}'")

        # 擴展查詢：結合最近的上下文
        expanded_query = query
        if self.context_history:
            # 添加最近的上下文關鍵詞
            recent_context = " ".join(self.context_history[-3:])
            expanded_query = f"{query} {recent_context}"
            print(f"  擴展查詢: '{expanded_query[:100]}...'")

        # 使用混合檢索
        results = self.hybrid_retriever.search(
            expanded_query,
            query_embedding,
            strategy="fusion",
            top_k=top_k
        )

        # 根據上下文重新排序
        results = self._rerank_by_context(results)

        return results

    def _rerank_by_context(self, results: List[RetrievalResult]) -> List[RetrievalResult]:
        """根據上下文重新排序結果"""
        if not self.context_history:
            return results

        # 計算每個結果與上下文的相關性
        for result in results:
            context_relevance = 0
            for context_msg in self.context_history:
                # 簡單的詞重疊計算
                content_words = set(result.memory_item.content.lower().split())
                context_words = set(context_msg.lower().split())
                overlap = len(content_words & context_words)
                context_relevance += overlap

            # 調整分數
            result.score = result.score * 0.7 + context_relevance * 0.3

        # 重新排序
        results.sort(key=lambda r: r.score, reverse=True)

        return results


def demonstrate_vector_retrieval():
    """演示向量檢索"""
    print("\n" + "=" * 60)
    print("向量檢索演示")
    print("=" * 60)

    retriever = VectorRetriever()

    # 添加記憶
    memories = [
        MemoryItem("mem_1", "Python 是一種高級編程語言"),
        MemoryItem("mem_2", "機器學習使用 Python 很方便"),
        MemoryItem("mem_3", "JavaScript 是 Web 開發的核心語言"),
        MemoryItem("mem_4", "深度學習需要大量數據"),
        MemoryItem("mem_5", "Python 在數據科學領域很流行")
    ]

    for memory in memories:
        retriever.add_memory(memory)

    # 生成查詢向量
    np.random.seed(42)
    query_embedding = np.random.randn(1536).tolist()

    # 搜索
    results = retriever.search(query_embedding, top_k=3)


def demonstrate_keyword_retrieval():
    """演示關鍵詞檢索"""
    print("\n" + "=" * 60)
    print("關鍵詞檢索演示")
    print("=" * 60)

    retriever = KeywordRetriever()

    # 添加記憶
    memories = [
        MemoryItem("mem_1", "學習 Python 編程需要掌握基礎語法"),
        MemoryItem("mem_2", "Python 的數據分析庫包括 pandas 和 numpy"),
        MemoryItem("mem_3", "機器學習算法可以用 scikit-learn 實現"),
        MemoryItem("mem_4", "深度學習框架有 TensorFlow 和 PyTorch"),
        MemoryItem("mem_5", "Web 開發可以使用 Django 或 Flask 框架")
    ]

    for memory in memories:
        retriever.add_memory(memory)

    # 搜索
    retriever.search("Python 數據分析", top_k=3)


def demonstrate_hybrid_retrieval():
    """演示混合檢索"""
    print("\n" + "=" * 60)
    print("混合檢索演示")
    print("=" * 60)

    retriever = HybridRetriever()

    # 添加記憶（帶時間戳和重要性）
    base_time = datetime.now()

    memories = [
        MemoryItem(
            "mem_1",
            "用戶喜歡 Python 編程",
            timestamp=(base_time - timedelta(days=1)).isoformat(),
            importance=0.8
        ),
        MemoryItem(
            "mem_2",
            "用戶正在學習機器學習",
            timestamp=(base_time - timedelta(days=3)).isoformat(),
            importance=0.9
        ),
        MemoryItem(
            "mem_3",
            "用戶詢問過 Web 開發",
            timestamp=(base_time - timedelta(days=7)).isoformat(),
            importance=0.5
        ),
        MemoryItem(
            "mem_4",
            "用戶對深度學習感興趣",
            timestamp=(base_time - timedelta(hours=2)).isoformat(),
            importance=0.95
        ),
        MemoryItem(
            "mem_5",
            "用戶使用過 TensorFlow",
            timestamp=(base_time - timedelta(days=5)).isoformat(),
            importance=0.7
        )
    ]

    for memory in memories:
        retriever.add_memory(memory)

    # 測試不同策略
    np.random.seed(42)
    query_embedding = np.random.randn(1536).tolist()

    print("\n" + "-" * 60)
    retriever.search("機器學習 Python", query_embedding, strategy="fusion", top_k=3)

    print("\n" + "-" * 60)
    retriever.search("機器學習 Python", query_embedding, strategy="cascade", top_k=3)

    print("\n" + "-" * 60)
    retriever.search("機器學習 Python", query_embedding, strategy="parallel", top_k=3)


def demonstrate_context_aware_retrieval():
    """演示上下文感知檢索"""
    print("\n" + "=" * 60)
    print("上下文感知檢索演示")
    print("=" * 60)

    hybrid = HybridRetriever()
    retriever = ContextAwareRetriever(hybrid)

    # 添加記憶
    memories = [
        MemoryItem("mem_1", "Python 的基礎語法很簡單"),
        MemoryItem("mem_2", "列表推導式是 Python 的特色"),
        MemoryItem("mem_3", "NumPy 用於數值計算"),
        MemoryItem("mem_4", "Pandas 處理表格數據"),
        MemoryItem("mem_5", "Matplotlib 用於數據可視化")
    ]

    for memory in memories:
        hybrid.add_memory(memory)

    # 模擬對話，建立上下文
    conversation = [
        "我想學習 Python",
        "Python 的數據科學庫有哪些？",
        "NumPy 和 Pandas 的區別是什麼？"
    ]

    for msg in conversation:
        print(f"\n[對話] {msg}")
        retriever.update_context(msg)

    # 基於上下文的檢索
    retriever.search("如何使用？", top_k=3)


def main():
    """主函數：運行所有演示"""
    print("\n" + "=" * 70)
    print(" " * 20 + "Letta 記憶檢索策略")
    print("=" * 70)

    # 向量檢索
    demonstrate_vector_retrieval()

    # 關鍵詞檢索
    demonstrate_keyword_retrieval()

    # 混合檢索
    demonstrate_hybrid_retrieval()

    # 上下文感知檢索
    demonstrate_context_aware_retrieval()

    print("\n" + "=" * 70)
    print("記憶檢索演示完成！")
    print("=" * 70)
    print("\n關鍵要點：")
    print("  1. 向量檢索捕捉語義相似性")
    print("  2. 關鍵詞檢索提供精確匹配")
    print("  3. 混合策略結合多種方法的優勢")
    print("  4. 時間和重要性權重提升相關性")
    print("  5. 上下文感知讓檢索更智能")
    print("\n下一步：查看 09_狀態序列化.py")
    print("=" * 70)


if __name__ == "__main__":
    main()

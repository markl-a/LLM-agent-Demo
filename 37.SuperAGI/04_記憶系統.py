"""
SuperAGI 記憶系統示例

這個示例展示了如何:
1. 實現短期記憶
2. 實現長期記憶
3. 向量記憶存儲
4. 記憶檢索和搜索
5. 記憶整合策略

記憶系統是 Agent 智能的重要組成部分。
"""

import os
import json
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import deque
import numpy as np


# ==================== 記憶條目 ====================

class MemoryItem:
    """記憶條目"""

    def __init__(
        self,
        content: str,
        metadata: Dict[str, Any] = None,
        importance: float = 0.5
    ):
        """
        初始化記憶條目

        參數:
            content: 記憶內容
            metadata: 元數據
            importance: 重要性 (0-1)
        """
        self.id = self._generate_id(content)
        self.content = content
        self.metadata = metadata or {}
        self.importance = importance
        self.created_at = datetime.now()
        self.last_accessed = datetime.now()
        self.access_count = 0

    def _generate_id(self, content: str) -> str:
        """生成唯一 ID"""
        return hashlib.md5(
            f"{content}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]

    def access(self):
        """記錄訪問"""
        self.last_accessed = datetime.now()
        self.access_count += 1

    def to_dict(self) -> Dict:
        """轉換為字典"""
        return {
            "id": self.id,
            "content": self.content,
            "metadata": self.metadata,
            "importance": self.importance,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "access_count": self.access_count
        }


# ==================== 短期記憶 ====================

class ShortTermMemory:
    """
    短期記憶

    特點:
    - 容量有限 (通常 50-100 項)
    - 快速訪問
    - 存儲當前會話上下文
    - 自動過期
    """

    def __init__(self, capacity: int = 100):
        """
        初始化短期記憶

        參數:
            capacity: 容量限制
        """
        self.capacity = capacity
        self.memories: deque = deque(maxlen=capacity)
        self.index: Dict[str, MemoryItem] = {}

    def add(self, content: str, metadata: Dict = None, importance: float = 0.5):
        """
        添加記憶

        參數:
            content: 記憶內容
            metadata: 元數據
            importance: 重要性
        """
        memory = MemoryItem(content, metadata, importance)

        # 如果達到容量限制，移除最舊的
        if len(self.memories) >= self.capacity:
            oldest = self.memories[0]
            del self.index[oldest.id]

        self.memories.append(memory)
        self.index[memory.id] = memory

        print(f"📝 添加短期記憶: {content[:50]}...")

    def get_recent(self, n: int = 10) -> List[MemoryItem]:
        """
        獲取最近的記憶

        參數:
            n: 數量

        返回:
            記憶列表
        """
        return list(self.memories)[-n:]

    def search(self, query: str, k: int = 5) -> List[MemoryItem]:
        """
        搜索記憶

        參數:
            query: 查詢字符串
            k: 返回數量

        返回:
            匹配的記憶
        """
        # 簡單的關鍵詞匹配
        matches = []
        for memory in self.memories:
            if query.lower() in memory.content.lower():
                memory.access()
                matches.append(memory)

        return matches[:k]

    def clear(self):
        """清空短期記憶"""
        self.memories.clear()
        self.index.clear()
        print("🗑️  清空短期記憶")

    def get_stats(self) -> Dict:
        """獲取統計信息"""
        return {
            "total": len(self.memories),
            "capacity": self.capacity,
            "usage": len(self.memories) / self.capacity,
            "oldest": self.memories[0].created_at.isoformat() if self.memories else None,
            "newest": self.memories[-1].created_at.isoformat() if self.memories else None
        }


# ==================== 長期記憶 ====================

class LongTermMemory:
    """
    長期記憶

    特點:
    - 容量大
    - 持久化存儲
    - 結構化索引
    - 重要性評分
    """

    def __init__(self):
        """初始化長期記憶"""
        self.memories: Dict[str, MemoryItem] = {}
        self.categories: Dict[str, List[str]] = {}  # 分類索引
        self.tags: Dict[str, List[str]] = {}  # 標籤索引

    def add(
        self,
        content: str,
        metadata: Dict = None,
        importance: float = 0.5,
        category: str = "general",
        tags: List[str] = None
    ):
        """
        添加記憶

        參數:
            content: 記憶內容
            metadata: 元數據
            importance: 重要性
            category: 分類
            tags: 標籤
        """
        memory = MemoryItem(content, metadata, importance)

        self.memories[memory.id] = memory

        # 添加到分類索引
        if category not in self.categories:
            self.categories[category] = []
        self.categories[category].append(memory.id)

        # 添加到標籤索引
        if tags:
            for tag in tags:
                if tag not in self.tags:
                    self.tags[tag] = []
                self.tags[tag].append(memory.id)

        print(f"💾 添加長期記憶: {content[:50]}... (分類: {category})")

    def get(self, memory_id: str) -> Optional[MemoryItem]:
        """獲取指定記憶"""
        memory = self.memories.get(memory_id)
        if memory:
            memory.access()
        return memory

    def search_by_category(self, category: str) -> List[MemoryItem]:
        """按分類搜索"""
        memory_ids = self.categories.get(category, [])
        return [self.memories[mid] for mid in memory_ids]

    def search_by_tag(self, tag: str) -> List[MemoryItem]:
        """按標籤搜索"""
        memory_ids = self.tags.get(tag, [])
        return [self.memories[mid] for mid in memory_ids]

    def search_by_importance(
        self,
        min_importance: float = 0.7
    ) -> List[MemoryItem]:
        """按重要性搜索"""
        return [
            memory for memory in self.memories.values()
            if memory.importance >= min_importance
        ]

    def search(self, query: str, k: int = 10) -> List[MemoryItem]:
        """
        全文搜索

        參數:
            query: 查詢字符串
            k: 返回數量

        返回:
            匹配的記憶
        """
        matches = []
        for memory in self.memories.values():
            if query.lower() in memory.content.lower():
                memory.access()
                matches.append((memory, memory.importance * (1 + memory.access_count * 0.1)))

        # 按重要性和訪問次數排序
        matches.sort(key=lambda x: x[1], reverse=True)

        return [m[0] for m in matches[:k]]

    def consolidate(self, short_term: ShortTermMemory, threshold: float = 0.6):
        """
        從短期記憶整合到長期記憶

        參數:
            short_term: 短期記憶實例
            threshold: 重要性閾值
        """
        print("\n🔄 整合記憶...")

        consolidated = 0
        for memory in short_term.memories:
            if memory.importance >= threshold:
                self.add(
                    content=memory.content,
                    metadata=memory.metadata,
                    importance=memory.importance,
                    category=memory.metadata.get("category", "general"),
                    tags=memory.metadata.get("tags", [])
                )
                consolidated += 1

        print(f"✅ 整合了 {consolidated} 條記憶到長期記憶")

    def get_stats(self) -> Dict:
        """獲取統計信息"""
        return {
            "total": len(self.memories),
            "categories": len(self.categories),
            "tags": len(self.tags),
            "avg_importance": (
                sum(m.importance for m in self.memories.values()) / len(self.memories)
                if self.memories else 0
            ),
            "most_accessed": max(
                self.memories.values(),
                key=lambda m: m.access_count
            ).to_dict() if self.memories else None
        }


# ==================== 向量記憶 ====================

class VectorMemory:
    """
    向量記憶

    特點:
    - 語義搜索
    - 相似度匹配
    - 高維向量存儲
    """

    def __init__(self, dimension: int = 768):
        """
        初始化向量記憶

        參數:
            dimension: 向量維度
        """
        self.dimension = dimension
        self.memories: Dict[str, MemoryItem] = {}
        self.embeddings: Dict[str, np.ndarray] = {}

    def _generate_embedding(self, text: str) -> np.ndarray:
        """
        生成文本嵌入（模擬）

        實際應使用: OpenAI embeddings, sentence-transformers 等

        參數:
            text: 文本

        返回:
            向量嵌入
        """
        # 簡單的模擬嵌入（實際應使用真實的嵌入模型）
        np.random.seed(hash(text) % (2**32))
        return np.random.randn(self.dimension)

    def add(
        self,
        content: str,
        metadata: Dict = None,
        importance: float = 0.5
    ):
        """
        添加記憶

        參數:
            content: 記憶內容
            metadata: 元數據
            importance: 重要性
        """
        memory = MemoryItem(content, metadata, importance)

        # 生成嵌入
        embedding = self._generate_embedding(content)

        self.memories[memory.id] = memory
        self.embeddings[memory.id] = embedding

        print(f"🔢 添加向量記憶: {content[:50]}...")

    def search(
        self,
        query: str,
        k: int = 5,
        threshold: float = 0.7
    ) -> List[tuple[MemoryItem, float]]:
        """
        語義搜索

        參數:
            query: 查詢文本
            k: 返回數量
            threshold: 相似度閾值

        返回:
            (記憶, 相似度) 列表
        """
        # 生成查詢嵌入
        query_embedding = self._generate_embedding(query)

        # 計算相似度
        similarities = []
        for memory_id, memory_embedding in self.embeddings.items():
            similarity = self._cosine_similarity(query_embedding, memory_embedding)

            if similarity >= threshold:
                memory = self.memories[memory_id]
                memory.access()
                similarities.append((memory, similarity))

        # 按相似度排序
        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities[:k]

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """
        計算餘弦相似度

        參數:
            a: 向量 A
            b: 向量 B

        返回:
            相似度
        """
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    def find_similar(
        self,
        memory_id: str,
        k: int = 5
    ) -> List[tuple[MemoryItem, float]]:
        """
        查找相似記憶

        參數:
            memory_id: 記憶 ID
            k: 返回數量

        返回:
            相似記憶列表
        """
        if memory_id not in self.embeddings:
            return []

        target_embedding = self.embeddings[memory_id]

        similarities = []
        for mid, embedding in self.embeddings.items():
            if mid != memory_id:
                similarity = self._cosine_similarity(target_embedding, embedding)
                similarities.append((self.memories[mid], similarity))

        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities[:k]

    def get_stats(self) -> Dict:
        """獲取統計信息"""
        return {
            "total": len(self.memories),
            "dimension": self.dimension,
            "storage_size": len(self.embeddings) * self.dimension * 8  # bytes
        }


# ==================== 記憶管理器 ====================

class MemoryManager:
    """
    記憶管理器

    整合短期、長期和向量記憶
    """

    def __init__(self):
        """初始化記憶管理器"""
        self.short_term = ShortTermMemory(capacity=100)
        self.long_term = LongTermMemory()
        self.vector = VectorMemory()

        self.consolidation_threshold = 0.6
        self.auto_consolidate = True

    def add_memory(
        self,
        content: str,
        metadata: Dict = None,
        importance: float = 0.5,
        category: str = "general",
        tags: List[str] = None
    ):
        """
        添加記憶（自動分配到不同存儲）

        參數:
            content: 記憶內容
            metadata: 元數據
            importance: 重要性
            category: 分類
            tags: 標籤
        """
        # 添加到短期記憶
        self.short_term.add(content, metadata, importance)

        # 如果重要，也添加到長期記憶
        if importance >= self.consolidation_threshold:
            self.long_term.add(content, metadata, importance, category, tags)

        # 添加到向量記憶
        self.vector.add(content, metadata, importance)

        # 檢查是否需要整合
        if self.auto_consolidate and len(self.short_term.memories) >= 80:
            self.consolidate()

    def search(
        self,
        query: str,
        search_type: str = "hybrid",
        k: int = 10
    ) -> List[MemoryItem]:
        """
        搜索記憶

        參數:
            query: 查詢
            search_type: 搜索類型 (keyword/semantic/hybrid)
            k: 返回數量

        返回:
            記憶列表
        """
        if search_type == "keyword":
            # 關鍵詞搜索
            short_results = self.short_term.search(query, k)
            long_results = self.long_term.search(query, k)
            return short_results + long_results

        elif search_type == "semantic":
            # 語義搜索
            vector_results = self.vector.search(query, k)
            return [m for m, _ in vector_results]

        else:  # hybrid
            # 混合搜索
            keyword_results = set()
            for m in self.short_term.search(query, k):
                keyword_results.add(m.id)
            for m in self.long_term.search(query, k):
                keyword_results.add(m.id)

            semantic_results = self.vector.search(query, k)

            # 合併結果
            all_memories = {}
            for m in self.short_term.memories:
                if m.id in keyword_results:
                    all_memories[m.id] = m

            for m in self.long_term.memories.values():
                if m.id in keyword_results:
                    all_memories[m.id] = m

            for m, score in semantic_results:
                all_memories[m.id] = m

            return list(all_memories.values())[:k]

    def consolidate(self):
        """整合記憶"""
        self.long_term.consolidate(self.short_term, self.consolidation_threshold)

    def get_context(self, query: str, max_tokens: int = 1000) -> str:
        """
        獲取相關上下文

        參數:
            query: 查詢
            max_tokens: 最大 token 數

        返回:
            上下文文本
        """
        # 獲取相關記憶
        memories = self.search(query, search_type="hybrid", k=10)

        # 構建上下文
        context_parts = []
        total_length = 0

        for memory in memories:
            content = memory.content
            if total_length + len(content) > max_tokens:
                break

            context_parts.append(content)
            total_length += len(content)

        return "\n\n".join(context_parts)

    def get_summary(self) -> Dict:
        """獲取記憶系統摘要"""
        return {
            "short_term": self.short_term.get_stats(),
            "long_term": self.long_term.get_stats(),
            "vector": self.vector.get_stats()
        }


# ==================== 示例場景 ====================

def example_1_short_term_memory():
    """示例 1: 短期記憶"""
    print("\n" + "=" * 60)
    print("示例 1: 短期記憶使用")
    print("=" * 60)

    stm = ShortTermMemory(capacity=10)

    # 添加記憶
    stm.add("用戶詢問關於 AI 的問題", importance=0.5)
    stm.add("Agent 回答了 AI 的定義", importance=0.6)
    stm.add("用戶要求提供示例", importance=0.7)
    stm.add("Agent 提供了 3 個示例", importance=0.8)

    # 獲取最近記憶
    recent = stm.get_recent(3)
    print("\n最近 3 條記憶:")
    for memory in recent:
        print(f"  - {memory.content}")

    # 搜索
    results = stm.search("示例")
    print(f"\n搜索 '示例' 的結果:")
    for memory in results:
        print(f"  - {memory.content}")

    # 統計
    print(f"\n統計信息:")
    print(json.dumps(stm.get_stats(), indent=2, ensure_ascii=False))


def example_2_long_term_memory():
    """示例 2: 長期記憶"""
    print("\n" + "=" * 60)
    print("示例 2: 長期記憶使用")
    print("=" * 60)

    ltm = LongTermMemory()

    # 添加不同分類的記憶
    ltm.add(
        "Python 是一種高級編程語言",
        importance=0.8,
        category="knowledge",
        tags=["python", "programming"]
    )

    ltm.add(
        "用戶偏好使用深色主題",
        importance=0.7,
        category="preference",
        tags=["user", "ui"]
    )

    ltm.add(
        "上次任務執行成功",
        importance=0.6,
        category="history",
        tags=["task", "success"]
    )

    # 按分類搜索
    knowledge = ltm.search_by_category("knowledge")
    print(f"\n知識類記憶:")
    for memory in knowledge:
        print(f"  - {memory.content}")

    # 按標籤搜索
    python_memories = ltm.search_by_tag("python")
    print(f"\nPython 相關記憶:")
    for memory in python_memories:
        print(f"  - {memory.content}")

    # 按重要性搜索
    important = ltm.search_by_importance(0.7)
    print(f"\n高重要性記憶 (>= 0.7):")
    for memory in important:
        print(f"  - {memory.content} (重要性: {memory.importance})")


def example_3_vector_memory():
    """示例 3: 向量記憶"""
    print("\n" + "=" * 60)
    print("示例 3: 向量記憶和語義搜索")
    print("=" * 60)

    vm = VectorMemory()

    # 添加相關記憶
    vm.add("機器學習是人工智能的一個分支")
    vm.add("深度學習使用神經網絡")
    vm.add("自然語言處理處理文本數據")
    vm.add("計算機視覺處理圖像")
    vm.add("今天天氣很好")

    # 語義搜索
    print("\n搜索: '神經網絡和AI'")
    results = vm.search("神經網絡和AI", k=3)
    for memory, similarity in results:
        print(f"  相似度 {similarity:.3f}: {memory.content}")

    # 查找相似記憶
    if results:
        first_memory_id = results[0][0].id
        print(f"\n查找相似記憶:")
        similar = vm.find_similar(first_memory_id, k=2)
        for memory, similarity in similar:
            print(f"  相似度 {similarity:.3f}: {memory.content}")


def example_4_memory_manager():
    """示例 4: 記憶管理器"""
    print("\n" + "=" * 60)
    print("示例 4: 統一記憶管理")
    print("=" * 60)

    manager = MemoryManager()

    # 添加各種記憶
    manager.add_memory(
        "用戶要求分析銷售數據",
        importance=0.9,
        category="task",
        tags=["sales", "analysis"]
    )

    manager.add_memory(
        "數據來源是 sales.csv 文件",
        importance=0.7,
        category="context",
        tags=["sales", "data"]
    )

    manager.add_memory(
        "分析完成，發現銷售增長 20%",
        importance=0.8,
        category="result",
        tags=["sales", "result"]
    )

    # 混合搜索
    print("\n搜索 '銷售分析':")
    results = manager.search("銷售分析", search_type="hybrid", k=5)
    for memory in results:
        print(f"  - {memory.content}")

    # 獲取上下文
    print("\n獲取相關上下文:")
    context = manager.get_context("銷售增長", max_tokens=500)
    print(context)

    # 系統摘要
    print("\n記憶系統摘要:")
    summary = manager.get_summary()
    print(json.dumps(summary, indent=2, ensure_ascii=False))


def example_5_consolidation():
    """示例 5: 記憶整合"""
    print("\n" + "=" * 60)
    print("示例 5: 短期到長期記憶整合")
    print("=" * 60)

    stm = ShortTermMemory()
    ltm = LongTermMemory()

    # 添加多條短期記憶
    memories = [
        ("重要的發現：AI 可以提高效率", 0.9),
        ("臨時筆記：測試數據", 0.3),
        ("用戶反饋：系統響應快速", 0.8),
        ("調試信息：變量 x = 5", 0.2),
        ("關鍵洞察：需要優化算法", 0.9)
    ]

    for content, importance in memories:
        stm.add(content, importance=importance)

    print(f"短期記憶數量: {len(stm.memories)}")

    # 整合到長期記憶
    ltm.consolidate(stm, threshold=0.7)

    print(f"長期記憶數量: {len(ltm.memories)}")

    print("\n長期記憶內容:")
    for memory in ltm.memories.values():
        print(f"  - {memory.content} (重要性: {memory.importance})")


# ==================== 主函數 ====================

def main():
    """主函數"""
    print("\n" + "🧠 " * 20)
    print("SuperAGI 記憶系統教程")
    print("🧠 " * 20)

    try:
        # 示例 1: 短期記憶
        example_1_short_term_memory()

        # 示例 2: 長期記憶
        example_2_long_term_memory()

        # 示例 3: 向量記憶
        example_3_vector_memory()

        # 示例 4: 記憶管理器
        example_4_memory_manager()

        # 示例 5: 記憶整合
        example_5_consolidation()

        print("\n" + "=" * 60)
        print("✅ 所有記憶系統示例執行完成！")
        print("=" * 60)

        print("""
        記憶系統最佳實踐:

        1. 合理設置短期記憶容量
        2. 根據重要性整合記憶
        3. 使用向量搜索提高檢索質量
        4. 定期清理低價值記憶
        5. 為記憶添加結構化元數據
        6. 實現增量學習機制
        """)

    except Exception as e:
        print(f"\n❌ 執行出錯: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

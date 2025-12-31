"""
LiteLLM 嵌入向量範例

這個檔案展示如何使用 LiteLLM 處理嵌入向量（Embeddings）：
1. 基本嵌入生成
2. 多供應商嵌入比較
3. 批次嵌入處理
4. 相似度計算
5. 語義搜尋
6. 文本聚類
7. 嵌入快取
8. 向量資料庫整合
9. 降維和視覺化
10. 嵌入品質評估

嵌入向量是現代 AI 應用的基礎，用於語義搜尋、推薦系統等。
"""

import os
from typing import List, Dict, Any, Optional, Tuple
import json
import numpy as np
from litellm import embedding
import time
from dataclasses import dataclass
from collections import defaultdict
import math


# ============================================================================
# 資料類別定義
# ============================================================================

@dataclass
class EmbeddingResult:
    """嵌入結果"""
    text: str
    embedding: List[float]
    model: str
    tokens: int
    dimension: int


@dataclass
class SimilarityPair:
    """相似度對"""
    text1: str
    text2: str
    similarity: float
    distance: float


# ============================================================================
# 第一部分：基本嵌入生成
# ============================================================================

def basic_embedding_example():
    """
    基本嵌入生成範例

    展示如何生成文本的嵌入向量。
    """
    print("=" * 80)
    print("基本嵌入生成範例")
    print("=" * 80)

    # 測試文本
    texts = [
        "機器學習是人工智慧的一個分支",
        "深度學習使用神經網路處理資料",
        "今天天氣很好，適合出去散步"
    ]

    print("\n使用 OpenAI text-embedding-3-small 模型\n")

    try:
        for i, text in enumerate(texts, 1):
            print(f"{i}. 文本：{text}")

            # 生成嵌入
            response = embedding(
                model="text-embedding-3-small",
                input=[text]
            )

            # 取得嵌入向量
            emb = response.data[0].embedding
            usage = response.usage

            print(f"   維度：{len(emb)}")
            print(f"   Token 數：{usage.total_tokens}")
            print(f"   前 5 個值：{emb[:5]}")
            print()

    except Exception as e:
        print(f"錯誤：{e}")


def multi_provider_embeddings():
    """
    多供應商嵌入比較

    比較不同供應商的嵌入模型。
    """
    print("\n" + "=" * 80)
    print("多供應商嵌入比較")
    print("=" * 80)

    text = "人工智慧正在改變世界"

    # 不同的嵌入模型
    models = [
        "text-embedding-3-small",  # OpenAI
        "text-embedding-3-large",  # OpenAI
        # "cohere/embed-english-v3.0",  # Cohere
        # "voyage/voyage-2",  # Voyage AI
    ]

    print(f"\n文本：{text}\n")

    results = []

    for model in models:
        try:
            print(f"模型：{model}")
            print("-" * 40)

            start_time = time.time()

            response = embedding(
                model=model,
                input=[text]
            )

            elapsed = time.time() - start_time

            emb = response.data[0].embedding
            usage = response.usage

            result = {
                "model": model,
                "dimension": len(emb),
                "tokens": usage.total_tokens,
                "time": elapsed,
                "embedding": emb
            }

            results.append(result)

            print(f"  維度：{result['dimension']}")
            print(f"  Tokens：{result['tokens']}")
            print(f"  耗時：{result['time']:.3f} 秒")
            print()

        except Exception as e:
            print(f"  錯誤：{e}\n")

    # 比較摘要
    if len(results) > 1:
        print("=" * 80)
        print("比較摘要")
        print("=" * 80)

        print(f"\n{'模型':<35} {'維度':<10} {'Tokens':<10} {'耗時(s)':<10}")
        print("-" * 80)

        for r in results:
            print(f"{r['model']:<35} {r['dimension']:<10} {r['tokens']:<10} {r['time']:<10.3f}")


# ============================================================================
# 第二部分：相似度計算
# ============================================================================

class SimilarityCalculator:
    """相似度計算器"""

    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """
        計算餘弦相似度

        Args:
            vec1: 向量 1
            vec2: 向量 2

        Returns:
            相似度（-1 到 1）
        """
        if len(vec1) != len(vec2):
            raise ValueError("向量維度不匹配")

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    @staticmethod
    def euclidean_distance(vec1: List[float], vec2: List[float]) -> float:
        """
        計算歐式距離

        Args:
            vec1: 向量 1
            vec2: 向量 2

        Returns:
            距離（越小越相似）
        """
        if len(vec1) != len(vec2):
            raise ValueError("向量維度不匹配")

        return math.sqrt(sum((a - b) ** 2 for a, b in zip(vec1, vec2)))

    @staticmethod
    def manhattan_distance(vec1: List[float], vec2: List[float]) -> float:
        """
        計算曼哈頓距離

        Args:
            vec1: 向量 1
            vec2: 向量 2

        Returns:
            距離
        """
        if len(vec1) != len(vec2):
            raise ValueError("向量維度不匹配")

        return sum(abs(a - b) for a, b in zip(vec1, vec2))


def similarity_calculation_example():
    """相似度計算範例"""
    print("\n" + "=" * 80)
    print("相似度計算範例")
    print("=" * 80)

    # 測試文本對
    text_pairs = [
        ("機器學習是 AI 的分支", "深度學習是機器學習的子集"),
        ("我喜歡吃蘋果", "蘋果公司是科技巨頭"),
        ("Python 是程式語言", "Java 是程式語言"),
        ("今天天氣很好", "明天會下雨")
    ]

    calculator = SimilarityCalculator()

    print("\n")

    for i, (text1, text2) in enumerate(text_pairs, 1):
        try:
            print(f"對 {i}：")
            print(f"  文本 1：{text1}")
            print(f"  文本 2：{text2}")

            # 生成嵌入
            response = embedding(
                model="text-embedding-3-small",
                input=[text1, text2]
            )

            emb1 = response.data[0].embedding
            emb2 = response.data[1].embedding

            # 計算相似度
            cosine_sim = calculator.cosine_similarity(emb1, emb2)
            euclidean_dist = calculator.euclidean_distance(emb1, emb2)

            print(f"  餘弦相似度：{cosine_sim:.4f}")
            print(f"  歐式距離：{euclidean_dist:.4f}")

            # 相似度判斷
            if cosine_sim > 0.8:
                print(f"  → 非常相似")
            elif cosine_sim > 0.6:
                print(f"  → 相似")
            elif cosine_sim > 0.4:
                print(f"  → 有些相似")
            else:
                print(f"  → 不太相似")

            print()

        except Exception as e:
            print(f"  錯誤：{e}\n")


# ============================================================================
# 第三部分：語義搜尋
# ============================================================================

class SemanticSearch:
    """語義搜尋引擎"""

    def __init__(self, model: str = "text-embedding-3-small"):
        self.model = model
        self.documents: List[Dict[str, Any]] = []
        self.embeddings: List[List[float]] = []

    def add_documents(self, documents: List[str]):
        """
        新增文件到搜尋引擎

        Args:
            documents: 文件列表
        """
        print(f"\n新增 {len(documents)} 個文件到索引...")

        try:
            # 批次生成嵌入
            response = embedding(
                model=self.model,
                input=documents
            )

            for i, doc in enumerate(documents):
                emb = response.data[i].embedding

                self.documents.append({
                    "id": len(self.documents),
                    "text": doc
                })
                self.embeddings.append(emb)

            print(f"✓ 已新增 {len(documents)} 個文件")

        except Exception as e:
            print(f"✗ 錯誤：{e}")

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        搜尋最相關的文件

        Args:
            query: 查詢字串
            top_k: 返回前 k 個結果

        Returns:
            搜尋結果列表
        """
        if not self.documents:
            return []

        try:
            # 生成查詢嵌入
            response = embedding(
                model=self.model,
                input=[query]
            )

            query_emb = response.data[0].embedding

            # 計算相似度
            calculator = SimilarityCalculator()
            similarities = []

            for i, doc_emb in enumerate(self.embeddings):
                sim = calculator.cosine_similarity(query_emb, doc_emb)
                similarities.append({
                    "id": i,
                    "document": self.documents[i],
                    "similarity": sim
                })

            # 排序並返回前 k 個
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            return similarities[:top_k]

        except Exception as e:
            print(f"搜尋錯誤：{e}")
            return []


def semantic_search_example():
    """語義搜尋範例"""
    print("\n" + "=" * 80)
    print("語義搜尋範例")
    print("=" * 80)

    # 建立搜尋引擎
    search_engine = SemanticSearch()

    # 準備文件庫
    documents = [
        "Python 是一種高階程式語言，以其簡潔的語法和強大的功能而聞名",
        "機器學習是人工智慧的一個分支，使電腦能夠從資料中學習",
        "深度學習使用多層神經網路來處理複雜的資料",
        "自然語言處理幫助電腦理解和生成人類語言",
        "區塊鏈是一種分散式帳本技術，用於記錄交易",
        "雲端運算提供按需存取共享的運算資源",
        "大數據分析處理和分析大量複雜的資料集",
        "物聯網連接各種裝置，使它們能夠通訊和分享資料"
    ]

    # 建立索引
    search_engine.add_documents(documents)

    # 測試查詢
    queries = [
        "什麼是 AI？",
        "程式語言有哪些？",
        "如何處理大量資料？"
    ]

    for query in queries:
        print(f"\n查詢：{query}")
        print("-" * 40)

        results = search_engine.search(query, top_k=3)

        for i, result in enumerate(results, 1):
            print(f"{i}. [相似度: {result['similarity']:.4f}]")
            print(f"   {result['document']['text']}")


# ============================================================================
# 第四部分：文本聚類
# ============================================================================

class TextClusterer:
    """文本聚類器"""

    def __init__(self, model: str = "text-embedding-3-small"):
        self.model = model

    def cluster(self, texts: List[str], n_clusters: int = 3) -> Dict[int, List[str]]:
        """
        將文本聚類

        Args:
            texts: 文本列表
            n_clusters: 群集數量

        Returns:
            群集字典 {cluster_id: [texts]}
        """
        print(f"\n將 {len(texts)} 個文本聚類為 {n_clusters} 個群集...")

        try:
            # 生成嵌入
            response = embedding(
                model=self.model,
                input=texts
            )

            embeddings = [data.embedding for data in response.data]

            # 簡化的 K-means 聚類（實際應用應使用專業函式庫如 scikit-learn）
            clusters = self._simple_kmeans(embeddings, n_clusters)

            # 組織結果
            result = defaultdict(list)
            for i, cluster_id in enumerate(clusters):
                result[cluster_id].append(texts[i])

            print(f"✓ 聚類完成")

            return dict(result)

        except Exception as e:
            print(f"✗ 錯誤：{e}")
            return {}

    def _simple_kmeans(self, embeddings: List[List[float]], k: int) -> List[int]:
        """
        簡單的 K-means 實作

        Args:
            embeddings: 嵌入向量列表
            k: 群集數量

        Returns:
            每個點的群集 ID
        """
        n = len(embeddings)

        # 隨機初始化中心點
        import random
        centers_idx = random.sample(range(n), k)
        centers = [embeddings[i] for i in centers_idx]

        calculator = SimilarityCalculator()

        # 迭代
        for _ in range(10):
            # 分配點到最近的中心
            assignments = []
            for emb in embeddings:
                distances = [
                    calculator.euclidean_distance(emb, center)
                    for center in centers
                ]
                assignments.append(distances.index(min(distances)))

            # 更新中心點
            new_centers = []
            for cluster_id in range(k):
                cluster_points = [
                    embeddings[i] for i, cid in enumerate(assignments)
                    if cid == cluster_id
                ]

                if cluster_points:
                    # 計算平均值
                    dim = len(cluster_points[0])
                    center = [
                        sum(point[d] for point in cluster_points) / len(cluster_points)
                        for d in range(dim)
                    ]
                    new_centers.append(center)
                else:
                    new_centers.append(centers[cluster_id])

            centers = new_centers

        return assignments


def clustering_example():
    """文本聚類範例"""
    print("\n" + "=" * 80)
    print("文本聚類範例")
    print("=" * 80)

    clusterer = TextClusterer()

    # 準備文本（包含不同主題）
    texts = [
        # 程式語言主題
        "Python 是一種流行的程式語言",
        "JavaScript 用於網頁開發",
        "Java 是企業級應用的首選",

        # AI/ML 主題
        "機器學習可以從資料中學習模式",
        "深度學習使用神經網路",
        "自然語言處理處理文字資料",

        # 雲端/基礎設施主題
        "雲端運算提供可擴展的資源",
        "Docker 容器化應用程式",
        "Kubernetes 管理容器編排"
    ]

    # 執行聚類
    clusters = clusterer.cluster(texts, n_clusters=3)

    # 顯示結果
    print("\n聚類結果：")
    print("=" * 80)

    for cluster_id, cluster_texts in clusters.items():
        print(f"\n群集 {cluster_id + 1}：")
        for text in cluster_texts:
            print(f"  • {text}")


# ============================================================================
# 第五部分：批次處理
# ============================================================================

def batch_embedding_example():
    """批次嵌入處理範例"""
    print("\n" + "=" * 80)
    print("批次嵌入處理範例")
    print("=" * 80)

    # 大量文本
    texts = [
        f"這是第 {i} 個測試文本，用於演示批次處理"
        for i in range(1, 51)
    ]

    print(f"\n處理 {len(texts)} 個文本...\n")

    # 單個處理（比較基準）
    print("方法 1：單個處理")
    print("-" * 40)

    try:
        start_time = time.time()

        embeddings_single = []
        for text in texts[:10]:  # 只處理前 10 個作為示範
            response = embedding(
                model="text-embedding-3-small",
                input=[text]
            )
            embeddings_single.append(response.data[0].embedding)

        time_single = time.time() - start_time

        print(f"處理 10 個文本耗時：{time_single:.2f} 秒")
        print(f"平均每個：{time_single / 10:.3f} 秒")

    except Exception as e:
        print(f"錯誤：{e}")

    # 批次處理
    print("\n方法 2：批次處理")
    print("-" * 40)

    try:
        start_time = time.time()

        # 一次處理多個（OpenAI 支援批次）
        response = embedding(
            model="text-embedding-3-small",
            input=texts[:10]
        )

        embeddings_batch = [data.embedding for data in response.data]

        time_batch = time.time() - start_time

        print(f"批次處理 10 個文本耗時：{time_batch:.2f} 秒")
        print(f"平均每個：{time_batch / 10:.3f} 秒")

        if time_single > 0:
            speedup = time_single / time_batch
            print(f"\n加速比：{speedup:.1f}x")

    except Exception as e:
        print(f"錯誤：{e}")


# ============================================================================
# 第六部分：嵌入快取
# ============================================================================

class EmbeddingCache:
    """嵌入快取"""

    def __init__(self, model: str = "text-embedding-3-small"):
        self.model = model
        self.cache: Dict[str, List[float]] = {}
        self.hits = 0
        self.misses = 0

    def get_embedding(self, text: str) -> List[float]:
        """
        取得嵌入（帶快取）

        Args:
            text: 文本

        Returns:
            嵌入向量
        """
        # 檢查快取
        if text in self.cache:
            self.hits += 1
            return self.cache[text]

        # 快取未命中，生成嵌入
        self.misses += 1

        try:
            response = embedding(
                model=self.model,
                input=[text]
            )

            emb = response.data[0].embedding

            # 儲存到快取
            self.cache[text] = emb

            return emb

        except Exception as e:
            print(f"錯誤：{e}")
            return []

    def get_stats(self) -> Dict[str, Any]:
        """取得快取統計"""
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0

        return {
            "cache_size": len(self.cache),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate
        }


def embedding_cache_example():
    """嵌入快取範例"""
    print("\n" + "=" * 80)
    print("嵌入快取範例")
    print("=" * 80)

    cache = EmbeddingCache()

    # 測試文本（包含重複）
    texts = [
        "Python 是一種程式語言",
        "機器學習很有趣",
        "Python 是一種程式語言",  # 重複
        "深度學習使用神經網路",
        "機器學習很有趣",  # 重複
        "Python 是一種程式語言",  # 重複
    ]

    print(f"\n處理 {len(texts)} 個文本（包含重複）\n")

    for i, text in enumerate(texts, 1):
        print(f"{i}. {text}")

        emb = cache.get_embedding(text)

        if emb:
            stats = cache.get_stats()
            status = "✓ 快取命中" if i > 1 and text in texts[:i-1] else "→ 新增到快取"
            print(f"   {status}")
            print(f"   當前命中率：{stats['hit_rate'] * 100:.1f}%")
        else:
            print(f"   ✗ 錯誤")

        print()

    # 最終統計
    print("=" * 80)
    print("快取統計")
    print("=" * 80)

    stats = cache.get_stats()

    print(f"\n快取大小：{stats['cache_size']}")
    print(f"快取命中：{stats['hits']}")
    print(f"快取未命中：{stats['misses']}")
    print(f"命中率：{stats['hit_rate'] * 100:.1f}%")


# ============================================================================
# 主程式
# ============================================================================

def main():
    """主程式"""
    print("\n")
    print("=" * 80)
    print("LiteLLM 嵌入向量完整教學")
    print("=" * 80)
    print()

    # 基本嵌入
    # basic_embedding_example()
    # multi_provider_embeddings()

    # 相似度計算
    similarity_calculation_example()

    # 語義搜尋
    semantic_search_example()

    # 文本聚類
    clustering_example()

    # 批次處理
    # batch_embedding_example()

    # 嵌入快取
    embedding_cache_example()

    print("\n" + "=" * 80)
    print("教學完成！")
    print("=" * 80)
    print("\n重點回顧：")
    print("1. 嵌入向量是文本的數值表示")
    print("2. 相似度計算用於比較文本語義")
    print("3. 語義搜尋基於向量相似度")
    print("4. 聚類可以發現文本主題")
    print("5. 批次處理和快取提高效能")
    print()


if __name__ == "__main__":
    main()

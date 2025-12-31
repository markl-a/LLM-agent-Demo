"""
Txtai - 語義搜索進階範例

本範例展示：
1. 高級語義搜索技術
2. 混合搜索（語義 + BM25）
3. 搜索過濾和排序
4. 批量搜索優化
5. 相似度計算

安裝：pip install txtai sentence-transformers
"""

from txtai import Embeddings, Similarity
import time


# ============================================================================
# 範例 1: 純語義搜索 vs 關鍵詞搜索
# ============================================================================

def example_1_semantic_vs_keyword():
    """比較語義搜索和關鍵詞搜索的差異"""
    print("\n" + "="*60)
    print("範例 1: 語義搜索 vs 關鍵詞搜索")
    print("="*60)

    embeddings = Embeddings({"content": True})

    documents = [
        "A canine is running through the park",
        "A dog is playing in the garden",
        "The feline is sleeping on the couch",
        "A cat is resting on the sofa",
        "Birds are flying in the sky"
    ]

    embeddings.index([(i, doc, None) for i, doc in enumerate(documents)])

    # 語義搜索 - 即使沒有完全匹配的詞也能找到相關結果
    query = "dog playing outside"
    results = embeddings.search(query, limit=3)

    print(f"查詢：'{query}'")
    print("\n語義搜索結果（理解同義詞和上下文）：")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['text']}")
        print(f"   評分: {result['score']:.4f}")
        print()


# ============================================================================
# 範例 2: 混合搜索（語義 + BM25）
# ============================================================================

def example_2_hybrid_search():
    """結合語義搜索和 BM25 關鍵詞搜索"""
    print("\n" + "="*60)
    print("範例 2: 混合搜索")
    print("="*60)

    # 啟用 BM25 評分
    config = {
        "content": True,
        "scoring": {
            "method": "bm25",
            "terms": True
        }
    }

    embeddings = Embeddings(config)

    documents = [
        "Python programming language tutorial",
        "Learn Python for data science",
        "JavaScript web development guide",
        "Python machine learning applications",
        "Java enterprise programming"
    ]

    embeddings.index([(i, doc, None) for i, doc in enumerate(documents)])

    query = "Python programming"

    # 純語義搜索（weights=0.0）
    print(f"查詢：'{query}'")
    print("\n1. 純語義搜索（weights=0.0）：")
    results = embeddings.search(query, limit=3, weights=0.0)
    for result in results:
        print(f"   - {result['text']} (評分: {result['score']:.4f})")

    # 混合搜索（weights=0.5）
    print("\n2. 混合搜索（weights=0.5）：")
    results = embeddings.search(query, limit=3, weights=0.5)
    for result in results:
        print(f"   - {result['text']} (評分: {result['score']:.4f})")

    # 純 BM25 搜索（weights=1.0）
    print("\n3. 純 BM25 搜索（weights=1.0）：")
    results = embeddings.search(query, limit=3, weights=1.0)
    for result in results:
        print(f"   - {result['text']} (評分: {result['score']:.4f})")


# ============================================================================
# 範例 3: 批量搜索優化
# ============================================================================

def example_3_batch_search():
    """高效執行批量搜索"""
    print("\n" + "="*60)
    print("範例 3: 批量搜索優化")
    print("="*60)

    embeddings = Embeddings()

    # 創建較大的文檔集
    documents = [
        f"Document about {topic} number {i}"
        for i, topic in enumerate([
            "machine learning", "data science", "web development",
            "cloud computing", "cybersecurity", "blockchain",
            "artificial intelligence", "DevOps", "mobile development",
            "database systems"
        ] * 5)
    ]

    embeddings.index([(i, doc, None) for i, doc in enumerate(documents)])
    print(f"✓ 已索引 {len(documents)} 個文檔")

    # 批量查詢
    queries = [
        "AI and machine learning",
        "web and mobile apps",
        "cloud infrastructure",
        "data storage systems"
    ]

    start_time = time.time()

    print("\n批量搜索結果：")
    for query in queries:
        results = embeddings.search(query, limit=2)
        print(f"\n查詢：'{query}'")
        for result in results:
            print(f"  → {result['text'][:40]}... (評分: {result['score']:.4f})")

    elapsed_time = time.time() - start_time
    print(f"\n批量搜索耗時: {elapsed_time:.3f} 秒")
    print(f"平均每個查詢: {elapsed_time/len(queries):.3f} 秒")


# ============================================================================
# 範例 4: 文本相似度計算
# ============================================================================

def example_4_similarity_calculation():
    """計算文本之間的相似度"""
    print("\n" + "="*60)
    print("範例 4: 文本相似度計算")
    print("="*60)

    # 使用 Similarity 管道
    similarity = Similarity()

    texts = [
        ("The weather is beautiful today", "It's a lovely day outside"),
        ("Machine learning is a subset of AI", "ML is part of artificial intelligence"),
        ("I love pizza", "The weather is cold"),
        ("Python is a programming language", "JavaScript is used for web development")
    ]

    print("文本對相似度：")
    for text1, text2 in texts:
        score = similarity(text1, text2)
        print(f"\n文本1: {text1}")
        print(f"文本2: {text2}")
        print(f"相似度: {score:.4f}")


# ============================================================================
# 範例 5: 多語言語義搜索
# ============================================================================

def example_5_multilingual_search():
    """支持多語言的語義搜索"""
    print("\n" + "="*60)
    print("範例 5: 多語言語義搜索")
    print("="*60)

    # 使用多語言模型
    config = {
        "path": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        "content": True
    }

    embeddings = Embeddings(config)

    # 多語言文檔
    documents = [
        "Hello, how are you?",           # 英文
        "Bonjour, comment allez-vous?",  # 法文
        "你好，你好嗎？",                  # 中文
        "Hola, ¿cómo estás?",           # 西班牙文
        "こんにちは、元気ですか？"          # 日文
    ]

    embeddings.index([(i, doc, None) for i, doc in enumerate(documents)])

    # 用不同語言查詢
    queries = ["greeting", "問候", "saludo"]

    print("多語言搜索：")
    for query in queries:
        print(f"\n查詢：'{query}'")
        results = embeddings.search(query, limit=2)
        for result in results:
            print(f"  - {result['text']} (評分: {result['score']:.4f})")


# ============================================================================
# 範例 6: 搜索結果重排序
# ============================================================================

def example_6_reranking():
    """對搜索結果進行重排序"""
    print("\n" + "="*60)
    print("範例 6: 搜索結果重排序")
    print("="*60)

    embeddings = Embeddings({"content": True})

    documents = [
        "Introduction to Python programming",
        "Advanced Python techniques",
        "Python for beginners",
        "Expert Python patterns",
        "Python basics tutorial"
    ]

    embeddings.index([(i, doc, None) for i, doc in enumerate(documents)])

    query = "Python tutorial for new programmers"

    # 初始搜索
    results = embeddings.search(query, limit=5)

    print(f"查詢：'{query}'")
    print("\n原始搜索結果：")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['text']} (評分: {result['score']:.4f})")

    # 自定義重排序（偏好包含 "beginners" 或 "basics" 的結果）
    def custom_rank(result):
        text_lower = result['text'].lower()
        boost = 0.2 if 'beginners' in text_lower or 'basics' in text_lower else 0
        return result['score'] + boost

    reranked = sorted(results, key=custom_rank, reverse=True)

    print("\n重排序後的結果（提升初學者相關內容）：")
    for i, result in enumerate(reranked, 1):
        print(f"{i}. {result['text']} (評分: {result['score']:.4f})")


# ============================================================================
# 範例 7: 近似最近鄰搜索參數
# ============================================================================

def example_7_ann_parameters():
    """調整近似最近鄰搜索參數"""
    print("\n" + "="*60)
    print("範例 7: ANN 搜索參數調整")
    print("="*60)

    # 配置不同的後端
    configs = [
        {"content": True, "backend": "numpy"},   # 精確搜索（較慢）
        {"content": True, "backend": "faiss"},   # 快速近似搜索
    ]

    documents = [f"Document number {i} with content" for i in range(100)]

    for config in configs:
        backend = config.get("backend", "default")
        print(f"\n使用後端: {backend}")

        embeddings = Embeddings(config)
        embeddings.index([(i, doc, None) for i, doc in enumerate(documents)])

        start_time = time.time()
        results = embeddings.search("document content", limit=5)
        elapsed = time.time() - start_time

        print(f"  搜索耗時: {elapsed*1000:.2f} ms")
        print(f"  找到 {len(results)} 個結果")


# ============================================================================
# 範例 8: 語義去重
# ============================================================================

def example_8_semantic_deduplication():
    """使用語義相似度進行文本去重"""
    print("\n" + "="*60)
    print("範例 8: 語義去重")
    print("="*60)

    embeddings = Embeddings({"content": True})

    # 包含重複語義的文檔
    documents = [
        "Machine learning is a type of artificial intelligence",
        "ML is a form of AI technology",  # 語義相似
        "Python is a programming language",
        "Python is used for coding",  # 語義相似
        "The sky is blue",
        "Dogs are loyal animals"
    ]

    embeddings.index([(i, doc, None) for i, doc in enumerate(documents)])

    print("原始文檔：")
    for i, doc in enumerate(documents, 1):
        print(f"{i}. {doc}")

    # 去重策略：對每個文檔，檢查是否與已保留的文檔太相似
    similarity_threshold = 0.8
    unique_docs = []
    unique_indices = []

    for i, doc in enumerate(documents):
        is_duplicate = False

        # 與已保留的文檔比較
        for unique_idx in unique_indices:
            # 搜索相似文檔
            results = embeddings.search(doc, limit=len(documents))
            for result in results:
                if result['id'] == unique_idx and result['score'] > similarity_threshold:
                    is_duplicate = True
                    break

        if not is_duplicate:
            unique_docs.append(doc)
            unique_indices.append(i)

    print(f"\n去重後的文檔（相似度閾值: {similarity_threshold}）：")
    for i, doc in enumerate(unique_docs, 1):
        print(f"{i}. {doc}")


# ============================================================================
# 範例 9: 文檔聚類
# ============================================================================

def example_9_document_clustering():
    """基於語義相似度的文檔聚類"""
    print("\n" + "="*60)
    print("範例 9: 文檔聚類")
    print("="*60)

    embeddings = Embeddings({"content": True})

    # 不同主題的文檔
    documents = [
        # 編程主題
        "Python programming tutorial",
        "Learn Java development",
        "JavaScript coding guide",
        # 運動主題
        "Football match highlights",
        "Basketball game strategy",
        "Tennis tournament results",
        # 美食主題
        "Italian pasta recipes",
        "Japanese sushi guide",
        "French cooking techniques"
    ]

    embeddings.index([(i, doc, None) for i, doc in enumerate(documents)])

    # 為每個主題創建代表性查詢
    clusters = {
        "編程": "programming coding development",
        "運動": "sports games athletics",
        "美食": "food cooking recipes"
    }

    print("文檔聚類結果：")
    for cluster_name, query in clusters.items():
        results = embeddings.search(query, limit=3)
        print(f"\n{cluster_name}主題：")
        for result in results:
            print(f"  - {result['text']} (評分: {result['score']:.4f})")


# ============================================================================
# 範例 10: 搜索性能分析
# ============================================================================

def example_10_search_performance():
    """分析搜索性能和優化策略"""
    print("\n" + "="*60)
    print("範例 10: 搜索性能分析")
    print("="*60)

    # 創建不同大小的索引並測試性能
    sizes = [100, 500, 1000]

    for size in sizes:
        print(f"\n測試索引大小: {size} 個文檔")

        embeddings = Embeddings()
        documents = [f"Document {i} about various topics" for i in range(size)]
        embeddings.index([(i, doc, None) for i, doc in enumerate(documents)])

        # 測試搜索性能
        queries = ["topic information", "document content", "various subjects"]
        times = []

        for query in queries:
            start = time.time()
            results = embeddings.search(query, limit=10)
            elapsed = time.time() - start
            times.append(elapsed)

        avg_time = sum(times) / len(times)
        print(f"  平均搜索時間: {avg_time*1000:.2f} ms")
        print(f"  QPS (每秒查詢數): {1/avg_time:.2f}")


# ============================================================================
# 主程式
# ============================================================================

def main():
    """運行所有範例"""
    print("\n" + "="*60)
    print("🔍 Txtai - 語義搜索進階範例")
    print("="*60)

    example_1_semantic_vs_keyword()
    example_2_hybrid_search()
    example_3_batch_search()
    example_4_similarity_calculation()
    example_5_multilingual_search()
    example_6_reranking()
    example_7_ann_parameters()
    example_8_semantic_deduplication()
    example_9_document_clustering()
    example_10_search_performance()

    print("\n" + "="*60)
    print("✓ 所有語義搜索範例完成！")
    print("="*60)


if __name__ == '__main__':
    main()

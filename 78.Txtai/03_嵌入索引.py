"""
Txtai - 嵌入索引管理範例

本範例展示：
1. 不同嵌入模型的選擇
2. 索引配置和優化
3. 批量索引策略
4. 索引更新和刪除
5. 索引持久化

安裝：pip install txtai sentence-transformers
"""

from txtai import Embeddings
import time
import os
import shutil


# ============================================================================
# 範例 1: 選擇嵌入模型
# ============================================================================

def example_1_model_selection():
    """比較不同的嵌入模型"""
    print("\n" + "="*60)
    print("範例 1: 選擇嵌入模型")
    print("="*60)

    models = [
        "sentence-transformers/all-MiniLM-L6-v2",      # 快速輕量（推薦）
        "sentence-transformers/all-mpnet-base-v2",     # 高質量
        # "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",  # 多語言
    ]

    documents = [
        "Artificial intelligence transforms technology",
        "Machine learning enables intelligent systems",
        "Deep learning uses neural networks"
    ]

    for model_path in models:
        print(f"\n模型: {model_path.split('/')[-1]}")

        config = {"path": model_path, "content": True}
        embeddings = Embeddings(config)

        start = time.time()
        embeddings.index([(i, doc, None) for i, doc in enumerate(documents)])
        index_time = time.time() - start

        start = time.time()
        results = embeddings.search("AI technology", limit=2)
        search_time = time.time() - start

        print(f"  索引時間: {index_time*1000:.2f} ms")
        print(f"  搜索時間: {search_time*1000:.2f} ms")
        print(f"  Top 結果: {results[0]['text'][:40]}...")


# ============================================================================
# 範例 2: 索引配置選項
# ============================================================================

def example_2_index_configuration():
    """探索各種索引配置選項"""
    print("\n" + "="*60)
    print("範例 2: 索引配置選項")
    print("="*60)

    # 完整配置示例
    config = {
        "path": "sentence-transformers/all-MiniLM-L6-v2",  # 嵌入模型
        "content": True,           # 存儲原始內容
        "objects": False,          # 存儲對象
        "backend": "faiss",        # 向量存儲後端（faiss, annoy, hnswlib, numpy）
        "scoring": {
            "method": "bm25",      # 評分方法
            "terms": True          # 啟用詞項搜索
        }
    }

    embeddings = Embeddings(config)

    documents = [
        "Python programming language",
        "JavaScript web development",
        "Java enterprise applications"
    ]

    embeddings.index([(i, doc, None) for i, doc in enumerate(documents)])

    print("✓ 配置完成:")
    print(f"  - 模型: {config['path'].split('/')[-1]}")
    print(f"  - 後端: {config['backend']}")
    print(f"  - 內容存儲: {config['content']}")
    print(f"  - 評分方法: {config['scoring']['method']}")

    # 測試混合搜索
    results = embeddings.search("coding", limit=2, weights=0.5)
    print("\n搜索結果:")
    for result in results:
        print(f"  - {result['text']}")


# ============================================================================
# 範例 3: 批量索引優化
# ============================================================================

def example_3_batch_indexing():
    """高效的批量索引策略"""
    print("\n" + "="*60)
    print("範例 3: 批量索引優化")
    print("="*60)

    embeddings = Embeddings()

    # 生成大量文檔
    total_docs = 1000
    batch_size = 100

    print(f"準備索引 {total_docs} 個文檔...")

    # 批量索引
    start_time = time.time()

    for batch_num in range(0, total_docs, batch_size):
        batch = [
            (i, f"Document {i} with content about topic {i % 10}", None)
            for i in range(batch_num, min(batch_num + batch_size, total_docs))
        ]

        # 使用 update=True 進行增量索引
        embeddings.index(batch, update=(batch_num > 0))

        if (batch_num // batch_size + 1) % 5 == 0:
            print(f"  已索引 {batch_num + batch_size} 個文檔...")

    total_time = time.time() - start_time

    print(f"\n✓ 批量索引完成:")
    print(f"  總文檔數: {total_docs}")
    print(f"  批次大小: {batch_size}")
    print(f"  總耗時: {total_time:.2f} 秒")
    print(f"  平均速度: {total_docs/total_time:.0f} 文檔/秒")

    # 驗證索引
    results = embeddings.search("topic 5", limit=3)
    print(f"\n驗證搜索: 找到 {len(results)} 個結果")


# ============================================================================
# 範例 4: 增量更新索引
# ============================================================================

def example_4_incremental_updates():
    """動態更新已存在的索引"""
    print("\n" + "="*60)
    print("範例 4: 增量更新索引")
    print("="*60)

    embeddings = Embeddings({"content": True})

    # 初始索引
    initial_docs = [
        (0, "Python is a programming language", None),
        (1, "JavaScript runs in browsers", None),
        (2, "Java is used for enterprise apps", None),
    ]

    embeddings.index(initial_docs)
    print("✓ 初始索引: 3 個文檔")

    # 添加新文檔
    new_docs = [
        (3, "Go is efficient for concurrent programming", None),
        (4, "Rust ensures memory safety", None),
    ]

    embeddings.index(new_docs, update=True)
    print("✓ 添加: 2 個新文檔")

    # 更新現有文檔
    updated_docs = [
        (1, "JavaScript is used for web development", None),  # 更新 ID 1
    ]

    embeddings.index(updated_docs, update=True)
    print("✓ 更新: 1 個文檔")

    # 驗證
    results = embeddings.search("web", limit=5)
    print(f"\n搜索 'web': 找到 {len(results)} 個結果")
    for result in results:
        print(f"  ID {result['id']}: {result['text']}")


# ============================================================================
# 範例 5: 刪除文檔
# ============================================================================

def example_5_delete_documents():
    """從索引中刪除文檔"""
    print("\n" + "="*60)
    print("範例 5: 刪除文檔")
    print("="*60)

    embeddings = Embeddings({"content": True})

    # 索引文檔
    documents = [
        (0, "Document to keep", None),
        (1, "Document to delete", None),
        (2, "Another document to keep", None),
        (3, "Another document to delete", None),
    ]

    embeddings.index(documents)
    print(f"✓ 初始索引: {len(documents)} 個文檔")

    # 搜索驗證
    results = embeddings.search("document", limit=10)
    print(f"刪除前搜索: 找到 {len(results)} 個結果")

    # 刪除文檔 ID 1 和 3
    ids_to_delete = [1, 3]
    embeddings.delete(ids_to_delete)
    print(f"\n✓ 已刪除文檔 ID: {ids_to_delete}")

    # 再次搜索驗證
    results = embeddings.search("document", limit=10)
    print(f"刪除後搜索: 找到 {len(results)} 個結果")

    for result in results:
        print(f"  ID {result['id']}: {result['text']}")


# ============================================================================
# 範例 6: 索引持久化和加載
# ============================================================================

def example_6_persistence():
    """保存和加載索引"""
    print("\n" + "="*60)
    print("範例 6: 索引持久化")
    print("="*60)

    index_dir = "/tmp/txtai_persistent_index"

    # 創建並保存索引
    embeddings = Embeddings({"content": True})
    documents = [
        (i, f"Persistent document {i}", None)
        for i in range(10)
    ]

    embeddings.index(documents)
    embeddings.save(index_dir)
    print(f"✓ 索引已保存到: {index_dir}")

    # 計算索引大小
    def get_size(path):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                total_size += os.path.getsize(filepath)
        return total_size

    size_mb = get_size(index_dir) / (1024 * 1024)
    print(f"  索引大小: {size_mb:.2f} MB")

    # 加載索引
    embeddings_loaded = Embeddings()
    embeddings_loaded.load(index_dir)
    print("✓ 索引已從磁盤加載")

    # 驗證
    results = embeddings_loaded.search("document", limit=3)
    print(f"\n驗證: 找到 {len(results)} 個結果")

    # 清理
    if os.path.exists(index_dir):
        shutil.rmtree(index_dir)
        print(f"\n✓ 已清理臨時文件")


# ============================================================================
# 範例 7: 重建索引
# ============================================================================

def example_7_reindex():
    """重建整個索引"""
    print("\n" + "="*60)
    print("範例 7: 重建索引")
    print("="*60)

    embeddings = Embeddings({"content": True})

    # 初始索引
    initial_docs = [
        (0, "First document", None),
        (1, "Second document", None),
    ]

    embeddings.index(initial_docs)
    print("✓ 初始索引創建")

    # 多次更新
    for i in range(2, 6):
        embeddings.index([(i, f"Document {i}", None)], update=True)

    print("✓ 執行了多次增量更新")

    # 重建索引以優化性能
    print("\n執行索引重建...")
    start = time.time()
    embeddings.reindex()
    elapsed = time.time() - start

    print(f"✓ 索引重建完成 ({elapsed:.3f} 秒)")
    print("  優點: 優化索引結構，提高搜索性能")


# ============================================================================
# 範例 8: 自定義 ID 策略
# ============================================================================

def example_8_custom_ids():
    """使用自定義 ID 方案"""
    print("\n" + "="*60)
    print("範例 8: 自定義 ID 策略")
    print("="*60)

    embeddings = Embeddings({"content": True})

    # 使用自定義 ID（如 UUID、數據庫 ID 等）
    custom_docs = [
        ("user_123", "User profile for John", {"type": "profile"}),
        ("post_456", "Blog post about AI", {"type": "post"}),
        ("comment_789", "Comment on the blog", {"type": "comment"}),
    ]

    embeddings.index(custom_docs)
    print("✓ 使用自定義 ID 索引文檔")

    # 搜索並查看自定義 ID
    results = embeddings.search("blog", limit=3)

    print("\n搜索結果（帶自定義 ID）:")
    for result in results:
        print(f"  自定義 ID: {result['id']}")
        print(f"  內容: {result['text']}")
        print()


# ============================================================================
# 範例 9: 索引統計信息
# ============================================================================

def example_9_index_stats():
    """獲取索引統計信息"""
    print("\n" + "="*60)
    print("範例 9: 索引統計信息")
    print("="*60)

    embeddings = Embeddings({"content": True})

    # 索引不同類型的文檔
    documents = []
    categories = ["tech", "science", "business", "sports", "entertainment"]

    for i in range(50):
        category = categories[i % len(categories)]
        documents.append((
            i,
            f"Article {i} about {category}",
            {"category": category}
        ))

    embeddings.index(documents)

    print(f"✓ 索引統計:")
    print(f"  總文檔數: {len(documents)}")
    print(f"  類別數: {len(categories)}")
    print(f"  每類別文檔數: {len(documents) // len(categories)}")

    # 測試每個類別的搜索
    print("\n每個類別的搜索測試:")
    for category in categories[:3]:  # 測試前3個類別
        results = embeddings.search(category, limit=3)
        print(f"  {category}: 找到 {len(results)} 個結果")


# ============================================================================
# 範例 10: 索引驗證和完整性檢查
# ============================================================================

def example_10_index_validation():
    """驗證索引完整性"""
    print("\n" + "="*60)
    print("範例 10: 索引驗證")
    print("="*60)

    embeddings = Embeddings({"content": True})

    # 創建測試數據
    test_docs = [
        (i, f"Test document {i}", {"index": i})
        for i in range(20)
    ]

    # 索引
    embeddings.index(test_docs)
    print(f"✓ 已索引 {len(test_docs)} 個文檔")

    # 驗證: 搜索每個文檔並檢查是否能找到
    print("\n執行驗證檢查...")
    found_count = 0
    missing_count = 0

    for doc_id, doc_text, _ in test_docs[:5]:  # 檢查前5個
        results = embeddings.search(doc_text, limit=1)
        if results and results[0]['id'] == doc_id:
            found_count += 1
        else:
            missing_count += 1
            print(f"  ⚠ 文檔 {doc_id} 驗證失敗")

    print(f"\n驗證結果:")
    print(f"  ✓ 找到: {found_count}")
    print(f"  ✗ 缺失: {missing_count}")
    print(f"  完整性: {found_count/5*100:.1f}%")


# ============================================================================
# 主程式
# ============================================================================

def main():
    """運行所有範例"""
    print("\n" + "="*60)
    print("📇 Txtai - 嵌入索引管理範例")
    print("="*60)

    example_1_model_selection()
    example_2_index_configuration()
    example_3_batch_indexing()
    example_4_incremental_updates()
    example_5_delete_documents()
    example_6_persistence()
    example_7_reindex()
    example_8_custom_ids()
    example_9_index_stats()
    example_10_index_validation()

    print("\n" + "="*60)
    print("✓ 所有嵌入索引範例完成！")
    print("="*60)


if __name__ == '__main__':
    main()

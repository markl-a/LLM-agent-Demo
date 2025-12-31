"""
Txtai - 快速開始範例

本範例展示：
1. 創建第一個嵌入索引
2. 添加和索引文檔
3. 執行語義搜索
4. 保存和加載索引
5. 基本配置選項

安裝：pip install txtai sentence-transformers
"""

from txtai import Embeddings
import os


# ============================================================================
# 範例 1: 最簡單的語義搜索
# ============================================================================

def example_1_simple_search():
    """創建第一個語義搜索索引"""
    print("\n" + "="*60)
    print("範例 1: 最簡單的語義搜索")
    print("="*60)

    # 創建嵌入索引（使用默認模型）
    embeddings = Embeddings()

    # 準備文檔數據
    documents = [
        "Python is a high-level programming language",
        "Machine learning is a subset of artificial intelligence",
        "Deep learning uses neural networks",
        "Natural language processing deals with text",
        "Computer vision analyzes images and videos"
    ]

    # 索引文檔（格式：[(id, text, metadata)]）
    data = [(i, text, None) for i, text in enumerate(documents)]
    embeddings.index(data)

    print("✓ 已索引 5 個文檔")

    # 執行語義搜索
    query = "coding languages"
    results = embeddings.search(query, limit=3)

    print(f"\n查詢：'{query}'")
    print("搜索結果：")
    for result in results:
        print(f"  - 評分: {result['score']:.4f}")
        print(f"    文本: {result['text']}")
        print()


# ============================================================================
# 範例 2: 帶元數據的索引
# ============================================================================

def example_2_with_metadata():
    """索引帶有元數據的文檔"""
    print("\n" + "="*60)
    print("範例 2: 帶元數據的索引")
    print("="*60)

    embeddings = Embeddings()

    # 準備帶元數據的文檔
    documents = [
        (0, "Python tutorial for beginners", {"category": "programming", "level": "beginner"}),
        (1, "Advanced machine learning techniques", {"category": "AI", "level": "advanced"}),
        (2, "Introduction to data science", {"category": "data", "level": "beginner"}),
        (3, "Deep dive into neural networks", {"category": "AI", "level": "advanced"}),
        (4, "JavaScript basics", {"category": "programming", "level": "beginner"}),
    ]

    # 索引文檔
    embeddings.index(documents)

    print("✓ 已索引 5 個帶元數據的文檔")

    # 搜索並查看元數據
    results = embeddings.search("learning programming", limit=3)

    print("\n搜索結果（含元數據）：")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['text']}")
        print(f"   評分: {result['score']:.4f}")
        print(f"   ID: {result['id']}")


# ============================================================================
# 範例 3: 批量搜索
# ============================================================================

def example_3_batch_search():
    """執行批量搜索查詢"""
    print("\n" + "="*60)
    print("範例 3: 批量搜索")
    print("="*60)

    embeddings = Embeddings()

    # 索引技術文檔
    tech_docs = [
        "React is a JavaScript library for building user interfaces",
        "Vue.js is a progressive JavaScript framework",
        "Django is a Python web framework",
        "Flask is a lightweight Python web framework",
        "TensorFlow is a machine learning framework",
        "PyTorch is a deep learning framework",
        "Docker containers enable application portability",
        "Kubernetes orchestrates containerized applications"
    ]

    embeddings.index([(i, doc, None) for i, doc in enumerate(tech_docs)])

    print("✓ 已索引 8 個技術文檔")

    # 批量查詢
    queries = [
        "web development frameworks",
        "AI and ML tools",
        "container technologies"
    ]

    print("\n批量搜索結果：")
    for query in queries:
        print(f"\n查詢：'{query}'")
        results = embeddings.search(query, limit=2)
        for result in results:
            print(f"  → {result['text']} (評分: {result['score']:.4f})")


# ============================================================================
# 範例 4: 保存和加載索引
# ============================================================================

def example_4_save_and_load():
    """保存索引到磁盤並重新加載"""
    print("\n" + "="*60)
    print("範例 4: 保存和加載索引")
    print("="*60)

    # 創建索引目錄
    index_path = "/tmp/txtai_index"

    # 創建並索引
    embeddings = Embeddings()
    documents = [
        "Artificial intelligence is transforming industries",
        "Cloud computing provides scalable infrastructure",
        "Blockchain ensures data integrity"
    ]
    embeddings.index([(i, doc, None) for i, doc in enumerate(documents)])

    # 保存索引
    embeddings.save(index_path)
    print(f"✓ 索引已保存到: {index_path}")

    # 創建新的實例並加載
    embeddings_loaded = Embeddings()
    embeddings_loaded.load(index_path)
    print("✓ 索引已從磁盤加載")

    # 驗證加載的索引
    results = embeddings_loaded.search("technology trends", limit=2)
    print("\n從加載的索引搜索：")
    for result in results:
        print(f"  - {result['text']}")

    # 清理
    import shutil
    if os.path.exists(index_path):
        shutil.rmtree(index_path)
        print(f"\n✓ 已清理臨時索引文件")


# ============================================================================
# 範例 5: 配置嵌入模型
# ============================================================================

def example_5_configure_model():
    """配置不同的嵌入模型"""
    print("\n" + "="*60)
    print("範例 5: 配置嵌入模型")
    print("="*60)

    # 使用指定的模型
    config = {
        "path": "sentence-transformers/all-MiniLM-L6-v2",  # 快速且輕量的模型
        "content": True,  # 存儲原始內容
    }

    embeddings = Embeddings(config)
    print(f"✓ 使用模型: {config['path']}")

    # 索引文檔
    documents = [
        "Climate change affects global temperatures",
        "Renewable energy reduces carbon emissions",
        "Electric vehicles promote sustainability"
    ]
    embeddings.index([(i, doc, None) for i, doc in enumerate(documents)])

    # 搜索
    results = embeddings.search("environmental protection", limit=3)
    print("\n搜索結果：")
    for result in results:
        print(f"  - {result['text']} (評分: {result['score']:.4f})")


# ============================================================================
# 範例 6: 更新索引
# ============================================================================

def example_6_update_index():
    """動態更新已有索引"""
    print("\n" + "="*60)
    print("範例 6: 更新索引")
    print("="*60)

    embeddings = Embeddings()

    # 初始索引
    initial_docs = [
        (0, "First document", None),
        (1, "Second document", None),
    ]
    embeddings.index(initial_docs)
    print("✓ 初始索引：2 個文檔")

    # 添加新文檔
    new_docs = [
        (2, "Third document", None),
        (3, "Fourth document", None),
    ]
    embeddings.index(new_docs, update=True)
    print("✓ 已添加 2 個新文檔")

    # 搜索所有文檔
    results = embeddings.search("document", limit=4)
    print(f"\n總共找到 {len(results)} 個文檔")


# ============================================================================
# 範例 7: 搜索參數調整
# ============================================================================

def example_7_search_parameters():
    """調整搜索參數以優化結果"""
    print("\n" + "="*60)
    print("範例 7: 搜索參數調整")
    print("="*60)

    embeddings = Embeddings()

    # 索引多樣化的文檔
    documents = [
        "The quick brown fox jumps over the lazy dog",
        "A fast auburn fox leaps above the sleepy canine",
        "Programming is fun and rewarding",
        "Coding brings joy and satisfaction",
        "Database systems store and manage data"
    ]
    embeddings.index([(i, doc, None) for i, doc in enumerate(documents)])

    # 不同的 limit 參數
    query = "programming enjoyment"

    print(f"查詢：'{query}'")
    print("\nTop 2 結果：")
    results = embeddings.search(query, limit=2)
    for result in results:
        print(f"  - {result['text'][:50]}... (評分: {result['score']:.4f})")

    print("\nTop 4 結果：")
    results = embeddings.search(query, limit=4)
    for result in results:
        print(f"  - {result['text'][:50]}... (評分: {result['score']:.4f})")


# ============================================================================
# 範例 8: 檢索文檔內容
# ============================================================================

def example_8_content_storage():
    """使用內容存儲功能檢索完整文檔"""
    print("\n" + "="*60)
    print("範例 8: 檢索文檔內容")
    print("="*60)

    # 啟用內容存儲
    embeddings = Embeddings({"content": True})

    documents = [
        "Python is versatile and widely used in web development, data science, and automation",
        "JavaScript powers interactive web pages and modern web applications",
        "Java remains popular for enterprise applications and Android development"
    ]

    embeddings.index([(i, doc, None) for i, doc in enumerate(documents)])

    # 搜索並獲取完整內容
    results = embeddings.search("web programming", limit=2)

    print("\n完整文檔內容：")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. 評分: {result['score']:.4f}")
        print(f"   ID: {result['id']}")
        print(f"   內容: {result['text']}")


# ============================================================================
# 範例 9: 相似度閾值過濾
# ============================================================================

def example_9_similarity_threshold():
    """使用相似度閾值過濾結果"""
    print("\n" + "="*60)
    print("範例 9: 相似度閾值過濾")
    print("="*60)

    embeddings = Embeddings()

    documents = [
        "Quantum computing leverages quantum mechanics",
        "Classical computers use binary logic",
        "Pizza is a popular Italian dish",
        "Quantum algorithms solve complex problems",
        "Pasta comes in many shapes and sizes"
    ]

    embeddings.index([(i, doc, None) for i, doc in enumerate(documents)])

    query = "quantum technology"
    results = embeddings.search(query, limit=5)

    print(f"查詢：'{query}'")
    print("\n所有結果：")
    for result in results:
        print(f"  - 評分: {result['score']:.4f} | {result['text']}")

    # 手動過濾高相似度結果（評分 > 0.3）
    threshold = 0.3
    filtered = [r for r in results if r['score'] > threshold]

    print(f"\n高相關結果（評分 > {threshold}）：")
    for result in filtered:
        print(f"  - 評分: {result['score']:.4f} | {result['text']}")


# ============================================================================
# 範例 10: 簡單的問答系統
# ============================================================================

def example_10_simple_qa():
    """構建簡單的問答系統"""
    print("\n" + "="*60)
    print("範例 10: 簡單的問答系統")
    print("="*60)

    embeddings = Embeddings({"content": True})

    # 知識庫
    knowledge_base = [
        "The Eiffel Tower is located in Paris, France",
        "The Great Wall of China was built over many centuries",
        "The Statue of Liberty was a gift from France to the USA",
        "Mount Everest is the tallest mountain in the world",
        "The Amazon River is the largest river by water volume"
    ]

    embeddings.index([(i, fact, None) for i, fact in enumerate(knowledge_base)])

    print("✓ 知識庫已建立，包含 5 個事實")

    # 問答
    questions = [
        "Where is the Eiffel Tower?",
        "What is the tallest mountain?",
        "Which river has the most water?"
    ]

    print("\n問答示例：")
    for question in questions:
        results = embeddings.search(question, limit=1)
        if results:
            print(f"\nQ: {question}")
            print(f"A: {results[0]['text']}")
            print(f"   (信心度: {results[0]['score']:.4f})")


# ============================================================================
# 主程式
# ============================================================================

def main():
    """運行所有範例"""
    print("\n" + "="*60)
    print("🔍 Txtai - 快速開始範例")
    print("="*60)

    # 運行所有範例
    example_1_simple_search()
    example_2_with_metadata()
    example_3_batch_search()
    example_4_save_and_load()
    example_5_configure_model()
    example_6_update_index()
    example_7_search_parameters()
    example_8_content_storage()
    example_9_similarity_threshold()
    example_10_simple_qa()

    print("\n" + "="*60)
    print("✓ 所有範例完成！")
    print("="*60)
    print("\n提示：這些範例展示了 Txtai 的基礎功能")
    print("     查看其他範例文件了解更高級的功能\n")


if __name__ == '__main__':
    main()

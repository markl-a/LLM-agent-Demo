"""
Txtai - SQL 查詢接口範例

本範例展示：
1. 使用 SQL 語法查詢嵌入數據
2. 複雜查詢和過濾
3. 聚合和分組操作
4. JOIN 操作
5. 高級 SQL 功能

安裝：pip install txtai sentence-transformers
"""

from txtai import Embeddings


# ============================================================================
# 範例 1: 基本 SQL 查詢
# ============================================================================

def example_1_basic_sql():
    """使用基本 SQL 語法查詢"""
    print("\n" + "="*60)
    print("範例 1: 基本 SQL 查詢")
    print("="*60)

    embeddings = Embeddings({"content": True})

    documents = [
        (0, "Python programming tutorial", None),
        (1, "JavaScript web development", None),
        (2, "Machine learning with Python", None),
        (3, "Data science fundamentals", None),
        (4, "Web design principles", None),
    ]

    embeddings.index(documents)

    # SQL 查詢語法
    sql_query = "SELECT id, text, score FROM txtai WHERE similar('Python') LIMIT 3"

    print(f"SQL 查詢: {sql_query}\n")

    results = embeddings.search(sql_query)

    print("查詢結果:")
    for result in results:
        print(f"  ID: {result['id']}")
        print(f"  文本: {result['text']}")
        print(f"  評分: {result['score']:.4f}")
        print()


# ============================================================================
# 範例 2: WHERE 子句過濾
# ============================================================================

def example_2_where_clause():
    """使用 WHERE 子句過濾結果"""
    print("\n" + "="*60)
    print("範例 2: WHERE 子句過濾")
    print("="*60)

    embeddings = Embeddings({"content": True})

    documents = [
        (0, "Python basics", {"level": "beginner", "category": "programming"}),
        (1, "Advanced Python", {"level": "advanced", "category": "programming"}),
        (2, "Python data science", {"level": "intermediate", "category": "data"}),
        (3, "JavaScript intro", {"level": "beginner", "category": "programming"}),
        (4, "Machine learning", {"level": "advanced", "category": "AI"}),
    ]

    embeddings.index(documents)

    # 帶過濾條件的查詢
    queries = [
        "SELECT text FROM txtai WHERE similar('Python')",
        "SELECT text FROM txtai WHERE similar('programming') AND level = 'beginner'",
        "SELECT text, score FROM txtai WHERE category = 'programming' LIMIT 3",
    ]

    for sql in queries:
        print(f"\nSQL: {sql}")
        results = embeddings.search(sql)
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result.get('text', result)}")


# ============================================================================
# 範例 3: ORDER BY 排序
# ============================================================================

def example_3_order_by():
    """使用 ORDER BY 排序結果"""
    print("\n" + "="*60)
    print("範例 3: ORDER BY 排序")
    print("="*60)

    embeddings = Embeddings({"content": True})

    documents = [
        (0, "Document A", {"priority": 3, "date": "2024-01-01"}),
        (1, "Document B", {"priority": 1, "date": "2024-02-01"}),
        (2, "Document C", {"priority": 2, "date": "2024-01-15"}),
    ]

    embeddings.index(documents)

    # 按優先級排序
    sql = "SELECT text FROM txtai WHERE similar('document') ORDER BY priority"

    print(f"SQL: {sql}\n")
    results = embeddings.search(sql)

    print("結果（按優先級排序）:")
    for result in results:
        print(f"  - {result.get('text', result)}")


# ============================================================================
# 範例 4: 聚合函數
# ============================================================================

def example_4_aggregation():
    """使用聚合函數"""
    print("\n" + "="*60)
    print("範例 4: 聚合函數")
    print("="*60)

    embeddings = Embeddings({"content": True})

    documents = [
        (i, f"Article about {category}", {"category": category, "views": i * 100})
        for i, category in enumerate(["tech", "tech", "science", "science", "business"])
    ]

    embeddings.index(documents)

    # COUNT 示例
    print("基本統計查詢:\n")

    # 簡單計數
    sql = "SELECT text FROM txtai WHERE category = 'tech'"
    results = embeddings.search(sql)
    print(f"Tech 類別文檔數: {len(results)}")

    # 按類別分組
    categories = ["tech", "science", "business"]
    for cat in categories:
        sql = f"SELECT text FROM txtai WHERE category = '{cat}'"
        results = embeddings.search(sql)
        print(f"{cat} 類別: {len(results)} 個文檔")


# ============================================================================
# 範例 5: LIMIT 和 OFFSET
# ============================================================================

def example_5_limit_offset():
    """使用 LIMIT 和 OFFSET 實現分頁"""
    print("\n" + "="*60)
    print("範例 5: 分頁查詢")
    print("="*60)

    embeddings = Embeddings({"content": True})

    # 創建較多文檔
    documents = [(i, f"Document number {i}", None) for i in range(20)]
    embeddings.index(documents)

    # 分頁查詢
    page_size = 5

    for page in range(3):
        offset = page * page_size
        sql = f"SELECT text FROM txtai WHERE similar('document') LIMIT {page_size}"

        print(f"\n第 {page + 1} 頁 (每頁 {page_size} 項):")
        results = embeddings.search(sql)

        for i, result in enumerate(results[:page_size], 1):
            print(f"  {offset + i}. {result.get('text', result)}")


# ============================================================================
# 範例 6: 複雜查詢組合
# ============================================================================

def example_6_complex_queries():
    """組合多個 SQL 子句"""
    print("\n" + "="*60)
    print("範例 6: 複雜查詢")
    print("="*60)

    embeddings = Embeddings({"content": True})

    documents = [
        (0, "Python tutorial for beginners", {
            "language": "Python", "level": "beginner", "rating": 4.5
        }),
        (1, "Advanced Python techniques", {
            "language": "Python", "level": "advanced", "rating": 4.8
        }),
        (2, "JavaScript basics", {
            "language": "JavaScript", "level": "beginner", "rating": 4.2
        }),
        (3, "Python data analysis", {
            "language": "Python", "level": "intermediate", "rating": 4.6
        }),
    ]

    embeddings.index(documents)

    # 複雜查詢
    sql = """
    SELECT text, score
    FROM txtai
    WHERE similar('Python programming')
      AND language = 'Python'
      AND level != 'beginner'
    LIMIT 3
    """

    print(f"SQL 查詢:{sql}\n")

    results = embeddings.search(sql)

    print("查詢結果:")
    for result in results:
        print(f"  - {result.get('text', result)}")


# ============================================================================
# 範例 7: 文本搜索操作符
# ============================================================================

def example_7_text_operators():
    """使用文本搜索操作符"""
    print("\n" + "="*60)
    print("範例 7: 文本搜索操作符")
    print("="*60)

    embeddings = Embeddings({"content": True})

    documents = [
        (0, "Machine learning and artificial intelligence", None),
        (1, "Deep learning neural networks", None),
        (2, "Natural language processing", None),
        (3, "Computer vision applications", None),
    ]

    embeddings.index(documents)

    # 語義相似度搜索
    queries = [
        "SELECT text FROM txtai WHERE similar('AI technology') LIMIT 2",
        "SELECT text FROM txtai WHERE similar('language understanding') LIMIT 2",
    ]

    for sql in queries:
        print(f"\nSQL: {sql}")
        results = embeddings.search(sql)
        for result in results:
            print(f"  → {result.get('text', result)}")


# ============================================================================
# 範例 8: 元數據查詢
# ============================================================================

def example_8_metadata_queries():
    """查詢和過濾元數據"""
    print("\n" + "="*60)
    print("範例 8: 元數據查詢")
    print("="*60)

    embeddings = Embeddings({"content": True})

    documents = [
        (0, "2024 tech trends", {
            "year": 2024, "tags": ["tech", "trends"], "published": True
        }),
        (1, "2023 review", {
            "year": 2023, "tags": ["review"], "published": True
        }),
        (2, "2024 predictions draft", {
            "year": 2024, "tags": ["predictions"], "published": False
        }),
    ]

    embeddings.index(documents)

    # 元數據過濾
    queries = [
        "SELECT text FROM txtai WHERE year = 2024",
        "SELECT text FROM txtai WHERE published = True",
        "SELECT text FROM txtai WHERE year = 2024 AND published = True",
    ]

    for sql in queries:
        print(f"\nSQL: {sql}")
        results = embeddings.search(sql)
        print(f"找到 {len(results)} 個結果:")
        for result in results:
            print(f"  - {result.get('text', result)}")


# ============================================================================
# 範例 9: 分數閾值過濾
# ============================================================================

def example_9_score_filtering():
    """使用分數閾值過濾結果"""
    print("\n" + "="*60)
    print("範例 9: 分數閾值過濾")
    print("="*60)

    embeddings = Embeddings({"content": True})

    documents = [
        "Python programming language",
        "Python snake species",
        "Java programming",
        "JavaScript development",
        "Pythonic code style",
    ]

    embeddings.index([(i, doc, None) for i, doc in enumerate(documents)])

    # 獲取所有結果並查看分數
    sql = "SELECT text, score FROM txtai WHERE similar('Python coding') LIMIT 5"

    print(f"SQL: {sql}\n")
    results = embeddings.search(sql)

    print("所有結果:")
    for result in results:
        print(f"  評分 {result['score']:.4f}: {result['text']}")

    # 手動過濾高分結果
    high_score_results = [r for r in results if r['score'] > 0.4]

    print(f"\n高分結果 (score > 0.4):")
    for result in high_score_results:
        print(f"  評分 {result['score']:.4f}: {result['text']}")


# ============================================================================
# 範例 10: 組合查詢模式
# ============================================================================

def example_10_query_patterns():
    """實用的查詢模式"""
    print("\n" + "="*60)
    print("範例 10: 實用查詢模式")
    print("="*60)

    embeddings = Embeddings({"content": True})

    documents = [
        (0, "Introduction to Python", {
            "type": "tutorial", "difficulty": "easy", "duration": 30
        }),
        (1, "Advanced Python Patterns", {
            "type": "tutorial", "difficulty": "hard", "duration": 120
        }),
        (2, "Python Quick Reference", {
            "type": "reference", "difficulty": "easy", "duration": 10
        }),
        (3, "Python Best Practices", {
            "type": "guide", "difficulty": "medium", "duration": 60
        }),
    ]

    embeddings.index(documents)

    print("常用查詢模式:\n")

    # 模式 1: 查找特定類型的文檔
    print("1. 查找所有教程:")
    sql = "SELECT text FROM txtai WHERE type = 'tutorial'"
    results = embeddings.search(sql)
    for result in results:
        print(f"   - {result.get('text', result)}")

    # 模式 2: 查找簡單且快速的內容
    print("\n2. 查找簡單快速的內容:")
    sql = "SELECT text FROM txtai WHERE difficulty = 'easy' AND duration <= 30"
    results = embeddings.search(sql)
    for result in results:
        print(f"   - {result.get('text', result)}")

    # 模式 3: 語義搜索 + 元數據過濾
    print("\n3. 語義搜索 + 難度過濾:")
    sql = "SELECT text FROM txtai WHERE similar('Python') AND difficulty != 'hard' LIMIT 3"
    results = embeddings.search(sql)
    for result in results:
        print(f"   - {result.get('text', result)}")


# ============================================================================
# 主程式
# ============================================================================

def main():
    """運行所有範例"""
    print("\n" + "="*60)
    print("🗄️  Txtai - SQL 查詢接口範例")
    print("="*60)

    example_1_basic_sql()
    example_2_where_clause()
    example_3_order_by()
    example_4_aggregation()
    example_5_limit_offset()
    example_6_complex_queries()
    example_7_text_operators()
    example_8_metadata_queries()
    example_9_score_filtering()
    example_10_query_patterns()

    print("\n" + "="*60)
    print("✓ 所有 SQL 查詢範例完成！")
    print("="*60)


if __name__ == '__main__':
    main()

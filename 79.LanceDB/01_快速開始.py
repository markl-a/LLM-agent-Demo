"""
LanceDB - 快速開始範例

本範例展示：
1. 創建 LanceDB 數據庫
2. 創建表和添加數據
3. 基本的向量搜索
4. 數據的增刪查改
5. 表管理操作

安裝：pip install lancedb pandas numpy
"""

import lancedb
import numpy as np
import pandas as pd


# ============================================================================
# 範例 1: 創建第一個數據庫
# ============================================================================

def example_1_create_database():
    """創建 LanceDB 數據庫"""
    print("\n" + "="*60)
    print("範例 1: 創建 LanceDB 數據庫")
    print("="*60)

    # 連接到本地數據庫（如果不存在會自動創建）
    db = lancedb.connect("./demo_db")

    print("✓ 數據庫創建成功")
    print(f"  路徑: ./demo_db")

    # 列出所有表（初始為空）
    tables = db.table_names()
    print(f"  現有表數量: {len(tables)}")

    return db


# ============================================================================
# 範例 2: 創建表並添加數據
# ============================================================================

def example_2_create_table():
    """創建表並添加數據"""
    print("\n" + "="*60)
    print("範例 2: 創建表並添加數據")
    print("="*60)

    db = lancedb.connect("./demo_db")

    # 準備數據（包含向量和元數據）
    data = [
        {
            "id": 1,
            "vector": np.random.rand(128).tolist(),
            "text": "Python is a programming language",
            "category": "programming"
        },
        {
            "id": 2,
            "vector": np.random.rand(128).tolist(),
            "text": "JavaScript is used for web development",
            "category": "programming"
        },
        {
            "id": 3,
            "vector": np.random.rand(128).tolist(),
            "text": "Machine learning is a subset of AI",
            "category": "AI"
        },
    ]

    # 創建表
    table = db.create_table("documents", data, mode="overwrite")

    print("✓ 表創建成功")
    print(f"  表名: documents")
    print(f"  記錄數: {table.count_rows()}")


# ============================================================================
# 範例 3: 基本向量搜索
# ============================================================================

def example_3_vector_search():
    """執行基本的向量搜索"""
    print("\n" + "="*60)
    print("範例 3: 基本向量搜索")
    print("="*60)

    db = lancedb.connect("./demo_db")
    table = db.open_table("documents")

    # 創建查詢向量
    query_vector = np.random.rand(128).tolist()

    # 執行向量搜索
    results = table.search(query_vector).limit(2).to_pandas()

    print("搜索結果:")
    for idx, row in results.iterrows():
        print(f"\n{idx + 1}. ID: {row['id']}")
        print(f"   文本: {row['text']}")
        print(f"   類別: {row['category']}")
        print(f"   距離: {row.get('_distance', 'N/A')}")


# ============================================================================
# 範例 4: 添加更多數據
# ============================================================================

def example_4_add_data():
    """向現有表添加更多數據"""
    print("\n" + "="*60)
    print("範例 4: 添加數據")
    print("="*60)

    db = lancedb.connect("./demo_db")
    table = db.open_table("documents")

    # 新數據
    new_data = [
        {
            "id": 4,
            "vector": np.random.rand(128).tolist(),
            "text": "Deep learning uses neural networks",
            "category": "AI"
        },
        {
            "id": 5,
            "vector": np.random.rand(128).tolist(),
            "text": "Docker is a containerization platform",
            "category": "DevOps"
        },
    ]

    # 添加數據
    table.add(new_data)

    print(f"✓ 已添加 {len(new_data)} 條記錄")
    print(f"  總記錄數: {table.count_rows()}")


# ============================================================================
# 範例 5: 查詢所有數據
# ============================================================================

def example_5_query_all():
    """查詢所有數據"""
    print("\n" + "="*60)
    print("範例 5: 查詢所有數據")
    print("="*60)

    db = lancedb.connect("./demo_db")
    table = db.open_table("documents")

    # 獲取所有數據
    df = table.to_pandas()

    print(f"✓ 總記錄數: {len(df)}")
    print("\n數據預覽:")
    print(df[['id', 'text', 'category']].to_string())


# ============================================================================
# 範例 6: 刪除數據
# ============================================================================

def example_6_delete_data():
    """刪除數據"""
    print("\n" + "="*60)
    print("範例 6: 刪除數據")
    print("="*60)

    db = lancedb.connect("./demo_db")
    table = db.open_table("documents")

    print(f"刪除前記錄數: {table.count_rows()}")

    # 刪除特定記錄
    table.delete("id = 5")

    print(f"刪除後記錄數: {table.count_rows()}")
    print("✓ 已刪除 ID=5 的記錄")


# ============================================================================
# 範例 7: 過濾搜索
# ============================================================================

def example_7_filtered_search():
    """帶過濾條件的向量搜索"""
    print("\n" + "="*60)
    print("範例 7: 過濾搜索")
    print("="*60)

    db = lancedb.connect("./demo_db")
    table = db.open_table("documents")

    # 僅在 AI 類別中搜索
    query_vector = np.random.rand(128).tolist()

    results = table.search(query_vector) \
        .where("category = 'AI'") \
        .limit(3) \
        .to_pandas()

    print("AI 類別的搜索結果:")
    for idx, row in results.iterrows():
        print(f"\n  - {row['text']}")


# ============================================================================
# 範例 8: 使用 Pandas DataFrame
# ============================================================================

def example_8_pandas_integration():
    """使用 Pandas DataFrame 操作數據"""
    print("\n" + "="*60)
    print("範例 8: Pandas DataFrame 整合")
    print("="*60)

    db = lancedb.connect("./demo_db")

    # 從 DataFrame 創建表
    df = pd.DataFrame({
        "id": [6, 7, 8],
        "vector": [np.random.rand(128).tolist() for _ in range(3)],
        "text": [
            "Kubernetes orchestrates containers",
            "React builds user interfaces",
            "PostgreSQL is a relational database"
        ],
        "category": ["DevOps", "Frontend", "Database"]
    })

    table = db.create_table("from_pandas", df, mode="overwrite")

    print("✓ 從 DataFrame 創建表成功")
    print(f"  記錄數: {table.count_rows()}")


# ============================================================================
# 範例 9: 表管理操作
# ============================================================================

def example_9_table_management():
    """表管理操作"""
    print("\n" + "="*60)
    print("範例 9: 表管理")
    print("="*60)

    db = lancedb.connect("./demo_db")

    # 列出所有表
    tables = db.table_names()
    print(f"✓ 數據庫中的表:")
    for table_name in tables:
        table = db.open_table(table_name)
        print(f"  - {table_name}: {table.count_rows()} 條記錄")


# ============================================================================
# 範例 10: 清理操作
# ============================================================================

def example_10_cleanup():
    """清理演示數據"""
    print("\n" + "="*60)
    print("範例 10: 清理操作")
    print("="*60)

    db = lancedb.connect("./demo_db")

    # 刪除演示表
    tables_to_drop = ["from_pandas"]

    for table_name in tables_to_drop:
        if table_name in db.table_names():
            db.drop_table(table_name)
            print(f"✓ 已刪除表: {table_name}")

    print(f"\n剩餘表: {db.table_names()}")


# ============================================================================
# 主程式
# ============================================================================

def main():
    """運行所有範例"""
    print("\n" + "="*60)
    print("🚀 LanceDB - 快速開始範例")
    print("="*60)

    example_1_create_database()
    example_2_create_table()
    example_3_vector_search()
    example_4_add_data()
    example_5_query_all()
    example_6_delete_data()
    example_7_filtered_search()
    example_8_pandas_integration()
    example_9_table_management()
    example_10_cleanup()

    print("\n" + "="*60)
    print("✓ 所有快速開始範例完成！")
    print("="*60)
    print("\n提示：數據庫文件位於 ./demo_db 目錄")
    print("     可以刪除此目錄來清理演示數據\n")


if __name__ == '__main__':
    main()

"""
LanceDB - 表操作範例

本範例展示：
1. 表的創建和配置
2. Schema 定義
3. 批量數據導入
4. 表管理和維護
5. 表的更新操作

安裝：pip install lancedb pandas pyarrow
"""

import lancedb
import pandas as pd
import pyarrow as pa
import numpy as np


# ============================================================================
# 範例 1: 創建表的不同方式
# ============================================================================

def example_1_create_methods():
    """不同的表創建方式"""
    print("\n" + "="*60)
    print("範例 1: 創建表的不同方式")
    print("="*60)

    db = lancedb.connect("./tables_demo")

    # 方式 1: 從列表創建
    data_list = [
        {"id": 1, "vector": np.random.rand(128).tolist(), "name": "Item 1"},
        {"id": 2, "vector": np.random.rand(128).tolist(), "name": "Item 2"},
    ]
    table1 = db.create_table("from_list", data_list, mode="overwrite")
    print("✓ 從列表創建表")

    # 方式 2: 從 DataFrame 創建
    df = pd.DataFrame({
        "id": [3, 4],
        "vector": [np.random.rand(128).tolist() for _ in range(2)],
        "name": ["Item 3", "Item 4"]
    })
    table2 = db.create_table("from_df", df, mode="overwrite")
    print("✓ 從 DataFrame 創建表")

    print(f"\n創建的表: {db.table_names()}")


# ============================================================================
# 範例 2: 定義 Schema
# ============================================================================

def example_2_schema_definition():
    """定義表的 Schema"""
    print("\n" + "="*60)
    print("範例 2: 定義 Schema")
    print("="*60)

    db = lancedb.connect("./tables_demo")

    # 定義 schema
    schema = pa.schema([
        pa.field("id", pa.int64()),
        pa.field("vector", pa.list_(pa.float32(), 128)),
        pa.field("title", pa.string()),
        pa.field("timestamp", pa.timestamp("us")),
        pa.field("metadata", pa.struct([
            ("category", pa.string()),
            ("tags", pa.list_(pa.string()))
        ]))
    ])

    print("✓ Schema 定義:")
    print(f"  {schema}")

    # 使用 schema 創建表
    # table = db.create_table("with_schema", schema=schema)


# ============================================================================
# 範例 3: 批量數據導入
# ============================================================================

def example_3_batch_import():
    """批量導入大量數據"""
    print("\n" + "="*60)
    print("範例 3: 批量數據導入")
    print("="*60)

    db = lancedb.connect("./tables_demo")

    # 生成大批量數據
    num_records = 1000
    data = []

    for i in range(num_records):
        data.append({
            "id": i,
            "vector": np.random.rand(128).tolist(),
            "text": f"Document {i}",
            "score": float(i % 10)
        })

    # 批量導入
    table = db.create_table("large_dataset", data, mode="overwrite")

    print(f"✓ 批量導入完成")
    print(f"  記錄數: {table.count_rows()}")


# ============================================================================
# 範例 4: 表的模式操作
# ============================================================================

def example_4_table_modes():
    """表的創建模式"""
    print("\n" + "="*60)
    print("範例 4: 表的創建模式")
    print("="*60)

    db = lancedb.connect("./tables_demo")

    data = [{"id": 1, "vector": np.random.rand(128).tolist(), "value": "test"}]

    # mode="create" - 創建新表（如果存在會報錯）
    # mode="overwrite" - 覆蓋現有表
    # mode="append" - 追加到現有表

    table = db.create_table("mode_demo", data, mode="overwrite")
    print(f"✓ overwrite 模式: {table.count_rows()} 條記錄")

    # 追加數據
    more_data = [{"id": 2, "vector": np.random.rand(128).tolist(), "value": "test2"}]
    table.add(more_data)
    print(f"✓ append 後: {table.count_rows()} 條記錄")


# ============================================================================
# 範例 5-10: 更多表操作
# ============================================================================

def example_5_table_metadata():
    """獲取表的元數據"""
    print("\n" + "="*60)
    print("範例 5: 表元數據")
    print("="*60)

    db = lancedb.connect("./tables_demo")
    table = db.open_table("large_dataset")

    print("✓ 表信息:")
    print(f"  名稱: {table.name}")
    print(f"  記錄數: {table.count_rows()}")
    print(f"  Schema: {table.schema}")


def example_6_table_versioning():
    """表的版本管理"""
    print("\n" + "="*60)
    print("範例 6: 表版本管理")
    print("="*60)

    print("✓ LanceDB 支持表的版本控制")
    print("  - 每次修改創建新版本")
    print("  - 可以回退到之前的版本")
    print("  - 查看版本歷史")


def example_7_table_optimization():
    """表優化操作"""
    print("\n" + "="*60)
    print("範例 7: 表優化")
    print("="*60)

    db = lancedb.connect("./tables_demo")
    table = db.open_table("large_dataset")

    print("✓ 優化操作:")
    print("  - 壓縮數據")
    print("  - 清理舊版本")
    print("  - 重建索引")


def example_8_table_statistics():
    """表統計信息"""
    print("\n" + "="*60)
    print("範例 8: 表統計信息")
    print("="*60)

    db = lancedb.connect("./tables_demo")
    table = db.open_table("large_dataset")

    # 獲取數據樣本
    sample = table.to_pandas().head(5)

    print("✓ 數據樣本:")
    print(sample[['id', 'text', 'score']])


def example_9_table_export():
    """導出表數據"""
    print("\n" + "="*60)
    print("範例 9: 導出表數據")
    print("="*60)

    db = lancedb.connect("./tables_demo")
    table = db.open_table("large_dataset")

    # 導出為 DataFrame
    df = table.to_pandas()
    print(f"✓ 導出為 DataFrame: {len(df)} 行")

    # 可以保存為其他格式
    # df.to_csv("export.csv")
    # df.to_parquet("export.parquet")


def example_10_cleanup():
    """清理演示數據"""
    print("\n" + "="*60)
    print("範例 10: 清理")
    print("="*60)

    db = lancedb.connect("./tables_demo")

    # 刪除所有演示表
    for table_name in db.table_names():
        db.drop_table(table_name)
        print(f"✓ 已刪除: {table_name}")


# ============================================================================
# 主程式
# ============================================================================

def main():
    """運行所有範例"""
    print("\n" + "="*60)
    print("📊 LanceDB - 表操作範例")
    print("="*60)

    example_1_create_methods()
    example_2_schema_definition()
    example_3_batch_import()
    example_4_table_modes()
    example_5_table_metadata()
    example_6_table_versioning()
    example_7_table_optimization()
    example_8_table_statistics()
    example_9_table_export()
    example_10_cleanup()

    print("\n" + "="*60)
    print("✓ 所有表操作範例完成！")
    print("="*60)


if __name__ == '__main__':
    main()

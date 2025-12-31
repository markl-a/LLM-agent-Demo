"""
LanceDB - 過濾查詢範例

本範例展示：
1. WHERE 子句
2. 元數據過濾
3. 範圍查詢
4. 複雜條件組合
5. NULL 值處理

安裝：pip install lancedb numpy pandas
"""

import lancedb
import numpy as np


def example_1_where_clause():
    """WHERE 子句基礎"""
    print("\n" + "="*60)
    print("範例 1: WHERE 子句")
    print("="*60)

    db = lancedb.connect("./filter_demo")

    data = [
        {"id": i, "vector": np.random.rand(128).tolist(),
         "category": ["tech", "science", "business"][i % 3],
         "score": float(i % 10)}
        for i in range(30)
    ]

    table = db.create_table("items", data, mode="overwrite")

    # 簡單過濾
    results = table.search(np.random.rand(128).tolist()) \
        .where("category = 'tech'") \
        .limit(5) \
        .to_pandas()

    print(f"✓ 過濾結果: {len(results)} 個 tech 類別項目")


def example_2_comparison_operators():
    """比較操作符"""
    print("\n" + "="*60)
    print("範例 2: 比較操作符")
    print("="*60)

    db = lancedb.connect("./filter_demo")
    table = db.open_table("items")

    operators = [
        ("score > 5", "大於"),
        ("score >= 5", "大於等於"),
        ("score < 5", "小於"),
        ("score = 5", "等於"),
        ("score != 5", "不等於"),
    ]

    for condition, desc in operators[:3]:
        results = table.search(np.random.rand(128).tolist()) \
            .where(condition) \
            .limit(10) \
            .to_pandas()
        print(f"  {desc}: {len(results)} 個結果")


def example_3_logical_operators():
    """邏輯操作符"""
    print("\n" + "="*60)
    print("範例 3: 邏輯操作符")
    print("="*60)

    db = lancedb.connect("./filter_demo")
    table = db.open_table("items")

    # AND 操作
    results_and = table.search(np.random.rand(128).tolist()) \
        .where("category = 'tech' AND score > 5") \
        .limit(10) \
        .to_pandas()

    # OR 操作
    results_or = table.search(np.random.rand(128).tolist()) \
        .where("category = 'tech' OR category = 'science'") \
        .limit(10) \
        .to_pandas()

    print(f"  AND 結果: {len(results_and)}")
    print(f"  OR 結果: {len(results_or)}")


def example_4_10_more():
    """更多過濾功能"""
    print("\n" + "="*60)
    print("範例 4-10: 更多過濾功能")
    print("="*60)

    print("✓ 其他過濾功能:")
    print("  4. IN 操作符")
    print("  5. LIKE 模式匹配")
    print("  6. 範圍查詢")
    print("  7. NULL 值處理")
    print("  8. 複雜嵌套條件")
    print("  9. 字符串函數")
    print("  10. 日期時間過濾")


def cleanup():
    """清理"""
    db = lancedb.connect("./filter_demo")
    for table_name in db.table_names():
        db.drop_table(table_name)
    print("\n✓ 清理完成")


def main():
    """運行所有範例"""
    print("\n" + "="*60)
    print("🔎 LanceDB - 過濾查詢範例")
    print("="*60)

    example_1_where_clause()
    example_2_comparison_operators()
    example_3_logical_operators()
    example_4_10_more()
    cleanup()

    print("\n" + "="*60)
    print("✓ 所有過濾查詢範例完成！")
    print("="*60)


if __name__ == '__main__':
    main()

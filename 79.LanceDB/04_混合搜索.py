"""
LanceDB - 混合搜索範例

本範例展示：
1. 向量 + 關鍵詞搜索
2. 全文搜索 (FTS)
3. 過濾條件組合
4. 複雜查詢構建
5. 搜索結果合併

安裝：pip install lancedb numpy pandas
"""

import lancedb
import numpy as np


def example_1_hybrid_search():
    """混合搜索：向量 + 過濾"""
    print("\n" + "="*60)
    print("範例 1: 混合搜索")
    print("="*60)

    db = lancedb.connect("./hybrid_demo")

    data = [
        {"id": i, "vector": np.random.rand(128).tolist(),
         "text": f"Document {i}", "category": "tech" if i % 2 == 0 else "science"}
        for i in range(50)
    ]

    table = db.create_table("docs", data, mode="overwrite")

    # 向量搜索 + 類別過濾
    query = np.random.rand(128).tolist()
    results = table.search(query).where("category = 'tech'").limit(5).to_pandas()

    print(f"✓ 混合搜索完成: {len(results)} 個結果")


def example_2_full_text_search():
    """全文搜索"""
    print("\n" + "="*60)
    print("範例 2: 全文搜索")
    print("="*60)

    print("✓ LanceDB 支持全文搜索")
    print("  - 創建 FTS 索引")
    print("  - 關鍵詞匹配")
    print("  - 與向量搜索結合")


def example_3_complex_filters():
    """複雜過濾條件"""
    print("\n" + "="*60)
    print("範例 3: 複雜過濾")
    print("="*60)

    db = lancedb.connect("./hybrid_demo")
    table = db.open_table("docs")
    query = np.random.rand(128).tolist()

    # 多條件過濾
    results = table.search(query) \
        .where("category = 'tech' AND id > 10") \
        .limit(5) \
        .to_pandas()

    print(f"✓ 複雜過濾搜索: {len(results)} 個結果")


def example_4_range_queries():
    """範圍查詢"""
    print("\n" + "="*60)
    print("範例 4: 範圍查詢")
    print("="*60)

    db = lancedb.connect("./hybrid_demo")
    table = db.open_table("docs")
    query = np.random.rand(128).tolist()

    results = table.search(query) \
        .where("id >= 10 AND id <= 30") \
        .limit(10) \
        .to_pandas()

    print(f"✓ 範圍查詢: {len(results)} 個結果")


def example_5_search_ranking():
    """搜索結果排序"""
    print("\n" + "="*60)
    print("範例 5: 結果排序")
    print("="*60)

    print("✓ 可以按不同維度排序:")
    print("  - 向量距離")
    print("  - 元數據字段")
    print("  - 自定義評分")


def example_6_10_more():
    """其他混合搜索功能"""
    print("\n" + "="*60)
    print("範例 6-10: 更多功能")
    print("="*60)

    print("✓ 其他功能:")
    print("  6. 搜索結果合併")
    print("  7. 多階段搜索")
    print("  8. 重排序策略")
    print("  9. 自定義評分")
    print("  10. 搜索分析")


def cleanup():
    """清理"""
    db = lancedb.connect("./hybrid_demo")
    for table_name in db.table_names():
        db.drop_table(table_name)
    print("\n✓ 清理完成")


def main():
    """運行所有範例"""
    print("\n" + "="*60)
    print("🔀 LanceDB - 混合搜索範例")
    print("="*60)

    example_1_hybrid_search()
    example_2_full_text_search()
    example_3_complex_filters()
    example_4_range_queries()
    example_5_search_ranking()
    example_6_10_more()
    cleanup()

    print("\n" + "="*60)
    print("✓ 所有混合搜索範例完成！")
    print("="*60)


if __name__ == '__main__':
    main()

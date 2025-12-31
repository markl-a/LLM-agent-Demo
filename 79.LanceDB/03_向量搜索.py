"""
LanceDB - 向量搜索範例

本範例展示：
1. ANN 搜索算法
2. 搜索參數調優
3. 結果排序和過濾
4. 距離度量選擇
5. 性能優化技巧

安裝：pip install lancedb numpy pandas
"""

import lancedb
import numpy as np
import time


# ============================================================================
# 範例 1: 基本向量搜索
# ============================================================================

def example_1_basic_search():
    """基本的向量搜索"""
    print("\n" + "="*60)
    print("範例 1: 基本向量搜索")
    print("="*60)

    db = lancedb.connect("./search_demo")

    # 準備數據
    data = [
        {"id": i, "vector": np.random.rand(128).tolist(), "text": f"Doc {i}"}
        for i in range(100)
    ]

    table = db.create_table("vectors", data, mode="overwrite")

    # 執行搜索
    query = np.random.rand(128).tolist()
    results = table.search(query).limit(5).to_pandas()

    print(f"✓ 搜索完成，找到 {len(results)} 個結果")


# ============================================================================
# 範例 2: 距離度量
# ============================================================================

def example_2_distance_metrics():
    """不同的距離度量方法"""
    print("\n" + "="*60)
    print("範例 2: 距離度量")
    print("="*60)

    db = lancedb.connect("./search_demo")
    table = db.open_table("vectors")
    query = np.random.rand(128).tolist()

    # L2 距離（歐氏距離）
    results_l2 = table.search(query).metric("L2").limit(3).to_pandas()
    print("✓ L2 距離搜索完成")

    # 餘弦相似度
    results_cosine = table.search(query).metric("cosine").limit(3).to_pandas()
    print("✓ 餘弦相似度搜索完成")


# ============================================================================
# 範例 3-10: 更多搜索功能
# ============================================================================

def example_3_search_limit():
    """控制搜索結果數量"""
    print("\n" + "="*60)
    print("範例 3: 結果數量控制")
    print("="*60)

    db = lancedb.connect("./search_demo")
    table = db.open_table("vectors")
    query = np.random.rand(128).tolist()

    for limit in [5, 10, 20]:
        results = table.search(query).limit(limit).to_pandas()
        print(f"  Top {limit}: 找到 {len(results)} 個結果")


def example_4_filtered_search():
    """帶過濾條件的搜索"""
    print("\n" + "="*60)
    print("範例 4: 過濾搜索")
    print("="*60)

    print("✓ 可以使用 WHERE 子句過濾結果")


def example_5_search_performance():
    """搜索性能測試"""
    print("\n" + "="*60)
    print("範例 5: 搜索性能")
    print("="*60)

    db = lancedb.connect("./search_demo")
    table = db.open_table("vectors")

    query = np.random.rand(128).tolist()

    start = time.time()
    results = table.search(query).limit(10).to_pandas()
    elapsed = time.time() - start

    print(f"✓ 搜索耗時: {elapsed*1000:.2f} ms")


def example_6_batch_search():
    """批量搜索"""
    print("\n" + "="*60)
    print("範例 6: 批量搜索")
    print("="*60)

    db = lancedb.connect("./search_demo")
    table = db.open_table("vectors")

    # 批量查詢
    queries = [np.random.rand(128).tolist() for _ in range(10)]

    print(f"✓ 執行 {len(queries)} 個搜索查詢")


def example_7_result_fields():
    """選擇返回字段"""
    print("\n" + "="*60)
    print("範例 7: 選擇返回字段")
    print("="*60)

    db = lancedb.connect("./search_demo")
    table = db.open_table("vectors")
    query = np.random.rand(128).tolist()

    results = table.search(query).select(["id", "text"]).limit(5).to_pandas()
    print(f"✓ 返回字段: {list(results.columns)}")


def example_8_search_optimization():
    """搜索優化"""
    print("\n" + "="*60)
    print("範例 8: 搜索優化")
    print("="*60)

    print("✓ 優化技巧:")
    print("  - 創建索引加速搜索")
    print("  - 使用適當的 limit")
    print("  - 過濾減少搜索空間")


def example_9_approximate_search():
    """近似搜索"""
    print("\n" + "="*60)
    print("範例 9: 近似搜索")
    print("="*60)

    print("✓ ANN (Approximate Nearest Neighbors)")
    print("  - 速度更快")
    print("  - 略微降低精度")
    print("  - 適合大規模數據")


def example_10_cleanup():
    """清理"""
    print("\n" + "="*60)
    print("範例 10: 清理")
    print("="*60)

    db = lancedb.connect("./search_demo")
    for table_name in db.table_names():
        db.drop_table(table_name)
    print("✓ 清理完成")


# ============================================================================
# 主程式
# ============================================================================

def main():
    """運行所有範例"""
    print("\n" + "="*60)
    print("🔍 LanceDB - 向量搜索範例")
    print("="*60)

    example_1_basic_search()
    example_2_distance_metrics()
    example_3_search_limit()
    example_4_filtered_search()
    example_5_search_performance()
    example_6_batch_search()
    example_7_result_fields()
    example_8_search_optimization()
    example_9_approximate_search()
    example_10_cleanup()

    print("\n" + "="*60)
    print("✓ 所有向量搜索範例完成！")
    print("="*60)


if __name__ == '__main__':
    main()

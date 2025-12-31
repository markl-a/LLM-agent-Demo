"""
Milvus 向量搜索示例

本示例展示：
1. 基本向量搜索
2. 搜索參數調優
3. 多向量搜索
4. 範圍搜索
"""

from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import numpy as np

console = Console()


def setup():
    """設置測試環境"""
    connections.connect(alias="default", host='localhost', port='19530')

    if utility.has_collection("search_collection"):
        utility.drop_collection("search_collection")

    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=128),
        FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=100),
        FieldSchema(name="category", dtype=DataType.VARCHAR, max_length=50),
    ]

    schema = CollectionSchema(fields=fields)
    collection = Collection(name="search_collection", schema=schema)

    # 插入測試數據
    num_entities = 1000
    entities = [
        [np.random.random(128).tolist() for _ in range(num_entities)],
        [f"文檔 {i}" for i in range(num_entities)],
        [["科技", "教育", "娛樂"][i % 3] for i in range(num_entities)]
    ]

    collection.insert(entities)
    collection.flush()

    # 創建索引
    index_params = {
        "index_type": "IVF_FLAT",
        "metric_type": "L2",
        "params": {"nlist": 128}
    }
    collection.create_index(field_name="vector", index_params=index_params)
    collection.load()

    console.print("[green]✓ 測試環境準備完成[/green]\n")
    return collection


def basic_search(collection):
    """基本向量搜索"""
    console.print("[bold cyan]1. 基本向量搜索[/bold cyan]")

    search_vectors = [np.random.random(128).tolist()]
    search_params = {"metric_type": "L2", "params": {"nprobe": 10}}

    results = collection.search(
        data=search_vectors,
        anns_field="vector",
        param=search_params,
        limit=5,
        output_fields=["title", "category"]
    )

    table = Table(title="搜索結果")
    table.add_column("排名", style="cyan")
    table.add_column("ID", style="yellow")
    table.add_column("標題", style="green")
    table.add_column("分類", style="magenta")
    table.add_column("距離", style="red")

    for i, hit in enumerate(results[0], 1):
        table.add_row(
            str(i),
            str(hit.id),
            hit.entity.get("title"),
            hit.entity.get("category"),
            f"{hit.distance:.4f}"
        )

    console.print(table)
    console.print()


def search_with_different_params(collection):
    """不同參數的搜索對比"""
    console.print("[bold cyan]2. 不同搜索參數對比[/bold cyan]")

    search_vector = [np.random.random(128).tolist()]

    nprobe_values = [5, 10, 20]

    table = Table(title="nprobe 參數對比")
    table.add_column("nprobe", style="cyan")
    table.add_column("Top-1 距離", style="green")
    table.add_column("搜索時間", style="yellow")

    import time

    for nprobe in nprobe_values:
        search_params = {"metric_type": "L2", "params": {"nprobe": nprobe}}

        start = time.time()
        results = collection.search(
            data=search_vector,
            anns_field="vector",
            param=search_params,
            limit=1
        )
        elapsed = (time.time() - start) * 1000

        distance = results[0][0].distance if results[0] else 0

        table.add_row(
            str(nprobe),
            f"{distance:.4f}",
            f"{elapsed:.2f}ms"
        )

    console.print(table)
    console.print()


def multi_vector_search(collection):
    """多向量批量搜索"""
    console.print("[bold cyan]3. 多向量批量搜索[/bold cyan]")

    search_vectors = [np.random.random(128).tolist() for _ in range(3)]
    search_params = {"metric_type": "L2", "params": {"nprobe": 10}}

    results = collection.search(
        data=search_vectors,
        anns_field="vector",
        param=search_params,
        limit=3,
        output_fields=["title"]
    )

    for idx, result in enumerate(results):
        console.print(f"[cyan]查詢 {idx + 1} 的結果:[/cyan]")
        for i, hit in enumerate(result, 1):
            console.print(f"  {i}. {hit.entity.get('title')} (距離: {hit.distance:.4f})")
        console.print()


def range_search(collection):
    """範圍搜索"""
    console.print("[bold cyan]4. 範圍搜索[/bold cyan]")

    search_vector = [np.random.random(128).tolist()]

    # 使用 radius 和 range_filter
    search_params = {
        "metric_type": "L2",
        "params": {
            "nprobe": 10,
            "radius": 10.0,  # 最大距離
            "range_filter": 0.0  # 最小距離
        }
    }

    results = collection.search(
        data=search_vector,
        anns_field="vector",
        param=search_params,
        limit=100,
        output_fields=["title"]
    )

    console.print(f"[green]找到 {len(results[0])} 個在範圍內的結果[/green]")

    # 顯示前5個
    for i, hit in enumerate(results[0][:5], 1):
        console.print(f"  {i}. {hit.entity.get('title')} (距離: {hit.distance:.4f})")

    console.print()


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Milvus 向量搜索示例[/bold cyan]",
        border_style="cyan"
    ))

    collection = setup()

    # 1. 基本搜索
    basic_search(collection)

    # 2. 參數對比
    search_with_different_params(collection)

    # 3. 多向量搜索
    multi_vector_search(collection)

    # 4. 範圍搜索
    range_search(collection)

    console.print("="*60)
    console.print("[bold green]✓ 向量搜索示例完成！[/bold green]")

    # 清理
    utility.drop_collection("search_collection")
    connections.disconnect("default")


if __name__ == "__main__":
    main()

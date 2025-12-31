"""
Milvus 標量過濾示例

本示例展示：
1. 基本過濾表達式
2. 混合搜索（向量+過濾）
3. 複雜過濾條件
4. 過濾性能優化
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

    if utility.has_collection("filter_collection"):
        utility.drop_collection("filter_collection")

    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=False),
        FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=128),
        FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=100),
        FieldSchema(name="category", dtype=DataType.VARCHAR, max_length=50),
        FieldSchema(name="score", dtype=DataType.FLOAT),
        FieldSchema(name="views", dtype=DataType.INT64),
    ]

    schema = CollectionSchema(fields=fields)
    collection = Collection(name="filter_collection", schema=schema)

    # 插入測試數據
    categories = ["科技", "教育", "娛樂", "體育", "財經"]
    num_entities = 500

    entities = [
        list(range(num_entities)),
        [np.random.random(128).tolist() for _ in range(num_entities)],
        [f"文章 {i}" for i in range(num_entities)],
        [categories[i % len(categories)] for i in range(num_entities)],
        [round(np.random.uniform(1.0, 10.0), 2) for _ in range(num_entities)],
        [np.random.randint(0, 10000) for _ in range(num_entities)]
    ]

    collection.insert(entities)
    collection.flush()

    # 創建索引
    index_params = {"index_type": "IVF_FLAT", "metric_type": "L2", "params": {"nlist": 64}}
    collection.create_index(field_name="vector", index_params=index_params)
    collection.load()

    console.print("[green]✓ 測試環境準備完成[/green]\n")
    return collection


def basic_filter_query(collection):
    """基本過濾查詢"""
    console.print("[bold cyan]1. 基本過濾查詢[/bold cyan]")

    # 過濾表達式
    expr = "category == '科技'"

    results = collection.query(
        expr=expr,
        output_fields=["title", "category", "score"],
        limit=5
    )

    table = Table(title="過濾結果: category == '科技'")
    table.add_column("ID", style="cyan")
    table.add_column("標題", style="green")
    table.add_column("分類", style="yellow")
    table.add_column("評分", style="magenta")

    for result in results:
        table.add_row(
            str(result["id"]),
            result["title"],
            result["category"],
            str(result["score"])
        )

    console.print(table)
    console.print()


def hybrid_search(collection):
    """混合搜索（向量+過濾）"""
    console.print("[bold cyan]2. 混合搜索（向量+過濾）[/bold cyan]")

    search_vector = [np.random.random(128).tolist()]
    search_params = {"metric_type": "L2", "params": {"nprobe": 10}}

    # 過濾條件：分類為"科技"且評分大於7
    expr = "category == '科技' and score > 7.0"

    results = collection.search(
        data=search_vector,
        anns_field="vector",
        param=search_params,
        limit=5,
        expr=expr,
        output_fields=["title", "category", "score"]
    )

    console.print(f"[yellow]過濾條件: {expr}[/yellow]\n")

    table = Table(title="混合搜索結果")
    table.add_column("排名", style="cyan")
    table.add_column("標題", style="green")
    table.add_column("評分", style="yellow")
    table.add_column("距離", style="red")

    for i, hit in enumerate(results[0], 1):
        table.add_row(
            str(i),
            hit.entity.get("title"),
            str(hit.entity.get("score")),
            f"{hit.distance:.4f}"
        )

    console.print(table)
    console.print()


def complex_filter_expressions(collection):
    """複雜過濾表達式"""
    console.print("[bold cyan]3. 複雜過濾表達式[/bold cyan]")

    expressions = [
        ("範圍過濾", "score >= 5.0 and score <= 8.0"),
        ("IN 操作符", "category in ['科技', '教育']"),
        ("複合條件", "(category == '科技' and score > 7) or (category == '教育' and views > 5000)"),
        ("LIKE 操作符", "title like '文章 1%'"),
    ]

    for name, expr in expressions:
        results = collection.query(
            expr=expr,
            output_fields=["title", "category", "score", "views"],
            limit=3
        )

        console.print(f"[cyan]{name}:[/cyan] {expr}")
        console.print(f"[green]找到 {len(results)} 條結果[/green]")
        if results:
            for r in results[:2]:
                console.print(f"  • {r['title']} - {r['category']}")
        console.print()


def filter_performance_comparison(collection):
    """過濾性能對比"""
    console.print("[bold cyan]4. 過濾性能對比[/bold cyan]")

    import time

    search_vector = [np.random.random(128).tolist()]
    search_params = {"metric_type": "L2", "params": {"nprobe": 10}}

    # 測試1: 無過濾
    start = time.time()
    results1 = collection.search(
        data=search_vector,
        anns_field="vector",
        param=search_params,
        limit=10
    )
    time1 = (time.time() - start) * 1000

    # 測試2: 簡單過濾
    start = time.time()
    results2 = collection.search(
        data=search_vector,
        anns_field="vector",
        param=search_params,
        limit=10,
        expr="category == '科技'"
    )
    time2 = (time.time() - start) * 1000

    # 測試3: 複雜過濾
    start = time.time()
    results3 = collection.search(
        data=search_vector,
        anns_field="vector",
        param=search_params,
        limit=10,
        expr="category == '科技' and score > 5.0 and views > 1000"
    )
    time3 = (time.time() - start) * 1000

    table = Table(title="性能對比")
    table.add_column("測試", style="cyan")
    table.add_column("過濾條件", style="yellow")
    table.add_column("結果數", style="green")
    table.add_column("耗時", style="magenta")

    table.add_row("無過濾", "無", str(len(results1[0])), f"{time1:.2f}ms")
    table.add_row("簡單過濾", "category == '科技'", str(len(results2[0])), f"{time2:.2f}ms")
    table.add_row("複雜過濾", "三個條件", str(len(results3[0])), f"{time3:.2f}ms")

    console.print(table)
    console.print()


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Milvus 標量過濾示例[/bold cyan]",
        border_style="cyan"
    ))

    collection = setup()

    # 1. 基本過濾
    basic_filter_query(collection)

    # 2. 混合搜索
    hybrid_search(collection)

    # 3. 複雜過濾表達式
    complex_filter_expressions(collection)

    # 4. 性能對比
    filter_performance_comparison(collection)

    console.print("="*60)
    console.print("[bold green]✓ 標量過濾示例完成！[/bold green]")

    # 清理
    utility.drop_collection("filter_collection")
    connections.disconnect("default")


if __name__ == "__main__":
    main()

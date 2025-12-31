"""
Milvus 分區管理示例

本示例展示：
1. 創建和刪除分區
2. 在分區中插入數據
3. 分區級別搜索
4. 分區管理最佳實踐
"""

from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility, Partition
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import numpy as np

console = Console()


def setup():
    """設置測試環境"""
    connections.connect(alias="default", host='localhost', port='19530')

    if utility.has_collection("partition_collection"):
        utility.drop_collection("partition_collection")

    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=128),
        FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=200),
    ]

    schema = CollectionSchema(fields=fields)
    collection = Collection(name="partition_collection", schema=schema)

    console.print("[green]✓ 集合創建成功[/green]\n")
    return collection


def create_partitions(collection):
    """創建分區"""
    console.print("[bold cyan]1. 創建分區[/bold cyan]")

    partition_names = ["partition_2023", "partition_2024", "partition_2025"]

    for name in partition_names:
        partition = collection.create_partition(name)
        console.print(f"[green]✓ 創建分區: {name}[/green]")

    console.print()


def list_partitions(collection):
    """列出所有分區"""
    console.print("[bold cyan]2. 列出所有分區[/bold cyan]")

    partitions = collection.partitions

    table = Table(title="分區列表")
    table.add_column("分區名稱", style="cyan")
    table.add_column("數據量", style="green")

    for partition in partitions:
        table.add_row(partition.name, str(partition.num_entities))

    console.print(table)
    console.print()


def insert_into_partitions(collection):
    """向分區插入數據"""
    console.print("[bold cyan]3. 向分區插入數據[/bold cyan]")

    partitions_data = {
        "partition_2023": 100,
        "partition_2024": 200,
        "partition_2025": 150
    }

    for partition_name, num_entities in partitions_data.items():
        entities = [
            [np.random.random(128).tolist() for _ in range(num_entities)],
            [f"{partition_name}_文檔_{i}" for i in range(num_entities)]
        ]

        collection.insert(entities, partition_name=partition_name)
        console.print(f"[green]✓ 向 {partition_name} 插入 {num_entities} 條數據[/green]")

    collection.flush()
    console.print()


def search_in_partition(collection):
    """在特定分區中搜索"""
    console.print("[bold cyan]4. 在特定分區中搜索[/bold cyan]")

    # 創建索引
    index_params = {"index_type": "IVF_FLAT", "metric_type": "L2", "params": {"nlist": 64}}
    collection.create_index(field_name="vector", index_params=index_params)

    # 加載特定分區
    collection.load(partition_names=["partition_2024"])

    search_vector = [np.random.random(128).tolist()]
    search_params = {"metric_type": "L2", "params": {"nprobe": 10}}

    # 只在 partition_2024 中搜索
    results = collection.search(
        data=search_vector,
        anns_field="vector",
        param=search_params,
        limit=3,
        partition_names=["partition_2024"],
        output_fields=["text"]
    )

    console.print("[yellow]在 partition_2024 中搜索:[/yellow]")
    for i, hit in enumerate(results[0], 1):
        console.print(f"  {i}. {hit.entity.get('text')} (距離: {hit.distance:.4f})")

    console.print()


def drop_partition(collection):
    """刪除分區"""
    console.print("[bold cyan]5. 刪除分區[/bold cyan]")

    partition_name = "partition_2023"

    if collection.has_partition(partition_name):
        collection.drop_partition(partition_name)
        console.print(f"[green]✓ 分區已刪除: {partition_name}[/green]")

    console.print()


def partition_best_practices():
    """分區最佳實踐"""
    console.print("[bold cyan]6. 分區最佳實踐[/bold cyan]")

    practices = [
        ("時間分區", "按日期/時間範圍分區,便於數據管理"),
        ("類別分區", "按業務類別分區,提升搜索效率"),
        ("分區數量", "避免創建過多分區,建議<100個"),
        ("負載均衡", "均勻分配數據到各分區"),
        ("按需加載", "只加載需要搜索的分區"),
        ("定期清理", "刪除過期分區釋放資源"),
    ]

    table = Table(title="分區管理最佳實踐")
    table.add_column("場景", style="cyan", width=12)
    table.add_column("建議", style="green", width=40)

    for scenario, advice in practices:
        table.add_row(scenario, advice)

    console.print(table)


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Milvus 分區管理示例[/bold cyan]",
        border_style="cyan"
    ))

    collection = setup()

    # 1. 創建分區
    create_partitions(collection)

    # 2. 列出分區
    list_partitions(collection)

    # 3. 插入數據到分區
    insert_into_partitions(collection)

    # 4. 在分區中搜索
    search_in_partition(collection)

    # 5. 刪除分區
    drop_partition(collection)

    # 6. 最佳實踐
    partition_best_practices()

    console.print("\n" + "="*60)
    console.print("[bold green]✓ 分區管理示例完成！[/bold green]")

    # 清理
    utility.drop_collection("partition_collection")
    connections.disconnect("default")


if __name__ == "__main__":
    main()

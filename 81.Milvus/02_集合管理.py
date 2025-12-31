"""
Milvus 集合管理示例

本示例展示：
1. 創建和刪除集合
2. Schema 設計
3. 集合屬性查詢
4. 集合列表管理
"""

from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def connect():
    """連接到 Milvus"""
    connections.connect(alias="default", host='localhost', port='19530')
    console.print("[green]✓ 已連接到 Milvus[/green]\n")


def create_basic_collection():
    """創建基本集合"""
    console.print("[bold cyan]1. 創建基本集合[/bold cyan]")

    # 定義字段
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=256),
        FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=500),
    ]

    schema = CollectionSchema(fields=fields, description="基本集合")

    collection = Collection(name="basic_collection", schema=schema)

    console.print(f"[green]✓ 創建成功: {collection.name}[/green]\n")
    return collection


def create_advanced_collection():
    """創建進階集合"""
    console.print("[bold cyan]2. 創建進階集合[/bold cyan]")

    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=False),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=512),
        FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=200),
        FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=2000),
        FieldSchema(name="score", dtype=DataType.FLOAT),
        FieldSchema(name="timestamp", dtype=DataType.INT64),
        FieldSchema(name="tags", dtype=DataType.ARRAY, element_type=DataType.VARCHAR, max_capacity=10, max_length=50),
    ]

    schema = CollectionSchema(
        fields=fields,
        description="進階集合示例",
        enable_dynamic_field=True  # 啟用動態字段
    )

    collection = Collection(name="advanced_collection", schema=schema)

    console.print(f"[green]✓ 創建成功: {collection.name}[/green]")
    console.print(f"[dim]動態字段: 已啟用[/dim]\n")

    return collection


def list_collections():
    """列出所有集合"""
    console.print("[bold cyan]3. 列出所有集合[/bold cyan]")

    collections = utility.list_collections()

    table = Table(title="集合列表")
    table.add_column("集合名稱", style="cyan")

    for coll_name in collections:
        table.add_row(coll_name)

    console.print(table)
    console.print()


def get_collection_info(collection):
    """獲取集合信息"""
    console.print("[bold cyan]4. 獲取集合信息[/bold cyan]")

    # 基本信息
    console.print(f"[cyan]集合名稱:[/cyan] {collection.name}")
    console.print(f"[cyan]描述:[/cyan] {collection.description}")
    console.print(f"[cyan]字段數量:[/cyan] {len(collection.schema.fields)}")

    # 字段詳情
    table = Table(title="字段詳情")
    table.add_column("字段名", style="cyan")
    table.add_column("類型", style="green")
    table.add_column("維度/長度", style="yellow")
    table.add_column("主鍵", style="magenta")

    for field in collection.schema.fields:
        is_primary = "✓" if field.is_primary else ""
        dim_len = ""
        if field.dtype == DataType.FLOAT_VECTOR:
            dim_len = f"dim={field.params.get('dim', 'N/A')}"
        elif field.dtype == DataType.VARCHAR:
            dim_len = f"max={field.params.get('max_length', 'N/A')}"

        table.add_row(
            field.name,
            str(field.dtype).split('.')[-1],
            dim_len,
            is_primary
        )

    console.print(table)
    console.print()


def rename_collection():
    """重命名集合"""
    console.print("[bold cyan]5. 重命名集合[/bold cyan]")

    old_name = "basic_collection"
    new_name = "renamed_collection"

    if utility.has_collection(old_name):
        utility.rename_collection(old_name, new_name)
        console.print(f"[green]✓ 集合已重命名: {old_name} -> {new_name}[/green]\n")
    else:
        console.print(f"[yellow]集合不存在: {old_name}[/yellow]\n")


def drop_collection(collection_name):
    """刪除集合"""
    console.print(f"[yellow]刪除集合: {collection_name}[/yellow]")

    if utility.has_collection(collection_name):
        utility.drop_collection(collection_name)
        console.print(f"[green]✓ 集合已刪除: {collection_name}[/green]\n")


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Milvus 集合管理示例[/bold cyan]",
        border_style="cyan"
    ))

    connect()

    # 清理舊集合
    for name in ["basic_collection", "advanced_collection", "renamed_collection"]:
        if utility.has_collection(name):
            utility.drop_collection(name)

    # 1. 創建基本集合
    basic_coll = create_basic_collection()

    # 2. 創建進階集合
    advanced_coll = create_advanced_collection()

    # 3. 列出集合
    list_collections()

    # 4. 獲取集合信息
    get_collection_info(advanced_coll)

    # 5. 重命名集合
    rename_collection()

    # 6. 列出集合（查看重命名結果）
    list_collections()

    # 清理
    for name in ["renamed_collection", "advanced_collection"]:
        drop_collection(name)

    console.print("="*60)
    console.print("[bold green]✓ 集合管理示例完成！[/bold green]")

    connections.disconnect("default")


if __name__ == "__main__":
    main()

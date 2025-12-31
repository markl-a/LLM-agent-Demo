"""
Milvus 快速開始示例

本示例展示：
1. 連接到 Milvus
2. 創建集合
3. 插入數據
4. 向量搜索
"""

from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import numpy as np

console = Console()


def connect_to_milvus():
    """連接到 Milvus"""
    try:
        console.print("\n[cyan]正在連接到 Milvus...[/cyan]")

        # 方式 1: 連接到本地 Milvus
        connections.connect(
            alias="default",
            host='localhost',
            port='19530'
        )

        # 方式 2: 連接到 Zilliz Cloud
        # connections.connect(
        #     alias="default",
        #     uri="https://your-cluster.aws-us-west-2.vectordb.zillizcloud.com:port",
        #     token="your-api-key"
        # )

        console.print("[green]✓ 成功連接到 Milvus[/green]")
        return True

    except Exception as e:
        console.print(f"[red]✗ 連接失敗: {e}[/red]")
        console.print("\n[yellow]請確保 Milvus 正在運行:[/yellow]")
        console.print("  docker-compose up -d")
        return False


def check_milvus_version():
    """檢查 Milvus 版本"""
    try:
        console.print("\n[cyan]檢查 Milvus 版本...[/cyan]")

        # 獲取服務器版本
        version = utility.get_server_version()

        table = Table(title="Milvus 信息")
        table.add_column("項目", style="cyan")
        table.add_column("值", style="green")

        table.add_row("服務器版本", version)

        console.print(table)
        console.print()

    except Exception as e:
        console.print(f"[red]✗ 檢查版本失敗: {e}[/red]")


def create_collection():
    """創建集合"""
    try:
        console.print("[cyan]創建集合...[/cyan]")

        # 定義字段 Schema
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=False),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=128),
            FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=200),
            FieldSchema(name="category", dtype=DataType.VARCHAR, max_length=100),
        ]

        # 創建 Collection Schema
        schema = CollectionSchema(
            fields=fields,
            description="示例集合"
        )

        # 創建 Collection
        collection_name = "demo_collection"

        # 如果集合已存在，先刪除
        if utility.has_collection(collection_name):
            utility.drop_collection(collection_name)
            console.print(f"[yellow]已刪除舊集合: {collection_name}[/yellow]")

        collection = Collection(
            name=collection_name,
            schema=schema
        )

        console.print(f"[green]✓ 集合創建成功: {collection_name}[/green]")
        console.print(f"[dim]字段: id, embedding(128), title, category[/dim]\n")

        return collection

    except Exception as e:
        console.print(f"[red]✗ 創建集合失敗: {e}[/red]")
        return None


def insert_data(collection):
    """插入示例數據"""
    try:
        console.print("[cyan]插入示例數據...[/cyan]")

        # 準備示例數據
        num_entities = 10

        entities = [
            # ID 列表
            list(range(num_entities)),
            # 向量列表（隨機生成）
            [np.random.random(128).tolist() for _ in range(num_entities)],
            # 標題列表
            [f"文檔 {i}" for i in range(num_entities)],
            # 分類列表
            ["科技", "教育", "娛樂", "體育", "財經"] * 2
        ]

        # 插入數據
        insert_result = collection.insert(entities)

        console.print(f"[green]✓ 成功插入 {num_entities} 條數據[/green]")
        console.print(f"[dim]插入的 IDs: {insert_result.primary_keys[:5]}...[/dim]\n")

        return True

    except Exception as e:
        console.print(f"[red]✗ 插入數據失敗: {e}[/red]")
        return False


def create_index(collection):
    """創建索引"""
    try:
        console.print("[cyan]創建索引...[/cyan]")

        # 定義索引參數
        index_params = {
            "index_type": "IVF_FLAT",
            "metric_type": "L2",
            "params": {"nlist": 128}
        }

        # 創建索引
        collection.create_index(
            field_name="embedding",
            index_params=index_params
        )

        console.print("[green]✓ 索引創建成功[/green]")
        console.print("[dim]索引類型: IVF_FLAT, 度量: L2[/dim]\n")

        return True

    except Exception as e:
        console.print(f"[red]✗ 創建索引失敗: {e}[/red]")
        return False


def load_collection(collection):
    """加載集合到內存"""
    try:
        console.print("[cyan]加載集合到內存...[/cyan]")

        collection.load()

        console.print("[green]✓ 集合已加載[/green]\n")

        return True

    except Exception as e:
        console.print(f"[red]✗ 加載集合失敗: {e}[/red]")
        return False


def search_vectors(collection):
    """搜索向量"""
    try:
        console.print("[cyan]執行向量搜索...[/cyan]")

        # 生成查詢向量
        search_vectors = [np.random.random(128).tolist()]

        # 搜索參數
        search_params = {
            "metric_type": "L2",
            "params": {"nprobe": 10}
        }

        # 執行搜索
        results = collection.search(
            data=search_vectors,
            anns_field="embedding",
            param=search_params,
            limit=5,
            output_fields=["title", "category"]
        )

        # 顯示結果
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

        return True

    except Exception as e:
        console.print(f"[red]✗ 搜索失敗: {e}[/red]")
        return False


def cleanup(collection):
    """清理資源"""
    try:
        console.print("[cyan]清理資源...[/cyan]")

        # 釋放集合
        collection.release()

        # 刪除集合（可選）
        # utility.drop_collection(collection.name)
        # console.print(f"[dim]✓ 已刪除集合: {collection.name}[/dim]")

        # 斷開連接
        connections.disconnect("default")
        console.print("[green]✓ 已斷開連接[/green]")

    except Exception as e:
        console.print(f"[red]清理失敗: {e}[/red]")


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Milvus 快速開始示例[/bold cyan]",
        border_style="cyan"
    ))

    # 1. 連接到 Milvus
    if not connect_to_milvus():
        return

    # 2. 檢查版本
    check_milvus_version()

    # 3. 創建集合
    collection = create_collection()
    if not collection:
        return

    # 4. 插入數據
    if not insert_data(collection):
        return

    # 5. 創建索引
    if not create_index(collection):
        return

    # 6. 加載集合
    if not load_collection(collection):
        return

    # 7. 搜索向量
    search_vectors(collection)

    # 完成
    console.print("="*60)
    console.print("[bold green]✓ 快速開始示例完成！[/bold green]")
    console.print("\n[cyan]下一步:[/cyan]")
    console.print("  1. 查看 02_集合管理.py 學習集合管理")
    console.print("  2. 查看 04_向量搜索.py 學習高級搜索")
    console.print("  3. 查看 08_LangChain整合.py 學習 RAG 應用")

    # 清理
    cleanup(collection)


if __name__ == "__main__":
    main()

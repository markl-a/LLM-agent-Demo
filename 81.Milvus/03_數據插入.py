"""
Milvus 數據插入示例

本示例展示：
1. 單條數據插入
2. 批量數據插入
3. 使用 auto_id
4. 數據驗證
"""

from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
from rich.console import Console
from rich.panel import Panel
from rich.progress import track
import numpy as np
import time

console = Console()


def setup():
    """設置環境"""
    connections.connect(alias="default", host='localhost', port='19530')

    if utility.has_collection("data_collection"):
        utility.drop_collection("data_collection")

    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=False),
        FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=128),
        FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=200),
        FieldSchema(name="views", dtype=DataType.INT64),
    ]

    schema = CollectionSchema(fields=fields)
    collection = Collection(name="data_collection", schema=schema)

    console.print("[green]✓ 環境設置完成[/green]\n")
    return collection


def single_insert(collection):
    """單條數據插入"""
    console.print("[bold cyan]1. 單條數據插入[/bold cyan]")

    entity = [
        [0],  # id
        [np.random.random(128).tolist()],  # vector
        ["第一篇文章"],  # title
        [100]  # views
    ]

    result = collection.insert(entity)
    console.print(f"[green]✓ 插入成功, ID: {result.primary_keys[0]}[/green]\n")


def batch_insert(collection):
    """批量數據插入"""
    console.print("[bold cyan]2. 批量數據插入[/bold cyan]")

    num_entities = 1000

    entities = [
        list(range(1, num_entities + 1)),  # ids
        [np.random.random(128).tolist() for _ in range(num_entities)],  # vectors
        [f"文章 {i}" for i in range(1, num_entities + 1)],  # titles
        [np.random.randint(0, 10000) for _ in range(num_entities)]  # views
    ]

    start_time = time.time()
    result = collection.insert(entities)
    elapsed_time = time.time() - start_time

    console.print(f"[green]✓ 成功插入 {num_entities} 條數據[/green]")
    console.print(f"[dim]耗時: {elapsed_time:.2f} 秒[/dim]")
    console.print(f"[dim]吞吐量: {num_entities/elapsed_time:.0f} 條/秒[/dim]\n")


def insert_with_progress(collection):
    """帶進度條的批量插入"""
    console.print("[bold cyan]3. 帶進度條的批量插入[/bold cyan]")

    batch_size = 100
    num_batches = 10

    total_inserted = 0

    for batch_idx in track(range(num_batches), description="插入數據..."):
        start_id = 1001 + batch_idx * batch_size

        entities = [
            list(range(start_id, start_id + batch_size)),
            [np.random.random(128).tolist() for _ in range(batch_size)],
            [f"批次{batch_idx}_文章{i}" for i in range(batch_size)],
            [np.random.randint(0, 5000) for _ in range(batch_size)]
        ]

        collection.insert(entities)
        total_inserted += batch_size

    console.print(f"[green]✓ 總共插入 {total_inserted} 條數據[/green]\n")


def verify_data(collection):
    """驗證插入的數據"""
    console.print("[bold cyan]4. 驗證數據[/bold cyan]")

    # 刷新數據
    collection.flush()

    # 獲取統計信息
    num_entities = collection.num_entities

    console.print(f"[green]✓ 集合中共有 {num_entities} 條數據[/green]\n")


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Milvus 數據插入示例[/bold cyan]",
        border_style="cyan"
    ))

    collection = setup()

    # 1. 單條插入
    single_insert(collection)

    # 2. 批量插入
    batch_insert(collection)

    # 3. 帶進度條插入
    insert_with_progress(collection)

    # 4. 驗證數據
    verify_data(collection)

    console.print("="*60)
    console.print("[bold green]✓ 數據插入示例完成！[/bold green]")

    # 清理
    utility.drop_collection("data_collection")
    connections.disconnect("default")


if __name__ == "__main__":
    main()

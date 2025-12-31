"""
Milvus 索引優化示例

本示例展示：
1. 不同索引類型對比
2. 索引參數調優
3. 性能測試
4. 索引選擇建議
"""

from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import numpy as np
import time

console = Console()


def create_test_collection(name, num_entities=10000):
    """創建測試集合"""
    if utility.has_collection(name):
        utility.drop_collection(name)

    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=128),
    ]

    schema = CollectionSchema(fields=fields)
    collection = Collection(name=name, schema=schema)

    # 插入測試數據
    entities = [[np.random.random(128).tolist() for _ in range(num_entities)]]
    collection.insert(entities)
    collection.flush()

    return collection


def test_flat_index():
    """測試 FLAT 索引"""
    console.print("[bold cyan]1. FLAT 索引 (精確搜索)[/bold cyan]")

    connections.connect(alias="default", host='localhost', port='19530')
    collection = create_test_collection("flat_collection", 1000)

    # 創建 FLAT 索引
    index_params = {
        "index_type": "FLAT",
        "metric_type": "L2",
        "params": {}
    }

    start = time.time()
    collection.create_index(field_name="vector", index_params=index_params)
    build_time = time.time() - start

    collection.load()

    # 測試搜索性能
    search_vector = [np.random.random(128).tolist()]
    search_params = {"metric_type": "L2", "params": {}}

    start = time.time()
    results = collection.search(data=search_vector, anns_field="vector", param=search_params, limit=10)
    search_time = (time.time() - start) * 1000

    console.print(f"  構建時間: {build_time:.2f}s")
    console.print(f"  搜索時間: {search_time:.2f}ms")
    console.print(f"  [green]優點: 100%召回率, 精確搜索[/green]")
    console.print(f"  [yellow]缺點: 大數據集性能差[/yellow]\n")

    utility.drop_collection("flat_collection")


def test_ivf_flat_index():
    """測試 IVF_FLAT 索引"""
    console.print("[bold cyan]2. IVF_FLAT 索引 (平衡型)[/bold cyan]")

    collection = create_test_collection("ivf_flat_collection", 10000)

    # 創建 IVF_FLAT 索引
    index_params = {
        "index_type": "IVF_FLAT",
        "metric_type": "L2",
        "params": {"nlist": 128}
    }

    start = time.time()
    collection.create_index(field_name="vector", index_params=index_params)
    build_time = time.time() - start

    collection.load()

    # 測試不同 nprobe 值
    search_vector = [np.random.random(128).tolist()]

    table = Table(title="IVF_FLAT 性能測試")
    table.add_column("nprobe", style="cyan")
    table.add_column("搜索時間", style="green")

    for nprobe in [1, 10, 50, 128]:
        search_params = {"metric_type": "L2", "params": {"nprobe": nprobe}}

        start = time.time()
        results = collection.search(data=search_vector, anns_field="vector", param=search_params, limit=10)
        search_time = (time.time() - start) * 1000

        table.add_row(str(nprobe), f"{search_time:.2f}ms")

    console.print(table)
    console.print(f"  構建時間: {build_time:.2f}s")
    console.print(f"  [green]優點: 速度和精度平衡[/green]")
    console.print(f"  [yellow]適用: 中等規模數據集[/yellow]\n")

    utility.drop_collection("ivf_flat_collection")


def test_hnsw_index():
    """測試 HNSW 索引"""
    console.print("[bold cyan]3. HNSW 索引 (高性能)[/bold cyan]")

    collection = create_test_collection("hnsw_collection", 10000)

    # 創建 HNSW 索引
    index_params = {
        "index_type": "HNSW",
        "metric_type": "L2",
        "params": {
            "M": 16,
            "efConstruction": 200
        }
    }

    start = time.time()
    collection.create_index(field_name="vector", index_params=index_params)
    build_time = time.time() - start

    collection.load()

    # 測試不同 ef 值
    search_vector = [np.random.random(128).tolist()]

    table = Table(title="HNSW 性能測試")
    table.add_column("ef", style="cyan")
    table.add_column("搜索時間", style="green")

    for ef in [16, 64, 128, 256]:
        search_params = {"metric_type": "L2", "params": {"ef": ef}}

        start = time.time()
        results = collection.search(data=search_vector, anns_field="vector", param=search_params, limit=10)
        search_time = (time.time() - start) * 1000

        table.add_row(str(ef), f"{search_time:.2f}ms")

    console.print(table)
    console.print(f"  構建時間: {build_time:.2f}s")
    console.print(f"  [green]優點: 高召回率, 快速搜索[/green]")
    console.print(f"  [yellow]適用: 生產環境, 大規模數據[/yellow]\n")

    utility.drop_collection("hnsw_collection")


def index_selection_guide():
    """索引選擇指南"""
    console.print("[bold cyan]4. 索引選擇指南[/bold cyan]")

    guide = [
        ("FLAT", "< 10萬", "100%", "最慢", "測試/小數據"),
        ("IVF_FLAT", "10萬-1000萬", "> 95%", "中等", "中等規模"),
        ("IVF_SQ8", "100萬-5000萬", "> 90%", "快", "內存受限"),
        ("IVF_PQ", "> 1000萬", "> 85%", "最快", "大規模/壓縮"),
        ("HNSW", "10萬-1億", "> 99%", "快", "生產環境"),
        ("ANNOY", "< 1000萬", "> 90%", "快", "靜態數據"),
    ]

    table = Table(title="索引類型選擇指南")
    table.add_column("索引類型", style="cyan")
    table.add_column("數據規模", style="yellow")
    table.add_column("召回率", style="green")
    table.add_column("速度", style="magenta")
    table.add_column("推薦場景", style="blue")

    for idx_type, scale, recall, speed, scenario in guide:
        table.add_row(idx_type, scale, recall, speed, scenario)

    console.print(table)


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Milvus 索引優化示例[/bold cyan]",
        border_style="cyan"
    ))

    connections.connect(alias="default", host='localhost', port='19530')

    # 1. FLAT 索引
    test_flat_index()

    # 2. IVF_FLAT 索引
    test_ivf_flat_index()

    # 3. HNSW 索引
    test_hnsw_index()

    # 4. 選擇指南
    index_selection_guide()

    console.print("="*60)
    console.print("[bold green]✓ 索引優化示例完成！[/bold green]")

    connections.disconnect("default")


if __name__ == "__main__":
    main()

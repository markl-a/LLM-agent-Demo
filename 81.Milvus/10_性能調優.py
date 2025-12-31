"""
Milvus 性能調優示例

本示例展示：
1. 性能基準測試
2. 參數優化
3. 監控指標
4. 故障排查
"""

from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import numpy as np
import time

console = Console()


def performance_benchmark():
    """性能基準測試"""
    console.print("[bold cyan]1. 性能基準測試[/bold cyan]")

    connections.connect(alias="default", host='localhost', port='19530')

    # 創建測試集合
    if utility.has_collection("benchmark"):
        utility.drop_collection("benchmark")

    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=128),
    ]

    schema = CollectionSchema(fields=fields)
    collection = Collection(name="benchmark", schema=schema)

    # 測試1: 插入性能
    console.print("\n[yellow]測試1: 批量插入性能[/yellow]")

    batch_sizes = [100, 500, 1000]
    results = []

    for batch_size in batch_sizes:
        vectors = [[np.random.random(128).tolist() for _ in range(batch_size)]]

        start = time.time()
        collection.insert(vectors)
        collection.flush()
        elapsed = time.time() - start

        throughput = batch_size / elapsed

        results.append((batch_size, elapsed, throughput))

    table = Table(title="插入性能測試")
    table.add_column("批次大小", style="cyan")
    table.add_column("耗時 (秒)", style="yellow")
    table.add_column("吞吐量 (條/秒)", style="green")

    for batch_size, elapsed, throughput in results:
        table.add_row(
            str(batch_size),
            f"{elapsed:.2f}",
            f"{throughput:.0f}"
        )

    console.print(table)

    # 測試2: 搜索性能
    console.print("\n[yellow]測試2: 搜索性能[/yellow]")

    # 創建索引
    index_params = {"index_type": "IVF_FLAT", "metric_type": "L2", "params": {"nlist": 128}}
    collection.create_index(field_name="vector", index_params=index_params)
    collection.load()

    search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
    search_vector = [np.random.random(128).tolist()]

    # 預熱
    for _ in range(5):
        collection.search(data=search_vector, anns_field="vector", param=search_params, limit=10)

    # 正式測試
    num_queries = 100
    start = time.time()

    for _ in range(num_queries):
        collection.search(data=search_vector, anns_field="vector", param=search_params, limit=10)

    elapsed = time.time() - start
    qps = num_queries / elapsed
    latency = (elapsed / num_queries) * 1000

    console.print(f"  查詢數量: {num_queries}")
    console.print(f"  總耗時: {elapsed:.2f}s")
    console.print(f"  QPS: {qps:.0f}")
    console.print(f"  平均延遲: {latency:.2f}ms\n")

    utility.drop_collection("benchmark")


def parameter_tuning():
    """參數優化"""
    console.print("[bold cyan]2. 參數優化建議[/bold cyan]")

    # IVF 參數調優
    ivf_params = [
        ("nlist", "聚類數量", "數據量的 4√ 到 16√", "1000"),
        ("nprobe", "搜索聚類數", "1-nlist", "10-128"),
        ("m", "PQ 子向量數", "dim/8 到 dim/4", "8"),
    ]

    table1 = Table(title="IVF 系列索引參數調優")
    table1.add_column("參數", style="cyan")
    table1.add_column("說明", style="yellow")
    table1.add_column("推薦範圍", style="green")
    table1.add_column("示例", style="magenta")

    for param, desc, range_val, example in ivf_params:
        table1.add_row(param, desc, range_val, example)

    console.print(table1)

    # HNSW 參數調優
    hnsw_params = [
        ("M", "每層最大連接數", "4-64", "16"),
        ("efConstruction", "構建時搜索範圍", "100-500", "200"),
        ("ef", "搜索時搜索範圍", "top_k 到 10×top_k", "64"),
    ]

    table2 = Table(title="HNSW 索引參數調優")
    table2.add_column("參數", style="cyan")
    table2.add_column("說明", style="yellow")
    table2.add_column("推薦範圍", style="green")
    table2.add_column("示例", style="magenta")

    for param, desc, range_val, example in hnsw_params:
        table2.add_row(param, desc, range_val, example)

    console.print(table2)
    console.print()


def monitoring_metrics():
    """監控指標"""
    console.print("[bold cyan]3. 關鍵監控指標[/bold cyan]")

    metrics = [
        ("系統指標", "CPU 使用率", "< 80%", "資源是否充足"),
        ("系統指標", "內存使用率", "< 85%", "是否需要擴容"),
        ("系統指標", "磁盤 I/O", "< 80%", "存儲性能"),
        ("性能指標", "QPS", "> 設計值", "查詢吞吐量"),
        ("性能指標", "P99 延遲", "< 100ms", "用戶體驗"),
        ("性能指標", "插入速率", "> 設計值", "寫入性能"),
        ("業務指標", "搜索召回率", "> 95%", "搜索質量"),
        ("業務指標", "索引構建時間", "合理範圍", "索引效率"),
        ("穩定性", "錯誤率", "< 0.1%", "系統穩定性"),
        ("穩定性", "節點健康", "100%", "高可用性"),
    ]

    table = Table(title="監控指標")
    table.add_column("類別", style="cyan")
    table.add_column("指標", style="yellow")
    table.add_column("閾值", style="green")
    table.add_column("用途", style="magenta")

    for category, metric, threshold, purpose in metrics:
        table.add_row(category, metric, threshold, purpose)

    console.print(table)

    console.print("\n[yellow]Prometheus 監控配置示例:[/yellow]\n")

    prometheus_config = """
# Milvus 暴露的 Prometheus 指標端口: 9091

# 關鍵指標查詢:
# 1. QPS
rate(milvus_proxy_sq_latency_count[1m])

# 2. P99 延遲
histogram_quantile(0.99, rate(milvus_proxy_sq_latency_bucket[1m]))

# 3. 內存使用
milvus_querynode_memory_used_bytes

# 4. 錯誤率
rate(milvus_proxy_sq_fail_count[1m]) / rate(milvus_proxy_sq_latency_count[1m])
"""

    console.print(prometheus_config)


def troubleshooting_guide():
    """故障排查指南"""
    console.print("[bold cyan]4. 常見問題排查[/bold cyan]")

    issues = [
        ("問題", "可能原因", "解決方案"),
        ("搜索慢", "nprobe/ef 設置過高", "降低搜索參數"),
        ("搜索慢", "索引未加載到內存", "檢查集合加載狀態"),
        ("搜索慢", "數據量過大", "使用分區或更高效索引"),
        ("內存不足", "數據集過大", "增加內存或使用 DiskANN"),
        ("內存不足", "向量緩存過多", "調整緩存配置"),
        ("插入失敗", "Schema 不匹配", "檢查數據類型和維度"),
        ("插入慢", "批次太小", "增加批次大小(100-1000)"),
        ("索引構建慢", "參數設置不當", "優化索引參數"),
        ("連接失敗", "網絡問題", "檢查防火牆和網絡配置"),
        ("連接失敗", "服務未啟動", "檢查 Milvus 服務狀態"),
    ]

    table = Table(title="故障排查指南")
    table.add_column("問題", style="cyan", width=12)
    table.add_column("可能原因", style="yellow", width=18)
    table.add_column("解決方案", style="green", width=25)

    for issue, cause, solution in issues:
        table.add_row(issue, cause, solution)

    console.print(table)


def optimization_checklist():
    """優化檢查清單"""
    console.print("\n[bold cyan]5. 性能優化檢查清單[/bold cyan]")

    checklist = [
        ("☐", "數據準備", "向量歸一化(如使用 IP 或 COSINE)"),
        ("☐", "索引選擇", "根據數據規模選擇合適索引"),
        ("☐", "索引參數", "調優 nlist/nprobe 或 M/ef"),
        ("☐", "批量操作", "使用批量插入(batch_size=100-1000)"),
        ("☐", "分區策略", "合理使用分區減小搜索範圍"),
        ("☐", "內存配置", "確保足夠內存加載索引"),
        ("☐", "並發控制", "設置合理的並發查詢數"),
        ("☐", "緩存優化", "配置適當的緩存大小"),
        ("☐", "網絡優化", "使用內網連接,減少延遲"),
        ("☐", "監控告警", "設置性能監控和告警"),
        ("☐", "定期維護", "清理過期數據,優化索引"),
        ("☐", "資源擴展", "根據負載動態擴展節點"),
    ]

    for status, category, item in checklist:
        console.print(f"  {status} [{category}] {item}")


def performance_tips():
    """性能優化技巧"""
    console.print("\n[bold cyan]6. 性能優化技巧[/bold cyan]")

    tips = [
        ("硬件", "使用 SSD 存儲,提升 I/O 性能"),
        ("硬件", "增加內存,允許更多向量緩存"),
        ("硬件", "使用 GPU 加速索引構建(支持的索引)"),
        ("配置", "調整 queryNode 內存池大小"),
        ("配置", "優化 Pulsar 配置提升消息吞吐"),
        ("配置", "使用對象存儲緩存加速讀取"),
        ("應用", "預先計算和緩存嵌入向量"),
        ("應用", "使用連接池管理客戶端連接"),
        ("應用", "實施查詢結果緩存"),
        ("架構", "讀寫分離,使用只讀副本"),
        ("架構", "冷熱數據分離存儲"),
        ("架構", "使用 CDN 加速全球訪問"),
    ]

    table = Table(title="性能優化技巧")
    table.add_column("類別", style="cyan", width=8)
    table.add_column("技巧", style="green", width=50)

    for category, tip in tips:
        table.add_row(category, tip)

    console.print(table)


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Milvus 性能調優示例[/bold cyan]",
        border_style="cyan"
    ))

    # 1. 性能基準測試
    performance_benchmark()

    # 2. 參數優化
    parameter_tuning()

    # 3. 監控指標
    monitoring_metrics()

    # 4. 故障排查
    troubleshooting_guide()

    # 5. 優化檢查清單
    optimization_checklist()

    # 6. 性能技巧
    performance_tips()

    console.print("\n" + "="*60)
    console.print("[bold green]✓ 性能調優示例完成！[/bold green]")
    console.print("\n[cyan]相關資源:[/cyan]")
    console.print("  • 性能調優: https://milvus.io/docs/performance_faq.md")
    console.print("  • 監控指南: https://milvus.io/docs/monitor.md")
    console.print("  • 故障排查: https://milvus.io/docs/troubleshooting.md")

    connections.disconnect("default")


if __name__ == "__main__":
    main()

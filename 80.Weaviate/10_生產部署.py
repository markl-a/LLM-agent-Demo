"""
Weaviate 生產部署示例

本示例展示：
1. 生產環境配置
2. 性能優化技巧
3. 監控和日誌
4. 安全配置
5. 高可用部署
"""

import weaviate
from weaviate.classes.config import Configure, Property, DataType, Reconfigure
from weaviate.classes.init import Auth, AdditionalConfig, Timeout
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
import os
from dotenv import load_dotenv

load_dotenv()

console = Console()


def production_connection_examples():
    """生產環境連接示例"""
    console.print("[bold cyan]1. 生產環境連接配置[/bold cyan]")

    examples = """
# 方式 1: Weaviate Cloud Service (WCS)
```python
client = weaviate.connect_to_wcs(
    cluster_url="https://my-cluster.weaviate.network",
    auth_credentials=Auth.api_key("your-wcs-api-key"),
    headers={
        "X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")
    },
    additional_config=AdditionalConfig(
        timeout=Timeout(init=30, query=60, insert=120)
    )
)
```

# 方式 2: 自托管集群 (帶認證)
```python
client = weaviate.connect_to_custom(
    http_host="weaviate.example.com",
    http_port=443,
    http_secure=True,
    grpc_host="weaviate.example.com",
    grpc_port=50051,
    grpc_secure=True,
    auth_credentials=Auth.api_key("your-api-key"),
    headers={
        "X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")
    },
    additional_config=AdditionalConfig(
        timeout=Timeout(init=30, query=60, insert=120)
    )
)
```

# 方式 3: 使用 OIDC 認證
```python
client = weaviate.connect_to_custom(
    http_host="weaviate.example.com",
    http_port=443,
    http_secure=True,
    grpc_host="weaviate.example.com",
    grpc_port=50051,
    grpc_secure=True,
    auth_credentials=Auth.client_credentials(
        client_secret="your-client-secret",
        scope="openid"
    )
)
```
"""

    console.print(examples)
    console.print()


def performance_optimization_config():
    """性能優化配置"""
    console.print("[bold cyan]2. 性能優化配置[/bold cyan]")

    console.print("[yellow]Schema 性能優化:[/yellow]\n")

    schema_config = """
```python
# HNSW 索引優化
client.collections.create(
    name="OptimizedCollection",
    properties=[
        Property(name="content", data_type=DataType.TEXT)
    ],
    vector_index_config=Configure.VectorIndex.hnsw(
        distance_metric=VectorDistances.COSINE,
        ef=-1,                    # 動態 ef (推薦)
        ef_construction=128,      # 構建時的 ef (越大越精確但越慢)
        max_connections=64,       # 每個節點最大連接數 (32-128)
        dynamic_ef_min=100,       # 動態 ef 最小值
        dynamic_ef_max=500,       # 動態 ef 最大值
        dynamic_ef_factor=8,      # 動態 ef 因子
        vector_cache_max_objects=1000000,  # 向量緩存大小
        flat_search_cutoff=40000, # 小於此數量使用暴力搜索
        skip=False,               # 不跳過索引
    ),
    # 倒排索引優化
    inverted_index_config=Configure.inverted_index(
        bm25_b=0.75,              # BM25 參數 b
        bm25_k1=1.2,              # BM25 參數 k1
        cleanup_interval_seconds=300,  # 清理間隔
        index_null_state=False,   # 不索引 null 值
        index_property_length=False,   # 不索引屬性長度
        index_timestamps=False,   # 不索引時間戳
    )
)
```
"""

    console.print(schema_config)

    table = Table(title="HNSW 參數建議")
    table.add_column("參數", style="cyan")
    table.add_column("小數據(<10萬)", style="green")
    table.add_column("中等數據(10萬-100萬)", style="yellow")
    table.add_column("大數據(>100萬)", style="red")

    table.add_row("ef_construction", "64", "128", "256")
    table.add_row("max_connections", "32", "64", "128")
    table.add_row("ef (query)", "自動", "自動", "自動")

    console.print(table)
    console.print()


def batch_import_optimization():
    """批量導入優化"""
    console.print("[bold cyan]3. 批量導入優化[/bold cyan]")

    import_code = """
```python
# 高性能批量導入配置
from weaviate.classes.config import Reconfigure

# 1. 臨時禁用向量化（如果自帶向量）
collection.config.update(
    vectorizer_config=Reconfigure.VectorIndex.hnsw(skip=True)
)

# 2. 使用動態批處理
with collection.batch.dynamic() as batch:
    for i, item in enumerate(data):
        batch.add_object(
            properties=item["properties"],
            vector=item["vector"]  # 提供預先計算的向量
        )

        # 可選: 顯示進度
        if i % 1000 == 0:
            print(f"已插入 {i} 條數據")

# 3. 重新啟用向量索引
collection.config.update(
    vectorizer_config=Reconfigure.VectorIndex.hnsw(skip=False)
)

# 批處理配置建議
配置批處理參數:
- batch_size: 100-500 (根據對象大小調整)
- num_workers: CPU核心數
- dynamic_batching: True (自動調整批大小)
```
"""

    console.print(import_code)
    console.print()


def monitoring_and_logging():
    """監控和日誌"""
    console.print("[bold cyan]4. 監控和日誌[/bold cyan]")

    console.print("[yellow]Prometheus 監控配置:[/yellow]\n")

    monitoring_config = """
```yaml
# docker-compose.yml
version: '3.4'
services:
  weaviate:
    image: semitechnologies/weaviate:latest
    environment:
      PROMETHEUS_MONITORING_ENABLED: 'true'
      PROMETHEUS_MONITORING_PORT: '2112'
    ports:
      - "8080:8080"
      - "2112:2112"  # Prometheus metrics

  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana-storage:/var/lib/grafana

volumes:
  grafana-storage:
```

# prometheus.yml
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'weaviate'
    static_configs:
      - targets: ['weaviate:2112']
```
"""

    console.print(monitoring_config)

    # 關鍵監控指標
    metrics = [
        ("請求延遲", "weaviate_requests_total", "監控查詢性能"),
        ("向量操作", "weaviate_vector_index_operations_total", "索引操作統計"),
        ("內存使用", "weaviate_memory_used_bytes", "內存使用情況"),
        ("對象數量", "weaviate_object_count", "集合對象總數"),
        ("批處理", "weaviate_batch_operations_total", "批量操作統計"),
        ("錯誤率", "weaviate_errors_total", "錯誤監控"),
    ]

    table = Table(title="關鍵監控指標")
    table.add_column("指標類型", style="cyan")
    table.add_column("Prometheus 指標", style="green")
    table.add_column("說明", style="yellow")

    for metric_type, metric_name, desc in metrics:
        table.add_row(metric_type, metric_name, desc)

    console.print(table)
    console.print()


def security_configuration():
    """安全配置"""
    console.print("[bold cyan]5. 安全配置[/bold cyan]")

    security_config = """
# 1. 啟用認證
```yaml
environment:
  AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED: 'false'
  AUTHENTICATION_APIKEY_ENABLED: 'true'
  AUTHENTICATION_APIKEY_ALLOWED_KEYS: 'your-secure-api-key'
  AUTHENTICATION_APIKEY_USERS: 'admin'
```

# 2. 使用 OIDC
```yaml
environment:
  AUTHENTICATION_OIDC_ENABLED: 'true'
  AUTHENTICATION_OIDC_ISSUER: 'https://your-issuer.com'
  AUTHENTICATION_OIDC_CLIENT_ID: 'your-client-id'
  AUTHENTICATION_OIDC_USERNAME_CLAIM: 'email'
```

# 3. HTTPS/TLS 配置
```yaml
environment:
  # 使用反向代理 (nginx/traefik) 處理 TLS
  # 或配置 Weaviate 直接使用 TLS
```

# 4. 網絡隔離
```yaml
networks:
  weaviate_network:
    driver: bridge
    internal: true  # 內部網絡

services:
  weaviate:
    networks:
      - weaviate_network
```
"""

    console.print(security_config)

    best_practices = [
        ("API 密鑰", "使用強密鑰,定期輪換,不要硬編碼"),
        ("網絡安全", "使用 VPC/防火牆限制訪問"),
        ("加密", "傳輸使用 TLS,靜態數據加密"),
        ("訪問控制", "實施最小權限原則"),
        ("審計日誌", "記錄所有訪問和操作"),
        ("定期更新", "及時更新 Weaviate 版本"),
        ("備份加密", "備份數據加密存儲"),
        ("漏洞掃描", "定期安全掃描和評估"),
    ]

    table = Table(title="安全最佳實踐")
    table.add_column("領域", style="cyan", width=12)
    table.add_column("建議", style="green", width=48)

    for domain, advice in best_practices:
        table.add_row(domain, advice)

    console.print(table)
    console.print()


def high_availability_setup():
    """高可用部署"""
    console.print("[bold cyan]6. 高可用部署[/bold cyan]")

    ha_config = """
# Kubernetes 部署示例
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: weaviate
spec:
  serviceName: weaviate
  replicas: 3  # 3個副本
  selector:
    matchLabels:
      app: weaviate
  template:
    metadata:
      labels:
        app: weaviate
    spec:
      containers:
      - name: weaviate
        image: semitechnologies/weaviate:latest
        env:
        - name: CLUSTER_HOSTNAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        - name: CLUSTER_GOSSIP_BIND_PORT
          value: "7100"
        - name: CLUSTER_DATA_BIND_PORT
          value: "7101"
        ports:
        - containerPort: 8080
          name: http
        - containerPort: 50051
          name: grpc
        - containerPort: 7100
          name: gossip
        - containerPort: 7101
          name: data
        resources:
          requests:
            memory: "8Gi"
            cpu: "2"
          limits:
            memory: "16Gi"
            cpu: "4"
        volumeMounts:
        - name: weaviate-data
          mountPath: /var/lib/weaviate
  volumeClaimTemplates:
  - metadata:
      name: weaviate-data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 100Gi
      storageClassName: fast-ssd
```
"""

    console.print(ha_config)

    # HA 架構圖
    tree = Tree("[bold cyan]高可用架構[/bold cyan]")

    lb = tree.add("[yellow]負載均衡器 (HAProxy/Nginx)[/yellow]")

    cluster = lb.add("[green]Weaviate 集群[/green]")
    cluster.add("[blue]Node 1 (Master)[/blue]")
    cluster.add("[blue]Node 2 (Replica)[/blue]")
    cluster.add("[blue]Node 3 (Replica)[/blue]")

    storage = lb.add("[magenta]存儲層[/magenta]")
    storage.add("持久化卷 (PV)")
    storage.add("備份存儲 (S3/GCS)")

    monitoring = tree.add("[red]監控告警[/red]")
    monitoring.add("Prometheus + Grafana")
    monitoring.add("日誌聚合 (ELK/Loki)")

    console.print(tree)
    console.print()


def resource_sizing_guide():
    """資源規劃指南"""
    console.print("[bold cyan]7. 資源規劃指南[/bold cyan]")

    sizing = [
        ("小型", "< 100萬向量", "8GB RAM, 2 CPU, 50GB SSD"),
        ("中型", "100萬-1000萬向量", "32GB RAM, 8 CPU, 500GB SSD"),
        ("大型", "1000萬-1億向量", "128GB RAM, 16 CPU, 2TB SSD"),
        ("超大型", "> 1億向量", "256GB+ RAM, 32+ CPU, 5TB+ SSD"),
    ]

    table = Table(title="資源規劃指南")
    table.add_column("規模", style="cyan")
    table.add_column("向量數量", style="yellow")
    table.add_column("推薦配置", style="green")

    for scale, vectors, config in sizing:
        table.add_row(scale, vectors, config)

    console.print(table)

    console.print("\n[yellow]計算公式:[/yellow]")
    console.print("  • 內存需求 ≈ 向量數量 × 向量維度 × 4字節 × 1.5倍開銷")
    console.print("  • 例: 100萬個1536維向量 ≈ 100萬 × 1536 × 4 × 1.5 ≈ 9.2GB")
    console.print()


def deployment_checklist():
    """部署檢查清單"""
    console.print("[bold cyan]8. 生產部署檢查清單[/bold cyan]")

    checklist = [
        ("☐", "環境配置", "配置環境變數和密鑰"),
        ("☐", "認證授權", "啟用並測試認證機制"),
        ("☐", "網絡安全", "配置防火牆和網絡隔離"),
        ("☐", "TLS/HTTPS", "啟用加密通信"),
        ("☐", "資源限制", "設置 CPU/內存限制"),
        ("☐", "持久化存儲", "配置持久化卷"),
        ("☐", "備份策略", "設置自動備份"),
        ("☐", "監控告警", "配置 Prometheus 和 Grafana"),
        ("☐", "日誌聚合", "設置日誌收集和分析"),
        ("☐", "高可用", "配置多副本和負載均衡"),
        ("☐", "災難恢復", "測試備份恢復流程"),
        ("☐", "性能測試", "進行壓力測試和性能調優"),
        ("☐", "文檔", "編寫運維文檔和流程"),
        ("☐", "培訓", "團隊培訓和知識傳遞"),
    ]

    table = Table(title="生產部署檢查清單")
    table.add_column("完成", style="yellow", width=8)
    table.add_column("項目", style="cyan", width=12)
    table.add_column("說明", style="green", width=35)

    for status, item, desc in checklist:
        table.add_row(status, item, desc)

    console.print(table)


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Weaviate 生產部署指南[/bold cyan]",
        border_style="cyan"
    ))

    console.print()

    # 1. 生產連接配置
    production_connection_examples()

    # 2. 性能優化
    performance_optimization_config()

    # 3. 批量導入優化
    batch_import_optimization()

    # 4. 監控和日誌
    monitoring_and_logging()

    # 5. 安全配置
    security_configuration()

    # 6. 高可用部署
    high_availability_setup()

    # 7. 資源規劃
    resource_sizing_guide()

    # 8. 部署檢查清單
    deployment_checklist()

    console.print("="*60)
    console.print("[bold green]✓ 生產部署指南完成！[/bold green]")
    console.print("\n[cyan]相關資源:[/cyan]")
    console.print("  • 官方文檔: https://weaviate.io/developers/weaviate")
    console.print("  • Kubernetes 部署: https://weaviate.io/developers/weaviate/installation/kubernetes")
    console.print("  • 性能優化: https://weaviate.io/developers/weaviate/config-refs/schema/vector-index")
    console.print("  • 監控指南: https://weaviate.io/developers/weaviate/configuration/monitoring")


if __name__ == "__main__":
    main()

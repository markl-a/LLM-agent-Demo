"""
Milvus 集群部署示例

本示例展示：
1. 集群架構介紹
2. Kubernetes 部署配置
3. Docker Compose 集群
4. 高可用配置
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

console = Console()


def cluster_architecture():
    """集群架構介紹"""
    console.print("[bold cyan]1. Milvus 集群架構[/bold cyan]")

    # 架構樹狀圖
    tree = Tree("[bold cyan]Milvus 集群架構[/bold cyan]")

    # 訪問層
    access = tree.add("[yellow]訪問層 (Access Layer)[/yellow]")
    access.add("[blue]Proxy 節點 × N[/blue] - 處理客戶端請求")

    # 協調層
    coord = tree.add("[green]協調層 (Coordinator Service)[/green]")
    coord.add("Root Coord - 集群管理")
    coord.add("Data Coord - 數據管理")
    coord.add("Query Coord - 查詢管理")
    coord.add("Index Coord - 索引管理")

    # 工作節點
    workers = tree.add("[magenta]工作節點層 (Worker Nodes)[/magenta]")
    workers.add("Query Node × N - 執行查詢")
    workers.add("Data Node × N - 數據持久化")
    workers.add("Index Node × N - 索引構建")

    # 存儲層
    storage = tree.add("[red]存儲層 (Storage)[/red]")
    storage.add("Meta Storage (etcd) - 元數據")
    storage.add("Object Storage (MinIO/S3) - 向量和日誌")
    storage.add("Message Storage (Pulsar/Kafka) - 消息隊列")

    console.print(tree)
    console.print()


def kubernetes_deployment():
    """Kubernetes 部署配置"""
    console.print("[bold cyan]2. Kubernetes 部署配置[/bold cyan]")

    console.print("[yellow]使用 Helm Chart 部署:[/yellow]\n")

    helm_commands = """
# 添加 Milvus Helm 倉庫
helm repo add milvus https://milvus-io.github.io/milvus-helm/
helm repo update

# 創建命名空間
kubectl create namespace milvus

# 安裝 Milvus 集群
helm install milvus milvus/milvus \\
  --namespace milvus \\
  --set cluster.enabled=true \\
  --set proxy.replicas=2 \\
  --set queryNode.replicas=2 \\
  --set dataNode.replicas=2 \\
  --set indexNode.replicas=1 \\
  --set pulsar.enabled=true \\
  --set minio.mode=distributed

# 查看部署狀態
kubectl get pods -n milvus

# 訪問 Milvus
kubectl port-forward -n milvus svc/milvus 19530:19530
"""

    console.print(helm_commands)

    # 自定義 values.yaml 示例
    console.print("\n[yellow]自定義 values.yaml:[/yellow]\n")

    values_yaml = """
cluster:
  enabled: true

proxy:
  replicas: 3
  resources:
    limits:
      cpu: 2
      memory: 4Gi
    requests:
      cpu: 1
      memory: 2Gi

queryNode:
  replicas: 3
  resources:
    limits:
      cpu: 4
      memory: 16Gi
    requests:
      cpu: 2
      memory: 8Gi

dataNode:
  replicas: 2
  resources:
    limits:
      cpu: 2
      memory: 8Gi

indexNode:
  replicas: 2
  resources:
    limits:
      cpu: 4
      memory: 16Gi

# 使用外部 etcd
etcd:
  enabled: false
  externalEndpoints:
    - etcd-cluster:2379

# 使用 S3
minio:
  enabled: false
  external:
    enabled: true
    endpoint: s3.amazonaws.com
    accessKey: "your-access-key"
    secretKey: "your-secret-key"
    bucketName: "milvus-bucket"
"""

    console.print(values_yaml)


def docker_compose_cluster():
    """Docker Compose 集群配置"""
    console.print("\n[bold cyan]3. Docker Compose 集群配置[/bold cyan]")

    console.print("[yellow]docker-compose-cluster.yml:[/yellow]\n")

    docker_compose = """
version: '3.5'

services:
  # 協調服務
  rootcoord:
    image: milvusdb/milvus:v2.3.3
    command: ["milvus", "run", "rootcoord"]
    environment:
      ETCD_ENDPOINTS: etcd:2379
      MINIO_ADDRESS: minio:9000
      PULSAR_ADDRESS: pulsar://pulsar:6650

  datacoord:
    image: milvusdb/milvus:v2.3.3
    command: ["milvus", "run", "datacoord"]
    environment:
      ETCD_ENDPOINTS: etcd:2379
      MINIO_ADDRESS: minio:9000
      PULSAR_ADDRESS: pulsar://pulsar:6650

  querycoord:
    image: milvusdb/milvus:v2.3.3
    command: ["milvus", "run", "querycoord"]
    environment:
      ETCD_ENDPOINTS: etcd:2379

  indexcoord:
    image: milvusdb/milvus:v2.3.3
    command: ["milvus", "run", "indexcoord"]
    environment:
      ETCD_ENDPOINTS: etcd:2379

  # Proxy (多個實例實現負載均衡)
  proxy1:
    image: milvusdb/milvus:v2.3.3
    command: ["milvus", "run", "proxy"]
    ports:
      - "19530:19530"
    environment:
      ETCD_ENDPOINTS: etcd:2379

  proxy2:
    image: milvusdb/milvus:v2.3.3
    command: ["milvus", "run", "proxy"]
    ports:
      - "19531:19530"
    environment:
      ETCD_ENDPOINTS: etcd:2379

  # 工作節點 (可擴展)
  querynode:
    image: milvusdb/milvus:v2.3.3
    command: ["milvus", "run", "querynode"]
    environment:
      ETCD_ENDPOINTS: etcd:2379
    deploy:
      replicas: 2

  datanode:
    image: milvusdb/milvus:v2.3.3
    command: ["milvus", "run", "datanode"]
    environment:
      ETCD_ENDPOINTS: etcd:2379
      MINIO_ADDRESS: minio:9000
      PULSAR_ADDRESS: pulsar://pulsar:6650
    deploy:
      replicas: 2

  indexnode:
    image: milvusdb/milvus:v2.3.3
    command: ["milvus", "run", "indexnode"]
    environment:
      ETCD_ENDPOINTS: etcd:2379
      MINIO_ADDRESS: minio:9000

  # 存儲服務
  etcd:
    image: quay.io/coreos/etcd:v3.5.5
    environment:
      - ETCD_AUTO_COMPACTION_MODE=revision
      - ETCD_AUTO_COMPACTION_RETENTION=1000

  minio:
    image: minio/minio:RELEASE.2023-03-20T20-16-18Z
    environment:
      MINIO_ACCESS_KEY: minioadmin
      MINIO_SECRET_KEY: minioadmin
    command: minio server /minio_data

  pulsar:
    image: apachepulsar/pulsar:2.8.2
    command: bin/pulsar standalone
"""

    console.print(docker_compose)


def high_availability_config():
    """高可用配置"""
    console.print("\n[bold cyan]4. 高可用配置[/bold cyan]")

    ha_features = [
        ("多副本", "Proxy 和 Worker 節點多副本部署", "✓"),
        ("自動故障轉移", "節點故障時自動切換", "✓"),
        ("負載均衡", "請求分發到多個 Proxy", "✓"),
        ("數據持久化", "數據存儲在對象存儲中", "✓"),
        ("元數據備份", "etcd 集群模式部署", "✓"),
        ("滾動更新", "零停機時間更新", "✓"),
    ]

    table = Table(title="高可用特性")
    table.add_column("特性", style="cyan")
    table.add_column("說明", style="green")
    table.add_column("支持", style="yellow")

    for feature, desc, support in ha_features:
        table.add_row(feature, desc, support)

    console.print(table)

    console.print("\n[yellow]高可用檢查清單:[/yellow]")
    checklist = [
        "☐ Proxy 節點至少 2 個",
        "☐ Query/Data/Index 節點至少 2 個",
        "☐ etcd 集群模式 (3/5 節點)",
        "☐ MinIO 分布式模式或使用雲對象存儲",
        "☐ Pulsar 集群模式",
        "☐ 配置健康檢查和自動重啟",
        "☐ 設置資源限制和請求",
        "☐ 配置持久化卷",
        "☐ 實施備份策略",
        "☐ 監控和告警配置",
    ]

    for item in checklist:
        console.print(f"  {item}")


def deployment_best_practices():
    """部署最佳實踐"""
    console.print("\n[bold cyan]5. 部署最佳實踐[/bold cyan]")

    practices = [
        ("資源規劃", "根據數據規模預估資源需求"),
        ("網絡配置", "使用內網通信,配置服務發現"),
        ("存儲選擇", "生產環境使用雲對象存儲 (S3/GCS/Azure)"),
        ("監控", "部署 Prometheus + Grafana 監控"),
        ("日誌", "集中化日誌收集和分析"),
        ("備份", "定期備份 etcd 和對象存儲"),
        ("安全", "啟用 TLS,配置訪問控制"),
        ("擴展", "預留擴展空間,支持水平擴展"),
    ]

    table = Table(title="部署最佳實踐")
    table.add_column("主題", style="cyan", width=12)
    table.add_column("建議", style="green", width=48)

    for topic, advice in practices:
        table.add_row(topic, advice)

    console.print(table)


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Milvus 集群部署示例[/bold cyan]",
        border_style="cyan"
    ))

    # 1. 集群架構
    cluster_architecture()

    # 2. Kubernetes 部署
    kubernetes_deployment()

    # 3. Docker Compose 集群
    docker_compose_cluster()

    # 4. 高可用配置
    high_availability_config()

    # 5. 最佳實踐
    deployment_best_practices()

    console.print("\n" + "="*60)
    console.print("[bold green]✓ 集群部署示例完成！[/bold green]")
    console.print("\n[cyan]相關資源:[/cyan]")
    console.print("  • 官方文檔: https://milvus.io/docs")
    console.print("  • Helm Chart: https://github.com/milvus-io/milvus-helm")
    console.print("  • K8s 部署: https://milvus.io/docs/install_cluster-milvusoperator.md")


if __name__ == "__main__":
    main()

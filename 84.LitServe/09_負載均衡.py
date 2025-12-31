"""
LitServe 負載均衡示例

本示例展示：
1. 水平擴展配置
2. 負載均衡策略
3. 健康檢查
4. 高可用部署
"""

from litserve import LitAPI, LitServer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import time
import os

console = Console()


class LoadBalancedAPI(LitAPI):
    """支持負載均衡的 API"""

    def setup(self, device):
        """初始化模型"""
        # 獲取實例 ID（用於識別不同的服務實例）
        self.instance_id = os.environ.get("INSTANCE_ID", "instance-1")

        console.print(f"[cyan]正在設置 API (實例: {self.instance_id}, 設備: {device})...[/cyan]")

        # 模擬模型加載
        time.sleep(1)
        self.model = lambda x: x.upper()

        console.print(f"[green]✓ 實例 {self.instance_id} 準備就緒[/green]")

    def decode_request(self, request):
        """解析請求"""
        text = request.get("text", "")
        console.print(f"[yellow][{self.instance_id}] 收到請求: {text[:30]}...[/yellow]")
        return text

    def predict(self, x):
        """執行推理"""
        # 模擬處理時間
        time.sleep(0.1)

        result = self.model(x)
        console.print(f"[magenta][{self.instance_id}] 處理完成[/magenta]")
        return result

    def encode_response(self, output):
        """格式化響應（包含實例 ID）"""
        return {
            "result": output,
            "instance": self.instance_id,
            "timestamp": time.time()
        }


def print_docker_compose():
    """打印 Docker Compose 配置"""
    console.print("\n" + "="*60)
    console.print("[bold cyan]Docker Compose 負載均衡配置:[/bold cyan]")
    console.print("""
# docker-compose.yml
version: '3.8'

services:
  # Nginx 負載均衡器
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - litserve-1
      - litserve-2
      - litserve-3

  # LitServe 實例 1
  litserve-1:
    build: .
    environment:
      - INSTANCE_ID=instance-1
    expose:
      - "8000"
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G

  # LitServe 實例 2
  litserve-2:
    build: .
    environment:
      - INSTANCE_ID=instance-2
    expose:
      - "8000"
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G

  # LitServe 實例 3
  litserve-3:
    build: .
    environment:
      - INSTANCE_ID=instance-3
    expose:
      - "8000"
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
    """)
    console.print("="*60 + "\n")


def print_nginx_config():
    """打印 Nginx 配置"""
    console.print("\n" + "="*60)
    console.print("[bold cyan]Nginx 負載均衡配置:[/bold cyan]")
    console.print("""
# nginx.conf
http {
    # 定義上游服務器組
    upstream litserve_backend {
        # 負載均衡策略: least_conn (最少連接)
        least_conn;

        # 服務器列表（帶健康檢查）
        server litserve-1:8000 max_fails=3 fail_timeout=30s;
        server litserve-2:8000 max_fails=3 fail_timeout=30s;
        server litserve-3:8000 max_fails=3 fail_timeout=30s;

        # 其他策略選項:
        # ip_hash;         # 基於客戶端 IP 的會話粘性
        # least_time;      # 最少響應時間（Nginx Plus）
        # random;          # 隨機選擇
    }

    server {
        listen 80;

        # 健康檢查端點
        location /health {
            access_log off;
            return 200 "healthy\\n";
            add_header Content-Type text/plain;
        }

        # API 端點
        location / {
            proxy_pass http://litserve_backend;

            # 代理設置
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # 超時設置
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;

            # 緩衝設置
            proxy_buffering off;
            proxy_request_buffering off;
        }
    }
}
    """)
    console.print("="*60 + "\n")


def print_kubernetes_deployment():
    """打印 Kubernetes 部署配置"""
    console.print("\n" + "="*60)
    console.print("[bold cyan]Kubernetes 負載均衡配置:[/bold cyan]")
    console.print("""
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: litserve
spec:
  replicas: 3  # 3 個副本
  selector:
    matchLabels:
      app: litserve
  template:
    metadata:
      labels:
        app: litserve
    spec:
      containers:
      - name: litserve
        image: your-registry/litserve:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: litserve
spec:
  type: LoadBalancer
  selector:
    app: litserve
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000

---
# hpa.yaml (水平自動擴展)
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: litserve
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: litserve
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
    """)
    console.print("="*60 + "\n")


def print_load_balancing_strategies():
    """打印負載均衡策略"""
    console.print("\n" + "="*60)
    console.print("[bold cyan]負載均衡策略對比:[/bold cyan]\n")

    table = Table(show_header=True)
    table.add_column("策略", style="cyan")
    table.add_column("說明", style="white")
    table.add_column("適用場景", style="green")

    table.add_row(
        "Round Robin",
        "輪詢分配請求",
        "請求處理時間相近"
    )
    table.add_row(
        "Least Connections",
        "分配給連接數最少的服務器",
        "請求處理時間差異大"
    )
    table.add_row(
        "IP Hash",
        "基於客戶端 IP 的會話粘性",
        "需要會話保持"
    )
    table.add_row(
        "Least Time",
        "分配給響應時間最快的服務器",
        "優化延遲（需 Nginx Plus）"
    )
    table.add_row(
        "Random",
        "隨機選擇服務器",
        "簡單場景"
    )
    table.add_row(
        "Weighted",
        "基於權重分配",
        "服務器性能不同"
    )

    console.print(table)
    console.print("="*60 + "\n")


def print_health_check_example():
    """打印健康檢查示例"""
    console.print("\n" + "="*60)
    console.print("[bold cyan]健康檢查最佳實踐:[/bold cyan]")
    console.print("""
[green]1. 端點實現[/green]
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health_check():
    # 檢查模型是否已加載
    if not model_loaded:
        return {"status": "unhealthy", "reason": "model_not_loaded"}

    # 檢查 GPU 可用性
    if use_gpu and not torch.cuda.is_available():
        return {"status": "unhealthy", "reason": "gpu_unavailable"}

    return {"status": "healthy"}

@app.get("/readiness")
async def readiness_check():
    # 檢查是否準備好接收流量
    return {"ready": True}
```

[green]2. 檢查類型[/green]
• Liveness Probe: 檢查服務是否存活
• Readiness Probe: 檢查服務是否準備好
• Startup Probe: 檢查服務是否啟動完成

[green]3. 檢查內容[/green]
✓ 模型加載狀態
✓ GPU/資源可用性
✓ 依賴服務連接
✓ 磁盤空間
✓ 內存使用

[yellow]配置建議:[/yellow]
• initialDelaySeconds: 根據模型加載時間調整
• periodSeconds: 5-10 秒合適
• failureThreshold: 3 次失敗後標記為不健康
• successThreshold: 1 次成功即恢復
    """)
    console.print("="*60 + "\n")


def print_scaling_tips():
    """打印擴展建議"""
    console.print("\n" + "="*60)
    console.print("[bold cyan]擴展策略建議:[/bold cyan]")
    console.print("""
[green]1. 垂直擴展（Scale Up）[/green]
   優點:
   • 配置簡單
   • 無需負載均衡
   • 適合大模型

   缺點:
   • 有硬件上限
   • 單點故障風險
   • 成本高

   適用場景:
   • 模型太大無法分散
   • 流量可預測
   • 開發/測試環境

[green]2. 水平擴展（Scale Out）[/green]
   優點:
   • 無理論上限
   • 高可用
   • 成本效益好

   缺點:
   • 配置複雜
   • 需要負載均衡
   • 狀態管理複雜

   適用場景:
   • 高流量
   • 需要高可用
   • 生產環境

[green]3. 自動擴展[/green]
   • 基於 CPU 使用率
   • 基於內存使用率
   • 基於請求隊列長度
   • 基於自定義指標（QPS、延遲）

[yellow]擴展指標:[/yellow]
  • CPU 使用率 > 70%: 擴容
  • 請求隊列 > 100: 擴容
  • P95 延遲 > 100ms: 擴容
  • 錯誤率 > 1%: 檢查後擴容
    """)
    console.print("="*60 + "\n")


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]LitServe 負載均衡示例[/bold cyan]\n"
        "[dim]水平擴展和高可用部署[/dim]",
        border_style="cyan"
    ))

    # 創建 API 實例
    api = LoadBalancedAPI()

    # 創建服務器
    server = LitServer(
        api,
        accelerator="auto",
        max_batch_size=4,
        workers_per_device=2,  # 每個設備運行 2 個 worker
        timeout=30
    )

    # 打印各種配置
    print_load_balancing_strategies()
    print_docker_compose()
    print_nginx_config()
    print_kubernetes_deployment()
    print_health_check_example()
    print_scaling_tips()

    # 啟動服務器
    console.print("[bold green]正在啟動負載均衡服務...[/bold green]")
    console.print("[dim]按 Ctrl+C 停止服務器[/dim]\n")

    console.print("[yellow]注意: 本示例展示單實例，生產環境請使用 Docker/K8s 部署多實例[/yellow]\n")

    try:
        server.run(port=8000)
    except KeyboardInterrupt:
        console.print("\n[yellow]服務器已停止[/yellow]")


if __name__ == "__main__":
    main()

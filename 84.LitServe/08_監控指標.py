"""
LitServe 監控指標示例

本示例展示：
1. Prometheus 指標集成
2. 自定義指標收集
3. 性能監控
4. 日誌記錄
"""

from litserve import LitAPI, LitServer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import time
import logging
from typing import Dict

console = Console()

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# 定義 Prometheus 指標
# 1. 計數器: 請求總數
request_count = Counter(
    'litserve_requests_total',
    '總請求數',
    ['method', 'endpoint', 'status']
)

# 2. 直方圖: 請求延遲
request_latency = Histogram(
    'litserve_request_duration_seconds',
    '請求處理時間（秒）',
    ['method', 'endpoint'],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)
)

# 3. 儀表: 當前正在處理的請求
active_requests = Gauge(
    'litserve_active_requests',
    '當前活躍請求數'
)

# 4. 計數器: 錯誤數
error_count = Counter(
    'litserve_errors_total',
    '錯誤總數',
    ['error_type']
)

# 5. 直方圖: 模型推理時間
inference_latency = Histogram(
    'litserve_inference_duration_seconds',
    '模型推理時間（秒）',
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5)
)

# 6. 儀表: 模型加載狀態
model_loaded = Gauge(
    'litserve_model_loaded',
    '模型是否已加載 (1=是, 0=否)'
)


class MonitoredAPI(LitAPI):
    """帶監控指標的 API"""

    def setup(self, device):
        """初始化模型"""
        logger.info(f"正在設置 API (設備: {device})")
        console.print(f"[cyan]正在設置監控 API (設備: {device})...[/cyan]")

        try:
            # 模擬模型加載
            time.sleep(1)
            self.model = lambda x: x.upper()

            # 標記模型已加載
            model_loaded.set(1)

            logger.info("模型加載成功")
            console.print("[green]✓ 模型加載完成[/green]")

        except Exception as e:
            # 標記模型未加載
            model_loaded.set(0)

            logger.error(f"模型加載失敗: {e}")
            error_count.labels(error_type='model_loading').inc()
            raise

        # 統計信息
        self.stats = {
            "total_requests": 0,
            "total_errors": 0,
            "total_inference_time": 0.0
        }

    def decode_request(self, request):
        """解析請求"""
        # 增加活躍請求計數
        active_requests.inc()

        try:
            text = request.get("text", "")

            if not text:
                raise ValueError("text 字段不能為空")

            logger.info(f"收到請求: {text[:50]}...")
            console.print(f"[yellow]收到請求: {text[:50]}...[/yellow]")

            return text

        except Exception as e:
            logger.error(f"請求解析失敗: {e}")
            error_count.labels(error_type='request_parsing').inc()
            active_requests.dec()
            raise

    def predict(self, x):
        """執行推理並記錄指標"""
        start_time = time.time()

        try:
            # 執行推理
            result = self.model(x)

            # 記錄推理時間
            inference_time = time.time() - start_time
            inference_latency.observe(inference_time)

            # 更新統計
            self.stats["total_inference_time"] += inference_time

            logger.info(f"推理完成，耗時: {inference_time*1000:.2f}ms")
            console.print(f"[magenta]推理完成: {inference_time*1000:.2f}ms[/magenta]")

            return result

        except Exception as e:
            logger.error(f"推理失敗: {e}")
            error_count.labels(error_type='inference').inc()
            raise

    def encode_response(self, output):
        """格式化響應並更新指標"""
        try:
            response = {
                "result": output,
                "timestamp": time.time()
            }

            # 增加請求計數
            request_count.labels(
                method='POST',
                endpoint='/predict',
                status='success'
            ).inc()

            # 更新統計
            self.stats["total_requests"] += 1

            logger.info("響應已發送")
            console.print("[green]✓ 響應已發送[/green]")

            # 打印統計信息
            self._print_stats()

            return response

        except Exception as e:
            logger.error(f"響應編碼失敗: {e}")
            error_count.labels(error_type='response_encoding').inc()
            request_count.labels(
                method='POST',
                endpoint='/predict',
                status='error'
            ).inc()
            raise

        finally:
            # 減少活躍請求計數
            active_requests.dec()

    def _print_stats(self):
        """打印統計信息"""
        total = self.stats["total_requests"]
        if total > 0:
            avg_time = self.stats["total_inference_time"] / total
            console.print(
                f"[dim]統計: 總請求={total}, "
                f"平均推理時間={avg_time*1000:.2f}ms[/dim]"
            )


def print_prometheus_setup():
    """打印 Prometheus 設置說明"""
    console.print("\n" + "="*60)
    console.print("[bold cyan]Prometheus 設置說明:[/bold cyan]")

    console.print("\n[yellow]1. 訪問指標端點:[/yellow]")
    console.print("  http://localhost:8000/metrics")

    console.print("\n[yellow]2. Prometheus 配置 (prometheus.yml):[/yellow]")
    console.print("""
scrape_configs:
  - job_name: 'litserve'
    scrape_interval: 5s
    static_configs:
      - targets: ['localhost:8000']
    """)

    console.print("\n[yellow]3. 啟動 Prometheus:[/yellow]")
    console.print("""
# 使用 Docker
docker run -d \\
  --name prometheus \\
  -p 9090:9090 \\
  -v /path/to/prometheus.yml:/etc/prometheus/prometheus.yml \\
  prom/prometheus
    """)

    console.print("\n[yellow]4. 訪問 Prometheus UI:[/yellow]")
    console.print("  http://localhost:9090")

    console.print("="*60 + "\n")


def print_available_metrics():
    """打印可用的指標"""
    console.print("\n" + "="*60)
    console.print("[bold cyan]可用的監控指標:[/bold cyan]\n")

    table = Table(show_header=True)
    table.add_column("指標名稱", style="cyan")
    table.add_column("類型", style="yellow")
    table.add_column("說明", style="white")

    table.add_row(
        "litserve_requests_total",
        "Counter",
        "總請求數（按方法、端點、狀態分組）"
    )
    table.add_row(
        "litserve_request_duration_seconds",
        "Histogram",
        "請求處理時間分布"
    )
    table.add_row(
        "litserve_active_requests",
        "Gauge",
        "當前活躍請求數"
    )
    table.add_row(
        "litserve_errors_total",
        "Counter",
        "錯誤總數（按錯誤類型分組）"
    )
    table.add_row(
        "litserve_inference_duration_seconds",
        "Histogram",
        "模型推理時間分布"
    )
    table.add_row(
        "litserve_model_loaded",
        "Gauge",
        "模型加載狀態"
    )

    console.print(table)
    console.print("="*60 + "\n")


def print_prometheus_queries():
    """打印有用的 Prometheus 查詢"""
    console.print("\n" + "="*60)
    console.print("[bold cyan]有用的 Prometheus 查詢:[/bold cyan]")
    console.print("""
[green]1. 每秒請求數 (QPS):[/green]
rate(litserve_requests_total[1m])

[green]2. 平均請求延遲:[/green]
rate(litserve_request_duration_seconds_sum[5m])
/ rate(litserve_request_duration_seconds_count[5m])

[green]3. P95 延遲:[/green]
histogram_quantile(0.95,
  rate(litserve_request_duration_seconds_bucket[5m]))

[green]4. 錯誤率:[/green]
rate(litserve_errors_total[1m])
/ rate(litserve_requests_total[1m])

[green]5. 當前活躍請求:[/green]
litserve_active_requests

[green]6. 平均推理時間:[/green]
rate(litserve_inference_duration_seconds_sum[5m])
/ rate(litserve_inference_duration_seconds_count[5m])
    """)
    console.print("="*60 + "\n")


def print_grafana_setup():
    """打印 Grafana 設置說明"""
    console.print("\n" + "="*60)
    console.print("[bold cyan]Grafana 可視化設置:[/bold cyan]")
    console.print("""
[yellow]1. 啟動 Grafana:[/yellow]
docker run -d \\
  --name grafana \\
  -p 3000:3000 \\
  grafana/grafana

[yellow]2. 訪問 Grafana:[/yellow]
http://localhost:3000
默認用戶名/密碼: admin/admin

[yellow]3. 添加 Prometheus 數據源:[/yellow]
Configuration > Data Sources > Add Prometheus
URL: http://prometheus:9090

[yellow]4. 導入儀表板:[/yellow]
• 使用預構建的 FastAPI 儀表板
• 或創建自定義儀表板

[green]推薦的可視化圖表:[/green]
• QPS 趨勢圖
• 延遲分布直方圖
• 錯誤率時間序列
• 活躍請求數儀表
• 推理時間熱圖
    """)
    console.print("="*60 + "\n")


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]LitServe 監控指標示例[/bold cyan]\n"
        "[dim]Prometheus + Grafana 集成[/dim]",
        border_style="cyan"
    ))

    # 創建 API 實例
    api = MonitoredAPI()

    # 創建服務器
    server = LitServer(
        api,
        accelerator="auto",
        max_batch_size=1,
        timeout=30
    )

    # 打印可用指標
    print_available_metrics()

    # 打印 Prometheus 設置
    print_prometheus_setup()

    # 打印查詢示例
    print_prometheus_queries()

    # 打印 Grafana 設置
    print_grafana_setup()

    # 啟動服務器
    console.print("[bold green]正在啟動監控服務...[/bold green]")
    console.print("[dim]按 Ctrl+C 停止服務器[/dim]\n")

    logger.info("服務器啟動")

    try:
        server.run(port=8000)
    except KeyboardInterrupt:
        console.print("\n[yellow]服務器已停止[/yellow]")
        logger.info("服務器停止")


if __name__ == "__main__":
    main()

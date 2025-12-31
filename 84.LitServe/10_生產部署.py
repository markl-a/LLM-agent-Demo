"""
LitServe 生產部署示例

本示例展示：
1. 完整的生產環境配置
2. Docker 容器化
3. 環境變量管理
4. 日誌和監控集成
5. 部署最佳實踐
"""

from litserve import LitAPI, LitServer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import torch
import os
import logging
from datetime import datetime

console = Console()

# 生產環境日誌配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'litserve_{datetime.now().strftime("%Y%m%d")}.log')
    ]
)
logger = logging.getLogger(__name__)


class ProductionAPI(LitAPI):
    """生產環境 API 配置"""

    def setup(self, device):
        """初始化（生產配置）"""
        logger.info("="*60)
        logger.info("開始初始化生產環境 API")
        logger.info(f"設備: {device}")
        logger.info(f"環境: {os.getenv('ENVIRONMENT', 'production')}")
        logger.info("="*60)

        console.print(f"[cyan]正在設置生產 API (設備: {device})...[/cyan]")

        try:
            # 1. 加載配置
            self.config = self._load_config()
            logger.info(f"配置加載完成: {self.config}")

            # 2. 初始化模型
            self.model = self._load_model(device)
            logger.info("模型加載成功")

            # 3. 預熱
            self._warmup(device)
            logger.info("預熱完成")

            # 4. 設置監控
            self.metrics = {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0
            }

            console.print("[green]✓ 生產 API 初始化完成[/green]")

        except Exception as e:
            logger.error(f"初始化失敗: {e}", exc_info=True)
            raise

    def _load_config(self):
        """加載配置（從環境變量）"""
        return {
            "model_path": os.getenv("MODEL_PATH", "./models/default"),
            "max_length": int(os.getenv("MAX_LENGTH", "512")),
            "temperature": float(os.getenv("TEMPERATURE", "0.7")),
            "batch_size": int(os.getenv("BATCH_SIZE", "8")),
            "environment": os.getenv("ENVIRONMENT", "production")
        }

    def _load_model(self, device):
        """加載模型"""
        logger.info(f"從 {self.config['model_path']} 加載模型")

        # 實際應用中在這裡加載真實模型
        # model = torch.load(self.config['model_path'])
        # model.to(device)
        # model.eval()

        # 演示用簡單模型
        model = torch.nn.Sequential(
            torch.nn.Linear(100, 50),
            torch.nn.ReLU(),
            torch.nn.Linear(50, 10)
        ).to(device)
        model.eval()

        return model

    def _warmup(self, device):
        """預熱模型"""
        logger.info("開始預熱...")
        dummy_input = torch.randn(1, 100).to(device)

        with torch.no_grad():
            for i in range(3):
                _ = self.model(dummy_input)
                logger.debug(f"預熱迭代 {i+1}/3")

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    def decode_request(self, request):
        """解析請求（帶驗證）"""
        try:
            self.metrics["total_requests"] += 1

            # 驗證必需字段
            if "input" not in request:
                raise ValueError("缺少必需字段: input")

            input_data = request["input"]

            # 驗證數據類型和範圍
            if not isinstance(input_data, list):
                raise ValueError("input 必須是列表")

            if len(input_data) != 100:
                raise ValueError(f"input 長度必須為 100，實際為 {len(input_data)}")

            logger.debug(f"請求解析成功: {len(input_data)} 個元素")

            return torch.tensor(input_data, dtype=torch.float32)

        except Exception as e:
            logger.error(f"請求解析失敗: {e}")
            self.metrics["failed_requests"] += 1
            raise

    def predict(self, x):
        """執行推理（帶錯誤處理）"""
        try:
            # 移到正確的設備
            x = x.to(next(self.model.parameters()).device)

            # 確保是 2D
            if x.dim() == 1:
                x = x.unsqueeze(0)

            # 推理
            with torch.no_grad():
                output = self.model(x)

            logger.debug(f"推理成功，輸出形狀: {output.shape}")

            return output

        except Exception as e:
            logger.error(f"推理失敗: {e}", exc_info=True)
            self.metrics["failed_requests"] += 1
            raise

    def encode_response(self, output):
        """編碼響應"""
        try:
            self.metrics["successful_requests"] += 1

            response = {
                "predictions": output.cpu().numpy().tolist(),
                "model_version": "1.0.0",
                "environment": self.config["environment"]
            }

            logger.debug("響應編碼成功")

            return response

        except Exception as e:
            logger.error(f"響應編碼失敗: {e}")
            raise


def print_dockerfile():
    """打印 Dockerfile"""
    console.print("\n" + "="*60)
    console.print("[bold cyan]Dockerfile (生產環境):[/bold cyan]")
    console.print("""
# Dockerfile
FROM python:3.10-slim

# 設置工作目錄
WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \\
    build-essential \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# 複製依賴文件
COPY requirements.txt .

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用代碼
COPY . .

# 創建非 root 用戶
RUN useradd -m -u 1000 appuser && \\
    chown -R appuser:appuser /app
USER appuser

# 暴露端口
EXPOSE 8000

# 健康檢查
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# 啟動應用
CMD ["python", "10_生產部署.py"]
    """)
    console.print("="*60 + "\n")


def print_env_file():
    """打印環境變量文件"""
    console.print("\n" + "="*60)
    console.print("[bold cyan].env 環境變量配置:[/bold cyan]")
    console.print("""
# .env.production
ENVIRONMENT=production
MODEL_PATH=/app/models/production
MAX_LENGTH=512
TEMPERATURE=0.7
BATCH_SIZE=8

# 服務配置
PORT=8000
HOST=0.0.0.0
WORKERS=4

# 日誌配置
LOG_LEVEL=INFO
LOG_FILE=/var/log/litserve/app.log

# 監控配置
PROMETHEUS_PORT=9090
ENABLE_METRICS=true

# 安全配置
API_KEY_REQUIRED=true
RATE_LIMIT=100

# 資源限制
MAX_MEMORY=8G
MAX_CPU=4
    """)
    console.print("="*60 + "\n")


def print_deployment_checklist():
    """打印部署檢查清單"""
    console.print("\n" + "="*60)
    console.print("[bold cyan]生產部署檢查清單:[/bold cyan]")
    console.print("""
[green]部署前檢查:[/green]
□ 代碼審查完成
□ 單元測試全部通過
□ 集成測試通過
□ 性能測試達標
□ 安全掃描無高危漏洞
□ 文檔更新完成

[green]環境配置:[/green]
□ 環境變量正確配置
□ 密鑰安全存儲
□ SSL 證書有效
□ 防火牆規則配置
□ 負載均衡器配置
□ DNS 記錄更新

[green]監控和日誌:[/green]
□ Prometheus 指標正常
□ Grafana 儀表板配置
□ 日誌收集配置（ELK/Loki）
□ 告警規則設置
□ 錯誤追蹤配置（Sentry）
□ APM 配置（New Relic/DataDog）

[green]高可用:[/green]
□ 多副本部署（至少 3 個）
□ 健康檢查配置
□ 自動重啟策略
□ 數據備份策略
□ 災難恢復計劃
□ 回滾計劃

[green]安全性:[/green]
□ API 密鑰認證
□ 速率限制
□ CORS 配置
□ 輸入驗證
□ SQL 注入防護
□ XSS 防護

[green]性能優化:[/green]
□ 啟用批處理
□ GPU 加速配置
□ 連接池配置
□ 緩存策略
□ CDN 配置
□ 壓縮啟用
    """)
    console.print("="*60 + "\n")


def print_monitoring_setup():
    """打印監控設置"""
    console.print("\n" + "="*60)
    console.print("[bold cyan]完整監控堆棧:[/bold cyan]")
    console.print("""
[green]1. 指標收集 (Prometheus)[/green]
   • QPS、延遲、錯誤率
   • 資源使用（CPU、內存、GPU）
   • 自定義業務指標

[green]2. 可視化 (Grafana)[/green]
   • 實時儀表板
   • 歷史趨勢分析
   • 多維度圖表

[green]3. 日誌聚合 (ELK Stack)[/green]
   • Elasticsearch: 存儲和搜索
   • Logstash: 日誌處理
   • Kibana: 可視化

[green]4. 追蹤 (Jaeger/Zipkin)[/green]
   • 分布式追蹤
   • 請求鏈路分析
   • 性能瓶頸定位

[green]5. 告警 (Alertmanager)[/green]
   • 錯誤率告警
   • 延遲告警
   • 資源告警
   • 多渠道通知（郵件、Slack、PagerDuty）

[yellow]docker-compose.monitoring.yml:[/yellow]
```yaml
version: '3.8'
services:
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
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin

  elasticsearch:
    image: elasticsearch:8.9.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"

  kibana:
    image: kibana:8.9.0
    ports:
      - "5601:5601"
```
    """)
    console.print("="*60 + "\n")


def print_cicd_pipeline():
    """打印 CI/CD 流水線"""
    console.print("\n" + "="*60)
    console.print("[bold cyan]CI/CD 流水線 (GitHub Actions):[/bold cyan]")
    console.print("""
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          pip install -r requirements.txt
          pytest tests/

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker image
        run: |
          docker build -t litserve:${{ github.sha }} .
          docker tag litserve:${{ github.sha }} litserve:latest

      - name: Push to registry
        run: |
          docker push litserve:${{ github.sha }}
          docker push litserve:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Kubernetes
        run: |
          kubectl set image deployment/litserve \\
            litserve=litserve:${{ github.sha }}
          kubectl rollout status deployment/litserve

      - name: Run smoke tests
        run: |
          ./scripts/smoke_test.sh

      - name: Notify team
        if: always()
        run: |
          curl -X POST ${{ secrets.SLACK_WEBHOOK }} \\
            -d '{"text":"Deployment ${{ job.status }}"}'
    """)
    console.print("="*60 + "\n")


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]LitServe 生產部署完整指南[/bold cyan]\n"
        "[dim]Docker + Kubernetes + 監控 + CI/CD[/dim]",
        border_style="cyan"
    ))

    # 創建 API 實例
    api = ProductionAPI()

    # 生產服務器配置
    server = LitServer(
        api,
        accelerator="auto",
        devices="auto",
        max_batch_size=int(os.getenv("BATCH_SIZE", "8")),
        batch_timeout=0.05,
        workers_per_device=2,
        timeout=60
    )

    # 打印所有配置
    print_dockerfile()
    print_env_file()
    print_deployment_checklist()
    print_monitoring_setup()
    print_cicd_pipeline()

    # 啟動服務器
    console.print("[bold green]正在啟動生產服務...[/bold green]")
    console.print("[dim]按 Ctrl+C 停止服務器[/dim]\n")

    logger.info("="*60)
    logger.info("生產服務器啟動")
    logger.info(f"端口: {os.getenv('PORT', '8000')}")
    logger.info(f"環境: {os.getenv('ENVIRONMENT', 'production')}")
    logger.info("="*60)

    try:
        server.run(
            port=int(os.getenv("PORT", "8000")),
            host=os.getenv("HOST", "0.0.0.0")
        )
    except KeyboardInterrupt:
        console.print("\n[yellow]服務器已停止[/yellow]")
        logger.info("服務器正常關閉")
    except Exception as e:
        console.print(f"\n[red]服務器錯誤: {e}[/red]")
        logger.error(f"服務器異常: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()

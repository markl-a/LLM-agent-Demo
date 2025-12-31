"""
Ollama 生產部署示例

本示例展示：
1. 生產環境配置
2. 性能優化策略
3. 監控和日誌
4. 安全性配置
5. 負載均衡和擴展
"""

import os
import psutil
import time
import logging
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.markdown import Markdown
import json

console = Console()


def configure_logging():
    """配置生產環境日誌"""
    try:
        console.print("\n[bold cyan]生產環境日誌配置[/bold cyan]")

        # 日誌配置示例
        log_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "detailed": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                },
                "json": {
                    "format": '{"time":"%(asctime)s", "level":"%(levelname)s", "message":"%(message)s"}'
                }
            },
            "handlers": {
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": "/var/log/ollama/app.log",
                    "maxBytes": 10485760,  # 10MB
                    "backupCount": 5,
                    "formatter": "detailed"
                },
                "error_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": "/var/log/ollama/error.log",
                    "maxBytes": 10485760,
                    "backupCount": 5,
                    "level": "ERROR",
                    "formatter": "detailed"
                },
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "detailed"
                }
            },
            "root": {
                "level": "INFO",
                "handlers": ["file", "error_file", "console"]
            }
        }

        console.print("\n[bold]日誌配置示例:[/bold]")
        console.print(Panel(
            Syntax(json.dumps(log_config, indent=2), "json", theme="monokai"),
            title="[bold yellow]logging_config.json[/bold yellow]",
            border_style="yellow"
        ))

        # Python 日誌使用示例
        logging_example = """import logging
import logging.config
import json

# 載入配置
with open('logging_config.json') as f:
    config = json.load(f)
    logging.config.dictConfig(config)

logger = logging.getLogger(__name__)

# 使用日誌
logger.info("Ollama service started")
logger.error("Model loading failed", exc_info=True)
logger.warning("High memory usage detected")
"""

        console.print("\n[bold]使用示例:[/bold]")
        console.print(Panel(
            Syntax(logging_example, "python", theme="monokai"),
            border_style="blue"
        ))

    except Exception as e:
        console.print(f"[red]日誌配置失敗: {e}[/red]")


def system_monitoring():
    """系統資源監控"""
    try:
        console.print("\n[bold cyan]系統資源監控[/bold cyan]")

        # CPU 使用率
        cpu_percent = psutil.cpu_percent(interval=1)

        # 內存使用
        memory = psutil.virtual_memory()

        # 磁碟使用
        disk = psutil.disk_usage('/')

        # 創建監控表格
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("資源", style="cyan", width=20)
        table.add_column("使用量", style="yellow", width=20)
        table.add_column("總量", style="blue", width=20)
        table.add_column("使用率", style="green", width=15)

        # CPU
        table.add_row(
            "CPU",
            f"{cpu_percent}%",
            f"{psutil.cpu_count()} 核心",
            f"{cpu_percent}%"
        )

        # 內存
        table.add_row(
            "內存",
            f"{memory.used / (1024**3):.2f} GB",
            f"{memory.total / (1024**3):.2f} GB",
            f"{memory.percent}%"
        )

        # 磁碟
        table.add_row(
            "磁碟",
            f"{disk.used / (1024**3):.2f} GB",
            f"{disk.total / (1024**3):.2f} GB",
            f"{disk.percent}%"
        )

        console.print(table)

        # 監控腳本示例
        monitor_script = """import psutil
import time
import logging

logger = logging.getLogger(__name__)

def monitor_resources():
    \"\"\"監控系統資源\"\"\"
    while True:
        # CPU
        cpu = psutil.cpu_percent(interval=1)

        # 內存
        memory = psutil.virtual_memory()

        # GPU (如果有 NVIDIA GPU)
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]
                logger.info(f"GPU: {gpu.memoryUsed}MB / {gpu.memoryTotal}MB ({gpu.memoryUtil*100:.1f}%)")
        except:
            pass

        # 告警
        if cpu > 90:
            logger.warning(f"High CPU usage: {cpu}%")

        if memory.percent > 90:
            logger.warning(f"High memory usage: {memory.percent}%")

        time.sleep(60)  # 每分鐘檢查一次

if __name__ == "__main__":
    monitor_resources()
"""

        console.print("\n[bold]監控腳本示例:[/bold]")
        console.print(Panel(
            Syntax(monitor_script, "python", theme="monokai"),
            border_style="blue"
        ))

    except Exception as e:
        console.print(f"[red]系統監控失敗: {e}[/red]")


def performance_optimization():
    """性能優化配置"""
    try:
        console.print("\n[bold cyan]性能優化配置[/bold cyan]")

        optimizations = [
            {
                "category": "環境變量",
                "items": [
                    ("OLLAMA_NUM_PARALLEL", "4", "並行請求數"),
                    ("OLLAMA_MAX_LOADED_MODELS", "2", "同時載入的模型數"),
                    ("OLLAMA_KEEP_ALIVE", "5m", "模型保持載入時間"),
                    ("OLLAMA_HOST", "0.0.0.0:11434", "監聽地址"),
                ]
            },
            {
                "category": "GPU 優化",
                "items": [
                    ("CUDA_VISIBLE_DEVICES", "0,1", "使用的 GPU"),
                    ("OLLAMA_GPU_OVERHEAD", "0.9", "GPU 內存使用比例"),
                ]
            },
            {
                "category": "模型參數",
                "items": [
                    ("num_ctx", "2048", "上下文窗口大小"),
                    ("num_batch", "512", "批次大小"),
                    ("num_gpu", "99", "使用的 GPU 層數"),
                ]
            }
        ]

        for opt in optimizations:
            console.print(f"\n[bold yellow]{opt['category']}:[/bold yellow]")

            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("參數", style="cyan", width=25)
            table.add_column("推薦值", style="yellow", width=15)
            table.add_column("說明", style="blue", width=35)

            for param, value, desc in opt['items']:
                table.add_row(param, value, desc)

            console.print(table)

        # 環境變量設置示例
        env_example = """# Linux/macOS
export OLLAMA_NUM_PARALLEL=4
export OLLAMA_MAX_LOADED_MODELS=2
export OLLAMA_KEEP_ALIVE=5m
export OLLAMA_HOST=0.0.0.0:11434

# Windows (PowerShell)
$env:OLLAMA_NUM_PARALLEL="4"
$env:OLLAMA_MAX_LOADED_MODELS="2"

# Docker
docker run -d \\
  -e OLLAMA_NUM_PARALLEL=4 \\
  -e OLLAMA_MAX_LOADED_MODELS=2 \\
  -p 11434:11434 \\
  ollama/ollama
"""

        console.print("\n[bold]環境變量設置:[/bold]")
        console.print(Panel(
            Syntax(env_example, "bash", theme="monokai"),
            border_style="blue"
        ))

    except Exception as e:
        console.print(f"[red]性能優化配置失敗: {e}[/red]")


def security_configuration():
    """安全性配置"""
    try:
        console.print("\n[bold cyan]安全性配置[/bold cyan]")

        security_practices = [
            {
                "title": "1. 網絡隔離",
                "desc": "將 Ollama 服務放在內網，不直接暴露到公網",
                "example": """# 只監聽本地
OLLAMA_HOST=127.0.0.1:11434

# 使用反向代理（Nginx）
upstream ollama {
    server 127.0.0.1:11434;
}

server {
    listen 443 ssl;
    server_name ollama.example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://ollama;
        proxy_set_header Host $host;
    }
}"""
            },
            {
                "title": "2. 訪問控制",
                "desc": "使用 API Gateway 或中間件進行身份驗證",
                "example": """# Python 中間件示例
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx

app = FastAPI()
security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != "your-secret-token":
        raise HTTPException(status_code=401, detail="Invalid token")
    return credentials.credentials

@app.post("/api/chat")
async def chat(request: dict, token: str = Depends(verify_token)):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:11434/api/chat",
            json=request
        )
        return response.json()
"""
            },
            {
                "title": "3. 請求限流",
                "desc": "防止濫用和 DDoS 攻擊",
                "example": """# 使用 Redis 實現簡單限流
from redis import Redis
from time import time

redis_client = Redis(host='localhost', port=6379)

def rate_limit(user_id: str, max_requests: int = 10, window: int = 60):
    \"\"\"限流檢查\"\"\"
    key = f"rate_limit:{user_id}"
    current = redis_client.get(key)

    if current and int(current) >= max_requests:
        return False

    pipe = redis_client.pipeline()
    pipe.incr(key)
    pipe.expire(key, window)
    pipe.execute()

    return True
"""
            },
            {
                "title": "4. 輸入驗證",
                "desc": "驗證和清理用戶輸入",
                "example": """def validate_input(text: str, max_length: int = 10000) -> str:
    \"\"\"驗證用戶輸入\"\"\"
    # 長度檢查
    if len(text) > max_length:
        raise ValueError(f"Input too long: {len(text)} > {max_length}")

    # 過濾惡意內容
    forbidden_patterns = [
        r'<script>',
        r'javascript:',
        # 添加其他模式
    ]

    for pattern in forbidden_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            raise ValueError("Forbidden content detected")

    return text.strip()
"""
            }
        ]

        for practice in security_practices:
            console.print(f"\n[bold yellow]{practice['title']}[/bold yellow]")
            console.print(f"[dim]{practice['desc']}[/dim]")
            console.print(Panel(
                Syntax(practice['example'], "python", theme="monokai"),
                border_style="blue"
            ))

    except Exception as e:
        console.print(f"[red]安全配置失敗: {e}[/red]")


def docker_deployment():
    """Docker 部署配置"""
    try:
        console.print("\n[bold cyan]Docker 部署配置[/bold cyan]")

        # Dockerfile
        dockerfile = """FROM ollama/ollama:latest

# 設置環境變量
ENV OLLAMA_NUM_PARALLEL=4
ENV OLLAMA_MAX_LOADED_MODELS=2
ENV OLLAMA_KEEP_ALIVE=5m

# 暴露端口
EXPOSE 11434

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \\
  CMD curl -f http://localhost:11434/api/tags || exit 1

# 啟動命令
CMD ["ollama", "serve"]
"""

        console.print("\n[bold yellow]Dockerfile:[/bold yellow]")
        console.print(Panel(
            Syntax(dockerfile, "dockerfile", theme="monokai"),
            border_style="yellow"
        ))

        # docker-compose.yml
        compose = """version: '3.8'

services:
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - OLLAMA_NUM_PARALLEL=4
      - OLLAMA_MAX_LOADED_MODELS=2
      - OLLAMA_KEEP_ALIVE=5m
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  ollama_data:
"""

        console.print("\n[bold yellow]docker-compose.yml:[/bold yellow]")
        console.print(Panel(
            Syntax(compose, "yaml", theme="monokai"),
            border_style="yellow"
        ))

        # 部署命令
        commands = """# 構建和啟動
docker-compose up -d

# 查看日誌
docker-compose logs -f ollama

# 進入容器
docker exec -it ollama bash

# 在容器中下載模型
docker exec -it ollama ollama pull llama3.2

# 停止和清理
docker-compose down
docker-compose down -v  # 包括數據卷
"""

        console.print("\n[bold yellow]部署命令:[/bold yellow]")
        console.print(Panel(
            Syntax(commands, "bash", theme="monokai"),
            border_style="blue"
        ))

    except Exception as e:
        console.print(f"[red]Docker 部署配置失敗: {e}[/red]")


def kubernetes_deployment():
    """Kubernetes 部署配置"""
    try:
        console.print("\n[bold cyan]Kubernetes 部署配置[/bold cyan]")

        k8s_deployment = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: ollama
  labels:
    app: ollama
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ollama
  template:
    metadata:
      labels:
        app: ollama
    spec:
      containers:
      - name: ollama
        image: ollama/ollama:latest
        ports:
        - containerPort: 11434
        env:
        - name: OLLAMA_NUM_PARALLEL
          value: "4"
        - name: OLLAMA_MAX_LOADED_MODELS
          value: "2"
        resources:
          requests:
            memory: "8Gi"
            cpu: "2"
          limits:
            memory: "16Gi"
            cpu: "4"
            nvidia.com/gpu: "1"
        livenessProbe:
          httpGet:
            path: /api/tags
            port: 11434
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/tags
            port: 11434
          initialDelaySeconds: 5
          periodSeconds: 5
        volumeMounts:
        - name: ollama-data
          mountPath: /root/.ollama
      volumes:
      - name: ollama-data
        persistentVolumeClaim:
          claimName: ollama-pvc

---
apiVersion: v1
kind: Service
metadata:
  name: ollama-service
spec:
  selector:
    app: ollama
  ports:
  - protocol: TCP
    port: 11434
    targetPort: 11434
  type: LoadBalancer

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: ollama-pvc
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 100Gi
"""

        console.print("\n[bold yellow]Kubernetes Deployment:[/bold yellow]")
        console.print(Panel(
            Syntax(k8s_deployment, "yaml", theme="monokai"),
            border_style="yellow"
        ))

        k8s_commands = """# 部署
kubectl apply -f ollama-deployment.yaml

# 查看狀態
kubectl get pods -l app=ollama
kubectl get svc ollama-service

# 查看日誌
kubectl logs -l app=ollama -f

# 擴展
kubectl scale deployment ollama --replicas=3

# 刪除
kubectl delete -f ollama-deployment.yaml
"""

        console.print("\n[bold yellow]部署命令:[/bold yellow]")
        console.print(Panel(
            Syntax(k8s_commands, "bash", theme="monokai"),
            border_style="blue"
        ))

    except Exception as e:
        console.print(f"[red]Kubernetes 部署失敗: {e}[/red]")


def production_checklist():
    """生產環境檢查清單"""
    try:
        console.print("\n[bold cyan]生產環境檢查清單[/bold cyan]")

        checklist = [
            ("配置管理", [
                "環境變量正確設置",
                "日誌級別設置為 INFO 或 WARNING",
                "資源限制已配置",
                "健康檢查已啟用"
            ]),
            ("安全性", [
                "API 身份驗證已啟用",
                "HTTPS/TLS 已配置",
                "輸入驗證已實現",
                "速率限制已設置",
                "敏感信息已加密"
            ]),
            ("監控", [
                "日誌收集已配置（ELK/Loki）",
                "指標監控已啟用（Prometheus）",
                "告警規則已設置",
                "儀表板已創建（Grafana）"
            ]),
            ("性能", [
                "GPU 配置已優化",
                "模型預加載策略",
                "並發請求限制",
                "響應超時設置",
                "緩存策略已實現"
            ]),
            ("高可用", [
                "多副本部署",
                "負載均衡已配置",
                "故障轉移機制",
                "數據持久化",
                "備份策略"
            ]),
            ("測試", [
                "負載測試已完成",
                "壓力測試已通過",
                "故障恢復測試",
                "安全掃描已執行"
            ])
        ]

        for category, items in checklist:
            console.print(f"\n[bold yellow]{category}:[/bold yellow]")

            for item in items:
                console.print(f"  □ {item}")

    except Exception as e:
        console.print(f"[red]檢查清單生成失敗: {e}[/red]")


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Ollama 生產部署示例[/bold cyan]",
        border_style="cyan"
    ))

    console.print("\n[dim]本示例展示生產環境的部署和配置最佳實踐[/dim]")

    # 1. 日誌配置
    console.print("\n[bold]示例 1: 日誌配置[/bold]")
    configure_logging()

    # 2. 系統監控
    console.print("\n[bold]示例 2: 系統監控[/bold]")
    system_monitoring()

    # 3. 性能優化
    console.print("\n[bold]示例 3: 性能優化[/bold]")
    performance_optimization()

    # 4. 安全配置
    console.print("\n[bold]示例 4: 安全配置[/bold]")
    security_configuration()

    # 5. Docker 部署
    console.print("\n[bold]示例 5: Docker 部署[/bold]")
    docker_deployment()

    # 6. Kubernetes 部署
    console.print("\n[bold]示例 6: Kubernetes 部署[/bold]")
    kubernetes_deployment()

    # 7. 檢查清單
    console.print("\n[bold]示例 7: 生產環境檢查清單[/bold]")
    production_checklist()

    # 完成
    console.print("\n" + "="*60)
    console.print("[bold green]✓ 生產部署示例完成！[/bold green]")

    console.print("\n[cyan]關鍵要點:[/cyan]")
    console.print("  1. 完善的日誌和監控是生產環境的基礎")
    console.print("  2. 安全性配置必不可少")
    console.print("  3. 性能優化需要根據實際負載調整")
    console.print("  4. 使用容器化簡化部署")
    console.print("  5. 高可用配置確保服務穩定性")

    console.print("\n[yellow]建議:[/yellow]")
    console.print("  • 從小規模開始，逐步擴展")
    console.print("  • 持續監控和優化")
    console.print("  • 定期備份模型和配置")
    console.print("  • 保持 Ollama 版本更新")


if __name__ == "__main__":
    main()

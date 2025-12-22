"""
MCP 生產環境部署
================

本模組介紹如何將 MCP 服務器部署到生產環境。
學習監控、日誌、擴展、容錯等生產級功能。

學習目標：
- 準備生產環境
- 實現監控和告警
- 配置日誌和追蹤
- 實現高可用和擴展
- 處理災難恢復

作者：Claude (Anthropic)
日期：2025-12-22
"""

import asyncio
import json
import time
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


# ============================================================================
# 第一部分：部署架構
# ============================================================================

class DeploymentArchitecture:
    """部署架構模式"""

    ARCHITECTURES = {
        "本地部署": {
            "描述": "在本地機器運行 MCP 服務器",
            "適用場景": "個人使用、開發測試",
            "優點": ["簡單", "快速啟動", "無網絡依賴"],
            "缺點": ["不可共享", "單點故障", "性能受限"],
            "示例": "python server.py"
        },

        "容器化部署": {
            "描述": "使用 Docker 容器運行",
            "適用場景": "團隊協作、CI/CD",
            "優點": ["環境一致", "易於擴展", "資源隔離"],
            "缺點": ["需要容器知識", "額外開銷"],
            "示例": "docker run -p 3000:3000 mcp-server"
        },

        "Kubernetes 部署": {
            "描述": "在 K8s 集群中運行",
            "適用場景": "企業級、高可用需求",
            "優點": ["自動擴展", "負載均衡", "自愈能力"],
            "缺點": ["複雜度高", "運維成本高"],
            "示例": "kubectl apply -f mcp-deployment.yaml"
        },

        "Serverless 部署": {
            "描述": "使用 AWS Lambda、Google Cloud Functions",
            "適用場景": "按需使用、成本優化",
            "優點": ["按需付費", "自動擴展", "無需管理服務器"],
            "缺點": ["冷啟動延遲", "執行時間限制"],
            "示例": "aws lambda create-function --function-name mcp-server"
        }
    }


# ============================================================================
# 第二部分：Docker 容器化
# ============================================================================

DOCKERFILE_EXAMPLE = '''
# Dockerfile for MCP Server
FROM python:3.11-slim

# 設置工作目錄
WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# 複製依賴文件
COPY requirements.txt .

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用代碼
COPY . .

# 創建非 root 用戶
RUN useradd -m -u 1000 mcpuser && \\
    chown -R mcpuser:mcpuser /app
USER mcpuser

# 健康檢查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD python -c "import sys; sys.exit(0)"

# 運行服務器
CMD ["python", "-u", "server.py"]
'''

DOCKER_COMPOSE_EXAMPLE = '''
# docker-compose.yml
version: '3.8'

services:
  mcp-server:
    build: .
    container_name: mcp-server
    restart: unless-stopped

    # 環境變數
    environment:
      - LOG_LEVEL=INFO
      - MAX_WORKERS=5
      - TIMEOUT=30

    # 卷掛載
    volumes:
      - ./data:/app/data:ro
      - ./logs:/app/logs

    # 資源限制
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M

    # 日誌配置
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # 可選：Prometheus 監控
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
'''


# ============================================================================
# 第三部分：監控和指標
# ============================================================================

@dataclass
class ServerMetrics:
    """服務器指標"""
    request_count: int = 0
    error_count: int = 0
    total_latency: float = 0.0
    active_connections: int = 0
    timestamp: datetime = datetime.now()

    def average_latency(self) -> float:
        """計算平均延遲"""
        if self.request_count == 0:
            return 0.0
        return self.total_latency / self.request_count

    def error_rate(self) -> float:
        """計算錯誤率"""
        if self.request_count == 0:
            return 0.0
        return (self.error_count / self.request_count) * 100


class MetricsCollector:
    """指標收集器"""

    def __init__(self):
        self.metrics = ServerMetrics()
        self.start_time = time.time()

    def record_request(self, latency: float, success: bool = True):
        """記錄請求"""
        self.metrics.request_count += 1
        self.metrics.total_latency += latency

        if not success:
            self.metrics.error_count += 1

    def get_metrics(self) -> Dict[str, Any]:
        """獲取指標數據"""
        uptime = time.time() - self.start_time

        return {
            "uptime_seconds": uptime,
            "requests_total": self.metrics.request_count,
            "errors_total": self.metrics.error_count,
            "error_rate_percent": self.metrics.error_rate(),
            "average_latency_ms": self.metrics.average_latency() * 1000,
            "active_connections": self.metrics.active_connections,
            "timestamp": self.metrics.timestamp.isoformat()
        }

    def export_prometheus_format(self) -> str:
        """導出 Prometheus 格式的指標"""
        metrics = self.get_metrics()

        lines = [
            f"# HELP mcp_requests_total Total number of requests",
            f"# TYPE mcp_requests_total counter",
            f"mcp_requests_total {metrics['requests_total']}",
            "",
            f"# HELP mcp_errors_total Total number of errors",
            f"# TYPE mcp_errors_total counter",
            f"mcp_errors_total {metrics['errors_total']}",
            "",
            f"# HELP mcp_latency_ms Average request latency in milliseconds",
            f"# TYPE mcp_latency_ms gauge",
            f"mcp_latency_ms {metrics['average_latency_ms']}"
        ]

        return "\n".join(lines)


# ============================================================================
# 第四部分：日誌和追蹤
# ============================================================================

class StructuredLogger:
    """結構化日誌記錄器"""

    def __init__(self, service_name: str):
        self.service_name = service_name

    def log(
        self,
        level: str,
        message: str,
        **extra_fields
    ):
        """記錄結構化日誌"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "service": self.service_name,
            "level": level,
            "message": message,
            **extra_fields
        }

        print(json.dumps(log_entry, ensure_ascii=False))

    def info(self, message: str, **extra):
        """記錄 INFO 級別日誌"""
        self.log("INFO", message, **extra)

    def error(self, message: str, **extra):
        """記錄 ERROR 級別日誌"""
        self.log("ERROR", message, **extra)

    def warning(self, message: str, **extra):
        """記錄 WARNING 級別日誌"""
        self.log("WARNING", message, **extra)


class DistributedTracing:
    """分佈式追蹤"""

    def __init__(self):
        self.traces: Dict[str, List[Dict[str, Any]]] = {}

    def start_trace(self, trace_id: str, operation: str) -> str:
        """開始追蹤"""
        span_id = f"span_{len(self.traces.get(trace_id, []))}"

        if trace_id not in self.traces:
            self.traces[trace_id] = []

        span = {
            "span_id": span_id,
            "operation": operation,
            "start_time": time.time(),
            "end_time": None,
            "duration_ms": None,
            "tags": {}
        }

        self.traces[trace_id].append(span)
        return span_id

    def end_trace(
        self,
        trace_id: str,
        span_id: str,
        tags: Optional[Dict[str, Any]] = None
    ):
        """結束追蹤"""
        if trace_id not in self.traces:
            return

        for span in self.traces[trace_id]:
            if span["span_id"] == span_id:
                span["end_time"] = time.time()
                span["duration_ms"] = (span["end_time"] - span["start_time"]) * 1000

                if tags:
                    span["tags"] = tags

                break


# ============================================================================
# 第五部分：高可用配置
# ============================================================================

KUBERNETES_DEPLOYMENT = '''
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-server
  labels:
    app: mcp-server
spec:
  replicas: 3  # 3 個副本
  selector:
    matchLabels:
      app: mcp-server

  template:
    metadata:
      labels:
        app: mcp-server
    spec:
      containers:
      - name: mcp-server
        image: your-registry/mcp-server:latest
        ports:
        - containerPort: 3000

        # 健康檢查
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10

        readinessProbe:
          httpGet:
            path: /ready
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5

        # 資源限制
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"

        # 環境變數
        env:
        - name: LOG_LEVEL
          value: "INFO"
        - name: MAX_WORKERS
          valueFrom:
            configMapKeyRef:
              name: mcp-config
              key: max_workers

---
apiVersion: v1
kind: Service
metadata:
  name: mcp-server
spec:
  selector:
    app: mcp-server
  ports:
  - protocol: TCP
    port: 80
    targetPort: 3000
  type: LoadBalancer

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: mcp-server-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: mcp-server
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
'''


# ============================================================================
# 第六部分：災難恢復
# ============================================================================

class DisasterRecovery:
    """災難恢復策略"""

    STRATEGIES = {
        "備份策略": {
            "配置備份": [
                "定期備份配置文件",
                "使用版本控制（Git）",
                "加密敏感配置"
            ],
            "數據備份": [
                "每日增量備份",
                "每週全量備份",
                "異地備份存儲",
                "定期測試恢復"
            ]
        },

        "故障恢復": {
            "自動重啟": "使用 systemd, supervisor, k8s 等",
            "健康檢查": "定期檢查服務狀態",
            "故障轉移": "主備切換、負載均衡",
            "降級策略": "關鍵功能優先"
        },

        "監控告警": {
            "指標監控": "CPU、內存、請求量、錯誤率",
            "日誌監控": "錯誤日誌、異常模式",
            "告警渠道": "郵件、Slack、PagerDuty",
            "告警升級": "根據嚴重程度分級"
        }
    }


# ============================================================================
# 第七部分：部署檢查清單
# ============================================================================

class DeploymentChecklist:
    """生產部署檢查清單"""

    CHECKLIST = {
        "部署前": [
            "☐ 代碼審查通過",
            "☐ 單元測試 100% 通過",
            "☐ 集成測試通過",
            "☐ 性能測試達標",
            "☐ 安全掃描無高危問題",
            "☐ 文檔更新完成",
            "☐ 變更記錄已記錄",
            "☐ 回滾方案已準備"
        ],

        "部署中": [
            "☐ 使用金絲雀發布或藍綠部署",
            "☐ 監控關鍵指標",
            "☐ 準備回滾命令",
            "☐ 團隊成員待命"
        ],

        "部署後": [
            "☐ 驗證功能正常",
            "☐ 檢查錯誤日誌",
            "☐ 確認監控數據正常",
            "☐ 通知相關人員",
            "☐ 更新運維文檔",
            "☐ 執行冒煙測試"
        ]
    }


# ============================================================================
# 第八部分：生產環境配置示例
# ============================================================================

PRODUCTION_CONFIG_EXAMPLE = '''
"""
生產環境 MCP 服務器配置
"""

import asyncio
import logging
from pathlib import Path
from mcp.server import Server
from mcp.server.stdio import stdio_server


# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/mcp/server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ProductionMCPServer:
    """生產級 MCP 服務器"""

    def __init__(self):
        self.app = Server(
            "production-server",
            version="1.0.0"
        )

        # 指標收集
        self.metrics = MetricsCollector()

        # 配置
        self.config = self.load_config()

        self.setup_tools()

    def load_config(self) -> dict:
        """載入配置"""
        config_path = Path("/etc/mcp/config.json")

        with open(config_path) as f:
            return json.load(f)

    def setup_tools(self):
        """設置工具"""

        @self.app.tool()
        async def example_tool(param: str) -> str:
            """示例工具"""
            start_time = time.time()

            try:
                # 執行業務邏輯
                result = f"處理: {param}"

                # 記錄成功
                latency = time.time() - start_time
                self.metrics.record_request(latency, success=True)

                logger.info(
                    "工具調用成功",
                    extra={
                        "tool": "example_tool",
                        "latency_ms": latency * 1000
                    }
                )

                return result

            except Exception as e:
                # 記錄失敗
                latency = time.time() - start_time
                self.metrics.record_request(latency, success=False)

                logger.error(
                    "工具調用失敗",
                    extra={
                        "tool": "example_tool",
                        "error": str(e)
                    }
                )

                raise

    async def run(self):
        """運行服務器"""
        logger.info("啟動 MCP 服務器", extra={"version": "1.0.0"})

        try:
            async with stdio_server() as (read, write):
                await self.app.run(
                    read,
                    write,
                    self.app.create_initialization_options()
                )
        except Exception as e:
            logger.error("服務器錯誤", extra={"error": str(e)})
            raise


async def main():
    server = ProductionMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
'''


# ============================================================================
# 主程式示例
# ============================================================================

def main():
    """主程式：生產部署指南"""

    print("=" * 70)
    print("MCP 生產環境部署")
    print("=" * 70)

    # 1. 部署架構
    print("\n【部署架構選擇】")
    for arch, details in list(DeploymentArchitecture.ARCHITECTURES.items())[:2]:
        print(f"\n{arch}:")
        print(f"  適用: {details['適用場景']}")
        print(f"  優點: {', '.join(details['優點'][:2])}")

    # 2. 容器化
    print("\n【Docker 容器化】")
    print("Dockerfile 示例：")
    print(DOCKERFILE_EXAMPLE[:300] + "...\n[已截斷]")

    # 3. 監控指標
    print("\n【監控和指標】")
    collector = MetricsCollector()

    # 模擬一些請求
    collector.record_request(0.1, success=True)
    collector.record_request(0.2, success=True)
    collector.record_request(0.3, success=False)

    metrics = collector.get_metrics()
    print(f"總請求: {metrics['requests_total']}")
    print(f"錯誤率: {metrics['error_rate_percent']:.1f}%")
    print(f"平均延遲: {metrics['average_latency_ms']:.1f}ms")

    # 4. 結構化日誌
    print("\n【結構化日誌】")
    logger = StructuredLogger("mcp-server")
    logger.info(
        "工具調用",
        tool="example",
        user_id="user123",
        duration_ms=150
    )

    # 5. 部署檢查清單
    print("\n【部署檢查清單】")
    for phase, items in list(DeploymentChecklist.CHECKLIST.items())[:2]:
        print(f"\n{phase}:")
        for item in items[:3]:
            print(f"  {item}")

    print("\n" + "=" * 70)
    print("恭喜！您已完成 MCP 完整教程")
    print("=" * 70)
    print("\n下一步建議：")
    print("  1. 查看 README.md 獲取更多資源")
    print("  2. 嘗試構建自己的 MCP 服務器")
    print("  3. 加入 MCP 社區討論")
    print("=" * 70)


if __name__ == "__main__":
    main()

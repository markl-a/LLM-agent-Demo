"""
Temporal 生產部署 - 集群部署與最佳實踐

這個示例展示了：
1. 生產環境配置
2. 高可用性部署
3. 監控和指標
4. 錯誤追蹤
5. 性能優化
6. 安全配置
7. 水平擴展
8. 運維最佳實踐
"""

import asyncio
import logging
import os
from dataclasses import dataclass
from datetime import timedelta
from typing import Dict, List, Optional

from temporalio import activity, workflow
from temporalio.client import Client, TLSConfig
from temporalio.common import RetryPolicy
from temporalio.runtime import Runtime, TelemetryConfig, PrometheusConfig
from temporalio.worker import Worker


# ============================================================
# 配置管理
# ============================================================

@dataclass
class TemporalConfig:
    """Temporal 配置"""

    # Server 連接
    server_address: str = "localhost:7233"
    namespace: str = "default"

    # TLS 配置（生產環境必須）
    tls_enabled: bool = False
    tls_cert_path: Optional[str] = None
    tls_key_path: Optional[str] = None
    tls_ca_path: Optional[str] = None

    # Worker 配置
    task_queue: str = "production-queue"
    max_concurrent_activities: int = 100
    max_concurrent_workflow_tasks: int = 100
    max_cached_workflows: int = 1000

    # 重試策略
    default_activity_retry_policy: RetryPolicy = None

    # 監控
    metrics_enabled: bool = True
    metrics_port: int = 9090

    # 日誌
    log_level: str = "INFO"

    def __post_init__(self):
        """初始化默認值"""
        if self.default_activity_retry_policy is None:
            self.default_activity_retry_policy = RetryPolicy(
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=60),
                backoff_coefficient=2.0,
                maximum_attempts=5,
            )


# ============================================================
# 環境配置加載
# ============================================================

def load_config_from_env() -> TemporalConfig:
    """
    從環境變量加載配置

    生產環境最佳實踐：不要硬編碼配置
    """
    return TemporalConfig(
        server_address=os.getenv("TEMPORAL_ADDRESS", "localhost:7233"),
        namespace=os.getenv("TEMPORAL_NAMESPACE", "default"),

        tls_enabled=os.getenv("TEMPORAL_TLS_ENABLED", "false").lower() == "true",
        tls_cert_path=os.getenv("TEMPORAL_TLS_CERT"),
        tls_key_path=os.getenv("TEMPORAL_TLS_KEY"),
        tls_ca_path=os.getenv("TEMPORAL_TLS_CA"),

        task_queue=os.getenv("TEMPORAL_TASK_QUEUE", "production-queue"),
        max_concurrent_activities=int(os.getenv("MAX_CONCURRENT_ACTIVITIES", "100")),
        max_concurrent_workflow_tasks=int(os.getenv("MAX_CONCURRENT_WORKFLOW_TASKS", "100")),

        metrics_enabled=os.getenv("METRICS_ENABLED", "true").lower() == "true",
        metrics_port=int(os.getenv("METRICS_PORT", "9090")),

        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )


# ============================================================
# 日誌配置
# ============================================================

def setup_logging(log_level: str = "INFO"):
    """
    配置日誌

    生產環境建議：
    - 使用結構化日誌
    - 輸出到文件或日誌收集系統
    - 包含上下文信息（工作流 ID、活動 ID 等）
    """
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),  # 控制台輸出
            # logging.FileHandler('temporal_worker.log'),  # 文件輸出
        ]
    )

    # 設置 Temporal SDK 日誌級別
    logging.getLogger('temporalio').setLevel(getattr(logging, log_level))


# ============================================================
# 監控和指標
# ============================================================

class MetricsCollector:
    """
    指標收集器

    生產環境應該集成 Prometheus、DataDog、CloudWatch 等
    """

    def __init__(self):
        self.workflow_started = 0
        self.workflow_completed = 0
        self.workflow_failed = 0
        self.activity_executed = 0
        self.activity_failed = 0

    def record_workflow_started(self):
        """記錄工作流啟動"""
        self.workflow_started += 1
        logging.info(f"Metric: workflow_started={self.workflow_started}")

    def record_workflow_completed(self, duration_ms: float):
        """記錄工作流完成"""
        self.workflow_completed += 1
        logging.info(f"Metric: workflow_completed={self.workflow_completed}, duration_ms={duration_ms}")

    def record_workflow_failed(self, error: str):
        """記錄工作流失敗"""
        self.workflow_failed += 1
        logging.error(f"Metric: workflow_failed={self.workflow_failed}, error={error}")

    def record_activity_executed(self, activity_name: str, duration_ms: float):
        """記錄活動執行"""
        self.activity_executed += 1
        logging.info(f"Metric: activity_executed={activity_name}, duration_ms={duration_ms}")

    def record_activity_failed(self, activity_name: str, error: str):
        """記錄活動失敗"""
        self.activity_failed += 1
        logging.error(f"Metric: activity_failed={activity_name}, error={error}")

    def get_stats(self) -> dict:
        """獲取統計信息"""
        return {
            "workflow_started": self.workflow_started,
            "workflow_completed": self.workflow_completed,
            "workflow_failed": self.workflow_failed,
            "activity_executed": self.activity_executed,
            "activity_failed": self.activity_failed,
        }


# 全局指標收集器
metrics = MetricsCollector()


# ============================================================
# Activity 定義（帶監控和錯誤處理）
# ============================================================

@activity.defn
async def process_order_activity(order_id: str, user_id: str, amount: float) -> dict:
    """
    處理訂單活動

    生產級實現：
    - 詳細日誌
    - 錯誤處理
    - 指標記錄
    - 心跳（如果是長時間運行）
    """
    logger = logging.getLogger(__name__)
    info = activity.info()

    start_time = asyncio.get_event_loop().time()

    logger.info(
        f"Activity started: {info.activity_type}",
        extra={
            "activity_id": info.activity_id,
            "workflow_id": info.workflow_id,
            "attempt": info.attempt,
            "order_id": order_id,
        }
    )

    try:
        # 模擬處理
        await asyncio.sleep(1)

        # 記錄心跳（對於長時間運行的活動）
        activity.heartbeat("Processing order...")

        result = {
            "order_id": order_id,
            "user_id": user_id,
            "amount": amount,
            "status": "completed",
            "attempt": info.attempt,
        }

        # 記錄成功指標
        duration_ms = (asyncio.get_event_loop().time() - start_time) * 1000
        metrics.record_activity_executed(info.activity_type, duration_ms)

        logger.info(f"Activity completed: {info.activity_type}", extra=result)

        return result

    except Exception as e:
        # 記錄失敗指標
        metrics.record_activity_failed(info.activity_type, str(e))

        logger.error(
            f"Activity failed: {info.activity_type}",
            extra={
                "error": str(e),
                "order_id": order_id,
            },
            exc_info=True
        )

        raise


@activity.defn
async def send_notification_activity(
    user_id: str,
    message: str,
    channel: str = "email"
) -> bool:
    """發送通知活動"""
    logger = logging.getLogger(__name__)

    logger.info(
        f"Sending notification",
        extra={
            "user_id": user_id,
            "channel": channel,
            "message": message,
        }
    )

    await asyncio.sleep(0.5)
    return True


@activity.defn
async def database_operation_activity(operation: str, data: dict) -> dict:
    """
    數據庫操作活動

    生產環境注意事項：
    - 使用連接池
    - 設置超時
    - 處理臨時故障（重試）
    - 記錄慢查詢
    """
    logger = logging.getLogger(__name__)

    logger.info(f"Database operation: {operation}", extra=data)

    # 模擬數據庫操作
    await asyncio.sleep(0.3)

    return {
        "operation": operation,
        "success": True,
        "affected_rows": 1,
    }


# ============================================================
# 工作流定義（生產級）
# ============================================================

@workflow.defn
class ProductionOrderWorkflow:
    """
    生產環境訂單處理工作流

    特點：
    - 完整的錯誤處理
    - 詳細的日誌記錄
    - 指標收集
    - 可觀測性
    """

    def __init__(self):
        self.logger = workflow.logger

    @workflow.run
    async def run(self, order_id: str, user_id: str, amount: float) -> dict:
        """執行訂單處理"""

        self.logger.info(
            f"Workflow started",
            extra={
                "workflow_id": workflow.info().workflow_id,
                "order_id": order_id,
            }
        )

        # 記錄工作流啟動
        metrics.record_workflow_started()

        try:
            # 步驟 1: 處理訂單
            order_result = await workflow.execute_activity(
                process_order_activity,
                order_id,
                user_id,
                amount,
                start_to_close_timeout=timedelta(minutes=5),
                heartbeat_timeout=timedelta(seconds=30),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=1),
                    maximum_interval=timedelta(seconds=60),
                    backoff_coefficient=2.0,
                    maximum_attempts=3,
                ),
            )

            # 步驟 2: 發送通知
            await workflow.execute_activity(
                send_notification_activity,
                user_id,
                f"訂單 {order_id} 處理完成",
                "email",
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=RetryPolicy(maximum_attempts=3),
            )

            # 步驟 3: 記錄到數據庫
            await workflow.execute_activity(
                database_operation_activity,
                "insert",
                {"table": "orders", "order_id": order_id},
                start_to_close_timeout=timedelta(seconds=30),
            )

            result = {
                "status": "success",
                "order_id": order_id,
                "order_result": order_result,
            }

            self.logger.info("Workflow completed", extra=result)

            # 記錄工作流完成
            # metrics.record_workflow_completed(duration_ms)  # 實際環境需要計算

            return result

        except Exception as e:
            # 記錄工作流失敗
            metrics.record_workflow_failed(str(e))

            self.logger.error(
                "Workflow failed",
                extra={"order_id": order_id, "error": str(e)},
                exc_info=True
            )

            raise

    @workflow.query
    def get_status(self) -> dict:
        """查詢工作流狀態"""
        return {
            "workflow_id": workflow.info().workflow_id,
            "workflow_type": workflow.info().workflow_type,
        }


# ============================================================
# Worker 工廠（生產級）
# ============================================================

async def create_production_worker(config: TemporalConfig) -> Worker:
    """
    創建生產級 Worker

    配置：
    - TLS 連接
    - 並發限制
    - 指標導出
    - 優雅關閉
    """

    # 配置 TLS（生產環境必須）
    tls_config = None
    if config.tls_enabled:
        if not all([config.tls_cert_path, config.tls_key_path]):
            raise ValueError("TLS enabled but cert/key paths not provided")

        with open(config.tls_cert_path, "rb") as f:
            client_cert = f.read()

        with open(config.tls_key_path, "rb") as f:
            client_key = f.read()

        tls_config = TLSConfig(
            client_cert=client_cert,
            client_private_key=client_key,
        )

    # 配置遙測（Prometheus 指標）
    runtime = None
    if config.metrics_enabled:
        telemetry_config = TelemetryConfig(
            metrics=PrometheusConfig(bind_address=f"0.0.0.0:{config.metrics_port}")
        )
        runtime = Runtime(telemetry=telemetry_config)

    # 連接到 Temporal Server
    client = await Client.connect(
        config.server_address,
        namespace=config.namespace,
        tls=tls_config,
        runtime=runtime,
    )

    # 創建 Worker
    worker = Worker(
        client,
        task_queue=config.task_queue,
        workflows=[ProductionOrderWorkflow],
        activities=[
            process_order_activity,
            send_notification_activity,
            database_operation_activity,
        ],
        max_concurrent_activities=config.max_concurrent_activities,
        max_concurrent_workflow_tasks=config.max_concurrent_workflow_tasks,
        max_cached_workflows=config.max_cached_workflows,
    )

    return worker


# ============================================================
# 健康檢查
# ============================================================

async def health_check(client: Client) -> bool:
    """
    健康檢查

    用於 Kubernetes liveness/readiness probe
    """
    try:
        # 檢查連接
        await client.list_workflows("WorkflowId = 'health-check'")
        return True
    except Exception as e:
        logging.error(f"Health check failed: {e}")
        return False


# ============================================================
# 主程序（生產級）
# ============================================================

async def run_production_worker():
    """
    運行生產級 Worker

    特點：
    - 配置管理
    - 日誌記錄
    - 指標導出
    - 優雅關閉
    - 健康檢查
    """

    # 加載配置
    config = load_config_from_env()

    # 設置日誌
    setup_logging(config.log_level)

    logger = logging.getLogger(__name__)

    logger.info("=" * 60)
    logger.info("🚀 Temporal Production Worker Starting...")
    logger.info("=" * 60)
    logger.info(f"Server: {config.server_address}")
    logger.info(f"Namespace: {config.namespace}")
    logger.info(f"Task Queue: {config.task_queue}")
    logger.info(f"TLS Enabled: {config.tls_enabled}")
    logger.info(f"Metrics Enabled: {config.metrics_enabled}")
    if config.metrics_enabled:
        logger.info(f"Metrics Port: {config.metrics_port}")
    logger.info(f"Max Concurrent Activities: {config.max_concurrent_activities}")
    logger.info(f"Max Concurrent Workflow Tasks: {config.max_concurrent_workflow_tasks}")
    logger.info("=" * 60)

    try:
        # 創建 Worker
        worker = await create_production_worker(config)

        logger.info("✓ Worker created successfully")
        logger.info("✓ Ready to process workflows and activities")

        if config.metrics_enabled:
            logger.info(f"✓ Prometheus metrics available at http://0.0.0.0:{config.metrics_port}/metrics")

        logger.info("\nPress Ctrl+C to shutdown gracefully...\n")

        # 運行 Worker
        await worker.run()

    except KeyboardInterrupt:
        logger.info("\n⚠️  Shutdown signal received")
        logger.info("🛑 Shutting down gracefully...")
        # Worker 會自動優雅關閉
        logger.info("✓ Worker stopped")

    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        raise

    finally:
        # 輸出最終統計
        logger.info("\n📊 Final Statistics:")
        stats = metrics.get_stats()
        for key, value in stats.items():
            logger.info(f"  {key}: {value}")


async def run_production_client():
    """運行生產客戶端示例"""

    config = load_config_from_env()
    setup_logging(config.log_level)

    logger = logging.getLogger(__name__)

    logger.info("\n" + "=" * 60)
    logger.info("📋 Production Client Example")
    logger.info("=" * 60)

    # 配置 TLS
    tls_config = None
    if config.tls_enabled:
        logger.info("Using TLS connection")
        # TLS 配置（簡化示例）

    # 連接到 Temporal
    client = await Client.connect(
        config.server_address,
        namespace=config.namespace,
        tls=tls_config,
    )

    logger.info(f"Connected to {config.server_address}")

    # 執行工作流
    logger.info("\n執行訂單處理工作流...")

    result = await client.execute_workflow(
        ProductionOrderWorkflow.run,
        "ORDER-PROD-001",
        "user123",
        299.99,
        id="prod-order-001",
        task_queue=config.task_queue,
    )

    logger.info(f"\n✓ Workflow completed: {result}")

    # 顯示指標
    logger.info("\n📊 Metrics:")
    stats = metrics.get_stats()
    for key, value in stats.items():
        logger.info(f"  {key}: {value}")

    logger.info("\n" + "=" * 60)


async def main():
    """主函數"""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "client":
        await run_production_client()
    else:
        await run_production_worker()


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║           Temporal 生產環境部署最佳實踐                        ║
╚══════════════════════════════════════════════════════════════╝

生產環境清單：
------------

✓ 安全性
  - 啟用 TLS 加密
  - 使用命名空間隔離
  - 實施訪問控制
  - 安全存儲憑證

✓ 高可用性
  - 部署多個 Worker 實例
  - 使用負載均衡
  - 配置健康檢查
  - 實施自動重啟

✓ 可觀測性
  - 結構化日誌記錄
  - Prometheus 指標導出
  - 分佈式追蹤
  - 告警配置

✓ 性能優化
  - 調整並發限制
  - 配置連接池
  - 優化活動超時
  - 使用 Continue-As-New

✓ 錯誤處理
  - 配置重試策略
  - 實施死信隊列
  - 錯誤通知機制
  - 故障恢復流程

配置示例：
---------
export TEMPORAL_ADDRESS="temporal.example.com:7233"
export TEMPORAL_NAMESPACE="production"
export TEMPORAL_TLS_ENABLED="true"
export TEMPORAL_TLS_CERT="/path/to/cert.pem"
export TEMPORAL_TLS_KEY="/path/to/key.pem"
export MAX_CONCURRENT_ACTIVITIES="200"
export METRICS_ENABLED="true"
export METRICS_PORT="9090"
export LOG_LEVEL="INFO"

Kubernetes 部署：
----------------
- 使用 Deployment 部署 Worker
- 配置 HPA（水平自動擴展）
- 設置資源限制（CPU、內存）
- 配置健康檢查探針
- 使用 ConfigMap/Secret 管理配置

監控指標：
---------
- workflow_started_total
- workflow_completed_total
- workflow_failed_total
- activity_execution_latency
- worker_task_slots_available

使用方法：
---------
1. 啟動 Worker: python 10_生產部署.py
2. 執行示例: python 10_生產部署.py client

Docker 部署：
-----------
docker run -d \\
  --name temporal-worker \\
  -e TEMPORAL_ADDRESS=temporal:7233 \\
  -e TEMPORAL_NAMESPACE=production \\
  -e MAX_CONCURRENT_ACTIVITIES=200 \\
  your-worker-image:latest
    """)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Worker shutdown complete")

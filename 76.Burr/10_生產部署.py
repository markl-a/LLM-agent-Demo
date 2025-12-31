"""
Burr 生產部署 - 部署到生產環境

這個示例展示如何：
1. 配置生產環境
2. 錯誤處理和恢復
3. 日誌和監控
4. 性能調優

將 Burr 應用部署到生產環境的最佳實踐。
"""

from burr.core import action, State, ApplicationBuilder, expr
from burr.core.persistence import SQLLitePersister
from burr.tracking import LocalTrackingClient
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import logging
import os
from typing import Optional
from datetime import datetime
import structlog

console = Console()


# ============================================================================
# 示例 1：生產環境配置
# ============================================================================

def production_config_example():
    """示例 1：生產環境配置"""
    console.print(Panel("[bold cyan]示例 1：生產環境配置[/bold cyan]"))

    console.print("""
[yellow]生產環境配置清單：[/yellow]

1. [cyan]環境變量[/cyan]
   ```env
   # 應用配置
   BURR_ENV=production
   BURR_APP_ID=my-app
   BURR_VERSION=1.0.0

   # 持久化配置
   BURR_DB_PATH=/var/lib/burr/state.db
   BURR_CHECKPOINT_INTERVAL=100

   # 追蹤配置
   BURR_TRACKING_ENABLED=true
   BURR_TRACKING_PROJECT=prod-project

   # 性能配置
   BURR_BATCH_SIZE=50
   BURR_MAX_ITERATIONS=1000
   BURR_TIMEOUT=300

   # 日誌配置
   LOG_LEVEL=INFO
   LOG_FILE=/var/log/burr/app.log
   ```

2. [cyan]配置類[/cyan]
    """)

    config_code = '''
from pydantic import BaseSettings

class BurrConfig(BaseSettings):
    """Burr 應用配置"""

    # 環境
    env: str = "development"
    app_id: str = "burr-app"
    version: str = "1.0.0"

    # 持久化
    db_path: str = "/tmp/burr.db"
    checkpoint_interval: int = 100

    # 追蹤
    tracking_enabled: bool = True
    tracking_project: str = "default"

    # 性能
    batch_size: int = 10
    max_iterations: int = 100
    timeout: int = 60

    # 日誌
    log_level: str = "INFO"
    log_file: Optional[str] = None

    class Config:
        env_file = ".env"

config = BurrConfig()
    '''

    console.print(Panel(config_code, border_style="blue", title="配置類"))


# ============================================================================
# 示例 2：錯誤處理
# ============================================================================

@action(reads=["data"], writes=["result", "error"])
def safe_process(state: State) -> State:
    """安全處理（帶錯誤處理）"""
    data = state.get("data")

    try:
        # 模擬可能失敗的操作
        if data is None:
            raise ValueError("數據不能為空")

        # 處理數據
        result = f"處理結果: {data}"
        return state.update(result=result, error=None)

    except Exception as e:
        # 記錄錯誤
        error_info = {
            "type": type(e).__name__,
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }

        return state.update(result=None, error=error_info)


@action(reads=["error"], writes=["retry_count"])
def handle_error(state: State) -> State:
    """處理錯誤"""
    error = state.get("error")
    retry_count = state.get("retry_count", 0)

    # 錯誤處理邏輯
    if retry_count < 3:
        # 重試
        return state.update(retry_count=retry_count + 1)
    else:
        # 達到最大重試次數，記錄並繼續
        return state.update(retry_count=retry_count)


def error_handling_example():
    """示例 2：錯誤處理"""
    console.print(Panel("[bold cyan]示例 2：錯誤處理[/bold cyan]"))

    console.print("""
[yellow]錯誤處理策略：[/yellow]

1. [cyan]Try-Catch 包裝[/cyan]
   - 在動作內部捕獲異常
   - 將錯誤信息保存到狀態
   - 不讓異常傳播導致崩潰

2. [cyan]重試機制[/cyan]
   - 自動重試失敗的操作
   - 設置最大重試次數
   - 使用指數退避

3. [cyan]降級處理[/cyan]
   - 提供降級方案
   - 部分功能失敗時繼續運行
   - 記錄降級事件

4. [cyan]錯誤上報[/cyan]
   - 記錄詳細錯誤信息
   - 發送告警通知
   - 集成錯誤追蹤服務

[yellow]示例代碼：[/yellow]
    """)

    error_handling_code = '''
@action(reads=["data"], writes=["result", "error"])
def robust_action(state: State) -> State:
    """健壯的動作"""
    try:
        # 業務邏輯
        result = process_data(state["data"])
        return state.update(result=result, error=None)

    except ValueError as e:
        # 預期錯誤，可以處理
        logger.warning(f"值錯誤: {e}")
        return state.update(
            result=None,
            error={"type": "ValueError", "message": str(e)}
        )

    except Exception as e:
        # 未預期錯誤，記錄並上報
        logger.error(f"未預期錯誤: {e}", exc_info=True)
        send_alert(f"錯誤: {e}")
        return state.update(
            result=None,
            error={"type": "UnexpectedError", "message": str(e)}
        )
    '''

    console.print(Panel(error_handling_code, border_style="blue"))


# ============================================================================
# 示例 3：日誌和監控
# ============================================================================

def logging_monitoring_example():
    """示例 3：日誌和監控"""
    console.print(Panel("[bold cyan]示例 3：日誌和監控[/bold cyan]"))

    console.print("""
[yellow]日誌配置：[/yellow]

1. [cyan]結構化日誌[/cyan]
   - 使用 structlog
   - JSON 格式輸出
   - 便於解析和查詢

2. [cyan]日誌級別[/cyan]
   - DEBUG: 調試信息
   - INFO: 一般信息
   - WARNING: 警告
   - ERROR: 錯誤
   - CRITICAL: 嚴重錯誤

3. [cyan]日誌內容[/cyan]
   - 時間戳
   - 日誌級別
   - 應用 ID
   - 動作名稱
   - 狀態快照
   - 錯誤追蹤

[yellow]日誌配置示例：[/yellow]
    """)

    logging_code = '''
import structlog

# 配置結構化日誌
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# 在動作中使用
@action(reads=["data"], writes=["result"])
def logged_action(state: State) -> State:
    logger.info("action_start", action="logged_action", data=state["data"])

    try:
        result = process(state["data"])
        logger.info("action_complete", action="logged_action", result=result)
        return state.update(result=result)

    except Exception as e:
        logger.error("action_failed", action="logged_action", error=str(e))
        raise
    '''

    console.print(Panel(logging_code, border_style="blue"))

    console.print("\n[yellow]監控指標：[/yellow]")

    metrics_table = Table(title="關鍵監控指標")
    metrics_table.add_column("指標", style="cyan")
    metrics_table.add_column("說明", style="yellow")
    metrics_table.add_column("告警閾值", style="red")

    metrics_table.add_row(
        "錯誤率",
        "失敗請求 / 總請求",
        "> 5%"
    )
    metrics_table.add_row(
        "平均響應時間",
        "處理時間平均值",
        "> 1000ms"
    )
    metrics_table.add_row(
        "P99 延遲",
        "99% 請求的響應時間",
        "> 2000ms"
    )
    metrics_table.add_row(
        "吞吐量",
        "每秒處理請求數",
        "< 10 req/s"
    )
    metrics_table.add_row(
        "狀態大小",
        "狀態對象大小",
        "> 10MB"
    )

    console.print(metrics_table)


# ============================================================================
# 示例 4：部署清單
# ============================================================================

def deployment_checklist():
    """示例 4：部署清單"""
    console.print(Panel("[bold cyan]示例 4：部署清單[/bold cyan]"))

    console.print("""
[yellow]生產部署清單：[/yellow]

[bold cyan]1. 代碼準備[/bold cyan]
   ✓ 代碼審查通過
   ✓ 所有測試通過
   ✓ 性能測試達標
   ✓ 安全掃描通過

[bold cyan]2. 環境配置[/bold cyan]
   ✓ 生產環境變量設置
   ✓ 數據庫配置
   ✓ 日誌配置
   ✓ 監控配置

[bold cyan]3. 依賴管理[/bold cyan]
   ✓ 鎖定依賴版本
   ✓ 安全漏洞檢查
   ✓ 依賴大小優化

[bold cyan]4. 持久化[/bold cyan]
   ✓ 數據庫備份策略
   ✓ 狀態恢復測試
   ✓ 數據遷移計劃

[bold cyan]5. 監控和告警[/bold cyan]
   ✓ 日誌聚合設置
   ✓ 監控面板配置
   ✓ 告警規則設置
   ✓ On-call 輪值安排

[bold cyan]6. 容災[/bold cyan]
   ✓ 備份恢復流程
   ✓ 故障切換機制
   ✓ 降級預案
   ✓ 應急響應流程

[bold cyan]7. 文檔[/bold cyan]
   ✓ 部署文檔
   ✓ 運維手冊
   ✓ 故障排查指南
   ✓ API 文檔

[yellow]Docker 部署示例：[/yellow]
    """)

    dockerfile = '''
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安裝依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製代碼
COPY . .

# 創建必要目錄
RUN mkdir -p /var/lib/burr /var/log/burr

# 運行應用
CMD ["python", "app.py"]
    '''

    console.print(Panel(dockerfile, border_style="blue", title="Dockerfile"))

    console.print("\n[yellow]Kubernetes 部署示例：[/yellow]")

    k8s_deployment = '''
apiVersion: apps/v1
kind: Deployment
metadata:
  name: burr-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: burr-app
  template:
    metadata:
      labels:
        app: burr-app
    spec:
      containers:
      - name: burr-app
        image: burr-app:1.0.0
        env:
        - name: BURR_ENV
          value: "production"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        volumeMounts:
        - name: burr-data
          mountPath: /var/lib/burr
      volumes:
      - name: burr-data
        persistentVolumeClaim:
          claimName: burr-pvc
    '''

    console.print(Panel(k8s_deployment, border_style="blue", title="Kubernetes"))


# ============================================================================
# 主函數
# ============================================================================

def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold green]Burr 生產部署 - 部署到生產環境[/bold green]",
        border_style="green"
    ))

    console.print("\n[bold]生產部署核心概念：[/bold]")
    console.print("1. [cyan]環境配置[/cyan]: 生產環境設置")
    console.print("2. [cyan]錯誤處理[/cyan]: 健壯的錯誤處理")
    console.print("3. [cyan]日誌監控[/cyan]: 完善的可觀測性")
    console.print("4. [cyan]部署策略[/cyan]: 安全的部署流程\n")

    # 運行示例
    production_config_example()
    console.print("\n" + "="*60 + "\n")

    error_handling_example()
    console.print("\n" + "="*60 + "\n")

    logging_monitoring_example()
    console.print("\n" + "="*60 + "\n")

    deployment_checklist()

    # 總結
    console.print(Panel("""
[bold green]生產部署完成！[/bold green]

關鍵要點：
1. 完善的環境配置管理
2. 健壯的錯誤處理機制
3. 全面的日誌和監控
4. 詳細的部署清單
5. 容災和備份策略

部署最佳實踐：
- 使用環境變量管理配置
- 實現完善的錯誤處理
- 設置結構化日誌
- 配置監控和告警
- 準備故障預案

運維建議：
- 定期備份狀態數據
- 監控關鍵性能指標
- 定期安全更新
- 保持文檔更新
- 定期進行容災演練

生產環境注意事項：
- 測試所有降級方案
- 設置合理的超時
- 限制資源使用
- 實施訪問控制
- 定期審計日誌

恭喜完成 Burr 框架學習！

你已經學習了：
1. 基本概念和快速開始
2. 狀態管理和動作鏈
3. 條件分支和持久化
4. 追蹤調試和可視化
5. 聊天應用和 Agent 循環
6. 並行執行和性能優化
7. 生產部署和最佳實踐

下一步建議：
- 構建自己的 Burr 應用
- 探索 Burr UI 的高級功能
- 閱讀官方文檔和示例
- 參與社區討論
- 分享你的經驗

訪問：https://burr.dagworks.io/
    """, title="總結", border_style="green"))


if __name__ == "__main__":
    main()

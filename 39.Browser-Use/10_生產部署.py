"""
Browser-Use 生產部署範例

這個範例展示了如何將 Browser-Use 應用部署到生產環境。
包括配置管理、日誌記錄、錯誤處理、監控、擴展性等。

主要功能：
1. 生產環境配置
2. 日誌系統設置
3. 錯誤處理和告警
4. 性能監控
5. 資源管理
6. 安全性加固
7. 部署策略
8. 高可用性設計
"""

import asyncio
import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import traceback
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

try:
    from browser_use import Agent, BrowserConfig
except ImportError:
    print("請先安裝 browser-use: pip install browser-use")
    exit(1)


# ============================================================================
# 配置管理
# ============================================================================

class Environment(Enum):
    """環境類型"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class ProductionConfig:
    """生產環境配置"""

    # 環境設置
    environment: Environment = Environment.PRODUCTION
    debug: bool = False

    # 瀏覽器配置
    headless: bool = True
    disable_security: bool = False
    window_width: int = 1920
    window_height: int = 1080

    # 性能配置
    max_concurrent_browsers: int = 5
    request_timeout: int = 30000
    page_load_timeout: int = 60000

    # 重試配置
    max_retries: int = 3
    retry_delay: int = 2
    exponential_backoff: bool = True

    # 日誌配置
    log_level: str = "INFO"
    log_file: Optional[str] = "/var/log/browser-use/app.log"
    log_rotation: str = "1 day"
    log_retention: str = "30 days"

    # 監控配置
    enable_metrics: bool = True
    metrics_port: int = 9090

    # 安全配置
    use_proxy: bool = False
    proxy_url: Optional[str] = None
    user_agent: Optional[str] = None

    # API 配置
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None

    def __post_init__(self):
        """從環境變數載入敏感配置"""
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

    @classmethod
    def from_file(cls, config_file: str) -> "ProductionConfig":
        """從配置文件載入"""
        with open(config_file, 'r') as f:
            config_data = json.load(f)
        return cls(**config_data)

    def to_file(self, config_file: str):
        """保存配置到文件"""
        # 不保存敏感資訊
        config_data = asdict(self)
        config_data.pop('openai_api_key', None)
        config_data.pop('anthropic_api_key', None)

        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)


# ============================================================================
# 日誌系統
# ============================================================================

class ProductionLogger:
    """生產環境日誌系統"""

    def __init__(self, config: ProductionConfig):
        self.config = config
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """設置日誌記錄器"""
        logger = logging.getLogger("browser_use_production")
        logger.setLevel(getattr(logging, self.config.log_level))

        # 移除現有的處理器
        logger.handlers.clear()

        # 格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # 控制台處理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # 文件處理器
        if self.config.log_file:
            # 確保日誌目錄存在
            log_dir = Path(self.config.log_file).parent
            log_dir.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(self.config.log_file)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        return logger

    def info(self, message: str, **kwargs):
        """記錄訊息日誌"""
        self.logger.info(message, extra=kwargs)

    def warning(self, message: str, **kwargs):
        """記錄警告日誌"""
        self.logger.warning(message, extra=kwargs)

    def error(self, message: str, **kwargs):
        """記錄錯誤日誌"""
        self.logger.error(message, extra=kwargs)

    def critical(self, message: str, **kwargs):
        """記錄嚴重錯誤日誌"""
        self.logger.critical(message, extra=kwargs)

    def exception(self, message: str, exc_info=True):
        """記錄異常日誌"""
        self.logger.exception(message, exc_info=exc_info)


# ============================================================================
# 錯誤處理
# ============================================================================

class ProductionErrorHandler:
    """生產環境錯誤處理器"""

    def __init__(self, logger: ProductionLogger):
        self.logger = logger
        self.error_count = 0
        self.error_threshold = 10

    async def handle_error(self, error: Exception, context: Dict[str, Any]) -> bool:
        """
        處理錯誤

        Args:
            error: 異常物件
            context: 錯誤上下文

        Returns:
            bool: 是否應該重試
        """
        self.error_count += 1

        # 記錄錯誤
        self.logger.error(
            f"錯誤發生: {str(error)}",
            error_type=type(error).__name__,
            context=context,
            stack_trace=traceback.format_exc()
        )

        # 檢查是否超過錯誤閾值
        if self.error_count >= self.error_threshold:
            self.logger.critical(
                f"錯誤數量超過閾值 ({self.error_threshold})，需要人工介入"
            )
            # 發送告警
            await self._send_alert(error, context)
            return False

        # 判斷是否應該重試
        return self._should_retry(error)

    def _should_retry(self, error: Exception) -> bool:
        """判斷錯誤是否應該重試"""
        # 網路錯誤通常可以重試
        retriable_errors = [
            "TimeoutError",
            "NetworkError",
            "ConnectionError",
        ]

        error_type = type(error).__name__
        return error_type in retriable_errors

    async def _send_alert(self, error: Exception, context: Dict[str, Any]):
        """發送告警"""
        alert_message = {
            "level": "critical",
            "error": str(error),
            "error_type": type(error).__name__,
            "context": context,
            "timestamp": datetime.now().isoformat(),
        }

        # 這裡應該整合告警系統（如 PagerDuty、Slack 等）
        self.logger.critical(f"告警: {json.dumps(alert_message, indent=2)}")


# ============================================================================
# 性能監控
# ============================================================================

@dataclass
class PerformanceMetrics:
    """性能指標"""
    task_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: float = 0.0
    success: bool = False
    error: Optional[str] = None
    memory_usage: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "task_name": self.task_name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.duration,
            "success": self.success,
            "error": self.error,
            "memory_usage": self.memory_usage,
        }


class PerformanceMonitor:
    """性能監控器"""

    def __init__(self, logger: ProductionLogger):
        self.logger = logger
        self.metrics: List[PerformanceMetrics] = []

    def start_task(self, task_name: str) -> PerformanceMetrics:
        """開始任務監控"""
        metric = PerformanceMetrics(
            task_name=task_name,
            start_time=datetime.now()
        )
        self.metrics.append(metric)
        self.logger.info(f"開始任務: {task_name}")
        return metric

    def end_task(self, metric: PerformanceMetrics, success: bool = True, error: Optional[str] = None):
        """結束任務監控"""
        metric.end_time = datetime.now()
        metric.duration = (metric.end_time - metric.start_time).total_seconds()
        metric.success = success
        metric.error = error

        self.logger.info(
            f"任務完成: {metric.task_name}",
            duration=f"{metric.duration:.2f}s",
            success=success
        )

    def get_summary(self) -> Dict[str, Any]:
        """獲取性能摘要"""
        if not self.metrics:
            return {"message": "無性能數據"}

        total_tasks = len(self.metrics)
        successful_tasks = sum(1 for m in self.metrics if m.success)
        failed_tasks = total_tasks - successful_tasks
        avg_duration = sum(m.duration for m in self.metrics) / total_tasks

        return {
            "total_tasks": total_tasks,
            "successful_tasks": successful_tasks,
            "failed_tasks": failed_tasks,
            "success_rate": f"{(successful_tasks / total_tasks * 100):.2f}%",
            "average_duration": f"{avg_duration:.2f}s",
        }


# ============================================================================
# 生產環境 Agent
# ============================================================================

class ProductionAgent:
    """生產環境 Agent 包裝器"""

    def __init__(self, config: ProductionConfig):
        self.config = config
        self.logger = ProductionLogger(config)
        self.error_handler = ProductionErrorHandler(self.logger)
        self.monitor = PerformanceMonitor(self.logger)

    async def execute_task(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        執行任務

        Args:
            task: 任務描述
            **kwargs: 其他參數

        Returns:
            Dict: 執行結果
        """
        metric = self.monitor.start_task(task)

        try:
            # 創建瀏覽器配置
            browser_config = BrowserConfig(
                headless=self.config.headless,
                disable_security=self.config.disable_security,
                window_width=self.config.window_width,
                window_height=self.config.window_height,
            )

            # 創建 Agent
            agent = Agent(
                task=task,
                llm_model=kwargs.get('llm_model', 'gpt-4'),
                browser_config=browser_config,
            )

            # 執行任務
            result = await agent.run()

            # 記錄成功
            self.monitor.end_task(metric, success=True)
            self.logger.info("任務執行成功", task=task)

            return {
                "success": True,
                "result": result,
                "metrics": metric.to_dict(),
            }

        except Exception as e:
            # 處理錯誤
            should_retry = await self.error_handler.handle_error(
                e,
                context={"task": task, "kwargs": kwargs}
            )

            self.monitor.end_task(metric, success=False, error=str(e))

            return {
                "success": False,
                "error": str(e),
                "should_retry": should_retry,
                "metrics": metric.to_dict(),
            }


# ============================================================================
# 部署範例
# ============================================================================

async def production_deployment_example():
    """
    生產部署範例
    """
    print("\n" + "="*60)
    print("範例 1: 生產環境部署配置")
    print("="*60)

    # 創建生產配置
    config = ProductionConfig(
        environment=Environment.PRODUCTION,
        headless=True,
        max_concurrent_browsers=5,
        log_level="INFO",
    )

    print("\n生產環境配置：")
    print(f"- 環境: {config.environment.value}")
    print(f"- 無頭模式: {config.headless}")
    print(f"- 最大並行瀏覽器數: {config.max_concurrent_browsers}")
    print(f"- 日誌級別: {config.log_level}")
    print(f"- 請求超時: {config.request_timeout}ms")

    # 保存配置
    config_file = "/tmp/browser_use_production_config.json"
    config.to_file(config_file)
    print(f"\n配置已保存到: {config_file}")


async def logging_example():
    """
    日誌系統範例
    """
    print("\n" + "="*60)
    print("範例 2: 生產環境日誌系統")
    print("="*60)

    config = ProductionConfig(log_file="/tmp/browser_use_production.log")
    logger = ProductionLogger(config)

    print("\n日誌系統功能：")
    logger.info("這是一條訊息日誌")
    logger.warning("這是一條警告日誌")
    logger.error("這是一條錯誤日誌")

    print(f"\n日誌已寫入: {config.log_file}")


async def error_handling_example():
    """
    錯誤處理範例
    """
    print("\n" + "="*60)
    print("範例 3: 生產環境錯誤處理")
    print("="*60)

    config = ProductionConfig()
    logger = ProductionLogger(config)
    error_handler = ProductionErrorHandler(logger)

    print("\n錯誤處理功能：")
    print("- 自動錯誤記錄")
    print("- 智能重試判斷")
    print("- 錯誤計數和閾值")
    print("- 自動告警發送")

    # 模擬錯誤
    try:
        raise TimeoutError("模擬超時錯誤")
    except Exception as e:
        should_retry = await error_handler.handle_error(
            e,
            context={"operation": "測試操作"}
        )
        print(f"\n錯誤已處理，是否重試: {should_retry}")


async def monitoring_example():
    """
    性能監控範例
    """
    print("\n" + "="*60)
    print("範例 4: 性能監控")
    print("="*60)

    config = ProductionConfig()
    logger = ProductionLogger(config)
    monitor = PerformanceMonitor(logger)

    # 模擬多個任務
    for i in range(5):
        metric = monitor.start_task(f"任務_{i+1}")
        await asyncio.sleep(0.5)  # 模擬任務執行
        monitor.end_task(metric, success=(i % 4 != 0))  # 模擬一個失敗

    # 獲取摘要
    summary = monitor.get_summary()
    print("\n性能監控摘要：")
    for key, value in summary.items():
        print(f"- {key}: {value}")


async def production_agent_example():
    """
    生產環境 Agent 範例
    """
    print("\n" + "="*60)
    print("範例 5: 生產環境 Agent")
    print("="*60)

    # 檢查 API 金鑰
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠ 請設置 OPENAI_API_KEY 環境變數")
        return

    config = ProductionConfig(
        headless=True,
        log_file="/tmp/browser_use_agent.log"
    )

    agent = ProductionAgent(config)

    print("\n執行生產環境任務...")

    result = await agent.execute_task(
        task="訪問 https://example.com 並提取頁面標題",
        llm_model="gpt-4"
    )

    print(f"\n任務執行結果：")
    print(f"- 成功: {result['success']}")
    if result['success']:
        print(f"- 結果: {result['result'][:200]}...")
    else:
        print(f"- 錯誤: {result['error']}")
    print(f"- 執行時間: {result['metrics']['duration']:.2f}s")


def print_deployment_checklist():
    """
    打印部署檢查清單
    """
    print("\n" + "="*60)
    print("生產環境部署檢查清單")
    print("="*60)

    checklist = """
1. 環境配置
   □ 設置所有必要的環境變數
   □ 配置日誌系統
   □ 設置監控和告警
   □ 配置資源限制

2. 安全性
   □ 使用 HTTPS
   □ 不在代碼中硬編碼憑證
   □ 實施訪問控制
   □ 定期更新依賴

3. 性能優化
   □ 啟用無頭模式
   □ 設置並行限制
   □ 配置超時時間
   □ 實施緩存策略

4. 錯誤處理
   □ 實現全局錯誤處理
   □ 配置重試機制
   □ 設置錯誤告警
   □ 記錄詳細日誌

5. 監控和日誌
   □ 配置日誌輪轉
   □ 設置性能監控
   □ 實施健康檢查
   □ 配置告警閾值

6. 擴展性
   □ 支援水平擴展
   □ 實施負載均衡
   □ 配置自動擴展
   □ 資源隔離

7. 測試
   □ 完成單元測試
   □ 完成整合測試
   □ 執行壓力測試
   □ 驗證容錯能力

8. 文檔
   □ 撰寫部署文檔
   □ 更新運維手冊
   □ 記錄故障排除步驟
   □ 準備回滾計劃
    """

    print(checklist)


def print_best_practices():
    """
    打印生產環境最佳實踐
    """
    print("\n" + "="*60)
    print("生產環境最佳實踐")
    print("="*60)

    practices = """
1. 配置管理
   - 使用配置文件分離環境
   - 從環境變數讀取敏感資訊
   - 版本控制配置文件
   - 實施配置驗證

2. 日誌策略
   - 使用結構化日誌
   - 實施日誌級別分級
   - 配置日誌輪轉和歸檔
   - 集中化日誌管理

3. 監控告警
   - 監控關鍵指標
   - 設置合理的告警閾值
   - 實施多級告警
   - 定期審查告警

4. 資源管理
   - 限制並行任務數量
   - 實施資源配額
   - 監控資源使用
   - 自動擴展策略

5. 安全加固
   - 最小權限原則
   - 定期安全審計
   - 加密敏感數據
   - 實施訪問控制

6. 災難恢復
   - 定期備份
   - 測試恢復流程
   - 準備回滾計劃
   - 維護運行手冊

7. 持續改進
   - 收集性能數據
   - 分析錯誤模式
   - 優化瓶頸
   - 定期審查和更新
    """

    print(practices)


async def main():
    """
    主函數 - 運行所有生產部署範例
    """
    print("\n" + "="*60)
    print("Browser-Use 生產部署範例集")
    print("="*60)

    examples = [
        ("生產環境配置", production_deployment_example),
        ("日誌系統", logging_example),
        ("錯誤處理", error_handling_example),
        ("性能監控", monitoring_example),
        ("生產環境 Agent", production_agent_example),
    ]

    print("\n可用的生產部署範例：")
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i}. {name}")

    print("\n" + "-"*60)
    user_input = input("\n請選擇要運行的範例編號（1-5），輸入 'c' 查看檢查清單，或按 Enter 查看最佳實踐：")

    if user_input.strip().lower() == 'c':
        print_deployment_checklist()
    elif user_input.strip():
        try:
            index = int(user_input) - 1
            if 0 <= index < len(examples):
                name, func = examples[index]
                await func()
            else:
                print("無效的選擇！")
        except ValueError:
            print("請輸入有效的數字！")
    else:
        print_best_practices()

    print("\n" + "="*60)
    print("生產部署範例演示完成！")
    print("="*60)
    print("\n重要提醒：")
    print("- 生產環境需要嚴格的配置和監控")
    print("- 實施完善的錯誤處理和日誌記錄")
    print("- 定期審查和優化系統性能")
    print("- 準備好應急響應計劃")
    print("="*60 + "\n")


if __name__ == "__main__":
    """
    運行生產部署範例

    使用方式：
    python 10_生產部署.py
    """
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n程式已被用戶中斷。")
    except Exception as e:
        print(f"\n發生錯誤：{str(e)}")
        import traceback
        traceback.print_exc()

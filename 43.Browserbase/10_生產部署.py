"""
Browserbase 生產部署示例
========================

本模塊展示了如何將 Browserbase 應用部署到生產環境。
包括配置管理、監控、日誌、錯誤處理、擴展等最佳實踐。

主要內容:
1. 生產環境配置
2. 日誌和監控
3. 錯誤處理和告警
4. 性能優化
5. 安全性配置
6. 擴展和負載均衡

作者: Browserbase 示例團隊
日期: 2025-12-31
"""

import os
import sys
import json
import time
import logging
import hashlib
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from collections import defaultdict
from dotenv import load_dotenv


# 加載環境變量
load_dotenv()


class Environment(Enum):
    """環境類型"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(Enum):
    """日誌級別"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class ProductionConfig:
    """生產環境配置"""
    # 環境設置
    environment: Environment = Environment.PRODUCTION
    debug: bool = False

    # API 配置
    browserbase_api_key: str = ""
    browserbase_project_id: str = ""
    browserbase_api_url: str = "https://api.browserbase.com"

    # 並發配置
    max_workers: int = 10
    max_sessions: int = 50
    session_timeout: int = 300  # 秒

    # 重試配置
    max_retries: int = 3
    retry_delay: float = 1.0
    backoff_factor: float = 2.0

    # 監控配置
    enable_metrics: bool = True
    metrics_interval: int = 60  # 秒
    enable_health_check: bool = True
    health_check_interval: int = 30  # 秒

    # 日誌配置
    log_level: str = "INFO"
    log_file: str = "/var/log/browserbase/app.log"
    log_max_size: int = 10 * 1024 * 1024  # 10MB
    log_backup_count: int = 5

    # 安全配置
    enable_ssl_verification: bool = True
    api_rate_limit: int = 100  # 每分鐘請求數
    enable_ip_whitelist: bool = False
    allowed_ips: List[str] = field(default_factory=list)

    # 緩存配置
    enable_cache: bool = True
    cache_ttl: int = 3600  # 秒

    # 告警配置
    enable_alerts: bool = True
    alert_email: str = ""
    alert_webhook: str = ""
    error_threshold: int = 10  # 錯誤數量閾值

    @classmethod
    def from_env(cls) -> 'ProductionConfig':
        """從環境變量加載配置"""
        return cls(
            environment=Environment(os.getenv("ENVIRONMENT", "production")),
            debug=os.getenv("DEBUG", "false").lower() == "true",
            browserbase_api_key=os.getenv("BROWSERBASE_API_KEY", ""),
            browserbase_project_id=os.getenv("BROWSERBASE_PROJECT_ID", ""),
            max_workers=int(os.getenv("MAX_WORKERS", "10")),
            max_sessions=int(os.getenv("MAX_SESSIONS", "50")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            alert_email=os.getenv("ALERT_EMAIL", ""),
        )

    def validate(self) -> List[str]:
        """驗證配置"""
        errors = []

        if not self.browserbase_api_key:
            errors.append("BROWSERBASE_API_KEY 未設置")

        if not self.browserbase_project_id:
            errors.append("BROWSERBASE_PROJECT_ID 未設置")

        if self.max_workers < 1:
            errors.append("max_workers 必須大於 0")

        if self.enable_alerts and not (self.alert_email or self.alert_webhook):
            errors.append("啟用告警時必須設置郵件或 webhook")

        return errors


class ProductionLogger:
    """
    生產環境日誌器

    提供結構化的日誌記錄。
    """

    def __init__(self, config: ProductionConfig):
        """
        初始化日誌器

        Args:
            config: 生產配置
        """
        self.config = config
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """設置日誌器"""
        logger = logging.getLogger("browserbase")
        logger.setLevel(getattr(logging, self.config.log_level))

        # 清除現有處理器
        logger.handlers.clear()

        # 控制台處理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # 文件處理器（如果配置了）
        if self.config.log_file:
            try:
                log_dir = Path(self.config.log_file).parent
                log_dir.mkdir(parents=True, exist_ok=True)

                from logging.handlers import RotatingFileHandler
                file_handler = RotatingFileHandler(
                    self.config.log_file,
                    maxBytes=self.config.log_max_size,
                    backupCount=self.config.log_backup_count
                )
                file_handler.setLevel(logging.DEBUG)
                file_formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
                file_handler.setFormatter(file_formatter)
                logger.addHandler(file_handler)

            except Exception as e:
                print(f"警告: 無法設置文件日誌: {e}")

        return logger

    def info(self, message: str, **kwargs):
        """記錄信息日誌"""
        self._log(logging.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs):
        """記錄警告日誌"""
        self._log(logging.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs):
        """記錄錯誤日誌"""
        self._log(logging.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs):
        """記錄嚴重錯誤日誌"""
        self._log(logging.CRITICAL, message, **kwargs)

    def debug(self, message: str, **kwargs):
        """記錄調試日誌"""
        self._log(logging.DEBUG, message, **kwargs)

    def _log(self, level: int, message: str, **kwargs):
        """內部日誌方法"""
        # 添加額外的上下文信息
        if kwargs:
            message = f"{message} | {json.dumps(kwargs)}"

        self.logger.log(level, message)


class MetricsCollector:
    """
    指標收集器

    收集和報告應用性能指標。
    """

    def __init__(self, config: ProductionConfig):
        """
        初始化指標收集器

        Args:
            config: 生產配置
        """
        self.config = config
        self.metrics: Dict[str, List[float]] = defaultdict(list)
        self.counters: Dict[str, int] = defaultdict(int)
        self.start_time = datetime.now()

        print("[MetricsCollector] 初始化完成")

    def record_metric(self, name: str, value: float):
        """
        記錄指標

        Args:
            name: 指標名稱
            value: 指標值
        """
        self.metrics[name].append(value)

    def increment_counter(self, name: str, value: int = 1):
        """
        增加計數器

        Args:
            name: 計數器名稱
            value: 增加值
        """
        self.counters[name] += value

    def get_summary(self) -> Dict:
        """
        獲取指標摘要

        Returns:
            指標摘要
        """
        summary = {
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "counters": dict(self.counters),
            "metrics": {}
        }

        # 計算指標統計
        for name, values in self.metrics.items():
            if values:
                summary["metrics"][name] = {
                    "count": len(values),
                    "min": min(values),
                    "max": max(values),
                    "avg": sum(values) / len(values),
                    "sum": sum(values)
                }

        return summary

    def export_prometheus(self) -> str:
        """
        導出 Prometheus 格式

        Returns:
            Prometheus 格式的指標
        """
        lines = []

        # 計數器
        for name, value in self.counters.items():
            metric_name = name.replace(".", "_").replace("-", "_")
            lines.append(f"# TYPE {metric_name} counter")
            lines.append(f"{metric_name} {value}")

        # 指標
        for name, values in self.metrics.items():
            if values:
                metric_name = name.replace(".", "_").replace("-", "_")
                lines.append(f"# TYPE {metric_name} gauge")
                lines.append(f"{metric_name} {values[-1]}")  # 最新值

        return "\n".join(lines)

    def reset(self):
        """重置指標"""
        self.metrics.clear()
        self.counters.clear()
        print("[MetricsCollector] 指標已重置")


class HealthChecker:
    """
    健康檢查器

    檢查應用和依賴服務的健康狀態。
    """

    def __init__(self, config: ProductionConfig):
        """
        初始化健康檢查器

        Args:
            config: 生產配置
        """
        self.config = config
        self.last_check = None
        self.health_status = {}

        print("[HealthChecker] 初始化完成")

    def check_all(self) -> Dict:
        """
        檢查所有組件

        Returns:
            健康狀態
        """
        print("\n[HealthChecker] 執行健康檢查...")

        checks = {
            "api": self._check_api(),
            "database": self._check_database(),
            "cache": self._check_cache(),
            "disk": self._check_disk_space(),
            "memory": self._check_memory(),
        }

        # 計算總體狀態
        all_healthy = all(c["healthy"] for c in checks.values())

        result = {
            "timestamp": datetime.now().isoformat(),
            "healthy": all_healthy,
            "checks": checks
        }

        self.last_check = result
        self.health_status = result

        # 輸出結果
        status = "✓ 健康" if all_healthy else "✗ 不健康"
        print(f"  總體狀態: {status}\n")

        for name, check in checks.items():
            icon = "✓" if check["healthy"] else "✗"
            print(f"  {icon} {name}: {check.get('message', 'OK')}")

        return result

    def _check_api(self) -> Dict:
        """檢查 API 連接"""
        try:
            # 模擬 API 檢查
            healthy = True
            message = "API 連接正常"
        except Exception as e:
            healthy = False
            message = f"API 錯誤: {str(e)}"

        return {"healthy": healthy, "message": message}

    def _check_database(self) -> Dict:
        """檢查數據庫連接"""
        # 模擬檢查
        return {"healthy": True, "message": "數據庫連接正常"}

    def _check_cache(self) -> Dict:
        """檢查緩存服務"""
        if not self.config.enable_cache:
            return {"healthy": True, "message": "緩存未啟用"}

        return {"healthy": True, "message": "緩存服務正常"}

    def _check_disk_space(self) -> Dict:
        """檢查磁盤空間"""
        try:
            import shutil
            total, used, free = shutil.disk_usage("/")
            free_percent = (free / total) * 100

            healthy = free_percent > 10  # 至少 10% 空閒
            message = f"磁盤空間: {free_percent:.1f}% 可用"

            return {"healthy": healthy, "message": message}
        except:
            return {"healthy": True, "message": "無法檢查磁盤空間"}

    def _check_memory(self) -> Dict:
        """檢查內存使用"""
        # 簡化處理
        return {"healthy": True, "message": "內存使用正常"}


class AlertManager:
    """
    告警管理器

    發送告警通知。
    """

    def __init__(self, config: ProductionConfig, logger: ProductionLogger):
        """
        初始化告警管理器

        Args:
            config: 生產配置
            logger: 日誌器
        """
        self.config = config
        self.logger = logger
        self.alert_count = defaultdict(int)
        self.last_alert_time = {}

        print("[AlertManager] 初始化完成")

    def send_alert(
        self,
        level: str,
        title: str,
        message: str,
        metadata: Optional[Dict] = None
    ):
        """
        發送告警

        Args:
            level: 告警級別 (warning, error, critical)
            title: 告警標題
            message: 告警消息
            metadata: 元數據
        """
        if not self.config.enable_alerts:
            return

        # 檢查告警頻率限制
        alert_key = f"{level}:{title}"
        now = datetime.now()

        if alert_key in self.last_alert_time:
            last_time = self.last_alert_time[alert_key]
            if (now - last_time).total_seconds() < 300:  # 5分鐘內不重複
                self.logger.debug(f"告警被限制: {title}")
                return

        # 記錄告警
        self.alert_count[alert_key] += 1
        self.last_alert_time[alert_key] = now

        # 構建告警消息
        alert_data = {
            "timestamp": now.isoformat(),
            "level": level,
            "title": title,
            "message": message,
            "metadata": metadata or {},
            "environment": self.config.environment.value,
            "count": self.alert_count[alert_key]
        }

        self.logger.warning(f"告警: {title} | {message}")

        # 發送告警（模擬）
        self._send_email(alert_data)
        self._send_webhook(alert_data)

    def _send_email(self, alert_data: Dict):
        """發送郵件告警"""
        if not self.config.alert_email:
            return

        print(f"[AlertManager] 發送郵件告警到: {self.config.alert_email}")
        # 實際應該使用真實的郵件服務

    def _send_webhook(self, alert_data: Dict):
        """發送 Webhook 告警"""
        if not self.config.alert_webhook:
            return

        print(f"[AlertManager] 發送 Webhook 告警到: {self.config.alert_webhook}")
        # 實際應該使用真實的 HTTP 請求


class ProductionApplication:
    """
    生產應用

    整合所有組件的生產就緒應用。
    """

    def __init__(self, config: ProductionConfig):
        """
        初始化應用

        Args:
            config: 生產配置
        """
        self.config = config
        self.logger = ProductionLogger(config)
        self.metrics = MetricsCollector(config)
        self.health_checker = HealthChecker(config)
        self.alert_manager = AlertManager(config, self.logger)

        self.logger.info("應用初始化", environment=config.environment.value)

    def start(self):
        """啟動應用"""
        self.logger.info("應用啟動中...")

        # 驗證配置
        errors = self.config.validate()
        if errors:
            self.logger.critical("配置驗證失敗", errors=errors)
            raise RuntimeError(f"配置錯誤: {errors}")

        # 健康檢查
        if self.config.enable_health_check:
            health = self.health_checker.check_all()
            if not health["healthy"]:
                self.alert_manager.send_alert(
                    "warning",
                    "應用健康檢查失敗",
                    "某些組件不健康",
                    health["checks"]
                )

        self.logger.info("應用已啟動",
                        workers=self.config.max_workers,
                        sessions=self.config.max_sessions)

    def process_task(self, task_id: str, url: str) -> Dict:
        """
        處理任務

        Args:
            task_id: 任務 ID
            url: URL

        Returns:
            處理結果
        """
        start_time = time.time()

        self.logger.info(f"處理任務: {task_id}", url=url)
        self.metrics.increment_counter("tasks.total")

        try:
            # 模擬任務處理
            time.sleep(0.5)

            result = {
                "task_id": task_id,
                "url": url,
                "success": True,
                "timestamp": datetime.now().isoformat()
            }

            # 記錄指標
            duration = time.time() - start_time
            self.metrics.record_metric("task.duration", duration)
            self.metrics.increment_counter("tasks.success")

            self.logger.info(f"任務完成: {task_id}", duration=duration)

            return result

        except Exception as e:
            # 錯誤處理
            self.metrics.increment_counter("tasks.failed")
            self.logger.error(f"任務失敗: {task_id}", error=str(e))

            # 發送告警
            if self.metrics.counters["tasks.failed"] >= self.config.error_threshold:
                self.alert_manager.send_alert(
                    "error",
                    "任務失敗率過高",
                    f"失敗任務數: {self.metrics.counters['tasks.failed']}"
                )

            raise

    def get_status(self) -> Dict:
        """
        獲取應用狀態

        Returns:
            狀態信息
        """
        return {
            "environment": self.config.environment.value,
            "uptime": (datetime.now() - self.metrics.start_time).total_seconds(),
            "metrics": self.metrics.get_summary(),
            "health": self.health_checker.health_status
        }

    def shutdown(self):
        """關閉應用"""
        self.logger.info("應用關閉中...")

        # 導出最終指標
        summary = self.metrics.get_summary()
        self.logger.info("最終指標", **summary)

        self.logger.info("應用已關閉")


def example_production_setup():
    """示例1: 生產環境設置"""
    print("\n" + "=" * 60)
    print("示例1: 生產環境設置")
    print("=" * 60 + "\n")

    # 從環境變量加載配置
    config = ProductionConfig.from_env()

    # 如果缺少必要配置，使用演示值
    if not config.browserbase_api_key:
        config.browserbase_api_key = "demo_api_key"
        config.browserbase_project_id = "demo_project"

    print("生產配置:")
    print(f"  - 環境: {config.environment.value}")
    print(f"  - Debug: {config.debug}")
    print(f"  - 最大工作線程: {config.max_workers}")
    print(f"  - 最大 Session: {config.max_sessions}")
    print(f"  - 日誌級別: {config.log_level}")
    print(f"  - 啟用監控: {config.enable_metrics}")
    print(f"  - 啟用告警: {config.enable_alerts}")

    # 驗證配置
    errors = config.validate()
    if errors:
        print(f"\n配置錯誤:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("\n✓ 配置驗證通過")


def example_logging():
    """示例2: 日誌記錄"""
    print("\n" + "=" * 60)
    print("示例2: 生產日誌記錄")
    print("=" * 60 + "\n")

    config = ProductionConfig(
        log_level="INFO",
        log_file="./logs/browserbase.log"
    )

    logger = ProductionLogger(config)

    # 記錄不同級別的日誌
    logger.info("應用啟動", version="1.0.0")
    logger.warning("Session 數量接近上限", current=45, max=50)
    logger.error("API 請求失敗", url="https://example.com", status_code=500)

    print("\n✓ 日誌已記錄")


def example_metrics_and_monitoring():
    """示例3: 指標和監控"""
    print("\n" + "=" * 60)
    print("示例3: 指標收集和監控")
    print("=" * 60 + "\n")

    config = ProductionConfig()
    metrics = MetricsCollector(config)

    # 記錄一些指標
    for i in range(10):
        metrics.record_metric("response_time", 0.1 + i * 0.05)
        metrics.increment_counter("requests")

    metrics.increment_counter("errors", 2)

    # 獲取摘要
    summary = metrics.get_summary()

    print("指標摘要:")
    print(json.dumps(summary, indent=2, ensure_ascii=False))

    # Prometheus 格式
    print("\nPrometheus 格式:")
    print(metrics.export_prometheus())


def example_health_checks():
    """示例4: 健康檢查"""
    print("\n" + "=" * 60)
    print("示例4: 健康檢查")
    print("=" * 60 + "\n")

    config = ProductionConfig()
    health_checker = HealthChecker(config)

    # 執行健康檢查
    health = health_checker.check_all()


def example_complete_application():
    """示例5: 完整應用"""
    print("\n" + "=" * 60)
    print("示例5: 完整生產應用")
    print("=" * 60 + "\n")

    # 創建配置
    config = ProductionConfig(
        browserbase_api_key="demo_key",
        browserbase_project_id="demo_project",
        max_workers=3,
        enable_metrics=True,
        enable_alerts=False  # 禁用告警以簡化演示
    )

    # 創建應用
    app = ProductionApplication(config)

    # 啟動應用
    app.start()

    # 處理一些任務
    print("\n處理任務:")
    for i in range(5):
        try:
            result = app.process_task(
                task_id=f"task_{i + 1}",
                url=f"https://example.com/page/{i + 1}"
            )
            print(f"  ✓ {result['task_id']}")
        except Exception as e:
            print(f"  ✗ 任務失敗: {e}")

    # 獲取狀態
    print("\n應用狀態:")
    status = app.get_status()
    print(f"  - 運行時間: {status['uptime']:.2f}秒")
    print(f"  - 總任務數: {status['metrics']['counters'].get('tasks.total', 0)}")
    print(f"  - 成功任務數: {status['metrics']['counters'].get('tasks.success', 0)}")

    # 關閉應用
    app.shutdown()


def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("Browserbase 生產部署示例")
    print("=" * 60)

    # 運行所有示例
    example_production_setup()
    example_logging()
    example_metrics_and_monitoring()
    example_health_checks()
    example_complete_application()

    print("\n" + "=" * 60)
    print("所有示例完成！")
    print("=" * 60 + "\n")

    print("生產部署檢查清單:")
    print("✓ 配置管理（環境變量、配置文件）")
    print("✓ 日誌系統（結構化日誌、日誌輪轉）")
    print("✓ 監控系統（指標收集、Prometheus 集成）")
    print("✓ 健康檢查（API、數據庫、資源）")
    print("✓ 告警系統（郵件、Webhook、閾值）")
    print("✓ 錯誤處理（重試、降級、容錯）")
    print("✓ 安全配置（SSL、認證、速率限制）")
    print("✓ 性能優化（並發、緩存、連接池）")
    print("✓ 擴展性（負載均衡、水平擴展）")
    print("✓ 備份恢復（數據備份、災難恢復）")

    print("\n推薦工具和服務:")
    print("- 容器化: Docker, Kubernetes")
    print("- 監控: Prometheus, Grafana, Datadog")
    print("- 日誌: ELK Stack, Splunk, CloudWatch")
    print("- CI/CD: GitHub Actions, GitLab CI, Jenkins")
    print("- 告警: PagerDuty, Opsgenie, Slack")


if __name__ == "__main__":
    main()

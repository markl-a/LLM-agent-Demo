"""
Letta 生產環境部署

本模組展示如何在生產環境中部署 Letta Agent：
1. 配置管理
2. 日誌和監控
3. 錯誤處理和恢復
4. 性能優化
5. 安全性最佳實踐
6. 擴展性和負載均衡
7. 備份和災難恢復

確保 Letta 系統的穩定性和可靠性。

作者：Letta 框架示例
日期：2025-01
"""

import os
import json
import logging
import time
import threading
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from pathlib import Path
from queue import Queue
import traceback


@dataclass
class DeploymentConfig:
    """部署配置"""
    environment: str  # development, staging, production
    log_level: str
    max_workers: int
    database_url: str
    redis_url: Optional[str] = None
    api_keys: Dict[str, str] = field(default_factory=dict)
    feature_flags: Dict[str, bool] = field(default_factory=dict)
    monitoring_enabled: bool = True
    backup_enabled: bool = True
    auto_scaling: bool = False


@dataclass
class HealthStatus:
    """健康狀態"""
    status: str  # healthy, degraded, unhealthy
    timestamp: str
    components: Dict[str, bool]
    metrics: Dict[str, Any]
    errors: List[str] = field(default_factory=list)


class ConfigManager:
    """
    配置管理器

    管理應用配置，支持多環境。
    """

    def __init__(self, config_path: str = "./config"):
        """
        初始化配置管理器

        參數:
            config_path: 配置文件路徑
        """
        self.config_path = Path(config_path)
        self.config_path.mkdir(parents=True, exist_ok=True)
        self.configs: Dict[str, DeploymentConfig] = {}

        print("配置管理器初始化完成")

    def load_config(self, environment: str) -> DeploymentConfig:
        """
        加載配置

        參數:
            environment: 環境名稱

        返回:
            部署配置
        """
        config_file = self.config_path / f"{environment}.json"

        if config_file.exists():
            with open(config_file, 'r') as f:
                config_data = json.load(f)
                config = DeploymentConfig(**config_data)
        else:
            # 默認配置
            config = self._create_default_config(environment)
            self.save_config(environment, config)

        self.configs[environment] = config

        print(f"\n[配置加載] 環境: {environment}")
        print(f"  日誌級別: {config.log_level}")
        print(f"  最大工作者: {config.max_workers}")
        print(f"  監控: {'啟用' if config.monitoring_enabled else '禁用'}")

        return config

    def save_config(self, environment: str, config: DeploymentConfig) -> None:
        """
        保存配置

        參數:
            environment: 環境名稱
            config: 部署配置
        """
        config_file = self.config_path / f"{environment}.json"

        with open(config_file, 'w') as f:
            json.dump(config.__dict__, f, indent=2)

        print(f"\n[配置保存] 環境: {environment} -> {config_file}")

    def _create_default_config(self, environment: str) -> DeploymentConfig:
        """創建默認配置"""
        if environment == "production":
            return DeploymentConfig(
                environment=environment,
                log_level="INFO",
                max_workers=10,
                database_url="postgresql://localhost/letta_prod",
                redis_url="redis://localhost:6379",
                monitoring_enabled=True,
                backup_enabled=True,
                auto_scaling=True
            )
        elif environment == "staging":
            return DeploymentConfig(
                environment=environment,
                log_level="DEBUG",
                max_workers=5,
                database_url="postgresql://localhost/letta_staging",
                redis_url="redis://localhost:6379",
                monitoring_enabled=True,
                backup_enabled=True
            )
        else:  # development
            return DeploymentConfig(
                environment=environment,
                log_level="DEBUG",
                max_workers=2,
                database_url="sqlite:///letta_dev.db",
                monitoring_enabled=False,
                backup_enabled=False
            )


class LoggingManager:
    """
    日誌管理器

    統一管理應用日誌。
    """

    def __init__(self, log_dir: str = "./logs", log_level: str = "INFO"):
        """
        初始化日誌管理器

        參數:
            log_dir: 日誌目錄
            log_level: 日誌級別
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # 配置日誌
        self.logger = logging.getLogger("LettaProduction")
        self.logger.setLevel(getattr(logging, log_level))

        # 文件處理器
        file_handler = logging.FileHandler(
            self.log_dir / f"letta_{datetime.now().strftime('%Y%m%d')}.log"
        )
        file_handler.setLevel(logging.DEBUG)

        # 控制台處理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # 格式化
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        print(f"日誌管理器初始化完成（級別: {log_level}）")

    def info(self, message: str, **kwargs) -> None:
        """記錄 INFO 日誌"""
        self.logger.info(message, extra=kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """記錄 WARNING 日誌"""
        self.logger.warning(message, extra=kwargs)

    def error(self, message: str, exc_info: bool = False, **kwargs) -> None:
        """記錄 ERROR 日誌"""
        self.logger.error(message, exc_info=exc_info, extra=kwargs)

    def debug(self, message: str, **kwargs) -> None:
        """記錄 DEBUG 日誌"""
        self.logger.debug(message, extra=kwargs)


class MonitoringSystem:
    """
    監控系統

    監控 Agent 性能和健康狀態。
    """

    def __init__(self, logger: LoggingManager):
        """
        初始化監控系統

        參數:
            logger: 日誌管理器
        """
        self.logger = logger
        self.metrics: Dict[str, List[float]] = {}
        self.alerts: List[Dict[str, Any]] = []

        print("監控系統初始化完成")

    def record_metric(self, metric_name: str, value: float) -> None:
        """
        記錄指標

        參數:
            metric_name: 指標名稱
            value: 指標值
        """
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []

        self.metrics[metric_name].append(value)

        # 保持最近 1000 個數據點
        if len(self.metrics[metric_name]) > 1000:
            self.metrics[metric_name].pop(0)

    def get_metric_stats(self, metric_name: str) -> Dict[str, float]:
        """
        獲取指標統計

        參數:
            metric_name: 指標名稱

        返回:
            統計信息
        """
        if metric_name not in self.metrics or not self.metrics[metric_name]:
            return {}

        values = self.metrics[metric_name]

        stats = {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "latest": values[-1]
        }

        return stats

    def check_health(self) -> HealthStatus:
        """
        檢查系統健康狀態

        返回:
            健康狀態
        """
        components = {
            "database": True,  # 模擬檢查
            "redis": True,
            "agent_pool": True
        }

        metrics = {}
        for metric_name in self.metrics:
            metrics[metric_name] = self.get_metric_stats(metric_name)

        # 判斷整體狀態
        if all(components.values()):
            status = "healthy"
        elif any(components.values()):
            status = "degraded"
        else:
            status = "unhealthy"

        health = HealthStatus(
            status=status,
            timestamp=datetime.now().isoformat(),
            components=components,
            metrics=metrics
        )

        self.logger.info(f"健康檢查: {status}")

        return health

    def create_alert(self, alert_type: str, message: str, severity: str = "warning") -> None:
        """
        創建告警

        參數:
            alert_type: 告警類型
            message: 告警消息
            severity: 嚴重程度
        """
        alert = {
            "type": alert_type,
            "message": message,
            "severity": severity,
            "timestamp": datetime.now().isoformat()
        }

        self.alerts.append(alert)

        self.logger.warning(f"告警: [{alert_type}] {message}")

        # 在實際應用中，這裡會發送通知（郵件、Slack 等）


class ErrorHandler:
    """
    錯誤處理器

    統一處理和恢復錯誤。
    """

    def __init__(self, logger: LoggingManager, monitoring: MonitoringSystem):
        """
        初始化錯誤處理器

        參數:
            logger: 日誌管理器
            monitoring: 監控系統
        """
        self.logger = logger
        self.monitoring = monitoring
        self.error_counts: Dict[str, int] = {}

        print("錯誤處理器初始化完成")

    def handle_error(self, error: Exception, context: Dict[str, Any]) -> bool:
        """
        處理錯誤

        參數:
            error: 異常對象
            context: 上下文信息

        返回:
            是否成功處理
        """
        error_type = type(error).__name__

        # 記錄錯誤
        self.logger.error(
            f"錯誤: {error_type} - {str(error)}",
            exc_info=True
        )

        # 統計錯誤
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1

        # 檢查錯誤頻率
        if self.error_counts[error_type] > 10:
            self.monitoring.create_alert(
                alert_type="high_error_rate",
                message=f"{error_type} 錯誤頻率過高",
                severity="critical"
            )

        # 嘗試恢復
        recovery_strategy = self._get_recovery_strategy(error_type)
        if recovery_strategy:
            try:
                recovery_strategy(error, context)
                self.logger.info(f"錯誤恢復成功: {error_type}")
                return True
            except Exception as recovery_error:
                self.logger.error(f"錯誤恢復失敗: {recovery_error}")

        return False

    def _get_recovery_strategy(self, error_type: str) -> Optional[Callable]:
        """獲取恢復策略"""
        strategies = {
            "ConnectionError": self._reconnect_strategy,
            "TimeoutError": self._retry_strategy,
            "MemoryError": self._cleanup_strategy
        }

        return strategies.get(error_type)

    def _reconnect_strategy(self, error: Exception, context: Dict) -> None:
        """重連策略"""
        self.logger.info("執行重連策略...")
        time.sleep(1)  # 模擬重連
        # 實際應用中會重新建立連接

    def _retry_strategy(self, error: Exception, context: Dict) -> None:
        """重試策略"""
        self.logger.info("執行重試策略...")
        time.sleep(0.5)  # 模擬重試
        # 實際應用中會重新執行操作

    def _cleanup_strategy(self, error: Exception, context: Dict) -> None:
        """清理策略"""
        self.logger.info("執行清理策略...")
        # 實際應用中會清理內存


class BackupManager:
    """
    備份管理器

    管理數據備份和恢復。
    """

    def __init__(self, backup_dir: str = "./backups", logger: LoggingManager):
        """
        初始化備份管理器

        參數:
            backup_dir: 備份目錄
            logger: 日誌管理器
        """
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logger

        print(f"備份管理器初始化完成（目錄: {self.backup_dir}）")

    def create_backup(self, data: Dict[str, Any], backup_name: Optional[str] = None) -> str:
        """
        創建備份

        參數:
            data: 要備份的數據
            backup_name: 備份名稱

        返回:
            備份文件路徑
        """
        if backup_name is None:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        backup_file = self.backup_dir / f"{backup_name}.json"

        with open(backup_file, 'w') as f:
            json.dump(data, f, indent=2)

        self.logger.info(f"備份創建: {backup_file}")

        return str(backup_file)

    def list_backups(self) -> List[str]:
        """
        列出所有備份

        返回:
            備份文件列表
        """
        backups = sorted(self.backup_dir.glob("*.json"), reverse=True)
        backup_names = [b.stem for b in backups]

        print(f"\n[備份列表] 共 {len(backup_names)} 個備份")
        for name in backup_names[:5]:  # 顯示最近 5 個
            print(f"  - {name}")

        return backup_names

    def restore_backup(self, backup_name: str) -> Dict[str, Any]:
        """
        恢復備份

        參數:
            backup_name: 備份名稱

        返回:
            恢復的數據
        """
        backup_file = self.backup_dir / f"{backup_name}.json"

        if not backup_file.exists():
            raise FileNotFoundError(f"備份文件不存在: {backup_name}")

        with open(backup_file, 'r') as f:
            data = json.load(f)

        self.logger.info(f"備份恢復: {backup_name}")

        return data

    def cleanup_old_backups(self, keep_days: int = 7) -> None:
        """
        清理舊備份

        參數:
            keep_days: 保留天數
        """
        cutoff_time = datetime.now() - timedelta(days=keep_days)

        removed_count = 0
        for backup_file in self.backup_dir.glob("*.json"):
            file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
            if file_time < cutoff_time:
                backup_file.unlink()
                removed_count += 1

        self.logger.info(f"清理舊備份: 刪除 {removed_count} 個文件")


class ProductionAgent:
    """
    生產環境 Agent

    集成所有生產環境功能的 Agent。
    """

    def __init__(self, agent_id: str, config: DeploymentConfig):
        """
        初始化生產 Agent

        參數:
            agent_id: Agent ID
            config: 部署配置
        """
        self.agent_id = agent_id
        self.config = config

        # 初始化各個組件
        self.logger = LoggingManager(log_level=config.log_level)
        self.monitoring = MonitoringSystem(self.logger)
        self.error_handler = ErrorHandler(self.logger, self.monitoring)
        self.backup_manager = BackupManager(logger=self.logger)

        self.is_running = False

        self.logger.info(f"生產 Agent 初始化: {agent_id}")

    def start(self) -> None:
        """啟動 Agent"""
        self.is_running = True
        self.logger.info(f"Agent {self.agent_id} 已啟動")

        # 開始監控
        if self.config.monitoring_enabled:
            self._start_monitoring()

    def stop(self) -> None:
        """停止 Agent"""
        self.is_running = False

        # 創建停機備份
        if self.config.backup_enabled:
            self._create_shutdown_backup()

        self.logger.info(f"Agent {self.agent_id} 已停止")

    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        處理請求

        參數:
            request: 請求數據

        返回:
            響應數據
        """
        start_time = time.time()

        try:
            self.logger.debug(f"處理請求: {request.get('request_id')}")

            # 模擬處理
            result = self._execute_request(request)

            # 記錄指標
            processing_time = time.time() - start_time
            self.monitoring.record_metric("request_processing_time", processing_time)
            self.monitoring.record_metric("request_success", 1.0)

            self.logger.info(f"請求成功: {request.get('request_id')} ({processing_time:.3f}s)")

            return {
                "success": True,
                "result": result,
                "processing_time": processing_time
            }

        except Exception as e:
            # 錯誤處理
            processing_time = time.time() - start_time
            self.monitoring.record_metric("request_failure", 1.0)

            handled = self.error_handler.handle_error(e, {"request": request})

            return {
                "success": False,
                "error": str(e),
                "handled": handled,
                "processing_time": processing_time
            }

    def _execute_request(self, request: Dict[str, Any]) -> Any:
        """執行請求（模擬）"""
        # 模擬處理時間
        time.sleep(0.1)

        # 模擬偶爾失敗
        import random
        if random.random() < 0.05:  # 5% 失敗率
            raise Exception("模擬錯誤")

        return {"message": "請求處理完成"}

    def _start_monitoring(self) -> None:
        """開始監控"""
        def monitor_loop():
            while self.is_running:
                health = self.monitoring.check_health()
                if health.status != "healthy":
                    self.monitoring.create_alert(
                        alert_type="health_check",
                        message=f"系統狀態: {health.status}",
                        severity="warning" if health.status == "degraded" else "critical"
                    )
                time.sleep(60)  # 每分鐘檢查一次

        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()

    def _create_shutdown_backup(self) -> None:
        """創建停機備份"""
        backup_data = {
            "agent_id": self.agent_id,
            "shutdown_time": datetime.now().isoformat(),
            "metrics": self.monitoring.metrics,
            "alerts": self.monitoring.alerts[-10:]  # 最近 10 條告警
        }

        self.backup_manager.create_backup(backup_data, f"shutdown_{self.agent_id}")


def demonstrate_configuration():
    """演示配置管理"""
    print("\n" + "=" * 60)
    print("配置管理演示")
    print("=" * 60)

    config_manager = ConfigManager()

    # 加載不同環境的配置
    dev_config = config_manager.load_config("development")
    staging_config = config_manager.load_config("staging")
    prod_config = config_manager.load_config("production")


def demonstrate_logging_monitoring():
    """演示日誌和監控"""
    print("\n" + "=" * 60)
    print("日誌和監控演示")
    print("=" * 60)

    logger = LoggingManager()
    monitoring = MonitoringSystem(logger)

    # 記錄日誌
    logger.info("系統啟動")
    logger.debug("調試信息")
    logger.warning("警告信息")

    # 記錄指標
    for i in range(10):
        monitoring.record_metric("response_time", 0.1 + i * 0.01)
        monitoring.record_metric("memory_usage", 50 + i * 5)

    # 查看指標統計
    print("\n[指標統計]")
    stats = monitoring.get_metric_stats("response_time")
    print(f"響應時間: {stats}")

    # 健康檢查
    health = monitoring.check_health()
    print(f"\n[健康狀態] {health.status}")


def demonstrate_error_handling():
    """演示錯誤處理"""
    print("\n" + "=" * 60)
    print("錯誤處理演示")
    print("=" * 60)

    logger = LoggingManager()
    monitoring = MonitoringSystem(logger)
    error_handler = ErrorHandler(logger, monitoring)

    # 模擬不同類型的錯誤
    errors = [
        (ConnectionError("數據庫連接失敗"), {"operation": "database_query"}),
        (TimeoutError("請求超時"), {"operation": "api_call"}),
        (ValueError("無效參數"), {"operation": "validation"})
    ]

    for error, context in errors:
        print(f"\n處理錯誤: {type(error).__name__}")
        handled = error_handler.handle_error(error, context)
        print(f"處理結果: {'成功' if handled else '失敗'}")


def demonstrate_backup():
    """演示備份功能"""
    print("\n" + "=" * 60)
    print("備份功能演示")
    print("=" * 60)

    logger = LoggingManager()
    backup_manager = BackupManager(logger=logger)

    # 創建備份
    data = {
        "agents": ["agent_1", "agent_2"],
        "sessions": [{"id": "session_1"}],
        "timestamp": datetime.now().isoformat()
    }

    backup_path = backup_manager.create_backup(data, "test_backup")

    # 列出備份
    backup_manager.list_backups()

    # 恢復備份
    restored_data = backup_manager.restore_backup("test_backup")
    print(f"\n[恢復驗證] Agent 數量: {len(restored_data['agents'])}")


def demonstrate_production_agent():
    """演示生產 Agent"""
    print("\n" + "=" * 60)
    print("生產 Agent 演示")
    print("=" * 60)

    # 加載配置
    config_manager = ConfigManager()
    config = config_manager.load_config("production")

    # 創建生產 Agent
    agent = ProductionAgent("prod_agent_001", config)
    agent.start()

    # 處理請求
    requests = [
        {"request_id": f"req_{i}", "data": f"data_{i}"}
        for i in range(10)
    ]

    for request in requests:
        response = agent.process_request(request)
        if not response["success"]:
            print(f"請求失敗: {request['request_id']}")

    time.sleep(2)  # 等待監控

    # 停止 Agent
    agent.stop()

    # 查看指標
    print("\n[性能指標]")
    success_stats = agent.monitoring.get_metric_stats("request_success")
    failure_stats = agent.monitoring.get_metric_stats("request_failure")

    if success_stats:
        print(f"成功請求: {success_stats['count']}")
    if failure_stats:
        print(f"失敗請求: {failure_stats.get('count', 0)}")


def main():
    """主函數：運行所有演示"""
    print("\n" + "=" * 70)
    print(" " * 20 + "Letta 生產環境部署")
    print("=" * 70)

    # 配置管理
    demonstrate_configuration()

    # 日誌和監控
    demonstrate_logging_monitoring()

    # 錯誤處理
    demonstrate_error_handling()

    # 備份功能
    demonstrate_backup()

    # 生產 Agent
    demonstrate_production_agent()

    print("\n" + "=" * 70)
    print("生產部署演示完成！")
    print("=" * 70)
    print("\n關鍵要點：")
    print("  1. 配置管理支持多環境部署")
    print("  2. 完善的日誌系統便於問題排查")
    print("  3. 監控系統實時追蹤性能和健康狀態")
    print("  4. 錯誤處理機制提高系統穩定性")
    print("  5. 備份系統保證數據安全")
    print("  6. 生產 Agent 集成所有最佳實踐")
    print("\n" + "=" * 70)
    print("恭喜！您已完成 Letta 框架的全部學習")
    print("=" * 70)
    print("\n建議下一步：")
    print("  1. 閱讀官方文檔深入了解細節")
    print("  2. 在實際項目中應用所學知識")
    print("  3. 加入社區討論和分享經驗")
    print("  4. 關注框架更新和新特性")
    print("\n訪問 https://www.letta.com/ 獲取更多資源")
    print("=" * 70)


if __name__ == "__main__":
    main()

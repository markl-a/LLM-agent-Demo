"""
Julep 生產部署示例

這個模塊展示了 Julep 平台的生產環境部署功能。
包括配置管理、日誌記錄、監控、錯誤處理和性能優化。

主要功能：
1. 生產環境配置
2. 日誌系統
3. 監控和指標
4. 錯誤處理和告警
5. 性能優化
6. 健康檢查

作者：Julep 示例
日期：2025-12-31
"""

import os
import sys
import json
import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import threading
from collections import deque, defaultdict
import traceback


class Environment(Enum):
    """部署環境"""
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
    environment: Environment
    api_key: str
    base_url: str
    timeout: int = 30
    max_retries: int = 3
    rate_limit: int = 100  # 每分鐘請求數
    max_concurrent: int = 10
    enable_monitoring: bool = True
    enable_logging: bool = True
    log_level: LogLevel = LogLevel.INFO
    cache_enabled: bool = True
    cache_ttl: int = 3600  # 緩存過期時間（秒）

    def validate(self) -> bool:
        """驗證配置"""
        if not self.api_key:
            raise ValueError("API key is required")
        if self.timeout <= 0:
            raise ValueError("Timeout must be positive")
        if self.max_retries < 0:
            raise ValueError("Max retries cannot be negative")
        return True

    @classmethod
    def from_env(cls) -> 'ProductionConfig':
        """從環境變量加載配置"""
        env_name = os.getenv("ENVIRONMENT", "development")
        environment = Environment(env_name)

        return cls(
            environment=environment,
            api_key=os.getenv("JULEP_API_KEY", ""),
            base_url=os.getenv("JULEP_BASE_URL", "https://api.julep.ai/v1"),
            timeout=int(os.getenv("TIMEOUT", "30")),
            max_retries=int(os.getenv("MAX_RETRIES", "3")),
            rate_limit=int(os.getenv("RATE_LIMIT", "100")),
            max_concurrent=int(os.getenv("MAX_CONCURRENT", "10")),
            enable_monitoring=os.getenv("ENABLE_MONITORING", "true").lower() == "true",
            enable_logging=os.getenv("ENABLE_LOGGING", "true").lower() == "true",
            log_level=LogLevel(os.getenv("LOG_LEVEL", "INFO"))
        )


class Logger:
    """日誌系統

    統一的日誌記錄系統，支持多種輸出目標。
    """

    def __init__(
        self,
        name: str,
        level: LogLevel = LogLevel.INFO,
        log_file: Optional[str] = None
    ):
        """初始化日誌系統

        Args:
            name: 日誌名稱
            level: 日誌級別
            log_file: 日誌文件路徑
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.value))

        # 格式化
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # 控制台處理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # 文件處理器
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def debug(self, message: str, **kwargs):
        """Debug 日誌"""
        self.logger.debug(message, extra=kwargs)

    def info(self, message: str, **kwargs):
        """Info 日誌"""
        self.logger.info(message, extra=kwargs)

    def warning(self, message: str, **kwargs):
        """Warning 日誌"""
        self.logger.warning(message, extra=kwargs)

    def error(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """Error 日誌"""
        if exception:
            self.logger.error(f"{message}: {str(exception)}", extra=kwargs)
            self.logger.error(traceback.format_exc())
        else:
            self.logger.error(message, extra=kwargs)

    def critical(self, message: str, **kwargs):
        """Critical 日誌"""
        self.logger.critical(message, extra=kwargs)


@dataclass
class Metric:
    """監控指標"""
    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "name": self.name,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "tags": self.tags
        }


class MetricsCollector:
    """指標收集器

    收集和聚合系統運行指標。
    """

    def __init__(self):
        """初始化指標收集器"""
        self.metrics: deque = deque(maxlen=10000)
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self.lock = threading.Lock()

    def record_metric(
        self,
        name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None
    ):
        """記錄指標

        Args:
            name: 指標名稱
            value: 指標值
            tags: 標籤
        """
        metric = Metric(
            name=name,
            value=value,
            timestamp=datetime.now(),
            tags=tags or {}
        )

        with self.lock:
            self.metrics.append(metric)

    def increment_counter(self, name: str, value: int = 1):
        """增加計數器

        Args:
            name: 計數器名稱
            value: 增加值
        """
        with self.lock:
            self.counters[name] += value

    def set_gauge(self, name: str, value: float):
        """設置儀表

        Args:
            name: 儀表名稱
            value: 值
        """
        with self.lock:
            self.gauges[name] = value

    def record_histogram(self, name: str, value: float):
        """記錄直方圖

        Args:
            name: 直方圖名稱
            value: 值
        """
        with self.lock:
            self.histograms[name].append(value)
            # 只保留最近 1000 個值
            if len(self.histograms[name]) > 1000:
                self.histograms[name] = self.histograms[name][-1000:]

    def get_counter(self, name: str) -> int:
        """獲取計數器值"""
        with self.lock:
            return self.counters.get(name, 0)

    def get_gauge(self, name: str) -> Optional[float]:
        """獲取儀表值"""
        with self.lock:
            return self.gauges.get(name)

    def get_histogram_stats(self, name: str) -> Dict[str, float]:
        """獲取直方圖統計

        Args:
            name: 直方圖名稱

        Returns:
            統計信息
        """
        with self.lock:
            values = self.histograms.get(name, [])

        if not values:
            return {}

        sorted_values = sorted(values)
        count = len(sorted_values)

        return {
            "count": count,
            "min": sorted_values[0],
            "max": sorted_values[-1],
            "mean": sum(sorted_values) / count,
            "median": sorted_values[count // 2],
            "p95": sorted_values[int(count * 0.95)],
            "p99": sorted_values[int(count * 0.99)]
        }

    def get_summary(self) -> Dict[str, Any]:
        """獲取所有指標摘要"""
        with self.lock:
            return {
                "counters": dict(self.counters),
                "gauges": dict(self.gauges),
                "histograms": {
                    name: self.get_histogram_stats(name)
                    for name in self.histograms.keys()
                },
                "total_metrics": len(self.metrics)
            }


class HealthChecker:
    """健康檢查

    檢查系統各組件的健康狀態。
    """

    def __init__(self):
        """初始化健康檢查器"""
        self.checks: Dict[str, Callable] = {}
        self.last_results: Dict[str, bool] = {}

    def register_check(self, name: str, check_func: Callable):
        """註冊健康檢查

        Args:
            name: 檢查名稱
            check_func: 檢查函數（返回 bool）
        """
        self.checks[name] = check_func

    def run_check(self, name: str) -> bool:
        """運行單個檢查

        Args:
            name: 檢查名稱

        Returns:
            是否健康
        """
        if name not in self.checks:
            return False

        try:
            result = self.checks[name]()
            self.last_results[name] = result
            return result
        except Exception as e:
            print(f"[ERROR] 健康檢查失敗 {name}: {e}")
            self.last_results[name] = False
            return False

    def run_all_checks(self) -> Dict[str, bool]:
        """運行所有檢查

        Returns:
            檢查結果字典
        """
        results = {}
        for name in self.checks:
            results[name] = self.run_check(name)
        return results

    def is_healthy(self) -> bool:
        """檢查整體健康狀態

        Returns:
            是否所有檢查都通過
        """
        results = self.run_all_checks()
        return all(results.values())


class ErrorHandler:
    """錯誤處理器

    統一的錯誤處理和告警。
    """

    def __init__(self, logger: Logger, metrics: MetricsCollector):
        """初始化錯誤處理器

        Args:
            logger: 日誌系統
            metrics: 指標收集器
        """
        self.logger = logger
        self.metrics = metrics
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.lock = threading.Lock()

    def handle_error(
        self,
        error: Exception,
        context: Optional[Dict] = None,
        alert: bool = False
    ):
        """處理錯誤

        Args:
            error: 異常對象
            context: 上下文信息
            alert: 是否發送告警
        """
        error_type = type(error).__name__

        with self.lock:
            self.error_counts[error_type] += 1

        # 記錄日誌
        self.logger.error(
            f"錯誤發生: {error_type}",
            exception=error,
            context=context
        )

        # 記錄指標
        self.metrics.increment_counter(f"error.{error_type}")

        # 發送告警
        if alert:
            self._send_alert(error, context)

    def _send_alert(self, error: Exception, context: Optional[Dict]):
        """發送告警

        Args:
            error: 異常
            context: 上下文
        """
        alert_message = {
            "type": "error",
            "error": str(error),
            "error_type": type(error).__name__,
            "context": context,
            "timestamp": datetime.now().isoformat()
        }

        # 這裡應該發送到告警系統（如 PagerDuty, Slack 等）
        print(f"[ALERT] {json.dumps(alert_message, indent=2)}")

    def get_error_stats(self) -> Dict[str, int]:
        """獲取錯誤統計"""
        with self.lock:
            return dict(self.error_counts)


class RateLimiter:
    """速率限制器

    控制 API 調用速率。
    """

    def __init__(self, max_calls: int, time_window: int = 60):
        """初始化速率限制器

        Args:
            max_calls: 最大調用次數
            time_window: 時間窗口（秒）
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls: deque = deque()
        self.lock = threading.Lock()

    def acquire(self) -> bool:
        """獲取許可

        Returns:
            是否允許調用
        """
        with self.lock:
            now = time.time()

            # 移除過期的調用記錄
            while self.calls and self.calls[0] < now - self.time_window:
                self.calls.popleft()

            # 檢查是否超過限制
            if len(self.calls) >= self.max_calls:
                return False

            # 記錄調用
            self.calls.append(now)
            return True

    def wait_if_needed(self):
        """等待直到可以調用"""
        while not self.acquire():
            time.sleep(0.1)

    def get_stats(self) -> Dict[str, Any]:
        """獲取統計信息"""
        with self.lock:
            now = time.time()
            recent_calls = sum(1 for t in self.calls if t > now - self.time_window)

            return {
                "max_calls": self.max_calls,
                "time_window": self.time_window,
                "current_calls": recent_calls,
                "available": self.max_calls - recent_calls
            }


class ProductionSystem:
    """生產系統

    整合所有生產環境組件。
    """

    def __init__(self, config: ProductionConfig):
        """初始化生產系統

        Args:
            config: 配置對象
        """
        self.config = config
        self.config.validate()

        # 初始化組件
        self.logger = Logger(
            name="julep_production",
            level=config.log_level,
            log_file="julep.log" if config.enable_logging else None
        )

        self.metrics = MetricsCollector() if config.enable_monitoring else None
        self.health_checker = HealthChecker()
        self.error_handler = ErrorHandler(self.logger, self.metrics)
        self.rate_limiter = RateLimiter(max_calls=config.rate_limit)

        # 註冊健康檢查
        self._register_health_checks()

        self.logger.info(f"生產系統初始化完成 (環境: {config.environment.value})")

    def _register_health_checks(self):
        """註冊健康檢查"""
        self.health_checker.register_check("api", self._check_api_health)
        self.health_checker.register_check("rate_limit", self._check_rate_limit)
        self.health_checker.register_check("memory", self._check_memory)

    def _check_api_health(self) -> bool:
        """檢查 API 健康"""
        # 模擬 API 健康檢查
        return True

    def _check_rate_limit(self) -> bool:
        """檢查速率限制"""
        stats = self.rate_limiter.get_stats()
        return stats["available"] > 0

    def _check_memory(self) -> bool:
        """檢查內存使用"""
        # 簡化的內存檢查
        return True

    def execute_with_monitoring(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """執行函數並監控

        Args:
            func: 要執行的函數
            *args: 參數
            **kwargs: 關鍵字參數

        Returns:
            函數返回值
        """
        func_name = func.__name__

        # 速率限制
        self.rate_limiter.wait_if_needed()

        # 記錄開始
        start_time = time.time()
        self.logger.info(f"開始執行: {func_name}")

        if self.metrics:
            self.metrics.increment_counter(f"calls.{func_name}")

        try:
            # 執行函數
            result = func(*args, **kwargs)

            # 記錄成功
            duration = time.time() - start_time
            self.logger.info(f"執行成功: {func_name} (耗時: {duration:.2f}s)")

            if self.metrics:
                self.metrics.record_histogram(f"duration.{func_name}", duration)
                self.metrics.increment_counter(f"success.{func_name}")

            return result

        except Exception as e:
            # 記錄失敗
            duration = time.time() - start_time
            self.logger.error(f"執行失敗: {func_name}", exception=e)

            if self.metrics:
                self.metrics.increment_counter(f"failure.{func_name}")
                self.metrics.record_histogram(f"duration.{func_name}", duration)

            self.error_handler.handle_error(e, {"function": func_name})
            raise

    def get_system_status(self) -> Dict[str, Any]:
        """獲取系統狀態

        Returns:
            系統狀態字典
        """
        status = {
            "environment": self.config.environment.value,
            "healthy": self.health_checker.is_healthy(),
            "health_checks": self.health_checker.run_all_checks(),
            "rate_limiter": self.rate_limiter.get_stats(),
            "errors": self.error_handler.get_error_stats()
        }

        if self.metrics:
            status["metrics"] = self.metrics.get_summary()

        return status


def demo_production_config():
    """生產配置示例"""
    print("\n" + "="*60)
    print("示例 1: 生產環境配置")
    print("="*60)

    # 創建配置
    config = ProductionConfig(
        environment=Environment.PRODUCTION,
        api_key="prod_api_key_12345",
        base_url="https://api.julep.ai/v1",
        timeout=30,
        max_retries=3,
        rate_limit=100
    )

    # 驗證配置
    config.validate()

    print(f"\n配置信息:")
    print(f"  環境: {config.environment.value}")
    print(f"  超時: {config.timeout}s")
    print(f"  最大重試: {config.max_retries}")
    print(f"  速率限制: {config.rate_limit}/分鐘")
    print(f"  監控: {'啟用' if config.enable_monitoring else '禁用'}")


def demo_logging_system():
    """日誌系統示例"""
    print("\n" + "="*60)
    print("示例 2: 日誌系統")
    print("="*60)

    logger = Logger("demo", level=LogLevel.INFO)

    # 不同級別的日誌
    logger.info("應用程序啟動")
    logger.debug("調試信息（不會顯示，因為級別是 INFO）")
    logger.warning("這是一個警告")

    try:
        raise ValueError("模擬錯誤")
    except Exception as e:
        logger.error("捕獲到錯誤", exception=e)


def demo_metrics_collection():
    """指標收集示例"""
    print("\n" + "="*60)
    print("示例 3: 指標收集")
    print("="*60)

    metrics = MetricsCollector()

    # 記錄不同類型的指標
    print("\n記錄指標...")
    for i in range(10):
        metrics.increment_counter("api_calls")
        metrics.record_histogram("response_time", 0.1 + i * 0.05)

    metrics.set_gauge("active_sessions", 42)
    metrics.set_gauge("cpu_usage", 65.5)

    # 獲取統計
    print(f"\n指標摘要:")
    summary = metrics.get_summary()
    print(json.dumps(summary, indent=2, ensure_ascii=False))


def demo_health_checks():
    """健康檢查示例"""
    print("\n" + "="*60)
    print("示例 4: 健康檢查")
    print("="*60)

    checker = HealthChecker()

    # 註冊檢查
    checker.register_check("database", lambda: True)
    checker.register_check("cache", lambda: True)
    checker.register_check("api", lambda: False)  # 模擬失敗

    # 運行檢查
    print("\n運行健康檢查:")
    results = checker.run_all_checks()

    for name, status in results.items():
        status_str = "✓ 健康" if status else "✗ 異常"
        print(f"  {name}: {status_str}")

    print(f"\n整體狀態: {'健康' if checker.is_healthy() else '異常'}")


def demo_rate_limiting():
    """速率限制示例"""
    print("\n" + "="*60)
    print("示例 5: 速率限制")
    print("="*60)

    limiter = RateLimiter(max_calls=5, time_window=2)

    print("\n測試速率限制（5 次/2秒）:")
    for i in range(8):
        if limiter.acquire():
            print(f"  請求 {i+1}: ✓ 允許")
        else:
            print(f"  請求 {i+1}: ✗ 限流")

        time.sleep(0.3)

    stats = limiter.get_stats()
    print(f"\n統計: {stats}")


def demo_integrated_system():
    """集成系統示例"""
    print("\n" + "="*60)
    print("示例 6: 完整生產系統")
    print("="*60)

    # 創建配置
    config = ProductionConfig(
        environment=Environment.PRODUCTION,
        api_key="demo_key",
        base_url="https://api.julep.ai/v1"
    )

    # 初始化系統
    system = ProductionSystem(config)

    # 定義測試函數
    def process_request(data: Dict) -> Dict:
        """處理請求"""
        time.sleep(0.2)
        return {"status": "success", "data": data}

    # 執行帶監控的函數
    print("\n執行監控任務:")
    for i in range(3):
        result = system.execute_with_monitoring(
            process_request,
            data={"request_id": i+1}
        )
        print(f"  結果 {i+1}: {result}")

    # 獲取系統狀態
    print("\n系統狀態:")
    status = system.get_system_status()
    print(json.dumps(status, indent=2, ensure_ascii=False))


def main():
    """主函數"""
    print("="*60)
    print("Julep 生產部署示例")
    print("="*60)

    try:
        demo_production_config()
        demo_logging_system()
        demo_metrics_collection()
        demo_health_checks()
        demo_rate_limiting()
        demo_integrated_system()

        print("\n" + "="*60)
        print("所有示例執行完成！")
        print("="*60)

    except Exception as e:
        print(f"\n[ERROR] 執行出錯: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

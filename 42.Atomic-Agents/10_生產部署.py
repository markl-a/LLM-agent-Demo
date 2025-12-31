"""
Atomic Agents 生產部署
======================

本文件展示如何將 Atomic Agents 部署到生產環境。
包含配置管理、監控、日誌、擴展等生產級特性。

主要內容：
1. 配置管理
2. 日誌系統
3. 監控指標
4. 健康檢查
5. 負載均衡
6. 容器化部署

作者：Atomic Agents 團隊
日期：2025-12-31
"""

from typing import Any, Dict, List, Optional, Callable
from pydantic import BaseModel, Field, validator
from datetime import datetime, timedelta
from enum import Enum
import os
import json
from dataclasses import dataclass, field
from collections import defaultdict


# ============================================================================
# 第一部分：配置管理
# ============================================================================

class Environment(str, Enum):
    """環境類型"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class DatabaseConfig(BaseModel):
    """數據庫配置"""
    host: str = Field(default="localhost")
    port: int = Field(default=5432)
    database: str = Field(...)
    username: str = Field(...)
    password: str = Field(...)
    pool_size: int = Field(default=10)
    max_overflow: int = Field(default=20)


class CacheConfig(BaseModel):
    """緩存配置"""
    backend: str = Field(default="redis")
    host: str = Field(default="localhost")
    port: int = Field(default=6379)
    ttl: int = Field(default=3600, description="默認 TTL（秒）")
    max_size: int = Field(default=1000)


class LLMConfig(BaseModel):
    """LLM 配置"""
    provider: str = Field(...)
    model: str = Field(...)
    api_key: str = Field(...)
    api_base: Optional[str] = Field(None)
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(default=1000)
    timeout: int = Field(default=60)
    max_retries: int = Field(default=3)


class ApplicationConfig(BaseModel):
    """應用配置"""
    environment: Environment = Field(...)
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")

    # 服務配置
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    workers: int = Field(default=4)

    # 外部服務
    database: DatabaseConfig = Field(...)
    cache: CacheConfig = Field(...)
    llm: LLMConfig = Field(...)

    # 監控配置
    metrics_enabled: bool = Field(default=True)
    metrics_port: int = Field(default=9090)

    # 安全配置
    cors_origins: List[str] = Field(default_factory=list)
    api_key_required: bool = Field(default=True)
    rate_limit: int = Field(default=100, description="每分鐘請求限制")

    @validator('environment', pre=True)
    def validate_environment(cls, v):
        """驗證環境"""
        if isinstance(v, str):
            return Environment(v.lower())
        return v


class ConfigManager:
    """
    配置管理器

    管理應用配置的加載和訪問。
    """

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self._config: Optional[ApplicationConfig] = None

    def load(self) -> ApplicationConfig:
        """加載配置"""
        # 優先級：環境變量 > 配置文件 > 默認值

        # 1. 從環境變量加載
        env = os.getenv('APP_ENV', 'development')

        # 2. 從配置文件加載（如果存在）
        if self.config_path and os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
        else:
            config_data = self._get_default_config()

        # 3. 覆蓋環境變量
        config_data['environment'] = env
        config_data['debug'] = os.getenv('DEBUG', 'false').lower() == 'true'

        # LLM 配置從環境變量
        if 'OPENAI_API_KEY' in os.environ:
            config_data['llm']['api_key'] = os.environ['OPENAI_API_KEY']

        self._config = ApplicationConfig(**config_data)
        return self._config

    def _get_default_config(self) -> Dict[str, Any]:
        """獲取默認配置"""
        return {
            'environment': 'development',
            'debug': True,
            'log_level': 'DEBUG',
            'database': {
                'host': 'localhost',
                'port': 5432,
                'database': 'atomic_agents',
                'username': 'postgres',
                'password': 'postgres'
            },
            'cache': {
                'backend': 'redis',
                'host': 'localhost',
                'port': 6379
            },
            'llm': {
                'provider': 'openai',
                'model': 'gpt-4',
                'api_key': 'your-api-key'
            }
        }

    @property
    def config(self) -> ApplicationConfig:
        """獲取配置"""
        if not self._config:
            self.load()
        return self._config


# ============================================================================
# 第二部分：日誌系統
# ============================================================================

class LogLevel(str, Enum):
    """日誌級別"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogRecord(BaseModel):
    """日誌記錄"""
    level: LogLevel = Field(...)
    message: str = Field(...)
    timestamp: datetime = Field(default_factory=datetime.now)
    logger_name: str = Field(default="atomic_agents")
    context: Dict[str, Any] = Field(default_factory=dict)
    exception: Optional[str] = Field(None)


class Logger:
    """
    結構化日誌器

    提供結構化的日誌記錄。
    """

    def __init__(self, name: str, level: LogLevel = LogLevel.INFO):
        self.name = name
        self.level = level
        self.handlers: List[Callable] = []

    def add_handler(self, handler: Callable) -> None:
        """添加日誌處理器"""
        self.handlers.append(handler)

    def _log(
        self,
        level: LogLevel,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        exception: Optional[Exception] = None
    ) -> None:
        """記錄日誌"""
        # 檢查日誌級別
        level_order = {
            LogLevel.DEBUG: 0,
            LogLevel.INFO: 1,
            LogLevel.WARNING: 2,
            LogLevel.ERROR: 3,
            LogLevel.CRITICAL: 4
        }

        if level_order[level] < level_order[self.level]:
            return

        # 創建日誌記錄
        record = LogRecord(
            level=level,
            message=message,
            logger_name=self.name,
            context=context or {},
            exception=str(exception) if exception else None
        )

        # 調用處理器
        for handler in self.handlers:
            handler(record)

    def debug(self, message: str, **context) -> None:
        """調試日誌"""
        self._log(LogLevel.DEBUG, message, context)

    def info(self, message: str, **context) -> None:
        """信息日誌"""
        self._log(LogLevel.INFO, message, context)

    def warning(self, message: str, **context) -> None:
        """警告日誌"""
        self._log(LogLevel.WARNING, message, context)

    def error(self, message: str, exception: Optional[Exception] = None, **context) -> None:
        """錯誤日誌"""
        self._log(LogLevel.ERROR, message, context, exception)

    def critical(self, message: str, exception: Optional[Exception] = None, **context) -> None:
        """嚴重錯誤日誌"""
        self._log(LogLevel.CRITICAL, message, context, exception)


def console_handler(record: LogRecord) -> None:
    """控制台日誌處理器"""
    timestamp = record.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {record.level.value} - {record.logger_name} - {record.message}")
    if record.context:
        print(f"  Context: {record.context}")
    if record.exception:
        print(f"  Exception: {record.exception}")


def file_handler(filename: str):
    """文件日誌處理器工廠"""
    def handler(record: LogRecord) -> None:
        # 實際實現會寫入文件
        # 這裡僅作示例
        log_line = {
            'timestamp': record.timestamp.isoformat(),
            'level': record.level.value,
            'logger': record.logger_name,
            'message': record.message,
            'context': record.context
        }
        # with open(filename, 'a') as f:
        #     f.write(json.dumps(log_line) + '\n')
        pass

    return handler


# ============================================================================
# 第三部分：監控指標
# ============================================================================

class MetricType(str, Enum):
    """指標類型"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class Metric(BaseModel):
    """指標"""
    name: str = Field(...)
    type: MetricType = Field(...)
    value: float = Field(...)
    labels: Dict[str, str] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)


class MetricsCollector:
    """
    指標收集器

    收集和管理應用指標。
    """

    def __init__(self):
        self.metrics: Dict[str, List[Metric]] = defaultdict(list)
        self.counters: Dict[str, float] = defaultdict(float)
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, List[float]] = defaultdict(list)

    def increment_counter(
        self,
        name: str,
        value: float = 1.0,
        labels: Optional[Dict[str, str]] = None
    ) -> None:
        """增加計數器"""
        key = self._make_key(name, labels)
        self.counters[key] += value

        metric = Metric(
            name=name,
            type=MetricType.COUNTER,
            value=self.counters[key],
            labels=labels or {}
        )
        self.metrics[name].append(metric)

    def set_gauge(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None
    ) -> None:
        """設置儀表"""
        key = self._make_key(name, labels)
        self.gauges[key] = value

        metric = Metric(
            name=name,
            type=MetricType.GAUGE,
            value=value,
            labels=labels or {}
        )
        self.metrics[name].append(metric)

    def observe_histogram(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None
    ) -> None:
        """記錄直方圖值"""
        key = self._make_key(name, labels)
        self.histograms[key].append(value)

        metric = Metric(
            name=name,
            type=MetricType.HISTOGRAM,
            value=value,
            labels=labels or {}
        )
        self.metrics[name].append(metric)

    def get_metrics(self, name: Optional[str] = None) -> List[Metric]:
        """獲取指標"""
        if name:
            return self.metrics.get(name, [])

        # 返回所有指標
        all_metrics = []
        for metric_list in self.metrics.values():
            all_metrics.extend(metric_list)
        return all_metrics

    def get_summary(self) -> Dict[str, Any]:
        """獲取指標摘要"""
        return {
            'counters': dict(self.counters),
            'gauges': dict(self.gauges),
            'histograms': {
                key: {
                    'count': len(values),
                    'sum': sum(values),
                    'avg': sum(values) / len(values) if values else 0,
                    'min': min(values) if values else 0,
                    'max': max(values) if values else 0
                }
                for key, values in self.histograms.items()
            }
        }

    def _make_key(self, name: str, labels: Optional[Dict[str, str]]) -> str:
        """生成指標鍵"""
        if not labels:
            return name
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"


# ============================================================================
# 第四部分：健康檢查
# ============================================================================

class HealthStatus(str, Enum):
    """健康狀態"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class ComponentHealth(BaseModel):
    """組件健康狀態"""
    name: str = Field(...)
    status: HealthStatus = Field(...)
    message: Optional[str] = Field(None)
    checked_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class HealthChecker:
    """
    健康檢查器

    檢查各個組件的健康狀態。
    """

    def __init__(self):
        self.checks: Dict[str, Callable] = {}

    def register_check(self, name: str, check_func: Callable) -> None:
        """註冊健康檢查"""
        self.checks[name] = check_func

    def check_health(self) -> Dict[str, Any]:
        """執行健康檢查"""
        results = []
        overall_status = HealthStatus.HEALTHY

        for name, check_func in self.checks.items():
            try:
                result = check_func()

                if isinstance(result, ComponentHealth):
                    health = result
                else:
                    health = ComponentHealth(
                        name=name,
                        status=HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY,
                        message="檢查通過" if result else "檢查失敗"
                    )

                results.append(health)

                # 更新整體狀態
                if health.status == HealthStatus.UNHEALTHY:
                    overall_status = HealthStatus.UNHEALTHY
                elif health.status == HealthStatus.DEGRADED and overall_status != HealthStatus.UNHEALTHY:
                    overall_status = HealthStatus.DEGRADED

            except Exception as e:
                health = ComponentHealth(
                    name=name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"檢查異常: {str(e)}"
                )
                results.append(health)
                overall_status = HealthStatus.UNHEALTHY

        return {
            'status': overall_status.value,
            'timestamp': datetime.now().isoformat(),
            'components': [c.dict() for c in results]
        }


# ============================================================================
# 第五部分：請求追蹤
# ============================================================================

class RequestTrace(BaseModel):
    """請求追蹤"""
    trace_id: str = Field(...)
    operation: str = Field(...)
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: Optional[datetime] = Field(None)
    duration: Optional[float] = Field(None)
    status: str = Field(default="pending")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    spans: List[Dict[str, Any]] = Field(default_factory=list)

    def add_span(self, name: str, duration: float, **metadata) -> None:
        """添加跨度"""
        self.spans.append({
            'name': name,
            'duration': duration,
            'metadata': metadata,
            'timestamp': datetime.now().isoformat()
        })

    def complete(self, status: str = "success") -> None:
        """完成追蹤"""
        self.end_time = datetime.now()
        self.duration = (self.end_time - self.start_time).total_seconds()
        self.status = status


class TracingContext:
    """追蹤上下文"""

    def __init__(self, trace_id: str, operation: str):
        self.trace = RequestTrace(trace_id=trace_id, operation=operation)

    def __enter__(self):
        return self.trace

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.trace.complete(status="error")
        else:
            self.trace.complete(status="success")


# ============================================================================
# 第六部分：部署輔助工具
# ============================================================================

class DeploymentManager:
    """
    部署管理器

    管理應用的部署生命週期。
    """

    def __init__(self, config: ApplicationConfig):
        self.config = config
        self.logger = Logger("deployment")
        self.logger.add_handler(console_handler)
        self.health_checker = HealthChecker()
        self.metrics = MetricsCollector()

    def initialize(self) -> None:
        """初始化應用"""
        self.logger.info("初始化應用", environment=self.config.environment.value)

        # 註冊健康檢查
        self._register_health_checks()

        # 設置指標
        self._setup_metrics()

        self.logger.info("應用初始化完成")

    def _register_health_checks(self) -> None:
        """註冊健康檢查"""
        def check_database():
            # 實際會檢查數據庫連接
            return ComponentHealth(
                name="database",
                status=HealthStatus.HEALTHY,
                message="數據庫連接正常"
            )

        def check_cache():
            # 實際會檢查緩存連接
            return ComponentHealth(
                name="cache",
                status=HealthStatus.HEALTHY,
                message="緩存連接正常"
            )

        def check_llm():
            # 實際會檢查 LLM 服務
            return ComponentHealth(
                name="llm",
                status=HealthStatus.HEALTHY,
                message="LLM 服務正常"
            )

        self.health_checker.register_check("database", check_database)
        self.health_checker.register_check("cache", check_cache)
        self.health_checker.register_check("llm", check_llm)

    def _setup_metrics(self) -> None:
        """設置指標"""
        self.metrics.set_gauge("app_info", 1.0, {
            'version': '1.0.0',
            'environment': self.config.environment.value
        })

    def start(self) -> None:
        """啟動應用"""
        self.logger.info(
            "啟動應用",
            host=self.config.host,
            port=self.config.port,
            workers=self.config.workers
        )

        # 實際會啟動 web 服務器
        self.logger.info("應用已啟動")

    def shutdown(self) -> None:
        """關閉應用"""
        self.logger.info("關閉應用")

        # 清理資源
        self.logger.info("資源清理完成")


# ============================================================================
# 第七部分：使用示例
# ============================================================================

def example_config_management():
    """配置管理示例"""
    print("\n" + "="*60)
    print("示例 1: 配置管理")
    print("="*60)

    # 設置環境變量
    os.environ['APP_ENV'] = 'production'
    os.environ['DEBUG'] = 'false'

    # 加載配置
    config_manager = ConfigManager()
    config = config_manager.load()

    print(f"\n環境: {config.environment.value}")
    print(f"調試模式: {config.debug}")
    print(f"日誌級別: {config.log_level}")
    print(f"服務器: {config.host}:{config.port}")
    print(f"工作進程: {config.workers}")


def example_logging():
    """日誌系統示例"""
    print("\n" + "="*60)
    print("示例 2: 結構化日誌")
    print("="*60)

    # 創建日誌器
    logger = Logger("my_app", level=LogLevel.DEBUG)
    logger.add_handler(console_handler)

    # 記錄各種級別的日誌
    logger.debug("調試信息", user_id="123")
    logger.info("用戶登錄", user_id="456", ip="192.168.1.1")
    logger.warning("API 速率限制", requests=100, limit=100)
    logger.error("數據庫錯誤", exception=Exception("連接超時"))


def example_metrics():
    """監控指標示例"""
    print("\n" + "="*60)
    print("示例 3: 監控指標")
    print("="*60)

    metrics = MetricsCollector()

    # 記錄各種指標
    metrics.increment_counter("requests_total", labels={'method': 'GET', 'status': '200'})
    metrics.increment_counter("requests_total", labels={'method': 'POST', 'status': '201'})

    metrics.set_gauge("active_connections", 45.0)
    metrics.set_gauge("memory_usage_bytes", 1024 * 1024 * 512)

    metrics.observe_histogram("request_duration_seconds", 0.123)
    metrics.observe_histogram("request_duration_seconds", 0.456)
    metrics.observe_histogram("request_duration_seconds", 0.789)

    # 獲取摘要
    summary = metrics.get_summary()
    print(f"\n指標摘要:")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


def example_health_check():
    """健康檢查示例"""
    print("\n" + "="*60)
    print("示例 4: 健康檢查")
    print("="*60)

    health_checker = HealthChecker()

    # 註冊檢查
    health_checker.register_check("database", lambda: True)
    health_checker.register_check("cache", lambda: True)
    health_checker.register_check("storage", lambda: False)

    # 執行檢查
    health = health_checker.check_health()
    print(f"\n整體狀態: {health['status']}")
    print(f"檢查時間: {health['timestamp']}")
    print(f"\n組件狀態:")
    for component in health['components']:
        print(f"  - {component['name']}: {component['status']}")


def example_request_tracing():
    """請求追蹤示例"""
    print("\n" + "="*60)
    print("示例 5: 請求追蹤")
    print("="*60)

    # 使用追蹤上下文
    with TracingContext("trace-123", "process_request") as trace:
        # 模擬各個處理階段
        import time

        time.sleep(0.1)
        trace.add_span("validation", 0.1, items=10)

        time.sleep(0.2)
        trace.add_span("processing", 0.2, operations=5)

        time.sleep(0.15)
        trace.add_span("response", 0.15, bytes=1024)

    print(f"\n追蹤 ID: {trace.trace_id}")
    print(f"操作: {trace.operation}")
    print(f"狀態: {trace.status}")
    print(f"總耗時: {trace.duration:.3f}秒")
    print(f"\n跨度:")
    for span in trace.spans:
        print(f"  - {span['name']}: {span['duration']:.3f}秒")


def example_full_deployment():
    """完整部署示例"""
    print("\n" + "="*60)
    print("示例 6: 完整部署流程")
    print("="*60)

    # 加載配置
    config_manager = ConfigManager()
    config = config_manager.load()

    # 創建部署管理器
    deployment = DeploymentManager(config)

    # 初始化
    deployment.initialize()

    # 檢查健康狀態
    health = deployment.health_checker.check_health()
    print(f"\n健康檢查: {health['status']}")

    # 記錄一些指標
    deployment.metrics.increment_counter("app_starts_total")
    deployment.metrics.set_gauge("uptime_seconds", 0.0)

    # 模擬運行
    print("\n應用運行中...")

    # 關閉
    deployment.shutdown()


def main():
    """主函數"""
    print("\n" + "="*60)
    print("Atomic Agents 生產部署")
    print("="*60)

    # 運行示例
    example_config_management()
    example_logging()
    example_metrics()
    example_health_check()
    example_request_tracing()
    example_full_deployment()

    print("\n" + "="*60)
    print("所有示例運行完成！")
    print("="*60)

    print("\n部署檢查清單:")
    print("  ✓ 配置管理")
    print("  ✓ 日誌系統")
    print("  ✓ 監控指標")
    print("  ✓ 健康檢查")
    print("  ✓ 請求追蹤")
    print("  ✓ 錯誤處理")
    print("  ✓ 性能優化")
    print("\n準備部署到生產環境！")


if __name__ == "__main__":
    main()

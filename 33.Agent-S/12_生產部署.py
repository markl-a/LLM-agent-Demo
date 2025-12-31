"""
Agent-S 生產部署模組

此模組展示如何將 Agent-S 部署到生產環境：
1. 配置管理 - 管理生產環境配置
2. 監控日誌 - 監控 agent 運行狀態
3. 性能優化 - 優化執行效率
4. 安全性 - 實施安全措施
5. 可擴展性 - 支持水平擴展

本模組提供生產級別的 Agent-S 部署最佳實踐。
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Callable
from enum import Enum
from datetime import datetime
import time
import json
import logging
from pathlib import Path


class Environment(Enum):
    """部署環境"""
    DEVELOPMENT = "開發環境"
    STAGING = "測試環境"
    PRODUCTION = "生產環境"


class LogLevel(Enum):
    """日誌級別"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class DeploymentConfig:
    """部署配置"""
    environment: Environment
    api_keys: Dict[str, str] = field(default_factory=dict)
    rate_limits: Dict[str, int] = field(default_factory=dict)
    timeout_seconds: int = 300
    max_retries: int = 3
    enable_caching: bool = True
    cache_ttl_seconds: int = 3600
    log_level: LogLevel = LogLevel.INFO
    monitoring_enabled: bool = True
    security_enabled: bool = True

    @classmethod
    def from_file(cls, config_path: Path) -> 'DeploymentConfig':
        """從文件加載配置"""
        print(f"從 {config_path} 加載配置")
        # 模擬加載
        return cls(
            environment=Environment.PRODUCTION,
            api_keys={"openai": "sk-xxx", "anthropic": "sk-ant-xxx"},
            rate_limits={"api": 100, "concurrent_tasks": 10},
            timeout_seconds=300
        )

    def validate(self) -> bool:
        """驗證配置"""
        print("\n驗證配置...")

        errors = []

        # 檢查 API keys
        if not self.api_keys:
            errors.append("缺少 API keys")

        # 檢查超時設置
        if self.timeout_seconds < 0:
            errors.append("無效的超時設置")

        # 檢查速率限制
        if self.rate_limits.get("api", 0) <= 0:
            errors.append("無效的速率限制")

        if errors:
            print("配置驗證失敗:")
            for error in errors:
                print(f"  ✗ {error}")
            return False

        print("✓ 配置驗證通過")
        return True


@dataclass
class MetricData:
    """性能指標數據"""
    timestamp: datetime
    metric_name: str
    value: float
    tags: Dict[str, str] = field(default_factory=dict)


class Logger:
    """
    日誌記錄器

    提供結構化日誌記錄
    """

    def __init__(self, name: str, level: LogLevel = LogLevel.INFO):
        self.name = name
        self.level = level
        self.logs: List[Dict[str, Any]] = []

    def _log(self, level: LogLevel, message: str, **kwargs):
        """記錄日誌"""
        # 檢查日誌級別
        levels_order = [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARNING, LogLevel.ERROR, LogLevel.CRITICAL]
        if levels_order.index(level) < levels_order.index(self.level):
            return

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level.value,
            "logger": self.name,
            "message": message,
            **kwargs
        }

        self.logs.append(log_entry)

        # 打印日誌
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level.value}] {self.name}: {message}")

        if kwargs:
            print(f"  額外信息: {kwargs}")

    def debug(self, message: str, **kwargs):
        """記錄調試信息"""
        self._log(LogLevel.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs):
        """記錄信息"""
        self._log(LogLevel.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs):
        """記錄警告"""
        self._log(LogLevel.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs):
        """記錄錯誤"""
        self._log(LogLevel.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs):
        """記錄嚴重錯誤"""
        self._log(LogLevel.CRITICAL, message, **kwargs)


class MetricsCollector:
    """
    指標收集器

    收集和報告性能指標
    """

    def __init__(self):
        self.metrics: List[MetricData] = []
        self.counters: Dict[str, int] = {}
        self.gauges: Dict[str, float] = {}

    def counter(self, name: str, value: int = 1, **tags):
        """計數器指標"""
        self.counters[name] = self.counters.get(name, 0) + value

        self.metrics.append(MetricData(
            timestamp=datetime.now(),
            metric_name=name,
            value=self.counters[name],
            tags=tags
        ))

    def gauge(self, name: str, value: float, **tags):
        """儀表指標"""
        self.gauges[name] = value

        self.metrics.append(MetricData(
            timestamp=datetime.now(),
            metric_name=name,
            value=value,
            tags=tags
        ))

    def timing(self, name: str, duration: float, **tags):
        """時間指標"""
        self.metrics.append(MetricData(
            timestamp=datetime.now(),
            metric_name=f"{name}.duration",
            value=duration,
            tags=tags
        ))

    def get_summary(self) -> Dict[str, Any]:
        """獲取指標摘要"""
        return {
            "total_metrics": len(self.metrics),
            "counters": self.counters.copy(),
            "gauges": self.gauges.copy(),
            "last_updated": datetime.now().isoformat()
        }


class HealthChecker:
    """
    健康檢查器

    檢查系統健康狀態
    """

    def __init__(self):
        self.checks: Dict[str, Callable] = {}
        self.last_check_results: Dict[str, bool] = {}

    def register_check(self, name: str, check_func: Callable):
        """註冊健康檢查"""
        self.checks[name] = check_func

    def run_checks(self) -> Dict[str, Any]:
        """運行所有健康檢查"""
        print("\n執行健康檢查...")

        results = {}
        all_healthy = True

        for name, check_func in self.checks.items():
            try:
                is_healthy = check_func()
                results[name] = {
                    "healthy": is_healthy,
                    "message": "OK" if is_healthy else "Failed"
                }
                self.last_check_results[name] = is_healthy

                status = "✓" if is_healthy else "✗"
                print(f"  {status} {name}: {results[name]['message']}")

                if not is_healthy:
                    all_healthy = False

            except Exception as e:
                results[name] = {
                    "healthy": False,
                    "message": str(e)
                }
                all_healthy = False
                print(f"  ✗ {name}: 錯誤 - {e}")

        results["overall"] = {
            "healthy": all_healthy,
            "timestamp": datetime.now().isoformat()
        }

        return results

    def is_healthy(self) -> bool:
        """檢查整體健康狀態"""
        return all(self.last_check_results.values())


class RateLimiter:
    """
    速率限制器

    控制 API 調用頻率
    """

    def __init__(self, max_requests: int, time_window: float = 60.0):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: List[datetime] = []

    def acquire(self) -> bool:
        """獲取許可"""
        now = datetime.now()

        # 清理過期請求
        cutoff = now.timestamp() - self.time_window
        self.requests = [
            req for req in self.requests
            if req.timestamp() > cutoff
        ]

        # 檢查是否超限
        if len(self.requests) >= self.max_requests:
            wait_time = self.time_window - (now.timestamp() - self.requests[0].timestamp())
            print(f"速率限制：需要等待 {wait_time:.1f} 秒")
            return False

        # 記錄請求
        self.requests.append(now)
        return True

    def wait_if_needed(self):
        """如果需要則等待"""
        while not self.acquire():
            time.sleep(1.0)


class Cache:
    """
    簡單緩存實現

    緩存計算結果以提高性能
    """

    def __init__(self, ttl_seconds: int = 3600):
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, Dict[str, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        """獲取緩存值"""
        if key not in self.cache:
            return None

        entry = self.cache[key]

        # 檢查是否過期
        age = (datetime.now() - entry["timestamp"]).total_seconds()
        if age > self.ttl_seconds:
            del self.cache[key]
            return None

        print(f"緩存命中: {key}")
        return entry["value"]

    def set(self, key: str, value: Any):
        """設置緩存值"""
        self.cache[key] = {
            "value": value,
            "timestamp": datetime.now()
        }
        print(f"緩存設置: {key}")

    def clear(self):
        """清空緩存"""
        self.cache.clear()
        print("緩存已清空")

    def get_stats(self) -> Dict[str, Any]:
        """獲取緩存統計"""
        return {
            "size": len(self.cache),
            "ttl_seconds": self.ttl_seconds
        }


class ProductionAgent:
    """
    生產級 Agent

    整合所有生產特性的 Agent
    """

    def __init__(self, config: DeploymentConfig):
        self.config = config
        self.logger = Logger("ProductionAgent", config.log_level)
        self.metrics = MetricsCollector()
        self.health_checker = HealthChecker()
        self.rate_limiter = RateLimiter(config.rate_limits.get("api", 100))
        self.cache = Cache(config.cache_ttl_seconds) if config.enable_caching else None

        # 註冊健康檢查
        self._register_health_checks()

        self.logger.info("生產 Agent 已初始化", environment=config.environment.value)

    def _register_health_checks(self):
        """註冊健康檢查"""
        self.health_checker.register_check("config", lambda: self.config.validate())
        self.health_checker.register_check("cache", lambda: self.cache is not None if self.config.enable_caching else True)

    def execute_task(self, task_id: str, task_func: Callable, *args, **kwargs) -> Any:
        """
        執行任務（帶完整監控）

        Args:
            task_id: 任務 ID
            task_func: 任務函數
            *args, **kwargs: 任務參數

        Returns:
            任務結果
        """
        self.logger.info(f"開始執行任務", task_id=task_id)

        # 增加任務計數器
        self.metrics.counter("tasks.started", task_id=task_id)

        start_time = time.time()

        try:
            # 檢查速率限制
            self.rate_limiter.wait_if_needed()

            # 檢查緩存
            cache_key = f"{task_id}_{hash(str(args))}"
            if self.cache:
                cached_result = self.cache.get(cache_key)
                if cached_result is not None:
                    self.metrics.counter("cache.hits")
                    self.logger.info("使用緩存結果", task_id=task_id)
                    return cached_result

            # 執行任務
            result = task_func(*args, **kwargs)

            # 緩存結果
            if self.cache:
                self.cache.set(cache_key, result)

            # 記錄成功
            duration = time.time() - start_time
            self.metrics.counter("tasks.completed", task_id=task_id)
            self.metrics.timing("tasks.duration", duration, task_id=task_id)
            self.logger.info(f"任務完成", task_id=task_id, duration=f"{duration:.2f}s")

            return result

        except Exception as e:
            # 記錄失敗
            duration = time.time() - start_time
            self.metrics.counter("tasks.failed", task_id=task_id)
            self.metrics.timing("tasks.duration", duration, task_id=task_id)
            self.logger.error(f"任務失敗", task_id=task_id, error=str(e), duration=f"{duration:.2f}s")

            raise

    def get_status(self) -> Dict[str, Any]:
        """獲取 Agent 狀態"""
        return {
            "environment": self.config.environment.value,
            "health": self.health_checker.run_checks(),
            "metrics": self.metrics.get_summary(),
            "cache": self.cache.get_stats() if self.cache else None
        }


class DeploymentManager:
    """
    部署管理器

    管理 Agent 的部署和運維
    """

    def __init__(self):
        self.agents: Dict[str, ProductionAgent] = {}
        self.logger = Logger("DeploymentManager")

    def deploy_agent(self, agent_id: str, config: DeploymentConfig) -> ProductionAgent:
        """部署 Agent"""
        self.logger.info(f"部署 Agent", agent_id=agent_id, environment=config.environment.value)

        # 驗證配置
        if not config.validate():
            raise ValueError("配置驗證失敗")

        # 創建 Agent
        agent = ProductionAgent(config)

        # 運行健康檢查
        health_results = agent.health_checker.run_checks()
        if not health_results["overall"]["healthy"]:
            raise RuntimeError("健康檢查失敗")

        # 註冊 Agent
        self.agents[agent_id] = agent

        self.logger.info(f"Agent 部署成功", agent_id=agent_id)

        return agent

    def shutdown_agent(self, agent_id: str):
        """關閉 Agent"""
        if agent_id not in self.agents:
            return

        self.logger.info(f"關閉 Agent", agent_id=agent_id)

        agent = self.agents[agent_id]

        # 清理資源
        if agent.cache:
            agent.cache.clear()

        # 移除 Agent
        del self.agents[agent_id]

        self.logger.info(f"Agent 已關閉", agent_id=agent_id)

    def get_all_status(self) -> Dict[str, Any]:
        """獲取所有 Agent 狀態"""
        return {
            agent_id: agent.get_status()
            for agent_id, agent in self.agents.items()
        }


def 示例1_配置管理():
    """示例：配置管理"""
    print("\n" + "="*60)
    print("示例 1: 配置管理")
    print("="*60)

    # 創建配置
    config = DeploymentConfig(
        environment=Environment.PRODUCTION,
        api_keys={
            "openai": "sk-xxx",
            "anthropic": "sk-ant-xxx"
        },
        rate_limits={
            "api": 100,
            "concurrent_tasks": 10
        },
        timeout_seconds=300,
        enable_caching=True,
        log_level=LogLevel.INFO
    )

    # 驗證配置
    config.validate()

    # 顯示配置
    print("\n配置詳情:")
    print(f"  環境: {config.environment.value}")
    print(f"  速率限制: {config.rate_limits}")
    print(f"  緩存: {'啟用' if config.enable_caching else '禁用'}")
    print(f"  日誌級別: {config.log_level.value}")

    return config


def 示例2_日誌記錄():
    """示例：日誌記錄"""
    print("\n" + "="*60)
    print("示例 2: 日誌記錄")
    print("="*60)

    logger = Logger("MyAgent", LogLevel.DEBUG)

    # 記錄不同級別的日誌
    logger.debug("這是調試信息", component="task_executor")
    logger.info("任務開始執行", task_id="task_001")
    logger.warning("速率限制接近", usage=90, limit=100)
    logger.error("任務執行失敗", task_id="task_002", error="Timeout")

    print(f"\n共記錄 {len(logger.logs)} 條日誌")

    return logger


def 示例3_性能監控():
    """示例：性能監控"""
    print("\n" + "="*60)
    print("示例 3: 性能監控")
    print("="*60)

    metrics = MetricsCollector()

    # 模擬收集指標
    for i in range(5):
        metrics.counter("api.requests", endpoint="/chat")
        metrics.timing("api.latency", 0.1 + i * 0.05, endpoint="/chat")

    metrics.gauge("memory.usage", 512.5, unit="MB")
    metrics.gauge("cpu.usage", 45.2, unit="%")

    # 顯示摘要
    summary = metrics.get_summary()
    print("\n指標摘要:")
    print(json.dumps(summary, indent=2, ensure_ascii=False))

    return metrics


def 示例4_健康檢查():
    """示例：健康檢查"""
    print("\n" + "="*60)
    print("示例 4: 健康檢查")
    print("="*60)

    health = HealthChecker()

    # 註冊檢查
    health.register_check("database", lambda: True)
    health.register_check("cache", lambda: True)
    health.register_check("api", lambda: True)

    # 運行檢查
    results = health.run_checks()

    print(f"\n整體健康狀態: {'健康' if results['overall']['healthy'] else '不健康'}")

    return health


def 示例5_生產部署():
    """示例：完整的生產部署"""
    print("\n" + "="*60)
    print("示例 5: 生產部署")
    print("="*60)

    # 創建部署管理器
    manager = DeploymentManager()

    # 創建生產配置
    config = DeploymentConfig(
        environment=Environment.PRODUCTION,
        api_keys={"openai": "sk-xxx"},
        rate_limits={"api": 50},
        enable_caching=True,
        log_level=LogLevel.INFO
    )

    # 部署 Agent
    agent = manager.deploy_agent("agent_001", config)

    # 執行任務
    def 示例任務():
        print("  執行示例任務...")
        time.sleep(0.2)
        return {"status": "success", "result": "任務完成"}

    # 執行多個任務
    for i in range(3):
        result = agent.execute_task(f"task_{i+1}", 示例任務)
        print(f"\n任務 {i+1} 結果: {result}")

    # 獲取狀態
    print("\n" + "="*60)
    print("Agent 狀態報告")
    print("="*60)

    status = agent.get_status()
    print(json.dumps(status, indent=2, ensure_ascii=False))

    # 關閉 Agent
    manager.shutdown_agent("agent_001")

    return manager


def 示例6_多環境部署():
    """示例：多環境部署"""
    print("\n" + "="*60)
    print("示例 6: 多環境部署")
    print("="*60)

    manager = DeploymentManager()

    # 部署到不同環境
    environments = [
        (Environment.DEVELOPMENT, LogLevel.DEBUG, 1000),
        (Environment.STAGING, LogLevel.INFO, 500),
        (Environment.PRODUCTION, LogLevel.WARNING, 100),
    ]

    for env, log_level, rate_limit in environments:
        config = DeploymentConfig(
            environment=env,
            api_keys={"openai": "sk-xxx"},
            rate_limits={"api": rate_limit},
            log_level=log_level
        )

        agent_id = f"agent_{env.name.lower()}"
        agent = manager.deploy_agent(agent_id, config)

        print(f"\n✓ {env.value} 部署完成")

    # 獲取所有狀態
    print("\n" + "="*60)
    print("所有環境狀態")
    print("="*60)

    all_status = manager.get_all_status()
    for agent_id, status in all_status.items():
        print(f"\n{agent_id}:")
        print(f"  環境: {status['environment']}")
        print(f"  健康: {status['health']['overall']['healthy']}")

    # 清理
    for agent_id in list(manager.agents.keys()):
        manager.shutdown_agent(agent_id)

    return manager


if __name__ == "__main__":
    print("Agent-S 生產部署演示\n")

    示例1_配置管理()
    示例2_日誌記錄()
    示例3_性能監控()
    示例4_健康檢查()
    示例5_生產部署()
    示例6_多環境部署()

    print("\n所有示例執行完成！")

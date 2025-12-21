"""
Dify 部署與監控範例
==================

本範例展示如何部署和監控 Dify 應用。

部署和監控功能：
1. Docker 部署
2. 健康檢查
3. 性能監控
4. 日誌管理
5. 告警設置

安裝依賴：
pip install requests prometheus-client
"""

import os
import json
import time
import logging
import requests
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
from threading import Thread, Lock
import statistics

# ============================================================
# 配置
# ============================================================

DIFY_API_KEY = os.getenv("DIFY_API_KEY", "app-xxxxxxxxxxxxxxxx")
DIFY_BASE_URL = os.getenv("DIFY_BASE_URL", "https://api.dify.ai/v1")

# 日誌配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("dify_monitor")


# ============================================================
# 健康檢查
# ============================================================

class HealthChecker:
    """
    健康檢查器

    監控 Dify 服務的健康狀態
    """

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def check_api_health(self) -> Dict[str, Any]:
        """
        檢查 API 健康狀態

        Returns:
            健康狀態信息
        """
        start_time = time.time()

        try:
            # 嘗試獲取應用信息
            url = f"{self.base_url}/parameters"
            response = requests.get(url, headers=self.headers, timeout=10)

            latency = (time.time() - start_time) * 1000  # 毫秒

            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "latency_ms": round(latency, 2),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": f"HTTP {response.status_code}",
                    "latency_ms": round(latency, 2),
                    "timestamp": datetime.now().isoformat()
                }

        except requests.exceptions.Timeout:
            return {
                "status": "unhealthy",
                "error": "Timeout",
                "timestamp": datetime.now().isoformat()
            }
        except requests.exceptions.RequestException as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def check_model_availability(self) -> Dict[str, Any]:
        """
        檢查模型可用性

        Returns:
            模型狀態信息
        """
        try:
            # 發送一個簡單的測試請求
            url = f"{self.base_url}/chat-messages"
            payload = {
                "query": "test",
                "user": "health-check",
                "response_mode": "blocking"
            }

            start_time = time.time()
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            latency = (time.time() - start_time) * 1000

            if response.status_code == 200:
                return {
                    "status": "available",
                    "latency_ms": round(latency, 2),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "unavailable",
                    "error": response.text[:100],
                    "timestamp": datetime.now().isoformat()
                }

        except Exception as e:
            return {
                "status": "unavailable",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


# ============================================================
# 性能監控
# ============================================================

@dataclass
class MetricPoint:
    """指標數據點"""
    value: float
    timestamp: datetime = field(default_factory=datetime.now)


class MetricsCollector:
    """
    指標收集器

    收集和管理性能指標
    """

    def __init__(self, retention_hours: int = 24):
        self.metrics: Dict[str, List[MetricPoint]] = defaultdict(list)
        self.retention = timedelta(hours=retention_hours)
        self._lock = Lock()

    def record(self, metric_name: str, value: float):
        """
        記錄指標值

        Args:
            metric_name: 指標名稱
            value: 指標值
        """
        with self._lock:
            self.metrics[metric_name].append(MetricPoint(value=value))
            self._cleanup(metric_name)

    def _cleanup(self, metric_name: str):
        """清理過期數據"""
        cutoff = datetime.now() - self.retention
        self.metrics[metric_name] = [
            p for p in self.metrics[metric_name]
            if p.timestamp > cutoff
        ]

    def get_stats(self, metric_name: str) -> Dict[str, Any]:
        """
        獲取指標統計信息

        Args:
            metric_name: 指標名稱

        Returns:
            統計信息
        """
        with self._lock:
            points = self.metrics.get(metric_name, [])

            if not points:
                return {"count": 0}

            values = [p.value for p in points]

            return {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "avg": statistics.mean(values),
                "median": statistics.median(values),
                "stddev": statistics.stdev(values) if len(values) > 1 else 0,
                "latest": values[-1],
                "timestamp": points[-1].timestamp.isoformat()
            }

    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """獲取所有指標統計"""
        return {name: self.get_stats(name) for name in self.metrics.keys()}


# ============================================================
# 請求追蹤
# ============================================================

@dataclass
class RequestTrace:
    """請求追蹤記錄"""
    request_id: str
    user: str
    query: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "pending"
    tokens_used: int = 0
    latency_ms: float = 0
    error: Optional[str] = None


class RequestTracker:
    """
    請求追蹤器

    追蹤和記錄 API 請求
    """

    def __init__(self, max_traces: int = 1000):
        self.traces: Dict[str, RequestTrace] = {}
        self.max_traces = max_traces
        self._lock = Lock()
        self._counter = 0

    def start_trace(self, user: str, query: str) -> str:
        """
        開始追蹤

        Args:
            user: 用戶標識
            query: 查詢內容

        Returns:
            請求 ID
        """
        with self._lock:
            self._counter += 1
            request_id = f"req_{self._counter}_{int(time.time())}"

            trace = RequestTrace(
                request_id=request_id,
                user=user,
                query=query,
                start_time=datetime.now()
            )

            self.traces[request_id] = trace

            # 清理舊追蹤
            if len(self.traces) > self.max_traces:
                oldest_key = min(self.traces.keys())
                del self.traces[oldest_key]

            return request_id

    def end_trace(
        self,
        request_id: str,
        status: str = "success",
        tokens_used: int = 0,
        error: Optional[str] = None
    ):
        """
        結束追蹤

        Args:
            request_id: 請求 ID
            status: 狀態
            tokens_used: 使用的 token 數
            error: 錯誤信息
        """
        with self._lock:
            if request_id in self.traces:
                trace = self.traces[request_id]
                trace.end_time = datetime.now()
                trace.status = status
                trace.tokens_used = tokens_used
                trace.error = error
                trace.latency_ms = (
                    trace.end_time - trace.start_time
                ).total_seconds() * 1000

    def get_recent_traces(self, limit: int = 10) -> List[Dict[str, Any]]:
        """獲取最近的追蹤記錄"""
        with self._lock:
            sorted_traces = sorted(
                self.traces.values(),
                key=lambda x: x.start_time,
                reverse=True
            )[:limit]

            return [
                {
                    "request_id": t.request_id,
                    "user": t.user,
                    "query": t.query[:50] + "..." if len(t.query) > 50 else t.query,
                    "status": t.status,
                    "latency_ms": round(t.latency_ms, 2),
                    "tokens_used": t.tokens_used,
                    "timestamp": t.start_time.isoformat()
                }
                for t in sorted_traces
            ]


# ============================================================
# 告警系統
# ============================================================

@dataclass
class AlertRule:
    """告警規則"""
    name: str
    metric: str
    condition: str  # gt, lt, eq
    threshold: float
    severity: str = "warning"  # info, warning, critical
    cooldown_minutes: int = 5


class AlertManager:
    """
    告警管理器

    管理告警規則和發送告警
    """

    def __init__(self):
        self.rules: Dict[str, AlertRule] = {}
        self.last_alert_time: Dict[str, datetime] = {}
        self.alert_handlers: List[Callable[[Dict[str, Any]], None]] = []

    def add_rule(self, rule: AlertRule):
        """添加告警規則"""
        self.rules[rule.name] = rule

    def add_handler(self, handler: Callable[[Dict[str, Any]], None]):
        """添加告警處理器"""
        self.alert_handlers.append(handler)

    def check_and_alert(
        self,
        metric_name: str,
        value: float,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        檢查並觸發告警

        Args:
            metric_name: 指標名稱
            value: 指標值
            context: 上下文信息
        """
        for rule_name, rule in self.rules.items():
            if rule.metric != metric_name:
                continue

            # 檢查冷卻時間
            last_time = self.last_alert_time.get(rule_name)
            if last_time:
                if datetime.now() - last_time < timedelta(minutes=rule.cooldown_minutes):
                    continue

            # 檢查條件
            triggered = False
            if rule.condition == "gt" and value > rule.threshold:
                triggered = True
            elif rule.condition == "lt" and value < rule.threshold:
                triggered = True
            elif rule.condition == "eq" and value == rule.threshold:
                triggered = True

            if triggered:
                self._fire_alert(rule, value, context)
                self.last_alert_time[rule_name] = datetime.now()

    def _fire_alert(
        self,
        rule: AlertRule,
        value: float,
        context: Optional[Dict[str, Any]]
    ):
        """觸發告警"""
        alert = {
            "rule_name": rule.name,
            "metric": rule.metric,
            "value": value,
            "threshold": rule.threshold,
            "severity": rule.severity,
            "timestamp": datetime.now().isoformat(),
            "context": context or {}
        }

        logger.warning(f"Alert triggered: {rule.name} - {rule.metric}={value}")

        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Alert handler error: {e}")


# ============================================================
# 監控服務
# ============================================================

class DifyMonitorService:
    """
    Dify 監控服務

    整合所有監控功能的服務類
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.dify.ai/v1"
    ):
        self.health_checker = HealthChecker(base_url, api_key)
        self.metrics = MetricsCollector()
        self.tracker = RequestTracker()
        self.alerts = AlertManager()

        self._running = False
        self._monitor_thread = None

        # 設置默認告警規則
        self._setup_default_alerts()

    def _setup_default_alerts(self):
        """設置默認告警規則"""
        self.alerts.add_rule(AlertRule(
            name="high_latency",
            metric="api_latency",
            condition="gt",
            threshold=5000,  # 5 秒
            severity="warning"
        ))

        self.alerts.add_rule(AlertRule(
            name="high_error_rate",
            metric="error_rate",
            condition="gt",
            threshold=0.1,  # 10%
            severity="critical"
        ))

        # 添加日誌告警處理器
        self.alerts.add_handler(
            lambda alert: logger.warning(f"ALERT: {json.dumps(alert)}")
        )

    def start_monitoring(self, interval_seconds: int = 60):
        """
        開始監控

        Args:
            interval_seconds: 監控間隔（秒）
        """
        self._running = True
        self._monitor_thread = Thread(
            target=self._monitor_loop,
            args=(interval_seconds,)
        )
        self._monitor_thread.daemon = True
        self._monitor_thread.start()
        logger.info("Monitoring started")

    def stop_monitoring(self):
        """停止監控"""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join()
        logger.info("Monitoring stopped")

    def _monitor_loop(self, interval: int):
        """監控循環"""
        while self._running:
            try:
                # 執行健康檢查
                health = self.health_checker.check_api_health()

                if health['status'] == 'healthy':
                    self.metrics.record('api_latency', health['latency_ms'])
                else:
                    self.metrics.record('health_check_failures', 1)

                # 檢查告警
                self.alerts.check_and_alert(
                    'api_latency',
                    health.get('latency_ms', 0)
                )

            except Exception as e:
                logger.error(f"Monitor error: {e}")

            time.sleep(interval)

    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        獲取儀表板數據

        Returns:
            儀表板數據
        """
        return {
            "health": self.health_checker.check_api_health(),
            "metrics": self.metrics.get_all_stats(),
            "recent_requests": self.tracker.get_recent_traces(5),
            "timestamp": datetime.now().isoformat()
        }


# ============================================================
# 使用範例
# ============================================================

def example_health_check():
    """
    範例 1: 健康檢查

    展示如何進行健康檢查
    """
    print("=" * 50)
    print("範例 1: 健康檢查")
    print("=" * 50)

    checker = HealthChecker(
        base_url=DIFY_BASE_URL,
        api_key=DIFY_API_KEY
    )

    # API 健康檢查
    print("檢查 API 健康狀態...")
    health = checker.check_api_health()
    print(f"  狀態: {health['status']}")
    if 'latency_ms' in health:
        print(f"  延遲: {health['latency_ms']} ms")
    if 'error' in health:
        print(f"  錯誤: {health['error']}")


def example_metrics_collection():
    """
    範例 2: 指標收集

    展示如何收集和查看指標
    """
    print("\n" + "=" * 50)
    print("範例 2: 指標收集")
    print("=" * 50)

    collector = MetricsCollector()

    # 模擬記錄指標
    for i in range(10):
        collector.record("api_latency", 100 + i * 10)
        collector.record("tokens_used", 500 + i * 50)

    # 查看統計
    print("API 延遲統計:")
    stats = collector.get_stats("api_latency")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\nToken 使用統計:")
    stats = collector.get_stats("tokens_used")
    for key, value in stats.items():
        print(f"  {key}: {value}")


def example_request_tracking():
    """
    範例 3: 請求追蹤

    展示如何追蹤請求
    """
    print("\n" + "=" * 50)
    print("範例 3: 請求追蹤")
    print("=" * 50)

    tracker = RequestTracker()

    # 模擬追蹤請求
    for i in range(5):
        request_id = tracker.start_trace(
            user=f"user-{i}",
            query=f"這是第 {i+1} 個測試查詢"
        )

        # 模擬處理延遲
        time.sleep(0.1)

        tracker.end_trace(
            request_id=request_id,
            status="success" if i % 2 == 0 else "error",
            tokens_used=100 + i * 20
        )

    # 查看追蹤記錄
    print("最近的請求:")
    for trace in tracker.get_recent_traces(5):
        print(f"  {trace['request_id']}: {trace['status']} ({trace['latency_ms']}ms)")


def example_alerting():
    """
    範例 4: 告警設置

    展示如何設置告警
    """
    print("\n" + "=" * 50)
    print("範例 4: 告警設置")
    print("=" * 50)

    alert_manager = AlertManager()

    # 添加告警規則
    alert_manager.add_rule(AlertRule(
        name="test_alert",
        metric="test_metric",
        condition="gt",
        threshold=100,
        severity="warning"
    ))

    # 添加告警處理器
    def alert_handler(alert: Dict[str, Any]):
        print(f"  [告警] {alert['rule_name']}: {alert['metric']}={alert['value']}")

    alert_manager.add_handler(alert_handler)

    # 測試告警
    print("測試告警觸發:")
    alert_manager.check_and_alert("test_metric", 50)  # 不觸發
    alert_manager.check_and_alert("test_metric", 150)  # 觸發


def example_monitoring_service():
    """
    範例 5: 監控服務

    展示完整的監控服務
    """
    print("\n" + "=" * 50)
    print("範例 5: 監控服務")
    print("=" * 50)

    service = DifyMonitorService(
        api_key=DIFY_API_KEY,
        base_url=DIFY_BASE_URL
    )

    # 獲取儀表板數據
    print("儀表板數據:")
    dashboard = service.get_dashboard_data()

    print(f"  健康狀態: {dashboard['health']['status']}")
    print(f"  時間戳: {dashboard['timestamp']}")


def example_docker_deployment():
    """
    範例 6: Docker 部署配置

    展示 Docker 部署的配置範例
    """
    print("\n" + "=" * 50)
    print("範例 6: Docker 部署配置")
    print("=" * 50)

    docker_compose = """
version: '3.8'

services:
  dify-api:
    image: langgenius/dify-api:latest
    restart: always
    environment:
      - MODE=api
      - LOG_LEVEL=INFO
      - SECRET_KEY=${SECRET_KEY}
      - CONSOLE_WEB_URL=${CONSOLE_WEB_URL}
      - CONSOLE_API_URL=${CONSOLE_API_URL}
    ports:
      - "5001:5001"
    depends_on:
      - db
      - redis
    volumes:
      - ./storage:/app/api/storage

  dify-worker:
    image: langgenius/dify-api:latest
    restart: always
    environment:
      - MODE=worker
      - LOG_LEVEL=INFO
    depends_on:
      - db
      - redis

  dify-web:
    image: langgenius/dify-web:latest
    restart: always
    ports:
      - "3000:3000"

  db:
    image: postgres:15-alpine
    restart: always
    environment:
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=dify
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    restart: always
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
"""

    print("Docker Compose 配置範例:")
    print(docker_compose[:500] + "...")


def example_logging_setup():
    """
    範例 7: 日誌配置

    展示如何配置日誌
    """
    print("\n" + "=" * 50)
    print("範例 7: 日誌配置")
    print("=" * 50)

    # 創建專用 logger
    app_logger = logging.getLogger("dify_app")
    app_logger.setLevel(logging.DEBUG)

    # 添加文件處理器
    file_handler = logging.FileHandler("dify_app.log")
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)

    app_logger.addHandler(file_handler)

    # 記錄日誌
    print("日誌配置完成，寫入測試日誌:")
    app_logger.info("這是一條信息日誌")
    app_logger.warning("這是一條警告日誌")
    app_logger.error("這是一條錯誤日誌")

    print("  - INFO: 這是一條信息日誌")
    print("  - WARNING: 這是一條警告日誌")
    print("  - ERROR: 這是一條錯誤日誌")


# ============================================================
# 主程序
# ============================================================

if __name__ == "__main__":
    print("Dify 部署與監控範例")
    print("請確保已設置相關環境變數")
    print()

    example_health_check()
    example_metrics_collection()
    example_request_tracking()
    example_alerting()
    example_monitoring_service()
    example_docker_deployment()
    example_logging_setup()

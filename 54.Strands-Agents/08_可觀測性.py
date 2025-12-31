"""
Strands Agents 可觀測性示例

這個示例展示了如何為 Strands Agents 實現完整的可觀測性：
1. OpenTelemetry 整合
2. 分布式追蹤（Tracing）
3. 指標收集（Metrics）
4. 結構化日誌（Logging）
5. 自定義儀器化
6. 性能監控
7. 錯誤追蹤
8. 可視化和告警

可觀測性是生產環境中不可或缺的能力，
幫助我們理解系統行為、診斷問題和優化性能。

作者: Strands Agents Team
日期: 2025-01
"""

import os
import sys
import json
import time
import logging
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from functools import wraps
from contextlib import contextmanager
import traceback

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# OpenTelemetry 模擬實現
# ============================================================================

class Span:
    """
    追蹤 Span

    表示一個操作的時間段
    """

    def __init__(
        self,
        name: str,
        parent: Optional['Span'] = None,
        attributes: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.parent = parent
        self.span_id = self._generate_id()
        self.trace_id = parent.trace_id if parent else self._generate_id()
        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self.attributes = attributes or {}
        self.events: List[Dict[str, Any]] = []
        self.status = "OK"

        logger.debug(f"創建 Span: {name} (trace_id={self.trace_id[:8]}...)")

    def _generate_id(self) -> str:
        """生成唯一 ID"""
        import uuid
        return str(uuid.uuid4())

    def set_attribute(self, key: str, value: Any):
        """設置屬性"""
        self.attributes[key] = value

    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """添加事件"""
        event = {
            "name": name,
            "timestamp": time.time(),
            "attributes": attributes or {}
        }
        self.events.append(event)
        logger.debug(f"添加事件: {name}")

    def set_status(self, status: str, description: Optional[str] = None):
        """設置狀態"""
        self.status = status
        if description:
            self.attributes["status_description"] = description

    def end(self):
        """結束 Span"""
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        logger.info(f"Span 結束: {self.name} (duration={duration:.3f}s)")

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "name": self.name,
            "span_id": self.span_id,
            "trace_id": self.trace_id,
            "parent_span_id": self.parent.span_id if self.parent else None,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.end_time - self.start_time if self.end_time else None,
            "attributes": self.attributes,
            "events": self.events,
            "status": self.status
        }


class Tracer:
    """
    追蹤器

    創建和管理 Span
    """

    def __init__(self, name: str):
        self.name = name
        self.current_span: Optional[Span] = None
        self.spans: List[Span] = []

        logger.info(f"創建追蹤器: {name}")

    def start_span(
        self,
        name: str,
        attributes: Optional[Dict[str, Any]] = None
    ) -> Span:
        """開始新的 Span"""
        span = Span(
            name=name,
            parent=self.current_span,
            attributes=attributes
        )

        self.current_span = span
        self.spans.append(span)

        return span

    @contextmanager
    def start_as_current_span(
        self,
        name: str,
        attributes: Optional[Dict[str, Any]] = None
    ):
        """使用上下文管理器創建 Span"""
        span = self.start_span(name, attributes)

        try:
            yield span
        except Exception as e:
            span.set_status("ERROR", str(e))
            span.add_event("exception", {
                "exception.type": type(e).__name__,
                "exception.message": str(e),
                "exception.stacktrace": traceback.format_exc()
            })
            raise
        finally:
            span.end()
            self.current_span = span.parent

    def get_all_spans(self) -> List[Dict[str, Any]]:
        """獲取所有 Span"""
        return [span.to_dict() for span in self.spans]


# ============================================================================
# 指標收集
# ============================================================================

class Counter:
    """計數器"""

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.value = 0

    def increment(self, amount: int = 1, labels: Optional[Dict[str, str]] = None):
        """增加計數"""
        self.value += amount
        logger.debug(f"計數器 {self.name} 增加: {amount} (總計: {self.value})")

    def get_value(self) -> int:
        """獲取當前值"""
        return self.value


class Histogram:
    """直方圖"""

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.values: List[float] = []

    def record(self, value: float, labels: Optional[Dict[str, str]] = None):
        """記錄值"""
        self.values.append(value)
        logger.debug(f"直方圖 {self.name} 記錄: {value}")

    def get_statistics(self) -> Dict[str, float]:
        """獲取統計信息"""
        if not self.values:
            return {}

        sorted_values = sorted(self.values)
        count = len(sorted_values)

        return {
            "count": count,
            "sum": sum(sorted_values),
            "min": sorted_values[0],
            "max": sorted_values[-1],
            "mean": sum(sorted_values) / count,
            "p50": sorted_values[int(count * 0.5)],
            "p95": sorted_values[int(count * 0.95)],
            "p99": sorted_values[int(count * 0.99)]
        }


class Gauge:
    """測量儀"""

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.value = 0.0

    def set(self, value: float, labels: Optional[Dict[str, str]] = None):
        """設置值"""
        self.value = value
        logger.debug(f"測量儀 {self.name} 設置: {value}")

    def get_value(self) -> float:
        """獲取當前值"""
        return self.value


class MetricsCollector:
    """
    指標收集器

    管理所有指標
    """

    def __init__(self):
        self.counters: Dict[str, Counter] = {}
        self.histograms: Dict[str, Histogram] = {}
        self.gauges: Dict[str, Gauge] = {}

        logger.info("初始化指標收集器")

    def create_counter(self, name: str, description: str = "") -> Counter:
        """創建計數器"""
        counter = Counter(name, description)
        self.counters[name] = counter
        return counter

    def create_histogram(self, name: str, description: str = "") -> Histogram:
        """創建直方圖"""
        histogram = Histogram(name, description)
        self.histograms[name] = histogram
        return histogram

    def create_gauge(self, name: str, description: str = "") -> Gauge:
        """創建測量儀"""
        gauge = Gauge(name, description)
        self.gauges[name] = gauge
        return gauge

    def get_all_metrics(self) -> Dict[str, Any]:
        """獲取所有指標"""
        return {
            "counters": {
                name: counter.get_value()
                for name, counter in self.counters.items()
            },
            "histograms": {
                name: histogram.get_statistics()
                for name, histogram in self.histograms.items()
            },
            "gauges": {
                name: gauge.get_value()
                for name, gauge in self.gauges.items()
            }
        }


# ============================================================================
# 結構化日誌
# ============================================================================

class StructuredLogger:
    """
    結構化日誌記錄器

    以 JSON 格式記錄日誌，便於解析和查詢
    """

    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(name)

    def log(
        self,
        level: str,
        message: str,
        extra: Optional[Dict[str, Any]] = None
    ):
        """
        記錄日誌

        Args:
            level: 日誌級別
            message: 消息
            extra: 額外信息
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "logger": self.name,
            "message": message,
            "extra": extra or {}
        }

        log_json = json.dumps(log_entry, ensure_ascii=False)

        if level == "DEBUG":
            self.logger.debug(log_json)
        elif level == "INFO":
            self.logger.info(log_json)
        elif level == "WARNING":
            self.logger.warning(log_json)
        elif level == "ERROR":
            self.logger.error(log_json)
        elif level == "CRITICAL":
            self.logger.critical(log_json)

    def debug(self, message: str, **kwargs):
        """記錄 DEBUG 日誌"""
        self.log("DEBUG", message, kwargs)

    def info(self, message: str, **kwargs):
        """記錄 INFO 日誌"""
        self.log("INFO", message, kwargs)

    def warning(self, message: str, **kwargs):
        """記錄 WARNING 日誌"""
        self.log("WARNING", message, kwargs)

    def error(self, message: str, **kwargs):
        """記錄 ERROR 日誌"""
        self.log("ERROR", message, kwargs)


# ============================================================================
# 可觀測性裝飾器
# ============================================================================

class ObservabilityDecorator:
    """
    可觀測性裝飾器

    為函數添加追蹤和指標
    """

    def __init__(
        self,
        tracer: Tracer,
        metrics: MetricsCollector
    ):
        self.tracer = tracer
        self.metrics = metrics

    def trace(
        self,
        span_name: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None
    ):
        """
        追蹤裝飾器

        為函數添加分布式追蹤
        """
        def decorator(func: Callable) -> Callable:
            name = span_name or func.__name__

            @wraps(func)
            def wrapper(*args, **kwargs):
                with self.tracer.start_as_current_span(
                    name,
                    attributes=attributes
                ) as span:
                    # 添加函數信息
                    span.set_attribute("function.name", func.__name__)
                    span.set_attribute("function.module", func.__module__)

                    # 執行函數
                    result = func(*args, **kwargs)

                    return result

            return wrapper

        return decorator

    def measure_duration(
        self,
        metric_name: Optional[str] = None
    ):
        """
        測量持續時間裝飾器

        記錄函數執行時間
        """
        def decorator(func: Callable) -> Callable:
            name = metric_name or f"{func.__name__}_duration"

            # 創建直方圖
            histogram = self.metrics.create_histogram(
                name,
                f"{func.__name__} 執行時間"
            )

            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()

                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    duration = time.time() - start_time
                    histogram.record(duration)

            return wrapper

        return decorator

    def count_calls(
        self,
        counter_name: Optional[str] = None
    ):
        """
        計數調用裝飾器

        統計函數調用次數
        """
        def decorator(func: Callable) -> Callable:
            name = counter_name or f"{func.__name__}_calls"

            # 創建計數器
            counter = self.metrics.create_counter(
                name,
                f"{func.__name__} 調用次數"
            )

            @wraps(func)
            def wrapper(*args, **kwargs):
                counter.increment()
                return func(*args, **kwargs)

            return wrapper

        return decorator


# ============================================================================
# Agent 可觀測性
# ============================================================================

class ObservableAgent:
    """
    可觀測的 Agent

    整合了完整的可觀測性功能
    """

    def __init__(
        self,
        name: str,
        tracer: Tracer,
        metrics: MetricsCollector,
        logger: StructuredLogger
    ):
        self.name = name
        self.tracer = tracer
        self.metrics = metrics
        self.logger = logger

        # 創建指標
        self.request_counter = metrics.create_counter(
            f"agent_{name}_requests",
            "Agent 請求總數"
        )

        self.error_counter = metrics.create_counter(
            f"agent_{name}_errors",
            "Agent 錯誤總數"
        )

        self.latency_histogram = metrics.create_histogram(
            f"agent_{name}_latency",
            "Agent 響應延遲"
        )

        self.active_requests = metrics.create_gauge(
            f"agent_{name}_active_requests",
            "當前活躍請求數"
        )

        logger.info("初始化可觀測 Agent", agent_name=name)

    def process(self, message: str, session_id: Optional[str] = None) -> str:
        """
        處理消息（含完整可觀測性）

        Args:
            message: 用戶消息
            session_id: 會話 ID

        Returns:
            str: 響應
        """
        # 增加計數器
        self.request_counter.increment()
        self.active_requests.set(self.active_requests.get_value() + 1)

        start_time = time.time()

        # 開始追蹤
        with self.tracer.start_as_current_span(
            "agent.process",
            attributes={
                "agent.name": self.name,
                "message.length": len(message),
                "session.id": session_id or "none"
            }
        ) as span:
            try:
                # 記錄開始日誌
                self.logger.info(
                    "處理請求",
                    agent=self.name,
                    message_length=len(message),
                    session_id=session_id
                )

                # 模擬處理
                response = self._execute_processing(message, session_id, span)

                # 記錄成功
                span.add_event("processing_completed")

                return response

            except Exception as e:
                # 增加錯誤計數
                self.error_counter.increment()

                # 記錄錯誤
                self.logger.error(
                    "處理失敗",
                    agent=self.name,
                    error=str(e),
                    error_type=type(e).__name__
                )

                # 在 span 中記錄錯誤
                span.set_status("ERROR", str(e))

                raise

            finally:
                # 記錄延遲
                latency = time.time() - start_time
                self.latency_histogram.record(latency)

                # 更新活躍請求數
                self.active_requests.set(self.active_requests.get_value() - 1)

                # 記錄完成日誌
                self.logger.info(
                    "請求完成",
                    agent=self.name,
                    latency=latency
                )

    def _execute_processing(
        self,
        message: str,
        session_id: Optional[str],
        parent_span: Span
    ) -> str:
        """
        執行處理（內部方法）

        Args:
            message: 消息
            session_id: 會話 ID
            parent_span: 父 Span

        Returns:
            str: 響應
        """
        # 創建子 Span
        with self.tracer.start_as_current_span("agent.understand") as span:
            span.add_event("analyzing_message")

            # 模擬理解消息
            time.sleep(0.1)

        with self.tracer.start_as_current_span("agent.generate") as span:
            span.add_event("generating_response")

            # 模擬生成響應
            time.sleep(0.2)

            response = f"這是對 '{message}' 的響應"

        return response


# ============================================================================
# 監控儀表板
# ============================================================================

class MonitoringDashboard:
    """
    監控儀表板

    展示可觀測性數據
    """

    def __init__(
        self,
        tracer: Tracer,
        metrics: MetricsCollector
    ):
        self.tracer = tracer
        self.metrics = metrics

    def generate_report(self) -> Dict[str, Any]:
        """
        生成監控報告

        Returns:
            Dict: 報告數據
        """
        # 獲取追蹤數據
        spans = self.tracer.get_all_spans()

        # 計算追蹤統計
        trace_stats = self._calculate_trace_stats(spans)

        # 獲取指標
        metrics = self.metrics.get_all_metrics()

        report = {
            "timestamp": datetime.now().isoformat(),
            "traces": {
                "total_spans": len(spans),
                "statistics": trace_stats
            },
            "metrics": metrics
        }

        return report

    def _calculate_trace_stats(self, spans: List[Dict[str, Any]]) -> Dict[str, Any]:
        """計算追蹤統計"""
        if not spans:
            return {}

        durations = [
            span["duration"] for span in spans
            if span["duration"] is not None
        ]

        if not durations:
            return {}

        return {
            "total_duration": sum(durations),
            "average_duration": sum(durations) / len(durations),
            "min_duration": min(durations),
            "max_duration": max(durations)
        }

    def print_summary(self):
        """打印摘要"""
        report = self.generate_report()

        print("\n" + "="*60)
        print("監控報告")
        print("="*60)

        print(f"\n時間: {report['timestamp']}")

        print("\n追蹤統計:")
        trace_stats = report['traces']['statistics']
        if trace_stats:
            print(f"  總 Spans: {report['traces']['total_spans']}")
            print(f"  平均持續時間: {trace_stats.get('average_duration', 0):.3f}s")
            print(f"  最大持續時間: {trace_stats.get('max_duration', 0):.3f}s")

        print("\n指標統計:")
        for metric_type, metrics in report['metrics'].items():
            if metrics:
                print(f"\n  {metric_type.upper()}:")
                for name, value in metrics.items():
                    if isinstance(value, dict):
                        print(f"    {name}:")
                        for k, v in value.items():
                            print(f"      {k}: {v}")
                    else:
                        print(f"    {name}: {value}")


# ============================================================================
# 示例和測試
# ============================================================================

def demonstrate_tracing():
    """演示分布式追蹤"""
    print("\n" + "="*60)
    print("示例 1: 分布式追蹤")
    print("="*60 + "\n")

    tracer = Tracer("demo_tracer")

    # 創建追蹤
    with tracer.start_as_current_span("operation_1") as span1:
        span1.set_attribute("user_id", "user_001")
        span1.add_event("step_1_started")

        time.sleep(0.1)

        with tracer.start_as_current_span("operation_2") as span2:
            span2.set_attribute("action", "process_data")
            time.sleep(0.2)

        span1.add_event("step_1_completed")

    # 顯示追蹤結果
    spans = tracer.get_all_spans()
    print(f"生成了 {len(spans)} 個 Spans:\n")

    for span_data in spans:
        print(f"Span: {span_data['name']}")
        print(f"  Duration: {span_data['duration']:.3f}s")
        print(f"  Attributes: {span_data['attributes']}")
        print()


def demonstrate_metrics():
    """演示指標收集"""
    print("\n" + "="*60)
    print("示例 2: 指標收集")
    print("="*60 + "\n")

    metrics = MetricsCollector()

    # 創建指標
    request_counter = metrics.create_counter("requests", "請求數")
    latency_histogram = metrics.create_histogram("latency", "延遲")
    memory_gauge = metrics.create_gauge("memory", "內存使用")

    # 模擬記錄
    for i in range(10):
        request_counter.increment()
        latency_histogram.record(0.1 + i * 0.05)
        memory_gauge.set(100 + i * 10)

    # 顯示指標
    all_metrics = metrics.get_all_metrics()
    print("收集的指標:")
    print(json.dumps(all_metrics, indent=2, ensure_ascii=False))


def demonstrate_structured_logging():
    """演示結構化日誌"""
    print("\n" + "="*60)
    print("示例 3: 結構化日誌")
    print("="*60 + "\n")

    struct_logger = StructuredLogger("demo")

    # 記錄不同級別的日誌
    struct_logger.info("應用啟動", version="1.0.0", environment="production")
    struct_logger.debug("調試信息", data={"key": "value"})
    struct_logger.warning("警告訊息", threshold=100, current=120)


def demonstrate_observable_agent():
    """演示可觀測 Agent"""
    print("\n" + "="*60)
    print("示例 4: 可觀測 Agent")
    print("="*60 + "\n")

    # 初始化可觀測性組件
    tracer = Tracer("agent_tracer")
    metrics = MetricsCollector()
    struct_logger = StructuredLogger("agent")

    # 創建可觀測 Agent
    agent = ObservableAgent(
        name="demo_agent",
        tracer=tracer,
        metrics=metrics,
        logger=struct_logger
    )

    # 處理請求
    messages = [
        "你好",
        "介紹一下 Strands Agents",
        "如何部署到 Lambda？"
    ]

    for msg in messages:
        print(f"\n處理: {msg}")
        response = agent.process(msg, session_id="test_session")
        print(f"響應: {response}")

    # 顯示監控數據
    dashboard = MonitoringDashboard(tracer, metrics)
    dashboard.print_summary()


def main():
    """主函數"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*18 + "可觀測性示例" + " "*21 + "║")
    print("╚" + "="*58 + "╝")

    try:
        demonstrate_tracing()
        demonstrate_metrics()
        demonstrate_structured_logging()
        demonstrate_observable_agent()

        print("\n" + "="*60)
        print("所有示例執行完成！")
        print("="*60)

    except Exception as e:
        logger.error(f"執行錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

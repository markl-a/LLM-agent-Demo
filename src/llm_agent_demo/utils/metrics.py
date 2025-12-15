"""監控指標模組 - 提供系統和應用程式性能監控功能

這個模組提供了完整的監控解決方案，包括：
- 計數器 (Counter) - 追蹤累計值
- 計量器 (Gauge) - 追蹤當前值
- 直方圖 (Histogram) - 追蹤值的分佈
- API 調用追蹤
- 延遲測量裝飾器
- 多種格式導出 (JSON/Prometheus)

使用示例：
    >>> from llm_agent_demo.utils.metrics import MetricsCollector, track_latency
    >>> metrics = MetricsCollector()
    >>> metrics.counter("api_calls").inc()
    >>> metrics.gauge("active_users").set(42)
    >>>
    >>> @track_latency(metrics, "process_request")
    >>> def process_request():
    >>>     # 處理邏輯
    >>>     pass
"""

import json
import threading
import time
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, TypedDict, Union
from statistics import mean, median, stdev


class MetricDataDict(TypedDict):
    """指標數據字典"""

    name: str
    type: str
    value: Union[int, float, Dict[str, Any]]
    timestamp: str
    labels: Dict[str, str]


class HistogramBucket(TypedDict):
    """直方圖桶"""

    le: float
    count: int


class HistogramData(TypedDict):
    """直方圖數據"""

    sum: float
    count: int
    buckets: List[HistogramBucket]
    percentiles: Dict[str, float]


@dataclass
class Counter:
    """計數器 - 只能增加的指標

    適用於追蹤：
    - API 請求總數
    - 錯誤總數
    - 處理的任務總數

    屬性：
        name: 計數器名稱
        help_text: 說明文字
        labels: 標籤鍵值對
        _value: 當前值
        _lock: 線程鎖
    """

    name: str
    help_text: str = ""
    labels: Dict[str, str] = field(default_factory=dict)
    _value: float = field(default=0.0, init=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False)

    def inc(self, amount: float = 1.0) -> None:
        """增加計數器值

        參數：
            amount: 增加的數量，必須為正數

        異常：
            ValueError: 如果 amount 為負數
        """
        if amount < 0:
            raise ValueError("計數器只能增加，不能減少")
        with self._lock:
            self._value += amount

    def get(self) -> float:
        """獲取當前值"""
        with self._lock:
            return self._value

    def reset(self) -> None:
        """重置計數器為 0"""
        with self._lock:
            self._value = 0.0

    def to_dict(self) -> MetricDataDict:
        """轉換為字典格式"""
        return {
            "name": self.name,
            "type": "counter",
            "value": self.get(),
            "timestamp": datetime.utcnow().isoformat(),
            "labels": self.labels,
        }


@dataclass
class Gauge:
    """計量器 - 可增可減的指標

    適用於追蹤：
    - 當前活躍連接數
    - 內存使用量
    - 隊列長度
    - 溫度、CPU 使用率等

    屬性：
        name: 計量器名稱
        help_text: 說明文字
        labels: 標籤鍵值對
        _value: 當前值
        _lock: 線程鎖
    """

    name: str
    help_text: str = ""
    labels: Dict[str, str] = field(default_factory=dict)
    _value: float = field(default=0.0, init=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False)

    def set(self, value: float) -> None:
        """設置計量器值"""
        with self._lock:
            self._value = value

    def inc(self, amount: float = 1.0) -> None:
        """增加計量器值"""
        with self._lock:
            self._value += amount

    def dec(self, amount: float = 1.0) -> None:
        """減少計量器值"""
        with self._lock:
            self._value -= amount

    def get(self) -> float:
        """獲取當前值"""
        with self._lock:
            return self._value

    def set_to_current_time(self) -> None:
        """設置為當前時間戳"""
        self.set(time.time())

    def to_dict(self) -> MetricDataDict:
        """轉換為字典格式"""
        return {
            "name": self.name,
            "type": "gauge",
            "value": self.get(),
            "timestamp": datetime.utcnow().isoformat(),
            "labels": self.labels,
        }


@dataclass
class Histogram:
    """直方圖 - 追蹤值的分佈

    適用於追蹤：
    - 請求延遲
    - 響應大小
    - 處理時間

    屬性：
        name: 直方圖名稱
        help_text: 說明文字
        labels: 標籤鍵值對
        buckets: 桶的邊界值
        _observations: 觀測值列表
        _bucket_counts: 每個桶的計數
        _sum: 所有觀測值的總和
        _lock: 線程鎖
    """

    name: str
    help_text: str = ""
    labels: Dict[str, str] = field(default_factory=dict)
    buckets: List[float] = field(
        default_factory=lambda: [0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0]
    )
    _observations: List[float] = field(default_factory=list, init=False)
    _bucket_counts: Dict[float, int] = field(default_factory=dict, init=False)
    _sum: float = field(default=0.0, init=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False)

    def __post_init__(self):
        """初始化桶計數"""
        self._bucket_counts = {b: 0 for b in self.buckets}

    def observe(self, value: float) -> None:
        """記錄一個觀測值

        參數：
            value: 觀測值
        """
        with self._lock:
            self._observations.append(value)
            self._sum += value

            # 更新桶計數
            for bucket in self.buckets:
                if value <= bucket:
                    self._bucket_counts[bucket] += 1

    def get_sum(self) -> float:
        """獲取所有觀測值的總和"""
        with self._lock:
            return self._sum

    def get_count(self) -> int:
        """獲取觀測值數量"""
        with self._lock:
            return len(self._observations)

    def get_buckets(self) -> List[HistogramBucket]:
        """獲取桶數據"""
        with self._lock:
            return [{"le": bucket, "count": count} for bucket, count in sorted(self._bucket_counts.items())]

    def get_percentile(self, percentile: float) -> Optional[float]:
        """計算百分位數

        參數：
            percentile: 百分位 (0-100)

        返回：
            百分位值，如果沒有數據則返回 None
        """
        with self._lock:
            if not self._observations:
                return None
            sorted_obs = sorted(self._observations)
            index = int(len(sorted_obs) * percentile / 100.0)
            return sorted_obs[min(index, len(sorted_obs) - 1)]

    def get_statistics(self) -> Dict[str, Optional[float]]:
        """獲取統計信息"""
        with self._lock:
            if not self._observations:
                return {
                    "count": 0,
                    "sum": 0.0,
                    "mean": None,
                    "median": None,
                    "std_dev": None,
                    "min": None,
                    "max": None,
                }

            return {
                "count": len(self._observations),
                "sum": self._sum,
                "mean": mean(self._observations),
                "median": median(self._observations),
                "std_dev": stdev(self._observations) if len(self._observations) > 1 else 0.0,
                "min": min(self._observations),
                "max": max(self._observations),
            }

    def to_dict(self) -> MetricDataDict:
        """轉換為字典格式"""
        percentiles = {
            "p50": self.get_percentile(50),
            "p90": self.get_percentile(90),
            "p95": self.get_percentile(95),
            "p99": self.get_percentile(99),
        }

        histogram_data: HistogramData = {
            "sum": self.get_sum(),
            "count": self.get_count(),
            "buckets": self.get_buckets(),
            "percentiles": percentiles,  # type: ignore
        }

        return {
            "name": self.name,
            "type": "histogram",
            "value": histogram_data,
            "timestamp": datetime.utcnow().isoformat(),
            "labels": self.labels,
        }


class MetricsCollector:
    """指標收集器 - 管理所有指標

    這是主要的指標管理類，提供：
    - 創建和獲取各類指標
    - 指標導出
    - API 調用追蹤

    屬性：
        _metrics: 存儲所有指標
        _lock: 線程鎖
        _api_tracker: API 調用追蹤器
    """

    def __init__(self):
        """初始化指標收集器"""
        self._metrics: Dict[str, Union[Counter, Gauge, Histogram]] = {}
        self._lock = threading.Lock()
        self._api_tracker = APICallTracker()

    def counter(self, name: str, help_text: str = "", labels: Optional[Dict[str, str]] = None) -> Counter:
        """獲取或創建計數器

        參數：
            name: 計數器名稱
            help_text: 說明文字
            labels: 標籤

        返回：
            Counter 實例
        """
        key = self._get_metric_key(name, labels or {})
        with self._lock:
            if key not in self._metrics:
                self._metrics[key] = Counter(name=name, help_text=help_text, labels=labels or {})
            metric = self._metrics[key]
            if not isinstance(metric, Counter):
                raise TypeError(f"指標 {name} 已存在但類型不是 Counter")
            return metric

    def gauge(self, name: str, help_text: str = "", labels: Optional[Dict[str, str]] = None) -> Gauge:
        """獲取或創建計量器

        參數：
            name: 計量器名稱
            help_text: 說明文字
            labels: 標籤

        返回：
            Gauge 實例
        """
        key = self._get_metric_key(name, labels or {})
        with self._lock:
            if key not in self._metrics:
                self._metrics[key] = Gauge(name=name, help_text=help_text, labels=labels or {})
            metric = self._metrics[key]
            if not isinstance(metric, Gauge):
                raise TypeError(f"指標 {name} 已存在但類型不是 Gauge")
            return metric

    def histogram(
        self,
        name: str,
        help_text: str = "",
        labels: Optional[Dict[str, str]] = None,
        buckets: Optional[List[float]] = None,
    ) -> Histogram:
        """獲取或創建直方圖

        參數：
            name: 直方圖名稱
            help_text: 說明文字
            labels: 標籤
            buckets: 桶的邊界值

        返回：
            Histogram 實例
        """
        key = self._get_metric_key(name, labels or {})
        with self._lock:
            if key not in self._metrics:
                kwargs = {"name": name, "help_text": help_text, "labels": labels or {}}
                if buckets:
                    kwargs["buckets"] = buckets
                self._metrics[key] = Histogram(**kwargs)
            metric = self._metrics[key]
            if not isinstance(metric, Histogram):
                raise TypeError(f"指標 {name} 已存在但類型不是 Histogram")
            return metric

    @staticmethod
    def _get_metric_key(name: str, labels: Dict[str, str]) -> str:
        """生成指標唯一鍵"""
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}:{label_str}" if label_str else name

    def get_all_metrics(self) -> List[MetricDataDict]:
        """獲取所有指標數據"""
        with self._lock:
            return [metric.to_dict() for metric in self._metrics.values()]

    def export_json(self, include_api_calls: bool = True) -> str:
        """導出為 JSON 格式

        參數：
            include_api_calls: 是否包含 API 調用數據

        返回：
            JSON 字符串
        """
        data = {
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": self.get_all_metrics(),
        }

        if include_api_calls:
            data["api_calls"] = self._api_tracker.get_summary()

        return json.dumps(data, indent=2, ensure_ascii=False)

    def export_prometheus(self) -> str:
        """導出為 Prometheus 格式

        返回：
            Prometheus 文本格式的指標
        """
        lines = []
        with self._lock:
            for metric in self._metrics.values():
                metric_dict = metric.to_dict()
                name = metric_dict["name"]
                metric_type = metric_dict["type"]
                labels = metric_dict["labels"]

                # 添加類型和幫助信息
                if isinstance(metric, (Counter, Gauge)):
                    help_text = metric.help_text or f"{metric_type.capitalize()} metric"
                    lines.append(f"# HELP {name} {help_text}")
                    lines.append(f"# TYPE {name} {metric_type}")

                    # 格式化標籤
                    label_str = ""
                    if labels:
                        label_pairs = [f'{k}="{v}"' for k, v in labels.items()]
                        label_str = "{" + ",".join(label_pairs) + "}"

                    lines.append(f"{name}{label_str} {metric_dict['value']}")

                elif isinstance(metric, Histogram):
                    help_text = metric.help_text or "Histogram metric"
                    lines.append(f"# HELP {name} {help_text}")
                    lines.append(f"# TYPE {name} histogram")

                    # 格式化標籤
                    base_labels = labels.copy()
                    label_prefix = ""
                    if base_labels:
                        label_pairs = [f'{k}="{v}"' for k, v in base_labels.items()]
                        label_prefix = ",".join(label_pairs) + ","

                    # 輸出桶
                    histogram_value = metric_dict["value"]
                    if isinstance(histogram_value, dict):
                        for bucket in histogram_value.get("buckets", []):
                            le = bucket["le"]
                            count = bucket["count"]
                            lines.append(f'{name}_bucket{{{label_prefix}le="{le}"}} {count}')

                        # 輸出總和和計數
                        label_str = "{" + label_prefix.rstrip(",") + "}" if label_prefix else ""
                        lines.append(f"{name}_sum{label_str} {histogram_value.get('sum', 0)}")
                        lines.append(f"{name}_count{label_str} {histogram_value.get('count', 0)}")

                lines.append("")  # 空行分隔

        return "\n".join(lines)

    def save_to_file(
        self,
        file_path: Union[str, Path],
        format: Literal["json", "prometheus"] = "json",
        include_api_calls: bool = True,
    ) -> None:
        """保存指標到文件

        參數：
            file_path: 文件路徑
            format: 導出格式 ('json' 或 'prometheus')
            include_api_calls: 是否包含 API 調用數據（僅 JSON 格式）
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        if format == "json":
            content = self.export_json(include_api_calls=include_api_calls)
        elif format == "prometheus":
            content = self.export_prometheus()
        else:
            raise ValueError(f"不支持的格式: {format}")

        path.write_text(content, encoding="utf-8")

    def reset_all(self) -> None:
        """重置所有指標"""
        with self._lock:
            for metric in self._metrics.values():
                if isinstance(metric, Counter):
                    metric.reset()
                elif isinstance(metric, Gauge):
                    metric.set(0.0)
                elif isinstance(metric, Histogram):
                    metric._observations.clear()
                    metric._sum = 0.0
                    metric._bucket_counts = {b: 0 for b in metric.buckets}

    @property
    def api_tracker(self) -> "APICallTracker":
        """獲取 API 調用追蹤器"""
        return self._api_tracker


@dataclass
class APICall:
    """API 調用記錄

    屬性：
        endpoint: API 端點
        method: HTTP 方法
        status_code: 狀態碼
        latency: 延遲（秒）
        timestamp: 時間戳
        error: 錯誤信息（如果有）
        metadata: 額外的元數據
    """

    endpoint: str
    method: str
    status_code: int
    latency: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "endpoint": self.endpoint,
            "method": self.method,
            "status_code": self.status_code,
            "latency": self.latency,
            "timestamp": self.timestamp.isoformat(),
            "error": self.error,
            "metadata": self.metadata,
        }


class APICallTracker:
    """API 調用追蹤器

    追蹤和分析 API 調用的性能和錯誤情況
    """

    def __init__(self, max_history: int = 1000):
        """初始化 API 調用追蹤器

        參數：
            max_history: 保留的最大歷史記錄數
        """
        self._calls: List[APICall] = []
        self._lock = threading.Lock()
        self._max_history = max_history

    def track(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        latency: float,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """記錄一次 API 調用

        參數：
            endpoint: API 端點
            method: HTTP 方法
            status_code: 狀態碼
            latency: 延遲（秒）
            error: 錯誤信息
            metadata: 額外的元數據
        """
        call = APICall(
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            latency=latency,
            error=error,
            metadata=metadata or {},
        )

        with self._lock:
            self._calls.append(call)
            # 保持歷史記錄在限制內
            if len(self._calls) > self._max_history:
                self._calls = self._calls[-self._max_history :]

    @contextmanager
    def track_call(
        self,
        endpoint: str,
        method: str = "GET",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """上下文管理器：自動追蹤 API 調用

        參數：
            endpoint: API 端點
            method: HTTP 方法
            metadata: 額外的元數據

        使用示例：
            >>> tracker = APICallTracker()
            >>> with tracker.track_call("/api/users", "GET") as call_context:
            >>>     # 執行 API 調用
            >>>     response = requests.get("...")
            >>>     call_context["status_code"] = response.status_code
        """
        start_time = time.time()
        call_context: Dict[str, Any] = {"status_code": 200, "error": None}

        try:
            yield call_context
        except Exception as e:
            call_context["status_code"] = 500
            call_context["error"] = str(e)
            raise
        finally:
            latency = time.time() - start_time
            self.track(
                endpoint=endpoint,
                method=method,
                status_code=call_context.get("status_code", 500),
                latency=latency,
                error=call_context.get("error"),
                metadata=metadata,
            )

    def get_summary(self) -> Dict[str, Any]:
        """獲取 API 調用摘要

        返回：
            包含統計信息的字典
        """
        with self._lock:
            if not self._calls:
                return {
                    "total_calls": 0,
                    "total_errors": 0,
                    "avg_latency": 0.0,
                    "by_endpoint": {},
                    "by_status": {},
                }

            total_calls = len(self._calls)
            total_errors = sum(1 for call in self._calls if call.error or call.status_code >= 400)
            latencies = [call.latency for call in self._calls]

            # 按端點統計
            by_endpoint: Dict[str, Dict[str, Any]] = defaultdict(lambda: {"count": 0, "errors": 0, "latencies": []})
            for call in self._calls:
                endpoint_stats = by_endpoint[call.endpoint]
                endpoint_stats["count"] += 1
                endpoint_stats["latencies"].append(call.latency)
                if call.error or call.status_code >= 400:
                    endpoint_stats["errors"] += 1

            # 計算每個端點的平均延遲
            endpoint_summary = {}
            for endpoint, stats in by_endpoint.items():
                endpoint_summary[endpoint] = {
                    "count": stats["count"],
                    "errors": stats["errors"],
                    "avg_latency": mean(stats["latencies"]) if stats["latencies"] else 0.0,
                    "p95_latency": (
                        sorted(stats["latencies"])[int(len(stats["latencies"]) * 0.95)]
                        if stats["latencies"]
                        else 0.0
                    ),
                }

            # 按狀態碼統計
            by_status: Dict[int, int] = defaultdict(int)
            for call in self._calls:
                by_status[call.status_code] += 1

            return {
                "total_calls": total_calls,
                "total_errors": total_errors,
                "error_rate": total_errors / total_calls if total_calls > 0 else 0.0,
                "avg_latency": mean(latencies),
                "p50_latency": sorted(latencies)[int(len(latencies) * 0.5)],
                "p95_latency": sorted(latencies)[int(len(latencies) * 0.95)],
                "p99_latency": sorted(latencies)[int(len(latencies) * 0.99)],
                "by_endpoint": dict(endpoint_summary),
                "by_status": dict(by_status),
            }

    def get_recent_calls(self, limit: int = 10) -> List[Dict[str, Any]]:
        """獲取最近的 API 調用

        參數：
            limit: 返回的最大記錄數

        返回：
            API 調用列表
        """
        with self._lock:
            recent = self._calls[-limit:]
            return [call.to_dict() for call in reversed(recent)]

    def clear(self) -> None:
        """清除所有歷史記錄"""
        with self._lock:
            self._calls.clear()


# ============================================================================
# 裝飾器：延遲測量
# ============================================================================


def track_latency(
    metrics: MetricsCollector,
    metric_name: str,
    labels: Optional[Dict[str, str]] = None,
    use_histogram: bool = True,
) -> Callable:
    """延遲測量裝飾器

    自動測量函數執行時間並記錄到指標系統

    參數：
        metrics: 指標收集器實例
        metric_name: 指標名稱
        labels: 標籤
        use_histogram: 使用直方圖（True）或計量器（False）

    使用示例：
        >>> metrics = MetricsCollector()
        >>> @track_latency(metrics, "process_duration")
        >>> def process_data():
        >>>     time.sleep(1)
        >>>     return "done"
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                if use_histogram:
                    metrics.histogram(metric_name, labels=labels).observe(duration)
                else:
                    metrics.gauge(f"{metric_name}_seconds", labels=labels).set(duration)

        return wrapper

    return decorator


def track_api_call(
    tracker: APICallTracker,
    endpoint: str,
    method: str = "GET",
) -> Callable:
    """API 調用追蹤裝飾器

    自動追蹤函數作為 API 調用的性能

    參數：
        tracker: API 調用追蹤器
        endpoint: API 端點名稱
        method: HTTP 方法

    使用示例：
        >>> tracker = APICallTracker()
        >>> @track_api_call(tracker, "/api/users", "GET")
        >>> def get_users():
        >>>     # API 調用邏輯
        >>>     return users
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            error = None
            status_code = 200

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                error = str(e)
                status_code = 500
                raise
            finally:
                latency = time.time() - start_time
                tracker.track(
                    endpoint=endpoint,
                    method=method,
                    status_code=status_code,
                    latency=latency,
                    error=error,
                )

        return wrapper

    return decorator


# ============================================================================
# 全局指標收集器實例
# ============================================================================

_global_metrics: Optional[MetricsCollector] = None
_global_metrics_lock = threading.Lock()


def get_metrics_collector() -> MetricsCollector:
    """獲取全局指標收集器實例

    這是獲取指標收集器的推薦方式，確保整個應用程式使用同一個實例

    返回：
        MetricsCollector 實例

    使用示例：
        >>> from llm_agent_demo.utils.metrics import get_metrics_collector
        >>> metrics = get_metrics_collector()
        >>> metrics.counter("requests_total").inc()
    """
    global _global_metrics

    if _global_metrics is None:
        with _global_metrics_lock:
            if _global_metrics is None:
                _global_metrics = MetricsCollector()

    return _global_metrics


# ============================================================================
# 便捷函數
# ============================================================================


def create_standard_metrics(metrics: Optional[MetricsCollector] = None) -> MetricsCollector:
    """創建標準的監控指標集

    包含常用的系統和應用程式指標

    參數：
        metrics: 現有的指標收集器，如果為 None 則創建新的

    返回：
        配置好的 MetricsCollector 實例
    """
    if metrics is None:
        metrics = MetricsCollector()

    # 計數器
    metrics.counter("requests_total", "總請求數")
    metrics.counter("errors_total", "總錯誤數")
    metrics.counter("llm_api_calls_total", "LLM API 調用總數")

    # 計量器
    metrics.gauge("active_connections", "當前活躍連接數")
    metrics.gauge("queue_size", "隊列大小")
    metrics.gauge("last_success_timestamp", "最後成功時間戳")

    # 直方圖
    metrics.histogram("request_duration_seconds", "請求處理時間")
    metrics.histogram("llm_api_latency_seconds", "LLM API 延遲")
    metrics.histogram("response_size_bytes", "響應大小", buckets=[100, 500, 1000, 5000, 10000, 50000, 100000])

    return metrics


__all__ = [
    "Counter",
    "Gauge",
    "Histogram",
    "MetricsCollector",
    "APICall",
    "APICallTracker",
    "track_latency",
    "track_api_call",
    "get_metrics_collector",
    "create_standard_metrics",
    "MetricDataDict",
    "HistogramBucket",
    "HistogramData",
]

"""監控指標模組測試

測試 metrics.py 模組的功能：
- Counter 計數器
- Gauge 計量器
- Histogram 直方圖
- MetricsCollector 指標收集器
- track_latency 裝飾器
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch

from llm_agent_demo.utils.metrics import (
    Counter,
    Gauge,
    Histogram,
    MetricsCollector,
    track_latency,
)


class TestCounter:
    """測試 Counter 計數器"""

    def test_create_counter(self):
        """測試創建計數器"""
        counter = Counter(name="test_counter", help_text="測試計數器")
        assert counter.name == "test_counter"
        assert counter.help_text == "測試計數器"
        assert counter.get() == 0.0

    def test_counter_increment(self):
        """測試計數器增加"""
        counter = Counter(name="test")
        counter.inc()
        assert counter.get() == 1.0

    def test_counter_increment_with_amount(self):
        """測試計數器增加指定數量"""
        counter = Counter(name="test")
        counter.inc(5.0)
        assert counter.get() == 5.0

    def test_counter_multiple_increments(self):
        """測試計數器多次增加"""
        counter = Counter(name="test")
        counter.inc(1.0)
        counter.inc(2.0)
        counter.inc(3.0)
        assert counter.get() == 6.0

    def test_counter_negative_increment_raises_error(self):
        """測試計數器負數增加拋出錯誤"""
        counter = Counter(name="test")
        with pytest.raises(ValueError, match="計數器只能增加"):
            counter.inc(-1.0)

    def test_counter_reset(self):
        """測試計數器重置"""
        counter = Counter(name="test")
        counter.inc(10.0)
        counter.reset()
        assert counter.get() == 0.0

    def test_counter_to_dict(self):
        """測試計數器轉換為字典"""
        counter = Counter(name="api_calls", help_text="API 調用次數")
        counter.inc(5.0)
        result = counter.to_dict()

        assert result["name"] == "api_calls"
        assert result["type"] == "counter"
        assert result["value"] == 5.0
        assert "timestamp" in result

    def test_counter_thread_safety(self):
        """測試計數器線程安全"""
        counter = Counter(name="test")
        threads = []

        def increment():
            for _ in range(100):
                counter.inc()

        for _ in range(10):
            t = threading.Thread(target=increment)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        assert counter.get() == 1000.0


class TestGauge:
    """測試 Gauge 計量器"""

    def test_create_gauge(self):
        """測試創建計量器"""
        gauge = Gauge(name="test_gauge", help_text="測試計量器")
        assert gauge.name == "test_gauge"
        assert gauge.help_text == "測試計量器"
        assert gauge.get() == 0.0

    def test_gauge_set(self):
        """測試設置計量器值"""
        gauge = Gauge(name="test")
        gauge.set(42.0)
        assert gauge.get() == 42.0

    def test_gauge_increment(self):
        """測試計量器增加"""
        gauge = Gauge(name="test")
        gauge.set(10.0)
        gauge.inc(5.0)
        assert gauge.get() == 15.0

    def test_gauge_decrement(self):
        """測試計量器減少"""
        gauge = Gauge(name="test")
        gauge.set(10.0)
        gauge.dec(3.0)
        assert gauge.get() == 7.0

    def test_gauge_can_be_negative(self):
        """測試計量器可以為負數"""
        gauge = Gauge(name="test")
        gauge.set(-10.0)
        assert gauge.get() == -10.0

    def test_gauge_to_dict(self):
        """測試計量器轉換為字典"""
        gauge = Gauge(name="active_users", help_text="活躍用戶數")
        gauge.set(100.0)
        result = gauge.to_dict()

        assert result["name"] == "active_users"
        assert result["type"] == "gauge"
        assert result["value"] == 100.0

    def test_gauge_thread_safety(self):
        """測試計量器線程安全"""
        gauge = Gauge(name="test")
        gauge.set(0.0)
        threads = []

        def modify():
            for _ in range(100):
                gauge.inc()
                gauge.dec()

        for _ in range(10):
            t = threading.Thread(target=modify)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # 增減相等，最終應該為 0
        assert gauge.get() == 0.0


class TestHistogram:
    """測試 Histogram 直方圖"""

    def test_create_histogram(self):
        """測試創建直方圖"""
        histogram = Histogram(name="test_histogram", help_text="測試直方圖")
        assert histogram.name == "test_histogram"
        assert histogram.help_text == "測試直方圖"

    def test_histogram_observe(self):
        """測試觀察值"""
        histogram = Histogram(name="test")
        histogram.observe(1.0)
        histogram.observe(2.0)
        histogram.observe(3.0)

        stats = histogram.get_stats()
        assert stats["count"] == 3
        assert stats["sum"] == 6.0

    def test_histogram_observe_multiple_values(self):
        """測試觀察多個值"""
        histogram = Histogram(name="test")
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        for v in values:
            histogram.observe(v)

        stats = histogram.get_stats()
        assert stats["count"] == 5
        assert stats["min"] == 1.0
        assert stats["max"] == 5.0
        assert stats["mean"] == 3.0

    def test_histogram_percentiles(self):
        """測試百分位數計算"""
        histogram = Histogram(name="test")
        # 觀察 1-100 的值
        for i in range(1, 101):
            histogram.observe(float(i))

        stats = histogram.get_stats()
        # p50 應該接近 50
        assert 45 <= stats["p50"] <= 55
        # p90 應該接近 90
        assert 85 <= stats["p90"] <= 95
        # p99 應該接近 99
        assert 95 <= stats["p99"] <= 100

    def test_histogram_to_dict(self):
        """測試直方圖轉換為字典"""
        histogram = Histogram(name="response_time", help_text="響應時間")
        histogram.observe(0.1)
        histogram.observe(0.2)
        result = histogram.to_dict()

        assert result["name"] == "response_time"
        assert result["type"] == "histogram"
        assert "value" in result


class TestMetricsCollector:
    """測試 MetricsCollector 指標收集器"""

    @pytest.fixture
    def collector(self):
        """創建 MetricsCollector 實例"""
        return MetricsCollector()

    def test_create_collector(self, collector):
        """測試創建收集器"""
        assert collector is not None

    def test_counter_method(self, collector):
        """測試 counter 方法"""
        counter = collector.counter("test_counter")
        assert isinstance(counter, Counter)
        assert counter.name == "test_counter"

    def test_counter_reuse(self, collector):
        """測試重複獲取相同計數器"""
        counter1 = collector.counter("test")
        counter2 = collector.counter("test")
        assert counter1 is counter2

    def test_gauge_method(self, collector):
        """測試 gauge 方法"""
        gauge = collector.gauge("test_gauge")
        assert isinstance(gauge, Gauge)
        assert gauge.name == "test_gauge"

    def test_histogram_method(self, collector):
        """測試 histogram 方法"""
        histogram = collector.histogram("test_histogram")
        assert isinstance(histogram, Histogram)
        assert histogram.name == "test_histogram"

    def test_collect_all_metrics(self, collector):
        """測試收集所有指標"""
        # 創建一些指標
        collector.counter("requests").inc(10)
        collector.gauge("active").set(5)
        collector.histogram("latency").observe(0.1)

        metrics = collector.collect()

        assert len(metrics) >= 3

    def test_export_json(self, collector):
        """測試導出 JSON 格式"""
        collector.counter("test").inc()

        json_output = collector.export_json()

        assert isinstance(json_output, str)
        assert "test" in json_output

    def test_export_prometheus(self, collector):
        """測試導出 Prometheus 格式"""
        collector.counter("http_requests_total").inc(100)

        prom_output = collector.export_prometheus()

        assert isinstance(prom_output, str)
        assert "http_requests_total" in prom_output

    def test_reset_all(self, collector):
        """測試重置所有指標"""
        collector.counter("test").inc(10)
        collector.gauge("test2").set(20)

        collector.reset_all()

        assert collector.counter("test").get() == 0.0


class TestTrackLatency:
    """測試 track_latency 裝飾器"""

    def test_track_latency_decorator(self):
        """測試延遲追蹤裝飾器"""
        collector = MetricsCollector()

        @track_latency(collector, "test_function")
        def slow_function():
            time.sleep(0.01)
            return "done"

        result = slow_function()

        assert result == "done"

        # 檢查直方圖是否記錄了延遲
        histogram = collector.histogram("test_function")
        stats = histogram.get_stats()
        assert stats["count"] == 1
        assert stats["sum"] > 0.01  # 至少 10ms

    def test_track_latency_preserves_function_metadata(self):
        """測試裝飾器保留函數元數據"""
        collector = MetricsCollector()

        @track_latency(collector, "my_function")
        def documented_function():
            """這是一個有文檔的函數"""
            pass

        assert documented_function.__doc__ == "這是一個有文檔的函數"

    def test_track_latency_with_exception(self):
        """測試帶異常的延遲追蹤"""
        collector = MetricsCollector()

        @track_latency(collector, "error_function")
        def error_function():
            raise ValueError("測試錯誤")

        with pytest.raises(ValueError):
            error_function()

        # 即使拋出異常，也應該記錄延遲
        histogram = collector.histogram("error_function")
        stats = histogram.get_stats()
        assert stats["count"] == 1

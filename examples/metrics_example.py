"""監控指標模組使用示例

這個示例展示了如何使用 metrics 模組進行系統監控和性能追蹤
"""

import time
from pathlib import Path

from llm_agent_demo.utils.metrics import (
    MetricsCollector,
    get_metrics_collector,
    create_standard_metrics,
    track_latency,
    track_api_call,
)


def example_1_basic_metrics():
    """示例 1: 基礎指標使用"""
    print("=" * 60)
    print("示例 1: 基礎指標使用")
    print("=" * 60)

    # 創建指標收集器
    metrics = MetricsCollector()

    # 計數器：追蹤請求總數
    requests_counter = metrics.counter("http_requests_total", "HTTP 請求總數")
    requests_counter.inc()  # 增加 1
    requests_counter.inc(5)  # 增加 5
    print(f"總請求數: {requests_counter.get()}")

    # 計數器帶標籤：按狀態碼分類
    metrics.counter("http_requests_total", labels={"status": "200"}).inc(10)
    metrics.counter("http_requests_total", labels={"status": "404"}).inc(2)
    metrics.counter("http_requests_total", labels={"status": "500"}).inc(1)

    # 計量器：追蹤當前活躍連接數
    active_conn = metrics.gauge("active_connections", "當前活躍連接數")
    active_conn.set(42)  # 設置為 42
    active_conn.inc(10)  # 增加 10
    active_conn.dec(5)  # 減少 5
    print(f"活躍連接數: {active_conn.get()}")

    # 直方圖：追蹤請求延遲
    latency_hist = metrics.histogram("request_latency_seconds", "請求延遲分佈")
    latency_hist.observe(0.1)
    latency_hist.observe(0.25)
    latency_hist.observe(0.5)
    latency_hist.observe(1.2)
    latency_hist.observe(2.5)

    stats = latency_hist.get_statistics()
    print(f"\n延遲統計:")
    print(f"  平均值: {stats['mean']:.3f}s")
    print(f"  中位數: {stats['median']:.3f}s")
    print(f"  P95: {latency_hist.get_percentile(95):.3f}s")
    print(f"  P99: {latency_hist.get_percentile(99):.3f}s")


def example_2_decorators():
    """示例 2: 使用裝飾器自動追蹤"""
    print("\n" + "=" * 60)
    print("示例 2: 使用裝飾器自動追蹤")
    print("=" * 60)

    metrics = MetricsCollector()

    # 使用 track_latency 裝飾器自動測量執行時間
    @track_latency(metrics, "process_data_duration")
    def process_data(data_size: int):
        """模擬數據處理"""
        print(f"處理 {data_size} 條數據...")
        time.sleep(0.1)  # 模擬處理時間
        return f"已處理 {data_size} 條數據"

    # 執行幾次
    for size in [100, 200, 300]:
        result = process_data(size)
        print(result)

    # 查看統計
    hist = metrics.histogram("process_data_duration")
    stats = hist.get_statistics()
    print(f"\n處理時間統計:")
    print(f"  平均: {stats['mean']:.3f}s")
    print(f"  最小: {stats['min']:.3f}s")
    print(f"  最大: {stats['max']:.3f}s")


def example_3_api_tracking():
    """示例 3: API 調用追蹤"""
    print("\n" + "=" * 60)
    print("示例 3: API 調用追蹤")
    print("=" * 60)

    metrics = MetricsCollector()
    tracker = metrics.api_tracker

    # 方式 1: 手動追蹤
    print("方式 1: 手動追蹤 API 調用")
    tracker.track(
        endpoint="/api/users",
        method="GET",
        status_code=200,
        latency=0.15,
    )

    tracker.track(
        endpoint="/api/users",
        method="POST",
        status_code=201,
        latency=0.25,
    )

    # 模擬一個失敗的請求
    tracker.track(
        endpoint="/api/users",
        method="GET",
        status_code=500,
        latency=1.5,
        error="Internal Server Error",
    )

    # 方式 2: 使用上下文管理器
    print("\n方式 2: 使用上下文管理器")
    with tracker.track_call("/api/products", "GET") as call_context:
        # 模擬 API 調用
        time.sleep(0.1)
        call_context["status_code"] = 200

    # 方式 3: 使用裝飾器
    @track_api_call(tracker, "/api/orders", "POST")
    def create_order(order_id: str):
        """創建訂單"""
        time.sleep(0.2)  # 模擬處理
        return f"訂單 {order_id} 已創建"

    print("\n方式 3: 使用裝飾器")
    create_order("ORD-001")
    create_order("ORD-002")

    # 獲取摘要
    summary = tracker.get_summary()
    print(f"\nAPI 調用摘要:")
    print(f"  總調用次數: {summary['total_calls']}")
    print(f"  總錯誤數: {summary['total_errors']}")
    print(f"  錯誤率: {summary['error_rate']:.1%}")
    print(f"  平均延遲: {summary['avg_latency']:.3f}s")
    print(f"  P95 延遲: {summary['p95_latency']:.3f}s")

    print(f"\n按端點統計:")
    for endpoint, stats in summary["by_endpoint"].items():
        print(f"  {endpoint}:")
        print(f"    調用次數: {stats['count']}")
        print(f"    錯誤數: {stats['errors']}")
        print(f"    平均延遲: {stats['avg_latency']:.3f}s")


def example_4_export():
    """示例 4: 導出指標"""
    print("\n" + "=" * 60)
    print("示例 4: 導出指標到文件")
    print("=" * 60)

    # 創建標準指標集
    metrics = create_standard_metrics()

    # 添加一些測試數據
    metrics.counter("requests_total").inc(100)
    metrics.counter("errors_total").inc(5)
    metrics.gauge("active_connections").set(42)
    metrics.histogram("request_duration_seconds").observe(0.1)
    metrics.histogram("request_duration_seconds").observe(0.5)
    metrics.histogram("request_duration_seconds").observe(1.0)

    # 添加 API 調用數據
    tracker = metrics.api_tracker
    tracker.track("/api/users", "GET", 200, 0.15)
    tracker.track("/api/products", "GET", 200, 0.12)

    # 導出為 JSON
    json_output = metrics.export_json(include_api_calls=True)
    print("\nJSON 格式預覽 (前 500 字符):")
    print(json_output[:500] + "...")

    # 保存到文件
    output_dir = Path(__file__).parent / "metrics_output"
    output_dir.mkdir(exist_ok=True)

    json_file = output_dir / "metrics.json"
    metrics.save_to_file(json_file, format="json")
    print(f"\n已保存 JSON 格式到: {json_file}")

    # 導出為 Prometheus 格式
    prom_file = output_dir / "metrics.prom"
    metrics.save_to_file(prom_file, format="prometheus")
    print(f"已保存 Prometheus 格式到: {prom_file}")

    # 顯示 Prometheus 格式預覽
    prom_output = metrics.export_prometheus()
    print(f"\nPrometheus 格式預覽 (前 500 字符):")
    print(prom_output[:500] + "...")


def example_5_global_instance():
    """示例 5: 使用全局指標收集器"""
    print("\n" + "=" * 60)
    print("示例 5: 使用全局指標收集器")
    print("=" * 60)

    # 獲取全局實例（推薦方式）
    metrics = get_metrics_collector()

    # 在不同的函數中使用同一個實例
    def function_a():
        m = get_metrics_collector()
        m.counter("function_a_calls").inc()

    def function_b():
        m = get_metrics_collector()
        m.counter("function_b_calls").inc()

    # 執行函數
    for _ in range(3):
        function_a()

    for _ in range(5):
        function_b()

    # 查看結果
    print(f"function_a 調用次數: {metrics.counter('function_a_calls').get()}")
    print(f"function_b 調用次數: {metrics.counter('function_b_calls').get()}")


def example_6_real_world_scenario():
    """示例 6: 真實場景 - 監控 LLM API 調用"""
    print("\n" + "=" * 60)
    print("示例 6: 真實場景 - 監控 LLM API 調用")
    print("=" * 60)

    metrics = MetricsCollector()

    @track_latency(metrics, "llm_api_latency", labels={"model": "gpt-4"})
    def call_llm_api(prompt: str, model: str = "gpt-4"):
        """模擬 LLM API 調用"""
        # 增加調用計數
        metrics.counter("llm_api_calls_total", labels={"model": model}).inc()

        # 模擬 API 調用
        time.sleep(0.3)  # 模擬網絡延遲

        # 模擬錯誤
        import random

        if random.random() < 0.1:  # 10% 失敗率
            metrics.counter("llm_api_errors_total", labels={"model": model}).inc()
            raise Exception("API 調用失敗")

        # 記錄 token 使用
        tokens_used = len(prompt.split()) * 2  # 簡化計算
        metrics.histogram("llm_tokens_used", labels={"model": model}).observe(tokens_used)

        return f"回應: {prompt[:20]}..."

    # 模擬多次調用
    prompts = [
        "請解釋什麼是機器學習",
        "如何優化 Python 代碼性能",
        "什麼是深度學習神經網絡",
        "介紹一下自然語言處理",
        "解釋強化學習的概念",
    ]

    print("執行 LLM API 調用...")
    for prompt in prompts:
        try:
            result = call_llm_api(prompt)
            print(f"  ✓ {result}")
        except Exception as e:
            print(f"  ✗ 錯誤: {e}")

    # 顯示統計
    print("\nLLM API 統計:")
    print(f"  總調用次數: {metrics.counter('llm_api_calls_total', labels={'model': 'gpt-4'}).get()}")
    print(f"  總錯誤次數: {metrics.counter('llm_api_errors_total', labels={'model': 'gpt-4'}).get()}")

    latency_stats = metrics.histogram("llm_api_latency", labels={"model": "gpt-4"}).get_statistics()
    print(f"  平均延遲: {latency_stats['mean']:.3f}s")
    print(f"  P95 延遲: {metrics.histogram('llm_api_latency', labels={'model': 'gpt-4'}).get_percentile(95):.3f}s")

    token_stats = metrics.histogram("llm_tokens_used", labels={"model": "gpt-4"}).get_statistics()
    print(f"  平均 Token 使用: {token_stats['mean']:.0f}")
    print(f"  總 Token 使用: {token_stats['sum']:.0f}")


def main():
    """運行所有示例"""
    print("監控指標模組使用示例")
    print("=" * 60)

    example_1_basic_metrics()
    example_2_decorators()
    example_3_api_tracking()
    example_4_export()
    example_5_global_instance()
    example_6_real_world_scenario()

    print("\n" + "=" * 60)
    print("所有示例執行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()

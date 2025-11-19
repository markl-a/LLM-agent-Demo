#!/usr/bin/env python3
"""
LangFlow - 監控與日誌示例

展示如何在 LangFlow 中實現監控和日誌記錄
"""

import json
import logging
from datetime import datetime


# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('langflow.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def create_monitored_flow():
    """創建帶監控的 Flow"""
    return {
        "name": "Monitored Flow",
        "description": "包含監控和日誌的 Flow",
        "data": {
            "nodes": [
                {"id": "input", "type": "ChatInput", "position": {"x": 100, "y": 100}},
                {"id": "logger", "type": "LoggerComponent", "data": {"log_level": "INFO"}, "position": {"x": 200, "y": 100}},
                {"id": "metrics", "type": "MetricsCollector", "position": {"x": 300, "y": 100}},
                {"id": "llm", "type": "ChatOpenAI", "position": {"x": 400, "y": 100}},
                {"id": "output", "type": "ChatOutput", "position": {"x": 500, "y": 100}},
            ],
            "edges": [
                {"source": "input", "target": "logger"},
                {"source": "logger", "target": "metrics"},
                {"source": "metrics", "target": "llm"},
                {"source": "llm", "target": "output"},
            ],
        },
    }


def log_flow_execution(flow_id: str, input_data: dict, output_data: dict, duration: float):
    """記錄 Flow 執行日誌"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "flow_id": flow_id,
        "input": input_data,
        "output": output_data,
        "duration_ms": duration * 1000,
    }

    logger.info(f"Flow execution: {json.dumps(log_entry, ensure_ascii=False)}")


def collect_metrics():
    """收集性能指標"""
    metrics = {
        "total_requests": 0,
        "successful_requests": 0,
        "failed_requests": 0,
        "avg_response_time": 0.0,
        "p95_response_time": 0.0,
        "p99_response_time": 0.0,
    }
    return metrics


def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("📊 LangFlow - 監控與日誌示例")
    print("=" * 60)

    # 創建監控 Flow
    flow = create_monitored_flow()
    with open("monitored_flow.json", "w", encoding="utf-8") as f:
        json.dump(flow, f, indent=2, ensure_ascii=False)
    print("\n✅ 已創建監控 Flow: monitored_flow.json")

    print("""
📋 監控最佳實踐：

1. 日誌記錄
   - 記錄所有請求和響應
   - 包含時間戳和唯一 ID
   - 記錄錯誤和異常
   - 使用結構化日誌（JSON）

2. 性能指標
   - 請求數量（總數/成功/失敗）
   - 響應時間（平均/P95/P99）
   - 錯誤率
   - Token 使用量

3. 告警配置
   - 錯誤率超過閾值
   - 響應時間過長
   - 資源使用異常
   - API 配額耗盡

4. 可視化儀表板
   - Grafana 儀表板
   - 實時監控
   - 歷史趨勢分析

5. 日誌聚合
   - 使用 ELK Stack
   - 或 Loki + Grafana
   - 集中式日誌管理

📊 Prometheus 指標示例：

# 請求計數
langflow_requests_total{flow_id="xxx", status="success"} 1234

# 響應時間直方圖
langflow_request_duration_seconds{flow_id="xxx"} 0.5

# 錯誤率
langflow_errors_total{flow_id="xxx", error_type="timeout"} 5

🔍 日誌查詢示例（Loki）：
{job="langflow"} |= "error" | json | duration > 1s
""")

    print("\n" + "=" * 60)
    print("✅ 監控與日誌示例完成")
    print("=" * 60)


if __name__ == "__main__":
    main()

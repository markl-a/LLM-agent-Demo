"""
PromptFlow 進階技巧範例
======================

本範例展示 PromptFlow 的進階使用技巧。

進階技巧：
1. 變體管理（Variants）
2. 調試技巧
3. 性能優化
4. 最佳實踐

安裝依賴：
pip install promptflow promptflow-tools
"""

import os
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

# ============================================================
# 1. 變體管理（Variants）
# ============================================================

VARIANTS_EXAMPLE = '''
# flow.dag.yaml - 帶變體的 Flow

inputs:
  question:
    type: string

outputs:
  answer:
    type: string
    reference: ${llm_node.output}

nodes:
  - name: llm_node
    type: llm
    source:
      type: code
      path: prompt.jinja2
    inputs:
      question: ${inputs.question}
    connection: azure_openai
    api: chat
    # 定義變體
    variants:
      variant_0:
        temperature: 0.3
        prompt: prompt_concise.jinja2
      variant_1:
        temperature: 0.7
        prompt: prompt_detailed.jinja2
      variant_2:
        temperature: 0.9
        prompt: prompt_creative.jinja2
'''

VARIANT_PROMPTS = {
    "concise": '''
system:
你是一個簡潔的助手，用最少的話回答問題。

user:
{{question}}

請用一句話回答：
''',
    "detailed": '''
system:
你是一個詳細的助手，提供全面的回答。

user:
{{question}}

請詳細解釋：
''',
    "creative": '''
system:
你是一個創意助手，用有趣的方式回答問題。

user:
{{question}}

請用創意的方式回答：
'''
}


# ============================================================
# 2. 調試工具
# ============================================================

class FlowDebugger:
    """
    Flow 調試器

    提供調試和追蹤功能
    """

    def __init__(self):
        self.traces = []
        self.breakpoints = []

    def trace_node(
        self,
        node_name: str,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        duration_ms: float
    ):
        """記錄節點執行"""
        self.traces.append({
            "node": node_name,
            "inputs": inputs,
            "outputs": outputs,
            "duration_ms": duration_ms,
            "timestamp": os.popen("date").read().strip()
        })

    def add_breakpoint(self, node_name: str, condition: Optional[str] = None):
        """添加斷點"""
        self.breakpoints.append({
            "node": node_name,
            "condition": condition
        })

    def print_traces(self):
        """打印追蹤信息"""
        print("=" * 50)
        print("執行追蹤")
        print("=" * 50)
        for trace in self.traces:
            print(f"\n節點: {trace['node']}")
            print(f"  輸入: {json.dumps(trace['inputs'], ensure_ascii=False)[:100]}...")
            print(f"  輸出: {json.dumps(trace['outputs'], ensure_ascii=False)[:100]}...")
            print(f"  耗時: {trace['duration_ms']:.2f}ms")


# ============================================================
# 3. 性能優化配置
# ============================================================

PERFORMANCE_CONFIG = '''
# performance_config.yaml - 性能優化配置

# 並行設置
parallel:
  max_workers: 10
  timeout_seconds: 300

# 緩存設置
cache:
  enabled: true
  ttl_seconds: 3600
  max_size: 1000

# 重試設置
retry:
  max_retries: 3
  backoff_factor: 2
  retry_on_status_codes: [429, 500, 502, 503]

# 批處理設置
batch:
  size: 20
  parallel_workers: 5

# 連接池設置
connection_pool:
  max_connections: 100
  keep_alive: true
  timeout: 30
'''


class CacheManager:
    """
    緩存管理器

    管理 Flow 執行的緩存
    """

    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.cache = {}
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds

    def get(self, key: str) -> Optional[Any]:
        """獲取緩存"""
        import time
        entry = self.cache.get(key)
        if entry:
            if time.time() - entry['timestamp'] < self.ttl_seconds:
                return entry['value']
            else:
                del self.cache[key]
        return None

    def set(self, key: str, value: Any):
        """設置緩存"""
        import time
        if len(self.cache) >= self.max_size:
            # 清理最舊的條目
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]['timestamp'])
            del self.cache[oldest_key]

        self.cache[key] = {
            'value': value,
            'timestamp': time.time()
        }

    def clear(self):
        """清空緩存"""
        self.cache.clear()


# ============================================================
# 4. 錯誤處理
# ============================================================

class FlowErrorHandler:
    """
    Flow 錯誤處理器

    處理 Flow 執行中的錯誤
    """

    def __init__(self):
        self.error_handlers = {}
        self.fallback_responses = {}

    def register_handler(
        self,
        error_type: str,
        handler: callable
    ):
        """註冊錯誤處理器"""
        self.error_handlers[error_type] = handler

    def set_fallback(self, node_name: str, fallback_value: Any):
        """設置回退值"""
        self.fallback_responses[node_name] = fallback_value

    def handle_error(
        self,
        error: Exception,
        node_name: str,
        context: Dict[str, Any]
    ) -> Any:
        """處理錯誤"""
        error_type = type(error).__name__

        if error_type in self.error_handlers:
            return self.error_handlers[error_type](error, context)

        if node_name in self.fallback_responses:
            return self.fallback_responses[node_name]

        raise error


# ============================================================
# 5. 最佳實踐模板
# ============================================================

BEST_PRACTICES_FLOW = '''
# best_practices_flow.dag.yaml

# 版本控制
version: "1.0.0"

# 元數據
metadata:
  name: production_qa_flow
  description: 生產環境問答 Flow
  author: team
  tags:
    - production
    - qa

inputs:
  question:
    type: string
    description: 用戶問題

outputs:
  answer:
    type: string
    reference: ${final_output.output}
  metadata:
    type: object
    reference: ${collect_metadata.output}

nodes:
  # 輸入驗證
  - name: validate_input
    type: python
    source:
      type: code
      path: validate.py
    inputs:
      question: ${inputs.question}

  # 查詢改寫
  - name: rewrite_query
    type: llm
    source:
      type: code
      path: rewrite.jinja2
    inputs:
      original_query: ${validate_input.output}
    connection: azure_openai
    # 啟用緩存
    cache:
      enabled: true
      ttl: 3600

  # 檢索文檔
  - name: retrieve_documents
    type: python
    source:
      type: code
      path: retrieve.py
    inputs:
      query: ${rewrite_query.output}
    # 重試配置
    retry:
      max_retries: 3
      backoff: exponential

  # 生成回答
  - name: generate_answer
    type: llm
    source:
      type: code
      path: generate.jinja2
    inputs:
      question: ${inputs.question}
      context: ${retrieve_documents.output}
    connection: azure_openai
    # 變體支持
    variants:
      default:
        temperature: 0.5
      creative:
        temperature: 0.8

  # 回答驗證
  - name: validate_answer
    type: python
    source:
      type: code
      path: validate_answer.py
    inputs:
      answer: ${generate_answer.output}
      question: ${inputs.question}

  # 最終輸出
  - name: final_output
    type: python
    source:
      type: code
      path: final_output.py
    inputs:
      answer: ${generate_answer.output}
      validation: ${validate_answer.output}

  # 收集元數據
  - name: collect_metadata
    type: python
    source:
      type: code
      path: metadata.py
    inputs:
      nodes_info:
        - ${validate_input.output}
        - ${rewrite_query.output}
        - ${retrieve_documents.output}
'''


# ============================================================
# 使用範例
# ============================================================

def example_variants():
    """
    範例 1: 變體管理

    展示如何使用變體進行 A/B 測試
    """
    print("=" * 50)
    print("範例 1: 變體管理")
    print("=" * 50)

    print("Flow 變體配置:")
    print(VARIANTS_EXAMPLE)

    print("\n不同變體的 Prompt:")
    for name, prompt in VARIANT_PROMPTS.items():
        print(f"\n=== {name} ===")
        print(prompt[:200] + "...")

    print("\n使用變體:")
    print("""
# 運行特定變體
pf flow test --flow . --inputs question="什麼是 AI？" --variant llm_node.variant_1

# 批量運行比較變體
pf run create --flow . --data ./test.jsonl --variant llm_node.variant_0
pf run create --flow . --data ./test.jsonl --variant llm_node.variant_1
pf run create --flow . --data ./test.jsonl --variant llm_node.variant_2

# 比較結果
pf run compare --runs run_v0 run_v1 run_v2
""")


def example_debugging():
    """
    範例 2: 調試技巧

    展示如何調試 Flow
    """
    print("\n" + "=" * 50)
    print("範例 2: 調試技巧")
    print("=" * 50)

    debugger = FlowDebugger()

    # 模擬追蹤
    debugger.trace_node(
        "validate_input",
        {"question": "什麼是機器學習？"},
        {"validated": True, "cleaned_question": "什麼是機器學習"},
        50
    )

    debugger.trace_node(
        "retrieve_documents",
        {"query": "什麼是機器學習"},
        {"documents": ["doc1", "doc2"]},
        200
    )

    debugger.print_traces()

    print("\n調試 CLI 命令:")
    print("""
# 單步調試
pf flow test --flow . --inputs question="測試" --debug

# 查看中間結果
pf flow test --flow . --inputs question="測試" --verbose

# 輸出到文件
pf flow test --flow . --inputs question="測試" --output ./debug_output
""")


def example_performance():
    """
    範例 3: 性能優化

    展示性能優化技巧
    """
    print("\n" + "=" * 50)
    print("範例 3: 性能優化")
    print("=" * 50)

    print("性能優化配置:")
    print(PERFORMANCE_CONFIG)

    print("\n緩存使用示例:")
    cache = CacheManager(max_size=100, ttl_seconds=300)

    # 模擬緩存使用
    cache.set("query_1", {"answer": "緩存的回答"})
    result = cache.get("query_1")
    print(f"緩存命中: {result}")

    result = cache.get("query_2")
    print(f"緩存未命中: {result}")


def example_error_handling():
    """
    範例 4: 錯誤處理

    展示錯誤處理策略
    """
    print("\n" + "=" * 50)
    print("範例 4: 錯誤處理")
    print("=" * 50)

    handler = FlowErrorHandler()

    # 註冊處理器
    handler.register_handler(
        "TimeoutError",
        lambda e, ctx: {"error": "請求超時，請稍後重試"}
    )

    # 設置回退值
    handler.set_fallback("llm_node", {"answer": "抱歉，無法處理您的請求"})

    print("錯誤處理配置:")
    print("""
# 在 Flow 中配置錯誤處理

nodes:
  - name: llm_node
    type: llm
    ...
    error_handling:
      # 重試配置
      retry:
        max_retries: 3
        backoff: exponential
        retry_on:
          - TimeoutError
          - RateLimitError

      # 回退配置
      fallback:
        type: static
        value: "抱歉，服務暫時不可用"

      # 或使用備用節點
      fallback:
        type: node
        node: backup_llm_node
""")


def example_best_practices():
    """
    範例 5: 最佳實踐

    展示生產環境最佳實踐
    """
    print("\n" + "=" * 50)
    print("範例 5: 最佳實踐")
    print("=" * 50)

    print("生產環境 Flow 配置:")
    print(BEST_PRACTICES_FLOW[:1500] + "...")

    print("\n最佳實踐清單:")
    practices = [
        "1. 輸入驗證：始終驗證用戶輸入",
        "2. 錯誤處理：為每個節點配置錯誤處理",
        "3. 緩存策略：對重複查詢使用緩存",
        "4. 重試機制：配置智能重試",
        "5. 監控追蹤：記錄關鍵指標",
        "6. 版本控制：為 Flow 添加版本號",
        "7. 文檔說明：為輸入輸出添加描述",
        "8. 測試覆蓋：編寫單元和集成測試",
    ]

    for p in practices:
        print(f"  {p}")


def example_testing():
    """
    範例 6: 測試策略

    展示如何測試 Flow
    """
    print("\n" + "=" * 50)
    print("範例 6: 測試策略")
    print("=" * 50)

    print("測試配置和命令:")
    print("""
# test_config.yaml

test_cases:
  - name: basic_qa
    inputs:
      question: "什麼是 Python？"
    expected:
      answer_contains: ["編程語言", "程式語言"]
      min_length: 50

  - name: edge_case_empty
    inputs:
      question: ""
    expected:
      error: true
      error_type: ValidationError

  - name: edge_case_long
    inputs:
      question: "很長的問題..." * 100
    expected:
      error: false
      max_latency_ms: 5000

---

# 運行測試
pf flow test --flow . --test-file test_config.yaml

# 運行單個測試
pf flow test --flow . --test-case basic_qa

# 生成測試報告
pf flow test --flow . --test-file test_config.yaml --report ./test_report.html
""")


def example_monitoring():
    """
    範例 7: 監控配置

    展示如何配置監控
    """
    print("\n" + "=" * 50)
    print("範例 7: 監控配置")
    print("=" * 50)

    print("監控配置:")
    print("""
# monitoring.yaml

metrics:
  - name: latency
    type: histogram
    buckets: [100, 500, 1000, 5000]

  - name: tokens_used
    type: counter

  - name: errors
    type: counter
    labels:
      - error_type
      - node_name

alerts:
  - name: high_latency
    metric: latency
    condition: p99 > 5000
    severity: warning

  - name: high_error_rate
    metric: errors
    condition: rate > 0.05
    severity: critical

exporters:
  - type: prometheus
    endpoint: /metrics

  - type: azure_monitor
    connection_string: ${AZURE_MONITOR_CONNECTION}

  - type: application_insights
    instrumentation_key: ${APPINSIGHTS_KEY}
""")


# ============================================================
# 主程序
# ============================================================

if __name__ == "__main__":
    print("PromptFlow 進階技巧範例")
    print()

    example_variants()
    example_debugging()
    example_performance()
    example_error_handling()
    example_best_practices()
    example_testing()
    example_monitoring()

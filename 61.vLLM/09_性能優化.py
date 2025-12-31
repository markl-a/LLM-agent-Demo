#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
vLLM 性能優化示例
=================

本示例展示如何優化 vLLM 的性能，包括：
1. 批處理優化
2. 內存管理優化
3. GPU 利用率優化
4. 吞吐量vs延遲權衡
5. 性能監控和分析
6. 實際優化案例

目標：
- 最大化吞吐量
- 最小化延遲
- 優化資源利用
- 降低成本

適用場景：
- 生產環境調優
- 性能基準測試
- 成本優化
- 問題診斷
"""

import sys
import time
import psutil
from typing import List, Dict
from vllm import LLM, SamplingParams


def performance_fundamentals():
    """
    性能優化基礎

    介紹性能優化的關鍵概念和指標
    """
    print("=" * 80)
    print("性能優化基礎")
    print("=" * 80)

    print("""
關鍵性能指標：
------------

1. 吞吐量 (Throughput)
   - 定義: 每秒處理的 tokens 數
   - 單位: tokens/second
   - 重要性: ★★★★★ (批量處理)
   - 優化方向: 增加批量大小、優化內存

2. 延遲 (Latency)
   - 定義: 單個請求的響應時間
   - 單位: milliseconds
   - 重要性: ★★★★★ (實時交互)
   - 優化方向: 減少批量大小、使用多 GPU

3. 首 Token 延遲 (TTFT - Time To First Token)
   - 定義: 從請求到首個 token 的時間
   - 單位: milliseconds
   - 重要性: ★★★★☆ (流式響應)
   - 優化方向: 減少排隊時間、優化調度

4. GPU 利用率
   - 定義: GPU 計算資源使用比例
   - 單位: percentage
   - 重要性: ★★★★☆
   - 目標: 80-95%

5. 內存利用率
   - 定義: GPU 內存使用比例
   - 單位: percentage
   - 重要性: ★★★★★
   - 目標: 85-95%

vLLM 性能優勢：
--------------

vs. HuggingFace Transformers:
✓ 吞吐量: 24x 提升
✓ 內存效率: 2-3x 提升
✓ 延遲: 相當或更好

核心技術:
1. PagedAttention
   - 減少內存碎片
   - 提高內存利用率
   - 支持更大批量

2. 連續批處理
   - 動態批量調整
   - 減少等待時間
   - 最大化吞吐量

3. 優化的 CUDA 內核
   - 針對 Transformer 優化
   - 融合操作
   - 減少內存訪問

性能權衡：
---------

高吞吐量配置:
✓ 大批量
✓ 長序列
✗ 高延遲

低延遲配置:
✓ 小批量
✓ 多 GPU
✗ 低吞吐量

平衡配置:
✓ 中等批量
✓ 合理的並發
✓ 適中的延遲和吞吐量
    """)


def batch_size_optimization():
    """
    批量大小優化

    展示如何調整批量大小以優化性能
    """
    print("\n" + "=" * 80)
    print("示例 1: 批量大小優化")
    print("=" * 80)

    print("""
批量大小的影響：
--------------

配置參數:
```python
llm = LLM(
    model="meta-llama/Llama-2-7b-hf",

    # 批量配置
    max_num_batched_tokens=8192,  # 批次最大 tokens 數
    max_num_seqs=256,  # 最大並發序列數

    # 序列長度
    max_model_len=4096,  # 最大序列長度
)
```

參數說明：
---------

1. max_num_batched_tokens
   - 單批次可以包含的最大 token 數
   - 直接影響吞吐量和內存使用
   - 推薦值: 2048-16384

   示例:
   - 2048: 低內存使用，適合長序列
   - 8192: 平衡配置（推薦）
   - 16384: 高吞吐量，需要大內存

2. max_num_seqs
   - 同時處理的最大序列數
   - 影響並發能力
   - 推薦值: 128-512

   示例:
   - 64: 低並發，低延遲
   - 256: 平衡配置（推薦）
   - 512: 高並發，高吞吐量

3. max_model_len
   - 模型支持的最大序列長度
   - 限制單個序列長度
   - 影響內存分配

性能測試框架：
------------
```python
import time
from vllm import LLM, SamplingParams

def benchmark_batch_size(
    model_name,
    batch_configs,
    num_prompts=100
):
    results = []

    for config in batch_configs:
        llm = LLM(
            model=model_name,
            max_num_batched_tokens=config['tokens'],
            max_num_seqs=config['seqs'],
        )

        prompts = ["Test prompt"] * num_prompts
        sampling_params = SamplingParams(max_tokens=100)

        start = time.time()
        outputs = llm.generate(prompts, sampling_params)
        elapsed = time.time() - start

        total_tokens = sum(
            len(o.outputs[0].token_ids) for o in outputs
        )
        throughput = total_tokens / elapsed

        results.append({
            'config': config,
            'throughput': throughput,
            'latency': elapsed / num_prompts,
            'total_time': elapsed,
        })

        # 清理
        del llm

    return results

# 測試不同配置
configs = [
    {'tokens': 2048, 'seqs': 128},
    {'tokens': 4096, 'seqs': 256},
    {'tokens': 8192, 'seqs': 256},
    {'tokens': 8192, 'seqs': 512},
]

results = benchmark_batch_size(
    "facebook/opt-125m",
    configs
)

for r in results:
    print(f"Config: {r['config']}")
    print(f"  Throughput: {r['throughput']:.2f} tok/s")
    print(f"  Latency: {r['latency']:.3f} s")
    print()
```

典型結果（示例）：
----------------

| max_batched_tokens | max_seqs | 吞吐量 | 延遲 | GPU內存 |
|--------------------|----------|--------|------|---------|
| 2048               | 128      | 1800   | 0.08s| 12GB    |
| 4096               | 256      | 2400   | 0.12s| 14GB    |
| 8192               | 256      | 2800   | 0.15s| 16GB    |
| 8192               | 512      | 3200   | 0.20s| 18GB    |

選擇建議：
---------

場景 1: 實時聊天（低延遲優先）
```python
llm = LLM(
    model="...",
    max_num_batched_tokens=2048,
    max_num_seqs=64,
    max_model_len=2048,
)
```

場景 2: 批量處理（高吞吐量優先）
```python
llm = LLM(
    model="...",
    max_num_batched_tokens=16384,
    max_num_seqs=512,
    max_model_len=4096,
)
```

場景 3: API 服務（平衡）
```python
llm = LLM(
    model="...",
    max_num_batched_tokens=8192,
    max_num_seqs=256,
    max_model_len=4096,
)
```
    """)


def memory_optimization():
    """
    內存優化

    展示內存管理的最佳實踐
    """
    print("\n" + "=" * 80)
    print("示例 2: 內存優化")
    print("=" * 80)

    print("""
GPU 內存管理：
-------------

1. gpu_memory_utilization
   控制 vLLM 使用的 GPU 內存比例

```python
llm = LLM(
    model="meta-llama/Llama-2-7b-hf",
    gpu_memory_utilization=0.9,  # 使用 90% GPU 內存
)
```

推薦值:
- 0.7: 保守（與其他程序共享）
- 0.85: 平衡（推薦）
- 0.9: 激進（單獨使用）
- 0.95: 最大化（可能不穩定）

2. swap_space
   CPU-GPU 交換空間（GB）

```python
llm = LLM(
    model="...",
    swap_space=4,  # 4GB swap
)
```

作用:
- 處理超長序列
- 緩解內存壓力
- 性能影響: 中等

3. max_model_len
   限制序列長度以節省內存

```python
llm = LLM(
    model="...",
    max_model_len=2048,  # 限制為 2048 tokens
)
```

效果:
- 減少 KV cache 內存
- 允許更大批量
- 適合短文本場景

內存優化策略：
------------

策略 1: 量化
```python
llm = LLM(
    model="TheBloke/Llama-2-7B-AWQ",
    quantization="awq",
    gpu_memory_utilization=0.9,
)
# 內存節省: 3-4x
```

策略 2: 張量並行
```python
llm = LLM(
    model="meta-llama/Llama-2-70b-hf",
    tensor_parallel_size=4,  # 分散到 4 GPU
)
# 每 GPU 內存: 1/4
```

策略 3: 限制序列長度
```python
llm = LLM(
    model="...",
    max_model_len=1024,  # 短序列
    max_num_seqs=512,  # 更多並發
)
```

策略 4: 組合優化
```python
llm = LLM(
    model="TheBloke/Llama-2-13B-AWQ",
    quantization="awq",
    tensor_parallel_size=2,
    gpu_memory_utilization=0.9,
    max_model_len=2048,
)
```

內存監控：
---------
```python
import torch

def monitor_gpu_memory():
    for i in range(torch.cuda.device_count()):
        total = torch.cuda.get_device_properties(i).total_memory / 1e9
        allocated = torch.cuda.memory_allocated(i) / 1e9
        reserved = torch.cuda.memory_reserved(i) / 1e9
        free = total - reserved

        print(f"GPU {i}:")
        print(f"  Total: {total:.2f} GB")
        print(f"  Allocated: {allocated:.2f} GB")
        print(f"  Reserved: {reserved:.2f} GB")
        print(f"  Free: {free:.2f} GB")
        print(f"  Utilization: {reserved/total*100:.1f}%")
        print()

# 定期調用
monitor_gpu_memory()
```

OOM 故障排除：
-------------

錯誤: CUDA out of memory

解決步驟:
1. 減少 gpu_memory_utilization
   ```python
   gpu_memory_utilization=0.7  # 從 0.9 降到 0.7
   ```

2. 減少批量大小
   ```python
   max_num_batched_tokens=4096  # 從 8192 降到 4096
   max_num_seqs=128  # 從 256 降到 128
   ```

3. 減少序列長度
   ```python
   max_model_len=2048  # 從 4096 降到 2048
   ```

4. 使用量化
   ```python
   quantization="awq"
   ```

5. 增加 GPU 數量
   ```python
   tensor_parallel_size=2
   ```

6. 添加 swap 空間
   ```python
   swap_space=8
   ```
    """)


def throughput_vs_latency():
    """
    吞吐量 vs 延遲權衡

    展示如何平衡吞吐量和延遲
    """
    print("\n" + "=" * 80)
    print("示例 3: 吞吐量 vs 延遲權衡")
    print("=" * 80)

    print("""
性能權衡分析：
------------

配置矩陣（Llama-2-7B，A100）:

| 配置 | 批量 | 並發 | 吞吐量 | P50延遲 | P99延遲 | 場景 |
|------|------|------|--------|---------|---------|------|
| A    | 2048 | 64   | 1600   | 0.06s   | 0.08s   | 實時聊天 |
| B    | 4096 | 128  | 2200   | 0.10s   | 0.15s   | 通用API |
| C    | 8192 | 256  | 2800   | 0.18s   | 0.25s   | 批量處理 |
| D    | 16384| 512  | 3400   | 0.35s   | 0.50s   | 離線處理 |

關鍵發現：
1. 批量↑ → 吞吐量↑, 延遲↑
2. 並發↑ → 吞吐量↑, 延遲↑
3. 需要根據場景選擇

場景分析：
---------

場景 1: 實時聊天機器人
需求:
- 低延遲 (< 100ms)
- 中等並發
- 流式響應

配置:
```python
llm = LLM(
    model="meta-llama/Llama-2-7b-chat-hf",

    # 優先延遲
    max_num_batched_tokens=2048,
    max_num_seqs=64,
    max_model_len=2048,

    # GPU 配置
    tensor_parallel_size=2,  # 使用多 GPU 降低延遲
    gpu_memory_utilization=0.85,
)
```

預期性能:
- 延遲: 50-80ms
- 吞吐量: 1500-1800 tok/s
- 並發: 60-80

場景 2: 文檔批量處理
需求:
- 高吞吐量
- 延遲不敏感
- 大量請求

配置:
```python
llm = LLM(
    model="meta-llama/Llama-2-7b-hf",

    # 優先吞吐量
    max_num_batched_tokens=16384,
    max_num_seqs=512,
    max_model_len=4096,

    # GPU 配置
    tensor_parallel_size=1,  # 單 GPU 足夠
    gpu_memory_utilization=0.95,
)
```

預期性能:
- 延遲: 300-500ms
- 吞吐量: 3000-3500 tok/s
- 並發: 500+

場景 3: API 服務（平衡）
需求:
- 平衡延遲和吞吐量
- 可變負載
- 穩定性

配置:
```python
llm = LLM(
    model="meta-llama/Llama-2-7b-hf",

    # 平衡配置
    max_num_batched_tokens=8192,
    max_num_seqs=256,
    max_model_len=4096,

    # GPU 配置
    tensor_parallel_size=1,
    gpu_memory_utilization=0.9,
)
```

預期性能:
- 延遲: 150-250ms
- 吞吐量: 2500-2800 tok/s
- 並發: 200-300

動態調整策略：
------------

根據負載動態調整:

```python
def adjust_config_by_load(current_qps):
    if current_qps < 10:
        # 低負載 - 優化延遲
        return {
            'max_num_batched_tokens': 2048,
            'max_num_seqs': 64,
        }
    elif current_qps < 50:
        # 中等負載 - 平衡
        return {
            'max_num_batched_tokens': 4096,
            'max_num_seqs': 128,
        }
    else:
        # 高負載 - 優化吞吐量
        return {
            'max_num_batched_tokens': 8192,
            'max_num_seqs': 256,
        }
```

性能基準測試：
------------

```python
import time
import numpy as np

def benchmark_latency_throughput(llm, num_requests):
    prompts = ["Test prompt"] * num_requests
    sampling_params = SamplingParams(max_tokens=100)

    latencies = []
    start_time = time.time()

    # 記錄每個請求的延遲
    for prompt in prompts:
        req_start = time.time()
        llm.generate([prompt], sampling_params)
        latency = time.time() - req_start
        latencies.append(latency)

    total_time = time.time() - start_time

    # 統計
    print(f"Total time: {total_time:.2f}s")
    print(f"Throughput: {num_requests/total_time:.2f} req/s")
    print(f"Latency P50: {np.percentile(latencies, 50):.3f}s")
    print(f"Latency P95: {np.percentile(latencies, 95):.3f}s")
    print(f"Latency P99: {np.percentile(latencies, 99):.3f}s")
```
    """)


def performance_monitoring():
    """
    性能監控

    展示如何監控和分析性能
    """
    print("\n" + "=" * 80)
    print("示例 4: 性能監控")
    print("=" * 80)

    print("""
監控指標：
---------

1. 系統級監控
```python
import psutil
import torch

def get_system_metrics():
    # CPU
    cpu_percent = psutil.cpu_percent(interval=1)

    # 內存
    memory = psutil.virtual_memory()
    memory_used_gb = memory.used / 1e9
    memory_percent = memory.percent

    # GPU
    gpu_metrics = []
    for i in range(torch.cuda.device_count()):
        gpu_mem_allocated = torch.cuda.memory_allocated(i) / 1e9
        gpu_mem_reserved = torch.cuda.memory_reserved(i) / 1e9
        gpu_utilization = torch.cuda.utilization(i) if hasattr(torch.cuda, 'utilization') else 0

        gpu_metrics.append({
            'id': i,
            'memory_allocated_gb': gpu_mem_allocated,
            'memory_reserved_gb': gpu_mem_reserved,
            'utilization_percent': gpu_utilization,
        })

    return {
        'cpu_percent': cpu_percent,
        'memory_used_gb': memory_used_gb,
        'memory_percent': memory_percent,
        'gpus': gpu_metrics,
    }
```

2. vLLM 性能指標
```python
import time
from collections import deque

class PerformanceMonitor:
    def __init__(self, window_size=100):
        self.latencies = deque(maxlen=window_size)
        self.throughputs = deque(maxlen=window_size)
        self.start_time = time.time()
        self.total_requests = 0
        self.total_tokens = 0

    def record_request(self, latency, num_tokens):
        self.latencies.append(latency)
        self.throughputs.append(num_tokens / latency)
        self.total_requests += 1
        self.total_tokens += num_tokens

    def get_stats(self):
        if not self.latencies:
            return None

        elapsed = time.time() - self.start_time

        return {
            'avg_latency': np.mean(self.latencies),
            'p50_latency': np.percentile(self.latencies, 50),
            'p95_latency': np.percentile(self.latencies, 95),
            'p99_latency': np.percentile(self.latencies, 99),
            'avg_throughput': np.mean(self.throughputs),
            'total_requests': self.total_requests,
            'total_tokens': self.total_tokens,
            'qps': self.total_requests / elapsed,
            'tokens_per_second': self.total_tokens / elapsed,
        }

# 使用
monitor = PerformanceMonitor()

for prompt in prompts:
    start = time.time()
    output = llm.generate([prompt], sampling_params)
    latency = time.time() - start
    num_tokens = len(output[0].outputs[0].token_ids)

    monitor.record_request(latency, num_tokens)

    # 定期打印統計
    if monitor.total_requests % 10 == 0:
        stats = monitor.get_stats()
        print(f"Stats: {stats}")
```

3. Prometheus 監控
```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# 定義指標
request_counter = Counter('vllm_requests_total', 'Total requests')
request_latency = Histogram('vllm_request_latency_seconds', 'Request latency')
tokens_generated = Counter('vllm_tokens_generated_total', 'Total tokens generated')
gpu_memory_used = Gauge('vllm_gpu_memory_used_bytes', 'GPU memory used')

# 記錄指標
def process_request(llm, prompt):
    request_counter.inc()

    start = time.time()
    output = llm.generate([prompt], sampling_params)
    latency = time.time() - start

    request_latency.observe(latency)
    tokens_generated.inc(len(output[0].outputs[0].token_ids))

    # 更新 GPU 內存
    gpu_memory_used.set(torch.cuda.memory_allocated(0))

    return output

# 啟動 Prometheus 服務器
start_http_server(8001)
```

4. 日誌記錄
```python
import logging
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vllm_performance.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('vllm_perf')

def log_request(prompt, output, latency, metadata=None):
    log_data = {
        'prompt_length': len(prompt),
        'output_length': len(output[0].outputs[0].text),
        'num_tokens': len(output[0].outputs[0].token_ids),
        'latency': latency,
        'throughput': len(output[0].outputs[0].token_ids) / latency,
    }

    if metadata:
        log_data.update(metadata)

    logger.info(json.dumps(log_data))
```

可視化：
-------

使用 Grafana + Prometheus:

1. 配置 Prometheus
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'vllm'
    static_configs:
      - targets: ['localhost:8001']
```

2. Grafana 面板
- QPS 趨勢圖
- 延遲分佈（P50/P95/P99）
- GPU 利用率
- 內存使用
- 吞吐量

告警規則：
---------

```python
def check_performance_alerts(stats):
    alerts = []

    # 延遲過高
    if stats['p99_latency'] > 1.0:
        alerts.append({
            'level': 'WARNING',
            'metric': 'latency',
            'value': stats['p99_latency'],
            'threshold': 1.0,
        })

    # GPU 內存過高
    gpu_memory_percent = get_gpu_memory_percent()
    if gpu_memory_percent > 95:
        alerts.append({
            'level': 'CRITICAL',
            'metric': 'gpu_memory',
            'value': gpu_memory_percent,
            'threshold': 95,
        })

    # 吞吐量過低
    if stats['tokens_per_second'] < 1000:
        alerts.append({
            'level': 'WARNING',
            'metric': 'throughput',
            'value': stats['tokens_per_second'],
            'threshold': 1000,
        })

    return alerts
```
    """)


def optimization_checklist():
    """
    優化檢查清單

    提供完整的優化檢查列表
    """
    print("\n" + "=" * 80)
    print("優化檢查清單")
    print("=" * 80)

    print("""
部署前檢查：
----------

□ 硬件配置
  □ GPU 型號和數量
  □ GPU 內存大小
  □ GPU 間連接（NVLink/PCIe）
  □ 系統內存
  □ CPU 核心數

□ 模型選擇
  □ 模型大小適合 GPU 內存
  □ 考慮量化（AWQ/GPTQ）
  □ 考慮 LoRA 適配器

□ 基礎配置
  □ gpu_memory_utilization (0.85-0.95)
  □ max_model_len (根據實際需求)
  □ dtype (float16/bfloat16)

運行時優化：
----------

□ 批處理配置
  □ max_num_batched_tokens
  □ max_num_seqs
  □ 根據負載調整

□ 並行策略
  □ tensor_parallel_size
  □ 數據並行實例數
  □ GPU 分配策略

□ 內存管理
  □ 監控內存使用
  □ 設置 swap_space
  □ 避免 OOM

□ 監控和日誌
  □ 性能指標收集
  □ 日誌記錄
  □ 告警設置

定期檢查：
---------

□ 每日
  □ 檢查錯誤日誌
  □ 查看性能趨勢
  □ 驗證服務可用性

□ 每週
  □ 性能基準測試
  □ 資源使用分析
  □ 優化配置調整

□ 每月
  □ 成本分析
  □ 容量規劃
  □ 技術更新評估

故障排查流程：
------------

1. 性能下降
   → 檢查 GPU 利用率
   → 查看內存使用
   → 分析請求模式
   → 調整批量配置

2. OOM 錯誤
   → 減少 gpu_memory_utilization
   → 減少 max_num_batched_tokens
   → 減少 max_model_len
   → 使用量化
   → 增加 GPU 數量

3. 延遲過高
   → 減少批量大小
   → 增加 GPU 數量
   → 檢查排隊情況
   → 優化請求路由

4. 吞吐量不足
   → 增加批量大小
   → 增加並發數
   → 優化內存配置
   → 使用多實例

最佳實踐總結：
------------

1. 從保守配置開始，逐步優化
2. 持續監控性能指標
3. 根據實際負載調整
4. 定期進行基準測試
5. 記錄所有配置變更
6. 準備回滾方案
7. 關注 vLLM 更新
8. 參與社區討論
    """)


def main():
    """
    主函數：運行所有示例
    """
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 25 + "vLLM 性能優化示例" + " " * 25 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")

    try:
        # 基礎知識
        performance_fundamentals()

        # 示例 1: 批量大小優化
        batch_size_optimization()

        # 示例 2: 內存優化
        memory_optimization()

        # 示例 3: 吞吐量vs延遲
        throughput_vs_latency()

        # 示例 4: 性能監控
        performance_monitoring()

        # 優化檢查清單
        optimization_checklist()

        print("\n" + "=" * 80)
        print("✓ 所有示例展示完成！")
        print("=" * 80)

        print("\n關鍵要點：")
        print("  1. 性能優化需要根據實際場景平衡")
        print("  2. 批量大小是最重要的調優參數")
        print("  3. 持續監控是優化的基礎")
        print("  4. 從保守配置開始，逐步優化")
        print("  5. 記錄所有變更，方便回滾")

    except KeyboardInterrupt:
        print("\n\n程序被用戶中斷")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ 運行出錯: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
vLLM 多 GPU 部署示例
===================

本示例展示如何使用 vLLM 進行多 GPU 部署，包括：
1. 張量並行（Tensor Parallelism）
2. 管道並行（Pipeline Parallelism）
3. 數據並行
4. GPU 資源管理
5. 性能優化配置
6. 實際部署案例

多 GPU 部署可以：
- 加載更大的模型（超過單 GPU 內存）
- 提高推理吞吐量
- 降低延遲

適用場景：
- 大型模型部署（13B+）
- 高並發服務
- 生產環境
"""

import sys
import torch
from typing import List, Dict
from vllm import LLM, SamplingParams


def check_gpu_availability():
    """
    檢查 GPU 可用性

    驗證系統中的 GPU 配置
    """
    print("=" * 80)
    print("GPU 資源檢查")
    print("=" * 80)

    try:
        if not torch.cuda.is_available():
            print("\n✗ 未檢測到 CUDA 支持")
            print("多 GPU 部署需要 NVIDIA GPU 和 CUDA")
            return False

        num_gpus = torch.cuda.device_count()
        print(f"\n✓ 檢測到 {num_gpus} 個 GPU")

        for i in range(num_gpus):
            gpu_name = torch.cuda.get_device_name(i)
            gpu_props = torch.cuda.get_device_properties(i)
            gpu_memory = gpu_props.total_memory / 1e9
            compute_capability = f"{gpu_props.major}.{gpu_props.minor}"

            print(f"\nGPU {i}:")
            print(f"  - 型號: {gpu_name}")
            print(f"  - 內存: {gpu_memory:.2f} GB")
            print(f"  - 計算能力: {compute_capability}")

            # 檢查內存使用
            allocated = torch.cuda.memory_allocated(i) / 1e9
            cached = torch.cuda.memory_reserved(i) / 1e9
            print(f"  - 已分配內存: {allocated:.2f} GB")
            print(f"  - 緩存內存: {cached:.2f} GB")
            print(f"  - 可用內存: {gpu_memory - cached:.2f} GB")

        return num_gpus > 0

    except Exception as e:
        print(f"✗ 檢查 GPU 時出錯: {str(e)}")
        return False


def tensor_parallelism_example():
    """
    張量並行示例

    展示如何使用張量並行跨多個 GPU 部署模型
    """
    print("\n" + "=" * 80)
    print("示例 1: 張量並行（Tensor Parallelism）")
    print("=" * 80)

    print("""
張量並行概念：
-------------
張量並行將模型的每一層分割到多個 GPU 上。
每個 GPU 處理層的一部分，適合超大模型。

優勢：
✓ 可以運行超過單 GPU 內存的模型
✓ 各 GPU 負載均衡
✓ 降低單次推理延遲

適用場景：
- 70B+ 超大模型
- GPU 內存不足以加載完整模型
- 需要降低延遲的場景

配置建議：
- 7B 模型: 單 GPU
- 13B 模型: 1-2 GPU
- 30B 模型: 2-4 GPU
- 70B 模型: 4-8 GPU
    """)

    try:
        num_gpus = torch.cuda.device_count()

        if num_gpus < 2:
            print("\n⚠ 需要至少 2 個 GPU 才能演示張量並行")
            print(f"當前可用 GPU 數量: {num_gpus}")
            return

        print(f"\n使用 {num_gpus} 個 GPU 進行張量並行...")
        print("-" * 80)

        # 初始化模型，使用張量並行
        llm = LLM(
            model="facebook/opt-125m",  # 實際應用中使用更大的模型
            tensor_parallel_size=num_gpus,  # 使用所有可用 GPU
            dtype="float16",
            trust_remote_code=True,
            gpu_memory_utilization=0.9,
        )

        print(f"✓ 模型已使用 {num_gpus} 個 GPU 加載（張量並行）")

        # 測試推理
        sampling_params = SamplingParams(
            temperature=0.8,
            max_tokens=50,
        )

        prompts = [
            "The future of technology is",
            "Artificial intelligence will revolutionize",
        ]

        print("\n執行推理測試...")
        outputs = llm.generate(prompts, sampling_params)

        print("\n生成結果：")
        for i, output in enumerate(outputs):
            print(f"\n[{i+1}] {output.prompt}")
            print(f"    {output.outputs[0].text[:100]}...")

        print("\n✓ 張量並行推理成功完成")

        # GPU 使用統計
        print("\nGPU 使用情況：")
        for i in range(num_gpus):
            allocated = torch.cuda.memory_allocated(i) / 1e9
            print(f"  GPU {i}: {allocated:.2f} GB 已分配")

    except Exception as e:
        print(f"\n✗ 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()


def pipeline_parallelism_example():
    """
    管道並行示例

    展示管道並行的概念和配置
    """
    print("\n" + "=" * 80)
    print("示例 2: 管道並行（Pipeline Parallelism）")
    print("=" * 80)

    print("""
管道並行概念：
-------------
管道並行將模型的不同層分配到不同的 GPU。
例如：GPU0 處理前半部分層，GPU1 處理後半部分層。

特點：
✓ 按層分割模型
✓ 序列化處理
✓ 適合非常深的模型

與張量並行的區別：
- 張量並行: 每層都分割到所有 GPU
- 管道並行: 不同層在不同 GPU

當前狀態：
⚠ vLLM 主要支持張量並行
⚠ 管道並行支持有限
⚠ 推薦優先使用張量並行

配置示例（如果支持）:
```python
llm = LLM(
    model="meta-llama/Llama-2-70b-hf",
    tensor_parallel_size=4,      # 張量並行
    pipeline_parallel_size=2,    # 管道並行（可能不支持）
)
```

組合使用：
對於超大模型，可以組合使用：
- 8 GPU 系統
- tensor_parallel_size=4
- pipeline_parallel_size=2
- 總計使用 4x2=8 個 GPU
    """)


def data_parallelism_example():
    """
    數據並行示例

    展示如何使用多個模型實例處理不同請求
    """
    print("\n" + "=" * 80)
    print("示例 3: 數據並行")
    print("=" * 80)

    print("""
數據並行概念：
-------------
在不同 GPU 上運行獨立的模型副本，
每個副本處理不同的請求批次。

特點：
✓ 提高吞吐量
✓ GPU 間獨立
✓ 易於擴展

實現方式：
1. 多進程方式：
   - 每個進程綁定到不同的 GPU
   - 使用負載均衡器分發請求

2. 多實例方式：
   - 啟動多個 vLLM API 服務器
   - 使用 Nginx/HAProxy 負載均衡

示例配置：

# GPU 0 運行實例 1
CUDA_VISIBLE_DEVICES=0 python -m vllm.entrypoints.openai.api_server \\
    --model meta-llama/Llama-2-7b-hf \\
    --port 8000

# GPU 1 運行實例 2
CUDA_VISIBLE_DEVICES=1 python -m vllm.entrypoints.openai.api_server \\
    --model meta-llama/Llama-2-7b-hf \\
    --port 8001

# GPU 2 運行實例 3
CUDA_VISIBLE_DEVICES=2 python -m vllm.entrypoints.openai.api_server \\
    --model meta-llama/Llama-2-7b-hf \\
    --port 8002

然後使用負載均衡器（Nginx/HAProxy）分發請求。

適用場景：
- 高並發 API 服務
- 模型可以在單 GPU 運行
- 需要高可用性
    """)


def gpu_resource_management():
    """
    GPU 資源管理

    展示如何配置和管理 GPU 資源
    """
    print("\n" + "=" * 80)
    print("示例 4: GPU 資源管理")
    print("=" * 80)

    print("""
關鍵參數配置：
-------------

1. gpu_memory_utilization
   控制每個 GPU 的內存使用比例

   ```python
   llm = LLM(
       model="model-name",
       gpu_memory_utilization=0.9,  # 使用 90% GPU 內存
   )
   ```

   建議值：
   - 開發環境: 0.7-0.8（留出調試空間）
   - 生產環境: 0.9-0.95（最大化利用）
   - 共享 GPU: 0.5-0.7（與其他程序共享）

2. tensor_parallel_size
   張量並行使用的 GPU 數量

   ```python
   llm = LLM(
       model="meta-llama/Llama-2-70b-hf",
       tensor_parallel_size=4,  # 使用 4 個 GPU
   )
   ```

   選擇建議：
   - 必須是 2 的冪次方（1, 2, 4, 8）
   - 不要超過實際 GPU 數量
   - 根據模型大小選擇

3. max_model_len
   限制最大序列長度，降低內存需求

   ```python
   llm = LLM(
       model="model-name",
       max_model_len=2048,  # 限制為 2048 tokens
   )
   ```

4. swap_space
   設置 CPU-GPU 交換空間（GB）

   ```python
   llm = LLM(
       model="model-name",
       swap_space=4,  # 4GB swap 空間
   )
   ```

完整配置示例：
```python
from vllm import LLM, SamplingParams

llm = LLM(
    # 模型配置
    model="meta-llama/Llama-2-13b-hf",

    # GPU 配置
    tensor_parallel_size=2,
    gpu_memory_utilization=0.9,

    # 內存配置
    max_model_len=4096,
    swap_space=4,

    # 數據類型
    dtype="float16",

    # 其他
    trust_remote_code=True,
)
```

監控 GPU 使用：
```bash
# 實時監控
nvidia-smi -l 1

# 查看詳細信息
nvidia-smi --query-gpu=index,name,memory.used,memory.total,utilization.gpu --format=csv

# Python 監控
import torch
for i in range(torch.cuda.device_count()):
    print(f"GPU {i}:")
    print(f"  Memory allocated: {torch.cuda.memory_allocated(i)/1e9:.2f} GB")
    print(f"  Memory cached: {torch.cuda.memory_reserved(i)/1e9:.2f} GB")
```
    """)


def multi_gpu_deployment_strategies():
    """
    多 GPU 部署策略

    根據不同需求選擇部署方案
    """
    print("\n" + "=" * 80)
    print("示例 5: 多 GPU 部署策略")
    print("=" * 80)

    print("""
場景 1: 7B 模型 + 4 GPU
-----------------------
策略 A - 單模型張量並行（低延遲）:
```python
# 使用 2 GPU 張量並行，其餘保留
llm = LLM(
    model="meta-llama/Llama-2-7b-hf",
    tensor_parallel_size=2,
)
```
- 延遲: 低
- 吞吐量: 中
- 適合: 實時交互應用

策略 B - 數據並行（高吞吐）:
```bash
# 在 4 個 GPU 上運行 4 個獨立實例
for i in 0 1 2 3; do
    CUDA_VISIBLE_DEVICES=$i python -m vllm.entrypoints.openai.api_server \\
        --model meta-llama/Llama-2-7b-hf \\
        --port $((8000+i)) &
done
```
- 延遲: 中
- 吞吐量: 高
- 適合: 高並發 API 服務

場景 2: 13B 模型 + 4 GPU
------------------------
推薦策略:
```python
llm = LLM(
    model="meta-llama/Llama-2-13b-hf",
    tensor_parallel_size=2,
)
```
- 每個實例使用 2 GPU
- 可運行 2 個實例（使用全部 4 GPU）
- 平衡延遲和吞吐量

場景 3: 70B 模型 + 4 GPU
------------------------
必須使用張量並行:
```python
llm = LLM(
    model="meta-llama/Llama-2-70b-hf",
    tensor_parallel_size=4,
    gpu_memory_utilization=0.95,
)
```
- 單個模型分布在 4 GPU
- 可能需要使用量化（AWQ/GPTQ）
- 延遲較高，但能運行大模型

場景 4: 70B 模型 + 8 GPU
------------------------
推薦策略:
```python
llm = LLM(
    model="meta-llama/Llama-2-70b-hf",
    tensor_parallel_size=8,
    gpu_memory_utilization=0.9,
)
```
- 或使用 4 GPU 張量並行 + 量化，運行 2 個實例
- 根據延遲/吞吐量需求選擇

決策樹：
-------
1. 模型能否在單 GPU 運行？
   YES → 考慮數據並行
   NO  → 使用張量並行

2. 需求是低延遲還是高吞吐？
   低延遲 → 張量並行
   高吞吐 → 數據並行

3. GPU 數量是否足夠？
   不足 → 使用量化
   足夠 → 選擇最優策略

性能對比（示例）:
----------------
配置: Llama-2-7b, A100 GPU, 批量大小=32

| 策略 | GPU數 | 延遲(ms) | 吞吐量(tok/s) |
|------|-------|----------|---------------|
| 單GPU | 1 | 25 | 2000 |
| 張量並行 | 2 | 18 | 2400 |
| 數據並行 | 2 | 25 | 4000 |
| 張量並行 | 4 | 12 | 3000 |
| 數據並行 | 4 | 25 | 8000 |

結論：數據並行提供更高吞吐量，張量並行降低延遲
    """)


def troubleshooting_guide():
    """
    常見問題排查

    多 GPU 部署的問題解決
    """
    print("\n" + "=" * 80)
    print("示例 6: 常見問題排查")
    print("=" * 80)

    print("""
問題 1: OOM (Out of Memory)
---------------------------
錯誤信息: "CUDA out of memory"

解決方案:
1. 減少 gpu_memory_utilization
   ```python
   llm = LLM(model="...", gpu_memory_utilization=0.7)
   ```

2. 增加 tensor_parallel_size
   ```python
   llm = LLM(model="...", tensor_parallel_size=2)
   ```

3. 減少 max_model_len
   ```python
   llm = LLM(model="...", max_model_len=2048)
   ```

4. 使用量化模型
   ```python
   llm = LLM(model="...", quantization="awq")
   ```

問題 2: GPU 未被使用
-------------------
現象: nvidia-smi 顯示 GPU 利用率為 0

檢查：
1. 驗證 CUDA 可用性
   ```python
   import torch
   print(torch.cuda.is_available())
   print(torch.cuda.device_count())
   ```

2. 檢查環境變量
   ```bash
   echo $CUDA_VISIBLE_DEVICES
   ```

3. 確認模型已加載到 GPU
   ```python
   llm = LLM(model="...", device="cuda")
   ```

問題 3: 張量並行失敗
-------------------
錯誤: "Tensor parallel size must be a power of 2"

解決：使用 1, 2, 4, 8, 16... 等值
```python
# 正確
tensor_parallel_size=4

# 錯誤
tensor_parallel_size=3
```

問題 4: 多 GPU 性能未提升
------------------------
可能原因:
1. 模型太小，通信開銷大於計算收益
2. 批量大小太小
3. GPU 間通信帶寬不足

解決:
- 使用 NVLink 連接的 GPU
- 增加批量大小
- 對小模型使用數據並行而非張量並行

問題 5: GPU 間負載不均
---------------------
現象: 某些 GPU 使用率很高，其他很低

檢查:
1. 確認使用了正確的並行策略
2. 檢查模型是否正確分片
3. 監控每個 GPU 的內存和計算使用

診斷命令:
```bash
# 持續監控所有 GPU
watch -n 1 nvidia-smi

# 詳細統計
nvidia-smi dmon -s pucvmet

# 進程級監控
nvidia-smi pmon
```

問題 6: NCCL 錯誤
----------------
錯誤: "NCCL error" 或通信超時

解決:
1. 設置環境變量
   ```bash
   export NCCL_DEBUG=INFO
   export NCCL_TIMEOUT=300
   ```

2. 檢查網絡配置
3. 確保 GPU 間通信暢通
4. 更新 NCCL 庫
    """)


def main():
    """
    主函數：運行所有示例
    """
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 25 + "vLLM 多 GPU 部署示例" + " " * 24 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")

    try:
        # 檢查 GPU 可用性
        if not check_gpu_availability():
            print("\n⚠ 系統中沒有可用的 GPU")
            print("多 GPU 示例需要 NVIDIA GPU 支持")
            print("\n以下將展示概念和配置信息...")

        # 示例 1: 張量並行
        tensor_parallelism_example()

        # 示例 2: 管道並行
        pipeline_parallelism_example()

        # 示例 3: 數據並行
        data_parallelism_example()

        # 示例 4: 資源管理
        gpu_resource_management()

        # 示例 5: 部署策略
        multi_gpu_deployment_strategies()

        # 示例 6: 問題排查
        troubleshooting_guide()

        print("\n" + "=" * 80)
        print("✓ 所有示例展示完成！")
        print("=" * 80)

        print("\n關鍵要點：")
        print("  1. 根據模型大小選擇合適的並行策略")
        print("  2. 張量並行降低延遲，數據並行提高吞吐量")
        print("  3. 合理配置 GPU 內存利用率")
        print("  4. 監控 GPU 使用情況並調優")
        print("  5. 大模型必須使用張量並行或量化")

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

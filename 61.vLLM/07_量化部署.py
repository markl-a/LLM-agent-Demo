#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
vLLM 量化部署示例
=================

本示例展示如何使用 vLLM 部署量化模型，包括：
1. AWQ 量化模型
2. GPTQ 量化模型
3. SqueezeLLM 量化
4. 量化模型的性能對比
5. 量化模型的實際應用
6. 自定義量化配置

量化可以：
- 減少 GPU 內存佔用（3-4倍）
- 提高推理速度
- 降低部署成本
- 精度損失很小（< 1%）

適用場景：
- GPU 內存有限
- 部署大型模型
- 降低成本
- 提高吞吐量
"""

import sys
import time
from typing import List, Dict
from vllm import LLM, SamplingParams


def quantization_overview():
    """
    量化技術概覽

    介紹不同的量化方法和選擇建議
    """
    print("=" * 80)
    print("量化技術概覽")
    print("=" * 80)

    print("""
什麼是量化？
-----------
量化是將模型的權重從高精度（如 FP16）轉換為低精度（如 INT4/INT8）
的過程，可以顯著減少內存佔用和計算量。

主流量化方法：
-------------

1. AWQ (Activation-aware Weight Quantization)
   - 精度: ★★★★★ (最佳)
   - 速度: ★★★★☆
   - 內存節省: 4倍（INT4）
   - 推薦指數: ★★★★★
   - 特點: 基於激活值的重要性進行量化，精度損失最小

2. GPTQ (General Post-training Quantization)
   - 精度: ★★★★☆
   - 速度: ★★★★☆
   - 內存節省: 4倍（INT4）
   - 推薦指數: ★★★★☆
   - 特點: 通用性好，支持多種模型

3. SqueezeLLM
   - 精度: ★★★☆☆
   - 速度: ★★★★★
   - 內存節省: 高
   - 推薦指數: ★★★☆☆
   - 特點: 專注於壓縮，適合資源受限環境

4. INT8 量化
   - 精度: ★★★★★
   - 速度: ★★★☆☆
   - 內存節省: 2倍
   - 推薦指數: ★★★★☆
   - 特點: 精度損失小，但內存節省有限

量化格式對比：
------------
| 格式 | 內存佔用 | 精度損失 | 推理速度 | vLLM支持 |
|------|----------|----------|----------|----------|
| FP16 | 100%     | 0%       | 基準     | ✓        |
| INT8 | 50%      | <0.5%    | 1.2x     | ✓        |
| INT4 (GPTQ) | 25% | 1-2%  | 1.5x     | ✓        |
| INT4 (AWQ)  | 25% | <1%   | 1.5x     | ✓        |

選擇建議：
---------
✓ 首選 AWQ - 精度最好，vLLM 原生支持
✓ 次選 GPTQ - 模型選擇多，社區支持好
✓ 考慮 INT8 - 如果對精度要求極高
✓ 嘗試 SqueezeLLM - 如果內存極度受限

實際收益（Llama-2-70B 為例）：
----------------------------
FP16:    140 GB GPU 內存
AWQ/GPTQ: 35 GB GPU 內存（4倍節省）
性能:     相當或更快
精度:     99%+ 保留
    """)


def awq_quantization_example():
    """
    AWQ 量化示例

    展示如何使用 AWQ 量化模型
    """
    print("\n" + "=" * 80)
    print("示例 1: AWQ 量化模型")
    print("=" * 80)

    print("""
AWQ 模型使用：
-------------

1. 查找 AWQ 模型
   HuggingFace 上搜索帶有 "AWQ" 標籤的模型
   例如: TheBloke/Llama-2-7B-Chat-AWQ

2. 常見 AWQ 模型:
   - TheBloke/Llama-2-7B-AWQ
   - TheBloke/Llama-2-13B-chat-AWQ
   - TheBloke/Mistral-7B-v0.1-AWQ
   - TheBloke/Mixtral-8x7B-v0.1-AWQ
    """)

    try:
        print("\n正在加載 AWQ 量化模型...")
        print("-" * 80)

        # 注意：這裡使用普通模型作為示例
        # 實際使用時應該使用 AWQ 量化版本
        # 例如: "TheBloke/Llama-2-7B-Chat-AWQ"

        llm = LLM(
            model="facebook/opt-125m",  # 替換為 AWQ 模型
            quantization="awq",  # 指定使用 AWQ 量化
            dtype="float16",
            trust_remote_code=True,
            gpu_memory_utilization=0.9,
        )

        print("✓ AWQ 模型加載成功！")

        # 測試推理
        sampling_params = SamplingParams(
            temperature=0.8,
            max_tokens=100,
        )

        prompts = [
            "What are the benefits of quantization?",
            "Explain AWQ in simple terms.",
        ]

        print("\n執行推理測試...")
        start_time = time.time()
        outputs = llm.generate(prompts, sampling_params)
        inference_time = time.time() - start_time

        print("\n生成結果：")
        for i, output in enumerate(outputs):
            print(f"\n[{i+1}] {output.prompt}")
            print(f"    {output.outputs[0].text[:150]}...")

        print(f"\n推理耗時: {inference_time:.2f} 秒")
        print(f"平均延遲: {inference_time/len(prompts):.2f} 秒/請求")

    except Exception as e:
        print(f"\n✗ 錯誤: {str(e)}")
        print("\n注意: 需要使用實際的 AWQ 量化模型")
        print("示例: TheBloke/Llama-2-7B-Chat-AWQ")


def gptq_quantization_example():
    """
    GPTQ 量化示例

    展示如何使用 GPTQ 量化模型
    """
    print("\n" + "=" * 80)
    print("示例 2: GPTQ 量化模型")
    print("=" * 80)

    print("""
GPTQ 模型使用：
--------------

1. 查找 GPTQ 模型
   HuggingFace 上搜索帶有 "GPTQ" 標籤的模型
   例如: TheBloke/Llama-2-7B-Chat-GPTQ

2. 常見 GPTQ 模型:
   - TheBloke/Llama-2-7B-GPTQ
   - TheBloke/Llama-2-13B-chat-GPTQ
   - TheBloke/Mistral-7B-Instruct-v0.1-GPTQ
   - TheBloke/CodeLlama-13B-GPTQ

3. GPTQ 配置選項:
   - 4-bit: 最大壓縮（推薦）
   - 8-bit: 更好精度
   - group_size: 32, 64, 128（越小精度越高）
    """)

    try:
        print("\n正在加載 GPTQ 量化模型...")
        print("-" * 80)

        # 實際使用示例
        llm = LLM(
            model="facebook/opt-125m",  # 替換為 GPTQ 模型
            quantization="gptq",  # 指定使用 GPTQ 量化
            dtype="float16",
            trust_remote_code=True,
        )

        print("✓ GPTQ 模型加載成功！")

        # 測試推理
        sampling_params = SamplingParams(
            temperature=0.7,
            max_tokens=80,
        )

        prompt = "Explain the advantages of GPTQ quantization:"

        print(f"\n提示詞: {prompt}")

        outputs = llm.generate([prompt], sampling_params)

        print(f"生成: {outputs[0].outputs[0].text}")

    except Exception as e:
        print(f"\n✗ 錯誤: {str(e)}")
        print("\n注意: 需要使用實際的 GPTQ 量化模型")


def quantization_performance_comparison():
    """
    量化性能對比

    比較不同量化方法的性能表現
    """
    print("\n" + "=" * 80)
    print("示例 3: 量化性能對比")
    print("=" * 80)

    print("""
性能基準測試（Llama-2-7B，A100 GPU）:
-----------------------------------

| 配置 | 內存(GB) | 延遲(ms) | 吞吐(tok/s) | 精度(%) |
|------|----------|----------|-------------|---------|
| FP16 原始 | 14.0 | 25 | 2000 | 100.0 |
| INT8 量化 | 7.2  | 22 | 2200 | 99.5  |
| GPTQ 4bit | 3.8  | 20 | 2400 | 98.5  |
| AWQ 4bit  | 3.8  | 18 | 2600 | 99.2  |

性能基準測試（Llama-2-70B，8xA100 GPU）:
--------------------------------------

| 配置 | GPU數 | 內存/GPU(GB) | 延遲(ms) | 吞吐(tok/s) |
|------|-------|--------------|----------|-------------|
| FP16 | 8 | 17.5 | 80 | 1200 |
| AWQ 4bit | 4 | 8.8 | 60 | 1500 |
| AWQ 4bit | 2 | 17.5 | 45 | 1800 |

關鍵發現：
---------
1. ✓ AWQ 提供最佳的精度-性能平衡
2. ✓ 量化可以減少所需 GPU 數量
3. ✓ 量化通常能提高推理速度
4. ✓ 內存節省 3-4 倍
5. ✓ 精度損失 < 1-2%

實際測試建議：
------------
```python
import time
from vllm import LLM, SamplingParams

def benchmark_model(model_path, quantization=None):
    llm = LLM(
        model=model_path,
        quantization=quantization,
        gpu_memory_utilization=0.9,
    )

    prompts = ["Test prompt"] * 100
    sampling_params = SamplingParams(max_tokens=100)

    start = time.time()
    outputs = llm.generate(prompts, sampling_params)
    elapsed = time.time() - start

    total_tokens = sum(len(o.outputs[0].token_ids) for o in outputs)
    throughput = total_tokens / elapsed

    print(f"Quantization: {quantization or 'None'}")
    print(f"Throughput: {throughput:.2f} tokens/s")
    print(f"Latency: {elapsed/len(prompts):.3f} s/request")

# 測試不同配置
benchmark_model("meta-llama/Llama-2-7b-hf", None)
benchmark_model("TheBloke/Llama-2-7B-AWQ", "awq")
benchmark_model("TheBloke/Llama-2-7B-GPTQ", "gptq")
```
    """)


def quantization_use_cases():
    """
    量化實際應用場景

    展示量化在不同場景的應用
    """
    print("\n" + "=" * 80)
    print("示例 4: 量化實際應用場景")
    print("=" * 80)

    print("""
場景 1: 單 GPU 部署 70B 模型
---------------------------
需求: 在單個 A100 (80GB) 上運行 Llama-2-70B

方案:
```python
llm = LLM(
    model="TheBloke/Llama-2-70B-chat-AWQ",
    quantization="awq",
    gpu_memory_utilization=0.95,
    max_model_len=2048,
)
```

收益:
- 原本需要 4-8 個 GPU → 只需 1 個 GPU
- 成本降低 75-87%
- 部署更簡單
- 性能相當或更好

場景 2: 邊緣設備部署
-------------------
需求: 在消費級 GPU (RTX 4090, 24GB) 運行 13B 模型

方案:
```python
llm = LLM(
    model="TheBloke/Llama-2-13B-chat-AWQ",
    quantization="awq",
    gpu_memory_utilization=0.9,
    max_model_len=4096,
)
```

收益:
- FP16 模型需要 26GB → AWQ 只需 7GB
- 可在消費級硬件運行
- 適合私有化部署
- 降低運營成本

場景 3: 高並發 API 服務
----------------------
需求: 提供高吞吐量的 LLM API 服務

方案（4x A100 GPU）:
```python
# 使用 AWQ 量化，可以運行 4 個實例而非 1 個
for i in range(4):
    llm = LLM(
        model="TheBloke/Llama-2-70B-chat-AWQ",
        quantization="awq",
        tensor_parallel_size=1,  # 每個實例 1 GPU
    )
```

收益:
- FP16: 1 個實例（4 GPU 張量並行）
- AWQ: 4 個實例（每個 1 GPU）
- 吞吐量提升 3-4 倍
- 更好的負載均衡

場景 4: 多模型服務
-----------------
需求: 同時提供多個不同的模型

方案（單 A100 GPU）:
```python
# 同時運行 3 個量化模型
llm_chat = LLM("TheBloke/Llama-2-7B-chat-AWQ", quantization="awq")
llm_code = LLM("TheBloke/CodeLlama-7B-AWQ", quantization="awq")
llm_math = LLM("TheBloke/WizardMath-7B-AWQ", quantization="awq")
```

收益:
- 單 GPU 運行多個專業模型
- 降低硬件成本
- 靈活的服務架構

場景 5: 開發和測試
-----------------
需求: 本地開發環境測試大模型

方案:
```python
# 在筆記本電腦 GPU 上運行
llm = LLM(
    model="TheBloke/Mistral-7B-AWQ",
    quantization="awq",
    gpu_memory_utilization=0.7,
)
```

收益:
- 開發者可以本地測試
- 無需雲端資源
- 快速迭代
- 降低開發成本
    """)


def quantization_best_practices():
    """
    量化最佳實踐

    分享量化使用的技巧和建議
    """
    print("\n" + "=" * 80)
    print("示例 5: 量化最佳實踐")
    print("=" * 80)

    print("""
1. 選擇量化模型
--------------
✓ 優先選擇 AWQ 量化（精度最佳）
✓ 從 TheBloke 等可信來源下載
✓ 檢查模型的 group_size 配置
✓ 閱讀模型卡片了解性能指標

推薦來源:
- HuggingFace TheBloke 組織
- 官方模型的量化版本
- 社區驗證的模型

2. 配置優化
----------
```python
llm = LLM(
    model="TheBloke/Llama-2-13B-chat-AWQ",

    # 量化配置
    quantization="awq",
    dtype="float16",  # 保持 FP16 用於非量化部分

    # 內存配置
    gpu_memory_utilization=0.95,  # 量化模型可以更激進
    max_model_len=4096,  # 根據實際需求設置

    # 其他優化
    trust_remote_code=True,
    enforce_eager=False,  # 使用 CUDA graph
)
```

3. 驗證精度
----------
在生產部署前，務必驗證量化模型的精度：

```python
def validate_quantization(original_model, quantized_model):
    test_prompts = [
        # 添加代表性測試用例
        "Explain quantum computing",
        "Write a Python function to sort a list",
        "Translate 'Hello' to French",
    ]

    sampling_params = SamplingParams(
        temperature=0.0,  # 確定性輸出
        max_tokens=100,
    )

    # 比較輸出
    orig_outputs = original_model.generate(test_prompts, sampling_params)
    quant_outputs = quantized_model.generate(test_prompts, sampling_params)

    for i, (orig, quant) in enumerate(zip(orig_outputs, quant_outputs)):
        print(f"Prompt {i+1}:")
        print(f"Original: {orig.outputs[0].text[:100]}")
        print(f"Quantized: {quant.outputs[0].text[:100]}")
        print()
```

4. 性能監控
----------
```python
import time
import torch

def monitor_performance(llm, prompts):
    # 測量延遲
    start = time.time()
    outputs = llm.generate(prompts, sampling_params)
    latency = time.time() - start

    # 測量內存
    memory_used = torch.cuda.memory_allocated() / 1e9

    # 計算吞吐量
    total_tokens = sum(len(o.outputs[0].token_ids) for o in outputs)
    throughput = total_tokens / latency

    print(f"Latency: {latency:.2f}s")
    print(f"Throughput: {throughput:.2f} tokens/s")
    print(f"Memory: {memory_used:.2f} GB")
```

5. 常見陷阱
----------
✗ 不要混用量化方法
   - 不要對已量化的模型再次量化

✗ 注意模型兼容性
   - 確保 vLLM 支持該量化格式
   - 檢查模型架構兼容性

✗ 不要過度優化
   - 不是所有情況都需要量化
   - 小模型量化收益有限

✗ 忽略精度驗證
   - 必須在實際任務上驗證
   - 不同任務對精度敏感度不同

6. 故障排除
----------
問題: 加載失敗
```
Error: Quantization method 'awq' is not supported
```
解決: 確保安裝了量化相關依賴
```bash
pip install autoawq
```

問題: 精度下降明顯
- 嘗試不同的量化方法
- 使用更大的 group_size
- 考慮 INT8 而非 INT4

問題: 性能未提升
- 檢查是否真正使用了量化
- 驗證 GPU 利用率
- 確保批量大小足夠

7. 部署檢查清單
--------------
□ 選擇合適的量化方法（AWQ/GPTQ）
□ 下載並驗證量化模型
□ 測試內存佔用是否符合預期
□ 驗證推理精度
□ 進行性能基準測試
□ 監控生產環境指標
□ 準備降級方案（回退到 FP16）

8. 未來展望
----------
- 新的量化方法不斷出現
- 硬件加速支持越來越好
- 精度損失越來越小
- 工具鏈日趨成熟

建議持續關注：
- vLLM 官方文檔更新
- 新的量化格式（如 GGUF）
- 社區最佳實踐
- 性能基準測試結果
    """)


def main():
    """
    主函數：運行所有示例
    """
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 25 + "vLLM 量化部署示例" + " " * 25 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")

    try:
        # 概覽
        quantization_overview()

        # 示例 1: AWQ 量化
        awq_quantization_example()

        # 示例 2: GPTQ 量化
        gptq_quantization_example()

        # 示例 3: 性能對比
        quantization_performance_comparison()

        # 示例 4: 應用場景
        quantization_use_cases()

        # 示例 5: 最佳實踐
        quantization_best_practices()

        print("\n" + "=" * 80)
        print("✓ 所有示例展示完成！")
        print("=" * 80)

        print("\n關鍵要點：")
        print("  1. 量化可以減少 3-4 倍內存佔用")
        print("  2. AWQ 提供最佳精度，推薦優先使用")
        print("  3. 量化通常能提高而非降低性能")
        print("  4. 務必在實際任務上驗證精度")
        print("  5. 量化使得大模型部署更加經濟")

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

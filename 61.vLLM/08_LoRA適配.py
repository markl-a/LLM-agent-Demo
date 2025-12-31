#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
vLLM LoRA 適配示例
==================

本示例展示如何在 vLLM 中使用 LoRA 適配器，包括：
1. LoRA 基礎概念
2. 加載單個 LoRA 適配器
3. 動態加載多個 LoRA 適配器
4. LoRA 適配器切換
5. LoRA 與基礎模型對比
6. 實際應用場景

LoRA (Low-Rank Adaptation) 允許：
- 低成本微調大型模型
- 多個適配器共享基礎模型
- 動態切換不同的任務適配器
- 減少部署成本

適用場景：
- 多任務模型服務
- 個性化模型
- 領域專用模型
- A/B 測試
"""

import sys
from typing import List, Dict
from vllm import LLM, SamplingParams


def lora_overview():
    """
    LoRA 技術概覽

    介紹 LoRA 的基本概念和優勢
    """
    print("=" * 80)
    print("LoRA 技術概覽")
    print("=" * 80)

    print("""
什麼是 LoRA？
------------
LoRA (Low-Rank Adaptation) 是一種參數高效的微調方法。
不直接修改原始模型參數，而是添加小型適配器層。

核心概念：
- 基礎模型: 保持凍結，不修改
- LoRA 適配器: 小型可訓練參數（通常 < 1% 模型大小）
- 推理時: 基礎模型 + 適配器 = 專用模型

LoRA 的優勢：
-------------
1. 參數效率
   ✓ 適配器只有基礎模型的 0.1-1%
   ✓ 7B 模型的 LoRA 通常只有 10-100MB
   ✓ 易於存儲和傳輸

2. 訓練效率
   ✓ 訓練速度快（只訓練少量參數）
   ✓ 顯存需求低
   ✓ 成本低廉

3. 部署優勢
   ✓ 一個基礎模型 + 多個適配器
   ✓ 動態加載不同適配器
   ✓ 節省 GPU 內存
   ✓ 快速切換任務

4. 靈活性
   ✓ 支持多任務學習
   ✓ 個性化定制
   ✓ A/B 測試
   ✓ 增量更新

vLLM 的 LoRA 支持：
------------------
✓ 動態加載多個 LoRA 適配器
✓ 批量處理時混合使用不同適配器
✓ 零開銷切換（共享基礎模型）
✓ 支持主流 LoRA 格式

應用場景：
---------
1. 多任務 API 服務
   - 單個部署支持多個任務
   - 根據請求選擇適配器

2. 個性化服務
   - 每個用戶/企業一個適配器
   - 保護隱私的同時共享基礎設施

3. 領域專用模型
   - 醫療、法律、金融等專業適配器
   - 快速切換專業領域

4. 實驗和 A/B 測試
   - 同時測試多個模型版本
   - 快速比較效果

示例架構：
---------
┌─────────────────────────────────────┐
│      基礎模型 (Llama-2-7B)           │
│         (保持凍結)                    │
└─────────────────────────────────────┘
           ↓         ↓         ↓
    ┌──────────┐ ┌──────────┐ ┌──────────┐
    │ LoRA 1   │ │ LoRA 2   │ │ LoRA 3   │
    │  醫療    │ │  法律    │ │  金融    │
    │  10MB    │ │  12MB    │ │  15MB    │
    └──────────┘ └──────────┘ └──────────┘

vs. 傳統方案：
┌──────────┐ ┌──────────┐ ┌──────────┐
│ 完整模型 1│ │ 完整模型 2│ │ 完整模型 3│
│  14GB    │ │  14GB    │ │  14GB    │
└──────────┘ └──────────┘ └──────────┘

節省: 14GB × 3 - (14GB + 37MB) ≈ 28GB
    """)


def single_lora_example():
    """
    單個 LoRA 適配器示例

    展示如何加載和使用單個 LoRA 適配器
    """
    print("\n" + "=" * 80)
    print("示例 1: 加載單個 LoRA 適配器")
    print("=" * 80)

    print("""
使用 LoRA 適配器：
-----------------

1. 準備 LoRA 模型
   可以從 HuggingFace 下載已訓練的 LoRA，或自己訓練

2. 常見 LoRA 資源:
   - tloen/alpaca-lora-7b (Alpaca 指令微調)
   - various Chinese LoRA models
   - domain-specific LoRAs

3. 基本用法：

```python
from vllm import LLM, SamplingParams
from vllm.lora.request import LoRARequest

# 加載基礎模型
llm = LLM(
    model="meta-llama/Llama-2-7b-hf",
    enable_lora=True,  # 啟用 LoRA 支持
    max_loras=1,  # 最大同時加載的 LoRA 數量
    max_lora_rank=64,  # LoRA rank 上限
)

# 創建 LoRA 請求
lora_request = LoRARequest(
    lora_name="alpaca",
    lora_int_id=1,
    lora_path="/path/to/alpaca-lora"
)

# 使用 LoRA 生成
outputs = llm.generate(
    prompts,
    sampling_params,
    lora_request=lora_request  # 指定使用的 LoRA
)
```

注意事項：
---------
⚠ vLLM 的 LoRA 支持仍在快速發展
⚠ 需要確保基礎模型與 LoRA 適配器兼容
⚠ LoRA rank 需要匹配
⚠ 某些模型可能不支持 LoRA
    """)

    try:
        print("\n概念演示（需要實際的 LoRA 模型）:")
        print("-" * 80)

        # 這裡只是展示代碼結構，實際運行需要真實的 LoRA 模型
        print("""
# 1. 加載基礎模型並啟用 LoRA
llm = LLM(
    model="meta-llama/Llama-2-7b-hf",
    enable_lora=True,
    max_loras=1,
)

# 2. 準備 LoRA 適配器
from vllm.lora.request import LoRARequest

lora_request = LoRARequest(
    lora_name="my-lora",
    lora_int_id=1,
    lora_path="./my-lora-adapter"
)

# 3. 使用 LoRA 進行推理
sampling_params = SamplingParams(temperature=0.7, max_tokens=100)
outputs = llm.generate(
    ["Explain quantum computing"],
    sampling_params,
    lora_request=lora_request
)

print(outputs[0].outputs[0].text)
        """)

    except Exception as e:
        print(f"\n✗ 錯誤: {str(e)}")


def multiple_lora_example():
    """
    多個 LoRA 適配器示例

    展示如何動態加載和切換多個 LoRA 適配器
    """
    print("\n" + "=" * 80)
    print("示例 2: 動態加載多個 LoRA 適配器")
    print("=" * 80)

    print("""
多 LoRA 架構：
-------------

vLLM 支持在同一批次中使用不同的 LoRA 適配器，
這是其獨特的優勢之一。

配置示例：
```python
from vllm import LLM
from vllm.lora.request import LoRARequest

# 啟用多 LoRA 支持
llm = LLM(
    model="meta-llama/Llama-2-7b-hf",
    enable_lora=True,
    max_loras=4,  # 同時支持最多 4 個 LoRA
    max_lora_rank=64,
    max_cpu_loras=10,  # CPU 上可以緩存更多 LoRA
)

# 定義多個 LoRA 適配器
lora_medical = LoRARequest("medical", 1, "./lora-medical")
lora_legal = LoRARequest("legal", 2, "./lora-legal")
lora_finance = LoRARequest("finance", 3, "./lora-finance")

# 批量處理時使用不同的 LoRA
prompts = [
    "Explain this medical condition:",  # 使用 medical LoRA
    "Interpret this legal clause:",     # 使用 legal LoRA
    "Analyze this financial report:",   # 使用 finance LoRA
]

# 為每個請求指定對應的 LoRA
# 注意：當前 vLLM 版本可能需要特殊 API 來支持
```

性能優勢：
---------
1. 內存效率
   基礎模型: 14GB (只加載一次)
   LoRA 1:   10MB
   LoRA 2:   12MB
   LoRA 3:   15MB
   總計:     ~14.04GB

   vs. 3個完整模型: 42GB
   節省: 66%

2. 切換速度
   ✓ LoRA 切換: < 1ms (已在 GPU 上)
   ✓ 從 CPU 加載: ~100ms
   ✗ 切換完整模型: 數秒

3. 吞吐量
   ✓ 批量處理可以混合不同 LoRA
   ✓ 高效利用 GPU
   ✓ 無切換開銷

實際應用架構：
------------

API 服務器:
```python
from fastapi import FastAPI
from vllm import LLM
from vllm.lora.request import LoRARequest

app = FastAPI()

# 初始化 vLLM
llm = LLM(
    model="meta-llama/Llama-2-7b-hf",
    enable_lora=True,
    max_loras=10,
)

# LoRA 註冊表
loras = {
    "medical": LoRARequest("medical", 1, "./loras/medical"),
    "legal": LoRARequest("legal", 2, "./loras/legal"),
    "finance": LoRARequest("finance", 3, "./loras/finance"),
}

@app.post("/generate")
async def generate(
    prompt: str,
    task: str = "general"  # medical, legal, finance, general
):
    lora = loras.get(task)  # None for general (base model)

    outputs = llm.generate(
        [prompt],
        sampling_params,
        lora_request=lora
    )

    return {"text": outputs[0].outputs[0].text}
```

客戶端調用:
```python
import requests

# 使用醫療 LoRA
response = requests.post("http://localhost:8000/generate", json={
    "prompt": "What is hypertension?",
    "task": "medical"
})

# 使用法律 LoRA
response = requests.post("http://localhost:8000/generate", json={
    "prompt": "Explain contract law",
    "task": "legal"
})

# 使用基礎模型（無 LoRA）
response = requests.post("http://localhost:8000/generate", json={
    "prompt": "Tell me a story",
    "task": "general"
})
```
    """)


def lora_vs_base_comparison():
    """
    LoRA 與基礎模型對比

    展示 LoRA 適配後的效果差異
    """
    print("\n" + "=" * 80)
    print("示例 3: LoRA vs 基礎模型對比")
    print("=" * 80)

    print("""
對比測試框架：
------------

```python
from vllm import LLM, SamplingParams
from vllm.lora.request import LoRARequest

# 加載模型
llm = LLM(
    model="meta-llama/Llama-2-7b-hf",
    enable_lora=True,
)

# 準備 LoRA
lora_request = LoRARequest("instruct", 1, "./alpaca-lora")

# 測試提示詞
prompts = [
    "Explain machine learning in simple terms",
    "Write a Python function to calculate fibonacci",
    "What are the health benefits of exercise?",
]

sampling_params = SamplingParams(temperature=0.7, max_tokens=200)

# 基礎模型輸出
print("=== 基礎模型 ===")
base_outputs = llm.generate(prompts, sampling_params)
for i, output in enumerate(base_outputs):
    print(f"\nPrompt {i+1}: {output.prompt}")
    print(f"Base: {output.outputs[0].text}")

# LoRA 適配模型輸出
print("\n=== LoRA 適配模型 ===")
lora_outputs = llm.generate(
    prompts,
    sampling_params,
    lora_request=lora_request
)
for i, output in enumerate(lora_outputs):
    print(f"\nPrompt {i+1}: {output.prompt}")
    print(f"LoRA: {output.outputs[0].text}")
```

典型差異（示例）：
----------------

提示: "Explain photosynthesis"

基礎模型 (Llama-2-7b):
"Photosynthesis is a process. Plants use sunlight. This happens in
leaves. It's important for life on Earth..."
[可能較冗長、結構鬆散]

Instruct LoRA (Alpaca):
"Photosynthesis is the process by which plants convert light energy
into chemical energy. Here's how it works:

1. Light absorption: Chlorophyll captures sunlight
2. Water splitting: H2O is broken down
3. Carbon fixation: CO2 is converted to glucose
4. Oxygen release: O2 is produced as byproduct

This process is essential for..."
[更結構化、更清晰、更適合問答]

醫療 LoRA:
"Photosynthesis is a biochemical process in plant cells where...
[From a biological perspective]...
Clinical relevance: Understanding photosynthesis helps in..."
[專業術語、領域視角]

觀察要點：
---------
1. 格式化程度
   - 基礎模型: 自由文本
   - Instruct LoRA: 有序列表、清晰結構
   - 專業 LoRA: 領域術語

2. 響應質量
   - 準確性
   - 完整性
   - 可讀性

3. 任務適應性
   - 基礎模型: 通用
   - LoRA: 針對特定任務優化
    """)


def lora_performance_optimization():
    """
    LoRA 性能優化

    展示如何優化 LoRA 的性能
    """
    print("\n" + "=" * 80)
    print("示例 4: LoRA 性能優化")
    print("=" * 80)

    print("""
優化配置：
---------

1. 內存優化
```python
llm = LLM(
    model="meta-llama/Llama-2-7b-hf",
    enable_lora=True,

    # LoRA 配置
    max_loras=8,  # GPU 上同時加載的 LoRA 數量
    max_lora_rank=64,  # 支持的最大 rank

    # CPU 緩存
    max_cpu_loras=20,  # CPU 上緩存更多 LoRA

    # 內存管理
    gpu_memory_utilization=0.9,
)
```

2. 性能參數
- max_loras: 越大越靈活，但佔用更多 GPU 內存
- max_lora_rank: 設置為實際 LoRA rank 的最大值
- max_cpu_loras: 頻繁切換時設置更大

3. 批處理策略
```python
# 將相同 LoRA 的請求分組
requests_by_lora = {
    "medical": [...],
    "legal": [...],
    "finance": [...],
}

# 分批處理
for lora_name, prompts in requests_by_lora.items():
    lora_request = loras[lora_name]
    outputs = llm.generate(
        prompts,
        sampling_params,
        lora_request=lora_request
    )
```

4. 預熱策略
```python
# 應用啟動時預加載常用 LoRA
def warmup_loras(llm, lora_requests):
    dummy_prompt = ["warmup"]
    dummy_params = SamplingParams(max_tokens=1)

    for lora in lora_requests:
        llm.generate(
            dummy_prompt,
            dummy_params,
            lora_request=lora
        )
```

性能基準（示例）：
----------------

配置: Llama-2-7B + 3個 LoRA，A100 GPU

| 指標 | 基礎模型 | +1 LoRA | +3 LoRA |
|------|----------|---------|---------|
| GPU 內存 | 14 GB | 14.01 GB | 14.04 GB |
| 首次推理 | 50ms | 55ms | 60ms |
| 後續推理 | 50ms | 50ms | 50ms |
| 吞吐量 | 2000 tok/s | 1980 tok/s | 1950 tok/s |

結論：
- LoRA 對內存影響極小
- 首次加載有輕微延遲
- 穩定狀態性能幾乎無損

監控指標：
---------
```python
import torch

def monitor_lora_performance(llm):
    # GPU 內存
    memory_allocated = torch.cuda.memory_allocated() / 1e9
    print(f"GPU Memory: {memory_allocated:.2f} GB")

    # LoRA 統計
    # 注意: 需要 vLLM 提供相應 API
    print(f"Active LoRAs: {llm.get_active_lora_count()}")
    print(f"Cached LoRAs: {llm.get_cached_lora_count()}")
```

故障排除：
---------

問題 1: LoRA 加載失敗
```
Error: LoRA rank mismatch
```
解決: 檢查 max_lora_rank 設置
```python
llm = LLM(
    model="...",
    enable_lora=True,
    max_lora_rank=128,  # 增加到匹配 LoRA rank
)
```

問題 2: 內存不足
```
CUDA out of memory with LoRA
```
解決: 減少 max_loras 或使用量化
```python
llm = LLM(
    model="...",
    enable_lora=True,
    max_loras=2,  # 減少同時加載的 LoRA
    gpu_memory_utilization=0.85,
)
```

問題 3: 性能下降
原因: 頻繁切換 LoRA
解決: 批量處理相同 LoRA 的請求
    """)


def lora_best_practices():
    """
    LoRA 最佳實踐

    分享 LoRA 使用的建議和技巧
    """
    print("\n" + "=" * 80)
    print("示例 5: LoRA 最佳實踐")
    print("=" * 80)

    print("""
1. 選擇基礎模型
--------------
✓ 選擇社區活躍的模型（如 Llama、Mistral）
✓ 確保模型支持 LoRA
✓ 優先選擇指令微調版本作為基礎

推薦基礎模型:
- meta-llama/Llama-2-7b-chat-hf
- meta-llama/Llama-2-13b-chat-hf
- mistralai/Mistral-7B-Instruct-v0.1

2. 訓練 LoRA
-----------
使用 PEFT 庫訓練:

```python
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM

# 加載基礎模型
base_model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf"
)

# 配置 LoRA
lora_config = LoraConfig(
    r=16,  # rank
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

# 創建 LoRA 模型
model = get_peft_model(base_model, lora_config)

# 訓練...
# trainer.train()

# 保存 LoRA 適配器
model.save_pretrained("./my-lora")
```

3. 組織 LoRA 文件
----------------
推薦結構:
```
lora_adapters/
├── medical/
│   ├── adapter_config.json
│   └── adapter_model.bin
├── legal/
│   ├── adapter_config.json
│   └── adapter_model.bin
└── finance/
    ├── adapter_config.json
    └── adapter_model.bin
```

4. 版本管理
----------
✓ 使用 Git LFS 管理 LoRA 文件
✓ 標記版本號和訓練日期
✓ 記錄訓練數據和參數
✓ 保存性能基準

5. 測試和驗證
------------
```python
def validate_lora(llm, lora_request, test_cases):
    """驗證 LoRA 質量"""
    results = []

    for prompt, expected in test_cases:
        output = llm.generate(
            [prompt],
            sampling_params,
            lora_request=lora_request
        )

        result = {
            "prompt": prompt,
            "expected": expected,
            "actual": output[0].outputs[0].text,
            "score": evaluate(expected, output[0].outputs[0].text)
        }
        results.append(result)

    return results
```

6. 部署策略
----------

場景 A: 固定任務集
```python
# 預加載所有 LoRA
llm = LLM(
    model="...",
    enable_lora=True,
    max_loras=5,  # 固定數量
)

# 註冊所有 LoRA
all_loras = {
    "medical": LoRARequest("medical", 1, "./loras/medical"),
    "legal": LoRARequest("legal", 2, "./loras/legal"),
    # ...
}
```

場景 B: 動態任務
```python
# 支持更多 LoRA，使用 CPU 緩存
llm = LLM(
    model="...",
    enable_lora=True,
    max_loras=3,  # GPU 上少量
    max_cpu_loras=20,  # CPU 緩存更多
)
```

7. 監控和維護
------------
✓ 跟踪每個 LoRA 的使用頻率
✓ 監控性能指標
✓ 定期評估質量
✓ 淘汰低質量或低使用率的 LoRA

8. 安全考慮
----------
✓ 驗證 LoRA 文件來源
✓ 掃描惡意代碼
✓ 隔離不同來源的 LoRA
✓ 實施訪問控制

9. 成本優化
----------

vs. 多模型部署:

多模型方案:
- 3個完整模型
- 每個 14GB
- 總計 42GB
- 需要 3個 GPU 或分時加載

LoRA 方案:
- 1個基礎模型: 14GB
- 3個 LoRA: 0.04GB
- 總計: 14.04GB
- 只需 1個 GPU
- 成本節省: 66%

10. 未來展望
-----------
- QLoRA: 量化 + LoRA
- 更高效的適配器架構
- 自動化 LoRA 選擇
- LoRA 組合（多個 LoRA 疊加）
    """)


def main():
    """
    主函數：運行所有示例
    """
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 25 + "vLLM LoRA 適配示例" + " " * 25 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")

    try:
        # 概覽
        lora_overview()

        # 示例 1: 單個 LoRA
        single_lora_example()

        # 示例 2: 多個 LoRA
        multiple_lora_example()

        # 示例 3: 對比測試
        lora_vs_base_comparison()

        # 示例 4: 性能優化
        lora_performance_optimization()

        # 示例 5: 最佳實踐
        lora_best_practices()

        print("\n" + "=" * 80)
        print("✓ 所有示例展示完成！")
        print("=" * 80)

        print("\n關鍵要點：")
        print("  1. LoRA 實現低成本的模型定制")
        print("  2. 一個基礎模型可以支持多個任務")
        print("  3. 動態加載 LoRA 無切換開銷")
        print("  4. vLLM 的多 LoRA 支持是獨特優勢")
        print("  5. 適合多任務和個性化服務場景")

        print("\n注意事項：")
        print("  - vLLM 的 LoRA 功能仍在快速發展")
        print("  - 需要使用實際的 LoRA 適配器文件測試")
        print("  - 確保基礎模型與 LoRA 兼容")
        print("  - 參考官方文檔獲取最新信息")

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

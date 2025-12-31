"""
PEFT 模型合併技術

這個文件介紹適配器合併的各種技術，包括：
1. 基礎合併（merge_and_unload）
2. 多適配器合併
3. 任務向量（Task Vectors）
4. 模型湯（Model Soups）
5. 合併策略和權重

適配器合併可以提升推理速度，簡化部署。
"""

import warnings
warnings.filterwarnings('ignore')


def explain_model_merging():
    """
    解釋模型合併的概念
    """
    print("=" * 70)
    print("模型合併概念")
    print("=" * 70)

    print("""
為什麼要合併？

1. LoRA 的工作方式：
   原始: h = W × x
   LoRA: h = W × x + B × A × x = (W + BA) × x

   推理時有兩種選擇：
   a) 分開計算 W × x 和 BA × x，然後相加（慢）
   b) 先合併 W' = W + BA，然後計算 W' × x（快）

2. 合併的優勢：

   性能：
   ┌────────────────┬──────────────┬──────────────┐
   │ 方式           │ 推理速度     │ 顯存占用     │
   ├────────────────┼──────────────┼──────────────┤
   │ 未合併         │ 慢（兩次計算)│ W + BA       │
   │ 合併後         │ 快（一次計算)│ W'           │
   │ 加速比         │ 1.2-1.5x     │ 相同         │
   └────────────────┴──────────────┴──────────────┘

   部署：
   • 合併後就是普通模型，無需 PEFT 庫
   • 簡化部署流程
   • 兼容性更好

3. 何時合併：
   ✓ 推理部署時
   ✓ 不需要切換適配器時
   ✓ 追求最佳性能時

4. 何時不合併：
   ✗ 需要動態切換適配器
   ✗ 需要保留適配器的模塊化
   ✗ 多任務場景
    """)


def basic_merge():
    """
    基礎合併方法
    """
    print("\n" + "=" * 70)
    print("基礎合併方法")
    print("=" * 70)

    print("""
方法 1：merge_and_unload（推薦）

```python
from transformers import AutoModelForCausalLM
from peft import PeftModel

# 1. 加載基礎模型
base_model = AutoModelForCausalLM.from_pretrained("gpt2")

# 2. 加載 PEFT 模型
peft_model = PeftModel.from_pretrained(base_model, "./lora_adapter")

# 3. 合併適配器
merged_model = peft_model.merge_and_unload()

# 4. 現在 merged_model 是一個普通的 transformers 模型
# 可以像使用原始模型一樣使用

# 5. 保存合併後的模型
merged_model.save_pretrained("./merged_model")
tokenizer.save_pretrained("./merged_model")

# 6. 加載和使用（不需要 PEFT）
from transformers import AutoModelForCausalLM
model = AutoModelForCausalLM.from_pretrained("./merged_model")
```

方法 2：手動合併（更底層）

```python
import torch

# 獲取 LoRA 權重
lora_A = peft_model.base_model.model.transformer.h[0].attn.c_attn.lora_A
lora_B = peft_model.base_model.model.transformer.h[0].attn.c_attn.lora_B

# 計算 delta_W
delta_W = lora_B.weight @ lora_A.weight

# 獲取原始權重
original_W = peft_model.base_model.model.transformer.h[0].attn.c_attn.weight

# 合併
merged_W = original_W + delta_W

# 更新權重
peft_model.base_model.model.transformer.h[0].attn.c_attn.weight.data = merged_W
```

方法 3：選擇性合併

```python
# 只合併某些層
# PEFT 目前不直接支持，但可以手動實現
for layer_idx in [0, 1, 2]:  # 只合併前 3 層
    layer = peft_model.base_model.model.transformer.h[layer_idx]
    # 合併這一層的 LoRA
    ...
```
    """)


def multi_adapter_merging():
    """
    多適配器合併
    """
    print("\n" + "=" * 70)
    print("多適配器合併")
    print("=" * 70)

    print("""
場景：有多個任務的適配器，想要合併它們

方法 1：簡單平均

```python
import torch
from transformers import AutoModelForCausalLM
from peft import PeftModel

base_model = AutoModelForCausalLM.from_pretrained("gpt2")

# 加載多個適配器並合併
adapters = ["./task1", "./task2", "./task3"]
weights = [0.33, 0.33, 0.34]  # 權重（可調整）

# 初始化合併後的權重
merged_state_dict = base_model.state_dict().copy()

for adapter_path, weight in zip(adapters, weights):
    # 加載適配器
    model = PeftModel.from_pretrained(base_model, adapter_path)
    model = model.merge_and_unload()

    # 加權平均
    adapter_state_dict = model.state_dict()
    for key in merged_state_dict.keys():
        if key in adapter_state_dict:
            merged_state_dict[key] += weight * (
                adapter_state_dict[key] - base_model.state_dict()[key]
            )

# 加載合併的權重
base_model.load_state_dict(merged_state_dict)
```

方法 2：任務向量合併

```python
# 計算任務向量
task_vectors = []

for adapter_path in adapters:
    model = PeftModel.from_pretrained(base_model, adapter_path)
    model = model.merge_and_unload()

    # 任務向量 = 微調後 - 原始
    task_vector = {}
    for key in model.state_dict().keys():
        task_vector[key] = (
            model.state_dict()[key] - base_model.state_dict()[key]
        )
    task_vectors.append(task_vector)

# 合併任務向量
combined_vector = {}
for key in task_vectors[0].keys():
    combined_vector[key] = sum(
        weight * tv[key] for weight, tv in zip(weights, task_vectors)
    )

# 應用到基礎模型
final_state_dict = base_model.state_dict().copy()
for key in combined_vector.keys():
    final_state_dict[key] += combined_vector[key]

base_model.load_state_dict(final_state_dict)
```
    """)


def task_vectors():
    """
    任務向量技術
    """
    print("\n" + "=" * 70)
    print("任務向量（Task Vectors）")
    print("=" * 70)

    print("""
任務向量的概念：

1. 定義：
   τ = θ_finetuned - θ_pretrained

   任務向量代表了為完成某個任務所需的權重變化

2. 性質：
   • 可以縮放: α × τ
   • 可以相加: τ₁ + τ₂
   • 可以相減: τ₁ - τ₂
   • 可以否定: -τ

3. 操作示例：

```python
# 假設我們有翻譯和摘要兩個任務向量

# 增強翻譯能力
enhanced_translation = base_weights + 1.5 * translation_vector

# 組合兩個任務
multi_task = base_weights + 0.5 * translation_vector + 0.5 * summary_vector

# 移除不想要的能力
cleaned_model = finetuned_weights - unwanted_task_vector
```

4. 實際應用：

a) 任務算術（Task Arithmetic）：
```python
# 增強特定能力
model = base + 2.0 * math_task_vector

# 中和負面能力
model = base + helpful_vector - harmful_vector
```

b) 模型編輯：
```python
# 更新過時的知識
model = current_model + new_knowledge_vector - old_knowledge_vector
```

c) 負向提示（Negative Prompting）：
```python
# 避免某種風格
model = base + desired_style - undesired_style
```

5. 最佳實踐：
   • 任務向量最好來自相同的基礎模型
   • 縮放因子通常在 0.5-2.0 之間
   • 需要在驗證集上調優權重
   • 可以用於快速實驗和探索
    """)


def model_soups():
    """
    模型湯技術
    """
    print("\n" + "=" * 70)
    print("模型湯（Model Soups）")
    print("=" * 70)

    print("""
模型湯的概念：

1. 基本思想：
   • 用不同超參數訓練同一任務的多個模型
   • 將這些模型的權重平均
   • 通常性能比單個模型更好

2. 為什麼有效：
   • 集成效應（ensemble）
   • 平滑損失landscape
   • 減少過擬合
   • 提高泛化能力

3. 實現：

```python
from transformers import AutoModelForCausalLM
from peft import PeftModel

base_model = AutoModelForCausalLM.from_pretrained("gpt2")

# 訓練多個 LoRA 適配器（不同超參數）
adapters = {
    "./lora_lr1e-4": 1.0,
    "./lora_lr3e-4": 1.0,
    "./lora_lr5e-4": 1.0,
}

# 均勻湯（Uniform Soup）
weights = [1/len(adapters)] * len(adapters)

# 貪婪湯（Greedy Soup）- 選擇性添加
# 1. 從最佳模型開始
# 2. 依次嘗試添加其他模型
# 3. 如果性能提升則保留，否則丟棄

def create_model_soup(base_model, adapters, weights):
    '''創建模型湯'''
    # 初始化
    soup_state_dict = {
        k: torch.zeros_like(v)
        for k, v in base_model.state_dict().items()
    }

    # 加權平均
    for adapter_path, weight in zip(adapters.keys(), weights):
        model = PeftModel.from_pretrained(base_model, adapter_path)
        model = model.merge_and_unload()

        for key, param in model.state_dict().items():
            soup_state_dict[key] += weight * param

    # 加載湯
    base_model.load_state_dict(soup_state_dict)
    return base_model

# 創建湯
soup_model = create_model_soup(base_model, adapters, weights)
```

4. 變體：

a) 均勻湯：
   所有模型權重相同（1/N）

b) 貪婪湯：
   選擇性添加提升性能的模型

c) 加權湯：
   根據驗證集性能分配權重

5. 實驗建議：
   • 至少使用 3-5 個模型
   • 變化一些超參數（學習率、dropout、batch size）
   • 在驗證集上評估
   • 通常比單個模型好 1-3%
    """)


def merging_strategies():
    """
    合併策略
    """
    print("\n" + "=" * 70)
    print("高級合併策略")
    print("=" * 70)

    strategies = {
        "線性插值（Linear Interpolation）": {
            "公式": "θ = (1-α)θ₀ + αθ₁",
            "用途": "在兩個模型間平滑過渡",
            "優點": "簡單，可控",
            "參數": "α ∈ [0, 1]"
        },
        "球面線性插值（SLERP）": {
            "公式": "θ = sin((1-α)Ω)/sin(Ω)·θ₀ + sin(αΩ)/sin(Ω)·θ₁",
            "用途": "保持向量長度的插值",
            "優點": "幾何上更優",
            "參數": "α ∈ [0, 1], Ω是夾角"
        },
        "任務算術（Task Arithmetic）": {
            "公式": "θ = θ₀ + Σᵢ λᵢτᵢ",
            "用途": "組合多個任務向量",
            "優點": "靈活，可解釋",
            "參數": "λᵢ 是縮放因子"
        },
        "TIES合併（TIES-Merging）": {
            "公式": "保留重要參數，平均其他",
            "用途": "減少任務沖突",
            "優點": "性能更好",
            "參數": "修剪閾值，保留比例"
        },
        "DARE合併": {
            "公式": "隨機丟棄部分delta",
            "用途": "減少干擾",
            "優點": "提升泛化",
            "參數": "丟棄率"
        },
    }

    for strategy, details in strategies.items():
        print(f"\n【{strategy}】")
        for key, value in details.items():
            print(f"  {key}: {value}")


def practical_tips():
    """
    實用技巧
    """
    print("\n" + "=" * 70)
    print("實用技巧")
    print("=" * 70)

    print("""
1. 合併前的檢查：
   ```python
   # 確保適配器和基礎模型匹配
   assert peft_model.base_model_name == base_model_name

   # 檢查配置
   print(peft_model.peft_config)
   ```

2. 驗證合併效果：
   ```python
   # 合併前後對比
   inputs = tokenizer("Test prompt", return_tensors="pt")

   with torch.no_grad():
       output_before = peft_model.generate(**inputs)
       output_after = merged_model.generate(**inputs)

   # 應該完全一致（數值誤差在可接受範圍內）
   assert torch.allclose(output_before, output_after, rtol=1e-5)
   ```

3. 保存和加載：
   ```python
   # 保存合併後的模型
   merged_model.save_pretrained(
       "./merged_model",
       safe_serialization=True  # 使用 safetensors
   )

   # 加載（不需要 PEFT 庫）
   from transformers import AutoModelForCausalLM
   model = AutoModelForCausalLM.from_pretrained("./merged_model")
   ```

4. 量化合併後的模型：
   ```python
   # 先合併，再量化
   merged_model = peft_model.merge_and_unload()

   # 使用 bitsandbytes 量化
   from transformers import BitsAndBytesConfig

   quantization_config = BitsAndBytesConfig(load_in_8bit=True)
   quantized_model = AutoModelForCausalLM.from_pretrained(
       "./merged_model",
       quantization_config=quantization_config
   )
   ```

5. 避免的錯誤：
   • 不要在不同基礎模型的適配器間合併
   • 合併後再訓練可能不穩定
   • 檢查數值精度（float32 vs float16）
   • 大規模合併注意顯存
    """)


def main():
    """
    主函數：模型合併完整教程
    """
    print("=" * 70)
    print("PEFT 模型合併完整指南")
    print("=" * 70)

    # 1. 概念講解
    explain_model_merging()

    # 2. 基礎合併
    basic_merge()

    # 3. 多適配器合併
    multi_adapter_merging()

    # 4. 任務向量
    task_vectors()

    # 5. 模型湯
    model_soups()

    # 6. 合併策略
    merging_strategies()

    # 7. 實用技巧
    practical_tips()

    # 8. 總結
    print("\n" + "=" * 70)
    print("總結")
    print("=" * 70)
    print("""
模型合併的關鍵要點：

1. 基礎合併（merge_and_unload）：
   • 最簡單，最常用
   • 提升推理速度 20-50%
   • 簡化部署

2. 多適配器合併：
   • 任務向量：靈活的算術運算
   • 模型湯：集成多個模型
   • 權重調優：在驗證集上找最佳權重

3. 何時合併：
   ✓ 生產部署
   ✓ 單一任務
   ✓ 追求性能

4. 何時不合併：
   ✗ 多任務切換
   ✗ 需要模塊化
   ✗ 頻繁更新適配器

5. 高級技術：
   • 任務算術：組合能力
   • 模型湯：提升泛化
   • TIES/DARE：減少衝突
    """)

    print("\n下一步:")
    print("  • 查看 09_推理優化.py - 優化推理性能")
    print("  • 查看 10_生產部署.py - 生產環境部署")

    print("\n資源:")
    print("  • Task Vectors 論文: https://arxiv.org/abs/2212.04089")
    print("  • Model Soups 論文: https://arxiv.org/abs/2203.05482")
    print("  • TIES-Merging 論文: https://arxiv.org/abs/2306.01708")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用戶中斷")
    except Exception as e:
        print(f"\n程序執行出錯: {e}")
        import traceback
        traceback.print_exc()

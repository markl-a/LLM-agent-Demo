"""
Prefix Tuning 前綴調優

這個文件介紹 Prefix Tuning 方法，包括：
1. Prefix Tuning 原理
2. 與 LoRA 的對比
3. 配置和使用
4. 適用場景
5. 性能分析

Prefix Tuning 通過在輸入前添加可訓練的前綴向量來適配模型。
"""

import warnings
warnings.filterwarnings('ignore')


def explain_prefix_tuning():
    """
    解釋 Prefix Tuning 的原理
    """
    print("=" * 70)
    print("Prefix Tuning 原理詳解")
    print("=" * 70)

    print("""
Prefix Tuning 的核心思想：

1. 基本概念：
   • 在每一層的 key 和 value 前添加可訓練的前綴向量
   • 原始模型參數保持凍結
   • 只訓練前綴參數

2. 數學表示：
   對於自注意力層：

   Q = XW_Q           (查詢，來自輸入)
   K = [P_K; XW_K]    (鍵，前綴 + 輸入)
   V = [P_V; XW_V]    (值，前綴 + 輸入)

   其中 P_K 和 P_V 是可訓練的前綴

3. 前綴向量：
   • 前綴長度: 通常 10-100 個 token
   • 參數量: num_layers × prefix_length × hidden_size × 2
   • 虛擬 token: 不對應實際文本

4. 重參數化技巧：
   為了訓練穩定性，使用 MLP 編碼器：

   P = MLP(prefix_embedding)

   而不是直接訓練前綴

5. 與其他方法對比：
   ┌─────────────┬──────────┬────────┬──────────┐
   │ 方法        │ 修改位置 │ 參數量 │ 推理開銷 │
   ├─────────────┼──────────┼────────┼──────────┤
   │ Fine-tuning │ 所有權重 │ 100%   │ 無       │
   │ LoRA        │ 權重矩陣 │ <1%    │ 無(合併) │
   │ Prefix      │ 激活值   │ <1%    │ 輕微     │
   │ Adapter     │ 中間層   │ <5%    │ 有       │
   └─────────────┴──────────┴────────┴──────────┘

6. 優勢：
   • 參數效率高
   • 模塊化（不同任務不同前綴）
   • 訓練穩定

7. 劣勢：
   • 推理時有額外序列長度
   • 性能可能略低於 LoRA
   • 前綴長度需要調優
    """)


def create_prefix_tuning_config():
    """
    創建 Prefix Tuning 配置

    Returns:
        配置對象
    """
    print("\n" + "=" * 70)
    print("Prefix Tuning 配置")
    print("=" * 70)

    try:
        from peft import PrefixTuningConfig, TaskType

        # 創建配置
        config = PrefixTuningConfig(
            task_type=TaskType.CAUSAL_LM,
            num_virtual_tokens=20,          # 虛擬 token 數量（前綴長度）
            encoder_hidden_size=128,        # 前綴編碼器隱藏層大小
            prefix_projection=True,         # 是否使用重參數化
        )

        print("\n配置參數:")
        print(f"  任務類型: {config.task_type}")
        print(f"  虛擬 token 數: {config.num_virtual_tokens}")
        print(f"  編碼器隱藏層: {config.encoder_hidden_size}")
        print(f"  前綴投影: {config.prefix_projection}")

        print("\n配置說明:")
        print("  • num_virtual_tokens: 前綴長度，通常 10-100")
        print("  • encoder_hidden_size: 重參數化 MLP 的大小")
        print("  • prefix_projection: True 使用 MLP，False 直接訓練")

        return config

    except Exception as e:
        print(f"✗ 創建配置失敗: {e}")
        return None


def compare_prefix_lengths(model_name: str = "gpt2"):
    """
    比較不同前綴長度的影響

    Args:
        model_name: 模型名稱
    """
    print("\n" + "=" * 70)
    print("前綴長度對比分析")
    print("=" * 70)

    try:
        from transformers import AutoModelForCausalLM
        from peft import PrefixTuningConfig, get_peft_model, TaskType

        print(f"\n加載模型: {model_name}...")
        base_model = AutoModelForCausalLM.from_pretrained(model_name)
        total_params = sum(p.numel() for p in base_model.parameters())

        lengths = [5, 10, 20, 50, 100]

        print(f"\n原始模型參數: {total_params:,} ({total_params/1e6:.2f}M)")
        print("\n" + "=" * 70)
        print(f"{'前綴長度':<12} {'可訓練參數':<15} {'占比':<10} {'推理開銷':<15}")
        print("=" * 70)

        for length in lengths:
            config = PrefixTuningConfig(
                task_type=TaskType.CAUSAL_LM,
                num_virtual_tokens=length,
                encoder_hidden_size=128,
                prefix_projection=True,
            )

            model = AutoModelForCausalLM.from_pretrained(model_name)
            peft_model = get_peft_model(model, config)

            trainable_params = sum(p.numel() for p in peft_model.parameters() if p.requires_grad)
            ratio = 100 * trainable_params / total_params

            # 推理時額外的 token 數量
            extra_tokens = length

            print(f"{length:<12} {trainable_params:>13,}  {ratio:>8.4f}%  +{extra_tokens} tokens")

            del model, peft_model

        print("=" * 70)
        print("\n建議:")
        print("  • 簡單任務: 5-10 個虛擬 token")
        print("  • 一般任務: 20-30 個虛擬 token")
        print("  • 復雜任務: 50-100 個虛擬 token")

    except Exception as e:
        print(f"對比失敗: {e}")
        import traceback
        traceback.print_exc()


def apply_prefix_tuning(model):
    """
    應用 Prefix Tuning 到模型

    Args:
        model: 基礎模型

    Returns:
        PEFT 模型
    """
    print("\n" + "=" * 70)
    print("應用 Prefix Tuning")
    print("=" * 70)

    try:
        from peft import PrefixTuningConfig, get_peft_model, TaskType

        # 創建配置
        config = PrefixTuningConfig(
            task_type=TaskType.CAUSAL_LM,
            num_virtual_tokens=20,
            encoder_hidden_size=128,
            prefix_projection=True,
        )

        print("\n配置詳情:")
        print(f"  虛擬 token 數: {config.num_virtual_tokens}")
        print(f"  編碼器大小: {config.encoder_hidden_size}")

        # 應用到模型
        peft_model = get_peft_model(model, config)

        print("\n參數統計:")
        peft_model.print_trainable_parameters()

        return peft_model

    except Exception as e:
        print(f"✗ 應用失敗: {e}")
        import traceback
        traceback.print_exc()
        return None


def lora_vs_prefix_tuning():
    """
    LoRA 與 Prefix Tuning 詳細對比
    """
    print("\n" + "=" * 70)
    print("LoRA vs Prefix Tuning 詳細對比")
    print("=" * 70)

    comparison = {
        "原理": {
            "LoRA": "在權重矩陣旁添加低秩分解",
            "Prefix": "在每層輸入前添加可訓練前綴"
        },
        "修改位置": {
            "LoRA": "模型權重（參數空間）",
            "Prefix": "激活值（表示空間）"
        },
        "參數量": {
            "LoRA": "r(d+k) per layer",
            "Prefix": "L × prefix_len × hidden_size"
        },
        "推理開銷": {
            "LoRA": "無（可合併到權重）",
            "Prefix": "有（額外的序列長度）"
        },
        "訓練穩定性": {
            "LoRA": "穩定",
            "Prefix": "需要重參數化技巧"
        },
        "性能": {
            "LoRA": "通常更好",
            "Prefix": "略低但仍很好"
        },
        "靈活性": {
            "LoRA": "可以選擇目標層",
            "Prefix": "應用於所有層"
        },
        "適用任務": {
            "LoRA": "大多數 NLP 任務",
            "Prefix": "特別適合生成任務"
        },
        "顯存使用": {
            "LoRA": "訓練時較少",
            "Prefix": "訓練和推理都稍高"
        },
        "部署": {
            "LoRA": "非常方便（合併後無差異）",
            "Prefix": "需要保留前綴結構"
        },
    }

    for aspect, details in comparison.items():
        print(f"\n【{aspect}】")
        for method, desc in details.items():
            print(f"  {method:8s}: {desc}")

    print("\n" + "=" * 70)
    print("選擇建議:")
    print("=" * 70)
    print("""
選擇 LoRA 如果：
  ✓ 追求最佳性能
  ✓ 需要零推理開銷
  ✓ 部署便利性重要
  ✓ 大多數微調場景

選擇 Prefix Tuning 如果：
  ✓ 生成任務
  ✓ 需要保持完整的參數空間
  ✓ 研究激活空間的影響
  ✓ 前綴可解釋性重要

實際中：LoRA 更常用，性能更好，部署更方便
    """)


def training_example():
    """
    Prefix Tuning 訓練示例
    """
    print("\n" + "=" * 70)
    print("Prefix Tuning 訓練示例")
    print("=" * 70)

    print("""
完整的訓練示例代碼：

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
from peft import PrefixTuningConfig, get_peft_model, TaskType
from datasets import Dataset

# 1. 加載模型和分詞器
model_name = "gpt2"
model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token

# 2. 配置 Prefix Tuning
prefix_config = PrefixTuningConfig(
    task_type=TaskType.CAUSAL_LM,
    num_virtual_tokens=20,
    encoder_hidden_size=128,
    prefix_projection=True,
)

# 3. 應用到模型
peft_model = get_peft_model(model, prefix_config)
peft_model.print_trainable_parameters()

# 4. 準備數據
dataset = Dataset.from_dict({
    "text": ["示例文本 1", "示例文本 2", ...]
})

def tokenize_function(examples):
    return tokenizer(examples["text"], truncation=True, max_length=128)

tokenized_dataset = dataset.map(tokenize_function, batched=True)

# 5. 訓練配置
training_args = TrainingArguments(
    output_dir="./prefix_model",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    learning_rate=1e-3,  # Prefix Tuning 可以使用較高的學習率
    logging_steps=10,
)

# 6. 訓練
trainer = Trainer(
    model=peft_model,
    args=training_args,
    train_dataset=tokenized_dataset,
)

trainer.train()

# 7. 保存前綴
peft_model.save_pretrained("./prefix_adapter")

# 8. 加載和使用
from peft import PeftModel

base_model = AutoModelForCausalLM.from_pretrained(model_name)
model_with_prefix = PeftModel.from_pretrained(base_model, "./prefix_adapter")
```
    """)


def best_practices():
    """
    Prefix Tuning 最佳實踐
    """
    print("\n" + "=" * 70)
    print("Prefix Tuning 最佳實踐")
    print("=" * 70)

    practices = {
        "1. 前綴長度選擇": [
            "從較小的值開始（10-20）",
            "根據任務復雜度調整",
            "太長會增加推理成本",
            "太短可能性能不足"
        ],
        "2. 重參數化": [
            "總是啟用 prefix_projection",
            "提升訓練穩定性",
            "編碼器大小通常是隱藏層的 1/8 到 1/4"
        ],
        "3. 學習率": [
            "可以使用較高的學習率（1e-3 到 5e-3）",
            "前綴參數較少，不易過擬合",
            "使用學習率調度器"
        ],
        "4. 適用場景": [
            "文本生成任務效果好",
            "分類任務考慮使用 LoRA",
            "多任務學習可以共享模型，切換前綴"
        ],
        "5. 調試技巧": [
            "檢查前綴是否被正確插入",
            "監控前綴參數的梯度",
            "比較有無前綴的輸出差異"
        ],
    }

    for title, items in practices.items():
        print(f"\n{title}:")
        for item in items:
            print(f"  • {item}")


def main():
    """
    主函數：Prefix Tuning 完整教程
    """
    print("=" * 70)
    print("Prefix Tuning 完整指南")
    print("=" * 70)

    # 1. 原理講解
    explain_prefix_tuning()

    # 2. 配置示例
    config = create_prefix_tuning_config()

    # 3. 前綴長度對比
    compare_prefix_lengths("gpt2")

    # 4. 與 LoRA 對比
    lora_vs_prefix_tuning()

    # 5. 訓練示例
    training_example()

    # 6. 最佳實踐
    best_practices()

    # 7. 總結
    print("\n" + "=" * 70)
    print("總結")
    print("=" * 70)
    print("""
Prefix Tuning 要點：
  • 通過添加可訓練前綴來適配模型
  • 參數效率高（< 1%）
  • 特別適合生成任務
  • 需要平衡前綴長度和性能

與 LoRA 相比：
  • LoRA: 更常用，性能更好，無推理開銷
  • Prefix: 適合特定場景，如多任務學習

何時使用 Prefix Tuning：
  ✓ 生成任務
  ✓ 需要保持參數空間完整
  ✓ 研究和實驗
  ✗ 不適合追求極致性能的生產環境
    """)

    print("\n資源:")
    print("  • Prefix-Tuning 論文: https://arxiv.org/abs/2101.00190")
    print("  • PEFT 文檔: https://huggingface.co/docs/peft/")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用戶中斷")
    except Exception as e:
        print(f"\n程序執行出錯: {e}")
        import traceback
        traceback.print_exc()

"""
IA3 (Infused Adapter by Inhibiting and Amplifying Inner Activations) 方法

這個文件介紹 IA3 方法，包括：
1. IA3 原理和優勢
2. 與 LoRA 的對比
3. 配置和使用
4. 參數效率分析
5. 適用場景

IA3 通過學習縮放向量來調整激活值，參數量比 LoRA 更少。
"""

import warnings
warnings.filterwarnings('ignore')


def explain_ia3():
    """
    解釋 IA3 的原理
    """
    print("=" * 70)
    print("IA3 原理詳解")
    print("=" * 70)

    print("""
IA3 (Infused Adapter by Inhibiting and Amplifying Inner Activations)

1. 核心思想：
   • 不修改權重矩陣
   • 學習縮放向量來調整激活值
   • 通過抑制（inhibit）和放大（amplify）機制進行微調

2. 數學表示：

   對於自注意力層：
   k = W_k · x ⊙ l_k    (縮放 key)
   v = W_v · x ⊙ l_v    (縮放 value)

   對於前饋層：
   ff = W_ff · x ⊙ l_ff  (縮放前饋輸出)

   其中：
   • W: 凍結的預訓練權重
   • ⊙: 元素級乘法
   • l: 可訓練的縮放向量

3. 與 LoRA 對比：

   LoRA:
   W' = W + BA
   參數量: r(d + k)

   IA3:
   output = (Wx) ⊙ l
   參數量: d （只是一個向量！）

4. 參數量對比（以 Transformer 層為例）：
   ┌─────────────┬────────────────┬──────────────┐
   │ 方法        │ 每層參數量     │ 對比 LoRA    │
   ├─────────────┼────────────────┼──────────────┤
   │ Full FT     │ d × k          │ -            │
   │ LoRA (r=16) │ 16(d + k)      │ 基準         │
   │ IA3         │ d              │ ~10-20x 更少 │
   └─────────────┴────────────────┴──────────────┘

5. 優勢：
   • 參數量極少（比 LoRA 還少 10-20 倍）
   • 推理無額外開銷
   • 訓練簡單高效
   • 性能surprisingly good

6. 適用任務：
   • T-Few: Few-shot 學習效果好
   • 特別適合 T5 等模型
   • 在 NLU 和 NLG 任務上都有效
    """)


def create_ia3_config():
    """
    創建 IA3 配置

    Returns:
        配置對象
    """
    print("\n" + "=" * 70)
    print("IA3 配置")
    print("=" * 70)

    try:
        from peft import IA3Config, TaskType

        # 創建 IA3 配置
        config = IA3Config(
            task_type=TaskType.CAUSAL_LM,
            target_modules=["k_proj", "v_proj", "down_proj"],  # 通常針對 k, v 和 FFN
            feedforward_modules=["down_proj"],  # FFN 模塊
        )

        print("\n配置參數:")
        print(f"  任務類型: {config.task_type}")
        print(f"  目標模塊: {config.target_modules}")
        print(f"  前饋模塊: {config.feedforward_modules}")

        print("\n說明:")
        print("  • target_modules: 要應用縮放的模塊")
        print("  • feedforward_modules: FFN 層（從 target_modules 中指定）")
        print("  • 通常針對 key, value 投影和 FFN 輸出")

        return config

    except Exception as e:
        print(f"✗ 創建配置失敗: {e}")
        return None


def compare_with_lora(model_name: str = "gpt2"):
    """
    與 LoRA 對比

    Args:
        model_name: 模型名稱
    """
    print("\n" + "=" * 70)
    print("IA3 vs LoRA 參數量對比")
    print("=" * 70)

    try:
        from transformers import AutoModelForCausalLM
        from peft import IA3Config, LoraConfig, get_peft_model, TaskType

        print(f"\n加載模型: {model_name}...")
        base_model = AutoModelForCausalLM.from_pretrained(model_name)
        total_params = sum(p.numel() for p in base_model.parameters())

        # IA3 配置
        ia3_config = IA3Config(
            task_type=TaskType.CAUSAL_LM,
            target_modules=["c_attn"],
            feedforward_modules=["c_attn"],
        )

        # LoRA 配置（不同的 r 值）
        lora_configs = {
            "LoRA (r=4)": LoraConfig(r=4, target_modules=["c_attn"], task_type=TaskType.CAUSAL_LM),
            "LoRA (r=8)": LoraConfig(r=8, target_modules=["c_attn"], task_type=TaskType.CAUSAL_LM),
            "LoRA (r=16)": LoraConfig(r=16, target_modules=["c_attn"], task_type=TaskType.CAUSAL_LM),
        }

        print(f"\n原始模型參數: {total_params:,} ({total_params/1e6:.2f}M)")
        print("\n" + "=" * 70)
        print(f"{'方法':<15} {'可訓練參數':<15} {'占比':<10} {'相比LoRA-16':<15}")
        print("=" * 70)

        # IA3
        model = AutoModelForCausalLM.from_pretrained(model_name)
        peft_model = get_peft_model(model, ia3_config)
        ia3_params = sum(p.numel() for p in peft_model.parameters() if p.requires_grad)
        ia3_ratio = 100 * ia3_params / total_params
        print(f"{'IA3':<15} {ia3_params:>13,}  {ia3_ratio:>8.4f}%  {'基準':<15}")
        del model, peft_model

        # LoRA 變體
        lora_16_params = None
        for name, config in lora_configs.items():
            model = AutoModelForCausalLM.from_pretrained(model_name)
            peft_model = get_peft_model(model, config)
            params = sum(p.numel() for p in peft_model.parameters() if p.requires_grad)
            ratio = 100 * params / total_params

            if name == "LoRA (r=16)":
                lora_16_params = params
                reduction = "基準"
            else:
                reduction = f"{params / ia3_params:.1f}x IA3"

            print(f"{name:<15} {params:>13,}  {ratio:>8.4f}%  {reduction:<15}")
            del model, peft_model

        if lora_16_params:
            print("=" * 70)
            print(f"\nIA3 參數量是 LoRA(r=16) 的 {ia3_params/lora_16_params*100:.1f}%")
            print(f"節省: {(1 - ia3_params/lora_16_params)*100:.1f}%")

    except Exception as e:
        print(f"對比失敗: {e}")
        import traceback
        traceback.print_exc()


def usage_example():
    """
    使用示例
    """
    print("\n" + "=" * 70)
    print("IA3 使用示例")
    print("=" * 70)

    print("""
完整的 IA3 使用流程：

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
from peft import IA3Config, get_peft_model, TaskType
from datasets import Dataset

# 1. 加載模型
model_name = "gpt2"
model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token

# 2. 配置 IA3
ia3_config = IA3Config(
    task_type=TaskType.CAUSAL_LM,
    target_modules=["c_attn"],  # GPT-2 的注意力層
    feedforward_modules=["c_attn"],
)

# 3. 應用 IA3
peft_model = get_peft_model(model, ia3_config)
peft_model.print_trainable_parameters()
# 輸出示例: trainable params: 7,680 || all params: 124,439,808 || trainable%: 0.006%

# 4. 準備數據
dataset = Dataset.from_dict({
    "text": ["示例文本 1", "示例文本 2", ...]
})

# 5. 訓練配置
training_args = TrainingArguments(
    output_dir="./ia3_model",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    learning_rate=3e-3,  # IA3 可以使用較高的學習率
    logging_steps=10,
)

# 6. 訓練
trainer = Trainer(
    model=peft_model,
    args=training_args,
    train_dataset=dataset,
)

trainer.train()

# 7. 保存
peft_model.save_pretrained("./ia3_adapter")

# 8. 加載和使用
from peft import PeftModel

base_model = AutoModelForCausalLM.from_pretrained(model_name)
model_with_ia3 = PeftModel.from_pretrained(base_model, "./ia3_adapter")
```

特別注意：
• IA3 適配器文件非常小（幾 KB 到幾 MB）
• 推理時無額外開銷
• 可以合併到基礎模型
    """)


def best_practices():
    """
    最佳實踐
    """
    print("\n" + "=" * 70)
    print("IA3 最佳實踐")
    print("=" * 70)

    practices = {
        "1. 目標模塊選擇": [
            "必須包含 key 和 value 投影",
            "可以添加 FFN 輸出層",
            "不要包含 query 投影（IA3 設計如此）",
        ],
        "2. 學習率設置": [
            "可以使用較高的學習率（1e-3 到 5e-3）",
            "參數量少，不易過擬合",
            "使用 warmup 可以提升穩定性",
        ],
        "3. 適用模型": [
            "T5 系列效果特別好",
            "GPT 系列也適用",
            "BERT 類模型可以嘗試",
        ],
        "4. 任務選擇": [
            "Few-shot 學習效果好",
            "分類任務適合",
            "生成任務也可以",
        ],
        "5. 與 LoRA 對比": [
            "參數更少，訓練更快",
            "在某些任務上性能相當",
            "優先嘗試，不行再用 LoRA",
        ],
    }

    for title, items in practices.items():
        print(f"\n{title}:")
        for item in items:
            print(f"  • {item}")


def when_to_use_ia3():
    """
    何時使用 IA3
    """
    print("\n" + "=" * 70)
    print("IA3 使用場景")
    print("=" * 70)

    print("""
優先使用 IA3 的場景：
  ✓ 極度關注參數效率
  ✓ Few-shot 學習任務
  ✓ 使用 T5 類模型
  ✓ 需要維護大量適配器
  ✓ 存儲和傳輸成本敏感

考慮使用 LoRA 的場景：
  ✓ 追求最佳性能
  ✓ 復雜任務
  ✓ IA3 效果不理想
  ✓ 社區支持和資源更豐富

IA3 vs LoRA 決策樹：

                 參數效率最重要？
                    /        \\
                  是          否
                  /            \\
               IA3            LoRA
                              /  \\
                         T5模型  其他
                          /        \\
                    也試試IA3    優先LoRA
    """)


def performance_tips():
    """
    性能優化技巧
    """
    print("\n" + "=" * 70)
    print("性能優化技巧")
    print("=" * 70)

    print("""
1. 初始化策略：
   • IA3 的縮放向量通常初始化為 1
   • 意味著開始時等同於原模型
   • 可以嘗試其他初始化（如 0.1）

2. 訓練技巧：
   • 使用較大的 batch size（IA3 參數少）
   • 可以訓練更多 epoch
   • 監控縮放向量的數值範圍

3. 調試方法：
   • 打印縮放向量的統計信息
   • 檢查是否有數值穩定性問題
   • 比較有無 IA3 的輸出差異

4. 組合使用：
   • 可以與量化結合
   • 可以與其他 PEFT 方法結合（實驗性）
   • 可以在 IA3 基礎上繼續訓練

5. 部署優化：
   • 合併縮放向量到模型
   • 使用 FP16/BF16 以進一步節省空間
   • 批量處理多個適配器
    """)


def main():
    """
    主函數：IA3 完整教程
    """
    print("=" * 70)
    print("IA3 方法完整指南")
    print("=" * 70)

    # 1. 原理講解
    explain_ia3()

    # 2. 配置示例
    config = create_ia3_config()

    # 3. 與 LoRA 對比
    compare_with_lora("gpt2")

    # 4. 使用示例
    usage_example()

    # 5. 最佳實踐
    best_practices()

    # 6. 使用場景
    when_to_use_ia3()

    # 7. 性能優化
    performance_tips()

    # 8. 總結
    print("\n" + "=" * 70)
    print("總結")
    print("=" * 70)
    print("""
IA3 關鍵要點：

1. 極致的參數效率：
   • 比 LoRA 少 10-20 倍參數
   • 適配器文件極小（KB 級別）
   • 訓練速度快

2. 工作原理：
   • 學習縮放向量
   • 調整激活值而非權重
   • 通過抑制和放大機制微調

3. 性能表現：
   • Few-shot 學習效果好
   • 某些任務接近 LoRA
   • T5 模型上特別有效

4. 實際建議：
   • 先嘗試 IA3（參數少，快）
   • 不滿意再用 LoRA（性能好）
   • 根據任務和資源選擇

5. 研究價值：
   • 展示了參數效率的極限
   • 激活空間調整的新思路
   • 為未來方法提供靈感
    """)

    print("\n資源:")
    print("  • IA3 論文 (T-Few): https://arxiv.org/abs/2205.05638")
    print("  • PEFT 文檔: https://huggingface.co/docs/peft/")
    print("  • 代碼: https://github.com/huggingface/peft")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用戶中斷")
    except Exception as e:
        print(f"\n程序執行出錯: {e}")
        import traceback
        traceback.print_exc()

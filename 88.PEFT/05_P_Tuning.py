"""
P-Tuning 實現

這個文件介紹 P-Tuning 和 Prompt Tuning 方法，包括：
1. P-Tuning 原理
2. Prompt Tuning 原理
3. 與 Prefix Tuning 的區別
4. 配置和使用
5. 適用場景

P-Tuning 使用可訓練的提示編碼器，Prompt Tuning 直接優化軟提示。
"""

import warnings
warnings.filterwarnings('ignore')


def explain_p_tuning():
    """
    解釋 P-Tuning 的原理
    """
    print("=" * 70)
    print("P-Tuning 原理詳解")
    print("=" * 70)

    print("""
P-Tuning 的核心思想：

1. 軟提示（Soft Prompts）：
   • 傳統提示: "Translate to French: [INPUT]" (離散的文本)
   • 軟提示: 連續的嵌入向量，可以通過梯度優化

2. P-Tuning 架構：

   輸入: [P₀][P₁]...[Pₙ] + 真實文本

   其中 Pᵢ 是可訓練的嵌入向量，不對應任何實際token

3. 提示編碼器：
   使用 LSTM/MLP 來編碼虛擬 token：

   prompt_embeddings = PromptEncoder(virtual_token_ids)

4. 優勢：
   • 自動學習最優提示
   • 不需要人工設計提示
   • 參數效率高
   • 可用於小樣本學習

5. 與 Prompt Engineering 對比：
   ┌──────────────┬────────────┬──────────┬────────┐
   │ 方法         │ 提示類型   │ 優化方式 │ 效果   │
   ├──────────────┼────────────┼──────────┼────────┤
   │ Prompt Eng.  │ 離散文本   │ 人工搜索 │ 中等   │
   │ P-Tuning     │ 連續向量   │ 梯度下降 │ 更好   │
   │ Prompt Tune  │ 連續向量   │ 直接訓練 │ 簡單   │
   │ Prefix Tune  │ 連續向量   │ 每層訓練 │ 最好   │
   └──────────────┴────────────┴──────────┴────────┘
    """)


def explain_prompt_tuning():
    """
    解釋 Prompt Tuning 的原理
    """
    print("\n" + "=" * 70)
    print("Prompt Tuning 原理詳解")
    print("=" * 70)

    print("""
Prompt Tuning 的核心思想：

1. 更簡單的方法：
   • 不使用復雜的編碼器
   • 直接訓練軟提示向量
   • 只在輸入層添加提示

2. 架構：

   input_embeddings = [soft_prompts; token_embeddings(input)]
   output = LLM(input_embeddings)

3. 參數量：
   • 極少：prompt_length × hidden_size
   • 例如：20 × 768 = 15,360 個參數
   • 相比模型總參數（億級）幾乎可忽略

4. 訓練：
   • 凍結整個模型
   • 只訓練 soft_prompts
   • 使用標準的交叉熵損失

5. 關鍵發現：
   • 模型越大，效果越好
   • 10B+ 參數模型上，Prompt Tuning 接近全量微調
   • 小模型上效果較差

6. 優勢：
   • 極致的參數效率
   • 訓練速度快
   • 易於多任務管理（每個任務一組提示）
    """)


def compare_tuning_methods():
    """
    對比不同的調優方法
    """
    print("\n" + "=" * 70)
    print("各種 Tuning 方法對比")
    print("=" * 70)

    methods = {
        "Prompt Tuning": {
            "位置": "輸入層",
            "編碼器": "無",
            "參數量": "最少",
            "性能": "大模型上好",
            "複雜度": "最簡單",
            "推理開銷": "極小",
        },
        "P-Tuning": {
            "位置": "輸入層",
            "編碼器": "LSTM/MLP",
            "參數量": "少",
            "性能": "中等",
            "複雜度": "中等",
            "推理開銷": "小",
        },
        "P-Tuning v2 (Prefix)": {
            "位置": "每一層",
            "編碼器": "MLP（可選）",
            "參數量": "較少",
            "性能": "好",
            "複雜度": "中等",
            "推理開銷": "中等",
        },
        "LoRA": {
            "位置": "權重矩陣",
            "編碼器": "無",
            "參數量": "少",
            "性能": "很好",
            "複雜度": "簡單",
            "推理開銷": "無",
        },
    }

    print()
    for method, details in methods.items():
        print(f"【{method}】")
        for key, value in details.items():
            print(f"  {key}: {value}")
        print()

    print("=" * 70)
    print("演進關係:")
    print("=" * 70)
    print("""
Prompt Tuning (2021)
  ↓
  只在輸入層，太簡單，小模型效果差
  ↓
P-Tuning (2021)
  ↓
  添加提示編碼器，提升小模型效果
  ↓
P-Tuning v2 / Prefix Tuning (2022)
  ↓
  擴展到每一層，性能大幅提升
  ↓
LoRA (2021, 獨立發展)
  ↓
  不同思路（修改權重而非激活），成為主流
    """)


def create_prompt_tuning_config():
    """
    創建 Prompt Tuning 配置

    Returns:
        配置對象
    """
    print("\n" + "=" * 70)
    print("Prompt Tuning 配置")
    print("=" * 70)

    try:
        from peft import PromptTuningConfig, TaskType, PromptTuningInit

        # 創建配置
        config = PromptTuningConfig(
            task_type=TaskType.CAUSAL_LM,
            prompt_tuning_init=PromptTuningInit.RANDOM,  # 初始化方式
            num_virtual_tokens=20,                        # 軟提示長度
            tokenizer_name_or_path="gpt2",               # 分詞器（用於文本初始化）
        )

        print("\n配置參數:")
        print(f"  任務類型: {config.task_type}")
        print(f"  初始化方式: {config.prompt_tuning_init}")
        print(f"  虛擬 token 數: {config.num_virtual_tokens}")

        print("\n初始化方式選項:")
        print("  • RANDOM: 隨機初始化（最常用）")
        print("  • TEXT: 從文本初始化（需要提供 prompt_tuning_init_text）")

        return config

    except Exception as e:
        print(f"✗ 創建配置失敗: {e}")
        return None


def create_p_tuning_config():
    """
    創建 P-Tuning 配置

    Returns:
        配置對象
    """
    print("\n" + "=" * 70)
    print("P-Tuning 配置 (通過 Prompt Tuning 實現)")
    print("=" * 70)

    try:
        from peft import PromptEncoderConfig, TaskType

        # P-Tuning 使用提示編碼器
        config = PromptEncoderConfig(
            task_type=TaskType.CAUSAL_LM,
            num_virtual_tokens=20,
            encoder_hidden_size=128,
            encoder_num_layers=2,
            encoder_dropout=0.1,
        )

        print("\n配置參數:")
        print(f"  任務類型: {config.task_type}")
        print(f"  虛擬 token 數: {config.num_virtual_tokens}")
        print(f"  編碼器隱藏層: {config.encoder_hidden_size}")
        print(f"  編碼器層數: {config.encoder_num_layers}")
        print(f"  編碼器 dropout: {config.encoder_dropout}")

        print("\n說明:")
        print("  • encoder_hidden_size: 提示編碼器的隱藏層大小")
        print("  • encoder_num_layers: 編碼器的層數（通常 2 層）")

        return config

    except Exception as e:
        print(f"✗ 創建配置失敗: {e}")
        return None


def parameter_comparison(model_name: str = "gpt2"):
    """
    參數量對比

    Args:
        model_name: 模型名稱
    """
    print("\n" + "=" * 70)
    print("參數量對比")
    print("=" * 70)

    try:
        from transformers import AutoModelForCausalLM
        from peft import (
            PromptTuningConfig,
            PromptEncoderConfig,
            PrefixTuningConfig,
            LoraConfig,
            get_peft_model,
            TaskType
        )

        print(f"\n加載模型: {model_name}...")
        base_model = AutoModelForCausalLM.from_pretrained(model_name)
        total_params = sum(p.numel() for p in base_model.parameters())

        configs = {
            "Prompt Tuning": PromptTuningConfig(
                task_type=TaskType.CAUSAL_LM,
                num_virtual_tokens=20,
            ),
            "P-Tuning": PromptEncoderConfig(
                task_type=TaskType.CAUSAL_LM,
                num_virtual_tokens=20,
                encoder_hidden_size=128,
            ),
            "Prefix Tuning": PrefixTuningConfig(
                task_type=TaskType.CAUSAL_LM,
                num_virtual_tokens=20,
            ),
            "LoRA": LoraConfig(
                r=16,
                target_modules=["c_attn"],
                task_type=TaskType.CAUSAL_LM,
            ),
        }

        print(f"\n原始模型參數: {total_params:,} ({total_params/1e6:.2f}M)")
        print("\n" + "=" * 70)
        print(f"{'方法':<20} {'可訓練參數':<15} {'占比':<10}")
        print("=" * 70)

        for method_name, config in configs.items():
            model = AutoModelForCausalLM.from_pretrained(model_name)
            peft_model = get_peft_model(model, config)

            trainable_params = sum(p.numel() for p in peft_model.parameters() if p.requires_grad)
            ratio = 100 * trainable_params / total_params

            print(f"{method_name:<20} {trainable_params:>13,}  {ratio:>8.4f}%")

            del model, peft_model

        print("=" * 70)
        print("\n觀察:")
        print("  • Prompt Tuning 參數最少")
        print("  • P-Tuning 因為編碼器略多一些")
        print("  • Prefix Tuning 參數較多（每層都有）")
        print("  • LoRA 取決於 r 和 target_modules")

    except Exception as e:
        print(f"對比失敗: {e}")
        import traceback
        traceback.print_exc()


def usage_example():
    """
    使用示例
    """
    print("\n" + "=" * 70)
    print("使用示例")
    print("=" * 70)

    print("""
1. Prompt Tuning 示例：

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PromptTuningConfig, get_peft_model, TaskType

# 加載模型
model = AutoModelForCausalLM.from_pretrained("gpt2")
tokenizer = AutoTokenizer.from_pretrained("gpt2")

# 配置 Prompt Tuning
config = PromptTuningConfig(
    task_type=TaskType.CAUSAL_LM,
    num_virtual_tokens=20,
)

# 應用
peft_model = get_peft_model(model, config)
peft_model.print_trainable_parameters()

# 訓練...
trainer.train()

# 保存
peft_model.save_pretrained("./prompt_adapter")
```

2. P-Tuning 示例：

```python
from peft import PromptEncoderConfig

# 配置 P-Tuning
config = PromptEncoderConfig(
    task_type=TaskType.CAUSAL_LM,
    num_virtual_tokens=20,
    encoder_hidden_size=128,
    encoder_num_layers=2,
)

# 其餘步驟相同
peft_model = get_peft_model(model, config)
```

3. 文本初始化的 Prompt Tuning：

```python
from peft import PromptTuningInit

config = PromptTuningConfig(
    task_type=TaskType.CAUSAL_LM,
    prompt_tuning_init=PromptTuningInit.TEXT,
    prompt_tuning_init_text="Classify the sentiment of this text:",
    num_virtual_tokens=8,  # 自動從文本計算
    tokenizer_name_or_path="gpt2",
)
```
    """)


def best_practices():
    """
    最佳實踐
    """
    print("\n" + "=" * 70)
    print("最佳實踐")
    print("=" * 70)

    practices = {
        "1. 方法選擇": [
            "大模型 (>10B): Prompt Tuning 就夠了",
            "中小模型: 優先考慮 LoRA 或 Prefix Tuning",
            "研究目的: P-Tuning 提供更多控制",
        ],
        "2. 提示長度": [
            "通常 10-20 個虛擬 token",
            "任務簡單可以更少 (5-10)",
            "任務復雜可以更多 (20-50)",
        ],
        "3. 初始化": [
            "隨機初始化最常用",
            "文本初始化可能提升收斂速度",
            "文本初始化需要精心設計初始文本",
        ],
        "4. 訓練": [
            "學習率可以較高 (1e-3)",
            "批次大小不需要太大",
            "通常收斂很快",
        ],
        "5. 評估": [
            "在大模型上，接近全量微調",
            "在小模型上，可能不如 LoRA",
            "特別適合多任務場景",
        ],
    }

    for title, items in practices.items():
        print(f"\n{title}:")
        for item in items:
            print(f"  • {item}")


def when_to_use():
    """
    何時使用這些方法
    """
    print("\n" + "=" * 70)
    print("使用場景指南")
    print("=" * 70)

    scenarios = {
        "使用 Prompt Tuning": [
            "模型非常大 (10B+)",
            "需要極致的參數效率",
            "多任務學習（每個任務一組提示）",
            "快速實驗和原型",
        ],
        "使用 P-Tuning": [
            "中小型模型",
            "需要提示編碼器的表達能力",
            "研究軟提示的學習過程",
        ],
        "使用 Prefix Tuning": [
            "需要更好的性能",
            "願意接受稍多的參數",
            "生成任務",
        ],
        "使用 LoRA": [
            "大多數生產場景（推薦）",
            "需要最佳性能",
            "需要零推理開銷",
            "部署便利性重要",
        ],
    }

    for scenario, reasons in scenarios.items():
        print(f"\n【{scenario}】")
        for reason in reasons:
            print(f"  ✓ {reason}")


def main():
    """
    主函數：P-Tuning 和 Prompt Tuning 完整教程
    """
    print("=" * 70)
    print("P-Tuning 和 Prompt Tuning 完整指南")
    print("=" * 70)

    # 1. 原理講解
    explain_p_tuning()
    explain_prompt_tuning()

    # 2. 方法對比
    compare_tuning_methods()

    # 3. 配置示例
    prompt_config = create_prompt_tuning_config()
    p_tuning_config = create_p_tuning_config()

    # 4. 參數對比
    parameter_comparison("gpt2")

    # 5. 使用示例
    usage_example()

    # 6. 最佳實踐
    best_practices()

    # 7. 使用場景
    when_to_use()

    # 8. 總結
    print("\n" + "=" * 70)
    print("總結")
    print("=" * 70)
    print("""
關鍵要點：

1. Prompt Tuning:
   • 最簡單，參數最少
   • 在大模型上效果好
   • 適合多任務學習

2. P-Tuning:
   • 添加了提示編碼器
   • 改善小模型性能
   • 研究價值高

3. 實際選擇:
   • 生產環境: LoRA (性能最好，部署最簡單)
   • 大模型實驗: Prompt Tuning (參數最少)
   • 研究探索: P-Tuning/Prefix Tuning

4. 關係:
   • P-Tuning v2 實際上就是 Prefix Tuning
   • Prompt Tuning 是最簡化的版本
   • LoRA 是完全不同的思路，但效果最好
    """)

    print("\n資源:")
    print("  • GPT Understands Too 論文: https://arxiv.org/abs/2103.10385")
    print("  • Prompt Tuning 論文: https://arxiv.org/abs/2104.08691")
    print("  • P-Tuning v2 論文: https://arxiv.org/abs/2110.07602")
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

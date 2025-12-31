"""
LoRA 基礎完整指南

這個文件深入介紹 LoRA (Low-Rank Adaptation) 的原理和使用，包括：
1. LoRA 原理詳解
2. 超參數配置與調優
3. 目標模塊選擇策略
4. 訓練技巧與最佳實踐
5. 性能對比分析

LoRA 是最流行和高效的 PEFT 方法之一。
"""

import os
import torch
from typing import List, Dict, Optional, Tuple
import warnings

warnings.filterwarnings('ignore')


def explain_lora_theory():
    """
    解釋 LoRA 的理論原理
    """
    print("=" * 70)
    print("LoRA 原理詳解")
    print("=" * 70)

    print("""
LoRA (Low-Rank Adaptation) 的核心思想：

1. 假設預訓練權重矩陣 W ∈ ℝ^(d×k)
2. 在微調時，不直接更新 W，而是學習一個低秩分解：

   W' = W + ΔW = W + BA

   其中：
   - W: 原始權重（凍結，不訓練）
   - B ∈ ℝ^(d×r): 下投影矩陣（可訓練）
   - A ∈ ℝ^(r×k): 上投影矩陣（可訓練）
   - r: 秩，遠小於 min(d, k)

3. 參數量對比：
   - 原始參數量: d × k
   - LoRA 參數量: d × r + r × k = r(d + k)
   - 參數減少率: 1 - r(d+k)/(dk) ≈ 99% (當 r << d,k 時)

4. 優勢：
   - 極少的可訓練參數
   - 推理時可合併 (W' = W + BA)，無額外計算開銷
   - 可以輕鬆切換不同的適配器

示例計算：
- 假設 W 是 1024×1024 的矩陣
- 原始參數: 1024 × 1024 = 1,048,576
- LoRA (r=8): 1024 × 8 + 8 × 1024 = 16,384
- 減少: 98.4%
    """)


def create_lora_config_variants():
    """
    創建不同的 LoRA 配置變體，展示超參數的影響

    Returns:
        List[Dict]: LoRA 配置列表
    """
    print("\n" + "=" * 70)
    print("LoRA 超參數配置變體")
    print("=" * 70)

    from peft import LoraConfig, TaskType

    configs = {
        "極小配置 (最省資源)": LoraConfig(
            r=4,
            lora_alpha=8,
            target_modules=["q_proj", "v_proj"],
            lora_dropout=0.05,
            bias="none",
            task_type=TaskType.CAUSAL_LM
        ),
        "標準配置 (推薦)": LoraConfig(
            r=16,
            lora_alpha=32,
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
            lora_dropout=0.1,
            bias="none",
            task_type=TaskType.CAUSAL_LM
        ),
        "高性能配置": LoraConfig(
            r=32,
            lora_alpha=64,
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
            lora_dropout=0.1,
            bias="none",
            task_type=TaskType.CAUSAL_LM
        ),
        "全層配置 (最佳性能)": LoraConfig(
            r=16,
            lora_alpha=32,
            target_modules="all-linear",  # 應用到所有線性層
            lora_dropout=0.1,
            bias="none",
            task_type=TaskType.CAUSAL_LM
        ),
    }

    print("\n各配置詳情：\n")
    for name, config in configs.items():
        print(f"【{name}】")
        print(f"  秩 (r): {config.r}")
        print(f"  Alpha: {config.lora_alpha}")
        print(f"  目標模塊: {config.target_modules}")
        print(f"  Dropout: {config.lora_dropout}")
        print(f"  用途: ", end="")

        if config.r <= 8:
            print("資源受限環境，快速實驗")
        elif config.r <= 16:
            print("大多數任務的平衡選擇")
        elif config.r <= 32:
            print("追求更好性能，有充足資源")
        else:
            print("研究實驗，追求最佳效果")
        print()

    return configs


def demonstrate_target_modules():
    """
    演示不同目標模塊的選擇策略
    """
    print("=" * 70)
    print("目標模塊選擇策略")
    print("=" * 70)

    strategies = {
        "策略 1: 只訓練 Query & Value": {
            "modules": ["q_proj", "v_proj"],
            "參數量": "最少",
            "訓練速度": "最快",
            "性能": "中等",
            "適用場景": "資源受限、快速實驗"
        },
        "策略 2: 訓練所有注意力投影": {
            "modules": ["q_proj", "k_proj", "v_proj", "o_proj"],
            "參數量": "較少",
            "訓練速度": "較快",
            "性能": "良好",
            "適用場景": "大多數微調任務（推薦）"
        },
        "策略 3: 包含 FFN 層": {
            "modules": ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
            "參數量": "中等",
            "訓練速度": "中等",
            "性能": "很好",
            "適用場景": "需要更強適應能力"
        },
        "策略 4: 所有線性層": {
            "modules": "all-linear",
            "參數量": "較多（但仍遠小於全量微調）",
            "訓練速度": "較慢",
            "性能": "最佳",
            "適用場景": "追求最佳性能"
        },
    }

    for strategy_name, details in strategies.items():
        print(f"\n【{strategy_name}】")
        for key, value in details.items():
            print(f"  {key}: {value}")


def calculate_parameters(model, lora_config):
    """
    計算應用 LoRA 後的參數量

    Args:
        model: 基礎模型
        lora_config: LoRA 配置

    Returns:
        Dict: 參數統計信息
    """
    from peft import get_peft_model

    print("\n" + "=" * 70)
    print("參數量計算")
    print("=" * 70)

    # 原始模型參數量
    original_params = sum(p.numel() for p in model.parameters())

    # 應用 LoRA
    peft_model = get_peft_model(model, lora_config)

    # 可訓練參數量
    trainable_params = sum(p.numel() for p in peft_model.parameters() if p.requires_grad)
    all_params = sum(p.numel() for p in peft_model.parameters())

    # 計算比例
    trainable_ratio = 100 * trainable_params / all_params

    print(f"\n原始模型參數: {original_params:,}")
    print(f"所有參數: {all_params:,}")
    print(f"可訓練參數: {trainable_params:,}")
    print(f"可訓練比例: {trainable_ratio:.4f}%")
    print(f"參數減少: {100 - trainable_ratio:.4f}%")

    # 估計顯存節省
    print(f"\n顯存估算（以 float32 計算）:")
    print(f"  原始模型: {original_params * 4 / 1e9:.2f} GB")
    print(f"  LoRA 增量: {trainable_params * 4 / 1e9:.4f} GB")
    print(f"  節省比例: ~{100 - trainable_ratio:.1f}%")

    return {
        "original_params": original_params,
        "trainable_params": trainable_params,
        "all_params": all_params,
        "trainable_ratio": trainable_ratio
    }


def compare_lora_ranks(model_name: str = "gpt2"):
    """
    比較不同秩（r）的影響

    Args:
        model_name: 模型名稱
    """
    print("\n" + "=" * 70)
    print("LoRA 秩（r）對比實驗")
    print("=" * 70)

    try:
        from transformers import AutoModelForCausalLM
        from peft import LoraConfig, get_peft_model, TaskType

        print(f"\n加載模型: {model_name}...")
        base_model = AutoModelForCausalLM.from_pretrained(model_name)
        original_params = sum(p.numel() for p in base_model.parameters())

        ranks = [4, 8, 16, 32, 64, 128]

        print(f"\n原始模型參數: {original_params:,} ({original_params/1e6:.2f}M)")
        print("\n" + "=" * 70)
        print(f"{'秩 (r)':<10} {'可訓練參數':<15} {'占比':<10} {'適配器大小':<15}")
        print("=" * 70)

        for r in ranks:
            # 創建配置
            config = LoraConfig(
                r=r,
                lora_alpha=r * 2,
                target_modules=["c_attn"],
                task_type=TaskType.CAUSAL_LM
            )

            # 應用 LoRA
            model = AutoModelForCausalLM.from_pretrained(model_name)
            peft_model = get_peft_model(model, config)

            # 計算參數
            trainable_params = sum(p.numel() for p in peft_model.parameters() if p.requires_grad)
            ratio = 100 * trainable_params / original_params
            size_mb = trainable_params * 4 / (1024 * 1024)  # float32

            print(f"{r:<10} {trainable_params:>13,}  {ratio:>8.4f}%  {size_mb:>12.2f} MB")

            # 清理記憶體
            del model, peft_model

        print("=" * 70)
        print("\n建議:")
        print("  • r=4-8:   快速實驗、資源受限")
        print("  • r=16-32: 大多數任務的最佳選擇")
        print("  • r=64+:   研究實驗、追求極致性能")

    except Exception as e:
        print(f"對比實驗失敗: {e}")
        import traceback
        traceback.print_exc()


def training_with_lora(
    model,
    tokenizer,
    lora_config,
    dataset,
    output_dir: str = "./output/lora_training"
):
    """
    使用 LoRA 進行訓練的完整示例

    Args:
        model: 基礎模型
        tokenizer: 分詞器
        lora_config: LoRA 配置
        dataset: 訓練數據集
        output_dir: 輸出目錄
    """
    print("\n" + "=" * 70)
    print("LoRA 訓練完整流程")
    print("=" * 70)

    try:
        from peft import get_peft_model
        from transformers import Trainer, TrainingArguments, DataCollatorForLanguageModeling

        # 應用 LoRA
        print("\n1. 應用 LoRA 配置...")
        peft_model = get_peft_model(model, lora_config)
        peft_model.print_trainable_parameters()

        # 創建輸出目錄
        os.makedirs(output_dir, exist_ok=True)

        # 訓練參數
        print("\n2. 配置訓練參數...")
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=3,
            per_device_train_batch_size=4,
            gradient_accumulation_steps=4,
            learning_rate=3e-4,  # LoRA 推薦較高的學習率
            weight_decay=0.01,
            logging_steps=10,
            save_strategy="epoch",
            save_total_limit=2,
            fp16=torch.cuda.is_available(),  # 使用混合精度
            report_to="none",
        )

        print(f"  學習率: {training_args.learning_rate}")
        print(f"  Batch Size: {training_args.per_device_train_batch_size}")
        print(f"  梯度累積: {training_args.gradient_accumulation_steps}")
        print(f"  有效 Batch Size: {training_args.per_device_train_batch_size * training_args.gradient_accumulation_steps}")

        # 數據整理器
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=tokenizer,
            mlm=False
        )

        # 預處理數據
        print("\n3. 預處理數據...")
        def tokenize_function(examples):
            return tokenizer(examples["text"], truncation=True, max_length=256, padding="max_length")

        tokenized_dataset = dataset.map(tokenize_function, batched=True, remove_columns=dataset.column_names)

        # 創建訓練器
        print("\n4. 創建訓練器...")
        trainer = Trainer(
            model=peft_model,
            args=training_args,
            train_dataset=tokenized_dataset,
            data_collator=data_collator,
        )

        # 訓練
        print("\n5. 開始訓練...")
        print("=" * 70)
        trainer.train()

        # 保存
        print("\n6. 保存 LoRA 適配器...")
        peft_model.save_pretrained(output_dir)
        tokenizer.save_pretrained(output_dir)

        # 檢查保存的文件
        print(f"\n保存的文件:")
        for file in os.listdir(output_dir):
            if file.endswith(('.bin', '.safetensors', '.json')):
                file_path = os.path.join(output_dir, file)
                size_mb = os.path.getsize(file_path) / (1024 * 1024)
                print(f"  • {file}: {size_mb:.2f} MB")

        print("\n✓ 訓練完成！")

        return peft_model

    except Exception as e:
        print(f"✗ 訓練失敗: {e}")
        import traceback
        traceback.print_exc()
        return None


def load_and_use_adapter(base_model_name: str, adapter_path: str, tokenizer):
    """
    加載和使用保存的適配器

    Args:
        base_model_name: 基礎模型名稱
        adapter_path: 適配器路徑
        tokenizer: 分詞器
    """
    print("\n" + "=" * 70)
    print("加載和使用 LoRA 適配器")
    print("=" * 70)

    try:
        from transformers import AutoModelForCausalLM
        from peft import PeftModel

        print(f"\n1. 加載基礎模型: {base_model_name}")
        base_model = AutoModelForCausalLM.from_pretrained(base_model_name)

        print(f"2. 加載 LoRA 適配器: {adapter_path}")
        model = PeftModel.from_pretrained(base_model, adapter_path)

        print("3. 合併適配器（可選，用於推理加速）")
        model = model.merge_and_unload()

        print("\n✓ 模型準備就緒！")

        # 測試生成
        print("\n4. 測試生成...")
        test_prompt = "PEFT 是"
        inputs = tokenizer(test_prompt, return_tensors="pt")

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=30,
                do_sample=True,
                temperature=0.7
            )

        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"\n輸入: {test_prompt}")
        print(f"輸出: {generated_text}")

        return model

    except Exception as e:
        print(f"✗ 加載適配器失敗: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """
    主函數：LoRA 完整教程
    """
    print("=" * 70)
    print("LoRA 完整使用指南")
    print("=" * 70)

    # 1. 理論講解
    explain_lora_theory()

    # 2. 配置變體
    configs = create_lora_config_variants()

    # 3. 目標模塊策略
    demonstrate_target_modules()

    # 4. 秩對比
    print("\n" + "=" * 70)
    print("提示: 接下來會進行參數對比實驗...")
    print("=" * 70)
    compare_lora_ranks("gpt2")

    # 5. 實際訓練示例
    print("\n" + "=" * 70)
    print("實際訓練示例（已註釋，取消註釋以運行）")
    print("=" * 70)
    print("""
取消以下代碼的註釋以運行完整的訓練示例：

# from transformers import AutoModelForCausalLM, AutoTokenizer
# from datasets import Dataset
#
# # 加載模型
# model = AutoModelForCausalLM.from_pretrained("gpt2")
# tokenizer = AutoTokenizer.from_pretrained("gpt2")
# tokenizer.pad_token = tokenizer.eos_token
#
# # 創建數據
# dataset = Dataset.from_dict({
#     "text": ["示例文本 " + str(i) for i in range(100)]
# })
#
# # 選擇配置
# lora_config = configs["標準配置 (推薦)"]
#
# # 訓練
# peft_model = training_with_lora(model, tokenizer, lora_config, dataset)
    """)

    # 6. 總結
    print("\n" + "=" * 70)
    print("LoRA 使用要點總結")
    print("=" * 70)
    print("""
1. 超參數選擇:
   • r (秩): 16-32 適合大多數任務
   • alpha: 通常設為 r 的 2 倍
   • dropout: 0.05-0.1

2. 目標模塊:
   • 入門: ["q_proj", "v_proj"]
   • 推薦: ["q_proj", "k_proj", "v_proj", "o_proj"]
   • 進階: "all-linear"

3. 學習率:
   • LoRA 通常使用較高的學習率 (2e-4 到 5e-4)
   • 比全量微調高 1-2 倍

4. 最佳實踐:
   • 從小的 r 開始實驗
   • 監控訓練指標，逐步調整
   • 使用混合精度訓練
   • 定期保存檢查點

5. 性能優化:
   • 使用 gradient_checkpointing
   • 合理設置 batch_size 和 gradient_accumulation_steps
   • 推理時合併適配器 (merge_and_unload)
    """)

    print("\n資源:")
    print("  • LoRA 論文: https://arxiv.org/abs/2106.09685")
    print("  • PEFT 文檔: https://huggingface.co/docs/peft/")
    print("  • 示例: https://github.com/huggingface/peft/tree/main/examples")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用戶中斷")
    except Exception as e:
        print(f"\n程序執行出錯: {e}")
        import traceback
        traceback.print_exc()

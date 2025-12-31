"""
DPO (Direct Preference Optimization) 訓練

這個文件演示了 DPO 訓練方法，包括：
1. DPO 算法原理
2. 偏好數據處理
3. DPO 訓練配置
4. 完整訓練流程
5. 與 PPO 的比較

DPO 是一種無需獎勵模型的偏好優化方法，
直接從偏好數據學習，大幅簡化了 RLHF 流程。
"""

import os
import sys
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
import warnings

warnings.filterwarnings('ignore')


@dataclass
class DPOTrainingConfig:
    """DPO 訓練配置"""

    # 模型配置
    model_name: str = "gpt2"
    model_max_length: int = 512

    # DPO 超參數
    beta: float = 0.1  # DPO 溫度參數
    loss_type: str = "sigmoid"  # 損失函數類型："sigmoid", "hinge", "ipo"

    # 訓練配置
    output_dir: str = "./output/dpo_training"
    num_train_epochs: int = 3
    per_device_train_batch_size: int = 4
    per_device_eval_batch_size: int = 4
    gradient_accumulation_steps: int = 4
    learning_rate: float = 5e-5
    weight_decay: float = 0.01
    warmup_ratio: float = 0.1

    # 優化配置
    fp16: bool = False
    bf16: bool = False
    gradient_checkpointing: bool = True
    optim: str = "adamw_torch"
    max_grad_norm: float = 1.0

    # 日誌與保存
    logging_steps: int = 10
    save_strategy: str = "epoch"
    evaluation_strategy: str = "epoch"
    save_total_limit: int = 2
    report_to: str = "none"

    # 其他
    seed: int = 42
    max_prompt_length: int = 256
    max_length: int = 512


def explain_dpo_algorithm():
    """
    解釋 DPO 算法原理
    """
    print("\n" + "=" * 60)
    print("DPO 算法原理")
    print("=" * 60)

    explanation = """
DPO (Direct Preference Optimization) 是一種創新的偏好學習方法，
由 Anthropic 等機構在 2023 年提出，徹底改變了 RLHF 訓練流程。

核心創新:
• 無需獎勵模型 - 直接從偏好數據學習
• 簡化訓練 - 只需一步訓練即可
• 穩定性好 - 避免了 RL 訓練的不穩定性

數學原理:
傳統 RLHF 流程:
1. SFT: 訓練基礎模型
2. RM: 訓練獎勵模型
3. RL: 使用 PPO 優化策略

DPO 直接優化:
最大化 log σ(β * log(π_θ(y_w|x) / π_ref(y_w|x))
           - β * log(π_θ(y_l|x) / π_ref(y_l|x)))

其中:
- y_w: 偏好的回答 (chosen)
- y_l: 不偏好的回答 (rejected)
- π_θ: 當前策略
- π_ref: 參考策略
- β: 溫度參數
- σ: sigmoid 函數

直觀理解:
DPO 直接增加偏好回答的概率，同時降低不偏好回答的概率，
不需要顯式的獎勵模型作為中介。

優勢:
✓ 訓練簡單 - 只需標準的監督學習
✓ 穩定性好 - 無 RL 訓練的不穩定性
✓ 高效 - 節省獎勵模型訓練時間
✓ 效果好 - 在多個基準上優於 PPO

適用場景:
• 有成對偏好數據
• 希望簡化訓練流程
• 對穩定性要求高
• 資源受限
"""

    print(explanation)


def create_dpo_dataset():
    """
    創建 DPO 偏好數據集

    Returns:
        tuple: (train_dataset, eval_dataset)
    """
    print("\n" + "=" * 60)
    print("創建 DPO 偏好數據集")
    print("=" * 60)

    try:
        from datasets import Dataset

        # DPO 數據格式：prompt, chosen, rejected
        train_data = {
            "prompt": [
                "### Human: 什麼是機器學習？\n### Assistant:",
                "### Human: Python 的優點是什麼？\n### Assistant:",
                "### Human: 如何開始學習 AI？\n### Assistant:",
                "### Human: 什麼是深度學習？\n### Assistant:",
                "### Human: GPU 在深度學習中的作用？\n### Assistant:",
                "### Human: 解釋神經網絡？\n### Assistant:",
                "### Human: 如何防止過擬合？\n### Assistant:",
                "### Human: 什麼是 Transformer？\n### Assistant:",
                "### Human: 解釋注意力機制？\n### Assistant:",
                "### Human: 什麼是遷移學習？\n### Assistant:",
            ],
            "chosen": [
                "機器學習是人工智能的一個分支，它使用算法和統計模型讓計算機系統能夠從數據中學習和改進，而無需明確編程。主要包括監督學習、無監督學習和強化學習。",
                "Python 的主要優點包括：1) 語法簡潔易學，2) 豐富的第三方庫，3) 強大的社區支持，4) 廣泛應用於數據科學和機器學習，5) 跨平台兼容性好。",
                "建議學習路徑：1) 掌握 Python 編程基礎，2) 學習數學基礎（線性代數、微積分、概率論），3) 理解機器學習基本概念，4) 學習深度學習框架如 PyTorch，5) 通過實際項目鞏固知識。",
                "深度學習是機器學習的子領域，使用多層神經網絡學習數據的複雜特徵表示。它在圖像識別、語音識別、自然語言處理等領域取得了突破性進展。",
                "GPU 能夠並行處理大量計算，這對深度學習訓練至關重要。相比 CPU，GPU 可以將訓練速度提升 10-100 倍，使得訓練大型神經網絡成為可能。",
                "神經網絡是受人腦啟發的計算模型，由多層相互連接的節點組成。每個連接都有權重，通過反向傳播算法訓練調整權重，從而學習數據模式。",
                "防止過擬合的方法包括：1) 增加訓練數據，2) 使用正則化（L1/L2），3) 使用 Dropout，4) 早停法，5) 數據增強，6) 簡化模型，7) 交叉驗證。",
                "Transformer 是基於注意力機制的神經網絡架構，由 Google 在 2017 年提出。它徹底改變了 NLP 領域，是 GPT、BERT 等模型的基礎，主要優勢是並行處理和長距離依賴建模。",
                "注意力機制允許模型在處理序列時動態地關注不同位置的信息。它計算查詢與鍵的相似度，用相似度加權值，從而捕捉重要的上下文信息。",
                "遷移學習是將在一個任務上訓練的模型應用到相關新任務的技術。通過利用預訓練模型的知識，可以大幅減少訓練時間和所需數據量。",
            ],
            "rejected": [
                "機器學習就是讓電腦學習的技術。",
                "Python 很好用，大家都在用。",
                "直接開始學就可以了。",
                "深度學習就是很深的學習方法。",
                "GPU 是用來打遊戲的硬件。",
                "神經網絡是一種網絡結構。",
                "不要過擬合就好了。",
                "Transformer 是變形金剛電影。",
                "注意力機制就是注意一些東西。",
                "遷移學習就是把學習遷移過去。",
            ],
        }

        eval_data = {
            "prompt": [
                "### Human: 什麼是自然語言處理？\n### Assistant:",
                "### Human: 如何評估機器學習模型？\n### Assistant:",
            ],
            "chosen": [
                "自然語言處理（NLP）是人工智能的分支，專注於讓計算機理解和生成人類語言。應用包括機器翻譯、情感分析、問答系統等。",
                "評估方法取決於任務：分類使用準確率、F1 分數；回歸使用 MSE、RMSE。需要使用交叉驗證和獨立測試集避免過擬合。",
            ],
            "rejected": [
                "NLP 就是處理語言的技術。",
                "看看準確率就知道了。",
            ],
        }

        train_dataset = Dataset.from_dict(train_data)
        eval_dataset = Dataset.from_dict(eval_data)

        print(f"✓ 創建 DPO 數據集成功")
        print(f"  訓練集: {len(train_dataset)} 個樣本")
        print(f"  驗證集: {len(eval_dataset)} 個樣本")

        # 顯示樣本
        print(f"\n數據格式示例:")
        print("-" * 60)
        print(f"Prompt:\n{train_dataset[0]['prompt']}")
        print(f"\nChosen (好的回答):\n{train_dataset[0]['chosen'][:100]}...")
        print(f"\nRejected (差的回答):\n{train_dataset[0]['rejected'][:100]}...")
        print("-" * 60)

        return train_dataset, eval_dataset

    except Exception as e:
        print(f"✗ 創建數據集失敗: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def load_dpo_models(config: DPOTrainingConfig):
    """
    加載 DPO 訓練所需的模型

    Args:
        config: DPO 訓練配置

    Returns:
        tuple: (model, ref_model, tokenizer)
    """
    print("\n" + "=" * 60)
    print("加載 DPO 模型")
    print("=" * 60)

    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch

        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"使用設備: {device}")

        # 1. 加載分詞器
        print("\n1. 加載分詞器...")
        tokenizer = AutoTokenizer.from_pretrained(config.model_name)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        print("   ✓ 分詞器加載成功")

        # 2. 加載策略模型（要訓練的模型）
        print("2. 加載策略模型...")
        model = AutoModelForCausalLM.from_pretrained(
            config.model_name,
            torch_dtype=torch.float16 if config.fp16 else torch.float32,
        )
        print(f"   ✓ 策略模型參數: {model.num_parameters() / 1e6:.2f}M")

        # 3. 加載參考模型（凍結的原始模型）
        print("3. 加載參考模型（凍結參數）...")
        ref_model = AutoModelForCausalLM.from_pretrained(config.model_name)
        ref_model.eval()
        for param in ref_model.parameters():
            param.requires_grad = False
        print("   ✓ 參考模型已凍結")

        print("\n✓ 所有模型加載完成")

        return model, ref_model, tokenizer

    except Exception as e:
        print(f"✗ 加載模型失敗: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None


def create_dpo_trainer(model, ref_model, tokenizer, train_dataset, eval_dataset, config: DPOTrainingConfig):
    """
    創建 DPO 訓練器

    Args:
        model: 策略模型
        ref_model: 參考模型
        tokenizer: 分詞器
        train_dataset: 訓練數據集
        eval_dataset: 驗證數據集
        config: 訓練配置

    Returns:
        DPOTrainer
    """
    print("\n" + "=" * 60)
    print("創建 DPO 訓練器")
    print("=" * 60)

    try:
        from trl import DPOTrainer, DPOConfig
        import torch

        # 創建輸出目錄
        os.makedirs(config.output_dir, exist_ok=True)

        # 創建訓練配置
        training_args = DPOConfig(
            # 輸出配置
            output_dir=config.output_dir,
            overwrite_output_dir=True,

            # DPO 參數
            beta=config.beta,
            loss_type=config.loss_type,

            # 訓練參數
            num_train_epochs=config.num_train_epochs,
            per_device_train_batch_size=config.per_device_train_batch_size,
            per_device_eval_batch_size=config.per_device_eval_batch_size,
            gradient_accumulation_steps=config.gradient_accumulation_steps,

            # 優化器配置
            learning_rate=config.learning_rate,
            weight_decay=config.weight_decay,
            warmup_ratio=config.warmup_ratio,
            max_grad_norm=config.max_grad_norm,
            optim=config.optim,

            # 精度配置
            fp16=config.fp16 and torch.cuda.is_available(),
            bf16=config.bf16 and torch.cuda.is_available(),

            # 記憶體優化
            gradient_checkpointing=config.gradient_checkpointing,

            # 日誌與保存
            logging_steps=config.logging_steps,
            save_strategy=config.save_strategy,
            evaluation_strategy=config.evaluation_strategy,
            save_total_limit=config.save_total_limit,
            report_to=config.report_to,

            # 其他
            seed=config.seed,
            max_prompt_length=config.max_prompt_length,
            max_length=config.max_length,
        )

        print("\nDPO 訓練配置:")
        print(f"  Beta (溫度參數): {config.beta}")
        print(f"  Loss Type: {config.loss_type}")
        print(f"  Epochs: {config.num_train_epochs}")
        print(f"  Batch Size: {config.per_device_train_batch_size}")
        print(f"  Learning Rate: {config.learning_rate}")
        print(f"  Max Prompt Length: {config.max_prompt_length}")
        print(f"  Max Length: {config.max_length}")

        # 創建訓練器
        trainer = DPOTrainer(
            model=model,
            ref_model=ref_model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            tokenizer=tokenizer,
        )

        print("\n✓ DPO 訓練器創建成功")

        return trainer

    except Exception as e:
        print(f"✗ 創建訓練器失敗: {e}")
        import traceback
        traceback.print_exc()
        return None


def train_dpo_model(trainer):
    """
    訓練 DPO 模型

    Args:
        trainer: DPO 訓練器

    Returns:
        訓練結果
    """
    print("\n" + "=" * 60)
    print("開始 DPO 訓練")
    print("=" * 60)

    try:
        # 訓練
        train_result = trainer.train()

        # 顯示訓練結果
        print("\n" + "=" * 60)
        print("DPO 訓練完成")
        print("=" * 60)

        metrics = train_result.metrics
        print(f"\n訓練指標:")
        print(f"  訓練損失: {metrics.get('train_loss', 'N/A'):.4f}")
        print(f"  訓練步數: {metrics.get('train_steps', 'N/A')}")
        print(f"  訓練時長: {metrics.get('train_runtime', 0):.2f} 秒")

        # 保存訓練指標
        trainer.save_metrics("train", metrics)

        return train_result

    except Exception as e:
        print(f"✗ 訓練失敗: {e}")
        import traceback
        traceback.print_exc()
        return None


def compare_dpo_with_ppo():
    """
    比較 DPO 和 PPO
    """
    print("\n" + "=" * 60)
    print("DPO vs PPO 比較")
    print("=" * 60)

    comparison = """
┌────────────────────┬──────────────────────┬──────────────────────┐
│      特性          │         DPO          │         PPO          │
├────────────────────┼──────────────────────┼──────────────────────┤
│  訓練步驟          │  1 步（SFT+偏好）    │  3 步（SFT+RM+RL）   │
│  需要獎勵模型      │  ❌ 不需要           │  ✓ 需要              │
│  訓練穩定性        │  ✓ 穩定              │  ⚠️  可能不穩定      │
│  實現複雜度        │  ✓ 簡單              │  ⚠️  較複雜          │
│  計算成本          │  ✓ 較低              │  ⚠️  較高            │
│  樣本效率          │  ✓ 高                │  ⚠️  中等            │
│  超參數敏感度      │  ✓ 低                │  ⚠️  高              │
│  理論保證          │  ✓ 有                │  ✓ 有                │
│  靈活性            │  ⚠️  較低            │  ✓ 高                │
│  適用場景          │  有偏好數據          │  需要複雜獎勵設計    │
└────────────────────┴──────────────────────┴──────────────────────┘

詳細比較:

1. 訓練流程:
   DPO: SFT → DPO 訓練（1 步完成偏好優化）
   PPO: SFT → 獎勵模型 → PPO 訓練（3 步流程）

2. 數據需求:
   DPO: 需要成對偏好數據 (chosen, rejected)
   PPO: 需要獎勵模型訓練數據 + 查詢數據

3. 模型需求:
   DPO: 策略模型 + 參考模型
   PPO: 策略模型 + 價值模型 + 參考模型 + 獎勵模型

4. 優化目標:
   DPO: 直接最大化偏好概率差異
   PPO: 通過獎勵信號優化策略

5. 適用場景:
   DPO:
     • 有高質量偏好數據
     • 資源有限
     • 需要快速迭代
     • 對穩定性要求高

   PPO:
     • 獎勵函數複雜
     • 需要多輪迭代優化
     • 有充足計算資源
     • 需要精細控制

6. 實際效果:
   • 在多個基準測試中，DPO 效果與 PPO 相當甚至更好
   • DPO 訓練更穩定，更容易調優
   • PPO 在某些複雜場景下可能更靈活

建議:
• 優先嘗試 DPO（更簡單、更穩定）
• 如果 DPO 效果不理想，再考慮 PPO
• 對於特殊獎勵設計需求，使用 PPO
"""

    print(comparison)


def test_dpo_model(model, tokenizer, test_prompts: List[str]):
    """
    測試訓練後的 DPO 模型

    Args:
        model: 訓練後的模型
        tokenizer: 分詞器
        test_prompts: 測試提示列表
    """
    print("\n" + "=" * 60)
    print("測試 DPO 訓練後的模型")
    print("=" * 60)

    try:
        import torch

        model.eval()
        device = next(model.parameters()).device

        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n測試 {i}/{len(test_prompts)}")
            print(f"輸入: {prompt}")
            print("-" * 60)

            # 編碼
            inputs = tokenizer(prompt, return_tensors="pt")
            inputs = {k: v.to(device) for k, v in inputs.items()}

            # 生成
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=100,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=tokenizer.pad_token_id,
                )

            # 解碼
            generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            print(f"輸出:\n{generated_text}")
            print("-" * 60)

    except Exception as e:
        print(f"✗ 測試失敗: {e}")
        import traceback
        traceback.print_exc()


def main():
    """
    主函數：執行完整的 DPO 訓練流程
    """
    print("=" * 60)
    print("DPO 直接偏好優化訓練")
    print("=" * 60)

    # 1. 解釋 DPO 算法
    explain_dpo_algorithm()

    # 2. 創建配置
    config = DPOTrainingConfig(
        model_name="gpt2",
        beta=0.1,
        num_train_epochs=1,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=2,
        output_dir="./output/dpo_training",
    )

    # 3. 創建數據集
    train_dataset, eval_dataset = create_dpo_dataset()
    if train_dataset is None:
        print("數據集創建失敗，退出程序")
        return

    # 4. 加載模型
    model, ref_model, tokenizer = load_dpo_models(config)
    if model is None:
        print("模型加載失敗，退出程序")
        return

    # 5. 創建訓練器
    trainer = create_dpo_trainer(model, ref_model, tokenizer, train_dataset, eval_dataset, config)
    if trainer is None:
        print("訓練器創建失敗，退出程序")
        return

    # 6. 訓練模型
    train_result = train_dpo_model(trainer)
    if train_result is None:
        print("訓練失敗")
        return

    # 7. 評估模型
    print("\n" + "=" * 60)
    print("評估模型")
    print("=" * 60)
    eval_result = trainer.evaluate()
    print(f"驗證損失: {eval_result.get('eval_loss', 'N/A'):.4f}")

    # 8. 保存模型
    print("\n" + "=" * 60)
    print("保存模型")
    print("=" * 60)
    final_model_path = os.path.join(config.output_dir, "final_model")
    trainer.save_model(final_model_path)
    tokenizer.save_pretrained(final_model_path)
    print(f"✓ 模型保存到: {final_model_path}")

    # 9. 測試模型
    test_prompts = [
        "### Human: 什麼是機器學習？\n### Assistant:",
        "### Human: Python 有什麼優點？\n### Assistant:",
    ]
    test_dpo_model(model, tokenizer, test_prompts)

    # 10. DPO vs PPO 比較
    compare_dpo_with_ppo()

    # 11. 總結
    print("\n" + "=" * 60)
    print("DPO 訓練完成！")
    print("=" * 60)

    print("\nDPO 的優勢:")
    print("  ✓ 無需獎勵模型 - 簡化訓練流程")
    print("  ✓ 訓練穩定 - 避免 RL 訓練的不穩定性")
    print("  ✓ 實現簡單 - 標準的監督學習")
    print("  ✓ 效果優秀 - 在多個基準上表現出色")
    print("  ✓ 資源效率高 - 減少訓練成本")

    print("\n何時使用 DPO:")
    print("  • 有成對偏好數據")
    print("  • 希望簡化訓練流程")
    print("  • 資源有限")
    print("  • 對穩定性要求高")

    print("\n參考論文:")
    print("  • Direct Preference Optimization (2023)")
    print("  • https://arxiv.org/abs/2305.18290")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用戶中斷")
    except Exception as e:
        print(f"\n程序執行出錯: {e}")
        import traceback
        traceback.print_exc()

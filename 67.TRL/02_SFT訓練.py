"""
SFT (Supervised Fine-Tuning) 監督微調訓練

這個文件演示了完整的 SFT 訓練流程，包括：
1. 數據加載與預處理
2. 模型配置與初始化
3. 訓練參數設置
4. 完整的訓練循環
5. 模型評估與保存
6. 訓練監控與日誌

SFT 是 RLHF 流程的第一步，使用高質量的指令-回答對訓練模型，
使其學會基本的對話格式和回答能力。
"""

import os
import sys
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
import warnings

warnings.filterwarnings('ignore')


@dataclass
class SFTTrainingConfig:
    """SFT 訓練配置類"""

    # 模型配置
    model_name: str = "gpt2"
    model_max_length: int = 512

    # 數據配置
    dataset_name: str = "timdettmers/openassistant-guanaco"
    dataset_text_field: str = "text"
    max_samples: Optional[int] = None  # None 表示使用全部數據

    # 訓練配置
    output_dir: str = "./output/sft_training"
    num_train_epochs: int = 3
    per_device_train_batch_size: int = 4
    per_device_eval_batch_size: int = 4
    gradient_accumulation_steps: int = 4
    learning_rate: float = 2e-5
    weight_decay: float = 0.01
    warmup_ratio: float = 0.1

    # 優化配置
    fp16: bool = False  # 混合精度訓練
    bf16: bool = False  # BF16 訓練（A100 GPU）
    gradient_checkpointing: bool = True  # 梯度檢查點，節省記憶體
    optim: str = "adamw_torch"

    # 日誌與保存
    logging_steps: int = 10
    save_strategy: str = "epoch"
    evaluation_strategy: str = "epoch"
    save_total_limit: int = 3
    report_to: str = "none"  # "tensorboard", "wandb", "none"

    # 其他
    seed: int = 42
    max_grad_norm: float = 1.0


def load_and_prepare_dataset(config: SFTTrainingConfig):
    """
    加載並準備訓練數據集

    Args:
        config: SFT 訓練配置

    Returns:
        tuple: (train_dataset, eval_dataset)
    """
    print("\n" + "=" * 60)
    print("加載數據集")
    print("=" * 60)

    try:
        from datasets import load_dataset

        print(f"數據集: {config.dataset_name}")

        # 加載數據集
        dataset = load_dataset(config.dataset_name, split="train")

        print(f"原始數據量: {len(dataset)} 個樣本")

        # 限制樣本數量（用於快速測試）
        if config.max_samples is not None:
            dataset = dataset.select(range(min(config.max_samples, len(dataset))))
            print(f"使用數據量: {len(dataset)} 個樣本")

        # 查看樣本
        print(f"\n樣本示例:")
        print("-" * 60)
        print(dataset[0][config.dataset_text_field][:200] + "...")
        print("-" * 60)

        # 分割訓練集和驗證集
        split_dataset = dataset.train_test_split(test_size=0.1, seed=config.seed)
        train_dataset = split_dataset["train"]
        eval_dataset = split_dataset["test"]

        print(f"\n訓練集: {len(train_dataset)} 個樣本")
        print(f"驗證集: {len(eval_dataset)} 個樣本")

        return train_dataset, eval_dataset

    except Exception as e:
        print(f"✗ 加載數據集失敗: {e}")
        print("\n創建示例數據集作為替代...")
        return create_demo_dataset()


def create_demo_dataset():
    """
    創建示例數據集（用於演示或數據加載失敗時）

    Returns:
        tuple: (train_dataset, eval_dataset)
    """
    try:
        from datasets import Dataset

        # 創建示例對話數據
        train_data = {
            "text": [
                "### Human: 什麼是機器學習？\n### Assistant: 機器學習是人工智能的一個分支，它使用算法和統計模型讓計算機系統能夠從數據中學習和改進，而無需明確編程。",
                "### Human: Python 有什麼優點？\n### Assistant: Python 的主要優點包括：1) 語法簡潔易學 2) 豐富的第三方庫 3) 強大的社區支持 4) 廣泛的應用領域，特別是在數據科學和機器學習方面。",
                "### Human: 如何開始學習深度學習？\n### Assistant: 建議的學習路徑是：1) 掌握 Python 編程基礎 2) 學習數學基礎（線性代數、微積分、概率論）3) 理解機器學習基本概念 4) 學習深度學習框架如 PyTorch 或 TensorFlow 5) 動手實踐項目。",
                "### Human: 什麼是神經網絡？\n### Assistant: 神經網絡是一種受人腦啟發的計算模型，由多層相互連接的節點（神經元）組成。每個連接都有權重，通過訓練調整這些權重來學習數據中的模式。",
                "### Human: 解釋什麼是過擬合？\n### Assistant: 過擬合是指模型在訓練數據上表現很好，但在新數據上表現不佳的現象。這通常是因為模型過於複雜，學習了訓練數據中的噪聲而不是真實的模式。可以通過正則化、dropout、數據增強等方法來防止過擬合。",
                "### Human: 什麼是 Transformer？\n### Assistant: Transformer 是一種基於注意力機制的神經網絡架構，由 Google 在 2017 年提出。它徹底改變了自然語言處理領域，是 GPT、BERT 等模型的基礎。主要特點是並行處理和長距離依賴建模能力。",
                "### Human: 如何評估機器學習模型？\n### Assistant: 評估方法取決於任務類型：1) 分類任務：準確率、精確率、召回率、F1 分數 2) 回歸任務：MSE、RMSE、MAE、R² 3) 排名任務：NDCG、MAP。同時要注意使用交叉驗證和獨立測試集。",
                "### Human: 什麼是遷移學習？\n### Assistant: 遷移學習是一種機器學習技術，將在一個任務上訓練的模型應用到相關的新任務上。通過利用預訓練模型的知識，可以大幅減少訓練時間和所需數據量，特別適合數據稀缺的場景。",
            ]
        }

        eval_data = {
            "text": [
                "### Human: 什麼是自然語言處理？\n### Assistant: 自然語言處理（NLP）是人工智能的一個分支，專注於讓計算機理解、解釋和生成人類語言。應用包括機器翻譯、情感分析、問答系統等。",
                "### Human: GPU 在深度學習中的作用？\n### Assistant: GPU（圖形處理器）能夠並行處理大量計算，這對深度學習訓練至關重要。相比 CPU，GPU 可以將訓練速度提升 10-100 倍，使得訓練大型神經網絡成為可能。",
            ]
        }

        train_dataset = Dataset.from_dict(train_data)
        eval_dataset = Dataset.from_dict(eval_data)

        print(f"✓ 創建示例數據集成功")
        print(f"  訓練集: {len(train_dataset)} 個樣本")
        print(f"  驗證集: {len(eval_dataset)} 個樣本")

        return train_dataset, eval_dataset

    except Exception as e:
        print(f"✗ 創建示例數據集失敗: {e}")
        return None, None


def load_model_and_tokenizer(config: SFTTrainingConfig):
    """
    加載模型和分詞器

    Args:
        config: SFT 訓練配置

    Returns:
        tuple: (model, tokenizer)
    """
    print("\n" + "=" * 60)
    print("加載模型和分詞器")
    print("=" * 60)

    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch

        print(f"模型: {config.model_name}")

        # 加載分詞器
        tokenizer = AutoTokenizer.from_pretrained(
            config.model_name,
            trust_remote_code=True,
            model_max_length=config.model_max_length,
        )

        # 設置特殊 token
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            print("設置 pad_token = eos_token")

        # 加載模型
        model = AutoModelForCausalLM.from_pretrained(
            config.model_name,
            trust_remote_code=True,
            torch_dtype=torch.float16 if config.fp16 else torch.float32,
        )

        print(f"✓ 模型加載成功")
        print(f"  參數量: {model.num_parameters() / 1e6:.2f}M")
        print(f"  詞彙表大小: {len(tokenizer)}")

        return model, tokenizer

    except Exception as e:
        print(f"✗ 加載模型失敗: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def create_sft_trainer(model, tokenizer, train_dataset, eval_dataset, config: SFTTrainingConfig):
    """
    創建 SFT 訓練器

    Args:
        model: 預訓練模型
        tokenizer: 分詞器
        train_dataset: 訓練數據集
        eval_dataset: 驗證數據集
        config: 訓練配置

    Returns:
        SFTTrainer: 訓練器對象
    """
    print("\n" + "=" * 60)
    print("創建 SFT 訓練器")
    print("=" * 60)

    try:
        from trl import SFTTrainer, SFTConfig
        import torch

        # 創建輸出目錄
        os.makedirs(config.output_dir, exist_ok=True)

        # 檢測設備
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"使用設備: {device}")

        # 創建訓練配置
        training_args = SFTConfig(
            # 輸出配置
            output_dir=config.output_dir,
            overwrite_output_dir=True,

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
            max_seq_length=config.model_max_length,
            dataset_text_field=config.dataset_text_field,
        )

        print("\n訓練配置:")
        print(f"  Epochs: {config.num_train_epochs}")
        print(f"  Batch Size: {config.per_device_train_batch_size}")
        print(f"  Gradient Accumulation: {config.gradient_accumulation_steps}")
        print(f"  Effective Batch Size: {config.per_device_train_batch_size * config.gradient_accumulation_steps}")
        print(f"  Learning Rate: {config.learning_rate}")
        print(f"  Warmup Ratio: {config.warmup_ratio}")
        print(f"  FP16: {training_args.fp16}")
        print(f"  BF16: {training_args.bf16}")
        print(f"  Gradient Checkpointing: {config.gradient_checkpointing}")

        # 創建訓練器
        trainer = SFTTrainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            tokenizer=tokenizer,
        )

        print("\n✓ 訓練器創建成功")

        return trainer

    except Exception as e:
        print(f"✗ 創建訓練器失敗: {e}")
        import traceback
        traceback.print_exc()
        return None


def train_model(trainer):
    """
    執行模型訓練

    Args:
        trainer: SFT 訓練器

    Returns:
        訓練結果
    """
    print("\n" + "=" * 60)
    print("開始訓練")
    print("=" * 60)

    try:
        # 訓練
        train_result = trainer.train()

        # 顯示訓練結果
        print("\n" + "=" * 60)
        print("訓練完成")
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


def evaluate_model(trainer):
    """
    評估模型性能

    Args:
        trainer: SFT 訓練器

    Returns:
        評估結果
    """
    print("\n" + "=" * 60)
    print("評估模型")
    print("=" * 60)

    try:
        # 評估
        eval_result = trainer.evaluate()

        # 顯示評估結果
        print(f"\n評估指標:")
        print(f"  驗證損失: {eval_result.get('eval_loss', 'N/A'):.4f}")
        print(f"  評估步數: {eval_result.get('eval_steps', 'N/A')}")
        print(f"  評估時長: {eval_result.get('eval_runtime', 0):.2f} 秒")

        # 保存評估指標
        trainer.save_metrics("eval", eval_result)

        return eval_result

    except Exception as e:
        print(f"✗ 評估失敗: {e}")
        import traceback
        traceback.print_exc()
        return None


def save_model(trainer, tokenizer, config: SFTTrainingConfig):
    """
    保存訓練好的模型

    Args:
        trainer: SFT 訓練器
        tokenizer: 分詞器
        config: 訓練配置
    """
    print("\n" + "=" * 60)
    print("保存模型")
    print("=" * 60)

    try:
        # 保存模型
        final_model_path = os.path.join(config.output_dir, "final_model")
        os.makedirs(final_model_path, exist_ok=True)

        trainer.save_model(final_model_path)
        tokenizer.save_pretrained(final_model_path)

        print(f"✓ 模型保存到: {final_model_path}")

        # 保存訓練配置
        import json
        config_path = os.path.join(config.output_dir, "training_config.json")
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config.__dict__, f, indent=2, ensure_ascii=False)

        print(f"✓ 訓練配置保存到: {config_path}")

    except Exception as e:
        print(f"✗ 保存模型失敗: {e}")
        import traceback
        traceback.print_exc()


def test_trained_model(model, tokenizer, test_prompts: List[str]):
    """
    測試訓練後的模型

    Args:
        model: 訓練後的模型
        tokenizer: 分詞器
        test_prompts: 測試提示列表
    """
    print("\n" + "=" * 60)
    print("測試訓練後的模型")
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
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=tokenizer.pad_token_id,
                )

            # 解碼
            generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            print(f"輸出: {generated_text}")
            print("-" * 60)

    except Exception as e:
        print(f"✗ 測試失敗: {e}")
        import traceback
        traceback.print_exc()


def main():
    """
    主函數：執行完整的 SFT 訓練流程
    """
    print("=" * 60)
    print("SFT 監督微調訓練")
    print("=" * 60)

    # 1. 創建配置
    config = SFTTrainingConfig(
        model_name="gpt2",
        num_train_epochs=1,  # 演示用，實際訓練建議 3-5 epochs
        per_device_train_batch_size=2,
        gradient_accumulation_steps=2,
        max_samples=50,  # 限制樣本數量以加快演示
        output_dir="./output/sft_training",
    )

    # 2. 加載數據
    train_dataset, eval_dataset = load_and_prepare_dataset(config)
    if train_dataset is None:
        print("數據集加載失敗，退出程序")
        return

    # 3. 加載模型
    model, tokenizer = load_model_and_tokenizer(config)
    if model is None:
        print("模型加載失敗，退出程序")
        return

    # 4. 創建訓練器
    trainer = create_sft_trainer(model, tokenizer, train_dataset, eval_dataset, config)
    if trainer is None:
        print("訓練器創建失敗，退出程序")
        return

    # 5. 訓練模型
    train_result = train_model(trainer)
    if train_result is None:
        print("訓練失敗")
        return

    # 6. 評估模型
    evaluate_model(trainer)

    # 7. 保存模型
    save_model(trainer, tokenizer, config)

    # 8. 測試模型
    test_prompts = [
        "### Human: 什麼是深度學習？\n### Assistant:",
        "### Human: 如何使用 Python？\n### Assistant:",
    ]
    test_trained_model(model, tokenizer, test_prompts)

    # 9. 總結
    print("\n" + "=" * 60)
    print("SFT 訓練流程完成！")
    print("=" * 60)
    print(f"\n模型保存在: {config.output_dir}")
    print("\n下一步:")
    print("  1. 使用訓練好的模型進行推理")
    print("  2. 訓練獎勵模型（查看 03_獎勵模型.py）")
    print("  3. 使用 PPO 或 DPO 進行強化學習訓練")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用戶中斷")
    except Exception as e:
        print(f"\n程序執行出錯: {e}")
        import traceback
        traceback.print_exc()

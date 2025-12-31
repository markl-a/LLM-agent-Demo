"""
獎勵模型 (Reward Model) 訓練

這個文件演示了獎勵模型的訓練過程，包括：
1. 偏好數據準備
2. 獎勵模型架構
3. 成對比較訓練
4. 模型評估
5. 獎勵預測

獎勵模型是 RLHF 流程的第二步，它學習人類偏好，
為生成的回答打分，用於後續的強化學習訓練。
"""

import os
import sys
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass
import warnings

warnings.filterwarnings('ignore')


@dataclass
class RewardModelConfig:
    """獎勵模型訓練配置"""

    # 模型配置
    model_name: str = "gpt2"
    model_max_length: int = 512

    # 數據配置
    dataset_name: str = "Anthropic/hh-rlhf"
    max_samples: Optional[int] = None

    # 訓練配置
    output_dir: str = "./output/reward_model"
    num_train_epochs: int = 1
    per_device_train_batch_size: int = 4
    per_device_eval_batch_size: int = 4
    gradient_accumulation_steps: int = 4
    learning_rate: float = 1e-5
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


def create_preference_dataset():
    """
    創建偏好數據集（成對比較數據）

    Returns:
        tuple: (train_dataset, eval_dataset)
    """
    print("\n" + "=" * 60)
    print("創建偏好數據集")
    print("=" * 60)

    try:
        from datasets import Dataset

        # 創建示例偏好數據
        # 每個樣本包含：prompt（問題）、chosen（好的回答）、rejected（差的回答）
        train_data = {
            "prompt": [
                "### Human: 什麼是機器學習？\n### Assistant: ",
                "### Human: Python 有什麼優點？\n### Assistant: ",
                "### Human: 如何開始學習 AI？\n### Assistant: ",
                "### Human: 什麼是深度學習？\n### Assistant: ",
                "### Human: GPU 的作用是什麼？\n### Assistant: ",
                "### Human: 什麼是神經網絡？\n### Assistant: ",
                "### Human: 如何防止過擬合？\n### Assistant: ",
                "### Human: 什麼是 Transformer？\n### Assistant: ",
            ],
            "chosen": [
                "機器學習是人工智能的一個分支，它使用算法和統計模型讓計算機系統能夠從數據中學習和改進，而無需明確編程。主要包括監督學習、無監督學習和強化學習三大類。",
                "Python 的主要優點包括：1) 語法簡潔易學，適合初學者 2) 擁有豐富的第三方庫和框架 3) 強大的社區支持 4) 廣泛應用於數據科學、機器學習、Web 開發等領域 5) 跨平台兼容性好。",
                "建議的學習路徑：1) 掌握 Python 編程基礎 2) 學習數學基礎（線性代數、微積分、概率論）3) 理解機器學習基本概念和算法 4) 學習深度學習框架如 PyTorch 或 TensorFlow 5) 通過實際項目鞏固知識。",
                "深度學習是機器學習的一個子領域，使用多層神經網絡來學習數據的複雜特徵表示。它在圖像識別、語音識別、自然語言處理等領域取得了突破性進展，是當前 AI 技術的核心。",
                "GPU（圖形處理器）在深度學習中起到關鍵作用，因為它能夠並行處理大量計算。相比 CPU，GPU 可以將訓練速度提升 10-100 倍，使得訓練大型神經網絡成為可能。現代深度學習幾乎都依賴 GPU 加速。",
                "神經網絡是一種受人腦啟發的計算模型，由多層相互連接的節點（神經元）組成。每個連接都有權重，通過反向傳播算法訓練調整這些權重，從而學習數據中的複雜模式。",
                "防止過擬合的方法包括：1) 增加訓練數據 2) 使用正則化（L1/L2）3) 使用 Dropout 4) 早停法（Early Stopping）5) 數據增強 6) 簡化模型複雜度 7) 交叉驗證。",
                "Transformer 是一種基於注意力機制的神經網絡架構，由 Google 在 2017 年提出。它徹底改變了自然語言處理領域，是 GPT、BERT 等先進模型的基礎。主要優勢是並行處理能力和長距離依賴建模能力。",
            ],
            "rejected": [
                "機器學習就是讓電腦學習。",
                "Python 很好用。",
                "直接學就好了。",
                "深度學習就是很深的學習。",
                "GPU 用來打遊戲的。",
                "神經網絡是一種網絡。",
                "不知道。",
                "Transformer 是變形金剛。",
            ],
        }

        eval_data = {
            "prompt": [
                "### Human: 什麼是自然語言處理？\n### Assistant: ",
                "### Human: 如何評估模型？\n### Assistant: ",
            ],
            "chosen": [
                "自然語言處理（NLP）是人工智能的一個分支，專注於讓計算機理解、解釋和生成人類語言。應用包括機器翻譯、情感分析、問答系統、文本摘要等。",
                "評估方法取決於任務類型：分類任務使用準確率、F1 分數等；回歸任務使用 MSE、RMSE 等。同時要注意使用交叉驗證和獨立測試集，避免過擬合。",
            ],
            "rejected": [
                "NLP 就是處理語言。",
                "看看準確率就好。",
            ],
        }

        train_dataset = Dataset.from_dict(train_data)
        eval_dataset = Dataset.from_dict(eval_data)

        print(f"✓ 創建偏好數據集成功")
        print(f"  訓練集: {len(train_dataset)} 個樣本")
        print(f"  驗證集: {len(eval_dataset)} 個樣本")

        # 顯示樣本
        print(f"\n樣本示例:")
        print("-" * 60)
        print(f"Prompt: {train_dataset[0]['prompt']}")
        print(f"Chosen: {train_dataset[0]['chosen'][:80]}...")
        print(f"Rejected: {train_dataset[0]['rejected'][:80]}...")
        print("-" * 60)

        return train_dataset, eval_dataset

    except Exception as e:
        print(f"✗ 創建偏好數據集失敗: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def load_reward_model_and_tokenizer(config: RewardModelConfig):
    """
    加載獎勵模型和分詞器

    Args:
        config: 獎勵模型配置

    Returns:
        tuple: (model, tokenizer)
    """
    print("\n" + "=" * 60)
    print("加載獎勵模型")
    print("=" * 60)

    try:
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
        import torch

        print(f"基礎模型: {config.model_name}")

        # 加載分詞器
        tokenizer = AutoTokenizer.from_pretrained(
            config.model_name,
            trust_remote_code=True,
        )

        # 設置特殊 token
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            print("設置 pad_token = eos_token")

        # 加載序列分類模型（輸出單一分數）
        model = AutoModelForSequenceClassification.from_pretrained(
            config.model_name,
            num_labels=1,  # 獎勵模型輸出單一分數
            trust_remote_code=True,
            torch_dtype=torch.float16 if config.fp16 else torch.float32,
        )

        print(f"✓ 獎勵模型加載成功")
        print(f"  參數量: {model.num_parameters() / 1e6:.2f}M")
        print(f"  輸出: 單一獎勵分數")

        return model, tokenizer

    except Exception as e:
        print(f"✗ 加載獎勵模型失敗: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def create_reward_trainer(model, tokenizer, train_dataset, eval_dataset, config: RewardModelConfig):
    """
    創建獎勵模型訓練器

    Args:
        model: 獎勵模型
        tokenizer: 分詞器
        train_dataset: 訓練數據集
        eval_dataset: 驗證數據集
        config: 訓練配置

    Returns:
        RewardTrainer: 訓練器對象
    """
    print("\n" + "=" * 60)
    print("創建獎勵模型訓練器")
    print("=" * 60)

    try:
        from trl import RewardTrainer, RewardConfig
        import torch

        # 創建輸出目錄
        os.makedirs(config.output_dir, exist_ok=True)

        # 檢測設備
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"使用設備: {device}")

        # 創建訓練配置
        training_args = RewardConfig(
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
            max_length=config.model_max_length,
        )

        print("\n訓練配置:")
        print(f"  Epochs: {config.num_train_epochs}")
        print(f"  Batch Size: {config.per_device_train_batch_size}")
        print(f"  Learning Rate: {config.learning_rate}")
        print(f"  Max Length: {config.model_max_length}")

        # 創建訓練器
        trainer = RewardTrainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            tokenizer=tokenizer,
        )

        print("\n✓ 獎勵模型訓練器創建成功")

        return trainer

    except Exception as e:
        print(f"✗ 創建訓練器失敗: {e}")
        import traceback
        traceback.print_exc()
        return None


def train_reward_model(trainer):
    """
    訓練獎勵模型

    Args:
        trainer: 獎勵模型訓練器

    Returns:
        訓練結果
    """
    print("\n" + "=" * 60)
    print("開始訓練獎勵模型")
    print("=" * 60)

    try:
        # 訓練
        train_result = trainer.train()

        # 顯示訓練結果
        print("\n" + "=" * 60)
        print("獎勵模型訓練完成")
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


def evaluate_reward_model(trainer):
    """
    評估獎勵模型

    Args:
        trainer: 獎勵模型訓練器

    Returns:
        評估結果
    """
    print("\n" + "=" * 60)
    print("評估獎勵模型")
    print("=" * 60)

    try:
        # 評估
        eval_result = trainer.evaluate()

        # 顯示評估結果
        print(f"\n評估指標:")
        print(f"  驗證損失: {eval_result.get('eval_loss', 'N/A'):.4f}")
        print(f"  準確率: {eval_result.get('eval_accuracy', 'N/A')}")

        # 保存評估指標
        trainer.save_metrics("eval", eval_result)

        return eval_result

    except Exception as e:
        print(f"✗ 評估失敗: {e}")
        import traceback
        traceback.print_exc()
        return None


def predict_rewards(model, tokenizer, texts: List[str]):
    """
    使用訓練好的獎勵模型預測文本的獎勵分數

    Args:
        model: 訓練好的獎勵模型
        tokenizer: 分詞器
        texts: 要評分的文本列表

    Returns:
        List[float]: 獎勵分數列表
    """
    print("\n" + "=" * 60)
    print("預測獎勵分數")
    print("=" * 60)

    try:
        import torch

        model.eval()
        device = next(model.parameters()).device

        rewards = []

        for i, text in enumerate(texts, 1):
            print(f"\n文本 {i}/{len(texts)}:")
            print(f"{text[:100]}...")

            # 編碼
            inputs = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True,
            )
            inputs = {k: v.to(device) for k, v in inputs.items()}

            # 預測
            with torch.no_grad():
                outputs = model(**inputs)
                reward = outputs.logits[0, 0].item()

            rewards.append(reward)
            print(f"獎勵分數: {reward:.4f}")

        return rewards

    except Exception as e:
        print(f"✗ 預測失敗: {e}")
        import traceback
        traceback.print_exc()
        return []


def compare_responses(model, tokenizer, prompt: str, response1: str, response2: str):
    """
    比較兩個回答的質量

    Args:
        model: 獎勵模型
        tokenizer: 分詞器
        prompt: 問題
        response1: 回答1
        response2: 回答2
    """
    print("\n" + "=" * 60)
    print("比較回答質量")
    print("=" * 60)

    try:
        # 組合文本
        text1 = prompt + response1
        text2 = prompt + response2

        # 預測獎勵
        rewards = predict_rewards(model, tokenizer, [text1, text2])

        if len(rewards) == 2:
            print("\n" + "=" * 60)
            print("比較結果")
            print("=" * 60)
            print(f"\n問題: {prompt}")
            print(f"\n回答 1 (獎勵: {rewards[0]:.4f}):")
            print(response1)
            print(f"\n回答 2 (獎勵: {rewards[1]:.4f}):")
            print(response2)

            if rewards[0] > rewards[1]:
                print(f"\n✓ 回答 1 更好 (差距: {rewards[0] - rewards[1]:.4f})")
            elif rewards[1] > rewards[0]:
                print(f"\n✓ 回答 2 更好 (差距: {rewards[1] - rewards[0]:.4f})")
            else:
                print(f"\n= 兩個回答質量相當")

    except Exception as e:
        print(f"✗ 比較失敗: {e}")
        import traceback
        traceback.print_exc()


def main():
    """
    主函數：執行完整的獎勵模型訓練流程
    """
    print("=" * 60)
    print("獎勵模型訓練")
    print("=" * 60)

    # 1. 創建配置
    config = RewardModelConfig(
        model_name="gpt2",
        num_train_epochs=1,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=2,
        output_dir="./output/reward_model",
    )

    # 2. 創建偏好數據集
    train_dataset, eval_dataset = create_preference_dataset()
    if train_dataset is None:
        print("數據集創建失敗，退出程序")
        return

    # 3. 加載獎勵模型
    model, tokenizer = load_reward_model_and_tokenizer(config)
    if model is None:
        print("模型加載失敗，退出程序")
        return

    # 4. 創建訓練器
    trainer = create_reward_trainer(model, tokenizer, train_dataset, eval_dataset, config)
    if trainer is None:
        print("訓練器創建失敗，退出程序")
        return

    # 5. 訓練模型
    train_result = train_reward_model(trainer)
    if train_result is None:
        print("訓練失敗")
        return

    # 6. 評估模型
    evaluate_reward_model(trainer)

    # 7. 保存模型
    print("\n" + "=" * 60)
    print("保存獎勵模型")
    print("=" * 60)

    final_model_path = os.path.join(config.output_dir, "final_model")
    trainer.save_model(final_model_path)
    tokenizer.save_pretrained(final_model_path)
    print(f"✓ 模型保存到: {final_model_path}")

    # 8. 測試獎勵模型
    print("\n" + "=" * 60)
    print("測試獎勵模型")
    print("=" * 60)

    # 測試單個文本
    test_texts = [
        "### Human: 什麼是 AI？\n### Assistant: AI 是人工智能，是計算機科學的一個分支，旨在創建能夠執行通常需要人類智能的任務的系統。",
        "### Human: 什麼是 AI？\n### Assistant: 不知道。",
    ]
    predict_rewards(model, tokenizer, test_texts)

    # 比較兩個回答
    compare_responses(
        model,
        tokenizer,
        prompt="### Human: 什麼是機器學習？\n### Assistant: ",
        response1="機器學習是人工智能的一個分支，使用算法和統計模型讓計算機從數據中學習。",
        response2="機器學習就是學習。",
    )

    # 9. 總結
    print("\n" + "=" * 60)
    print("獎勵模型訓練完成！")
    print("=" * 60)
    print(f"\n模型保存在: {final_model_path}")
    print("\n獎勵模型的作用:")
    print("  1. 評估生成文本的質量")
    print("  2. 為強化學習提供獎勵信號")
    print("  3. 用於 PPO 訓練（查看 04_PPO訓練.py）")
    print("  4. 或直接使用 DPO（查看 05_DPO訓練.py）跳過獎勵模型")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用戶中斷")
    except Exception as e:
        print(f"\n程序執行出錯: {e}")
        import traceback
        traceback.print_exc()

"""
TRL 快速開始示例

這個文件演示了 TRL 框架的基礎使用，包括：
1. 環境設置與依賴檢查
2. 模型和分詞器加載
3. 簡單的 SFT 訓練
4. 模型保存和加載
5. 基礎推理測試

TRL (Transformer Reinforcement Learning) 是 HuggingFace 的強化學習框架，
專門用於訓練語言模型使用人類反饋進行強化學習（RLHF）。
"""

import os
import sys
from typing import Optional, Dict, Any
import warnings

warnings.filterwarnings('ignore')


def check_dependencies() -> Dict[str, bool]:
    """
    檢查必要的依賴包是否已安裝

    Returns:
        Dict[str, bool]: 各依賴包的安裝狀態
    """
    print("=" * 60)
    print("檢查依賴包...")
    print("=" * 60)

    dependencies = {
        'torch': False,
        'transformers': False,
        'trl': False,
        'datasets': False,
        'peft': False
    }

    for package in dependencies.keys():
        try:
            __import__(package)
            dependencies[package] = True
            print(f"✓ {package:15s} - 已安裝")
        except ImportError:
            dependencies[package] = False
            print(f"✗ {package:15s} - 未安裝")

    print("=" * 60)

    all_installed = all(dependencies.values())
    if not all_installed:
        print("\n⚠️  部分依賴未安裝，請運行：pip install -r requirements.txt")
    else:
        print("\n✓ 所有依賴已安裝完成！")

    return dependencies


def get_device() -> str:
    """
    獲取可用的計算設備（GPU 或 CPU）

    Returns:
        str: 設備名稱
    """
    try:
        import torch
        if torch.cuda.is_available():
            device = "cuda"
            print(f"\n使用 GPU: {torch.cuda.get_device_name(0)}")
            print(f"顯存: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
        else:
            device = "cpu"
            print("\n使用 CPU (建議使用 GPU 進行訓練)")
        return device
    except Exception as e:
        print(f"獲取設備信息時出錯: {e}")
        return "cpu"


def load_model_and_tokenizer(model_name: str = "gpt2"):
    """
    加載預訓練模型和分詞器

    Args:
        model_name: 模型名稱，默認使用 GPT-2

    Returns:
        tuple: (model, tokenizer)
    """
    print("\n" + "=" * 60)
    print(f"加載模型: {model_name}")
    print("=" * 60)

    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer

        print("加載分詞器...")
        tokenizer = AutoTokenizer.from_pretrained(model_name)

        # 設置 pad_token（GPT-2 默認沒有）
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            print("設置 pad_token = eos_token")

        print("加載模型...")
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            trust_remote_code=True
        )

        print(f"✓ 模型加載成功")
        print(f"  模型參數量: {model.num_parameters() / 1e6:.2f}M")

        return model, tokenizer

    except Exception as e:
        print(f"✗ 加載模型失敗: {e}")
        return None, None


def create_sample_dataset():
    """
    創建示例訓練數據集

    Returns:
        Dataset: HuggingFace 數據集對象
    """
    print("\n" + "=" * 60)
    print("創建示例數據集")
    print("=" * 60)

    try:
        from datasets import Dataset

        # 創建簡單的對話數據
        data = {
            "text": [
                "問：什麼是機器學習？\n答：機器學習是人工智能的一個分支，通過數據和算法讓計算機自動學習和改進。",
                "問：Python 有什麼優點？\n答：Python 語法簡潔、生態豐富、應用廣泛，特別適合數據科學和機器學習。",
                "問：什麼是深度學習？\n答：深度學習使用多層神經網絡來學習數據的複雜特徵表示。",
                "問：如何開始學習 AI？\n答：建議從 Python 基礎開始，然後學習機器學習理論，最後實踐深度學習項目。",
                "問：什麼是自然語言處理？\n答：自然語言處理（NLP）是讓計算機理解和生成人類語言的技術。",
            ]
        }

        dataset = Dataset.from_dict(data)
        print(f"✓ 創建數據集成功，包含 {len(dataset)} 個樣本")
        print(f"\n示例數據：")
        print(dataset[0]["text"][:100] + "...")

        return dataset

    except Exception as e:
        print(f"✗ 創建數據集失敗: {e}")
        return None


def quick_sft_training(model, tokenizer, dataset, output_dir: str = "./output/quick_start"):
    """
    快速 SFT (Supervised Fine-Tuning) 訓練示例

    Args:
        model: 預訓練模型
        tokenizer: 分詞器
        dataset: 訓練數據集
        output_dir: 輸出目錄
    """
    print("\n" + "=" * 60)
    print("開始 SFT 訓練")
    print("=" * 60)

    try:
        from trl import SFTTrainer, SFTConfig

        # 創建輸出目錄
        os.makedirs(output_dir, exist_ok=True)

        # 配置訓練參數
        config = SFTConfig(
            output_dir=output_dir,
            num_train_epochs=1,  # 快速演示，只訓練 1 個 epoch
            per_device_train_batch_size=2,
            gradient_accumulation_steps=2,
            learning_rate=2e-5,
            logging_steps=1,
            save_strategy="epoch",
            max_seq_length=128,  # 較短的序列長度以節省記憶體
            report_to="none",  # 不使用 wandb 等工具
        )

        print(f"\n訓練配置:")
        print(f"  Epochs: {config.num_train_epochs}")
        print(f"  Batch Size: {config.per_device_train_batch_size}")
        print(f"  Learning Rate: {config.learning_rate}")
        print(f"  Max Seq Length: {config.max_seq_length}")

        # 創建訓練器
        trainer = SFTTrainer(
            model=model,
            args=config,
            train_dataset=dataset,
            dataset_text_field="text",
            tokenizer=tokenizer,
        )

        print("\n開始訓練...")
        trainer.train()

        print("\n✓ 訓練完成！")

        # 保存模型
        print(f"\n保存模型到: {output_dir}")
        trainer.save_model(output_dir)
        tokenizer.save_pretrained(output_dir)
        print("✓ 模型保存成功")

        return trainer

    except Exception as e:
        print(f"✗ 訓練失敗: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_generation(model, tokenizer, prompt: str = "問：什麼是"):
    """
    測試模型生成能力

    Args:
        model: 訓練後的模型
        tokenizer: 分詞器
        prompt: 輸入提示
    """
    print("\n" + "=" * 60)
    print("測試模型生成")
    print("=" * 60)

    try:
        import torch

        model.eval()

        print(f"輸入提示: {prompt}")

        # 編碼輸入
        inputs = tokenizer(prompt, return_tensors="pt")

        # 將輸入移到與模型相同的設備
        device = next(model.parameters()).device
        inputs = {k: v.to(device) for k, v in inputs.items()}

        # 生成
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=50,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.pad_token_id,
            )

        # 解碼輸出
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

        print(f"\n生成結果:")
        print("-" * 60)
        print(generated_text)
        print("-" * 60)

    except Exception as e:
        print(f"✗ 生成失敗: {e}")
        import traceback
        traceback.print_exc()


def show_trl_info():
    """
    顯示 TRL 框架信息
    """
    print("\n" + "=" * 60)
    print("TRL 框架信息")
    print("=" * 60)

    try:
        import trl
        print(f"TRL 版本: {trl.__version__}")

        print("\n主要組件:")
        components = [
            "SFTTrainer - 監督微調訓練器",
            "RewardTrainer - 獎勵模型訓練器",
            "PPOTrainer - PPO 算法訓練器",
            "DPOTrainer - DPO 算法訓練器",
            "ORPOTrainer - ORPO 算法訓練器",
        ]
        for comp in components:
            print(f"  • {comp}")

        print("\n支持的訓練方法:")
        methods = [
            "SFT (Supervised Fine-Tuning) - 監督微調",
            "RM (Reward Modeling) - 獎勵建模",
            "PPO (Proximal Policy Optimization) - 近端策略優化",
            "DPO (Direct Preference Optimization) - 直接偏好優化",
            "ORPO (Odds Ratio Preference Optimization) - 比值偏好優化",
        ]
        for method in methods:
            print(f"  • {method}")

    except Exception as e:
        print(f"獲取 TRL 信息失敗: {e}")


def main():
    """
    主函數：執行完整的快速開始流程
    """
    print("=" * 60)
    print("TRL 框架快速開始")
    print("=" * 60)

    # 1. 檢查依賴
    dependencies = check_dependencies()
    if not all(dependencies.values()):
        print("\n請先安裝所有必要的依賴包")
        return

    # 2. 顯示 TRL 信息
    show_trl_info()

    # 3. 檢查設備
    device = get_device()

    # 4. 加載模型
    print("\n提示: 首次運行會下載模型，可能需要幾分鐘...")
    model, tokenizer = load_model_and_tokenizer("gpt2")

    if model is None or tokenizer is None:
        print("模型加載失敗，退出程序")
        return

    # 將模型移到設備
    import torch
    model = model.to(device)

    # 5. 創建數據集
    dataset = create_sample_dataset()

    if dataset is None:
        print("數據集創建失敗，退出程序")
        return

    # 6. 訓練前測試
    print("\n【訓練前生成測試】")
    test_generation(model, tokenizer, "問：什麼是")

    # 7. 執行訓練
    print("\n" + "=" * 60)
    print("注意: 這是一個快速演示，實際訓練需要更多數據和更長時間")
    print("=" * 60)

    trainer = quick_sft_training(model, tokenizer, dataset)

    if trainer is None:
        print("訓練失敗，但可以繼續測試原始模型")

    # 8. 訓練後測試
    print("\n【訓練後生成測試】")
    test_generation(model, tokenizer, "問：什麼是")

    # 9. 總結
    print("\n" + "=" * 60)
    print("快速開始完成！")
    print("=" * 60)
    print("\n接下來可以:")
    print("  1. 查看 02_SFT訓練.py - 深入學習監督微調")
    print("  2. 查看 03_獎勵模型.py - 學習獎勵模型訓練")
    print("  3. 查看 04_PPO訓練.py - 學習強化學習訓練")
    print("  4. 查看其他示例文件，探索更多功能")

    print("\n資源:")
    print("  • 官方文檔: https://huggingface.co/docs/trl/")
    print("  • GitHub: https://github.com/huggingface/trl")
    print("  • 示例: https://github.com/huggingface/trl/tree/main/examples")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用戶中斷")
    except Exception as e:
        print(f"\n程序執行出錯: {e}")
        import traceback
        traceback.print_exc()

"""
PPO (Proximal Policy Optimization) 訓練

這個文件演示了使用 PPO 算法進行強化學習訓練，包括：
1. PPO 算法原理
2. 策略模型和價值模型
3. 獎勵函數設計
4. PPO 訓練循環
5. 模型優化

PPO 是 RLHF 流程的第三步，使用獎勵模型的反饋來優化生成策略，
是訓練 ChatGPT 等對話模型的核心算法。
"""

import os
import sys
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
import warnings

warnings.filterwarnings('ignore')


@dataclass
class PPOTrainingConfig:
    """PPO 訓練配置"""

    # 模型配置
    model_name: str = "gpt2"
    reward_model_path: Optional[str] = None

    # PPO 超參數
    batch_size: int = 128
    mini_batch_size: int = 32
    ppo_epochs: int = 4
    learning_rate: float = 1.41e-5
    init_kl_coef: float = 0.2  # KL 散度係數
    target_kl: float = 0.1
    cliprange: float = 0.2  # PPO clip 範圍
    vf_coef: float = 0.1  # 價值函數係數
    cliprange_value: float = 0.2

    # 生成配置
    max_new_tokens: int = 128
    temperature: float = 0.7
    top_k: int = 50
    top_p: float = 0.95

    # 訓練配置
    output_dir: str = "./output/ppo_training"
    steps: int = 20000  # 總訓練步數
    save_freq: int = 1000  # 保存頻率
    log_with: str = "tensorboard"

    # 其他
    seed: int = 42


def explain_ppo_algorithm():
    """
    解釋 PPO 算法原理
    """
    print("\n" + "=" * 60)
    print("PPO 算法原理")
    print("=" * 60)

    explanation = """
PPO (Proximal Policy Optimization) 是一種強化學習算法，
專門設計用於優化策略（生成模型）。

核心思想:
1. 策略優化：通過獎勵信號改進生成策略
2. 近端約束：限制每次更新的幅度，保持訓練穩定
3. 重要性採樣：重複使用採樣數據

訓練流程:
1. 使用當前策略生成回答
2. 使用獎勵模型評分
3. 計算優勢函數（Advantage）
4. 使用 PPO 目標函數更新策略
5. 重複以上步驟

關鍵組件:
• 策略模型（Actor）：生成回答的語言模型
• 價值模型（Critic）：預測狀態價值
• 獎勵模型：評估生成質量
• KL 散度懲罰：防止偏離原始模型太遠

數學公式:
L^CLIP(θ) = E[min(r(θ)A, clip(r(θ), 1-ε, 1+ε)A)]
其中:
- r(θ) = π_θ(a|s) / π_θ_old(a|s)  # 重要性比率
- A = 優勢函數
- ε = cliprange  # 裁剪範圍
"""

    print(explanation)


def load_ppo_models(config: PPOTrainingConfig):
    """
    加載 PPO 訓練所需的模型

    Args:
        config: PPO 訓練配置

    Returns:
        tuple: (model, ref_model, tokenizer, reward_model, reward_tokenizer)
    """
    print("\n" + "=" * 60)
    print("加載 PPO 模型")
    print("=" * 60)

    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModelForSequenceClassification
        from trl import AutoModelForCausalLMWithValueHead
        import torch

        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"使用設備: {device}")

        # 1. 加載分詞器
        print("\n1. 加載分詞器...")
        tokenizer = AutoTokenizer.from_pretrained(config.model_name)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        # 2. 加載策略模型（帶價值頭）
        print("2. 加載策略模型（帶價值頭）...")
        model = AutoModelForCausalLMWithValueHead.from_pretrained(
            config.model_name
        )
        print(f"   ✓ 策略模型參數: {model.num_parameters() / 1e6:.2f}M")

        # 3. 加載參考模型（用於 KL 散度計算）
        print("3. 加載參考模型（凍結參數）...")
        ref_model = AutoModelForCausalLM.from_pretrained(config.model_name)
        ref_model.eval()
        for param in ref_model.parameters():
            param.requires_grad = False
        print(f"   ✓ 參考模型已凍結")

        # 4. 加載獎勵模型（如果提供路徑）
        reward_model = None
        reward_tokenizer = None
        if config.reward_model_path and os.path.exists(config.reward_model_path):
            print(f"4. 加載獎勵模型: {config.reward_model_path}...")
            try:
                reward_model = AutoModelForSequenceClassification.from_pretrained(
                    config.reward_model_path,
                    num_labels=1,
                )
                reward_tokenizer = AutoTokenizer.from_pretrained(config.reward_model_path)
                reward_model.eval()
                for param in reward_model.parameters():
                    param.requires_grad = False
                print(f"   ✓ 獎勵模型加載成功")
            except Exception as e:
                print(f"   ✗ 獎勵模型加載失敗: {e}")
                print("   使用模擬獎勵函數")
        else:
            print("4. 未提供獎勵模型，將使用模擬獎勵函數")

        print("\n✓ 所有模型加載完成")

        return model, ref_model, tokenizer, reward_model, reward_tokenizer

    except Exception as e:
        print(f"✗ 加載模型失敗: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None, None, None


def create_reward_function(reward_model, reward_tokenizer):
    """
    創建獎勵函數

    Args:
        reward_model: 獎勵模型（可選）
        reward_tokenizer: 獎勵模型分詞器（可選）

    Returns:
        callable: 獎勵函數
    """
    import torch

    if reward_model is not None and reward_tokenizer is not None:
        # 使用真實獎勵模型
        def reward_fn(samples):
            """使用獎勵模型計算獎勵"""
            device = next(reward_model.parameters()).device
            inputs = reward_tokenizer(
                samples,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512,
            )
            inputs = {k: v.to(device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = reward_model(**inputs)
                rewards = outputs.logits.squeeze(-1)

            return rewards.cpu().tolist()

        print("使用獎勵模型計算獎勵")

    else:
        # 使用模擬獎勵函數（基於啟發式規則）
        def reward_fn(samples):
            """模擬獎勵函數"""
            rewards = []
            for sample in samples:
                # 簡單的啟發式規則
                reward = 0.0

                # 長度獎勵（適中的長度）
                length = len(sample.split())
                if 20 <= length <= 100:
                    reward += 0.5
                elif length < 20:
                    reward -= 0.3
                elif length > 200:
                    reward -= 0.5

                # 避免重複
                words = sample.split()
                if len(words) > 0:
                    unique_ratio = len(set(words)) / len(words)
                    reward += unique_ratio * 0.3

                # 避免特定模式
                if "不知道" in sample or "無法回答" in sample:
                    reward -= 0.5

                rewards.append(reward)

            return rewards

        print("使用模擬獎勵函數（基於啟發式規則）")

    return reward_fn


def create_query_dataset():
    """
    創建查詢數據集（問題列表）

    Returns:
        list: 問題列表
    """
    print("\n" + "=" * 60)
    print("創建查詢數據集")
    print("=" * 60)

    queries = [
        "### Human: 什麼是機器學習？\n### Assistant:",
        "### Human: Python 有什麼優點？\n### Assistant:",
        "### Human: 如何開始學習 AI？\n### Assistant:",
        "### Human: 什麼是深度學習？\n### Assistant:",
        "### Human: GPU 的作用是什麼？\n### Assistant:",
        "### Human: 什麼是神經網絡？\n### Assistant:",
        "### Human: 如何防止過擬合？\n### Assistant:",
        "### Human: 什麼是 Transformer？\n### Assistant:",
        "### Human: 解釋注意力機制？\n### Assistant:",
        "### Human: 什麼是遷移學習？\n### Assistant:",
    ]

    print(f"✓ 創建 {len(queries)} 個查詢")
    print(f"\n示例查詢:")
    print(queries[0])

    return queries


def setup_ppo_trainer(model, ref_model, tokenizer, config: PPOTrainingConfig):
    """
    設置 PPO 訓練器

    Args:
        model: 策略模型
        ref_model: 參考模型
        tokenizer: 分詞器
        config: PPO 配置

    Returns:
        PPOTrainer
    """
    print("\n" + "=" * 60)
    print("設置 PPO 訓練器")
    print("=" * 60)

    try:
        from trl import PPOConfig, PPOTrainer

        # 創建輸出目錄
        os.makedirs(config.output_dir, exist_ok=True)

        # PPO 配置
        ppo_config = PPOConfig(
            model_name=config.model_name,
            learning_rate=config.learning_rate,
            batch_size=config.batch_size,
            mini_batch_size=config.mini_batch_size,
            ppo_epochs=config.ppo_epochs,
            init_kl_coef=config.init_kl_coef,
            target=config.target_kl,
            cliprange=config.cliprange,
            vf_coef=config.vf_coef,
            cliprange_value=config.cliprange_value,
            seed=config.seed,
        )

        print("\nPPO 配置:")
        print(f"  Batch Size: {config.batch_size}")
        print(f"  Mini Batch Size: {config.mini_batch_size}")
        print(f"  PPO Epochs: {config.ppo_epochs}")
        print(f"  Learning Rate: {config.learning_rate}")
        print(f"  KL Coef: {config.init_kl_coef}")
        print(f"  Clip Range: {config.cliprange}")

        # 創建訓練器
        ppo_trainer = PPOTrainer(
            config=ppo_config,
            model=model,
            ref_model=ref_model,
            tokenizer=tokenizer,
        )

        print("\n✓ PPO 訓練器創建成功")

        return ppo_trainer

    except Exception as e:
        print(f"✗ 創建 PPO 訓練器失敗: {e}")
        import traceback
        traceback.print_exc()
        return None


def ppo_training_loop(ppo_trainer, queries, reward_fn, config: PPOTrainingConfig):
    """
    PPO 訓練循環（簡化版示例）

    Args:
        ppo_trainer: PPO 訓練器
        queries: 查詢列表
        reward_fn: 獎勵函數
        config: 訓練配置
    """
    print("\n" + "=" * 60)
    print("開始 PPO 訓練")
    print("=" * 60)

    try:
        import torch
        from tqdm import tqdm

        # 訓練參數
        generation_kwargs = {
            "max_new_tokens": config.max_new_tokens,
            "temperature": config.temperature,
            "top_k": config.top_k,
            "top_p": config.top_p,
            "do_sample": True,
            "pad_token_id": ppo_trainer.tokenizer.pad_token_id,
        }

        print(f"\n生成參數:")
        print(f"  Max New Tokens: {config.max_new_tokens}")
        print(f"  Temperature: {config.temperature}")
        print(f"  Top K: {config.top_k}")
        print(f"  Top P: {config.top_p}")

        print(f"\n開始訓練循環（演示前 5 步）...")

        # 簡化的訓練循環（只演示幾步）
        for step in range(min(5, config.steps)):
            print(f"\n--- Step {step + 1} ---")

            # 1. 從查詢中採樣
            query = queries[step % len(queries)]
            print(f"Query: {query[:50]}...")

            # 2. 生成回答
            query_tensors = ppo_trainer.tokenizer.encode(query, return_tensors="pt")

            with torch.no_grad():
                response_tensors = ppo_trainer.generate(
                    query_tensors,
                    **generation_kwargs
                )

            response = ppo_trainer.tokenizer.decode(
                response_tensors[0],
                skip_special_tokens=True
            )
            print(f"Response: {response[:100]}...")

            # 3. 計算獎勵
            rewards = reward_fn([response])
            reward_tensor = torch.tensor(rewards)
            print(f"Reward: {rewards[0]:.4f}")

            # 4. PPO 更新（實際使用時需要批量處理）
            # 這裡只是演示概念
            print(f"執行 PPO 更新...")

            # 注意：完整的 PPO 更新需要批量數據
            # stats = ppo_trainer.step([query_tensors], [response_tensors], [reward_tensor])
            # print(f"Stats: {stats}")

        print("\n✓ 訓練循環完成（演示版）")

        print("\n注意:")
        print("  這是一個簡化的演示版本")
        print("  完整的 PPO 訓練需要:")
        print("    1. 批量處理多個查詢")
        print("    2. 計算優勢函數和價值目標")
        print("    3. 執行多個 PPO epochs")
        print("    4. 監控 KL 散度和其他指標")
        print("    5. 定期保存檢查點")

    except Exception as e:
        print(f"✗ 訓練循環失敗: {e}")
        import traceback
        traceback.print_exc()


def demonstrate_ppo_concepts():
    """
    演示 PPO 的核心概念
    """
    print("\n" + "=" * 60)
    print("PPO 核心概念演示")
    print("=" * 60)

    concepts = """
1. 優勢函數 (Advantage Function):
   A(s,a) = Q(s,a) - V(s)
   • 衡量某個動作相比平均水平有多好
   • 正值表示比平均好，負值表示比平均差

2. 重要性採樣比率 (Importance Sampling Ratio):
   r(θ) = π_θ(a|s) / π_θ_old(a|s)
   • 新策略和舊策略的概率比
   • 允許重複使用舊數據

3. PPO 目標函數:
   L^CLIP = E[min(r(θ)A, clip(r(θ), 1-ε, 1+ε)A)]
   • 限制策略更新幅度
   • 防止訓練不穩定

4. KL 散度約束:
   KL(π_old || π_new) < δ
   • 確保新策略不會偏離舊策略太遠
   • 保持生成質量

5. 價值函數學習:
   L^VF = E[(V_θ(s) - V^target)²]
   • 學習狀態價值
   • 用於計算優勢函數

實際應用中的權衡:
• 學習率：太高不穩定，太低訓練慢
• Clip Range：太大可能過度更新，太小學習慢
• KL Coef：平衡探索和利用
• Mini Batch Size：影響梯度估計質量
"""

    print(concepts)


def main():
    """
    主函數：執行 PPO 訓練演示
    """
    print("=" * 60)
    print("PPO 強化學習訓練")
    print("=" * 60)

    # 1. 解釋 PPO 算法
    explain_ppo_algorithm()

    # 2. 創建配置
    config = PPOTrainingConfig(
        model_name="gpt2",
        reward_model_path=None,  # 使用模擬獎勵函數
        batch_size=4,
        mini_batch_size=2,
        steps=10,
        output_dir="./output/ppo_training",
    )

    # 3. 加載模型
    model, ref_model, tokenizer, reward_model, reward_tokenizer = load_ppo_models(config)

    if model is None:
        print("模型加載失敗，退出程序")
        return

    # 4. 創建獎勵函數
    reward_fn = create_reward_function(reward_model, reward_tokenizer)

    # 5. 創建查詢數據集
    queries = create_query_dataset()

    # 6. 設置 PPO 訓練器
    ppo_trainer = setup_ppo_trainer(model, ref_model, tokenizer, config)

    if ppo_trainer is None:
        print("PPO 訓練器創建失敗，退出程序")
        return

    # 7. 執行訓練循環
    ppo_training_loop(ppo_trainer, queries, reward_fn, config)

    # 8. 演示 PPO 概念
    demonstrate_ppo_concepts()

    # 9. 總結
    print("\n" + "=" * 60)
    print("PPO 訓練演示完成！")
    print("=" * 60)

    print("\nPPO 訓練的優勢:")
    print("  1. 穩定性好 - 限制更新幅度")
    print("  2. 樣本效率高 - 可重複使用數據")
    print("  3. 易於實現 - 相比 TRPO 更簡單")
    print("  4. 廣泛應用 - ChatGPT、Claude 等都使用")

    print("\nPPO 訓練的挑戰:")
    print("  1. 需要獎勵模型 - 額外的訓練成本")
    print("  2. 超參數敏感 - 需要仔細調優")
    print("  3. 計算成本高 - 需要多次前向傳播")
    print("  4. 可能不穩定 - 需要監控訓練過程")

    print("\n替代方案:")
    print("  • DPO - 無需獎勵模型（查看 05_DPO訓練.py）")
    print("  • ORPO - 結合 SFT 和偏好優化（查看 06_ORPO訓練.py）")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用戶中斷")
    except Exception as e:
        print(f"\n程序執行出錯: {e}")
        import traceback
        traceback.print_exc()

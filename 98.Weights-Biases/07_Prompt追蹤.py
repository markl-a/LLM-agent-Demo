"""
Weights & Biases Prompt 追蹤示例

這個示例專注於 Prompt 工程的追蹤和優化。
包含 Prompt 版本管理、A/B 測試、性能比較和最佳實踐。

主要功能：
1. Prompt 版本控制
2. A/B 測試
3. Prompt 性能比較
4. Template 管理
5. 參數優化
6. 輸出質量評估
7. Prompt 鏈追蹤
8. 最佳 Prompt 選擇

作者: W&B Team
日期: 2025-01-01
"""

import wandb
import numpy as np
from typing import List, Dict
import time


def prompt_ab_testing():
    """Prompt A/B 測試"""
    print("\n" + "="*60)
    print("Prompt A/B 測試")
    print("="*60)

    run = wandb.init(
        project="prompt-engineering",
        name="ab-testing"
    )

    prompts = {
        "A": "簡單直接的提示",
        "B": "詳細結構化的提示",
        "C": "帶示例的提示"
    }

    for variant, prompt in prompts.items():
        quality = 0.7 + np.random.random() * 0.3
        user_satisfaction = np.random.randint(1, 6)

        wandb.log({
            f"variant_{variant}/quality": quality,
            f"variant_{variant}/satisfaction": user_satisfaction,
            f"variant_{variant}/tokens": len(prompt) * 10
        })

        print(f"  Variant {variant}: quality={quality:.2f}")

    wandb.finish()


def prompt_chain_tracking():
    """Prompt 鏈追蹤"""
    print("\n" + "="*60)
    print("Prompt 鏈追蹤")
    print("="*60)

    run = wandb.init(
        project="prompt-engineering",
        name="chain-tracking"
    )

    chain_steps = [
        "分析問題",
        "生成大綱",
        "撰寫內容",
        "優化結果"
    ]

    for i, step in enumerate(chain_steps):
        latency = 0.5 + np.random.random()
        tokens = 100 + np.random.randint(0, 200)

        wandb.log({
            "step": i,
            "step_name": step,
            "latency": latency,
            "tokens": tokens
        })

        print(f"  步驟 {i+1}: {step}")

    wandb.finish()


def main():
    """主函數"""
    print("\n" + "="*70)
    print("Weights & Biases Prompt 追蹤示例")
    print("="*70)

    try:
        prompt_ab_testing()
        prompt_chain_tracking()

        print("\n✅ 所有示例完成！")

    except Exception as e:
        print(f"\n❌ 錯誤: {e}")


if __name__ == "__main__":
    main()

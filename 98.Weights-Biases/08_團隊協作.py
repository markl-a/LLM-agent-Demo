"""
Weights & Biases 團隊協作示例

這個示例展示了如何使用 W&B 進行團隊協作。
包含實驗共享、報告創建、評論和權限管理。

主要功能：
1. 項目組織和團隊設置
2. 實驗共享和比較
3. 報告創建和分享
4. 評論和討論
5. 標籤和分組管理
6. 權限控制
7. 工作流程集成
8. 協作最佳實踐

作者: W&B Team
日期: 2025-01-01
"""

import wandb
import numpy as np


def team_project_setup():
    """團隊項目設置"""
    print("\n" + "="*60)
    print("團隊項目設置")
    print("="*60)

    run = wandb.init(
        project="team-collaboration",
        name="team-experiment-1",
        tags=["team-a", "baseline"],
        notes="這是團隊 A 的基礎實驗"
    )

    for epoch in range(10):
        wandb.log({
            "epoch": epoch,
            "loss": 1.0 / (epoch + 1),
            "accuracy": epoch / 10
        })

    wandb.summary["team"] = "Team A"
    wandb.summary["status"] = "完成"

    print("✅ 團隊實驗已記錄")

    wandb.finish()


def shared_experiments():
    """共享實驗示例"""
    print("\n" + "="*60)
    print("共享實驗")
    print("="*60)

    # 模擬多個團隊成員的實驗
    team_members = ["Alice", "Bob", "Charlie"]

    for member in team_members:
        run = wandb.init(
            project="team-collaboration",
            name=f"{member}-experiment",
            group="sprint-1",
            tags=["collaborative", member],
            reinit=True
        )

        # 模擬實驗
        performance = 0.7 + np.random.random() * 0.3

        wandb.log({"performance": performance})
        wandb.summary["member"] = member

        print(f"  {member}: performance={performance:.2f}")

        wandb.finish()

    print("\n✅ 團隊實驗已共享")


def main():
    """主函數"""
    print("\n" + "="*70)
    print("Weights & Biases 團隊協作示例")
    print("="*70)

    try:
        team_project_setup()
        shared_experiments()

        print("\n✅ 所有示例完成！")
        print("\n💡 訪問 W&B 儀表板進行團隊協作")

    except Exception as e:
        print(f"\n❌ 錯誤: {e}")


if __name__ == "__main__":
    main()

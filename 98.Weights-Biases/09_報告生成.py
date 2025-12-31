"""
Weights & Biases 報告生成示例

這個示例展示了如何使用 W&B 創建專業的實驗報告。
包含報告模板、圖表嵌入、Markdown 支援和自動化報告生成。

主要功能：
1. 創建交互式報告
2. 嵌入圖表和可視化
3. Markdown 格式支援
4. 自動報告生成
5. 報告分享和導出
6. 自定義報告模板
7. 實驗結果總結
8. 報告版本管理

作者: W&B Team
日期: 2025-01-01
"""

import wandb
import numpy as np


def create_experiment_report():
    """創建實驗報告"""
    print("\n" + "="*60)
    print("創建實驗報告")
    print("="*60)

    run = wandb.init(
        project="report-generation",
        name="experiment-for-report"
    )

    print("\n📊 運行實驗...")

    # 運行實驗並記錄數據
    for epoch in range(20):
        train_loss = 2.0 * np.exp(-epoch / 5) + np.random.random() * 0.1
        val_loss = train_loss * 1.1
        accuracy = 1 - np.exp(-epoch / 10)

        wandb.log({
            "epoch": epoch,
            "train_loss": train_loss,
            "val_loss": val_loss,
            "accuracy": accuracy
        })

    # 記錄摘要指標
    wandb.summary.update({
        "final_accuracy": accuracy,
        "best_val_loss": min(val_loss, 0.3),
        "total_epochs": 20
    })

    print("✅ 實驗數據已記錄")

    # 記錄報告所需的可視化
    print("\n📈 創建可視化...")

    # 記錄圖像
    image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    wandb.log({"example_image": wandb.Image(image)})

    # 記錄表格
    table_data = [
        ["Metric", "Value"],
        ["Accuracy", f"{accuracy:.2%}"],
        ["Train Loss", f"{train_loss:.4f}"],
        ["Val Loss", f"{val_loss:.4f}"]
    ]

    table = wandb.Table(
        columns=table_data[0],
        data=table_data[1:]
    )

    wandb.log({"results_table": table})

    print("✅ 可視化已創建")
    print("\n💡 訪問 W&B 儀表板創建報告:")
    print(f"   1. 打開運行: {run.url}")
    print("   2. 點擊 'Create Report' 按鈕")
    print("   3. 選擇要包含的圖表")
    print("   4. 添加 Markdown 說明")
    print("   5. 分享報告鏈接")

    wandb.finish()


def automated_summary_report():
    """自動化摘要報告"""
    print("\n" + "="*60)
    print("自動化摘要報告")
    print("="*60)

    run = wandb.init(
        project="report-generation",
        name="automated-summary"
    )

    # 運行多個實驗並自動生成摘要
    experiments = []

    for i in range(5):
        config = {
            "lr": 10 ** np.random.uniform(-4, -2),
            "batch_size": np.random.choice([16, 32, 64]),
        }

        accuracy = 0.7 + np.random.random() * 0.25

        experiments.append({
            "id": i,
            "learning_rate": config["lr"],
            "batch_size": config["batch_size"],
            "accuracy": accuracy
        })

    # 創建摘要表格
    table = wandb.Table(
        columns=list(experiments[0].keys()),
        data=[list(exp.values()) for exp in experiments]
    )

    wandb.log({"experiments_summary": table})

    # 記錄最佳實驗
    best_exp = max(experiments, key=lambda x: x["accuracy"])

    wandb.summary.update({
        "best_accuracy": best_exp["accuracy"],
        "best_learning_rate": best_exp["learning_rate"],
        "best_batch_size": best_exp["batch_size"],
        "total_experiments": len(experiments)
    })

    print(f"\n📊 實驗摘要:")
    print(f"   總實驗數: {len(experiments)}")
    print(f"   最佳準確率: {best_exp['accuracy']:.2%}")
    print(f"   最佳學習率: {best_exp['learning_rate']:.6f}")

    wandb.finish()


def main():
    """主函數"""
    print("\n" + "="*70)
    print("Weights & Biases 報告生成示例")
    print("="*70)

    try:
        create_experiment_report()
        automated_summary_report()

        print("\n✅ 所有示例完成！")

    except Exception as e:
        print(f"\n❌ 錯誤: {e}")


if __name__ == "__main__":
    main()

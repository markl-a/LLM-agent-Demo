"""
Weights & Biases 快速開始示例

這個示例展示了如何快速開始使用 W&B 進行 ML 實驗追蹤。
包含基本的初始化、配置管理和指標記錄功能。

主要功能：
1. W&B 初始化和配置
2. 基本指標記錄
3. 配置管理
4. 運行狀態管理
5. 多種日誌類型
6. 離線模式使用
7. 工件保存
8. 運行分組和標籤

作者: W&B Team
日期: 2025-01-01
"""

import wandb
import numpy as np
import time
import os
from typing import Dict, List, Any
import random


# ============================================================================
# 第一部分：基本初始化
# ============================================================================

def basic_initialization():
    """
    基本初始化示例

    展示如何初始化 W&B 運行並設置基本配置。
    """
    print("\n" + "="*60)
    print("基本初始化示例")
    print("="*60)

    # 初始化運行
    run = wandb.init(
        # 項目名稱（必需）
        project="wandb-quickstart",

        # 運行名稱（可選，默認自動生成）
        name="basic-run",

        # 配置參數
        config={
            "learning_rate": 0.001,
            "epochs": 10,
            "batch_size": 32,
            "architecture": "CNN",
            "dataset": "MNIST"
        },

        # 標籤（用於分組和過濾）
        tags=["quickstart", "demo", "tutorial"],

        # 備註
        notes="這是一個基本的 W&B 快速開始示例",

        # 運行分組
        group="baseline-experiments",

        # 運行模式：online, offline, disabled
        # mode="online",
    )

    print(f"✅ 運行初始化成功")
    print(f"   運行 ID: {run.id}")
    print(f"   運行名稱: {run.name}")
    print(f"   項目: {run.project}")
    print(f"   URL: {run.url}")

    # 訪問配置
    print(f"\n📋 配置參數:")
    for key, value in wandb.config.items():
        print(f"   {key}: {value}")

    return run


def log_simple_metrics():
    """
    記錄簡單指標示例

    展示如何記錄各種類型的指標到 W&B。
    """
    print("\n" + "="*60)
    print("記錄簡單指標示例")
    print("="*60)

    # 初始化運行
    run = wandb.init(
        project="wandb-quickstart",
        name="metrics-logging",
        config={"epochs": 10}
    )

    # 模擬訓練循環
    print("\n🏃 開始訓練循環...")

    for epoch in range(wandb.config.epochs):
        # 模擬訓練指標
        train_loss = 1.0 / (epoch + 1) + random.uniform(0, 0.1)
        train_acc = epoch / wandb.config.epochs + random.uniform(0, 0.1)
        val_loss = 1.0 / (epoch + 1) + random.uniform(0, 0.15)
        val_acc = epoch / wandb.config.epochs + random.uniform(0, 0.05)

        # 記錄指標
        wandb.log({
            "epoch": epoch,
            "train/loss": train_loss,
            "train/accuracy": train_acc,
            "val/loss": val_loss,
            "val/accuracy": val_acc,
            "learning_rate": 0.001 * (0.95 ** epoch)  # 學習率衰減
        })

        print(f"  Epoch {epoch+1}/{wandb.config.epochs} - "
              f"train_loss: {train_loss:.4f}, val_loss: {val_loss:.4f}")

        time.sleep(0.2)  # 模擬訓練時間

    print("\n✅ 訓練完成")

    # 記錄最終指標
    wandb.summary["final_train_loss"] = train_loss
    wandb.summary["final_val_loss"] = val_loss
    wandb.summary["best_val_accuracy"] = max(val_acc, 0.9)

    print(f"\n📊 最終摘要:")
    print(f"   最終訓練損失: {train_loss:.4f}")
    print(f"   最終驗證損失: {val_loss:.4f}")

    # 完成運行
    wandb.finish()


# ============================================================================
# 第二部分：配置管理
# ============================================================================

def configuration_management():
    """
    配置管理示例

    展示如何管理和更新實驗配置。
    """
    print("\n" + "="*60)
    print("配置管理示例")
    print("="*60)

    # 初始化配置
    config = {
        "model": {
            "type": "ResNet",
            "layers": 50,
            "pretrained": True
        },
        "optimizer": {
            "name": "Adam",
            "lr": 0.001,
            "betas": [0.9, 0.999]
        },
        "training": {
            "epochs": 20,
            "batch_size": 64,
            "early_stopping": True,
            "patience": 5
        },
        "data": {
            "dataset": "ImageNet",
            "augmentation": True,
            "normalization": "ImageNet"
        }
    }

    # 初始化運行
    run = wandb.init(
        project="wandb-quickstart",
        name="config-management",
        config=config
    )

    print("📋 初始配置:")
    print_nested_dict(wandb.config)

    # 更新配置
    wandb.config.update({
        "training.learning_rate_schedule": "cosine",
        "data.validation_split": 0.2
    }, allow_val_change=True)

    print("\n📝 更新後配置:")
    print(f"   學習率調度: {wandb.config.get('training.learning_rate_schedule')}")
    print(f"   驗證集分割: {wandb.config.get('data.validation_split')}")

    # 訪問嵌套配置
    print(f"\n🔍 訪問嵌套配置:")
    print(f"   模型類型: {wandb.config.model.type}")
    print(f"   優化器: {wandb.config.optimizer.name}")
    print(f"   批次大小: {wandb.config.training.batch_size}")

    wandb.finish()


def print_nested_dict(d, indent=0):
    """輔助函數：打印嵌套字典"""
    for key, value in d.items():
        if isinstance(value, dict):
            print("  " * indent + f"{key}:")
            print_nested_dict(value, indent + 1)
        else:
            print("  " * indent + f"{key}: {value}")


# ============================================================================
# 第三部分：多種數據類型記錄
# ============================================================================

def log_various_data_types():
    """
    記錄各種數據類型示例

    展示如何記錄圖像、直方圖、表格等多種數據類型。
    """
    print("\n" + "="*60)
    print("多種數據類型記錄示例")
    print("="*60)

    run = wandb.init(
        project="wandb-quickstart",
        name="data-types",
    )

    # 1. 記錄圖像
    print("\n📸 記錄圖像...")
    random_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)

    wandb.log({
        "examples/random_image": wandb.Image(
            random_image,
            caption="隨機生成的圖像"
        )
    })

    # 2. 記錄直方圖
    print("📊 記錄直方圖...")
    data = np.random.randn(1000)

    wandb.log({
        "distributions/normal": wandb.Histogram(data)
    })

    # 3. 記錄表格
    print("📋 記錄表格...")
    columns = ["id", "prediction", "actual", "confidence"]
    data = [
        [1, "cat", "cat", 0.95],
        [2, "dog", "dog", 0.88],
        [3, "bird", "cat", 0.62],
        [4, "dog", "dog", 0.91],
    ]

    table = wandb.Table(columns=columns, data=data)
    wandb.log({"predictions/samples": table})

    # 4. 記錄音頻（示例路徑）
    print("🎵 記錄音頻路徑示例...")
    # wandb.log({"audio/sample": wandb.Audio("path/to/audio.wav", sample_rate=16000)})

    # 5. 記錄自定義圖表
    print("📈 記錄自定義圖表...")
    data = [[x, np.sin(x)] for x in np.linspace(0, 10, 100)]
    table = wandb.Table(data=data, columns=["x", "sin(x)"])

    wandb.log({
        "custom_charts/sine_wave": wandb.plot.line(
            table, "x", "sin(x)", title="正弦波"
        )
    })

    # 6. 記錄 HTML
    print("🌐 記錄 HTML...")
    html_content = "<h1>實驗結果</h1><p>這是一個 HTML 報告</p>"
    wandb.log({"reports/html": wandb.Html(html_content)})

    print("\n✅ 所有數據類型記錄完成")

    wandb.finish()


# ============================================================================
# 第四部分：工件管理
# ============================================================================

def artifact_management():
    """
    工件管理示例

    展示如何保存和管理模型、數據集等工件。
    """
    print("\n" + "="*60)
    print("工件管理示例")
    print("="*60)

    run = wandb.init(
        project="wandb-quickstart",
        name="artifact-demo"
    )

    # 1. 創建並保存模型工件
    print("\n💾 創建模型工件...")

    # 創建模擬模型文件
    model_path = "/tmp/model.txt"
    with open(model_path, "w") as f:
        f.write("這是一個模擬的模型文件\n")
        f.write(f"準確率: 0.95\n")

    # 創建工件
    artifact = wandb.Artifact(
        name="demo-model",
        type="model",
        description="演示用的模型工件",
        metadata={
            "accuracy": 0.95,
            "framework": "PyTorch",
            "version": "1.0"
        }
    )

    # 添加文件到工件
    artifact.add_file(model_path)

    # 記錄工件
    run.log_artifact(artifact)
    print(f"✅ 模型工件已保存: {artifact.name}")

    # 2. 創建數據集工件
    print("\n📦 創建數據集工件...")

    dataset_artifact = wandb.Artifact(
        name="demo-dataset",
        type="dataset",
        description="演示數據集"
    )

    # 創建模擬數據文件
    data_path = "/tmp/data.txt"
    with open(data_path, "w") as f:
        for i in range(100):
            f.write(f"sample_{i}\n")

    dataset_artifact.add_file(data_path)
    run.log_artifact(dataset_artifact)
    print(f"✅ 數據集工件已保存: {dataset_artifact.name}")

    # 3. 保存運行文件
    print("\n📄 保存運行文件...")

    # 創建配置文件
    config_path = "/tmp/config.json"
    import json
    with open(config_path, "w") as f:
        json.dump({"setting": "value"}, f)

    wandb.save(config_path)
    print("✅ 配置文件已保存")

    # 清理臨時文件
    os.remove(model_path)
    os.remove(data_path)
    os.remove(config_path)

    wandb.finish()


# ============================================================================
# 第五部分：離線模式
# ============================================================================

def offline_mode_example():
    """
    離線模式示例

    展示如何在沒有網絡連接時使用 W&B。
    """
    print("\n" + "="*60)
    print("離線模式示例")
    print("="*60)

    # 設置離線模式
    os.environ["WANDB_MODE"] = "offline"

    print("🔌 離線模式已啟用")

    run = wandb.init(
        project="wandb-quickstart",
        name="offline-run",
        config={"mode": "offline"}
    )

    # 記錄一些指標
    for i in range(5):
        wandb.log({"metric": i * 0.1})

    print("✅ 數據已在本地記錄")
    print("💡 提示: 運行 'wandb sync' 來同步離線數據")

    wandb.finish()

    # 恢復在線模式
    os.environ["WANDB_MODE"] = "online"


# ============================================================================
# 第六部分：運行管理
# ============================================================================

def run_management():
    """
    運行管理示例

    展示如何管理運行狀態、暫停、恢復等。
    """
    print("\n" + "="*60)
    print("運行管理示例")
    print("="*60)

    # 初始化運行
    run = wandb.init(
        project="wandb-quickstart",
        name="run-management",
        resume="allow"  # 允許恢復運行
    )

    print(f"▶️  運行開始: {run.id}")

    # 記錄一些步驟
    for step in range(5):
        wandb.log({"step": step, "value": step ** 2})
        time.sleep(0.1)

    # 標記運行
    run.tags = run.tags + ["completed", "successful"]
    print(f"🏷️  已添加標籤: {run.tags}")

    # 更新運行摘要
    wandb.summary.update({
        "total_steps": 5,
        "status": "completed",
        "final_value": 16
    })

    # 添加備註
    run.notes = "這次運行成功完成了所有步驟"

    print("✅ 運行管理操作完成")

    wandb.finish()


# ============================================================================
# 第七部分：分組和比較
# ============================================================================

def grouping_and_comparison():
    """
    分組和比較示例

    展示如何組織多個運行以便比較。
    """
    print("\n" + "="*60)
    print("分組和比較示例")
    print("="*60)

    # 運行多個實驗
    learning_rates = [0.001, 0.01, 0.1]

    for lr in learning_rates:
        print(f"\n🚀 運行實驗: lr={lr}")

        run = wandb.init(
            project="wandb-quickstart",
            name=f"lr-{lr}",
            group="learning-rate-comparison",  # 分組
            tags=["lr-sweep", f"lr-{lr}"],
            config={
                "learning_rate": lr,
                "epochs": 10
            },
            reinit=True  # 允許在同一進程中多次初始化
        )

        # 模擬訓練
        for epoch in range(10):
            loss = 1.0 / ((epoch + 1) * lr) + random.uniform(0, 0.1)
            wandb.log({
                "epoch": epoch,
                "loss": loss,
                "learning_rate": lr
            })

        wandb.finish()

    print("\n✅ 所有實驗完成")
    print("💡 訪問 W&B 儀表板查看比較結果")


# ============================================================================
# 第八部分：環境信息記錄
# ============================================================================

def log_environment_info():
    """
    記錄環境信息示例

    展示如何記錄系統和環境信息。
    """
    print("\n" + "="*60)
    print("環境信息記錄示例")
    print("="*60)

    import platform
    import sys

    run = wandb.init(
        project="wandb-quickstart",
        name="environment-info"
    )

    # 記錄系統信息
    env_info = {
        "python_version": sys.version,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "machine": platform.machine(),
    }

    wandb.config.update(env_info)

    print("💻 系統信息:")
    for key, value in env_info.items():
        print(f"   {key}: {value}")

    # 記錄 Git 信息（如果可用）
    try:
        import subprocess
        git_hash = subprocess.check_output(
            ['git', 'rev-parse', 'HEAD']
        ).decode('ascii').strip()

        wandb.config.update({"git_commit": git_hash})
        print(f"\n📝 Git Commit: {git_hash[:8]}")
    except:
        print("\n⚠️  Git 信息不可用")

    wandb.finish()


# ============================================================================
# 主程序
# ============================================================================

def main():
    """
    主函數：運行所有示例
    """
    print("\n" + "="*70)
    print("Weights & Biases 快速開始示例")
    print("="*70)

    try:
        # 1. 基本初始化
        run = basic_initialization()
        run.finish()

        # 2. 記錄簡單指標
        log_simple_metrics()

        # 3. 配置管理
        configuration_management()

        # 4. 多種數據類型
        log_various_data_types()

        # 5. 工件管理
        artifact_management()

        # 6. 離線模式
        offline_mode_example()

        # 7. 運行管理
        run_management()

        # 8. 分組和比較
        grouping_and_comparison()

        # 9. 環境信息
        log_environment_info()

        print("\n" + "="*70)
        print("✅ 所有示例運行完成！")
        print("="*70)
        print("\n💡 接下來的步驟:")
        print("   1. 訪問 https://wandb.ai 查看你的運行")
        print("   2. 探索儀表板中的圖表和可視化")
        print("   3. 嘗試比較不同的運行")
        print("   4. 創建自定義報告")

    except Exception as e:
        print(f"\n❌ 運行示例時出錯: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

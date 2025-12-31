"""
Weights & Biases 數據可視化示例

這個示例展示了 W&B 豐富的數據可視化功能。
包含圖表、圖像、音頻、視頻、3D對象和自定義可視化。

主要功能：
1. 訓練曲線可視化
2. 混淆矩陣和ROC曲線
3. 圖像和圖像序列
4. 自定義圖表
5. 直方圖和分佈
6. 3D可視化
7. 表格和數據框
8. 交互式繪圖

作者: W&B Team
日期: 2025-01-01
"""

import wandb
import numpy as np
import torch
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, roc_curve, auc
import io


# ============================================================================
# 第一部分:基本圖表可視化
# ============================================================================

def basic_charts_visualization():
    """基本圖表可視化示例"""
    print("\n" + "="*60)
    print("基本圖表可視化")
    print("="*60)

    run = wandb.init(
        project="data-visualization",
        name="basic-charts"
    )

    # 模擬訓練數據
    epochs = 50

    for epoch in range(epochs):
        # 多個相關指標
        train_loss = 2.0 * np.exp(-epoch / 10) + np.random.random() * 0.1
        val_loss = 2.2 * np.exp(-epoch / 10) + np.random.random() * 0.15

        train_acc = 1 - np.exp(-epoch / 15) + np.random.random() * 0.05
        val_acc = 1 - np.exp(-epoch / 15) + np.random.random() * 0.03

        learning_rate = 0.1 * (0.95 ** epoch)

        # 記錄所有指標
        wandb.log({
            "epoch": epoch,
            "loss/train": train_loss,
            "loss/validation": val_loss,
            "accuracy/train": train_acc,
            "accuracy/validation": val_acc,
            "learning_rate": learning_rate,
            "gradient_norm": np.random.random() * 2
        })

    print("✅ 已記錄訓練曲線數據")

    wandb.finish()


# ============================================================================
# 第二部分:混淆矩陣和ROC曲線
# ============================================================================

def confusion_matrix_and_roc():
    """混淆矩陣和ROC曲線示例"""
    print("\n" + "="*60)
    print("混淆矩陣和ROC曲線")
    print("="*60)

    run = wandb.init(
        project="data-visualization",
        name="classification-metrics"
    )

    # 模擬分類結果
    num_classes = 5
    num_samples = 1000

    y_true = np.random.randint(0, num_classes, num_samples)
    y_pred = y_true.copy()

    # 添加一些錯誤
    error_indices = np.random.choice(num_samples, size=int(num_samples * 0.2), replace=False)
    y_pred[error_indices] = np.random.randint(0, num_classes, len(error_indices))

    # 1. 混淆矩陣
    print("\n📊 記錄混淆矩陣...")

    wandb.log({
        "confusion_matrix": wandb.plot.confusion_matrix(
            probs=None,
            y_true=y_true,
            preds=y_pred,
            class_names=[f"Class {i}" for i in range(num_classes)]
        )
    })

    # 2. ROC曲線 (二分類)
    print("📈 記錄ROC曲線...")

    # 二分類示例
    binary_true = (y_true == 0).astype(int)
    binary_scores = np.random.random(num_samples)

    wandb.log({
        "roc": wandb.plot.roc_curve(
            binary_true,
            binary_scores,
            labels=["Class 0", "Others"]
        )
    })

    # 3. PR曲線
    print("📉 記錄PR曲線...")

    wandb.log({
        "pr_curve": wandb.plot.pr_curve(
            binary_true,
            binary_scores,
            labels=["Class 0", "Others"]
        )
    })

    print("✅ 分類指標可視化完成")

    wandb.finish()


# ============================================================================
# 第三部分:圖像可視化
# ============================================================================

def image_visualization():
    """圖像可視化示例"""
    print("\n" + "="*60)
    print("圖像可視化")
    print("="*60)

    run = wandb.init(
        project="data-visualization",
        name="image-visualization"
    )

    print("\n📸 記錄圖像...")

    # 1. 單張圖像
    image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)

    wandb.log({
        "examples/single_image": wandb.Image(
            image,
            caption="隨機生成的圖像"
        )
    })

    # 2. 帶標註的圖像
    class_labels = {0: "cat", 1: "dog", 2: "bird"}

    boxes = {
        "predictions": {
            "box_data": [
                {
                    "position": {
                        "minX": 50,
                        "minY": 50,
                        "maxX": 150,
                        "maxY": 150
                    },
                    "class_id": 0,
                    "box_caption": "cat",
                    "scores": {"confidence": 0.9}
                }
            ],
            "class_labels": class_labels
        }
    }

    wandb.log({
        "examples/annotated_image": wandb.Image(
            image,
            boxes=boxes,
            caption="帶邊界框的圖像"
        )
    })

    # 3. 圖像網格
    images = [np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8) for _ in range(10)]
    captions = [f"Image {i}" for i in range(10)]

    wandb.log({
        "examples/image_grid": [
            wandb.Image(img, caption=cap)
            for img, cap in zip(images, captions)
        ]
    })

    # 4. 遮罩可視化
    mask = np.random.randint(0, 3, (224, 224))

    wandb.log({
        "examples/segmentation": wandb.Image(
            image,
            masks={
                "predictions": {
                    "mask_data": mask,
                    "class_labels": class_labels
                }
            }
        )
    })

    print("✅ 圖像可視化完成")

    wandb.finish()


# ============================================================================
# 第四部分:直方圖和分佈
# ============================================================================

def histogram_visualization():
    """直方圖可視化示例"""
    print("\n" + "="*60)
    print("直方圖和分佈可視化")
    print("="*60)

    run = wandb.init(
        project="data-visualization",
        name="histograms"
    )

    print("\n📊 記錄直方圖...")

    # 1. 簡單直方圖
    data = np.random.randn(1000)

    wandb.log({
        "distributions/normal": wandb.Histogram(data)
    })

    # 2. 多個直方圖對比
    for epoch in range(10):
        # 模擬權重分佈隨訓練變化
        weights = np.random.randn(1000) * (1 - epoch * 0.05)

        wandb.log({
            "epoch": epoch,
            "weights/distribution": wandb.Histogram(weights),
            "gradients/distribution": wandb.Histogram(np.random.randn(500))
        })

    # 3. 自定義直方圖
    hist, bins = np.histogram(data, bins=50)

    wandb.log({
        "distributions/custom": wandb.Histogram(
            np_histogram=(hist, bins)
        )
    })

    print("✅ 直方圖可視化完成")

    wandb.finish()


# ============================================================================
# 第五部分:表格可視化
# ============================================================================

def table_visualization():
    """表格可視化示例"""
    print("\n" + "="*60)
    print("表格可視化")
    print("="*60)

    run = wandb.init(
        project="data-visualization",
        name="tables"
    )

    print("\n📋 記錄表格...")

    # 1. 簡單表格
    columns = ["id", "name", "score", "passed"]
    data = [
        [1, "Alice", 95, True],
        [2, "Bob", 87, True],
        [3, "Charlie", 72, True],
        [4, "David", 58, False],
    ]

    table = wandb.Table(columns=columns, data=data)

    wandb.log({"examples/simple_table": table})

    # 2. 帶圖像的表格
    columns = ["image", "prediction", "confidence", "correct"]
    data = []

    for i in range(5):
        img = np.random.randint(0, 255, (32, 32, 3), dtype=np.uint8)
        pred = np.random.choice(["cat", "dog", "bird"])
        conf = np.random.random()
        correct = np.random.choice([True, False])

        data.append([wandb.Image(img), pred, conf, correct])

    table = wandb.Table(columns=columns, data=data)
    wandb.log({"predictions/samples": table})

    # 3. 動態表格
    for epoch in range(5):
        table_data = []
        for i in range(10):
            table_data.append([
                epoch,
                i,
                np.random.random(),
                np.random.random()
            ])

        table = wandb.Table(
            columns=["epoch", "batch", "loss", "accuracy"],
            data=table_data
        )

        wandb.log({f"epoch_{epoch}/batch_metrics": table})

    print("✅ 表格可視化完成")

    wandb.finish()


# ============================================================================
# 第六部分:自定義圖表
# ============================================================================

def custom_charts():
    """自定義圖表示例"""
    print("\n" + "="*60)
    print("自定義圖表")
    print("="*60)

    run = wandb.init(
        project="data-visualization",
        name="custom-charts"
    )

    print("\n📈 創建自定義圖表...")

    # 1. 散點圖
    data = [[x, np.sin(x), np.cos(x)] for x in np.linspace(0, 10, 100)]
    table = wandb.Table(data=data, columns=["x", "sin(x)", "cos(x)"])

    wandb.log({
        "custom/scatter": wandb.plot.scatter(
            table,
            "x",
            "sin(x)",
            title="Sin vs X"
        )
    })

    # 2. 折線圖
    wandb.log({
        "custom/line": wandb.plot.line(
            table,
            "x",
            "cos(x)",
            title="Cos vs X"
        )
    })

    # 3. 條形圖
    data = [["A", 10], ["B", 20], ["C", 15], ["D", 25]]
    table = wandb.Table(data=data, columns=["category", "value"])

    wandb.log({
        "custom/bar": wandb.plot.bar(
            table,
            "category",
            "value",
            title="Category Distribution"
        )
    })

    print("✅ 自定義圖表完成")

    wandb.finish()


# ============================================================================
# 第七部分:Matplotlib整合
# ============================================================================

def matplotlib_integration():
    """Matplotlib整合示例"""
    print("\n" + "="*60)
    print("Matplotlib整合")
    print("="*60)

    run = wandb.init(
        project="data-visualization",
        name="matplotlib"
    )

    print("\n🎨 記錄Matplotlib圖表...")

    # 1. 簡單折線圖
    fig, ax = plt.subplots()
    x = np.linspace(0, 10, 100)
    ax.plot(x, np.sin(x), label='sin(x)')
    ax.plot(x, np.cos(x), label='cos(x)')
    ax.legend()
    ax.set_title('Trigonometric Functions')

    wandb.log({"matplotlib/trig": wandb.Image(fig)})
    plt.close(fig)

    # 2. 子圖
    fig, axes = plt.subplots(2, 2, figsize=(10, 10))

    axes[0, 0].plot(x, np.sin(x))
    axes[0, 0].set_title('sin(x)')

    axes[0, 1].plot(x, np.cos(x))
    axes[0, 1].set_title('cos(x)')

    axes[1, 0].hist(np.random.randn(1000), bins=30)
    axes[1, 0].set_title('Normal Distribution')

    axes[1, 1].scatter(np.random.randn(100), np.random.randn(100))
    axes[1, 1].set_title('Scatter Plot')

    plt.tight_layout()
    wandb.log({"matplotlib/subplots": wandb.Image(fig)})
    plt.close(fig)

    # 3. 熱力圖
    fig, ax = plt.subplots()
    data = np.random.rand(10, 10)
    im = ax.imshow(data, cmap='hot')
    plt.colorbar(im, ax=ax)
    ax.set_title('Heatmap')

    wandb.log({"matplotlib/heatmap": wandb.Image(fig)})
    plt.close(fig)

    print("✅ Matplotlib整合完成")

    wandb.finish()


# ============================================================================
# 主程序
# ============================================================================

def main():
    """主函數：運行所有示例"""
    print("\n" + "="*70)
    print("Weights & Biases 數據可視化示例")
    print("="*70)

    try:
        # 1. 基本圖表
        basic_charts_visualization()

        # 2. 混淆矩陣和ROC
        confusion_matrix_and_roc()

        # 3. 圖像可視化
        image_visualization()

        # 4. 直方圖
        histogram_visualization()

        # 5. 表格
        table_visualization()

        # 6. 自定義圖表
        custom_charts()

        # 7. Matplotlib整合
        matplotlib_integration()

        print("\n" + "="*70)
        print("✅ 所有可視化示例完成！")
        print("="*70)

    except Exception as e:
        print(f"\n❌ 運行示例時出錯: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

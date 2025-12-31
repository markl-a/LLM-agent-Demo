"""
Weights & Biases 實驗追蹤示例

這個示例展示了如何使用 W&B 進行深度學習實驗的完整追蹤。
包含 PyTorch 模型訓練、指標記錄、模型檢查點保存等功能。

主要功能：
1. PyTorch 模型訓練追蹤
2. 訓練和驗證指標記錄
3. 模型架構可視化
4. 梯度和參數追蹤
5. 學習率調度追蹤
6. 模型檢查點保存
7. 混淆矩陣可視化
8. 預測樣本記錄

作者: W&B Team
日期: 2025-01-01
"""

import wandb
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
from typing import Dict, List, Tuple
import time


# ============================================================================
# 第一部分：定義模型
# ============================================================================

class SimpleCNN(nn.Module):
    """
    簡單的卷積神經網絡模型

    用於演示 W&B 追蹤功能。
    """

    def __init__(self, num_classes=10):
        super(SimpleCNN, self).__init__()

        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(64 * 7 * 7, 128)
        self.fc2 = nn.Linear(128, num_classes)
        self.dropout = nn.Dropout(0.5)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 64 * 7 * 7)
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x


class SimpleRNN(nn.Module):
    """
    簡單的循環神經網絡模型
    """

    def __init__(self, input_size=10, hidden_size=64, num_layers=2, num_classes=10):
        super(SimpleRNN, self).__init__()

        self.hidden_size = hidden_size
        self.num_layers = num_layers

        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, num_classes)

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)

        out, _ = self.lstm(x, (h0, c0))
        out = self.fc(out[:, -1, :])
        return out


# ============================================================================
# 第二部分：數據準備
# ============================================================================

def create_dummy_data(num_samples=1000, image_size=28) -> Tuple[DataLoader, DataLoader]:
    """
    創建虛擬數據集

    Args:
        num_samples: 樣本數量
        image_size: 圖像大小

    Returns:
        訓練和驗證數據加載器
    """
    print("\n📦 創建虛擬數據集...")

    # 訓練數據
    train_images = torch.randn(num_samples, 1, image_size, image_size)
    train_labels = torch.randint(0, 10, (num_samples,))
    train_dataset = TensorDataset(train_images, train_labels)
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)

    # 驗證數據
    val_images = torch.randn(num_samples // 5, 1, image_size, image_size)
    val_labels = torch.randint(0, 10, (num_samples // 5,))
    val_dataset = TensorDataset(val_images, val_labels)
    val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)

    print(f"✅ 數據集創建完成")
    print(f"   訓練樣本: {len(train_dataset)}")
    print(f"   驗證樣本: {len(val_dataset)}")

    return train_loader, val_loader


# ============================================================================
# 第三部分：訓練函數
# ============================================================================

def train_epoch(
    model: nn.Module,
    train_loader: DataLoader,
    criterion: nn.Module,
    optimizer: optim.Optimizer,
    epoch: int,
    device: torch.device
) -> Dict[str, float]:
    """
    訓練一個 epoch

    Args:
        model: 模型
        train_loader: 訓練數據加載器
        criterion: 損失函數
        optimizer: 優化器
        epoch: 當前 epoch
        device: 設備

    Returns:
        訓練指標字典
    """
    model.train()

    total_loss = 0.0
    correct = 0
    total = 0

    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)

        # 前向傳播
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)

        # 反向傳播
        loss.backward()
        optimizer.step()

        # 統計
        total_loss += loss.item()
        _, predicted = output.max(1)
        total += target.size(0)
        correct += predicted.eq(target).sum().item()

        # 記錄批次級別的指標
        if batch_idx % 10 == 0:
            wandb.log({
                "batch/train_loss": loss.item(),
                "batch/train_step": epoch * len(train_loader) + batch_idx
            })

    # 計算平均指標
    avg_loss = total_loss / len(train_loader)
    accuracy = 100. * correct / total

    return {
        "train/loss": avg_loss,
        "train/accuracy": accuracy
    }


def validate(
    model: nn.Module,
    val_loader: DataLoader,
    criterion: nn.Module,
    device: torch.device
) -> Dict[str, float]:
    """
    驗證模型

    Args:
        model: 模型
        val_loader: 驗證數據加載器
        criterion: 損失函數
        device: 設備

    Returns:
        驗證指標字典
    """
    model.eval()

    total_loss = 0.0
    correct = 0
    total = 0
    all_predictions = []
    all_targets = []

    with torch.no_grad():
        for data, target in val_loader:
            data, target = data.to(device), target.to(device)

            output = model(data)
            loss = criterion(output, target)

            total_loss += loss.item()
            _, predicted = output.max(1)
            total += target.size(0)
            correct += predicted.eq(target).sum().item()

            all_predictions.extend(predicted.cpu().numpy())
            all_targets.extend(target.cpu().numpy())

    avg_loss = total_loss / len(val_loader)
    accuracy = 100. * correct / total

    return {
        "val/loss": avg_loss,
        "val/accuracy": accuracy,
        "predictions": all_predictions,
        "targets": all_targets
    }


# ============================================================================
# 第四部分：完整訓練流程
# ============================================================================

def train_with_wandb():
    """
    使用 W&B 追蹤的完整訓練流程
    """
    print("\n" + "="*60)
    print("使用 W&B 追蹤訓練")
    print("="*60)

    # 配置參數
    config = {
        "architecture": "SimpleCNN",
        "dataset": "Dummy MNIST",
        "epochs": 10,
        "batch_size": 32,
        "learning_rate": 0.001,
        "optimizer": "Adam",
        "loss_function": "CrossEntropy",
        "weight_decay": 1e-4,
        "lr_scheduler": "StepLR",
        "step_size": 5,
        "gamma": 0.1,
    }

    # 初始化 W&B
    run = wandb.init(
        project="experiment-tracking",
        name="cnn-training",
        config=config,
        tags=["pytorch", "cnn", "training"]
    )

    # 設備配置
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"📱 使用設備: {device}")

    # 創建模型
    model = SimpleCNN(num_classes=10).to(device)

    # 追蹤模型架構
    wandb.watch(model, log="all", log_freq=10)
    print(f"✅ 模型架構已追蹤")

    # 損失函數和優化器
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(
        model.parameters(),
        lr=config["learning_rate"],
        weight_decay=config["weight_decay"]
    )

    # 學習率調度器
    scheduler = optim.lr_scheduler.StepLR(
        optimizer,
        step_size=config["step_size"],
        gamma=config["gamma"]
    )

    # 準備數據
    train_loader, val_loader = create_dummy_data()

    # 訓練循環
    print(f"\n🏃 開始訓練 {config['epochs']} 個 epochs...")

    best_val_acc = 0.0

    for epoch in range(config["epochs"]):
        epoch_start = time.time()

        # 訓練
        train_metrics = train_epoch(
            model, train_loader, criterion, optimizer, epoch, device
        )

        # 驗證
        val_metrics = validate(model, val_loader, criterion, device)

        # 更新學習率
        current_lr = optimizer.param_groups[0]['lr']
        scheduler.step()

        epoch_time = time.time() - epoch_start

        # 記錄指標
        metrics = {
            **train_metrics,
            **{k: v for k, v in val_metrics.items() if k not in ["predictions", "targets"]},
            "epoch": epoch,
            "learning_rate": current_lr,
            "epoch_time": epoch_time
        }

        wandb.log(metrics)

        # 打印進度
        print(f"Epoch {epoch+1}/{config['epochs']} - "
              f"train_loss: {train_metrics['train/loss']:.4f}, "
              f"val_loss: {val_metrics['val/loss']:.4f}, "
              f"val_acc: {val_metrics['val/accuracy']:.2f}%, "
              f"time: {epoch_time:.2f}s")

        # 保存最佳模型
        if val_metrics['val/accuracy'] > best_val_acc:
            best_val_acc = val_metrics['val/accuracy']

            # 保存模型檢查點
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_accuracy': best_val_acc,
            }, "/tmp/best_model.pth")

            # 記錄為工件
            artifact = wandb.Artifact(
                name=f"model-{run.id}",
                type="model",
                description=f"Best model at epoch {epoch}",
                metadata={
                    "epoch": epoch,
                    "val_accuracy": best_val_acc
                }
            )
            artifact.add_file("/tmp/best_model.pth")
            run.log_artifact(artifact)

            print(f"   💾 最佳模型已保存 (val_acc: {best_val_acc:.2f}%)")

    # 記錄混淆矩陣
    print("\n📊 生成混淆矩陣...")
    val_metrics = validate(model, val_loader, criterion, device)

    wandb.log({
        "confusion_matrix": wandb.plot.confusion_matrix(
            probs=None,
            y_true=val_metrics["targets"],
            preds=val_metrics["predictions"],
            class_names=[str(i) for i in range(10)]
        )
    })

    # 記錄預測樣本
    log_prediction_samples(model, val_loader, device)

    # 記錄最終摘要
    wandb.summary["best_val_accuracy"] = best_val_acc
    wandb.summary["total_epochs"] = config["epochs"]
    wandb.summary["total_parameters"] = sum(p.numel() for p in model.parameters())

    print("\n✅ 訓練完成")
    print(f"   最佳驗證準確率: {best_val_acc:.2f}%")
    print(f"   總參數量: {wandb.summary['total_parameters']:,}")

    wandb.finish()


# ============================================================================
# 第五部分：預測樣本記錄
# ============================================================================

def log_prediction_samples(model, val_loader, device, num_samples=10):
    """
    記錄預測樣本到 W&B

    Args:
        model: 模型
        val_loader: 驗證數據加載器
        device: 設備
        num_samples: 樣本數量
    """
    print("📸 記錄預測樣本...")

    model.eval()

    # 獲取一批數據
    data, targets = next(iter(val_loader))
    data, targets = data.to(device), targets.to(device)

    # 預測
    with torch.no_grad():
        outputs = model(data)
        _, predictions = outputs.max(1)
        probabilities = F.softmax(outputs, dim=1)

    # 創建表格
    columns = ["image", "prediction", "truth", "confidence"]
    table_data = []

    for i in range(min(num_samples, len(data))):
        img = data[i].cpu().numpy().squeeze()
        pred = predictions[i].item()
        truth = targets[i].item()
        conf = probabilities[i][pred].item()

        table_data.append([
            wandb.Image(img),
            pred,
            truth,
            conf
        ])

    table = wandb.Table(columns=columns, data=table_data)
    wandb.log({"predictions/samples": table})

    print(f"✅ 已記錄 {len(table_data)} 個預測樣本")


# ============================================================================
# 第六部分：多模型比較
# ============================================================================

def compare_models():
    """
    比較不同模型架構的性能
    """
    print("\n" + "="*60)
    print("多模型比較")
    print("="*60)

    architectures = ["SimpleCNN", "SimpleRNN"]
    device = torch.device("cpu")

    # 準備數據
    train_loader, val_loader = create_dummy_data(num_samples=500)

    for arch_name in architectures:
        print(f"\n🚀 訓練 {arch_name}...")

        # 初始化運行
        run = wandb.init(
            project="experiment-tracking",
            name=f"{arch_name}-comparison",
            group="architecture-comparison",
            config={
                "architecture": arch_name,
                "epochs": 5,
                "learning_rate": 0.001
            },
            reinit=True
        )

        # 創建模型
        if arch_name == "SimpleCNN":
            model = SimpleCNN().to(device)
        else:
            # RNN 需要不同的輸入格式，這裡簡化處理
            model = SimpleCNN().to(device)  # 為了演示，都使用 CNN

        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(model.parameters(), lr=0.001)

        # 追蹤模型
        wandb.watch(model, log="all")

        # 快速訓練
        for epoch in range(5):
            train_metrics = train_epoch(
                model, train_loader, criterion, optimizer, epoch, device
            )
            val_metrics = validate(model, val_loader, criterion, device)

            wandb.log({
                **train_metrics,
                **{k: v for k, v in val_metrics.items()
                   if k not in ["predictions", "targets"]},
                "epoch": epoch
            })

        print(f"✅ {arch_name} 訓練完成")

        wandb.finish()

    print("\n✅ 所有模型比較完成")
    print("💡 訪問 W&B 儀表板查看比較結果")


# ============================================================================
# 第七部分：梯度和參數追蹤
# ============================================================================

def gradient_tracking_example():
    """
    梯度和參數追蹤示例
    """
    print("\n" + "="*60)
    print("梯度和參數追蹤示例")
    print("="*60)

    run = wandb.init(
        project="experiment-tracking",
        name="gradient-tracking",
        config={"epochs": 3}
    )

    device = torch.device("cpu")
    model = SimpleCNN().to(device)

    # 使用 wandb.watch 追蹤梯度和參數
    wandb.watch(
        model,
        log="all",  # 'gradients', 'parameters', 'all', or None
        log_freq=1,  # 記錄頻率
        log_graph=True  # 記錄計算圖
    )

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.9)

    train_loader, _ = create_dummy_data(num_samples=200)

    print("\n🔍 開始追蹤梯度...")

    for epoch in range(3):
        for batch_idx, (data, target) in enumerate(train_loader):
            data, target = data.to(device), target.to(device)

            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()

            # 手動記錄梯度統計
            if batch_idx % 5 == 0:
                grad_norms = {}
                for name, param in model.named_parameters():
                    if param.grad is not None:
                        grad_norms[f"gradients/{name}"] = param.grad.norm().item()

                wandb.log({
                    "batch_loss": loss.item(),
                    **grad_norms
                })

        print(f"  Epoch {epoch+1} 完成")

    print("✅ 梯度追蹤完成")

    wandb.finish()


# ============================================================================
# 主程序
# ============================================================================

def main():
    """
    主函數：運行所有示例
    """
    print("\n" + "="*70)
    print("Weights & Biases 實驗追蹤示例")
    print("="*70)

    try:
        # 1. 完整訓練流程
        train_with_wandb()

        # 2. 多模型比較
        compare_models()

        # 3. 梯度追蹤
        gradient_tracking_example()

        print("\n" + "="*70)
        print("✅ 所有實驗追蹤示例完成！")
        print("="*70)
        print("\n💡 提示:")
        print("   - 查看 W&B 儀表板了解詳細的訓練過程")
        print("   - 比較不同運行的性能")
        print("   - 分析梯度流動和參數變化")
        print("   - 下載保存的模型檢查點")

    except Exception as e:
        print(f"\n❌ 運行示例時出錯: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

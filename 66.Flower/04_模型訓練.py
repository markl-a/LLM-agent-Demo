"""
Flower 聯邦學習框架 - 模型訓練

這個示例展示完整的聯邦學習訓練流程：
1. 數據準備和分區
2. 模型定義
3. 客戶端訓練邏輯
4. 服務器聚合邏輯
5. 完整的訓練循環
"""

import flwr as fl
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset, Subset
import numpy as np
from typing import Dict, List, Tuple, Optional
from collections import OrderedDict
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
import logging
from pathlib import Path

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console = Console()


# ============================================================================
# 1. 模型定義
# ============================================================================

class MNISTNet(nn.Module):
    """
    簡單的 CNN 模型用於 MNIST 分類

    架構：
    - 2 個卷積層
    - 2 個全連接層
    - ReLU 激活
    - MaxPooling
    """

    def __init__(self):
        super(MNISTNet, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(64 * 7 * 7, 128)
        self.fc2 = nn.Linear(128, 10)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.5)

    def forward(self, x):
        x = self.relu(self.conv1(x))
        x = self.pool(x)
        x = self.relu(self.conv2(x))
        x = self.pool(x)
        x = x.view(-1, 64 * 7 * 7)
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x


# ============================================================================
# 2. 數據準備
# ============================================================================

def create_synthetic_dataset(
    num_samples: int = 1000,
    num_features: int = 28 * 28,
    num_classes: int = 10
) -> Tuple[torch.Tensor, torch.Tensor]:
    """
    創建合成數據集（模擬 MNIST）

    Args:
        num_samples: 樣本數量
        num_features: 特徵維度
        num_classes: 類別數量

    Returns:
        特徵張量和標籤張量
    """
    console.print("[yellow]創建合成數據集...[/yellow]")

    # 創建隨機圖像數據
    X = torch.randn(num_samples, 1, 28, 28)

    # 創建隨機標籤
    y = torch.randint(0, num_classes, (num_samples,))

    console.print(f"[green]✓ 數據集創建完成[/green]")
    console.print(f"  - 樣本數: {num_samples}")
    console.print(f"  - 圖像形狀: {X.shape}")
    console.print(f"  - 類別數: {num_classes}")

    return X, y


def partition_data(
    X: torch.Tensor,
    y: torch.Tensor,
    num_clients: int = 10,
    iid: bool = True
) -> List[Tuple[torch.Tensor, torch.Tensor]]:
    """
    將數據分配給多個客戶端

    Args:
        X: 特徵張量
        y: 標籤張量
        num_clients: 客戶端數量
        iid: 是否為獨立同分佈（IID）

    Returns:
        每個客戶端的數據列表
    """
    console.print(f"\n[yellow]數據分區 ({'IID' if iid else 'Non-IID'})...[/yellow]")

    num_samples = len(X)
    client_data = []

    if iid:
        # IID 分區：隨機打亂後均勻分配
        indices = torch.randperm(num_samples)
        samples_per_client = num_samples // num_clients

        for i in range(num_clients):
            start_idx = i * samples_per_client
            end_idx = start_idx + samples_per_client if i < num_clients - 1 else num_samples

            client_indices = indices[start_idx:end_idx]
            client_X = X[client_indices]
            client_y = y[client_indices]
            client_data.append((client_X, client_y))

            console.print(f"  客戶端 {i}: {len(client_X)} 樣本")

    else:
        # Non-IID 分區：每個客戶端只有部分類別的數據
        num_classes = torch.max(y).item() + 1
        classes_per_client = max(2, num_classes // num_clients)

        for i in range(num_clients):
            # 為每個客戶端分配特定類別
            client_classes = list(range(
                (i * classes_per_client) % num_classes,
                ((i + 1) * classes_per_client) % num_classes
            ))

            # 獲取屬於這些類別的樣本
            mask = torch.zeros(num_samples, dtype=torch.bool)
            for c in client_classes:
                mask |= (y == c)

            client_X = X[mask]
            client_y = y[mask]
            client_data.append((client_X, client_y))

            console.print(f"  客戶端 {i}: {len(client_X)} 樣本，類別 {client_classes}")

    console.print(f"[green]✓ 數據分區完成[/green]")

    return client_data


# ============================================================================
# 3. 客戶端實現
# ============================================================================

class TrainingClient(fl.client.NumPyClient):
    """
    完整的訓練客戶端實現

    包含：
    - 模型訓練
    - 模型評估
    - 訓練指標記錄
    """

    def __init__(
        self,
        client_id: int,
        model: nn.Module,
        trainloader: DataLoader,
        valloader: DataLoader,
        device: str = "cpu"
    ):
        """
        初始化訓練客戶端

        Args:
            client_id: 客戶端 ID
            model: PyTorch 模型
            trainloader: 訓練數據加載器
            valloader: 驗證數據加載器
            device: 計算設備
        """
        self.client_id = client_id
        self.model = model
        self.trainloader = trainloader
        self.valloader = valloader
        self.device = torch.device(device)
        self.model.to(self.device)

        logger.info(f"客戶端 {client_id} 初始化完成")

    def get_parameters(self, config: Dict[str, str]) -> List[np.ndarray]:
        """獲取模型參數"""
        return [val.cpu().numpy() for _, val in self.model.state_dict().items()]

    def set_parameters(self, parameters: List[np.ndarray]) -> None:
        """設置模型參數"""
        params_dict = zip(self.model.state_dict().keys(), parameters)
        state_dict = OrderedDict({k: torch.tensor(v) for k, v in params_dict})
        self.model.load_state_dict(state_dict, strict=True)

    def fit(
        self,
        parameters: List[np.ndarray],
        config: Dict[str, str]
    ) -> Tuple[List[np.ndarray], int, Dict]:
        """
        訓練模型

        Args:
            parameters: 全局模型參數
            config: 訓練配置

        Returns:
            更新後的參數、樣本數、訓練指標
        """
        # 設置模型參數
        self.set_parameters(parameters)

        # 獲取訓練配置
        epochs = int(config.get("local_epochs", 1))
        lr = float(config.get("learning_rate", 0.001))
        server_round = int(config.get("server_round", 0))

        console.print(f"\n[bold blue]客戶端 {self.client_id} - 輪次 {server_round}[/bold blue]")

        # 訓練
        train_loss, train_acc = self._train(epochs, lr)

        # 返回結果
        num_examples = len(self.trainloader.dataset)
        metrics = {
            "train_loss": train_loss,
            "train_accuracy": train_acc,
        }

        console.print(f"[green]✓ 訓練完成[/green]")
        console.print(f"  - 損失: {train_loss:.4f}")
        console.print(f"  - 準確率: {train_acc:.4f}")

        return self.get_parameters(config={}), num_examples, metrics

    def evaluate(
        self,
        parameters: List[np.ndarray],
        config: Dict[str, str]
    ) -> Tuple[float, int, Dict]:
        """
        評估模型

        Args:
            parameters: 模型參數
            config: 評估配置

        Returns:
            損失值、樣本數、評估指標
        """
        self.set_parameters(parameters)

        loss, accuracy = self._evaluate()

        num_examples = len(self.valloader.dataset)
        metrics = {"accuracy": accuracy}

        console.print(f"[cyan]客戶端 {self.client_id} 評估: Loss={loss:.4f}, Acc={accuracy:.4f}[/cyan]")

        return loss, num_examples, metrics

    def _train(self, epochs: int, learning_rate: float) -> Tuple[float, float]:
        """
        執行訓練

        Args:
            epochs: 訓練輪數
            learning_rate: 學習率

        Returns:
            平均損失和準確率
        """
        self.model.train()

        optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        criterion = nn.CrossEntropyLoss()

        total_loss = 0.0
        total_correct = 0
        total_samples = 0

        for epoch in range(epochs):
            epoch_loss = 0.0
            epoch_correct = 0
            epoch_samples = 0

            for data, target in self.trainloader:
                data, target = data.to(self.device), target.to(self.device)

                optimizer.zero_grad()
                output = self.model(data)
                loss = criterion(output, target)
                loss.backward()
                optimizer.step()

                epoch_loss += loss.item() * len(data)
                _, predicted = torch.max(output, 1)
                epoch_correct += (predicted == target).sum().item()
                epoch_samples += len(data)

            total_loss += epoch_loss
            total_correct += epoch_correct
            total_samples += epoch_samples

            avg_loss = epoch_loss / epoch_samples
            avg_acc = epoch_correct / epoch_samples

            console.print(f"    Epoch {epoch + 1}/{epochs}: Loss={avg_loss:.4f}, Acc={avg_acc:.4f}")

        avg_loss = total_loss / total_samples
        avg_accuracy = total_correct / total_samples

        return avg_loss, avg_accuracy

    def _evaluate(self) -> Tuple[float, float]:
        """
        執行評估

        Returns:
            平均損失和準確率
        """
        self.model.eval()

        criterion = nn.CrossEntropyLoss()
        total_loss = 0.0
        total_correct = 0
        total_samples = 0

        with torch.no_grad():
            for data, target in self.valloader:
                data, target = data.to(self.device), target.to(self.device)

                output = self.model(data)
                loss = criterion(output, target)

                total_loss += loss.item() * len(data)
                _, predicted = torch.max(output, 1)
                total_correct += (predicted == target).sum().item()
                total_samples += len(data)

        avg_loss = total_loss / total_samples
        avg_accuracy = total_correct / total_samples

        return avg_loss, avg_accuracy


# ============================================================================
# 4. 完整訓練流程
# ============================================================================

def create_client_fn(client_datasets: List[Tuple[torch.Tensor, torch.Tensor]]):
    """
    創建客戶端工廠函數

    Args:
        client_datasets: 客戶端數據列表

    Returns:
        客戶端工廠函數
    """
    def client_fn(cid: str) -> fl.client.Client:
        """客戶端工廠函數"""
        client_id = int(cid)

        # 獲取客戶端數據
        X, y = client_datasets[client_id]

        # 分割訓練和驗證集
        train_size = int(0.8 * len(X))
        X_train, X_val = X[:train_size], X[train_size:]
        y_train, y_val = y[:train_size], y[train_size:]

        # 創建數據加載器
        trainset = TensorDataset(X_train, y_train)
        valset = TensorDataset(X_val, y_val)

        trainloader = DataLoader(trainset, batch_size=32, shuffle=True)
        valloader = DataLoader(valset, batch_size=64, shuffle=False)

        # 創建模型
        model = MNISTNet()

        # 創建客戶端
        client = TrainingClient(
            client_id=client_id,
            model=model,
            trainloader=trainloader,
            valloader=valloader
        )

        return client.to_client()

    return client_fn


def run_federated_training(
    num_clients: int = 10,
    num_rounds: int = 5,
    iid: bool = True
):
    """
    運行完整的聯邦學習訓練

    Args:
        num_clients: 客戶端數量
        num_rounds: 訓練輪數
        iid: 是否為 IID 數據分佈
    """
    console.print(Panel.fit(
        f"[bold cyan]聯邦學習訓練啟動[/bold cyan]\n"
        f"客戶端數: {num_clients} | 訓練輪數: {num_rounds} | 數據分佈: {'IID' if iid else 'Non-IID'}",
        border_style="cyan"
    ))

    try:
        # 1. 創建數據集
        X, y = create_synthetic_dataset(num_samples=5000)

        # 2. 分區數據
        client_datasets = partition_data(X, y, num_clients, iid)

        # 3. 創建客戶端工廠函數
        client_fn = create_client_fn(client_datasets)

        # 4. 配置策略
        def fit_config(server_round: int):
            return {
                "server_round": server_round,
                "local_epochs": 3,
                "learning_rate": 0.001,
            }

        strategy = fl.server.strategy.FedAvg(
            fraction_fit=0.5,
            fraction_evaluate=0.5,
            min_fit_clients=min(5, num_clients),
            min_evaluate_clients=min(3, num_clients),
            min_available_clients=num_clients,
            on_fit_config_fn=fit_config,
        )

        # 5. 啟動訓練
        console.print("\n[bold green]開始聯邦學習訓練...[/bold green]\n")

        history = fl.simulation.start_simulation(
            client_fn=client_fn,
            num_clients=num_clients,
            config=fl.server.ServerConfig(num_rounds=num_rounds),
            strategy=strategy,
        )

        # 6. 顯示結果
        display_training_results(history)

    except Exception as e:
        logger.exception("訓練過程出錯")
        console.print(f"[red]✗ 錯誤: {str(e)}[/red]")
        raise


def display_training_results(history):
    """
    顯示訓練結果

    Args:
        history: 訓練歷史
    """
    console.print("\n" + "="*70)
    console.print(Panel.fit(
        "[bold green]聯邦學習訓練完成！[/bold green]",
        border_style="green"
    ))

    # 創建結果表格
    table = Table(title="訓練歷史", show_header=True, header_style="bold magenta")
    table.add_column("輪次", style="cyan", justify="center")
    table.add_column("損失", style="yellow", justify="right")
    table.add_column("準確率", style="green", justify="right")
    table.add_column("狀態", style="white", justify="center")

    if hasattr(history, 'losses_distributed') and history.losses_distributed:
        for round_num, (loss, _) in enumerate(history.losses_distributed, 1):
            accuracy = "N/A"
            status = "✓"

            if (hasattr(history, 'metrics_distributed') and
                history.metrics_distributed and
                round_num - 1 < len(history.metrics_distributed)):
                metrics = history.metrics_distributed[round_num - 1][1]
                if 'accuracy' in metrics:
                    accuracy = f"{metrics['accuracy']:.4f}"

            table.add_row(
                f"{round_num}",
                f"{loss:.4f}",
                accuracy,
                status
            )

    console.print(table)


def main():
    """主函數"""
    console.print("\n[bold magenta]Flower 聯邦學習 - 完整訓練流程[/bold magenta]\n")

    # 運行 IID 訓練
    console.print("[bold]場景 1: IID 數據分佈[/bold]")
    run_federated_training(num_clients=5, num_rounds=3, iid=True)

    # 運行 Non-IID 訓練
    console.print("\n[bold]場景 2: Non-IID 數據分佈[/bold]")
    run_federated_training(num_clients=5, num_rounds=3, iid=False)

    console.print("\n[bold green]✓ 訓練示例完成！[/bold green]")
    console.print("\n[yellow]關鍵要點:[/yellow]")
    console.print("  1. 數據分區 - IID vs Non-IID")
    console.print("  2. 客戶端訓練 - 本地模型更新")
    console.print("  3. 服務器聚合 - 合併客戶端更新")
    console.print("  4. 訓練配置 - 動態調整超參數")
    console.print("  5. 指標跟踪 - 監控訓練進度")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]程序被用戶中斷[/yellow]")
    except Exception as e:
        logger.exception("程序執行出錯")
        console.print(f"[red]錯誤: {str(e)}[/red]")

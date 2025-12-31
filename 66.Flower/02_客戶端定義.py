"""
Flower 聯邦學習框架 - 客戶端定義

這個示例展示如何實現各種類型的 Flower 客戶端：
1. NumPyClient - 使用 NumPy 數組的客戶端
2. PyTorch 客戶端 - 使用 PyTorch 模型的客戶端
3. 自定義客戶端 - 實現複雜邏輯的客戶端
"""

import flwr as fl
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
from typing import Dict, List, Tuple, Optional
from collections import OrderedDict
from rich.console import Console
from rich.panel import Panel
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console = Console()


# ============================================================================
# 1. NumPy 客戶端 - 最簡單的客戶端實現
# ============================================================================

class BasicNumPyClient(fl.client.NumPyClient):
    """
    基於 NumPy 的基本客戶端

    適用於：
    - 簡單的機器學習模型
    - 原型開發
    - 不依賴深度學習框架的場景
    """

    def __init__(self, client_id: int, model_size: int = 100):
        """
        初始化客戶端

        Args:
            client_id: 客戶端 ID
            model_size: 模型參數數量
        """
        self.client_id = client_id
        self.model_params = np.random.randn(model_size).astype(np.float32)
        self.learning_rate = 0.01

        console.print(f"[green]✓ NumPy 客戶端 {client_id} 初始化[/green]")

    def get_parameters(self, config: Dict[str, str]) -> List[np.ndarray]:
        """獲取模型參數"""
        return [self.model_params]

    def fit(
        self,
        parameters: List[np.ndarray],
        config: Dict[str, str]
    ) -> Tuple[List[np.ndarray], int, Dict]:
        """
        本地訓練

        Args:
            parameters: 全局模型參數
            config: 訓練配置

        Returns:
            更新後的參數、樣本數、訓練指標
        """
        # 更新本地模型
        self.model_params = parameters[0]

        # 獲取配置
        epochs = int(config.get("local_epochs", 1))
        batch_size = int(config.get("batch_size", 32))

        # 模擬訓練
        for epoch in range(epochs):
            # 計算梯度（這裡只是示例）
            gradient = np.random.randn(*self.model_params.shape) * 0.01
            # 更新參數
            self.model_params = self.model_params - self.learning_rate * gradient

        num_examples = 100
        metrics = {"train_loss": 0.5}

        console.print(f"[blue]客戶端 {self.client_id}: 訓練完成[/blue]")

        return [self.model_params], num_examples, metrics

    def evaluate(
        self,
        parameters: List[np.ndarray],
        config: Dict[str, str]
    ) -> Tuple[float, int, Dict]:
        """評估模型"""
        self.model_params = parameters[0]

        # 模擬評估
        loss = np.random.uniform(0.2, 0.6)
        accuracy = np.random.uniform(0.7, 0.95)
        num_examples = 50

        return loss, num_examples, {"accuracy": accuracy}


# ============================================================================
# 2. PyTorch 客戶端 - 使用 PyTorch 模型的客戶端
# ============================================================================

class SimpleNN(nn.Module):
    """簡單的神經網絡模型"""

    def __init__(self, input_size: int = 10, hidden_size: int = 64, output_size: int = 2):
        super(SimpleNN, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x


class PyTorchClient(fl.client.NumPyClient):
    """
    基於 PyTorch 的客戶端

    適用於：
    - 深度學習模型
    - 複雜的神經網絡架構
    - GPU 加速訓練
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
        初始化 PyTorch 客戶端

        Args:
            client_id: 客戶端 ID
            model: PyTorch 模型
            trainloader: 訓練數據加載器
            valloader: 驗證數據加載器
            device: 計算設備 (cpu/cuda)
        """
        self.client_id = client_id
        self.model = model
        self.trainloader = trainloader
        self.valloader = valloader
        self.device = torch.device(device)
        self.model.to(self.device)

        console.print(f"[green]✓ PyTorch 客戶端 {client_id} 初始化[/green]")
        console.print(f"  - 設備: {device}")
        console.print(f"  - 訓練樣本: {len(trainloader.dataset)}")
        console.print(f"  - 驗證樣本: {len(valloader.dataset)}")

    def get_parameters(self, config: Dict[str, str]) -> List[np.ndarray]:
        """獲取模型參數（轉換為 NumPy 數組）"""
        return [val.cpu().numpy() for _, val in self.model.state_dict().items()]

    def set_parameters(self, parameters: List[np.ndarray]) -> None:
        """設置模型參數（從 NumPy 數組轉換）"""
        params_dict = zip(self.model.state_dict().keys(), parameters)
        state_dict = OrderedDict({k: torch.tensor(v) for k, v in params_dict})
        self.model.load_state_dict(state_dict, strict=True)

    def fit(
        self,
        parameters: List[np.ndarray],
        config: Dict[str, str]
    ) -> Tuple[List[np.ndarray], int, Dict]:
        """
        訓練 PyTorch 模型

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
        learning_rate = float(config.get("learning_rate", 0.001))

        # 定義優化器和損失函數
        optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        criterion = nn.CrossEntropyLoss()

        # 訓練模式
        self.model.train()

        total_loss = 0.0
        num_batches = 0

        console.print(f"[blue]客戶端 {self.client_id}: 開始訓練 (Epochs: {epochs})[/blue]")

        try:
            for epoch in range(epochs):
                epoch_loss = 0.0
                for batch_idx, (data, target) in enumerate(self.trainloader):
                    data, target = data.to(self.device), target.to(self.device)

                    # 前向傳播
                    optimizer.zero_grad()
                    output = self.model(data)
                    loss = criterion(output, target)

                    # 反向傳播
                    loss.backward()
                    optimizer.step()

                    epoch_loss += loss.item()
                    num_batches += 1

                total_loss += epoch_loss
                avg_epoch_loss = epoch_loss / len(self.trainloader)
                console.print(f"  Epoch {epoch + 1}/{epochs} - Loss: {avg_epoch_loss:.4f}")

        except Exception as e:
            logger.error(f"訓練過程出錯: {str(e)}")
            raise

        # 計算平均損失
        avg_loss = total_loss / num_batches if num_batches > 0 else 0.0

        # 返回更新後的參數
        num_examples = len(self.trainloader.dataset)
        metrics = {"train_loss": avg_loss}

        console.print(f"[green]✓ 客戶端 {self.client_id}: 訓練完成[/green]")

        return self.get_parameters(config={}), num_examples, metrics

    def evaluate(
        self,
        parameters: List[np.ndarray],
        config: Dict[str, str]
    ) -> Tuple[float, int, Dict]:
        """
        評估 PyTorch 模型

        Args:
            parameters: 模型參數
            config: 評估配置

        Returns:
            損失值、樣本數、評估指標
        """
        # 設置模型參數
        self.set_parameters(parameters)

        # 評估模式
        self.model.eval()

        criterion = nn.CrossEntropyLoss()
        total_loss = 0.0
        correct = 0
        total = 0

        console.print(f"[cyan]客戶端 {self.client_id}: 開始評估[/cyan]")

        try:
            with torch.no_grad():
                for data, target in self.valloader:
                    data, target = data.to(self.device), target.to(self.device)

                    output = self.model(data)
                    loss = criterion(output, target)
                    total_loss += loss.item()

                    # 計算準確率
                    _, predicted = torch.max(output.data, 1)
                    total += target.size(0)
                    correct += (predicted == target).sum().item()

        except Exception as e:
            logger.error(f"評估過程出錯: {str(e)}")
            raise

        # 計算指標
        avg_loss = total_loss / len(self.valloader)
        accuracy = correct / total if total > 0 else 0.0

        console.print(f"[green]✓ 評估完成 - Loss: {avg_loss:.4f}, Accuracy: {accuracy:.4f}[/green]")

        return avg_loss, len(self.valloader.dataset), {"accuracy": accuracy}


# ============================================================================
# 3. 自定義客戶端 - 實現複雜業務邏輯
# ============================================================================

class CustomFlowerClient(fl.client.NumPyClient):
    """
    自定義 Flower 客戶端

    支持的高級功能：
    - 自定義數據預處理
    - 模型檢查點保存
    - 訓練過程監控
    - 錯誤處理和重試
    """

    def __init__(
        self,
        client_id: int,
        model: nn.Module,
        trainloader: DataLoader,
        valloader: DataLoader,
        checkpoint_dir: Optional[str] = None
    ):
        self.client_id = client_id
        self.model = model
        self.trainloader = trainloader
        self.valloader = valloader
        self.checkpoint_dir = checkpoint_dir
        self.training_history = []

        console.print(f"[green]✓ 自定義客戶端 {client_id} 初始化[/green]")

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
        自定義訓練邏輯

        包含：
        - 動態學習率調整
        - 訓練歷史記錄
        - 檢查點保存
        """
        self.set_parameters(parameters)

        # 動態配置
        epochs = int(config.get("local_epochs", 1))
        lr = float(config.get("learning_rate", 0.001))
        use_scheduler = config.get("use_scheduler", "false").lower() == "true"

        optimizer = optim.Adam(self.model.parameters(), lr=lr)
        criterion = nn.CrossEntropyLoss()

        # 學習率調度器
        scheduler = None
        if use_scheduler:
            scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=1, gamma=0.9)

        self.model.train()
        metrics_history = []

        for epoch in range(epochs):
            epoch_loss = 0.0
            for data, target in self.trainloader:
                optimizer.zero_grad()
                output = self.model(data)
                loss = criterion(output, target)
                loss.backward()
                optimizer.step()
                epoch_loss += loss.item()

            avg_loss = epoch_loss / len(self.trainloader)
            metrics_history.append({"epoch": epoch + 1, "loss": avg_loss})

            if scheduler:
                scheduler.step()

            console.print(f"  Epoch {epoch + 1}: Loss={avg_loss:.4f}")

        # 保存訓練歷史
        self.training_history.extend(metrics_history)

        # 保存檢查點
        if self.checkpoint_dir:
            self._save_checkpoint()

        return (
            self.get_parameters(config={}),
            len(self.trainloader.dataset),
            {"train_loss": metrics_history[-1]["loss"]}
        )

    def evaluate(
        self,
        parameters: List[np.ndarray],
        config: Dict[str, str]
    ) -> Tuple[float, int, Dict]:
        """自定義評估邏輯"""
        self.set_parameters(parameters)
        self.model.eval()

        criterion = nn.CrossEntropyLoss()
        total_loss = 0.0
        correct = 0
        total = 0

        with torch.no_grad():
            for data, target in self.valloader:
                output = self.model(data)
                loss = criterion(output, target)
                total_loss += loss.item()

                _, predicted = torch.max(output.data, 1)
                total += target.size(0)
                correct += (predicted == target).sum().item()

        avg_loss = total_loss / len(self.valloader)
        accuracy = correct / total

        return avg_loss, len(self.valloader.dataset), {"accuracy": accuracy}

    def _save_checkpoint(self):
        """保存模型檢查點"""
        if self.checkpoint_dir:
            import os
            os.makedirs(self.checkpoint_dir, exist_ok=True)
            checkpoint_path = os.path.join(
                self.checkpoint_dir,
                f"client_{self.client_id}_checkpoint.pth"
            )
            torch.save(self.model.state_dict(), checkpoint_path)
            console.print(f"[yellow]檢查點已保存: {checkpoint_path}[/yellow]")


# ============================================================================
# 演示和測試
# ============================================================================

def create_dummy_data(num_samples: int = 100) -> Tuple[DataLoader, DataLoader]:
    """
    創建虛擬數據集

    Args:
        num_samples: 樣本數量

    Returns:
        訓練和驗證數據加載器
    """
    # 創建隨機數據
    X = torch.randn(num_samples, 10)
    y = torch.randint(0, 2, (num_samples,))

    # 分割訓練和驗證集
    train_size = int(0.8 * num_samples)
    X_train, X_val = X[:train_size], X[train_size:]
    y_train, y_val = y[:train_size], y[train_size:]

    # 創建數據集和加載器
    trainset = TensorDataset(X_train, y_train)
    valset = TensorDataset(X_val, y_val)

    trainloader = DataLoader(trainset, batch_size=16, shuffle=True)
    valloader = DataLoader(valset, batch_size=16, shuffle=False)

    return trainloader, valloader


def demonstrate_clients():
    """演示不同類型的客戶端"""
    console.print(Panel.fit(
        "[bold cyan]Flower 客戶端類型演示[/bold cyan]",
        border_style="cyan"
    ))

    # 1. NumPy 客戶端
    console.print("\n[bold]1. NumPy 客戶端[/bold]")
    numpy_client = BasicNumPyClient(client_id=1)
    params = numpy_client.get_parameters({})
    console.print(f"   參數形狀: {params[0].shape}")

    # 2. PyTorch 客戶端
    console.print("\n[bold]2. PyTorch 客戶端[/bold]")
    model = SimpleNN()
    trainloader, valloader = create_dummy_data()
    pytorch_client = PyTorchClient(
        client_id=2,
        model=model,
        trainloader=trainloader,
        valloader=valloader
    )

    # 測試訓練
    config = {"local_epochs": "2", "learning_rate": "0.001"}
    params = pytorch_client.get_parameters({})
    updated_params, num_examples, metrics = pytorch_client.fit(params, config)
    console.print(f"   訓練樣本數: {num_examples}")
    console.print(f"   訓練損失: {metrics['train_loss']:.4f}")

    # 3. 自定義客戶端
    console.print("\n[bold]3. 自定義客戶端[/bold]")
    custom_model = SimpleNN()
    custom_client = CustomFlowerClient(
        client_id=3,
        model=custom_model,
        trainloader=trainloader,
        valloader=valloader
    )
    console.print("   ✓ 支持高級功能：檢查點、歷史記錄等")


def main():
    """主函數"""
    console.print("\n[bold magenta]Flower 客戶端定義示例[/bold magenta]\n")

    demonstrate_clients()

    console.print("\n[bold green]✓ 客戶端定義示例完成！[/bold green]")
    console.print("\n[yellow]關鍵要點:[/yellow]")
    console.print("  1. NumPyClient - 適合簡單模型和原型開發")
    console.print("  2. PyTorch/TensorFlow Client - 適合深度學習模型")
    console.print("  3. 自定義客戶端 - 實現複雜業務邏輯")
    console.print("  4. get_parameters/set_parameters - 參數序列化")
    console.print("  5. fit/evaluate - 核心訓練和評估邏輯")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]程序被用戶中斷[/yellow]")
    except Exception as e:
        logger.exception("程序執行出錯")
        console.print(f"[red]錯誤: {str(e)}[/red]")

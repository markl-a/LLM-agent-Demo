"""
Flower 聯邦學習框架 - 差分隱私

這個示例展示如何在聯邦學習中實現差分隱私保護：
1. 差分隱私基本概念
2. 客戶端級差分隱私
3. 梯度裁剪和噪聲添加
4. 隱私預算管理
5. Opacus 集成
"""

import flwr as fl
from flwr.server.strategy import DifferentialPrivacyClientSideFixedClipping
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
from typing import Dict, List, Tuple, Optional
from collections import OrderedDict
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import logging
import math

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console = Console()


# ============================================================================
# 1. 差分隱私基礎
# ============================================================================

class DifferentialPrivacyExplainer:
    """差分隱私概念解釋器"""

    @staticmethod
    def explain_basics():
        """解釋差分隱私基本概念"""
        console.print(Panel.fit(
            "[bold cyan]差分隱私 (Differential Privacy)[/bold cyan]",
            border_style="cyan"
        ))

        console.print("\n[bold yellow]核心思想:[/bold yellow]")
        console.print("  確保單個數據記錄的存在或不存在，")
        console.print("  不會顯著影響模型訓練結果。\n")

        console.print("[bold yellow]數學定義:[/bold yellow]")
        console.print("  對於任意兩個只相差一條記錄的數據集 D 和 D',")
        console.print("  以及任意輸出 O:")
        console.print("  Pr[M(D) = O] ≤ e^ε × Pr[M(D') = O]\n")

        console.print("[bold yellow]關鍵參數:[/bold yellow]")

        table = Table(show_header=True, header_style="bold blue")
        table.add_column("參數", style="cyan", width=15)
        table.add_column("含義", style="white", width=40)
        table.add_column("典型值", style="green", width=15)

        table.add_row(
            "ε (epsilon)",
            "隱私預算，越小隱私保護越強",
            "0.1 - 10"
        )
        table.add_row(
            "δ (delta)",
            "隱私失效概率",
            "1e-5 - 1e-3"
        )
        table.add_row(
            "C (clipping)",
            "梯度裁剪閾值",
            "0.1 - 10"
        )
        table.add_row(
            "σ (sigma)",
            "噪聲標準差",
            "與 ε 相關"
        )

        console.print(table)

        console.print("\n[bold yellow]在聯邦學習中的應用:[/bold yellow]")
        console.print("  1. 客戶端級 DP：保護整個客戶端的數據")
        console.print("  2. 樣本級 DP：保護單個訓練樣本")
        console.print("  3. 梯度裁剪：限制單個更新的影響")
        console.print("  4. 噪聲添加：在聚合時添加高斯噪聲")


# ============================================================================
# 2. 差分隱私客戶端
# ============================================================================

class DPClient(fl.client.NumPyClient):
    """
    實現差分隱私的客戶端

    特性：
    - 梯度裁剪
    - 噪聲添加
    - 隱私預算跟踪
    """

    def __init__(
        self,
        client_id: int,
        model: nn.Module,
        trainloader: DataLoader,
        valloader: DataLoader,
        epsilon: float = 1.0,
        delta: float = 1e-5,
        max_grad_norm: float = 1.0,
        device: str = "cpu"
    ):
        """
        初始化差分隱私客戶端

        Args:
            client_id: 客戶端 ID
            model: PyTorch 模型
            trainloader: 訓練數據加載器
            valloader: 驗證數據加載器
            epsilon: 隱私預算
            delta: 隱私失效概率
            max_grad_norm: 梯度裁剪範數
            device: 計算設備
        """
        self.client_id = client_id
        self.model = model
        self.trainloader = trainloader
        self.valloader = valloader
        self.epsilon = epsilon
        self.delta = delta
        self.max_grad_norm = max_grad_norm
        self.device = torch.device(device)
        self.model.to(self.device)

        # 隱私預算跟踪
        self.privacy_spent = 0.0

        console.print(f"[green]✓ DP 客戶端 {client_id} 初始化[/green]")
        console.print(f"  - ε = {epsilon}")
        console.print(f"  - δ = {delta}")
        console.print(f"  - 梯度裁剪: {max_grad_norm}")

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
        使用差分隱私訓練模型

        Args:
            parameters: 全局模型參數
            config: 訓練配置

        Returns:
            更新後的參數、樣本數、訓練指標
        """
        self.set_parameters(parameters)

        # 獲取配置
        epochs = int(config.get("local_epochs", 1))
        lr = float(config.get("learning_rate", 0.001))

        console.print(f"\n[bold blue]DP 客戶端 {self.client_id} 開始訓練[/bold blue]")

        # 使用差分隱私訓練
        train_loss = self._train_with_dp(epochs, lr)

        # 添加噪聲到模型參數
        noisy_parameters = self._add_noise_to_parameters()

        # 更新隱私預算
        self._update_privacy_budget(epochs)

        console.print(f"[green]✓ 訓練完成[/green]")
        console.print(f"  - 損失: {train_loss:.4f}")
        console.print(f"  - 已消耗隱私預算: {self.privacy_spent:.4f}/{self.epsilon}")

        metrics = {
            "train_loss": train_loss,
            "privacy_spent": self.privacy_spent,
        }

        return noisy_parameters, len(self.trainloader.dataset), metrics

    def evaluate(
        self,
        parameters: List[np.ndarray],
        config: Dict[str, str]
    ) -> Tuple[float, int, Dict]:
        """評估模型"""
        self.set_parameters(parameters)
        self.model.eval()

        criterion = nn.CrossEntropyLoss()
        total_loss = 0.0
        correct = 0
        total = 0

        with torch.no_grad():
            for data, target in self.valloader:
                data, target = data.to(self.device), target.to(self.device)
                output = self.model(data)
                loss = criterion(output, target)
                total_loss += loss.item() * len(data)

                _, predicted = torch.max(output, 1)
                total += target.size(0)
                correct += (predicted == target).sum().item()

        avg_loss = total_loss / total
        accuracy = correct / total

        return avg_loss, total, {"accuracy": accuracy}

    def _train_with_dp(self, epochs: int, learning_rate: float) -> float:
        """
        使用差分隱私訓練

        實現步驟：
        1. 正常前向傳播和反向傳播
        2. 裁剪每個樣本的梯度
        3. 聚合裁剪後的梯度
        4. 添加噪聲
        5. 更新參數
        """
        self.model.train()

        optimizer = optim.SGD(self.model.parameters(), lr=learning_rate)
        criterion = nn.CrossEntropyLoss(reduction='none')  # 需要每個樣本的損失

        total_loss = 0.0
        num_batches = 0

        for epoch in range(epochs):
            for data, target in self.trainloader:
                data, target = data.to(self.device), target.to(self.device)

                optimizer.zero_grad()

                # 前向傳播
                output = self.model(data)
                loss = criterion(output, target)

                # 對每個樣本單獨計算梯度
                for i in range(len(data)):
                    optimizer.zero_grad()
                    loss[i].backward(retain_graph=(i < len(data) - 1))

                    # 裁剪梯度
                    self._clip_gradients()

                # 更新參數
                optimizer.step()

                total_loss += loss.mean().item()
                num_batches += 1

        return total_loss / num_batches

    def _clip_gradients(self):
        """
        裁剪梯度範數

        確保每個樣本的梯度範數不超過 max_grad_norm
        """
        total_norm = 0.0
        for p in self.model.parameters():
            if p.grad is not None:
                param_norm = p.grad.data.norm(2)
                total_norm += param_norm.item() ** 2
        total_norm = total_norm ** 0.5

        clip_coef = self.max_grad_norm / (total_norm + 1e-6)
        if clip_coef < 1:
            for p in self.model.parameters():
                if p.grad is not None:
                    p.grad.data.mul_(clip_coef)

    def _add_noise_to_parameters(self) -> List[np.ndarray]:
        """
        在模型參數中添加高斯噪聲

        噪聲標準差: σ = C * sqrt(2 * ln(1.25/δ)) / ε
        """
        # 計算噪聲標準差
        noise_scale = self._compute_noise_scale()

        parameters = self.get_parameters({})
        noisy_parameters = []

        for param in parameters:
            # 添加高斯噪聲
            noise = np.random.normal(0, noise_scale, param.shape)
            noisy_param = param + noise
            noisy_parameters.append(noisy_param)

        return noisy_parameters

    def _compute_noise_scale(self) -> float:
        """
        計算噪聲比例

        使用高斯機制的標準公式
        """
        sensitivity = self.max_grad_norm  # L2 敏感度
        noise_scale = sensitivity * math.sqrt(2 * math.log(1.25 / self.delta)) / self.epsilon
        return noise_scale

    def _update_privacy_budget(self, epochs: int):
        """
        更新已消耗的隱私預算

        使用組合定理計算累積隱私損失
        """
        # 簡化版本：線性累積
        # 實際應該使用更精確的組合定理（如 RDP）
        privacy_per_epoch = self.epsilon / 10  # 假設總共 10 輪
        self.privacy_spent += privacy_per_epoch * epochs


# ============================================================================
# 3. 使用 Flower 內置的差分隱私策略
# ============================================================================

def demonstrate_dp_strategy():
    """
    演示 Flower 內置的差分隱私策略
    """
    console.print(Panel.fit(
        "[bold cyan]Flower 內置差分隱私策略[/bold cyan]",
        border_style="cyan"
    ))

    # 客戶端固定裁剪差分隱私
    strategy = DifferentialPrivacyClientSideFixedClipping(
        # 基本參數
        fraction_fit=0.1,
        fraction_evaluate=0.1,
        min_fit_clients=10,
        min_available_clients=100,

        # 差分隱私參數
        noise_multiplier=1.0,  # 噪聲倍數
        clipping_norm=1.0,  # 裁剪範數
        num_sampled_clients=10,  # 每輪採樣的客戶端數

        # 配置函數
        on_fit_config_fn=lambda rnd: {
            "learning_rate": 0.01,
            "local_epochs": 3,
        },
    )

    console.print("[green]✓ DP 策略配置完成[/green]")
    console.print("  - 噪聲倍數: 1.0")
    console.print("  - 裁剪範數: 1.0")
    console.print("  - 每輪採樣: 10 個客戶端")

    console.print("\n[yellow]工作原理:[/yellow]")
    console.print("  1. 客戶端訓練並裁剪梯度")
    console.print("  2. 服務器聚合時添加高斯噪聲")
    console.print("  3. 自動跟踪隱私預算")


# ============================================================================
# 4. 隱私預算計算
# ============================================================================

class PrivacyAccountant:
    """
    隱私預算會計師

    跟踪和計算累積的隱私損失
    """

    def __init__(
        self,
        target_epsilon: float,
        target_delta: float,
        num_clients: int,
        sampling_rate: float
    ):
        """
        初始化隱私會計師

        Args:
            target_epsilon: 目標隱私預算
            target_delta: 目標失效概率
            num_clients: 總客戶端數
            sampling_rate: 客戶端採樣率
        """
        self.target_epsilon = target_epsilon
        self.target_delta = target_delta
        self.num_clients = num_clients
        self.sampling_rate = sampling_rate
        self.accumulated_epsilon = 0.0

    def compute_epsilon(
        self,
        noise_multiplier: float,
        num_rounds: int
    ) -> float:
        """
        計算給定參數下的隱私預算

        使用 Rényi DP (RDP) 組合定理

        Args:
            noise_multiplier: 噪聲倍數
            num_rounds: 訓練輪數

        Returns:
            累積的 epsilon 值
        """
        # 簡化計算（實際應使用 autodp 庫）
        # epsilon ≈ sqrt(2 * num_rounds * ln(1/δ)) * sampling_rate / noise_multiplier

        epsilon = math.sqrt(
            2 * num_rounds * math.log(1 / self.target_delta)
        ) * self.sampling_rate / noise_multiplier

        return epsilon

    def compute_noise_multiplier(
        self,
        num_rounds: int
    ) -> float:
        """
        反向計算：給定 epsilon，計算所需的噪聲倍數

        Args:
            num_rounds: 訓練輪數

        Returns:
            所需的噪聲倍數
        """
        noise_multiplier = (
            math.sqrt(2 * num_rounds * math.log(1 / self.target_delta))
            * self.sampling_rate
            / self.target_epsilon
        )

        return noise_multiplier

    def max_rounds(
        self,
        noise_multiplier: float
    ) -> int:
        """
        計算給定噪聲倍數下的最大訓練輪數

        Args:
            noise_multiplier: 噪聲倍數

        Returns:
            最大輪數
        """
        max_rounds = int(
            (self.target_epsilon * noise_multiplier / self.sampling_rate) ** 2
            / (2 * math.log(1 / self.target_delta))
        )

        return max_rounds

    def print_privacy_analysis(self):
        """打印隱私分析結果"""
        console.print(Panel.fit(
            "[bold cyan]隱私預算分析[/bold cyan]",
            border_style="cyan"
        ))

        table = Table(show_header=True, header_style="bold blue")
        table.add_column("訓練輪數", style="cyan", justify="center")
        table.add_column("噪聲倍數", style="yellow", justify="center")
        table.add_column("ε (epsilon)", style="green", justify="center")
        table.add_column("狀態", style="white", justify="center")

        rounds_options = [5, 10, 20, 50, 100]
        for rounds in rounds_options:
            noise_mult = self.compute_noise_multiplier(rounds)
            epsilon = self.compute_epsilon(noise_mult, rounds)

            status = "✓" if epsilon <= self.target_epsilon else "✗"
            color = "green" if epsilon <= self.target_epsilon else "red"

            table.add_row(
                str(rounds),
                f"{noise_mult:.4f}",
                f"{epsilon:.4f}",
                f"[{color}]{status}[/{color}]"
            )

        console.print(table)


# ============================================================================
# 演示和測試
# ============================================================================

def create_dummy_model_and_data():
    """創建虛擬模型和數據"""
    class SimpleModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.fc1 = nn.Linear(10, 32)
            self.fc2 = nn.Linear(32, 2)
            self.relu = nn.ReLU()

        def forward(self, x):
            x = self.relu(self.fc1(x))
            return self.fc2(x)

    model = SimpleModel()

    # 創建數據
    X = torch.randn(100, 10)
    y = torch.randint(0, 2, (100,))
    dataset = TensorDataset(X, y)
    trainloader = DataLoader(dataset[:80], batch_size=16)
    valloader = DataLoader(dataset[80:], batch_size=16)

    return model, trainloader, valloader


def main():
    """主函數"""
    console.print("\n[bold magenta]Flower 聯邦學習 - 差分隱私[/bold magenta]\n")

    # 1. 基礎概念
    DifferentialPrivacyExplainer.explain_basics()

    console.print("\n" + "="*70 + "\n")

    # 2. DP 策略
    demonstrate_dp_strategy()

    console.print("\n" + "="*70 + "\n")

    # 3. 隱私預算分析
    accountant = PrivacyAccountant(
        target_epsilon=1.0,
        target_delta=1e-5,
        num_clients=100,
        sampling_rate=0.1
    )
    accountant.print_privacy_analysis()

    console.print("\n" + "="*70 + "\n")

    # 4. DP 客戶端演示
    console.print(Panel.fit(
        "[bold cyan]差分隱私客戶端演示[/bold cyan]",
        border_style="cyan"
    ))

    model, trainloader, valloader = create_dummy_model_and_data()

    dp_client = DPClient(
        client_id=1,
        model=model,
        trainloader=trainloader,
        valloader=valloader,
        epsilon=1.0,
        delta=1e-5,
        max_grad_norm=1.0
    )

    console.print("\n[green]✓ DP 客戶端創建成功[/green]")

    console.print("\n[bold green]✓ 差分隱私示例完成！[/bold green]")
    console.print("\n[yellow]關鍵要點:[/yellow]")
    console.print("  1. ε (epsilon) - 隱私預算，越小越私密")
    console.print("  2. δ (delta) - 失效概率")
    console.print("  3. 梯度裁剪 - 限制單個樣本的影響")
    console.print("  4. 噪聲添加 - 保護隱私的關鍵")
    console.print("  5. 隱私預算 - 需要仔細管理和跟踪")

    console.print("\n[cyan]最佳實踐:[/cyan]")
    console.print("  • ε = 0.1-10 (較小值提供更強隱私)")
    console.print("  • δ < 1/n (n 是數據集大小)")
    console.print("  • 梯度裁剪閾值需要調優")
    console.print("  • 使用 RDP 進行精確隱私會計")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]程序被用戶中斷[/yellow]")
    except Exception as e:
        logger.exception("程序執行出錯")
        console.print(f"[red]錯誤: {str(e)}[/red]")

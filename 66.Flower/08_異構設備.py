"""
Flower 聯邦學習框架 - 異構設備處理

這個示例展示如何處理異構設備環境：
1. 系統異構性（計算能力不同）
2. 數據異構性（Non-IID 數據）
3. 動態客戶端選擇
4. 自適應訓練配置
5. 資源感知調度
"""

import flwr as fl
from flwr.server.strategy import FedAvg
from flwr.common import Scalar
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import logging
import time

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console = Console()


# ============================================================================
# 1. 設備類型定義
# ============================================================================

class DeviceType(Enum):
    """設備類型枚舉"""
    HIGH_END = "high_end"  # 高端設備（強大計算能力）
    MID_RANGE = "mid_range"  # 中端設備
    LOW_END = "low_end"  # 低端設備（資源受限）
    EDGE = "edge"  # 邊緣設備
    MOBILE = "mobile"  # 移動設備


@dataclass
class DeviceProfile:
    """
    設備配置文件

    記錄設備的各種特性和能力
    """
    device_id: int
    device_type: DeviceType

    # 計算能力
    compute_power: float  # 相對計算能力 (0.1 - 1.0)
    memory_mb: int  # 內存大小（MB）
    has_gpu: bool  # 是否有 GPU

    # 網絡狀況
    bandwidth_mbps: float  # 帶寬（Mbps）
    latency_ms: float  # 延遲（ms）

    # 電池狀態（移動設備）
    battery_level: Optional[float] = None  # 電量 (0-1)
    is_charging: Optional[bool] = None  # 是否充電中

    # 數據特性
    num_samples: int = 0  # 數據量
    data_quality: float = 1.0  # 數據質量 (0-1)

    def can_participate(self) -> bool:
        """判斷設備是否可以參與訓練"""
        # 基本資源檢查
        if self.memory_mb < 512:
            return False

        # 移動設備電量檢查
        if self.device_type == DeviceType.MOBILE:
            if self.battery_level is not None and self.battery_level < 0.3:
                if not self.is_charging:
                    return False

        # 網絡檢查
        if self.bandwidth_mbps < 1.0:
            return False

        return True

    def get_max_batch_size(self) -> int:
        """根據設備能力計算最大 batch size"""
        if self.device_type == DeviceType.HIGH_END:
            return 128
        elif self.device_type == DeviceType.MID_RANGE:
            return 64
        elif self.device_type == DeviceType.LOW_END:
            return 16
        else:
            return 8

    def get_max_epochs(self) -> int:
        """根據設備能力計算最大訓練輪數"""
        if self.compute_power > 0.8:
            return 10
        elif self.compute_power > 0.5:
            return 5
        else:
            return 2


# ============================================================================
# 2. 異構設備客戶端
# ============================================================================

class HeterogeneousClient(fl.client.NumPyClient):
    """
    異構設備客戶端

    根據設備能力自適應調整訓練策略
    """

    def __init__(
        self,
        profile: DeviceProfile,
        model: nn.Module,
        trainloader: DataLoader,
        valloader: DataLoader
    ):
        """
        初始化異構客戶端

        Args:
            profile: 設備配置文件
            model: PyTorch 模型
            trainloader: 訓練數據加載器
            valloader: 驗證數據加載器
        """
        self.profile = profile
        self.model = model
        self.trainloader = trainloader
        self.valloader = valloader

        # 根據設備選擇計算設備
        if self.profile.has_gpu:
            self.device = torch.device("cuda")
        else:
            self.device = torch.device("cpu")

        self.model.to(self.device)

        console.print(f"[green]✓ 異構客戶端 {profile.device_id} ({profile.device_type.value})[/green]")
        console.print(f"  - 計算能力: {profile.compute_power:.2f}")
        console.print(f"  - 內存: {profile.memory_mb} MB")
        console.print(f"  - GPU: {'是' if profile.has_gpu else '否'}")

    def get_parameters(self, config: Dict[str, Scalar]) -> List[np.ndarray]:
        """獲取模型參數"""
        return [val.cpu().numpy() for _, val in self.model.state_dict().items()]

    def set_parameters(self, parameters: List[np.ndarray]) -> None:
        """設置模型參數"""
        from collections import OrderedDict
        params_dict = zip(self.model.state_dict().keys(), parameters)
        state_dict = OrderedDict({k: torch.tensor(v) for k, v in params_dict})
        self.model.load_state_dict(state_dict, strict=True)

    def fit(
        self,
        parameters: List[np.ndarray],
        config: Dict[str, Scalar]
    ) -> Tuple[List[np.ndarray], int, Dict]:
        """
        自適應訓練

        根據設備能力調整訓練參數
        """
        self.set_parameters(parameters)

        # 從服務器獲取基礎配置
        base_lr = float(config.get("learning_rate", 0.01))
        base_epochs = int(config.get("local_epochs", 5))
        base_batch_size = int(config.get("batch_size", 32))

        # 根據設備能力調整
        actual_epochs = min(base_epochs, self.profile.get_max_epochs())
        actual_batch_size = min(base_batch_size, self.profile.get_max_batch_size())

        # 低端設備降低學習率避免不穩定
        if self.profile.compute_power < 0.3:
            actual_lr = base_lr * 0.5
        else:
            actual_lr = base_lr

        console.print(f"\n[blue]客戶端 {self.profile.device_id} 開始訓練[/blue]")
        console.print(f"  配置: epochs={actual_epochs}, batch_size={actual_batch_size}, lr={actual_lr:.4f}")

        # 訓練
        start_time = time.time()
        train_loss, train_acc = self._train(actual_epochs, actual_lr, actual_batch_size)
        training_time = time.time() - start_time

        console.print(f"[green]✓ 訓練完成[/green]")
        console.print(f"  - 損失: {train_loss:.4f}")
        console.print(f"  - 準確率: {train_acc:.4f}")
        console.print(f"  - 訓練時間: {training_time:.2f}s")

        # 返回指標（包含設備信息）
        metrics = {
            "train_loss": train_loss,
            "train_accuracy": train_acc,
            "training_time": training_time,
            "device_type": self.profile.device_type.value,
            "compute_power": self.profile.compute_power,
        }

        return self.get_parameters(config={}), len(self.trainloader.dataset), metrics

    def evaluate(
        self,
        parameters: List[np.ndarray],
        config: Dict[str, Scalar]
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

    def _train(
        self,
        epochs: int,
        learning_rate: float,
        batch_size: int
    ) -> Tuple[float, float]:
        """執行訓練"""
        self.model.train()

        # 重新創建 DataLoader（使用調整後的 batch size）
        dataset = self.trainloader.dataset
        trainloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

        optimizer = torch.optim.SGD(self.model.parameters(), lr=learning_rate)
        criterion = nn.CrossEntropyLoss()

        total_loss = 0.0
        total_correct = 0
        total_samples = 0

        for epoch in range(epochs):
            for data, target in trainloader:
                data, target = data.to(self.device), target.to(self.device)

                optimizer.zero_grad()
                output = self.model(data)
                loss = criterion(output, target)
                loss.backward()
                optimizer.step()

                total_loss += loss.item() * len(data)
                _, predicted = torch.max(output, 1)
                total_correct += (predicted == target).sum().item()
                total_samples += len(data)

        avg_loss = total_loss / total_samples
        avg_accuracy = total_correct / total_samples

        return avg_loss, avg_accuracy


# ============================================================================
# 3. 異構感知策略
# ============================================================================

class HeterogeneousAwareStrategy(FedAvg):
    """
    異構感知聚合策略

    考慮設備異構性的智能客戶端選擇和聚合
    """

    def __init__(
        self,
        device_profiles: Dict[int, DeviceProfile],
        **kwargs
    ):
        """
        初始化策略

        Args:
            device_profiles: 設備配置字典
        """
        super().__init__(**kwargs)
        self.device_profiles = device_profiles

        console.print("[green]✓ 異構感知策略初始化[/green]")

    def configure_fit(
        self,
        server_round: int,
        parameters,
        client_manager
    ):
        """
        配置訓練階段

        智能選擇客戶端並提供自適應配置
        """
        # 獲取配置
        config = {}
        if self.on_fit_config_fn is not None:
            config = self.on_fit_config_fn(server_round)

        # 獲取可用客戶端
        sample_size, min_num_clients = self.num_fit_clients(
            client_manager.num_available()
        )

        # 智能客戶端選擇
        clients = self._select_heterogeneous_clients(
            client_manager,
            sample_size
        )

        console.print(f"\n[yellow]輪次 {server_round}: 選擇了 {len(clients)} 個客戶端[/yellow]")

        # 為每個客戶端提供配置
        from flwr.common import FitIns, ndarrays_to_parameters

        fit_ins = FitIns(parameters, config)

        return [(client, fit_ins) for client in clients]

    def _select_heterogeneous_clients(
        self,
        client_manager,
        num_clients: int
    ):
        """
        智能選擇客戶端

        優先選擇：
        1. 計算能力強的設備
        2. 網絡狀況好的設備
        3. 電量充足的移動設備
        """
        all_clients = list(client_manager.all().values())

        # 計算每個客戶端的優先級分數
        client_scores = []

        for client in all_clients:
            # 簡化：使用客戶端 ID 獲取設備配置
            # 實際應從客戶端獲取實時狀態
            try:
                # 假設客戶端 ID 存儲在 cid 中
                client_id = int(client.cid)

                if client_id not in self.device_profiles:
                    continue

                profile = self.device_profiles[client_id]

                # 檢查是否可以參與
                if not profile.can_participate():
                    continue

                # 計算優先級分數
                score = (
                    profile.compute_power * 0.4 +  # 計算能力權重 40%
                    (profile.bandwidth_mbps / 100) * 0.3 +  # 帶寬權重 30%
                    profile.data_quality * 0.2 +  # 數據質量權重 20%
                    (1.0 if profile.has_gpu else 0.5) * 0.1  # GPU 權重 10%
                )

                # 移動設備電量懲罰
                if profile.device_type == DeviceType.MOBILE and profile.battery_level:
                    score *= profile.battery_level

                client_scores.append((client, score))

            except (ValueError, AttributeError):
                continue

        # 按分數排序並選擇
        client_scores.sort(key=lambda x: x[1], reverse=True)
        selected_clients = [client for client, _ in client_scores[:num_clients]]

        return selected_clients

    def aggregate_fit(
        self,
        server_round: int,
        results,
        failures
    ):
        """
        聚合訓練結果

        考慮設備異構性的加權聚合
        """
        if not results:
            return None, {}

        # 顯示設備類型分布
        device_types = {}
        for _, fit_res in results:
            device_type = fit_res.metrics.get("device_type", "unknown")
            device_types[device_type] = device_types.get(device_type, 0) + 1

        console.print(f"\n[cyan]輪次 {server_round} 設備分布:[/cyan]")
        for dtype, count in device_types.items():
            console.print(f"  - {dtype}: {count}")

        # 調用父類的聚合方法
        parameters, metrics = super().aggregate_fit(server_round, results, failures)

        return parameters, metrics


# ============================================================================
# 4. 設備模擬器
# ============================================================================

def create_heterogeneous_devices(num_devices: int = 20) -> List[DeviceProfile]:
    """
    創建模擬的異構設備

    Args:
        num_devices: 設備數量

    Returns:
        設備配置列表
    """
    console.print(f"\n[yellow]創建 {num_devices} 個異構設備...[/yellow]")

    devices = []
    device_types = [
        DeviceType.HIGH_END,
        DeviceType.MID_RANGE,
        DeviceType.LOW_END,
        DeviceType.EDGE,
        DeviceType.MOBILE
    ]

    for i in range(num_devices):
        # 隨機選擇設備類型
        device_type = np.random.choice(device_types)

        # 根據設備類型設置參數
        if device_type == DeviceType.HIGH_END:
            compute_power = np.random.uniform(0.8, 1.0)
            memory_mb = np.random.randint(4096, 8192)
            has_gpu = True
            bandwidth_mbps = np.random.uniform(50, 100)
            latency_ms = np.random.uniform(10, 30)
        elif device_type == DeviceType.MID_RANGE:
            compute_power = np.random.uniform(0.5, 0.8)
            memory_mb = np.random.randint(2048, 4096)
            has_gpu = np.random.choice([True, False])
            bandwidth_mbps = np.random.uniform(20, 50)
            latency_ms = np.random.uniform(30, 60)
        elif device_type == DeviceType.LOW_END:
            compute_power = np.random.uniform(0.2, 0.5)
            memory_mb = np.random.randint(512, 2048)
            has_gpu = False
            bandwidth_mbps = np.random.uniform(5, 20)
            latency_ms = np.random.uniform(60, 120)
        elif device_type == DeviceType.EDGE:
            compute_power = np.random.uniform(0.3, 0.6)
            memory_mb = np.random.randint(1024, 2048)
            has_gpu = False
            bandwidth_mbps = np.random.uniform(10, 30)
            latency_ms = np.random.uniform(40, 80)
        else:  # MOBILE
            compute_power = np.random.uniform(0.3, 0.7)
            memory_mb = np.random.randint(1024, 3072)
            has_gpu = False
            bandwidth_mbps = np.random.uniform(5, 30)
            latency_ms = np.random.uniform(50, 150)

        profile = DeviceProfile(
            device_id=i,
            device_type=device_type,
            compute_power=compute_power,
            memory_mb=memory_mb,
            has_gpu=has_gpu,
            bandwidth_mbps=bandwidth_mbps,
            latency_ms=latency_ms,
            num_samples=np.random.randint(100, 1000),
            data_quality=np.random.uniform(0.7, 1.0)
        )

        # 移動設備添加電池信息
        if device_type == DeviceType.MOBILE:
            profile.battery_level = np.random.uniform(0.2, 1.0)
            profile.is_charging = np.random.choice([True, False])

        devices.append(profile)

    # 顯示統計
    display_device_statistics(devices)

    return devices


def display_device_statistics(devices: List[DeviceProfile]):
    """顯示設備統計信息"""
    table = Table(title="設備統計", show_header=True, header_style="bold blue")
    table.add_column("設備類型", style="cyan")
    table.add_column("數量", justify="center", style="yellow")
    table.add_column("平均算力", justify="center", style="green")
    table.add_column("GPU 比例", justify="center", style="magenta")

    device_stats = {}
    for device in devices:
        dtype = device.device_type.value
        if dtype not in device_stats:
            device_stats[dtype] = {
                "count": 0,
                "total_compute": 0.0,
                "gpu_count": 0
            }

        device_stats[dtype]["count"] += 1
        device_stats[dtype]["total_compute"] += device.compute_power
        device_stats[dtype]["gpu_count"] += 1 if device.has_gpu else 0

    for dtype, stats in device_stats.items():
        count = stats["count"]
        avg_compute = stats["total_compute"] / count
        gpu_ratio = stats["gpu_count"] / count

        table.add_row(
            dtype,
            str(count),
            f"{avg_compute:.2f}",
            f"{gpu_ratio:.1%}"
        )

    console.print(table)


# ============================================================================
# 主函數
# ============================================================================

def main():
    """主函數"""
    console.print("\n[bold magenta]Flower 聯邦學習 - 異構設備處理[/bold magenta]\n")

    # 創建異構設備
    devices = create_heterogeneous_devices(num_devices=20)

    # 統計可參與設備
    eligible_devices = [d for d in devices if d.can_participate()]
    console.print(f"\n[green]可參與訓練的設備: {len(eligible_devices)}/{len(devices)}[/green]")

    console.print("\n[bold green]✓ 異構設備處理示例完成！[/bold green]")
    console.print("\n[yellow]關鍵要點:[/yellow]")
    console.print("  1. 設備分類 - 識別不同類型的設備")
    console.print("  2. 自適應配置 - 根據設備能力調整參數")
    console.print("  3. 智能選擇 - 優先選擇高性能設備")
    console.print("  4. 資源感知 - 考慮電量、帶寬等因素")
    console.print("  5. 公平性 - 確保所有設備都能參與")

    console.print("\n[cyan]處理策略:[/cyan]")
    console.print("  • 高端設備: 大 batch size, 多 epochs")
    console.print("  • 低端設備: 小 batch size, 少 epochs")
    console.print("  • 移動設備: 檢查電量和充電狀態")
    console.print("  • 邊緣設備: 考慮網絡延遲")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]程序被用戶中斷[/yellow]")
    except Exception as e:
        logger.exception("程序執行出錯")
        console.print(f"[red]錯誤: {str(e)}[/red]")

"""
Flower 聯邦學習框架 - 模型評估

這個示例展示聯邦學習中的模型評估方法：
1. 分佈式評估
2. 集中式評估
3. 公平性評估
4. 隱私保護評估
5. 評估指標聚合
"""

import flwr as fl
from flwr.server.strategy import FedAvg
from flwr.common import Scalar, Parameters
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
from typing import Dict, List, Tuple, Optional, Callable
from collections import OrderedDict
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress
import logging
import matplotlib.pyplot as plt
from pathlib import Path

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console = Console()


# ============================================================================
# 1. 評估客戶端
# ============================================================================

class EvaluationClient(fl.client.NumPyClient):
    """
    支持詳細評估的客戶端
    """

    def __init__(
        self,
        client_id: int,
        model: nn.Module,
        trainloader: DataLoader,
        valloader: DataLoader,
        testloader: Optional[DataLoader] = None,
        device: str = "cpu"
    ):
        """
        初始化評估客戶端

        Args:
            client_id: 客戶端 ID
            model: PyTorch 模型
            trainloader: 訓練數據加載器
            valloader: 驗證數據加載器
            testloader: 測試數據加載器（可選）
            device: 計算設備
        """
        self.client_id = client_id
        self.model = model
        self.trainloader = trainloader
        self.valloader = valloader
        self.testloader = testloader or valloader
        self.device = torch.device(device)
        self.model.to(self.device)

        console.print(f"[green]✓ 評估客戶端 {client_id} 初始化[/green]")

    def get_parameters(self, config: Dict[str, Scalar]) -> List[np.ndarray]:
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
        config: Dict[str, Scalar]
    ) -> Tuple[List[np.ndarray], int, Dict]:
        """訓練模型"""
        self.set_parameters(parameters)

        epochs = int(config.get("local_epochs", 1))
        lr = float(config.get("learning_rate", 0.001))

        train_loss, train_acc = self._train(epochs, lr)

        metrics = {
            "train_loss": train_loss,
            "train_accuracy": train_acc,
        }

        return self.get_parameters(config={}), len(self.trainloader.dataset), metrics

    def evaluate(
        self,
        parameters: List[np.ndarray],
        config: Dict[str, Scalar]
    ) -> Tuple[float, int, Dict]:
        """
        詳細評估模型

        返回多種評估指標
        """
        self.set_parameters(parameters)

        # 選擇評估數據集
        use_test = config.get("use_test_set", False)
        dataloader = self.testloader if use_test else self.valloader

        # 執行評估
        metrics = self._evaluate_detailed(dataloader)

        console.print(f"[cyan]客戶端 {self.client_id} 評估結果:[/cyan]")
        console.print(f"  - 損失: {metrics['loss']:.4f}")
        console.print(f"  - 準確率: {metrics['accuracy']:.4f}")
        console.print(f"  - F1 分數: {metrics.get('f1', 0):.4f}")

        return metrics["loss"], metrics["num_examples"], metrics

    def _train(self, epochs: int, learning_rate: float) -> Tuple[float, float]:
        """執行訓練"""
        self.model.train()

        optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate)
        criterion = nn.CrossEntropyLoss()

        total_loss = 0.0
        total_correct = 0
        total_samples = 0

        for epoch in range(epochs):
            for data, target in self.trainloader:
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

    def _evaluate_detailed(self, dataloader: DataLoader) -> Dict[str, float]:
        """
        詳細評估

        計算多種指標：
        - 損失
        - 準確率
        - 精確率、召回率、F1
        - 混淆矩陣
        """
        self.model.eval()

        criterion = nn.CrossEntropyLoss()
        total_loss = 0.0
        all_predictions = []
        all_targets = []

        with torch.no_grad():
            for data, target in dataloader:
                data, target = data.to(self.device), target.to(self.device)

                output = self.model(data)
                loss = criterion(output, target)
                total_loss += loss.item() * len(data)

                _, predicted = torch.max(output, 1)
                all_predictions.extend(predicted.cpu().numpy())
                all_targets.extend(target.cpu().numpy())

        # 轉換為 numpy 數組
        predictions = np.array(all_predictions)
        targets = np.array(all_targets)

        # 計算指標
        num_examples = len(targets)
        accuracy = (predictions == targets).sum() / num_examples

        # 計算每個類別的精確率、召回率
        num_classes = len(np.unique(targets))
        precision_per_class = []
        recall_per_class = []

        for class_id in range(num_classes):
            # True Positives
            tp = ((predictions == class_id) & (targets == class_id)).sum()
            # False Positives
            fp = ((predictions == class_id) & (targets != class_id)).sum()
            # False Negatives
            fn = ((predictions != class_id) & (targets == class_id)).sum()

            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0

            precision_per_class.append(precision)
            recall_per_class.append(recall)

        # 宏平均
        macro_precision = np.mean(precision_per_class)
        macro_recall = np.mean(recall_per_class)
        macro_f1 = 2 * (macro_precision * macro_recall) / (macro_precision + macro_recall) \
            if (macro_precision + macro_recall) > 0 else 0.0

        metrics = {
            "loss": total_loss / num_examples,
            "accuracy": float(accuracy),
            "precision": float(macro_precision),
            "recall": float(macro_recall),
            "f1": float(macro_f1),
            "num_examples": num_examples,
        }

        return metrics


# ============================================================================
# 2. 集中式評估
# ============================================================================

def get_centralized_evaluate_fn(
    model: nn.Module,
    testloader: DataLoader,
    device: str = "cpu"
) -> Callable[[int, Parameters, Dict], Optional[Tuple[float, Dict]]]:
    """
    創建集中式評估函數

    在服務器端使用全局測試集評估模型

    Args:
        model: PyTorch 模型
        testloader: 測試數據加載器
        device: 計算設備

    Returns:
        評估函數
    """
    def evaluate(
        server_round: int,
        parameters: Parameters,
        config: Dict[str, Scalar]
    ) -> Optional[Tuple[float, Dict]]:
        """
        在服務器端評估模型

        Args:
            server_round: 當前輪次
            parameters: 模型參數
            config: 配置

        Returns:
            (損失, 指標字典)
        """
        console.print(f"\n[bold yellow]輪次 {server_round}: 集中式評估[/bold yellow]")

        # 設置模型參數
        params_dict = zip(
            model.state_dict().keys(),
            parameters_to_ndarrays(parameters)
        )
        state_dict = OrderedDict({k: torch.tensor(v) for k, v in params_dict})
        model.load_state_dict(state_dict, strict=True)

        # 評估
        model.to(device)
        model.eval()

        criterion = nn.CrossEntropyLoss()
        total_loss = 0.0
        correct = 0
        total = 0

        with torch.no_grad():
            for data, target in testloader:
                data, target = data.to(device), target.to(device)

                output = model(data)
                loss = criterion(output, target)
                total_loss += loss.item() * len(data)

                _, predicted = torch.max(output, 1)
                total += target.size(0)
                correct += (predicted == target).sum().item()

        avg_loss = total_loss / total
        accuracy = correct / total

        console.print(f"[green]集中式評估結果:[/green]")
        console.print(f"  - 損失: {avg_loss:.4f}")
        console.print(f"  - 準確率: {accuracy:.4f}")

        return avg_loss, {"accuracy": accuracy}

    return evaluate


def parameters_to_ndarrays(parameters: Parameters) -> List[np.ndarray]:
    """將 Parameters 轉換為 ndarray 列表"""
    from flwr.common import parameters_to_ndarrays as flwr_params_to_ndarrays
    return flwr_params_to_ndarrays(parameters)


# ============================================================================
# 3. 公平性評估
# ============================================================================

class FairnessEvaluator:
    """
    公平性評估器

    評估模型在不同客戶端上的性能差異
    """

    def __init__(self):
        self.client_metrics = {}

    def record_client_metrics(
        self,
        client_id: int,
        metrics: Dict[str, float]
    ):
        """記錄客戶端指標"""
        self.client_metrics[client_id] = metrics

    def evaluate_fairness(self) -> Dict[str, float]:
        """
        評估公平性

        計算：
        - 準確率標準差（越小越公平）
        - 最小-最大準確率差距
        - 變異係數
        """
        if not self.client_metrics:
            return {}

        accuracies = [m["accuracy"] for m in self.client_metrics.values()]

        fairness_metrics = {
            "accuracy_mean": float(np.mean(accuracies)),
            "accuracy_std": float(np.std(accuracies)),
            "accuracy_min": float(np.min(accuracies)),
            "accuracy_max": float(np.max(accuracies)),
            "accuracy_gap": float(np.max(accuracies) - np.min(accuracies)),
            "coefficient_of_variation": float(np.std(accuracies) / np.mean(accuracies))
        }

        return fairness_metrics

    def print_fairness_report(self):
        """打印公平性報告"""
        console.print(Panel.fit(
            "[bold cyan]公平性評估報告[/bold cyan]",
            border_style="cyan"
        ))

        fairness = self.evaluate_fairness()

        table = Table(show_header=True, header_style="bold blue")
        table.add_column("指標", style="cyan", width=25)
        table.add_column("數值", style="yellow", justify="right")
        table.add_column("評價", style="white")

        table.add_row(
            "平均準確率",
            f"{fairness['accuracy_mean']:.4f}",
            "基準性能"
        )
        table.add_row(
            "準確率標準差",
            f"{fairness['accuracy_std']:.4f}",
            "越小越公平" if fairness['accuracy_std'] < 0.05 else "存在差異"
        )
        table.add_row(
            "最小準確率",
            f"{fairness['accuracy_min']:.4f}",
            "最差客戶端"
        )
        table.add_row(
            "最大準確率",
            f"{fairness['accuracy_max']:.4f}",
            "最佳客戶端"
        )
        table.add_row(
            "準確率差距",
            f"{fairness['accuracy_gap']:.4f}",
            "良好" if fairness['accuracy_gap'] < 0.1 else "需改進"
        )

        console.print(table)

        # 評估總結
        if fairness['accuracy_std'] < 0.05 and fairness['accuracy_gap'] < 0.1:
            console.print("\n[green]✓ 公平性良好[/green]")
        elif fairness['accuracy_std'] < 0.1 and fairness['accuracy_gap'] < 0.2:
            console.print("\n[yellow]⚠ 公平性中等[/yellow]")
        else:
            console.print("\n[red]✗ 公平性較差，需要改進[/red]")


# ============================================================================
# 4. 評估策略
# ============================================================================

class DetailedEvaluationStrategy(FedAvg):
    """
    詳細評估策略

    支持集中式和分佈式評估
    """

    def __init__(
        self,
        evaluate_fn: Optional[Callable] = None,
        **kwargs
    ):
        """
        初始化策略

        Args:
            evaluate_fn: 集中式評估函數
        """
        super().__init__(**kwargs)
        self.evaluate_fn_custom = evaluate_fn
        self.fairness_evaluator = FairnessEvaluator()
        self.evaluation_history = {
            "rounds": [],
            "centralized_loss": [],
            "centralized_accuracy": [],
            "distributed_loss": [],
            "distributed_accuracy": [],
        }

    def evaluate(
        self,
        server_round: int,
        parameters: Parameters
    ) -> Optional[Tuple[float, Dict[str, Scalar]]]:
        """
        集中式評估

        在服務器端使用全局測試集評估
        """
        if self.evaluate_fn_custom is None:
            return None

        loss, metrics = self.evaluate_fn_custom(server_round, parameters, {})

        # 記錄歷史
        self.evaluation_history["rounds"].append(server_round)
        self.evaluation_history["centralized_loss"].append(loss)
        self.evaluation_history["centralized_accuracy"].append(metrics["accuracy"])

        return loss, metrics

    def aggregate_evaluate(
        self,
        server_round: int,
        results,
        failures
    ) -> Tuple[Optional[float], Dict[str, Scalar]]:
        """
        聚合分佈式評估結果
        """
        if not results:
            return None, {}

        # 記錄每個客戶端的指標（用於公平性評估）
        for client_proxy, evaluate_res in results:
            client_id = int(client_proxy.cid)
            self.fairness_evaluator.record_client_metrics(
                client_id,
                evaluate_res.metrics
            )

        # 調用父類的聚合方法
        loss, metrics = super().aggregate_evaluate(server_round, results, failures)

        # 記錄歷史
        if loss is not None:
            self.evaluation_history["distributed_loss"].append(loss)
            self.evaluation_history["distributed_accuracy"].append(
                metrics.get("accuracy", 0)
            )

        console.print(f"\n[cyan]輪次 {server_round} 分佈式評估:[/cyan]")
        console.print(f"  - 平均損失: {loss:.4f}")
        console.print(f"  - 平均準確率: {metrics.get('accuracy', 0):.4f}")

        return loss, metrics

    def print_evaluation_summary(self):
        """打印評估總結"""
        console.print("\n" + "="*70)
        console.print(Panel.fit(
            "[bold green]評估總結[/bold green]",
            border_style="green"
        ))

        # 評估歷史表格
        table = Table(title="評估歷史", show_header=True, header_style="bold magenta")
        table.add_column("輪次", style="cyan", justify="center")
        table.add_column("集中式準確率", style="yellow", justify="right")
        table.add_column("分佈式準確率", style="green", justify="right")
        table.add_column("差異", style="white", justify="right")

        for i, round_num in enumerate(self.evaluation_history["rounds"]):
            cent_acc = self.evaluation_history["centralized_accuracy"][i]
            dist_acc = self.evaluation_history["distributed_accuracy"][i] \
                if i < len(self.evaluation_history["distributed_accuracy"]) else 0
            diff = abs(cent_acc - dist_acc)

            table.add_row(
                str(round_num),
                f"{cent_acc:.4f}",
                f"{dist_acc:.4f}",
                f"{diff:.4f}"
            )

        console.print(table)

        # 公平性報告
        self.fairness_evaluator.print_fairness_report()


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
    X = torch.randn(200, 10)
    y = torch.randint(0, 2, (200,))
    dataset = TensorDataset(X, y)

    trainloader = DataLoader(dataset[:100], batch_size=16)
    valloader = DataLoader(dataset[100:150], batch_size=16)
    testloader = DataLoader(dataset[150:], batch_size=16)

    return model, trainloader, valloader, testloader


def main():
    """主函數"""
    console.print("\n[bold magenta]Flower 聯邦學習 - 模型評估[/bold magenta]\n")

    # 創建模型和數據
    model, trainloader, valloader, testloader = create_dummy_model_and_data()

    # 創建評估客戶端
    console.print(Panel.fit(
        "[bold cyan]創建評估客戶端[/bold cyan]",
        border_style="cyan"
    ))

    client = EvaluationClient(
        client_id=1,
        model=model,
        trainloader=trainloader,
        valloader=valloader,
        testloader=testloader
    )

    # 測試評估
    console.print("\n[yellow]執行詳細評估...[/yellow]")
    params = client.get_parameters({})
    loss, num_examples, metrics = client.evaluate(params, {})

    # 公平性評估器演示
    console.print("\n" + "="*70)
    fairness_eval = FairnessEvaluator()

    # 模擬多個客戶端的指標
    for i in range(5):
        fairness_eval.record_client_metrics(
            i,
            {"accuracy": np.random.uniform(0.7, 0.95)}
        )

    fairness_eval.print_fairness_report()

    console.print("\n[bold green]✓ 模型評估示例完成！[/bold green]")
    console.print("\n[yellow]關鍵要點:[/yellow]")
    console.print("  1. 分佈式評估 - 客戶端使用本地數據評估")
    console.print("  2. 集中式評估 - 服務器使用全局測試集評估")
    console.print("  3. 詳細指標 - 準確率、F1、精確率、召回率")
    console.print("  4. 公平性評估 - 確保所有客戶端性能均衡")
    console.print("  5. 評估歷史 - 跟踪訓練過程中的性能變化")

    console.print("\n[cyan]最佳實踐:[/cyan]")
    console.print("  • 同時使用集中式和分佈式評估")
    console.print("  • 監控公平性指標")
    console.print("  • 記錄和可視化評估歷史")
    console.print("  • 使用多種評估指標")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]程序被用戶中斷[/yellow]")
    except Exception as e:
        logger.exception("程序執行出錯")
        console.print(f"[red]錯誤: {str(e)}[/red]")

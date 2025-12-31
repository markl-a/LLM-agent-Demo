"""
Flower 聯邦學習框架 - 聚合策略

這個示例深入探討各種聚合策略：
1. FedAvg - 聯邦平均
2. FedProx - 帶正則化的聯邦學習
3. FedAdam/FedAdagrad/FedYogi - 自適應優化器
4. QFedAvg - 公平聯邦平均
5. 自定義聚合策略
"""

import flwr as fl
from flwr.server.strategy import (
    Strategy,
    FedAvg,
    FedProx,
    FedAdam,
    FedAdagrad,
    FedYogi,
    QFedAvg
)
from flwr.common import (
    Parameters,
    Scalar,
    FitRes,
    EvaluateRes,
    FitIns,
    EvaluateIns,
    parameters_to_ndarrays,
    ndarrays_to_parameters
)
from flwr.server.client_proxy import ClientProxy
import numpy as np
from typing import Dict, List, Tuple, Optional, Union, Callable
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console = Console()


# ============================================================================
# 1. FedAvg - 聯邦平均（經典算法）
# ============================================================================

def demonstrate_fedavg():
    """
    FedAvg (Federated Averaging) 策略演示

    算法流程：
    1. 服務器將全局模型發送給選定的客戶端
    2. 客戶端使用本地數據訓練模型
    3. 客戶端將更新後的模型發送回服務器
    4. 服務器對所有模型進行加權平均（權重 = 數據量）

    公式: w_global = Σ(n_i * w_i) / Σ(n_i)
    """
    console.print(Panel.fit(
        "[bold cyan]FedAvg - 聯邦平均算法[/bold cyan]",
        border_style="cyan"
    ))

    strategy = FedAvg(
        # === 客戶端選擇參數 ===
        fraction_fit=0.1,  # 每輪選擇 10% 客戶端訓練
        fraction_evaluate=0.1,  # 每輪選擇 10% 客戶端評估
        min_fit_clients=10,  # 最少訓練客戶端數
        min_evaluate_clients=5,  # 最少評估客戶端數
        min_available_clients=100,  # 最少可用客戶端數

        # === 初始化參數 ===
        initial_parameters=None,  # 如果為 None，從第一個客戶端獲取

        # === 配置函數 ===
        on_fit_config_fn=lambda rnd: {
            "learning_rate": 0.01,
            "local_epochs": 5,
        },

        # === 聚合函數 ===
        fit_metrics_aggregation_fn=weighted_average,
        evaluate_metrics_aggregation_fn=weighted_average,

        # === 其他選項 ===
        accept_failures=True,  # 接受部分客戶端失敗
    )

    console.print("[green]✓ FedAvg 策略配置[/green]")
    console.print("\n[yellow]優點:[/yellow]")
    console.print("  • 簡單高效，易於實現")
    console.print("  • 通信效率高")
    console.print("  • 理論基礎紮實")

    console.print("\n[yellow]缺點:[/yellow]")
    console.print("  • 對 Non-IID 數據表現不佳")
    console.print("  • 容易受到惡意客戶端影響")
    console.print("  • 不考慮客戶端計算能力差異")

    console.print("\n[yellow]適用場景:[/yellow]")
    console.print("  • 數據分佈相對均勻（IID）")
    console.print("  • 客戶端計算能力相似")
    console.print("  • 對通信效率要求高")

    return strategy


# ============================================================================
# 2. FedProx - 帶正則化的聯邦學習
# ============================================================================

def demonstrate_fedprox():
    """
    FedProx 策略演示

    改進點：
    - 添加近端項（proximal term）來限制本地更新偏離全局模型太遠
    - 更適合處理系統異構性和數據異構性

    損失函數: L_local + (μ/2) * ||w - w_global||²
    """
    console.print(Panel.fit(
        "[bold cyan]FedProx - 近端聯邦學習[/bold cyan]",
        border_style="cyan"
    ))

    strategy = FedProx(
        # 繼承 FedAvg 的參數
        fraction_fit=0.1,
        min_fit_clients=10,
        min_available_clients=100,

        # === FedProx 特有參數 ===
        proximal_mu=0.01,  # 近端項係數（通常 0.001-0.1）

        on_fit_config_fn=lambda rnd: {
            "learning_rate": 0.01,
            "local_epochs": 5,
            "proximal_mu": 0.01,  # 傳遞給客戶端
        },
    )

    console.print("[green]✓ FedProx 策略配置[/green]")
    console.print(f"  近端係數 μ = 0.01")

    console.print("\n[yellow]優點:[/yellow]")
    console.print("  • 處理異構數據能力更強")
    console.print("  • 收斂更穩定")
    console.print("  • 容忍部分客戶端掉線")

    console.print("\n[yellow]缺點:[/yellow]")
    console.print("  • 需要調整 μ 參數")
    console.print("  • 計算開銷略高於 FedAvg")

    console.print("\n[yellow]適用場景:[/yellow]")
    console.print("  • Non-IID 數據分佈")
    console.print("  • 客戶端計算能力差異大")
    console.print("  • 部分客戶端可能掉線")

    return strategy


# ============================================================================
# 3. FedAdam - 自適應優化器
# ============================================================================

def demonstrate_fedadam():
    """
    FedAdam 策略演示

    使用 Adam 優化器進行服務器端聚合：
    - 一階矩估計（動量）
    - 二階矩估計（自適應學習率）
    - 更快的收斂速度
    """
    console.print(Panel.fit(
        "[bold cyan]FedAdam - 自適應聯邦學習[/bold cyan]",
        border_style="cyan"
    ))

    strategy = FedAdam(
        fraction_fit=0.1,
        min_fit_clients=10,
        min_available_clients=100,

        # === Adam 優化器參數 ===
        eta=1e-3,  # 服務器學習率
        eta_l=1e-1,  # 客戶端學習率
        beta_1=0.9,  # 一階矩估計的衰減率
        beta_2=0.99,  # 二階矩估計的衰減率
        tau=1e-9,  # 數值穩定性參數

        on_fit_config_fn=lambda rnd: {
            "learning_rate": 0.001,
            "local_epochs": 3,
        },
    )

    console.print("[green]✓ FedAdam 策略配置[/green]")
    console.print("  η (服務器學習率) = 1e-3")
    console.print("  β₁ (動量) = 0.9")
    console.print("  β₂ (RMSprop) = 0.99")

    console.print("\n[yellow]優點:[/yellow]")
    console.print("  • 收斂速度快")
    console.print("  • 自適應學習率")
    console.print("  • 適合複雜優化問題")

    console.print("\n[yellow]缺點:[/yellow]")
    console.print("  • 內存佔用較高（需存儲一階和二階矩）")
    console.print("  • 參數調優複雜")

    return strategy


# ============================================================================
# 4. QFedAvg - 公平聯邦平均
# ============================================================================

def demonstrate_qfedavg():
    """
    QFedAvg (q-Fair Federated Averaging) 策略演示

    目標：確保所有客戶端都能公平受益
    - 不只是優化全局性能
    - 考慮每個客戶端的性能
    - q 參數控制公平性程度
    """
    console.print(Panel.fit(
        "[bold cyan]QFedAvg - 公平聯邦平均[/bold cyan]",
        border_style="cyan"
    ))

    strategy = QFedAvg(
        fraction_fit=0.1,
        min_fit_clients=10,
        min_available_clients=100,

        # === QFedAvg 特有參數 ===
        q_param=0.2,  # 公平性參數（0 = FedAvg, >0 = 更公平）
        qffl_learning_rate=0.1,  # q-FFL 學習率

        on_fit_config_fn=lambda rnd: {
            "learning_rate": 0.01,
            "local_epochs": 5,
        },
    )

    console.print("[green]✓ QFedAvg 策略配置[/green]")
    console.print("  q = 0.2 (公平性參數)")

    console.print("\n[yellow]優點:[/yellow]")
    console.print("  • 保證所有客戶端公平受益")
    console.print("  • 避免性能差的客戶端被忽視")
    console.print("  • 提高邊緣設備性能")

    console.print("\n[yellow]缺點:[/yellow]")
    console.print("  • 全局性能可能稍差於 FedAvg")
    console.print("  • 計算開銷較大")

    console.print("\n[yellow]適用場景:[/yellow]")
    console.print("  • 需要確保公平性")
    console.print("  • 客戶端數據質量差異大")
    console.print("  • 每個客戶端性能都很重要")

    return strategy


# ============================================================================
# 5. 自定義聚合策略
# ============================================================================

class MedianAggregationStrategy(FedAvg):
    """
    中位數聚合策略

    使用中位數代替平均值，更魯棒地處理異常值和惡意客戶端。
    """

    def aggregate_fit(
        self,
        server_round: int,
        results: List[Tuple[ClientProxy, FitRes]],
        failures: List[Union[Tuple[ClientProxy, FitRes], BaseException]],
    ) -> Tuple[Optional[Parameters], Dict[str, Scalar]]:
        """使用中位數聚合客戶端參數"""

        if not results:
            return None, {}

        # 將參數轉換為 NumPy 數組
        weights_results = [
            (parameters_to_ndarrays(fit_res.parameters), fit_res.num_examples)
            for _, fit_res in results
        ]

        # 對每一層的參數計算中位數
        num_layers = len(weights_results[0][0])
        aggregated_weights = []

        for layer_idx in range(num_layers):
            # 收集所有客戶端的該層參數
            layer_weights = [weights[layer_idx] for weights, _ in weights_results]

            # 計算中位數
            median_weight = np.median(layer_weights, axis=0)
            aggregated_weights.append(median_weight)

        # 轉換回 Parameters
        parameters_aggregated = ndarrays_to_parameters(aggregated_weights)

        # 聚合指標
        metrics_aggregated = {}
        if results:
            metrics_aggregated = self._aggregate_metrics(results)

        console.print(f"[cyan]輪次 {server_round}: 使用中位數聚合[/cyan]")

        return parameters_aggregated, metrics_aggregated

    def _aggregate_metrics(
        self, results: List[Tuple[ClientProxy, FitRes]]
    ) -> Dict[str, Scalar]:
        """聚合訓練指標"""
        total_examples = sum([fit_res.num_examples for _, fit_res in results])

        aggregated = {}
        for _, fit_res in results:
            for key, value in fit_res.metrics.items():
                if key not in aggregated:
                    aggregated[key] = 0.0
                aggregated[key] += value * fit_res.num_examples

        for key in aggregated:
            aggregated[key] /= total_examples

        return aggregated


class RobustAggregationStrategy(FedAvg):
    """
    魯棒聚合策略

    特性：
    - 檢測和過濾異常更新
    - 使用修剪均值（trimmed mean）
    - 防禦拜占庭攻擊
    """

    def __init__(self, trim_ratio: float = 0.1, **kwargs):
        """
        Args:
            trim_ratio: 要修剪的客戶端比例（兩端各修剪）
        """
        super().__init__(**kwargs)
        self.trim_ratio = trim_ratio

    def aggregate_fit(
        self,
        server_round: int,
        results: List[Tuple[ClientProxy, FitRes]],
        failures: List[Union[Tuple[ClientProxy, FitRes], BaseException]],
    ) -> Tuple[Optional[Parameters], Dict[str, Scalar]]:
        """使用修剪均值聚合"""

        if not results:
            return None, {}

        # 轉換參數
        weights_results = [
            (parameters_to_ndarrays(fit_res.parameters), fit_res.num_examples)
            for _, fit_res in results
        ]

        num_clients = len(weights_results)
        num_trim = int(num_clients * self.trim_ratio)

        console.print(f"[yellow]修剪 {num_trim} 個客戶端（兩端各 {num_trim//2}）[/yellow]")

        # 計算每個客戶端的參數範數
        norms = []
        for weights, _ in weights_results:
            norm = sum([np.linalg.norm(w) for w in weights])
            norms.append(norm)

        # 排序並修剪
        sorted_indices = np.argsort(norms)
        # 移除最小和最大的
        keep_indices = sorted_indices[num_trim//2 : -num_trim//2 if num_trim > 0 else None]

        console.print(f"[green]保留 {len(keep_indices)} 個客戶端用於聚合[/green]")

        # 只使用保留的客戶端進行加權平均
        filtered_results = [
            (weights_results[i][0], weights_results[i][1])
            for i in keep_indices
        ]

        # 加權平均
        total_examples = sum([num_examples for _, num_examples in filtered_results])
        aggregated_weights = []

        num_layers = len(filtered_results[0][0])
        for layer_idx in range(num_layers):
            weighted_sum = sum([
                weights[layer_idx] * num_examples
                for weights, num_examples in filtered_results
            ])
            aggregated_weights.append(weighted_sum / total_examples)

        parameters_aggregated = ndarrays_to_parameters(aggregated_weights)

        # 聚合指標
        metrics_aggregated = {}

        return parameters_aggregated, metrics_aggregated


# ============================================================================
# 輔助函數
# ============================================================================

def weighted_average(metrics: List[Tuple[int, Dict[str, Scalar]]]) -> Dict[str, Scalar]:
    """
    加權平均聚合函數

    Args:
        metrics: [(樣本數, 指標字典), ...]

    Returns:
        聚合後的指標字典
    """
    total_examples = sum([num_examples for num_examples, _ in metrics])

    aggregated = {}
    if metrics:
        metric_keys = metrics[0][1].keys()
        for key in metric_keys:
            weighted_sum = sum([
                num_examples * m[key]
                for num_examples, m in metrics
                if key in m
            ])
            aggregated[key] = weighted_sum / total_examples

    return aggregated


def compare_strategies():
    """比較不同策略的特性"""
    console.print(Panel.fit(
        "[bold magenta]聚合策略對比[/bold magenta]",
        border_style="magenta"
    ))

    table = Table(show_header=True, header_style="bold blue")
    table.add_column("策略", style="cyan", width=15)
    table.add_column("收斂速度", justify="center", width=12)
    table.add_column("Non-IID 處理", justify="center", width=15)
    table.add_column("魯棒性", justify="center", width=12)
    table.add_column("計算開銷", justify="center", width=12)
    table.add_column("通信開銷", justify="center", width=12)

    table.add_row("FedAvg", "⭐⭐⭐", "⭐⭐", "⭐⭐", "⭐⭐⭐⭐⭐", "⭐⭐⭐⭐⭐")
    table.add_row("FedProx", "⭐⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐")
    table.add_row("FedAdam", "⭐⭐⭐⭐⭐", "⭐⭐⭐", "⭐⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐")
    table.add_row("QFedAvg", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐")
    table.add_row("Median", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐")
    table.add_row("Robust", "⭐⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐")

    console.print(table)


def main():
    """主函數"""
    console.print("\n[bold magenta]Flower 聯邦學習 - 聚合策略[/bold magenta]\n")

    # 演示各種策略
    strategies = []

    strategies.append(("FedAvg", demonstrate_fedavg()))
    console.print("\n" + "="*70 + "\n")

    strategies.append(("FedProx", demonstrate_fedprox()))
    console.print("\n" + "="*70 + "\n")

    strategies.append(("FedAdam", demonstrate_fedadam()))
    console.print("\n" + "="*70 + "\n")

    strategies.append(("QFedAvg", demonstrate_qfedavg()))
    console.print("\n" + "="*70 + "\n")

    # 自定義策略
    console.print(Panel.fit(
        "[bold cyan]自定義聚合策略[/bold cyan]",
        border_style="cyan"
    ))

    median_strategy = MedianAggregationStrategy(
        fraction_fit=0.1,
        min_fit_clients=10,
        min_available_clients=100,
    )
    console.print("[green]✓ 中位數聚合策略[/green]")
    console.print("  適用於：防禦惡意客戶端攻擊\n")

    robust_strategy = RobustAggregationStrategy(
        trim_ratio=0.1,
        fraction_fit=0.1,
        min_fit_clients=10,
        min_available_clients=100,
    )
    console.print("[green]✓ 魯棒聚合策略（修剪均值）[/green]")
    console.print("  適用於：拜占庭容錯場景")

    console.print("\n" + "="*70 + "\n")

    # 比較策略
    compare_strategies()

    console.print("\n[bold green]✓ 聚合策略示例完成！[/bold green]")
    console.print("\n[yellow]選擇策略的建議:[/yellow]")
    console.print("  1. IID 數據 → FedAvg")
    console.print("  2. Non-IID 數據 → FedProx")
    console.print("  3. 需要快速收斂 → FedAdam")
    console.print("  4. 需要公平性 → QFedAvg")
    console.print("  5. 有惡意客戶端 → Median/Robust")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]程序被用戶中斷[/yellow]")
    except Exception as e:
        logger.exception("程序執行出錯")
        console.print(f"[red]錯誤: {str(e)}[/red]")

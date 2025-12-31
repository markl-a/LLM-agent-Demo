"""
Flower 聯邦學習框架 - 服務端配置

這個示例展示如何配置 Flower 服務器：
1. 基本服務器配置
2. 聚合策略選擇
3. 客戶端選擇策略
4. 服務器回調函數
5. 自定義服務器邏輯
"""

import flwr as fl
from flwr.server.strategy import (
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
    parameters_to_ndarrays,
    ndarrays_to_parameters
)
from typing import Dict, List, Tuple, Optional, Union, Callable
import numpy as np
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console = Console()


# ============================================================================
# 1. 基本服務器配置
# ============================================================================

def basic_server_config():
    """
    基本服務器配置示例

    ServerConfig 控制聯邦學習的基本參數
    """
    console.print(Panel.fit(
        "[bold cyan]基本服務器配置[/bold cyan]",
        border_style="cyan"
    ))

    # 創建服務器配置
    config = fl.server.ServerConfig(
        num_rounds=10,  # 訓練輪數
        round_timeout=None,  # 每輪超時時間（秒），None 表示不限制
    )

    console.print("[green]服務器配置:[/green]")
    console.print(f"  - 訓練輪數: {config.num_rounds}")
    console.print(f"  - 輪次超時: {config.round_timeout or '無限制'}")

    return config


# ============================================================================
# 2. 聚合策略配置
# ============================================================================

def fedavg_strategy():
    """
    FedAvg (聯邦平均) 策略

    最經典的聯邦學習算法，對所有客戶端的模型參數進行加權平均。
    權重通常是客戶端的數據量。
    """
    console.print("\n[bold]1. FedAvg (聯邦平均) 策略[/bold]")

    strategy = FedAvg(
        # 客戶端採樣配置
        fraction_fit=0.1,  # 每輪選擇 10% 的客戶端進行訓練
        fraction_evaluate=0.1,  # 每輪選擇 10% 的客戶端進行評估
        min_fit_clients=10,  # 每輪最少訓練客戶端數
        min_evaluate_clients=5,  # 每輪最少評估客戶端數
        min_available_clients=100,  # 開始訓練需要的最少可用客戶端數

        # 初始化參數
        initial_parameters=None,  # 初始模型參數（可選）

        # 配置函數
        on_fit_config_fn=fit_config,  # 訓練配置函數
        on_evaluate_config_fn=evaluate_config,  # 評估配置函數

        # 聚合函數
        fit_metrics_aggregation_fn=weighted_average_metrics,  # 訓練指標聚合
        evaluate_metrics_aggregation_fn=weighted_average_metrics,  # 評估指標聚合

        # 客戶端選擇
        accept_failures=True,  # 是否接受部分客戶端失敗
    )

    console.print("[green]✓ FedAvg 策略配置完成[/green]")
    console.print("  - 適用場景: 數據分佈相似的客戶端")
    console.print("  - 優點: 簡單、高效、易於理解")
    console.print("  - 缺點: 對異構數據表現欠佳")

    return strategy


def fedprox_strategy():
    """
    FedProx 策略

    在 FedAvg 基礎上添加正則化項，更適合處理異構數據和系統異構性。
    """
    console.print("\n[bold]2. FedProx 策略[/bold]")

    strategy = FedProx(
        fraction_fit=0.1,
        fraction_evaluate=0.1,
        min_fit_clients=10,
        min_evaluate_clients=5,
        min_available_clients=100,

        # FedProx 特有參數
        proximal_mu=0.01,  # 近端項係數，控制本地更新與全局模型的接近程度

        on_fit_config_fn=fit_config,
        on_evaluate_config_fn=evaluate_config,
        fit_metrics_aggregation_fn=weighted_average_metrics,
        evaluate_metrics_aggregation_fn=weighted_average_metrics,
    )

    console.print("[green]✓ FedProx 策略配置完成[/green]")
    console.print("  - 適用場景: 異構數據、不同設備計算能力差異大")
    console.print("  - 優點: 提高收斂穩定性")
    console.print(f"  - 正則化係數: {0.01}")

    return strategy


def fedadam_strategy():
    """
    FedAdam 策略

    使用 Adam 優化器進行服務器端聚合。
    """
    console.print("\n[bold]3. FedAdam 策略[/bold]")

    strategy = FedAdam(
        fraction_fit=0.1,
        fraction_evaluate=0.1,
        min_fit_clients=10,
        min_evaluate_clients=5,
        min_available_clients=100,

        # Adam 優化器參數
        eta=1e-3,  # 學習率
        eta_l=1e-1,  # 本地學習率
        beta_1=0.9,  # 一階矩估計的指數衰減率
        beta_2=0.99,  # 二階矩估計的指數衰減率
        tau=1e-9,  # 數值穩定性參數

        on_fit_config_fn=fit_config,
        on_evaluate_config_fn=evaluate_config,
    )

    console.print("[green]✓ FedAdam 策略配置完成[/green]")
    console.print("  - 適用場景: 需要自適應學習率的場景")
    console.print("  - 優點: 收斂速度快")

    return strategy


def qfedavg_strategy():
    """
    QFedAvg (公平聯邦平均) 策略

    考慮公平性的聚合策略，確保所有客戶端都能受益。
    """
    console.print("\n[bold]4. QFedAvg (公平聯邦平均) 策略[/bold]")

    strategy = QFedAvg(
        fraction_fit=0.1,
        fraction_evaluate=0.1,
        min_fit_clients=10,
        min_evaluate_clients=5,
        min_available_clients=100,

        # QFedAvg 特有參數
        q_param=0.2,  # 公平性參數，越大越公平
        qffl_learning_rate=0.1,  # 學習率

        on_fit_config_fn=fit_config,
        on_evaluate_config_fn=evaluate_config,
    )

    console.print("[green]✓ QFedAvg 策略配置完成[/green]")
    console.print("  - 適用場景: 需要確保公平性的場景")
    console.print("  - 優點: 避免某些客戶端被忽視")

    return strategy


# ============================================================================
# 3. 配置函數
# ============================================================================

def fit_config(server_round: int) -> Dict[str, Scalar]:
    """
    訓練配置函數

    為每個訓練輪次動態生成配置。

    Args:
        server_round: 當前訓練輪次

    Returns:
        配置字典
    """
    config = {
        "server_round": server_round,
        "local_epochs": 5 if server_round < 5 else 3,  # 前幾輪多訓練
        "batch_size": 32,
        "learning_rate": 0.001 * (0.95 ** server_round),  # 學習率衰減
    }

    logger.info(f"輪次 {server_round} 訓練配置: {config}")
    return config


def evaluate_config(server_round: int) -> Dict[str, Scalar]:
    """
    評估配置函數

    Args:
        server_round: 當前訓練輪次

    Returns:
        配置字典
    """
    config = {
        "server_round": server_round,
        "batch_size": 64,  # 評估時可以用更大的 batch size
    }

    return config


def weighted_average_metrics(metrics: List[Tuple[int, Dict[str, Scalar]]]) -> Dict[str, Scalar]:
    """
    加權平均聚合指標

    Args:
        metrics: [(樣本數, 指標字典), ...] 列表

    Returns:
        聚合後的指標字典
    """
    # 計算總樣本數
    total_examples = sum([num_examples for num_examples, _ in metrics])

    # 加權平均每個指標
    aggregated_metrics = {}

    # 獲取所有指標的鍵
    if metrics:
        metric_keys = metrics[0][1].keys()

        for key in metric_keys:
            weighted_sum = sum([
                num_examples * m[key]
                for num_examples, m in metrics
                if key in m
            ])
            aggregated_metrics[key] = weighted_sum / total_examples

    return aggregated_metrics


# ============================================================================
# 4. 自定義策略
# ============================================================================

class CustomStrategy(FedAvg):
    """
    自定義聚合策略

    擴展 FedAvg，添加自定義邏輯。
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.round_losses = []
        console.print("[green]✓ 自定義策略初始化[/green]")

    def aggregate_fit(
        self,
        server_round: int,
        results: List[Tuple[fl.server.client_proxy.ClientProxy, FitRes]],
        failures: List[Union[Tuple[fl.server.client_proxy.ClientProxy, FitRes], BaseException]],
    ) -> Tuple[Optional[Parameters], Dict[str, Scalar]]:
        """
        自定義訓練結果聚合

        Args:
            server_round: 當前輪次
            results: 成功的客戶端結果
            failures: 失敗的客戶端

        Returns:
            聚合後的參數和指標
        """
        console.print(f"\n[bold cyan]輪次 {server_round} - 聚合訓練結果[/bold cyan]")
        console.print(f"  - 成功客戶端: {len(results)}")
        console.print(f"  - 失敗客戶端: {len(failures)}")

        # 處理失敗的客戶端
        if failures:
            logger.warning(f"輪次 {server_round} 有 {len(failures)} 個客戶端失敗")

        # 調用父類的聚合方法
        parameters, metrics = super().aggregate_fit(server_round, results, failures)

        # 自定義邏輯：記錄損失
        if "train_loss" in metrics:
            self.round_losses.append(metrics["train_loss"])
            console.print(f"  - 平均訓練損失: {metrics['train_loss']:.4f}")

        # 自定義邏輯：早停檢查
        if len(self.round_losses) >= 3:
            recent_losses = self.round_losses[-3:]
            if all(recent_losses[i] >= recent_losses[i-1] for i in range(1, len(recent_losses))):
                logger.warning("檢測到損失持續上升，可能需要調整學習率")

        return parameters, metrics

    def aggregate_evaluate(
        self,
        server_round: int,
        results: List[Tuple[fl.server.client_proxy.ClientProxy, EvaluateRes]],
        failures: List[Union[Tuple[fl.server.client_proxy.ClientProxy, EvaluateRes], BaseException]],
    ) -> Tuple[Optional[float], Dict[str, Scalar]]:
        """
        自定義評估結果聚合

        Args:
            server_round: 當前輪次
            results: 成功的客戶端結果
            failures: 失敗的客戶端

        Returns:
            聚合後的損失和指標
        """
        console.print(f"\n[bold cyan]輪次 {server_round} - 聚合評估結果[/bold cyan]")

        # 調用父類的聚合方法
        loss, metrics = super().aggregate_evaluate(server_round, results, failures)

        if metrics and "accuracy" in metrics:
            console.print(f"  - 全局準確率: {metrics['accuracy']:.4f}")

        return loss, metrics


# ============================================================================
# 5. 服務器回調
# ============================================================================

def get_on_fit_config(
    learning_rate_schedule: Dict[int, float]
) -> Callable[[int], Dict[str, Scalar]]:
    """
    創建帶學習率調度的訓練配置函數

    Args:
        learning_rate_schedule: {輪次: 學習率} 字典

    Returns:
        配置函數
    """
    def fit_config_fn(server_round: int) -> Dict[str, Scalar]:
        # 根據輪次選擇學習率
        lr = learning_rate_schedule.get(server_round, 0.001)

        config = {
            "server_round": server_round,
            "local_epochs": 5,
            "batch_size": 32,
            "learning_rate": lr,
        }

        console.print(f"[yellow]輪次 {server_round} 學習率: {lr}[/yellow]")
        return config

    return fit_config_fn


# ============================================================================
# 演示和測試
# ============================================================================

def compare_strategies():
    """比較不同的聚合策略"""
    console.print(Panel.fit(
        "[bold magenta]聯邦學習策略比較[/bold magenta]",
        border_style="magenta"
    ))

    # 創建比較表格
    table = Table(title="策略對比", show_header=True, header_style="bold blue")
    table.add_column("策略", style="cyan", width=15)
    table.add_column("適用場景", style="white", width=30)
    table.add_column("優點", style="green", width=25)
    table.add_column("缺點", style="red", width=20)

    table.add_row(
        "FedAvg",
        "數據分佈相似",
        "簡單、高效、易實現",
        "對異構數據效果差"
    )
    table.add_row(
        "FedProx",
        "異構數據、設備差異大",
        "收斂穩定、魯棒性強",
        "需要調整正則化參數"
    )
    table.add_row(
        "FedAdam",
        "需要自適應學習率",
        "收斂快、性能好",
        "內存佔用稍高"
    )
    table.add_row(
        "QFedAvg",
        "公平性要求高",
        "確保所有客戶端受益",
        "計算開銷較大"
    )

    console.print(table)


def demonstrate_server_config():
    """演示服務器配置"""
    console.print(Panel.fit(
        "[bold cyan]服務器配置演示[/bold cyan]",
        border_style="cyan"
    ))

    # 1. 基本配置
    server_config = basic_server_config()

    # 2. 策略配置
    console.print("\n[bold yellow]聚合策略配置:[/bold yellow]")
    strategies = {
        "FedAvg": fedavg_strategy(),
        "FedProx": fedprox_strategy(),
        "FedAdam": fedadam_strategy(),
        "QFedAvg": qfedavg_strategy(),
    }

    # 3. 自定義策略
    console.print("\n[bold]5. 自定義策略[/bold]")
    custom_strategy = CustomStrategy(
        fraction_fit=0.1,
        min_fit_clients=5,
        min_available_clients=10,
        on_fit_config_fn=fit_config,
        fit_metrics_aggregation_fn=weighted_average_metrics,
    )

    # 4. 學習率調度
    console.print("\n[bold yellow]學習率調度示例:[/bold yellow]")
    lr_schedule = {
        1: 0.01,
        2: 0.01,
        3: 0.005,
        4: 0.005,
        5: 0.001,
    }
    scheduled_config_fn = get_on_fit_config(lr_schedule)

    console.print("[green]✓ 學習率調度配置完成[/green]")
    for round_num, lr in lr_schedule.items():
        console.print(f"  輪次 {round_num}: 學習率 = {lr}")


def main():
    """主函數"""
    console.print("\n[bold magenta]Flower 服務端配置示例[/bold magenta]\n")

    # 演示服務器配置
    demonstrate_server_config()

    # 比較策略
    console.print("\n")
    compare_strategies()

    console.print("\n[bold green]✓ 服務端配置示例完成！[/bold green]")
    console.print("\n[yellow]關鍵要點:[/yellow]")
    console.print("  1. ServerConfig - 控制訓練輪數等基本參數")
    console.print("  2. Strategy - 選擇合適的聚合策略")
    console.print("  3. 配置函數 - 動態調整訓練參數")
    console.print("  4. 自定義策略 - 實現特殊業務邏輯")
    console.print("  5. 客戶端選擇 - 控制每輪參與的客戶端數量")

    console.print("\n[cyan]推薦閱讀:[/cyan]")
    console.print("  - 04_模型訓練.py - 完整的訓練流程")
    console.print("  - 05_聚合策略.py - 深入理解各種策略")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]程序被用戶中斷[/yellow]")
    except Exception as e:
        logger.exception("程序執行出錯")
        console.print(f"[red]錯誤: {str(e)}[/red]")

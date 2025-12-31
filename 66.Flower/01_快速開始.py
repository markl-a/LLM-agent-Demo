"""
Flower 聯邦學習框架 - 快速開始

這個示例展示 Flower 的基本概念和簡單的聯邦學習流程。

核心概念：
1. 客戶端（Client）- 持有數據並執行本地訓練
2. 服務器（Server）- 協調訓練並聚合模型更新
3. 策略（Strategy）- 定義如何聚合客戶端更新
4. 聯邦學習流程 - 分發→訓練→聚合→重複
"""

import flwr as fl
import numpy as np
from typing import Dict, List, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console = Console()


class SimpleFlowerClient(fl.client.NumPyClient):
    """
    簡單的 Flower 客戶端實現

    這個客戶端模擬一個基本的機器學習訓練流程：
    - get_parameters: 獲取模型參數
    - fit: 本地訓練
    - evaluate: 模型評估
    """

    def __init__(self, client_id: int):
        """
        初始化客戶端

        Args:
            client_id: 客戶端唯一標識符
        """
        self.client_id = client_id
        # 模擬模型參數（簡單的權重向量）
        self.parameters = np.random.randn(10).astype(np.float32)
        # 模擬本地數據集大小
        self.num_examples = np.random.randint(100, 1000)

        console.print(f"[green]✓ 客戶端 {client_id} 初始化完成[/green]")
        console.print(f"  - 數據集大小: {self.num_examples} 樣本")

    def get_parameters(self, config: Dict[str, str]) -> np.ndarray:
        """
        獲取當前模型參數

        Args:
            config: 配置字典（來自服務器）

        Returns:
            模型參數數組
        """
        logger.info(f"客戶端 {self.client_id}: 獲取模型參數")
        return self.parameters

    def fit(
        self,
        parameters: np.ndarray,
        config: Dict[str, str]
    ) -> Tuple[np.ndarray, int, Dict]:
        """
        使用本地數據訓練模型

        Args:
            parameters: 全局模型參數
            config: 訓練配置

        Returns:
            - 更新後的參數
            - 訓練樣本數量
            - 訓練指標字典
        """
        logger.info(f"客戶端 {self.client_id}: 開始本地訓練")

        # 接收全局模型參數
        self.parameters = parameters

        # 模擬本地訓練（實際應用中這裡是真實的訓練邏輯）
        # 這裡只是簡單地添加一些隨機噪聲來模擬梯度更新
        gradient = np.random.randn(*self.parameters.shape) * 0.01
        self.parameters = self.parameters - gradient

        # 模擬訓練損失
        loss = np.random.uniform(0.1, 0.5)

        console.print(f"[blue]客戶端 {self.client_id} 訓練完成[/blue]")
        console.print(f"  - 訓練樣本: {self.num_examples}")
        console.print(f"  - 訓練損失: {loss:.4f}")

        # 返回更新後的參數、樣本數量和指標
        return self.parameters, self.num_examples, {"loss": loss}

    def evaluate(
        self,
        parameters: np.ndarray,
        config: Dict[str, str]
    ) -> Tuple[float, int, Dict]:
        """
        評估模型性能

        Args:
            parameters: 要評估的模型參數
            config: 評估配置

        Returns:
            - 損失值
            - 評估樣本數量
            - 評估指標字典
        """
        logger.info(f"客戶端 {self.client_id}: 開始模型評估")

        self.parameters = parameters

        # 模擬評估（實際應用中這裡是真實的評估邏輯）
        loss = np.random.uniform(0.1, 0.4)
        accuracy = np.random.uniform(0.7, 0.95)

        console.print(f"[cyan]客戶端 {self.client_id} 評估完成[/cyan]")
        console.print(f"  - 評估樣本: {self.num_examples}")
        console.print(f"  - 損失: {loss:.4f}")
        console.print(f"  - 準確率: {accuracy:.4f}")

        return loss, self.num_examples, {"accuracy": accuracy}


def client_fn(cid: str) -> fl.client.Client:
    """
    客戶端工廠函數

    這個函數用於創建客戶端實例，Flower 會為每個客戶端調用此函數。

    Args:
        cid: 客戶端 ID（字符串）

    Returns:
        客戶端實例
    """
    return SimpleFlowerClient(int(cid)).to_client()


def weighted_average(metrics: List[Tuple[int, Dict]]) -> Dict:
    """
    加權平均聚合函數

    用於聚合多個客戶端的評估指標。

    Args:
        metrics: [(樣本數, 指標字典), ...] 列表

    Returns:
        聚合後的指標字典
    """
    # 計算總樣本數
    total_examples = sum([num_examples for num_examples, _ in metrics])

    # 加權平均損失
    weighted_loss = sum([num_examples * m["accuracy"] for num_examples, m in metrics])
    avg_accuracy = weighted_loss / total_examples

    return {"accuracy": avg_accuracy}


def start_simulation():
    """
    啟動聯邦學習模擬

    這個函數使用 Flower 的模擬模式，在單機上模擬多個客戶端。
    適合用於快速原型開發和測試。
    """
    console.print(Panel.fit(
        "[bold cyan]Flower 聯邦學習模擬啟動[/bold cyan]",
        border_style="cyan"
    ))

    try:
        # 定義聯邦學習策略
        strategy = fl.server.strategy.FedAvg(
            # 客戶端選擇參數
            fraction_fit=0.5,  # 每輪選擇 50% 的客戶端進行訓練
            fraction_evaluate=0.5,  # 每輪選擇 50% 的客戶端進行評估
            min_fit_clients=2,  # 每輪至少 2 個客戶端訓練
            min_evaluate_clients=2,  # 每輪至少 2 個客戶端評估
            min_available_clients=3,  # 至少需要 3 個客戶端可用
            # 評估指標聚合函數
            evaluate_metrics_aggregation_fn=weighted_average,
        )

        console.print("[yellow]策略配置:[/yellow]")
        console.print(f"  - 算法: FedAvg (聯邦平均)")
        console.print(f"  - 每輪訓練客戶端比例: 50%")
        console.print(f"  - 每輪評估客戶端比例: 50%")
        console.print(f"  - 最少客戶端數: 3")

        # 啟動模擬
        console.print("\n[bold green]開始聯邦學習模擬...[/bold green]\n")

        history = fl.simulation.start_simulation(
            client_fn=client_fn,  # 客戶端工廠函數
            num_clients=5,  # 總客戶端數量
            config=fl.server.ServerConfig(num_rounds=3),  # 訓練輪數
            strategy=strategy,  # 聚合策略
        )

        # 顯示訓練結果
        display_results(history)

    except Exception as e:
        logger.error(f"模擬過程出錯: {str(e)}")
        console.print(f"[red]✗ 錯誤: {str(e)}[/red]")
        raise


def display_results(history):
    """
    顯示訓練結果

    Args:
        history: Flower 訓練歷史對象
    """
    console.print("\n" + "="*60)
    console.print(Panel.fit(
        "[bold green]聯邦學習訓練完成！[/bold green]",
        border_style="green"
    ))

    # 創建結果表格
    table = Table(title="訓練歷史", show_header=True, header_style="bold magenta")
    table.add_column("輪次", style="cyan", justify="center")
    table.add_column("損失", style="yellow", justify="right")
    table.add_column("準確率", style="green", justify="right")

    # 填充表格數據
    if hasattr(history, 'losses_distributed') and history.losses_distributed:
        for round_num, (loss, _) in enumerate(history.losses_distributed, 1):
            accuracy = "N/A"
            if (hasattr(history, 'metrics_distributed') and
                history.metrics_distributed and
                round_num - 1 < len(history.metrics_distributed)):
                metrics = history.metrics_distributed[round_num - 1][1]
                if 'accuracy' in metrics:
                    accuracy = f"{metrics['accuracy']:.4f}"

            table.add_row(
                f"第 {round_num} 輪",
                f"{loss:.4f}",
                accuracy
            )

    console.print(table)

    # 顯示關鍵學習點
    console.print("\n[bold cyan]關鍵學習點:[/bold cyan]")
    console.print("1. [green]客戶端[/green]: 每個客戶端持有本地數據並執行訓練")
    console.print("2. [yellow]服務器[/yellow]: 協調訓練流程並聚合模型更新")
    console.print("3. [blue]隱私保護[/blue]: 原始數據永不離開客戶端")
    console.print("4. [magenta]聯邦平均[/magenta]: FedAvg 算法聚合所有客戶端的模型參數")


def demonstrate_concepts():
    """
    演示 Flower 核心概念
    """
    console.print(Panel.fit(
        "[bold]Flower 核心概念演示[/bold]",
        border_style="blue"
    ))

    concepts = Table(show_header=True, header_style="bold blue")
    concepts.add_column("概念", style="cyan", width=20)
    concepts.add_column("說明", style="white", width=50)

    concepts.add_row(
        "聯邦學習",
        "多個客戶端協同訓練模型，數據保留在本地"
    )
    concepts.add_row(
        "客戶端 (Client)",
        "持有私有數據，執行本地訓練和評估"
    )
    concepts.add_row(
        "服務器 (Server)",
        "協調訓練過程，聚合客戶端更新"
    )
    concepts.add_row(
        "策略 (Strategy)",
        "定義聚合算法（FedAvg、FedProx 等）"
    )
    concepts.add_row(
        "輪次 (Round)",
        "一次完整的訓練-聚合週期"
    )
    concepts.add_row(
        "隱私保護",
        "原始數據永不共享，只傳輸模型更新"
    )

    console.print(concepts)
    console.print()


def main():
    """
    主函數：演示 Flower 基本用法
    """
    console.print("\n[bold magenta]Flower 聯邦學習框架 - 快速開始[/bold magenta]\n")

    # 演示核心概念
    demonstrate_concepts()

    # 啟動模擬
    start_simulation()

    console.print("\n[bold green]✓ 快速開始示例完成！[/bold green]")
    console.print("\n[yellow]下一步:[/yellow]")
    console.print("  - 查看 02_客戶端定義.py 學習如何實現自定義客戶端")
    console.print("  - 查看 03_服務端配置.py 學習服務器配置選項")
    console.print("  - 查看 04_模型訓練.py 學習真實的模型訓練流程")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]程序被用戶中斷[/yellow]")
    except Exception as e:
        logger.exception("程序執行出錯")
        console.print(f"[red]錯誤: {str(e)}[/red]")

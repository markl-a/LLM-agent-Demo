"""
Flower 聯邦學習框架 - 生產部署

這個示例展示如何將 Flower 部署到生產環境：
1. Docker 容器化
2. 服務器-客戶端架構
3. gRPC 通信
4. 監控和日誌
5. 故障恢復
"""

import flwr as fl
from flwr.server.strategy import FedAvg
from flwr.common import Scalar
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
from typing import Dict, List, Tuple, Optional
from collections import OrderedDict
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import json
import time
from datetime import datetime
import os

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console = Console()


# ============================================================================
# 1. 配置管理
# ============================================================================

class ProductionConfig:
    """
    生產環境配置

    管理所有配置參數
    """

    def __init__(self, config_file: Optional[str] = None):
        """
        初始化配置

        Args:
            config_file: 配置文件路徑（JSON）
        """
        # 默認配置
        self.config = {
            # 服務器配置
            "server": {
                "host": "0.0.0.0",
                "port": 8080,
                "num_rounds": 10,
                "round_timeout": 600,  # 10 分鐘
            },

            # 客戶端配置
            "client": {
                "server_address": "localhost:8080",
                "local_epochs": 5,
                "batch_size": 32,
                "learning_rate": 0.001,
            },

            # 策略配置
            "strategy": {
                "name": "FedAvg",
                "fraction_fit": 0.1,
                "fraction_evaluate": 0.1,
                "min_fit_clients": 10,
                "min_evaluate_clients": 5,
                "min_available_clients": 100,
            },

            # 模型配置
            "model": {
                "name": "SimpleNet",
                "input_size": 784,
                "hidden_size": 128,
                "output_size": 10,
            },

            # 日誌配置
            "logging": {
                "level": "INFO",
                "log_dir": "./logs",
                "max_bytes": 10485760,  # 10 MB
                "backup_count": 5,
            },

            # 檢查點配置
            "checkpoint": {
                "enabled": True,
                "save_dir": "./checkpoints",
                "save_interval": 5,  # 每 5 輪保存一次
            },

            # 監控配置
            "monitoring": {
                "enabled": True,
                "metrics_dir": "./metrics",
            },
        }

        # 加載配置文件
        if config_file and Path(config_file).exists():
            self.load_from_file(config_file)

    def load_from_file(self, config_file: str):
        """從文件加載配置"""
        with open(config_file, 'r', encoding='utf-8') as f:
            user_config = json.load(f)
            self._update_config(self.config, user_config)

        console.print(f"[green]✓ 配置已從 {config_file} 加載[/green]")

    def _update_config(self, base: dict, update: dict):
        """遞歸更新配置"""
        for key, value in update.items():
            if isinstance(value, dict) and key in base:
                self._update_config(base[key], value)
            else:
                base[key] = value

    def save_to_file(self, config_file: str):
        """保存配置到文件"""
        Path(config_file).parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

        console.print(f"[green]✓ 配置已保存到 {config_file}[/green]")

    def get(self, *keys):
        """獲取配置值"""
        value = self.config
        for key in keys:
            value = value[key]
        return value


# ============================================================================
# 2. 日誌管理
# ============================================================================

class ProductionLogger:
    """
    生產環境日誌管理器

    特性：
    - 日誌輪轉
    - 多級別日誌
    - 結構化日誌
    """

    def __init__(self, config: ProductionConfig):
        """
        初始化日誌管理器

        Args:
            config: 配置對象
        """
        self.config = config

        # 創建日誌目錄
        log_dir = Path(config.get("logging", "log_dir"))
        log_dir.mkdir(parents=True, exist_ok=True)

        # 設置日誌級別
        level = getattr(logging, config.get("logging", "level"))

        # 創建日誌格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # 文件處理器（帶輪轉）
        file_handler = RotatingFileHandler(
            log_dir / "federated_learning.log",
            maxBytes=config.get("logging", "max_bytes"),
            backupCount=config.get("logging", "backup_count")
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)

        # 控制台處理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)

        # 配置根日誌記錄器
        root_logger = logging.getLogger()
        root_logger.setLevel(level)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)

        console.print(f"[green]✓ 日誌系統初始化完成[/green]")
        console.print(f"  - 日誌目錄: {log_dir}")
        console.print(f"  - 日誌級別: {config.get('logging', 'level')}")

    def log_metrics(self, round_num: int, metrics: Dict[str, float]):
        """記錄訓練指標"""
        logger.info(f"Round {round_num} Metrics: {json.dumps(metrics)}")


# ============================================================================
# 3. 檢查點管理
# ============================================================================

class CheckpointManager:
    """
    檢查點管理器

    自動保存和恢復模型檢查點
    """

    def __init__(self, config: ProductionConfig):
        """
        初始化檢查點管理器

        Args:
            config: 配置對象
        """
        self.config = config
        self.enabled = config.get("checkpoint", "enabled")

        if self.enabled:
            self.save_dir = Path(config.get("checkpoint", "save_dir"))
            self.save_dir.mkdir(parents=True, exist_ok=True)
            self.save_interval = config.get("checkpoint", "save_interval")

            console.print(f"[green]✓ 檢查點管理器初始化[/green]")
            console.print(f"  - 保存目錄: {self.save_dir}")
            console.print(f"  - 保存間隔: 每 {self.save_interval} 輪")

    def save_checkpoint(
        self,
        round_num: int,
        parameters: List[np.ndarray],
        metrics: Optional[Dict] = None
    ):
        """
        保存檢查點

        Args:
            round_num: 輪次編號
            parameters: 模型參數
            metrics: 評估指標
        """
        if not self.enabled:
            return

        if round_num % self.save_interval != 0:
            return

        checkpoint_path = self.save_dir / f"checkpoint_round_{round_num}.npz"

        # 保存參數
        np.savez(
            checkpoint_path,
            round=round_num,
            timestamp=time.time(),
            *parameters
        )

        # 保存指標
        if metrics:
            metrics_path = self.save_dir / f"metrics_round_{round_num}.json"
            with open(metrics_path, 'w') as f:
                json.dump(metrics, f, indent=2)

        console.print(f"[yellow]✓ 檢查點已保存: {checkpoint_path}[/yellow]")
        logger.info(f"Checkpoint saved at round {round_num}")

    def load_latest_checkpoint(self) -> Optional[Tuple[int, List[np.ndarray]]]:
        """
        加載最新的檢查點

        Returns:
            (輪次, 參數列表) 或 None
        """
        if not self.enabled:
            return None

        # 查找所有檢查點
        checkpoints = list(self.save_dir.glob("checkpoint_round_*.npz"))

        if not checkpoints:
            console.print("[yellow]沒有找到檢查點[/yellow]")
            return None

        # 找到最新的檢查點
        latest_checkpoint = max(checkpoints, key=lambda p: p.stat().st_mtime)

        # 加載
        data = np.load(latest_checkpoint)
        round_num = int(data['round'])

        # 提取參數
        parameters = []
        i = 0
        while f'arr_{i}' in data:
            if i > 0:  # 跳過 'round' 和 'timestamp'
                parameters.append(data[f'arr_{i}'])
            i += 1

        console.print(f"[green]✓ 已加載檢查點: {latest_checkpoint}[/green]")
        console.print(f"  - 輪次: {round_num}")

        return round_num, parameters


# ============================================================================
# 4. 監控系統
# ============================================================================

class MonitoringSystem:
    """
    監控系統

    記錄和可視化訓練指標
    """

    def __init__(self, config: ProductionConfig):
        """
        初始化監控系統

        Args:
            config: 配置對象
        """
        self.config = config
        self.enabled = config.get("monitoring", "enabled")

        if self.enabled:
            self.metrics_dir = Path(config.get("monitoring", "metrics_dir"))
            self.metrics_dir.mkdir(parents=True, exist_ok=True)

            self.metrics_history = {
                "rounds": [],
                "timestamps": [],
                "train_loss": [],
                "train_accuracy": [],
                "eval_loss": [],
                "eval_accuracy": [],
                "num_clients": [],
            }

            console.print(f"[green]✓ 監控系統初始化[/green]")
            console.print(f"  - 指標目錄: {self.metrics_dir}")

    def record_round(
        self,
        round_num: int,
        train_metrics: Optional[Dict] = None,
        eval_metrics: Optional[Dict] = None,
        num_clients: int = 0
    ):
        """
        記錄一輪的指標

        Args:
            round_num: 輪次編號
            train_metrics: 訓練指標
            eval_metrics: 評估指標
            num_clients: 參與客戶端數量
        """
        if not self.enabled:
            return

        self.metrics_history["rounds"].append(round_num)
        self.metrics_history["timestamps"].append(datetime.now().isoformat())
        self.metrics_history["num_clients"].append(num_clients)

        if train_metrics:
            self.metrics_history["train_loss"].append(train_metrics.get("loss", 0))
            self.metrics_history["train_accuracy"].append(train_metrics.get("accuracy", 0))

        if eval_metrics:
            self.metrics_history["eval_loss"].append(eval_metrics.get("loss", 0))
            self.metrics_history["eval_accuracy"].append(eval_metrics.get("accuracy", 0))

    def save_metrics(self):
        """保存指標到文件"""
        if not self.enabled:
            return

        metrics_file = self.metrics_dir / f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(metrics_file, 'w') as f:
            json.dump(self.metrics_history, f, indent=2)

        console.print(f"[green]✓ 指標已保存: {metrics_file}[/green]")

    def print_summary(self):
        """打印訓練總結"""
        console.print(Panel.fit(
            "[bold cyan]訓練總結[/bold cyan]",
            border_style="cyan"
        ))

        if not self.metrics_history["rounds"]:
            console.print("[yellow]沒有記錄[/yellow]")
            return

        table = Table(show_header=True, header_style="bold blue")
        table.add_column("指標", style="cyan")
        table.add_column("最終值", style="yellow", justify="right")
        table.add_column("最佳值", style="green", justify="right")

        # 訓練損失
        if self.metrics_history["train_loss"]:
            final_train_loss = self.metrics_history["train_loss"][-1]
            best_train_loss = min(self.metrics_history["train_loss"])
            table.add_row("訓練損失", f"{final_train_loss:.4f}", f"{best_train_loss:.4f}")

        # 訓練準確率
        if self.metrics_history["train_accuracy"]:
            final_train_acc = self.metrics_history["train_accuracy"][-1]
            best_train_acc = max(self.metrics_history["train_accuracy"])
            table.add_row("訓練準確率", f"{final_train_acc:.4f}", f"{best_train_acc:.4f}")

        # 評估損失
        if self.metrics_history["eval_loss"]:
            final_eval_loss = self.metrics_history["eval_loss"][-1]
            best_eval_loss = min(self.metrics_history["eval_loss"])
            table.add_row("評估損失", f"{final_eval_loss:.4f}", f"{best_eval_loss:.4f}")

        # 評估準確率
        if self.metrics_history["eval_accuracy"]:
            final_eval_acc = self.metrics_history["eval_accuracy"][-1]
            best_eval_acc = max(self.metrics_history["eval_accuracy"])
            table.add_row("評估準確率", f"{final_eval_acc:.4f}", f"{best_eval_acc:.4f}")

        console.print(table)


# ============================================================================
# 5. 生產服務器
# ============================================================================

class ProductionServer:
    """
    生產環境服務器

    整合所有生產功能
    """

    def __init__(self, config: ProductionConfig):
        """
        初始化生產服務器

        Args:
            config: 配置對象
        """
        self.config = config

        # 初始化組件
        self.logger = ProductionLogger(config)
        self.checkpoint_manager = CheckpointManager(config)
        self.monitoring = MonitoringSystem(config)

        console.print(Panel.fit(
            "[bold green]生產服務器初始化完成[/bold green]",
            border_style="green"
        ))

    def start(self):
        """啟動服務器"""
        console.print("\n[bold cyan]啟動聯邦學習服務器...[/bold cyan]")

        # 檢查是否有檢查點
        checkpoint = self.checkpoint_manager.load_latest_checkpoint()
        if checkpoint:
            start_round, initial_parameters = checkpoint
            console.print(f"[yellow]從輪次 {start_round} 恢復訓練[/yellow]")
        else:
            start_round = 0
            initial_parameters = None

        # 創建策略
        strategy = self._create_strategy(initial_parameters)

        # 服務器配置
        server_config = fl.server.ServerConfig(
            num_rounds=self.config.get("server", "num_rounds")
        )

        # 服務器地址
        server_address = f"{self.config.get('server', 'host')}:{self.config.get('server', 'port')}"

        console.print(f"[green]服務器地址: {server_address}[/green]")
        console.print(f"[green]訓練輪數: {server_config.num_rounds}[/green]")

        try:
            # 啟動服務器（實際生產環境中使用）
            # fl.server.start_server(
            #     server_address=server_address,
            #     config=server_config,
            #     strategy=strategy,
            # )

            # 模擬模式（用於演示）
            console.print("\n[yellow]使用模擬模式運行（演示用途）[/yellow]")
            self._run_simulation(strategy, server_config)

        except Exception as e:
            logger.exception("服務器運行出錯")
            console.print(f"[red]錯誤: {str(e)}[/red]")
        finally:
            # 保存最終狀態
            self.monitoring.save_metrics()
            self.monitoring.print_summary()

    def _create_strategy(self, initial_parameters):
        """創建聚合策略"""
        strategy = FedAvg(
            fraction_fit=self.config.get("strategy", "fraction_fit"),
            fraction_evaluate=self.config.get("strategy", "fraction_evaluate"),
            min_fit_clients=self.config.get("strategy", "min_fit_clients"),
            min_evaluate_clients=self.config.get("strategy", "min_evaluate_clients"),
            min_available_clients=self.config.get("strategy", "min_available_clients"),
            initial_parameters=initial_parameters,
        )

        return strategy

    def _run_simulation(self, strategy, server_config):
        """運行模擬（用於演示）"""
        console.print("[yellow]模擬聯邦學習過程...[/yellow]\n")

        for round_num in range(1, server_config.num_rounds + 1):
            console.print(f"[bold blue]輪次 {round_num}[/bold blue]")

            # 模擬訓練
            train_metrics = {
                "loss": np.random.uniform(0.3, 0.7),
                "accuracy": np.random.uniform(0.7, 0.95)
            }

            # 模擬評估
            eval_metrics = {
                "loss": np.random.uniform(0.3, 0.7),
                "accuracy": np.random.uniform(0.7, 0.95)
            }

            # 記錄指標
            self.monitoring.record_round(
                round_num,
                train_metrics=train_metrics,
                eval_metrics=eval_metrics,
                num_clients=10
            )

            # 保存檢查點
            dummy_params = [np.random.randn(10, 10)]
            self.checkpoint_manager.save_checkpoint(
                round_num,
                dummy_params,
                eval_metrics
            )

            console.print(f"  訓練損失: {train_metrics['loss']:.4f}")
            console.print(f"  評估準確率: {eval_metrics['accuracy']:.4f}\n")

            time.sleep(0.5)  # 模擬訓練時間


# ============================================================================
# 6. Docker 部署指南
# ============================================================================

def generate_dockerfile():
    """生成 Dockerfile"""
    dockerfile_content = """# Flower 聯邦學習服務器 Dockerfile

FROM python:3.9-slim

# 設置工作目錄
WORKDIR /app

# 安裝依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用代碼
COPY . .

# 暴露端口
EXPOSE 8080

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD python -c "import socket; s=socket.socket(); s.connect(('localhost', 8080)); s.close()"

# 啟動服務器
CMD ["python", "server.py"]
"""

    console.print(Panel.fit(
        "[bold cyan]Docker 部署配置[/bold cyan]",
        border_style="cyan"
    ))

    console.print("\n[bold yellow]Dockerfile:[/bold yellow]")
    console.print(dockerfile_content)

    console.print("\n[bold yellow]Docker Compose 配置:[/bold yellow]")

    compose_content = """version: '3.8'

services:
  # 聯邦學習服務器
  fl-server:
    build: .
    ports:
      - "8080:8080"
    volumes:
      - ./logs:/app/logs
      - ./checkpoints:/app/checkpoints
      - ./metrics:/app/metrics
    environment:
      - FL_SERVER_HOST=0.0.0.0
      - FL_SERVER_PORT=8080
    restart: unless-stopped

  # 客戶端（可選，用於測試）
  fl-client:
    build: .
    command: python client.py
    environment:
      - FL_SERVER_ADDRESS=fl-server:8080
    depends_on:
      - fl-server
    deploy:
      replicas: 5
"""

    console.print(compose_content)

    console.print("\n[bold yellow]部署命令:[/bold yellow]")
    console.print("  1. 構建鏡像: docker-compose build")
    console.print("  2. 啟動服務: docker-compose up -d")
    console.print("  3. 查看日誌: docker-compose logs -f")
    console.print("  4. 停止服務: docker-compose down")


# ============================================================================
# 主函數
# ============================================================================

def main():
    """主函數"""
    console.print("\n[bold magenta]Flower 聯邦學習 - 生產部署[/bold magenta]\n")

    # 1. 創建配置
    console.print("[bold]1. 配置管理[/bold]")
    config = ProductionConfig()

    # 保存配置示例
    config_file = Path("./config_example.json")
    config.save_to_file(str(config_file))

    console.print("\n" + "="*70 + "\n")

    # 2. 啟動生產服務器
    console.print("[bold]2. 生產服務器[/bold]")
    server = ProductionServer(config)
    server.start()

    console.print("\n" + "="*70 + "\n")

    # 3. Docker 部署指南
    console.print("[bold]3. Docker 部署[/bold]")
    generate_dockerfile()

    console.print("\n[bold green]✓ 生產部署示例完成！[/bold green]")
    console.print("\n[yellow]關鍵要點:[/yellow]")
    console.print("  1. 配置管理 - 使用配置文件管理參數")
    console.print("  2. 日誌系統 - 結構化日誌和日誌輪轉")
    console.print("  3. 檢查點 - 自動保存和恢復訓練狀態")
    console.print("  4. 監控 - 記錄和可視化訓練指標")
    console.print("  5. Docker - 容器化部署")

    console.print("\n[cyan]生產部署清單:[/cyan]")
    console.print("  ✓ 配置管理系統")
    console.print("  ✓ 完善的日誌記錄")
    console.print("  ✓ 檢查點和恢復機制")
    console.print("  ✓ 性能監控和告警")
    console.print("  ✓ Docker 容器化")
    console.print("  ✓ 健康檢查")
    console.print("  ✓ 錯誤處理和重試")
    console.print("  ✓ 資源管理")

    console.print("\n[cyan]下一步:[/cyan]")
    console.print("  • 設置 CI/CD 管道")
    console.print("  • 配置負載均衡")
    console.print("  • 實施安全加固")
    console.print("  • 部署到 Kubernetes")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]程序被用戶中斷[/yellow]")
    except Exception as e:
        logger.exception("程序執行出錯")
        console.print(f"[red]錯誤: {str(e)}[/red]")

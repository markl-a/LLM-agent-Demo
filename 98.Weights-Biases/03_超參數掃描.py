"""
Weights & Biases 超參數掃描示例

這個示例展示了如何使用 W&B Sweeps 進行自動化超參數優化。
包含多種搜索策略、早停機制和最佳配置選擇。

主要功能：
1. 網格搜索 (Grid Search)
2. 隨機搜索 (Random Search)
3. 貝葉斯優化 (Bayesian Optimization)
4. 早停機制
5. 並行掃描
6. 自定義目標函數
7. 超參數重要性分析
8. 最佳配置提取

作者: W&B Team
日期: 2025-01-01
"""

import wandb
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from typing import Dict, Any
import random


# ============================================================================
# 第一部分：訓練函數
# ============================================================================

def train_model(config: Dict[str, Any] = None):
    """
    訓練模型函數

    這個函數會被 W&B sweep 調用，使用不同的超參數配置。

    Args:
        config: 超參數配置字典
    """
    # 初始化 wandb
    with wandb.init(config=config) as run:
        # 獲取配置
        config = wandb.config

        print(f"\n🚀 開始訓練，配置: {dict(config)}")

        # 創建簡單模型
        model = nn.Sequential(
            nn.Linear(10, config.hidden_size),
            nn.ReLU(),
            nn.Dropout(config.dropout),
            nn.Linear(config.hidden_size, config.hidden_size // 2),
            nn.ReLU(),
            nn.Linear(config.hidden_size // 2, 1)
        )

        # 選擇優化器
        if config.optimizer == "adam":
            optimizer = optim.Adam(
                model.parameters(),
                lr=config.learning_rate,
                weight_decay=config.weight_decay
            )
        elif config.optimizer == "sgd":
            optimizer = optim.SGD(
                model.parameters(),
                lr=config.learning_rate,
                momentum=config.momentum,
                weight_decay=config.weight_decay
            )
        else:
            optimizer = optim.RMSprop(
                model.parameters(),
                lr=config.learning_rate,
                weight_decay=config.weight_decay
            )

        criterion = nn.MSELoss()

        # 創建虛擬數據
        X_train = torch.randn(1000, 10)
        y_train = torch.randn(1000, 1)
        X_val = torch.randn(200, 10)
        y_val = torch.randn(200, 1)

        # 訓練循環
        best_val_loss = float('inf')

        for epoch in range(config.epochs):
            # 訓練
            model.train()
            optimizer.zero_grad()
            train_pred = model(X_train)
            train_loss = criterion(train_pred, y_train)
            train_loss.backward()
            optimizer.step()

            # 驗證
            model.eval()
            with torch.no_grad():
                val_pred = model(X_val)
                val_loss = criterion(val_pred, y_val)

            # 記錄指標
            wandb.log({
                "epoch": epoch,
                "train_loss": train_loss.item(),
                "val_loss": val_loss.item()
            })

            # 更新最佳驗證損失
            if val_loss.item() < best_val_loss:
                best_val_loss = val_loss.item()

            print(f"  Epoch {epoch+1}/{config.epochs} - "
                  f"train_loss: {train_loss.item():.4f}, "
                  f"val_loss: {val_loss.item():.4f}")

        # 記錄最終指標
        wandb.log({"best_val_loss": best_val_loss})

        print(f"✅ 訓練完成，最佳驗證損失: {best_val_loss:.4f}")


# ============================================================================
# 第二部分：網格搜索
# ============================================================================

def grid_search_sweep():
    """
    網格搜索示例

    遍歷所有超參數組合。
    """
    print("\n" + "="*60)
    print("網格搜索 (Grid Search)")
    print("="*60)

    # 定義掃描配置
    sweep_config = {
        "name": "grid-search-demo",
        "method": "grid",  # 網格搜索
        "metric": {
            "name": "val_loss",
            "goal": "minimize"
        },
        "parameters": {
            "learning_rate": {
                "values": [0.001, 0.01, 0.1]
            },
            "hidden_size": {
                "values": [32, 64, 128]
            },
            "dropout": {
                "values": [0.1, 0.3, 0.5]
            },
            "optimizer": {
                "values": ["adam", "sgd"]
            },
            # 固定參數
            "epochs": {"value": 10},
            "batch_size": {"value": 32},
            "weight_decay": {"value": 1e-4},
            "momentum": {"value": 0.9}
        }
    }

    print(f"📋 掃描配置:")
    print(f"   方法: {sweep_config['method']}")
    print(f"   目標: {sweep_config['metric']['goal']} {sweep_config['metric']['name']}")
    print(f"   總組合數: {3 * 3 * 3 * 2} = 54")

    # 初始化掃描
    sweep_id = wandb.sweep(
        sweep_config,
        project="hyperparameter-sweeps"
    )

    print(f"\n🔍 掃描 ID: {sweep_id}")
    print("💡 運行: wandb agent <sweep_id> 開始掃描")

    # 運行掃描 (這裡只運行少量以演示)
    print("\n🏃 開始運行掃描 (演示用，僅運行 3 次)...")
    wandb.agent(sweep_id, function=train_model, count=3)

    print("\n✅ 網格搜索完成")


# ============================================================================
# 第三部分：隨機搜索
# ============================================================================

def random_search_sweep():
    """
    隨機搜索示例

    隨機採樣超參數組合。
    """
    print("\n" + "="*60)
    print("隨機搜索 (Random Search)")
    print("="*60)

    sweep_config = {
        "name": "random-search-demo",
        "method": "random",  # 隨機搜索
        "metric": {
            "name": "best_val_loss",
            "goal": "minimize"
        },
        "parameters": {
            "learning_rate": {
                # 對數均勻分佈
                "distribution": "log_uniform_values",
                "min": 0.0001,
                "max": 0.1
            },
            "hidden_size": {
                # 整數均勻分佈
                "distribution": "int_uniform",
                "min": 16,
                "max": 256
            },
            "dropout": {
                # 均勻分佈
                "distribution": "uniform",
                "min": 0.0,
                "max": 0.5
            },
            "optimizer": {
                "values": ["adam", "sgd", "rmsprop"]
            },
            "weight_decay": {
                "distribution": "log_uniform_values",
                "min": 1e-6,
                "max": 1e-2
            },
            "epochs": {"value": 15},
            "batch_size": {"value": 32},
            "momentum": {"value": 0.9}
        }
    }

    print(f"📋 掃描配置:")
    print(f"   方法: {sweep_config['method']}")
    print(f"   learning_rate: log_uniform [{sweep_config['parameters']['learning_rate']['min']}, "
          f"{sweep_config['parameters']['learning_rate']['max']}]")
    print(f"   hidden_size: int_uniform [{sweep_config['parameters']['hidden_size']['min']}, "
          f"{sweep_config['parameters']['hidden_size']['max']}]")

    # 初始化掃描
    sweep_id = wandb.sweep(
        sweep_config,
        project="hyperparameter-sweeps"
    )

    print(f"\n🔍 掃描 ID: {sweep_id}")

    # 運行掃描
    print("\n🏃 開始運行隨機搜索 (演示用，僅運行 5 次)...")
    wandb.agent(sweep_id, function=train_model, count=5)

    print("\n✅ 隨機搜索完成")


# ============================================================================
# 第四部分：貝葉斯優化
# ============================================================================

def bayesian_optimization_sweep():
    """
    貝葉斯優化示例

    使用貝葉斯優化智能搜索最佳超參數。
    """
    print("\n" + "="*60)
    print("貝葉斯優化 (Bayesian Optimization)")
    print("="*60)

    sweep_config = {
        "name": "bayesian-optimization-demo",
        "method": "bayes",  # 貝葉斯優化
        "metric": {
            "name": "best_val_loss",
            "goal": "minimize"
        },
        "parameters": {
            "learning_rate": {
                "min": 0.0001,
                "max": 0.1
            },
            "hidden_size": {
                "min": 16,
                "max": 256
            },
            "dropout": {
                "min": 0.0,
                "max": 0.5
            },
            "optimizer": {
                "values": ["adam", "sgd"]
            },
            "weight_decay": {
                "min": 1e-6,
                "max": 1e-2
            },
            "epochs": {"value": 15},
            "batch_size": {"value": 32},
            "momentum": {"value": 0.9}
        },
        # 早停配置
        "early_terminate": {
            "type": "hyperband",
            "min_iter": 3,
            "eta": 2,
            "s": 3
        }
    }

    print(f"📋 掃描配置:")
    print(f"   方法: {sweep_config['method']}")
    print(f"   早停: {sweep_config['early_terminate']['type']}")

    # 初始化掃描
    sweep_id = wandb.sweep(
        sweep_config,
        project="hyperparameter-sweeps"
    )

    print(f"\n🔍 掃描 ID: {sweep_id}")

    # 運行掃描
    print("\n🏃 開始運行貝葉斯優化 (演示用，僅運行 5 次)...")
    wandb.agent(sweep_id, function=train_model, count=5)

    print("\n✅ 貝葉斯優化完成")


# ============================================================================
# 第五部分：帶早停的掃描
# ============================================================================

def sweep_with_early_stopping():
    """
    帶早停的掃描示例

    使用 Hyperband 算法提前終止表現不佳的運行。
    """
    print("\n" + "="*60)
    print("帶早停的掃描")
    print("="*60)

    sweep_config = {
        "name": "early-stopping-demo",
        "method": "random",
        "metric": {
            "name": "val_loss",
            "goal": "minimize"
        },
        "parameters": {
            "learning_rate": {
                "distribution": "log_uniform_values",
                "min": 0.0001,
                "max": 0.1
            },
            "hidden_size": {
                "values": [32, 64, 128, 256]
            },
            "dropout": {
                "distribution": "uniform",
                "min": 0.0,
                "max": 0.5
            },
            "optimizer": {
                "values": ["adam", "sgd"]
            },
            "epochs": {"value": 20},
            "batch_size": {"value": 32},
            "weight_decay": {"value": 1e-4},
            "momentum": {"value": 0.9}
        },
        # Hyperband 早停
        "early_terminate": {
            "type": "hyperband",
            "min_iter": 5,  # 最小迭代次數
            "eta": 3,  # 淘汰率
            "s": 2  # 預算倍數
        }
    }

    print(f"📋 早停配置:")
    print(f"   類型: Hyperband")
    print(f"   最小迭代: {sweep_config['early_terminate']['min_iter']}")
    print(f"   淘汰率: {sweep_config['early_terminate']['eta']}")

    sweep_id = wandb.sweep(
        sweep_config,
        project="hyperparameter-sweeps"
    )

    print(f"\n🔍 掃描 ID: {sweep_id}")
    print("\n🏃 開始運行掃描...")
    wandb.agent(sweep_id, function=train_model, count=5)

    print("\n✅ 帶早停的掃描完成")


# ============================================================================
# 第六部分：自定義訓練函數
# ============================================================================

def custom_training_function():
    """
    自定義訓練函數示例

    展示更複雜的訓練邏輯和自定義指標。
    """

    def train_with_custom_metrics(config=None):
        """帶自定義指標的訓練函數"""
        with wandb.init(config=config) as run:
            config = wandb.config

            # 模擬訓練
            for epoch in range(config.epochs):
                # 計算多個指標
                train_loss = 1.0 / (epoch + 1) * (1.0 / config.learning_rate)
                val_loss = train_loss * 1.1
                custom_metric = train_loss * config.hidden_size / 100

                # 記錄所有指標
                wandb.log({
                    "epoch": epoch,
                    "train_loss": train_loss,
                    "val_loss": val_loss,
                    "custom_metric": custom_metric,
                    "learning_rate": config.learning_rate,
                    "hidden_size": config.hidden_size
                })

            # 記錄組合指標
            final_score = val_loss * (1 + config.dropout)
            wandb.log({"final_score": final_score})

    print("\n" + "="*60)
    print("自定義訓練函數")
    print("="*60)

    sweep_config = {
        "name": "custom-metrics-sweep",
        "method": "bayes",
        "metric": {
            "name": "final_score",
            "goal": "minimize"
        },
        "parameters": {
            "learning_rate": {"min": 0.001, "max": 0.1},
            "hidden_size": {"values": [32, 64, 128]},
            "dropout": {"min": 0.0, "max": 0.5},
            "epochs": {"value": 10}
        }
    }

    sweep_id = wandb.sweep(
        sweep_config,
        project="hyperparameter-sweeps"
    )

    print(f"\n🔍 掃描 ID: {sweep_id}")
    print("\n🏃 運行自定義訓練...")
    wandb.agent(sweep_id, function=train_with_custom_metrics, count=3)

    print("\n✅ 自定義訓練完成")


# ============================================================================
# 第七部分：並行掃描
# ============================================================================

def parallel_sweep_example():
    """
    並行掃描示例

    展示如何配置並行運行的掃描。
    """
    print("\n" + "="*60)
    print("並行掃描配置")
    print("="*60)

    sweep_config = {
        "name": "parallel-sweep-demo",
        "method": "random",
        "metric": {
            "name": "best_val_loss",
            "goal": "minimize"
        },
        "parameters": {
            "learning_rate": {
                "distribution": "log_uniform_values",
                "min": 0.0001,
                "max": 0.1
            },
            "hidden_size": {
                "values": [32, 64, 128, 256]
            },
            "dropout": {"min": 0.0, "max": 0.5},
            "optimizer": {"values": ["adam", "sgd"]},
            "epochs": {"value": 10},
            "batch_size": {"value": 32},
            "weight_decay": {"value": 1e-4},
            "momentum": {"value": 0.9}
        }
    }

    sweep_id = wandb.sweep(
        sweep_config,
        project="hyperparameter-sweeps"
    )

    print(f"\n🔍 掃描 ID: {sweep_id}")
    print("\n💡 並行運行掃描:")
    print("   在多個終端中運行:")
    print(f"   $ wandb agent {sweep_id}")
    print("\n   或使用多進程:")
    print(f"   $ for i in {{1..4}}; do wandb agent {sweep_id} & done")

    # 演示單線程運行
    print("\n🏃 單線程演示運行...")
    wandb.agent(sweep_id, function=train_model, count=3)

    print("\n✅ 並行掃描配置完成")


# ============================================================================
# 第八部分：分析掃描結果
# ============================================================================

def analyze_sweep_results(sweep_id: str):
    """
    分析掃描結果

    提取最佳配置和超參數重要性。

    Args:
        sweep_id: 掃描 ID
    """
    print("\n" + "="*60)
    print("分析掃描結果")
    print("="*60)

    api = wandb.Api()

    # 獲取掃描
    sweep = api.sweep(f"your-entity/hyperparameter-sweeps/{sweep_id}")

    print(f"\n📊 掃描信息:")
    print(f"   名稱: {sweep.config.get('name', 'N/A')}")
    print(f"   方法: {sweep.config.get('method', 'N/A')}")

    # 獲取所有運行
    runs = sweep.runs

    print(f"   總運行數: {len(runs)}")

    # 找到最佳運行
    best_run = min(runs, key=lambda run: run.summary.get("best_val_loss", float('inf')))

    print(f"\n🏆 最佳運行:")
    print(f"   ID: {best_run.id}")
    print(f"   名稱: {best_run.name}")
    print(f"   驗證損失: {best_run.summary.get('best_val_loss', 'N/A'):.4f}")

    print(f"\n⚙️  最佳配置:")
    for key, value in best_run.config.items():
        print(f"   {key}: {value}")

    print("\n💡 使用最佳配置重新訓練你的模型！")


# ============================================================================
# 主程序
# ============================================================================

def main():
    """
    主函數：運行所有示例
    """
    print("\n" + "="*70)
    print("Weights & Biases 超參數掃描示例")
    print("="*70)

    try:
        # 1. 網格搜索
        grid_search_sweep()

        # 2. 隨機搜索
        random_search_sweep()

        # 3. 貝葉斯優化
        bayesian_optimization_sweep()

        # 4. 早停掃描
        sweep_with_early_stopping()

        # 5. 自定義訓練函數
        custom_training_function()

        # 6. 並行掃描
        parallel_sweep_example()

        # 注意: 分析掃描結果需要實際的 sweep_id
        # analyze_sweep_results("your-sweep-id")

        print("\n" + "="*70)
        print("✅ 所有超參數掃描示例完成！")
        print("="*70)
        print("\n💡 提示:")
        print("   - 訪問 W&B 儀表板查看掃描結果")
        print("   - 使用並行 agents 加速搜索")
        print("   - 分析超參數重要性")
        print("   - 使用最佳配置進行最終訓練")

    except Exception as e:
        print(f"\n❌ 運行示例時出錯: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

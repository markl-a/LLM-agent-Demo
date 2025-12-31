"""
Axolotl 全量微調示例

本示例展示：
1. 全量微調配置
2. 與 LoRA/QLoRA 的對比
3. 資源需求評估
4. 訓練策略
"""

import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def explain_full_finetuning():
    """解釋全量微調"""
    console.print("\n[cyan]什麼是全量微調？[/cyan]\n")
    console.print("全量微調（Full Fine-tuning）訓練模型的所有參數：\n")
    console.print("  [green]優點:[/green]")
    console.print("    - 最佳的模型性能")
    console.print("    - 完全適應新任務")
    console.print("    - 不受適配器限制")
    console.print("\n  [yellow]缺點:[/yellow]")
    console.print("    - 需要大量 GPU 內存")
    console.print("    - 訓練時間長")
    console.print("    - 需要更多數據")
    console.print("    - 容易過擬合\n")


def create_full_finetuning_config():
    """創建全量微調配置"""
    console.print("[cyan]創建全量微調配置...[/cyan]")

    config = {
        # 基礎模型
        "base_model": "meta-llama/Llama-2-7b-hf",
        "model_type": "LlamaForCausalLM",
        "tokenizer_type": "LlamaTokenizer",
        "trust_remote_code": True,

        # 不使用適配器（全量微調）
        "adapter": None,

        # 數據配置
        "datasets": [
            {
                "path": "data/train.jsonl",
                "type": "alpaca",
            }
        ],
        "sequence_len": 2048,
        "val_set_size": 0.1,

        # 訓練參數
        "batch_size": 4,
        "micro_batch_size": 1,
        "gradient_accumulation_steps": 4,
        "num_epochs": 3,

        # 優化器
        "optimizer": "adamw_torch",
        "learning_rate": 0.00005,  # 全量微調使用較小的學習率
        "lr_scheduler": "cosine",
        "warmup_steps": 100,
        "weight_decay": 0.01,

        # 精度設置
        "bf16": True,
        "fp16": False,
        "tf32": True,

        # 內存優化（必需）
        "gradient_checkpointing": True,
        "flash_attention": True,

        # DeepSpeed 配置（推薦用於大模型）
        "deepspeed": "deepspeed_configs/zero2.json",

        # 輸出設置
        "output_dir": "./full_finetuning_output",
        "logging_steps": 10,
        "save_steps": 500,
        "eval_steps": 250,
        "save_total_limit": 2,

        # 正則化
        "max_grad_norm": 1.0,

        # 實驗追蹤
        "wandb_project": "axolotl-full-ft",
        "wandb_run_id": "full_ft_7b",
    }

    config_path = "full_finetuning_config.yml"
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, sort_keys=False)

    console.print(f"[green]✓ 全量微調配置已保存: {config_path}[/green]\n")
    return config_path


def compare_methods():
    """比較不同微調方法"""
    console.print("[cyan]微調方法對比:[/cyan]\n")

    comparison = [
        ("訓練參數", "100%", "0.1-1%", "0.1-1%"),
        ("7B 內存需求", "~80 GB", "~22 GB", "~6 GB"),
        ("訓練速度", "慢", "快", "中等"),
        ("模型效果", "最佳", "優秀", "優秀"),
        ("過擬合風險", "高", "低", "低"),
        ("所需數據量", "大", "中", "中"),
        ("推理速度", "快", "稍慢", "稍慢"),
        ("部署大小", "14 GB", "14GB + 40MB", "14GB + 40MB"),
    ]

    table = Table(title="全量微調 vs LoRA vs QLoRA")
    table.add_column("指標", style="cyan")
    table.add_column("全量微調", style="yellow")
    table.add_column("LoRA", style="green")
    table.add_column("QLoRA", style="magenta")

    for row in comparison:
        table.add_row(*row)

    console.print(table)
    console.print()


def show_resource_requirements():
    """顯示資源需求"""
    console.print("[cyan]不同模型的資源需求（全量微調）:[/cyan]\n")

    requirements = [
        ("LLaMA-7B", "80 GB", "1x A100 80GB", "12-24 小時"),
        ("LLaMA-13B", "150 GB", "2x A100 80GB", "24-48 小時"),
        ("LLaMA-30B", "300 GB", "4-8x A100 80GB", "3-7 天"),
        ("LLaMA-65B", "600 GB", "8-16x A100 80GB", "7-14 天"),
    ]

    table = Table(title="資源需求估算")
    table.add_column("模型", style="cyan")
    table.add_column("內存需求", style="yellow")
    table.add_column("推薦配置", style="green")
    table.add_column("訓練時間", style="magenta")

    for req in requirements:
        table.add_row(*req)

    console.print(table)
    console.print("\n[yellow]注意：時間估算基於 10K 訓練樣本，3 個 epoch[/yellow]\n")


def show_when_to_use():
    """顯示何時使用全量微調"""
    console.print("[cyan]何時使用全量微調？[/cyan]\n")

    scenarios = [
        ("✓ 有充足的計算資源（多 GPU 集群）", "green"),
        ("✓ 有大量高質量訓練數據（>10K 樣本）", "green"),
        ("✓ 需要最佳的模型性能", "green"),
        ("✓ 任務與預訓練差異大", "green"),
        ("✗ 資源有限（單 GPU 或小內存）", "red"),
        ("✗ 數據量少（<1K 樣本）", "red"),
        ("✗ 快速實驗和迭代", "red"),
        ("✗ 需要多個任務適配器", "red"),
    ]

    for scenario, color in scenarios:
        console.print(f"  [{color}]{scenario}[/{color}]")
    console.print()


def show_training_strategies():
    """顯示訓練策略"""
    console.print("[cyan]全量微調訓練策略:[/cyan]\n")

    strategies = [
        "1. 使用較小的學習率（5e-5 到 1e-4）",
        "2. 充足的 warmup（總步數的 5-10%）",
        "3. 使用權重衰減（weight_decay=0.01）",
        "4. 啟用梯度裁剪（max_grad_norm=1.0）",
        "5. 監控驗證損失，及早停止",
        "6. 使用餘弦學習率調度",
        "7. 定期保存檢查點",
        "8. 使用 DeepSpeed ZeRO 優化內存",
    ]

    for strategy in strategies:
        console.print(f"  {strategy}")
    console.print()


def create_deepspeed_config():
    """創建 DeepSpeed 配置"""
    console.print("[cyan]創建 DeepSpeed ZeRO-2 配置...[/cyan]")

    import os
    os.makedirs("deepspeed_configs", exist_ok=True)

    deepspeed_config = {
        "fp16": {
            "enabled": False
        },
        "bf16": {
            "enabled": True
        },
        "zero_optimization": {
            "stage": 2,
            "offload_optimizer": {
                "device": "cpu",
                "pin_memory": True
            },
            "allgather_partitions": True,
            "allgather_bucket_size": 2e8,
            "overlap_comm": True,
            "reduce_scatter": True,
            "reduce_bucket_size": 2e8,
            "contiguous_gradients": True
        },
        "gradient_accumulation_steps": 4,
        "gradient_clipping": 1.0,
        "steps_per_print": 10,
        "train_batch_size": "auto",
        "train_micro_batch_size_per_gpu": "auto",
        "wall_clock_breakdown": False
    }

    config_path = "deepspeed_configs/zero2.json"
    import json
    with open(config_path, 'w') as f:
        json.dump(deepspeed_config, f, indent=2)

    console.print(f"[green]✓ DeepSpeed 配置已保存: {config_path}[/green]\n")
    return config_path


def show_training_command():
    """顯示訓練命令"""
    console.print("[cyan]全量微調訓練命令:[/cyan]\n")

    commands = [
        ("單 GPU (80GB+)", "accelerate launch -m axolotl.cli.train full_finetuning_config.yml"),
        ("多 GPU + DeepSpeed", "deepspeed --num_gpus=4 -m axolotl.cli.train full_finetuning_config.yml"),
        ("使用 FSDP", "accelerate launch --config_file fsdp_config.yaml -m axolotl.cli.train full_finetuning_config.yml"),
    ]

    for name, cmd in commands:
        console.print(f"[yellow]{name}:[/yellow]")
        console.print(f"  {cmd}")
        console.print()


def show_best_practices():
    """顯示最佳實踐"""
    console.print("[cyan]全量微調最佳實踐:[/cyan]\n")

    practices = [
        "數據準備：",
        "  - 至少 10K 高質量樣本",
        "  - 數據清洗和去重",
        "  - 驗證集佔比 10-15%",
        "",
        "訓練監控：",
        "  - 使用 Weights & Biases 或 TensorBoard",
        "  - 監控訓練/驗證損失",
        "  - 定期檢查生成質量",
        "",
        "內存優化：",
        "  - 使用 DeepSpeed ZeRO-2/3",
        "  - 啟用梯度檢查點",
        "  - 使用 Flash Attention",
        "  - 考慮激活值檢查點",
        "",
        "防止過擬合：",
        "  - 使用權重衰減",
        "  - Early stopping",
        "  - Dropout（如適用）",
        "  - 數據增強",
    ]

    for practice in practices:
        console.print(f"  {practice}")
    console.print()


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Axolotl 全量微調示例[/bold cyan]",
        border_style="cyan"
    ))

    # 1. 解釋全量微調
    explain_full_finetuning()

    # 2. 創建配置
    create_full_finetuning_config()
    create_deepspeed_config()

    # 3. 方法對比
    compare_methods()

    # 4. 資源需求
    show_resource_requirements()

    # 5. 使用場景
    show_when_to_use()

    # 6. 訓練策略
    show_training_strategies()

    # 7. 訓練命令
    show_training_command()

    # 8. 最佳實踐
    show_best_practices()

    # 完成
    console.print("="*60)
    console.print("[bold green]✓ 全量微調示例完成！[/bold green]")
    console.print("\n[cyan]建議:[/cyan]")
    console.print("  對於大多數應用，LoRA 或 QLoRA 已經足夠")
    console.print("  只在有充足資源和明確需求時使用全量微調")


if __name__ == "__main__":
    main()

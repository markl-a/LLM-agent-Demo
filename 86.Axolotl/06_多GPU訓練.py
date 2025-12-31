"""
Axolotl 多 GPU 訓練示例

本示例展示：
1. 分散式訓練配置（DDP、FSDP）
2. DeepSpeed 整合
3. 多 GPU 訓練策略
4. 性能優化
"""

import yaml
import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def explain_distributed_training():
    """解釋分散式訓練方法"""
    console.print("\n[cyan]分散式訓練方法:[/cyan]\n")

    methods = {
        "DDP (DistributedDataParallel)": {
            "描述": "每個 GPU 都有完整模型副本",
            "優點": "簡單、穩定、通信開銷小",
            "缺點": "每個 GPU 需要完整模型內存",
            "適用": "小模型（7B 以下）",
        },
        "FSDP (Fully Sharded Data Parallel)": {
            "描述": "分片模型參數、梯度和優化器狀態",
            "優點": "內存效率高、可訓練大模型",
            "缺點": "通信開銷大、實現複雜",
            "適用": "大模型（13B 以上）",
        },
        "DeepSpeed ZeRO": {
            "描述": "分階段的內存優化策略",
            "優點": "靈活、功能豐富、生態完善",
            "缺點": "需要額外配置",
            "適用": "各種規模模型",
        },
    }

    for method, info in methods.items():
        console.print(f"[yellow]{method}:[/yellow]")
        for key, value in info.items():
            console.print(f"  {key}: {value}")
        console.print()


def create_ddp_config():
    """創建 DDP 配置"""
    console.print("[cyan]創建 DDP (分散式數據並行) 配置...[/cyan]")

    config = {
        "base_model": "meta-llama/Llama-2-7b-hf",
        "model_type": "LlamaForCausalLM",

        # LoRA 配置
        "adapter": "lora",
        "lora_r": 16,
        "lora_alpha": 32,
        "lora_dropout": 0.05,
        "lora_target_modules": ["q_proj", "v_proj", "k_proj", "o_proj"],

        # 數據
        "datasets": [{"path": "data/train.jsonl", "type": "alpaca"}],
        "sequence_len": 2048,

        # 訓練參數（會自動分配到多 GPU）
        "batch_size": 32,  # 總批次大小
        "micro_batch_size": 4,  # 每個 GPU 的批次
        "num_epochs": 3,

        # 優化器
        "optimizer": "adamw_torch",
        "learning_rate": 0.0002,

        # 精度
        "bf16": True,
        "gradient_checkpointing": True,

        # 輸出
        "output_dir": "./ddp_output",
        "logging_steps": 10,
        "save_steps": 100,
    }

    config_path = "ddp_config.yml"
    with open(config_path, 'w') as f:
        yaml.dump(config, f, sort_keys=False)

    console.print(f"[green]✓ DDP 配置已保存: {config_path}[/green]\n")
    return config_path


def create_fsdp_config():
    """創建 FSDP 配置"""
    console.print("[cyan]創建 FSDP 配置...[/cyan]")

    # Accelerate FSDP 配置文件
    fsdp_config = {
        "compute_environment": "LOCAL_MACHINE",
        "distributed_type": "FSDP",
        "fsdp_config": {
            "fsdp_auto_wrap_policy": "TRANSFORMER_BASED_WRAP",
            "fsdp_backward_prefetch_policy": "BACKWARD_PRE",
            "fsdp_forward_prefetch": True,
            "fsdp_offload_params": False,
            "fsdp_sharding_strategy": "FULL_SHARD",
            "fsdp_state_dict_type": "SHARDED_STATE_DICT",
            "fsdp_sync_module_states": True,
            "fsdp_use_orig_params": True,
        },
        "machine_rank": 0,
        "main_training_function": "main",
        "mixed_precision": "bf16",
        "num_machines": 1,
        "num_processes": 4,
        "use_cpu": False,
    }

    config_path = "fsdp_config.yaml"
    with open(config_path, 'w') as f:
        yaml.dump(fsdp_config, f, sort_keys=False)

    console.print(f"[green]✓ FSDP 配置已保存: {config_path}[/green]\n")
    return config_path


def create_deepspeed_configs():
    """創建 DeepSpeed 配置"""
    console.print("[cyan]創建 DeepSpeed 配置（ZeRO-1/2/3）...[/cyan]")

    Path("deepspeed_configs").mkdir(exist_ok=True)

    # ZeRO Stage 1: 優化器狀態分片
    zero1_config = {
        "bf16": {"enabled": True},
        "zero_optimization": {
            "stage": 1,
        },
        "gradient_accumulation_steps": "auto",
        "train_batch_size": "auto",
        "train_micro_batch_size_per_gpu": "auto",
    }

    # ZeRO Stage 2: 優化器 + 梯度分片
    zero2_config = {
        "bf16": {"enabled": True},
        "zero_optimization": {
            "stage": 2,
            "offload_optimizer": {"device": "cpu", "pin_memory": True},
            "allgather_partitions": True,
            "allgather_bucket_size": 2e8,
            "reduce_scatter": True,
            "reduce_bucket_size": 2e8,
            "overlap_comm": True,
            "contiguous_gradients": True,
        },
        "gradient_accumulation_steps": "auto",
        "train_batch_size": "auto",
        "train_micro_batch_size_per_gpu": "auto",
    }

    # ZeRO Stage 3: 優化器 + 梯度 + 參數分片
    zero3_config = {
        "bf16": {"enabled": True},
        "zero_optimization": {
            "stage": 3,
            "offload_optimizer": {"device": "cpu", "pin_memory": True},
            "offload_param": {"device": "cpu", "pin_memory": True},
            "overlap_comm": True,
            "contiguous_gradients": True,
            "sub_group_size": 1e9,
            "reduce_bucket_size": "auto",
            "stage3_prefetch_bucket_size": "auto",
            "stage3_param_persistence_threshold": "auto",
            "stage3_max_live_parameters": 1e9,
            "stage3_max_reuse_distance": 1e9,
            "stage3_gather_16bit_weights_on_model_save": True,
        },
        "gradient_accumulation_steps": "auto",
        "train_batch_size": "auto",
        "train_micro_batch_size_per_gpu": "auto",
    }

    configs = [
        ("zero1.json", zero1_config),
        ("zero2.json", zero2_config),
        ("zero3.json", zero3_config),
    ]

    for filename, config in configs:
        path = f"deepspeed_configs/{filename}"
        with open(path, 'w') as f:
            json.dump(config, f, indent=2)
        console.print(f"[green]✓ {path} 已創建[/green]")

    console.print()


def compare_methods():
    """比較不同方法"""
    console.print("[cyan]分散式訓練方法對比:[/cyan]\n")

    comparison = [
        ("內存效率", "低", "高", "最高"),
        ("通信開銷", "低", "中", "中"),
        ("訓練速度", "快", "中", "中"),
        ("配置複雜度", "簡單", "中等", "中等"),
        ("模型規模", "小", "大", "極大"),
        ("GPU 數量", "2-8", "4-16", "4-64"),
    ]

    table = Table(title="DDP vs FSDP vs DeepSpeed")
    table.add_column("指標", style="cyan")
    table.add_column("DDP", style="yellow")
    table.add_column("FSDP", style="green")
    table.add_column("DeepSpeed ZeRO-3", style="magenta")

    for row in comparison:
        table.add_row(*row)

    console.print(table)
    console.print()


def show_training_commands():
    """顯示訓練命令"""
    console.print("[cyan]多 GPU 訓練命令:[/cyan]\n")

    commands = {
        "DDP (2 GPUs)": "accelerate launch --multi_gpu --num_processes 2 -m axolotl.cli.train ddp_config.yml",

        "DDP (4 GPUs)": "accelerate launch --multi_gpu --num_processes 4 -m axolotl.cli.train ddp_config.yml",

        "FSDP (4 GPUs)": "accelerate launch --config_file fsdp_config.yaml -m axolotl.cli.train config.yml",

        "DeepSpeed ZeRO-2 (4 GPUs)": "deepspeed --num_gpus=4 -m axolotl.cli.train config.yml --deepspeed deepspeed_configs/zero2.json",

        "DeepSpeed ZeRO-3 (8 GPUs)": "deepspeed --num_gpus=8 -m axolotl.cli.train config.yml --deepspeed deepspeed_configs/zero3.json",
    }

    for name, cmd in commands.items():
        console.print(f"[yellow]{name}:[/yellow]")
        console.print(f"  {cmd}")
        console.print()


def show_performance_tips():
    """顯示性能優化技巧"""
    console.print("[cyan]多 GPU 訓練性能優化:[/cyan]\n")

    tips = [
        "1. 批次大小優化：",
        "   - 總批次 = micro_batch_size × num_gpus × gradient_accumulation_steps",
        "   - 確保每個 GPU 的批次大小充分利用 VRAM",
        "",
        "2. 通信優化：",
        "   - 使用高速互連（NVLink、InfiniBand）",
        "   - 啟用梯度壓縮（如適用）",
        "   - 優化 bucket_size 參數",
        "",
        "3. 內存優化：",
        "   - 根據模型大小選擇合適的分散式方法",
        "   - 使用 CPU offload（ZeRO-2/3）",
        "   - 啟用激活值檢查點",
        "",
        "4. 負載均衡：",
        "   - 確保數據均勻分配到各 GPU",
        "   - 避免某些 GPU 空閒",
        "   - 監控 GPU 利用率",
        "",
        "5. 檢查點策略：",
        "   - 只在主進程保存模型",
        "   - 使用分片檢查點（FSDP/ZeRO-3）",
        "   - 定期保存以便恢復",
    ]

    for tip in tips:
        console.print(f"  {tip}")
    console.print()


def show_troubleshooting():
    """顯示故障排除"""
    console.print("[cyan]常見問題和解決方案:[/cyan]\n")

    issues = [
        ("GPU 利用率不均", [
            "檢查數據分配是否均勻",
            "調整 batch size",
            "檢查是否有同步瓶頸",
        ]),
        ("訓練速度慢", [
            "檢查 GPU 間通信（使用 nvidia-smi topo -m）",
            "增大 batch size 減少通信頻率",
            "使用梯度累積",
            "檢查是否使用了 CPU offload",
        ]),
        ("OOM 錯誤", [
            "使用更激進的分片（FSDP 或 ZeRO-3）",
            "減小 micro_batch_size",
            "啟用 CPU offload",
            "使用梯度檢查點",
        ]),
        ("進程掛起", [
            "檢查所有 GPU 是否可見",
            "確認網絡配置正確",
            "檢查 NCCL 環境變量",
            "查看詳細日誌",
        ]),
    ]

    for issue, solutions in issues:
        console.print(f"[yellow]問題: {issue}[/yellow]")
        for solution in solutions:
            console.print(f"  - {solution}")
        console.print()


def show_monitoring():
    """顯示監控方法"""
    console.print("[cyan]監控多 GPU 訓練:[/cyan]\n")

    console.print("[yellow]1. GPU 監控:[/yellow]")
    console.print("  watch -n 1 nvidia-smi")
    console.print()

    console.print("[yellow]2. GPU 拓撲:[/yellow]")
    console.print("  nvidia-smi topo -m")
    console.print()

    console.print("[yellow]3. NCCL 調試:[/yellow]")
    console.print("  export NCCL_DEBUG=INFO")
    console.print("  export NCCL_DEBUG_SUBSYS=ALL")
    console.print()

    console.print("[yellow]4. 進程監控:[/yellow]")
    console.print("  使用 Weights & Biases 或 TensorBoard")
    console.print("  監控每個進程的 GPU 利用率和內存")
    console.print()


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Axolotl 多 GPU 訓練示例[/bold cyan]",
        border_style="cyan"
    ))

    # 1. 解釋分散式訓練
    explain_distributed_training()

    # 2. 創建配置
    create_ddp_config()
    create_fsdp_config()
    create_deepspeed_configs()

    # 3. 方法對比
    compare_methods()

    # 4. 訓練命令
    show_training_commands()

    # 5. 性能優化
    show_performance_tips()

    # 6. 監控
    show_monitoring()

    # 7. 故障排除
    show_troubleshooting()

    # 完成
    console.print("="*60)
    console.print("[bold green]✓ 多 GPU 訓練示例完成！[/bold green]")
    console.print("\n[cyan]選擇建議:[/cyan]")
    console.print("  - 7B 模型 + 2-4 GPU: 使用 DDP")
    console.print("  - 13B+ 模型 + 4-8 GPU: 使用 FSDP 或 DeepSpeed ZeRO-2")
    console.print("  - 30B+ 模型 + 8+ GPU: 使用 DeepSpeed ZeRO-3")


if __name__ == "__main__":
    main()

"""
Axolotl LoRA 微調示例

本示例展示：
1. LoRA 配置詳解
2. LoRA 訓練流程
3. 超參數調優
4. 訓練監控
"""

import yaml
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def explain_lora_params():
    """解釋 LoRA 參數"""
    console.print("\n[cyan]LoRA 參數詳解:[/cyan]\n")

    params = [
        ("lora_r", "LoRA 的秩（rank）", "8-64", "越大效果越好，但內存消耗越多"),
        ("lora_alpha", "LoRA 的縮放因子", "16-128", "通常設為 r 的 2 倍"),
        ("lora_dropout", "Dropout 率", "0.05-0.1", "防止過擬合"),
        ("lora_target_modules", "目標模塊", "q_proj, v_proj 等", "選擇要微調的注意力層"),
    ]

    table = Table(title="LoRA 參數")
    table.add_column("參數", style="cyan")
    table.add_column("說明", style="yellow")
    table.add_column("推薦值", style="green")
    table.add_column("備註", style="dim")

    for param in params:
        table.add_row(*param)

    console.print(table)
    console.print()


def create_lora_config(rank: int = 16, alpha: int = 32):
    """創建 LoRA 訓練配置"""
    console.print(f"[cyan]創建 LoRA 配置 (r={rank}, alpha={alpha})...[/cyan]")

    config = {
        # 基礎模型
        "base_model": "meta-llama/Llama-2-7b-hf",
        "model_type": "LlamaForCausalLM",
        "tokenizer_type": "LlamaTokenizer",

        # LoRA 配置
        "adapter": "lora",
        "lora_r": rank,
        "lora_alpha": alpha,
        "lora_dropout": 0.05,
        "lora_target_modules": [
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ],
        "lora_fan_in_fan_out": False,

        # 數據配置
        "datasets": [
            {
                "path": "data/train.jsonl",
                "type": "alpaca",
            }
        ],
        "dataset_prepared_path": "data/prepared",
        "val_set_size": 0.1,
        "sequence_len": 2048,

        # 訓練參數
        "batch_size": 8,
        "micro_batch_size": 2,
        "gradient_accumulation_steps": 4,
        "num_epochs": 3,

        # 優化器
        "optimizer": "adamw_torch",
        "learning_rate": 0.0002,
        "lr_scheduler": "cosine",
        "warmup_steps": 100,

        # 精度和內存優化
        "bf16": True,
        "fp16": False,
        "tf32": True,
        "gradient_checkpointing": True,
        "flash_attention": True,

        # 日誌和保存
        "logging_steps": 10,
        "save_steps": 100,
        "eval_steps": 50,
        "save_total_limit": 3,
        "output_dir": "./lora_output",

        # 評估
        "eval_table_size": 5,
        "evaluation_strategy": "steps",

        # Weights & Biases
        "wandb_project": "axolotl-lora",
        "wandb_run_id": f"lora_r{rank}_alpha{alpha}",
    }

    # 保存配置
    config_path = f"lora_r{rank}_config.yml"
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, sort_keys=False)

    console.print(f"[green]✓ LoRA 配置已保存: {config_path}[/green]\n")

    return config_path


def show_target_modules():
    """顯示不同模型的目標模塊"""
    console.print("[cyan]不同模型的 LoRA 目標模塊:[/cyan]\n")

    models = {
        "LLaMA/LLaMA-2": ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        "GPT-2/GPT-J": ["c_attn", "c_proj"],
        "BLOOM": ["query_key_value", "dense", "dense_h_to_4h", "dense_4h_to_h"],
        "Falcon": ["query_key_value", "dense", "dense_h_to_4h", "dense_4h_to_h"],
        "Mistral": ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    }

    for model, modules in models.items():
        console.print(f"[yellow]{model}:[/yellow]")
        console.print(f"  {', '.join(modules)}")
    console.print()


def compare_lora_configs():
    """比較不同的 LoRA 配置"""
    console.print("[cyan]LoRA 配置對比:[/cyan]\n")

    configs = [
        ("輕量級", 8, 16, "低內存，快速實驗"),
        ("標準", 16, 32, "平衡性能和資源"),
        ("高性能", 32, 64, "更好效果，更多資源"),
        ("極限", 64, 128, "最佳效果，高資源需求"),
    ]

    table = Table(title="LoRA 配置對比")
    table.add_column("配置名稱", style="cyan")
    table.add_column("Rank (r)", style="yellow")
    table.add_column("Alpha", style="green")
    table.add_column("適用場景", style="dim")

    for config in configs:
        table.add_row(config[0], str(config[1]), str(config[2]), config[3])

    console.print(table)
    console.print()


def show_training_tips():
    """顯示訓練技巧"""
    console.print("[cyan]LoRA 訓練技巧:[/cyan]\n")

    tips = [
        "1. 選擇合適的 rank：從小開始（r=8），根據效果逐步增加",
        "2. alpha 設置：通常為 r 的 2 倍，可以實驗 1x 到 4x",
        "3. 目標模塊：至少包含 q_proj 和 v_proj，更多模塊 = 更好效果",
        "4. 學習率：LoRA 通常使用較高的學習率（2e-4 到 5e-4）",
        "5. Dropout：0.05-0.1 之間，防止過擬合",
        "6. 批次大小：使用梯度累積來模擬大批次",
        "7. 監控驗證損失：及時發現過擬合",
        "8. 保存檢查點：定期保存以便恢復訓練",
    ]

    for tip in tips:
        console.print(f"  {tip}")
    console.print()


def show_memory_estimation():
    """顯示內存估算"""
    console.print("[cyan]LoRA 內存需求估算（7B 模型）:[/cyan]\n")

    memory_data = [
        ("基礎模型 (bf16)", "14 GB"),
        ("LoRA 參數 (r=8)", "~20 MB"),
        ("LoRA 參數 (r=16)", "~40 MB"),
        ("LoRA 參數 (r=32)", "~80 MB"),
        ("優化器狀態", "~2 GB"),
        ("梯度", "~2 GB"),
        ("激活值", "~4-8 GB"),
        ("總計 (r=16)", "~22-26 GB"),
    ]

    table = Table(title="內存需求")
    table.add_column("組件", style="cyan")
    table.add_column("內存", style="green")

    for component, memory in memory_data:
        table.add_row(component, memory)

    console.print(table)
    console.print("\n[yellow]建議：至少使用 24GB VRAM 的 GPU（如 RTX 3090/4090, A5000）[/yellow]\n")


def show_training_command():
    """顯示訓練命令"""
    console.print("[cyan]訓練命令示例:[/cyan]\n")

    commands = [
        ("基礎訓練", "accelerate launch -m axolotl.cli.train lora_r16_config.yml"),
        ("使用 DeepSpeed", "accelerate launch --config_file deepspeed_config.yaml -m axolotl.cli.train lora_r16_config.yml"),
        ("恢復訓練", "accelerate launch -m axolotl.cli.train lora_r16_config.yml --resume_from_checkpoint ./lora_output/checkpoint-100"),
        ("僅預處理數據", "python -m axolotl.cli.preprocess lora_r16_config.yml"),
    ]

    for name, cmd in commands:
        console.print(f"[yellow]{name}:[/yellow]")
        console.print(f"  {cmd}")
        console.print()


def show_evaluation():
    """顯示評估方法"""
    console.print("[cyan]LoRA 模型評估:[/cyan]\n")

    console.print("[yellow]1. 自動評估指標:[/yellow]")
    console.print("  - Perplexity: 衡量模型的困惑度")
    console.print("  - Loss: 訓練和驗證損失")
    console.print()

    console.print("[yellow]2. 生成質量評估:[/yellow]")
    console.print("  - 使用測試提示詞檢查輸出質量")
    console.print("  - 對比基礎模型和微調模型的輸出")
    console.print()

    console.print("[yellow]3. 評估代碼示例:[/yellow]")
    console.print("""
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

# 載入模型
base_model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf")
model = PeftModel.from_pretrained(base_model, "./lora_output/checkpoint-100")

# 測試生成
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
prompt = "解釋什麼是機器學習"
inputs = tokenizer(prompt, return_tensors="pt")
outputs = model.generate(**inputs, max_length=200)
print(tokenizer.decode(outputs[0]))
    """)


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Axolotl LoRA 微調示例[/bold cyan]",
        border_style="cyan"
    ))

    # 1. 解釋 LoRA 參數
    explain_lora_params()

    # 2. 顯示目標模塊
    show_target_modules()

    # 3. 比較配置
    compare_lora_configs()

    # 4. 創建配置文件
    create_lora_config(rank=8, alpha=16)
    create_lora_config(rank=16, alpha=32)
    create_lora_config(rank=32, alpha=64)

    # 5. 內存估算
    show_memory_estimation()

    # 6. 訓練技巧
    show_training_tips()

    # 7. 訓練命令
    show_training_command()

    # 8. 評估方法
    show_evaluation()

    # 完成
    console.print("="*60)
    console.print("[bold green]✓ LoRA 微調示例完成！[/bold green]")
    console.print("\n[cyan]下一步:[/cyan]")
    console.print("  1. 查看 04_QLoRA訓練.py 學習量化訓練")
    console.print("  2. 查看 06_多GPU訓練.py 學習分散式訓練")
    console.print("  3. 查看 08_模型合併.py 學習權重合併")


if __name__ == "__main__":
    main()

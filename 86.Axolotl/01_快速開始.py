"""
Axolotl 快速開始示例

本示例展示：
1. Axolotl 環境檢查
2. 創建基礎訓練配置
3. 準備示例數據
4. 啟動訓練流程
"""

import os
import yaml
import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def check_environment():
    """檢查 Axolotl 環境"""
    console.print("\n[cyan]檢查 Axolotl 環境...[/cyan]")

    try:
        # 檢查 PyTorch
        import torch
        pytorch_version = torch.__version__
        cuda_available = torch.cuda.is_available()
        gpu_count = torch.cuda.device_count() if cuda_available else 0

        # 檢查主要依賴
        import transformers
        import peft

        # 創建環境信息表格
        table = Table(title="環境信息")
        table.add_column("組件", style="cyan")
        table.add_column("狀態", style="green")

        table.add_row("PyTorch", pytorch_version)
        table.add_row("CUDA 可用", "✓ 是" if cuda_available else "✗ 否")
        table.add_row("GPU 數量", str(gpu_count))
        table.add_row("Transformers", transformers.__version__)
        table.add_row("PEFT", peft.__version__)

        console.print(table)
        console.print()

        if not cuda_available:
            console.print("[yellow]警告: 未檢測到 CUDA，訓練將使用 CPU（非常慢）[/yellow]")

        return True

    except ImportError as e:
        console.print(f"[red]✗ 缺少依賴: {e}[/red]")
        console.print("[yellow]請運行: pip install -r requirements.txt[/yellow]")
        return False


def create_config_file():
    """創建 Axolotl 配置文件"""
    console.print("[cyan]創建訓練配置文件...[/cyan]")

    # 基礎配置
    config = {
        # 模型配置
        "base_model": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",  # 使用小模型示例
        "model_type": "LlamaForCausalLM",
        "tokenizer_type": "LlamaTokenizer",

        # LoRA 配置
        "adapter": "lora",
        "lora_r": 8,
        "lora_alpha": 16,
        "lora_dropout": 0.05,
        "lora_target_modules": [
            "q_proj",
            "v_proj",
            "k_proj",
            "o_proj",
        ],

        # 數據配置
        "datasets": [
            {
                "path": "data/train.jsonl",
                "type": "alpaca",
            }
        ],

        # 訓練配置
        "sequence_len": 512,
        "sample_packing": True,
        "pad_to_sequence_len": True,

        # 批次配置
        "batch_size": 4,
        "micro_batch_size": 1,
        "gradient_accumulation_steps": 4,

        # 優化器配置
        "optimizer": "adamw_torch",
        "learning_rate": 0.0002,
        "num_epochs": 3,
        "warmup_steps": 10,

        # 保存配置
        "output_dir": "./output",
        "save_steps": 100,
        "eval_steps": 50,

        # 其他配置
        "bf16": True,
        "tf32": True,
        "gradient_checkpointing": True,
        "logging_steps": 10,
    }

    # 保存配置文件
    config_path = "axolotl_config.yml"
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, sort_keys=False)

    console.print(f"[green]✓ 配置文件已創建: {config_path}[/green]")

    # 顯示配置摘要
    console.print("\n[cyan]配置摘要:[/cyan]")
    console.print(f"  基礎模型: {config['base_model']}")
    console.print(f"  微調方法: {config['adapter']}")
    console.print(f"  LoRA Rank: {config['lora_r']}")
    console.print(f"  學習率: {config['learning_rate']}")
    console.print(f"  訓練輪數: {config['num_epochs']}")
    console.print()

    return config_path


def create_sample_data():
    """創建示例訓練數據"""
    console.print("[cyan]創建示例訓練數據...[/cyan]")

    # 創建數據目錄
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    # 示例數據（Alpaca 格式）
    sample_data = [
        {
            "instruction": "解釋什麼是機器學習",
            "input": "",
            "output": "機器學習是人工智能的一個分支，它使計算機系統能夠從數據中學習和改進，而無需明確編程。通過算法和統計模型，機器學習系統可以識別模式、做出預測和決策。"
        },
        {
            "instruction": "將以下句子翻譯成英文",
            "input": "今天天氣很好",
            "output": "The weather is very nice today."
        },
        {
            "instruction": "列出三種常見的編程語言",
            "input": "",
            "output": "三種常見的編程語言包括：\n1. Python - 廣泛用於數據科學和 Web 開發\n2. JavaScript - 主要用於 Web 前端開發\n3. Java - 企業級應用開發的首選"
        },
        {
            "instruction": "計算",
            "input": "15 + 27",
            "output": "15 + 27 = 42"
        },
        {
            "instruction": "寫一個 Python 函數來計算階乘",
            "input": "",
            "output": "```python\ndef factorial(n):\n    if n == 0 or n == 1:\n        return 1\n    return n * factorial(n - 1)\n```"
        },
    ]

    # 保存為 JSONL 格式
    data_path = data_dir / "train.jsonl"
    with open(data_path, 'w', encoding='utf-8') as f:
        for item in sample_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    console.print(f"[green]✓ 示例數據已創建: {data_path}[/green]")
    console.print(f"[dim]數據條數: {len(sample_data)}[/dim]\n")

    return str(data_path)


def show_training_command(config_path):
    """顯示訓練命令"""
    console.print("[cyan]訓練命令:[/cyan]")

    # 基礎訓練命令
    basic_cmd = f"accelerate launch -m axolotl.cli.train {config_path}"

    # 多 GPU 訓練命令
    multi_gpu_cmd = f"accelerate launch --multi_gpu --num_processes 4 -m axolotl.cli.train {config_path}"

    # DeepSpeed 訓練命令
    deepspeed_cmd = f"accelerate launch --deepspeed_config_file ds_config.json -m axolotl.cli.train {config_path}"

    console.print("\n[yellow]1. 單 GPU 訓練:[/yellow]")
    console.print(f"   {basic_cmd}")

    console.print("\n[yellow]2. 多 GPU 訓練:[/yellow]")
    console.print(f"   {multi_gpu_cmd}")

    console.print("\n[yellow]3. DeepSpeed 加速:[/yellow]")
    console.print(f"   {deepspeed_cmd}")

    console.print()


def show_inference_example():
    """顯示推理示例代碼"""
    console.print("[cyan]推理示例代碼:[/cyan]\n")

    inference_code = '''
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

# 載入基礎模型
base_model = AutoModelForCausalLM.from_pretrained(
    "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    device_map="auto",
    torch_dtype=torch.float16
)

# 載入 LoRA 適配器
model = PeftModel.from_pretrained(
    base_model,
    "./output/checkpoint-100"
)

# 載入 tokenizer
tokenizer = AutoTokenizer.from_pretrained(
    "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
)

# 推理
prompt = "解釋什麼是深度學習"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_length=200)
print(tokenizer.decode(outputs[0]))
'''

    console.print(inference_code)
    console.print()


def show_next_steps():
    """顯示後續步驟"""
    console.print("="*60)
    console.print("[bold green]✓ 快速開始配置完成！[/bold green]\n")

    console.print("[cyan]後續步驟:[/cyan]")
    console.print("  1. 查看 02_數據準備.py 學習數據格式轉換")
    console.print("  2. 查看 03_LoRA微調.py 學習完整的 LoRA 訓練")
    console.print("  3. 查看 04_QLoRA訓練.py 學習量化訓練")
    console.print("  4. 查看 06_多GPU訓練.py 學習分散式訓練")

    console.print("\n[cyan]常用命令:[/cyan]")
    console.print("  # 預處理數據")
    console.print("  python -m axolotl.cli.preprocess axolotl_config.yml")
    console.print()
    console.print("  # 開始訓練")
    console.print("  accelerate launch -m axolotl.cli.train axolotl_config.yml")
    console.print()
    console.print("  # 推理測試")
    console.print("  python -m axolotl.cli.inference axolotl_config.yml \\")
    console.print("      --lora_model_dir ./output")
    console.print()


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Axolotl 快速開始示例[/bold cyan]",
        border_style="cyan"
    ))

    # 1. 檢查環境
    if not check_environment():
        return

    # 2. 創建配置文件
    config_path = create_config_file()

    # 3. 創建示例數據
    data_path = create_sample_data()

    # 4. 顯示訓練命令
    show_training_command(config_path)

    # 5. 顯示推理示例
    show_inference_example()

    # 6. 顯示後續步驟
    show_next_steps()


if __name__ == "__main__":
    main()

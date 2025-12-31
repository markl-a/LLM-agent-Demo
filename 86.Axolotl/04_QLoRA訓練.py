"""
Axolotl QLoRA 訓練示例

本示例展示：
1. QLoRA 4-bit 量化配置
2. 內存優化技術
3. QLoRA vs LoRA 對比
4. 量化訓練最佳實踐
"""

import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def explain_qlora():
    """解釋 QLoRA"""
    console.print("\n[cyan]什麼是 QLoRA？[/cyan]\n")

    console.print("QLoRA (Quantized LoRA) 是一種內存高效的微調方法，主要特點：\n")
    console.print("  1. [yellow]4-bit 量化[/yellow]: 將模型權重量化為 4-bit，大幅減少內存")
    console.print("  2. [yellow]NF4 數據類型[/yellow]: 使用 Normal Float 4-bit 格式")
    console.print("  3. [yellow]雙重量化[/yellow]: 對量化常數再次量化")
    console.print("  4. [yellow]分頁優化器[/yellow]: 使用分頁的 AdamW 優化器")
    console.print("\n[green]優勢:[/green] 可以在消費級 GPU 上訓練大模型（如 RTX 3090 24GB 可訓練 65B）\n")


def create_qlora_config():
    """創建 QLoRA 配置"""
    console.print("[cyan]創建 QLoRA 訓練配置...[/cyan]")

    config = {
        # 基礎模型
        "base_model": "meta-llama/Llama-2-7b-hf",
        "model_type": "LlamaForCausalLM",
        "tokenizer_type": "LlamaTokenizer",

        # QLoRA 特定配置
        "adapter": "qlora",
        "lora_r": 64,  # QLoRA 可以使用更大的 rank
        "lora_alpha": 16,
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

        # 量化配置
        "load_in_4bit": True,
        "bnb_4bit_quant_type": "nf4",
        "bnb_4bit_compute_dtype": "bfloat16",
        "bnb_4bit_use_double_quant": True,

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
        "batch_size": 16,  # QLoRA 可以用更大的批次
        "micro_batch_size": 4,
        "gradient_accumulation_steps": 4,
        "num_epochs": 3,

        # 優化器（分頁版本）
        "optimizer": "paged_adamw_32bit",
        "learning_rate": 0.0002,
        "lr_scheduler": "cosine",
        "warmup_steps": 100,

        # 精度設置
        "bf16": True,
        "fp16": False,
        "tf32": True,

        # 內存優化
        "gradient_checkpointing": True,
        "max_memory": None,
        "fsdp": [],
        "fsdp_config": {},

        # 輸出設置
        "output_dir": "./qlora_output",
        "logging_steps": 10,
        "save_steps": 200,
        "eval_steps": 100,
        "save_total_limit": 3,

        # 實驗追蹤
        "wandb_project": "axolotl-qlora",
        "wandb_run_id": "qlora_7b",
    }

    config_path = "qlora_config.yml"
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, sort_keys=False)

    console.print(f"[green]✓ QLoRA 配置已保存: {config_path}[/green]\n")

    return config_path


def compare_qlora_lora():
    """比較 QLoRA 和 LoRA"""
    console.print("[cyan]QLoRA vs LoRA 對比:[/cyan]\n")

    comparison = [
        ("7B 模型內存", "~6 GB", "~14 GB", "↓ 57%"),
        ("13B 模型內存", "~10 GB", "~26 GB", "↓ 62%"),
        ("30B 模型內存", "~20 GB", "~60 GB", "↓ 67%"),
        ("65B 模型內存", "~40 GB", "~130 GB", "↓ 69%"),
        ("訓練速度", "中等", "快", "↓ 20-30%"),
        ("模型質量", "優秀", "優秀", "相近"),
        ("適用 GPU", "消費級", "專業級", "更廣泛"),
    ]

    table = Table(title="QLoRA vs LoRA")
    table.add_column("指標", style="cyan")
    table.add_column("QLoRA", style="yellow")
    table.add_column("LoRA", style="green")
    table.add_column("差異", style="magenta")

    for row in comparison:
        table.add_row(*row)

    console.print(table)
    console.print()


def show_quantization_options():
    """顯示量化選項"""
    console.print("[cyan]量化配置選項:[/cyan]\n")

    options = {
        "bnb_4bit_quant_type": {
            "nf4": "Normal Float 4-bit（推薦）",
            "fp4": "Float 4-bit",
        },
        "bnb_4bit_compute_dtype": {
            "float16": "Float16 計算",
            "bfloat16": "BFloat16 計算（推薦）",
            "float32": "Float32 計算",
        },
        "bnb_4bit_use_double_quant": {
            "True": "啟用雙重量化（進一步減少內存）",
            "False": "不使用雙重量化",
        }
    }

    for param, choices in options.items():
        console.print(f"[yellow]{param}:[/yellow]")
        for value, desc in choices.items():
            console.print(f"  - {value}: {desc}")
        console.print()


def show_memory_savings():
    """顯示內存節省"""
    console.print("[cyan]不同模型的內存節省（QLoRA）:[/cyan]\n")

    models = [
        ("LLaMA-7B", "14 GB", "6 GB", "RTX 3060 12GB (需優化)"),
        ("LLaMA-13B", "26 GB", "10 GB", "RTX 3090 24GB"),
        ("LLaMA-30B", "60 GB", "20 GB", "RTX 4090 24GB"),
        ("LLaMA-65B", "130 GB", "40 GB", "A100 40GB/80GB"),
    ]

    table = Table(title="內存需求對比")
    table.add_column("模型", style="cyan")
    table.add_column("LoRA (16bit)", style="yellow")
    table.add_column("QLoRA (4bit)", style="green")
    table.add_column("推薦 GPU", style="dim")

    for model in models:
        table.add_row(*model)

    console.print(table)
    console.print()


def show_training_tips():
    """顯示 QLoRA 訓練技巧"""
    console.print("[cyan]QLoRA 訓練技巧:[/cyan]\n")

    tips = [
        "1. 使用更大的 rank：QLoRA 內存更少，可以用 r=64 甚至 128",
        "2. 分頁優化器：使用 paged_adamw_32bit 或 paged_adamw_8bit",
        "3. 雙重量化：啟用 bnb_4bit_use_double_quant 進一步節省內存",
        "4. 計算精度：使用 bfloat16 而非 float16（更穩定）",
        "5. 批次大小：QLoRA 可以使用更大的批次，提升訓練效率",
        "6. 梯度檢查點：必須啟用以節省激活值內存",
        "7. 學習率：與 LoRA 相同，通常 2e-4 到 5e-4",
        "8. 量化類型：NF4 通常優於 FP4",
    ]

    for tip in tips:
        console.print(f"  {tip}")
    console.print()


def show_troubleshooting():
    """顯示故障排除"""
    console.print("[cyan]常見問題和解決方案:[/cyan]\n")

    issues = [
        ("OOM 錯誤", [
            "減小批次大小（micro_batch_size）",
            "啟用梯度檢查點",
            "使用雙重量化",
            "減小序列長度",
        ]),
        ("訓練速度慢", [
            "減小 rank（但會影響效果）",
            "增加批次大小",
            "使用更少的目標模塊",
            "檢查是否正確使用 GPU",
        ]),
        ("精度問題", [
            "使用 bfloat16 而非 float16",
            "檢查學習率是否過大",
            "增加 warmup steps",
            "檢查數據質量",
        ]),
        ("量化錯誤", [
            "更新 bitsandbytes 到最新版本",
            "確保 CUDA 版本兼容",
            "檢查 GPU 驅動版本",
        ]),
    ]

    for issue, solutions in issues:
        console.print(f"[yellow]問題: {issue}[/yellow]")
        for solution in solutions:
            console.print(f"  - {solution}")
        console.print()


def show_training_command():
    """顯示訓練命令"""
    console.print("[cyan]QLoRA 訓練命令:[/cyan]\n")

    commands = [
        ("單 GPU 訓練", "accelerate launch -m axolotl.cli.train qlora_config.yml"),
        ("多 GPU 訓練", "accelerate launch --multi_gpu --num_processes 2 -m axolotl.cli.train qlora_config.yml"),
        ("檢查配置", "python -m axolotl.cli.preprocess qlora_config.yml --debug"),
    ]

    for name, cmd in commands:
        console.print(f"[yellow]{name}:[/yellow]")
        console.print(f"  {cmd}")
        console.print()


def show_inference_example():
    """顯示推理示例"""
    console.print("[cyan]QLoRA 模型推理:[/cyan]\n")

    console.print("[yellow]推理代碼:[/yellow]")
    console.print("""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel

# 配置 4-bit 量化
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)

# 載入量化的基礎模型
base_model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    quantization_config=bnb_config,
    device_map="auto",
)

# 載入 QLoRA 適配器
model = PeftModel.from_pretrained(base_model, "./qlora_output/checkpoint-200")

# 推理
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
prompt = "解釋什麼是量化"
inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
outputs = model.generate(**inputs, max_length=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
    """)


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Axolotl QLoRA 訓練示例[/bold cyan]",
        border_style="cyan"
    ))

    # 1. 解釋 QLoRA
    explain_qlora()

    # 2. 創建配置
    create_qlora_config()

    # 3. QLoRA vs LoRA
    compare_qlora_lora()

    # 4. 量化選項
    show_quantization_options()

    # 5. 內存節省
    show_memory_savings()

    # 6. 訓練技巧
    show_training_tips()

    # 7. 訓練命令
    show_training_command()

    # 8. 故障排除
    show_troubleshooting()

    # 9. 推理示例
    show_inference_example()

    # 完成
    console.print("="*60)
    console.print("[bold green]✓ QLoRA 訓練示例完成！[/bold green]")
    console.print("\n[cyan]總結:[/cyan]")
    console.print("  QLoRA 讓你能在消費級 GPU 上訓練大模型")
    console.print("  內存需求減少約 60-70%，效果接近全精度訓練")
    console.print("  特別適合個人研究者和小團隊")


if __name__ == "__main__":
    main()

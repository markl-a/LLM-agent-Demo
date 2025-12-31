"""
Unsloth 快速開始示例

本示例展示：
1. Unsloth 安裝檢查
2. 載入預訓練模型
3. 配置 LoRA
4. 快速訓練示例
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def check_environment():
    """檢查 Unsloth 環境"""
    console.print("\n[cyan]檢查 Unsloth 環境...[/cyan]")

    try:
        # 檢查 PyTorch
        import torch
        pytorch_version = torch.__version__
        cuda_available = torch.cuda.is_available()
        cuda_version = torch.version.cuda if cuda_available else "N/A"

        # 檢查 Unsloth
        import unsloth
        unsloth_available = True

        # 檢查其他依賴
        import transformers
        import peft
        import trl

        # 創建信息表格
        table = Table(title="環境信息")
        table.add_column("組件", style="cyan")
        table.add_column("版本/狀態", style="green")

        table.add_row("PyTorch", pytorch_version)
        table.add_row("CUDA", cuda_version)
        table.add_row("CUDA 可用", "✓ 是" if cuda_available else "✗ 否")
        table.add_row("Unsloth", "✓ 已安裝" if unsloth_available else "✗ 未安裝")
        table.add_row("Transformers", transformers.__version__)
        table.add_row("PEFT", peft.__version__)
        table.add_row("TRL", trl.__version__)

        console.print(table)
        console.print()

        if not cuda_available:
            console.print("[yellow]警告: 未檢測到 CUDA，Unsloth 需要 GPU[/yellow]")
            return False

        console.print("[green]✓ 環境檢查通過[/green]\n")
        return True

    except ImportError as e:
        console.print(f"[red]✗ 缺少依賴: {e}[/red]")
        console.print("\n[yellow]安裝 Unsloth:[/yellow]")
        console.print('  pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"')
        return False


def show_basic_usage():
    """顯示基本使用方法"""
    console.print("[cyan]Unsloth 基本使用:[/cyan]\n")

    console.print("[yellow]1. 載入模型（4-bit 量化）:[/yellow]")
    console.print("""
from unsloth import FastLanguageModel

# 載入 Unsloth 優化的 4-bit 模型
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/llama-2-7b-bnb-4bit",  # Unsloth 優化版本
    max_seq_length=2048,                        # 最大序列長度
    dtype=None,                                 # 自動選擇（bf16/fp16）
    load_in_4bit=True,                          # 4-bit 量化
)

print(f"模型載入成功: {model.config.model_type}")
print(f"模型參數: {model.num_parameters() / 1e9:.2f}B")
    """)

    console.print("\n[yellow]2. 配置 LoRA:[/yellow]")
    console.print("""
# 添加 LoRA 適配器
model = FastLanguageModel.get_peft_model(
    model,
    r=16,                                       # LoRA rank
    target_modules=[
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj"
    ],
    lora_alpha=16,
    lora_dropout=0,                             # Unsloth 建議設為 0
    bias="none",
    use_gradient_checkpointing="unsloth",       # 使用優化的檢查點
    random_state=3407,
)

print("✓ LoRA 配置完成")
    """)

    console.print("\n[yellow]3. 準備數據:[/yellow]")
    console.print("""
from datasets import load_dataset

# 載入數據集
dataset = load_dataset("yahma/alpaca-cleaned", split="train[:1000]")

# Alpaca 提示詞模板
alpaca_prompt = '''Below is an instruction. Write a response.

### Instruction:
{}

### Response:
{}'''

# 格式化函數
def formatting_prompts_func(examples):
    instructions = examples["instruction"]
    outputs = examples["output"]
    texts = []
    for instruction, output in zip(instructions, outputs):
        text = alpaca_prompt.format(instruction, output)
        texts.append(text)
    return {"text": texts}

dataset = dataset.map(formatting_prompts_func, batched=True)
    """)

    console.print("\n[yellow]4. 訓練:[/yellow]")
    console.print("""
from trl import SFTTrainer
from transformers import TrainingArguments

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=2048,
    args=TrainingArguments(
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        warmup_steps=10,
        max_steps=100,
        learning_rate=2e-4,
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        logging_steps=10,
        output_dir="outputs",
        optim="adamw_8bit",                     # 8-bit 優化器
    ),
)

# 開始訓練
trainer.train()
    """)


def show_speed_comparison():
    """顯示速度對比"""
    console.print("[cyan]Unsloth 速度優勢:[/cyan]\n")

    comparison = [
        ("前向傳播", "1.0x", "1.3x", "+30%"),
        ("反向傳播", "1.0x", "2.1x", "+110%"),
        ("完整訓練步", "1.0x", "2.5x", "+150%"),
        ("內存使用", "100%", "20%", "-80%"),
        ("批次大小", "2", "4-8", "2-4x"),
    ]

    table = Table(title="Unsloth vs 標準 HuggingFace（7B 模型）")
    table.add_column("操作", style="cyan")
    table.add_column("標準 HF", style="yellow")
    table.add_column("Unsloth", style="green")
    table.add_column("改進", style="magenta")

    for row in comparison:
        table.add_row(*row)

    console.print(table)
    console.print()


def show_supported_models():
    """顯示支持的模型"""
    console.print("[cyan]Unsloth 支持的模型:[/cyan]\n")

    models = {
        "LLaMA 系列": [
            "unsloth/llama-2-7b-bnb-4bit",
            "unsloth/llama-2-13b-bnb-4bit",
            "unsloth/llama-3-8b-bnb-4bit",
        ],
        "Mistral 系列": [
            "unsloth/mistral-7b-v0.2-bnb-4bit",
            "unsloth/mixtral-8x7b-bnb-4bit",
        ],
        "Phi 系列": [
            "unsloth/phi-2-bnb-4bit",
            "unsloth/phi-3-mini-bnb-4bit",
        ],
        "其他": [
            "unsloth/gemma-7b-bnb-4bit",
            "unsloth/qwen1.5-7b-bnb-4bit",
        ],
    }

    for category, model_list in models.items():
        console.print(f"[yellow]{category}:[/yellow]")
        for model in model_list:
            console.print(f"  - {model}")
        console.print()


def show_minimal_example():
    """顯示最小化示例"""
    console.print("[cyan]完整最小化示例:[/cyan]\n")

    console.print("""
# 完整的訓練腳本（不到 50 行）
from unsloth import FastLanguageModel
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments
import torch

# 1. 載入模型
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/llama-2-7b-bnb-4bit",
    max_seq_length=2048,
    dtype=None,
    load_in_4bit=True,
)

# 2. 配置 LoRA
model = FastLanguageModel.get_peft_model(
    model, r=16, target_modules=["q_proj", "v_proj"],
    lora_alpha=16, lora_dropout=0, bias="none",
    use_gradient_checkpointing="unsloth",
)

# 3. 準備數據
dataset = load_dataset("yahma/alpaca-cleaned", split="train[:100]")

# 4. 訓練
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=2048,
    args=TrainingArguments(
        per_device_train_batch_size=2,
        max_steps=50,
        learning_rate=2e-4,
        output_dir="outputs",
        optim="adamw_8bit",
    ),
)

trainer.train()

# 5. 保存
model.save_pretrained("lora_model")
    """)


def show_next_steps():
    """顯示後續步驟"""
    console.print("="*60)
    console.print("[bold green]✓ Unsloth 快速開始完成！[/bold green]")
    console.print("\n[cyan]下一步:[/cyan]")
    console.print("  1. 查看 02_模型加載.py 學習不同模型的載入")
    console.print("  2. 查看 03_數據格式.py 學習數據準備")
    console.print("  3. 查看 04_LoRA配置.py 學習參數調優")
    console.print("  4. 查看 08_GGUF導出.py 學習模型導出")

    console.print("\n[cyan]有用的連結:[/cyan]")
    console.print("  - GitHub: https://github.com/unslothai/unsloth")
    console.print("  - Colab 筆記本: https://github.com/unslothai/unsloth/tree/main/notebooks")
    console.print("  - Discord: https://discord.gg/unsloth")


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Unsloth 快速開始示例[/bold cyan]",
        border_style="cyan"
    ))

    # 1. 檢查環境
    if not check_environment():
        return

    # 2. 基本使用
    show_basic_usage()

    # 3. 速度對比
    show_speed_comparison()

    # 4. 支持的模型
    show_supported_models()

    # 5. 最小化示例
    show_minimal_example()

    # 6. 後續步驟
    show_next_steps()


if __name__ == "__main__":
    main()

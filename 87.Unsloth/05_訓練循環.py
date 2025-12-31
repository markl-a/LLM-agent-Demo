"""
Unsloth 訓練循環示例

本示例展示：
1. SFTTrainer 配置
2. 訓練參數設置
3. 訓練監控
4. 常見問題解決
"""

from rich.console import Console
from rich.panel import Panel

console = Console()


def show_basic_training():
    """基本訓練"""
    console.print("\n[cyan]基本訓練循環:[/cyan]\n")

    console.print("""
from unsloth import FastLanguageModel
from trl import SFTTrainer
from transformers import TrainingArguments
from datasets import load_dataset

# 1. 載入模型
model, tokenizer = FastLanguageModel.from_pretrained(
    "unsloth/llama-2-7b-bnb-4bit",
    max_seq_length=2048,
)

# 2. 配置 LoRA
model = FastLanguageModel.get_peft_model(
    model, r=16, lora_alpha=16,
    target_modules=["q_proj", "v_proj"],
    use_gradient_checkpointing="unsloth",
)

# 3. 準備數據
dataset = load_dataset("yahma/alpaca-cleaned", split="train")

# 4. 訓練參數
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
        seed=3407,
    ),
)

# 5. 開始訓練
trainer.train()
    """)


def show_training_args():
    """訓練參數詳解"""
    console.print("[cyan]重要訓練參數:[/cyan]\n")

    console.print("""
TrainingArguments(
    # 批次設置
    per_device_train_batch_size=2,              # 每個 GPU 的批次
    gradient_accumulation_steps=4,              # 梯度累積
    # 實際批次 = 2 * 4 = 8

    # 學習率
    learning_rate=2e-4,                         # LoRA 推薦值
    warmup_steps=10,                            # warmup 步數

    # 訓練長度
    max_steps=100,                              # 最大步數
    # 或 num_train_epochs=3,                    # 訓練輪數

    # 精度
    fp16=not torch.cuda.is_bf16_supported(),
    bf16=torch.cuda.is_bf16_supported(),

    # 優化器
    optim="adamw_8bit",                         # 推薦使用 8-bit

    # 日誌和保存
    logging_steps=10,
    save_steps=50,
    output_dir="outputs",

    # 其他
    seed=3407,
)
    """)


def show_monitoring():
    """訓練監控"""
    console.print("[cyan]訓練監控:[/cyan]\n")

    console.print("""
# 使用 Weights & Biases
import wandb
wandb.init(project="llama2-finetune")

trainer = SFTTrainer(
    ...
    args=TrainingArguments(
        ...
        report_to="wandb",                      # 報告到 W&B
    ),
)

# 訓練中查看指標
# - Loss 曲線
# - 學習率變化
# - 訓練速度
    """)


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Unsloth 訓練循環示例[/bold cyan]",
        border_style="cyan"
    ))

    show_basic_training()
    show_training_args()
    show_monitoring()

    console.print("="*60)
    console.print("[bold green]✓ 訓練循環示例完成！[/bold green]")


if __name__ == "__main__":
    main()

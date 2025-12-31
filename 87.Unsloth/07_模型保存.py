"""
Unsloth 模型保存示例

本示例展示：
1. 保存 LoRA 適配器
2. 保存合併後的模型
3. 保存為 16-bit
4. 檢查點管理
"""

from rich.console import Console
from rich.panel import Panel

console = Console()


def show_save_lora():
    """保存 LoRA 適配器"""
    console.print("\n[cyan]1. 保存 LoRA 適配器（最小）:[/cyan]\n")

    console.print("""
# 訓練完成後保存 LoRA 權重
model.save_pretrained("lora_model")
tokenizer.save_pretrained("lora_model")

# 大小：通常只有幾十 MB
# 載入時需要基礎模型 + LoRA 權重
    """)


def show_save_merged():
    """保存合併模型"""
    console.print("[cyan]2. 保存合併後的模型:[/cyan]\n")

    console.print("""
# 合併 LoRA 權重到基礎模型
model.save_pretrained_merged(
    "merged_model",
    tokenizer,
    save_method="merged_16bit",                 # 16-bit 精度
)

# 或保持 4-bit 量化
model.save_pretrained_merged(
    "merged_model_4bit",
    tokenizer,
    save_method="merged_4bit",
)

# 大小：完整模型大小（7B 約 14GB for 16-bit）
# 載入：直接使用，無需基礎模型
    """)


def show_save_formats():
    """不同保存格式"""
    console.print("[cyan]3. 不同保存格式:[/cyan]\n")

    console.print("""
# LoRA 適配器（最小）
model.save_pretrained("lora_adapter")

# 合併 16-bit（推薦用於部署）
model.save_pretrained_merged(
    "model_16bit",
    tokenizer,
    save_method="merged_16bit",
)

# 合併 4-bit（保持量化）
model.save_pretrained_merged(
    "model_4bit",
    tokenizer,
    save_method="merged_4bit",
)

# Lora 16-bit（不合併）
model.save_pretrained_merged(
    "lora_16bit",
    tokenizer,
    save_method="lora",
)
    """)


def show_checkpoint_management():
    """檢查點管理"""
    console.print("[cyan]4. 訓練中的檢查點:[/cyan]\n")

    console.print("""
from transformers import TrainingArguments

args = TrainingArguments(
    output_dir="checkpoints",
    save_steps=100,                             # 每 100 步保存
    save_total_limit=3,                         # 最多保留 3 個
)

# 恢復訓練
trainer.train(resume_from_checkpoint="checkpoints/checkpoint-100")
    """)


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Unsloth 模型保存示例[/bold cyan]",
        border_style="cyan"
    ))

    show_save_lora()
    show_save_merged()
    show_save_formats()
    show_checkpoint_management()

    console.print("="*60)
    console.print("[bold green]✓ 模型保存示例完成！[/bold green]")


if __name__ == "__main__":
    main()

"""
Unsloth LoRA配置示例

本示例展示：
1. LoRA 參數配置
2. 目標模塊選擇
3. Unsloth 特殊優化
4. 參數調優建議
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def explain_lora_params():
    """解釋 LoRA 參數"""
    console.print("\n[cyan]LoRA 參數詳解:[/cyan]\n")

    params = [
        ("r", "LoRA rank", "8-64", "越大效果越好但內存越多"),
        ("lora_alpha", "縮放因子", "通常等於 r", "Unsloth 建議 alpha = r"),
        ("lora_dropout", "Dropout率", "0", "Unsloth 建議設為 0"),
        ("bias", "偏置訓練", "none", "通常不訓練"),
        ("target_modules", "目標模塊", "見下文", "選擇要微調的層"),
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


def show_basic_config():
    """基本配置"""
    console.print("[cyan]基本 LoRA 配置:[/cyan]\n")

    console.print("""
from unsloth import FastLanguageModel

# 載入模型
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/llama-2-7b-bnb-4bit",
    max_seq_length=2048,
)

# 添加 LoRA（基本配置）
model = FastLanguageModel.get_peft_model(
    model,
    r=16,                                       # rank
    lora_alpha=16,                              # alpha (建議等於 r)
    lora_dropout=0,                             # Unsloth 建議為 0
    bias="none",
    target_modules=[
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj"
    ],
    use_gradient_checkpointing="unsloth",       # 使用優化檢查點
    random_state=3407,
)
    """)


def show_target_modules():
    """目標模塊選擇"""
    console.print("[cyan]不同模型的目標模塊:[/cyan]\n")

    modules = {
        "LLaMA/Mistral": [
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj"
        ],
        "Phi-2/Phi-3": [
            "q_proj", "k_proj", "v_proj", "dense",
            "fc1", "fc2"
        ],
        "Gemma": [
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj"
        ],
    }

    for model, mods in modules.items():
        console.print(f"[yellow]{model}:[/yellow]")
        console.print(f"  {', '.join(mods)}")
        console.print()

    console.print("[dim]建議：至少包含 q_proj 和 v_proj[/dim]\n")


def show_unsloth_optimizations():
    """Unsloth 特殊優化"""
    console.print("[cyan]Unsloth 特殊優化:[/cyan]\n")

    console.print("[yellow]1. 優化的梯度檢查點:[/yellow]")
    console.print("""
model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    use_gradient_checkpointing="unsloth",       # 使用 Unsloth 優化版本
    # 不要使用 "True"，會使用標準版本
)
    """)

    console.print("\n[yellow]2. Dropout 設為 0:[/yellow]")
    console.print("""
# Unsloth 建議不使用 dropout
lora_dropout=0,  # 速度更快，效果不差
    """)

    console.print("\n[yellow]3. Alpha 等於 Rank:[/yellow]")
    console.print("""
# Unsloth 測試發現 alpha = r 效果最好
r=16,
lora_alpha=16,  # 相等
    """)


def compare_configs():
    """對比不同配置"""
    console.print("[cyan]不同配置對比:[/cyan]\n")

    configs = [
        ("輕量級", "8", "8", "快速實驗"),
        ("標準", "16", "16", "大多數任務"),
        ("高性能", "32", "32", "複雜任務"),
        ("極限", "64", "64", "追求最佳效果"),
    ]

    table = Table(title="LoRA 配置建議")
    table.add_column("配置", style="cyan")
    table.add_column("rank", style="yellow")
    table.add_column("alpha", style="green")
    table.add_column("適用場景", style="dim")

    for config in configs:
        table.add_row(*config)

    console.print(table)
    console.print()


def show_advanced_config():
    """高級配置"""
    console.print("[cyan]高級配置示例:[/cyan]\n")

    console.print("""
# 高性能配置（更多模塊，更大 rank）
model = FastLanguageModel.get_peft_model(
    model,
    r=32,                                       # 更大的 rank
    lora_alpha=32,
    lora_dropout=0,
    bias="none",
    target_modules=[
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj",
        "embed_tokens", "lm_head"               # 額外模塊
    ],
    use_gradient_checkpointing="unsloth",
    random_state=3407,
    max_seq_length=2048,
)
    """)


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Unsloth LoRA配置示例[/bold cyan]",
        border_style="cyan"
    ))

    explain_lora_params()
    show_basic_config()
    show_target_modules()
    show_unsloth_optimizations()
    compare_configs()
    show_advanced_config()

    console.print("="*60)
    console.print("[bold green]✓ LoRA配置示例完成！[/bold green]")
    console.print("\n[cyan]關鍵要點:[/cyan]")
    console.print("  1. lora_dropout=0（Unsloth 特色）")
    console.print("  2. lora_alpha=r（簡化配置）")
    console.print("  3. use_gradient_checkpointing='unsloth'")


if __name__ == "__main__":
    main()

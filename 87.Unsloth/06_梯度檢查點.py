"""
Unsloth 梯度檢查點示例

本示例展示：
1. Unsloth 優化的梯度檢查點
2. 內存優化技術
3. 速度和內存權衡
"""

from rich.console import Console
from rich.panel import Panel

console = Console()


def explain_gradient_checkpointing():
    """解釋梯度檢查點"""
    console.print("\n[cyan]什麼是梯度檢查點？[/cyan]\n")
    console.print("通過重新計算部分前向傳播來節省內存：\n")
    console.print("  [green]優點:[/green] 大幅減少內存使用（30-50%）")
    console.print("  [yellow]缺點:[/yellow] 訓練速度略慢（10-20%）\n")
    console.print("Unsloth 的優化：手寫 CUDA 內核，減少開銷\n")


def show_unsloth_checkpointing():
    """Unsloth 檢查點配置"""
    console.print("[cyan]Unsloth 梯度檢查點配置:[/cyan]\n")

    console.print("""
from unsloth import FastLanguageModel

# 載入模型
model, tokenizer = FastLanguageModel.from_pretrained(
    "unsloth/llama-2-7b-bnb-4bit",
    max_seq_length=2048,
)

# 配置 LoRA 時啟用優化的梯度檢查點
model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    use_gradient_checkpointing="unsloth",       # 關鍵！使用 Unsloth 版本
)

# 不要使用標準版本
# use_gradient_checkpointing=True              # 標準版本，較慢
    """)


def compare_methods():
    """對比不同方法"""
    console.print("[cyan]梯度檢查點對比:[/cyan]\n")

    console.print("""
方法                       內存     速度      推薦
────────────────────────────────────────────
無檢查點                   100%     100%      小模型/大 GPU
標準檢查點 (True)           60%      80%       兼容性優先
Unsloth 檢查點 ("unsloth")  50%      90%       推薦！
    """)


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Unsloth 梯度檢查點示例[/bold cyan]",
        border_style="cyan"
    ))

    explain_gradient_checkpointing()
    show_unsloth_checkpointing()
    compare_methods()

    console.print("="*60)
    console.print("[bold green]✓ 梯度檢查點示例完成！[/bold green]")


if __name__ == "__main__":
    main()

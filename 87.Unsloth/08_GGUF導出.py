"""
Unsloth GGUF 導出示例

本示例展示：
1. 導出為 GGUF 格式
2. 不同量化級別
3. 用於 llama.cpp 和 Ollama
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def explain_gguf():
    """解釋 GGUF 格式"""
    console.print("\n[cyan]什麼是 GGUF？[/cyan]\n")
    console.print("GGUF（GPT-Generated Unified Format）是 llama.cpp 使用的模型格式：\n")
    console.print("  [green]優點:[/green]")
    console.print("    - CPU 友好（可在 CPU 上運行）")
    console.print("    - 多種量化級別")
    console.print("    - 兼容 llama.cpp、Ollama、LM Studio")
    console.print("    - 文件小，易於分發\n")


def show_basic_export():
    """基本導出"""
    console.print("[cyan]基本 GGUF 導出:[/cyan]\n")

    console.print("""
from unsloth import FastLanguageModel

# 載入訓練好的模型
model, tokenizer = FastLanguageModel.from_pretrained(
    "lora_model",  # 你的 LoRA 模型
    max_seq_length=2048,
)

# 導出為 GGUF（F16 精度）
model.save_pretrained_gguf(
    "model_gguf",
    tokenizer,
    quantization_method="f16",                  # 16-bit
)

# 導出為 Q4_K_M（推薦用於大多數情況）
model.save_pretrained_gguf(
    "model_q4_k_m",
    tokenizer,
    quantization_method="q4_k_m",               # 4-bit 量化
)
    """)


def show_quantization_methods():
    """量化方法對比"""
    console.print("[cyan]GGUF 量化方法對比:[/cyan]\n")

    methods = [
        ("f16", "16-bit", "最高", "100%", "最佳質量"),
        ("q8_0", "8-bit", "高", "50%", "質量和大小平衡"),
        ("q5_k_m", "5-bit", "優秀", "35%", "推薦用於大模型"),
        ("q4_k_m", "4-bit", "良好", "25%", "推薦！質量好"),
        ("q4_k_s", "4-bit", "良好", "23%", "更小的 q4"),
        ("q3_k_m", "3-bit", "中等", "18%", "極致壓縮"),
        ("q2_k", "2-bit", "較低", "12%", "最小文件"),
    ]

    table = Table(title="GGUF 量化方法（7B 模型）")
    table.add_column("方法", style="cyan")
    table.add_column("精度", style="yellow")
    table.add_column("質量", style="green")
    table.add_column("大小", style="magenta")
    table.add_column("說明", style="dim")

    for method in methods:
        table.add_row(*method)

    console.print(table)
    console.print()


def show_advanced_export():
    """高級導出選項"""
    console.print("[cyan]高級導出選項:[/cyan]\n")

    console.print("""
# 導出多個量化版本
quantization_methods = ["q4_k_m", "q5_k_m", "q8_0"]

for method in quantization_methods:
    model.save_pretrained_gguf(
        f"model_{method}",
        tokenizer,
        quantization_method=method,
    )

# 同時推送到 HuggingFace Hub
model.push_to_hub_gguf(
    "your-username/model-name",
    tokenizer,
    quantization_method="q4_k_m",
    token="hf_your_token",
)
    """)


def show_usage():
    """使用導出的模型"""
    console.print("[cyan]使用導出的 GGUF 模型:[/cyan]\n")

    console.print("[yellow]1. 使用 llama.cpp:[/yellow]")
    console.print("""
# 下載 llama.cpp
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make

# 運行推理
./main -m ../model_q4_k_m/model.gguf \\
       -p "解釋什麼是機器學習" \\
       -n 200

# 啟動服務器
./server -m ../model_q4_k_m/model.gguf \\
         --host 0.0.0.0 \\
         --port 8080
    """)

    console.print("\n[yellow]2. 使用 Ollama:[/yellow]")
    console.print("""
# 創建 Modelfile
FROM ./model_q4_k_m/model.gguf

# 導入到 Ollama
ollama create my-model -f Modelfile

# 運行
ollama run my-model "解釋深度學習"
    """)

    console.print("\n[yellow]3. 使用 LM Studio:[/yellow]")
    console.print("    直接在 LM Studio 中載入 .gguf 文件\n")


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Unsloth GGUF 導出示例[/bold cyan]",
        border_style="cyan"
    ))

    explain_gguf()
    show_basic_export()
    show_quantization_methods()
    show_advanced_export()
    show_usage()

    console.print("="*60)
    console.print("[bold green]✓ GGUF 導出示例完成！[/bold green]")
    console.print("\n[cyan]建議:[/cyan]")
    console.print("  使用 q4_k_m 獲得最佳的質量/大小平衡")


if __name__ == "__main__":
    main()

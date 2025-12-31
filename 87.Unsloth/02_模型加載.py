"""
Unsloth 模型加載示例

本示例展示：
1. 不同量化級別的模型載入
2. 自定義模型載入
3. HuggingFace Hub 模型
4. 本地模型載入
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def show_4bit_loading():
    """顯示 4-bit 模型載入"""
    console.print("\n[cyan]1. 4-bit 量化模型載入（最省內存）:[/cyan]\n")

    console.print("""
from unsloth import FastLanguageModel

# 使用 Unsloth 預優化的 4-bit 模型
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/llama-2-7b-bnb-4bit",
    max_seq_length=2048,
    dtype=None,                 # 自動選擇 bf16 或 fp16
    load_in_4bit=True,          # 4-bit 量化
)

# 查看模型信息
print(f"模型類型: {model.config.model_type}")
print(f"隱藏層大小: {model.config.hidden_size}")
print(f"層數: {model.config.num_hidden_layers}")
    """)

    console.print("[green]優點: 最省內存（~6GB for 7B），訓練速度快[/green]")
    console.print("[yellow]適用: 大多數微調任務[/yellow]\n")


def show_16bit_loading():
    """顯示 16-bit 模型載入"""
    console.print("[cyan]2. 16-bit 模型載入（更高精度）:[/cyan]\n")

    console.print("""
# 使用 16-bit 精度（fp16 或 bf16）
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/llama-2-7b",
    max_seq_length=2048,
    dtype=None,                 # 自動選擇
    load_in_4bit=False,         # 不使用 4-bit
)

# 或明確指定精度
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/llama-2-7b",
    max_seq_length=2048,
    dtype=torch.bfloat16,       # 使用 bf16
)
    """)

    console.print("[green]優點: 更高精度，可能效果更好[/green]")
    console.print("[yellow]缺點: 內存需求更高（~14GB for 7B）[/yellow]\n")


def show_custom_model_loading():
    """顯示自定義模型載入"""
    console.print("[cyan]3. 載入任意 HuggingFace 模型:[/cyan]\n")

    console.print("""
# 載入標準 HuggingFace 模型並應用 Unsloth 優化
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="meta-llama/Llama-2-7b-hf",      # 標準 HF 模型
    max_seq_length=2048,
    dtype=None,
    load_in_4bit=True,                          # Unsloth 會自動優化
)

# 其他例子
models = [
    "mistralai/Mistral-7B-v0.1",
    "microsoft/phi-2",
    "google/gemma-7b",
    "Qwen/Qwen1.5-7B",
]
    """)

    console.print("[green]優點: 靈活，可使用任何兼容模型[/green]\n")


def show_local_model_loading():
    """顯示本地模型載入"""
    console.print("[cyan]4. 載入本地模型:[/cyan]\n")

    console.print("""
# 載入本地保存的模型
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="./my_saved_model",              # 本地路徑
    max_seq_length=2048,
    dtype=None,
    load_in_4bit=True,
)

# 或載入之前訓練的 LoRA
from peft import PeftModel

base_model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/llama-2-7b-bnb-4bit",
    max_seq_length=2048,
)

# 載入 LoRA 權重
model = PeftModel.from_pretrained(
    base_model,
    "./lora_checkpoint",
)
    """)


def compare_loading_methods():
    """比較載入方法"""
    console.print("[cyan]不同載入方法對比:[/cyan]\n")

    methods = [
        ("4-bit Unsloth", "~6GB", "快", "最佳", "大多數任務"),
        ("16-bit Unsloth", "~14GB", "快", "優秀", "需要高精度"),
        ("4-bit 標準 HF", "~8GB", "中等", "良好", "兼容性優先"),
        ("16-bit 標準 HF", "~18GB", "慢", "優秀", "非 LLaMA 模型"),
    ]

    table = Table(title="模型載入方法對比（7B 模型）")
    table.add_column("方法", style="cyan")
    table.add_column("內存", style="yellow")
    table.add_column("速度", style="green")
    table.add_column("Unsloth 優化", style="magenta")
    table.add_column("推薦場景", style="dim")

    for method in methods:
        table.add_row(*method)

    console.print(table)
    console.print()


def show_advanced_options():
    """顯示高級選項"""
    console.print("[cyan]高級載入選項:[/cyan]\n")

    console.print("[yellow]1. 自定義最大序列長度:[/yellow]")
    console.print("""
# 根據任務調整序列長度
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/llama-2-7b-bnb-4bit",
    max_seq_length=512,         # 短序列，節省內存
    # max_seq_length=4096,      # 長序列，需要更多內存
)
    """)

    console.print("\n[yellow]2. 設備映射:[/yellow]")
    console.print("""
# 自動設備映射（推薦）
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/llama-2-7b-bnb-4bit",
    device_map="auto",          # 自動分配到 GPU
)

# 手動指定設備
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/llama-2-7b-bnb-4bit",
    device_map="cuda:0",        # 指定 GPU 0
)
    """)

    console.print("\n[yellow]3. Token 認證（私有模型）:[/yellow]")
    console.print("""
from huggingface_hub import login

# 登錄 HuggingFace
login(token="hf_your_token")

# 載入私有或門控模型
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="meta-llama/Llama-2-7b-hf",
    token="hf_your_token",
)
    """)


def show_memory_requirements():
    """顯示內存需求"""
    console.print("[cyan]不同模型的內存需求（4-bit + Unsloth）:[/cyan]\n")

    models = [
        ("TinyLlama-1.1B", "1.1B", "~2GB", "GTX 1660"),
        ("Phi-2", "2.7B", "~3GB", "RTX 2060"),
        ("LLaMA-2-7B", "7B", "~6GB", "RTX 3060"),
        ("Mistral-7B", "7B", "~6GB", "RTX 3060"),
        ("LLaMA-2-13B", "13B", "~10GB", "RTX 3090"),
        ("Mixtral-8x7B", "47B", "~30GB", "A100 40GB"),
        ("LLaMA-2-70B", "70B", "~40GB", "A100 40GB"),
    ]

    table = Table(title="內存需求參考")
    table.add_column("模型", style="cyan")
    table.add_column("參數量", style="yellow")
    table.add_column("VRAM 需求", style="green")
    table.add_column("推薦 GPU", style="dim")

    for model in models:
        table.add_row(*model)

    console.print(table)
    console.print()


def show_troubleshooting():
    """顯示故障排除"""
    console.print("[cyan]常見問題和解決方案:[/cyan]\n")

    issues = [
        ("CUDA Out of Memory", [
            "使用 4-bit 量化",
            "減小 max_seq_length",
            "關閉其他 GPU 程序",
        ]),
        ("模型載入慢", [
            "第一次載入需要下載，請耐心等待",
            "使用本地緩存的模型",
            "檢查網絡連接",
        ]),
        ("Token 認證失敗", [
            "使用 huggingface-cli login",
            "檢查 token 權限",
            "確認模型訪問權限",
        ]),
    ]

    for issue, solutions in issues:
        console.print(f"[yellow]問題: {issue}[/yellow]")
        for solution in solutions:
            console.print(f"  - {solution}")
        console.print()


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Unsloth 模型加載示例[/bold cyan]",
        border_style="cyan"
    ))

    # 1. 4-bit 載入
    show_4bit_loading()

    # 2. 16-bit 載入
    show_16bit_loading()

    # 3. 自定義模型
    show_custom_model_loading()

    # 4. 本地模型
    show_local_model_loading()

    # 5. 方法對比
    compare_loading_methods()

    # 6. 高級選項
    show_advanced_options()

    # 7. 內存需求
    show_memory_requirements()

    # 8. 故障排除
    show_troubleshooting()

    # 完成
    console.print("="*60)
    console.print("[bold green]✓ 模型加載示例完成！[/bold green]")
    console.print("\n[cyan]建議:[/cyan]")
    console.print("  優先使用 Unsloth 預優化的 4-bit 模型")
    console.print("  它們經過專門優化，速度最快，內存最省")


if __name__ == "__main__":
    main()

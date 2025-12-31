"""
Axolotl 評估測試示例

本示例展示：
1. 模型評估方法
2. 自動評估指標
3. 生成質量測試
4. 基準測試
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def explain_evaluation():
    """解釋評估方法"""
    console.print("\n[cyan]模型評估方法:[/cyan]\n")

    methods = [
        ("自動指標", "Perplexity, Loss, BLEU, ROUGE", "客觀、可重現", "不全面反映質量"),
        ("生成質量", "人工評估輸出質量", "全面、真實", "主觀、耗時"),
        ("基準測試", "標準數據集測試", "可比較性強", "可能與實際應用不符"),
        ("實際應用", "真實場景測試", "最準確", "難以量化"),
    ]

    table = Table(title="評估方法對比")
    table.add_column("方法", style="cyan")
    table.add_column("內容", style="yellow")
    table.add_column("優點", style="green")
    table.add_column("缺點", style="red")

    for method in methods:
        table.add_row(*method)

    console.print(table)
    console.print()


def show_automatic_metrics():
    """顯示自動評估指標"""
    console.print("[cyan]自動評估指標:[/cyan]\n")

    metrics = {
        "Perplexity（困惑度）": {
            "定義": "模型對測試數據的預測不確定性",
            "計算": "exp(loss)",
            "解釋": "越低越好，表示模型越確定",
            "範圍": "1 到 ∞",
        },
        "Loss（損失）": {
            "定義": "模型預測與真實值的差距",
            "計算": "交叉熵損失",
            "解釋": "越低越好",
            "範圍": "0 到 ∞",
        },
        "BLEU": {
            "定義": "生成文本與參考文本的 n-gram 重疊",
            "計算": "精確率的幾何平均",
            "解釋": "常用於翻譯任務",
            "範圍": "0 到 100",
        },
        "ROUGE": {
            "定義": "生成文本與參考文本的召回率",
            "計算": "n-gram 召回率",
            "解釋": "常用於摘要任務",
            "範圍": "0 到 1",
        },
    }

    for metric, info in metrics.items():
        console.print(f"[yellow]{metric}:[/yellow]")
        for key, value in info.items():
            console.print(f"  {key}: {value}")
        console.print()


def show_evaluation_code():
    """顯示評估代碼示例"""
    console.print("[cyan]評估代碼示例:[/cyan]\n")

    console.print("[yellow]1. 基本評估:[/yellow]")
    console.print("""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

# 載入模型
base_model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    device_map="auto",
    torch_dtype=torch.bfloat16
)
model = PeftModel.from_pretrained(base_model, "./lora_output/checkpoint-100")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")

# 評估模式
model.eval()

# 計算 Perplexity
def calculate_perplexity(model, tokenizer, texts):
    total_loss = 0
    total_tokens = 0

    with torch.no_grad():
        for text in texts:
            inputs = tokenizer(text, return_tensors="pt").to(model.device)
            outputs = model(**inputs, labels=inputs["input_ids"])
            total_loss += outputs.loss.item() * inputs["input_ids"].size(1)
            total_tokens += inputs["input_ids"].size(1)

    perplexity = torch.exp(torch.tensor(total_loss / total_tokens))
    return perplexity.item()

# 測試數據
test_texts = ["測試文本1", "測試文本2", "測試文本3"]
ppl = calculate_perplexity(model, tokenizer, test_texts)
print(f"Perplexity: {ppl:.2f}")
    """)

    console.print("\n[yellow]2. 生成質量測試:[/yellow]")
    console.print("""
# 測試提示詞
test_prompts = [
    "解釋什麼是機器學習",
    "寫一個 Python 函數計算階乘",
    "總結人工智能的發展歷史",
]

# 生成回覆
for prompt in test_prompts:
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(
        **inputs,
        max_length=200,
        temperature=0.7,
        top_p=0.9,
        do_sample=True
    )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(f"\\nPrompt: {prompt}")
    print(f"Response: {response}")
    """)

    console.print("\n[yellow]3. 對比評估:[/yellow]")
    console.print("""
# 對比基礎模型和微調模型
def compare_models(base_model, finetuned_model, tokenizer, prompt):
    # 基礎模型生成
    inputs = tokenizer(prompt, return_tensors="pt").to(base_model.device)
    base_output = base_model.generate(**inputs, max_length=200)
    base_text = tokenizer.decode(base_output[0], skip_special_tokens=True)

    # 微調模型生成
    ft_output = finetuned_model.generate(**inputs, max_length=200)
    ft_text = tokenizer.decode(ft_output[0], skip_special_tokens=True)

    print(f"Base Model: {base_text}")
    print(f"Fine-tuned Model: {ft_text}")

compare_models(base_model, model, tokenizer, "解釋深度學習")
    """)


def show_benchmark_tests():
    """顯示基準測試"""
    console.print("[cyan]基準測試數據集:[/cyan]\n")

    benchmarks = [
        ("MMLU", "多任務語言理解", "57 個任務", "通用知識"),
        ("HellaSwag", "常識推理", "選擇題", "推理能力"),
        ("TruthfulQA", "真實性問答", "817 個問題", "事實準確性"),
        ("GSM8K", "數學問題", "8500 個題目", "數學推理"),
        ("HumanEval", "代碼生成", "164 個編程題", "編程能力"),
        ("MT-Bench", "多輪對話", "80 個對話", "對話能力"),
    ]

    table = Table(title="常用基準測試")
    table.add_column("名稱", style="cyan")
    table.add_column("類型", style="yellow")
    table.add_column("規模", style="green")
    table.add_column("評估內容", style="magenta")

    for benchmark in benchmarks:
        table.add_row(*benchmark)

    console.print(table)
    console.print()


def show_evaluation_checklist():
    """顯示評估檢查清單"""
    console.print("[cyan]評估檢查清單:[/cyan]\n")

    checklist = [
        "□ 訓練集性能（檢查過擬合）",
        "□ 驗證集性能（模型選擇）",
        "□ 測試集性能（最終評估）",
        "□ Perplexity 指標",
        "□ 生成質量測試（10-20 個提示詞）",
        "□ 領域特定任務測試",
        "□ 與基礎模型對比",
        "□ 與其他方法對比（如不同 rank 的 LoRA）",
        "□ 邊緣案例測試",
        "□ 事實準確性檢查",
        "□ 有害內容檢測",
        "□ 推理速度測試",
    ]

    for item in checklist:
        console.print(f"  {item}")
    console.print()


def show_quality_criteria():
    """顯示質量評估標準"""
    console.print("[cyan]生成質量評估標準:[/cyan]\n")

    criteria = {
        "相關性": "回答是否切題、相關",
        "準確性": "事實是否正確、可靠",
        "完整性": "回答是否全面、詳細",
        "連貫性": "邏輯是否清晰、流暢",
        "格式": "格式是否正確、規範",
        "創造性": "是否有新穎見解（如適用）",
        "安全性": "是否避免有害、不當內容",
        "一致性": "多次生成是否穩定一致",
    }

    for criterion, description in criteria.items():
        console.print(f"  [yellow]{criterion}:[/yellow] {description}")
    console.print()


def show_ab_testing():
    """顯示 A/B 測試方法"""
    console.print("[cyan]A/B 測試方法:[/cyan]\n")

    console.print("對比不同版本的模型：\n")

    console.print("  1. [yellow]準備:[/yellow]")
    console.print("     - 選擇代表性測試用例（20-50 個）")
    console.print("     - 定義評估標準")
    console.print("     - 設置評估人員\n")

    console.print("  2. [yellow]執行:[/yellow]")
    console.print("     - 盲測（不告知模型版本）")
    console.print("     - 隨機順序")
    console.print("     - 多人評估求平均\n")

    console.print("  3. [yellow]分析:[/yellow]")
    console.print("     - 計算勝率")
    console.print("     - 統計顯著性檢驗")
    console.print("     - 定性分析差異\n")

    console.print("[dim]示例：LoRA rank=8 vs rank=16 vs rank=32[/dim]\n")


def show_continuous_evaluation():
    """顯示持續評估策略"""
    console.print("[cyan]持續評估策略:[/cyan]\n")

    strategies = [
        "1. 訓練中評估：",
        "   - 每 N 步在驗證集上評估",
        "   - 監控 Loss 曲線",
        "   - Early stopping",
        "",
        "2. 檢查點評估：",
        "   - 保存多個檢查點",
        "   - 對每個檢查點進行完整評估",
        "   - 選擇最佳檢查點",
        "",
        "3. 增量評估：",
        "   - 定義核心測試集（快速評估）",
        "   - 定義完整測試集（詳細評估）",
        "   - 先快速篩選，再詳細測試",
        "",
        "4. 生產監控：",
        "   - 收集真實用戶反饋",
        "   - A/B 測試新版本",
        "   - 監控異常案例",
    ]

    for strategy in strategies:
        console.print(f"  {strategy}")
    console.print()


def show_reporting():
    """顯示評估報告模板"""
    console.print("[cyan]評估報告模板:[/cyan]\n")

    console.print("""
# 模型評估報告

## 1. 基本信息
- 模型: meta-llama/Llama-2-7b-hf
- 微調方法: LoRA (r=16, alpha=32)
- 訓練數據: 10,000 樣本
- 訓練時長: 3 epochs

## 2. 自動指標
- Validation Loss: 1.23
- Perplexity: 3.42
- Training Time: 4 小時

## 3. 生成質量（1-5 分）
- 相關性: 4.5
- 準確性: 4.2
- 完整性: 4.0
- 連貫性: 4.3
- 平均: 4.25

## 4. 對比結果
- vs 基礎模型: +15% 提升
- vs LoRA r=8: +5% 提升
- vs 全量微調: -2% 差距

## 5. 優勢與不足
優勢：
- 指令遵循能力強
- 格式化輸出規範
- 推理邏輯清晰

不足：
- 偶爾出現重複
- 事實性有待提升
- 創造性略顯不足

## 6. 建議
- 增加訓練數據多樣性
- 考慮增大 LoRA rank 到 32
- 加強事實性數據訓練
    """)


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Axolotl 評估測試示例[/bold cyan]",
        border_style="cyan"
    ))

    # 1. 解釋評估方法
    explain_evaluation()

    # 2. 自動指標
    show_automatic_metrics()

    # 3. 評估代碼
    show_evaluation_code()

    # 4. 基準測試
    show_benchmark_tests()

    # 5. 質量標準
    show_quality_criteria()

    # 6. 評估檢查清單
    show_evaluation_checklist()

    # 7. A/B 測試
    show_ab_testing()

    # 8. 持續評估
    show_continuous_evaluation()

    # 9. 評估報告
    show_reporting()

    # 完成
    console.print("="*60)
    console.print("[bold green]✓ 評估測試示例完成！[/bold green]")
    console.print("\n[cyan]記住:[/cyan]")
    console.print("  評估不是一次性的，而是持續的過程")
    console.print("  結合自動指標和人工評估才能全面了解模型質量")


if __name__ == "__main__":
    main()

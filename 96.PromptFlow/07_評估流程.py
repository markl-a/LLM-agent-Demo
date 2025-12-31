"""
PromptFlow 評估流程示例

本示例展示：
1. 評估 Flow 的創建
2. 評估指標定義
3. 運行評估
4. 結果分析
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax

console = Console()


def explain_evaluation():
    """解釋評估概念"""
    console.print("\n[cyan]評估 Flow 概念[/cyan]\n")

    explanation = """評估 Flow (Evaluation Flow) 是用於評估主 Flow 性能的特殊 Flow

主要用途：
1. 質量評估 - 評估輸出的正確性、相關性
2. 性能評估 - 測量延遲、成本等指標
3. A/B 測試 - 對比不同版本的效果
4. 回歸測試 - 確保更新不影響質量

評估流程：
Main Flow (生成答案) → Eval Flow (評估答案) → 指標輸出
"""

    console.print(Panel(explanation, border_style="cyan"))
    console.print()


def create_evaluation_flow():
    """創建評估 Flow"""
    console.print("[cyan]1. 創建評估 Flow[/cyan]\n")

    console.print("[yellow]評估 Flow 配置:[/yellow]\n")

    config = """# eval_flow/flow.dag.yaml
$schema: https://azuremlschemas.azureedge.net/promptflow/latest/Flow.schema.json

inputs:
  # 主 Flow 的輸入
  question:
    type: string
  # 主 Flow 的輸出
  answer:
    type: string
  # 標準答案（可選）
  ground_truth:
    type: string
    default: ""

outputs:
  # 評估分數
  score:
    type: number
    reference: ${calculate_score.output.score}
  # 評估詳情
  details:
    type: object
    reference: ${calculate_score.output}

nodes:
  # 評估節點
  - name: calculate_score
    type: python
    source:
      type: code
      path: evaluate.py
    inputs:
      question: ${inputs.question}
      answer: ${inputs.answer}
      ground_truth: ${inputs.ground_truth}"""

    syntax = Syntax(config, "yaml", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def show_evaluation_metrics():
    """顯示評估指標"""
    console.print("[cyan]2. 常見評估指標[/cyan]\n")

    code = """from promptflow import tool
from typing import Dict
import re

@tool
def evaluate(question: str, answer: str, ground_truth: str = "") -> Dict:
    \"\"\"綜合評估函數\"\"\"

    # 1. 答案完整性評分
    completeness_score = evaluate_completeness(answer)

    # 2. 相關性評分
    relevance_score = evaluate_relevance(question, answer)

    # 3. 準確性評分（如果有標準答案）
    accuracy_score = 0.0
    if ground_truth:
        accuracy_score = evaluate_accuracy(answer, ground_truth)

    # 4. 長度檢查
    length_appropriate = 50 <= len(answer) <= 500

    # 綜合分數
    overall_score = (
        completeness_score * 0.3 +
        relevance_score * 0.3 +
        accuracy_score * 0.4
    )

    return {
        "score": overall_score,
        "completeness": completeness_score,
        "relevance": relevance_score,
        "accuracy": accuracy_score,
        "length_check": length_appropriate,
        "answer_length": len(answer)
    }


def evaluate_completeness(answer: str) -> float:
    \"\"\"評估答案完整性\"\"\"
    # 檢查答案是否包含基本要素
    has_subject = len(answer) > 20
    has_punctuation = any(p in answer for p in "。！？")
    has_structure = "\\n" in answer or len(answer.split("。")) > 1

    score = sum([has_subject, has_punctuation, has_structure]) / 3
    return score


def evaluate_relevance(question: str, answer: str) -> float:
    \"\"\"評估相關性\"\"\"
    # 簡單的關鍵詞匹配
    question_words = set(re.findall(r'\\w+', question.lower()))
    answer_words = set(re.findall(r'\\w+', answer.lower()))

    if not question_words:
        return 0.0

    # 計算重疊度
    overlap = len(question_words & answer_words)
    score = overlap / len(question_words)

    return min(score, 1.0)


def evaluate_accuracy(answer: str, ground_truth: str) -> float:
    \"\"\"評估準確性\"\"\"
    # 簡單的文本相似度
    answer_words = set(re.findall(r'\\w+', answer.lower()))
    truth_words = set(re.findall(r'\\w+', ground_truth.lower()))

    if not truth_words:
        return 0.0

    # 計算 F1 分數
    intersection = len(answer_words & truth_words)
    precision = intersection / len(answer_words) if answer_words else 0
    recall = intersection / len(truth_words) if truth_words else 0

    if precision + recall == 0:
        return 0.0

    f1 = 2 * (precision * recall) / (precision + recall)
    return f1
"""

    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def show_llm_based_evaluation():
    """基於 LLM 的評估"""
    console.print("[cyan]3. 基於 LLM 的評估[/cyan]\n")

    code = """from promptflow import tool

@tool
def llm_evaluate(question: str, answer: str, ground_truth: str) -> dict:
    \"\"\"使用 LLM 進行評估\"\"\"

    # 構建評估提示
    evaluation_prompt = f\"\"\"
請評估以下問答的質量：

問題：{question}

回答：{answer}

標準答案：{ground_truth}

請從以下維度評分（0-10分）：
1. 準確性 - 回答是否正確
2. 完整性 - 是否涵蓋重點
3. 清晰度 - 表達是否清晰
4. 相關性 - 是否切題

返回 JSON 格式：
{{
    "accuracy": 分數,
    "completeness": 分數,
    "clarity": 分數,
    "relevance": 分數,
    "explanation": "評分理由"
}}
\"\"\"

    # 調用 LLM（這裡需要實際的 LLM 連接）
    # response = call_llm(evaluation_prompt)

    # 模擬返回
    return {
        "accuracy": 8.5,
        "completeness": 7.0,
        "clarity": 9.0,
        "relevance": 8.0,
        "overall": 8.1,
        "explanation": "回答準確且清晰，但可以更完整"
    }
"""

    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def show_run_evaluation():
    """運行評估"""
    console.print("[cyan]4. 運行評估 Flow[/cyan]\n")

    commands = """# 步驟 1: 運行主 Flow 並保存結果
pf run create \\
  --flow ./main_flow \\
  --data ./test_data.jsonl \\
  --name main_run

# 步驟 2: 運行評估 Flow
pf run create \\
  --flow ./eval_flow \\
  --data ./test_data.jsonl \\
  --column-mapping \\
    question='${data.question}' \\
    answer='${run.outputs.answer}' \\
    ground_truth='${data.ground_truth}' \\
  --run main_run \\
  --name eval_run

# 步驟 3: 查看評估結果
pf run show-metrics --name eval_run

# 步驟 4: 查看詳細結果
pf run show-details --name eval_run
"""

    syntax = Syntax(commands, "bash", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def simulate_evaluation_results():
    """模擬評估結果"""
    console.print("[cyan]5. 評估結果示例[/cyan]\n")

    results = [
        {"id": 1, "score": 0.85, "completeness": 0.9, "relevance": 0.8, "accuracy": 0.85},
        {"id": 2, "score": 0.72, "completeness": 0.7, "relevance": 0.75, "accuracy": 0.70},
        {"id": 3, "score": 0.91, "completeness": 0.95, "relevance": 0.90, "accuracy": 0.88},
        {"id": 4, "score": 0.68, "completeness": 0.6, "relevance": 0.70, "accuracy": 0.75},
        {"id": 5, "score": 0.88, "completeness": 0.85, "relevance": 0.90, "accuracy": 0.90},
    ]

    table = Table(title="評估結果")
    table.add_column("ID", style="cyan")
    table.add_column("總分", style="yellow")
    table.add_column("完整性", style="green")
    table.add_column("相關性", style="magenta")
    table.add_column("準確性", style="blue")

    for r in results:
        table.add_row(
            str(r["id"]),
            f"{r['score']:.2f}",
            f"{r['completeness']:.2f}",
            f"{r['relevance']:.2f}",
            f"{r['accuracy']:.2f}"
        )

    console.print(table)
    console.print()

    # 統計摘要
    avg_score = sum(r["score"] for r in results) / len(results)
    console.print(f"[cyan]平均分數:[/cyan] [yellow]{avg_score:.2f}[/yellow]")
    console.print(f"[cyan]通過率 (>0.7):[/cyan] [yellow]{sum(1 for r in results if r['score'] > 0.7) / len(results):.1%}[/yellow]")
    console.print()


def show_builtin_evaluators():
    """內置評估器"""
    console.print("[cyan]6. PromptFlow 內置評估器[/cyan]\n")

    evaluators = [
        ("Classification", "分類任務評估", "準確率、精確率、召回率、F1"),
        ("QA", "問答系統評估", "相關性、連貫性、流暢度"),
        ("Similarity", "相似度評估", "餘弦相似度、BLEU、ROUGE"),
        ("Groundedness", "基於事實評估", "答案是否基於提供的上下文"),
        ("Relevance", "相關性評估", "答案與問題的相關度"),
        ("Coherence", "連貫性評估", "答案的邏輯連貫性"),
        ("Fluency", "流暢度評估", "語言表達的流暢程度"),
    ]

    table = Table(title="內置評估器")
    table.add_column("評估器", style="cyan")
    table.add_column("用途", style="yellow")
    table.add_column("指標", style="green")

    for name, purpose, metrics in evaluators:
        table.add_row(name, purpose, metrics)

    console.print(table)
    console.print()

    # 使用示例
    example = """# 使用內置評估器
from promptflow.evals.evaluators import RelevanceEvaluator

relevance_eval = RelevanceEvaluator(model_config)
result = relevance_eval(
    question="問題",
    answer="回答",
    context="上下文"
)
"""

    syntax = Syntax(example, "python", theme="monokai")
    console.print("[dim]使用示例:[/dim]")
    console.print(syntax)
    console.print()


def show_best_practices():
    """最佳實踐"""
    console.print("[cyan]評估 Flow 最佳實踐[/cyan]\n")

    practices = """1. 多維度評估
   - 不要只依賴單一指標
   - 結合自動評估和人工評估
   - 考慮任務特定的指標

2. 基準數據集
   - 維護高質量的測試集
   - 包含標準答案
   - 定期更新數據

3. 評估指標選擇
   - 根據任務類型選擇
   - 考慮業務目標
   - 平衡速度和質量

4. 持續評估
   - 整合到 CI/CD
   - 監控性能變化
   - 設置告警閾值

5. 結果分析
   - 分析失敗案例
   - 識別模式
   - 指導優化方向

6. 版本對比
   - 保存歷史評估結果
   - 對比不同版本
   - 追蹤改進效果"""

    console.print(Panel(practices, border_style="cyan"))
    console.print()


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]PromptFlow 評估流程示例[/bold cyan]\n"
        "[dim]學習如何評估 Flow 性能[/dim]",
        border_style="cyan"
    ))

    # 1. 解釋評估
    explain_evaluation()

    # 2. 創建評估 Flow
    create_evaluation_flow()

    # 3. 評估指標
    show_evaluation_metrics()

    # 4. LLM 評估
    show_llm_based_evaluation()

    # 5. 運行評估
    show_run_evaluation()

    # 6. 評估結果
    simulate_evaluation_results()

    # 7. 內置評估器
    show_builtin_evaluators()

    # 8. 最佳實踐
    show_best_practices()

    # 完成
    console.print("="*60)
    console.print("[bold green]✓ 評估流程示例完成！[/bold green]\n")
    console.print("[cyan]下一步:[/cyan]")
    console.print("  1. 查看 08_部署服務.py - 學習部署")
    console.print("  2. 查看 09_Azure整合.py - 學習 Azure 整合")
    console.print("  3. 實踐: 為自己的 Flow 創建評估流程")


if __name__ == "__main__":
    main()

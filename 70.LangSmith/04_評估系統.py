"""
LangSmith 評估系統 - Evaluations

這個示例展示如何：
1. 創建和使用評估器
2. 運行批量評估
3. 使用內建評估指標
4. 創建自定義評估器
5. 比較不同模型/提示的性能
6. 分析評估結果

評估是改進 LLM 應用的關鍵工具。
"""

import os
from typing import Dict, Any, List
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langsmith import Client, evaluate
from langsmith.evaluation import EvaluationResult
from langsmith.schemas import Run, Example
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def setup_environment():
    """配置環境"""
    load_dotenv()
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    if not os.getenv("LANGCHAIN_PROJECT"):
        os.environ["LANGCHAIN_PROJECT"] = "evaluation-demo"
    console.print("[green]✓ 環境配置完成[/green]")


def create_sample_dataset():
    """創建示例數據集用於評估"""
    console.print(Panel("[bold cyan]創建示例數據集[/bold cyan]"))

    try:
        client = Client()

        dataset_name = "qa-evaluation-dataset"

        # 檢查數據集是否已存在
        try:
            existing = client.read_dataset(dataset_name=dataset_name)
            console.print(f"[yellow]數據集已存在，刪除舊版本...[/yellow]")
            client.delete_dataset(dataset_name=dataset_name)
        except:
            pass

        # 創建新數據集
        dataset = client.create_dataset(
            dataset_name=dataset_name,
            description="問答評估測試數據集"
        )

        console.print(f"[green]✓ 創建數據集：{dataset_name}[/green]")

        # 添加示例數據
        examples = [
            {
                "inputs": {"question": "什麼是機器學習？"},
                "outputs": {
                    "answer": "機器學習是人工智慧的一個分支，它使計算機系統能夠從數據中學習和改進，而無需明確編程。"
                }
            },
            {
                "inputs": {"question": "Python 是什麼？"},
                "outputs": {
                    "answer": "Python 是一種高級、解釋型、通用的程式語言，以其簡潔的語法和強大的功能而聞名。"
                }
            },
            {
                "inputs": {"question": "什麼是深度學習？"},
                "outputs": {
                    "answer": "深度學習是機器學習的一個子集，使用多層神經網絡來學習數據的複雜模式和表示。"
                }
            },
            {
                "inputs": {"question": "解釋一下 API"},
                "outputs": {
                    "answer": "API（應用程式介面）是一組定義和協議，允許不同的軟體應用程式相互通信和交換數據。"
                }
            },
            {
                "inputs": {"question": "什麼是雲計算？"},
                "outputs": {
                    "answer": "雲計算是通過網際網路提供計算服務，包括伺服器、存儲、數據庫、網絡等，按需使用和付費。"
                }
            }
        ]

        for example in examples:
            client.create_example(
                dataset_id=dataset.id,
                inputs=example["inputs"],
                outputs=example["outputs"]
            )

        console.print(f"[green]✓ 添加了 {len(examples)} 個示例[/green]")

        return dataset_name

    except Exception as e:
        console.print(f"[red]錯誤：{e}[/red]")
        return None


# 示例 1：簡單的評估器
def correctness_evaluator(run: Run, example: Example) -> dict:
    """
    評估答案的正確性
    這是一個簡單的基於關鍵詞匹配的評估器
    """
    # 獲取模型輸出
    prediction = run.outputs.get("output", "")

    # 獲取期望輸出
    expected = example.outputs.get("answer", "")

    # 簡單的評分邏輯：檢查關鍵詞是否存在
    # 實際應用中應該使用更複雜的評估邏輯
    score = 0.0

    # 轉換為小寫進行比較
    pred_lower = prediction.lower()
    exp_lower = expected.lower()

    # 提取關鍵詞（簡化版）
    expected_words = set(exp_lower.split())

    # 計算重疊度
    if expected_words:
        pred_words = set(pred_lower.split())
        overlap = len(expected_words & pred_words)
        score = overlap / len(expected_words)

    return {
        "key": "correctness",
        "score": score,
        "comment": f"關鍵詞重疊度：{score:.2%}"
    }


# 示例 2：長度評估器
def length_evaluator(run: Run, example: Example) -> dict:
    """評估答案的長度是否合適"""
    prediction = run.outputs.get("output", "")

    # 期望的答案長度範圍
    min_length = 50
    max_length = 300

    length = len(prediction)

    # 評分
    if min_length <= length <= max_length:
        score = 1.0
        comment = "長度適中"
    elif length < min_length:
        score = max(0.0, length / min_length)
        comment = "答案太短"
    else:
        score = max(0.0, 1.0 - (length - max_length) / max_length)
        comment = "答案太長"

    return {
        "key": "length",
        "score": score,
        "comment": f"{comment} (長度: {length})"
    }


# 示例 3：使用 LLM 作為評估器
def llm_evaluator(run: Run, example: Example) -> dict:
    """
    使用 LLM 評估答案質量
    這是一個更智能的評估方法
    """
    try:
        prediction = run.outputs.get("output", "")
        question = example.inputs.get("question", "")
        expected = example.outputs.get("answer", "")

        # 創建評估 LLM
        evaluator_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

        # 評估提示
        eval_prompt = f"""
請評估以下答案的質量（0-1 分）：

問題：{question}

參考答案：{expected}

實際答案：{prediction}

評估標準：
1. 準確性：信息是否正確
2. 完整性：是否涵蓋了關鍵點
3. 清晰度：表達是否清楚

請只返回一個 0-1 之間的分數，保留兩位小數。
        """

        # 獲取評分
        response = evaluator_llm.invoke(eval_prompt)
        score_str = response.content.strip()

        # 解析分數
        try:
            score = float(score_str)
            score = max(0.0, min(1.0, score))  # 確保在 0-1 範圍內
        except:
            score = 0.5  # 默認分數

        return {
            "key": "llm_quality",
            "score": score,
            "comment": f"LLM 評分：{score:.2f}"
        }

    except Exception as e:
        console.print(f"[red]LLM 評估器錯誤：{e}[/red]")
        return {
            "key": "llm_quality",
            "score": 0.0,
            "comment": f"評估失敗：{str(e)}"
        }


def run_basic_evaluation():
    """示例 1：運行基本評估"""
    console.print(Panel("[bold cyan]示例 1：基本評估[/bold cyan]"))

    try:
        # 創建被測試的系統
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        prompt = ChatPromptTemplate.from_template(
            "請簡潔回答以下問題：{question}"
        )
        chain = prompt | llm | StrOutputParser()

        def predict(inputs: dict) -> dict:
            """預測函數"""
            answer = chain.invoke(inputs)
            return {"output": answer}

        # 創建數據集
        dataset_name = create_sample_dataset()
        if not dataset_name:
            return

        console.print("\n[cyan]開始評估...[/cyan]\n")

        # 運行評估
        results = evaluate(
            predict,
            data=dataset_name,
            evaluators=[correctness_evaluator, length_evaluator],
            experiment_prefix="basic-eval",
            description="基本評估測試"
        )

        # 顯示結果
        console.print("[green]✓ 評估完成！[/green]\n")

        # 打印結果摘要
        display_evaluation_results(results)

        return results

    except Exception as e:
        console.print(f"[red]錯誤：{e}[/red]")
        import traceback
        console.print(traceback.format_exc())
        return None


def run_llm_evaluation():
    """示例 2：使用 LLM 評估器"""
    console.print(Panel("[bold cyan]示例 2：LLM 評估器[/bold cyan]"))

    try:
        # 創建被測試的系統
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        prompt = ChatPromptTemplate.from_template(
            "請詳細回答：{question}"
        )
        chain = prompt | llm | StrOutputParser()

        def predict(inputs: dict) -> dict:
            answer = chain.invoke(inputs)
            return {"output": answer}

        # 獲取數據集
        client = Client()
        dataset_name = "qa-evaluation-dataset"

        console.print("\n[cyan]使用 LLM 進行評估...[/cyan]\n")

        # 運行評估（包含 LLM 評估器）
        results = evaluate(
            predict,
            data=dataset_name,
            evaluators=[
                correctness_evaluator,
                length_evaluator,
                llm_evaluator
            ],
            experiment_prefix="llm-eval",
            description="使用 LLM 評估器"
        )

        console.print("[green]✓ LLM 評估完成！[/green]\n")

        display_evaluation_results(results)

        return results

    except Exception as e:
        console.print(f"[red]錯誤：{e}[/red]")
        import traceback
        console.print(traceback.format_exc())
        return None


def compare_models():
    """示例 3：比較不同模型"""
    console.print(Panel("[bold cyan]示例 3：模型比較[/bold cyan]"))

    try:
        client = Client()
        dataset_name = "qa-evaluation-dataset"

        # 定義要比較的模型
        models = [
            {"name": "GPT-4o-mini (temp=0.3)", "model": "gpt-4o-mini", "temp": 0.3},
            {"name": "GPT-4o-mini (temp=0.7)", "model": "gpt-4o-mini", "temp": 0.7},
        ]

        all_results = {}

        for model_config in models:
            console.print(f"\n[cyan]評估模型：{model_config['name']}[/cyan]\n")

            # 創建預測函數
            llm = ChatOpenAI(
                model=model_config["model"],
                temperature=model_config["temp"]
            )
            prompt = ChatPromptTemplate.from_template("簡潔回答：{question}")
            chain = prompt | llm | StrOutputParser()

            def predict(inputs: dict) -> dict:
                answer = chain.invoke(inputs)
                return {"output": answer}

            # 運行評估
            results = evaluate(
                predict,
                data=dataset_name,
                evaluators=[correctness_evaluator, length_evaluator],
                experiment_prefix=f"compare-{model_config['name']}",
                description=f"評估 {model_config['name']}"
            )

            all_results[model_config["name"]] = results

        # 比較結果
        console.print("\n[bold green]模型比較結果[/bold green]\n")
        compare_results(all_results)

        return all_results

    except Exception as e:
        console.print(f"[red]錯誤：{e}[/red]")
        import traceback
        console.print(traceback.format_exc())
        return None


def display_evaluation_results(results):
    """顯示評估結果"""
    console.print("[bold]評估結果摘要：[/bold]\n")

    # 創建結果表格
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("指標", style="cyan", width=20)
    table.add_column("平均分數", style="green", width=15)
    table.add_column("最小值", style="yellow", width=15)
    table.add_column("最大值", style="yellow", width=15)

    # 提取結果（這裡簡化處理）
    metrics = {
        "correctness": [],
        "length": [],
        "llm_quality": []
    }

    # 注意：實際的 results 對象結構可能不同
    # 這裡展示概念性的代碼

    console.print("[yellow]詳細結果請查看 LangSmith UI[/yellow]")
    console.print(f"項目：{os.getenv('LANGCHAIN_PROJECT')}")


def compare_results(all_results: Dict[str, Any]):
    """比較多個評估結果"""
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("模型", style="cyan", width=30)
    table.add_column("正確性", style="green", width=15)
    table.add_column("長度", style="green", width=15)

    for model_name, results in all_results.items():
        # 這裡應該從實際結果中提取分數
        # 簡化展示
        table.add_row(model_name, "查看 UI", "查看 UI")

    console.print(table)
    console.print("\n[yellow]詳細比較請訪問 LangSmith UI 的 Experiments 頁面[/yellow]")


def custom_evaluator_examples():
    """展示更多自定義評估器示例"""
    console.print(Panel("[bold cyan]自定義評估器示例[/bold cyan]"))

    code = '''
# 1. 有害內容檢測
def toxicity_evaluator(run: Run, example: Example) -> dict:
    """檢測答案是否包含有害內容"""
    prediction = run.outputs.get("output", "")

    # 有害詞列表（簡化示例）
    toxic_words = ["offensive", "hate", "violence"]

    has_toxic = any(word in prediction.lower() for word in toxic_words)

    return {
        "key": "toxicity",
        "score": 0.0 if has_toxic else 1.0,
        "comment": "包含有害內容" if has_toxic else "內容安全"
    }


# 2. 事實準確性（需要知識庫）
def factuality_evaluator(run: Run, example: Example) -> dict:
    """檢查事實準確性"""
    # 這裡需要外部知識庫或事實檢查 API
    # 簡化示例
    return {
        "key": "factuality",
        "score": 0.9,
        "comment": "事實基本準確"
    }


# 3. 格式評估
def format_evaluator(run: Run, example: Example) -> dict:
    """評估答案格式"""
    prediction = run.outputs.get("output", "")

    # 檢查是否有適當的結構
    has_structure = "\\n" in prediction or "。" in prediction

    return {
        "key": "format",
        "score": 1.0 if has_structure else 0.5,
        "comment": "格式良好" if has_structure else "格式需改進"
    }


# 4. 相關性評估
def relevance_evaluator(run: Run, example: Example) -> dict:
    """評估答案相關性"""
    question = example.inputs.get("question", "")
    prediction = run.outputs.get("output", "")

    # 提取問題關鍵詞
    question_keywords = set(question.lower().split())

    # 檢查答案中是否包含問題關鍵詞
    prediction_words = set(prediction.lower().split())
    overlap = len(question_keywords & prediction_words)

    score = overlap / len(question_keywords) if question_keywords else 0.0

    return {
        "key": "relevance",
        "score": score,
        "comment": f"相關性：{score:.2%}"
    }
'''

    console.print(Panel(code, title="自定義評估器示例", border_style="blue"))


def evaluation_best_practices():
    """評估最佳實踐"""
    console.print(Panel("[bold cyan]評估最佳實踐[/bold cyan]"))

    practices = """
[bold green]評估最佳實踐：[/bold green]

1. [cyan]數據集質量[/cyan]
   ✓ 使用代表性的測試數據
   ✓ 包含邊緣情況
   ✓ 定期更新數據集
   ✗ 只用簡單的示例

2. [cyan]評估器設計[/cyan]
   ✓ 使用多個互補的評估器
   ✓ 結合自動和人工評估
   ✓ 考慮業務指標
   ✗ 只依賴單一指標

3. [cyan]持續評估[/cyan]
   ✓ 每次改動後都評估
   ✓ 建立基準線
   ✓ 追蹤性能趨勢
   ✗ 只在發布前評估

4. [cyan]結果分析[/cyan]
   ✓ 深入分析失敗案例
   ✓ 尋找模式和規律
   ✓ 迭代改進
   ✗ 只看總體分數

5. [cyan]評估成本[/cyan]
   ✓ 平衡評估質量和成本
   ✓ 對於 LLM 評估器，使用較便宜的模型
   ✓ 使用緩存避免重複評估
   ✗ 過度使用昂貴的評估方法

6. [cyan]團隊協作[/cyan]
   ✓ 共享評估結果
   ✓ 統一評估標準
   ✓ 建立評估流程
   ✗ 各自為政
    """

    console.print(practices)


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold green]LangSmith 評估系統[/bold green]",
        border_style="green"
    ))

    # 設置環境
    setup_environment()

    console.print("\n" + "="*60 + "\n")

    # 運行示例
    run_basic_evaluation()
    console.print("\n" + "="*60 + "\n")

    run_llm_evaluation()
    console.print("\n" + "="*60 + "\n")

    compare_models()
    console.print("\n" + "="*60 + "\n")

    # 展示自定義評估器
    custom_evaluator_examples()
    console.print("\n" + "="*60 + "\n")

    # 最佳實踐
    evaluation_best_practices()

    # 總結
    console.print(Panel("""
[bold green]評估系統總結[/bold green]

關鍵概念：

1. [cyan]評估器類型[/cyan]
   - 基於規則的評估器
   - LLM 評估器
   - 人工評估

2. [cyan]評估流程[/cyan]
   - 創建數據集
   - 定義評估器
   - 運行評估
   - 分析結果

3. [cyan]使用場景[/cyan]
   - 模型選擇
   - 提示工程
   - 性能監控
   - A/B 測試

下一步：
- 查看 05_數據集.py 深入了解數據集管理
- 查看 06_AB測試.py 學習如何進行 A/B 測試
- 訪問 LangSmith UI 查看詳細的評估結果

提示：
在 LangSmith UI 中可以：
- 查看每個示例的詳細結果
- 比較不同實驗
- 導出評估數據
- 設置自動化評估
    """, title="總結", border_style="green"))


if __name__ == "__main__":
    main()

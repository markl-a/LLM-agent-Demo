"""
LangSmith A/B 測試 - A/B Testing

這個示例展示如何：
1. 設置 A/B 測試實驗
2. 比較不同模型
3. 比較不同提示詞
4. 比較不同參數配置
5. 分析實驗結果
6. 做出數據驅動的決策

A/B 測試幫助你找到最佳配置。
"""

import os
from typing import Dict, Any, List
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langsmith import Client, evaluate
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def setup_environment():
    """配置環境"""
    load_dotenv()
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    if not os.getenv("LANGCHAIN_PROJECT"):
        os.environ["LANGCHAIN_PROJECT"] = "ab-testing-demo"
    console.print("[green]✓ 環境配置完成[/green]")


def create_test_dataset():
    """創建 A/B 測試用的數據集"""
    console.print("[cyan]創建測試數據集...[/cyan]")

    try:
        client = Client()
        dataset_name = "ab-test-dataset"

        # 刪除已存在的
        try:
            client.delete_dataset(dataset_name=dataset_name)
        except:
            pass

        # 創建數據集
        dataset = client.create_dataset(
            dataset_name=dataset_name,
            description="A/B 測試數據集"
        )

        # 添加多樣化的測試案例
        examples = [
            {
                "inputs": {"question": "什麼是人工智慧？"},
                "outputs": {"answer": "人工智慧是讓機器模擬人類智能的技術"}
            },
            {
                "inputs": {"question": "解釋機器學習"},
                "outputs": {"answer": "機器學習是 AI 的子領域，讓系統從數據中學習"}
            },
            {
                "inputs": {"question": "深度學習是什麼？"},
                "outputs": {"answer": "深度學習使用多層神經網絡處理複雜數據"}
            },
            {
                "inputs": {"question": "什麼是自然語言處理？"},
                "outputs": {"answer": "NLP 是讓計算機理解和生成人類語言的技術"}
            },
            {
                "inputs": {"question": "解釋神經網絡"},
                "outputs": {"answer": "神經網絡是模仿人腦結構的計算模型"}
            }
        ]

        for example in examples:
            client.create_example(
                dataset_id=dataset.id,
                inputs=example["inputs"],
                outputs=example["outputs"]
            )

        console.print(f"[green]✓ 創建數據集：{dataset_name}（{len(examples)} 個示例）[/green]")

        return dataset_name

    except Exception as e:
        console.print(f"[red]錯誤：{e}[/red]")
        return None


def test_different_models():
    """示例 1：比較不同模型"""
    console.print(Panel("[bold cyan]示例 1：比較不同模型[/bold cyan]"))

    try:
        dataset_name = create_test_dataset()
        if not dataset_name:
            return

        # 定義要測試的模型配置
        models = [
            {
                "name": "GPT-4o-mini",
                "model": "gpt-4o-mini",
                "temperature": 0.7
            },
            {
                "name": "GPT-3.5-turbo",
                "model": "gpt-3.5-turbo",
                "temperature": 0.7
            }
        ]

        # 共用的提示詞模板
        prompt = ChatPromptTemplate.from_template(
            "請用簡潔的一句話回答：{question}"
        )

        results = {}

        for model_config in models:
            console.print(f"\n[cyan]測試模型：{model_config['name']}[/cyan]")

            # 創建鏈
            llm = ChatOpenAI(
                model=model_config["model"],
                temperature=model_config["temperature"]
            )
            chain = prompt | llm | StrOutputParser()

            def predict(inputs: dict) -> dict:
                answer = chain.invoke(inputs)
                return {"output": answer}

            # 運行評估
            result = evaluate(
                predict,
                data=dataset_name,
                experiment_prefix=f"model-{model_config['name']}",
                description=f"測試 {model_config['name']}"
            )

            results[model_config["name"]] = result

            console.print(f"[green]✓ {model_config['name']} 測試完成[/green]")

        # 顯示比較
        console.print("\n[bold green]模型比較結果：[/bold green]")
        console.print("詳細結果請查看 LangSmith UI 的 Experiments 頁面")

        return results

    except Exception as e:
        console.print(f"[red]錯誤：{e}[/red]")
        import traceback
        console.print(traceback.format_exc())
        return None


def test_different_prompts():
    """示例 2：比較不同提示詞"""
    console.print(Panel("[bold cyan]示例 2：比較不同提示詞[/bold cyan]"))

    try:
        client = Client()
        dataset_name = "ab-test-dataset"

        # 定義不同的提示詞變體
        prompts = [
            {
                "name": "簡潔版",
                "template": "簡單回答：{question}"
            },
            {
                "name": "詳細版",
                "template": "請詳細解釋：{question}"
            },
            {
                "name": "專業版",
                "template": "作為專家，請專業地解釋：{question}"
            }
        ]

        # 使用相同的模型
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

        results = {}

        for prompt_config in prompts:
            console.print(f"\n[cyan]測試提示詞：{prompt_config['name']}[/cyan]")

            # 創建提示詞模板
            prompt = ChatPromptTemplate.from_template(prompt_config["template"])
            chain = prompt | llm | StrOutputParser()

            def predict(inputs: dict) -> dict:
                answer = chain.invoke(inputs)
                return {"output": answer}

            # 運行評估
            result = evaluate(
                predict,
                data=dataset_name,
                experiment_prefix=f"prompt-{prompt_config['name']}",
                description=f"測試提示詞：{prompt_config['name']}"
            )

            results[prompt_config["name"]] = result

            console.print(f"[green]✓ {prompt_config['name']} 測試完成[/green]")

        console.print("\n[bold green]提示詞比較結果：[/bold green]")
        console.print("詳細結果請查看 LangSmith UI")

        return results

    except Exception as e:
        console.print(f"[red]錯誤：{e}[/red]")
        import traceback
        console.print(traceback.format_exc())
        return None


def test_different_temperatures():
    """示例 3：比較不同溫度參數"""
    console.print(Panel("[bold cyan]示例 3：比較不同 Temperature[/bold cyan]"))

    try:
        dataset_name = "ab-test-dataset"

        # 測試不同的溫度值
        temperatures = [0.0, 0.3, 0.7, 1.0]

        prompt = ChatPromptTemplate.from_template("簡潔回答：{question}")

        results = {}

        for temp in temperatures:
            console.print(f"\n[cyan]測試 temperature={temp}[/cyan]")

            llm = ChatOpenAI(model="gpt-4o-mini", temperature=temp)
            chain = prompt | llm | StrOutputParser()

            def predict(inputs: dict) -> dict:
                answer = chain.invoke(inputs)
                return {"output": answer}

            result = evaluate(
                predict,
                data=dataset_name,
                experiment_prefix=f"temp-{temp}",
                description=f"Temperature={temp}"
            )

            results[f"temp_{temp}"] = result

            console.print(f"[green]✓ temperature={temp} 測試完成[/green]")

        console.print("\n[bold green]Temperature 比較：[/bold green]")
        console.print("""
溫度參數影響：
- 0.0：最確定性，輸出穩定
- 0.3：略微創意，保持一致性
- 0.7：平衡創意和一致性
- 1.0：最大創意，輸出多樣
        """)

        return results

    except Exception as e:
        console.print(f"[red]錯誤：{e}[/red]")
        import traceback
        console.print(traceback.format_exc())
        return None


def test_with_custom_evaluators():
    """示例 4：使用自定義評估器進行 A/B 測試"""
    console.print(Panel("[bold cyan]示例 4：自定義評估器 A/B 測試[/bold cyan]"))

    try:
        from langsmith.schemas import Run, Example

        # 自定義評估器：評估簡潔性
        def conciseness_evaluator(run: Run, example: Example) -> dict:
            output = run.outputs.get("output", "")
            length = len(output)

            # 理想長度：50-150 字符
            if 50 <= length <= 150:
                score = 1.0
            elif length < 50:
                score = length / 50
            else:
                score = max(0.0, 1.0 - (length - 150) / 150)

            return {
                "key": "conciseness",
                "score": score,
                "comment": f"長度：{length}"
            }

        # 自定義評估器：評估專業性（簡化版）
        def professionalism_evaluator(run: Run, example: Example) -> dict:
            output = run.outputs.get("output", "")

            # 檢查是否包含專業術語
            professional_terms = ["技術", "系統", "算法", "模型", "數據"]
            term_count = sum(1 for term in professional_terms if term in output)

            score = min(1.0, term_count / 2)

            return {
                "key": "professionalism",
                "score": score,
                "comment": f"專業術語數：{term_count}"
            }

        dataset_name = "ab-test-dataset"

        # 兩個配置
        configs = [
            {"name": "配置A", "temp": 0.3},
            {"name": "配置B", "temp": 0.7}
        ]

        for config in configs:
            console.print(f"\n[cyan]測試：{config['name']}[/cyan]")

            llm = ChatOpenAI(model="gpt-4o-mini", temperature=config["temp"])
            prompt = ChatPromptTemplate.from_template("專業地回答：{question}")
            chain = prompt | llm | StrOutputParser()

            def predict(inputs: dict) -> dict:
                answer = chain.invoke(inputs)
                return {"output": answer}

            result = evaluate(
                predict,
                data=dataset_name,
                evaluators=[conciseness_evaluator, professionalism_evaluator],
                experiment_prefix=f"custom-{config['name']}",
                description=config['name']
            )

            console.print(f"[green]✓ {config['name']} 完成[/green]")

        console.print("\n[yellow]使用自定義評估器可以針對特定業務指標進行優化[/yellow]")

    except Exception as e:
        console.print(f"[red]錯誤：{e}[/red]")
        import traceback
        console.print(traceback.format_exc())


def sequential_ab_test():
    """示例 5：順序 A/B 測試（迭代優化）"""
    console.print(Panel("[bold cyan]示例 5：順序 A/B 測試[/bold cyan]"))

    workflow = """
[bold green]順序 A/B 測試工作流：[/bold green]

[cyan]第一輪：基準測試[/cyan]
1. 使用當前生產配置作為基準（Variant A）
2. 運行評估獲得基準分數
3. 記錄關鍵指標

[cyan]第二輪：單一變量測試[/cyan]
1. 只改變一個參數（如 temperature）
2. 運行評估比較結果
3. 如果改進 → 採用新配置
4. 如果未改進 → 保持原配置

[cyan]第三輪：組合優化[/cyan]
1. 基於最佳單一配置
2. 測試多個參數組合
3. 找到最優組合

[cyan]第四輪：驗證測試[/cyan]
1. 使用獨立的驗證數據集
2. 確認改進是否一致
3. 避免過擬合

[bold yellow]示例代碼：[/bold yellow]

```python
# 第一輪：基準
baseline_result = evaluate(
    baseline_predict,
    data="test-dataset",
    experiment_prefix="round1-baseline"
)

# 第二輪：測試溫度
for temp in [0.3, 0.5, 0.7]:
    result = evaluate(
        create_predict(temp),
        data="test-dataset",
        experiment_prefix=f"round2-temp{temp}"
    )
    # 比較結果，選擇最佳

# 第三輪：測試提示詞（使用最佳溫度）
best_temp = 0.5
for prompt_variant in prompts:
    result = evaluate(
        create_predict(best_temp, prompt_variant),
        data="test-dataset",
        experiment_prefix=f"round3-{prompt_variant}"
    )

# 第四輪：驗證
final_result = evaluate(
    best_predict,
    data="validation-dataset",
    experiment_prefix="round4-validation"
)
```
    """

    console.print(workflow)


def analyze_ab_results():
    """分析 A/B 測試結果的方法"""
    console.print(Panel("[bold cyan]分析 A/B 測試結果[/bold cyan]"))

    analysis_guide = """
[bold green]結果分析指南：[/bold green]

[cyan]1. 查看 LangSmith UI[/cyan]
   - 進入 Experiments 頁面
   - 選擇要比較的實驗
   - 查看並排比較視圖

[cyan]2. 關鍵指標[/cyan]
   ✓ 準確性分數
   ✓ 平均延遲
   ✓ Token 成本
   ✓ 錯誤率
   ✓ 用戶滿意度（如果有）

[cyan]3. 統計顯著性[/cyan]
   - 確保樣本量足夠（建議 >30）
   - 查看分數分佈
   - 考慮方差和標準差
   - 不要只看平均值

[cyan]4. 成本效益分析[/cyan]
   - 性能提升 vs 成本增加
   - 延遲增加是否可接受
   - ROI 計算

[cyan]5. 失敗案例分析[/cyan]
   - 深入查看失敗的示例
   - 找出模式
   - 決定是否可接受

[cyan]6. 決策標準[/cyan]
   - 設定最小改進閾值（如 5%）
   - 考慮業務影響
   - 平衡多個指標

[bold yellow]使用 SDK 分析：[/bold yellow]

```python
from langsmith import Client

client = Client()

# 獲取實驗結果
experiments = client.list_projects(
    project_name_contains="experiment"
)

# 比較兩個實驗
exp_a = client.read_project(project_name="experiment-a")
exp_b = client.read_project(project_name="experiment-b")

# 獲取詳細 runs
runs_a = list(client.list_runs(project_name="experiment-a"))
runs_b = list(client.list_runs(project_name="experiment-b"))

# 計算統計
def calculate_stats(runs):
    scores = [run.feedback_stats.get("score", 0) for run in runs]
    return {
        "mean": sum(scores) / len(scores),
        "min": min(scores),
        "max": max(scores)
    }

stats_a = calculate_stats(runs_a)
stats_b = calculate_stats(runs_b)

print(f"Variant A: {stats_a}")
print(f"Variant B: {stats_b}")
```
    """

    console.print(analysis_guide)


def ab_testing_best_practices():
    """A/B 測試最佳實踐"""
    console.print(Panel("[bold cyan]A/B 測試最佳實踐[/bold cyan]"))

    practices = """
[bold green]A/B 測試最佳實踐：[/bold green]

1. [cyan]測試設計[/cyan]
   ✓ 一次只改變一個變量
   ✓ 使用相同的測試數據集
   ✓ 設定清晰的成功標準
   ✗ 同時改變多個變量

2. [cyan]樣本大小[/cyan]
   ✓ 確保足夠的樣本量（建議 >50）
   ✓ 包含多樣化的案例
   ✓ 測試邊緣情況
   ✗ 只用幾個示例

3. [cyan]評估指標[/cyan]
   ✓ 使用多個互補的指標
   ✓ 包含業務相關指標
   ✓ 考慮成本和性能
   ✗ 只關注一個指標

4. [cyan]實驗管理[/cyan]
   ✓ 使用描述性的實驗名稱
   ✓ 記錄實驗假設和結果
   ✓ 保持實驗結果用於參考
   ✗ 隨意刪除實驗

5. [cyan]迭代過程[/cyan]
   ✓ 從基準開始
   ✓ 逐步優化
   ✓ 驗證改進
   ✗ 一步到位

6. [cyan]生產部署[/cyan]
   ✓ 使用漸進式發布
   ✓ 監控實際性能
   ✓ 準備回滾方案
   ✗ 立即全面部署

7. [cyan]成本控制[/cyan]
   ✓ 使用較小的數據集進行初步測試
   ✓ 對於 LLM 評估器使用便宜的模型
   ✓ 利用緩存
   ✗ 不計成本地測試

8. [cyan]團隊協作[/cyan]
   ✓ 共享實驗結果
   ✓ 討論決策依據
   ✓ 建立標準流程
   ✗ 獨立決策
    """

    console.print(practices)


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold green]LangSmith A/B 測試[/bold green]",
        border_style="green"
    ))

    # 設置環境
    setup_environment()

    console.print("\n" + "="*60 + "\n")

    # 運行示例
    test_different_models()
    console.print("\n" + "="*60 + "\n")

    test_different_prompts()
    console.print("\n" + "="*60 + "\n")

    test_different_temperatures()
    console.print("\n" + "="*60 + "\n")

    test_with_custom_evaluators()
    console.print("\n" + "="*60 + "\n")

    sequential_ab_test()
    console.print("\n" + "="*60 + "\n")

    analyze_ab_results()
    console.print("\n" + "="*60 + "\n")

    ab_testing_best_practices()

    # 總結
    console.print(Panel("""
[bold green]A/B 測試總結[/bold green]

測試類型：
1. 模型比較：選擇最佳 LLM
2. 提示詞優化：找到最佳提示
3. 參數調優：優化 temperature 等參數
4. 組合測試：多變量優化

關鍵步驟：
1. ✓ 創建測試數據集
2. ✓ 定義評估指標
3. ✓ 運行對比實驗
4. ✓ 分析結果
5. ✓ 做出決策
6. ✓ 驗證和部署

成功要素：
- 清晰的測試假設
- 足夠的樣本量
- 合適的評估指標
- 統計顯著性
- 成本效益考慮

下一步：
- 查看 07_提示管理.py 學習 Prompt Hub
- 查看 09_成本分析.py 了解成本追蹤
- 在 LangSmith UI 中比較實驗結果
    """, title="總結", border_style="green"))


if __name__ == "__main__":
    main()

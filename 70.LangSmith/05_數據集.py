"""
LangSmith 數據集管理 - Datasets

這個示例展示如何：
1. 創建和管理數據集
2. 從追蹤創建數據集
3. 導入導出數據集
4. 數據集版本控制
5. 使用數據集進行測試
6. 數據集最佳實踐

數據集是評估和測試的基礎。
"""

import os
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
from langsmith import Client
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def setup_environment():
    """配置環境"""
    load_dotenv()
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    if not os.getenv("LANGCHAIN_PROJECT"):
        os.environ["LANGCHAIN_PROJECT"] = "dataset-demo"
    console.print("[green]✓ 環境配置完成[/green]")


def create_simple_dataset():
    """示例 1：創建簡單數據集"""
    console.print(Panel("[bold cyan]示例 1：創建簡單數據集[/bold cyan]"))

    try:
        client = Client()

        dataset_name = "simple-qa-dataset"

        # 刪除已存在的數據集
        try:
            client.delete_dataset(dataset_name=dataset_name)
            console.print("[yellow]刪除舊數據集[/yellow]")
        except:
            pass

        # 創建數據集
        dataset = client.create_dataset(
            dataset_name=dataset_name,
            description="簡單的問答數據集",
            data_type="kv"  # key-value 類型
        )

        console.print(f"[green]✓ 創建數據集：{dataset_name}[/green]")
        console.print(f"  ID: {dataset.id}")

        # 添加示例
        examples = [
            {
                "inputs": {"question": "什麼是 Python？"},
                "outputs": {"answer": "Python 是一種高級程式語言"}
            },
            {
                "inputs": {"question": "什麼是機器學習？"},
                "outputs": {"answer": "機器學習是 AI 的一個分支"}
            },
            {
                "inputs": {"question": "解釋深度學習"},
                "outputs": {"answer": "深度學習使用多層神經網絡"}
            }
        ]

        for i, example in enumerate(examples, 1):
            client.create_example(
                dataset_id=dataset.id,
                inputs=example["inputs"],
                outputs=example["outputs"]
            )
            console.print(f"[cyan]添加示例 {i}[/cyan]")

        console.print(f"\n[green]✓ 成功添加 {len(examples)} 個示例[/green]")

        return dataset

    except Exception as e:
        console.print(f"[red]錯誤：{e}[/red]")
        return None


def create_dataset_from_runs():
    """示例 2：從追蹤創建數據集"""
    console.print(Panel("[bold cyan]示例 2：從追蹤創建數據集[/bold cyan]"))

    try:
        client = Client()

        # 首先生成一些追蹤
        console.print("[cyan]生成示例追蹤...[/cyan]\n")

        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        prompt = ChatPromptTemplate.from_template("簡短回答：{question}")
        chain = prompt | llm | StrOutputParser()

        questions = [
            "什麼是雲計算？",
            "解釋 API",
            "什麼是數據庫？"
        ]

        for question in questions:
            result = chain.invoke({"question": question})
            console.print(f"Q: {question}")
            console.print(f"A: {result[:50]}...\n")

        console.print("[green]✓ 生成了 3 個追蹤[/green]")

        # 說明如何從 runs 創建數據集
        info = """
[bold yellow]從追蹤創建數據集的步驟：[/bold yellow]

1. 在 LangSmith UI 中：
   - 進入 Projects 頁面
   - 選擇包含追蹤的項目
   - 篩選並選擇想要的 runs
   - 點擊 "Add to Dataset" 按鈕
   - 選擇現有數據集或創建新數據集

2. 使用 SDK（需要 run_id）：

```python
from langsmith import Client

client = Client()

# 從特定 run 創建示例
client.create_example_from_run(
    run_id="your-run-id",
    dataset_id="your-dataset-id"
)

# 或批量添加
run_ids = ["run-id-1", "run-id-2", "run-id-3"]
for run_id in run_ids:
    client.create_example_from_run(
        run_id=run_id,
        dataset_id=dataset_id
    )
```

3. 優點：
   - 快速從實際運行中創建測試案例
   - 保留真實的輸入輸出
   - 可以選擇性添加（例如只添加成功的）
        """

        console.print(Panel(info, border_style="blue"))

    except Exception as e:
        console.print(f"[red]錯誤：{e}[/red]")


def create_dataset_from_csv():
    """示例 3：從 CSV 創建數據集"""
    console.print(Panel("[bold cyan]示例 3：從 CSV/JSON 創建數據集[/bold cyan]"))

    try:
        client = Client()

        # 準備數據
        data = [
            {
                "inputs": {"text": "這是一個測試"},
                "outputs": {"classification": "測試"}
            },
            {
                "inputs": {"text": "這是生產環境"},
                "outputs": {"classification": "生產"}
            },
            {
                "inputs": {"text": "開發中的功能"},
                "outputs": {"classification": "開發"}
            }
        ]

        dataset_name = "classification-dataset"

        # 刪除已存在的
        try:
            client.delete_dataset(dataset_name=dataset_name)
        except:
            pass

        # 創建數據集
        dataset = client.create_dataset(
            dataset_name=dataset_name,
            description="分類測試數據集"
        )

        console.print(f"[green]✓ 創建數據集：{dataset_name}[/green]")

        # 批量添加示例
        for item in data:
            client.create_example(
                dataset_id=dataset.id,
                inputs=item["inputs"],
                outputs=item["outputs"]
            )

        console.print(f"[green]✓ 添加了 {len(data)} 個示例[/green]")

        # 展示如何從 CSV 導入
        csv_example = """
[bold yellow]從 CSV 導入的代碼示例：[/bold yellow]

```python
import pandas as pd
from langsmith import Client

client = Client()

# 讀取 CSV
df = pd.read_csv("your_data.csv")

# 創建數據集
dataset = client.create_dataset(
    dataset_name="from-csv",
    description="從 CSV 導入"
)

# 添加示例
for _, row in df.iterrows():
    client.create_example(
        dataset_id=dataset.id,
        inputs={"question": row["question"]},
        outputs={"answer": row["answer"]}
    )
```

CSV 格式示例：
question,answer
什麼是 AI?,人工智慧是...
什麼是 ML?,機器學習是...
        """

        console.print(Panel(csv_example, border_style="blue"))

        return dataset

    except Exception as e:
        console.print(f"[red]錯誤：{e}[/red]")
        return None


def list_and_query_datasets():
    """示例 4：列出和查詢數據集"""
    console.print(Panel("[bold cyan]示例 4：列出和查詢數據集[/bold cyan]"))

    try:
        client = Client()

        # 列出所有數據集
        console.print("[cyan]所有數據集：[/cyan]\n")

        datasets = list(client.list_datasets())

        if not datasets:
            console.print("[yellow]沒有找到數據集[/yellow]")
            return

        # 創建表格
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("名稱", style="cyan", width=30)
        table.add_column("描述", style="white", width=30)
        table.add_column("示例數", style="green", width=10)
        table.add_column("創建時間", style="yellow", width=20)

        for dataset in datasets[:10]:  # 只顯示前 10 個
            # 獲取示例數量
            examples = list(client.list_examples(dataset_id=dataset.id))
            example_count = len(examples)

            table.add_row(
                dataset.name,
                dataset.description or "無描述",
                str(example_count),
                dataset.created_at.strftime("%Y-%m-%d %H:%M") if dataset.created_at else "N/A"
            )

        console.print(table)

        # 查詢特定數據集
        if datasets:
            dataset = datasets[0]
            console.print(f"\n[cyan]查詢數據集詳情：{dataset.name}[/cyan]\n")

            examples = list(client.list_examples(dataset_id=dataset.id, limit=3))

            for i, example in enumerate(examples, 1):
                console.print(f"[bold]示例 {i}:[/bold]")
                console.print(f"  輸入: {example.inputs}")
                console.print(f"  輸出: {example.outputs}")
                console.print()

    except Exception as e:
        console.print(f"[red]錯誤：{e}[/red]")


def update_dataset():
    """示例 5：更新數據集"""
    console.print(Panel("[bold cyan]示例 5：更新數據集[/bold cyan]"))

    try:
        client = Client()

        dataset_name = "updateable-dataset"

        # 創建數據集
        try:
            client.delete_dataset(dataset_name=dataset_name)
        except:
            pass

        dataset = client.create_dataset(
            dataset_name=dataset_name,
            description="可更新的數據集"
        )

        console.print(f"[green]✓ 創建數據集[/green]")

        # 添加初始示例
        example = client.create_example(
            dataset_id=dataset.id,
            inputs={"question": "原始問題"},
            outputs={"answer": "原始答案"}
        )

        console.print(f"[cyan]添加示例 ID: {example.id}[/cyan]")

        # 更新示例
        console.print("\n[cyan]更新示例...[/cyan]")

        client.update_example(
            example_id=example.id,
            inputs={"question": "更新後的問題"},
            outputs={"answer": "更新後的答案"}
        )

        console.print("[green]✓ 示例已更新[/green]")

        # 驗證更新
        updated = client.read_example(example.id)
        console.print(f"\n更新後的內容：")
        console.print(f"  輸入: {updated.inputs}")
        console.print(f"  輸出: {updated.outputs}")

        # 刪除示例
        console.print("\n[cyan]刪除示例...[/cyan]")
        client.delete_example(example.id)
        console.print("[green]✓ 示例已刪除[/green]")

    except Exception as e:
        console.print(f"[red]錯誤：{e}[/red]")


def export_import_dataset():
    """示例 6：導出和導入數據集"""
    console.print(Panel("[bold cyan]示例 6：導出和導入數據集[/bold cyan]"))

    try:
        client = Client()

        # 創建示例數據集
        dataset_name = "export-test"

        try:
            client.delete_dataset(dataset_name=dataset_name)
        except:
            pass

        dataset = client.create_dataset(
            dataset_name=dataset_name,
            description="用於導出測試"
        )

        # 添加示例
        examples_data = [
            {"inputs": {"q": "Q1"}, "outputs": {"a": "A1"}},
            {"inputs": {"q": "Q2"}, "outputs": {"a": "A2"}},
        ]

        for data in examples_data:
            client.create_example(
                dataset_id=dataset.id,
                inputs=data["inputs"],
                outputs=data["outputs"]
            )

        console.print(f"[green]✓ 創建測試數據集[/green]")

        # 導出數據集
        console.print("\n[cyan]導出數據集...[/cyan]")

        examples = list(client.list_examples(dataset_id=dataset.id))

        export_data = {
            "dataset_name": dataset.name,
            "description": dataset.description,
            "examples": [
                {
                    "inputs": example.inputs,
                    "outputs": example.outputs
                }
                for example in examples
            ]
        }

        # 保存到文件
        export_file = "/tmp/dataset_export.json"
        with open(export_file, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)

        console.print(f"[green]✓ 導出到：{export_file}[/green]")
        console.print(f"  包含 {len(export_data['examples'])} 個示例")

        # 導入數據集
        console.print("\n[cyan]導入數據集...[/cyan]")

        with open(export_file, "r", encoding="utf-8") as f:
            import_data = json.load(f)

        new_dataset_name = "imported-dataset"

        try:
            client.delete_dataset(dataset_name=new_dataset_name)
        except:
            pass

        new_dataset = client.create_dataset(
            dataset_name=new_dataset_name,
            description=import_data["description"]
        )

        for example in import_data["examples"]:
            client.create_example(
                dataset_id=new_dataset.id,
                inputs=example["inputs"],
                outputs=example["outputs"]
            )

        console.print(f"[green]✓ 導入完成：{new_dataset_name}[/green]")

    except Exception as e:
        console.print(f"[red]錯誤：{e}[/red]")
        import traceback
        console.print(traceback.format_exc())


def dataset_best_practices():
    """數據集最佳實踐"""
    console.print(Panel("[bold cyan]數據集最佳實踐[/bold cyan]"))

    practices = """
[bold green]數據集管理最佳實踐：[/bold green]

1. [cyan]命名規範[/cyan]
   ✓ 使用描述性名稱：product-qa-v1
   ✓ 包含版本號
   ✓ 使用一致的命名模式
   ✗ 使用模糊名稱：dataset1, test

2. [cyan]數據質量[/cyan]
   ✓ 確保輸入輸出格式一致
   ✓ 包含多樣化的案例
   ✓ 定期審查和更新
   ✗ 只有簡單的正面案例

3. [cyan]數據集大小[/cyan]
   ✓ 開發：10-50 個示例
   ✓ 測試：100-500 個示例
   ✓ 基準測試：500+ 個示例
   ✗ 過大或過小

4. [cyan]版本控制[/cyan]
   ✓ 為重要變更創建新版本
   ✓ 記錄變更歷史
   ✓ 保留舊版本用於對比
   ✗ 直接修改生產數據集

5. [cyan]組織結構[/cyan]
   ✓ 按功能劃分數據集
   ✓ 區分訓練/驗證/測試集
   ✓ 使用標籤分類
   ✗ 所有數據混在一起

6. [cyan]敏感數據[/cyan]
   ✓ 脫敏敏感信息
   ✓ 限制訪問權限
   ✓ 定期審計
   ✗ 包含真實的用戶數據

7. [cyan]持續改進[/cyan]
   ✓ 從生產失敗案例添加示例
   ✓ 定期評估數據集質量
   ✓ 收集團隊反饋
   ✗ 創建後不再更新

8. [cyan]文檔化[/cyan]
   ✓ 添加清晰的描述
   ✓ 記錄數據來源
   ✓ 說明預期用途
   ✗ 沒有任何說明
    """

    console.print(practices)


def dataset_workflow_example():
    """展示完整的數據集工作流"""
    console.print(Panel("[bold cyan]完整數據集工作流[/bold cyan]"))

    workflow = """
[bold green]推薦的數據集工作流：[/bold green]

[cyan]階段 1：初始創建[/cyan]
1. 收集真實用例
2. 創建小型初始數據集（10-20 個示例）
3. 手動驗證每個示例
4. 添加描述性元數據

[cyan]階段 2：迭代改進[/cyan]
1. 運行評估發現問題
2. 從失敗案例添加示例
3. 擴充邊緣案例
4. 達到 50-100 個示例

[cyan]階段 3：生產就緒[/cyan]
1. 建立穩定的基準數據集
2. 創建版本（v1.0）
3. 設置定期評估
4. 監控性能趨勢

[cyan]階段 4：持續維護[/cyan]
1. 每月審查數據集
2. 從生產追蹤添加案例
3. 移除過時的示例
4. 發布新版本（v1.1, v2.0等）

[bold yellow]自動化建議：[/bold yellow]

```python
# 定期從生產中採樣
def sample_production_cases():
    client = Client()

    # 獲取最近的成功和失敗案例
    runs = client.list_runs(
        project_name="production",
        filter='status="success" OR status="error"'
    )

    # 添加到數據集
    for run in runs[:10]:
        client.create_example_from_run(
            run_id=run.id,
            dataset_id="production-samples"
        )
```
    """

    console.print(workflow)


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold green]LangSmith 數據集管理[/bold green]",
        border_style="green"
    ))

    # 設置環境
    setup_environment()

    console.print("\n" + "="*60 + "\n")

    # 運行示例
    create_simple_dataset()
    console.print("\n" + "="*60 + "\n")

    create_dataset_from_runs()
    console.print("\n" + "="*60 + "\n")

    create_dataset_from_csv()
    console.print("\n" + "="*60 + "\n")

    list_and_query_datasets()
    console.print("\n" + "="*60 + "\n")

    update_dataset()
    console.print("\n" + "="*60 + "\n")

    export_import_dataset()
    console.print("\n" + "="*60 + "\n")

    # 最佳實踐
    dataset_best_practices()
    console.print("\n" + "="*60 + "\n")

    # 工作流示例
    dataset_workflow_example()

    # 總結
    console.print(Panel("""
[bold green]數據集管理總結[/bold green]

核心操作：
1. ✓ 創建數據集
2. ✓ 添加/更新/刪除示例
3. ✓ 查詢和列出數據集
4. ✓ 導出/導入數據集
5. ✓ 從追蹤創建示例

關鍵要點：
- 數據集是評估的基礎
- 保持數據集質量和相關性
- 使用版本控制
- 從實際使用中持續改進
- 妥善處理敏感數據

下一步：
- 查看 06_AB測試.py 學習使用數據集進行 A/B 測試
- 查看 04_評估系統.py 了解如何使用數據集評估
- 在 LangSmith UI 中管理和可視化數據集
    """, title="總結", border_style="green"))


if __name__ == "__main__":
    main()

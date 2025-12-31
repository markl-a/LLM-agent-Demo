"""
LangSmith 手動追蹤 - Manual Tracing

這個示例展示如何：
1. 使用 traceable 裝飾器手動追蹤函數
2. 創建自定義 spans
3. 追蹤非 LangChain 代碼
4. 嵌套追蹤
5. 錯誤處理和重試追蹤

手動追蹤適用於需要精確控制追蹤範圍的場景。
"""

import os
import time
from typing import List, Dict, Any
from dotenv import load_dotenv
from langsmith import Client, traceable
from langsmith.run_trees import RunTree
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress

console = Console()


def setup_environment():
    """配置環境"""
    load_dotenv()
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    if not os.getenv("LANGCHAIN_PROJECT"):
        os.environ["LANGCHAIN_PROJECT"] = "manual-tracing-demo"
    console.print("[green]✓ 環境配置完成[/green]")


# 示例 1：使用 @traceable 裝飾器
@traceable(name="數據處理流程")
def process_data(data: List[str]) -> List[str]:
    """
    處理數據的簡單函數
    使用 @traceable 裝飾器自動追蹤
    """
    console.print(f"[cyan]處理 {len(data)} 條數據...[/cyan]")

    # 模擬數據處理
    time.sleep(0.5)

    processed = [item.upper() for item in data]
    return processed


@traceable(name="數據驗證")
def validate_data(data: List[str]) -> bool:
    """驗證數據有效性"""
    console.print("[cyan]驗證數據...[/cyan]")

    # 模擬驗證邏輯
    time.sleep(0.3)

    is_valid = all(len(item) > 0 for item in data)
    return is_valid


def traceable_decorator_example():
    """示例 1：traceable 裝飾器"""
    console.print(Panel("[bold cyan]示例 1：@traceable 裝飾器[/bold cyan]"))

    try:
        data = ["hello", "world", "langsmith"]

        # 驗證數據
        is_valid = validate_data(data)
        console.print(f"數據有效：{is_valid}")

        # 處理數據
        result = process_data(data)
        console.print(f"[green]處理結果：{result}[/green]")

        console.print(
            "\n[yellow]提示：兩個函數調用都被自動追蹤[/yellow]"
        )

        return result

    except Exception as e:
        console.print(f"[red]錯誤：{e}[/red]")
        return None


# 示例 2：追蹤帶參數的函數
@traceable(
    name="LLM 調用",
    metadata={"model": "gpt-4o-mini"},
    tags=["llm", "custom"]
)
def call_llm(prompt: str, temperature: float = 0.7) -> str:
    """
    調用 LLM 的函數
    使用 metadata 和 tags 添加額外信息
    """
    console.print(f"[cyan]調用 LLM (temperature={temperature})...[/cyan]")

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=temperature)
    result = llm.invoke(prompt)

    return result.content


def traceable_with_metadata_example():
    """示例 2：帶元數據的追蹤"""
    console.print(Panel("[bold cyan]示例 2：帶元數據的追蹤[/bold cyan]"))

    try:
        prompts = [
            ("介紹量子計算", 0.3),
            ("寫一首詩", 0.9),
        ]

        for prompt, temp in prompts:
            console.print(f"\n處理：{prompt}")
            result = call_llm(prompt, temperature=temp)
            console.print(f"[green]結果：{result[:100]}...[/green]")

        console.print(
            "\n[yellow]提示：每個調用都記錄了 temperature 參數[/yellow]"
        )

    except Exception as e:
        console.print(f"[red]錯誤：{e}[/red]")


# 示例 3：嵌套追蹤
@traceable(name="子任務A")
def subtask_a(data: str) -> str:
    """子任務 A"""
    console.print("[cyan]執行子任務 A[/cyan]")
    time.sleep(0.2)
    return f"A-{data}"


@traceable(name="子任務B")
def subtask_b(data: str) -> str:
    """子任務 B"""
    console.print("[cyan]執行子任務 B[/cyan]")
    time.sleep(0.2)
    return f"B-{data}"


@traceable(name="主任務")
def main_task(data: str) -> Dict[str, str]:
    """
    主任務，包含多個子任務
    展示嵌套追蹤
    """
    console.print("[cyan]執行主任務[/cyan]")

    # 調用子任務
    result_a = subtask_a(data)
    result_b = subtask_b(data)

    return {
        "task_a": result_a,
        "task_b": result_b,
        "combined": f"{result_a}+{result_b}"
    }


def nested_tracing_example():
    """示例 3：嵌套追蹤"""
    console.print(Panel("[bold cyan]示例 3：嵌套追蹤[/bold cyan]"))

    try:
        result = main_task("test")
        console.print(f"\n[green]結果：{result}[/green]")

        console.print(
            "\n[yellow]提示：在 LangSmith UI 中可以看到完整的調用層次[/yellow]"
        )

        return result

    except Exception as e:
        console.print(f"[red]錯誤：{e}[/red]")
        return None


# 示例 4：使用 RunTree 手動控制
def manual_run_tree_example():
    """示例 4：使用 RunTree 手動控制追蹤"""
    console.print(Panel("[bold cyan]示例 4：RunTree 手動控制[/bold cyan]"))

    try:
        client = Client()

        # 創建根 run
        root_run = RunTree(
            name="自定義流程",
            run_type="chain",
            inputs={"task": "處理用戶請求"},
            project_name=os.getenv("LANGCHAIN_PROJECT"),
            client=client
        )

        console.print("[cyan]開始自定義流程...[/cyan]")

        # 創建子 run 1
        child_run_1 = root_run.create_child(
            name="數據預處理",
            run_type="tool",
            inputs={"data": "raw_data"}
        )

        # 模擬處理
        time.sleep(0.3)
        preprocessed_data = "processed_data"

        # 結束子 run 1
        child_run_1.end(outputs={"result": preprocessed_data})
        child_run_1.post()

        console.print("[green]✓ 數據預處理完成[/green]")

        # 創建子 run 2
        child_run_2 = root_run.create_child(
            name="LLM 處理",
            run_type="llm",
            inputs={"data": preprocessed_data}
        )

        # 模擬 LLM 調用
        time.sleep(0.5)
        llm_result = "LLM 輸出結果"

        # 結束子 run 2
        child_run_2.end(outputs={"result": llm_result})
        child_run_2.post()

        console.print("[green]✓ LLM 處理完成[/green]")

        # 結束根 run
        root_run.end(outputs={"final_result": llm_result})
        root_run.post()

        console.print(
            "\n[yellow]提示：RunTree 提供了最細粒度的控制[/yellow]"
        )

        return llm_result

    except Exception as e:
        console.print(f"[red]錯誤：{e}[/red]")
        return None


# 示例 5：錯誤處理和追蹤
@traceable(name="可能失敗的任務")
def risky_task(value: int) -> str:
    """可能拋出異常的任務"""
    console.print(f"[cyan]執行任務，輸入值：{value}[/cyan]")

    if value < 0:
        raise ValueError("值不能為負數")

    if value > 100:
        raise ValueError("值不能大於 100")

    time.sleep(0.2)
    return f"成功處理值：{value}"


def error_tracking_example():
    """示例 5：錯誤追蹤"""
    console.print(Panel("[bold cyan]示例 5：錯誤追蹤[/bold cyan]"))

    test_values = [50, -10, 150, 75]

    for value in test_values:
        try:
            console.print(f"\n測試值：{value}")
            result = risky_task(value)
            console.print(f"[green]✓ {result}[/green]")

        except ValueError as e:
            console.print(f"[red]✗ 錯誤：{e}[/red]")
            # 錯誤會自動被追蹤到 LangSmith

    console.print(
        "\n[yellow]提示：所有錯誤都被記錄在 LangSmith 中，包括堆棧跟蹤[/yellow]"
    )


# 示例 6：帶重試的追蹤
@traceable(name="帶重試的任務")
def task_with_retry(attempt: int, max_retries: int = 3) -> str:
    """帶重試邏輯的任務"""
    console.print(f"[cyan]嘗試 {attempt}/{max_retries}[/cyan]")

    # 模擬前兩次失敗
    if attempt < 2:
        time.sleep(0.2)
        raise Exception(f"嘗試 {attempt} 失敗")

    time.sleep(0.3)
    return "任務成功完成"


def retry_tracking_example():
    """示例 6：重試追蹤"""
    console.print(Panel("[bold cyan]示例 6：重試追蹤[/bold cyan]"))

    max_retries = 3
    attempt = 0

    while attempt < max_retries:
        try:
            result = task_with_retry(attempt, max_retries)
            console.print(f"[green]✓ {result}[/green]")
            break

        except Exception as e:
            console.print(f"[yellow]⚠ {e}[/yellow]")
            attempt += 1

            if attempt >= max_retries:
                console.print("[red]✗ 達到最大重試次數[/red]")

    console.print(
        "\n[yellow]提示：每次重試都會被單獨追蹤[/yellow]"
    )


# 示例 7：批量操作追蹤
@traceable(name="批量處理")
def batch_process(items: List[str]) -> List[str]:
    """批量處理多個項目"""
    console.print(f"[cyan]批量處理 {len(items)} 個項目[/cyan]")

    results = []

    with Progress() as progress:
        task = progress.add_task("[cyan]處理中...", total=len(items))

        for item in items:
            # 每個項目可以有自己的子追蹤
            result = process_single_item(item)
            results.append(result)
            progress.update(task, advance=1)

    return results


@traceable(name="處理單個項目")
def process_single_item(item: str) -> str:
    """處理單個項目"""
    time.sleep(0.1)
    return f"processed-{item}"


def batch_tracking_example():
    """示例 7：批量操作追蹤"""
    console.print(Panel("[bold cyan]示例 7：批量操作追蹤[/bold cyan]"))

    try:
        items = [f"item-{i}" for i in range(5)]
        results = batch_process(items)

        console.print(f"\n[green]處理完成：{len(results)} 個項目[/green]")
        console.print(
            "\n[yellow]提示：批量操作和每個子項目都被追蹤[/yellow]"
        )

        return results

    except Exception as e:
        console.print(f"[red]錯誤：{e}[/red]")
        return None


# 示例 8：混合使用自動和手動追蹤
@traceable(name="混合追蹤流程")
def hybrid_tracing_example():
    """示例 8：混合使用自動和手動追蹤"""
    console.print(Panel("[bold cyan]示例 8：混合追蹤[/bold cyan]"))

    try:
        # 手動追蹤的部分
        console.print("\n[cyan]1. 手動追蹤：數據準備[/cyan]")
        data = process_data(["hello", "world"])

        # 自動追蹤的 LangChain 部分
        console.print("\n[cyan]2. 自動追蹤：LangChain 調用[/cyan]")
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        prompt = ChatPromptTemplate.from_template("總結這些詞：{words}")
        chain = prompt | llm | StrOutputParser()

        result = chain.invoke({"words": ", ".join(data)})

        console.print(f"\n[green]最終結果：{result}[/green]")
        console.print(
            "\n[yellow]提示：手動和自動追蹤無縫結合[/yellow]"
        )

        return result

    except Exception as e:
        console.print(f"[red]錯誤：{e}[/red]")
        return None


def tracing_best_practices():
    """追蹤最佳實踐"""
    console.print(Panel("[bold cyan]手動追蹤最佳實踐[/bold cyan]"))

    practices = """
[bold green]最佳實踐：[/bold green]

1. [cyan]使用描述性名稱[/cyan]
   ✓ run_name="用戶查詢-搜索-排序"
   ✗ run_name="task1"

2. [cyan]添加有意義的元數據[/cyan]
   ✓ metadata={"user_id": "123", "query_type": "search"}
   ✗ metadata={}

3. [cyan]合理使用標籤[/cyan]
   ✓ tags=["production", "high-priority", "user-facing"]
   ✗ tags=["tag1", "tag2"]

4. [cyan]錯誤處理[/cyan]
   ✓ 使用 try-except，讓錯誤被追蹤
   ✗ 忽略異常

5. [cyan]嵌套結構[/cyan]
   ✓ 使用清晰的層次結構
   ✗ 所有操作都在頂層

6. [cyan]性能考慮[/cyan]
   ✓ 追蹤關鍵操作
   ✗ 過度追蹤導致性能下降

7. [cyan]輸入輸出[/cyan]
   ✓ 記錄完整的輸入輸出
   ✗ 丟失重要信息

8. [cyan]一致性[/cyan]
   ✓ 團隊統一命名規範
   ✗ 每個人用不同風格
    """

    console.print(practices)


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold green]LangSmith 手動追蹤[/bold green]",
        border_style="green"
    ))

    # 設置環境
    setup_environment()

    console.print("\n" + "="*60 + "\n")

    # 運行示例
    traceable_decorator_example()
    console.print("\n" + "="*60 + "\n")

    traceable_with_metadata_example()
    console.print("\n" + "="*60 + "\n")

    nested_tracing_example()
    console.print("\n" + "="*60 + "\n")

    manual_run_tree_example()
    console.print("\n" + "="*60 + "\n")

    error_tracking_example()
    console.print("\n" + "="*60 + "\n")

    retry_tracking_example()
    console.print("\n" + "="*60 + "\n")

    batch_tracking_example()
    console.print("\n" + "="*60 + "\n")

    hybrid_tracing_example()
    console.print("\n" + "="*60 + "\n")

    # 最佳實踐
    tracing_best_practices()

    # 總結
    console.print(Panel("""
[bold green]手動追蹤總結[/bold green]

追蹤方式對比：

1. [cyan]@traceable 裝飾器[/cyan]
   - 最簡單的手動追蹤方式
   - 適合追蹤函數調用
   - 自動捕獲輸入輸出

2. [cyan]RunTree[/cyan]
   - 最細粒度的控制
   - 適合複雜的自定義流程
   - 需要手動管理生命週期

3. [cyan]RunnableConfig[/cyan]
   - 用於 LangChain 組件
   - 添加元數據和標籤
   - 與自動追蹤配合使用

選擇建議：
✓ 簡單函數：使用 @traceable
✓ LangChain 鏈：使用自動追蹤 + RunnableConfig
✓ 複雜流程：使用 RunTree
✓ 混合場景：結合使用

下一步：
- 查看 04_評估系統.py 學習如何評估追蹤結果
- 查看 05_數據集.py 了解數據集管理
    """, title="總結", border_style="green"))


if __name__ == "__main__":
    main()

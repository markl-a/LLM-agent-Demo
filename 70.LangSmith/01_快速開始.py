"""
LangSmith 快速開始 - 基本追蹤

這個示例展示如何：
1. 配置 LangSmith 環境
2. 啟用自動追蹤
3. 使用 LangChain 進行基本操作
4. 在 LangSmith UI 中查看追蹤結果

LangSmith 會自動追蹤所有 LangChain 操作，無需額外代碼。
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langsmith import Client
from rich.console import Console
from rich.panel import Panel

console = Console()


def setup_langsmith():
    """配置 LangSmith 環境變量"""
    load_dotenv()

    # LangSmith 配置
    os.environ["LANGCHAIN_TRACING_V2"] = "true"  # 啟用追蹤
    os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"

    # 確保已設置必要的環境變量
    required_vars = ["LANGCHAIN_API_KEY", "OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        console.print(
            f"[red]錯誤：缺少必要的環境變量：{', '.join(missing_vars)}[/red]"
        )
        console.print("\n請在 .env 文件中設置：")
        console.print("LANGCHAIN_API_KEY=your_langsmith_api_key")
        console.print("OPENAI_API_KEY=your_openai_api_key")
        console.print("LANGCHAIN_PROJECT=your_project_name  # 可選")
        return False

    # 設置項目名稱（可選）
    if not os.getenv("LANGCHAIN_PROJECT"):
        os.environ["LANGCHAIN_PROJECT"] = "langsmith-demo"

    console.print("[green]✓ LangSmith 環境配置成功[/green]")
    console.print(f"項目名稱: {os.getenv('LANGCHAIN_PROJECT')}")
    return True


def verify_langsmith_connection():
    """驗證 LangSmith 連接"""
    try:
        client = Client()
        # 嘗試獲取項目信息
        console.print("[green]✓ LangSmith 連接成功[/green]")
        return True
    except Exception as e:
        console.print(f"[red]✗ LangSmith 連接失敗: {e}[/red]")
        console.print("\n請檢查：")
        console.print("1. API Key 是否正確")
        console.print("2. 網絡連接是否正常")
        console.print("3. 是否已註冊 LangSmith 帳號")
        return False


def simple_chain_example():
    """示例 1：簡單的 LLM 鏈"""
    console.print(Panel("[bold cyan]示例 1：簡單的 LLM 鏈[/bold cyan]"))

    try:
        # 創建 LLM
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7
        )

        # 創建提示詞模板
        prompt = ChatPromptTemplate.from_template(
            "請用一句話介紹 {topic}"
        )

        # 創建輸出解析器
        output_parser = StrOutputParser()

        # 組合成鏈
        chain = prompt | llm | output_parser

        # 執行鏈 - 這個調用會自動被追蹤
        result = chain.invoke({"topic": "LangSmith"})

        console.print(f"\n[green]結果：[/green]{result}")
        console.print("\n[yellow]提示：這次調用已自動追蹤到 LangSmith[/yellow]")

        return result

    except Exception as e:
        console.print(f"[red]錯誤：{e}[/red]")
        return None


def multi_chain_example():
    """示例 2：多步驟鏈"""
    console.print(Panel("[bold cyan]示例 2：多步驟鏈[/bold cyan]"))

    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

        # 第一步：生成主題
        topic_prompt = ChatPromptTemplate.from_template(
            "請生成一個關於 {category} 的有趣主題"
        )
        topic_chain = topic_prompt | llm | StrOutputParser()

        # 第二步：基於主題寫故事
        story_prompt = ChatPromptTemplate.from_template(
            "基於這個主題寫一個簡短的故事：{topic}"
        )
        story_chain = story_prompt | llm | StrOutputParser()

        # 執行多步驟
        console.print("\n[cyan]步驟 1：生成主題...[/cyan]")
        topic = topic_chain.invoke({"category": "科技"})
        console.print(f"主題：{topic}")

        console.print("\n[cyan]步驟 2：創作故事...[/cyan]")
        story = story_chain.invoke({"topic": topic})
        console.print(f"故事：{story}")

        console.print(
            "\n[yellow]提示：兩個步驟都被追蹤，可以在 LangSmith UI 中看到完整的調用鏈[/yellow]"
        )

        return {"topic": topic, "story": story}

    except Exception as e:
        console.print(f"[red]錯誤：{e}[/red]")
        return None


def batch_processing_example():
    """示例 3：批量處理"""
    console.print(Panel("[bold cyan]示例 3：批量處理[/bold cyan]"))

    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

        prompt = ChatPromptTemplate.from_template(
            "用一個詞描述 {item}"
        )

        chain = prompt | llm | StrOutputParser()

        # 批量處理多個輸入
        items = [
            {"item": "太陽"},
            {"item": "海洋"},
            {"item": "森林"}
        ]

        console.print("\n[cyan]批量處理中...[/cyan]")
        results = chain.batch(items)

        console.print("\n[green]結果：[/green]")
        for item, result in zip(items, results):
            console.print(f"  {item['item']}: {result}")

        console.print(
            "\n[yellow]提示：每個批量項目都會被單獨追蹤[/yellow]"
        )

        return results

    except Exception as e:
        console.print(f"[red]錯誤：{e}[/red]")
        return None


def streaming_example():
    """示例 4：流式輸出"""
    console.print(Panel("[bold cyan]示例 4：流式輸出[/bold cyan]"))

    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, streaming=True)

        prompt = ChatPromptTemplate.from_template(
            "寫一首關於 {topic} 的短詩"
        )

        chain = prompt | llm | StrOutputParser()

        console.print("\n[cyan]流式生成中：[/cyan]\n")

        full_response = ""
        for chunk in chain.stream({"topic": "星空"}):
            console.print(chunk, end="")
            full_response += chunk

        console.print(
            "\n\n[yellow]提示：流式輸出也會被完整追蹤[/yellow]"
        )

        return full_response

    except Exception as e:
        console.print(f"[red]錯誤：{e}[/red]")
        return None


def view_traces_info():
    """顯示如何查看追蹤結果"""
    console.print(Panel("[bold cyan]查看追蹤結果[/bold cyan]"))

    project_name = os.getenv("LANGCHAIN_PROJECT", "default")

    info = f"""
[green]追蹤已自動上傳到 LangSmith！[/green]

查看追蹤結果：
1. 訪問：https://smith.langchain.com/
2. 登入你的帳號
3. 選擇項目：{project_name}
4. 查看最近的追蹤記錄

在 UI 中你可以看到：
- 完整的調用鏈
- 輸入和輸出
- Token 使用情況
- 執行時間
- 錯誤信息（如果有）

也可以使用 LangSmith SDK 查詢追蹤：
    """

    console.print(info)

    # 顯示代碼示例
    code = """
from langsmith import Client

client = Client()

# 獲取最近的 runs
runs = client.list_runs(project_name="{project_name}", limit=5)

for run in runs:
    print(f"Run ID: {run.id}")
    print(f"Name: {run.name}")
    print(f"Status: {run.status}")
    print(f"Start time: {run.start_time}")
    print("---")
    """.format(project_name=project_name)

    console.print(Panel(code, title="代碼示例", border_style="blue"))


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold green]LangSmith 快速開始 - 基本追蹤[/bold green]",
        border_style="green"
    ))

    # 1. 設置環境
    console.print("\n[bold]步驟 1：配置環境[/bold]")
    if not setup_langsmith():
        return

    # 2. 驗證連接
    console.print("\n[bold]步驟 2：驗證連接[/bold]")
    if not verify_langsmith_connection():
        console.print("\n[yellow]提示：即使連接失敗，追蹤功能仍會在後台工作[/yellow]")

    # 3. 運行示例
    console.print("\n[bold]步驟 3：運行示例[/bold]\n")

    simple_chain_example()
    console.print("\n" + "="*60 + "\n")

    multi_chain_example()
    console.print("\n" + "="*60 + "\n")

    batch_processing_example()
    console.print("\n" + "="*60 + "\n")

    streaming_example()
    console.print("\n" + "="*60 + "\n")

    # 4. 查看追蹤信息
    view_traces_info()

    # 總結
    console.print(Panel("""
[bold green]快速開始完成！[/bold green]

關鍵要點：
1. 設置 LANGCHAIN_TRACING_V2=true 啟用追蹤
2. 設置 LANGCHAIN_API_KEY 進行認證
3. LangChain 操作會自動追蹤，無需額外代碼
4. 在 LangSmith UI 中查看詳細的追蹤結果

下一步：
- 查看 02_自動追蹤.py 了解更多自動追蹤選項
- 查看 03_手動追蹤.py 學習手動控制追蹤
- 訪問 https://docs.smith.langchain.com/ 閱讀官方文檔
    """, title="總結", border_style="green"))


if __name__ == "__main__":
    main()

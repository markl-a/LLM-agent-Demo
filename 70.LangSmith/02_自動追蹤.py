"""
LangSmith 自動追蹤 - Auto-tracing

這個示例展示如何：
1. 配置不同的追蹤選項
2. 使用環境變量控制追蹤行為
3. 追蹤自定義元數據和標籤
4. 過濾和採樣追蹤
5. 處理敏感信息

LangSmith 的自動追蹤功能強大且靈活。
"""

import os
import time
from typing import Dict, Any
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnableConfig
from langsmith import Client
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def setup_basic_tracing():
    """配置基本的自動追蹤"""
    load_dotenv()

    # 基本配置
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"

    # 設置項目名稱
    if not os.getenv("LANGCHAIN_PROJECT"):
        os.environ["LANGCHAIN_PROJECT"] = "auto-tracing-demo"

    console.print("[green]✓ 基本追蹤配置完成[/green]")


def tracing_with_metadata():
    """示例 1：追蹤時添加元數據"""
    console.print(Panel("[bold cyan]示例 1：添加元數據[/bold cyan]"))

    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        prompt = ChatPromptTemplate.from_template("介紹 {topic}")
        chain = prompt | llm | StrOutputParser()

        # 使用 RunnableConfig 添加元數據
        config = RunnableConfig(
            metadata={
                "user_id": "user_123",
                "session_id": "session_456",
                "environment": "development",
                "version": "1.0.0"
            },
            tags=["demo", "metadata", "test"]
        )

        console.print("\n[cyan]執行帶元數據的調用...[/cyan]")
        result = chain.invoke(
            {"topic": "人工智慧"},
            config=config
        )

        console.print(f"\n[green]結果：[/green]{result}")
        console.print(
            "\n[yellow]提示：元數據和標籤已添加到追蹤中，可在 UI 中過濾和搜索[/yellow]"
        )

        return result

    except Exception as e:
        console.print(f"[red]錯誤：{e}[/red]")
        return None


def tracing_with_custom_name():
    """示例 2：自定義 run 名稱"""
    console.print(Panel("[bold cyan]示例 2：自定義 Run 名稱[/bold cyan]"))

    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        prompt = ChatPromptTemplate.from_template("翻譯成英文：{text}")
        chain = prompt | llm | StrOutputParser()

        # 設置自定義 run 名稱
        config = RunnableConfig(
            run_name="中英翻譯-用戶請求",
            tags=["translation", "zh-to-en"]
        )

        console.print("\n[cyan]執行翻譯...[/cyan]")
        result = chain.invoke(
            {"text": "你好，世界"},
            config=config
        )

        console.print(f"\n[green]翻譯結果：[/green]{result}")
        console.print(
            "\n[yellow]提示：在 LangSmith UI 中會顯示自定義的 run 名稱[/yellow]"
        )

        return result

    except Exception as e:
        console.print(f"[red]錯誤：{e}[/red]")
        return None


def conditional_tracing():
    """示例 3：條件性追蹤"""
    console.print(Panel("[bold cyan]示例 3：條件性追蹤[/bold cyan]"))

    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        prompt = ChatPromptTemplate.from_template("總結：{content}")
        chain = prompt | llm | StrOutputParser()

        # 模擬不同的用戶類型
        users = [
            {"id": "premium_user", "trace": True},
            {"id": "free_user", "trace": False},
            {"id": "test_user", "trace": True}
        ]

        results = []
        for user in users:
            console.print(f"\n[cyan]處理用戶：{user['id']}[/cyan]")

            # 根據條件啟用/禁用追蹤
            if user["trace"]:
                # 啟用追蹤
                config = RunnableConfig(
                    metadata={"user_id": user["id"]},
                    tags=["traced_user"]
                )
            else:
                # 禁用追蹤（通過不使用 LangSmith）
                # 注意：需要臨時禁用環境變量
                old_value = os.environ.get("LANGCHAIN_TRACING_V2")
                os.environ["LANGCHAIN_TRACING_V2"] = "false"
                config = None

            result = chain.invoke(
                {"content": f"這是 {user['id']} 的內容"},
                config=config
            )

            # 恢復追蹤設置
            if not user["trace"] and old_value:
                os.environ["LANGCHAIN_TRACING_V2"] = old_value

            console.print(f"追蹤狀態：{'✓ 已追蹤' if user['trace'] else '✗ 未追蹤'}")
            results.append(result)

        console.print(
            "\n[yellow]提示：可以根據用戶類型或其他條件選擇性追蹤[/yellow]"
        )

        return results

    except Exception as e:
        console.print(f"[red]錯誤：{e}[/red]")
        return None


def sampling_traces():
    """示例 4：採樣追蹤（減少追蹤量）"""
    console.print(Panel("[bold cyan]示例 4：採樣追蹤[/bold cyan]"))

    try:
        import random

        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        prompt = ChatPromptTemplate.from_template("簡短回答：{question}")
        chain = prompt | llm | StrOutputParser()

        # 設置採樣率（例如：只追蹤 20% 的請求）
        sampling_rate = 0.2

        console.print(f"\n[cyan]採樣率：{sampling_rate * 100}%[/cyan]\n")

        traced_count = 0
        total_count = 10

        for i in range(total_count):
            # 隨機決定是否追蹤
            should_trace = random.random() < sampling_rate

            if should_trace:
                config = RunnableConfig(
                    metadata={"request_id": f"req_{i}", "sampled": True},
                    tags=["sampled"]
                )
                traced_count += 1
            else:
                # 禁用追蹤
                old_value = os.environ.get("LANGCHAIN_TRACING_V2")
                os.environ["LANGCHAIN_TRACING_V2"] = "false"
                config = None

            result = chain.invoke(
                {"question": f"問題 {i}"},
                config=config
            )

            # 恢復設置
            if not should_trace and old_value:
                os.environ["LANGCHAIN_TRACING_V2"] = old_value

            status = "✓" if should_trace else "✗"
            console.print(f"請求 {i}: {status}")

        console.print(
            f"\n[green]總請求數：{total_count}[/green]"
        )
        console.print(
            f"[green]追蹤數量：{traced_count}[/green]"
        )
        console.print(
            "\n[yellow]提示：採樣追蹤可以在高流量場景下減少成本[/yellow]"
        )

    except Exception as e:
        console.print(f"[red]錯誤：{e}[/red]")


def hiding_sensitive_data():
    """示例 5：隱藏敏感信息"""
    console.print(Panel("[bold cyan]示例 5：隱藏敏感信息[/bold cyan]"))

    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

        # 創建一個包含敏感信息的提示
        prompt = ChatPromptTemplate.from_template(
            """
            用戶信息：
            姓名：{name}
            郵箱：{email}
            信用卡：{credit_card}

            請生成一個歡迎消息。
            """
        )

        chain = prompt | llm | StrOutputParser()

        # 實際數據
        user_data = {
            "name": "張三",
            "email": "zhang@example.com",
            "credit_card": "1234-5678-9012-3456"
        }

        # 配置追蹤，添加警告標籤
        config = RunnableConfig(
            metadata={
                "contains_pii": True,  # PII = Personally Identifiable Information
                "data_classification": "sensitive"
            },
            tags=["sensitive", "pii"],
            run_name="敏感數據處理"
        )

        console.print("\n[cyan]處理包含敏感信息的請求...[/cyan]")
        result = chain.invoke(user_data, config=config)

        console.print(f"\n[green]結果：[/green]{result}")

        console.print("\n[red]⚠️  最佳實踐：[/red]")
        console.print("1. 在發送到 LLM 前脫敏數據")
        console.print("2. 使用標籤標記敏感追蹤")
        console.print("3. 定期審查和清理敏感追蹤")
        console.print("4. 考慮使用本地追蹤解決方案（如 Langfuse 自託管）")

        # 展示如何脫敏
        console.print("\n[cyan]脫敏示例：[/cyan]")

        def mask_sensitive_data(data: Dict[str, Any]) -> Dict[str, Any]:
            """脫敏敏感數據"""
            masked = data.copy()
            if "credit_card" in masked:
                masked["credit_card"] = "****-****-****-" + masked["credit_card"][-4:]
            if "email" in masked:
                email = masked["email"]
                masked["email"] = email[0] + "***@" + email.split("@")[1]
            return masked

        masked_data = mask_sensitive_data(user_data)
        console.print(f"原始數據：{user_data}")
        console.print(f"脫敏數據：{masked_data}")

        return result

    except Exception as e:
        console.print(f"[red]錯誤：{e}[/red]")
        return None


def tracing_with_feedback():
    """示例 6：為追蹤添加反饋"""
    console.print(Panel("[bold cyan]示例 6：為追蹤添加反饋[/bold cyan]"))

    try:
        client = Client()

        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        prompt = ChatPromptTemplate.from_template("創作一個關於 {topic} 的笑話")
        chain = prompt | llm | StrOutputParser()

        console.print("\n[cyan]生成笑話...[/cyan]")

        # 執行並獲取 run_id
        result = chain.invoke({"topic": "程序員"})

        console.print(f"\n笑話：{result}")

        # 模擬用戶反饋
        console.print("\n[cyan]添加用戶反饋...[/cyan]")

        # 注意：需要 run_id 來添加反饋
        # 在實際應用中，可以從回調中獲取 run_id
        # 這裡我們演示概念

        feedback_info = """
        # 添加反饋的代碼示例：

        from langsmith import Client

        client = Client()

        # 為 run 添加反饋
        client.create_feedback(
            run_id=run_id,
            key="user_rating",
            score=0.8,  # 0-1 之間的分數
            comment="很有趣的笑話！"
        )

        # 或使用簡化的方法
        client.create_feedback(
            run_id=run_id,
            key="thumbs_up",
            score=1.0
        )
        """

        console.print(Panel(feedback_info, border_style="blue"))

        console.print(
            "\n[yellow]提示：反饋數據可用於評估和改進模型[/yellow]"
        )

        return result

    except Exception as e:
        console.print(f"[red]錯誤：{e}[/red]")
        return None


def tracing_configuration_summary():
    """總結追蹤配置選項"""
    console.print(Panel("[bold cyan]追蹤配置選項總結[/bold cyan]"))

    table = Table(title="環境變量配置", show_header=True, header_style="bold magenta")
    table.add_column("環境變量", style="cyan", width=30)
    table.add_column("說明", style="white", width=40)
    table.add_column("示例", style="green", width=20)

    configs = [
        ("LANGCHAIN_TRACING_V2", "啟用追蹤", "true"),
        ("LANGCHAIN_ENDPOINT", "API 端點", "https://api.smith..."),
        ("LANGCHAIN_API_KEY", "認證密鑰", "ls__..."),
        ("LANGCHAIN_PROJECT", "項目名稱", "my-project"),
        ("LANGCHAIN_SESSION", "會話 ID（已棄用）", "session-123"),
    ]

    for var, desc, example in configs:
        table.add_row(var, desc, example)

    console.print(table)

    # RunnableConfig 選項
    table2 = Table(title="RunnableConfig 選項", show_header=True, header_style="bold magenta")
    table2.add_column("選項", style="cyan", width=20)
    table2.add_column("說明", style="white", width=50)
    table2.add_column("示例", style="green", width=20)

    options = [
        ("run_name", "自定義 run 名稱", '"my-custom-run"'),
        ("tags", "添加標籤", '["tag1", "tag2"]'),
        ("metadata", "添加元數據", '{"user": "123"}'),
        ("callbacks", "自定義回調", '[MyCallback()]'),
    ]

    for opt, desc, example in options:
        table2.add_row(opt, desc, example)

    console.print("\n")
    console.print(table2)


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold green]LangSmith 自動追蹤[/bold green]",
        border_style="green"
    ))

    # 設置追蹤
    setup_basic_tracing()

    console.print("\n" + "="*60 + "\n")

    # 運行示例
    tracing_with_metadata()
    console.print("\n" + "="*60 + "\n")

    tracing_with_custom_name()
    console.print("\n" + "="*60 + "\n")

    conditional_tracing()
    console.print("\n" + "="*60 + "\n")

    sampling_traces()
    console.print("\n" + "="*60 + "\n")

    hiding_sensitive_data()
    console.print("\n" + "="*60 + "\n")

    tracing_with_feedback()
    console.print("\n" + "="*60 + "\n")

    # 配置總結
    tracing_configuration_summary()

    # 總結
    console.print(Panel("""
[bold green]自動追蹤總結[/bold green]

關鍵要點：
1. 使用 RunnableConfig 添加元數據和標籤
2. 自定義 run 名稱提高可讀性
3. 根據條件選擇性追蹤
4. 使用採樣減少高流量場景的成本
5. 妥善處理敏感信息
6. 利用反饋改進模型

最佳實踐：
✓ 為所有追蹤添加有意義的標籤
✓ 使用元數據記錄重要上下文
✓ 在生產環境中考慮採樣
✓ 脫敏或避免記錄敏感數據
✓ 定期審查追蹤數據

下一步：
- 查看 03_手動追蹤.py 學習手動控制
- 查看 04_評估系統.py 了解如何評估性能
    """, title="總結", border_style="green"))


if __name__ == "__main__":
    main()

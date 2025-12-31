"""
LangMem 短期記憶示例

本示例展示:
1. 對話緩衝記憶
2. 對話窗口記憶
3. 對話摘要記憶
4. 記憶限制和管理
"""

from langchain.memory import (
    ConversationBufferMemory,
    ConversationBufferWindowMemory,
    ConversationSummaryMemory,
    ConversationTokenBufferMemory
)
from langchain_openai import ChatOpenAI
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from dotenv import load_dotenv
import os

console = Console()
load_dotenv()


def demonstrate_buffer_memory():
    """演示緩衝記憶"""
    try:
        console.print("\n[cyan]1. 對話緩衝記憶 (Buffer Memory)[/cyan]")
        console.print("[dim]保留所有對話歷史[/dim]\n")

        # 創建緩衝記憶
        memory = ConversationBufferMemory(return_messages=True)

        # 添加對話
        conversations = [
            ("你好!", "您好!很高興見到您。"),
            ("今天天氣如何?", "今天天氣很好,陽光明媚。"),
            ("推薦一些活動吧", "可以去公園散步或騎自行車。"),
        ]

        for user_msg, ai_msg in conversations:
            memory.save_context({"input": user_msg}, {"output": ai_msg})

        # 顯示記憶
        memory_vars = memory.load_memory_variables({})
        history = memory_vars["history"]

        table = Table(title="緩衝記憶內容")
        table.add_column("輪次", style="cyan")
        table.add_column("內容", style="green")

        for idx, msg in enumerate(history, 1):
            role = "👤 用戶" if msg.type == "human" else "🤖 AI"
            table.add_row(f"{role}", msg.content)

        console.print(table)
        console.print(f"[yellow]總消息數: {len(history)}[/yellow]\n")

        return memory

    except Exception as e:
        console.print(f"[red]✗ 演示失敗: {e}[/red]")
        return None


def demonstrate_window_memory():
    """演示窗口記憶"""
    try:
        console.print("[cyan]2. 對話窗口記憶 (Window Memory)[/cyan]")
        console.print("[dim]只保留最近 K 輪對話[/dim]\n")

        # 創建窗口記憶 (只保留最近 2 輪)
        memory = ConversationBufferWindowMemory(
            k=2,
            return_messages=True
        )

        # 添加多輪對話
        conversations = [
            ("第一條消息", "收到第一條"),
            ("第二條消息", "收到第二條"),
            ("第三條消息", "收到第三條"),
            ("第四條消息", "收到第四條"),
        ]

        for user_msg, ai_msg in conversations:
            memory.save_context({"input": user_msg}, {"output": ai_msg})

        # 顯示記憶
        memory_vars = memory.load_memory_variables({})
        history = memory_vars["history"]

        table = Table(title=f"窗口記憶內容 (k=2, 只保留最近 {memory.k} 輪)")
        table.add_column("角色", style="cyan")
        table.add_column("內容", style="green")

        for msg in history:
            role = "👤 用戶" if msg.type == "human" else "🤖 AI"
            table.add_row(role, msg.content)

        console.print(table)
        console.print(f"[yellow]保留消息數: {len(history)} (應該是 {memory.k * 2})[/yellow]\n")

        return memory

    except Exception as e:
        console.print(f"[red]✗ 演示失敗: {e}[/red]")
        return None


def demonstrate_summary_memory():
    """演示摘要記憶"""
    try:
        console.print("[cyan]3. 對話摘要記憶 (Summary Memory)[/cyan]")
        console.print("[dim]自動總結對話歷史[/dim]\n")

        # 檢查 API Key
        if not os.getenv("OPENAI_API_KEY"):
            console.print("[yellow]⚠ 跳過: 需要 OPENAI_API_KEY[/yellow]\n")
            return None

        # 創建 LLM
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY")
        )

        # 創建摘要記憶
        memory = ConversationSummaryMemory(
            llm=llm,
            return_messages=True
        )

        # 添加對話
        memory.save_context(
            {"input": "嗨,我是小明,我在一家科技公司工作。"},
            {"output": "你好小明!很高興認識你。請問你在科技公司做什麼工作呢?"}
        )
        memory.save_context(
            {"input": "我是一名軟體工程師,主要使用 Python 開發。"},
            {"output": "太棒了! Python 是一個很強大的語言。你主要開發什麼類型的應用?"}
        )
        memory.save_context(
            {"input": "我主要做 AI 和機器學習相關的項目。"},
            {"output": "很有意思!你在 AI 領域有什麼特別感興趣的方向嗎?"}
        )

        # 獲取摘要
        memory_vars = memory.load_memory_variables({})

        console.print("[yellow]對話摘要:[/yellow]")
        console.print(Panel(
            memory_vars.get("history", "無摘要"),
            border_style="green"
        ))
        console.print()

        return memory

    except Exception as e:
        console.print(f"[red]✗ 演示失敗: {e}[/red]")
        return None


def demonstrate_token_buffer_memory():
    """演示令牌緩衝記憶"""
    try:
        console.print("[cyan]4. 令牌緩衝記憶 (Token Buffer Memory)[/cyan]")
        console.print("[dim]基於令牌數限制記憶[/dim]\n")

        # 檢查 API Key
        if not os.getenv("OPENAI_API_KEY"):
            console.print("[yellow]⚠ 跳過: 需要 OPENAI_API_KEY[/yellow]\n")
            return None

        # 創建 LLM
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            api_key=os.getenv("OPENAI_API_KEY")
        )

        # 創建令牌緩衝記憶 (限制 100 tokens)
        memory = ConversationTokenBufferMemory(
            llm=llm,
            max_token_limit=100,
            return_messages=True
        )

        # 添加對話
        conversations = [
            ("什麼是人工智慧?", "人工智慧(AI)是計算機科學的一個分支,致力於創建能夠執行需要人類智慧的任務的系統。"),
            ("AI 有哪些應用?", "AI 應用廣泛,包括自然語言處理、計算機視覺、推薦系統、自動駕駛等。"),
            ("機器學習和深度學習的區別?", "機器學習是 AI 的子集,深度學習又是機器學習的子集,使用多層神經網絡。"),
        ]

        for user_msg, ai_msg in conversations:
            memory.save_context({"input": user_msg}, {"output": ai_msg})

        # 顯示記憶
        memory_vars = memory.load_memory_variables({})
        history = memory_vars["history"]

        table = Table(title="令牌緩衝記憶 (限制 100 tokens)")
        table.add_column("角色", style="cyan")
        table.add_column("內容", style="green")

        for msg in history:
            role = "👤 用戶" if msg.type == "human" else "🤖 AI"
            content = msg.content[:80] + "..." if len(msg.content) > 80 else msg.content
            table.add_row(role, content)

        console.print(table)
        console.print(f"[yellow]保留消息數: {len(history)}[/yellow]\n")

        return memory

    except Exception as e:
        console.print(f"[red]✗ 演示失敗: {e}[/red]")
        return None


def compare_memory_types():
    """比較不同記憶類型"""
    try:
        console.print("[cyan]5. 記憶類型比較[/cyan]\n")

        table = Table(title="短期記憶類型比較")
        table.add_column("類型", style="cyan")
        table.add_column("優點", style="green")
        table.add_column("缺點", style="red")
        table.add_column("適用場景", style="yellow")

        table.add_row(
            "Buffer Memory",
            "完整上下文",
            "消耗資源多",
            "短對話、完整上下文需求"
        )
        table.add_row(
            "Window Memory",
            "固定資源消耗",
            "可能丟失重要信息",
            "固定長度對話"
        )
        table.add_row(
            "Summary Memory",
            "高效壓縮",
            "需要 LLM 調用",
            "長對話、信息提取"
        )
        table.add_row(
            "Token Buffer",
            "精確控制成本",
            "配置複雜",
            "成本敏感場景"
        )

        console.print(table)
        console.print()

    except Exception as e:
        console.print(f"[red]✗ 比較失敗: {e}[/red]")


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]LangMem 短期記憶示例[/bold cyan]\n"
        "[dim]展示不同類型的短期記憶管理[/dim]",
        border_style="cyan"
    ))

    # 演示各種記憶類型
    demonstrate_buffer_memory()
    demonstrate_window_memory()
    demonstrate_summary_memory()
    demonstrate_token_buffer_memory()

    # 比較記憶類型
    compare_memory_types()

    # 完成
    console.print("="*60)
    console.print("[bold green]✓ 短期記憶示例完成！[/bold green]")
    console.print("\n[cyan]關鍵要點:[/cyan]")
    console.print("  • Buffer Memory: 完整保留所有對話")
    console.print("  • Window Memory: 只保留最近 K 輪對話")
    console.print("  • Summary Memory: 自動總結歷史對話")
    console.print("  • Token Buffer: 基於令牌數限制記憶")


if __name__ == "__main__":
    main()

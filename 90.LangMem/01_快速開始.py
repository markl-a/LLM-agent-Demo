"""
LangMem 快速開始示例

本示例展示:
1. LangMem 基礎配置
2. 創建簡單記憶
3. 添加和檢索記憶
4. 基本記憶操作
"""

from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain_openai import ChatOpenAI
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from dotenv import load_dotenv
import os

console = Console()

# 載入環境變數
load_dotenv()


def setup_memory():
    """設置基礎記憶"""
    try:
        console.print("\n[cyan]正在設置基礎記憶...[/cyan]")

        # 創建對話緩衝記憶
        memory = ConversationBufferMemory(
            return_messages=True,
            memory_key="history"
        )

        console.print("[green]✓ 記憶設置成功[/green]\n")

        return memory

    except Exception as e:
        console.print(f"[red]✗ 設置記憶失敗: {e}[/red]")
        return None


def create_conversation_chain(memory):
    """創建對話鏈"""
    try:
        console.print("[cyan]創建對話鏈...[/cyan]")

        # 初始化 LLM
        llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY")
        )

        # 創建對話鏈
        conversation = ConversationChain(
            llm=llm,
            memory=memory,
            verbose=True
        )

        console.print("[green]✓ 對話鏈創建成功[/green]\n")

        return conversation

    except Exception as e:
        console.print(f"[red]✗ 創建對話鏈失敗: {e}[/red]")
        return None


def demonstrate_memory(conversation):
    """演示記憶功能"""
    try:
        console.print("[cyan]演示記憶功能...[/cyan]\n")

        # 第一輪對話
        console.print("[bold yellow]>>> 對話 1:[/bold yellow]")
        response1 = conversation.predict(
            input="你好！我叫張三,我喜歡寫程式。"
        )
        console.print(f"[green]AI:[/green] {response1}\n")

        # 第二輪對話
        console.print("[bold yellow]>>> 對話 2:[/bold yellow]")
        response2 = conversation.predict(
            input="我最喜歡的程式語言是 Python。"
        )
        console.print(f"[green]AI:[/green] {response2}\n")

        # 第三輪對話 - 測試記憶
        console.print("[bold yellow]>>> 對話 3:[/bold yellow]")
        response3 = conversation.predict(
            input="你還記得我叫什麼名字嗎?我喜歡什麼?"
        )
        console.print(f"[green]AI:[/green] {response3}\n")

        return True

    except Exception as e:
        console.print(f"[red]✗ 演示失敗: {e}[/red]")
        return False


def view_memory_content(memory):
    """查看記憶內容"""
    try:
        console.print("[cyan]查看記憶內容...[/cyan]")

        # 獲取記憶內容
        memory_vars = memory.load_memory_variables({})

        # 創建表格顯示
        table = Table(title="記憶內容")
        table.add_column("編號", style="cyan")
        table.add_column("角色", style="yellow")
        table.add_column("內容", style="green")

        # 顯示歷史記錄
        history = memory_vars.get("history", [])
        for idx, message in enumerate(history, 1):
            role = "用戶" if message.type == "human" else "AI"
            content = message.content[:100] + "..." if len(message.content) > 100 else message.content
            table.add_row(str(idx), role, content)

        console.print(table)
        console.print()

        return True

    except Exception as e:
        console.print(f"[red]✗ 查看記憶失敗: {e}[/red]")
        return False


def demonstrate_memory_operations(memory):
    """演示記憶操作"""
    try:
        console.print("[cyan]演示記憶操作...[/cyan]\n")

        # 手動添加記憶
        console.print("[yellow]1. 手動添加記憶[/yellow]")
        memory.save_context(
            {"input": "我的生日是 1990-01-01"},
            {"output": "好的,我記住了您的生日是 1990 年 1 月 1 日。"}
        )
        console.print("[green]✓ 已添加記憶[/green]\n")

        # 查看記憶變數
        console.print("[yellow]2. 查看記憶變數[/yellow]")
        memory_vars = memory.load_memory_variables({})
        console.print(f"[dim]記憶變數鍵: {list(memory_vars.keys())}[/dim]\n")

        # 清空記憶
        console.print("[yellow]3. 清空記憶[/yellow]")
        memory.clear()
        console.print("[green]✓ 記憶已清空[/green]\n")

        # 驗證記憶已清空
        memory_vars_after = memory.load_memory_variables({})
        console.print(f"[dim]清空後的記憶: {memory_vars_after.get('history', [])}[/dim]\n")

        return True

    except Exception as e:
        console.print(f"[red]✗ 操作失敗: {e}[/red]")
        return False


def demonstrate_memory_persistence():
    """演示記憶持久化"""
    try:
        console.print("[cyan]演示記憶持久化...[/cyan]\n")

        # 創建可持久化的記憶
        from langchain.memory import ConversationBufferMemory
        from langchain.memory.chat_message_histories import FileChatMessageHistory

        # 使用文件存儲歷史
        file_history = FileChatMessageHistory("conversation_history.json")

        memory = ConversationBufferMemory(
            chat_memory=file_history,
            return_messages=True
        )

        # 添加一些記憶
        memory.save_context(
            {"input": "今天天氣很好"},
            {"output": "是的,今天是個好天氣!"}
        )

        console.print("[green]✓ 記憶已持久化到文件[/green]")
        console.print("[dim]文件: conversation_history.json[/dim]\n")

        return True

    except Exception as e:
        console.print(f"[red]✗ 持久化失敗: {e}[/red]")
        return False


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]LangMem 快速開始示例[/bold cyan]\n"
        "[dim]展示基礎記憶功能[/dim]",
        border_style="cyan"
    ))

    # 檢查 API Key
    if not os.getenv("OPENAI_API_KEY"):
        console.print("[red]錯誤: 請在 .env 文件中設置 OPENAI_API_KEY[/red]")
        return

    # 1. 設置記憶
    memory = setup_memory()
    if not memory:
        return

    # 2. 創建對話鏈
    conversation = create_conversation_chain(memory)
    if not conversation:
        return

    # 3. 演示記憶功能
    demonstrate_memory(conversation)

    # 4. 查看記憶內容
    view_memory_content(memory)

    # 5. 演示記憶操作
    demonstrate_memory_operations(memory)

    # 6. 演示記憶持久化
    demonstrate_memory_persistence()

    # 完成
    console.print("="*60)
    console.print("[bold green]✓ 快速開始示例完成！[/bold green]")
    console.print("\n[cyan]下一步:[/cyan]")
    console.print("  1. 查看 02_短期記憶.py 學習短期記憶管理")
    console.print("  2. 查看 03_長期記憶.py 學習持久化記憶")
    console.print("  3. 查看 04_語義記憶.py 學習向量搜索")


if __name__ == "__main__":
    main()

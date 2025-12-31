"""
LangMem 記憶壓縮示例

本示例展示:
1. 對話摘要壓縮
2. 記憶token優化
3. 關鍵信息提取
4. 記憶層次化管理
"""

from langchain.memory import (
    ConversationSummaryMemory,
    ConversationSummaryBufferMemory
)
from langchain_openai import ChatOpenAI
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress
from dotenv import load_dotenv
import os

console = Console()
load_dotenv()


def demonstrate_summary_compression():
    """演示摘要壓縮"""
    try:
        console.print("\n[cyan]1. 對話摘要壓縮[/cyan]")
        console.print("[dim]自動總結長對話歷史[/dim]\n")

        if not os.getenv("OPENAI_API_KEY"):
            console.print("[yellow]⚠ 需要 OPENAI_API_KEY[/yellow]\n")
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
            return_messages=False
        )

        # 添加長對話
        console.print("[yellow]添加對話歷史...[/yellow]")

        conversations = [
            ("你好,我是一名軟體工程師", "你好!很高興認識你。請問你主要使用什麼技術棧?"),
            ("我主要用 Python 開發,特別是 Django 和 FastAPI", "很棒的選擇!你有做過什麼有趣的項目嗎?"),
            ("我最近在開發一個 AI 聊天機器人", "聽起來很有意思!你使用什麼 AI 框架?"),
            ("我使用 LangChain 和 OpenAI 的 API", "LangChain 是個很強大的框架。你遇到什麼挑戰嗎?"),
            ("主要是記憶管理比較複雜", "確實,記憶管理是 AI Agent 的核心挑戰之一。"),
        ]

        for user_msg, ai_msg in conversations:
            memory.save_context({"input": user_msg}, {"output": ai_msg})

        # 顯示原始對話長度
        total_chars = sum(len(u) + len(a) for u, a in conversations)
        console.print(f"[dim]原始對話總字符數: {total_chars}[/dim]\n")

        # 獲取摘要
        console.print("[yellow]生成的摘要:[/yellow]")
        summary = memory.load_memory_variables({})

        console.print(Panel(
            summary.get("history", "無摘要"),
            border_style="green",
            title="壓縮後的摘要"
        ))

        summary_chars = len(summary.get("history", ""))
        compression_ratio = (1 - summary_chars / total_chars) * 100 if total_chars > 0 else 0

        console.print(f"\n[green]✓ 壓縮完成[/green]")
        console.print(f"[dim]摘要字符數: {summary_chars}[/dim]")
        console.print(f"[dim]壓縮比: {compression_ratio:.1f}%[/dim]\n")

        return memory

    except Exception as e:
        console.print(f"[red]✗ 壓縮失敗: {e}[/red]")
        return None


def demonstrate_summary_buffer_memory():
    """演示摘要緩衝記憶"""
    try:
        console.print("[cyan]2. 摘要緩衝記憶[/cyan]")
        console.print("[dim]保留最近對話 + 壓縮舊對話[/dim]\n")

        if not os.getenv("OPENAI_API_KEY"):
            console.print("[yellow]⚠ 需要 OPENAI_API_KEY[/yellow]\n")
            return None

        # 創建 LLM
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            api_key=os.getenv("OPENAI_API_KEY")
        )

        # 創建摘要緩衝記憶
        memory = ConversationSummaryBufferMemory(
            llm=llm,
            max_token_limit=100,  # 超過此限制則壓縮
            return_messages=True
        )

        # 添加對話
        console.print("[yellow]添加多輪對話...[/yellow]")

        conversations = [
            ("介紹一下 Python", "Python 是一種高級編程語言,語法簡潔優雅。"),
            ("Python 有什麼特點?", "Python 具有動態類型、自動記憶體管理等特點。"),
            ("推薦一些 Python 框架", "Django、Flask、FastAPI 都是很好的 Web 框架。"),
            ("什麼是 LangChain?", "LangChain 是用於開發 AI 應用的框架。"),
        ]

        for user_msg, ai_msg in conversations:
            memory.save_context({"input": user_msg}, {"output": ai_msg})

        # 顯示記憶內容
        memory_vars = memory.load_memory_variables({})

        console.print("\n[yellow]記憶內容:[/yellow]")
        console.print(Panel(
            str(memory_vars.get("history", [])),
            border_style="green",
            title="混合記憶(摘要 + 最近對話)"
        ))
        console.print()

        return memory

    except Exception as e:
        console.print(f"[red]✗ 演示失敗: {e}[/red]")
        return None


def demonstrate_key_extraction():
    """演示關鍵信息提取"""
    try:
        console.print("[cyan]3. 關鍵信息提取[/cyan]")
        console.print("[dim]從對話中提取重要信息[/dim]\n")

        # 模擬長對話
        long_conversation = """
        用戶: 你好,我叫張三,是一名 35 歲的軟體工程師。
        AI: 你好張三!很高興認識你。
        用戶: 我在一家 AI 公司工作,主要負責開發聊天機器人。
        AI: 聽起來是個很有趣的工作!
        用戶: 是的,我們使用 Python 和 LangChain 框架。
        AI: LangChain 是個很強大的工具。
        用戶: 我的郵箱是 zhangsan@example.com,電話是 0912-345-678。
        AI: 好的,我記下了您的聯繫方式。
        """

        # 提取關鍵信息
        key_info = {
            "姓名": "張三",
            "年齡": "35歲",
            "職業": "軟體工程師",
            "公司類型": "AI 公司",
            "工作內容": "開發聊天機器人",
            "技術棧": "Python, LangChain",
            "郵箱": "zhangsan@example.com",
            "電話": "0912-345-678"
        }

        # 顯示提取結果
        console.print("[yellow]原始對話長度:[/yellow]")
        console.print(f"  {len(long_conversation)} 字符\n")

        console.print("[yellow]提取的關鍵信息:[/yellow]")

        table = Table()
        table.add_column("類別", style="cyan")
        table.add_column("信息", style="green")

        for key, value in key_info.items():
            table.add_row(key, value)

        console.print(table)

        compressed_size = sum(len(k) + len(v) for k, v in key_info.items())
        compression = (1 - compressed_size / len(long_conversation)) * 100

        console.print(f"\n[green]✓ 信息提取完成[/green]")
        console.print(f"[dim]壓縮比: {compression:.1f}%[/dim]\n")

        return key_info

    except Exception as e:
        console.print(f"[red]✗ 提取失敗: {e}[/red]")
        return None


def demonstrate_hierarchical_memory():
    """演示層次化記憶管理"""
    try:
        console.print("[cyan]4. 層次化記憶管理[/cyan]")
        console.print("[dim]將記憶組織成多個層次[/dim]\n")

        # 定義記憶層次
        memory_hierarchy = {
            "L1 - 工作記憶": {
                "容量": "7±2 項",
                "內容": "當前對話上下文",
                "保留時間": "對話期間"
            },
            "L2 - 短期記憶": {
                "容量": "最近 N 輪對話",
                "內容": "最近對話歷史",
                "保留時間": "當前會話"
            },
            "L3 - 長期記憶": {
                "容量": "無限制",
                "內容": "壓縮後的重要信息",
                "保留時間": "永久"
            }
        }

        # 顯示層次結構
        table = Table(title="記憶層次結構")
        table.add_column("層次", style="cyan")
        table.add_column("容量", style="yellow")
        table.add_column("內容", style="green")
        table.add_column("保留時間", style="magenta")

        for level, info in memory_hierarchy.items():
            table.add_row(
                level,
                info["容量"],
                info["內容"],
                info["保留時間"]
            )

        console.print(table)
        console.print()

        # 記憶流轉示意
        console.print("[yellow]記憶流轉過程:[/yellow]")
        console.print("  📥 新信息 → L1 工作記憶")
        console.print("  ⬇️  對話進行 → L2 短期記憶")
        console.print("  ⬇️  壓縮摘要 → L3 長期記憶")
        console.print("  ♻️  重要信息保留,其他遺忘\n")

        return memory_hierarchy

    except Exception as e:
        console.print(f"[red]✗ 演示失敗: {e}[/red]")
        return None


def compare_compression_methods():
    """比較壓縮方法"""
    try:
        console.print("[cyan]5. 壓縮方法比較[/cyan]\n")

        table = Table(title="記憶壓縮方法比較")
        table.add_column("方法", style="cyan")
        table.add_column("優點", style="green")
        table.add_column("缺點", style="red")
        table.add_column("適用場景", style="yellow")

        table.add_row(
            "摘要壓縮",
            "大幅減少 token",
            "可能丟失細節",
            "長對話歷史"
        )
        table.add_row(
            "關鍵信息提取",
            "保留重要信息",
            "需要人工定義規則",
            "結構化信息"
        )
        table.add_row(
            "層次化管理",
            "平衡效率和完整性",
            "實現複雜",
            "複雜應用"
        )
        table.add_row(
            "Token 限制",
            "精確控制成本",
            "可能截斷對話",
            "成本敏感"
        )

        console.print(table)
        console.print()

        # 使用建議
        console.print("[yellow]使用建議:[/yellow]")
        console.print("  1. 短對話: 無需壓縮")
        console.print("  2. 中長對話: 使用摘要壓縮")
        console.print("  3. 結構化數據: 關鍵信息提取")
        console.print("  4. 複雜系統: 層次化管理")
        console.print("  5. 生產環境: 多種方法結合\n")

    except Exception as e:
        console.print(f"[red]✗ 比較失敗: {e}[/red]")


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]LangMem 記憶壓縮示例[/bold cyan]\n"
        "[dim]展示記憶壓縮和優化技術[/dim]",
        border_style="cyan"
    ))

    # 演示各種壓縮方法
    demonstrate_summary_compression()
    demonstrate_summary_buffer_memory()
    demonstrate_key_extraction()
    demonstrate_hierarchical_memory()

    # 比較壓縮方法
    compare_compression_methods()

    # 完成
    console.print("="*60)
    console.print("[bold green]✓ 記憶壓縮示例完成！[/bold green]")
    console.print("\n[cyan]關鍵要點:[/cyan]")
    console.print("  • 摘要壓縮: 自動總結長對話")
    console.print("  • 混合策略: 摘要 + 最近對話")
    console.print("  • 信息提取: 保留關鍵數據")
    console.print("  • 層次管理: 多級記憶組織")


if __name__ == "__main__":
    main()

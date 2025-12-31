"""
Mem0 添加記憶示例

本示例展示:
1. 單條記憶添加
2. 批量記憶添加
3. 帶元數據的記憶
4. 不同類型的記憶
"""

from mem0 import Memory
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from dotenv import load_dotenv
import os
import time

console = Console()
load_dotenv()


def setup_memory():
    """設置記憶系統"""
    try:
        console.print("\n[cyan]設置 Mem0...[/cyan]")

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            console.print("[yellow]⚠ 需要 OPENAI_API_KEY[/yellow]\n")
            return None

        config = {
            "llm": {
                "provider": "openai",
                "config": {
                    "model": "gpt-4",
                    "api_key": api_key
                }
            }
        }

        memory = Memory.from_config(config)
        console.print("[green]✓ 記憶系統就緒[/green]\n")

        return memory

    except Exception as e:
        console.print(f"[red]✗ 設置失敗: {e}[/red]")
        return None


def demonstrate_simple_add(memory):
    """演示簡單添加"""
    try:
        console.print("[cyan]1. 簡單記憶添加[/cyan]")
        console.print("[dim]最基礎的添加方式[/dim]\n")

        user_id = "user_001"

        # 簡單文本記憶
        memories = [
            "用戶的名字是李明",
            "用戶的生日是 1990 年 5 月 15 日",
            "用戶的電子郵件是 liming@example.com"
        ]

        table = Table(title="添加簡單記憶")
        table.add_column("編號", style="cyan")
        table.add_column("記憶", style="green")

        for idx, mem in enumerate(memories, 1):
            memory.add(mem, user_id=user_id)
            table.add_row(str(idx), mem)
            time.sleep(0.1)

        console.print(table)
        console.print(f"\n[green]✓ 成功添加 {len(memories)} 條記憶[/green]\n")

        return user_id

    except Exception as e:
        console.print(f"[red]✗ 添加失敗: {e}[/red]")
        return None


def demonstrate_batch_add(memory, user_id):
    """演示批量添加"""
    try:
        console.print("[cyan]2. 批量記憶添加[/cyan]")
        console.print("[dim]一次添加多條記憶[/dim]\n")

        # 批量記憶數據
        batch_memories = [
            "用戶喜歡的程式語言: Python, JavaScript, Go",
            "用戶的工作經驗: 5 年軟體開發",
            "用戶擅長的領域: Web 開發, AI, 雲計算",
            "用戶的教育背景: 計算機科學碩士",
            "用戶的工作地點: 台北市信義區"
        ]

        console.print("[yellow]批量添加中...[/yellow]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("處理中...", total=len(batch_memories))

            for mem in batch_memories:
                memory.add(mem, user_id=user_id)
                progress.update(task, advance=1)
                time.sleep(0.1)

        console.print(f"[green]✓ 批量添加完成: {len(batch_memories)} 條記憶[/green]\n")

        return True

    except Exception as e:
        console.print(f"[red]✗ 批量添加失敗: {e}[/red]")
        return False


def demonstrate_metadata_add(memory):
    """演示帶元數據的添加"""
    try:
        console.print("[cyan]3. 帶元數據的記憶[/cyan]")
        console.print("[dim]添加額外的結構化信息[/dim]\n")

        user_id = "user_002"

        # 帶元數據的記憶
        memories_with_metadata = [
            {
                "text": "用戶完成了 Python 進階課程",
                "metadata": {
                    "category": "education",
                    "importance": 8,
                    "source": "learning_platform",
                    "date": "2024-01-15"
                }
            },
            {
                "text": "用戶參加了 AI 技術峰會",
                "metadata": {
                    "category": "event",
                    "importance": 7,
                    "source": "conference",
                    "date": "2024-02-20"
                }
            },
            {
                "text": "用戶獲得了 AWS 認證",
                "metadata": {
                    "category": "certification",
                    "importance": 9,
                    "source": "aws",
                    "date": "2024-03-10"
                }
            }
        ]

        table = Table(title="帶元數據的記憶")
        table.add_column("記憶", style="green")
        table.add_column("分類", style="cyan")
        table.add_column("重要性", style="yellow")

        for item in memories_with_metadata:
            memory.add(
                item["text"],
                user_id=user_id,
                metadata=item["metadata"]
            )

            table.add_row(
                item["text"],
                item["metadata"]["category"],
                str(item["metadata"]["importance"])
            )

        console.print(table)
        console.print(f"\n[green]✓ 成功添加 {len(memories_with_metadata)} 條帶元數據的記憶[/green]\n")

        return user_id

    except Exception as e:
        console.print(f"[red]✗ 添加失敗: {e}[/red]")
        return None


def demonstrate_different_types(memory):
    """演示不同類型的記憶"""
    try:
        console.print("[cyan]4. 不同類型的記憶[/cyan]")
        console.print("[dim]事實、偏好、事件等[/dim]\n")

        user_id = "user_003"

        memory_types = [
            {
                "type": "事實",
                "examples": [
                    "用戶的身高是 175 公分",
                    "用戶會說中文、英文和日文",
                    "用戶擁有駕照"
                ]
            },
            {
                "type": "偏好",
                "examples": [
                    "用戶喜歡早起工作",
                    "用戶偏好遠程辦公",
                    "用戶喜歡聽爵士音樂"
                ]
            },
            {
                "type": "事件",
                "examples": [
                    "用戶上週參加了馬拉松",
                    "用戶最近完成了項目發布",
                    "用戶計劃下個月去日本旅遊"
                ]
            }
        ]

        table = Table(title="不同類型的記憶")
        table.add_column("類型", style="cyan", width=10)
        table.add_column("示例", style="green")

        for mem_type in memory_types:
            type_name = mem_type["type"]
            for idx, example in enumerate(mem_type["examples"]):
                memory.add(example, user_id=user_id)

                if idx == 0:
                    table.add_row(type_name, example)
                else:
                    table.add_row("", example)

        console.print(table)
        console.print()

        return user_id

    except Exception as e:
        console.print(f"[red]✗ 添加失敗: {e}[/red]")
        return None


def demonstrate_conversation_memory(memory):
    """演示從對話中提取記憶"""
    try:
        console.print("[cyan]5. 從對話中提取記憶[/cyan]")
        console.print("[dim]自動識別對話中的重要信息[/dim]\n")

        user_id = "user_004"

        # 模擬對話
        conversations = [
            "我最近搬到台中了,在一家新創公司工作",
            "我們公司主要做 AI 相關的產品,我負責後端開發",
            "我每天都會花 2 小時學習新技術,最近在研究 LangChain",
            "週末我喜歡去爬山,台中附近有很多不錯的登山步道"
        ]

        console.print("[yellow]處理對話...[/yellow]")

        table = Table(title="對話記憶提取")
        table.add_column("對話", style="green", width=50)

        for conv in conversations:
            memory.add(conv, user_id=user_id)
            table.add_row(conv)

        console.print(table)
        console.print("\n[green]✓ Mem0 會自動從對話中提取關鍵信息[/green]\n")

        # 驗證提取結果
        console.print("[yellow]提取的記憶:[/yellow]")
        all_memories = memory.get_all(user_id=user_id)

        for idx, mem in enumerate(all_memories[:5], 1):
            console.print(f"  {idx}. {mem.get('memory', '無')}")

        console.print()

        return user_id

    except Exception as e:
        console.print(f"[red]✗ 處理失敗: {e}[/red]")
        return None


def demonstrate_best_practices():
    """演示最佳實踐"""
    try:
        console.print("[cyan]6. 添加記憶的最佳實踐[/cyan]\n")

        practices = [
            {
                "實踐": "明確具體",
                "好例子": "用戶喜歡美式咖啡,不加糖",
                "壞例子": "用戶喜歡咖啡"
            },
            {
                "實踐": "原子化",
                "好例子": "用戶的生日是 1990-05-15",
                "壞例子": "用戶 30 歲,生日在 5 月"
            },
            {
                "實踐": "時效性",
                "好例子": "用戶 2024 年加入公司",
                "壞例子": "用戶最近加入公司"
            },
            {
                "實踐": "可驗證",
                "好例子": "用戶的郵箱是 user@example.com",
                "壞例子": "用戶有個郵箱"
            }
        ]

        table = Table(title="記憶添加最佳實踐")
        table.add_column("最佳實踐", style="cyan")
        table.add_column("✅ 好例子", style="green")
        table.add_column("❌ 避免", style="red")

        for practice in practices:
            table.add_row(
                practice["實踐"],
                practice["好例子"],
                practice["壞例子"]
            )

        console.print(table)
        console.print()

    except Exception as e:
        console.print(f"[red]✗ 演示失敗: {e}[/red]")


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Mem0 添加記憶示例[/bold cyan]\n"
        "[dim]展示各種添加記憶的方式[/dim]",
        border_style="cyan"
    ))

    # 設置記憶系統
    memory = setup_memory()
    if not memory:
        return

    # 演示各種添加方式
    user_id = demonstrate_simple_add(memory)
    if user_id:
        demonstrate_batch_add(memory, user_id)

    demonstrate_metadata_add(memory)
    demonstrate_different_types(memory)
    demonstrate_conversation_memory(memory)

    # 最佳實踐
    demonstrate_best_practices()

    # 完成
    console.print("="*60)
    console.print("[bold green]✓ 添加記憶示例完成！[/bold green]")
    console.print("\n[cyan]關鍵要點:[/cyan]")
    console.print("  • 簡單添加: 直接添加文本記憶")
    console.print("  • 批量添加: 高效處理多條記憶")
    console.print("  • 元數據: 增強記憶的可檢索性")
    console.print("  • 明確具體: 記憶內容要清晰明確")


if __name__ == "__main__":
    main()

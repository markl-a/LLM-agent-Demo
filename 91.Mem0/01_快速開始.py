"""
Mem0 快速開始示例

本示例展示:
1. Mem0 基礎配置
2. 添加記憶
3. 搜索記憶
4. 基本操作演示
"""

from mem0 import Memory
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from dotenv import load_dotenv
import os

console = Console()
load_dotenv()


def initialize_memory():
    """初始化 Mem0"""
    try:
        console.print("\n[cyan]正在初始化 Mem0...[/cyan]")

        # 檢查 API Key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            console.print("[red]錯誤: 請在 .env 文件中設置 OPENAI_API_KEY[/red]")
            return None

        # 配置 Mem0
        config = {
            "llm": {
                "provider": "openai",
                "config": {
                    "model": "gpt-4",
                    "api_key": api_key,
                    "temperature": 0
                }
            }
        }

        # 初始化記憶
        memory = Memory.from_config(config)

        console.print("[green]✓ Mem0 初始化成功[/green]\n")

        return memory

    except Exception as e:
        console.print(f"[red]✗ 初始化失敗: {e}[/red]")
        return None


def add_memories(memory):
    """添加記憶"""
    try:
        console.print("[cyan]添加記憶...[/cyan]")

        # 準備記憶數據
        memories_to_add = [
            "用戶叫張三,是一名軟體工程師",
            "用戶喜歡喝咖啡,特別是美式咖啡",
            "用戶正在學習 AI 和機器學習",
            "用戶住在台北市",
            "用戶的興趣是爬山和閱讀"
        ]

        user_id = "user_123"

        # 添加記憶
        table = Table(title="添加的記憶")
        table.add_column("編號", style="cyan")
        table.add_column("內容", style="green")
        table.add_column("狀態", style="yellow")

        for idx, mem_text in enumerate(memories_to_add, 1):
            try:
                result = memory.add(
                    mem_text,
                    user_id=user_id
                )

                table.add_row(
                    str(idx),
                    mem_text,
                    "✓ 成功"
                )

            except Exception as e:
                table.add_row(
                    str(idx),
                    mem_text,
                    f"✗ 失敗: {str(e)[:20]}"
                )

        console.print(table)
        console.print()

        return user_id

    except Exception as e:
        console.print(f"[red]✗ 添加記憶失敗: {e}[/red]")
        return None


def search_memories(memory, user_id):
    """搜索記憶"""
    try:
        console.print("[cyan]搜索記憶...[/cyan]")

        # 定義查詢
        queries = [
            "用戶的職業是什麼?",
            "用戶喜歡什麼飲料?",
            "用戶的興趣愛好"
        ]

        for query in queries:
            console.print(f"\n[yellow]查詢: {query}[/yellow]")

            # 執行搜索
            results = memory.search(
                query=query,
                user_id=user_id
            )

            # 顯示結果
            if results:
                table = Table()
                table.add_column("排名", style="cyan")
                table.add_column("記憶內容", style="green")

                for idx, result in enumerate(results, 1):
                    memory_text = result.get("memory", "無內容")
                    table.add_row(str(idx), memory_text)

                console.print(table)
            else:
                console.print("[dim]無相關記憶[/dim]")

        console.print()

        return True

    except Exception as e:
        console.print(f"[red]✗ 搜索失敗: {e}[/red]")
        return False


def get_all_memories(memory, user_id):
    """獲取所有記憶"""
    try:
        console.print("[cyan]獲取所有記憶...[/cyan]")

        # 獲取用戶的所有記憶
        all_memories = memory.get_all(user_id=user_id)

        # 顯示記憶列表
        table = Table(title=f"用戶 {user_id} 的所有記憶")
        table.add_column("ID", style="cyan")
        table.add_column("內容", style="green")
        table.add_column("創建時間", style="yellow")

        for mem in all_memories:
            mem_id = mem.get("id", "N/A")
            mem_text = mem.get("memory", "無內容")
            created_at = mem.get("created_at", "未知")

            table.add_row(
                str(mem_id)[:8] + "...",
                mem_text[:60] + "..." if len(mem_text) > 60 else mem_text,
                created_at[:10] if created_at != "未知" else created_at
            )

        console.print(table)
        console.print(f"\n[green]總計: {len(all_memories)} 條記憶[/green]\n")

        return all_memories

    except Exception as e:
        console.print(f"[red]✗ 獲取記憶失敗: {e}[/red]")
        return []


def demonstrate_memory_operations(memory, user_id):
    """演示記憶操作"""
    try:
        console.print("[cyan]演示記憶操作...[/cyan]\n")

        # 1. 添加新記憶
        console.print("[yellow]1. 添加新記憶[/yellow]")
        memory.add(
            "用戶最近開始學習 LangChain 框架",
            user_id=user_id
        )
        console.print("[green]✓ 記憶已添加[/green]\n")

        # 2. 搜索剛添加的記憶
        console.print("[yellow]2. 搜索新添加的記憶[/yellow]")
        results = memory.search(
            "用戶在學習什麼框架?",
            user_id=user_id
        )

        if results:
            console.print(f"[green]找到記憶: {results[0].get('memory', '無')}[/green]\n")
        else:
            console.print("[yellow]未找到相關記憶[/yellow]\n")

        # 3. 統計記憶數量
        all_mems = memory.get_all(user_id=user_id)
        console.print(f"[yellow]3. 當前記憶總數: {len(all_mems)}[/yellow]\n")

        return True

    except Exception as e:
        console.print(f"[red]✗ 操作失敗: {e}[/red]")
        return False


def demonstrate_memory_features():
    """演示 Mem0 特性"""
    try:
        console.print("[cyan]Mem0 核心特性[/cyan]\n")

        features = [
            {
                "特性": "自動提取",
                "描述": "從對話中自動識別重要信息",
                "優勢": "無需手動標記"
            },
            {
                "特性": "語義搜索",
                "描述": "基於語義理解而非關鍵字匹配",
                "優勢": "更智能的檢索"
            },
            {
                "特性": "去重機制",
                "描述": "自動合併重複或相似的記憶",
                "優勢": "避免冗餘"
            },
            {
                "特性": "用戶隔離",
                "描述": "每個用戶獨立的記憶空間",
                "優勢": "隱私保護"
            }
        ]

        table = Table(title="Mem0 核心特性")
        table.add_column("特性", style="cyan")
        table.add_column("描述", style="green")
        table.add_column("優勢", style="yellow")

        for feature in features:
            table.add_row(
                feature["特性"],
                feature["描述"],
                feature["優勢"]
            )

        console.print(table)
        console.print()

    except Exception as e:
        console.print(f"[red]✗ 演示失敗: {e}[/red]")


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Mem0 快速開始示例[/bold cyan]\n"
        "[dim]展示 Mem0 的基礎功能[/dim]",
        border_style="cyan"
    ))

    # 1. 初始化 Mem0
    memory = initialize_memory()
    if not memory:
        console.print("[yellow]提示: 需要 OpenAI API Key 才能運行此示例[/yellow]")
        console.print("[dim]請在 .env 文件中設置: OPENAI_API_KEY=your-key[/dim]")
        return

    # 2. 添加記憶
    user_id = add_memories(memory)
    if not user_id:
        return

    # 3. 搜索記憶
    search_memories(memory, user_id)

    # 4. 獲取所有記憶
    get_all_memories(memory, user_id)

    # 5. 演示記憶操作
    demonstrate_memory_operations(memory, user_id)

    # 6. 展示特性
    demonstrate_memory_features()

    # 完成
    console.print("="*60)
    console.print("[bold green]✓ 快速開始示例完成！[/bold green]")
    console.print("\n[cyan]下一步:[/cyan]")
    console.print("  1. 查看 02_添加記憶.py 學習更多添加方式")
    console.print("  2. 查看 03_搜索記憶.py 學習高級搜索")
    console.print("  3. 查看 05_用戶記憶.py 學習多用戶管理")


if __name__ == "__main__":
    main()

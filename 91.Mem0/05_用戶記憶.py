"""
Mem0 用戶記憶示例

本示例展示:
1. 多用戶記憶隔離
2. 用戶記憶管理
3. 跨用戶操作
4. 用戶記憶統計
"""

from mem0 import Memory
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from dotenv import load_dotenv
import os

console = Console()
load_dotenv()

def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Mem0 用戶記憶示例[/bold cyan]\n"
        "[dim]展示多用戶記憶管理[/dim]",
        border_style="cyan"
    ))
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        console.print("[yellow]需要 OPENAI_API_KEY[/yellow]")
        return
    
    config = {"llm": {"provider": "openai", "config": {"model": "gpt-4", "api_key": api_key}}}
    memory = Memory.from_config(config)
    
    # 創建多個用戶的記憶
    console.print("\n[cyan]為不同用戶添加記憶...[/cyan]\n")
    
    users = [
        {"id": "alice", "memory": "Alice 喜歡喝咖啡"},
        {"id": "bob", "memory": "Bob 喜歡喝茶"},
        {"id": "charlie", "memory": "Charlie 喜歡喝果汁"}
    ]
    
    table = Table(title="用戶記憶")
    table.add_column("用戶ID", style="cyan")
    table.add_column("記憶", style="green")
    
    for user in users:
        memory.add(user["memory"], user_id=user["id"])
        table.add_row(user["id"], user["memory"])
    
    console.print(table)
    console.print()
    
    # 測試隔離
    console.print("[cyan]測試用戶隔離...[/cyan]\n")
    
    for user in users:
        results = memory.search("喜歡喝什麼", user_id=user["id"])
        if results:
            console.print(f"[yellow]{user['id']}:[/yellow] {results[0].get('memory', '無')}")
    
    console.print("\n" + "="*60)
    console.print("[bold green]✓ 用戶記憶示例完成！[/bold green]")
    console.print("\n[cyan]關鍵點:[/cyan]")
    console.print("  • 每個用戶有獨立的記憶空間")
    console.print("  • 記憶自動隔離,不會互相干擾")
    console.print("  • 可以輕鬆管理多用戶記憶")

if __name__ == "__main__":
    main()

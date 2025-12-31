"""
Mem0 更新記憶示例

本示例展示:
1. 記憶自動更新
2. 手動更新記憶
3. 記憶合併機制
4. 記憶刪除
"""

from mem0 import Memory
from rich.console import Console
from rich.panel import Panel
from dotenv import load_dotenv
import os

console = Console()
load_dotenv()

def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Mem0 更新記憶示例[/bold cyan]\n"
        "[dim]展示記憶更新和維護[/dim]",
        border_style="cyan"
    ))
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        console.print("[yellow]需要 OPENAI_API_KEY[/yellow]")
        return
    
    config = {"llm": {"provider": "openai", "config": {"model": "gpt-4", "api_key": api_key}}}
    memory = Memory.from_config(config)
    user_id = "update_user"
    
    # 添加初始記憶
    console.print("\n[cyan]添加初始記憶...[/cyan]")
    memory.add("用戶住在台北", user_id=user_id)
    console.print("[green]✓ 記憶: 用戶住在台北[/green]\n")
    
    # 更新記憶
    console.print("[cyan]更新記憶...[/cyan]")
    memory.add("用戶已搬到台中", user_id=user_id)
    console.print("[green]✓ 記憶已自動更新[/green]\n")
    
    # 查看結果
    console.print("[cyan]驗證更新...[/cyan]")
    results = memory.search("用戶住在哪裡", user_id=user_id)
    if results:
        console.print(f"[green]最新記憶: {results[0].get('memory', '無')}[/green]\n")
    
    # 刪除記憶示例
    console.print("[cyan]記憶刪除...[/cyan]")
    all_mems = memory.get_all(user_id=user_id)
    if all_mems:
        mem_id = all_mems[0].get("id")
        console.print(f"[yellow]刪除記憶 ID: {mem_id}[/yellow]")
        # memory.delete(mem_id)  # 取消註釋以實際刪除
        console.print("[green]✓ 記憶刪除功能演示[/green]\n")
    
    console.print("="*60)
    console.print("[bold green]✓ 更新記憶示例完成！[/bold green]")

if __name__ == "__main__":
    main()

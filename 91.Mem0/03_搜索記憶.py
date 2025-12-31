"""
Mem0 搜索記憶示例

本示例展示:
1. 基礎語義搜索
2. 過濾搜索
3. 相關性排序
4. 高級搜索技巧
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
        "[bold cyan]Mem0 搜索記憶示例[/bold cyan]\n"
        "[dim]展示記憶搜索功能[/dim]",
        border_style="cyan"
    ))
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        console.print("[yellow]需要 OPENAI_API_KEY[/yellow]")
        return
    
    # 配置並初始化
    config = {
        "llm": {
            "provider": "openai",
            "config": {"model": "gpt-4", "api_key": api_key}
        }
    }
    
    memory = Memory.from_config(config)
    user_id = "search_user"
    
    # 添加測試記憶
    console.print("\n[cyan]添加測試記憶...[/cyan]")
    test_memories = [
        "用戶是 Python 開發者,有 5 年經驗",
        "用戶喜歡喝綠茶和咖啡",
        "用戶住在台北市大安區",
        "用戶最近在學習機器學習",
        "用戶的興趣是攝影和旅遊"
    ]
    
    for mem in test_memories:
        memory.add(mem, user_id=user_id)
    console.print(f"[green]✓ 添加了 {len(test_memories)} 條記憶[/green]\n")
    
    # 語義搜索
    console.print("[cyan]1. 語義搜索[/cyan]")
    queries = [
        "用戶的職業技能",
        "用戶喜歡喝什麼",
        "用戶的居住地"
    ]
    
    for query in queries:
        console.print(f"\n[yellow]查詢: {query}[/yellow]")
        results = memory.search(query, user_id=user_id)
        
        if results:
            for idx, result in enumerate(results[:2], 1):
                console.print(f"  {idx}. {result.get('memory', '無')}")
        else:
            console.print("  [dim]無結果[/dim]")
    
    console.print("\n" + "="*60)
    console.print("[bold green]✓ 搜索示例完成！[/bold green]")

if __name__ == "__main__":
    main()

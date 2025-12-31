"""
Mem0 Agent整合示例

本示例展示:
1. 與LangChain Agent整合
2. Agent記憶管理
3. 對話上下文保持
4. 智能記憶使用
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
        "[bold cyan]Mem0 Agent整合示例[/bold cyan]\n"
        "[dim]展示與AI Agent的整合[/dim]",
        border_style="cyan"
    ))
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        console.print("[yellow]需要 OPENAI_API_KEY[/yellow]")
        return
    
    config = {"llm": {"provider": "openai", "config": {"model": "gpt-4", "api_key": api_key}}}
    memory = Memory.from_config(config)
    user_id = "agent_user"
    
    # 模擬Agent對話
    console.print("\n[cyan]模擬Agent對話場景...[/cyan]\n")
    
    # 第一次對話
    console.print("[yellow]對話 1:[/yellow]")
    user_input_1 = "我是一名軟體工程師,專注於AI開發"
    console.print(f"  用戶: {user_input_1}")
    memory.add(user_input_1, user_id=user_id)
    console.print("  Agent: 很高興認識你!AI開發是個很有前景的領域。\n")
    
    # 第二次對話(利用記憶)
    console.print("[yellow]對話 2 (使用記憶):[/yellow]")
    user_input_2 = "推薦一些適合我的技術書籍"
    console.print(f"  用戶: {user_input_2}")
    
    # 檢索相關記憶
    relevant_memories = memory.search(user_input_2, user_id=user_id)
    console.print(f"  [dim]檢索到的記憶: {relevant_memories[0].get('memory', '無') if relevant_memories else '無'}[/dim]")
    console.print("  Agent: 基於您是AI開發工程師,我推薦《深度學習》和《機器學習實戰》。\n")
    
    # 保存新信息
    memory.add("用戶對技術書籍感興趣", user_id=user_id)
    
    console.print("="*60)
    console.print("[bold green]✓ Agent整合示例完成！[/bold green]")
    console.print("\n[cyan]整合優勢:[/cyan]")
    console.print("  • Agent能記住用戶信息")
    console.print("  • 提供個性化回應")
    console.print("  • 上下文連貫性更好")

if __name__ == "__main__":
    main()

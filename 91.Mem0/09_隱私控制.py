"""
Mem0 隱私控制示例

本示例展示:
1. 記憶訪問控制
2. 敏感信息處理
3. 記憶刪除和清理
4. 隱私合規
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
        "[bold cyan]Mem0 隱私控制示例[/bold cyan]\n"
        "[dim]展示隱私和安全管理[/dim]",
        border_style="cyan"
    ))
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        console.print("[yellow]需要 OPENAI_API_KEY[/yellow]")
        return
    
    config = {"llm": {"provider": "openai", "config": {"model": "gpt-4", "api_key": api_key}}}
    memory = Memory.from_config(config)
    user_id = "privacy_user"
    
    # 隱私控制最佳實踐
    console.print("\n[cyan]隱私控制最佳實踐[/cyan]\n")
    
    practices = [
        {
            "實踐": "數據最小化",
            "描述": "只存儲必要的信息",
            "示例": "存儲用戶偏好,而非詳細個人信息"
        },
        {
            "實踐": "用戶控制",
            "描述": "用戶可查看和刪除自己的記憶",
            "示例": "提供記憶管理界面"
        },
        {
            "實踐": "訪問隔離",
            "描述": "嚴格的用戶記憶隔離",
            "示例": "通過user_id完全隔離"
        },
        {
            "實踐": "敏感信息",
            "描述": "避免存儲敏感數據",
            "示例": "不存儲密碼、身份證號等"
        }
    ]
    
    table = Table(title="隱私保護措施")
    table.add_column("最佳實踐", style="cyan")
    table.add_column("描述", style="green")
    table.add_column("示例", style="yellow")
    
    for practice in practices:
        table.add_row(
            practice["實踐"],
            practice["描述"],
            practice["示例"]
        )
    
    console.print(table)
    console.print()
    
    # 記憶刪除示例
    console.print("[cyan]記憶刪除操作[/cyan]\n")
    
    # 添加測試記憶
    memory.add("測試記憶 - 待刪除", user_id=user_id)
    console.print("[green]✓ 添加測試記憶[/green]")
    
    # 獲取所有記憶
    all_mems = memory.get_all(user_id=user_id)
    console.print(f"[yellow]當前記憶數: {len(all_mems)}[/yellow]")
    
    # 演示刪除操作(不實際執行)
    console.print("\n[yellow]刪除操作示例:[/yellow]")
    console.print("  • 單條刪除: memory.delete(memory_id)")
    console.print("  • 批量刪除: memory.delete_all(user_id)")
    console.print()
    
    # 合規要求
    console.print("[cyan]隱私合規要求[/cyan]\n")
    
    compliance = [
        "✅ GDPR - 用戶數據刪除權",
        "✅ CCPA - 加州消費者隱私法",
        "✅ 數據加密 - 傳輸和存儲加密",
        "✅ 訪問日誌 - 記錄所有訪問操作"
    ]
    
    for item in compliance:
        console.print(f"  {item}")
    
    console.print()
    console.print("="*60)
    console.print("[bold green]✓ 隱私控制示例完成！[/bold green]")
    console.print("\n[cyan]關鍵要點:[/cyan]")
    console.print("  • 用戶隔離: 確保記憶完全隔離")
    console.print("  • 數據最小化: 只存必要信息")
    console.print("  • 刪除權利: 用戶可刪除記憶")
    console.print("  • 合規性: 遵守隱私法規")

if __name__ == "__main__":
    main()

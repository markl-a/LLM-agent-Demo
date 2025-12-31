"""
Mem0 多模態記憶示例

本示例展示:
1. 文本記憶
2. 圖像描述記憶  
3. 結構化數據記憶
4. 混合模態記憶
"""

from mem0 import Memory
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from dotenv import load_dotenv
import os
import json

console = Console()
load_dotenv()

def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Mem0 多模態記憶示例[/bold cyan]\n"
        "[dim]展示處理多種類型的記憶[/dim]",
        border_style="cyan"
    ))
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        console.print("[yellow]需要 OPENAI_API_KEY[/yellow]")
        return
    
    config = {"llm": {"provider": "openai", "config": {"model": "gpt-4", "api_key": api_key}}}
    memory = Memory.from_config(config)
    user_id = "multimodal_user"
    
    # 文本記憶
    console.print("\n[cyan]1. 文本記憶[/cyan]")
    text_memory = "用戶最喜歡的電影是《星際效應》"
    memory.add(text_memory, user_id=user_id)
    console.print(f"[green]✓ {text_memory}[/green]\n")
    
    # 圖像描述記憶
    console.print("[cyan]2. 圖像描述記憶[/cyan]")
    image_memory = "用戶分享了一張在台北101拍攝的夜景照片"
    memory.add(image_memory, user_id=user_id)
    console.print(f"[green]✓ {image_memory}[/green]\n")
    
    # 結構化數據記憶
    console.print("[cyan]3. 結構化數據記憶[/cyan]")
    structured_data = {
        "用戶偏好": {
            "程式語言": ["Python", "JavaScript"],
            "框架": ["Django", "React"],
            "工具": ["Docker", "Git"]
        }
    }
    struct_memory = f"用戶的技術棧偏好: {json.dumps(structured_data, ensure_ascii=False)}"
    memory.add(struct_memory, user_id=user_id)
    console.print(f"[green]✓ 結構化數據已保存[/green]\n")
    
    # 顯示所有記憶
    console.print("[cyan]4. 查看所有多模態記憶[/cyan]")
    all_memories = memory.get_all(user_id=user_id)
    
    table = Table(title="多模態記憶列表")
    table.add_column("類型", style="cyan")
    table.add_column("記憶內容", style="green")
    
    memory_types = ["文本", "圖像描述", "結構化數據"]
    for idx, mem in enumerate(all_memories[:3]):
        table.add_row(
            memory_types[idx] if idx < len(memory_types) else "其他",
            mem.get("memory", "無")[:60] + "..." if len(mem.get("memory", "")) > 60 else mem.get("memory", "無")
        )
    
    console.print(table)
    console.print()
    
    console.print("="*60)
    console.print("[bold green]✓ 多模態記憶示例完成！[/bold green]")
    console.print("\n[cyan]支持的模態:[/cyan]")
    console.print("  • 文本: 直接文本記憶")
    console.print("  • 圖像: 圖像描述和視覺信息")
    console.print("  • 結構化: JSON、表格等數據")

if __name__ == "__main__":
    main()

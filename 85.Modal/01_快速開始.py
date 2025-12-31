"""
Modal 快速開始示例

本示例展示：
1. 創建第一個 Modal 應用
2. 定義雲端函數
3. 本地調用遠程函數
4. 查看執行日誌
"""

import modal
from rich.console import Console
from rich.panel import Panel

console = Console()

# 創建 Modal 應用
# 應用名稱必須唯一
app = modal.App("quickstart-demo")


@app.function()
def hello(name: str) -> str:
    """
    最簡單的雲端函數

    這個函數會在 Modal 雲端執行，而不是在本地執行
    """
    import time
    import platform

    # 打印一些信息（會顯示在 Modal 日誌中）
    print(f"正在雲端處理請求: {name}")
    print(f"運行平台: {platform.system()}")
    print(f"Python 版本: {platform.python_version()}")

    # 模擬一些處理
    time.sleep(1)

    result = f"Hello, {name}! 這條消息來自 Modal 雲端 ☁️"
    print(f"處理完成: {result}")

    return result


@app.function()
def compute(x: int, y: int) -> dict:
    """
    執行簡單計算的雲端函數

    Args:
        x: 第一個數字
        y: 第二個數字

    Returns:
        包含計算結果的字典
    """
    print(f"正在計算: {x} 和 {y}")

    return {
        "sum": x + y,
        "product": x * y,
        "difference": x - y,
        "division": x / y if y != 0 else None
    }


@app.function()
def list_processing(items: list) -> dict:
    """
    處理列表數據

    Args:
        items: 要處理的列表

    Returns:
        處理結果
    """
    print(f"收到 {len(items)} 個項目")

    # 處理每個項目
    processed = [item.upper() if isinstance(item, str) else item * 2 for item in items]

    print(f"處理完成: {processed}")

    return {
        "original_count": len(items),
        "processed": processed,
        "total": sum(x for x in processed if isinstance(x, (int, float)))
    }


@app.local_entrypoint()
def main():
    """
    本地入口函數

    這個函數在本地執行，用於調用雲端函數
    """
    console.print(Panel.fit(
        "[bold cyan]Modal 快速開始示例[/bold cyan]\n"
        "[dim]創建和調用雲端函數[/dim]",
        border_style="cyan"
    ))

    console.print("\n[cyan]1. 調用簡單的 hello 函數...[/cyan]")

    # 調用雲端函數（使用 .remote() 方法）
    result1 = hello.remote("World")
    console.print(f"[green]結果: {result1}[/green]")

    console.print("\n[cyan]2. 調用計算函數...[/cyan]")
    result2 = compute.remote(10, 5)
    console.print(f"[green]結果: {result2}[/green]")

    console.print("\n[cyan]3. 處理列表數據...[/cyan]")
    test_items = ["hello", "world", 5, 10]
    result3 = list_processing.remote(test_items)
    console.print(f"[green]結果: {result3}[/green]")

    console.print("\n[cyan]4. 批量調用多個函數...[/cyan]")

    # 可以並行調用多個函數
    names = ["Alice", "Bob", "Charlie"]

    # 使用列表推導並行調用
    results = [hello.remote(name) for name in names]

    # 顯示結果
    for i, result in enumerate(results):
        console.print(f"[green]  {i+1}. {result}[/green]")

    console.print("\n" + "="*60)
    console.print("[bold green]✓ 快速開始示例完成！[/bold green]")
    console.print("\n[cyan]接下來可以嘗試:[/cyan]")
    console.print("  1. 運行其他示例了解更多功能")
    console.print("  2. 查看 Modal Dashboard: https://modal.com/apps")
    console.print("  3. 閱讀官方文檔: https://modal.com/docs")


def print_usage():
    """打印使用說明"""
    console.print("\n" + "="*60)
    console.print("[bold cyan]如何運行此示例:[/bold cyan]")
    console.print("""
[yellow]1. 首次使用 - 設置 Modal token:[/yellow]
   modal token new

[yellow]2. 運行此腳本:[/yellow]
   modal run 01_快速開始.py

[yellow]3. 部署為持久服務:[/yellow]
   modal deploy 01_快速開始.py

[yellow]4. 查看應用日誌:[/yellow]
   modal app logs quickstart-demo

[green]重要概念:[/green]
  • @app.function() - 將函數標記為雲端函數
  • .remote() - 在雲端執行函數
  • @app.local_entrypoint() - 本地入口點
    """)
    console.print("="*60 + "\n")


if __name__ == "__main__":
    # 打印使用說明
    print_usage()

    console.print("[yellow]提示: 使用 'modal run 01_快速開始.py' 運行此示例[/yellow]\n")

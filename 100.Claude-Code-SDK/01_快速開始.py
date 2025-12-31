"""
Claude Code SDK 快速開始示例

本示例展示：
1. SDK 初始化
2. 基本對話
3. 錯誤處理
4. 環境配置
"""

import os
from anthropic import Anthropic, APIError, APIConnectionError, RateLimitError
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from dotenv import load_dotenv

console = Console()

# 加載環境變量
load_dotenv()


def check_api_key():
    """檢查 API Key 配置"""
    console.print("\n[cyan]檢查 API Key 配置...[/cyan]")

    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        console.print("[red]✗ 未找到 ANTHROPIC_API_KEY 環境變量[/red]")
        console.print("\n[yellow]請設置環境變量：[/yellow]")
        console.print("  export ANTHROPIC_API_KEY='your-api-key'")
        console.print("\n[yellow]或創建 .env 文件：[/yellow]")
        console.print("  ANTHROPIC_API_KEY=your-api-key")
        return False

    console.print("[green]✓ API Key 已配置[/green]")
    console.print(f"[dim]Key: {api_key[:10]}...{api_key[-4:]}[/dim]\n")
    return True


def initialize_client():
    """初始化 Claude 客戶端"""
    try:
        console.print("[cyan]初始化 Claude 客戶端...[/cyan]")

        # 方式 1: 使用環境變量（推薦）
        client = Anthropic()

        # 方式 2: 明確指定 API Key
        # client = Anthropic(api_key="your-api-key")

        console.print("[green]✓ 客戶端初始化成功[/green]\n")
        return client

    except Exception as e:
        console.print(f"[red]✗ 初始化失敗: {e}[/red]")
        return None


def simple_chat(client):
    """簡單對話示例"""
    try:
        console.print("[cyan]執行簡單對話...[/cyan]")

        # 創建消息
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": "你好！請用一句話介紹你自己。"
                }
            ]
        )

        # 顯示響應
        response_text = message.content[0].text

        console.print("\n[green]Claude 的回答：[/green]")
        console.print(Panel(response_text, border_style="green"))

        # 顯示元數據
        table = Table(title="響應元數據")
        table.add_column("屬性", style="cyan")
        table.add_column("值", style="yellow")

        table.add_row("模型", message.model)
        table.add_row("角色", message.role)
        table.add_row("輸入 Tokens", str(message.usage.input_tokens))
        table.add_row("輸出 Tokens", str(message.usage.output_tokens))
        table.add_row("停止原因", message.stop_reason)

        console.print(table)
        console.print()

        return True

    except RateLimitError:
        console.print("[red]✗ 速率限制：請求過於頻繁[/red]")
        return False
    except APIConnectionError:
        console.print("[red]✗ 網絡連接錯誤：請檢查網絡[/red]")
        return False
    except APIError as e:
        console.print(f"[red]✗ API 錯誤: {e}[/red]")
        return False


def chat_with_system_prompt(client):
    """使用系統提示詞的對話"""
    try:
        console.print("[cyan]使用系統提示詞的對話...[/cyan]")

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            system="你是一個專業的 Python 程序員助手，請用簡潔專業的方式回答問題。",
            messages=[
                {
                    "role": "user",
                    "content": "什麼是列表推導式？用一個例子說明。"
                }
            ]
        )

        response_text = message.content[0].text

        console.print("\n[green]Claude 的專業回答：[/green]")
        console.print(Panel(response_text, border_style="green"))
        console.print()

        return True

    except Exception as e:
        console.print(f"[red]✗ 對話失敗: {e}[/red]")
        return False


def multi_turn_chat(client):
    """多輪對話示例"""
    try:
        console.print("[cyan]多輪對話示例...[/cyan]")

        # 對話歷史
        messages = [
            {
                "role": "user",
                "content": "我想學習 Python，應該從哪裡開始？"
            }
        ]

        # 第一輪
        response1 = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=512,
            messages=messages
        )

        assistant_msg1 = response1.content[0].text
        console.print("\n[yellow]第一輪對話：[/yellow]")
        console.print(f"[blue]用戶：[/blue] {messages[0]['content']}")
        console.print(f"[green]Claude：[/green] {assistant_msg1[:100]}...\n")

        # 添加 Assistant 回答到歷史
        messages.append({
            "role": "assistant",
            "content": assistant_msg1
        })

        # 第二輪
        messages.append({
            "role": "user",
            "content": "那麼推薦哪些學習資源？"
        })

        response2 = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=512,
            messages=messages
        )

        assistant_msg2 = response2.content[0].text
        console.print("[yellow]第二輪對話：[/yellow]")
        console.print(f"[blue]用戶：[/blue] {messages[2]['content']}")
        console.print(f"[green]Claude：[/green] {assistant_msg2[:100]}...\n")

        console.print("[dim]提示：多輪對話需要維護完整的對話歷史[/dim]\n")

        return True

    except Exception as e:
        console.print(f"[red]✗ 多輪對話失敗: {e}[/red]")
        return False


def demonstrate_error_handling(client):
    """錯誤處理示例"""
    console.print("[cyan]錯誤處理示例...[/cyan]")

    # 示例 1: 處理無效模型
    try:
        console.print("\n[yellow]測試：使用無效模型名稱[/yellow]")
        client.messages.create(
            model="invalid-model-name",
            max_tokens=100,
            messages=[{"role": "user", "content": "Hello"}]
        )
    except APIError as e:
        console.print(f"[green]✓ 成功捕獲錯誤: {type(e).__name__}[/green]")
        console.print(f"[dim]錯誤信息: {str(e)[:80]}...[/dim]\n")

    # 示例 2: 處理過長的輸入
    try:
        console.print("[yellow]測試：max_tokens 設置為 0[/yellow]")
        client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=0,  # 無效值
            messages=[{"role": "user", "content": "Hello"}]
        )
    except APIError as e:
        console.print(f"[green]✓ 成功捕獲錯誤: {type(e).__name__}[/green]")
        console.print(f"[dim]錯誤信息: {str(e)[:80]}...[/dim]\n")


def show_best_practices():
    """顯示最佳實踐"""
    console.print("\n[bold cyan]最佳實踐建議：[/bold cyan]")

    best_practices = [
        ("API Key 安全", "使用環境變量，不要硬編碼在代碼中"),
        ("錯誤處理", "始終使用 try-except 處理 API 調用"),
        ("模型選擇", "根據任務選擇合適的模型（Haiku/Sonnet/Opus）"),
        ("Token 管理", "合理設置 max_tokens 避免不必要的成本"),
        ("系統提示詞", "使用系統提示詞定義 AI 的行為和角色"),
        ("對話歷史", "多輪對話時維護完整的消息歷史"),
    ]

    table = Table(title="開發建議", show_header=True)
    table.add_column("主題", style="cyan", width=15)
    table.add_column("建議", style="green", width=45)

    for topic, advice in best_practices:
        table.add_row(topic, advice)

    console.print(table)
    console.print()


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Claude Code SDK 快速開始[/bold cyan]\n"
        "[dim]學習 Claude API 的基本使用[/dim]",
        border_style="cyan"
    ))

    # 1. 檢查 API Key
    if not check_api_key():
        return

    # 2. 初始化客戶端
    client = initialize_client()
    if not client:
        return

    # 3. 簡單對話
    simple_chat(client)

    # 4. 系統提示詞
    chat_with_system_prompt(client)

    # 5. 多輪對話
    multi_turn_chat(client)

    # 6. 錯誤處理
    demonstrate_error_handling(client)

    # 7. 最佳實踐
    show_best_practices()

    # 完成
    console.print("="*60)
    console.print("[bold green]✓ 快速開始示例完成！[/bold green]")
    console.print("\n[cyan]下一步：[/cyan]")
    console.print("  1. 查看 02_對話管理.py 學習對話管理")
    console.print("  2. 查看 03_工具使用.py 學習工具調用")
    console.print("  3. 查看 04_流式輸出.py 學習流式響應")


if __name__ == "__main__":
    main()

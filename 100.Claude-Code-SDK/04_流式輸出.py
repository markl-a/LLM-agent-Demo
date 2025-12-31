"""
Claude Code SDK 流式輸出示例

本示例展示：
1. 流式文本輸出
2. 流式事件處理
3. 流式工具調用
4. 實時用戶體驗優化
"""

import os
import time
from anthropic import Anthropic
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from dotenv import load_dotenv

console = Console()
load_dotenv()


def demo_basic_streaming():
    """基本流式輸出示例"""
    console.print("\n[bold cyan]1. 基本流式輸出[/bold cyan]\n")

    client = Anthropic()

    console.print("[yellow]用戶：[/yellow] 請講一個關於 AI 的故事\n")
    console.print("[green]Claude（流式）：[/green]")

    # 使用流式 API
    with client.messages.stream(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": "請講一個關於 AI 的簡短故事（3-4 段）"}
        ]
    ) as stream:
        for text in stream.text_stream:
            console.print(text, end="")

    console.print("\n")


def demo_streaming_with_events():
    """流式事件處理示例"""
    console.print("[bold cyan]2. 流式事件處理[/bold cyan]\n")

    client = Anthropic()

    console.print("[yellow]監控流式事件...[/yellow]\n")

    message_start_received = False
    content_blocks = []
    message_delta_count = 0

    with client.messages.stream(
        model="claude-3-5-sonnet-20241022",
        max_tokens=512,
        messages=[
            {"role": "user", "content": "用三句話介紹量子計算"}
        ]
    ) as stream:
        for event in stream:
            event_type = event.type

            if event_type == "message_start":
                message_start_received = True
                console.print("[dim]📨 收到消息開始事件[/dim]")

            elif event_type == "content_block_start":
                console.print(f"[dim]📝 內容塊開始 (index: {event.index})[/dim]")
                content_blocks.append("")

            elif event_type == "content_block_delta":
                if hasattr(event.delta, "text"):
                    content_blocks[-1] += event.delta.text
                    message_delta_count += 1

            elif event_type == "content_block_stop":
                console.print(f"[dim]✅ 內容塊結束[/dim]")

            elif event_type == "message_delta":
                console.print(f"[dim]📊 消息元數據更新[/dim]")

            elif event_type == "message_stop":
                console.print(f"[dim]🏁 消息完成[/dim]\n")

    # 顯示統計
    console.print(f"[cyan]事件統計：[/cyan]")
    console.print(f"  • Delta 事件數：{message_delta_count}")
    console.print(f"  • 內容塊數：{len(content_blocks)}")
    console.print(f"\n[green]完整內容：[/green]")
    console.print(Panel("".join(content_blocks), border_style="green"))
    console.print()


def demo_progressive_display():
    """漸進式顯示示例"""
    console.print("[bold cyan]3. 漸進式顯示（Live）[/bold cyan]\n")

    client = Anthropic()

    console.print("[yellow]用戶：[/yellow] 解釋什麼是機器學習\n")

    accumulated_text = ""

    with Live(console=console, refresh_per_second=10) as live:
        with client.messages.stream(
            model="claude-3-5-sonnet-20241022",
            max_tokens=512,
            messages=[
                {"role": "user", "content": "用一段話解釋什麼是機器學習"}
            ]
        ) as stream:
            for text in stream.text_stream:
                accumulated_text += text
                # 使用 Markdown 渲染
                live.update(Panel(
                    Markdown(accumulated_text),
                    title="Claude 的回答",
                    border_style="green"
                ))

    console.print()


def demo_streaming_with_thinking():
    """帶思考過程的流式輸出"""
    console.print("[bold cyan]4. 帶思考過程的流式輸出[/bold cyan]\n")

    client = Anthropic()

    console.print("[yellow]用戶：[/yellow] 如何優化 Python 代碼性能？\n")

    thinking_phase = True
    thinking_text = ""
    response_text = ""

    with client.messages.stream(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": "列出 5 個優化 Python 代碼性能的方法"}
        ]
    ) as stream:
        console.print("[dim]🤔 思考中...[/dim]")

        for text in stream.text_stream:
            if thinking_phase and len(response_text) < 50:
                # 模擬思考階段（實際上 Claude 沒有明確的思考階段）
                thinking_text += text
                console.print("[dim].[/dim]", end="")
            else:
                if thinking_phase:
                    thinking_phase = False
                    console.print("\n\n[green]📝 回答：[/green]\n")

                response_text += text
                console.print(text, end="")

    console.print("\n")


def demo_streaming_cancellation():
    """流式取消示例"""
    console.print("[bold cyan]5. 流式取消[/bold cyan]\n")

    client = Anthropic()

    console.print("[yellow]演示：接收部分內容後取消[/yellow]\n")

    token_count = 0
    max_tokens_to_receive = 50

    try:
        with client.messages.stream(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": "詳細解釋神經網絡的工作原理"}
            ]
        ) as stream:
            for text in stream.text_stream:
                console.print(text, end="")
                token_count += len(text.split())

                # 當接收到足夠的內容時取消
                if token_count >= max_tokens_to_receive:
                    console.print("\n\n[yellow]⚠️  已取消流式傳輸[/yellow]")
                    break

    except Exception as e:
        console.print(f"\n[red]錯誤：{e}[/red]")

    console.print()


def demo_streaming_with_progress():
    """帶進度指示的流式輸出"""
    console.print("[bold cyan]6. 帶進度指示的流式輸出[/bold cyan]\n")

    client = Anthropic()

    console.print("[yellow]用戶：[/yellow] 生成一篇技術文章大綱\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]正在生成...", total=None)

        accumulated_text = ""
        with client.messages.stream(
            model="claude-3-5-sonnet-20241022",
            max_tokens=512,
            messages=[
                {"role": "user", "content": "為'深度學習入門'這個主題生成文章大綱"}
            ]
        ) as stream:
            for text in stream.text_stream:
                accumulated_text += text

                # 更新進度描述
                char_count = len(accumulated_text)
                progress.update(
                    task,
                    description=f"[cyan]已生成 {char_count} 個字符..."
                )

        progress.update(task, description="[green]✓ 生成完成")

    console.print(f"\n[green]生成的內容：[/green]")
    console.print(Panel(accumulated_text, border_style="green"))
    console.print()


def demo_streaming_comparison():
    """流式 vs 非流式對比"""
    console.print("[bold cyan]7. 流式 vs 非流式對比[/bold cyan]\n")

    client = Anthropic()
    query = "用一段話介紹 Python"

    # 非流式
    console.print("[yellow]⏱️  非流式請求...[/yellow]")
    start_time = time.time()

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=256,
        messages=[{"role": "user", "content": query}]
    )

    non_streaming_time = time.time() - start_time
    console.print(f"[cyan]完成時間：{non_streaming_time:.2f} 秒[/cyan]")
    console.print(f"[dim]需要等待全部內容生成完成[/dim]\n")

    # 流式
    console.print("[yellow]⚡ 流式請求...[/yellow]")
    start_time = time.time()
    first_token_time = None

    with client.messages.stream(
        model="claude-3-5-sonnet-20241022",
        max_tokens=256,
        messages=[{"role": "user", "content": query}]
    ) as stream:
        for i, text in enumerate(stream.text_stream):
            if i == 0:
                first_token_time = time.time() - start_time
            # 不打印，只是測量時間
            pass

    streaming_time = time.time() - start_time

    console.print(f"[cyan]首字時間：{first_token_time:.2f} 秒[/cyan]")
    console.print(f"[cyan]完成時間：{streaming_time:.2f} 秒[/cyan]")
    console.print(f"[green]✓ 用戶體驗提升：{((1 - first_token_time/non_streaming_time) * 100):.1f}%[/green]\n")


def show_best_practices():
    """流式輸出最佳實踐"""
    console.print("[bold cyan]最佳實踐[/bold cyan]\n")

    practices = [
        ("即時反饋", "立即顯示第一個 token，改善用戶體驗"),
        ("進度指示", "使用進度條或動畫指示處理中"),
        ("優雅降級", "如果流式失敗，回退到非流式"),
        ("取消支持", "允許用戶取消長時間運行的請求"),
        ("錯誤處理", "妥善處理流式過程中的錯誤"),
        ("內容緩衝", "適當緩衝避免過於頻繁的 UI 更新"),
    ]

    for practice, description in practices:
        console.print(f"[cyan]• {practice}：[/cyan]{description}")

    console.print()


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Claude Code SDK 流式輸出[/bold cyan]\n"
        "[dim]學習如何使用流式 API 提升用戶體驗[/dim]",
        border_style="cyan"
    ))

    # 1. 基本流式
    demo_basic_streaming()

    # 2. 事件處理
    demo_streaming_with_events()

    # 3. 漸進式顯示
    demo_progressive_display()

    # 4. 思考過程
    demo_streaming_with_thinking()

    # 5. 取消流式
    demo_streaming_cancellation()

    # 6. 進度指示
    demo_streaming_with_progress()

    # 7. 性能對比
    demo_streaming_comparison()

    # 最佳實踐
    show_best_practices()

    # 完成
    console.print("="*60)
    console.print("[bold green]✓ 流式輸出示例完成！[/bold green]")
    console.print("\n[cyan]關鍵要點：[/cyan]")
    console.print("  • 流式輸出顯著改善用戶體驗")
    console.print("  • 監控流式事件實現細粒度控制")
    console.print("  • 使用 Live 實現優雅的實時更新")
    console.print("  • 支持取消以應對用戶中斷")


if __name__ == "__main__":
    main()

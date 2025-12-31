"""
Ollama 流式輸出示例

本示例展示：
1. 基礎流式輸出
2. 流式對話
3. 實時進度顯示
4. 流式數據處理
5. 打字機效果
"""

import ollama
import time
import sys
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


def basic_streaming(model_name='llama3.2'):
    """基礎流式輸出"""
    try:
        console.print("\n[bold cyan]基礎流式輸出[/bold cyan]")

        user_message = "請用三個段落介紹人工智能的發展歷史"

        console.print(f"\n[bold]用戶:[/bold] {user_message}")
        console.print("\n[bold green]助手:[/bold green]")

        # 使用流式輸出
        stream = ollama.chat(
            model=model_name,
            messages=[
                {
                    'role': 'user',
                    'content': user_message
                }
            ],
            stream=True
        )

        # 逐塊接收並打印
        full_response = ""
        for chunk in stream:
            content = chunk['message']['content']
            full_response += content
            console.print(content, end='')

        console.print("\n")  # 換行

        return full_response

    except Exception as e:
        console.print(f"\n[red]流式輸出失敗: {e}[/red]")
        return None


def streaming_with_typewriter_effect(model_name='llama3.2'):
    """打字機效果的流式輸出"""
    try:
        console.print("\n[bold cyan]打字機效果流式輸出[/bold cyan]")

        user_message = "用一段話描述量子計算的原理"

        console.print(f"\n[bold]用戶:[/bold] {user_message}")
        console.print("\n[bold green]助手:[/bold green] ", end='')

        stream = ollama.chat(
            model=model_name,
            messages=[
                {
                    'role': 'user',
                    'content': user_message
                }
            ],
            stream=True
        )

        full_response = ""
        for chunk in stream:
            content = chunk['message']['content']
            full_response += content

            # 打字機效果：逐字符輸出
            for char in content:
                print(char, end='', flush=True)
                time.sleep(0.01)  # 控制打字速度

        print("\n")  # 換行

        return full_response

    except Exception as e:
        console.print(f"\n[red]打字機效果失敗: {e}[/red]")
        return None


def streaming_with_live_panel(model_name='llama3.2'):
    """使用 Rich Live 面板顯示流式輸出"""
    try:
        console.print("\n[bold cyan]Live 面板流式輸出[/bold cyan]")

        user_message = "解釋什麼是區塊鏈技術"

        console.print(f"\n[bold]用戶:[/bold] {user_message}\n")

        stream = ollama.chat(
            model=model_name,
            messages=[
                {
                    'role': 'user',
                    'content': user_message
                }
            ],
            stream=True
        )

        full_response = ""

        # 使用 Live 顯示更新
        with Live(
            Panel("", title="[bold green]AI 正在思考...[/bold green]", border_style="green"),
            console=console,
            refresh_per_second=10
        ) as live:
            for chunk in stream:
                content = chunk['message']['content']
                full_response += content

                # 更新面板內容
                live.update(
                    Panel(
                        Markdown(full_response),
                        title="[bold green]助手響應[/bold green]",
                        border_style="green"
                    )
                )

        return full_response

    except Exception as e:
        console.print(f"[red]Live 面板流式輸出失敗: {e}[/red]")
        return None


def streaming_multi_turn(model_name='llama3.2'):
    """流式多輪對話"""
    try:
        console.print("\n[bold cyan]流式多輪對話[/bold cyan]")

        # 對話歷史
        conversation = []

        # 多輪對話
        questions = [
            "什麼是深度學習？",
            "它與機器學習有什麼區別？",
            "請舉一個實際應用的例子"
        ]

        for i, question in enumerate(questions, 1):
            console.print(f"\n[bold yellow]第 {i} 輪[/bold yellow]")
            console.print(f"[bold]用戶:[/bold] {question}")

            # 添加用戶消息
            conversation.append({
                'role': 'user',
                'content': question
            })

            console.print("[bold green]助手:[/bold green] ", end='')

            # 流式獲取響應
            stream = ollama.chat(
                model=model_name,
                messages=conversation,
                stream=True
            )

            full_response = ""
            for chunk in stream:
                content = chunk['message']['content']
                full_response += content
                console.print(content, end='')

            console.print("\n")  # 換行

            # 添加助手響應到歷史
            conversation.append({
                'role': 'assistant',
                'content': full_response
            })

        return conversation

    except Exception as e:
        console.print(f"[red]流式多輪對話失敗: {e}[/red]")
        return None


def streaming_with_progress(model_name='llama3.2'):
    """帶進度指示的流式輸出"""
    try:
        console.print("\n[bold cyan]帶進度指示的流式輸出[/bold cyan]")

        user_message = "列出 5 種編程語言及其主要用途"

        console.print(f"\n[bold]用戶:[/bold] {user_message}\n")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("生成響應中...", total=None)

            stream = ollama.chat(
                model=model_name,
                messages=[
                    {
                        'role': 'user',
                        'content': user_message
                    }
                ],
                stream=True
            )

            full_response = ""
            token_count = 0

            for chunk in stream:
                content = chunk['message']['content']
                full_response += content
                token_count += 1

                # 更新進度描述
                progress.update(
                    task,
                    description=f"已生成 {token_count} 個 tokens..."
                )

            progress.update(task, description="✓ 生成完成")

        # 顯示完整響應
        console.print(Panel(
            Markdown(full_response),
            title="[bold green]完整響應[/bold green]",
            border_style="green"
        ))

        console.print(f"\n[dim]總共生成 {token_count} 個 tokens[/dim]")

        return full_response

    except Exception as e:
        console.print(f"[red]帶進度的流式輸出失敗: {e}[/red]")
        return None


def streaming_with_callback(model_name='llama3.2'):
    """使用回調函數處理流式數據"""
    try:
        console.print("\n[bold cyan]回調函數處理流式數據[/bold cyan]")

        user_message = "解釋什麼是微服務架構"

        console.print(f"\n[bold]用戶:[/bold] {user_message}\n")

        # 數據收集器
        chunks = []
        char_count = 0

        def on_chunk(chunk_data):
            """處理每個數據塊的回調函數"""
            nonlocal char_count
            content = chunk_data['message']['content']
            chunks.append(content)
            char_count += len(content)

            # 可以在這裡添加其他處理邏輯
            # 例如：保存到文件、發送到其他服務等

        console.print("[bold green]助手:[/bold green] ")

        stream = ollama.chat(
            model=model_name,
            messages=[
                {
                    'role': 'user',
                    'content': user_message
                }
            ],
            stream=True
        )

        full_response = ""
        for chunk in stream:
            on_chunk(chunk)
            content = chunk['message']['content']
            full_response += content
            console.print(content, end='')

        console.print("\n")

        # 顯示統計
        console.print(f"\n[dim]統計信息:[/dim]")
        console.print(f"[dim]  - 數據塊數量: {len(chunks)}[/dim]")
        console.print(f"[dim]  - 總字符數: {char_count}[/dim]")
        console.print(f"[dim]  - 平均塊大小: {char_count/len(chunks):.1f} 字符[/dim]")

        return full_response

    except Exception as e:
        console.print(f"[red]回調處理失敗: {e}[/red]")
        return None


def streaming_with_timeout(model_name='llama3.2', timeout_seconds=10):
    """帶超時控制的流式輸出"""
    try:
        console.print("\n[bold cyan]帶超時控制的流式輸出[/bold cyan]")
        console.print(f"[dim]超時設置: {timeout_seconds} 秒[/dim]")

        user_message = "介紹雲計算的基本概念"

        console.print(f"\n[bold]用戶:[/bold] {user_message}")
        console.print("[bold green]助手:[/bold green] ", end='')

        stream = ollama.chat(
            model=model_name,
            messages=[
                {
                    'role': 'user',
                    'content': user_message
                }
            ],
            stream=True
        )

        full_response = ""
        start_time = time.time()

        for chunk in stream:
            # 檢查超時
            if time.time() - start_time > timeout_seconds:
                console.print("\n[yellow]⚠ 超時，停止接收[/yellow]")
                break

            content = chunk['message']['content']
            full_response += content
            console.print(content, end='')

        console.print("\n")

        elapsed = time.time() - start_time
        console.print(f"\n[dim]耗時: {elapsed:.2f} 秒[/dim]")

        return full_response

    except Exception as e:
        console.print(f"\n[red]超時控制失敗: {e}[/red]")
        return None


def compare_streaming_vs_normal(model_name='llama3.2'):
    """比較流式與非流式輸出"""
    try:
        console.print("\n[bold cyan]流式 vs 非流式對比[/bold cyan]")

        user_message = "用一段話介紹容器化技術"

        # 非流式輸出
        console.print("\n[bold yellow]1. 非流式輸出（等待完整響應）[/bold yellow]")
        console.print(f"[bold]用戶:[/bold] {user_message}")
        console.print("[dim]等待中...[/dim]")

        start_time = time.time()

        response = ollama.chat(
            model=model_name,
            messages=[
                {
                    'role': 'user',
                    'content': user_message
                }
            ],
            stream=False
        )

        normal_time = time.time() - start_time
        normal_content = response['message']['content']

        console.print(f"\n[bold green]助手:[/bold green]\n{normal_content}")
        console.print(f"\n[dim]總耗時: {normal_time:.2f} 秒（等待後一次性顯示）[/dim]")

        # 流式輸出
        console.print("\n[bold yellow]2. 流式輸出（實時顯示）[/bold yellow]")
        console.print(f"[bold]用戶:[/bold] {user_message}")
        console.print("[bold green]助手:[/bold green] ", end='')

        start_time = time.time()
        first_chunk_time = None

        stream = ollama.chat(
            model=model_name,
            messages=[
                {
                    'role': 'user',
                    'content': user_message
                }
            ],
            stream=True
        )

        stream_content = ""
        for i, chunk in enumerate(stream):
            if i == 0:
                first_chunk_time = time.time() - start_time

            content = chunk['message']['content']
            stream_content += content
            console.print(content, end='')

        stream_time = time.time() - start_time

        console.print("\n")
        console.print(f"\n[dim]首個 token 時間: {first_chunk_time:.2f} 秒[/dim]")
        console.print(f"[dim]總耗時: {stream_time:.2f} 秒（逐步顯示）[/dim]")

        # 對比
        console.print("\n[bold]對比分析:[/bold]")
        console.print(f"  • 非流式: 用戶等待 {normal_time:.2f}s 後看到完整響應")
        console.print(f"  • 流式: 用戶在 {first_chunk_time:.2f}s 後開始看到內容")
        console.print(f"  • 改善: 首次反饋時間減少 {((normal_time-first_chunk_time)/normal_time*100):.1f}%")

    except Exception as e:
        console.print(f"[red]對比失敗: {e}[/red]")
        return None


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Ollama 流式輸出示例[/bold cyan]",
        border_style="cyan"
    ))

    model_name = 'llama3.2'

    console.print(f"\n[dim]使用模型: {model_name}[/dim]")

    # 1. 基礎流式輸出
    console.print("\n[bold]示例 1: 基礎流式輸出[/bold]")
    basic_streaming(model_name)

    # 2. 打字機效果
    console.print("\n[bold]示例 2: 打字機效果[/bold]")
    streaming_with_typewriter_effect(model_name)

    # 3. Live 面板
    console.print("\n[bold]示例 3: Live 面板顯示[/bold]")
    streaming_with_live_panel(model_name)

    # 4. 流式多輪對話
    console.print("\n[bold]示例 4: 流式多輪對話[/bold]")
    streaming_multi_turn(model_name)

    # 5. 帶進度指示
    console.print("\n[bold]示例 5: 帶進度指示[/bold]")
    streaming_with_progress(model_name)

    # 6. 回調函數
    console.print("\n[bold]示例 6: 回調函數處理[/bold]")
    streaming_with_callback(model_name)

    # 7. 超時控制
    console.print("\n[bold]示例 7: 超時控制[/bold]")
    streaming_with_timeout(model_name, timeout_seconds=10)

    # 8. 流式 vs 非流式對比
    console.print("\n[bold]示例 8: 流式 vs 非流式對比[/bold]")
    compare_streaming_vs_normal(model_name)

    # 完成
    console.print("\n" + "="*60)
    console.print("[bold green]✓ 流式輸出示例完成！[/bold green]")
    console.print("\n[cyan]關鍵要點:[/cyan]")
    console.print("  1. 流式輸出提供更好的用戶體驗")
    console.print("  2. 首個 token 延遲顯著降低")
    console.print("  3. 適合長文本生成場景")
    console.print("  4. 可以實現實時進度反饋")


if __name__ == "__main__":
    main()

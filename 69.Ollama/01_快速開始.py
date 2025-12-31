"""
Ollama 快速開始示例

本示例展示：
1. Ollama 安裝驗證
2. 基本配置檢查
3. 簡單對話交互
4. 基礎參數設置
"""

import ollama
import subprocess
import sys
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()


def check_ollama_installed():
    """檢查 Ollama 是否已安裝"""
    try:
        result = subprocess.run(
            ['ollama', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            version = result.stdout.strip()
            console.print(f"[green]✓ Ollama 已安裝: {version}[/green]")
            return True
        else:
            console.print("[red]✗ Ollama 未正確安裝[/red]")
            return False

    except FileNotFoundError:
        console.print("[red]✗ Ollama 未安裝[/red]")
        console.print("\n請訪問 https://ollama.com 下載並安裝 Ollama")
        return False
    except Exception as e:
        console.print(f"[red]✗ 檢查 Ollama 時出錯: {e}[/red]")
        return False


def check_ollama_service():
    """檢查 Ollama 服務是否運行"""
    try:
        # 嘗試列出模型來檢查服務是否可用
        models = ollama.list()
        console.print("[green]✓ Ollama 服務正在運行[/green]")
        return True

    except Exception as e:
        console.print(f"[red]✗ Ollama 服務未運行: {e}[/red]")
        console.print("\n請運行: ollama serve")
        return False


def list_available_models():
    """列出已下載的模型"""
    try:
        response = ollama.list()
        models = response.get('models', [])

        if not models:
            console.print("[yellow]! 尚未下載任何模型[/yellow]")
            console.print("\n請先下載模型，例如: ollama pull llama3.2")
            return []

        console.print("\n[cyan]已下載的模型:[/cyan]")
        for model in models:
            name = model.get('name', 'Unknown')
            size = model.get('size', 0)
            size_gb = size / (1024**3)
            console.print(f"  • {name} ({size_gb:.2f} GB)")

        return models

    except Exception as e:
        console.print(f"[red]獲取模型列表失敗: {e}[/red]")
        return []


def simple_chat(model_name='llama3.2'):
    """簡單的對話示例"""
    try:
        console.print(f"\n[cyan]使用模型: {model_name}[/cyan]")
        console.print("[yellow]正在生成響應...[/yellow]\n")

        # 發送簡單的問候
        response = ollama.chat(
            model=model_name,
            messages=[
                {
                    'role': 'user',
                    'content': '你好！請用一句話介紹一下你自己。'
                }
            ]
        )

        # 提取響應內容
        message = response['message']['content']

        # 顯示響應
        console.print(Panel(
            Markdown(message),
            title="[bold green]AI 響應[/bold green]",
            border_style="green"
        ))

        return response

    except Exception as e:
        console.print(f"[red]對話失敗: {e}[/red]")
        return None


def chat_with_parameters(model_name='llama3.2'):
    """帶參數的對話示例"""
    try:
        console.print(f"\n[cyan]使用模型: {model_name} (自定義參數)[/cyan]")
        console.print("[yellow]正在生成響應...[/yellow]\n")

        # 使用自定義參數
        response = ollama.chat(
            model=model_name,
            messages=[
                {
                    'role': 'user',
                    'content': '用三個要點說明人工智能的優勢'
                }
            ],
            options={
                'temperature': 0.7,      # 控制創造性（0.0-1.0）
                'top_p': 0.9,            # 核採樣參數
                'top_k': 40,             # 保留的最高概率詞彙數量
                'num_predict': 200,      # 最大生成 token 數
            }
        )

        message = response['message']['content']

        # 顯示參數信息
        console.print("[dim]參數設置:[/dim]")
        console.print("[dim]  - Temperature: 0.7[/dim]")
        console.print("[dim]  - Top P: 0.9[/dim]")
        console.print("[dim]  - Top K: 40[/dim]")
        console.print("[dim]  - Max Tokens: 200[/dim]\n")

        # 顯示響應
        console.print(Panel(
            Markdown(message),
            title="[bold green]AI 響應[/bold green]",
            border_style="green"
        ))

        # 顯示統計信息
        total_duration = response.get('total_duration', 0) / 1e9  # 轉換為秒
        load_duration = response.get('load_duration', 0) / 1e9
        prompt_eval_count = response.get('prompt_eval_count', 0)
        eval_count = response.get('eval_count', 0)

        console.print(f"\n[dim]統計信息:[/dim]")
        console.print(f"[dim]  - 總時長: {total_duration:.2f}s[/dim]")
        console.print(f"[dim]  - 加載時長: {load_duration:.2f}s[/dim]")
        console.print(f"[dim]  - 提示詞 tokens: {prompt_eval_count}[/dim]")
        console.print(f"[dim]  - 生成 tokens: {eval_count}[/dim]")

        return response

    except Exception as e:
        console.print(f"[red]對話失敗: {e}[/red]")
        return None


def multi_turn_conversation(model_name='llama3.2'):
    """多輪對話示例"""
    try:
        console.print(f"\n[cyan]多輪對話示例 - 模型: {model_name}[/cyan]\n")

        # 對話歷史
        messages = []

        # 第一輪對話
        messages.append({
            'role': 'user',
            'content': '我想學習 Python 編程'
        })

        console.print("[bold]用戶:[/bold] 我想學習 Python 編程\n")

        response1 = ollama.chat(model=model_name, messages=messages)
        assistant_msg1 = response1['message']['content']
        messages.append(response1['message'])

        console.print(Panel(
            Markdown(assistant_msg1),
            title="[bold green]助手 (第1輪)[/bold green]",
            border_style="green"
        ))

        # 第二輪對話
        messages.append({
            'role': 'user',
            'content': '給我推薦一個適合初學者的項目'
        })

        console.print("\n[bold]用戶:[/bold] 給我推薦一個適合初學者的項目\n")

        response2 = ollama.chat(model=model_name, messages=messages)
        assistant_msg2 = response2['message']['content']

        console.print(Panel(
            Markdown(assistant_msg2),
            title="[bold green]助手 (第2輪)[/bold green]",
            border_style="green"
        ))

        return messages

    except Exception as e:
        console.print(f"[red]多輪對話失敗: {e}[/red]")
        return None


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Ollama 快速開始示例[/bold cyan]",
        border_style="cyan"
    ))

    # 1. 檢查 Ollama 安裝
    console.print("\n[bold]步驟 1: 檢查 Ollama 安裝[/bold]")
    if not check_ollama_installed():
        console.print("\n[red]請先安裝 Ollama 後再運行此示例[/red]")
        return

    # 2. 檢查 Ollama 服務
    console.print("\n[bold]步驟 2: 檢查 Ollama 服務[/bold]")
    if not check_ollama_service():
        console.print("\n[red]請先啟動 Ollama 服務: ollama serve[/red]")
        return

    # 3. 列出可用模型
    console.print("\n[bold]步驟 3: 列出可用模型[/bold]")
    models = list_available_models()

    if not models:
        console.print("\n[yellow]建議下載一個模型開始使用:[/yellow]")
        console.print("  ollama pull llama3.2        # 輕量級模型 (2GB)")
        console.print("  ollama pull mistral         # 高性能模型 (4GB)")
        console.print("  ollama pull llama3.2:1b     # 最小模型 (1GB)")
        return

    # 使用第一個可用模型
    model_name = models[0].get('name', 'llama3.2').split(':')[0]

    # 4. 簡單對話
    console.print("\n[bold]步驟 4: 簡單對話[/bold]")
    simple_chat(model_name)

    # 5. 帶參數的對話
    console.print("\n[bold]步驟 5: 帶參數的對話[/bold]")
    chat_with_parameters(model_name)

    # 6. 多輪對話
    console.print("\n[bold]步驟 6: 多輪對話[/bold]")
    multi_turn_conversation(model_name)

    # 完成
    console.print("\n" + "="*60)
    console.print("[bold green]✓ 快速開始示例完成！[/bold green]")
    console.print("\n[cyan]下一步:[/cyan]")
    console.print("  1. 查看 02_模型管理.py 學習如何管理模型")
    console.print("  2. 查看 04_流式輸出.py 學習流式響應")
    console.print("  3. 查看 07_LangChain整合.py 學習 LangChain 整合")


if __name__ == "__main__":
    main()

"""
Ollama 對話生成示例

本示例展示：
1. 基礎對話生成
2. 多輪對話管理
3. 系統提示詞設置
4. 角色扮演
5. 溫度和創造性控制
"""

import ollama
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
import json

console = Console()


def basic_chat(model_name='llama3.2'):
    """基礎對話示例"""
    try:
        console.print("\n[bold cyan]基礎對話示例[/bold cyan]")

        user_message = "請用簡單的語言解釋什麼是機器學習"

        console.print(f"\n[bold]用戶:[/bold] {user_message}")

        response = ollama.chat(
            model=model_name,
            messages=[
                {
                    'role': 'user',
                    'content': user_message
                }
            ]
        )

        assistant_message = response['message']['content']

        console.print(Panel(
            Markdown(assistant_message),
            title="[bold green]助手[/bold green]",
            border_style="green"
        ))

        return response

    except Exception as e:
        console.print(f"[red]對話失敗: {e}[/red]")
        return None


def chat_with_system_prompt(model_name='llama3.2'):
    """帶系統提示詞的對話"""
    try:
        console.print("\n[bold cyan]系統提示詞示例[/bold cyan]")

        # 設置系統角色
        system_prompt = """你是一位資深的 Python 編程導師。
你的職責是：
1. 用簡單易懂的語言解釋概念
2. 提供實用的代碼示例
3. 鼓勵學習者主動思考
4. 回答要簡潔但完整"""

        console.print("\n[bold]系統提示:[/bold]")
        console.print(Panel(system_prompt, border_style="blue"))

        user_message = "什麼是列表推導式？請舉個例子"

        console.print(f"\n[bold]用戶:[/bold] {user_message}")

        response = ollama.chat(
            model=model_name,
            messages=[
                {
                    'role': 'system',
                    'content': system_prompt
                },
                {
                    'role': 'user',
                    'content': user_message
                }
            ]
        )

        assistant_message = response['message']['content']

        console.print(Panel(
            Markdown(assistant_message),
            title="[bold green]Python 導師[/bold green]",
            border_style="green"
        ))

        return response

    except Exception as e:
        console.print(f"[red]對話失敗: {e}[/red]")
        return None


def multi_turn_conversation(model_name='llama3.2'):
    """多輪對話示例"""
    try:
        console.print("\n[bold cyan]多輪對話示例[/bold cyan]")

        # 初始化對話歷史
        conversation = [
            {
                'role': 'system',
                'content': '你是一個友好的 AI 助手，喜歡用比喻和例子來解釋概念。'
            }
        ]

        # 定義對話序列
        user_inputs = [
            "什麼是 API？",
            "可以給我舉個現實生活的例子嗎？",
            "那 REST API 又是什麼？"
        ]

        for i, user_input in enumerate(user_inputs, 1):
            console.print(f"\n[bold yellow]第 {i} 輪對話[/bold yellow]")

            # 添加用戶消息
            conversation.append({
                'role': 'user',
                'content': user_input
            })

            console.print(f"[bold]用戶:[/bold] {user_input}")

            # 獲取響應
            response = ollama.chat(
                model=model_name,
                messages=conversation
            )

            assistant_message = response['message']['content']

            # 添加助手消息到歷史
            conversation.append(response['message'])

            console.print(Panel(
                Markdown(assistant_message),
                title=f"[bold green]助手 (第 {i} 輪)[/bold green]",
                border_style="green"
            ))

        console.print(f"\n[dim]對話歷史共 {len(conversation)} 條消息[/dim]")

        return conversation

    except Exception as e:
        console.print(f"[red]多輪對話失敗: {e}[/red]")
        return None


def role_playing_chat(model_name='llama3.2'):
    """角色扮演對話"""
    try:
        console.print("\n[bold cyan]角色扮演示例[/bold cyan]")

        # 設置角色
        roles = [
            {
                'name': '莎士比亞',
                'system': '你是威廉·莎士比亞，16世紀的英國劇作家。請用詩意和戲劇化的語言回答問題，偶爾引用你的作品。',
                'question': '你對現代科技有什麼看法？'
            },
            {
                'name': '科學家',
                'system': '你是一位嚴謹的科學家，總是基於證據和邏輯思考。回答要準確、客觀，並引用科學原理。',
                'question': '愛情是什麼？'
            },
            {
                'name': '廚師',
                'system': '你是一位充滿熱情的主廚，喜歡用烹飪和食物來比喻生活中的事物。',
                'question': '如何處理壓力？'
            }
        ]

        for role in roles:
            console.print(f"\n[bold magenta]角色: {role['name']}[/bold magenta]")
            console.print(f"[dim]系統設定: {role['system'][:50]}...[/dim]")

            response = ollama.chat(
                model=model_name,
                messages=[
                    {
                        'role': 'system',
                        'content': role['system']
                    },
                    {
                        'role': 'user',
                        'content': role['question']
                    }
                ]
            )

            console.print(f"\n[bold]問題:[/bold] {role['question']}")

            console.print(Panel(
                Markdown(response['message']['content']),
                title=f"[bold green]{role['name']} 的回答[/bold green]",
                border_style="green"
            ))

    except Exception as e:
        console.print(f"[red]角色扮演失敗: {e}[/red]")
        return None


def temperature_comparison(model_name='llama3.2'):
    """比較不同溫度參數的效果"""
    try:
        console.print("\n[bold cyan]溫度參數比較[/bold cyan]")
        console.print("[dim]溫度控制模型的創造性：0.0 = 確定性，1.0 = 創造性[/dim]")

        question = "用一句話描述春天"

        temperatures = [0.0, 0.5, 1.0]

        for temp in temperatures:
            console.print(f"\n[bold yellow]溫度: {temp}[/bold yellow]")

            response = ollama.chat(
                model=model_name,
                messages=[
                    {
                        'role': 'user',
                        'content': question
                    }
                ],
                options={
                    'temperature': temp,
                    'num_predict': 50  # 限制長度以便比較
                }
            )

            console.print(f"[bold]問題:[/bold] {question}")
            console.print(f"[green]回答:[/green] {response['message']['content']}")

        console.print("\n[dim]注意: 較高的溫度產生更多樣化但可能更不可預測的輸出[/dim]")

    except Exception as e:
        console.print(f"[red]溫度比較失敗: {e}[/red]")
        return None


def structured_output_chat(model_name='llama3.2'):
    """結構化輸出示例"""
    try:
        console.print("\n[bold cyan]結構化輸出示例[/bold cyan]")

        system_prompt = """你是一個數據提取助手。
請從用戶的描述中提取信息，並以 JSON 格式返回。
只返回 JSON，不要其他解釋。"""

        user_message = """請從以下文本提取信息：
張三，35歲，軟件工程師，居住在台北市，愛好是攝影和登山。"""

        console.print(f"\n[bold]用戶:[/bold] {user_message}")

        response = ollama.chat(
            model=model_name,
            messages=[
                {
                    'role': 'system',
                    'content': system_prompt
                },
                {
                    'role': 'user',
                    'content': user_message
                }
            ],
            options={
                'temperature': 0.1  # 低溫度以獲得更一致的輸出
            },
            format='json'  # 請求 JSON 格式
        )

        output = response['message']['content']

        console.print("\n[bold green]結構化輸出:[/bold green]")
        try:
            # 嘗試解析和美化 JSON
            parsed = json.loads(output)
            console.print(Panel(
                json.dumps(parsed, indent=2, ensure_ascii=False),
                border_style="green"
            ))
        except:
            # 如果不是有效 JSON，直接顯示
            console.print(Panel(output, border_style="yellow"))

        return response

    except Exception as e:
        console.print(f"[red]結構化輸出失敗: {e}[/red]")
        return None


def interactive_chat(model_name='llama3.2'):
    """交互式對話示例"""
    try:
        console.print("\n[bold cyan]交互式對話[/bold cyan]")
        console.print("[dim]輸入 'quit' 或 'exit' 結束對話[/dim]\n")

        # 初始化對話
        conversation = [
            {
                'role': 'system',
                'content': '你是一個友好、樂於助人的 AI 助手。請用簡潔但完整的方式回答問題。'
            }
        ]

        turn = 0

        while turn < 3:  # 限制輪數以便示例
            turn += 1

            # 獲取用戶輸入
            user_input = Prompt.ask(f"\n[bold cyan]你[/bold cyan] (第{turn}輪)")

            if user_input.lower() in ['quit', 'exit', '退出']:
                console.print("[yellow]結束對話[/yellow]")
                break

            # 添加到對話歷史
            conversation.append({
                'role': 'user',
                'content': user_input
            })

            # 獲取響應
            console.print("[dim]思考中...[/dim]")
            response = ollama.chat(
                model=model_name,
                messages=conversation
            )

            assistant_message = response['message']['content']
            conversation.append(response['message'])

            # 顯示響應
            console.print(Panel(
                Markdown(assistant_message),
                title=f"[bold green]助手 (第{turn}輪)[/bold green]",
                border_style="green"
            ))

        console.print(f"\n[dim]對話結束，共 {turn} 輪[/dim]")

        return conversation

    except KeyboardInterrupt:
        console.print("\n[yellow]對話被中斷[/yellow]")
        return None
    except Exception as e:
        console.print(f"[red]交互式對話失敗: {e}[/red]")
        return None


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Ollama 對話生成示例[/bold cyan]",
        border_style="cyan"
    ))

    # 使用的模型
    model_name = 'llama3.2'

    console.print(f"\n[dim]使用模型: {model_name}[/dim]")
    console.print("[dim]如果模型未下載，請先運行: ollama pull llama3.2[/dim]")

    # 1. 基礎對話
    console.print("\n[bold]示例 1: 基礎對話[/bold]")
    basic_chat(model_name)

    # 2. 系統提示詞
    console.print("\n[bold]示例 2: 系統提示詞[/bold]")
    chat_with_system_prompt(model_name)

    # 3. 多輪對話
    console.print("\n[bold]示例 3: 多輪對話[/bold]")
    multi_turn_conversation(model_name)

    # 4. 角色扮演
    console.print("\n[bold]示例 4: 角色扮演[/bold]")
    role_playing_chat(model_name)

    # 5. 溫度比較
    console.print("\n[bold]示例 5: 溫度參數比較[/bold]")
    temperature_comparison(model_name)

    # 6. 結構化輸出
    console.print("\n[bold]示例 6: 結構化輸出[/bold]")
    structured_output_chat(model_name)

    # 7. 交互式對話
    console.print("\n[bold]示例 7: 交互式對話 (限制3輪)[/bold]")
    interactive_chat(model_name)

    # 完成
    console.print("\n" + "="*60)
    console.print("[bold green]✓ 對話生成示例完成！[/bold green]")
    console.print("\n[cyan]關鍵要點:[/cyan]")
    console.print("  1. 使用系統提示詞定義角色和行為")
    console.print("  2. 維護對話歷史實現上下文理解")
    console.print("  3. 調整溫度控制創造性")
    console.print("  4. 使用 format='json' 獲取結構化輸出")


if __name__ == "__main__":
    main()

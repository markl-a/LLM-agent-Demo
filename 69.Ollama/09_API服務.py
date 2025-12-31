"""
Ollama API 服務示例

本示例展示：
1. REST API 基礎使用
2. OpenAI 兼容接口
3. HTTP 請求處理
4. API 服務配置
5. 錯誤處理和重試
"""

import requests
import json
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.markdown import Markdown
from openai import OpenAI

console = Console()


def check_ollama_server(base_url='http://localhost:11434'):
    """檢查 Ollama 服務器狀態"""
    try:
        console.print("\n[bold cyan]檢查 Ollama 服務器[/bold cyan]")
        console.print(f"[dim]服務器地址: {base_url}[/dim]")

        # 檢查服務器是否運行
        response = requests.get(f"{base_url}/api/tags", timeout=5)

        if response.status_code == 200:
            console.print("[green]✓ Ollama 服務器正在運行[/green]")

            data = response.json()
            models = data.get('models', [])

            console.print(f"[dim]可用模型數: {len(models)}[/dim]")

            return True
        else:
            console.print(f"[yellow]服務器響應異常: {response.status_code}[/yellow]")
            return False

    except requests.exceptions.ConnectionError:
        console.print("[red]✗ 無法連接到 Ollama 服務器[/red]")
        console.print("[yellow]請確保 Ollama 服務正在運行[/yellow]")
        return False
    except Exception as e:
        console.print(f"[red]檢查服務器失敗: {e}[/red]")
        return False


def rest_api_generate(prompt, model='llama3.2', base_url='http://localhost:11434'):
    """使用 REST API 生成文本"""
    try:
        console.print("\n[bold cyan]REST API 文本生成[/bold cyan]")

        url = f"{base_url}/api/generate"

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }

        console.print(f"\n[bold]請求 URL:[/bold] {url}")
        console.print(f"[bold]提示詞:[/bold] {prompt}")

        # 發送請求
        console.print("\n[dim]發送請求...[/dim]")
        response = requests.post(url, json=payload, timeout=60)

        if response.status_code == 200:
            data = response.json()
            generated_text = data.get('response', '')

            console.print(Panel(
                Markdown(generated_text),
                title="[bold green]生成的文本[/bold green]",
                border_style="green"
            ))

            # 顯示統計信息
            console.print("\n[dim]統計信息:[/dim]")
            console.print(f"[dim]  總時長: {data.get('total_duration', 0) / 1e9:.2f}s[/dim]")
            console.print(f"[dim]  生成 tokens: {data.get('eval_count', 0)}[/dim]")

            return generated_text
        else:
            console.print(f"[red]請求失敗: {response.status_code}[/red]")
            return None

    except Exception as e:
        console.print(f"[red]REST API 生成失敗: {e}[/red]")
        return None


def rest_api_chat(messages, model='llama3.2', base_url='http://localhost:11434'):
    """使用 REST API 進行對話"""
    try:
        console.print("\n[bold cyan]REST API 對話[/bold cyan]")

        url = f"{base_url}/api/chat"

        payload = {
            "model": model,
            "messages": messages,
            "stream": False
        }

        console.print(f"\n[bold]請求 URL:[/bold] {url}")
        console.print(f"[bold]消息數量:[/bold] {len(messages)}")

        # 顯示最後一條用戶消息
        last_user_msg = next(
            (m['content'] for m in reversed(messages) if m['role'] == 'user'),
            None
        )
        if last_user_msg:
            console.print(f"[bold]用戶:[/bold] {last_user_msg}")

        console.print("\n[dim]發送請求...[/dim]")
        response = requests.post(url, json=payload, timeout=60)

        if response.status_code == 200:
            data = response.json()
            message = data.get('message', {})
            content = message.get('content', '')

            console.print(Panel(
                Markdown(content),
                title="[bold green]助手響應[/bold green]",
                border_style="green"
            ))

            return content
        else:
            console.print(f"[red]請求失敗: {response.status_code}[/red]")
            return None

    except Exception as e:
        console.print(f"[red]REST API 對話失敗: {e}[/red]")
        return None


def rest_api_streaming(prompt, model='llama3.2', base_url='http://localhost:11434'):
    """使用 REST API 流式生成"""
    try:
        console.print("\n[bold cyan]REST API 流式生成[/bold cyan]")

        url = f"{base_url}/api/generate"

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": True
        }

        console.print(f"\n[bold]提示詞:[/bold] {prompt}")
        console.print("\n[bold green]助手:[/bold green] ", end='')

        # 流式請求
        response = requests.post(url, json=payload, stream=True, timeout=60)

        full_response = ""

        for line in response.iter_lines():
            if line:
                chunk = json.loads(line)
                text = chunk.get('response', '')
                full_response += text
                console.print(text, end='')

                # 檢查是否完成
                if chunk.get('done', False):
                    break

        console.print("\n")

        return full_response

    except Exception as e:
        console.print(f"\n[red]流式生成失敗: {e}[/red]")
        return None


def openai_compatible_api(model='llama3.2'):
    """使用 OpenAI 兼容接口"""
    try:
        console.print("\n[bold cyan]OpenAI 兼容接口[/bold cyan]")

        # 配置 OpenAI 客戶端指向 Ollama
        client = OpenAI(
            base_url='http://localhost:11434/v1',
            api_key='ollama'  # Ollama 不需要真實 API key
        )

        console.print("[dim]使用 OpenAI SDK 連接到 Ollama[/dim]")

        # 創建聊天完成
        messages = [
            {"role": "system", "content": "你是一個有幫助的助手。"},
            {"role": "user", "content": "用三個要點說明 Docker 的優勢"}
        ]

        console.print(f"\n[bold]用戶:[/bold] {messages[-1]['content']}")
        console.print("\n[dim]調用 OpenAI 兼容 API...[/dim]")

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7
        )

        # 提取響應
        content = response.choices[0].message.content

        console.print(Panel(
            Markdown(content),
            title="[bold green]助手響應[/bold green]",
            border_style="green"
        ))

        # 顯示使用統計
        console.print("\n[dim]使用統計:[/dim]")
        console.print(f"[dim]  模型: {response.model}[/dim]")
        console.print(f"[dim]  完成原因: {response.choices[0].finish_reason}[/dim]")

        return content

    except Exception as e:
        console.print(f"[red]OpenAI 兼容 API 失敗: {e}[/red]")
        console.print("[yellow]提示: 確保 Ollama 服務正在運行[/yellow]")
        return None


def rest_api_embeddings(text, model='nomic-embed-text', base_url='http://localhost:11434'):
    """使用 REST API 生成嵌入向量"""
    try:
        console.print("\n[bold cyan]REST API 嵌入向量[/bold cyan]")

        url = f"{base_url}/api/embeddings"

        payload = {
            "model": model,
            "prompt": text
        }

        console.print(f"\n[bold]文本:[/bold] {text}")
        console.print(f"[bold]模型:[/bold] {model}")

        response = requests.post(url, json=payload, timeout=30)

        if response.status_code == 200:
            data = response.json()
            embedding = data.get('embedding', [])

            console.print(f"\n[green]✓ 嵌入向量已生成[/green]")
            console.print(f"[dim]維度: {len(embedding)}[/dim]")
            console.print(f"[dim]前 10 個值: {embedding[:10]}[/dim]")

            return embedding
        else:
            console.print(f"[red]請求失敗: {response.status_code}[/red]")
            return None

    except Exception as e:
        console.print(f"[red]生成嵌入失敗: {e}[/red]")
        return None


def api_with_retry(max_retries=3, base_url='http://localhost:11434'):
    """帶重試機制的 API 調用"""
    try:
        console.print("\n[bold cyan]帶重試機制的 API 調用[/bold cyan]")

        url = f"{base_url}/api/generate"
        prompt = "什麼是微服務？"

        console.print(f"[dim]最大重試次數: {max_retries}[/dim]")

        for attempt in range(1, max_retries + 1):
            try:
                console.print(f"\n[yellow]嘗試 {attempt}/{max_retries}[/yellow]")

                payload = {
                    "model": "llama3.2",
                    "prompt": prompt,
                    "stream": False
                }

                response = requests.post(url, json=payload, timeout=30)

                if response.status_code == 200:
                    data = response.json()
                    text = data.get('response', '')

                    console.print(f"[green]✓ 請求成功（第 {attempt} 次嘗試）[/green]")
                    console.print(Panel(
                        text[:200] + "..." if len(text) > 200 else text,
                        title="[bold green]響應預覽[/bold green]",
                        border_style="green"
                    ))

                    return text

                else:
                    console.print(f"[yellow]請求失敗: {response.status_code}[/yellow]")

            except requests.exceptions.Timeout:
                console.print("[yellow]請求超時[/yellow]")

            except Exception as e:
                console.print(f"[yellow]錯誤: {e}[/yellow]")

            # 如果不是最後一次嘗試，等待後重試
            if attempt < max_retries:
                wait_time = 2 ** attempt  # 指數退避
                console.print(f"[dim]等待 {wait_time}s 後重試...[/dim]")
                time.sleep(wait_time)

        console.print("[red]✗ 所有重試均失敗[/red]")
        return None

    except Exception as e:
        console.print(f"[red]重試機制失敗: {e}[/red]")
        return None


def api_endpoints_reference():
    """API 端點參考"""
    try:
        console.print("\n[bold cyan]Ollama API 端點參考[/bold cyan]")

        endpoints = [
            {
                'method': 'POST',
                'path': '/api/generate',
                'desc': '文本生成',
                'params': 'model, prompt, stream, options'
            },
            {
                'method': 'POST',
                'path': '/api/chat',
                'desc': '對話生成',
                'params': 'model, messages, stream, options'
            },
            {
                'method': 'POST',
                'path': '/api/embeddings',
                'desc': '嵌入向量生成',
                'params': 'model, prompt'
            },
            {
                'method': 'POST',
                'path': '/api/pull',
                'desc': '下載模型',
                'params': 'name, stream'
            },
            {
                'method': 'POST',
                'path': '/api/push',
                'desc': '推送模型',
                'params': 'name, stream'
            },
            {
                'method': 'POST',
                'path': '/api/create',
                'desc': '創建模型',
                'params': 'name, modelfile, stream'
            },
            {
                'method': 'GET',
                'path': '/api/tags',
                'desc': '列出模型',
                'params': '-'
            },
            {
                'method': 'POST',
                'path': '/api/show',
                'desc': '顯示模型信息',
                'params': 'name'
            },
            {
                'method': 'DELETE',
                'path': '/api/delete',
                'desc': '刪除模型',
                'params': 'name'
            }
        ]

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("方法", style="cyan", width=8)
        table.add_column("路徑", style="yellow", width=20)
        table.add_column("描述", style="blue", width=15)
        table.add_column("主要參數", style="green", width=30)

        for endpoint in endpoints:
            table.add_row(
                endpoint['method'],
                endpoint['path'],
                endpoint['desc'],
                endpoint['params']
            )

        console.print(table)

        console.print("\n[bold]OpenAI 兼容端點:[/bold]")
        console.print("  • POST /v1/chat/completions")
        console.print("  • POST /v1/completions")
        console.print("  • GET  /v1/models")

    except Exception as e:
        console.print(f"[red]API 參考失敗: {e}[/red]")


def api_usage_examples():
    """API 使用示例代碼"""
    try:
        console.print("\n[bold cyan]API 使用示例代碼[/bold cyan]")

        examples = {
            "cURL - 生成文本": """curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "Why is the sky blue?",
  "stream": false
}'""",
            "Python - 對話": """import requests

response = requests.post(
    'http://localhost:11434/api/chat',
    json={
        'model': 'llama3.2',
        'messages': [
            {'role': 'user', 'content': 'Hello!'}
        ]
    }
)

data = response.json()
print(data['message']['content'])""",
            "JavaScript - 流式": """const response = await fetch('http://localhost:11434/api/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    model: 'llama3.2',
    prompt: 'Tell me a story',
    stream: true
  })
});

const reader = response.body.getReader();
while (true) {
  const {done, value} = await reader.read();
  if (done) break;
  console.log(new TextDecoder().decode(value));
}""",
            "OpenAI SDK": """from openai import OpenAI

client = OpenAI(
    base_url='http://localhost:11434/v1',
    api_key='ollama'
)

response = client.chat.completions.create(
    model='llama3.2',
    messages=[
        {'role': 'user', 'content': 'Hello!'}
    ]
)

print(response.choices[0].message.content)"""
        }

        for title, code in examples.items():
            console.print(f"\n[bold yellow]{title}:[/bold yellow]")

            # 檢測語言
            if 'curl' in title.lower():
                lang = 'bash'
            elif 'javascript' in title.lower():
                lang = 'javascript'
            else:
                lang = 'python'

            console.print(Panel(
                Syntax(code, lang, theme="monokai"),
                border_style="blue"
            ))

    except Exception as e:
        console.print(f"[red]示例代碼失敗: {e}[/red]")


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Ollama API 服務示例[/bold cyan]",
        border_style="cyan"
    ))

    base_url = 'http://localhost:11434'

    # 1. 檢查服務器
    console.print("\n[bold]示例 1: 檢查服務器狀態[/bold]")
    server_ok = check_ollama_server(base_url)

    if not server_ok:
        console.print("\n[yellow]請先啟動 Ollama 服務器才能運行 API 示例[/yellow]")

    # 2. API 端點參考
    console.print("\n[bold]示例 2: API 端點參考[/bold]")
    api_endpoints_reference()

    # 3. API 使用示例
    console.print("\n[bold]示例 3: API 使用示例代碼[/bold]")
    api_usage_examples()

    if server_ok:
        # 4. REST API 生成
        console.print("\n[bold]示例 4: REST API 文本生成[/bold]")
        rest_api_generate("用一句話解釋什麼是 API", base_url=base_url)

        # 5. REST API 對話
        console.print("\n[bold]示例 5: REST API 對話[/bold]")
        rest_api_chat([
            {"role": "user", "content": "什麼是 REST API？"}
        ], base_url=base_url)

        # 6. REST API 流式
        console.print("\n[bold]示例 6: REST API 流式生成[/bold]")
        rest_api_streaming("簡單介紹雲計算", base_url=base_url)

        # 7. OpenAI 兼容
        console.print("\n[bold]示例 7: OpenAI 兼容接口[/bold]")
        openai_compatible_api()

        # 8. 嵌入向量
        console.print("\n[bold]示例 8: REST API 嵌入向量[/bold]")
        rest_api_embeddings("人工智能", base_url=base_url)

        # 9. 重試機制
        console.print("\n[bold]示例 9: 帶重試機制的 API[/bold]")
        api_with_retry(max_retries=3, base_url=base_url)

    # 完成
    console.print("\n" + "="*60)
    console.print("[bold green]✓ API 服務示例完成！[/bold green]")

    console.print("\n[cyan]關鍵要點:[/cyan]")
    console.print("  1. Ollama 提供完整的 REST API")
    console.print("  2. 兼容 OpenAI API 格式")
    console.print("  3. 支持流式和非流式請求")
    console.print("  4. 可以通過 HTTP 從任何語言調用")
    console.print("  5. 默認監聽 localhost:11434")


if __name__ == "__main__":
    main()

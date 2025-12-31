"""
LitServe 流式響應示例

本示例展示：
1. 實現流式輸出（Server-Sent Events）
2. 逐字生成文本（類似 ChatGPT）
3. 客戶端接收流式數據
4. 流式響應的錯誤處理
"""

from litserve import LitAPI, LitServer
from rich.console import Console
from rich.panel import Panel
import time
from typing import Generator

console = Console()


class StreamingAPI(LitAPI):
    """支持流式響應的 API"""

    def setup(self, device):
        """初始化文本生成模型"""
        console.print(f"[cyan]正在設置流式 API (設備: {device})...[/cyan]")

        # 模擬一個文本生成模型
        # 實際應用中可能是 GPT、LLaMA 等模型
        self.model_name = "SimpleGenerator"

        console.print("[green]✓ 模型加載完成[/green]")

    def decode_request(self, request):
        """解析請求"""
        prompt = request.get("prompt", "")
        max_tokens = request.get("max_tokens", 50)

        console.print(f"[yellow]收到流式請求:[/yellow]")
        console.print(f"  提示: {prompt[:50]}...")
        console.print(f"  最大 tokens: {max_tokens}")

        return {
            "prompt": prompt,
            "max_tokens": max_tokens
        }

    def predict(self, x) -> Generator[str, None, None]:
        """
        生成流式輸出

        這個方法使用 yield 來逐步返回結果，
        而不是一次性返回所有結果
        """
        prompt = x["prompt"]
        max_tokens = x["max_tokens"]

        console.print(f"[magenta]開始生成流式響應...[/magenta]")

        # 模擬文本生成過程
        # 實際應用中會調用模型的 generate() 方法
        response_text = f"根據您的提示「{prompt}」，我來為您生成一段文字。這是一個流式響應示例，文字會逐個生成並實時返回給客戶端。"

        words = response_text.split()

        # 逐詞生成
        for i, word in enumerate(words[:max_tokens]):
            # 模擬生成延遲
            time.sleep(0.1)

            # 生成 token
            token = word + " "

            console.print(f"[dim]生成 token {i+1}: {token.strip()}[/dim]")

            # yield 返回 token（而不是 return）
            yield token

        console.print(f"[green]✓ 流式生成完成[/green]")

    def encode_response(self, output_stream: Generator[str, None, None]) -> Generator[dict, None, None]:
        """
        編碼流式響應

        這個方法也使用 yield，將每個 token 包裝為 JSON 格式
        """
        token_count = 0

        for token in output_stream:
            token_count += 1

            # 將每個 token 包裝為 JSON
            yield {
                "token": token,
                "index": token_count,
                "finished": False
            }

        # 發送結束標記
        yield {
            "token": "",
            "index": token_count,
            "finished": True
        }


def print_client_examples():
    """打印客戶端示例"""
    console.print("\n" + "="*60)
    console.print("[bold cyan]客戶端接收流式響應示例:[/bold cyan]")

    console.print("\n[yellow]1. Python (requests):[/yellow]")
    console.print("""
import requests
import json

url = "http://localhost:8000/predict"
data = {"prompt": "介紹一下人工智能", "max_tokens": 30}

# 流式接收
response = requests.post(url, json=data, stream=True)

for line in response.iter_lines():
    if line:
        chunk = json.loads(line.decode('utf-8'))
        print(chunk['token'], end='', flush=True)
        if chunk['finished']:
            print("\\n完成！")
            break
    """)

    console.print("\n[yellow]2. JavaScript (fetch):[/yellow]")
    console.print("""
const response = await fetch('http://localhost:8000/predict', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        prompt: '介紹一下人工智能',
        max_tokens: 30
    })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
    const {done, value} = await reader.read();
    if (done) break;

    const chunk = JSON.parse(decoder.decode(value));
    process.stdout.write(chunk.token);

    if (chunk.finished) {
        console.log('\\n完成！');
        break;
    }
}
    """)

    console.print("\n[yellow]3. curl（查看原始輸出）:[/yellow]")
    console.print("""
curl -X POST http://localhost:8000/predict \\
  -H "Content-Type: application/json" \\
  -d '{"prompt": "介紹一下人工智能", "max_tokens": 20}' \\
  --no-buffer
    """)

    console.print("="*60 + "\n")


def print_use_cases():
    """打印使用場景"""
    console.print("\n" + "="*60)
    console.print("[bold cyan]流式響應適用場景:[/bold cyan]")
    console.print("""
[green]1. 文本生成[/green]
   • ChatGPT 風格的對話
   • 文章、代碼生成
   • 內容創作助手

[green]2. 實時翻譯[/green]
   • 同聲翻譯
   • 字幕生成
   • 文檔翻譯

[green]3. 語音識別[/green]
   • 實時語音轉文字
   • 會議記錄
   • 語音助手

[green]4. 數據處理[/green]
   • 大文件處理
   • 批量轉換
   • 實時分析

[yellow]優勢:[/yellow]
  ✓ 更好的用戶體驗（即時反饋）
  ✓ 降低首字節時間 (TTFB)
  ✓ 適合長時間運行的任務
  ✓ 減少內存占用
    """)
    console.print("="*60 + "\n")


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]LitServe 流式響應示例[/bold cyan]\n"
        "[dim]實時逐字生成文本[/dim]",
        border_style="cyan"
    ))

    # 創建 API 實例
    api = StreamingAPI()

    # 創建服務器
    server = LitServer(
        api,
        accelerator="auto",
        stream=True,  # 啟用流式響應
        timeout=60    # 流式請求可能需要更長時間
    )

    console.print("[green]✓ 流式服務器配置完成[/green]")

    # 打印使用場景
    print_use_cases()

    # 打印客戶端示例
    print_client_examples()

    # 啟動服務器
    console.print("[bold green]正在啟動流式響應服務...[/bold green]")
    console.print("[dim]按 Ctrl+C 停止服務器[/dim]\n")

    try:
        server.run(port=8000)
    except KeyboardInterrupt:
        console.print("\n[yellow]服務器已停止[/yellow]")


if __name__ == "__main__":
    main()

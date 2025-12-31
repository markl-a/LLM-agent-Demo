"""
LitServe 快速開始示例

本示例展示：
1. 創建最簡單的 LitAPI
2. 啟動 LitServe 服務器
3. 處理基本的預測請求
4. 測試 API 端點
"""

from litserve import LitAPI, LitServer
from rich.console import Console
from rich.panel import Panel
import time

console = Console()


class SimpleAPI(LitAPI):
    """最簡單的 LitAPI 示例"""

    def setup(self, device):
        """
        初始化階段（服務啟動時調用一次）

        Args:
            device: 計算設備（cpu 或 cuda）
        """
        console.print(f"[cyan]正在設置 API (設備: {device})...[/cyan]")

        # 這裡只使用一個簡單的函數作為"模型"
        self.model = lambda x: x.upper()

        console.print("[green]✓ API 設置完成[/green]")

    def decode_request(self, request):
        """
        解析 HTTP 請求

        Args:
            request: 原始請求數據（字典）

        Returns:
            處理後的輸入數據
        """
        # 從請求中提取文本
        text = request.get("text", "")
        console.print(f"[yellow]收到請求: {text}[/yellow]")
        return text

    def predict(self, x):
        """
        執行推理

        Args:
            x: 經過 decode_request 處理的輸入

        Returns:
            模型輸出
        """
        # 執行預測（這裡只是轉大寫）
        result = self.model(x)
        console.print(f"[magenta]預測結果: {result}[/magenta]")
        return result

    def encode_response(self, output):
        """
        格式化響應

        Args:
            output: predict 方法的輸出

        Returns:
            要返回給客戶端的字典
        """
        response = {
            "result": output,
            "timestamp": time.time()
        }
        console.print(f"[green]返回響應: {response}[/green]")
        return response


def print_usage():
    """打印使用說明"""
    console.print("\n" + "="*60)
    console.print("[bold cyan]如何測試 API:[/bold cyan]")
    console.print("\n[yellow]1. 使用 curl:[/yellow]")
    console.print("""
curl -X POST http://localhost:8000/predict \\
  -H "Content-Type: application/json" \\
  -d '{"text": "hello world"}'
    """)

    console.print("[yellow]2. 使用 Python requests:[/yellow]")
    console.print("""
import requests

response = requests.post(
    "http://localhost:8000/predict",
    json={"text": "hello world"}
)
print(response.json())
    """)

    console.print("[yellow]3. 訪問 API 文檔:[/yellow]")
    console.print("  http://localhost:8000/docs")
    console.print("="*60 + "\n")


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]LitServe 快速開始示例[/bold cyan]\n"
        "[dim]最簡單的模型服務[/dim]",
        border_style="cyan"
    ))

    # 創建 API 實例
    console.print("\n[cyan]創建 SimpleAPI 實例...[/cyan]")
    api = SimpleAPI()

    # 創建服務器
    console.print("[cyan]創建 LitServer...[/cyan]")
    server = LitServer(
        api,
        accelerator="auto",  # 自動選擇設備（CPU/GPU）
        max_batch_size=1,    # 每次處理一個請求
        timeout=30           # 請求超時時間（秒）
    )

    console.print("[green]✓ 服務器創建成功[/green]")

    # 打印使用說明
    print_usage()

    # 啟動服務器
    console.print("[bold green]正在啟動服務器...[/bold green]")
    console.print("[dim]按 Ctrl+C 停止服務器[/dim]\n")

    try:
        server.run(port=8000)
    except KeyboardInterrupt:
        console.print("\n[yellow]服務器已停止[/yellow]")


if __name__ == "__main__":
    main()

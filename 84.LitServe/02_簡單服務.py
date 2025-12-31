"""
LitServe 簡單服務示例

本示例展示：
1. 創建完整的 REST API 服務
2. 使用真實的機器學習模型（情感分析）
3. 輸入驗證和錯誤處理
4. 健康檢查端點
"""

from litserve import LitAPI, LitServer
from rich.console import Console
from rich.panel import Panel
from pydantic import BaseModel, Field
from typing import Optional
import time

console = Console()


class PredictionRequest(BaseModel):
    """請求數據模型"""
    text: str = Field(..., min_length=1, max_length=1000, description="要分析的文本")
    return_score: Optional[bool] = Field(False, description="是否返回置信度分數")


class SentimentAPI(LitAPI):
    """情感分析 API"""

    def setup(self, device):
        """初始化情感分析模型"""
        console.print(f"[cyan]正在加載情感分析模型 (設備: {device})...[/cyan]")

        # 模擬模型加載（實際應用中會加載真實模型）
        # 例如: self.model = pipeline("sentiment-analysis", device=device)

        # 這裡使用簡單的規則作為演示
        self.positive_words = {"好", "棒", "優秀", "喜歡", "愛", "great", "good", "excellent", "love"}
        self.negative_words = {"壞", "差", "糟糕", "討厭", "恨", "bad", "poor", "terrible", "hate"}

        console.print("[green]✓ 模型加載完成[/green]")

    def decode_request(self, request):
        """解析並驗證請求"""
        try:
            # 驗證請求數據
            validated_request = PredictionRequest(**request)

            console.print(f"[yellow]收到請求:[/yellow]")
            console.print(f"  文本: {validated_request.text[:50]}...")
            console.print(f"  返回分數: {validated_request.return_score}")

            return {
                "text": validated_request.text,
                "return_score": validated_request.return_score
            }

        except Exception as e:
            console.print(f"[red]請求驗證失敗: {e}[/red]")
            raise ValueError(f"Invalid request: {e}")

    def predict(self, x):
        """執行情感分析"""
        text = x["text"]
        return_score = x["return_score"]

        # 簡單的情感分析邏輯
        text_lower = text.lower()

        positive_count = sum(1 for word in self.positive_words if word in text_lower)
        negative_count = sum(1 for word in self.negative_words if word in text_lower)

        # 判斷情感
        if positive_count > negative_count:
            sentiment = "positive"
            score = min(0.5 + (positive_count - negative_count) * 0.1, 1.0)
        elif negative_count > positive_count:
            sentiment = "negative"
            score = min(0.5 + (negative_count - positive_count) * 0.1, 1.0)
        else:
            sentiment = "neutral"
            score = 0.5

        console.print(f"[magenta]情感: {sentiment}, 分數: {score:.2f}[/magenta]")

        return {
            "sentiment": sentiment,
            "score": score,
            "return_score": return_score
        }

    def encode_response(self, output):
        """格式化響應"""
        response = {
            "sentiment": output["sentiment"],
            "timestamp": time.time()
        }

        # 如果請求要求返回分數
        if output["return_score"]:
            response["confidence"] = output["score"]

        console.print(f"[green]返回響應: {response}[/green]")
        return response


def print_examples():
    """打印測試示例"""
    console.print("\n" + "="*60)
    console.print("[bold cyan]測試示例:[/bold cyan]")

    console.print("\n[yellow]1. 正面情感:[/yellow]")
    console.print("""
curl -X POST http://localhost:8000/predict \\
  -H "Content-Type: application/json" \\
  -d '{"text": "這個產品真的很棒，我很喜歡！", "return_score": true}'
    """)

    console.print("[yellow]2. 負面情感:[/yellow]")
    console.print("""
curl -X POST http://localhost:8000/predict \\
  -H "Content-Type: application/json" \\
  -d '{"text": "這個服務太差了，我很失望。", "return_score": true}'
    """)

    console.print("[yellow]3. 中性情感:[/yellow]")
    console.print("""
curl -X POST http://localhost:8000/predict \\
  -H "Content-Type: application/json" \\
  -d '{"text": "今天天氣不錯。", "return_score": false}'
    """)

    console.print("\n[yellow]4. 健康檢查:[/yellow]")
    console.print("  curl http://localhost:8000/health")

    console.print("\n[yellow]5. API 文檔:[/yellow]")
    console.print("  http://localhost:8000/docs")
    console.print("="*60 + "\n")


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]LitServe 簡單服務示例[/bold cyan]\n"
        "[dim]情感分析 REST API[/dim]",
        border_style="cyan"
    ))

    # 創建 API 實例
    api = SentimentAPI()

    # 創建服務器
    server = LitServer(
        api,
        accelerator="auto",
        max_batch_size=1,
        timeout=30
    )

    # 打印測試示例
    print_examples()

    # 啟動服務器
    console.print("[bold green]正在啟動情感分析服務...[/bold green]")
    console.print("[dim]按 Ctrl+C 停止服務器[/dim]\n")

    try:
        server.run(port=8000)
    except KeyboardInterrupt:
        console.print("\n[yellow]服務器已停止[/yellow]")


if __name__ == "__main__":
    main()

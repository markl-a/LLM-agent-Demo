"""
LitServe 多模型服務示例

本示例展示：
1. 在同一服務器上部署多個模型
2. 路由請求到不同模型
3. 模型版本管理
4. 多模型資源共享
"""

from litserve import LitAPI, LitServer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import torch
import time
from typing import Dict

console = Console()


class MultiModelAPI(LitAPI):
    """支持多個模型的 API"""

    def setup(self, device):
        """加載多個模型"""
        console.print(f"[cyan]正在加載多個模型 (設備: {device})...[/cyan]")

        # 加載多個模型
        self.models = {}

        # 模型 1: 分類模型
        console.print("[yellow]加載分類模型...[/yellow]")
        self.models["classifier"] = self._create_classifier()
        self.models["classifier"].to(device)

        # 模型 2: 回歸模型
        console.print("[yellow]加載回歸模型...[/yellow]")
        self.models["regressor"] = self._create_regressor()
        self.models["regressor"].to(device)

        # 模型 3: 生成模型
        console.print("[yellow]加載生成模型...[/yellow]")
        self.models["generator"] = self._create_generator()
        self.models["generator"].to(device)

        self.device = device

        console.print(f"[green]✓ 成功加載 {len(self.models)} 個模型[/green]")
        self._print_model_info()

    def _create_classifier(self):
        """創建分類模型"""
        return torch.nn.Sequential(
            torch.nn.Linear(100, 50),
            torch.nn.ReLU(),
            torch.nn.Linear(50, 10),
            torch.nn.Softmax(dim=1)
        )

    def _create_regressor(self):
        """創建回歸模型"""
        return torch.nn.Sequential(
            torch.nn.Linear(50, 25),
            torch.nn.ReLU(),
            torch.nn.Linear(25, 1)
        )

    def _create_generator(self):
        """創建生成模型"""
        return torch.nn.Sequential(
            torch.nn.Linear(10, 50),
            torch.nn.ReLU(),
            torch.nn.Linear(50, 100),
            torch.nn.Tanh()
        )

    def _print_model_info(self):
        """打印模型信息"""
        table = Table(title="已加載的模型")
        table.add_column("模型名稱", style="cyan")
        table.add_column("類型", style="yellow")
        table.add_column("輸入維度", style="green")
        table.add_column("輸出維度", style="magenta")

        table.add_row("classifier", "分類", "100", "10")
        table.add_row("regressor", "回歸", "50", "1")
        table.add_row("generator", "生成", "10", "100")

        console.print(table)

    def decode_request(self, request):
        """解析請求並確定使用哪個模型"""
        # 從請求中獲取模型名稱
        model_name = request.get("model", "classifier")

        # 驗證模型是否存在
        if model_name not in self.models:
            available = ", ".join(self.models.keys())
            raise ValueError(
                f"模型 '{model_name}' 不存在。可用模型: {available}"
            )

        # 獲取輸入數據
        input_data = request.get("input", [])

        console.print(f"[yellow]使用模型: {model_name}[/yellow]")
        console.print(f"[dim]輸入長度: {len(input_data)}[/dim]")

        # 轉換為張量
        tensor = torch.tensor(input_data, dtype=torch.float32).to(self.device)

        # 確保是 2D 張量 (batch_size, features)
        if tensor.dim() == 1:
            tensor = tensor.unsqueeze(0)

        return {
            "model_name": model_name,
            "input": tensor
        }

    def predict(self, x):
        """使用指定模型進行推理"""
        model_name = x["model_name"]
        input_tensor = x["input"]

        console.print(f"[magenta]執行推理: {model_name}[/magenta]")

        start_time = time.time()

        # 選擇對應的模型
        model = self.models[model_name]

        # 執行推理
        with torch.no_grad():
            output = model(input_tensor)

        elapsed = time.time() - start_time
        console.print(f"[dim]推理耗時: {elapsed*1000:.2f}ms[/dim]")

        return {
            "model_name": model_name,
            "output": output
        }

    def encode_response(self, output):
        """格式化響應"""
        model_name = output["model_name"]
        result = output["output"].cpu().numpy().tolist()

        return {
            "model": model_name,
            "predictions": result,
            "timestamp": time.time()
        }


def print_model_examples():
    """打印各個模型的測試示例"""
    console.print("\n" + "="*60)
    console.print("[bold cyan]多模型測試示例:[/bold cyan]")

    console.print("\n[yellow]1. 分類模型（100 維輸入 → 10 類）:[/yellow]")
    console.print("""
curl -X POST http://localhost:8000/predict \\
  -H "Content-Type: application/json" \\
  -d '{
    "model": "classifier",
    "input": [0.1, 0.2, ..., 0.1]  # 100 維向量
  }'
    """)

    console.print("\n[yellow]2. 回歸模型（50 維輸入 → 1 維輸出）:[/yellow]")
    console.print("""
curl -X POST http://localhost:8000/predict \\
  -H "Content-Type: application/json" \\
  -d '{
    "model": "regressor",
    "input": [0.5, 0.3, ..., 0.7]  # 50 維向量
  }'
    """)

    console.print("\n[yellow]3. 生成模型（10 維輸入 → 100 維輸出）:[/yellow]")
    console.print("""
curl -X POST http://localhost:8000/predict \\
  -H "Content-Type: application/json" \\
  -d '{
    "model": "generator",
    "input": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
  }'
    """)

    console.print("="*60 + "\n")


def print_multi_model_patterns():
    """打印多模型部署模式"""
    console.print("\n" + "="*60)
    console.print("[bold cyan]多模型部署模式:[/bold cyan]")
    console.print("""
[green]1. 單服務器多模型（本示例）[/green]
   優點:
   • 資源共享（GPU、內存）
   • 統一管理和監控
   • 降低部署複雜度

   缺點:
   • 單點故障風險
   • 資源競爭
   • 擴展受限

[green]2. 多服務器單模型[/green]
   優點:
   • 獨立擴展
   • 故障隔離
   • 性能優化

   缺點:
   • 資源利用率低
   • 管理複雜
   • 成本較高

[green]3. 模型路由（推薦）[/green]
   • 使用 API Gateway 路由到不同服務
   • 每個模型獨立部署
   • 靈活的負載均衡

[yellow]選擇建議:[/yellow]
  • 小規模/開發環境: 單服務器多模型
  • 生產環境: 模型路由 + 多服務器
  • 高流量: 每個模型獨立擴展
    """)
    console.print("="*60 + "\n")


def print_version_management():
    """打印版本管理建議"""
    console.print("\n" + "="*60)
    console.print("[bold cyan]模型版本管理:[/bold cyan]")
    console.print("""
[green]1. 版本命名[/green]
   • model_v1, model_v2
   • model_2024_01, model_2024_02
   • model_prod, model_staging

[green]2. A/B 測試[/green]
   • 同時運行多個版本
   • 按比例分配流量
   • 比較性能和準確度

[green]3. 藍綠部署[/green]
   • 保留舊版本（藍）
   • 部署新版本（綠）
   • 快速回滾

[green]4. 金絲雀發布[/green]
   • 小部分流量測試新版本
   • 逐步增加流量
   • 降低風險

示例代碼:
```python
self.models = {
    "classifier_v1": load_model("v1"),
    "classifier_v2": load_model("v2"),
    "classifier_prod": load_model("prod")
}
```
    """)
    console.print("="*60 + "\n")


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]LitServe 多模型服務示例[/bold cyan]\n"
        "[dim]在同一服務器上運行多個模型[/dim]",
        border_style="cyan"
    ))

    # 創建 API 實例
    api = MultiModelAPI()

    # 創建服務器
    server = LitServer(
        api,
        accelerator="auto",
        max_batch_size=1,
        timeout=30
    )

    # 打印示例
    print_model_examples()

    # 打印部署模式
    print_multi_model_patterns()

    # 打印版本管理
    print_version_management()

    # 啟動服務器
    console.print("[bold green]正在啟動多模型服務...[/bold green]")
    console.print("[dim]按 Ctrl+C 停止服務器[/dim]\n")

    try:
        server.run(port=8000)
    except KeyboardInterrupt:
        console.print("\n[yellow]服務器已停止[/yellow]")


if __name__ == "__main__":
    main()

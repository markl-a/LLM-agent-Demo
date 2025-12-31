"""
LitServe GPU 加速示例

本示例展示：
1. 使用 GPU 加速模型推理
2. 多 GPU 支持和配置
3. 設備管理和內存優化
4. GPU 性能監控
"""

from litserve import LitAPI, LitServer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import torch
import time
import numpy as np

console = Console()


class GPUAcceleratedAPI(LitAPI):
    """GPU 加速的推理 API"""

    def setup(self, device):
        """
        在指定設備上初始化模型

        Args:
            device: PyTorch 設備（'cpu', 'cuda:0', 'cuda:1' 等）
        """
        console.print(f"[cyan]正在設置 GPU 加速 API...[/cyan]")
        console.print(f"[yellow]目標設備: {device}[/yellow]")

        # 檢查 GPU 可用性
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(device)
            gpu_memory = torch.cuda.get_device_properties(device).total_memory / 1e9
            console.print(f"[green]✓ GPU 可用: {gpu_name}[/green]")
            console.print(f"[dim]GPU 內存: {gpu_memory:.2f} GB[/dim]")
        else:
            console.print("[yellow]⚠ GPU 不可用，使用 CPU[/yellow]")

        # 創建一個簡單的神經網絡模型
        self.model = self._create_model()

        # 將模型移到指定設備
        self.model = self.model.to(device)
        self.model.eval()  # 設為評估模式

        # 保存設備引用
        self.device = device

        console.print("[green]✓ 模型已加載到設備[/green]")

        # 預熱（可選，但推薦）
        self._warmup()

    def _create_model(self):
        """創建示例模型"""
        return torch.nn.Sequential(
            torch.nn.Linear(512, 256),
            torch.nn.ReLU(),
            torch.nn.Linear(256, 128),
            torch.nn.ReLU(),
            torch.nn.Linear(128, 10)
        )

    def _warmup(self):
        """預熱 GPU（避免首次推理慢）"""
        console.print("[cyan]正在預熱 GPU...[/cyan]")

        dummy_input = torch.randn(1, 512).to(self.device)

        # 執行幾次預熱推理
        with torch.no_grad():
            for _ in range(5):
                _ = self.model(dummy_input)

        # 清空 CUDA 緩存
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        console.print("[green]✓ GPU 預熱完成[/green]")

    def decode_request(self, request):
        """解析請求並轉換為張量"""
        # 獲取輸入數據
        input_data = np.array(request.get("input", []))

        if input_data.shape[-1] != 512:
            raise ValueError(f"期望輸入維度為 512，實際得到 {input_data.shape[-1]}")

        # 轉換為 PyTorch 張量並移到設備
        tensor = torch.from_numpy(input_data).float().to(self.device)

        console.print(f"[yellow]輸入形狀: {tensor.shape}, 設備: {tensor.device}[/yellow]")

        return tensor

    def predict(self, x):
        """在 GPU 上執行推理"""
        start_time = time.time()

        # 使用 torch.no_grad() 節省內存
        with torch.no_grad():
            output = self.model(x)

        # 同步 GPU（確保計算完成）
        if torch.cuda.is_available():
            torch.cuda.synchronize()

        elapsed = time.time() - start_time

        console.print(f"[magenta]GPU 推理耗時: {elapsed*1000:.2f}ms[/magenta]")

        # 檢查 GPU 內存使用
        if torch.cuda.is_available():
            memory_used = torch.cuda.memory_allocated(self.device) / 1e9
            console.print(f"[dim]GPU 內存使用: {memory_used:.2f} GB[/dim]")

        return output

    def encode_response(self, output):
        """將 GPU 張量轉換為響應"""
        # 將張量移回 CPU 並轉為列表
        result = output.cpu().numpy().tolist()

        return {
            "predictions": result,
            "device": str(self.device),
            "shape": list(output.shape)
        }


def check_gpu_info():
    """檢查並打印 GPU 信息"""
    console.print("\n" + "="*60)
    console.print("[bold cyan]GPU 信息:[/bold cyan]\n")

    if not torch.cuda.is_available():
        console.print("[yellow]未檢測到 CUDA GPU[/yellow]")
        console.print("[dim]服務將在 CPU 上運行[/dim]")
        return

    table = Table(show_header=True)
    table.add_column("GPU ID", style="cyan")
    table.add_column("名稱", style="green")
    table.add_column("顯存", style="yellow")
    table.add_column("計算能力", style="magenta")

    for i in range(torch.cuda.device_count()):
        props = torch.cuda.get_device_properties(i)
        table.add_row(
            str(i),
            torch.cuda.get_device_name(i),
            f"{props.total_memory / 1e9:.2f} GB",
            f"{props.major}.{props.minor}"
        )

    console.print(table)
    console.print("="*60 + "\n")


def print_gpu_tips():
    """打印 GPU 優化建議"""
    console.print("\n" + "="*60)
    console.print("[bold cyan]GPU 優化建議:[/bold cyan]")
    console.print("""
[green]1. 批量處理[/green]
   • 啟用批處理以提高 GPU 利用率
   • max_batch_size=16 或更大

[green]2. 混合精度[/green]
   • 使用 torch.cuda.amp 進行 FP16 推理
   • 可以 2x 提升速度，減少顯存使用

[green]3. 多 GPU[/green]
   • devices="auto" 自動使用所有 GPU
   • devices=[0, 1] 指定使用的 GPU

[green]4. 內存管理[/green]
   • 使用 torch.cuda.empty_cache() 清理緩存
   • 避免在推理時創建不必要的張量

[green]5. 異步操作[/green]
   • GPU 操作是異步的
   • 使用 torch.cuda.synchronize() 確保完成

[yellow]性能提升:[/yellow]
  • CPU → GPU: 10-100x 提升（取決於模型）
  • 單 GPU → 多 GPU: 近線性擴展
  • FP32 → FP16: 1.5-2x 提升
    """)
    console.print("="*60 + "\n")


def print_multi_gpu_config():
    """打印多 GPU 配置"""
    console.print("\n" + "="*60)
    console.print("[bold cyan]多 GPU 配置示例:[/bold cyan]")
    console.print("""
# 使用所有可用 GPU
server = LitServer(
    api,
    accelerator="auto",
    devices="auto"  # 自動檢測並使用所有 GPU
)

# 使用指定 GPU
server = LitServer(
    api,
    accelerator="cuda",
    devices=[0, 1, 2]  # 使用 GPU 0, 1, 2
)

# 使用單個 GPU
server = LitServer(
    api,
    accelerator="cuda",
    devices=[0]  # 只使用 GPU 0
)
    """)
    console.print("="*60 + "\n")


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]LitServe GPU 加速示例[/bold cyan]\n"
        "[dim]使用 GPU 加速模型推理[/dim]",
        border_style="cyan"
    ))

    # 檢查 GPU 信息
    check_gpu_info()

    # 創建 API 實例
    api = GPUAcceleratedAPI()

    # 創建服務器（自動選擇最佳設備）
    console.print("[cyan]創建 GPU 加速服務器...[/cyan]")
    server = LitServer(
        api,
        accelerator="auto",      # 自動選擇（優先 GPU）
        devices="auto",          # 使用所有可用設備
        max_batch_size=8,        # 批處理提升 GPU 利用率
        workers_per_device=1     # 每個 GPU 的 worker 數
    )

    console.print("[green]✓ 服務器配置完成[/green]")

    # 打印優化建議
    print_gpu_tips()

    # 打印多 GPU 配置
    print_multi_gpu_config()

    # 啟動服務器
    console.print("[bold green]正在啟動 GPU 加速服務...[/bold green]")
    console.print("[dim]按 Ctrl+C 停止服務器[/dim]\n")

    try:
        server.run(port=8000)
    except KeyboardInterrupt:
        console.print("\n[yellow]服務器已停止[/yellow]")


if __name__ == "__main__":
    main()

"""
LitServe 批量處理示例

本示例展示：
1. 自動批量處理提升吞吐量
2. 實現 batch() 和 unbatch() 方法
3. 配置批處理參數
4. 性能對比測試
"""

from litserve import LitAPI, LitServer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import numpy as np
import time
from typing import List

console = Console()


class BatchedAPI(LitAPI):
    """支持批量處理的 API"""

    def setup(self, device):
        """初始化模型"""
        console.print(f"[cyan]正在設置批量處理 API (設備: {device})...[/cyan]")

        # 模擬一個需要計算的模型
        # 實際應用中可能是深度學習模型
        self.model_weights = np.random.randn(100, 50)

        console.print("[green]✓ 模型加載完成[/green]")
        console.print(f"[dim]模型權重形狀: {self.model_weights.shape}[/dim]")

    def decode_request(self, request):
        """解析單個請求"""
        # 提取輸入向量
        input_vector = np.array(request.get("vector", []))

        if len(input_vector) != 100:
            raise ValueError(f"期望輸入維度為 100，實際得到 {len(input_vector)}")

        return input_vector

    def batch(self, inputs: List[np.ndarray]) -> np.ndarray:
        """
        將多個請求合併為批次

        Args:
            inputs: 單個輸入的列表

        Returns:
            批量輸入（numpy 數組）
        """
        batch_size = len(inputs)
        console.print(f"[cyan]批量處理: {batch_size} 個請求[/cyan]")

        # 將列表轉換為批量數組
        batched = np.stack(inputs)

        console.print(f"[dim]批次形狀: {batched.shape}[/dim]")
        return batched

    def predict(self, x_batch: np.ndarray):
        """
        批量推理

        Args:
            x_batch: 批量輸入 (batch_size, 100)

        Returns:
            批量輸出 (batch_size, 50)
        """
        start_time = time.time()

        # 矩陣乘法（模擬模型推理）
        # 在實際應用中，批量處理可以更有效地利用 GPU
        output_batch = np.dot(x_batch, self.model_weights)

        # 添加一些處理時間模擬（實際模型可能更慢）
        time.sleep(0.01)

        elapsed = time.time() - start_time
        console.print(f"[magenta]批量推理完成: {elapsed:.3f}秒[/magenta]")

        return output_batch

    def unbatch(self, output_batch: np.ndarray) -> List[np.ndarray]:
        """
        將批量結果拆分為單個輸出

        Args:
            output_batch: 批量輸出

        Returns:
            單個輸出的列表
        """
        # 將批量數組拆分為列表
        outputs = [output_batch[i] for i in range(len(output_batch))]

        console.print(f"[cyan]拆分批次: {len(outputs)} 個結果[/cyan]")
        return outputs

    def encode_response(self, output: np.ndarray):
        """格式化單個響應"""
        return {
            "result": output.tolist(),
            "shape": list(output.shape),
            "mean": float(np.mean(output)),
            "std": float(np.std(output))
        }


def print_performance_tips():
    """打印性能優化建議"""
    console.print("\n" + "="*60)
    console.print("[bold cyan]批量處理性能優化建議:[/bold cyan]")

    table = Table(show_header=True)
    table.add_column("參數", style="cyan")
    table.add_column("說明", style="white")
    table.add_column("推薦值", style="green")

    table.add_row(
        "max_batch_size",
        "最大批次大小",
        "4-32（根據 GPU 內存）"
    )
    table.add_row(
        "batch_timeout",
        "批次等待超時",
        "0.01-0.1 秒"
    )
    table.add_row(
        "workers_per_device",
        "每個設備的 worker 數",
        "1-4"
    )

    console.print(table)
    console.print("\n[yellow]性能提升效果:[/yellow]")
    console.print("  • 小批次 (4-8):   2-4x 吞吐量提升")
    console.print("  • 中批次 (16-32): 5-10x 吞吐量提升")
    console.print("  • 大批次 (64+):   10-20x 吞吐量提升（GPU）")
    console.print("="*60 + "\n")


def print_test_script():
    """打印測試腳本"""
    console.print("\n" + "="*60)
    console.print("[bold cyan]性能測試腳本:[/bold cyan]")
    console.print("""
# test_batch.py
import requests
import time
import concurrent.futures
import numpy as np

def send_request():
    vector = np.random.randn(100).tolist()
    response = requests.post(
        "http://localhost:8000/predict",
        json={"vector": vector}
    )
    return response.json()

# 並發測試
start = time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(send_request) for _ in range(50)]
    results = [f.result() for f in futures]
elapsed = time.time() - start

print(f"處理 50 個請求耗時: {elapsed:.2f}秒")
print(f"平均延遲: {elapsed/50*1000:.2f}ms")
print(f"吞吐量: {50/elapsed:.2f} 請求/秒")
    """)
    console.print("="*60 + "\n")


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]LitServe 批量處理示例[/bold cyan]\n"
        "[dim]自動批處理提升吞吐量[/dim]",
        border_style="cyan"
    ))

    # 創建 API 實例
    api = BatchedAPI()

    # 創建服務器（啟用批處理）
    console.print("\n[cyan]創建支持批處理的服務器...[/cyan]")
    server = LitServer(
        api,
        accelerator="auto",
        max_batch_size=8,      # 最大批次大小
        batch_timeout=0.05,    # 批次等待時間（秒）
        timeout=30
    )

    console.print("[green]✓ 服務器配置:[/green]")
    console.print(f"  最大批次大小: 8")
    console.print(f"  批次超時: 0.05 秒")

    # 打印性能建議
    print_performance_tips()

    # 打印測試腳本
    print_test_script()

    # 啟動服務器
    console.print("[bold green]正在啟動批量處理服務...[/bold green]")
    console.print("[dim]按 Ctrl+C 停止服務器[/dim]\n")

    try:
        server.run(port=8000)
    except KeyboardInterrupt:
        console.print("\n[yellow]服務器已停止[/yellow]")


if __name__ == "__main__":
    main()

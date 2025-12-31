"""
Modal GPU 運算示例

本示例展示：
1. 使用不同類型的 GPU
2. PyTorch GPU 加速
3. 批量 GPU 推理
4. GPU 資源管理
"""

import modal
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

# 創建應用
app = modal.App("gpu-compute")

# 定義 GPU 鏡像（包含 PyTorch）
gpu_image = modal.Image.debian_slim().pip_install(
    "torch>=2.0.0",
    "torchvision",
    "numpy"
)


# 示例 1: 檢測 GPU 可用性
@app.function(
    gpu="T4",  # 使用 T4 GPU（最便宜的選項）
    image=gpu_image
)
def check_gpu():
    """檢測 GPU 是否可用"""
    import torch

    info = {
        "cuda_available": torch.cuda.is_available(),
        "device_count": torch.cuda.device_count(),
    }

    if torch.cuda.is_available():
        info["device_name"] = torch.cuda.get_device_name(0)
        info["memory_total"] = f"{torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB"
        info["cuda_version"] = torch.version.cuda

    print(f"GPU 信息: {info}")
    return info


# 示例 2: 簡單的 GPU 計算
@app.function(
    gpu="T4",
    image=gpu_image
)
def gpu_matrix_multiply(size: int = 1000):
    """在 GPU 上執行矩陣乘法"""
    import torch
    import time

    print(f"創建 {size}x{size} 矩陣...")

    # 在 GPU 上創建隨機矩陣
    device = torch.device("cuda")
    a = torch.randn(size, size, device=device)
    b = torch.randn(size, size, device=device)

    # GPU 計算
    print("在 GPU 上計算...")
    start = time.time()
    c = torch.matmul(a, b)
    torch.cuda.synchronize()  # 等待 GPU 完成
    gpu_time = time.time() - start

    # CPU 計算（對比）
    print("在 CPU 上計算...")
    a_cpu = a.cpu()
    b_cpu = b.cpu()
    start = time.time()
    c_cpu = torch.matmul(a_cpu, b_cpu)
    cpu_time = time.time() - start

    speedup = cpu_time / gpu_time

    result = {
        "matrix_size": size,
        "gpu_time": f"{gpu_time:.4f}s",
        "cpu_time": f"{cpu_time:.4f}s",
        "speedup": f"{speedup:.2f}x"
    }

    print(f"結果: {result}")
    return result


# 示例 3: 使用不同的 GPU 類型
@app.function(
    gpu="A100",  # 高性能 GPU
    image=gpu_image
)
def a100_computation():
    """使用 A100 GPU 進行計算"""
    import torch

    device = torch.device("cuda")
    print(f"使用 GPU: {torch.cuda.get_device_name(0)}")

    # 創建大型張量
    x = torch.randn(10000, 10000, device=device)

    # 執行計算
    result = torch.sum(x * x)

    return {
        "gpu": "A100",
        "result": float(result.cpu())
    }


# 示例 4: 批量 GPU 推理
@app.function(
    gpu="T4",
    image=gpu_image
)
def batch_inference(batch_size: int = 32):
    """批量 GPU 推理示例"""
    import torch
    import torch.nn as nn

    print(f"批量大小: {batch_size}")

    # 創建簡單模型
    device = torch.device("cuda")
    model = nn.Sequential(
        nn.Linear(100, 50),
        nn.ReLU(),
        nn.Linear(50, 10)
    ).to(device)

    model.eval()

    # 創建批量數據
    inputs = torch.randn(batch_size, 100, device=device)

    # 推理
    with torch.no_grad():
        outputs = model(inputs)

    print(f"輸入形狀: {inputs.shape}")
    print(f"輸出形狀: {outputs.shape}")

    return {
        "batch_size": batch_size,
        "input_shape": list(inputs.shape),
        "output_shape": list(outputs.shape)
    }


# 示例 5: 混合精度計算
@app.function(
    gpu="A100",  # A100 支持更好的混合精度
    image=gpu_image
)
def mixed_precision_compute():
    """使用混合精度加速計算"""
    import torch
    import time

    device = torch.device("cuda")

    # 創建數據
    x = torch.randn(5000, 5000, device=device)
    y = torch.randn(5000, 5000, device=device)

    # FP32 計算
    start = time.time()
    z_fp32 = torch.matmul(x, y)
    torch.cuda.synchronize()
    fp32_time = time.time() - start

    # FP16 計算（自動混合精度）
    with torch.cuda.amp.autocast():
        start = time.time()
        z_fp16 = torch.matmul(x, y)
        torch.cuda.synchronize()
        fp16_time = time.time() - start

    speedup = fp32_time / fp16_time

    return {
        "fp32_time": f"{fp32_time:.4f}s",
        "fp16_time": f"{fp16_time:.4f}s",
        "speedup": f"{speedup:.2f}x"
    }


# 示例 6: 多 GPU（如果可用）
@app.function(
    gpu="A100",
    gpu_count=2,  # 使用 2 個 GPU
    image=gpu_image
)
def multi_gpu_compute():
    """使用多個 GPU"""
    import torch

    gpu_count = torch.cuda.device_count()
    print(f"可用 GPU 數量: {gpu_count}")

    gpus_info = []
    for i in range(gpu_count):
        info = {
            "gpu_id": i,
            "name": torch.cuda.get_device_name(i),
            "memory": f"{torch.cuda.get_device_properties(i).total_memory / 1e9:.2f} GB"
        }
        gpus_info.append(info)
        print(f"GPU {i}: {info}")

    return {
        "gpu_count": gpu_count,
        "gpus": gpus_info
    }


@app.local_entrypoint()
def main():
    """本地入口"""
    console.print(Panel.fit(
        "[bold cyan]Modal GPU 運算示例[/bold cyan]\n"
        "[dim]使用雲端 GPU 加速計算[/dim]",
        border_style="cyan"
    ))

    # 1. 檢測 GPU
    console.print("\n[cyan]1. 檢測 GPU 可用性[/cyan]")
    gpu_info = check_gpu.remote()

    table = Table(title="GPU 信息")
    table.add_column("屬性", style="cyan")
    table.add_column("值", style="green")

    for key, value in gpu_info.items():
        table.add_row(key, str(value))

    console.print(table)

    # 2. GPU 矩陣乘法
    console.print("\n[cyan]2. GPU vs CPU 矩陣乘法[/cyan]")
    result = gpu_matrix_multiply.remote(2000)

    table = Table(title="性能對比")
    table.add_column("項目", style="cyan")
    table.add_column("值", style="green")

    for key, value in result.items():
        table.add_row(key, str(value))

    console.print(table)

    # 3. A100 GPU 計算
    console.print("\n[cyan]3. A100 GPU 高性能計算[/cyan]")
    result = a100_computation.remote()
    console.print(f"[green]結果: {result}[/green]")

    # 4. 批量推理
    console.print("\n[cyan]4. 批量 GPU 推理[/cyan]")
    result = batch_inference.remote(64)
    console.print(f"[green]結果: {result}[/green]")

    # 5. 混合精度
    console.print("\n[cyan]5. 混合精度計算（FP16 vs FP32）[/cyan]")
    result = mixed_precision_compute.remote()

    table = Table(title="混合精度性能")
    table.add_column("精度", style="cyan")
    table.add_column("時間", style="yellow")

    table.add_row("FP32", result["fp32_time"])
    table.add_row("FP16", result["fp16_time"])
    table.add_row("加速比", result["speedup"])

    console.print(table)

    console.print("\n" + "="*60)
    console.print("[bold green]✓ GPU 運算示例完成！[/bold green]")


def print_gpu_pricing():
    """打印 GPU 價格信息"""
    console.print("\n" + "="*60)
    console.print("[bold cyan]Modal GPU 價格參考:[/bold cyan]\n")

    table = Table(show_header=True)
    table.add_column("GPU 型號", style="cyan")
    table.add_column("顯存", style="yellow")
    table.add_column("價格/秒", style="green")
    table.add_column("價格/小時", style="magenta")
    table.add_column("適用場景", style="white")

    table.add_row(
        "T4",
        "16 GB",
        "$0.00055",
        "$1.98",
        "推理、中小模型"
    )
    table.add_row(
        "A10G",
        "24 GB",
        "$0.0012",
        "$4.32",
        "推理、中型模型"
    )
    table.add_row(
        "A100",
        "40/80 GB",
        "$0.0040",
        "$14.40",
        "訓練、大模型"
    )
    table.add_row(
        "H100",
        "80 GB",
        "$0.0120",
        "$43.20",
        "大規模訓練"
    )

    console.print(table)

    console.print("""
[green]選擇建議:[/green]
  • 開發/測試: T4（最便宜）
  • 中小模型推理: T4 或 A10G
  • 大模型推理: A100
  • 模型訓練: A100 或 H100
  • 大規模訓練: H100

[yellow]成本優化:[/yellow]
  ✓ 使用批量處理提升 GPU 利用率
  ✓ 選擇合適的 GPU 型號（不要過度配置）
  ✓ 使用混合精度（FP16）加速
  ✓ 合理設置超時時間
    """)
    console.print("="*60 + "\n")


if __name__ == "__main__":
    print_gpu_pricing()
    console.print("[yellow]使用 'modal run 03_GPU運算.py' 運行此示例[/yellow]\n")
    console.print("[red]注意: GPU 使用會產生費用，請監控使用量！[/red]\n")

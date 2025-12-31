"""
Modal 函數部署示例

本示例展示：
1. 不同類型的函數部署
2. 函數調用方式
3. 同步 vs 異步執行
4. 函數配置選項
"""

import modal
from rich.console import Console
from rich.panel import Panel
import time

console = Console()

# 創建應用
app = modal.App("function-deployment")


# 示例 1: 基本函數
@app.function()
def basic_function(x: int) -> int:
    """最基本的函數"""
    print(f"處理輸入: {x}")
    return x * 2


# 示例 2: 配置資源的函數
@app.function(
    cpu=2,           # 2 個 CPU 核心
    memory=1024,     # 1GB 內存
    timeout=60       # 60 秒超時
)
def resource_function(data: list) -> dict:
    """配置了資源限制的函數"""
    import psutil

    print(f"CPU 核心數: {psutil.cpu_count()}")
    print(f"可用內存: {psutil.virtual_memory().total / 1e9:.2f} GB")

    # 處理數據
    result = sum(data)

    return {
        "sum": result,
        "count": len(data),
        "average": result / len(data)
    }


# 示例 3: 長時間運行的函數
@app.function(timeout=300)  # 5 分鐘超時
def long_running_task(duration: int) -> str:
    """模擬長時間運行的任務"""
    print(f"開始執行，預計耗時 {duration} 秒")

    for i in range(duration):
        print(f"進度: {i+1}/{duration}")
        time.sleep(1)

    print("任務完成！")
    return f"成功執行了 {duration} 秒的任務"


# 示例 4: 返回多個值的函數
@app.function()
def multi_return(text: str) -> tuple:
    """返回多個值"""
    return (
        text.upper(),
        text.lower(),
        len(text),
        text[::-1]  # 反轉
    )


# 示例 5: 處理異常的函數
@app.function()
def error_handling(x: int, y: int) -> dict:
    """展示錯誤處理"""
    try:
        result = x / y
        return {"success": True, "result": result}
    except ZeroDivisionError:
        print("錯誤: 除數不能為零")
        return {"success": False, "error": "Division by zero"}
    except Exception as e:
        print(f"未知錯誤: {e}")
        return {"success": False, "error": str(e)}


# 示例 6: 使用環境變量的函數
@app.function(
    secrets=[modal.Secret.from_name("my-secret")]  # 需要先創建 secret
)
def with_secrets() -> dict:
    """使用 secrets 的函數"""
    import os

    # 從環境變量讀取 secret
    # api_key = os.environ.get("API_KEY", "not-set")

    return {
        "has_secrets": True,
        "env_vars": len(os.environ)
    }


# 示例 7: 重試機制
@app.function(retries=3)  # 失敗後重試 3 次
def flaky_function(should_fail: bool = False) -> str:
    """可能失敗的函數（帶重試）"""
    import random

    if should_fail or random.random() < 0.3:
        print("模擬失敗...")
        raise Exception("Random failure!")

    return "Success!"


@app.local_entrypoint()
def main():
    """本地入口"""
    console.print(Panel.fit(
        "[bold cyan]Modal 函數部署示例[/bold cyan]\n"
        "[dim]各種函數配置和調用方式[/dim]",
        border_style="cyan"
    ))

    # 1. 基本函數調用
    console.print("\n[cyan]1. 基本函數調用[/cyan]")
    result = basic_function.remote(5)
    console.print(f"[green]結果: {result}[/green]")

    # 2. 資源配置函數
    console.print("\n[cyan]2. 資源配置函數[/cyan]")
    data = list(range(1, 101))
    result = resource_function.remote(data)
    console.print(f"[green]結果: {result}[/green]")

    # 3. 長時間運行（異步）
    console.print("\n[cyan]3. 長時間運行任務（5 秒）[/cyan]")
    console.print("[yellow]正在執行...[/yellow]")
    result = long_running_task.remote(5)
    console.print(f"[green]結果: {result}[/green]")

    # 4. 多返回值
    console.print("\n[cyan]4. 多返回值函數[/cyan]")
    upper, lower, length, reversed_text = multi_return.remote("Hello Modal")
    console.print(f"[green]大寫: {upper}[/green]")
    console.print(f"[green]小寫: {lower}[/green]")
    console.print(f"[green]長度: {length}[/green]")
    console.print(f"[green]反轉: {reversed_text}[/green]")

    # 5. 錯誤處理
    console.print("\n[cyan]5. 錯誤處理[/cyan]")
    result1 = error_handling.remote(10, 2)
    console.print(f"[green]正常: {result1}[/green]")

    result2 = error_handling.remote(10, 0)
    console.print(f"[yellow]異常: {result2}[/yellow]")

    # 6. 批量並行調用
    console.print("\n[cyan]6. 批量並行調用（10 個函數）[/cyan]")
    start_time = time.time()

    # 並行執行多個函數
    results = [basic_function.remote(i) for i in range(10)]

    elapsed = time.time() - start_time
    console.print(f"[green]結果: {results}[/green]")
    console.print(f"[dim]耗時: {elapsed:.2f} 秒（並行執行）[/dim]")

    # 7. 使用 map 進行批量處理
    console.print("\n[cyan]7. 使用 map 批量處理[/cyan]")
    inputs = list(range(1, 11))

    # 使用 map 並行處理
    start_time = time.time()
    results = list(basic_function.map(inputs))
    elapsed = time.time() - start_time

    console.print(f"[green]輸入: {inputs}[/green]")
    console.print(f"[green]結果: {results}[/green]")
    console.print(f"[dim]耗時: {elapsed:.2f} 秒[/dim]")

    # 8. 重試機制測試
    console.print("\n[cyan]8. 重試機制測試[/cyan]")
    try:
        # 強制成功
        result = flaky_function.remote(should_fail=False)
        console.print(f"[green]結果: {result}[/green]")
    except Exception as e:
        console.print(f"[red]失敗: {e}[/red]")

    console.print("\n" + "="*60)
    console.print("[bold green]✓ 函數部署示例完成！[/bold green]")


def print_deployment_guide():
    """打印部署指南"""
    console.print("\n" + "="*60)
    console.print("[bold cyan]函數部署指南:[/bold cyan]")
    console.print("""
[green]1. 函數配置選項:[/green]

@app.function(
    cpu=2,              # CPU 核心數（0.25-32）
    memory=1024,        # 內存 MB（128-262144）
    gpu="A100",         # GPU 類型（T4/A10G/A100/H100）
    timeout=60,         # 超時秒數
    retries=3,          # 重試次數
    secrets=[...],      # Secrets
    volumes={...},      # Volumes
    image=...,          # 自定義鏡像
)

[green]2. 調用方式:[/green]

# 同步調用（等待結果）
result = func.remote(arg)

# 異步調用（獲取 future）
future = func.spawn(arg)
result = future.get()

# 批量調用
results = list(func.map([arg1, arg2, arg3]))

# 並行調用
futures = [func.spawn(arg) for arg in args]
results = [f.get() for f in futures]

[green]3. 部署命令:[/green]

# 臨時運行
modal run script.py

# 部署為持久服務
modal deploy script.py

# 本地開發模式
modal serve script.py
    """)
    console.print("="*60 + "\n")


if __name__ == "__main__":
    print_deployment_guide()
    console.print("[yellow]使用 'modal run 02_函數部署.py' 運行此示例[/yellow]\n")

"""
Modal 並行計算示例

本示例展示：
1. 使用 map() 並行處理
2. 並行 vs 順序執行對比
3. 動態並發控制
4. 實際應用場景
"""

import modal
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import time

console = Console()

# 創建應用
app = modal.App("parallel-computing")


# 示例 1: 計算密集型任務
@app.function(cpu=2)
def compute_fibonacci(n: int) -> dict:
    """計算斐波那契數列（計算密集）"""
    def fib(x):
        if x <= 1:
            return x
        return fib(x - 1) + fib(x - 2)

    start = time.time()
    result = fib(n)
    elapsed = time.time() - start

    return {
        "n": n,
        "result": result,
        "time": elapsed
    }


# 示例 2: I/O 密集型任務
@app.function()
def fetch_url(url: str) -> dict:
    """模擬網絡請求（I/O 密集）"""
    import requests

    print(f"請求: {url}")
    start = time.time()

    try:
        response = requests.get(url, timeout=10)
        elapsed = time.time() - start

        return {
            "url": url,
            "status": response.status_code,
            "time": elapsed,
            "size": len(response.content)
        }
    except Exception as e:
        return {
            "url": url,
            "error": str(e),
            "time": time.time() - start
        }


# 示例 3: 數據處理任務
@app.function()
def process_record(record: dict) -> dict:
    """處理單條記錄"""
    # 模擬處理時間
    time.sleep(0.1)

    # 數據轉換
    processed = {
        "id": record["id"],
        "value": record["value"] * 2,
        "squared": record["value"] ** 2,
        "category": record.get("category", "unknown").upper()
    }

    return processed


# 示例 4: 批量處理任務
@app.function()
def batch_process(batch: list) -> dict:
    """處理一批數據"""
    print(f"處理批次，包含 {len(batch)} 個項目")

    start = time.time()

    # 處理批次
    results = []
    for item in batch:
        # 模擬處理
        time.sleep(0.01)
        results.append(item * 2)

    elapsed = time.time() - start

    return {
        "batch_size": len(batch),
        "results": results,
        "time": elapsed
    }


# 示例 5: Map-Reduce 模式
@app.function()
def map_task(chunk: list) -> dict:
    """Map 階段：處理數據塊"""
    print(f"Map: 處理 {len(chunk)} 個項目")

    # 計算局部聚合
    total = sum(chunk)
    count = len(chunk)
    max_val = max(chunk)
    min_val = min(chunk)

    return {
        "sum": total,
        "count": count,
        "max": max_val,
        "min": min_val
    }


@app.function()
def reduce_task(results: list) -> dict:
    """Reduce 階段：合併結果"""
    print(f"Reduce: 合併 {len(results)} 個結果")

    # 合併所有結果
    total_sum = sum(r["sum"] for r in results)
    total_count = sum(r["count"] for r in results)
    global_max = max(r["max"] for r in results)
    global_min = min(r["min"] for r in results)

    return {
        "total": total_sum,
        "count": total_count,
        "average": total_sum / total_count if total_count > 0 else 0,
        "max": global_max,
        "min": global_min
    }


# 示例 6: 並行 Web 爬蟲
@app.function()
def scrape_page(url: str) -> dict:
    """爬取單個頁面"""
    import requests
    from bs4 import BeautifulSoup

    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        return {
            "url": url,
            "title": soup.title.string if soup.title else "No title",
            "links": len(soup.find_all('a')),
            "images": len(soup.find_all('img'))
        }
    except Exception as e:
        return {
            "url": url,
            "error": str(e)
        }


@app.local_entrypoint()
def main():
    """本地測試"""
    console.print(Panel.fit(
        "[bold cyan]Modal 並行計算示例[/bold cyan]\n"
        "[dim]高效並行處理任務[/dim]",
        border_style="cyan"
    ))

    # 1. 順序 vs 並行對比
    console.print("\n[cyan]1. 順序 vs 並行執行對比[/cyan]")

    # 測試數據
    numbers = [30, 31, 32, 33, 34]

    # 順序執行
    console.print("[yellow]  順序執行...[/yellow]")
    start = time.time()
    sequential_results = []
    for n in numbers:
        result = compute_fibonacci.remote(n)
        sequential_results.append(result)
    sequential_time = time.time() - start

    # 並行執行
    console.print("[yellow]  並行執行...[/yellow]")
    start = time.time()
    parallel_results = list(compute_fibonacci.map(numbers))
    parallel_time = time.time() - start

    # 結果對比
    table = Table(title="性能對比")
    table.add_column("執行方式", style="cyan")
    table.add_column("耗時", style="yellow")
    table.add_column("加速比", style="green")

    table.add_row("順序執行", f"{sequential_time:.2f}s", "-")
    table.add_row("並行執行", f"{parallel_time:.2f}s", f"{sequential_time/parallel_time:.2f}x")

    console.print(table)

    # 2. 批量數據處理
    console.print("\n[cyan]2. 批量並行處理[/cyan]")

    # 創建測試數據
    records = [
        {"id": i, "value": i * 10, "category": f"cat_{i % 3}"}
        for i in range(100)
    ]

    start = time.time()
    processed = list(process_record.map(records))
    elapsed = time.time() - start

    console.print(f"[green]處理 {len(records)} 條記錄[/green]")
    console.print(f"[dim]耗時: {elapsed:.2f}s[/dim]")
    console.print(f"[dim]吞吐量: {len(records)/elapsed:.2f} 記錄/秒[/dim]")

    # 3. Map-Reduce 示例
    console.print("\n[cyan]3. Map-Reduce 並行聚合[/cyan]")

    # 大型數據集
    large_data = list(range(1, 10001))

    # 分塊
    chunk_size = 1000
    chunks = [
        large_data[i:i + chunk_size]
        for i in range(0, len(large_data), chunk_size)
    ]

    console.print(f"[yellow]  Map: 處理 {len(chunks)} 個數據塊...[/yellow]")
    start = time.time()
    map_results = list(map_task.map(chunks))
    map_time = time.time() - start

    console.print(f"[yellow]  Reduce: 合併結果...[/yellow]")
    start = time.time()
    final_result = reduce_task.remote(map_results)
    reduce_time = time.time() - start

    console.print(f"[green]結果:[/green]")
    console.print(f"  總和: {final_result['total']}")
    console.print(f"  平均: {final_result['average']:.2f}")
    console.print(f"  最大: {final_result['max']}")
    console.print(f"  最小: {final_result['min']}")
    console.print(f"[dim]Map 耗時: {map_time:.2f}s, Reduce 耗時: {reduce_time:.2f}s[/dim]")

    # 4. 並行批處理
    console.print("\n[cyan]4. 並行批處理[/cyan]")

    data = list(range(1, 1001))

    # 分批
    batch_size = 100
    batches = [
        data[i:i + batch_size]
        for i in range(0, len(data), batch_size)
    ]

    console.print(f"[yellow]  處理 {len(batches)} 個批次（每批 {batch_size} 個項目）...[/yellow]")
    start = time.time()
    batch_results = list(batch_process.map(batches))
    elapsed = time.time() - start

    total_processed = sum(r["batch_size"] for r in batch_results)

    console.print(f"[green]處理完成: {total_processed} 個項目[/green]")
    console.print(f"[dim]耗時: {elapsed:.2f}s[/dim]")

    console.print("\n" + "="*60)
    console.print("[bold green]✓ 並行計算示例完成！[/bold green]")


def print_parallel_guide():
    """打印並行計算指南"""
    console.print("\n" + "="*60)
    console.print("[bold cyan]並行計算最佳實踐:[/bold cyan]")
    console.print("""
[green]1. 使用 map() 並行處理:[/green]

# 基本用法
results = list(func.map(items))

# 帶額外參數
results = list(func.map(
    items,
    kwargs=[{"param": value} for _ in items]
))

# 使用 enumerate
results = list(func.map(
    enumerate(items),
    kwargs=[{"index": i} for i in range(len(items))]
))

[green]2. 使用 starmap() 解包參數:[/green]

# 多個參數
args_list = [(arg1, arg2), (arg3, arg4)]
results = list(func.starmap(args_list))

[green]3. Map-Reduce 模式:[/green]

# Map 階段
map_results = list(map_func.map(chunks))

# Reduce 階段
final = reduce_func.remote(map_results)

[green]4. 並發控制:[/green]

# 限制並發數
@app.function(concurrency_limit=10)
def limited_func():
    pass

[yellow]何時使用並行:[/yellow]

✓ I/O 密集型任務（網絡請求、文件讀寫）
✓ 計算密集型任務（數據處理、模型推理）
✓ 獨立的任務（無依賴關係）
✓ 大批量數據處理

[yellow]何時避免並行:[/yellow]

✗ 任務間有強依賴關係
✗ 單個任務執行時間很短（< 0.1s）
✗ 需要嚴格的執行順序
✗ 共享狀態的任務

[yellow]性能優化:[/yellow]

✓ 合理設置批次大小
✓ 避免過度並行（成本）
✓ 使用合適的 CPU/內存配置
✓ 監控並發數和成本
    """)
    console.print("="*60 + "\n")


if __name__ == "__main__":
    print_parallel_guide()
    console.print("[yellow]運行並行計算示例:[/yellow]")
    console.print("  modal run 08_並行計算.py\n")

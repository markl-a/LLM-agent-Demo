"""
Burr 並行執行 - 優化性能

這個示例展示如何：
1. 並行執行多個動作
2. 批處理優化
3. 異步操作
4. 性能監控

Burr 支持並行執行以提升性能。
"""

from burr.core import action, State, ApplicationBuilder, expr
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict

console = Console()


# ============================================================================
# 示例 1：批處理
# ============================================================================

@action(reads=["items"], writes=["items", "processed_count"])
def process_batch_items(state: State, batch_size: int = 10) -> State:
    """批處理項目"""
    items = state.get("items", [])
    processed_count = state.get("processed_count", 0)

    # 模擬批處理
    start_time = time.time()

    # 一次處理 batch_size 個項目
    batch = items[:batch_size]
    remaining = items[batch_size:]

    # 模擬處理時間（批處理更快）
    time.sleep(0.1)  # 無論批次大小，處理時間固定

    processed_count += len(batch)
    duration = time.time() - start_time

    return state.update(
        items=remaining,
        processed_count=processed_count,
        last_batch_size=len(batch),
        last_duration=duration
    )


def batch_processing_example():
    """示例 1：批處理"""
    console.print(Panel("[bold cyan]示例 1：批處理優化[/bold cyan]"))

    # 創建大量項目
    total_items = 100
    items = list(range(total_items))

    # 比較不同批次大小
    batch_sizes = [1, 10, 20]

    for batch_size in batch_sizes:
        console.print(f"\n[yellow]批次大小: {batch_size}[/yellow]")

        # 構建應用
        app = (
            ApplicationBuilder()
            .with_state(
                items=items.copy(),
                processed_count=0,
                total_items=total_items
            )
            .with_actions(
                process_batch_items.bind(batch_size=batch_size)
            )
            .with_transitions(
                ("process_batch_items", "process_batch_items",
                 expr("len(items) > 0")),
            )
            .with_entrypoint("process_batch_items")
            .build()
        )

        # 執行並計時
        start_time = time.time()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            task = progress.add_task(f"處理中...", total=None)

            while len(app.state.get("items", [])) > 0:
                action_result, state, _ = app.step()

        total_time = time.time() - start_time

        console.print(f"  總時間: {total_time:.2f} 秒")
        console.print(f"  每項平均時間: {total_time/total_items*1000:.2f} 毫秒")
        console.print(f"  處理項目數: {state['processed_count']}")


# ============================================================================
# 示例 2：並行動作執行
# ============================================================================

@action(reads=["data"], writes=["result_a"])
def process_a(state: State) -> State:
    """處理 A（耗時操作）"""
    time.sleep(0.2)
    result = f"處理 A 完成: {state['data']}"
    return state.update(result_a=result)


@action(reads=["data"], writes=["result_b"])
def process_b(state: State) -> State:
    """處理 B（耗時操作）"""
    time.sleep(0.2)
    result = f"處理 B 完成: {state['data']}"
    return state.update(result_b=result)


@action(reads=["data"], writes=["result_c"])
def process_c(state: State) -> State:
    """處理 C（耗時操作）"""
    time.sleep(0.2)
    result = f"處理 C 完成: {state['data']}"
    return state.update(result_c=result)


@action(reads=["result_a", "result_b", "result_c"], writes=["final_result"])
def combine_results(state: State) -> State:
    """合併結果"""
    results = [
        state.get("result_a", ""),
        state.get("result_b", ""),
        state.get("result_c", "")
    ]
    return state.update(final_result=", ".join(results))


def parallel_actions_example():
    """示例 2：並行動作執行（概念演示）"""
    console.print(Panel("[bold cyan]示例 2：並行動作概念[/bold cyan]"))

    console.print("""
[yellow]Burr 並行執行說明：[/yellow]

Burr 的核心是狀態機，每個動作按順序執行。但可以通過以下方式實現並行：

1. [cyan]外部並行化[/cyan]
   - 在動作內部使用線程池
   - 使用 asyncio 處理異步操作
   - 並行調用外部 API

2. [cyan]多實例並行[/cyan]
   - 創建多個 Burr 應用實例
   - 每個實例處理不同的任務
   - 使用進程池或分布式系統

3. [cyan]數據並行[/cyan]
   - 將數據分批
   - 每批數據獨立處理
   - 最後合併結果

[yellow]示例：內部並行化[/yellow]
    """)

    # 演示：順序執行 vs 並行執行
    console.print("\n[cyan]順序執行：[/cyan]")

    start_time = time.time()

    app_sequential = (
        ApplicationBuilder()
        .with_state(data="測試數據")
        .with_actions(process_a, process_b, process_c, combine_results)
        .with_transitions(
            ("process_a", "process_b"),
            ("process_b", "process_c"),
            ("process_c", "combine_results"),
        )
        .with_entrypoint("process_a")
        .build()
    )

    # 執行
    for _ in range(4):
        action_result, state, _ = app_sequential.step()

    sequential_time = time.time() - start_time
    console.print(f"  耗時: {sequential_time:.2f} 秒")

    # 並行執行（在動作內部）
    console.print("\n[cyan]並行執行（模擬）：[/cyan]")

    @action(reads=["data"], writes=["result_a", "result_b", "result_c"])
    def process_parallel(state: State) -> State:
        """並行處理"""
        data = state["data"]

        def task_a():
            time.sleep(0.2)
            return f"處理 A 完成: {data}"

        def task_b():
            time.sleep(0.2)
            return f"處理 B 完成: {data}"

        def task_c():
            time.sleep(0.2)
            return f"處理 C 完成: {data}"

        # 使用線程池並行執行
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_a = executor.submit(task_a)
            future_b = executor.submit(task_b)
            future_c = executor.submit(task_c)

            result_a = future_a.result()
            result_b = future_b.result()
            result_c = future_c.result()

        return state.update(
            result_a=result_a,
            result_b=result_b,
            result_c=result_c
        )

    start_time = time.time()

    app_parallel = (
        ApplicationBuilder()
        .with_state(data="測試數據")
        .with_actions(process_parallel, combine_results)
        .with_transitions(
            ("process_parallel", "combine_results"),
        )
        .with_entrypoint("process_parallel")
        .build()
    )

    # 執行
    for _ in range(2):
        action_result, state, _ = app_parallel.step()

    parallel_time = time.time() - start_time
    console.print(f"  耗時: {parallel_time:.2f} 秒")

    # 比較
    console.print(f"\n[green]加速比: {sequential_time/parallel_time:.2f}x[/green]")


# ============================================================================
# 示例 3：異步操作
# ============================================================================

async def async_api_call(item_id: int) -> str:
    """模擬異步 API 調用"""
    await asyncio.sleep(0.1)  # 模擬網絡延遲
    return f"Item {item_id} data"


@action(reads=["item_ids"], writes=["api_results"])
def fetch_data_async(state: State) -> State:
    """異步獲取數據"""
    item_ids = state["item_ids"]

    async def fetch_all():
        """異步獲取所有數據"""
        tasks = [async_api_call(item_id) for item_id in item_ids]
        results = await asyncio.gather(*tasks)
        return results

    # 運行異步任務
    results = asyncio.run(fetch_all())

    return state.update(api_results=results)


def async_operations_example():
    """示例 3：異步操作"""
    console.print(Panel("[bold cyan]示例 3：異步操作[/bold cyan]"))

    item_ids = list(range(10))

    console.print(f"\n[yellow]獲取 {len(item_ids)} 個項目的數據[/yellow]")

    # 順序執行
    console.print("\n[cyan]順序執行：[/cyan]")
    start_time = time.time()

    @action(reads=["item_ids"], writes=["api_results"])
    def fetch_data_sync(state: State) -> State:
        """同步獲取數據"""
        item_ids = state["item_ids"]
        results = []
        for item_id in item_ids:
            time.sleep(0.1)  # 模擬 API 調用
            results.append(f"Item {item_id} data")
        return state.update(api_results=results)

    app_sync = (
        ApplicationBuilder()
        .with_state(item_ids=item_ids)
        .with_actions(fetch_data_sync)
        .with_entrypoint("fetch_data_sync")
        .build()
    )

    action_result, state, _ = app_sync.step()
    sync_time = time.time() - start_time

    console.print(f"  耗時: {sync_time:.2f} 秒")
    console.print(f"  獲取結果數: {len(state['api_results'])}")

    # 異步執行
    console.print("\n[cyan]異步執行：[/cyan]")
    start_time = time.time()

    app_async = (
        ApplicationBuilder()
        .with_state(item_ids=item_ids)
        .with_actions(fetch_data_async)
        .with_entrypoint("fetch_data_async")
        .build()
    )

    action_result, state, _ = app_async.step()
    async_time = time.time() - start_time

    console.print(f"  耗時: {async_time:.2f} 秒")
    console.print(f"  獲取結果數: {len(state['api_results'])}")

    console.print(f"\n[green]加速比: {sync_time/async_time:.2f}x[/green]")


# ============================================================================
# 示例 4：性能監控
# ============================================================================

def performance_monitoring_example():
    """示例 4：性能監控"""
    console.print(Panel("[bold cyan]示例 4：性能監控[/bold cyan]"))

    console.print("""
[yellow]性能監控策略：[/yellow]

1. [cyan]執行時間追蹤[/cyan]
   - 追蹤每個動作的執行時間
   - 識別性能瓶頸
   - 生成性能報告

2. [cyan]資源使用監控[/cyan]
   - 內存使用
   - CPU 使用率
   - API 調用次數

3. [cyan]性能優化建議[/cyan]
   - 批處理優化
   - 並行化機會
   - 緩存策略

4. [cyan]實時監控[/cyan]
   - 使用 Burr UI 查看
   - 自定義監控面板
   - 告警機制

[yellow]性能優化清單：[/yellow]
    """)

    optimization_checklist = '''
✓ 使用批處理減少開銷
✓ 並行執行獨立任務
✓ 異步處理 I/O 密集型操作
✓ 緩存重複計算結果
✓ 優化數據結構
✓ 減少狀態複製
✓ 使用生成器處理大數據
✓ 監控和分析性能指標
    '''

    console.print(Panel(optimization_checklist, border_style="green"))

    # 性能指標示例
    console.print("\n[yellow]性能指標示例：[/yellow]")

    metrics_table = Table(title="性能指標")
    metrics_table.add_column("指標", style="cyan")
    metrics_table.add_column("值", style="green")
    metrics_table.add_column("建議", style="yellow")

    metrics_table.add_row(
        "平均響應時間",
        "150ms",
        "✓ 良好"
    )
    metrics_table.add_row(
        "批處理大小",
        "10",
        "可增加到 20"
    )
    metrics_table.add_row(
        "並行度",
        "1",
        "⚠ 考慮並行化"
    )
    metrics_table.add_row(
        "緩存命中率",
        "85%",
        "✓ 優秀"
    )

    console.print(metrics_table)


# ============================================================================
# 主函數
# ============================================================================

def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold green]Burr 並行執行 - 優化性能[/bold green]",
        border_style="green"
    ))

    console.print("\n[bold]並行執行核心概念：[/bold]")
    console.print("1. [cyan]批處理[/cyan]: 減少處理開銷")
    console.print("2. [cyan]內部並行[/cyan]: 動作內使用線程池")
    console.print("3. [cyan]異步操作[/cyan]: 提升 I/O 效率")
    console.print("4. [cyan]性能監控[/cyan]: 識別瓶頸\n")

    # 運行示例
    batch_processing_example()
    console.print("\n" + "="*60 + "\n")

    parallel_actions_example()
    console.print("\n" + "="*60 + "\n")

    async_operations_example()
    console.print("\n" + "="*60 + "\n")

    performance_monitoring_example()

    # 總結
    console.print(Panel("""
[bold green]並行執行完成！[/bold green]

關鍵要點：
1. Burr 是狀態機，動作順序執行
2. 在動作內部實現並行化
3. 使用批處理優化性能
4. 異步操作提升 I/O 效率
5. 持續監控和優化性能

並行化策略：
- 批處理: 減少開銷
- 線程池: CPU 密集型任務
- Asyncio: I/O 密集型任務
- 多實例: 分布式處理

性能優化建議：
- 識別瓶頸動作
- 合理設置批次大小
- 使用異步 API 調用
- 實現結果緩存
- 監控資源使用

最佳實踐：
- 先優化算法，再優化執行
- 測量再優化，避免過早優化
- 使用 Burr UI 分析性能
- 設置性能基準
- 持續監控生產環境

下一步：
- 查看 10_生產部署.py 部署應用
- 閱讀 Burr 性能優化文檔
    """, title="總結", border_style="green"))


if __name__ == "__main__":
    main()

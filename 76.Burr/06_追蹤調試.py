"""
Burr 追蹤調試 - 時間旅行與可視化

這個示例展示如何：
1. 啟用完整追蹤
2. 使用 Burr UI 可視化
3. 時間旅行調試
4. 追蹤性能指標

Burr 提供強大的可觀測性工具，讓調試變得簡單。
"""

from burr.core import action, State, ApplicationBuilder, expr
from burr.tracking import LocalTrackingClient
from burr.visibility import TracerFactory
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import time
from datetime import datetime

console = Console()


# ============================================================================
# 示例 1：基本追蹤
# ============================================================================

@action(reads=["value"], writes=["value", "operations"])
def add_value(state: State, amount: int) -> State:
    """添加值"""
    value = state.get("value", 0)
    operations = state.get("operations", [])

    new_value = value + amount
    operations.append({
        "type": "add",
        "amount": amount,
        "result": new_value,
        "timestamp": datetime.now().isoformat()
    })

    # 模擬一些處理時間
    time.sleep(0.1)

    return state.update(value=new_value, operations=operations)


@action(reads=["value"], writes=["value", "operations"])
def multiply_value(state: State, factor: int) -> State:
    """乘以值"""
    value = state.get("value", 0)
    operations = state.get("operations", [])

    new_value = value * factor
    operations.append({
        "type": "multiply",
        "factor": factor,
        "result": new_value,
        "timestamp": datetime.now().isoformat()
    })

    time.sleep(0.1)

    return state.update(value=new_value, operations=operations)


def basic_tracking_example():
    """示例 1：基本追蹤"""
    console.print(Panel("[bold cyan]示例 1：基本追蹤[/bold cyan]"))

    # 創建追蹤客戶端
    tracker = LocalTrackingClient(project="burr_demo")

    console.print("\n[yellow]構建帶追蹤的應用：[/yellow]")

    # 構建應用（啟用追蹤）
    app = (
        ApplicationBuilder()
        .with_state(value=10, operations=[])
        .with_actions(
            add_value.bind(amount=5),
            multiply_value.bind(factor=2),
        )
        .with_transitions(
            ("add_value", "multiply_value"),
            ("multiply_value", "add_value"),
        )
        .with_entrypoint("add_value")
        .with_tracker(tracker)
        .build()
    )

    console.print("[green]✓ 追蹤已啟用[/green]")

    # 執行一些操作
    console.print("\n[yellow]執行操作（所有步驟都被追蹤）：[/yellow]")

    operations_sequence = [
        ("add_value", 5),
        ("multiply_value", 2),
        ("add_value", 10),
        ("multiply_value", 3),
    ]

    for i, (op_name, _) in enumerate(operations_sequence):
        action_result, state, _ = app.step()
        console.print(
            f"  步驟 {i+1}: {action_result.name}, "
            f"值={state['value']}"
        )

    # 顯示追蹤信息
    console.print("\n[green]✓ 所有操作已追蹤[/green]")
    console.print("[yellow]提示：追蹤數據已保存到本地[/yellow]")


# ============================================================================
# 示例 2：詳細追蹤信息
# ============================================================================

@action(reads=["items"], writes=["items", "processed_count"])
def process_item(state: State, item_id: int) -> State:
    """處理項目（帶詳細追蹤）"""
    items = state.get("items", [])
    processed_count = state.get("processed_count", 0)

    # 模擬處理
    start_time = time.time()
    time.sleep(0.05)  # 模擬處理時間

    item = {
        "id": item_id,
        "processed_at": datetime.now().isoformat(),
        "duration_ms": (time.time() - start_time) * 1000
    }

    items.append(item)

    return state.update(
        items=items,
        processed_count=processed_count + 1
    )


def detailed_tracking_example():
    """示例 2：詳細追蹤信息"""
    console.print(Panel("[bold cyan]示例 2：詳細追蹤信息[/bold cyan]"))

    tracker = LocalTrackingClient(project="detailed_demo")

    # 構建應用
    app = (
        ApplicationBuilder()
        .with_state(items=[], processed_count=0, total=5)
        .with_actions(process_item)
        .with_transitions(
            ("process_item", "process_item", expr("processed_count < total")),
        )
        .with_entrypoint("process_item")
        .with_tracker(tracker)
        .build()
    )

    console.print("\n[yellow]處理項目（追蹤性能指標）：[/yellow]")

    # 處理多個項目
    for i in range(5):
        action_result, state, _ = app.step()

        # 需要重新綁定 item_id
        app = (
            ApplicationBuilder()
            .with_state(**dict(state._state))
            .with_actions(process_item.bind(item_id=i+2))
            .with_transitions(
                ("process_item", "process_item", expr("processed_count < total")),
            )
            .with_tracker(tracker)
            .build()
        )

    # 創建性能報表
    items = state["items"]
    table = Table(title="處理性能報表")
    table.add_column("項目 ID", style="cyan")
    table.add_column("處理時間", style="green")
    table.add_column("完成時間", style="yellow")

    for item in items:
        table.add_row(
            str(item["id"]),
            f"{item['duration_ms']:.2f} ms",
            item["processed_at"]
        )

    console.print("\n")
    console.print(table)

    # 統計
    avg_duration = sum(item["duration_ms"] for item in items) / len(items)
    console.print(f"\n[green]平均處理時間: {avg_duration:.2f} ms[/green]")


# ============================================================================
# 示例 3：Burr UI 集成
# ============================================================================

def burr_ui_example():
    """示例 3：Burr UI 集成"""
    console.print(Panel("[bold cyan]示例 3：Burr UI 集成[/bold cyan]"))

    console.print("""
[yellow]Burr UI 使用步驟：[/yellow]

1. [cyan]安裝完整版本[/cyan]：
   pip install "burr[start]"

2. [cyan]在代碼中啟用追蹤[/cyan]：
   app = (
       ApplicationBuilder()
       ...
       .with_tracker(tracker="local")  # 使用本地追蹤
       .build()
   )

3. [cyan]啟動 Burr UI[/cyan]：
   burr

   默認端口：7241
   訪問：http://localhost:7241

4. [cyan]查看功能[/cyan]：
   - 實時狀態轉換圖
   - 狀態歷史時間線
   - 每個動作的詳細信息
   - 性能指標和統計
   - 時間旅行調試

[yellow]UI 特性：[/yellow]

📊 [cyan]狀態機可視化[/cyan]
   - 查看完整的狀態轉換圖
   - 高亮當前狀態
   - 顯示轉換條件

⏱️ [cyan]時間旅行[/cyan]
   - 回到任意歷史狀態
   - 查看狀態演變過程
   - 重放執行序列

📈 [cyan]性能分析[/cyan]
   - 每個動作的執行時間
   - 狀態大小追蹤
   - 瓶頸識別

🔍 [cyan]調試工具[/cyan]
   - 檢查輸入輸出
   - 查看完整的狀態快照
   - 錯誤追蹤

[green]提示：運行任何帶追蹤的應用後，啟動 Burr UI 即可查看所有追蹤數據[/green]
    """)


# ============================================================================
# 示例 4：時間旅行調試
# ============================================================================

def time_travel_debugging():
    """示例 4：時間旅行調試"""
    console.print(Panel("[bold cyan]示例 4：時間旅行調試[/bold cyan]"))

    console.print("""
[yellow]時間旅行調試概念：[/yellow]

時間旅行調試允許你：
1. 回到應用的任意歷史狀態
2. 從該狀態重新開始執行
3. 比較不同執行路徑的結果

[cyan]使用場景：[/cyan]

🐛 [yellow]調試錯誤[/yellow]
   - 發現錯誤後，回到錯誤發生前
   - 檢查導致錯誤的狀態
   - 嘗試不同的執行路徑

🔬 [yellow]實驗不同策略[/yellow]
   - 從某個狀態分叉
   - 嘗試不同的決策
   - 比較結果

📊 [yellow]性能分析[/yellow]
   - 識別慢操作
   - 測試優化方案
   - 比較前後性能

[cyan]代碼示例：[/cyan]
    """)

    example_code = '''
# 從追蹤中加載歷史狀態
from burr.tracking import LocalTrackingClient

tracker = LocalTrackingClient(project="my_project")

# 獲取特定執行的狀態歷史
run_id = "some_run_id"
states = tracker.load_state_history(run_id)

# 選擇一個歷史狀態
historical_state = states[5]  # 第6個狀態

# 從該狀態重新構建應用
app = (
    ApplicationBuilder()
    .with_state(**historical_state)
    .with_actions(...)
    .build()
)

# 從這裡繼續執行
app.step()  # 會從歷史狀態繼續
    '''

    console.print(Panel(example_code, border_style="blue", title="時間旅行示例"))

    # 實際演示
    console.print("\n[yellow]實際演示：[/yellow]")

    tracker = LocalTrackingClient(project="time_travel_demo")

    # 創建初始應用
    app = (
        ApplicationBuilder()
        .with_state(counter=0, history=[])
        .with_actions(
            add_value.bind(amount=1),
            multiply_value.bind(factor=2)
        )
        .with_transitions(
            ("add_value", "multiply_value"),
            ("multiply_value", "add_value"),
        )
        .with_entrypoint("add_value")
        .with_tracker(tracker)
        .build()
    )

    # 執行幾步
    states_history = []
    for i in range(4):
        action_result, state, _ = app.step()
        states_history.append((i+1, action_result.name, state.get("value", 0)))
        console.print(f"  步驟 {i+1}: {action_result.name}, 值={state.get('value', 0)}")

    # 顯示狀態歷史
    console.print("\n[yellow]狀態歷史：[/yellow]")
    history_table = Table()
    history_table.add_column("步驟", style="cyan")
    history_table.add_column("動作", style="magenta")
    history_table.add_column("值", style="green")

    for step, action, value in states_history:
        history_table.add_row(str(step), action, str(value))

    console.print(history_table)

    console.print("\n[green]提示：在 Burr UI 中可以點擊任意步驟回到該狀態[/green]")


# ============================================================================
# 主函數
# ============================================================================

def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold green]Burr 追蹤調試 - 時間旅行與可視化[/bold green]",
        border_style="green"
    ))

    console.print("\n[bold]追蹤調試核心概念：[/bold]")
    console.print("1. [cyan]LocalTrackingClient[/cyan]: 本地追蹤")
    console.print("2. [cyan]Burr UI[/cyan]: 可視化工具")
    console.print("3. [cyan]時間旅行[/cyan]: 回到歷史狀態")
    console.print("4. [cyan]性能分析[/cyan]: 追蹤執行指標\n")

    # 運行示例
    basic_tracking_example()
    console.print("\n" + "="*60 + "\n")

    detailed_tracking_example()
    console.print("\n" + "="*60 + "\n")

    burr_ui_example()
    console.print("\n" + "="*60 + "\n")

    time_travel_debugging()

    # 總結
    console.print(Panel("""
[bold green]追蹤調試完成！[/bold green]

關鍵要點：
1. 使用 with_tracker() 啟用追蹤
2. Burr UI 提供強大的可視化
3. 時間旅行讓調試更簡單
4. 自動追蹤性能指標
5. 完整的狀態歷史記錄

啟動 Burr UI：
```bash
pip install "burr[start]"
burr
```

訪問：http://localhost:7241

追蹤的優勢：
- 完整的執行可見性
- 輕鬆重現問題
- 性能瓶頸識別
- 團隊協作調試

最佳實踐：
- 開發環境始終啟用追蹤
- 為重要操作添加元數據
- 定期清理舊追蹤數據
- 使用 UI 分析複雜流程

下一步：
- 查看 07_聊天應用.py 構建實際應用
- 查看 10_生產部署.py 了解生產配置
    """, title="總結", border_style="green"))


if __name__ == "__main__":
    main()

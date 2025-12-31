"""
Burr 快速開始 - 基本狀態機

這個示例展示如何：
1. 定義簡單的動作（Actions）
2. 創建狀態機應用
3. 執行狀態轉換
4. 查看狀態變化

Burr 使用狀態機模型來構建應用，每個動作都是狀態轉換的基本單位。
"""

from burr.core import action, State, ApplicationBuilder, default, expr
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


# ============================================================================
# 示例 1：最簡單的計數器
# ============================================================================

@action(reads=[], writes=["counter"])
def initialize_counter(state: State) -> State:
    """初始化計數器"""
    return state.update(counter=0)


@action(reads=["counter"], writes=["counter"])
def increment(state: State) -> State:
    """增加計數器"""
    current = state.get("counter", 0)
    return state.update(counter=current + 1)


@action(reads=["counter"], writes=["counter"])
def decrement(state: State) -> State:
    """減少計數器"""
    current = state.get("counter", 0)
    return state.update(counter=current - 1)


@action(reads=["counter"], writes=["result"])
def finish(state: State) -> State:
    """完成並保存結果"""
    final_count = state.get("counter", 0)
    return state.update(result=f"最終計數: {final_count}")


def simple_counter_example():
    """示例 1：簡單計數器"""
    console.print(Panel("[bold cyan]示例 1：簡單計數器[/bold cyan]"))

    # 構建應用
    app = (
        ApplicationBuilder()
        .with_actions(
            initialize_counter,
            increment,
            decrement,
            finish
        )
        .with_transitions(
            ("initialize_counter", "increment"),  # 初始化後增加
            ("increment", "increment", default),  # 默認繼續增加
            ("increment", "finish"),              # 可以完成
            ("decrement", "decrement", default),  # 默認繼續減少
            ("decrement", "finish"),              # 可以完成
        )
        .with_entrypoint("initialize_counter")
        .build()
    )

    console.print("\n[yellow]執行步驟：[/yellow]")

    # 執行步驟
    steps = [
        ("初始化", 1),
        ("增加計數", 3),
        ("完成", 1)
    ]

    for step_name, count in steps:
        console.print(f"\n[cyan]{step_name}[/cyan]")
        for i in range(count):
            action_result, state, _ = app.step()
            console.print(
                f"  步驟 {i+1}: 動作={action_result.name}, "
                f"計數器={state.get('counter', 'N/A')}"
            )

            # 如果是完成動作，顯示結果
            if action_result.name == "finish":
                console.print(f"  [green]{state['result']}[/green]")
                break

    return app


# ============================================================================
# 示例 2：帶條件的狀態機
# ============================================================================

@action(reads=["value"], writes=["value", "status"])
def check_value(state: State) -> State:
    """檢查值"""
    value = state.get("value", 0)
    status = "positive" if value > 0 else "negative" if value < 0 else "zero"
    return state.update(status=status)


@action(reads=["value"], writes=["value"])
def double_value(state: State) -> State:
    """值翻倍"""
    value = state.get("value", 0)
    return state.update(value=value * 2)


@action(reads=["value"], writes=["value"])
def negate_value(state: State) -> State:
    """值取反"""
    value = state.get("value", 0)
    return state.update(value=-value)


@action(reads=["value"], writes=["message"])
def complete(state: State) -> State:
    """完成"""
    value = state.get("value", 0)
    return state.update(message=f"處理完成，最終值: {value}")


def conditional_example():
    """示例 2：帶條件的狀態機"""
    console.print(Panel("[bold cyan]示例 2：帶條件的狀態機[/bold cyan]"))

    # 構建應用
    app = (
        ApplicationBuilder()
        .with_actions(
            check_value,
            double_value,
            negate_value,
            complete
        )
        .with_transitions(
            ("check_value", "double_value", expr("status == 'positive'")),
            ("check_value", "negate_value", expr("status == 'negative'")),
            ("check_value", "complete", expr("status == 'zero'")),
            ("double_value", "complete"),
            ("negate_value", "complete"),
        )
        .with_state(value=5)
        .with_entrypoint("check_value")
        .build()
    )

    console.print("\n[yellow]執行流程：[/yellow]")

    # 執行直到完成
    max_steps = 10
    for i in range(max_steps):
        action_result, state, _ = app.step()

        console.print(
            f"  步驟 {i+1}: 動作={action_result.name}, "
            f"值={state.get('value', 'N/A')}, "
            f"狀態={state.get('status', 'N/A')}"
        )

        # 如果完成，顯示消息並退出
        if action_result.name == "complete":
            console.print(f"  [green]{state.get('message')}[/green]")
            break

    return app


# ============================================================================
# 示例 3：迭代處理
# ============================================================================

@action(reads=[], writes=["items", "current_index", "results"])
def setup_items(state: State) -> State:
    """設置要處理的項目"""
    items = ["蘋果", "香蕉", "橘子", "葡萄", "西瓜"]
    return state.update(
        items=items,
        current_index=0,
        results=[]
    )


@action(reads=["items", "current_index"], writes=["current_index", "results"])
def process_item(state: State) -> State:
    """處理一個項目"""
    items = state["items"]
    index = state["current_index"]
    results = state["results"]

    # 處理當前項目
    current_item = items[index]
    processed = f"已處理: {current_item}"

    # 更新結果和索引
    return state.update(
        current_index=index + 1,
        results=results + [processed]
    )


@action(reads=["results"], writes=["summary"])
def summarize(state: State) -> State:
    """總結處理結果"""
    results = state["results"]
    summary = f"共處理 {len(results)} 個項目"
    return state.update(summary=summary)


def iteration_example():
    """示例 3：迭代處理"""
    console.print(Panel("[bold cyan]示例 3：迭代處理[/bold cyan]"))

    # 構建應用
    app = (
        ApplicationBuilder()
        .with_actions(
            setup_items,
            process_item,
            summarize
        )
        .with_transitions(
            ("setup_items", "process_item"),
            ("process_item", "process_item",
             expr("current_index < len(items)")),  # 繼續處理
            ("process_item", "summarize",
             expr("current_index >= len(items)")),  # 完成處理
        )
        .with_entrypoint("setup_items")
        .build()
    )

    console.print("\n[yellow]處理項目：[/yellow]")

    # 執行直到完成
    while True:
        action_result, state, _ = app.step()

        if action_result.name == "setup_items":
            items = state["items"]
            console.print(f"  待處理項目: {items}")

        elif action_result.name == "process_item":
            results = state["results"]
            console.print(f"  {results[-1]}")

        elif action_result.name == "summarize":
            summary = state["summary"]
            console.print(f"\n  [green]{summary}[/green]")
            break

    return app


# ============================================================================
# 示例 4：狀態追蹤
# ============================================================================

def state_tracking_example():
    """示例 4：狀態追蹤"""
    console.print(Panel("[bold cyan]示例 4：狀態追蹤[/bold cyan]"))

    # 創建一個簡單的應用
    app = (
        ApplicationBuilder()
        .with_actions(increment, decrement)
        .with_transitions(
            ("increment", "increment", expr("counter < 3")),
            ("increment", "decrement", expr("counter >= 3")),
            ("decrement", "decrement", default),
        )
        .with_state(counter=0)
        .with_entrypoint("increment")
        .build()
    )

    # 創建表格顯示狀態歷史
    table = Table(title="狀態轉換歷史")
    table.add_column("步驟", style="cyan")
    table.add_column("動作", style="magenta")
    table.add_column("計數器", style="green")
    table.add_column("狀態變化", style="yellow")

    previous_counter = None

    # 執行並追蹤
    for i in range(8):
        action_result, state, _ = app.step()
        current_counter = state["counter"]

        # 計算狀態變化
        if previous_counter is not None:
            change = current_counter - previous_counter
            change_str = f"+{change}" if change > 0 else str(change)
        else:
            change_str = "初始"

        table.add_row(
            str(i + 1),
            action_result.name,
            str(current_counter),
            change_str
        )

        previous_counter = current_counter

    console.print(table)

    return app


# ============================================================================
# 主函數
# ============================================================================

def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold green]Burr 快速開始 - 基本狀態機[/bold green]",
        border_style="green"
    ))

    console.print("\n[bold]Burr 核心概念：[/bold]")
    console.print("1. [cyan]State[/cyan]: 不可變的狀態容器")
    console.print("2. [cyan]Action[/cyan]: 狀態轉換的基本單位")
    console.print("3. [cyan]Transition[/cyan]: 動作之間的流轉規則")
    console.print("4. [cyan]Application[/cyan]: 狀態機的容器\n")

    # 運行示例
    simple_counter_example()
    console.print("\n" + "="*60 + "\n")

    conditional_example()
    console.print("\n" + "="*60 + "\n")

    iteration_example()
    console.print("\n" + "="*60 + "\n")

    state_tracking_example()

    # 總結
    console.print(Panel("""
[bold green]快速開始完成！[/bold green]

關鍵要點：
1. 使用 @action 裝飾器定義動作
2. 明確聲明 reads 和 writes 依賴
3. 使用 ApplicationBuilder 構建應用
4. 使用 with_transitions 定義狀態流轉
5. 使用 expr() 定義條件轉換

Burr 的優勢：
- 清晰的狀態機模型
- 類型安全的狀態管理
- 易於測試和調試
- 完整的執行追蹤

下一步：
- 查看 02_狀態定義.py 學習高級狀態管理
- 查看 03_動作鏈.py 了解動作組合
- 訪問 https://burr.dagworks.io/ 閱讀官方文檔
    """, title="總結", border_style="green"))


if __name__ == "__main__":
    main()

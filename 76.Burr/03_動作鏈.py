"""
Burr 動作鏈 - 動作組合與鏈式處理

這個示例展示如何：
1. 組合多個動作形成處理鏈
2. 使用 bind() 方法綁定參數
3. 創建可重用的動作模塊
4. 實現數據處理管道

動作鏈讓複雜的處理流程變得清晰和可維護。
"""

from burr.core import action, State, ApplicationBuilder, expr
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from typing import List, Dict
import re

console = Console()


# ============================================================================
# 示例 1：文本處理鏈
# ============================================================================

@action(reads=["text"], writes=["text"])
def to_lowercase(state: State) -> State:
    """轉換為小寫"""
    text = state["text"]
    return state.update(text=text.lower())


@action(reads=["text"], writes=["text"])
def remove_punctuation(state: State) -> State:
    """移除標點符號"""
    text = state["text"]
    # 移除標點，但保留中文字符
    cleaned = re.sub(r'[^\w\s\u4e00-\u9fff]', '', text)
    return state.update(text=cleaned)


@action(reads=["text"], writes=["text", "word_count"])
def count_words(state: State) -> State:
    """統計詞數"""
    text = state["text"]
    words = text.split()
    return state.update(word_count=len(words))


@action(reads=["text"], writes=["text"])
def trim_whitespace(state: State) -> State:
    """修剪空白字符"""
    text = state["text"]
    # 移除多餘空白
    cleaned = ' '.join(text.split())
    return state.update(text=cleaned)


@action(reads=["text", "word_count"], writes=["summary"])
def create_summary(state: State) -> State:
    """創建摘要"""
    text = state["text"]
    word_count = state["word_count"]
    summary = {
        "processed_text": text,
        "word_count": word_count,
        "char_count": len(text),
    }
    return state.update(summary=summary)


def text_processing_chain():
    """示例 1：文本處理鏈"""
    console.print(Panel("[bold cyan]示例 1：文本處理鏈[/bold cyan]"))

    # 測試文本
    original_text = "  Hello, World!  This is a TEST.  "

    console.print(f"\n[yellow]原始文本：[/yellow]'{original_text}'")

    # 構建處理鏈
    app = (
        ApplicationBuilder()
        .with_state(text=original_text)
        .with_actions(
            to_lowercase,
            remove_punctuation,
            trim_whitespace,
            count_words,
            create_summary
        )
        .with_transitions(
            ("to_lowercase", "remove_punctuation"),
            ("remove_punctuation", "trim_whitespace"),
            ("trim_whitespace", "count_words"),
            ("count_words", "create_summary"),
        )
        .with_entrypoint("to_lowercase")
        .build()
    )

    # 執行處理鏈
    console.print("\n[yellow]處理步驟：[/yellow]")

    steps = [
        "to_lowercase",
        "remove_punctuation",
        "trim_whitespace",
        "count_words",
        "create_summary"
    ]

    for step_name in steps:
        action_result, state, _ = app.step()
        console.print(f"  ✓ {step_name}")

        if step_name == "create_summary":
            summary = state["summary"]
            console.print(f"\n[green]處理結果：[/green]")
            console.print(f"  最終文本: '{summary['processed_text']}'")
            console.print(f"  詞數: {summary['word_count']}")
            console.print(f"  字符數: {summary['char_count']}")

    return app


# ============================================================================
# 示例 2：數據轉換鏈
# ============================================================================

@action(reads=["data"], writes=["data"])
def filter_positive(state: State) -> State:
    """過濾正數"""
    data = state["data"]
    filtered = [x for x in data if x > 0]
    return state.update(data=filtered)


@action(reads=["data"], writes=["data"])
def square_values(state: State) -> State:
    """平方值"""
    data = state["data"]
    squared = [x ** 2 for x in data]
    return state.update(data=squared)


@action(reads=["data"], writes=["data"])
def normalize(state: State) -> State:
    """歸一化（0-1 範圍）"""
    data = state["data"]
    if not data:
        return state

    min_val = min(data)
    max_val = max(data)

    if max_val == min_val:
        normalized = [0.5] * len(data)
    else:
        normalized = [(x - min_val) / (max_val - min_val) for x in data]

    return state.update(data=normalized)


@action(reads=["data"], writes=["statistics"])
def calculate_stats(state: State) -> State:
    """計算統計信息"""
    data = state["data"]

    if not data:
        stats = {"count": 0, "sum": 0, "mean": 0, "min": 0, "max": 0}
    else:
        stats = {
            "count": len(data),
            "sum": sum(data),
            "mean": sum(data) / len(data),
            "min": min(data),
            "max": max(data),
        }

    return state.update(statistics=stats)


def data_transformation_chain():
    """示例 2：數據轉換鏈"""
    console.print(Panel("[bold cyan]示例 2：數據轉換鏈[/bold cyan]"))

    # 測試數據
    original_data = [-2, 3, -1, 5, 0, 8, -4, 10]

    console.print(f"\n[yellow]原始數據：[/yellow]{original_data}")

    # 構建轉換鏈
    app = (
        ApplicationBuilder()
        .with_state(data=original_data.copy())
        .with_actions(
            filter_positive,
            square_values,
            normalize,
            calculate_stats
        )
        .with_transitions(
            ("filter_positive", "square_values"),
            ("square_values", "normalize"),
            ("normalize", "calculate_stats"),
        )
        .with_entrypoint("filter_positive")
        .build()
    )

    # 執行轉換
    console.print("\n[yellow]轉換步驟：[/yellow]")

    transformations = [
        ("filter_positive", "過濾正數"),
        ("square_values", "計算平方"),
        ("normalize", "歸一化"),
        ("calculate_stats", "統計分析"),
    ]

    for step_name, description in transformations:
        action_result, state, _ = app.step()
        console.print(f"  ✓ {description}")

        if step_name != "calculate_stats":
            console.print(f"    結果: {state['data']}")

    # 顯示最終統計
    stats = state["statistics"]
    console.print(f"\n[green]統計結果：[/green]")
    console.print(f"  數量: {stats['count']}")
    console.print(f"  總和: {stats['sum']:.4f}")
    console.print(f"  平均: {stats['mean']:.4f}")
    console.print(f"  最小: {stats['min']:.4f}")
    console.print(f"  最大: {stats['max']:.4f}")

    return app


# ============================================================================
# 示例 3：可配置的處理鏈
# ============================================================================

@action(reads=["items"], writes=["items", "log"])
def filter_items(state: State, condition: str) -> State:
    """根據條件過濾項目"""
    items = state["items"]
    log = state.get("log", [])

    # 簡單的條件評估
    if condition == "even":
        filtered = [x for x in items if x % 2 == 0]
        log.append(f"過濾偶數: {len(filtered)} 項")
    elif condition == "odd":
        filtered = [x for x in items if x % 2 != 0]
        log.append(f"過濾奇數: {len(filtered)} 項")
    elif condition == "gt5":
        filtered = [x for x in items if x > 5]
        log.append(f"過濾大於5: {len(filtered)} 項")
    else:
        filtered = items
        log.append("無過濾")

    return state.update(items=filtered, log=log)


@action(reads=["items"], writes=["items", "log"])
def transform_items(state: State, operation: str) -> State:
    """轉換項目"""
    items = state["items"]
    log = state.get("log", [])

    if operation == "double":
        transformed = [x * 2 for x in items]
        log.append("值翻倍")
    elif operation == "square":
        transformed = [x ** 2 for x in items]
        log.append("計算平方")
    elif operation == "negate":
        transformed = [-x for x in items]
        log.append("取負值")
    else:
        transformed = items
        log.append("無轉換")

    return state.update(items=transformed, log=log)


@action(reads=["items", "log"], writes=["result"])
def finalize_processing(state: State) -> State:
    """完成處理"""
    items = state["items"]
    log = state.get("log", [])

    result = {
        "final_items": items,
        "processing_log": log,
        "item_count": len(items)
    }

    return state.update(result=result)


def configurable_chain():
    """示例 3：可配置的處理鏈"""
    console.print(Panel("[bold cyan]示例 3：可配置的處理鏈[/bold cyan]"))

    # 定義不同的處理配置
    configs = [
        ("配置1: 偶數翻倍", "even", "double"),
        ("配置2: 大於5取平方", "gt5", "square"),
        ("配置3: 奇數取負", "odd", "negate"),
    ]

    original_items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    for config_name, filter_cond, transform_op in configs:
        console.print(f"\n[yellow]{config_name}[/yellow]")
        console.print(f"  原始數據: {original_items}")

        # 使用 bind 綁定參數
        app = (
            ApplicationBuilder()
            .with_state(items=original_items.copy(), log=[])
            .with_actions(
                filter_items.bind(condition=filter_cond),
                transform_items.bind(operation=transform_op),
                finalize_processing
            )
            .with_transitions(
                ("filter_items", "transform_items"),
                ("transform_items", "finalize_processing"),
            )
            .with_entrypoint("filter_items")
            .build()
        )

        # 執行處理鏈
        for _ in range(3):
            action_result, state, _ = app.step()

        result = state["result"]
        console.print(f"  處理日誌: {' -> '.join(result['processing_log'])}")
        console.print(f"  [green]最終結果: {result['final_items']}[/green]")


# ============================================================================
# 示例 4：動態鏈構建
# ============================================================================

@action(reads=["value"], writes=["value", "operations"])
def add_operation(state: State, amount: int, op_name: str) -> State:
    """執行加法操作"""
    value = state.get("value", 0)
    operations = state.get("operations", [])

    new_value = value + amount
    operations.append(f"{op_name}: {value} + {amount} = {new_value}")

    return state.update(value=new_value, operations=operations)


@action(reads=["value"], writes=["value", "operations"])
def multiply_operation(state: State, factor: int, op_name: str) -> State:
    """執行乘法操作"""
    value = state.get("value", 0)
    operations = state.get("operations", [])

    new_value = value * factor
    operations.append(f"{op_name}: {value} × {factor} = {new_value}")

    return state.update(value=new_value, operations=operations)


def dynamic_chain():
    """示例 4：動態鏈構建"""
    console.print(Panel("[bold cyan]示例 4：動態鏈構建[/bold cyan]"))

    # 定義操作序列
    operation_sequence = [
        ("add", 10, "初始化"),
        ("multiply", 2, "翻倍"),
        ("add", 5, "增加5"),
        ("multiply", 3, "乘以3"),
        ("add", -15, "減少15"),
    ]

    console.print("\n[yellow]構建動態處理鏈：[/yellow]")

    # 構建動作列表
    actions = []
    transitions = []

    for i, (op_type, value, name) in enumerate(operation_sequence):
        if op_type == "add":
            bound_action = add_operation.bind(amount=value, op_name=name)
        else:  # multiply
            bound_action = multiply_operation.bind(factor=value, op_name=name)

        actions.append(bound_action)

        # 添加轉換（如果不是最後一個操作）
        if i < len(operation_sequence) - 1:
            # 注意：這裡需要使用操作的實際名稱
            transitions.append((f"{op_type}_operation", f"{operation_sequence[i+1][0]}_operation"))

    # 構建應用
    app = (
        ApplicationBuilder()
        .with_state(value=0, operations=[])
        .with_actions(*actions)
        .with_entrypoint(f"{operation_sequence[0][0]}_operation")
        .build()
    )

    # 執行所有操作
    console.print("\n[yellow]執行操作：[/yellow]")

    with Progress() as progress:
        task = progress.add_task("[cyan]處理中...", total=len(operation_sequence))

        for _ in range(len(operation_sequence)):
            action_result, state, _ = app.step()
            progress.update(task, advance=1)

    # 顯示結果
    console.print("\n[green]操作歷史：[/green]")
    for op in state["operations"]:
        console.print(f"  • {op}")

    console.print(f"\n[green]最終值: {state['value']}[/green]")


# ============================================================================
# 主函數
# ============================================================================

def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold green]Burr 動作鏈 - 動作組合與鏈式處理[/bold green]",
        border_style="green"
    ))

    console.print("\n[bold]動作鏈核心概念：[/bold]")
    console.print("1. [cyan]組合性[/cyan]: 小動作組合成大功能")
    console.print("2. [cyan]可重用性[/cyan]: 動作可以在多處重用")
    console.print("3. [cyan]參數綁定[/cyan]: 使用 bind() 綁定參數")
    console.print("4. [cyan]動態構建[/cyan]: 根據需求動態構建處理鏈\n")

    # 運行示例
    text_processing_chain()
    console.print("\n" + "="*60 + "\n")

    data_transformation_chain()
    console.print("\n" + "="*60 + "\n")

    configurable_chain()
    console.print("\n" + "="*60 + "\n")

    dynamic_chain()

    # 總結
    console.print(Panel("""
[bold green]動作鏈完成！[/bold green]

關鍵要點：
1. 使用簡單動作組合複雜功能
2. bind() 方法綁定動作參數
3. 動作可以在不同配置中重用
4. 支持動態構建處理鏈
5. 每個動作保持單一職責

動作鏈的優勢：
- 代碼模塊化和可維護
- 易於測試單個動作
- 靈活的組合方式
- 清晰的數據流向

最佳實踐：
- 保持動作簡單和專注
- 使用有意義的動作名稱
- 明確聲明讀寫依賴
- 合理使用參數綁定
- 避免動作間的緊耦合

下一步：
- 查看 04_條件分支.py 學習條件路由
- 查看 08_Agent循環.py 了解循環處理
    """, title="總結", border_style="green"))


if __name__ == "__main__":
    main()

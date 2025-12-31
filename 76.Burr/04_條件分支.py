"""
Burr 條件分支 - 基於條件的動態路由

這個示例展示如何：
1. 使用 expr() 定義條件表達式
2. 實現複雜的分支邏輯
3. 創建決策樹
4. 動態路由到不同的處理路徑

條件分支讓狀態機能夠根據運行時狀態智能決策。
"""

from burr.core import action, State, ApplicationBuilder, expr, default
from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree
from typing import Dict
import random

console = Console()


# ============================================================================
# 示例 1：簡單條件分支
# ============================================================================

@action(reads=["age"], writes=["category"])
def categorize_age(state: State) -> State:
    """根據年齡分類"""
    age = state["age"]

    if age < 18:
        category = "minor"
    elif age < 65:
        category = "adult"
    else:
        category = "senior"

    return state.update(category=category)


@action(reads=["category"], writes=["message"])
def handle_minor(state: State) -> State:
    """處理未成年人"""
    return state.update(message="您是未成年人，需要家長監護")


@action(reads=["category"], writes=["message"])
def handle_adult(state: State) -> State:
    """處理成年人"""
    return state.update(message="您是成年人，享有完全權利")


@action(reads=["category"], writes=["message"])
def handle_senior(state: State) -> State:
    """處理老年人"""
    return state.update(message="您是老年人，享有優惠政策")


def simple_branch_example():
    """示例 1：簡單條件分支"""
    console.print(Panel("[bold cyan]示例 1：簡單條件分支[/bold cyan]"))

    test_ages = [10, 25, 70]

    for age in test_ages:
        console.print(f"\n[yellow]測試年齡: {age}[/yellow]")

        # 構建應用
        app = (
            ApplicationBuilder()
            .with_state(age=age)
            .with_actions(
                categorize_age,
                handle_minor,
                handle_adult,
                handle_senior
            )
            .with_transitions(
                ("categorize_age", "handle_minor", expr("category == 'minor'")),
                ("categorize_age", "handle_adult", expr("category == 'adult'")),
                ("categorize_age", "handle_senior", expr("category == 'senior'")),
            )
            .with_entrypoint("categorize_age")
            .build()
        )

        # 執行分類
        action_result, state, _ = app.step()
        console.print(f"  分類: {state['category']}")

        # 執行對應處理
        action_result, state, _ = app.step()
        console.print(f"  [green]{state['message']}[/green]")


# ============================================================================
# 示例 2：多條件決策樹
# ============================================================================

@action(reads=[], writes=["score", "attendance"])
def get_student_data(state: State, score: int, attendance: float) -> State:
    """獲取學生數據"""
    return state.update(score=score, attendance=attendance)


@action(reads=["score", "attendance"], writes=["decision"])
def evaluate_student(state: State) -> State:
    """評估學生表現"""
    score = state["score"]
    attendance = state["attendance"]

    # 決策邏輯
    if score >= 90 and attendance >= 0.95:
        decision = "excellent"
    elif score >= 80 and attendance >= 0.90:
        decision = "good"
    elif score >= 60 and attendance >= 0.80:
        decision = "pass"
    else:
        decision = "fail"

    return state.update(decision=decision)


@action(reads=["decision"], writes=["reward"])
def excellent_reward(state: State) -> State:
    """優秀獎勵"""
    return state.update(reward="獎學金 + 榮譽證書")


@action(reads=["decision"], writes=["reward"])
def good_reward(state: State) -> State:
    """良好獎勵"""
    return state.update(reward="榮譽證書")


@action(reads=["decision"], writes=["reward"])
def pass_reward(state: State) -> State:
    """及格獎勵"""
    return state.update(reward="通過證明")


@action(reads=["decision"], writes=["action_required"])
def fail_action(state: State) -> State:
    """不及格處理"""
    return state.update(action_required="需要補考或重修")


def decision_tree_example():
    """示例 2：多條件決策樹"""
    console.print(Panel("[bold cyan]示例 2：多條件決策樹[/bold cyan]"))

    # 測試案例
    test_cases = [
        ("學生A", 95, 0.98),
        ("學生B", 85, 0.92),
        ("學生C", 70, 0.85),
        ("學生D", 55, 0.75),
    ]

    for name, score, attendance in test_cases:
        console.print(f"\n[yellow]{name}[/yellow]")
        console.print(f"  成績: {score}, 出勤率: {attendance*100:.0f}%")

        # 構建應用
        app = (
            ApplicationBuilder()
            .with_actions(
                get_student_data.bind(score=score, attendance=attendance),
                evaluate_student,
                excellent_reward,
                good_reward,
                pass_reward,
                fail_action
            )
            .with_transitions(
                ("get_student_data", "evaluate_student"),
                ("evaluate_student", "excellent_reward", expr("decision == 'excellent'")),
                ("evaluate_student", "good_reward", expr("decision == 'good'")),
                ("evaluate_student", "pass_reward", expr("decision == 'pass'")),
                ("evaluate_student", "fail_action", expr("decision == 'fail'")),
            )
            .with_entrypoint("get_student_data")
            .build()
        )

        # 執行評估
        for _ in range(3):
            action_result, state, _ = app.step()

        # 顯示結果
        decision = state["decision"]
        if decision == "fail":
            console.print(f"  評價: {decision}")
            console.print(f"  [red]處理: {state['action_required']}[/red]")
        else:
            console.print(f"  評價: {decision}")
            console.print(f"  [green]獎勵: {state['reward']}[/green]")


# ============================================================================
# 示例 3：複雜分支與循環
# ============================================================================

@action(reads=[], writes=["attempts", "max_attempts", "success"])
def initialize_retry(state: State, max_attempts: int = 3) -> State:
    """初始化重試邏輯"""
    return state.update(
        attempts=0,
        max_attempts=max_attempts,
        success=False
    )


@action(reads=["attempts"], writes=["attempts", "success", "result"])
def attempt_operation(state: State) -> State:
    """嘗試執行操作"""
    attempts = state["attempts"] + 1

    # 模擬隨機成功/失敗（30% 成功率）
    success = random.random() < 0.3

    if success:
        result = f"操作在第 {attempts} 次嘗試時成功"
    else:
        result = f"第 {attempts} 次嘗試失敗"

    return state.update(
        attempts=attempts,
        success=success,
        result=result
    )


@action(reads=["result"], writes=["final_message"])
def handle_success(state: State) -> State:
    """處理成功情況"""
    result = state["result"]
    return state.update(final_message=f"✓ {result}")


@action(reads=["attempts", "max_attempts"], writes=["final_message"])
def handle_failure(state: State) -> State:
    """處理失敗情況"""
    attempts = state["attempts"]
    max_attempts = state["max_attempts"]
    return state.update(
        final_message=f"✗ 操作失敗，已達到最大重試次數 ({attempts}/{max_attempts})"
    )


def retry_logic_example():
    """示例 3：複雜分支與循環"""
    console.print(Panel("[bold cyan]示例 3：重試邏輯（分支 + 循環）[/bold cyan]"))

    # 設置隨機種子以便結果可重現（可選）
    random.seed(42)

    console.print("\n[yellow]執行帶重試的操作：[/yellow]")

    # 構建應用
    app = (
        ApplicationBuilder()
        .with_actions(
            initialize_retry.bind(max_attempts=5),
            attempt_operation,
            handle_success,
            handle_failure
        )
        .with_transitions(
            ("initialize_retry", "attempt_operation"),
            # 成功 -> 處理成功
            ("attempt_operation", "handle_success", expr("success == True")),
            # 失敗但未達上限 -> 繼續重試
            ("attempt_operation", "attempt_operation",
             expr("success == False and attempts < max_attempts")),
            # 失敗且達上限 -> 處理失敗
            ("attempt_operation", "handle_failure",
             expr("success == False and attempts >= max_attempts")),
        )
        .with_entrypoint("initialize_retry")
        .build()
    )

    # 執行操作
    max_steps = 10
    for i in range(max_steps):
        action_result, state, _ = app.step()

        if action_result.name == "attempt_operation":
            console.print(f"  {state['result']}")

        elif action_result.name in ["handle_success", "handle_failure"]:
            message = state["final_message"]
            if state.get("success", False):
                console.print(f"\n[green]{message}[/green]")
            else:
                console.print(f"\n[red]{message}[/red]")
            break


# ============================================================================
# 示例 4：狀態機可視化
# ============================================================================

def visualize_state_machine():
    """示例 4：狀態機可視化"""
    console.print(Panel("[bold cyan]示例 4：狀態機可視化[/bold cyan]"))

    # 創建決策樹可視化
    tree = Tree("[bold]學生評估決策樹[/bold]")

    # 根節點
    root = tree.add("[cyan]開始[/cyan]")

    # 第一層：獲取數據
    data_node = root.add("[yellow]獲取學生數據[/yellow]")

    # 第二層：評估
    eval_node = data_node.add("[yellow]評估表現[/yellow]")

    # 第三層：決策分支
    excellent = eval_node.add("[green]優秀 (score≥90 & attendance≥95%)[/green]")
    excellent.add("→ 獎學金 + 榮譽證書")

    good = eval_node.add("[green]良好 (score≥80 & attendance≥90%)[/green]")
    good.add("→ 榮譽證書")

    pass_node = eval_node.add("[yellow]及格 (score≥60 & attendance≥80%)[/yellow]")
    pass_node.add("→ 通過證明")

    fail = eval_node.add("[red]不及格[/red]")
    fail.add("→ 補考或重修")

    console.print("\n")
    console.print(tree)

    # 創建重試邏輯可視化
    console.print("\n")
    retry_tree = Tree("[bold]重試邏輯流程[/bold]")

    start = retry_tree.add("[cyan]初始化 (attempts=0)[/cyan]")
    attempt = start.add("[yellow]嘗試操作[/yellow]")

    success_branch = attempt.add("[green]成功?[/green]")
    success_branch.add("→ 處理成功 ✓")

    fail_branch = attempt.add("[red]失敗?[/red]")
    retry = fail_branch.add("[yellow]attempts < max?[/yellow]")
    retry.add("→ 繼續重試 ↺")
    max_reached = fail_branch.add("[red]達到上限?[/red]")
    max_reached.add("→ 處理失敗 ✗")

    console.print(retry_tree)


# ============================================================================
# 主函數
# ============================================================================

def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold green]Burr 條件分支 - 基於條件的動態路由[/bold green]",
        border_style="green"
    ))

    console.print("\n[bold]條件分支核心概念：[/bold]")
    console.print("1. [cyan]expr()[/cyan]: 定義條件表達式")
    console.print("2. [cyan]多路分支[/cyan]: 根據狀態選擇路徑")
    console.print("3. [cyan]循環控制[/cyan]: 條件循環與退出")
    console.print("4. [cyan]決策樹[/cyan]: 複雜的決策邏輯\n")

    # 運行示例
    simple_branch_example()
    console.print("\n" + "="*60 + "\n")

    decision_tree_example()
    console.print("\n" + "="*60 + "\n")

    retry_logic_example()
    console.print("\n" + "="*60 + "\n")

    visualize_state_machine()

    # 總結
    console.print(Panel("""
[bold green]條件分支完成！[/bold green]

關鍵要點：
1. 使用 expr() 定義條件表達式
2. 支持複雜的布爾邏輯
3. 可以訪問狀態中的任何值
4. 結合循環實現重試邏輯
5. 條件按順序評估，找到第一個匹配

條件表達式語法：
- 比較: ==, !=, <, >, <=, >=
- 邏輯: and, or, not
- 成員: in, not in
- 調用: len(), str(), int() 等

最佳實踐：
- 條件表達式保持簡單清晰
- 考慮所有可能的分支
- 使用 default 處理默認情況
- 避免重複的條件邏輯
- 為複雜決策添加註釋

常見模式：
- if-else: 二選一分支
- if-elif-else: 多選一分支
- 重試邏輯: 循環 + 退出條件
- 狀態機: 複雜的狀態轉換

下一步：
- 查看 05_持久化.py 學習狀態保存
- 查看 08_Agent循環.py 了解 Agent 決策
    """, title="總結", border_style="green"))


if __name__ == "__main__":
    main()

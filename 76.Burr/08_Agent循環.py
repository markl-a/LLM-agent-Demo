"""
Burr Agent 循環 - 實現思考-行動-觀察循環

這個示例展示如何：
1. 實現 ReAct 模式（Reasoning + Acting）
2. 工具調用循環
3. Agent 決策邏輯
4. 循環控制與退出條件

Burr 非常適合構建需要迭代決策的 Agent 系統。
"""

from burr.core import action, State, ApplicationBuilder, expr
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from typing import List, Dict, Any
import random

console = Console()


# ============================================================================
# 示例 1：簡單 Agent 循環
# ============================================================================

@action(reads=[], writes=["task", "max_iterations", "current_iteration"])
def initialize_agent(state: State, task: str, max_iterations: int = 5) -> State:
    """初始化 Agent"""
    return state.update(
        task=task,
        max_iterations=max_iterations,
        current_iteration=0,
        steps=[],
        completed=False
    )


@action(reads=["task", "steps"], writes=["thought", "current_iteration"])
def think(state: State) -> State:
    """思考步驟"""
    task = state["task"]
    steps = state["steps"]
    iteration = state["current_iteration"]

    # 簡單的思考邏輯
    if not steps:
        thought = f"我需要分析任務：{task}"
    elif len(steps) < 3:
        thought = f"繼續執行步驟 {len(steps) + 1}"
    else:
        thought = "任務即將完成，進行最後檢查"

    return state.update(
        thought=thought,
        current_iteration=iteration + 1
    )


@action(reads=["thought"], writes=["action_taken"])
def act(state: State) -> State:
    """執行動作"""
    thought = state["thought"]

    # 根據思考決定動作
    if "分析" in thought:
        action_taken = "分析任務需求"
    elif "步驟" in thought:
        action_taken = f"執行處理步驟"
    else:
        action_taken = "執行最終檢查"

    return state.update(action_taken=action_taken)


@action(reads=["action_taken"], writes=["observation", "steps"])
def observe(state: State) -> State:
    """觀察結果"""
    action_taken = state["action_taken"]
    steps = state["steps"]

    # 模擬觀察結果
    observation = f"完成：{action_taken}"

    # 記錄步驟
    steps.append({
        "thought": state["thought"],
        "action": action_taken,
        "observation": observation
    })

    return state.update(
        observation=observation,
        steps=steps
    )


@action(reads=["steps", "current_iteration", "max_iterations"], writes=["completed"])
def check_completion(state: State) -> State:
    """檢查是否完成"""
    steps = state["steps"]
    current_iteration = state["current_iteration"]
    max_iterations = state["max_iterations"]

    # 完成條件
    completed = len(steps) >= 3 or current_iteration >= max_iterations

    return state.update(completed=completed)


def simple_agent_example():
    """示例 1：簡單 Agent 循環"""
    console.print(Panel("[bold cyan]示例 1：簡單 Agent 循環[/bold cyan]"))

    # 構建 Agent
    app = (
        ApplicationBuilder()
        .with_actions(
            initialize_agent.bind(task="處理用戶請求", max_iterations=5),
            think,
            act,
            observe,
            check_completion
        )
        .with_transitions(
            ("initialize_agent", "think"),
            ("think", "act"),
            ("act", "observe"),
            ("observe", "check_completion"),
            ("check_completion", "think", expr("not completed")),
        )
        .with_entrypoint("initialize_agent")
        .build()
    )

    console.print("\n[yellow]Agent 執行循環：[/yellow]\n")

    # 執行 Agent 循環
    step_count = 0
    max_steps = 20  # 防止無限循環

    while step_count < max_steps:
        action_result, state, _ = app.step()
        step_count += 1

        # 顯示關鍵步驟
        if action_result.name == "think":
            console.print(f"[cyan]💭 思考：[/cyan]{state['thought']}")
        elif action_result.name == "act":
            console.print(f"[yellow]⚡ 行動：[/yellow]{state['action_taken']}")
        elif action_result.name == "observe":
            console.print(f"[green]👁  觀察：[/green]{state['observation']}")
            console.print()

        # 檢查是否完成
        if action_result.name == "check_completion":
            if state["completed"]:
                console.print("[green]✓ Agent 任務完成！[/green]")
                break

    # 顯示執行總結
    console.print(f"\n[yellow]執行總結：[/yellow]")
    console.print(f"  總迭代次數：{state['current_iteration']}")
    console.print(f"  執行步驟數：{len(state['steps'])}")


# ============================================================================
# 示例 2：帶工具的 Agent
# ============================================================================

# 定義工具
TOOLS = {
    "calculator": lambda x, y: x + y,
    "search": lambda query: f"搜索結果: {query}",
    "database": lambda table: f"從 {table} 獲取數據",
}


@action(reads=["query"], writes=["plan", "tool_calls"])
def plan_actions(state: State) -> State:
    """規劃動作"""
    query = state["query"]

    # 簡單的規劃邏輯
    if "計算" in query:
        plan = "使用計算器工具"
        tool_calls = ["calculator"]
    elif "搜索" in query:
        plan = "使用搜索工具"
        tool_calls = ["search"]
    elif "數據" in query:
        plan = "查詢數據庫"
        tool_calls = ["database"]
    else:
        plan = "使用通用處理"
        tool_calls = []

    return state.update(plan=plan, tool_calls=tool_calls)


@action(reads=["tool_calls"], writes=["tool_results"])
def execute_tools(state: State) -> State:
    """執行工具"""
    tool_calls = state["tool_calls"]
    results = []

    for tool_name in tool_calls:
        if tool_name == "calculator":
            result = TOOLS[tool_name](10, 5)
        elif tool_name == "search":
            result = TOOLS[tool_name]("Python 教程")
        elif tool_name == "database":
            result = TOOLS[tool_name]("users")
        else:
            result = "未知工具"

        results.append({
            "tool": tool_name,
            "result": result
        })

    return state.update(tool_results=results)


@action(reads=["tool_results", "query"], writes=["final_answer"])
def synthesize_answer(state: State) -> State:
    """綜合答案"""
    tool_results = state.get("tool_results", [])
    query = state["query"]

    if tool_results:
        answer = f"基於工具結果，回答 '{query}': " + str(tool_results[0]["result"])
    else:
        answer = f"直接回答 '{query}': 這是一個通用回答"

    return state.update(final_answer=answer)


def tool_agent_example():
    """示例 2：帶工具的 Agent"""
    console.print(Panel("[bold cyan]示例 2：帶工具的 Agent[/bold cyan]"))

    # 測試查詢
    queries = [
        "請幫我計算 10 + 5",
        "搜索 Python 教程",
        "獲取用戶數據",
    ]

    for query in queries:
        console.print(f"\n[yellow]查詢：[/yellow]{query}")

        # 構建 Agent
        app = (
            ApplicationBuilder()
            .with_state(query=query)
            .with_actions(
                plan_actions,
                execute_tools,
                synthesize_answer
            )
            .with_transitions(
                ("plan_actions", "execute_tools", expr("len(tool_calls) > 0")),
                ("plan_actions", "synthesize_answer", expr("len(tool_calls) == 0")),
                ("execute_tools", "synthesize_answer"),
            )
            .with_entrypoint("plan_actions")
            .build()
        )

        # 執行
        # 規劃
        action_result, state, _ = app.step()
        console.print(f"  [cyan]規劃：[/cyan]{state['plan']}")

        # 執行工具（如果需要）
        if state["tool_calls"]:
            action_result, state, _ = app.step()
            console.print(f"  [yellow]工具：[/yellow]{state['tool_calls']}")

        # 綜合答案
        action_result, state, _ = app.step()
        console.print(f"  [green]答案：[/green]{state['final_answer']}")


# ============================================================================
# 示例 3：ReAct 模式
# ============================================================================

@action(reads=["goal", "history"], writes=["reasoning", "history"])
def reason(state: State) -> State:
    """推理步驟"""
    goal = state["goal"]
    history = state.get("history", [])

    # 根據歷史和目標進行推理
    if not history:
        reasoning = f"開始分析目標：{goal}"
    elif len(history) < 3:
        reasoning = f"根據之前的結果，繼續探索"
    else:
        reasoning = "已收集足夠信息，準備總結"

    history.append({
        "step": "reason",
        "content": reasoning
    })

    return state.update(reasoning=reasoning, history=history)


@action(reads=["reasoning", "history"], writes=["action_plan", "history"])
def plan_react_action(state: State) -> State:
    """計劃行動"""
    reasoning = state["reasoning"]
    history = state["history"]

    # 根據推理計劃行動
    if "開始" in reasoning:
        action_plan = "收集初始信息"
    elif "繼續" in reasoning:
        action_plan = "深入分析"
    else:
        action_plan = "整理結論"

    history.append({
        "step": "act",
        "content": action_plan
    })

    return state.update(action_plan=action_plan, history=history)


@action(reads=["action_plan", "history"], writes=["result", "history"])
def execute_react_action(state: State) -> State:
    """執行並觀察"""
    action_plan = state["action_plan"]
    history = state["history"]

    # 模擬執行結果
    result = f"執行 '{action_plan}' 的結果"

    history.append({
        "step": "observe",
        "content": result
    })

    return state.update(result=result, history=history)


@action(reads=["history"], writes=["should_continue"])
def decide_next(state: State) -> State:
    """決定是否繼續"""
    history = state["history"]

    # 計算 reason 步驟數
    reason_steps = len([h for h in history if h["step"] == "reason"])

    should_continue = reason_steps < 3

    return state.update(should_continue=should_continue)


def react_pattern_example():
    """示例 3：ReAct 模式"""
    console.print(Panel("[bold cyan]示例 3：ReAct 模式[/bold cyan]"))

    # 構建 ReAct Agent
    app = (
        ApplicationBuilder()
        .with_state(
            goal="分析用戶行為模式",
            history=[],
            should_continue=True
        )
        .with_actions(
            reason,
            plan_react_action,
            execute_react_action,
            decide_next
        )
        .with_transitions(
            ("reason", "plan_react_action"),
            ("plan_react_action", "execute_react_action"),
            ("execute_react_action", "decide_next"),
            ("decide_next", "reason", expr("should_continue")),
        )
        .with_entrypoint("reason")
        .build()
    )

    console.print("\n[yellow]ReAct 循環執行：[/yellow]\n")

    # 執行 ReAct 循環
    cycle_count = 0
    while True:
        action_result, state, _ = app.step()

        if action_result.name == "reason":
            cycle_count += 1
            console.print(f"[bold cyan]循環 {cycle_count}[/bold cyan]")
            console.print(f"  推理：{state['reasoning']}")

        elif action_result.name == "plan_react_action":
            console.print(f"  行動：{state['action_plan']}")

        elif action_result.name == "execute_react_action":
            console.print(f"  觀察：{state['result']}")

        elif action_result.name == "decide_next":
            if not state["should_continue"]:
                console.print("\n[green]✓ ReAct 循環完成[/green]")
                break
            console.print()

    # 顯示完整歷史
    console.print("\n[yellow]完整執行歷史：[/yellow]")
    table = Table()
    table.add_column("步驟", style="cyan")
    table.add_column("類型", style="magenta")
    table.add_column("內容", style="green")

    for i, item in enumerate(state["history"], 1):
        table.add_row(str(i), item["step"], item["content"])

    console.print(table)


# ============================================================================
# 示例 4：Agent 循環控制
# ============================================================================

def agent_loop_control():
    """示例 4：Agent 循環控制"""
    console.print(Panel("[bold cyan]示例 4：Agent 循環控制[/bold cyan]"))

    console.print("""
[yellow]Agent 循環控制策略：[/yellow]

1. [cyan]最大迭代次數[/cyan]
   - 防止無限循環
   - 設置合理的上限
   - 超時保護

2. [cyan]目標完成檢測[/cyan]
   - 檢查任務是否達成
   - 驗證結果質量
   - 確認用戶滿意度

3. [cyan]錯誤處理[/cyan]
   - 捕獲和記錄錯誤
   - 實現重試邏輯
   - 優雅降級

4. [cyan]資源限制[/cyan]
   - 控制 API 調用次數
   - 限制計算資源
   - 管理成本

[yellow]循環退出條件示例：[/yellow]
    """)

    exit_conditions = '''
# 1. 迭代次數限制
expr("current_iteration >= max_iterations")

# 2. 目標達成
expr("goal_achieved == True")

# 3. 用戶確認
expr("user_confirmed == True")

# 4. 錯誤次數過多
expr("error_count > max_errors")

# 5. 超時
expr("elapsed_time > timeout")

# 6. 組合條件
expr("goal_achieved or current_iteration >= max_iterations")
    '''

    console.print(Panel(exit_conditions, border_style="blue", title="退出條件"))


# ============================================================================
# 主函數
# ============================================================================

def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold green]Burr Agent 循環 - 思考-行動-觀察[/bold green]",
        border_style="green"
    ))

    console.print("\n[bold]Agent 循環核心概念：[/bold]")
    console.print("1. [cyan]Think-Act-Observe[/cyan]: 經典循環模式")
    console.print("2. [cyan]ReAct[/cyan]: 推理與行動結合")
    console.print("3. [cyan]工具調用[/cyan]: 集成外部工具")
    console.print("4. [cyan]循環控制[/cyan]: 退出條件管理\n")

    # 運行示例
    simple_agent_example()
    console.print("\n" + "="*60 + "\n")

    tool_agent_example()
    console.print("\n" + "="*60 + "\n")

    react_pattern_example()
    console.print("\n" + "="*60 + "\n")

    agent_loop_control()

    # 總結
    console.print(Panel("""
[bold green]Agent 循環完成！[/bold green]

關鍵要點：
1. 使用狀態機實現 Agent 循環
2. 清晰的思考-行動-觀察結構
3. 支持工具集成
4. 靈活的循環控制
5. 完整的執行追蹤

Agent 模式：
- Simple Loop: 基本迭代
- ReAct: 推理 + 行動
- Tool-using: 工具調用
- Multi-agent: 多 Agent 協作

循環控制要點：
- 設置最大迭代次數
- 定義明確的退出條件
- 實現錯誤處理
- 追蹤執行歷史
- 資源使用監控

最佳實踐：
- 保持循環邏輯簡單
- 記錄每個循環的狀態
- 實現超時保護
- 處理異常情況
- 提供調試信息

下一步：
- 查看 09_並行執行.py 優化性能
- 查看 10_生產部署.py 部署 Agent
    """, title="總結", border_style="green"))


if __name__ == "__main__":
    main()

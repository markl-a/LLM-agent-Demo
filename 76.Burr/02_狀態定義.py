"""
Burr 狀態定義 - 高級狀態管理

這個示例展示如何：
1. 使用 Pydantic 模型定義類型化狀態
2. 管理複雜的嵌套狀態
3. 狀態驗證和轉換
4. 狀態的不可變性

Burr 的狀態是不可變的，每次更新都會創建新的狀態對象。
"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from burr.core import action, State, ApplicationBuilder, expr
from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree
import json

console = Console()


# ============================================================================
# 示例 1：使用 Pydantic 模型
# ============================================================================

class UserProfile(BaseModel):
    """用戶資料模型"""
    name: str
    age: int = Field(gt=0, lt=150)
    email: str
    interests: List[str] = Field(default_factory=list)


class TaskItem(BaseModel):
    """任務項模型"""
    id: int
    title: str
    completed: bool = False
    priority: str = "medium"  # low, medium, high


@action(reads=[], writes=["user"])
def create_user(state: State, name: str, age: int, email: str) -> State:
    """創建用戶"""
    user = UserProfile(name=name, age=age, email=email)
    return state.update(user=user.model_dump())


@action(reads=["user"], writes=["user"])
def add_interest(state: State, interest: str) -> State:
    """添加興趣"""
    user_dict = state["user"]
    user = UserProfile(**user_dict)

    # 更新興趣列表
    if interest not in user.interests:
        user.interests.append(interest)

    return state.update(user=user.model_dump())


@action(reads=["user"], writes=["profile_summary"])
def summarize_profile(state: State) -> State:
    """總結用戶資料"""
    user_dict = state["user"]
    user = UserProfile(**user_dict)

    summary = (
        f"{user.name} ({user.age}歲) - {user.email}\n"
        f"興趣: {', '.join(user.interests) if user.interests else '無'}"
    )

    return state.update(profile_summary=summary)


def pydantic_model_example():
    """示例 1：使用 Pydantic 模型"""
    console.print(Panel("[bold cyan]示例 1：使用 Pydantic 模型[/bold cyan]"))

    # 構建應用
    app = (
        ApplicationBuilder()
        .with_actions(
            create_user.bind(name="張三", age=25, email="zhang@example.com"),
            add_interest.bind(interest="編程"),
            summarize_profile
        )
        .with_transitions(
            ("create_user", "add_interest"),
            ("add_interest", "add_interest"),
            ("add_interest", "summarize_profile")
        )
        .with_entrypoint("create_user")
        .build()
    )

    console.print("\n[yellow]創建和更新用戶資料：[/yellow]")

    # 創建用戶
    action_result, state, _ = app.step()
    console.print(f"✓ 用戶已創建: {state['user']['name']}")

    # 添加多個興趣
    interests = ["編程", "閱讀", "旅行"]
    for interest in interests:
        # 綁定新的興趣值
        action_result, state, _ = app.step()
        if action_result.name == "add_interest":
            console.print(f"✓ 添加興趣: {interest}")

    # 總結
    action_result, state, _ = app.step()
    console.print(f"\n[green]資料總結：[/green]")
    console.print(state["profile_summary"])

    return app


# ============================================================================
# 示例 2：複雜嵌套狀態
# ============================================================================

class ProjectState(BaseModel):
    """專案狀態模型"""
    name: str
    tasks: List[TaskItem] = Field(default_factory=list)
    completed_count: int = 0
    total_count: int = 0


@action(reads=[], writes=["project"])
def initialize_project(state: State, project_name: str) -> State:
    """初始化專案"""
    project = ProjectState(name=project_name)
    return state.update(project=project.model_dump())


@action(reads=["project"], writes=["project"])
def add_task(state: State, task_id: int, title: str, priority: str = "medium") -> State:
    """添加任務"""
    project_dict = state["project"]
    project = ProjectState(**project_dict)

    # 創建新任務
    task = TaskItem(id=task_id, title=title, priority=priority)
    project.tasks.append(task)
    project.total_count = len(project.tasks)

    return state.update(project=project.model_dump())


@action(reads=["project"], writes=["project"])
def complete_task(state: State, task_id: int) -> State:
    """完成任務"""
    project_dict = state["project"]
    project = ProjectState(**project_dict)

    # 找到並完成任務
    for task in project.tasks:
        if task.id == task_id and not task.completed:
            task.completed = True
            project.completed_count += 1
            break

    return state.update(project=project.model_dump())


@action(reads=["project"], writes=["project_status"])
def get_project_status(state: State) -> State:
    """獲取專案狀態"""
    project_dict = state["project"]
    project = ProjectState(**project_dict)

    status = {
        "name": project.name,
        "total": project.total_count,
        "completed": project.completed_count,
        "pending": project.total_count - project.completed_count,
        "progress": (
            f"{project.completed_count}/{project.total_count} "
            f"({project.completed_count/project.total_count*100:.0f}%)"
            if project.total_count > 0 else "0/0 (0%)"
        )
    }

    return state.update(project_status=status)


def nested_state_example():
    """示例 2：複雜嵌套狀態"""
    console.print(Panel("[bold cyan]示例 2：複雜嵌套狀態[/bold cyan]"))

    # 初始化專案
    app = (
        ApplicationBuilder()
        .with_actions(
            initialize_project.bind(project_name="AI Agent 開發"),
            add_task,
            complete_task,
            get_project_status
        )
        .with_entrypoint("initialize_project")
        .build()
    )

    # 初始化
    console.print("\n[yellow]初始化專案...[/yellow]")
    action_result, state, _ = app.step()
    console.print(f"✓ 專案已創建: {state['project']['name']}")

    # 添加任務
    console.print("\n[yellow]添加任務...[/yellow]")
    tasks = [
        (1, "設計架構", "high"),
        (2, "實現核心功能", "high"),
        (3, "編寫測試", "medium"),
        (4, "編寫文檔", "low")
    ]

    for task_id, title, priority in tasks:
        # 需要重新構建 action 並綁定參數
        bound_action = add_task.bind(task_id=task_id, title=title, priority=priority)
        app = app.with_actions(bound_action, complete_task, get_project_status).build()
        action_result, state, _ = app.step()
        console.print(f"  ✓ {title} (優先級: {priority})")

    # 完成一些任務
    console.print("\n[yellow]完成任務...[/yellow]")
    for task_id in [1, 3]:
        bound_action = complete_task.bind(task_id=task_id)
        app = app.with_actions(add_task, bound_action, get_project_status).build()
        action_result, state, _ = app.step()

        # 找到任務標題
        project = ProjectState(**state["project"])
        task = next((t for t in project.tasks if t.id == task_id), None)
        if task:
            console.print(f"  ✓ 已完成: {task.title}")

    # 獲取狀態
    console.print("\n[yellow]專案狀態：[/yellow]")
    action_result, state, _ = app.step()
    status = state["project_status"]

    console.print(f"  專案名稱: {status['name']}")
    console.print(f"  總任務數: {status['total']}")
    console.print(f"  已完成: {status['completed']}")
    console.print(f"  待完成: {status['pending']}")
    console.print(f"  [green]進度: {status['progress']}[/green]")

    return app


# ============================================================================
# 示例 3：狀態驗證
# ============================================================================

class ValidatedData(BaseModel):
    """經過驗證的數據"""
    username: str = Field(min_length=3, max_length=20)
    password: str = Field(min_length=8)
    age: int = Field(ge=18, le=100)


@action(reads=[], writes=["validation_result", "data"])
def validate_input(
    state: State,
    username: str,
    password: str,
    age: int
) -> State:
    """驗證輸入數據"""
    try:
        # 嘗試創建模型（會自動驗證）
        data = ValidatedData(username=username, password=password, age=age)
        return state.update(
            validation_result="success",
            data=data.model_dump(),
            error=None
        )
    except Exception as e:
        return state.update(
            validation_result="failed",
            data=None,
            error=str(e)
        )


@action(reads=["data"], writes=["message"])
def process_valid_data(state: State) -> State:
    """處理有效數據"""
    data = ValidatedData(**state["data"])
    message = f"歡迎 {data.username}！您的帳號已創建。"
    return state.update(message=message)


@action(reads=["error"], writes=["message"])
def handle_invalid_data(state: State) -> State:
    """處理無效數據"""
    error = state["error"]
    message = f"驗證失敗: {error}"
    return state.update(message=message)


def validation_example():
    """示例 3：狀態驗證"""
    console.print(Panel("[bold cyan]示例 3：狀態驗證[/bold cyan]"))

    test_cases = [
        ("有效數據", "john_doe", "secure123456", 25),
        ("用戶名太短", "jo", "secure123456", 25),
        ("密碼太短", "john_doe", "short", 25),
        ("年齡不符", "john_doe", "secure123456", 15),
    ]

    for test_name, username, password, age in test_cases:
        console.print(f"\n[yellow]測試: {test_name}[/yellow]")
        console.print(f"  輸入: username={username}, age={age}")

        # 構建應用
        app = (
            ApplicationBuilder()
            .with_actions(
                validate_input.bind(
                    username=username,
                    password=password,
                    age=age
                ),
                process_valid_data,
                handle_invalid_data
            )
            .with_transitions(
                ("validate_input", "process_valid_data",
                 expr("validation_result == 'success'")),
                ("validate_input", "handle_invalid_data",
                 expr("validation_result == 'failed'")),
            )
            .with_entrypoint("validate_input")
            .build()
        )

        # 執行驗證
        action_result, state, _ = app.step()

        # 處理結果
        action_result, state, _ = app.step()
        message = state.get("message", "")

        if state.get("validation_result") == "success":
            console.print(f"  [green]✓ {message}[/green]")
        else:
            console.print(f"  [red]✗ {message}[/red]")


# ============================================================================
# 示例 4：狀態可視化
# ============================================================================

def visualize_state_example():
    """示例 4：狀態可視化"""
    console.print(Panel("[bold cyan]示例 4：狀態可視化[/bold cyan]"))

    # 創建一個複雜的狀態
    app = (
        ApplicationBuilder()
        .with_actions(
            initialize_project.bind(project_name="演示專案"),
            add_task.bind(task_id=1, title="任務1", priority="high")
        )
        .with_entrypoint("initialize_project")
        .build()
    )

    # 執行初始化和添加任務
    action_result, state, _ = app.step()  # 初始化
    action_result, state, _ = app.step()  # 添加任務

    # 創建樹形視圖
    tree = Tree("[bold]狀態結構[/bold]")

    def add_to_tree(parent, data, name=""):
        """遞歸添加到樹"""
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    branch = parent.add(f"[cyan]{key}[/cyan]")
                    add_to_tree(branch, value, key)
                else:
                    parent.add(f"[yellow]{key}[/yellow]: {value}")
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    branch = parent.add(f"[cyan][{i}][/cyan]")
                    add_to_tree(branch, item, f"[{i}]")
                else:
                    parent.add(f"[{i}]: {item}")

    # 添加狀態到樹
    state_dict = dict(state._state)  # 獲取內部狀態
    add_to_tree(tree, state_dict)

    console.print("\n[yellow]當前狀態結構：[/yellow]")
    console.print(tree)

    # 也可以用 JSON 格式顯示
    console.print("\n[yellow]JSON 格式：[/yellow]")
    console.print(Panel(
        json.dumps(state_dict, indent=2, ensure_ascii=False),
        title="狀態 JSON",
        border_style="blue"
    ))


# ============================================================================
# 主函數
# ============================================================================

def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold green]Burr 狀態定義 - 高級狀態管理[/bold green]",
        border_style="green"
    ))

    console.print("\n[bold]狀態管理核心概念：[/bold]")
    console.print("1. [cyan]不可變性[/cyan]: 狀態更新創建新對象")
    console.print("2. [cyan]類型安全[/cyan]: 使用 Pydantic 模型驗證")
    console.print("3. [cyan]可序列化[/cyan]: 狀態可以輕鬆序列化")
    console.print("4. [cyan]可追蹤[/cyan]: 完整的狀態變更歷史\n")

    # 運行示例
    pydantic_model_example()
    console.print("\n" + "="*60 + "\n")

    nested_state_example()
    console.print("\n" + "="*60 + "\n")

    validation_example()
    console.print("\n" + "="*60 + "\n")

    visualize_state_example()

    # 總結
    console.print(Panel("""
[bold green]狀態管理完成！[/bold green]

關鍵要點：
1. 使用 Pydantic 模型定義結構化狀態
2. 狀態是不可變的，每次更新創建新對象
3. 自動驗證確保數據完整性
4. 支持複雜的嵌套結構
5. 狀態可以輕鬆序列化和持久化

最佳實踐：
- 為複雜數據定義 Pydantic 模型
- 保持狀態結構扁平化
- 使用有意義的鍵名
- 添加適當的驗證規則
- 避免在狀態中存儲不可序列化的對象

下一步：
- 查看 03_動作鏈.py 學習動作組合
- 查看 05_持久化.py 了解狀態持久化
    """, title="總結", border_style="green"))


if __name__ == "__main__":
    main()

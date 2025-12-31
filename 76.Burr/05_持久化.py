"""
Burr 持久化 - 狀態保存與恢復

這個示例展示如何：
1. 持久化應用狀態
2. 從持久化狀態恢復
3. 實現檢查點機制
4. 處理狀態遷移

持久化讓應用可以在崩潰後恢復，支持長時間運行的任務。
"""

from burr.core import action, State, ApplicationBuilder, expr
from burr.core.persistence import SQLLitePersister, BaseStatePersister
from rich.console import Console
from rich.panel import Panel
from pathlib import Path
import json
import time
from typing import Dict, Any

console = Console()


# ============================================================================
# 示例 1：基本持久化
# ============================================================================

@action(reads=["counter"], writes=["counter", "history"])
def increment_with_history(state: State) -> State:
    """增加計數器並記錄歷史"""
    counter = state.get("counter", 0)
    history = state.get("history", [])

    new_counter = counter + 1
    history.append({"step": len(history) + 1, "value": new_counter})

    return state.update(counter=new_counter, history=history)


@action(reads=["counter"], writes=["counter", "history"])
def decrement_with_history(state: State) -> State:
    """減少計數器並記錄歷史"""
    counter = state.get("counter", 0)
    history = state.get("history", [])

    new_counter = counter - 1
    history.append({"step": len(history) + 1, "value": new_counter})

    return state.update(counter=new_counter, history=history)


def basic_persistence_example():
    """示例 1：基本持久化"""
    console.print(Panel("[bold cyan]示例 1：基本持久化[/bold cyan]"))

    # 設置持久化路徑
    db_path = "/tmp/burr_demo.db"
    app_id = "counter_app"

    console.print(f"\n[yellow]持久化路徑：{db_path}[/yellow]")

    # 創建持久化器
    persister = SQLLitePersister(db_path=db_path, table_name="burr_state")

    # 構建應用（啟用持久化）
    app = (
        ApplicationBuilder()
        .with_state(counter=0, history=[])
        .with_actions(increment_with_history, decrement_with_history)
        .with_transitions(
            ("increment_with_history", "increment_with_history", expr("counter < 5")),
            ("increment_with_history", "decrement_with_history", expr("counter >= 5")),
            ("decrement_with_history", "decrement_with_history", default=True),
        )
        .with_entrypoint("increment_with_history")
        .with_state_persister(persister)
        .with_identifiers(app_id=app_id)
        .build()
    )

    console.print("\n[yellow]執行操作（每步都會持久化）：[/yellow]")

    # 執行幾步
    for i in range(8):
        action_result, state, _ = app.step()
        counter = state["counter"]
        console.print(f"  步驟 {i+1}: 動作={action_result.name}, 計數器={counter}")

        # 模擬崩潰（在第5步停止）
        if i == 4:
            console.print("\n[red]⚠ 模擬應用崩潰...[/red]")
            break

    console.print("\n[yellow]從持久化狀態恢復：[/yellow]")

    # 從持久化狀態恢復
    recovered_app = (
        ApplicationBuilder()
        .with_actions(increment_with_history, decrement_with_history)
        .with_transitions(
            ("increment_with_history", "increment_with_history", expr("counter < 5")),
            ("increment_with_history", "decrement_with_history", expr("counter >= 5")),
            ("decrement_with_history", "decrement_with_history", default=True),
        )
        .with_state_persister(persister)
        .with_identifiers(app_id=app_id)
        .initialize_from(
            persister,
            resume_at_next_action=True,
            default_entrypoint="increment_with_history"
        )
        .build()
    )

    # 獲取恢復的狀態
    current_state = recovered_app.state
    console.print(f"[green]✓ 已恢復狀態：計數器={current_state['counter']}[/green]")
    console.print(f"[green]✓ 歷史記錄數：{len(current_state['history'])}[/green]")

    # 繼續執行
    console.print("\n[yellow]繼續執行：[/yellow]")
    for i in range(5):
        action_result, state, _ = recovered_app.step()
        counter = state["counter"]
        console.print(f"  步驟 {i+1}: 動作={action_result.name}, 計數器={counter}")

    # 清理
    Path(db_path).unlink(missing_ok=True)


# ============================================================================
# 示例 2：自定義持久化後端
# ============================================================================

class JSONFilePersister(BaseStatePersister):
    """JSON 文件持久化器"""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def save(
        self,
        partition_key: str,
        app_id: str,
        sequence_id: int,
        position: str,
        state: State,
        **kwargs
    ) -> None:
        """保存狀態到 JSON 文件"""
        data = {
            "partition_key": partition_key,
            "app_id": app_id,
            "sequence_id": sequence_id,
            "position": position,
            "state": dict(state._state),
            "timestamp": time.time()
        }

        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load(
        self,
        partition_key: str,
        app_id: str,
        sequence_id: int = None,
        **kwargs
    ) -> Dict[str, Any]:
        """從 JSON 文件加載狀態"""
        if not self.file_path.exists():
            return {}

        with open(self.file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return {
            "state": State(data["state"]),
            "position": data["position"],
            "sequence_id": data["sequence_id"]
        }


@action(reads=["task_name"], writes=["task_name", "status", "progress"])
def start_task(state: State, task_name: str) -> State:
    """開始任務"""
    return state.update(
        task_name=task_name,
        status="running",
        progress=0
    )


@action(reads=["progress"], writes=["progress"])
def process_task(state: State) -> State:
    """處理任務"""
    progress = state.get("progress", 0)
    return state.update(progress=progress + 25)


@action(reads=["task_name", "progress"], writes=["status", "result"])
def complete_task(state: State) -> State:
    """完成任務"""
    task_name = state["task_name"]
    return state.update(
        status="completed",
        result=f"任務 '{task_name}' 已完成"
    )


def custom_persister_example():
    """示例 2：自定義持久化後端"""
    console.print(Panel("[bold cyan]示例 2：自定義 JSON 持久化[/bold cyan]"))

    # 使用自定義持久化器
    json_path = "/tmp/burr_task_state.json"
    persister = JSONFilePersister(json_path)

    console.print(f"\n[yellow]持久化到：{json_path}[/yellow]")

    # 構建應用
    app = (
        ApplicationBuilder()
        .with_actions(
            start_task.bind(task_name="數據處理"),
            process_task,
            complete_task
        )
        .with_transitions(
            ("start_task", "process_task"),
            ("process_task", "process_task", expr("progress < 100")),
            ("process_task", "complete_task", expr("progress >= 100")),
        )
        .with_entrypoint("start_task")
        .with_state_persister(persister)
        .with_identifiers(app_id="task_processor")
        .build()
    )

    # 執行一半
    console.print("\n[yellow]執行任務（部分）：[/yellow]")
    for i in range(3):
        action_result, state, _ = app.step()
        console.print(
            f"  步驟 {i+1}: 動作={action_result.name}, "
            f"進度={state.get('progress', 0)}%"
        )

    # 顯示保存的 JSON
    console.print("\n[yellow]保存的狀態（JSON）：[/yellow]")
    with open(json_path, 'r') as f:
        saved_data = json.load(f)
        console.print(Panel(
            json.dumps(saved_data, indent=2, ensure_ascii=False),
            border_style="blue"
        ))

    # 清理
    Path(json_path).unlink(missing_ok=True)


# ============================================================================
# 示例 3：檢查點機制
# ============================================================================

@action(reads=["data"], writes=["data", "checkpoints"])
def process_batch(state: State, batch_id: int) -> State:
    """處理批次"""
    data = state.get("data", [])
    checkpoints = state.get("checkpoints", [])

    # 模擬處理
    processed_item = f"batch_{batch_id}_processed"
    data.append(processed_item)

    # 每5個批次創建檢查點
    if batch_id % 5 == 0:
        checkpoints.append({
            "batch_id": batch_id,
            "data_count": len(data)
        })

    return state.update(data=data, checkpoints=checkpoints)


def checkpoint_example():
    """示例 3：檢查點機制"""
    console.print(Panel("[bold cyan]示例 3：檢查點機制[/bold cyan]"))

    db_path = "/tmp/burr_checkpoint.db"
    persister = SQLLitePersister(db_path=db_path, table_name="checkpoints")

    console.print("\n[yellow]執行批處理（每5個批次創建檢查點）：[/yellow]")

    # 構建應用
    app = (
        ApplicationBuilder()
        .with_state(
            data=[],
            checkpoints=[],
            batch_id=1,
            total_batches=15
        )
        .with_actions(process_batch)
        .with_transitions(
            ("process_batch", "process_batch", expr("batch_id < total_batches")),
        )
        .with_entrypoint("process_batch")
        .with_state_persister(persister)
        .with_identifiers(app_id="batch_processor")
        .build()
    )

    # 執行所有批次
    for i in range(15):
        # 綁定批次 ID
        action_result, state, _ = app.step()

        batch_id = i + 1
        checkpoints = state.get("checkpoints", [])

        if checkpoints and checkpoints[-1]["batch_id"] == batch_id:
            console.print(
                f"  [green]✓ 檢查點 {len(checkpoints)}: "
                f"批次 {batch_id}, 已處理 {len(state['data'])} 項[/green]"
            )
        else:
            console.print(f"  批次 {batch_id} 已處理")

        # 更新批次 ID
        app = app.with_state(batch_id=batch_id + 1).build()

    console.print(f"\n[green]✓ 所有批次完成，共創建 {len(state['checkpoints'])} 個檢查點[/green]")

    # 清理
    Path(db_path).unlink(missing_ok=True)


# ============================================================================
# 示例 4：狀態遷移
# ============================================================================

def state_migration_example():
    """示例 4：狀態遷移"""
    console.print(Panel("[bold cyan]示例 4：狀態遷移[/bold cyan]"))

    console.print("""
[yellow]狀態遷移策略：[/yellow]

1. [cyan]添加字段[/cyan]：
   - 在代碼中添加默認值
   - 舊狀態自動兼容

2. [cyan]刪除字段[/cyan]：
   - 代碼中不再讀取該字段
   - 舊狀態中的字段會被忽略

3. [cyan]重命名字段[/cyan]：
   - 編寫遷移函數
   - 在加載時轉換

4. [cyan]改變類型[/cyan]：
   - 編寫轉換邏輯
   - 驗證數據完整性

示例遷移代碼：
    """)

    migration_code = '''
def migrate_state(old_state: dict) -> dict:
    """遷移舊狀態到新格式"""
    new_state = old_state.copy()

    # 添加新字段
    if "version" not in new_state:
        new_state["version"] = "2.0"

    # 重命名字段
    if "old_name" in new_state:
        new_state["new_name"] = new_state.pop("old_name")

    # 類型轉換
    if "count" in new_state and isinstance(new_state["count"], str):
        new_state["count"] = int(new_state["count"])

    return new_state
    '''

    console.print(Panel(migration_code, title="遷移示例", border_style="blue"))


# ============================================================================
# 主函數
# ============================================================================

def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold green]Burr 持久化 - 狀態保存與恢復[/bold green]",
        border_style="green"
    ))

    console.print("\n[bold]持久化核心概念：[/bold]")
    console.print("1. [cyan]StatePersister[/cyan]: 持久化介面")
    console.print("2. [cyan]SQLLitePersister[/cyan]: SQLite 持久化")
    console.print("3. [cyan]檢查點[/cyan]: 定期保存狀態")
    console.print("4. [cyan]狀態恢復[/cyan]: 從持久化狀態恢復\n")

    # 運行示例
    basic_persistence_example()
    console.print("\n" + "="*60 + "\n")

    custom_persister_example()
    console.print("\n" + "="*60 + "\n")

    checkpoint_example()
    console.print("\n" + "="*60 + "\n")

    state_migration_example()

    # 總結
    console.print(Panel("""
[bold green]持久化完成！[/bold green]

關鍵要點：
1. 使用 with_state_persister() 啟用持久化
2. 每次狀態更新自動保存
3. 支持從崩潰中恢復
4. 可以自定義持久化後端
5. 檢查點機制保證數據安全

內建持久化器：
- SQLLitePersister: SQLite 資料庫
- 可擴展: 實現 BaseStatePersister

最佳實踐：
- 為長時間運行的任務啟用持久化
- 定期創建檢查點
- 實現狀態遷移邏輯
- 測試恢復流程
- 考慮性能影響

使用場景：
- 長時間運行的批處理
- 容錯的工作流
- 可恢復的 Agent 系統
- 需要審計追蹤的應用

下一步：
- 查看 06_追蹤調試.py 學習調試功能
- 查看 10_生產部署.py 了解生產環境配置
    """, title="總結", border_style="green"))


if __name__ == "__main__":
    main()

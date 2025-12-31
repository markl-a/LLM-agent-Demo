"""
ControlFlow 狀態管理詳解
========================

本文件深入探討 ControlFlow 中的狀態管理,包括:
1. 工作流狀態追蹤
2. 任務狀態管理
3. 共享狀態
4. 狀態持久化
5. 狀態轉換
6. 狀態恢復
7. 分布式狀態

作者: ControlFlow 示例團隊
日期: 2025
"""

import os
import json
import pickle
from typing import Optional, List, Dict, Any, TypeVar, Generic
from datetime import datetime
from pathlib import Path
from enum import Enum
import controlflow as cf
from controlflow import Agent, Task, Flow
from pydantic import BaseModel, Field
from dotenv import load_dotenv


# ========== 配置 ==========

load_dotenv()


# ========== 數據模型 ==========

class WorkflowState(str, Enum):
    """工作流狀態枚舉"""
    INITIALIZED = "initialized"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskState(str, Enum):
    """任務狀態枚舉"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class StateSnapshot(BaseModel):
    """狀態快照模型"""
    timestamp: datetime = Field(default_factory=datetime.now)
    workflow_state: WorkflowState
    task_states: Dict[str, TaskState]
    variables: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ProcessingContext(BaseModel):
    """處理上下文模型"""
    session_id: str
    user_id: Optional[str] = None
    variables: Dict[str, Any] = Field(default_factory=dict)
    history: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# ========== 基本狀態管理 ==========

class BasicStateManagement:
    """
    基本狀態管理示例

    演示工作流中的基本狀態追蹤和管理
    """

    def __init__(self):
        """初始化狀態管理器"""
        self.workflow_state = WorkflowState.INITIALIZED
        self.task_states: Dict[str, TaskState] = {}
        self.variables: Dict[str, Any] = {}

    def update_workflow_state(self, new_state: WorkflowState):
        """
        更新工作流狀態

        Args:
            new_state: 新狀態
        """
        old_state = self.workflow_state
        self.workflow_state = new_state

        print(f"🔄 工作流狀態變更: {old_state.value} → {new_state.value}")

    def update_task_state(self, task_id: str, new_state: TaskState):
        """
        更新任務狀態

        Args:
            task_id: 任務 ID
            new_state: 新狀態
        """
        old_state = self.task_states.get(task_id, TaskState.PENDING)
        self.task_states[task_id] = new_state

        print(f"📋 任務 {task_id} 狀態: {old_state.value} → {new_state.value}")

    def set_variable(self, key: str, value: Any):
        """
        設置變量

        Args:
            key: 變量名
            value: 變量值
        """
        self.variables[key] = value
        print(f"💾 設置變量: {key} = {value}")

    def get_variable(self, key: str, default: Any = None) -> Any:
        """
        獲取變量

        Args:
            key: 變量名
            default: 默認值

        Returns:
            Any: 變量值
        """
        value = self.variables.get(key, default)
        print(f"📖 讀取變量: {key} = {value}")
        return value

    def get_state_summary(self) -> Dict[str, Any]:
        """
        獲取狀態摘要

        Returns:
            Dict[str, Any]: 狀態摘要
        """
        summary = {
            "workflow_state": self.workflow_state.value,
            "total_tasks": len(self.task_states),
            "task_breakdown": {
                state.value: sum(1 for s in self.task_states.values() if s == state)
                for state in TaskState
            },
            "variables_count": len(self.variables)
        }

        print("\n📊 狀態摘要:")
        print(f"   工作流狀態: {summary['workflow_state']}")
        print(f"   任務總數: {summary['total_tasks']}")
        print(f"   變量數量: {summary['variables_count']}")

        return summary

    @staticmethod
    def demonstrate_basic_state():
        """演示基本狀態管理"""
        print("🔄 演示基本狀態管理\n")

        state_mgr = BasicStateManagement()

        # 初始化
        print("📍 初始化工作流")
        state_mgr.update_workflow_state(WorkflowState.INITIALIZED)
        state_mgr.set_variable("start_time", datetime.now().isoformat())
        print()

        # 開始執行
        print("📍 開始執行")
        state_mgr.update_workflow_state(WorkflowState.RUNNING)
        state_mgr.update_task_state("task_1", TaskState.RUNNING)
        state_mgr.set_variable("current_step", 1)
        print()

        # 任務完成
        print("📍 任務完成")
        state_mgr.update_task_state("task_1", TaskState.SUCCESS)
        state_mgr.update_task_state("task_2", TaskState.RUNNING)
        state_mgr.set_variable("current_step", 2)
        print()

        # 獲取摘要
        print("📍 獲取狀態摘要")
        summary = state_mgr.get_state_summary()
        print()


# ========== 共享狀態 ==========

class SharedState:
    """
    共享狀態管理

    在多個任務和 Agent 之間共享狀態
    """

    def __init__(self):
        """初始化共享狀態"""
        self._state: Dict[str, Any] = {}
        self._locks: Dict[str, bool] = {}
        self._history: List[Dict[str, Any]] = []

    def set(self, key: str, value: Any, record_history: bool = True):
        """
        設置共享狀態

        Args:
            key: 鍵
            value: 值
            record_history: 是否記錄歷史
        """
        old_value = self._state.get(key)
        self._state[key] = value

        if record_history:
            self._history.append({
                "action": "set",
                "key": key,
                "old_value": old_value,
                "new_value": value,
                "timestamp": datetime.now().isoformat()
            })

        print(f"🔄 共享狀態更新: {key} = {value}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        獲取共享狀態

        Args:
            key: 鍵
            default: 默認值

        Returns:
            Any: 值
        """
        return self._state.get(key, default)

    def update(self, updates: Dict[str, Any]):
        """
        批量更新

        Args:
            updates: 更新字典
        """
        print(f"📦 批量更新 {len(updates)} 個鍵")

        for key, value in updates.items():
            self.set(key, value, record_history=True)

    def delete(self, key: str):
        """
        刪除鍵

        Args:
            key: 鍵
        """
        if key in self._state:
            value = self._state.pop(key)
            self._history.append({
                "action": "delete",
                "key": key,
                "value": value,
                "timestamp": datetime.now().isoformat()
            })
            print(f"🗑️ 刪除鍵: {key}")

    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        獲取歷史記錄

        Args:
            limit: 限制數量

        Returns:
            List[Dict[str, Any]]: 歷史記錄
        """
        if limit:
            return self._history[-limit:]
        return self._history.copy()

    def clear(self):
        """清空狀態"""
        self._state.clear()
        self._locks.clear()
        print("🧹 共享狀態已清空")

    @staticmethod
    @cf.flow
    def demonstrate_shared_state():
        """演示共享狀態"""
        print("🔄 演示共享狀態管理\n")

        shared = SharedState()

        # 任務 1: 收集數據
        print("📍 任務 1: 收集數據")
        shared.set("data_collected", True)
        shared.set("data_count", 100)
        shared.set("collection_time", datetime.now().isoformat())
        print()

        # 任務 2: 處理數據
        print("📍 任務 2: 處理數據")
        data_count = shared.get("data_count", 0)
        print(f"   處理 {data_count} 條數據")
        shared.set("data_processed", True)
        shared.set("processing_time", datetime.now().isoformat())
        print()

        # 任務 3: 生成報告
        print("📍 任務 3: 生成報告")
        if shared.get("data_processed"):
            print("   數據已處理,生成報告")
            shared.set("report_generated", True)
        print()

        # 查看歷史
        print("📍 查看歷史記錄")
        history = shared.get_history(limit=5)
        print(f"   最近 {len(history)} 條記錄:")
        for record in history:
            print(f"      {record['action']}: {record['key']}")
        print()


# ========== 狀態持久化 ==========

class StatePersistence:
    """
    狀態持久化

    將狀態保存到磁盤並恢復
    """

    def __init__(self, storage_dir: str = "./.controlflow_state"):
        """
        初始化狀態持久化

        Args:
            storage_dir: 存儲目錄
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)

        self.state: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {}

    def save_state(self, state_id: str, state_data: Dict[str, Any]):
        """
        保存狀態

        Args:
            state_id: 狀態 ID
            state_data: 狀態數據
        """
        print(f"💾 保存狀態: {state_id}")

        file_path = self.storage_dir / f"{state_id}.json"

        save_data = {
            "state_id": state_id,
            "data": state_data,
            "timestamp": datetime.now().isoformat(),
            "version": "1.0"
        }

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)

        print(f"   ✅ 已保存到: {file_path}")

    def load_state(self, state_id: str) -> Optional[Dict[str, Any]]:
        """
        加載狀態

        Args:
            state_id: 狀態 ID

        Returns:
            Optional[Dict[str, Any]]: 狀態數據
        """
        print(f"📂 加載狀態: {state_id}")

        file_path = self.storage_dir / f"{state_id}.json"

        if not file_path.exists():
            print(f"   ❌ 狀態文件不存在")
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            save_data = json.load(f)

        print(f"   ✅ 已加載 (時間戳: {save_data['timestamp']})")

        return save_data['data']

    def list_states(self) -> List[str]:
        """
        列出所有保存的狀態

        Returns:
            List[str]: 狀態 ID 列表
        """
        states = [
            f.stem for f in self.storage_dir.glob("*.json")
        ]

        print(f"📋 找到 {len(states)} 個保存的狀態")
        return states

    def delete_state(self, state_id: str):
        """
        刪除狀態

        Args:
            state_id: 狀態 ID
        """
        file_path = self.storage_dir / f"{state_id}.json"

        if file_path.exists():
            file_path.unlink()
            print(f"🗑️ 已刪除狀態: {state_id}")
        else:
            print(f"⚠️ 狀態不存在: {state_id}")

    def create_snapshot(self, snapshot_name: str, data: Dict[str, Any]):
        """
        創建狀態快照

        Args:
            snapshot_name: 快照名稱
            data: 數據
        """
        print(f"📸 創建快照: {snapshot_name}")

        snapshot = StateSnapshot(
            workflow_state=WorkflowState.RUNNING,
            task_states={},
            variables=data,
            metadata={"name": snapshot_name}
        )

        self.save_state(f"snapshot_{snapshot_name}", snapshot.dict())

    @staticmethod
    def demonstrate_persistence():
        """演示狀態持久化"""
        print("🔄 演示狀態持久化\n")

        persistence = StatePersistence()

        # 保存狀態
        print("📍 保存狀態")
        workflow_state = {
            "current_step": 3,
            "completed_tasks": ["task1", "task2"],
            "variables": {"count": 42, "status": "running"}
        }
        persistence.save_state("workflow_001", workflow_state)
        print()

        # 創建快照
        print("📍 創建快照")
        persistence.create_snapshot("checkpoint_1", {"step": 5})
        print()

        # 列出狀態
        print("📍 列出所有狀態")
        states = persistence.list_states()
        for state_id in states:
            print(f"   - {state_id}")
        print()

        # 加載狀態
        print("📍 加載狀態")
        loaded_state = persistence.load_state("workflow_001")
        if loaded_state:
            print(f"   當前步驟: {loaded_state.get('current_step')}")
            print(f"   已完成任務: {loaded_state.get('completed_tasks')}")
        print()


# ========== 狀態轉換 ==========

class StateTransition:
    """
    狀態轉換管理

    定義和管理狀態之間的轉換規則
    """

    def __init__(self):
        """初始化狀態轉換管理器"""
        self.current_state: Optional[WorkflowState] = None
        self.transitions: Dict[WorkflowState, List[WorkflowState]] = {
            WorkflowState.INITIALIZED: [WorkflowState.RUNNING, WorkflowState.CANCELLED],
            WorkflowState.RUNNING: [WorkflowState.PAUSED, WorkflowState.COMPLETED, WorkflowState.FAILED],
            WorkflowState.PAUSED: [WorkflowState.RUNNING, WorkflowState.CANCELLED],
            WorkflowState.COMPLETED: [],
            WorkflowState.FAILED: [WorkflowState.RUNNING],
            WorkflowState.CANCELLED: []
        }
        self.transition_history: List[Dict[str, Any]] = []

    def can_transition(self, to_state: WorkflowState) -> bool:
        """
        檢查是否可以轉換到目標狀態

        Args:
            to_state: 目標狀態

        Returns:
            bool: 是否可以轉換
        """
        if self.current_state is None:
            return to_state == WorkflowState.INITIALIZED

        allowed = self.transitions.get(self.current_state, [])
        return to_state in allowed

    def transition(self, to_state: WorkflowState) -> bool:
        """
        執行狀態轉換

        Args:
            to_state: 目標狀態

        Returns:
            bool: 是否成功轉換
        """
        if not self.can_transition(to_state):
            print(f"❌ 無法從 {self.current_state} 轉換到 {to_state}")
            return False

        old_state = self.current_state
        self.current_state = to_state

        # 記錄轉換
        self.transition_history.append({
            "from": old_state.value if old_state else None,
            "to": to_state.value,
            "timestamp": datetime.now().isoformat()
        })

        print(f"✅ 狀態轉換: {old_state} → {to_state}")
        return True

    def get_allowed_transitions(self) -> List[WorkflowState]:
        """
        獲取當前允許的轉換

        Returns:
            List[WorkflowState]: 允許的下一狀態列表
        """
        if self.current_state is None:
            return [WorkflowState.INITIALIZED]

        return self.transitions.get(self.current_state, [])

    def get_transition_history(self) -> List[Dict[str, Any]]:
        """
        獲取轉換歷史

        Returns:
            List[Dict[str, Any]]: 轉換歷史
        """
        return self.transition_history.copy()

    @staticmethod
    def demonstrate_transitions():
        """演示狀態轉換"""
        print("🔄 演示狀態轉換\n")

        fsm = StateTransition()

        # 正常流程
        print("📍 正常工作流程")
        fsm.transition(WorkflowState.INITIALIZED)
        fsm.transition(WorkflowState.RUNNING)

        print(f"\n   當前允許的轉換:")
        for state in fsm.get_allowed_transitions():
            print(f"      - {state.value}")

        fsm.transition(WorkflowState.PAUSED)
        fsm.transition(WorkflowState.RUNNING)
        fsm.transition(WorkflowState.COMPLETED)
        print()

        # 嘗試非法轉換
        print("📍 嘗試非法轉換")
        fsm.transition(WorkflowState.RUNNING)  # 完成後不能再運行
        print()

        # 查看歷史
        print("📍 轉換歷史")
        for i, record in enumerate(fsm.get_transition_history(), 1):
            print(f"   {i}. {record['from']} → {record['to']}")
        print()


# ========== 上下文管理器 ==========

class ContextManager:
    """
    上下文管理器

    管理工作流執行上下文
    """

    def __init__(self):
        """初始化上下文管理器"""
        self.contexts: Dict[str, ProcessingContext] = {}

    def create_context(self, session_id: str, user_id: Optional[str] = None) -> ProcessingContext:
        """
        創建新上下文

        Args:
            session_id: 會話 ID
            user_id: 用戶 ID

        Returns:
            ProcessingContext: 上下文對象
        """
        print(f"🆕 創建上下文: {session_id}")

        context = ProcessingContext(
            session_id=session_id,
            user_id=user_id
        )

        self.contexts[session_id] = context
        return context

    def get_context(self, session_id: str) -> Optional[ProcessingContext]:
        """
        獲取上下文

        Args:
            session_id: 會話 ID

        Returns:
            Optional[ProcessingContext]: 上下文對象
        """
        return self.contexts.get(session_id)

    def update_context(
        self,
        session_id: str,
        variables: Optional[Dict[str, Any]] = None,
        append_history: Optional[Dict[str, Any]] = None
    ):
        """
        更新上下文

        Args:
            session_id: 會話 ID
            variables: 要更新的變量
            append_history: 要添加的歷史記錄
        """
        context = self.get_context(session_id)
        if not context:
            print(f"❌ 上下文不存在: {session_id}")
            return

        if variables:
            context.variables.update(variables)
            print(f"🔄 更新變量: {list(variables.keys())}")

        if append_history:
            context.history.append(append_history)
            print(f"📝 添加歷史記錄")

        context.updated_at = datetime.now()

    def delete_context(self, session_id: str):
        """
        刪除上下文

        Args:
            session_id: 會話 ID
        """
        if session_id in self.contexts:
            del self.contexts[session_id]
            print(f"🗑️ 刪除上下文: {session_id}")

    @staticmethod
    def demonstrate_context():
        """演示上下文管理"""
        print("🔄 演示上下文管理\n")

        mgr = ContextManager()

        # 創建上下文
        print("📍 創建用戶會話")
        ctx = mgr.create_context("session_001", "user_123")
        print()

        # 更新上下文
        print("📍 更新上下文")
        mgr.update_context(
            "session_001",
            variables={"step": 1, "score": 0},
            append_history={"action": "start", "time": datetime.now().isoformat()}
        )
        print()

        # 使用上下文
        print("📍 使用上下文")
        ctx = mgr.get_context("session_001")
        if ctx:
            print(f"   會話 ID: {ctx.session_id}")
            print(f"   用戶 ID: {ctx.user_id}")
            print(f"   變量: {ctx.variables}")
            print(f"   歷史記錄數: {len(ctx.history)}")
        print()


# ========== 主程序 ==========

def main():
    """
    主程序入口

    演示各種狀態管理方法
    """
    print("=" * 70)
    print("  ControlFlow 狀態管理示例")
    print("=" * 70)
    print()

    try:
        # 1. 基本狀態管理
        print("\n" + "=" * 70)
        print("1. 基本狀態管理")
        print("=" * 70 + "\n")

        BasicStateManagement.demonstrate_basic_state()

        # 2. 共享狀態
        print("\n" + "=" * 70)
        print("2. 共享狀態")
        print("=" * 70 + "\n")

        SharedState.demonstrate_shared_state()

        # 3. 狀態持久化
        print("\n" + "=" * 70)
        print("3. 狀態持久化")
        print("=" * 70 + "\n")

        StatePersistence.demonstrate_persistence()

        # 4. 狀態轉換
        print("\n" + "=" * 70)
        print("4. 狀態轉換")
        print("=" * 70 + "\n")

        StateTransition.demonstrate_transitions()

        # 5. 上下文管理
        print("\n" + "=" * 70)
        print("5. 上下文管理")
        print("=" * 70 + "\n")

        ContextManager.demonstrate_context()

        print("\n" + "=" * 70)
        print("演示完成")
        print("=" * 70)
        print("\n✅ 所有狀態管理示例已成功展示!")
        print("\n💡 狀態管理要點:")
        print("   - 狀態追蹤: 實時監控工作流和任務狀態")
        print("   - 共享狀態: 在組件間安全共享數據")
        print("   - 持久化: 保存和恢復狀態以支持長時運行")
        print("   - 狀態轉換: 定義合法的狀態轉換規則")
        print("   - 上下文管理: 維護執行環境和用戶會話")
        print("\n💡 下一步:")
        print("   - 查看 08_錯誤處理.py 學習錯誤處理")
        print("   - 查看 09_子流程.py 學習子流程組合")
        print()

    except Exception as e:
        print(f"\n❌ 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

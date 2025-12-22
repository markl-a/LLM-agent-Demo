"""
Pydantic AI - 持久執行 (Durable Execution) 範例

本範例展示：
1. 執行狀態持久化
2. 錯誤恢復機制
3. 斷點續傳
4. 長時間運行任務
5. 檢查點管理

持久執行確保長時間運行的 Agent 任務能夠可靠完成
注意：本範例展示概念，具體實現可能需要額外的持久化庫
"""

import asyncio
import json
import pickle
from typing import Optional, Any
from pathlib import Path
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field, asdict
from pydantic import BaseModel
from pydantic_ai import Agent


# ============================================================================
# 範例 1: 基本狀態持久化
# ============================================================================

class ExecutionState(BaseModel):
    """執行狀態"""
    execution_id: str
    current_step: int = 0
    total_steps: int
    completed: bool = False
    results: dict = {}
    started_at: str
    updated_at: str


class StatePersistence:
    """狀態持久化管理"""

    def __init__(self, storage_dir: str = "./execution_states"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)

    def save_state(self, state: ExecutionState):
        """保存狀態"""
        file_path = self.storage_dir / f"{state.execution_id}.json"

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(state.model_dump(), f, ensure_ascii=False, indent=2)

        print(f"  💾 狀態已保存：{state.current_step}/{state.total_steps}")

    def load_state(self, execution_id: str) -> Optional[ExecutionState]:
        """加載狀態"""
        file_path = self.storage_dir / f"{execution_id}.json"

        if not file_path.exists():
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        print(f"  📂 狀態已加載：{data['current_step']}/{data['total_steps']}")
        return ExecutionState(**data)

    def delete_state(self, execution_id: str):
        """刪除狀態"""
        file_path = self.storage_dir / f"{execution_id}.json"
        if file_path.exists():
            file_path.unlink()
            print(f"  🗑️  狀態已刪除")


async def example_1_basic_persistence():
    """基本狀態持久化"""
    print("\n" + "="*60)
    print("範例 1: 基本狀態持久化")
    print("="*60)

    persistence = StatePersistence()
    execution_id = f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # 創建初始狀態
    state = ExecutionState(
        execution_id=execution_id,
        total_steps=5,
        started_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat()
    )

    # 模擬多步驟執行
    for step in range(1, state.total_steps + 1):
        print(f"\n執行步驟 {step}/{state.total_steps}")

        # 更新狀態
        state.current_step = step
        state.results[f"step_{step}"] = f"結果 {step}"
        state.updated_at = datetime.now().isoformat()

        # 保存狀態
        persistence.save_state(state)

        await asyncio.sleep(0.2)

    state.completed = True
    persistence.save_state(state)

    print(f"\n✓ 執行完成")

    # 清理
    persistence.delete_state(execution_id)


# ============================================================================
# 範例 2: 錯誤恢復
# ============================================================================

@dataclass
class ResilientTask:
    """具有錯誤恢復能力的任務"""

    execution_id: str
    steps: list[str]
    persistence: StatePersistence

    def __post_init__(self):
        self.agent = Agent('openai:gpt-4')

    async def execute_step(self, step_name: str, step_num: int) -> str:
        """執行單個步驟"""
        print(f"  → 執行步驟 {step_num}: {step_name}")

        # 模擬可能失敗的操作
        if step_num == 3:
            # 模擬錯誤（註釋掉以正常運行）
            # raise Exception("模擬錯誤")
            pass

        # 使用 Agent 處理
        result = await self.agent.run(f"處理任務：{step_name}")

        return result.data[:50] + "..."

    async def run(self, resume: bool = False) -> dict:
        """運行任務"""
        # 嘗試恢復狀態
        state = None
        if resume:
            state = self.persistence.load_state(self.execution_id)

        # 創建新狀態或使用恢復的狀態
        if state is None:
            state = ExecutionState(
                execution_id=self.execution_id,
                total_steps=len(self.steps),
                started_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            print("開始新執行")
        else:
            print(f"從步驟 {state.current_step + 1} 恢復執行")

        try:
            # 從當前步驟繼續
            for i in range(state.current_step, len(self.steps)):
                step_name = self.steps[i]
                result = await self.execute_step(step_name, i + 1)

                # 更新並保存狀態
                state.current_step = i + 1
                state.results[f"step_{i + 1}"] = result
                state.updated_at = datetime.now().isoformat()

                self.persistence.save_state(state)

                await asyncio.sleep(0.3)

            # 完成
            state.completed = True
            self.persistence.save_state(state)

            return {
                "status": "completed",
                "steps_completed": state.current_step,
                "results": state.results
            }

        except Exception as e:
            print(f"\n✗ 錯誤發生：{e}")
            print(f"已保存狀態，可以稍後恢復")

            return {
                "status": "failed",
                "error": str(e),
                "steps_completed": state.current_step,
                "can_resume": True
            }


async def example_2_error_recovery():
    """錯誤恢復機制"""
    print("\n" + "="*60)
    print("範例 2: 錯誤恢復")
    print("="*60)

    persistence = StatePersistence()
    execution_id = "resilient_task_001"

    task = ResilientTask(
        execution_id=execution_id,
        steps=[
            "收集數據",
            "分析數據",
            "生成報告",
            "發送通知"
        ],
        persistence=persistence
    )

    # 首次執行
    print("首次執行：")
    result = await task.run(resume=False)

    print(f"\n結果：{result['status']}")
    print(f"完成步驟：{result['steps_completed']}")

    # 如果失敗，嘗試恢復
    if result['status'] == 'failed' and result.get('can_resume'):
        print("\n嘗試恢復執行...")
        result = await task.run(resume=True)
        print(f"恢復結果：{result['status']}")

    # 清理
    persistence.delete_state(execution_id)


# ============================================================================
# 範例 3: 檢查點管理
# ============================================================================

class Checkpoint:
    """檢查點"""

    def __init__(self, name: str, data: dict):
        self.name = name
        self.data = data
        self.timestamp = datetime.now().isoformat()


class CheckpointManager:
    """檢查點管理器"""

    def __init__(self, execution_id: str):
        self.execution_id = execution_id
        self.checkpoints: list[Checkpoint] = []
        self.storage_path = Path(f"./checkpoints/{execution_id}.pkl")
        self.storage_path.parent.mkdir(exist_ok=True)

    def create_checkpoint(self, name: str, data: dict):
        """創建檢查點"""
        checkpoint = Checkpoint(name, data)
        self.checkpoints.append(checkpoint)

        # 持久化
        self._save()

        print(f"  📍 檢查點已創建：{name}")

    def get_latest_checkpoint(self) -> Optional[Checkpoint]:
        """獲取最新檢查點"""
        if not self.checkpoints:
            return None
        return self.checkpoints[-1]

    def restore_checkpoint(self, name: str) -> Optional[dict]:
        """恢復到指定檢查點"""
        for checkpoint in reversed(self.checkpoints):
            if checkpoint.name == name:
                print(f"  📍 恢復檢查點：{name}")
                return checkpoint.data
        return None

    def _save(self):
        """保存到磁盤"""
        with open(self.storage_path, 'wb') as f:
            pickle.dump(self.checkpoints, f)

    def _load(self):
        """從磁盤加載"""
        if self.storage_path.exists():
            with open(self.storage_path, 'rb') as f:
                self.checkpoints = pickle.load(f)


async def example_3_checkpoints():
    """檢查點管理"""
    print("\n" + "="*60)
    print("範例 3: 檢查點管理")
    print("="*60)

    execution_id = "checkpoint_demo"
    manager = CheckpointManager(execution_id)

    # 模擬多階段處理
    stages = [
        ("初始化", {"config": "loaded"}),
        ("數據收集", {"records": 1000}),
        ("數據處理", {"processed": 950}),
        ("結果生成", {"report": "generated"}),
    ]

    for stage_name, stage_data in stages:
        print(f"\n階段：{stage_name}")

        # 執行階段工作
        await asyncio.sleep(0.3)

        # 創建檢查點
        manager.create_checkpoint(stage_name, stage_data)

    # 獲取最新檢查點
    latest = manager.get_latest_checkpoint()
    if latest:
        print(f"\n最新檢查點：{latest.name}")
        print(f"數據：{latest.data}")

    # 恢復到特定檢查點
    restored = manager.restore_checkpoint("數據處理")
    if restored:
        print(f"恢復的數據：{restored}")

    # 清理
    if manager.storage_path.exists():
        manager.storage_path.unlink()


# ============================================================================
# 範例 4: 長時間運行任務
# ============================================================================

@dataclass
class LongRunningTask:
    """長時間運行的任務"""

    task_id: str
    total_items: int
    batch_size: int = 10

    def __post_init__(self):
        self.agent = Agent('openai:gpt-4')
        self.persistence = StatePersistence()
        self.processed_items = 0

    async def process_batch(
        self,
        batch_num: int,
        items: list[str]
    ) -> list[str]:
        """處理一批項目"""
        print(f"  處理批次 {batch_num} ({len(items)} 項)")

        # 模擬處理
        await asyncio.sleep(0.5)

        results = [f"已處理: {item}" for item in items]
        return results

    async def run(self, resume: bool = False) -> dict:
        """運行長任務"""
        # 加載或創建狀態
        state = None
        if resume:
            state = self.persistence.load_state(self.task_id)

        if state is None:
            state = ExecutionState(
                execution_id=self.task_id,
                total_steps=self.total_items,
                started_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )

        self.processed_items = state.current_step

        # 模擬項目列表
        all_items = [f"項目_{i}" for i in range(1, self.total_items + 1)]

        # 分批處理
        while self.processed_items < self.total_items:
            # 獲取下一批
            start_idx = self.processed_items
            end_idx = min(start_idx + self.batch_size, self.total_items)
            batch = all_items[start_idx:end_idx]

            # 處理批次
            batch_num = (start_idx // self.batch_size) + 1
            results = await self.process_batch(batch_num, batch)

            # 更新狀態
            self.processed_items = end_idx
            state.current_step = self.processed_items
            state.results[f"batch_{batch_num}"] = results
            state.updated_at = datetime.now().isoformat()

            # 保存狀態（檢查點）
            self.persistence.save_state(state)

            print(f"  進度：{self.processed_items}/{self.total_items}")

        # 完成
        state.completed = True
        self.persistence.save_state(state)

        return {
            "status": "completed",
            "total_processed": self.processed_items,
            "batches": len(state.results)
        }


async def example_4_long_running():
    """長時間運行任務"""
    print("\n" + "="*60)
    print("範例 4: 長時間運行任務")
    print("="*60)

    task = LongRunningTask(
        task_id="long_task_001",
        total_items=50,
        batch_size=10
    )

    print("開始處理 50 個項目...\n")

    result = await task.run(resume=False)

    print(f"\n✓ 任務完成")
    print(f"  處理項目數：{result['total_processed']}")
    print(f"  批次數：{result['batches']}")

    # 清理
    task.persistence.delete_state(task.task_id)


# ============================================================================
# 範例 5: 事務性執行
# ============================================================================

class TransactionStatus(str, Enum):
    """事務狀態"""
    PENDING = "pending"
    COMMITTED = "committed"
    ROLLED_BACK = "rolled_back"


@dataclass
class Transaction:
    """事務"""

    transaction_id: str
    operations: list[dict]
    status: TransactionStatus = TransactionStatus.PENDING
    completed_operations: list[str] = field(default_factory=list)

    async def execute(self) -> dict:
        """執行事務"""
        print(f"開始事務：{self.transaction_id}")

        try:
            # 執行所有操作
            for i, operation in enumerate(self.operations):
                print(f"  → 執行操作 {i + 1}: {operation['name']}")

                # 模擬操作
                await asyncio.sleep(0.2)

                # 模擬可能的錯誤
                if operation.get('fail'):
                    raise Exception(f"操作失敗：{operation['name']}")

                self.completed_operations.append(operation['name'])

            # 提交事務
            self.status = TransactionStatus.COMMITTED
            print(f"✓ 事務已提交")

            return {
                "status": "success",
                "operations_completed": len(self.completed_operations)
            }

        except Exception as e:
            # 回滾事務
            print(f"\n✗ 錯誤：{e}")
            print("回滾事務...")

            # 回滾已完成的操作
            for op in reversed(self.completed_operations):
                print(f"  ← 回滾：{op}")
                await asyncio.sleep(0.1)

            self.status = TransactionStatus.ROLLED_BACK

            return {
                "status": "rolled_back",
                "error": str(e),
                "operations_rolled_back": len(self.completed_operations)
            }


async def example_5_transactions():
    """事務性執行"""
    print("\n" + "="*60)
    print("範例 5: 事務性執行")
    print("="*60)

    # 成功的事務
    print("測試 1: 成功的事務")
    transaction1 = Transaction(
        transaction_id="txn_001",
        operations=[
            {"name": "創建記錄"},
            {"name": "更新索引"},
            {"name": "發送通知"},
        ]
    )

    result1 = await transaction1.execute()
    print(f"結果：{result1['status']}\n")

    # 失敗的事務
    print("測試 2: 失敗的事務（會回滾）")
    transaction2 = Transaction(
        transaction_id="txn_002",
        operations=[
            {"name": "創建記錄"},
            {"name": "更新索引"},
            {"name": "發送通知", "fail": True},  # 這個會失敗
        ]
    )

    result2 = await transaction2.execute()
    print(f"結果：{result2['status']}")


# ============================================================================
# 主程式
# ============================================================================

async def main():
    """運行所有範例"""
    print("\n" + "💾 " + "="*58)
    print("Pydantic AI - 持久執行範例")
    print("="*60)

    await example_1_basic_persistence()
    await example_2_error_recovery()
    await example_3_checkpoints()
    await example_4_long_running()
    await example_5_transactions()

    print("\n" + "="*60)
    print("✓ 持久執行範例完成！")
    print("💡 持久執行的關鍵：")
    print("   1. 定期保存執行狀態")
    print("   2. 支持從任意點恢復")
    print("   3. 使用檢查點機制")
    print("   4. 實現事務性操作")
    print("="*60)


if __name__ == '__main__':
    import os
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  請設置 OPENAI_API_KEY 環境變量")
    else:
        asyncio.run(main())

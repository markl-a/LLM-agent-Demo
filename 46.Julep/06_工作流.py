"""
Julep 工作流示例

這個模塊展示了 Julep 平台的多步驟工作流功能。
包括順序執行、並行執行、條件分支、循環和錯誤處理。

主要功能：
1. 順序工作流
2. 並行工作流
3. 條件分支
4. 循環迭代
5. 錯誤處理和重試
6. 工作流監控

作者：Julep 示例
日期：2025-12-31
"""

import time
import json
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import uuid
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed


class WorkflowStatus(Enum):
    """工作流狀態"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class StepStatus(Enum):
    """步驟狀態"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowContext:
    """工作流上下文

    在工作流執行過程中傳遞的數據。
    """
    variables: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

    def set(self, key: str, value: Any):
        """設置變量"""
        self.variables[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """獲取變量"""
        return self.variables.get(key, default)

    def set_output(self, step_id: str, output: Any):
        """設置步驟輸出"""
        self.outputs[step_id] = output

    def get_output(self, step_id: str) -> Any:
        """獲取步驟輸出"""
        return self.outputs.get(step_id)

    def add_error(self, error: str):
        """添加錯誤"""
        self.errors.append(error)


@dataclass
class WorkflowStep:
    """工作流步驟"""
    id: str
    name: str
    action: Callable
    depends_on: List[str] = field(default_factory=list)
    timeout: Optional[int] = None
    retry: int = 0
    retry_delay: int = 1
    on_error: Optional[str] = None  # "continue", "fail", "retry"
    condition: Optional[Callable] = None

    status: StepStatus = StepStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def can_execute(self, context: WorkflowContext, completed_steps: set) -> bool:
        """檢查是否可以執行

        Args:
            context: 工作流上下文
            completed_steps: 已完成的步驟 ID 集合

        Returns:
            是否可以執行
        """
        # 檢查依賴
        if self.depends_on:
            if not all(dep in completed_steps for dep in self.depends_on):
                return False

        # 檢查條件
        if self.condition:
            try:
                return self.condition(context)
            except Exception as e:
                print(f"[ERROR] 條件評估失敗: {e}")
                return False

        return True

    def execute(self, context: WorkflowContext) -> Any:
        """執行步驟

        Args:
            context: 工作流上下文

        Returns:
            執行結果
        """
        self.status = StepStatus.RUNNING
        self.started_at = datetime.now()

        print(f"\n[STEP] 執行步驟: {self.name} (ID: {self.id})")

        attempt = 0
        max_attempts = self.retry + 1

        while attempt < max_attempts:
            try:
                # 執行動作
                result = self.action(context)

                # 成功
                self.status = StepStatus.COMPLETED
                self.result = result
                self.completed_at = datetime.now()

                duration = (self.completed_at - self.started_at).total_seconds()
                print(f"[SUCCESS] 步驟完成: {self.name} (耗時: {duration:.2f}s)")

                return result

            except Exception as e:
                attempt += 1
                error_msg = f"步驟失敗: {str(e)}"

                if attempt < max_attempts:
                    print(f"[RETRY] {error_msg}, 重試 {attempt}/{self.retry}")
                    time.sleep(self.retry_delay)
                else:
                    self.status = StepStatus.FAILED
                    self.error = error_msg
                    self.completed_at = datetime.now()

                    print(f"[FAILED] {error_msg}")

                    if self.on_error == "continue":
                        context.add_error(error_msg)
                        return None
                    else:
                        raise

        return None

    def get_duration(self) -> Optional[float]:
        """獲取執行時長"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


class Workflow:
    """工作流類"""

    def __init__(
        self,
        name: str,
        description: str = "",
        max_parallel: int = 5
    ):
        """初始化工作流

        Args:
            name: 工作流名稱
            description: 描述
            max_parallel: 最大並行數
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.max_parallel = max_parallel
        self.steps: Dict[str, WorkflowStep] = {}
        self.status = WorkflowStatus.PENDING
        self.context = WorkflowContext()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

    def add_step(self, step: WorkflowStep):
        """添加步驟

        Args:
            step: 工作流步驟
        """
        self.steps[step.id] = step
        print(f"[INFO] 添加步驟: {step.name}")

    def execute(self) -> WorkflowContext:
        """執行工作流

        Returns:
            工作流上下文
        """
        print(f"\n{'='*60}")
        print(f"執行工作流: {self.name}")
        print(f"{'='*60}")
        print(f"總步驟數: {len(self.steps)}")
        print(f"最大並行數: {self.max_parallel}")

        self.status = WorkflowStatus.RUNNING
        self.started_at = datetime.now()

        try:
            completed_steps = set()
            failed_steps = set()

            # 按依賴順序執行
            while len(completed_steps) + len(failed_steps) < len(self.steps):
                # 找出可以執行的步驟
                ready_steps = [
                    step for step in self.steps.values()
                    if step.id not in completed_steps
                    and step.id not in failed_steps
                    and step.status == StepStatus.PENDING
                    and step.can_execute(self.context, completed_steps)
                ]

                if not ready_steps:
                    # 檢查是否有步驟仍在運行
                    running_steps = [
                        step for step in self.steps.values()
                        if step.status == StepStatus.RUNNING
                    ]
                    if not running_steps:
                        # 沒有可執行的步驟，可能有循環依賴
                        break
                    time.sleep(0.1)
                    continue

                # 並行執行就緒的步驟
                with ThreadPoolExecutor(max_workers=self.max_parallel) as executor:
                    futures = {
                        executor.submit(step.execute, self.context): step
                        for step in ready_steps
                    }

                    for future in as_completed(futures):
                        step = futures[future]
                        try:
                            result = future.result()
                            self.context.set_output(step.id, result)
                            completed_steps.add(step.id)
                        except Exception as e:
                            failed_steps.add(step.id)
                            if step.on_error != "continue":
                                raise

            # 完成
            self.status = WorkflowStatus.COMPLETED
            self.completed_at = datetime.now()

            duration = (self.completed_at - self.started_at).total_seconds()
            print(f"\n{'='*60}")
            print(f"工作流執行完成")
            print(f"完成步驟: {len(completed_steps)}/{len(self.steps)}")
            print(f"失敗步驟: {len(failed_steps)}")
            print(f"總耗時: {duration:.2f}s")
            print(f"{'='*60}")

        except Exception as e:
            self.status = WorkflowStatus.FAILED
            self.completed_at = datetime.now()
            print(f"\n[ERROR] 工作流執行失敗: {e}")
            raise

        return self.context

    def get_step_graph(self) -> Dict[str, Any]:
        """獲取步驟依賴圖"""
        return {
            step_id: {
                "name": step.name,
                "depends_on": step.depends_on,
                "status": step.status.value
            }
            for step_id, step in self.steps.items()
        }


class WorkflowBuilder:
    """工作流構建器

    提供流暢的 API 構建工作流。
    """

    def __init__(self, name: str):
        """初始化構建器"""
        self.workflow = Workflow(name)
        self.step_counter = 0

    def add_step(
        self,
        name: str,
        action: Callable,
        depends_on: Optional[List[str]] = None,
        **kwargs
    ) -> 'WorkflowBuilder':
        """添加步驟

        Args:
            name: 步驟名稱
            action: 執行函數
            depends_on: 依賴步驟 ID 列表
            **kwargs: 其他參數

        Returns:
            構建器自身
        """
        self.step_counter += 1
        step_id = f"step_{self.step_counter}"

        step = WorkflowStep(
            id=step_id,
            name=name,
            action=action,
            depends_on=depends_on or [],
            **kwargs
        )

        self.workflow.add_step(step)
        return self

    def add_parallel_steps(
        self,
        steps: List[tuple]
    ) -> 'WorkflowBuilder':
        """添加並行步驟

        Args:
            steps: (名稱, 動作) 元組列表

        Returns:
            構建器自身
        """
        for name, action in steps:
            self.add_step(name, action)
        return self

    def add_conditional_step(
        self,
        name: str,
        condition: Callable,
        action: Callable,
        depends_on: Optional[List[str]] = None
    ) -> 'WorkflowBuilder':
        """添加條件步驟

        Args:
            name: 步驟名稱
            condition: 條件函數
            action: 執行函數
            depends_on: 依賴步驟

        Returns:
            構建器自身
        """
        return self.add_step(
            name,
            action,
            depends_on=depends_on,
            condition=condition
        )

    def build(self) -> Workflow:
        """構建工作流"""
        return self.workflow


# 示例動作函數

def action_fetch_data(context: WorkflowContext) -> Dict:
    """獲取數據"""
    print("  -> 從數據源獲取數據...")
    time.sleep(0.5)
    data = {"records": 100, "timestamp": datetime.now().isoformat()}
    context.set("data", data)
    return data


def action_process_data(context: WorkflowContext) -> Dict:
    """處理數據"""
    print("  -> 處理數據...")
    data = context.get("data", {})
    time.sleep(0.3)
    processed = {
        "original_records": data.get("records", 0),
        "processed_records": data.get("records", 0) * 2,
        "status": "processed"
    }
    return processed


def action_validate_data(context: WorkflowContext) -> bool:
    """驗證數據"""
    print("  -> 驗證數據...")
    time.sleep(0.2)
    data = context.get("data", {})
    is_valid = data.get("records", 0) > 0
    context.set("is_valid", is_valid)
    return is_valid


def action_save_results(context: WorkflowContext) -> str:
    """保存結果"""
    print("  -> 保存結果...")
    time.sleep(0.4)
    return "results_saved.json"


def action_send_notification(context: WorkflowContext) -> bool:
    """發送通知"""
    print("  -> 發送通知...")
    time.sleep(0.3)
    return True


def action_cleanup(context: WorkflowContext):
    """清理"""
    print("  -> 清理臨時資源...")
    time.sleep(0.2)


def demo_sequential_workflow():
    """順序工作流示例"""
    print("\n" + "="*60)
    print("示例 1: 順序工作流")
    print("="*60)

    # 構建工作流
    workflow = (WorkflowBuilder("數據處理工作流")
                .add_step("獲取數據", action_fetch_data)
                .add_step("驗證數據", action_validate_data, depends_on=["step_1"])
                .add_step("處理數據", action_process_data, depends_on=["step_2"])
                .add_step("保存結果", action_save_results, depends_on=["step_3"])
                .build())

    # 執行工作流
    context = workflow.execute()

    # 查看結果
    print(f"\n最終上下文變量: {list(context.variables.keys())}")
    print(f"步驟輸出: {list(context.outputs.keys())}")


def demo_parallel_workflow():
    """並行工作流示例"""
    print("\n" + "="*60)
    print("示例 2: 並行工作流")
    print("="*60)

    def fetch_source_a(ctx):
        print("  -> 從來源 A 獲取數據...")
        time.sleep(0.5)
        return {"source": "A", "data": [1, 2, 3]}

    def fetch_source_b(ctx):
        print("  -> 從來源 B 獲取數據...")
        time.sleep(0.4)
        return {"source": "B", "data": [4, 5, 6]}

    def fetch_source_c(ctx):
        print("  -> 從來源 C 獲取數據...")
        time.sleep(0.3)
        return {"source": "C", "data": [7, 8, 9]}

    def merge_data(ctx):
        print("  -> 合併所有數據...")
        # 獲取所有源的數據
        all_data = []
        for output in ctx.outputs.values():
            if isinstance(output, dict) and "data" in output:
                all_data.extend(output["data"])
        return {"merged": all_data, "count": len(all_data)}

    # 構建工作流
    workflow = (WorkflowBuilder("並行數據獲取")
                .add_parallel_steps([
                    ("獲取來源 A", fetch_source_a),
                    ("獲取來源 B", fetch_source_b),
                    ("獲取來源 C", fetch_source_c)
                ])
                .add_step("合併數據", merge_data, depends_on=["step_1", "step_2", "step_3"])
                .build())

    # 執行
    context = workflow.execute()

    # 查看合併結果
    merged = context.get_output("step_4")
    print(f"\n合併結果: {merged}")


def demo_conditional_workflow():
    """條件工作流示例"""
    print("\n" + "="*60)
    print("示例 3: 條件工作流")
    print("="*60)

    def check_condition(ctx):
        """條件檢查：數據是否有效"""
        return ctx.get("is_valid", False)

    def handle_valid_data(ctx):
        print("  -> 處理有效數據...")
        time.sleep(0.3)
        return "valid_data_processed"

    def handle_invalid_data(ctx):
        print("  -> 處理無效數據...")
        time.sleep(0.2)
        return "invalid_data_logged"

    # 構建工作流
    workflow = WorkflowBuilder("條件處理工作流")

    # 步驟 1: 獲取和驗證數據
    workflow.add_step("獲取數據", action_fetch_data)
    workflow.add_step("驗證數據", action_validate_data, depends_on=["step_1"])

    # 步驟 2: 條件分支
    workflow.add_conditional_step(
        "處理有效數據",
        condition=check_condition,
        action=handle_valid_data,
        depends_on=["step_2"]
    )

    workflow.add_conditional_step(
        "處理無效數據",
        condition=lambda ctx: not check_condition(ctx),
        action=handle_invalid_data,
        depends_on=["step_2"]
    )

    # 構建並執行
    wf = workflow.build()
    context = wf.execute()

    print(f"\n數據是否有效: {context.get('is_valid')}")


def demo_error_handling():
    """錯誤處理示例"""
    print("\n" + "="*60)
    print("示例 4: 錯誤處理和重試")
    print("="*60)

    attempt_count = {"value": 0}

    def unreliable_action(ctx):
        """不可靠的動作（會失敗幾次）"""
        attempt_count["value"] += 1
        print(f"  -> 嘗試執行 (第 {attempt_count['value']} 次)...")

        if attempt_count["value"] < 3:
            raise Exception("模擬失敗")

        time.sleep(0.2)
        return "success_after_retry"

    def cleanup_on_error(ctx):
        print("  -> 執行錯誤清理...")
        return "cleaned_up"

    # 構建工作流
    workflow = (WorkflowBuilder("錯誤處理工作流")
                .add_step(
                    "不穩定操作",
                    unreliable_action,
                    retry=3,
                    retry_delay=0.5
                )
                .add_step("清理", cleanup_on_error, depends_on=["step_1"])
                .build())

    # 執行
    context = workflow.execute()

    print(f"\n總嘗試次數: {attempt_count['value']}")


def demo_complex_workflow():
    """複雜工作流示例"""
    print("\n" + "="*60)
    print("示例 5: 複雜工作流")
    print("="*60)

    # 構建複雜的多階段工作流
    workflow = WorkflowBuilder("ETL 工作流")

    # 階段 1: 並行提取
    workflow.add_parallel_steps([
        ("提取數據庫數據", lambda ctx: {"db": "data"}),
        ("提取 API 數據", lambda ctx: {"api": "data"}),
        ("提取文件數據", lambda ctx: {"file": "data"})
    ])

    # 階段 2: 轉換
    workflow.add_step(
        "轉換數據",
        lambda ctx: {"transformed": "data"},
        depends_on=["step_1", "step_2", "step_3"]
    )

    # 階段 3: 驗證
    workflow.add_step(
        "驗證轉換結果",
        lambda ctx: True,
        depends_on=["step_4"]
    )

    # 階段 4: 並行加載
    workflow.add_parallel_steps([
        ("加載到數據倉庫", lambda ctx: "loaded_to_dw"),
        ("生成報告", lambda ctx: "report_generated")
    ])

    # 這些步驟依賴驗證
    workflow.steps["step_6"].depends_on = ["step_5"]
    workflow.steps["step_7"].depends_on = ["step_5"]

    # 階段 5: 清理和通知
    workflow.add_step(
        "發送完成通知",
        lambda ctx: "notification_sent",
        depends_on=["step_6", "step_7"]
    )

    # 執行
    wf = workflow.build()
    context = wf.execute()

    # 顯示執行圖
    print(f"\n步驟依賴圖:")
    graph = wf.get_step_graph()
    for step_id, info in graph.items():
        print(f"  {step_id}: {info['name']}")
        print(f"    依賴: {info['depends_on']}")
        print(f"    狀態: {info['status']}")


def main():
    """主函數"""
    print("="*60)
    print("Julep 工作流示例")
    print("="*60)

    try:
        demo_sequential_workflow()
        demo_parallel_workflow()
        demo_conditional_workflow()
        demo_error_handling()
        demo_complex_workflow()

        print("\n" + "="*60)
        print("所有示例執行完成！")
        print("="*60)

    except Exception as e:
        print(f"\n[ERROR] 執行出錯: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

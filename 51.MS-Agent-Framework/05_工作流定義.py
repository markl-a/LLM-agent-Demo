"""
Microsoft Agent Framework - 工作流定義

這個檔案展示如何定義和執行複雜的工作流程。
Agent Framework 提供聲明式和程式化兩種工作流定義方式。

主要內容:
1. 工作流基本概念
2. YAML 格式工作流定義
3. 程式化工作流建構
4. 條件分支和循環
5. 並行執行
6. 錯誤處理和重試
7. 工作流監控
8. 實際應用案例

作者: Microsoft Agent Framework Team
日期: 2025-12-31
版本: 1.0.0
"""

import os
import yaml
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from dotenv import load_dotenv

# Agent Framework 核心模組
from agent_framework import Agent, AgentThread
from agent_framework.models import OpenAIModel
from agent_framework.workflow import (
    Workflow,
    WorkflowStep,
    WorkflowBuilder,
    StepResult,
    WorkflowContext,
)
from agent_framework.conditions import (
    Condition,
    AndCondition,
    OrCondition,
    CustomCondition,
)

# ============================================================================
# 1. 工作流基本概念
# ============================================================================

class StepStatus(str, Enum):
    """步驟狀態"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowStatus(str, Enum):
    """工作流狀態"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class StepConfig:
    """步驟配置"""
    name: str
    agent_name: str
    description: str
    inputs: Dict[str, Any]
    retry_count: int = 0
    timeout: Optional[int] = None
    on_success: Optional[str] = None
    on_failure: Optional[str] = None


# ============================================================================
# 2. YAML 工作流定義
# ============================================================================

def create_yaml_workflow_example():
    """
    創建 YAML 格式的工作流定義範例

    YAML 格式適合:
    - 非程式設計人員編輯
    - 版本控制
    - 可視化工具整合
    """
    workflow_yaml = """
# 內容創作工作流
name: content_creation_workflow
description: 自動化內容創作流程

# 全局配置
config:
  max_retries: 3
  timeout: 300
  on_error: continue

# Agent 定義
agents:
  - name: researcher
    role: 研究員
    instructions: 收集和分析資訊

  - name: writer
    role: 作家
    instructions: 撰寫高品質內容

  - name: editor
    role: 編輯
    instructions: 審核和改進內容

# 工作流步驟
steps:
  # 步驟 1: 主題研究
  - name: research_topic
    agent: researcher
    description: 研究主題並收集資料
    inputs:
      topic: ${workflow.input.topic}
      depth: comprehensive
    outputs:
      research_data: ${step.result}
    next: write_draft

  # 步驟 2: 撰寫草稿
  - name: write_draft
    agent: writer
    description: 根據研究資料撰寫草稿
    inputs:
      research: ${steps.research_topic.outputs.research_data}
      style: professional
    outputs:
      draft: ${step.result}
    next: review_draft

  # 步驟 3: 審核草稿
  - name: review_draft
    agent: editor
    description: 審核草稿並提供反饋
    inputs:
      content: ${steps.write_draft.outputs.draft}
    outputs:
      review_result: ${step.result}
      needs_revision: ${step.result.needs_revision}
    next:
      - condition: ${steps.review_draft.outputs.needs_revision}
        goto: revise_content
      - else: finalize_content

  # 步驟 4: 修訂內容 (條件執行)
  - name: revise_content
    agent: writer
    description: 根據反饋修訂內容
    inputs:
      original: ${steps.write_draft.outputs.draft}
      feedback: ${steps.review_draft.outputs.review_result}
    outputs:
      revised: ${step.result}
    next: review_draft  # 循環回審核

  # 步驟 5: 完成
  - name: finalize_content
    agent: editor
    description: 最終確認和格式化
    inputs:
      content: ${steps.write_draft.outputs.draft}
    outputs:
      final_content: ${step.result}
    """

    return yaml_load(workflow_yaml)


def yaml_load(yaml_str: str) -> Dict[str, Any]:
    """載入 YAML (模擬)"""
    # 在實際實作中,這裡會使用 yaml.safe_load()
    return {
        "name": "content_creation_workflow",
        "description": "自動化內容創作流程",
        "steps": [
            {"name": "research_topic", "agent": "researcher"},
            {"name": "write_draft", "agent": "writer"},
            {"name": "review_draft", "agent": "editor"},
        ]
    }


# ============================================================================
# 3. 程式化工作流建構
# ============================================================================

class WorkflowBuilderExample:
    """
    程式化工作流建構範例

    提供更靈活的工作流定義方式
    """

    def __init__(self, model: OpenAIModel):
        """初始化"""
        self.model = model
        self.builder = WorkflowBuilder()

    def create_simple_workflow(self) -> Workflow:
        """
        創建簡單的線性工作流

        步驟順序: A -> B -> C
        """
        print("\n建構簡單線性工作流:")

        # 創建 Agent
        agent_a = Agent(
            name="agent_a",
            model=self.model,
            instructions="執行步驟 A"
        )

        agent_b = Agent(
            name="agent_b",
            model=self.model,
            instructions="執行步驟 B"
        )

        agent_c = Agent(
            name="agent_c",
            model=self.model,
            instructions="執行步驟 C"
        )

        # 建構工作流
        workflow = (
            self.builder
            .add_step("step_a", agent_a, "執行第一步")
            .then("step_b", agent_b, "執行第二步")
            .then("step_c", agent_c, "執行第三步")
            .build()
        )

        print("   ✅ 步驟順序: step_a -> step_b -> step_c")

        return workflow

    def create_conditional_workflow(self) -> Workflow:
        """
        創建帶條件分支的工作流

        根據步驟結果決定下一步
        """
        print("\n建構條件分支工作流:")

        # 創建 Agent
        validator = Agent(
            name="validator",
            model=self.model,
            instructions="驗證輸入資料"
        )

        processor_a = Agent(
            name="processor_a",
            model=self.model,
            instructions="處理方式 A"
        )

        processor_b = Agent(
            name="processor_b",
            model=self.model,
            instructions="處理方式 B"
        )

        finalizer = Agent(
            name="finalizer",
            model=self.model,
            instructions="完成處理"
        )

        # 定義條件
        def is_type_a(context: WorkflowContext) -> bool:
            """檢查是否為類型 A"""
            result = context.get_step_result("validate")
            return result.get("type") == "A"

        # 建構工作流
        workflow = (
            self.builder
            .add_step("validate", validator, "驗證資料")
            .add_conditional_branch(
                condition=is_type_a,
                if_true="process_a",
                if_false="process_b"
            )
            .add_step("process_a", processor_a, "處理方式 A")
            .add_step("process_b", processor_b, "處理方式 B")
            .merge_branches("finalize", finalizer, "完成")
            .build()
        )

        print("   ✅ 條件分支: validate -> [process_a | process_b] -> finalize")

        return workflow

    def create_parallel_workflow(self) -> Workflow:
        """
        創建並行執行的工作流

        多個步驟同時執行,然後聚合結果
        """
        print("\n建構並行執行工作流:")

        # 創建 Agent
        task_a = Agent(name="task_a", model=self.model, instructions="任務 A")
        task_b = Agent(name="task_b", model=self.model, instructions="任務 B")
        task_c = Agent(name="task_c", model=self.model, instructions="任務 C")
        aggregator = Agent(name="aggregator", model=self.model, instructions="聚合結果")

        # 建構工作流
        workflow = (
            self.builder
            .add_parallel_steps([
                ("task_a", task_a, "並行任務 A"),
                ("task_b", task_b, "並行任務 B"),
                ("task_c", task_c, "並行任務 C"),
            ])
            .then("aggregate", aggregator, "聚合所有結果")
            .build()
        )

        print("   ✅ 並行執行: [task_a, task_b, task_c] -> aggregate")

        return workflow

    def create_loop_workflow(self) -> Workflow:
        """
        創建帶循環的工作流

        重複執行某些步驟直到滿足條件
        """
        print("\n建構循環工作流:")

        # 創建 Agent
        processor = Agent(
            name="processor",
            model=self.model,
            instructions="處理資料"
        )

        checker = Agent(
            name="checker",
            model=self.model,
            instructions="檢查是否完成"
        )

        # 定義循環條件
        def should_continue(context: WorkflowContext) -> bool:
            """檢查是否繼續循環"""
            result = context.get_step_result("check")
            iteration = context.get_variable("iteration", 0)
            return not result.get("completed") and iteration < 5

        # 建構工作流
        workflow = (
            self.builder
            .add_step("process", processor, "處理資料")
            .then("check", checker, "檢查結果")
            .add_loop(
                condition=should_continue,
                loop_to="process",
                max_iterations=5
            )
            .build()
        )

        print("   ✅ 循環: process -> check -> [繼續 | 結束]")

        return workflow


# ============================================================================
# 4. 工作流執行器
# ============================================================================

class WorkflowExecutor:
    """
    工作流執行器

    負責執行工作流並管理狀態
    """

    def __init__(self):
        """初始化執行器"""
        self.context = WorkflowContext()
        self.step_results: Dict[str, StepResult] = {}

    def execute(
        self,
        workflow: Workflow,
        inputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        執行工作流

        Args:
            workflow: 工作流定義
            inputs: 輸入參數

        Returns:
            工作流執行結果
        """
        print(f"\n🚀 開始執行工作流: {workflow.name}")
        print(f"   輸入參數: {inputs}")

        # 初始化上下文
        self.context.set_inputs(inputs)
        start_time = datetime.now()

        try:
            # 執行每個步驟
            for step in workflow.steps:
                self._execute_step(step)

            # 計算執行時間
            duration = (datetime.now() - start_time).total_seconds()

            result = {
                "status": WorkflowStatus.COMPLETED,
                "duration": duration,
                "steps_completed": len(workflow.steps),
                "outputs": self.context.get_outputs(),
            }

            print(f"\n✅ 工作流執行完成!")
            print(f"   總耗時: {duration:.2f} 秒")
            print(f"   完成步驟: {len(workflow.steps)}")

            return result

        except Exception as e:
            print(f"\n❌ 工作流執行失敗: {str(e)}")
            return {
                "status": WorkflowStatus.FAILED,
                "error": str(e),
            }

    def _execute_step(self, step: WorkflowStep):
        """執行單個步驟"""
        print(f"\n   執行步驟: {step.name}")
        print(f"   描述: {step.description}")

        # 模擬步驟執行
        result = StepResult(
            step_name=step.name,
            status=StepStatus.COMPLETED,
            output=f"步驟 {step.name} 的結果",
            duration=0.5,
        )

        self.step_results[step.name] = result
        self.context.set_step_result(step.name, result)

        print(f"   ✅ 完成")


# ============================================================================
# 5. 錯誤處理和重試
# ============================================================================

class RetryStrategy:
    """重試策略"""

    def __init__(
        self,
        max_retries: int = 3,
        backoff_multiplier: float = 2.0
    ):
        """
        初始化重試策略

        Args:
            max_retries: 最大重試次數
            backoff_multiplier: 退避倍數
        """
        self.max_retries = max_retries
        self.backoff_multiplier = backoff_multiplier

    def execute_with_retry(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        執行函數並在失敗時重試

        Args:
            func: 要執行的函數
            *args: 位置參數
            **kwargs: 關鍵字參數

        Returns:
            函數執行結果
        """
        for attempt in range(self.max_retries + 1):
            try:
                result = func(*args, **kwargs)
                if attempt > 0:
                    print(f"   ✅ 重試成功 (第 {attempt} 次)")
                return result

            except Exception as e:
                if attempt < self.max_retries:
                    wait_time = self.backoff_multiplier ** attempt
                    print(f"   ⚠️  失敗,{wait_time}秒後重試 (第 {attempt + 1}/{self.max_retries} 次)")
                    # time.sleep(wait_time)
                else:
                    print(f"   ❌ 達到最大重試次數,放棄")
                    raise


def demonstrate_error_handling():
    """示範錯誤處理和重試"""
    print("\n" + "="*70)
    print("🎯 錯誤處理和重試機制")
    print("="*70)

    retry_strategy = RetryStrategy(max_retries=3)

    # 模擬可能失敗的操作
    attempt_count = [0]

    def unreliable_operation():
        """不穩定的操作"""
        attempt_count[0] += 1
        if attempt_count[0] < 3:
            raise Exception(f"暫時性錯誤 (嘗試 {attempt_count[0]})")
        return "成功!"

    print("\n測試重試機制:")
    try:
        result = retry_strategy.execute_with_retry(unreliable_operation)
        print(f"   最終結果: {result}")
    except Exception as e:
        print(f"   最終失敗: {str(e)}")


# ============================================================================
# 6. 工作流監控
# ============================================================================

class WorkflowMonitor:
    """工作流監控器"""

    def __init__(self):
        """初始化監控器"""
        self.events: List[Dict[str, Any]] = []

    def log_event(
        self,
        event_type: str,
        step_name: str,
        details: Dict[str, Any]
    ):
        """記錄事件"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "step": step_name,
            "details": details,
        }
        self.events.append(event)

    def get_summary(self) -> Dict[str, Any]:
        """獲取執行摘要"""
        return {
            "total_events": len(self.events),
            "steps_executed": len(set(e["step"] for e in self.events)),
            "errors": [e for e in self.events if e["type"] == "error"],
        }

    def print_timeline(self):
        """輸出執行時間線"""
        print("\n📊 執行時間線:")
        for event in self.events:
            print(f"   [{event['timestamp']}] {event['type']}: {event['step']}")


# ============================================================================
# 7. 實際應用案例
# ============================================================================

def demonstrate_real_world_workflow():
    """示範實際應用工作流"""
    print("\n" + "="*70)
    print("🎯 實際案例: 客戶服務工作流")
    print("="*70)

    load_dotenv()
    model = OpenAIModel(
        model=os.getenv("OPENAI_MODEL", "gpt-4"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    builder = WorkflowBuilderExample(model)

    # 定義客戶服務工作流
    print("\n客戶服務工作流步驟:")
    print("   1. 接收客戶問題")
    print("   2. 分類問題類型")
    print("   3. 路由到適當的專員")
    print("   4. 處理問題")
    print("   5. 確認客戶滿意度")
    print("   6. 如果不滿意,升級處理")
    print("   7. 關閉工單")

    # 創建工作流 (簡化版)
    workflow = builder.create_conditional_workflow()

    # 執行工作流
    executor = WorkflowExecutor()
    inputs = {
        "customer_id": "C12345",
        "question": "產品無法正常啟動",
        "priority": "high",
    }

    result = executor.execute(workflow, inputs)


# ============================================================================
# 8. 主程式
# ============================================================================

def main():
    """主程式"""
    print("="*70)
    print("Microsoft Agent Framework - 工作流定義")
    print("="*70)

    load_dotenv()
    model = OpenAIModel(
        model=os.getenv("OPENAI_MODEL", "gpt-4"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    # 示範 YAML 工作流
    print("\n" + "="*70)
    print("🎯 範例 1: YAML 工作流定義")
    print("="*70)
    yaml_workflow = create_yaml_workflow_example()
    print(f"\n✅ 載入 YAML 工作流: {yaml_workflow['name']}")
    print(f"   步驟數: {len(yaml_workflow['steps'])}")

    # 示範程式化工作流建構
    print("\n" + "="*70)
    print("🎯 範例 2: 程式化工作流建構")
    print("="*70)
    builder = WorkflowBuilderExample(model)

    builder.create_simple_workflow()
    builder.create_conditional_workflow()
    builder.create_parallel_workflow()
    builder.create_loop_workflow()

    # 錯誤處理
    demonstrate_error_handling()

    # 實際案例
    demonstrate_real_world_workflow()

    print("\n" + "="*70)
    print("✅ 工作流定義示範完成!")
    print("="*70)

    print("\n💡 關鍵要點:")
    print("   1. 支援 YAML 和程式化兩種定義方式")
    print("   2. 提供條件分支、並行、循環等控制結構")
    print("   3. 內建錯誤處理和重試機制")
    print("   4. 可監控和追蹤工作流執行")
    print("   5. 適合複雜的業務流程自動化")

    print("\n📚 下一步:")
    print("   查看 06_MCP整合.py 學習 MCP 協議整合")


if __name__ == "__main__":
    main()

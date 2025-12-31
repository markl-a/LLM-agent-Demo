"""
Julep 任務定義和執行示例

這個模塊展示了 Julep 平台的任務系統功能。
包括任務定義、工作流編排、條件分支、循環和錯誤處理。

主要功能：
1. 聲明式任務定義
2. 工作流步驟編排
3. 條件分支執行
4. 循環和迭代
5. 錯誤處理和重試
6. 任務執行監控

作者：Julep 示例
日期：2025-12-31
"""

import time
import json
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from enum import Enum
import uuid


class StepType(Enum):
    """步驟類型枚舉"""
    PROMPT = "prompt"  # LLM 提示
    TOOL = "tool"  # 工具調用
    EVALUATE = "evaluate"  # 表達式求值
    WAIT = "wait"  # 等待
    PARALLEL = "parallel"  # 並行執行
    CONDITIONAL = "conditional"  # 條件分支
    LOOP = "loop"  # 循環


class ExecutionStatus(Enum):
    """執行狀態枚舉"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskStep:
    """任務步驟類

    表示工作流中的單個步驟。
    """

    def __init__(
        self,
        step_type: StepType,
        name: str,
        config: Dict[str, Any],
        timeout: Optional[int] = None,
        retry: int = 0
    ):
        """初始化步驟

        Args:
            step_type: 步驟類型
            name: 步驟名稱
            config: 步驟配置
            timeout: 超時時間（秒）
            retry: 重試次數
        """
        self.id = str(uuid.uuid4())
        self.step_type = step_type
        self.name = name
        self.config = config
        self.timeout = timeout
        self.retry = retry

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "id": self.id,
            "type": self.step_type.value,
            "name": self.name,
            "config": self.config,
            "timeout": self.timeout,
            "retry": self.retry
        }

    def __repr__(self) -> str:
        return f"TaskStep(type={self.step_type.value}, name={self.name})"


class Task:
    """任務類

    定義完整的任務，包含多個步驟和執行配置。
    """

    def __init__(
        self,
        task_id: str,
        name: str,
        description: str,
        agent_id: str,
        steps: Optional[List[TaskStep]] = None,
        metadata: Optional[Dict] = None
    ):
        """初始化任務

        Args:
            task_id: 任務 ID
            name: 任務名稱
            description: 任務描述
            agent_id: Agent ID
            steps: 任務步驟列表
            metadata: 元數據
        """
        self.id = task_id
        self.name = name
        self.description = description
        self.agent_id = agent_id
        self.steps = steps or []
        self.metadata = metadata or {}
        self.created_at = datetime.now()

    def add_step(self, step: TaskStep):
        """添加步驟"""
        self.steps.append(step)

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "agent_id": self.agent_id,
            "steps": [step.to_dict() for step in self.steps],
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }

    def __repr__(self) -> str:
        return f"Task(id={self.id}, name={self.name}, steps={len(self.steps)})"


class TaskExecution:
    """任務執行類

    表示任務的一次執行實例。
    """

    def __init__(
        self,
        execution_id: str,
        task_id: str,
        input_data: Dict[str, Any]
    ):
        """初始化執行

        Args:
            execution_id: 執行 ID
            task_id: 任務 ID
            input_data: 輸入數據
        """
        self.id = execution_id
        self.task_id = task_id
        self.input = input_data
        self.output: Optional[Any] = None
        self.status = ExecutionStatus.PENDING
        self.current_step = 0
        self.step_outputs: List[Any] = []
        self.errors: List[str] = []
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

    def start(self):
        """開始執行"""
        self.status = ExecutionStatus.RUNNING
        self.started_at = datetime.now()

    def complete(self, output: Any):
        """完成執行"""
        self.status = ExecutionStatus.COMPLETED
        self.output = output
        self.completed_at = datetime.now()

    def fail(self, error: str):
        """執行失敗"""
        self.status = ExecutionStatus.FAILED
        self.errors.append(error)
        self.completed_at = datetime.now()

    def add_step_output(self, output: Any):
        """添加步驟輸出"""
        self.step_outputs.append(output)

    def get_duration(self) -> Optional[float]:
        """獲取執行時長（秒）"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "id": self.id,
            "task_id": self.task_id,
            "status": self.status.value,
            "input": self.input,
            "output": self.output,
            "current_step": self.current_step,
            "step_outputs": self.step_outputs,
            "errors": self.errors,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration": self.get_duration()
        }


class TaskExecutor:
    """任務執行器

    負責執行任務的各個步驟。
    """

    def __init__(self):
        """初始化執行器"""
        self.tool_registry: Dict[str, Callable] = {}
        self._register_default_tools()

    def _register_default_tools(self):
        """註冊默認工具"""
        self.tool_registry["calculate"] = self._tool_calculate
        self.tool_registry["format_text"] = self._tool_format_text
        self.tool_registry["extract_data"] = self._tool_extract_data

    def _tool_calculate(self, expression: str) -> float:
        """計算工具"""
        try:
            result = eval(expression, {"__builtins__": {}}, {})
            print(f"  [TOOL] 計算: {expression} = {result}")
            return result
        except Exception as e:
            raise ValueError(f"計算錯誤: {e}")

    def _tool_format_text(self, text: str, format_type: str = "upper") -> str:
        """文本格式化工具"""
        if format_type == "upper":
            result = text.upper()
        elif format_type == "lower":
            result = text.lower()
        elif format_type == "title":
            result = text.title()
        else:
            result = text
        print(f"  [TOOL] 格式化文本: {format_type}")
        return result

    def _tool_extract_data(self, data: Dict, key: str) -> Any:
        """數據提取工具"""
        result = data.get(key)
        print(f"  [TOOL] 提取數據: {key} = {result}")
        return result

    def register_tool(self, name: str, func: Callable):
        """註冊自定義工具

        Args:
            name: 工具名稱
            func: 工具函數
        """
        self.tool_registry[name] = func
        print(f"[INFO] 註冊工具: {name}")

    def execute_step(
        self,
        step: TaskStep,
        context: Dict[str, Any]
    ) -> Any:
        """執行單個步驟

        Args:
            step: 任務步驟
            context: 執行上下文

        Returns:
            步驟輸出
        """
        print(f"\n[STEP] 執行步驟: {step.name} ({step.step_type.value})")

        if step.step_type == StepType.PROMPT:
            return self._execute_prompt(step, context)
        elif step.step_type == StepType.TOOL:
            return self._execute_tool(step, context)
        elif step.step_type == StepType.EVALUATE:
            return self._execute_evaluate(step, context)
        elif step.step_type == StepType.WAIT:
            return self._execute_wait(step, context)
        elif step.step_type == StepType.CONDITIONAL:
            return self._execute_conditional(step, context)
        else:
            raise ValueError(f"不支持的步驟類型: {step.step_type}")

    def _execute_prompt(self, step: TaskStep, context: Dict[str, Any]) -> str:
        """執行 LLM 提示步驟"""
        prompt = step.config.get("prompt", "")
        # 替換上下文變量
        for key, value in context.items():
            prompt = prompt.replace(f"{{{{{key}}}}}", str(value))

        print(f"  [PROMPT] {prompt}")

        # 模擬 LLM 響應
        time.sleep(0.5)
        response = f"基於提示 '{prompt}' 的模擬回復"
        print(f"  [RESPONSE] {response}")

        return response

    def _execute_tool(self, step: TaskStep, context: Dict[str, Any]) -> Any:
        """執行工具調用步驟"""
        tool_name = step.config.get("tool")
        arguments = step.config.get("arguments", {})

        # 替換參數中的上下文變量
        resolved_args = {}
        for key, value in arguments.items():
            if isinstance(value, str) and value == "_":
                # "_" 表示使用上一步的輸出
                resolved_args[key] = context.get("_last_output")
            elif isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
                # 從上下文獲取變量
                var_name = value[2:-2]
                resolved_args[key] = context.get(var_name)
            else:
                resolved_args[key] = value

        # 調用工具
        if tool_name not in self.tool_registry:
            raise ValueError(f"工具未註冊: {tool_name}")

        tool_func = self.tool_registry[tool_name]
        result = tool_func(**resolved_args)

        return result

    def _execute_evaluate(self, step: TaskStep, context: Dict[str, Any]) -> Any:
        """執行表達式求值步驟"""
        expression = step.config.get("expression", "")
        result = eval(expression, {"__builtins__": {}}, context)
        print(f"  [EVAL] {expression} = {result}")
        return result

    def _execute_wait(self, step: TaskStep, context: Dict[str, Any]) -> None:
        """執行等待步驟"""
        duration = step.config.get("duration", 1)
        print(f"  [WAIT] 等待 {duration} 秒")
        time.sleep(duration)
        return None

    def _execute_conditional(self, step: TaskStep, context: Dict[str, Any]) -> Any:
        """執行條件分支步驟"""
        condition = step.config.get("condition", "True")
        then_step = step.config.get("then")
        else_step = step.config.get("else")

        # 評估條件
        result = eval(condition, {"__builtins__": {}}, context)
        print(f"  [CONDITION] {condition} = {result}")

        if result and then_step:
            return self.execute_step(then_step, context)
        elif not result and else_step:
            return self.execute_step(else_step, context)

        return None

    def execute_task(
        self,
        task: Task,
        input_data: Dict[str, Any]
    ) -> TaskExecution:
        """執行完整任務

        Args:
            task: 任務對象
            input_data: 輸入數據

        Returns:
            執行結果
        """
        execution_id = f"exec_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        execution = TaskExecution(execution_id, task.id, input_data)

        print(f"\n{'='*60}")
        print(f"開始執行任務: {task.name}")
        print(f"執行 ID: {execution.id}")
        print(f"{'='*60}")

        execution.start()

        # 初始化上下文
        context = dict(input_data)
        context["_last_output"] = None

        try:
            # 執行每個步驟
            for i, step in enumerate(task.steps):
                execution.current_step = i

                # 執行步驟
                step_output = self.execute_step(step, context)

                # 保存輸出
                execution.add_step_output(step_output)
                context["_last_output"] = step_output

            # 任務完成
            final_output = context.get("_last_output")
            execution.complete(final_output)

            print(f"\n{'='*60}")
            print(f"任務執行完成")
            print(f"耗時: {execution.get_duration():.2f} 秒")
            print(f"{'='*60}")

        except Exception as e:
            error_msg = f"執行失敗: {str(e)}"
            execution.fail(error_msg)
            print(f"\n[ERROR] {error_msg}")

        return execution


class TaskBuilder:
    """任務構建器

    提供流暢的 API 來構建任務。
    """

    def __init__(self, name: str, agent_id: str):
        """初始化構建器"""
        self.task_id = f"task_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        self.name = name
        self.agent_id = agent_id
        self.description = ""
        self.steps: List[TaskStep] = []
        self.metadata: Dict[str, Any] = {}

    def with_description(self, description: str) -> 'TaskBuilder':
        """設置描述"""
        self.description = description
        return self

    def with_metadata(self, key: str, value: Any) -> 'TaskBuilder':
        """添加元數據"""
        self.metadata[key] = value
        return self

    def add_prompt_step(
        self,
        name: str,
        prompt: str,
        timeout: Optional[int] = None
    ) -> 'TaskBuilder':
        """添加提示步驟"""
        step = TaskStep(
            step_type=StepType.PROMPT,
            name=name,
            config={"prompt": prompt},
            timeout=timeout
        )
        self.steps.append(step)
        return self

    def add_tool_step(
        self,
        name: str,
        tool: str,
        arguments: Dict[str, Any],
        retry: int = 0
    ) -> 'TaskBuilder':
        """添加工具步驟"""
        step = TaskStep(
            step_type=StepType.TOOL,
            name=name,
            config={"tool": tool, "arguments": arguments},
            retry=retry
        )
        self.steps.append(step)
        return self

    def add_wait_step(self, name: str, duration: float) -> 'TaskBuilder':
        """添加等待步驟"""
        step = TaskStep(
            step_type=StepType.WAIT,
            name=name,
            config={"duration": duration}
        )
        self.steps.append(step)
        return self

    def add_conditional_step(
        self,
        name: str,
        condition: str,
        then_step: Optional[TaskStep] = None,
        else_step: Optional[TaskStep] = None
    ) -> 'TaskBuilder':
        """添加條件步驟"""
        step = TaskStep(
            step_type=StepType.CONDITIONAL,
            name=name,
            config={
                "condition": condition,
                "then": then_step,
                "else": else_step
            }
        )
        self.steps.append(step)
        return self

    def build(self) -> Task:
        """構建任務"""
        return Task(
            task_id=self.task_id,
            name=self.name,
            description=self.description,
            agent_id=self.agent_id,
            steps=self.steps,
            metadata=self.metadata
        )


def demo_simple_task():
    """簡單任務示例"""
    print("\n" + "="*60)
    print("示例 1: 簡單任務執行")
    print("="*60)

    # 構建任務
    task = (TaskBuilder("數據分析任務", "agent_001")
            .with_description("分析銷售數據並生成報告")
            .add_prompt_step("分析數據", "分析以下數據: {{data}}")
            .add_tool_step("格式化結果", "format_text", {"text": "_", "format_type": "title"})
            .build())

    # 執行任務
    executor = TaskExecutor()
    execution = executor.execute_task(
        task,
        {"data": "Q1銷售額: 100萬"}
    )

    print(f"\n執行狀態: {execution.status.value}")
    print(f"最終輸出: {execution.output}")


def demo_conditional_task():
    """條件分支任務示例"""
    print("\n" + "="*60)
    print("示例 2: 條件分支任務")
    print("="*60)

    # 構建任務
    task = (TaskBuilder("條件處理任務", "agent_002")
            .with_description("根據條件執行不同操作")
            .add_tool_step("提取數值", "extract_data", {"data": "{{input}}", "key": "value"})
            .add_tool_step("計算", "calculate", {"expression": "_ * 2"})
            .build())

    # 執行任務
    executor = TaskExecutor()
    execution = executor.execute_task(
        task,
        {"input": {"value": 42, "type": "number"}}
    )

    print(f"\n執行結果: {execution.output}")


def demo_multi_step_workflow():
    """多步驟工作流示例"""
    print("\n" + "="*60)
    print("示例 3: 多步驟工作流")
    print("="*60)

    # 構建複雜工作流
    task = (TaskBuilder("報告生成工作流", "agent_003")
            .with_description("收集數據、分析、生成報告")
            .add_prompt_step("收集數據", "收集 {{source}} 的數據")
            .add_wait_step("等待處理", 0.5)
            .add_prompt_step("數據分析", "分析數據並找出趨勢")
            .add_tool_step("格式化", "format_text", {"text": "最終報告", "format_type": "upper"})
            .add_prompt_step("生成摘要", "為報告生成執行摘要")
            .build())

    # 執行工作流
    executor = TaskExecutor()
    execution = executor.execute_task(
        task,
        {"source": "銷售系統"}
    )

    print(f"\n工作流步驟數: {len(execution.step_outputs)}")
    print(f"總耗時: {execution.get_duration():.2f} 秒")


def main():
    """主函數"""
    print("="*60)
    print("Julep 任務定義和執行示例")
    print("="*60)

    try:
        demo_simple_task()
        demo_conditional_task()
        demo_multi_step_workflow()

        print("\n" + "="*60)
        print("所有示例執行完成！")
        print("="*60)

    except Exception as e:
        print(f"\n[ERROR] 執行出錯: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

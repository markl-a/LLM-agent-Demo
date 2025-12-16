"""
DSPy Pipeline 構建範例
=====================

本範例展示如何構建複雜的 DSPy 處理流水線。

Pipeline 類型：
1. 線性流水線
2. 分支流水線
3. 循環流水線
4. 條件流水線

安裝依賴：
pip install dspy-ai
"""

import dspy
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

# ============================================================
# 配置
# ============================================================

turbo = dspy.OpenAI(model='gpt-3.5-turbo')
dspy.settings.configure(lm=turbo)


# ============================================================
# 1. 基礎 Pipeline 組件
# ============================================================

class PipelineStep(ABC):
    """流水線步驟基類"""

    @abstractmethod
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass


class DSPyStep(PipelineStep):
    """DSPy 模組步驟"""

    def __init__(self, name: str, module: dspy.Module, input_mapping: Dict[str, str] = None):
        self._name = name
        self.module = module
        self.input_mapping = input_mapping or {}

    @property
    def name(self) -> str:
        return self._name

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # 映射輸入
        mapped_inputs = {}
        for module_key, input_key in self.input_mapping.items():
            if input_key in inputs:
                mapped_inputs[module_key] = inputs[input_key]

        # 執行模組
        result = self.module(**mapped_inputs)

        # 收集輸出
        outputs = {}
        for field in dir(result):
            if not field.startswith('_'):
                outputs[field] = getattr(result, field)

        return outputs


class FunctionStep(PipelineStep):
    """函數步驟"""

    def __init__(self, name: str, func: Callable):
        self._name = name
        self.func = func

    @property
    def name(self) -> str:
        return self._name

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        return self.func(inputs)


# ============================================================
# 2. 線性流水線
# ============================================================

class LinearPipeline:
    """線性流水線"""

    def __init__(self, name: str = "linear_pipeline"):
        self.name = name
        self.steps: List[PipelineStep] = []

    def add_step(self, step: PipelineStep) -> 'LinearPipeline':
        """添加步驟"""
        self.steps.append(step)
        return self

    def execute(self, initial_inputs: Dict[str, Any]) -> Dict[str, Any]:
        """執行流水線"""
        current_data = initial_inputs.copy()

        for step in self.steps:
            print(f"執行步驟: {step.name}")
            step_outputs = step.execute(current_data)
            current_data.update(step_outputs)

        return current_data


# ============================================================
# 3. 分支流水線
# ============================================================

class BranchPipeline:
    """分支流水線"""

    def __init__(self, name: str = "branch_pipeline"):
        self.name = name
        self.branches: Dict[str, List[PipelineStep]] = {}
        self.router: Callable = None

    def add_branch(self, branch_name: str, steps: List[PipelineStep]) -> 'BranchPipeline':
        """添加分支"""
        self.branches[branch_name] = steps
        return self

    def set_router(self, router: Callable) -> 'BranchPipeline':
        """設置路由器"""
        self.router = router
        return self

    def execute(self, initial_inputs: Dict[str, Any]) -> Dict[str, Any]:
        """執行流水線"""
        # 路由到分支
        branch_name = self.router(initial_inputs)

        if branch_name not in self.branches:
            raise ValueError(f"未知分支: {branch_name}")

        print(f"路由到分支: {branch_name}")

        # 執行分支
        current_data = initial_inputs.copy()
        for step in self.branches[branch_name]:
            print(f"  執行步驟: {step.name}")
            step_outputs = step.execute(current_data)
            current_data.update(step_outputs)

        current_data['branch'] = branch_name
        return current_data


# ============================================================
# 4. 條件流水線
# ============================================================

@dataclass
class ConditionalStep:
    """條件步驟"""
    condition: Callable[[Dict[str, Any]], bool]
    step: PipelineStep
    else_step: Optional[PipelineStep] = None


class ConditionalPipeline:
    """條件流水線"""

    def __init__(self, name: str = "conditional_pipeline"):
        self.name = name
        self.steps: List[ConditionalStep] = []

    def add_conditional_step(
        self,
        condition: Callable[[Dict[str, Any]], bool],
        step: PipelineStep,
        else_step: PipelineStep = None
    ) -> 'ConditionalPipeline':
        """添加條件步驟"""
        self.steps.append(ConditionalStep(condition, step, else_step))
        return self

    def execute(self, initial_inputs: Dict[str, Any]) -> Dict[str, Any]:
        """執行流水線"""
        current_data = initial_inputs.copy()

        for cond_step in self.steps:
            if cond_step.condition(current_data):
                print(f"條件滿足，執行: {cond_step.step.name}")
                step_outputs = cond_step.step.execute(current_data)
            elif cond_step.else_step:
                print(f"條件不滿足，執行: {cond_step.else_step.name}")
                step_outputs = cond_step.else_step.execute(current_data)
            else:
                print("條件不滿足，跳過步驟")
                continue

            current_data.update(step_outputs)

        return current_data


# ============================================================
# 5. 循環流水線
# ============================================================

class LoopPipeline:
    """循環流水線"""

    def __init__(
        self,
        name: str = "loop_pipeline",
        max_iterations: int = 10,
        stop_condition: Callable[[Dict[str, Any], int], bool] = None
    ):
        self.name = name
        self.max_iterations = max_iterations
        self.stop_condition = stop_condition or (lambda data, i: False)
        self.steps: List[PipelineStep] = []

    def add_step(self, step: PipelineStep) -> 'LoopPipeline':
        """添加步驟"""
        self.steps.append(step)
        return self

    def execute(self, initial_inputs: Dict[str, Any]) -> Dict[str, Any]:
        """執行流水線"""
        current_data = initial_inputs.copy()
        iteration = 0

        while iteration < self.max_iterations:
            iteration += 1
            print(f"\n迭代 {iteration}:")

            # 檢查停止條件
            if self.stop_condition(current_data, iteration):
                print("達到停止條件")
                break

            # 執行所有步驟
            for step in self.steps:
                print(f"  執行步驟: {step.name}")
                step_outputs = step.execute(current_data)
                current_data.update(step_outputs)

        current_data['iterations'] = iteration
        return current_data


# ============================================================
# 6. 組合流水線
# ============================================================

class CompositePipeline:
    """組合流水線 - 支持嵌套"""

    def __init__(self, name: str = "composite_pipeline"):
        self.name = name
        self.components: List[Any] = []  # 可以是 Step 或 Pipeline

    def add(self, component: Any) -> 'CompositePipeline':
        """添加組件"""
        self.components.append(component)
        return self

    def execute(self, initial_inputs: Dict[str, Any]) -> Dict[str, Any]:
        """執行流水線"""
        current_data = initial_inputs.copy()

        for component in self.components:
            if isinstance(component, PipelineStep):
                print(f"執行步驟: {component.name}")
                step_outputs = component.execute(current_data)
            else:  # Pipeline
                print(f"執行子流水線: {component.name}")
                step_outputs = component.execute(current_data)

            current_data.update(step_outputs)

        return current_data


# ============================================================
# 7. 實用 DSPy 模組
# ============================================================

class ExtractSignature(dspy.Signature):
    """信息提取簽名"""
    text = dspy.InputField(desc="輸入文本")
    entities = dspy.OutputField(desc="提取的實體")


class SummarizeSignature(dspy.Signature):
    """摘要簽名"""
    text = dspy.InputField(desc="輸入文本")
    summary = dspy.OutputField(desc="摘要")


class ClassifySignature(dspy.Signature):
    """分類簽名"""
    text = dspy.InputField(desc="輸入文本")
    category = dspy.OutputField(desc="分類結果")


class ExtractModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.extract = dspy.Predict(ExtractSignature)

    def forward(self, text: str):
        return self.extract(text=text)


class SummarizeModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.summarize = dspy.Predict(SummarizeSignature)

    def forward(self, text: str):
        return self.summarize(text=text)


class ClassifyModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.classify = dspy.Predict(ClassifySignature)

    def forward(self, text: str):
        return self.classify(text=text)


# ============================================================
# 8. Pipeline 構建器
# ============================================================

class PipelineBuilder:
    """流水線構建器"""

    def __init__(self):
        self.pipeline = None
        self.pipeline_type = None

    def create_linear(self, name: str = "linear") -> 'PipelineBuilder':
        """創建線性流水線"""
        self.pipeline = LinearPipeline(name)
        self.pipeline_type = "linear"
        return self

    def create_branch(self, name: str = "branch") -> 'PipelineBuilder':
        """創建分支流水線"""
        self.pipeline = BranchPipeline(name)
        self.pipeline_type = "branch"
        return self

    def create_conditional(self, name: str = "conditional") -> 'PipelineBuilder':
        """創建條件流水線"""
        self.pipeline = ConditionalPipeline(name)
        self.pipeline_type = "conditional"
        return self

    def create_loop(self, name: str = "loop", max_iter: int = 10) -> 'PipelineBuilder':
        """創建循環流水線"""
        self.pipeline = LoopPipeline(name, max_iterations=max_iter)
        self.pipeline_type = "loop"
        return self

    def add_dspy_step(
        self,
        name: str,
        module: dspy.Module,
        input_mapping: Dict[str, str] = None
    ) -> 'PipelineBuilder':
        """添加 DSPy 步驟"""
        step = DSPyStep(name, module, input_mapping)
        self.pipeline.add_step(step)
        return self

    def add_function_step(self, name: str, func: Callable) -> 'PipelineBuilder':
        """添加函數步驟"""
        step = FunctionStep(name, func)
        self.pipeline.add_step(step)
        return self

    def build(self):
        """構建流水線"""
        return self.pipeline


# ============================================================
# 使用範例
# ============================================================

def example_linear_pipeline():
    """範例 1: 線性流水線"""
    print("=" * 50)
    print("範例 1: 線性流水線")
    print("=" * 50)

    # 創建流水線
    pipeline = LinearPipeline("text_processing")

    # 添加步驟
    pipeline.add_step(FunctionStep(
        "preprocess",
        lambda x: {"cleaned_text": x.get("text", "").strip().lower()}
    ))

    pipeline.add_step(FunctionStep(
        "tokenize",
        lambda x: {"tokens": x.get("cleaned_text", "").split()}
    ))

    pipeline.add_step(FunctionStep(
        "count",
        lambda x: {"word_count": len(x.get("tokens", []))}
    ))

    # 執行
    result = pipeline.execute({"text": "Hello World This Is A Test"})
    print(f"\n結果: {result}")


def example_branch_pipeline():
    """範例 2: 分支流水線"""
    print("\n" + "=" * 50)
    print("範例 2: 分支流水線")
    print("=" * 50)

    # 創建分支流水線
    pipeline = BranchPipeline("language_router")

    # 路由器
    def router(inputs):
        text = inputs.get("text", "")
        if any(c > '\u4e00' and c < '\u9fff' for c in text):
            return "chinese"
        return "english"

    pipeline.set_router(router)

    # 添加分支
    pipeline.add_branch("chinese", [
        FunctionStep("process_chinese", lambda x: {"language": "中文", "processed": True})
    ])

    pipeline.add_branch("english", [
        FunctionStep("process_english", lambda x: {"language": "English", "processed": True})
    ])

    # 測試
    result1 = pipeline.execute({"text": "Hello World"})
    print(f"英文結果: {result1}")

    result2 = pipeline.execute({"text": "你好世界"})
    print(f"中文結果: {result2}")


def example_conditional_pipeline():
    """範例 3: 條件流水線"""
    print("\n" + "=" * 50)
    print("範例 3: 條件流水線")
    print("=" * 50)

    pipeline = ConditionalPipeline("quality_check")

    # 條件步驟
    pipeline.add_conditional_step(
        condition=lambda x: len(x.get("text", "")) > 100,
        step=FunctionStep("summarize", lambda x: {"action": "summarized"}),
        else_step=FunctionStep("expand", lambda x: {"action": "expanded"})
    )

    # 測試
    short_text = {"text": "短文本"}
    long_text = {"text": "這是一段很長的文本" * 20}

    print(f"短文本結果: {pipeline.execute(short_text)}")
    print(f"長文本結果: {pipeline.execute(long_text)}")


def example_loop_pipeline():
    """範例 4: 循環流水線"""
    print("\n" + "=" * 50)
    print("範例 4: 循環流水線")
    print("=" * 50)

    pipeline = LoopPipeline(
        "refinement",
        max_iterations=5,
        stop_condition=lambda data, i: data.get("quality", 0) >= 0.9
    )

    # 模擬改進步驟
    def improve(inputs):
        current_quality = inputs.get("quality", 0)
        new_quality = min(current_quality + 0.3, 1.0)
        return {"quality": new_quality}

    pipeline.add_step(FunctionStep("improve", improve))

    result = pipeline.execute({"quality": 0.2})
    print(f"\n最終結果: {result}")


def example_builder():
    """範例 5: Pipeline 構建器"""
    print("\n" + "=" * 50)
    print("範例 5: Pipeline 構建器")
    print("=" * 50)

    builder = PipelineBuilder()

    pipeline = (
        builder
        .create_linear("my_pipeline")
        .add_function_step("step1", lambda x: {"step1": "done"})
        .add_function_step("step2", lambda x: {"step2": "done"})
        .add_function_step("step3", lambda x: {"step3": "done"})
        .build()
    )

    result = pipeline.execute({"input": "test"})
    print(f"結果: {result}")


def example_composite():
    """範例 6: 組合流水線"""
    print("\n" + "=" * 50)
    print("範例 6: 組合流水線")
    print("=" * 50)

    # 創建子流水線
    preprocess = LinearPipeline("preprocess")
    preprocess.add_step(FunctionStep("clean", lambda x: {"cleaned": True}))

    process = LinearPipeline("process")
    process.add_step(FunctionStep("analyze", lambda x: {"analyzed": True}))

    # 組合
    main = CompositePipeline("main")
    main.add(preprocess)
    main.add(process)
    main.add(FunctionStep("finalize", lambda x: {"finalized": True}))

    result = main.execute({"input": "test"})
    print(f"結果: {result}")


if __name__ == "__main__":
    print("DSPy Pipeline 構建範例\n")
    example_linear_pipeline()
    example_branch_pipeline()
    example_conditional_pipeline()
    example_loop_pipeline()
    example_builder()
    example_composite()

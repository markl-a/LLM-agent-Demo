"""
Atomic Agents 鏈式管道設計
==========================

本文件展示如何構建和使用 Agent 管道（Pipeline）。
管道允許將多個 Agent 串聯，形成複雜的工作流。

主要內容：
1. 線性管道
2. 條件分支管道
3. 並行執行管道
4. 動態管道
5. 錯誤處理和重試
6. 管道監控和日誌

作者：Atomic Agents 團隊
日期：2025-12-31
"""

from typing import Any, Dict, List, Optional, Callable, Union
from pydantic import BaseModel, Field
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import time
from abc import ABC, abstractmethod


# ============================================================================
# 第一部分：管道基礎架構
# ============================================================================

class PipelineStage(BaseModel):
    """管道階段"""
    name: str = Field(..., description="階段名稱")
    start_time: Optional[datetime] = Field(None, description="開始時間")
    end_time: Optional[datetime] = Field(None, description="結束時間")
    status: str = Field(default="pending", description="狀態")
    input_data: Optional[Any] = Field(None, description="輸入數據")
    output_data: Optional[Any] = Field(None, description="輸出數據")
    error: Optional[str] = Field(None, description="錯誤信息")

    class Config:
        arbitrary_types_allowed = True


class PipelineResult(BaseModel):
    """管道執行結果"""
    success: bool = Field(..., description="是否成功")
    stages: List[PipelineStage] = Field(..., description="各階段執行情況")
    final_output: Any = Field(None, description="最終輸出")
    total_time: float = Field(..., description="總執行時間（秒）")
    error: Optional[str] = Field(None, description="錯誤信息")

    class Config:
        arbitrary_types_allowed = True


class StageExecutor(ABC):
    """階段執行器基類"""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def execute(self, input_data: Any) -> Any:
        """執行階段邏輯"""
        pass

    def run(self, input_data: Any) -> PipelineStage:
        """運行階段"""
        stage = PipelineStage(name=self.name)
        stage.start_time = datetime.now()
        stage.input_data = input_data
        stage.status = "running"

        try:
            output = self.execute(input_data)
            stage.output_data = output
            stage.status = "completed"
            stage.end_time = datetime.now()
            return stage

        except Exception as e:
            stage.error = str(e)
            stage.status = "failed"
            stage.end_time = datetime.now()
            raise


# ============================================================================
# 第二部分：線性管道
# ============================================================================

class LinearPipeline:
    """
    線性管道

    按順序執行一系列階段。
    """

    def __init__(self, name: str):
        self.name = name
        self.stages: List[StageExecutor] = []

    def add_stage(self, stage: StageExecutor) -> 'LinearPipeline':
        """添加階段"""
        self.stages.append(stage)
        return self

    def execute(self, initial_input: Any) -> PipelineResult:
        """執行管道"""
        print(f"\n{'='*60}")
        print(f"執行線性管道: {self.name}")
        print(f"{'='*60}")

        start_time = time.time()
        stage_results = []
        current_data = initial_input

        for i, stage in enumerate(self.stages, 1):
            print(f"\n[階段 {i}/{len(self.stages)}] {stage.name}")

            try:
                stage_result = stage.run(current_data)
                stage_results.append(stage_result)
                current_data = stage_result.output_data

                print(f"  ✓ 完成")

            except Exception as e:
                print(f"  ✗ 失敗: {str(e)}")
                stage_results.append(stage_result)

                total_time = time.time() - start_time
                return PipelineResult(
                    success=False,
                    stages=stage_results,
                    final_output=None,
                    total_time=total_time,
                    error=f"階段 {stage.name} 失敗: {str(e)}"
                )

        total_time = time.time() - start_time
        print(f"\n{'='*60}")
        print(f"管道執行完成 (耗時: {total_time:.2f}秒)")
        print(f"{'='*60}")

        return PipelineResult(
            success=True,
            stages=stage_results,
            final_output=current_data,
            total_time=total_time
        )


# ============================================================================
# 第三部分：具體的階段執行器
# ============================================================================

class DataInput(BaseModel):
    """數據輸入"""
    content: str = Field(..., description="內容")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ClassificationStage(StageExecutor):
    """分類階段"""

    def __init__(self):
        super().__init__("分類")

    def execute(self, input_data: DataInput) -> Dict[str, Any]:
        """執行分類"""
        content = input_data.content.lower()

        # 簡單的分類邏輯
        if any(word in content for word in ['問題', '疑問', '為什麼']):
            category = 'question'
        elif any(word in content for word in ['建議', '應該', '推薦']):
            category = 'suggestion'
        elif any(word in content for word in ['問題', '錯誤', '故障']):
            category = 'issue'
        else:
            category = 'general'

        return {
            'category': category,
            'content': input_data.content,
            'confidence': 0.85
        }


class AnalysisStage(StageExecutor):
    """分析階段"""

    def __init__(self):
        super().__init__("分析")

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """執行分析"""
        category = input_data['category']
        content = input_data['content']

        # 基於類別的分析
        analysis = {
            'category': category,
            'content': content,
            'sentiment': 'neutral',
            'key_points': [],
            'priority': 'medium'
        }

        # 簡單的情感分析
        positive_words = ['好', '優秀', '棒', '感謝']
        negative_words = ['壞', '差', '問題', '錯誤']

        positive_count = sum(1 for word in positive_words if word in content)
        negative_count = sum(1 for word in negative_words if word in content)

        if positive_count > negative_count:
            analysis['sentiment'] = 'positive'
        elif negative_count > positive_count:
            analysis['sentiment'] = 'negative'

        # 提取關鍵點
        sentences = content.split('。')
        analysis['key_points'] = [s.strip() for s in sentences if s.strip()][:3]

        return analysis


class ResponseGenerationStage(StageExecutor):
    """響應生成階段"""

    def __init__(self):
        super().__init__("響應生成")

    def execute(self, input_data: Dict[str, Any]) -> str:
        """生成響應"""
        category = input_data['category']
        sentiment = input_data.get('sentiment', 'neutral')

        # 基於類別和情感生成響應
        templates = {
            'question': "感謝您的提問。讓我為您解答：",
            'suggestion': "感謝您的建議。我們會認真考慮：",
            'issue': "很抱歉您遇到了問題。讓我們來解決：",
            'general': "感謝您的反饋："
        }

        response = templates.get(category, templates['general'])

        if sentiment == 'negative':
            response = "我們對此深感抱歉。" + response

        return response


# ============================================================================
# 第四部分：條件分支管道
# ============================================================================

class ConditionalBranch:
    """條件分支"""

    def __init__(self, condition: Callable[[Any], bool], pipeline: LinearPipeline):
        self.condition = condition
        self.pipeline = pipeline


class ConditionalPipeline:
    """
    條件分支管道

    根據條件選擇不同的執行路徑。
    """

    def __init__(self, name: str):
        self.name = name
        self.branches: List[ConditionalBranch] = []
        self.default_pipeline: Optional[LinearPipeline] = None

    def add_branch(
        self,
        condition: Callable[[Any], bool],
        pipeline: LinearPipeline
    ) -> 'ConditionalPipeline':
        """添加條件分支"""
        self.branches.append(ConditionalBranch(condition, pipeline))
        return self

    def set_default(self, pipeline: LinearPipeline) -> 'ConditionalPipeline':
        """設置默認管道"""
        self.default_pipeline = pipeline
        return self

    def execute(self, input_data: Any) -> PipelineResult:
        """執行管道"""
        print(f"\n{'='*60}")
        print(f"執行條件管道: {self.name}")
        print(f"{'='*60}")

        # 檢查條件
        for i, branch in enumerate(self.branches, 1):
            if branch.condition(input_data):
                print(f"\n✓ 匹配分支 {i}: {branch.pipeline.name}")
                return branch.pipeline.execute(input_data)

        # 使用默認管道
        if self.default_pipeline:
            print(f"\n使用默認管道: {self.default_pipeline.name}")
            return self.default_pipeline.execute(input_data)

        # 沒有匹配的分支
        return PipelineResult(
            success=False,
            stages=[],
            final_output=None,
            total_time=0.0,
            error="沒有匹配的條件分支"
        )


# ============================================================================
# 第五部分：並行執行管道
# ============================================================================

class ParallelStage:
    """並行階段"""

    def __init__(self, name: str, stages: List[StageExecutor]):
        self.name = name
        self.stages = stages

    def execute(self, input_data: Any) -> Dict[str, Any]:
        """並行執行多個階段"""
        print(f"\n[並行執行] {self.name}")
        results = {}

        for stage in self.stages:
            print(f"  → {stage.name}")
            try:
                stage_result = stage.run(input_data)
                results[stage.name] = stage_result.output_data
            except Exception as e:
                results[stage.name] = {'error': str(e)}

        return results


# ============================================================================
# 第六部分：動態管道
# ============================================================================

class DynamicPipeline:
    """
    動態管道

    在執行過程中動態決定下一步。
    """

    def __init__(self, name: str):
        self.name = name
        self.stage_selector: Optional[Callable] = None
        self.available_stages: Dict[str, StageExecutor] = {}

    def add_stage(self, stage: StageExecutor) -> 'DynamicPipeline':
        """添加可用階段"""
        self.available_stages[stage.name] = stage
        return self

    def set_selector(self, selector: Callable) -> 'DynamicPipeline':
        """設置階段選擇器"""
        self.stage_selector = selector
        return self

    def execute(self, input_data: Any, max_steps: int = 10) -> PipelineResult:
        """執行動態管道"""
        print(f"\n{'='*60}")
        print(f"執行動態管道: {self.name}")
        print(f"{'='*60}")

        start_time = time.time()
        stage_results = []
        current_data = input_data
        step = 0

        while step < max_steps:
            step += 1

            # 選擇下一個階段
            next_stage_name = self.stage_selector(current_data, self.available_stages)

            if next_stage_name is None or next_stage_name == "END":
                print(f"\n管道結束於步驟 {step}")
                break

            if next_stage_name not in self.available_stages:
                error = f"未知階段: {next_stage_name}"
                print(f"\n✗ {error}")
                return PipelineResult(
                    success=False,
                    stages=stage_results,
                    final_output=None,
                    total_time=time.time() - start_time,
                    error=error
                )

            # 執行階段
            stage = self.available_stages[next_stage_name]
            print(f"\n[步驟 {step}] {stage.name}")

            try:
                stage_result = stage.run(current_data)
                stage_results.append(stage_result)
                current_data = stage_result.output_data
            except Exception as e:
                print(f"  ✗ 失敗: {str(e)}")
                return PipelineResult(
                    success=False,
                    stages=stage_results,
                    final_output=None,
                    total_time=time.time() - start_time,
                    error=str(e)
                )

        total_time = time.time() - start_time

        return PipelineResult(
            success=True,
            stages=stage_results,
            final_output=current_data,
            total_time=total_time
        )


# ============================================================================
# 第七部分：帶重試的管道
# ============================================================================

class RetryConfig(BaseModel):
    """重試配置"""
    max_attempts: int = Field(default=3, description="最大嘗試次數")
    delay: float = Field(default=1.0, description="重試延遲（秒）")
    backoff: float = Field(default=2.0, description="退避係數")


class RetryableStage(StageExecutor):
    """可重試的階段"""

    def __init__(self, stage: StageExecutor, retry_config: RetryConfig):
        super().__init__(f"Retryable-{stage.name}")
        self.stage = stage
        self.retry_config = retry_config

    def execute(self, input_data: Any) -> Any:
        """執行帶重試的階段"""
        delay = self.retry_config.delay

        for attempt in range(1, self.retry_config.max_attempts + 1):
            try:
                print(f"    嘗試 {attempt}/{self.retry_config.max_attempts}")
                return self.stage.execute(input_data)

            except Exception as e:
                if attempt == self.retry_config.max_attempts:
                    raise

                print(f"    失敗，{delay:.1f}秒後重試...")
                time.sleep(delay)
                delay *= self.retry_config.backoff


# ============================================================================
# 第八部分：使用示例
# ============================================================================

def example_linear_pipeline():
    """線性管道示例"""
    print("\n" + "="*60)
    print("示例 1: 線性管道")
    print("="*60)

    # 創建管道
    pipeline = LinearPipeline("內容處理管道")
    pipeline.add_stage(ClassificationStage())
    pipeline.add_stage(AnalysisStage())
    pipeline.add_stage(ResponseGenerationStage())

    # 執行管道
    input_data = DataInput(
        content="我有一個關於 Atomic Agents 的問題，它真的很好用！"
    )

    result = pipeline.execute(input_data)

    if result.success:
        print(f"\n最終輸出: {result.final_output}")
        print(f"總耗時: {result.total_time:.2f}秒")


def example_conditional_pipeline():
    """條件分支管道示例"""
    print("\n" + "="*60)
    print("示例 2: 條件分支管道")
    print("="*60)

    # 創建不同的處理管道
    question_pipeline = LinearPipeline("問題處理")
    question_pipeline.add_stage(AnalysisStage())
    question_pipeline.add_stage(ResponseGenerationStage())

    issue_pipeline = LinearPipeline("問題處理")
    issue_pipeline.add_stage(AnalysisStage())

    # 創建條件管道
    conditional = ConditionalPipeline("智能路由")
    conditional.add_branch(
        condition=lambda x: '問題' in x.content,
        pipeline=question_pipeline
    )
    conditional.add_branch(
        condition=lambda x: '錯誤' in x.content,
        pipeline=issue_pipeline
    )

    # 執行
    input_data = DataInput(content="這個功能有問題，無法正常工作。")
    result = conditional.execute(input_data)

    if result.success:
        print(f"\n處理完成")


def example_parallel_stages():
    """並行階段示例"""
    print("\n" + "="*60)
    print("示例 3: 並行執行")
    print("="*60)

    # 創建並行階段
    parallel = ParallelStage(
        "多維度分析",
        stages=[
            ClassificationStage(),
            AnalysisStage()
        ]
    )

    # 執行
    input_data = DataInput(content="Atomic Agents 框架非常強大！")

    # 先進行分類
    classifier = ClassificationStage()
    classified = classifier.run(input_data).output_data

    # 再並行執行
    results = parallel.execute(classified)
    print(f"\n並行執行結果: {list(results.keys())}")


def example_dynamic_pipeline():
    """動態管道示例"""
    print("\n" + "="*60)
    print("示例 4: 動態管道")
    print("="*60)

    def stage_selector(data: Any, available_stages: Dict) -> Optional[str]:
        """選擇下一個階段"""
        if isinstance(data, DataInput):
            return "分類"
        elif isinstance(data, dict):
            if 'category' in data and 'sentiment' not in data:
                return "分析"
            elif 'sentiment' in data:
                return "響應生成"
        return "END"

    # 創建動態管道
    pipeline = DynamicPipeline("自適應處理")
    pipeline.add_stage(ClassificationStage())
    pipeline.add_stage(AnalysisStage())
    pipeline.add_stage(ResponseGenerationStage())
    pipeline.set_selector(stage_selector)

    # 執行
    input_data = DataInput(content="請問如何使用這個框架？")
    result = pipeline.execute(input_data)

    if result.success:
        print(f"\n經過 {len(result.stages)} 個階段")
        print(f"最終輸出: {result.final_output}")


def example_retry_pipeline():
    """重試管道示例"""
    print("\n" + "="*60)
    print("示例 5: 帶重試的管道")
    print("="*60)

    # 創建重試配置
    retry_config = RetryConfig(max_attempts=3, delay=0.5, backoff=2.0)

    # 創建可重試的階段
    pipeline = LinearPipeline("容錯處理管道")
    pipeline.add_stage(
        RetryableStage(ClassificationStage(), retry_config)
    )
    pipeline.add_stage(AnalysisStage())

    # 執行
    input_data = DataInput(content="測試重試機制")
    result = pipeline.execute(input_data)

    print(f"\n執行{'成功' if result.success else '失敗'}")


def main():
    """主函數"""
    print("\n" + "="*60)
    print("Atomic Agents 鏈式管道設計")
    print("="*60)

    # 運行示例
    example_linear_pipeline()
    example_conditional_pipeline()
    example_parallel_stages()
    example_dynamic_pipeline()
    example_retry_pipeline()

    print("\n" + "="*60)
    print("所有示例運行完成！")
    print("="*60)


if __name__ == "__main__":
    main()

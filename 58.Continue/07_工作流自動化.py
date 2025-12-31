"""
Continue AI 編程助手 - 工作流自動化

這個文件展示了如何使用 Continue 自動化常見的編程工作流。
包括代碼生成、測試、文檔、部署等完整流程的自動化。

主要內容:
1. 工作流定義和執行
2. 代碼生成工作流
3. 測試自動化工作流
4. 文檔生成工作流
5. 代碼審查工作流
6. CI/CD 集成
7. 自定義工作流

Author: Continue Team
Date: 2025
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import time
from datetime import datetime


# =====================================================
# 第一部分: 工作流基礎定義
# =====================================================

class WorkflowStatus(Enum):
    """
    工作流狀態
    """
    PENDING = "pending"  # 等待中
    RUNNING = "running"  # 運行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失敗
    CANCELLED = "cancelled"  # 已取消


class StepStatus(Enum):
    """
    步驟狀態
    """
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowContext:
    """
    工作流上下文

    在工作流步驟之間共享數據
    """
    data: Dict[str, Any] = field(default_factory=dict)
    artifacts: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

    def set(self, key: str, value: Any):
        """設置數據"""
        self.data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """獲取數據"""
        return self.data.get(key, default)

    def add_artifact(self, name: str, content: Any):
        """添加產物"""
        self.artifacts[name] = content

    def add_error(self, error: str):
        """添加錯誤"""
        self.errors.append(error)


@dataclass
class StepResult:
    """
    步驟執行結果
    """
    success: bool
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    artifacts: Dict[str, Any] = field(default_factory=dict)


# =====================================================
# 第二部分: 工作流步驟定義
# =====================================================

class WorkflowStep(ABC):
    """
    工作流步驟抽象基類
    """

    def __init__(
        self,
        name: str,
        description: str,
        required: bool = True,
        retry_count: int = 0
    ):
        """
        初始化工作流步驟

        Args:
            name: 步驟名稱
            description: 步驟描述
            required: 是否必需(失敗時是否中止工作流)
            retry_count: 重試次數
        """
        self.name = name
        self.description = description
        self.required = required
        self.retry_count = retry_count
        self.status = StepStatus.PENDING

    @abstractmethod
    def execute(self, context: WorkflowContext) -> StepResult:
        """
        執行步驟

        Args:
            context: 工作流上下文

        Returns:
            步驟結果
        """
        pass

    def run(self, context: WorkflowContext) -> StepResult:
        """
        運行步驟(包含重試邏輯)

        Args:
            context: 工作流上下文

        Returns:
            步驟結果
        """
        self.status = StepStatus.RUNNING
        attempts = self.retry_count + 1

        for attempt in range(attempts):
            try:
                result = self.execute(context)

                if result.success:
                    self.status = StepStatus.COMPLETED
                    return result
                elif attempt < attempts - 1:
                    print(f"步驟 {self.name} 失敗,重試 {attempt + 1}/{self.retry_count}...")
                    time.sleep(1)
                else:
                    self.status = StepStatus.FAILED
                    return result

            except Exception as e:
                error_msg = f"步驟 {self.name} 執行異常: {str(e)}"
                context.add_error(error_msg)

                if attempt < attempts - 1:
                    print(f"{error_msg},重試 {attempt + 1}/{self.retry_count}...")
                    time.sleep(1)
                else:
                    self.status = StepStatus.FAILED
                    return StepResult(
                        success=False,
                        message=error_msg
                    )

        # 不應該到達這裡
        self.status = StepStatus.FAILED
        return StepResult(success=False, message="未知錯誤")


# =====================================================
# 第三部分: 代碼生成工作流步驟
# =====================================================

class GenerateCodeStep(WorkflowStep):
    """
    生成代碼步驟
    """

    def __init__(self, feature_description: str):
        """
        初始化

        Args:
            feature_description: 功能描述
        """
        super().__init__(
            name="生成代碼",
            description=f"根據需求生成代碼: {feature_description}"
        )
        self.feature_description = feature_description

    def execute(self, context: WorkflowContext) -> StepResult:
        """執行代碼生成"""
        print(f"正在生成代碼: {self.feature_description}")

        # 這裡應該調用 AI 模型生成代碼
        # 示例代碼
        generated_code = f"""
def {self._get_function_name()}():
    '''
    {self.feature_description}
    '''
    # TODO: 實現功能
    pass
"""

        context.set("generated_code", generated_code)
        context.add_artifact("code_file", generated_code)

        return StepResult(
            success=True,
            message="代碼生成成功",
            data={"code": generated_code}
        )

    def _get_function_name(self) -> str:
        """從描述生成函數名"""
        # 簡化實現
        return "new_feature"


class AddCommentsStep(WorkflowStep):
    """
    添加註釋步驟
    """

    def __init__(self):
        super().__init__(
            name="添加註釋",
            description="為生成的代碼添加詳細註釋"
        )

    def execute(self, context: WorkflowContext) -> StepResult:
        """執行添加註釋"""
        code = context.get("generated_code")
        if not code:
            return StepResult(
                success=False,
                message="未找到生成的代碼"
            )

        print("正在添加註釋...")

        # 這裡應該調用 AI 添加註釋
        commented_code = f'"""\n詳細的函數說明\n"""\n{code}'

        context.set("commented_code", commented_code)
        context.add_artifact("commented_code_file", commented_code)

        return StepResult(
            success=True,
            message="註釋添加成功"
        )


class GenerateTestsStep(WorkflowStep):
    """
    生成測試步驟
    """

    def __init__(self):
        super().__init__(
            name="生成測試",
            description="為代碼生成單元測試"
        )

    def execute(self, context: WorkflowContext) -> StepResult:
        """執行測試生成"""
        code = context.get("commented_code") or context.get("generated_code")
        if not code:
            return StepResult(
                success=False,
                message="未找到代碼"
            )

        print("正在生成測試...")

        # 生成測試代碼
        test_code = f"""
import pytest

def test_new_feature():
    '''測試新功能'''
    # TODO: 實現測試
    assert True
"""

        context.set("test_code", test_code)
        context.add_artifact("test_file", test_code)

        return StepResult(
            success=True,
            message="測試生成成功",
            data={"test_code": test_code}
        )


class RunTestsStep(WorkflowStep):
    """
    運行測試步驟
    """

    def __init__(self):
        super().__init__(
            name="運行測試",
            description="執行生成的測試",
            retry_count=1
        )

    def execute(self, context: WorkflowContext) -> StepResult:
        """執行測試運行"""
        test_code = context.get("test_code")
        if not test_code:
            return StepResult(
                success=False,
                message="未找到測試代碼"
            )

        print("正在運行測試...")

        # 這裡應該實際運行測試
        # 模擬測試結果
        test_passed = True

        if test_passed:
            return StepResult(
                success=True,
                message="測試通過",
                data={"test_results": "所有測試通過"}
            )
        else:
            return StepResult(
                success=False,
                message="測試失敗",
                data={"test_results": "部分測試失敗"}
            )


# =====================================================
# 第四部分: 文檔生成工作流步驟
# =====================================================

class GenerateDocumentationStep(WorkflowStep):
    """
    生成文檔步驟
    """

    def __init__(self, doc_type: str = "markdown"):
        """
        初始化

        Args:
            doc_type: 文檔類型(markdown, rst, html)
        """
        super().__init__(
            name="生成文檔",
            description=f"生成 {doc_type} 格式的文檔"
        )
        self.doc_type = doc_type

    def execute(self, context: WorkflowContext) -> StepResult:
        """執行文檔生成"""
        code = context.get("commented_code") or context.get("generated_code")
        if not code:
            return StepResult(
                success=False,
                message="未找到代碼"
            )

        print(f"正在生成 {self.doc_type} 文檔...")

        # 生成文檔
        if self.doc_type == "markdown":
            documentation = self._generate_markdown(code)
        else:
            documentation = "# 文檔\n\n待生成"

        context.add_artifact("documentation", documentation)

        return StepResult(
            success=True,
            message="文檔生成成功",
            data={"documentation": documentation}
        )

    def _generate_markdown(self, code: str) -> str:
        """生成 Markdown 文檔"""
        return f"""# API 文檔

## 功能說明

此模塊提供以下功能...

## 使用示例

```python
{code}
```

## API 參考

### 函數列表

- `function_name()`: 功能描述

"""


class GenerateREADMEStep(WorkflowStep):
    """
    生成 README 步驟
    """

    def __init__(self):
        super().__init__(
            name="生成 README",
            description="生成項目 README 文件"
        )

    def execute(self, context: WorkflowContext) -> StepResult:
        """執行 README 生成"""
        print("正在生成 README...")

        readme = """# 項目名稱

## 簡介

這個項目...

## 安裝

```bash
pip install -r requirements.txt
```

## 使用

```python
# 示例代碼
```

## 測試

```bash
pytest
```

## 貢獻

歡迎貢獻!

## 許可證

MIT License
"""

        context.add_artifact("README.md", readme)

        return StepResult(
            success=True,
            message="README 生成成功"
        )


# =====================================================
# 第五部分: 代碼審查工作流步驟
# =====================================================

class CodeReviewStep(WorkflowStep):
    """
    代碼審查步驟
    """

    def __init__(self):
        super().__init__(
            name="代碼審查",
            description="自動審查代碼質量",
            required=False
        )

    def execute(self, context: WorkflowContext) -> StepResult:
        """執行代碼審查"""
        code = context.get("commented_code") or context.get("generated_code")
        if not code:
            return StepResult(
                success=False,
                message="未找到代碼"
            )

        print("正在審查代碼...")

        # 執行代碼審查
        review_result = {
            "quality_score": 85,
            "issues": [
                "建議添加更多錯誤處理",
                "考慮使用類型註解"
            ],
            "suggestions": [
                "可以提取重複代碼為函數",
                "添加更多測試用例"
            ]
        }

        context.set("review_result", review_result)

        return StepResult(
            success=True,
            message="代碼審查完成",
            data=review_result
        )


class ApplyLinterStep(WorkflowStep):
    """
    應用代碼檢查工具步驟
    """

    def __init__(self, linter: str = "pylint"):
        """
        初始化

        Args:
            linter: 檢查工具名稱
        """
        super().__init__(
            name=f"運行 {linter}",
            description=f"使用 {linter} 檢查代碼",
            required=False
        )
        self.linter = linter

    def execute(self, context: WorkflowContext) -> StepResult:
        """執行代碼檢查"""
        print(f"正在運行 {self.linter}...")

        # 這裡應該實際運行 linter
        # 模擬結果
        linter_result = {
            "score": 9.5,
            "warnings": 2,
            "errors": 0
        }

        context.set(f"{self.linter}_result", linter_result)

        return StepResult(
            success=True,
            message=f"{self.linter} 檢查完成",
            data=linter_result
        )


# =====================================================
# 第六部分: Git 操作步驟
# =====================================================

class CreateGitBranchStep(WorkflowStep):
    """
    創建 Git 分支步驟
    """

    def __init__(self, branch_name: str):
        """
        初始化

        Args:
            branch_name: 分支名稱
        """
        super().__init__(
            name="創建 Git 分支",
            description=f"創建新分支: {branch_name}"
        )
        self.branch_name = branch_name

    def execute(self, context: WorkflowContext) -> StepResult:
        """執行分支創建"""
        print(f"正在創建分支: {self.branch_name}")

        # 這裡應該執行 git checkout -b
        # 模擬成功
        context.set("branch_name", self.branch_name)

        return StepResult(
            success=True,
            message=f"分支 {self.branch_name} 創建成功"
        )


class CommitChangesStep(WorkflowStep):
    """
    提交更改步驟
    """

    def __init__(self, commit_message: str):
        """
        初始化

        Args:
            commit_message: 提交消息
        """
        super().__init__(
            name="提交更改",
            description="提交代碼更改到 Git"
        )
        self.commit_message = commit_message

    def execute(self, context: WorkflowContext) -> StepResult:
        """執行提交"""
        print(f"正在提交更改: {self.commit_message}")

        # 這裡應該執行 git add 和 git commit
        # 模擬成功
        return StepResult(
            success=True,
            message="更改已提交"
        )


# =====================================================
# 第七部分: 工作流定義
# =====================================================

class Workflow:
    """
    工作流

    編排多個步驟按順序執行
    """

    def __init__(self, name: str, description: str):
        """
        初始化工作流

        Args:
            name: 工作流名稱
            description: 工作流描述
        """
        self.name = name
        self.description = description
        self.steps: List[WorkflowStep] = []
        self.status = WorkflowStatus.PENDING
        self.context = WorkflowContext()
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None

    def add_step(self, step: WorkflowStep):
        """
        添加步驟

        Args:
            step: 工作流步驟
        """
        self.steps.append(step)

    def execute(self) -> bool:
        """
        執行工作流

        Returns:
            是否執行成功
        """
        self.status = WorkflowStatus.RUNNING
        self.start_time = datetime.now()

        print(f"\n{'='*60}")
        print(f"開始執行工作流: {self.name}")
        print(f"描述: {self.description}")
        print(f"{'='*60}\n")

        for i, step in enumerate(self.steps, 1):
            print(f"\n[步驟 {i}/{len(self.steps)}] {step.name}")
            print(f"描述: {step.description}")

            result = step.run(self.context)

            if result.success:
                print(f"✓ {result.message}")

                # 合併產物
                for name, content in result.artifacts.items():
                    self.context.add_artifact(name, content)
            else:
                print(f"✗ {result.message}")

                if step.required:
                    print(f"\n工作流失敗: 必需步驟 '{step.name}' 執行失敗")
                    self.status = WorkflowStatus.FAILED
                    self.end_time = datetime.now()
                    return False
                else:
                    print(f"步驟 '{step.name}' 失敗但非必需,繼續執行")

        self.status = WorkflowStatus.COMPLETED
        self.end_time = datetime.now()

        print(f"\n{'='*60}")
        print(f"工作流執行完成: {self.name}")
        print(f"耗時: {self.end_time - self.start_time}")
        print(f"{'='*60}\n")

        return True

    def get_summary(self) -> Dict[str, Any]:
        """
        獲取工作流摘要

        Returns:
            摘要信息
        """
        completed_steps = sum(
            1 for step in self.steps
            if step.status == StepStatus.COMPLETED
        )

        return {
            "name": self.name,
            "status": self.status.value,
            "total_steps": len(self.steps),
            "completed_steps": completed_steps,
            "start_time": str(self.start_time),
            "end_time": str(self.end_time),
            "duration": str(self.end_time - self.start_time) if self.end_time else None,
            "artifacts": list(self.context.artifacts.keys()),
            "errors": self.context.errors
        }


# =====================================================
# 第八部分: 預定義工作流
# =====================================================

class WorkflowTemplates:
    """
    工作流模板

    提供常用的工作流模板
    """

    @staticmethod
    def create_feature_workflow(feature_description: str) -> Workflow:
        """
        創建功能開發工作流

        Args:
            feature_description: 功能描述

        Returns:
            工作流對象
        """
        workflow = Workflow(
            name="功能開發工作流",
            description=f"開發新功能: {feature_description}"
        )

        # 添加步驟
        workflow.add_step(GenerateCodeStep(feature_description))
        workflow.add_step(AddCommentsStep())
        workflow.add_step(GenerateTestsStep())
        workflow.add_step(RunTestsStep())
        workflow.add_step(CodeReviewStep())
        workflow.add_step(GenerateDocumentationStep())

        return workflow

    @staticmethod
    def create_documentation_workflow() -> Workflow:
        """
        創建文檔生成工作流

        Returns:
            工作流對象
        """
        workflow = Workflow(
            name="文檔生成工作流",
            description="為項目生成完整文檔"
        )

        workflow.add_step(GenerateDocumentationStep())
        workflow.add_step(GenerateREADMEStep())

        return workflow

    @staticmethod
    def create_ci_workflow() -> Workflow:
        """
        創建 CI 工作流

        Returns:
            工作流對象
        """
        workflow = Workflow(
            name="持續集成工作流",
            description="運行測試和代碼檢查"
        )

        workflow.add_step(RunTestsStep())
        workflow.add_step(ApplyLinterStep("pylint"))
        workflow.add_step(ApplyLinterStep("mypy"))
        workflow.add_step(CodeReviewStep())

        return workflow


# =====================================================
# 第九部分: 使用示例
# =====================================================

def feature_development_example():
    """
    功能開發工作流示例
    """
    print("示例 1: 功能開發工作流")

    # 創建工作流
    workflow = WorkflowTemplates.create_feature_workflow(
        "實現用戶認證功能"
    )

    # 執行工作流
    success = workflow.execute()

    # 顯示摘要
    summary = workflow.get_summary()
    print("\n工作流摘要:")
    print(json.dumps(summary, indent=2, ensure_ascii=False))

    # 顯示產物
    print("\n生成的產物:")
    for name in workflow.context.artifacts.keys():
        print(f"  - {name}")


def documentation_workflow_example():
    """
    文檔生成工作流示例
    """
    print("\n" + "="*60)
    print("示例 2: 文檔生成工作流")

    workflow = WorkflowTemplates.create_documentation_workflow()
    workflow.execute()


def custom_workflow_example():
    """
    自定義工作流示例
    """
    print("\n" + "="*60)
    print("示例 3: 自定義工作流")

    # 創建自定義工作流
    workflow = Workflow(
        name="自定義代碼發布工作流",
        description="生成代碼、測試、審查並提交"
    )

    # 添加自定義步驟序列
    workflow.add_step(CreateGitBranchStep("feature/new-feature"))
    workflow.add_step(GenerateCodeStep("新功能實現"))
    workflow.add_step(GenerateTestsStep())
    workflow.add_step(RunTestsStep())
    workflow.add_step(CodeReviewStep())
    workflow.add_step(CommitChangesStep("feat: 添加新功能"))

    # 執行
    workflow.execute()

    # 顯示摘要
    print("\n" + json.dumps(workflow.get_summary(), indent=2, ensure_ascii=False))


def main():
    """
    主函數
    """
    print("Continue - 工作流自動化\n")

    feature_development_example()
    documentation_workflow_example()
    custom_workflow_example()

    print("\n" + "="*60)
    print("所有示例運行完成!")
    print("="*60)


if __name__ == "__main__":
    main()

"""
Agent-S 多步任務模組

此模組展示 Agent-S 處理複雜多步驟任務的能力：
1. 任務規劃 - 將複雜目標分解為步驟序列
2. 上下文管理 - 在多步驟間保持上下文信息
3. 錯誤處理 - 處理中間步驟的失敗
4. 狀態恢復 - 從中斷點恢復任務執行

Agent-S 能夠執行需要跨多個應用和領域的端到端任務。
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Callable
from enum import Enum
from datetime import datetime
import time
import json


class StepStatus(Enum):
    """步驟狀態"""
    PENDING = "待執行"
    RUNNING = "執行中"
    COMPLETED = "已完成"
    FAILED = "失敗"
    SKIPPED = "已跳過"


class TaskComplexity(Enum):
    """任務複雜度"""
    SIMPLE = "簡單"
    MODERATE = "中等"
    COMPLEX = "複雜"
    VERY_COMPLEX = "非常複雜"


@dataclass
class StepResult:
    """步驟執行結果"""
    success: bool
    output: Any
    error_message: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskStep:
    """
    任務步驟

    表示多步任務中的一個步驟
    """
    step_id: str
    name: str
    description: str
    action: Callable  # 執行函數
    params: Dict[str, Any] = field(default_factory=dict)
    status: StepStatus = StepStatus.PENDING
    result: Optional[StepResult] = None
    dependencies: List[str] = field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3

    def can_execute(self, completed_steps: set) -> bool:
        """檢查是否可以執行"""
        if self.status != StepStatus.PENDING:
            return False
        return all(dep in completed_steps for dep in self.dependencies)

    def execute(self, context: Dict[str, Any]) -> StepResult:
        """執行步驟"""
        self.status = StepStatus.RUNNING

        start_time = time.time()

        try:
            # 執行操作
            output = self.action(context, **self.params)

            execution_time = time.time() - start_time

            self.result = StepResult(
                success=True,
                output=output,
                execution_time=execution_time
            )

            self.status = StepStatus.COMPLETED

        except Exception as e:
            execution_time = time.time() - start_time

            self.result = StepResult(
                success=False,
                output=None,
                error_message=str(e),
                execution_time=execution_time
            )

            self.status = StepStatus.FAILED

        return self.result


@dataclass
class MultiStepTask:
    """
    多步任務

    包含多個有序步驟的複雜任務
    """
    task_id: str
    name: str
    description: str
    steps: List[TaskStep] = field(default_factory=list)
    complexity: TaskComplexity = TaskComplexity.SIMPLE
    context: Dict[str, Any] = field(default_factory=dict)
    checkpoint_enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def add_step(self, step: TaskStep):
        """添加步驟"""
        self.steps.append(step)

    def get_progress(self) -> float:
        """獲取進度百分比"""
        if not self.steps:
            return 0.0

        completed = sum(1 for s in self.steps if s.status == StepStatus.COMPLETED)
        return completed / len(self.steps)

    def get_total_time(self) -> float:
        """獲取總執行時間"""
        if not self.started_at:
            return 0.0

        end_time = self.completed_at or datetime.now()
        return (end_time - self.started_at).total_seconds()


class TaskExecutor:
    """
    任務執行器

    執行多步驟任務並管理狀態
    """

    def __init__(self):
        self.current_task: Optional[MultiStepTask] = None
        self.completed_steps: set = set()
        self.checkpoints: Dict[str, Dict] = {}

    def execute(self, task: MultiStepTask) -> bool:
        """執行任務"""
        print("\n" + "="*60)
        print(f"開始執行任務: {task.name}")
        print(f"複雜度: {task.complexity.value}")
        print(f"步驟數: {len(task.steps)}")
        print("="*60)

        self.current_task = task
        self.completed_steps.clear()

        task.started_at = datetime.now()

        # 執行所有步驟
        for i, step in enumerate(task.steps, 1):
            print(f"\n[{i}/{len(task.steps)}] {step.name}")
            print(f"描述: {step.description}")

            # 檢查依賴
            if not step.can_execute(self.completed_steps):
                print(f"⏸ 跳過（等待依賴）")
                step.status = StepStatus.SKIPPED
                continue

            # 執行步驟
            result = step.execute(task.context)

            # 顯示結果
            if result.success:
                print(f"✓ 完成 ({result.execution_time:.2f}秒)")
                self.completed_steps.add(step.step_id)

                # 更新上下文
                if result.output:
                    task.context[f"step_{step.step_id}_output"] = result.output

                # 創建檢查點
                if task.checkpoint_enabled:
                    self._create_checkpoint(task, step)

            else:
                print(f"✗ 失敗: {result.error_message}")

                # 重試邏輯
                if step.retry_count < step.max_retries:
                    step.retry_count += 1
                    step.status = StepStatus.PENDING
                    print(f"🔄 重試 ({step.retry_count}/{step.max_retries})")
                    # 重新執行（簡化處理）
                    time.sleep(0.5)
                    continue
                else:
                    print("❌ 任務失敗")
                    return False

        task.completed_at = datetime.now()

        # 顯示總結
        self._print_summary(task)

        return True

    def _create_checkpoint(self, task: MultiStepTask, step: TaskStep):
        """創建檢查點"""
        checkpoint = {
            "task_id": task.task_id,
            "step_id": step.step_id,
            "completed_steps": list(self.completed_steps),
            "context": task.context.copy(),
            "timestamp": datetime.now().isoformat()
        }

        self.checkpoints[f"{task.task_id}_{step.step_id}"] = checkpoint

    def restore_from_checkpoint(self, task: MultiStepTask, checkpoint_key: str) -> bool:
        """從檢查點恢復"""
        if checkpoint_key not in self.checkpoints:
            print(f"檢查點不存在: {checkpoint_key}")
            return False

        checkpoint = self.checkpoints[checkpoint_key]

        print(f"\n從檢查點恢復: {checkpoint_key}")
        print(f"時間: {checkpoint['timestamp']}")

        # 恢復狀態
        self.current_task = task
        self.completed_steps = set(checkpoint['completed_steps'])
        task.context = checkpoint['context'].copy()

        # 更新步驟狀態
        for step in task.steps:
            if step.step_id in self.completed_steps:
                step.status = StepStatus.COMPLETED

        print(f"已恢復 {len(self.completed_steps)} 個已完成步驟")

        return True

    def _print_summary(self, task: MultiStepTask):
        """打印任務總結"""
        print("\n" + "="*60)
        print("任務執行總結")
        print("="*60)

        total_steps = len(task.steps)
        completed = sum(1 for s in task.steps if s.status == StepStatus.COMPLETED)
        failed = sum(1 for s in task.steps if s.status == StepStatus.FAILED)

        print(f"任務名稱: {task.name}")
        print(f"總步驟數: {total_steps}")
        print(f"已完成: {completed}")
        print(f"失敗: {failed}")
        print(f"進度: {task.get_progress():.1%}")
        print(f"總時間: {task.get_total_time():.2f}秒")

        if failed == 0:
            print("\n✓ 任務成功完成！")
        else:
            print("\n✗ 任務部分失敗")


# ========== 任務工廠函數 ==========

def 創建數據分析任務() -> MultiStepTask:
    """創建數據分析任務"""

    def 下載數據(ctx, source):
        print(f"  從 {source} 下載數據...")
        time.sleep(0.3)
        return {"records": 1000, "format": "csv"}

    def 清洗數據(ctx):
        print(f"  清洗數據...")
        time.sleep(0.3)
        return {"clean_records": 950}

    def 分析數據(ctx, analysis_type):
        print(f"  執行 {analysis_type} 分析...")
        time.sleep(0.4)
        return {"insights": ["洞察1", "洞察2"]}

    def 生成報告(ctx):
        print(f"  生成報告...")
        time.sleep(0.3)
        return {"report_path": "/reports/analysis_2024.pdf"}

    task = MultiStepTask(
        task_id="data_analysis_001",
        name="數據分析流程",
        description="完整的數據分析工作流",
        complexity=TaskComplexity.MODERATE
    )

    task.add_step(TaskStep("step1", "下載數據", "從數據源下載原始數據", 下載數據,
                          {"source": "database"}))
    task.add_step(TaskStep("step2", "數據清洗", "清洗和預處理數據", 清洗數據,
                          dependencies=["step1"]))
    task.add_step(TaskStep("step3", "統計分析", "執行統計分析", 分析數據,
                          {"analysis_type": "統計"}, dependencies=["step2"]))
    task.add_step(TaskStep("step4", "生成報告", "創建分析報告", 生成報告,
                          dependencies=["step3"]))

    return task


def 創建電商購物任務() -> MultiStepTask:
    """創建電商購物任務"""

    def 搜索商品(ctx, keyword):
        print(f"  搜索: {keyword}")
        time.sleep(0.2)
        return {"results": ["商品A", "商品B", "商品C"]}

    def 比較價格(ctx):
        print(f"  比較價格...")
        time.sleep(0.2)
        return {"best_price": "商品A - $99"}

    def 加入購物車(ctx, product):
        print(f"  添加 {product} 到購物車")
        time.sleep(0.1)
        return {"cart_items": 1}

    def 填寫地址(ctx, address):
        print(f"  填寫配送地址: {address}")
        time.sleep(0.1)
        return {"address_id": "addr_123"}

    def 選擇支付(ctx, method):
        print(f"  選擇支付方式: {method}")
        time.sleep(0.1)
        return {"payment_ready": True}

    def 確認訂單(ctx):
        print(f"  確認並提交訂單")
        time.sleep(0.2)
        return {"order_id": "ORD-2024-001"}

    task = MultiStepTask(
        task_id="shopping_001",
        name="在線購物流程",
        description="從搜索到下單的完整購物流程",
        complexity=TaskComplexity.COMPLEX
    )

    task.add_step(TaskStep("search", "搜索商品", "搜索目標商品", 搜索商品,
                          {"keyword": "筆記本電腦"}))
    task.add_step(TaskStep("compare", "比較價格", "比較不同商家的價格", 比較價格,
                          dependencies=["search"]))
    task.add_step(TaskStep("add_cart", "加入購物車", "添加商品到購物車", 加入購物車,
                          {"product": "商品A"}, dependencies=["compare"]))
    task.add_step(TaskStep("address", "填寫地址", "填寫配送地址", 填寫地址,
                          {"address": "台北市信義區"}, dependencies=["add_cart"]))
    task.add_step(TaskStep("payment", "選擇支付", "選擇支付方式", 選擇支付,
                          {"method": "信用卡"}, dependencies=["address"]))
    task.add_step(TaskStep("confirm", "確認訂單", "確認並提交訂單", 確認訂單,
                          dependencies=["payment"]))

    return task


def 創建內容創作任務() -> MultiStepTask:
    """創建內容創作任務"""

    def 研究主題(ctx, topic):
        print(f"  研究主題: {topic}")
        time.sleep(0.3)
        return {"sources": 5, "notes": "研究筆記..."}

    def 起草大綱(ctx):
        print(f"  創建內容大綱")
        time.sleep(0.2)
        return {"outline": ["引言", "正文", "結論"]}

    def 撰寫內容(ctx):
        print(f"  撰寫文章內容")
        time.sleep(0.4)
        return {"word_count": 2000}

    def 添加圖片(ctx):
        print(f"  添加配圖")
        time.sleep(0.2)
        return {"images": 3}

    def 校對編輯(ctx):
        print(f"  校對和編輯")
        time.sleep(0.3)
        return {"corrections": 12}

    def 發布內容(ctx, platform):
        print(f"  發布到 {platform}")
        time.sleep(0.2)
        return {"post_url": f"https://{platform}.com/post/123"}

    task = MultiStepTask(
        task_id="content_creation_001",
        name="博客文章創作",
        description="從研究到發布的內容創作流程",
        complexity=TaskComplexity.COMPLEX
    )

    task.add_step(TaskStep("research", "研究主題", "收集資料和信息", 研究主題,
                          {"topic": "AI 技術趨勢"}))
    task.add_step(TaskStep("outline", "創建大綱", "規劃文章結構", 起草大綱,
                          dependencies=["research"]))
    task.add_step(TaskStep("write", "撰寫內容", "撰寫文章內容", 撰寫內容,
                          dependencies=["outline"]))
    task.add_step(TaskStep("images", "添加圖片", "插入相關圖片", 添加圖片,
                          dependencies=["write"]))
    task.add_step(TaskStep("proofread", "校對編輯", "檢查和修正錯誤", 校對編輯,
                          dependencies=["write"]))
    task.add_step(TaskStep("publish", "發布內容", "發布到平台", 發布內容,
                          {"platform": "blog"}, dependencies=["images", "proofread"]))

    return task


def 創建項目部署任務() -> MultiStepTask:
    """創建項目部署任務"""

    def 代碼審查(ctx):
        print(f"  執行代碼審查")
        time.sleep(0.2)
        return {"issues": 0, "approved": True}

    def 運行測試(ctx):
        print(f"  運行測試套件")
        time.sleep(0.4)
        return {"tests_passed": 145, "tests_failed": 0}

    def 構建項目(ctx):
        print(f"  構建生產版本")
        time.sleep(0.5)
        return {"build_id": "build_2024_001"}

    def 部署到測試環境(ctx):
        print(f"  部署到測試環境")
        time.sleep(0.3)
        return {"test_url": "https://test.example.com"}

    def 集成測試(ctx):
        print(f"  執行集成測試")
        time.sleep(0.3)
        return {"all_passed": True}

    def 部署到生產環境(ctx):
        print(f"  部署到生產環境")
        time.sleep(0.4)
        return {"prod_url": "https://example.com"}

    def 健康檢查(ctx):
        print(f"  執行健康檢查")
        time.sleep(0.2)
        return {"status": "healthy"}

    task = MultiStepTask(
        task_id="deployment_001",
        name="項目部署流程",
        description="完整的 CI/CD 部署流程",
        complexity=TaskComplexity.VERY_COMPLEX
    )

    task.add_step(TaskStep("review", "代碼審查", "審查代碼變更", 代碼審查))
    task.add_step(TaskStep("test", "運行測試", "執行單元測試", 運行測試,
                          dependencies=["review"]))
    task.add_step(TaskStep("build", "構建項目", "構建生產版本", 構建項目,
                          dependencies=["test"]))
    task.add_step(TaskStep("deploy_test", "部署測試", "部署到測試環境", 部署到測試環境,
                          dependencies=["build"]))
    task.add_step(TaskStep("integration", "集成測試", "執行集成測試", 集成測試,
                          dependencies=["deploy_test"]))
    task.add_step(TaskStep("deploy_prod", "部署生產", "部署到生產環境", 部署到生產環境,
                          dependencies=["integration"]))
    task.add_step(TaskStep("health", "健康檢查", "檢查服務健康狀態", 健康檢查,
                          dependencies=["deploy_prod"]))

    return task


def 示例1_數據分析流程():
    """示例：執行數據分析任務"""
    print("\n" + "="*60)
    print("示例 1: 數據分析流程")
    print("="*60)

    task = 創建數據分析任務()
    executor = TaskExecutor()
    executor.execute(task)

    return task


def 示例2_在線購物():
    """示例：執行購物任務"""
    print("\n" + "="*60)
    print("示例 2: 在線購物流程")
    print("="*60)

    task = 創建電商購物任務()
    executor = TaskExecutor()
    executor.execute(task)

    return task


def 示例3_內容創作():
    """示例：內容創作任務"""
    print("\n" + "="*60)
    print("示例 3: 內容創作流程")
    print("="*60)

    task = 創建內容創作任務()
    executor = TaskExecutor()
    executor.execute(task)

    return task


def 示例4_項目部署():
    """示例：項目部署任務"""
    print("\n" + "="*60)
    print("示例 4: 項目部署流程")
    print("="*60)

    task = 創建項目部署任務()
    executor = TaskExecutor()
    executor.execute(task)

    return task


def 示例5_檢查點恢復():
    """示例：從檢查點恢復任務"""
    print("\n" + "="*60)
    print("示例 5: 檢查點恢復")
    print("="*60)

    task = 創建數據分析任務()
    executor = TaskExecutor()

    # 執行部分任務
    print("\n第一次執行（模擬中斷）...")
    for i, step in enumerate(task.steps[:2]):  # 只執行前兩步
        step.execute(task.context)
        executor.completed_steps.add(step.step_id)
        executor._create_checkpoint(task, step)

    # 顯示檢查點
    print(f"\n創建了 {len(executor.checkpoints)} 個檢查點")

    # 從檢查點恢復
    checkpoint_key = list(executor.checkpoints.keys())[-1]
    executor.restore_from_checkpoint(task, checkpoint_key)

    # 繼續執行剩餘步驟
    print("\n從檢查點繼續執行...")
    executor.execute(task)

    return executor


if __name__ == "__main__":
    print("Agent-S 多步任務演示\n")

    示例1_數據分析流程()
    示例2_在線購物()
    示例3_內容創作()
    示例4_項目部署()
    示例5_檢查點恢復()

    print("\n所有示例執行完成！")

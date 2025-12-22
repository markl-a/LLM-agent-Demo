"""
Pydantic AI - Graph 工作流範例

本範例展示：
1. Graph 定義
2. 節點和邊
3. 條件路由
4. 循環處理
5. 狀態持久化

Graph 支持複雜的工作流編排
注意：本範例展示 Graph 概念，具體 API 可能隨版本更新
"""

import asyncio
from typing import Literal, Optional, Annotated
from enum import Enum
from dataclasses import dataclass, field
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext


# ============================================================================
# 範例 1: 簡單的順序工作流
# ============================================================================

class WorkflowState(BaseModel):
    """工作流狀態"""
    current_step: str = "start"
    data: dict = Field(default_factory=dict)
    completed_steps: list[str] = Field(default_factory=list)


@dataclass
class SimpleWorkflow:
    """簡單的順序工作流"""

    def __init__(self):
        self.state = WorkflowState()
        self.steps = ["收集需求", "分析", "設計", "完成"]

    async def run_step(self, step: str) -> str:
        """執行單個步驟"""
        print(f"  執行步驟：{step}")
        self.state.completed_steps.append(step)
        return f"{step}完成"

    async def execute(self) -> dict:
        """執行工作流"""
        for step in self.steps:
            result = await self.run_step(step)
            self.state.data[step] = result

        return {
            "status": "success",
            "completed_steps": self.state.completed_steps,
            "results": self.state.data
        }


async def example_1_sequential_workflow():
    """簡單的順序工作流"""
    print("\n" + "="*60)
    print("範例 1: 順序工作流")
    print("="*60)

    workflow = SimpleWorkflow()
    print("開始執行工作流...")

    result = await workflow.execute()

    print(f"\n工作流完成！")
    print(f"完成步驟：{' → '.join(result['completed_steps'])}")


# ============================================================================
# 範例 2: 條件分支工作流
# ============================================================================

class TaskType(str, Enum):
    """任務類型"""
    SIMPLE = "simple"
    COMPLEX = "complex"
    URGENT = "urgent"


@dataclass
class ConditionalWorkflow:
    """條件分支工作流"""

    def __init__(self, task_type: TaskType):
        self.task_type = task_type
        self.steps_executed = []

    async def step_analyze(self) -> str:
        """分析步驟"""
        print("  → 執行：分析任務")
        self.steps_executed.append("analyze")
        return "analysis_complete"

    async def step_simple_process(self) -> str:
        """簡單處理"""
        print("  → 執行：簡單處理")
        self.steps_executed.append("simple_process")
        return "simple_done"

    async def step_complex_process(self) -> str:
        """複雜處理"""
        print("  → 執行：複雜處理")
        self.steps_executed.append("complex_process")
        return "complex_done"

    async def step_urgent_process(self) -> str:
        """緊急處理"""
        print("  → 執行：緊急處理（優先級高）")
        self.steps_executed.append("urgent_process")
        return "urgent_done"

    async def step_finalize(self) -> str:
        """完成步驟"""
        print("  → 執行：最終處理")
        self.steps_executed.append("finalize")
        return "finalized"

    async def execute(self) -> dict:
        """執行工作流"""
        # 分析階段
        await self.step_analyze()

        # 根據任務類型選擇處理路徑
        if self.task_type == TaskType.URGENT:
            await self.step_urgent_process()
        elif self.task_type == TaskType.COMPLEX:
            await self.step_complex_process()
        else:
            await self.step_simple_process()

        # 最終處理
        await self.step_finalize()

        return {
            "task_type": self.task_type.value,
            "steps": self.steps_executed,
            "path": " → ".join(self.steps_executed)
        }


async def example_2_conditional_workflow():
    """條件分支工作流"""
    print("\n" + "="*60)
    print("範例 2: 條件分支工作流")
    print("="*60)

    for task_type in TaskType:
        print(f"\n任務類型：{task_type.value}")

        workflow = ConditionalWorkflow(task_type)
        result = await workflow.execute()

        print(f"執行路徑：{result['path']}")


# ============================================================================
# 範例 3: 循環工作流
# ============================================================================

@dataclass
class IterativeWorkflow:
    """循環工作流"""

    def __init__(self, max_iterations: int = 5):
        self.max_iterations = max_iterations
        self.iteration = 0
        self.quality_score = 0.0

    async def step_generate(self) -> float:
        """生成內容"""
        print(f"  迭代 {self.iteration + 1}: 生成內容")

        # 模擬生成質量逐步提升
        import random
        quality = random.uniform(0.5, 1.0) + (self.iteration * 0.1)
        return min(quality, 1.0)

    async def step_evaluate(self, quality: float) -> bool:
        """評估質量"""
        print(f"  迭代 {self.iteration + 1}: 評估質量 = {quality:.2f}")
        self.quality_score = quality

        # 質量 > 0.9 則通過
        passed = quality > 0.9
        print(f"  迭代 {self.iteration + 1}: {'✓ 通過' if passed else '✗ 未通過，繼續優化'}")

        return passed

    async def step_refine(self):
        """優化內容"""
        print(f"  迭代 {self.iteration + 1}: 優化中...")

    async def execute(self) -> dict:
        """執行循環工作流"""
        while self.iteration < self.max_iterations:
            # 生成
            quality = await self.step_generate()

            # 評估
            passed = await self.step_evaluate(quality)

            if passed:
                print(f"\n✓ 在第 {self.iteration + 1} 次迭代達到目標質量！")
                break

            # 優化
            await self.step_refine()
            self.iteration += 1

        else:
            print(f"\n⚠️  達到最大迭代次數 ({self.max_iterations})")

        return {
            "iterations": self.iteration + 1,
            "final_quality": self.quality_score,
            "success": self.quality_score > 0.9
        }


async def example_3_iterative_workflow():
    """循環工作流"""
    print("\n" + "="*60)
    print("範例 3: 循環工作流")
    print("="*60)

    workflow = IterativeWorkflow(max_iterations=10)
    result = await workflow.execute()

    print(f"\n結果：")
    print(f"  總迭代次數：{result['iterations']}")
    print(f"  最終質量：{result['final_quality']:.2f}")
    print(f"  是否成功：{'是' if result['success'] else '否'}")


# ============================================================================
# 範例 4: 並行工作流
# ============================================================================

@dataclass
class ParallelWorkflow:
    """並行工作流"""

    async def task_a(self) -> str:
        """任務 A"""
        print("  → 任務 A 開始")
        await asyncio.sleep(1)
        print("  ✓ 任務 A 完成")
        return "Result A"

    async def task_b(self) -> str:
        """任務 B"""
        print("  → 任務 B 開始")
        await asyncio.sleep(0.8)
        print("  ✓ 任務 B 完成")
        return "Result B"

    async def task_c(self) -> str:
        """任務 C"""
        print("  → 任務 C 開始")
        await asyncio.sleep(0.5)
        print("  ✓ 任務 C 完成")
        return "Result C"

    async def merge_results(self, results: list[str]) -> str:
        """合併結果"""
        print("\n  → 合併結果")
        return " + ".join(results)

    async def execute(self) -> dict:
        """執行並行工作流"""
        import time
        start = time.time()

        # 並行執行任務 A, B, C
        results = await asyncio.gather(
            self.task_a(),
            self.task_b(),
            self.task_c()
        )

        # 合併結果
        final_result = await self.merge_results(results)

        elapsed = time.time() - start

        return {
            "results": results,
            "merged": final_result,
            "elapsed_time": elapsed
        }


async def example_4_parallel_workflow():
    """並行工作流"""
    print("\n" + "="*60)
    print("範例 4: 並行工作流")
    print("="*60)

    print("開始並行執行任務...")

    workflow = ParallelWorkflow()
    result = await workflow.execute()

    print(f"\n合併結果：{result['merged']}")
    print(f"總耗時：{result['elapsed_time']:.2f} 秒")


# ============================================================================
# 範例 5: 狀態機工作流
# ============================================================================

class OrderStatus(str, Enum):
    """訂單狀態"""
    CREATED = "created"
    PAID = "paid"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


@dataclass
class OrderWorkflow:
    """訂單狀態機工作流"""

    def __init__(self, order_id: str):
        self.order_id = order_id
        self.status = OrderStatus.CREATED
        self.history = [OrderStatus.CREATED]

    def can_transition(self, to_status: OrderStatus) -> bool:
        """檢查是否可以轉換狀態"""
        valid_transitions = {
            OrderStatus.CREATED: [OrderStatus.PAID, OrderStatus.CANCELLED],
            OrderStatus.PAID: [OrderStatus.PROCESSING, OrderStatus.CANCELLED],
            OrderStatus.PROCESSING: [OrderStatus.SHIPPED, OrderStatus.CANCELLED],
            OrderStatus.SHIPPED: [OrderStatus.DELIVERED],
            OrderStatus.DELIVERED: [],
            OrderStatus.CANCELLED: [],
        }

        return to_status in valid_transitions.get(self.status, [])

    async def transition(self, to_status: OrderStatus) -> bool:
        """執行狀態轉換"""
        if not self.can_transition(to_status):
            print(f"  ✗ 無法從 {self.status.value} 轉換到 {to_status.value}")
            return False

        print(f"  ✓ 狀態轉換：{self.status.value} → {to_status.value}")
        self.status = to_status
        self.history.append(to_status)
        return True

    async def process_order(self) -> dict:
        """處理訂單（正常流程）"""
        transitions = [
            OrderStatus.PAID,
            OrderStatus.PROCESSING,
            OrderStatus.SHIPPED,
            OrderStatus.DELIVERED,
        ]

        for status in transitions:
            success = await self.transition(status)
            if not success:
                break
            await asyncio.sleep(0.2)

        return {
            "order_id": self.order_id,
            "final_status": self.status.value,
            "history": [s.value for s in self.history]
        }


async def example_5_state_machine():
    """狀態機工作流"""
    print("\n" + "="*60)
    print("範例 5: 狀態機工作流")
    print("="*60)

    print("正常訂單流程：")
    order1 = OrderWorkflow("ORD-001")
    result1 = await order1.process_order()
    print(f"訂單歷程：{' → '.join(result1['history'])}\n")

    print("嘗試無效轉換：")
    order2 = OrderWorkflow("ORD-002")
    await order2.transition(OrderStatus.SHIPPED)  # 無效：跳過付款


# ============================================================================
# 範例 6: Agent 協作工作流
# ============================================================================

class ResearchWorkflow:
    """研究工作流 - 多個 Agent 協作"""

    def __init__(self):
        self.researcher = Agent('openai:gpt-4', name='researcher')
        self.analyzer = Agent('openai:gpt-4', name='analyzer')
        self.writer = Agent('openai:gpt-4', name='writer')

    async def step_research(self, topic: str) -> str:
        """研究步驟"""
        print("  → Researcher: 收集資料")

        result = await self.researcher.run(
            f"列出關於 '{topic}' 的 3 個關鍵要點"
        )

        return result.data

    async def step_analyze(self, research_data: str) -> str:
        """分析步驟"""
        print("  → Analyzer: 分析數據")

        result = await self.analyzer.run(
            f"分析以下研究資料並提取見解：\n{research_data}"
        )

        return result.data

    async def step_write(self, analysis: str) -> str:
        """寫作步驟"""
        print("  → Writer: 撰寫報告")

        result = await self.writer.run(
            f"基於以下分析撰寫一段摘要：\n{analysis}"
        )

        return result.data

    async def execute(self, topic: str) -> dict:
        """執行研究工作流"""
        # 順序執行各個步驟
        research = await self.step_research(topic)
        analysis = await self.step_analyze(research)
        report = await self.step_write(analysis)

        return {
            "topic": topic,
            "research": research,
            "analysis": analysis,
            "report": report
        }


async def example_6_agent_collaboration():
    """Agent 協作工作流"""
    print("\n" + "="*60)
    print("範例 6: Agent 協作工作流")
    print("="*60)

    workflow = ResearchWorkflow()

    print("開始研究工作流...")
    result = await workflow.execute("人工智慧")

    print(f"\n最終報告：")
    print(f"{result['report'][:200]}...")


# ============================================================================
# 範例 7: 錯誤處理工作流
# ============================================================================

@dataclass
class RobustWorkflow:
    """具有錯誤處理的工作流"""

    def __init__(self):
        self.retries = 3
        self.errors = []

    async def step_with_retry(
        self,
        step_name: str,
        step_func,
        *args
    ) -> Optional[any]:
        """帶重試的步驟執行"""
        for attempt in range(self.retries):
            try:
                print(f"  → 執行 {step_name} (嘗試 {attempt + 1}/{self.retries})")
                result = await step_func(*args)
                print(f"  ✓ {step_name} 成功")
                return result

            except Exception as e:
                print(f"  ✗ {step_name} 失敗: {e}")
                self.errors.append({
                    "step": step_name,
                    "attempt": attempt + 1,
                    "error": str(e)
                })

                if attempt < self.retries - 1:
                    await asyncio.sleep(1)  # 等待後重試

        return None

    async def execute(self) -> dict:
        """執行工作流"""
        # 模擬可能失敗的步驟
        async def unreliable_step():
            import random
            if random.random() < 0.3:  # 30% 失敗率
                raise Exception("隨機錯誤")
            return "success"

        result = await self.step_with_retry(
            "不穩定步驟",
            unreliable_step
        )

        return {
            "success": result is not None,
            "result": result,
            "errors": self.errors
        }


async def example_7_error_handling():
    """錯誤處理工作流"""
    print("\n" + "="*60)
    print("範例 7: 錯誤處理工作流")
    print("="*60)

    workflow = RobustWorkflow()
    result = await workflow.execute()

    print(f"\n結果：{'成功' if result['success'] else '失敗'}")
    if result['errors']:
        print(f"遇到 {len(result['errors'])} 個錯誤")


# ============================================================================
# 主程式
# ============================================================================

async def main():
    """運行所有範例"""
    print("\n" + "🕸️  " + "="*58)
    print("Pydantic AI - Graph 工作流範例")
    print("="*60)

    await example_1_sequential_workflow()
    await example_2_conditional_workflow()
    await example_3_iterative_workflow()
    await example_4_parallel_workflow()
    await example_5_state_machine()
    await example_6_agent_collaboration()
    await example_7_error_handling()

    print("\n" + "="*60)
    print("✓ Graph 工作流範例完成！")
    print("💡 工作流設計原則：")
    print("   1. 清晰的狀態管理")
    print("   2. 適當的錯誤處理")
    print("   3. 合理的並行策略")
    print("   4. 可追蹤的執行歷史")
    print("="*60)


if __name__ == '__main__':
    import os
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  請設置 OPENAI_API_KEY 環境變量")
    else:
        asyncio.run(main())

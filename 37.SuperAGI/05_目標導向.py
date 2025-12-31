"""
SuperAGI 目標導向 Agent 示例

這個示例展示了如何:
1. 設置和分解目標
2. 生成執行計劃
3. 追蹤目標進度
4. 動態調整策略
5. 評估目標完成度

目標導向是 SuperAGI 的核心特性之一。
"""

import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field


# ==================== 目標狀態 ====================

class GoalStatus(Enum):
    """目標狀態"""
    PENDING = "pending"  # 待處理
    IN_PROGRESS = "in_progress"  # 進行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失敗
    BLOCKED = "blocked"  # 被阻塞


class TaskStatus(Enum):
    """任務狀態"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    FAILED = "failed"


# ==================== 目標定義 ====================

@dataclass
class Goal:
    """目標"""
    id: str
    description: str
    priority: int = 1  # 1-10, 10 最高
    status: GoalStatus = GoalStatus.PENDING
    success_criteria: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    progress: float = 0.0  # 0-1

    def is_completed(self) -> bool:
        """檢查是否完成"""
        return self.status == GoalStatus.COMPLETED

    def is_blocked(self) -> bool:
        """檢查是否被阻塞"""
        return self.status == GoalStatus.BLOCKED

    def mark_completed(self):
        """標記為完成"""
        self.status = GoalStatus.COMPLETED
        self.progress = 1.0
        self.completed_at = datetime.now()

    def mark_failed(self):
        """標記為失敗"""
        self.status = GoalStatus.FAILED

    def update_progress(self, progress: float):
        """更新進度"""
        self.progress = min(1.0, max(0.0, progress))
        if self.progress >= 1.0:
            self.mark_completed()


# ==================== 任務定義 ====================

@dataclass
class Task:
    """任務"""
    id: str
    description: str
    goal_id: str
    tool: str
    parameters: Dict = field(default_factory=dict)
    status: TaskStatus = TaskStatus.TODO
    priority: int = 1
    dependencies: List[str] = field(default_factory=list)
    result: Optional[Dict] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def start(self):
        """開始任務"""
        self.status = TaskStatus.IN_PROGRESS
        self.started_at = datetime.now()

    def complete(self, result: Dict):
        """完成任務"""
        self.status = TaskStatus.DONE
        self.result = result
        self.completed_at = datetime.now()

    def fail(self, error: str):
        """任務失敗"""
        self.status = TaskStatus.FAILED
        self.error = error
        self.completed_at = datetime.now()


# ==================== 目標分解器 ====================

class GoalDecomposer:
    """
    目標分解器

    將高層目標分解為具體任務
    """

    def __init__(self):
        self.decomposition_count = 0

    def decompose(self, goal: Goal) -> List[Task]:
        """
        分解目標為任務

        參數:
            goal: 目標對象

        返回:
            任務列表
        """
        print(f"\n🎯 分解目標: {goal.description}")

        # 模擬 LLM 分解過程
        tasks = self._simulate_decomposition(goal)

        print(f"   生成了 {len(tasks)} 個任務")
        for task in tasks:
            print(f"   - {task.description} (工具: {task.tool})")

        self.decomposition_count += 1

        return tasks

    def _simulate_decomposition(self, goal: Goal) -> List[Task]:
        """模擬目標分解"""
        # 根據目標類型生成任務
        if "搜索" in goal.description or "研究" in goal.description:
            return self._decompose_research_goal(goal)
        elif "分析" in goal.description:
            return self._decompose_analysis_goal(goal)
        elif "生成" in goal.description or "創建" in goal.description:
            return self._decompose_generation_goal(goal)
        else:
            return self._decompose_generic_goal(goal)

    def _decompose_research_goal(self, goal: Goal) -> List[Task]:
        """分解研究類目標"""
        return [
            Task(
                id=f"{goal.id}_task_1",
                description=f"搜索關於 '{goal.description}' 的信息",
                goal_id=goal.id,
                tool="GoogleSearchTool",
                parameters={"query": goal.description, "num_results": 5}
            ),
            Task(
                id=f"{goal.id}_task_2",
                description="提取關鍵信息",
                goal_id=goal.id,
                tool="WebScraperTool",
                parameters={},
                dependencies=[f"{goal.id}_task_1"]
            ),
            Task(
                id=f"{goal.id}_task_3",
                description="總結研究結果",
                goal_id=goal.id,
                tool="TextSummarizerTool",
                parameters={},
                dependencies=[f"{goal.id}_task_2"]
            )
        ]

    def _decompose_analysis_goal(self, goal: Goal) -> List[Task]:
        """分解分析類目標"""
        return [
            Task(
                id=f"{goal.id}_task_1",
                description="讀取數據",
                goal_id=goal.id,
                tool="FileReadTool",
                parameters={"file_path": "data.csv"}
            ),
            Task(
                id=f"{goal.id}_task_2",
                description="執行數據分析",
                goal_id=goal.id,
                tool="DataAnalysisTool",
                parameters={"analysis_type": "comprehensive"},
                dependencies=[f"{goal.id}_task_1"]
            ),
            Task(
                id=f"{goal.id}_task_3",
                description="生成分析報告",
                goal_id=goal.id,
                tool="ReportGeneratorTool",
                parameters={"format": "markdown"},
                dependencies=[f"{goal.id}_task_2"]
            )
        ]

    def _decompose_generation_goal(self, goal: Goal) -> List[Task]:
        """分解生成類目標"""
        return [
            Task(
                id=f"{goal.id}_task_1",
                description="收集相關資料",
                goal_id=goal.id,
                tool="GoogleSearchTool",
                parameters={}
            ),
            Task(
                id=f"{goal.id}_task_2",
                description="生成內容草稿",
                goal_id=goal.id,
                tool="ContentGeneratorTool",
                parameters={},
                dependencies=[f"{goal.id}_task_1"]
            ),
            Task(
                id=f"{goal.id}_task_3",
                description="審核和優化內容",
                goal_id=goal.id,
                tool="ContentReviewTool",
                parameters={},
                dependencies=[f"{goal.id}_task_2"]
            ),
            Task(
                id=f"{goal.id}_task_4",
                description="保存最終結果",
                goal_id=goal.id,
                tool="FileWriteTool",
                parameters={},
                dependencies=[f"{goal.id}_task_3"]
            )
        ]

    def _decompose_generic_goal(self, goal: Goal) -> List[Task]:
        """分解通用目標"""
        return [
            Task(
                id=f"{goal.id}_task_1",
                description=f"執行: {goal.description}",
                goal_id=goal.id,
                tool="GenericTool",
                parameters={}
            )
        ]


# ==================== 執行計劃器 ====================

class ExecutionPlanner:
    """
    執行計劃器

    生成和管理任務執行計劃
    """

    def __init__(self):
        self.plan_count = 0

    def create_plan(self, tasks: List[Task]) -> Dict[str, Any]:
        """
        創建執行計劃

        參數:
            tasks: 任務列表

        返回:
            執行計劃
        """
        print(f"\n📋 創建執行計劃...")

        # 拓撲排序任務（考慮依賴關係）
        sorted_tasks = self._topological_sort(tasks)

        # 分配優先級
        for i, task in enumerate(sorted_tasks):
            task.priority = len(sorted_tasks) - i

        plan = {
            "id": f"plan_{self.plan_count}",
            "tasks": sorted_tasks,
            "total_tasks": len(sorted_tasks),
            "estimated_time": len(sorted_tasks) * 10,  # 秒
            "created_at": datetime.now().isoformat()
        }

        print(f"   計劃包含 {len(sorted_tasks)} 個任務")
        print(f"   預計耗時: {plan['estimated_time']} 秒")

        self.plan_count += 1

        return plan

    def _topological_sort(self, tasks: List[Task]) -> List[Task]:
        """
        拓撲排序任務

        參數:
            tasks: 任務列表

        返回:
            排序後的任務列表
        """
        # 構建依賴圖
        task_map = {task.id: task for task in tasks}
        in_degree = {task.id: 0 for task in tasks}

        for task in tasks:
            for dep in task.dependencies:
                if dep in in_degree:
                    in_degree[task.id] += 1

        # 執行拓撲排序
        queue = [tid for tid, degree in in_degree.items() if degree == 0]
        sorted_tasks = []

        while queue:
            # 按優先級排序
            queue.sort(key=lambda tid: task_map[tid].priority, reverse=True)

            task_id = queue.pop(0)
            task = task_map[task_id]
            sorted_tasks.append(task)

            # 更新依賴此任務的其他任務
            for t in tasks:
                if task_id in t.dependencies:
                    in_degree[t.id] -= 1
                    if in_degree[t.id] == 0:
                        queue.append(t.id)

        return sorted_tasks


# ==================== 目標追蹤器 ====================

class GoalTracker:
    """
    目標追蹤器

    追蹤目標和任務的執行進度
    """

    def __init__(self):
        self.goals: Dict[str, Goal] = {}
        self.tasks: Dict[str, Task] = {}
        self.execution_log = []

    def add_goal(self, goal: Goal):
        """添加目標"""
        self.goals[goal.id] = goal
        print(f"✅ 添加目標: {goal.description}")

    def add_task(self, task: Task):
        """添加任務"""
        self.tasks[task.id] = task

    def update_task_status(self, task_id: str, status: TaskStatus, result: Dict = None):
        """更新任務狀態"""
        if task_id not in self.tasks:
            return

        task = self.tasks[task_id]
        old_status = task.status
        task.status = status

        if status == TaskStatus.DONE and result:
            task.complete(result)
        elif status == TaskStatus.FAILED:
            task.fail(result.get("error", "Unknown error") if result else "Unknown error")

        # 記錄日誌
        self.execution_log.append({
            "timestamp": datetime.now().isoformat(),
            "task_id": task_id,
            "old_status": old_status.value,
            "new_status": status.value
        })

        # 更新目標進度
        self._update_goal_progress(task.goal_id)

    def _update_goal_progress(self, goal_id: str):
        """更新目標進度"""
        if goal_id not in self.goals:
            return

        goal = self.goals[goal_id]

        # 計算任務完成率
        goal_tasks = [t for t in self.tasks.values() if t.goal_id == goal_id]
        if not goal_tasks:
            return

        completed_tasks = sum(1 for t in goal_tasks if t.status == TaskStatus.DONE)
        progress = completed_tasks / len(goal_tasks)

        goal.update_progress(progress)

        print(f"📊 目標進度更新: {goal.description} - {progress:.1%}")

    def get_goal_status(self, goal_id: str) -> Dict:
        """獲取目標狀態"""
        if goal_id not in self.goals:
            return {}

        goal = self.goals[goal_id]
        goal_tasks = [t for t in self.tasks.values() if t.goal_id == goal_id]

        return {
            "goal": goal.description,
            "status": goal.status.value,
            "progress": goal.progress,
            "total_tasks": len(goal_tasks),
            "completed_tasks": sum(1 for t in goal_tasks if t.status == TaskStatus.DONE),
            "failed_tasks": sum(1 for t in goal_tasks if t.status == TaskStatus.FAILED),
            "pending_tasks": sum(1 for t in goal_tasks if t.status == TaskStatus.TODO)
        }

    def get_summary(self) -> Dict:
        """獲取總體摘要"""
        total_goals = len(self.goals)
        completed_goals = sum(1 for g in self.goals.values() if g.is_completed())

        total_tasks = len(self.tasks)
        completed_tasks = sum(1 for t in self.tasks.values() if t.status == TaskStatus.DONE)

        return {
            "total_goals": total_goals,
            "completed_goals": completed_goals,
            "goal_completion_rate": completed_goals / total_goals if total_goals > 0 else 0,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "task_completion_rate": completed_tasks / total_tasks if total_tasks > 0 else 0,
            "execution_log_size": len(self.execution_log)
        }


# ==================== 目標導向 Agent ====================

class GoalOrientedAgent:
    """
    目標導向 Agent

    整合目標分解、計劃和執行
    """

    def __init__(self, name: str):
        self.name = name
        self.decomposer = GoalDecomposer()
        self.planner = ExecutionPlanner()
        self.tracker = GoalTracker()

    def set_goals(self, goals: List[Goal]):
        """
        設置目標

        參數:
            goals: 目標列表
        """
        print(f"\n🎯 {self.name} 設置目標")
        print("=" * 60)

        for goal in goals:
            self.tracker.add_goal(goal)

    def execute(self):
        """執行目標"""
        print(f"\n🚀 {self.name} 開始執行")
        print("=" * 60)

        # 處理每個目標
        for goal in self.tracker.goals.values():
            if goal.is_completed():
                continue

            print(f"\n處理目標: {goal.description}")

            # 1. 分解目標
            tasks = self.decomposer.decompose(goal)

            # 添加任務到追蹤器
            for task in tasks:
                self.tracker.add_task(task)

            # 2. 創建執行計劃
            plan = self.planner.create_plan(tasks)

            # 3. 執行任務
            self._execute_plan(plan)

            # 4. 檢查目標完成狀態
            status = self.tracker.get_goal_status(goal.id)
            print(f"\n目標狀態: {json.dumps(status, indent=2, ensure_ascii=False)}")

    def _execute_plan(self, plan: Dict):
        """執行計劃"""
        print(f"\n⚙️  執行計劃: {plan['id']}")

        for task in plan["tasks"]:
            # 檢查依賴
            if not self._check_dependencies(task):
                print(f"   ⏸️  任務 {task.id} 依賴未滿足，跳過")
                continue

            # 執行任務
            print(f"\n   執行任務: {task.description}")
            task.start()

            # 模擬工具執行
            result = self._simulate_tool_execution(task)

            # 更新任務狀態
            if result.get("success"):
                self.tracker.update_task_status(task.id, TaskStatus.DONE, result)
                print(f"   ✅ 任務完成")
            else:
                self.tracker.update_task_status(task.id, TaskStatus.FAILED, result)
                print(f"   ❌ 任務失敗: {result.get('error')}")

    def _check_dependencies(self, task: Task) -> bool:
        """檢查任務依賴"""
        for dep_id in task.dependencies:
            if dep_id in self.tracker.tasks:
                dep_task = self.tracker.tasks[dep_id]
                if dep_task.status != TaskStatus.DONE:
                    return False
        return True

    def _simulate_tool_execution(self, task: Task) -> Dict:
        """模擬工具執行"""
        import time
        import random

        time.sleep(0.1)  # 模擬執行時間

        # 90% 成功率
        if random.random() < 0.9:
            return {
                "success": True,
                "result": f"任務 {task.id} 執行成功",
                "data": {"output": "模擬輸出"}
            }
        else:
            return {
                "success": False,
                "error": "模擬執行失敗"
            }

    def get_report(self) -> str:
        """生成執行報告"""
        summary = self.tracker.get_summary()

        report = f"""
╔══════════════════════════════════════════════════╗
║         {self.name} 執行報告                      ║
╠══════════════════════════════════════════════════╣
║ 目標總數: {summary['total_goals']:37} ║
║ 完成目標: {summary['completed_goals']:37} ║
║ 目標完成率: {summary['goal_completion_rate']:.1%}{' ' * 34} ║
║                                                  ║
║ 任務總數: {summary['total_tasks']:37} ║
║ 完成任務: {summary['completed_tasks']:37} ║
║ 任務完成率: {summary['task_completion_rate']:.1%}{' ' * 34} ║
╚══════════════════════════════════════════════════╝
        """

        return report


# ==================== 示例場景 ====================

def example_1_basic_goal():
    """示例 1: 基本目標執行"""
    print("\n" + "=" * 60)
    print("示例 1: 基本目標執行")
    print("=" * 60)

    # 創建目標
    goal = Goal(
        id="goal_1",
        description="搜索並總結 AI Agent 的最新發展",
        priority=8,
        success_criteria=[
            "找到至少 5 個相關資源",
            "生成結構化摘要",
            "保存結果到文件"
        ]
    )

    # 創建 Agent
    agent = GoalOrientedAgent("ResearchAgent")

    # 設置並執行目標
    agent.set_goals([goal])
    agent.execute()

    # 顯示報告
    print(agent.get_report())


def example_2_multiple_goals():
    """示例 2: 多目標執行"""
    print("\n" + "=" * 60)
    print("示例 2: 多目標執行")
    print("=" * 60)

    goals = [
        Goal(
            id="goal_1",
            description="分析銷售數據",
            priority=9,
            success_criteria=["讀取數據", "執行分析", "生成報告"]
        ),
        Goal(
            id="goal_2",
            description="生成月度報告",
            priority=7,
            success_criteria=["收集數據", "創建報告", "發送給團隊"],
            dependencies=["goal_1"]  # 依賴目標 1
        ),
        Goal(
            id="goal_3",
            description="更新文檔",
            priority=5,
            success_criteria=["檢查變更", "更新內容", "提交 PR"]
        )
    ]

    agent = GoalOrientedAgent("AnalysisAgent")
    agent.set_goals(goals)
    agent.execute()

    print(agent.get_report())


def example_3_goal_tracking():
    """示例 3: 目標追蹤"""
    print("\n" + "=" * 60)
    print("示例 3: 詳細目標追蹤")
    print("=" * 60)

    tracker = GoalTracker()

    # 添加目標
    goal = Goal(
        id="goal_track",
        description="開發新功能",
        priority=10
    )
    tracker.add_goal(goal)

    # 添加任務
    tasks = [
        Task(id="t1", description="設計", goal_id=goal.id, tool="DesignTool"),
        Task(id="t2", description="實現", goal_id=goal.id, tool="CodeTool", dependencies=["t1"]),
        Task(id="t3", description="測試", goal_id=goal.id, tool="TestTool", dependencies=["t2"]),
    ]

    for task in tasks:
        tracker.add_task(task)

    # 模擬任務執行
    tracker.update_task_status("t1", TaskStatus.DONE, {"success": True})
    tracker.update_task_status("t2", TaskStatus.DONE, {"success": True})
    tracker.update_task_status("t3", TaskStatus.DONE, {"success": True})

    # 顯示狀態
    status = tracker.get_goal_status(goal.id)
    print(f"\n目標狀態:")
    print(json.dumps(status, indent=2, ensure_ascii=False))

    summary = tracker.get_summary()
    print(f"\n總體摘要:")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


# ==================== 主函數 ====================

def main():
    """主函數"""
    print("\n" + "🎯 " * 20)
    print("SuperAGI 目標導向 Agent 教程")
    print("🎯 " * 20)

    try:
        # 示例 1: 基本目標
        example_1_basic_goal()

        # 示例 2: 多目標
        example_2_multiple_goals()

        # 示例 3: 目標追蹤
        example_3_goal_tracking()

        print("\n" + "=" * 60)
        print("✅ 所有目標導向示例執行完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 執行出錯: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

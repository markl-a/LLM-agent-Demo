"""
Agent-S 任務規劃模組

此模組展示 Agent-S 的階層式任務規劃能力：
1. 高層任務分解 - 將複雜目標分解為子任務
2. 低層操作執行 - 將子任務轉換為具體操作
3. 動態規劃調整 - 根據執行結果調整計劃
4. 依賴關係管理 - 處理任務間的依賴關係

Agent-S 使用類似 STRIPS 的規劃器來自動分解和執行任務。
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Callable, Any
from enum import Enum
import time
from datetime import datetime


class TaskStatus(Enum):
    """任務狀態枚舉"""
    PENDING = "待執行"
    IN_PROGRESS = "執行中"
    COMPLETED = "已完成"
    FAILED = "失敗"
    BLOCKED = "阻塞"


class TaskPriority(Enum):
    """任務優先級"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Action:
    """原子操作"""
    name: str
    description: str
    params: Dict[str, Any] = field(default_factory=dict)
    preconditions: List[str] = field(default_factory=list)
    effects: List[str] = field(default_factory=list)

    def execute(self) -> bool:
        """執行操作"""
        print(f"  執行操作: {self.name}")
        print(f"    描述: {self.description}")
        print(f"    參數: {self.params}")
        # 模擬執行
        time.sleep(0.1)
        return True


@dataclass
class Task:
    """任務定義"""
    id: str
    name: str
    description: str
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    parent_id: Optional[str] = None
    dependencies: Set[str] = field(default_factory=set)
    actions: List[Action] = field(default_factory=list)
    subtasks: List['Task'] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

    def is_ready(self, completed_tasks: Set[str]) -> bool:
        """檢查任務是否可以執行"""
        if self.status != TaskStatus.PENDING:
            return False
        return self.dependencies.issubset(completed_tasks)

    def add_dependency(self, task_id: str):
        """添加依賴"""
        self.dependencies.add(task_id)

    def add_subtask(self, subtask: 'Task'):
        """添加子任務"""
        self.subtasks.append(subtask)
        subtask.parent_id = self.id


class TaskPlanner:
    """
    階層式任務規劃器

    實現功能：
    1. 任務分解：將高層目標分解為可執行的子任務
    2. 依賴分析：自動分析任務間的依賴關係
    3. 執行排序：根據依賴關係排序任務執行順序
    4. 動態調整：根據執行結果動態調整計劃
    """

    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.completed_tasks: Set[str] = set()
        self.knowledge_base: Dict[str, Any] = {}

    def decompose_task(self, task: Task) -> List[Task]:
        """
        分解高層任務為低層子任務

        Args:
            task: 要分解的任務

        Returns:
            子任務列表
        """
        print(f"\n分解任務: {task.name}")

        # 根據任務類型進行分解（這裡使用規則）
        subtasks = []

        if "網頁" in task.name or "瀏覽" in task.name:
            subtasks = self._decompose_web_task(task)
        elif "文件" in task.name or "編輯" in task.name:
            subtasks = self._decompose_file_task(task)
        elif "郵件" in task.name:
            subtasks = self._decompose_email_task(task)
        else:
            # 通用分解策略
            subtasks = self._decompose_generic_task(task)

        # 設置子任務關係
        for i, subtask in enumerate(subtasks):
            subtask.id = f"{task.id}.{i+1}"
            task.add_subtask(subtask)
            self.tasks[subtask.id] = subtask

            # 設置順序依賴
            if i > 0:
                subtask.add_dependency(subtasks[i-1].id)

        return subtasks

    def _decompose_web_task(self, task: Task) -> List[Task]:
        """分解網頁任務"""
        return [
            Task(
                id="", name="打開瀏覽器",
                description="啟動瀏覽器應用程序",
                actions=[Action("launch_browser", "啟動瀏覽器")]
            ),
            Task(
                id="", name="導航到網站",
                description=f"訪問目標網站: {task.metadata.get('url', '')}",
                actions=[Action("navigate", "導航到URL", {"url": task.metadata.get('url')})]
            ),
            Task(
                id="", name="執行操作",
                description="在網頁上執行指定操作",
                actions=[Action("interact", "與網頁交互", task.metadata.get('actions', {}))]
            ),
            Task(
                id="", name="獲取結果",
                description="提取所需信息",
                actions=[Action("extract", "提取信息")]
            )
        ]

    def _decompose_file_task(self, task: Task) -> List[Task]:
        """分解文件操作任務"""
        return [
            Task(
                id="", name="定位文件",
                description=f"找到文件: {task.metadata.get('filename', '')}",
                actions=[Action("find_file", "搜索文件", {"name": task.metadata.get('filename')})]
            ),
            Task(
                id="", name="打開文件",
                description="用適當的應用程序打開文件",
                actions=[Action("open_file", "打開文件")]
            ),
            Task(
                id="", name="編輯內容",
                description="執行編輯操作",
                actions=[Action("edit", "編輯文件", task.metadata.get('edits', {}))]
            ),
            Task(
                id="", name="保存文件",
                description="保存更改",
                actions=[Action("save", "保存文件")]
            )
        ]

    def _decompose_email_task(self, task: Task) -> List[Task]:
        """分解郵件任務"""
        return [
            Task(
                id="", name="打開郵件客戶端",
                description="啟動郵件應用",
                actions=[Action("launch_email", "打開郵件")]
            ),
            Task(
                id="", name="創建新郵件",
                description="新建郵件",
                actions=[Action("new_email", "新建郵件")]
            ),
            Task(
                id="", name="填寫內容",
                description="填寫收件人、主題和正文",
                actions=[Action("compose", "撰寫郵件", task.metadata.get('email_data', {}))]
            ),
            Task(
                id="", name="發送郵件",
                description="發送郵件",
                actions=[Action("send", "發送")]
            )
        ]

    def _decompose_generic_task(self, task: Task) -> List[Task]:
        """通用任務分解"""
        return [
            Task(
                id="", name="準備階段",
                description="準備執行環境",
                actions=[Action("prepare", "準備")]
            ),
            Task(
                id="", name="執行階段",
                description="執行主要操作",
                actions=[Action("execute", "執行", task.metadata)]
            ),
            Task(
                id="", name="驗證階段",
                description="驗證執行結果",
                actions=[Action("verify", "驗證")]
            )
        ]

    def create_execution_plan(self, root_task: Task) -> List[Task]:
        """
        創建執行計劃

        Args:
            root_task: 根任務

        Returns:
            按執行順序排列的任務列表
        """
        print(f"\n創建執行計劃: {root_task.name}")

        # 註冊根任務
        self.tasks[root_task.id] = root_task

        # 遞歸分解任務
        self._recursive_decompose(root_task)

        # 拓撲排序得到執行順序
        execution_order = self._topological_sort()

        print(f"執行計劃創建完成，共 {len(execution_order)} 個任務")
        return execution_order

    def _recursive_decompose(self, task: Task, max_depth: int = 3, current_depth: int = 0):
        """遞歸分解任務"""
        if current_depth >= max_depth:
            return

        if self._should_decompose(task):
            subtasks = self.decompose_task(task)
            for subtask in subtasks:
                self._recursive_decompose(subtask, max_depth, current_depth + 1)

    def _should_decompose(self, task: Task) -> bool:
        """判斷任務是否需要進一步分解"""
        # 如果任務已有具體操作，不需要分解
        if task.actions:
            return False

        # 如果任務已有子任務，不需要分解
        if task.subtasks:
            return False

        # 簡單任務不需要分解
        if task.priority == TaskPriority.LOW and len(task.description) < 20:
            return False

        return True

    def _topological_sort(self) -> List[Task]:
        """拓撲排序任務"""
        # 計算入度
        in_degree = {task_id: 0 for task_id in self.tasks}
        for task in self.tasks.values():
            for dep in task.dependencies:
                if dep in in_degree:
                    in_degree[task.id] += 1

        # 找出所有入度為 0 的任務
        queue = [task_id for task_id, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            # 按優先級排序
            queue.sort(key=lambda tid: self.tasks[tid].priority.value, reverse=True)
            task_id = queue.pop(0)
            result.append(self.tasks[task_id])

            # 更新依賴此任務的其他任務
            for other_task in self.tasks.values():
                if task_id in other_task.dependencies:
                    in_degree[other_task.id] -= 1
                    if in_degree[other_task.id] == 0:
                        queue.append(other_task.id)

        return result

    def execute_plan(self, execution_plan: List[Task]) -> Dict[str, Any]:
        """
        執行計劃

        Args:
            execution_plan: 執行計劃

        Returns:
            執行結果統計
        """
        print("\n" + "="*60)
        print("開始執行任務計劃")
        print("="*60)

        stats = {
            "total": len(execution_plan),
            "completed": 0,
            "failed": 0,
            "blocked": 0
        }

        for task in execution_plan:
            print(f"\n[{task.id}] {task.name}")

            # 檢查是否可執行
            if not task.is_ready(self.completed_tasks):
                task.status = TaskStatus.BLOCKED
                stats["blocked"] += 1
                print(f"  狀態: {task.status.value} (等待依賴: {task.dependencies - self.completed_tasks})")
                continue

            # 執行任務
            task.status = TaskStatus.IN_PROGRESS
            success = True

            try:
                for action in task.actions:
                    if not action.execute():
                        success = False
                        break

                if success:
                    task.status = TaskStatus.COMPLETED
                    task.completed_at = datetime.now()
                    self.completed_tasks.add(task.id)
                    stats["completed"] += 1
                    print(f"  狀態: {task.status.value} ✓")
                else:
                    task.status = TaskStatus.FAILED
                    stats["failed"] += 1
                    print(f"  狀態: {task.status.value} ✗")

            except Exception as e:
                task.status = TaskStatus.FAILED
                stats["failed"] += 1
                print(f"  狀態: {task.status.value} - 錯誤: {e}")

        print("\n" + "="*60)
        print("執行完成")
        print(f"總任務數: {stats['total']}")
        print(f"已完成: {stats['completed']}")
        print(f"失敗: {stats['failed']}")
        print(f"阻塞: {stats['blocked']}")
        print("="*60)

        return stats


def 示例1_簡單任務規劃():
    """示例：簡單任務的規劃與執行"""
    print("\n" + "="*60)
    print("示例 1: 簡單任務規劃")
    print("="*60)

    planner = TaskPlanner()

    # 創建一個簡單任務
    task = Task(
        id="T1",
        name="發送報告郵件",
        description="將月度報告發送給團隊成員",
        priority=TaskPriority.HIGH,
        metadata={
            "email_data": {
                "to": "team@example.com",
                "subject": "月度報告",
                "body": "請查收本月報告"
            }
        }
    )

    # 創建並執行計劃
    plan = planner.create_execution_plan(task)
    results = planner.execute_plan(plan)

    return results


def 示例2_複雜任務分解():
    """示例：複雜任務的階層式分解"""
    print("\n" + "="*60)
    print("示例 2: 複雜任務分解")
    print("="*60)

    planner = TaskPlanner()

    # 創建一個複雜的多步驟任務
    task = Task(
        id="T2",
        name="在線購物",
        description="在電商網站上購買商品",
        priority=TaskPriority.CRITICAL,
        metadata={
            "url": "https://example-shop.com",
            "product": "筆記本電腦",
            "actions": {
                "search": "筆記本電腦",
                "filter": {"price": "5000-10000", "brand": "Dell"},
                "purchase": True
            }
        }
    )

    # 創建執行計劃
    plan = planner.create_execution_plan(task)

    # 顯示分解結構
    print("\n任務分解結構:")
    for i, t in enumerate(plan, 1):
        indent = "  " * t.id.count('.')
        print(f"{indent}{i}. [{t.id}] {t.name}")
        if t.dependencies:
            print(f"{indent}   依賴: {t.dependencies}")

    # 執行計劃
    results = planner.execute_plan(plan)

    return results


def 示例3_任務依賴管理():
    """示例：具有複雜依賴關係的任務"""
    print("\n" + "="*60)
    print("示例 3: 任務依賴管理")
    print("="*60)

    planner = TaskPlanner()

    # 創建多個相互依賴的任務
    tasks = [
        Task(id="T3.1", name="下載數據", description="從服務器下載數據文件"),
        Task(id="T3.2", name="數據清洗", description="清洗和預處理數據"),
        Task(id="T3.3", name="數據分析", description="執行統計分析"),
        Task(id="T3.4", name="生成圖表", description="創建可視化圖表"),
        Task(id="T3.5", name="編寫報告", description="撰寫分析報告"),
        Task(id="T3.6", name="發送報告", description="將報告發送給相關人員"),
    ]

    # 設置依賴關係
    tasks[1].add_dependency("T3.1")  # 數據清洗依賴下載
    tasks[2].add_dependency("T3.2")  # 分析依賴清洗
    tasks[3].add_dependency("T3.2")  # 圖表依賴清洗
    tasks[4].add_dependency("T3.3")  # 報告依賴分析
    tasks[4].add_dependency("T3.4")  # 報告依賴圖表
    tasks[5].add_dependency("T3.5")  # 發送依賴報告

    # 註冊任務
    for task in tasks:
        planner.tasks[task.id] = task
        # 添加一些模擬操作
        task.actions.append(Action(f"execute_{task.id}", task.description))

    # 創建執行順序
    plan = planner._topological_sort()

    print("\n執行順序（考慮依賴關係）:")
    for i, task in enumerate(plan, 1):
        deps = f" (依賴: {task.dependencies})" if task.dependencies else ""
        print(f"{i}. [{task.id}] {task.name}{deps}")

    # 執行計劃
    results = planner.execute_plan(plan)

    return results


def 示例4_動態計劃調整():
    """示例：根據執行結果動態調整計劃"""
    print("\n" + "="*60)
    print("示例 4: 動態計劃調整")
    print("="*60)

    planner = TaskPlanner()

    # 創建初始任務
    main_task = Task(
        id="T4",
        name="編輯文檔並分享",
        description="編輯文檔並通過郵件分享",
        priority=TaskPriority.HIGH,
        metadata={
            "filename": "報告.docx",
            "edits": {"section": "結論", "content": "更新內容"}
        }
    )

    # 創建計劃
    plan = planner.create_execution_plan(main_task)

    print("\n初始計劃:")
    for i, task in enumerate(plan, 1):
        print(f"{i}. {task.name}")

    # 執行並模擬調整
    print("\n執行過程中發現需要額外步驟...")

    # 動態添加新任務（例如：需要先轉換格式）
    new_task = Task(
        id="T4.1.5",
        name="轉換文檔格式",
        description="將文檔轉換為 PDF 格式",
        actions=[Action("convert", "轉換格式", {"format": "pdf"})]
    )
    new_task.add_dependency("T4.2")  # 在打開文件後執行

    planner.tasks[new_task.id] = new_task

    # 更新後續任務的依賴
    for task in plan:
        if task.id.startswith("T4.3"):
            task.add_dependency(new_task.id)

    # 重新計劃
    updated_plan = planner._topological_sort()

    print("\n調整後的計劃:")
    for i, task in enumerate(updated_plan, 1):
        print(f"{i}. {task.name}")

    results = planner.execute_plan(updated_plan)

    return results


if __name__ == "__main__":
    # 運行所有示例
    print("Agent-S 任務規劃演示\n")

    示例1_簡單任務規劃()
    示例2_複雜任務分解()
    示例3_任務依賴管理()
    示例4_動態計劃調整()

    print("\n所有示例執行完成！")

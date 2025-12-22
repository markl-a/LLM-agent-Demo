"""
Orchestrator - 協調者 Agent
===================================

Orchestrator 是 Magentic-One 的大腦，負責：
1. 理解和分解複雜任務
2. 制定執行計劃
3. 分配任務給專門化 Agent
4. 監控執行進度
5. 處理異常和重試
6. 整合最終結果

核心能力：
- 使用高級 LLM (GPT-4) 進行智能決策
- 維護任務上下文和狀態
- 動態調整執行策略
- 支持多種規劃模式（順序、並行、層次化）
"""

import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from enum import Enum


class PlanningStrategy(Enum):
    """規劃策略枚舉"""
    SEQUENTIAL = "sequential"      # 順序執行
    PARALLEL = "parallel"          # 並行執行
    HIERARCHICAL = "hierarchical"  # 層次化執行
    ADAPTIVE = "adaptive"          # 自適應執行


class TaskStatus(Enum):
    """任務狀態枚舉"""
    PENDING = "pending"
    PLANNING = "planning"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class OrchestratorAgent:
    """
    協調者 Agent

    負責整個任務的規劃、協調和執行控制
    """

    def __init__(
        self,
        llm_config: Dict[str, Any],
        max_rounds: int = 30,
        timeout: int = 600,
        planning_strategy: str = "hierarchical"
    ):
        """
        初始化 Orchestrator

        Args:
            llm_config: LLM 配置
            max_rounds: 最大執行輪數
            timeout: 超時時間（秒）
            planning_strategy: 規劃策略
        """
        self.llm_config = llm_config
        self.max_rounds = max_rounds
        self.timeout = timeout
        self.planning_strategy = PlanningStrategy(planning_strategy)

        # 註冊的 Agents
        self.agents: Dict[str, Any] = {}

        # 任務追蹤
        self.current_task = None
        self.task_status = TaskStatus.PENDING
        self.execution_history: List[Dict] = []

        # 統計數據
        self.stats = {
            'tasks_completed': 0,
            'tasks_failed': 0,
            'total_steps': 0,
            'llm_calls': 0
        }

    def register_agent(self, name: str, agent: Any, capabilities: List[str]):
        """
        註冊一個 Agent

        Args:
            name: Agent 名稱
            agent: Agent 實例
            capabilities: Agent 能力列表
        """
        self.agents[name] = {
            'instance': agent,
            'capabilities': capabilities,
            'status': 'active'
        }
        print(f"✓ 已註冊 Agent: {name} (能力: {', '.join(capabilities)})")

    def analyze_task(self, task: str) -> Dict[str, Any]:
        """
        分析任務並生成執行計劃

        Args:
            task: 任務描述

        Returns:
            任務計劃
        """
        print(f"\n{'='*60}")
        print(f"Orchestrator: 開始分析任務")
        print(f"{'='*60}")
        print(f"任務: {task}")
        print(f"規劃策略: {self.planning_strategy.value}")

        self.task_status = TaskStatus.PLANNING
        self.current_task = task

        # 1. 任務分解
        print("\n步驟 1: 任務分解")
        subtasks = self._decompose_task(task)
        print(f"  已分解為 {len(subtasks)} 個子任務")

        # 2. 能力匹配
        print("\n步驟 2: Agent 能力匹配")
        matched_plan = self._match_agents(subtasks)

        # 3. 依賴分析
        print("\n步驟 3: 依賴關係分析")
        plan_with_deps = self._analyze_dependencies(matched_plan)

        # 4. 優化執行順序
        print("\n步驟 4: 優化執行順序")
        optimized_plan = self._optimize_plan(plan_with_deps)

        # 5. 生成最終計劃
        final_plan = {
            'task_id': self._generate_task_id(),
            'description': task,
            'strategy': self.planning_strategy.value,
            'steps': optimized_plan,
            'created_at': datetime.now().isoformat(),
            'estimated_duration': self._estimate_duration(optimized_plan)
        }

        print(f"\n計劃生成完成:")
        print(f"  總步驟數: {len(final_plan['steps'])}")
        print(f"  預估耗時: {final_plan['estimated_duration']} 秒")

        return final_plan

    def _decompose_task(self, task: str) -> List[Dict]:
        """將任務分解為子任務"""
        self.stats['llm_calls'] += 1

        # 這裡簡化處理，實際應使用 LLM 進行智能分解
        subtasks = []

        # 檢測任務關鍵字並分解
        task_lower = task.lower()

        # 網頁搜索任務
        if any(kw in task_lower for kw in ['搜索', '查找', '調查', 'search', 'find']):
            subtasks.append({
                'type': 'web_search',
                'description': '搜索相關信息',
                'priority': 1
            })

        # 數據處理任務
        if any(kw in task_lower for kw in ['分析', '處理', '計算', 'analyze', 'process']):
            subtasks.append({
                'type': 'data_processing',
                'description': '處理和分析數據',
                'priority': 2
            })

        # 代碼生成任務
        if any(kw in task_lower for kw in ['生成代碼', '編程', '開發', 'code', 'develop']):
            subtasks.append({
                'type': 'code_generation',
                'description': '生成代碼',
                'priority': 3
            })

        # 文件操作任務
        if any(kw in task_lower for kw in ['保存', '讀取', '文件', 'save', 'read', 'file']):
            subtasks.append({
                'type': 'file_operation',
                'description': '文件讀寫操作',
                'priority': 4
            })

        # 如果沒有匹配到特定任務，創建通用任務
        if not subtasks:
            subtasks.append({
                'type': 'general',
                'description': task,
                'priority': 1
            })

        return subtasks

    def _match_agents(self, subtasks: List[Dict]) -> List[Dict]:
        """將子任務匹配到合適的 Agent"""
        matched = []

        # Agent 能力映射
        capability_mapping = {
            'web_search': 'web_surfer',
            'data_processing': 'coder',
            'code_generation': 'coder',
            'file_operation': 'file_surfer',
            'terminal_command': 'terminal',
            'general': 'coder'  # 默認使用 coder
        }

        for subtask in subtasks:
            task_type = subtask['type']
            agent_name = capability_mapping.get(task_type, 'coder')

            if agent_name in self.agents:
                matched.append({
                    **subtask,
                    'agent': agent_name,
                    'agent_status': self.agents[agent_name]['status']
                })
                print(f"  ✓ {subtask['description']} → {agent_name}")
            else:
                print(f"  ✗ 無法為 '{subtask['description']}' 找到合適的 Agent")

        return matched

    def _analyze_dependencies(self, plan: List[Dict]) -> List[Dict]:
        """分析步驟之間的依賴關係"""
        for i, step in enumerate(plan):
            # 簡化處理：根據優先級設置依賴
            if i > 0:
                # 當前步驟依賴前一個步驟
                step['depends_on'] = [i - 1]
            else:
                step['depends_on'] = []

            # 並行執行的步驟（相同優先級）
            step['can_parallel'] = any(
                s['priority'] == step['priority'] and s != step
                for s in plan
            )

        return plan

    def _optimize_plan(self, plan: List[Dict]) -> List[Dict]:
        """根據規劃策略優化執行計劃"""
        if self.planning_strategy == PlanningStrategy.SEQUENTIAL:
            # 順序執行：按優先級排序
            return sorted(plan, key=lambda x: x['priority'])

        elif self.planning_strategy == PlanningStrategy.PARALLEL:
            # 並行執行：標記可並行的步驟
            for step in plan:
                step['parallel_group'] = step['priority']
            return plan

        elif self.planning_strategy == PlanningStrategy.HIERARCHICAL:
            # 層次化執行：構建層次結構
            return self._build_hierarchy(plan)

        else:  # ADAPTIVE
            # 自適應：根據當前狀態動態調整
            return self._adaptive_optimize(plan)

    def _build_hierarchy(self, plan: List[Dict]) -> List[Dict]:
        """構建層次化執行計劃"""
        # 按優先級分組
        levels = {}
        for step in plan:
            priority = step['priority']
            if priority not in levels:
                levels[priority] = []
            levels[priority].append(step)

        # 重新組織為層次結構
        hierarchical = []
        for priority in sorted(levels.keys()):
            for step in levels[priority]:
                step['level'] = priority
                hierarchical.append(step)

        return hierarchical

    def _adaptive_optimize(self, plan: List[Dict]) -> List[Dict]:
        """自適應優化"""
        # 根據 Agent 狀態和歷史性能動態調整
        for step in plan:
            agent_name = step['agent']
            # 這裡可以根據歷史數據調整優先級
            step['adjusted_priority'] = step['priority']

        return sorted(plan, key=lambda x: x.get('adjusted_priority', x['priority']))

    def execute_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        執行計劃

        Args:
            plan: 執行計劃

        Returns:
            執行結果
        """
        print(f"\n{'='*60}")
        print(f"Orchestrator: 開始執行計劃")
        print(f"{'='*60}")

        self.task_status = TaskStatus.EXECUTING
        start_time = datetime.now()
        results = []
        errors = []

        try:
            for i, step in enumerate(plan['steps'], 1):
                print(f"\n執行步驟 {i}/{len(plan['steps'])}: {step['description']}")

                # 檢查依賴
                if not self._check_dependencies(step, results):
                    print(f"  ⚠ 依賴未滿足，跳過此步驟")
                    continue

                # 執行步驟
                try:
                    result = self._execute_step(step)
                    results.append({
                        'step_id': i,
                        'status': 'success',
                        'result': result,
                        'timestamp': datetime.now().isoformat()
                    })
                    print(f"  ✓ 步驟 {i} 完成")

                except Exception as e:
                    error_info = {
                        'step_id': i,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    }
                    errors.append(error_info)
                    print(f"  ✗ 步驟 {i} 失敗: {e}")

                    # 重試邏輯
                    if self._should_retry(step, error_info):
                        print(f"  ↻ 重試步驟 {i}...")
                        retry_result = self._retry_step(step)
                        if retry_result:
                            results.append(retry_result)
                            print(f"  ✓ 重試成功")
                        else:
                            print(f"  ✗ 重試失敗")

                self.stats['total_steps'] += 1

            # 整合結果
            final_result = self._integrate_results(results)

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            self.task_status = TaskStatus.COMPLETED
            self.stats['tasks_completed'] += 1

            return {
                'task_id': plan['task_id'],
                'status': 'completed',
                'duration': duration,
                'steps_completed': len(results),
                'steps_failed': len(errors),
                'result': final_result,
                'errors': errors
            }

        except Exception as e:
            self.task_status = TaskStatus.FAILED
            self.stats['tasks_failed'] += 1
            raise

    def _check_dependencies(self, step: Dict, completed_results: List[Dict]) -> bool:
        """檢查步驟依賴是否滿足"""
        depends_on = step.get('depends_on', [])
        if not depends_on:
            return True

        completed_ids = {r['step_id'] for r in completed_results if r['status'] == 'success'}
        return all(dep_id in completed_ids for dep_id in depends_on)

    def _execute_step(self, step: Dict) -> Any:
        """執行單個步驟"""
        agent_name = step['agent']
        if agent_name not in self.agents:
            raise ValueError(f"Agent '{agent_name}' 不存在")

        agent = self.agents[agent_name]['instance']

        # 構建執行參數
        action = {
            'type': step['type'],
            'description': step['description'],
            'params': step.get('params', {})
        }

        # 執行
        return agent.execute(action)

    def _should_retry(self, step: Dict, error_info: Dict) -> bool:
        """判斷是否應該重試"""
        # 簡化判斷：允許重試一次
        retry_count = step.get('retry_count', 0)
        return retry_count < 1

    def _retry_step(self, step: Dict) -> Optional[Dict]:
        """重試步驟"""
        step['retry_count'] = step.get('retry_count', 0) + 1
        self.task_status = TaskStatus.RETRYING

        try:
            result = self._execute_step(step)
            return {
                'step_id': step.get('step_id'),
                'status': 'success',
                'result': result,
                'retried': True
            }
        except Exception as e:
            print(f"重試失敗: {e}")
            return None

    def _integrate_results(self, results: List[Dict]) -> Dict:
        """整合所有步驟的結果"""
        print("\n整合執行結果...")

        integrated = {
            'summary': f'成功執行 {len(results)} 個步驟',
            'results': results,
            'metadata': {
                'total_steps': len(results),
                'success_rate': len(results) / max(self.stats['total_steps'], 1)
            }
        }

        return integrated

    def _estimate_duration(self, plan: List[Dict]) -> int:
        """估算執行時長"""
        # 簡化估算：每步 10 秒
        base_time = len(plan) * 10

        # 根據策略調整
        if self.planning_strategy == PlanningStrategy.PARALLEL:
            # 並行執行可能更快
            base_time = base_time * 0.6

        return int(base_time)

    def _generate_task_id(self) -> str:
        """生成任務 ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"task_{timestamp}"

    def get_statistics(self) -> Dict[str, Any]:
        """獲取統計數據"""
        return {
            'tasks_completed': self.stats['tasks_completed'],
            'tasks_failed': self.stats['tasks_failed'],
            'total_steps': self.stats['total_steps'],
            'llm_calls': self.stats['llm_calls'],
            'success_rate': self.stats['tasks_completed'] / max(
                self.stats['tasks_completed'] + self.stats['tasks_failed'], 1
            )
        }


# 模擬 Agent 類別用於測試
class MockAgent:
    """模擬 Agent"""

    def __init__(self, name: str):
        self.name = name

    def execute(self, action: Dict) -> Dict:
        """執行操作"""
        return {
            'agent': self.name,
            'action': action['type'],
            'status': 'completed'
        }


def demo_basic_orchestration():
    """基礎協調示範"""
    print("=" * 60)
    print("範例 1: 基礎任務協調")
    print("=" * 60)

    # 創建 Orchestrator
    orchestrator = OrchestratorAgent(
        llm_config={"model": "gpt-4"},
        planning_strategy="sequential"
    )

    # 註冊 Agents
    orchestrator.register_agent(
        "web_surfer",
        MockAgent("WebSurfer"),
        ["web_search", "web_navigation"]
    )
    orchestrator.register_agent(
        "coder",
        MockAgent("Coder"),
        ["code_generation", "data_processing"]
    )
    orchestrator.register_agent(
        "file_surfer",
        MockAgent("FileSurfer"),
        ["file_operation"]
    )

    # 分析任務
    task = "搜索 Python 最佳實踐，生成範例代碼，並保存到文件"
    plan = orchestrator.analyze_task(task)

    print("\n生成的執行計劃:")
    print(json.dumps(plan, indent=2, ensure_ascii=False))


def demo_parallel_execution():
    """並行執行示範"""
    print("\n" + "=" * 60)
    print("範例 2: 並行執行策略")
    print("=" * 60)

    orchestrator = OrchestratorAgent(
        llm_config={"model": "gpt-4"},
        planning_strategy="parallel"
    )

    # 註冊 Agents
    orchestrator.register_agent("web_surfer", MockAgent("WebSurfer"), ["web_search"])
    orchestrator.register_agent("coder", MockAgent("Coder"), ["code_generation"])
    orchestrator.register_agent("file_surfer", MockAgent("FileSurfer"), ["file_operation"])

    task = "同時搜索三個主題：AI、區塊鏈、量子計算"
    plan = orchestrator.analyze_task(task)
    result = orchestrator.execute_plan(plan)

    print("\n執行結果:")
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))


def demo_error_handling():
    """錯誤處理示範"""
    print("\n" + "=" * 60)
    print("範例 3: 錯誤處理和重試")
    print("=" * 60)

    orchestrator = OrchestratorAgent(
        llm_config={"model": "gpt-4"},
        planning_strategy="adaptive"
    )

    orchestrator.register_agent("coder", MockAgent("Coder"), ["code_generation"])

    task = "生成複雜的機器學習模型代碼"
    plan = orchestrator.analyze_task(task)

    # 執行並查看統計
    result = orchestrator.execute_plan(plan)
    stats = orchestrator.get_statistics()

    print("\n統計數據:")
    print(json.dumps(stats, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    demo_basic_orchestration()
    demo_parallel_execution()
    demo_error_handling()

    print("\n" + "=" * 60)
    print("Orchestrator 示範完成！")
    print("=" * 60)

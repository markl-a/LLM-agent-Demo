"""
團隊協作 - 多 Agent 協同工作
===================================

本範例展示 Magentic-One 中多個 Agent 如何協同工作完成複雜任務。

協作模式：
1. 順序協作 - Agent 按順序執行任務
2. 並行協作 - 多個 Agent 同時執行不同子任務
3. 迭代協作 - Agent 之間反覆交互直到完成
4. 層次化協作 - 按優先級分層執行

關鍵組件：
- Orchestrator: 協調所有 Agent
- Agent 通信機制
- 結果整合
- 錯誤處理和恢復
"""

import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from enum import Enum


class CollaborationMode(Enum):
    """協作模式"""
    SEQUENTIAL = "sequential"    # 順序
    PARALLEL = "parallel"        # 並行
    ITERATIVE = "iterative"      # 迭代
    HIERARCHICAL = "hierarchical"  # 層次化


class AgentTeam:
    """
    Agent 團隊

    管理多個 Agent 的協同工作
    """

    def __init__(
        self,
        orchestrator: Any,
        collaboration_mode: str = "sequential"
    ):
        """
        初始化團隊

        Args:
            orchestrator: 協調者
            collaboration_mode: 協作模式
        """
        self.orchestrator = orchestrator
        self.collaboration_mode = CollaborationMode(collaboration_mode)
        self.agents: Dict[str, Any] = {}
        self.shared_context: Dict[str, Any] = {}
        self.message_queue: List[Dict] = []

    def add_agent(self, name: str, agent: Any, role: str):
        """添加 Agent 到團隊"""
        self.agents[name] = {
            'instance': agent,
            'role': role,
            'status': 'ready'
        }
        print(f"✓ 添加 Agent: {name} (角色: {role})")

    def execute_task(self, task: str) -> Dict[str, Any]:
        """
        執行團隊任務

        Args:
            task: 任務描述

        Returns:
            執行結果
        """
        print(f"\n{'='*60}")
        print(f"團隊任務: {task}")
        print(f"協作模式: {self.collaboration_mode.value}")
        print(f"{'='*60}\n")

        # 1. Orchestrator 制定計劃
        plan = self.orchestrator.analyze_task(task)

        # 2. 根據協作模式執行
        if self.collaboration_mode == CollaborationMode.SEQUENTIAL:
            result = self._execute_sequential(plan)
        elif self.collaboration_mode == CollaborationMode.PARALLEL:
            result = self._execute_parallel(plan)
        elif self.collaboration_mode == CollaborationMode.ITERATIVE:
            result = self._execute_iterative(plan)
        else:  # HIERARCHICAL
            result = self._execute_hierarchical(plan)

        return result

    def _execute_sequential(self, plan: Dict) -> Dict[str, Any]:
        """順序執行"""
        print("\n執行模式: 順序協作")
        print("─" * 60)

        results = []
        for i, step in enumerate(plan['steps'], 1):
            print(f"\n步驟 {i}: {step['description']}")
            print(f"  分配給: {step['agent']}")

            # 獲取前一步的結果作為上下文
            previous_result = results[-1] if results else None

            # 執行步驟
            result = self._execute_step(
                step,
                context={'previous_result': previous_result}
            )

            results.append(result)

            # 更新共享上下文
            self._update_shared_context(step['agent'], result)

            print(f"  ✓ 完成")

        return {
            'mode': 'sequential',
            'results': results,
            'final_context': self.shared_context
        }

    def _execute_parallel(self, plan: Dict) -> Dict[str, Any]:
        """並行執行"""
        print("\n執行模式: 並行協作")
        print("─" * 60)

        # 按優先級分組
        groups = self._group_by_priority(plan['steps'])

        all_results = []

        for priority, steps in sorted(groups.items()):
            print(f"\n優先級 {priority} 組（{len(steps)} 個任務）")

            # 並行執行同優先級的步驟
            group_results = []
            for step in steps:
                print(f"  ↻ 並行執行: {step['description']} ({step['agent']})")
                result = self._execute_step(step, context={})
                group_results.append(result)
                print(f"  ✓ 完成")

            all_results.extend(group_results)

        return {
            'mode': 'parallel',
            'groups': len(groups),
            'results': all_results
        }

    def _execute_iterative(self, plan: Dict) -> Dict[str, Any]:
        """迭代執行"""
        print("\n執行模式: 迭代協作")
        print("─" * 60)

        max_iterations = 5
        iteration = 0
        results = []
        task_complete = False

        while not task_complete and iteration < max_iterations:
            iteration += 1
            print(f"\n迭代 {iteration}")

            for step in plan['steps']:
                print(f"  執行: {step['description']} ({step['agent']})")

                # 使用共享上下文
                result = self._execute_step(step, context=self.shared_context)
                results.append(result)

                # 更新共享上下文
                self._update_shared_context(step['agent'], result)

                # 檢查是否完成（簡化判斷）
                if self._check_completion(result):
                    task_complete = True
                    break

            if task_complete:
                print(f"\n✓ 任務在第 {iteration} 次迭代後完成")

        return {
            'mode': 'iterative',
            'iterations': iteration,
            'completed': task_complete,
            'results': results
        }

    def _execute_hierarchical(self, plan: Dict) -> Dict[str, Any]:
        """層次化執行"""
        print("\n執行模式: 層次化協作")
        print("─" * 60)

        # 構建層次結構
        levels = self._build_hierarchy(plan['steps'])

        all_results = []

        for level, steps in sorted(levels.items()):
            print(f"\n層級 {level} ({len(steps)} 個任務)")

            level_results = []
            for step in steps:
                print(f"  執行: {step['description']} ({step['agent']})")

                # 使用前一層級的結果
                previous_level_results = all_results if all_results else None

                result = self._execute_step(
                    step,
                    context={'previous_level': previous_level_results}
                )

                level_results.append(result)
                print(f"  ✓ 完成")

            all_results.extend(level_results)

        return {
            'mode': 'hierarchical',
            'levels': len(levels),
            'results': all_results
        }

    def _execute_step(self, step: Dict, context: Dict) -> Dict[str, Any]:
        """執行單個步驟"""
        agent_name = step['agent']

        if agent_name not in self.agents:
            return {
                'success': False,
                'error': f'Agent {agent_name} 不存在'
            }

        agent = self.agents[agent_name]['instance']

        # 構建操作
        action = {
            'type': step['type'],
            'description': step['description'],
            'context': context
        }

        # 執行
        try:
            result = agent.execute(action)
            return {
                'success': True,
                'agent': agent_name,
                'result': result,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'agent': agent_name,
                'error': str(e)
            }

    def _update_shared_context(self, agent_name: str, result: Dict):
        """更新共享上下文"""
        self.shared_context[agent_name] = result

    def _group_by_priority(self, steps: List[Dict]) -> Dict[int, List[Dict]]:
        """按優先級分組"""
        groups = {}
        for step in steps:
            priority = step.get('priority', 1)
            if priority not in groups:
                groups[priority] = []
            groups[priority].append(step)
        return groups

    def _build_hierarchy(self, steps: List[Dict]) -> Dict[int, List[Dict]]:
        """構建層次結構"""
        levels = {}
        for step in steps:
            level = step.get('level', step.get('priority', 1))
            if level not in levels:
                levels[level] = []
            levels[level].append(step)
        return levels

    def _check_completion(self, result: Dict) -> bool:
        """檢查任務是否完成"""
        # 簡化判斷
        return result.get('success', False)

    def broadcast_message(self, message: str, sender: str):
        """廣播消息給所有 Agent"""
        print(f"\n📢 {sender} 廣播: {message}")

        msg = {
            'sender': sender,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }

        self.message_queue.append(msg)

    def send_message(self, message: str, sender: str, receiver: str):
        """發送消息給特定 Agent"""
        print(f"\n✉️ {sender} → {receiver}: {message}")

        msg = {
            'sender': sender,
            'receiver': receiver,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }

        self.message_queue.append(msg)

    def get_team_status(self) -> Dict[str, Any]:
        """獲取團隊狀態"""
        return {
            'team_size': len(self.agents),
            'agents': {
                name: info['status']
                for name, info in self.agents.items()
            },
            'collaboration_mode': self.collaboration_mode.value,
            'messages_exchanged': len(self.message_queue)
        }


# 模擬 Agent 和 Orchestrator
class MockOrchestrator:
    """模擬協調者"""

    def analyze_task(self, task: str) -> Dict:
        """分析任務"""
        return {
            'task': task,
            'steps': [
                {
                    'description': '搜索相關信息',
                    'agent': 'web_surfer',
                    'type': 'web_search',
                    'priority': 1,
                    'level': 1
                },
                {
                    'description': '處理數據',
                    'agent': 'coder',
                    'type': 'data_processing',
                    'priority': 2,
                    'level': 2
                },
                {
                    'description': '保存結果',
                    'agent': 'file_surfer',
                    'type': 'file_operation',
                    'priority': 3,
                    'level': 3
                }
            ]
        }


class MockAgent:
    """模擬 Agent"""

    def __init__(self, name: str):
        self.name = name

    def execute(self, action: Dict) -> Dict:
        """執行操作"""
        return {
            'agent': self.name,
            'action': action['type'],
            'description': action['description'],
            'status': 'completed'
        }


def demo_sequential_collaboration():
    """順序協作示範"""
    print("=" * 60)
    print("範例 1: 順序協作")
    print("=" * 60)

    orchestrator = MockOrchestrator()
    team = AgentTeam(orchestrator, collaboration_mode="sequential")

    # 添加 Agents
    team.add_agent("web_surfer", MockAgent("WebSurfer"), "信息收集")
    team.add_agent("coder", MockAgent("Coder"), "數據處理")
    team.add_agent("file_surfer", MockAgent("FileSurfer"), "文件操作")

    # 執行任務
    result = team.execute_task("研究 Python 最新特性並生成報告")

    print("\n執行結果:")
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))


def demo_parallel_collaboration():
    """並行協作示範"""
    print("\n" + "=" * 60)
    print("範例 2: 並行協作")
    print("=" * 60)

    orchestrator = MockOrchestrator()
    team = AgentTeam(orchestrator, collaboration_mode="parallel")

    team.add_agent("web_surfer", MockAgent("WebSurfer"), "信息收集")
    team.add_agent("coder", MockAgent("Coder"), "數據處理")
    team.add_agent("file_surfer", MockAgent("FileSurfer"), "文件操作")

    result = team.execute_task("同時處理多個數據源")

    print("\n執行結果:")
    print(f"並行組數: {result['groups']}")
    print(f"總任務數: {len(result['results'])}")


def demo_iterative_collaboration():
    """迭代協作示範"""
    print("\n" + "=" * 60)
    print("範例 3: 迭代協作")
    print("=" * 60)

    orchestrator = MockOrchestrator()
    team = AgentTeam(orchestrator, collaboration_mode="iterative")

    team.add_agent("web_surfer", MockAgent("WebSurfer"), "信息收集")
    team.add_agent("coder", MockAgent("Coder"), "代碼生成")
    team.add_agent("file_surfer", MockAgent("FileSurfer"), "結果驗證")

    result = team.execute_task("生成並測試代碼直到通過")

    print("\n執行結果:")
    print(f"迭代次數: {result['iterations']}")
    print(f"是否完成: {result['completed']}")


def demo_hierarchical_collaboration():
    """層次化協作示範"""
    print("\n" + "=" * 60)
    print("範例 4: 層次化協作")
    print("=" * 60)

    orchestrator = MockOrchestrator()
    team = AgentTeam(orchestrator, collaboration_mode="hierarchical")

    team.add_agent("web_surfer", MockAgent("WebSurfer"), "L1-信息收集")
    team.add_agent("coder", MockAgent("Coder"), "L2-數據處理")
    team.add_agent("file_surfer", MockAgent("FileSurfer"), "L3-結果保存")

    result = team.execute_task("多層次數據處理流程")

    print("\n執行結果:")
    print(f"層級數: {result['levels']}")
    print(f"總任務數: {len(result['results'])}")


def demo_agent_communication():
    """Agent 通信示範"""
    print("\n" + "=" * 60)
    print("範例 5: Agent 間通信")
    print("=" * 60)

    orchestrator = MockOrchestrator()
    team = AgentTeam(orchestrator)

    team.add_agent("web_surfer", MockAgent("WebSurfer"), "信息收集")
    team.add_agent("coder", MockAgent("Coder"), "數據處理")
    team.add_agent("file_surfer", MockAgent("FileSurfer"), "文件操作")

    # 廣播消息
    team.broadcast_message("開始執行任務", "Orchestrator")

    # 點對點消息
    team.send_message("數據已準備好", "web_surfer", "coder")
    team.send_message("處理完成", "coder", "file_surfer")

    # 查看團隊狀態
    status = team.get_team_status()

    print("\n團隊狀態:")
    print(json.dumps(status, indent=2, ensure_ascii=False))


def demo_complex_workflow():
    """複雜工作流示範"""
    print("\n" + "=" * 60)
    print("範例 6: 複雜工作流")
    print("=" * 60)

    print("""
    複雜工作流示例：構建數據分析報告

    階段 1（並行）:
        ├─ WebSurfer: 收集在線數據
        ├─ FileSurfer: 讀取本地數據
        └─ Coder: 準備分析腳本

    階段 2（順序）:
        └─ Coder: 合併和清理數據

    階段 3（迭代）:
        ├─ Coder: 分析數據
        ├─ Coder: 生成可視化
        └─ FileSurfer: 驗證結果
        └─ 重複直到滿意

    階段 4（順序）:
        ├─ Coder: 生成報告
        └─ FileSurfer: 保存最終報告

    協調流程：
        Orchestrator
            ↓
        階段規劃
            ↓
        Agent 分配
            ↓
        執行監控
            ↓
        結果整合
    """)

    orchestrator = MockOrchestrator()

    # 階段 1: 並行收集
    print("\n階段 1: 並行數據收集")
    team1 = AgentTeam(orchestrator, collaboration_mode="parallel")
    team1.add_agent("web_surfer", MockAgent("WebSurfer"), "在線數據")
    team1.add_agent("file_surfer", MockAgent("FileSurfer"), "本地數據")
    team1.add_agent("coder", MockAgent("Coder"), "腳本準備")
    result1 = team1.execute_task("收集數據")

    # 階段 2: 順序處理
    print("\n階段 2: 順序數據處理")
    team2 = AgentTeam(orchestrator, collaboration_mode="sequential")
    team2.add_agent("coder", MockAgent("Coder"), "數據處理")
    result2 = team2.execute_task("清理和合併數據")

    # 階段 3: 迭代分析
    print("\n階段 3: 迭代分析")
    team3 = AgentTeam(orchestrator, collaboration_mode="iterative")
    team3.add_agent("coder", MockAgent("Coder"), "數據分析")
    team3.add_agent("file_surfer", MockAgent("FileSurfer"), "結果驗證")
    result3 = team3.execute_task("分析和驗證")

    # 階段 4: 順序報告
    print("\n階段 4: 生成最終報告")
    team4 = AgentTeam(orchestrator, collaboration_mode="sequential")
    team4.add_agent("coder", MockAgent("Coder"), "報告生成")
    team4.add_agent("file_surfer", MockAgent("FileSurfer"), "報告保存")
    result4 = team4.execute_task("生成和保存報告")

    print("\n✓ 複雜工作流執行完成")


if __name__ == "__main__":
    demo_sequential_collaboration()
    demo_parallel_collaboration()
    demo_iterative_collaboration()
    demo_hierarchical_collaboration()
    demo_agent_communication()
    demo_complex_workflow()

    print("\n" + "=" * 60)
    print("團隊協作示範完成！")
    print("=" * 60)

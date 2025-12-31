"""
Strands Agents 多 Agent 協作示例

這個示例展示了如何實現多個 Agent 之間的協作：
1. Agent 間的通訊機制
2. 順序執行工作流
3. 並行執行工作流
4. 條件分支執行
5. Agent 路由和調度
6. 共享上下文管理
7. 任務分解和委派
8. 協作模式（辯論、投票、共識）

多 Agent 協作是構建複雜 AI 系統的關鍵，
能夠結合不同 Agent 的專長來解決複雜問題。

作者: Strands Agents Team
日期: 2025-01
"""

import os
import sys
import json
import logging
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import asyncio
from abc import ABC, abstractmethod

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# 核心數據結構
# ============================================================================

@dataclass
class Task:
    """
    任務定義

    Attributes:
        id: 任務 ID
        description: 任務描述
        input_data: 輸入數據
        output_data: 輸出數據
        status: 任務狀態
        assigned_agent: 分配的 Agent
        created_at: 創建時間
        completed_at: 完成時間
    """
    id: str
    description: str
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    status: str = "pending"  # pending, running, completed, failed
    assigned_agent: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "id": self.id,
            "description": self.description,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "status": self.status,
            "assigned_agent": self.assigned_agent,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error": self.error
        }


class WorkflowType(Enum):
    """工作流類型"""
    SEQUENTIAL = "sequential"      # 順序執行
    PARALLEL = "parallel"          # 並行執行
    CONDITIONAL = "conditional"    # 條件分支
    LOOP = "loop"                  # 循環執行


# ============================================================================
# Agent 基類
# ============================================================================

class BaseAgent(ABC):
    """
    Agent 基類

    所有 Agent 都應繼承此類
    """

    def __init__(
        self,
        name: str,
        role: str,
        capabilities: List[str]
    ):
        self.name = name
        self.role = role
        self.capabilities = capabilities
        self.task_history: List[Task] = []

        logger.info(f"創建 Agent: {name} (角色: {role})")

    @abstractmethod
    def execute(self, task: Task) -> Dict[str, Any]:
        """
        執行任務

        Args:
            task: 任務對象

        Returns:
            Dict: 執行結果
        """
        pass

    def can_handle(self, task: Task) -> bool:
        """
        判斷是否能處理該任務

        Args:
            task: 任務對象

        Returns:
            bool: 是否能處理
        """
        # 檢查任務類型是否在能力範圍內
        task_type = task.input_data.get("type", "")
        return task_type in self.capabilities

    def add_to_history(self, task: Task):
        """添加任務到歷史記錄"""
        self.task_history.append(task)


# ============================================================================
# 專業 Agent 實現
# ============================================================================

class ResearchAgent(BaseAgent):
    """
    研究 Agent

    專門負責信息收集和研究任務
    """

    def __init__(self, name: str = "研究員"):
        super().__init__(
            name=name,
            role="研究員",
            capabilities=["research", "search", "analysis"]
        )

    def execute(self, task: Task) -> Dict[str, Any]:
        """執行研究任務"""
        logger.info(f"{self.name} 開始研究: {task.description}")

        # 模擬研究過程
        query = task.input_data.get("query", "")

        # 模擬搜索和分析
        research_results = {
            "query": query,
            "findings": [
                f"發現 1: 關於 {query} 的重要信息",
                f"發現 2: {query} 的相關數據",
                f"發現 3: {query} 的最新趨勢"
            ],
            "sources": [
                "來源 A", "來源 B", "來源 C"
            ],
            "summary": f"關於 {query} 的研究總結"
        }

        logger.info(f"{self.name} 完成研究")

        return research_results


class WriterAgent(BaseAgent):
    """
    寫作 Agent

    專門負責內容創作和文檔撰寫
    """

    def __init__(self, name: str = "作家"):
        super().__init__(
            name=name,
            role="作家",
            capabilities=["writing", "editing", "content_creation"]
        )

    def execute(self, task: Task) -> Dict[str, Any]:
        """執行寫作任務"""
        logger.info(f"{self.name} 開始寫作: {task.description}")

        # 獲取輸入內容
        topic = task.input_data.get("topic", "")
        research_data = task.input_data.get("research_data", {})

        # 模擬寫作過程
        content = self._generate_content(topic, research_data)

        result = {
            "topic": topic,
            "content": content,
            "word_count": len(content.split()),
            "sections": ["引言", "主體", "結論"]
        }

        logger.info(f"{self.name} 完成寫作")

        return result

    def _generate_content(
        self,
        topic: str,
        research_data: Dict[str, Any]
    ) -> str:
        """生成內容"""
        # 簡化的內容生成
        content_parts = [
            f"# {topic}\n",
            "\n## 引言\n",
            f"本文將探討 {topic} 的相關主題。\n",
            "\n## 主體內容\n"
        ]

        # 添加研究發現
        if "findings" in research_data:
            content_parts.append("根據研究發現：\n")
            for finding in research_data["findings"]:
                content_parts.append(f"- {finding}\n")

        content_parts.append("\n## 結論\n")
        content_parts.append(f"綜上所述，{topic} 是一個重要的主題。\n")

        return "".join(content_parts)


class ReviewerAgent(BaseAgent):
    """
    審核 Agent

    專門負責內容審核和質量檢查
    """

    def __init__(self, name: str = "審核員"):
        super().__init__(
            name=name,
            role="審核員",
            capabilities=["review", "quality_check", "editing"]
        )

    def execute(self, task: Task) -> Dict[str, Any]:
        """執行審核任務"""
        logger.info(f"{self.name} 開始審核: {task.description}")

        content = task.input_data.get("content", "")

        # 模擬審核過程
        review_result = {
            "approved": True,
            "quality_score": 8.5,
            "comments": [
                "內容結構清晰",
                "論據充分",
                "建議：可以添加更多實例"
            ],
            "suggestions": [
                "增加具體案例",
                "優化段落過渡"
            ],
            "revised_content": content  # 在實際中可能會有修訂
        }

        logger.info(f"{self.name} 完成審核，評分: {review_result['quality_score']}")

        return review_result


class CoordinatorAgent(BaseAgent):
    """
    協調 Agent

    負責任務分配和整體協調
    """

    def __init__(self, name: str = "協調員"):
        super().__init__(
            name=name,
            role="協調員",
            capabilities=["coordination", "planning", "task_allocation"]
        )

    def execute(self, task: Task) -> Dict[str, Any]:
        """執行協調任務"""
        logger.info(f"{self.name} 開始協調: {task.description}")

        # 分析任務並制定計劃
        plan = self._create_execution_plan(task)

        result = {
            "plan": plan,
            "status": "plan_created"
        }

        logger.info(f"{self.name} 完成協調計劃")

        return result

    def _create_execution_plan(self, task: Task) -> List[Dict[str, Any]]:
        """創建執行計劃"""
        # 簡化的計劃創建
        return [
            {"step": 1, "agent": "research", "action": "收集資料"},
            {"step": 2, "agent": "writer", "action": "撰寫內容"},
            {"step": 3, "agent": "reviewer", "action": "審核質量"}
        ]


# ============================================================================
# 工作流編排器
# ============================================================================

class AgentOrchestrator:
    """
    Agent 編排器

    管理多個 Agent 的協作和工作流執行
    """

    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.workflows: Dict[str, Dict[str, Any]] = {}
        self.shared_context: Dict[str, Any] = {}

        logger.info("初始化 Agent 編排器")

    def register_agent(self, agent: BaseAgent):
        """註冊 Agent"""
        self.agents[agent.name] = agent
        logger.info(f"註冊 Agent: {agent.name} ({agent.role})")

    def execute_sequential(
        self,
        tasks: List[Task],
        agent_names: List[str]
    ) -> List[Dict[str, Any]]:
        """
        順序執行工作流

        每個任務按順序分配給對應的 Agent 執行

        Args:
            tasks: 任務列表
            agent_names: Agent 名稱列表（與任務對應）

        Returns:
            List[Dict]: 執行結果列表
        """
        logger.info("開始順序執行工作流")

        results = []
        context = {}

        for i, (task, agent_name) in enumerate(zip(tasks, agent_names)):
            logger.info(f"步驟 {i+1}/{len(tasks)}: {task.description}")

            # 將前一步的結果作為上下文
            task.input_data["context"] = context

            # 獲取 Agent 並執行
            agent = self.agents.get(agent_name)
            if not agent:
                logger.error(f"Agent 不存在: {agent_name}")
                continue

            task.status = "running"
            task.assigned_agent = agent_name

            try:
                result = agent.execute(task)
                task.output_data = result
                task.status = "completed"
                task.completed_at = datetime.now()

                # 更新上下文
                context.update(result)

                results.append(result)

            except Exception as e:
                logger.error(f"任務執行失敗: {str(e)}")
                task.status = "failed"
                task.error = str(e)

            agent.add_to_history(task)

        logger.info("順序執行完成")

        return results

    async def execute_parallel(
        self,
        tasks: List[Task],
        agent_names: List[str]
    ) -> List[Dict[str, Any]]:
        """
        並行執行工作流

        多個任務同時分配給不同的 Agent 並行執行

        Args:
            tasks: 任務列表
            agent_names: Agent 名稱列表

        Returns:
            List[Dict]: 執行結果列表
        """
        logger.info("開始並行執行工作流")

        async def execute_task(task: Task, agent_name: str):
            """執行單個任務"""
            agent = self.agents.get(agent_name)
            if not agent:
                return None

            task.status = "running"
            task.assigned_agent = agent_name

            # 模擬異步執行
            await asyncio.sleep(0.1)

            try:
                result = agent.execute(task)
                task.output_data = result
                task.status = "completed"
                task.completed_at = datetime.now()

                agent.add_to_history(task)

                return result

            except Exception as e:
                logger.error(f"任務執行失敗: {str(e)}")
                task.status = "failed"
                task.error = str(e)
                return None

        # 並行執行所有任務
        results = await asyncio.gather(*[
            execute_task(task, agent_name)
            for task, agent_name in zip(tasks, agent_names)
        ])

        logger.info("並行執行完成")

        return [r for r in results if r is not None]

    def execute_conditional(
        self,
        task: Task,
        condition_func: Callable[[Task], str],
        agent_mapping: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        條件執行工作流

        根據條件選擇不同的 Agent 執行

        Args:
            task: 任務
            condition_func: 條件判斷函數
            agent_mapping: 條件到 Agent 的映射

        Returns:
            Dict: 執行結果
        """
        logger.info("開始條件執行工作流")

        # 評估條件
        condition_result = condition_func(task)
        logger.info(f"條件評估結果: {condition_result}")

        # 選擇對應的 Agent
        agent_name = agent_mapping.get(condition_result)
        if not agent_name or agent_name not in self.agents:
            logger.error(f"無效的 Agent 選擇: {agent_name}")
            return {}

        # 執行任務
        agent = self.agents[agent_name]
        task.status = "running"
        task.assigned_agent = agent_name

        result = agent.execute(task)
        task.output_data = result
        task.status = "completed"
        task.completed_at = datetime.now()

        agent.add_to_history(task)

        logger.info("條件執行完成")

        return result

    def route_task(self, task: Task) -> Optional[str]:
        """
        路由任務到合適的 Agent

        根據 Agent 的能力自動選擇

        Args:
            task: 任務

        Returns:
            Optional[str]: 選中的 Agent 名稱
        """
        for agent_name, agent in self.agents.items():
            if agent.can_handle(task):
                logger.info(f"路由任務到 {agent_name}")
                return agent_name

        logger.warning("沒有找到合適的 Agent")
        return None


# ============================================================================
# 協作模式
# ============================================================================

class CollaborationPattern:
    """協作模式基類"""

    @staticmethod
    def debate(
        agents: List[BaseAgent],
        topic: str,
        rounds: int = 3
    ) -> Dict[str, Any]:
        """
        辯論模式

        多個 Agent 就某個話題進行辯論

        Args:
            agents: 參與辯論的 Agent 列表
            topic: 辯論話題
            rounds: 辯論輪次

        Returns:
            Dict: 辯論結果
        """
        logger.info(f"開始辯論: {topic}")

        debate_history = []

        for round_num in range(rounds):
            logger.info(f"辯論第 {round_num + 1} 輪")

            for agent in agents:
                task = Task(
                    id=f"debate_{round_num}_{agent.name}",
                    description=f"辯論: {topic}",
                    input_data={
                        "type": "debate",
                        "topic": topic,
                        "round": round_num,
                        "previous_arguments": debate_history
                    }
                )

                # 簡化的辯論發言
                argument = f"{agent.name} 的觀點（第{round_num+1}輪）：基於專業角度的分析"

                debate_history.append({
                    "round": round_num,
                    "agent": agent.name,
                    "argument": argument
                })

        return {
            "topic": topic,
            "rounds": rounds,
            "debate_history": debate_history,
            "participants": [a.name for a in agents]
        }

    @staticmethod
    def vote(
        agents: List[BaseAgent],
        options: List[str],
        task_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        投票模式

        多個 Agent 對選項進行投票

        Args:
            agents: 參與投票的 Agent 列表
            options: 選項列表
            task_context: 任務上下文

        Returns:
            Dict: 投票結果
        """
        logger.info("開始投票")

        votes = {option: 0 for option in options}
        vote_details = []

        for agent in agents:
            # 簡化的投票邏輯（實際應基於 Agent 的判斷）
            import random
            vote = random.choice(options)
            votes[vote] += 1

            vote_details.append({
                "agent": agent.name,
                "vote": vote
            })

            logger.info(f"{agent.name} 投票: {vote}")

        # 確定獲勝選項
        winner = max(votes.items(), key=lambda x: x[1])

        return {
            "options": options,
            "votes": votes,
            "vote_details": vote_details,
            "winner": winner[0],
            "winner_count": winner[1]
        }


# ============================================================================
# 示例和測試
# ============================================================================

def demonstrate_sequential_workflow():
    """演示順序工作流"""
    print("\n" + "="*60)
    print("示例 1: 順序工作流 - 內容創作流程")
    print("="*60 + "\n")

    # 創建編排器
    orchestrator = AgentOrchestrator()

    # 註冊 Agent
    orchestrator.register_agent(ResearchAgent("研究員"))
    orchestrator.register_agent(WriterAgent("作家"))
    orchestrator.register_agent(ReviewerAgent("審核員"))

    # 創建任務
    tasks = [
        Task(
            id="task_1",
            description="研究 AI Agent 技術",
            input_data={"type": "research", "query": "AI Agent"}
        ),
        Task(
            id="task_2",
            description="撰寫技術文章",
            input_data={"type": "writing", "topic": "AI Agent 技術"}
        ),
        Task(
            id="task_3",
            description="審核文章質量",
            input_data={"type": "review"}
        )
    ]

    # 執行順序工作流
    results = orchestrator.execute_sequential(
        tasks=tasks,
        agent_names=["研究員", "作家", "審核員"]
    )

    print("\n工作流執行結果:")
    for i, result in enumerate(results, 1):
        print(f"\n步驟 {i} 結果:")
        print(json.dumps(result, indent=2, ensure_ascii=False)[:200] + "...")


async def demonstrate_parallel_workflow():
    """演示並行工作流"""
    print("\n" + "="*60)
    print("示例 2: 並行工作流 - 多主題研究")
    print("="*60 + "\n")

    orchestrator = AgentOrchestrator()

    # 註冊多個研究 Agent
    orchestrator.register_agent(ResearchAgent("研究員A"))
    orchestrator.register_agent(ResearchAgent("研究員B"))
    orchestrator.register_agent(ResearchAgent("研究員C"))

    # 創建並行任務
    tasks = [
        Task(
            id="task_a",
            description="研究 Strands Agents",
            input_data={"type": "research", "query": "Strands Agents"}
        ),
        Task(
            id="task_b",
            description="研究 Amazon Bedrock",
            input_data={"type": "research", "query": "Amazon Bedrock"}
        ),
        Task(
            id="task_c",
            description="研究 AWS Lambda",
            input_data={"type": "research", "query": "AWS Lambda"}
        )
    ]

    # 並行執行
    results = await orchestrator.execute_parallel(
        tasks=tasks,
        agent_names=["研究員A", "研究員B", "研究員C"]
    )

    print("\n並行執行結果:")
    for i, result in enumerate(results, 1):
        print(f"\n任務 {i}:")
        print(f"  查詢: {result.get('query')}")
        print(f"  發現數量: {len(result.get('findings', []))}")


def demonstrate_conditional_workflow():
    """演示條件工作流"""
    print("\n" + "="*60)
    print("示例 3: 條件工作流 - 智能路由")
    print("="*60 + "\n")

    orchestrator = AgentOrchestrator()

    # 註冊不同類型的 Agent
    orchestrator.register_agent(ResearchAgent())
    orchestrator.register_agent(WriterAgent())
    orchestrator.register_agent(ReviewerAgent())

    # 條件判斷函數
    def task_router(task: Task) -> str:
        task_type = task.input_data.get("type", "")
        if "research" in task_type:
            return "research"
        elif "writing" in task_type:
            return "writing"
        else:
            return "review"

    # 測試不同類型的任務
    test_tasks = [
        Task("1", "研究任務", {"type": "research", "query": "測試"}),
        Task("2", "寫作任務", {"type": "writing", "topic": "測試"}),
        Task("3", "審核任務", {"type": "review", "content": "測試"})
    ]

    agent_mapping = {
        "research": "研究員",
        "writing": "作家",
        "review": "審核員"
    }

    for task in test_tasks:
        print(f"\n處理任務: {task.description}")
        result = orchestrator.execute_conditional(
            task=task,
            condition_func=task_router,
            agent_mapping=agent_mapping
        )
        print(f"  執行 Agent: {task.assigned_agent}")
        print(f"  狀態: {task.status}")


def demonstrate_collaboration_patterns():
    """演示協作模式"""
    print("\n" + "="*60)
    print("示例 4: 協作模式 - 辯論和投票")
    print("="*60 + "\n")

    # 創建 Agent
    agents = [
        ResearchAgent("研究員"),
        WriterAgent("作家"),
        ReviewerAgent("審核員")
    ]

    # 辯論模式
    print("辯論模式:")
    debate_result = CollaborationPattern.debate(
        agents=agents,
        topic="AI 的未來發展方向",
        rounds=2
    )
    print(f"  參與者: {', '.join(debate_result['participants'])}")
    print(f"  辯論輪次: {debate_result['rounds']}")

    # 投票模式
    print("\n投票模式:")
    vote_result = CollaborationPattern.vote(
        agents=agents,
        options=["選項A: 重點發展技術", "選項B: 重點應用落地", "選項C: 兼顧兩者"],
        task_context={}
    )
    print(f"  獲勝選項: {vote_result['winner']}")
    print(f"  得票數: {vote_result['winner_count']}")


def main():
    """主函數"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "多 Agent 協作示例" + " "*20 + "║")
    print("╚" + "="*58 + "╝")

    try:
        demonstrate_sequential_workflow()
        asyncio.run(demonstrate_parallel_workflow())
        demonstrate_conditional_workflow()
        demonstrate_collaboration_patterns()

        print("\n" + "="*60)
        print("所有示例執行完成！")
        print("="*60)

    except Exception as e:
        logger.error(f"執行錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

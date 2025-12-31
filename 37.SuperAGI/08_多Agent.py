"""
SuperAGI 多 Agent 協作示例

這個示例展示了如何:
1. 創建 Agent 團隊
2. Agent 間通信
3. 任務協調和分配
4. 協作模式設計
5. 團隊性能優化

多 Agent 協作是解決複雜問題的關鍵。
"""

import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import time


# ==================== Agent 角色 ====================

class AgentRole(Enum):
    """Agent 角色"""
    COORDINATOR = "coordinator"  # 協調者
    RESEARCHER = "researcher"    # 研究員
    ANALYST = "analyst"          # 分析師
    WRITER = "writer"            # 寫作者
    REVIEWER = "reviewer"        # 審核者
    DEVELOPER = "developer"      # 開發者
    TESTER = "tester"           # 測試者


# ==================== 消息類型 ====================

class MessageType(Enum):
    """消息類型"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    QUERY = "query"
    RESULT = "result"


# ==================== 消息 ====================

@dataclass
class Message:
    """Agent 間消息"""
    from_agent: str
    to_agent: str
    message_type: MessageType
    content: Dict
    timestamp: datetime = field(default_factory=datetime.now)
    message_id: str = field(default="")

    def __post_init__(self):
        if not self.message_id:
            self.message_id = f"msg_{int(time.time()*1000)}"


# ==================== Agent 基類 ====================

class TeamAgent:
    """團隊 Agent 基類"""

    def __init__(
        self,
        agent_id: str,
        name: str,
        role: AgentRole,
        capabilities: List[str] = None
    ):
        """
        初始化 Agent

        參數:
            agent_id: Agent ID
            name: Agent 名稱
            role: Agent 角色
            capabilities: 能力列表
        """
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.capabilities = capabilities or []
        self.inbox: List[Message] = []
        self.outbox: List[Message] = []
        self.task_queue: List[Dict] = []
        self.status = "idle"

    def receive_message(self, message: Message):
        """接收消息"""
        self.inbox.append(message)
        print(f"📬 {self.name} 收到消息: {message.message_type.value} from {message.from_agent}")

    def send_message(
        self,
        to_agent: str,
        message_type: MessageType,
        content: Dict
    ) -> Message:
        """發送消息"""
        message = Message(
            from_agent=self.agent_id,
            to_agent=to_agent,
            message_type=message_type,
            content=content
        )

        self.outbox.append(message)
        print(f"📤 {self.name} 發送消息: {message_type.value} to {to_agent}")

        return message

    def process_messages(self):
        """處理收件箱中的消息"""
        while self.inbox:
            message = self.inbox.pop(0)
            self.handle_message(message)

    def handle_message(self, message: Message):
        """處理單個消息"""
        print(f"⚙️  {self.name} 處理消息: {message.message_type.value}")

        if message.message_type == MessageType.REQUEST:
            self.handle_request(message)
        elif message.message_type == MessageType.QUERY:
            self.handle_query(message)
        elif message.message_type == MessageType.NOTIFICATION:
            self.handle_notification(message)

    def handle_request(self, message: Message):
        """處理請求"""
        pass

    def handle_query(self, message: Message):
        """處理查詢"""
        pass

    def handle_notification(self, message: Message):
        """處理通知"""
        pass

    def execute_task(self, task: Dict) -> Dict:
        """執行任務"""
        print(f"🔧 {self.name} 執行任務: {task.get('description')}")
        self.status = "working"

        # 模擬任務執行
        time.sleep(0.1)

        result = {
            "success": True,
            "agent_id": self.agent_id,
            "task_id": task.get("id"),
            "result": f"{self.name} 完成任務",
            "timestamp": datetime.now().isoformat()
        }

        self.status = "idle"

        return result


# ==================== 具體 Agent 實現 ====================

class CoordinatorAgent(TeamAgent):
    """協調者 Agent"""

    def __init__(self, agent_id: str, name: str):
        super().__init__(
            agent_id=agent_id,
            name=name,
            role=AgentRole.COORDINATOR,
            capabilities=["task_assignment", "progress_tracking", "team_management"]
        )
        self.team_members: List[TeamAgent] = []
        self.task_assignments: Dict[str, str] = {}  # task_id -> agent_id

    def add_team_member(self, agent: TeamAgent):
        """添加團隊成員"""
        self.team_members.append(agent)
        print(f"✅ {agent.name} 加入團隊")

    def assign_task(self, task: Dict, agent_id: str):
        """分配任務"""
        self.task_assignments[task["id"]] = agent_id

        # 發送任務請求
        message = self.send_message(
            to_agent=agent_id,
            message_type=MessageType.REQUEST,
            content={"task": task}
        )

        return message

    def get_team_status(self) -> Dict:
        """獲取團隊狀態"""
        return {
            "team_size": len(self.team_members),
            "active_tasks": len(self.task_assignments),
            "members": [
                {
                    "id": agent.agent_id,
                    "name": agent.name,
                    "role": agent.role.value,
                    "status": agent.status
                }
                for agent in self.team_members
            ]
        }


class ResearcherAgent(TeamAgent):
    """研究員 Agent"""

    def __init__(self, agent_id: str, name: str):
        super().__init__(
            agent_id=agent_id,
            name=name,
            role=AgentRole.RESEARCHER,
            capabilities=["web_search", "information_gathering", "summarization"]
        )

    def handle_request(self, message: Message):
        """處理研究請求"""
        task = message.content.get("task")
        if task:
            result = self.execute_task(task)

            # 發送結果
            self.send_message(
                to_agent=message.from_agent,
                message_type=MessageType.RESULT,
                content={"result": result}
            )


class AnalystAgent(TeamAgent):
    """分析師 Agent"""

    def __init__(self, agent_id: str, name: str):
        super().__init__(
            agent_id=agent_id,
            name=name,
            role=AgentRole.ANALYST,
            capabilities=["data_analysis", "pattern_recognition", "reporting"]
        )

    def handle_request(self, message: Message):
        """處理分析請求"""
        task = message.content.get("task")
        if task:
            result = self.execute_task(task)

            self.send_message(
                to_agent=message.from_agent,
                message_type=MessageType.RESULT,
                content={"result": result}
            )


class WriterAgent(TeamAgent):
    """寫作者 Agent"""

    def __init__(self, agent_id: str, name: str):
        super().__init__(
            agent_id=agent_id,
            name=name,
            role=AgentRole.WRITER,
            capabilities=["content_generation", "document_creation", "editing"]
        )

    def handle_request(self, message: Message):
        """處理寫作請求"""
        task = message.content.get("task")
        if task:
            result = self.execute_task(task)

            self.send_message(
                to_agent=message.from_agent,
                message_type=MessageType.RESULT,
                content={"result": result}
            )


# ==================== 消息路由器 ====================

class MessageRouter:
    """
    消息路由器

    管理 Agent 間的消息傳遞
    """

    def __init__(self):
        """初始化路由器"""
        self.agents: Dict[str, TeamAgent] = {}
        self.message_log: List[Message] = []

    def register_agent(self, agent: TeamAgent):
        """註冊 Agent"""
        self.agents[agent.agent_id] = agent
        print(f"🔌 註冊 Agent: {agent.name} ({agent.agent_id})")

    def route_message(self, message: Message):
        """路由消息"""
        if message.to_agent in self.agents:
            self.agents[message.to_agent].receive_message(message)
            self.message_log.append(message)
        else:
            print(f"❌ 未找到目標 Agent: {message.to_agent}")

    def broadcast_message(self, from_agent: str, message_type: MessageType, content: Dict):
        """廣播消息"""
        print(f"\n📢 廣播消息: {message_type.value}")

        for agent_id, agent in self.agents.items():
            if agent_id != from_agent:
                message = Message(
                    from_agent=from_agent,
                    to_agent=agent_id,
                    message_type=message_type,
                    content=content
                )
                self.route_message(message)

    def get_message_stats(self) -> Dict:
        """獲取消息統計"""
        return {
            "total_messages": len(self.message_log),
            "by_type": {
                msg_type.value: sum(1 for m in self.message_log if m.message_type == msg_type)
                for msg_type in MessageType
            }
        }


# ==================== 團隊協調器 ====================

class TeamCoordinator:
    """
    團隊協調器

    管理整個 Agent 團隊
    """

    def __init__(self, team_name: str):
        """
        初始化團隊協調器

        參數:
            team_name: 團隊名稱
        """
        self.team_name = team_name
        self.agents: List[TeamAgent] = []
        self.router = MessageRouter()
        self.tasks: List[Dict] = []
        self.results: List[Dict] = []

    def add_agent(self, agent: TeamAgent):
        """添加 Agent"""
        self.agents.append(agent)
        self.router.register_agent(agent)

    def assign_tasks(self, tasks: List[Dict]):
        """分配任務給團隊"""
        print(f"\n📋 分配 {len(tasks)} 個任務...")

        for task in tasks:
            # 根據任務類型選擇 Agent
            agent = self._select_agent_for_task(task)

            if agent:
                message = Message(
                    from_agent="coordinator",
                    to_agent=agent.agent_id,
                    message_type=MessageType.REQUEST,
                    content={"task": task}
                )

                self.router.route_message(message)
                self.tasks.append(task)

    def _select_agent_for_task(self, task: Dict) -> Optional[TeamAgent]:
        """為任務選擇合適的 Agent"""
        task_type = task.get("type")

        role_mapping = {
            "research": AgentRole.RESEARCHER,
            "analysis": AgentRole.ANALYST,
            "writing": AgentRole.WRITER
        }

        target_role = role_mapping.get(task_type)

        if target_role:
            for agent in self.agents:
                if agent.role == target_role and agent.status == "idle":
                    return agent

        return None

    def process_all_messages(self):
        """處理所有 Agent 的消息"""
        print(f"\n⚙️  處理團隊消息...")

        for agent in self.agents:
            agent.process_messages()

    def collect_results(self):
        """收集所有結果"""
        print(f"\n📊 收集執行結果...")

        for agent in self.agents:
            for message in agent.outbox:
                if message.message_type == MessageType.RESULT:
                    self.results.append(message.content.get("result"))

    def get_team_report(self) -> str:
        """生成團隊報告"""
        report = f"\n{'=' * 60}\n"
        report += f"團隊報告: {self.team_name}\n"
        report += f"{'=' * 60}\n\n"

        report += f"團隊成員: {len(self.agents)}\n"
        for agent in self.agents:
            report += f"  - {agent.name} ({agent.role.value}): {agent.status}\n"

        report += f"\n已分配任務: {len(self.tasks)}\n"
        report += f"完成結果: {len(self.results)}\n"

        msg_stats = self.router.get_message_stats()
        report += f"\n消息統計:\n"
        report += f"  總消息數: {msg_stats['total_messages']}\n"
        for msg_type, count in msg_stats['by_type'].items():
            if count > 0:
                report += f"  {msg_type}: {count}\n"

        return report


# ==================== 協作模式 ====================

class CollaborationPattern:
    """協作模式"""

    @staticmethod
    def sequential_workflow(team: TeamCoordinator, tasks: List[Dict]):
        """
        順序工作流

        任務按順序執行，每個任務的輸出是下一個任務的輸入
        """
        print("\n🔄 順序工作流模式")

        previous_result = None

        for i, task in enumerate(tasks):
            if previous_result:
                task["input"] = previous_result

            print(f"\n步驟 {i+1}: {task['description']}")

            team.assign_tasks([task])
            team.process_all_messages()
            team.collect_results()

            if team.results:
                previous_result = team.results[-1]

    @staticmethod
    def parallel_workflow(team: TeamCoordinator, tasks: List[Dict]):
        """
        並行工作流

        所有任務同時執行
        """
        print("\n⚡ 並行工作流模式")

        team.assign_tasks(tasks)
        team.process_all_messages()
        team.collect_results()

    @staticmethod
    def pipeline_workflow(team: TeamCoordinator, tasks: List[Dict]):
        """
        流水線工作流

        任務在不同 Agent 間傳遞處理
        """
        print("\n🏭 流水線工作流模式")

        # 第一階段: 研究
        research_tasks = [t for t in tasks if t["type"] == "research"]
        team.assign_tasks(research_tasks)
        team.process_all_messages()

        # 第二階段: 分析
        analysis_tasks = [t for t in tasks if t["type"] == "analysis"]
        team.assign_tasks(analysis_tasks)
        team.process_all_messages()

        # 第三階段: 寫作
        writing_tasks = [t for t in tasks if t["type"] == "writing"]
        team.assign_tasks(writing_tasks)
        team.process_all_messages()

        team.collect_results()


# ==================== 示例場景 ====================

def example_1_basic_team():
    """示例 1: 基本團隊協作"""
    print("\n" + "=" * 60)
    print("示例 1: 基本團隊協作")
    print("=" * 60)

    # 創建團隊
    team = TeamCoordinator("ResearchTeam")

    # 添加 Agents
    team.add_agent(ResearcherAgent("r1", "研究員 Alice"))
    team.add_agent(AnalystAgent("a1", "分析師 Bob"))
    team.add_agent(WriterAgent("w1", "寫作者 Carol"))

    # 分配任務
    tasks = [
        {
            "id": "task_1",
            "type": "research",
            "description": "搜索 AI Agent 相關資料"
        },
        {
            "id": "task_2",
            "type": "analysis",
            "description": "分析研究數據"
        },
        {
            "id": "task_3",
            "type": "writing",
            "description": "撰寫研究報告"
        }
    ]

    team.assign_tasks(tasks)

    # 處理消息
    team.process_all_messages()

    # 收集結果
    team.collect_results()

    # 生成報告
    print(team.get_team_report())


def example_2_coordinator_pattern():
    """示例 2: 協調者模式"""
    print("\n" + "=" * 60)
    print("示例 2: 協調者模式")
    print("=" * 60)

    # 創建協調者
    coordinator = CoordinatorAgent("coord_1", "協調者")

    # 創建團隊成員
    researcher = ResearcherAgent("r1", "研究員")
    analyst = AnalystAgent("a1", "分析師")
    writer = WriterAgent("w1", "寫作者")

    # 添加團隊成員
    coordinator.add_team_member(researcher)
    coordinator.add_team_member(analyst)
    coordinator.add_team_member(writer)

    # 創建消息路由器
    router = MessageRouter()
    router.register_agent(coordinator)
    router.register_agent(researcher)
    router.register_agent(analyst)
    router.register_agent(writer)

    # 協調者分配任務
    task = {
        "id": "task_1",
        "type": "research",
        "description": "研究市場趨勢"
    }

    message = coordinator.assign_task(task, researcher.agent_id)
    router.route_message(message)

    # 處理消息
    researcher.process_messages()

    # 查看團隊狀態
    status = coordinator.get_team_status()
    print(f"\n團隊狀態:")
    print(json.dumps(status, indent=2, ensure_ascii=False))


def example_3_workflow_patterns():
    """示例 3: 工作流模式"""
    print("\n" + "=" * 60)
    print("示例 3: 不同工作流模式")
    print("=" * 60)

    # 創建團隊
    team = TeamCoordinator("WorkflowTeam")

    team.add_agent(ResearcherAgent("r1", "研究員 A"))
    team.add_agent(ResearcherAgent("r2", "研究員 B"))
    team.add_agent(AnalystAgent("a1", "分析師 A"))
    team.add_agent(WriterAgent("w1", "寫作者 A"))

    # 準備任務
    tasks = [
        {"id": "1", "type": "research", "description": "研究階段 1"},
        {"id": "2", "type": "research", "description": "研究階段 2"},
        {"id": "3", "type": "analysis", "description": "分析階段"},
        {"id": "4", "type": "writing", "description": "寫作階段"}
    ]

    # 測試並行工作流
    CollaborationPattern.parallel_workflow(team, tasks[:2])

    # 重置
    team.results = []

    # 測試流水線工作流
    CollaborationPattern.pipeline_workflow(team, tasks)

    print(team.get_team_report())


def example_4_message_broadcast():
    """示例 4: 消息廣播"""
    print("\n" + "=" * 60)
    print("示例 4: 消息廣播")
    print("=" * 60)

    router = MessageRouter()

    # 註冊多個 Agents
    agents = [
        ResearcherAgent("r1", "研究員 1"),
        ResearcherAgent("r2", "研究員 2"),
        AnalystAgent("a1", "分析師 1")
    ]

    for agent in agents:
        router.register_agent(agent)

    # 廣播消息
    router.broadcast_message(
        from_agent="system",
        message_type=MessageType.NOTIFICATION,
        content={
            "message": "系統維護通知",
            "timestamp": datetime.now().isoformat()
        }
    )

    # 處理消息
    for agent in agents:
        agent.process_messages()

    # 消息統計
    stats = router.get_message_stats()
    print(f"\n消息統計:")
    print(json.dumps(stats, indent=2, ensure_ascii=False))


# ==================== 主函數 ====================

def main():
    """主函數"""
    print("\n" + "👥 " * 20)
    print("SuperAGI 多 Agent 協作教程")
    print("👥 " * 20)

    try:
        # 示例 1: 基本團隊
        example_1_basic_team()

        # 示例 2: 協調者模式
        example_2_coordinator_pattern()

        # 示例 3: 工作流模式
        example_3_workflow_patterns()

        # 示例 4: 消息廣播
        example_4_message_broadcast()

        print("\n" + "=" * 60)
        print("✅ 所有多 Agent 協作示例執行完成！")
        print("=" * 60)

        print("""
        多 Agent 協作最佳實踐:

        1. 明確定義 Agent 角色和職責
        2. 設計清晰的消息協議
        3. 實現可靠的消息路由
        4. 選擇合適的協作模式
        5. 監控團隊性能
        6. 處理 Agent 間的衝突
        7. 實現容錯機制
        8. 優化任務分配策略
        """)

    except Exception as e:
        print(f"\n❌ 執行出錯: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

"""
Letta 多 Agent 系統

本模組展示如何構建和管理多 Agent 系統：
1. Agent 間通信機制
2. 協作和任務分配
3. Agent 編排和協調
4. 共享知識庫
5. 衝突解決機制
6. 分布式 Agent 系統

讓多個 Agent 協同工作，完成複雜任務。

作者：Letta 框架示例
日期：2025-01
"""

import os
import json
import time
import threading
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from queue import Queue, PriorityQueue
import uuid


class AgentRole(Enum):
    """Agent 角色"""
    COORDINATOR = "coordinator"  # 協調者
    WORKER = "worker"  # 工作者
    SPECIALIST = "specialist"  # 專家
    REVIEWER = "reviewer"  # 審查者
    FACILITATOR = "facilitator"  # 促進者


class MessageType(Enum):
    """消息類型"""
    REQUEST = "request"  # 請求
    RESPONSE = "response"  # 響應
    BROADCAST = "broadcast"  # 廣播
    NOTIFICATION = "notification"  # 通知
    TASK_ASSIGNMENT = "task_assignment"  # 任務分配


@dataclass
class Message:
    """Agent 間的消息"""
    message_id: str
    sender_id: str
    receiver_id: str
    message_type: MessageType
    content: Any
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    priority: int = 5
    requires_response: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Task:
    """任務定義"""
    task_id: str
    description: str
    assigned_to: Optional[str] = None
    status: str = "pending"  # pending, in_progress, completed, failed
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    result: Optional[Any] = None
    priority: int = 5
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class MessageBus:
    """
    消息總線

    管理 Agent 間的消息傳遞。
    """

    def __init__(self):
        """初始化消息總線"""
        self.message_queues: Dict[str, Queue] = {}
        self.message_history: List[Message] = []
        self.subscriptions: Dict[str, List[str]] = {}  # topic -> agent_ids

        print("消息總線初始化完成")

    def register_agent(self, agent_id: str) -> None:
        """
        註冊 Agent

        參數:
            agent_id: Agent ID
        """
        if agent_id not in self.message_queues:
            self.message_queues[agent_id] = Queue()
            print(f"[消息總線] Agent {agent_id} 已註冊")

    def send_message(self, message: Message) -> None:
        """
        發送消息

        參數:
            message: 消息對象
        """
        if message.receiver_id == "broadcast":
            # 廣播消息給所有 Agent
            for agent_id in self.message_queues.keys():
                if agent_id != message.sender_id:
                    self.message_queues[agent_id].put(message)
            print(f"[廣播] {message.sender_id}: {message.content}")
        else:
            # 點對點消息
            if message.receiver_id in self.message_queues:
                self.message_queues[message.receiver_id].put(message)
                print(f"[消息] {message.sender_id} -> {message.receiver_id}: {message.content}")
            else:
                print(f"[錯誤] 接收者 {message.receiver_id} 不存在")

        # 記錄到歷史
        self.message_history.append(message)

    def receive_message(self, agent_id: str, timeout: Optional[float] = None) -> Optional[Message]:
        """
        接收消息

        參數:
            agent_id: Agent ID
            timeout: 超時時間（秒）

        返回:
            消息對象，如果沒有消息則返回 None
        """
        if agent_id not in self.message_queues:
            return None

        try:
            if timeout:
                message = self.message_queues[agent_id].get(timeout=timeout)
            else:
                message = self.message_queues[agent_id].get_nowait()
            return message
        except:
            return None

    def subscribe(self, agent_id: str, topic: str) -> None:
        """
        訂閱主題

        參數:
            agent_id: Agent ID
            topic: 主題名稱
        """
        if topic not in self.subscriptions:
            self.subscriptions[topic] = []

        if agent_id not in self.subscriptions[topic]:
            self.subscriptions[topic].append(agent_id)
            print(f"[訂閱] {agent_id} 訂閱了主題: {topic}")

    def publish(self, topic: str, message: Message) -> None:
        """
        發布到主題

        參數:
            topic: 主題名稱
            message: 消息對象
        """
        if topic in self.subscriptions:
            for agent_id in self.subscriptions[topic]:
                if agent_id in self.message_queues:
                    self.message_queues[agent_id].put(message)
            print(f"[發布] 主題 {topic}: {len(self.subscriptions[topic])} 個訂閱者")


class LettaAgent:
    """
    Letta Agent 基類

    支持多 Agent 協作的 Agent 實現。
    """

    def __init__(self, agent_id: str, role: AgentRole, message_bus: MessageBus):
        """
        初始化 Agent

        參數:
            agent_id: Agent ID
            role: Agent 角色
            message_bus: 消息總線
        """
        self.agent_id = agent_id
        self.role = role
        self.message_bus = message_bus
        self.is_running = False
        self.tasks: Dict[str, Task] = {}
        self.knowledge: Dict[str, Any] = {}

        # 註冊到消息總線
        self.message_bus.register_agent(agent_id)

        print(f"\n[Agent 創建] {agent_id} (角色: {role.value})")

    def start(self) -> None:
        """啟動 Agent"""
        self.is_running = True
        print(f"[{self.agent_id}] 已啟動")

    def stop(self) -> None:
        """停止 Agent"""
        self.is_running = False
        print(f"[{self.agent_id}] 已停止")

    def send_message(self, receiver_id: str, content: Any,
                    message_type: MessageType = MessageType.REQUEST) -> str:
        """
        發送消息給其他 Agent

        參數:
            receiver_id: 接收者 ID
            content: 消息內容
            message_type: 消息類型

        返回:
            消息 ID
        """
        message = Message(
            message_id=str(uuid.uuid4())[:8],
            sender_id=self.agent_id,
            receiver_id=receiver_id,
            message_type=message_type,
            content=content
        )

        self.message_bus.send_message(message)
        return message.message_id

    def broadcast(self, content: Any) -> None:
        """
        廣播消息給所有 Agent

        參數:
            content: 消息內容
        """
        self.send_message("broadcast", content, MessageType.BROADCAST)

    def process_messages(self) -> None:
        """處理收到的消息"""
        while self.is_running:
            message = self.message_bus.receive_message(self.agent_id, timeout=0.1)
            if message:
                self.handle_message(message)

    def handle_message(self, message: Message) -> None:
        """
        處理單個消息

        參數:
            message: 消息對象
        """
        print(f"[{self.agent_id}] 收到消息: {message.content}")

        if message.message_type == MessageType.REQUEST:
            self.handle_request(message)
        elif message.message_type == MessageType.TASK_ASSIGNMENT:
            self.handle_task_assignment(message)
        elif message.message_type == MessageType.BROADCAST:
            self.handle_broadcast(message)

    def handle_request(self, message: Message) -> None:
        """處理請求消息"""
        # 子類可以覆蓋此方法
        response = f"收到請求: {message.content}"
        self.send_message(message.sender_id, response, MessageType.RESPONSE)

    def handle_task_assignment(self, message: Message) -> None:
        """處理任務分配"""
        task = message.content
        if isinstance(task, Task):
            self.tasks[task.task_id] = task
            task.assigned_to = self.agent_id
            task.status = "in_progress"
            print(f"[{self.agent_id}] 接受任務: {task.description}")

    def handle_broadcast(self, message: Message) -> None:
        """處理廣播消息"""
        # 子類可以覆蓋此方法
        pass

    def execute_task(self, task: Task) -> Any:
        """
        執行任務

        參數:
            task: 任務對象

        返回:
            任務結果
        """
        print(f"[{self.agent_id}] 執行任務: {task.description}")

        # 模擬任務執行
        time.sleep(0.5)
        result = f"任務 {task.task_id} 已完成"

        task.status = "completed"
        task.completed_at = datetime.now().isoformat()
        task.result = result

        return result


class CoordinatorAgent(LettaAgent):
    """
    協調者 Agent

    負責任務分配和協調其他 Agent。
    """

    def __init__(self, agent_id: str, message_bus: MessageBus):
        super().__init__(agent_id, AgentRole.COORDINATOR, message_bus)
        self.worker_agents: List[str] = []
        self.task_queue = PriorityQueue()

    def register_worker(self, worker_id: str) -> None:
        """
        註冊工作者 Agent

        參數:
            worker_id: 工作者 ID
        """
        self.worker_agents.append(worker_id)
        print(f"[{self.agent_id}] 註冊工作者: {worker_id}")

    def assign_task(self, task: Task) -> None:
        """
        分配任務

        參數:
            task: 任務對象
        """
        if not self.worker_agents:
            print(f"[{self.agent_id}] 沒有可用的工作者")
            return

        # 簡單的輪詢分配策略
        worker_id = self.worker_agents[len(self.tasks) % len(self.worker_agents)]

        message = Message(
            message_id=str(uuid.uuid4())[:8],
            sender_id=self.agent_id,
            receiver_id=worker_id,
            message_type=MessageType.TASK_ASSIGNMENT,
            content=task
        )

        self.message_bus.send_message(message)
        self.tasks[task.task_id] = task

        print(f"[{self.agent_id}] 分配任務 {task.task_id} 給 {worker_id}")

    def create_and_assign_task(self, description: str, priority: int = 5) -> str:
        """
        創建並分配任務

        參數:
            description: 任務描述
            priority: 優先級

        返回:
            任務 ID
        """
        task = Task(
            task_id=str(uuid.uuid4())[:8],
            description=description,
            priority=priority
        )

        self.assign_task(task)
        return task.task_id


class SpecialistAgent(LettaAgent):
    """
    專家 Agent

    在特定領域有專長的 Agent。
    """

    def __init__(self, agent_id: str, message_bus: MessageBus, specialty: str):
        super().__init__(agent_id, AgentRole.SPECIALIST, message_bus)
        self.specialty = specialty
        print(f"  專長: {specialty}")

    def handle_request(self, message: Message) -> None:
        """處理專業領域的請求"""
        request = message.content

        if isinstance(request, str) and self.specialty.lower() in request.lower():
            response = f"[專家意見] 關於 {self.specialty}: {request} - 這是專業的解答..."
            self.send_message(message.sender_id, response, MessageType.RESPONSE)
        else:
            response = f"這不是我的專長領域（{self.specialty}）"
            self.send_message(message.sender_id, response, MessageType.RESPONSE)


class AgentOrchestrator:
    """
    Agent 編排器

    管理多個 Agent 的協作和編排。
    """

    def __init__(self):
        """初始化編排器"""
        self.message_bus = MessageBus()
        self.agents: Dict[str, LettaAgent] = {}
        self.agent_threads: Dict[str, threading.Thread] = {}

        print("\nAgent 編排器初始化完成")

    def add_agent(self, agent: LettaAgent) -> None:
        """
        添加 Agent

        參數:
            agent: Agent 實例
        """
        self.agents[agent.agent_id] = agent
        print(f"[編排器] 添加 Agent: {agent.agent_id}")

    def start_agent(self, agent_id: str) -> None:
        """
        啟動 Agent

        參數:
            agent_id: Agent ID
        """
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            agent.start()

            # 在單獨的線程中運行消息處理
            thread = threading.Thread(target=agent.process_messages, daemon=True)
            thread.start()
            self.agent_threads[agent_id] = thread

    def start_all_agents(self) -> None:
        """啟動所有 Agent"""
        print("\n[編排器] 啟動所有 Agent...")
        for agent_id in self.agents.keys():
            self.start_agent(agent_id)
        time.sleep(0.5)  # 等待 Agent 啟動

    def stop_all_agents(self) -> None:
        """停止所有 Agent"""
        print("\n[編排器] 停止所有 Agent...")
        for agent in self.agents.values():
            agent.stop()

    def get_agent_status(self) -> Dict[str, Any]:
        """
        獲取所有 Agent 的狀態

        返回:
            狀態字典
        """
        status = {
            "total_agents": len(self.agents),
            "running_agents": sum(1 for a in self.agents.values() if a.is_running),
            "agents": {}
        }

        for agent_id, agent in self.agents.items():
            status["agents"][agent_id] = {
                "role": agent.role.value,
                "is_running": agent.is_running,
                "tasks": len(agent.tasks)
            }

        print(f"\n[狀態] {status['running_agents']}/{status['total_agents']} 個 Agent 運行中")

        return status


def demonstrate_basic_communication():
    """演示基本的 Agent 通信"""
    print("\n" + "=" * 60)
    print("基本通信演示")
    print("=" * 60)

    orchestrator = AgentOrchestrator()

    # 創建 Agent
    agent1 = LettaAgent("agent_1", AgentRole.WORKER, orchestrator.message_bus)
    agent2 = LettaAgent("agent_2", AgentRole.WORKER, orchestrator.message_bus)

    orchestrator.add_agent(agent1)
    orchestrator.add_agent(agent2)

    orchestrator.start_all_agents()

    # Agent 間通信
    agent1.send_message("agent_2", "你好，Agent 2！")
    time.sleep(1)

    agent2.send_message("agent_1", "你好，Agent 1！收到你的消息了。")
    time.sleep(1)

    # 廣播消息
    agent1.broadcast("這是一條廣播消息！")
    time.sleep(1)

    orchestrator.stop_all_agents()


def demonstrate_task_coordination():
    """演示任務協調"""
    print("\n" + "=" * 60)
    print("任務協調演示")
    print("=" * 60)

    orchestrator = AgentOrchestrator()

    # 創建協調者
    coordinator = CoordinatorAgent("coordinator", orchestrator.message_bus)
    orchestrator.add_agent(coordinator)

    # 創建工作者
    workers = []
    for i in range(3):
        worker = LettaAgent(f"worker_{i+1}", AgentRole.WORKER, orchestrator.message_bus)
        orchestrator.add_agent(worker)
        workers.append(worker)
        coordinator.register_worker(worker.agent_id)

    orchestrator.start_all_agents()

    # 分配任務
    tasks = [
        "處理數據集 A",
        "訓練模型 B",
        "評估結果 C",
        "生成報告 D",
        "部署模型 E"
    ]

    for task_desc in tasks:
        coordinator.create_and_assign_task(task_desc)
        time.sleep(0.5)

    time.sleep(2)  # 等待任務處理

    # 查看狀態
    orchestrator.get_agent_status()

    orchestrator.stop_all_agents()


def demonstrate_specialist_agents():
    """演示專家 Agent"""
    print("\n" + "=" * 60)
    print("專家 Agent 演示")
    print("=" * 60)

    orchestrator = AgentOrchestrator()

    # 創建不同專長的專家
    specialists = [
        SpecialistAgent("python_expert", orchestrator.message_bus, "Python"),
        SpecialistAgent("ml_expert", orchestrator.message_bus, "機器學習"),
        SpecialistAgent("db_expert", orchestrator.message_bus, "數據庫")
    ]

    for specialist in specialists:
        orchestrator.add_agent(specialist)

    # 創建一個查詢 Agent
    query_agent = LettaAgent("query_agent", AgentRole.FACILITATOR, orchestrator.message_bus)
    orchestrator.add_agent(query_agent)

    orchestrator.start_all_agents()

    # 向專家諮詢
    query_agent.send_message("python_expert", "如何優化 Python 代碼性能？")
    time.sleep(1)

    query_agent.send_message("ml_expert", "機器學習模型過擬合怎麼辦？")
    time.sleep(1)

    query_agent.send_message("db_expert", "數據庫索引如何設計？")
    time.sleep(1)

    orchestrator.stop_all_agents()


def demonstrate_publish_subscribe():
    """演示發布-訂閱模式"""
    print("\n" + "=" * 60)
    print("發布-訂閱演示")
    print("=" * 60)

    message_bus = MessageBus()

    # 創建 Agent
    agents = []
    for i in range(4):
        agent = LettaAgent(f"agent_{i+1}", AgentRole.WORKER, message_bus)
        agents.append(agent)

    # 訂閱主題
    message_bus.subscribe("agent_1", "技術討論")
    message_bus.subscribe("agent_2", "技術討論")
    message_bus.subscribe("agent_3", "項目更新")
    message_bus.subscribe("agent_4", "項目更新")
    message_bus.subscribe("agent_4", "技術討論")  # agent_4 訂閱多個主題

    # 發布消息
    message = Message(
        message_id="msg_001",
        sender_id="system",
        receiver_id="",
        message_type=MessageType.BROADCAST,
        content="新的技術文章發布了！"
    )

    message_bus.publish("技術討論", message)

    time.sleep(0.5)

    message2 = Message(
        message_id="msg_002",
        sender_id="system",
        receiver_id="",
        message_type=MessageType.NOTIFICATION,
        content="項目里程碑已達成！"
    )

    message_bus.publish("項目更新", message2)


def demonstrate_complex_workflow():
    """演示複雜工作流"""
    print("\n" + "=" * 60)
    print("複雜工作流演示")
    print("=" * 60)

    orchestrator = AgentOrchestrator()

    # 創建多層 Agent 架構
    # 主協調者
    main_coordinator = CoordinatorAgent("main_coordinator", orchestrator.message_bus)
    orchestrator.add_agent(main_coordinator)

    # 子協調者（負責不同領域）
    data_coordinator = CoordinatorAgent("data_coordinator", orchestrator.message_bus)
    ml_coordinator = CoordinatorAgent("ml_coordinator", orchestrator.message_bus)

    orchestrator.add_agent(data_coordinator)
    orchestrator.add_agent(ml_coordinator)

    main_coordinator.register_worker("data_coordinator")
    main_coordinator.register_worker("ml_coordinator")

    # 數據處理工作者
    data_workers = []
    for i in range(2):
        worker = LettaAgent(f"data_worker_{i+1}", AgentRole.WORKER, orchestrator.message_bus)
        orchestrator.add_agent(worker)
        data_workers.append(worker)
        data_coordinator.register_worker(worker.agent_id)

    # 機器學習工作者
    ml_workers = []
    for i in range(2):
        worker = SpecialistAgent(f"ml_worker_{i+1}", orchestrator.message_bus, "機器學習")
        orchestrator.add_agent(worker)
        ml_workers.append(worker)
        ml_coordinator.register_worker(worker.agent_id)

    orchestrator.start_all_agents()

    # 執行複雜工作流
    print("\n[工作流] 開始執行數據科學項目...")

    # 階段 1：數據處理
    main_coordinator.create_and_assign_task("數據收集", priority=10)
    time.sleep(1)

    main_coordinator.create_and_assign_task("數據清洗", priority=9)
    time.sleep(1)

    # 階段 2：模型訓練
    main_coordinator.create_and_assign_task("模型訓練", priority=8)
    time.sleep(1)

    # 階段 3：評估和部署
    main_coordinator.create_and_assign_task("模型評估", priority=7)
    time.sleep(1)

    time.sleep(2)  # 等待任務完成

    orchestrator.get_agent_status()
    orchestrator.stop_all_agents()


def main():
    """主函數：運行所有演示"""
    print("\n" + "=" * 70)
    print(" " * 20 + "Letta 多 Agent 系統")
    print("=" * 70)

    # 基本通信
    demonstrate_basic_communication()

    # 任務協調
    demonstrate_task_coordination()

    # 專家 Agent
    demonstrate_specialist_agents()

    # 發布-訂閱
    demonstrate_publish_subscribe()

    # 複雜工作流
    demonstrate_complex_workflow()

    print("\n" + "=" * 70)
    print("多 Agent 系統演示完成！")
    print("=" * 70)
    print("\n關鍵要點：")
    print("  1. 消息總線實現 Agent 間的解耦通信")
    print("  2. 協調者模式管理任務分配")
    print("  3. 專家 Agent 提供專業能力")
    print("  4. 發布-訂閱支持事件驅動架構")
    print("  5. 層次化架構處理複雜工作流")
    print("\n下一步：查看 07_自定義Persona.py")
    print("=" * 70)


if __name__ == "__main__":
    main()

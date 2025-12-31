"""
Google ADK - 多 Agent 協作範例

這個範例展示如何實現多 Agent 系統：
- 多 Agent 架構設計
- Agent 間通信
- 任務編排和分配
- 協作模式（順序、並行、層級）
- 衝突解決
"""

import os
from typing import Optional, List, Dict, Any
from datetime import datetime
import asyncio
from google_adk import Agent, MultiAgent
from google_adk.models import GeminiPro
from google_adk.orchestration import (
    SequentialOrchestrator,
    ParallelOrchestrator,
    HierarchicalOrchestrator
)


class MultiAgentExample:
    """多 Agent 協作範例類"""

    def __init__(self, api_key: Optional[str] = None):
        """初始化多 Agent 範例"""
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("請設置 GOOGLE_API_KEY 環境變量")

    def example_1_basic_multi_agent(self):
        """範例 1: 基礎多 Agent 系統"""
        print("\n" + "="*60)
        print("範例 1: 基礎多 Agent 系統")
        print("="*60)

        # 創建專業 Agent
        researcher = Agent(
            model=GeminiPro(),
            name="researcher",
            instructions="你是一個專業的研究員，負責收集和整理信息。"
        )

        analyst = Agent(
            model=GeminiPro(),
            name="analyst",
            instructions="你是一個數據分析師，負責分析研究結果。"
        )

        writer = Agent(
            model=GeminiPro(),
            name="writer",
            instructions="你是一個專業作家，負責撰寫報告。"
        )

        print("創建的 Agent:")
        print("  1. researcher - 研究員")
        print("  2. analyst - 分析師")
        print("  3. writer - 作家")

        # 創建多 Agent 系統
        multi_agent = MultiAgent(
            agents=[researcher, analyst, writer],
            name="research-team"
        )

        print(f"\n多 Agent 系統創建完成")
        print(f"  團隊成員: {len(multi_agent.agents)}")

        return multi_agent

    def example_2_sequential_orchestration(self):
        """範例 2: 順序編排"""
        print("\n" + "="*60)
        print("範例 2: 順序編排")
        print("="*60)

        # 創建 Agent 團隊
        agents = [
            Agent(
                model=GeminiPro(),
                name="planner",
                instructions="你負責制定計劃和策略。"
            ),
            Agent(
                model=GeminiPro(),
                name="executor",
                instructions="你負責執行計劃。"
            ),
            Agent(
                model=GeminiPro(),
                name="reviewer",
                instructions="你負責審核執行結果。"
            )
        ]

        # 使用順序編排器
        orchestrator = SequentialOrchestrator(
            mode="pipeline",  # 流水線模式
            pass_context=True  # 傳遞上下文
        )

        multi_agent = MultiAgent(
            agents=agents,
            orchestrator=orchestrator,
            name="sequential-team"
        )

        # 執行任務
        task = "創建一個客戶滿意度調查問卷"
        print(f"\n任務: {task}")
        print("\n執行流程:")
        print("  步驟 1: Planner 制定計劃")
        print("  步驟 2: Executor 執行計劃")
        print("  步驟 3: Reviewer 審核結果")

        # 模擬執行
        """
        result = multi_agent.run(task)
        print(f"\n最終結果: {result.content}")
        """

        print("\n✓ 順序編排配置完成")
        return multi_agent

    def example_3_parallel_orchestration(self):
        """範例 3: 並行編排"""
        print("\n" + "="*60)
        print("範例 3: 並行編排")
        print("="*60)

        # 創建並行工作的 Agent
        agents = [
            Agent(
                model=GeminiPro(),
                name="market-analyst",
                instructions="分析市場趨勢。"
            ),
            Agent(
                model=GeminiPro(),
                name="competitor-analyst",
                instructions="分析競爭對手。"
            ),
            Agent(
                model=GeminiPro(),
                name="customer-analyst",
                instructions="分析客戶需求。"
            )
        ]

        # 使用並行編排器
        orchestrator = ParallelOrchestrator(
            aggregation_strategy="consensus",  # 共識聚合
            timeout=30  # 30 秒超時
        )

        multi_agent = MultiAgent(
            agents=agents,
            orchestrator=orchestrator,
            name="parallel-team"
        )

        task = "分析智能手機市場現狀"
        print(f"\n任務: {task}")
        print("\n並行執行:")
        print("  - market-analyst: 市場趨勢分析")
        print("  - competitor-analyst: 競爭對手分析")
        print("  - customer-analyst: 客戶需求分析")
        print("\n聚合策略: consensus（共識）")

        print("\n✓ 並行編排配置完成")
        return multi_agent

    def example_4_hierarchical_orchestration(self):
        """範例 4: 層級編排"""
        print("\n" + "="*60)
        print("範例 4: 層級編排")
        print("="*60)

        # 創建管理者 Agent
        manager = Agent(
            model=GeminiPro(),
            name="manager",
            instructions="""
            你是團隊管理者，負責：
            1. 分解任務
            2. 分配工作
            3. 協調團隊
            4. 整合結果
            """
        )

        # 創建工作 Agent
        workers = [
            Agent(
                model=GeminiPro(),
                name="developer",
                instructions="你是開發人員，負責編寫代碼。"
            ),
            Agent(
                model=GeminiPro(),
                name="tester",
                instructions="你是測試人員，負責測試代碼。"
            ),
            Agent(
                model=GeminiPro(),
                name="documenter",
                instructions="你是文檔編寫員，負責撰寫文檔。"
            )
        ]

        # 使用層級編排器
        orchestrator = HierarchicalOrchestrator(
            manager=manager,
            workers=workers,
            delegation_strategy="load_balance"  # 負載平衡
        )

        multi_agent = MultiAgent(
            agents=[manager] + workers,
            orchestrator=orchestrator,
            name="hierarchical-team"
        )

        print("團隊結構:")
        print("  Manager (管理者)")
        print("    ├── Developer (開發)")
        print("    ├── Tester (測試)")
        print("    └── Documenter (文檔)")

        print("\n✓ 層級編排配置完成")
        return multi_agent

    def example_5_agent_communication(self):
        """範例 5: Agent 間通信"""
        print("\n" + "="*60)
        print("範例 5: Agent 間通信")
        print("="*60)

        from google_adk.communication import MessageBus, Message

        # 創建消息總線
        message_bus = MessageBus()

        # 創建能通信的 Agent
        sender = Agent(
            model=GeminiPro(),
            name="sender",
            message_bus=message_bus
        )

        receiver = Agent(
            model=GeminiPro(),
            name="receiver",
            message_bus=message_bus
        )

        # 發送消息
        message = Message(
            from_agent="sender",
            to_agent="receiver",
            content="請幫我分析這份數據",
            priority="high",
            metadata={"task_id": "task-123"}
        )

        print("消息內容:")
        print(f"  發送者: {message.from_agent}")
        print(f"  接收者: {message.to_agent}")
        print(f"  內容: {message.content}")
        print(f"  優先級: {message.priority}")

        # 模擬消息傳遞
        """
        message_bus.send(message)
        received = message_bus.receive("receiver")
        response = receiver.process_message(received)
        message_bus.send(response)
        """

        print("\n✓ Agent 通信配置完成")

    def example_6_task_distribution(self):
        """範例 6: 任務分配"""
        print("\n" + "="*60)
        print("範例 6: 任務分配")
        print("="*60)

        from google_adk.orchestration import TaskDistributor

        # 創建任務分配器
        distributor = TaskDistributor(
            strategy="round_robin",  # 輪詢分配
            load_threshold=0.8       # 負載閾值
        )

        # 創建工作 Agent
        agents = [
            Agent(model=GeminiPro(), name=f"worker-{i}")
            for i in range(5)
        ]

        # 準備任務列表
        tasks = [
            "分析客戶反饋",
            "生成月度報告",
            "處理支持票據",
            "更新產品文檔",
            "審核代碼變更",
            "優化數據庫查詢",
            "設計新功能",
            "修復 Bug"
        ]

        print(f"任務總數: {len(tasks)}")
        print(f"可用 Agent: {len(agents)}")
        print(f"分配策略: {distributor.strategy}")

        # 分配任務
        assignments = distributor.distribute(tasks, agents)

        print("\n任務分配結果:")
        for agent_name, assigned_tasks in assignments.items():
            print(f"  {agent_name}: {len(assigned_tasks)} 個任務")
            for task in assigned_tasks:
                print(f"    - {task}")

    def example_7_conflict_resolution(self):
        """範例 7: 衝突解決"""
        print("\n" + "="*60)
        print("範例 7: 衝突解決")
        print("="*60)

        from google_adk.conflict import ConflictResolver

        # 創建衝突解決器
        resolver = ConflictResolver(
            strategy="voting",  # 投票策略
            require_consensus=False,
            fallback="arbitrator"  # 仲裁者
        )

        # 創建有不同觀點的 Agent
        optimist = Agent(
            model=GeminiPro(temperature=0.9),
            name="optimist",
            instructions="你總是看到積極的一面。"
        )

        pessimist = Agent(
            model=GeminiPro(temperature=0.9),
            name="pessimist",
            instructions="你總是謹慎評估風險。"
        )

        realist = Agent(
            model=GeminiPro(temperature=0.5),
            name="realist",
            instructions="你客觀分析利弊。"
        )

        # 模擬衝突場景
        task = "評估新產品發布的時機"

        print(f"任務: {task}")
        print("\n不同觀點:")
        print("  - Optimist: 立即發布，機會難得")
        print("  - Pessimist: 延遲發布，需要更多測試")
        print("  - Realist: 評估風險後決定")

        # 解決衝突
        """
        responses = {
            "optimist": optimist.run(task),
            "pessimist": pessimist.run(task),
            "realist": realist.run(task)
        }

        resolution = resolver.resolve(responses)
        print(f"\n最終決策: {resolution}")
        """

        print("\n✓ 衝突解決機制配置完成")

    def example_8_agent_specialization(self):
        """範例 8: Agent 專業化"""
        print("\n" + "="*60)
        print("範例 8: Agent 專業化")
        print("="*60)

        # 創建專業領域的 Agent
        specialists = {
            "frontend": Agent(
                model=GeminiPro(),
                name="frontend-expert",
                instructions="""
                你是前端開發專家，精通：
                - React, Vue, Angular
                - HTML, CSS, JavaScript
                - UI/UX 設計
                """
            ),
            "backend": Agent(
                model=GeminiPro(),
                name="backend-expert",
                instructions="""
                你是後端開發專家，精通：
                - Python, Java, Node.js
                - 數據庫設計
                - API 開發
                """
            ),
            "devops": Agent(
                model=GeminiPro(),
                name="devops-expert",
                instructions="""
                你是 DevOps 專家，精通：
                - Docker, Kubernetes
                - CI/CD 流程
                - 雲平台部署
                """
            ),
            "security": Agent(
                model=GeminiPro(),
                name="security-expert",
                instructions="""
                你是安全專家，精通：
                - 安全審計
                - 漏洞分析
                - 加密技術
                """
            )
        }

        print("專業 Agent 團隊:")
        for role, agent in specialists.items():
            print(f"  - {role}: {agent.name}")

        # 根據任務類型路由到專業 Agent
        from google_adk.routing import SpecialistRouter

        router = SpecialistRouter(specialists)

        tasks = [
            ("設計登錄頁面", "frontend"),
            ("優化數據庫查詢", "backend"),
            ("配置 CI/CD", "devops"),
            ("修復安全漏洞", "security")
        ]

        print("\n任務路由:")
        for task, expected_specialist in tasks:
            specialist = router.route(task)
            print(f"  '{task}' -> {specialist}")

    def example_9_collaborative_learning(self):
        """範例 9: 協作學習"""
        print("\n" + "="*60)
        print("範例 9: 協作學習")
        print("="*60)

        from google_adk.learning import CollaborativeLearning

        # 創建學習環境
        learning_env = CollaborativeLearning(
            strategy="federated",  # 聯邦學習
            sharing_policy="gradients"  # 共享梯度
        )

        # 創建學習 Agent
        learners = [
            Agent(
                model=GeminiPro(),
                name=f"learner-{i}",
                learning_enabled=True
            )
            for i in range(3)
        ]

        print("協作學習配置:")
        print(f"  學習者數量: {len(learners)}")
        print(f"  學習策略: {learning_env.strategy}")
        print(f"  共享策略: {learning_env.sharing_policy}")

        # 學習循環
        print("\n學習流程:")
        print("  1. 每個 Agent 在本地數據上訓練")
        print("  2. 共享學習成果（梯度/參數）")
        print("  3. 聚合更新到全局模型")
        print("  4. 分發更新後的模型")

        """
        for epoch in range(10):
            # 本地訓練
            for agent in learners:
                agent.train_local()

            # 聚合學習成果
            updates = learning_env.aggregate([
                agent.get_updates() for agent in learners
            ])

            # 分發更新
            for agent in learners:
                agent.apply_updates(updates)
        """

        print("\n✓ 協作學習配置完成")

    def example_10_agent_ecosystem(self):
        """範例 10: Agent 生態系統"""
        print("\n" + "="*60)
        print("範例 10: Agent 生態系統")
        print("="*60)

        from google_adk.ecosystem import AgentEcosystem

        # 創建 Agent 生態系統
        ecosystem = AgentEcosystem(
            name="enterprise-ai-system",
            discovery_enabled=True,  # 啟用服務發現
            auto_scaling=True,       # 自動擴展
            health_check=True        # 健康檢查
        )

        # 註冊不同類型的 Agent
        agent_types = {
            "customer_service": {
                "count": 5,
                "role": "處理客戶諮詢",
                "scaling": {"min": 3, "max": 10}
            },
            "data_analysis": {
                "count": 3,
                "role": "數據分析和報告",
                "scaling": {"min": 2, "max": 6}
            },
            "content_generation": {
                "count": 4,
                "role": "內容創作",
                "scaling": {"min": 2, "max": 8}
            },
            "monitoring": {
                "count": 2,
                "role": "系統監控",
                "scaling": {"min": 2, "max": 2}
            }
        }

        print("Agent 生態系統:")
        total_agents = 0
        for agent_type, config in agent_types.items():
            count = config["count"]
            total_agents += count
            print(f"  - {agent_type}: {count} 個 ({config['role']})")
            print(f"    擴展範圍: {config['scaling']['min']}-{config['scaling']['max']}")

        print(f"\n總計: {total_agents} 個 Agent")

        # 生態系統功能
        print("\n生態系統功能:")
        print("  ✓ 服務發現: Agent 自動註冊和發現")
        print("  ✓ 負載均衡: 自動分配任務")
        print("  ✓ 自動擴展: 根據負載調整 Agent 數量")
        print("  ✓ 健康檢查: 監控 Agent 狀態")
        print("  ✓ 故障恢復: 自動重啟失敗的 Agent")

        """
        # 啟動生態系統
        ecosystem.start()

        # 提交任務
        task_id = ecosystem.submit_task(
            task_type="customer_service",
            content="客戶諮詢問題"
        )

        # 監控狀態
        status = ecosystem.get_status()
        print(f"活躍 Agent: {status['active_agents']}")
        print(f"待處理任務: {status['pending_tasks']}")
        """

        print("\n✓ Agent 生態系統配置完成")


def main():
    """主函數"""
    print("="*60)
    print("Google ADK - 多 Agent 協作範例")
    print("="*60)

    # 檢查 API 密鑰
    if not os.getenv("GOOGLE_API_KEY"):
        print("\n⚠️  請先設置 GOOGLE_API_KEY 環境變量")
        print("export GOOGLE_API_KEY='your-api-key-here'")
        return

    # 創建範例實例
    example = MultiAgentExample()

    try:
        # 運行所有範例
        example.example_1_basic_multi_agent()
        example.example_2_sequential_orchestration()
        example.example_3_parallel_orchestration()
        example.example_4_hierarchical_orchestration()
        example.example_5_agent_communication()
        example.example_6_task_distribution()
        example.example_7_conflict_resolution()
        example.example_8_agent_specialization()
        example.example_9_collaborative_learning()
        example.example_10_agent_ecosystem()

        print("\n" + "="*60)
        print("所有多 Agent 協作範例執行完成！")
        print("="*60)

    except Exception as e:
        print(f"\n❌ 執行錯誤: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

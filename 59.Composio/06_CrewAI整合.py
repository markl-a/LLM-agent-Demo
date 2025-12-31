#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Composio CrewAI 整合範例
========================

本範例展示如何整合 Composio 與 CrewAI，包括：
1. CrewAI Agent 配置
2. Composio 工具整合
3. 多 Agent 協作
4. 任務分配和執行
5. 工作流程編排
6. 實際應用場景
7. 團隊協作模式

CrewAI 是一個強大的多 Agent 協作框架，與 Composio 完美配合。

作者: Composio 團隊
日期: 2025-01-01
"""

import os
import sys
import json
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 導入 CrewAI 和 Composio
try:
    from crewai import Agent, Task, Crew, Process
    from langchain_openai import ChatOpenAI
    from composio_crewai import ComposioToolSet, App, Action
except ImportError as e:
    print("錯誤：請先安裝必要的套件")
    print("執行: pip install composio-crewai crewai langchain-openai")
    sys.exit(1)


class CrewAIComposioIntegration:
    """
    CrewAI 與 Composio 整合類別

    提供完整的整合功能，包括：
    - 工具集配置
    - Agent 創建
    - 任務定義
    - Crew 編排
    - 執行管理
    """

    def __init__(self, composio_api_key: Optional[str] = None,
                 openai_api_key: Optional[str] = None,
                 model: str = "gpt-4"):
        """
        初始化整合

        Args:
            composio_api_key: Composio API 金鑰
            openai_api_key: OpenAI API 金鑰
            model: OpenAI 模型名稱
        """
        print("=" * 70)
        print("初始化 CrewAI-Composio 整合")
        print("=" * 70)

        # 設置 API 金鑰
        self.composio_api_key = composio_api_key or os.getenv("COMPOSIO_API_KEY")
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")

        if not self.composio_api_key:
            print("警告：未設置 COMPOSIO_API_KEY")

        if not self.openai_api_key:
            print("警告：未設置 OPENAI_API_KEY")

        try:
            # 初始化 Composio 工具集
            self.toolset = ComposioToolSet(api_key=self.composio_api_key)
            print("✓ Composio 工具集初始化成功")

            # 初始化 LLM
            self.llm = ChatOpenAI(
                model=model,
                temperature=0.7,
                openai_api_key=self.openai_api_key
            )
            print(f"✓ OpenAI LLM 初始化成功 (模型: {model})")

        except Exception as e:
            print(f"✗ 初始化失敗: {e}")
            raise

    def get_tools(self, apps: Optional[List[str]] = None,
                  actions: Optional[List[str]] = None) -> List:
        """
        獲取 Composio 工具

        Args:
            apps: 應用程式列表
            actions: 動作列表

        Returns:
            工具列表
        """
        print("\n" + "=" * 70)
        print("獲取 Composio 工具")
        print("=" * 70)

        try:
            # 獲取工具
            if apps:
                tools = self.toolset.get_tools(apps=apps)
                print(f"✓ 從應用程式獲取了 {len(tools)} 個工具")
            elif actions:
                tools = self.toolset.get_tools(actions=actions)
                print(f"✓ 獲取了 {len(tools)} 個特定動作工具")
            else:
                tools = []

            return tools

        except Exception as e:
            print(f"✗ 獲取工具失敗: {e}")
            return []

    def create_agent(self, role: str, goal: str, backstory: str,
                    tools: List, verbose: bool = True,
                    allow_delegation: bool = False) -> Agent:
        """
        創建 CrewAI Agent

        Args:
            role: Agent 角色
            goal: Agent 目標
            backstory: Agent 背景故事
            tools: 工具列表
            verbose: 是否顯示詳細資訊
            allow_delegation: 是否允許委派任務

        Returns:
            Agent 對象
        """
        print("\n" + "=" * 70)
        print(f"創建 Agent: {role}")
        print("=" * 70)

        try:
            agent = Agent(
                role=role,
                goal=goal,
                backstory=backstory,
                tools=tools,
                llm=self.llm,
                verbose=verbose,
                allow_delegation=allow_delegation
            )

            print(f"✓ Agent '{role}' 創建成功")
            print(f"  目標: {goal}")
            print(f"  工具數量: {len(tools)}")

            return agent

        except Exception as e:
            print(f"✗ 創建 Agent 失敗: {e}")
            raise

    def create_task(self, description: str, agent: Agent,
                   expected_output: Optional[str] = None) -> Task:
        """
        創建任務

        Args:
            description: 任務描述
            agent: 負責的 Agent
            expected_output: 預期輸出

        Returns:
            Task 對象
        """
        task = Task(
            description=description,
            agent=agent,
            expected_output=expected_output or "任務完成報告"
        )

        return task

    def create_crew(self, agents: List[Agent], tasks: List[Task],
                   process: Process = Process.sequential,
                   verbose: bool = True) -> Crew:
        """
        創建 Crew

        Args:
            agents: Agent 列表
            tasks: 任務列表
            process: 執行流程（sequential/hierarchical）
            verbose: 是否顯示詳細資訊

        Returns:
            Crew 對象
        """
        print("\n" + "=" * 70)
        print("創建 Crew")
        print("=" * 70)

        try:
            crew = Crew(
                agents=agents,
                tasks=tasks,
                process=process,
                verbose=verbose
            )

            print(f"✓ Crew 創建成功")
            print(f"  Agents 數量: {len(agents)}")
            print(f"  任務數量: {len(tasks)}")
            print(f"  執行流程: {process.value}")

            return crew

        except Exception as e:
            print(f"✗ 創建 Crew 失敗: {e}")
            raise

    def run_crew(self, crew: Crew) -> str:
        """
        執行 Crew

        Args:
            crew: Crew 對象

        Returns:
            執行結果
        """
        print("\n" + "=" * 70)
        print("執行 Crew")
        print("=" * 70)

        try:
            result = crew.kickoff()

            print("\n" + "=" * 70)
            print("執行完成")
            print("=" * 70)

            return result

        except Exception as e:
            print(f"\n✗ 執行失敗: {e}")
            return f"錯誤: {e}"


class SoftwareDevelopmentCrew:
    """
    軟體開發團隊

    模擬一個完整的軟體開發團隊，包括：
    - 產品經理
    - 開發工程師
    - 測試工程師
    """

    def __init__(self):
        """初始化軟體開發團隊"""
        print("\n" + "=" * 70)
        print("初始化軟體開發團隊")
        print("=" * 70)

        # 創建整合實例
        self.integration = CrewAIComposioIntegration()

        # 獲取工具
        github_tools = self.integration.get_tools(apps=["github"])
        slack_tools = self.integration.get_tools(apps=["slack"])

        # 創建產品經理 Agent
        self.product_manager = self.integration.create_agent(
            role="產品經理",
            goal="定義產品需求並管理開發流程",
            backstory="""你是一位經驗豐富的產品經理，擅長：
- 分析用戶需求
- 定義產品規格
- 管理開發進度
- 協調團隊溝通""",
            tools=github_tools + slack_tools,
            allow_delegation=True
        )

        # 創建開發工程師 Agent
        self.developer = self.integration.create_agent(
            role="軟體開發工程師",
            goal="實現產品功能並保證代碼質量",
            backstory="""你是一位資深的軟體開發工程師，專長於：
- 編寫高質量代碼
- 進行代碼審查
- 解決技術問題
- 遵循最佳實踐""",
            tools=github_tools,
            allow_delegation=False
        )

        # 創建測試工程師 Agent
        self.qa_engineer = self.integration.create_agent(
            role="測試工程師",
            goal="確保產品質量和穩定性",
            backstory="""你是一位細心的測試工程師，負責：
- 設計測試計劃
- 執行功能測試
- 報告 Bug
- 驗證修復""",
            tools=github_tools + slack_tools,
            allow_delegation=False
        )

    def develop_feature(self, feature_description: str) -> str:
        """
        開發新功能

        Args:
            feature_description: 功能描述

        Returns:
            開發結果
        """
        print("\n" + "=" * 70)
        print(f"開發新功能: {feature_description}")
        print("=" * 70)

        # 定義任務
        # 任務1: 需求分析
        requirement_task = self.integration.create_task(
            description=f"""
分析以下功能需求：{feature_description}

請執行以下步驟：
1. 理解功能需求
2. 在 GitHub 創建相應的 Issue
3. 定義驗收標準
4. 在 Slack 通知開發團隊
            """,
            agent=self.product_manager,
            expected_output="需求分析報告和 GitHub Issue 連結"
        )

        # 任務2: 代碼實現
        development_task = self.integration.create_task(
            description="""
基於產品經理創建的 Issue，進行代碼實現：

1. 創建功能分支
2. 實現代碼
3. 進行自我審查
4. 創建 Pull Request
            """,
            agent=self.developer,
            expected_output="Pull Request 連結"
        )

        # 任務3: 測試驗證
        testing_task = self.integration.create_task(
            description="""
測試新開發的功能：

1. 審查 Pull Request
2. 執行功能測試
3. 如有問題，在 PR 中添加評論
4. 驗證通過後，在 Slack 通知團隊
            """,
            agent=self.qa_engineer,
            expected_output="測試報告"
        )

        # 創建並執行 Crew
        crew = self.integration.create_crew(
            agents=[self.product_manager, self.developer, self.qa_engineer],
            tasks=[requirement_task, development_task, testing_task],
            process=Process.sequential
        )

        result = self.integration.run_crew(crew)
        return result


class MarketingCampaignCrew:
    """
    營銷活動團隊

    管理營銷活動的 AI 團隊
    """

    def __init__(self):
        """初始化營銷活動團隊"""
        print("\n" + "=" * 70)
        print("初始化營銷活動團隊")
        print("=" * 70)

        # 創建整合實例
        self.integration = CrewAIComposioIntegration()

        # 獲取工具
        slack_tools = self.integration.get_tools(apps=["slack"])

        # 創建內容創作者 Agent
        self.content_creator = self.integration.create_agent(
            role="內容創作者",
            goal="創作吸引人的營銷內容",
            backstory="""你是一位富有創意的內容創作者，擅長：
- 撰寫引人入勝的文案
- 設計營銷策略
- 了解目標受眾
- 創新內容形式""",
            tools=slack_tools
        )

        # 創建社交媒體經理 Agent
        self.social_media_manager = self.integration.create_agent(
            role="社交媒體經理",
            goal="管理和發布社交媒體內容",
            backstory="""你是一位經驗豐富的社交媒體經理，負責：
- 規劃發布時間
- 管理多個平台
- 監控互動反饋
- 優化內容策略""",
            tools=slack_tools
        )

        # 創建數據分析師 Agent
        self.data_analyst = self.integration.create_agent(
            role="數據分析師",
            goal="分析營銷活動效果",
            backstory="""你是一位數據驅動的分析師，專注於：
- 收集營銷數據
- 分析活動效果
- 提供優化建議
- 創建報告儀表板""",
            tools=slack_tools
        )

    def run_campaign(self, campaign_description: str) -> str:
        """
        執行營銷活動

        Args:
            campaign_description: 活動描述

        Returns:
            執行結果
        """
        # 創建任務
        content_task = self.integration.create_task(
            description=f"為以下營銷活動創作內容：{campaign_description}",
            agent=self.content_creator
        )

        publishing_task = self.integration.create_task(
            description="發布內容到社交媒體並在 Slack 通知團隊",
            agent=self.social_media_manager
        )

        analysis_task = self.integration.create_task(
            description="分析活動效果並在 Slack 分享報告",
            agent=self.data_analyst
        )

        # 創建並執行 Crew
        crew = self.integration.create_crew(
            agents=[self.content_creator, self.social_media_manager, self.data_analyst],
            tasks=[content_task, publishing_task, analysis_task]
        )

        return self.integration.run_crew(crew)


class CustomerSupportCrew:
    """
    客戶支援團隊

    處理客戶問題的 AI 團隊
    """

    def __init__(self):
        """初始化客戶支援團隊"""
        print("\n" + "=" * 70)
        print("初始化客戶支援團隊")
        print("=" * 70)

        # 創建整合實例
        self.integration = CrewAIComposioIntegration()

        # 獲取工具
        github_tools = self.integration.get_tools(apps=["github"])
        slack_tools = self.integration.get_tools(apps=["slack"])

        # 創建客服專員 Agent
        self.support_agent = self.integration.create_agent(
            role="客服專員",
            goal="快速解決客戶問題",
            backstory="""你是一位友善的客服專員，專注於：
- 理解客戶問題
- 提供解決方案
- 升級複雜問題
- 確保客戶滿意""",
            tools=slack_tools,
            allow_delegation=True
        )

        # 創建技術支援 Agent
        self.tech_support = self.integration.create_agent(
            role="技術支援工程師",
            goal="解決技術問題",
            backstory="""你是一位技術專家，負責：
- 診斷技術問題
- 提供技術解決方案
- 創建 Bug 報告
- 協助客戶""",
            tools=github_tools + slack_tools
        )

        # 創建客戶成功經理 Agent
        self.success_manager = self.integration.create_agent(
            role="客戶成功經理",
            goal="確保客戶長期成功",
            backstory="""你是一位客戶成功經理，關注：
- 客戶滿意度
- 產品採用率
- 客戶反饋
- 持續改進""",
            tools=slack_tools
        )

    def handle_ticket(self, ticket_description: str) -> str:
        """
        處理客戶工單

        Args:
            ticket_description: 工單描述

        Returns:
            處理結果
        """
        # 創建任務
        initial_response = self.integration.create_task(
            description=f"回應客戶問題：{ticket_description}",
            agent=self.support_agent
        )

        technical_resolution = self.integration.create_task(
            description="如有技術問題，提供解決方案並在 GitHub 創建 Issue",
            agent=self.tech_support
        )

        follow_up = self.integration.create_task(
            description="跟進客戶滿意度並在 Slack 分享反饋",
            agent=self.success_manager
        )

        # 創建並執行 Crew
        crew = self.integration.create_crew(
            agents=[self.support_agent, self.tech_support, self.success_manager],
            tasks=[initial_response, technical_resolution, follow_up]
        )

        return self.integration.run_crew(crew)


def demo_basic_crew():
    """
    演示基礎 Crew 使用
    """
    print("\n" + "=" * 80)
    print("CrewAI 基礎使用演示")
    print("=" * 80)

    print("\nCrewAI 核心概念:")
    print("-" * 80)
    print("""
1. Agent（代理）
   - 具有特定角色和目標的 AI
   - 配備特定工具
   - 可以委派任務給其他 Agent

2. Task（任務）
   - 具體的工作項目
   - 分配給特定 Agent
   - 有明確的預期輸出

3. Crew（團隊）
   - 多個 Agent 的集合
   - 按順序或階層執行任務
   - 協同完成複雜目標

4. Process（流程）
   - Sequential：順序執行
   - Hierarchical：階層式管理
    """)


def demo_collaboration_patterns():
    """
    演示協作模式
    """
    print("\n" + "=" * 80)
    print("Agent 協作模式")
    print("=" * 80)

    patterns = [
        ("順序協作", [
            "Agent A 完成任務後，傳遞給 Agent B",
            "適合有明確步驟的流程",
            "例如：需求分析 → 開發 → 測試"
        ]),
        ("並行協作", [
            "多個 Agent 同時處理不同任務",
            "提高效率",
            "例如：同時進行多個功能開發"
        ]),
        ("階層協作", [
            "有管理者 Agent 協調其他 Agent",
            "適合複雜的項目",
            "例如：產品經理協調開發團隊"
        ]),
        ("委派模式", [
            "Agent 可以將任務委派給專家",
            "靈活的任務分配",
            "例如：主 Agent 委派技術問題給技術 Agent"
        ])
    ]

    for pattern, descriptions in patterns:
        print(f"\n{pattern}:")
        for desc in descriptions:
            print(f"  • {desc}")


def print_best_practices():
    """
    印出最佳實踐
    """
    print("\n" + "=" * 80)
    print("CrewAI-Composio 整合最佳實踐")
    print("=" * 80)

    practices = [
        ("1. Agent 設計", [
            "為每個 Agent 定義清晰的角色",
            "設置具體的目標",
            "撰寫詳細的背景故事",
            "分配合適的工具"
        ]),
        ("2. 任務設計", [
            "任務描述要具體明確",
            "定義預期輸出",
            "考慮任務依賴關係",
            "設置合理的複雜度"
        ]),
        ("3. 團隊編排", [
            "選擇合適的執行流程",
            "平衡 Agent 數量",
            "避免循環依賴",
            "測試協作邏輯"
        ]),
        ("4. 工具使用", [
            "只提供必要的工具",
            "避免工具衝突",
            "測試工具可用性",
            "處理工具錯誤"
        ]),
        ("5. 性能優化", [
            "限制 Agent 迭代次數",
            "使用快取機制",
            "監控執行時間",
            "優化提示詞"
        ])
    ]

    for title, items in practices:
        print(f"\n{title}")
        print("-" * 80)
        for item in items:
            print(f"  • {item}")


def main():
    """
    主函數
    """
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║              Composio CrewAI 整合範例                            ║
    ║                                                                  ║
    ║              構建協作式 AI 團隊                                  ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)

    # 演示基礎使用
    demo_basic_crew()

    # 演示協作模式
    demo_collaboration_patterns()

    # 印出最佳實踐
    print_best_practices()

    print("\n" + "=" * 80)
    print("團隊範例:")
    print("  • SoftwareDevelopmentCrew - 軟體開發團隊")
    print("  • MarketingCampaignCrew - 營銷活動團隊")
    print("  • CustomerSupportCrew - 客戶支援團隊")
    print("\n更多資源:")
    print("  • CrewAI 文檔: https://docs.crewai.com")
    print("  • Composio-CrewAI: https://docs.composio.dev/crewai")
    print("=" * 80)


if __name__ == "__main__":
    main()

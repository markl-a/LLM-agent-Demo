#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Composio LangChain 整合範例
===========================

本範例展示如何整合 Composio 與 LangChain，包括：
1. ComposioToolSet 初始化
2. 工具整合到 LangChain Agent
3. 創建功能性 AI Agent
4. 鏈式工具調用
5. 記憶和狀態管理
6. 錯誤處理和重試
7. 實際應用場景

LangChain 是最流行的 LLM 應用開發框架，與 Composio 完美整合。

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

# 導入 LangChain 和 Composio
try:
    from langchain.agents import AgentExecutor, create_openai_functions_agent
    from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_openai import ChatOpenAI
    from langchain.memory import ConversationBufferMemory
    from langchain.schema import HumanMessage, AIMessage, SystemMessage
    from composio_langchain import ComposioToolSet, App, Action
except ImportError as e:
    print("錯誤：請先安裝必要的套件")
    print("執行: pip install composio-langchain langchain langchain-openai")
    sys.exit(1)


class LangChainComposioIntegration:
    """
    LangChain 與 Composio 整合類別

    提供完整的整合功能，包括：
    - 工具集配置
    - Agent 創建
    - 任務執行
    - 記憶管理
    - 工作流程編排
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
        print("初始化 LangChain-Composio 整合")
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
                temperature=0,
                openai_api_key=self.openai_api_key
            )
            print(f"✓ OpenAI LLM 初始化成功 (模型: {model})")

            # 初始化記憶
            self.memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )

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
            LangChain 工具列表
        """
        print("\n" + "=" * 70)
        print("獲取 Composio 工具")
        print("=" * 70)

        try:
            # 獲取工具
            if apps:
                tools = self.toolset.get_tools(apps=apps)
                print(f"✓ 從應用程式獲取了 {len(tools)} 個工具")
                print(f"  應用: {', '.join(apps)}")
            elif actions:
                tools = self.toolset.get_tools(actions=actions)
                print(f"✓ 獲取了 {len(tools)} 個特定動作工具")
            else:
                print("⚠ 未指定應用或動作")
                tools = []

            # 顯示工具資訊
            if tools:
                print("\n可用工具:")
                print("-" * 70)
                for i, tool in enumerate(tools[:10], 1):  # 只顯示前10個
                    print(f"{i}. {tool.name}")
                if len(tools) > 10:
                    print(f"... 還有 {len(tools) - 10} 個工具")

            return tools

        except Exception as e:
            print(f"✗ 獲取工具失敗: {e}")
            return []

    def create_agent(self, tools: List, system_message: str = None) -> AgentExecutor:
        """
        創建 LangChain Agent

        Args:
            tools: 工具列表
            system_message: 系統訊息

        Returns:
            Agent 執行器
        """
        print("\n" + "=" * 70)
        print("創建 LangChain Agent")
        print("=" * 70)

        try:
            # 設置預設系統訊息
            if not system_message:
                system_message = """你是一個有用的 AI 助手，可以使用各種工具來完成任務。

請根據用戶的請求：
1. 分析需要使用哪些工具
2. 按照正確的順序執行操作
3. 提供清晰的執行結果
4. 如果遇到錯誤，嘗試解決或向用戶說明

始終保持專業和有禮貌。"""

            # 創建提示模板
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_message),
                MessagesPlaceholder(variable_name="chat_history", optional=True),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad")
            ])

            # 創建 Agent
            agent = create_openai_functions_agent(
                llm=self.llm,
                tools=tools,
                prompt=prompt
            )

            # 創建 Agent 執行器
            agent_executor = AgentExecutor(
                agent=agent,
                tools=tools,
                memory=self.memory,
                verbose=True,
                handle_parsing_errors=True,
                max_iterations=10
            )

            print(f"✓ Agent 創建成功")
            print(f"  工具數量: {len(tools)}")
            print(f"  最大迭代: 10")

            return agent_executor

        except Exception as e:
            print(f"✗ 創建 Agent 失敗: {e}")
            raise

    def run_agent(self, agent_executor: AgentExecutor, task: str) -> Dict[str, Any]:
        """
        執行 Agent 任務

        Args:
            agent_executor: Agent 執行器
            task: 任務描述

        Returns:
            執行結果
        """
        print("\n" + "=" * 70)
        print("執行 Agent 任務")
        print("=" * 70)
        print(f"\n任務: {task}")
        print("-" * 70)

        try:
            # 執行任務
            result = agent_executor.invoke({"input": task})

            print("\n" + "=" * 70)
            print("任務完成")
            print("=" * 70)
            print(f"\n輸出: {result['output']}")

            return result

        except Exception as e:
            print(f"\n✗ 執行失敗: {e}")
            return {"error": str(e)}


class GitHubAssistant:
    """
    GitHub 助手 Agent

    專門處理 GitHub 相關任務的 AI Agent
    """

    def __init__(self):
        """初始化 GitHub 助手"""
        print("\n" + "=" * 70)
        print("初始化 GitHub 助手")
        print("=" * 70)

        # 創建整合實例
        self.integration = LangChainComposioIntegration()

        # 獲取 GitHub 工具
        self.tools = self.integration.get_tools(apps=["github"])

        # 創建專門的 GitHub Agent
        system_message = """你是一個專業的 GitHub 助手，擅長管理代碼倉庫。

你的職責包括：
1. 管理 GitHub Issues 和 Pull Requests
2. 審查代碼和提供反饋
3. 自動化 GitHub 工作流程
4. 協助團隊協作

請使用專業的語言，並確保所有操作都是安全和符合最佳實踐的。"""

        self.agent = self.integration.create_agent(
            tools=self.tools,
            system_message=system_message
        )

    def handle_task(self, task: str) -> Dict[str, Any]:
        """
        處理 GitHub 相關任務

        Args:
            task: 任務描述

        Returns:
            執行結果
        """
        return self.integration.run_agent(self.agent, task)


class SlackNotifier:
    """
    Slack 通知器 Agent

    專門處理 Slack 訊息通知的 AI Agent
    """

    def __init__(self):
        """初始化 Slack 通知器"""
        print("\n" + "=" * 70)
        print("初始化 Slack 通知器")
        print("=" * 70)

        # 創建整合實例
        self.integration = LangChainComposioIntegration()

        # 獲取 Slack 工具
        self.tools = self.integration.get_tools(apps=["slack"])

        # 創建 Slack Agent
        system_message = """你是一個 Slack 通知助手，負責發送團隊通知。

你的職責包括：
1. 發送訊息到正確的頻道
2. 格式化訊息使其清晰易讀
3. 管理頻道和用戶通知
4. 確保訊息及時送達

請保持訊息簡潔、專業和友好。"""

        self.agent = self.integration.create_agent(
            tools=self.tools,
            system_message=system_message
        )

    def send_notification(self, task: str) -> Dict[str, Any]:
        """
        發送 Slack 通知

        Args:
            task: 通知任務描述

        Returns:
            執行結果
        """
        return self.integration.run_agent(self.agent, task)


class MultiAppAgent:
    """
    多應用 Agent

    可以同時使用多個應用的工具
    """

    def __init__(self, apps: List[str]):
        """
        初始化多應用 Agent

        Args:
            apps: 應用程式列表
        """
        print("\n" + "=" * 70)
        print(f"初始化多應用 Agent")
        print(f"應用: {', '.join(apps)}")
        print("=" * 70)

        # 創建整合實例
        self.integration = LangChainComposioIntegration()

        # 獲取多個應用的工具
        self.tools = self.integration.get_tools(apps=apps)

        # 創建通用 Agent
        system_message = f"""你是一個多功能 AI 助手，可以使用多個應用的工具。

可用的應用：{', '.join(apps)}

你的職責：
1. 理解用戶的需求
2. 選擇合適的工具組合
3. 協調多個工具的使用
4. 提供綜合的解決方案

請智能地使用工具，並確保操作的正確性。"""

        self.agent = self.integration.create_agent(
            tools=self.tools,
            system_message=system_message
        )

    def execute(self, task: str) -> Dict[str, Any]:
        """
        執行任務

        Args:
            task: 任務描述

        Returns:
            執行結果
        """
        return self.integration.run_agent(self.agent, task)


def demo_basic_integration():
    """
    演示基礎整合
    """
    print("\n" + "=" * 80)
    print("LangChain-Composio 基礎整合演示")
    print("=" * 80)

    try:
        # 創建整合實例
        integration = LangChainComposioIntegration()

        # 示例：獲取工具
        print("\n1. 獲取 GitHub 工具")
        github_tools = integration.get_tools(apps=["github"])

        print("\n2. 獲取 Slack 工具")
        slack_tools = integration.get_tools(apps=["slack"])

        print("\n3. 創建 Agent（示例）")
        print("   tools = integration.get_tools(apps=['github'])")
        print("   agent = integration.create_agent(tools)")
        print("   result = integration.run_agent(agent, '列出我的倉庫')")

    except Exception as e:
        print(f"\n演示過程中發生錯誤: {e}")


def demo_github_assistant():
    """
    演示 GitHub 助手
    """
    print("\n" + "=" * 80)
    print("GitHub 助手演示")
    print("=" * 80)

    # 示例任務
    tasks = [
        "列出我的所有 GitHub 倉庫",
        "在倉庫 'my-project' 中創建一個新的 Issue，標題是 '添加文檔'",
        "查看倉庫 'my-project' 中所有開放的 Pull Requests",
        "審查 Pull Request #42 並添加評論"
    ]

    print("\nGitHub 助手可以處理的任務示例:")
    print("-" * 80)
    for i, task in enumerate(tasks, 1):
        print(f"{i}. {task}")

    print("\n使用方式:")
    print("-" * 80)
    print("""
assistant = GitHubAssistant()
result = assistant.handle_task("列出我的 GitHub 倉庫")
    """)


def demo_slack_notifier():
    """
    演示 Slack 通知器
    """
    print("\n" + "=" * 80)
    print("Slack 通知器演示")
    print("=" * 80)

    # 示例通知
    notifications = [
        "發送訊息到 #general 頻道：'會議將在10分鐘後開始'",
        "通知 @john 關於新的任務分配",
        "在 #engineering 頻道分享部署成功的消息",
        "創建一個新頻道 #project-alpha 並邀請團隊成員"
    ]

    print("\nSlack 通知器可以處理的任務示例:")
    print("-" * 80)
    for i, notification in enumerate(notifications, 1):
        print(f"{i}. {notification}")

    print("\n使用方式:")
    print("-" * 80)
    print("""
notifier = SlackNotifier()
result = notifier.send_notification(
    "發送訊息到 #general：'部署完成'"
)
    """)


def demo_multi_app_workflow():
    """
    演示多應用工作流程
    """
    print("\n" + "=" * 80)
    print("多應用工作流程演示")
    print("=" * 80)

    workflows = [
        ("代碼審查通知流程", [
            "1. 檢查 GitHub 上的新 Pull Requests",
            "2. 分析 PR 的更改",
            "3. 在 Slack 通知審查者",
            "4. 添加 GitHub 評論確認已通知"
        ]),
        ("每日站會準備", [
            "1. 從 GitHub 獲取昨天的提交",
            "2. 檢查關閉的 Issues",
            "3. 準備更新摘要",
            "4. 發送到 Slack 會議頻道"
        ]),
        ("問題追蹤", [
            "1. 監控系統告警",
            "2. 在 GitHub 創建 Issue",
            "3. 分配給相關開發者",
            "4. 在 Slack 通知團隊"
        ])
    ]

    print("\n常見的多應用工作流程:")
    print("-" * 80)
    for workflow, steps in workflows:
        print(f"\n{workflow}:")
        for step in steps:
            print(f"  {step}")

    print("\n實現示例:")
    print("-" * 80)
    print("""
# 創建多應用 Agent
agent = MultiAppAgent(apps=["github", "slack"])

# 執行複雜任務
task = '''
檢查我的 GitHub 倉庫中是否有新的 Pull Requests，
如果有，在 Slack 的 #code-review 頻道通知團隊。
'''

result = agent.execute(task)
    """)


def print_best_practices():
    """
    印出最佳實踐
    """
    print("\n" + "=" * 80)
    print("LangChain-Composio 整合最佳實踐")
    print("=" * 80)

    practices = [
        ("1. Agent 設計", [
            "使用清晰的系統提示詞",
            "限制工具數量以提高性能",
            "設置合理的最大迭代次數",
            "實施錯誤處理機制"
        ]),
        ("2. 工具選擇", [
            "只加載需要的工具",
            "使用特定動作而非整個應用",
            "考慮工具執行時間",
            "測試工具組合的兼容性"
        ]),
        ("3. 記憶管理", [
            "選擇合適的記憶類型",
            "定期清理對話歷史",
            "注意 token 限制",
            "保護敏感資訊"
        ]),
        ("4. 性能優化", [
            "快取常用結果",
            "並行執行獨立操作",
            "使用流式輸出",
            "監控 API 使用量"
        ]),
        ("5. 錯誤處理", [
            "實施重試邏輯",
            "提供有用的錯誤訊息",
            "記錄失敗案例",
            "優雅地降級"
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
    ║              Composio LangChain 整合範例                         ║
    ║                                                                  ║
    ║              構建強大的 AI Agent 應用                            ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)

    # 演示基礎整合
    demo_basic_integration()

    # 演示 GitHub 助手
    demo_github_assistant()

    # 演示 Slack 通知器
    demo_slack_notifier()

    # 演示多應用工作流程
    demo_multi_app_workflow()

    # 印出最佳實踐
    print_best_practices()

    print("\n" + "=" * 80)
    print("更多資源:")
    print("  • LangChain 文檔: https://python.langchain.com/docs")
    print("  • Composio-LangChain: https://docs.composio.dev/langchain")
    print("  • 範例專案: https://github.com/ComposioHQ/composio/tree/main/python/examples/langchain")
    print("=" * 80)


if __name__ == "__main__":
    main()

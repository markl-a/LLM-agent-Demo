"""
Letta 框架快速開始示例

本模組展示了 Letta (MemGPT) 框架的基本使用方法，包括：
1. 客戶端初始化和配置
2. 創建和管理 Agent
3. 基本對話交互
4. Agent 配置和參數設定
5. 簡單的記憶查看

Letta 是一個革命性的有狀態 AI Agent 框架，能夠讓 Agent 擁有持久記憶。
作者：Letta 框架示例
日期：2025-01
"""

import os
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime


class LettaQuickStart:
    """
    Letta 快速開始類

    這個類演示了 Letta 框架的基本功能，包括創建客戶端、
    設置 Agent、進行對話等核心操作。
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化 Letta 快速開始實例

        參數:
            api_key: OpenAI API 密鑰（可選，也可從環境變量獲取）
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None
        self.agents = {}

        print("=" * 60)
        print("Letta (MemGPT) 框架快速開始")
        print("=" * 60)

    def initialize_client(self) -> None:
        """
        初始化 Letta 客戶端

        這是使用 Letta 的第一步。客戶端負責管理所有的 Agent 和對話。
        在實際應用中，這裡會創建真正的 Letta 客戶端。
        """
        print("\n[步驟 1] 初始化 Letta 客戶端...")

        # 模擬客戶端配置
        config = {
            "api_key": self.api_key,
            "backend": "openai",
            "model": "gpt-4",
            "storage": "local",
            "db_path": "./letta_data"
        }

        # 在實際應用中：
        # from letta import create_client
        # self.client = create_client()

        # 這裡使用模擬客戶端
        self.client = MockLettaClient(config)

        print("✓ 客戶端初始化成功")
        print(f"  - 後端: {config['backend']}")
        print(f"  - 模型: {config['model']}")
        print(f"  - 存儲: {config['storage']}")

    def create_basic_agent(self, name: str = "小助手") -> Dict[str, Any]:
        """
        創建基本的 Letta Agent

        參數:
            name: Agent 的名稱

        返回:
            Agent 狀態字典
        """
        print(f"\n[步驟 2] 創建 Agent: {name}...")

        # 定義 Agent 的 persona（人格設定）
        persona = """
        你是一個友善、樂於助人的 AI 助手。
        你擁有持久記憶，能記住與用戶的所有對話。
        你善於總結信息並在需要時回憶起來。
        你會主動管理自己的記憶，確保重要信息不會遺失。
        """

        # 定義 human 設定（用戶描述）
        human = """
        用戶是一個希望得到長期支持的客戶。
        他們重視對話的連續性和上下文理解。
        """

        # 創建 Agent
        agent_state = self.client.create_agent(
            name=name,
            persona=persona.strip(),
            human=human.strip()
        )

        self.agents[name] = agent_state

        print(f"✓ Agent '{name}' 創建成功")
        print(f"  - ID: {agent_state['id']}")
        print(f"  - 創建時間: {agent_state['created_at']}")

        return agent_state

    def send_message(self, agent_name: str, message: str) -> Dict[str, Any]:
        """
        向 Agent 發送消息

        參數:
            agent_name: Agent 名稱
            message: 要發送的消息

        返回:
            Agent 的響應
        """
        if agent_name not in self.agents:
            raise ValueError(f"Agent '{agent_name}' 不存在")

        agent_state = self.agents[agent_name]

        print(f"\n[用戶] {message}")

        # 發送消息並獲取響應
        response = self.client.send_message(
            agent_id=agent_state['id'],
            message=message
        )

        print(f"[{agent_name}] {response['content']}")

        return response

    def view_core_memory(self, agent_name: str) -> Dict[str, str]:
        """
        查看 Agent 的核心記憶

        核心記憶是 Agent 的"工作記憶"，包含當前對話中最重要的信息。

        參數:
            agent_name: Agent 名稱

        返回:
            核心記憶內容
        """
        if agent_name not in self.agents:
            raise ValueError(f"Agent '{agent_name}' 不存在")

        agent_state = self.agents[agent_name]
        core_memory = self.client.get_core_memory(agent_state['id'])

        print(f"\n[核心記憶] {agent_name}")
        print("-" * 40)
        print(f"人格設定:\n{core_memory['persona']}")
        print(f"\n用戶信息:\n{core_memory['human']}")
        print("-" * 40)

        return core_memory

    def conversation_demo(self) -> None:
        """
        完整的對話演示

        展示如何與 Letta Agent 進行多輪對話，
        並演示 Agent 的記憶能力。
        """
        print("\n" + "=" * 60)
        print("對話演示：測試 Agent 的記憶能力")
        print("=" * 60)

        # 創建 Agent
        agent = self.create_basic_agent("記憶助手")

        # 第一輪對話：介紹自己
        self.send_message("記憶助手", "你好！我叫小明，我是一名 Python 開發者。")
        time.sleep(1)

        # 第二輪對話：分享興趣
        self.send_message("記憶助手", "我最喜歡的編程語言是 Python，我也在學習機器學習。")
        time.sleep(1)

        # 查看核心記憶（應該已經更新）
        self.view_core_memory("記憶助手")

        # 第三輪對話：測試記憶
        self.send_message("記憶助手", "你還記得我的名字嗎？")
        time.sleep(1)

        # 第四輪對話：測試詳細記憶
        self.send_message("記憶助手", "我喜歡什麼編程語言？")

    def multiple_agents_demo(self) -> None:
        """
        多 Agent 演示

        展示如何同時管理多個 Agent，每個 Agent 有獨立的記憶。
        """
        print("\n" + "=" * 60)
        print("多 Agent 演示")
        print("=" * 60)

        # 創建多個不同用途的 Agent
        agents_config = [
            ("技術顧問", "你是一個專業的技術顧問，專注於軟件開發和架構設計。"),
            ("生活助手", "你是一個貼心的生活助手，幫助用戶管理日常事務。"),
            ("學習夥伴", "你是一個學習夥伴，幫助用戶學習新知識和技能。")
        ]

        for name, persona in agents_config:
            print(f"\n創建 Agent: {name}")
            agent_state = self.client.create_agent(
                name=name,
                persona=persona,
                human="用戶是一個追求成長的專業人士。"
            )
            self.agents[name] = agent_state
            print(f"✓ {name} 創建成功 (ID: {agent_state['id']})")

        # 與不同 Agent 對話
        print("\n" + "-" * 60)
        self.send_message("技術顧問", "我想學習微服務架構，有什麼建議？")

        print("\n" + "-" * 60)
        self.send_message("生活助手", "提醒我明天早上 9 點開會。")

        print("\n" + "-" * 60)
        self.send_message("學習夥伴", "能幫我制定一個 Python 學習計劃嗎？")


class MockLettaClient:
    """
    模擬的 Letta 客戶端

    在實際應用中，這會是真正的 Letta 客戶端。
    這個模擬版本用於演示目的。
    """

    def __init__(self, config: Dict[str, Any]):
        """初始化模擬客戶端"""
        self.config = config
        self.agents = {}
        self.agent_counter = 0

    def create_agent(self, name: str, persona: str, human: str) -> Dict[str, Any]:
        """創建新的 Agent"""
        self.agent_counter += 1
        agent_id = f"agent_{self.agent_counter}"

        agent_state = {
            "id": agent_id,
            "name": name,
            "persona": persona,
            "human": human,
            "created_at": datetime.now().isoformat(),
            "core_memory": {
                "persona": persona,
                "human": human
            },
            "messages": []
        }

        self.agents[agent_id] = agent_state
        return agent_state

    def send_message(self, agent_id: str, message: str) -> Dict[str, Any]:
        """向 Agent 發送消息"""
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} 不存在")

        agent = self.agents[agent_id]

        # 記錄消息
        agent['messages'].append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })

        # 生成響應（簡化版）
        response_content = self._generate_response(agent, message)

        agent['messages'].append({
            "role": "assistant",
            "content": response_content,
            "timestamp": datetime.now().isoformat()
        })

        return {
            "content": response_content,
            "agent_id": agent_id,
            "timestamp": datetime.now().isoformat()
        }

    def get_core_memory(self, agent_id: str) -> Dict[str, str]:
        """獲取核心記憶"""
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} 不存在")

        agent = self.agents[agent_id]

        # 根據對話歷史更新核心記憶
        if len(agent['messages']) > 0:
            # 模擬記憶更新
            user_info = []
            for msg in agent['messages']:
                if msg['role'] == 'user':
                    if '小明' in msg['content']:
                        user_info.append("用戶名稱：小明")
                    if 'Python' in msg['content']:
                        user_info.append("技能：Python 開發")
                    if '機器學習' in msg['content']:
                        user_info.append("興趣：機器學習")

            if user_info:
                agent['core_memory']['human'] = agent['human'] + "\n" + "\n".join(user_info)

        return agent['core_memory']

    def _generate_response(self, agent: Dict[str, Any], message: str) -> str:
        """生成響應（簡化版）"""
        message_lower = message.lower()

        # 簡單的關鍵詞匹配
        if '名字' in message or '叫什麼' in message:
            if any('小明' in msg['content'] for msg in agent['messages'] if msg['role'] == 'user'):
                return "當然記得！你是小明。"
            return "抱歉，你還沒告訴我你的名字。"

        elif '編程語言' in message or '喜歡什麼' in message:
            if any('Python' in msg['content'] for msg in agent['messages'] if msg['role'] == 'user'):
                return "你最喜歡 Python！而且你還在學習機器學習。"
            return "你還沒告訴我你喜歡什麼編程語言。"

        elif '你好' in message or 'hello' in message_lower:
            return f"你好！我是 {agent['name']}，很高興認識你！我會記住我們的每一次對話。"

        elif '微服務' in message:
            return "微服務架構是個很好的學習方向！建議從理解分布式系統開始，然後學習容器化、API 設計和服務編排。"

        elif '提醒' in message or '開會' in message:
            return "好的，我已經記下了！明天早上 9 點的會議，我會提醒你的。"

        elif '學習計劃' in message:
            return "當然可以！建議分三個階段：1) 基礎語法和數據結構 2) 面向對象和常用庫 3) 高級特性和框架。每個階段 4-6 週。"

        else:
            return f"我理解了。作為 {agent['name']}，我會記住這些信息，並在需要時回憶起來。"


def demonstrate_agent_lifecycle():
    """
    演示 Agent 的完整生命週期

    包括創建、使用、查看狀態和清理。
    """
    print("\n" + "=" * 60)
    print("Agent 生命週期演示")
    print("=" * 60)

    quick_start = LettaQuickStart()
    quick_start.initialize_client()

    # 創建 Agent
    agent = quick_start.create_basic_agent("生命週期測試")

    # 使用 Agent
    quick_start.send_message("生命週期測試", "你好！")
    quick_start.send_message("生命週期測試", "今天天氣不錯。")

    # 查看狀態
    quick_start.view_core_memory("生命週期測試")

    print("\n✓ Agent 生命週期演示完成")


def demonstrate_persistence():
    """
    演示持久化特性

    展示如何保存和恢復 Agent 狀態。
    """
    print("\n" + "=" * 60)
    print("持久化演示")
    print("=" * 60)

    quick_start = LettaQuickStart()
    quick_start.initialize_client()

    # 創建並使用 Agent
    agent = quick_start.create_basic_agent("持久化測試")
    quick_start.send_message("持久化測試", "我叫張三，是一名醫生。")

    # 獲取 Agent 狀態
    agent_state = quick_start.agents["持久化測試"]

    print("\n[保存狀態]")
    print(f"Agent ID: {agent_state['id']}")
    print(f"消息數量: {len(agent_state.get('messages', []))}")

    # 在實際應用中，這裡會將狀態保存到數據庫
    # 然後可以在另一個會話中恢復

    print("\n✓ 在實際應用中，這個 Agent 的所有狀態都會自動保存")
    print("  下次創建客戶端時，可以通過 ID 恢復這個 Agent")


def advanced_configuration_demo():
    """
    高級配置演示

    展示如何配置 Agent 的各種參數。
    """
    print("\n" + "=" * 60)
    print("高級配置演示")
    print("=" * 60)

    # 配置選項
    configs = {
        "基本配置": {
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 2000
        },
        "記憶配置": {
            "core_memory_size": 2048,
            "archival_storage": "chromadb",
            "recall_storage": "sqlite"
        },
        "行為配置": {
            "persona_mode": "friendly",
            "verbosity": "normal",
            "memory_management": "auto"
        }
    }

    for category, settings in configs.items():
        print(f"\n[{category}]")
        for key, value in settings.items():
            print(f"  {key}: {value}")

    print("\n✓ 這些配置可以在創建 Agent 時指定")
    print("  或在運行時動態調整")


def main():
    """
    主函數：運行所有演示
    """
    print("\n" + "=" * 70)
    print(" " * 20 + "Letta 框架快速開始教程")
    print("=" * 70)

    # 基本演示
    quick_start = LettaQuickStart()
    quick_start.initialize_client()

    # 對話演示
    quick_start.conversation_demo()

    # 多 Agent 演示
    quick_start.multiple_agents_demo()

    # 生命週期演示
    demonstrate_agent_lifecycle()

    # 持久化演示
    demonstrate_persistence()

    # 高級配置演示
    advanced_configuration_demo()

    print("\n" + "=" * 70)
    print("教程完成！")
    print("=" * 70)
    print("\n下一步:")
    print("  1. 查看 02_記憶管理.py 學習詳細的記憶管理")
    print("  2. 查看 03_對話持久化.py 學習如何保存對話")
    print("  3. 查看 04_工具整合.py 學習如何添加自定義功能")
    print("\n訪問 https://docs.letta.com/ 獲取更多信息")
    print("=" * 70)


if __name__ == "__main__":
    main()

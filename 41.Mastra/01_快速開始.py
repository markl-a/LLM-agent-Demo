"""
Mastra 快速開始示例

本示例展示如何使用 Python 與 Mastra API 進行基本交互。
Mastra 是 TypeScript-first 框架，Python 通過 HTTP API 調用。

功能：
1. 連接 Mastra API
2. 創建基本 Agent
3. 執行簡單對話
4. 獲取響應結果
"""

import os
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import json

# 載入環境變量
load_dotenv()


class MastraClient:
    """Mastra API 客戶端"""

    def __init__(self, api_url: Optional[str] = None, api_key: Optional[str] = None):
        """
        初始化 Mastra 客戶端

        Args:
            api_url: Mastra API URL（默認從環境變量讀取）
            api_key: API 密鑰（默認從環境變量讀取）
        """
        self.api_url = api_url or os.getenv('MASTRA_API_URL', 'http://localhost:3000')
        self.api_key = api_key or os.getenv('MASTRA_API_KEY')

        self.headers = {
            'Content-Type': 'application/json',
        }

        if self.api_key:
            self.headers['Authorization'] = f'Bearer {self.api_key}'

    def health_check(self) -> Dict[str, Any]:
        """
        檢查 Mastra 服務健康狀態

        Returns:
            健康檢查結果
        """
        try:
            response = requests.get(
                f'{self.api_url}/api/health',
                headers=self.headers,
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'status': 'error', 'message': str(e)}

    def create_agent(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        創建新的 Agent

        Args:
            config: Agent 配置
                - name: Agent 名稱
                - description: Agent 描述
                - model: 使用的模型
                - instructions: 系統指令
                - tools: 可用工具列表

        Returns:
            創建結果
        """
        try:
            response = requests.post(
                f'{self.api_url}/api/agents',
                headers=self.headers,
                json=config,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}

    def chat(self, agent_name: str, message: str,
             session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        與 Agent 進行對話

        Args:
            agent_name: Agent 名稱
            message: 用戶消息
            session_id: 會話 ID（可選，用於保持對話上下文）

        Returns:
            Agent 響應
        """
        payload = {
            'message': message,
        }

        if session_id:
            payload['sessionId'] = session_id

        try:
            response = requests.post(
                f'{self.api_url}/api/agents/{agent_name}/chat',
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}

    def get_agent(self, agent_name: str) -> Dict[str, Any]:
        """
        獲取 Agent 信息

        Args:
            agent_name: Agent 名稱

        Returns:
            Agent 詳細信息
        """
        try:
            response = requests.get(
                f'{self.api_url}/api/agents/{agent_name}',
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}

    def list_agents(self) -> Dict[str, Any]:
        """
        列出所有 Agents

        Returns:
            Agents 列表
        """
        try:
            response = requests.get(
                f'{self.api_url}/api/agents',
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}


def example_1_basic_connection():
    """示例 1：基本連接和健康檢查"""
    print("=" * 60)
    print("示例 1：基本連接和健康檢查")
    print("=" * 60)

    # 創建客戶端
    client = MastraClient()

    # 健康檢查
    health = client.health_check()
    print(f"\n健康檢查結果: {json.dumps(health, indent=2, ensure_ascii=False)}")


def example_2_create_simple_agent():
    """示例 2：創建簡單的 Agent"""
    print("\n" + "=" * 60)
    print("示例 2：創建簡單的 Agent")
    print("=" * 60)

    client = MastraClient()

    # Agent 配置
    agent_config = {
        'name': 'hello-assistant',
        'description': '一個友好的問候助手',
        'model': {
            'provider': 'openai',
            'name': 'gpt-4',
        },
        'instructions': '''你是一個友好且有禮貌的助手。
        你的任務是：
        1. 熱情地問候用戶
        2. 提供有幫助的信息
        3. 保持積極正面的態度
        ''',
        'tools': []
    }

    # 創建 Agent
    result = client.create_agent(agent_config)
    print(f"\nAgent 創建結果: {json.dumps(result, indent=2, ensure_ascii=False)}")


def example_3_simple_chat():
    """示例 3：簡單對話"""
    print("\n" + "=" * 60)
    print("示例 3：簡單對話")
    print("=" * 60)

    client = MastraClient()

    # 與 Agent 對話
    messages = [
        "你好！",
        "你能做什麼？",
        "告訴我一個有趣的事實",
    ]

    for msg in messages:
        print(f"\n用戶: {msg}")
        response = client.chat('hello-assistant', msg)

        if 'error' in response:
            print(f"錯誤: {response['error']}")
        else:
            print(f"助手: {response.get('message', response)}")


def example_4_contextual_conversation():
    """示例 4：保持上下文的對話"""
    print("\n" + "=" * 60)
    print("示例 4：保持上下文的對話")
    print("=" * 60)

    client = MastraClient()

    # 使用相同的 session_id 保持上下文
    session_id = "session-" + os.urandom(8).hex()

    conversation = [
        "我叫小明",
        "我喜歡編程",
        "你還記得我的名字嗎？",
        "我喜歡什麼？",
    ]

    for msg in conversation:
        print(f"\n用戶: {msg}")
        response = client.chat('hello-assistant', msg, session_id=session_id)

        if 'error' in response:
            print(f"錯誤: {response['error']}")
        else:
            print(f"助手: {response.get('message', response)}")


def example_5_list_and_get_agents():
    """示例 5：列出和獲取 Agents"""
    print("\n" + "=" * 60)
    print("示例 5：列出和獲取 Agents")
    print("=" * 60)

    client = MastraClient()

    # 列出所有 Agents
    print("\n所有 Agents:")
    agents = client.list_agents()
    print(json.dumps(agents, indent=2, ensure_ascii=False))

    # 獲取特定 Agent
    print("\n獲取 hello-assistant Agent:")
    agent = client.get_agent('hello-assistant')
    print(json.dumps(agent, indent=2, ensure_ascii=False))


def example_6_environment_setup():
    """示例 6：環境設置說明"""
    print("\n" + "=" * 60)
    print("示例 6：環境設置說明")
    print("=" * 60)

    print("""
    要使用 Mastra，需要設置以下環境變量：

    1. 創建 .env 文件：

       MASTRA_API_URL=http://localhost:3000
       MASTRA_API_KEY=your-api-key-here
       OPENAI_API_KEY=your-openai-key

    2. 啟動 Mastra 服務（TypeScript）：

       # 安裝依賴
       npm install @mastra/core

       # 創建 server.ts
       # （參見 Mastra 官方文檔）

       # 啟動服務
       npm run dev

    3. 運行 Python 客戶端：

       python 01_快速開始.py

    注意：
    - Mastra 是 TypeScript 框架，需要先啟動 TypeScript 服務
    - Python 客戶端通過 HTTP API 與 Mastra 交互
    - 確保 API URL 和密鑰配置正確
    """)


def main():
    """主函數 - 運行所有示例"""
    print("\n🚀 Mastra 快速開始示例\n")

    # 檢查環境變量
    if not os.getenv('MASTRA_API_URL'):
        print("⚠️  警告: MASTRA_API_URL 未設置")
        print("請設置環境變量或啟動 Mastra 服務")
        example_6_environment_setup()
        return

    try:
        # 運行示例
        example_1_basic_connection()
        example_2_create_simple_agent()
        example_3_simple_chat()
        example_4_contextual_conversation()
        example_5_list_and_get_agents()

        print("\n" + "=" * 60)
        print("✅ 所有示例運行完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        print("\n提示: 請確保 Mastra 服務正在運行")
        example_6_environment_setup()


if __name__ == "__main__":
    main()

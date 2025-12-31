"""
Julep 快速開始示例

這個模塊展示了如何使用 Julep 平台進行基礎設置和 Agent 創建。
包括客戶端初始化、Agent 創建、用戶管理和基本的對話功能。

主要功能：
1. Julep 客戶端初始化
2. 創建和配置 AI Agent
3. 用戶創建和管理
4. 會話創建
5. 基本的聊天對話
6. Agent 配置和自定義

作者：Julep 示例
日期：2025-12-31
"""

import os
import sys
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import time


class JulepConfig:
    """Julep 配置管理類

    管理 Julep 平台的各種配置參數，包括 API 金鑰、模型選擇、
    超時設置等。支持從環境變量或配置文件加載配置。
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3
    ):
        """初始化配置

        Args:
            api_key: Julep API 金鑰，如果未提供則從環境變量讀取
            base_url: API 基礎 URL，默認使用官方 API
            timeout: 請求超時時間（秒）
            max_retries: 最大重試次數
        """
        self.api_key = api_key or os.getenv("JULEP_API_KEY")
        self.base_url = base_url or "https://api.julep.ai/v1"
        self.timeout = timeout
        self.max_retries = max_retries

        # 驗證必需的配置
        if not self.api_key:
            raise ValueError("JULEP_API_KEY 未設置，請設置環境變量或傳入參數")

    def to_dict(self) -> Dict[str, Any]:
        """將配置轉換為字典格式"""
        return {
            "api_key": "***" if self.api_key else None,  # 隱藏 API 金鑰
            "base_url": self.base_url,
            "timeout": self.timeout,
            "max_retries": self.max_retries
        }

    def __repr__(self) -> str:
        """字符串表示"""
        return f"JulepConfig({self.to_dict()})"


class JulepClient:
    """Julep 客戶端類

    這是與 Julep API 交互的主要接口。提供了創建 Agent、用戶、
    會話等功能的方法。
    """

    def __init__(self, config: Optional[JulepConfig] = None):
        """初始化客戶端

        Args:
            config: JulepConfig 對象，如果未提供則使用默認配置
        """
        self.config = config or JulepConfig()
        self.agents = AgentManager(self)
        self.users = UserManager(self)
        self.sessions = SessionManager(self)

        print(f"[INFO] Julep 客戶端初始化成功")
        print(f"[INFO] 基礎 URL: {self.config.base_url}")

    def health_check(self) -> bool:
        """檢查 API 健康狀態

        Returns:
            bool: API 是否可用
        """
        try:
            print("[INFO] 執行健康檢查...")
            # 模擬 API 健康檢查
            time.sleep(0.1)
            print("[SUCCESS] API 健康檢查通過")
            return True
        except Exception as e:
            print(f"[ERROR] 健康檢查失敗: {e}")
            return False


class Agent:
    """Agent 類

    表示一個 AI Agent，包含其配置、模型、工具等信息。
    """

    def __init__(
        self,
        id: str,
        name: str,
        about: str,
        model: str,
        instructions: Optional[List[str]] = None,
        tools: Optional[List[Dict]] = None,
        metadata: Optional[Dict] = None
    ):
        """初始化 Agent

        Args:
            id: Agent 唯一標識符
            name: Agent 名稱
            about: Agent 描述
            model: 使用的模型名稱
            instructions: Agent 指令列表
            tools: Agent 可用的工具列表
            metadata: 元數據
        """
        self.id = id
        self.name = name
        self.about = about
        self.model = model
        self.instructions = instructions or []
        self.tools = tools or []
        self.metadata = metadata or {}
        self.created_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            "id": self.id,
            "name": self.name,
            "about": self.about,
            "model": self.model,
            "instructions": self.instructions,
            "tools": self.tools,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }

    def __repr__(self) -> str:
        return f"Agent(id='{self.id}', name='{self.name}', model='{self.model}')"


class AgentManager:
    """Agent 管理器

    負責創建、更新、刪除和查詢 Agent。
    """

    def __init__(self, client: JulepClient):
        """初始化管理器"""
        self.client = client
        self._agents: Dict[str, Agent] = {}

    def create(
        self,
        name: str,
        about: str = "",
        model: str = "gpt-4",
        instructions: Optional[List[str]] = None,
        tools: Optional[List[Dict]] = None,
        metadata: Optional[Dict] = None
    ) -> Agent:
        """創建新 Agent

        Args:
            name: Agent 名稱
            about: Agent 描述
            model: 模型名稱（默認 gpt-4）
            instructions: 指令列表
            tools: 工具列表
            metadata: 元數據

        Returns:
            創建的 Agent 對象
        """
        # 生成唯一 ID
        agent_id = f"agent_{len(self._agents) + 1}_{int(time.time())}"

        # 創建 Agent 對象
        agent = Agent(
            id=agent_id,
            name=name,
            about=about,
            model=model,
            instructions=instructions,
            tools=tools,
            metadata=metadata
        )

        # 存儲 Agent
        self._agents[agent_id] = agent

        print(f"[SUCCESS] 創建 Agent: {agent.name} (ID: {agent.id})")
        return agent

    def get(self, agent_id: str) -> Optional[Agent]:
        """獲取 Agent

        Args:
            agent_id: Agent ID

        Returns:
            Agent 對象或 None
        """
        return self._agents.get(agent_id)

    def list(self) -> List[Agent]:
        """列出所有 Agent"""
        return list(self._agents.values())

    def delete(self, agent_id: str) -> bool:
        """刪除 Agent

        Args:
            agent_id: Agent ID

        Returns:
            是否成功刪除
        """
        if agent_id in self._agents:
            del self._agents[agent_id]
            print(f"[SUCCESS] 刪除 Agent: {agent_id}")
            return True
        return False


class User:
    """用戶類"""

    def __init__(self, id: str, name: str, about: str = "", metadata: Optional[Dict] = None):
        self.id = id
        self.name = name
        self.about = about
        self.metadata = metadata or {}
        self.created_at = datetime.now()

    def __repr__(self) -> str:
        return f"User(id='{self.id}', name='{self.name}')"


class UserManager:
    """用戶管理器"""

    def __init__(self, client: JulepClient):
        self.client = client
        self._users: Dict[str, User] = {}

    def create(self, name: str, about: str = "", metadata: Optional[Dict] = None) -> User:
        """創建新用戶"""
        user_id = f"user_{len(self._users) + 1}_{int(time.time())}"
        user = User(id=user_id, name=name, about=about, metadata=metadata)
        self._users[user_id] = user
        print(f"[SUCCESS] 創建用戶: {user.name} (ID: {user.id})")
        return user

    def get(self, user_id: str) -> Optional[User]:
        """獲取用戶"""
        return self._users.get(user_id)


class Session:
    """會話類"""

    def __init__(self, id: str, agent_id: str, user_id: str):
        self.id = id
        self.agent_id = agent_id
        self.user_id = user_id
        self.messages: List[Dict] = []
        self.created_at = datetime.now()

    def __repr__(self) -> str:
        return f"Session(id='{self.id}', messages={len(self.messages)})"


class SessionManager:
    """會話管理器"""

    def __init__(self, client: JulepClient):
        self.client = client
        self._sessions: Dict[str, Session] = {}

    def create(self, agent_id: str, user_id: Optional[str] = None) -> Session:
        """創建新會話"""
        session_id = f"session_{len(self._sessions) + 1}_{int(time.time())}"
        session = Session(id=session_id, agent_id=agent_id, user_id=user_id or "")
        self._sessions[session_id] = session
        print(f"[SUCCESS] 創建會話: {session.id}")
        return session

    def chat(
        self,
        session_id: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """發送聊天消息

        Args:
            session_id: 會話 ID
            messages: 消息列表
            temperature: 溫度參數
            max_tokens: 最大 token 數

        Returns:
            響應字典
        """
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError(f"會話不存在: {session_id}")

        # 添加消息到會話歷史
        session.messages.extend(messages)

        # 模擬 AI 響應
        response_content = f"這是對 '{messages[-1]['content']}' 的模擬回復"

        response = {
            "id": f"msg_{int(time.time())}",
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": response_content
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150
            }
        }

        # 保存助手回復
        session.messages.append({
            "role": "assistant",
            "content": response_content
        })

        return response


def basic_agent_creation():
    """基礎 Agent 創建示例"""
    print("\n" + "="*60)
    print("示例 1: 基礎 Agent 創建")
    print("="*60)

    # 初始化客戶端
    client = JulepClient()

    # 創建簡單的 Agent
    agent = client.agents.create(
        name="通用助手",
        about="我是一個通用 AI 助手，可以回答各種問題",
        model="gpt-4"
    )

    print(f"\nAgent 詳情:")
    print(f"  ID: {agent.id}")
    print(f"  名稱: {agent.name}")
    print(f"  模型: {agent.model}")
    print(f"  創建時間: {agent.created_at}")


def agent_with_instructions():
    """帶指令的 Agent 創建示例"""
    print("\n" + "="*60)
    print("示例 2: 帶指令的 Agent 創建")
    print("="*60)

    client = JulepClient()

    # 創建帶有詳細指令的 Agent
    agent = client.agents.create(
        name="專業翻譯助手",
        about="專門提供中英文翻譯服務",
        model="gpt-4",
        instructions=[
            "你是一個專業的翻譯助手",
            "請提供準確、流暢的翻譯",
            "保持原文的語氣和風格",
            "如果遇到專業術語，請提供解釋"
        ],
        metadata={
            "category": "translation",
            "languages": ["zh", "en"]
        }
    )

    print(f"\nAgent 配置:")
    for key, value in agent.to_dict().items():
        print(f"  {key}: {value}")


def simple_conversation():
    """簡單對話示例"""
    print("\n" + "="*60)
    print("示例 3: 簡單對話")
    print("="*60)

    client = JulepClient()

    # 創建 Agent 和用戶
    agent = client.agents.create(
        name="對話助手",
        about="友好的對話助手"
    )

    user = client.users.create(
        name="張三",
        about="測試用戶"
    )

    # 創建會話
    session = client.sessions.create(
        agent_id=agent.id,
        user_id=user.id
    )

    # 發送消息
    messages_to_send = [
        "你好，請介紹一下你自己",
        "你能幫我做什麼？",
        "謝謝你的幫助"
    ]

    for msg in messages_to_send:
        print(f"\n用戶: {msg}")

        response = client.sessions.chat(
            session_id=session.id,
            messages=[{"role": "user", "content": msg}]
        )

        assistant_msg = response["choices"][0]["message"]["content"]
        print(f"助手: {assistant_msg}")

        time.sleep(0.5)  # 模擬對話間隔


def main():
    """主函數：運行所有示例"""
    print("="*60)
    print("Julep 快速開始示例")
    print("="*60)

    try:
        # 運行各個示例
        basic_agent_creation()
        agent_with_instructions()
        simple_conversation()

        print("\n" + "="*60)
        print("所有示例執行完成！")
        print("="*60)

    except Exception as e:
        print(f"\n[ERROR] 執行過程中出現錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

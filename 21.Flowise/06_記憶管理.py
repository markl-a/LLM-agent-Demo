"""
Flowise 記憶管理範例
==================

本範例展示如何在 Flowise 中管理對話記憶。

記憶類型：
1. Buffer Memory
2. Buffer Window Memory
3. Summary Memory
4. Vector Store Memory
5. Redis Memory

安裝依賴：
pip install requests redis
"""

import os
import json
import requests
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

# ============================================================
# 配置
# ============================================================

FLOWISE_API_URL = os.getenv("FLOWISE_API_URL", "http://localhost:3000")
FLOWISE_API_KEY = os.getenv("FLOWISE_API_KEY", "")


# ============================================================
# 記憶類型配置
# ============================================================

BUFFER_MEMORY_CONFIG = '''
{
    "nodes": [
        {
            "id": "bufferMemory_0",
            "type": "BufferMemory",
            "data": {
                "label": "Buffer Memory",
                "name": "bufferMemory",
                "inputs": {
                    "memoryKey": "chat_history",
                    "inputKey": "input",
                    "outputKey": "output",
                    "sessionId": ""
                }
            }
        }
    ]
}
'''

BUFFER_WINDOW_MEMORY_CONFIG = '''
{
    "nodes": [
        {
            "id": "bufferWindowMemory_0",
            "type": "BufferWindowMemory",
            "data": {
                "label": "Buffer Window Memory",
                "name": "bufferWindowMemory",
                "inputs": {
                    "memoryKey": "chat_history",
                    "k": 5,
                    "sessionId": ""
                }
            }
        }
    ]
}
'''

SUMMARY_MEMORY_CONFIG = '''
{
    "nodes": [
        {
            "id": "chatOpenAI_0",
            "type": "ChatOpenAI",
            "data": {
                "label": "ChatOpenAI (Summarizer)",
                "inputs": {
                    "modelName": "gpt-3.5-turbo",
                    "temperature": 0
                }
            }
        },
        {
            "id": "conversationSummaryMemory_0",
            "type": "ConversationSummaryMemory",
            "data": {
                "label": "Conversation Summary Memory",
                "name": "conversationSummaryMemory",
                "inputs": {
                    "memoryKey": "chat_history",
                    "sessionId": ""
                }
            }
        }
    ],
    "edges": [
        {
            "source": "chatOpenAI_0",
            "target": "conversationSummaryMemory_0"
        }
    ]
}
'''

VECTOR_STORE_MEMORY_CONFIG = '''
{
    "nodes": [
        {
            "id": "openAIEmbeddings_0",
            "type": "OpenAIEmbeddings"
        },
        {
            "id": "pinecone_0",
            "type": "Pinecone",
            "data": {
                "inputs": {
                    "index": "conversation-memory"
                }
            }
        },
        {
            "id": "vectorStoreRetrieverMemory_0",
            "type": "VectorStoreRetrieverMemory",
            "data": {
                "label": "Vector Store Memory",
                "inputs": {
                    "memoryKey": "chat_history",
                    "k": 5,
                    "sessionId": ""
                }
            }
        }
    ],
    "edges": [
        {
            "source": "openAIEmbeddings_0",
            "target": "pinecone_0"
        },
        {
            "source": "pinecone_0",
            "target": "vectorStoreRetrieverMemory_0"
        }
    ]
}
'''

REDIS_MEMORY_CONFIG = '''
{
    "nodes": [
        {
            "id": "redisChatMemory_0",
            "type": "RedisChatMemory",
            "data": {
                "label": "Redis Chat Memory",
                "name": "redisChatMemory",
                "inputs": {
                    "baseURL": "redis://localhost:6379",
                    "sessionId": "",
                    "sessionTTL": 3600
                }
            }
        }
    ]
}
'''


# ============================================================
# 記憶管理類
# ============================================================

@dataclass
class Message:
    """消息"""
    role: str  # user, assistant
    content: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Conversation:
    """對話"""
    session_id: str
    messages: List[Message] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class MemoryManager:
    """
    記憶管理器

    管理對話記憶和歷史
    """

    def __init__(self, api_url: str, api_key: str = ""):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json"
        }
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

    def get_chat_history(
        self,
        chatflow_id: str,
        session_id: str
    ) -> List[Dict[str, Any]]:
        """
        獲取聊天歷史

        Args:
            chatflow_id: Chatflow ID
            session_id: 會話 ID

        Returns:
            消息歷史列表
        """
        url = f"{self.api_url}/api/v1/chatmessage/{chatflow_id}"

        params = {
            "sessionId": session_id,
            "sort": "asc"
        }

        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return []

    def delete_chat_history(
        self,
        chatflow_id: str,
        session_id: str
    ) -> bool:
        """
        刪除聊天歷史

        Args:
            chatflow_id: Chatflow ID
            session_id: 會話 ID

        Returns:
            是否成功
        """
        url = f"{self.api_url}/api/v1/chatmessage/{chatflow_id}"

        params = {"sessionId": session_id}

        try:
            response = requests.delete(url, headers=self.headers, params=params)
            return response.status_code == 200
        except Exception:
            return False

    def clear_all_history(self, chatflow_id: str) -> bool:
        """
        清除所有歷史

        Args:
            chatflow_id: Chatflow ID

        Returns:
            是否成功
        """
        url = f"{self.api_url}/api/v1/chatmessage/{chatflow_id}"

        try:
            response = requests.delete(url, headers=self.headers)
            return response.status_code == 200
        except Exception:
            return False


# ============================================================
# 本地記憶實現
# ============================================================

class LocalBufferMemory:
    """
    本地緩衝記憶

    在本地存儲對話歷史
    """

    def __init__(self, max_messages: int = 100):
        self.conversations: Dict[str, Conversation] = {}
        self.max_messages = max_messages

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str
    ):
        """添加消息"""
        if session_id not in self.conversations:
            self.conversations[session_id] = Conversation(session_id=session_id)

        conv = self.conversations[session_id]
        conv.messages.append(Message(role=role, content=content))
        conv.updated_at = datetime.now()

        # 限制消息數量
        if len(conv.messages) > self.max_messages:
            conv.messages = conv.messages[-self.max_messages:]

    def get_history(
        self,
        session_id: str,
        limit: int = 10
    ) -> List[Dict[str, str]]:
        """獲取歷史"""
        if session_id not in self.conversations:
            return []

        messages = self.conversations[session_id].messages[-limit:]
        return [
            {"role": m.role, "content": m.content}
            for m in messages
        ]

    def clear(self, session_id: str):
        """清除歷史"""
        if session_id in self.conversations:
            del self.conversations[session_id]


class LocalWindowMemory(LocalBufferMemory):
    """
    本地窗口記憶

    只保留最近 k 輪對話
    """

    def __init__(self, k: int = 5):
        super().__init__(max_messages=k * 2)
        self.k = k


class LocalSummaryMemory:
    """
    本地摘要記憶

    將歷史對話壓縮為摘要
    """

    def __init__(self, summarize_func=None):
        self.summaries: Dict[str, str] = {}
        self.recent_messages: Dict[str, List[Message]] = {}
        self.summarize_func = summarize_func or self._default_summarize

    def _default_summarize(self, messages: List[Dict[str, str]]) -> str:
        """默認摘要函數"""
        if not messages:
            return ""

        topics = []
        for m in messages[-5:]:
            if m['role'] == 'user':
                topics.append(m['content'][:50])

        return f"討論了：{', '.join(topics)}"

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str
    ):
        """添加消息"""
        if session_id not in self.recent_messages:
            self.recent_messages[session_id] = []
            self.summaries[session_id] = ""

        self.recent_messages[session_id].append(
            Message(role=role, content=content)
        )

        # 每 10 條消息生成一次摘要
        if len(self.recent_messages[session_id]) >= 10:
            messages = [
                {"role": m.role, "content": m.content}
                for m in self.recent_messages[session_id]
            ]
            new_summary = self.summarize_func(messages)
            self.summaries[session_id] += f" {new_summary}"
            self.recent_messages[session_id] = []

    def get_context(self, session_id: str) -> str:
        """獲取上下文"""
        summary = self.summaries.get(session_id, "")
        recent = self.recent_messages.get(session_id, [])

        context_parts = []
        if summary:
            context_parts.append(f"之前的對話摘要：{summary}")

        if recent:
            recent_text = "\n".join([
                f"{m.role}: {m.content}"
                for m in recent[-5:]
            ])
            context_parts.append(f"最近的對話：\n{recent_text}")

        return "\n\n".join(context_parts)


# ============================================================
# 使用範例
# ============================================================

def example_buffer_memory():
    """
    範例 1: Buffer Memory

    展示基本的緩衝記憶配置
    """
    print("=" * 50)
    print("範例 1: Buffer Memory")
    print("=" * 50)

    print("Buffer Memory 配置:")
    print(BUFFER_MEMORY_CONFIG)

    print("\n特點:")
    print("  - 存儲所有對話歷史")
    print("  - 簡單易用")
    print("  - 適合短對話")


def example_window_memory():
    """
    範例 2: Buffer Window Memory

    展示窗口記憶配置
    """
    print("\n" + "=" * 50)
    print("範例 2: Buffer Window Memory")
    print("=" * 50)

    print("Buffer Window Memory 配置:")
    print(BUFFER_WINDOW_MEMORY_CONFIG)

    print("\n特點:")
    print("  - 只保留最近 k 輪對話")
    print("  - 控制上下文長度")
    print("  - 適合長對話")


def example_summary_memory():
    """
    範例 3: Summary Memory

    展示摘要記憶配置
    """
    print("\n" + "=" * 50)
    print("範例 3: Summary Memory")
    print("=" * 50)

    print("Summary Memory 配置:")
    print(SUMMARY_MEMORY_CONFIG)

    print("\n特點:")
    print("  - 自動生成對話摘要")
    print("  - 保留核心信息")
    print("  - 適合超長對話")


def example_vector_store_memory():
    """
    範例 4: Vector Store Memory

    展示向量存儲記憶配置
    """
    print("\n" + "=" * 50)
    print("範例 4: Vector Store Memory")
    print("=" * 50)

    print("Vector Store Memory 配置:")
    print(VECTOR_STORE_MEMORY_CONFIG)

    print("\n特點:")
    print("  - 基於語義檢索歷史")
    print("  - 找到最相關的對話")
    print("  - 適合知識密集型對話")


def example_redis_memory():
    """
    範例 5: Redis Memory

    展示 Redis 持久化記憶
    """
    print("\n" + "=" * 50)
    print("範例 5: Redis Memory")
    print("=" * 50)

    print("Redis Memory 配置:")
    print(REDIS_MEMORY_CONFIG)

    print("\n特點:")
    print("  - 持久化存儲")
    print("  - 支持 TTL")
    print("  - 適合生產環境")


def example_local_memory():
    """
    範例 6: 本地記憶實現

    展示本地記憶的使用
    """
    print("\n" + "=" * 50)
    print("範例 6: 本地記憶實現")
    print("=" * 50)

    memory = LocalBufferMemory()

    # 模擬對話
    memory.add_message("session1", "user", "你好")
    memory.add_message("session1", "assistant", "你好！有什麼可以幫助你的嗎？")
    memory.add_message("session1", "user", "介紹一下 Python")
    memory.add_message("session1", "assistant", "Python 是一種高級編程語言...")

    # 獲取歷史
    history = memory.get_history("session1")

    print("對話歷史:")
    for msg in history:
        print(f"  [{msg['role']}]: {msg['content'][:50]}...")


def example_memory_api():
    """
    範例 7: 記憶 API

    展示如何通過 API 管理記憶
    """
    print("\n" + "=" * 50)
    print("範例 7: 記憶 API")
    print("=" * 50)

    print("Flowise 記憶 API:")
    print("""
# 獲取聊天歷史
GET /api/v1/chatmessage/{chatflowId}?sessionId={sessionId}

# 刪除特定會話歷史
DELETE /api/v1/chatmessage/{chatflowId}?sessionId={sessionId}

# 刪除所有歷史
DELETE /api/v1/chatmessage/{chatflowId}

# 在聊天時傳遞 sessionId
POST /api/v1/prediction/{chatflowId}
{
    "question": "你好",
    "overrideConfig": {
        "sessionId": "user-123"
    }
}
""")


# ============================================================
# 主程序
# ============================================================

if __name__ == "__main__":
    print("Flowise 記憶管理範例")
    print()

    example_buffer_memory()
    example_window_memory()
    example_summary_memory()
    example_vector_store_memory()
    example_redis_memory()
    example_local_memory()
    example_memory_api()

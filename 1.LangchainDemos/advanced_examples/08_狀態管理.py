"""
LangChain 狀態管理範例
=====================

本範例展示如何在 LangChain 中管理對話和應用狀態。

狀態管理類型：
1. 對話記憶
2. 會話狀態
3. 持久化狀態
4. 分布式狀態

安裝依賴：
pip install langchain langchain-openai redis
"""

from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.messages import HumanMessage, AIMessage
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import json
import time
from datetime import datetime

# ============================================================
# 1. 基礎對話記憶
# ============================================================

BASIC_MEMORY_EXAMPLE = '''
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain

llm = ChatOpenAI()

# 創建記憶
memory = ConversationBufferMemory()

# 創建對話鏈
conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)

# 對話
response1 = conversation.predict(input="我叫小明")
response2 = conversation.predict(input="你還記得我的名字嗎？")

# 查看記憶
print(memory.buffer)
'''


# ============================================================
# 2. 高級記憶類型
# ============================================================

MEMORY_TYPES_EXAMPLE = '''
from langchain.memory import (
    ConversationBufferMemory,
    ConversationBufferWindowMemory,
    ConversationSummaryMemory,
    ConversationSummaryBufferMemory,
    ConversationTokenBufferMemory,
    VectorStoreRetrieverMemory
)

# 1. 緩衝記憶 - 保存所有消息
buffer_memory = ConversationBufferMemory()

# 2. 窗口記憶 - 只保存最近 k 輪
window_memory = ConversationBufferWindowMemory(k=5)

# 3. 摘要記憶 - 自動總結舊對話
summary_memory = ConversationSummaryMemory(llm=llm)

# 4. 摘要緩衝記憶 - 混合模式
summary_buffer = ConversationSummaryBufferMemory(
    llm=llm,
    max_token_limit=1000
)

# 5. Token 緩衝記憶 - 基於 token 限制
token_memory = ConversationTokenBufferMemory(
    llm=llm,
    max_token_limit=500
)
'''


# ============================================================
# 3. 自定義狀態管理器
# ============================================================

@dataclass
class ConversationState:
    """對話狀態"""
    session_id: str
    messages: List[Dict] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)


class StateManager:
    """狀態管理器"""

    def __init__(self):
        self.states: Dict[str, ConversationState] = {}

    def create_session(self, session_id: str) -> ConversationState:
        """創建會話"""
        state = ConversationState(session_id=session_id)
        self.states[session_id] = state
        return state

    def get_state(self, session_id: str) -> Optional[ConversationState]:
        """獲取狀態"""
        return self.states.get(session_id)

    def add_message(self, session_id: str, role: str, content: str):
        """添加消息"""
        state = self.get_state(session_id)
        if state:
            state.messages.append({
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat()
            })
            state.last_activity = datetime.now()

    def set_context(self, session_id: str, key: str, value: Any):
        """設置上下文"""
        state = self.get_state(session_id)
        if state:
            state.context[key] = value

    def get_context(self, session_id: str, key: str) -> Any:
        """獲取上下文"""
        state = self.get_state(session_id)
        return state.context.get(key) if state else None

    def get_history(self, session_id: str, limit: int = None) -> List[Dict]:
        """獲取歷史"""
        state = self.get_state(session_id)
        if not state:
            return []

        messages = state.messages
        if limit:
            messages = messages[-limit:]
        return messages

    def clear_session(self, session_id: str):
        """清除會話"""
        if session_id in self.states:
            del self.states[session_id]


STATE_MANAGER_EXAMPLE = '''
# 狀態管理器使用

manager = StateManager()

# 創建會話
session = manager.create_session("user-123")

# 添加消息
manager.add_message("user-123", "human", "你好！")
manager.add_message("user-123", "ai", "你好！有什麼可以幫助你的？")

# 設置上下文
manager.set_context("user-123", "user_name", "小明")
manager.set_context("user-123", "preferences", {"language": "zh-TW"})

# 獲取歷史
history = manager.get_history("user-123", limit=10)
'''


# ============================================================
# 4. 持久化狀態
# ============================================================

class PersistentStateManager:
    """持久化狀態管理器"""

    def __init__(self, storage_path: str = "state_storage.json"):
        self.storage_path = storage_path
        self.states: Dict[str, Dict] = {}
        self._load()

    def _load(self):
        """從文件加載"""
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                self.states = json.load(f)
        except FileNotFoundError:
            self.states = {}

    def _save(self):
        """保存到文件"""
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(self.states, f, ensure_ascii=False, indent=2, default=str)

    def set(self, session_id: str, key: str, value: Any):
        """設置值"""
        if session_id not in self.states:
            self.states[session_id] = {}
        self.states[session_id][key] = value
        self._save()

    def get(self, session_id: str, key: str, default: Any = None) -> Any:
        """獲取值"""
        return self.states.get(session_id, {}).get(key, default)

    def delete(self, session_id: str, key: str = None):
        """刪除值或會話"""
        if session_id in self.states:
            if key:
                self.states[session_id].pop(key, None)
            else:
                del self.states[session_id]
            self._save()


PERSISTENT_EXAMPLE = '''
# 持久化狀態

manager = PersistentStateManager("my_state.json")

# 設置
manager.set("session-1", "messages", [
    {"role": "human", "content": "Hello"},
    {"role": "ai", "content": "Hi there!"}
])

# 獲取（即使重啟後也能恢復）
messages = manager.get("session-1", "messages", [])
'''


# ============================================================
# 5. Redis 分布式狀態
# ============================================================

REDIS_STATE_EXAMPLE = '''
import redis
import json

class RedisStateManager:
    """Redis 分布式狀態管理器"""

    def __init__(self, host="localhost", port=6379, db=0):
        self.redis = redis.Redis(host=host, port=port, db=db)
        self.prefix = "langchain:state:"

    def _key(self, session_id: str) -> str:
        return f"{self.prefix}{session_id}"

    def set(self, session_id: str, data: Dict, ttl: int = 3600):
        """設置狀態（帶過期時間）"""
        key = self._key(session_id)
        self.redis.setex(key, ttl, json.dumps(data))

    def get(self, session_id: str) -> Optional[Dict]:
        """獲取狀態"""
        key = self._key(session_id)
        data = self.redis.get(key)
        return json.loads(data) if data else None

    def update(self, session_id: str, updates: Dict):
        """更新狀態"""
        current = self.get(session_id) or {}
        current.update(updates)
        self.set(session_id, current)

    def delete(self, session_id: str):
        """刪除狀態"""
        self.redis.delete(self._key(session_id))

# 使用
manager = RedisStateManager()
manager.set("session-1", {"user": "alice", "messages": []})
state = manager.get("session-1")
'''


# ============================================================
# 6. 帶狀態的對話鏈
# ============================================================

class StatefulConversation:
    """帶狀態的對話"""

    def __init__(self, llm=None):
        self.llm = llm or ChatOpenAI()
        self.state_manager = StateManager()
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一個有幫助的助手。{context}"),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])

    def chat(self, session_id: str, user_input: str) -> str:
        """進行對話"""
        # 確保會話存在
        if not self.state_manager.get_state(session_id):
            self.state_manager.create_session(session_id)

        # 獲取歷史
        history = self.state_manager.get_history(session_id)
        messages = [
            HumanMessage(content=m["content"]) if m["role"] == "human"
            else AIMessage(content=m["content"])
            for m in history
        ]

        # 獲取上下文
        context = self.state_manager.get_context(session_id, "system_context") or ""

        # 調用 LLM
        chain = self.prompt | self.llm
        response = chain.invoke({
            "context": context,
            "history": messages,
            "input": user_input
        })

        # 保存消息
        self.state_manager.add_message(session_id, "human", user_input)
        self.state_manager.add_message(session_id, "ai", response.content)

        return response.content


STATEFUL_CONVERSATION_EXAMPLE = '''
# 帶狀態的對話

conv = StatefulConversation()

# 對話
response1 = conv.chat("session-1", "我叫小明")
response2 = conv.chat("session-1", "你還記得我的名字嗎？")

# 設置上下文
conv.state_manager.set_context("session-1", "system_context", "用戶是一位軟體工程師")
response3 = conv.chat("session-1", "給我一些建議")
'''


# ============================================================
# 7. 狀態快照
# ============================================================

class StateSnapshot:
    """狀態快照"""

    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager
        self.snapshots: Dict[str, List[Dict]] = {}

    def take_snapshot(self, session_id: str) -> str:
        """創建快照"""
        state = self.state_manager.get_state(session_id)
        if not state:
            return None

        snapshot_id = f"{session_id}_{int(time.time())}"
        snapshot = {
            "id": snapshot_id,
            "timestamp": datetime.now().isoformat(),
            "messages": state.messages.copy(),
            "context": state.context.copy()
        }

        if session_id not in self.snapshots:
            self.snapshots[session_id] = []
        self.snapshots[session_id].append(snapshot)

        return snapshot_id

    def restore_snapshot(self, session_id: str, snapshot_id: str) -> bool:
        """恢復快照"""
        snapshots = self.snapshots.get(session_id, [])
        snapshot = next((s for s in snapshots if s["id"] == snapshot_id), None)

        if not snapshot:
            return False

        state = self.state_manager.get_state(session_id)
        if state:
            state.messages = snapshot["messages"].copy()
            state.context = snapshot["context"].copy()
            return True

        return False


# ============================================================
# 使用範例
# ============================================================

def example_basic_memory():
    """範例 1: 基礎記憶"""
    print("=" * 50)
    print("範例 1: 基礎對話記憶")
    print("=" * 50)
    print(BASIC_MEMORY_EXAMPLE)


def example_memory_types():
    """範例 2: 記憶類型"""
    print("\n" + "=" * 50)
    print("範例 2: 高級記憶類型")
    print("=" * 50)
    print(MEMORY_TYPES_EXAMPLE)


def example_state_manager():
    """範例 3: 狀態管理器"""
    print("\n" + "=" * 50)
    print("範例 3: 自定義狀態管理器")
    print("=" * 50)
    print(STATE_MANAGER_EXAMPLE)


def example_persistent():
    """範例 4: 持久化"""
    print("\n" + "=" * 50)
    print("範例 4: 持久化狀態")
    print("=" * 50)
    print(PERSISTENT_EXAMPLE)


def example_redis():
    """範例 5: Redis"""
    print("\n" + "=" * 50)
    print("範例 5: Redis 分布式狀態")
    print("=" * 50)
    print(REDIS_STATE_EXAMPLE)


def example_stateful():
    """範例 6: 帶狀態的對話"""
    print("\n" + "=" * 50)
    print("範例 6: 帶狀態的對話鏈")
    print("=" * 50)
    print(STATEFUL_CONVERSATION_EXAMPLE)


def example_snapshot():
    """範例 7: 狀態快照"""
    print("\n" + "=" * 50)
    print("範例 7: 狀態快照")
    print("=" * 50)

    manager = StateManager()
    manager.create_session("test")
    manager.add_message("test", "human", "Hello")

    snapshot = StateSnapshot(manager)

    # 創建快照
    snapshot_id = snapshot.take_snapshot("test")
    print(f"快照 ID: {snapshot_id}")

    # 添加更多消息
    manager.add_message("test", "ai", "Hi!")

    # 恢復快照
    success = snapshot.restore_snapshot("test", snapshot_id)
    print(f"恢復成功: {success}")


if __name__ == "__main__":
    print("LangChain 狀態管理範例\n")
    example_basic_memory()
    example_memory_types()
    example_state_manager()
    example_persistent()
    example_redis()
    example_stateful()
    example_snapshot()

"""
Atomic Agents 上下文管理
========================

本文件展示如何管理 Agent 的上下文和記憶。
上下文管理對於多輪對話和狀態保持至關重要。

主要內容：
1. 會話上下文
2. 記憶管理
3. 上下文窗口控制
4. 持久化存儲
5. 上下文壓縮
6. 多用戶上下文隔離

作者：Atomic Agents 團隊
日期：2025-12-31
"""

from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field, validator
from datetime import datetime, timedelta
from collections import deque
from enum import Enum
import json
from uuid import UUID, uuid4
from dataclasses import dataclass, field


# ============================================================================
# 第一部分：基礎上下文模型
# ============================================================================

class MessageRole(str, Enum):
    """消息角色"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"


class Message(BaseModel):
    """消息模型"""
    id: UUID = Field(default_factory=uuid4, description="消息 ID")
    role: MessageRole = Field(..., description="角色")
    content: str = Field(..., description="內容")
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tokens: Optional[int] = Field(None, description="Token 數量")

    def estimate_tokens(self) -> int:
        """估算 token 數量（簡化版）"""
        # 實際應用中應使用 tiktoken 等工具
        return len(self.content.split())


class ConversationMetadata(BaseModel):
    """對話元數據"""
    user_id: str = Field(..., description="用戶 ID")
    session_id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    tags: List[str] = Field(default_factory=list)
    custom_data: Dict[str, Any] = Field(default_factory=dict)


class ConversationContext(BaseModel):
    """
    對話上下文

    管理整個對話的歷史和狀態。
    """
    id: UUID = Field(default_factory=uuid4)
    metadata: ConversationMetadata = Field(...)
    messages: List[Message] = Field(default_factory=list)
    max_messages: int = Field(default=100, ge=1)
    max_tokens: int = Field(default=4000, ge=100)

    class Config:
        arbitrary_types_allowed = True

    def add_message(
        self,
        role: MessageRole,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Message:
        """添加消息"""
        message = Message(
            role=role,
            content=content,
            metadata=metadata or {}
        )
        message.tokens = message.estimate_tokens()

        self.messages.append(message)
        self.metadata.updated_at = datetime.now()

        # 自動清理舊消息
        self._trim_messages()

        return message

    def _trim_messages(self) -> None:
        """修剪消息以保持在限制內"""
        # 保留系統消息
        system_messages = [m for m in self.messages if m.role == MessageRole.SYSTEM]
        other_messages = [m for m in self.messages if m.role != MessageRole.SYSTEM]

        # 按消息數量限制
        if len(other_messages) > self.max_messages:
            other_messages = other_messages[-self.max_messages:]

        # 按 token 數量限制
        total_tokens = sum(m.tokens or 0 for m in system_messages)
        kept_messages = []

        for message in reversed(other_messages):
            msg_tokens = message.tokens or 0
            if total_tokens + msg_tokens > self.max_tokens:
                break
            kept_messages.insert(0, message)
            total_tokens += msg_tokens

        self.messages = system_messages + kept_messages

    def get_messages(self, limit: Optional[int] = None) -> List[Message]:
        """獲取消息列表"""
        if limit:
            return self.messages[-limit:]
        return self.messages

    def get_context_string(self, separator: str = "\n") -> str:
        """獲取格式化的上下文字符串"""
        return separator.join(
            f"{msg.role.value}: {msg.content}"
            for msg in self.messages
        )

    def clear(self) -> None:
        """清空對話（保留系統消息）"""
        self.messages = [
            m for m in self.messages
            if m.role == MessageRole.SYSTEM
        ]


# ============================================================================
# 第二部分：記憶管理
# ============================================================================

class MemoryType(str, Enum):
    """記憶類型"""
    SHORT_TERM = "short_term"  # 短期記憶
    LONG_TERM = "long_term"    # 長期記憶
    WORKING = "working"        # 工作記憶


class MemoryEntry(BaseModel):
    """記憶條目"""
    id: UUID = Field(default_factory=uuid4)
    key: str = Field(..., description="記憶鍵")
    value: Any = Field(..., description="記憶值")
    memory_type: MemoryType = Field(..., description="記憶類型")
    created_at: datetime = Field(default_factory=datetime.now)
    accessed_at: datetime = Field(default_factory=datetime.now)
    access_count: int = Field(default=0, description="訪問次數")
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    expires_at: Optional[datetime] = Field(None, description="過期時間")

    class Config:
        arbitrary_types_allowed = True

    def is_expired(self) -> bool:
        """檢查是否過期"""
        if self.expires_at:
            return datetime.now() > self.expires_at
        return False

    def access(self) -> None:
        """記錄訪問"""
        self.accessed_at = datetime.now()
        self.access_count += 1


class MemoryManager:
    """
    記憶管理器

    管理不同類型的記憶。
    """

    def __init__(
        self,
        short_term_capacity: int = 10,
        long_term_capacity: int = 100,
        working_capacity: int = 5
    ):
        self.memories: Dict[str, MemoryEntry] = {}
        self.capacities = {
            MemoryType.SHORT_TERM: short_term_capacity,
            MemoryType.LONG_TERM: long_term_capacity,
            MemoryType.WORKING: working_capacity
        }

    def store(
        self,
        key: str,
        value: Any,
        memory_type: MemoryType = MemoryType.SHORT_TERM,
        importance: float = 0.5,
        ttl: Optional[int] = None
    ) -> MemoryEntry:
        """
        存儲記憶

        Args:
            key: 記憶鍵
            value: 記憶值
            memory_type: 記憶類型
            importance: 重要性 (0-1)
            ttl: 存活時間（秒）

        Returns:
            記憶條目
        """
        # 計算過期時間
        expires_at = None
        if ttl:
            expires_at = datetime.now() + timedelta(seconds=ttl)

        entry = MemoryEntry(
            key=key,
            value=value,
            memory_type=memory_type,
            importance=importance,
            expires_at=expires_at
        )

        self.memories[key] = entry

        # 清理過期記憶
        self._cleanup()

        # 確保不超過容量
        self._enforce_capacity(memory_type)

        return entry

    def retrieve(self, key: str) -> Optional[Any]:
        """
        檢索記憶

        Args:
            key: 記憶鍵

        Returns:
            記憶值，如果不存在或已過期則返回 None
        """
        entry = self.memories.get(key)

        if not entry:
            return None

        if entry.is_expired():
            del self.memories[key]
            return None

        entry.access()
        return entry.value

    def search(
        self,
        memory_type: Optional[MemoryType] = None,
        min_importance: float = 0.0
    ) -> List[MemoryEntry]:
        """
        搜索記憶

        Args:
            memory_type: 記憶類型過濾
            min_importance: 最小重要性

        Returns:
            匹配的記憶列表
        """
        results = []

        for entry in self.memories.values():
            if entry.is_expired():
                continue

            if memory_type and entry.memory_type != memory_type:
                continue

            if entry.importance < min_importance:
                continue

            results.append(entry)

        # 按重要性和訪問次數排序
        results.sort(
            key=lambda e: (e.importance, e.access_count),
            reverse=True
        )

        return results

    def delete(self, key: str) -> bool:
        """刪除記憶"""
        if key in self.memories:
            del self.memories[key]
            return True
        return False

    def clear(self, memory_type: Optional[MemoryType] = None) -> None:
        """清空記憶"""
        if memory_type:
            self.memories = {
                k: v for k, v in self.memories.items()
                if v.memory_type != memory_type
            }
        else:
            self.memories.clear()

    def _cleanup(self) -> None:
        """清理過期記憶"""
        expired_keys = [
            key for key, entry in self.memories.items()
            if entry.is_expired()
        ]
        for key in expired_keys:
            del self.memories[key]

    def _enforce_capacity(self, memory_type: MemoryType) -> None:
        """強制執行容量限制"""
        capacity = self.capacities[memory_type]
        entries = [
            (k, v) for k, v in self.memories.items()
            if v.memory_type == memory_type
        ]

        if len(entries) <= capacity:
            return

        # 按重要性和訪問時間排序
        entries.sort(
            key=lambda x: (x[1].importance, x[1].accessed_at),
            reverse=True
        )

        # 刪除最不重要的條目
        for key, _ in entries[capacity:]:
            del self.memories[key]

    def get_stats(self) -> Dict[str, Any]:
        """獲取統計信息"""
        stats = {
            'total': len(self.memories),
            'by_type': {}
        }

        for memory_type in MemoryType:
            count = sum(
                1 for entry in self.memories.values()
                if entry.memory_type == memory_type
            )
            stats['by_type'][memory_type.value] = count

        return stats


# ============================================================================
# 第三部分：上下文窗口管理
# ============================================================================

class WindowStrategy(str, Enum):
    """窗口策略"""
    SLIDING = "sliding"      # 滑動窗口
    FIXED = "fixed"          # 固定窗口
    IMPORTANCE = "importance" # 基於重要性
    HYBRID = "hybrid"        # 混合策略


class ContextWindow:
    """
    上下文窗口管理器

    控制傳遞給 LLM 的上下文大小。
    """

    def __init__(
        self,
        max_tokens: int = 4000,
        strategy: WindowStrategy = WindowStrategy.SLIDING
    ):
        self.max_tokens = max_tokens
        self.strategy = strategy

    def select_messages(
        self,
        messages: List[Message],
        system_message: Optional[Message] = None
    ) -> List[Message]:
        """
        選擇要包含在上下文中的消息

        Args:
            messages: 所有消息
            system_message: 系統消息（始終包含）

        Returns:
            選中的消息列表
        """
        if self.strategy == WindowStrategy.SLIDING:
            return self._sliding_window(messages, system_message)
        elif self.strategy == WindowStrategy.FIXED:
            return self._fixed_window(messages, system_message)
        elif self.strategy == WindowStrategy.IMPORTANCE:
            return self._importance_window(messages, system_message)
        else:
            return self._hybrid_window(messages, system_message)

    def _sliding_window(
        self,
        messages: List[Message],
        system_message: Optional[Message]
    ) -> List[Message]:
        """滑動窗口策略"""
        selected = []
        total_tokens = 0

        # 首先添加系統消息
        if system_message:
            selected.append(system_message)
            total_tokens += system_message.tokens or 0

        # 從最新的消息開始添加
        for message in reversed(messages):
            msg_tokens = message.tokens or message.estimate_tokens()

            if total_tokens + msg_tokens > self.max_tokens:
                break

            selected.insert(0 if not system_message else 1, message)
            total_tokens += msg_tokens

        return selected

    def _fixed_window(
        self,
        messages: List[Message],
        system_message: Optional[Message]
    ) -> List[Message]:
        """固定窗口策略"""
        # 取最後 N 條消息
        window_size = 10  # 固定大小
        selected = messages[-window_size:]

        if system_message:
            selected.insert(0, system_message)

        return selected

    def _importance_window(
        self,
        messages: List[Message],
        system_message: Optional[Message]
    ) -> List[Message]:
        """基於重要性的窗口策略"""
        # 根據消息的重要性分數選擇
        scored_messages = []

        for msg in messages:
            # 簡單的重要性計算
            importance = msg.metadata.get('importance', 0.5)
            scored_messages.append((importance, msg))

        # 按重要性排序
        scored_messages.sort(key=lambda x: x[0], reverse=True)

        selected = []
        total_tokens = 0

        if system_message:
            selected.append(system_message)
            total_tokens += system_message.tokens or 0

        for _, msg in scored_messages:
            msg_tokens = msg.tokens or msg.estimate_tokens()

            if total_tokens + msg_tokens > self.max_tokens:
                break

            selected.append(msg)
            total_tokens += msg_tokens

        # 按時間順序排序
        selected.sort(key=lambda m: m.timestamp)

        return selected

    def _hybrid_window(
        self,
        messages: List[Message],
        system_message: Optional[Message]
    ) -> List[Message]:
        """混合策略"""
        # 結合滑動窗口和重要性
        recent_messages = messages[-20:]  # 最近的消息
        return self._importance_window(recent_messages, system_message)


# ============================================================================
# 第四部分：上下文壓縮
# ============================================================================

class ContextCompressor:
    """
    上下文壓縮器

    壓縮長對話歷史。
    """

    def __init__(self):
        pass

    def compress_messages(
        self,
        messages: List[Message],
        target_length: int
    ) -> List[Message]:
        """
        壓縮消息列表

        Args:
            messages: 原始消息
            target_length: 目標長度

        Returns:
            壓縮後的消息
        """
        if len(messages) <= target_length:
            return messages

        # 策略1: 保留系統消息和最近的消息
        system_msgs = [m for m in messages if m.role == MessageRole.SYSTEM]
        other_msgs = [m for m in messages if m.role != MessageRole.SYSTEM]

        # 計算可以保留的其他消息數量
        available_slots = target_length - len(system_msgs)

        if available_slots <= 0:
            return system_msgs

        # 保留最近的消息
        recent_msgs = other_msgs[-available_slots:]

        return system_msgs + recent_msgs

    def summarize_context(self, messages: List[Message]) -> str:
        """
        總結上下文

        Args:
            messages: 消息列表

        Returns:
            總結文本
        """
        # 實際應用中會使用 LLM 進行總結
        # 這裡使用簡化版本
        if not messages:
            return ""

        user_messages = [m for m in messages if m.role == MessageRole.USER]
        assistant_messages = [m for m in messages if m.role == MessageRole.ASSISTANT]

        summary = f"對話包含 {len(user_messages)} 個用戶消息和 {len(assistant_messages)} 個助手回復。"

        # 提取關鍵主題（簡化版）
        all_content = " ".join(m.content for m in messages)
        words = all_content.split()
        summary += f" 總共約 {len(words)} 個詞。"

        return summary


# ============================================================================
# 第五部分：持久化存儲
# ============================================================================

class ContextStore:
    """
    上下文存儲

    持久化保存對話上下文。
    """

    def __init__(self, storage_path: str = "./contexts"):
        self.storage_path = storage_path
        self._contexts: Dict[str, ConversationContext] = {}

    def save(self, context: ConversationContext) -> bool:
        """保存上下文"""
        try:
            self._contexts[str(context.id)] = context
            print(f"上下文已保存: {context.id}")
            return True
        except Exception as e:
            print(f"保存失敗: {str(e)}")
            return False

    def load(self, context_id: str) -> Optional[ConversationContext]:
        """加載上下文"""
        return self._contexts.get(context_id)

    def delete(self, context_id: str) -> bool:
        """刪除上下文"""
        if context_id in self._contexts:
            del self._contexts[context_id]
            return True
        return False

    def list_contexts(self, user_id: Optional[str] = None) -> List[ConversationContext]:
        """列出上下文"""
        contexts = list(self._contexts.values())

        if user_id:
            contexts = [
                c for c in contexts
                if c.metadata.user_id == user_id
            ]

        return contexts


# ============================================================================
# 第六部分：使用示例
# ============================================================================

def example_conversation_context():
    """對話上下文示例"""
    print("\n" + "="*60)
    print("示例 1: 對話上下文管理")
    print("="*60)

    # 創建上下文
    metadata = ConversationMetadata(user_id="user_123")
    context = ConversationContext(
        metadata=metadata,
        max_messages=10,
        max_tokens=1000
    )

    # 添加系統消息
    context.add_message(
        MessageRole.SYSTEM,
        "你是一個專業的 AI 助手。"
    )

    # 模擬多輪對話
    conversations = [
        ("你好！", "你好！我能幫你什麼？"),
        ("什麼是 Atomic Agents？", "Atomic Agents 是一個輕量級的 AI Agent 框架..."),
        ("它有什麼特點？", "主要特點包括模組化設計、Schema 驅動..."),
    ]

    for user_msg, assistant_msg in conversations:
        context.add_message(MessageRole.USER, user_msg)
        context.add_message(MessageRole.ASSISTANT, assistant_msg)

    print(f"\n消息數量: {len(context.messages)}")
    print(f"上下文預覽:\n{context.get_context_string()[:200]}...")


def example_memory_manager():
    """記憶管理示例"""
    print("\n" + "="*60)
    print("示例 2: 記憶管理")
    print("="*60)

    manager = MemoryManager()

    # 存儲不同類型的記憶
    manager.store(
        "user_name",
        "張三",
        MemoryType.LONG_TERM,
        importance=0.9
    )

    manager.store(
        "last_query",
        "如何使用 Atomic Agents？",
        MemoryType.SHORT_TERM,
        importance=0.5,
        ttl=300  # 5分鐘過期
    )

    manager.store(
        "current_task",
        "學習上下文管理",
        MemoryType.WORKING,
        importance=0.8
    )

    # 檢索記憶
    user_name = manager.retrieve("user_name")
    print(f"\n用戶名: {user_name}")

    # 搜索記憶
    important_memories = manager.search(min_importance=0.8)
    print(f"\n重要記憶數量: {len(important_memories)}")

    # 統計
    stats = manager.get_stats()
    print(f"\n記憶統計: {stats}")


def example_context_window():
    """上下文窗口示例"""
    print("\n" + "="*60)
    print("示例 3: 上下文窗口管理")
    print("="*60)

    # 創建消息
    messages = []
    for i in range(15):
        msg = Message(
            role=MessageRole.USER if i % 2 == 0 else MessageRole.ASSISTANT,
            content=f"這是第 {i+1} 條消息，包含一些內容。" * 5
        )
        messages.append(msg)

    system_msg = Message(
        role=MessageRole.SYSTEM,
        content="你是一個助手。"
    )

    # 測試不同策略
    strategies = [
        WindowStrategy.SLIDING,
        WindowStrategy.IMPORTANCE,
        WindowStrategy.HYBRID
    ]

    for strategy in strategies:
        window = ContextWindow(max_tokens=200, strategy=strategy)
        selected = window.select_messages(messages, system_msg)
        print(f"\n{strategy.value} 策略選擇了 {len(selected)} 條消息")


def example_context_compression():
    """上下文壓縮示例"""
    print("\n" + "="*60)
    print("示例 4: 上下文壓縮")
    print("="*60)

    # 創建長對話
    messages = []
    for i in range(50):
        msg = Message(
            role=MessageRole.USER if i % 2 == 0 else MessageRole.ASSISTANT,
            content=f"消息 {i+1}"
        )
        messages.append(msg)

    compressor = ContextCompressor()

    # 壓縮到10條消息
    compressed = compressor.compress_messages(messages, target_length=10)
    print(f"\n原始消息數: {len(messages)}")
    print(f"壓縮後消息數: {len(compressed)}")

    # 生成摘要
    summary = compressor.summarize_context(messages)
    print(f"\n對話摘要:\n{summary}")


def example_context_persistence():
    """上下文持久化示例"""
    print("\n" + "="*60)
    print("示例 5: 上下文持久化")
    print("="*60)

    store = ContextStore()

    # 創建並保存上下文
    metadata = ConversationMetadata(user_id="user_456")
    context = ConversationContext(metadata=metadata)
    context.add_message(MessageRole.USER, "測試消息")

    context_id = str(context.id)
    store.save(context)

    # 加載上下文
    loaded = store.load(context_id)
    print(f"\n加載的上下文 ID: {loaded.id}")
    print(f"消息數量: {len(loaded.messages)}")

    # 列出所有上下文
    all_contexts = store.list_contexts()
    print(f"\n存儲的上下文總數: {len(all_contexts)}")


def main():
    """主函數"""
    print("\n" + "="*60)
    print("Atomic Agents 上下文管理")
    print("="*60)

    # 運行示例
    example_conversation_context()
    example_memory_manager()
    example_context_window()
    example_context_compression()
    example_context_persistence()

    print("\n" + "="*60)
    print("所有示例運行完成！")
    print("="*60)


if __name__ == "__main__":
    main()

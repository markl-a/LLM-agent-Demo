"""
Julep 對話管理示例

這個模塊展示了 Julep 平台的狀態化對話管理功能。
包括會話持久化、上下文管理、對話歷史追蹤和多輪對話。

主要功能：
1. 會話創建和管理
2. 對話歷史持久化
3. 上下文窗口管理
4. 多輪對話支持
5. 會話狀態保存和恢復
6. 對話記憶管理

作者：Julep 示例
日期：2025-12-31
"""

import os
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import deque
import pickle


class ConversationMessage:
    """對話消息類

    表示單個對話消息，包含角色、內容、時間戳等信息。
    """

    def __init__(
        self,
        role: str,
        content: str,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict] = None
    ):
        """初始化消息

        Args:
            role: 角色（user, assistant, system）
            content: 消息內容
            timestamp: 時間戳
            metadata: 元數據
        """
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.now()
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationMessage':
        """從字典創建消息"""
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
            metadata=data.get("metadata", {})
        )

    def __repr__(self) -> str:
        return f"Message({self.role}: {self.content[:30]}...)"


class ConversationHistory:
    """對話歷史管理類

    管理完整的對話歷史，支持持久化、查詢和清理。
    """

    def __init__(self, max_messages: int = 1000):
        """初始化對話歷史

        Args:
            max_messages: 最大保存消息數量
        """
        self.messages: deque = deque(maxlen=max_messages)
        self.max_messages = max_messages
        self.created_at = datetime.now()

    def add_message(self, message: ConversationMessage):
        """添加消息到歷史"""
        self.messages.append(message)

    def get_recent_messages(self, count: int = 10) -> List[ConversationMessage]:
        """獲取最近的 N 條消息

        Args:
            count: 消息數量

        Returns:
            消息列表
        """
        return list(self.messages)[-count:]

    def get_messages_by_role(self, role: str) -> List[ConversationMessage]:
        """按角色獲取消息

        Args:
            role: 角色名稱

        Returns:
            該角色的所有消息
        """
        return [msg for msg in self.messages if msg.role == role]

    def get_messages_in_timerange(
        self,
        start: datetime,
        end: Optional[datetime] = None
    ) -> List[ConversationMessage]:
        """獲取時間範圍內的消息

        Args:
            start: 開始時間
            end: 結束時間（默認為當前時間）

        Returns:
            時間範圍內的消息
        """
        end = end or datetime.now()
        return [
            msg for msg in self.messages
            if start <= msg.timestamp <= end
        ]

    def clear(self):
        """清除所有消息"""
        self.messages.clear()

    def get_total_tokens(self) -> int:
        """估算總 token 數量

        簡單估算：每個字符約 0.5 token
        """
        total_chars = sum(len(msg.content) for msg in self.messages)
        return int(total_chars * 0.5)

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            "messages": [msg.to_dict() for msg in self.messages],
            "max_messages": self.max_messages,
            "created_at": self.created_at.isoformat()
        }

    def save_to_file(self, filepath: str):
        """保存到文件

        Args:
            filepath: 文件路徑
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        print(f"[INFO] 對話歷史已保存到: {filepath}")

    @classmethod
    def load_from_file(cls, filepath: str) -> 'ConversationHistory':
        """從文件加載

        Args:
            filepath: 文件路徑

        Returns:
            ConversationHistory 對象
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        history = cls(max_messages=data.get("max_messages", 1000))
        history.created_at = datetime.fromisoformat(data.get("created_at", datetime.now().isoformat()))

        for msg_data in data.get("messages", []):
            history.add_message(ConversationMessage.from_dict(msg_data))

        print(f"[INFO] 從文件加載了 {len(history.messages)} 條消息")
        return history


class ContextWindow:
    """上下文窗口管理類

    管理有限的上下文窗口，自動裁剪和優化消息。
    """

    def __init__(self, max_tokens: int = 4000, reserve_tokens: int = 500):
        """初始化上下文窗口

        Args:
            max_tokens: 最大 token 數
            reserve_tokens: 為響應預留的 token 數
        """
        self.max_tokens = max_tokens
        self.reserve_tokens = reserve_tokens
        self.available_tokens = max_tokens - reserve_tokens

    def fit_messages(
        self,
        messages: List[ConversationMessage],
        system_message: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """調整消息以適應上下文窗口

        Args:
            messages: 消息列表
            system_message: 系統消息

        Returns:
            適配後的消息列表
        """
        result = []
        current_tokens = 0

        # 添加系統消息
        if system_message:
            system_tokens = len(system_message) // 2
            if system_tokens <= self.available_tokens:
                result.append({"role": "system", "content": system_message})
                current_tokens += system_tokens

        # 從最新的消息開始添加
        for msg in reversed(messages):
            msg_tokens = len(msg.content) // 2
            if current_tokens + msg_tokens <= self.available_tokens:
                result.insert(0 if system_message else 0, {
                    "role": msg.role,
                    "content": msg.content
                })
                current_tokens += msg_tokens
            else:
                break

        print(f"[INFO] 上下文窗口: 使用 {current_tokens}/{self.available_tokens} tokens")
        return result

    def summarize_old_messages(
        self,
        messages: List[ConversationMessage],
        summary_length: int = 200
    ) -> str:
        """摘要舊消息

        Args:
            messages: 消息列表
            summary_length: 摘要長度

        Returns:
            摘要文本
        """
        if not messages:
            return ""

        # 簡單摘要：提取關鍵信息
        summary_parts = []
        for msg in messages[:5]:  # 只摘要前5條
            summary_parts.append(f"{msg.role}: {msg.content[:50]}")

        summary = "早期對話摘要：\n" + "\n".join(summary_parts)
        return summary[:summary_length]


class StatefulSession:
    """狀態化會話類

    管理完整的會話狀態，包括對話歷史、上下文窗口、用戶偏好等。
    """

    def __init__(
        self,
        session_id: str,
        agent_id: str,
        user_id: str,
        max_context_tokens: int = 4000
    ):
        """初始化會話

        Args:
            session_id: 會話 ID
            agent_id: Agent ID
            user_id: 用戶 ID
            max_context_tokens: 最大上下文 token 數
        """
        self.session_id = session_id
        self.agent_id = agent_id
        self.user_id = user_id
        self.history = ConversationHistory()
        self.context_window = ContextWindow(max_tokens=max_context_tokens)
        self.state: Dict[str, Any] = {}
        self.created_at = datetime.now()
        self.last_active = datetime.now()

    def add_user_message(self, content: str, metadata: Optional[Dict] = None):
        """添加用戶消息"""
        message = ConversationMessage(
            role="user",
            content=content,
            metadata=metadata
        )
        self.history.add_message(message)
        self.last_active = datetime.now()

    def add_assistant_message(self, content: str, metadata: Optional[Dict] = None):
        """添加助手消息"""
        message = ConversationMessage(
            role="assistant",
            content=content,
            metadata=metadata
        )
        self.history.add_message(message)
        self.last_active = datetime.now()

    def get_context_messages(self) -> List[Dict[str, str]]:
        """獲取適合當前上下文窗口的消息"""
        recent_messages = self.history.get_recent_messages(count=50)
        return self.context_window.fit_messages(recent_messages)

    def set_state(self, key: str, value: Any):
        """設置會話狀態"""
        self.state[key] = value

    def get_state(self, key: str, default: Any = None) -> Any:
        """獲取會話狀態"""
        return self.state.get(key, default)

    def is_active(self, timeout_minutes: int = 30) -> bool:
        """檢查會話是否活躍

        Args:
            timeout_minutes: 超時分鐘數

        Returns:
            是否活躍
        """
        timeout = timedelta(minutes=timeout_minutes)
        return (datetime.now() - self.last_active) < timeout

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "session_id": self.session_id,
            "agent_id": self.agent_id,
            "user_id": self.user_id,
            "history": self.history.to_dict(),
            "state": self.state,
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat()
        }


class ConversationManager:
    """對話管理器

    管理多個會話，提供會話創建、持久化、恢復等功能。
    """

    def __init__(self, storage_dir: str = "./sessions"):
        """初始化管理器

        Args:
            storage_dir: 會話存儲目錄
        """
        self.storage_dir = storage_dir
        self.sessions: Dict[str, StatefulSession] = {}

        # 創建存儲目錄
        os.makedirs(storage_dir, exist_ok=True)

    def create_session(
        self,
        agent_id: str,
        user_id: str,
        session_id: Optional[str] = None
    ) -> StatefulSession:
        """創建新會話

        Args:
            agent_id: Agent ID
            user_id: 用戶 ID
            session_id: 會話 ID（可選）

        Returns:
            創建的會話
        """
        session_id = session_id or f"session_{int(time.time())}"
        session = StatefulSession(
            session_id=session_id,
            agent_id=agent_id,
            user_id=user_id
        )
        self.sessions[session_id] = session
        print(f"[SUCCESS] 創建會話: {session_id}")
        return session

    def get_session(self, session_id: str) -> Optional[StatefulSession]:
        """獲取會話"""
        return self.sessions.get(session_id)

    def save_session(self, session_id: str):
        """保存會話到磁盤

        Args:
            session_id: 會話 ID
        """
        session = self.sessions.get(session_id)
        if not session:
            print(f"[ERROR] 會話不存在: {session_id}")
            return

        filepath = os.path.join(self.storage_dir, f"{session_id}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(session.to_dict(), f, ensure_ascii=False, indent=2)
        print(f"[SUCCESS] 會話已保存: {filepath}")

    def load_session(self, session_id: str) -> Optional[StatefulSession]:
        """從磁盤加載會話

        Args:
            session_id: 會話 ID

        Returns:
            加載的會話
        """
        filepath = os.path.join(self.storage_dir, f"{session_id}.json")
        if not os.path.exists(filepath):
            print(f"[ERROR] 會話文件不存在: {filepath}")
            return None

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 重建會話
        session = StatefulSession(
            session_id=data["session_id"],
            agent_id=data["agent_id"],
            user_id=data["user_id"]
        )
        session.created_at = datetime.fromisoformat(data["created_at"])
        session.last_active = datetime.fromisoformat(data["last_active"])
        session.state = data.get("state", {})

        # 加載歷史
        for msg_data in data["history"]["messages"]:
            msg = ConversationMessage.from_dict(msg_data)
            session.history.add_message(msg)

        self.sessions[session_id] = session
        print(f"[SUCCESS] 會話已加載: {session_id} ({len(session.history.messages)} 條消息)")
        return session

    def cleanup_inactive_sessions(self, timeout_hours: int = 24):
        """清理不活躍的會話

        Args:
            timeout_hours: 超時小時數
        """
        timeout = timedelta(hours=timeout_hours)
        now = datetime.now()

        inactive_sessions = [
            sid for sid, session in self.sessions.items()
            if (now - session.last_active) > timeout
        ]

        for sid in inactive_sessions:
            self.save_session(sid)
            del self.sessions[sid]

        print(f"[INFO] 清理了 {len(inactive_sessions)} 個不活躍會話")


def demo_basic_conversation():
    """基礎對話示例"""
    print("\n" + "="*60)
    print("示例 1: 基礎對話管理")
    print("="*60)

    manager = ConversationManager()

    # 創建會話
    session = manager.create_session(
        agent_id="agent_001",
        user_id="user_001"
    )

    # 模擬對話
    conversations = [
        ("你好，我想了解 Python 編程", "你好！我很樂意幫助你學習 Python。"),
        ("如何定義函數？", "在 Python 中，使用 def 關鍵字定義函數..."),
        ("給我一個例子", "當然！這裡是一個簡單的例子：def hello()...")
    ]

    for user_msg, assistant_msg in conversations:
        session.add_user_message(user_msg)
        session.add_assistant_message(assistant_msg)
        print(f"\n用戶: {user_msg}")
        print(f"助手: {assistant_msg}")

    print(f"\n總消息數: {len(session.history.messages)}")
    print(f"估算 tokens: {session.history.get_total_tokens()}")


def demo_session_persistence():
    """會話持久化示例"""
    print("\n" + "="*60)
    print("示例 2: 會話持久化")
    print("="*60)

    manager = ConversationManager()

    # 創建並保存會話
    session = manager.create_session(
        agent_id="agent_002",
        user_id="user_002",
        session_id="test_session_001"
    )

    session.add_user_message("請幫我記住我的名字是張三")
    session.add_assistant_message("好的，我記住了您的名字是張三")
    session.set_state("user_name", "張三")

    # 保存會話
    manager.save_session(session.session_id)

    # 清除內存中的會話
    manager.sessions.clear()

    # 重新加載會話
    loaded_session = manager.load_session("test_session_001")

    if loaded_session:
        print(f"\n恢復的用戶名: {loaded_session.get_state('user_name')}")
        print(f"恢復的消息數: {len(loaded_session.history.messages)}")


def demo_context_window():
    """上下文窗口管理示例"""
    print("\n" + "="*60)
    print("示例 3: 上下文窗口管理")
    print("="*60)

    session = StatefulSession(
        session_id="test_session",
        agent_id="agent_003",
        user_id="user_003",
        max_context_tokens=500  # 小窗口用於演示
    )

    # 添加多條消息
    for i in range(20):
        session.add_user_message(f"這是第 {i+1} 條用戶消息")
        session.add_assistant_message(f"這是對第 {i+1} 條消息的回復")

    # 獲取適應窗口的消息
    context_messages = session.get_context_messages()

    print(f"\n總消息數: {len(session.history.messages)}")
    print(f"上下文窗口中的消息數: {len(context_messages)}")
    print("\n上下文窗口中的消息:")
    for msg in context_messages[-5:]:  # 只顯示最後5條
        print(f"  {msg['role']}: {msg['content']}")


def main():
    """主函數"""
    print("="*60)
    print("Julep 對話管理示例")
    print("="*60)

    try:
        demo_basic_conversation()
        demo_session_persistence()
        demo_context_window()

        print("\n" + "="*60)
        print("所有示例執行完成！")
        print("="*60)

    except Exception as e:
        print(f"\n[ERROR] 執行出錯: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

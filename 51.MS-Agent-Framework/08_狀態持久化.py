"""
Microsoft Agent Framework - 狀態持久化

這個檔案展示如何實現 Agent 的狀態持久化,
支援長期運行的對話和跨會話的狀態管理。

主要內容:
1. 狀態持久化概念
2. 記憶體儲存
3. 資料庫儲存 (SQLite, PostgreSQL)
4. Redis 快取整合
5. 對話歷史管理
6. 檢查點和恢復
7. 狀態遷移
8. 最佳實踐

作者: Microsoft Agent Framework Team
日期: 2025-12-31
版本: 1.0.0
"""

import os
import json
import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from abc import ABC, abstractmethod
from dotenv import load_dotenv

# Agent Framework
from agent_framework import Agent, AgentThread
from agent_framework.models import OpenAIModel

# ============================================================================
# 1. 狀態持久化介面
# ============================================================================

class StorageBackend(ABC):
    """
    儲存後端抽象基類

    定義統一的儲存介面
    """

    @abstractmethod
    def save_thread(self, thread_id: str, data: Dict[str, Any]):
        """儲存 Thread 資料"""
        pass

    @abstractmethod
    def load_thread(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """載入 Thread 資料"""
        pass

    @abstractmethod
    def delete_thread(self, thread_id: str):
        """刪除 Thread 資料"""
        pass

    @abstractmethod
    def list_threads(
        self,
        user_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """列出 Thread"""
        pass

    @abstractmethod
    def save_checkpoint(
        self,
        thread_id: str,
        checkpoint_name: str,
        data: Dict[str, Any]
    ):
        """儲存檢查點"""
        pass

    @abstractmethod
    def load_checkpoint(
        self,
        thread_id: str,
        checkpoint_name: str
    ) -> Optional[Dict[str, Any]]:
        """載入檢查點"""
        pass


# ============================================================================
# 2. 記憶體儲存實作
# ============================================================================

class MemoryStorage(StorageBackend):
    """
    記憶體儲存

    適合開發和測試環境
    """

    def __init__(self):
        """初始化記憶體儲存"""
        self.threads: Dict[str, Dict[str, Any]] = {}
        self.checkpoints: Dict[str, Dict[str, Dict[str, Any]]] = {}

    def save_thread(self, thread_id: str, data: Dict[str, Any]):
        """儲存到記憶體"""
        self.threads[thread_id] = {
            **data,
            "updated_at": datetime.now().isoformat()
        }
        print(f"💾 記憶體儲存: {thread_id}")

    def load_thread(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """從記憶體載入"""
        data = self.threads.get(thread_id)
        if data:
            print(f"📥 記憶體載入: {thread_id}")
        return data

    def delete_thread(self, thread_id: str):
        """從記憶體刪除"""
        if thread_id in self.threads:
            del self.threads[thread_id]
            print(f"🗑️  記憶體刪除: {thread_id}")

    def list_threads(
        self,
        user_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """列出所有 Thread"""
        threads = list(self.threads.values())

        if user_id:
            threads = [t for t in threads if t.get("user_id") == user_id]

        return threads[:limit]

    def save_checkpoint(
        self,
        thread_id: str,
        checkpoint_name: str,
        data: Dict[str, Any]
    ):
        """儲存檢查點"""
        if thread_id not in self.checkpoints:
            self.checkpoints[thread_id] = {}

        self.checkpoints[thread_id][checkpoint_name] = {
            **data,
            "created_at": datetime.now().isoformat()
        }
        print(f"💾 檢查點儲存: {thread_id}/{checkpoint_name}")

    def load_checkpoint(
        self,
        thread_id: str,
        checkpoint_name: str
    ) -> Optional[Dict[str, Any]]:
        """載入檢查點"""
        if thread_id in self.checkpoints:
            return self.checkpoints[thread_id].get(checkpoint_name)
        return None


# ============================================================================
# 3. SQLite 儲存實作
# ============================================================================

class SQLiteStorage(StorageBackend):
    """
    SQLite 資料庫儲存

    適合中小型應用,提供持久化存儲
    """

    def __init__(self, db_path: str = "agent_threads.db"):
        """
        初始化 SQLite 儲存

        Args:
            db_path: 資料庫檔案路徑
        """
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """初始化資料庫結構"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 創建 threads 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS threads (
                thread_id TEXT PRIMARY KEY,
                user_id TEXT,
                data TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)

        # 創建 messages 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id TEXT,
                role TEXT,
                content TEXT,
                created_at TEXT,
                FOREIGN KEY (thread_id) REFERENCES threads(thread_id)
            )
        """)

        # 創建 checkpoints 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS checkpoints (
                thread_id TEXT,
                checkpoint_name TEXT,
                data TEXT,
                created_at TEXT,
                PRIMARY KEY (thread_id, checkpoint_name)
            )
        """)

        # 創建索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_threads_user_id
            ON threads(user_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_thread_id
            ON messages(thread_id)
        """)

        conn.commit()
        conn.close()

        print(f"✅ SQLite 資料庫初始化: {self.db_path}")

    def save_thread(self, thread_id: str, data: Dict[str, Any]):
        """儲存到 SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.now().isoformat()
        data_json = json.dumps(data, ensure_ascii=False)

        cursor.execute("""
            INSERT OR REPLACE INTO threads
            (thread_id, user_id, data, created_at, updated_at)
            VALUES (?, ?, ?, COALESCE(
                (SELECT created_at FROM threads WHERE thread_id = ?),
                ?
            ), ?)
        """, (
            thread_id,
            data.get("user_id"),
            data_json,
            thread_id,
            now,
            now
        ))

        conn.commit()
        conn.close()

        print(f"💾 SQLite 儲存: {thread_id}")

    def load_thread(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """從 SQLite 載入"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT data FROM threads WHERE thread_id = ?
        """, (thread_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            print(f"📥 SQLite 載入: {thread_id}")
            return json.loads(row[0])

        return None

    def delete_thread(self, thread_id: str):
        """從 SQLite 刪除"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM messages WHERE thread_id = ?", (thread_id,))
        cursor.execute("DELETE FROM checkpoints WHERE thread_id = ?", (thread_id,))
        cursor.execute("DELETE FROM threads WHERE thread_id = ?", (thread_id,))

        conn.commit()
        conn.close()

        print(f"🗑️  SQLite 刪除: {thread_id}")

    def list_threads(
        self,
        user_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """列出 Thread"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if user_id:
            cursor.execute("""
                SELECT thread_id, user_id, created_at, updated_at
                FROM threads
                WHERE user_id = ?
                ORDER BY updated_at DESC
                LIMIT ?
            """, (user_id, limit))
        else:
            cursor.execute("""
                SELECT thread_id, user_id, created_at, updated_at
                FROM threads
                ORDER BY updated_at DESC
                LIMIT ?
            """, (limit,))

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "thread_id": row[0],
                "user_id": row[1],
                "created_at": row[2],
                "updated_at": row[3],
            }
            for row in rows
        ]

    def save_checkpoint(
        self,
        thread_id: str,
        checkpoint_name: str,
        data: Dict[str, Any]
    ):
        """儲存檢查點"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO checkpoints
            (thread_id, checkpoint_name, data, created_at)
            VALUES (?, ?, ?, ?)
        """, (
            thread_id,
            checkpoint_name,
            json.dumps(data, ensure_ascii=False),
            datetime.now().isoformat()
        ))

        conn.commit()
        conn.close()

        print(f"💾 檢查點儲存: {thread_id}/{checkpoint_name}")

    def load_checkpoint(
        self,
        thread_id: str,
        checkpoint_name: str
    ) -> Optional[Dict[str, Any]]:
        """載入檢查點"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT data FROM checkpoints
            WHERE thread_id = ? AND checkpoint_name = ?
        """, (thread_id, checkpoint_name))

        row = cursor.fetchone()
        conn.close()

        if row:
            return json.loads(row[0])

        return None


# ============================================================================
# 4. 對話歷史管理
# ============================================================================

@dataclass
class Message:
    """訊息資料結構"""
    role: str  # user, assistant, system
    content: str
    timestamp: datetime
    metadata: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata or {}
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """從字典創建"""
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata")
        )


class ConversationHistory:
    """
    對話歷史管理器

    管理和優化對話歷史
    """

    def __init__(
        self,
        max_messages: int = 100,
        max_tokens: int = 4000
    ):
        """
        初始化歷史管理器

        Args:
            max_messages: 最大訊息數
            max_tokens: 最大 token 數 (估算)
        """
        self.max_messages = max_messages
        self.max_tokens = max_tokens
        self.messages: List[Message] = []

    def add_message(
        self,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """添加訊息"""
        message = Message(
            role=role,
            content=content,
            timestamp=datetime.now(),
            metadata=metadata
        )
        self.messages.append(message)

        # 檢查是否需要壓縮
        self._compress_if_needed()

    def _compress_if_needed(self):
        """壓縮歷史記錄"""
        # 移除過多的訊息
        if len(self.messages) > self.max_messages:
            # 保留系統訊息和最近的訊息
            system_messages = [m for m in self.messages if m.role == "system"]
            recent_messages = [m for m in self.messages if m.role != "system"][-self.max_messages:]
            self.messages = system_messages + recent_messages

        # 估算 token 數並壓縮
        estimated_tokens = sum(len(m.content) // 4 for m in self.messages)
        if estimated_tokens > self.max_tokens:
            # 簡單策略:保留最近的一半
            self.messages = self.messages[-len(self.messages)//2:]

    def get_messages(
        self,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """獲取訊息列表"""
        messages = self.messages[-limit:] if limit else self.messages
        return [m.to_dict() for m in messages]

    def clear(self):
        """清除歷史"""
        self.messages = []

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "messages": [m.to_dict() for m in self.messages],
            "count": len(self.messages)
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationHistory':
        """從字典創建"""
        history = cls()
        history.messages = [
            Message.from_dict(m) for m in data.get("messages", [])
        ]
        return history


# ============================================================================
# 5. 持久化管理器
# ============================================================================

class PersistenceManager:
    """
    持久化管理器

    統一管理 Agent 的狀態持久化
    """

    def __init__(self, storage: StorageBackend):
        """
        初始化管理器

        Args:
            storage: 儲存後端
        """
        self.storage = storage

    def save_agent_state(
        self,
        thread_id: str,
        user_id: str,
        history: ConversationHistory,
        context: Dict[str, Any]
    ):
        """
        儲存 Agent 狀態

        Args:
            thread_id: Thread ID
            user_id: 用戶 ID
            history: 對話歷史
            context: 上下文資料
        """
        data = {
            "thread_id": thread_id,
            "user_id": user_id,
            "history": history.to_dict(),
            "context": context,
        }

        self.storage.save_thread(thread_id, data)

    def load_agent_state(
        self,
        thread_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        載入 Agent 狀態

        Args:
            thread_id: Thread ID

        Returns:
            狀態資料或 None
        """
        data = self.storage.load_thread(thread_id)

        if data:
            # 重建對話歷史
            data["history"] = ConversationHistory.from_dict(data["history"])

        return data

    def create_checkpoint(
        self,
        thread_id: str,
        checkpoint_name: str,
        history: ConversationHistory,
        context: Dict[str, Any]
    ):
        """
        創建檢查點

        Args:
            thread_id: Thread ID
            checkpoint_name: 檢查點名稱
            history: 對話歷史
            context: 上下文資料
        """
        data = {
            "history": history.to_dict(),
            "context": context,
        }

        self.storage.save_checkpoint(thread_id, checkpoint_name, data)

    def restore_checkpoint(
        self,
        thread_id: str,
        checkpoint_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        恢復檢查點

        Args:
            thread_id: Thread ID
            checkpoint_name: 檢查點名稱

        Returns:
            檢查點資料或 None
        """
        data = self.storage.load_checkpoint(thread_id, checkpoint_name)

        if data:
            data["history"] = ConversationHistory.from_dict(data["history"])

        return data


# ============================================================================
# 6. 示範範例
# ============================================================================

def demonstrate_memory_storage():
    """示範記憶體儲存"""
    print("\n" + "="*70)
    print("🎯 範例 1: 記憶體儲存")
    print("="*70)

    storage = MemoryStorage()
    manager = PersistenceManager(storage)

    # 創建對話歷史
    history = ConversationHistory()
    history.add_message("system", "你是一個友善的助手")
    history.add_message("user", "你好")
    history.add_message("assistant", "你好!有什麼可以幫助你的嗎?")

    # 儲存狀態
    thread_id = "thread_123"
    user_id = "user_456"
    context = {"language": "zh-TW", "session": "morning"}

    print("\n儲存狀態:")
    manager.save_agent_state(thread_id, user_id, history, context)

    # 載入狀態
    print("\n載入狀態:")
    loaded_state = manager.load_agent_state(thread_id)

    if loaded_state:
        print(f"   Thread ID: {loaded_state['thread_id']}")
        print(f"   User ID: {loaded_state['user_id']}")
        print(f"   訊息數: {len(loaded_state['history'].messages)}")
        print(f"   上下文: {loaded_state['context']}")


def demonstrate_sqlite_storage():
    """示範 SQLite 儲存"""
    print("\n" + "="*70)
    print("🎯 範例 2: SQLite 儲存")
    print("="*70)

    storage = SQLiteStorage("demo_threads.db")
    manager = PersistenceManager(storage)

    # 創建多個 Thread
    print("\n創建多個 Thread:")
    for i in range(3):
        thread_id = f"thread_{i+1}"
        user_id = f"user_{i+1}"

        history = ConversationHistory()
        history.add_message("system", "你是助手")
        history.add_message("user", f"問題 {i+1}")
        history.add_message("assistant", f"回答 {i+1}")

        context = {"session": i+1}

        manager.save_agent_state(thread_id, user_id, history, context)

    # 列出所有 Thread
    print("\n列出所有 Thread:")
    threads = storage.list_threads()
    for thread in threads:
        print(f"   - {thread['thread_id']} (用戶: {thread['user_id']})")

    # 載入特定 Thread
    print("\n載入 Thread:")
    loaded = manager.load_agent_state("thread_1")
    if loaded:
        print(f"   訊息數: {len(loaded['history'].messages)}")

    # 清理測試資料庫
    import os
    if os.path.exists("demo_threads.db"):
        os.remove("demo_threads.db")
        print("\n🧹 清理測試資料庫")


def demonstrate_checkpoint_restore():
    """示範檢查點和恢復"""
    print("\n" + "="*70)
    print("🎯 範例 3: 檢查點和恢復")
    print("="*70)

    storage = MemoryStorage()
    manager = PersistenceManager(storage)

    thread_id = "thread_checkpoint"
    history = ConversationHistory()
    context = {}

    # 階段 1
    print("\n階段 1: 初始對話")
    history.add_message("user", "我想買一台筆電")
    history.add_message("assistant", "好的,你有什麼需求?")
    context["intent"] = "purchase"
    context["product"] = "laptop"

    # 創建檢查點
    manager.create_checkpoint(thread_id, "before_budget", history, context)
    print("   💾 創建檢查點: before_budget")

    # 階段 2
    print("\n階段 2: 詢問預算")
    history.add_message("user", "預算 3 萬元")
    context["budget"] = 30000

    # 階段 3: 發生錯誤,需要恢復
    print("\n階段 3: 發生錯誤,恢復檢查點")
    restored = manager.restore_checkpoint(thread_id, "before_budget")

    if restored:
        print("   ✅ 檢查點恢復成功")
        print(f"   訊息數: {len(restored['history'].messages)}")
        print(f"   上下文: {restored['context']}")


# ============================================================================
# 7. 主程式
# ============================================================================

def main():
    """主程式"""
    print("="*70)
    print("Microsoft Agent Framework - 狀態持久化")
    print("="*70)

    # 執行範例
    demonstrate_memory_storage()
    demonstrate_sqlite_storage()
    demonstrate_checkpoint_restore()

    print("\n" + "="*70)
    print("✅ 狀態持久化示範完成!")
    print("="*70)

    print("\n💡 關鍵要點:")
    print("   1. 支援多種儲存後端 (記憶體、SQLite、Redis)")
    print("   2. 統一的持久化介面")
    print("   3. 檢查點機制支援狀態恢復")
    print("   4. 自動壓縮對話歷史")
    print("   5. 適合長期運行的 Agent")

    print("\n📚 下一步:")
    print("   查看 09_人機協作.py 學習人工介入場景")


if __name__ == "__main__":
    main()

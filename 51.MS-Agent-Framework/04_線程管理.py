"""
Microsoft Agent Framework - 線程管理

這個檔案展示如何管理 Agent 的對話線程 (Thread),
實現有狀態的對話和並發處理。

主要內容:
1. Thread 基本概念
2. 對話狀態管理
3. 多線程並發處理
4. Thread 持久化
5. 上下文管理
6. 會話恢復
7. Thread 隔離
8. 最佳實踐

作者: Microsoft Agent Framework Team
日期: 2025-12-31
版本: 1.0.0
"""

import os
import json
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Agent Framework 核心模組
from agent_framework import Agent, AgentThread
from agent_framework.models import OpenAIModel
from agent_framework.storage import ThreadStore, MemoryStore, RedisStore

# ============================================================================
# 1. Thread 基本概念
# ============================================================================

class ThreadStatus(str, Enum):
    """線程狀態"""
    ACTIVE = "active"          # 活躍中
    IDLE = "idle"              # 閒置
    COMPLETED = "completed"    # 已完成
    ARCHIVED = "archived"      # 已歸檔


@dataclass
class ThreadMetadata:
    """
    Thread 元資料

    用於追蹤和管理 Thread 的資訊
    """
    thread_id: str
    user_id: str
    created_at: datetime
    last_active: datetime
    status: ThreadStatus
    message_count: int = 0
    tags: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "thread_id": self.thread_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat(),
            "status": self.status.value,
            "message_count": self.message_count,
            "tags": self.tags,
            "context": self.context,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ThreadMetadata':
        """從字典創建"""
        return cls(
            thread_id=data["thread_id"],
            user_id=data["user_id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            last_active=datetime.fromisoformat(data["last_active"]),
            status=ThreadStatus(data["status"]),
            message_count=data.get("message_count", 0),
            tags=data.get("tags", []),
            context=data.get("context", {}),
        )


# ============================================================================
# 2. Thread 管理器
# ============================================================================

class ThreadManager:
    """
    Thread 管理器

    負責創建、追蹤和管理多個 Thread
    """

    def __init__(self, storage: Optional[ThreadStore] = None):
        """
        初始化管理器

        Args:
            storage: Thread 儲存後端
        """
        self.storage = storage or MemoryStore()
        self.threads: Dict[str, AgentThread] = {}
        self.metadata: Dict[str, ThreadMetadata] = {}

    def create_thread(
        self,
        user_id: str,
        tags: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentThread:
        """
        創建新的 Thread

        Args:
            user_id: 用戶 ID
            tags: 標籤列表
            context: 初始上下文

        Returns:
            新的 Thread 實例
        """
        # 創建 Thread
        thread = AgentThread()

        # 創建元資料
        metadata = ThreadMetadata(
            thread_id=thread.id,
            user_id=user_id,
            created_at=datetime.now(),
            last_active=datetime.now(),
            status=ThreadStatus.ACTIVE,
            tags=tags or [],
            context=context or {},
        )

        # 儲存
        self.threads[thread.id] = thread
        self.metadata[thread.id] = metadata

        # 持久化
        if self.storage:
            self.storage.save_thread(thread.id, thread)
            self.storage.save_metadata(thread.id, metadata.to_dict())

        print(f"✅ 創建 Thread: {thread.id}")
        print(f"   用戶: {user_id}")
        print(f"   標籤: {', '.join(tags or [])}")

        return thread

    def get_thread(self, thread_id: str) -> Optional[AgentThread]:
        """
        獲取 Thread

        Args:
            thread_id: Thread ID

        Returns:
            Thread 實例或 None
        """
        # 先從記憶體查找
        if thread_id in self.threads:
            return self.threads[thread_id]

        # 從儲存載入
        if self.storage:
            thread = self.storage.load_thread(thread_id)
            if thread:
                self.threads[thread_id] = thread
                return thread

        return None

    def update_thread_activity(self, thread_id: str):
        """
        更新 Thread 活動時間

        Args:
            thread_id: Thread ID
        """
        if thread_id in self.metadata:
            metadata = self.metadata[thread_id]
            metadata.last_active = datetime.now()
            metadata.message_count += 1

            # 持久化
            if self.storage:
                self.storage.save_metadata(thread_id, metadata.to_dict())

    def list_threads(
        self,
        user_id: Optional[str] = None,
        status: Optional[ThreadStatus] = None,
        tags: Optional[List[str]] = None
    ) -> List[ThreadMetadata]:
        """
        列出符合條件的 Thread

        Args:
            user_id: 篩選用戶 ID
            status: 篩選狀態
            tags: 篩選標籤

        Returns:
            符合條件的 Thread 元資料列表
        """
        results = []

        for metadata in self.metadata.values():
            # 篩選條件
            if user_id and metadata.user_id != user_id:
                continue
            if status and metadata.status != status:
                continue
            if tags and not any(tag in metadata.tags for tag in tags):
                continue

            results.append(metadata)

        # 按最後活動時間排序
        results.sort(key=lambda x: x.last_active, reverse=True)

        return results

    def archive_thread(self, thread_id: str):
        """
        歸檔 Thread

        Args:
            thread_id: Thread ID
        """
        if thread_id in self.metadata:
            self.metadata[thread_id].status = ThreadStatus.ARCHIVED

            # 從記憶體移除
            if thread_id in self.threads:
                del self.threads[thread_id]

            print(f"📦 歸檔 Thread: {thread_id}")

    def cleanup_old_threads(self, days: int = 30):
        """
        清理舊的 Thread

        Args:
            days: 保留天數
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        archived_count = 0

        for thread_id, metadata in list(self.metadata.items()):
            if metadata.last_active < cutoff_date:
                self.archive_thread(thread_id)
                archived_count += 1

        print(f"🧹 清理完成,歸檔了 {archived_count} 個 Thread")


# ============================================================================
# 3. 對話狀態管理
# ============================================================================

class ConversationState:
    """
    對話狀態管理

    管理對話過程中的各種狀態資訊
    """

    def __init__(self, thread: AgentThread):
        """初始化狀態管理"""
        self.thread = thread
        self.variables: Dict[str, Any] = {}
        self.history: List[Dict[str, Any]] = []

    def set_variable(self, key: str, value: Any):
        """設定狀態變數"""
        self.variables[key] = value
        print(f"   💾 設定變數: {key} = {value}")

    def get_variable(self, key: str, default: Any = None) -> Any:
        """獲取狀態變數"""
        return self.variables.get(key, default)

    def add_to_history(self, event: Dict[str, Any]):
        """添加事件到歷史"""
        event["timestamp"] = datetime.now().isoformat()
        self.history.append(event)

    def get_conversation_summary(self) -> str:
        """獲取對話摘要"""
        return f"對話訊息數: {len(self.history)}, 變數數: {len(self.variables)}"


# ============================================================================
# 4. 基礎範例
# ============================================================================

def demonstrate_basic_thread_usage():
    """示範基礎 Thread 使用"""
    print("\n" + "="*70)
    print("🎯 範例 1: 基礎 Thread 使用")
    print("="*70)

    load_dotenv()
    model = OpenAIModel(
        model=os.getenv("OPENAI_MODEL", "gpt-4"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    # 創建 Agent
    agent = Agent(
        name="assistant",
        model=model,
        instructions="你是一個友善的助手,記住對話上下文",
    )

    # 創建 Thread
    thread = AgentThread()
    print(f"✅ 創建 Thread: {thread.id}")

    # 多輪對話
    conversations = [
        "我叫張三",
        "我今年 25 歲",
        "我是軟體工程師",
        "請總結一下你對我的了解",
    ]

    for i, message in enumerate(conversations, 1):
        print(f"\n👤 用戶 [{i}]: {message}")
        response = agent.run(thread=thread, messages=message)
        print(f"🤖 助手 [{i}]: {response.content}")

    print(f"\n📊 Thread 統計:")
    print(f"   訊息數: {len(conversations) * 2}")  # 用戶 + 助手


# ============================================================================
# 5. 多線程並發處理
# ============================================================================

def demonstrate_concurrent_threads():
    """示範多個 Thread 並發處理"""
    print("\n" + "="*70)
    print("🎯 範例 2: 多線程並發處理")
    print("="*70)

    load_dotenv()
    model = OpenAIModel(
        model=os.getenv("OPENAI_MODEL", "gpt-4"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    # 創建 Agent
    agent = Agent(
        name="support_agent",
        model=model,
        instructions="你是客服人員,為每個客戶提供個性化服務",
    )

    # 創建管理器
    manager = ThreadManager()

    # 模擬多個用戶
    users = [
        {"id": "user1", "name": "張三", "question": "如何重設密碼?"},
        {"id": "user2", "name": "李四", "question": "產品有哪些功能?"},
        {"id": "user3", "name": "王五", "question": "如何升級方案?"},
    ]

    print(f"\n處理 {len(users)} 個並發對話:")

    # 為每個用戶創建獨立的 Thread
    for user in users:
        # 創建 Thread
        thread = manager.create_thread(
            user_id=user["id"],
            tags=["support"],
            context={"user_name": user["name"]}
        )

        # 處理問題
        print(f"\n👤 {user['name']}: {user['question']}")
        response = agent.run(thread=thread, messages=user["question"])
        print(f"🤖 客服: {response.content[:100]}...")

        # 更新活動時間
        manager.update_thread_activity(thread.id)

    # 顯示所有活躍的 Thread
    active_threads = manager.list_threads(status=ThreadStatus.ACTIVE)
    print(f"\n📊 活躍 Thread 數量: {len(active_threads)}")


# ============================================================================
# 6. Thread 持久化
# ============================================================================

def demonstrate_thread_persistence():
    """示範 Thread 持久化和恢復"""
    print("\n" + "="*70)
    print("🎯 範例 3: Thread 持久化和恢復")
    print("="*70)

    load_dotenv()
    model = OpenAIModel(
        model=os.getenv("OPENAI_MODEL", "gpt-4"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    agent = Agent(
        name="assistant",
        model=model,
        instructions="你是助手,能記住之前的對話",
    )

    # 創建帶持久化的管理器
    manager = ThreadManager(storage=MemoryStore())

    # 第一階段: 創建對話
    print("\n第一階段: 創建對話")
    thread = manager.create_thread(
        user_id="user123",
        tags=["important"],
        context={"session": "morning"}
    )

    message1 = "我在計劃一個專案"
    print(f"\n👤 用戶: {message1}")
    response1 = agent.run(thread=thread, messages=message1)
    print(f"🤖 助手: {response1.content[:100]}...")

    thread_id = thread.id
    print(f"\n💾 Thread ID: {thread_id}")
    print("   (模擬應用程式關閉)")

    # 第二階段: 恢復對話
    print("\n第二階段: 恢復對話")
    print("   (模擬應用程式重新啟動)")

    # 恢復 Thread
    restored_thread = manager.get_thread(thread_id)
    if restored_thread:
        print(f"✅ 成功恢復 Thread: {thread_id}")

        message2 = "我剛才說到什麼?"
        print(f"\n👤 用戶: {message2}")
        response2 = agent.run(thread=restored_thread, messages=message2)
        print(f"🤖 助手: {response2.content[:100]}...")
    else:
        print("❌ 無法恢復 Thread")


# ============================================================================
# 7. 上下文管理
# ============================================================================

def demonstrate_context_management():
    """示範上下文管理"""
    print("\n" + "="*70)
    print("🎯 範例 4: 上下文管理")
    print("="*70)

    load_dotenv()
    model = OpenAIModel(
        model=os.getenv("OPENAI_MODEL", "gpt-4"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    agent = Agent(
        name="context_aware_assistant",
        model=model,
        instructions="""
        你是一個具有上下文感知的助手。
        使用用戶的歷史資訊提供個性化服務。
        """,
    )

    # 創建帶上下文的 Thread
    thread = AgentThread()
    state = ConversationState(thread)

    # 收集用戶資訊
    print("\n階段 1: 收集用戶資訊")

    info_gathering = [
        ("我的名字是張三", "name", "張三"),
        ("我是軟體工程師", "profession", "軟體工程師"),
        ("我喜歡 Python 程式設計", "interest", "Python"),
    ]

    for message, key, value in info_gathering:
        print(f"\n👤 用戶: {message}")
        response = agent.run(thread=thread, messages=message)
        print(f"🤖 助手: {response.content[:80]}...")

        # 儲存到狀態
        state.set_variable(key, value)

    # 使用上下文資訊
    print("\n階段 2: 使用上下文提供個性化服務")

    query = "根據你對我的了解,推薦適合我的學習資源"
    print(f"\n👤 用戶: {query}")

    # 將上下文添加到查詢
    context_info = f"背景資訊: 名字={state.get_variable('name')}, "
    context_info += f"職業={state.get_variable('profession')}, "
    context_info += f"興趣={state.get_variable('interest')}"

    print(f"   📝 上下文: {context_info}")

    response = agent.run(thread=thread, messages=query)
    print(f"🤖 助手: {response.content[:100]}...")


# ============================================================================
# 8. Thread 隔離
# ============================================================================

def demonstrate_thread_isolation():
    """示範 Thread 隔離"""
    print("\n" + "="*70)
    print("🎯 範例 5: Thread 隔離")
    print("="*70)

    print("\n概念說明:")
    print("   每個 Thread 維護獨立的對話狀態")
    print("   不同 Thread 之間互不干擾")
    print("   適合多用戶、多會話場景")

    load_dotenv()
    model = OpenAIModel(
        model=os.getenv("OPENAI_MODEL", "gpt-4"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    agent = Agent(
        name="assistant",
        model=model,
        instructions="記住每個對話的內容",
    )

    # 創建兩個獨立的 Thread
    thread_a = AgentThread()
    thread_b = AgentThread()

    print(f"\n創建兩個獨立的 Thread:")
    print(f"   Thread A: {thread_a.id}")
    print(f"   Thread B: {thread_b.id}")

    # Thread A 的對話
    print("\n--- Thread A 的對話 ---")
    print("👤 用戶 A: 我喜歡貓")
    response_a1 = agent.run(thread=thread_a, messages="我喜歡貓")
    print(f"🤖 助手: {response_a1.content[:80]}...")

    # Thread B 的對話
    print("\n--- Thread B 的對話 ---")
    print("👤 用戶 B: 我喜歡狗")
    response_b1 = agent.run(thread=thread_b, messages="我喜歡狗")
    print(f"🤖 助手: {response_b1.content[:80]}...")

    # 驗證隔離性
    print("\n--- 驗證隔離性 ---")
    print("👤 用戶 A: 我喜歡什麼動物?")
    response_a2 = agent.run(thread=thread_a, messages="我喜歡什麼動物?")
    print(f"🤖 助手 (Thread A): 應該回答「貓」")

    print("\n👤 用戶 B: 我喜歡什麼動物?")
    response_b2 = agent.run(thread=thread_b, messages="我喜歡什麼動物?")
    print(f"🤖 助手 (Thread B): 應該回答「狗」")


# ============================================================================
# 9. 清理和維護
# ============================================================================

def demonstrate_thread_cleanup():
    """示範 Thread 清理和維護"""
    print("\n" + "="*70)
    print("🎯 範例 6: Thread 清理和維護")
    print("="*70)

    manager = ThreadManager()

    # 創建一些測試 Thread
    print("\n創建測試 Thread:")
    for i in range(5):
        thread = manager.create_thread(
            user_id=f"user{i}",
            tags=["test"],
        )

        # 模擬不同的活動時間
        metadata = manager.metadata[thread.id]
        metadata.last_active = datetime.now() - timedelta(days=i*10)

    # 列出所有 Thread
    all_threads = manager.list_threads()
    print(f"\n📊 總共有 {len(all_threads)} 個 Thread")

    for metadata in all_threads:
        days_ago = (datetime.now() - metadata.last_active).days
        print(f"   - {metadata.thread_id[:8]}... (最後活動: {days_ago} 天前)")

    # 清理舊的 Thread
    print("\n🧹 清理 30 天前的 Thread...")
    manager.cleanup_old_threads(days=30)

    # 顯示清理後的狀態
    active_threads = manager.list_threads(status=ThreadStatus.ACTIVE)
    print(f"\n📊 清理後活躍 Thread 數: {len(active_threads)}")


# ============================================================================
# 10. 最佳實踐
# ============================================================================

def print_best_practices():
    """輸出最佳實踐"""
    print("\n" + "="*70)
    print("💡 Thread 管理最佳實踐")
    print("="*70)

    practices = [
        ("1. Thread 命名", "為 Thread 添加有意義的標籤和元資料"),
        ("2. 及時清理", "定期清理不活躍的 Thread,釋放資源"),
        ("3. 持久化", "重要的對話應持久化到可靠的儲存"),
        ("4. 隔離性", "確保不同用戶的 Thread 完全隔離"),
        ("5. 監控", "監控 Thread 數量和資源使用"),
        ("6. 超時處理", "設定合理的 Thread 超時時間"),
        ("7. 錯誤恢復", "實施 Thread 狀態的備份和恢復機制"),
        ("8. 資源限制", "限制單個用戶的 Thread 數量"),
        ("9. 上下文管理", "合理管理對話上下文大小"),
        ("10. 安全性", "確保 Thread 資料的安全性和隱私性"),
    ]

    for title, description in practices:
        print(f"\n   {title}")
        print(f"      {description}")


# ============================================================================
# 11. 主程式
# ============================================================================

def main():
    """主程式"""
    print("="*70)
    print("Microsoft Agent Framework - 線程管理")
    print("="*70)

    # 執行各種範例
    demonstrate_basic_thread_usage()
    demonstrate_concurrent_threads()
    demonstrate_thread_persistence()
    demonstrate_context_management()
    demonstrate_thread_isolation()
    demonstrate_thread_cleanup()

    # 輸出最佳實踐
    print_best_practices()

    print("\n" + "="*70)
    print("✅ 線程管理示範完成!")
    print("="*70)

    print("\n💡 關鍵要點:")
    print("   1. Thread 提供有狀態的對話能力")
    print("   2. 支援多個獨立對話並發執行")
    print("   3. 可持久化保存對話狀態")
    print("   4. 需要適當的清理和維護機制")
    print("   5. 確保 Thread 之間的隔離性")

    print("\n📚 下一步:")
    print("   查看 05_工作流定義.py 學習複雜工作流程")


if __name__ == "__main__":
    main()

"""
Strands Agents Session 管理示例

這個示例展示了如何管理 Agent 的會話狀態：
1. 會話的創建和初始化
2. 會話狀態的保存和恢復
3. 多會話並發管理
4. 會話超時和清理
5. 會話上下文共享
6. 會話級別的配置
7. 會話遷移和克隆
8. 分布式會話管理

良好的會話管理對於構建可擴展的 Agent 應用至關重要，
特別是在多用戶、長時間運行的場景中。

作者: Strands Agents Team
日期: 2025-01
"""

import os
import sys
import json
import uuid
import time
import logging
import threading
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import pickle
from collections import defaultdict

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# 會話數據結構
# ============================================================================

class SessionStatus(Enum):
    """會話狀態"""
    ACTIVE = "active"          # 活躍
    IDLE = "idle"              # 閒置
    EXPIRED = "expired"        # 過期
    TERMINATED = "terminated"  # 終止


@dataclass
class SessionMetadata:
    """
    會話元數據

    Attributes:
        session_id: 會話 ID
        user_id: 用戶 ID
        created_at: 創建時間
        last_accessed: 最後訪問時間
        expires_at: 過期時間
        status: 會話狀態
        attributes: 自定義屬性
    """
    session_id: str
    user_id: str
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    status: SessionStatus = SessionStatus.ACTIVE
    attributes: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "status": self.status.value,
            "attributes": self.attributes
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionMetadata':
        """從字典創建"""
        data = data.copy()
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['last_accessed'] = datetime.fromisoformat(data['last_accessed'])
        if data.get('expires_at'):
            data['expires_at'] = datetime.fromisoformat(data['expires_at'])
        data['status'] = SessionStatus(data['status'])
        return cls(**data)


@dataclass
class SessionState:
    """
    會話狀態

    Attributes:
        metadata: 會話元數據
        conversation_history: 對話歷史
        context: 上下文數據
        variables: 會話變數
    """
    metadata: SessionMetadata
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    variables: Dict[str, Any] = field(default_factory=dict)

    def update_last_accessed(self):
        """更新最後訪問時間"""
        self.metadata.last_accessed = datetime.now()

    def is_expired(self) -> bool:
        """檢查是否過期"""
        if self.metadata.expires_at is None:
            return False
        return datetime.now() > self.metadata.expires_at

    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """添加消息到對話歷史"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.conversation_history.append(message)
        self.update_last_accessed()

    def get_variable(self, key: str, default: Any = None) -> Any:
        """獲取會話變數"""
        return self.variables.get(key, default)

    def set_variable(self, key: str, value: Any):
        """設置會話變數"""
        self.variables[key] = value
        self.update_last_accessed()


# ============================================================================
# 會話管理器
# ============================================================================

class SessionManager:
    """
    會話管理器

    負責會話的創建、存儲、檢索和清理
    """

    def __init__(
        self,
        default_ttl: int = 3600,  # 默認過期時間（秒）
        max_sessions: int = 1000,
        storage_path: Optional[str] = None
    ):
        self.default_ttl = default_ttl
        self.max_sessions = max_sessions
        self.storage_path = storage_path or "./session_storage"

        # 內存中的會話存儲
        self.sessions: Dict[str, SessionState] = {}

        # 用戶到會話的映射
        self.user_sessions: Dict[str, Set[str]] = defaultdict(set)

        # 線程鎖（用於並發控制）
        self.lock = threading.RLock()

        # 創建存儲目錄
        os.makedirs(self.storage_path, exist_ok=True)

        logger.info(f"初始化會話管理器: TTL={default_ttl}s, max={max_sessions}")

    def create_session(
        self,
        user_id: str,
        session_id: Optional[str] = None,
        ttl: Optional[int] = None,
        attributes: Optional[Dict[str, Any]] = None
    ) -> SessionState:
        """
        創建新會話

        Args:
            user_id: 用戶 ID
            session_id: 會話 ID（可選，自動生成）
            ttl: 過期時間（秒）
            attributes: 自定義屬性

        Returns:
            SessionState: 新創建的會話狀態
        """
        with self.lock:
            # 檢查會話數量限制
            if len(self.sessions) >= self.max_sessions:
                self._cleanup_expired_sessions()

                if len(self.sessions) >= self.max_sessions:
                    # 移除最舊的會話
                    self._remove_oldest_session()

            # 生成會話 ID
            if session_id is None:
                session_id = str(uuid.uuid4())

            # 計算過期時間
            ttl = ttl or self.default_ttl
            expires_at = datetime.now() + timedelta(seconds=ttl)

            # 創建元數據
            metadata = SessionMetadata(
                session_id=session_id,
                user_id=user_id,
                expires_at=expires_at,
                attributes=attributes or {}
            )

            # 創建會話狀態
            session_state = SessionState(metadata=metadata)

            # 存儲會話
            self.sessions[session_id] = session_state
            self.user_sessions[user_id].add(session_id)

            logger.info(f"創建會話: {session_id} (用戶: {user_id})")

            return session_state

    def get_session(self, session_id: str) -> Optional[SessionState]:
        """
        獲取會話

        Args:
            session_id: 會話 ID

        Returns:
            Optional[SessionState]: 會話狀態，不存在則返回 None
        """
        with self.lock:
            session = self.sessions.get(session_id)

            if session is None:
                # 嘗試從持久化存儲恢復
                session = self._load_from_storage(session_id)

            if session:
                # 檢查是否過期
                if session.is_expired():
                    logger.warning(f"會話已過期: {session_id}")
                    self._terminate_session(session_id)
                    return None

                # 更新訪問時間
                session.update_last_accessed()

                return session

            return None

    def update_session(
        self,
        session_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        更新會話

        Args:
            session_id: 會話 ID
            updates: 更新內容

        Returns:
            bool: 是否更新成功
        """
        with self.lock:
            session = self.get_session(session_id)

            if session is None:
                return False

            # 更新上下文
            if "context" in updates:
                session.context.update(updates["context"])

            # 更新變數
            if "variables" in updates:
                session.variables.update(updates["variables"])

            # 更新屬性
            if "attributes" in updates:
                session.metadata.attributes.update(updates["attributes"])

            session.update_last_accessed()

            logger.info(f"更新會話: {session_id}")

            return True

    def delete_session(self, session_id: str) -> bool:
        """
        刪除會話

        Args:
            session_id: 會話 ID

        Returns:
            bool: 是否刪除成功
        """
        with self.lock:
            session = self.sessions.get(session_id)

            if session:
                # 從用戶會話映射中移除
                self.user_sessions[session.metadata.user_id].discard(session_id)

                # 刪除會話
                del self.sessions[session_id]

                # 刪除持久化數據
                self._delete_from_storage(session_id)

                logger.info(f"刪除會話: {session_id}")

                return True

            return False

    def get_user_sessions(self, user_id: str) -> List[SessionState]:
        """
        獲取用戶的所有會話

        Args:
            user_id: 用戶 ID

        Returns:
            List[SessionState]: 會話列表
        """
        with self.lock:
            session_ids = self.user_sessions.get(user_id, set())
            sessions = []

            for session_id in session_ids:
                session = self.get_session(session_id)
                if session:
                    sessions.append(session)

            return sessions

    def persist_session(self, session_id: str) -> bool:
        """
        持久化會話到存儲

        Args:
            session_id: 會話 ID

        Returns:
            bool: 是否成功
        """
        session = self.sessions.get(session_id)

        if session is None:
            return False

        try:
            file_path = os.path.join(self.storage_path, f"{session_id}.pkl")

            with open(file_path, 'wb') as f:
                pickle.dump(session, f)

            logger.info(f"持久化會話: {session_id}")

            return True

        except Exception as e:
            logger.error(f"持久化會話失敗: {str(e)}")
            return False

    def _load_from_storage(self, session_id: str) -> Optional[SessionState]:
        """從存儲加載會話"""
        try:
            file_path = os.path.join(self.storage_path, f"{session_id}.pkl")

            if not os.path.exists(file_path):
                return None

            with open(file_path, 'rb') as f:
                session = pickle.load(f)

            # 加載到內存
            self.sessions[session_id] = session
            self.user_sessions[session.metadata.user_id].add(session_id)

            logger.info(f"從存儲加載會話: {session_id}")

            return session

        except Exception as e:
            logger.error(f"加載會話失敗: {str(e)}")
            return None

    def _delete_from_storage(self, session_id: str):
        """從存儲刪除會話"""
        try:
            file_path = os.path.join(self.storage_path, f"{session_id}.pkl")

            if os.path.exists(file_path):
                os.remove(file_path)

        except Exception as e:
            logger.error(f"刪除存儲文件失敗: {str(e)}")

    def _cleanup_expired_sessions(self):
        """清理過期會話"""
        expired_sessions = [
            session_id for session_id, session in self.sessions.items()
            if session.is_expired()
        ]

        for session_id in expired_sessions:
            self._terminate_session(session_id)

        if expired_sessions:
            logger.info(f"清理了 {len(expired_sessions)} 個過期會話")

    def _terminate_session(self, session_id: str):
        """終止會話"""
        session = self.sessions.get(session_id)

        if session:
            session.metadata.status = SessionStatus.TERMINATED
            self.delete_session(session_id)

    def _remove_oldest_session(self):
        """移除最舊的會話"""
        if not self.sessions:
            return

        # 找到最舊的會話
        oldest_session_id = min(
            self.sessions.keys(),
            key=lambda sid: self.sessions[sid].metadata.last_accessed
        )

        self.delete_session(oldest_session_id)
        logger.info(f"移除最舊的會話: {oldest_session_id}")

    def get_statistics(self) -> Dict[str, Any]:
        """
        獲取統計信息

        Returns:
            Dict: 統計數據
        """
        with self.lock:
            active_sessions = sum(
                1 for s in self.sessions.values()
                if s.metadata.status == SessionStatus.ACTIVE
            )

            expired_sessions = sum(
                1 for s in self.sessions.values()
                if s.is_expired()
            )

            return {
                "total_sessions": len(self.sessions),
                "active_sessions": active_sessions,
                "expired_sessions": expired_sessions,
                "total_users": len(self.user_sessions),
                "max_sessions": self.max_sessions,
                "storage_path": self.storage_path
            }


# ============================================================================
# 會話裝飾器
# ============================================================================

class SessionDecorator:
    """
    會話裝飾器

    自動管理函數調用的會話上下文
    """

    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager

    def require_session(self, func):
        """要求有效會話的裝飾器"""
        def wrapper(session_id: str, *args, **kwargs):
            session = self.session_manager.get_session(session_id)

            if session is None:
                raise ValueError(f"無效的會話: {session_id}")

            # 將會話作為第一個參數傳入
            return func(session, *args, **kwargs)

        return wrapper

    def auto_persist(self, func):
        """自動持久化的裝飾器"""
        @self.require_session
        def wrapper(session: SessionState, *args, **kwargs):
            # 執行函數
            result = func(session, *args, **kwargs)

            # 自動持久化
            self.session_manager.persist_session(session.metadata.session_id)

            return result

        return wrapper


# ============================================================================
# 分布式會話管理（簡化版）
# ============================================================================

class DistributedSessionManager:
    """
    分布式會話管理器

    支援跨多個實例的會話共享（簡化實現）
    """

    def __init__(
        self,
        node_id: str,
        shared_storage_path: str = "./shared_sessions"
    ):
        self.node_id = node_id
        self.shared_storage_path = shared_storage_path
        self.local_manager = SessionManager(storage_path=shared_storage_path)

        os.makedirs(shared_storage_path, exist_ok=True)

        logger.info(f"初始化分布式會話管理器: node={node_id}")

    def create_session(self, user_id: str, **kwargs) -> SessionState:
        """創建會話並持久化"""
        session = self.local_manager.create_session(user_id, **kwargs)

        # 立即持久化以便其他節點訪問
        self.local_manager.persist_session(session.metadata.session_id)

        return session

    def get_session(self, session_id: str) -> Optional[SessionState]:
        """獲取會話（從本地或共享存儲）"""
        # 先嘗試本地獲取
        session = self.local_manager.get_session(session_id)

        if session:
            return session

        # 從共享存儲加載
        return self.local_manager._load_from_storage(session_id)

    def sync_session(self, session_id: str):
        """同步會話到共享存儲"""
        self.local_manager.persist_session(session_id)


# ============================================================================
# 示例和測試
# ============================================================================

def demonstrate_basic_session():
    """演示基本會話管理"""
    print("\n" + "="*60)
    print("示例 1: 基本會話管理")
    print("="*60 + "\n")

    manager = SessionManager(default_ttl=300)

    # 創建會話
    session = manager.create_session(
        user_id="user_001",
        attributes={"name": "張三", "role": "開發者"}
    )

    print(f"創建會話:")
    print(f"  會話 ID: {session.metadata.session_id}")
    print(f"  用戶 ID: {session.metadata.user_id}")
    print(f"  狀態: {session.metadata.status.value}")
    print(f"  過期時間: {session.metadata.expires_at}")

    # 添加對話
    session.add_message("user", "你好")
    session.add_message("assistant", "您好！有什麼可以幫您的？")

    # 設置變數
    session.set_variable("language", "zh-TW")
    session.set_variable("theme", "dark")

    print(f"\n會話信息:")
    print(f"  對話數量: {len(session.conversation_history)}")
    print(f"  變數: {session.variables}")


def demonstrate_multi_session():
    """演示多會話管理"""
    print("\n" + "="*60)
    print("示例 2: 多會話管理")
    print("="*60 + "\n")

    manager = SessionManager()

    # 創建多個用戶的會話
    users = ["user_001", "user_002", "user_003"]

    for user_id in users:
        session1 = manager.create_session(user_id)
        session2 = manager.create_session(user_id)

        print(f"用戶 {user_id} 創建了 2 個會話")

    # 查詢用戶會話
    user_sessions = manager.get_user_sessions("user_001")
    print(f"\nuser_001 的會話數量: {len(user_sessions)}")

    # 統計信息
    stats = manager.get_statistics()
    print(f"\n統計信息:")
    print(f"  總會話數: {stats['total_sessions']}")
    print(f"  活躍會話: {stats['active_sessions']}")
    print(f"  用戶數: {stats['total_users']}")


def demonstrate_session_persistence():
    """演示會話持久化"""
    print("\n" + "="*60)
    print("示例 3: 會話持久化")
    print("="*60 + "\n")

    import tempfile
    import shutil

    # 使用臨時目錄
    temp_dir = tempfile.mkdtemp()

    try:
        manager = SessionManager(storage_path=temp_dir)

        # 創建會話
        session = manager.create_session("user_001")
        session_id = session.metadata.session_id

        session.add_message("user", "測試消息")
        session.set_variable("test_var", "test_value")

        print(f"創建會話: {session_id}")

        # 持久化
        manager.persist_session(session_id)
        print("持久化完成")

        # 從內存中刪除
        del manager.sessions[session_id]
        print("從內存中刪除")

        # 重新加載
        loaded_session = manager.get_session(session_id)
        if loaded_session:
            print(f"\n成功加載會話:")
            print(f"  對話數: {len(loaded_session.conversation_history)}")
            print(f"  變數: {loaded_session.variables}")

    finally:
        # 清理臨時目錄
        shutil.rmtree(temp_dir, ignore_errors=True)


def demonstrate_session_expiration():
    """演示會話過期"""
    print("\n" + "="*60)
    print("示例 4: 會話過期管理")
    print("="*60 + "\n")

    manager = SessionManager(default_ttl=2)  # 2秒過期

    # 創建會話
    session = manager.create_session("user_001")
    session_id = session.metadata.session_id

    print(f"創建會話，過期時間: 2秒")

    # 立即獲取（應該成功）
    result = manager.get_session(session_id)
    print(f"立即訪問: {'成功' if result else '失敗'}")

    # 等待過期
    print("等待 3 秒...")
    time.sleep(3)

    # 再次獲取（應該失敗）
    result = manager.get_session(session_id)
    print(f"過期後訪問: {'成功' if result else '失敗（已過期）'}")


def demonstrate_session_decorator():
    """演示會話裝飾器"""
    print("\n" + "="*60)
    print("示例 5: 會話裝飾器")
    print("="*60 + "\n")

    manager = SessionManager()
    decorator = SessionDecorator(manager)

    # 創建會話
    session = manager.create_session("user_001")
    session_id = session.metadata.session_id

    # 使用裝飾器的函數
    @decorator.auto_persist
    def process_message(session: SessionState, message: str):
        """處理消息並自動持久化"""
        session.add_message("user", message)
        session.add_message("assistant", f"收到: {message}")
        return f"處理完成: {message}"

    # 調用函數
    result = process_message(session_id, "測試消息")
    print(f"結果: {result}")
    print(f"對話數: {len(session.conversation_history)}")


def main():
    """主函數"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*17 + "Session 管理示例" + " "*19 + "║")
    print("╚" + "="*58 + "╝")

    try:
        demonstrate_basic_session()
        demonstrate_multi_session()
        demonstrate_session_persistence()
        demonstrate_session_expiration()
        demonstrate_session_decorator()

        print("\n" + "="*60)
        print("所有示例執行完成！")
        print("="*60)

    except Exception as e:
        logger.error(f"執行錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

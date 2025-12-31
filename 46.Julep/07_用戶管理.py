"""
Julep 用戶和會話管理示例

這個模塊展示了 Julep 平台的用戶和會話管理功能。
包括用戶創建、會話管理、用戶偏好、權限控制和多用戶支持。

主要功能：
1. 用戶創建和管理
2. 會話生命週期管理
3. 用戶偏好設置
4. 權限和角色管理
5. 多用戶並發支持
6. 會話持久化

作者：Julep 示例
日期：2025-12-31
"""

import os
import json
import time
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import uuid
import hashlib


class UserRole(Enum):
    """用戶角色"""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"
    DEVELOPER = "developer"


class SessionStatus(Enum):
    """會話狀態"""
    ACTIVE = "active"
    IDLE = "idle"
    EXPIRED = "expired"
    TERMINATED = "terminated"


@dataclass
class UserPreferences:
    """用戶偏好設置"""
    language: str = "zh-CN"
    timezone: str = "Asia/Shanghai"
    theme: str = "light"
    notifications_enabled: bool = True
    auto_save: bool = True
    custom_settings: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "language": self.language,
            "timezone": self.timezone,
            "theme": self.theme,
            "notifications_enabled": self.notifications_enabled,
            "auto_save": self.auto_save,
            "custom_settings": self.custom_settings
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserPreferences':
        """從字典創建"""
        return cls(
            language=data.get("language", "zh-CN"),
            timezone=data.get("timezone", "Asia/Shanghai"),
            theme=data.get("theme", "light"),
            notifications_enabled=data.get("notifications_enabled", True),
            auto_save=data.get("auto_save", True),
            custom_settings=data.get("custom_settings", {})
        )


class User:
    """用戶類

    表示系統中的一個用戶。
    """

    def __init__(
        self,
        user_id: str,
        name: str,
        email: str,
        role: UserRole = UserRole.USER,
        about: str = "",
        metadata: Optional[Dict] = None
    ):
        """初始化用戶

        Args:
            user_id: 用戶 ID
            name: 用戶名
            email: 郵箱
            role: 用戶角色
            about: 用戶描述
            metadata: 元數據
        """
        self.id = user_id
        self.name = name
        self.email = email
        self.role = role
        self.about = about
        self.metadata = metadata or {}
        self.preferences = UserPreferences()
        self.created_at = datetime.now()
        self.last_active = datetime.now()
        self.session_count = 0
        self.tags: Set[str] = set()

    def update_last_active(self):
        """更新最後活躍時間"""
        self.last_active = datetime.now()

    def add_tag(self, tag: str):
        """添加標籤"""
        self.tags.add(tag)

    def remove_tag(self, tag: str):
        """移除標籤"""
        self.tags.discard(tag)

    def has_permission(self, permission: str) -> bool:
        """檢查權限

        Args:
            permission: 權限名稱

        Returns:
            是否有權限
        """
        # 簡單的權限檢查邏輯
        permissions_by_role = {
            UserRole.ADMIN: {"read", "write", "delete", "manage_users", "manage_system"},
            UserRole.DEVELOPER: {"read", "write", "debug", "deploy"},
            UserRole.USER: {"read", "write"},
            UserRole.GUEST: {"read"}
        }
        return permission in permissions_by_role.get(self.role, set())

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role.value,
            "about": self.about,
            "metadata": self.metadata,
            "preferences": self.preferences.to_dict(),
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat(),
            "session_count": self.session_count,
            "tags": list(self.tags)
        }

    def __repr__(self) -> str:
        return f"User(id={self.id}, name={self.name}, role={self.role.value})"


class Session:
    """會話類

    表示用戶和 Agent 之間的一次會話。
    """

    def __init__(
        self,
        session_id: str,
        user_id: str,
        agent_id: str,
        context: Optional[Dict] = None
    ):
        """初始化會話

        Args:
            session_id: 會話 ID
            user_id: 用戶 ID
            agent_id: Agent ID
            context: 會話上下文
        """
        self.id = session_id
        self.user_id = user_id
        self.agent_id = agent_id
        self.context = context or {}
        self.status = SessionStatus.ACTIVE
        self.created_at = datetime.now()
        self.last_active = datetime.now()
        self.message_count = 0
        self.metadata: Dict[str, Any] = {}

    def update_activity(self):
        """更新活躍時間"""
        self.last_active = datetime.now()
        self.status = SessionStatus.ACTIVE

    def increment_message_count(self):
        """增加消息計數"""
        self.message_count += 1
        self.update_activity()

    def is_expired(self, timeout_minutes: int = 30) -> bool:
        """檢查會話是否過期

        Args:
            timeout_minutes: 超時分鐘數

        Returns:
            是否過期
        """
        if self.status == SessionStatus.TERMINATED:
            return True

        timeout = timedelta(minutes=timeout_minutes)
        elapsed = datetime.now() - self.last_active

        if elapsed > timeout:
            self.status = SessionStatus.EXPIRED
            return True

        return False

    def terminate(self):
        """終止會話"""
        self.status = SessionStatus.TERMINATED

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "agent_id": self.agent_id,
            "context": self.context,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat(),
            "message_count": self.message_count,
            "metadata": self.metadata
        }

    def __repr__(self) -> str:
        return f"Session(id={self.id}, user={self.user_id}, status={self.status.value})"


class UserManager:
    """用戶管理器

    管理所有用戶的創建、更新、查詢和刪除。
    """

    def __init__(self, storage_dir: str = "./users"):
        """初始化管理器

        Args:
            storage_dir: 用戶數據存儲目錄
        """
        self.storage_dir = storage_dir
        self.users: Dict[str, User] = {}
        self.email_index: Dict[str, str] = {}  # email -> user_id

        # 創建存儲目錄
        os.makedirs(storage_dir, exist_ok=True)

    def create_user(
        self,
        name: str,
        email: str,
        role: UserRole = UserRole.USER,
        about: str = "",
        metadata: Optional[Dict] = None
    ) -> User:
        """創建用戶

        Args:
            name: 用戶名
            email: 郵箱
            role: 角色
            about: 描述
            metadata: 元數據

        Returns:
            創建的用戶對象
        """
        # 檢查郵箱是否已存在
        if email in self.email_index:
            raise ValueError(f"郵箱已存在: {email}")

        # 生成用戶 ID
        user_id = f"user_{int(time.time())}_{uuid.uuid4().hex[:8]}"

        # 創建用戶
        user = User(
            user_id=user_id,
            name=name,
            email=email,
            role=role,
            about=about,
            metadata=metadata
        )

        # 存儲用戶
        self.users[user_id] = user
        self.email_index[email] = user_id

        print(f"[SUCCESS] 創建用戶: {name} ({user_id})")
        return user

    def get_user(self, user_id: str) -> Optional[User]:
        """獲取用戶

        Args:
            user_id: 用戶 ID

        Returns:
            用戶對象或 None
        """
        return self.users.get(user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """通過郵箱獲取用戶

        Args:
            email: 郵箱地址

        Returns:
            用戶對象或 None
        """
        user_id = self.email_index.get(email)
        if user_id:
            return self.users.get(user_id)
        return None

    def update_user(self, user_id: str, **kwargs) -> bool:
        """更新用戶信息

        Args:
            user_id: 用戶 ID
            **kwargs: 要更新的字段

        Returns:
            是否成功
        """
        user = self.users.get(user_id)
        if not user:
            return False

        # 更新字段
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)

        print(f"[INFO] 更新用戶: {user_id}")
        return True

    def delete_user(self, user_id: str) -> bool:
        """刪除用戶

        Args:
            user_id: 用戶 ID

        Returns:
            是否成功
        """
        user = self.users.get(user_id)
        if not user:
            return False

        # 從索引中移除
        if user.email in self.email_index:
            del self.email_index[user.email]

        # 刪除用戶
        del self.users[user_id]

        print(f"[INFO] 刪除用戶: {user_id}")
        return True

    def list_users(
        self,
        role: Optional[UserRole] = None,
        tag: Optional[str] = None
    ) -> List[User]:
        """列出用戶

        Args:
            role: 按角色篩選
            tag: 按標籤篩選

        Returns:
            用戶列表
        """
        users = list(self.users.values())

        if role:
            users = [u for u in users if u.role == role]

        if tag:
            users = [u for u in users if tag in u.tags]

        return users

    def save_user(self, user_id: str):
        """保存用戶到磁盤

        Args:
            user_id: 用戶 ID
        """
        user = self.users.get(user_id)
        if not user:
            return

        filepath = os.path.join(self.storage_dir, f"{user_id}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(user.to_dict(), f, ensure_ascii=False, indent=2)

        print(f"[INFO] 用戶已保存: {filepath}")

    def load_user(self, user_id: str) -> Optional[User]:
        """從磁盤加載用戶

        Args:
            user_id: 用戶 ID

        Returns:
            用戶對象或 None
        """
        filepath = os.path.join(self.storage_dir, f"{user_id}.json")
        if not os.path.exists(filepath):
            return None

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 重建用戶對象
        user = User(
            user_id=data["id"],
            name=data["name"],
            email=data["email"],
            role=UserRole(data["role"]),
            about=data.get("about", ""),
            metadata=data.get("metadata", {})
        )

        user.preferences = UserPreferences.from_dict(data.get("preferences", {}))
        user.created_at = datetime.fromisoformat(data["created_at"])
        user.last_active = datetime.fromisoformat(data["last_active"])
        user.session_count = data.get("session_count", 0)
        user.tags = set(data.get("tags", []))

        self.users[user_id] = user
        self.email_index[user.email] = user_id

        print(f"[INFO] 用戶已加載: {user_id}")
        return user


class SessionManager:
    """會話管理器

    管理用戶會話的創建、更新和清理。
    """

    def __init__(self, user_manager: UserManager):
        """初始化管理器

        Args:
            user_manager: 用戶管理器
        """
        self.user_manager = user_manager
        self.sessions: Dict[str, Session] = {}
        self.user_sessions: Dict[str, List[str]] = {}  # user_id -> [session_ids]

    def create_session(
        self,
        user_id: str,
        agent_id: str,
        context: Optional[Dict] = None
    ) -> Session:
        """創建會話

        Args:
            user_id: 用戶 ID
            agent_id: Agent ID
            context: 初始上下文

        Returns:
            創建的會話
        """
        # 檢查用戶是否存在
        user = self.user_manager.get_user(user_id)
        if not user:
            raise ValueError(f"用戶不存在: {user_id}")

        # 生成會話 ID
        session_id = f"session_{int(time.time())}_{uuid.uuid4().hex[:8]}"

        # 創建會話
        session = Session(
            session_id=session_id,
            user_id=user_id,
            agent_id=agent_id,
            context=context
        )

        # 存儲會話
        self.sessions[session_id] = session

        # 更新用戶會話索引
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = []
        self.user_sessions[user_id].append(session_id)

        # 更新用戶統計
        user.session_count += 1
        user.update_last_active()

        print(f"[SUCCESS] 創建會話: {session_id} (用戶: {user.name})")
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """獲取會話"""
        return self.sessions.get(session_id)

    def get_user_sessions(self, user_id: str) -> List[Session]:
        """獲取用戶的所有會話

        Args:
            user_id: 用戶 ID

        Returns:
            會話列表
        """
        session_ids = self.user_sessions.get(user_id, [])
        return [self.sessions[sid] for sid in session_ids if sid in self.sessions]

    def get_active_sessions(self, user_id: Optional[str] = None) -> List[Session]:
        """獲取活躍會話

        Args:
            user_id: 用戶 ID（可選，篩選特定用戶）

        Returns:
            活躍會話列表
        """
        sessions = list(self.sessions.values())

        if user_id:
            sessions = [s for s in sessions if s.user_id == user_id]

        return [s for s in sessions if not s.is_expired()]

    def terminate_session(self, session_id: str):
        """終止會話

        Args:
            session_id: 會話 ID
        """
        session = self.sessions.get(session_id)
        if session:
            session.terminate()
            print(f"[INFO] 終止會話: {session_id}")

    def cleanup_expired_sessions(self, timeout_minutes: int = 30):
        """清理過期會話

        Args:
            timeout_minutes: 超時分鐘數
        """
        expired = []
        for session_id, session in self.sessions.items():
            if session.is_expired(timeout_minutes):
                expired.append(session_id)

        for session_id in expired:
            del self.sessions[session_id]

        print(f"[INFO] 清理了 {len(expired)} 個過期會話")

    def get_stats(self) -> Dict[str, Any]:
        """獲取統計信息"""
        total_sessions = len(self.sessions)
        active_sessions = len(self.get_active_sessions())

        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "expired_sessions": total_sessions - active_sessions
        }


def demo_user_management():
    """用戶管理示例"""
    print("\n" + "="*60)
    print("示例 1: 用戶管理")
    print("="*60)

    manager = UserManager()

    # 創建不同角色的用戶
    admin = manager.create_user(
        name="管理員",
        email="admin@example.com",
        role=UserRole.ADMIN,
        about="系統管理員"
    )

    developer = manager.create_user(
        name="開發者張三",
        email="zhang@example.com",
        role=UserRole.DEVELOPER,
        about="後端開發工程師"
    )

    user = manager.create_user(
        name="普通用戶李四",
        email="li@example.com",
        role=UserRole.USER
    )

    # 添加標籤
    developer.add_tag("backend")
    developer.add_tag("python")
    user.add_tag("premium")

    # 列出用戶
    print(f"\n所有用戶:")
    for u in manager.list_users():
        print(f"  - {u.name} ({u.role.value})")

    # 按角色篩選
    print(f"\n開發者:")
    for u in manager.list_users(role=UserRole.DEVELOPER):
        print(f"  - {u.name}")

    # 按標籤篩選
    print(f"\n帶 'python' 標籤的用戶:")
    for u in manager.list_users(tag="python"):
        print(f"  - {u.name}")


def demo_session_management():
    """會話管理示例"""
    print("\n" + "="*60)
    print("示例 2: 會話管理")
    print("="*60)

    user_manager = UserManager()
    session_manager = SessionManager(user_manager)

    # 創建用戶
    user1 = user_manager.create_user("用戶1", "user1@example.com")
    user2 = user_manager.create_user("用戶2", "user2@example.com")

    # 為用戶創建多個會話
    session1 = session_manager.create_session(user1.id, "agent_001")
    session2 = session_manager.create_session(user1.id, "agent_002")
    session3 = session_manager.create_session(user2.id, "agent_001")

    # 模擬會話活動
    for i in range(3):
        session1.increment_message_count()
        time.sleep(0.1)

    # 查看用戶會話
    print(f"\n用戶1 的會話:")
    for session in session_manager.get_user_sessions(user1.id):
        print(f"  - {session.id}: {session.message_count} 條消息")

    # 查看活躍會話
    print(f"\n活躍會話數: {len(session_manager.get_active_sessions())}")

    # 統計信息
    stats = session_manager.get_stats()
    print(f"\n會話統計:")
    for key, value in stats.items():
        print(f"  {key}: {value}")


def demo_user_preferences():
    """用戶偏好設置示例"""
    print("\n" + "="*60)
    print("示例 3: 用戶偏好設置")
    print("="*60)

    manager = UserManager()

    # 創建用戶
    user = manager.create_user("張三", "zhang@example.com")

    # 設置偏好
    user.preferences.language = "en-US"
    user.preferences.theme = "dark"
    user.preferences.custom_settings = {
        "font_size": 14,
        "code_theme": "monokai",
        "auto_complete": True
    }

    print(f"\n用戶偏好設置:")
    prefs = user.preferences.to_dict()
    for key, value in prefs.items():
        print(f"  {key}: {value}")

    # 保存和加載
    manager.save_user(user.id)
    manager.users.clear()  # 清空內存

    loaded_user = manager.load_user(user.id)
    print(f"\n加載的用戶偏好:")
    print(f"  語言: {loaded_user.preferences.language}")
    print(f"  主題: {loaded_user.preferences.theme}")


def demo_permission_check():
    """權限檢查示例"""
    print("\n" + "="*60)
    print("示例 4: 權限檢查")
    print("="*60)

    manager = UserManager()

    # 創建不同角色的用戶
    admin = manager.create_user("管理員", "admin@example.com", UserRole.ADMIN)
    dev = manager.create_user("開發者", "dev@example.com", UserRole.DEVELOPER)
    user = manager.create_user("用戶", "user@example.com", UserRole.USER)
    guest = manager.create_user("訪客", "guest@example.com", UserRole.GUEST)

    # 檢查權限
    permissions = ["read", "write", "delete", "manage_users", "debug"]

    print(f"\n權限檢查:")
    print(f"{'用戶':12} | " + " | ".join(f"{p:12}" for p in permissions))
    print("-" * 80)

    for u in [admin, dev, user, guest]:
        perms = [u.has_permission(p) for p in permissions]
        perm_str = " | ".join(f"{'✓' if p else '✗':^12}" for p in perms)
        print(f"{u.name:12} | {perm_str}")


def demo_multi_user_concurrent():
    """多用戶並發示例"""
    print("\n" + "="*60)
    print("示例 5: 多用戶並發會話")
    print("="*60)

    user_manager = UserManager()
    session_manager = SessionManager(user_manager)

    # 創建多個用戶
    users = []
    for i in range(5):
        user = user_manager.create_user(
            name=f"用戶{i+1}",
            email=f"user{i+1}@example.com"
        )
        users.append(user)

    # 為每個用戶創建會話
    print(f"\n創建並發會話:")
    for user in users:
        session = session_manager.create_session(user.id, "agent_001")
        # 模擬消息交互
        for _ in range(3):
            session.increment_message_count()

    # 查看統計
    stats = session_manager.get_stats()
    print(f"\n系統統計:")
    print(f"  總用戶數: {len(user_manager.users)}")
    print(f"  總會話數: {stats['total_sessions']}")
    print(f"  活躍會話數: {stats['active_sessions']}")

    # 查看每個用戶的會話數
    print(f"\n用戶會話分佈:")
    for user in users:
        sessions = session_manager.get_user_sessions(user.id)
        print(f"  {user.name}: {len(sessions)} 個會話")


def main():
    """主函數"""
    print("="*60)
    print("Julep 用戶和會話管理示例")
    print("="*60)

    try:
        demo_user_management()
        demo_session_management()
        demo_user_preferences()
        demo_permission_check()
        demo_multi_user_concurrent()

        print("\n" + "="*60)
        print("所有示例執行完成！")
        print("="*60)

    except Exception as e:
        print(f"\n[ERROR] 執行出錯: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

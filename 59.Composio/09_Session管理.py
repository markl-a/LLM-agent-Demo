#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Composio Session 管理範例
=========================

本範例展示 Composio 的 Session 管理和路由功能，包括：
1. Session 基礎概念
2. Session 創建和管理
3. Session-based 路由
4. 多用戶隔離
5. Session 狀態追蹤
6. 最佳實踐
7. 實際應用場景

Session 管理讓您可以為不同用戶或上下文維護獨立的連接和狀態。

作者: Composio 團隊
日期: 2025-01-01
"""

import os
import sys
import json
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 導入 Composio SDK
try:
    from composio import Composio, App
    from composio.client.exceptions import ComposioException
except ImportError as e:
    print("錯誤：請先安裝 Composio SDK")
    print("執行: pip install composio-core")
    sys.exit(1)


@dataclass
class Session:
    """
    Session 數據類別

    表示一個用戶會話
    """
    session_id: str
    user_id: str
    entity_id: str
    created_at: datetime
    last_active: datetime
    metadata: Dict[str, Any]
    is_active: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['last_active'] = self.last_active.isoformat()
        return data

    def update_activity(self):
        """更新最後活動時間"""
        self.last_active = datetime.now()


class SessionManager:
    """
    Session 管理器

    管理用戶會話的創建、追蹤和清理
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化 Session 管理器

        Args:
            api_key: Composio API 金鑰
        """
        print("=" * 70)
        print("初始化 Session 管理器")
        print("=" * 70)

        self.api_key = api_key or os.getenv("COMPOSIO_API_KEY")

        try:
            # 初始化 Composio 客戶端
            self.client = Composio(api_key=self.api_key)
            print("✓ Composio 客戶端初始化成功")

            # Session 儲存
            self.sessions: Dict[str, Session] = {}

            # Entity 映射
            self.user_to_entity: Dict[str, str] = {}

        except Exception as e:
            print(f"✗ 初始化失敗: {e}")
            raise

    def create_session(self, user_id: str, metadata: Optional[Dict] = None) -> Session:
        """
        創建新的用戶會話

        Args:
            user_id: 用戶 ID
            metadata: 會話元數據

        Returns:
            Session 對象
        """
        print("\n" + "=" * 70)
        print(f"創建 Session: 用戶 {user_id}")
        print("=" * 70)

        # 生成唯一的 Session ID
        session_id = str(uuid.uuid4())

        # 為用戶創建或獲取 Entity ID
        entity_id = self._get_or_create_entity(user_id)

        # 創建 Session
        session = Session(
            session_id=session_id,
            user_id=user_id,
            entity_id=entity_id,
            created_at=datetime.now(),
            last_active=datetime.now(),
            metadata=metadata or {}
        )

        # 保存 Session
        self.sessions[session_id] = session

        print(f"✓ Session 創建成功")
        print(f"  Session ID: {session_id}")
        print(f"  Entity ID: {entity_id}")
        print(f"  用戶 ID: {user_id}")

        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """
        獲取 Session

        Args:
            session_id: Session ID

        Returns:
            Session 對象或 None
        """
        session = self.sessions.get(session_id)

        if session:
            # 更新最後活動時間
            session.update_activity()

        return session

    def list_sessions(self, user_id: Optional[str] = None,
                     active_only: bool = True) -> List[Session]:
        """
        列出會話

        Args:
            user_id: 過濾特定用戶（可選）
            active_only: 只顯示活躍會話

        Returns:
            Session 列表
        """
        print("\n" + "=" * 70)
        print("列出會話")
        print("=" * 70)

        sessions = list(self.sessions.values())

        # 過濾
        if user_id:
            sessions = [s for s in sessions if s.user_id == user_id]

        if active_only:
            sessions = [s for s in sessions if s.is_active]

        print(f"\n找到 {len(sessions)} 個會話:")
        print("-" * 70)

        for i, session in enumerate(sessions, 1):
            print(f"{i}. Session ID: {session.session_id[:8]}...")
            print(f"   用戶: {session.user_id}")
            print(f"   狀態: {'活躍' if session.is_active else '非活躍'}")
            print(f"   最後活動: {session.last_active.strftime('%Y-%m-%d %H:%M:%S')}")
            print()

        return sessions

    def end_session(self, session_id: str) -> bool:
        """
        結束會話

        Args:
            session_id: Session ID

        Returns:
            是否成功
        """
        print("\n" + "=" * 70)
        print(f"結束 Session: {session_id}")
        print("=" * 70)

        session = self.sessions.get(session_id)

        if not session:
            print(f"✗ Session 不存在")
            return False

        session.is_active = False
        print(f"✓ Session 已結束")

        return True

    def cleanup_inactive_sessions(self, timeout_minutes: int = 30) -> int:
        """
        清理不活躍的會話

        Args:
            timeout_minutes: 超時時間（分鐘）

        Returns:
            清理的會話數量
        """
        print("\n" + "=" * 70)
        print(f"清理不活躍會話（超時: {timeout_minutes} 分鐘）")
        print("=" * 70)

        timeout = timedelta(minutes=timeout_minutes)
        now = datetime.now()
        cleaned = 0

        for session_id, session in list(self.sessions.items()):
            if session.is_active and (now - session.last_active) > timeout:
                session.is_active = False
                cleaned += 1

        print(f"✓ 清理了 {cleaned} 個不活躍會話")

        return cleaned

    def _get_or_create_entity(self, user_id: str) -> str:
        """
        獲取或創建用戶的 Entity

        Args:
            user_id: 用戶 ID

        Returns:
            Entity ID
        """
        # 檢查是否已存在 Entity
        if user_id in self.user_to_entity:
            return self.user_to_entity[user_id]

        # 創建新的 Entity ID
        entity_id = f"user_{user_id}"

        try:
            # 在 Composio 中創建 Entity
            entity = self.client.get_entity(id=entity_id)
            self.user_to_entity[user_id] = entity_id

            return entity_id

        except Exception as e:
            print(f"警告：創建 Entity 時出錯: {e}")
            return entity_id


class SessionBasedRouter:
    """
    基於 Session 的路由器

    根據 Session 路由請求到正確的 Entity
    """

    def __init__(self, session_manager: SessionManager):
        """
        初始化路由器

        Args:
            session_manager: Session 管理器
        """
        self.session_manager = session_manager
        print("\n✓ Session 路由器初始化成功")

    def execute_action(self, session_id: str, action_name: str,
                      params: Dict[str, Any]) -> Dict[str, Any]:
        """
        執行動作（帶 Session 路由）

        Args:
            session_id: Session ID
            action_name: 動作名稱
            params: 動作參數

        Returns:
            執行結果
        """
        print("\n" + "=" * 70)
        print(f"執行動作（Session 路由）")
        print("=" * 70)

        # 獲取 Session
        session = self.session_manager.get_session(session_id)

        if not session:
            return {
                "success": False,
                "error": "Session 不存在或已過期"
            }

        if not session.is_active:
            return {
                "success": False,
                "error": "Session 已結束"
            }

        print(f"Session ID: {session_id}")
        print(f"用戶 ID: {session.user_id}")
        print(f"Entity ID: {session.entity_id}")
        print(f"動作: {action_name}")

        try:
            # 獲取 Entity
            entity = self.session_manager.client.get_entity(id=session.entity_id)

            # 執行動作
            result = entity.execute(
                action=action_name,
                params=params
            )

            # 更新會話活動時間
            session.update_activity()

            print(f"\n✓ 動作執行成功")

            return {
                "success": True,
                "data": result,
                "session_id": session_id
            }

        except Exception as e:
            print(f"\n✗ 執行失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id
            }

    def get_user_connections(self, session_id: str, app_name: str) -> List[Dict[str, Any]]:
        """
        獲取用戶的應用連接

        Args:
            session_id: Session ID
            app_name: 應用名稱

        Returns:
            連接列表
        """
        print("\n" + "=" * 70)
        print(f"獲取用戶連接: {app_name}")
        print("=" * 70)

        # 獲取 Session
        session = self.session_manager.get_session(session_id)

        if not session:
            print("✗ Session 不存在")
            return []

        try:
            # 獲取 Entity
            entity = self.session_manager.client.get_entity(id=session.entity_id)

            # 獲取連接
            connections = entity.get_connections(app_name=app_name)

            print(f"✓ 找到 {len(connections)} 個連接")

            return [
                {
                    "id": conn.id,
                    "app": conn.appName,
                    "status": conn.status
                }
                for conn in connections
            ]

        except Exception as e:
            print(f"✗ 獲取連接失敗: {e}")
            return []


class MultiTenantManager:
    """
    多租戶管理器

    管理多租戶環境中的用戶和會話
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化多租戶管理器

        Args:
            api_key: Composio API 金鑰
        """
        print("\n" + "=" * 70)
        print("初始化多租戶管理器")
        print("=" * 70)

        self.session_manager = SessionManager(api_key=api_key)
        self.router = SessionBasedRouter(self.session_manager)

        # 租戶到用戶的映射
        self.tenant_users: Dict[str, List[str]] = {}

    def register_user(self, tenant_id: str, user_id: str,
                     user_metadata: Optional[Dict] = None) -> str:
        """
        註冊用戶到租戶

        Args:
            tenant_id: 租戶 ID
            user_id: 用戶 ID
            user_metadata: 用戶元數據

        Returns:
            Session ID
        """
        print("\n" + "=" * 70)
        print(f"註冊用戶: {user_id} 到租戶 {tenant_id}")
        print("=" * 70)

        # 添加到租戶用戶列表
        if tenant_id not in self.tenant_users:
            self.tenant_users[tenant_id] = []

        if user_id not in self.tenant_users[tenant_id]:
            self.tenant_users[tenant_id].append(user_id)

        # 創建會話
        metadata = user_metadata or {}
        metadata['tenant_id'] = tenant_id

        session = self.session_manager.create_session(
            user_id=user_id,
            metadata=metadata
        )

        print(f"✓ 用戶註冊成功")

        return session.session_id

    def list_tenant_users(self, tenant_id: str) -> List[str]:
        """
        列出租戶的用戶

        Args:
            tenant_id: 租戶 ID

        Returns:
            用戶 ID 列表
        """
        print("\n" + "=" * 70)
        print(f"列出租戶 {tenant_id} 的用戶")
        print("=" * 70)

        users = self.tenant_users.get(tenant_id, [])

        print(f"\n找到 {len(users)} 個用戶:")
        for i, user_id in enumerate(users, 1):
            print(f"{i}. {user_id}")

        return users

    def get_tenant_stats(self, tenant_id: str) -> Dict[str, Any]:
        """
        獲取租戶統計資訊

        Args:
            tenant_id: 租戶 ID

        Returns:
            統計資訊
        """
        print("\n" + "=" * 70)
        print(f"獲取租戶統計: {tenant_id}")
        print("=" * 70)

        users = self.tenant_users.get(tenant_id, [])

        # 獲取租戶的所有會話
        all_sessions = self.session_manager.list_sessions(active_only=False)
        tenant_sessions = [
            s for s in all_sessions
            if s.metadata.get('tenant_id') == tenant_id
        ]

        active_sessions = [s for s in tenant_sessions if s.is_active]

        stats = {
            "tenant_id": tenant_id,
            "total_users": len(users),
            "total_sessions": len(tenant_sessions),
            "active_sessions": len(active_sessions),
            "inactive_sessions": len(tenant_sessions) - len(active_sessions)
        }

        print(f"\n租戶統計:")
        print("-" * 70)
        for key, value in stats.items():
            print(f"  {key}: {value}")

        return stats


def demo_basic_session():
    """
    演示基礎 Session 管理
    """
    print("\n" + "=" * 80)
    print("基礎 Session 管理演示")
    print("=" * 80)

    try:
        # 創建 Session 管理器
        manager = SessionManager()

        # 創建會話
        session1 = manager.create_session(
            user_id="user_001",
            metadata={"role": "admin"}
        )

        session2 = manager.create_session(
            user_id="user_002",
            metadata={"role": "developer"}
        )

        # 列出會話
        manager.list_sessions()

        # 獲取會話
        session = manager.get_session(session1.session_id)
        print(f"\n獲取的會話: {session.session_id}")

        # 結束會話
        manager.end_session(session2.session_id)

        # 再次列出會話
        manager.list_sessions(active_only=True)

    except Exception as e:
        print(f"\n演示過程中發生錯誤: {e}")


def demo_session_routing():
    """
    演示 Session 路由
    """
    print("\n" + "=" * 80)
    print("Session 路由演示")
    print("=" * 80)

    print("""
Session 路由的優勢：
------------------

1. 用戶隔離
   - 每個用戶有獨立的 Entity
   - 連接和資料完全隔離
   - 安全性和隱私保護

2. 上下文管理
   - 維護用戶會話狀態
   - 追蹤用戶活動
   - 個性化體驗

3. 多租戶支援
   - 同一應用服務多個租戶
   - 資源隔離
   - 獨立計費和配額

4. 會話生命週期
   - 自動清理不活躍會話
   - 會話超時管理
   - 資源釋放

使用範例：
--------
# 創建會話
session_id = manager.create_session("user_123")

# 執行操作（自動路由到用戶的 Entity）
result = router.execute_action(
    session_id=session_id,
    action_name="GITHUB_LIST_REPOS",
    params={}
)

# 每個用戶看到的是自己的倉庫
# 不會看到其他用戶的資料
    """)


def demo_multi_tenant():
    """
    演示多租戶管理
    """
    print("\n" + "=" * 80)
    print("多租戶管理演示")
    print("=" * 80)

    try:
        # 創建多租戶管理器
        mt_manager = MultiTenantManager()

        # 註冊用戶到不同租戶
        print("\n註冊用戶到租戶:")
        print("-" * 80)

        session1 = mt_manager.register_user(
            tenant_id="company_a",
            user_id="alice",
            user_metadata={"department": "engineering"}
        )

        session2 = mt_manager.register_user(
            tenant_id="company_a",
            user_id="bob",
            user_metadata={"department": "sales"}
        )

        session3 = mt_manager.register_user(
            tenant_id="company_b",
            user_id="charlie",
            user_metadata={"department": "marketing"}
        )

        # 列出租戶用戶
        mt_manager.list_tenant_users("company_a")
        mt_manager.list_tenant_users("company_b")

        # 獲取租戶統計
        mt_manager.get_tenant_stats("company_a")
        mt_manager.get_tenant_stats("company_b")

    except Exception as e:
        print(f"\n演示過程中發生錯誤: {e}")


def print_best_practices():
    """
    印出最佳實踐
    """
    print("\n" + "=" * 80)
    print("Session 管理最佳實踐")
    print("=" * 80)

    practices = [
        ("1. Session 安全", [
            "使用安全的 Session ID（UUID）",
            "實施 Session 超時",
            "加密敏感的 Session 數據",
            "驗證 Session 有效性"
        ]),
        ("2. 資源管理", [
            "定期清理不活躍會話",
            "設置合理的超時時間",
            "限制每個用戶的會話數量",
            "監控資源使用"
        ]),
        ("3. 多租戶隔離", [
            "嚴格的數據隔離",
            "獨立的 Entity 管理",
            "租戶級別的配額",
            "審計和日誌記錄"
        ]),
        ("4. 性能優化", [
            "快取 Session 數據",
            "使用數據庫存儲持久化會話",
            "實施 Session 池",
            "異步清理過期會話"
        ]),
        ("5. 錯誤處理", [
            "處理 Session 過期",
            "優雅的降級",
            "清晰的錯誤訊息",
            "自動重新建立會話"
        ])
    ]

    for title, items in practices:
        print(f"\n{title}")
        print("-" * 80)
        for item in items:
            print(f"  • {item}")


def main():
    """
    主函數
    """
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║              Composio Session 管理範例                           ║
    ║                                                                  ║
    ║              安全、可擴展的用戶會話管理                          ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)

    # 演示基礎 Session
    demo_basic_session()

    # 演示 Session 路由
    demo_session_routing()

    # 演示多租戶
    demo_multi_tenant()

    # 印出最佳實踐
    print_best_practices()

    print("\n" + "=" * 80)
    print("Session 管理的重要性:")
    print("  • 用戶隔離和安全")
    print("  • 多租戶支援")
    print("  • 狀態管理")
    print("  • 資源優化")
    print("  • 可擴展性")
    print("=" * 80)


if __name__ == "__main__":
    main()

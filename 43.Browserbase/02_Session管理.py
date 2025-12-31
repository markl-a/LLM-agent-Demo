"""
Browserbase Session 管理示例
============================

本模塊展示了 Browserbase Session 的高級管理功能。
包括 Session 創建、持久化、復用、清理和監控。

主要內容:
1. Session 生命週期管理
2. 持久化 Session 和狀態保持
3. Session 池管理
4. Session 監控和統計
5. 自動清理和回收機制
6. Session 快照和恢復

作者: Browserbase 示例團隊
日期: 2025-12-31
"""

import os
import time
import json
import threading
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict
from dotenv import load_dotenv


# 加載環境變量
load_dotenv()


class SessionStatus(Enum):
    """Session 狀態枚舉"""
    PENDING = "pending"      # 待創建
    RUNNING = "running"      # 運行中
    IDLE = "idle"           # 閒置
    PAUSED = "paused"       # 暫停
    STOPPED = "stopped"     # 已停止
    ERROR = "error"         # 錯誤


@dataclass
class SessionConfig:
    """Session 配置類"""
    stealth: bool = True                # 隱身模式
    proxy: bool = False                 # 使用代理
    keep_alive: bool = False            # 持久化
    timeout: int = 300                  # 超時時間（秒）
    max_idle_time: int = 60            # 最大閒置時間（秒）
    viewport: Dict[str, int] = field(default_factory=lambda: {"width": 1920, "height": 1080})
    user_agent: Optional[str] = None    # 自定義 User-Agent
    cookies: List[Dict] = field(default_factory=list)  # 預設 Cookie
    locale: str = "zh-TW"              # 語言設置
    timezone: str = "Asia/Taipei"      # 時區設置


@dataclass
class Session:
    """Session 數據類"""
    id: str
    project_id: str
    status: SessionStatus
    config: SessionConfig
    created_at: datetime
    last_used_at: datetime
    usage_count: int = 0
    total_duration: float = 0.0  # 總使用時長（秒）
    error_count: int = 0
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """轉換為字典"""
        data = asdict(self)
        data['status'] = self.status.value
        data['created_at'] = self.created_at.isoformat()
        data['last_used_at'] = self.last_used_at.isoformat()
        return data


class SessionManager:
    """
    Session 管理器

    提供完整的 Session 生命週期管理功能，
    包括創建、復用、監控、清理等。
    """

    def __init__(self, project_id: str, max_sessions: int = 10):
        """
        初始化 Session 管理器

        Args:
            project_id: 項目 ID
            max_sessions: 最大 Session 數量
        """
        self.project_id = project_id
        self.max_sessions = max_sessions
        self.sessions: Dict[str, Session] = {}
        self.session_lock = threading.Lock()
        self.stats = defaultdict(int)

        print(f"[SessionManager] 初始化完成 (max_sessions={max_sessions})")

    def create_session(
        self,
        config: Optional[SessionConfig] = None,
        session_id: Optional[str] = None
    ) -> Session:
        """
        創建新的 Session

        Args:
            config: Session 配置
            session_id: 自定義 Session ID（可選）

        Returns:
            創建的 Session 對象

        Raises:
            RuntimeError: 當 Session 數量超過限制時
        """
        with self.session_lock:
            # 檢查數量限制
            if len(self.sessions) >= self.max_sessions:
                raise RuntimeError(f"Session 數量已達上限: {self.max_sessions}")

            # 生成 Session ID
            if session_id is None:
                session_id = f"session_{int(time.time() * 1000)}"

            # 使用默認配置
            if config is None:
                config = SessionConfig()

            # 創建 Session
            now = datetime.now()
            session = Session(
                id=session_id,
                project_id=self.project_id,
                status=SessionStatus.RUNNING,
                config=config,
                created_at=now,
                last_used_at=now
            )

            self.sessions[session_id] = session
            self.stats['total_created'] += 1
            self.stats['active_sessions'] = len(self.sessions)

            print(f"[SessionManager] Session 創建成功: {session_id}")
            return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """
        獲取 Session

        Args:
            session_id: Session ID

        Returns:
            Session 對象，不存在則返回 None
        """
        return self.sessions.get(session_id)

    def update_session_status(
        self,
        session_id: str,
        status: SessionStatus
    ) -> bool:
        """
        更新 Session 狀態

        Args:
            session_id: Session ID
            status: 新狀態

        Returns:
            是否成功更新
        """
        session = self.get_session(session_id)
        if session:
            old_status = session.status
            session.status = status
            session.last_used_at = datetime.now()
            print(f"[SessionManager] Session {session_id} 狀態變更: {old_status.value} -> {status.value}")
            return True
        return False

    def use_session(self, session_id: str) -> bool:
        """
        使用 Session（更新使用計數和時間）

        Args:
            session_id: Session ID

        Returns:
            是否成功
        """
        session = self.get_session(session_id)
        if session:
            session.usage_count += 1
            session.last_used_at = datetime.now()
            self.stats['total_uses'] += 1
            print(f"[SessionManager] Session {session_id} 使用次數: {session.usage_count}")
            return True
        return False

    def delete_session(self, session_id: str) -> bool:
        """
        刪除 Session

        Args:
            session_id: Session ID

        Returns:
            是否成功刪除
        """
        with self.session_lock:
            if session_id in self.sessions:
                session = self.sessions.pop(session_id)
                self.stats['total_deleted'] += 1
                self.stats['active_sessions'] = len(self.sessions)
                print(f"[SessionManager] Session 已刪除: {session_id}")
                print(f"  - 使用次數: {session.usage_count}")
                print(f"  - 總時長: {session.total_duration:.2f}秒")
                return True
        return False

    def cleanup_idle_sessions(self, max_idle_seconds: int = 300) -> int:
        """
        清理閒置的 Session

        Args:
            max_idle_seconds: 最大閒置時間（秒）

        Returns:
            清理的 Session 數量
        """
        print(f"[SessionManager] 開始清理閒置 Session (閒置時間 > {max_idle_seconds}秒)")

        now = datetime.now()
        to_delete = []

        for session_id, session in self.sessions.items():
            idle_time = (now - session.last_used_at).total_seconds()
            if idle_time > max_idle_seconds:
                to_delete.append(session_id)
                print(f"  - {session_id} 閒置 {idle_time:.0f}秒，準備刪除")

        for session_id in to_delete:
            self.delete_session(session_id)

        print(f"[SessionManager] 清理完成，共刪除 {len(to_delete)} 個 Session")
        return len(to_delete)

    def get_statistics(self) -> Dict:
        """
        獲取統計信息

        Returns:
            統計信息字典
        """
        stats = dict(self.stats)
        stats['active_sessions'] = len(self.sessions)

        # 計算平均使用次數
        if self.sessions:
            total_uses = sum(s.usage_count for s in self.sessions.values())
            stats['avg_usage_per_session'] = total_uses / len(self.sessions)

        return stats

    def list_sessions(
        self,
        status: Optional[SessionStatus] = None
    ) -> List[Session]:
        """
        列出所有 Session

        Args:
            status: 過濾狀態（可選）

        Returns:
            Session 列表
        """
        sessions = list(self.sessions.values())

        if status:
            sessions = [s for s in sessions if s.status == status]

        return sessions


class SessionPool:
    """
    Session 池

    管理一組可復用的 Session，自動創建、復用和清理。
    適用於需要頻繁創建 Session 的場景。
    """

    def __init__(
        self,
        manager: SessionManager,
        pool_size: int = 5,
        config: Optional[SessionConfig] = None
    ):
        """
        初始化 Session 池

        Args:
            manager: Session 管理器
            pool_size: 池大小
            config: 默認 Session 配置
        """
        self.manager = manager
        self.pool_size = pool_size
        self.default_config = config or SessionConfig(keep_alive=True)
        self.available_sessions: List[str] = []
        self.in_use_sessions: Dict[str, datetime] = {}
        self.pool_lock = threading.Lock()

        print(f"[SessionPool] 初始化 Session 池 (大小={pool_size})")
        self._initialize_pool()

    def _initialize_pool(self):
        """初始化池中的 Session"""
        for i in range(self.pool_size):
            session = self.manager.create_session(config=self.default_config)
            self.available_sessions.append(session.id)
            print(f"[SessionPool] 預創建 Session {i + 1}/{self.pool_size}: {session.id}")

    def acquire(self, timeout: int = 30) -> Optional[str]:
        """
        從池中獲取一個 Session

        Args:
            timeout: 超時時間（秒）

        Returns:
            Session ID，如果超時則返回 None
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            with self.pool_lock:
                if self.available_sessions:
                    session_id = self.available_sessions.pop(0)
                    self.in_use_sessions[session_id] = datetime.now()
                    self.manager.use_session(session_id)
                    print(f"[SessionPool] 獲取 Session: {session_id}")
                    return session_id

            # 如果沒有可用的，等待一下
            time.sleep(0.1)

        print(f"[SessionPool] 獲取 Session 超時")
        return None

    def release(self, session_id: str):
        """
        釋放 Session 回池中

        Args:
            session_id: Session ID
        """
        with self.pool_lock:
            if session_id in self.in_use_sessions:
                use_time = (datetime.now() - self.in_use_sessions[session_id]).total_seconds()
                del self.in_use_sessions[session_id]
                self.available_sessions.append(session_id)
                print(f"[SessionPool] 釋放 Session: {session_id} (使用時長: {use_time:.2f}秒)")

    def get_pool_status(self) -> Dict:
        """
        獲取池狀態

        Returns:
            狀態信息字典
        """
        return {
            "pool_size": self.pool_size,
            "available": len(self.available_sessions),
            "in_use": len(self.in_use_sessions),
            "utilization": len(self.in_use_sessions) / self.pool_size * 100
        }


class SessionSnapshot:
    """Session 快照管理"""

    def __init__(self):
        """初始化快照管理器"""
        self.snapshots: Dict[str, Dict] = {}
        print("[SessionSnapshot] 快照管理器初始化")

    def create_snapshot(self, session: Session, name: str) -> bool:
        """
        創建 Session 快照

        Args:
            session: Session 對象
            name: 快照名稱

        Returns:
            是否成功
        """
        snapshot_data = {
            "session_data": session.to_dict(),
            "timestamp": datetime.now().isoformat(),
            "cookies": session.config.cookies.copy(),
            "metadata": session.metadata.copy()
        }

        self.snapshots[name] = snapshot_data
        print(f"[SessionSnapshot] 創建快照: {name} (Session: {session.id})")
        return True

    def restore_snapshot(
        self,
        name: str,
        manager: SessionManager
    ) -> Optional[Session]:
        """
        從快照恢復 Session

        Args:
            name: 快照名稱
            manager: Session 管理器

        Returns:
            恢復的 Session 對象
        """
        if name not in self.snapshots:
            print(f"[SessionSnapshot] 快照不存在: {name}")
            return None

        snapshot = self.snapshots[name]
        session_data = snapshot["session_data"]

        # 創建新的配置
        config = SessionConfig(
            cookies=snapshot["cookies"]
        )

        # 創建新 Session
        session = manager.create_session(config=config)
        session.metadata = snapshot["metadata"].copy()

        print(f"[SessionSnapshot] 恢復快照: {name} -> 新Session: {session.id}")
        return session

    def list_snapshots(self) -> List[str]:
        """列出所有快照"""
        return list(self.snapshots.keys())


def example_basic_session_management():
    """示例1: 基礎 Session 管理"""
    print("\n" + "=" * 60)
    print("示例1: 基礎 Session 管理")
    print("=" * 60 + "\n")

    manager = SessionManager(project_id="demo_project", max_sessions=5)

    # 創建 Session
    config = SessionConfig(stealth=True, keep_alive=True)
    session = manager.create_session(config=config)

    print(f"\nSession 信息:")
    print(f"  - ID: {session.id}")
    print(f"  - 狀態: {session.status.value}")
    print(f"  - 隱身模式: {session.config.stealth}")
    print(f"  - 創建時間: {session.created_at}")

    # 使用 Session
    for i in range(3):
        manager.use_session(session.id)
        time.sleep(0.5)

    # 查看統計
    stats = manager.get_statistics()
    print(f"\n統計信息:")
    for key, value in stats.items():
        print(f"  - {key}: {value}")

    # 刪除 Session
    manager.delete_session(session.id)


def example_session_pool():
    """示例2: Session 池使用"""
    print("\n" + "=" * 60)
    print("示例2: Session 池使用")
    print("=" * 60 + "\n")

    manager = SessionManager(project_id="demo_project", max_sessions=10)
    pool = SessionPool(manager, pool_size=3)

    # 查看初始狀態
    status = pool.get_pool_status()
    print(f"池狀態: {json.dumps(status, indent=2)}")

    # 獲取 Session
    session_ids = []
    for i in range(2):
        session_id = pool.acquire()
        if session_id:
            session_ids.append(session_id)
            print(f"獲取到 Session: {session_id}")

    # 查看使用中的狀態
    status = pool.get_pool_status()
    print(f"\n使用中的池狀態: {json.dumps(status, indent=2)}")

    # 釋放 Session
    for session_id in session_ids:
        pool.release(session_id)

    # 查看釋放後的狀態
    status = pool.get_pool_status()
    print(f"\n釋放後的池狀態: {json.dumps(status, indent=2)}")


def example_session_cleanup():
    """示例3: Session 自動清理"""
    print("\n" + "=" * 60)
    print("示例3: Session 自動清理")
    print("=" * 60 + "\n")

    manager = SessionManager(project_id="demo_project")

    # 創建多個 Session
    for i in range(5):
        session = manager.create_session()
        # 模擬不同的最後使用時間
        session.last_used_at = datetime.now() - timedelta(seconds=i * 100)

    print(f"創建了 {len(manager.sessions)} 個 Session\n")

    # 列出所有 Session 及其閒置時間
    for session in manager.list_sessions():
        idle_time = (datetime.now() - session.last_used_at).total_seconds()
        print(f"Session {session.id}: 閒置 {idle_time:.0f}秒")

    # 清理閒置超過 200 秒的 Session
    print()
    cleaned = manager.cleanup_idle_sessions(max_idle_seconds=200)

    print(f"\n剩餘 Session 數量: {len(manager.sessions)}")


def example_session_snapshots():
    """示例4: Session 快照"""
    print("\n" + "=" * 60)
    print("示例4: Session 快照")
    print("=" * 60 + "\n")

    manager = SessionManager(project_id="demo_project")
    snapshot_mgr = SessionSnapshot()

    # 創建一個 Session 並設置一些數據
    config = SessionConfig(
        cookies=[
            {"name": "session_id", "value": "abc123"},
            {"name": "user_token", "value": "xyz789"}
        ]
    )
    session = manager.create_session(config=config)
    session.metadata = {"user": "test_user", "login_time": "2025-12-31"}

    print(f"原始 Session: {session.id}")
    print(f"Cookies: {len(session.config.cookies)} 個")
    print(f"Metadata: {session.metadata}")

    # 創建快照
    snapshot_mgr.create_snapshot(session, name="logged_in_state")

    # 刪除原 Session
    manager.delete_session(session.id)
    print(f"\n原始 Session 已刪除")

    # 從快照恢復
    print(f"\n從快照恢復...")
    restored_session = snapshot_mgr.restore_snapshot("logged_in_state", manager)

    if restored_session:
        print(f"恢復的 Session: {restored_session.id}")
        print(f"Cookies: {len(restored_session.config.cookies)} 個")
        print(f"Metadata: {restored_session.metadata}")


def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("Browserbase Session 管理示例")
    print("=" * 60)

    # 運行所有示例
    example_basic_session_management()
    example_session_pool()
    example_session_cleanup()
    example_session_snapshots()

    print("\n" + "=" * 60)
    print("所有示例完成！")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()

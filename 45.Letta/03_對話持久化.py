"""
Letta 對話持久化系統

本模組展示如何實現持久化對話功能：
1. 會話保存和恢復
2. 多會話管理
3. 狀態快照和回滾
4. 對話導出和導入
5. 跨設備同步

讓 Agent 能夠在不同時間、不同設備上繼續對話。

作者：Letta 框架示例
日期：2025-01
"""

import os
import json
import pickle
import sqlite3
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict, field
from pathlib import Path
import hashlib


@dataclass
class SessionMetadata:
    """會話元數據"""
    session_id: str
    agent_id: str
    created_at: str
    updated_at: str
    title: str
    description: str
    tags: List[str] = field(default_factory=list)
    message_count: int = 0
    is_active: bool = True


@dataclass
class SessionSnapshot:
    """會話快照"""
    snapshot_id: str
    session_id: str
    timestamp: str
    core_memory: Dict[str, str]
    messages: List[Dict[str, Any]]
    metadata: Dict[str, Any]


class SessionStorage:
    """
    會話存儲管理器

    負責持久化保存和恢復會話數據。
    """

    def __init__(self, storage_path: str = "./letta_sessions"):
        """
        初始化會話存儲管理器

        參數:
            storage_path: 存儲路徑
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # 初始化 SQLite 數據庫
        self.db_path = self.storage_path / "sessions.db"
        self._init_database()

        print(f"會話存儲初始化完成")
        print(f"存儲路徑: {self.storage_path.absolute()}")

    def _init_database(self) -> None:
        """初始化數據庫表結構"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 會話元數據表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                tags TEXT,
                message_count INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1
            )
        """)

        # 消息表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                metadata TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)

        # 快照表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS snapshots (
                snapshot_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                data TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)

        conn.commit()
        conn.close()

        print("數據庫初始化完成")

    def create_session(self, agent_id: str, title: str,
                      description: str = "", tags: Optional[List[str]] = None) -> str:
        """
        創建新會話

        參數:
            agent_id: Agent ID
            title: 會話標題
            description: 會話描述
            tags: 標籤列表

        返回:
            會話 ID
        """
        session_id = self._generate_session_id(agent_id)
        now = datetime.now().isoformat()

        metadata = SessionMetadata(
            session_id=session_id,
            agent_id=agent_id,
            created_at=now,
            updated_at=now,
            title=title,
            description=description,
            tags=tags or []
        )

        # 保存到數據庫
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO sessions
            (session_id, agent_id, created_at, updated_at, title, description, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            metadata.session_id,
            metadata.agent_id,
            metadata.created_at,
            metadata.updated_at,
            metadata.title,
            metadata.description,
            json.dumps(metadata.tags)
        ))

        conn.commit()
        conn.close()

        print(f"\n[會話創建] {title}")
        print(f"  會話 ID: {session_id}")
        print(f"  Agent ID: {agent_id}")

        return session_id

    def save_message(self, session_id: str, role: str, content: str,
                    metadata: Optional[Dict] = None) -> None:
        """
        保存消息

        參數:
            session_id: 會話 ID
            role: 角色（'user' 或 'assistant'）
            content: 消息內容
            metadata: 額外元數據
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO messages (session_id, role, content, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (
            session_id,
            role,
            content,
            datetime.now().isoformat(),
            json.dumps(metadata or {})
        ))

        # 更新會話的消息計數和更新時間
        cursor.execute("""
            UPDATE sessions
            SET message_count = message_count + 1,
                updated_at = ?
            WHERE session_id = ?
        """, (datetime.now().isoformat(), session_id))

        conn.commit()
        conn.close()

        print(f"[消息保存] {role}: {content[:50]}...")

    def load_session(self, session_id: str) -> Dict[str, Any]:
        """
        加載會話

        參數:
            session_id: 會話 ID

        返回:
            會話數據
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 加載會話元數據
        cursor.execute("""
            SELECT * FROM sessions WHERE session_id = ?
        """, (session_id,))

        session_row = cursor.fetchone()
        if not session_row:
            raise ValueError(f"會話 {session_id} 不存在")

        # 加載消息
        cursor.execute("""
            SELECT role, content, timestamp, metadata
            FROM messages
            WHERE session_id = ?
            ORDER BY timestamp ASC
        """, (session_id,))

        messages = [
            {
                "role": row[0],
                "content": row[1],
                "timestamp": row[2],
                "metadata": json.loads(row[3])
            }
            for row in cursor.fetchall()
        ]

        conn.close()

        session_data = {
            "session_id": session_row[0],
            "agent_id": session_row[1],
            "created_at": session_row[2],
            "updated_at": session_row[3],
            "title": session_row[4],
            "description": session_row[5],
            "tags": json.loads(session_row[6]),
            "message_count": session_row[7],
            "is_active": bool(session_row[8]),
            "messages": messages
        }

        print(f"\n[會話加載] {session_data['title']}")
        print(f"  消息數: {len(messages)}")
        print(f"  最後更新: {session_data['updated_at']}")

        return session_data

    def list_sessions(self, agent_id: Optional[str] = None,
                     active_only: bool = True) -> List[SessionMetadata]:
        """
        列出所有會話

        參數:
            agent_id: 過濾特定 Agent 的會話
            active_only: 只顯示活躍會話

        返回:
            會話元數據列表
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM sessions WHERE 1=1"
        params = []

        if agent_id:
            query += " AND agent_id = ?"
            params.append(agent_id)

        if active_only:
            query += " AND is_active = 1"

        query += " ORDER BY updated_at DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        sessions = []
        for row in rows:
            metadata = SessionMetadata(
                session_id=row[0],
                agent_id=row[1],
                created_at=row[2],
                updated_at=row[3],
                title=row[4],
                description=row[5],
                tags=json.loads(row[6]),
                message_count=row[7],
                is_active=bool(row[8])
            )
            sessions.append(metadata)

        print(f"\n[會話列表] 找到 {len(sessions)} 個會話")
        for s in sessions:
            print(f"  - {s.title} ({s.message_count} 條消息)")

        return sessions

    def delete_session(self, session_id: str) -> None:
        """
        刪除會話

        參數:
            session_id: 會話 ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 刪除消息
        cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))

        # 刪除快照
        cursor.execute("DELETE FROM snapshots WHERE session_id = ?", (session_id,))

        # 刪除會話
        cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))

        conn.commit()
        conn.close()

        print(f"[會話刪除] 已刪除會話 {session_id}")

    def _generate_session_id(self, agent_id: str) -> str:
        """生成唯一的會話 ID"""
        timestamp = datetime.now().isoformat()
        data = f"{agent_id}_{timestamp}"
        return hashlib.md5(data.encode()).hexdigest()[:16]


class SnapshotManager:
    """
    快照管理器

    管理會話的快照，支持回滾到之前的狀態。
    """

    def __init__(self, storage: SessionStorage):
        """
        初始化快照管理器

        參數:
            storage: 會話存儲實例
        """
        self.storage = storage
        print("快照管理器初始化完成")

    def create_snapshot(self, session_id: str, core_memory: Dict[str, str],
                       metadata: Optional[Dict] = None) -> str:
        """
        創建會話快照

        參數:
            session_id: 會話 ID
            core_memory: 核心記憶
            metadata: 額外元數據

        返回:
            快照 ID
        """
        snapshot_id = self._generate_snapshot_id(session_id)

        # 加載當前會話的消息
        session_data = self.storage.load_session(session_id)

        snapshot = SessionSnapshot(
            snapshot_id=snapshot_id,
            session_id=session_id,
            timestamp=datetime.now().isoformat(),
            core_memory=core_memory,
            messages=session_data['messages'],
            metadata=metadata or {}
        )

        # 保存到數據庫
        conn = sqlite3.connect(self.storage.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO snapshots (snapshot_id, session_id, timestamp, data)
            VALUES (?, ?, ?, ?)
        """, (
            snapshot.snapshot_id,
            snapshot.session_id,
            snapshot.timestamp,
            json.dumps(asdict(snapshot))
        ))

        conn.commit()
        conn.close()

        print(f"\n[快照創建] {snapshot_id}")
        print(f"  會話: {session_id}")
        print(f"  消息數: {len(snapshot.messages)}")

        return snapshot_id

    def list_snapshots(self, session_id: str) -> List[SessionSnapshot]:
        """
        列出會話的所有快照

        參數:
            session_id: 會話 ID

        返回:
            快照列表
        """
        conn = sqlite3.connect(self.storage.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT data FROM snapshots
            WHERE session_id = ?
            ORDER BY timestamp DESC
        """, (session_id,))

        snapshots = []
        for row in cursor.fetchall():
            data = json.loads(row[0])
            snapshot = SessionSnapshot(**data)
            snapshots.append(snapshot)

        conn.close()

        print(f"\n[快照列表] 會話 {session_id} 有 {len(snapshots)} 個快照")

        return snapshots

    def restore_snapshot(self, snapshot_id: str) -> Dict[str, Any]:
        """
        恢復快照

        參數:
            snapshot_id: 快照 ID

        返回:
            恢復的會話數據
        """
        conn = sqlite3.connect(self.storage.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT data FROM snapshots WHERE snapshot_id = ?
        """, (snapshot_id,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            raise ValueError(f"快照 {snapshot_id} 不存在")

        snapshot_data = json.loads(row[0])
        snapshot = SessionSnapshot(**snapshot_data)

        print(f"\n[快照恢復] {snapshot_id}")
        print(f"  時間: {snapshot.timestamp}")
        print(f"  消息數: {len(snapshot.messages)}")

        return {
            "core_memory": snapshot.core_memory,
            "messages": snapshot.messages,
            "metadata": snapshot.metadata
        }

    def _generate_snapshot_id(self, session_id: str) -> str:
        """生成快照 ID"""
        timestamp = datetime.now().isoformat()
        data = f"{session_id}_{timestamp}"
        return hashlib.md5(data.encode()).hexdigest()[:16]


class SessionManager:
    """
    會話管理器

    提供高級的會話管理功能。
    """

    def __init__(self, storage_path: str = "./letta_sessions"):
        """
        初始化會話管理器

        參數:
            storage_path: 存儲路徑
        """
        self.storage = SessionStorage(storage_path)
        self.snapshot_manager = SnapshotManager(self.storage)
        self.active_sessions: Dict[str, Dict[str, Any]] = {}

        print("\n會話管理器初始化完成")

    def new_session(self, agent_id: str, title: str,
                   description: str = "") -> str:
        """
        創建新會話

        參數:
            agent_id: Agent ID
            title: 會話標題
            description: 會話描述

        返回:
            會話 ID
        """
        session_id = self.storage.create_session(agent_id, title, description)
        self.active_sessions[session_id] = {
            "agent_id": agent_id,
            "title": title,
            "messages": []
        }
        return session_id

    def send_message_to_session(self, session_id: str, role: str,
                               content: str) -> None:
        """
        向會話發送消息

        參數:
            session_id: 會話 ID
            role: 角色
            content: 消息內容
        """
        # 保存到存儲
        self.storage.save_message(session_id, role, content)

        # 更新內存中的會話
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["messages"].append({
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat()
            })

    def get_session_history(self, session_id: str, limit: Optional[int] = None) -> List[Dict]:
        """
        獲取會話歷史

        參數:
            session_id: 會話 ID
            limit: 限制返回的消息數量

        返回:
            消息列表
        """
        session_data = self.storage.load_session(session_id)
        messages = session_data['messages']

        if limit:
            messages = messages[-limit:]

        print(f"\n[會話歷史] {session_data['title']}")
        for msg in messages:
            print(f"  [{msg['role']}] {msg['content'][:50]}...")

        return messages

    def search_sessions(self, query: str) -> List[SessionMetadata]:
        """
        搜索會話

        參數:
            query: 搜索查詢

        返回:
            匹配的會話列表
        """
        all_sessions = self.storage.list_sessions(active_only=False)

        # 簡單的文本匹配
        results = [
            s for s in all_sessions
            if query.lower() in s.title.lower() or
               query.lower() in s.description.lower() or
               any(query.lower() in tag.lower() for tag in s.tags)
        ]

        print(f"\n[會話搜索] 查詢 '{query}': 找到 {len(results)} 個會話")

        return results

    def merge_sessions(self, session_ids: List[str], new_title: str) -> str:
        """
        合併多個會話

        參數:
            session_ids: 要合併的會話 ID 列表
            new_title: 新會話的標題

        返回:
            新會話 ID
        """
        print(f"\n[會話合併] 合併 {len(session_ids)} 個會話")

        # 加載所有會話的消息
        all_messages = []
        agent_id = None

        for session_id in session_ids:
            session_data = self.storage.load_session(session_id)
            if agent_id is None:
                agent_id = session_data['agent_id']
            all_messages.extend(session_data['messages'])

        # 按時間排序
        all_messages.sort(key=lambda m: m['timestamp'])

        # 創建新會話
        new_session_id = self.new_session(
            agent_id,
            new_title,
            f"合併自 {len(session_ids)} 個會話"
        )

        # 保存所有消息
        for msg in all_messages:
            self.storage.save_message(
                new_session_id,
                msg['role'],
                msg['content'],
                msg.get('metadata')
            )

        print(f"✓ 新會話創建: {new_session_id}")
        print(f"  總消息數: {len(all_messages)}")

        return new_session_id

    def export_session(self, session_id: str, export_path: str) -> None:
        """
        導出會話到文件

        參數:
            session_id: 會話 ID
            export_path: 導出文件路徑
        """
        session_data = self.storage.load_session(session_id)

        export_file = Path(export_path)
        export_file.parent.mkdir(parents=True, exist_ok=True)

        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)

        print(f"\n[會話導出] {session_id}")
        print(f"  導出到: {export_file.absolute()}")
        print(f"  消息數: {len(session_data['messages'])}")

    def import_session(self, import_path: str) -> str:
        """
        從文件導入會話

        參數:
            import_path: 導入文件路徑

        返回:
            新會話 ID
        """
        with open(import_path, 'r', encoding='utf-8') as f:
            session_data = json.load(f)

        # 創建新會話
        new_session_id = self.new_session(
            session_data['agent_id'],
            session_data['title'] + " (導入)",
            session_data.get('description', '')
        )

        # 導入消息
        for msg in session_data['messages']:
            self.storage.save_message(
                new_session_id,
                msg['role'],
                msg['content'],
                msg.get('metadata')
            )

        print(f"\n[會話導入] 成功")
        print(f"  新會話 ID: {new_session_id}")
        print(f"  消息數: {len(session_data['messages'])}")

        return new_session_id


def demonstrate_basic_persistence():
    """演示基本的持久化功能"""
    print("\n" + "=" * 60)
    print("基本持久化演示")
    print("=" * 60)

    manager = SessionManager("./demo_sessions")

    # 創建會話
    session_id = manager.new_session(
        agent_id="agent_001",
        title="Python 學習諮詢",
        description="幫助用戶學習 Python 編程"
    )

    # 模擬對話
    manager.send_message_to_session(session_id, "user", "我想學習 Python")
    manager.send_message_to_session(session_id, "assistant", "很好！我來幫你制定學習計劃。")
    manager.send_message_to_session(session_id, "user", "我應該從哪裡開始？")
    manager.send_message_to_session(session_id, "assistant", "建議從基礎語法開始。")

    # 查看歷史
    manager.get_session_history(session_id)


def demonstrate_multi_session():
    """演示多會話管理"""
    print("\n" + "=" * 60)
    print("多會話管理演示")
    print("=" * 60)

    manager = SessionManager("./demo_sessions")

    # 創建多個會話
    sessions = []
    for i, (title, desc) in enumerate([
        ("技術諮詢", "解答技術問題"),
        ("項目規劃", "幫助規劃項目"),
        ("代碼審查", "審查代碼質量")
    ]):
        session_id = manager.new_session(f"agent_{i}", title, desc)
        sessions.append(session_id)
        manager.send_message_to_session(session_id, "user", f"關於{title}的問題")

    # 列出所有會話
    all_sessions = manager.storage.list_sessions()


def demonstrate_snapshot():
    """演示快照功能"""
    print("\n" + "=" * 60)
    print("快照功能演示")
    print("=" * 60)

    manager = SessionManager("./demo_sessions")

    # 創建會話
    session_id = manager.new_session(
        "agent_snapshot",
        "快照測試會話"
    )

    # 第一階段對話
    manager.send_message_to_session(session_id, "user", "初始消息")
    manager.send_message_to_session(session_id, "assistant", "收到")

    # 創建快照 1
    snapshot1_id = manager.snapshot_manager.create_snapshot(
        session_id,
        {"persona": "友善助手", "human": "普通用戶"},
        {"note": "第一個快照"}
    )

    # 繼續對話
    manager.send_message_to_session(session_id, "user", "更多消息")
    manager.send_message_to_session(session_id, "assistant", "明白了")

    # 創建快照 2
    snapshot2_id = manager.snapshot_manager.create_snapshot(
        session_id,
        {"persona": "友善助手", "human": "高級用戶"},
        {"note": "第二個快照"}
    )

    # 列出快照
    snapshots = manager.snapshot_manager.list_snapshots(session_id)

    # 恢復到快照 1
    restored_data = manager.snapshot_manager.restore_snapshot(snapshot1_id)
    print(f"\n恢復的消息數: {len(restored_data['messages'])}")


def demonstrate_export_import():
    """演示導出和導入功能"""
    print("\n" + "=" * 60)
    print("導出/導入演示")
    print("=" * 60)

    manager = SessionManager("./demo_sessions")

    # 創建並填充會話
    session_id = manager.new_session(
        "agent_export",
        "導出測試會話"
    )

    for i in range(5):
        manager.send_message_to_session(session_id, "user", f"消息 {i}")
        manager.send_message_to_session(session_id, "assistant", f"回復 {i}")

    # 導出會話
    export_path = "./demo_sessions/exports/test_session.json"
    manager.export_session(session_id, export_path)

    # 導入會話
    new_session_id = manager.import_session(export_path)


def demonstrate_session_search():
    """演示會話搜索"""
    print("\n" + "=" * 60)
    print("會話搜索演示")
    print("=" * 60)

    manager = SessionManager("./demo_sessions")

    # 創建多個帶標籤的會話
    titles = ["Python 教學", "JavaScript 學習", "數據分析指導"]
    for title in titles:
        session_id = manager.new_session("agent_search", title, f"{title}相關內容")

    # 搜索會話
    results = manager.search_sessions("Python")
    results = manager.search_sessions("學習")


def main():
    """主函數：運行所有演示"""
    print("\n" + "=" * 70)
    print(" " * 20 + "Letta 對話持久化系統")
    print("=" * 70)

    # 基本持久化
    demonstrate_basic_persistence()

    # 多會話管理
    demonstrate_multi_session()

    # 快照功能
    demonstrate_snapshot()

    # 導出/導入
    demonstrate_export_import()

    # 會話搜索
    demonstrate_session_search()

    print("\n" + "=" * 70)
    print("對話持久化演示完成！")
    print("=" * 70)
    print("\n關鍵要點：")
    print("  1. 所有對話都自動保存到數據庫")
    print("  2. 支持多會話並行管理")
    print("  3. 快照功能允許回滾到之前的狀態")
    print("  4. 可以導出和導入會話進行備份或遷移")
    print("  5. 強大的搜索功能幫助找到歷史會話")
    print("\n下一步：查看 04_工具整合.py")
    print("=" * 70)


if __name__ == "__main__":
    main()

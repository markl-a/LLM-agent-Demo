"""
Continue AI 編程助手 - 團隊協作

這個文件展示了如何在團隊中使用 Continue 進行協作。
包括配置共享、助手共享、知識庫管理等。

主要內容:
1. 團隊配置管理
2. 共享助手配置
3. 團隊知識庫
4. 代碼規範強制
5. 協作工作流
6. 使用統計和分析
7. 權限管理

Author: Continue Team
Date: 2025
"""

import os
import json
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
from datetime import datetime, timedelta
import hashlib


# =====================================================
# 第一部分: 團隊配置定義
# =====================================================

class UserRole(Enum):
    """
    用戶角色
    """
    ADMIN = "admin"  # 管理員
    DEVELOPER = "developer"  # 開發者
    REVIEWER = "reviewer"  # 審查者
    VIEWER = "viewer"  # 觀察者


@dataclass
class TeamMember:
    """
    團隊成員
    """
    username: str
    email: str
    role: UserRole
    joined_at: datetime = field(default_factory=datetime.now)
    active: bool = True

    def has_permission(self, permission: str) -> bool:
        """
        檢查權限

        Args:
            permission: 權限名稱

        Returns:
            是否擁有權限
        """
        permissions = {
            UserRole.ADMIN: {"read", "write", "delete", "manage"},
            UserRole.DEVELOPER: {"read", "write"},
            UserRole.REVIEWER: {"read", "review"},
            UserRole.VIEWER: {"read"}
        }

        return permission in permissions.get(self.role, set())


@dataclass
class TeamConfig:
    """
    團隊配置
    """
    team_name: str
    team_id: str
    members: List[TeamMember] = field(default_factory=list)
    shared_assistants: List[str] = field(default_factory=list)
    coding_standards: Dict[str, Any] = field(default_factory=dict)
    shared_knowledge: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def add_member(self, member: TeamMember):
        """添加成員"""
        self.members.append(member)

    def remove_member(self, username: str):
        """移除成員"""
        self.members = [m for m in self.members if m.username != username]

    def get_member(self, username: str) -> Optional[TeamMember]:
        """獲取成員"""
        for member in self.members:
            if member.username == username:
                return member
        return None

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "team_name": self.team_name,
            "team_id": self.team_id,
            "members": [
                {
                    "username": m.username,
                    "email": m.email,
                    "role": m.role.value,
                    "joined_at": m.joined_at.isoformat(),
                    "active": m.active
                }
                for m in self.members
            ],
            "shared_assistants": self.shared_assistants,
            "coding_standards": self.coding_standards,
            "created_at": self.created_at.isoformat()
        }


# =====================================================
# 第二部分: 團隊配置管理器
# =====================================================

class TeamConfigManager:
    """
    團隊配置管理器

    管理團隊的共享配置
    """

    def __init__(self, config_dir: str = "./.continue/team"):
        """
        初始化

        Args:
            config_dir: 配置目錄
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "team_config.json"

    def create_team(
        self,
        team_name: str,
        admin_username: str,
        admin_email: str
    ) -> TeamConfig:
        """
        創建團隊

        Args:
            team_name: 團隊名稱
            admin_username: 管理員用戶名
            admin_email: 管理員郵箱

        Returns:
            團隊配置
        """
        team_id = self._generate_team_id(team_name)

        # 創建管理員
        admin = TeamMember(
            username=admin_username,
            email=admin_email,
            role=UserRole.ADMIN
        )

        # 創建團隊配置
        config = TeamConfig(
            team_name=team_name,
            team_id=team_id
        )
        config.add_member(admin)

        # 保存配置
        self.save_config(config)

        print(f"團隊 '{team_name}' 創建成功!")
        print(f"團隊 ID: {team_id}")

        return config

    def load_config(self) -> Optional[TeamConfig]:
        """
        加載團隊配置

        Returns:
            團隊配置或 None
        """
        if not self.config_file.exists():
            return None

        with open(self.config_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 重建 TeamConfig 對象
        config = TeamConfig(
            team_name=data["team_name"],
            team_id=data["team_id"],
            created_at=datetime.fromisoformat(data["created_at"])
        )

        # 重建成員
        for member_data in data["members"]:
            member = TeamMember(
                username=member_data["username"],
                email=member_data["email"],
                role=UserRole(member_data["role"]),
                joined_at=datetime.fromisoformat(member_data["joined_at"]),
                active=member_data["active"]
            )
            config.add_member(member)

        config.shared_assistants = data.get("shared_assistants", [])
        config.coding_standards = data.get("coding_standards", {})

        return config

    def save_config(self, config: TeamConfig):
        """
        保存團隊配置

        Args:
            config: 團隊配置
        """
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)

        print(f"團隊配置已保存")

    def _generate_team_id(self, team_name: str) -> str:
        """
        生成團隊 ID

        Args:
            team_name: 團隊名稱

        Returns:
            團隊 ID
        """
        hash_input = f"{team_name}{datetime.now().isoformat()}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:12]


# =====================================================
# 第三部分: 共享助手管理
# =====================================================

@dataclass
class SharedAssistant:
    """
    共享助手
    """
    name: str
    description: str
    system_prompt: str
    model: str
    author: str
    version: str
    created_at: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "name": self.name,
            "description": self.description,
            "system_prompt": self.system_prompt,
            "model": self.model,
            "author": self.author,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "tags": self.tags
        }


class SharedAssistantLibrary:
    """
    共享助手庫

    管理團隊的共享助手
    """

    def __init__(self, library_dir: str = "./.continue/team/assistants"):
        """
        初始化

        Args:
            library_dir: 助手庫目錄
        """
        self.library_dir = Path(library_dir)
        self.library_dir.mkdir(parents=True, exist_ok=True)

    def publish_assistant(self, assistant: SharedAssistant) -> bool:
        """
        發布助手到團隊庫

        Args:
            assistant: 共享助手

        Returns:
            是否發布成功
        """
        filename = f"{assistant.name.lower().replace(' ', '_')}.json"
        filepath = self.library_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(assistant.to_dict(), f, indent=2, ensure_ascii=False)

        print(f"助手 '{assistant.name}' 已發布到團隊庫")
        return True

    def list_assistants(self) -> List[SharedAssistant]:
        """
        列出所有共享助手

        Returns:
            助手列表
        """
        assistants = []

        for filepath in self.library_dir.glob("*.json"):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            assistant = SharedAssistant(
                name=data["name"],
                description=data["description"],
                system_prompt=data["system_prompt"],
                model=data["model"],
                author=data["author"],
                version=data["version"],
                created_at=datetime.fromisoformat(data["created_at"]),
                tags=data.get("tags", [])
            )
            assistants.append(assistant)

        return assistants

    def get_assistant(self, name: str) -> Optional[SharedAssistant]:
        """
        獲取指定助手

        Args:
            name: 助手名稱

        Returns:
            助手對象或 None
        """
        assistants = self.list_assistants()
        for assistant in assistants:
            if assistant.name.lower() == name.lower():
                return assistant
        return None

    def search_assistants(self, query: str) -> List[SharedAssistant]:
        """
        搜索助手

        Args:
            query: 搜索關鍵詞

        Returns:
            匹配的助手列表
        """
        assistants = self.list_assistants()
        query_lower = query.lower()

        return [
            a for a in assistants
            if query_lower in a.name.lower()
            or query_lower in a.description.lower()
            or any(query_lower in tag.lower() for tag in a.tags)
        ]


# =====================================================
# 第四部分: 團隊知識庫
# =====================================================

@dataclass
class KnowledgeEntry:
    """
    知識條目
    """
    title: str
    content: str
    category: str
    author: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)
    upvotes: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "title": self.title,
            "content": self.content,
            "category": self.category,
            "author": self.author,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "tags": self.tags,
            "upvotes": self.upvotes
        }


class TeamKnowledgeBase:
    """
    團隊知識庫

    存儲和管理團隊共享的知識和最佳實踐
    """

    def __init__(self, kb_dir: str = "./.continue/team/knowledge"):
        """
        初始化

        Args:
            kb_dir: 知識庫目錄
        """
        self.kb_dir = Path(kb_dir)
        self.kb_dir.mkdir(parents=True, exist_ok=True)

    def add_entry(self, entry: KnowledgeEntry) -> bool:
        """
        添加知識條目

        Args:
            entry: 知識條目

        Returns:
            是否添加成功
        """
        # 生成文件名
        filename = f"{entry.category}_{entry.title.lower().replace(' ', '_')}.json"
        filepath = self.kb_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(entry.to_dict(), f, indent=2, ensure_ascii=False)

        print(f"知識條目 '{entry.title}' 已添加")
        return True

    def list_entries(self, category: Optional[str] = None) -> List[KnowledgeEntry]:
        """
        列出知識條目

        Args:
            category: 可選的分類過濾

        Returns:
            知識條目列表
        """
        entries = []

        for filepath in self.kb_dir.glob("*.json"):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 分類過濾
            if category and data["category"] != category:
                continue

            entry = KnowledgeEntry(
                title=data["title"],
                content=data["content"],
                category=data["category"],
                author=data["author"],
                created_at=datetime.fromisoformat(data["created_at"]),
                updated_at=datetime.fromisoformat(data["updated_at"]),
                tags=data.get("tags", []),
                upvotes=data.get("upvotes", 0)
            )
            entries.append(entry)

        # 按讚數排序
        entries.sort(key=lambda e: e.upvotes, reverse=True)
        return entries

    def search(self, query: str) -> List[KnowledgeEntry]:
        """
        搜索知識庫

        Args:
            query: 搜索關鍵詞

        Returns:
            匹配的條目列表
        """
        entries = self.list_entries()
        query_lower = query.lower()

        return [
            e for e in entries
            if query_lower in e.title.lower()
            or query_lower in e.content.lower()
            or any(query_lower in tag.lower() for tag in e.tags)
        ]

    def get_categories(self) -> List[str]:
        """
        獲取所有分類

        Returns:
            分類列表
        """
        entries = self.list_entries()
        categories = set(e.category for e in entries)
        return sorted(categories)


# =====================================================
# 第五部分: 代碼規範管理
# =====================================================

@dataclass
class CodingStandard:
    """
    代碼規範
    """
    name: str
    description: str
    rules: Dict[str, Any]
    enforced: bool = True

    def validate_code(self, code: str) -> List[str]:
        """
        驗證代碼是否符合規範

        Args:
            code: 代碼

        Returns:
            違規列表
        """
        violations = []

        # 檢查規則
        if "max_line_length" in self.rules:
            max_length = self.rules["max_line_length"]
            for i, line in enumerate(code.split('\n'), 1):
                if len(line) > max_length:
                    violations.append(
                        f"第 {i} 行超過最大長度 {max_length}"
                    )

        if "require_docstrings" in self.rules and self.rules["require_docstrings"]:
            if '"""' not in code and "'''" not in code:
                violations.append("缺少文檔字符串")

        return violations


class CodingStandardsManager:
    """
    代碼規範管理器

    管理和執行團隊代碼規範
    """

    def __init__(self):
        """初始化"""
        self.standards: Dict[str, CodingStandard] = {}
        self._setup_default_standards()

    def _setup_default_standards(self):
        """設置默認規範"""
        python_standard = CodingStandard(
            name="Python 代碼規範",
            description="基於 PEP 8 的 Python 代碼規範",
            rules={
                "max_line_length": 88,
                "require_docstrings": True,
                "require_type_hints": True,
                "naming_convention": "snake_case"
            }
        )
        self.add_standard(python_standard)

    def add_standard(self, standard: CodingStandard):
        """
        添加規範

        Args:
            standard: 代碼規範
        """
        self.standards[standard.name] = standard

    def validate_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        驗證代碼

        Args:
            code: 代碼
            language: 語言

        Returns:
            驗證結果
        """
        # 找到對應的規範
        standard_name = f"{language.title()} 代碼規範"
        standard = self.standards.get(standard_name)

        if not standard:
            return {
                "valid": True,
                "violations": [],
                "message": "未找到對應的代碼規範"
            }

        violations = standard.validate_code(code)

        return {
            "valid": len(violations) == 0,
            "violations": violations,
            "standard": standard_name
        }


# =====================================================
# 第六部分: 使用統計
# =====================================================

@dataclass
class UsageStats:
    """
    使用統計
    """
    user: str
    total_requests: int = 0
    total_tokens: int = 0
    commands_used: Dict[str, int] = field(default_factory=dict)
    assistants_used: Dict[str, int] = field(default_factory=dict)
    last_active: datetime = field(default_factory=datetime.now)

    def record_request(self, tokens: int, command: str, assistant: str):
        """
        記錄請求

        Args:
            tokens: token 數
            command: 命令
            assistant: 助手
        """
        self.total_requests += 1
        self.total_tokens += tokens
        self.commands_used[command] = self.commands_used.get(command, 0) + 1
        self.assistants_used[assistant] = self.assistants_used.get(assistant, 0) + 1
        self.last_active = datetime.now()


class TeamAnalytics:
    """
    團隊分析

    分析團隊使用情況
    """

    def __init__(self):
        """初始化"""
        self.user_stats: Dict[str, UsageStats] = {}

    def record_usage(self, user: str, tokens: int, command: str, assistant: str):
        """
        記錄使用情況

        Args:
            user: 用戶
            tokens: token 數
            command: 命令
            assistant: 助手
        """
        if user not in self.user_stats:
            self.user_stats[user] = UsageStats(user=user)

        self.user_stats[user].record_request(tokens, command, assistant)

    def get_team_summary(self) -> Dict[str, Any]:
        """
        獲取團隊摘要

        Returns:
            摘要信息
        """
        total_users = len(self.user_stats)
        total_requests = sum(s.total_requests for s in self.user_stats.values())
        total_tokens = sum(s.total_tokens for s in self.user_stats.values())

        # 最活躍用戶
        most_active_user = max(
            self.user_stats.values(),
            key=lambda s: s.total_requests
        ) if self.user_stats else None

        return {
            "total_users": total_users,
            "total_requests": total_requests,
            "total_tokens": total_tokens,
            "most_active_user": most_active_user.user if most_active_user else None,
            "average_requests_per_user": total_requests / total_users if total_users > 0 else 0
        }

    def get_popular_commands(self, top_n: int = 5) -> List[tuple]:
        """
        獲取最受歡迎的命令

        Args:
            top_n: 返回前 N 個

        Returns:
            (命令, 使用次數) 列表
        """
        command_counts = {}

        for stats in self.user_stats.values():
            for cmd, count in stats.commands_used.items():
                command_counts[cmd] = command_counts.get(cmd, 0) + count

        sorted_commands = sorted(
            command_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return sorted_commands[:top_n]


# =====================================================
# 第七部分: 使用示例
# =====================================================

def team_setup_example():
    """
    團隊設置示例
    """
    print("=" * 60)
    print("示例 1: 團隊設置")
    print("=" * 60)

    # 創建團隊
    manager = TeamConfigManager()
    team = manager.create_team(
        team_name="開發團隊 A",
        admin_username="alice",
        admin_email="alice@example.com"
    )

    # 添加成員
    team.add_member(TeamMember(
        username="bob",
        email="bob@example.com",
        role=UserRole.DEVELOPER
    ))

    team.add_member(TeamMember(
        username="charlie",
        email="charlie@example.com",
        role=UserRole.REVIEWER
    ))

    # 保存配置
    manager.save_config(team)

    # 列出成員
    print("\n團隊成員:")
    for member in team.members:
        print(f"  - {member.username} ({member.role.value})")


def shared_assistant_example():
    """
    共享助手示例
    """
    print("\n" + "=" * 60)
    print("示例 2: 共享助手")
    print("=" * 60)

    library = SharedAssistantLibrary()

    # 創建並發布助手
    assistant = SharedAssistant(
        name="Python 代碼審查員",
        description="專門審查 Python 代碼的助手",
        system_prompt="你是一位 Python 代碼審查專家...",
        model="gpt-4",
        author="alice",
        version="1.0.0",
        tags=["python", "code-review", "quality"]
    )

    library.publish_assistant(assistant)

    # 列出所有助手
    print("\n共享助手庫:")
    for asst in library.list_assistants():
        print(f"  - {asst.name} by {asst.author}")
        print(f"    {asst.description}")


def knowledge_base_example():
    """
    知識庫示例
    """
    print("\n" + "=" * 60)
    print("示例 3: 團隊知識庫")
    print("=" * 60)

    kb = TeamKnowledgeBase()

    # 添加知識條目
    entry1 = KnowledgeEntry(
        title="如何處理異步錯誤",
        content="在 Python 中處理異步錯誤的最佳實踐...",
        category="Python",
        author="alice",
        tags=["async", "error-handling", "best-practices"]
    )

    entry2 = KnowledgeEntry(
        title="Git 工作流規範",
        content="團隊 Git 分支和合併規範...",
        category="工具",
        author="bob",
        tags=["git", "workflow", "standards"]
    )

    kb.add_entry(entry1)
    kb.add_entry(entry2)

    # 列出知識條目
    print("\n知識庫內容:")
    for entry in kb.list_entries():
        print(f"  - [{entry.category}] {entry.title}")
        print(f"    作者: {entry.author}")


def analytics_example():
    """
    分析統計示例
    """
    print("\n" + "=" * 60)
    print("示例 4: 使用統計")
    print("=" * 60)

    analytics = TeamAnalytics()

    # 模擬使用記錄
    analytics.record_usage("alice", 1000, "/generate", "GPT-4")
    analytics.record_usage("alice", 500, "/test", "GPT-4")
    analytics.record_usage("bob", 800, "/review", "Claude")
    analytics.record_usage("bob", 600, "/generate", "GPT-4")

    # 顯示統計
    summary = analytics.get_team_summary()
    print("\n團隊摘要:")
    print(f"  總用戶數: {summary['total_users']}")
    print(f"  總請求數: {summary['total_requests']}")
    print(f"  總 Token 數: {summary['total_tokens']}")
    print(f"  最活躍用戶: {summary['most_active_user']}")

    print("\n最受歡迎的命令:")
    for cmd, count in analytics.get_popular_commands():
        print(f"  - {cmd}: {count} 次")


def main():
    """
    主函數
    """
    print("Continue - 團隊協作\n")

    team_setup_example()
    shared_assistant_example()
    knowledge_base_example()
    analytics_example()

    print("\n" + "=" * 60)
    print("所有示例運行完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()

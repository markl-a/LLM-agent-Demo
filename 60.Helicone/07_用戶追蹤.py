"""
Helicone 用戶追蹤與會話管理
===========================

本文件展示如何使用 Helicone 追蹤用戶行為和管理會話。
有效的用戶追蹤對於了解使用模式、優化體驗和計費至關重要。

主要內容:
1. 用戶識別和追蹤
2. 會話管理
3. 用戶行為分析
4. 多輪對話追蹤
5. 用戶分群分析
6. 活躍度監控
7. 個性化體驗

作者: Helicone Team
日期: 2025-12-31
"""

import os
import sys
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
from dotenv import load_dotenv

try:
    import openai
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.tree import Tree
    import pandas as pd
except ImportError as e:
    print(f"❌ 缺少必要的依賴: {e}")
    print("請運行: pip install openai rich pandas")
    sys.exit(1)


class UserSegment(Enum):
    """用戶分群"""
    NEW = "new"                    # 新用戶 (< 7 天)
    ACTIVE = "active"              # 活躍用戶
    POWER_USER = "power_user"      # 重度用戶
    INACTIVE = "inactive"          # 不活躍用戶
    CHURNED = "churned"            # 流失用戶


@dataclass
class UserProfile:
    """用戶資料"""
    user_id: str
    username: str
    email: str
    created_at: datetime
    segment: UserSegment
    total_requests: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    last_active: Optional[datetime] = None
    favorite_model: Optional[str] = None
    favorite_feature: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


@dataclass
class Session:
    """會話"""
    session_id: str
    user_id: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    messages: List[Dict] = field(default_factory=list)
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    context: Dict = field(default_factory=dict)

    @property
    def duration(self) -> Optional[timedelta]:
        """會話持續時間"""
        if self.ended_at:
            return self.ended_at - self.started_at
        return datetime.now() - self.started_at

    @property
    def message_count(self) -> int:
        """消息數量"""
        return len(self.messages)

    def is_active(self, timeout_minutes: int = 30) -> bool:
        """檢查會話是否仍然活躍"""
        if self.ended_at:
            return False

        time_since_last = datetime.now() - self.messages[-1]["timestamp"] if self.messages else datetime.now() - self.started_at
        return time_since_last.total_seconds() < (timeout_minutes * 60)


@dataclass
class UserActivity:
    """用戶活動記錄"""
    timestamp: datetime
    user_id: str
    session_id: str
    action_type: str
    feature: str
    model: str
    tokens: int
    cost_usd: float
    metadata: Dict = field(default_factory=dict)


class HeliconeUserTracker:
    """
    Helicone 用戶追蹤器

    提供全面的用戶行為追蹤和分析功能。
    """

    def __init__(self):
        """初始化用戶追蹤器"""
        load_dotenv()

        # API 配置
        self.helicone_api_key = os.getenv("HELICONE_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.helicone_base_url = "https://oai.helicone.ai/v1"

        # 初始化客戶端
        self.client = openai.OpenAI(
            api_key=self.openai_api_key,
            base_url=self.helicone_base_url,
            default_headers={
                "Helicone-Auth": f"Bearer {self.helicone_api_key}"
            }
        )

        self.console = Console()

        # 用戶管理
        self.users: Dict[str, UserProfile] = {}

        # 會話管理
        self.sessions: Dict[str, Session] = {}
        self.active_sessions: Set[str] = set()

        # 活動記錄
        self.activities: List[UserActivity] = []

        self.console.print("✅ [green]用戶追蹤器已初始化[/green]")

    def create_user(
        self,
        user_id: str,
        username: str,
        email: str,
        **metadata
    ) -> UserProfile:
        """
        創建新用戶

        在系統中註冊新用戶並創建用戶資料。
        """
        user = UserProfile(
            user_id=user_id,
            username=username,
            email=email,
            created_at=datetime.now(),
            segment=UserSegment.NEW,
            metadata=metadata
        )

        self.users[user_id] = user

        self.console.print(f"✅ [green]已創建用戶: {username} ({user_id})[/green]")

        return user

    def get_or_create_user(
        self,
        user_id: str,
        username: str = None,
        email: str = None
    ) -> UserProfile:
        """獲取或創建用戶"""
        if user_id in self.users:
            return self.users[user_id]

        return self.create_user(
            user_id=user_id,
            username=username or f"user_{user_id}",
            email=email or f"{user_id}@example.com"
        )

    def start_session(
        self,
        user_id: str,
        **context
    ) -> Session:
        """
        開始新會話

        為用戶創建一個新的對話會話。
        """
        session_id = f"session_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

        session = Session(
            session_id=session_id,
            user_id=user_id,
            started_at=datetime.now(),
            context=context
        )

        self.sessions[session_id] = session
        self.active_sessions.add(session_id)

        self.console.print(f"🔵 [cyan]已開始會話: {session_id}[/cyan]")

        return session

    def end_session(self, session_id: str):
        """結束會話"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.ended_at = datetime.now()

            if session_id in self.active_sessions:
                self.active_sessions.remove(session_id)

            self.console.print(f"🔴 [yellow]已結束會話: {session_id}[/yellow]")
            self.console.print(f"   持續時間: {session.duration}")
            self.console.print(f"   消息數: {session.message_count}")
            self.console.print(f"   總成本: ${session.total_cost_usd:.6f}")

    def send_message_in_session(
        self,
        session_id: str,
        message: str,
        model: str = "gpt-3.5-turbo",
        feature: str = "chat",
        **kwargs
    ) -> Dict:
        """
        在會話中發送消息

        這是核心方法,將消息、用戶和會話關聯起來。
        """
        if session_id not in self.sessions:
            return {
                "success": False,
                "error": "會話不存在"
            }

        session = self.sessions[session_id]
        user = self.users.get(session.user_id)

        if not user:
            return {
                "success": False,
                "error": "用戶不存在"
            }

        try:
            start_time = time.time()

            # 構建完整的對話歷史
            messages = []
            for msg in session.messages:
                messages.append({"role": "user", "content": msg["user_message"]})
                messages.append({"role": "assistant", "content": msg["assistant_response"]})

            # 添加當前消息
            messages.append({"role": "user", "content": message})

            # 發送請求
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                extra_headers={
                    # 用戶追蹤
                    "Helicone-User-Id": session.user_id,
                    "Helicone-Session-Id": session_id,

                    # 元數據
                    "Helicone-Property-Feature": feature,
                    "Helicone-Property-MessageIndex": str(session.message_count + 1),
                    "Helicone-Property-SessionStartTime": session.started_at.isoformat(),

                    # 用戶資料
                    "Helicone-Property-UserSegment": user.segment.value,
                    "Helicone-Property-UserTotalRequests": str(user.total_requests),
                },
                **kwargs
            )

            end_time = time.time()

            # 計算成本
            cost = self._calculate_cost(response)

            # 記錄消息
            message_record = {
                "timestamp": datetime.now(),
                "user_message": message,
                "assistant_response": response.choices[0].message.content,
                "model": response.model,
                "tokens": response.usage.total_tokens,
                "cost": cost,
                "duration": end_time - start_time
            }

            session.messages.append(message_record)
            session.total_tokens += response.usage.total_tokens
            session.total_cost_usd += cost

            # 更新用戶資料
            self._update_user_stats(
                user_id=session.user_id,
                model=response.model,
                feature=feature,
                tokens=response.usage.total_tokens,
                cost=cost
            )

            # 記錄活動
            self._record_activity(
                user_id=session.user_id,
                session_id=session_id,
                action_type="message",
                feature=feature,
                model=response.model,
                tokens=response.usage.total_tokens,
                cost=cost
            )

            self.console.print(f"✅ [green]消息 {session.message_count}[/green]")
            self.console.print(f"   Tokens: {response.usage.total_tokens}")
            self.console.print(f"   成本: ${cost:.6f}")

            return {
                "success": True,
                "response": response.choices[0].message.content,
                "message_index": session.message_count,
                "session_stats": {
                    "total_messages": session.message_count,
                    "total_tokens": session.total_tokens,
                    "total_cost": session.total_cost_usd,
                    "duration": str(session.duration)
                }
            }

        except Exception as e:
            self.console.print(f"❌ [red]錯誤: {str(e)}[/red]")
            return {
                "success": False,
                "error": str(e)
            }

    def _calculate_cost(self, response) -> float:
        """計算成本"""
        # 簡化的成本計算
        input_cost = (response.usage.prompt_tokens / 1000) * 0.0005
        output_cost = (response.usage.completion_tokens / 1000) * 0.0015
        return input_cost + output_cost

    def _update_user_stats(
        self,
        user_id: str,
        model: str,
        feature: str,
        tokens: int,
        cost: float
    ):
        """更新用戶統計信息"""
        if user_id not in self.users:
            return

        user = self.users[user_id]
        user.total_requests += 1
        user.total_tokens += tokens
        user.total_cost_usd += cost
        user.last_active = datetime.now()

        # 更新最常用模型
        if not user.favorite_model:
            user.favorite_model = model

        # 更新最常用功能
        if not user.favorite_feature:
            user.favorite_feature = feature

        # 更新用戶分群
        self._update_user_segment(user_id)

    def _update_user_segment(self, user_id: str):
        """更新用戶分群"""
        user = self.users[user_id]

        # 計算用戶年齡
        user_age_days = (datetime.now() - user.created_at).days

        # 計算最近活躍度
        days_since_active = (datetime.now() - user.last_active).days if user.last_active else 999

        # 分群邏輯
        if user_age_days < 7:
            user.segment = UserSegment.NEW
        elif days_since_active > 30:
            user.segment = UserSegment.CHURNED
        elif days_since_active > 7:
            user.segment = UserSegment.INACTIVE
        elif user.total_requests > 100:
            user.segment = UserSegment.POWER_USER
        else:
            user.segment = UserSegment.ACTIVE

    def _record_activity(
        self,
        user_id: str,
        session_id: str,
        action_type: str,
        feature: str,
        model: str,
        tokens: int,
        cost: float,
        **metadata
    ):
        """記錄用戶活動"""
        activity = UserActivity(
            timestamp=datetime.now(),
            user_id=user_id,
            session_id=session_id,
            action_type=action_type,
            feature=feature,
            model=model,
            tokens=tokens,
            cost_usd=cost,
            metadata=metadata
        )

        self.activities.append(activity)

    def get_user_stats(self, user_id: str) -> Dict:
        """獲取用戶統計"""
        if user_id not in self.users:
            return {"error": "用戶不存在"}

        user = self.users[user_id]

        # 計算用戶的會話統計
        user_sessions = [s for s in self.sessions.values() if s.user_id == user_id]
        total_sessions = len(user_sessions)
        active_sessions_count = sum(1 for s in user_sessions if s.is_active())

        # 計算平均值
        avg_tokens_per_request = user.total_tokens / user.total_requests if user.total_requests > 0 else 0
        avg_cost_per_request = user.total_cost_usd / user.total_requests if user.total_requests > 0 else 0

        return {
            "user_id": user.user_id,
            "username": user.username,
            "segment": user.segment.value,
            "created_at": user.created_at.isoformat(),
            "last_active": user.last_active.isoformat() if user.last_active else None,
            "total_requests": user.total_requests,
            "total_tokens": user.total_tokens,
            "total_cost_usd": user.total_cost_usd,
            "total_sessions": total_sessions,
            "active_sessions": active_sessions_count,
            "avg_tokens_per_request": avg_tokens_per_request,
            "avg_cost_per_request": avg_cost_per_request,
            "favorite_model": user.favorite_model,
            "favorite_feature": user.favorite_feature
        }

    def display_user_profile(self, user_id: str):
        """顯示用戶資料"""
        stats = self.get_user_stats(user_id)

        if "error" in stats:
            self.console.print(f"❌ [red]{stats['error']}[/red]")
            return

        # 創建用戶資料面板
        content = f"""
[bold cyan]基本信息:[/bold cyan]
  用戶名: {stats['username']}
  用戶 ID: {stats['user_id']}
  分群: {stats['segment'].upper()}
  創建時間: {stats['created_at']}
  最後活躍: {stats['last_active'] or '從未活躍'}

[bold yellow]使用統計:[/bold yellow]
  總請求: {stats['total_requests']:,}
  總 Tokens: {stats['total_tokens']:,}
  總成本: ${stats['total_cost_usd']:.6f}
  總會話: {stats['total_sessions']}
  活躍會話: {stats['active_sessions']}

[bold green]平均值:[/bold green]
  每請求 Tokens: {stats['avg_tokens_per_request']:.0f}
  每請求成本: ${stats['avg_cost_per_request']:.6f}

[bold magenta]偏好:[/bold magenta]
  常用模型: {stats['favorite_model'] or '無'}
  常用功能: {stats['favorite_feature'] or '無'}
        """

        panel = Panel(
            content.strip(),
            title=f"👤 用戶資料",
            border_style="cyan"
        )

        self.console.print(panel)

    def display_session_details(self, session_id: str):
        """顯示會話詳情"""
        if session_id not in self.sessions:
            self.console.print(f"❌ [red]會話不存在[/red]")
            return

        session = self.sessions[session_id]

        self.console.print(f"\n[bold cyan]💬 會話詳情: {session_id}[/bold cyan]")
        self.console.print("=" * 80)

        # 基本信息
        self.console.print(f"用戶: {session.user_id}")
        self.console.print(f"開始時間: {session.started_at.strftime('%Y-%m-%d %H:%M:%S')}")
        if session.ended_at:
            self.console.print(f"結束時間: {session.ended_at.strftime('%Y-%m-%d %H:%M:%S')}")
        self.console.print(f"持續時間: {session.duration}")
        self.console.print(f"狀態: {'已結束' if session.ended_at else '進行中'}")
        self.console.print(f"\n消息數: {session.message_count}")
        self.console.print(f"總 Tokens: {session.total_tokens:,}")
        self.console.print(f"總成本: ${session.total_cost_usd:.6f}")

        # 消息列表
        if session.messages:
            self.console.print(f"\n[bold yellow]消息歷史:[/bold yellow]")

            for i, msg in enumerate(session.messages, 1):
                self.console.print(f"\n{i}. [{msg['timestamp'].strftime('%H:%M:%S')}]")
                self.console.print(f"   👤 用戶: {msg['user_message'][:100]}...")
                self.console.print(f"   🤖 助手: {msg['assistant_response'][:100]}...")
                self.console.print(f"   📊 {msg['tokens']} tokens, ${msg['cost']:.6f}")

    def get_user_segment_distribution(self) -> Dict:
        """獲取用戶分群分布"""
        distribution = defaultdict(int)

        for user in self.users.values():
            distribution[user.segment.value] += 1

        return dict(distribution)

    def display_analytics_dashboard(self):
        """顯示分析儀表板"""
        self.console.print("\n[bold green]📊 用戶分析儀表板[/bold green]")
        self.console.print("=" * 80)

        # 總體統計
        total_users = len(self.users)
        total_sessions = len(self.sessions)
        active_sessions = len(self.active_sessions)
        total_activities = len(self.activities)

        panel_content = f"""
[bold cyan]總體統計:[/bold cyan]
  總用戶數: {total_users}
  總會話數: {total_sessions}
  活躍會話: {active_sessions}
  總活動記錄: {total_activities}
        """

        self.console.print(Panel(panel_content.strip(), border_style="cyan"))

        # 用戶分群分布
        segment_dist = self.get_user_segment_distribution()

        self.console.print("\n[bold yellow]用戶分群分布:[/bold yellow]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("分群", style="cyan")
        table.add_column("用戶數", justify="right")
        table.add_column("佔比", justify="right")

        for segment, count in sorted(segment_dist.items()):
            percentage = (count / total_users * 100) if total_users > 0 else 0
            table.add_row(
                segment.upper(),
                str(count),
                f"{percentage:.1f}%"
            )

        self.console.print(table)

        # Top 用戶
        self.console.print("\n[bold yellow]Top 用戶 (按請求數):[/bold yellow]")
        top_users = sorted(
            self.users.values(),
            key=lambda u: u.total_requests,
            reverse=True
        )[:5]

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("用戶名", style="cyan")
        table.add_column("請求數", justify="right")
        table.add_column("Tokens", justify="right")
        table.add_column("成本", justify="right")

        for user in top_users:
            table.add_row(
                user.username,
                str(user.total_requests),
                f"{user.total_tokens:,}",
                f"${user.total_cost_usd:.4f}"
            )

        self.console.print(table)

    def simulate_conversation(self, user_id: str, num_messages: int = 5):
        """
        模擬對話

        這個演示展示了如何追蹤完整的多輪對話。
        """
        self.console.print(f"\n[bold cyan]🎭 模擬用戶 {user_id} 的對話[/bold cyan]")
        self.console.print("=" * 80)

        # 開始會話
        session = self.start_session(
            user_id=user_id,
            platform="web",
            language="zh-TW"
        )

        # 預定義的對話
        conversation = [
            "你好,我想了解機器學習",
            "機器學習有哪些主要類型?",
            "監督學習和無監督學習有什麼區別?",
            "可以給我一個實際的應用例子嗎?",
            "謝謝你的解釋!"
        ]

        for i, message in enumerate(conversation[:num_messages]):
            self.console.print(f"\n[bold]消息 {i+1}:[/bold] {message}")

            result = self.send_message_in_session(
                session_id=session.session_id,
                message=message,
                max_tokens=150
            )

            if result["success"]:
                self.console.print(f"[dim]回應: {result['response'][:100]}...[/dim]\n")

            time.sleep(0.5)

        # 結束會話
        self.end_session(session.session_id)

        # 顯示會話詳情
        # self.display_session_details(session.session_id)


def demo_user_tracking():
    """演示用戶追蹤"""
    console = Console()
    console.print("[bold cyan]演示: 用戶追蹤與會話管理[/bold cyan]")
    console.print("=" * 80)

    tracker = HeliconeUserTracker()

    # 創建幾個測試用戶
    users = [
        ("alice_001", "Alice", "alice@example.com"),
        ("bob_002", "Bob", "bob@example.com"),
        ("charlie_003", "Charlie", "charlie@example.com"),
    ]

    for user_id, username, email in users:
        tracker.create_user(user_id, username, email)

    # 模擬對話
    tracker.simulate_conversation("alice_001", num_messages=3)
    tracker.simulate_conversation("bob_002", num_messages=2)

    # 顯示用戶資料
    console.print("\n")
    tracker.display_user_profile("alice_001")

    # 顯示分析儀表板
    tracker.display_analytics_dashboard()

    return tracker


def main():
    """主函數"""
    console = Console()
    console.print("[bold green]🎯 Helicone 用戶追蹤演示[/bold green]\n")

    try:
        tracker = demo_user_tracking()

        console.print("\n✅ [green]演示完成![/green]")
        console.print("📊 前往 https://helicone.ai/dashboard 查看詳細用戶分析")

    except Exception as e:
        console.print(f"\n❌ [red]錯誤: {str(e)}[/red]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

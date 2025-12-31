"""
Helicone 限流控制與配額管理
==========================

本文件展示如何使用 Helicone 實現速率限制、配額管理和成本控制。
這對於保護您的 API 端點和管理預算至關重要。

主要內容:
1. 基本速率限制
2. 用戶級別配額
3. 成本限制和告警
4. 時間窗口限流
5. 自適應限流
6. 配額重置和管理
7. 超限處理策略

作者: Helicone Team
日期: 2025-12-31
"""

import os
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
from collections import defaultdict
from dotenv import load_dotenv

try:
    import openai
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    import pandas as pd
except ImportError as e:
    print(f"❌ 缺少必要的依賴: {e}")
    print("請運行: pip install openai rich pandas")
    sys.exit(1)


class RateLimitType(Enum):
    """限流類型"""
    REQUESTS_PER_MINUTE = "rpm"
    REQUESTS_PER_HOUR = "rph"
    REQUESTS_PER_DAY = "rpd"
    TOKENS_PER_MINUTE = "tpm"
    TOKENS_PER_DAY = "tpd"
    COST_PER_DAY = "cpd"
    COST_PER_MONTH = "cpm"


class UserTier(Enum):
    """用戶等級"""
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


@dataclass
class RateLimitConfig:
    """限流配置"""
    limit_type: RateLimitType
    limit_value: int
    window_seconds: int
    burst_allowed: bool = False
    burst_multiplier: float = 1.5


@dataclass
class UserQuota:
    """用戶配額"""
    user_id: str
    tier: UserTier
    requests_per_day: int
    tokens_per_day: int
    cost_per_day_usd: float
    used_requests: int = 0
    used_tokens: int = 0
    used_cost_usd: float = 0.0
    last_reset: datetime = field(default_factory=datetime.now)

    def remaining_requests(self) -> int:
        """剩餘請求數"""
        return max(0, self.requests_per_day - self.used_requests)

    def remaining_tokens(self) -> int:
        """剩餘 token 數"""
        return max(0, self.tokens_per_day - self.used_tokens)

    def remaining_budget_usd(self) -> float:
        """剩餘預算"""
        return max(0, self.cost_per_day_usd - self.used_cost_usd)

    def usage_percentage(self) -> Dict[str, float]:
        """使用百分比"""
        return {
            "requests": (self.used_requests / self.requests_per_day * 100) if self.requests_per_day > 0 else 0,
            "tokens": (self.used_tokens / self.tokens_per_day * 100) if self.tokens_per_day > 0 else 0,
            "cost": (self.used_cost_usd / self.cost_per_day_usd * 100) if self.cost_per_day_usd > 0 else 0
        }

    def is_quota_exceeded(self) -> Tuple[bool, str]:
        """檢查是否超過配額"""
        if self.used_requests >= self.requests_per_day:
            return True, "請求數超限"
        if self.used_tokens >= self.tokens_per_day:
            return True, "Token 數超限"
        if self.used_cost_usd >= self.cost_per_day_usd:
            return True, "成本超限"
        return False, ""

    def should_reset(self) -> bool:
        """檢查是否應該重置配額"""
        time_since_reset = datetime.now() - self.last_reset
        return time_since_reset.total_seconds() >= 86400  # 24 小時


@dataclass
class RateLimitViolation:
    """限流違規記錄"""
    timestamp: datetime
    user_id: str
    limit_type: str
    limit_value: int
    actual_value: int
    action_taken: str


class HeliconeRateLimiter:
    """
    Helicone 限流控制器

    實現全面的速率限制和配額管理功能。
    """

    def __init__(self):
        """初始化限流控制器"""
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

        # 用戶配額管理
        self.user_quotas: Dict[str, UserQuota] = {}

        # 限流違規記錄
        self.violations: List[RateLimitViolation] = []

        # 請求歷史 (用於限流檢查)
        self.request_history: Dict[str, List[Dict]] = defaultdict(list)

        # 初始化默認配額
        self._initialize_tier_quotas()

        self.console.print("✅ [green]限流控制器已初始化[/green]")

    def _initialize_tier_quotas(self):
        """
        初始化不同等級的默認配額

        為不同用戶等級定義不同的配額限制。
        """
        self.tier_limits = {
            UserTier.FREE: {
                "requests_per_day": 100,
                "tokens_per_day": 50000,
                "cost_per_day_usd": 1.0
            },
            UserTier.BASIC: {
                "requests_per_day": 1000,
                "tokens_per_day": 500000,
                "cost_per_day_usd": 10.0
            },
            UserTier.PRO: {
                "requests_per_day": 10000,
                "tokens_per_day": 5000000,
                "cost_per_day_usd": 100.0
            },
            UserTier.ENTERPRISE: {
                "requests_per_day": 100000,
                "tokens_per_day": 50000000,
                "cost_per_day_usd": 1000.0
            }
        }

    def create_user_quota(self, user_id: str, tier: UserTier) -> UserQuota:
        """
        為用戶創建配額

        根據用戶等級分配相應的配額。
        """
        limits = self.tier_limits[tier]

        quota = UserQuota(
            user_id=user_id,
            tier=tier,
            requests_per_day=limits["requests_per_day"],
            tokens_per_day=limits["tokens_per_day"],
            cost_per_day_usd=limits["cost_per_day_usd"]
        )

        self.user_quotas[user_id] = quota

        self.console.print(f"✅ [green]已為用戶 {user_id} 創建 {tier.value} 等級配額[/green]")

        return quota

    def get_or_create_quota(self, user_id: str, tier: UserTier = UserTier.FREE) -> UserQuota:
        """獲取或創建用戶配額"""
        if user_id not in self.user_quotas:
            return self.create_user_quota(user_id, tier)
        return self.user_quotas[user_id]

    def check_rate_limit(
        self,
        user_id: str,
        estimated_tokens: int = 500,
        estimated_cost: float = 0.001
    ) -> Tuple[bool, str]:
        """
        檢查是否超過限流

        返回: (是否允許, 原因)
        """
        quota = self.user_quotas.get(user_id)

        if not quota:
            return True, "未設置配額限制"

        # 檢查是否需要重置配額
        if quota.should_reset():
            self._reset_quota(user_id)
            quota = self.user_quotas[user_id]

        # 檢查請求數限制
        if quota.used_requests >= quota.requests_per_day:
            self._record_violation(
                user_id, "requests_per_day",
                quota.requests_per_day, quota.used_requests + 1
            )
            return False, f"已達到每日請求限制 ({quota.requests_per_day})"

        # 檢查 token 限制
        if quota.used_tokens + estimated_tokens > quota.tokens_per_day:
            self._record_violation(
                user_id, "tokens_per_day",
                quota.tokens_per_day, quota.used_tokens + estimated_tokens
            )
            return False, f"Token 配額不足 (剩餘: {quota.remaining_tokens()})"

        # 檢查成本限制
        if quota.used_cost_usd + estimated_cost > quota.cost_per_day_usd:
            self._record_violation(
                user_id, "cost_per_day",
                quota.cost_per_day_usd, quota.used_cost_usd + estimated_cost
            )
            return False, f"預算不足 (剩餘: ${quota.remaining_budget_usd():.4f})"

        return True, "在限制範圍內"

    def _record_violation(
        self,
        user_id: str,
        limit_type: str,
        limit_value: float,
        actual_value: float
    ):
        """記錄限流違規"""
        violation = RateLimitViolation(
            timestamp=datetime.now(),
            user_id=user_id,
            limit_type=limit_type,
            limit_value=int(limit_value),
            actual_value=int(actual_value),
            action_taken="rejected"
        )
        self.violations.append(violation)

    def _reset_quota(self, user_id: str):
        """重置用戶配額"""
        if user_id in self.user_quotas:
            quota = self.user_quotas[user_id]
            old_tier = quota.tier

            # 重新創建配額
            self.create_user_quota(user_id, old_tier)

            self.console.print(f"🔄 [yellow]已重置用戶 {user_id} 的配額[/yellow]")

    def request_with_rate_limit(
        self,
        user_id: str,
        prompt: str,
        model: str = "gpt-3.5-turbo",
        **kwargs
    ) -> Dict:
        """
        發送帶限流檢查的請求

        在發送請求前檢查配額,請求後更新使用量。
        """
        # 估算請求參數
        estimated_tokens = kwargs.get("max_tokens", 500) + len(prompt.split()) * 1.3
        estimated_cost = (estimated_tokens / 1000) * 0.002  # 粗略估算

        # 檢查限流
        allowed, reason = self.check_rate_limit(
            user_id,
            int(estimated_tokens),
            estimated_cost
        )

        if not allowed:
            self.console.print(f"🚫 [red]請求被拒絕: {reason}[/red]")
            return {
                "success": False,
                "error": reason,
                "quota_info": self._get_quota_info(user_id)
            }

        # 發送請求
        try:
            start_time = time.time()

            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                extra_headers={
                    "Helicone-User-Id": user_id,
                    "Helicone-Property-RateLimitEnabled": "true",
                    "Helicone-Property-UserTier": self.user_quotas[user_id].tier.value
                },
                **kwargs
            )

            end_time = time.time()

            # 計算實際成本
            actual_tokens = response.usage.total_tokens
            actual_cost = self._calculate_cost(response, model)

            # 更新配額使用
            self._update_quota_usage(
                user_id,
                requests=1,
                tokens=actual_tokens,
                cost=actual_cost
            )

            # 記錄請求
            request_record = {
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "model": model,
                "tokens": actual_tokens,
                "cost": actual_cost,
                "duration": end_time - start_time
            }
            self.request_history[user_id].append(request_record)

            quota = self.user_quotas[user_id]
            usage_pct = quota.usage_percentage()

            self.console.print(f"✅ [green]請求成功[/green]")
            self.console.print(f"   Tokens: {actual_tokens} (已用 {usage_pct['tokens']:.1f}%)")
            self.console.print(f"   成本: ${actual_cost:.6f} (已用 {usage_pct['cost']:.1f}%)")

            return {
                "success": True,
                "response": response.choices[0].message.content,
                "usage": {
                    "tokens": actual_tokens,
                    "cost": actual_cost
                },
                "quota_info": self._get_quota_info(user_id)
            }

        except Exception as e:
            self.console.print(f"❌ [red]請求失敗: {str(e)}[/red]")
            return {
                "success": False,
                "error": str(e)
            }

    def _calculate_cost(self, response, model: str) -> float:
        """計算請求成本"""
        # 簡化的定價模型
        pricing = {
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        }

        price = pricing.get(model, {"input": 0.001, "output": 0.002})

        input_cost = (response.usage.prompt_tokens / 1000) * price["input"]
        output_cost = (response.usage.completion_tokens / 1000) * price["output"]

        return input_cost + output_cost

    def _update_quota_usage(
        self,
        user_id: str,
        requests: int = 0,
        tokens: int = 0,
        cost: float = 0.0
    ):
        """更新配額使用量"""
        if user_id in self.user_quotas:
            quota = self.user_quotas[user_id]
            quota.used_requests += requests
            quota.used_tokens += tokens
            quota.used_cost_usd += cost

    def _get_quota_info(self, user_id: str) -> Dict:
        """獲取配額信息"""
        if user_id not in self.user_quotas:
            return {}

        quota = self.user_quotas[user_id]
        usage_pct = quota.usage_percentage()

        return {
            "user_id": user_id,
            "tier": quota.tier.value,
            "requests": {
                "used": quota.used_requests,
                "limit": quota.requests_per_day,
                "remaining": quota.remaining_requests(),
                "usage_percent": usage_pct["requests"]
            },
            "tokens": {
                "used": quota.used_tokens,
                "limit": quota.tokens_per_day,
                "remaining": quota.remaining_tokens(),
                "usage_percent": usage_pct["tokens"]
            },
            "cost": {
                "used": quota.used_cost_usd,
                "limit": quota.cost_per_day_usd,
                "remaining": quota.remaining_budget_usd(),
                "usage_percent": usage_pct["cost"]
            }
        }

    def display_quota_status(self, user_id: str):
        """顯示用戶配額狀態"""
        if user_id not in self.user_quotas:
            self.console.print(f"⚠️  [yellow]用戶 {user_id} 沒有配額信息[/yellow]")
            return

        quota = self.user_quotas[user_id]
        usage_pct = quota.usage_percentage()

        # 創建面板
        content = f"""
[bold cyan]用戶 ID:[/bold cyan] {user_id}
[bold cyan]等級:[/bold cyan] {quota.tier.value.upper()}

[bold yellow]請求配額:[/bold yellow]
  已使用: {quota.used_requests:,} / {quota.requests_per_day:,}
  使用率: {usage_pct['requests']:.1f}%
  剩餘: {quota.remaining_requests():,}

[bold yellow]Token 配額:[/bold yellow]
  已使用: {quota.used_tokens:,} / {quota.tokens_per_day:,}
  使用率: {usage_pct['tokens']:.1f}%
  剩餘: {quota.remaining_tokens():,}

[bold yellow]成本配額:[/bold yellow]
  已使用: ${quota.used_cost_usd:.4f} / ${quota.cost_per_day_usd:.2f}
  使用率: {usage_pct['cost']:.1f}%
  剩餘: ${quota.remaining_budget_usd():.4f}

[bold cyan]上次重置:[/bold cyan] {quota.last_reset.strftime('%Y-%m-%d %H:%M:%S')}
        """

        panel = Panel(
            content.strip(),
            title=f"📊 配額狀態",
            border_style="cyan"
        )

        self.console.print(panel)

    def simulate_usage_until_limit(self, user_id: str):
        """
        模擬使用直到達到限制

        這個演示展示了限流如何防止過度使用。
        """
        self.console.print(f"\n🔄 [cyan]模擬用戶 {user_id} 的使用直到達到限制[/cyan]")
        self.console.print("=" * 80)

        quota = self.user_quotas.get(user_id)
        if not quota:
            self.console.print("⚠️  [yellow]用戶沒有配額[/yellow]")
            return

        request_count = 0
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self.console
        ) as progress:
            task = progress.add_task(
                "發送請求...",
                total=quota.requests_per_day
            )

            while True:
                result = self.request_with_rate_limit(
                    user_id=user_id,
                    prompt=f"測試請求 {request_count + 1}",
                    max_tokens=50
                )

                request_count += 1

                if not result["success"]:
                    # 達到限制
                    self.console.print(f"\n🚫 [red]達到限制: {result['error']}[/red]")
                    break

                progress.update(task, advance=1)

                # 避免速率限制
                time.sleep(0.2)

                # 安全退出條件
                if request_count >= quota.requests_per_day:
                    break

        self.console.print(f"\n📊 總共發送了 {request_count} 個請求")
        self.display_quota_status(user_id)

    def generate_usage_report(self) -> pd.DataFrame:
        """生成使用報告"""
        report_data = []

        for user_id, quota in self.user_quotas.items():
            usage_pct = quota.usage_percentage()

            report_data.append({
                "用戶 ID": user_id,
                "等級": quota.tier.value,
                "請求使用率": f"{usage_pct['requests']:.1f}%",
                "Token 使用率": f"{usage_pct['tokens']:.1f}%",
                "成本使用率": f"{usage_pct['cost']:.1f}%",
                "已用成本": f"${quota.used_cost_usd:.4f}",
                "剩餘預算": f"${quota.remaining_budget_usd():.4f}"
            })

        df = pd.DataFrame(report_data)
        return df

    def get_violation_report(self):
        """獲取違規報告"""
        if not self.violations:
            self.console.print("✅ [green]沒有限流違規記錄[/green]")
            return

        self.console.print("\n[bold red]⚠️  限流違規報告[/bold red]")
        self.console.print("=" * 80)

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("時間", style="cyan")
        table.add_column("用戶", style="yellow")
        table.add_column("類型", style="red")
        table.add_column("限制值", justify="right")
        table.add_column("實際值", justify="right")

        for v in self.violations[-10:]:  # 顯示最近 10 條
            table.add_row(
                v.timestamp.strftime("%H:%M:%S"),
                v.user_id,
                v.limit_type,
                str(v.limit_value),
                str(v.actual_value)
            )

        self.console.print(table)
        self.console.print(f"\n總違規次數: {len(self.violations)}")


def demo_basic_rate_limiting():
    """演示基本限流"""
    console = Console()
    console.print("[bold cyan]演示 1: 基本限流控制[/bold cyan]")
    console.print("=" * 80)

    limiter = HeliconeRateLimiter()

    # 創建一個免費用戶
    user_id = "demo_user_001"
    limiter.create_user_quota(user_id, UserTier.FREE)

    # 顯示初始配額
    limiter.display_quota_status(user_id)

    # 發送幾個請求
    console.print("\n發送測試請求...\n")
    for i in range(5):
        console.print(f"請求 {i+1}:")
        limiter.request_with_rate_limit(
            user_id=user_id,
            prompt=f"這是測試請求 {i+1}",
            max_tokens=50
        )
        console.print()
        time.sleep(0.5)

    # 顯示最終配額
    limiter.display_quota_status(user_id)

    return limiter


def demo_tier_comparison():
    """演示不同等級的配額"""
    console = Console()
    console.print("\n[bold cyan]演示 2: 不同用戶等級配額對比[/bold cyan]")
    console.print("=" * 80)

    limiter = HeliconeRateLimiter()

    # 創建不同等級的用戶
    tiers = [UserTier.FREE, UserTier.BASIC, UserTier.PRO, UserTier.ENTERPRISE]

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("等級", style="cyan")
    table.add_column("每日請求", justify="right")
    table.add_column("每日 Tokens", justify="right")
    table.add_column("每日預算", justify="right")

    for i, tier in enumerate(tiers):
        user_id = f"user_tier_{tier.value}"
        quota = limiter.create_user_quota(user_id, tier)

        table.add_row(
            tier.value.upper(),
            f"{quota.requests_per_day:,}",
            f"{quota.tokens_per_day:,}",
            f"${quota.cost_per_day_usd:.2f}"
        )

    console.print(table)


def main():
    """主函數"""
    console = Console()
    console.print("[bold green]🎯 Helicone 限流控制演示[/bold green]\n")

    try:
        # 演示 1: 基本限流
        limiter = demo_basic_rate_limiting()

        # 演示 2: 等級對比
        demo_tier_comparison()

        # 生成報告
        console.print("\n[bold cyan]📊 使用報告[/bold cyan]")
        console.print("=" * 80)
        report = limiter.generate_usage_report()
        console.print(report.to_string(index=False))

        # 違規報告
        limiter.get_violation_report()

        console.print("\n✅ [green]演示完成![/green]")

    except Exception as e:
        console.print(f"\n❌ [red]錯誤: {str(e)}[/red]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

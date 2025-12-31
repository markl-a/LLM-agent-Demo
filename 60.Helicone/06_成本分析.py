"""
Helicone 成本分析與優化
======================

本文件展示如何使用 Helicone 進行詳細的成本追蹤、分析和優化。
有效的成本管理可以幫助您節省高達 90% 的 AI 支出。

主要內容:
1. 實時成本追蹤
2. 成本歸屬分析
3. 成本預測和預算管理
4. 成本優化建議
5. 不同模型成本對比
6. 成本告警系統
7. ROI 分析

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
    from rich.progress import track
    import pandas as pd
    import matplotlib.pyplot as plt
    import numpy as np
except ImportError as e:
    print(f"❌ 缺少必要的依賴: {e}")
    print("請運行: pip install openai rich pandas matplotlib numpy")
    sys.exit(1)


@dataclass
class CostRecord:
    """成本記錄"""
    timestamp: datetime
    user_id: str
    feature: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    input_cost_usd: float
    output_cost_usd: float
    total_cost_usd: float
    request_id: str
    metadata: Dict = field(default_factory=dict)


@dataclass
class CostBudget:
    """成本預算"""
    name: str
    daily_limit_usd: float
    monthly_limit_usd: float
    alert_threshold: float = 0.8  # 80% 時告警
    current_daily_spend: float = 0.0
    current_monthly_spend: float = 0.0
    last_reset_daily: datetime = field(default_factory=datetime.now)
    last_reset_monthly: datetime = field(default_factory=datetime.now)


class CostCategory(Enum):
    """成本類別"""
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"
    RESEARCH = "research"


class HeliconeCostAnalyzer:
    """
    Helicone 成本分析器

    提供全面的成本追蹤、分析和優化功能。
    """

    def __init__(self):
        """初始化成本分析器"""
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

        # 成本記錄
        self.cost_records: List[CostRecord] = []

        # 預算管理
        self.budgets: Dict[str, CostBudget] = {}

        # 定價信息
        self.pricing = self._initialize_pricing()

        # 告警歷史
        self.alerts: List[Dict] = []

        self.console.print("✅ [green]成本分析器已初始化[/green]")

    def _initialize_pricing(self) -> Dict[str, Dict[str, float]]:
        """
        初始化模型定價

        定價單位: 每 1000 tokens 的美元價格
        """
        return {
            "gpt-4": {
                "input": 0.03,
                "output": 0.06,
                "description": "GPT-4 (8K context)"
            },
            "gpt-4-32k": {
                "input": 0.06,
                "output": 0.12,
                "description": "GPT-4 (32K context)"
            },
            "gpt-4-turbo": {
                "input": 0.01,
                "output": 0.03,
                "description": "GPT-4 Turbo (128K context)"
            },
            "gpt-3.5-turbo": {
                "input": 0.0005,
                "output": 0.0015,
                "description": "GPT-3.5 Turbo (4K context)"
            },
            "gpt-3.5-turbo-16k": {
                "input": 0.001,
                "output": 0.002,
                "description": "GPT-3.5 Turbo (16K context)"
            },
            "claude-3-opus": {
                "input": 0.015,
                "output": 0.075,
                "description": "Claude 3 Opus"
            },
            "claude-3-sonnet": {
                "input": 0.003,
                "output": 0.015,
                "description": "Claude 3 Sonnet"
            },
            "claude-3-haiku": {
                "input": 0.00025,
                "output": 0.00125,
                "description": "Claude 3 Haiku"
            }
        }

    def display_pricing_table(self):
        """顯示所有模型的定價"""
        self.console.print("\n[bold cyan]💰 模型定價表[/bold cyan]")
        self.console.print("=" * 80)

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("模型", style="cyan")
        table.add_column("描述", style="yellow")
        table.add_column("輸入 ($/1K tokens)", justify="right")
        table.add_column("輸出 ($/1K tokens)", justify="right")
        table.add_column("相對成本", justify="right")

        # 計算相對成本 (以 GPT-3.5-Turbo 為基準)
        base_cost = self.pricing["gpt-3.5-turbo"]["output"]

        for model, price in self.pricing.items():
            relative_cost = price["output"] / base_cost

            table.add_row(
                model,
                price["description"],
                f"${price['input']:.5f}",
                f"${price['output']:.5f}",
                f"{relative_cost:.1f}x"
            )

        self.console.print(table)

    def calculate_cost(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int
    ) -> Dict[str, float]:
        """
        計算請求成本

        返回詳細的成本分解。
        """
        # 獲取定價,如果模型不在列表中,使用默認價格
        if model in self.pricing:
            price = self.pricing[model]
        else:
            # 嘗試模糊匹配
            matched = False
            for key in self.pricing.keys():
                if key in model.lower():
                    price = self.pricing[key]
                    matched = True
                    break

            if not matched:
                # 默認使用 GPT-3.5-Turbo 價格
                price = self.pricing["gpt-3.5-turbo"]
                self.console.print(f"⚠️  [yellow]未知模型 {model}, 使用默認定價[/yellow]")

        # 計算成本
        input_cost = (prompt_tokens / 1000) * price["input"]
        output_cost = (completion_tokens / 1000) * price["output"]
        total_cost = input_cost + output_cost

        return {
            "input_cost_usd": input_cost,
            "output_cost_usd": output_cost,
            "total_cost_usd": total_cost,
            "cost_per_token": total_cost / (prompt_tokens + completion_tokens) if (prompt_tokens + completion_tokens) > 0 else 0
        }

    def track_request_cost(
        self,
        prompt: str,
        user_id: str,
        feature: str,
        model: str = "gpt-3.5-turbo",
        category: CostCategory = CostCategory.PRODUCTION,
        **kwargs
    ) -> Dict:
        """
        追蹤請求並記錄成本

        這是成本追蹤的核心方法。
        """
        start_time = time.time()

        try:
            # 發送請求
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                extra_headers={
                    "Helicone-User-Id": user_id,
                    "Helicone-Property-Feature": feature,
                    "Helicone-Property-Category": category.value,
                    "Helicone-Property-CostTracking": "true"
                },
                **kwargs
            )

            end_time = time.time()

            # 計算成本
            cost_breakdown = self.calculate_cost(
                model=response.model,
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens
            )

            # 創建成本記錄
            record = CostRecord(
                timestamp=datetime.now(),
                user_id=user_id,
                feature=feature,
                model=response.model,
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens,
                input_cost_usd=cost_breakdown["input_cost_usd"],
                output_cost_usd=cost_breakdown["output_cost_usd"],
                total_cost_usd=cost_breakdown["total_cost_usd"],
                request_id=f"req_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                metadata={
                    "category": category.value,
                    "duration": end_time - start_time
                }
            )

            self.cost_records.append(record)

            # 檢查預算
            self._check_budgets(record)

            # 顯示成本信息
            self.console.print(f"✅ [green]請求完成[/green]")
            self.console.print(f"   Tokens: {response.usage.total_tokens} "
                             f"({response.usage.prompt_tokens} + {response.usage.completion_tokens})")
            self.console.print(f"   成本: ${cost_breakdown['total_cost_usd']:.6f}")

            return {
                "success": True,
                "response": response.choices[0].message.content,
                "cost_record": record,
                "cost_breakdown": cost_breakdown
            }

        except Exception as e:
            self.console.print(f"❌ [red]請求失敗: {str(e)}[/red]")
            return {
                "success": False,
                "error": str(e)
            }

    def _check_budgets(self, record: CostRecord):
        """檢查是否超過預算"""
        for budget_name, budget in self.budgets.items():
            # 更新支出
            budget.current_daily_spend += record.total_cost_usd
            budget.current_monthly_spend += record.total_cost_usd

            # 檢查每日預算
            daily_usage_pct = budget.current_daily_spend / budget.daily_limit_usd
            if daily_usage_pct >= budget.alert_threshold:
                self._trigger_alert(
                    budget_name,
                    "daily",
                    budget.current_daily_spend,
                    budget.daily_limit_usd,
                    daily_usage_pct
                )

            # 檢查每月預算
            monthly_usage_pct = budget.current_monthly_spend / budget.monthly_limit_usd
            if monthly_usage_pct >= budget.alert_threshold:
                self._trigger_alert(
                    budget_name,
                    "monthly",
                    budget.current_monthly_spend,
                    budget.monthly_limit_usd,
                    monthly_usage_pct
                )

    def _trigger_alert(
        self,
        budget_name: str,
        period: str,
        current: float,
        limit: float,
        percentage: float
    ):
        """觸發成本告警"""
        alert = {
            "timestamp": datetime.now(),
            "budget_name": budget_name,
            "period": period,
            "current_spend": current,
            "limit": limit,
            "percentage": percentage * 100,
            "message": f"預算 '{budget_name}' 的{period}支出已達到 {percentage*100:.1f}%"
        }

        self.alerts.append(alert)

        # 顯示告警
        self.console.print(
            f"\n⚠️  [bold red]成本告警![/bold red]",
            style="on red"
        )
        self.console.print(
            f"   {alert['message']}\n"
            f"   當前: ${current:.4f} / ${limit:.2f}"
        )

    def create_budget(
        self,
        name: str,
        daily_limit: float,
        monthly_limit: float,
        alert_threshold: float = 0.8
    ):
        """創建預算"""
        budget = CostBudget(
            name=name,
            daily_limit_usd=daily_limit,
            monthly_limit_usd=monthly_limit,
            alert_threshold=alert_threshold
        )

        self.budgets[name] = budget

        self.console.print(f"✅ [green]已創建預算 '{name}'[/green]")
        self.console.print(f"   每日限額: ${daily_limit:.2f}")
        self.console.print(f"   每月限額: ${monthly_limit:.2f}")
        self.console.print(f"   告警閾值: {alert_threshold*100:.0f}%")

    def get_cost_summary(self, time_period: str = "all") -> Dict:
        """
        獲取成本摘要

        time_period: 'hour', 'day', 'week', 'month', 'all'
        """
        if not self.cost_records:
            return {"message": "沒有成本記錄"}

        # 過濾記錄
        now = datetime.now()
        filtered_records = []

        for record in self.cost_records:
            time_diff = now - record.timestamp

            if time_period == "hour" and time_diff <= timedelta(hours=1):
                filtered_records.append(record)
            elif time_period == "day" and time_diff <= timedelta(days=1):
                filtered_records.append(record)
            elif time_period == "week" and time_diff <= timedelta(weeks=1):
                filtered_records.append(record)
            elif time_period == "month" and time_diff <= timedelta(days=30):
                filtered_records.append(record)
            elif time_period == "all":
                filtered_records.append(record)

        if not filtered_records:
            return {"message": f"在 {time_period} 時間段內沒有記錄"}

        # 計算統計
        total_cost = sum(r.total_cost_usd for r in filtered_records)
        total_tokens = sum(r.total_tokens for r in filtered_records)
        total_requests = len(filtered_records)

        # 按用戶統計
        by_user = defaultdict(float)
        for r in filtered_records:
            by_user[r.user_id] += r.total_cost_usd

        # 按功能統計
        by_feature = defaultdict(float)
        for r in filtered_records:
            by_feature[r.feature] += r.total_cost_usd

        # 按模型統計
        by_model = defaultdict(lambda: {"cost": 0.0, "requests": 0})
        for r in filtered_records:
            by_model[r.model]["cost"] += r.total_cost_usd
            by_model[r.model]["requests"] += 1

        return {
            "time_period": time_period,
            "total_cost_usd": total_cost,
            "total_tokens": total_tokens,
            "total_requests": total_requests,
            "avg_cost_per_request": total_cost / total_requests if total_requests > 0 else 0,
            "avg_tokens_per_request": total_tokens / total_requests if total_requests > 0 else 0,
            "cost_by_user": dict(by_user),
            "cost_by_feature": dict(by_feature),
            "cost_by_model": dict(by_model),
            "earliest_record": min(r.timestamp for r in filtered_records),
            "latest_record": max(r.timestamp for r in filtered_records)
        }

    def display_cost_summary(self, time_period: str = "all"):
        """顯示成本摘要"""
        summary = self.get_cost_summary(time_period)

        if "message" in summary:
            self.console.print(f"⚠️  [yellow]{summary['message']}[/yellow]")
            return

        self.console.print(f"\n[bold cyan]📊 成本摘要 ({summary['time_period']})[/bold cyan]")
        self.console.print("=" * 80)

        # 總體統計
        panel_content = f"""
[bold yellow]總體統計:[/bold yellow]
  總成本: ${summary['total_cost_usd']:.6f}
  總請求: {summary['total_requests']:,}
  總 Tokens: {summary['total_tokens']:,}
  平均每請求成本: ${summary['avg_cost_per_request']:.6f}
  平均每請求 Tokens: {summary['avg_tokens_per_request']:.0f}
        """

        self.console.print(Panel(panel_content.strip(), border_style="cyan"))

        # 按用戶分解
        if summary['cost_by_user']:
            self.console.print("\n[bold yellow]按用戶分解:[/bold yellow]")
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("用戶 ID", style="cyan")
            table.add_column("成本", justify="right", style="green")
            table.add_column("佔比", justify="right")

            for user_id, cost in sorted(summary['cost_by_user'].items(), key=lambda x: x[1], reverse=True):
                percentage = (cost / summary['total_cost_usd']) * 100
                table.add_row(
                    user_id,
                    f"${cost:.6f}",
                    f"{percentage:.1f}%"
                )

            self.console.print(table)

        # 按功能分解
        if summary['cost_by_feature']:
            self.console.print("\n[bold yellow]按功能分解:[/bold yellow]")
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("功能", style="cyan")
            table.add_column("成本", justify="right", style="green")
            table.add_column("佔比", justify="right")

            for feature, cost in sorted(summary['cost_by_feature'].items(), key=lambda x: x[1], reverse=True):
                percentage = (cost / summary['total_cost_usd']) * 100
                table.add_row(
                    feature,
                    f"${cost:.6f}",
                    f"{percentage:.1f}%"
                )

            self.console.print(table)

        # 按模型分解
        if summary['cost_by_model']:
            self.console.print("\n[bold yellow]按模型分解:[/bold yellow]")
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("模型", style="cyan")
            table.add_column("請求數", justify="right")
            table.add_column("成本", justify="right", style="green")
            table.add_column("平均成本", justify="right")

            for model, stats in sorted(summary['cost_by_model'].items(), key=lambda x: x[1]['cost'], reverse=True):
                avg_cost = stats['cost'] / stats['requests'] if stats['requests'] > 0 else 0
                table.add_row(
                    model,
                    str(stats['requests']),
                    f"${stats['cost']:.6f}",
                    f"${avg_cost:.6f}"
                )

            self.console.print(table)

    def compare_model_costs(self, prompt: str, token_estimate: int = 500):
        """
        比較不同模型的成本

        對於相同的任務,計算使用不同模型的預估成本。
        """
        self.console.print("\n[bold cyan]💰 模型成本對比[/bold cyan]")
        self.console.print(f"提示詞: {prompt[:100]}...")
        self.console.print(f"預估 Tokens: {token_estimate}")
        self.console.print("=" * 80)

        # 假設輸入輸出各佔一半
        input_tokens = token_estimate // 2
        output_tokens = token_estimate // 2

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("模型", style="cyan")
        table.add_column("輸入成本", justify="right")
        table.add_column("輸出成本", justify="right")
        table.add_column("總成本", justify="right", style="bold green")
        table.add_column("相對成本", justify="right")

        costs = []
        for model in self.pricing.keys():
            cost = self.calculate_cost(model, input_tokens, output_tokens)
            costs.append((model, cost['total_cost_usd']))

        # 排序
        costs.sort(key=lambda x: x[1])
        min_cost = costs[0][1]

        for model, total_cost in costs:
            cost = self.calculate_cost(model, input_tokens, output_tokens)
            relative = total_cost / min_cost

            color = "green" if relative < 2 else "yellow" if relative < 5 else "red"

            table.add_row(
                model,
                f"${cost['input_cost_usd']:.6f}",
                f"${cost['output_cost_usd']:.6f}",
                f"[{color}]${total_cost:.6f}[/{color}]",
                f"{relative:.1f}x"
            )

        self.console.print(table)

        # 節省建議
        cheapest = costs[0]
        most_expensive = costs[-1]
        savings = most_expensive[1] - cheapest[1]
        savings_pct = (savings / most_expensive[1]) * 100

        self.console.print(
            f"\n💡 [bold green]優化建議:[/bold green] "
            f"使用 {cheapest[0]} 替代 {most_expensive[0]} "
            f"可節省 ${savings:.6f} ({savings_pct:.1f}%)"
        )

    def export_cost_report(self, filename: str = "cost_report.csv"):
        """導出成本報告"""
        if not self.cost_records:
            self.console.print("⚠️  [yellow]沒有成本記錄可導出[/yellow]")
            return

        # 轉換為 DataFrame
        data = []
        for record in self.cost_records:
            data.append({
                "時間": record.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "用戶": record.user_id,
                "功能": record.feature,
                "模型": record.model,
                "輸入Tokens": record.prompt_tokens,
                "輸出Tokens": record.completion_tokens,
                "總Tokens": record.total_tokens,
                "輸入成本": f"${record.input_cost_usd:.6f}",
                "輸出成本": f"${record.output_cost_usd:.6f}",
                "總成本": f"${record.total_cost_usd:.6f}",
                "類別": record.metadata.get("category", "N/A")
            })

        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding='utf-8-sig')

        self.console.print(f"✅ [green]成本報告已導出到 {filename}[/green]")
        self.console.print(f"   共 {len(data)} 條記錄")


def demo_cost_tracking():
    """演示成本追蹤"""
    console = Console()
    console.print("[bold cyan]演示 1: 成本追蹤[/bold cyan]")
    console.print("=" * 80)

    analyzer = HeliconeCostAnalyzer()

    # 顯示定價表
    analyzer.display_pricing_table()

    # 創建預算
    analyzer.create_budget(
        name="開發環境",
        daily_limit=5.0,
        monthly_limit=150.0,
        alert_threshold=0.8
    )

    # 模擬幾個請求
    test_cases = [
        ("user_001", "chat", "gpt-3.5-turbo", "解釋什麼是機器學習"),
        ("user_002", "summarization", "gpt-4", "總結這篇文章的要點"),
        ("user_001", "translation", "gpt-3.5-turbo", "將這段文字翻譯成英文"),
    ]

    console.print("\n發送測試請求...\n")
    for user_id, feature, model, prompt in test_cases:
        analyzer.track_request_cost(
            prompt=prompt,
            user_id=user_id,
            feature=feature,
            model=model,
            max_tokens=200
        )
        console.print()
        time.sleep(0.5)

    # 顯示摘要
    analyzer.display_cost_summary()

    return analyzer


def demo_model_comparison():
    """演示模型成本對比"""
    console = Console()
    console.print("\n[bold cyan]演示 2: 模型成本對比[/bold cyan]")
    console.print("=" * 80)

    analyzer = HeliconeCostAnalyzer()

    # 對比不同模型的成本
    analyzer.compare_model_costs(
        prompt="生成一個詳細的產品描述,包括特性、優勢和使用案例",
        token_estimate=1000
    )


def main():
    """主函數"""
    console = Console()
    console.print("[bold green]🎯 Helicone 成本分析演示[/bold green]\n")

    try:
        # 演示 1: 成本追蹤
        analyzer = demo_cost_tracking()

        # 演示 2: 模型對比
        demo_model_comparison()

        # 導出報告
        analyzer.export_cost_report("helicone_cost_report.csv")

        console.print("\n✅ [green]演示完成![/green]")
        console.print("📊 前往 https://helicone.ai/dashboard 查看詳細成本分析")

    except Exception as e:
        console.print(f"\n❌ [red]錯誤: {str(e)}[/red]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

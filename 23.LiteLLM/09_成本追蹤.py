"""
LiteLLM 成本追蹤範例
===================

本範例展示如何追蹤和管理 LLM API 調用成本。

功能：
1. Token 計數
2. 成本計算
3. 預算管理
4. 使用報告

安裝依賴：
pip install litellm tiktoken
"""

import litellm
from litellm import completion, completion_cost
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json

# ============================================================
# 1. 基本成本計算
# ============================================================

BASIC_COST_EXAMPLE = '''
import litellm
from litellm import completion, completion_cost

# 調用 API
response = litellm.completion(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)

# 計算成本
cost = completion_cost(completion_response=response)
print(f"此次調用成本: ${cost:.6f}")

# 查看 token 使用
print(f"輸入 tokens: {response.usage.prompt_tokens}")
print(f"輸出 tokens: {response.usage.completion_tokens}")
print(f"總 tokens: {response.usage.total_tokens}")
'''


# ============================================================
# 2. 模型定價表
# ============================================================

MODEL_PRICING = {
    # OpenAI
    "gpt-4": {"input": 0.03, "output": 0.06},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},

    # Anthropic
    "claude-3-opus": {"input": 0.015, "output": 0.075},
    "claude-3-sonnet": {"input": 0.003, "output": 0.015},
    "claude-3-haiku": {"input": 0.00025, "output": 0.00125},

    # Google
    "gemini-pro": {"input": 0.00025, "output": 0.0005},
    "gemini-pro-vision": {"input": 0.00025, "output": 0.0005},
}


def get_model_pricing(model: str) -> Dict[str, float]:
    """獲取模型定價"""
    # 嘗試精確匹配
    if model in MODEL_PRICING:
        return MODEL_PRICING[model]

    # 嘗試部分匹配
    for key, pricing in MODEL_PRICING.items():
        if key in model:
            return pricing

    # 默認定價
    return {"input": 0.001, "output": 0.002}


# ============================================================
# 3. 成本追蹤器
# ============================================================

@dataclass
class UsageRecord:
    """使用記錄"""
    timestamp: datetime
    model: str
    prompt_tokens: int
    completion_tokens: int
    cost: float
    request_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class CostTracker:
    """成本追蹤器"""

    def __init__(self):
        self.records: List[UsageRecord] = []
        self.total_cost = 0.0
        self.total_tokens = 0

    def record_usage(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        request_id: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ) -> UsageRecord:
        """記錄使用"""
        pricing = get_model_pricing(model)
        cost = (
            prompt_tokens * pricing["input"] / 1000 +
            completion_tokens * pricing["output"] / 1000
        )

        record = UsageRecord(
            timestamp=datetime.now(),
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost=cost,
            request_id=request_id,
            metadata=metadata or {}
        )

        self.records.append(record)
        self.total_cost += cost
        self.total_tokens += prompt_tokens + completion_tokens

        return record

    def get_summary(self) -> Dict[str, Any]:
        """獲取摘要"""
        by_model = {}
        for record in self.records:
            if record.model not in by_model:
                by_model[record.model] = {
                    "requests": 0,
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "cost": 0.0
                }
            by_model[record.model]["requests"] += 1
            by_model[record.model]["prompt_tokens"] += record.prompt_tokens
            by_model[record.model]["completion_tokens"] += record.completion_tokens
            by_model[record.model]["cost"] += record.cost

        return {
            "total_requests": len(self.records),
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "by_model": by_model
        }

    def get_daily_report(self) -> Dict[str, Any]:
        """獲取每日報告"""
        by_day = {}
        for record in self.records:
            day = record.timestamp.date().isoformat()
            if day not in by_day:
                by_day[day] = {"requests": 0, "tokens": 0, "cost": 0.0}
            by_day[day]["requests"] += 1
            by_day[day]["tokens"] += record.prompt_tokens + record.completion_tokens
            by_day[day]["cost"] += record.cost

        return by_day


# ============================================================
# 4. 預算管理器
# ============================================================

@dataclass
class Budget:
    """預算配置"""
    daily_limit: float = 10.0
    monthly_limit: float = 100.0
    per_request_limit: float = 1.0
    alert_threshold: float = 0.8  # 80% 時告警


class BudgetManager:
    """預算管理器"""

    def __init__(self, budget: Budget):
        self.budget = budget
        self.daily_spend: Dict[str, float] = {}
        self.monthly_spend: Dict[str, float] = {}
        self.alerts: List[Dict[str, Any]] = []

    def _get_today(self) -> str:
        return datetime.now().date().isoformat()

    def _get_month(self) -> str:
        return datetime.now().strftime("%Y-%m")

    def can_spend(self, estimated_cost: float) -> tuple[bool, str]:
        """檢查是否可以花費"""
        today = self._get_today()
        month = self._get_month()

        daily_total = self.daily_spend.get(today, 0) + estimated_cost
        monthly_total = self.monthly_spend.get(month, 0) + estimated_cost

        # 檢查單次請求限制
        if estimated_cost > self.budget.per_request_limit:
            return False, f"超出單次請求限制 (${self.budget.per_request_limit})"

        # 檢查每日限制
        if daily_total > self.budget.daily_limit:
            return False, f"超出每日限制 (${self.budget.daily_limit})"

        # 檢查月度限制
        if monthly_total > self.budget.monthly_limit:
            return False, f"超出月度限制 (${self.budget.monthly_limit})"

        return True, "OK"

    def record_spend(self, cost: float):
        """記錄花費"""
        today = self._get_today()
        month = self._get_month()

        self.daily_spend[today] = self.daily_spend.get(today, 0) + cost
        self.monthly_spend[month] = self.monthly_spend.get(month, 0) + cost

        # 檢查是否需要告警
        self._check_alerts()

    def _check_alerts(self):
        """檢查告警"""
        today = self._get_today()
        month = self._get_month()

        daily_usage = self.daily_spend.get(today, 0) / self.budget.daily_limit
        monthly_usage = self.monthly_spend.get(month, 0) / self.budget.monthly_limit

        if daily_usage >= self.budget.alert_threshold:
            self.alerts.append({
                "type": "daily",
                "usage": daily_usage,
                "timestamp": datetime.now().isoformat()
            })

        if monthly_usage >= self.budget.alert_threshold:
            self.alerts.append({
                "type": "monthly",
                "usage": monthly_usage,
                "timestamp": datetime.now().isoformat()
            })

    def get_status(self) -> Dict[str, Any]:
        """獲取預算狀態"""
        today = self._get_today()
        month = self._get_month()

        return {
            "daily": {
                "spent": self.daily_spend.get(today, 0),
                "limit": self.budget.daily_limit,
                "remaining": self.budget.daily_limit - self.daily_spend.get(today, 0)
            },
            "monthly": {
                "spent": self.monthly_spend.get(month, 0),
                "limit": self.budget.monthly_limit,
                "remaining": self.budget.monthly_limit - self.monthly_spend.get(month, 0)
            },
            "alerts": len(self.alerts)
        }


# ============================================================
# 5. 成本優化建議
# ============================================================

class CostOptimizer:
    """成本優化器"""

    def __init__(self, tracker: CostTracker):
        self.tracker = tracker

    def analyze(self) -> List[Dict[str, Any]]:
        """分析並提供優化建議"""
        recommendations = []
        summary = self.tracker.get_summary()

        # 分析模型使用
        for model, stats in summary.get("by_model", {}).items():
            avg_cost_per_request = stats["cost"] / stats["requests"] if stats["requests"] > 0 else 0

            # 如果使用高成本模型，建議考慮替代
            if "gpt-4" in model and avg_cost_per_request > 0.05:
                recommendations.append({
                    "type": "model_switch",
                    "current_model": model,
                    "suggestion": "考慮對簡單任務使用 gpt-3.5-turbo",
                    "potential_savings": f"可節省約 {avg_cost_per_request * 0.9:.4f}$/請求"
                })

            # 如果輸出 tokens 很多，建議限制
            avg_output = stats["completion_tokens"] / stats["requests"] if stats["requests"] > 0 else 0
            if avg_output > 1000:
                recommendations.append({
                    "type": "output_limit",
                    "model": model,
                    "avg_output_tokens": avg_output,
                    "suggestion": "考慮設置 max_tokens 限制輸出長度"
                })

        return recommendations

    def estimate_cost(
        self,
        model: str,
        prompt_tokens: int,
        max_completion_tokens: int
    ) -> Dict[str, float]:
        """估算成本"""
        pricing = get_model_pricing(model)

        min_cost = prompt_tokens * pricing["input"] / 1000
        max_cost = min_cost + max_completion_tokens * pricing["output"] / 1000

        return {
            "min_cost": min_cost,
            "max_cost": max_cost,
            "estimated_avg": (min_cost + max_cost) / 2
        }


# ============================================================
# 6. 使用報告生成器
# ============================================================

class ReportGenerator:
    """報告生成器"""

    def __init__(self, tracker: CostTracker):
        self.tracker = tracker

    def generate_text_report(self) -> str:
        """生成文本報告"""
        summary = self.tracker.get_summary()
        daily = self.tracker.get_daily_report()

        lines = []
        lines.append("=" * 60)
        lines.append("LLM 使用報告")
        lines.append("=" * 60)

        lines.append(f"\n總請求數: {summary['total_requests']}")
        lines.append(f"總 Tokens: {summary['total_tokens']:,}")
        lines.append(f"總成本: ${summary['total_cost']:.4f}")

        lines.append("\n按模型統計:")
        for model, stats in summary.get("by_model", {}).items():
            lines.append(f"\n  {model}:")
            lines.append(f"    請求數: {stats['requests']}")
            lines.append(f"    Tokens: {stats['prompt_tokens'] + stats['completion_tokens']:,}")
            lines.append(f"    成本: ${stats['cost']:.4f}")

        lines.append("\n每日統計:")
        for day, stats in sorted(daily.items()):
            lines.append(f"  {day}: {stats['requests']} 請求, ${stats['cost']:.4f}")

        lines.append("\n" + "=" * 60)

        return "\n".join(lines)

    def generate_json_report(self) -> str:
        """生成 JSON 報告"""
        return json.dumps({
            "generated_at": datetime.now().isoformat(),
            "summary": self.tracker.get_summary(),
            "daily": self.tracker.get_daily_report()
        }, indent=2)


# ============================================================
# 7. 帶成本追蹤的客戶端
# ============================================================

class CostAwareLLMClient:
    """成本感知 LLM 客戶端"""

    def __init__(self, budget: Budget = None):
        self.tracker = CostTracker()
        self.budget_manager = BudgetManager(budget or Budget())
        self.optimizer = CostOptimizer(self.tracker)

    def completion(
        self,
        model: str,
        messages: List[Dict],
        max_tokens: int = 1000,
        **kwargs
    ) -> Any:
        """帶成本追蹤的完成調用"""
        # 估算成本
        estimated_prompt_tokens = sum(len(m.get("content", "")) // 4 for m in messages)
        estimate = self.optimizer.estimate_cost(model, estimated_prompt_tokens, max_tokens)

        # 檢查預算
        can_spend, reason = self.budget_manager.can_spend(estimate["max_cost"])
        if not can_spend:
            raise Exception(f"預算限制: {reason}")

        # 調用 API
        response = completion(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            **kwargs
        )

        # 記錄使用
        if response.usage:
            record = self.tracker.record_usage(
                model=model,
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens
            )
            self.budget_manager.record_spend(record.cost)

        return response

    def get_report(self) -> str:
        """獲取報告"""
        generator = ReportGenerator(self.tracker)
        return generator.generate_text_report()

    def get_recommendations(self) -> List[Dict[str, Any]]:
        """獲取優化建議"""
        return self.optimizer.analyze()


# ============================================================
# 使用範例
# ============================================================

def example_basic_cost():
    """範例 1: 基本成本計算"""
    print("=" * 50)
    print("範例 1: 基本成本計算")
    print("=" * 50)
    print(BASIC_COST_EXAMPLE)


def example_model_pricing():
    """範例 2: 模型定價"""
    print("\n" + "=" * 50)
    print("範例 2: 模型定價表")
    print("=" * 50)

    print("\n每 1000 tokens 價格 (USD):")
    print(f"{'模型':<25} {'輸入':<10} {'輸出':<10}")
    print("-" * 45)
    for model, pricing in MODEL_PRICING.items():
        print(f"{model:<25} ${pricing['input']:<9.5f} ${pricing['output']:<9.5f}")


def example_cost_tracker():
    """範例 3: 成本追蹤"""
    print("\n" + "=" * 50)
    print("範例 3: 成本追蹤器")
    print("=" * 50)

    tracker = CostTracker()

    # 模擬使用記錄
    tracker.record_usage("gpt-4", 500, 200)
    tracker.record_usage("gpt-3.5-turbo", 1000, 500)
    tracker.record_usage("gpt-4", 300, 150)

    summary = tracker.get_summary()
    print(f"\n總請求: {summary['total_requests']}")
    print(f"總 tokens: {summary['total_tokens']}")
    print(f"總成本: ${summary['total_cost']:.4f}")


def example_budget():
    """範例 4: 預算管理"""
    print("\n" + "=" * 50)
    print("範例 4: 預算管理")
    print("=" * 50)

    budget = Budget(
        daily_limit=10.0,
        monthly_limit=100.0,
        per_request_limit=1.0,
        alert_threshold=0.8
    )

    manager = BudgetManager(budget)

    # 檢查並記錄花費
    can_spend, msg = manager.can_spend(0.5)
    print(f"可以花費 $0.5: {can_spend} ({msg})")

    manager.record_spend(0.5)
    status = manager.get_status()
    print(f"\n預算狀態:")
    print(f"  每日剩餘: ${status['daily']['remaining']:.2f}")
    print(f"  月度剩餘: ${status['monthly']['remaining']:.2f}")


def example_optimizer():
    """範例 5: 成本優化"""
    print("\n" + "=" * 50)
    print("範例 5: 成本優化建議")
    print("=" * 50)

    tracker = CostTracker()
    tracker.record_usage("gpt-4", 2000, 1500)
    tracker.record_usage("gpt-4", 1800, 1200)

    optimizer = CostOptimizer(tracker)
    recommendations = optimizer.analyze()

    print("\n優化建議:")
    for rec in recommendations:
        print(f"  - {rec['type']}: {rec['suggestion']}")


def example_report():
    """範例 6: 使用報告"""
    print("\n" + "=" * 50)
    print("範例 6: 使用報告")
    print("=" * 50)

    tracker = CostTracker()
    tracker.record_usage("gpt-4", 500, 200)
    tracker.record_usage("gpt-3.5-turbo", 1000, 500)

    generator = ReportGenerator(tracker)
    report = generator.generate_text_report()
    print(report)


if __name__ == "__main__":
    print("LiteLLM 成本追蹤範例\n")
    example_basic_cost()
    example_model_pricing()
    example_cost_tracker()
    example_budget()
    example_optimizer()
    example_report()

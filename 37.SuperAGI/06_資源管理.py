"""
SuperAGI 資源管理示例

這個示例展示了如何:
1. 資源分配和限制
2. 預算控制
3. 成本追蹤
4. 限額管理
5. 資源優化

合理的資源管理對生產環境至關重要。
"""

import os
import json
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum


# ==================== 資源類型 ====================

class ResourceType(Enum):
    """資源類型"""
    CPU = "cpu"
    MEMORY = "memory"
    API_CALLS = "api_calls"
    TOKENS = "tokens"
    STORAGE = "storage"
    NETWORK = "network"


# ==================== 資源配額 ====================

@dataclass
class ResourceQuota:
    """資源配額"""
    resource_type: ResourceType
    total: float
    used: float = 0.0
    reserved: float = 0.0

    @property
    def available(self) -> float:
        """可用資源"""
        return self.total - self.used - self.reserved

    @property
    def usage_rate(self) -> float:
        """使用率"""
        return self.used / self.total if self.total > 0 else 0

    def allocate(self, amount: float) -> bool:
        """
        分配資源

        參數:
            amount: 分配數量

        返回:
            是否成功
        """
        if self.available >= amount:
            self.used += amount
            return True
        return False

    def reserve(self, amount: float) -> bool:
        """預留資源"""
        if self.available >= amount:
            self.reserved += amount
            return True
        return False

    def release(self, amount: float):
        """釋放資源"""
        self.used = max(0, self.used - amount)

    def unreserve(self, amount: float):
        """取消預留"""
        self.reserved = max(0, self.reserved - amount)


# ==================== 預算管理器 ====================

class BudgetManager:
    """
    預算管理器

    管理 Agent 的成本預算
    """

    def __init__(self, total_budget: float, currency: str = "USD"):
        """
        初始化預算管理器

        參數:
            total_budget: 總預算
            currency: 貨幣單位
        """
        self.total_budget = total_budget
        self.currency = currency
        self.used_budget = 0.0
        self.transactions: List[Dict] = []

        # 成本模型（示例價格）
        self.cost_model = {
            "gpt-4": {
                "input": 0.03 / 1000,   # per token
                "output": 0.06 / 1000
            },
            "gpt-3.5-turbo": {
                "input": 0.0015 / 1000,
                "output": 0.002 / 1000
            },
            "embedding": 0.0001 / 1000,
            "api_call": 0.001,
            "storage": 0.001  # per MB
        }

    def check_budget(self, estimated_cost: float) -> bool:
        """
        檢查預算

        參數:
            estimated_cost: 預估成本

        返回:
            是否有足夠預算
        """
        return (self.used_budget + estimated_cost) <= self.total_budget

    def allocate(self, amount: float, description: str) -> bool:
        """
        分配預算

        參數:
            amount: 金額
            description: 描述

        返回:
            是否成功
        """
        if not self.check_budget(amount):
            print(f"❌ 預算不足: 需要 ${amount:.4f}, 剩餘 ${self.remaining_budget:.4f}")
            return False

        self.used_budget += amount

        # 記錄交易
        self.transactions.append({
            "timestamp": datetime.now().isoformat(),
            "amount": amount,
            "description": description,
            "remaining": self.remaining_budget
        })

        print(f"💰 分配預算: ${amount:.4f} - {description}")

        return True

    @property
    def remaining_budget(self) -> float:
        """剩餘預算"""
        return self.total_budget - self.used_budget

    @property
    def usage_percentage(self) -> float:
        """使用百分比"""
        return (self.used_budget / self.total_budget) * 100

    def estimate_llm_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """
        估算 LLM 成本

        參數:
            model: 模型名稱
            input_tokens: 輸入 token 數
            output_tokens: 輸出 token 數

        返回:
            預估成本
        """
        if model not in self.cost_model:
            return 0.0

        prices = self.cost_model[model]
        cost = (
            input_tokens * prices["input"] +
            output_tokens * prices["output"]
        )

        return cost

    def get_summary(self) -> Dict:
        """獲取預算摘要"""
        return {
            "total_budget": self.total_budget,
            "used_budget": self.used_budget,
            "remaining_budget": self.remaining_budget,
            "usage_percentage": self.usage_percentage,
            "transaction_count": len(self.transactions),
            "currency": self.currency
        }

    def export_transactions(self, file_path: str):
        """導出交易記錄"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.transactions, f, indent=2, ensure_ascii=False)

        print(f"📊 交易記錄已導出到: {file_path}")


# ==================== 資源管理器 ====================

class ResourceManager:
    """
    資源管理器

    統一管理各種資源
    """

    def __init__(self):
        """初始化資源管理器"""
        self.quotas: Dict[ResourceType, ResourceQuota] = {}
        self.allocations: Dict[str, Dict] = {}  # agent_id -> resources

        # 初始化默認配額
        self._initialize_default_quotas()

    def _initialize_default_quotas(self):
        """初始化默認配額"""
        self.quotas[ResourceType.CPU] = ResourceQuota(ResourceType.CPU, total=100.0)
        self.quotas[ResourceType.MEMORY] = ResourceQuota(ResourceType.MEMORY, total=1000.0)  # MB
        self.quotas[ResourceType.API_CALLS] = ResourceQuota(ResourceType.API_CALLS, total=10000.0)
        self.quotas[ResourceType.TOKENS] = ResourceQuota(ResourceType.TOKENS, total=1000000.0)
        self.quotas[ResourceType.STORAGE] = ResourceQuota(ResourceType.STORAGE, total=10000.0)  # MB

    def allocate_resources(
        self,
        agent_id: str,
        resources: Dict[ResourceType, float]
    ) -> bool:
        """
        為 Agent 分配資源

        參數:
            agent_id: Agent ID
            resources: 資源需求

        返回:
            是否成功
        """
        print(f"\n📦 為 Agent {agent_id} 分配資源...")

        # 檢查是否所有資源都可用
        for resource_type, amount in resources.items():
            if resource_type not in self.quotas:
                print(f"❌ 未知資源類型: {resource_type}")
                return False

            quota = self.quotas[resource_type]
            if quota.available < amount:
                print(f"❌ {resource_type.value} 資源不足")
                print(f"   需要: {amount}, 可用: {quota.available}")
                return False

        # 分配資源
        allocated = {}
        for resource_type, amount in resources.items():
            if self.quotas[resource_type].allocate(amount):
                allocated[resource_type] = amount
                print(f"   ✅ {resource_type.value}: {amount}")
            else:
                # 回滾已分配的資源
                self._rollback_allocation(allocated)
                return False

        # 記錄分配
        self.allocations[agent_id] = {
            "resources": allocated,
            "allocated_at": datetime.now().isoformat()
        }

        return True

    def _rollback_allocation(self, allocated: Dict[ResourceType, float]):
        """回滾資源分配"""
        for resource_type, amount in allocated.items():
            self.quotas[resource_type].release(amount)

    def release_resources(self, agent_id: str):
        """
        釋放 Agent 的資源

        參數:
            agent_id: Agent ID
        """
        if agent_id not in self.allocations:
            return

        allocation = self.allocations[agent_id]

        print(f"\n🔓 釋放 Agent {agent_id} 的資源...")

        for resource_type, amount in allocation["resources"].items():
            self.quotas[resource_type].release(amount)
            print(f"   ✅ {resource_type.value}: {amount}")

        del self.allocations[agent_id]

    def get_resource_stats(self) -> Dict:
        """獲取資源統計"""
        stats = {}

        for resource_type, quota in self.quotas.items():
            stats[resource_type.value] = {
                "total": quota.total,
                "used": quota.used,
                "reserved": quota.reserved,
                "available": quota.available,
                "usage_rate": quota.usage_rate
            }

        return stats

    def get_agent_allocation(self, agent_id: str) -> Optional[Dict]:
        """獲取 Agent 的資源分配"""
        return self.allocations.get(agent_id)


# ==================== 限額管理器 ====================

class RateLimiter:
    """
    限額管理器

    控制 API 調用頻率
    """

    def __init__(self):
        """初始化限額管理器"""
        self.limits: Dict[str, Dict] = {}
        self.usage: Dict[str, List[datetime]] = {}

    def set_limit(
        self,
        key: str,
        max_calls: int,
        time_window: int  # 秒
    ):
        """
        設置限額

        參數:
            key: 限額鍵（如 agent_id, api_name）
            max_calls: 最大調用次數
            time_window: 時間窗口（秒）
        """
        self.limits[key] = {
            "max_calls": max_calls,
            "time_window": time_window
        }

        if key not in self.usage:
            self.usage[key] = []

        print(f"🚦 設置限額: {key} - {max_calls} 次/{time_window}秒")

    def check_limit(self, key: str) -> bool:
        """
        檢查是否超過限額

        參數:
            key: 限額鍵

        返回:
            是否可以執行
        """
        if key not in self.limits:
            return True

        limit = self.limits[key]
        now = datetime.now()

        # 清理過期記錄
        cutoff = now - timedelta(seconds=limit["time_window"])
        self.usage[key] = [
            ts for ts in self.usage[key]
            if ts > cutoff
        ]

        # 檢查是否超限
        current_calls = len(self.usage[key])

        if current_calls >= limit["max_calls"]:
            wait_time = (self.usage[key][0] - cutoff).total_seconds()
            print(f"⏳ 超過限額，需等待 {wait_time:.1f} 秒")
            return False

        return True

    def record_call(self, key: str):
        """記錄調用"""
        if key not in self.usage:
            self.usage[key] = []

        self.usage[key].append(datetime.now())

    def get_remaining_calls(self, key: str) -> int:
        """獲取剩餘調用次數"""
        if key not in self.limits:
            return float('inf')

        limit = self.limits[key]
        now = datetime.now()
        cutoff = now - timedelta(seconds=limit["time_window"])

        current_calls = len([
            ts for ts in self.usage.get(key, [])
            if ts > cutoff
        ])

        return max(0, limit["max_calls"] - current_calls)


# ==================== 成本追蹤器 ====================

class CostTracker:
    """
    成本追蹤器

    詳細追蹤各項成本
    """

    def __init__(self):
        """初始化成本追蹤器"""
        self.costs: Dict[str, List[Dict]] = {
            "llm_calls": [],
            "tool_executions": [],
            "storage": [],
            "network": [],
            "other": []
        }

    def track_llm_call(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost: float
    ):
        """追蹤 LLM 調用成本"""
        self.costs["llm_calls"].append({
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost
        })

    def track_tool_execution(self, tool_name: str, cost: float):
        """追蹤工具執行成本"""
        self.costs["tool_executions"].append({
            "timestamp": datetime.now().isoformat(),
            "tool": tool_name,
            "cost": cost
        })

    def get_total_cost(self) -> float:
        """獲取總成本"""
        total = 0.0

        for category, items in self.costs.items():
            total += sum(item["cost"] for item in items)

        return total

    def get_cost_breakdown(self) -> Dict:
        """獲取成本分解"""
        breakdown = {}

        for category, items in self.costs.items():
            breakdown[category] = sum(item["cost"] for item in items)

        return breakdown

    def generate_report(self) -> str:
        """生成成本報告"""
        total = self.get_total_cost()
        breakdown = self.get_cost_breakdown()

        report = "\n" + "=" * 60 + "\n"
        report += "成本報告\n"
        report += "=" * 60 + "\n\n"

        report += f"總成本: ${total:.4f}\n\n"

        report += "分類成本:\n"
        for category, cost in breakdown.items():
            percentage = (cost / total * 100) if total > 0 else 0
            report += f"  {category:20s}: ${cost:8.4f} ({percentage:5.1f}%)\n"

        report += "\n詳細統計:\n"
        for category, items in self.costs.items():
            report += f"  {category}: {len(items)} 項\n"

        return report


# ==================== 示例場景 ====================

def example_1_budget_management():
    """示例 1: 預算管理"""
    print("\n" + "=" * 60)
    print("示例 1: 預算管理")
    print("=" * 60)

    # 創建預算管理器
    budget = BudgetManager(total_budget=10.0)

    # 估算 LLM 成本
    cost_gpt4 = budget.estimate_llm_cost("gpt-4", 1000, 500)
    print(f"\nGPT-4 成本估算: ${cost_gpt4:.4f} (1000 輸入 + 500 輸出 tokens)")

    cost_gpt35 = budget.estimate_llm_cost("gpt-3.5-turbo", 1000, 500)
    print(f"GPT-3.5 成本估算: ${cost_gpt35:.4f}")

    # 分配預算
    budget.allocate(cost_gpt4, "GPT-4 API 調用")
    budget.allocate(0.05, "數據存儲")
    budget.allocate(0.01, "工具執行")

    # 顯示預算摘要
    summary = budget.get_summary()
    print(f"\n預算摘要:")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


def example_2_resource_allocation():
    """示例 2: 資源分配"""
    print("\n" + "=" * 60)
    print("示例 2: 資源分配")
    print("=" * 60)

    manager = ResourceManager()

    # 為 Agent 分配資源
    success = manager.allocate_resources(
        "agent_1",
        {
            ResourceType.CPU: 10.0,
            ResourceType.MEMORY: 100.0,
            ResourceType.API_CALLS: 100.0,
            ResourceType.TOKENS: 10000.0
        }
    )

    if success:
        print("\n✅ 資源分配成功")

    # 顯示資源統計
    stats = manager.get_resource_stats()
    print(f"\n資源統計:")
    print(json.dumps(stats, indent=2, ensure_ascii=False))

    # 釋放資源
    manager.release_resources("agent_1")

    # 再次顯示統計
    stats = manager.get_resource_stats()
    print(f"\n釋放後資源統計:")
    print(json.dumps(stats, indent=2, ensure_ascii=False))


def example_3_rate_limiting():
    """示例 3: 限額管理"""
    print("\n" + "=" * 60)
    print("示例 3: API 限額管理")
    print("=" * 60)

    limiter = RateLimiter()

    # 設置限額: 每分鐘最多 10 次調用
    limiter.set_limit("openai_api", max_calls=10, time_window=60)

    # 模擬 API 調用
    print("\n模擬 API 調用:")
    for i in range(12):
        if limiter.check_limit("openai_api"):
            limiter.record_call("openai_api")
            remaining = limiter.get_remaining_calls("openai_api")
            print(f"  調用 {i+1}: ✅ 成功 (剩餘: {remaining})")
        else:
            print(f"  調用 {i+1}: ❌ 超過限額")

        time.sleep(0.1)


def example_4_cost_tracking():
    """示例 4: 成本追蹤"""
    print("\n" + "=" * 60)
    print("示例 4: 成本追蹤")
    print("=" * 60)

    tracker = CostTracker()

    # 追蹤各種成本
    tracker.track_llm_call("gpt-4", 1000, 500, 0.045)
    tracker.track_llm_call("gpt-4", 800, 400, 0.036)
    tracker.track_llm_call("gpt-3.5-turbo", 2000, 1000, 0.005)

    tracker.track_tool_execution("GoogleSearchTool", 0.01)
    tracker.track_tool_execution("FileWriteTool", 0.002)

    # 生成報告
    report = tracker.generate_report()
    print(report)


def example_5_comprehensive():
    """示例 5: 綜合資源管理"""
    print("\n" + "=" * 60)
    print("示例 5: 綜合資源管理示例")
    print("=" * 60)

    # 初始化各個管理器
    budget = BudgetManager(total_budget=20.0)
    resource_mgr = ResourceManager()
    rate_limiter = RateLimiter()
    cost_tracker = CostTracker()

    # 設置限額
    rate_limiter.set_limit("agent_1", max_calls=100, time_window=60)

    # 分配資源
    print("\n步驟 1: 分配資源")
    resource_mgr.allocate_resources(
        "agent_1",
        {
            ResourceType.CPU: 20.0,
            ResourceType.MEMORY: 200.0,
            ResourceType.API_CALLS: 100.0
        }
    )

    # 模擬 Agent 執行
    print("\n步驟 2: 模擬 Agent 執行")
    for i in range(5):
        # 檢查限額
        if not rate_limiter.check_limit("agent_1"):
            print(f"  迭代 {i+1}: 超過限額")
            break

        # 估算成本
        cost = budget.estimate_llm_cost("gpt-4", 500, 250)

        # 檢查預算
        if not budget.check_budget(cost):
            print(f"  迭代 {i+1}: 預算不足")
            break

        # 分配預算
        budget.allocate(cost, f"迭代 {i+1} LLM 調用")

        # 記錄調用
        rate_limiter.record_call("agent_1")

        # 追蹤成本
        cost_tracker.track_llm_call("gpt-4", 500, 250, cost)

        print(f"  迭代 {i+1}: ✅ 成功")

    # 顯示最終統計
    print("\n步驟 3: 最終統計")
    print(f"\n預算使用: {budget.usage_percentage:.1f}%")
    print(f"剩餘調用次數: {rate_limiter.get_remaining_calls('agent_1')}")

    print(cost_tracker.generate_report())


# ==================== 主函數 ====================

def main():
    """主函數"""
    print("\n" + "💰 " * 20)
    print("SuperAGI 資源管理教程")
    print("💰 " * 20)

    try:
        # 示例 1: 預算管理
        example_1_budget_management()

        # 示例 2: 資源分配
        example_2_resource_allocation()

        # 示例 3: 限額管理
        example_3_rate_limiting()

        # 示例 4: 成本追蹤
        example_4_cost_tracking()

        # 示例 5: 綜合示例
        example_5_comprehensive()

        print("\n" + "=" * 60)
        print("✅ 所有資源管理示例執行完成！")
        print("=" * 60)

        print("""
        資源管理最佳實踐:

        1. 設置合理的預算上限
        2. 實時監控資源使用
        3. 實施 API 調用限額
        4. 追蹤詳細成本數據
        5. 定期生成成本報告
        6. 優化資源分配策略
        7. 實現自動告警機制
        """)

    except Exception as e:
        print(f"\n❌ 執行出錯: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

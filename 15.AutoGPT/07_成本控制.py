#!/usr/bin/env python3
"""AutoGPT - 成本控制示例"""

class CostController:
    def __init__(self, budget: float):
        self.budget = budget
        self.spent = 0.0

    def check_budget(self, cost: float) -> bool:
        if self.spent + cost <= self.budget:
            self.spent += cost
            print(f"💰 花費: ${cost:.4f}, 剩餘: ${self.budget - self.spent:.4f}")
            return True
        print(f"⚠️  預算不足！需要 ${cost:.4f}, 剩餘 ${self.budget - self.spent:.4f}")
        return False

controller = CostController(budget=1.0)
controller.check_budget(0.05)  # API 調用
controller.check_budget(0.03)  # API 調用
print(f"\n✅ 總花費: ${controller.spent:.4f}")

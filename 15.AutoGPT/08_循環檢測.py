#!/usr/bin/env python3
"""AutoGPT - 循環檢測示例"""

class LoopDetector:
    def __init__(self, max_repeats=3):
        self.history = []
        self.max_repeats = max_repeats

    def check_loop(self, action: str) -> bool:
        self.history.append(action)

        # 檢查最近的重複
        recent = self.history[-self.max_repeats:]
        if len(recent) == self.max_repeats and len(set(recent)) == 1:
            print(f"🔄 檢測到循環: {action} 重複 {self.max_repeats} 次")
            return True
        return False

detector = LoopDetector()

actions = ["搜索", "搜索", "搜索", "分析"]
for action in actions:
    if detector.check_loop(action):
        print("  → 需要改變策略")
        break

print("\n✅ 循環檢測完成")

#!/usr/bin/env python3
"""AutoGPT - 自我反思示例"""

class SelfReflection:
    def reflect_on_action(self, action: str, result: str) -> str:
        """反思行動結果"""
        print(f"🤔 反思行動: {action}")
        print(f"📊 結果: {result}")

        if "成功" in result:
            return "✅ 行動有效，繼續"
        elif "失敗" in result:
            return "❌ 需要調整策略"
        else:
            return "⚠️  結果不明確，需要更多信息"

reflection = SelfReflection()

actions = [
    ("搜索資料", "成功找到10篇相關文章"),
    ("編寫代碼", "失敗：缺少依賴"),
]

for action, result in actions:
    feedback = reflection.reflect_on_action(action, result)
    print(f"💡 反思: {feedback}\n")

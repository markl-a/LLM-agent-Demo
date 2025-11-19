#!/usr/bin/env python3
"""OpenAI Swarm - 上下文變量示例"""

class ContextVariables:
    """上下文變量管理"""

    def __init__(self):
        self.data = {}

    def set(self, key: str, value):
        self.data[key] = value
        print(f"📝 設置: {key} = {value}")

    def get(self, key: str):
        return self.data.get(key)

# 使用示例
context = ContextVariables()
context.set("user_name", "張三")
context.set("user_plan", "專業版")
context.set("conversation_id", "conv_123")

print(f"\n✅ 上下文變量: {len(context.data)} 個")
print("💡 在 Agent 間共享狀態")

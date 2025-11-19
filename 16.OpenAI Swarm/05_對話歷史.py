#!/usr/bin/env python3
"""OpenAI Swarm - 對話歷史管理"""

class ConversationHistory:
    def __init__(self):
        self.messages = []

    def add(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})

    def get_recent(self, n: int = 10):
        return self.messages[-n:]

history = ConversationHistory()
history.add("user", "你好")
history.add("assistant", "您好！有什麼可以幫助您的？")
history.add("user", "推薦產品")

print(f"💬 對話歷史: {len(history.messages)} 條消息")
print("✅ 保持對話上下文")

#!/usr/bin/env python3
"""OpenAI Swarm - 多輪對話"""

class MultiTurnConversation:
    def __init__(self):
        self.turns = []

    def add_turn(self, user: str, assistant: str):
        self.turns.append({"user": user, "assistant": assistant})

    def get_context(self):
        return "\n".join([f"用戶: {t['user']}\n助手: {t['assistant']}" for t in self.turns])

conv = MultiTurnConversation()
conv.add_turn("我想買手機", "請問您的預算是多少？")
conv.add_turn("5000元左右", "我為您推薦以下機型...")

print(conv.get_context())
print(f"\n✅ {len(conv.turns)} 輪對話")

#!/usr/bin/env python3
"""OpenAI Swarm - 狀態管理"""

class StateManager:
    def __init__(self):
        self.state = {"current_agent": None, "context": {}}

    def update(self, key, value):
        self.state[key] = value

    def get(self, key):
        return self.state.get(key)

sm = StateManager()
sm.update("current_agent", "銷售專員")
sm.update("user_intent", "購買")
print(f"✅ 狀態管理: {len(sm.state)} 個狀態變量")

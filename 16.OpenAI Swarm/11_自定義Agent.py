#!/usr/bin/env python3
"""OpenAI Swarm - 自定義 Agent"""

class CustomAgent:
    def __init__(self, name: str, specialty: str):
        self.name = name
        self.specialty = specialty
        self.tools = []

    def add_tool(self, tool):
        self.tools.append(tool)

    def process(self, message: str):
        return f"{self.name} ({self.specialty}): 處理 '{message}'"

agent = CustomAgent("專業顧問", "技術諮詢")
agent.add_tool(lambda x: x * 2)

print(agent.process("用戶詢問"))
print(f"✅ 自定義 Agent 包含 {len(agent.tools)} 個工具")

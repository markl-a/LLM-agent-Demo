#!/usr/bin/env python3
"""OpenAI Swarm - 工作流程"""

class Workflow:
    def __init__(self):
        self.steps = []

    def add_step(self, agent_name: str, action: str):
        self.steps.append({" agent": agent_name, "action": action})

    def execute(self):
        for i, step in enumerate(self.steps, 1):
            print(f"步驟 {i}: {step['agent']} - {step['action']}")

wf = Workflow()
wf.add_step("接待員", "歡迎用戶")
wf.add_step("顧問", "提供建議")
wf.add_step("銷售", "完成交易")
wf.execute()
print("\n✅ 工作流程執行完成")

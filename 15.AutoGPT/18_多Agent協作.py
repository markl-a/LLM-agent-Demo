#!/usr/bin/env python3
"""AutoGPT - 多 Agent 協作"""

class AgentTeam:
    def __init__(self):
        self.agents = {}

    def add_agent(self, name: str, role: str):
        self.agents[name] = {"role": role, "tasks": []}
        print(f"➕ 添加 Agent: {name} ({role})")

    def assign_task(self, agent_name: str, task: str):
        if agent_name in self.agents:
            self.agents[agent_name]["tasks"].append(task)

    def collaborate(self):
        print("\n🤝 Agent 協作:")
        for name, info in self.agents.items():
            print(f"  {name} ({info['role']}): {len(info['tasks'])} 個任務")

team = AgentTeam()
team.add_agent("研究員", "數據收集")
team.add_agent("分析師", "數據分析")
team.assign_task("研究員", "收集市場數據")
team.collaborate()
print("\n✅ 協作完成")

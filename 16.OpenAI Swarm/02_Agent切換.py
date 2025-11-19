#!/usr/bin/env python3
"""OpenAI Swarm - Agent 切換示例"""

from typing import Optional

class Agent:
    def __init__(self, name: str, instructions: str):
        self.name = name
        self.instructions = instructions

def transfer_to_sales():
    """轉接到銷售 Agent"""
    return Agent(name="銷售專員", instructions="協助客戶購買產品")

def transfer_to_support():
    """轉接到客服 Agent"""
    return Agent(name="技術支持", instructions="解決技術問題")

# 路由 Agent
router = Agent(
    name="路由員",
    instructions="根據客戶需求轉接到合適的 Agent"
)

print("🔀 Agent 切換系統")
print(f"路由員 → 銷售專員")
print(f"路由員 → 技術支持")
print("\n✅ 支持動態 Agent 切換")

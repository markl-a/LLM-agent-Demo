#!/usr/bin/env python3
"""Haystack - Agent 代理示例"""
from haystack.components.agents import ToolInvokingAgent, Tool

def calculator(expression: str) -> float:
    """計算器工具"""
    return eval(expression)

tool = Tool(name="calculator", description="計算數學表達式", function=calculator)
print("✅ 計算器工具已創建")

# agent = ToolInvokingAgent(tools=[tool])
print("✅ Agent 可使用工具完成任務")

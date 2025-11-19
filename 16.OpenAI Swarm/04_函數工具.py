#!/usr/bin/env python3
"""OpenAI Swarm - 函數工具示例"""

def get_weather(location: str) -> str:
    """獲取天氣"""
    return f"{location} 的天氣：晴天，25°C"

def search_products(query: str, max_results: int = 5) -> list:
    """搜索產品"""
    return [f"產品 {i+1}: {query}" for i in range(max_results)]

def calculate(expression: str) -> float:
    """計算器"""
    try:
        return eval(expression)
    except:
        return 0.0

# 工具列表
tools = [get_weather, search_products, calculate]

print("🔧 可用工具:")
for tool in tools:
    print(f"  - {tool.__name__}: {tool.__doc__}")

print("\n✅ Agent 可調用這些工具")

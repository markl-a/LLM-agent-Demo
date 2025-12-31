"""
Mirascope 工具調用示例
運行方式：python 04_工具調用.py
"""
import os
from mirascope.openai import OpenAICall

def get_weather(city: str) -> str:
    """獲取城市天氣"""
    return f"{city} 的天氣是晴天，25°C"

def calculate(operation: str, a: float, b: float) -> float:
    """執行計算"""
    if operation == "add":
        return a + b
    elif operation == "multiply":
        return a * b
    return 0

class WeatherAssistant(OpenAICall):
    prompt_template = "用戶問題：{question}"
    question: str
    call_params = {"tools": [get_weather]}

class Calculator(OpenAICall):
    prompt_template = "計算：{expression}"
    expression: str
    call_params = {"tools": [calculate]}

def main():
    print("\\nMirascope 工具調用示例\\n")
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 請設置 OPENAI_API_KEY")
        return
    
    print("示例 1: 天氣查詢工具")
    print("(工具調用功能演示)")
    
    print("\\n示例 2: 計算器工具")
    print("(工具調用功能演示)")
    
    print("\\n✅ 示例完成")

if __name__ == "__main__":
    main()

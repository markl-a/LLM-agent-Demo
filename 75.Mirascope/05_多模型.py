"""
Mirascope 多模型支持示例
運行方式：python 05_多模型.py
"""
import os
from mirascope.openai import OpenAICall

class OpenAIChat(OpenAICall):
    prompt_template = "你好，{name}"
    name: str
    call_params = {"model": "gpt-3.5-turbo"}

class GPT4Chat(OpenAICall):
    prompt_template = "分析：{topic}"
    topic: str
    call_params = {"model": "gpt-4"}

def main():
    print("\\nMirascope 多模型支持示例\\n")
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 請設置 OPENAI_API_KEY")
        return
    
    print("示例 1: GPT-3.5 Turbo")
    try:
        response = OpenAIChat(name="世界").call()
        print(f"  {response.content[:50]}...")
    except Exception as e:
        print(f"❌ 錯誤: {e}")
    
    print("\\n示例 2: GPT-4")
    try:
        response = GPT4Chat(topic="人工智能").call()
        print(f"  {response.content[:50]}...")
    except Exception as e:
        print(f"❌ 錯誤: {e}")
    
    print("\\n✅ 示例完成")

if __name__ == "__main__":
    main()

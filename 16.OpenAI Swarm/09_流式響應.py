#!/usr/bin/env python3
"""OpenAI Swarm - 流式響應"""

def stream_response(text: str):
    """模擬流式輸出"""
    for char in text:
        print(char, end="", flush=True)
    print()

print("🔄 流式響應示例:")
stream_response("這是一個流式輸出的回答...")
print("\n✅ 支持實時流式響應")

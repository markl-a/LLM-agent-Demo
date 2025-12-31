"""
Mirascope 流式輸出示例
運行方式：python 06_流式輸出.py
"""
import os
from mirascope.openai import OpenAICall

class StreamingWriter(OpenAICall):
    prompt_template = "寫一個關於{topic}的故事"
    topic: str

def main():
    print("\\nMirascope 流式輸出示例\\n")
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 請設置 OPENAI_API_KEY")
        return
    
    print("示例: 流式生成故事")
    try:
        call = StreamingWriter(topic="未來科技")
        stream = call.stream()
        
        print("生成中: ", end="", flush=True)
        for chunk in stream:
            if hasattr(chunk, 'content') and chunk.content:
                print(chunk.content, end="", flush=True)
        print("\\n")
    except Exception as e:
        print(f"❌ 錯誤: {e}")
    
    print("✅ 示例完成")

if __name__ == "__main__":
    main()

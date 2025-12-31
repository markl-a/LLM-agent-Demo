"""
Mirascope 重試機制示例
運行方式：python 07_重試機制.py
"""
import os
from mirascope.openai import OpenAICall
from tenacity import retry, stop_after_attempt, wait_exponential

class RobustCall(OpenAICall):
    prompt_template = "處理：{data}"
    data: str
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def call(self):
        return super().call()

def main():
    print("\\nMirascope 重試機制示例\\n")
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 請設置 OPENAI_API_KEY")
        return
    
    print("示例: 帶重試的調用")
    try:
        response = RobustCall(data="測試數據").call()
        print(f"  成功: {response.content[:50]}...")
    except Exception as e:
        print(f"❌ 所有重試都失敗: {e}")
    
    print("\\n✅ 示例完成")

if __name__ == "__main__":
    main()

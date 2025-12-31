"""
流式輸出示例
演示如何實現打字機效果，逐字顯示 AI 回復
"""

import os
import sys
from openai import OpenAI

# 初始化客戶端
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def main():
    print("=" * 50)
    print("流式輸出示例（打字機效果）")
    print("=" * 50)

    question = "請用 50 字介紹 Python 編程語言的特點"
    print(f"\n問題：{question}")
    print(f"回答：", end="", flush=True)

    # 使用 stream=True 啟用流式輸出
    stream = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": question}],
        stream=True  # 關鍵參數：啟用流式輸出
    )

    # 逐塊接收並打印內容
    full_response = ""
    for chunk in stream:
        # 檢查是否有內容
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            full_response += content
            # 實時打印，不換行
            print(content, end="", flush=True)

    print("\n")
    print("=" * 50)
    print(f"\n完整回答：{full_response}\n")

if __name__ == "__main__":
    main()

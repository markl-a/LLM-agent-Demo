"""
最簡單的 OpenAI API 調用示例
演示如何使用 GPT 模型進行基礎對話
"""

import os
from openai import OpenAI

# 初始化 OpenAI 客戶端
# API key 從環境變量讀取：export OPENAI_API_KEY="your-key"
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def main():
    print("=" * 50)
    print("OpenAI GPT 基礎調用示例")
    print("=" * 50)

    # 發送簡單的對話請求
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # 使用 GPT-3.5 模型
        messages=[
            {"role": "user", "content": "用一句話介紹什麼是人工智能"}
        ]
    )

    # 提取並打印回復
    answer = response.choices[0].message.content
    print(f"\n問題：用一句話介紹什麼是人工智能")
    print(f"回答：{answer}\n")
    print("=" * 50)

if __name__ == "__main__":
    main()

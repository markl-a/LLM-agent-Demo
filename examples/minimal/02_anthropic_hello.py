"""
最簡單的 Anthropic Claude API 調用示例
演示如何使用 Claude 模型進行基礎對話
"""

import os
from anthropic import Anthropic

# 初始化 Anthropic 客戶端
# API key 從環境變量讀取：export ANTHROPIC_API_KEY="your-key"
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def main():
    print("=" * 50)
    print("Anthropic Claude 基礎調用示例")
    print("=" * 50)

    # 發送簡單的對話請求
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",  # 使用 Claude 3.5 Sonnet 模型
        max_tokens=1024,
        messages=[
            {"role": "user", "content": "用一句話介紹什麼是機器學習"}
        ]
    )

    # 提取並打印回復
    answer = message.content[0].text
    print(f"\n問題：用一句話介紹什麼是機器學習")
    print(f"回答：{answer}\n")
    print("=" * 50)

if __name__ == "__main__":
    main()

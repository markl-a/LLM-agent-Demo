"""
最簡單的 Agent 實現
演示 Agent 的核心概念：感知、決策、執行
"""

import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class SimpleAgent:
    """簡單的 Agent 類"""

    def __init__(self, name):
        self.name = name
        self.memory = []  # 記憶（對話歷史）

    def perceive(self, user_input):
        """感知：接收用戶輸入"""
        print(f"\n[{self.name}] 接收到：{user_input}")
        self.memory.append({"role": "user", "content": user_input})

    def think(self):
        """思考：使用 LLM 進行決策"""
        print(f"[{self.name}] 正在思考...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=self.memory
        )
        answer = response.choices[0].message.content
        self.memory.append({"role": "assistant", "content": answer})
        return answer

    def act(self, response):
        """行動：輸出回復"""
        print(f"[{self.name}] 回答：{response}\n")

    def run(self, user_input):
        """完整的感知-思考-行動循環"""
        self.perceive(user_input)
        response = self.think()
        self.act(response)
        return response

def main():
    print("=" * 50)
    print("簡單 Agent 示例")
    print("=" * 50)

    # 創建一個 AI 助手 Agent
    agent = SimpleAgent("AI助手")

    # 進行多輪對話
    agent.run("你好，請介紹一下你自己")
    agent.run("你剛才說了什麼？")  # Agent 會記住上下文

    print("=" * 50)

if __name__ == "__main__":
    main()

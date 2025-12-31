"""
最簡單的多 Agent 協作示例
演示兩個 Agent 如何協作完成任務
"""

import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class Agent:
    """基礎 Agent 類"""

    def __init__(self, name, role):
        self.name = name
        self.role = role

    def process(self, input_text):
        """處理輸入並生成輸出"""
        print(f"\n[{self.name}] 開始工作...")

        # 根據角色定制提示詞
        prompt = f"""你是一個{self.role}。

任務：{input_text}

請按照你的角色完成任務。"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )

        result = response.choices[0].message.content
        print(f"[{self.name}] 完成：{result[:100]}...")  # 只顯示前100字
        return result

class MultiAgentSystem:
    """多 Agent 協作系統"""

    def __init__(self):
        self.agents = []

    def add_agent(self, agent):
        """添加 Agent"""
        self.agents.append(agent)
        print(f"添加 Agent：{agent.name} ({agent.role})")

    def run(self, task):
        """按順序執行所有 Agent"""
        print("\n" + "=" * 50)
        print(f"任務：{task}")
        print("=" * 50)

        result = task
        for agent in self.agents:
            # 每個 Agent 處理上一個 Agent 的輸出
            result = agent.process(result)

        return result

def main():
    print("=" * 50)
    print("多 Agent 協作示例")
    print("=" * 50)

    # 創建多 Agent 系統
    system = MultiAgentSystem()

    # 添加多個專業 Agent
    system.add_agent(Agent("策劃師", "創意策劃專家，負責構思創意方案"))
    system.add_agent(Agent("撰稿人", "文案撰寫專家，負責將創意轉化為文案"))
    system.add_agent(Agent("審核員", "內容審核專家，負責檢查並優化文案"))

    # 執行協作任務
    task = "為一款新的 AI 編程助手工具寫一句廣告語"
    final_result = system.run(task)

    print("\n" + "=" * 50)
    print("最終結果：")
    print(final_result)
    print("=" * 50)

if __name__ == "__main__":
    main()

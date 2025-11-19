"""
CrewAI 示例 01: 快速開始

這個示例展示如何創建你的第一個 CrewAI Agent 和 Task。
我們將創建一個簡單的研究團隊，包含一個研究員 Agent 來收集信息。

CrewAI 核心概念:
- Agent: 具有角色、目標和背景的 AI 智能體
- Task: 分配給 Agent 的具體任務
- Crew: 協同工作的 Agents 團隊

官方文檔: https://docs.crewai.com/
"""

import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process

# 加載環境變量
load_dotenv()

# 確保 OpenAI API Key 已設置
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("請設置 OPENAI_API_KEY 環境變量")


def create_research_agent():
    """
    創建一個研究員 Agent

    Agent 的關鍵屬性:
    - role: Agent 的角色定位
    - goal: Agent 的目標
    - backstory: Agent 的背景故事（影響行為方式）
    - verbose: 是否顯示詳細輸出
    - allow_delegation: 是否允許委託任務給其他 Agent
    """
    researcher = Agent(
        role="高級研究員",
        goal="發現並分析關於 {topic} 的最新信息和趨勢",
        backstory="""你是一位經驗豐富的研究員，擅長從各種來源收集和分析信息。
        你對細節有敏銳的洞察力，能夠識別重要的模式和趨勢。
        你的研究報告總是準確、全面且易於理解。""",
        verbose=True,
        allow_delegation=False  # 這個簡單示例不需要委託
    )

    return researcher


def create_research_task(agent):
    """
    創建一個研究任務

    Task 的關鍵屬性:
    - description: 任務的詳細描述
    - expected_output: 期望的輸出格式
    - agent: 執行任務的 Agent
    """
    task = Task(
        description="""對 {topic} 進行深入研究。

        你的研究應該包括:
        1. 定義和基本概念
        2. 當前的主要趨勢
        3. 關鍵的應用場景
        4. 未來的發展方向

        請提供清晰、結構化的研究報告。""",

        expected_output="""一份結構化的研究報告，包含:
        - 概述（2-3 句話）
        - 主要發現（3-5 個要點）
        - 具體應用（2-3 個例子）
        - 未來展望（1-2 段）""",

        agent=agent
    )

    return task


def create_crew(agent, task):
    """
    創建一個 Crew（團隊）

    Crew 的關鍵屬性:
    - agents: Agent 列表
    - tasks: Task 列表
    - process: 執行流程（Sequential 或 Hierarchical）
    - verbose: 是否顯示詳細輸出
    """
    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,  # 順序執行任務
        verbose=True
    )

    return crew


def main():
    """主函數：創建並運行 CrewAI 團隊"""

    print("=" * 60)
    print("CrewAI 快速開始示例")
    print("=" * 60)
    print()

    # 步驟 1: 創建 Agent
    print("📝 步驟 1: 創建研究員 Agent")
    print("-" * 60)
    researcher = create_research_agent()
    print(f"✅ 創建了角色為 '{researcher.role}' 的 Agent")
    print()

    # 步驟 2: 創建 Task
    print("📋 步驟 2: 創建研究任務")
    print("-" * 60)
    research_task = create_research_task(researcher)
    print("✅ 創建了研究任務")
    print()

    # 步驟 3: 創建 Crew
    print("👥 步驟 3: 組建研究團隊")
    print("-" * 60)
    crew = create_crew(researcher, research_task)
    print("✅ 團隊組建完成")
    print()

    # 步驟 4: 執行任務
    print("🚀 步驟 4: 開始執行研究任務")
    print("-" * 60)

    # 定義研究主題
    topic = "AI Agent 框架"

    print(f"研究主題: {topic}")
    print()

    try:
        # 運行 Crew（傳入變量）
        result = crew.kickoff(inputs={"topic": topic})

        print()
        print("=" * 60)
        print("📊 研究結果")
        print("=" * 60)
        print()
        print(result)
        print()

        # 顯示使用統計
        print("=" * 60)
        print("📈 執行統計")
        print("=" * 60)
        print(f"✅ 任務完成")
        print(f"👤 參與 Agents: 1")
        print(f"📋 完成任務: 1")

    except Exception as e:
        print(f"❌ 執行過程中出現錯誤: {str(e)}")
        print("\n提示: 請確保已設置 OPENAI_API_KEY 環境變量")


if __name__ == "__main__":
    main()


"""
運行說明:
----------
1. 安裝依賴:
   pip install crewai crewai-tools openai python-dotenv

2. 設置環境變量:
   export OPENAI_API_KEY="your-api-key-here"

3. 運行腳本:
   python 01_快速開始.py

關鍵概念:
----------
1. Agent（智能體）:
   - role: 定義 Agent 的專業角色
   - goal: Agent 要達成的目標
   - backstory: 影響 Agent 行為的背景故事
   - verbose: 控制輸出詳細程度
   - allow_delegation: 是否可以委託給其他 Agent

2. Task（任務）:
   - description: 詳細的任務說明（可使用變量 {topic}）
   - expected_output: 明確的輸出要求
   - agent: 負責執行的 Agent

3. Crew（團隊）:
   - agents: 團隊成員列表
   - tasks: 要完成的任務列表
   - process: Sequential（順序）或 Hierarchical（層級）
   - kickoff(): 啟動任務執行

CrewAI 的優勢:
--------------
✅ 角色扮演: 每個 Agent 都有獨特的角色和個性
✅ 簡單易用: 幾行代碼就能創建一個 AI 團隊
✅ 靈活擴展: 輕鬆添加更多 Agents 和 Tasks
✅ 自動協作: Agents 會自動協調完成任務

下一步:
-------
- 02_角色定義.py: 學習如何設計更豐富的 Agent 角色
- 03_任務設計.py: 創建複雜的多步驟任務
- 04_團隊組建.py: 構建多 Agent 協作團隊
"""

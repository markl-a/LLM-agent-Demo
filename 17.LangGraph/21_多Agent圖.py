#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LangGraph 示例 21: 多Agent圖

本示例展示:
1. 多個 Agent 的協作圖結構
2. Agent 之間的消息傳遞
3. 協調者模式 (Supervisor Pattern)
4. 角色分工與專業化

學習重點:
- 多 Agent 系統設計
- Agent 通信機制
- 任務分配與協調
- 團隊協作模式
"""

from typing import TypedDict, Annotated, Literal, List
import operator
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import os
from dotenv import load_dotenv

load_dotenv()


# ============================================
# 1. 定義多Agent狀態
# ============================================

class MultiAgentState(TypedDict):
    """
    多Agent協作狀態

    包含:
    - messages: 消息歷史
    - current_agent: 當前活躍的 Agent
    - task: 當前任務描述
    - results: 各 Agent 的結果
    - next_action: 下一步動作
    """
    messages: Annotated[list, operator.add]
    current_agent: str
    task: str
    results: dict
    next_action: str


# ============================================
# 2. 定義各個專業Agent
# ============================================

class ResearchAgent:
    """研究員 Agent - 負責資料搜集和研究"""

    def __init__(self, llm):
        self.llm = llm
        self.name = "研究員"
        self.role = "負責搜集資料、進行研究分析"

    def run(self, state: MultiAgentState) -> MultiAgentState:
        """執行研究任務"""
        print(f"\n🔬 [{self.name}] 開始執行研究任務...")

        task = state["task"]

        # 構建研究提示
        messages = [
            SystemMessage(content=f"""你是一位專業的研究員。
你的職責是: {self.role}
請針對以下任務進行深入研究和分析。"""),
            HumanMessage(content=f"任務: {task}\n\n請提供詳細的研究分析。")
        ]

        # 調用 LLM
        response = self.llm.invoke(messages)

        # 更新狀態
        state["messages"].append(
            AIMessage(content=f"[{self.name}]: {response.content}")
        )
        state["results"]["research"] = response.content
        state["current_agent"] = self.name

        print(f"✅ [{self.name}] 研究完成")

        return state


class WriterAgent:
    """撰寫員 Agent - 負責內容創作"""

    def __init__(self, llm):
        self.llm = llm
        self.name = "撰寫員"
        self.role = "負責撰寫文章、報告和文檔"

    def run(self, state: MultiAgentState) -> MultiAgentState:
        """執行撰寫任務"""
        print(f"\n✍️ [{self.name}] 開始執行撰寫任務...")

        research_result = state["results"].get("research", "")

        # 構建撰寫提示
        messages = [
            SystemMessage(content=f"""你是一位專業的撰寫員。
你的職責是: {self.role}
請基於研究結果撰寫高質量的內容。"""),
            HumanMessage(content=f"""基於以下研究結果:
{research_result}

請撰寫一篇結構清晰、內容豐富的文章。""")
        ]

        # 調用 LLM
        response = self.llm.invoke(messages)

        # 更新狀態
        state["messages"].append(
            AIMessage(content=f"[{self.name}]: {response.content}")
        )
        state["results"]["writing"] = response.content
        state["current_agent"] = self.name

        print(f"✅ [{self.name}] 撰寫完成")

        return state


class ReviewerAgent:
    """審查員 Agent - 負責質量檢查"""

    def __init__(self, llm):
        self.llm = llm
        self.name = "審查員"
        self.role = "負責審查內容質量和提供改進建議"

    def run(self, state: MultiAgentState) -> MultiAgentState:
        """執行審查任務"""
        print(f"\n🔍 [{self.name}] 開始執行審查任務...")

        writing_result = state["results"].get("writing", "")

        # 構建審查提示
        messages = [
            SystemMessage(content=f"""你是一位專業的審查員。
你的職責是: {self.role}
請仔細審查內容並提供具體的評價和建議。"""),
            HumanMessage(content=f"""請審查以下內容:
{writing_result}

請提供:
1. 質量評分 (1-10)
2. 優點分析
3. 改進建議""")
        ]

        # 調用 LLM
        response = self.llm.invoke(messages)

        # 更新狀態
        state["messages"].append(
            AIMessage(content=f"[{self.name}]: {response.content}")
        )
        state["results"]["review"] = response.content
        state["current_agent"] = self.name

        print(f"✅ [{self.name}] 審查完成")

        return state


class SupervisorAgent:
    """協調者 Agent - 負責任務分配和流程控制"""

    def __init__(self, llm):
        self.llm = llm
        self.name = "協調者"
        self.role = "負責協調各個 Agent 的工作流程"

    def run(self, state: MultiAgentState) -> MultiAgentState:
        """執行協調任務"""
        print(f"\n👔 [{self.name}] 進行任務協調...")

        # 檢查當前進度
        results = state["results"]

        if "research" not in results:
            state["next_action"] = "research"
            print(f"📋 決策: 開始研究階段")
        elif "writing" not in results:
            state["next_action"] = "write"
            print(f"📋 決策: 開始撰寫階段")
        elif "review" not in results:
            state["next_action"] = "review"
            print(f"📋 決策: 開始審查階段")
        else:
            state["next_action"] = "end"
            print(f"📋 決策: 所有任務完成")

        state["current_agent"] = self.name

        return state


# ============================================
# 3. 構建多Agent圖
# ============================================

def create_multi_agent_graph():
    """創建多Agent協作圖"""
    print("🔨 構建多Agent協作圖...")

    # 初始化 LLM
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.7,
        api_key=os.getenv("OPENAI_API_KEY")
    )

    # 創建各個 Agent
    research_agent = ResearchAgent(llm)
    writer_agent = WriterAgent(llm)
    reviewer_agent = ReviewerAgent(llm)
    supervisor_agent = SupervisorAgent(llm)

    # 定義節點函數
    def research_node(state: MultiAgentState) -> MultiAgentState:
        return research_agent.run(state)

    def writer_node(state: MultiAgentState) -> MultiAgentState:
        return writer_agent.run(state)

    def reviewer_node(state: MultiAgentState) -> MultiAgentState:
        return reviewer_agent.run(state)

    def supervisor_node(state: MultiAgentState) -> MultiAgentState:
        return supervisor_agent.run(state)

    # 創建狀態圖
    workflow = StateGraph(MultiAgentState)

    # 添加節點
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("research", research_node)
    workflow.add_node("write", writer_node)
    workflow.add_node("review", reviewer_node)

    # 設置入口點
    workflow.set_entry_point("supervisor")

    # 定義條件路由函數
    def route_next(state: MultiAgentState) -> Literal["research", "write", "review", "end"]:
        """根據協調者的決策路由到下一個節點"""
        next_action = state["next_action"]

        if next_action == "research":
            return "research"
        elif next_action == "write":
            return "write"
        elif next_action == "review":
            return "review"
        else:
            return "end"

    # 添加條件邊
    workflow.add_conditional_edges(
        "supervisor",
        route_next,
        {
            "research": "research",
            "write": "write",
            "review": "review",
            "end": END
        }
    )

    # 各個工作節點完成後返回協調者
    workflow.add_edge("research", "supervisor")
    workflow.add_edge("write", "supervisor")
    workflow.add_edge("review", "supervisor")

    return workflow


# ============================================
# 4. 運行多Agent工作流
# ============================================

def run_multi_agent_workflow():
    """運行多Agent協作示例"""
    print("=" * 70)
    print("LangGraph 示例 21: 多Agent協作圖")
    print("=" * 70)

    # 創建工作流
    workflow = create_multi_agent_graph()
    app = workflow.compile()

    # 初始化狀態
    initial_state = {
        "messages": [],
        "current_agent": "none",
        "task": "請分析 Python 異步編程的優缺點，並撰寫一篇技術文章",
        "results": {},
        "next_action": ""
    }

    print(f"\n📋 任務: {initial_state['task']}\n")
    print("🚀 開始多Agent協作...\n")

    # 運行工作流
    result = app.invoke(initial_state)

    # 顯示結果
    print("\n" + "=" * 70)
    print("📊 協作結果總結:")
    print("=" * 70)

    print(f"\n✅ 參與的 Agent: {len(result['results'])} 個")

    if "research" in result["results"]:
        print(f"\n🔬 研究結果:")
        print(result["results"]["research"][:200] + "...")

    if "writing" in result["results"]:
        print(f"\n✍️ 撰寫結果:")
        print(result["results"]["writing"][:200] + "...")

    if "review" in result["results"]:
        print(f"\n🔍 審查結果:")
        print(result["results"]["review"][:200] + "...")

    print("\n" + "=" * 70)
    print(f"💡 總共經過 {len(result['messages'])} 個消息交互")
    print("=" * 70)


# ============================================
# 5. 關鍵概念說明
# ============================================

def print_concepts():
    """打印關鍵概念"""
    print("\n" + "=" * 70)
    print("💡 多Agent協作關鍵概念:")
    print("=" * 70)
    print("""
1. Agent 角色分工:
   - 每個 Agent 有明確的職責和專業領域
   - 通過類封裝 Agent 的行為和狀態
   - Agent 之間相互獨立，通過狀態通信

2. 協調者模式 (Supervisor Pattern):
   - 協調者負責任務分配和流程控制
   - 工作節點完成任務後返回協調者
   - 協調者決定下一步的執行路徑

3. 消息傳遞:
   - 所有交互記錄在 messages 中
   - 使用 results 字典共享工作成果
   - 狀態在 Agent 之間流動和累積

4. 流程控制:
   - 使用條件邊實現動態路由
   - 基於當前狀態決定下一個 Agent
   - 支持循環和迭代優化

5. 應用場景:
   - 內容創作流程 (研究-撰寫-審查)
   - 軟件開發流程 (設計-編碼-測試)
   - 業務流程自動化
   - 複雜問題的協作解決
    """)


# ============================================
# 主程序
# ============================================

if __name__ == "__main__":
    # 運行多Agent工作流
    run_multi_agent_workflow()

    # 打印關鍵概念
    print_concepts()

    print("\n✅ 示例完成！")
    print("💡 提示: 這展示了如何構建多Agent協作系統")
    print("      可以根據實際需求添加更多專業Agent")

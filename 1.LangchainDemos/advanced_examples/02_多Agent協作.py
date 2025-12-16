"""
02_多Agent協作.py - 多代理協作系統

本範例展示如何使用 LangGraph 構建多 Agent 協作系統，包括：
- LangGraph 基礎架構與狀態管理
- 多 Agent 角色定義與協調
- 監督者模式 (Supervisor Pattern)
- 階層式團隊協作
- Agent 間通信與任務委派
- LangGraph Swarm 模式
- 工具共享與結果整合

基於 2025 年最新的 LangGraph 特性

作者：LLM-agent-Demo Team
日期：2025-12
"""

import os
import operator
from typing import Annotated, TypedDict, List, Dict, Any, Sequence
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_core.output_parsers import StrOutputParser

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor, ToolInvocation

# 載入環境變數
load_dotenv()


# ============================================================================
# 工具定義
# ============================================================================

@tool
def web_search(query: str) -> str:
    """
    模擬網路搜尋工具

    Args:
        query: 搜尋查詢字符串

    Returns:
        搜尋結果
    """
    # 實際應用中應該連接真實的搜索 API（如 Tavily）
    return f"搜尋結果：關於 '{query}' 的最新信息包括市場趨勢、技術進展和行業分析。"


@tool
def data_analysis(data_description: str) -> str:
    """
    模擬數據分析工具

    Args:
        data_description: 需要分析的數據描述

    Returns:
        分析結果
    """
    return f"數據分析結果：根據 '{data_description}'，發現關鍵趨勢和異常值。"


@tool
def write_report(content: str, report_type: str = "summary") -> str:
    """
    模擬報告撰寫工具

    Args:
        content: 報告內容
        report_type: 報告類型

    Returns:
        格式化的報告
    """
    return f"""
    【{report_type.upper()} 報告】
    ==========================================
    {content}
    ==========================================
    """


# ============================================================================
# 範例 1: 基礎多 Agent 系統 - 研究團隊
# ============================================================================

class ResearchState(TypedDict):
    """研究團隊的狀態定義"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    topic: str
    research_data: str
    analysis_result: str
    final_report: str
    next_agent: str


def create_researcher_agent():
    """創建研究員 Agent"""
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

    system_prompt = """你是一位專業的研究員。
    你的任務是收集關於給定主題的信息。
    使用 web_search 工具來查找相關資料。
    將你的發現整理成結構化的摘要。
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
    ])

    # 綁定工具到 LLM
    llm_with_tools = llm.bind_tools([web_search])

    return prompt | llm_with_tools


def create_analyst_agent():
    """創建分析師 Agent"""
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

    system_prompt = """你是一位數據分析師。
    你的任務是分析研究員提供的數據。
    識別關鍵趨勢、模式和洞察。
    使用 data_analysis 工具輔助分析。
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
    ])

    llm_with_tools = llm.bind_tools([data_analysis])

    return prompt | llm_with_tools


def create_writer_agent():
    """創建撰寫者 Agent"""
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

    system_prompt = """你是一位專業的報告撰寫者。
    你的任務是將研究和分析結果整合成清晰、專業的報告。
    確保報告結構完整、語言流暢、重點突出。
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
    ])

    return prompt | llm | StrOutputParser()


def example_1_basic_multi_agent():
    """
    展示基礎的多 Agent 協作系統

    流程：研究員 → 分析師 → 撰寫者
    """
    print("\n" + "="*80)
    print("範例 1: 基礎多 Agent 協作 - 研究團隊")
    print("="*80)

    # 創建 Agent
    researcher = create_researcher_agent()
    analyst = create_analyst_agent()
    writer = create_writer_agent()

    # 定義節點函數
    def researcher_node(state: ResearchState) -> ResearchState:
        """研究員節點"""
        print("\n[研究員] 開始收集資料...")

        messages = state["messages"]
        topic = state["topic"]

        # 添加研究任務
        messages = list(messages) + [
            HumanMessage(content=f"請研究主題：{topic}，並使用 web_search 工具收集資料。")
        ]

        # 執行研究
        response = researcher.invoke({"messages": messages})

        # 模擬工具調用結果
        research_data = f"已收集關於 '{topic}' 的相關資料和市場信息。"

        print(f"[研究員] 完成資料收集")

        return {
            **state,
            "research_data": research_data,
            "next_agent": "analyst"
        }

    def analyst_node(state: ResearchState) -> ResearchState:
        """分析師節點"""
        print("\n[分析師] 開始分析數據...")

        messages = state["messages"]
        research_data = state["research_data"]

        # 添加分析任務
        messages = list(messages) + [
            HumanMessage(content=f"請分析以下研究數據：\n{research_data}")
        ]

        # 執行分析
        response = analyst.invoke({"messages": messages})

        # 模擬分析結果
        analysis_result = f"分析發現：{state['topic']} 具有高增長潛力，市場需求強勁。"

        print(f"[分析師] 完成數據分析")

        return {
            **state,
            "analysis_result": analysis_result,
            "next_agent": "writer"
        }

    def writer_node(state: ResearchState) -> ResearchState:
        """撰寫者節點"""
        print("\n[撰寫者] 開始撰寫報告...")

        messages = [
            HumanMessage(content=f"""
            請根據以下信息撰寫一份簡潔的報告：

            主題：{state['topic']}
            研究數據：{state['research_data']}
            分析結果：{state['analysis_result']}

            報告應包含：摘要、關鍵發現、結論。
            """)
        ]

        # 生成報告
        report = writer.invoke({"messages": messages})

        print(f"[撰寫者] 完成報告撰寫")

        return {
            **state,
            "final_report": report,
            "next_agent": "end"
        }

    # 構建圖
    workflow = StateGraph(ResearchState)

    # 添加節點
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("writer", writer_node)

    # 定義邊（流程）
    workflow.set_entry_point("researcher")
    workflow.add_edge("researcher", "analyst")
    workflow.add_edge("analyst", "writer")
    workflow.add_edge("writer", END)

    # 編譯圖
    app = workflow.compile()

    # 執行工作流
    initial_state = {
        "messages": [],
        "topic": "人工智能在醫療領域的應用",
        "research_data": "",
        "analysis_result": "",
        "final_report": "",
        "next_agent": ""
    }

    result = app.invoke(initial_state)

    print("\n" + "="*80)
    print("最終報告：")
    print("="*80)
    print(result["final_report"])

    return app


# ============================================================================
# 範例 2: 監督者模式 (Supervisor Pattern)
# ============================================================================

class SupervisorState(TypedDict):
    """監督者狀態"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: str  # 下一個要執行的 Agent
    task_description: str
    results: Dict[str, str]


def create_supervisor(agents: List[str]):
    """
    創建監督者 Agent

    監督者負責：
    1. 理解任務需求
    2. 決定委派給哪個 Agent
    3. 協調多個 Agent 的工作
    """
    llm = ChatOpenAI(model="gpt-4", temperature=0)

    system_prompt = f"""你是一個團隊監督者，負責協調以下團隊成員：
    {', '.join(agents)}

    對於給定的任務，你需要決定：
    1. 哪個團隊成員最適合處理
    2. 是否需要多個成員協作
    3. 任務是否已完成

    回應格式：
    - 如果需要委派任務，回覆成員名稱
    - 如果任務完成，回覆 "FINISH"
    """

    options = agents + ["FINISH"]

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
        ("human", "給定以上對話，下一步應該由誰處理？選項：{options}")
    ])

    chain = prompt | llm | StrOutputParser()

    return chain


def example_2_supervisor_pattern():
    """
    展示監督者模式的多 Agent 系統

    特點：
    - 動態任務分配
    - 中央協調控制
    - 靈活的工作流
    """
    print("\n" + "="*80)
    print("範例 2: 監督者模式")
    print("="*80)

    # 定義團隊成員
    agents = ["researcher", "analyst", "coder"]

    # 創建監督者
    supervisor = create_supervisor(agents)

    # 創建各個 Agent（簡化版）
    def researcher_work(state: SupervisorState) -> SupervisorState:
        print("\n[研究員] 執行研究任務...")
        result = "已完成主題研究，收集了相關文獻和數據。"
        state["results"]["researcher"] = result
        state["messages"] = list(state["messages"]) + [
            AIMessage(content=f"研究員報告：{result}")
        ]
        return state

    def analyst_work(state: SupervisorState) -> SupervisorState:
        print("\n[分析師] 執行分析任務...")
        result = "已完成數據分析，識別出關鍵趨勢和模式。"
        state["results"]["analyst"] = result
        state["messages"] = list(state["messages"]) + [
            AIMessage(content=f"分析師報告：{result}")
        ]
        return state

    def coder_work(state: SupervisorState) -> SupervisorState:
        print("\n[程式員] 執行編碼任務...")
        result = "已完成原型開發，代碼可供測試。"
        state["results"]["coder"] = result
        state["messages"] = list(state["messages"]) + [
            AIMessage(content=f"程式員報告：{result}")
        ]
        return state

    def supervisor_node(state: SupervisorState) -> SupervisorState:
        """監督者決策節點"""
        print("\n[監督者] 評估當前狀態並分配任務...")

        # 簡化版：按順序分配
        if "researcher" not in state["results"]:
            next_agent = "researcher"
        elif "analyst" not in state["results"]:
            next_agent = "analyst"
        elif "coder" not in state["results"]:
            next_agent = "coder"
        else:
            next_agent = "FINISH"

        print(f"[監督者] 決定：交給 {next_agent}")

        return {**state, "next": next_agent}

    # 構建圖
    workflow = StateGraph(SupervisorState)

    # 添加節點
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("researcher", researcher_work)
    workflow.add_node("analyst", analyst_work)
    workflow.add_node("coder", coder_work)

    # 定義條件路由
    def route_to_agent(state: SupervisorState) -> str:
        """根據監督者的決定路由到相應的 Agent"""
        next_agent = state["next"]
        if next_agent == "FINISH":
            return END
        return next_agent

    # 設置邊
    workflow.set_entry_point("supervisor")

    for agent in agents:
        workflow.add_edge(agent, "supervisor")

    workflow.add_conditional_edges(
        "supervisor",
        route_to_agent,
        {agent: agent for agent in agents} | {"__end__": END}
    )

    # 編譯並執行
    app = workflow.compile()

    initial_state = {
        "messages": [HumanMessage(content="開發一個 AI 醫療診斷系統")],
        "next": "",
        "task_description": "開發一個 AI 醫療診斷系統",
        "results": {}
    }

    result = app.invoke(initial_state)

    print("\n" + "="*80)
    print("團隊協作結果：")
    print("="*80)
    for agent, output in result["results"].items():
        print(f"\n{agent}: {output}")

    return app


# ============================================================================
# 範例 3: 階層式團隊協作
# ============================================================================

def example_3_hierarchical_teams():
    """
    展示階層式團隊結構

    結構：
    - 總監督者
      - 研發團隊（研究員 + 開發者）
      - 市場團隊（分析師 + 行銷人員）
    """
    print("\n" + "="*80)
    print("範例 3: 階層式團隊協作")
    print("="*80)

    print("""
    團隊結構：

    總監督者
    ├── 研發團隊
    │   ├── 研究員
    │   └── 開發者
    └── 市場團隊
        ├── 分析師
        └── 行銷人員
    """)

    # 實際實現會更複雜，這裡展示概念
    print("\n階層式團隊可以：")
    print("- 將複雜任務分解為子任務")
    print("- 每個子團隊獨立運作")
    print("- 上級監督者協調各團隊")
    print("- 實現更好的關注點分離")


# ============================================================================
# 範例 4: Agent 通信與消息傳遞
# ============================================================================

class CollaborationState(TypedDict):
    """協作狀態"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    shared_memory: Dict[str, Any]  # 共享記憶
    current_agent: str
    task_queue: List[str]


def example_4_agent_communication():
    """
    展示 Agent 之間的通信機制

    特點：
    - 共享記憶空間
    - 消息傳遞
    - 任務隊列管理
    """
    print("\n" + "="*80)
    print("範例 4: Agent 通信與消息傳遞")
    print("="*80)

    def agent_a(state: CollaborationState) -> CollaborationState:
        """Agent A：數據收集者"""
        print("\n[Agent A] 收集數據並存入共享記憶...")

        # 將數據寫入共享記憶
        state["shared_memory"]["collected_data"] = {
            "source": "database",
            "records": 1000,
            "timestamp": "2025-12-15"
        }

        # 發送消息給下一個 Agent
        state["messages"] = list(state["messages"]) + [
            AIMessage(
                content="[Agent A] 數據收集完成，已存入共享記憶。",
                name="agent_a"
            )
        ]

        return state

    def agent_b(state: CollaborationState) -> CollaborationState:
        """Agent B：數據處理者"""
        print("\n[Agent B] 從共享記憶讀取數據並處理...")

        # 從共享記憶讀取數據
        data = state["shared_memory"].get("collected_data", {})
        print(f"[Agent B] 讀取到數據：{data}")

        # 處理並更新
        state["shared_memory"]["processed_data"] = {
            "status": "processed",
            "insights": "發現關鍵趨勢"
        }

        state["messages"] = list(state["messages"]) + [
            AIMessage(
                content="[Agent B] 數據處理完成。",
                name="agent_b"
            )
        ]

        return state

    def agent_c(state: CollaborationState) -> CollaborationState:
        """Agent C：報告生成者"""
        print("\n[Agent C] 生成最終報告...")

        data = state["shared_memory"].get("collected_data", {})
        processed = state["shared_memory"].get("processed_data", {})

        report = f"""
        報告摘要：
        - 數據來源：{data.get('source')}
        - 記錄數：{data.get('records')}
        - 處理狀態：{processed.get('status')}
        - 洞察：{processed.get('insights')}
        """

        state["shared_memory"]["final_report"] = report

        print(report)

        return state

    # 構建簡單的線性工作流
    workflow = StateGraph(CollaborationState)

    workflow.add_node("agent_a", agent_a)
    workflow.add_node("agent_b", agent_b)
    workflow.add_node("agent_c", agent_c)

    workflow.set_entry_point("agent_a")
    workflow.add_edge("agent_a", "agent_b")
    workflow.add_edge("agent_b", "agent_c")
    workflow.add_edge("agent_c", END)

    app = workflow.compile()

    # 執行
    initial_state = {
        "messages": [],
        "shared_memory": {},
        "current_agent": "",
        "task_queue": []
    }

    result = app.invoke(initial_state)

    print("\n" + "="*80)
    print("共享記憶內容：")
    print("="*80)
    for key, value in result["shared_memory"].items():
        print(f"\n{key}:")
        print(value)


# ============================================================================
# 範例 5: LangGraph Swarm 模式（2025 新特性）
# ============================================================================

def example_5_swarm_pattern():
    """
    展示 LangGraph Swarm 模式（2025 年 3 月發布）

    Swarm 特點：
    - 輕量級多 Agent 協作
    - 靈活的上下文切換
    - 內建的 Agent 間通信
    - 動態任務分配
    """
    print("\n" + "="*80)
    print("範例 5: LangGraph Swarm 模式")
    print("="*80)

    print("""
    LangGraph Swarm (2025) 主要特性：

    1. 專業化 Agent
       - 每個 Agent 專注於特定任務
       - 清晰的職責劃分

    2. 上下文切換
       - Agent 之間可以無縫移交任務
       - 保持完整的對話歷史

    3. 內建工具
       - 提供 Agent 間通信的預建工具
       - 簡化協作邏輯

    4. 動態協作
       - 根據任務需求動態組合 Agent
       - 支持並行和串行執行

    安裝：
    pip install langgraph-swarm

    基本用法：
    ```python
    from langgraph_swarm import Swarm, Agent

    # 定義 Agent
    researcher = Agent(
        name="researcher",
        instructions="你是一位研究員...",
        functions=[search_tool]
    )

    analyst = Agent(
        name="analyst",
        instructions="你是一位分析師...",
        functions=[analyze_tool]
    )

    # 創建 Swarm
    swarm = Swarm()

    # 執行任務
    result = swarm.run(
        agent=researcher,
        messages=[{"role": "user", "content": "研究 AI 趨勢"}],
        context_variables={"project": "AI Research"}
    )
    ```
    """)

    print("\n✨ Swarm 模式非常適合：")
    print("- 客戶服務系統（多個專業客服 Agent）")
    print("- 內容創作團隊（研究、撰寫、編輯）")
    print("- 軟體開發團隊（需求、開發、測試）")


# ============================================================================
# 主函數
# ============================================================================

def main():
    """運行所有多 Agent 協作範例"""

    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║                                                                ║
    ║            多 Agent 協作系統 - 完整示範                        ║
    ║                                                                ║
    ║  基於 LangGraph (2025) 的進階多代理協作範例                   ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
    """)

    # 檢查環境變數
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 錯誤: 請設置 OPENAI_API_KEY 環境變數")
        return

    try:
        # 運行範例
        example_1_basic_multi_agent()
        example_2_supervisor_pattern()
        example_3_hierarchical_teams()
        example_4_agent_communication()
        example_5_swarm_pattern()

        print("\n" + "="*80)
        print("✅ 所有範例執行完成！")
        print("="*80)

    except Exception as e:
        print(f"\n❌ 執行過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()


# ============================================================================
# 學習要點總結
# ============================================================================
"""
📚 多 Agent 協作系統學習要點：

1. **LangGraph 基礎**
   - StateGraph: 定義狀態機
   - 節點 (Node): 執行具體任務
   - 邊 (Edge): 定義流程
   - 條件路由: 動態決定下一步

2. **Agent 協作模式**

   a) 順序協作
      - Agent 按固定順序執行
      - 適合明確的工作流程

   b) 監督者模式
      - 中央監督者協調其他 Agent
      - 動態任務分配
      - 適合複雜、不確定的任務

   c) 階層式團隊
      - 多層次的組織結構
      - 子團隊獨立運作
      - 適合大規模、複雜項目

   d) Swarm 模式 (2025)
      - 輕量級協作
      - 靈活的上下文切換
      - 適合需要頻繁 Agent 切換的場景

3. **狀態管理**
   - TypedDict: 定義狀態類型
   - Annotated: 定義狀態更新方式
   - 共享記憶: Agent 間數據共享

4. **工具使用**
   - @tool 裝飾器定義工具
   - bind_tools 綁定工具到 LLM
   - ToolExecutor 執行工具調用

5. **通信機制**
   - Messages: Agent 間消息傳遞
   - Shared Memory: 共享數據空間
   - State Updates: 狀態更新傳播

6. **LangGraph 2025 新特性**
   - Swarm 庫: 簡化多 Agent 協作
   - 改進的調試工具 (Studio v2)
   - 更好的並行處理支持
   - 增強的狀態管理

💡 最佳實踐：

1. 清晰的職責劃分
   - 每個 Agent 有明確的角色
   - 避免職責重疊

2. 有效的狀態管理
   - 使用類型化的狀態
   - 最小化狀態複雜度

3. 錯誤處理
   - 實施重試機制
   - 提供降級方案

4. 監控與調試
   - 使用 LangSmith 追蹤
   - 記錄關鍵決策點

5. 效能優化
   - 並行執行獨立任務
   - 避免不必要的 Agent 切換

🔗 相關資源：
- LangGraph 官方文檔: https://langchain-ai.github.io/langgraph/
- Multi-Agent 教程: https://langchain-ai.github.io/langgraph/tutorials/multi_agent/
- LangGraph Swarm: https://changelog.langchain.com/announcements/langgraph-swarm
- 範例庫: https://github.com/langchain-ai/langgraph/tree/main/examples/multi_agent
"""

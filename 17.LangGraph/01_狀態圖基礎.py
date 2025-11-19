#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LangGraph 示例 01: 狀態圖基礎

本示例展示:
1. LangGraph 的基本概念和架構
2. 創建簡單的狀態圖
3. 定義狀態和節點
4. 運行基本工作流

LangGraph 是什麼？
- LangChain 官方的狀態管理框架
- 用於構建複雜的、有狀態的 Agent 應用
- 基於圖結構的工作流編排
- 支持循環、條件、並行等複雜邏輯
"""

from typing import TypedDict, Annotated
import operator
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import os
from dotenv import load_dotenv

# 載入環境變量
load_dotenv()


# ============================================
# 1. 定義狀態 (State)
# ============================================

class AgentState(TypedDict):
    """
    Agent 的狀態定義

    狀態是在節點之間傳遞的數據結構
    使用 TypedDict 定義狀態的結構
    """
    messages: Annotated[list, operator.add]  # 消息列表（會累積）
    next_step: str  # 下一步操作
    counter: int  # 計數器


# ============================================
# 2. 定義節點 (Nodes)
# ============================================

def input_node(state: AgentState) -> AgentState:
    """
    輸入節點: 處理用戶輸入

    節點是執行特定操作的函數
    接收當前狀態，返回更新後的狀態
    """
    print("📥 [輸入節點] 處理用戶輸入")

    # 添加系統消息
    state["messages"].append(
        SystemMessage(content="你是一個友好的助手，用簡潔的方式回答問題。")
    )

    # 添加用戶消息
    state["messages"].append(
        HumanMessage(content="請介紹一下 LangGraph 是什麼？")
    )

    state["next_step"] = "process"
    state["counter"] = state.get("counter", 0) + 1

    return state


def process_node(state: AgentState) -> AgentState:
    """
    處理節點: 使用 LLM 處理消息
    """
    print("⚙️ [處理節點] 使用 LLM 生成回答")

    # 初始化 LLM
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.7,
        api_key=os.getenv("OPENAI_API_KEY")
    )

    # 調用 LLM
    response = llm.invoke(state["messages"])

    # 添加 AI 回應到消息列表
    state["messages"].append(response)

    state["next_step"] = "output"
    state["counter"] = state.get("counter", 0) + 1

    return state


def output_node(state: AgentState) -> AgentState:
    """
    輸出節點: 顯示結果
    """
    print("📤 [輸出節點] 輸出結果")

    # 獲取最後的 AI 回應
    last_message = state["messages"][-1]

    print(f"\n✅ AI 回答:\n{last_message.content}\n")

    state["next_step"] = "end"
    state["counter"] = state.get("counter", 0) + 1

    return state


# ============================================
# 3. 構建狀態圖 (State Graph)
# ============================================

def create_basic_graph() -> StateGraph:
    """
    創建基本的狀態圖

    狀態圖的組成:
    - 節點 (Nodes): 執行特定操作的函數
    - 邊 (Edges): 連接節點的路徑
    - 入口 (Entry Point): 圖的起始節點
    - 結束 (END): 圖的終止標記
    """
    print("🔨 創建狀態圖...")

    # 創建狀態圖
    workflow = StateGraph(AgentState)

    # 添加節點
    workflow.add_node("input", input_node)
    workflow.add_node("process", process_node)
    workflow.add_node("output", output_node)

    # 設置入口點
    workflow.set_entry_point("input")

    # 添加邊（定義節點之間的連接）
    workflow.add_edge("input", "process")
    workflow.add_edge("process", "output")
    workflow.add_edge("output", END)

    return workflow


# ============================================
# 4. 運行工作流
# ============================================

def run_basic_workflow():
    """
    運行基本工作流示例
    """
    print("=" * 60)
    print("LangGraph 基礎示例: 簡單狀態圖")
    print("=" * 60)

    # 創建工作流
    workflow = create_basic_graph()

    # 編譯圖
    app = workflow.compile()

    print("\n📊 圖結構:")
    print(f"節點: {list(app.nodes.keys())}")
    print(f"邊: {[(e[0], e[1]) for e in app.edges]}")

    # 初始化狀態
    initial_state = {
        "messages": [],
        "next_step": "start",
        "counter": 0
    }

    print("\n🚀 開始運行工作流...\n")

    # 運行工作流
    result = app.invoke(initial_state)

    print("\n" + "=" * 60)
    print("📊 最終狀態:")
    print(f"- 消息數量: {len(result['messages'])}")
    print(f"- 執行步驟: {result['counter']}")
    print(f"- 最終狀態: {result['next_step']}")
    print("=" * 60)


# ============================================
# 5. 可視化圖結構 (可選)
# ============================================

def visualize_graph():
    """
    可視化圖結構

    需要安裝: pip install graphviz
    """
    try:
        from IPython.display import Image, display

        workflow = create_basic_graph()
        app = workflow.compile()

        # 生成 Mermaid 圖
        print("\n📊 Mermaid 圖:")
        print(app.get_graph().draw_mermaid())

        # 如果在 Jupyter 中，可以顯示圖片
        try:
            display(Image(app.get_graph().draw_mermaid_png()))
        except:
            print("(在 Jupyter Notebook 中可以顯示圖片)")

    except ImportError:
        print("提示: 安裝 graphviz 和 IPython 可以可視化圖結構")
        print("pip install graphviz ipython")


# ============================================
# 主程序
# ============================================

if __name__ == "__main__":
    # 運行基本工作流
    run_basic_workflow()

    # 嘗試可視化圖結構
    print("\n" + "=" * 60)
    visualize_graph()

    print("\n" + "=" * 60)
    print("💡 關鍵概念總結:")
    print("=" * 60)
    print("""
1. 狀態 (State):
   - 使用 TypedDict 定義
   - 在節點之間傳遞
   - 可以包含任意數據

2. 節點 (Nodes):
   - 接收狀態，返回更新後的狀態
   - 執行特定的操作
   - 可以是任意 Python 函數

3. 邊 (Edges):
   - 連接節點
   - 定義工作流的路徑
   - 可以是條件邊

4. 圖 (Graph):
   - 由節點和邊組成
   - 需要設置入口點
   - 使用 END 標記結束

5. 執行:
   - 使用 compile() 編譯圖
   - 使用 invoke() 運行工作流
   - 狀態會在節點間傳遞
    """)

    print("\n✅ 示例完成！")
    print("💡 提示: 這是最基本的 LangGraph 工作流")
    print("      接下來的示例會展示更複雜的功能")

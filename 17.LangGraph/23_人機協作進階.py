#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LangGraph 示例 23: 人機協作進階 (Human-in-the-Loop)

本示例展示:
1. 使用 interrupt() 函數實現人工介入
2. 審批流程的實現
3. 人工決策點的設置
4. 恢復執行和狀態管理

學習重點:
- Human-in-the-Loop 設計模式
- interrupt() 函數的使用 (LangGraph 0.2.31+)
- Command API 進行恢復
- 交互式工作流
"""

from typing import TypedDict, Annotated, Literal
import operator
from langgraph.graph import StateGraph, END
from langgraph.types import interrupt
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import os
from dotenv import load_dotenv

load_dotenv()


# ============================================
# 1. 定義審批工作流狀態
# ============================================

class ApprovalState(TypedDict):
    """
    審批工作流狀態

    包含:
    - request: 請求內容
    - analysis: AI 分析結果
    - approval_status: 審批狀態
    - human_feedback: 人工反饋
    - final_decision: 最終決策
    """
    messages: Annotated[list, operator.add]
    request: str
    analysis: dict
    approval_status: str
    human_feedback: str
    final_decision: str
    risk_level: str


# ============================================
# 2. 定義工作流節點
# ============================================

def analyze_request(state: ApprovalState) -> ApprovalState:
    """
    分析請求節點

    使用 AI 分析請求的風險和影響
    """
    print("\n🔍 [AI分析] 正在分析請求...")

    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.3,
        api_key=os.getenv("OPENAI_API_KEY")
    )

    request = state["request"]

    # 構建分析提示
    messages = [
        SystemMessage(content="""你是一個專業的風險分析師。
請分析以下請求的風險等級和潛在影響。

輸出格式:
風險等級: [低/中/高]
影響分析: [詳細說明]
建議: [具體建議]"""),
        HumanMessage(content=f"請求內容: {request}")
    ]

    # 調用 LLM
    response = llm.invoke(messages)

    # 解析風險等級
    risk_level = "中"
    if "高" in response.content[:50]:
        risk_level = "高"
    elif "低" in response.content[:50]:
        risk_level = "低"

    # 更新狀態
    state["analysis"] = {
        "content": response.content,
        "timestamp": "2025-12-15"
    }
    state["risk_level"] = risk_level
    state["messages"].append(
        AIMessage(content=f"[AI分析完成] 風險等級: {risk_level}")
    )

    print(f"✅ 分析完成，風險等級: {risk_level}")

    return state


def check_approval_needed(state: ApprovalState) -> Literal["auto_approve", "human_review"]:
    """
    條件路由: 判斷是否需要人工審批

    低風險自動批准，中高風險需要人工審批
    """
    risk_level = state["risk_level"]

    print(f"\n⚖️ [決策] 風險等級 '{risk_level}' ", end="")

    if risk_level == "低":
        print("→ 自動批准")
        return "auto_approve"
    else:
        print("→ 需要人工審批")
        return "human_review"


def auto_approve(state: ApprovalState) -> ApprovalState:
    """自動批准節點"""
    print("\n✅ [自動批准] 請求已自動批准")

    state["approval_status"] = "已批准"
    state["final_decision"] = "自動批准 - 低風險請求"
    state["messages"].append(
        AIMessage(content="自動批准: 風險等級低，無需人工審批")
    )

    return state


def human_review(state: ApprovalState) -> ApprovalState:
    """
    人工審批節點

    使用 interrupt() 暫停執行，等待人工輸入
    """
    print("\n⏸️ [暫停執行] 等待人工審批...")

    # 準備審批信息
    review_info = f"""
請審批以下請求:
================
請求內容: {state['request']}
風險等級: {state['risk_level']}

AI 分析結果:
{state['analysis']['content']}

請輸入您的決定:
- 輸入 '批准' 批准該請求
- 輸入 '拒絕' 拒絕該請求
- 輸入 '需要更多信息' 請求補充資料
"""

    # 使用 interrupt() 暫停執行，等待人工輸入
    # 在 LangGraph 0.2.31+ 中，這是推薦的做法
    human_input = interrupt(review_info)

    # 注意: interrupt() 後的代碼會在恢復時執行
    print(f"▶️ [恢復執行] 收到人工輸入: {human_input}")

    state["human_feedback"] = str(human_input)
    state["messages"].append(
        HumanMessage(content=f"人工決策: {human_input}")
    )

    return state


def process_human_decision(state: ApprovalState) -> ApprovalState:
    """處理人工決策"""
    print("\n📋 [處理決策] 處理人工反饋...")

    feedback = state["human_feedback"].lower()

    if "批准" in feedback:
        state["approval_status"] = "已批准"
        state["final_decision"] = f"人工批准 - {state['human_feedback']}"
        print("✅ 決策: 批准")
    elif "拒絕" in feedback:
        state["approval_status"] = "已拒絕"
        state["final_decision"] = f"人工拒絕 - {state['human_feedback']}"
        print("❌ 決策: 拒絕")
    else:
        state["approval_status"] = "需要補充"
        state["final_decision"] = f"需要更多信息 - {state['human_feedback']}"
        print("ℹ️ 決策: 需要補充信息")

    state["messages"].append(
        AIMessage(content=f"最終決策: {state['final_decision']}")
    )

    return state


def generate_report(state: ApprovalState) -> ApprovalState:
    """生成審批報告"""
    print("\n📄 [生成報告] 生成審批記錄...")

    report = f"""
審批報告
========
請求: {state['request']}
風險等級: {state['risk_level']}
審批狀態: {state['approval_status']}
最終決策: {state['final_decision']}
處理流程: {len(state['messages'])} 個步驟
"""

    state["messages"].append(
        AIMessage(content=report)
    )

    print("✅ 報告生成完成")

    return state


# ============================================
# 3. 構建人機協作圖
# ============================================

def create_human_in_loop_graph():
    """創建帶人工介入的審批圖"""
    print("🔨 構建人機協作工作流...")

    # 創建狀態圖
    workflow = StateGraph(ApprovalState)

    # 添加節點
    workflow.add_node("analyze", analyze_request)
    workflow.add_node("auto_approve", auto_approve)
    workflow.add_node("human_review", human_review)
    workflow.add_node("process_decision", process_human_decision)
    workflow.add_node("report", generate_report)

    # 設置入口點
    workflow.set_entry_point("analyze")

    # 添加條件邊: 根據風險等級決定路由
    workflow.add_conditional_edges(
        "analyze",
        check_approval_needed,
        {
            "auto_approve": "auto_approve",
            "human_review": "human_review"
        }
    )

    # 自動批准直接到報告
    workflow.add_edge("auto_approve", "report")

    # 人工審批需要處理決策
    workflow.add_edge("human_review", "process_decision")
    workflow.add_edge("process_decision", "report")

    # 報告完成後結束
    workflow.add_edge("report", END)

    return workflow


# ============================================
# 4. 運行人機協作示例
# ============================================

def run_human_in_loop_example():
    """運行人機協作示例"""
    print("=" * 70)
    print("LangGraph 示例 23: 人機協作進階 (Human-in-the-Loop)")
    print("=" * 70)

    # 創建工作流
    workflow = create_human_in_loop_graph()
    app = workflow.compile()

    # 測試案例
    test_cases = [
        {
            "request": "申請購買 500 元的辦公用品",
            "expected_risk": "低"
        },
        {
            "request": "申請採購 50 萬元的新服務器設備，需要立即批准",
            "expected_risk": "高"
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"測試案例 {i}: {test_case['request']}")
        print(f"{'='*70}")

        # 初始化狀態
        initial_state = {
            "messages": [],
            "request": test_case["request"],
            "analysis": {},
            "approval_status": "待審批",
            "human_feedback": "",
            "final_decision": "",
            "risk_level": ""
        }

        # 運行工作流
        print("\n🚀 開始處理...\n")

        try:
            result = app.invoke(initial_state)

            # 顯示結果
            print("\n" + "=" * 70)
            print("📊 處理結果:")
            print("=" * 70)
            print(f"請求: {result['request']}")
            print(f"風險等級: {result['risk_level']}")
            print(f"審批狀態: {result['approval_status']}")
            print(f"最終決策: {result['final_decision']}")
            print(f"處理步驟: {len(result['messages'])} 個")
            print("=" * 70)

        except Exception as e:
            print(f"\n⚠️ 注意: {str(e)}")
            print("💡 提示: interrupt() 功能需要在支持持久化的環境中運行")
            print("   在本地演示中，我們使用模擬的人工輸入")


# ============================================
# 5. 模擬恢復執行 (演示概念)
# ============================================

def demonstrate_resume_concept():
    """演示恢復執行的概念"""
    print("\n" + "=" * 70)
    print("💡 恢復執行概念演示:")
    print("=" * 70)
    print("""
在實際生產環境中使用 interrupt() 和 Command API:

1. 暫停執行:
   ```python
   human_input = interrupt("請輸入您的決定")
   ```

2. 檢查中斷的線程:
   ```python
   state = graph.get_state(config)
   if state.next == ("human_review",):
       print("等待人工輸入")
   ```

3. 使用 Command 恢復執行:
   ```python
   from langgraph.types import Command

   # 恢復執行並提供人工輸入
   result = graph.invoke(
       Command(resume="批准"),
       config={"thread_id": "thread-1"}
   )
   ```

4. 關鍵特性:
   - 中斷的線程不佔用資源（僅佔用存儲空間）
   - 可以在數月後恢復執行
   - 可以在不同機器上恢復
   - 需要配置持久化存儲（checkpointer）

5. 實際應用場景:
   - 審批流程（需要管理層批准）
   - 人工驗證（需要確認 AI 輸出）
   - 交互式調試（逐步檢查執行）
   - 長時間運行任務（可暫停和恢復）
    """)


# ============================================
# 6. 關鍵概念說明
# ============================================

def print_concepts():
    """打印關鍵概念"""
    print("\n" + "=" * 70)
    print("💡 Human-in-the-Loop 關鍵概念:")
    print("=" * 70)
    print("""
1. interrupt() 函數 (LangGraph 0.2.31+):
   - 暫停圖的執行
   - 將當前狀態保存到持久層
   - 等待外部輸入
   - 支持跨時間和機器恢復

2. 審批模式:
   - 自動審批: 低風險請求直接通過
   - 人工審批: 高風險請求需要人工決策
   - 混合模式: 結合自動化和人工判斷

3. 條件路由:
   - 基於風險評估選擇路徑
   - 動態決定是否需要人工介入
   - 靈活的決策邏輯

4. 狀態管理:
   - 保存所有審批信息
   - 記錄人工反饋
   - 生成完整的審計跟蹤

5. 最佳實踐:
   - 明確定義介入點
   - 提供足夠的上下文信息
   - 設置合理的超時機制
   - 記錄所有決策過程
    """)


# ============================================
# 主程序
# ============================================

if __name__ == "__main__":
    # 運行人機協作示例
    run_human_in_loop_example()

    # 演示恢復執行概念
    demonstrate_resume_concept()

    # 打印關鍵概念
    print_concepts()

    print("\n✅ 示例完成！")
    print("💡 提示: Human-in-the-Loop 是構建可信 AI 系統的關鍵")
    print("      結合自動化和人工判斷可以提高系統的可靠性")

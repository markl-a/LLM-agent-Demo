#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LangGraph 示例 24: 持久化狀態

本示例展示:
1. 使用 Checkpointer 實現狀態持久化
2. 檢查點的保存和恢復
3. 時間旅行 (Time Travel) 功能
4. 線程管理和多會話支持

學習重點:
- MemorySaver 和其他 Checkpointer
- 狀態的保存和加載
- 歷史狀態的訪問
- 容錯和恢復機制
"""

from typing import TypedDict, Annotated
import operator
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import os
from dotenv import load_dotenv
import json
from datetime import datetime

load_dotenv()


# ============================================
# 1. 定義對話狀態
# ============================================

class ConversationState(TypedDict):
    """
    對話狀態

    包含:
    - messages: 對話消息列表
    - user_info: 用戶信息
    - context: 對話上下文
    - step_count: 步驟計數
    """
    messages: Annotated[list, operator.add]
    user_info: dict
    context: dict
    step_count: int


# ============================================
# 2. 定義對話節點
# ============================================

def process_input(state: ConversationState) -> ConversationState:
    """處理用戶輸入"""
    print(f"\n📥 [步驟 {state['step_count']}] 處理用戶輸入...")

    # 提取最後一條用戶消息
    last_message = state["messages"][-1] if state["messages"] else None

    if last_message:
        print(f"用戶: {last_message.content[:50]}...")

    # 更新上下文
    state["context"]["last_interaction"] = datetime.now().isoformat()
    state["step_count"] += 1

    return state


def generate_response(state: ConversationState) -> ConversationState:
    """生成 AI 回應"""
    print(f"🤖 [步驟 {state['step_count']}] 生成回應...")

    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.7,
        api_key=os.getenv("OPENAI_API_KEY")
    )

    # 構建對話歷史
    conversation_messages = [
        SystemMessage(content=f"""你是一個友好的助手。
用戶信息: {json.dumps(state['user_info'], ensure_ascii=False)}
請根據對話歷史提供有幫助的回應。""")
    ]

    # 添加最近的對話消息（保留最後 5 條）
    recent_messages = state["messages"][-5:] if len(state["messages"]) > 5 else state["messages"]
    conversation_messages.extend(recent_messages)

    # 生成回應
    response = llm.invoke(conversation_messages)

    # 添加到消息列表
    state["messages"].append(response)

    print(f"助手: {response.content[:50]}...")

    state["step_count"] += 1

    return state


def update_context(state: ConversationState) -> ConversationState:
    """更新對話上下文"""
    print(f"📊 [步驟 {state['step_count']}] 更新上下文...")

    # 更新統計信息
    state["context"]["total_messages"] = len(state["messages"])
    state["context"]["last_update"] = datetime.now().isoformat()

    state["step_count"] += 1

    return state


# ============================================
# 3. 創建帶持久化的對話圖
# ============================================

def create_persistent_graph():
    """
    創建支持持久化的對話圖

    使用 MemorySaver 作為 Checkpointer
    """
    print("🔨 創建持久化對話圖...")

    # 創建狀態圖
    workflow = StateGraph(ConversationState)

    # 添加節點
    workflow.add_node("process_input", process_input)
    workflow.add_node("generate_response", generate_response)
    workflow.add_node("update_context", update_context)

    # 設置流程
    workflow.set_entry_point("process_input")
    workflow.add_edge("process_input", "generate_response")
    workflow.add_edge("generate_response", "update_context")
    workflow.add_edge("update_context", END)

    # 創建 MemorySaver 作為 Checkpointer
    # 這會在內存中保存檢查點
    checkpointer = MemorySaver()

    # 編譯圖時指定 checkpointer
    app = workflow.compile(checkpointer=checkpointer)

    print("✅ 圖創建完成，已啟用持久化")

    return app, checkpointer


# ============================================
# 4. 演示持久化功能
# ============================================

def demonstrate_persistence():
    """演示持久化功能"""
    print("=" * 70)
    print("LangGraph 示例 24: 持久化狀態")
    print("=" * 70)

    # 創建持久化圖
    app, checkpointer = create_persistent_graph()

    # 定義線程配置（用於標識會話）
    thread_id = "conversation-001"
    config = {"configurable": {"thread_id": thread_id}}

    print(f"\n📝 線程 ID: {thread_id}")

    # ========================================
    # 場景 1: 第一次對話
    # ========================================
    print("\n" + "=" * 70)
    print("場景 1: 開始新對話")
    print("=" * 70)

    initial_state = {
        "messages": [HumanMessage(content="你好，我想了解 Python 的異步編程")],
        "user_info": {
            "name": "張三",
            "level": "中級開發者"
        },
        "context": {},
        "step_count": 0
    }

    print("\n🚀 第一次交互...")
    result1 = app.invoke(initial_state, config)

    print(f"\n📊 狀態: {result1['step_count']} 個步驟完成")
    print(f"💬 消息數: {len(result1['messages'])} 條")

    # ========================================
    # 場景 2: 繼續對話（從檢查點恢復）
    # ========================================
    print("\n" + "=" * 70)
    print("場景 2: 繼續對話（使用相同的 thread_id）")
    print("=" * 70)

    # 注意: 我們只需要提供新的消息，其他狀態會從檢查點恢復
    continue_state = {
        "messages": [HumanMessage(content="能給我一個 asyncio 的例子嗎？")],
        "user_info": {},
        "context": {},
        "step_count": 0
    }

    print("\n🚀 第二次交互...")
    result2 = app.invoke(continue_state, config)

    print(f"\n📊 狀態: {result2['step_count']} 個步驟")
    print(f"💬 消息數: {len(result2['messages'])} 條（包含歷史）")
    print(f"📝 上下文保留: {result2['user_info']}")

    # ========================================
    # 場景 3: 訪問歷史狀態（時間旅行）
    # ========================================
    print("\n" + "=" * 70)
    print("場景 3: 訪問歷史狀態（時間旅行）")
    print("=" * 70)

    # 獲取當前狀態
    current_state = app.get_state(config)

    print(f"\n📍 當前狀態:")
    print(f"   - 檢查點 ID: {current_state.config['configurable'].get('checkpoint_id', 'N/A')}")
    print(f"   - 消息數: {len(current_state.values.get('messages', []))} 條")
    print(f"   - 步驟數: {current_state.values.get('step_count', 0)}")

    # 獲取狀態歷史
    print(f"\n📜 狀態歷史:")
    history = list(app.get_state_history(config))
    print(f"   - 總共 {len(history)} 個檢查點")

    for i, state_snapshot in enumerate(history[:3], 1):
        print(f"   {i}. 步驟數: {state_snapshot.values.get('step_count', 0)}, "
              f"消息數: {len(state_snapshot.values.get('messages', []))}")

    # ========================================
    # 場景 4: 新會話（不同的 thread_id）
    # ========================================
    print("\n" + "=" * 70)
    print("場景 4: 開始新會話（不同的 thread_id）")
    print("=" * 70)

    new_thread_id = "conversation-002"
    new_config = {"configurable": {"thread_id": new_thread_id}}

    print(f"\n📝 新線程 ID: {new_thread_id}")

    new_state = {
        "messages": [HumanMessage(content="你好，我想學習機器學習")],
        "user_info": {
            "name": "李四",
            "level": "初學者"
        },
        "context": {},
        "step_count": 0
    }

    print("\n🚀 新會話交互...")
    result3 = app.invoke(new_state, new_config)

    print(f"\n📊 新會話狀態: {result3['step_count']} 個步驟")
    print(f"💬 消息數: {len(result3['messages'])} 條（新會話）")
    print(f"📝 用戶信息: {result3['user_info']}")

    # 驗證兩個會話是獨立的
    old_state = app.get_state(config)
    print(f"\n🔍 驗證會話隔離:")
    print(f"   - 會話 1 消息數: {len(old_state.values['messages'])}")
    print(f"   - 會話 2 消息數: {len(result3['messages'])}")
    print(f"   - 會話獨立: {'✅' if len(old_state.values['messages']) != len(result3['messages']) else '❌'}")


# ============================================
# 5. 演示狀態回滾
# ============================================

def demonstrate_state_rollback():
    """演示狀態回滾功能"""
    print("\n" + "=" * 70)
    print("場景 5: 狀態回滾（時間旅行）")
    print("=" * 70)

    # 創建新的持久化圖
    app, checkpointer = create_persistent_graph()

    thread_id = "rollback-test"
    config = {"configurable": {"thread_id": thread_id}}

    # 執行多次交互
    states = []
    for i in range(3):
        state = {
            "messages": [HumanMessage(content=f"這是第 {i+1} 條消息")],
            "user_info": {"step": i+1},
            "context": {},
            "step_count": 0
        }
        result = app.invoke(state, config)
        states.append(result)
        print(f"✅ 完成交互 {i+1}: {result['step_count']} 步驟, {len(result['messages'])} 條消息")

    # 獲取歷史
    print(f"\n📜 查看歷史檢查點:")
    history = list(app.get_state_history(config))

    for i, snapshot in enumerate(history[:5], 1):
        print(f"   檢查點 {i}: "
              f"消息數={len(snapshot.values.get('messages', []))}, "
              f"步驟={snapshot.values.get('step_count', 0)}")

    print(f"\n💡 可以回滾到任意檢查點並從該點繼續執行")


# ============================================
# 6. 關鍵概念說明
# ============================================

def print_concepts():
    """打印關鍵概念"""
    print("\n" + "=" * 70)
    print("💡 持久化狀態關鍵概念:")
    print("=" * 70)
    print("""
1. Checkpointer 類型:
   - MemorySaver: 內存中保存（適合開發和測試）
   - SqliteSaver: SQLite 數據庫（適合單機應用）
   - PostgresSaver: PostgreSQL 數據庫（適合生產環境）
   - RedisSaver: Redis 緩存（適合分布式系統）

2. 線程管理:
   - thread_id: 唯一標識一個會話
   - 不同 thread_id 的狀態完全隔離
   - 支持多用戶、多會話並發

3. 檢查點特性:
   - 自動保存: 每個節點執行後自動保存
   - 增量更新: 只保存變化的部分
   - 歷史訪問: 可以訪問任意歷史狀態

4. 時間旅行 (Time Travel):
   - 查看歷史狀態: get_state_history()
   - 回滾到歷史點: 使用特定的 checkpoint_id
   - 從歷史點繼續: 創建新的執行分支

5. 容錯能力:
   - 故障恢復: 從最後的檢查點恢復
   - 重試機制: 失敗的步驟可以重新執行
   - 數據一致性: 保證狀態的完整性

6. 實際應用:
   - 長時間運行的任務
   - 需要暫停和恢復的工作流
   - 多輪對話系統
   - 審計和調試需求

7. 最佳實踐:
   - 選擇合適的 Checkpointer
   - 合理設置檢查點頻率
   - 定期清理舊檢查點
   - 處理並發訪問
    """)


# ============================================
# 主程序
# ============================================

if __name__ == "__main__":
    # 演示持久化功能
    demonstrate_persistence()

    # 演示狀態回滾
    demonstrate_state_rollback()

    # 打印關鍵概念
    print_concepts()

    print("\n✅ 示例完成！")
    print("💡 提示: 持久化是構建可靠 Agent 系統的基礎")
    print("      合理使用檢查點可以提高系統的容錯能力和用戶體驗")

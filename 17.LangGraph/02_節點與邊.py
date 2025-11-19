#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LangGraph 示例 02: 節點與邊

本示例展示:
1. 不同類型的邊：普通邊、條件邊
2. 節點之間的數據流轉
3. 動態路由決策
4. 多路徑執行
"""

from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# 定義狀態
class WorkflowState(TypedDict):
    input_text: str
    sentiment: str  # positive, negative, neutral
    response: str
    steps: list

# 節點1: 分析情感
def analyze_sentiment(state: WorkflowState) -> WorkflowState:
    """分析文本情感"""
    print(f"📊 分析情感: {state['input_text']}")
    
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    
    prompt = f"""分析以下文本的情感，只回答 positive、negative 或 neutral：
    
文本: {state['input_text']}

情感:"""
    
    result = llm.invoke(prompt)
    sentiment = result.content.strip().lower()
    
    state["sentiment"] = sentiment
    state["steps"].append("sentiment_analysis")
    
    print(f"✅ 情感: {sentiment}")
    return state

# 節點2: 正面回應
def positive_response(state: WorkflowState) -> WorkflowState:
    """生成正面回應"""
    print("😊 生成正面回應")
    state["response"] = "太好了！我很高興聽到這個好消息！"
    state["steps"].append("positive_response")
    return state

# 節點3: 負面回應
def negative_response(state: WorkflowState) -> WorkflowState:
    """生成負面回應"""
    print("😢 生成負面回應")
    state["response"] = "我很抱歉聽到這個。我能幫你做些什麼嗎？"
    state["steps"].append("negative_response")
    return state

# 節點4: 中性回應
def neutral_response(state: WorkflowState) -> WorkflowState:
    """生成中性回應"""
    print("😐 生成中性回應")
    state["response"] = "我明白了。還有什麼我可以幫助你的嗎？"
    state["steps"].append("neutral_response")
    return state

# 條件邊: 根據情感路由
def route_by_sentiment(state: WorkflowState) -> Literal["positive", "negative", "neutral"]:
    """
    條件邊函數
    
    根據狀態決定下一個節點
    返回值必須是添加的條件邊中的鍵
    """
    sentiment = state["sentiment"]
    print(f"🔀 路由決策: {sentiment}")
    
    if "positive" in sentiment:
        return "positive"
    elif "negative" in sentiment:
        return "negative"
    else:
        return "neutral"

# 構建圖
def create_routing_graph():
    """創建帶條件路由的圖"""
    workflow = StateGraph(WorkflowState)
    
    # 添加節點
    workflow.add_node("analyze", analyze_sentiment)
    workflow.add_node("positive", positive_response)
    workflow.add_node("negative", negative_response)
    workflow.add_node("neutral", neutral_response)
    
    # 設置入口
    workflow.set_entry_point("analyze")
    
    # 添加條件邊
    workflow.add_conditional_edges(
        "analyze",  # 源節點
        route_by_sentiment,  # 路由函數
        {
            "positive": "positive",  # 路由結果 -> 目標節點
            "negative": "negative",
            "neutral": "neutral"
        }
    )
    
    # 所有回應節點都連接到 END
    workflow.add_edge("positive", END)
    workflow.add_edge("negative", END)
    workflow.add_edge("neutral", END)
    
    return workflow

# 主程序
if __name__ == "__main__":
    print("=" * 60)
    print("LangGraph 示例: 節點與邊")
    print("=" * 60)
    
    workflow = create_routing_graph()
    app = workflow.compile()
    
    # 測試不同情感的文本
    test_cases = [
        "我今天心情特別好，剛拿到了升職！",
        "我的項目失敗了，感覺很沮喪。",
        "今天是星期三。"
    ]
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"測試案例 {i}: {text}")
        print(f"{'='*60}")
        
        initial_state = {
            "input_text": text,
            "sentiment": "",
            "response": "",
            "steps": []
        }
        
        result = app.invoke(initial_state)
        
        print(f"\n結果:")
        print(f"  情感: {result['sentiment']}")
        print(f"  回應: {result['response']}")
        print(f"  執行步驟: {' -> '.join(result['steps'])}")
    
    print("\n" + "=" * 60)
    print("💡 關鍵概念:")
    print("=" * 60)
    print("""
1. 普通邊 (Normal Edges):
   - add_edge(source, target)
   - 固定的路徑

2. 條件邊 (Conditional Edges):
   - add_conditional_edges(source, routing_function, mapping)
   - 根據狀態動態決定路徑
   - 路由函數返回映射中的鍵

3. 路由函數:
   - 接收當前狀態
   - 返回路由鍵
   - 決定下一個節點
    """)
    
    print("\n✅ 示例完成！")

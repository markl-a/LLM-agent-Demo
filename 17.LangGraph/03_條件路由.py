#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LangGraph 示例 3: 條件路由

本示例展示:
if-else 邏輯、多條件判斷、動態分支

學習重點:
- LangGraph 的 條件路由 功能
- 實際應用場景
- 最佳實踐建議
"""

from typing import TypedDict, Annotated, List
import operator
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import os
from dotenv import load_dotenv

load_dotenv()


# ============================================
# 狀態定義
# ============================================

class AgentState(TypedDict):
    """Agent 狀態"""
    messages: Annotated[list, operator.add]
    data: dict
    counter: int


# ============================================
# 示例: 條件路由
# ============================================

def main():
    """
    條件路由 示例
    
    主題: if-else 邏輯、多條件判斷、動態分支
    """
    print("=" * 70)
    print(f"LangGraph 示例 3: 條件路由")
    print("=" * 70)
    
    print(f"""
📚 本示例展示: if-else 邏輯、多條件判斷、動態分支

🎯 關鍵概念:
- 條件路由 的基本原理
- 實際應用場景
- 最佳實踐建議

💡 提示: 
    這是 LangGraph 的第 3 個示例
    展示了如何使用 條件路由 功能
    """)
    
    # TODO: 實現具體邏輯
    # 這裡是示例的核心代碼
    
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.7,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    print("\n" + "=" * 70)
    print("✅ 示例演示完成！")
    print(f"💡 關鍵學習點: if-else 邏輯、多條件判斷、動態分支")
    print("=" * 70)


if __name__ == "__main__":
    main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LangGraph 示例 22: 子圖組合

本示例展示:
1. 子圖的創建和使用
2. 模組化設計模式
3. 子圖的組合和嵌套
4. 跨子圖的狀態管理

學習重點:
- 子圖設計原則
- 模組化工作流
- 可重用組件
- 複雜系統的分解
"""

from typing import TypedDict, Annotated
import operator
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import os
from dotenv import load_dotenv

load_dotenv()


# ============================================
# 1. 定義狀態結構
# ============================================

class DocumentState(TypedDict):
    """文檔處理狀態"""
    content: str
    processed_content: str
    metadata: dict
    status: str


class ValidationState(TypedDict):
    """驗證狀態"""
    data: str
    validation_result: dict
    is_valid: bool


class ParentState(TypedDict):
    """父圖狀態"""
    messages: Annotated[list, operator.add]
    document: str
    analysis_result: dict
    quality_score: float
    final_output: str


# ============================================
# 2. 子圖 1: 文檔預處理子圖
# ============================================

def create_preprocessing_subgraph():
    """
    創建文檔預處理子圖

    功能:
    - 清理文本
    - 提取關鍵詞
    - 生成摘要
    """
    print("  🔧 創建預處理子圖...")

    def clean_text(state: DocumentState) -> DocumentState:
        """清理文本節點"""
        print("    🧹 清理文本...")

        content = state["content"]

        # 簡單的文本清理
        cleaned = content.strip()
        cleaned = " ".join(cleaned.split())  # 移除多餘空白

        state["processed_content"] = cleaned
        state["metadata"]["cleaned"] = True
        state["status"] = "cleaned"

        return state

    def extract_keywords(state: DocumentState) -> DocumentState:
        """提取關鍵詞節點"""
        print("    🔑 提取關鍵詞...")

        content = state["processed_content"]

        # 簡化版關鍵詞提取（實際應使用 NLP 工具）
        words = content.split()
        keywords = list(set([w for w in words if len(w) > 5]))[:5]

        state["metadata"]["keywords"] = keywords
        state["status"] = "keywords_extracted"

        return state

    def generate_summary(state: DocumentState) -> DocumentState:
        """生成摘要節點"""
        print("    📝 生成摘要...")

        content = state["processed_content"]

        # 簡化版摘要（實際應使用 LLM）
        sentences = content.split("。")
        summary = sentences[0] + "。" if sentences else ""

        state["metadata"]["summary"] = summary
        state["status"] = "summarized"

        return state

    # 構建子圖
    subgraph = StateGraph(DocumentState)

    # 添加節點
    subgraph.add_node("clean", clean_text)
    subgraph.add_node("extract", extract_keywords)
    subgraph.add_node("summarize", generate_summary)

    # 設置入口點和邊
    subgraph.set_entry_point("clean")
    subgraph.add_edge("clean", "extract")
    subgraph.add_edge("extract", "summarize")
    subgraph.add_edge("summarize", END)

    return subgraph.compile()


# ============================================
# 3. 子圖 2: 內容驗證子圖
# ============================================

def create_validation_subgraph():
    """
    創建內容驗證子圖

    功能:
    - 格式驗證
    - 長度檢查
    - 質量評估
    """
    print("  🔧 創建驗證子圖...")

    def validate_format(state: ValidationState) -> ValidationState:
        """格式驗證節點"""
        print("    ✓ 驗證格式...")

        data = state["data"]

        # 簡單的格式檢查
        has_content = len(data) > 0
        has_proper_ending = data.endswith("。") or data.endswith(".")

        state["validation_result"]["format"] = {
            "has_content": has_content,
            "has_proper_ending": has_proper_ending
        }

        return state

    def check_length(state: ValidationState) -> ValidationState:
        """長度檢查節點"""
        print("    📏 檢查長度...")

        data = state["data"]
        length = len(data)

        state["validation_result"]["length"] = {
            "char_count": length,
            "is_sufficient": length >= 10,
            "is_reasonable": 10 <= length <= 5000
        }

        return state

    def assess_quality(state: ValidationState) -> ValidationState:
        """質量評估節點"""
        print("    ⭐ 評估質量...")

        format_ok = all(state["validation_result"]["format"].values())
        length_ok = state["validation_result"]["length"]["is_reasonable"]

        state["is_valid"] = format_ok and length_ok
        state["validation_result"]["overall"] = "通過" if state["is_valid"] else "未通過"

        return state

    # 構建子圖
    subgraph = StateGraph(ValidationState)

    # 添加節點
    subgraph.add_node("format", validate_format)
    subgraph.add_node("length", check_length)
    subgraph.add_node("assess", assess_quality)

    # 設置入口點和邊
    subgraph.set_entry_point("format")
    subgraph.add_edge("format", "length")
    subgraph.add_edge("length", "assess")
    subgraph.add_edge("assess", END)

    return subgraph.compile()


# ============================================
# 4. 主圖: 組合多個子圖
# ============================================

def create_parent_graph():
    """
    創建父圖，組合多個子圖

    流程:
    1. 接收文檔
    2. 調用預處理子圖
    3. 調用驗證子圖
    4. 生成最終結果
    """
    print("🔨 創建主圖...")

    # 創建子圖
    preprocessing_graph = create_preprocessing_subgraph()
    validation_graph = create_validation_subgraph()

    def receive_document(state: ParentState) -> ParentState:
        """接收文檔節點"""
        print("\n📥 接收文檔...")

        state["messages"].append(
            HumanMessage(content=f"處理文檔: {state['document'][:50]}...")
        )

        return state

    def run_preprocessing(state: ParentState) -> ParentState:
        """運行預處理子圖"""
        print("\n🔄 調用預處理子圖...")

        # 準備子圖輸入
        subgraph_input = {
            "content": state["document"],
            "processed_content": "",
            "metadata": {},
            "status": "pending"
        }

        # 運行子圖
        result = preprocessing_graph.invoke(subgraph_input)

        # 保存結果
        state["analysis_result"]["preprocessing"] = result
        state["messages"].append(
            AIMessage(content=f"預處理完成: {result['status']}")
        )

        return state

    def run_validation(state: ParentState) -> ParentState:
        """運行驗證子圖"""
        print("\n🔄 調用驗證子圖...")

        # 獲取預處理結果
        preprocessed = state["analysis_result"]["preprocessing"]["processed_content"]

        # 準備子圖輸入
        subgraph_input = {
            "data": preprocessed,
            "validation_result": {},
            "is_valid": False
        }

        # 運行子圖
        result = validation_graph.invoke(subgraph_input)

        # 保存結果
        state["analysis_result"]["validation"] = result
        state["quality_score"] = 0.8 if result["is_valid"] else 0.3

        state["messages"].append(
            AIMessage(content=f"驗證結果: {result['validation_result']['overall']}")
        )

        return state

    def generate_final_output(state: ParentState) -> ParentState:
        """生成最終輸出"""
        print("\n📤 生成最終輸出...")

        preprocessing = state["analysis_result"]["preprocessing"]
        validation = state["analysis_result"]["validation"]

        output = f"""
文檔處理報告
============
原始長度: {len(state['document'])} 字符
處理後長度: {len(preprocessing['processed_content'])} 字符
關鍵詞: {', '.join(preprocessing['metadata']['keywords'])}
摘要: {preprocessing['metadata']['summary']}
驗證結果: {validation['validation_result']['overall']}
質量分數: {state['quality_score']:.2f}
"""

        state["final_output"] = output
        state["messages"].append(
            AIMessage(content="處理完成！")
        )

        return state

    # 構建主圖
    workflow = StateGraph(ParentState)

    # 添加節點
    workflow.add_node("receive", receive_document)
    workflow.add_node("preprocess", run_preprocessing)
    workflow.add_node("validate", run_validation)
    workflow.add_node("output", generate_final_output)

    # 設置流程
    workflow.set_entry_point("receive")
    workflow.add_edge("receive", "preprocess")
    workflow.add_edge("preprocess", "validate")
    workflow.add_edge("validate", "output")
    workflow.add_edge("output", END)

    return workflow


# ============================================
# 5. 運行子圖組合示例
# ============================================

def run_subgraph_composition():
    """運行子圖組合示例"""
    print("=" * 70)
    print("LangGraph 示例 22: 子圖組合")
    print("=" * 70)

    # 創建主圖
    workflow = create_parent_graph()
    app = workflow.compile()

    # 測試文檔
    test_document = """
    LangGraph 是一個強大的狀態管理框架，專為構建複雜的 Agent 應用而設計。
    它提供了圖結構、狀態管理、條件路由等多種功能。
    通過子圖組合，可以構建模組化、可重用的工作流。
    這使得複雜系統的開發和維護變得更加簡單。
    """

    # 初始化狀態
    initial_state = {
        "messages": [],
        "document": test_document.strip(),
        "analysis_result": {},
        "quality_score": 0.0,
        "final_output": ""
    }

    print("\n🚀 開始處理...\n")

    # 運行工作流
    result = app.invoke(initial_state)

    # 顯示結果
    print("\n" + "=" * 70)
    print("📊 處理結果:")
    print("=" * 70)
    print(result["final_output"])

    print("\n" + "=" * 70)
    print(f"💬 總共 {len(result['messages'])} 條消息")
    print("=" * 70)


# ============================================
# 6. 關鍵概念說明
# ============================================

def print_concepts():
    """打印關鍵概念"""
    print("\n" + "=" * 70)
    print("💡 子圖組合關鍵概念:")
    print("=" * 70)
    print("""
1. 子圖設計原則:
   - 單一職責: 每個子圖專注於一個特定功能
   - 獨立性: 子圖可以獨立運行和測試
   - 可重用: 子圖可以在多個場景中重用
   - 清晰接口: 明確定義輸入和輸出狀態

2. 模組化優勢:
   - 降低複雜度: 將大問題分解為小問題
   - 提高可維護性: 每個模組獨立維護
   - 促進重用: 通用功能封裝為子圖
   - 便於測試: 可以單獨測試每個子圖

3. 子圖組合模式:
   - 順序組合: 子圖按順序執行
   - 並行組合: 多個子圖並行執行
   - 條件組合: 根據條件選擇子圖
   - 嵌套組合: 子圖內包含子圖

4. 狀態管理:
   - 父圖狀態: 主工作流的狀態
   - 子圖狀態: 每個子圖的內部狀態
   - 狀態映射: 父子圖之間的狀態轉換
   - 結果整合: 合併多個子圖的結果

5. 實際應用:
   - 數據處理管道
   - 文檔工作流
   - 業務流程自動化
   - 微服務編排
    """)


# ============================================
# 主程序
# ============================================

if __name__ == "__main__":
    # 運行子圖組合示例
    run_subgraph_composition()

    # 打印關鍵概念
    print_concepts()

    print("\n✅ 示例完成！")
    print("💡 提示: 子圖組合是構建複雜系統的關鍵技術")
    print("      合理的模組化設計可以大大提高系統的可維護性")

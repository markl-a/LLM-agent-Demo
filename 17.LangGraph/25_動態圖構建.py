#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LangGraph 示例 25: 動態圖構建

本示例展示:
1. 運行時動態添加節點和邊
2. 基於輸入動態構建工作流
3. 條件節點創建
4. 圖的動態重組

學習重點:
- 動態圖構建策略
- 運行時工作流調整
- 靈活的架構設計
- 適配不同的業務場景
"""

from typing import TypedDict, Annotated, List, Dict, Callable
import operator
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import os
from dotenv import load_dotenv

load_dotenv()


# ============================================
# 1. 定義通用狀態
# ============================================

class DynamicState(TypedDict):
    """
    動態工作流狀態

    包含:
    - messages: 消息列表
    - workflow_spec: 工作流規格說明
    - current_step: 當前步驟
    - results: 執行結果
    - metadata: 元數據
    """
    messages: Annotated[list, operator.add]
    workflow_spec: dict
    current_step: str
    results: dict
    metadata: dict


# ============================================
# 2. 工作流構建器
# ============================================

class DynamicWorkflowBuilder:
    """動態工作流構建器"""

    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY")
        )

    def create_generic_node(self, node_name: str, node_config: dict) -> Callable:
        """
        創建通用節點函數

        參數:
            node_name: 節點名稱
            node_config: 節點配置
        """
        def node_function(state: DynamicState) -> DynamicState:
            print(f"\n🔄 [{node_name}] 執行中...")

            node_type = node_config.get("type", "generic")
            description = node_config.get("description", "")

            if node_type == "llm":
                # LLM 處理節點
                result = self._process_with_llm(state, description)
                state["results"][node_name] = result

            elif node_type == "transform":
                # 數據轉換節點
                result = self._transform_data(state, node_config)
                state["results"][node_name] = result

            elif node_type == "validate":
                # 驗證節點
                result = self._validate_data(state, node_config)
                state["results"][node_name] = result

            else:
                # 通用處理節點
                result = f"處理完成: {description}"
                state["results"][node_name] = result

            state["current_step"] = node_name
            state["messages"].append(
                AIMessage(content=f"[{node_name}] 完成")
            )

            print(f"   ✅ {node_name} 完成")

            return state

        return node_function

    def _process_with_llm(self, state: DynamicState, prompt: str) -> str:
        """使用 LLM 處理"""
        messages = [
            SystemMessage(content="你是一個專業的助手"),
            HumanMessage(content=prompt)
        ]

        response = self.llm.invoke(messages)
        return response.content[:100] + "..."

    def _transform_data(self, state: DynamicState, config: dict) -> dict:
        """轉換數據"""
        transform_type = config.get("transform_type", "uppercase")

        if transform_type == "uppercase":
            return {"transformed": "DATA TRANSFORMED"}
        elif transform_type == "lowercase":
            return {"transformed": "data transformed"}
        else:
            return {"transformed": "data processed"}

    def _validate_data(self, state: DynamicState, config: dict) -> dict:
        """驗證數據"""
        rules = config.get("rules", [])

        return {
            "is_valid": True,
            "rules_checked": len(rules),
            "status": "通過"
        }

    def build_graph_from_spec(self, spec: dict) -> StateGraph:
        """
        根據規格說明構建圖

        參數:
            spec: 包含節點和邊的規格說明
                {
                    "nodes": [
                        {"name": "node1", "type": "llm", "description": "..."},
                        {"name": "node2", "type": "transform", ...}
                    ],
                    "edges": [
                        {"from": "node1", "to": "node2"},
                        ...
                    ],
                    "entry": "node1"
                }
        """
        print(f"\n🔨 根據規格動態構建圖...")

        # 創建狀態圖
        workflow = StateGraph(DynamicState)

        # 動態添加節點
        node_configs = {}
        for node_spec in spec.get("nodes", []):
            node_name = node_spec["name"]
            node_configs[node_name] = node_spec

            # 創建並添加節點
            node_function = self.create_generic_node(node_name, node_spec)
            workflow.add_node(node_name, node_function)

            print(f"   ➕ 添加節點: {node_name} ({node_spec.get('type', 'generic')})")

        # 設置入口點
        entry_node = spec.get("entry", spec["nodes"][0]["name"])
        workflow.set_entry_point(entry_node)
        print(f"   🚪 入口點: {entry_node}")

        # 動態添加邊
        for edge_spec in spec.get("edges", []):
            from_node = edge_spec["from"]
            to_node = edge_spec["to"]

            if to_node == "END":
                workflow.add_edge(from_node, END)
            else:
                workflow.add_edge(from_node, to_node)

            print(f"   🔗 添加邊: {from_node} → {to_node}")

        print(f"   ✅ 圖構建完成")

        return workflow


# ============================================
# 3. 預定義的工作流模板
# ============================================

class WorkflowTemplates:
    """工作流模板庫"""

    @staticmethod
    def data_processing_pipeline() -> dict:
        """數據處理管道"""
        return {
            "name": "數據處理管道",
            "nodes": [
                {
                    "name": "ingest",
                    "type": "generic",
                    "description": "數據接入"
                },
                {
                    "name": "clean",
                    "type": "transform",
                    "description": "數據清洗",
                    "transform_type": "uppercase"
                },
                {
                    "name": "validate",
                    "type": "validate",
                    "description": "數據驗證",
                    "rules": ["non_empty", "format_check"]
                },
                {
                    "name": "analyze",
                    "type": "llm",
                    "description": "分析數據質量並生成報告"
                }
            ],
            "edges": [
                {"from": "ingest", "to": "clean"},
                {"from": "clean", "to": "validate"},
                {"from": "validate", "to": "analyze"},
                {"from": "analyze", "to": "END"}
            ],
            "entry": "ingest"
        }

    @staticmethod
    def content_creation_workflow() -> dict:
        """內容創作工作流"""
        return {
            "name": "內容創作工作流",
            "nodes": [
                {
                    "name": "research",
                    "type": "llm",
                    "description": "研究主題並收集資料"
                },
                {
                    "name": "outline",
                    "type": "llm",
                    "description": "創建文章大綱"
                },
                {
                    "name": "write",
                    "type": "llm",
                    "description": "撰寫文章內容"
                },
                {
                    "name": "review",
                    "type": "validate",
                    "description": "審查內容質量",
                    "rules": ["grammar", "coherence", "length"]
                }
            ],
            "edges": [
                {"from": "research", "to": "outline"},
                {"from": "outline", "to": "write"},
                {"from": "write", "to": "review"},
                {"from": "review", "to": "END"}
            ],
            "entry": "research"
        }

    @staticmethod
    def simple_qa_workflow() -> dict:
        """簡單問答工作流"""
        return {
            "name": "簡單問答工作流",
            "nodes": [
                {
                    "name": "understand",
                    "type": "llm",
                    "description": "理解用戶問題"
                },
                {
                    "name": "answer",
                    "type": "llm",
                    "description": "生成答案"
                }
            ],
            "edges": [
                {"from": "understand", "to": "answer"},
                {"from": "answer", "to": "END"}
            ],
            "entry": "understand"
        }


# ============================================
# 4. 動態工作流選擇
# ============================================

def select_workflow_by_task(task_type: str) -> dict:
    """
    根據任務類型選擇工作流

    參數:
        task_type: 任務類型（data_processing, content_creation, qa）

    返回:
        工作流規格
    """
    templates = WorkflowTemplates()

    workflows = {
        "data_processing": templates.data_processing_pipeline(),
        "content_creation": templates.content_creation_workflow(),
        "qa": templates.simple_qa_workflow()
    }

    return workflows.get(task_type, templates.simple_qa_workflow())


# ============================================
# 5. 運行動態工作流
# ============================================

def run_dynamic_workflow_example():
    """運行動態工作流示例"""
    print("=" * 70)
    print("LangGraph 示例 25: 動態圖構建")
    print("=" * 70)

    # 創建工作流構建器
    builder = DynamicWorkflowBuilder()

    # ========================================
    # 示例 1: 數據處理管道
    # ========================================
    print("\n" + "=" * 70)
    print("示例 1: 動態構建數據處理管道")
    print("=" * 70)

    spec1 = select_workflow_by_task("data_processing")
    print(f"\n📋 工作流: {spec1['name']}")
    print(f"   節點數: {len(spec1['nodes'])}")
    print(f"   邊數: {len(spec1['edges'])}")

    workflow1 = builder.build_graph_from_spec(spec1)
    app1 = workflow1.compile()

    # 運行工作流
    initial_state1 = {
        "messages": [],
        "workflow_spec": spec1,
        "current_step": "",
        "results": {},
        "metadata": {"task": "data_processing"}
    }

    print("\n🚀 運行工作流...")
    result1 = app1.invoke(initial_state1)

    print("\n📊 執行結果:")
    for node_name, result in result1["results"].items():
        print(f"   - {node_name}: {str(result)[:50]}...")

    # ========================================
    # 示例 2: 內容創作工作流
    # ========================================
    print("\n" + "=" * 70)
    print("示例 2: 動態構建內容創作工作流")
    print("=" * 70)

    spec2 = select_workflow_by_task("content_creation")
    print(f"\n📋 工作流: {spec2['name']}")
    print(f"   節點數: {len(spec2['nodes'])}")
    print(f"   邊數: {len(spec2['edges'])}")

    workflow2 = builder.build_graph_from_spec(spec2)
    app2 = workflow2.compile()

    initial_state2 = {
        "messages": [],
        "workflow_spec": spec2,
        "current_step": "",
        "results": {},
        "metadata": {"task": "content_creation", "topic": "AI"}
    }

    print("\n🚀 運行工作流...")
    result2 = app2.invoke(initial_state2)

    print("\n📊 執行結果:")
    for node_name, result in result2["results"].items():
        print(f"   - {node_name}: {str(result)[:50]}...")

    # ========================================
    # 示例 3: 自定義工作流
    # ========================================
    print("\n" + "=" * 70)
    print("示例 3: 完全自定義的工作流")
    print("=" * 70)

    custom_spec = {
        "name": "自定義測試工作流",
        "nodes": [
            {
                "name": "start",
                "type": "generic",
                "description": "開始處理"
            },
            {
                "name": "step1",
                "type": "llm",
                "description": "執行第一步 LLM 處理"
            },
            {
                "name": "step2",
                "type": "transform",
                "description": "數據轉換",
                "transform_type": "uppercase"
            },
            {
                "name": "finish",
                "type": "generic",
                "description": "完成處理"
            }
        ],
        "edges": [
            {"from": "start", "to": "step1"},
            {"from": "step1", "to": "step2"},
            {"from": "step2", "to": "finish"},
            {"from": "finish", "to": "END"}
        ],
        "entry": "start"
    }

    print(f"\n📋 工作流: {custom_spec['name']}")
    workflow3 = builder.build_graph_from_spec(custom_spec)
    app3 = workflow3.compile()

    initial_state3 = {
        "messages": [],
        "workflow_spec": custom_spec,
        "current_step": "",
        "results": {},
        "metadata": {"custom": True}
    }

    print("\n🚀 運行工作流...")
    result3 = app3.invoke(initial_state3)

    print("\n📊 執行結果:")
    print(f"   完成步驟數: {len(result3['results'])}")
    print(f"   當前步驟: {result3['current_step']}")


# ============================================
# 6. 關鍵概念說明
# ============================================

def print_concepts():
    """打印關鍵概念"""
    print("\n" + "=" * 70)
    print("💡 動態圖構建關鍵概念:")
    print("=" * 70)
    print("""
1. 動態構建的優勢:
   - 靈活性: 根據需求動態調整工作流
   - 可配置: 通過配置文件定義工作流
   - 可擴展: 輕鬆添加新的節點類型
   - 可重用: 模板化的工作流設計

2. 構建策略:
   - 規格驅動: 基於 JSON/YAML 規格構建
   - 模板模式: 預定義常用工作流模板
   - 工廠模式: 動態創建節點函數
   - 策略模式: 根據任務類型選擇工作流

3. 節點工廠:
   - 通用節點函數生成器
   - 基於配置創建特定行為
   - 支持多種節點類型
   - 統一的接口設計

4. 應用場景:
   - 多租戶系統（每個租戶不同工作流）
   - A/B 測試（不同版本的工作流）
   - 規則引擎（基於規則構建流程）
   - 工作流編排平台

5. 設計考慮:
   - 節點命名規範
   - 狀態結構設計
   - 錯誤處理機制
   - 性能優化

6. 局限性:
   - 複雜度增加
   - 調試困難
   - 類型檢查弱化
   - 需要良好的文檔

7. 最佳實踐:
   - 定義清晰的規格格式
   - 驗證規格的正確性
   - 提供豐富的模板庫
   - 記錄工作流的執行歷史
    """)


# ============================================
# 主程序
# ============================================

if __name__ == "__main__":
    # 運行動態工作流示例
    run_dynamic_workflow_example()

    # 打印關鍵概念
    print_concepts()

    print("\n✅ 示例完成！")
    print("💡 提示: 動態圖構建提供了極大的靈活性")
    print("      適合需要運行時調整工作流的場景")

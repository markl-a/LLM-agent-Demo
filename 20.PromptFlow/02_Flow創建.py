"""
PromptFlow Flow 創建指南

這個範例展示如何創建和管理 PromptFlow 的流程：
1. 理解 Flow 的結構（DAG - 有向無環圖）
2. 創建簡單的 Flow
3. 定義節點和連接
4. 保存和加載 Flow
5. Flow 的配置和元數據

作者：LLM Agent Demo Project
日期：2025-12-15
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any


# ============================================
# 範例 1: Flow 的基本結構
# ============================================
def example_1_flow_structure():
    """
    展示 Flow 的基本結構和組成部分

    Flow 由以下部分組成：
    - flow.dag.yaml: 流程定義文件
    - 節點 (Nodes): 執行具體任務的組件
    - 連接 (Connections): 節點之間的數據流
    """
    print("=" * 50)
    print("範例 1: Flow 的基本結構")
    print("=" * 50)

    # Flow 的目錄結構
    flow_structure = """
    my_flow/
    ├── flow.dag.yaml          # 流程定義文件（必需）
    ├── .promptflow/           # PromptFlow 系統文件夾
    │   └── flow.tools.json    # 工具定義
    ├── requirements.txt       # Python 依賴
    ├── data/                  # 測試數據
    │   └── test_data.jsonl
    └── nodes/                 # 節點實現
        ├── node1.py
        └── node2.py
    """

    print("Flow 目錄結構:")
    print(flow_structure)

    # Flow DAG 的基本組成
    print("\nFlow DAG 包含的元素:")
    print("1. inputs - 流程的輸入參數")
    print("2. outputs - 流程的輸出結果")
    print("3. nodes - 執行任務的節點")
    print("4. node_variants - 節點的變體（用於 A/B 測試）")
    print()


# ============================================
# 範例 2: 創建簡單的 Flow DAG 配置
# ============================================
def example_2_create_simple_flow():
    """
    創建一個簡單的 Flow DAG 配置文件

    這個範例展示如何創建一個包含輸入、處理和輸出的基本流程。
    """
    print("=" * 50)
    print("範例 2: 創建簡單的 Flow DAG")
    print("=" * 50)

    # 定義 Flow DAG 配置
    flow_dag = {
        "$schema": "https://azuremlschemas.azureedge.net/promptflow/latest/Flow.schema.json",
        "inputs": {
            "question": {
                "type": "string",
                "description": "用戶的問題"
            }
        },
        "outputs": {
            "answer": {
                "type": "string",
                "reference": "${generate_answer.output}",
                "description": "AI 的回答"
            }
        },
        "nodes": [
            {
                "name": "process_question",
                "type": "python",
                "source": {
                    "type": "code",
                    "path": "process_question.py"
                },
                "inputs": {
                    "question": "${inputs.question}"
                }
            },
            {
                "name": "generate_answer",
                "type": "llm",
                "source": {
                    "type": "code",
                    "path": "generate_answer.jinja2"
                },
                "inputs": {
                    "processed_question": "${process_question.output}"
                },
                "connection": "azure_openai_connection",
                "api": "chat"
            }
        ]
    }

    # 創建 Flow 目錄
    flow_dir = Path("/home/user/LLM-agent-Demo/20.PromptFlow/simple_flow")
    flow_dir.mkdir(exist_ok=True)

    # 保存 flow.dag.yaml
    flow_dag_path = flow_dir / "flow.dag.yaml"
    with open(flow_dag_path, 'w', encoding='utf-8') as f:
        yaml.dump(flow_dag, f, allow_unicode=True, sort_keys=False)

    print(f"✓ Flow DAG 已創建: {flow_dag_path}")
    print("\nFlow DAG 內容:")
    print(yaml.dump(flow_dag, allow_unicode=True, sort_keys=False))


# ============================================
# 範例 3: 創建節點的 Python 實現
# ============================================
def example_3_create_node_implementation():
    """
    創建 Flow 節點的 Python 實現

    每個 Python 節點都需要一個帶有 @tool 裝飾器的函數。
    """
    print("=" * 50)
    print("範例 3: 創建節點實現")
    print("=" * 50)

    # process_question.py 的內容
    process_question_code = '''"""
處理問題節點

這個節點負責預處理用戶的問題。
"""

from promptflow.core import tool


@tool
def process_question(question: str) -> str:
    """
    預處理用戶問題

    Args:
        question: 用戶的原始問題

    Returns:
        處理後的問題
    """
    # 清理和標準化問題
    processed = question.strip()

    # 確保問題以問號結尾
    if processed and not processed.endswith(('?', '？')):
        processed += '？'

    # 記錄處理
    print(f"原始問題: {question}")
    print(f"處理後: {processed}")

    return processed
'''

    # generate_answer.jinja2 的內容
    generate_answer_template = '''system:
你是一個專業的 AI 助手，擅長回答各種問題。
請用繁體中文提供準確、有用的回答。

user:
{{processed_question}}

assistant:
'''

    # 創建 Flow 目錄（如果不存在）
    flow_dir = Path("/home/user/LLM-agent-Demo/20.PromptFlow/simple_flow")
    flow_dir.mkdir(exist_ok=True)

    # 保存 process_question.py
    process_path = flow_dir / "process_question.py"
    with open(process_path, 'w', encoding='utf-8') as f:
        f.write(process_question_code)

    # 保存 generate_answer.jinja2
    template_path = flow_dir / "generate_answer.jinja2"
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(generate_answer_template)

    print(f"✓ 節點實現已創建:")
    print(f"  - {process_path}")
    print(f"  - {template_path}")
    print()


# ============================================
# 範例 4: 創建複雜的多節點 Flow
# ============================================
def example_4_complex_flow():
    """
    創建一個包含多個節點的複雜 Flow

    這個範例展示如何創建一個完整的 RAG（檢索增強生成）流程。
    """
    print("=" * 50)
    print("範例 4: 創建複雜的多節點 Flow")
    print("=" * 50)

    # RAG Flow 配置
    rag_flow_dag = {
        "$schema": "https://azuremlschemas.azureedge.net/promptflow/latest/Flow.schema.json",
        "name": "rag_flow",
        "description": "檢索增強生成流程",
        "inputs": {
            "question": {
                "type": "string",
                "description": "用戶問題"
            },
            "top_k": {
                "type": "int",
                "default": 3,
                "description": "檢索的文檔數量"
            }
        },
        "outputs": {
            "answer": {
                "type": "string",
                "reference": "${generate_with_context.output}",
                "description": "基於檢索內容的回答"
            },
            "sources": {
                "type": "list",
                "reference": "${retrieve_documents.output}",
                "description": "參考文檔"
            }
        },
        "nodes": [
            {
                "name": "embed_question",
                "type": "python",
                "source": {
                    "type": "code",
                    "path": "embed_question.py"
                },
                "inputs": {
                    "question": "${inputs.question}"
                },
                "comment": "將問題轉換為向量嵌入"
            },
            {
                "name": "retrieve_documents",
                "type": "python",
                "source": {
                    "type": "code",
                    "path": "retrieve_documents.py"
                },
                "inputs": {
                    "question_embedding": "${embed_question.output}",
                    "top_k": "${inputs.top_k}"
                },
                "comment": "從向量數據庫檢索相關文檔"
            },
            {
                "name": "rerank_documents",
                "type": "python",
                "source": {
                    "type": "code",
                    "path": "rerank_documents.py"
                },
                "inputs": {
                    "documents": "${retrieve_documents.output}",
                    "question": "${inputs.question}"
                },
                "comment": "重新排序檢索到的文檔"
            },
            {
                "name": "build_context",
                "type": "python",
                "source": {
                    "type": "code",
                    "path": "build_context.py"
                },
                "inputs": {
                    "documents": "${rerank_documents.output}"
                },
                "comment": "構建上下文字符串"
            },
            {
                "name": "generate_with_context",
                "type": "llm",
                "source": {
                    "type": "code",
                    "path": "generate_with_context.jinja2"
                },
                "inputs": {
                    "question": "${inputs.question}",
                    "context": "${build_context.output}"
                },
                "connection": "azure_openai_connection",
                "api": "chat",
                "comment": "基於上下文生成回答"
            }
        ]
    }

    # 創建 RAG Flow 目錄
    rag_flow_dir = Path("/home/user/LLM-agent-Demo/20.PromptFlow/rag_flow")
    rag_flow_dir.mkdir(exist_ok=True)

    # 保存 flow.dag.yaml
    rag_dag_path = rag_flow_dir / "flow.dag.yaml"
    with open(rag_dag_path, 'w', encoding='utf-8') as f:
        yaml.dump(rag_flow_dag, f, allow_unicode=True, sort_keys=False)

    print(f"✓ RAG Flow DAG 已創建: {rag_dag_path}")

    # 創建節點實現的佔位符
    node_files = [
        "embed_question.py",
        "retrieve_documents.py",
        "rerank_documents.py",
        "build_context.py",
        "generate_with_context.jinja2"
    ]

    for node_file in node_files:
        node_path = rag_flow_dir / node_file
        if not node_path.exists():
            with open(node_path, 'w', encoding='utf-8') as f:
                f.write(f"# {node_file} - 待實現\n")

    print("✓ 節點文件已創建（佔位符）")
    print()


# ============================================
# 範例 5: Flow 元數據和配置
# ============================================
def example_5_flow_metadata():
    """
    配置 Flow 的元數據和設置

    元數據包括版本、作者、標籤等信息。
    """
    print("=" * 50)
    print("範例 5: Flow 元數據配置")
    print("=" * 50)

    # Flow 元數據配置
    flow_metadata = {
        "$schema": "https://azuremlschemas.azureedge.net/promptflow/latest/Flow.schema.json",
        "name": "customer_support_flow",
        "display_name": "客戶支持流程",
        "description": "自動化的客戶支持回答系統",
        "version": "1.0.0",
        "type": "standard",
        "tags": {
            "category": "customer_service",
            "language": "zh-TW",
            "version": "v1"
        },
        "environment": {
            "python_requirements_txt": "requirements.txt",
            "environment_variables": {
                "LOG_LEVEL": "INFO",
                "MAX_RETRIES": "3"
            }
        },
        "inputs": {
            "customer_query": {
                "type": "string",
                "description": "客戶的問題或請求"
            }
        },
        "outputs": {
            "response": {
                "type": "string",
                "reference": "${respond_to_customer.output}"
            }
        },
        "nodes": [
            {
                "name": "classify_intent",
                "type": "python",
                "source": {
                    "type": "code",
                    "path": "classify_intent.py"
                },
                "inputs": {
                    "query": "${inputs.customer_query}"
                }
            },
            {
                "name": "respond_to_customer",
                "type": "llm",
                "source": {
                    "type": "code",
                    "path": "respond.jinja2"
                },
                "inputs": {
                    "query": "${inputs.customer_query}",
                    "intent": "${classify_intent.output}"
                },
                "connection": "azure_openai_connection",
                "api": "chat"
            }
        ]
    }

    # 創建 Flow 目錄
    metadata_flow_dir = Path("/home/user/LLM-agent-Demo/20.PromptFlow/customer_support_flow")
    metadata_flow_dir.mkdir(exist_ok=True)

    # 保存配置
    metadata_path = metadata_flow_dir / "flow.dag.yaml"
    with open(metadata_path, 'w', encoding='utf-8') as f:
        yaml.dump(flow_metadata, f, allow_unicode=True, sort_keys=False)

    # 創建 requirements.txt
    requirements_content = """promptflow>=1.13.0
promptflow-tools>=1.4.0
openai>=1.0.0
python-dotenv>=1.0.0
"""
    requirements_path = metadata_flow_dir / "requirements.txt"
    with open(requirements_path, 'w', encoding='utf-8') as f:
        f.write(requirements_content)

    print(f"✓ Flow 元數據已創建: {metadata_path}")
    print(f"✓ Requirements 已創建: {requirements_path}")
    print()


# ============================================
# 範例 6: 節點變體（Variants）
# ============================================
def example_6_node_variants():
    """
    創建節點變體用於 A/B 測試

    變體允許您在同一個 Flow 中測試不同的實現。
    """
    print("=" * 50)
    print("範例 6: 節點變體")
    print("=" * 50)

    # 包含變體的 Flow 配置
    variant_flow = {
        "$schema": "https://azuremlschemas.azureedge.net/promptflow/latest/Flow.schema.json",
        "name": "ab_test_flow",
        "inputs": {
            "text": {
                "type": "string"
            }
        },
        "outputs": {
            "result": {
                "type": "string",
                "reference": "${summarize.output}"
            }
        },
        "nodes": [
            {
                "name": "summarize",
                "type": "llm",
                "source": {
                    "type": "code",
                    "path": "summarize.jinja2"
                },
                "inputs": {
                    "text": "${inputs.text}"
                },
                "connection": "azure_openai_connection",
                "api": "chat",
                "use_variants": True
            }
        ],
        "node_variants": {
            "summarize": {
                "default_variant_id": "variant_0",
                "variants": {
                    "variant_0": {
                        "node": {
                            "name": "summarize",
                            "type": "llm",
                            "source": {
                                "type": "code",
                                "path": "summarize_short.jinja2"
                            },
                            "inputs": {
                                "text": "${inputs.text}"
                            },
                            "connection": "azure_openai_connection",
                            "api": "chat",
                            "description": "簡短摘要版本"
                        }
                    },
                    "variant_1": {
                        "node": {
                            "name": "summarize",
                            "type": "llm",
                            "source": {
                                "type": "code",
                                "path": "summarize_detailed.jinja2"
                            },
                            "inputs": {
                                "text": "${inputs.text}"
                            },
                            "connection": "azure_openai_connection",
                            "api": "chat",
                            "description": "詳細摘要版本"
                        }
                    }
                }
            }
        }
    }

    # 創建 Flow 目錄
    variant_flow_dir = Path("/home/user/LLM-agent-Demo/20.PromptFlow/ab_test_flow")
    variant_flow_dir.mkdir(exist_ok=True)

    # 保存配置
    variant_path = variant_flow_dir / "flow.dag.yaml"
    with open(variant_path, 'w', encoding='utf-8') as f:
        yaml.dump(variant_flow, f, allow_unicode=True, sort_keys=False)

    print(f"✓ 變體 Flow 已創建: {variant_path}")
    print("\n變體說明:")
    print("- variant_0: 生成簡短摘要")
    print("- variant_1: 生成詳細摘要")
    print("可以運行批量測試來比較不同變體的性能")
    print()


# ============================================
# 範例 7: 使用 Python 代碼創建 Flow
# ============================================
def example_7_programmatic_flow_creation():
    """
    使用 Python 代碼程序化創建 Flow

    這種方法適合動態生成流程或自動化工作流。
    """
    print("=" * 50)
    print("範例 7: 程序化創建 Flow")
    print("=" * 50)

    class FlowBuilder:
        """Flow 構建器類"""

        def __init__(self, name: str, description: str = ""):
            self.flow_config = {
                "$schema": "https://azuremlschemas.azureedge.net/promptflow/latest/Flow.schema.json",
                "name": name,
                "description": description,
                "inputs": {},
                "outputs": {},
                "nodes": []
            }

        def add_input(self, name: str, type_: str, description: str = "", default: Any = None):
            """添加輸入參數"""
            input_def = {
                "type": type_,
                "description": description
            }
            if default is not None:
                input_def["default"] = default

            self.flow_config["inputs"][name] = input_def
            return self

        def add_output(self, name: str, type_: str, reference: str, description: str = ""):
            """添加輸出"""
            self.flow_config["outputs"][name] = {
                "type": type_,
                "reference": reference,
                "description": description
            }
            return self

        def add_python_node(self, name: str, source_path: str, inputs: Dict[str, str]):
            """添加 Python 節點"""
            node = {
                "name": name,
                "type": "python",
                "source": {
                    "type": "code",
                    "path": source_path
                },
                "inputs": inputs
            }
            self.flow_config["nodes"].append(node)
            return self

        def add_llm_node(self, name: str, source_path: str, inputs: Dict[str, str],
                        connection: str = "azure_openai_connection"):
            """添加 LLM 節點"""
            node = {
                "name": name,
                "type": "llm",
                "source": {
                    "type": "code",
                    "path": source_path
                },
                "inputs": inputs,
                "connection": connection,
                "api": "chat"
            }
            self.flow_config["nodes"].append(node)
            return self

        def build(self) -> dict:
            """構建並返回 Flow 配置"""
            return self.flow_config

        def save(self, directory: Path):
            """保存 Flow 到目錄"""
            directory.mkdir(exist_ok=True)
            flow_path = directory / "flow.dag.yaml"

            with open(flow_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.flow_config, f, allow_unicode=True, sort_keys=False)

            return flow_path

    # 使用 FlowBuilder 創建 Flow
    builder = FlowBuilder(
        name="sentiment_analysis_flow",
        description="文本情感分析流程"
    )

    # 配置流程
    builder.add_input("text", "string", "待分析的文本") \
           .add_python_node(
               "preprocess",
               "preprocess.py",
               {"text": "${inputs.text}"}
           ) \
           .add_llm_node(
               "analyze_sentiment",
               "analyze_sentiment.jinja2",
               {"text": "${preprocess.output}"}
           ) \
           .add_python_node(
               "format_result",
               "format_result.py",
               {"sentiment": "${analyze_sentiment.output}"}
           ) \
           .add_output(
               "sentiment",
               "string",
               "${format_result.output}",
               "情感分析結果"
           )

    # 保存 Flow
    flow_dir = Path("/home/user/LLM-agent-Demo/20.PromptFlow/sentiment_flow")
    saved_path = builder.save(flow_dir)

    print(f"✓ Flow 已程序化創建: {saved_path}")
    print("\nFlow 配置:")
    print(yaml.dump(builder.build(), allow_unicode=True, sort_keys=False))


# ============================================
# 範例 8: 條件分支 Flow
# ============================================
def example_8_conditional_flow():
    """
    創建包含條件分支的 Flow

    使用 Python 節點來實現條件邏輯。
    """
    print("=" * 50)
    print("範例 8: 條件分支 Flow")
    print("=" * 50)

    # 條件 Flow 配置
    conditional_flow = {
        "$schema": "https://azuremlschemas.azureedge.net/promptflow/latest/Flow.schema.json",
        "name": "conditional_routing_flow",
        "description": "根據條件路由到不同處理分支",
        "inputs": {
            "message": {
                "type": "string",
                "description": "用戶消息"
            }
        },
        "outputs": {
            "response": {
                "type": "string",
                "reference": "${route_and_respond.output}",
                "description": "最終響應"
            }
        },
        "nodes": [
            {
                "name": "detect_intent",
                "type": "python",
                "source": {
                    "type": "code",
                    "path": "detect_intent.py"
                },
                "inputs": {
                    "message": "${inputs.message}"
                },
                "comment": "檢測用戶意圖"
            },
            {
                "name": "route_and_respond",
                "type": "python",
                "source": {
                    "type": "code",
                    "path": "route_and_respond.py"
                },
                "inputs": {
                    "message": "${inputs.message}",
                    "intent": "${detect_intent.output}"
                },
                "comment": "根據意圖路由和響應"
            }
        ]
    }

    # 創建條件路由節點的實現
    route_respond_code = '''"""
條件路由和響應節點
"""

from promptflow.core import tool


@tool
def route_and_respond(message: str, intent: str) -> str:
    """
    根據檢測到的意圖選擇不同的響應策略

    Args:
        message: 用戶消息
        intent: 檢測到的意圖

    Returns:
        響應消息
    """
    # 根據不同意圖選擇不同處理
    if intent == "greeting":
        return "您好！很高興見到您。有什麼我可以幫助您的嗎？"

    elif intent == "farewell":
        return "再見！祝您有美好的一天！"

    elif intent == "question":
        return f"我理解您的問題是：{message}。讓我為您查找答案..."

    elif intent == "complaint":
        return "我很抱歉給您帶來了不便。讓我幫您解決這個問題..."

    else:
        return "謝謝您的消息。我會盡力幫助您。"
'''

    # 創建 Flow 目錄
    conditional_dir = Path("/home/user/LLM-agent-Demo/20.PromptFlow/conditional_flow")
    conditional_dir.mkdir(exist_ok=True)

    # 保存配置
    conditional_path = conditional_dir / "flow.dag.yaml"
    with open(conditional_path, 'w', encoding='utf-8') as f:
        yaml.dump(conditional_flow, f, allow_unicode=True, sort_keys=False)

    # 保存路由節點實現
    route_path = conditional_dir / "route_and_respond.py"
    with open(route_path, 'w', encoding='utf-8') as f:
        f.write(route_respond_code)

    print(f"✓ 條件分支 Flow 已創建: {conditional_path}")
    print(f"✓ 路由節點已創建: {route_path}")
    print()


# ============================================
# 主函數
# ============================================
def main():
    """
    運行所有範例
    """
    print("\n")
    print("=" * 50)
    print("PromptFlow Flow 創建 - 範例演示")
    print("=" * 50)
    print("\n")

    example_1_flow_structure()
    example_2_create_simple_flow()
    example_3_create_node_implementation()
    example_4_complex_flow()
    example_5_flow_metadata()
    example_6_node_variants()
    example_7_programmatic_flow_creation()
    example_8_conditional_flow()

    print("=" * 50)
    print("所有範例演示完成！")
    print("=" * 50)
    print("\n創建的 Flow 目錄:")
    print("- simple_flow/")
    print("- rag_flow/")
    print("- customer_support_flow/")
    print("- ab_test_flow/")
    print("- sentiment_flow/")
    print("- conditional_flow/")
    print("\n下一步:")
    print("1. 查看 03_Prompt模板.py 學習提示詞管理")
    print("2. 實現節點的具體邏輯")
    print("3. 使用 pf test 測試 Flow")
    print()


if __name__ == "__main__":
    main()

"""
Flowise Agent 配置範例
====================

本範例展示如何在 Flowise 中配置和使用 Agent。

Agent 類型：
1. OpenAI Functions Agent
2. ReAct Agent
3. Conversational Agent
4. Plan and Execute Agent

安裝依賴：
pip install requests
"""

import os
import json
import requests
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

# ============================================================
# 配置
# ============================================================

FLOWISE_API_URL = os.getenv("FLOWISE_API_URL", "http://localhost:3000")
FLOWISE_API_KEY = os.getenv("FLOWISE_API_KEY", "")


# ============================================================
# Agent 節點配置
# ============================================================

OPENAI_FUNCTIONS_AGENT = '''
{
    "nodes": [
        {
            "id": "chatOpenAI_0",
            "type": "ChatOpenAI",
            "data": {
                "label": "ChatOpenAI",
                "name": "chatOpenAI",
                "inputs": {
                    "modelName": "gpt-4",
                    "temperature": 0
                }
            }
        },
        {
            "id": "calculator_0",
            "type": "Calculator",
            "data": {
                "label": "Calculator",
                "name": "calculator"
            }
        },
        {
            "id": "searchAPI_0",
            "type": "SearchAPI",
            "data": {
                "label": "Search API",
                "name": "searchAPI"
            }
        },
        {
            "id": "openAIFunctionAgent_0",
            "type": "OpenAIFunctionAgent",
            "data": {
                "label": "OpenAI Function Agent",
                "name": "openAIFunctionAgent",
                "inputs": {
                    "systemMessage": "你是一個有幫助的助手，可以使用工具來完成任務。"
                }
            }
        }
    ],
    "edges": [
        {
            "source": "chatOpenAI_0",
            "target": "openAIFunctionAgent_0",
            "targetHandle": "model"
        },
        {
            "source": "calculator_0",
            "target": "openAIFunctionAgent_0",
            "targetHandle": "tools"
        },
        {
            "source": "searchAPI_0",
            "target": "openAIFunctionAgent_0",
            "targetHandle": "tools"
        }
    ]
}
'''

REACT_AGENT = '''
{
    "nodes": [
        {
            "id": "chatOpenAI_0",
            "type": "ChatOpenAI",
            "data": {
                "label": "ChatOpenAI",
                "name": "chatOpenAI",
                "inputs": {
                    "modelName": "gpt-4",
                    "temperature": 0
                }
            }
        },
        {
            "id": "reactAgent_0",
            "type": "ReactAgent",
            "data": {
                "label": "ReAct Agent",
                "name": "reactAgent",
                "inputs": {
                    "maxIterations": 10,
                    "systemMessage": "你是一個擅長推理的助手。使用思考-行動-觀察的模式來解決問題。"
                }
            }
        }
    ],
    "edges": [
        {
            "source": "chatOpenAI_0",
            "target": "reactAgent_0",
            "targetHandle": "model"
        }
    ]
}
'''

CONVERSATIONAL_AGENT = '''
{
    "nodes": [
        {
            "id": "chatOpenAI_0",
            "type": "ChatOpenAI",
            "data": {
                "label": "ChatOpenAI",
                "name": "chatOpenAI",
                "inputs": {
                    "modelName": "gpt-4",
                    "temperature": 0.7
                }
            }
        },
        {
            "id": "bufferMemory_0",
            "type": "BufferMemory",
            "data": {
                "label": "Buffer Memory",
                "name": "bufferMemory",
                "inputs": {
                    "memoryKey": "chat_history",
                    "inputKey": "input",
                    "outputKey": "output"
                }
            }
        },
        {
            "id": "conversationalAgent_0",
            "type": "ConversationalAgent",
            "data": {
                "label": "Conversational Agent",
                "name": "conversationalAgent",
                "inputs": {
                    "systemMessage": "你是一個友好的對話助手。"
                }
            }
        }
    ],
    "edges": [
        {
            "source": "chatOpenAI_0",
            "target": "conversationalAgent_0",
            "targetHandle": "model"
        },
        {
            "source": "bufferMemory_0",
            "target": "conversationalAgent_0",
            "targetHandle": "memory"
        }
    ]
}
'''

PLAN_EXECUTE_AGENT = '''
{
    "nodes": [
        {
            "id": "chatOpenAI_0",
            "type": "ChatOpenAI",
            "data": {
                "label": "ChatOpenAI (Planner)",
                "name": "chatOpenAI",
                "inputs": {
                    "modelName": "gpt-4",
                    "temperature": 0
                }
            }
        },
        {
            "id": "chatOpenAI_1",
            "type": "ChatOpenAI",
            "data": {
                "label": "ChatOpenAI (Executor)",
                "name": "chatOpenAI",
                "inputs": {
                    "modelName": "gpt-4",
                    "temperature": 0
                }
            }
        },
        {
            "id": "planAndExecuteAgent_0",
            "type": "PlanAndExecuteAgent",
            "data": {
                "label": "Plan and Execute Agent",
                "name": "planAndExecuteAgent",
                "inputs": {
                    "systemMessage": "你是一個善於規劃和執行的助手。先制定計劃，然後逐步執行。"
                }
            }
        }
    ],
    "edges": [
        {
            "source": "chatOpenAI_0",
            "target": "planAndExecuteAgent_0",
            "targetHandle": "planner"
        },
        {
            "source": "chatOpenAI_1",
            "target": "planAndExecuteAgent_0",
            "targetHandle": "executor"
        }
    ]
}
'''


# ============================================================
# Agent 配置類
# ============================================================

@dataclass
class AgentConfig:
    """Agent 配置"""
    type: str  # openai_functions, react, conversational, plan_execute
    model: str = "gpt-4"
    temperature: float = 0
    max_iterations: int = 10
    system_message: str = ""
    tools: List[str] = None

    def __post_init__(self):
        if self.tools is None:
            self.tools = []


class AgentBuilder:
    """
    Agent 構建器

    用於構建 Flowise Agent 配置
    """

    def __init__(self):
        self.nodes = []
        self.edges = []

    def add_model(
        self,
        model_name: str = "gpt-4",
        temperature: float = 0,
        node_id: str = "chatOpenAI_0"
    ):
        """添加模型節點"""
        self.nodes.append({
            "id": node_id,
            "type": "ChatOpenAI",
            "data": {
                "label": "ChatOpenAI",
                "name": "chatOpenAI",
                "inputs": {
                    "modelName": model_name,
                    "temperature": temperature
                }
            }
        })
        return node_id

    def add_tool(
        self,
        tool_type: str,
        tool_name: str,
        node_id: str
    ):
        """添加工具節點"""
        self.nodes.append({
            "id": node_id,
            "type": tool_type,
            "data": {
                "label": tool_name,
                "name": tool_name.lower().replace(" ", "_")
            }
        })
        return node_id

    def add_memory(
        self,
        memory_type: str = "BufferMemory",
        node_id: str = "memory_0"
    ):
        """添加記憶節點"""
        self.nodes.append({
            "id": node_id,
            "type": memory_type,
            "data": {
                "label": memory_type,
                "name": memory_type.lower(),
                "inputs": {
                    "memoryKey": "chat_history"
                }
            }
        })
        return node_id

    def add_agent(
        self,
        agent_type: str,
        system_message: str = "",
        node_id: str = "agent_0"
    ):
        """添加 Agent 節點"""
        self.nodes.append({
            "id": node_id,
            "type": agent_type,
            "data": {
                "label": agent_type,
                "name": agent_type.lower(),
                "inputs": {
                    "systemMessage": system_message
                }
            }
        })
        return node_id

    def connect(
        self,
        source_id: str,
        target_id: str,
        target_handle: str = None
    ):
        """連接節點"""
        edge = {
            "source": source_id,
            "target": target_id
        }
        if target_handle:
            edge["targetHandle"] = target_handle
        self.edges.append(edge)

    def build(self) -> Dict[str, Any]:
        """構建配置"""
        return {
            "nodes": self.nodes,
            "edges": self.edges
        }


# ============================================================
# 使用範例
# ============================================================

def example_openai_functions_agent():
    """
    範例 1: OpenAI Functions Agent

    展示 OpenAI Function Calling Agent 配置
    """
    print("=" * 50)
    print("範例 1: OpenAI Functions Agent")
    print("=" * 50)

    print("OpenAI Functions Agent 配置:")
    print(OPENAI_FUNCTIONS_AGENT[:800] + "...")

    print("\n特點:")
    print("  - 使用 OpenAI Function Calling")
    print("  - 自動選擇和調用工具")
    print("  - 適合結構化任務")


def example_react_agent():
    """
    範例 2: ReAct Agent

    展示 ReAct（Reasoning + Acting）Agent 配置
    """
    print("\n" + "=" * 50)
    print("範例 2: ReAct Agent")
    print("=" * 50)

    print("ReAct Agent 配置:")
    print(REACT_AGENT)

    print("\n特點:")
    print("  - 思考-行動-觀察循環")
    print("  - 明確的推理過程")
    print("  - 適合複雜推理任務")


def example_conversational_agent():
    """
    範例 3: Conversational Agent

    展示對話式 Agent 配置
    """
    print("\n" + "=" * 50)
    print("範例 3: Conversational Agent")
    print("=" * 50)

    print("Conversational Agent 配置:")
    print(CONVERSATIONAL_AGENT)

    print("\n特點:")
    print("  - 支持多輪對話")
    print("  - 記憶對話歷史")
    print("  - 適合聊天場景")


def example_plan_execute_agent():
    """
    範例 4: Plan and Execute Agent

    展示計劃執行 Agent 配置
    """
    print("\n" + "=" * 50)
    print("範例 4: Plan and Execute Agent")
    print("=" * 50)

    print("Plan and Execute Agent 配置:")
    print(PLAN_EXECUTE_AGENT)

    print("\n特點:")
    print("  - 先規劃後執行")
    print("  - 分離規劃和執行模型")
    print("  - 適合複雜多步任務")


def example_agent_builder():
    """
    範例 5: Agent 構建器

    展示如何使用構建器創建 Agent
    """
    print("\n" + "=" * 50)
    print("範例 5: Agent 構建器")
    print("=" * 50)

    builder = AgentBuilder()

    # 添加模型
    model_id = builder.add_model("gpt-4", temperature=0)

    # 添加工具
    calc_id = builder.add_tool("Calculator", "Calculator", "calc_0")
    search_id = builder.add_tool("SearchAPI", "Search", "search_0")

    # 添加記憶
    memory_id = builder.add_memory("BufferMemory")

    # 添加 Agent
    agent_id = builder.add_agent(
        "OpenAIFunctionAgent",
        system_message="你是一個智能助手"
    )

    # 連接節點
    builder.connect(model_id, agent_id, "model")
    builder.connect(calc_id, agent_id, "tools")
    builder.connect(search_id, agent_id, "tools")
    builder.connect(memory_id, agent_id, "memory")

    # 構建配置
    config = builder.build()

    print("構建的 Agent 配置:")
    print(json.dumps(config, indent=2, ensure_ascii=False))


def example_multi_agent():
    """
    範例 6: 多 Agent 系統

    展示如何配置多個 Agent 協作
    """
    print("\n" + "=" * 50)
    print("範例 6: 多 Agent 系統")
    print("=" * 50)

    multi_agent_config = """
{
    "nodes": [
        {
            "id": "supervisor_0",
            "type": "SupervisorAgent",
            "data": {
                "label": "Supervisor",
                "inputs": {
                    "systemMessage": "你是一個協調者，負責分配任務給其他助手。"
                }
            }
        },
        {
            "id": "researcher_0",
            "type": "OpenAIFunctionAgent",
            "data": {
                "label": "Researcher",
                "inputs": {
                    "systemMessage": "你是一個研究員，負責搜索和收集信息。"
                }
            }
        },
        {
            "id": "writer_0",
            "type": "OpenAIFunctionAgent",
            "data": {
                "label": "Writer",
                "inputs": {
                    "systemMessage": "你是一個作家，負責撰寫和編輯內容。"
                }
            }
        },
        {
            "id": "critic_0",
            "type": "OpenAIFunctionAgent",
            "data": {
                "label": "Critic",
                "inputs": {
                    "systemMessage": "你是一個評論者，負責審核和改進內容。"
                }
            }
        }
    ],
    "edges": [
        {
            "source": "supervisor_0",
            "target": "researcher_0"
        },
        {
            "source": "supervisor_0",
            "target": "writer_0"
        },
        {
            "source": "supervisor_0",
            "target": "critic_0"
        }
    ]
}
"""

    print("多 Agent 系統配置:")
    print(multi_agent_config)


def example_agent_with_rag():
    """
    範例 7: Agent + RAG

    展示如何將 Agent 與 RAG 結合
    """
    print("\n" + "=" * 50)
    print("範例 7: Agent + RAG")
    print("=" * 50)

    agent_rag_config = """
{
    "nodes": [
        {
            "id": "chatOpenAI_0",
            "type": "ChatOpenAI",
            "data": {
                "inputs": {
                    "modelName": "gpt-4"
                }
            }
        },
        {
            "id": "openAIEmbeddings_0",
            "type": "OpenAIEmbeddings"
        },
        {
            "id": "pinecone_0",
            "type": "Pinecone",
            "data": {
                "inputs": {
                    "index": "knowledge-base"
                }
            }
        },
        {
            "id": "retrieverTool_0",
            "type": "RetrieverTool",
            "data": {
                "label": "Knowledge Base Search",
                "inputs": {
                    "name": "knowledge_search",
                    "description": "搜索知識庫獲取相關信息"
                }
            }
        },
        {
            "id": "openAIFunctionAgent_0",
            "type": "OpenAIFunctionAgent",
            "data": {
                "inputs": {
                    "systemMessage": "你是一個知識助手，使用知識庫回答問題。"
                }
            }
        }
    ],
    "edges": [
        {
            "source": "openAIEmbeddings_0",
            "target": "pinecone_0"
        },
        {
            "source": "pinecone_0",
            "target": "retrieverTool_0"
        },
        {
            "source": "chatOpenAI_0",
            "target": "openAIFunctionAgent_0",
            "targetHandle": "model"
        },
        {
            "source": "retrieverTool_0",
            "target": "openAIFunctionAgent_0",
            "targetHandle": "tools"
        }
    ]
}
"""

    print("Agent + RAG 配置:")
    print(agent_rag_config)


# ============================================================
# 主程序
# ============================================================

if __name__ == "__main__":
    print("Flowise Agent 配置範例")
    print()

    example_openai_functions_agent()
    example_react_agent()
    example_conversational_agent()
    example_plan_execute_agent()
    example_agent_builder()
    example_multi_agent()
    example_agent_with_rag()

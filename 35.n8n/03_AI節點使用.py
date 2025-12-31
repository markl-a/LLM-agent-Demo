"""
n8n AI 節點使用
===============

本範例展示如何在 n8n 中使用 AI 相關節點，包括：
- AI Agent 節點
- LLM Chain 節點
- Chat Model 節點
- Embeddings 節點
- Memory 節點

安裝依賴:
pip install requests python-dotenv openai

作者: n8n Demo
日期: 2025-12-31
"""

import os
import requests
import json
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

# 加載環境變量
load_dotenv()


class N8NAIWorkflowBuilder:
    """
    n8n AI 工作流構建器

    創建包含 AI 功能的工作流
    """

    def __init__(self, base_url: str = "http://localhost:5678", api_key: Optional[str] = None):
        """初始化 AI 工作流構建器"""
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key or os.getenv("N8N_API_KEY")

        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({
                "X-N8N-API-KEY": self.api_key,
                "Content-Type": "application/json"
            })

        print(f"✓ n8n AI 工作流構建器已初始化")

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """發送 HTTP 請求"""
        url = f"{self.base_url}{endpoint}"

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                timeout=30
            )
            response.raise_for_status()

            if response.status_code == 204 or not response.content:
                return {}

            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"✗ API 請求錯誤: {str(e)}")
            raise

    def example_1_create_openai_chat_workflow(
        self,
        workflow_name: str,
        openai_api_key: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        示例 1: 創建 OpenAI Chat 工作流

        使用 OpenAI Chat Model 節點進行對話

        參數:
            workflow_name: 工作流名稱
            openai_api_key: OpenAI API 密鑰

        返回:
            創建的工作流對象
        """
        print("\n" + "="*60)
        print("示例 1: 創建 OpenAI Chat 工作流")
        print("="*60)

        api_key = openai_api_key or os.getenv("OPENAI_API_KEY")

        try:
            workflow_data = {
                "name": workflow_name,
                "active": True,
                "nodes": [
                    {
                        "parameters": {
                            "httpMethod": "POST",
                            "path": "ai-chat",
                            "responseMode": "lastNode"
                        },
                        "name": "Webhook",
                        "type": "n8n-nodes-base.webhook",
                        "typeVersion": 1,
                        "position": [250, 300]
                    },
                    {
                        "parameters": {
                            "model": "gpt-4",
                            "options": {
                                "temperature": 0.7,
                                "maxTokens": 500
                            },
                            "messages": {
                                "messageValues": [
                                    {
                                        "role": "system",
                                        "message": "你是一個有幫助的 AI 助手。"
                                    },
                                    {
                                        "role": "user",
                                        "message": "={{ $json.question }}"
                                    }
                                ]
                            }
                        },
                        "name": "OpenAI Chat Model",
                        "type": "@n8n/n8n-nodes-langchain.lmChatOpenAi",
                        "typeVersion": 1,
                        "position": [450, 300],
                        "credentials": {
                            "openAiApi": {
                                "id": "1",
                                "name": "OpenAI account"
                            }
                        }
                    },
                    {
                        "parameters": {
                            "values": {
                                "string": [
                                    {
                                        "name": "response",
                                        "value": "={{ $json.response }}"
                                    }
                                ]
                            }
                        },
                        "name": "Format Response",
                        "type": "n8n-nodes-base.set",
                        "typeVersion": 1,
                        "position": [650, 300]
                    }
                ],
                "connections": {
                    "Webhook": {
                        "main": [
                            [
                                {
                                    "node": "OpenAI Chat Model",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    },
                    "OpenAI Chat Model": {
                        "main": [
                            [
                                {
                                    "node": "Format Response",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    }
                },
                "settings": {}
            }

            print(f"\n創建 OpenAI Chat 工作流: {workflow_name}")

            workflow = self._make_request("POST", "/api/v1/workflows", data=workflow_data)

            print(f"\n✓ 工作流創建成功")
            print(f"  ID: {workflow.get('id')}")
            print(f"  Webhook URL: {self.base_url}/webhook/ai-chat")
            print(f"  測試: curl -X POST {self.base_url}/webhook/ai-chat -d '{{\"question\":\"什麼是人工智能？\"}}'")

            return workflow

        except Exception as e:
            print(f"\n✗ 創建工作流失敗: {str(e)}")
            return None

    def example_2_create_ai_agent_workflow(
        self,
        workflow_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        示例 2: 創建 AI Agent 工作流

        使用 AI Agent 節點構建智能代理

        參數:
            workflow_name: 工作流名稱

        返回:
            創建的工作流對象
        """
        print("\n" + "="*60)
        print("示例 2: 創建 AI Agent 工作流")
        print("="*60)

        try:
            workflow_data = {
                "name": workflow_name,
                "active": True,
                "nodes": [
                    {
                        "parameters": {
                            "httpMethod": "POST",
                            "path": "ai-agent",
                            "responseMode": "lastNode"
                        },
                        "name": "Webhook",
                        "type": "n8n-nodes-base.webhook",
                        "typeVersion": 1,
                        "position": [250, 300]
                    },
                    {
                        "parameters": {
                            "agent": "conversationalAgent",
                            "promptType": "define",
                            "text": "你是一個智能助手，可以回答問題並執行任務。用戶問題：{{ $json.question }}",
                            "options": {
                                "systemMessage": "你是一個專業的 AI 助手，提供準確和有幫助的回答。"
                            }
                        },
                        "name": "AI Agent",
                        "type": "@n8n/n8n-nodes-langchain.agent",
                        "typeVersion": 1,
                        "position": [450, 300]
                    },
                    {
                        "parameters": {
                            "model": "gpt-4",
                            "options": {
                                "temperature": 0.7
                            }
                        },
                        "name": "OpenAI Chat Model",
                        "type": "@n8n/n8n-nodes-langchain.lmChatOpenAi",
                        "typeVersion": 1,
                        "position": [450, 450]
                    }
                ],
                "connections": {
                    "Webhook": {
                        "main": [
                            [
                                {
                                    "node": "AI Agent",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    },
                    "OpenAI Chat Model": {
                        "ai_languageModel": [
                            [
                                {
                                    "node": "AI Agent",
                                    "type": "ai_languageModel",
                                    "index": 0
                                }
                            ]
                        ]
                    }
                },
                "settings": {}
            }

            print(f"\n創建 AI Agent 工作流: {workflow_name}")

            workflow = self._make_request("POST", "/api/v1/workflows", data=workflow_data)

            print(f"\n✓ AI Agent 工作流創建成功")
            print(f"  ID: {workflow.get('id')}")
            print(f"  Webhook URL: {self.base_url}/webhook/ai-agent")

            return workflow

        except Exception as e:
            print(f"\n✗ 創建工作流失敗: {str(e)}")
            return None

    def example_3_create_rag_workflow(
        self,
        workflow_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        示例 3: 創建 RAG (檢索增強生成) 工作流

        使用向量存儲和嵌入進行文檔問答

        參數:
            workflow_name: 工作流名稱

        返回:
            創建的工作流對象
        """
        print("\n" + "="*60)
        print("示例 3: 創建 RAG 工作流")
        print("="*60)

        try:
            workflow_data = {
                "name": workflow_name,
                "active": True,
                "nodes": [
                    {
                        "parameters": {
                            "httpMethod": "POST",
                            "path": "rag-query",
                            "responseMode": "lastNode"
                        },
                        "name": "Webhook",
                        "type": "n8n-nodes-base.webhook",
                        "typeVersion": 1,
                        "position": [250, 300]
                    },
                    {
                        "parameters": {
                            "model": "gpt-4",
                            "options": {
                                "temperature": 0.3
                            }
                        },
                        "name": "OpenAI Chat Model",
                        "type": "@n8n/n8n-nodes-langchain.lmChatOpenAi",
                        "typeVersion": 1,
                        "position": [650, 450]
                    },
                    {
                        "parameters": {},
                        "name": "OpenAI Embeddings",
                        "type": "@n8n/n8n-nodes-langchain.embeddingsOpenAi",
                        "typeVersion": 1,
                        "position": [650, 600]
                    },
                    {
                        "parameters": {
                            "mode": "load",
                            "qdrantCollection": "documents"
                        },
                        "name": "Qdrant Vector Store",
                        "type": "@n8n/n8n-nodes-langchain.vectorStoreQdrant",
                        "typeVersion": 1,
                        "position": [450, 450]
                    },
                    {
                        "parameters": {
                            "promptType": "define",
                            "text": "=基於以下上下文回答問題:\n\n{{ $json.context }}\n\n問題: {{ $json.question }}"
                        },
                        "name": "Question Answering Chain",
                        "type": "@n8n/n8n-nodes-langchain.chainRetrievalQa",
                        "typeVersion": 1,
                        "position": [650, 300]
                    }
                ],
                "connections": {
                    "Webhook": {
                        "main": [
                            [
                                {
                                    "node": "Question Answering Chain",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    },
                    "OpenAI Chat Model": {
                        "ai_languageModel": [
                            [
                                {
                                    "node": "Question Answering Chain",
                                    "type": "ai_languageModel",
                                    "index": 0
                                }
                            ]
                        ]
                    },
                    "OpenAI Embeddings": {
                        "ai_embedding": [
                            [
                                {
                                    "node": "Qdrant Vector Store",
                                    "type": "ai_embedding",
                                    "index": 0
                                }
                            ]
                        ]
                    },
                    "Qdrant Vector Store": {
                        "ai_vectorStore": [
                            [
                                {
                                    "node": "Question Answering Chain",
                                    "type": "ai_vectorStore",
                                    "index": 0
                                }
                            ]
                        ]
                    }
                },
                "settings": {}
            }

            print(f"\n創建 RAG 工作流: {workflow_name}")

            workflow = self._make_request("POST", "/api/v1/workflows", data=workflow_data)

            print(f"\n✓ RAG 工作流創建成功")
            print(f"  ID: {workflow.get('id')}")
            print(f"  功能: 基於向量存儲的文檔問答")

            return workflow

        except Exception as e:
            print(f"\n✗ 創建工作流失敗: {str(e)}")
            return None

    def example_4_create_conversation_memory_workflow(
        self,
        workflow_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        示例 4: 創建帶記憶的對話工作流

        使用 Memory 節點保持對話上下文

        參數:
            workflow_name: 工作流名稱

        返回:
            創建的工作流對象
        """
        print("\n" + "="*60)
        print("示例 4: 創建帶記憶的對話工作流")
        print("="*60)

        try:
            workflow_data = {
                "name": workflow_name,
                "active": True,
                "nodes": [
                    {
                        "parameters": {
                            "httpMethod": "POST",
                            "path": "chat-with-memory",
                            "responseMode": "lastNode"
                        },
                        "name": "Webhook",
                        "type": "n8n-nodes-base.webhook",
                        "typeVersion": 1,
                        "position": [250, 300]
                    },
                    {
                        "parameters": {
                            "agent": "conversationalAgent",
                            "text": "={{ $json.message }}"
                        },
                        "name": "Conversational Agent",
                        "type": "@n8n/n8n-nodes-langchain.agent",
                        "typeVersion": 1,
                        "position": [450, 300]
                    },
                    {
                        "parameters": {
                            "model": "gpt-3.5-turbo",
                            "options": {
                                "temperature": 0.7,
                                "maxTokens": 500
                            }
                        },
                        "name": "OpenAI Chat Model",
                        "type": "@n8n/n8n-nodes-langchain.lmChatOpenAi",
                        "typeVersion": 1,
                        "position": [450, 450]
                    },
                    {
                        "parameters": {
                            "sessionIdType": "customKey",
                            "sessionKey": "={{ $json.sessionId }}",
                            "contextWindowLength": 10
                        },
                        "name": "Window Buffer Memory",
                        "type": "@n8n/n8n-nodes-langchain.memoryBufferWindow",
                        "typeVersion": 1,
                        "position": [450, 600]
                    }
                ],
                "connections": {
                    "Webhook": {
                        "main": [
                            [
                                {
                                    "node": "Conversational Agent",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    },
                    "OpenAI Chat Model": {
                        "ai_languageModel": [
                            [
                                {
                                    "node": "Conversational Agent",
                                    "type": "ai_languageModel",
                                    "index": 0
                                }
                            ]
                        ]
                    },
                    "Window Buffer Memory": {
                        "ai_memory": [
                            [
                                {
                                    "node": "Conversational Agent",
                                    "type": "ai_memory",
                                    "index": 0
                                }
                            ]
                        ]
                    }
                },
                "settings": {}
            }

            print(f"\n創建帶記憶的對話工作流: {workflow_name}")

            workflow = self._make_request("POST", "/api/v1/workflows", data=workflow_data)

            print(f"\n✓ 對話記憶工作流創建成功")
            print(f"  ID: {workflow.get('id')}")
            print(f"  功能: 保持對話上下文的聊天機器人")
            print(f"  測試: curl -X POST {self.base_url}/webhook/chat-with-memory")
            print(f"        -d '{{\"message\":\"你好\",\"sessionId\":\"user123\"}}'")

            return workflow

        except Exception as e:
            print(f"\n✗ 創建工作流失敗: {str(e)}")
            return None

    def example_5_execute_ai_workflow(
        self,
        workflow_id: str,
        question: str
    ) -> Optional[Dict[str, Any]]:
        """
        示例 5: 執行 AI 工作流

        參數:
            workflow_id: 工作流 ID
            question: 要提問的問題

        返回:
            執行結果
        """
        print("\n" + "="*60)
        print("示例 5: 執行 AI 工作流")
        print("="*60)

        try:
            execution_data = {
                "question": question
            }

            print(f"\n執行工作流 ID: {workflow_id}")
            print(f"問題: {question}")

            result = self._make_request(
                "POST",
                f"/api/v1/workflows/{workflow_id}/execute",
                data=execution_data
            )

            print(f"\n✓ AI 工作流執行成功")
            print(f"  執行 ID: {result.get('id')}")

            # 顯示 AI 響應
            if result.get('data'):
                print(f"\n  AI 響應:")
                print(f"  {json.dumps(result.get('data'), indent=2, ensure_ascii=False)}")

            return result

        except Exception as e:
            print(f"\n✗ 執行失敗: {str(e)}")
            return None


def main():
    """
    主函數：演示所有 AI 節點使用示例
    """
    print("\n" + "="*60)
    print("n8n AI 節點使用示例")
    print("="*60)

    # 配置參數
    BASE_URL = os.getenv("N8N_API_URL", "http://localhost:5678")
    N8N_API_KEY = os.getenv("N8N_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # 檢查 OpenAI API Key
    if not OPENAI_API_KEY:
        print("\n警告: 未設置 OPENAI_API_KEY 環境變量")
        print("某些示例可能無法正常運行")

    # 初始化構建器
    builder = N8NAIWorkflowBuilder(base_url=BASE_URL, api_key=N8N_API_KEY)

    # 示例 1: OpenAI Chat 工作流
    chat_workflow = builder.example_1_create_openai_chat_workflow(
        "OpenAI Chat Workflow",
        openai_api_key=OPENAI_API_KEY
    )

    # 示例 2: AI Agent 工作流
    agent_workflow = builder.example_2_create_ai_agent_workflow(
        "AI Agent Workflow"
    )

    # 示例 3: RAG 工作流
    rag_workflow = builder.example_3_create_rag_workflow(
        "RAG Question Answering"
    )

    # 示例 4: 對話記憶工作流
    memory_workflow = builder.example_4_create_conversation_memory_workflow(
        "Conversation with Memory"
    )

    # 示例 5: 執行 AI 工作流（如果創建成功）
    if chat_workflow:
        builder.example_5_execute_ai_workflow(
            workflow_id=chat_workflow['id'],
            question="什麼是機器學習？"
        )

    print("\n" + "="*60)
    print("所有 AI 示例運行完成！")
    print("="*60)


if __name__ == "__main__":
    main()

    print("\n" + "-"*60)
    print("n8n AI 節點最佳實踐:")
    print("-"*60)
    print("""
    1. 模型選擇
       - GPT-4: 複雜任務，高質量輸出
       - GPT-3.5: 快速響應，成本較低
       - Claude: 長文本處理
       - 本地模型 (Ollama): 隱私保護

    2. Prompt 設計
       - 清晰的系統消息
       - 結構化的用戶輸入
       - 使用示例 (Few-shot Learning)
       - 限制輸出格式

    3. Memory 管理
       - 選擇合適的記憶類型
       - 控制上下文窗口大小
       - 定期清理過期記憶
       - 使用 Session ID 隔離用戶

    4. RAG 優化
       - 優質的文檔分割
       - 適當的 Chunk 大小
       - 相關性閾值設置
       - 混合檢索策略

    5. 成本控制
       - 設置 Token 限制
       - 使用緩存減少重複調用
       - 選擇性使用高級模型
       - 監控 API 使用量
    """)

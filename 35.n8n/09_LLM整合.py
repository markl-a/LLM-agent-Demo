"""
n8n LLM 整合
============

本範例展示如何在 n8n 中整合各種 LLM 模型，包括：
- OpenAI GPT 整合
- Anthropic Claude 整合
- Google Gemini 整合
- 本地模型（Ollama）整合
- 多模型比較

安裝依賴:
pip install requests python-dotenv openai anthropic

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


class N8NLLMIntegration:
    """
    n8n LLM 整合工具

    創建整合各種 LLM 的工作流
    """

    def __init__(self, base_url: str = "http://localhost:5678", api_key: Optional[str] = None):
        """初始化 LLM 整合工具"""
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key or os.getenv("N8N_API_KEY")

        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({
                "X-N8N-API-KEY": self.api_key,
                "Content-Type": "application/json"
            })

        print(f"✓ n8n LLM 整合工具已初始化")

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

    def example_1_create_openai_workflow(
        self,
        workflow_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        示例 1: 創建 OpenAI GPT 整合工作流

        使用 OpenAI API 進行文本生成

        參數:
            workflow_name: 工作流名稱

        返回:
            創建的工作流對象
        """
        print("\n" + "="*60)
        print("示例 1: 創建 OpenAI GPT 整合工作流")
        print("="*60)

        try:
            workflow_data = {
                "name": workflow_name,
                "active": True,
                "nodes": [
                    {
                        "parameters": {
                            "httpMethod": "POST",
                            "path": "openai-chat",
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
                                "maxTokens": 1000,
                                "topP": 1,
                                "frequencyPenalty": 0,
                                "presencePenalty": 0
                            },
                            "messages": {
                                "messageValues": [
                                    {
                                        "role": "system",
                                        "message": "你是一個專業的 AI 助手，提供準確、有幫助的回答。"
                                    },
                                    {
                                        "role": "user",
                                        "message": "={{ $json.prompt }}"
                                    }
                                ]
                            }
                        },
                        "name": "OpenAI GPT-4",
                        "type": "@n8n/n8n-nodes-langchain.lmChatOpenAi",
                        "typeVersion": 1,
                        "position": [450, 300]
                    },
                    {
                        "parameters": {
                            "mode": "manual",
                            "duplicateItem": False,
                            "assignments": {
                                "assignments": [
                                    {
                                        "id": "1",
                                        "name": "model",
                                        "value": "gpt-4",
                                        "type": "string"
                                    },
                                    {
                                        "id": "2",
                                        "name": "response",
                                        "value": "={{ $json.response }}",
                                        "type": "string"
                                    },
                                    {
                                        "id": "3",
                                        "name": "timestamp",
                                        "value": "={{ new Date().toISOString() }}",
                                        "type": "string"
                                    }
                                ]
                            }
                        },
                        "name": "Format Response",
                        "type": "n8n-nodes-base.set",
                        "typeVersion": 3,
                        "position": [650, 300]
                    }
                ],
                "connections": {
                    "Webhook": {
                        "main": [
                            [
                                {
                                    "node": "OpenAI GPT-4",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    },
                    "OpenAI GPT-4": {
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

            print(f"\n創建 OpenAI 工作流: {workflow_name}")

            workflow = self._make_request("POST", "/api/v1/workflows", data=workflow_data)

            print(f"\n✓ 工作流創建成功")
            print(f"  ID: {workflow.get('id')}")
            print(f"  模型: GPT-4")
            print(f"  URL: {self.base_url}/webhook/openai-chat")

            return workflow

        except Exception as e:
            print(f"\n✗ 創建失敗: {str(e)}")
            return None

    def example_2_create_claude_workflow(
        self,
        workflow_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        示例 2: 創建 Anthropic Claude 整合工作流

        使用 Claude API 進行文本生成

        參數:
            workflow_name: 工作流名稱

        返回:
            創建的工作流對象
        """
        print("\n" + "="*60)
        print("示例 2: 創建 Anthropic Claude 整合工作流")
        print("="*60)

        try:
            workflow_data = {
                "name": workflow_name,
                "active": True,
                "nodes": [
                    {
                        "parameters": {
                            "httpMethod": "POST",
                            "path": "claude-chat",
                            "responseMode": "lastNode"
                        },
                        "name": "Webhook",
                        "type": "n8n-nodes-base.webhook",
                        "typeVersion": 1,
                        "position": [250, 300]
                    },
                    {
                        "parameters": {
                            "model": "claude-3-opus-20240229",
                            "options": {
                                "temperature": 0.7,
                                "maxTokens": 1000
                            },
                            "messages": {
                                "messageValues": [
                                    {
                                        "role": "user",
                                        "message": "={{ $json.prompt }}"
                                    }
                                ]
                            }
                        },
                        "name": "Claude 3 Opus",
                        "type": "@n8n/n8n-nodes-langchain.lmChatAnthropic",
                        "typeVersion": 1,
                        "position": [450, 300]
                    },
                    {
                        "parameters": {
                            "mode": "manual",
                            "duplicateItem": False,
                            "assignments": {
                                "assignments": [
                                    {
                                        "id": "1",
                                        "name": "model",
                                        "value": "claude-3-opus",
                                        "type": "string"
                                    },
                                    {
                                        "id": "2",
                                        "name": "response",
                                        "value": "={{ $json.response }}",
                                        "type": "string"
                                    }
                                ]
                            }
                        },
                        "name": "Format Response",
                        "type": "n8n-nodes-base.set",
                        "typeVersion": 3,
                        "position": [650, 300]
                    }
                ],
                "connections": {
                    "Webhook": {
                        "main": [
                            [
                                {
                                    "node": "Claude 3 Opus",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    },
                    "Claude 3 Opus": {
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

            print(f"\n創建 Claude 工作流: {workflow_name}")

            workflow = self._make_request("POST", "/api/v1/workflows", data=workflow_data)

            print(f"\n✓ 工作流創建成功")
            print(f"  ID: {workflow.get('id')}")
            print(f"  模型: Claude 3 Opus")

            return workflow

        except Exception as e:
            print(f"\n✗ 創建失敗: {str(e)}")
            return None

    def example_3_create_multi_model_comparison_workflow(
        self,
        workflow_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        示例 3: 創建多模型比較工作流

        同時調用多個 LLM 並比較結果

        參數:
            workflow_name: 工作流名稱

        返回:
            創建的工作流對象
        """
        print("\n" + "="*60)
        print("示例 3: 創建多模型比較工作流")
        print("="*60)

        comparison_code = """
// 比較多個 LLM 的響應
const items = $input.all();

const comparison = {
  prompt: items[0]?.json?.prompt || 'Unknown',
  models: items.map(item => ({
    model: item.json.model,
    response: item.json.response,
    responseLength: item.json.response?.length || 0,
    timestamp: item.json.timestamp
  })),
  comparisonTime: new Date().toISOString(),
  totalModels: items.length
};

return { json: comparison };
"""

        try:
            workflow_data = {
                "name": workflow_name,
                "active": True,
                "nodes": [
                    {
                        "parameters": {
                            "httpMethod": "POST",
                            "path": "model-comparison",
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
                            "messages": {
                                "messageValues": [
                                    {
                                        "role": "user",
                                        "message": "={{ $json.prompt }}"
                                    }
                                ]
                            }
                        },
                        "name": "GPT-4",
                        "type": "@n8n/n8n-nodes-langchain.lmChatOpenAi",
                        "typeVersion": 1,
                        "position": [450, 200]
                    },
                    {
                        "parameters": {
                            "model": "gpt-3.5-turbo",
                            "messages": {
                                "messageValues": [
                                    {
                                        "role": "user",
                                        "message": "={{ $json.prompt }}"
                                    }
                                ]
                            }
                        },
                        "name": "GPT-3.5",
                        "type": "@n8n/n8n-nodes-langchain.lmChatOpenAi",
                        "typeVersion": 1,
                        "position": [450, 350]
                    },
                    {
                        "parameters": {
                            "mode": "combine",
                            "combinationMode": "mergeByPosition"
                        },
                        "name": "Merge Responses",
                        "type": "n8n-nodes-base.merge",
                        "typeVersion": 2,
                        "position": [650, 275]
                    },
                    {
                        "parameters": {
                            "language": "javaScript",
                            "jsCode": comparison_code
                        },
                        "name": "Compare Results",
                        "type": "n8n-nodes-base.code",
                        "typeVersion": 2,
                        "position": [850, 275]
                    }
                ],
                "connections": {
                    "Webhook": {
                        "main": [
                            [
                                {
                                    "node": "GPT-4",
                                    "type": "main",
                                    "index": 0
                                },
                                {
                                    "node": "GPT-3.5",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    },
                    "GPT-4": {
                        "main": [
                            [
                                {
                                    "node": "Merge Responses",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    },
                    "GPT-3.5": {
                        "main": [
                            [
                                {
                                    "node": "Merge Responses",
                                    "type": "main",
                                    "index": 1
                                }
                            ]
                        ]
                    },
                    "Merge Responses": {
                        "main": [
                            [
                                {
                                    "node": "Compare Results",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    }
                },
                "settings": {}
            }

            print(f"\n創建多模型比較工作流: {workflow_name}")

            workflow = self._make_request("POST", "/api/v1/workflows", data=workflow_data)

            print(f"\n✓ 工作流創建成功")
            print(f"  ID: {workflow.get('id')}")
            print(f"  功能: 同時調用 GPT-4 和 GPT-3.5 並比較結果")

            return workflow

        except Exception as e:
            print(f"\n✗ 創建失敗: {str(e)}")
            return None

    def example_4_create_ollama_workflow(
        self,
        workflow_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        示例 4: 創建本地 Ollama 模型工作流

        使用本地運行的開源模型

        參數:
            workflow_name: 工作流名稱

        返回:
            創建的工作流對象
        """
        print("\n" + "="*60)
        print("示例 4: 創建本地 Ollama 模型工作流")
        print("="*60)

        try:
            workflow_data = {
                "name": workflow_name,
                "active": True,
                "nodes": [
                    {
                        "parameters": {
                            "httpMethod": "POST",
                            "path": "ollama-chat",
                            "responseMode": "lastNode"
                        },
                        "name": "Webhook",
                        "type": "n8n-nodes-base.webhook",
                        "typeVersion": 1,
                        "position": [250, 300]
                    },
                    {
                        "parameters": {
                            "model": "llama2",
                            "options": {
                                "baseURL": "http://localhost:11434",
                                "temperature": 0.7
                            },
                            "messages": {
                                "messageValues": [
                                    {
                                        "role": "user",
                                        "message": "={{ $json.prompt }}"
                                    }
                                ]
                            }
                        },
                        "name": "Ollama Llama2",
                        "type": "@n8n/n8n-nodes-langchain.lmChatOllama",
                        "typeVersion": 1,
                        "position": [450, 300]
                    },
                    {
                        "parameters": {
                            "mode": "manual",
                            "duplicateItem": False,
                            "assignments": {
                                "assignments": [
                                    {
                                        "id": "1",
                                        "name": "model",
                                        "value": "ollama-llama2",
                                        "type": "string"
                                    },
                                    {
                                        "id": "2",
                                        "name": "response",
                                        "value": "={{ $json.response }}",
                                        "type": "string"
                                    },
                                    {
                                        "id": "3",
                                        "name": "isLocal",
                                        "value": True,
                                        "type": "boolean"
                                    }
                                ]
                            }
                        },
                        "name": "Format Response",
                        "type": "n8n-nodes-base.set",
                        "typeVersion": 3,
                        "position": [650, 300]
                    }
                ],
                "connections": {
                    "Webhook": {
                        "main": [
                            [
                                {
                                    "node": "Ollama Llama2",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    },
                    "Ollama Llama2": {
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

            print(f"\n創建 Ollama 工作流: {workflow_name}")

            workflow = self._make_request("POST", "/api/v1/workflows", data=workflow_data)

            print(f"\n✓ 工作流創建成功")
            print(f"  ID: {workflow.get('id')}")
            print(f"  模型: Llama2 (本地)")
            print(f"\n  注意:")
            print(f"  1. 需要先安裝 Ollama: https://ollama.ai/")
            print(f"  2. 運行: ollama pull llama2")
            print(f"  3. Ollama 默認運行在 http://localhost:11434")

            return workflow

        except Exception as e:
            print(f"\n✗ 創建失敗: {str(e)}")
            return None


def main():
    """
    主函數：演示所有 LLM 整合示例
    """
    print("\n" + "="*60)
    print("n8n LLM 整合示例")
    print("="*60)

    # 配置參數
    BASE_URL = os.getenv("N8N_API_URL", "http://localhost:5678")
    N8N_API_KEY = os.getenv("N8N_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

    # 檢查 API Keys
    if not OPENAI_API_KEY:
        print("\n警告: 未設置 OPENAI_API_KEY")
    if not ANTHROPIC_API_KEY:
        print("\n警告: 未設置 ANTHROPIC_API_KEY")

    # 初始化工具
    integrator = N8NLLMIntegration(base_url=BASE_URL, api_key=N8N_API_KEY)

    # 示例 1: OpenAI GPT
    integrator.example_1_create_openai_workflow(
        "LLM: OpenAI GPT-4"
    )

    # 示例 2: Claude
    integrator.example_2_create_claude_workflow(
        "LLM: Anthropic Claude"
    )

    # 示例 3: 多模型比較
    integrator.example_3_create_multi_model_comparison_workflow(
        "LLM: Model Comparison"
    )

    # 示例 4: Ollama 本地模型
    integrator.example_4_create_ollama_workflow(
        "LLM: Ollama Local Model"
    )

    print("\n" + "="*60)
    print("所有 LLM 整合示例創建完成！")
    print("="*60)


if __name__ == "__main__":
    main()

    print("\n" + "-"*60)
    print("LLM 整合最佳實踐:")
    print("-"*60)
    print("""
    1. 模型選擇
       - GPT-4: 複雜任務、高質量輸出
       - GPT-3.5: 快速響應、成本較低
       - Claude: 長文本處理、安全性
       - Gemini: 多模態、Google 生態
       - 本地模型: 隱私、離線使用

    2. 參數調優
       - Temperature: 控制隨機性
         * 0: 確定性輸出
         * 0.7: 平衡創造力
         * 1: 高度創造性
       - Max Tokens: 限制輸出長度
       - Top P: 核採樣參數
       - Frequency Penalty: 減少重複

    3. Prompt 工程
       - 清晰的系統消息
       - 結構化的用戶輸入
       - Few-shot 示例
       - 明確的輸出格式要求

    4. 成本控制
       - 設置 Token 限制
       - 使用緩存
       - 選擇性使用高級模型
       - 監控使用量

    5. 錯誤處理
       - API 限流處理
       - 超時重試
       - 降級策略
       - 錯誤日誌

    支援的 LLM:
    - OpenAI: GPT-4, GPT-3.5, GPT-4 Turbo
    - Anthropic: Claude 3 (Opus, Sonnet, Haiku)
    - Google: Gemini Pro, Gemini Ultra
    - Ollama: Llama2, Mistral, CodeLlama等
    - Azure OpenAI
    - Hugging Face
    """)

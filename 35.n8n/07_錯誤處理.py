"""
n8n 錯誤處理
============

本範例展示如何在 n8n 中處理錯誤，包括：
- Error Trigger 錯誤觸發器
- Try-Catch 錯誤捕獲
- 重試機制
- 錯誤通知
- 錯誤日誌記錄

安裝依賴:
pip install requests python-dotenv

作者: n8n Demo
日期: 2025-12-31
"""

import os
import requests
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# 加載環境變量
load_dotenv()


class N8NErrorHandler:
    """
    n8n 錯誤處理工具

    創建包含錯誤處理機制的工作流
    """

    def __init__(self, base_url: str = "http://localhost:5678", api_key: Optional[str] = None):
        """初始化錯誤處理工具"""
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key or os.getenv("N8N_API_KEY")

        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({
                "X-N8N-API-KEY": self.api_key,
                "Content-Type": "application/json"
            })

        print(f"✓ n8n 錯誤處理工具已初始化")

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

    def example_1_create_error_trigger_workflow(
        self,
        workflow_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        示例 1: 創建錯誤觸發器工作流

        使用 Error Trigger 捕獲其他工作流的錯誤

        參數:
            workflow_name: 工作流名稱

        返回:
            創建的工作流對象
        """
        print("\n" + "="*60)
        print("示例 1: 創建錯誤觸發器工作流")
        print("="*60)

        try:
            workflow_data = {
                "name": workflow_name,
                "active": True,
                "nodes": [
                    {
                        "parameters": {},
                        "name": "Error Trigger",
                        "type": "n8n-nodes-base.errorTrigger",
                        "typeVersion": 1,
                        "position": [250, 300]
                    },
                    {
                        "parameters": {
                            "language": "javaScript",
                            "jsCode": "// 處理錯誤信息\nconst error = $input.first().json;\n\nconst errorInfo = {\n  workflowId: error.workflow?.id || 'unknown',\n  workflowName: error.workflow?.name || 'unknown',\n  executionId: error.execution?.id || 'unknown',\n  errorMessage: error.error?.message || 'No error message',\n  errorStack: error.error?.stack || 'No stack trace',\n  nodeName: error.node?.name || 'unknown',\n  timestamp: new Date().toISOString(),\n  severity: 'ERROR'\n};\n\nreturn { json: errorInfo };"
                        },
                        "name": "Process Error",
                        "type": "n8n-nodes-base.code",
                        "typeVersion": 2,
                        "position": [450, 300]
                    },
                    {
                        "parameters": {
                            "functionCode": "// 記錄錯誤到控制台\nconsole.error('Workflow Error:', $json);\n\n// 返回錯誤信息\nreturn $input.all();"
                        },
                        "name": "Log Error",
                        "type": "n8n-nodes-base.function",
                        "typeVersion": 1,
                        "position": [650, 300]
                    },
                    {
                        "parameters": {
                            "conditions": {
                                "string": [
                                    {
                                        "value1": "={{ $json.severity }}",
                                        "operation": "equals",
                                        "value2": "ERROR"
                                    }
                                ]
                            }
                        },
                        "name": "IF Critical",
                        "type": "n8n-nodes-base.if",
                        "typeVersion": 1,
                        "position": [850, 300]
                    },
                    {
                        "parameters": {
                            "mode": "manual",
                            "duplicateItem": False,
                            "assignments": {
                                "assignments": [
                                    {
                                        "id": "1",
                                        "name": "notification",
                                        "value": "發送告警通知",
                                        "type": "string"
                                    },
                                    {
                                        "id": "2",
                                        "name": "message",
                                        "value": "={{ '工作流 ' + $json.workflowName + ' 發生錯誤: ' + $json.errorMessage }}",
                                        "type": "string"
                                    }
                                ]
                            }
                        },
                        "name": "Send Alert",
                        "type": "n8n-nodes-base.set",
                        "typeVersion": 3,
                        "position": [1050, 200]
                    }
                ],
                "connections": {
                    "Error Trigger": {
                        "main": [
                            [
                                {
                                    "node": "Process Error",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    },
                    "Process Error": {
                        "main": [
                            [
                                {
                                    "node": "Log Error",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    },
                    "Log Error": {
                        "main": [
                            [
                                {
                                    "node": "IF Critical",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    },
                    "IF Critical": {
                        "main": [
                            [
                                {
                                    "node": "Send Alert",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    }
                },
                "settings": {}
            }

            print(f"\n創建錯誤觸發器工作流: {workflow_name}")

            workflow = self._make_request("POST", "/api/v1/workflows", data=workflow_data)

            print(f"\n✓ 工作流創建成功")
            print(f"  ID: {workflow.get('id')}")
            print(f"  功能: 捕獲並處理工作流錯誤")

            return workflow

        except Exception as e:
            print(f"\n✗ 創建失敗: {str(e)}")
            return None

    def example_2_create_retry_workflow(
        self,
        workflow_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        示例 2: 創建重試機制工作流

        配置節點重試參數

        參數:
            workflow_name: 工作流名稱

        返回:
            創建的工作流對象
        """
        print("\n" + "="*60)
        print("示例 2: 創建重試機制工作流")
        print("="*60)

        try:
            workflow_data = {
                "name": workflow_name,
                "active": True,
                "nodes": [
                    {
                        "parameters": {
                            "httpMethod": "POST",
                            "path": "retry-test",
                            "responseMode": "lastNode"
                        },
                        "name": "Webhook",
                        "type": "n8n-nodes-base.webhook",
                        "typeVersion": 1,
                        "position": [250, 300]
                    },
                    {
                        "parameters": {
                            "url": "={{ $json.apiUrl }}",
                            "options": {
                                "timeout": 10000
                            }
                        },
                        "name": "HTTP Request",
                        "type": "n8n-nodes-base.httpRequest",
                        "typeVersion": 3,
                        "position": [450, 300],
                        "retryOnFail": True,
                        "maxTries": 3,
                        "waitBetweenTries": 1000,
                        "onError": "continueErrorOutput"
                    },
                    {
                        "parameters": {
                            "conditions": {
                                "boolean": [
                                    {
                                        "value1": "={{ $json.error !== undefined }}",
                                        "value2": True
                                    }
                                ]
                            }
                        },
                        "name": "Check Error",
                        "type": "n8n-nodes-base.if",
                        "typeVersion": 1,
                        "position": [650, 300]
                    },
                    {
                        "parameters": {
                            "mode": "manual",
                            "duplicateItem": False,
                            "assignments": {
                                "assignments": [
                                    {
                                        "id": "1",
                                        "name": "status",
                                        "value": "failed",
                                        "type": "string"
                                    },
                                    {
                                        "id": "2",
                                        "name": "message",
                                        "value": "API 調用失敗，已重試 3 次",
                                        "type": "string"
                                    },
                                    {
                                        "id": "3",
                                        "name": "error",
                                        "value": "={{ $json.error }}",
                                        "type": "object"
                                    }
                                ]
                            }
                        },
                        "name": "Handle Failure",
                        "type": "n8n-nodes-base.set",
                        "typeVersion": 3,
                        "position": [850, 200]
                    },
                    {
                        "parameters": {
                            "mode": "manual",
                            "duplicateItem": False,
                            "assignments": {
                                "assignments": [
                                    {
                                        "id": "1",
                                        "name": "status",
                                        "value": "success",
                                        "type": "string"
                                    },
                                    {
                                        "id": "2",
                                        "name": "message",
                                        "value": "API 調用成功",
                                        "type": "string"
                                    },
                                    {
                                        "id": "3",
                                        "name": "data",
                                        "value": "={{ $json }}",
                                        "type": "object"
                                    }
                                ]
                            }
                        },
                        "name": "Handle Success",
                        "type": "n8n-nodes-base.set",
                        "typeVersion": 3,
                        "position": [850, 400]
                    }
                ],
                "connections": {
                    "Webhook": {
                        "main": [
                            [
                                {
                                    "node": "HTTP Request",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    },
                    "HTTP Request": {
                        "main": [
                            [
                                {
                                    "node": "Check Error",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    },
                    "Check Error": {
                        "main": [
                            [
                                {
                                    "node": "Handle Failure",
                                    "type": "main",
                                    "index": 0
                                }
                            ],
                            [
                                {
                                    "node": "Handle Success",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    }
                },
                "settings": {
                    "saveDataErrorExecution": "all",
                    "saveDataSuccessExecution": "all"
                }
            }

            print(f"\n創建重試機制工作流: {workflow_name}")

            workflow = self._make_request("POST", "/api/v1/workflows", data=workflow_data)

            print(f"\n✓ 工作流創建成功")
            print(f"  ID: {workflow.get('id')}")
            print(f"  重試配置:")
            print(f"    - 最大重試次數: 3")
            print(f"    - 重試間隔: 1000ms")
            print(f"    - 錯誤處理: 繼續執行錯誤輸出")

            return workflow

        except Exception as e:
            print(f"\n✗ 創建失敗: {str(e)}")
            return None

    def example_3_create_try_catch_workflow(
        self,
        workflow_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        示例 3: 創建 Try-Catch 模式工作流

        使用錯誤輸出實現 Try-Catch 邏輯

        參數:
            workflow_name: 工作流名稱

        返回:
            創建的工作流對象
        """
        print("\n" + "="*60)
        print("示例 3: 創建 Try-Catch 模式工作流")
        print("="*60)

        try_code = """
// Try 塊：嘗試執行可能失敗的操作
try {
  const data = $json;

  // 模擬可能失敗的操作
  if (!data.value) {
    throw new Error('Missing required field: value');
  }

  if (data.value < 0) {
    throw new Error('Value must be positive');
  }

  // 成功處理
  return {
    json: {
      status: 'success',
      result: data.value * 2,
      processedAt: new Date().toISOString()
    }
  };

} catch (error) {
  // Catch 塊：處理錯誤
  return {
    json: {
      status: 'error',
      message: error.message,
      originalData: $json,
      errorAt: new Date().toISOString()
    }
  };
}
"""

        try:
            workflow_data = {
                "name": workflow_name,
                "active": True,
                "nodes": [
                    {
                        "parameters": {
                            "httpMethod": "POST",
                            "path": "try-catch",
                            "responseMode": "lastNode"
                        },
                        "name": "Webhook",
                        "type": "n8n-nodes-base.webhook",
                        "typeVersion": 1,
                        "position": [250, 300]
                    },
                    {
                        "parameters": {
                            "language": "javaScript",
                            "jsCode": try_code
                        },
                        "name": "Try-Catch Logic",
                        "type": "n8n-nodes-base.code",
                        "typeVersion": 2,
                        "position": [450, 300],
                        "continueOnFail": True
                    },
                    {
                        "parameters": {
                            "conditions": {
                                "string": [
                                    {
                                        "value1": "={{ $json.status }}",
                                        "operation": "equals",
                                        "value2": "error"
                                    }
                                ]
                            }
                        },
                        "name": "Check Status",
                        "type": "n8n-nodes-base.if",
                        "typeVersion": 1,
                        "position": [650, 300]
                    },
                    {
                        "parameters": {
                            "language": "javaScript",
                            "jsCode": "// 錯誤恢復邏輯\nconst errorData = $json;\n\nreturn {\n  json: {\n    recovered: true,\n    originalError: errorData.message,\n    fallbackResult: 0,\n    message: '使用默認值恢復'\n  }\n};"
                        },
                        "name": "Recover from Error",
                        "type": "n8n-nodes-base.code",
                        "typeVersion": 2,
                        "position": [850, 200]
                    },
                    {
                        "parameters": {
                            "mode": "manual",
                            "duplicateItem": False,
                            "assignments": {
                                "assignments": [
                                    {
                                        "id": "1",
                                        "name": "finalResult",
                                        "value": "={{ $json }}",
                                        "type": "object"
                                    }
                                ]
                            }
                        },
                        "name": "Success Result",
                        "type": "n8n-nodes-base.set",
                        "typeVersion": 3,
                        "position": [850, 400]
                    }
                ],
                "connections": {
                    "Webhook": {
                        "main": [
                            [
                                {
                                    "node": "Try-Catch Logic",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    },
                    "Try-Catch Logic": {
                        "main": [
                            [
                                {
                                    "node": "Check Status",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    },
                    "Check Status": {
                        "main": [
                            [
                                {
                                    "node": "Recover from Error",
                                    "type": "main",
                                    "index": 0
                                }
                            ],
                            [
                                {
                                    "node": "Success Result",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    }
                },
                "settings": {}
            }

            print(f"\n創建 Try-Catch 工作流: {workflow_name}")

            workflow = self._make_request("POST", "/api/v1/workflows", data=workflow_data)

            print(f"\n✓ 工作流創建成功")
            print(f"  ID: {workflow.get('id')}")
            print(f"  功能: 錯誤捕獲和恢復")

            return workflow

        except Exception as e:
            print(f"\n✗ 創建失敗: {str(e)}")
            return None


def main():
    """
    主函數：演示所有錯誤處理示例
    """
    print("\n" + "="*60)
    print("n8n 錯誤處理示例")
    print("="*60)

    # 配置參數
    BASE_URL = os.getenv("N8N_API_URL", "http://localhost:5678")
    API_KEY = os.getenv("N8N_API_KEY")

    # 初始化處理工具
    handler = N8NErrorHandler(base_url=BASE_URL, api_key=API_KEY)

    # 示例 1: 錯誤觸發器
    handler.example_1_create_error_trigger_workflow(
        "Global Error Handler"
    )

    # 示例 2: 重試機制
    handler.example_2_create_retry_workflow(
        "API Retry Logic"
    )

    # 示例 3: Try-Catch
    handler.example_3_create_try_catch_workflow(
        "Try-Catch Pattern"
    )

    print("\n" + "="*60)
    print("所有錯誤處理示例創建完成！")
    print("="*60)


if __name__ == "__main__":
    main()

    print("\n" + "-"*60)
    print("錯誤處理最佳實踐:")
    print("-"*60)
    print("""
    1. Error Trigger
       - 全局錯誤處理
       - 集中式錯誤日誌
       - 告警通知
       - 錯誤分析

    2. 重試機制
       - 設置合理的重試次數
       - 指數退避策略
       - 區分可重試錯誤
       - 記錄重試歷史

    3. 錯誤恢復
       - 提供默認值
       - 降級處理
       - 補償事務
       - 保持數據一致性

    4. 錯誤日誌
       - 記錄詳細的錯誤信息
       - 包含上下文數據
       - 時間戳和追蹤 ID
       - 結構化日誌格式

    5. 監控告警
       - 設置錯誤閾值
       - 實時告警通知
       - 錯誤統計分析
       - 定期審查錯誤日誌

    節點配置:
    - continueOnFail: 錯誤時繼續執行
    - retryOnFail: 啟用重試
    - maxTries: 最大重試次數
    - waitBetweenTries: 重試間隔
    - onError: 錯誤處理方式
    """)

"""
n8n 條件邏輯
============

本範例展示如何在 n8n 中實現條件分支邏輯，包括：
- IF 節點條件判斷
- Switch 節點多條件路由
- Merge 節點合併路徑
- Loop 節點循環處理
- Split 節點分割數據

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


class N8NConditionalLogic:
    """
    n8n 條件邏輯構建器

    創建包含各種條件控制的工作流
    """

    def __init__(self, base_url: str = "http://localhost:5678", api_key: Optional[str] = None):
        """初始化條件邏輯構建器"""
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key or os.getenv("N8N_API_KEY")

        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({
                "X-N8N-API-KEY": self.api_key,
                "Content-Type": "application/json"
            })

        print(f"✓ n8n 條件邏輯構建器已初始化")

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

    def example_1_create_if_workflow(
        self,
        workflow_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        示例 1: 創建 IF 條件判斷工作流

        使用 IF 節點進行二元分支

        參數:
            workflow_name: 工作流名稱

        返回:
            創建的工作流對象
        """
        print("\n" + "="*60)
        print("示例 1: 創建 IF 條件判斷工作流")
        print("="*60)

        try:
            workflow_data = {
                "name": workflow_name,
                "active": True,
                "nodes": [
                    {
                        "parameters": {
                            "httpMethod": "POST",
                            "path": "if-condition",
                            "responseMode": "lastNode"
                        },
                        "name": "Webhook",
                        "type": "n8n-nodes-base.webhook",
                        "typeVersion": 1,
                        "position": [250, 300]
                    },
                    {
                        "parameters": {
                            "conditions": {
                                "string": [
                                    {
                                        "value1": "={{ $json.status }}",
                                        "operation": "equals",
                                        "value2": "active"
                                    }
                                ],
                                "number": [
                                    {
                                        "value1": "={{ $json.price }}",
                                        "operation": "largerEqual",
                                        "value2": 100
                                    }
                                ]
                            },
                            "combineOperation": "all"
                        },
                        "name": "IF",
                        "type": "n8n-nodes-base.if",
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
                                        "name": "result",
                                        "value": "premium",
                                        "type": "string"
                                    },
                                    {
                                        "id": "2",
                                        "name": "discount",
                                        "value": "={{ $json.price * 0.1 }}",
                                        "type": "number"
                                    }
                                ]
                            }
                        },
                        "name": "Premium Path",
                        "type": "n8n-nodes-base.set",
                        "typeVersion": 3,
                        "position": [650, 200]
                    },
                    {
                        "parameters": {
                            "mode": "manual",
                            "duplicateItem": False,
                            "assignments": {
                                "assignments": [
                                    {
                                        "id": "1",
                                        "name": "result",
                                        "value": "standard",
                                        "type": "string"
                                    },
                                    {
                                        "id": "2",
                                        "name": "discount",
                                        "value": 0,
                                        "type": "number"
                                    }
                                ]
                            }
                        },
                        "name": "Standard Path",
                        "type": "n8n-nodes-base.set",
                        "typeVersion": 3,
                        "position": [650, 400]
                    }
                ],
                "connections": {
                    "Webhook": {
                        "main": [
                            [
                                {
                                    "node": "IF",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    },
                    "IF": {
                        "main": [
                            [
                                {
                                    "node": "Premium Path",
                                    "type": "main",
                                    "index": 0
                                }
                            ],
                            [
                                {
                                    "node": "Standard Path",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    }
                },
                "settings": {}
            }

            print(f"\n創建 IF 條件工作流: {workflow_name}")

            workflow = self._make_request("POST", "/api/v1/workflows", data=workflow_data)

            print(f"\n✓ 工作流創建成功")
            print(f"  ID: {workflow.get('id')}")
            print(f"  條件: status=active AND price>=100")
            print(f"  True 路徑: Premium Path (10% 折扣)")
            print(f"  False 路徑: Standard Path (無折扣)")

            return workflow

        except Exception as e:
            print(f"\n✗ 創建失敗: {str(e)}")
            return None

    def example_2_create_switch_workflow(
        self,
        workflow_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        示例 2: 創建 Switch 多條件路由工作流

        使用 Switch 節點進行多路分支

        參數:
            workflow_name: 工作流名稱

        返回:
            創建的工作流對象
        """
        print("\n" + "="*60)
        print("示例 2: 創建 Switch 多條件路由工作流")
        print("="*60)

        try:
            workflow_data = {
                "name": workflow_name,
                "active": True,
                "nodes": [
                    {
                        "parameters": {
                            "httpMethod": "POST",
                            "path": "switch-routing",
                            "responseMode": "lastNode"
                        },
                        "name": "Webhook",
                        "type": "n8n-nodes-base.webhook",
                        "typeVersion": 1,
                        "position": [250, 300]
                    },
                    {
                        "parameters": {
                            "mode": "rules",
                            "rules": {
                                "rules": [
                                    {
                                        "operation": "equal",
                                        "value1": "={{ $json.priority }}",
                                        "value2": "high",
                                        "output": 0
                                    },
                                    {
                                        "operation": "equal",
                                        "value1": "={{ $json.priority }}",
                                        "value2": "medium",
                                        "output": 1
                                    },
                                    {
                                        "operation": "equal",
                                        "value1": "={{ $json.priority }}",
                                        "value2": "low",
                                        "output": 2
                                    }
                                ]
                            },
                            "fallbackOutput": 3
                        },
                        "name": "Switch",
                        "type": "n8n-nodes-base.switch",
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
                                        "name": "route",
                                        "value": "high_priority",
                                        "type": "string"
                                    },
                                    {
                                        "id": "2",
                                        "name": "sla",
                                        "value": "1 hour",
                                        "type": "string"
                                    }
                                ]
                            }
                        },
                        "name": "High Priority",
                        "type": "n8n-nodes-base.set",
                        "typeVersion": 3,
                        "position": [650, 100]
                    },
                    {
                        "parameters": {
                            "mode": "manual",
                            "duplicateItem": False,
                            "assignments": {
                                "assignments": [
                                    {
                                        "id": "1",
                                        "name": "route",
                                        "value": "medium_priority",
                                        "type": "string"
                                    },
                                    {
                                        "id": "2",
                                        "name": "sla",
                                        "value": "4 hours",
                                        "type": "string"
                                    }
                                ]
                            }
                        },
                        "name": "Medium Priority",
                        "type": "n8n-nodes-base.set",
                        "typeVersion": 3,
                        "position": [650, 250]
                    },
                    {
                        "parameters": {
                            "mode": "manual",
                            "duplicateItem": False,
                            "assignments": {
                                "assignments": [
                                    {
                                        "id": "1",
                                        "name": "route",
                                        "value": "low_priority",
                                        "type": "string"
                                    },
                                    {
                                        "id": "2",
                                        "name": "sla",
                                        "value": "24 hours",
                                        "type": "string"
                                    }
                                ]
                            }
                        },
                        "name": "Low Priority",
                        "type": "n8n-nodes-base.set",
                        "typeVersion": 3,
                        "position": [650, 400]
                    },
                    {
                        "parameters": {
                            "mode": "manual",
                            "duplicateItem": False,
                            "assignments": {
                                "assignments": [
                                    {
                                        "id": "1",
                                        "name": "route",
                                        "value": "default",
                                        "type": "string"
                                    },
                                    {
                                        "id": "2",
                                        "name": "sla",
                                        "value": "best effort",
                                        "type": "string"
                                    }
                                ]
                            }
                        },
                        "name": "Default",
                        "type": "n8n-nodes-base.set",
                        "typeVersion": 3,
                        "position": [650, 550]
                    }
                ],
                "connections": {
                    "Webhook": {
                        "main": [
                            [
                                {
                                    "node": "Switch",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    },
                    "Switch": {
                        "main": [
                            [
                                {
                                    "node": "High Priority",
                                    "type": "main",
                                    "index": 0
                                }
                            ],
                            [
                                {
                                    "node": "Medium Priority",
                                    "type": "main",
                                    "index": 0
                                }
                            ],
                            [
                                {
                                    "node": "Low Priority",
                                    "type": "main",
                                    "index": 0
                                }
                            ],
                            [
                                {
                                    "node": "Default",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    }
                },
                "settings": {}
            }

            print(f"\n創建 Switch 路由工作流: {workflow_name}")

            workflow = self._make_request("POST", "/api/v1/workflows", data=workflow_data)

            print(f"\n✓ 工作流創建成功")
            print(f"  ID: {workflow.get('id')}")
            print(f"  路由規則:")
            print(f"    - High: priority='high' -> SLA 1 hour")
            print(f"    - Medium: priority='medium' -> SLA 4 hours")
            print(f"    - Low: priority='low' -> SLA 24 hours")
            print(f"    - Default: 其他情況 -> best effort")

            return workflow

        except Exception as e:
            print(f"\n✗ 創建失敗: {str(e)}")
            return None

    def example_3_create_merge_workflow(
        self,
        workflow_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        示例 3: 創建路徑合併工作流

        使用 Merge 節點合併多個執行路徑

        參數:
            workflow_name: 工作流名稱

        返回:
            創建的工作流對象
        """
        print("\n" + "="*60)
        print("示例 3: 創建路徑合併工作流")
        print("="*60)

        try:
            workflow_data = {
                "name": workflow_name,
                "active": True,
                "nodes": [
                    {
                        "parameters": {
                            "httpMethod": "POST",
                            "path": "merge-paths",
                            "responseMode": "lastNode"
                        },
                        "name": "Webhook",
                        "type": "n8n-nodes-base.webhook",
                        "typeVersion": 1,
                        "position": [250, 300]
                    },
                    {
                        "parameters": {
                            "conditions": {
                                "number": [
                                    {
                                        "value1": "={{ $json.value }}",
                                        "operation": "larger",
                                        "value2": 50
                                    }
                                ]
                            }
                        },
                        "name": "IF",
                        "type": "n8n-nodes-base.if",
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
                                        "name": "category",
                                        "value": "large",
                                        "type": "string"
                                    }
                                ]
                            }
                        },
                        "name": "Process Large",
                        "type": "n8n-nodes-base.set",
                        "typeVersion": 3,
                        "position": [650, 200]
                    },
                    {
                        "parameters": {
                            "mode": "manual",
                            "duplicateItem": False,
                            "assignments": {
                                "assignments": [
                                    {
                                        "id": "1",
                                        "name": "category",
                                        "value": "small",
                                        "type": "string"
                                    }
                                ]
                            }
                        },
                        "name": "Process Small",
                        "type": "n8n-nodes-base.set",
                        "typeVersion": 3,
                        "position": [650, 400]
                    },
                    {
                        "parameters": {
                            "mode": "combine",
                            "combinationMode": "mergeByPosition",
                            "options": {}
                        },
                        "name": "Merge",
                        "type": "n8n-nodes-base.merge",
                        "typeVersion": 2,
                        "position": [850, 300]
                    },
                    {
                        "parameters": {
                            "language": "javaScript",
                            "jsCode": "// 合併後的處理\nconst items = $input.all();\n\nreturn items.map(item => ({\n  json: {\n    ...item.json,\n    processedAt: new Date().toISOString(),\n    totalItems: items.length\n  }\n}));"
                        },
                        "name": "Final Processing",
                        "type": "n8n-nodes-base.code",
                        "typeVersion": 2,
                        "position": [1050, 300]
                    }
                ],
                "connections": {
                    "Webhook": {
                        "main": [
                            [
                                {
                                    "node": "IF",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    },
                    "IF": {
                        "main": [
                            [
                                {
                                    "node": "Process Large",
                                    "type": "main",
                                    "index": 0
                                }
                            ],
                            [
                                {
                                    "node": "Process Small",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    },
                    "Process Large": {
                        "main": [
                            [
                                {
                                    "node": "Merge",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    },
                    "Process Small": {
                        "main": [
                            [
                                {
                                    "node": "Merge",
                                    "type": "main",
                                    "index": 1
                                }
                            ]
                        ]
                    },
                    "Merge": {
                        "main": [
                            [
                                {
                                    "node": "Final Processing",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    }
                },
                "settings": {}
            }

            print(f"\n創建路徑合併工作流: {workflow_name}")

            workflow = self._make_request("POST", "/api/v1/workflows", data=workflow_data)

            print(f"\n✓ 工作流創建成功")
            print(f"  ID: {workflow.get('id')}")
            print(f"  功能: 根據條件分支處理，最後合併結果")

            return workflow

        except Exception as e:
            print(f"\n✗ 創建失敗: {str(e)}")
            return None

    def example_4_create_loop_workflow(
        self,
        workflow_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        示例 4: 創建循環處理工作流

        使用 Loop 節點進行迭代處理

        參數:
            workflow_name: 工作流名稱

        返回:
            創建的工作流對象
        """
        print("\n" + "="*60)
        print("示例 4: 創建循環處理工作流")
        print("="*60)

        loop_code = """
// 循環處理邏輯
const items = $input.all();
const currentIndex = $node["Loop Over Items"].runIndex || 0;

// 處理當前項
if (currentIndex < items.length) {
  const currentItem = items[currentIndex];

  return {
    json: {
      index: currentIndex,
      item: currentItem.json,
      processed: true,
      timestamp: new Date().toISOString()
    }
  };
}

// 循環結束
return null;
"""

        try:
            workflow_data = {
                "name": workflow_name,
                "active": True,
                "nodes": [
                    {
                        "parameters": {
                            "httpMethod": "POST",
                            "path": "loop-process",
                            "responseMode": "lastNode"
                        },
                        "name": "Webhook",
                        "type": "n8n-nodes-base.webhook",
                        "typeVersion": 1,
                        "position": [250, 300]
                    },
                    {
                        "parameters": {
                            "options": {}
                        },
                        "name": "Loop Over Items",
                        "type": "n8n-nodes-base.splitInBatches",
                        "typeVersion": 1,
                        "position": [450, 300]
                    },
                    {
                        "parameters": {
                            "language": "javaScript",
                            "jsCode": "// 處理每個批次\nconst items = $input.all();\n\nreturn items.map((item, index) => ({\n  json: {\n    ...item.json,\n    batchIndex: index,\n    processedAt: new Date().toISOString()\n  }\n}));"
                        },
                        "name": "Process Batch",
                        "type": "n8n-nodes-base.code",
                        "typeVersion": 2,
                        "position": [650, 300]
                    }
                ],
                "connections": {
                    "Webhook": {
                        "main": [
                            [
                                {
                                    "node": "Loop Over Items",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    },
                    "Loop Over Items": {
                        "main": [
                            [
                                {
                                    "node": "Process Batch",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    },
                    "Process Batch": {
                        "main": [
                            [
                                {
                                    "node": "Loop Over Items",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    }
                },
                "settings": {}
            }

            print(f"\n創建循環處理工作流: {workflow_name}")

            workflow = self._make_request("POST", "/api/v1/workflows", data=workflow_data)

            print(f"\n✓ 工作流創建成功")
            print(f"  ID: {workflow.get('id')}")
            print(f"  功能: 批次循環處理數據")

            return workflow

        except Exception as e:
            print(f"\n✗ 創建失敗: {str(e)}")
            return None


def main():
    """
    主函數：演示所有條件邏輯示例
    """
    print("\n" + "="*60)
    print("n8n 條件邏輯示例")
    print("="*60)

    # 配置參數
    BASE_URL = os.getenv("N8N_API_URL", "http://localhost:5678")
    API_KEY = os.getenv("N8N_API_KEY")

    # 初始化構建器
    builder = N8NConditionalLogic(base_url=BASE_URL, api_key=API_KEY)

    # 示例 1: IF 條件
    builder.example_1_create_if_workflow(
        "IF Conditional Routing"
    )

    # 示例 2: Switch 路由
    builder.example_2_create_switch_workflow(
        "Switch Multi-Path Routing"
    )

    # 示例 3: 路徑合併
    builder.example_3_create_merge_workflow(
        "Merge Execution Paths"
    )

    # 示例 4: 循環處理
    builder.example_4_create_loop_workflow(
        "Loop Batch Processing"
    )

    print("\n" + "="*60)
    print("所有條件邏輯示例創建完成！")
    print("="*60)


if __name__ == "__main__":
    main()

    print("\n" + "-"*60)
    print("條件邏輯最佳實踐:")
    print("-"*60)
    print("""
    1. IF 節點
       - 用於簡單的二元判斷
       - 支持多個條件組合
       - AND/OR 邏輯運算
       - True/False 兩個輸出

    2. Switch 節點
       - 用於多路分支
       - 支持多個規則
       - 可設置默認路徑
       - 性能優於多個 IF

    3. Merge 節點
       - 合併多個執行路徑
       - 三種合併模式:
         * Append: 追加所有數據
         * Merge by Position: 按位置合併
         * Merge by Key: 按鍵合併
       - 處理並發執行

    4. Loop 節點
       - 批次處理大量數據
       - 控制內存使用
       - 支持暫停和恢復
       - 避免超時

    5. 設計原則
       - 盡早過濾數據
       - 避免深層嵌套
       - 使用有意義的命名
       - 添加註釋說明
       - 處理邊界情況
    """)

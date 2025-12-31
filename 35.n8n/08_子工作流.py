"""
n8n 子工作流
============

本範例展示如何在 n8n 中使用子工作流，包括：
- Execute Workflow 節點
- 子工作流調用
- 參數傳遞
- 數據返回
- 工作流重用

安裝依賴:
pip install requests python-dotenv

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


class N8NSubWorkflowManager:
    """
    n8n 子工作流管理器

    創建和管理子工作流
    """

    def __init__(self, base_url: str = "http://localhost:5678", api_key: Optional[str] = None):
        """初始化子工作流管理器"""
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key or os.getenv("N8N_API_KEY")

        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({
                "X-N8N-API-KEY": self.api_key,
                "Content-Type": "application/json"
            })

        print(f"✓ n8n 子工作流管理器已初始化")

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

    def example_1_create_data_validator_subworkflow(
        self,
        workflow_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        示例 1: 創建數據驗證子工作流

        可被其他工作流調用的數據驗證工具

        參數:
            workflow_name: 工作流名稱

        返回:
            創建的工作流對象
        """
        print("\n" + "="*60)
        print("示例 1: 創建數據驗證子工作流")
        print("="*60)

        validation_code = """
// 數據驗證邏輯
const items = $input.all();

const validated = items.map(item => {
  const data = item.json;
  const errors = [];

  // 驗證必填字段
  if (!data.email) {
    errors.push('Email is required');
  } else if (!/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(data.email)) {
    errors.push('Invalid email format');
  }

  if (!data.name) {
    errors.push('Name is required');
  }

  if (data.age && (data.age < 0 || data.age > 150)) {
    errors.push('Invalid age');
  }

  return {
    json: {
      ...data,
      valid: errors.length === 0,
      errors: errors,
      validatedAt: new Date().toISOString()
    }
  };
});

return validated;
"""

        try:
            workflow_data = {
                "name": workflow_name,
                "active": False,  # 子工作流通常不需要啟用
                "nodes": [
                    {
                        "parameters": {},
                        "name": "Execute Workflow Trigger",
                        "type": "n8n-nodes-base.executeWorkflowTrigger",
                        "typeVersion": 1,
                        "position": [250, 300]
                    },
                    {
                        "parameters": {
                            "language": "javaScript",
                            "jsCode": validation_code
                        },
                        "name": "Validate Data",
                        "type": "n8n-nodes-base.code",
                        "typeVersion": 2,
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
                                        "name": "validationResult",
                                        "value": "={{ $json }}",
                                        "type": "object"
                                    },
                                    {
                                        "id": "2",
                                        "name": "timestamp",
                                        "value": "={{ new Date().toISOString() }}",
                                        "type": "string"
                                    }
                                ]
                            }
                        },
                        "name": "Format Result",
                        "type": "n8n-nodes-base.set",
                        "typeVersion": 3,
                        "position": [650, 300]
                    }
                ],
                "connections": {
                    "Execute Workflow Trigger": {
                        "main": [
                            [
                                {
                                    "node": "Validate Data",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    },
                    "Validate Data": {
                        "main": [
                            [
                                {
                                    "node": "Format Result",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    }
                },
                "settings": {}
            }

            print(f"\n創建數據驗證子工作流: {workflow_name}")

            workflow = self._make_request("POST", "/api/v1/workflows", data=workflow_data)

            print(f"\n✓ 子工作流創建成功")
            print(f"  ID: {workflow.get('id')}")
            print(f"  類型: 可重用的數據驗證工具")

            return workflow

        except Exception as e:
            print(f"\n✗ 創建失敗: {str(e)}")
            return None

    def example_2_create_data_enrichment_subworkflow(
        self,
        workflow_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        示例 2: 創建數據豐富化子工作流

        添加額外信息到數據中

        參數:
            workflow_name: 工作流名稱

        返回:
            創建的工作流對象
        """
        print("\n" + "="*60)
        print("示例 2: 創建數據豐富化子工作流")
        print("="*60)

        enrichment_code = """
// 數據豐富化邏輯
const items = $input.all();

const enriched = items.map(item => {
  const data = item.json;

  // 添加計算字段
  const fullName = [data.firstName, data.lastName].filter(Boolean).join(' ');

  // 添加元數據
  const metadata = {
    enrichedAt: new Date().toISOString(),
    version: '1.0',
    source: 'n8n-enrichment'
  };

  // 地理位置數據（示例）
  const locationData = {
    timezone: 'Asia/Taipei',
    country: 'Taiwan'
  };

  return {
    json: {
      ...data,
      fullName: fullName,
      metadata: metadata,
      location: locationData,
      enriched: true
    }
  };
});

return enriched;
"""

        try:
            workflow_data = {
                "name": workflow_name,
                "active": False,
                "nodes": [
                    {
                        "parameters": {},
                        "name": "Execute Workflow Trigger",
                        "type": "n8n-nodes-base.executeWorkflowTrigger",
                        "typeVersion": 1,
                        "position": [250, 300]
                    },
                    {
                        "parameters": {
                            "language": "javaScript",
                            "jsCode": enrichment_code
                        },
                        "name": "Enrich Data",
                        "type": "n8n-nodes-base.code",
                        "typeVersion": 2,
                        "position": [450, 300]
                    }
                ],
                "connections": {
                    "Execute Workflow Trigger": {
                        "main": [
                            [
                                {
                                    "node": "Enrich Data",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    }
                },
                "settings": {}
            }

            print(f"\n創建數據豐富化子工作流: {workflow_name}")

            workflow = self._make_request("POST", "/api/v1/workflows", data=workflow_data)

            print(f"\n✓ 子工作流創建成功")
            print(f"  ID: {workflow.get('id')}")

            return workflow

        except Exception as e:
            print(f"\n✗ 創建失敗: {str(e)}")
            return None

    def example_3_create_main_workflow_with_subworkflows(
        self,
        workflow_name: str,
        validator_id: str,
        enricher_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        示例 3: 創建調用子工作流的主工作流

        參數:
            workflow_name: 工作流名稱
            validator_id: 驗證子工作流 ID
            enricher_id: 豐富化子工作流 ID

        返回:
            創建的工作流對象
        """
        print("\n" + "="*60)
        print("示例 3: 創建調用子工作流的主工作流")
        print("="*60)

        try:
            workflow_data = {
                "name": workflow_name,
                "active": True,
                "nodes": [
                    {
                        "parameters": {
                            "httpMethod": "POST",
                            "path": "process-data",
                            "responseMode": "lastNode"
                        },
                        "name": "Webhook",
                        "type": "n8n-nodes-base.webhook",
                        "typeVersion": 1,
                        "position": [250, 300]
                    },
                    {
                        "parameters": {
                            "workflowId": validator_id,
                            "options": {}
                        },
                        "name": "Call Validator",
                        "type": "n8n-nodes-base.executeWorkflow",
                        "typeVersion": 1,
                        "position": [450, 300]
                    },
                    {
                        "parameters": {
                            "conditions": {
                                "boolean": [
                                    {
                                        "value1": "={{ $json.validationResult.valid }}",
                                        "value2": True
                                    }
                                ]
                            }
                        },
                        "name": "IF Valid",
                        "type": "n8n-nodes-base.if",
                        "typeVersion": 1,
                        "position": [650, 300]
                    },
                    {
                        "parameters": {
                            "workflowId": enricher_id,
                            "options": {}
                        },
                        "name": "Call Enricher",
                        "type": "n8n-nodes-base.executeWorkflow",
                        "typeVersion": 1,
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
                                        "name": "data",
                                        "value": "={{ $json }}",
                                        "type": "object"
                                    }
                                ]
                            }
                        },
                        "name": "Success Response",
                        "type": "n8n-nodes-base.set",
                        "typeVersion": 3,
                        "position": [1050, 200]
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
                                        "value": "validation_failed",
                                        "type": "string"
                                    },
                                    {
                                        "id": "2",
                                        "name": "errors",
                                        "value": "={{ $json.validationResult.errors }}",
                                        "type": "object"
                                    }
                                ]
                            }
                        },
                        "name": "Validation Error",
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
                                    "node": "Call Validator",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    },
                    "Call Validator": {
                        "main": [
                            [
                                {
                                    "node": "IF Valid",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    },
                    "IF Valid": {
                        "main": [
                            [
                                {
                                    "node": "Call Enricher",
                                    "type": "main",
                                    "index": 0
                                }
                            ],
                            [
                                {
                                    "node": "Validation Error",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    },
                    "Call Enricher": {
                        "main": [
                            [
                                {
                                    "node": "Success Response",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    }
                },
                "settings": {}
            }

            print(f"\n創建主工作流: {workflow_name}")

            workflow = self._make_request("POST", "/api/v1/workflows", data=workflow_data)

            print(f"\n✓ 主工作流創建成功")
            print(f"  ID: {workflow.get('id')}")
            print(f"  流程:")
            print(f"    1. 接收數據 (Webhook)")
            print(f"    2. 調用驗證子工作流")
            print(f"    3. 如果驗證通過，調用豐富化子工作流")
            print(f"    4. 返回處理結果")

            return workflow

        except Exception as e:
            print(f"\n✗ 創建失敗: {str(e)}")
            return None

    def example_4_get_workflow_id_by_name(self, workflow_name: str) -> Optional[str]:
        """
        示例 4: 根據名稱獲取工作流 ID

        參數:
            workflow_name: 工作流名稱

        返回:
            工作流 ID
        """
        print(f"\n查找工作流: {workflow_name}")

        try:
            workflows = self._make_request("GET", "/api/v1/workflows")

            for workflow in workflows:
                if workflow.get('name') == workflow_name:
                    workflow_id = workflow.get('id')
                    print(f"✓ 找到工作流 ID: {workflow_id}")
                    return workflow_id

            print(f"✗ 未找到工作流: {workflow_name}")
            return None

        except Exception as e:
            print(f"✗ 查找失敗: {str(e)}")
            return None


def main():
    """
    主函數：演示所有子工作流示例
    """
    print("\n" + "="*60)
    print("n8n 子工作流示例")
    print("="*60)

    # 配置參數
    BASE_URL = os.getenv("N8N_API_URL", "http://localhost:5678")
    API_KEY = os.getenv("N8N_API_KEY")

    # 初始化管理器
    manager = N8NSubWorkflowManager(base_url=BASE_URL, api_key=API_KEY)

    # 示例 1: 創建驗證子工作流
    validator = manager.example_1_create_data_validator_subworkflow(
        "SUB: Data Validator"
    )

    # 示例 2: 創建豐富化子工作流
    enricher = manager.example_2_create_data_enrichment_subworkflow(
        "SUB: Data Enricher"
    )

    # 示例 3: 創建主工作流（如果子工作流創建成功）
    if validator and enricher:
        manager.example_3_create_main_workflow_with_subworkflows(
            workflow_name="Main: Data Processing Pipeline",
            validator_id=validator['id'],
            enricher_id=enricher['id']
        )
    else:
        print("\n提示: 子工作流創建失敗，跳過主工作流創建")

    print("\n" + "="*60)
    print("所有子工作流示例創建完成！")
    print("="*60)


if __name__ == "__main__":
    main()

    print("\n" + "-"*60)
    print("子工作流最佳實踐:")
    print("-"*60)
    print("""
    1. 設計原則
       - 單一職責：每個子工作流只做一件事
       - 可重用性：設計為通用工具
       - 參數化：接受輸入參數
       - 清晰的輸出：返回結構化數據

    2. 命名約定
       - 使用前綴標識子工作流（如 SUB:）
       - 描述性名稱
       - 版本控制（如果需要）

    3. 數據傳遞
       - 明確輸入格式
       - 驗證輸入數據
       - 返回完整的處理結果
       - 包含錯誤信息

    4. 錯誤處理
       - 子工作流內處理錯誤
       - 返回錯誤狀態
       - 不要中斷主流程
       - 記錄詳細日誌

    5. 性能考慮
       - 避免過深的嵌套調用
       - 控制子工作流的複雜度
       - 監控執行時間
       - 考慮並發執行

    6. 使用場景
       - 數據驗證
       - 數據轉換
       - 外部 API 調用
       - 業務邏輯封裝
       - 通知發送

    Execute Workflow 節點選項:
    - workflowId: 子工作流 ID
    - source: 數據來源（database/parameter）
    - waitForCompletion: 等待完成
    """)

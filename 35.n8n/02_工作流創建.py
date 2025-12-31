"""
n8n 工作流創建
==============

本範例展示如何通過 API 創建和管理 n8n 工作流，包括：
- 創建工作流
- 更新工作流
- 啟用/禁用工作流
- 刪除工作流
- 導入/導出工作流

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


class N8NWorkflowManager:
    """
    n8n 工作流管理類

    提供工作流的創建、更新、刪除等操作
    """

    def __init__(self, base_url: str = "http://localhost:5678", api_key: Optional[str] = None):
        """
        初始化工作流管理器

        參數:
            base_url: n8n 服務器地址
            api_key: API 密鑰
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key or os.getenv("N8N_API_KEY")

        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({
                "X-N8N-API-KEY": self.api_key,
                "Content-Type": "application/json"
            })
        else:
            self.session.headers.update({
                "Content-Type": "application/json"
            })

        print(f"✓ n8n 工作流管理器已初始化")
        print(f"  服務器地址: {self.base_url}")

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """發送 HTTP 請求"""
        url = f"{self.base_url}{endpoint}"

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=30
            )

            response.raise_for_status()

            if response.status_code == 204 or not response.content:
                return {}

            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"✗ API 請求錯誤: {str(e)}")
            raise

    def example_1_create_simple_workflow(self, workflow_name: str) -> Optional[Dict[str, Any]]:
        """
        示例 1: 創建簡單的工作流

        創建一個包含 Manual Trigger 和 Set 節點的基礎工作流

        參數:
            workflow_name: 工作流名稱

        返回:
            創建的工作流對象
        """
        print("\n" + "="*60)
        print("示例 1: 創建簡單的工作流")
        print("="*60)

        try:
            # 定義工作流結構
            workflow_data = {
                "name": workflow_name,
                "active": False,
                "nodes": [
                    {
                        "parameters": {},
                        "name": "Manual Trigger",
                        "type": "n8n-nodes-base.manualTrigger",
                        "typeVersion": 1,
                        "position": [250, 300]
                    },
                    {
                        "parameters": {
                            "values": {
                                "string": [
                                    {
                                        "name": "message",
                                        "value": "Hello from n8n API!"
                                    }
                                ]
                            },
                            "options": {}
                        },
                        "name": "Set",
                        "type": "n8n-nodes-base.set",
                        "typeVersion": 1,
                        "position": [450, 300]
                    }
                ],
                "connections": {
                    "Manual Trigger": {
                        "main": [
                            [
                                {
                                    "node": "Set",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    }
                },
                "settings": {}
            }

            print(f"\n創建工作流: {workflow_name}")

            # 調用 API 創建工作流
            workflow = self._make_request("POST", "/api/v1/workflows", data=workflow_data)

            print(f"\n✓ 工作流創建成功")
            print(f"  ID: {workflow.get('id')}")
            print(f"  名稱: {workflow.get('name')}")
            print(f"  節點數量: {len(workflow.get('nodes', []))}")

            return workflow

        except Exception as e:
            print(f"\n✗ 創建工作流失敗: {str(e)}")
            return None

    def example_2_create_webhook_workflow(self, workflow_name: str) -> Optional[Dict[str, Any]]:
        """
        示例 2: 創建 Webhook 觸發的工作流

        創建一個可以接收 HTTP 請求的工作流

        參數:
            workflow_name: 工作流名稱

        返回:
            創建的工作流對象
        """
        print("\n" + "="*60)
        print("示例 2: 創建 Webhook 工作流")
        print("="*60)

        try:
            workflow_data = {
                "name": workflow_name,
                "active": True,  # 啟用以接收 Webhook
                "nodes": [
                    {
                        "parameters": {
                            "httpMethod": "POST",
                            "path": "test-webhook",
                            "responseMode": "lastNode",
                            "options": {}
                        },
                        "name": "Webhook",
                        "type": "n8n-nodes-base.webhook",
                        "typeVersion": 1,
                        "position": [250, 300],
                        "webhookId": ""
                    },
                    {
                        "parameters": {
                            "values": {
                                "string": [
                                    {
                                        "name": "status",
                                        "value": "success"
                                    },
                                    {
                                        "name": "receivedData",
                                        "value": "={{ JSON.stringify($json) }}"
                                    }
                                ]
                            }
                        },
                        "name": "Response",
                        "type": "n8n-nodes-base.set",
                        "typeVersion": 1,
                        "position": [450, 300]
                    }
                ],
                "connections": {
                    "Webhook": {
                        "main": [
                            [
                                {
                                    "node": "Response",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    }
                },
                "settings": {
                    "saveDataErrorExecution": "all",
                    "saveDataSuccessExecution": "all",
                    "saveManualExecutions": True
                }
            }

            print(f"\n創建 Webhook 工作流: {workflow_name}")

            workflow = self._make_request("POST", "/api/v1/workflows", data=workflow_data)

            print(f"\n✓ Webhook 工作流創建成功")
            print(f"  ID: {workflow.get('id')}")
            print(f"  Webhook URL: {self.base_url}/webhook/test-webhook")
            print(f"  測試命令: curl -X POST {self.base_url}/webhook/test-webhook -d '{{\"test\":\"data\"}}'")

            return workflow

        except Exception as e:
            print(f"\n✗ 創建 Webhook 工作流失敗: {str(e)}")
            return None

    def example_3_create_schedule_workflow(
        self,
        workflow_name: str,
        cron_expression: str = "0 9 * * *"
    ) -> Optional[Dict[str, Any]]:
        """
        示例 3: 創建定時觸發的工作流

        參數:
            workflow_name: 工作流名稱
            cron_expression: Cron 表達式（默認每天上午 9 點）

        返回:
            創建的工作流對象
        """
        print("\n" + "="*60)
        print("示例 3: 創建定時工作流")
        print("="*60)

        try:
            workflow_data = {
                "name": workflow_name,
                "active": True,
                "nodes": [
                    {
                        "parameters": {
                            "rule": {
                                "interval": [
                                    {
                                        "field": "cronExpression",
                                        "expression": cron_expression
                                    }
                                ]
                            }
                        },
                        "name": "Schedule Trigger",
                        "type": "n8n-nodes-base.scheduleTrigger",
                        "typeVersion": 1,
                        "position": [250, 300]
                    },
                    {
                        "parameters": {
                            "functionCode": "// 執行定時任務\nconst now = new Date();\nreturn [{\n  json: {\n    executedAt: now.toISOString(),\n    message: '定時任務已執行'\n  }\n}];"
                        },
                        "name": "Code",
                        "type": "n8n-nodes-base.code",
                        "typeVersion": 1,
                        "position": [450, 300]
                    }
                ],
                "connections": {
                    "Schedule Trigger": {
                        "main": [
                            [
                                {
                                    "node": "Code",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    }
                },
                "settings": {}
            }

            print(f"\n創建定時工作流: {workflow_name}")
            print(f"Cron 表達式: {cron_expression}")

            workflow = self._make_request("POST", "/api/v1/workflows", data=workflow_data)

            print(f"\n✓ 定時工作流創建成功")
            print(f"  ID: {workflow.get('id')}")
            print(f"  執行時間: {cron_expression}")

            return workflow

        except Exception as e:
            print(f"\n✗ 創建定時工作流失敗: {str(e)}")
            return None

    def example_4_update_workflow(
        self,
        workflow_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        示例 4: 更新工作流

        參數:
            workflow_id: 工作流 ID
            updates: 要更新的字段

        返回:
            更新後的工作流對象
        """
        print("\n" + "="*60)
        print("示例 4: 更新工作流")
        print("="*60)

        try:
            print(f"\n更新工作流 ID: {workflow_id}")
            print(f"更新內容: {json.dumps(updates, indent=2, ensure_ascii=False)}")

            # 調用 API 更新工作流
            workflow = self._make_request(
                "PATCH",
                f"/api/v1/workflows/{workflow_id}",
                data=updates
            )

            print(f"\n✓ 工作流更新成功")
            print(f"  名稱: {workflow.get('name')}")
            print(f"  狀態: {'啟用' if workflow.get('active') else '未啟用'}")

            return workflow

        except Exception as e:
            print(f"\n✗ 更新工作流失敗: {str(e)}")
            return None

    def example_5_activate_workflow(self, workflow_id: str, active: bool = True) -> bool:
        """
        示例 5: 啟用或禁用工作流

        參數:
            workflow_id: 工作流 ID
            active: True 啟用，False 禁用

        返回:
            是否成功
        """
        print("\n" + "="*60)
        print(f"示例 5: {'啟用' if active else '禁用'}工作流")
        print("="*60)

        try:
            updates = {"active": active}

            workflow = self._make_request(
                "PATCH",
                f"/api/v1/workflows/{workflow_id}",
                data=updates
            )

            print(f"\n✓ 工作流{'啟用' if active else '禁用'}成功")
            print(f"  工作流: {workflow.get('name')}")

            return True

        except Exception as e:
            print(f"\n✗ 操作失敗: {str(e)}")
            return False

    def example_6_delete_workflow(self, workflow_id: str) -> bool:
        """
        示例 6: 刪除工作流

        參數:
            workflow_id: 工作流 ID

        返回:
            是否成功
        """
        print("\n" + "="*60)
        print("示例 6: 刪除工作流")
        print("="*60)

        try:
            print(f"\n刪除工作流 ID: {workflow_id}")

            # 調用 API 刪除工作流
            self._make_request("DELETE", f"/api/v1/workflows/{workflow_id}")

            print("\n✓ 工作流刪除成功")
            return True

        except Exception as e:
            print(f"\n✗ 刪除工作流失敗: {str(e)}")
            return False

    def example_7_export_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        示例 7: 導出工作流

        獲取工作流的完整 JSON 配置

        參數:
            workflow_id: 工作流 ID

        返回:
            工作流配置
        """
        print("\n" + "="*60)
        print("示例 7: 導出工作流")
        print("="*60)

        try:
            workflow = self._make_request("GET", f"/api/v1/workflows/{workflow_id}")

            # 保存到文件
            filename = f"workflow_{workflow_id}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(workflow, f, indent=2, ensure_ascii=False)

            print(f"\n✓ 工作流導出成功")
            print(f"  文件: {filename}")

            return workflow

        except Exception as e:
            print(f"\n✗ 導出工作流失敗: {str(e)}")
            return None

    def example_8_import_workflow(self, workflow_file: str) -> Optional[Dict[str, Any]]:
        """
        示例 8: 導入工作流

        從 JSON 文件導入工作流

        參數:
            workflow_file: 工作流文件路徑

        返回:
            創建的工作流對象
        """
        print("\n" + "="*60)
        print("示例 8: 導入工作流")
        print("="*60)

        try:
            # 讀取工作流文件
            with open(workflow_file, 'r', encoding='utf-8') as f:
                workflow_data = json.load(f)

            # 移除 ID（創建新工作流）
            if 'id' in workflow_data:
                del workflow_data['id']

            # 修改名稱（避免衝突）
            workflow_data['name'] = f"{workflow_data.get('name', 'Imported')}_imported"

            print(f"\n導入工作流: {workflow_file}")

            # 創建工作流
            workflow = self._make_request("POST", "/api/v1/workflows", data=workflow_data)

            print(f"\n✓ 工作流導入成功")
            print(f"  ID: {workflow.get('id')}")
            print(f"  名稱: {workflow.get('name')}")

            return workflow

        except Exception as e:
            print(f"\n✗ 導入工作流失敗: {str(e)}")
            return None


def main():
    """
    主函數：演示所有工作流管理示例
    """
    print("\n" + "="*60)
    print("n8n 工作流創建和管理示例")
    print("="*60)

    # 配置參數
    BASE_URL = os.getenv("N8N_API_URL", "http://localhost:5678")
    API_KEY = os.getenv("N8N_API_KEY")

    # 初始化工作流管理器
    manager = N8NWorkflowManager(base_url=BASE_URL, api_key=API_KEY)

    # 示例 1: 創建簡單工作流
    simple_workflow = manager.example_1_create_simple_workflow("Simple Test Workflow")

    # 示例 2: 創建 Webhook 工作流
    webhook_workflow = manager.example_2_create_webhook_workflow("Webhook Test Workflow")

    # 示例 3: 創建定時工作流
    schedule_workflow = manager.example_3_create_schedule_workflow(
        "Daily Schedule Workflow",
        cron_expression="0 9 * * *"  # 每天上午 9 點
    )

    # 示例 4: 更新工作流
    if simple_workflow:
        manager.example_4_update_workflow(
            workflow_id=simple_workflow['id'],
            updates={
                "name": "Updated Simple Workflow",
                "settings": {
                    "saveDataErrorExecution": "all"
                }
            }
        )

    # 示例 5: 啟用/禁用工作流
    if simple_workflow:
        # 啟用工作流
        manager.example_5_activate_workflow(simple_workflow['id'], active=True)

        # 禁用工作流
        manager.example_5_activate_workflow(simple_workflow['id'], active=False)

    # 示例 7: 導出工作流
    if simple_workflow:
        exported = manager.example_7_export_workflow(simple_workflow['id'])

        # 示例 8: 導入工作流
        if exported:
            manager.example_8_import_workflow(f"workflow_{simple_workflow['id']}.json")

    # 示例 6: 清理 - 刪除測試工作流（可選）
    print("\n提示: 如需刪除測試工作流，請取消註釋以下代碼")
    # if simple_workflow:
    #     manager.example_6_delete_workflow(simple_workflow['id'])
    # if webhook_workflow:
    #     manager.example_6_delete_workflow(webhook_workflow['id'])
    # if schedule_workflow:
    #     manager.example_6_delete_workflow(schedule_workflow['id'])

    print("\n" + "="*60)
    print("所有示例運行完成！")
    print("="*60)


if __name__ == "__main__":
    main()

    print("\n" + "-"*60)
    print("工作流設計最佳實踐:")
    print("-"*60)
    print("""
    1. 命名規範
       - 使用有意義的工作流名稱
       - 節點名稱要描述其功能
       - 使用標籤分類工作流

    2. 錯誤處理
       - 添加錯誤處理節點
       - 配置重試機制
       - 記錄錯誤日誌

    3. 性能優化
       - 避免不必要的節點
       - 使用批次處理
       - 優化 HTTP 請求

    4. 安全性
       - 使用環境變量存儲密鑰
       - 限制 Webhook 訪問
       - 定期審計工作流

    5. 維護性
       - 添加註釋說明
       - 版本控制（導出 JSON）
       - 模塊化設計（子工作流）
    """)

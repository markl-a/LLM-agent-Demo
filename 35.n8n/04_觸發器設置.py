"""
n8n 觸發器設置
==============

本範例展示如何配置各種類型的觸發器，包括：
- Webhook 觸發器
- Schedule 觸發器（Cron）
- Email 觸發器
- Form 觸發器
- Chat 觸發器

安裝依賴:
pip install requests python-dotenv croniter

作者: n8n Demo
日期: 2025-12-31
"""

import os
import requests
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from datetime import datetime, timedelta

# 加載環境變量
load_dotenv()


class N8NTriggerManager:
    """
    n8n 觸發器管理器

    管理各種類型的工作流觸發器
    """

    def __init__(self, base_url: str = "http://localhost:5678", api_key: Optional[str] = None):
        """初始化觸發器管理器"""
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key or os.getenv("N8N_API_KEY")

        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({
                "X-N8N-API-KEY": self.api_key,
                "Content-Type": "application/json"
            })

        print(f"✓ n8n 觸發器管理器已初始化")

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

    def example_1_create_webhook_trigger(
        self,
        workflow_name: str,
        webhook_path: str,
        http_method: str = "POST"
    ) -> Optional[Dict[str, Any]]:
        """
        示例 1: 創建 Webhook 觸發器

        參數:
            workflow_name: 工作流名稱
            webhook_path: Webhook 路徑
            http_method: HTTP 方法 (GET, POST, PUT, DELETE)

        返回:
            創建的工作流對象
        """
        print("\n" + "="*60)
        print("示例 1: 創建 Webhook 觸發器")
        print("="*60)

        try:
            workflow_data = {
                "name": workflow_name,
                "active": True,
                "nodes": [
                    {
                        "parameters": {
                            "httpMethod": http_method,
                            "path": webhook_path,
                            "responseMode": "lastNode",
                            "options": {
                                "rawBody": False
                            }
                        },
                        "name": "Webhook",
                        "type": "n8n-nodes-base.webhook",
                        "typeVersion": 1,
                        "position": [250, 300],
                        "webhookId": ""
                    },
                    {
                        "parameters": {
                            "functionCode": "// 處理 Webhook 數據\nconst payload = $input.item.json;\n\nreturn {\n  json: {\n    receivedAt: new Date().toISOString(),\n    method: '{{ $node[\"Webhook\"].context[\"httpMethod\"] }}',\n    data: payload,\n    processed: true\n  }\n};"
                        },
                        "name": "Process Data",
                        "type": "n8n-nodes-base.code",
                        "typeVersion": 1,
                        "position": [450, 300]
                    }
                ],
                "connections": {
                    "Webhook": {
                        "main": [
                            [
                                {
                                    "node": "Process Data",
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

            print(f"\n創建 Webhook 觸發器工作流: {workflow_name}")
            print(f"路徑: /{webhook_path}")
            print(f"方法: {http_method}")

            workflow = self._make_request("POST", "/api/v1/workflows", data=workflow_data)

            webhook_url = f"{self.base_url}/webhook/{webhook_path}"
            print(f"\n✓ Webhook 工作流創建成功")
            print(f"  ID: {workflow.get('id')}")
            print(f"  Webhook URL: {webhook_url}")
            print(f"\n  測試命令:")
            print(f"  curl -X {http_method} {webhook_url} \\")
            print(f"    -H 'Content-Type: application/json' \\")
            print(f"    -d '{{\"test\": \"data\", \"timestamp\": \"{datetime.now().isoformat()}\"}}'")

            return workflow

        except Exception as e:
            print(f"\n✗ 創建失敗: {str(e)}")
            return None

    def example_2_create_schedule_trigger(
        self,
        workflow_name: str,
        cron_expression: str = "0 9 * * *",
        timezone: str = "Asia/Taipei"
    ) -> Optional[Dict[str, Any]]:
        """
        示例 2: 創建定時觸發器（Cron）

        參數:
            workflow_name: 工作流名稱
            cron_expression: Cron 表達式
            timezone: 時區

        返回:
            創建的工作流對象
        """
        print("\n" + "="*60)
        print("示例 2: 創建定時觸發器")
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
                                        "expression": cron_expression,
                                        "timezone": timezone
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
                            "functionCode": "// 定時任務執行邏輯\nconst now = new Date();\n\nreturn {\n  json: {\n    executedAt: now.toISOString(),\n    message: '定時任務已執行',\n    cronExpression: '" + cron_expression + "',\n    nextRun: 'Check schedule'\n  }\n};"
                        },
                        "name": "Execute Task",
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
                                    "node": "Execute Task",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    }
                },
                "settings": {}
            }

            print(f"\n創建定時觸發器工作流: {workflow_name}")
            print(f"Cron 表達式: {cron_expression}")
            print(f"時區: {timezone}")

            workflow = self._make_request("POST", "/api/v1/workflows", data=workflow_data)

            print(f"\n✓ 定時工作流創建成功")
            print(f"  ID: {workflow.get('id')}")
            print(f"\n  Cron 說明:")
            self._explain_cron(cron_expression)

            return workflow

        except Exception as e:
            print(f"\n✗ 創建失敗: {str(e)}")
            return None

    def example_3_create_email_trigger(
        self,
        workflow_name: str,
        imap_host: str = "imap.gmail.com",
        imap_port: int = 993
    ) -> Optional[Dict[str, Any]]:
        """
        示例 3: 創建郵件觸發器

        參數:
            workflow_name: 工作流名稱
            imap_host: IMAP 服務器地址
            imap_port: IMAP 端口

        返回:
            創建的工作流對象
        """
        print("\n" + "="*60)
        print("示例 3: 創建郵件觸發器")
        print("="*60)

        try:
            workflow_data = {
                "name": workflow_name,
                "active": False,  # 需要配置郵箱憑證後啟用
                "nodes": [
                    {
                        "parameters": {
                            "pollTimes": {
                                "item": [
                                    {
                                        "mode": "everyMinute"
                                    }
                                ]
                            },
                            "options": {
                                "allowUnauthorizedCerts": False
                            }
                        },
                        "name": "Email Trigger (IMAP)",
                        "type": "n8n-nodes-base.emailReadImap",
                        "typeVersion": 2,
                        "position": [250, 300]
                    },
                    {
                        "parameters": {
                            "functionCode": "// 處理收到的郵件\nconst email = $input.item.json;\n\nreturn {\n  json: {\n    from: email.from?.text || 'Unknown',\n    subject: email.subject || 'No Subject',\n    receivedAt: new Date().toISOString(),\n    hasAttachments: (email.attachments?.length || 0) > 0,\n    bodyPreview: (email.text || '').substring(0, 100)\n  }\n};"
                        },
                        "name": "Process Email",
                        "type": "n8n-nodes-base.code",
                        "typeVersion": 1,
                        "position": [450, 300]
                    }
                ],
                "connections": {
                    "Email Trigger (IMAP)": {
                        "main": [
                            [
                                {
                                    "node": "Process Email",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    }
                },
                "settings": {}
            }

            print(f"\n創建郵件觸發器工作流: {workflow_name}")

            workflow = self._make_request("POST", "/api/v1/workflows", data=workflow_data)

            print(f"\n✓ 郵件觸發器工作流創建成功")
            print(f"  ID: {workflow.get('id')}")
            print(f"\n  注意:")
            print(f"  1. 需要在 n8n 中配置 IMAP 憑證")
            print(f"  2. Gmail 需要開啟「應用程式密碼」")
            print(f"  3. 配置完成後啟用工作流")

            return workflow

        except Exception as e:
            print(f"\n✗ 創建失敗: {str(e)}")
            return None

    def example_4_create_form_trigger(
        self,
        workflow_name: str,
        form_path: str
    ) -> Optional[Dict[str, Any]]:
        """
        示例 4: 創建表單觸發器

        參數:
            workflow_name: 工作流名稱
            form_path: 表單路徑

        返回:
            創建的工作流對象
        """
        print("\n" + "="*60)
        print("示例 4: 創建表單觸發器")
        print("="*60)

        try:
            workflow_data = {
                "name": workflow_name,
                "active": True,
                "nodes": [
                    {
                        "parameters": {
                            "path": form_path,
                            "formTitle": "聯絡我們",
                            "formDescription": "請填寫以下表單，我們會盡快回覆您。",
                            "formFields": {
                                "values": [
                                    {
                                        "fieldLabel": "姓名",
                                        "fieldType": "text",
                                        "requiredField": True
                                    },
                                    {
                                        "fieldLabel": "電子郵件",
                                        "fieldType": "email",
                                        "requiredField": True
                                    },
                                    {
                                        "fieldLabel": "訊息",
                                        "fieldType": "textarea",
                                        "requiredField": True
                                    }
                                ]
                            },
                            "responseMode": "onReceived",
                            "options": {
                                "formSubmittedText": "感謝您的提交！我們會盡快回覆。"
                            }
                        },
                        "name": "Form Trigger",
                        "type": "n8n-nodes-base.formTrigger",
                        "typeVersion": 1,
                        "position": [250, 300]
                    },
                    {
                        "parameters": {
                            "values": {
                                "string": [
                                    {
                                        "name": "submittedAt",
                                        "value": "={{ new Date().toISOString() }}"
                                    },
                                    {
                                        "name": "name",
                                        "value": "={{ $json.name }}"
                                    },
                                    {
                                        "name": "email",
                                        "value": "={{ $json.email }}"
                                    },
                                    {
                                        "name": "message",
                                        "value": "={{ $json.message }}"
                                    }
                                ]
                            }
                        },
                        "name": "Process Submission",
                        "type": "n8n-nodes-base.set",
                        "typeVersion": 1,
                        "position": [450, 300]
                    }
                ],
                "connections": {
                    "Form Trigger": {
                        "main": [
                            [
                                {
                                    "node": "Process Submission",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    }
                },
                "settings": {}
            }

            print(f"\n創建表單觸發器工作流: {workflow_name}")

            workflow = self._make_request("POST", "/api/v1/workflows", data=workflow_data)

            form_url = f"{self.base_url}/form/{form_path}"
            print(f"\n✓ 表單觸發器工作流創建成功")
            print(f"  ID: {workflow.get('id')}")
            print(f"  表單 URL: {form_url}")
            print(f"  在瀏覽器中打開此 URL 即可查看表單")

            return workflow

        except Exception as e:
            print(f"\n✗ 創建失敗: {str(e)}")
            return None

    def example_5_create_chat_trigger(
        self,
        workflow_name: str,
        chat_path: str
    ) -> Optional[Dict[str, Any]]:
        """
        示例 5: 創建聊天觸發器

        參數:
            workflow_name: 工作流名稱
            chat_path: 聊天路徑

        返回:
            創建的工作流對象
        """
        print("\n" + "="*60)
        print("示例 5: 創建聊天觸發器")
        print("="*60)

        try:
            workflow_data = {
                "name": workflow_name,
                "active": True,
                "nodes": [
                    {
                        "parameters": {
                            "path": chat_path,
                            "options": {
                                "title": "AI 聊天助手",
                                "subtitle": "有什麼可以幫助您的？",
                                "welcomeMessage": "您好！我是 AI 助手，請問有什麼可以幫您？"
                            }
                        },
                        "name": "Chat Trigger",
                        "type": "@n8n/n8n-nodes-langchain.chatTrigger",
                        "typeVersion": 1,
                        "position": [250, 300]
                    },
                    {
                        "parameters": {
                            "agent": "conversationalAgent",
                            "text": "={{ $json.chatInput }}"
                        },
                        "name": "AI Agent",
                        "type": "@n8n/n8n-nodes-langchain.agent",
                        "typeVersion": 1,
                        "position": [450, 300]
                    },
                    {
                        "parameters": {
                            "model": "gpt-3.5-turbo",
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
                    "Chat Trigger": {
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

            print(f"\n創建聊天觸發器工作流: {workflow_name}")

            workflow = self._make_request("POST", "/api/v1/workflows", data=workflow_data)

            chat_url = f"{self.base_url}/chat/{chat_path}"
            print(f"\n✓ 聊天觸發器工作流創建成功")
            print(f"  ID: {workflow.get('id')}")
            print(f"  聊天 URL: {chat_url}")
            print(f"  在瀏覽器中打開此 URL 即可開始聊天")

            return workflow

        except Exception as e:
            print(f"\n✗ 創建失敗: {str(e)}")
            return None

    def _explain_cron(self, cron_expression: str):
        """解釋 Cron 表達式"""
        parts = cron_expression.split()

        if len(parts) == 5:
            minute, hour, day, month, weekday = parts

            print(f"  分鐘: {minute}")
            print(f"  小時: {hour}")
            print(f"  日期: {day}")
            print(f"  月份: {month}")
            print(f"  星期: {weekday}")

            # 常見範例
            examples = {
                "0 9 * * *": "每天上午 9:00",
                "*/5 * * * *": "每 5 分鐘",
                "0 */2 * * *": "每 2 小時",
                "0 0 * * 0": "每週日午夜",
                "0 0 1 * *": "每月 1 號午夜"
            }

            if cron_expression in examples:
                print(f"\n  說明: {examples[cron_expression]}")


def main():
    """
    主函數：演示所有觸發器設置示例
    """
    print("\n" + "="*60)
    print("n8n 觸發器設置示例")
    print("="*60)

    # 配置參數
    BASE_URL = os.getenv("N8N_API_URL", "http://localhost:5678")
    API_KEY = os.getenv("N8N_API_KEY")

    # 初始化管理器
    manager = N8NTriggerManager(base_url=BASE_URL, api_key=API_KEY)

    # 示例 1: Webhook 觸發器
    webhook_workflow = manager.example_1_create_webhook_trigger(
        workflow_name="Webhook API Endpoint",
        webhook_path="api/webhook-test",
        http_method="POST"
    )

    # 示例 2: 定時觸發器
    schedule_workflow = manager.example_2_create_schedule_trigger(
        workflow_name="Daily Report Generator",
        cron_expression="0 9 * * *",  # 每天上午 9 點
        timezone="Asia/Taipei"
    )

    # 示例 3: 郵件觸發器
    email_workflow = manager.example_3_create_email_trigger(
        workflow_name="Email Auto Responder",
        imap_host="imap.gmail.com",
        imap_port=993
    )

    # 示例 4: 表單觸發器
    form_workflow = manager.example_4_create_form_trigger(
        workflow_name="Contact Form Handler",
        form_path="contact-us"
    )

    # 示例 5: 聊天觸發器
    chat_workflow = manager.example_5_create_chat_trigger(
        workflow_name="AI Chat Assistant",
        chat_path="support-chat"
    )

    print("\n" + "="*60)
    print("所有觸發器示例創建完成！")
    print("="*60)


if __name__ == "__main__":
    main()

    print("\n" + "-"*60)
    print("觸發器最佳實踐:")
    print("-"*60)
    print("""
    1. Webhook 觸發器
       - 使用有意義的路徑名稱
       - 驗證請求來源
       - 設置速率限制
       - 記錄所有請求

    2. 定時觸發器
       - 選擇合適的執行時間
       - 避免高峰期執行
       - 設置時區
       - 監控執行狀態

    3. 郵件觸發器
       - 使用專用郵箱
       - 設置過濾規則
       - 定期清理郵件
       - 處理附件安全

    4. 表單觸發器
       - 驗證輸入數據
       - 防止垃圾提交
       - 提供友好的反饋
       - 記錄提交數據

    5. 聊天觸發器
       - 設置歡迎消息
       - 配置 AI 模型
       - 管理會話狀態
       - 處理錯誤情況

    常用 Cron 表達式:
    - */5 * * * * : 每 5 分鐘
    - 0 * * * *   : 每小時
    - 0 9 * * *   : 每天上午 9 點
    - 0 0 * * 0   : 每週日午夜
    - 0 0 1 * *   : 每月 1 號午夜
    """)

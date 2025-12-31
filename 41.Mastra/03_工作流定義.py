"""
Mastra 工作流定義示例

本示例展示如何定義和執行複雜的工作流。

功能：
1. 順序工作流
2. 並行工作流
3. 條件分支
4. 循環執行
5. 錯誤處理工作流
"""

import os
import requests
from typing import Dict, Any, List, Optional, Callable
from dotenv import load_dotenv
import json
import time
from datetime import datetime

load_dotenv()


class MastraWorkflow:
    """Mastra 工作流客戶端"""

    def __init__(self, api_url: str = None):
        """初始化工作流客戶端"""
        self.api_url = api_url or os.getenv('MASTRA_API_URL', 'http://localhost:3000')
        self.api_key = os.getenv('MASTRA_API_KEY')

        self.headers = {
            'Content-Type': 'application/json',
        }
        if self.api_key:
            self.headers['Authorization'] = f'Bearer {self.api_key}'

    def create_workflow(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """創建工作流"""
        try:
            response = requests.post(
                f'{self.api_url}/api/workflows',
                headers=self.headers,
                json=config,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}

    def execute_workflow(self, workflow_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """執行工作流"""
        try:
            response = requests.post(
                f'{self.api_url}/api/workflows/{workflow_name}/execute',
                headers=self.headers,
                json=input_data,
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}

    def get_workflow_status(self, workflow_name: str, execution_id: str) -> Dict[str, Any]:
        """獲取工作流執行狀態"""
        try:
            response = requests.get(
                f'{self.api_url}/api/workflows/{workflow_name}/executions/{execution_id}',
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}


def example_1_sequential_workflow():
    """示例 1：順序工作流"""
    print("=" * 60)
    print("示例 1：順序工作流 - 客戶入職流程")
    print("=" * 60)

    workflow_client = MastraWorkflow()

    # 定義順序工作流
    config = {
        'name': 'customer-onboarding',
        'description': '客戶入職流程',
        'steps': [
            {
                'id': 'validate-info',
                'name': '驗證客戶信息',
                'type': 'agent',
                'agent': 'validation-agent',
                'input': {
                    'data': '{{workflow.input.customerData}}'
                },
                'output': 'validationResult'
            },
            {
                'id': 'create-account',
                'name': '創建帳戶',
                'type': 'function',
                'function': 'createAccount',
                'input': {
                    'customerData': '{{steps.validate-info.output}}'
                },
                'output': 'account'
            },
            {
                'id': 'send-welcome-email',
                'name': '發送歡迎郵件',
                'type': 'integration',
                'integration': 'sendgrid',
                'action': 'send_email',
                'input': {
                    'to': '{{steps.create-account.output.email}}',
                    'template': 'welcome-email',
                    'data': {
                        'accountId': '{{steps.create-account.output.id}}',
                        'name': '{{steps.create-account.output.name}}'
                    }
                },
                'output': 'emailResult'
            },
            {
                'id': 'assign-to-team',
                'name': '分配到團隊',
                'type': 'function',
                'function': 'assignToTeam',
                'input': {
                    'accountId': '{{steps.create-account.output.id}}',
                    'teamId': 'default-team'
                },
                'output': 'assignmentResult'
            }
        ],
        'execution': {
            'type': 'sequential',  # 順序執行
            'timeout': 300000,  # 5 分鐘超時
        }
    }

    result = workflow_client.create_workflow(config)
    print(f"\n工作流創建結果: {json.dumps(result, indent=2, ensure_ascii=False)}")

    # 執行工作流
    input_data = {
        'customerData': {
            'name': '張三',
            'email': 'zhang@example.com',
            'phone': '+886-912-345-678',
            'company': 'ABC Corp'
        }
    }

    print(f"\n執行工作流，輸入: {json.dumps(input_data, indent=2, ensure_ascii=False)}")
    execution_result = workflow_client.execute_workflow('customer-onboarding', input_data)
    print(f"\n執行結果: {json.dumps(execution_result, indent=2, ensure_ascii=False)}")


def example_2_parallel_workflow():
    """示例 2：並行工作流"""
    print("\n" + "=" * 60)
    print("示例 2：並行工作流 - 內容發布流程")
    print("=" * 60)

    workflow_client = MastraWorkflow()

    config = {
        'name': 'content-publishing',
        'description': '多平台內容發布',
        'steps': [
            {
                'id': 'prepare-content',
                'name': '準備內容',
                'type': 'agent',
                'agent': 'content-writer',
                'input': {
                    'topic': '{{workflow.input.topic}}',
                    'style': '{{workflow.input.style}}'
                },
                'output': 'content'
            },
            # 並行執行以下步驟
            {
                'id': 'publish-to-blog',
                'name': '發布到博客',
                'type': 'integration',
                'integration': 'wordpress',
                'action': 'create_post',
                'parallel': true,  # 並行執行
                'dependsOn': ['prepare-content'],
                'input': {
                    'title': '{{steps.prepare-content.output.title}}',
                    'content': '{{steps.prepare-content.output.body}}'
                },
                'output': 'blogPost'
            },
            {
                'id': 'publish-to-twitter',
                'name': '發布到 Twitter',
                'type': 'integration',
                'integration': 'twitter',
                'action': 'create_tweet',
                'parallel': true,  # 並行執行
                'dependsOn': ['prepare-content'],
                'input': {
                    'text': '{{steps.prepare-content.output.summary}}'
                },
                'output': 'tweet'
            },
            {
                'id': 'publish-to-linkedin',
                'name': '發布到 LinkedIn',
                'type': 'integration',
                'integration': 'linkedin',
                'action': 'create_post',
                'parallel': true,  # 並行執行
                'dependsOn': ['prepare-content'],
                'input': {
                    'text': '{{steps.prepare-content.output.body}}'
                },
                'output': 'linkedinPost'
            },
            {
                'id': 'collect-results',
                'name': '收集發布結果',
                'type': 'function',
                'function': 'collectResults',
                'dependsOn': ['publish-to-blog', 'publish-to-twitter', 'publish-to-linkedin'],
                'input': {
                    'blog': '{{steps.publish-to-blog.output}}',
                    'twitter': '{{steps.publish-to-twitter.output}}',
                    'linkedin': '{{steps.publish-to-linkedin.output}}'
                },
                'output': 'publishResults'
            }
        ],
        'execution': {
            'type': 'parallel',  # 支持並行執行
            'maxConcurrency': 3,  # 最多 3 個並發
        }
    }

    result = workflow_client.create_workflow(config)
    print(f"\n工作流創建結果: {json.dumps(result, indent=2, ensure_ascii=False)}")


def example_3_conditional_workflow():
    """示例 3：條件分支工作流"""
    print("\n" + "=" * 60)
    print("示例 3：條件分支工作流 - 訂單處理")
    print("=" * 60)

    workflow_client = MastraWorkflow()

    config = {
        'name': 'order-processing',
        'description': '智能訂單處理流程',
        'steps': [
            {
                'id': 'validate-order',
                'name': '驗證訂單',
                'type': 'function',
                'function': 'validateOrder',
                'input': {
                    'order': '{{workflow.input.order}}'
                },
                'output': 'validation'
            },
            {
                'id': 'check-inventory',
                'name': '檢查庫存',
                'type': 'function',
                'function': 'checkInventory',
                'condition': '{{steps.validate-order.output.isValid}}',
                'input': {
                    'items': '{{workflow.input.order.items}}'
                },
                'output': 'inventory'
            },
            # 條件分支：根據庫存情況決定路徑
            {
                'id': 'process-payment',
                'name': '處理付款',
                'type': 'integration',
                'integration': 'stripe',
                'action': 'create_payment',
                'condition': '{{steps.check-inventory.output.inStock}}',
                'input': {
                    'amount': '{{workflow.input.order.total}}',
                    'customer': '{{workflow.input.order.customerId}}'
                },
                'output': 'payment'
            },
            {
                'id': 'ship-order',
                'name': '發貨',
                'type': 'function',
                'function': 'shipOrder',
                'condition': '{{steps.process-payment.output.success}}',
                'input': {
                    'order': '{{workflow.input.order}}',
                    'payment': '{{steps.process-payment.output}}'
                },
                'output': 'shipment'
            },
            {
                'id': 'notify-out-of-stock',
                'name': '缺貨通知',
                'type': 'integration',
                'integration': 'sendgrid',
                'action': 'send_email',
                'condition': '{{!steps.check-inventory.output.inStock}}',
                'input': {
                    'to': '{{workflow.input.order.customerEmail}}',
                    'template': 'out-of-stock',
                    'data': {
                        'items': '{{steps.check-inventory.output.outOfStockItems}}'
                    }
                },
                'output': 'notification'
            },
            {
                'id': 'refund-payment',
                'name': '退款',
                'type': 'integration',
                'integration': 'stripe',
                'action': 'refund',
                'condition': '{{steps.process-payment.output.success && !steps.ship-order.output.success}}',
                'input': {
                    'paymentId': '{{steps.process-payment.output.id}}'
                },
                'output': 'refund'
            }
        ],
        'execution': {
            'type': 'conditional',
            'timeout': 600000,
        }
    }

    result = workflow_client.create_workflow(config)
    print(f"\n工作流創建結果: {json.dumps(result, indent=2, ensure_ascii=False)}")


def example_4_loop_workflow():
    """示例 4：循環工作流"""
    print("\n" + "=" * 60)
    print("示例 4：循環工作流 - 批量數據處理")
    print("=" * 60)

    workflow_client = MastraWorkflow()

    config = {
        'name': 'batch-processing',
        'description': '批量處理客戶數據',
        'steps': [
            {
                'id': 'fetch-customers',
                'name': '獲取客戶列表',
                'type': 'function',
                'function': 'fetchCustomers',
                'input': {
                    'batchSize': '{{workflow.input.batchSize || 100}}'
                },
                'output': 'customers'
            },
            {
                'id': 'process-customer',
                'name': '處理單個客戶',
                'type': 'loop',  # 循環步驟
                'iterator': '{{steps.fetch-customers.output.customers}}',
                'itemName': 'customer',
                'steps': [
                    {
                        'id': 'enrich-data',
                        'name': '豐富數據',
                        'type': 'agent',
                        'agent': 'data-enrichment',
                        'input': {
                            'customer': '{{loop.customer}}'
                        },
                        'output': 'enrichedCustomer'
                    },
                    {
                        'id': 'update-crm',
                        'name': '更新 CRM',
                        'type': 'integration',
                        'integration': 'salesforce',
                        'action': 'update_contact',
                        'input': {
                            'contactId': '{{loop.customer.id}}',
                            'data': '{{steps.enrich-data.output}}'
                        },
                        'output': 'updateResult'
                    }
                ],
                'output': 'processedCustomers'
            },
            {
                'id': 'generate-report',
                'name': '生成報告',
                'type': 'function',
                'function': 'generateReport',
                'input': {
                    'results': '{{steps.process-customer.output}}'
                },
                'output': 'report'
            }
        ],
        'execution': {
            'type': 'loop',
            'maxIterations': 1000,  # 最多迭代 1000 次
        }
    }

    result = workflow_client.create_workflow(config)
    print(f"\n工作流創建結果: {json.dumps(result, indent=2, ensure_ascii=False)}")


def example_5_error_handling_workflow():
    """示例 5：錯誤處理工作流"""
    print("\n" + "=" * 60)
    print("示例 5：錯誤處理工作流 - API 集成")
    print("=" * 60)

    workflow_client = MastraWorkflow()

    config = {
        'name': 'api-integration-with-retry',
        'description': '帶重試機制的 API 集成',
        'steps': [
            {
                'id': 'call-external-api',
                'name': '調用外部 API',
                'type': 'function',
                'function': 'callExternalAPI',
                'input': {
                    'endpoint': '{{workflow.input.endpoint}}',
                    'data': '{{workflow.input.data}}'
                },
                'retry': {
                    'maxAttempts': 3,  # 最多重試 3 次
                    'backoff': 'exponential',  # 指數退避
                    'initialDelay': 1000,  # 初始延遲 1 秒
                    'maxDelay': 10000,  # 最大延遲 10 秒
                },
                'errorHandling': {
                    'onError': 'continue',  # 出錯時繼續
                    'fallback': {
                        'step': 'use-cache'
                    }
                },
                'output': 'apiResult'
            },
            {
                'id': 'use-cache',
                'name': '使用緩存數據',
                'type': 'function',
                'function': 'getCachedData',
                'condition': '{{steps.call-external-api.error}}',
                'input': {
                    'endpoint': '{{workflow.input.endpoint}}'
                },
                'output': 'cachedResult'
            },
            {
                'id': 'process-result',
                'name': '處理結果',
                'type': 'function',
                'function': 'processData',
                'input': {
                    'data': '{{steps.call-external-api.output || steps.use-cache.output}}'
                },
                'output': 'processedData'
            },
            {
                'id': 'log-error',
                'name': '記錄錯誤',
                'type': 'integration',
                'integration': 'logger',
                'action': 'log_error',
                'condition': '{{steps.call-external-api.error}}',
                'input': {
                    'error': '{{steps.call-external-api.error}}',
                    'context': {
                        'workflow': 'api-integration-with-retry',
                        'step': 'call-external-api'
                    }
                }
            }
        ],
        'errorHandling': {
            'global': {
                'onError': 'rollback',  # 全局錯誤處理：回滾
                'notification': {
                    'channels': ['email', 'slack'],
                    'recipients': ['admin@example.com']
                }
            }
        }
    }

    result = workflow_client.create_workflow(config)
    print(f"\n工作流創建結果: {json.dumps(result, indent=2, ensure_ascii=False)}")


def example_6_human_in_loop_workflow():
    """示例 6：人工審核工作流"""
    print("\n" + "=" * 60)
    print("示例 6：人工審核工作流 - 內容審核")
    print("=" * 60)

    workflow_client = MastraWorkflow()

    config = {
        'name': 'content-moderation',
        'description': '內容審核流程',
        'steps': [
            {
                'id': 'auto-check',
                'name': '自動檢查',
                'type': 'agent',
                'agent': 'moderation-agent',
                'input': {
                    'content': '{{workflow.input.content}}'
                },
                'output': 'autoCheckResult'
            },
            {
                'id': 'human-review',
                'name': '人工審核',
                'type': 'human-task',  # 需要人工介入
                'condition': '{{steps.auto-check.output.confidence < 0.8}}',
                'input': {
                    'content': '{{workflow.input.content}}',
                    'autoCheckResult': '{{steps.auto-check.output}}',
                    'assignee': 'moderation-team'
                },
                'timeout': 3600000,  # 1 小時超時
                'output': 'humanReviewResult'
            },
            {
                'id': 'make-decision',
                'name': '做出決定',
                'type': 'function',
                'function': 'makeDecision',
                'input': {
                    'autoCheck': '{{steps.auto-check.output}}',
                    'humanReview': '{{steps.human-review.output}}'
                },
                'output': 'decision'
            },
            {
                'id': 'publish-content',
                'name': '發布內容',
                'type': 'function',
                'function': 'publishContent',
                'condition': '{{steps.make-decision.output.approved}}',
                'input': {
                    'content': '{{workflow.input.content}}'
                },
                'output': 'publishResult'
            },
            {
                'id': 'notify-author',
                'name': '通知作者',
                'type': 'integration',
                'integration': 'sendgrid',
                'action': 'send_email',
                'input': {
                    'to': '{{workflow.input.authorEmail}}',
                    'template': '{{steps.make-decision.output.approved ? "approved" : "rejected"}}',
                    'data': {
                        'reason': '{{steps.make-decision.output.reason}}'
                    }
                }
            }
        ]
    }

    result = workflow_client.create_workflow(config)
    print(f"\n工作流創建結果: {json.dumps(result, indent=2, ensure_ascii=False)}")


def example_7_multi_agent_workflow():
    """示例 7：多 Agent 協作工作流"""
    print("\n" + "=" * 60)
    print("示例 7：多 Agent 協作工作流 - 研究報告生成")
    print("=" * 60)

    workflow_client = MastraWorkflow()

    config = {
        'name': 'research-report-generation',
        'description': '多 Agent 協作生成研究報告',
        'steps': [
            {
                'id': 'research',
                'name': '研究階段',
                'type': 'agent',
                'agent': 'researcher',
                'input': {
                    'topic': '{{workflow.input.topic}}',
                    'depth': 'comprehensive'
                },
                'output': 'researchData'
            },
            {
                'id': 'analyze',
                'name': '分析階段',
                'type': 'agent',
                'agent': 'data-analyst',
                'input': {
                    'data': '{{steps.research.output}}'
                },
                'output': 'analysis'
            },
            {
                'id': 'write-draft',
                'name': '撰寫草稿',
                'type': 'agent',
                'agent': 'writer',
                'input': {
                    'research': '{{steps.research.output}}',
                    'analysis': '{{steps.analyze.output}}',
                    'style': '{{workflow.input.style || "professional"}}'
                },
                'output': 'draft'
            },
            {
                'id': 'review',
                'name': '審核',
                'type': 'agent',
                'agent': 'reviewer',
                'input': {
                    'draft': '{{steps.write-draft.output}}',
                    'criteria': ['accuracy', 'clarity', 'completeness']
                },
                'output': 'review'
            },
            {
                'id': 'revise',
                'name': '修訂',
                'type': 'agent',
                'agent': 'writer',
                'condition': '{{!steps.review.output.approved}}',
                'input': {
                    'draft': '{{steps.write-draft.output}}',
                    'feedback': '{{steps.review.output.feedback}}'
                },
                'output': 'revisedDraft'
            },
            {
                'id': 'finalize',
                'name': '最終確定',
                'type': 'function',
                'function': 'finalize Report',
                'input': {
                    'content': '{{steps.revise.output || steps.write-draft.output}}'
                },
                'output': 'finalReport'
            }
        ]
    }

    result = workflow_client.create_workflow(config)
    print(f"\n工作流創建結果: {json.dumps(result, indent=2, ensure_ascii=False)}")


def example_8_workflow_best_practices():
    """示例 8：工作流設計最佳實踐"""
    print("\n" + "=" * 60)
    print("示例 8：工作流設計最佳實踐")
    print("=" * 60)

    print("""
    📋 工作流設計最佳實踐

    1. 模塊化設計
       ✅ 將複雜流程分解為小步驟
       ✅ 每個步驟專注單一職責
       ✅ 使用清晰的步驟命名

    2. 錯誤處理
       ✅ 為關鍵步驟設置重試機制
       ✅ 提供降級方案
       ✅ 記錄所有錯誤

    3. 性能優化
       ✅ 識別可並行執行的步驟
       ✅ 設置合理的超時時間
       ✅ 使用緩存減少重複計算

    4. 可觀測性
       ✅ 記錄每個步驟的輸入輸出
       ✅ 追蹤執行時間
       ✅ 監控失敗率

    5. 可維護性
       ✅ 使用變量而不是硬編碼
       ✅ 添加詳細的描述和註釋
       ✅ 版本控制工作流定義

    6. 測試策略
       ✅ 單元測試各個步驟
       ✅ 集成測試完整流程
       ✅ 測試錯誤處理路徑

    7. 安全性
       ✅ 敏感數據加密
       ✅ 使用密鑰管理服務
       ✅ 限制工作流訪問權限
    """)


def main():
    """主函數"""
    print("\n⚙️  Mastra 工作流定義示例\n")

    try:
        example_1_sequential_workflow()
        example_2_parallel_workflow()
        example_3_conditional_workflow()
        example_4_loop_workflow()
        example_5_error_handling_workflow()
        example_6_human_in_loop_workflow()
        example_7_multi_agent_workflow()
        example_8_workflow_best_practices()

        print("\n" + "=" * 60)
        print("✅ 所有示例運行完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 錯誤: {e}")


if __name__ == "__main__":
    main()

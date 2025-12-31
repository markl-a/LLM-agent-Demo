"""
Mastra 工具整合示例

本示例展示如何創建和使用工具，以及如何整合第三方服務。

功能：
1. 自定義工具創建
2. 內建工具使用
3. 第三方服務整合
4. 工具鏈組合
5. 工具權限管理
"""

import os
import requests
from typing import Dict, Any, List, Optional, Callable
from dotenv import load_dotenv
import json
from datetime import datetime
import re

load_dotenv()


class MastraToolManager:
    """Mastra 工具管理器"""

    def __init__(self, api_url: str = None):
        """初始化工具管理器"""
        self.api_url = api_url or os.getenv('MASTRA_API_URL', 'http://localhost:3000')
        self.api_key = os.getenv('MASTRA_API_KEY')

        self.headers = {
            'Content-Type': 'application/json',
        }
        if self.api_key:
            self.headers['Authorization'] = f'Bearer {self.api_key}'

    def register_tool(self, tool_config: Dict[str, Any]) -> Dict[str, Any]:
        """註冊工具"""
        try:
            response = requests.post(
                f'{self.api_url}/api/tools',
                headers=self.headers,
                json=tool_config,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}

    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """執行工具"""
        try:
            response = requests.post(
                f'{self.api_url}/api/tools/{tool_name}/execute',
                headers=self.headers,
                json=parameters,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}


def example_1_simple_tool():
    """示例 1：創建簡單工具"""
    print("=" * 60)
    print("示例 1：創建簡單工具 - 計算器")
    print("=" * 60)

    tool_manager = MastraToolManager()

    # 定義計算器工具
    calculator_tool = {
        'name': 'calculator',
        'description': '執行基本數學計算',
        'parameters': {
            'type': 'object',
            'properties': {
                'operation': {
                    'type': 'string',
                    'enum': ['add', 'subtract', 'multiply', 'divide'],
                    'description': '要執行的運算'
                },
                'a': {
                    'type': 'number',
                    'description': '第一個數字'
                },
                'b': {
                    'type': 'number',
                    'description': '第二個數字'
                }
            },
            'required': ['operation', 'a', 'b']
        },
        'implementation': {
            'type': 'function',
            'code': '''
                function execute({ operation, a, b }) {
                    switch (operation) {
                        case 'add': return a + b;
                        case 'subtract': return a - b;
                        case 'multiply': return a * b;
                        case 'divide': return b !== 0 ? a / b : 'Error: Division by zero';
                        default: return 'Error: Unknown operation';
                    }
                }
            '''
        }
    }

    result = tool_manager.register_tool(calculator_tool)
    print(f"\n工具註冊結果: {json.dumps(result, indent=2, ensure_ascii=False)}")

    # 使用工具
    print("\n測試計算器工具:")
    test_cases = [
        {'operation': 'add', 'a': 10, 'b': 5},
        {'operation': 'multiply', 'a': 7, 'b': 8},
        {'operation': 'divide', 'a': 100, 'b': 4},
    ]

    for params in test_cases:
        result = tool_manager.execute_tool('calculator', params)
        print(f"  {params['a']} {params['operation']} {params['b']} = {result.get('result', 'error')}")


def example_2_web_scraper_tool():
    """示例 2：網頁抓取工具"""
    print("\n" + "=" * 60)
    print("示例 2：網頁抓取工具")
    print("=" * 60)

    tool_manager = MastraToolManager()

    web_scraper_tool = {
        'name': 'web_scraper',
        'description': '從網頁提取內容',
        'parameters': {
            'type': 'object',
            'properties': {
                'url': {
                    'type': 'string',
                    'description': '要抓取的 URL'
                },
                'selector': {
                    'type': 'string',
                    'description': 'CSS 選擇器（可選）',
                    'default': 'body'
                },
                'extract': {
                    'type': 'string',
                    'enum': ['text', 'html', 'links'],
                    'description': '提取類型',
                    'default': 'text'
                }
            },
            'required': ['url']
        },
        'implementation': {
            'type': 'function',
            'dependencies': ['axios', 'cheerio'],
            'code': '''
                async function execute({ url, selector = 'body', extract = 'text' }) {
                    const axios = require('axios');
                    const cheerio = require('cheerio');

                    try {
                        const response = await axios.get(url);
                        const $ = cheerio.load(response.data);
                        const element = $(selector);

                        switch (extract) {
                            case 'text':
                                return element.text().trim();
                            case 'html':
                                return element.html();
                            case 'links':
                                const links = [];
                                element.find('a').each((i, el) => {
                                    links.push({
                                        text: $(el).text(),
                                        href: $(el).attr('href')
                                    });
                                });
                                return links;
                            default:
                                return element.text();
                        }
                    } catch (error) {
                        return { error: error.message };
                    }
                }
            '''
        },
        'rateLimit': {
            'maxRequests': 10,
            'perMinutes': 1
        }
    }

    result = tool_manager.register_tool(web_scraper_tool)
    print(f"\n工具註冊結果: {json.dumps(result, indent=2, ensure_ascii=False)}")


def example_3_database_tool():
    """示例 3：數據庫查詢工具"""
    print("\n" + "=" * 60)
    print("示例 3：數據庫查詢工具")
    print("=" * 60)

    tool_manager = MastraToolManager()

    database_tool = {
        'name': 'database_query',
        'description': '執行數據庫查詢（僅限 SELECT）',
        'parameters': {
            'type': 'object',
            'properties': {
                'query': {
                    'type': 'string',
                    'description': 'SQL 查詢語句'
                },
                'database': {
                    'type': 'string',
                    'description': '數據庫名稱',
                    'default': 'main'
                },
                'limit': {
                    'type': 'number',
                    'description': '結果數量限制',
                    'default': 100,
                    'maximum': 1000
                }
            },
            'required': ['query']
        },
        'implementation': {
            'type': 'integration',
            'integration': 'postgresql',
            'config': {
                'connectionString': '{{env.DATABASE_URL}}',
                'ssl': true
            },
            'validation': {
                'allowedOperations': ['SELECT'],  # 僅允許查詢
                'preventSQLInjection': true
            }
        },
        'security': {
            'requiresAuth': true,
            'permissions': ['read:database']
        }
    }

    result = tool_manager.register_tool(database_tool)
    print(f"\n工具註冊結果: {json.dumps(result, indent=2, ensure_ascii=False)}")


def example_4_email_tool():
    """示例 4：郵件發送工具"""
    print("\n" + "=" * 60)
    print("示例 4：郵件發送工具")
    print("=" * 60)

    tool_manager = MastraToolManager()

    email_tool = {
        'name': 'send_email',
        'description': '發送電子郵件',
        'parameters': {
            'type': 'object',
            'properties': {
                'to': {
                    'type': 'string',
                    'description': '收件人郵箱'
                },
                'subject': {
                    'type': 'string',
                    'description': '郵件主題'
                },
                'body': {
                    'type': 'string',
                    'description': '郵件內容'
                },
                'template': {
                    'type': 'string',
                    'description': '郵件模板（可選）'
                },
                'attachments': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'filename': {'type': 'string'},
                            'content': {'type': 'string'},
                            'contentType': {'type': 'string'}
                        }
                    },
                    'description': '附件列表（可選）'
                }
            },
            'required': ['to', 'subject', 'body']
        },
        'implementation': {
            'type': 'integration',
            'integration': 'sendgrid',
            'config': {
                'apiKey': '{{env.SENDGRID_API_KEY}}',
                'from': '{{env.SENDGRID_FROM_EMAIL}}'
            }
        },
        'rateLimit': {
            'maxRequests': 100,
            'perHour': 1
        }
    }

    result = tool_manager.register_tool(email_tool)
    print(f"\n工具註冊結果: {json.dumps(result, indent=2, ensure_ascii=False)}")


def example_5_slack_integration():
    """示例 5：Slack 整合工具"""
    print("\n" + "=" * 60)
    print("示例 5：Slack 整合工具")
    print("=" * 60)

    tool_manager = MastraToolManager()

    slack_tools = [
        {
            'name': 'slack_post_message',
            'description': '發送 Slack 消息',
            'parameters': {
                'type': 'object',
                'properties': {
                    'channel': {
                        'type': 'string',
                        'description': '頻道 ID 或名稱'
                    },
                    'text': {
                        'type': 'string',
                        'description': '消息內容'
                    },
                    'blocks': {
                        'type': 'array',
                        'description': 'Slack Block Kit 格式的消息（可選）'
                    },
                    'thread_ts': {
                        'type': 'string',
                        'description': '回覆串時間戳（可選）'
                    }
                },
                'required': ['channel', 'text']
            },
            'implementation': {
                'type': 'integration',
                'integration': 'slack',
                'action': 'chat.postMessage',
                'config': {
                    'token': '{{env.SLACK_BOT_TOKEN}}'
                }
            }
        },
        {
            'name': 'slack_create_channel',
            'description': '創建 Slack 頻道',
            'parameters': {
                'type': 'object',
                'properties': {
                    'name': {
                        'type': 'string',
                        'description': '頻道名稱'
                    },
                    'is_private': {
                        'type': 'boolean',
                        'description': '是否為私有頻道',
                        'default': false
                    },
                    'description': {
                        'type': 'string',
                        'description': '頻道描述（可選）'
                    }
                },
                'required': ['name']
            },
            'implementation': {
                'type': 'integration',
                'integration': 'slack',
                'action': 'conversations.create'
            }
        },
        {
            'name': 'slack_add_reaction',
            'description': '添加 emoji 反應',
            'parameters': {
                'type': 'object',
                'properties': {
                    'channel': {
                        'type': 'string',
                        'description': '頻道 ID'
                    },
                    'timestamp': {
                        'type': 'string',
                        'description': '消息時間戳'
                    },
                    'name': {
                        'type': 'string',
                        'description': 'Emoji 名稱（不含冒號）'
                    }
                },
                'required': ['channel', 'timestamp', 'name']
            },
            'implementation': {
                'type': 'integration',
                'integration': 'slack',
                'action': 'reactions.add'
            }
        }
    ]

    for tool in slack_tools:
        result = tool_manager.register_tool(tool)
        print(f"\n註冊 {tool['name']}: {result.get('status', 'error')}")


def example_6_file_operations_tool():
    """示例 6：文件操作工具"""
    print("\n" + "=" * 60)
    print("示例 6：文件操作工具")
    print("=" * 60)

    tool_manager = MastraToolManager()

    file_tools = [
        {
            'name': 'read_file',
            'description': '讀取文件內容',
            'parameters': {
                'type': 'object',
                'properties': {
                    'path': {
                        'type': 'string',
                        'description': '文件路徑'
                    },
                    'encoding': {
                        'type': 'string',
                        'description': '文件編碼',
                        'default': 'utf-8'
                    }
                },
                'required': ['path']
            },
            'security': {
                'allowedPaths': ['/data/', '/uploads/'],  # 限制訪問路徑
                'requiresAuth': true
            }
        },
        {
            'name': 'write_file',
            'description': '寫入文件',
            'parameters': {
                'type': 'object',
                'properties': {
                    'path': {
                        'type': 'string',
                        'description': '文件路徑'
                    },
                    'content': {
                        'type': 'string',
                        'description': '文件內容'
                    },
                    'encoding': {
                        'type': 'string',
                        'default': 'utf-8'
                    },
                    'mode': {
                        'type': 'string',
                        'enum': ['overwrite', 'append'],
                        'default': 'overwrite'
                    }
                },
                'required': ['path', 'content']
            },
            'security': {
                'allowedPaths': ['/data/', '/uploads/'],
                'requiresAuth': true,
                'permissions': ['write:files']
            }
        },
        {
            'name': 'list_files',
            'description': '列出目錄文件',
            'parameters': {
                'type': 'object',
                'properties': {
                    'path': {
                        'type': 'string',
                        'description': '目錄路徑'
                    },
                    'pattern': {
                        'type': 'string',
                        'description': '文件名模式（glob）'
                    },
                    'recursive': {
                        'type': 'boolean',
                        'description': '是否遞歸',
                        'default': false
                    }
                },
                'required': ['path']
            }
        }
    ]

    for tool in file_tools:
        result = tool_manager.register_tool(tool)
        print(f"\n註冊 {tool['name']}: {result.get('status', 'error')}")


def example_7_api_integration_tool():
    """示例 7：通用 API 調用工具"""
    print("\n" + "=" * 60)
    print("示例 7：通用 API 調用工具")
    print("=" * 60)

    tool_manager = MastraToolManager()

    api_tool = {
        'name': 'api_call',
        'description': '調用外部 API',
        'parameters': {
            'type': 'object',
            'properties': {
                'url': {
                    'type': 'string',
                    'description': 'API URL'
                },
                'method': {
                    'type': 'string',
                    'enum': ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
                    'default': 'GET'
                },
                'headers': {
                    'type': 'object',
                    'description': '請求頭'
                },
                'body': {
                    'type': 'object',
                    'description': '請求體（JSON）'
                },
                'auth': {
                    'type': 'object',
                    'properties': {
                        'type': {
                            'type': 'string',
                            'enum': ['bearer', 'basic', 'apikey']
                        },
                        'token': {'type': 'string'}
                    }
                },
                'timeout': {
                    'type': 'number',
                    'description': '超時時間（毫秒）',
                    'default': 30000
                }
            },
            'required': ['url']
        },
        'implementation': {
            'type': 'function',
            'code': '''
                async function execute({ url, method = 'GET', headers = {}, body, auth, timeout = 30000 }) {
                    const axios = require('axios');

                    const config = {
                        url,
                        method,
                        headers,
                        timeout
                    };

                    if (body) {
                        config.data = body;
                    }

                    if (auth) {
                        if (auth.type === 'bearer') {
                            config.headers.Authorization = `Bearer ${auth.token}`;
                        } else if (auth.type === 'apikey') {
                            config.headers['X-API-Key'] = auth.token;
                        }
                    }

                    try {
                        const response = await axios(config);
                        return {
                            status: response.status,
                            data: response.data,
                            headers: response.headers
                        };
                    } catch (error) {
                        return {
                            error: error.message,
                            status: error.response?.status
                        };
                    }
                }
            '''
        },
        'rateLimit': {
            'maxRequests': 60,
            'perMinutes': 1
        }
    }

    result = tool_manager.register_tool(api_tool)
    print(f"\n工具註冊結果: {json.dumps(result, indent=2, ensure_ascii=False)}")


def example_8_tool_chain():
    """示例 8：工具鏈組合"""
    print("\n" + "=" * 60)
    print("示例 8：工具鏈組合 - 搜索並總結")
    print("=" * 60)

    # 這展示如何在 Agent 中組合多個工具
    tool_chain_config = {
        'name': 'research-assistant',
        'description': '研究助手（組合多個工具）',
        'tools': [
            'web_scraper',      # 抓取網頁
            'database_query',   # 查詢數據庫
            'api_call',         # 調用 API
        ],
        'workflow': {
            'name': 'research_and_summarize',
            'steps': [
                {
                    'id': 'search',
                    'tool': 'web_scraper',
                    'description': '搜索相關信息'
                },
                {
                    'id': 'analyze',
                    'agent': 'analyzer',
                    'description': '分析搜索結果'
                },
                {
                    'id': 'summarize',
                    'agent': 'summarizer',
                    'description': '生成摘要'
                },
                {
                    'id': 'save',
                    'tool': 'database_query',
                    'description': '保存結果'
                }
            ]
        }
    }

    print(f"\n工具鏈配置: {json.dumps(tool_chain_config, indent=2, ensure_ascii=False)}")


def example_9_tool_permissions():
    """示例 9：工具權限管理"""
    print("\n" + "=" * 60)
    print("示例 9：工具權限管理")
    print("=" * 60)

    print("""
    🔒 工具權限管理最佳實踐

    1. 最小權限原則
       ✅ 只授予必要的權限
       ✅ 使用細粒度權限控制
       ✅ 定期審核權限

    2. 安全配置
       ✅ 敏感操作需要身份驗證
       ✅ 使用環境變量存儲密鑰
       ✅ 限制訪問路徑和資源

    3. 速率限制
       ✅ 防止濫用
       ✅ 保護外部 API 配額
       ✅ 設置合理的限制

    4. 輸入驗證
       ✅ 驗證所有輸入參數
       ✅ 防止注入攻擊
       ✅ 清理用戶輸入

    5. 審計日誌
       ✅ 記錄所有工具調用
       ✅ 追蹤誰、何時、做了什麼
       ✅ 異常行為告警

    權限示例：
    {
        "security": {
            "requiresAuth": true,
            "permissions": ["read:files", "write:files"],
            "allowedPaths": ["/data/", "/uploads/"],
            "rateLimit": {
                "maxRequests": 100,
                "perHour": 1
            },
            "validation": {
                "preventSQLInjection": true,
                "sanitizeInput": true
            },
            "audit": {
                "logAllCalls": true,
                "alertOnFailure": true
            }
        }
    }
    """)


def example_10_integration_catalog():
    """示例 10：常用整合目錄"""
    print("\n" + "=" * 60)
    print("示例 10：Mastra 常用整合目錄")
    print("=" * 60)

    integrations_catalog = {
        '通訊': [
            'Slack', 'Discord', 'Telegram', 'WhatsApp', 'Microsoft Teams'
        ],
        'CRM': [
            'Salesforce', 'HubSpot', 'Zoho CRM', 'Pipedrive', 'Close'
        ],
        '數據庫': [
            'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Supabase'
        ],
        '向量數據庫': [
            'Pinecone', 'Weaviate', 'Qdrant', 'Chroma', 'Milvus'
        ],
        '郵件': [
            'SendGrid', 'Mailgun', 'Gmail', 'Outlook', 'Postmark'
        ],
        '文檔': [
            'Google Docs', 'Notion', 'Confluence', 'Dropbox', 'Google Drive'
        ],
        '開發工具': [
            'GitHub', 'GitLab', 'Jira', 'Linear', 'Sentry'
        ],
        '支付': [
            'Stripe', 'PayPal', 'Square', 'Braintree'
        ],
        '分析': [
            'Google Analytics', 'Mixpanel', 'Amplitude', 'Segment'
        ],
        '搜索': [
            'Algolia', 'Elasticsearch', 'Typesense', 'MeiliSearch'
        ],
        'AI/ML': [
            'OpenAI', 'Anthropic', 'Cohere', 'Hugging Face', 'Replicate'
        ],
        '社交媒體': [
            'Twitter/X', 'LinkedIn', 'Facebook', 'Instagram'
        ],
        '自動化': [
            'Zapier', 'Make', 'n8n', 'Pipedream'
        ],
        '客服': [
            'Zendesk', 'Intercom', 'Freshdesk', 'Help Scout'
        ],
        '電商': [
            'Shopify', 'WooCommerce', 'BigCommerce', 'Magento'
        ]
    }

    print("\n📚 Mastra 支持的整合服務：\n")
    for category, services in integrations_catalog.items():
        print(f"{category}:")
        for service in services:
            print(f"  • {service}")
        print()


def main():
    """主函數"""
    print("\n🔧 Mastra 工具整合示例\n")

    try:
        example_1_simple_tool()
        example_2_web_scraper_tool()
        example_3_database_tool()
        example_4_email_tool()
        example_5_slack_integration()
        example_6_file_operations_tool()
        example_7_api_integration_tool()
        example_8_tool_chain()
        example_9_tool_permissions()
        example_10_integration_catalog()

        print("\n" + "=" * 60)
        print("✅ 所有示例運行完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 錯誤: {e}")


if __name__ == "__main__":
    main()

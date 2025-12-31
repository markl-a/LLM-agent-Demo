"""
n8n 數據轉換
============

本範例展示如何在 n8n 中進行數據處理和轉換，包括：
- Set 節點設置數據
- Code 節點自定義處理
- Function 節點編寫函數
- 數據映射和過濾
- JSON 處理

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


class N8NDataTransformer:
    """
    n8n 數據轉換工具

    創建包含各種數據處理節點的工作流
    """

    def __init__(self, base_url: str = "http://localhost:5678", api_key: Optional[str] = None):
        """初始化數據轉換工具"""
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key or os.getenv("N8N_API_KEY")

        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({
                "X-N8N-API-KEY": self.api_key,
                "Content-Type": "application/json"
            })

        print(f"✓ n8n 數據轉換工具已初始化")

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

    def example_1_create_set_node_workflow(
        self,
        workflow_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        示例 1: 使用 Set 節點設置數據

        Set 節點用於設置變量和轉換數據結構

        參數:
            workflow_name: 工作流名稱

        返回:
            創建的工作流對象
        """
        print("\n" + "="*60)
        print("示例 1: 使用 Set 節點設置數據")
        print("="*60)

        try:
            workflow_data = {
                "name": workflow_name,
                "active": True,
                "nodes": [
                    {
                        "parameters": {
                            "httpMethod": "POST",
                            "path": "data-transform",
                            "responseMode": "lastNode"
                        },
                        "name": "Webhook",
                        "type": "n8n-nodes-base.webhook",
                        "typeVersion": 1,
                        "position": [250, 300]
                    },
                    {
                        "parameters": {
                            "mode": "manual",
                            "duplicateItem": False,
                            "assignments": {
                                "assignments": [
                                    {
                                        "id": "1",
                                        "name": "userId",
                                        "value": "={{ $json.id }}",
                                        "type": "string"
                                    },
                                    {
                                        "id": "2",
                                        "name": "fullName",
                                        "value": "={{ $json.firstName + ' ' + $json.lastName }}",
                                        "type": "string"
                                    },
                                    {
                                        "id": "3",
                                        "name": "isActive",
                                        "value": "={{ $json.status === 'active' }}",
                                        "type": "boolean"
                                    },
                                    {
                                        "id": "4",
                                        "name": "age",
                                        "value": "={{ $json.age }}",
                                        "type": "number"
                                    },
                                    {
                                        "id": "5",
                                        "name": "processedAt",
                                        "value": "={{ new Date().toISOString() }}",
                                        "type": "string"
                                    }
                                ]
                            }
                        },
                        "name": "Set User Data",
                        "type": "n8n-nodes-base.set",
                        "typeVersion": 3,
                        "position": [450, 300]
                    }
                ],
                "connections": {
                    "Webhook": {
                        "main": [
                            [
                                {
                                    "node": "Set User Data",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    }
                },
                "settings": {}
            }

            print(f"\n創建 Set 節點工作流: {workflow_name}")

            workflow = self._make_request("POST", "/api/v1/workflows", data=workflow_data)

            print(f"\n✓ 工作流創建成功")
            print(f"  ID: {workflow.get('id')}")
            print(f"  URL: {self.base_url}/webhook/data-transform")

            return workflow

        except Exception as e:
            print(f"\n✗ 創建失敗: {str(e)}")
            return None

    def example_2_create_code_node_workflow(
        self,
        workflow_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        示例 2: 使用 Code 節點進行複雜數據處理

        Code 節點支持 JavaScript 和 Python

        參數:
            workflow_name: 工作流名稱

        返回:
            創建的工作流對象
        """
        print("\n" + "="*60)
        print("示例 2: 使用 Code 節點進行複雜數據處理")
        print("="*60)

        # JavaScript 代碼示例
        js_code = """
// 處理輸入數據
const items = $input.all();

// 轉換數據
const transformed = items.map(item => {
  const data = item.json;

  return {
    json: {
      // 計算總價
      totalPrice: (data.quantity || 0) * (data.price || 0),

      // 格式化日期
      formattedDate: new Date(data.date).toLocaleDateString('zh-TW'),

      // 分類
      category: data.price > 1000 ? 'premium' : 'standard',

      // 添加元數據
      metadata: {
        processedAt: new Date().toISOString(),
        version: '1.0'
      },

      // 保留原始數據
      original: data
    }
  };
});

return transformed;
"""

        try:
            workflow_data = {
                "name": workflow_name,
                "active": True,
                "nodes": [
                    {
                        "parameters": {
                            "httpMethod": "POST",
                            "path": "code-transform",
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
                            "jsCode": js_code
                        },
                        "name": "Transform Data",
                        "type": "n8n-nodes-base.code",
                        "typeVersion": 2,
                        "position": [450, 300]
                    }
                ],
                "connections": {
                    "Webhook": {
                        "main": [
                            [
                                {
                                    "node": "Transform Data",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    }
                },
                "settings": {}
            }

            print(f"\n創建 Code 節點工作流: {workflow_name}")

            workflow = self._make_request("POST", "/api/v1/workflows", data=workflow_data)

            print(f"\n✓ 工作流創建成功")
            print(f"  ID: {workflow.get('id')}")
            print(f"  功能: 使用 JavaScript 進行複雜數據轉換")

            return workflow

        except Exception as e:
            print(f"\n✗ 創建失敗: {str(e)}")
            return None

    def example_3_create_filter_workflow(
        self,
        workflow_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        示例 3: 創建數據過濾工作流

        使用 Filter 節點過濾數據

        參數:
            workflow_name: 工作流名稱

        返回:
            創建的工作流對象
        """
        print("\n" + "="*60)
        print("示例 3: 創建數據過濾工作流")
        print("="*60)

        filter_code = """
// 過濾數據
const items = $input.all();

// 過濾條件：只保留價格大於 100 且狀態為 active 的項目
const filtered = items.filter(item => {
  const data = item.json;
  return (data.price || 0) > 100 && data.status === 'active';
});

// 排序：按價格降序
filtered.sort((a, b) => (b.json.price || 0) - (a.json.price || 0));

// 限制數量：只返回前 10 項
return filtered.slice(0, 10);
"""

        try:
            workflow_data = {
                "name": workflow_name,
                "active": True,
                "nodes": [
                    {
                        "parameters": {
                            "httpMethod": "POST",
                            "path": "filter-data",
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
                            "jsCode": filter_code
                        },
                        "name": "Filter and Sort",
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
                                        "name": "totalItems",
                                        "value": "={{ $items().length }}",
                                        "type": "number"
                                    },
                                    {
                                        "id": "2",
                                        "name": "filteredData",
                                        "value": "={{ $json }}",
                                        "type": "object"
                                    }
                                ]
                            }
                        },
                        "name": "Add Metadata",
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
                                    "node": "Filter and Sort",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    },
                    "Filter and Sort": {
                        "main": [
                            [
                                {
                                    "node": "Add Metadata",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    }
                },
                "settings": {}
            }

            print(f"\n創建數據過濾工作流: {workflow_name}")

            workflow = self._make_request("POST", "/api/v1/workflows", data=workflow_data)

            print(f"\n✓ 工作流創建成功")
            print(f"  ID: {workflow.get('id')}")
            print(f"  功能: 過濾、排序和限制數據")

            return workflow

        except Exception as e:
            print(f"\n✗ 創建失敗: {str(e)}")
            return None

    def example_4_create_aggregation_workflow(
        self,
        workflow_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        示例 4: 創建數據聚合工作流

        聚合和統計數據

        參數:
            workflow_name: 工作流名稱

        返回:
            創建的工作流對象
        """
        print("\n" + "="*60)
        print("示例 4: 創建數據聚合工作流")
        print("="*60)

        aggregation_code = """
// 數據聚合
const items = $input.all();

// 按類別分組
const grouped = {};
items.forEach(item => {
  const category = item.json.category || 'uncategorized';
  if (!grouped[category]) {
    grouped[category] = {
      items: [],
      totalPrice: 0,
      count: 0
    };
  }
  grouped[category].items.push(item.json);
  grouped[category].totalPrice += (item.json.price || 0);
  grouped[category].count += 1;
});

// 計算統計
const statistics = {
  totalItems: items.length,
  totalValue: items.reduce((sum, item) => sum + (item.json.price || 0), 0),
  averagePrice: items.length > 0
    ? items.reduce((sum, item) => sum + (item.json.price || 0), 0) / items.length
    : 0,
  categories: Object.keys(grouped).length,
  groupedData: grouped
};

return [{ json: statistics }];
"""

        try:
            workflow_data = {
                "name": workflow_name,
                "active": True,
                "nodes": [
                    {
                        "parameters": {
                            "httpMethod": "POST",
                            "path": "aggregate-data",
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
                            "jsCode": aggregation_code
                        },
                        "name": "Aggregate Statistics",
                        "type": "n8n-nodes-base.code",
                        "typeVersion": 2,
                        "position": [450, 300]
                    }
                ],
                "connections": {
                    "Webhook": {
                        "main": [
                            [
                                {
                                    "node": "Aggregate Statistics",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    }
                },
                "settings": {}
            }

            print(f"\n創建數據聚合工作流: {workflow_name}")

            workflow = self._make_request("POST", "/api/v1/workflows", data=workflow_data)

            print(f"\n✓ 工作流創建成功")
            print(f"  ID: {workflow.get('id')}")
            print(f"  功能: 分組、聚合和統計分析")

            return workflow

        except Exception as e:
            print(f"\n✗ 創建失敗: {str(e)}")
            return None

    def example_5_create_json_manipulation_workflow(
        self,
        workflow_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        示例 5: 創建 JSON 處理工作流

        深度處理 JSON 數據結構

        參數:
            workflow_name: 工作流名稱

        返回:
            創建的工作流對象
        """
        print("\n" + "="*60)
        print("示例 5: 創建 JSON 處理工作流")
        print("="*60)

        json_code = """
// JSON 深度處理
const items = $input.all();

const processed = items.map(item => {
  const data = item.json;

  // 扁平化嵌套對象
  function flattenObject(obj, prefix = '') {
    return Object.keys(obj).reduce((acc, key) => {
      const pre = prefix.length ? prefix + '.' : '';
      if (typeof obj[key] === 'object' && obj[key] !== null && !Array.isArray(obj[key])) {
        Object.assign(acc, flattenObject(obj[key], pre + key));
      } else {
        acc[pre + key] = obj[key];
      }
      return acc;
    }, {});
  }

  // 移除空值
  function removeEmpty(obj) {
    return Object.entries(obj).reduce((acc, [key, value]) => {
      if (value !== null && value !== undefined && value !== '') {
        acc[key] = value;
      }
      return acc;
    }, {});
  }

  // 處理數據
  const flattened = flattenObject(data);
  const cleaned = removeEmpty(flattened);

  return {
    json: {
      original: data,
      flattened: cleaned,
      metadata: {
        processedAt: new Date().toISOString(),
        fieldCount: Object.keys(cleaned).length
      }
    }
  };
});

return processed;
"""

        try:
            workflow_data = {
                "name": workflow_name,
                "active": True,
                "nodes": [
                    {
                        "parameters": {
                            "httpMethod": "POST",
                            "path": "json-process",
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
                            "jsCode": json_code
                        },
                        "name": "Process JSON",
                        "type": "n8n-nodes-base.code",
                        "typeVersion": 2,
                        "position": [450, 300]
                    }
                ],
                "connections": {
                    "Webhook": {
                        "main": [
                            [
                                {
                                    "node": "Process JSON",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    }
                },
                "settings": {}
            }

            print(f"\n創建 JSON 處理工作流: {workflow_name}")

            workflow = self._make_request("POST", "/api/v1/workflows", data=workflow_data)

            print(f"\n✓ 工作流創建成功")
            print(f"  ID: {workflow.get('id')}")
            print(f"  功能: JSON 扁平化、清理和轉換")

            return workflow

        except Exception as e:
            print(f"\n✗ 創建失敗: {str(e)}")
            return None


def main():
    """
    主函數：演示所有數據轉換示例
    """
    print("\n" + "="*60)
    print("n8n 數據轉換示例")
    print("="*60)

    # 配置參數
    BASE_URL = os.getenv("N8N_API_URL", "http://localhost:5678")
    API_KEY = os.getenv("N8N_API_KEY")

    # 初始化轉換工具
    transformer = N8NDataTransformer(base_url=BASE_URL, api_key=API_KEY)

    # 示例 1: Set 節點
    transformer.example_1_create_set_node_workflow(
        "Set Node Data Transform"
    )

    # 示例 2: Code 節點
    transformer.example_2_create_code_node_workflow(
        "Code Node Processing"
    )

    # 示例 3: 數據過濾
    transformer.example_3_create_filter_workflow(
        "Data Filter and Sort"
    )

    # 示例 4: 數據聚合
    transformer.example_4_create_aggregation_workflow(
        "Data Aggregation"
    )

    # 示例 5: JSON 處理
    transformer.example_5_create_json_manipulation_workflow(
        "JSON Processing"
    )

    print("\n" + "="*60)
    print("所有數據轉換示例創建完成！")
    print("="*60)


if __name__ == "__main__":
    main()

    print("\n" + "-"*60)
    print("數據轉換最佳實踐:")
    print("-"*60)
    print("""
    1. Set 節點
       - 用於簡單的數據映射
       - 支持表達式計算
       - 適合設置固定值
       - 性能較好

    2. Code 節點
       - 用於複雜邏輯
       - 支持 JavaScript/Python
       - 可以使用外部庫
       - 靈活性高

    3. 數據過濾
       - 盡早過濾數據
       - 減少後續處理量
       - 使用索引優化
       - 避免過度過濾

    4. 數據聚合
       - 合理分組
       - 選擇適當的聚合函數
       - 注意內存使用
       - 批次處理大數據

    5. JSON 處理
       - 驗證 JSON 格式
       - 處理嵌套結構
       - 移除無用字段
       - 保持數據一致性

    常用表達式:
    - {{ $json.field }}          : 訪問字段
    - {{ $json.field || 'default' }} : 默認值
    - {{ new Date().toISOString() }} : 當前時間
    - {{ Math.round($json.price) }}  : 數學運算
    - {{ $items().length }}          : 項目數量
    """)

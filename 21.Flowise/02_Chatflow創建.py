"""
Flowise Chatflow 創建與管理
===========================

本範例展示如何通過 API 創建、更新、刪除和管理 Chatflow。
雖然 Flowise 主要通過 UI 創建 Chatflow，但也可以通過 API 進行程式化管理。

安裝依賴:
pip install requests python-dotenv

作者: Flowise Demo
日期: 2025-12-15
"""

import os
import requests
import json
from typing import Dict, Any, Optional, List
from datetime import datetime


class FlowiseChatflowManager:
    """
    Flowise Chatflow 管理類

    提供 Chatflow 的 CRUD 操作和配置管理功能
    """

    def __init__(self, base_url: str = "http://localhost:3000", api_key: Optional[str] = None):
        """
        初始化 Chatflow 管理器

        參數:
            base_url: Flowise 服務器地址
            api_key: API 密鑰（如果需要）
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key or os.getenv("FLOWISE_API_KEY")

        print(f"✓ Chatflow 管理器已初始化")
        print(f"  服務器: {self.base_url}")

    def get_headers(self) -> Dict[str, str]:
        """獲取請求頭"""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def example_1_list_chatflows(self):
        """
        示例 1: 列出所有 Chatflow

        獲取服務器上所有可用的 Chatflow 列表
        """
        print("\n" + "="*60)
        print("示例 1: 列出所有 Chatflow")
        print("="*60)

        try:
            url = f"{self.base_url}/api/v1/chatflows"
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()

            chatflows = response.json()

            print(f"\n找到 {len(chatflows)} 個 Chatflow:\n")

            for i, flow in enumerate(chatflows, 1):
                print(f"{i}. 名稱: {flow.get('name', 'Unnamed')}")
                print(f"   ID: {flow.get('id')}")
                print(f"   類型: {flow.get('type', 'CHATFLOW')}")
                print(f"   類別: {flow.get('category', 'N/A')}")
                print(f"   創建時間: {flow.get('createdDate', 'N/A')}")
                print(f"   更新時間: {flow.get('updatedDate', 'N/A')}")
                print(f"   已部署: {'是' if flow.get('deployed') else '否'}")
                print()

            return chatflows

        except requests.exceptions.RequestException as e:
            print(f"✗ 錯誤: {str(e)}")
            return []

    def example_2_get_chatflow_details(self, chatflow_id: str):
        """
        示例 2: 獲取 Chatflow 詳細信息

        查詢特定 Chatflow 的完整配置和節點信息

        參數:
            chatflow_id: Chatflow ID
        """
        print("\n" + "="*60)
        print("示例 2: 獲取 Chatflow 詳細信息")
        print("="*60)

        try:
            url = f"{self.base_url}/api/v1/chatflows/{chatflow_id}"
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()

            chatflow = response.json()

            print(f"\nChatflow 詳細信息:")
            print(f"  名稱: {chatflow.get('name')}")
            print(f"  ID: {chatflow.get('id')}")
            print(f"  類型: {chatflow.get('type')}")

            # 解析流程數據
            flowData = chatflow.get('flowData')
            if flowData:
                if isinstance(flowData, str):
                    flowData = json.loads(flowData)

                nodes = flowData.get('nodes', [])
                edges = flowData.get('edges', [])

                print(f"\n  節點數量: {len(nodes)}")
                print(f"  連接數量: {len(edges)}")

                print("\n  節點列表:")
                for node in nodes:
                    node_data = node.get('data', {})
                    print(f"    - {node_data.get('label', 'Unknown')} ({node_data.get('name', 'N/A')})")

            return chatflow

        except requests.exceptions.RequestException as e:
            print(f"✗ 錯誤: {str(e)}")
            return None

    def example_3_create_simple_chatflow(self, name: str, description: str = ""):
        """
        示例 3: 創建簡單的 Chatflow

        通過 API 創建一個基礎的 Chatflow 配置

        參數:
            name: Chatflow 名稱
            description: Chatflow 描述
        """
        print("\n" + "="*60)
        print("示例 3: 創建簡單的 Chatflow")
        print("="*60)

        try:
            # 定義一個簡單的 Chatflow 結構
            # 包含 ChatOpenAI + ConversationChain
            flowData = {
                "nodes": [
                    {
                        "id": "chatOpenAI_0",
                        "position": {"x": 400, "y": 100},
                        "type": "customNode",
                        "data": {
                            "id": "chatOpenAI_0",
                            "label": "ChatOpenAI",
                            "name": "chatOpenAI",
                            "type": "ChatOpenAI",
                            "baseClasses": ["ChatOpenAI", "BaseChatModel"],
                            "category": "Chat Models",
                            "inputParams": [
                                {
                                    "label": "Model Name",
                                    "name": "modelName",
                                    "type": "options",
                                    "options": [
                                        {"label": "gpt-4", "name": "gpt-4"},
                                        {"label": "gpt-3.5-turbo", "name": "gpt-3.5-turbo"}
                                    ],
                                    "default": "gpt-3.5-turbo"
                                },
                                {
                                    "label": "Temperature",
                                    "name": "temperature",
                                    "type": "number",
                                    "default": 0.9
                                }
                            ],
                            "inputs": {
                                "modelName": "gpt-3.5-turbo",
                                "temperature": 0.7
                            }
                        }
                    },
                    {
                        "id": "conversationChain_0",
                        "position": {"x": 800, "y": 100},
                        "type": "customNode",
                        "data": {
                            "id": "conversationChain_0",
                            "label": "Conversation Chain",
                            "name": "conversationChain",
                            "type": "ConversationChain",
                            "baseClasses": ["ConversationChain"],
                            "category": "Chains",
                            "inputs": {}
                        }
                    }
                ],
                "edges": [
                    {
                        "source": "chatOpenAI_0",
                        "sourceHandle": "chatOpenAI_0-output-chatOpenAI-ChatOpenAI",
                        "target": "conversationChain_0",
                        "targetHandle": "conversationChain_0-input-model-BaseChatModel",
                        "type": "buttonedge",
                        "id": "chatOpenAI_0-chatOpenAI_0-output-chatOpenAI-ChatOpenAI-conversationChain_0-conversationChain_0-input-model-BaseChatModel"
                    }
                ]
            }

            # 準備創建請求
            payload = {
                "name": name,
                "description": description,
                "flowData": json.dumps(flowData),
                "deployed": False,
                "type": "CHATFLOW"
            }

            url = f"{self.base_url}/api/v1/chatflows"
            response = requests.post(
                url,
                json=payload,
                headers=self.get_headers()
            )
            response.raise_for_status()

            new_chatflow = response.json()

            print(f"\n✓ Chatflow 創建成功!")
            print(f"  名稱: {new_chatflow.get('name')}")
            print(f"  ID: {new_chatflow.get('id')}")
            print(f"\n提示: 你可以在 Flowise UI 中進一步編輯這個 Chatflow")
            print(f"URL: {self.base_url}/chatflow/{new_chatflow.get('id')}")

            return new_chatflow

        except requests.exceptions.RequestException as e:
            print(f"✗ 錯誤: {str(e)}")
            if hasattr(e.response, 'text'):
                print(f"詳細錯誤: {e.response.text}")
            return None

    def example_4_update_chatflow(self, chatflow_id: str, updates: Dict[str, Any]):
        """
        示例 4: 更新 Chatflow

        修改現有 Chatflow 的配置

        參數:
            chatflow_id: Chatflow ID
            updates: 要更新的字段
        """
        print("\n" + "="*60)
        print("示例 4: 更新 Chatflow")
        print("="*60)

        try:
            # 首先獲取當前配置
            url = f"{self.base_url}/api/v1/chatflows/{chatflow_id}"
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()

            current = response.json()

            # 合併更新
            updated_data = {**current, **updates}

            # 發送更新請求
            response = requests.put(
                url,
                json=updated_data,
                headers=self.get_headers()
            )
            response.raise_for_status()

            updated_chatflow = response.json()

            print(f"\n✓ Chatflow 更新成功!")
            print(f"  ID: {chatflow_id}")
            print(f"\n更新的字段:")
            for key, value in updates.items():
                print(f"  {key}: {value}")

            return updated_chatflow

        except requests.exceptions.RequestException as e:
            print(f"✗ 錯誤: {str(e)}")
            return None

    def example_5_delete_chatflow(self, chatflow_id: str):
        """
        示例 5: 刪除 Chatflow

        從服務器刪除指定的 Chatflow

        參數:
            chatflow_id: Chatflow ID
        """
        print("\n" + "="*60)
        print("示例 5: 刪除 Chatflow")
        print("="*60)

        try:
            url = f"{self.base_url}/api/v1/chatflows/{chatflow_id}"

            # 確認刪除
            print(f"\n警告: 即將刪除 Chatflow: {chatflow_id}")
            print("這個操作不可逆！")

            response = requests.delete(url, headers=self.get_headers())
            response.raise_for_status()

            print(f"\n✓ Chatflow 已刪除")

            return True

        except requests.exceptions.RequestException as e:
            print(f"✗ 錯誤: {str(e)}")
            return False

    def example_6_export_chatflow(self, chatflow_id: str, output_file: str):
        """
        示例 6: 導出 Chatflow 配置

        將 Chatflow 配置導出為 JSON 文件

        參數:
            chatflow_id: Chatflow ID
            output_file: 輸出文件路徑
        """
        print("\n" + "="*60)
        print("示例 6: 導出 Chatflow 配置")
        print("="*60)

        try:
            # 獲取 Chatflow 數據
            chatflow = self.example_2_get_chatflow_details(chatflow_id)

            if chatflow:
                # 導出為 JSON
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(chatflow, f, indent=2, ensure_ascii=False)

                print(f"\n✓ Chatflow 已導出到: {output_file}")
                print(f"  文件大小: {os.path.getsize(output_file)} 字節")

                return True

        except Exception as e:
            print(f"✗ 錯誤: {str(e)}")
            return False

    def example_7_import_chatflow(self, input_file: str):
        """
        示例 7: 導入 Chatflow 配置

        從 JSON 文件導入 Chatflow

        參數:
            input_file: 輸入文件路徑
        """
        print("\n" + "="*60)
        print("示例 7: 導入 Chatflow 配置")
        print("="*60)

        try:
            # 讀取 JSON 文件
            with open(input_file, 'r', encoding='utf-8') as f:
                chatflow_data = json.load(f)

            # 移除 ID 和時間戳（讓系統生成新的）
            if 'id' in chatflow_data:
                del chatflow_data['id']
            if 'createdDate' in chatflow_data:
                del chatflow_data['createdDate']
            if 'updatedDate' in chatflow_data:
                del chatflow_data['updatedDate']

            # 添加導入標記
            chatflow_data['name'] = f"{chatflow_data.get('name', 'Imported')} (導入)"

            # 創建新的 Chatflow
            url = f"{self.base_url}/api/v1/chatflows"
            response = requests.post(
                url,
                json=chatflow_data,
                headers=self.get_headers()
            )
            response.raise_for_status()

            new_chatflow = response.json()

            print(f"\n✓ Chatflow 導入成功!")
            print(f"  名稱: {new_chatflow.get('name')}")
            print(f"  新 ID: {new_chatflow.get('id')}")

            return new_chatflow

        except Exception as e:
            print(f"✗ 錯誤: {str(e)}")
            return None

    def example_8_clone_chatflow(self, chatflow_id: str, new_name: str):
        """
        示例 8: 克隆 Chatflow

        複製現有的 Chatflow 創建新副本

        參數:
            chatflow_id: 源 Chatflow ID
            new_name: 新 Chatflow 名稱
        """
        print("\n" + "="*60)
        print("示例 8: 克隆 Chatflow")
        print("="*60)

        try:
            # 獲取源 Chatflow
            url = f"{self.base_url}/api/v1/chatflows/{chatflow_id}"
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()

            source = response.json()

            # 準備克隆數據
            clone_data = {
                "name": new_name,
                "description": f"克隆自: {source.get('name')}",
                "flowData": source.get('flowData'),
                "deployed": False,
                "type": source.get('type', 'CHATFLOW'),
                "category": source.get('category')
            }

            # 創建克隆
            url = f"{self.base_url}/api/v1/chatflows"
            response = requests.post(
                url,
                json=clone_data,
                headers=self.get_headers()
            )
            response.raise_for_status()

            cloned = response.json()

            print(f"\n✓ Chatflow 克隆成功!")
            print(f"  源 ID: {chatflow_id}")
            print(f"  新 ID: {cloned.get('id')}")
            print(f"  新名稱: {cloned.get('name')}")

            return cloned

        except requests.exceptions.RequestException as e:
            print(f"✗ 錯誤: {str(e)}")
            return None


def main():
    """
    主函數：演示 Chatflow 管理示例
    """
    print("\n" + "="*60)
    print("Flowise Chatflow 創建與管理示例")
    print("="*60)

    # 配置
    BASE_URL = os.getenv("FLOWISE_BASE_URL", "http://localhost:3000")
    API_KEY = os.getenv("FLOWISE_API_KEY")

    # 初始化管理器
    manager = FlowiseChatflowManager(base_url=BASE_URL, api_key=API_KEY)

    # 示例 1: 列出所有 Chatflow
    chatflows = manager.example_1_list_chatflows()

    # 如果有 Chatflow，執行其他示例
    if chatflows:
        first_chatflow_id = chatflows[0].get('id')

        # 示例 2: 獲取詳細信息
        manager.example_2_get_chatflow_details(first_chatflow_id)

        # 示例 6: 導出 Chatflow
        export_file = "/tmp/chatflow_export.json"
        manager.example_6_export_chatflow(first_chatflow_id, export_file)

        # 示例 8: 克隆 Chatflow
        manager.example_8_clone_chatflow(
            first_chatflow_id,
            f"克隆 - {chatflows[0].get('name')}"
        )

    # 示例 3: 創建新 Chatflow
    new_chatflow = manager.example_3_create_simple_chatflow(
        name="API 創建的測試 Chatflow",
        description="這是通過 Python API 創建的示例 Chatflow"
    )

    # 如果創建成功，執行更新和刪除示例
    if new_chatflow:
        new_id = new_chatflow.get('id')

        # 示例 4: 更新 Chatflow
        manager.example_4_update_chatflow(
            new_id,
            {
                "name": "API 創建的測試 Chatflow（已更新）",
                "description": "描述已更新"
            }
        )

        # 注意: 實際使用時可能不想立即刪除
        # 示例 5: 刪除 Chatflow
        # manager.example_5_delete_chatflow(new_id)

    print("\n" + "="*60)
    print("Chatflow 管理示例完成！")
    print("="*60)


if __name__ == "__main__":
    main()

    # 使用說明
    print("\n" + "-"*60)
    print("Chatflow 管理最佳實踐:")
    print("-"*60)
    print("""
    1. 版本控制
       - 定期導出 Chatflow 配置到版本控制系統
       - 使用有意義的命名和描述
       - 記錄重大變更

    2. 測試流程
       - 在開發環境測試新配置
       - 使用克隆功能進行實驗
       - 驗證後再部署到生產環境

    3. 備份策略
       - 定期備份所有 Chatflow
       - 保留歷史版本
       - 測試恢復流程

    4. 組織管理
       - 使用類別標籤組織 Chatflow
       - 建立命名規範
       - 文檔化複雜流程

    5. 安全考慮
       - 不要在配置中硬編碼敏感信息
       - 使用環境變量管理 API 密鑰
       - 限制 API 訪問權限
    """)

"""
Flowise API 調用基礎
==================

本範例展示如何使用 Flowise Python SDK 和 REST API 進行基礎的 API 調用。
包含非流式和流式響應的使用方法。

安裝依賴:
pip install flowise requests

作者: Flowise Demo
日期: 2025-12-15
"""

import os
import requests
import json
from typing import Dict, Any, Optional, List
from flowise import Flowise, PredictionData, IMessage, IFileUpload


class FlowiseAPIBasics:
    """
    Flowise API 基礎使用類

    這個類展示了如何使用 Flowise SDK 和原生 HTTP 請求進行 API 調用
    """

    def __init__(self, base_url: str = "http://localhost:3000", api_key: Optional[str] = None):
        """
        初始化 Flowise 客戶端

        參數:
            base_url: Flowise 服務器地址，默認為本地服務
            api_key: API 密鑰（如果配置了認證）
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key or os.getenv("FLOWISE_API_KEY")

        # 初始化 Flowise SDK 客戶端
        self.client = Flowise()

        print(f"✓ Flowise 客戶端已初始化")
        print(f"  服務器地址: {self.base_url}")
        print(f"  API 密鑰: {'已配置' if self.api_key else '未配置'}")

    def get_headers(self) -> Dict[str, str]:
        """
        獲取 HTTP 請求頭

        返回:
            包含認證信息的請求頭字典
        """
        headers = {
            "Content-Type": "application/json"
        }

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        return headers

    def example_1_simple_prediction(self, chatflow_id: str, question: str):
        """
        示例 1: 簡單的非流式預測

        使用 Flowise SDK 進行基礎的問答交互

        參數:
            chatflow_id: Chatflow 的唯一標識符
            question: 要提問的問題
        """
        print("\n" + "="*60)
        print("示例 1: 簡單的非流式預測")
        print("="*60)

        try:
            # 創建預測請求
            completion = self.client.create_prediction(
                PredictionData(
                    chatflowId=chatflow_id,
                    question=question,
                    streaming=False  # 非流式模式
                )
            )

            # 處理響應
            print(f"\n問題: {question}")
            print("\n回答:")
            for response in completion:
                print(response)

            print("\n✓ 預測完成")

        except Exception as e:
            print(f"\n✗ 錯誤: {str(e)}")

    def example_2_streaming_prediction(self, chatflow_id: str, question: str):
        """
        示例 2: 流式預測

        使用流式響應獲取實時生成的內容

        參數:
            chatflow_id: Chatflow 的唯一標識符
            question: 要提問的問題
        """
        print("\n" + "="*60)
        print("示例 2: 流式預測")
        print("="*60)

        try:
            # 創建流式預測請求
            completion = self.client.create_prediction(
                PredictionData(
                    chatflowId=chatflow_id,
                    question=question,
                    streaming=True  # 啟用流式模式
                )
            )

            print(f"\n問題: {question}")
            print("\n回答（流式）:")

            # 逐塊處理流式響應
            for chunk in completion:
                # 流式響應會逐字或逐句返回
                print(chunk, end='', flush=True)

            print("\n\n✓ 流式預測完成")

        except Exception as e:
            print(f"\n✗ 錯誤: {str(e)}")

    def example_3_prediction_with_history(
        self,
        chatflow_id: str,
        question: str,
        history: List[IMessage]
    ):
        """
        示例 3: 帶有對話歷史的預測

        保持上下文連貫性的對話

        參數:
            chatflow_id: Chatflow 的唯一標識符
            question: 要提問的問題
            history: 對話歷史記錄列表
        """
        print("\n" + "="*60)
        print("示例 3: 帶有對話歷史的預測")
        print("="*60)

        try:
            # 創建帶歷史的預測請求
            completion = self.client.create_prediction(
                PredictionData(
                    chatflowId=chatflow_id,
                    question=question,
                    history=history,
                    streaming=False
                )
            )

            # 顯示對話歷史
            print("\n對話歷史:")
            for msg in history:
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                print(f"  [{role.upper()}]: {content}")

            print(f"\n當前問題: {question}")
            print("\n回答:")

            for response in completion:
                print(response)

            print("\n✓ 預測完成")

        except Exception as e:
            print(f"\n✗ 錯誤: {str(e)}")

    def example_4_http_request_prediction(self, chatflow_id: str, question: str):
        """
        示例 4: 使用原生 HTTP 請求

        不使用 SDK，直接調用 REST API

        參數:
            chatflow_id: Chatflow 的唯一標識符
            question: 要提問的問題
        """
        print("\n" + "="*60)
        print("示例 4: 使用原生 HTTP 請求")
        print("="*60)

        try:
            # 構建 API URL
            url = f"{self.base_url}/api/v1/prediction/{chatflow_id}"

            # 準備請求數據
            payload = {
                "question": question,
                "streaming": False
            }

            # 發送 POST 請求
            print(f"\n發送請求到: {url}")
            response = requests.post(
                url,
                json=payload,
                headers=self.get_headers()
            )

            # 檢查響應狀態
            response.raise_for_status()

            # 解析響應
            result = response.json()

            print(f"\n問題: {question}")
            print("\n回答:")
            print(json.dumps(result, indent=2, ensure_ascii=False))

            print("\n✓ HTTP 請求成功")

        except requests.exceptions.RequestException as e:
            print(f"\n✗ HTTP 請求錯誤: {str(e)}")
        except Exception as e:
            print(f"\n✗ 錯誤: {str(e)}")

    def example_5_get_chatflows(self):
        """
        示例 5: 獲取所有 Chatflow 列表

        查詢服務器上所有可用的 Chatflow
        """
        print("\n" + "="*60)
        print("示例 5: 獲取所有 Chatflow 列表")
        print("="*60)

        try:
            # 構建 API URL
            url = f"{self.base_url}/api/v1/chatflows"

            # 發送 GET 請求
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()

            # 解析響應
            chatflows = response.json()

            print(f"\n找到 {len(chatflows)} 個 Chatflow:")

            for i, chatflow in enumerate(chatflows, 1):
                print(f"\n{i}. {chatflow.get('name', 'Unnamed')}")
                print(f"   ID: {chatflow.get('id')}")
                print(f"   類型: {chatflow.get('type', 'N/A')}")
                print(f"   更新時間: {chatflow.get('updatedDate', 'N/A')}")

            print("\n✓ Chatflow 列表獲取成功")

            return chatflows

        except requests.exceptions.RequestException as e:
            print(f"\n✗ HTTP 請求錯誤: {str(e)}")
            return []
        except Exception as e:
            print(f"\n✗ 錯誤: {str(e)}")
            return []

    def example_6_prediction_with_overrides(
        self,
        chatflow_id: str,
        question: str,
        overrides: Dict[str, Any]
    ):
        """
        示例 6: 帶有配置覆蓋的預測

        動態修改 Chatflow 的配置參數

        參數:
            chatflow_id: Chatflow 的唯一標識符
            question: 要提問的問題
            overrides: 要覆蓋的配置參數
        """
        print("\n" + "="*60)
        print("示例 6: 帶有配置覆蓋的預測")
        print("="*60)

        try:
            # 構建 API URL
            url = f"{self.base_url}/api/v1/prediction/{chatflow_id}"

            # 準備請求數據，包含覆蓋配置
            payload = {
                "question": question,
                "streaming": False,
                "overrideConfig": overrides
            }

            print(f"\n覆蓋配置:")
            print(json.dumps(overrides, indent=2, ensure_ascii=False))

            # 發送請求
            response = requests.post(
                url,
                json=payload,
                headers=self.get_headers()
            )
            response.raise_for_status()

            result = response.json()

            print(f"\n問題: {question}")
            print("\n回答:")
            print(json.dumps(result, indent=2, ensure_ascii=False))

            print("\n✓ 帶配置覆蓋的預測完成")

        except Exception as e:
            print(f"\n✗ 錯誤: {str(e)}")


def main():
    """
    主函數：演示所有 API 調用示例
    """
    print("\n" + "="*60)
    print("Flowise API 調用基礎示例")
    print("="*60)

    # 配置參數（請根據實際情況修改）
    BASE_URL = os.getenv("FLOWISE_BASE_URL", "http://localhost:3000")
    API_KEY = os.getenv("FLOWISE_API_KEY")  # 如果需要認證
    CHATFLOW_ID = os.getenv("FLOWISE_CHATFLOW_ID", "your-chatflow-id")

    # 初始化 API 客戶端
    api = FlowiseAPIBasics(base_url=BASE_URL, api_key=API_KEY)

    # 示例 1: 簡單預測
    api.example_1_simple_prediction(
        chatflow_id=CHATFLOW_ID,
        question="什麼是人工智能？"
    )

    # 示例 2: 流式預測
    api.example_2_streaming_prediction(
        chatflow_id=CHATFLOW_ID,
        question="請解釋機器學習的基本概念。"
    )

    # 示例 3: 帶對話歷史的預測
    history = [
        {"role": "user", "content": "我想學習 Python"},
        {"role": "assistant", "content": "Python 是一門優秀的編程語言，適合初學者。"},
        {"role": "user", "content": "從哪裡開始？"},
        {"role": "assistant", "content": "建議從基礎語法開始，然後學習數據結構和算法。"}
    ]
    api.example_3_prediction_with_history(
        chatflow_id=CHATFLOW_ID,
        question="有推薦的學習資源嗎？",
        history=history
    )

    # 示例 4: HTTP 請求
    api.example_4_http_request_prediction(
        chatflow_id=CHATFLOW_ID,
        question="Flowise 有哪些主要功能？"
    )

    # 示例 5: 獲取 Chatflow 列表
    chatflows = api.example_5_get_chatflows()

    # 示例 6: 配置覆蓋
    if chatflows:
        # 覆蓋 LLM 溫度參數和模型
        overrides = {
            "temperature": 0.7,
            "modelName": "gpt-4",
            "maxTokens": 500
        }
        api.example_6_prediction_with_overrides(
            chatflow_id=CHATFLOW_ID,
            question="請創作一首關於 AI 的詩。",
            overrides=overrides
        )

    print("\n" + "="*60)
    print("所有示例運行完成！")
    print("="*60)

    # 使用提示
    print("\n使用提示:")
    print("1. 確保 Flowise 服務正在運行（默認端口 3000）")
    print("2. 設置環境變量 FLOWISE_CHATFLOW_ID 為你的 Chatflow ID")
    print("3. 如果啟用了 API 認證，設置 FLOWISE_API_KEY")
    print("4. 根據需要調整 BASE_URL 參數")
    print("\n獲取 Chatflow ID:")
    print("  - 在 Flowise UI 中打開一個 Chatflow")
    print("  - 查看瀏覽器地址欄的 URL")
    print("  - ID 在 /chatflow/ 之後，例如: http://localhost:3000/chatflow/abc123")


if __name__ == "__main__":
    # 運行示例
    main()

    # 額外說明
    print("\n" + "-"*60)
    print("API 調用最佳實踐:")
    print("-"*60)
    print("""
    1. 錯誤處理
       - 始終使用 try-except 捕獲異常
       - 檢查 HTTP 響應狀態碼
       - 處理網絡超時和連接錯誤

    2. 性能優化
       - 使用流式響應處理長文本生成
       - 合理設置超時時間
       - 考慮使用連接池（requests.Session）

    3. 安全性
       - 不要在代碼中硬編碼 API 密鑰
       - 使用環境變量存儲敏感信息
       - 在生產環境啟用 HTTPS

    4. 調試技巧
       - 使用詳細的日誌記錄
       - 檢查完整的請求和響應內容
       - 使用 Flowise UI 測試 Chatflow

    5. 資源管理
       - 適當關閉連接和資源
       - 控制並發請求數量
       - 監控 API 使用配額
    """)

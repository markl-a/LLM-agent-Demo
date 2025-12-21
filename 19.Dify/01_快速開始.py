"""
Dify 快速開始範例
==================

本範例展示如何使用 Dify Python SDK 進行基礎的 API 調用。
包含以下內容：
1. 環境設置和 API Key 配置
2. 基礎聊天對話
3. 串流式回應
4. 錯誤處理
5. 應用參數獲取

作者：Dify 範例教程
日期：2025
"""

import os
from typing import Optional
from dotenv import load_dotenv

# 方法一：使用官方 dify-client
try:
    from dify_client import ChatClient, CompletionClient
    DIFY_CLIENT_AVAILABLE = True
except ImportError:
    DIFY_CLIENT_AVAILABLE = False
    print("提示：未安裝 dify-client，請執行：pip install dify-client")

# 方法二：使用 HTTP 請求（備用方案）
import requests
import json


class DifyQuickStart:
    """Dify 快速開始類"""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        初始化 Dify 客戶端

        參數：
            api_key: Dify API 金鑰（可從環境變數讀取）
            base_url: Dify API 基礎 URL（默認為官方服務）
        """
        # 載入環境變數
        load_dotenv()

        # 設置 API Key
        self.api_key = api_key or os.getenv("DIFY_API_KEY")
        if not self.api_key:
            raise ValueError("請設置 DIFY_API_KEY 環境變數或傳入 api_key 參數")

        # 設置基礎 URL
        self.base_url = base_url or os.getenv("DIFY_API_BASE", "https://api.dify.ai/v1")

        # 初始化客戶端
        if DIFY_CLIENT_AVAILABLE:
            self.chat_client = ChatClient(api_key=self.api_key)
            print("✓ 已使用官方 dify-client SDK")
        else:
            self.chat_client = None
            print("✓ 使用 HTTP 請求方式")

    def simple_chat(self, query: str, user_id: str = "default-user") -> dict:
        """
        發送簡單的聊天訊息（阻塞模式）

        參數：
            query: 用戶查詢內容
            user_id: 用戶識別碼

        返回：
            包含回應內容的字典
        """
        print(f"\n{'='*60}")
        print(f"發送訊息：{query}")
        print(f"{'='*60}")

        if DIFY_CLIENT_AVAILABLE and self.chat_client:
            # 使用官方 SDK
            try:
                response = self.chat_client.create_chat_message(
                    inputs={"query": query},
                    user=user_id,
                    response_mode="blocking"
                )

                print(f"回應：{response.get('answer', '')}")
                print(f"對話 ID：{response.get('conversation_id', '')}")
                print(f"消耗 Token：{response.get('metadata', {}).get('usage', {})}")

                return response
            except Exception as e:
                print(f"錯誤：{e}")
                return {"error": str(e)}
        else:
            # 使用 HTTP 請求
            return self._chat_http(query, user_id)

    def _chat_http(self, query: str, user_id: str, conversation_id: Optional[str] = None) -> dict:
        """
        使用 HTTP 請求發送聊天訊息

        參數：
            query: 用戶查詢
            user_id: 用戶 ID
            conversation_id: 對話 ID（可選，用於繼續對話）

        返回：
            API 回應字典
        """
        url = f"{self.base_url}/chat-messages"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "inputs": {},
            "query": query,
            "user": user_id,
            "response_mode": "blocking"
        }

        # 如果有對話 ID，加入請求中以繼續對話
        if conversation_id:
            payload["conversation_id"] = conversation_id

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()

            data = response.json()
            print(f"回應：{data.get('answer', '')}")
            print(f"對話 ID：{data.get('conversation_id', '')}")

            return data
        except requests.exceptions.RequestException as e:
            print(f"HTTP 請求錯誤：{e}")
            return {"error": str(e)}

    def streaming_chat(self, query: str, user_id: str = "default-user"):
        """
        發送聊天訊息並以串流方式接收回應

        參數：
            query: 用戶查詢
            user_id: 用戶 ID
        """
        print(f"\n{'='*60}")
        print(f"串流訊息：{query}")
        print(f"{'='*60}")
        print("回應（串流）：", end="", flush=True)

        url = f"{self.base_url}/chat-messages"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "inputs": {},
            "query": query,
            "user": user_id,
            "response_mode": "streaming"
        }

        try:
            response = requests.post(url, headers=headers, json=payload, stream=True, timeout=30)
            response.raise_for_status()

            full_answer = ""

            # 處理 Server-Sent Events (SSE) 串流
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')

                    # SSE 格式：data: {...}
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]  # 移除 'data: ' 前綴

                        try:
                            data = json.loads(data_str)

                            # 處理不同的事件類型
                            event = data.get('event')

                            if event == 'message':
                                # 訊息事件 - 包含回應內容
                                answer = data.get('answer', '')
                                print(answer, end="", flush=True)
                                full_answer += answer

                            elif event == 'message_end':
                                # 訊息結束事件
                                print("\n")
                                metadata = data.get('metadata', {})
                                print(f"\n對話 ID：{data.get('conversation_id', '')}")
                                print(f"消耗 Token：{metadata.get('usage', {})}")

                            elif event == 'error':
                                # 錯誤事件
                                print(f"\n錯誤：{data.get('message', '')}")

                        except json.JSONDecodeError:
                            continue

            return full_answer

        except requests.exceptions.RequestException as e:
            print(f"\nHTTP 請求錯誤：{e}")
            return None

    def get_application_parameters(self) -> dict:
        """
        獲取應用程式參數和配置

        返回：
            應用參數字典
        """
        print(f"\n{'='*60}")
        print("獲取應用參數")
        print(f"{'='*60}")

        url = f"{self.base_url}/parameters"

        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            params = response.json()

            print(f"應用名稱：{params.get('name', 'N/A')}")
            print(f"模型配置：{params.get('model_config', {}).get('model_name', 'N/A')}")
            print(f"功能：{params.get('features', [])}")

            return params

        except requests.exceptions.RequestException as e:
            print(f"獲取參數失敗：{e}")
            return {"error": str(e)}

    def multi_turn_conversation(self):
        """
        展示多輪對話的範例
        維持對話上下文
        """
        print(f"\n{'='*60}")
        print("多輪對話範例")
        print(f"{'='*60}")

        conversation_id = None
        user_id = "demo-user"

        # 第一輪對話
        print("\n第 1 輪對話")
        response1 = self._chat_http(
            query="我想了解 Python 的基礎知識",
            user_id=user_id
        )
        conversation_id = response1.get('conversation_id')

        # 第二輪對話 - 使用相同的 conversation_id
        if conversation_id:
            print("\n第 2 輪對話（帶上下文）")
            response2 = self._chat_http(
                query="能給我一個簡單的範例嗎？",
                user_id=user_id,
                conversation_id=conversation_id
            )

            print("\n第 3 輪對話（繼續上下文）")
            response3 = self._chat_http(
                query="謝謝！還有其他建議嗎？",
                user_id=user_id,
                conversation_id=conversation_id
            )


def main():
    """主函數 - 執行各種範例"""

    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║           Dify 快速開始範例                              ║
    ║                                                          ║
    ║  本範例展示 Dify API 的基本使用方式                      ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    # 檢查環境變數
    if not os.getenv("DIFY_API_KEY"):
        print("""
        ⚠️  請先設置環境變數！

        方法 1：創建 .env 檔案
        ----------------------
        DIFY_API_KEY=your-api-key-here
        DIFY_API_BASE=https://api.dify.ai/v1  # 可選

        方法 2：在終端中設置
        --------------------
        export DIFY_API_KEY="your-api-key-here"

        如何獲取 API Key：
        1. 訪問 https://dify.ai 或您的自部署實例
        2. 登入後進入應用設置
        3. 在「API 金鑰」部分創建新的金鑰
        """)
        return

    try:
        # 初始化客戶端
        dify = DifyQuickStart()

        # 範例 1：簡單聊天
        print("\n\n📝 範例 1：簡單聊天對話")
        dify.simple_chat(
            query="你好！請簡單介紹一下 Dify 框架。",
            user_id="demo-user-001"
        )

        # 範例 2：串流式回應
        print("\n\n📝 範例 2：串流式回應")
        dify.streaming_chat(
            query="請列出 Python 的 5 個主要特點。",
            user_id="demo-user-001"
        )

        # 範例 3：獲取應用參數
        print("\n\n📝 範例 3：獲取應用參數")
        dify.get_application_parameters()

        # 範例 4：多輪對話
        print("\n\n📝 範例 4：多輪對話")
        dify.multi_turn_conversation()

        print("""

        ✓ 所有範例執行完成！

        下一步：
        --------
        1. 查看 02_工作流創建.py 學習如何創建工作流
        2. 查看 03_知識庫管理.py 學習如何管理知識庫
        3. 查看 04_對話應用.py 學習如何構建聊天機器人
        """)

    except Exception as e:
        print(f"\n❌ 執行錯誤：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

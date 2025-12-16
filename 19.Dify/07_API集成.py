"""
Dify API 集成範例
================

本範例展示如何將 Dify 與外部 API 和服務集成。

集成功能：
1. 外部 API 調用
2. Webhook 設置
3. 第三方服務集成
4. 自定義連接器

安裝依賴：
pip install requests flask
"""

import os
import json
import requests
import hashlib
import hmac
import time
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from functools import wraps

# ============================================================
# 配置
# ============================================================

DIFY_API_KEY = os.getenv("DIFY_API_KEY", "app-xxxxxxxxxxxxxxxx")
DIFY_BASE_URL = os.getenv("DIFY_BASE_URL", "https://api.dify.ai/v1")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "your-webhook-secret")


# ============================================================
# API 集成客戶端
# ============================================================

class DifyIntegrationClient:
    """
    Dify API 集成客戶端

    提供與外部服務集成的功能
    """

    def __init__(self, api_key: str, base_url: str = "https://api.dify.ai/v1"):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def call_with_external_data(
        self,
        query: str,
        user: str,
        external_data: Dict[str, Any],
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        帶外部數據的調用

        Args:
            query: 用戶查詢
            user: 用戶標識
            external_data: 外部數據
            conversation_id: 對話 ID

        Returns:
            響應結果
        """
        url = f"{self.base_url}/chat-messages"

        payload = {
            "query": query,
            "user": user,
            "response_mode": "blocking",
            "inputs": external_data
        }

        if conversation_id:
            payload["conversation_id"] = conversation_id

        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()

        return response.json()

    def get_app_info(self) -> Dict[str, Any]:
        """
        獲取應用信息

        Returns:
            應用信息
        """
        url = f"{self.base_url}/parameters"

        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        return response.json()

    def get_meta(self) -> Dict[str, Any]:
        """
        獲取應用元數據

        Returns:
            元數據
        """
        url = f"{self.base_url}/meta"

        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        return response.json()


# ============================================================
# 外部 API 連接器
# ============================================================

@dataclass
class APIConnector:
    """API 連接器基類"""
    name: str
    base_url: str
    auth_type: str = "bearer"  # bearer, api_key, basic
    auth_value: str = ""


class ExternalAPIManager:
    """
    外部 API 管理器

    管理和調用外部 API
    """

    def __init__(self):
        self.connectors: Dict[str, APIConnector] = {}
        self.cache: Dict[str, Any] = {}
        self.cache_ttl: int = 300  # 5 分鐘緩存

    def register_connector(
        self,
        name: str,
        base_url: str,
        auth_type: str = "bearer",
        auth_value: str = ""
    ):
        """
        註冊 API 連接器

        Args:
            name: 連接器名稱
            base_url: API 基礎 URL
            auth_type: 認證類型
            auth_value: 認證值
        """
        self.connectors[name] = APIConnector(
            name=name,
            base_url=base_url,
            auth_type=auth_type,
            auth_value=auth_value
        )

    def call_api(
        self,
        connector_name: str,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        調用外部 API

        Args:
            connector_name: 連接器名稱
            endpoint: API 端點
            method: HTTP 方法
            params: 查詢參數
            data: 請求數據
            use_cache: 是否使用緩存

        Returns:
            API 響應
        """
        if connector_name not in self.connectors:
            raise ValueError(f"連接器不存在: {connector_name}")

        connector = self.connectors[connector_name]

        # 檢查緩存
        if use_cache and method == "GET":
            cache_key = f"{connector_name}:{endpoint}:{json.dumps(params or {})}"
            if cache_key in self.cache:
                cached = self.cache[cache_key]
                if time.time() - cached['timestamp'] < self.cache_ttl:
                    return cached['data']

        # 構建請求
        url = f"{connector.base_url.rstrip('/')}/{endpoint.lstrip('/')}"

        headers = {"Content-Type": "application/json"}

        if connector.auth_type == "bearer":
            headers["Authorization"] = f"Bearer {connector.auth_value}"
        elif connector.auth_type == "api_key":
            headers["X-API-Key"] = connector.auth_value

        # 發送請求
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=data
        )
        response.raise_for_status()

        result = response.json()

        # 更新緩存
        if use_cache and method == "GET":
            self.cache[cache_key] = {
                'data': result,
                'timestamp': time.time()
            }

        return result


# ============================================================
# Webhook 處理器
# ============================================================

class WebhookHandler:
    """
    Webhook 處理器

    處理來自 Dify 的 Webhook 回調
    """

    def __init__(self, secret: str):
        self.secret = secret
        self.handlers: Dict[str, Callable] = {}

    def verify_signature(
        self,
        payload: bytes,
        signature: str
    ) -> bool:
        """
        驗證 Webhook 簽名

        Args:
            payload: 請求體
            signature: 簽名

        Returns:
            是否驗證通過
        """
        expected = hmac.new(
            self.secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(f"sha256={expected}", signature)

    def register_handler(
        self,
        event_type: str,
        handler: Callable[[Dict[str, Any]], Any]
    ):
        """
        註冊事件處理器

        Args:
            event_type: 事件類型
            handler: 處理函數
        """
        self.handlers[event_type] = handler

    def process_event(
        self,
        event_type: str,
        payload: Dict[str, Any]
    ) -> Any:
        """
        處理事件

        Args:
            event_type: 事件類型
            payload: 事件數據

        Returns:
            處理結果
        """
        if event_type not in self.handlers:
            raise ValueError(f"未註冊的事件類型: {event_type}")

        return self.handlers[event_type](payload)


# ============================================================
# 服務集成範例
# ============================================================

class WeatherService:
    """天氣服務集成"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"

    def get_weather(self, city: str) -> Dict[str, Any]:
        """獲取城市天氣"""
        url = f"{self.base_url}/weather"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric"
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        return response.json()


class NotificationService:
    """通知服務集成"""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def send_notification(
        self,
        title: str,
        message: str,
        level: str = "info"
    ) -> bool:
        """
        發送通知

        Args:
            title: 標題
            message: 消息內容
            level: 通知級別

        Returns:
            是否成功
        """
        payload = {
            "title": title,
            "message": message,
            "level": level,
            "timestamp": time.time()
        }

        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False


# ============================================================
# 使用範例
# ============================================================

def example_external_data():
    """
    範例 1: 帶外部數據調用

    展示如何將外部數據傳遞給 Dify
    """
    print("=" * 50)
    print("範例 1: 帶外部數據調用")
    print("=" * 50)

    client = DifyIntegrationClient(
        api_key=DIFY_API_KEY,
        base_url=DIFY_BASE_URL
    )

    # 準備外部數據
    external_data = {
        "user_name": "張三",
        "user_level": "VIP",
        "purchase_history": ["商品A", "商品B", "商品C"],
        "current_time": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    try:
        result = client.call_with_external_data(
            query="根據我的購買記錄，推薦一些商品",
            user="user-001",
            external_data=external_data
        )

        print(f"回答: {result.get('answer', '')}")

    except requests.exceptions.RequestException as e:
        print(f"請求錯誤: {e}")


def example_api_connector():
    """
    範例 2: API 連接器

    展示如何使用 API 連接器調用外部服務
    """
    print("\n" + "=" * 50)
    print("範例 2: API 連接器")
    print("=" * 50)

    manager = ExternalAPIManager()

    # 註冊連接器
    manager.register_connector(
        name="jsonplaceholder",
        base_url="https://jsonplaceholder.typicode.com",
        auth_type="none"
    )

    try:
        # 調用外部 API
        posts = manager.call_api(
            connector_name="jsonplaceholder",
            endpoint="/posts",
            params={"_limit": 3}
        )

        print("獲取的文章:")
        for post in posts:
            print(f"  - {post.get('title', '')[:30]}...")

    except requests.exceptions.RequestException as e:
        print(f"請求錯誤: {e}")


def example_webhook_handler():
    """
    範例 3: Webhook 處理器

    展示如何設置 Webhook 處理器
    """
    print("\n" + "=" * 50)
    print("範例 3: Webhook 處理器")
    print("=" * 50)

    handler = WebhookHandler(secret=WEBHOOK_SECRET)

    # 註冊事件處理器
    def on_message_created(payload: Dict[str, Any]) -> Dict[str, Any]:
        print(f"收到新消息: {payload.get('message', '')}")
        return {"status": "processed"}

    def on_conversation_finished(payload: Dict[str, Any]) -> Dict[str, Any]:
        print(f"對話結束: {payload.get('conversation_id', '')}")
        return {"status": "processed"}

    handler.register_handler("message_created", on_message_created)
    handler.register_handler("conversation_finished", on_conversation_finished)

    # 模擬處理事件
    test_payload = {
        "event": "message_created",
        "message": "這是一條測試消息",
        "timestamp": time.time()
    }

    result = handler.process_event("message_created", test_payload)
    print(f"處理結果: {result}")


def example_service_integration():
    """
    範例 4: 服務集成

    展示如何集成第三方服務
    """
    print("\n" + "=" * 50)
    print("範例 4: 服務集成")
    print("=" * 50)

    # 通知服務（模擬）
    notification = NotificationService(
        webhook_url="https://example.com/webhook"
    )

    # 模擬發送通知
    print("模擬發送通知...")
    print(f"標題: AI 助手回覆")
    print(f"內容: 您的查詢已處理完成")
    print(f"級別: info")


def example_combined_workflow():
    """
    範例 5: 組合工作流

    展示如何組合多個服務
    """
    print("\n" + "=" * 50)
    print("範例 5: 組合工作流")
    print("=" * 50)

    client = DifyIntegrationClient(
        api_key=DIFY_API_KEY,
        base_url=DIFY_BASE_URL
    )

    api_manager = ExternalAPIManager()

    # 註冊外部 API
    api_manager.register_connector(
        name="jsonplaceholder",
        base_url="https://jsonplaceholder.typicode.com"
    )

    try:
        # 步驟 1: 從外部 API 獲取數據
        print("步驟 1: 獲取外部數據...")
        users = api_manager.call_api(
            connector_name="jsonplaceholder",
            endpoint="/users",
            params={"_limit": 3}
        )

        user_names = [u.get('name', '') for u in users]
        print(f"  獲取到 {len(user_names)} 個用戶")

        # 步驟 2: 將數據傳給 Dify 處理
        print("\n步驟 2: 調用 Dify 處理...")
        result = client.call_with_external_data(
            query="分析這些用戶的特點",
            user="user-001",
            external_data={"users": user_names}
        )

        print(f"  處理結果: {result.get('answer', '')[:100]}...")

        # 步驟 3: 處理結果（模擬通知）
        print("\n步驟 3: 發送結果通知...")
        print("  通知已發送（模擬）")

    except requests.exceptions.RequestException as e:
        print(f"請求錯誤: {e}")


def example_rate_limiting():
    """
    範例 6: 速率限制

    展示如何處理 API 速率限制
    """
    print("\n" + "=" * 50)
    print("範例 6: 速率限制")
    print("=" * 50)

    def rate_limited_call(func, max_calls: int = 5, period: float = 60):
        """速率限制裝飾器"""
        calls = []

        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            # 清理過期的調用記錄
            calls[:] = [c for c in calls if now - c < period]

            if len(calls) >= max_calls:
                wait_time = period - (now - calls[0])
                print(f"速率限制：需要等待 {wait_time:.1f} 秒")
                return None

            calls.append(now)
            return func(*args, **kwargs)

        return wrapper

    @rate_limited_call
    def api_call(message: str):
        print(f"API 調用: {message}")
        return {"status": "success"}

    # 測試速率限制
    for i in range(7):
        result = api_call(f"調用 {i + 1}")
        if result:
            print(f"  結果: {result}")
        time.sleep(0.1)


def example_error_handling():
    """
    範例 7: 錯誤處理

    展示如何處理集成中的錯誤
    """
    print("\n" + "=" * 50)
    print("範例 7: 錯誤處理")
    print("=" * 50)

    class RetryableClient:
        """支持重試的客戶端"""

        def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
            self.max_retries = max_retries
            self.retry_delay = retry_delay

        def call_with_retry(
            self,
            func: Callable,
            *args,
            **kwargs
        ) -> Any:
            """帶重試的調用"""
            last_error = None

            for attempt in range(self.max_retries):
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.RequestException as e:
                    last_error = e
                    print(f"  嘗試 {attempt + 1} 失敗: {e}")

                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * (attempt + 1))

            raise last_error

    # 測試重試機制
    client = RetryableClient(max_retries=3, retry_delay=0.5)

    def failing_call():
        raise requests.exceptions.ConnectionError("模擬連接錯誤")

    try:
        print("測試重試機制...")
        client.call_with_retry(failing_call)
    except Exception as e:
        print(f"所有重試都失敗: {e}")


# ============================================================
# 主程序
# ============================================================

if __name__ == "__main__":
    print("Dify API 集成範例")
    print("請確保已設置相關環境變數")
    print()

    example_external_data()
    example_api_connector()
    example_webhook_handler()
    example_service_integration()
    example_combined_workflow()
    example_rate_limiting()
    example_error_handling()

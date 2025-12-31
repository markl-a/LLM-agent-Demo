"""
SuperAGI API 整合示例

這個示例展示了如何:
1. 使用 REST API
2. Webhook 處理
3. 事件驅動架構
4. API 認證和授權
5. API 客戶端開發

SuperAGI 提供完整的 API 支持，方便與其他系統整合。
"""

import os
import json
import hashlib
import hmac
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum


# ==================== API 配置 ====================

class APIConfig:
    """API 配置"""

    def __init__(self):
        self.base_url = "http://localhost:8000/api/v1"
        self.api_key = os.getenv("SUPERAGI_API_KEY", "your-api-key")
        self.api_secret = os.getenv("SUPERAGI_API_SECRET", "your-secret")
        self.timeout = 30
        self.max_retries = 3


# ==================== HTTP 方法 ====================

class HTTPMethod(Enum):
    """HTTP 方法"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


# ==================== API 客戶端 ====================

class SuperAGIClient:
    """
    SuperAGI API 客戶端

    提供與 SuperAGI 服務交互的接口
    """

    def __init__(self, config: APIConfig = None):
        """
        初始化客戶端

        參數:
            config: API 配置
        """
        self.config = config or APIConfig()
        self.session_token = None

    def _make_request(
        self,
        method: HTTPMethod,
        endpoint: str,
        data: Dict = None,
        params: Dict = None
    ) -> Dict:
        """
        發送 API 請求（模擬）

        參數:
            method: HTTP 方法
            endpoint: API 端點
            data: 請求數據
            params: 查詢參數

        返回:
            響應數據
        """
        url = f"{self.config.base_url}/{endpoint}"

        print(f"\n🌐 API 請求: {method.value} {url}")

        # 模擬 API 響應
        if method == HTTPMethod.POST and "agents" in endpoint:
            return {
                "success": True,
                "agent_id": "agent_12345",
                "message": "Agent 創建成功"
            }
        elif method == HTTPMethod.GET and "agents" in endpoint:
            return {
                "success": True,
                "agents": [
                    {"id": "agent_1", "name": "ResearchAgent", "status": "active"},
                    {"id": "agent_2", "name": "DataAgent", "status": "inactive"}
                ]
            }
        else:
            return {
                "success": True,
                "data": {},
                "timestamp": datetime.now().isoformat()
            }

    # ========== Agent 操作 ==========

    def create_agent(
        self,
        name: str,
        description: str,
        goals: List[str],
        tools: List[str] = None,
        **kwargs
    ) -> Dict:
        """
        創建 Agent

        參數:
            name: Agent 名稱
            description: 描述
            goals: 目標列表
            tools: 工具列表
            **kwargs: 其他參數

        返回:
            創建結果
        """
        data = {
            "name": name,
            "description": description,
            "goals": goals,
            "tools": tools or [],
            **kwargs
        }

        return self._make_request(HTTPMethod.POST, "agents", data=data)

    def list_agents(self, status: str = None) -> Dict:
        """
        列出 Agents

        參數:
            status: 狀態篩選

        返回:
            Agent 列表
        """
        params = {"status": status} if status else None
        return self._make_request(HTTPMethod.GET, "agents", params=params)

    def get_agent(self, agent_id: str) -> Dict:
        """
        獲取 Agent 詳情

        參數:
            agent_id: Agent ID

        返回:
            Agent 詳情
        """
        return self._make_request(HTTPMethod.GET, f"agents/{agent_id}")

    def update_agent(self, agent_id: str, **kwargs) -> Dict:
        """
        更新 Agent

        參數:
            agent_id: Agent ID
            **kwargs: 更新字段

        返回:
            更新結果
        """
        return self._make_request(HTTPMethod.PUT, f"agents/{agent_id}", data=kwargs)

    def delete_agent(self, agent_id: str) -> Dict:
        """
        刪除 Agent

        參數:
            agent_id: Agent ID

        返回:
            刪除結果
        """
        return self._make_request(HTTPMethod.DELETE, f"agents/{agent_id}")

    def run_agent(self, agent_id: str) -> Dict:
        """
        運行 Agent

        參數:
            agent_id: Agent ID

        返回:
            運行結果
        """
        return self._make_request(HTTPMethod.POST, f"agents/{agent_id}/run")

    def stop_agent(self, agent_id: str) -> Dict:
        """
        停止 Agent

        參數:
            agent_id: Agent ID

        返回:
            停止結果
        """
        return self._make_request(HTTPMethod.POST, f"agents/{agent_id}/stop")

    def get_agent_logs(self, agent_id: str, limit: int = 100) -> Dict:
        """
        獲取 Agent 日誌

        參數:
            agent_id: Agent ID
            limit: 日誌數量限制

        返回:
            日誌數據
        """
        return self._make_request(
            HTTPMethod.GET,
            f"agents/{agent_id}/logs",
            params={"limit": limit}
        )

    # ========== 工具操作 ==========

    def list_tools(self, category: str = None) -> Dict:
        """
        列出工具

        參數:
            category: 工具分類

        返回:
            工具列表
        """
        params = {"category": category} if category else None
        return self._make_request(HTTPMethod.GET, "tools", params=params)

    def install_tool(self, tool_name: str, version: str = "latest") -> Dict:
        """
        安裝工具

        參數:
            tool_name: 工具名稱
            version: 版本

        返回:
            安裝結果
        """
        return self._make_request(
            HTTPMethod.POST,
            "tools/install",
            data={"tool_name": tool_name, "version": version}
        )

    # ========== 任務操作 ==========

    def get_tasks(self, agent_id: str, status: str = None) -> Dict:
        """
        獲取任務列表

        參數:
            agent_id: Agent ID
            status: 任務狀態

        返回:
            任務列表
        """
        params = {"agent_id": agent_id}
        if status:
            params["status"] = status

        return self._make_request(HTTPMethod.GET, "tasks", params=params)


# ==================== Webhook 處理器 ====================

@dataclass
class WebhookEvent:
    """Webhook 事件"""
    event_type: str
    payload: Dict
    timestamp: datetime = field(default_factory=datetime.now)
    signature: Optional[str] = None


class WebhookHandler:
    """
    Webhook 處理器

    接收和處理 SuperAGI 的 Webhook 事件
    """

    def __init__(self, secret: str):
        """
        初始化處理器

        參數:
            secret: Webhook 簽名密鑰
        """
        self.secret = secret
        self.handlers: Dict[str, List[Callable]] = {}

    def register_handler(self, event_type: str, handler: Callable):
        """
        註冊事件處理器

        參數:
            event_type: 事件類型
            handler: 處理函數
        """
        if event_type not in self.handlers:
            self.handlers[event_type] = []

        self.handlers[event_type].append(handler)
        print(f"✅ 註冊 Webhook 處理器: {event_type}")

    def verify_signature(self, payload: str, signature: str) -> bool:
        """
        驗證 Webhook 簽名

        參數:
            payload: 請求體
            signature: 簽名

        返回:
            是否有效
        """
        expected_signature = hmac.new(
            self.secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(expected_signature, signature)

    def handle_webhook(self, event: WebhookEvent) -> Dict:
        """
        處理 Webhook 事件

        參數:
            event: Webhook 事件

        返回:
            處理結果
        """
        print(f"\n📨 收到 Webhook: {event.event_type}")

        # 驗證簽名
        if event.signature:
            payload_str = json.dumps(event.payload)
            if not self.verify_signature(payload_str, event.signature):
                return {
                    "success": False,
                    "error": "Invalid signature"
                }

        # 調用處理器
        if event.event_type in self.handlers:
            results = []
            for handler in self.handlers[event.event_type]:
                try:
                    result = handler(event.payload)
                    results.append(result)
                except Exception as e:
                    print(f"❌ 處理器執行失敗: {e}")
                    results.append({"success": False, "error": str(e)})

            return {
                "success": True,
                "results": results
            }
        else:
            print(f"⚠️  未找到處理器: {event.event_type}")
            return {
                "success": False,
                "error": f"No handler for event type: {event.event_type}"
            }


# ==================== 事件系統 ====================

class EventBus:
    """
    事件總線

    實現事件驅動架構
    """

    def __init__(self):
        """初始化事件總線"""
        self.subscribers: Dict[str, List[Callable]] = {}
        self.events: List[Dict] = []

    def subscribe(self, event_type: str, callback: Callable):
        """
        訂閱事件

        參數:
            event_type: 事件類型
            callback: 回調函數
        """
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []

        self.subscribers[event_type].append(callback)
        print(f"✅ 訂閱事件: {event_type}")

    def publish(self, event_type: str, data: Dict):
        """
        發布事件

        參數:
            event_type: 事件類型
            data: 事件數據
        """
        print(f"\n📢 發布事件: {event_type}")

        # 記錄事件
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        self.events.append(event)

        # 通知訂閱者
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    print(f"❌ 回調執行失敗: {e}")

    def get_events(self, event_type: str = None) -> List[Dict]:
        """
        獲取事件歷史

        參數:
            event_type: 事件類型篩選

        返回:
            事件列表
        """
        if event_type:
            return [e for e in self.events if e["type"] == event_type]
        return self.events


# ==================== API 認證 ====================

class APIAuthenticator:
    """
    API 認證器

    管理 API 認證和授權
    """

    def __init__(self):
        """初始化認證器"""
        self.api_keys: Dict[str, Dict] = {}
        self.tokens: Dict[str, Dict] = {}

    def create_api_key(
        self,
        user_id: str,
        permissions: List[str] = None
    ) -> str:
        """
        創建 API Key

        參數:
            user_id: 用戶 ID
            permissions: 權限列表

        返回:
            API Key
        """
        import secrets

        api_key = f"sk_{secrets.token_urlsafe(32)}"

        self.api_keys[api_key] = {
            "user_id": user_id,
            "permissions": permissions or ["read"],
            "created_at": datetime.now().isoformat(),
            "active": True
        }

        print(f"🔑 創建 API Key: {api_key[:20]}...")

        return api_key

    def validate_api_key(self, api_key: str) -> Optional[Dict]:
        """
        驗證 API Key

        參數:
            api_key: API Key

        返回:
            用戶信息（如果有效）
        """
        key_info = self.api_keys.get(api_key)

        if not key_info or not key_info["active"]:
            return None

        return key_info

    def create_token(
        self,
        user_id: str,
        expiry_hours: int = 24
    ) -> str:
        """
        創建訪問令牌

        參數:
            user_id: 用戶 ID
            expiry_hours: 過期時間（小時）

        返回:
            訪問令牌
        """
        import secrets

        token = secrets.token_urlsafe(32)

        self.tokens[token] = {
            "user_id": user_id,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(hours=expiry_hours)
        }

        return token

    def validate_token(self, token: str) -> Optional[Dict]:
        """
        驗證令牌

        參數:
            token: 訪問令牌

        返回:
            令牌信息（如果有效）
        """
        token_info = self.tokens.get(token)

        if not token_info:
            return None

        # 檢查是否過期
        if datetime.now() > token_info["expires_at"]:
            return None

        return token_info


# ==================== 示例場景 ====================

def example_1_basic_api():
    """示例 1: 基本 API 使用"""
    print("\n" + "=" * 60)
    print("示例 1: 基本 API 操作")
    print("=" * 60)

    client = SuperAGIClient()

    # 創建 Agent
    print("\n1. 創建 Agent")
    result = client.create_agent(
        name="APITestAgent",
        description="通過 API 創建的測試 Agent",
        goals=["完成測試任務"],
        tools=["GoogleSearchTool"]
    )
    print(f"結果: {json.dumps(result, indent=2, ensure_ascii=False)}")

    # 列出 Agents
    print("\n2. 列出所有 Agents")
    result = client.list_agents()
    print(f"結果: {json.dumps(result, indent=2, ensure_ascii=False)}")

    # 運行 Agent
    if result.get("success") and result.get("agents"):
        agent_id = result["agents"][0]["id"]
        print(f"\n3. 運行 Agent: {agent_id}")
        result = client.run_agent(agent_id)
        print(f"結果: {json.dumps(result, indent=2, ensure_ascii=False)}")


def example_2_webhook():
    """示例 2: Webhook 處理"""
    print("\n" + "=" * 60)
    print("示例 2: Webhook 處理")
    print("=" * 60)

    # 創建 Webhook 處理器
    webhook_handler = WebhookHandler(secret="my_webhook_secret")

    # 註冊事件處理器
    def on_agent_started(payload):
        print(f"   處理器: Agent 啟動 - {payload.get('agent_id')}")
        return {"acknowledged": True}

    def on_task_completed(payload):
        print(f"   處理器: 任務完成 - {payload.get('task_id')}")
        return {"acknowledged": True}

    webhook_handler.register_handler("agent.started", on_agent_started)
    webhook_handler.register_handler("task.completed", on_task_completed)

    # 模擬接收 Webhook
    event1 = WebhookEvent(
        event_type="agent.started",
        payload={"agent_id": "agent_123", "timestamp": datetime.now().isoformat()}
    )

    result = webhook_handler.handle_webhook(event1)
    print(f"\n處理結果: {json.dumps(result, indent=2, ensure_ascii=False)}")

    event2 = WebhookEvent(
        event_type="task.completed",
        payload={"task_id": "task_456", "status": "success"}
    )

    result = webhook_handler.handle_webhook(event2)
    print(f"\n處理結果: {json.dumps(result, indent=2, ensure_ascii=False)}")


def example_3_event_bus():
    """示例 3: 事件驅動架構"""
    print("\n" + "=" * 60)
    print("示例 3: 事件驅動架構")
    print("=" * 60)

    event_bus = EventBus()

    # 訂閱事件
    def on_agent_created(data):
        print(f"   📨 收到事件: Agent 創建 - {data['name']}")

    def on_agent_completed(data):
        print(f"   📨 收到事件: Agent 完成 - {data['agent_id']}")
        print(f"      執行時間: {data['execution_time']}s")

    event_bus.subscribe("agent.created", on_agent_created)
    event_bus.subscribe("agent.completed", on_agent_completed)

    # 發布事件
    event_bus.publish("agent.created", {
        "name": "DataProcessor",
        "description": "數據處理 Agent"
    })

    event_bus.publish("agent.completed", {
        "agent_id": "agent_789",
        "execution_time": 45.2,
        "status": "success"
    })

    # 查看事件歷史
    print("\n事件歷史:")
    events = event_bus.get_events()
    for event in events:
        print(f"  - {event['type']} at {event['timestamp']}")


def example_4_authentication():
    """示例 4: API 認證"""
    print("\n" + "=" * 60)
    print("示例 4: API 認證和授權")
    print("=" * 60)

    auth = APIAuthenticator()

    # 創建 API Key
    print("\n1. 創建 API Key")
    api_key = auth.create_api_key(
        user_id="user_123",
        permissions=["read", "write", "execute"]
    )

    # 驗證 API Key
    print("\n2. 驗證 API Key")
    key_info = auth.validate_api_key(api_key)
    if key_info:
        print(f"   ✅ API Key 有效")
        print(f"   用戶: {key_info['user_id']}")
        print(f"   權限: {', '.join(key_info['permissions'])}")
    else:
        print(f"   ❌ API Key 無效")

    # 創建訪問令牌
    print("\n3. 創建訪問令牌")
    token = auth.create_token("user_123", expiry_hours=24)
    print(f"   令牌: {token[:20]}...")

    # 驗證令牌
    print("\n4. 驗證令牌")
    token_info = auth.validate_token(token)
    if token_info:
        print(f"   ✅ 令牌有效")
        print(f"   用戶: {token_info['user_id']}")
        print(f"   過期時間: {token_info['expires_at']}")
    else:
        print(f"   ❌ 令牌無效或已過期")


def example_5_comprehensive():
    """示例 5: 綜合 API 整合"""
    print("\n" + "=" * 60)
    print("示例 5: 綜合 API 整合示例")
    print("=" * 60)

    # 初始化組件
    client = SuperAGIClient()
    event_bus = EventBus()
    auth = APIAuthenticator()

    # 1. 認證
    print("\n步驟 1: 創建 API Key")
    api_key = auth.create_api_key("demo_user", ["read", "write", "execute"])

    # 2. 訂閱事件
    print("\n步驟 2: 訂閱事件")

    def log_event(data):
        print(f"   📊 記錄事件: {json.dumps(data, ensure_ascii=False)}")

    event_bus.subscribe("agent.created", log_event)
    event_bus.subscribe("agent.running", log_event)

    # 3. 創建 Agent
    print("\n步驟 3: 創建 Agent")
    result = client.create_agent(
        name="IntegratedAgent",
        description="整合示例 Agent",
        goals=["演示 API 整合"]
    )

    if result.get("success"):
        agent_id = result.get("agent_id")

        # 發布事件
        event_bus.publish("agent.created", {
            "agent_id": agent_id,
            "name": "IntegratedAgent"
        })

        # 4. 運行 Agent
        print("\n步驟 4: 運行 Agent")
        run_result = client.run_agent(agent_id)

        # 發布事件
        event_bus.publish("agent.running", {
            "agent_id": agent_id,
            "status": "running"
        })

    # 5. 查看事件歷史
    print("\n步驟 5: 查看事件歷史")
    events = event_bus.get_events()
    print(f"   總共 {len(events)} 個事件")


# ==================== 主函數 ====================

def main():
    """主函數"""
    print("\n" + "🔌 " * 20)
    print("SuperAGI API 整合教程")
    print("🔌 " * 20)

    try:
        # 示例 1: 基本 API
        example_1_basic_api()

        # 示例 2: Webhook
        example_2_webhook()

        # 示例 3: 事件總線
        example_3_event_bus()

        # 示例 4: 認證
        example_4_authentication()

        # 示例 5: 綜合示例
        example_5_comprehensive()

        print("\n" + "=" * 60)
        print("✅ 所有 API 整合示例執行完成！")
        print("=" * 60)

        print("""
        API 整合最佳實踐:

        1. 使用 API Key 進行認證
        2. 實施適當的錯誤處理
        3. 設置合理的超時時間
        4. 使用 Webhook 接收異步事件
        5. 實現重試機制
        6. 記錄所有 API 調用
        7. 驗證 Webhook 簽名
        8. 使用事件驅動架構解耦系統
        """)

    except Exception as e:
        print(f"\n❌ 執行出錯: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

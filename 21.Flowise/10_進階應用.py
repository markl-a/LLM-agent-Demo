"""
Flowise 進階應用範例
==================

本範例展示 Flowise 的進階使用技巧。

進階功能：
1. 變數覆蓋
2. 條件路由
3. 自定義節點
4. API 集成
5. 最佳實踐

安裝依賴：
pip install requests
"""

import os
import json
import requests
from typing import Dict, Any, List, Optional

# ============================================================
# 配置
# ============================================================

FLOWISE_API_URL = os.getenv("FLOWISE_API_URL", "http://localhost:3000")
FLOWISE_API_KEY = os.getenv("FLOWISE_API_KEY", "")


# ============================================================
# 進階 API 調用
# ============================================================

class FlowiseAdvancedClient:
    """進階 Flowise 客戶端"""

    def __init__(self, base_url: str, api_key: str = ""):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {"Content-Type": "application/json"}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

    def predict_with_override(
        self,
        chatflow_id: str,
        question: str,
        override_config: Dict[str, Any] = None,
        session_id: str = None
    ) -> Dict[str, Any]:
        """帶配置覆蓋的預測"""
        url = f"{self.base_url}/api/v1/prediction/{chatflow_id}"

        payload = {"question": question}

        if override_config:
            payload["overrideConfig"] = override_config

        if session_id:
            payload["overrideConfig"] = payload.get("overrideConfig", {})
            payload["overrideConfig"]["sessionId"] = session_id

        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()

    def stream_predict(
        self,
        chatflow_id: str,
        question: str,
        override_config: Dict[str, Any] = None
    ):
        """流式預測"""
        url = f"{self.base_url}/api/v1/prediction/{chatflow_id}"

        payload = {
            "question": question,
            "streaming": True
        }

        if override_config:
            payload["overrideConfig"] = override_config

        response = requests.post(
            url,
            headers=self.headers,
            json=payload,
            stream=True
        )

        for line in response.iter_lines():
            if line:
                yield json.loads(line.decode('utf-8'))


# ============================================================
# 進階配置範例
# ============================================================

OVERRIDE_CONFIG_EXAMPLE = '''
{
    "question": "什麼是機器學習？",
    "overrideConfig": {
        "modelName": "gpt-4",
        "temperature": 0.5,
        "maxTokens": 2000,
        "topK": 5,
        "sessionId": "user-123",
        "systemMessage": "你是一個專業的 AI 教育助手。"
    }
}
'''

CONDITIONAL_FLOW = '''
{
    "nodes": [
        {
            "id": "ifElse_0",
            "type": "IfElseFunction",
            "data": {
                "label": "If/Else",
                "inputs": {
                    "functionName": "checkIntent",
                    "inputVariables": "question",
                    "code": "if (question.includes('天氣')) { return 'weather'; } else if (question.includes('新聞')) { return 'news'; } return 'general';"
                }
            }
        },
        {
            "id": "weatherAgent_0",
            "type": "OpenAIFunctionAgent",
            "data": {
                "label": "Weather Agent"
            }
        },
        {
            "id": "newsAgent_0",
            "type": "OpenAIFunctionAgent",
            "data": {
                "label": "News Agent"
            }
        },
        {
            "id": "generalAgent_0",
            "type": "OpenAIFunctionAgent",
            "data": {
                "label": "General Agent"
            }
        }
    ],
    "edges": [
        {"source": "ifElse_0", "target": "weatherAgent_0", "sourceHandle": "weather"},
        {"source": "ifElse_0", "target": "newsAgent_0", "sourceHandle": "news"},
        {"source": "ifElse_0", "target": "generalAgent_0", "sourceHandle": "general"}
    ]
}
'''


# ============================================================
# 使用範例
# ============================================================

def example_override_config():
    """範例 1: 配置覆蓋"""
    print("=" * 50)
    print("範例 1: 動態配置覆蓋")
    print("=" * 50)
    print(OVERRIDE_CONFIG_EXAMPLE)
    print("""
可覆蓋的配置：
- modelName: 模型名稱
- temperature: 溫度
- maxTokens: 最大 token
- topK: 檢索數量
- sessionId: 會話 ID
- systemMessage: 系統提示
""")


def example_conditional_routing():
    """範例 2: 條件路由"""
    print("\n" + "=" * 50)
    print("範例 2: 條件路由")
    print("=" * 50)
    print(CONDITIONAL_FLOW[:800] + "...")


def example_streaming():
    """範例 3: 流式響應"""
    print("\n" + "=" * 50)
    print("範例 3: 流式響應")
    print("=" * 50)
    print("""
# Python 流式調用
client = FlowiseAdvancedClient(FLOWISE_API_URL, FLOWISE_API_KEY)

for chunk in client.stream_predict(chatflow_id, "解釋量子計算"):
    if chunk.get('event') == 'token':
        print(chunk['data'], end='', flush=True)

# JavaScript 流式調用
const response = await fetch(url, {
    method: 'POST',
    body: JSON.stringify({ question, streaming: true })
});

const reader = response.body.getReader();
while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    console.log(new TextDecoder().decode(value));
}
""")


def example_webhooks():
    """範例 4: Webhook 集成"""
    print("\n" + "=" * 50)
    print("範例 4: Webhook 集成")
    print("=" * 50)
    print("""
# 設置 Webhook 回調
{
    "overrideConfig": {
        "webhook": {
            "url": "https://your-server.com/webhook",
            "events": ["onStart", "onEnd", "onError"],
            "headers": {
                "Authorization": "Bearer your-token"
            }
        }
    }
}

# Webhook 接收示例
from flask import Flask, request

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    event = data.get('event')

    if event == 'onStart':
        print(f"開始處理: {data['sessionId']}")
    elif event == 'onEnd':
        print(f"處理完成: {data['response']}")
    elif event == 'onError':
        print(f"錯誤: {data['error']}")

    return {'status': 'ok'}
""")


def example_caching():
    """範例 5: 緩存策略"""
    print("\n" + "=" * 50)
    print("範例 5: 緩存策略")
    print("=" * 50)
    print("""
# 啟用響應緩存
{
    "nodes": [
        {
            "id": "cache_0",
            "type": "InMemoryCache",
            "data": {
                "inputs": {
                    "ttl": 3600,
                    "maxSize": 100
                }
            }
        }
    ]
}

# 或使用 Redis 緩存
{
    "nodes": [
        {
            "id": "redisCache_0",
            "type": "RedisCache",
            "data": {
                "inputs": {
                    "baseURL": "redis://localhost:6379",
                    "ttl": 3600
                }
            }
        }
    ]
}
""")


def example_rate_limiting():
    """範例 6: 速率限制"""
    print("\n" + "=" * 50)
    print("範例 6: 速率限制")
    print("=" * 50)
    print("""
# 環境變數配置
FLOWISE_RATE_LIMIT_MAX=100
FLOWISE_RATE_LIMIT_WINDOW=60000

# Nginx 配置
limit_req_zone $binary_remote_addr zone=flowise:10m rate=10r/s;

server {
    location /api/v1/prediction/ {
        limit_req zone=flowise burst=20 nodelay;
        proxy_pass http://flowise:3000;
    }
}

# 客戶端限制
import time
from functools import wraps

def rate_limit(calls_per_minute):
    def decorator(func):
        last_calls = []

        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            last_calls[:] = [t for t in last_calls if now - t < 60]

            if len(last_calls) >= calls_per_minute:
                raise Exception("Rate limit exceeded")

            last_calls.append(now)
            return func(*args, **kwargs)

        return wrapper
    return decorator
""")


def example_best_practices():
    """範例 7: 最佳實踐"""
    print("\n" + "=" * 50)
    print("範例 7: 最佳實踐")
    print("=" * 50)
    print("""
# 1. 使用環境變數管理敏感信息
OPENAI_API_KEY=sk-xxx
FLOWISE_PASSWORD=secure-password

# 2. 啟用身份驗證
FLOWISE_USERNAME=admin
FLOWISE_PASSWORD=strong-password
FLOWISE_SECRETKEY_PATH=/path/to/secret

# 3. 使用持久化存儲
DATABASE_TYPE=postgres
DATABASE_HOST=localhost

# 4. 配置健康檢查
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:3000/api/v1/health"]
  interval: 30s

# 5. 設置資源限制
resources:
  limits:
    memory: "2Gi"
    cpu: "2000m"

# 6. 啟用日誌記錄
LOG_LEVEL=info

# 7. 定期備份
*/6 * * * * pg_dump flowise > /backups/flowise_$(date +\\%Y\\%m\\%d).sql

# 8. 監控關鍵指標
- 請求延遲
- 錯誤率
- 內存使用
- CPU 使用
""")


if __name__ == "__main__":
    print("Flowise 進階應用範例\\n")
    example_override_config()
    example_conditional_routing()
    example_streaming()
    example_webhooks()
    example_caching()
    example_rate_limiting()
    example_best_practices()

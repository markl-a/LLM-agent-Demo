# OpenAI Agents SDK 完整指南

## 目錄
1. [簡介](#簡介)
2. [核心概念](#核心概念)
3. [安裝與設置](#安裝與設置)
4. [快速開始](#快速開始)
5. [與 Swarm 的對比](#與-swarm-的對比)
6. [範例目錄](#範例目錄)
7. [最佳實踐](#最佳實踐)
8. [進階主題](#進階主題)
9. [生產部署](#生產部署)
10. [故障排除](#故障排除)

---

## 簡介

### 什麼是 OpenAI Agents SDK？

OpenAI Agents SDK 是 OpenAI 官方推出的**生產級多 Agent 工作流框架**，可以看作是 Swarm 的正式升級版本。它提供了更強大、更靈活、更適合生產環境的 Agent 開發能力。

### 主要特點

1. **官方支持** - OpenAI 官方維護，長期更新保障
2. **生產就緒** - 內建監控、追蹤、錯誤處理
3. **多 LLM 支持** - 通過 LiteLLM 支持 100+ 模型提供商
4. **持久化工作流** - Temporal 整合，支持長時間運行的任務
5. **雙語言支持** - Python 和 TypeScript 同時支持
6. **輕量設計** - 保持 Swarm 的簡潔性，但功能更強

### 核心改進（相比 Swarm）

| 特性 | Swarm | Agents SDK |
|------|-------|------------|
| 狀態管理 | 基礎 | Sessions 持久化 |
| 錯誤處理 | 簡單 | Guardrails 驗證 |
| 追蹤調試 | 無 | 完整 Tracing |
| LLM 支持 | 僅 OpenAI | 100+ 提供商 |
| 工作流持久化 | 無 | Temporal 整合 |
| 生產部署 | 實驗性 | 完全支持 |

---

## 核心概念

### 1. Agents（代理）

Agent 是具有特定能力和職責的智能實體：

```python
from openai_agents import Agent

agent = Agent(
    name="助手",
    model="gpt-4",
    instructions="你是一個友善的助手",
    tools=[tool1, tool2],
    guardrails=[validator1]
)
```

**核心屬性：**
- `name`: Agent 的唯一標識
- `model`: 使用的語言模型
- `instructions`: 系統提示詞
- `tools`: 可調用的工具函數
- `guardrails`: 輸入/輸出驗證器

### 2. Handoffs（控制權轉移）

允許 Agent 之間無縫轉移對話控制權：

```python
from openai_agents import handoff_to

def transfer_to_specialist():
    """當需要專家意見時轉移"""
    return handoff_to(specialist_agent)

general_agent = Agent(
    name="總機",
    tools=[transfer_to_specialist]
)
```

**特點：**
- 保留完整對話歷史
- 支持條件轉移
- 可帶參數傳遞

### 3. Guardrails（護欄）

輸入輸出的驗證和安全機制：

```python
from openai_agents import Guardrail

def validate_input(message: str) -> bool:
    """檢查輸入是否安全"""
    forbidden = ["hack", "攻擊", "破壞"]
    return not any(word in message for word in forbidden)

safety_rail = Guardrail(
    type="input",
    validator=validate_input,
    error_message="輸入包含不當內容"
)
```

**類型：**
- `input`: 驗證用戶輸入
- `output`: 驗證 Agent 回應
- `tool`: 驗證工具調用結果

### 4. Sessions（會話）

管理對話歷史和狀態：

```python
from openai_agents import Session

session = Session(
    agent=my_agent,
    storage="redis://localhost:6379",  # 持久化存儲
    ttl=3600  # 會話有效期（秒）
)

# 在會話中運行
result = session.run("你好，請幫我...")
```

**功能：**
- 自動保存對話歷史
- 支持多種存儲後端（Redis、MongoDB、PostgreSQL）
- 會話恢復和重放
- 並發會話管理

### 5. Tracing（追蹤）

完整的調試和監控能力：

```python
from openai_agents import trace_run

with trace_run(name="客服對話") as tracer:
    result = agent.run("我要退貨")

# 查看追蹤數據
print(tracer.get_metrics())
print(tracer.get_timeline())
```

**追蹤內容：**
- 每步 Agent 決策
- 工具調用記錄
- Token 使用統計
- 性能指標
- 錯誤堆棧

### 6. Tools（工具）

Agent 可調用的函數：

```python
from openai_agents import tool

@tool
def search_database(query: str) -> dict:
    """搜索數據庫

    Args:
        query: 搜索關鍵詞

    Returns:
        搜索結果字典
    """
    # 實現搜索邏輯
    return {"results": [...]}
```

**特點：**
- 自動生成 JSON Schema
- 類型檢查和驗證
- 異步支持
- 錯誤處理

---

## 安裝與設置

### 基礎安裝

```bash
# 核心包
pip install openai-agents

# 使用其他 LLM（可選）
pip install openai-agents[litellm]

# Temporal 整合（可選）
pip install openai-agents[temporal]

# 完整安裝
pip install openai-agents[all]
```

### 環境配置

```bash
# .env 文件
OPENAI_API_KEY=sk-...
OPENAI_API_BASE=https://api.openai.com/v1  # 可選

# 使用其他 LLM
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
```

### Python 代碼配置

```python
import os
from openai_agents import configure

configure(
    api_key=os.getenv("OPENAI_API_KEY"),
    default_model="gpt-4",
    timeout=60,
    max_retries=3
)
```

---

## 快速開始

### 第一個 Agent

```python
from openai_agents import Agent, run

# 創建 Agent
agent = Agent(
    name="助手",
    model="gpt-4",
    instructions="你是一個友善的助手，用繁體中文回答問題。"
)

# 運行對話
response = run(
    agent=agent,
    messages=[{"role": "user", "content": "你好！"}]
)

print(response.messages[-1]["content"])
```

### 添加工具

```python
from openai_agents import Agent, tool, run
from datetime import datetime

@tool
def get_current_time() -> str:
    """獲取當前時間"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

agent = Agent(
    name="時間助手",
    model="gpt-4",
    instructions="你可以告訴用戶當前時間。",
    tools=[get_current_time]
)

response = run(
    agent=agent,
    messages=[{"role": "user", "content": "現在幾點？"}]
)

print(response.messages[-1]["content"])
```

### 多 Agent 協作

```python
from openai_agents import Agent, handoff_to, run

# 專家 Agent
specialist = Agent(
    name="技術專家",
    model="gpt-4",
    instructions="你是技術專家，專門回答技術問題。"
)

# 轉移函數
def transfer_to_specialist():
    """轉移到技術專家"""
    return handoff_to(specialist)

# 總機 Agent
receptionist = Agent(
    name="總機",
    model="gpt-4",
    instructions="你是總機，遇到技術問題請轉給專家。",
    tools=[transfer_to_specialist]
)

# 運行
response = run(
    agent=receptionist,
    messages=[{"role": "user", "content": "如何部署 Docker？"}]
)
```

---

## 與 Swarm 的對比

### 代碼對比

**Swarm 風格：**
```python
from swarm import Swarm, Agent

client = Swarm()
agent = Agent(
    name="助手",
    instructions="你是助手"
)

response = client.run(
    agent=agent,
    messages=[{"role": "user", "content": "你好"}]
)
```

**Agents SDK 風格：**
```python
from openai_agents import Agent, run, Session

agent = Agent(
    name="助手",
    instructions="你是助手",
    guardrails=[safety_check]  # 新增：安全檢查
)

# 方式 1：直接運行（類似 Swarm）
response = run(agent=agent, messages=[...])

# 方式 2：使用 Session（新功能）
session = Session(agent=agent, storage="redis://...")
response = session.run("你好")  # 自動管理歷史
```

### 主要差異

#### 1. 狀態管理
```python
# Swarm - 需手動管理
messages = []
response1 = client.run(agent, messages)
messages.extend(response1.messages)
response2 = client.run(agent, messages)  # 手動傳遞歷史

# Agents SDK - 自動管理
session = Session(agent=agent)
response1 = session.run("問題1")
response2 = session.run("問題2")  # 自動保留上下文
```

#### 2. 錯誤處理
```python
# Swarm - 基礎錯誤處理
try:
    response = client.run(agent, messages)
except Exception as e:
    print(f"錯誤: {e}")

# Agents SDK - Guardrails
from openai_agents import Guardrail

agent = Agent(
    name="助手",
    guardrails=[
        Guardrail(type="input", validator=validate_input),
        Guardrail(type="output", validator=validate_output)
    ]
)
```

#### 3. 追蹤調試
```python
# Swarm - 無內建追蹤
# 需要自己添加日誌

# Agents SDK - 完整追蹤
from openai_agents import trace_run

with trace_run(name="對話") as tracer:
    response = run(agent, messages)

print(tracer.get_metrics())  # Token 使用、延遲等
print(tracer.get_timeline())  # 完整執行時間線
```

### 遷移指南

從 Swarm 遷移到 Agents SDK 的步驟：

1. **更新導入**
   ```python
   # 舊
   from swarm import Swarm, Agent

   # 新
   from openai_agents import Agent, run, Session
   ```

2. **更新 Agent 定義**（大部分兼容）
   ```python
   # 基本保持不變
   agent = Agent(name="...", instructions="...", tools=[...])
   ```

3. **更新執行方式**
   ```python
   # 舊
   client = Swarm()
   response = client.run(agent, messages)

   # 新 - 選項 1
   response = run(agent, messages)

   # 新 - 選項 2（推薦）
   session = Session(agent)
   response = session.run("...")
   ```

4. **添加新功能**（可選）
   ```python
   # 添加 Guardrails
   agent.guardrails = [safety_check]

   # 添加追蹤
   with trace_run(name="...") as tracer:
       response = run(agent, messages)
   ```

---

## 範例目錄

本目錄包含以下範例：

### 基礎範例
- `01_基礎Agent.py` - 創建第一個 Agent
- `02_工具函數.py` - 定義和使用工具
- `03_Handoffs.py` - Agent 間控制權轉移
- `04_Guardrails.py` - 輸入輸出驗證
- `05_Sessions.py` - 會話管理和持久化
- `06_Tracing.py` - 調試和性能追蹤

### 進階範例
- `07_多Agent工作流.py` - 複雜的多 Agent 協作
- `11_LiteLLM整合.py` - 使用其他 LLM 提供商
- `12_Temporal整合.py` - 長時間運行的工作流

### 實際應用
- `08_客服系統.py` - 智能客服自動化
- `09_研究助手.py` - 多步驟研究任務

### 對比與遷移
- `10_與Swarm對比.py` - Swarm 遷移指南

---

## 最佳實踐

### 1. Agent 設計

**單一職責原則：**
```python
# 好 - 每個 Agent 職責明確
sales_agent = Agent(name="銷售", instructions="處理銷售問題")
tech_agent = Agent(name="技術", instructions="處理技術問題")

# 差 - Agent 職責過多
all_in_one = Agent(name="全能", instructions="處理所有問題")
```

**清晰的指令：**
```python
# 好
agent = Agent(
    name="客服",
    instructions="""你是客服人員，職責如下：
    1. 友善回答客戶問題
    2. 技術問題轉給技術團隊
    3. 退貨問題轉給退貨部門
    使用繁體中文，保持專業態度。"""
)

# 差
agent = Agent(name="客服", instructions="幫助客戶")
```

### 2. 工具設計

**明確的文檔字符串：**
```python
@tool
def search_orders(
    customer_id: str,
    status: Optional[str] = None
) -> List[dict]:
    """搜索訂單記錄

    Args:
        customer_id: 客戶 ID（必填）
        status: 訂單狀態，可選值：pending, shipped, delivered

    Returns:
        訂單列表，每個訂單包含 id, date, status, total

    Example:
        >>> search_orders("C123", status="shipped")
        [{"id": "O456", "status": "shipped", ...}]
    """
    # 實現
```

**錯誤處理：**
```python
@tool
def get_user_info(user_id: str) -> dict:
    """獲取用戶信息"""
    try:
        user = database.get(user_id)
        if not user:
            return {"error": "用戶不存在"}
        return user
    except Exception as e:
        return {"error": f"查詢失敗: {str(e)}"}
```

### 3. Guardrails 使用

**分層驗證：**
```python
# 輸入驗證
input_guardrail = Guardrail(
    type="input",
    validator=lambda msg: len(msg) < 1000,
    error_message="輸入過長"
)

# 輸出驗證
output_guardrail = Guardrail(
    type="output",
    validator=lambda msg: not contains_sensitive_data(msg),
    error_message="輸出包含敏感信息"
)

agent = Agent(
    name="安全助手",
    guardrails=[input_guardrail, output_guardrail]
)
```

### 4. Session 管理

**使用持久化存儲：**
```python
# 生產環境
session = Session(
    agent=agent,
    storage="redis://prod-redis:6379/0",
    ttl=86400  # 24 小時
)

# 開發環境
session = Session(
    agent=agent,
    storage="memory",  # 內存存儲
)
```

### 5. 監控和追蹤

**關鍵路徑追蹤：**
```python
from openai_agents import trace_run

with trace_run(name="訂單處理") as tracer:
    tracer.add_metadata({
        "order_id": order_id,
        "customer_id": customer_id
    })

    result = session.run(f"處理訂單 {order_id}")

    # 記錄關鍵指標
    tracer.log_metric("processing_time", tracer.elapsed_time)
    tracer.log_metric("tokens_used", result.usage.total_tokens)
```

---

## 進階主題

### 並發處理

```python
import asyncio
from openai_agents import Agent, run_async

async def process_multiple_queries():
    agent = Agent(name="助手", model="gpt-4")

    tasks = [
        run_async(agent, [{"role": "user", "content": q}])
        for q in ["問題1", "問題2", "問題3"]
    ]

    results = await asyncio.gather(*tasks)
    return results
```

### 自定義存儲後端

```python
from openai_agents import StorageBackend

class CustomStorage(StorageBackend):
    def save(self, session_id: str, data: dict):
        # 實現保存邏輯
        pass

    def load(self, session_id: str) -> dict:
        # 實現加載邏輯
        pass

session = Session(agent=agent, storage=CustomStorage())
```

### 動態工具加載

```python
def load_tools_for_user(user_id: str) -> list:
    """根據用戶權限動態加載工具"""
    permissions = get_user_permissions(user_id)
    tools = []

    if "admin" in permissions:
        tools.append(admin_tool)
    if "sales" in permissions:
        tools.append(sales_tool)

    return tools

agent = Agent(
    name="個性化助手",
    tools=load_tools_for_user(current_user_id)
)
```

---

## 生產部署

### Docker 部署

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

### 環境變量管理

```python
from openai_agents import configure
import os

configure(
    api_key=os.getenv("OPENAI_API_KEY"),
    default_model=os.getenv("DEFAULT_MODEL", "gpt-4"),
    timeout=int(os.getenv("TIMEOUT", "60")),
    max_retries=int(os.getenv("MAX_RETRIES", "3"))
)
```

### 錯誤處理和重試

```python
from openai_agents import Agent, run
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def run_with_retry(agent, messages):
    return run(agent=agent, messages=messages)
```

---

## 故障排除

### 常見問題

**Q: 如何處理 API 限流？**
```python
from openai_agents import configure

configure(
    max_retries=5,
    timeout=120,
    retry_on_rate_limit=True
)
```

**Q: Session 無法持久化？**
```python
# 檢查 Redis 連接
import redis
r = redis.from_url("redis://localhost:6379")
r.ping()  # 應該返回 True

# 使用正確的 URL 格式
session = Session(
    agent=agent,
    storage="redis://localhost:6379/0"  # /0 指定數據庫
)
```

**Q: 工具調用失敗？**
```python
# 確保工具有正確的類型提示
@tool
def my_tool(param: str) -> dict:  # 必須有類型提示
    """必須有文檔字符串"""
    return {"result": "..."}
```

### 日誌配置

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("openai_agents")
logger.setLevel(logging.DEBUG)
```

---

## 資源和參考

- 官方文檔：https://openai.com/docs/agents
- GitHub：https://github.com/openai/openai-agents-python
- 社區：https://community.openai.com/c/agents
- 範例庫：https://github.com/openai/agents-examples

---

## 總結

OpenAI Agents SDK 提供了從實驗到生產的完整路徑：

1. **簡單上手** - 保持 Swarm 的簡潔性
2. **功能強大** - Guardrails、Sessions、Tracing
3. **生產就緒** - 完整的監控、錯誤處理、持久化
4. **生態豐富** - LiteLLM、Temporal 整合

無論是簡單的聊天機器人還是複雜的企業級 Agent 系統，Agents SDK 都能提供合適的解決方案。

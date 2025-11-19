# OpenAI Swarm - 輕量級多 Agent 協作框架

<div align="center">

![Swarm Logo](https://img.shields.io/badge/OpenAI-Swarm-412991?style=for-the-badge&logo=openai)
![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**輕量級、可控、可測試的多 Agent 編排框架**

[官方倉庫](https://github.com/openai/swarm) | [API 文檔](https://platform.openai.com/docs) | [示例代碼](./01_多Agent協作.py)

</div>

---

## 📚 目錄

- [簡介](#-簡介)
- [核心特點](#-核心特點)
- [核心概念](#-核心概念)
- [快速開始](#-快速開始)
- [詳細教程](#-詳細教程)
- [實際應用場景](#-實際應用場景)
- [框架對比](#-框架對比)
- [最佳實踐](#-最佳實踐)
- [常見問題](#-常見問題)
- [參考資源](#-參考資源)

---

## 🎯 簡介

### 什麼是 OpenAI Swarm？

**OpenAI Swarm** 是由 OpenAI 於 2024 年底發布的**實驗性**多 Agent 編排框架。它專注於使 Agent 協調和執行變得輕量、可控且易於測試。

### 為什麼選擇 Swarm？

與現有的 Agent 框架不同，Swarm 不是一個獨立的庫，而是一套**編排模式**的實現參考：

- **輕量級**：核心代碼不到 500 行
- **可控性**：完全透明的執行流程
- **可測試**：每個組件都易於單元測試
- **靈活性**：基於函數調用的簡單抽象
- **教育性**：展示如何構建多 Agent 系統

### 適用場景

✅ **適合**：
- 需要多個專業 Agent 協作的場景
- 客服系統、客戶支持
- 任務路由和分發
- 教育和原型開發

❌ **不適合**：
- 高度自主的 Agent
- 複雜的記憶管理
- 長期運行的工作流
- 生產級部署（實驗性質）

---

## ⭐ 核心特點

### 1. 簡單性

```python
from swarm import Swarm, Agent

# 定義 Agent 就這麼簡單
agent = Agent(
    name="助手",
    instructions="你是一個友好的助手",
)

# 運行也很簡單
client = Swarm()
response = client.run(agent=agent, messages=[{"role": "user", "content": "你好"}])
```

### 2. Agent 切換（Handoffs）

```python
def transfer_to_expert():
    """切換到專家 Agent"""
    return expert_agent

basic_agent = Agent(
    name="基礎助手",
    instructions="遇到複雜問題轉給專家",
    functions=[transfer_to_expert]
)
```

### 3. 函數工具

```python
def get_weather(location: str) -> str:
    """獲取天氣信息"""
    return f"{location} 的天氣是晴天"

agent = Agent(
    name="天氣助手",
    functions=[get_weather]
)
```

### 4. 上下文共享

```python
# 消息歷史在 Agent 之間共享
messages = [{"role": "user", "content": "幫我處理訂單"}]

# Agent A 處理
response = client.run(agent=agent_a, messages=messages)

# Agent B 繼續（保留上下文）
response = client.run(agent=agent_b, messages=response.messages)
```

---

## 🧩 核心概念

### 1. Agent（智能體）

Agent 是 Swarm 的基本單位，包含三個核心要素：

```python
from swarm import Agent

agent = Agent(
    name="客服助手",           # Agent 名稱
    instructions="...",       # 系統提示（角色定義）
    functions=[func1, func2], # 可用的函數工具
    model="gpt-4",           # 使用的模型（可選）
)
```

**關鍵特性**：
- **無狀態**：Agent 本身不保存狀態
- **可組合**：可以自由組合和切換
- **專業化**：每個 Agent 負責特定領域

### 2. Handoffs（切換）

Agent 之間的切換是通過**返回 Agent 對象**實現的：

```python
def transfer_to_sales():
    """轉接到銷售部門"""
    return sales_agent  # 返回 Agent 對象觸發切換

customer_service = Agent(
    name="客服",
    instructions="處理一般問題，銷售問題轉給銷售",
    functions=[transfer_to_sales]
)
```

**切換模式**：
- **主動切換**：Agent 決定何時切換
- **條件切換**：基於特定條件
- **雙向切換**：可以切換回原 Agent

### 3. Functions（函數工具）

函數是 Agent 與外部世界交互的方式：

```python
def search_database(query: str) -> str:
    """搜索數據庫

    Args:
        query: 搜索關鍵詞

    Returns:
        搜索結果
    """
    # 實際搜索邏輯
    return "搜索結果"

# 函數簽名和文檔字符串很重要！
# LLM 使用它們來決定何時調用
```

**函數類型**：
- **信息查詢**：獲取數據
- **操作執行**：執行動作
- **Agent 切換**：返回 Agent 對象

### 4. Context Variables（上下文變量）

在 Agent 之間共享狀態：

```python
from swarm import Agent

def process_order(context_variables: dict):
    user_id = context_variables.get("user_id")
    # 使用共享上下文
    return f"處理用戶 {user_id} 的訂單"

agent = Agent(
    name="訂單處理",
    functions=[process_order]
)

# 運行時提供上下文
response = client.run(
    agent=agent,
    messages=messages,
    context_variables={"user_id": "12345"}
)
```

---

## 🚀 快速開始

### 1. 安裝

```bash
# 從 GitHub 安裝（官方未發布到 PyPI）
pip install git+https://github.com/openai/swarm.git

# 安裝 OpenAI SDK
pip install openai

# 或使用本項目的 requirements.txt
pip install -r requirements.txt
```

### 2. 設置 API Key

```bash
# 方法 1: 環境變量
export OPENAI_API_KEY='your-api-key-here'

# 方法 2: .env 文件
echo "OPENAI_API_KEY=your-api-key-here" > .env

# Python 中加載
from dotenv import load_dotenv
load_dotenv()
```

### 3. 第一個 Agent

```python
from swarm import Swarm, Agent

# 創建 Agent
agent = Agent(
    name="友好助手",
    instructions="你是一個友好、樂於助人的 AI 助手。"
)

# 初始化客戶端
client = Swarm()

# 運行對話
messages = [{"role": "user", "content": "你好！"}]
response = client.run(agent=agent, messages=messages)

# 輸出回應
print(response.messages[-1]["content"])
```

### 4. 運行示例

```bash
# 運行多 Agent 協作示例
python 01_多Agent協作.py
```

---

## 📖 詳細教程

### 教程 1：基礎 Agent

創建一個簡單的助手：

```python
from swarm import Swarm, Agent

# 定義 Agent
simple_agent = Agent(
    name="數學助手",
    instructions="""你是一個數學助手。
    幫助用戶解決數學問題，提供清晰的步驟說明。"""
)

# 使用 Agent
client = Swarm()
messages = [{"role": "user", "content": "什麼是二次方程式？"}]

response = client.run(
    agent=simple_agent,
    messages=messages
)

print(response.messages[-1]["content"])
```

### 教程 2：使用函數工具

為 Agent 添加能力：

```python
def calculate(expression: str) -> str:
    """計算數學表達式

    Args:
        expression: 數學表達式，如 "2 + 2"

    Returns:
        計算結果
    """
    try:
        result = eval(expression)
        return f"結果是：{result}"
    except Exception as e:
        return f"計算錯誤：{str(e)}"


def get_formula(formula_name: str) -> str:
    """獲取數學公式

    Args:
        formula_name: 公式名稱

    Returns:
        公式說明
    """
    formulas = {
        "二次方程": "ax² + bx + c = 0，解為 x = (-b ± √(b²-4ac)) / 2a",
        "畢達哥拉斯定理": "a² + b² = c²",
    }
    return formulas.get(formula_name, "未找到該公式")


# 創建帶工具的 Agent
math_agent = Agent(
    name="數學專家",
    instructions="你是數學專家，可以計算表達式和提供公式",
    functions=[calculate, get_formula]
)

# 測試
messages = [{"role": "user", "content": "計算 25 * 4"}]
response = client.run(agent=math_agent, messages=messages)
print(response.messages[-1]["content"])
```

### 教程 3：Agent 切換

實現多 Agent 協作：

```python
# 定義專家 Agent
spanish_agent = Agent(
    name="西班牙語專家",
    instructions="你是西班牙語專家，用西班牙語回答問題。"
)

french_agent = Agent(
    name="法語專家",
    instructions="你是法語專家，用法語回答問題。"
)


# 定義切換函數
def transfer_to_spanish():
    """轉接到西班牙語專家"""
    return spanish_agent


def transfer_to_french():
    """轉接到法語專家"""
    return french_agent


# 定義路由 Agent
router_agent = Agent(
    name="語言路由",
    instructions="""你是語言服務路由。
    根據用戶需求轉接到對應的語言專家：
    - 西班牙語問題 → 轉接西班牙語專家
    - 法語問題 → 轉接法語專家
    """,
    functions=[transfer_to_spanish, transfer_to_french]
)

# 測試切換
messages = [{"role": "user", "content": "我想學西班牙語的問候語"}]
response = client.run(agent=router_agent, messages=messages)

print(f"當前 Agent: {response.agent.name}")
print(f"回應: {response.messages[-1]['content']}")
```

### 教程 4：上下文管理

在 Agent 之間共享信息：

```python
def check_balance(context_variables: dict) -> str:
    """查詢賬戶餘額"""
    user_id = context_variables.get("user_id", "未知")
    # 模擬查詢
    balance = 1000.50
    return f"用戶 {user_id} 的餘額是：${balance:.2f}"


def transfer_money(amount: float, to_account: str, context_variables: dict) -> str:
    """轉賬"""
    user_id = context_variables.get("user_id", "未知")
    return f"已從用戶 {user_id} 轉賬 ${amount:.2f} 到 {to_account}"


banking_agent = Agent(
    name="銀行助手",
    instructions="你是銀行助手，可以查詢餘額和轉賬",
    functions=[check_balance, transfer_money]
)

# 運行時提供上下文
response = client.run(
    agent=banking_agent,
    messages=[{"role": "user", "content": "查詢我的餘額"}],
    context_variables={"user_id": "USER_12345"}
)
```

### 教程 5：完整對話流程

實現多輪對話：

```python
def run_conversation():
    """運行完整對話"""
    agent = Agent(
        name="助手",
        instructions="你是友好的助手"
    )

    messages = []

    print("開始對話（輸入 'quit' 退出）\n")

    while True:
        # 獲取用戶輸入
        user_input = input("你: ")
        if user_input.lower() == 'quit':
            break

        # 添加到消息歷史
        messages.append({"role": "user", "content": user_input})

        # 運行 Swarm
        response = client.run(agent=agent, messages=messages)

        # 獲取回應
        assistant_message = response.messages[-1]["content"]
        print(f"助手: {assistant_message}\n")

        # 更新消息歷史（包含函數調用等）
        messages = response.messages

# 運行
run_conversation()
```

---

## 🎨 實際應用場景

### 場景 1：智能客服系統

**需求**：多層級客服，自動路由到專業部門

**實現**：見 `01_多Agent協作.py`

**特點**：
- 接待員負責初步接待和路由
- 銷售、技術支持、退款各司其職
- 無縫切換，保持上下文
- 可擴展新的專業部門

### 場景 2：個人助理系統

```python
# 日程管理
calendar_agent = Agent(
    name="日程助手",
    instructions="管理日程、會議、提醒",
    functions=[add_event, check_schedule, set_reminder]
)

# 郵件處理
email_agent = Agent(
    name="郵件助手",
    instructions="處理郵件、撰寫回復",
    functions=[read_email, send_email, draft_reply]
)

# 任務管理
task_agent = Agent(
    name="任務助手",
    instructions="管理待辦事項、項目任務",
    functions=[add_task, complete_task, list_tasks]
)

# 主助理（路由）
main_assistant = Agent(
    name="個人助理",
    instructions="根據需求分配給專業助手",
    functions=[
        transfer_to_calendar,
        transfer_to_email,
        transfer_to_task
    ]
)
```

### 場景 3：教育輔導系統

```python
# 數學老師
math_tutor = Agent(
    name="數學老師",
    instructions="教授數學，提供練習題和解答",
    functions=[generate_problem, check_answer, explain_concept]
)

# 物理老師
physics_tutor = Agent(
    name="物理老師",
    instructions="教授物理，做實驗演示",
    functions=[explain_physics, simulate_experiment]
)

# 化學老師
chemistry_tutor = Agent(
    name="化學老師",
    instructions="教授化學，解釋化學反應",
    functions=[explain_reaction, balance_equation]
)

# 教務助手（路由）
education_assistant = Agent(
    name="教務助手",
    instructions="根據學科需求分配給對應老師",
    functions=[to_math, to_physics, to_chemistry]
)
```

### 場景 4：內容創作團隊

```python
# 研究員
researcher = Agent(
    name="研究員",
    instructions="收集資料、事實核查",
    functions=[search_web, verify_facts]
)

# 作家
writer = Agent(
    name="作家",
    instructions="撰寫文章、創作內容",
    functions=[write_draft, revise_content]
)

# 編輯
editor = Agent(
    name="編輯",
    instructions="審核、修改、優化內容",
    functions=[review_content, suggest_improvements]
)

# 協調員
coordinator = Agent(
    name="項目協調",
    instructions="協調創作流程",
    functions=[to_researcher, to_writer, to_editor]
)
```

---

## 🔄 框架對比

### Swarm vs AutoGen vs CrewAI

| 特性 | OpenAI Swarm | AutoGen | CrewAI |
|------|--------------|---------|--------|
| **定位** | 輕量級編排模式 | 通用對話框架 | 角色扮演協作 |
| **複雜度** | 極簡（<500行） | 中等 | 較高 |
| **學習曲線** | 平緩 | 中等 | 陡峭 |
| **Agent 切換** | ✅ 簡單直接 | ✅ 支持 | ✅ 支持 |
| **自主性** | ❌ 低 | ✅ 高 | ✅ 高 |
| **記憶管理** | ❌ 基礎 | ✅ 高級 | ✅ 支持 |
| **工作流** | ❌ 簡單 | ✅ 複雜 | ✅ 流程化 |
| **測試性** | ✅ 優秀 | ⚠️ 中等 | ⚠️ 中等 |
| **生產就緒** | ❌ 實驗性 | ✅ 是 | ✅ 是 |
| **適用場景** | 原型、教育 | 通用 AI 應用 | 團隊協作任務 |

### 選擇建議

**選擇 Swarm 當**：
- 需要快速原型開發
- 學習多 Agent 系統
- 需要完全可控的執行流程
- Agent 協作模式簡單明確

**選擇 AutoGen 當**：
- 需要複雜的對話模式
- 需要高度自主的 Agent
- 構建生產級應用
- 需要人機協作

**選擇 CrewAI 當**：
- 任務有明確的角色分工
- 需要流程化的工作流
- 模擬真實團隊協作
- 需要任務規劃能力

---

## 💡 最佳實踐

### 1. Agent 設計原則

**單一職責**：
```python
# ✅ 好的設計
sales_agent = Agent(
    name="銷售專員",
    instructions="只負責產品銷售相關問題"
)

# ❌ 避免
everything_agent = Agent(
    name="全能助手",
    instructions="處理所有問題"  # 太寬泛
)
```

**清晰的指令**：
```python
# ✅ 清晰具體
agent = Agent(
    name="客服",
    instructions="""你是客服專員。職責：
    1. 熱情接待客戶
    2. 解答產品問題
    3. 複雜問題轉技術支持
    4. 使用禮貌、專業的語氣
    """
)

# ❌ 模糊不清
agent = Agent(
    name="客服",
    instructions="幫助客戶"  # 太籠統
)
```

### 2. 函數設計原則

**描述性文檔**：
```python
# ✅ 好的函數
def search_product(
    category: str,
    max_price: float = None,
    in_stock: bool = True
) -> str:
    """搜索產品

    Args:
        category: 產品類別（如 "電子產品"、"服裝"）
        max_price: 最高價格（可選）
        in_stock: 是否只顯示有貨商品（默認 True）

    Returns:
        產品列表的 JSON 字符串
    """
    pass

# ❌ 避免
def search(cat, p=None, s=True):  # 參數名不清晰
    pass  # 沒有文檔
```

**錯誤處理**：
```python
def get_user_info(user_id: str) -> str:
    """獲取用戶信息"""
    try:
        # 查詢邏輯
        user = database.get_user(user_id)
        if not user:
            return f"用戶 {user_id} 不存在"
        return format_user_info(user)
    except Exception as e:
        return f"查詢失敗：{str(e)}"
```

### 3. 切換策略

**明確的切換條件**：
```python
def transfer_to_technical():
    """轉接到技術支持

    適用場景：
    - 產品故障
    - 使用問題
    - 技術諮詢
    """
    return technical_agent

agent = Agent(
    name="客服",
    instructions="""遇到以下情況轉技術支持：
    - 用戶報告產品故障
    - 詢問使用方法
    - 技術參數問題
    """,
    functions=[transfer_to_technical]
)
```

**雙向切換**：
```python
# 允許切換回來
def back_to_main():
    return main_agent

specialized_agent = Agent(
    name="專員",
    instructions="處理完畢後可以切回主助手",
    functions=[back_to_main]
)
```

### 4. 上下文管理

**最小必要原則**：
```python
# 只傳遞必要的上下文
context = {
    "user_id": "12345",
    "session_id": "abc",
    "language": "zh-TW"
}

# 避免傳遞過多不必要的數據
```

**不可變數據**：
```python
# 在函數中不要修改 context_variables
def process(context_variables: dict):
    # ❌ 不要這樣做
    # context_variables["new_key"] = "value"

    # ✅ 需要新數據時返回
    return Result(
        value="result",
        context_variables={"new_key": "value"}
    )
```

### 5. 測試策略

**單元測試 Agent**：
```python
import pytest
from swarm import Swarm, Agent

def test_basic_agent():
    agent = Agent(
        name="測試助手",
        instructions="簡單回答問題"
    )

    client = Swarm()
    response = client.run(
        agent=agent,
        messages=[{"role": "user", "content": "你好"}]
    )

    assert response.messages[-1]["role"] == "assistant"
    assert len(response.messages[-1]["content"]) > 0
```

**測試函數調用**：
```python
def test_function_calling():
    def get_time() -> str:
        return "12:00"

    agent = Agent(
        name="時間助手",
        instructions="告訴用戶時間",
        functions=[get_time]
    )

    client = Swarm()
    response = client.run(
        agent=agent,
        messages=[{"role": "user", "content": "現在幾點？"}]
    )

    # 檢查是否調用了函數
    assert any(msg.get("tool_calls") for msg in response.messages)
```

---

## ❓ 常見問題

### Q1: Swarm 是生產就緒的嗎？

**A**: **不是**。Swarm 是實驗性項目，用於探索多 Agent 編排模式。不建議直接用於生產環境。

### Q2: Swarm 與 OpenAI Assistants API 有什麼區別？

**A**:
- **Assistants API**：託管服務，處理狀態、記憶、工具
- **Swarm**：客戶端庫，完全由你控制執行流程

### Q3: 如何處理 Agent 切換循環？

**A**:
```python
# 在 instructions 中明確切換條件
agent = Agent(
    instructions="""
    處理完問題後不要反覆切換。
    只在必要時切換一次。
    """
)

# 或在代碼中限制切換次數
max_switches = 5
switch_count = 0

while switch_count < max_switches:
    response = client.run(agent=current_agent, messages=messages)
    if response.agent != current_agent:
        switch_count += 1
    current_agent = response.agent
```

### Q4: 可以使用其他 LLM（非 OpenAI）嗎？

**A**: 目前 Swarm 只支持 OpenAI 模型。如需其他模型，需要修改源碼或等待社區支持。

### Q5: 如何保存和恢復對話？

**A**:
```python
import json

# 保存
conversation_state = {
    "messages": messages,
    "current_agent": current_agent.name,
    "context": context_variables
}

with open("conversation.json", "w") as f:
    json.dump(conversation_state, f)

# 恢復
with open("conversation.json", "r") as f:
    state = json.load(f)

messages = state["messages"]
current_agent = agent_map[state["current_agent"]]
context_variables = state["context"]
```

### Q6: 如何處理並發請求？

**A**: Swarm 本身是同步的。並發需要：
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=5)

def handle_request(user_id, message):
    client = Swarm()  # 每個線程獨立客戶端
    return client.run(agent=agent, messages=[{"role": "user", "content": message}])

# 使用線程池
futures = [
    executor.submit(handle_request, user_id, message)
    for user_id, message in requests
]
```

### Q7: 如何計算 Token 使用量？

**A**:
```python
response = client.run(agent=agent, messages=messages)

# 檢查使用量（如果可用）
if hasattr(response, 'usage'):
    print(f"Tokens 使用: {response.usage}")
```

### Q8: 可以自定義模型參數嗎？

**A**:
```python
agent = Agent(
    name="助手",
    instructions="...",
    model="gpt-4-turbo-preview",  # 指定模型
)

# 運行時參數
response = client.run(
    agent=agent,
    messages=messages,
    model_override="gpt-4",  # 覆蓋模型
    temperature=0.7,          # 自定義參數（如果支持）
)
```

---

## 📚 參考資源

### 官方資源

- [Swarm GitHub 倉庫](https://github.com/openai/swarm)
- [OpenAI 官方文檔](https://platform.openai.com/docs)
- [OpenAI Cookbook](https://github.com/openai/openai-cookbook)

### 相關框架

- [AutoGen](https://github.com/microsoft/autogen)
- [CrewAI](https://github.com/joaomdmoura/crewAI)
- [LangChain](https://github.com/langchain-ai/langchain)
- [LlamaIndex](https://github.com/run-llama/llama_index)

### 學習資源

- [多 Agent 系統設計模式](https://www.deeplearning.ai/short-courses/ai-agents-in-langgraph/)
- [Function Calling 最佳實踐](https://platform.openai.com/docs/guides/function-calling)
- [提示工程指南](https://www.promptingguide.ai/)

### 社區

- [OpenAI 社區論壇](https://community.openai.com/)
- [Reddit r/OpenAI](https://www.reddit.com/r/OpenAI/)
- [Discord 服務器](https://discord.gg/openai)

---

## 🎓 總結

### 核心要點

1. **Swarm 是輕量級的**：不到 500 行代碼，易於理解和定制
2. **基於編排模式**：展示如何構建多 Agent 系統，而非完整框架
3. **適合學習**：了解多 Agent 協作的絕佳起點
4. **實驗性質**：不建議直接用於生產環境

### 何時使用 Swarm

- ✅ 快速原型開發
- ✅ 學習多 Agent 系統
- ✅ 需要完全控制執行流程
- ✅ 教育和演示

### 下一步

1. **運行示例**：`python 01_多Agent協作.py`
2. **閱讀源碼**：Swarm 代碼量小，易於理解
3. **構建應用**：基於你的需求定制
4. **探索其他框架**：AutoGen、CrewAI 等

---

## 📝 許可證

本教程基於 MIT 許可證開源。

OpenAI Swarm 同樣採用 MIT 許可證。

---

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

---

<div align="center">

**Happy Coding with Swarm!** 🐝

Made with ❤️ by AI Enthusiasts

</div>

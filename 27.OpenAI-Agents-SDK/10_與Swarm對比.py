"""
OpenAI Agents SDK vs Swarm 詳細對比

展示兩個框架的差異和遷移方法
包含：代碼對比、功能對比、遷移指南
"""

import os
from openai_agents import Agent, tool, handoff_to, run, Session, Guardrail, trace_run, configure

print("""
="*80)
OpenAI Agents SDK vs Swarm 完整對比
="*80)

# ============================================================================
# 1. 基本概念對比
# ============================================================================

【Swarm】
  - OpenAI 實驗性項目（2024年10月發布）
  - 輕量級多 Agent 協調
  - 設計目標：簡單、教育性、可控
  - 狀態：實驗性，不推薦生產使用

【Agents SDK】
  - OpenAI 官方生產級框架
  - Swarm 的正式升級版
  - 設計目標：生產就緒、功能完整、可擴展
  - 狀態：穩定版本，推薦生產使用

# ============================================================================
# 2. 代碼對比
# ============================================================================

## 2.1 Hello World 對比

### Swarm 版本:
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

print(response.messages[-1]["content"])
```

### Agents SDK 版本:
```python
from openai_agents import Agent, run, configure

configure(api_key="...")  # 全局配置

agent = Agent(
    name="助手",
    instructions="你是助手"
)

response = run(  # 不需要 client
    agent=agent,
    messages=[{"role": "user", "content": "你好"}]
)

print(response.messages[-1]["content"])
```

**主要差異：**
1. Agents SDK 不需要創建 client 實例
2. 支持全局配置（configure）
3. 更簡潔的 API

## 2.2 工具函數對比

### Swarm 版本:
```python
def get_weather(city):
    '''獲取天氣'''
    return f"{city} 的天氣是晴天"

agent = Agent(
    name="天氣助手",
    functions=[get_weather]  # 使用 functions
)
```

### Agents SDK 版本:
```python
from openai_agents import tool

@tool  # 使用裝飾器
def get_weather(city: str) -> str:  # 類型提示必須
    '''獲取天氣

    Args:
        city: 城市名稱

    Returns:
        天氣信息
    '''
    return f"{city} 的天氣是晴天"

agent = Agent(
    name="天氣助手",
    tools=[get_weather]  # 使用 tools
)
```

**主要差異：**
1. 使用 @tool 裝飾器（自動生成 schema）
2. 必須提供類型提示
3. 參數名從 functions 改為 tools
4. 更好的文檔字符串支持

## 2.3 Agent 轉移對比

### Swarm 版本:
```python
specialist = Agent(name="專家")

def transfer():
    return specialist  # 直接返回 Agent

general = Agent(
    name="總機",
    functions=[transfer]
)
```

### Agents SDK 版本:
```python
from openai_agents import handoff_to

specialist = Agent(name="專家")

def transfer():
    return handoff_to(specialist)  # 使用 handoff_to

general = Agent(
    name="總機",
    tools=[transfer]
)
```

**主要差異：**
1. 使用 handoff_to() 函數（更明確）
2. 支持轉移元數據
3. 更好的追蹤和日誌

## 2.4 狀態管理對比

### Swarm 版本（手動管理）:
```python
client = Swarm()
messages = []

# 第 1 輪
messages.append({"role": "user", "content": "你好"})
response = client.run(agent, messages)
messages = response.messages  # 手動更新

# 第 2 輪
messages.append({"role": "user", "content": "再見"})
response = client.run(agent, messages)
messages = response.messages  # 再次手動更新
```

### Agents SDK 版本（自動管理）:
```python
from openai_agents import Session

session = Session(agent=agent)

# 第 1 輪
session.run("你好")  # 自動保存歷史

# 第 2 輪
session.run("再見")  # 自動保存歷史
```

**主要差異：**
1. Agents SDK 提供 Session 自動管理
2. 不需要手動維護 messages 列表
3. 支持持久化存儲
4. 可以隨時恢復會話

# ============================================================================
# 3. 功能對比表
# ============================================================================

| 功能 | Swarm | Agents SDK | 說明 |
|------|-------|------------|------|
| **基礎功能** |
| 創建 Agent | ✓ | ✓ | 都支持 |
| 工具調用 | ✓ | ✓ | SDK 有裝飾器 |
| Agent 轉移 | ✓ | ✓ | SDK 使用 handoff_to |
| 多輪對話 | ✓ | ✓ | SDK 有 Session |
| **進階功能** |
| 會話管理 | ✗ | ✓ | SDK 獨有 |
| 持久化存儲 | ✗ | ✓ | SDK 支持多種後端 |
| Guardrails | ✗ | ✓ | SDK 獨有安全驗證 |
| Tracing | ✗ | ✓ | SDK 完整追蹤系統 |
| 自定義指標 | ✗ | ✓ | SDK 支持 |
| 錯誤處理 | 基礎 | 完整 | SDK 更健壯 |
| **生產特性** |
| 性能監控 | ✗ | ✓ | SDK 內建 |
| 成本追蹤 | ✗ | ✓ | SDK 自動計算 |
| 日誌系統 | 簡單 | 完整 | SDK 專業級 |
| 配置管理 | ✗ | ✓ | SDK 全局配置 |
| **LLM 支持** |
| OpenAI | ✓ | ✓ | 都支持 |
| 其他 LLM | ✗ | ✓ | SDK 通過 LiteLLM |
| **工作流** |
| 基礎工作流 | ✓ | ✓ | 都支持 |
| Temporal 整合 | ✗ | ✓ | SDK 支持長工作流 |
| 並發控制 | 手動 | 自動 | SDK 更方便 |
| **開發體驗** |
| TypeScript | ✗ | ✓ | SDK 雙語言支持 |
| 文檔質量 | 基礎 | 完整 | SDK 更詳細 |
| 社區支持 | 小 | 大 | SDK 官方支持 |

# ============================================================================
# 4. 遷移指南
# ============================================================================

## 步驟 1: 更新導入

Swarm:
```python
from swarm import Swarm, Agent
```

Agents SDK:
```python
from openai_agents import Agent, run, Session, configure
```

## 步驟 2: 移除 Client

Swarm:
```python
client = Swarm()
response = client.run(agent, messages)
```

Agents SDK:
```python
# 選項 1: 直接運行（類似 Swarm）
response = run(agent, messages)

# 選項 2: 使用 Session（推薦）
session = Session(agent=agent)
response = session.run("...")
```

## 步驟 3: 更新工具定義

Swarm:
```python
def my_tool(param):
    return "result"

agent = Agent(
    name="...",
    functions=[my_tool]
)
```

Agents SDK:
```python
from openai_agents import tool

@tool
def my_tool(param: str) -> str:  # 添加類型提示
    '''工具描述

    Args:
        param: 參數說明

    Returns:
        返回值說明
    '''
    return "result"

agent = Agent(
    name="...",
    tools=[my_tool]  # functions → tools
)
```

## 步驟 4: 更新 Handoffs

Swarm:
```python
def transfer():
    return other_agent

agent = Agent(
    name="...",
    functions=[transfer]
)
```

Agents SDK:
```python
from openai_agents import handoff_to

def transfer():
    return handoff_to(other_agent)

agent = Agent(
    name="...",
    tools=[transfer]
)
```

## 步驟 5: 添加新功能（可選）

### 5.1 添加 Guardrails
```python
from openai_agents import Guardrail

def validate_input(msg: str) -> bool:
    return len(msg) < 1000

rail = Guardrail(
    type="input",
    validator=validate_input,
    error_message="輸入過長"
)

agent = Agent(
    name="...",
    guardrails=[rail]  # 新功能
)
```

### 5.2 添加 Tracing
```python
from openai_agents import trace_run

with trace_run(name="對話") as tracer:
    response = run(agent, messages)

print(tracer.total_tokens)  # Token 使用
print(tracer.elapsed_time)  # 執行時間
```

### 5.3 使用 Session
```python
from openai_agents import Session

session = Session(
    agent=agent,
    storage="redis://localhost:6379/0",  # 持久化
    ttl=3600
)

response = session.run("...")  # 自動保存歷史
```

# ============================================================================
# 5. 遷移檢查清單
# ============================================================================

□ 更新導入語句
□ 移除 Swarm client
□ 更新函數參數名 (functions → tools)
□ 添加 @tool 裝飾器
□ 添加類型提示
□ 更新 handoff (使用 handoff_to)
□ 考慮使用 Session（推薦）
□ 添加 Guardrails（可選）
□ 添加 Tracing（可選）
□ 更新錯誤處理
□ 測試所有功能
□ 更新文檔

# ============================================================================
# 6. 為什麼要遷移？
# ============================================================================

從 Swarm 遷移到 Agents SDK 的理由：

1. **官方支持**
   - Swarm: 實驗性項目，可能停止維護
   - Agents SDK: 官方生產級框架，長期支持

2. **生產就緒**
   - Swarm: 僅用於學習和原型
   - Agents SDK: 完整的生產特性（監控、日誌、錯誤處理）

3. **功能完整**
   - Session 管理（自動化狀態）
   - Guardrails（安全驗證）
   - Tracing（性能監控）
   - 多 LLM 支持

4. **性能優化**
   - 更好的錯誤處理
   - 自動重試機制
   - 並發控制
   - 資源管理

5. **開發體驗**
   - 更好的文檔
   - 類型檢查
   - 調試工具
   - 社區支持

# ============================================================================
# 7. 遷移時間線建議
# ============================================================================

**階段 1: 評估（1-2 天）**
- 審查現有 Swarm 代碼
- 識別需要遷移的部分
- 評估工作量

**階段 2: 準備（2-3 天）**
- 設置 Agents SDK 環境
- 學習新 API
- 準備測試計劃

**階段 3: 遷移（3-5 天）**
- 逐步遷移代碼
- 添加測試
- 解決兼容性問題

**階段 4: 增強（2-3 天）**
- 添加 Guardrails
- 添加 Tracing
- 使用 Session

**階段 5: 驗證（2-3 天）**
- 完整測試
- 性能驗證
- 文檔更新

**總計: 10-16 天**

# ============================================================================
# 8. 常見問題
# ============================================================================

Q: 必須遷移嗎？
A: 如果是生產環境，強烈建議遷移。Swarm 是實驗性項目。

Q: 遷移會破壞現有代碼嗎？
A: 基本 API 兼容，需要一些語法調整，但邏輯可以保持。

Q: 遷移後性能會更好嗎？
A: 是的，Agents SDK 有更好的優化和錯誤處理。

Q: 可以逐步遷移嗎？
A: 可以，建議先遷移非關鍵部分，驗證後再完整遷移。

Q: 兩個框架可以共存嗎？
A: 技術上可以，但不建議長期共存，應盡快完成遷移。

# ============================================================================
# 9. 總結
# ============================================================================

OpenAI Agents SDK 是 Swarm 的正式升級版：
✓ 保持了 Swarm 的簡潔性
✓ 增加了生產級特性
✓ 官方長期支持
✓ 更完整的功能
✓ 更好的開發體驗

遷移建議：
✓ 新項目：直接使用 Agents SDK
✓ 現有項目：儘快規劃遷移
✓ 學習項目：可以繼續使用 Swarm 學習概念

="*80)
""")


# ============================================================================
# 實際遷移示例
# ============================================================================

def swarm_example():
    """Swarm 風格代碼示例（偽代碼）"""
    print("\n" + "="*60)
    print("Swarm 風格代碼示例")
    print("="*60)

    print("""
# 這是 Swarm 風格的代碼（偽代碼示例）

from swarm import Swarm, Agent

# 1. 創建 client
client = Swarm()

# 2. 定義工具
def get_weather(city):
    return f"{city} 天氣晴"

# 3. 創建 Agent
agent = Agent(
    name="助手",
    instructions="你是助手",
    functions=[get_weather]
)

# 4. 運行對話
messages = []
messages.append({"role": "user", "content": "台北天氣？"})
response = client.run(agent=agent, messages=messages)

# 5. 手動管理歷史
messages = response.messages
messages.append({"role": "user", "content": "謝謝"})
response = client.run(agent=agent, messages=messages)
    """)


def agents_sdk_example():
    """Agents SDK 風格代碼示例（實際代碼）"""
    print("\n" + "="*60)
    print("Agents SDK 風格代碼示例（實際運行）")
    print("="*60)

    # 1. 配置
    configure(
        api_key=os.getenv("OPENAI_API_KEY"),
        timeout=60
    )

    # 2. 定義工具
    @tool
    def get_weather(city: str) -> str:
        """獲取天氣"""
        return f"{city} 天氣晴"

    # 3. 創建 Agent
    agent = Agent(
        name="助手",
        instructions="你是助手，使用繁體中文。",
        tools=[get_weather]
    )

    # 4. 使用 Session（自動管理歷史）
    session = Session(agent=agent)

    print("\n執行對話:")
    print("用戶: 台北天氣？")
    response1 = session.run("台北天氣？")
    print(f"助手: {response1.messages[-1]['content']}")

    print("\n用戶: 謝謝")
    response2 = session.run("謝謝")
    print(f"助手: {response2.messages[-1]['content']}")

    print("\n✓ 歷史自動保存，無需手動管理")


def migration_complete_example():
    """完整遷移示例"""
    print("\n" + "="*60)
    print("完整遷移示例：添加新功能")
    print("="*60)

    configure(api_key=os.getenv("OPENAI_API_KEY"))

    # 添加 Guardrail
    def validate(msg: str) -> bool:
        return len(msg) < 500

    rail = Guardrail(
        type="input",
        validator=validate,
        error_message="輸入過長"
    )

    # 工具
    @tool
    def search(query: str) -> str:
        """搜索"""
        return f"搜索結果: {query}"

    # Agent with Guardrail
    agent = Agent(
        name="增強助手",
        instructions="你是助手，使用繁體中文。",
        tools=[search],
        guardrails=[rail]  # 新功能
    )

    # Session with Tracing
    session = Session(agent=agent)

    with trace_run(name="增強對話") as tracer:
        response = session.run("搜索 Python")

    print(f"\n回應: {response.messages[-1]['content'][:100]}...")
    print(f"\n性能指標:")
    print(f"  耗時: {tracer.elapsed_time:.2f}s")
    print(f"  Token: {tracer.total_tokens}")
    print("\n✓ 這些功能 Swarm 都沒有！")


def main():
    """運行所有示例"""
    print("="*60)
    print("Swarm → Agents SDK 遷移實戰")
    print("="*60)

    try:
        swarm_example()
        agents_sdk_example()
        migration_complete_example()
    except Exception as e:
        print(f"\n錯誤: {e}")
        print("（Swarm 示例是偽代碼，Agents SDK 示例需要 API key）")

    print("\n" + "="*60)
    print("遷移指南完成！")
    print("="*60)


if __name__ == "__main__":
    main()

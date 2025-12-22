# Pydantic AI 框架完整範例

## 框架簡介

Pydantic AI 是由 Pydantic 團隊開發的新一代 AI Agent 框架，採用 FastAPI 風格的 API 設計，為 Python 開發者提供最佳的開發體驗。

### 核心特點

#### 1. 完全類型安全 ⚡
- 完整的類型提示支持
- IDE 自動補全和錯誤檢查
- 運行時類型驗證
- 與 mypy、pyright 完美整合

```python
from pydantic_ai import Agent
from pydantic import BaseModel

class UserInfo(BaseModel):
    name: str
    age: int

agent = Agent[None, UserInfo](
    'openai:gpt-4',
    result_type=UserInfo,
)

# 返回值自動驗證為 UserInfo 類型
result = agent.run_sync('Extract: John is 30 years old')
print(result.data.name)  # IDE 知道這是 str
```

#### 2. FastAPI 風格設計 🚀
- 熟悉的裝飾器語法
- 依賴注入系統
- 直觀的 API 設計
- 快速上手

```python
@agent.tool
def get_weather(city: str) -> dict:
    """獲取城市天氣"""
    return {"temp": 25, "condition": "sunny"}

@agent.system_prompt
def get_system_prompt() -> str:
    return "你是一個友善的助手"
```

#### 3. 多模型支持 🌐
支持所有主流 LLM 提供商：
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude 3.5, Claude 3)
- Google (Gemini Pro)
- DeepSeek
- Groq
- Ollama (本地模型)
- 任何 OpenAI 相容 API

```python
# 切換模型只需改變字符串
agent1 = Agent('openai:gpt-4')
agent2 = Agent('anthropic:claude-3-5-sonnet-20241022')
agent3 = Agent('google:gemini-pro')
agent4 = Agent('ollama:llama3')
```

#### 4. MCP + A2A 協議支持 🔗
- Model Context Protocol (MCP) 整合
- Agent-to-Agent (A2A) 通信
- 標準化工具調用
- 跨平台互操作性

#### 5. 持久執行 (Durable Execution) 💾
- 執行狀態持久化
- 錯誤恢復機制
- 長時間運行任務支持
- 斷點續傳

#### 6. Human-in-the-Loop 👥
- 人機協作流程
- 審批機制
- 用戶輸入整合
- 決策點控制

#### 7. Graph 工作流 🕸️
- 複雜工作流定義
- 條件分支
- 循環處理
- 狀態管理

#### 8. Logfire 深度整合 📊
- 實時監控
- 性能追蹤
- 成本分析
- 調試工具

## 安裝指南

### 基礎安裝
```bash
pip install pydantic-ai
```

### 完整安裝（包含所有功能）
```bash
# 基礎 + OpenAI
pip install 'pydantic-ai[openai]'

# 基礎 + Anthropic
pip install 'pydantic-ai[anthropic]'

# 基礎 + Google
pip install 'pydantic-ai[google]'

# 完整安裝（所有提供商）
pip install 'pydantic-ai[all]'

# 包含 Logfire
pip install 'pydantic-ai[logfire]'

# 包含 Graph 支持
pip install 'pydantic-ai[graph]'
```

### 開發環境設置
```bash
# 創建虛擬環境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安裝依賴
pip install 'pydantic-ai[all,logfire]'

# 設置環境變量
export OPENAI_API_KEY='your-key-here'
export ANTHROPIC_API_KEY='your-key-here'
```

## 快速開始

### 第一個 Agent

```python
from pydantic_ai import Agent

# 創建 Agent
agent = Agent('openai:gpt-4')

# 同步運行
result = agent.run_sync('Hello, who are you?')
print(result.data)

# 異步運行
import asyncio

async def main():
    result = await agent.run('Tell me a joke')
    print(result.data)

asyncio.run(main())
```

### 帶工具的 Agent

```python
from pydantic_ai import Agent, RunContext

agent = Agent('openai:gpt-4')

@agent.tool
def calculate(ctx: RunContext, x: int, y: int) -> int:
    """計算兩數之和"""
    return x + y

result = agent.run_sync('What is 123 + 456?')
print(result.data)  # Agent 會調用 calculate 工具
```

### 結構化輸出

```python
from pydantic import BaseModel

class MovieReview(BaseModel):
    title: str
    rating: float
    summary: str

agent = Agent('openai:gpt-4', result_type=MovieReview)

result = agent.run_sync('Review the movie Inception')
review = result.data
print(f"{review.title}: {review.rating}/10")
```

## 範例文件導覽

### 基礎篇

#### 01_基礎Agent.py
- Agent 的創建和配置
- 同步與異步運行
- 基本參數設置
- 錯誤處理

#### 02_類型安全.py
- 完整的類型提示
- Pydantic 模型驗證
- 泛型支持
- 類型安全的工具定義

#### 03_工具定義.py
- 使用 @agent.tool 裝飾器
- 工具參數和返回值
- 工具描述最佳實踐
- 多工具協作

#### 04_依賴注入.py
- RunContext 的使用
- 依賴項定義
- 狀態管理
- 上下文傳遞

### 進階篇

#### 05_結構化輸出.py
- Pydantic 模型作為輸出
- 嵌套模型
- 列表和字典輸出
- 驗證規則

#### 06_對話歷史.py
- 對話上下文管理
- 歷史記錄存取
- 多輪對話
- 上下文窗口控制

#### 07_流式輸出.py
- 流式響應處理
- 實時輸出展示
- 流式工具調用
- 錯誤處理

#### 08_多模型支持.py
- 不同 LLM 提供商
- 模型切換
- Fallback 機制
- 模型比較

### 高級篇

#### 09_Graph工作流.py
- Graph 定義
- 節點和邊
- 條件路由
- 循環處理
- 狀態持久化

#### 10_Human_in_Loop.py
- 人工審批流程
- 用戶輸入整合
- 決策點設計
- 超時處理

#### 11_持久執行.py
- Durable Execution 配置
- 執行狀態保存
- 錯誤恢復
- 斷點續傳

#### 12_Logfire整合.py
- Logfire 設置
- 實時監控
- 性能追蹤
- 成本分析
- 調試工具

## 核心概念

### Agent

Agent 是 Pydantic AI 的核心抽象，代表一個可以執行任務的智能體。

```python
from pydantic_ai import Agent

# 最簡單的 Agent
agent = Agent('openai:gpt-4')

# 帶依賴注入的 Agent
agent = Agent(
    'openai:gpt-4',
    deps_type=MyDependencies,
    result_type=MyResult,
)

# 配置參數
agent = Agent(
    'openai:gpt-4',
    system_prompt='你是一個專業助手',
    retries=3,
)
```

### Tools（工具）

工具允許 Agent 執行特定操作，如調用 API、查詢數據庫等。

```python
@agent.tool
def search_database(ctx: RunContext[MyDeps], query: str) -> list[dict]:
    """在數據庫中搜索"""
    return ctx.deps.db.search(query)
```

### RunContext（運行上下文）

提供工具訪問依賴項和運行時信息的接口。

```python
from pydantic_ai import RunContext

@agent.tool
def my_tool(ctx: RunContext[MyDeps]) -> str:
    # 訪問依賴
    db = ctx.deps.database

    # 訪問運行時信息
    usage = ctx.usage
    messages = ctx.messages

    return "result"
```

### Dependencies（依賴注入）

使用依賴注入模式管理外部資源。

```python
from dataclasses import dataclass

@dataclass
class MyDeps:
    api_key: str
    database: Database

agent = Agent('openai:gpt-4', deps_type=MyDeps)

deps = MyDeps(api_key='xxx', database=db)
result = agent.run_sync('query', deps=deps)
```

### Result Types（結果類型）

使用 Pydantic 模型定義結構化輸出。

```python
class AnalysisResult(BaseModel):
    summary: str
    confidence: float
    tags: list[str]

agent = Agent('openai:gpt-4', result_type=AnalysisResult)
result = agent.run_sync('Analyze this text...')
# result.data 自動驗證為 AnalysisResult
```

## 最佳實踐

### 1. 類型提示

始終使用完整的類型提示：

```python
from typing import Annotated
from pydantic import Field

@agent.tool
def process_data(
    ctx: RunContext[MyDeps],
    value: Annotated[int, Field(gt=0, description="必須為正數")],
) -> dict[str, any]:
    """處理數據"""
    return {"result": value * 2}
```

### 2. 工具設計

- 每個工具做一件事
- 清晰的文檔字符串
- 適當的錯誤處理
- 合理的參數驗證

```python
@agent.tool
def get_weather(
    ctx: RunContext,
    city: str,
    units: Literal["metric", "imperial"] = "metric"
) -> dict:
    """
    獲取指定城市的天氣信息

    Args:
        city: 城市名稱
        units: 溫度單位，metric（攝氏）或 imperial（華氏）

    Returns:
        包含溫度、濕度等信息的字典
    """
    try:
        # 實現邏輯
        return {...}
    except Exception as e:
        raise ToolError(f"無法獲取天氣: {e}")
```

### 3. 錯誤處理

使用 retries 和適當的異常處理：

```python
from pydantic_ai.exceptions import UnexpectedModelBehavior

agent = Agent(
    'openai:gpt-4',
    retries=3,  # 自動重試
)

try:
    result = agent.run_sync('prompt')
except UnexpectedModelBehavior as e:
    print(f"模型行為異常: {e}")
except Exception as e:
    print(f"其他錯誤: {e}")
```

### 4. 性能優化

- 使用流式輸出處理長響應
- 合理設置超時
- 批量處理請求
- 緩存常用結果

```python
# 流式處理
async with agent.run_stream('long task') as response:
    async for chunk in response.stream_text():
        print(chunk, end='', flush=True)

# 設置超時
result = await agent.run('task', timeout=30.0)
```

### 5. 監控和調試

使用 Logfire 追蹤執行：

```python
import logfire

logfire.configure()

agent = Agent('openai:gpt-4')
# 自動記錄所有 Agent 活動
result = agent.run_sync('task')
```

## 常見問題

### Q: 如何選擇模型？

**A:** 根據任務需求選擇：
- 簡單任務：gpt-3.5-turbo, claude-3-haiku
- 複雜推理：gpt-4, claude-3-5-sonnet
- 成本敏感：gemini-pro, ollama 本地模型
- 速度要求：groq 模型

### Q: 工具調用失敗怎麼辦？

**A:** Pydantic AI 提供自動重試機制：
```python
agent = Agent('openai:gpt-4', retries=3)
```

### Q: 如何管理 API 成本？

**A:**
1. 使用 Logfire 追蹤成本
2. 設置合理的 max_tokens
3. 使用較小的模型處理簡單任務
4. 實現緩存機制

### Q: 支持本地模型嗎？

**A:** 支持，通過 Ollama：
```python
agent = Agent('ollama:llama3')
```

## 進階主題

### 自定義模型

實現自己的模型接口：

```python
from pydantic_ai.models import Model, ModelRequestPart

class MyCustomModel(Model):
    async def request(
        self,
        parts: list[ModelRequestPart],
    ) -> ModelResponse:
        # 實現自定義邏輯
        pass
```

### 工具鏈模式

組合多個 Agent：

```python
researcher = Agent('openai:gpt-4', name='researcher')
writer = Agent('openai:gpt-4', name='writer')

# researcher 的結果作為 writer 的輸入
research = await researcher.run('Research topic')
article = await writer.run(f'Write based on: {research.data}')
```

### 向量數據庫整合

結合 RAG 模式：

```python
@agent.tool
async def search_knowledge(ctx: RunContext, query: str) -> str:
    """搜索知識庫"""
    embeddings = await ctx.deps.embedder.embed(query)
    results = await ctx.deps.vector_db.search(embeddings)
    return "\n".join(results)
```

## 參考資源

### 官方文檔
- [Pydantic AI 文檔](https://ai.pydantic.dev/)
- [API 參考](https://ai.pydantic.dev/api/)
- [GitHub 倉庫](https://github.com/pydantic/pydantic-ai)

### 社區資源
- [Discord 社區](https://discord.gg/pydantic)
- [示例項目](https://github.com/pydantic/pydantic-ai/tree/main/examples)
- [變更日誌](https://github.com/pydantic/pydantic-ai/releases)

### 相關工具
- [Pydantic](https://docs.pydantic.dev/) - 數據驗證
- [FastAPI](https://fastapi.tiangolo.com/) - Web 框架
- [Logfire](https://logfire.pydantic.dev/) - 監控平台

## 貢獻指南

歡迎貢獻新的範例或改進現有代碼！

1. Fork 本倉庫
2. 創建功能分支
3. 編寫清晰的註釋
4. 測試代碼
5. 提交 Pull Request

## 授權

本範例集採用 MIT 授權，可自由使用和修改。

## 更新日誌

- **2024-12**: 創建初始範例集
- 包含 12 個完整範例
- 涵蓋所有核心功能
- 繁體中文註釋

---

**開始探索** → 從 `01_基礎Agent.py` 開始你的 Pydantic AI 之旅！

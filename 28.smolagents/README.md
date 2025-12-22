# smolagents - Hugging Face 官方極簡 Agent 框架

smolagents 是 Hugging Face 開發的新一代 Agent 框架，作為 `transformers.agents` 的繼任者。它以極簡設計理念為核心，核心代碼僅約 1000 行，但功能強大且易於使用。

## 目錄

- [框架特點](#框架特點)
- [安裝](#安裝)
- [核心概念](#核心概念)
- [快速開始](#快速開始)
- [範例列表](#範例列表)
- [Code Agent vs Tool Calling Agent](#code-agent-vs-tool-calling-agent)
- [多模態支持](#多模態支持)
- [沙盒執行](#沙盒執行)
- [Hub 整合](#hub-整合)
- [最佳實踐](#最佳實踐)
- [資源連結](#資源連結)

## 框架特點

### 1. 極簡設計 🎯
- **核心代碼僅 ~1000 行**：易於理解、調試和擴展
- **零依賴噪音**：只依賴必要的庫
- **清晰的抽象**：Agent、Tool、Model 三大核心組件

### 2. Code Agent 革新 🚀
- **直接生成 Python 代碼**：不是 JSON 工具調用
- **更強的推理能力**：LLM 直接編寫執行邏輯
- **靈活性更高**：可以使用任何 Python 功能

```python
# 傳統 Tool Calling: LLM 輸出 JSON
{"tool": "calculator", "args": {"a": 5, "b": 3}}

# Code Agent: LLM 輸出 Python 代碼
result = calculator(5, 3)
print(f"計算結果: {result}")
```

### 3. 多模態原生支持 🎨
- **視覺**：圖像理解、生成、編輯
- **音頻**：語音識別、文字轉語音
- **文本**：自然語言處理

### 4. 安全的沙盒執行 🔒
- **E2B**：雲端沙盒環境
- **Modal**：無服務器執行
- **Docker**：容器化隔離
- **WebAssembly**：瀏覽器內執行

### 5. Hub 生態整合 🌐
- **分享工具**：上傳自定義工具到 Hugging Face Hub
- **使用社區工具**：一鍵導入他人的工具
- **版本管理**：完整的版本控制

### 6. 框架互操作性 🔗
- **LangChain 工具**：直接使用 LangChain 生態
- **自定義工具**：簡單的裝飾器創建工具
- **多模型支持**：OpenAI、Anthropic、本地模型

## 安裝

```bash
# 基礎安裝
pip install smolagents

# 包含所有額外功能
pip install smolagents[all]

# 僅安裝特定功能
pip install smolagents[e2b]      # E2B 沙盒
pip install smolagents[modal]    # Modal 執行
pip install smolagents[langchain] # LangChain 工具
```

## 核心概念

### 1. Agent（代理）
Agent 是執行任務的主體，有兩種類型：

- **CodeAgent**：生成並執行 Python 代碼
  - 優點：靈活、強大、可處理複雜邏輯
  - 適用：複雜任務、需要多步驟推理

- **ToolCallingAgent**：傳統的工具調用方式
  - 優點：可控、安全、易於追蹤
  - 適用：簡單任務、需要嚴格控制

### 2. Tool（工具）
工具是 Agent 可以使用的能力：

```python
from smolagents import tool

@tool
def calculator(operation: str, a: float, b: float) -> float:
    """
    執行基本數學運算

    Args:
        operation: 運算類型 ('add', 'subtract', 'multiply', 'divide')
        a: 第一個數字
        b: 第二個數字

    Returns:
        運算結果
    """
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        return a / b if b != 0 else float('inf')
```

### 3. Model（模型）
模型是 Agent 的"大腦"：

- **OpenAI**：GPT-4、GPT-3.5
- **Anthropic**：Claude 3.5 Sonnet
- **Hugging Face**：Hub 上的開源模型
- **本地模型**：通過 Ollama 等運行

## 快速開始

最簡單的 30 行代碼創建一個 Agent：

```python
from smolagents import CodeAgent, HfApiModel, DuckDuckGoSearchTool

# 1. 選擇模型
model = HfApiModel()

# 2. 準備工具
tools = [DuckDuckGoSearchTool()]

# 3. 創建 Agent
agent = CodeAgent(
    tools=tools,
    model=model,
    max_steps=10
)

# 4. 運行任務
result = agent.run("搜索 smolagents 的最新文檔")
print(result)
```

## 範例列表

本目錄包含 11 個詳細範例，從基礎到進階：

| 檔案 | 說明 | 難度 | 重點內容 |
|------|------|------|----------|
| `01_快速入門.py` | 30 行代碼創建第一個 Agent | ⭐ | 基本概念、快速上手 |
| `02_CodeAgent.py` | Code Agent 的原理和優勢 | ⭐⭐ | 代碼生成、執行流程 |
| `03_ToolCallingAgent.py` | 傳統工具調用方式 | ⭐⭐ | 工具調用、對比分析 |
| `04_自定義工具.py` | 創建自己的工具 | ⭐⭐ | 工具開發、最佳實踐 |
| `05_多模態Agent.py` | 視覺和音頻處理 | ⭐⭐⭐ | 多模態、跨領域 |
| `06_沙盒執行.py` | 安全的代碼執行環境 | ⭐⭐⭐ | E2B、安全性 |
| `07_Hub整合.py` | 分享和使用社區工具 | ⭐⭐ | Hub、社區 |
| `08_多Agent系統.py` | 多 Agent 協作 | ⭐⭐⭐⭐ | 協作、編排 |
| `09_LangChain工具.py` | 使用 LangChain 生態 | ⭐⭐⭐ | 互操作性、整合 |
| `10_本地模型.py` | 使用 Ollama 等本地模型 | ⭐⭐ | 本地部署、隱私 |
| `11_流式輸出.py` | 流式響應處理 | ⭐⭐ | 實時反饋、UX |

## Code Agent vs Tool Calling Agent

### Code Agent 的優勢

**1. 更強的推理能力**
```python
# Tool Calling: 需要多次工具調用
search("Python 3.12 新特性") →
read_page(url) →
extract_info(content)

# Code Agent: 一次性完成邏輯
results = search("Python 3.12 新特性")
for result in results[:3]:
    content = read_page(result.url)
    if "type hints" in content:
        print(extract_info(content))
        break
```

**2. 複雜數據處理**
```python
# Code Agent 可以直接使用 Python 的全部能力
import pandas as pd
from collections import Counter

data = get_sales_data()
df = pd.DataFrame(data)
summary = df.groupby('category').agg({
    'revenue': 'sum',
    'units': 'sum'
}).sort_values('revenue', ascending=False)
print(summary.head(10))
```

**3. 錯誤處理和重試**
```python
# Code Agent 可以編寫完整的錯誤處理邏輯
for attempt in range(3):
    try:
        result = api_call(params)
        if validate(result):
            break
    except Exception as e:
        if attempt == 2:
            print(f"失敗: {e}")
        else:
            time.sleep(2 ** attempt)
```

### Tool Calling Agent 的優勢

**1. 更可控**
- 只能調用預定義的工具
- 易於審計和監控

**2. 更安全**
- 不執行任意代碼
- 降低安全風險

**3. 更容易調試**
- 工具調用序列清晰
- 易於重現問題

### 如何選擇？

| 場景 | 推薦 Agent 類型 | 原因 |
|------|----------------|------|
| 複雜數據分析 | Code Agent | 需要靈活的數據處理 |
| 多步驟推理 | Code Agent | 可以編寫完整邏輯 |
| 簡單查詢 | Tool Calling | 更可控、更快 |
| 生產環境 | Tool Calling | 更安全、可預測 |
| 探索性任務 | Code Agent | 更靈活、適應性強 |

## 多模態支持

smolagents 原生支持多種模態：

### 視覺任務
```python
from smolagents import CodeAgent, HfApiModel
from smolagents.tools import ImageQuestionAnsweringTool

agent = CodeAgent(
    tools=[ImageQuestionAnsweringTool()],
    model=HfApiModel()
)

result = agent.run(
    "這張圖片中有什麼？",
    image="https://example.com/image.jpg"
)
```

### 音頻任務
```python
from smolagents.tools import SpeechToTextTool, TextToSpeechTool

agent = CodeAgent(
    tools=[SpeechToTextTool(), TextToSpeechTool()],
    model=HfApiModel()
)

result = agent.run(
    "轉錄這段音頻並生成摘要的語音版本",
    audio="path/to/audio.mp3"
)
```

## 沙盒執行

為了安全執行 Agent 生成的代碼，smolagents 支持多種沙盒環境：

### E2B（推薦）
```python
from smolagents import CodeAgent
from smolagents.e2b import E2BExecutor

agent = CodeAgent(
    tools=tools,
    model=model,
    executor=E2BExecutor()  # 雲端沙盒
)
```

### Docker
```python
from smolagents.docker import DockerExecutor

agent = CodeAgent(
    tools=tools,
    model=model,
    executor=DockerExecutor(image="python:3.11")
)
```

### Local（開發用）
```python
from smolagents import LocalExecutor

agent = CodeAgent(
    tools=tools,
    model=model,
    executor=LocalExecutor()  # 本地執行（謹慎使用）
)
```

## Hub 整合

### 分享工具到 Hub
```python
from smolagents import push_to_hub, tool

@tool
def my_custom_tool(input: str) -> str:
    """我的自定義工具"""
    return input.upper()

# 上傳到 Hub
push_to_hub(
    my_custom_tool,
    repo_id="username/my-custom-tool",
    commit_message="初始版本"
)
```

### 從 Hub 載入工具
```python
from smolagents import load_tool

# 從 Hub 載入工具
custom_tool = load_tool("username/my-custom-tool")

# 直接使用
agent = CodeAgent(tools=[custom_tool], model=model)
```

## 最佳實踐

### 1. 工具設計原則

**單一職責**
```python
# 好的設計
@tool
def get_weather(city: str) -> dict:
    """獲取城市天氣"""
    return weather_api.get(city)

@tool
def format_weather(weather_data: dict) -> str:
    """格式化天氣數據"""
    return f"{weather_data['temp']}°C, {weather_data['condition']}"

# 不好的設計
@tool
def get_and_format_weather(city: str) -> str:
    """獲取並格式化天氣（做太多事）"""
    data = weather_api.get(city)
    return f"{data['temp']}°C, {data['condition']}"
```

**清晰的文檔字符串**
```python
@tool
def search_database(
    query: str,
    filters: dict = None,
    limit: int = 10
) -> list:
    """
    在數據庫中搜索記錄

    Args:
        query: 搜索查詢字符串
        filters: 可選的過濾條件，格式 {"field": "value"}
        limit: 返回的最大結果數，默認 10

    Returns:
        匹配的記錄列表

    Examples:
        >>> search_database("Python", {"category": "programming"}, 5)
        [{"title": "Python Guide", ...}, ...]
    """
    # 實現...
```

### 2. Agent 配置

**合理設置步驟限制**
```python
# 簡單任務
agent = CodeAgent(tools=tools, model=model, max_steps=5)

# 複雜任務
agent = CodeAgent(tools=tools, model=model, max_steps=20)

# 探索性任務
agent = CodeAgent(tools=tools, model=model, max_steps=50)
```

**使用合適的模型**
```python
# 簡單任務：使用較小模型
from smolagents import HfApiModel
model = HfApiModel(model_id="meta-llama/Llama-3.2-3B-Instruct")

# 複雜任務：使用強大模型
from smolagents import OpenAIModel
model = OpenAIModel(model_id="gpt-4-turbo")
```

### 3. 錯誤處理

**優雅的降級**
```python
try:
    result = agent.run(task)
except Exception as e:
    logging.error(f"Agent 執行失敗: {e}")
    # 降級到簡單邏輯
    result = fallback_solution(task)
```

**重試機制**
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def run_agent_with_retry(agent, task):
    return agent.run(task)
```

### 4. 性能優化

**緩存工具結果**
```python
from functools import lru_cache

@tool
@lru_cache(maxsize=100)
def expensive_api_call(query: str) -> dict:
    """緩存 API 調用結果"""
    return api.call(query)
```

**批量處理**
```python
@tool
def batch_process(items: list) -> list:
    """批量處理以減少 API 調用"""
    return [process(item) for item in items]
```

## 資源連結

### 官方資源
- [GitHub Repository](https://github.com/huggingface/smolagents)
- [官方文檔](https://huggingface.co/docs/smolagents)
- [Hugging Face Hub](https://huggingface.co/models?library=smolagents)
- [發布公告](https://huggingface.co/blog/smolagents)

### 社區資源
- [Discord 社群](https://discord.gg/hugging-face)
- [論壇討論](https://discuss.huggingface.co/)
- [示例項目](https://huggingface.co/spaces?search=smolagents)

### 學習資源
- [入門教程](https://huggingface.co/learn/cookbook/agents)
- [視頻演示](https://www.youtube.com/c/HuggingFace)
- [博客文章](https://huggingface.co/blog)

## 進階主題

### 自定義 Executor
```python
from smolagents import Executor

class CustomExecutor(Executor):
    def __call__(self, code: str) -> str:
        # 自定義執行邏輯
        return self.execute_safely(code)
```

### 多 Agent 編排
```python
class AgentOrchestrator:
    def __init__(self):
        self.researcher = CodeAgent(tools=research_tools, model=model)
        self.writer = CodeAgent(tools=writing_tools, model=model)

    def process(self, topic: str):
        research = self.researcher.run(f"研究 {topic}")
        article = self.writer.run(f"基於以下研究寫文章: {research}")
        return article
```

### 自定義工具加載器
```python
from smolagents import Tool

class DatabaseTool(Tool):
    def __init__(self, connection_string: str):
        self.db = connect(connection_string)

    def forward(self, query: str) -> list:
        return self.db.execute(query)
```

## 常見問題

**Q: Code Agent 安全嗎？**
A: 使用沙盒執行器（E2B、Docker）時是安全的。本地執行僅推薦在開發環境中使用。

**Q: 如何選擇模型？**
A: 簡單任務用小模型（Llama-3.2-3B），複雜任務用大模型（GPT-4、Claude）。

**Q: 可以自定義提示詞嗎？**
A: 可以，通過 `system_prompt` 和 `additional_prompting` 參數。

**Q: 如何調試 Agent？**
A: 啟用詳細日誌：`agent.run(task, verbose=True)`

**Q: 支持流式輸出嗎？**
A: 支持，參見 `11_流式輸出.py` 範例。

## 貢獻

歡迎提交問題和改進建議！本範例集持續更新中。

## 授權

本範例集採用 MIT 授權。smolagents 框架本身採用 Apache 2.0 授權。

---

**開始探索 smolagents 的強大功能吧！從 `01_快速入門.py` 開始您的旅程。**

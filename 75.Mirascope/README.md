# Mirascope 框架完整範例

## 框架簡介

Mirascope 是一個輕量級的 LLM 工具庫，提供簡潔優雅的 API 來與各種大語言模型進行交互。它專注於提供類型安全、易於使用的接口，支持多個 LLM 提供商，包括 OpenAI、Anthropic、Google 等。

### 核心特點

#### 1. 簡潔的 API 設計 ✨
- Pythonic 的函數式接口
- 裝飾器驅動的開發方式
- 最小化的樣板代碼
- 直觀易懂的使用方式

```python
from mirascope.openai import OpenAICall

class RecipeRecommender(OpenAICall):
    prompt_template = "推薦一道{cuisine}菜系的{meal_type}食譜"

    cuisine: str
    meal_type: str

response = RecipeRecommender(cuisine="中式", meal_type="晚餐").call()
print(response.content)
```

#### 2. 提示模板系統 📝
- Jinja2 模板支持
- 變量插值
- 條件邏輯
- 循環結構
- 模板繼承

```python
class Summarizer(OpenAICall):
    prompt_template = """
    請總結以下文本：

    {{ text }}

    {% if max_length %}
    限制在 {{ max_length }} 字以內。
    {% endif %}
    """

    text: str
    max_length: int = None
```

#### 3. 結構化輸出 🎯
- Pydantic 模型整合
- 自動 JSON Schema 生成
- 類型驗證
- 格式化輸出

```python
from pydantic import BaseModel

class Person(BaseModel):
    name: str
    age: int
    occupation: str

class ExtractPerson(OpenAICall):
    prompt_template = "從以下文本提取人物信息：{text}"
    text: str
    call_params = {"response_model": Person}

person = ExtractPerson(text="張三今年30歲，是工程師").call()
```

#### 4. 工具調用 🔧
- 函數調用支持
- 自動工具註冊
- 參數驗證
- 結果處理

```python
def get_weather(city: str) -> str:
    """獲取指定城市的天氣"""
    return f"{city} 的天氣是晴天"

class WeatherAssistant(OpenAICall):
    prompt_template = "用戶問題：{question}"
    question: str
    call_params = {"tools": [get_weather]}
```

#### 5. 多模型支持 🌐
- OpenAI (GPT-3.5, GPT-4)
- Anthropic (Claude)
- Google (PaLM, Gemini)
- 統一的接口
- 輕鬆切換提供商

```python
from mirascope.anthropic import AnthropicCall
from mirascope.openai import OpenAICall

# 使用 OpenAI
class OpenAIChat(OpenAICall):
    prompt_template = "你好"

# 使用 Anthropic
class ClaudeChat(AnthropicCall):
    prompt_template = "你好"
```

#### 6. 流式輸出 ⚡
- 實時響應流
- Token 級別流式傳輸
- 減少等待時間
- 更好的用戶體驗

```python
stream = RecipeRecommender(
    cuisine="意大利",
    meal_type="午餐"
).stream()

for chunk in stream:
    print(chunk.content, end="", flush=True)
```

#### 7. 重試機制 🔄
- 自動重試失敗的請求
- 可配置的重試策略
- 指數退避
- 錯誤處理

```python
from tenacity import retry, stop_after_attempt

class RobustCall(OpenAICall):
    prompt_template = "處理：{data}"
    data: str

    @retry(stop=stop_after_attempt(3))
    def call(self):
        return super().call()
```

#### 8. 驗證器 ✅
- 輸入驗證
- 輸出驗證
- 自定義驗證邏輯
- 錯誤提示

```python
from pydantic import validator

class ValidatedCall(OpenAICall):
    prompt_template = "分析：{text}"
    text: str

    @validator('text')
    def text_not_empty(cls, v):
        if not v.strip():
            raise ValueError("文本不能為空")
        return v
```

## 安裝指南

### 基礎安裝
```bash
pip install mirascope
```

### 安裝特定提供商
```bash
# OpenAI
pip install mirascope[openai]

# Anthropic
pip install mirascope[anthropic]

# Google
pip install mirascope[google]

# 全部安裝
pip install mirascope[all]
```

### 開發環境設置
```bash
# 創建虛擬環境
python -m venv venv
source venv/bin/activate  # Linux/Mac

# 安裝依賴
pip install -r requirements.txt

# 設置 API 密鑰
export OPENAI_API_KEY='your-openai-key'
export ANTHROPIC_API_KEY='your-anthropic-key'
```

## 快速開始

### 第一個 Mirascope 應用

```python
from mirascope.openai import OpenAICall

class SimpleChat(OpenAICall):
    prompt_template = "你好，我是用戶。請向我問好。"

response = SimpleChat().call()
print(response.content)
```

### 帶參數的調用

```python
class Translator(OpenAICall):
    prompt_template = "將以下文本翻譯成{target_language}：{text}"

    text: str
    target_language: str

response = Translator(
    text="Hello, world!",
    target_language="中文"
).call()
print(response.content)
```

### 結構化輸出

```python
from pydantic import BaseModel

class Article(BaseModel):
    title: str
    summary: str
    tags: list[str]

class ArticleAnalyzer(OpenAICall):
    prompt_template = "分析這篇文章：{content}"
    content: str
    call_params = {"response_model": Article}

article = ArticleAnalyzer(content="文章內容...").call()
print(f"標題：{article.title}")
```

## 與其他框架對比

### Mirascope vs LangChain

| 特性 | Mirascope | LangChain |
|------|-----------|-----------|
| **設計理念** | 簡潔、類型安全 | 功能豐富、模塊化 |
| **學習曲線** | 低 | 中高 |
| **代碼量** | 少 | 多 |
| **類型提示** | 完善 | 部分 |
| **多模型** | ✅ 原生支持 | ✅ 支持 |
| **適用場景** | 簡單到中等複雜度 | 複雜應用 |

**LangChain 優勢：**
- 更豐富的生態系統
- 更多的預構建組件
- RAG 和 Agent 系統
- 大型社區

**Mirascope 優勢：**
- 更簡潔的 API
- 更好的類型安全
- 更少的樣板代碼
- 更容易調試

### Mirascope vs Marvin

| 特性 | Mirascope | Marvin |
|------|-----------|--------|
| **核心功能** | LLM 調用 | AI 函數 |
| **提示管理** | ✅ 模板系統 | ⚠️ 文檔字符串 |
| **多模型** | ✅ 原生 | ⚠️ 主要 OpenAI |
| **結構化輸出** | ✅ 優秀 | ✅ 優秀 |
| **學習曲線** | 低 | 非常低 |

**Marvin 優勢：**
- 更自然的函數式風格
- 自動提示詞生成
- 多模態支持內建

**Mirascope 優勢：**
- 更靈活的提示管理
- 多模型原生支持
- 更好的工具整合

### 選擇建議

**選擇 Mirascope：**
- 需要類型安全的代碼
- 多 LLM 提供商支持
- 簡潔的 API 設計
- 靈活的提示模板
- 中小型項目
- 快速原型開發

**選擇 LangChain：**
- 複雜的 AI 應用
- 需要豐富的組件
- RAG 系統
- Agent 編排
- 企業級項目

**選擇 Marvin：**
- 極簡的代碼風格
- 函數式編程偏好
- 快速實驗
- 與 Prefect 整合

## 範例文件導覽

### 基礎篇

#### 01_快速開始.py
- Mirascope 基本概念
- 環境配置
- 第一個調用
- 基本使用模式

#### 02_提示模板.py
- Jinja2 模板語法
- 變量插值
- 條件和循環
- 模板繼承
- 最佳實踐

#### 03_結構化輸出.py
- Pydantic 模型
- 響應格式化
- 類型驗證
- 嵌套結構
- 列表輸出

#### 04_工具調用.py
- 函數工具
- 工具註冊
- 參數傳遞
- 結果處理
- 多工具組合

### 進階篇

#### 05_多模型.py
- OpenAI 使用
- Anthropic/Claude
- Google PaLM
- 模型切換
- 統一接口

#### 06_流式輸出.py
- 流式調用
- Token 處理
- 實時展示
- 錯誤處理
- 應用場景

#### 07_重試機制.py
- 自動重試
- 重試策略
- 指數退避
- 錯誤處理
- 降級方案

#### 08_驗證器.py
- 輸入驗證
- 輸出驗證
- 自定義驗證
- 錯誤消息
- 驗證鏈

### 高級篇

#### 09_Agent構建.py
- Agent 架構
- 工具集成
- 決策邏輯
- 多輪對話
- 狀態管理

#### 10_最佳實踐.py
- 代碼組織
- 錯誤處理
- 性能優化
- 測試策略
- 生產部署

## 核心概念

### Call 類

Mirascope 的核心是 `Call` 類，它封裝了 LLM 調用的所有細節：

```python
class MyCall(OpenAICall):
    prompt_template = "提示模板"

    # 參數定義
    param1: str
    param2: int = 10

    # 調用參數
    call_params = {
        "model": "gpt-4",
        "temperature": 0.7
    }
```

### 提示模板

使用 Jinja2 模板語法：

```python
prompt_template = """
系統消息：你是一個助手

用戶消息：{{ user_message }}

{% if context %}
上下文：{{ context }}
{% endif %}
"""
```

### 響應處理

```python
response = MyCall().call()

# 訪問內容
print(response.content)

# 訪問原始響應
print(response.response)

# 訪問使用統計
print(response.usage)
```

## 最佳實踐

### 1. 使用類型提示

```python
from typing import List

class TypedCall(OpenAICall):
    prompt_template = "分析：{data}"

    data: str
    options: List[str] = []

    def process(self) -> dict:
        response = self.call()
        return {"result": response.content}
```

### 2. 錯誤處理

```python
try:
    response = MyCall().call()
except Exception as e:
    logger.error(f"調用失敗：{e}")
    # 實施降級策略
    response = fallback_function()
```

### 3. 環境管理

```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    model: str = "gpt-3.5-turbo"

    class Config:
        env_file = ".env"

settings = Settings()
```

### 4. 提示版本控制

```python
# prompts/v1.py
SUMMARIZE_V1 = "總結：{text}"

# prompts/v2.py
SUMMARIZE_V2 = """
總結以下內容，重點關注：
- 主要觀點
- 關鍵數據
{text}
"""
```

### 5. 測試

```python
def test_my_call():
    call = MyCall(param1="test")
    response = call.call()

    assert response.content is not None
    assert len(response.content) > 0
```

## 常見問題

### Q: 如何選擇合適的模型？

**A:** 根據任務複雜度選擇：

- 簡單任務：gpt-3.5-turbo
- 複雜推理：gpt-4
- 長文本：gpt-4-32k
- 成本優先：gpt-3.5-turbo

### Q: 如何處理 API 限流？

**A:** 使用重試機制和速率限制：

```python
from tenacity import retry, wait_exponential

class RateLimitedCall(OpenAICall):
    @retry(wait=wait_exponential(multiplier=1, min=4, max=10))
    def call(self):
        return super().call()
```

### Q: 如何優化提示詞？

**A:** 遵循這些原則：

1. 明確具體的指令
2. 提供示例
3. 設定輸出格式
4. 使用分隔符
5. 迭代測試

### Q: 支持本地模型嗎？

**A:** 支持，通過自定義提供商：

```python
class LocalLLMCall(BaseCall):
    api_base = "http://localhost:8000"
```

## 進階主題

### 自定義提供商

```python
from mirascope.base import BaseCall

class CustomLLMCall(BaseCall):
    api_base = "https://custom-llm.com/v1"

    def _create_completion(self):
        # 自定義實現
        pass
```

### 中間件

```python
def logging_middleware(call_func):
    def wrapper(*args, **kwargs):
        logger.info(f"調用開始：{call_func.__name__}")
        result = call_func(*args, **kwargs)
        logger.info(f"調用結束：{call_func.__name__}")
        return result
    return wrapper

class LoggedCall(OpenAICall):
    @logging_middleware
    def call(self):
        return super().call()
```

### 批量處理

```python
import asyncio

async def batch_process(items):
    calls = [MyCall(data=item) for item in items]
    tasks = [call.call_async() for call in calls]
    return await asyncio.gather(*tasks)
```

## 參考資源

### 官方文檔
- [Mirascope 官方文檔](https://docs.mirascope.io/)
- [GitHub 倉庫](https://github.com/Mirascope/mirascope)
- [API 參考](https://docs.mirascope.io/api-reference/)

### 社區資源
- [Discord 社區](https://discord.gg/mirascope)
- [示例項目](https://github.com/Mirascope/mirascope-examples)
- [視頻教程](https://www.youtube.com/c/mirascope)

### 相關工具
- [OpenAI](https://openai.com/) - LLM 提供商
- [Anthropic](https://anthropic.com/) - Claude API
- [Pydantic](https://pydantic.dev/) - 數據驗證

## 生態系統

### 整合案例
- 聊天機器人
- 內容生成
- 數據提取
- 文本分析
- 代碼生成

### 企業應用
- 客戶服務
- 文檔處理
- 決策支持
- 自動化工作流
- 知識管理

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

- **2025-01**: 創建初始範例集
- 包含 10 個完整範例
- 涵蓋所有核心功能
- 繁體中文註釋

---

**開始探索** → 從 `01_快速開始.py` 開始你的 Mirascope 之旅！

# Marvin 框架完整範例

## 框架簡介

Marvin 是由 Prefect 團隊開發的一個輕量級 AI 函數庫，讓開發者能夠像調用普通函數一樣使用 AI 功能。它提供了一種優雅的方式將 AI 能力集成到 Python 應用中，無需編寫複雜的提示詞或處理 API 調用細節。

### 核心特點

#### 1. AI 函數裝飾器 🎯
- 使用 `@ai_fn` 裝飾器創建 AI 函數
- 自動處理提示詞和 API 調用
- 類型安全的輸入輸出
- 支持文檔字符串作為指令

```python
import marvin

@marvin.fn
def sentiment_analysis(text: str) -> str:
    """分析文本的情感傾向，返回 positive、negative 或 neutral"""

# 使用時就像普通函數
result = sentiment_analysis("這個產品太棒了！")  # 返回 "positive"
```

#### 2. 結構化數據提取 📊
- 從非結構化文本中提取結構化數據
- 使用 Pydantic 模型定義數據結構
- 自動驗證和類型轉換
- 支持複雜的嵌套結構

```python
from pydantic import BaseModel
import marvin

class Person(BaseModel):
    name: str
    age: int
    occupation: str

result = marvin.extract(
    "張三今年30歲，是一名軟件工程師",
    target=Person
)
# 返回: Person(name="張三", age=30, occupation="軟件工程師")
```

#### 3. 分類任務 🏷️
- 簡單的文本分類
- 支持枚舉和字面量類型
- 多標籤分類
- 自定義分類標籤

```python
from enum import Enum

class Sentiment(Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

result = marvin.classify("這個產品太棒了！", labels=Sentiment)
# 返回: Sentiment.POSITIVE
```

#### 4. 數據轉換 🔄
- 自動化數據格式轉換
- 支持跨語言轉換
- 智能數據清理
- 格式標準化

```python
# 自動轉換數據格式
data = marvin.cast("100美元", target=float)  # 返回: 100.0
```

#### 5. 圖像處理 🖼️
- 圖像描述生成
- 視覺問答
- 圖像分類
- OCR 文字識別

```python
# 圖像描述
description = marvin.caption("image.jpg")

# 視覺問答
answer = marvin.vision.ask("這張圖片裡有什麼？", image="photo.jpg")
```

#### 6. 語音功能 🎤
- 文字轉語音（TTS）
- 語音轉文字（STT）
- 多語言支持
- 自定義語音參數

```python
# 文字轉語音
marvin.speak("你好，世界！", output="hello.mp3")

# 語音轉文字
text = marvin.transcribe("audio.mp3")
```

#### 7. 異步支持 ⚡
- 原生異步 API
- 並發處理
- 流式響應
- 高性能應用

```python
import asyncio

@marvin.fn
async def async_analysis(text: str) -> str:
    """異步分析文本"""

result = await async_analysis("測試文本")
```

#### 8. 可組合性 🔗
- 函數組合
- 鏈式調用
- 工作流構建
- 與 Prefect 整合

## 安裝指南

### 基礎安裝
```bash
pip install marvin
```

### 完整安裝（包含所有功能）
```bash
pip install marvin[all]
```

### 指定功能安裝
```bash
# 圖像處理
pip install marvin[images]

# 語音功能
pip install marvin[audio]

# 視頻處理
pip install marvin[video]
```

### 開發環境設置
```bash
# 創建虛擬環境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安裝依賴
pip install -r requirements.txt

# 設置 API 密鑰
export OPENAI_API_KEY='your-key-here'
```

## 快速開始

### 第一個 AI 函數

```python
import marvin

# 定義 AI 函數
@marvin.fn
def generate_slogan(product: str) -> str:
    """為產品生成一個吸引人的廣告標語"""

# 使用
slogan = generate_slogan("智能手錶")
print(slogan)  # "時間在你掌握，智能隨行"
```

### 結構化數據提取

```python
from pydantic import BaseModel
import marvin

class Contact(BaseModel):
    name: str
    email: str
    phone: str

text = "請聯繫張三，他的郵箱是 zhangsan@example.com，電話是 138-1234-5678"
contact = marvin.extract(text, target=Contact)
print(contact)
# Contact(name="張三", email="zhangsan@example.com", phone="138-1234-5678")
```

### 文本分類

```python
import marvin

# 簡單分類
category = marvin.classify(
    "Python 是一門優秀的編程語言",
    labels=["技術", "娛樂", "體育", "政治"]
)
print(category)  # "技術"
```

## 與其他框架對比

### Marvin vs LangChain

| 特性 | Marvin | LangChain |
|------|--------|-----------|
| **設計理念** | 簡單、函數式 | 複雜、鏈式 |
| **學習曲線** | 低 | 中高 |
| **代碼風格** | Pythonic | 特定模式 |
| **類型安全** | 強類型（Pydantic） | 弱類型 |
| **適用場景** | 簡單 AI 任務 | 複雜工作流 |
| **性能** | 高（輕量級） | 中（框架開銷） |

**LangChain 優勢：**
- 豐富的組件生態
- 複雜的工作流編排
- 更多的工具整合
- 強大的 Agent 系統

**Marvin 優勢：**
- 更簡單的 API
- 更好的類型安全
- 更少的樣板代碼
- 與 Prefect 深度整合

### Marvin vs Instructor

| 特性 | Marvin | Instructor |
|------|--------|------------|
| **核心功能** | AI 函數庫 | 結構化輸出 |
| **數據提取** | ✅ 優秀 | ✅ 優秀 |
| **函數式 API** | ✅ 原生支持 | ⚠️ 有限支持 |
| **圖像/語音** | ✅ 內建支持 | ❌ 不支持 |
| **Pydantic 整合** | ✅ 深度整合 | ✅ 核心特性 |
| **異步支持** | ✅ 原生異步 | ✅ 支持 |

**Instructor 優勢：**
- 專注於結構化輸出
- 更靈活的驗證
- 更好的錯誤處理
- 支持多個 LLM 提供商

**Marvin 優勢：**
- 更完整的功能集
- 函數式編程風格
- 多模態支持
- Prefect 工作流整合

### 選擇建議

**選擇 Marvin：**
- 需要簡單的 AI 函數
- 重視類型安全
- 需要多模態支持（圖像、語音）
- 使用 Prefect 工作流
- 快速原型開發
- Python 原生風格代碼

**選擇 LangChain：**
- 複雜的 AI 工作流
- 需要 Agent 系統
- RAG 應用
- 豐富的工具整合
- 企業級應用

**選擇 Instructor：**
- 專注於數據提取
- 需要複雜的驗證邏輯
- 多 LLM 提供商支持
- API 數據解析

## 範例文件導覽

### 基礎篇

#### 01_快速開始.py
- Marvin 基本概念
- 環境配置
- 第一個 AI 函數
- 基本使用模式

#### 02_AI函數.py
- `@marvin.fn` 裝飾器
- 函數參數和返回值
- 類型注解
- 文檔字符串作為提示
- 錯誤處理

#### 03_分類任務.py
- `marvin.classify()` 使用
- 枚舉分類
- 多標籤分類
- 自定義標籤
- 置信度評分

#### 04_實體提取.py
- `marvin.extract()` 功能
- Pydantic 模型定義
- 從文本提取實體
- 列表提取
- 嵌套結構提取

### 進階篇

#### 05_數據轉換.py
- `marvin.cast()` 轉換
- 格式轉換
- 數據清理
- 單位轉換
- 跨語言轉換

#### 06_圖像處理.py
- 圖像描述生成
- 視覺問答
- 圖像分類
- OCR 識別
- 多圖像處理

#### 07_語音功能.py
- 文字轉語音（TTS）
- 語音轉文字（STT）
- 語音參數配置
- 多語言支持
- 音頻處理

#### 08_自定義模型.py
- 自定義 LLM 配置
- 模型選擇
- 參數調整
- 提示詞工程
- 溫度和 top_p 設置

### 高級篇

#### 09_異步處理.py
- 異步 AI 函數
- 並發處理
- 流式響應
- 批量處理
- 性能優化

#### 10_生產應用.py
- 錯誤處理和重試
- 日誌記錄
- 性能監控
- 緩存策略
- 部署最佳實踐

## 核心概念

### AI 函數

AI 函數是 Marvin 的核心概念，允許你像使用普通函數一樣使用 AI：

```python
@marvin.fn
def translate(text: str, target_language: str) -> str:
    """將文本翻譯成目標語言"""

result = translate("Hello", "中文")  # "你好"
```

### 類型安全

Marvin 使用 Python 的類型注解和 Pydantic 模型確保類型安全：

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int
    email: str

# 自動驗證和轉換
user = marvin.extract("張三，30歲，zhangsan@example.com", target=User)
```

### 提示詞工程

Marvin 自動處理提示詞，但你可以通過文檔字符串自定義：

```python
@marvin.fn
def summarize(text: str) -> str:
    """
    總結文本的主要內容。
    要求：
    - 不超過 100 字
    - 保留關鍵信息
    - 使用簡潔的語言
    """
```

### 模型配置

可以為每個函數配置不同的模型：

```python
@marvin.fn(model="gpt-4")
def complex_task(input: str) -> str:
    """需要 GPT-4 處理的複雜任務"""

@marvin.fn(model="gpt-3.5-turbo")
def simple_task(input: str) -> str:
    """簡單任務使用更快的模型"""
```

## 最佳實踐

### 1. 清晰的函數定義

```python
# 好的做法：清晰的類型和文檔
@marvin.fn
def extract_keywords(text: str, max_keywords: int = 5) -> list[str]:
    """
    從文本中提取關鍵詞。

    Args:
        text: 輸入文本
        max_keywords: 最多返回的關鍵詞數量

    Returns:
        關鍵詞列表
    """

# 避免：模糊的定義
@marvin.fn
def process(data):
    """處理數據"""
```

### 2. 使用 Pydantic 模型

```python
from pydantic import BaseModel, Field

class Article(BaseModel):
    title: str = Field(description="文章標題")
    author: str = Field(description="作者姓名")
    published_date: str = Field(description="發布日期 YYYY-MM-DD")
    tags: list[str] = Field(description="文章標籤")

# 結構化提取
article = marvin.extract(text, target=Article)
```

### 3. 錯誤處理

```python
import marvin
from marvin.exceptions import MarvinError

try:
    result = marvin.classify(text, labels=["A", "B", "C"])
except MarvinError as e:
    print(f"Marvin 錯誤: {e}")
    result = "Unknown"
except Exception as e:
    print(f"其他錯誤: {e}")
    result = "Error"
```

### 4. 性能優化

```python
import asyncio
import marvin

# 並發處理多個任務
async def process_batch(texts: list[str]):
    tasks = [marvin.fn_async(analyze)(text) for text in texts]
    results = await asyncio.gather(*tasks)
    return results

# 使用緩存
@marvin.fn(cache=True)
def expensive_operation(input: str) -> str:
    """會被緩存的昂貴操作"""
```

### 5. 測試

```python
import pytest
import marvin

def test_sentiment_analysis():
    result = marvin.classify(
        "這個產品太棒了！",
        labels=["positive", "negative", "neutral"]
    )
    assert result == "positive"

@pytest.mark.asyncio
async def test_async_function():
    @marvin.fn
    async def async_task(x: str) -> str:
        """異步任務"""

    result = await async_task("test")
    assert isinstance(result, str)
```

## 常見問題

### Q: Marvin 支持哪些 LLM 提供商？

**A:** Marvin 主要支持 OpenAI，但也可以通過配置使用其他兼容 OpenAI API 的提供商：

```python
import marvin

marvin.settings.openai.api_key = "your-key"
marvin.settings.openai.api_base = "https://api.custom-provider.com/v1"
```

### Q: 如何控制 API 調用成本？

**A:** 幾個策略：

1. 使用更便宜的模型
2. 啟用緩存
3. 批量處理
4. 設置速率限制

```python
# 使用更便宜的模型
@marvin.fn(model="gpt-3.5-turbo")
def cheap_task(input: str) -> str:
    """使用便宜的模型"""

# 啟用緩存
@marvin.fn(cache=True)
def cached_task(input: str) -> str:
    """結果會被緩存"""
```

### Q: Marvin 可以離線使用嗎？

**A:** 不可以。Marvin 依賴 LLM API，需要網絡連接。但你可以：

1. 使用本地 LLM 提供商（如 Ollama）
2. 緩存常見查詢結果
3. 實現回退機制

### Q: 如何調試 AI 函數？

**A:** 啟用詳細日誌：

```python
import marvin
import logging

# 啟用調試日誌
marvin.settings.log_level = "DEBUG"
logging.basicConfig(level=logging.DEBUG)

# 查看生成的提示詞
@marvin.fn(verbose=True)
def debug_function(input: str) -> str:
    """會顯示提示詞的函數"""
```

### Q: 支持流式響應嗎？

**A:** 支持：

```python
@marvin.fn(stream=True)
def streaming_function(input: str) -> str:
    """支持流式輸出的函數"""

for chunk in streaming_function("長文本生成"):
    print(chunk, end="", flush=True)
```

## 進階主題

### 與 Prefect 整合

```python
from prefect import flow, task
import marvin

@task
def extract_data(text: str):
    return marvin.extract(text, target=DataModel)

@task
def classify_data(data):
    return marvin.classify(data.content, labels=Categories)

@flow
def data_pipeline(texts: list[str]):
    extracted = [extract_data(text) for text in texts]
    classified = [classify_data(data) for data in extracted]
    return classified
```

### 自定義工具

```python
from marvin import Tool

class CustomTool(Tool):
    name = "custom_search"
    description = "自定義搜索工具"

    def run(self, query: str) -> str:
        # 實現自定義邏輯
        return f"搜索結果: {query}"
```

### 多模態應用

```python
import marvin

# 組合圖像和文本
image_description = marvin.caption("product.jpg")
category = marvin.classify(
    image_description,
    labels=["電子產品", "服裝", "食品"]
)

# 視覺問答
answer = marvin.vision.ask(
    "這個產品的顏色是什麼？",
    image="product.jpg"
)
```

### 工作流編排

```python
from marvin import Pipeline

# 創建處理流水線
pipeline = Pipeline([
    ("extract", marvin.extract),
    ("classify", marvin.classify),
    ("summarize", marvin.fn(summarize))
])

# 執行流水線
result = pipeline.run(input_data)
```

## 參考資源

### 官方文檔
- [Marvin 官方文檔](https://www.askmarvin.ai/)
- [GitHub 倉庫](https://github.com/PrefectHQ/marvin)
- [API 參考](https://www.askmarvin.ai/api-reference/)

### 社區資源
- [Discord 社區](https://discord.gg/prefect)
- [示例項目](https://github.com/PrefectHQ/marvin/tree/main/examples)
- [Prefect 博客](https://www.prefect.io/blog)

### 相關工具
- [Prefect](https://www.prefect.io/) - 工作流編排
- [Pydantic](https://pydantic.dev/) - 數據驗證
- [OpenAI](https://openai.com/) - LLM 提供商

## 生態系統

### 整合案例
- 數據提取和清理
- 內容分類和標記
- 自動化客戶支持
- 文檔處理
- 多模態應用

### 企業應用
- 智能數據處理
- 自動化工作流
- 客戶服務增強
- 內容生成
- 決策支持系統

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

**開始探索** → 從 `01_快速開始.py` 開始你的 Marvin 之旅！

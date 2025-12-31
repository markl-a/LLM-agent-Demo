# Guidance - LLM 輸出控制庫

## 框架簡介

Guidance 是微軟研究院開發的一個強大的 LLM 輸出控制庫，專注於通過受控解碼(Constrained Decoding)技術來精確控制大型語言模型的輸出。與傳統的提示工程不同，Guidance 在 token 級別實施約束，能夠將結構化任務的錯誤率降低 90%。

### 核心價值

- **Token 級控制**: 在生成過程中逐個 token 強制執行約束
- **零錯誤率**: 保證輸出完全符合指定的格式和規則
- **高效性能**: 相比多次重試，大幅降低延遲和成本
- **靈活語法**: 支持 CFG、正則表達式、JSON Schema 等多種約束方式

## 主要特性

### 1. 受控解碼 (Constrained Decoding)

Guidance 的核心創新是在 LLM 生成過程中實時約束輸出空間：

- **Token 屏蔽**: 在每個生成步驟中，只允許符合約束的 token
- **零重試**: 不需要生成後驗證和重試
- **確定性保證**: 100% 保證輸出符合規範

### 2. CFG 語法支援

支持上下文無關文法(Context-Free Grammar)定義複雜的結構約束：

```python
# 定義 JSON 對象的語法規則
grammar = {
    "object": '{ "name": string, "age": integer }',
    "string": r'"[^"]*"',
    "integer": r'[0-9]+'
}
```

### 3. JSON Schema 整合

原生支持 JSON Schema，自動生成符合 schema 的 JSON：

- 支持所有 JSON Schema 特性（type, enum, pattern, etc.）
- 嵌套對象和數組的完整支持
- 自定義驗證規則

### 4. 多模型後端

支持多種 LLM 後端：

- **OpenAI API**: GPT-4, GPT-3.5 等
- **Transformers**: 本地運行開源模型
- **vLLM**: 高性能批量推理
- **llama.cpp**: 輕量級部署

### 5. 模板語言

提供直觀的模板語法來組合提示和約束：

```python
from guidance import models, gen, select

# 加載模型
lm = models.OpenAI("gpt-4")

# 使用模板
lm += f"The answer is: {select(['yes', 'no'])}"
```

## 安裝指南

### 基礎安裝

```bash
pip install guidance>=0.2.0
```

### 完整安裝（包含所有後端支持）

```bash
pip install -r requirements.txt
```

### 從源碼安裝

```bash
git clone https://github.com/guidance-ai/guidance.git
cd guidance
pip install -e .
```

## 快速開始

### 基本範例

```python
from guidance import models, gen

# 初始化模型
lm = models.OpenAI("gpt-4")

# 生成文本
lm += "The top 3 programming languages are:\n"
lm += "1. " + gen("lang1", max_tokens=10) + "\n"
lm += "2. " + gen("lang2", max_tokens=10) + "\n"
lm += "3. " + gen("lang3", max_tokens=10) + "\n"

print(lm)
```

### 結構化輸出範例

```python
from guidance import models, gen, select

lm = models.OpenAI("gpt-4")

# 強制從選項中選擇
lm += f"Is Python a compiled language? {select(['yes', 'no'], name='answer')}"

print(f"Answer: {lm['answer']}")
```

### JSON 生成範例

```python
from guidance import models
import json

lm = models.OpenAI("gpt-4")

# 定義 JSON schema
schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"},
        "email": {"type": "string", "pattern": r"^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$"}
    },
    "required": ["name", "age", "email"]
}

# 生成符合 schema 的 JSON
lm += "Generate a user profile:\n"
lm += gen(name="user", json_schema=schema)

user_data = json.loads(lm["user"])
print(json.dumps(user_data, indent=2))
```

## 核心概念

### 1. 模型對象 (Model Object)

Guidance 使用可變的模型對象來累積生成的文本：

```python
lm = models.OpenAI("gpt-4")  # 創建模型實例
lm += "Hello"                 # 添加靜態文本
lm += gen(max_tokens=10)      # 添加生成操作
```

### 2. 生成函數 (Generation Functions)

- `gen()`: 自由文本生成
- `select()`: 從選項中選擇
- `regex()`: 匹配正則表達式
- `json()`: 生成 JSON 對象

### 3. 約束類型

- **選擇約束**: 從預定義選項中選擇
- **正則約束**: 匹配正則表達式模式
- **語法約束**: 符合 CFG 語法規則
- **Schema 約束**: 符合 JSON/XML Schema

## 使用場景

### 1. 數據提取

從非結構化文本中提取結構化數據：

```python
# 從文本中提取實體
lm += "Extract entities from: 'John lives in New York'\n"
lm += f"Person: {gen('person', stop=',')}\n"
lm += f"Location: {gen('location', stop='.')}\n"
```

### 2. 表單填寫

自動填寫具有格式要求的表單：

```python
# 生成符合格式的表單數據
lm += f"Name: {gen('name', regex=r'[A-Z][a-z]+ [A-Z][a-z]+')}\n"
lm += f"Phone: {gen('phone', regex=r'\d{3}-\d{3}-\d{4}')}\n"
lm += f"Email: {gen('email', regex=r'[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+')}\n"
```

### 3. API 調用

生成符合 API 規範的請求：

```python
# 生成 API 請求 payload
api_schema = {
    "type": "object",
    "properties": {
        "method": {"enum": ["GET", "POST", "PUT", "DELETE"]},
        "endpoint": {"type": "string"},
        "params": {"type": "object"}
    }
}

lm += gen(name="api_request", json_schema=api_schema)
```

### 4. 代碼生成

生成語法正確的代碼：

```python
# 生成符合語法的 Python 函數
lm += "def calculate("
lm += gen("params", regex=r"[a-z_]+(?:, [a-z_]+)*")
lm += "):\n"
lm += "    " + gen("body", stop="return")
lm += "return " + gen("return_value", stop="\n")
```

### 5. 對話系統

構建結構化的對話流程：

```python
# 多輪對話控制
lm += "User: What's the weather?\n"
lm += f"Assistant: {gen('response', max_tokens=50)}\n"
lm += f"Sentiment: {select(['positive', 'neutral', 'negative'])}\n"
```

### 6. 分類任務

強制模型從預定義類別中選擇：

```python
# 文本分類
text = "This product is amazing!"
lm += f"Text: {text}\n"
lm += f"Category: {select(['positive', 'negative', 'neutral'])}\n"
lm += f"Confidence: {select(['high', 'medium', 'low'])}\n"
```

### 7. 數據驗證

生成符合驗證規則的數據：

```python
# 生成符合驗證規則的用戶輸入
lm += f"Username: {gen('username', regex=r'[a-z0-9_]{{3,16}}')}\n"
lm += f"Password: {gen('password', regex=r'(?=.*[A-Z])(?=.*[0-9]).{{8,}}')}\n"
```

## 高級特性

### 1. 嵌套結構

支持複雜的嵌套約束：

```python
# 嵌套 JSON 對象
schema = {
    "type": "object",
    "properties": {
        "user": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "contacts": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            }
        }
    }
}
```

### 2. 條件生成

基於上下文的條件約束：

```python
# 根據條件調整約束
if condition:
    lm += select(['option1', 'option2'])
else:
    lm += select(['option3', 'option4'])
```

### 3. 批量處理

高效處理多個輸入：

```python
# 批量生成
inputs = ["text1", "text2", "text3"]
results = []

for text in inputs:
    lm = models.OpenAI("gpt-4")
    lm += f"Analyze: {text}\n"
    lm += f"Sentiment: {select(['pos', 'neg'])}"
    results.append(lm["sentiment"])
```

### 4. 自定義語法

定義特定領域的語法規則：

```python
# SQL 查詢語法
sql_grammar = """
SELECT {columns} FROM {table} WHERE {condition}
"""
```

## 性能優化

### 1. 緩存機制

Guidance 自動緩存中間結果，避免重複計算。

### 2. 批量推理

使用 vLLM 後端進行高效批量處理。

### 3. Token 預算

控制生成長度以優化成本：

```python
lm += gen(max_tokens=100)  # 限制最大 token 數
```

## 最佳實踐

1. **明確約束**: 盡可能具體地定義約束規則
2. **測試驗證**: 用多個測試案例驗證約束效果
3. **錯誤處理**: 為異常情況準備後備方案
4. **性能監控**: 跟蹤延遲和 token 使用量
5. **版本管理**: 記錄模型和 Guidance 版本

## 與其他框架比較

| 特性 | Guidance | LangChain | Outlines |
|------|----------|-----------|----------|
| Token 級控制 | ✅ | ❌ | ✅ |
| CFG 支持 | ✅ | ❌ | ✅ |
| 模板語法 | ✅ | ✅ | ❌ |
| 多模型後端 | ✅ | ✅ | ✅ |
| 零錯誤保證 | ✅ | ❌ | ✅ |

## 參考資源

- **官方網站**: https://github.com/guidance-ai/guidance
- **文檔**: https://guidance.readthedocs.io/
- **論文**: "Guidance: A Framework for Controlling Large Language Models"
- **社區**: https://discord.gg/guidance

## 目錄結構

```
55.Guidance/
├── README.md                 # 本文件
├── requirements.txt          # 依賴列表
├── 01_快速開始.py           # 基礎使用
├── 02_模板語法.py           # 模板系統
├── 03_選擇控制.py           # 選擇約束
├── 04_正則約束.py           # 正則表達式
├── 05_JSON生成.py           # JSON Schema
├── 06_語法控制.py           # CFG 語法
├── 07_多模型支援.py         # 多後端支持
├── 08_批量推理.py           # 批量處理
├── 09_嵌套結構.py           # 複雜結構
└── 10_生產部署.py           # 部署實踐
```

## 授權

本示例代碼採用 MIT 授權。Guidance 框架本身遵循其原始授權條款。

## 貢獻

歡迎提交問題和改進建議！

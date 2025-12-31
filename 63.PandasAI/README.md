# PandasAI - 數據科學 AI Agent 框架

## 簡介

PandasAI 是一個革命性的 Python 庫，將生成式 AI 的能力與 Pandas 數據分析相結合。它允許你使用自然語言與數據進行對話，無需編寫複雜的查詢或代碼。PandasAI 可以理解你的問題，生成相應的 Python 代碼，執行它，並返回結果。

PandasAI 不僅僅是一個問答工具，它還能：
- 自動生成數據可視化
- 清理和轉換數據
- 提供數據洞察和建議
- 支持多種數據源（CSV、Excel、SQL 數據庫等）
- 與商業智能工具整合

## 核心特點

### 1. 自然語言查詢
使用日常語言向你的數據提問，無需記憶複雜的 Pandas 語法：
```python
agent.chat("銷售額最高的 5 個產品是什麼？")
```

### 2. 智能數據分析
自動執行探索性數據分析（EDA），識別模式、異常值和趨勢：
```python
agent.chat("分析這個數據集的主要特徵")
```

### 3. 自動可視化
根據你的問題自動生成合適的圖表和可視化：
```python
agent.chat("畫出每月銷售趨勢圖")
```

### 4. 多數據源支持
輕鬆連接和查詢多種數據源：
- Pandas DataFrame
- CSV/Excel 文件
- SQL 數據庫（MySQL、PostgreSQL、SQLite 等）
- NoSQL 數據庫
- 雲端數據倉庫（BigQuery、Snowflake 等）

### 5. 數據清理和轉換
智能處理缺失值、異常值和數據格式問題：
```python
agent.chat("清理這個數據集中的異常值")
```

### 6. 可擴展性
支持自定義函數、提示詞和工具，可根據特定需求定制：
```python
# 自定義提示詞以獲得更精確的結果
```

### 7. 隱私和安全
- 支持本地 LLM 運行
- 數據不會被發送到外部服務器（除非使用雲端 LLM）
- 可配置的安全設置

### 8. 緩存機制
智能緩存查詢結果，提高重複查詢的性能

## 安裝

### 基本安裝

```bash
pip install pandasai
```

### 完整安裝（包含所有依賴）

```bash
pip install -r requirements.txt
```

### 環境配置

創建 `.env` 文件並設置你的 API 密鑰：

```bash
OPENAI_API_KEY=your_openai_api_key_here
# 或使用其他 LLM 提供商
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key
```

## 使用案例

### 1. 快速開始
```python
from pandasai import Agent
import pandas as pd

# 創建數據集
df = pd.DataFrame({
    "產品": ["A", "B", "C"],
    "銷售額": [100, 200, 150]
})

# 創建 Agent
agent = Agent(df)

# 使用自然語言查詢
result = agent.chat("哪個產品的銷售額最高？")
print(result)
```

### 2. 數據可視化
```python
# 自動生成圖表
agent.chat("畫出產品銷售額的柱狀圖")
```

### 3. SQL 數據庫連接
```python
from pandasai import Agent
from pandasai.connectors import SQLConnector

# 連接到 SQL 數據庫
connector = SQLConnector(
    config={
        "dialect": "postgresql",
        "host": "localhost",
        "port": 5432,
        "database": "mydb",
        "username": "user",
        "password": "password",
        "table": "sales"
    }
)

agent = Agent(connector)
agent.chat("過去一個月的總銷售額是多少？")
```

### 4. 多數據源整合
```python
# 同時查詢多個數據源
sales_df = pd.read_csv("sales.csv")
customers_df = pd.read_csv("customers.csv")

agent = Agent([sales_df, customers_df])
agent.chat("哪些客戶的購買金額超過 10000？")
```

### 5. 數據分析和洞察
```python
agent.chat("分析銷售數據並提供增長建議")
```

## 支持的數據源

### 文件格式
- CSV
- Excel (XLS, XLSX)
- JSON
- Parquet
- Feather

### 數據庫
- **關係型數據庫**
  - PostgreSQL
  - MySQL
  - SQLite
  - SQL Server
  - Oracle

- **雲端數據倉庫**
  - Google BigQuery
  - Snowflake
  - Amazon Redshift
  - Databricks

- **NoSQL 數據庫**
  - MongoDB
  - Elasticsearch

### API 和雲端服務
- Google Sheets
- Airtable
- REST APIs
- GraphQL APIs

## 支持的 LLM 提供商

PandasAI 支持多種大語言模型：

- **OpenAI**: GPT-4, GPT-3.5
- **Anthropic**: Claude 3.5, Claude 3
- **Google**: PaLM 2, Gemini
- **本地模型**: Ollama, LM Studio
- **Azure OpenAI**
- **HuggingFace 模型**

## 項目結構

```
63.PandasAI/
├── README.md                 # 項目說明文件
├── requirements.txt          # 依賴項目
├── 01_快速開始.py           # 基本使用示例
├── 02_數據查詢.py           # 自然語言查詢示例
├── 03_數據分析.py           # 自動數據分析示例
├── 04_可視化生成.py         # 自動生成圖表示例
├── 05_SQL連接.py            # 數據庫連接示例
├── 06_多數據源.py           # 多數據源整合示例
├── 07_自定義提示.py         # 自定義 Prompt 示例
├── 08_緩存機制.py           # 結果緩存示例
├── 09_安全設置.py           # 安全配置示例
└── 10_BI整合.py             # 商業智能整合示例
```

## 進階功能

### 自定義函數
可以定義自己的函數供 AI 使用：
```python
agent.add_function(my_custom_function)
```

### 訓練和微調
可以通過提供示例來改進 AI 的響應：
```python
agent.train(questions=["..."], answers=["..."])
```

### 中間件
支持添加中間件來修改請求和響應

### 回調函數
監控 AI 的執行過程

## 最佳實踐

1. **明確的問題**：提出具體、清晰的問題以獲得更好的結果
2. **數據質量**：確保數據乾淨且格式正確
3. **安全設置**：在生產環境中啟用安全模式
4. **緩存使用**：為重複查詢啟用緩存以提高性能
5. **錯誤處理**：始終實施適當的錯誤處理
6. **API 限制**：注意 LLM 提供商的 API 速率限制

## 性能優化

- 使用緩存減少 API 調用
- 選擇合適的 LLM 模型（速度 vs 質量）
- 對大數據集進行預處理和採樣
- 使用本地 LLM 以減少延遲

## 限制和注意事項

1. **準確性**：AI 生成的代碼可能需要驗證
2. **隱私**：使用雲端 LLM 時注意數據隱私
3. **成本**：API 調用可能產生費用
4. **複雜查詢**：非常複雜的分析可能需要多次迭代

## 相關資源

- 官方文檔：https://docs.pandas-ai.com
- GitHub：https://github.com/gventuri/pandas-ai
- 社區論壇：https://github.com/gventuri/pandas-ai/discussions
- 示例庫：https://github.com/gventuri/pandas-ai/tree/main/examples

## 貢獻

歡迎貢獻！請查看示例文件了解如何使用 PandasAI 的各種功能。

## 許可證

PandasAI 使用 MIT 許可證。

## 聯繫方式

如有問題或建議，請訪問項目的 GitHub 頁面。

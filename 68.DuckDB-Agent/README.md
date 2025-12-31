# DuckDB-Agent 框架

## 簡介

DuckDB-Agent 是一個將嵌入式 OLAP 數據庫 DuckDB 與 AI Agent 整合的創新框架。DuckDB 是一個高性能的列式嵌入式分析數據庫，專為 OLAP（在線分析處理）工作負載設計。結合 AI Agent，可以實現自然語言查詢、智能數據分析和自動化 BI 應用。

## 核心特點

### 1. **嵌入式架構**
- 無需獨立服務器進程
- 零配置，開箱即用
- 進程內運行，極低延遲
- 支持持久化和內存模式

### 2. **高性能 OLAP**
- 列式存儲，查詢速度快
- 向量化執行引擎
- 並行查詢處理
- 智能查詢優化器

### 3. **豐富的數據格式支持**
- CSV、Parquet、JSON
- Pandas DataFrame 直接集成
- Arrow 格式零拷貝
- 遠程數據源（S3、HTTP）

### 4. **AI Agent 整合**
- Text-to-SQL 自然語言查詢
- 智能數據分析建議
- 自動化報表生成
- 異常檢測與洞察

### 5. **現代化特性**
- WASM 支持（瀏覽器運行）
- 向量擴展（相似度搜索）
- 全文搜索
- 地理空間分析

## 安裝

```bash
# 安裝依賴
pip install -r requirements.txt

# 或單獨安裝
pip install duckdb>=0.10.0
pip install openai>=1.50.0
pip install pandas>=2.0.0
pip install pyarrow>=14.0.0
```

## 快速開始

```python
import duckdb

# 創建內存數據庫
con = duckdb.connect(':memory:')

# 執行 SQL 查詢
result = con.execute("SELECT 42 AS answer").fetchall()
print(result)  # [(42,)]

# 直接查詢 Parquet 文件
con.execute("SELECT * FROM 'data.parquet' LIMIT 10")
```

## 使用案例

### 1. **快速數據分析**
```python
import duckdb
import pandas as pd

# 直接查詢 Pandas DataFrame
df = pd.read_csv('sales.csv')
result = duckdb.query("SELECT product, SUM(amount) FROM df GROUP BY product")
print(result.to_df())
```

### 2. **自然語言查詢**
```python
from openai import OpenAI

client = OpenAI()
user_question = "去年銷售額最高的前 10 個產品是什麼？"

# AI 生成 SQL
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": f"轉換為 SQL: {user_question}"}]
)

sql = response.choices[0].message.content
result = duckdb.query(sql)
```

### 3. **大規模數據處理**
```python
# 直接查詢 GB 級別的 Parquet 文件
duckdb.query("""
    SELECT
        date_trunc('month', order_date) as month,
        SUM(total_amount) as revenue
    FROM 'data/*.parquet'
    GROUP BY month
    ORDER BY month
""")
```

### 4. **向量搜索**
```python
# 安裝向量擴展
con.execute("INSTALL vss; LOAD vss;")

# 語義搜索
con.execute("""
    SELECT text,
           array_distance(embedding, [0.1, 0.2, 0.3]) as similarity
    FROM documents
    ORDER BY similarity
    LIMIT 5
""")
```

## 與傳統數據庫對比

| 特性 | DuckDB | PostgreSQL | SQLite | Spark |
|------|--------|------------|--------|-------|
| **架構** | 嵌入式 | 客戶端-服務器 | 嵌入式 | 分布式 |
| **OLAP 性能** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| **OLTP 性能** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ |
| **安裝難度** | 極簡 | 中等 | 極簡 | 複雜 |
| **資源消耗** | 低 | 中 | 極低 | 高 |
| **並行處理** | ✅ | ✅ | ❌ | ✅ |
| **Parquet 支持** | 原生 | 擴展 | 擴展 | 原生 |
| **Arrow 集成** | 零拷貝 | 有限 | 無 | 有限 |
| **WASM 支持** | ✅ | ❌ | ✅ | ❌ |

### 適用場景

#### ✅ DuckDB 適合：
- 數據分析與探索
- BI 報表生成
- 數據科學工作流
- 嵌入式分析應用
- 快速原型開發
- 日誌分析
- 時序數據分析

#### ❌ DuckDB 不適合：
- 高並發寫入（OLTP）
- 多用戶事務系統
- 需要強一致性的應用
- 超大規模分布式計算

## 示例文件說明

1. **01_快速開始.py** - DuckDB 基礎操作和連接管理
2. **02_SQL查詢.py** - 標準 SQL 查詢和聚合操作
3. **03_數據導入.py** - 從 CSV/Parquet 導入數據
4. **04_自然語言查詢.py** - 使用 AI 將自然語言轉換為 SQL
5. **05_分析函數.py** - 窗口函數和高級分析
6. **06_向量搜索.py** - 向量相似度搜索和語義檢索
7. **07_Agent整合.py** - 完整的 LLM Agent 數據分析助手
8. **08_WASM部署.py** - 在瀏覽器中運行 DuckDB
9. **09_性能優化.py** - 查詢優化和性能調優
10. **10_BI應用.py** - 構建商業智能儀表板

## 技術優勢

### 1. **零拷貝集成**
DuckDB 與 Pandas、Arrow 的零拷貝集成，數據傳輸無需序列化：
```python
import pandas as pd
df = pd.DataFrame({'a': [1, 2, 3]})
# 零拷貝查詢
result = duckdb.query("SELECT * FROM df WHERE a > 1")
```

### 2. **智能查詢優化**
- 謂詞下推（Predicate Pushdown）
- 列裁剪（Column Pruning）
- 投影下推（Projection Pushdown）
- 自動並行化

### 3. **豐富的函數庫**
- 200+ 內置函數
- 窗口函數
- 正則表達式
- JSON 處理
- 時間序列函數

## 生態系統

- **語言支持**: Python, R, Java, Node.js, Rust, Go
- **數據格式**: Parquet, CSV, JSON, Arrow, Excel
- **擴展**: 向量搜索、全文搜索、地理空間、HTTP
- **部署**: 本地、雲端、WASM（瀏覽器）

## 性能基準

在典型的分析查詢中（TPC-H Benchmark）：
- 比 SQLite 快 **10-100x**
- 比 Pandas 快 **5-50x**
- 接近或超過 PostgreSQL 的 OLAP 性能
- 單機性能接近小規模 Spark 集群

## 參考資源

- [官方網站](https://duckdb.org/)
- [官方文檔](https://duckdb.org/docs/)
- [GitHub](https://github.com/duckdb/duckdb)
- [Python API](https://duckdb.org/docs/api/python/overview)

## 授權

本示例代碼使用 MIT 授權。DuckDB 本身使用 MIT 授權。

## 貢獻

歡迎提交 Issue 和 Pull Request！

---

**注意**: 本框架示例使用 OpenAI API 進行 AI Agent 功能。使用前請設置 `OPENAI_API_KEY` 環境變量。

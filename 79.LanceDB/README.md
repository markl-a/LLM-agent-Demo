# LanceDB 向量數據庫完整範例

## 框架簡介

LanceDB 是一個開源的嵌入式向量數據庫，專為 AI 應用設計。它基於 Lance 列式數據格式構建，提供快速的向量相似度搜索、混合搜索和完整的 CRUD 操作，無需額外的服務器部署。

### 核心特點

#### 1. 嵌入式架構 🚀
- 無服務器設計，直接嵌入應用
- 零配置快速啟動
- 本地文件存儲
- 支持雲端部署

```python
import lancedb

# 創建/連接數據庫（就這麼簡單！）
db = lancedb.connect("./my_database")
```

#### 2. 高性能向量搜索 ⚡
- 基於 Lance 格式的列式存儲
- ANN（近似最近鄰）索引
- 毫秒級查詢響應
- 支持 GPU 加速

性能基準：
- 百萬級向量：< 10ms
- 十億級向量：< 100ms
- 磁盤空間效率高

#### 3. 混合搜索 🔍
- 向量相似度搜索
- 全文搜索（FTS）
- SQL WHERE 過濾
- 組合查詢能力

```python
# 混合搜索示例
results = table.search("AI technology") \
    .where("category = 'tech'") \
    .limit(10) \
    .to_pandas()
```

#### 4. 完整 CRUD 操作 💾
- Create: 創建表和插入數據
- Read: 向量搜索和查詢
- Update: 更新記錄
- Delete: 刪除數據

```python
# CRUD 示例
table.add(data)           # Create
table.search(vector)      # Read
table.update(updates)     # Update
table.delete("id = 123")  # Delete
```

#### 5. 多語言嵌入支持 🌐
- OpenAI embeddings
- Sentence Transformers
- Cohere embeddings
- 自定義嵌入模型
- 多模態嵌入（CLIP）

#### 6. 框架整合 🔗
- **LangChain** 原生支持
- **LlamaIndex** 完整整合
- **Pandas** DataFrame 兼容
- **Arrow** 格式支持

```python
from langchain_community.vectorstores import LanceDB

vectorstore = LanceDB(connection=db, embedding=embeddings)
```

#### 7. 版本控制 📊
- 數據版本管理
- 時間旅行查詢
- 回滾能力
- 完整的審計軌跡

#### 8. 雲端部署 ☁️
- LanceDB Cloud 整合
- S3/GCS/Azure 存儲
- 分佈式查詢
- 無縫擴展

## 安裝指南

### 基礎安裝
```bash
pip install lancedb
```

### 完整安裝（包含所有功能）
```bash
# 基礎 + OpenAI
pip install lancedb openai

# 基礎 + Sentence Transformers
pip install lancedb sentence-transformers

# 完整安裝
pip install lancedb openai sentence-transformers pandas pyarrow
```

### 開發環境設置
```bash
# 創建虛擬環境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安裝依賴
pip install lancedb openai sentence-transformers pandas

# 設置環境變量
export OPENAI_API_KEY='your-key-here'
```

## 快速開始

### 第一個向量數據庫

```python
import lancedb
import numpy as np

# 連接數據庫
db = lancedb.connect("./my_database")

# 準備數據（ID + 向量 + 元數據）
data = [
    {"id": 1, "vector": np.random.rand(128), "text": "First document"},
    {"id": 2, "vector": np.random.rand(128), "text": "Second document"},
]

# 創建表
table = db.create_table("documents", data)

# 向量搜索
query_vector = np.random.rand(128)
results = table.search(query_vector).limit(2).to_pandas()
print(results)
```

### 使用 OpenAI Embeddings

```python
import lancedb
from openai import OpenAI

client = OpenAI()

# 創建嵌入函數
def embed(text):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

# 準備數據
texts = ["AI is amazing", "Machine learning rocks"]
data = [{"text": t, "vector": embed(t)} for t in texts]

# 存儲
db = lancedb.connect("./db")
table = db.create_table("embeddings", data)

# 搜索
query = "artificial intelligence"
results = table.search(embed(query)).limit(1).to_pandas()
```

### LangChain 整合

```python
from langchain_community.vectorstores import LanceDB
from langchain_community.embeddings import OpenAIEmbeddings

# 創建 LanceDB 向量存儲
embeddings = OpenAIEmbeddings()
vectorstore = LanceDB.from_texts(
    texts=["Document 1", "Document 2"],
    embedding=embeddings,
    connection=lancedb.connect("./db")
)

# 相似度搜索
docs = vectorstore.similarity_search("query", k=2)
```

## 範例文件導覽

### 基礎篇

#### 01_快速開始.py
- LanceDB 基本概念
- 創建數據庫和表
- 基本的向量搜索
- 數據的增刪查改

#### 02_表操作.py
- 表的創建和配置
- Schema 定義
- 批量數據導入
- 表管理和維護

#### 03_向量搜索.py
- ANN 搜索算法
- 搜索參數調優
- 結果排序和過濾
- 性能優化技巧

#### 04_混合搜索.py
- 向量 + 關鍵詞搜索
- 全文搜索 (FTS)
- 過濾條件組合
- 複雜查詢構建

### 進階篇

#### 05_過濾查詢.py
- WHERE 子句
- 元數據過濾
- 範圍查詢
- 複雜條件組合

#### 06_嵌入模型.py
- OpenAI embeddings
- Sentence Transformers
- 自定義嵌入模型
- 多模態嵌入

#### 07_LangChain整合.py
- VectorStore 接口
- RAG 應用構建
- 文檔加載和切分
- 對話鏈構建

#### 08_LlamaIndex整合.py
- VectorStoreIndex
- 查詢引擎
- 響應合成
- 高級查詢模式

### 高級篇

#### 09_多模態存儲.py
- 文本 + 圖像嵌入
- CLIP 模型整合
- 跨模態搜索
- 多模態應用

#### 10_雲端部署.py
- LanceDB Cloud
- S3 存儲後端
- 分佈式部署
- 生產環境最佳實踐

## 核心概念

### Database（數據庫）

Database 是 LanceDB 的頂層抽象，包含多個表。

```python
import lancedb

# 本地數據庫
db = lancedb.connect("./local_db")

# 內存數據庫
db = lancedb.connect("memory://")

# S3 數據庫
db = lancedb.connect("s3://my-bucket/my-db")
```

### Table（表）

Table 存儲向量和元數據。

```python
# 創建表
table = db.create_table("my_table", data)

# 打開現有表
table = db.open_table("my_table")

# 列出所有表
tables = db.table_names()

# 刪除表
db.drop_table("my_table")
```

### Schema（模式）

定義表的結構。

```python
import pyarrow as pa

schema = pa.schema([
    pa.field("id", pa.int64()),
    pa.field("vector", pa.list_(pa.float32(), 128)),
    pa.field("text", pa.string()),
    pa.field("metadata", pa.string())
])

table = db.create_table("docs", schema=schema)
```

### Search（搜索）

向量相似度搜索。

```python
# 基本搜索
results = table.search(query_vector).limit(10).to_pandas()

# 帶過濾的搜索
results = table.search(query_vector) \
    .where("category = 'tech'") \
    .limit(10) \
    .to_pandas()

# 指定距離度量
results = table.search(query_vector) \
    .metric("cosine") \
    .limit(10) \
    .to_pandas()
```

### Indexing（索引）

創建 ANN 索引以加速搜索。

```python
# 創建 IVF-PQ 索引
table.create_index(
    metric="cosine",
    num_partitions=256,
    num_sub_vectors=16
)

# 搜索會自動使用索引
results = table.search(vector).limit(10)
```

## 最佳實踐

### 1. 數據模型設計

```python
# 良好的 schema 設計
schema = pa.schema([
    pa.field("id", pa.string()),           # 唯一標識符
    pa.field("vector", pa.list_(pa.float32(), 1536)),  # 嵌入向量
    pa.field("text", pa.string()),         # 原始文本
    pa.field("metadata", pa.struct([       # 結構化元數據
        ("category", pa.string()),
        ("timestamp", pa.timestamp("us")),
        ("tags", pa.list_(pa.string()))
    ]))
])
```

### 2. 批量操作

```python
# 批量插入（更高效）
batch_size = 1000
for i in range(0, len(data), batch_size):
    batch = data[i:i + batch_size]
    table.add(batch)

# 而非逐條插入
# for item in data:
#     table.add([item])  # 效率低
```

### 3. 索引策略

```python
# 對於大型數據集創建索引
if table.count_rows() > 100000:
    table.create_index(
        metric="cosine",
        num_partitions=256,  # 根據數據量調整
        num_sub_vectors=16   # 壓縮級別
    )
```

### 4. 查詢優化

```python
# 使用 where 過濾減少搜索空間
results = table.search(vector) \
    .where("timestamp > '2024-01-01'") \
    .limit(10) \
    .to_pandas()

# 選擇需要的列
results = table.search(vector) \
    .select(["id", "text"]) \
    .limit(10) \
    .to_pandas()
```

### 5. 內存管理

```python
# 使用迭代器處理大結果集
for batch in table.search(vector).limit(10000).to_batches():
    # 處理 batch
    process(batch)

# 而非一次加載全部
# results = table.search(vector).limit(10000).to_pandas()  # 可能OOM
```

## 高級功能

### 全文搜索

```python
# 創建 FTS 索引
table.create_fts_index("text")

# 全文搜索
results = table.search("machine learning", query_type="fts") \
    .limit(10) \
    .to_pandas()
```

### 混合搜索

```python
# 向量 + 全文 + 過濾
results = table.search(vector) \
    .where("category = 'tech'") \
    .limit(10) \
    .to_pandas()
```

### 版本管理

```python
# 獲取表的版本
version = table.version()

# 檢出特定版本
table.checkout(version - 1)

# 查看版本歷史
versions = table.list_versions()
```

### 自定義嵌入函數

```python
class CustomEmbedding:
    def embed_documents(self, texts):
        # 自定義嵌入邏輯
        return [self.embed(text) for text in texts]

    def embed_query(self, text):
        # 自定義查詢嵌入
        return self.embed(text)

    def embed(self, text):
        # 實現嵌入
        return np.random.rand(128)
```

## 實際應用場景

### 1. RAG 應用
- 問答系統
- 文檔檢索
- 知識庫搜索
- 上下文增強生成

### 2. 推薦系統
- 內容推薦
- 產品推薦
- 用戶匹配
- 相似項查找

### 3. 語義搜索
- 企業搜索
- 文檔管理
- 代碼搜索
- 多語言搜索

### 4. 圖像搜索
- 視覺搜索
- 以圖搜圖
- 商品查找
- 人臉識別

## 性能基準

### 搜索延遲
- 1K 向量：< 1ms
- 100K 向量：< 10ms
- 1M 向量：< 50ms
- 10M 向量：< 200ms

### 存儲效率
- 原始向量：100%
- IVF 索引：~120%
- PQ 壓縮：~20-30%

### 吞吐量
- 插入：10K-100K 向量/秒
- 查詢：1K-10K QPS

*基於 1536 維向量，Intel Xeon CPU*

## 與其他向量數據庫比較

| 特性 | LanceDB | Pinecone | Milvus | Chroma |
|------|---------|----------|--------|--------|
| 部署 | 嵌入式 | 雲服務 | 自託管 | 嵌入式 |
| 成本 | 免費 | 付費 | 免費 | 免費 |
| 擴展性 | 高 | 非常高 | 高 | 中 |
| 混合搜索 | ✅ | ✅ | ✅ | ❌ |
| 版本控制 | ✅ | ❌ | ❌ | ❌ |
| GPU | ✅ | ✅ | ✅ | ❌ |

## 參考資源

### 官方文檔
- [LanceDB 官網](https://lancedb.com/)
- [文檔](https://lancedb.github.io/lancedb/)
- [GitHub](https://github.com/lancedb/lancedb)

### 教程和示例
- [快速入門](https://lancedb.github.io/lancedb/basic/)
- [LangChain 集成](https://lancedb.github.io/lancedb/integrations/langchain/)
- [示例應用](https://github.com/lancedb/lancedb/tree/main/examples)

### 社區
- [Discord](https://discord.gg/lancedb)
- [GitHub Discussions](https://github.com/lancedb/lancedb/discussions)
- [Twitter](https://twitter.com/lancedb)

## 常見問題

### Q: LanceDB vs Chroma，如何選擇？

**A:**
- LanceDB：更適合需要混合搜索、版本控制、大規模數據
- Chroma：更適合簡單的向量搜索、快速原型

### Q: 可以在生產環境使用嗎？

**A:** 可以！LanceDB 已在多個生產環境中使用，支持：
- 雲端部署
- 高可用性
- 數據持久化
- 性能監控

### Q: 如何遷移現有數據？

**A:**
```python
# 從其他向量數據庫遷移
import lancedb

db = lancedb.connect("./db")
table = db.create_table("migrated", data_from_other_db)
```

### Q: 支持哪些嵌入模型？

**A:** 幾乎所有！
- OpenAI embeddings
- Sentence Transformers
- Cohere
- HuggingFace 模型
- 自定義模型

## 貢獻指南

歡迎貢獻新的範例或改進現有代碼！

1. Fork 本倉庫
2. 創建功能分支
3. 編寫清晰的中文註釋
4. 測試代碼
5. 提交 Pull Request

## 授權

本範例集採用 MIT 授權，可自由使用和修改。

## 更新日誌

- **2025-01**: 創建初始範例集
- 包含 10 個完整範例
- 涵蓋所有核心功能
- 完整繁體中文註釋

---

**開始探索** → 從 `01_快速開始.py` 開始你的 LanceDB 之旅！

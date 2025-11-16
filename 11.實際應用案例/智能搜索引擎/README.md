# 智能搜索引擎

結合傳統關鍵詞搜索和 AI 語義搜索的混合搜索系統，提供更準確、更智能的搜索體驗。

## 功能特點

### 1. 混合搜索
- **關鍵詞搜索**: 基於詞匹配的傳統搜索
- **語義搜索**: 基於向量相似度的語義理解
- **智能融合**: 自動調整權重，結合兩種搜索優勢

### 2. 結果重排序 (Reranking)
- 使用 LLM 理解查詢意圖
- 根據相關性重新排序結果
- 提高前排結果的質量

### 3. 自動摘要生成
- 整合多個搜索結果
- 生成簡潔、準確的答案摘要
- 直接回答用戶問題

### 4. 相關查詢推薦
- 基於當前搜索生成延伸建議
- 幫助用戶探索相關主題
- 提升搜索體驗

## 架構設計

```
┌──────────────┐
│  用戶查詢     │
└──────┬───────┘
       │
   ┌───▼────────────────┐
   │   混合搜索引擎      │
   └───┬────────────────┘
       │
  ┌────┴─────┐
  │          │
  ▼          ▼
┌─────┐  ┌──────┐
│關鍵詞│  │語義  │
│搜索  │  │搜索  │
└──┬──┘  └───┬──┘
   │         │
   └────┬────┘
        │
   ┌────▼─────┐
   │ 結果合併  │
   └────┬─────┘
        │
   ┌────▼──────┐
   │ LLM重排序 │
   └────┬──────┘
        │
   ┌────▼──────┐
   │ 摘要生成  │
   └────┬──────┘
        │
   ┌────▼──────────┐
   │ 相關查詢推薦  │
   └────┬──────────┘
        │
   ┌────▼──────┐
   │ 返回結果  │
   └───────────┘
```

## 快速開始

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 配置環境變數

```bash
export OPENAI_API_KEY='your-openai-api-key'
```

### 3. 運行搜索引擎

```bash
python main.py
```

## 使用範例

### 範例 1：技術查詢

```
🔍 請輸入搜索查詢: Python 數據分析

📊 執行混合搜索...
🔄 重排序結果...
📝 生成摘要...
💡 生成相關查詢...

============================================================
搜索時間: 2.34 秒
============================================================

📋 摘要:
------------------------------------------------------------
Python 是數據分析領域最流行的程式語言之一。Pandas 是 Python 中
最強大的數據分析庫，提供了高性能、易於使用的數據結構（如 DataFrame）
和豐富的數據操作工具。

對於想要進行數據分析的開發者，建議從 Python 基礎語法開始學習，
然後深入 Pandas、NumPy 等核心庫。這些工具能夠處理各種規模的
數據集，從小型實驗到大規模數據處理都能勝任。

📚 搜索結果:
------------------------------------------------------------

1. Python 數據分析 - Pandas 教程
   相關性: 2.850 | 來源: hybrid
   連結: https://example.com/pandas-tutorial
   Pandas 是 Python 中最流行的數據分析庫。它提供了高性能、
   易於使用的數據結構和數據分析工具...

2. Python 入門教程 - 基礎語法
   相關性: 1.920 | 來源: hybrid
   連結: https://example.com/python-basics
   Python 是一種直譯式、高階、通用的程式語言...

💡 相關搜索:
------------------------------------------------------------
1. Pandas 進階數據處理技巧
2. Python 數據視覺化工具
3. NumPy 和 Pandas 的區別
```

### 範例 2：AI/ML 查詢

```
🔍 請輸入搜索查詢: 什麼是 RAG

📋 摘要:
------------------------------------------------------------
RAG（Retrieval-Augmented Generation）是一種創新的技術，結合了
檢索和生成兩個階段。它的工作原理是：首先從知識庫中檢索與查詢
相關的文檔，然後將這些檢索結果作為上下文提供給大型語言模型
（LLM）來生成回答。

RAG 技術的主要優勢是能夠有效減少 LLM 的「幻覺」問題（生成不準確
或虛假的信息），因為生成的回答基於實際檢索到的文檔內容。這使得
RAG 特別適合需要準確性和可靠性的應用場景。

📚 搜索結果:
------------------------------------------------------------

1. RAG 技術詳解
   相關性: 2.950 | 來源: semantic
   連結: https://example.com/rag-explained
   ...

💡 相關搜索:
------------------------------------------------------------
1. RAG 與傳統問答系統的區別
2. 如何優化 RAG 系統性能
3. RAG 的實際應用案例
```

## API 使用

### 基本搜索

```python
from main import IntelligentSearchEngine

# 初始化搜索引擎
search_engine = IntelligentSearchEngine()

# 執行搜索
response = search_engine.search(
    query="Python 機器學習",
    top_k=5,
    use_rerank=True
)

# 獲取結果
print(f"摘要: {response.summary}")
print(f"結果數: {len(response.results)}")
print(f"搜索時間: {response.search_time}秒")

# 訪問單個結果
for result in response.results:
    print(f"標題: {result.title}")
    print(f"分數: {result.score}")
    print(f"來源: {result.source}")
```

### 只使用關鍵詞搜索

```python
results = search_engine.keyword_search("Python", top_k=5)
```

### 只使用語義搜索

```python
results = search_engine.semantic_search("機器學習入門", top_k=5)
```

### 自定義權重的混合搜索

```python
results = search_engine.hybrid_search(
    query="深度學習",
    top_k=5,
    keyword_weight=0.4,  # 關鍵詞權重 40%
    semantic_weight=0.6   # 語義權重 60%
)
```

## 進階功能

### 1. 添加自定義文檔

修改 `main.py` 中的 `SAMPLE_DOCUMENTS`:

```python
SAMPLE_DOCUMENTS = [
    {
        "id": "doc_custom_1",
        "title": "你的文檔標題",
        "content": "你的文檔內容...",
        "url": "https://example.com/your-doc"
    },
    # 添加更多文檔...
]
```

### 2. 從文件加載文檔

```python
import json

# 從 JSON 文件加載
with open('documents.json', 'r', encoding='utf-8') as f:
    SAMPLE_DOCUMENTS = json.load(f)
```

### 3. 整合外部搜索 API

```python
def search_with_google(query):
    """整合 Google Search API"""
    # 使用 Serper API
    from langchain_community.utilities import GoogleSerperAPIWrapper

    search = GoogleSerperAPIWrapper()
    results = search.results(query)

    # 轉換為 SearchResult 格式
    ...
```

### 4. 持久化向量存儲

```python
# 保存向量存儲
vectorstore.save_local("./faiss_index")

# 加載已保存的向量存儲
from langchain_community.vectorstores import FAISS

vectorstore = FAISS.load_local(
    "./faiss_index",
    embeddings=embeddings
)
```

### 5. 使用其他向量數據庫

#### Pinecone

```python
from langchain_community.vectorstores import Pinecone
import pinecone

pinecone.init(
    api_key=os.getenv("PINECONE_API_KEY"),
    environment=os.getenv("PINECONE_ENVIRONMENT")
)

vectorstore = Pinecone.from_documents(
    docs,
    embeddings,
    index_name="search-engine"
)
```

#### Chroma

```python
from langchain_community.vectorstores import Chroma

vectorstore = Chroma.from_documents(
    docs,
    embeddings,
    persist_directory="./chroma_db"
)
```

## 配置選項

### 搜索參數調整

```python
# 調整返回結果數量
response = search_engine.search(query, top_k=10)

# 禁用重排序（更快）
response = search_engine.search(query, use_rerank=False)

# 調整混合搜索權重
results = search_engine.hybrid_search(
    query,
    keyword_weight=0.5,
    semantic_weight=0.5
)
```

### 模型選擇

```python
# 使用更快的模型
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# 使用更準確的模型
llm = ChatOpenAI(model="gpt-4", temperature=0.7)

# 調整創造性
llm = ChatOpenAI(model="gpt-4o", temperature=0.3)  # 更保守
```

## 性能優化

### 1. 緩存搜索結果

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_search(query: str):
    return search_engine.search(query)
```

### 2. 批量處理

```python
def batch_search(queries: List[str]) -> List[SearchResponse]:
    """批量搜索多個查詢"""
    responses = []
    for query in queries:
        response = search_engine.search(query)
        responses.append(response)
    return responses
```

### 3. 異步處理

```python
import asyncio

async def async_search(query: str):
    """異步搜索"""
    # 使用異步 LLM 調用
    ...
```

## 評估指標

### 搜索質量評估

```python
def evaluate_search_quality(test_queries):
    """評估搜索質量"""
    total_time = 0
    results_count = 0

    for query, expected_docs in test_queries.items():
        response = search_engine.search(query)

        # 計算命中率
        hits = sum(1 for r in response.results if r.id in expected_docs)
        precision = hits / len(response.results) if response.results else 0

        total_time += response.search_time
        results_count += len(response.results)

        print(f"查詢: {query}")
        print(f"精確率: {precision:.2%}")
        print(f"搜索時間: {response.search_time:.2f}秒")
```

## 常見問題

### Q1: 如何提高搜索準確性？

1. 增加文檔數量和質量
2. 優化文檔內容和標題
3. 調整混合搜索權重
4. 使用更好的 embedding 模型
5. 啟用重排序功能

### Q2: 搜索速度太慢怎麼辦？

1. 禁用重排序（`use_rerank=False`）
2. 減少返回結果數量（`top_k`）
3. 使用更快的模型（`gpt-4o-mini`）
4. 實現結果緩存
5. 使用專業向量數據庫

### Q3: 如何處理大量文檔？

1. 使用專業向量數據庫（Pinecone、Weaviate）
2. 實現分片索引
3. 使用異步處理
4. 添加預過濾邏輯
5. 考慮分佈式部署

## 部署建議

### Docker 部署

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

### API 服務

使用 FastAPI 提供 REST API：

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
search_engine = IntelligentSearchEngine()

class SearchQuery(BaseModel):
    query: str
    top_k: int = 5
    use_rerank: bool = True

@app.post("/search")
def search(query: SearchQuery):
    response = search_engine.search(
        query.query,
        top_k=query.top_k,
        use_rerank=query.use_rerank
    )
    return response
```

## 授權

MIT License

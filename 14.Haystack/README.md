# Haystack AI 框架完整教程

## 目錄

- [1. Haystack 簡介](#1-haystack-簡介)
- [2. 核心概念](#2-核心概念)
- [3. 環境設置](#3-環境設置)
- [4. Document Store](#4-document-store)
- [5. Pipeline 設計](#5-pipeline-設計)
- [6. Retriever 檢索器](#6-retriever-檢索器)
- [7. Generator 生成器](#7-generator-生成器)
- [8. 完整 RAG 流程](#8-完整-rag-流程)
- [9. 框架對比](#9-框架對比)
- [10. 最佳實踐](#10-最佳實踐)
- [11. 進階功能](#11-進階功能)
- [12. 常見問題](#12-常見問題)

---

## 1. Haystack 簡介

### 1.1 什麼是 Haystack？

Haystack 是由 deepset 開發的開源 NLP 框架，專注於構建基於大型語言模型的搜索和問答系統。它是一個 **RAG 原生** 的框架，為檢索增強生成（Retrieval-Augmented Generation）提供了完整的解決方案。

### 1.2 核心特點

#### RAG 原生設計
- 從設計之初就專注於 RAG 場景
- 提供完整的文檔處理、索引、檢索、生成流程
- 優化的向量檢索和語義搜索能力

#### Pipeline 架構
- 模塊化的管道設計
- 靈活的組件組合
- 可視化的工作流

#### 開源生態
- 完全開源（Apache 2.0）
- 活躍的社區支持
- 豐富的預構建組件

#### 生產就緒
- 企業級性能和穩定性
- 支持多種部署方式
- 完善的監控和日誌

### 1.3 主要用途

```
1. 問答系統（QA）
   - 文檔問答
   - 知識庫查詢
   - FAQ 系統

2. 語義搜索
   - 企業文檔搜索
   - 產品信息檢索
   - 學術論文查找

3. 文檔分析
   - 合同分析
   - 報告摘要
   - 內容提取

4. RAG 應用
   - 對話系統
   - 智能客服
   - 知識助手
```

### 1.4 架構概覽

```
┌─────────────────────────────────────────────────┐
│                  Haystack Pipeline              │
├─────────────────────────────────────────────────┤
│                                                 │
│  Document Ingestion     →    Document Store     │
│  ├─ Converters                ├─ Elasticsearch │
│  ├─ Preprocessors             ├─ Weaviate      │
│  └─ Embedders                 ├─ Pinecone      │
│                               └─ InMemory      │
│                                                 │
│  Retrieval              →    Generation         │
│  ├─ Dense Retriever           ├─ LLM Generator │
│  ├─ Sparse Retriever          ├─ Prompt Node   │
│  └─ Hybrid Retriever          └─ Custom Node   │
│                                                 │
│  Evaluation             →    Deployment         │
│  ├─ Metrics                   ├─ REST API      │
│  ├─ Feedback                  ├─ Docker        │
│  └─ Monitoring                └─ Cloud         │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 🔥 完整示例代碼 (20 個)

### 基礎入門 (1-5)
1. **[RAG 基礎](01_RAG基礎.py)** - Haystack 快速開始、基礎 RAG 實現、文檔問答
2. **[文檔處理](02_文檔處理.py)** - 文檔清洗、分塊、格式轉換、預處理
3. **[多種檢索器](03_多種檢索器.py)** - BM25、向量檢索、混合檢索策略
4. **[Pipeline 構建](04_Pipeline構建.py)** - 管道設計、組件連接、DAG 構建
5. **[問答系統](05_問答系統.py)** - 提取式問答、生成式問答、答案評分

### 核心功能 (6-10)
6. **[嵌入模型](06_嵌入模型.py)** - Sentence Transformers、DPR、自定義嵌入
7. **[文檔存儲](07_文檔存儲.py)** - InMemory、Elasticsearch、Weaviate、Pinecone
8. **[Ranker 重排序](08_Ranker重排序.py)** - 交叉編碼器、多階段排序、相關性優化
9. **[生成器 Generator](09_生成器Generator.py)** - PromptNode、RAG 生成、提示模板
10. **[路由 Router](10_路由Router.py)** - 條件路由、多路徑執行、動態分支

### 進階應用 (11-15)
11. **[Web 檢索](11_Web檢索.py)** - 網頁爬取、實時搜索、外部數據集成
12. **[評估 Evaluation](12_評估Evaluation.py)** - 檢索評估、生成評估、端到端評估
13. **[Agent 代理](13_Agent代理.py)** - Agent Pipeline、工具調用、自主決策
14. **[流式處理](14_流式處理.py)** - 實時響應、流式生成、逐 token 輸出
15. **[自定義組件](15_自定義組件.py)** - 創建自定義節點、擴展 Pipeline 功能

### 實戰場景 (16-20)
16. **[多語言支持](16_多語言支持.py)** - 多語言模型、跨語言檢索、翻譯集成
17. **[提示詞管理](17_提示詞管理.py)** - 提示模板、Few-shot、鏈式提示
18. **[錯誤處理](18_錯誤處理.py)** - 異常捕獲、重試機制、降級策略
19. **[性能優化](19_性能優化.py)** - 批量處理、緩存策略、並發控制
20. **[部署與監控](20_部署與監控.py)** - REST API、Docker 部署、性能監控

> 💡 **提示**: 所有示例都包含完整的代碼、詳細註釋和生產級最佳實踐，可直接用於構建企業級 RAG 系統。

---

## 2. 核心概念

### 2.1 Document

Document 是 Haystack 中的基本數據單元：

```python
from haystack import Document

# 創建文檔
doc = Document(
    content="Haystack 是一個強大的 NLP 框架",
    meta={
        "name": "intro.txt",
        "category": "tutorial",
        "author": "deepset"
    }
)

# 文檔屬性
print(doc.id)          # 唯一標識符
print(doc.content)     # 文檔內容
print(doc.meta)        # 元數據
print(doc.embedding)   # 向量嵌入（可選）
```

### 2.2 Document Store

Document Store 是文檔存儲和檢索的核心：

```python
# 支持多種後端
- InMemoryDocumentStore    # 內存存儲（開發測試）
- ElasticsearchDocumentStore  # Elasticsearch
- WeaviateDocumentStore    # Weaviate 向量數據庫
- PineconeDocumentStore    # Pinecone 向量數據庫
- FAISSDocumentStore       # Facebook AI Similarity Search
- MilvusDocumentStore      # Milvus 向量數據庫
```

### 2.3 Pipeline

Pipeline 是組件的有向無環圖（DAG）：

```python
from haystack import Pipeline

# 創建管道
pipeline = Pipeline()

# 添加節點
pipeline.add_node(component=retriever, name="Retriever", inputs=["Query"])
pipeline.add_node(component=reader, name="Reader", inputs=["Retriever"])

# 運行管道
result = pipeline.run(query="What is Haystack?")
```

### 2.4 Node（節點）

Node 是 Pipeline 中的處理單元：

**常用節點類型：**
- **Retriever**: 檢索相關文檔
- **Reader**: 從文檔中提取答案
- **Generator**: 生成文本回答
- **Ranker**: 對結果排序
- **Summarizer**: 文檔摘要
- **Translator**: 文本翻譯

---

## 3. 環境設置

### 3.1 安裝 Haystack

```bash
# 基礎安裝
pip install farm-haystack

# 包含所有依賴
pip install farm-haystack[all]

# 特定後端
pip install farm-haystack[elasticsearch]
pip install farm-haystack[weaviate]
pip install farm-haystack[pinecone]

# GPU 支持
pip install farm-haystack[gpu]
```

### 3.2 依賴項

```bash
# 核心依賴
transformers>=4.0.0
torch>=1.9.0
requests>=2.25.0

# 可選依賴
elasticsearch>=7.0.0    # Elasticsearch 支持
weaviate-client>=3.0.0  # Weaviate 支持
pinecone-client>=2.0.0  # Pinecone 支持
faiss-cpu>=1.7.0        # FAISS 支持
```

### 3.3 環境配置

```python
import os
from dotenv import load_dotenv

# 加載環境變量
load_dotenv()

# API 密鑰配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "localhost")
WEAVIATE_HOST = os.getenv("WEAVIATE_HOST", "localhost")
```

---

## 4. Document Store

### 4.1 InMemoryDocumentStore

適合開發和小規模應用：

```python
from haystack.document_stores import InMemoryDocumentStore

# 創建內存存儲
document_store = InMemoryDocumentStore(
    use_bm25=True,              # 使用 BM25 算法
    embedding_dim=768,          # 嵌入維度
    similarity="cosine"         # 相似度度量
)

# 寫入文檔
documents = [
    Document(content="Paris is the capital of France."),
    Document(content="Berlin is the capital of Germany."),
]
document_store.write_documents(documents)

# 查詢文檔
results = document_store.query(query="capital of France")
```

### 4.2 ElasticsearchDocumentStore

適合生產環境：

```python
from haystack.document_stores import ElasticsearchDocumentStore

# 創建 Elasticsearch 存儲
document_store = ElasticsearchDocumentStore(
    host="localhost",
    port=9200,
    username="elastic",
    password="password",
    index="documents",
    embedding_dim=768,
    similarity="cosine"
)

# 批量寫入
document_store.write_documents(
    documents=documents,
    batch_size=1000
)

# 更新嵌入
document_store.update_embeddings(
    retriever=retriever,
    batch_size=100
)
```

### 4.3 WeaviateDocumentStore

向量數據庫優化：

```python
from haystack.document_stores import WeaviateDocumentStore

# 創建 Weaviate 存儲
document_store = WeaviateDocumentStore(
    host="http://localhost",
    port=8080,
    embedding_dim=768,
    index="Document",
    similarity="cosine",
    progress_bar=True
)

# 配置索引
document_store.create_index(
    index_name="Document",
    schema={
        "class": "Document",
        "properties": [
            {"name": "content", "dataType": ["text"]},
            {"name": "meta", "dataType": ["object"]}
        ]
    }
)
```

### 4.4 操作示例

```python
# 搜索文檔
results = document_store.query(
    query="machine learning",
    top_k=10,
    filters={"category": ["AI", "ML"]}
)

# 通過 ID 獲取
doc = document_store.get_document_by_id("doc_123")

# 更新文檔
document_store.update_document_meta(
    id="doc_123",
    meta={"status": "reviewed"}
)

# 刪除文檔
document_store.delete_documents(
    ids=["doc_1", "doc_2"]
)

# 統計信息
count = document_store.get_document_count()
labels_count = document_store.get_label_count()
```

---

## 5. Pipeline 設計

### 5.1 基礎 Pipeline

```python
from haystack import Pipeline
from haystack.nodes import BM25Retriever, FARMReader

# 初始化組件
retriever = BM25Retriever(document_store=document_store)
reader = FARMReader(model_name_or_path="deepset/roberta-base-squad2")

# 創建管道
pipeline = Pipeline()
pipeline.add_node(component=retriever, name="Retriever", inputs=["Query"])
pipeline.add_node(component=reader, name="Reader", inputs=["Retriever"])

# 運行
result = pipeline.run(
    query="What is machine learning?",
    params={
        "Retriever": {"top_k": 10},
        "Reader": {"top_k": 5}
    }
)
```

### 5.2 RAG Pipeline

```python
from haystack.nodes import PromptNode, PromptTemplate

# 創建提示模板
prompt_template = PromptTemplate(
    name="rag-template",
    prompt_text="""
    Answer the question based on the context below.

    Context: {join(documents)}

    Question: {query}

    Answer:
    """
)

# 創建生成器
generator = PromptNode(
    model_name_or_path="gpt-3.5-turbo",
    api_key=OPENAI_API_KEY,
    default_prompt_template=prompt_template
)

# RAG 管道
rag_pipeline = Pipeline()
rag_pipeline.add_node(component=retriever, name="Retriever", inputs=["Query"])
rag_pipeline.add_node(component=generator, name="Generator", inputs=["Retriever"])
```

### 5.3 混合檢索 Pipeline

```python
from haystack.nodes import EmbeddingRetriever, JoinDocuments

# 密集檢索器
dense_retriever = EmbeddingRetriever(
    document_store=document_store,
    embedding_model="sentence-transformers/all-MiniLM-L6-v2"
)

# 稀疏檢索器
sparse_retriever = BM25Retriever(document_store=document_store)

# 結果合併
join_documents = JoinDocuments(join_mode="merge")

# 混合管道
hybrid_pipeline = Pipeline()
hybrid_pipeline.add_node(component=sparse_retriever, name="BM25", inputs=["Query"])
hybrid_pipeline.add_node(component=dense_retriever, name="Dense", inputs=["Query"])
hybrid_pipeline.add_node(
    component=join_documents,
    name="Join",
    inputs=["BM25", "Dense"]
)
hybrid_pipeline.add_node(component=reader, name="Reader", inputs=["Join"])
```

### 5.4 條件路由

```python
from haystack.nodes import RouteDocuments

# 路由節點
route_documents = RouteDocuments(
    split_by="content_type",
    metadata_values=["pdf", "txt", "html"]
)

# 條件管道
conditional_pipeline = Pipeline()
conditional_pipeline.add_node(
    component=route_documents,
    name="Router",
    inputs=["Query"]
)
conditional_pipeline.add_node(
    component=pdf_converter,
    name="PDFConverter",
    inputs=["Router.output_1"]
)
conditional_pipeline.add_node(
    component=text_converter,
    name="TextConverter",
    inputs=["Router.output_2"]
)
```

---

## 6. Retriever 檢索器

### 6.1 BM25Retriever（稀疏檢索）

```python
from haystack.nodes import BM25Retriever

retriever = BM25Retriever(
    document_store=document_store,
    top_k=10
)

# 檢索
documents = retriever.retrieve(
    query="What is AI?",
    top_k=5,
    filters={"category": ["technology"]}
)
```

### 6.2 EmbeddingRetriever（密集檢索）

```python
from haystack.nodes import EmbeddingRetriever

retriever = EmbeddingRetriever(
    document_store=document_store,
    embedding_model="sentence-transformers/all-MiniLM-L6-v2",
    model_format="sentence_transformers",
    top_k=10
)

# 更新嵌入
document_store.update_embeddings(retriever)

# 檢索
documents = retriever.retrieve(
    query="machine learning applications",
    top_k=5
)
```

### 6.3 DensePassageRetriever

```python
from haystack.nodes import DensePassageRetriever

retriever = DensePassageRetriever(
    document_store=document_store,
    query_embedding_model="facebook/dpr-question_encoder-single-nq-base",
    passage_embedding_model="facebook/dpr-ctx_encoder-single-nq-base",
    use_gpu=True
)
```

### 6.4 MultiModalRetriever

```python
from haystack.nodes import MultiModalRetriever

retriever = MultiModalRetriever(
    document_store=document_store,
    query_embedding_model="sentence-transformers/clip-ViT-B-32",
    query_type="text",
    document_embedding_models={
        "text": "sentence-transformers/all-MiniLM-L6-v2",
        "image": "sentence-transformers/clip-ViT-B-32"
    }
)
```

---

## 7. Generator 生成器

### 7.1 PromptNode

```python
from haystack.nodes import PromptNode

# OpenAI Generator
generator = PromptNode(
    model_name_or_path="gpt-3.5-turbo",
    api_key=OPENAI_API_KEY,
    max_length=200,
    temperature=0.7
)

# 生成答案
answer = generator.run(
    query="What is Haystack?",
    documents=retrieved_docs
)
```

### 7.2 自定義提示模板

```python
from haystack.nodes import PromptTemplate

# QA 模板
qa_template = PromptTemplate(
    name="question-answering",
    prompt_text="""
    Answer the question truthfully based solely on the given documents.
    If the documents do not contain the answer, say 'I don't know'.

    Documents:
    {join(documents, delimiter=new_line, pattern='Document $idx: $content')}

    Question: {query}
    Answer:
    """
)

# 摘要模板
summary_template = PromptTemplate(
    name="summarization",
    prompt_text="""
    Summarize the following documents in 3-5 sentences:

    {join(documents)}

    Summary:
    """
)

# 使用模板
generator = PromptNode(
    model_name_or_path="gpt-3.5-turbo",
    api_key=OPENAI_API_KEY,
    default_prompt_template=qa_template
)
```

### 7.3 RAG Generator

```python
from haystack.nodes import RAGenerator

rag_generator = RAGenerator(
    model_name_or_path="facebook/rag-token-nq",
    retriever=retriever,
    generator_type="token",
    num_beams=5,
    max_length=200,
    min_length=2,
    embed_title=True
)
```

---

## 8. 完整 RAG 流程

### 8.1 數據準備

```python
from haystack import Document
from haystack.nodes import PreProcessor

# 文檔預處理器
preprocessor = PreProcessor(
    clean_empty_lines=True,
    clean_whitespace=True,
    clean_header_footer=True,
    split_by="word",
    split_length=200,
    split_overlap=20,
    split_respect_sentence_boundary=True
)

# 加載和處理文檔
raw_docs = [
    Document(content="Long document content..."),
    Document(content="Another document...")
]

processed_docs = preprocessor.process(raw_docs)
document_store.write_documents(processed_docs)
```

### 8.2 索引構建

```python
# 創建嵌入
retriever = EmbeddingRetriever(
    document_store=document_store,
    embedding_model="sentence-transformers/all-MiniLM-L6-v2"
)

# 更新文檔嵌入
document_store.update_embeddings(
    retriever=retriever,
    batch_size=100,
    update_existing_embeddings=False
)
```

### 8.3 構建 RAG Pipeline

```python
# 完整 RAG 管道
from haystack import Pipeline
from haystack.nodes import AnswerParser

# 答案解析器
answer_parser = AnswerParser()

# 組裝管道
rag_pipeline = Pipeline()
rag_pipeline.add_node(
    component=retriever,
    name="Retriever",
    inputs=["Query"]
)
rag_pipeline.add_node(
    component=generator,
    name="Generator",
    inputs=["Retriever"]
)
rag_pipeline.add_node(
    component=answer_parser,
    name="Parser",
    inputs=["Generator"]
)
```

### 8.4 查詢和生成

```python
# 執行查詢
result = rag_pipeline.run(
    query="What are the benefits of RAG?",
    params={
        "Retriever": {
            "top_k": 5,
            "filters": {"category": ["AI"]}
        },
        "Generator": {
            "top_k": 1,
            "temperature": 0.7
        }
    }
)

# 處理結果
print("Answer:", result["answers"][0].answer)
print("Score:", result["answers"][0].score)
print("Context:", result["answers"][0].context)
```

---

## 9. 框架對比

### 9.1 Haystack vs LangChain

| 特性 | Haystack | LangChain |
|-----|----------|-----------|
| **核心定位** | RAG 專注 | 通用 LLM 應用 |
| **架構** | Pipeline DAG | Chain 鏈式 |
| **文檔處理** | 強大 | 中等 |
| **向量檢索** | 優秀 | 良好 |
| **Agent 支持** | 基礎 | 豐富 |
| **生產就緒** | 高 | 中 |
| **學習曲線** | 中等 | 較陡 |

### 9.2 Haystack vs LlamaIndex

| 特性 | Haystack | LlamaIndex |
|-----|----------|------------|
| **核心定位** | 企業 RAG | 數據索引 |
| **索引類型** | 多樣 | 非常豐富 |
| **查詢引擎** | Pipeline | Query Engine |
| **靈活性** | 高 | 高 |
| **性能** | 優秀 | 良好 |
| **部署** | 容易 | 中等 |

### 9.3 選擇建議

**選擇 Haystack 當：**
- 構建生產級 RAG 系統
- 需要企業級搜索功能
- 重視性能和擴展性
- 需要靈活的 Pipeline 設計

**選擇 LangChain 當：**
- 快速原型開發
- 需要豐富的 Agent 功能
- 廣泛的 LLM 集成
- 實驗性項目

**選擇 LlamaIndex 當：**
- 複雜的索引需求
- 多樣化的數據源
- 高級查詢功能
- 數據密集型應用

---

## 10. 最佳實踐

### 10.1 文檔分塊策略

```python
# 根據內容類型選擇分塊策略
preprocessor = PreProcessor(
    split_by="word",           # 按詞分塊
    split_length=200,          # 塊大小
    split_overlap=20,          # 重疊部分
    split_respect_sentence_boundary=True  # 尊重句子邊界
)
```

### 10.2 混合檢索

```python
# 結合稀疏和密集檢索
# BM25 處理精確匹配
# 向量檢索處理語義相似

def hybrid_retrieval(query, top_k=10):
    bm25_results = sparse_retriever.retrieve(query, top_k=top_k)
    dense_results = dense_retriever.retrieve(query, top_k=top_k)

    # 合併和重排序
    combined = join_documents.run(
        documents=[bm25_results, dense_results]
    )
    return combined
```

### 10.3 提示工程

```python
# 結構化提示模板
prompt = """
System: You are a helpful assistant.

Context:
{documents}

Instructions:
- Answer based only on the context
- Be concise and accurate
- Cite sources when possible

Question: {query}
Answer:
"""
```

### 10.4 錯誤處理

```python
try:
    result = pipeline.run(query=user_query)
except Exception as e:
    logger.error(f"Pipeline error: {e}")
    # 降級策略
    result = fallback_pipeline.run(query=user_query)
```

---

## 11. 進階功能

### 11.1 文檔排序

```python
from haystack.nodes import SentenceTransformersRanker

ranker = SentenceTransformersRanker(
    model_name_or_path="cross-encoder/ms-marco-MiniLM-L-6-v2"
)

pipeline.add_node(
    component=ranker,
    name="Ranker",
    inputs=["Retriever"]
)
```

### 11.2 答案評估

```python
from haystack.nodes import EvalAnswers

eval_pipeline = Pipeline()
# ... 添加節點

# 評估答案
metrics = eval_pipeline.eval(
    labels=ground_truth_labels,
    params={"Retriever": {"top_k": 5}}
)

print(f"Recall: {metrics['Retriever']['recall']}")
print(f"F1: {metrics['Reader']['f1']}")
```

### 11.3 REST API 部署

```python
from haystack.utils import launch_ui

# 啟動 REST API
launch_ui(pipeline, server_name="0.0.0.0", server_port=8000)

# 訪問 http://localhost:8000
```

---

## 12. 常見問題

### Q1: 如何選擇 Document Store？

**開發/測試**: InMemoryDocumentStore
**小規模生產**: FAISSDocumentStore
**大規模生產**: ElasticsearchDocumentStore, WeaviateDocumentStore

### Q2: 如何提升檢索質量？

1. 使用混合檢索
2. 調整分塊大小
3. 優化嵌入模型
4. 添加重排序

### Q3: 如何處理多語言？

```python
# 使用多語言模型
retriever = EmbeddingRetriever(
    embedding_model="sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
)
```

### Q4: 如何監控性能？

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 添加性能監控
from haystack.nodes import Monitoring

monitor = Monitoring(pipeline)
metrics = monitor.get_metrics()
```

---

## 參考資源

- [官方文檔](https://haystack.deepset.ai/)
- [GitHub](https://github.com/deepset-ai/haystack)
- [教程](https://haystack.deepset.ai/tutorials)
- [Discord 社區](https://haystack.deepset.ai/community)
- [示例代碼](https://github.com/deepset-ai/haystack-examples)

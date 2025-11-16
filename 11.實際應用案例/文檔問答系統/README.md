# 文檔問答系統

一個基於 RAG（檢索增強生成）技術的企業級文檔問答系統，支持多種文檔格式，提供準確的答案和來源追蹤。

## ✨ 功能特點

- 📄 **多格式支持**: PDF, Word, Excel, TXT, Markdown
- 🔍 **智能檢索**: 語義搜索 + 關鍵詞搜索
- 📊 **來源追蹤**: 顯示答案來源和頁碼
- 💾 **持久化索引**: 索引保存，無需重複構建
- 🎨 **友好界面**: Streamlit Web UI
- ⚡ **快速響應**: 平均 1-2 秒

## 🏗️ 架構

```
用戶問題 → 查詢處理 → 向量檢索 → 上下文構建 → LLM 生成 → 答案返回
                           ↑
                    向量數據庫 (Chroma)
```

## 🚀 快速開始

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 配置環境變數

```bash
cp .env.example .env
```

編輯 `.env` 文件：
```bash
OPENAI_API_KEY=your_openai_api_key
# 或使用 Gemini
GOOGLE_API_KEY=your_google_api_key
```

### 3. 運行程序

```bash
# Web UI 版本
streamlit run app.py

# 命令行版本
python main.py
```

## 📁 文件結構

```
文檔問答系統/
├── README.md           # 本文件
├── requirements.txt    # 依賴列表
├── .env.example       # 環境變數範例
├── app.py             # Streamlit Web 應用
├── main.py            # 命令行應用
├── rag_system.py      # RAG 核心邏輯
├── document_loader.py # 文檔加載器
├── config.yaml        # 配置文件
├── data/              # 文檔目錄
├── vectorstore/       # 向量數據庫
└── examples/          # 使用範例
    └── example_queries.txt
```

## 💻 使用方法

### 方法 1: Web 界面

```bash
streamlit run app.py
```

然後在瀏覽器中：
1. 上傳文檔或選擇已有文檔
2. 點擊「索引文檔」
3. 輸入問題
4. 查看答案和來源

### 方法 2: Python API

```python
from rag_system import DocumentQASystem

# 初始化系統
qa_system = DocumentQASystem()

# 索引文檔
qa_system.index_documents("data/")

# 提問
answer = qa_system.query("公司的休假政策是什麼？")

print(f"答案: {answer['answer']}")
print(f"來源: {answer['sources']}")
```

### 方法 3: 命令行

```bash
# 索引文檔
python main.py --index data/

# 提問
python main.py --query "公司的休假政策是什麼？"

# 互動模式
python main.py --interactive
```

## ⚙️ 配置選項

編輯 `config.yaml`:

```yaml
# LLM 配置
llm:
  provider: openai  # 或 google
  model: gpt-4-turbo
  temperature: 0.3
  max_tokens: 1000

# 嵌入模型
embeddings:
  provider: openai
  model: text-embedding-3-small

# 向量數據庫
vectorstore:
  type: chroma
  persist_directory: ./vectorstore
  collection_name: documents

# 檢索配置
retrieval:
  top_k: 5
  score_threshold: 0.7

# 文檔處理
document_processing:
  chunk_size: 1000
  chunk_overlap: 200
```

## 📊 性能優化

### 1. 選擇合適的分塊大小

```python
# 短文檔（FAQ, 政策文件）
chunk_size = 500

# 長文檔（技術手冊）
chunk_size = 1500

# 代碼文檔
chunk_size = 1000
```

### 2. 調整檢索數量

```python
# 簡單問題
top_k = 3

# 複雜問題
top_k = 7
```

### 3. 使用緩存

```python
from langchain.cache import InMemoryCache
from langchain.globals import set_llm_cache

set_llm_cache(InMemoryCache())
```

## 🎯 實際應用場景

### 1. 企業內部知識庫

```python
# 索引公司文檔
qa_system.index_documents([
    "policies/",      # 政策文件
    "handbooks/",     # 員工手冊
    "procedures/",    # 流程文檔
])

# 員工查詢
qa_system.query("如何申請年假？")
```

### 2. 客戶支持

```python
# 索引產品文檔
qa_system.index_documents([
    "product_manuals/",
    "faq/",
    "troubleshooting/",
])

# 客戶問題
qa_system.query("如何重置密碼？")
```

### 3. 研究助手

```python
# 索引研究論文
qa_system.index_documents([
    "papers/",
    "research_notes/",
])

# 研究問題
qa_system.query("關於這個主題的最新研究有哪些？")
```

## 🔧 進階功能

### 1. 多語言支持

```python
# 配置多語言嵌入
from langchain.embeddings import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="paraphrase-multilingual-MiniLM-L12-v2"
)
```

### 2. 混合檢索

```python
from langchain.retrievers import EnsembleRetriever
from langchain.retrievers import BM25Retriever

# 組合向量檢索和關鍵詞檢索
ensemble_retriever = EnsembleRetriever(
    retrievers=[vector_retriever, bm25_retriever],
    weights=[0.7, 0.3]
)
```

### 3. 重排序

```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

# 使用 LLM 重排序結果
compressor = LLMChainExtractor.from_llm(llm)
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=vector_retriever
)
```

## 📈 評估指標

```python
# 評估系統性能
from evaluation import evaluate_qa_system

metrics = evaluate_qa_system(
    qa_system,
    test_questions="test_set.json"
)

print(f"準確率: {metrics['accuracy']:.2%}")
print(f"平均響應時間: {metrics['avg_response_time']:.2f}s")
print(f"答案相關性: {metrics['relevance_score']:.2f}")
```

## 🐛 故障排除

### 問題 1: 索引速度慢

**解決**:
```python
# 使用批處理
qa_system.batch_size = 50

# 減少嵌入維度
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
```

### 問題 2: 答案不準確

**解決**:
1. 增加 `top_k` 值
2. 調整 `chunk_size`
3. 改進提示詞
4. 使用更強大的 LLM

### 問題 3: 成本過高

**解決**:
```python
# 使用較小的模型
llm = ChatOpenAI(model="gpt-3.5-turbo")

# 減少檢索數量
top_k = 3

# 啟用緩存
set_llm_cache(SQLiteCache(database_path=".cache.db"))
```

## 📚 相關資源

- [LlamaIndex 文檔](https://docs.llamaindex.ai/)
- [RAG 最佳實踐](../../10.框架對比與選擇指南/最佳實踐.md)
- [向量數據庫選擇](https://python.langchain.com/docs/integrations/vectorstores/)

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

---

**最後更新**: 2025-01-14

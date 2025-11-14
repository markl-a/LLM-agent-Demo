# LlamaIndex 學習教程

## 📚 教程概覽

LlamaIndex（原名 GPT Index）是一個強大的數據索引和查詢框架，專注於將你的私有數據與大型語言模型（LLM）連接起來。

### 為什麼選擇 LlamaIndex？

- **簡單易用**: 比 LangChain 更專注於數據索引，學習曲線更平緩
- **強大的數據連接器**: 支持 100+ 種數據源（PDF、數據庫、API 等）
- **靈活的索引結構**: 多種索引類型（向量索引、樹狀索引、關鍵詞索引等）
- **高效的查詢引擎**: 優化的檢索和查詢性能
- **原生 Chat 支持**: 內建聊天引擎，輕鬆構建對話系統

## 🎯 學習路徑

### 1. 快速開始 (0.快速開始.ipynb)
- LlamaIndex 基礎概念
- 安裝和配置
- 第一個索引和查詢
- 基本的 RAG 應用

### 2. 數據加載與索引 (1.數據加載與索引.ipynb)
- 各種數據加載器（SimpleDirectoryReader、DatabaseReader 等）
- 文檔預處理和分塊
- 創建和管理索引
- 向量存儲集成
- 索引持久化

### 3. 查詢引擎 (2.查詢引擎.ipynb)
- 查詢引擎基礎
- 不同類型的查詢引擎
- 查詢轉換和優化
- 自定義檢索器
- 響應合成

### 4. Chat Engine 聊天引擎 (3.Chat_Engine聊天引擎.ipynb)
- 對話上下文管理
- 不同的 Chat 模式
- 記憶和歷史管理
- 構建智能對話系統

## 🔑 核心概念

### 文檔（Documents）
LlamaIndex 中的基本數據單元，可以是文本、PDF、網頁等。

### 節點（Nodes）
文檔被分塊後的單元，包含元數據和關係信息。

### 索引（Index）
組織數據的結構，支持高效檢索。主要類型：
- **VectorStoreIndex**: 向量索引，最常用
- **SummaryIndex**: 摘要索引
- **TreeIndex**: 樹狀索引
- **KeywordTableIndex**: 關鍵詞索引

### 查詢引擎（Query Engine）
用於查詢索引的接口，提供各種查詢策略。

### Chat Engine（聊天引擎）
在查詢引擎基礎上增加對話上下文管理。

## 📊 LlamaIndex vs LangChain

| 特性 | LlamaIndex | LangChain |
|------|-----------|-----------|
| **主要焦點** | 數據索引和檢索 | 通用 LLM 應用開發 |
| **學習曲線** | 較簡單 | 較陡峭 |
| **數據連接器** | 100+ 開箱即用 | 需要更多配置 |
| **索引類型** | 多種專門優化 | 較少 |
| **查詢優化** | 內建多種策略 | 需要手動配置 |
| **適用場景** | RAG、文檔問答、知識庫 | 複雜工作流、Agent |

## 🛠️ 安裝

```bash
# 基礎安裝
pip install llama-index

# 核心組件
pip install llama-index-core

# LLM 集成
pip install llama-index-llms-openai
pip install llama-index-llms-anthropic

# 嵌入模型
pip install llama-index-embeddings-openai
pip install llama-index-embeddings-huggingface

# 向量數據庫
pip install llama-index-vector-stores-chroma
pip install llama-index-vector-stores-pinecone
```

## 🚀 快速示例

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

# 加載文檔
documents = SimpleDirectoryReader("data").load_data()

# 創建索引
index = VectorStoreIndex.from_documents(documents)

# 查詢
query_engine = index.as_query_engine()
response = query_engine.query("你的問題")
print(response)
```

## 📖 教程內容詳細

### 0. 快速開始
- 環境配置
- 基本概念理解
- 第一個 RAG 應用
- 常見問題排查

### 1. 數據加載與索引
- SimpleDirectoryReader 使用
- DatabaseReader 數據庫讀取
- 自定義 Reader
- 文檔分塊策略
- 元數據管理
- 向量存儲選擇
- 索引優化技巧

### 2. 查詢引擎
- VectorStoreQuery 向量查詢
- SubQuestionQueryEngine 子問題分解
- RouterQueryEngine 路由查詢
- RetrieverQueryEngine 自定義檢索
- 查詢轉換技術
- 響應合成模式

### 3. Chat Engine 聊天引擎
- SimpleChatEngine 簡單對話
- CondensePlusContextChatEngine 上下文壓縮
- ReActAgent 對話 Agent
- 對話歷史管理
- 流式響應
- 多輪對話策略

## 🔗 相關資源

- [LlamaIndex 官方文檔](https://docs.llamaindex.ai/)
- [LlamaIndex GitHub](https://github.com/run-llama/llama_index)
- [社區示例](https://github.com/run-llama/llama_index/tree/main/docs/examples)

## 💡 最佳實踐

1. **數據準備**: 確保文檔格式清晰，適當預處理
2. **分塊策略**: 根據內容類型選擇合適的分塊大小
3. **嵌入模型**: 根據語言和場景選擇合適的嵌入模型
4. **索引選擇**: 簡單場景用 VectorStoreIndex，複雜場景可組合多種索引
5. **查詢優化**: 使用查詢轉換和子問題分解提高準確性
6. **成本控制**: 合理使用緩存和批處理

## 🎯 學習建議

1. **順序學習**: 按照教程順序逐步學習
2. **動手實踐**: 每個教程都包含可運行的代碼
3. **修改實驗**: 嘗試修改參數，觀察效果變化
4. **實際應用**: 使用自己的數據進行實驗
5. **對比學習**: 與 LangChain 對比，理解各自優勢

開始你的 LlamaIndex 學習之旅吧！🚀

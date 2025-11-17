# LlamaIndex 完整學習教程

## 📚 教程概覽

LlamaIndex（原名 GPT Index）是一個強大的數據索引和查詢框架，專為將私有數據與大型語言模型（LLM）無縫連接而設計。它是構建生產級 RAG（檢索增強生成）應用的首選框架。

### 🌟 為什麼選擇 LlamaIndex？

- **🎯 專注數據索引**: 比 LangChain 更專注於數據檢索，學習曲線更平緩
- **🔌 強大的數據連接器**: 內建 100+ 種數據源連接器（PDF、Word、資料庫、API、網頁等）
- **📊 靈活的索引結構**: 支援多種索引類型（向量、圖譜、樹狀、關鍵詞等）
- **⚡ 高效的查詢引擎**: 優化的檢索和查詢性能，支援複雜查詢策略
- **💬 原生 Chat 支持**: 內建聊天引擎，輕鬆構建對話系統
- **🤖 Agent 框架**: 完整的 Agent 工具生態系統
- **🎨 多模態支持**: 支援文字、圖片、音訊等多種數據類型
- **🚀 生產就緒**: 企業級功能，包含監控、評估、優化等工具

## 🎯 完整學習路徑

### 📖 基礎入門系列

#### 0. 快速開始 (0.快速開始.ipynb)
**難度**: ⭐ 入門
**時長**: 30 分鐘

- LlamaIndex 核心概念與架構
- 環境安裝和配置（支援多種 LLM）
- 創建第一個索引和查詢
- 基本的 RAG 應用實作
- 常見問題排查

#### 1. 進階索引技術 (1.進階索引技術.ipynb)
**難度**: ⭐⭐ 進階
**時長**: 1 小時

- 多種索引類型詳解（Tree、Keyword、Graph）
- 索引性能優化技巧
- 向量資料庫整合（Chroma、Pinecone、Weaviate）
- 增量更新與索引管理
- 大規模數據索引策略

#### 2. 數據加載與處理 (2.數據加載與處理.ipynb)
**難度**: ⭐⭐ 進階
**時長**: 45 分鐘

- 100+ 種數據加載器使用
- 自定義 Reader 開發
- 文檔分塊策略與最佳實踐
- 元數據提取與管理
- 數據預處理流程

### 🚀 進階應用系列

#### 3. 查詢引擎深入 (3.查詢引擎深入.ipynb)
**難度**: ⭐⭐⭐ 高級
**時長**: 1.5 小時

- 多種查詢引擎類型與應用場景
- 子問題分解（SubQuestion）
- 路由查詢（Router）
- 自定義檢索器開發
- 查詢轉換與優化
- 響應合成模式

#### 4. Chat Engine 聊天引擎 (4.Chat_Engine聊天引擎.ipynb)
**難度**: ⭐⭐ 進階
**時長**: 1 小時

- 對話上下文管理機制
- 多種 Chat 模式（Simple、ReAct、Context）
- 對話記憶與歷史管理
- 流式響應實作
- 構建智能客服系統

#### 5. Agents 與工具使用 (5.Agents與工具使用.ipynb)
**難度**: ⭐⭐⭐ 高級
**時長**: 1.5 小時

- ReAct Agent 原理與實作
- 工具定義與註冊
- 多 Agent 協作
- Function Calling 整合
- Agent 記憶與規劃

### 🎨 特殊主題系列

#### 6. 多模態 RAG (6.多模態RAG.ipynb)
**難度**: ⭐⭐⭐ 高級
**時長**: 2 小時

- 圖片索引與查詢
- 文字 + 圖片混合檢索
- 多模態嵌入模型（CLIP、BLIP）
- PDF 圖表理解
- 音訊轉文字整合

#### 7. 生產環境最佳實踐 (7.生產環境最佳實踐.ipynb)
**難度**: ⭐⭐⭐⭐ 專家
**時長**: 2 小時

- 性能監控與優化
- 成本控制策略
- 快取機制設計
- 錯誤處理與重試
- A/B 測試與評估
- 部署架構設計

### 💼 實戰案例系列

#### 案例1: 企業文檔問答系統 (案例1_企業文檔問答系統.ipynb)
**難度**: ⭐⭐⭐ 高級
**項目時長**: 3-4 小時

- 完整的企業級 RAG 系統
- 多格式文檔處理
- 權限控制與安全
- 答案質量評估
- 生產部署方案

## 🔑 核心概念詳解

### 📄 文檔（Documents）
**定義**: LlamaIndex 中的基本數據單元

**特點**:
- 支援多種格式：文字、PDF、Word、Markdown、HTML 等
- 包含原始內容和元數據（作者、日期、標籤等）
- 可以來自檔案系統、資料庫、API、網頁等

**範例**:
```python
from llama_index.core import Document
doc = Document(text="內容", metadata={"source": "file.pdf", "page": 1})
```

### 🧩 節點（Nodes）
**定義**: 文檔分塊後的基本單元

**特點**:
- 包含文本內容和豐富的元數據
- 維護與其他節點的關係（前後、父子）
- 是索引和檢索的基本單位
- 可自定義分塊策略

**應用場景**:
- 長文檔需要分塊以適應 LLM 上下文限制
- 精確定位信息來源
- 優化檢索粒度

### 📚 索引（Index）
**定義**: 組織數據的結構，支持高效檢索

**主要類型**:

| 索引類型 | 適用場景 | 特點 | 查詢速度 |
|---------|---------|------|---------|
| **VectorStoreIndex** | 語義搜尋、一般問答 | 最常用，支援相似度檢索 | ⚡⚡⚡ |
| **TreeIndex** | 階層性文檔、長文檔摘要 | 自下而上構建摘要樹 | ⚡⚡ |
| **KeywordTableIndex** | 精確關鍵詞匹配 | 快速關鍵詞查找 | ⚡⚡⚡⚡ |
| **KnowledgeGraphIndex** | 實體關係查詢 | 提取三元組，構建知識圖譜 | ⚡⚡ |
| **SummaryIndex** | 摘要性問題 | 掃描所有文檔 | ⚡ |

### 🔍 查詢引擎（Query Engine）
**定義**: 用於查詢索引的高級接口

**功能**:
- 將自然語言問題轉換為檢索查詢
- 執行檢索並排序結果
- 合成最終回答

**高級特性**:
- 子問題分解（複雜問題拆解）
- 查詢轉換（改寫、擴展）
- 多路由選擇（選擇最佳索引）
- 自定義後處理

### 💬 聊天引擎（Chat Engine）
**定義**: 在查詢引擎基礎上增加對話上下文管理

**模式**:
- **Simple**: 簡單對話，無上下文
- **Condense**: 壓縮歷史為單一查詢
- **Context**: 完整保留對話上下文
- **ReAct**: Agent 模式，可使用工具

**應用**:
- 多輪對話系統
- 智能客服
- 個人助理

### 🤖 Agents（代理）
**定義**: 能夠使用工具並進行多步推理的智能體

**能力**:
- 分解複雜任務
- 選擇並使用合適的工具
- 動態規劃執行步驟
- 錯誤處理與重試

## 📊 LlamaIndex vs LangChain 詳細對比

| 特性 | LlamaIndex | LangChain | 推薦場景 |
|------|-----------|-----------|---------|
| **主要焦點** | 數據索引和檢索 | 通用 LLM 應用開發 | 選 LlamaIndex for RAG |
| **學習曲線** | ⭐⭐ 較簡單 | ⭐⭐⭐⭐ 較陡峭 | 新手首選 LlamaIndex |
| **數據連接器** | 100+ 開箱即用 | 需要更多配置 | LlamaIndex 勝 |
| **索引類型** | 5+ 種專門優化 | 基礎向量檢索 | LlamaIndex 更豐富 |
| **查詢優化** | 內建多種策略 | 需要手動配置 | LlamaIndex 開箱即用 |
| **Agent 支持** | ReAct Agent | 完整 Agent 框架 | LangChain 更強大 |
| **文檔質量** | ⭐⭐⭐⭐ 優秀 | ⭐⭐⭐ 良好 | LlamaIndex 文檔更清晰 |
| **社群規模** | 中等 | 大型 | LangChain 社群更活躍 |
| **適用場景** | RAG、文檔問答、知識庫 | 複雜工作流、多 Agent | 各有所長 |
| **性能** | 檢索優化更好 | 通用性更強 | 依場景而定 |

**選擇建議**:
- 🎯 **選 LlamaIndex**: 文檔問答、知識庫、RAG 系統、需要快速原型
- 🎯 **選 LangChain**: 複雜工作流、多 Agent 協作、需要高度客製化
- 🎯 **兩者結合**: 可以在同一專案中結合使用各自優勢

## 🛠️ 完整安裝指南

### 基礎安裝

```bash
# 一鍵安裝完整套件（推薦新手）
pip install llama-index

# 或者分別安裝核心組件
pip install llama-index-core
```

### LLM 提供商整合

```bash
# OpenAI (GPT-3.5, GPT-4)
pip install llama-index-llms-openai

# Anthropic (Claude)
pip install llama-index-llms-anthropic

# Google (Gemini)
pip install llama-index-llms-gemini

# Azure OpenAI
pip install llama-index-llms-azure-openai

# 本地模型 (Ollama, LM Studio)
pip install llama-index-llms-ollama

# HuggingFace 模型
pip install llama-index-llms-huggingface
```

### 嵌入模型

```bash
# OpenAI Embeddings
pip install llama-index-embeddings-openai

# HuggingFace Embeddings
pip install llama-index-embeddings-huggingface

# Cohere Embeddings
pip install llama-index-embeddings-cohere

# 本地嵌入模型
pip install sentence-transformers
```

### 向量資料庫

```bash
# Chroma (本地輕量級)
pip install llama-index-vector-stores-chroma

# Pinecone (雲端託管)
pip install llama-index-vector-stores-pinecone

# Weaviate
pip install llama-index-vector-stores-weaviate

# Qdrant
pip install llama-index-vector-stores-qdrant

# Milvus
pip install llama-index-vector-stores-milvus
```

### 數據加載器

```bash
# 文檔處理
pip install pypdf  # PDF
pip install docx2txt  # Word
pip install python-pptx  # PowerPoint

# 資料庫連接器
pip install llama-index-readers-database

# 網頁爬取
pip install llama-index-readers-web

# API 整合
pip install llama-index-readers-notion  # Notion
pip install llama-index-readers-slack  # Slack
pip install llama-index-readers-github  # GitHub
```

### 完整開發環境

```bash
# 創建虛擬環境
python -m venv llamaindex-env
source llamaindex-env/bin/activate  # Linux/Mac
# llamaindex-env\Scripts\activate  # Windows

# 安裝完整套件
pip install llama-index
pip install llama-index-llms-openai llama-index-llms-anthropic
pip install llama-index-embeddings-openai
pip install llama-index-vector-stores-chroma
pip install pypdf docx2txt python-dotenv

# 驗證安裝
python -c "import llama_index; print(llama_index.__version__)"
```

## 🚀 快速示例

### 最簡單的 RAG 應用

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
import os

# 設置 API Key
os.environ["OPENAI_API_KEY"] = "your-api-key"

# 加載文檔
documents = SimpleDirectoryReader("data").load_data()

# 創建索引
index = VectorStoreIndex.from_documents(documents)

# 查詢
query_engine = index.as_query_engine()
response = query_engine.query("你的問題")
print(response)
```

### 進階：使用不同 LLM

```python
from llama_index.core import VectorStoreIndex, Settings
from llama_index.llms.anthropic import Anthropic
from llama_index.embeddings.openai import OpenAIEmbedding

# 配置全局設置
Settings.llm = Anthropic(model="claude-3-sonnet-20240229")
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-large")

# 創建索引（會自動使用上面的設置）
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()
```

### 進階：持久化索引

```python
from llama_index.core import StorageContext, load_index_from_storage

# 首次創建並保存
index = VectorStoreIndex.from_documents(documents)
index.storage_context.persist(persist_dir="./storage")

# 後續直接加載
storage_context = StorageContext.from_defaults(persist_dir="./storage")
index = load_index_from_storage(storage_context)
```

## 🔗 學習資源

### 官方資源
- 📖 [LlamaIndex 官方文檔](https://docs.llamaindex.ai/) - 最權威的學習資料
- 💻 [GitHub 倉庫](https://github.com/run-llama/llama_index) - 源碼和範例
- 📚 [官方範例集](https://github.com/run-llama/llama_index/tree/main/docs/examples) - 100+ 實用範例
- 🎥 [官方 YouTube 頻道](https://www.youtube.com/@LlamaIndex) - 影片教學

### 社群資源
- 💬 [Discord 社群](https://discord.gg/dGcwcsnxhU) - 問題討論和交流
- 🐦 [Twitter](https://twitter.com/llama_index) - 最新動態
- 📝 [官方部落格](https://blog.llamaindex.ai/) - 深度文章

### 擴充學習
- 🔧 [LlamaHub](https://llamahub.ai/) - 數據加載器和工具市場
- 🧪 [LlamaLab](https://github.com/run-llama/llama-lab) - 實驗性專案
- 📊 [RAGAs](https://github.com/explodinggradients/ragas) - RAG 評估框架

## 💡 生產環境最佳實踐

### 數據準備
- ✅ 清理和標準化文檔格式
- ✅ 移除敏感資訊
- ✅ 添加豐富的元數據（來源、日期、標籤）
- ✅ 設計合理的文檔結構

### 分塊策略
- ✅ 根據內容類型選擇分塊大小
  - 一般文檔：512-1024 tokens
  - 程式碼：256-512 tokens
  - 長文檔：1024-2048 tokens
- ✅ 設置適當的 overlap（10-20%）
- ✅ 保持語義完整性（句子、段落邊界）

### 模型選擇
- ✅ **嵌入模型**：
  - 英文：`text-embedding-3-large`
  - 中文：`text-embedding-3-large` 或多語言模型
  - 成本考量：`text-embedding-3-small`
- ✅ **LLM**：
  - 高質量：GPT-4, Claude 3.5 Sonnet
  - 平衡：GPT-3.5 Turbo, Claude 3 Haiku
  - 本地：Ollama (Llama 3, Mistral)

### 索引策略
- ✅ 簡單場景：VectorStoreIndex
- ✅ 需要精確匹配：組合 Keyword + Vector
- ✅ 關係查詢：KnowledgeGraphIndex
- ✅ 大規模數據：使用專業向量資料庫（Pinecone, Weaviate）

### 查詢優化
- ✅ 使用查詢轉換改寫問題
- ✅ 複雜問題使用子問題分解
- ✅ 實現查詢結果快取
- ✅ 設置合理的 top_k（3-10）
- ✅ 使用混合檢索（Hybrid Search）

### 成本控制
- ✅ 實現嵌入快取避免重複計算
- ✅ 批次處理文檔
- ✅ 選擇性使用昂貴的 LLM
- ✅ 監控 API 使用量
- ✅ 考慮本地嵌入模型

### 監控與評估
- ✅ 記錄查詢延遲
- ✅ 追蹤答案質量
- ✅ 監控檢索準確率
- ✅ 收集使用者回饋
- ✅ 定期評估和改進

## 🎯 學習建議

### 🌱 初學者（0-2 週）
1. ✅ 完成「快速開始」教程
2. ✅ 理解核心概念（Document、Node、Index）
3. ✅ 動手建立第一個簡單的 RAG 應用
4. ✅ 實驗不同的查詢方式
5. ✅ 閱讀官方文檔的基礎部分

### 🚀 進階學習（2-4 週）
1. ✅ 學習多種索引類型和應用場景
2. ✅ 掌握數據加載和預處理技巧
3. ✅ 深入理解查詢引擎和檢索器
4. ✅ 建立聊天引擎應用
5. ✅ 整合向量資料庫

### 🎓 高級應用（4-8 週）
1. ✅ 學習 Agent 和工具使用
2. ✅ 實作多模態 RAG
3. ✅ 優化性能和成本
4. ✅ 建立生產級應用
5. ✅ 貢獻開源專案

### 📚 學習方法
- **動手實踐**: 每個概念都要親自寫程式碼驗證
- **修改實驗**: 嘗試修改參數，觀察效果變化
- **使用真實數據**: 用自己的文檔進行實驗
- **對比學習**: 與 LangChain 對比，理解各自優勢
- **參與社群**: 在 Discord 提問和分享經驗
- **閱讀原始碼**: 深入理解內部實作

## 🆘 常見問題

### Q: LlamaIndex 免費嗎？
A: LlamaIndex 本身是開源免費的，但使用 OpenAI、Anthropic 等 LLM 服務需要付費。可以使用本地模型（Ollama）來避免費用。

### Q: 需要什麼基礎知識？
A: 需要 Python 基礎，了解 LLM 基本概念。不需要深度學習背景。

### Q: 適合什麼樣的專案？
A: 文檔問答、知識庫、客服系統、內容檢索、程式碼助手等需要 RAG 的場景。

### Q: 資料安全嗎？
A: 如果使用 OpenAI 等雲端服務，資料會傳送到第三方。可以使用本地 LLM 和向量資料庫保證資料隱私。

### Q: 支援中文嗎？
A: 完全支援！使用支援多語言的嵌入模型（如 OpenAI text-embedding-3）即可。

## 📊 學習進度追蹤

- [ ] 完成快速開始教程
- [ ] 理解核心概念
- [ ] 建立第一個 RAG 應用
- [ ] 學會使用不同索引類型
- [ ] 掌握數據加載和處理
- [ ] 深入理解查詢引擎
- [ ] 建立聊天引擎
- [ ] 學會使用 Agents
- [ ] 實作多模態 RAG
- [ ] 完成實戰案例
- [ ] 部署生產環境應用

---

**準備好了嗎？開始你的 LlamaIndex 學習之旅吧！🚀**

有任何問題歡迎在 [Issues](https://github.com/markl-a/LLM-agent-Demo/issues) 提出，或加入 [Discord 社群](https://discord.gg/dGcwcsnxhU)討論！

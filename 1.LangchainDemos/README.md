# LangChain 深度學習與實戰指南

## 目錄
- [專案簡介](#專案簡介)
- [學習路徑](#學習路徑)
- [技術棧說明](#技術棧說明)
- [環境準備](#環境準備)
- [教程列表](#教程列表)
- [進階應用](#進階應用)
- [最佳實踐](#最佳實踐)
- [常見問題](#常見問題)
- [參考資源](#參考資源)

## 專案簡介

本專案是一個全面的 LangChain 學習與實戰教程集合，從基礎概念到進階應用，涵蓋了構建 LLM 應用所需的核心技術。每個教程都包含詳細的中文說明和實際可運行的程式碼範例。

### 適合對象

- 想要學習如何構建 LLM 應用的開發者
- 對 RAG (Retrieval-Augmented Generation) 技術感興趣的研究者
- 希望深入了解 Agent 系統設計的工程師
- 需要實現企業級 AI 應用的開發團隊

### 學習成果

完成本教程後，你將能夠：

- 理解 LangChain 的核心概念與架構
- 實作各種類型的 RAG 系統
- 構建具有工具調用能力的 Agent
- 設計複雜的多步驟 LLM 工作流
- 將 LLM 應用部署到生產環境

## 學習路徑

### 第一階段：基礎入門 (1-3天)

建議學習順序：
1. **0. 簡單的RAG_範例.ipynb** - 快速了解 RAG 的基本概念
2. **1. RAG問答** - 深入學習 RAG 的完整流程
3. **2. 向量儲存與檢索器** - 理解向量化與相似度搜尋

**目標**：掌握 LangChain 基礎和 RAG 核心原理

### 第二階段：核心技術 (3-5天)

建議學習順序：
1. **3. 使用_LCEL_建立簡單的_LLM_應用** - 學習 LangChain Expression Language
2. **4. 建構一個聊天機器人** - 實作對話系統
3. **6. code_understanding_ipynb繁中翻譯** - 理解程式碼分析應用

**目標**：熟練使用 LCEL 構建各類 LLM 應用

### 第三階段：進階應用 (5-7天)

建議學習順序：
1. **5. 使用langgraph建立Agent** - 掌握 Agent 架構
2. **9. sql_agent_中文化** - 實作資料庫查詢 Agent
3. **7. 結合_RAG_與自我修正的程式碼生成** - 進階 RAG 技術

**目標**：能夠設計和實現複雜的 Agent 系統

### 第四階段：專業領域 (依需求)

1. **8. LongWriter_粗略了解** - 長文本生成技術
2. **yt_email_reply_llama3_crewai_groq.ipynb** - 實際業務場景應用

**目標**：根據實際需求選擇性學習專業領域技術

## 技術棧說明

### 核心框架

- **LangChain**: LLM 應用開發框架
- **LangGraph**: 構建狀態機和工作流
- **LangSmith**: 追蹤和評估 LLM 應用

### 向量資料庫

- **Chroma**: 輕量級向量資料庫
- **FAISS**: 高效相似度搜尋
- **Pinecone**: 雲端向量資料庫（選用）

### LLM 提供者

- **OpenAI**: GPT-3.5/GPT-4
- **Anthropic**: Claude 系列
- **HuggingFace**: 開源模型支援
- **Groq**: 高速推理引擎

### 輔助工具

- **Sentence Transformers**: 文本向量化
- **Tavily**: 網路搜尋工具
- **SQLite**: 資料庫範例

## 環境準備

### 1. 安裝依賴

```bash
# 基礎環境
pip install langchain langchain-community langchain-core

# 向量資料庫
pip install chromadb sentence-transformers

# LLM 提供者
pip install langchain-openai langchain-anthropic langchain-huggingface

# LangGraph 和工具
pip install langgraph tavily-python

# 輔助套件
pip install python-dotenv jupyter notebook
```

或使用專案提供的 requirements.txt：

```bash
pip install -r requirements.txt
```

### 2. 設定 API Keys

創建 `.env` 文件並設定以下環境變數：

```bash
# OpenAI
OPENAI_API_KEY=your_openai_key_here

# LangSmith (用於追蹤)
LANGCHAIN_API_KEY=your_langsmith_key_here
LANGCHAIN_TRACING_V2=true

# Tavily (用於網路搜尋)
TAVILY_API_KEY=your_tavily_key_here

# HuggingFace (選用)
HUGGINGFACE_TOKEN=your_huggingface_token_here
```

### 3. 驗證安裝

```python
import langchain
from langchain_openai import ChatOpenAI

print(f"LangChain 版本: {langchain.__version__}")

# 測試 LLM 連接
llm = ChatOpenAI()
response = llm.invoke("Hello!")
print(response.content)
```

## 教程列表

### 基礎教程

#### 0. 簡單的RAG_範例.ipynb

**難度**: ⭐
**時間**: 30分鐘
**前置知識**: Python 基礎

**內容概要**:
- RAG 的基本概念
- 使用 Chroma 建立向量資料庫
- 實現簡單的問答系統
- 理解 Embedding 和檢索流程

**學習重點**:
```python
# 核心流程
docs → Embedding → VectorStore → Retriever → LLM → Answer
```

#### 1. RAG問答 (langchain官網使用範例)

**難度**: ⭐⭐
**時間**: 1-2小時
**前置知識**: 完成教程 0

**內容概要**:
- 完整的 RAG 實現流程
- 文檔索引與檢索策略
- 提示工程最佳實踐
- 效能優化技巧

**學習重點**:
- 文檔分割策略 (RecursiveCharacterTextSplitter)
- 檢索器配置 (top_k, similarity_threshold)
- Prompt Template 設計

#### 2. 向量儲存與檢索器

**難度**: ⭐⭐
**時間**: 1-2小時
**前置知識**: 完成教程 0, 1

**內容概要**:
- 深入理解向量嵌入原理
- 多種向量資料庫比較 (Chroma vs FAISS vs Pinecone)
- 進階檢索策略
- 混合搜尋技術

**學習重點**:
- Embedding Models 選擇
- 相似度計算方法 (cosine, euclidean, dot product)
- Multi-query Retriever
- Contextual Compression

#### 3. 使用_LCEL_建立簡單的_LLM_應用

**難度**: ⭐⭐
**時間**: 1-2小時
**前置知識**: 完成教程 0-2

**內容概要**:
- LangChain Expression Language (LCEL) 詳解
- 鏈式組合 (Chain Composition)
- 使用 HuggingFace 開源模型
- Prompt Template 進階應用

**學習重點**:
```python
# LCEL 範例
chain = prompt_template | llm | output_parser
result = chain.invoke({"input": "..."})
```

- Runnable 接口
- 串流輸出 (Streaming)
- 錯誤處理與重試

#### 4. 建構一個聊天機器人

**難度**: ⭐⭐⭐
**時間**: 2-3小時
**前置知識**: 完成教程 0-3

**內容概要**:
- 對話記憶管理 (Conversation Memory)
- 多輪對話系統設計
- 上下文維護策略
- 對話流控制

**學習重點**:
- ConversationBufferMemory
- ConversationSummaryMemory
- Message History 管理
- Session 狀態追蹤

### 進階教程

#### 5. 使用langgraph建立Agent

**難度**: ⭐⭐⭐⭐
**時間**: 3-4小時
**前置知識**: 完成教程 0-4

**內容概要**:
- LangGraph 核心概念
- Agent 架構設計
- 工具調用 (Tool Calling)
- 狀態圖與工作流

**學習重點**:
```python
# Agent 工作流程
State → Agent → Tool Selection → Tool Execution → State Update
```

- ReAct Pattern
- Tool Definition
- Memory Integration
- Streaming Events

#### 6. code_understanding_ipynb繁中翻譯

**難度**: ⭐⭐⭐
**時間**: 2-3小時
**前置知識**: 完成教程 0-5

**內容概要**:
- 程式碼理解與分析
- AST (抽象語法樹) 解析
- 程式碼問答系統
- 文檔自動生成

**學習重點**:
- Code Splitting 策略
- 程式碼向量化
- 跨文件引用處理

#### 7. 結合_RAG_與自我修正的程式碼生成

**難度**: ⭐⭐⭐⭐⭐
**時間**: 4-5小時
**前置知識**: 完成教程 0-6

**內容概要**:
- 進階 RAG 技術
- 自我修正機制 (Self-Correction)
- 程式碼生成與驗證
- 迭代優化流程

**學習重點**:
```python
# 自我修正循環
Generate Code → Test → Fix Errors → Verify → Return
```

- Code Execution Sandbox
- Error Analysis
- Reflection Pattern
- Multi-step Reasoning

#### 8. LongWriter_粗略了解

**難度**: ⭐⭐⭐
**時間**: 1-2小時
**前置知識**: RAG 基礎

**內容概要**:
- 長文本生成技術
- 內容一致性維護
- 大綱規劃策略

**學習重點**:
- Long Context Handling
- Hierarchical Generation
- Content Coherence

#### 9. sql_agent_中文化

**難度**: ⭐⭐⭐⭐
**時間**: 3-4小時
**前置知識**: 完成教程 5

**內容概要**:
- SQL Agent 完整實現
- 資料庫查詢自動化
- 錯誤處理與重試
- 安全性考量

**學習重點**:
```python
# SQL Agent 工作流程
Question → List Tables → Get Schema → Generate SQL →
Check Query → Execute → Format Answer
```

- Dynamic Tool Selection
- SQL Injection Prevention
- Query Validation
- Result Formatting

### 特殊應用

#### yt_email_reply_llama3_crewai_groq.ipynb

**難度**: ⭐⭐⭐⭐
**時間**: 3-4小時
**前置知識**: Agent 基礎

**內容概要**:
- CrewAI 多 Agent 協作
- Llama3 模型應用
- Groq 高速推理
- YouTube 內容分析
- 郵件自動回覆

**學習重點**:
- Multi-Agent Collaboration
- Task Delegation
- Agent Communication
- Real-world Integration

## 進階應用

### 實際業務場景

本節包含完整的實際應用案例，展示如何將 LangChain 技術應用於真實業務場景：

1. **智能客服系統** - 結合 RAG 和 Agent 的完整客服解決方案
2. **文檔分析助手** - 企業知識庫問答系統
3. **代碼審查助手** - 自動化代碼審查和建議
4. **數據分析 Agent** - 自然語言查詢資料庫

詳見 `advanced_examples/` 目錄。

## 最佳實踐

### 1. Prompt Engineering

```python
# 好的 Prompt 設計
system_prompt = """
你是一個專業的助手，請遵循以下原則：
1. 準確性：基於提供的上下文回答
2. 簡潔性：避免冗長的回答
3. 誠實性：不確定時明確說明

上下文：
{context}

問題：{question}
"""
```

### 2. 錯誤處理

```python
from langchain.callbacks import get_openai_callback

try:
    with get_openai_callback() as cb:
        response = chain.invoke({"input": query})
        print(f"Token 使用: {cb.total_tokens}")
except Exception as e:
    logger.error(f"錯誤: {e}")
    # 降級處理
```

### 3. 效能優化

- 使用快取減少重複調用
- 批次處理提高效率
- 選擇合適的 Embedding 模型
- 優化文檔分割策略

### 4. 安全性考量

- API Key 管理（使用環境變數）
- 輸入驗證與過濾
- 輸出內容審查
- Rate Limiting

## 常見問題

### Q1: 如何選擇合適的 Embedding 模型？

**A**: 根據場景選擇：
- 中文優先：`text-embedding-ada-002` 或 `bge-large-zh`
- 多語言：`multilingual-e5-large`
- 效能優先：`all-MiniLM-L6-v2`
- 精度優先：`text-embedding-3-large`

### Q2: RAG 檢索效果不好怎麼辦？

**A**: 優化策略：
1. 調整文檔分割大小 (chunk_size)
2. 增加重疊部分 (chunk_overlap)
3. 使用混合搜尋 (Hybrid Search)
4. 實施重排序 (Re-ranking)
5. 優化 Prompt Template

### Q3: Agent 調用工具時出錯？

**A**: 檢查清單：
- 工具定義是否清晰（名稱、描述、參數）
- 是否正確綁定工具到模型
- 檢查模型是否支援 function calling
- 查看錯誤日誌和 LangSmith 追蹤

### Q4: 如何降低 API 成本？

**A**: 節省成本的方法：
- 使用更小的模型（如 GPT-3.5 vs GPT-4）
- 實施快取機制
- 優化 Prompt 長度
- 使用開源模型（HuggingFace）
- 批次處理請求

### Q5: 生產環境部署建議？

**A**: 關鍵考量：
- 使用 LangServe 提供 API 服務
- 實施 Rate Limiting 和請求驗證
- 設置完善的日誌和監控
- 使用向量資料庫持久化
- 實施錯誤重試和降級策略

## 參考資源

### 官方文檔

- [LangChain 官方文檔](https://python.langchain.com/)
- [LangGraph 文檔](https://langchain-ai.github.io/langgraph/)
- [LangSmith 文檔](https://docs.smith.langchain.com/)

### 推薦閱讀

- [RAG 技術深度解析](https://blog.langchain.dev/)
- [Agent 設計模式](https://arxiv.org/abs/2308.08155)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)

### 社群資源

- [LangChain Discord](https://discord.gg/langchain)
- [LangChain GitHub](https://github.com/langchain-ai/langchain)
- [LangChain 中文社群](https://github.com/liaokongVFX/LangChain-Chinese-Getting-Started-Guide)

### 相關工具

- [OpenAI Playground](https://platform.openai.com/playground)
- [HuggingFace Models](https://huggingface.co/models)
- [Chroma Documentation](https://docs.trychroma.com/)

---

## 貢獻指南

歡迎提交 Issue 和 Pull Request！

### 如何貢獻

1. Fork 本專案
2. 創建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 授權

本專案採用 MIT 授權 - 詳見 LICENSE 文件

## 聯絡方式

如有問題或建議，請開 Issue 或聯繫維護者。

---

**最後更新**: 2025-11
**維護狀態**: 積極維護中 ✅

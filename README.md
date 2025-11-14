# 🤖 LLM Agent 與 RAG 完整實戰指南

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3.0+-green.svg)](https://python.langchain.com/)
[![LlamaIndex](https://img.shields.io/badge/LlamaIndex-0.11.0+-orange.svg)](https://www.llamaindex.ai/)

> 一個全面的 LLM Agent 框架學習與實踐專案，涵蓋 LangChain、LlamaIndex、AutoGen、CrewAI 等主流框架，以及 RAG、多模態處理、程式碼解析等實際應用。

![Cover](cover.png)

## 📚 目錄

- [專案簡介](#-專案簡介)
- [特色功能](#-特色功能)
- [目錄結構](#-目錄結構)
- [快速開始](#-快速開始)
- [學習路徑](#-學習路徑)
- [框架對比](#-框架對比)
- [實際應用案例](#-實際應用案例)
- [貢獻指南](#-貢獻指南)
- [授權](#-授權)

## 🎯 專案簡介

本專案是一個全面的 LLM Agent 和 RAG（Retrieval-Augmented Generation）學習資源庫，旨在幫助開發者：

- **深入理解**多個主流 LLM Agent 框架的原理和使用
- **掌握 RAG** 技術的各種實現方式
- **學習多模態** LLM 應用開發
- **分析開源專案**的內部運作機制
- **實踐真實場景**的 AI Agent 應用

### 支持的框架和技術

| 框架/技術 | 版本 | 完成度 | 說明 |
|----------|------|--------|------|
| **LangChain** | 0.3.0+ | ✅ 完整 | 11個詳細教程，涵蓋RAG、Agent、LCEL等 |
| **LangGraph** | 0.2.30+ | ✅ 完整 | 狀態圖Agent構建框架 |
| **LlamaIndex** | 0.11.0+ | 🆕 新增 | 數據索引和查詢框架 |
| **AutoGen** | 0.2.0+ | 🆕 新增 | 微軟多Agent對話框架 |
| **CrewAI** | 0.80.0+ | 🆕 新增 | 角色扮演型多Agent框架 |
| **MetaGPT** | Latest | 🆕 新增 | 軟體公司模擬框架 |
| **RAG技術** | - | ✅ 完整 | 基礎RAG、多模態RAG、進階檢索 |
| **向量數據庫** | - | ✅ 完整 | Chroma, FAISS, Pinecone, Qdrant |

## ✨ 特色功能

### 1. 完整的學習路徑
- 📖 從基礎到進階的系統化教程
- 💡 豐富的程式碼範例和詳細註解
- 🎓 實際專案案例學習

### 2. 多框架對比
- 🔍 深入分析各框架優缺點
- 📊 提供選擇指南和對比表
- 🛠️ 實踐中的最佳實踐

### 3. 開源專案解析
- 🔬 深入分析 Open Hands、UFO、PCAgent 等專案
- 📐 詳細的架構圖和流程圖
- 💻 原始碼解讀和實現原理

### 4. 實際應用案例
- 📧 郵件自動回覆系統
- 🗣️ 智能聊天機器人
- 🔍 SQL查詢Agent
- 📊 銷售外聯自動化

## 📂 目錄結構

```
LLM-agent-Demo/
│
├── 1.LangchainDemos/              # LangChain 學習教程
│   ├── 0.簡單的RAG_範例.ipynb
│   ├── 1.langchain官網使用範例：RAG問答/
│   ├── 2.向量儲存與檢索器.ipynb
│   ├── 3.使用_LCEL_建立簡單的_LLM_應用.ipynb
│   ├── 4.建構一個聊天機器人.ipynb
│   ├── 5.使用langgraph建立Agent.ipynb
│   ├── 6.code_understanding_ipynb繁中翻譯.ipynb
│   ├── 7.結合_RAG_與自我修正的程式碼生成.ipynb
│   ├── 8.LongWriter_粗略了解.md
│   └── 9.sql_agent_中文化.ipynb
│
├── 2.Multi_modal_RAG/             # 多模態 RAG 教程
│   ├── langchain_cookbook_Multi_modal_RAG.ipynb
│   └── cj/                        # 範例資料
│
├── 3.程式碼解析/                   # 開源專案程式碼分析
│   ├── 1-open_hands_程式碼解析.md
│   ├── 2-open-hands-docker交互流程.md
│   ├── Cline.md                   # 🆕 新增
│   ├── PCAgent架構流程.md
│   ├── RDAgent.md
│   ├── RDAgent-通用模型.md
│   ├── UFO.md
│   └── OepnAdapt.md
│
├── 4.RPA_LLM/                     # RPA與LLM結合調研
│   └── survey.md
│
├── 5.demo-sales-outreach-automation-langgraph/  # 銷售自動化案例
│   ├── README.md
│   └── setup_script.py
│
├── 6.LlamaIndex/                  # 🆕 LlamaIndex 教程
│   ├── 0.快速開始.ipynb
│   ├── 1.數據加載與索引.ipynb
│   ├── 2.查詢引擎.ipynb
│   ├── 3.Chat_Engine聊天引擎.ipynb
│   └── README.md
│
├── 7.AutoGen/                     # 🆕 AutoGen 教程
│   ├── 0.基礎對話.ipynb
│   ├── 1.多Agent協作.ipynb
│   ├── 2.程式碼執行Agent.ipynb
│   └── README.md
│
├── 8.CrewAI/                      # 🆕 CrewAI 教程
│   ├── 0.快速開始.ipynb
│   ├── 1.角色和任務.ipynb
│   ├── 2.實際案例.ipynb
│   └── README.md
│
├── 9.MetaGPT/                     # 🆕 MetaGPT 教程
│   ├── 0.基礎概念.ipynb
│   ├── 1.軟體開發流程.ipynb
│   └── README.md
│
├── 10.框架對比與選擇指南/          # 🆕 框架對比
│   ├── 框架對比表.md
│   ├── 選擇指南.md
│   └── 最佳實踐.md
│
├── 11.實際應用案例/                # 🆕 更多應用案例
│   ├── 客服機器人/
│   ├── 文檔問答系統/
│   ├── 智能搜索引擎/
│   └── 程式碼助手/
│
├── requirements.txt               # 專案依賴
├── .gitignore                     # Git 忽略規則
├── Dockerfile                     # 🆕 Docker 支持
├── docker-compose.yml             # 🆕 容器編排
├── LICENSE                        # MIT 授權
└── README.md                      # 本文件
```

## 🚀 快速開始

### 環境需求

- Python 3.9 或更高版本
- pip 或 conda 包管理器
- （可選）Docker 和 Docker Compose

### 安裝步驟

#### 方法 1: 使用虛擬環境（推薦）

```bash
# 1. 克隆專案
git clone https://github.com/yourusername/LLM-agent-Demo.git
cd LLM-agent-Demo

# 2. 創建虛擬環境
python -m venv venv

# 3. 啟動虛擬環境
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 4. 安裝依賴
pip install -r requirements.txt

# 5. 配置環境變數
cp .env.example .env
# 編輯 .env 文件，添加你的 API Keys
```

#### 方法 2: 使用 Docker（推薦用於生產環境）

```bash
# 1. 克隆專案
git clone https://github.com/yourusername/LLM-agent-Demo.git
cd LLM-agent-Demo

# 2. 使用 Docker Compose 啟動
docker-compose up -d

# 3. 訪問 Jupyter Lab
# 在瀏覽器中打開 http://localhost:8888
```

### API Keys 配置

創建 `.env` 文件並添加以下內容：

```bash
# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Google Gemini
GOOGLE_API_KEY=your_google_api_key

# Anthropic Claude
ANTHROPIC_API_KEY=your_anthropic_api_key

# Groq
GROQ_API_KEY=your_groq_api_key

# 向量數據庫（可選）
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_environment

# 其他服務（可選）
SERPER_API_KEY=your_serper_api_key
```

### 運行範例

```bash
# 啟動 Jupyter Lab
jupyter lab

# 或啟動 Jupyter Notebook
jupyter notebook

# 然後打開任何 .ipynb 文件開始學習
```

## 🎓 學習路徑

### 初學者路徑（第 1-2 週）

1. **LangChain 基礎**
   - `1.LangchainDemos/0.簡單的RAG_範例.ipynb`
   - `1.LangchainDemos/2.向量儲存與檢索器.ipynb`
   - `1.LangchainDemos/3.使用_LCEL_建立簡單的_LLM_應用.ipynb`

2. **RAG 技術**
   - `1.LangchainDemos/1.langchain官網使用範例：RAG問答/`

3. **基礎 Agent**
   - `1.LangchainDemos/4.建構一個聊天機器人.ipynb`

### 中級路徑（第 3-4 週）

1. **LangGraph Agent**
   - `1.LangchainDemos/5.使用langgraph建立Agent.ipynb`

2. **多模態 RAG**
   - `2.Multi_modal_RAG/langchain_cookbook_Multi_modal_RAG.ipynb`

3. **LlamaIndex**
   - `6.LlamaIndex/` 目錄下所有教程

4. **實際應用**
   - `1.LangchainDemos/9.sql_agent_中文化.ipynb`
   - `1.LangchainDemos/7.結合_RAG_與自我修正的程式碼生成.ipynb`

### 進階路徑（第 5-6 週）

1. **多 Agent 系統**
   - `7.AutoGen/` 目錄下所有教程
   - `8.CrewAI/` 目錄下所有教程
   - `9.MetaGPT/` 目錄下所有教程

2. **程式碼解析**
   - `3.程式碼解析/` 目錄下所有文件
   - 理解開源專案的架構和實現

3. **實際專案**
   - `5.demo-sales-outreach-automation-langgraph/`
   - `11.實際應用案例/` 各個子目錄

## 🔍 框架對比

詳細對比請查看 `10.框架對比與選擇指南/框架對比表.md`

### 快速對比

| 框架 | 適用場景 | 複雜度 | 社區支持 | 學習曲線 |
|------|---------|--------|---------|---------|
| **LangChain** | 通用 LLM 應用 | 中 | ⭐⭐⭐⭐⭐ | 中等 |
| **LlamaIndex** | 數據索引和查詢 | 低-中 | ⭐⭐⭐⭐ | 較低 |
| **AutoGen** | 多 Agent 對話 | 中-高 | ⭐⭐⭐⭐ | 中等 |
| **CrewAI** | 角色扮演 Agent | 中 | ⭐⭐⭐ | 較低 |
| **MetaGPT** | 軟體開發流程 | 高 | ⭐⭐⭐ | 較高 |
| **LangGraph** | 複雜狀態管理 | 中-高 | ⭐⭐⭐⭐ | 中等 |

### 選擇建議

- **RAG 應用**: LangChain 或 LlamaIndex
- **聊天機器人**: LangChain + LangGraph
- **多 Agent 協作**: AutoGen 或 CrewAI
- **軟體開發**: MetaGPT
- **複雜工作流**: LangGraph

## 💼 實際應用案例

### 1. 郵件自動回覆系統
- 位置: `1.LangchainDemos/yt_email_reply_llama3_crewai_groq.ipynb`
- 技術: CrewAI + Groq
- 功能: 自動分析 YouTube 評論並生成專業回覆

### 2. SQL 查詢 Agent
- 位置: `1.LangchainDemos/9.sql_agent_中文化.ipynb`
- 技術: LangChain + SQL Database
- 功能: 自然語言轉 SQL 查詢

### 3. 銷售外聯自動化
- 位置: `5.demo-sales-outreach-automation-langgraph/`
- 技術: LangGraph + 多種 API
- 功能: 自動化銷售流程管理

### 4. 程式碼理解與生成
- 位置: `1.LangchainDemos/6.code_understanding_ipynb繁中翻譯.ipynb`
- 技術: LangChain + RAG
- 功能: 程式碼分析和智能生成

## 🆕 2025 年最新更新

本專案已更新到 2025 年最新版本，包括：

- ✅ LangChain 0.3.0+ 新特性
- ✅ LangGraph 0.2.30+ 狀態管理
- ✅ LlamaIndex 0.11.0+ 完整教程
- ✅ AutoGen 0.2.0+ 多 Agent 系統
- ✅ CrewAI 0.80.0+ 角色扮演框架
- ✅ 最新的向量數據庫集成
- ✅ Docker 容器化支持
- ✅ 完整的依賴管理

## 🤝 貢獻指南

我們歡迎所有形式的貢獻！

### 如何貢獻

1. Fork 本專案
2. 創建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

### 貢獻方向

- 📝 添加新的教程或範例
- 🐛 修復 bug 或改進現有程式碼
- 📚 改進文檔
- 🌐 添加其他語言版本
- 💡 提出新的想法或建議

## 📄 授權

本專案採用 MIT 授權 - 詳見 [LICENSE](LICENSE) 文件

## 🙏 致謝

- [LangChain](https://python.langchain.com/)
- [LlamaIndex](https://www.llamaindex.ai/)
- [AutoGen](https://microsoft.github.io/autogen/)
- [CrewAI](https://www.crewai.io/)
- [MetaGPT](https://github.com/geekan/MetaGPT)
- 所有開源社區的貢獻者

## 📞 聯絡方式

- 問題回報: [GitHub Issues](https://github.com/yourusername/LLM-agent-Demo/issues)
- 討論區: [GitHub Discussions](https://github.com/yourusername/LLM-agent-Demo/discussions)

## 🗺️ 路線圖

- [x] LangChain 完整教程
- [x] LangGraph Agent 系統
- [x] 多模態 RAG
- [x] LlamaIndex 教程
- [x] AutoGen 教程
- [x] CrewAI 教程
- [x] MetaGPT 教程
- [x] 框架對比指南
- [ ] 更多實際應用案例
- [ ] 視頻教程
- [ ] 英文版本
- [ ] 在線互動式教程

---

⭐ 如果這個專案對你有幫助，請給我們一個 Star！

📖 持續更新中... 最後更新: 2025-01-14

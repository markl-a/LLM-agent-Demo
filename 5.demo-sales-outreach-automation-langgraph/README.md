# 🚀 Sales Outreach Automation with LangGraph

## 📋 目錄

- [專案簡介](#專案簡介)
- [核心功能](#核心功能)
- [系統架構](#系統架構)
- [技術棧](#技術棧)
- [前置需求](#前置需求)
- [快速開始](#快速開始)
- [詳細配置指南](#詳細配置指南)
- [使用說明](#使用說明)
- [專案結構](#專案結構)
- [常見問題](#常見問題)
- [進階使用](#進階使用)
- [貢獻指南](#貢獻指南)
- [授權](#授權)

---

## 專案簡介

**Sales Outreach Automation** 是一個基於 LangGraph 和大型語言模型（LLM）的智能銷售自動化系統。此專案展示如何利用 AI Agent 技術自動化銷售外展流程，從潛在客戶研究到個性化郵件生成，大幅提升銷售團隊的效率。

### 🎯 專案目標

- **自動化銷售流程**：減少手動操作，提升銷售效率
- **個性化溝通**：利用 AI 生成針對性的銷售郵件
- **智能客戶洞察**：自動收集和分析潛在客戶信息
- **CRM 整合**：無縫連接主流 CRM 系統（Airtable、HubSpot）

### 🌟 適用場景

- B2B 銷售團隊的客戶開發
- 市場行銷的潛在客戶培育
- 客戶成功團隊的主動溝通
- 商業拓展的合作夥伴聯繫

---

## 核心功能

### 1️⃣ 智能客戶研究
- **LinkedIn 數據抓取**：自動獲取潛在客戶的職業背景
- **公司信息分析**：深度分析目標公司的業務和需求
- **市場洞察**：收集行業趨勢和競爭情報

### 2️⃣ AI 驅動的內容生成
- **個性化郵件**：基於客戶背景生成定制化郵件
- **多輪對話**：支持後續跟進郵件的自動生成
- **語調適配**：根據客戶類型調整溝通風格

### 3️⃣ 自動化執行
- **郵件自動發送**：通過 Gmail API 自動發送郵件
- **時間優化**：智能選擇最佳發送時間
- **批量處理**：支持大規模客戶列表的批量處理

### 4️⃣ CRM 整合
- **Airtable 整合**：自動同步客戶數據和互動記錄
- **HubSpot 整合**：與 HubSpot CRM 無縫對接
- **Google Sheets**：支持簡易的表格數據管理

### 5️⃣ LangGraph 工作流
- **狀態管理**：追蹤銷售流程的每個階段
- **條件分支**：根據客戶響應智能調整策略
- **錯誤處理**：自動重試和異常處理機制

---

## 系統架構

```
┌─────────────────────────────────────────────────────────────┐
│                     Sales Outreach System                    │
└─────────────────────────────────────────────────────────────┘
                              ▼
        ┌────────────────────────────────────────┐
        │         LangGraph Orchestration        │
        │    (State Machine & Workflow Engine)   │
        └────────────────────────────────────────┘
                              ▼
    ┌──────────────┬──────────────┬──────────────┬──────────────┐
    │              │              │              │              │
┌───▼───┐    ┌────▼────┐   ┌────▼────┐   ┌────▼────┐   ┌────▼────┐
│ Data  │    │  LLM    │   │ Email   │   │  CRM    │   │ Search  │
│ Agent │    │ Agent   │   │ Agent   │   │ Agent   │   │ Agent   │
└───┬───┘    └────┬────┘   └────┬────┘   └────┬────┘   └────┬────┘
    │             │              │              │              │
    ▼             ▼              ▼              ▼              ▼
┌────────┐  ┌─────────┐   ┌─────────┐   ┌──────────┐  ┌──────────┐
│LinkedIn│  │ Gemini/ │   │  Gmail  │   │ Airtable │  │  Serper  │
│  API   │  │ OpenAI  │   │   API   │   │ HubSpot  │  │   API    │
└────────┘  └─────────┘   └─────────┘   └──────────┘  └──────────┘
```

### 工作流程說明

1. **數據收集階段**：從 CRM 或 Google Sheets 讀取潛在客戶列表
2. **研究階段**：使用 LinkedIn API 和搜索引擎收集客戶信息
3. **內容生成階段**：LLM 基於收集的信息生成個性化郵件
4. **執行階段**：通過 Gmail API 發送郵件
5. **同步階段**：將互動記錄回寫到 CRM 系統

更多架構細節請參考 [architecture.md](./docs/architecture.md)

---

## 技術棧

### 核心框架
- **LangGraph**：用於構建複雜的 AI Agent 工作流
- **LangChain**：LLM 應用開發框架

### LLM 提供商
- **Google Gemini**：主要推薦的 LLM（性價比高）
- **OpenAI GPT**：備選方案
- **Groq**：高速推理的備選方案

### 整合服務
- **Gmail API**：郵件發送
- **LinkedIn API (RapidAPI)**：客戶數據抓取
- **Serper API**：網路搜索
- **Airtable API**：CRM 數據管理
- **HubSpot API**：企業級 CRM 整合

### 開發工具
- Python 3.9+
- html2text：HTML 轉換
- python-dotenv：環境變數管理

---

## 前置需求

### 系統需求
- **Python**：3.9 或更高版本
- **作業系統**：Linux、macOS 或 Windows
- **記憶體**：建議 4GB 以上

### API 金鑰需求

以下 API 金鑰是必須的：

1. **Google Gemini API Key**（或 OpenAI API Key）
   - 申請地址：https://ai.google.dev/

2. **Serper API Key**（用於網路搜索）
   - 申請地址：https://serper.dev/

3. **RapidAPI Key**（用於 LinkedIn 數據抓取）
   - 申請地址：https://rapidapi.com/

4. **Google APIs Credentials**（用於 Gmail）
   - 配置指南見下方

5. **CRM API 金鑰**（選擇其中一個）
   - Airtable：https://airtable.com/create/tokens
   - HubSpot：https://developers.hubspot.com/

### Python 依賴套件

所有依賴套件都列在原始專案的 `requirements.txt` 中，設置腳本會自動安裝。

---

## 快速開始

### 步驟 1：執行自動化設置腳本

```bash
# 在專案根目錄執行
cd 5.demo-sales-outreach-automation-langgraph
python setup_script.py
```

此腳本會自動完成：
- ✅ 克隆原始專案倉庫
- ✅ 創建 Python 虛擬環境
- ✅ 安裝所有依賴套件
- ✅ 生成 `.env` 配置文件模板

### 步驟 2：啟動虛擬環境

```bash
# Linux/macOS
source sales-outreach-automation-langgraph/venv/bin/activate

# Windows
sales-outreach-automation-langgraph\venv\Scripts\activate
```

### 步驟 3：安裝額外依賴

```bash
pip install html2text
```

### 步驟 4：進入專案目錄

```bash
cd sales-outreach-automation-langgraph
```

### 步驟 5：配置環境變數

編輯 `.env` 文件，填入你的 API 金鑰：

```env
# LLM API Keys
GEMINI_API_KEY=your-gemini-api-key
GOOGLE_API_KEY=your-gemini-api-key
OPENAI_API_KEY=your-openai-api-key

# Search & Data APIs
SERPER_API_KEY=your-serper-api-key
RAPIDAPI_KEY=your-rapidapi-key

# CRM Configuration (選擇其中一個)
AIRTABLE_ACCESS_TOKEN=your-airtable-token
AIRTABLE_BASE_ID=your-base-id
AIRTABLE_TABLE_NAME=your-table-name

HUBSPOT_API_KEY=your-hubspot-key

# Google Sheets
SHEET_ID=your-google-sheet-id
```

詳細配置說明請參考 [config-guide.md](./docs/config-guide.md)

### 步驟 6：設置 Google API 憑證

#### 6.1 創建 OAuth 憑證

1. 訪問 [Google Gmail API Quickstart](https://developers.google.com/gmail/api/quickstart/python?hl=zh-tw)
2. 按照「授權電腦版應用程式的憑證」步驟操作
3. 下載 `credentials.json` 文件
4. 將文件移動到 `sales-outreach-automation-langgraph/` 目錄（與 `main.py` 同級）

#### 6.2 配置 OAuth 同意畫面

1. 前往 [Google Cloud Console](https://console.cloud.google.com/auth/clients?hl=zh-tw)
2. 點擊「OAuth 同意畫面」
3. 選擇「資料存取權」→「新增或移除範圍」
4. 添加以下範圍：
   - Gmail API：`https://www.googleapis.com/auth/gmail.send`
   - Gmail API：`https://www.googleapis.com/auth/gmail.readonly`

### 步驟 7：配置 Airtable（如使用）

#### 7.1 獲取 Access Token

1. 訪問 [Airtable Token Creator](https://airtable.com/create/tokens)
2. 點擊「Create token」
3. 設置權限：
   - `data.records:read`：讀取數據
   - `data.records:write`：寫入數據
   - `schema.bases:read`：讀取結構
4. 選擇要授權的 Base
5. 複製生成的 Token

#### 7.2 獲取 Base ID 和 Table Name

- **Base ID**：在 Airtable URL 中，格式為 `appXXXXXXXXXXXXXX`
  - 例如：`https://airtable.com/appABC123/tblXYZ456`
  - Base ID 就是 `appABC123`

- **Table Name**：你在 Airtable 中創建的表格名稱（預設為 "Databases"）

#### 7.3 添加 Status 欄位

⚠️ **重要**：在 Airtable 表格的最右側添加一個名為 `status` 的欄位，否則執行時會出錯。

### 步驟 8：運行專案

```bash
python main.py
```

首次運行時，會打開瀏覽器要求你授權 Gmail API 訪問權限。

---

## 詳細配置指南

完整的配置指南已獨立成文檔，包含：

- 各個 API 的詳細申請步驟
- 環境變數的完整說明
- Google OAuth 的高級配置
- CRM 系統的深度整合
- 常見配置錯誤和解決方案

請參考：[config-guide.md](./docs/config-guide.md)

---

## 使用說明

### 基本使用流程

1. **準備客戶列表**
   - 在 Airtable/HubSpot/Google Sheets 中創建客戶列表
   - 必填字段：姓名、郵箱、公司名稱

2. **運行系統**
   ```bash
   python main.py
   ```

3. **監控執行**
   - 系統會自動處理客戶列表
   - 在終端查看實時日誌
   - 在 CRM 中查看更新狀態

4. **查看結果**
   - 已發送的郵件會顯示在 Gmail「已發送」文件夾
   - CRM 中的 `status` 欄位會更新為 `sent`

### 自定義配置

你可以修改以下參數來適應你的需求：

- **郵件模板**：編輯 prompt 文件來自定義郵件風格
- **處理速度**：調整批量處理的並發數
- **LLM 選擇**：在 `.env` 中切換不同的 LLM 提供商

詳見 [best-practices.md](./docs/best-practices.md)

---

## 專案結構

```
5.demo-sales-outreach-automation-langgraph/
├── README.md                    # 本文件
├── setup_script.py             # 自動化設置腳本
├── docs/                       # 文檔目錄
│   ├── config-guide.md        # 詳細配置指南
│   ├── architecture.md        # 系統架構說明
│   ├── troubleshooting.md     # 故障排除指南
│   └── best-practices.md      # 最佳實踐
├── examples/                   # 示例代碼
│   ├── basic_usage.py         # 基礎使用示例
│   ├── custom_agent.py        # 自定義 Agent 示例
│   └── batch_processing.py    # 批量處理示例
└── sales-outreach-automation-langgraph/  # 原始專案（克隆後）
    ├── main.py                # 主程式入口
    ├── requirements.txt       # Python 依賴
    ├── .env                   # 環境變數（需自行配置）
    ├── credentials.json       # Google API 憑證（需自行配置）
    └── ...                    # 其他專案文件
```

---

## 常見問題

### Q1：為什麼需要這麼多 API 金鑰？

**A**：每個 API 服務都有特定用途：
- **Gemini/OpenAI**：生成個性化內容
- **Serper**：搜索公司和行業信息
- **RapidAPI**：獲取 LinkedIn 數據
- **Gmail**：發送郵件
- **CRM API**：管理客戶數據

你可以根據實際需求選擇性配置。最小化配置只需要 LLM API 和 Gmail API。

### Q2：我可以使用免費版的 API 嗎？

**A**：大部分 API 都有免費額度：
- **Gemini**：每日免費配額
- **Serper**：2,500 次免費搜索
- **RapidAPI**：依服務而定
- **Airtable**：免費版有限制但足夠測試

### Q3：如何處理 API 配額限制？

**A**：系統內建了速率限制和重試機制。你也可以：
- 調整批量處理的大小
- 使用多個 API 金鑰輪換
- 升級到付費方案

### Q4：支援哪些 CRM 系統？

**A**：目前支援：
- Airtable（推薦用於小型團隊）
- HubSpot（企業級）
- Google Sheets（簡易方案）

### Q5：可以自定義郵件模板嗎？

**A**：可以！系統使用 LLM 生成郵件，你可以通過修改 prompt 來自定義：
- 郵件語調和風格
- 郵件長度
- 包含的信息類型

更多問題請參考 [troubleshooting.md](./docs/troubleshooting.md)

---

## 進階使用

### 1. 自定義 Agent

你可以創建自己的 Agent 來擴展系統功能：

```python
from langgraph.graph import StateGraph
from typing import TypedDict

class CustomAgent:
    def __init__(self):
        # 初始化你的 Agent
        pass

    def process(self, state):
        # 處理邏輯
        return state
```

詳見 [examples/custom_agent.py](./examples/custom_agent.py)

### 2. 批量處理優化

對於大規模客戶列表，使用批量處理模式：

```python
# 見 examples/batch_processing.py
```

### 3. 多語言支持

系統支持多語言郵件生成，只需在 prompt 中指定語言。

### 4. A/B 測試

你可以設置多個郵件模板進行 A/B 測試，比較效果。

---

## 貢獻指南

歡迎貢獻！如果你有改進建議：

1. Fork 本專案
2. 創建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

### 貢獻方向

- 🐛 Bug 修復
- 📝 文檔改進
- ✨ 新功能開發
- 🎨 UI/UX 改進
- 🧪 測試覆蓋

---

## 授權

本 demo 基於原始專案：[sales-outreach-automation-langgraph](https://github.com/kaymen99/sales-outreach-automation-langgraph)

請遵守原專案的授權條款。

---

## 相關資源

- **原始專案**：https://github.com/kaymen99/sales-outreach-automation-langgraph
- **LangGraph 文檔**：https://python.langchain.com/docs/langgraph
- **LangChain 文檔**：https://python.langchain.com/
- **Google Gemini API**：https://ai.google.dev/
- **Gmail API 文檔**：https://developers.google.com/gmail/api

---

## 支援與反饋

如遇到問題或有建議，請：

1. 查看 [troubleshooting.md](./docs/troubleshooting.md)
2. 查看原專案的 Issues
3. 在本專案中創建 Issue

---

**Happy Selling! 🎉**

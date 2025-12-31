# n8n - 開源工作流自動化平台

## 簡介

n8n 是一個功能強大的開源工作流自動化平台，專為技術用戶和開發者設計。它允許你連接任何應用程序並自動化工作流程，特別擅長構建 AI 驅動的 Agent 和複雜的多系統整合流程。n8n 在 GitHub 上擁有 **150K+ stars**，是最受歡迎的工作流自動化工具之一。

**官方網站**: [https://n8n.io/](https://n8n.io/)
**GitHub**: [https://github.com/n8n-io/n8n](https://github.com/n8n-io/n8n)
**官方文檔**: [https://docs.n8n.io/](https://docs.n8n.io/)

## 核心特點

### 1. 豐富的整合生態系統
- **400+ 原生整合**: 支援主流服務和 API
- **自定義節點**: 可以創建自己的整合節點
- **HTTP 請求**: 可以調用任何 REST API
- **Webhook**: 支援接收和發送 Webhook

### 2. AI Agent 能力

#### AI 工作流節點
- **AI Agent**: 構建智能代理，自動決策和執行任務
- **LLM Chain**: 串連多個 LLM 調用，構建複雜對話流程
- **AI Transform**: 使用 AI 進行數據轉換和處理
- **Embeddings**: 生成和使用文本嵌入向量

#### 支援的 AI 服務
- **OpenAI**: GPT-4, GPT-3.5, DALL-E, Whisper
- **Anthropic**: Claude 3 系列模型
- **Google**: Gemini, PaLM
- **Hugging Face**: 開源模型
- **Ollama**: 本地運行的開源模型
- **Azure OpenAI**: 企業級 AI 服務

### 3. 工作流功能

#### 觸發器類型
- **Webhook Trigger**: HTTP 請求觸發
- **Schedule Trigger**: 定時觸發（Cron）
- **Manual Trigger**: 手動觸發
- **Email Trigger**: 郵件觸發
- **Form Trigger**: 表單提交觸發
- **Chat Trigger**: 聊天機器人觸發

#### 執行控制
- **IF 節點**: 條件判斷和分支
- **Switch 節點**: 多條件路由
- **Merge 節點**: 合併多個執行路徑
- **Loop 節點**: 循環處理數據
- **Split 節點**: 分割批次處理
- **Wait 節點**: 延遲執行

#### 數據處理
- **Set 節點**: 設置變數和數據
- **Code 節點**: JavaScript/Python 自定義邏輯
- **Function 節點**: 編寫函數處理數據
- **HTTP Request**: 調用外部 API
- **Database 節點**: 直接操作資料庫

### 4. 錯誤處理與重試
- **Error Trigger**: 捕獲工作流錯誤
- **Retry 機制**: 自動重試失敗的節點
- **Error Workflow**: 專門處理錯誤的子工作流
- **Alert 通知**: 錯誤時發送通知

### 5. 向量數據庫整合
支援多種向量數據庫，用於 RAG 應用：
- **Pinecone**: 雲端向量數據庫
- **Qdrant**: 高性能向量搜索
- **Chroma**: 輕量級向量數據庫
- **Weaviate**: 開源向量搜索引擎
- **Supabase**: PostgreSQL + pgvector

### 6. 記憶和狀態管理
- **Chat Memory**: 對話歷史記憶
- **Window Memory**: 滑動窗口記憶
- **Summary Memory**: 摘要式記憶
- **Redis 整合**: 分佈式狀態存儲

### 7. 子工作流
- **Execute Workflow**: 調用其他工作流
- **參數傳遞**: 在工作流之間傳遞數據
- **工作流重用**: 模塊化設計
- **遞迴調用**: 支援工作流自我調用

## 安裝方式

### 方法 1: Docker（推薦）

**最簡單的安裝方式**：

```bash
# 使用 Docker 運行 n8n
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n

# 使用 Docker Compose（持久化配置）
docker-compose up -d
```

**docker-compose.yml** 示例：
```yaml
version: '3.8'

services:
  n8n:
    image: n8nio/n8n
    restart: always
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=password
      - N8N_HOST=localhost
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - NODE_ENV=production
      - WEBHOOK_URL=http://localhost:5678/
      # AI 服務配置
      - OPENAI_API_KEY=sk-...
      - ANTHROPIC_API_KEY=sk-ant-...
    volumes:
      - ~/.n8n:/home/node/.n8n
    networks:
      - n8n-network

  # PostgreSQL 數據庫（可選，生產環境推薦）
  postgres:
    image: postgres:15
    restart: always
    environment:
      - POSTGRES_USER=n8n
      - POSTGRES_PASSWORD=n8n
      - POSTGRES_DB=n8n
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - n8n-network

volumes:
  postgres-data:

networks:
  n8n-network:
    driver: bridge
```

訪問 `http://localhost:5678` 使用 n8n UI。

### 方法 2: npm 安裝

**前置要求**: Node.js v18.10 或更高版本

```bash
# 全局安裝 n8n
npm install n8n -g

# 啟動 n8n
n8n start

# 指定端口
n8n start --tunnel
```

### 方法 3: n8n.cloud（雲端服務）

官方提供的托管服務，無需自行部署：
- **免費方案**: 每月 5,000 次執行
- **付費方案**: 更多執行次數和功能
- **網址**: https://app.n8n.cloud/

### 方法 4: 自托管部署

#### 使用 PM2（生產環境）
```bash
# 安裝 PM2
npm install pm2 -g

# 安裝 n8n
npm install n8n -g

# 使用 PM2 啟動 n8n
pm2 start n8n

# 設置開機自啟
pm2 startup
pm2 save
```

#### 使用 Nginx 反向代理
```nginx
server {
    listen 80;
    server_name n8n.yourdomain.com;

    location / {
        proxy_pass http://localhost:5678;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## AI Agent 相關節點介紹

### 1. AI Agent 節點
構建智能代理，可以自動選擇工具並執行任務。

**特點**：
- 自主決策能力
- 多工具調用
- 上下文理解
- 任務分解

**使用場景**：
- 客戶服務自動化
- 數據分析助手
- 內容生成
- 任務調度

### 2. AI Chain 節點
創建多步驟的 AI 處理流程。

**支援的 Chain 類型**：
- **LLM Chain**: 基礎的 LLM 調用鏈
- **Conversation Chain**: 對話式交互
- **Summarization Chain**: 文本摘要
- **Question Answering Chain**: 問答系統
- **SQL Database Chain**: 自然語言查詢數據庫

### 3. Document Loaders
加載各種格式的文檔用於 RAG 應用。

**支援格式**：
- PDF, DOCX, TXT, CSV, JSON
- Markdown, HTML
- Notion, Confluence
- GitHub, GitBook
- Web Scraping

### 4. Text Splitters
將長文本分割成適合處理的塊。

**分割策略**：
- Character Text Splitter
- Recursive Character Splitter
- Token Text Splitter
- Markdown Text Splitter

### 5. Embeddings 節點
生成文本的向量嵌入。

**支援的 Embedding 模型**：
- OpenAI Embeddings
- Cohere Embeddings
- Hugging Face Embeddings
- Azure OpenAI Embeddings
- Ollama Embeddings

### 6. Vector Store 節點
存儲和檢索向量數據。

**操作**：
- Insert Documents
- Retrieve Documents
- Get Relevant Documents
- Similarity Search

## REST API 使用

n8n 提供完整的 REST API 用於工作流管理和執行。

### API 端點

#### 1. 執行工作流
```bash
POST /api/v1/workflows/:id/execute

# 請求體
{
  "data": {
    "param1": "value1",
    "param2": "value2"
  }
}
```

#### 2. 獲取工作流列表
```bash
GET /api/v1/workflows
```

#### 3. 創建工作流
```bash
POST /api/v1/workflows

# 請求體
{
  "name": "My Workflow",
  "nodes": [...],
  "connections": {...},
  "active": true
}
```

#### 4. 更新工作流
```bash
PATCH /api/v1/workflows/:id

# 請求體
{
  "name": "Updated Name",
  "active": false
}
```

#### 5. 刪除工作流
```bash
DELETE /api/v1/workflows/:id
```

#### 6. 獲取執行歷史
```bash
GET /api/v1/executions

# 查詢參數
?workflowId=123&status=success&limit=10
```

### API 認證

```bash
# 使用 API Key 認證
curl -X GET http://localhost:5678/api/v1/workflows \
  -H "X-N8N-API-KEY: your-api-key"
```

## 環境變量配置

創建 `.env` 文件或在 Docker 中配置：

```bash
# 基本配置
N8N_PORT=5678
N8N_HOST=localhost
N8N_PROTOCOL=http
NODE_ENV=production

# 認證配置
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=secure_password

# Webhook 配置
WEBHOOK_URL=https://your-domain.com/

# 數據庫配置（PostgreSQL）
DB_TYPE=postgresdb
DB_POSTGRESDB_HOST=localhost
DB_POSTGRESDB_PORT=5432
DB_POSTGRESDB_DATABASE=n8n
DB_POSTGRESDB_USER=n8n
DB_POSTGRESDB_PASSWORD=password

# AI 服務 API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
COHERE_API_KEY=...

# 向量數據庫
PINECONE_API_KEY=...
PINECONE_ENVIRONMENT=...
QDRANT_API_KEY=...
QDRANT_URL=...

# 日誌配置
N8N_LOG_LEVEL=info
N8N_LOG_OUTPUT=console

# 執行配置
EXECUTIONS_DATA_SAVE_ON_ERROR=all
EXECUTIONS_DATA_SAVE_ON_SUCCESS=all
EXECUTIONS_DATA_SAVE_MANUAL_EXECUTIONS=true

# 性能配置
N8N_PAYLOAD_SIZE_MAX=16
N8N_METRICS=true
```

## 使用場景

### 1. AI 客服機器人
- 接收客戶查詢（Webhook/Chat Trigger）
- AI Agent 理解問題並查詢知識庫
- 自動回復或轉人工處理
- 記錄對話歷史

### 2. 文檔問答系統（RAG）
- 加載和處理文檔
- 生成向量嵌入並存儲
- 接收用戶問題
- 檢索相關文檔並生成答案

### 3. 數據管道自動化
- 定時抓取數據（API/Web Scraping）
- AI 清洗和轉換數據
- 存儲到數據庫或數據倉庫
- 生成報告並發送通知

### 4. 內容生成工作流
- 接收內容需求
- AI 生成初稿
- 多輪審核和優化
- 發佈到 CMS 或社交媒體

### 5. 監控和告警系統
- 監控系統指標或日誌
- AI 分析異常模式
- 自動分類和優先級排序
- 發送告警通知

### 6. 多系統數據同步
- 監聽系統 A 的事件
- 轉換數據格式
- 更新系統 B、C、D
- 處理衝突和錯誤

## 優勢與特點

### 優勢
- ✅ **開源自托管**: 完全控制數據和部署
- ✅ **豐富的整合**: 400+ 預建節點
- ✅ **強大的 AI 能力**: 原生支援 LLM 和 Vector Store
- ✅ **視覺化編輯器**: 直觀的拖放式界面
- ✅ **靈活的部署**: Docker、npm、雲端多種選擇
- ✅ **活躍社區**: GitHub 150K+ stars
- ✅ **可擴展性**: 支援自定義節點和函數
- ✅ **企業級功能**: 錯誤處理、重試、日誌、監控

### 適用對象
- DevOps 工程師
- 數據工程師
- AI 開發者
- 自動化專家
- 全棧開發者
- 企業 IT 團隊

## 與其他平台比較

| 特性 | n8n | Zapier | Make (Integromat) | Flowise |
|------|-----|--------|-------------------|---------|
| 開源 | ✅ | ❌ | ❌ | ✅ |
| 自托管 | ✅ | ❌ | ❌ | ✅ |
| 整合數量 | 400+ | 5000+ | 1000+ | 150+ |
| AI Agent | ✅ | 有限 | 有限 | ✅ 專注 |
| 程式碼節點 | ✅ | 有限 | 有限 | ✅ |
| 價格 | 免費 | 訂閱制 | 訂閱制 | 免費 |
| 學習曲線 | 中等 | 簡單 | 中等 | 中等 |
| 目標用戶 | 技術用戶 | 非技術用戶 | 非技術用戶 | AI 開發者 |

## 最佳實踐

### 1. 工作流設計
- 使用清晰的命名約定
- 添加註釋說明複雜邏輯
- 模塊化設計，使用子工作流
- 合理使用變量和參數

### 2. 錯誤處理
- 為關鍵節點添加錯誤處理
- 使用 Error Trigger 捕獲異常
- 設置重試機制
- 配置告警通知

### 3. 性能優化
- 避免不必要的節點
- 使用批次處理大量數據
- 優化 HTTP 請求（併發控制）
- 監控執行時間

### 4. 安全性
- 使用環境變量存儲敏感信息
- 啟用認證機制
- 定期備份工作流
- 使用 HTTPS 部署

### 5. 維護性
- 版本控制工作流（JSON 導出）
- 文檔化複雜邏輯
- 定期清理舊的執行記錄
- 監控工作流狀態

## 資源鏈接

- **官方網站**: https://n8n.io/
- **GitHub**: https://github.com/n8n-io/n8n (150K+ stars)
- **官方文檔**: https://docs.n8n.io/
- **社區論壇**: https://community.n8n.io/
- **Discord**: https://discord.gg/n8n
- **YouTube**: https://www.youtube.com/@n8n-io
- **模板市場**: https://n8n.io/workflows/
- **Node.js API**: https://www.npmjs.com/package/n8n
- **Python SDK**: 社區提供（非官方）

## 示例說明

本目錄包含以下 Python 示例，展示如何通過 REST API 與 n8n 交互：

1. **01_API調用基礎.py** - n8n REST API 的基礎使用方法
2. **02_工作流創建.py** - 通過 API 創建和管理工作流
3. **03_AI節點使用.py** - 配置和使用 AI Agent 節點
4. **04_觸發器設置.py** - 設置 Webhook 和定時觸發器
5. **05_數據轉換.py** - 使用 Code 節點進行數據處理
6. **06_條件邏輯.py** - 實現 IF/Switch 條件分支
7. **07_錯誤處理.py** - 配置錯誤處理和重試機制
8. **08_子工作流.py** - 創建和調用子工作流
9. **09_LLM整合.py** - 整合 OpenAI、Claude 等 LLM 模型
10. **10_生產部署.py** - 自托管部署和監控配置

## 快速開始

### 1. 安裝 n8n
```bash
# 使用 Docker
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

### 2. 安裝 Python 依賴
```bash
pip install -r requirements.txt
```

### 3. 配置環境變量
```bash
export N8N_API_URL="http://localhost:5678"
export N8N_API_KEY="your-api-key"  # 如果啟用了 API 認證
export OPENAI_API_KEY="sk-..."     # 用於 AI 功能
```

### 4. 運行示例
```bash
# 運行基礎 API 調用示例
python 01_API調用基礎.py

# 創建一個簡單的工作流
python 02_工作流創建.py

# 測試 AI Agent 功能
python 03_AI節點使用.py
```

## 常見問題

### Q: n8n 和 Zapier 有什麼區別？
A: n8n 是開源的，可以自托管，完全控制數據。Zapier 是 SaaS 服務，更適合非技術用戶。n8n 提供更多技術靈活性（自定義代碼、複雜邏輯）。

### Q: n8n 可以免費使用嗎？
A: 是的，n8n 是開源的（Apache 2.0 許可證），自托管完全免費。官方也提供 n8n.cloud 雲端服務，有免費方案。

### Q: 如何在生產環境部署 n8n？
A: 建議使用 Docker + PostgreSQL + Nginx 的組合。使用 PM2 或 Kubernetes 管理進程，配置 HTTPS 和認證。

### Q: n8n 支援哪些 AI 模型？
A: 支援 OpenAI GPT、Claude、Gemini、Hugging Face 模型，以及通過 Ollama 運行的本地開源模型。

### Q: 如何擴展 n8n 的功能？
A: 可以創建自定義節點、使用 Code 節點編寫 JavaScript/Python、調用外部 API、開發社區節點。

### Q: n8n 的執行限制是什麼？
A: 自托管版本沒有執行次數限制，僅受服務器資源限制。雲端版本根據方案有不同的執行次數配額。

## 許可證

n8n 採用 **Apache 2.0 許可證**，允許商業使用和修改。

部分企業功能需要 n8n Enterprise License。

## 貢獻

歡迎貢獻代碼、創建自定義節點、報告問題或提出功能請求！

- **GitHub Issues**: https://github.com/n8n-io/n8n/issues
- **貢獻指南**: https://docs.n8n.io/contributing/
- **Node 開發**: https://docs.n8n.io/integrations/creating-nodes/

---

**最後更新**: 2025-12-31
**維護者**: n8n Community
**Star 數量**: 150K+ (GitHub)

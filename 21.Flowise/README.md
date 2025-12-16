# Flowise - 視覺化 AI 工作流構建平台

## 簡介

Flowise 是一個開源的低代碼平台，用於視覺化構建 AI Agent 和 LLM 工作流。它基於 LangChain 和 LlamaIndex 生態系統，提供拖放式界面讓開發者和非技術用戶都能輕鬆創建 AI 應用。

**官方網站**: [https://flowiseai.com/](https://flowiseai.com/)
**GitHub**: [https://github.com/FlowiseAI/Flowise](https://github.com/FlowiseAI/Flowise)
**官方文檔**: [https://docs.flowiseai.com/](https://docs.flowiseai.com/)

## 核心特點

### 1. 視覺化工作流編輯器
- **拖放式界面**: 通過拖放節點創建複雜的 AI 工作流
- **即時預覽**: 實時測試和調試流程
- **節點庫**: 提供 150+ 預建節點，包括 LLM、向量數據庫、工具等

### 2. 多種 Agent 類型支持

#### Chatflow
- 用於構建單一代理系統、聊天機器人和簡單 LLM 流程
- 支持 RAG（檢索增強生成）、重排序、檢索器等高級技術
- 更靈活的配置選項

#### Agentflow V2
- 支持多代理系統和複雜工作流編排
- 基於原生 Flowise 組件的細粒度節點設計
- 每個節點作為獨立單元執行離散操作
- 支持循環和迭代處理

#### Sequential Agents
- 基於 LangGraph 構建
- 使用有向循環圖（DCG）結構化工作流
- 支持受控循環和迭代處理

### 3. 廣泛的集成支持

#### LLM 提供商
- OpenAI (GPT-3.5, GPT-4, GPT-4o)
- Anthropic (Claude 2, Claude 3)
- Google (Gemini, PaLM)
- AWS Bedrock
- Azure OpenAI
- Hugging Face
- Ollama (本地模型)

#### 向量數據庫
- Pinecone
- Chroma
- Qdrant
- Weaviate
- Supabase
- Redis
- Milvus
- FAISS

#### 工具集成
- BraveSearch API
- Google Search
- Calculator
- Custom Tools
- Gmail
- Google Calendar
- Google Sheets
- OpenAPI Toolkit
- Code Interpreter

### 4. RAG 能力
- 支持多種文檔加載器（PDF、TXT、CSV、JSON、Markdown 等）
- 文檔分割和預處理
- 向量嵌入和存儲
- 高級檢索技術（重排序、混合搜索、Graph RAG）

### 5. 記憶管理
- **會話記憶**: 自動管理用戶對話歷史
- **長期記憶**: 使用 SQLite 存儲持久化數據
- **自定義 Session ID**: 支持多用戶會話隔離

### 6. API 支持
- RESTful API 端點
- 流式響應（SSE）
- 文件上傳支持
- API 密鑰認證
- Webhook 集成

### 7. 部署選項
- **本地部署**: NPM、Docker
- **雲端部署**: Render、Railway、AWS、Azure、Digital Ocean
- **Flowise Cloud**: 官方托管服務

## 安裝方式

### 方法 1: NPM 安裝（推薦）

**前置要求**: Node.js v18.15.0 或 v20 以上

```bash
# 全局安裝
npm install -g flowise

# 啟動 Flowise
npx flowise start

# 指定端口啟動
npx flowise start --PORT=3000
```

訪問 `http://localhost:3000` 使用 Flowise UI。

### 方法 2: Git Clone

```bash
# 克隆倉庫
git clone https://github.com/FlowiseAI/Flowise.git
cd Flowise

# 安裝依賴（使用 pnpm）
npm install -g pnpm
pnpm install

# 構建代碼
pnpm build

# 啟動應用
pnpm start
```

### 方法 3: Docker

```bash
# 拉取並運行 Docker 鏡像
docker run -d \
  --name flowise \
  -p 3000:3000 \
  -v ~/.flowise:/root/.flowise \
  flowiseai/flowise

# 或使用 Docker Compose
docker-compose up -d
```

**docker-compose.yml** 示例：
```yaml
version: '3.8'

services:
  flowise:
    image: flowiseai/flowise
    restart: always
    ports:
      - "3000:3000"
    volumes:
      - ~/.flowise:/root/.flowise
    environment:
      - DATABASE_PATH=/root/.flowise
      - APIKEY_PATH=/root/.flowise
      - SECRETKEY_PATH=/root/.flowise
      - FLOWISE_USERNAME=admin
      - FLOWISE_PASSWORD=1234
```

### 方法 4: Python SDK 安裝

```bash
# 安裝 Flowise Python SDK
pip install flowise
```

## Python SDK 快速開始

```python
from flowise import Flowise, PredictionData

# 初始化客戶端
client = Flowise(
    base_url="http://localhost:3000",
    api_key="your-api-key"  # 如果配置了 API 密鑰
)

# 創建預測（非流式）
response = client.create_prediction(
    PredictionData(
        chatflowId="your-chatflow-id",
        question="你好，請問什麼是 AI？",
        streaming=False
    )
)

# 處理響應
for item in response:
    print(item)
```

## 項目架構

Flowise 是一個 monorepo 結構，包含三個主要模塊：

```
Flowise/
├── packages/
│   ├── server/          # Node.js Express 後端，提供 REST API
│   ├── ui/              # React SPA 前端，基於 Vite 構建
│   └── components/      # LangChain/LlamaIndex 組件節點（150+）
├── docker/
├── docs/
└── examples/
```

### 核心組件

1. **Server (後端)**
   - Express.js REST API
   - 工作流執行引擎
   - 數據庫管理（SQLite/PostgreSQL）
   - 認證和授權

2. **UI (前端)**
   - React + Vite
   - ReactFlow 畫布編輯器
   - 拖放交互
   - 實時預覽和調試

3. **Components (節點)**
   - 實現 INode 接口
   - 150+ 預建節點
   - 支持自定義節點開發

## API 使用

### REST API 端點

#### 1. 創建預測
```bash
POST /api/v1/prediction/:chatflowId

# 請求體
{
  "question": "你的問題",
  "streaming": false,
  "history": [],
  "uploads": []
}
```

#### 2. 流式預測
```bash
POST /api/v1/prediction/:chatflowId

# 請求體
{
  "question": "你的問題",
  "streaming": true  # 啟用流式響應
}
```

#### 3. 獲取 Chatflow 列表
```bash
GET /api/v1/chatflows
```

#### 4. 獲取特定 Chatflow
```bash
GET /api/v1/chatflows/:id
```

### API 認證

```bash
# 使用 API Key 認證
curl -X POST http://localhost:3000/api/v1/prediction/:id \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{"question": "Hello!"}'
```

## 環境變量配置

創建 `.env` 文件：

```bash
# 端口配置
PORT=3000

# 數據庫路徑
DATABASE_PATH=/root/.flowise

# API 密鑰路徑
APIKEY_PATH=/root/.flowise

# 密鑰路徑
SECRETKEY_PATH=/root/.flowise

# 用戶名和密碼（可選）
FLOWISE_USERNAME=admin
FLOWISE_PASSWORD=secure_password

# OpenAI API 密鑰
OPENAI_API_KEY=sk-...

# 其他 LLM API 密鑰
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
```

## 使用場景

1. **聊天機器人**: 客服、FAQ、知識庫問答
2. **RAG 應用**: 文檔問答、企業知識管理
3. **代理系統**: 自動化任務、工作流編排
4. **多模態應用**: 圖像理解、語音交互
5. **數據分析**: 自然語言查詢、報表生成

## 優勢與特點

### 優勢
- ✅ 低代碼/無代碼開發
- ✅ 快速原型設計和迭代
- ✅ 豐富的預建組件
- ✅ 活躍的社區支持
- ✅ 開源免費
- ✅ 支持本地部署

### 適用對象
- 產品經理和業務人員
- AI 開發者
- 數據科學家
- 企業 IT 團隊

## 資源鏈接

- **官方網站**: https://flowiseai.com/
- **GitHub**: https://github.com/FlowiseAI/Flowise
- **官方文檔**: https://docs.flowiseai.com/
- **Python SDK**: https://github.com/FlowiseAI/FlowisePy
- **Discord 社區**: https://discord.gg/flowise
- **YouTube 教程**: https://www.youtube.com/@FlowiseAI

## 示例說明

本目錄包含以下 Python 示例：

1. **01_API調用基礎.py** - Flowise API 的基礎使用方法
2. **02_Chatflow創建.py** - 如何通過 API 創建和管理 Chatflow
3. **03_自定義工具.py** - 自定義工具的開發和集成
4. **04_向量存儲.py** - 向量數據庫的使用和管理
5. **05_Agent配置.py** - Agent 的配置和使用
6. **06_記憶管理.py** - 對話記憶和會話管理
7. **07_文檔處理.py** - 文檔加載、分割和處理
8. **08_嵌入模型.py** - Embedding 模型的配置和使用
9. **09_部署監控.py** - 應用部署和性能監控
10. **10_進階應用.py** - 多代理系統和複雜工作流

## 許可證

Flowise 採用 Apache 2.0 許可證。

## 貢獻

歡迎貢獻代碼、報告問題或提出功能請求！請訪問 [GitHub Issues](https://github.com/FlowiseAI/Flowise/issues)。

---

**最後更新**: 2025-12-15

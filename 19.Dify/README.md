# Dify 框架範例教程

## 框架簡介

Dify 是一個開源的 LLM 應用開發平台，專注於簡化 AI 應用的構建過程。Dify 名稱來源於 "Define + Modify"，意指定義和持續改進您的 AI 應用。

### 核心特點

#### 1. 生產就緒的 Agentic 工作流平台
- **視覺化工作流編輯器**：在視覺化畫布上構建和測試強大的 AI 工作流
- **直觀的界面**：結合 Agent AI 工作流、RAG 流水線、Agent 能力、模型管理和可觀測性功能

#### 2. 全面的模型支持
- 無縫整合數百個專有/開源 LLM
- 支援來自數十家推理提供商和自託管解決方案的模型
- 涵蓋 GPT、Mistral、Llama3 和任何 OpenAI API 相容模型
- 2025 年新增 MCP 協議支持，可透過標準化 MCP 協議訪問外部 API、資料庫和服務

#### 3. Prompt IDE
- 直觀的界面用於編寫提示詞
- 比較模型性能
- 為基於聊天的應用添加額外功能（如文字轉語音）

#### 4. RAG 流水線
- 廣泛的 RAG 能力，從文檔攝取到檢索
- 開箱即用支援從 PDF、PPT 和其他常見文檔格式提取文字
- 高質量的檢索引擎

#### 5. Agent 能力
- 基於 LLM Function Calling 或 ReAct 定義 Agent
- 為 Agent 添加預建或自定義工具
- 提供 50+ 內建工具，如 Google Search、DALL·E、Stable Diffusion 和 WolframAlpha

#### 6. LLMOps
- 監控和分析應用日誌和性能
- 基於生產數據和標註持續改進提示詞、數據集和模型

#### 7. 完整的 API 支持
- 所有功能都提供對應的 RESTful API
- 可輕鬆整合到現有業務邏輯中
- API 端點涵蓋聊天、完成、工作流執行和數據集管理

### 架構優勢

1. **降低系統複雜度**：透過將複雜任務分解為較小的步驟（節點）
2. **減少依賴性**：降低對提示詞技術和模型推理能力的依賴
3. **提高性能**：提升 LLM 應用面對複雜任務的表現
4. **增強可靠性**：提升系統的可解釋性、穩定性和容錯性

### 應用類型

#### 對話流（Chatflow）
- 適用於設計複雜流程的多輪對話場景
- 支持記憶功能，能進行動態應用編排
- 提供問題理解類節點
- 支持對話歷史（Memory）、標註回復、Answer 節點等

#### 工作流（Workflow）
- 適用於自動化、批處理等單輪生成類任務
- 單向生成結果
- 提供豐富的邏輯節點：代碼節點、IF/ELSE 節點、模板轉換、迭代節點等

## 安裝方式

### 方法一：使用 Docker Compose（推薦）

最簡單的啟動 Dify 伺服器的方式是透過 Docker Compose：

```bash
# 克隆倉庫
git clone https://github.com/langgenius/dify.git
cd dify/docker

# 啟動服務
docker-compose up -d

# 訪問 Dify 控制台
# 瀏覽器打開 http://localhost/install 開始初始化過程
```

### 方法二：使用 Dify Cloud

Dify 提供雲端服務，無需任何設置即可試用：
- 訪問：https://dify.ai
- 提供自部署版本的所有功能
- 沙盒計劃包含 200 次免費 GPT-4 調用

### 方法三：本地開發安裝

```bash
# 1. 安裝依賴
pip install dify-client

# 或者使用其他 Python SDK
pip install dify-client-python
pip install dify-oapi

# 2. 設置環境變數
export DIFY_API_KEY="your-api-key"
export DIFY_API_BASE="http://localhost/v1"

# 3. 開始開發
python your_app.py
```

## Python SDK 選項

### 1. dify-client（官方）
```bash
pip install dify-client
```
- 官方 Dify App Service-API 客戶端
- 用於通過請求 Service-API 構建網頁應用
- 支持聊天消息、圖片處理、對話管理

### 2. dify-client-python
```bash
pip install dify-client-python
```
- 提供方便且強大的介面與 Dify API 互動
- 支持同步和異步方法
- 支持串流和非串流端點
- 全面的端點覆蓋：完成、聊天、工作流、反饋、檔案上傳

### 3. dify-oapi
```bash
pip install dify-oapi
```
- 2025 年 10 月 12 日發布
- 用於與 Dify Service-API 互動
- 需要 Python >=3.10

### 4. pydify
```bash
pip install pydify
```
- 輕量級 Python 客戶端庫
- 包含 ChatbotClient 用於對話應用
- TextGenerationClient 用於文字生成任務
- DifySite 管理工具用於自動化平台管理

## 範例檔案說明

本目錄包含 10 個完整的 Python 範例，涵蓋 Dify 的主要功能：

| 檔案 | 說明 | 難度 |
|------|------|------|
| `01_快速開始.py` | 基礎 API 調用和身份驗證 | ⭐ |
| `02_工作流創建.py` | 建立和執行工作流 | ⭐⭐ |
| `03_知識庫管理.py` | 文檔上傳、索引和查詢 | ⭐⭐ |
| `04_對話應用.py` | 多輪對話聊天機器人 | ⭐⭐ |
| `05_Agent應用.py` | 使用工具的自主 Agent | ⭐⭐⭐ |
| `06_數據處理.py` | 數據集批量操作 | ⭐⭐ |
| `07_API集成.py` | 整合外部 API 和服務 | ⭐⭐⭐ |
| `08_多模態.py` | 處理圖片和音頻輸入 | ⭐⭐⭐ |
| `09_部署與監控.py` | 生產環境部署和監控 | ⭐⭐⭐⭐ |
| `10_進階技巧.py` | 高級配置和優化技巧 | ⭐⭐⭐⭐ |

## 快速開始

```python
from dify_client import ChatClient

# 初始化客戶端
client = ChatClient(api_key="your-api-key")

# 創建聊天消息
response = client.create_chat_message(
    inputs={"query": "你好，Dify！"},
    user="user-123",
    response_mode="blocking"
)

print(response['answer'])
```

## 主要 API 端點

### 1. 聊天消息 API
```
POST /v1/chat-messages
```
- 支持串流和阻塞模式
- 可攜帶對話歷史
- 支持文件上傳

### 2. 工作流執行 API
```
POST /v1/workflows/run
```
- 執行定義好的工作流
- 獲取執行結果
- 支持參數傳遞

### 3. 知識庫管理 API
```
POST /v1/datasets
GET /v1/datasets/{dataset_id}
POST /v1/datasets/{dataset_id}/documents
```
- 創建和管理知識庫
- 上傳文檔
- 查詢和檢索

### 4. 應用參數 API
```
GET /v1/parameters
```
- 獲取應用配置
- 查看可用工具和功能

## 最佳實踐

### 1. API Key 管理
```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("DIFY_API_KEY")
```

### 2. 錯誤處理
```python
try:
    response = client.create_chat_message(...)
except Exception as e:
    print(f"錯誤：{e}")
```

### 3. 串流處理
```python
for chunk in client.create_chat_message_stream(...):
    if chunk.event == "message":
        print(chunk.answer, end="")
```

### 4. 對話管理
```python
# 記錄 conversation_id 以維持對話上下文
response = client.create_chat_message(
    inputs={"query": "繼續之前的話題"},
    conversation_id=previous_conversation_id,
    user="user-123"
)
```

## 社群與資源

- **官方網站**：https://dify.ai
- **官方文檔**：https://docs.dify.ai
- **GitHub 倉庫**：https://github.com/langgenius/dify (180,000+ 開發者)
- **中文文檔**：https://docs.dify.ai/zh-hans
- **Discord 社群**：加入 Dify Discord
- **入門教程**：https://dify101.com

## 2025 年新特性

### MCP 協議支持
- 支持基於 HTTP 的 MCP 服務（協議 2025-03-26）
- 預授權和免授權模式
- 將 Dify 構建的工作流或 Agent 轉換為標準 MCP 伺服器

### 插件市場
- Dify v1.0.0 引入 120+ 插件的 Marketplace
- 工作流中的 Agent 節點增強功能
- 豐富的第三方工具整合

### 企業級功能
- 增強的可觀測性和追蹤
- 與 Langfuse 整合進行性能監控
- 更完善的權限管理和團隊協作

## 授權

Dify 採用 Apache 2.0 開源授權，可自由用於商業和個人項目。

## 貢獻

歡迎貢獻代碼、報告問題或提出改進建議。請訪問 GitHub 倉庫參與貢獻。

---

**開始使用 Dify，快速構建您的 AI 應用！**

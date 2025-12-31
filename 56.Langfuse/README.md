# Langfuse - 開源 LLM 可觀測性平台

## 框架簡介

Langfuse 是一個開源的大型語言模型（LLM）可觀測性平台，採用 MIT 許可證。它為 LLM 應用提供完整的追蹤、提示管理和評估功能，幫助開發者監控、調試和優化 AI 應用程序。

### 核心特點

- **🔍 全面追蹤**: 記錄每個 LLM 調用的詳細信息，包括輸入、輸出、延遲和成本
- **📝 提示管理**: 版本化管理提示詞，支持 A/B 測試和快速迭代
- **📊 評估系統**: 內建評分機制，支持人工和自動評估
- **💰 成本追蹤**: 自動計算和追蹤 LLM API 調用成本
- **🔄 OpenTelemetry 支援**: 標準化的追蹤協議整合
- **🤝 框架整合**: 原生支援 LangChain、LlamaIndex 等主流框架
- **🏠 可自託管**: 完全開源，可部署在自己的基礎設施上
- **📈 分析儀表板**: 直觀的 UI 展示應用性能和使用情況

### 主要功能

#### 1. 追蹤與監控
- 完整的請求鏈追蹤
- 多層級 Span 支援
- 實時性能監控
- 錯誤追蹤和調試

#### 2. 提示工程
- 提示詞版本控制
- 集中式提示管理
- 動態提示載入
- A/B 測試支援

#### 3. 評估與分析
- 自定義評分標準
- 人工標註整合
- 自動化評估流程
- 數據集管理

#### 4. 成本優化
- 詳細的成本分析
- 按模型/用戶追蹤
- 預算警報
- 使用趨勢分析

## 安裝指南

### 基本安裝

```bash
# 使用 pip 安裝
pip install langfuse

# 安裝完整依賴
pip install -r requirements.txt
```

### 環境配置

```bash
# 設置 Langfuse 環境變量
export LANGFUSE_PUBLIC_KEY="your-public-key"
export LANGFUSE_SECRET_KEY="your-secret-key"
export LANGFUSE_HOST="https://cloud.langfuse.com"  # 或自託管地址
```

### Docker 自託管

```bash
# 使用 Docker Compose 部署
git clone https://github.com/langfuse/langfuse.git
cd langfuse
docker-compose up -d
```

## 快速開始

### 基本使用示例

```python
from langfuse import Langfuse
from openai import OpenAI

# 初始化 Langfuse 客戶端
langfuse = Langfuse(
    public_key="your-public-key",
    secret_key="your-secret-key",
    host="https://cloud.langfuse.com"
)

# 創建追蹤
trace = langfuse.trace(
    name="chat-completion",
    user_id="user-123",
    metadata={"environment": "production"}
)

# 創建 generation
generation = trace.generation(
    name="openai-call",
    model="gpt-4",
    input={"messages": [{"role": "user", "content": "Hello!"}]}
)

# 調用 OpenAI API
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)

# 結束 generation 並記錄輸出
generation.end(
    output=response.choices[0].message.content,
    usage={
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens
    }
)

print("追蹤已記錄到 Langfuse")
```

### LangChain 整合

```python
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import LangfuseCallbackHandler

# 初始化 Langfuse 回調
handler = LangfuseCallbackHandler(
    public_key="your-public-key",
    secret_key="your-secret-key"
)

# 使用 LangChain
llm = ChatOpenAI(callbacks=[handler])
response = llm.invoke("你好，請介紹一下自己")

print(response.content)
```

### 提示管理

```python
from langfuse import Langfuse

langfuse = Langfuse()

# 從 Langfuse 載入提示
prompt = langfuse.get_prompt("customer-support-v1")

# 使用提示模板
compiled_prompt = prompt.compile(
    customer_name="張三",
    issue="產品無法啟動"
)

print(compiled_prompt)
```

## 使用場景

### 1. 生產監控
- 監控 LLM 應用的健康狀態
- 追蹤 API 調用成本和使用量
- 識別性能瓶頸
- 錯誤檢測和告警

### 2. 開發調試
- 詳細的請求/響應日誌
- 追蹤完整的調用鏈
- 比較不同模型的表現
- 優化提示詞效果

### 3. 質量保證
- 自動化評估流程
- 人工標註和審核
- A/B 測試提示變體
- 回歸測試

### 4. 成本優化
- 識別高成本操作
- 優化 Token 使用
- 選擇性使用不同模型
- 預算控制

### 5. 團隊協作
- 集中管理提示詞
- 版本控制和回滾
- 共享評估數據集
- 統一的可觀測性平台

## 架構組件

### 1. SDK (客戶端)
- Python SDK (官方)
- JavaScript/TypeScript SDK
- OpenTelemetry 整合
- LangChain/LlamaIndex 整合

### 2. 後端服務
- PostgreSQL 數據庫
- Redis 緩存
- ClickHouse (可選，用於分析)
- S3/MinIO (可選，用於存儲)

### 3. Web UI
- Next.js 前端應用
- 實時儀表板
- 追蹤瀏覽器
- 提示管理界面
- 評估工具

## 定價方案

### 免費方案
- 50,000 observations/月
- 無限項目
- 基本分析功能
- 社區支援

### 專業方案
- 從 $59/月起
- 更多 observations
- 高級分析功能
- 優先支援

### 企業方案
- 自訂定價
- 無限 observations
- 專屬支援
- SLA 保證
- 私有部署選項

### 自託管
- 完全免費（MIT 許可證）
- 無使用限制
- 完全數據控制
- 需要自行維護

## 最佳實踐

### 1. 追蹤組織
```python
# 使用層級結構組織追蹤
trace = langfuse.trace(name="user-query")
span1 = trace.span(name="retrieval")
span2 = trace.span(name="generation")
```

### 2. 元數據管理
```python
# 添加豐富的元數據以便分析
trace = langfuse.trace(
    name="chat",
    user_id="user-123",
    session_id="session-456",
    metadata={
        "environment": "production",
        "version": "v2.1.0",
        "feature": "chat-support"
    },
    tags=["support", "urgent"]
)
```

### 3. 成本追蹤
```python
# 準確記錄成本信息
generation.end(
    usage={
        "prompt_tokens": 100,
        "completion_tokens": 50,
        "total_tokens": 150
    },
    model="gpt-4",  # 自動計算成本
)
```

### 4. 評估整合
```python
# 結合評分系統
trace = langfuse.trace(name="qa-system")
# ... 執行操作 ...
trace.score(
    name="accuracy",
    value=0.95,
    comment="高質量回答"
)
```

## 技術規格

- **語言**: Python 3.8+, Node.js 16+
- **數據庫**: PostgreSQL 12+
- **許可證**: MIT
- **GitHub**: https://github.com/langfuse/langfuse
- **文檔**: https://langfuse.com/docs
- **官網**: https://langfuse.com

## 社區與支援

- **Discord**: 活躍的開發者社區
- **GitHub Issues**: 問題追蹤和功能請求
- **文檔**: 詳細的使用指南和 API 參考
- **示例**: 豐富的實際應用案例

## 與其他工具比較

| 功能 | Langfuse | LangSmith | W&B |
|------|----------|-----------|-----|
| 開源 | ✅ MIT | ❌ 閉源 | ❌ 部分開源 |
| 自託管 | ✅ | ❌ | ⚠️ 企業版 |
| 免費額度 | 50K obs | 有限 | 有限 |
| 提示管理 | ✅ | ✅ | ⚠️ |
| 成本追蹤 | ✅ | ✅ | ✅ |
| OpenTelemetry | ✅ | ❌ | ❌ |

## 總結

Langfuse 是一個強大而靈活的 LLM 可觀測性平台，特別適合：

- 需要完全數據控制的企業（可自託管）
- 快速迭代的 AI 產品團隊
- 注重成本優化的項目
- 需要詳細追蹤的複雜 AI 系統

通過本目錄中的示例，你可以學習如何：
- 設置基本追蹤
- 管理和版本化提示詞
- 實施評估系統
- 整合到現有工作流
- 部署到生產環境

開始探索示例文件，構建可觀測、可優化的 LLM 應用！

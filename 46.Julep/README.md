# Julep - AI 應用開發平台

## 框架簡介

Julep 是一個開源平台，專門用於構建、管理和部署 AI 應用程序。它提供了狀態化的對話管理、內建 RAG（檢索增強生成）功能，以及通過 Composio 與 90 多個第三方應用程序的整合能力。

Julep 旨在簡化 AI 應用的開發流程，讓開發者能夠專注於業務邏輯，而不必擔心底層的狀態管理、工具整合和部署問題。

### 主要特點

- **狀態管理**: 自動管理對話狀態和上下文，支持長期記憶
- **內建 RAG**: 原生支持文檔檢索和增強生成
- **90+ 整合**: 通過 Composio 整合 90 多個第三方應用（如 GitHub, Slack, Gmail 等）
- **任務系統**: 強大的任務定義和執行引擎，支持複雜工作流
- **自適應上下文**: 智能管理上下文窗口，優化 token 使用
- **並行執行**: 支持多任務並行處理，提高效率
- **生產就緒**: 內建監控、日誌和部署工具

## 核心功能

### 1. 狀態化對話管理
- 自動保存和恢復對話狀態
- 支持多輪對話和上下文延續
- 靈活的會話管理機制

### 2. 內建 RAG 系統
- 文檔索引和向量存儲
- 智能檢索和上下文注入
- 支持多種文檔格式

### 3. 第三方應用整合
- 通過 Composio 無縫整合 90+ 應用
- 預定義的工具和動作
- 自定義工具擴展

### 4. 任務工作流
- 聲明式任務定義
- 條件分支和循環
- 錯誤處理和重試機制

## 安裝指南

### 環境要求

- Python 3.8+
- pip 或 poetry 包管理器
- OpenAI API 金鑰或其他 LLM 提供商

### 安裝步驟

```bash
# 使用 pip 安裝
pip install julep

# 或使用 poetry
poetry add julep

# 安裝依賴
pip install -r requirements.txt
```

### 環境配置

創建 `.env` 文件並配置 API 金鑰：

```env
JULEP_API_KEY=your_julep_api_key
OPENAI_API_KEY=your_openai_api_key
COMPOSIO_API_KEY=your_composio_api_key  # 可選，用於第三方整合
```

## 快速開始

### 基礎範例

```python
from julep import Client
import os

# 初始化客戶端
client = Client(api_key=os.getenv("JULEP_API_KEY"))

# 創建 Agent
agent = client.agents.create(
    name="助手",
    about="我是一個智能助手，可以幫助你完成各種任務",
    model="gpt-4"
)

# 創建用戶
user = client.users.create(
    name="用戶",
    about="系統用戶"
)

# 創建會話
session = client.sessions.create(
    agent_id=agent.id,
    user_id=user.id
)

# 發送消息
response = client.sessions.chat(
    session_id=session.id,
    messages=[
        {
            "role": "user",
            "content": "你好，請介紹一下你自己"
        }
    ]
)

print(response.choices[0].message.content)
```

### 任務執行範例

```python
from julep import Client

client = Client()

# 定義任務
task = client.tasks.create(
    agent_id=agent.id,
    name="數據分析任務",
    description="分析銷售數據並生成報告",
    main=[
        {
            "prompt": "分析以下銷售數據：{{data}}",
            "unwrap": True
        },
        {
            "tool": "generate_report",
            "arguments": {
                "analysis": "_"  # 使用上一步的輸出
            }
        }
    ]
)

# 執行任務
execution = client.executions.create(
    task_id=task.id,
    input={"data": "Q1銷售數據..."}
)

# 獲取結果
result = client.executions.get(execution.id)
print(result.output)
```

### RAG 範例

```python
from julep import Client

client = Client()

# 創建帶有文檔的 Agent
agent = client.agents.create(
    name="文檔助手",
    model="gpt-4",
    docs=[
        {
            "title": "產品手冊",
            "content": "這是產品使用手冊的內容...",
            "metadata": {"type": "manual", "version": "1.0"}
        }
    ]
)

# 基於文檔回答問題
session = client.sessions.create(agent_id=agent.id)
response = client.sessions.chat(
    session_id=session.id,
    messages=[
        {
            "role": "user",
            "content": "如何使用這個產品？"
        }
    ],
    recall=True  # 啟用文檔檢索
)

print(response.choices[0].message.content)
```

## 使用場景

### 1. 對話系統
- 客戶服務聊天機器人
- 虛擬助手
- 教育輔導系統

### 2. 自動化工作流
- 數據處理和分析
- 報告生成
- 任務調度和執行

### 3. AI 應用
- 知識庫問答
- 文檔分析和摘要
- 智能推薦系統

### 4. 企業整合
- CRM 系統整合
- 項目管理工具整合
- 通訊平台整合

## 目錄結構

```
46.Julep/
├── README.md                 # 本文件
├── requirements.txt          # 依賴列表
├── 01_快速開始.py           # 基礎設置和 Agent 創建
├── 02_對話管理.py           # 狀態化對話管理
├── 03_任務定義.py           # 任務定義和執行
├── 04_工具整合.py           # 與 Composio 的工具整合
├── 05_文檔處理.py           # 文檔處理和 RAG
├── 06_工作流.py             # 多步驟工作流
├── 07_用戶管理.py           # 用戶和會話管理
├── 08_自適應上下文.py       # 自適應上下文管理
├── 09_並行執行.py           # 並行任務執行
└── 10_生產部署.py           # 生產環境部署
```

## 進階主題

### 自定義工具

```python
# 定義自定義工具
custom_tool = {
    "type": "function",
    "function": {
        "name": "calculate",
        "description": "執行數學計算",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {"type": "string"}
            }
        }
    }
}

agent = client.agents.create(
    name="計算助手",
    tools=[custom_tool]
)
```

### 條件工作流

```python
# 創建帶條件的任務
task = client.tasks.create(
    agent_id=agent.id,
    main=[
        {"prompt": "分析數據：{{input}}"},
        {
            "if": "_.sentiment == 'positive'",
            "then": {"prompt": "生成積極回應"},
            "else": {"prompt": "生成建設性反饋"}
        }
    ]
)
```

## 最佳實踐

1. **狀態管理**: 合理使用會話，避免過長的對話歷史
2. **錯誤處理**: 在任務定義中添加錯誤處理邏輯
3. **性能優化**: 使用並行執行提高效率
4. **安全性**: 妥善保管 API 金鑰，使用環境變量
5. **監控**: 在生產環境中啟用日誌和監控

## 資源鏈接

- 官方網站: https://julep.ai
- GitHub 倉庫: https://github.com/julep-ai/julep
- 文檔: https://docs.julep.ai
- Discord 社區: https://discord.gg/julep
- API 參考: https://api.julep.ai/docs

## 許可證

Julep 是開源項目，採用 Apache 2.0 許可證。

## 貢獻

歡迎貢獻代碼、報告問題或提出功能建議。請訪問 GitHub 倉庫了解更多信息。

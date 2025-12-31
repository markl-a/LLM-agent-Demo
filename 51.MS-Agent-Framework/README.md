# Microsoft Agent Framework

## 框架介紹

Microsoft Agent Framework 是微軟於 2025 年 10 月發布的統一 Agent 開發框架,代表了 AutoGen 和 Semantic Kernel 兩大專案的戰略性融合。這個框架本質上是 "Semantic Kernel v2.0",將 AutoGen 的多 Agent 編排能力與 Semantic Kernel 的企業級特性完美結合。

### 背景

- **AutoGen**: 微軟研究院開發的多 Agent 對話框架
- **Semantic Kernel**: 微軟的企業級 LLM 整合框架
- **Agent Framework**: 兩者融合的下一代統一框架

這個統一框架代表了微軟在 AI Agent 領域的戰略整合,為開發者提供了一個全面、強大且易用的解決方案。

## 核心特性

### 1. AutoGen + Semantic Kernel 融合

- **多 Agent 編排**: 繼承 AutoGen 的強大對話編排能力
- **插件系統**: 整合 Semantic Kernel 的插件生態系統
- **記憶管理**: 統一的上下文和狀態管理機制
- **企業級特性**: 完整的監控、日誌和安全性支援

### 2. MCP 協議支援

Model Context Protocol (MCP) 是 Anthropic 提出的標準化協議:

- **標準化整合**: 透過 MCP 連接各種工具和數據源
- **互操作性**: 與其他支援 MCP 的系統無縫整合
- **擴展性**: 輕鬆添加新的外部能力

### 3. A2A (Agent-to-Agent) 通信

- **分散式架構**: Agent 可以跨服務、跨網路通信
- **標準協議**: 基於開放標準的 Agent 通信機制
- **可擴展性**: 支援大規模多 Agent 系統部署

### 4. 線程管理

- **有狀態對話**: 基於線程的對話狀態管理
- **並行處理**: 多個獨立對話線程同時運行
- **持久化**: 長期會話的狀態保存和恢復

### 5. 工作流定義

- **聲明式**: YAML/JSON 格式的工作流定義
- **可視化**: 支援圖形化工作流設計
- **靈活控制**: 條件分支、循環、並行執行

## 安裝指南

### 前置需求

- Python 3.10 或更高版本
- pip 套件管理器

### 安裝步驟

#### 基礎安裝

```bash
pip install agent-framework
```

#### Azure AI 整合

```bash
pip install agent-framework-azure-ai
```

#### 完整安裝

```bash
pip install -r requirements.txt
```

### 環境配置

創建 `.env` 檔案:

```env
# OpenAI API 配置
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4

# Azure OpenAI 配置 (可選)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_azure_api_key
AZURE_OPENAI_DEPLOYMENT=gpt-4

# Azure AI Foundry 配置 (可選)
AZURE_AI_PROJECT_CONNECTION_STRING=your_connection_string
```

## 快速開始

### 基礎範例

```python
from agent_framework import Agent, AgentThread
from agent_framework.models import OpenAIModel

# 創建模型
model = OpenAIModel(model="gpt-4")

# 定義工具
def get_weather(location: str) -> str:
    """獲取指定位置的天氣資訊"""
    return f"{location} 的天氣是晴天,溫度 25°C"

# 創建 Agent
agent = Agent(
    name="weather_assistant",
    model=model,
    tools=[get_weather],
    instructions="你是一個友善的天氣助手,幫助用戶查詢天氣資訊。"
)

# 創建對話線程
thread = AgentThread()

# 執行對話
response = agent.run(
    thread=thread,
    messages="台北今天天氣如何?"
)

print(response.content)
```

### 多 Agent 範例

```python
from agent_framework import Agent, AgentTeam
from agent_framework.patterns import SequentialPattern

# 創建研究員 Agent
researcher = Agent(
    name="researcher",
    instructions="你是一個研究員,負責收集和分析資訊。",
    tools=[search_web, analyze_data]
)

# 創建寫作 Agent
writer = Agent(
    name="writer",
    instructions="你是一個專業作家,負責撰寫報告。",
    tools=[format_text, check_grammar]
)

# 創建 Agent 團隊
team = AgentTeam(
    agents=[researcher, writer],
    pattern=SequentialPattern()  # 順序執行
)

# 執行任務
result = team.run(
    task="研究 AI Agent 的最新發展並撰寫一份報告"
)

print(result)
```

## 使用案例

### 1. 客戶服務系統

多 Agent 協作處理客戶諮詢:

- **接待 Agent**: 初步分類和路由
- **技術支援 Agent**: 處理技術問題
- **銷售 Agent**: 處理產品諮詢
- **升級 Agent**: 處理複雜問題的人工轉接

### 2. 研究與分析

自動化研究流程:

- **資料收集 Agent**: 從多個來源收集資訊
- **分析 Agent**: 分析和提取關鍵見解
- **報告 Agent**: 生成結構化報告
- **審核 Agent**: 檢查品質和準確性

### 3. 軟體開發助手

輔助開發流程:

- **需求分析 Agent**: 理解和細化需求
- **程式碼生成 Agent**: 生成程式碼
- **測試 Agent**: 編寫和執行測試
- **文件 Agent**: 生成技術文件

### 4. 內容創作平台

自動化內容生產:

- **主題研究 Agent**: 研究趨勢和主題
- **大綱 Agent**: 創建內容大綱
- **寫作 Agent**: 撰寫內容
- **編輯 Agent**: 校對和潤色

### 5. 企業工作流自動化

自動化業務流程:

- **資料處理 Agent**: 處理和轉換資料
- **決策 Agent**: 基於規則做出決策
- **通知 Agent**: 發送通知和提醒
- **整合 Agent**: 與企業系統整合

## 核心概念

### Agent

Agent 是框架的基本單位,具有:

- **身份**: 名稱和描述
- **能力**: 工具和函數
- **指令**: 行為指南
- **模型**: 底層 LLM

### Thread

Thread 代表一個對話會話:

- **狀態管理**: 保存對話歷史和上下文
- **並行性**: 多個獨立線程
- **持久化**: 可保存和恢復

### Team

Team 是多個 Agent 的組合:

- **協作模式**: 順序、並行、動態路由
- **共享上下文**: Agent 間資訊共享
- **協調機制**: 任務分配和結果聚合

### Workflow

Workflow 定義複雜的執行流程:

- **步驟定義**: 明確的執行步驟
- **控制流**: 條件、循環、並行
- **錯誤處理**: 異常捕獲和恢復

## 架構優勢

### 1. 統一性

- 單一框架滿足多種需求
- 一致的 API 和概念模型
- 減少學習曲線

### 2. 企業級

- 完整的監控和日誌
- 安全性和合規性支援
- 可擴展的架構設計

### 3. 互操作性

- MCP 協議支援
- 標準化的介面
- 生態系統整合

### 4. 靈活性

- 從簡單到複雜的場景
- 多種編排模式
- 可定製化的行為

## 與其他框架的比較

| 特性 | MS Agent Framework | LangGraph | CrewAI |
|------|-------------------|-----------|---------|
| 多 Agent 支援 | ✅ 原生支援 | ✅ 圖結構 | ✅ 角色導向 |
| 企業級特性 | ✅ 完整 | ⚠️ 部分 | ⚠️ 基礎 |
| MCP 支援 | ✅ 內建 | ❌ 需擴展 | ❌ 不支援 |
| Azure 整合 | ✅ 深度整合 | ⚠️ 基礎 | ⚠️ 基礎 |
| 學習曲線 | 中等 | 較陡 | 較平緩 |
| 社群生態 | 微軟支援 | LangChain | 新興 |

## 最佳實踐

### 1. Agent 設計

- 單一職責:每個 Agent 專注一個明確的任務
- 清晰指令:提供明確、具體的行為指南
- 適當工具:只提供必要的工具和函數

### 2. 工作流設計

- 模組化:將複雜流程分解為可管理的步驟
- 錯誤處理:為每個步驟添加錯誤處理邏輯
- 可觀測性:添加適當的日誌和監控

### 3. 性能優化

- 並行執行:識別可並行的操作
- 快取策略:快取重複的計算結果
- 資源管理:合理分配和釋放資源

### 4. 安全性

- 輸入驗證:驗證所有外部輸入
- 權限控制:實施適當的訪問控制
- 敏感資料:安全處理機密資訊

## 學習資源

### 官方文檔

- [Agent Framework 文檔](https://learn.microsoft.com/en-us/azure/ai-services/agents/)
- [API 參考](https://learn.microsoft.com/en-us/python/api/agent-framework/)
- [範例庫](https://github.com/microsoft/agent-framework-examples)

### 社群資源

- [GitHub 討論區](https://github.com/microsoft/agent-framework/discussions)
- [Stack Overflow 標籤](https://stackoverflow.com/questions/tagged/ms-agent-framework)
- [官方部落格](https://devblogs.microsoft.com/semantic-kernel/)

## 專案結構

```
51.MS-Agent-Framework/
├── README.md                 # 專案說明文檔
├── requirements.txt          # 依賴套件
├── 01_快速開始.py           # 基礎設定和使用
├── 02_Agent創建.py          # 創建和配置 Agent
├── 03_多Agent編排.py        # 多 Agent 協作模式
├── 04_線程管理.py           # 對話線程管理
├── 05_工作流定義.py         # 工作流程定義
├── 06_MCP整合.py            # MCP 協議整合
├── 07_Azure部署.py          # Azure AI Foundry 部署
├── 08_狀態持久化.py         # 狀態保存和恢復
├── 09_人機協作.py           # 人工介入場景
└── 10_生產部署.py           # 生產環境最佳實踐
```

## 版本資訊

- **當前版本**: 1.0.0
- **發布日期**: 2025 年 10 月
- **Python 版本**: 3.10+
- **授權**: MIT License

## 貢獻

歡迎提交問題和改進建議!

## 授權

MIT License - 詳見 LICENSE 檔案

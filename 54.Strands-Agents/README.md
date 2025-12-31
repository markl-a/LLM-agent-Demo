# Strands Agents - AWS 企業級 AI Agent SDK

## 框架簡介

Strands Agents 是 AWS 推出的開源 AI Agent 開發工具包（SDK），採用模型驅動的架構設計方式。這個框架已經在 Amazon Q Developer、AWS Glue 和 VPC Reachability Analyzer 等多個 AWS 生產環境服務中得到驗證和使用。

Strands Agents 提供了一個統一的介面來構建智能代理，支援多種大型語言模型供應商，並與 AWS 生態系統深度整合。它的設計理念是簡化 AI Agent 的開發流程，同時提供企業級的可靠性、可擴展性和可觀測性。

### 核心特性

- **模型驅動架構**: 靈活的模型驅動設計，支援多種 LLM 供應商（Amazon Bedrock、Anthropic、OpenAI 等）
- **企業級可靠性**: 已在多個 AWS 生產環境服務中驗證，提供穩定可靠的性能
- **AWS 深度整合**: 與 Amazon Bedrock、Lambda、CloudWatch 等 AWS 服務無縫整合
- **動態工具註冊**: 支援動態工具定義和註冊，靈活擴展 Agent 能力
- **會話管理**: 內建會話狀態管理和記憶持久化機制
- **多 Agent 協作**: 支援多個 Agent 之間的協同工作和編排
- **可觀測性**: 整合 OpenTelemetry，提供完整的追蹤和監控能力
- **結構化輸出**: 支援結構化數據輸出，確保響應格式的一致性
- **Lambda 部署**: 專為無服務器架構優化，輕鬆部署到 AWS Lambda
- **生產就緒**: 內建錯誤處理、重試機制和日誌記錄功能

## 安裝指南

### 前置需求

- Python 3.9 或更高版本
- AWS 帳戶（用於 Bedrock 和其他 AWS 服務）
- pip 套件管理器

### 使用 pip 安裝

```bash
# 安裝 Strands Agents
pip install strands-agents

# 安裝所有相關依賴
pip install -r requirements.txt
```

### 從源碼安裝

```bash
# 克隆倉庫
git clone https://github.com/awslabs/strands-agents.git
cd strands-agents

# 安裝開發依賴
pip install -e ".[dev]"
```

### AWS 憑證配置

確保已配置 AWS 憑證以使用 Amazon Bedrock：

```bash
# 使用 AWS CLI 配置
aws configure

# 或設置環境變數
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

## 快速開始

以下是一個簡單的示例，展示如何使用 Strands Agents 創建一個基本的 AI Agent：

```python
from strands_agents import Agent, BedrockModel
from strands_agents.tools import tool

# 定義一個工具函數
@tool
def get_weather(city: str) -> str:
    """獲取指定城市的天氣資訊"""
    return f"{city}的天氣：晴朗，溫度 25°C"

# 創建模型配置
model = BedrockModel(
    model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
    region="us-east-1"
)

# 創建 Agent
agent = Agent(
    name="weather_assistant",
    model=model,
    tools=[get_weather],
    system_prompt="你是一個友善的天氣助手，幫助用戶查詢天氣資訊。"
)

# 執行對話
response = agent.run("台北現在的天氣如何？")
print(response.content)
```

## 主要功能

### 1. 工具定義與註冊

Strands Agents 支援靈活的工具定義方式：

```python
from strands_agents.tools import tool, ToolParameter

@tool(
    name="calculate",
    description="執行數學計算",
    parameters=[
        ToolParameter(name="expression", type="string", required=True)
    ]
)
def calculate(expression: str) -> float:
    return eval(expression)
```

### 2. 對話記憶管理

內建多種記憶策略：

```python
from strands_agents.memory import ConversationMemory, WindowMemory

# 使用滑動窗口記憶
memory = WindowMemory(window_size=10)

agent = Agent(
    name="assistant",
    model=model,
    memory=memory
)
```

### 3. 多 Agent 協作

支援複雜的多 Agent 協同工作流：

```python
from strands_agents.orchestration import AgentOrchestrator

orchestrator = AgentOrchestrator(
    agents=[research_agent, writing_agent, review_agent],
    workflow="sequential"
)

result = orchestrator.execute(task="撰寫技術報告")
```

### 4. 可觀測性

整合 OpenTelemetry 提供完整的追蹤：

```python
from strands_agents.observability import configure_tracing

configure_tracing(
    service_name="my-agent",
    endpoint="http://jaeger:4318"
)
```

## 使用案例

### 1. 客戶服務 Agent

構建智能客服系統，處理常見問題和工單管理：

```python
agent = Agent(
    name="customer_service",
    model=model,
    tools=[search_knowledge_base, create_ticket, check_order_status],
    system_prompt="你是客戶服務專員，協助解答問題並處理工單。"
)
```

### 2. 數據分析 Agent

自動化數據分析和報告生成：

```python
agent = Agent(
    name="data_analyst",
    model=model,
    tools=[query_database, generate_chart, create_report],
    system_prompt="你是數據分析專家，負責分析數據並生成報告。"
)
```

### 3. DevOps 自動化

AWS 基礎設施管理和監控：

```python
agent = Agent(
    name="devops_assistant",
    model=model,
    tools=[check_ec2_status, scale_instances, deploy_application],
    system_prompt="你是 DevOps 助手，協助管理 AWS 基礎設施。"
)
```

### 4. 內容生成 Agent

自動化內容創作和多語言翻譯：

```python
agent = Agent(
    name="content_creator",
    model=model,
    tools=[generate_text, translate, optimize_seo],
    system_prompt="你是內容創作專家，協助生成高質量內容。"
)
```

### 5. 研究助手

文獻檢索和知識整合：

```python
agent = Agent(
    name="research_assistant",
    model=model,
    tools=[search_papers, summarize_article, extract_citations],
    system_prompt="你是研究助手，協助文獻檢索和知識整合。"
)
```

## 架構優勢

### 模型驅動設計

Strands Agents 採用模型驅動架構，將業務邏輯與模型實現解耦：

- **靈活性**: 輕鬆切換不同的 LLM 供應商
- **可測試性**: 獨立測試業務邏輯和模型集成
- **可維護性**: 清晰的代碼結構，便於長期維護

### AWS 生態整合

深度整合 AWS 服務生態：

- **Amazon Bedrock**: 直接訪問多種基礎模型
- **AWS Lambda**: 無服務器部署，按需擴展
- **CloudWatch**: 完整的日誌和監控
- **DynamoDB**: 會話狀態持久化
- **S3**: 大型文件存儲和檢索

### 企業級特性

滿足企業應用的各項需求：

- **安全性**: 支援 IAM 角色和策略
- **合規性**: 符合 AWS 安全最佳實踐
- **可擴展性**: 支援大規模並發請求
- **成本優化**: 靈活的定價模型

## 項目結構

```
54.Strands-Agents/
├── README.md                # 項目說明文件
├── requirements.txt         # 依賴套件清單
├── 01_快速開始.py          # 基礎設置示例
├── 02_工具定義.py          # 工具定義和註冊
├── 03_對話記憶.py          # 記憶管理
├── 04_Bedrock整合.py       # Bedrock 集成
├── 05_多Agent協作.py       # 多 Agent 協同
├── 06_Session管理.py       # 會話狀態管理
├── 07_Lambda部署.py        # Lambda 部署
├── 08_可觀測性.py          # 追蹤和監控
├── 09_結構化輸出.py        # 結構化輸出
└── 10_生產部署.py          # 生產環境部署
```

## 學習資源

### 官方文檔

- [Strands Agents GitHub](https://github.com/awslabs/strands-agents)
- [Amazon Bedrock 文檔](https://docs.aws.amazon.com/bedrock/)
- [AWS Lambda 開發指南](https://docs.aws.amazon.com/lambda/)

### 範例代碼

本目錄包含 10 個完整的示例，涵蓋從基礎到進階的各種使用場景。建議按順序學習：

1. **01_快速開始.py** - 了解基本概念和設置
2. **02_工具定義.py** - 學習如何定義和註冊工具
3. **03_對話記憶.py** - 掌握記憶管理策略
4. **04_Bedrock整合.py** - 集成 Amazon Bedrock
5. **05_多Agent協作.py** - 實現複雜的協作流程
6. **06_Session管理.py** - 管理會話狀態
7. **07_Lambda部署.py** - 部署到無服務器環境
8. **08_可觀測性.py** - 實施監控和追蹤
9. **09_結構化輸出.py** - 處理結構化數據
10. **10_生產部署.py** - 完整的生產部署方案

## 最佳實踐

### 1. 工具設計

- 保持工具函數的單一職責
- 提供清晰的描述和參數說明
- 實現適當的錯誤處理
- 考慮性能和超時設置

### 2. 提示詞工程

- 編寫明確的系統提示詞
- 提供具體的任務指導
- 包含示例和格式要求
- 定期優化和測試

### 3. 記憶管理

- 選擇合適的記憶策略
- 定期清理過期數據
- 考慮成本和性能平衡
- 實施數據隱私保護

### 4. 可觀測性

- 啟用完整的追蹤
- 設置適當的日誌級別
- 監控關鍵指標
- 建立告警機制

### 5. 安全性

- 使用 IAM 角色而非憑證
- 實施最小權限原則
- 加密敏感數據
- 定期安全審計

## 常見問題

### Q: Strands Agents 與其他 Agent 框架有何不同？

A: Strands Agents 專為 AWS 生態系統設計，已在多個 AWS 生產服務中驗證，提供企業級的可靠性和性能。它與 AWS 服務深度整合，特別適合已使用 AWS 的團隊。

### Q: 支援哪些 LLM 模型？

A: 支援 Amazon Bedrock 上的所有模型（包括 Claude、Llama、Titan 等），以及通過適配器支援 OpenAI、Anthropic 等其他供應商的模型。

### Q: 如何處理成本控制？

A: 可以通過設置最大 token 數、實施緩存策略、選擇合適的模型等方式控制成本。建議使用 CloudWatch 監控使用情況。

### Q: 是否支援本地部署？

A: 主要設計用於 AWS 雲端環境，但也可以在本地開發和測試。生產環境建議使用 AWS 以獲得最佳性能。

## 貢獻指南

歡迎提交問題報告、功能建議或代碼貢獻：

1. Fork 項目倉庫
2. 創建特性分支
3. 提交更改
4. 推送到分支
5. 創建 Pull Request

## 授權協議

本項目採用 Apache 2.0 授權協議。詳見 [LICENSE](https://github.com/awslabs/strands-agents/blob/main/LICENSE) 文件。

## 聯繫方式

- GitHub Issues: [提交問題](https://github.com/awslabs/strands-agents/issues)
- AWS Support: [AWS 支援中心](https://aws.amazon.com/support/)
- 社區論壇: [AWS Developer Forums](https://forums.aws.amazon.com/)

## 更新日誌

### v1.0.0 (2025-01)

- 首次正式發布
- 支援 Amazon Bedrock 整合
- 多 Agent 協作功能
- OpenTelemetry 可觀測性
- AWS Lambda 部署支援
- 生產環境優化

---

開始使用 Strands Agents，構建下一代企業級 AI Agent 應用！

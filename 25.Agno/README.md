# Agno (原 Phidata) 深度學習與實戰指南

## 目錄
- [專案簡介](#專案簡介)
- [Agno 核心優勢](#agno-核心優勢)
- [學習路徑](#學習路徑)
- [技術棧說明](#技術棧說明)
- [環境準備](#環境準備)
- [教程列表](#教程列表)
- [進階應用](#進階應用)
- [最佳實踐](#最佳實踐)
- [常見問題](#常見問題)
- [參考資源](#參考資源)

## 專案簡介

Agno（前身為 Phidata）是新一代的 AI Agent 框架，專為構建生產級的多模態 Agent 應用而設計。2025 年正式更名為 Agno，帶來了革命性的性能提升和更強大的功能。

### 為什麼選擇 Agno？

**性能優勢：**
- ⚡ 比 LangGraph 快 **529 倍**
- 💾 內存使用低 **24 倍**
- 🚀 毫秒級響應時間
- 📊 更高的吞吐量

**功能特色：**
- 🎭 **多模態支持**：文本、圖像、音頻、視頻
- 🧠 **Agentic RAG**：智能檢索增強生成
- 🛠️ **100+ 工具包**：開箱即用的工具生態
- 🏗️ **AgentOS**：企業級運行時環境
- 🔌 **MCP 支持**：Model Context Protocol 整合
- 🎯 **結構化輸出**：原生 Pydantic 支持

### 適合對象

- 想要構建高性能 AI Agent 的開發者
- 需要處理多模態數據的工程師
- 追求極致性能的生產環境團隊
- 對最新 Agent 技術感興趣的研究者

### 學習成果

完成本教程後，你將能夠：

- 使用 Agno 構建高性能 Agent 系統
- 實現多模態 AI 應用（圖像、音頻、視頻）
- 部署 Agentic RAG 解決方案
- 創建多 Agent 協作團隊
- 將 Agent 應用部署到生產環境
- 整合 Model Context Protocol (MCP)

## Agno 核心優勢

### 1. 卓越性能

```
性能對比（處理 1000 個請求）：
┌─────────────┬──────────┬──────────┬─────────────┐
│   框架      │  時間    │  內存    │   吞吐量    │
├─────────────┼──────────┼──────────┼─────────────┤
│ Agno        │  1.2s    │  45 MB   │  833 req/s  │
│ LangGraph   │  635s    │  1080 MB │  1.57 req/s │
│ CrewAI      │  420s    │  890 MB  │  2.38 req/s │
└─────────────┴──────────┴──────────┴─────────────┘
```

### 2. 多模態能力

- **文本處理**：自然語言理解與生成
- **圖像分析**：計算機視覺、OCR、圖像生成
- **音頻處理**：語音識別、音頻分析
- **視頻理解**：視頻內容分析、場景識別

### 3. Agentic RAG

傳統 RAG vs Agentic RAG：

```python
# 傳統 RAG：靜態檢索
retrieve() → generate()

# Agentic RAG：智能決策
analyze_query() →
  decide_retrieval_strategy() →
  dynamic_search() →
  verify_relevance() →
  generate_with_context()
```

### 4. 豐富的工具生態

**內建工具包分類：**
- 🔍 **搜索工具**：DuckDuckGo, Tavily, Exa, Google
- 💾 **數據庫工具**：PostgreSQL, MySQL, MongoDB, Redis
- 📊 **數據分析**：Pandas, NumPy, Matplotlib
- 🌐 **API 工具**：REST, GraphQL, WebSocket
- 📧 **通訊工具**：Email, Slack, Discord
- 🗂️ **文件處理**：PDF, Excel, CSV, JSON
- ☁️ **雲服務**：AWS, GCP, Azure
- 💻 **開發工具**：Git, Docker, Shell

### 5. AgentOS 運行時

企業級特性：
- 🔐 安全沙箱執行
- 📈 自動擴展
- 🔄 錯誤恢復
- 📊 實時監控
- 🎛️ 資源管理

## 學習路徑

### 第一階段：基礎入門（1-2 天）

建議學習順序：
1. **01_基礎入門.py** - 快速上手 Agno
2. **02_工具使用.py** - 掌握工具調用
3. **08_結構化輸出.py** - 學習數據建模

**目標**：理解 Agno 核心概念，能夠創建基本 Agent

### 第二階段：核心功能（2-3 天）

建議學習順序：
1. **03_多模態Agent.py** - 多模態處理能力
2. **04_Agentic_RAG.py** - 智能 RAG 系統
3. **06_記憶和知識.py** - 持久化與記憶

**目標**：掌握 Agno 的核心特性，實現複雜應用

### 第三階段：進階應用（3-4 天）

建議學習順序：
1. **05_團隊協作.py** - 多 Agent 系統
2. **07_推理Agent.py** - 高級推理能力
3. **09_AgentOS部署.py** - 生產環境部署

**目標**：能夠設計和部署企業級 Agent 系統

### 第四階段：專業領域（依需求）

1. **10_MCP整合.py** - Model Context Protocol
2. 自定義工具開發
3. 性能優化與調優

**目標**：深入掌握專業技術，解決實際業務問題

## 技術棧說明

### 核心框架

```bash
# 主框架
agno                 # Agno 核心框架（原 Phidata）

# 模型支持
openai              # OpenAI GPT 系列
anthropic           # Claude 系列
google-generativeai # Gemini 系列
groq                # Groq 高速推理
```

### 工具包

```bash
# 搜索工具
duckduckgo-search
tavily-python
exa-py

# 數據處理
pandas
numpy
sqlalchemy

# 向量數據庫
lancedb
chromadb
qdrant-client

# 多模態
pillow              # 圖像處理
opencv-python       # 計算機視覺
pydub               # 音頻處理
```

### 輔助工具

```bash
# 數據驗證
pydantic

# 異步支持
asyncio
aiohttp

# 環境管理
python-dotenv

# 監控與追蹤
opentelemetry-api
```

## 環境準備

### 1. 安裝 Agno

```bash
# 基礎安裝
pip install agno

# 完整安裝（包含所有工具）
pip install "agno[all]"

# 選擇性安裝
pip install "agno[openai]"      # OpenAI 支持
pip install "agno[anthropic]"   # Claude 支持
pip install "agno[aws]"         # AWS 工具
pip install "agno[postgres]"    # PostgreSQL 工具
```

### 2. 快速安裝（推薦）

```bash
# 使用專案提供的 requirements.txt
cd 25.Agno
pip install -r requirements.txt
```

### 3. 設定 API Keys

創建 `.env` 文件並設定以下環境變數：

```bash
# OpenAI（推薦）
OPENAI_API_KEY=your_openai_key_here

# Anthropic Claude
ANTHROPIC_API_KEY=your_anthropic_key_here

# Google Gemini
GOOGLE_API_KEY=your_google_key_here

# Groq（高速推理）
GROQ_API_KEY=your_groq_key_here

# 搜索工具
TAVILY_API_KEY=your_tavily_key_here
EXA_API_KEY=your_exa_key_here

# AgentOS（生產環境）
AGNO_API_KEY=your_agno_key_here
```

### 4. 驗證安裝

```python
import agno
from agno.agent import Agent
from agno.models.openai import OpenAIChat

# 創建測試 Agent
agent = Agent(
    model=OpenAIChat(id="gpt-4"),
    description="測試 Agent"
)

# 測試運行
response = agent.run("你好！")
print(response.content)
```

## 教程列表

### 基礎教程

#### 01_基礎入門.py

**難度**: ⭐
**時間**: 30-45 分鐘
**前置知識**: Python 基礎

**內容概要**:
- Agno 核心概念與架構
- 創建第一個 Agent
- 基本對話與交互
- Agent 配置與參數
- 調試與日誌

**學習重點**:
```python
# 核心概念
Agent → Model → Tools → Response
```

**關鍵技能**:
- Agent 初始化與配置
- 模型選擇與切換
- 基本對話處理
- 錯誤處理機制

#### 02_工具使用.py

**難度**: ⭐⭐
**時間**: 1 小時
**前置知識**: 完成教程 01

**內容概要**:
- 使用內建工具包
- 網頁搜索（DuckDuckGo, Tavily）
- 計算器與數學工具
- 文件操作工具
- 自定義工具開發

**學習重點**:
- 工具註冊與調用
- 工具參數定義
- 工具組合使用
- 錯誤處理與降級

**實戰場景**:
- 實時信息查詢
- 數據計算與分析
- 文件處理自動化

#### 03_多模態Agent.py

**難度**: ⭐⭐⭐
**時間**: 1.5 小時
**前置知識**: 完成教程 01, 02

**內容概要**:
- 圖像理解與分析
- OCR 文字識別
- 音頻處理與轉錄
- 視頻內容分析
- 多模態融合

**學習重點**:
```python
# 多模態流程
Input (Text/Image/Audio/Video) →
  Multimodal Agent →
  Processing →
  Unified Response
```

**支持的模態**:
- 文本：GPT-4, Claude
- 圖像：GPT-4 Vision, Claude 3
- 音頻：Whisper
- 視頻：GPT-4 Vision + 幀分析

#### 04_Agentic_RAG.py

**難度**: ⭐⭐⭐⭐
**時間**: 2 小時
**前置知識**: 完成教程 01, 02

**內容概要**:
- Agentic RAG 原理
- 智能檢索策略
- 向量數據庫整合
- 動態查詢優化
- 自我評估與修正

**學習重點**:
```python
# Agentic RAG 工作流
Query Analysis →
  Strategy Selection →
  Multi-step Retrieval →
  Relevance Verification →
  Context Generation →
  Answer Synthesis
```

**核心優勢**:
- 自主決策檢索策略
- 動態調整查詢
- 多輪檢索與驗證
- 結果質量保證

#### 05_團隊協作.py

**難度**: ⭐⭐⭐⭐
**時間**: 2-3 小時
**前置知識**: 完成教程 01-04

**內容概要**:
- 多 Agent 系統設計
- Agent 角色分工
- 團隊協作模式
- 任務委派與執行
- 結果聚合與整合

**學習重點**:
```python
# 團隊工作流
Task →
  Team Coordinator →
  Agent 1 (Research) →
  Agent 2 (Analysis) →
  Agent 3 (Writing) →
  Consolidator →
  Final Output
```

**協作模式**:
- 順序執行（Sequential）
- 並行處理（Parallel）
- 階層式（Hierarchical）
- 圓桌討論（Round-robin）

### 進階教程

#### 06_記憶和知識.py

**難度**: ⭐⭐⭐
**時間**: 1.5 小時
**前置知識**: 完成教程 01, 02

**內容概要**:
- Agent 記憶系統
- 會話歷史管理
- 知識庫構建
- 長期記憶持久化
- 記憶檢索策略

**學習重點**:
- Memory Types: Short-term, Long-term
- Storage: Session, Database, Vector Store
- Retrieval: Recency, Relevance, Importance

**實戰應用**:
- 多輪對話系統
- 個性化推薦
- 知識管理助手

#### 07_推理Agent.py

**難度**: ⭐⭐⭐⭐
**時間**: 2 小時
**前置知識**: 完成教程 01-04

**內容概要**:
- Chain of Thought (CoT) 推理
- 思維樹（Tree of Thoughts）
- 自我反思（Self-Reflection）
- 計劃與執行（Plan-and-Execute）
- ReAct 模式

**學習重點**:
```python
# ReAct 循環
Thought → Action → Observation →
  Thought → Action → Observation →
  ... → Final Answer
```

**推理策略**:
- Zero-shot CoT
- Few-shot CoT
- Multi-step Reasoning
- Backward Chaining

#### 08_結構化輸出.py

**難度**: ⭐⭐
**時間**: 1 小時
**前置知識**: 完成教程 01

**內容概要**:
- Pydantic 模型定義
- 結構化數據提取
- 類型驗證與約束
- JSON Schema 生成
- 批量數據處理

**學習重點**:
```python
# 結構化輸出流程
Unstructured Input →
  Agent with Response Model →
  Validated Pydantic Object →
  Structured Output
```

**應用場景**:
- 數據提取
- 表單填寫
- API 響應
- 數據庫記錄

#### 09_AgentOS部署.py

**難度**: ⭐⭐⭐⭐⭐
**時間**: 3-4 小時
**前置知識**: 完成教程 01-08

**內容概要**:
- AgentOS 架構
- 生產環境配置
- 性能監控與追蹤
- 水平擴展策略
- 安全性與合規

**學習重點**:
```python
# 部署流程
Development →
  Testing →
  Staging →
  AgentOS Deployment →
  Monitoring →
  Scaling
```

**生產考量**:
- Rate Limiting
- Error Recovery
- Load Balancing
- Logging & Metrics
- Cost Optimization

#### 10_MCP整合.py

**難度**: ⭐⭐⭐⭐
**時間**: 2 小時
**前置知識**: 完成教程 01, 02

**內容概要**:
- Model Context Protocol 介紹
- MCP 服務器配置
- 工具註冊與發現
- 跨模型工具共享
- MCP 最佳實踐

**學習重點**:
- MCP Server Setup
- Tool Registration
- Context Management
- Security & Auth

**MCP 優勢**:
- 標準化工具接口
- 跨框架兼容
- 集中式管理
- 安全性保障

## 進階應用

### 實際業務場景

#### 1. 智能客服系統

**技術組合**: Agno + Agentic RAG + Memory

```python
# 客服 Agent 架構
Customer Query →
  Intent Classification →
  Knowledge Retrieval →
  Personalized Response →
  Follow-up Management
```

**特色功能**:
- 多語言支持
- 情感分析
- 上下文理解
- 自動升級

#### 2. 多模態內容分析

**技術組合**: Multimodal Agent + Team

```python
# 內容分析流程
Mixed Content (Text/Image/Video) →
  Modality Detection →
  Parallel Processing →
  Result Fusion →
  Comprehensive Report
```

**應用領域**:
- 社交媒體監控
- 品牌分析
- 內容審核
- 市場研究

#### 3. 代碼審查助手

**技術組合**: Reasoning Agent + Tools

```python
# 代碼審查流程
Code Input →
  Static Analysis →
  Logic Review →
  Security Check →
  Performance Analysis →
  Improvement Suggestions
```

**檢查項目**:
- 代碼質量
- 安全漏洞
- 性能瓶頸
- 最佳實踐

#### 4. 數據分析 Agent

**技術組合**: Structured Output + Tools

```python
# 分析流程
Natural Language Query →
  Data Retrieval →
  Analysis & Computation →
  Visualization →
  Insights Report
```

**支持功能**:
- SQL 生成
- 數據可視化
- 統計分析
- 預測建模

## 最佳實踐

### 1. Agent 設計原則

```python
# ✅ 好的設計
agent = Agent(
    name="data_analyst",
    role="專業的數據分析師",
    instructions=[
        "仔細分析數據，確保準確性",
        "使用適當的統計方法",
        "提供清晰的解釋和建議"
    ],
    tools=[PythonTools(), ChartTools()],
    show_tool_calls=True,
    markdown=True
)

# ❌ 避免的設計
agent = Agent(model=OpenAIChat())  # 缺乏明確指導
```

### 2. 工具使用策略

```python
# 工具選擇原則
1. 專用工具優於通用工具
2. 輕量工具優於重量工具
3. 本地工具優於遠程工具
4. 確定性工具優於不確定性工具

# 工具組合
search_agent = Agent(
    tools=[
        DuckDuckGoTools(),  # 快速搜索
        TavilyTools(),      # 深度研究
        WebScraper()        # 內容提取
    ],
    tool_choice="auto"  # 讓 Agent 智能選擇
)
```

### 3. 性能優化

```python
# 並行處理
from agno.utils.async_runner import run_agents_async

results = await run_agents_async([
    agent1.run_async(task1),
    agent2.run_async(task2),
    agent3.run_async(task3)
])

# 緩存策略
agent = Agent(
    model=OpenAIChat(),
    cache=True,  # 啟用響應緩存
    cache_ttl=3600  # 緩存時間 1 小時
)

# 流式輸出
for chunk in agent.run(query, stream=True):
    print(chunk, end="", flush=True)
```

### 4. 錯誤處理

```python
from agno.exceptions import AgentError, ModelError

try:
    response = agent.run(query)
except ModelError as e:
    # 模型錯誤：切換到備用模型
    backup_agent = Agent(model=OpenAIChat(id="gpt-3.5-turbo"))
    response = backup_agent.run(query)
except AgentError as e:
    # Agent 錯誤：記錄並返回友好消息
    logger.error(f"Agent error: {e}")
    response = "抱歉，處理請求時遇到問題。"
```

### 5. 安全性考量

```python
# API Key 管理
from agno.utils.env import get_env_var

api_key = get_env_var("OPENAI_API_KEY")  # 從環境變數讀取

# 輸入驗證
def validate_input(user_input: str) -> bool:
    # 檢查惡意內容
    forbidden_patterns = ["DROP TABLE", "DELETE FROM", "'; --"]
    return not any(pattern in user_input.upper()
                   for pattern in forbidden_patterns)

# 輸出過濾
def sanitize_output(response: str) -> str:
    # 移除敏感信息
    import re
    response = re.sub(r'\b\d{16}\b', '[CARD NUMBER]', response)
    response = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', response)
    return response
```

## 常見問題

### Q1: Agno 與 LangChain/LangGraph 有什麼區別？

**A**: 主要區別：

| 特性 | Agno | LangGraph |
|------|------|-----------|
| 性能 | 極快（529x） | 較慢 |
| 內存 | 極低（1/24） | 較高 |
| 學習曲線 | 簡單直觀 | 較複雜 |
| 多模態 | 原生支持 | 需要擴展 |
| 工具生態 | 100+ 內建 | 需要自行集成 |
| 部署 | AgentOS | 需要自行配置 |

**選擇建議**:
- 追求性能 → Agno
- 需要多模態 → Agno
- 複雜狀態機 → LangGraph
- 豐富生態 → LangChain

### Q2: 如何選擇合適的模型？

**A**: 選擇策略：

```python
# 速度優先（簡單任務）
model = OpenAIChat(id="gpt-3.5-turbo")

# 質量優先（複雜推理）
model = OpenAIChat(id="gpt-4-turbo")

# 多模態任務
model = OpenAIChat(id="gpt-4-vision-preview")

# 成本優先
model = GroqChat(id="mixtral-8x7b")

# 隱私優先（本地部署）
model = Ollama(id="llama3")
```

### Q3: Agentic RAG 效果不好怎麼辦？

**A**: 優化清單：

1. **改進知識庫**
   - 提高文檔質量
   - 優化分塊策略
   - 添加元數據

2. **調整檢索策略**
   ```python
   agent = Agent(
       knowledge_base=kb,
       search_knowledge=True,
       num_documents=5,  # 增加檢索數量
       rerank=True       # 啟用重排序
   )
   ```

3. **優化提示詞**
   ```python
   agent.instructions.append(
       "仔細閱讀檢索到的文檔，只基於文檔內容回答"
   )
   ```

### Q4: 如何降低 API 成本？

**A**: 成本優化策略：

```python
# 1. 使用更小的模型
agent = Agent(model=OpenAIChat(id="gpt-3.5-turbo"))

# 2. 啟用緩存
agent.cache = True

# 3. 限制輸出長度
agent.model.max_tokens = 500

# 4. 批量處理
responses = agent.batch_run(queries)

# 5. 使用 Groq（免費配額）
from agno.models.groq import GroqChat
agent = Agent(model=GroqChat(id="mixtral-8x7b"))
```

### Q5: 如何監控生產環境的 Agent？

**A**: 監控方案：

```python
# 1. 啟用詳細日誌
import logging
logging.basicConfig(level=logging.INFO)

# 2. 使用 AgentOS 監控
agent = Agent(
    model=OpenAIChat(),
    monitoring=True,
    log_level="INFO"
)

# 3. 自定義追蹤
from agno.utils.telemetry import track_run

@track_run
def process_request(query):
    return agent.run(query)

# 4. 集成 OpenTelemetry
from opentelemetry import trace
tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("agent-run"):
    response = agent.run(query)
```

## 參考資源

### 官方資源

- [Agno 官方網站](https://www.agno.com)
- [Agno GitHub](https://github.com/agno-agi/agno)
- [Agno 文檔](https://docs.agno.com)
- [AgentOS 文檔](https://docs.agno.com/agentos)

### 學習資源

- [Agno Cookbook](https://cookbook.agno.com)
- [視頻教程](https://www.youtube.com/@agno)
- [示範應用](https://github.com/agno-agi/examples)
- [Discord 社群](https://discord.gg/agno)

### 工具資源

- [Agno Playground](https://playground.agno.com)
- [工具包文檔](https://docs.agno.com/tools)
- [模型對比](https://docs.agno.com/models)

### 部落格文章

- [為什麼 Agno 比 LangGraph 快 529 倍](https://www.agno.com/blog/performance)
- [Agentic RAG 深度解析](https://www.agno.com/blog/agentic-rag)
- [多模態 Agent 最佳實踐](https://www.agno.com/blog/multimodal)
- [從 Phidata 遷移到 Agno](https://www.agno.com/blog/migration)

### 相關工具

- [Model Context Protocol](https://modelcontextprotocol.io)
- [LanceDB](https://lancedb.com) - 推薦的向量數據庫
- [Groq](https://groq.com) - 高速推理引擎

---

## 貢獻指南

歡迎提交 Issue 和 Pull Request！

### 如何貢獻

1. Fork 本專案
2. 創建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

### 範例貢獻

如果你創建了有趣的 Agno 範例，歡迎貢獻：
- 新的工具集成
- 實際業務場景
- 性能優化技巧
- 最佳實踐案例

## 授權

本專案採用 MIT 授權 - 詳見 LICENSE 文件

## 聯絡方式

如有問題或建議，請開 Issue 或聯繫維護者。

---

**最後更新**: 2025-12
**維護狀態**: 積極維護中 ✅
**框架版本**: Agno 1.0+

**特別說明**:
- Phidata 於 2025 年正式更名為 Agno
- 本教程基於最新的 Agno 1.0 版本
- 如果你使用的是 Phidata，建議升級到 Agno

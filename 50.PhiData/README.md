# PhiData (Agno) - 多模態 AI Agent 框架

## 框架簡介

PhiData（現品牌為 Agno）是一個開源的多模態、多 Agent AI 系統框架，專為構建高性能的 AI 應用而設計。它提供了簡潔的 API 和強大的功能，讓開發者能夠快速構建生產級的 AI Agent 系統。

PhiData 的核心理念是將 AI Agent 視為軟體工程的一部分，提供模塊化、可測試、可部署的解決方案。

## 主要特性

### 🚀 高性能架構
- **異步處理**: 支持異步任務處理，提高系統吞吐量
- **流式輸出**: 實時流式響應，提升用戶體驗
- **並行執行**: 多 Agent 並行工作，提高效率
- **智能緩存**: 減少重複計算，降低成本

### 🎯 多模態支持
- **文本處理**: 支持各種文本理解和生成任務
- **圖像分析**: 集成視覺模型，處理圖像相關任務
- **音頻處理**: 支持語音識別和合成
- **文檔解析**: 處理 PDF、Word 等多種文檔格式

### 👥 多 Agent 協作
- **Agent 團隊**: 構建多個專業 Agent 協同工作
- **任務分配**: 智能分配任務給最適合的 Agent
- **狀態共享**: Agent 之間共享上下文和狀態
- **工作流編排**: 靈活定義 Agent 協作流程

### 📚 知識庫集成
- **向量數據庫**: 支持多種向量數據庫（Pinecone、Qdrant、Chroma 等）
- **RAG 模式**: 內建檢索增強生成支持
- **文檔索引**: 自動化文檔處理和索引
- **語義搜索**: 高效的語義檢索功能

### 🛠️ 豐富的工具生態
- **網頁搜索**: DuckDuckGo、Google 搜索集成
- **數據分析**: Python 代碼執行、數據可視化
- **API 調用**: 輕鬆集成外部 API
- **自定義工具**: 簡單的工具擴展機制

### 🔒 企業級功能
- **安全性**: 內建安全機制，保護敏感數據
- **可觀測性**: 完整的日誌和監控支持
- **可擴展性**: 支持水平擴展和負載均衡
- **版本管理**: Agent 版本控制和 A/B 測試

## 安裝指南

### 基礎安裝

```bash
pip install phidata
```

### 完整安裝（包含所有依賴）

```bash
pip install -r requirements.txt
```

### 環境變量配置

創建 `.env` 文件：

```env
# OpenAI API 配置
OPENAI_API_KEY=your_openai_api_key

# Anthropic API 配置（可選）
ANTHROPIC_API_KEY=your_anthropic_api_key

# 向量數據庫配置（可選）
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_environment

# 其他配置
PHI_API_KEY=your_phi_api_key  # 用於監控和追蹤
```

## 快速開始

### 基礎 Agent 示例

```python
from phi.agent import Agent
from phi.model.openai import OpenAIChat

# 創建一個簡單的 Agent
agent = Agent(
    model=OpenAIChat(id="gpt-4"),
    description="一個友好的助手",
    instructions=["提供清晰、準確的回答", "使用中文回應"],
    markdown=True,
)

# 運行 Agent
agent.print_response("什麼是人工智能？")
```

### 帶工具的 Agent

```python
from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.tools.duckduckgo import DuckDuckGo

# 創建帶搜索功能的 Agent
search_agent = Agent(
    model=OpenAIChat(id="gpt-4"),
    tools=[DuckDuckGo()],
    description="網頁搜索助手",
    instructions=["搜索最新信息", "提供可靠來源"],
    show_tool_calls=True,
    markdown=True,
)

# 使用搜索功能
search_agent.print_response("2024年AI領域的最新進展")
```

### RAG Agent 示例

```python
from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.knowledge.pdf import PDFKnowledgeBase
from phi.vectordb.pgvector import PgVector

# 創建知識庫
knowledge_base = PDFKnowledgeBase(
    path="data/documents",
    vector_db=PgVector(
        table_name="pdf_documents",
        db_url="postgresql://localhost:5432/ai_db",
    ),
)

# 創建 RAG Agent
rag_agent = Agent(
    model=OpenAIChat(id="gpt-4"),
    knowledge_base=knowledge_base,
    description="文檔問答助手",
    instructions=["基於文檔內容回答", "引用相關段落"],
    search_knowledge=True,
    markdown=True,
)

# 載入知識庫
knowledge_base.load(recreate=False)

# 問答
rag_agent.print_response("文檔中提到了哪些重點？")
```

### 多 Agent 團隊

```python
from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.yfinance import YFinanceTools

# 研究員 Agent
researcher = Agent(
    name="研究員",
    role="研究最新信息",
    model=OpenAIChat(id="gpt-4"),
    tools=[DuckDuckGo()],
    instructions=["搜索相關信息", "提供詳細資料"],
)

# 分析師 Agent
analyst = Agent(
    name="分析師",
    role="分析數據和趨勢",
    model=OpenAIChat(id="gpt-4"),
    tools=[YFinanceTools()],
    instructions=["分析數據", "提供洞察"],
)

# 作家 Agent
writer = Agent(
    name="作家",
    role="撰寫報告",
    model=OpenAIChat(id="gpt-4"),
    instructions=["整合信息", "撰寫專業報告"],
)

# 團隊協作
team_leader = Agent(
    name="團隊領導",
    model=OpenAIChat(id="gpt-4"),
    team=[researcher, analyst, writer],
    instructions=["協調團隊工作", "確保任務完成"],
    markdown=True,
)

# 執行團隊任務
team_leader.print_response("分析特斯拉公司的最新發展和股價趨勢")
```

## 核心概念

### Agent 組件

1. **Model**: AI 模型（OpenAI、Anthropic、Local 模型等）
2. **Tools**: Agent 可以使用的工具
3. **Knowledge Base**: 知識庫，用於 RAG
4. **Memory**: 記憶系統，保持對話上下文
5. **Storage**: 持久化存儲

### 工具系統

PhiData 提供豐富的內建工具：

- **搜索工具**: DuckDuckGo、Google、Bing
- **金融工具**: YFinance、Alpha Vantage
- **數據庫工具**: SQL、MongoDB
- **文件工具**: PDF、CSV、JSON
- **API 工具**: HTTP 客戶端
- **代碼執行**: Python、Shell

### 知識庫類型

- **PDF**: PDF 文檔知識庫
- **網頁**: 網頁內容知識庫
- **文本**: 純文本知識庫
- **JSON**: 結構化數據知識庫
- **CSV**: 表格數據知識庫

## 使用場景

### 1. 智能客服系統
利用多 Agent 協作處理客戶查詢，提供個性化服務。

### 2. 文檔問答系統
基於企業內部文檔構建知識庫，提供精準問答。

### 3. 金融分析助手
整合實時金融數據，提供市場分析和投資建議。

### 4. 研究助手
自動化文獻搜索、數據收集和報告生成。

### 5. 代碼助手
提供代碼解釋、調試建議和文檔生成。

### 6. 內容創作
多 Agent 協作進行內容研究、撰寫和編輯。

### 7. 數據分析
自動化數據處理、可視化和洞察生成。

### 8. 任務自動化
處理重複性任務，提高工作效率。

## 項目結構

```
50.PhiData/
├── README.md                 # 項目文檔
├── requirements.txt          # 依賴配置
├── 01_快速開始.py           # 基礎入門
├── 02_網頁搜索.py           # 網頁搜索功能
├── 03_金融分析.py           # 金融分析應用
├── 04_RAG助手.py            # RAG 實現
├── 05_多Agent團隊.py        # 多 Agent 協作
├── 06_結構化輸出.py         # 結構化數據輸出
├── 07_工具使用.py           # 工具集成
├── 08_知識庫.py             # 知識庫管理
├── 09_多模態.py             # 多模態功能
└── 10_生產部署.py           # 生產環境部署
```

## 最佳實踐

### 1. Agent 設計
- 明確定義 Agent 的角色和職責
- 提供清晰的指令和約束
- 合理選擇模型和工具

### 2. 性能優化
- 使用流式輸出提升體驗
- 啟用緩存減少成本
- 並行處理提高效率

### 3. 錯誤處理
- 實現重試機制
- 提供降級方案
- 記錄詳細日誌

### 4. 安全性
- 保護 API 密鑰
- 驗證用戶輸入
- 限制工具權限

### 5. 監控
- 追蹤 Agent 性能
- 監控成本使用
- 分析用戶反饋

## 進階功能

### 自定義工具

```python
from phi.tools import Toolkit

class CustomTool(Toolkit):
    def __init__(self):
        super().__init__(name="custom_tool")
        self.register(self.my_function)

    def my_function(self, param: str) -> str:
        """工具描述"""
        return f"處理結果: {param}"
```

### 自定義存儲

```python
from phi.storage.agent.base import AgentStorage

class CustomStorage(AgentStorage):
    def create(self) -> None:
        # 實現創建邏輯
        pass

    def read(self, session_id: str) -> dict:
        # 實現讀取邏輯
        pass

    def upsert(self, session_id: str, data: dict) -> None:
        # 實現更新邏輯
        pass
```

## 資源鏈接

- **官方網站**: https://phidata.com
- **GitHub**: https://github.com/phidatahq/phidata
- **文檔**: https://docs.phidata.com
- **Discord 社區**: https://discord.gg/phidata
- **示例項目**: https://github.com/phidatahq/phidata/tree/main/cookbook

## 版本信息

- **當前版本**: 2.5.0+
- **Python 要求**: 3.8+
- **更新日期**: 2025年

## 貢獻指南

歡迎貢獻代碼、報告問題或提出建議！

## 許可證

PhiData 採用 MIT 許可證，可自由用於商業和個人項目。

## 總結

PhiData 是一個功能強大、易於使用的 AI Agent 框架，適合從原型開發到生產部署的各個階段。通過本目錄中的示例，您可以快速掌握 PhiData 的核心功能，構建自己的 AI Agent 應用。

開始您的 PhiData 之旅，探索 AI Agent 的無限可能！

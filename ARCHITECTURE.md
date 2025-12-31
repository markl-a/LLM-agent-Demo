# 項目架構文檔

> LLM Agent Demo 專案架構設計與開發指南

## 📋 目錄

- [項目概述](#項目概述)
- [架構設計](#架構設計)
- [目錄結構](#目錄結構)
- [核心模塊](#核心模塊)
- [數據流](#數據流)
- [擴展指南](#擴展指南)
- [最佳實踐](#最佳實踐)

## 項目概述

LLM Agent Demo 是一個全面的 LLM Agent 框架學習與實踐專案，提供 80+ 個主流 AI Agent 框架的完整示例和教程。

### 設計目標

- **教育性**: 為學習者提供系統化的學習路徑
- **實用性**: 包含真實場景的應用案例
- **可擴展**: 易於添加新框架和示例
- **模塊化**: 每個框架獨立，互不干擾
- **文檔完整**: 每個示例都有詳細中文註釋

### 技術棧

- **語言**: Python 3.9+
- **AI 框架**: LangChain, LlamaIndex, AutoGen, CrewAI 等
- **向量數據庫**: Chroma, FAISS, Pinecone, Qdrant, LanceDB, Weaviate
- **LLM 提供商**: OpenAI, Anthropic, Google, Azure, 本地模型
- **開發工具**: Jupyter, Docker, pytest, pre-commit
- **文檔工具**: MkDocs, Markdown

## 架構設計

### 整體架構圖

```
┌─────────────────────────────────────────────────────────────────┐
│                      LLM Agent Demo 專案                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │  基礎教程    │  │  框架示例    │  │  應用案例    │        │
│  │              │  │              │  │              │        │
│  │ 0.AI基礎     │  │ 1-80個框架   │  │ 11.應用案例  │        │
│  │ 機器學習     │  │ 完整示例     │  │ 真實場景     │        │
│  │ LLM基礎      │  │ 中文註釋     │  │ 最佳實踐     │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                 │
│  ┌──────────────────────────────────────────────────┐          │
│  │              核心庫 (src/llm_agent_demo)          │          │
│  ├──────────────────────────────────────────────────┤          │
│  │ - utils/          工具函數                       │          │
│  │ - langchain/      LangChain 封裝                 │          │
│  │ - llamaindex/     LlamaIndex 封裝                │          │
│  │ - vector_stores/  向量數據庫接口                 │          │
│  │ - common/         通用組件                       │          │
│  └──────────────────────────────────────────────────┘          │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │  向量數據庫  │  │  LLM 提供商  │  │  工具集成    │        │
│  │              │  │              │  │              │        │
│  │ Chroma       │  │ OpenAI       │  │ Web Search   │        │
│  │ FAISS        │  │ Anthropic    │  │ File Tools   │        │
│  │ Pinecone     │  │ Google       │  │ Code Exec    │        │
│  │ Qdrant       │  │ Azure        │  │ SQL/DB       │        │
│  │ LanceDB      │  │ Local LLM    │  │ API Calls    │        │
│  │ Weaviate     │  │ Ollama       │  │ Custom       │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 分層架構

```
┌────────────────────────────────────────────┐
│         應用層 (Application Layer)          │
│  - 示例代碼                                 │
│  - 教程 Jupyter Notebooks                  │
│  - 實際應用案例                             │
├────────────────────────────────────────────┤
│         框架層 (Framework Layer)            │
│  - LangChain, LlamaIndex, AutoGen...       │
│  - 80+ AI Agent 框架                       │
│  - 框架特定封裝                             │
├────────────────────────────────────────────┤
│         核心層 (Core Layer)                 │
│  - 通用工具函數                             │
│  - 共享組件                                │
│  - 配置管理                                │
├────────────────────────────────────────────┤
│         基礎設施層 (Infrastructure Layer)   │
│  - LLM API 調用                            │
│  - 向量數據庫                               │
│  - 文件存儲                                │
│  - 緩存機制                                │
└────────────────────────────────────────────┘
```

## 目錄結構

### 完整結構說明

```
LLM-agent-Demo/
│
├── 0.從AI到LLM基礎/              # AI/ML/DL/LLM 基礎教程
│   ├── 0.AI基礎概念.md            # 人工智能基礎
│   ├── 1.機器學習基礎.md          # 機器學習入門
│   ├── 2.深度學習基礎.md          # 深度學習基礎
│   ├── 3.Transformer架構詳解.md   # Transformer 原理
│   ├── 4.LLM基礎知識.md           # 大語言模型基礎
│   ├── 5.提示工程指南.md          # Prompt Engineering
│   └── README.md                  # 學習路徑指南
│
├── 1.LangchainDemos/              # LangChain 完整教程
│   ├── 0.簡單的RAG_範例.ipynb     # RAG 入門
│   ├── 1-9.*.ipynb                # 系統化教程
│   └── advanced_examples/         # 進階示例
│
├── 2.Multi_modal_RAG/             # 多模態 RAG
│   ├── langchain_cookbook_Multi_modal_RAG.ipynb
│   └── utils/                     # 工具函數
│
├── 3.程式碼解析/                   # 開源項目分析
│   ├── 1-open_hands_程式碼解析.md
│   ├── Cline.md
│   ├── PCAgent架構流程.md
│   └── ...                        # 更多項目分析
│
├── 4.RPA_LLM/                     # RPA 與 LLM 結合
│   └── survey.md                  # 調研報告
│
├── 5.demo-sales-outreach-automation-langgraph/  # 銷售自動化案例
│   ├── README.md
│   └── examples/
│
├── 6-9.*/                         # LlamaIndex, AutoGen, CrewAI, MetaGPT
│   └── [各框架完整教程]
│
├── 10.框架對比與選擇指南/          # 框架對比分析
│   ├── 框架對比表.md
│   ├── 選擇指南.md
│   └── 最佳實踐.md
│
├── 11.實際應用案例/                # 真實應用場景
│   ├── 客服機器人/
│   ├── 文檔問答系統/
│   ├── 智能搜索引擎/
│   └── 程式碼助手/
│
├── 12-80.*/                       # 80+ AI Agent 框架
│   ├── 12.Semantic Kernel/        # Microsoft 企業框架
│   ├── 13.LangFlow/               # 可視化構建
│   ├── 14.Haystack/               # RAG 專家
│   ├── 15.AutoGPT/                # 自主 Agent
│   ├── 16.OpenAI Swarm/           # 輕量協作
│   ├── 17.LangGraph/              # 狀態管理
│   ├── ...                        # 更多框架
│   ├── 70.LangSmith/              # LLM 可觀測性
│   ├── 71.Chainlit/               # 聊天界面
│   ├── 72.Gradio/                 # UI 快速原型
│   ├── 76.Burr/                   # 狀態機管理
│   ├── 77.Langroid/               # 多 Agent 協作
│   ├── 78.Txtai/                  # 語義搜索
│   ├── 79.LanceDB/                # 向量數據庫
│   └── 80.Weaviate/               # 企業級向量庫
│
├── src/llm_agent_demo/            # 核心庫（可選）
│   ├── __init__.py
│   ├── utils/                     # 工具模組
│   │   ├── __init__.py
│   │   ├── config.py              # 配置管理
│   │   ├── logger.py              # 日誌工具
│   │   └── helpers.py             # 輔助函數
│   ├── langchain/                 # LangChain 封裝
│   │   ├── __init__.py
│   │   ├── chains.py
│   │   └── agents.py
│   ├── llamaindex/                # LlamaIndex 封裝
│   │   ├── __init__.py
│   │   └── indexes.py
│   └── vector_stores/             # 向量數據庫封裝
│       ├── __init__.py
│       ├── chroma.py
│       └── faiss.py
│
├── tests/                         # 測試文件
│   ├── __init__.py
│   ├── test_basic.py
│   ├── test_langchain.py
│   └── test_llamaindex.py
│
├── docs/                          # MkDocs 文檔
│   ├── index.md
│   ├── getting-started.md
│   └── frameworks/
│
├── examples/                      # 通用示例
│   └── minimal/                   # 最小示例
│
├── .github/                       # GitHub 配置
│   └── workflows/                 # CI/CD
│
├── .env.example                   # 環境變量模板
├── .gitignore                     # Git 忽略規則
├── .pre-commit-config.yaml        # Pre-commit 配置
├── docker-compose.yml             # Docker 編排
├── Dockerfile                     # Docker 鏡像
├── Makefile                       # 開發工具命令
├── mkdocs.yml                     # 文檔配置
├── requirements.txt               # 主要依賴
├── requirements-dev.txt           # 開發依賴
├── setup.py                       # 安裝配置
├── pyproject.toml                 # 項目配置
│
├── README.md                      # 項目主文檔
├── QUICKSTART.md                  # 快速開始指南
├── CONTRIBUTING.md                # 貢獻指南
├── ARCHITECTURE.md                # 本文件
├── SECURITY.md                    # 安全政策
├── DOCS_INDEX.md                  # 文檔索引
├── PROJECT_SUMMARY.md             # 項目總結
└── LICENSE                        # MIT 授權
```

### 框架目錄標準結構

每個框架目錄都遵循統一的結構：

```
XX.FrameworkName/
├── README.md                      # 框架介紹和完整教程
├── requirements.txt               # 框架專用依賴
├── 01_快速開始.py                 # 基礎入門
├── 02_核心功能.py                 # 核心功能演示
├── 03-10_*.py                     # 循序漸進的示例
├── examples/                      # 額外示例（可選）
│   ├── basic/                     # 基礎示例
│   └── advanced/                  # 進階示例
├── data/                          # 示例數據（可選）
└── notebooks/                     # Jupyter 教程（可選）
```

## 核心模塊

### 1. 配置管理模塊

負責管理環境變量、API Keys 和框架配置。

```python
# src/llm_agent_demo/utils/config.py
class Config:
    """統一配置管理"""

    @staticmethod
    def get_openai_api_key():
        """獲取 OpenAI API Key"""
        return os.getenv("OPENAI_API_KEY")

    @staticmethod
    def get_vector_store_config():
        """獲取向量數據庫配置"""
        return {...}
```

### 2. LLM 抽象層

統一不同 LLM 提供商的接口。

```python
# src/llm_agent_demo/utils/llm_factory.py
class LLMFactory:
    """LLM 工廠類"""

    @staticmethod
    def create_llm(provider="openai", model="gpt-4", **kwargs):
        """創建 LLM 實例"""
        if provider == "openai":
            return ChatOpenAI(model=model, **kwargs)
        elif provider == "anthropic":
            return ChatAnthropic(model=model, **kwargs)
        # ...
```

### 3. 向量存儲抽象層

統一向量數據庫操作接口。

```python
# src/llm_agent_demo/vector_stores/base.py
class VectorStoreBase(ABC):
    """向量數據庫基類"""

    @abstractmethod
    def add_documents(self, documents):
        pass

    @abstractmethod
    def similarity_search(self, query, k=4):
        pass
```

### 4. 工具集成模塊

標準化外部工具的集成。

```python
# src/llm_agent_demo/utils/tools.py
class ToolManager:
    """工具管理器"""

    @staticmethod
    def get_web_search_tool():
        """獲取網絡搜索工具"""
        return SerperDevTool()

    @staticmethod
    def get_file_tools():
        """獲取文件操作工具"""
        return [ReadFileTool(), WriteFileTool()]
```

## 數據流

### RAG 應用數據流

```
用戶查詢
    │
    ├─→ [Embedding] ─→ 向量化
    │                     │
    ├─→ [Vector DB] ←─────┘
    │        │
    │        ├─→ 相似度搜索
    │        │
    │        └─→ 檢索文檔
    │                │
    └─→ [LLM] ←──────┴─→ [提示模板]
           │
           └─→ 生成回答
                  │
                  └─→ 返回用戶
```

### Agent 工作流數據流

```
用戶輸入
    │
    ├─→ [Agent] ─→ 分析任務
    │                  │
    │                  ├─→ 選擇工具
    │                  │      │
    │                  │      ├─→ [Tool 1] ─→ 執行
    │                  │      ├─→ [Tool 2] ─→ 執行
    │                  │      └─→ [Tool N] ─→ 執行
    │                  │                │
    │                  ├─→ [LLM] ←──────┘
    │                  │      │
    │                  │      ├─→ 推理決策
    │                  │      │
    │                  └──────┴─→ 下一步行動
    │                                │
    │                                ├─→ 繼續執行
    │                                │
    │                                └─→ 完成任務
    │
    └─→ 返回結果
```

## 擴展指南

### 添加新框架

1. **創建框架目錄**
   ```bash
   mkdir "XX.NewFramework"
   cd "XX.NewFramework"
   ```

2. **創建標準文件**
   ```bash
   touch README.md
   touch requirements.txt
   touch 01_快速開始.py
   ```

3. **編寫 README.md**
   - 框架簡介
   - 核心特點
   - 安裝指南
   - 快速開始
   - 示例導覽
   - 最佳實踐

4. **創建示例代碼**
   - 從簡單到複雜
   - 每個文件專注一個主題
   - 詳細中文註釋
   - 可直接運行

5. **更新項目文檔**
   - 更新 DOCS_INDEX.md
   - 更新 README.md
   - 添加到框架對比表

### 添加新應用案例

1. **選擇合適框架**
2. **設計應用架構**
3. **實現核心功能**
4. **編寫文檔**
5. **提供示例數據**

## 最佳實踐

### 代碼規範

1. **Python 代碼**
   - 使用 Black 格式化（行長 100）
   - 使用 isort 排序導入
   - 添加類型提示
   - 編寫 docstring

2. **示例代碼**
   - 每個示例獨立運行
   - 包含詳細註釋
   - 處理常見錯誤
   - 提供輸出示例

3. **文檔**
   - 使用清晰的標題層級
   - 代碼塊指定語言
   - 提供完整示例
   - 更新目錄索引

### 環境管理

1. **使用虛擬環境**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. **依賴管理**
   - 框架專用依賴放在框架目錄
   - 共享依賴放在根目錄
   - 定期更新依賴版本

3. **環境變量**
   - 使用 `.env` 文件
   - 不提交敏感信息
   - 提供 `.env.example` 模板

### 測試策略

1. **單元測試**
   - 測試核心功能
   - 使用 pytest
   - Mock 外部 API

2. **集成測試**
   - 測試完整流程
   - 使用真實 API（CI/CD）
   - 檢查輸出格式

3. **示例驗證**
   - 確保示例可運行
   - 檢查輸出正確性
   - 處理 API 限流

### 性能優化

1. **緩存策略**
   - 緩存 LLM 響應
   - 緩存向量數據
   - 使用本地緩存

2. **批處理**
   - 批量處理文檔
   - 批量 API 調用
   - 異步處理

3. **資源管理**
   - 及時釋放資源
   - 限制並發數
   - 監控內存使用

### 安全考慮

1. **API Key 管理**
   - 使用環境變量
   - 不硬編碼
   - 定期輪換

2. **輸入驗證**
   - 驗證用戶輸入
   - 防止注入攻擊
   - 限制輸入長度

3. **錯誤處理**
   - 不暴露敏感信息
   - 記錄錯誤日誌
   - 優雅降級

## 開發工具

### Makefile 命令

```bash
make install       # 安裝依賴
make test          # 運行測試
make lint          # 代碼檢查
make format        # 代碼格式化
make docs          # 生成文檔
make clean         # 清理緩存
```

### Pre-commit Hooks

自動執行：
- 代碼格式化
- 導入排序
- 類型檢查
- 基礎 lint

### Docker 支持

```bash
# 構建鏡像
docker build -t llm-agent-demo .

# 運行容器
docker-compose up -d

# 停止容器
docker-compose down
```

## 維護指南

### 版本更新

1. 更新框架版本
2. 測試兼容性
3. 更新文檔
4. 發布更新日誌

### 問題處理

1. 檢查 GitHub Issues
2. 重現問題
3. 修復並測試
4. 更新文檔

### 社區互動

1. 及時回應 Issues
2. Review Pull Requests
3. 更新 FAQ
4. 分享最佳實踐

---

**最後更新**: 2025-12-31

**維護者**: LLM Agent Demo Team

**問題反饋**: [GitHub Issues](https://github.com/markl-a/LLM-agent-Demo/issues)

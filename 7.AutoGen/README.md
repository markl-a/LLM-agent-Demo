# AutoGen 學習教程

## 📚 簡介

AutoGen 是微軟推出的多 Agent 對話框架，能夠讓多個 AI Agent 相互協作完成複雜任務。它是構建下一代 LLM 應用的強大工具。

### 核心特性

- **多 Agent 協作**: 支持多個 Agent 之間的自動對話和協作
- **人機協作**: 可以讓人類參與到 Agent 對話中，實現 Human-in-the-Loop
- **程式碼執行**: 內建安全的程式碼執行環境（支持 Docker 隔離）
- **靈活配置**: 支持多種 LLM 配置和 Agent 角色定義
- **工具調用**: 支持函數調用和外部工具整合
- **對話模式**: 支持兩方對話、群組對話、嵌套對話等多種模式

### 為什麼選擇 AutoGen？

✅ **簡化多 Agent 開發**：提供高層抽象，無需手動管理對話流程
✅ **內建最佳實踐**：整合了多 Agent 系統的成熟設計模式
✅ **生產級別**：由微軟維護，適合企業級應用
✅ **活躍社區**：豐富的文檔、示例和社區支持
✅ **可擴展性**：易於整合自定義工具和外部 API

## 📋 系統要求

- Python 3.8 或更高版本
- pip 或 conda 包管理器
- （可選）Docker（用於安全代碼執行）
- 至少 4GB 可用記憶體

## 🔧 安裝指南

### 基礎安裝

```bash
# 使用 pip 安裝
pip install pyautogen

# 或使用 conda
conda install -c conda-forge pyautogen
```

### 完整安裝（包含所有可選依賴）

```bash
# 安裝所有功能
pip install "pyautogen[all]"

# 或分別安裝需要的功能
pip install "pyautogen[retrievechat]"  # RAG 功能
pip install "pyautogen[teachable]"     # 可學習 Agent
pip install "pyautogen[lmm]"           # 多模態支持
pip install "pyautogen[graph]"         # 圖可視化
```

### Docker 支持（推薦用於代碼執行）

```bash
# 安裝 Docker
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io

# macOS
brew install docker

# 或從官網下載：https://www.docker.com/get-started

# 拉取 AutoGen 執行環境鏡像
docker pull python:3.11-slim
```

### 驗證安裝

```python
import autogen
print(f"AutoGen 版本: {autogen.__version__}")
```

## ⚙️ 環境配置

### 方式 1：使用環境變數

創建 `.env` 文件：

```bash
# OpenAI
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_API_BASE=https://api.openai.com/v1  # 可選

# Azure OpenAI
AZURE_OPENAI_API_KEY=your-azure-key
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-your-key

# Google Gemini
GOOGLE_API_KEY=your-google-api-key

# 本地模型（Ollama）
OLLAMA_BASE_URL=http://localhost:11434
```

在代碼中加載：

```python
from dotenv import load_dotenv
import os

load_dotenv()

config_list = [
    {
        "model": "gpt-4",
        "api_key": os.getenv("OPENAI_API_KEY")
    }
]
```

### 方式 2：使用配置文件

創建 `OAI_CONFIG_LIST.json`：

```json
[
    {
        "model": "gpt-4",
        "api_key": "sk-your-api-key"
    },
    {
        "model": "gpt-3.5-turbo",
        "api_key": "sk-your-api-key",
        "api_type": "openai",
        "api_base": "https://api.openai.com/v1",
        "api_version": null
    },
    {
        "model": "gpt-4",
        "api_key": "your-azure-key",
        "api_type": "azure",
        "api_base": "https://your-endpoint.openai.azure.com/",
        "api_version": "2024-02-15-preview"
    }
]
```

在代碼中使用：

```python
import autogen

config_list = autogen.config_list_from_json(
    "OAI_CONFIG_LIST.json",
    filter_dict={
        "model": ["gpt-4", "gpt-3.5-turbo"]
    }
)
```

### 方式 3：支持多種 LLM 提供商

```python
config_list = [
    # OpenAI GPT-4
    {
        "model": "gpt-4",
        "api_key": "sk-...",
    },
    # Azure OpenAI
    {
        "model": "gpt-4",
        "api_type": "azure",
        "api_key": "...",
        "api_base": "https://....openai.azure.com/",
        "api_version": "2024-02-15-preview"
    },
    # 本地 Ollama
    {
        "model": "llama2",
        "api_base": "http://localhost:11434/v1",
        "api_key": "ollama",  # 本地模型可以是任意值
    },
    # Anthropic Claude
    {
        "model": "claude-3-opus-20240229",
        "api_key": "sk-ant-...",
        "api_type": "anthropic"
    }
]
```

## 🎯 教程內容

### 📘 基礎教程

| 章節 | 文件 | 內容 | 難度 |
|------|------|------|------|
| 0 | [基礎對話](0.基礎對話.ipynb) | AutoGen 安裝、配置、創建第一個 Agent、基本對話 | ⭐ |
| 1 | [進階Agent協作模式](1.進階Agent協作模式.md) | 群組聊天、嵌套對話、工具調用、狀態管理 | ⭐⭐⭐ |
| 2 | [程式碼執行Agent](2.程式碼執行Agent.ipynb) | CodeExecutor、安全執行環境、自動化調試 | ⭐⭐ |
| 3 | [ConversableAgent詳解](3.ConversableAgent詳解.md) | Agent 類型、配置選項、生命週期管理 | ⭐⭐⭐ |

### 🚀 進階教程

| 章節 | 文件 | 內容 | 難度 |
|------|------|------|------|
| 4 | [AutoGen Studio實戰](4.AutoGen%20Studio實戰.md) | 可視化工具、低代碼開發、快速原型 | ⭐⭐ |
| 5 | [高級功能與技巧](5.高級功能與技巧.md) | RAG、記憶管理、多模態、流式輸出 | ⭐⭐⭐⭐ |
| 6 | [故障排除與最佳實踐](6.故障排除與最佳實踐.md) | 常見問題、性能優化、安全建議 | ⭐⭐⭐ |
| 7 | [實戰項目案例](7.實戰項目案例.md) | 完整項目、端到端實現、部署指南 | ⭐⭐⭐⭐⭐ |

### 📁 示例代碼

`examples/` 目錄包含可直接運行的示例：

- `simple_chat.py` - 簡單兩方對話
- `group_chat.py` - 多 Agent 群組協作
- `code_execution.py` - 代碼生成與執行
- `function_calling.py` - 工具和函數調用
- `rag_example.py` - RAG 檢索增強生成
- `web_scraping_team.py` - 網頁爬蟲團隊協作
- `data_analysis_pipeline.py` - 數據分析流水線

## 🚀 快速開始

### 最簡單的例子（5 行代碼）

```python
from autogen import AssistantAgent, UserProxyAgent

# 配置
config_list = [{"model": "gpt-4", "api_key": "YOUR_API_KEY"}]

# 創建 Agents
assistant = AssistantAgent("assistant", llm_config={"config_list": config_list})
user = UserProxyAgent("user", code_execution_config={"work_dir": "coding"})

# 開始對話
user.initiate_chat(assistant, message="請幫我寫一個計算斐波那契數列的 Python 函數")
```

### 實用範例：數據分析助手

```python
from autogen import AssistantAgent, UserProxyAgent
import os

# 配置
config_list = [
    {
        "model": "gpt-4",
        "api_key": os.getenv("OPENAI_API_KEY")
    }
]

# 創建數據分析師 Agent
data_analyst = AssistantAgent(
    name="數據分析師",
    system_message="""你是一個專業的數據分析師，擅長：
    1. 使用 Python (pandas, numpy, matplotlib) 進行數據分析
    2. 生成清晰的可視化圖表
    3. 提供數據洞察和建議
    請為每個任務編寫完整、可執行的代碼。""",
    llm_config={"config_list": config_list}
)

# 創建執行者 Agent
executor = UserProxyAgent(
    name="執行者",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={
        "work_dir": "data_analysis",
        "use_docker": False
    }
)

# 開始分析任務
task = """
請分析以下銷售數據並生成報告：
1. 讀取 sales_data.csv
2. 計算每月總銷售額
3. 找出銷售額最高的前5個產品
4. 繪製銷售趨勢圖
5. 提供業務建議
"""

executor.initiate_chat(data_analyst, message=task)
```

### 實用範例：軟體開發團隊

```python
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager

# 創建開發團隊
product_manager = AssistantAgent(
    name="產品經理",
    system_message="負責需求分析和產品設計",
    llm_config={"config_list": config_list}
)

backend_dev = AssistantAgent(
    name="後端工程師",
    system_message="負責後端 API 開發",
    llm_config={"config_list": config_list}
)

frontend_dev = AssistantAgent(
    name="前端工程師",
    system_message="負責前端界面開發",
    llm_config={"config_list": config_list}
)

qa_engineer = AssistantAgent(
    name="QA工程師",
    system_message="負責測試和質量保證",
    llm_config={"config_list": config_list}
)

user = UserProxyAgent(
    name="用戶",
    human_input_mode="TERMINATE",
    code_execution_config={"work_dir": "project"}
)

# 創建群組聊天
groupchat = GroupChat(
    agents=[user, product_manager, backend_dev, frontend_dev, qa_engineer],
    messages=[],
    max_round=20
)

manager = GroupChatManager(groupchat=groupchat, llm_config={"config_list": config_list})

# 啟動項目
user.initiate_chat(
    manager,
    message="我們需要開發一個待辦事項應用，包含用戶認證、任務管理和提醒功能。"
)
```

## 💡 應用場景

### 1️⃣ 軟體開發自動化
- 需求分析 → 設計 → 編碼 → 測試 → 部署
- 代碼審查和重構建議
- 自動化文檔生成

### 2️⃣ 數據科學與分析
- 數據清洗和預處理
- 探索性數據分析（EDA）
- 機器學習模型開發
- 可視化報告生成

### 3️⃣ 研究與寫作
- 文獻調研和總結
- 論文撰寫協作
- 多語言翻譯校對

### 4️⃣ 客戶服務
- 智能客服系統
- 問題分級處理
- 知識庫管理

### 5️⃣ 教育培訓
- 個性化學習助手
- 編程教學系統
- 作業批改和反饋

### 6️⃣ 業務流程自動化
- 報告自動生成
- 數據監控和告警
- 工作流程編排

## 🎓 學習路徑

### 🔰 初學者（1-2 週）
1. 完成 `0.基礎對話.ipynb`
2. 理解 Agent 基本概念
3. 嘗試修改示例代碼
4. 完成簡單的對話任務

### 🔵 進階者（2-4 週）
1. 學習 `1.進階Agent協作模式.md`
2. 掌握群組聊天和工具調用
3. 構建多 Agent 協作系統
4. 嘗試 `examples/` 中的項目

### 🔴 高級用戶（持續學習）
1. 深入 `5.高級功能與技巧.md`
2. 實現 RAG 和記憶管理
3. 優化性能和成本
4. 部署生產級應用

## 📊 版本兼容性

| AutoGen 版本 | Python 版本 | 主要特性 |
|-------------|------------|---------|
| 0.2.x | 3.8-3.11 | 穩定版本，推薦使用 |
| 0.3.x (Beta) | 3.9-3.12 | 新功能預覽 |

## ⚠️ 常見問題 (FAQ)

<details>
<summary><b>Q: 如何選擇合適的模型？</b></summary>

- **GPT-4**: 最強能力，適合複雜任務，成本較高
- **GPT-3.5-turbo**: 性價比高，適合大多數任務
- **本地模型（Ollama）**: 隱私性好，無 API 成本，但能力較弱
- **Claude**: 擅長長文本和複雜推理
</details>

<details>
<summary><b>Q: 代碼執行不安全怎麼辦？</b></summary>

建議使用 Docker 隔離：
```python
code_execution_config={
    "work_dir": "coding",
    "use_docker": True,  # 啟用 Docker
    "timeout": 60,       # 超時設置
    "last_n_messages": 3 # 限制上下文
}
```
</details>

<details>
<summary><b>Q: 如何控制 API 成本？</b></summary>

1. 設置 `max_consecutive_auto_reply` 限制回合數
2. 使用便宜的模型（如 gpt-3.5-turbo）
3. 啟用緩存：`cache_seed=42`
4. 設置 token 限制：`max_tokens=1000`
</details>

<details>
<summary><b>Q: Agent 對話陷入死循環怎麼辦？</b></summary>

設置合理的終止條件：
```python
is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE")
max_consecutive_auto_reply=10
```
</details>

<details>
<summary><b>Q: 支持中文嗎？</b></summary>

完全支持！只需在 `system_message` 中使用中文即可。
</details>

## 🔗 學習資源

### 官方資源
- 📖 [AutoGen 官方文檔](https://microsoft.github.io/autogen/)
- 💻 [GitHub 倉庫](https://github.com/microsoft/autogen)
- 🎥 [官方 YouTube 頻道](https://www.youtube.com/@autogen-ai)
- 📝 [官方博客](https://www.microsoft.com/en-us/research/project/autogen/)

### 社區資源
- 💬 [Discord 社區](https://discord.gg/pAbnFJrkgZ)
- 🐦 [Twitter 更新](https://twitter.com/pyautogen)
- 📚 [示例庫](https://github.com/microsoft/autogen/tree/main/notebook)

### 相關項目
- [LangChain](https://github.com/langchain-ai/langchain) - 另一個流行的 LLM 框架
- [CrewAI](https://github.com/joaomdmoura/crewAI) - 專注於協作 AI Agent
- [Semantic Kernel](https://github.com/microsoft/semantic-kernel) - 微軟的另一個 AI 框架

## 🤝 貢獻

歡迎貢獻改進建議和新示例！請參考 [貢獻指南](../CONTRIBUTING.md)。

## 📄 許可證

本教程採用 MIT 許可證。AutoGen 框架本身也是 MIT 許可證。

---

**💡 提示**：建議從 `0.基礎對話.ipynb` 開始，逐步深入學習。每個教程都包含可運行的代碼示例！

**🆘 需要幫助？** 查看 [故障排除與最佳實踐](6.故障排除與最佳實踐.md) 或在 GitHub Issues 提問。

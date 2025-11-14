# AutoGen 學習教程

## 📚 簡介

AutoGen 是微軟推出的多 Agent 對話框架，能夠讓多個 AI Agent 相互協作完成複雜任務。

### 核心特性

- **多 Agent 協作**: 支持多個 Agent 之間的自動對話和協作
- **人機協作**: 可以讓人類參與到 Agent 對話中
- **程式碼執行**: 內建安全的程式碼執行環境
- **靈活配置**: 支持多種 LLM 配置和 Agent 角色定義

## 🎯 教程內容

### 0. 基礎對話 (0.基礎對話.ipynb)
- AutoGen 安裝和配置
- 創建第一個 Agent
- Agent 之間的基本對話
- 配置 LLM 模型

### 1. 多 Agent 協作 (1.多Agent協作.ipynb)
- 創建多個專業 Agent
- Agent 角色定義
- 對話流程控制
- 任務分配和協作

### 2. 程式碼執行 Agent (2.程式碼執行Agent.ipynb)
- CodeExecutor 使用
- 安全執行環境
- 自動化程式碼生成和執行
- 錯誤處理和調試

## 🚀 快速開始

```python
from autogen import AssistantAgent, UserProxyAgent

# 配置
config_list = [{"model": "gpt-4", "api_key": "YOUR_API_KEY"}]

# 創建 Assistant Agent
assistant = AssistantAgent(
    name="assistant",
    llm_config={"config_list": config_list}
)

# 創建 User Proxy Agent (可執行程式碼)
user_proxy = UserProxyAgent(
    name="user_proxy",
    code_execution_config={"work_dir": "coding"}
)

# 開始對話
user_proxy.initiate_chat(
    assistant,
    message="請幫我寫一個計算斐波那契數列的 Python 函數"
)
```

## 💡 應用場景

- 自動化軟體開發
- 複雜問題解決
- 研究和數據分析
- 多輪對話系統

## 📖 學習資源

- [AutoGen 官方文檔](https://microsoft.github.io/autogen/)
- [GitHub 倉庫](https://github.com/microsoft/autogen)

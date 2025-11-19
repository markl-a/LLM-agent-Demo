# Semantic Kernel 教程

## 📚 簡介

[Semantic Kernel](https://github.com/microsoft/semantic-kernel) 是 Microsoft 開發的開源 AI orchestration SDK，用於快速將 LLM 功能集成到應用程式中。它是 **Microsoft Agent Framework** 的核心組件。

### ✨ 核心特點

- 🎯 **企業級**: Microsoft 官方支持，適合生產環境
- 🔌 **插件系統**: 靈活的插件架構，支持自定義功能
- 🤖 **Agent 框架**: 內建強大的 Agent 協作能力
- 🔄 **多語言**: 支持 Python、.NET、Java
- 🧠 **規劃器**: 自動任務規劃和執行
- 📊 **可觀測性**: 內建追蹤和監控功能

### 🆚 與其他框架對比

| 特性 | Semantic Kernel | LangChain | LlamaIndex |
|------|----------------|-----------|------------|
| **企業支持** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **Agent 能力** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **插件生態** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **學習曲線** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **文檔質量** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## 🚀 快速開始

### 安裝

```bash
# 安裝 Semantic Kernel
pip install semantic-kernel

# 安裝額外依賴
pip install openai anthropic google-generativeai
```

### 基礎配置

```python
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

# 創建 Kernel
kernel = sk.Kernel()

# 添加 LLM 服務
kernel.add_service(
    OpenAIChatCompletion(
        service_id="gpt-4o-mini",
        ai_model_id="gpt-4o-mini"
    )
)
```

---

## 📖 教程列表

### 1. [基礎概念](01_基礎概念.ipynb)
- Kernel 核心概念
- Service 服務管理
- Plugin 插件系統
- Function 函數調用

### 2. [插件開發](02_插件開發.ipynb)
- 創建自定義插件
- Native Functions
- Semantic Functions
- 插件組合

### 3. [Agent 開發](03_Agent開發.ipynb)
- 創建 AI Agent
- 多 Agent 協作
- Agent 通信機制
- 狀態管理

### 4. [規劃器](04_規劃器.ipynb)
- 自動任務規劃
- Sequential Planner
- Stepwise Planner
- 計劃執行

### 5. [記憶管理](05_記憶管理.ipynb)
- 短期記憶
- 長期記憶
- 語義記憶
- 記憶檢索

### 6. [實戰案例：智能助手](06_智能助手.ipynb)
- 構建完整的智能助手
- 集成多個插件
- 對話管理
- 錯誤處理

---

## 🔥 完整示例代碼 (20 個)

### 基礎入門 (1-5)
1. **[快速開始](01_快速開始.py)** - Kernel 初始化、基本使用、完整示例
2. **[多 LLM 提供商](02_多LLM提供商.py)** - OpenAI、Claude、Gemini 集成與切換
3. **[流式輸出](03_流式輸出.py)** - 實時 token 輸出、並行流式請求
4. **[提示詞工程](04_提示詞工程.py)** - 模板、Few-shot、鏈式提示詞
5. **[記憶管理](05_記憶管理.py)** - 對話歷史、語義記憶、上下文窗口管理

### 核心功能 (6-10)
6. **[函數調用](06_函數調用.py)** - 原生函數、自動函數調用、並行執行
7. **[規劃器 Planner](07_規劃器Planner.py)** - 任務規劃、多步驟執行
8. **[RAG 檢索增強](08_RAG檢索增強.py)** - 文檔檢索、語義搜索、問答系統
9. **[錯誤處理](09_錯誤處理.py)** - 重試機制、超時處理、降級策略
10. **[內容生成](10_內容生成.py)** - 文章、代碼、創意寫作生成

### 進階應用 (11-15)
11. **[翻譯與摘要](11_翻譯與摘要.py)** - 多語言翻譯、文本摘要、關鍵字提取
12. **[數據分析](12_數據分析.py)** - 統計分析、趨勢預測、異常檢測
13. **[多 Agent 協作](13_多Agent協作.py)** - Agent 團隊、協作解決問題
14. **[聊天機器人](14_聊天機器人.py)** - 客服機器人、意圖識別、多語言支持
15. **[情感分析與分類](15_情感分析與分類.py)** - NLP 任務、垃圾郵件檢測

### 實戰場景 (16-20)
16. **[文檔處理](16_文檔處理.py)** - 文檔摘要、問答、比較、格式轉換
17. **[郵件自動化](17_郵件自動化.py)** - 郵件生成、分類、自動回復、翻譯
18. **[API 與數據集成](18_API與數據集成.py)** - 外部 API 調用、數據整合
19. **[知識庫與 FAQ](19_知識庫與FAQ.py)** - 知識庫構建、FAQ 自動回答
20. **[高級技巧與優化](20_高級技巧與優化.py)** - 批量處理、緩存、並發控制、性能監控

> 💡 **提示**: 所有示例都包含完整的代碼、詳細註釋和最佳實踐建議，可直接運行學習。

---

## 💻 核心概念

### Kernel（核心）

Kernel 是 Semantic Kernel 的中心，負責管理所有服務、插件和配置：

```python
import semantic_kernel as sk

# 創建 Kernel
kernel = sk.Kernel()

# 添加服務
kernel.add_service(chat_service)

# 註冊插件
kernel.add_plugin(my_plugin, plugin_name="MyPlugin")

# 執行函數
result = await kernel.invoke(function, arguments)
```

### Plugin（插件）

插件是一組相關功能的集合：

```python
from semantic_kernel.functions import kernel_function

class WeatherPlugin:
    @kernel_function(
        name="get_weather",
        description="獲取指定城市的天氣"
    )
    def get_weather(self, city: str) -> str:
        # 實現天氣查詢邏輯
        return f"{city} 的天氣是晴天"

# 註冊插件
kernel.add_plugin(WeatherPlugin(), plugin_name="Weather")
```

### Agent（智能代理）

Agent 是具有自主決策能力的智能實體：

```python
from semantic_kernel.agents import ChatCompletionAgent

# 創建 Agent
agent = ChatCompletionAgent(
    service_id="gpt-4o-mini",
    kernel=kernel,
    name="AssistantAgent",
    instructions="你是一個有幫助的助手"
)

# Agent 執行任務
response = await agent.invoke("幫我查詢今天的天氣")
```

---

## 🎯 實際應用場景

### 1. 企業知識助手

```python
# 集成企業數據
knowledge_plugin = create_knowledge_plugin(
    data_sources=["SharePoint", "OneDrive", "Teams"]
)

# 創建企業助手
enterprise_agent = ChatCompletionAgent(
    kernel=kernel,
    name="EnterpriseAssistant",
    instructions="協助員工查詢公司資訊"
)
```

### 2. 客戶服務機器人

```python
# 添加客服插件
kernel.add_plugin(CustomerServicePlugin(), "CustomerService")
kernel.add_plugin(OrderManagementPlugin(), "OrderManagement")

# 創建客服 Agent
customer_service_agent = ChatCompletionAgent(
    kernel=kernel,
    name="CustomerServiceBot",
    instructions="處理客戶諮詢和訂單問題"
)
```

### 3. 開發助手

```python
# 添加開發工具插件
kernel.add_plugin(CodeAnalysisPlugin(), "CodeAnalysis")
kernel.add_plugin(GitHubPlugin(), "GitHub")

# 創建開發助手
dev_assistant = ChatCompletionAgent(
    kernel=kernel,
    name="DevAssistant",
    instructions="協助代碼審查和項目管理"
)
```

---

## 🔧 進階功能

### 多 Agent 協作

```python
from semantic_kernel.agents import AgentGroupChat

# 創建多個 Agent
researcher = ChatCompletionAgent(
    kernel=kernel,
    name="Researcher",
    instructions="負責研究和收集信息"
)

writer = ChatCompletionAgent(
    kernel=kernel,
    name="Writer",
    instructions="負責撰寫文章"
)

# 創建 Agent 群組
group_chat = AgentGroupChat(
    agents=[researcher, writer],
    termination_strategy=...
)

# 執行協作任務
async for message in group_chat.invoke("寫一篇關於 AI 的文章"):
    print(message)
```

### 自動規劃

```python
from semantic_kernel.planners import SequentialPlanner

# 創建規劃器
planner = SequentialPlanner(kernel=kernel)

# 自動規劃任務
plan = await planner.create_plan("幫我訂一張去紐約的機票")

# 執行計劃
result = await plan.invoke(kernel)
```

---

## 📊 性能優化

### 1. 並行執行

```python
import asyncio

# 並行調用多個函數
results = await asyncio.gather(
    kernel.invoke(function1, args1),
    kernel.invoke(function2, args2),
    kernel.invoke(function3, args3)
)
```

### 2. 緩存策略

```python
from semantic_kernel.memory import SemanticTextMemory

# 啟用記憶緩存
memory = SemanticTextMemory(storage=..., embeddings=...)
kernel.add_plugin(memory, "Memory")
```

### 3. 成本控制

```python
# 使用較小的模型處理簡單任務
kernel.add_service(
    OpenAIChatCompletion(
        service_id="simple-tasks",
        ai_model_id="gpt-3.5-turbo"
    )
)

# 設置 token 限制
response = await kernel.invoke(
    function,
    arguments,
    max_tokens=500
)
```

---

## 🐛 故障排除

### 問題 1: 插件無法調用

**症狀**: Agent 無法找到插件函數

**解決方案**:
```python
# 確保插件正確註冊
kernel.add_plugin(plugin, plugin_name="PluginName")

# 使用完整的函數名稱
result = await kernel.invoke(
    function_name="PluginName.FunctionName",
    arguments={"arg": "value"}
)
```

### 問題 2: 記憶體使用過高

**症狀**: 長時間對話後記憶體不足

**解決方案**:
```python
# 限制對話歷史長度
from semantic_kernel.contents import ChatHistory

chat_history = ChatHistory()
chat_history.max_messages = 20  # 只保留最近 20 條消息
```

### 問題 3: API 速率限制

**症狀**: 頻繁遇到 429 錯誤

**解決方案**:
```python
# 添加重試機制
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

service = OpenAIChatCompletion(
    service_id="gpt-4o-mini",
    ai_model_id="gpt-4o-mini",
    max_retries=3,
    retry_delay=1.0
)
```

---

## 📚 相關資源

### 官方資源
- [Semantic Kernel 官網](https://learn.microsoft.com/en-us/semantic-kernel/)
- [GitHub 倉庫](https://github.com/microsoft/semantic-kernel)
- [API 文檔](https://learn.microsoft.com/en-us/python/api/semantic-kernel/)
- [示例代碼](https://github.com/microsoft/semantic-kernel/tree/main/python/samples)

### 社區資源
- [Discord 社區](https://aka.ms/SKDiscord)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/semantic-kernel)
- [YouTube 教程](https://www.youtube.com/@semantickernel)

### 學習路徑
1. 📖 閱讀官方文檔
2. 💻 完成本教程的所有示例
3. 🔨 構建自己的插件
4. 🤖 創建多 Agent 應用
5. 🚀 部署到生產環境

---

## 🤝 貢獻

歡迎貢獻新的示例和改進！請查看 [貢獻指南](../../CONTRIBUTING.md)。

---

## 📄 許可證

本教程採用 MIT License。

**最後更新**: 2025-11-18
**Semantic Kernel 版本**: 1.0+

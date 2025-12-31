# Langroid - 多 Agent LLM 編程框架

## 簡介

Langroid 是一個直觀、輕量級的 Python 框架，專為構建基於大語言模型（LLM）的多 Agent 應用而設計。它採用面向對象的方法，將 Agent 和任務作為核心抽象，讓開發者能夠輕鬆構建複雜的多 Agent 系統。

Langroid 的設計理念是簡單直觀，同時保持強大的功能。它原生支持工具調用、向量存儲、結構化輸出等功能，並提供了優雅的 API 來組織 Agent 之間的交互。

## 核心特點

### 1. Agent 為中心
- **ChatAgent**：基本對話 Agent
- **工具集成**：原生支持工具/函數調用
- **記憶管理**：自動管理對話歷史
- **角色定義**：靈活的系統提示詞

### 2. 任務系統
- **Task 抽象**：將 Agent 包裝為任務
- **任務編排**：組織複雜的任務流程
- **委託機制**：Agent 之間的任務委託
- **層次結構**：支持任務的層次組織

### 3. 工具與函數
- **ToolMessage**：結構化的工具消息
- **自動解析**：自動解析工具調用
- **類型安全**：基於 Pydantic 的類型檢查
- **靈活綁定**：輕鬆將函數綁定到 Agent

### 4. 向量存儲
- **內建支持**：支持多種向量資料庫
- **文檔檢索**：RAG（檢索增強生成）
- **語義搜索**：基於向量的語義搜索
- **自動嵌入**：自動生成文檔嵌入

### 5. 結構化輸出
- **Pydantic 模型**：使用模型定義輸出結構
- **自動驗證**：自動驗證和解析
- **類型提示**：完整的類型提示支持
- **JSON 模式**：支持 JSON Schema

### 6. 對話管理
- **對話歷史**：自動管理對話上下文
- **輪次控制**：靈活的對話輪次管理
- **消息類型**：豐富的消息類型系統
- **上下文窗口**：智能的上下文窗口管理

### 7. 多模態支持
- **圖像輸入**：支持視覺模型
- **文檔處理**：PDF、文本等文檔處理
- **音頻處理**：語音輸入支持
- **混合輸入**：支持多模態混合輸入

### 8. 生產就緒
- **錯誤處理**：健壯的錯誤處理機制
- **日誌系統**：詳細的日誌記錄
- **性能優化**：高效的執行引擎
- **可擴展性**：易於擴展和自定義

## 安裝

### 基本安裝

```bash
pip install langroid
pip install openai
```

### 完整安裝（包含向量存儲）

```bash
pip install "langroid[all]"
pip install -r requirements.txt
```

### 環境配置

創建 `.env` 文件：

```env
# OpenAI 配置
OPENAI_API_KEY=your_openai_api_key

# 可選：其他 LLM 提供商
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key
```

## 快速開始

```python
import langroid as lr
import langroid.language_models as lm

# 配置語言模型
config = lm.OpenAIGPTConfig(
    chat_model="gpt-4o-mini",
    temperature=0.7
)

# 創建 Agent
agent = lr.ChatAgent(
    config=lr.ChatAgentConfig(
        llm=config,
        name="助手",
        system_message="你是一個友好的 AI 助手。"
    )
)

# 創建任務
task = lr.Task(agent, name="聊天任務")

# 運行任務
response = task.run("你好！請介紹一下自己。")
print(response.content)
```

## 核心概念

### 1. ChatAgent
Agent 是 Langroid 的核心抽象，封裝了 LLM、工具和對話歷史：
- 管理與 LLM 的交互
- 處理工具調用
- 維護對話上下文
- 定義角色和行為

### 2. Task
Task 將 Agent 組織為可執行的單元：
- 包裝 Agent 為任務
- 處理消息路由
- 支持任務委託
- 管理任務生命週期

### 3. ToolMessage
結構化的工具消息系統：
- 定義工具接口
- 自動解析調用
- 類型安全
- 結果驗證

### 4. 向量存儲
支持 RAG 和語義搜索：
- 文檔索引
- 向量檢索
- 相似度搜索
- 自動重排序

## 與其他框架的對比

| 特性 | Langroid | LangChain | AutoGen |
|------|----------|-----------|---------|
| **Agent 抽象** | ⭐⭐⭐⭐⭐ 優秀 | ⭐⭐⭐ 基礎 | ⭐⭐⭐⭐⭐ 優秀 |
| **多 Agent** | ⭐⭐⭐⭐⭐ 原生支持 | ⭐⭐⭐ 需要組合 | ⭐⭐⭐⭐⭐ 專注 |
| **工具調用** | ⭐⭐⭐⭐⭐ 優雅 | ⭐⭐⭐⭐ 良好 | ⭐⭐⭐⭐ 良好 |
| **類型安全** | ⭐⭐⭐⭐⭐ Pydantic | ⭐⭐⭐ 有限 | ⭐⭐⭐ 有限 |
| **學習曲線** | ⭐⭐⭐⭐ 適中 | ⭐⭐⭐ 較陡 | ⭐⭐⭐⭐ 適中 |
| **靈活性** | ⭐⭐⭐⭐⭐ 極高 | ⭐⭐⭐⭐⭐ 極高 | ⭐⭐⭐⭐ 高 |
| **文檔質量** | ⭐⭐⭐⭐ 優秀 | ⭐⭐⭐⭐⭐ 豐富 | ⭐⭐⭐⭐ 優秀 |

### 選擇建議

**選擇 Langroid 如果：**
- 構建多 Agent 系統
- 需要類型安全和結構化輸出
- 重視代碼的簡潔和可讀性
- 需要優雅的工具調用機制
- 想要面向對象的設計
- 需要良好的向量存儲集成

**選擇 LangChain 如果：**
- 需要豐富的組件生態
- 需要大量預構建的鏈
- 重視社區和文檔
- 需要廣泛的集成

**選擇 AutoGen 如果：**
- 專注於多 Agent 對話
- 需要 Microsoft 生態集成
- 構建對話式 Agent 系統

## 項目結構

```
77.Langroid/
├── README.md                 # 本文件
├── requirements.txt          # 依賴項
├── 01_快速開始.py           # 基本用法
├── 02_Agent基礎.py          # Agent 詳解
├── 03_任務系統.py           # Task 系統
├── 04_工具使用.py           # 工具和函數
├── 05_向量存儲.py           # RAG 和檢索
├── 06_多Agent.py            # 多 Agent 協作
├── 07_對話管理.py           # 對話流程
├── 08_文檔處理.py           # 文檔處理
├── 09_代碼生成.py           # 代碼生成
└── 10_企業應用.py           # 企業級應用
```

## 學習路徑

1. **入門階段**
   - 01_快速開始.py - 了解基本概念
   - 02_Agent基礎.py - 掌握 Agent 使用

2. **進階功能**
   - 03_任務系統.py - 學習任務組織
   - 04_工具使用.py - 集成工具和函數
   - 05_向量存儲.py - 實現 RAG

3. **高級應用**
   - 06_多Agent.py - 構建多 Agent 系統
   - 07_對話管理.py - 管理複雜對話
   - 08_文檔處理.py - 處理文檔數據

4. **實戰項目**
   - 09_代碼生成.py - 代碼生成助手
   - 10_企業應用.py - 企業級應用

## 最佳實踐

### 1. Agent 設計
- 為每個 Agent 定義清晰的角色
- 使用描述性的系統消息
- 合理設置溫度和其他參數
- 實現適當的工具集

### 2. 任務組織
- 將複雜任務分解為子任務
- 使用任務委託組織流程
- 定義清晰的終止條件
- 處理任務超時

### 3. 工具開發
- 使用 Pydantic 模型定義工具
- 提供清晰的工具描述
- 實現錯誤處理
- 驗證輸入輸出

### 4. 向量存儲
- 選擇合適的嵌入模型
- 優化分塊策略
- 實現高效的檢索
- 處理大規模數據

### 5. 性能優化
- 使用批處理減少 API 調用
- 實現結果緩存
- 優化提示詞長度
- 監控 token 使用

### 6. 錯誤處理
- 捕獲和處理 LLM 錯誤
- 實現重試機制
- 提供降級方案
- 記錄詳細日誌

## 使用場景

### 1. 智能助手
- 多領域知識問答
- 任務規劃和執行
- 工具調用和集成
- 個性化服務

### 2. 文檔處理
- 文檔分析和總結
- 信息提取
- 問答系統
- 語義搜索

### 3. 代碼開發
- 代碼生成
- 代碼審查
- 重構建議
- 文檔生成

### 4. 數據分析
- 數據處理
- 報告生成
- 可視化
- 洞察提取

### 5. 客戶服務
- 智能客服
- 問題診斷
- 解決方案推薦
- 工單管理

## 常見問題

### Q: Langroid 與 LangChain 有什麼區別？
A: Langroid 更注重 Agent 和多 Agent 系統，提供更簡潔的 API 和更好的類型安全。LangChain 則提供更豐富的組件生態。

### Q: 如何實現多 Agent 協作？
A: 使用 Task 的委託機制，讓 Agent 可以將子任務委託給其他 Agent。參見 06_多Agent.py。

### Q: 支持哪些 LLM？
A: 支持 OpenAI、Anthropic、Google、本地模型（通過 Ollama）等。

### Q: 如何實現 RAG？
A: 使用內建的向量存儲功能，Langroid 提供了簡潔的 RAG 實現。參見 05_向量存儲.py。

### Q: 可以使用本地模型嗎？
A: 可以，通過 Ollama 等工具可以輕鬆使用本地模型。

## 相關資源

- [官方網站](https://langroid.github.io/langroid/)
- [GitHub 倉庫](https://github.com/langroid/langroid)
- [官方文檔](https://langroid.github.io/langroid/)
- [示例集合](https://github.com/langroid/langroid/tree/main/examples)
- [API 參考](https://langroid.github.io/langroid/reference/)
- [Discord 社區](https://discord.gg/langroid)

## 總結

Langroid 是一個優雅、強大的多 Agent LLM 框架，特別適合構建複雜的 Agent 系統。它的核心優勢在於：

1. **簡潔的 API**：直觀易用的接口設計
2. **類型安全**：完整的 Pydantic 支持
3. **多 Agent**：原生的多 Agent 支持
4. **工具集成**：優雅的工具調用機制
5. **向量存儲**：內建的 RAG 支持

如果你正在構建需要多個 Agent 協作的複雜應用，或者重視代碼的類型安全和可維護性，Langroid 是一個優秀的選擇。

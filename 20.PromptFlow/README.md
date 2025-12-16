# Microsoft PromptFlow 框架學習指南

## 目錄
- [框架介紹](#框架介紹)
- [核心特點](#核心特點)
- [安裝方式](#安裝方式)
- [範例文件說明](#範例文件說明)
- [學習資源](#學習資源)

## 框架介紹

Microsoft PromptFlow 是一個專為 LLM（大型語言模型）應用開發設計的綜合性開發工具套件，由微軟開發並開源。它簡化了從概念設計、原型開發、測試、評估到生產部署和監控的整個開發生命週期。

### 什麼是 PromptFlow？

PromptFlow 提供了一個完整的解決方案，幫助開發者：

1. **可視化工作流**：通過有向無環圖（DAG）將 LLM、提示詞和 Python 工具連接起來
2. **協作開發**：輕鬆調試、分享和迭代流程
3. **質量評估**：通過大規模測試創建提示詞變體並評估其性能
4. **生產部署**：將流程部署為實時端點，釋放 LLM 的全部潛力

### 可用性

PromptFlow 有多種使用方式：

- **開源版本**：作為獨立的開源項目，擁有自己的 SDK 和 VS Code 擴展
- **Azure 集成**：在 Azure AI Foundry 和 Azure Machine Learning Studio 中作為功能提供
- **本地與雲端**：支持本地開發和雲端協作的無縫切換

## 核心特點

### 1. 流程創建（Flow Creation）

- **節點系統**：流程中的節點代表具有特定功能的工具，處理數據、執行任務
- **可視化編輯**：提供 DAG 圖形界面，清晰展示工作流結構
- **YAML 定義**：流程以 YAML 格式定義，便於版本控制

### 2. 工具系統（Tools）

- **內置工具**：LLM 工具、Python 工具、Prompt 工具
- **自定義工具**：使用 `@tool` 裝飾器創建自定義工具
- **模組化設計**：工具作為獨立可執行節點，易於測試和重用

### 3. 連接管理（Connections）

- **安全存儲**：安全管理外部服務的憑證和密鑰
- **多種類型**：
  - 強類型連接：`AzureOpenAIConnection`、`OpenAIConnection` 等
  - 自定義連接：用於存儲自定義憑證
- **工作區共享**：連接資源可與工作區所有成員共享

### 4. Prompty 模板

- **模板格式**：`.prompty` 文件使用修改過的 Markdown frontmatter
- **模型配置**：在 YAML frontmatter 中定義模型配置和預期輸入
- **靈活性**：支持提示詞變體和迭代優化

### 5. 批量處理與評估

- **批量運行**：使用 `PFClient` 執行批量數據處理
- **數據格式**：支持 CSV、TSV、JSONL 格式
- **可視化追蹤**：提供 Trace UI 可視化執行細節

### 6. 評估系統

- **評估流程**：特殊類型的流程，用於計算指標評估輸出質量
- **自定義指標**：可創建或自定義評估流程和指標
- **聚合功能**：使用聚合節點計算整體評估值

### 7. DevOps 集成

- **版本控制**：流程文件以 YAML 格式存儲，與源文件對齊
- **CI/CD 集成**：使用 CLI 或 SDK 在 CI/CD 管道中自動觸發流程運行
- **協作友好**：支持團隊協作和代碼審查

### 8. 部署能力

- **多平台部署**：可部署到您選擇的服務平台
- **端點創建**：輕鬆創建實時 API 端點
- **代碼集成**：可集成到應用程序代碼庫中

## 安裝方式

### 基本安裝

確保您有 Python 環境（推薦 Python >= 3.9, <= 3.11）：

```bash
# 安裝核心包
pip install promptflow promptflow-tools

# 如果需要 Azure 集成
pip install promptflow[azure]

# 完整安裝（包括所有功能）
pip install promptflow[all]
```

### VS Code 擴展

1. 在 VS Code 擴展市場搜索 "Prompt flow"
2. 安裝官方 Microsoft Prompt flow 擴展
3. 使用可視化界面開發流程

### Azure CLI 集成

```bash
# 安裝 Azure CLI（如果尚未安裝）
pip install azure-cli

# 安裝 Azure Machine Learning 擴展
az extension add -n ml
```

### 驗證安裝

```bash
# 檢查 PromptFlow CLI
pf --version

# 列出可用命令
pf --help
```

## 範例文件說明

本資料夾包含 10 個詳細的 Python 範例，涵蓋 PromptFlow 的主要功能：

### 01_快速開始.py
- PromptFlow 基礎概念
- 簡單的 Hello World 示例
- 基本的 LLM 調用
- Trace 追蹤功能

### 02_Flow創建.py
- 創建標準 Flow
- DAG（有向無環圖）結構
- 節點定義和連接
- Flow 的保存和加載

### 03_Prompt模板.py
- Prompty 文件格式
- 模板變量使用
- Frontmatter 配置
- 提示詞變體管理

### 04_Tool定義.py
- 使用 `@tool` 裝飾器
- 自定義工具開發
- 工具參數定義
- 工具測試和調試

### 05_連接管理.py
- 創建和管理連接
- AzureOpenAI 連接
- OpenAI 連接
- 自定義連接
- 連接安全性

### 06_批量處理.py
- 批量數據處理
- JSONL 數據格式
- 批量運行配置
- 結果收集和分析

### 07_評估系統.py
- 評估流程創建
- 自定義評估指標
- 聚合節點使用
- 評估結果分析

### 08_部署服務.py
- 本地服務部署
- Docker 容器化
- API 端點創建
- 服務測試

### 09_Azure集成.py
- Azure AI Foundry 集成
- Azure Machine Learning 連接
- 雲端資源使用
- 雲端部署

### 10_進階技巧.py
- 條件分支
- 循環處理
- 錯誤處理
- 性能優化
- 最佳實踐

## 學習路徑建議

1. **初學者**：
   - 從 `01_快速開始.py` 開始
   - 學習 `02_Flow創建.py` 理解基本結構
   - 練習 `03_Prompt模板.py` 掌握模板使用

2. **中級開發者**：
   - 深入 `04_Tool定義.py` 創建自定義工具
   - 學習 `05_連接管理.py` 管理外部服務
   - 使用 `06_批量處理.py` 處理大規模數據

3. **高級開發者**：
   - 掌握 `07_評估系統.py` 評估模型質量
   - 實踐 `08_部署服務.py` 部署到生產環境
   - 探索 `09_Azure集成.py` 利用雲端資源
   - 學習 `10_進階技巧.py` 優化和最佳實踐

## 環境變量配置

創建 `.env` 文件來存儲敏感信息：

```bash
# OpenAI 配置
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_BASE=https://api.openai.com/v1

# Azure OpenAI 配置
AZURE_OPENAI_API_KEY=your_azure_openai_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
AZURE_OPENAI_API_VERSION=2024-02-01

# Azure 訂閱配置
AZURE_SUBSCRIPTION_ID=your_subscription_id
AZURE_RESOURCE_GROUP=your_resource_group
AZURE_WORKSPACE_NAME=your_workspace_name
```

## 最佳實踐

1. **版本控制**：
   - 將流程文件提交到 Git
   - 使用有意義的提交訊息
   - 維護流程變更歷史

2. **測試策略**：
   - 在小數據集上測試流程
   - 使用評估流程驗證質量
   - 在部署前進行完整測試

3. **安全性**：
   - 不要將 API 密鑰提交到版本控制
   - 使用環境變量或連接管理
   - 定期輪換密鑰

4. **性能優化**：
   - 合理設置批量大小
   - 使用快取減少 API 調用
   - 監控和記錄執行時間

5. **協作開發**：
   - 使用雲端工作區共享流程
   - 文檔化流程設計決策
   - 定期團隊代碼審查

## 學習資源

### 官方文檔
- [PromptFlow 官方文檔](https://microsoft.github.io/promptflow/)
- [GitHub 倉庫](https://github.com/microsoft/promptflow)
- [PyPI 包頁面](https://pypi.org/project/promptflow/)

### Azure 資源
- [Azure AI Foundry 文檔](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/prompt-flow)
- [Azure Machine Learning PromptFlow](https://learn.microsoft.com/en-us/azure/machine-learning/prompt-flow/)

### 教程和範例
- [快速開始指南](https://microsoft.github.io/promptflow/how-to-guides/quick-start.html)
- [教程集合](https://microsoft.github.io/promptflow/tutorials/index.html)
- [Chat with PDF 教程](https://microsoft.github.io/promptflow/tutorials/chat-with-prompty.html)

### API 參考
- [Python 庫參考](https://microsoft.github.io/promptflow/reference/python-library-reference/)
- [CLI 命令參考](https://microsoft.github.io/promptflow/reference/pf-command-reference.html)
- [工具參考](https://microsoft.github.io/promptflow/reference/tools-reference/)

## 常見問題

### Q: PromptFlow 與 LangChain 的區別？
A: PromptFlow 更注重可視化開發、評估和 Azure 集成，而 LangChain 更側重於鏈式組合和豐富的組件生態。

### Q: 可以在生產環境中使用嗎？
A: 是的，PromptFlow 設計用於生產環境，支持部署、監控和 DevOps 集成。

### Q: 是否必須使用 Azure？
A: 不是，PromptFlow 可以完全本地使用，Azure 集成是可選的。

### Q: 支持哪些 LLM 提供商？
A: 支持 OpenAI、Azure OpenAI，並可通過自定義連接支持其他提供商。

### Q: 如何調試流程？
A: 使用 Trace UI 可視化執行細節，使用 VS Code 擴展進行交互式調試。

## 貢獻和反饋

如果您發現問題或有改進建議：

1. 在 [GitHub Issues](https://github.com/microsoft/promptflow/issues) 提交問題
2. 貢獻代碼請遵循項目的貢獻指南
3. 參與社區討論和分享經驗

## 授權

本範例代碼僅供學習參考使用。PromptFlow 框架本身遵循 MIT 授權。

---

**最後更新**：2025-12-15
**版本**：基於 PromptFlow 1.13.0+
**維護者**：LLM Agent Demo Project

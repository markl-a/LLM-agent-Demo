# PromptFlow - Azure 提示工程平台

## 簡介

PromptFlow 是微軟開發的開源提示工程工具和平台，專為簡化大型語言模型（LLM）應用的端到端開發週期而設計。它提供了一個可視化的流程設計器、靈活的節點系統以及完整的 CI/CD 整合能力，幫助開發者輕鬆構建、測試、評估和部署 LLM 應用。

PromptFlow 結合了 Azure AI 服務的強大功能，支持多種 LLM 提供商（OpenAI、Azure OpenAI、Hugging Face 等），並提供豐富的內置工具和自定義能力。它特別適合需要複雜提示編排、批量處理和生產級部署的企業級 AI 應用。

## 核心特點

### 1. 視覺化流程設計
- **DAG 編輯器**: 直觀的拖放式流程設計
- **節點系統**: 豐富的預置節點類型
- **實時預覽**: 流程執行的即時反饋
- **版本控制**: 完整的流程版本管理

### 2. 豐富的節點類型
- **LLM**: 調用各種語言模型
- **Prompt**: 提示模板管理
- **Python**: 自定義 Python 代碼
- **Tool**: 內置和自定義工具
- **Conditional**: 條件分支邏輯
- **Loop**: 循環處理節點

### 3. 多模型支持
- **Azure OpenAI**: GPT-4, GPT-3.5, embeddings
- **OpenAI**: 直接調用 OpenAI API
- **Hugging Face**: 開源模型整合
- **自定義模型**: 支持自己的模型端點

### 4. 評估和測試
- **批量運行**: 大規模測試數據集
- **評估器**: 內置和自定義評估指標
- **A/B 測試**: 多版本對比
- **性能分析**: 詳細的執行統計

### 5. 部署和整合
- **Azure 部署**: 一鍵部署到 Azure
- **REST API**: 自動生成 API 端點
- **容器化**: Docker 支持
- **CI/CD**: GitHub Actions、Azure DevOps

### 6. 企業級功能
- **團隊協作**: 多人協同開發
- **安全性**: Azure AD 認證
- **監控**: Application Insights 整合
- **成本管理**: 詳細的 token 使用追蹤

## 安裝

### 使用 pip 安裝

```bash
pip install promptflow promptflow-tools
```

### 安裝 VS Code 擴展

1. 在 VS Code 中搜索 "Prompt Flow"
2. 安裝官方擴展
3. 重啟 VS Code

### Azure CLI 擴展（可選）

```bash
az extension add --name ml
```

### 完整安裝（包含所有依賴）

```bash
pip install -r requirements.txt
```

## 系統要求

### 最小配置
- **Python**: 3.8+
- **內存**: 4GB RAM
- **硬碟**: 5GB 可用空間
- **操作系統**: Windows/Linux/macOS

### 推薦配置
- **Python**: 3.10+
- **內存**: 8GB+ RAM
- **硬碟**: 10GB+ 可用空間
- **GPU**: 可選，用於本地模型

### Azure 服務（可選）
- **Azure OpenAI**: 調用 GPT 模型
- **Azure ML**: 雲端訓練和部署
- **Application Insights**: 監控和日誌

## 核心概念

### Flow（流程）
Flow 是 PromptFlow 的核心概念，定義了從輸入到輸出的完整處理邏輯：

```yaml
# flow.dag.yaml
inputs:
  question:
    type: string

outputs:
  answer:
    type: string
    reference: ${llm_node.output}

nodes:
  - name: llm_node
    type: llm
    source:
      type: code
      path: llm_prompt.jinja2
    inputs:
      question: ${inputs.question}
    connection: azure_openai
    api: chat
```

### Node（節點）
節點是 Flow 的基本組成單元：

**1. LLM 節點:**
```python
from promptflow import tool

@tool
def my_llm_tool(question: str) -> str:
    # LLM 調用邏輯
    return response
```

**2. Python 節點:**
```python
from promptflow import tool

@tool
def process_data(input_data: dict) -> dict:
    # 自定義處理邏輯
    return processed_data
```

### Connection（連接）
連接管理外部服務的憑證：

```yaml
# connections/azure_openai.yaml
type: azure_openai
api_key: ${env:AZURE_OPENAI_KEY}
api_base: ${env:AZURE_OPENAI_ENDPOINT}
api_version: "2024-02-15-preview"
```

### Evaluation（評估）
評估 Flow 的性能和質量：

```python
from promptflow import tool

@tool
def evaluate_answer(answer: str, ground_truth: str) -> dict:
    # 評估邏輯
    return {
        "accuracy": score,
        "relevance": relevance
    }
```

## 使用案例

### 1. RAG 應用
- **知識庫問答**: 基於文檔的智能問答
- **客服機器人**: 結合企業知識的客服
- **代碼助手**: 基於代碼庫的編程助手

### 2. 內容生成
- **文章寫作**: 自動化內容創作
- **營銷文案**: 廣告和營銷材料生成
- **報告生成**: 數據報告自動化

### 3. 數據處理
- **文本分類**: 大規模文本分類
- **情感分析**: 用戶評論分析
- **實體提取**: 結構化信息提取

### 4. 多輪對話
- **對話系統**: 上下文感知的對話
- **任務助手**: 多步驟任務執行
- **教育輔導**: 智能學習助手

### 5. 批量處理
- **數據標註**: 自動化數據標註
- **質量檢查**: 內容質量評估
- **翻譯服務**: 批量翻譯處理

### 6. API 服務
- **企業 API**: 內部 AI 服務
- **SaaS 產品**: 對外 AI 能力
- **微服務**: AI 微服務架構

## 示例文件說明

本目錄包含 10 個完整的示例文件，涵蓋 PromptFlow 的各個方面：

1. **01_快速開始.py** - PromptFlow 安裝和基本使用
2. **02_流程設計.py** - 創建和管理 Flow
3. **03_節點類型.py** - 各種節點類型的使用
4. **04_變量傳遞.py** - 節點間的數據傳遞
5. **05_條件分支.py** - 條件邏輯和分支
6. **06_批量運行.py** - 批量測試和評估
7. **07_評估流程.py** - Flow 性能評估
8. **08_部署服務.py** - 部署為 REST API
9. **09_Azure整合.py** - Azure 服務整合
10. **10_最佳實踐.py** - 生產級最佳實踐

## 最佳實踐

### 1. Flow 設計
- 保持 Flow 簡潔，避免過度複雜
- 合理使用節點，避免冗餘
- 明確定義輸入輸出類型
- 使用有意義的節點名稱

### 2. 提示工程
- 使用 Jinja2 模板管理提示
- 版本控制提示模板
- 測試不同的提示變體
- 收集用戶反饋優化提示

### 3. 性能優化
- 緩存重複的 LLM 調用
- 並行執行獨立節點
- 合理設置超時時間
- 監控 token 使用量

### 4. 安全性
- 使用環境變量存儲密鑰
- 實施訪問控制
- 驗證輸入數據
- 審計敏感操作

### 5. 測試和評估
- 建立完整的測試數據集
- 定義明確的評估指標
- 自動化評估流程
- 持續監控性能

### 6. 部署和維護
- 使用 CI/CD 自動化部署
- 實施 A/B 測試
- 監控生產環境性能
- 定期更新和優化

## 架構對比

### PromptFlow vs 其他工具

| 特性 | PromptFlow | LangChain | LlamaIndex | Semantic Kernel |
|-----|-----------|-----------|-----------|----------------|
| 視覺化設計 | ✅ | ❌ | ❌ | ❌ |
| Azure 整合 | ✅✅ | ⚠️ | ⚠️ | ✅ |
| 批量評估 | ✅✅ | ⚠️ | ❌ | ❌ |
| CI/CD 支持 | ✅ | ⚠️ | ❌ | ⚠️ |
| 企業級功能 | ✅✅ | ⚠️ | ⚠️ | ✅ |
| 學習曲線 | 中等 | 陡峭 | 中等 | 中等 |
| 社區支持 | 成長中 | 活躍 | 活躍 | 成長中 |

## 工作流程

```
┌─────────────────────────────────────────────────┐
│              開發階段                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ 設計流程 │→ │ 編寫節點 │→ │ 本地測試 │      │
│  └──────────┘  └──────────┘  └──────────┘      │
└──────────────┬──────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────┐
│              評估階段                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ 批量運行 │→ │ 性能評估 │→ │ 優化調整 │      │
│  └──────────┘  └──────────┘  └──────────┘      │
└──────────────┬──────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────┐
│              部署階段                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ 容器打包 │→ │ 部署服務 │→ │ 監控維護 │      │
│  └──────────┘  └──────────┘  └──────────┘      │
└─────────────────────────────────────────────────┘
```

## 相關資源

- **官方網站**: https://microsoft.github.io/promptflow/
- **GitHub**: https://github.com/microsoft/promptflow
- **官方文檔**: https://microsoft.github.io/promptflow/reference/
- **VS Code 擴展**: https://marketplace.visualstudio.com/items?itemName=prompt-flow.prompt-flow
- **示例庫**: https://github.com/microsoft/promptflow/tree/main/examples
- **Azure ML**: https://azure.microsoft.com/services/machine-learning/
- **教學影片**: https://www.youtube.com/@MicrosoftDeveloper
- **社區論壇**: https://github.com/microsoft/promptflow/discussions

## CLI 命令

### 創建 Flow
```bash
pf flow init --flow my_flow --type chat
```

### 測試 Flow
```bash
pf flow test --flow ./my_flow --inputs question="你好"
```

### 批量運行
```bash
pf run create --flow ./my_flow --data ./data.jsonl --stream
```

### 評估運行
```bash
pf run evaluate --run run_name --eval-flow ./eval_flow
```

### 部署服務
```bash
pf flow build --source ./my_flow --output ./dist --format docker
```

## 版本信息

- **PromptFlow**: 1.8+
- **PromptFlow Tools**: 1.4+
- **支持的 Python 版本**: 3.8-3.11
- **Azure OpenAI API**: 2024-02-15-preview+

## 授權

PromptFlow 採用 MIT 授權。本示例代碼僅供學習參考使用。

---

**注意**: PromptFlow 是微軟的開源項目，持續更新中。建議定期查看官方文檔獲取最新功能和最佳實踐。Azure 整合功能需要有效的 Azure 訂閱。

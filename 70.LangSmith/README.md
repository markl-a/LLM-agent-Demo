# LangSmith - LangChain 的可觀測性和調試平台

## 簡介

LangSmith 是 LangChain 官方推出的企業級 LLM 應用可觀測性、調試和評估平台。它提供了完整的追蹤、監控、評估和協作功能，幫助開發者構建、測試和優化 LLM 應用。

LangSmith 專為 LangChain 生態系統設計，但也支持其他框架和自定義應用的追蹤。它是 LangChain 團隊推薦的生產環境監控解決方案。

## 核心特點

### 1. 自動追蹤
- **無縫集成**：自動追蹤 LangChain 應用的所有操作
- **詳細記錄**：記錄輸入、輸出、token 使用、延遲等
- **嵌套追蹤**：支持多層次的調用鏈追蹤
- **異步支持**：完整支持異步操作追蹤

### 2. 手動追蹤
- **靈活控制**：手動創建和管理追蹤 spans
- **自定義元數據**：添加自定義標籤和元數據
- **跨框架支持**：支持非 LangChain 應用
- **細粒度控制**：精確控制追蹤範圍

### 3. 評估系統
- **多樣化評估器**：內建多種評估指標
- **自定義評估**：支持自定義評估函數
- **批量評估**：高效的批量評估能力
- **比較分析**：對比不同版本的性能

### 4. 數據集管理
- **數據集創建**：從追蹤中創建測試數據集
- **版本控制**：管理數據集版本
- **共享協作**：團隊共享測試數據
- **持續測試**：基於數據集的回歸測試

### 5. Prompt Hub
- **提示詞管理**：集中管理 prompt 模板
- **版本控制**：追蹤 prompt 的版本變化
- **A/B 測試**：對比不同 prompt 的效果
- **團隊協作**：共享和復用 prompt

### 6. 生產監控
- **實時監控**：監控生產環境的運行狀態
- **成本追蹤**：詳細的 API 成本分析
- **性能指標**：延遲、吞吐量等關鍵指標
- **告警系統**：異常情況自動告警

### 7. 團隊協作
- **多人協作**：支持團隊協作開發
- **權限管理**：細粒度的權限控制
- **共享工作區**：共享追蹤和評估結果
- **註釋功能**：為追蹤添加註釋和反饋

### 8. A/B 測試
- **實驗管理**：管理多個實驗版本
- **流量分配**：靈活的流量分配策略
- **統計分析**：自動化的統計分析
- **結果對比**：直觀的結果對比視圖

## 安裝

### 基本安裝

```bash
pip install langsmith
pip install langchain
pip install openai
```

### 完整安裝

```bash
pip install -r requirements.txt
```

### 環境配置

創建 `.env` 文件：

```env
# LangSmith 配置
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_PROJECT=your_project_name

# OpenAI 配置
OPENAI_API_KEY=your_openai_api_key
```

獲取 API Key：
1. 訪問 [LangSmith](https://smith.langchain.com/)
2. 註冊/登入帳號
3. 在設置中創建 API Key
4. 創建項目並獲取項目名稱

## 快速開始

```python
import os
from langsmith import Client
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

# 配置環境變量
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "my-project"

# 自動追蹤 LangChain 調用
llm = ChatOpenAI(model="gpt-4")
prompt = ChatPromptTemplate.from_template("Tell me a joke about {topic}")
chain = prompt | llm

# 這個調用會自動被追蹤
result = chain.invoke({"topic": "programming"})
```

## 與 Langfuse 對比

### LangSmith 的優勢

| 特性 | LangSmith | Langfuse |
|------|-----------|----------|
| **LangChain 集成** | ⭐⭐⭐⭐⭐ 原生集成 | ⭐⭐⭐⭐ 良好支持 |
| **自動追蹤** | ⭐⭐⭐⭐⭐ 零配置 | ⭐⭐⭐⭐ 需要配置 |
| **Prompt Hub** | ⭐⭐⭐⭐⭐ 內建支持 | ⭐⭐⭐ 基礎支持 |
| **評估系統** | ⭐⭐⭐⭐⭐ 強大完整 | ⭐⭐⭐⭐ 功能豐富 |
| **數據集管理** | ⭐⭐⭐⭐⭐ 優秀 | ⭐⭐⭐ 基礎功能 |
| **團隊協作** | ⭐⭐⭐⭐⭐ 企業級 | ⭐⭐⭐⭐ 良好支持 |
| **開源** | ❌ 閉源 | ✅ 開源 |
| **自託管** | ❌ 僅雲端 | ✅ 支持自託管 |
| **定價** | 💰 有免費層 | 💰 免費自託管 |

### 選擇建議

**選擇 LangSmith 如果：**
- 主要使用 LangChain 框架
- 需要與 LangChain 生態深度集成
- 重視開箱即用的體驗
- 不介意使用雲端服務
- 需要 Prompt Hub 功能
- 團隊規模較大，需要企業級功能

**選擇 Langfuse 如果：**
- 需要開源解決方案
- 要求數據私有化（自託管）
- 使用多種框架（不僅限於 LangChain）
- 預算有限
- 需要自定義和擴展
- 重視數據安全和隱私

### 核心差異

1. **生態集成**
   - LangSmith：LangChain 官方產品，深度集成
   - Langfuse：獨立產品，支持多框架

2. **部署方式**
   - LangSmith：僅雲端 SaaS
   - Langfuse：雲端 + 自託管

3. **開源性**
   - LangSmith：閉源商業產品
   - Langfuse：開源（MIT 許可證）

4. **功能側重**
   - LangSmith：調試、評估、Prompt 管理
   - Langfuse：可觀測性、分析、成本追蹤

## 核心功能示例

### 1. 基本追蹤
```python
from langsmith import Client

client = Client()
# 自動追蹤 LangChain 調用
```

### 2. 評估系統
```python
from langsmith import Client, evaluate

client = Client()

def my_evaluator(run, example):
    return {"score": 0.9}

results = evaluate(
    lambda x: chain.invoke(x),
    data=dataset_name,
    evaluators=[my_evaluator]
)
```

### 3. Prompt Hub
```python
from langchain import hub

prompt = hub.pull("username/prompt-name")
chain = prompt | llm
```

### 4. 成本追蹤
```python
# LangSmith 自動追蹤成本
# 在 UI 中查看詳細的成本分析
```

## 項目結構

```
70.LangSmith/
├── README.md                 # 本文件
├── requirements.txt          # 依賴項
├── 01_快速開始.py           # 基本追蹤
├── 02_自動追蹤.py           # Auto-tracing
├── 03_手動追蹤.py           # Manual spans
├── 04_評估系統.py           # Evaluations
├── 05_數據集.py             # Datasets
├── 06_AB測試.py             # A/B Testing
├── 07_提示管理.py           # Prompt Hub
├── 08_團隊協作.py           # 協作功能
├── 09_成本分析.py           # Cost tracking
└── 10_生產監控.py           # Production 監控
```

## 學習路徑

1. **入門階段**
   - 01_快速開始.py - 了解基本追蹤
   - 02_自動追蹤.py - 掌握自動追蹤機制

2. **進階功能**
   - 03_手動追蹤.py - 學習手動控制追蹤
   - 04_評估系統.py - 使用評估功能
   - 05_數據集.py - 管理測試數據集

3. **高級應用**
   - 06_AB測試.py - 進行 A/B 測試
   - 07_提示管理.py - 使用 Prompt Hub
   - 08_團隊協作.py - 團隊協作功能

4. **生產環境**
   - 09_成本分析.py - 追蹤和優化成本
   - 10_生產監控.py - 生產環境監控

## 最佳實踐

### 1. 項目組織
- 為不同環境使用不同的項目（dev/staging/prod）
- 使用描述性的 run 名稱
- 添加有意義的標籤和元數據

### 2. 評估策略
- 建立基準測試數據集
- 定期運行評估
- 追蹤性能變化趨勢

### 3. 成本優化
- 監控 token 使用情況
- 識別異常高成本的調用
- 優化 prompt 以減少 token 消耗

### 4. 團隊協作
- 建立 prompt 命名規範
- 共享最佳實踐
- 定期審查追蹤數據

### 5. 生產監控
- 設置關鍵指標告警
- 監控錯誤率和延遲
- 建立事故響應流程

## 常見問題

### Q: LangSmith 是免費的嗎？
A: LangSmith 提供免費層，包含一定額度的追蹤和評估。超出免費額度後需要付費。

### Q: 可以在本地運行 LangSmith 嗎？
A: 不可以，LangSmith 目前僅提供雲端 SaaS 服務，不支持自託管。

### Q: LangSmith 支持哪些 LLM 提供商？
A: 支持所有 LangChain 支持的 LLM 提供商，包括 OpenAI、Anthropic、Google、Azure 等。

### Q: 如何導出追蹤數據？
A: 可以通過 LangSmith API 或 SDK 導出追蹤數據，也可以在 UI 中下載 CSV 格式。

### Q: 數據會被用來訓練模型嗎？
A: 不會，LangSmith 承諾不會使用客戶數據訓練模型。詳見隱私政策。

## 相關資源

- [官方網站](https://smith.langchain.com/)
- [官方文檔](https://docs.smith.langchain.com/)
- [LangChain 文檔](https://python.langchain.com/docs/langsmith/)
- [API 參考](https://api.smith.langchain.com/redoc)
- [示例代碼](https://github.com/langchain-ai/langsmith-cookbook)
- [定價信息](https://smith.langchain.com/pricing)

## 總結

LangSmith 是 LangChain 生態系統的重要組成部分，提供了企業級的可觀測性和調試能力。如果你正在使用 LangChain 構建生產級應用，LangSmith 是不可或缺的工具。

對於需要開源解決方案或多框架支持的場景，可以考慮 Langfuse 作為替代方案。兩者可以根據具體需求選擇，甚至可以在不同場景下結合使用。

# NeMo Guardrails - NVIDIA 對話安全框架

## 簡介

NeMo Guardrails 是 NVIDIA 開發的開源工具包，專門用於為 LLM 對話系統添加可編程的護欄（Guardrails）。它提供了一種簡單的方式來控制 AI 助手的行為，確保對話安全、可控且符合業務要求。

## 核心特性

- **對話控制**：使用 Colang 語言定義對話流程和規則
- **輸入護欄**：檢測和阻止不當的用戶輸入
- **輸出護欄**：驗證和過濾 LLM 的輸出
- **主題控制**：限制對話主題在特定範圍內
- **越獄防護**：防止提示注入和越獄攻擊
- **事實核查**：驗證 LLM 輸出的事實準確性
- **多輪對話管理**：維護對話上下文和狀態
- **模塊化設計**：靈活的護欄組合和定制

## 安裝

```bash
pip install nemoguardrails openai
```

## 主要概念

### Colang
Colang（Conversation Language）是 NeMo Guardrails 的核心 DSL，用於定義：
- 對話流程（flows）
- 用戶和機器人的消息模式
- 護欄規則
- 動作和函數調用

### Rails（護欄）
護欄是應用於對話的規則和約束：
- **Input Rails**：在請求發送到 LLM 前檢查
- **Output Rails**：在 LLM 響應返回給用戶前檢查
- **Dialog Rails**：控制對話流程和上下文

### Actions（動作）
動作是 Python 函數，可以在對話中執行自定義邏輯，如：
- 調用外部 API
- 數據庫查詢
- 事實核查
- 內容過濾

## 架構優勢

1. **聲明式編程**：使用 Colang 聲明式定義對話規則
2. **分層防禦**：多層護欄提供全面保護
3. **靈活可擴展**：易於添加自定義護欄和動作
4. **LLM 無關**：支持多種 LLM（OpenAI、Anthropic、HuggingFace 等）
5. **企業級**：適合生產環境部署

## 使用場景

1. **客服機器人**：確保回應專業且在業務範圍內
2. **教育助手**：限制話題並確保內容適齡
3. **醫療諮詢**：防止提供未授權的醫療建議
4. **企業助手**：保護敏感信息不被泄露
5. **內容審核**：過濾不當內容和有害信息

## 示例文件說明

- `01_快速開始.py`：NeMo Guardrails 的基本使用
- `02_輸入護欄.py`：檢測和過濾用戶輸入
- `03_輸出護欄.py`：驗證和過濾 LLM 輸出
- `04_主題控制.py`：限制對話主題範圍
- `05_越獄防護.py`：防止提示注入攻擊
- `06_事實核查.py`：驗證 LLM 輸出的準確性
- `07_自定義軌道.py`：創建自定義護欄規則
- `08_Colang語法.py`：Colang 語言詳細示例
- `09_多輪對話.py`：管理有狀態的多輪對話
- `10_企業部署.py`：生產環境完整配置

## Colang 基礎

```colang
# 定義用戶消息
define user express greeting
  "hello"
  "hi"
  "hey"

# 定義機器人消息
define bot express greeting
  "Hello! How can I help you?"

# 定義對話流程
define flow greeting
  user express greeting
  bot express greeting
```

## 與其他框架的對比

| 特性 | NeMo Guardrails | Guardrails AI | LangChain |
|------|----------------|---------------|-----------|
| 對話流程控制 | ✅ 強大 | ⚠️ 基礎 | ✅ 中等 |
| 聲明式語法 | ✅ Colang | ❌ 無 | ⚠️ LCEL |
| 輸入/輸出護欄 | ✅ 都支持 | ✅ 都支持 | ⚠️ 有限 |
| 越獄防護 | ✅ 內建 | ❌ 需自定義 | ❌ 需自定義 |
| 事實核查 | ✅ 內建 | ❌ 需自定義 | ⚠️ RAG |
| 學習曲線 | 中等 | 簡單 | 中等 |

## 最佳實踐

1. **分層設計**：組合使用輸入、輸出和對話護欄
2. **測試驅動**：為每個護欄編寫測試用例
3. **漸進增強**：從基本護欄開始，逐步添加複雜規則
4. **性能優化**：合理配置護欄避免過度檢查
5. **監控日誌**：記錄所有護欄觸發事件

## 安全考量

- **提示注入**：使用內建的越獄防護
- **敏感信息**：配置 PII 檢測和過濾
- **主題偏離**：使用主題控制限制對話範圍
- **有害內容**：啟用毒性檢測護欄
- **事實錯誤**：配置事實核查機制

## 與 LangChain 集成

```python
from nemoguardrails import RailsConfig, LLMRails
from langchain.llms import OpenAI

# 創建配置
config = RailsConfig.from_path("./config")

# 創建 Rails 實例
rails = LLMRails(config)

# 使用 LangChain LLM
llm = OpenAI()
rails.register_action(llm, name="llm")
```

## 參考資源

- [官方文檔](https://docs.nvidia.com/nemo/guardrails/)
- [GitHub 倉庫](https://github.com/NVIDIA/NeMo-Guardrails)
- [Colang 語言指南](https://docs.nvidia.com/nemo/guardrails/colang/)
- [示例集合](https://github.com/NVIDIA/NeMo-Guardrails/tree/main/examples)
- [社區討論](https://github.com/NVIDIA/NeMo-Guardrails/discussions)

## 配置文件結構

```
config/
├── config.yml          # 主配置文件
├── rails/
│   ├── input.co       # 輸入護欄 Colang
│   ├── output.co      # 輸出護欄 Colang
│   └── dialog.co      # 對話流程 Colang
└── actions.py         # 自定義動作
```

## 注意事項

- 需要設置環境變量 `OPENAI_API_KEY`
- Colang 語法對縮進敏感
- 護欄會增加延遲，需要權衡安全性和性能
- 建議在開發環境充分測試後再部署
- 某些功能可能需要特定版本的依賴

## 許可證

NeMo Guardrails 採用 Apache 2.0 許可證。

## 版本要求

- Python >= 3.8
- nemoguardrails >= 0.5.0
- openai >= 1.0.0

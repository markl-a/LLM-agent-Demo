# LangFlow 教程

## 📚 簡介

[LangFlow](https://github.com/logspace-ai/langflow) 是一個視覺化的低代碼 AI 應用構建平台，讓你可以通過拖放界面快速構建 LLM 應用和 AI Agent。

### ✨ 核心特點

- 🎨 **可視化設計**: 拖放式流程圖設計界面
- 🔌 **豐富組件**: 內建 100+ 個預製組件
- 🚀 **快速原型**: 無需編碼即可構建 AI 應用
- 🔄 **實時預覽**: 即時查看流程執行結果
- 📦 **導出導入**: 輕鬆分享和復用流程
- 🌐 **API 生成**: 自動生成 REST API

### 🆚 與其他框架對比

| 特性 | LangFlow | LangChain | Semantic Kernel |
|------|----------|-----------|-----------------|
| **可視化** | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐ |
| **學習曲線** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **靈活性** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **企業支持** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **代碼優先** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 🚀 快速開始

### 安裝方式

#### 方式 1: pip 安裝（推薦）

```bash
# 安裝 LangFlow
pip install langflow

# 啟動 LangFlow
langflow run
```

#### 方式 2: Docker 運行

```bash
# 拉取 Docker 鏡像
docker pull langflowai/langflow:latest

# 運行容器
docker run -d -p 7860:7860 langflowai/langflow:latest
```

#### 方式 3: 從源碼安裝

```bash
# 克隆倉庫
git clone https://github.com/logspace-ai/langflow
cd langflow

# 安裝依賴
pip install -e .

# 啟動
langflow run
```

### 訪問界面

安裝完成後，訪問 http://localhost:7860 即可使用 LangFlow 的可視化界面。

---

## 💻 核心概念

### Flow（流程）

Flow 是 LangFlow 中的基本單位，代表一個完整的 AI 應用流程。

**組成部分**：
- **節點（Nodes）**: 執行特定功能的組件
- **邊（Edges）**: 連接節點，傳遞數據
- **輸入（Inputs）**: 流程的起點
- **輸出（Outputs）**: 流程的終點

### Components（組件）

LangFlow 提供豐富的預製組件：

**LLM 組件**：
- OpenAI
- Anthropic
- Google Gemini
- Groq
- Ollama (本地模型)

**Memory 組件**：
- Conversation Buffer Memory
- Conversation Summary Memory
- Vector Store Memory

**Tools 組件**：
- Search (Google, Serper)
- Calculator
- Python REPL
- API Request

**Embeddings 組件**：
- OpenAI Embeddings
- Hugging Face Embeddings
- Cohere Embeddings

**Vector Stores 組件**：
- Chroma
- Pinecone
- Qdrant
- Weaviate
- FAISS

---

## 📖 使用教程

### 1. 創建簡單的 RAG 流程

**步驟**：

1. **添加文檔加載器**
   - 拖放 "File" 組件
   - 上傳你的文檔

2. **添加文本分割器**
   - 拖放 "Text Splitter" 組件
   - 設置 chunk_size 和 chunk_overlap

3. **添加嵌入模型**
   - 拖放 "OpenAI Embeddings" 組件
   - 配置 API Key

4. **添加向量存儲**
   - 拖放 "Chroma" 組件
   - 連接嵌入模型

5. **添加檢索器**
   - 拖放 "Vector Store Retriever" 組件

6. **添加 LLM**
   - 拖放 "ChatOpenAI" 組件
   - 配置模型參數

7. **連接組件**
   - 按流程連接所有組件
   - 文檔 → 分割 → 嵌入 → 存儲 → 檢索 → LLM

8. **測試運行**
   - 點擊 "Run" 按鈕
   - 輸入問題並查看結果

### 2. 創建 Agent 流程

**組件選擇**：
```
Chat Input → Agent → Tools → LLM → Chat Output
```

**配置步驟**：

1. 添加 Agent 組件
2. 為 Agent 添加工具（Search, Calculator 等）
3. 連接 LLM
4. 配置 Agent 的 System Message
5. 測試 Agent 執行任務

### 3. 創建多輪對話機器人

**組件配置**：
```
Chat Input → Memory → LLM → Chat Output
```

**Memory 配置**：
- 選擇 Conversation Buffer Memory
- 設置 max_token_limit
- 連接到 LLM

---

## 🎯 實戰案例

### 案例 1: 客戶服務機器人

**流程設計**：

1. **輸入處理**
   - Chat Input (用戶問題)

2. **意圖識別**
   - LLM (分類用戶意圖)

3. **知識檢索**
   - Vector Store (查詢相關文檔)

4. **回答生成**
   - LLM (生成個性化回答)

5. **輸出**
   - Chat Output

**特色功能**：
- 自動分類客戶問題
- 從知識庫檢索相關信息
- 生成友好的回答
- 支持多輪對話

### 案例 2: 文檔分析助手

**流程設計**：

```
File Upload → Document Loader → Text Splitter →
Embeddings → Vector Store → Retriever → LLM → Output
```

**功能**：
- 上傳 PDF/Word/TXT 文檔
- 自動分塊和向量化
- 語義搜索
- 問答和摘要

### 案例 3: 數據分析 Agent

**組件**：
- CSV Loader
- Pandas Agent
- Code Executor
- LLM

**功能**：
- 上傳 CSV 數據
- 自然語言查詢數據
- 自動生成 Python 代碼
- 執行數據分析並返回結果

---

## 🔧 高級功能

### 1. 自定義組件

```python
from langflow import CustomComponent
from langflow.field_typing import Text

class MyCustomComponent(CustomComponent):
    display_name = "My Custom Tool"
    description = "自定義工具"

    def build_config(self):
        return {
            "input_text": {"display_name": "Input"},
        }

    def build(self, input_text: Text) -> Text:
        # 自定義邏輯
        result = input_text.upper()
        return result
```

### 2. API 導出

LangFlow 可以將流程導出為 REST API：

```bash
# 自動生成的 API 端點
POST /api/v1/process/{flow_id}

# 請求格式
{
    "inputs": {
        "input_1": "value"
    }
}
```

### 3. Python 集成

```python
from langflow import load_flow_from_json

# 加載流程
flow = load_flow_from_json("my_flow.json")

# 運行流程
result = flow.run(inputs={"question": "什麼是 AI?"})

print(result)
```

---

## 📊 最佳實踐

### 1. 組件復用

- 創建可復用的子流程
- 使用組件模板
- 導出常用配置

### 2. 性能優化

- 合理設置 chunk 大小
- 使用緩存減少 LLM 調用
- 並行處理多個任務

### 3. 錯誤處理

- 添加錯誤處理組件
- 設置重試機制
- 記錄執行日誌

### 4. 安全考慮

- 使用環境變數存儲 API Key
- 限制用戶輸入長度
- 過濾敏感信息

---

## 🐛 故障排除

### 問題 1: 組件無法連接

**原因**: 數據類型不匹配

**解決**:
- 檢查組件的輸入/輸出類型
- 使用轉換組件
- 查看組件文檔

### 問題 2: 流程運行緩慢

**原因**: LLM 調用過多

**解決**:
- 啟用緩存
- 優化提示詞
- 使用更快的模型

### 問題 3: 記憶體不足

**原因**: 文檔過大或分塊過多

**解決**:
- 增加 chunk 大小
- 限制上傳文件大小
- 使用流式處理

---

## 📚 相關資源

### 官方資源
- [LangFlow 官網](https://www.langflow.org/)
- [GitHub 倉庫](https://github.com/logspace-ai/langflow)
- [文檔](https://docs.langflow.org/)
- [Discord 社區](https://discord.gg/langflow)

### 教程資源
- [YouTube 頻道](https://www.youtube.com/@langflow)
- [示例流程庫](https://github.com/logspace-ai/langflow-examples)

### 相關工具
- [DataStax](https://www.datastax.com/) (LangFlow 母公司)
- [LangChain](https://www.langchain.com/)

---

## 💡 提示

### 適用場景

✅ **適合**:
- 快速原型開發
- 非技術人員使用
- 教學和演示
- 簡單的 AI 應用

❌ **不適合**:
- 複雜的邏輯處理
- 高性能要求的應用
- 需要精細控制的場景

### 學習建議

1. 從簡單流程開始
2. 熟悉各類組件
3. 學習最佳實踐
4. 結合代碼使用
5. 參與社區討論

---

## 📄 許可證

LangFlow 採用 MIT License。

**最後更新**: 2025-11-18
**LangFlow 版本**: 1.0+

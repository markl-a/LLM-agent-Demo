# Ollama - 本地 LLM 運行框架

## 簡介

Ollama 是一個強大的本地大型語言模型運行框架，讓您能夠在自己的電腦上輕鬆運行 Llama 3.3、Mistral、Gemma 2 等開源大型語言模型。完全離線運行，保護數據隱私，無需依賴雲端 API。

Ollama 提供簡單的命令行界面和 REST API，使得部署和使用本地 LLM 變得異常簡單。它支持多種流行的開源模型，並能夠通過 Modelfile 自定義模型配置。

## 核心特點

### 1. 完全本地運行
- **數據隱私**: 所有數據處理都在本地進行，不會發送到雲端
- **離線可用**: 下載模型後可完全離線使用
- **無 API 費用**: 不需要支付任何 API 調用費用

### 2. 簡單易用
- **一鍵安裝**: 提供各平台的安裝包
- **命令行友好**: 簡潔的 CLI 命令
- **REST API**: 標準的 HTTP API 接口
- **多語言支持**: Python、JavaScript、Go 等多種語言的 SDK

### 3. 豐富的模型支持
- **Llama 系列**: Llama 3.3, Llama 3.2, Llama 2
- **Mistral 系列**: Mistral, Mixtral, Mistral-NeMo
- **Gemma 系列**: Gemma 2, Gemma
- **其他模型**: Qwen, Phi, DeepSeek, Neural Chat 等
- **多模態模型**: LLaVA, BakLLaVA (支持圖像輸入)

### 4. 高性能
- **GPU 加速**: 自動利用 NVIDIA、AMD、Metal GPU
- **CPU 優化**: CPU 模式下也有良好性能
- **內存管理**: 智能加載和卸載模型
- **量化支持**: 支持 4-bit、8-bit 量化模型

### 5. 靈活擴展
- **自定義模型**: 通過 Modelfile 自定義系統提示和參數
- **LangChain 整合**: 無縫接入 LangChain 生態
- **OpenAI 兼容**: 兼容 OpenAI API 格式

## 安裝

### 系統要求
- **macOS**: macOS 11 或更高版本
- **Linux**: Ubuntu 18.04 或更高版本
- **Windows**: Windows 10 或更高版本
- **內存**: 至少 8GB RAM（推薦 16GB+）
- **硬碟**: 至少 10GB 可用空間

### 安裝 Ollama

**macOS:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
下載並運行安裝程序：https://ollama.com/download/windows

### 驗證安裝
```bash
ollama --version
```

### 安裝 Python 依賴
```bash
pip install -r requirements.txt
```

## 支持的模型

### 文本生成模型

| 模型名稱 | 參數量 | 內存需求 | 用途 |
|---------|--------|----------|------|
| llama3.3 | 70B | 40GB | 最新 Llama 模型，性能強大 |
| llama3.2 | 1B/3B | 2-4GB | 輕量級模型，適合邊緣設備 |
| mistral | 7B | 4GB | 高性能開源模型 |
| mixtral | 8x7B | 26GB | MoE 架構，性能優異 |
| gemma2 | 2B/9B/27B | 2-16GB | Google 最新開源模型 |
| qwen2.5 | 0.5B-72B | 1-40GB | 阿里巴巴通義千問 |
| phi4 | 14B | 8GB | 微軟小型高效模型 |
| deepseek-r1 | 7B/70B | 4-40GB | 推理能力強的模型 |

### 多模態模型

| 模型名稱 | 功能 | 內存需求 |
|---------|------|----------|
| llava | 圖像理解 | 6GB |
| llava-phi3 | 輕量級視覺模型 | 4GB |
| bakllava | 圖像分析 | 6GB |

### 嵌入模型

| 模型名稱 | 維度 | 用途 |
|---------|------|------|
| nomic-embed-text | 768 | 文本嵌入 |
| mxbai-embed-large | 1024 | 高質量嵌入 |
| all-minilm | 384 | 輕量級嵌入 |

## 快速開始

### 1. 下載模型
```bash
ollama pull llama3.2
```

### 2. 運行模型
```bash
ollama run llama3.2
```

### 3. Python 使用
```python
import ollama

response = ollama.chat(model='llama3.2', messages=[
    {'role': 'user', 'content': '你好，請介紹一下自己'}
])
print(response['message']['content'])
```

## 使用案例

### 1. 個人助手
- 離線 AI 助手，保護隱私
- 文檔摘要和問答
- 代碼生成和審查

### 2. 企業應用
- **內網部署**: 在企業內網中部署，保護敏感數據
- **知識庫問答**: 構建企業知識庫 RAG 系統
- **文檔處理**: 自動化文檔分析和生成

### 3. 開發測試
- **原型開發**: 快速測試 LLM 應用原型
- **成本控制**: 開發階段使用本地模型，節省 API 費用
- **性能測試**: 測試不同模型的性能表現

### 4. 教育研究
- **AI 教學**: 教授 LLM 原理和應用
- **算法研究**: 研究提示工程和模型行為
- **離線演示**: 無需網絡的課堂演示

### 5. 多模態應用
- **圖像分析**: 使用視覺模型分析圖片
- **文檔理解**: 處理包含圖表的文檔
- **視覺問答**: 基於圖像的問答系統

### 6. RAG 系統
- **本地向量數據庫**: 結合 ChromaDB、FAISS
- **文檔檢索**: 智能文檔搜索和問答
- **知識管理**: 構建個人或企業知識庫

## 示例文件說明

本目錄包含 10 個完整的示例文件，涵蓋 Ollama 的各個方面：

1. **01_快速開始.py** - Ollama 安裝、基本配置和簡單對話
2. **02_模型管理.py** - 模型下載、列出、刪除等管理操作
3. **03_對話生成.py** - Chat Completion、多輪對話、角色設定
4. **04_流式輸出.py** - Streaming 響應、實時輸出
5. **05_嵌入向量.py** - 文本嵌入、相似度計算、語義搜索
6. **06_多模態.py** - Vision 模型、圖像理解、視覺問答
7. **07_LangChain整合.py** - 與 LangChain 框架整合使用
8. **08_自定義模型.py** - Modelfile 創建、自定義系統提示
9. **09_API服務.py** - REST API 使用、OpenAI 兼容接口
10. **10_生產部署.py** - 生產環境配置、性能優化、監控

## 最佳實踐

### 1. 模型選擇
- 開發測試：使用小模型（1B-7B）
- 生產環境：根據性能需求選擇（7B-70B）
- 邊緣設備：使用量化模型和小參數模型

### 2. 性能優化
- 使用 GPU 加速
- 合理設置 num_ctx（上下文長度）
- 使用流式輸出提升體驗
- 預加載常用模型

### 3. 安全性
- 輸入驗證和過濾
- 輸出內容審查
- 資源使用限制
- 訪問控制

### 4. 監控運維
- 監控內存和 GPU 使用
- 記錄請求和響應
- 設置超時機制
- 定期更新模型

## 相關資源

- **官方網站**: https://ollama.com
- **GitHub**: https://github.com/ollama/ollama
- **模型庫**: https://ollama.com/library
- **官方文檔**: https://github.com/ollama/ollama/tree/main/docs
- **Python 庫**: https://github.com/ollama/ollama-python
- **Discord 社群**: https://discord.gg/ollama

## 系統架構

```
┌─────────────────────────────────────────┐
│          應用層                          │
│  Python/JS SDK │ REST API │ CLI         │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│          Ollama 服務                     │
│  - 模型管理                              │
│  - 請求處理                              │
│  - 內存管理                              │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│          推理引擎                        │
│  llama.cpp │ GGUF │ 量化支持            │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│          硬件層                          │
│  CPU │ NVIDIA GPU │ AMD GPU │ Metal     │
└─────────────────────────────────────────┘
```

## 版本信息

- **當前版本**: 0.5.0+
- **Python SDK**: 0.1.0+
- **支持的 Python 版本**: 3.8+

## 授權

Ollama 採用 MIT 授權。本示例代碼僅供學習參考使用。

---

**注意**: 使用 Ollama 需要下載和運行大型語言模型，請確保您的硬件配置滿足要求，並遵守相關模型的使用條款和授權協議。

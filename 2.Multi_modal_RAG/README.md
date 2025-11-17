# 多模態檢索生成（Multi-modal RAG）

## 📚 目錄
- [專案概述](#專案概述)
- [核心概念](#核心概念)
- [三種多模態 RAG 策略](#三種多模態-rag-策略)
- [目錄結構](#目錄結構)
- [快速開始](#快速開始)
- [詳細教程](#詳細教程)
- [進階主題](#進階主題)
- [常見問題](#常見問題)
- [相關資源](#相關資源)

## 專案概述

本專案提供完整的多模態 RAG（Retrieval-Augmented Generation）實作教程和範例。多模態 RAG 能夠處理包含文字、圖像、表格等多種內容類型的文件，並利用多模態大型語言模型（如 GPT-4o、Claude 3.5 Sonnet）進行智能檢索和答案生成。

### 為什麼需要多模態 RAG？

傳統的 RAG 系統主要處理純文字內容，但實際應用中的文件往往包含：
- 📊 **圖表和數據視覺化**：如財報圖表、趨勢分析圖
- 📋 **表格數據**：如財務報表、性能指標表
- 🖼️ **插圖和示意圖**：如架構圖、流程圖
- 📄 **混合內容**：文字與視覺元素的結合

忽略這些非文字內容會導致資訊損失，影響答案的準確性和完整性。

## 核心概念

### 什麼是 RAG？

RAG（Retrieval-Augmented Generation）是一種結合檢索和生成的技術：
1. **檢索（Retrieval）**：從知識庫中找出相關資訊
2. **增強（Augmented）**：將檢索到的資訊作為上下文
3. **生成（Generation）**：使用 LLM 基於上下文生成答案

### 多模態 RAG 的挑戰

1. **異質性資料處理**：文字、圖像、表格需要不同的處理方式
2. **語義理解**：如何理解圖像和表格的語義內容
3. **檢索策略**：如何有效檢索不同類型的內容
4. **上下文整合**：如何將多種模態的資訊整合到 LLM 提示中

## 三種多模態 RAG 策略

### 策略 1：多模態嵌入（Multi-modal Embeddings）

```
文件 → 提取文字和圖像 → 使用 CLIP 等模型嵌入
    ↓
  向量庫（文字 + 圖像向量）
    ↓
  相似性檢索 → 返回原始文字和圖像
    ↓
  多模態 LLM（如 GPT-4o）→ 生成答案
```

**優點**：
- ✅ 直接檢索原始圖像，保留完整視覺資訊
- ✅ 統一的嵌入空間，文字和圖像可以互相檢索

**缺點**：
- ❌ CLIP 等模型對某些領域的圖像理解可能不夠精確
- ❌ 需要多模態嵌入模型的額外成本

### 策略 2：圖像轉文字摘要（Image-to-Text）

```
文件 → 提取圖像 → 使用多模態 LLM 生成文字摘要
    ↓
  向量庫（純文字：原文 + 圖像摘要）
    ↓
  文字檢索 → 返回文字塊
    ↓
  文字 LLM（如 GPT-4）→ 生成答案
```

**優點**：
- ✅ 可以使用更便宜的純文字 LLM 進行答案生成
- ✅ 檢索邏輯簡單，使用標準的文字向量檢索

**缺點**：
- ❌ 圖像資訊經過摘要後可能損失細節
- ❌ 無法利用多模態 LLM 的視覺理解能力

### 策略 3：摘要檢索 + 原始內容生成（推薦）⭐

```
文件 → 提取文字、圖像、表格
    ↓
  生成摘要（用於檢索）
    ↓
  向量庫（存儲摘要） + 文件庫（存儲原始內容）
    ↓
  基於摘要檢索 → 返回原始文字和圖像
    ↓
  多模態 LLM → 生成答案
```

**優點**：
- ✅ **最佳語義檢索**：摘要經過優化，包含關鍵資訊
- ✅ **保留原始細節**：答案生成時使用原始圖像和文字
- ✅ **靈活性高**：可以針對不同類型內容使用不同的摘要策略
- ✅ **準確度高**：結合了檢索效率和生成質量

**本專案採用策略 3**

## 目錄結構

```
2.Multi_modal_RAG/
├── README.md                                    # 本文件
├── 01_理論與架構.md                            # 多模態 RAG 深度理論說明
├── 02_性能評估與優化.md                        # 性能基準測試和優化指南
├── 03_生產環境部署.md                          # 生產環境部署最佳實踐
├── langchain_cookbook_Multi_modal_RAG.ipynb    # 基礎教程（策略 3 實現）
├── advanced_multimodal_rag.ipynb               # 進階應用示例
├── utils/                                       # 實用工具腳本
│   ├── batch_processor.py                      # 批量處理 PDF 文件
│   ├── cost_calculator.py                      # API 成本計算器
│   └── image_quality_checker.py                # 圖像質量評估
├── cj/                                          # 示例數據（財務博客）
│   ├── cj.pdf
│   └── figure-*.jpg
├── pic1.png                                     # 文檔插圖
└── pic2.png                                     # 文檔插圖
```

## 快速開始

### 環境要求

- Python 3.8+
- OpenAI API Key（用於 GPT-4o）
- 系統依賴：
  - `poppler-utils`（PDF 處理）
  - `tesseract-ocr`（OCR 文字識別）

### 安裝步驟

#### 1. 克隆專案

```bash
git clone https://github.com/markl-a/LLM-agent-Demo.git
cd LLM-agent-Demo/2.Multi_modal_RAG
```

#### 2. 安裝 Python 依賴

```bash
pip install -U langchain openai langchain-chroma langchain-experimental
pip install "unstructured[all-docs]" pillow pydantic lxml matplotlib chromadb tiktoken
pip install langchain-openai pytesseract nltk==3.8.1
```

#### 3. 安裝系統依賴

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install poppler-utils tesseract-ocr
```

**MacOS:**
```bash
brew install poppler tesseract
```

**Windows:**
- Poppler: 下載 [poppler-windows](https://github.com/oschwartz10612/poppler-windows/releases/)
- Tesseract: 下載 [tesseract-installer](https://github.com/UB-Mannheim/tesseract/wiki)

#### 4. 設置環境變數

```bash
export OPENAI_API_KEY="your-api-key-here"
export LANGCHAIN_API_KEY="your-langsmith-key-here"  # 可選，用於追蹤
export LANGCHAIN_TRACING_V2="true"  # 可選
```

### 運行基礎教程

1. 啟動 Jupyter Notebook：
```bash
jupyter notebook langchain_cookbook_Multi_modal_RAG.ipynb
```

2. 依序執行每個 cell，觀察多模態 RAG 的完整流程

### 快速測試示例

```python
# 導入必要的模組
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

# 設置 API Key
import os
os.environ["OPENAI_API_KEY"] = "your-key-here"

# 執行查詢
query = "根據 EV/NTM 和 NTM 營收增長，哪些公司值得投資？"
docs = retriever.invoke(query)

# 使用 RAG 鏈生成答案
answer = chain_multimodal_rag.invoke(query)
print(answer)
```

## 詳細教程

### 教程 1：基礎多模態 RAG

**檔案**: `langchain_cookbook_Multi_modal_RAG.ipynb`

**學習目標**:
- 理解多模態 RAG 的基本概念
- 使用 Unstructured 解析 PDF 文件
- 生成圖像和表格摘要
- 構建多向量檢索器
- 實現完整的 RAG 鏈

**適合對象**: 初學者，想了解多模態 RAG 基礎的開發者

### 教程 2：進階應用

**檔案**: `advanced_multimodal_rag.ipynb`（即將推出）

**內容包括**:
- 使用不同的 LLM（Claude、Gemini）
- 自定義檢索策略
- 混合檢索（Hybrid Retrieval）
- Re-ranking 和檢索優化
- 批量處理和並行化

**適合對象**: 有基礎知識，想深入優化的開發者

## 進階主題

### 性能優化

1. **圖像大小優化**
   - 原始圖像：保留高質量用於答案生成
   - 摘要生成：可以使用壓縮版本以降低成本

2. **批次處理**
   - 使用 `batch()` 方法並行處理多個摘要生成請求
   - 設置合適的 `max_concurrency` 參數

3. **快取策略**
   - 快取圖像摘要和文字摘要
   - 使用持久化向量庫（而非 InMemoryStore）

### 成本控制

| 組件 | 模型選擇 | 成本影響 |
|------|---------|---------|
| 圖像摘要生成 | GPT-4o / GPT-4o-mini | 高 |
| 文字摘要生成 | GPT-4 / GPT-3.5-turbo | 中 |
| 答案生成 | GPT-4o | 高 |
| 嵌入 | text-embedding-3-small | 低 |

**成本優化建議**:
- 圖像摘要生成使用 GPT-4o-mini（成本降低 60%）
- 文字摘要可考慮使用 GPT-3.5-turbo
- 對於簡單查詢，可以只檢索文字，跳過圖像

### 準確度提升

1. **改進摘要質量**
   - 使用更詳細的提示詞
   - 針對不同類型內容（圖表、流程圖、表格）使用不同的摘要模板

2. **優化檢索**
   - 調整 `chunk_size` 和 `chunk_overlap`
   - 使用元數據過濾
   - 實現混合檢索（向量 + 關鍵字）

3. **增強上下文**
   - 檢索更多相關文檔
   - 使用 Re-ranking 提升檢索精度
   - 添加文檔來源資訊

## 常見問題

### Q1: 為什麼圖像檢索效果不好？

**可能原因**:
- 圖像摘要質量不佳：改進摘要提示詞
- 競爭的文字塊太多：增大文字塊大小並生成摘要
- 嵌入模型不適合：嘗試不同的嵌入模型

### Q2: 如何處理大型 PDF 文件？

```python
# 使用分塊策略
partition_pdf(
    filename=pdf_path,
    chunking_strategy="by_title",  # 按標題分塊
    max_characters=4000,           # 最大字符數
    new_after_n_chars=3800,        # 新塊開始位置
    combine_text_under_n_chars=2000  # 合併小塊
)
```

### Q3: 如何支援中文 PDF？

1. 安裝中文 Tesseract 語言包：
```bash
sudo apt-get install tesseract-ocr-chi-sim tesseract-ocr-chi-tra
```

2. 在 `partition_pdf` 中指定語言：
```python
partition_pdf(
    filename=pdf_path,
    languages=["chi_sim", "eng"]  # 簡體中文 + 英文
)
```

### Q4: 如何降低 API 成本？

1. 使用更便宜的模型：
   - 圖像摘要：`gpt-4o-mini` 而非 `gpt-4o`
   - 文字摘要：`gpt-3.5-turbo` 而非 `gpt-4`

2. 優化處理流程：
   - 快取已生成的摘要
   - 減少不必要的圖像處理
   - 批次處理以提高效率

3. 智能選擇：
   - 只在需要時才生成圖像摘要
   - 簡單查詢只使用文字檢索

### Q5: 支援哪些文件格式？

使用 Unstructured 可以處理：
- PDF (.pdf)
- Word (.docx, .doc)
- PowerPoint (.pptx, .ppt)
- Excel (.xlsx, .xls)
- HTML (.html)
- Markdown (.md)
- 圖像 (.jpg, .png, .gif, .bmp)

## 最佳實踐

### ✅ 推薦做法

1. **文件預處理**
   - 檢查 PDF 質量（是否可搜索、圖像清晰度）
   - 統一文件格式和命名規範
   - 移除敏感資訊

2. **摘要生成**
   - 為不同類型內容（圖表、表格、流程圖）設計專門的提示詞
   - 包含足夠的上下文資訊以提升檢索效果
   - 定期評估摘要質量

3. **向量庫管理**
   - 使用持久化存儲（Chroma、Pinecone 等）
   - 定期備份向量庫
   - 實現版本控制

4. **監控和評估**
   - 使用 LangSmith 追蹤執行過程
   - 收集用戶反饋
   - 定期評估檢索和生成質量

### ❌ 避免事項

1. ❌ 不要忽略圖像大小優化（會增加成本和延遲）
2. ❌ 不要使用過小的文字塊（會導致上下文碎片化）
3. ❌ 不要跳過錯誤處理（API 可能失敗）
4. ❌ 不要在生產環境中使用 InMemoryStore（數據會丟失）

## 相關資源

### 官方文檔

- [LangChain 多模態 RAG 文檔](https://python.langchain.com/docs/use_cases/multi_modal)
- [OpenAI Vision API](https://platform.openai.com/docs/guides/vision)
- [Unstructured 文檔](https://unstructured-io.github.io/unstructured/)
- [Chroma 向量庫文檔](https://docs.trychroma.com/)

### 相關博客文章

- [LangChain Blog: Semi-structured Multi-modal RAG](https://blog.langchain.dev/semi-structured-multi-modal-rag/)
- [OpenAI: GPT-4 with Vision](https://openai.com/research/gpt-4v-system-card)

### 社群資源

- [LangChain GitHub](https://github.com/langchain-ai/langchain)
- [LangChain Discord](https://discord.gg/langchain)

### 相關專案

- [Multi-modal RAG with CLIP](https://github.com/langchain-ai/langchain/blob/master/cookbook/multi_modal_RAG_chroma.ipynb)
- [LLaVA: Large Language and Vision Assistant](https://llava.hliu.cc/)

## 技術支援

如有問題或建議，請：
1. 查看 [常見問題](#常見問題) 部分
2. 提交 [GitHub Issue](https://github.com/markl-a/LLM-agent-Demo/issues)
3. 參考官方文檔和社群資源

## 授權

本專案採用 MIT 授權條款。

---

**更新日誌**

- 2024-11-17: 初始版本發布，包含基礎教程和完整文檔
- 預計更新: 進階應用示例、批量處理工具、成本計算器

**貢獻者**

感謝所有為本專案做出貢獻的開發者！

---

*本專案基於 LangChain 官方教程擴展和優化，旨在為中文社群提供更完整的多模態 RAG 學習資源。*

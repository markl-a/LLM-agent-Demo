# GraphRAG - Microsoft 知識圖譜增強 RAG 框架

## 簡介

GraphRAG 是 Microsoft 開發的創新型檢索增強生成（RAG）框架，它通過構建知識圖譜來增強傳統 RAG 系統的能力。該框架利用 LLM 從非結構化文本中自動提取實體、關係和社區結構，從而支持更複雜的查詢和推理任務。

GraphRAG 不僅能回答具體的事實性問題，還能處理需要全局理解的複雜查詢，例如："這個數據集的主要主題是什麼？" 或 "不同概念之間有什麼關聯？"

## 核心特點

### 1. **自動知識圖譜構建**
- 使用 LLM 自動從文本中提取實體和關係
- 無需人工標註或預定義本體
- 支持大規模文檔集的處理

### 2. **社區檢測算法**
- 採用 Leiden 算法進行層次化社區檢測
- 自動識別文檔中的主題和概念集群
- 生成多層次的摘要信息

### 3. **雙模式搜索**
- **Local Search（本地搜索）**：針對特定實體和關係的精確查詢
- **Global Search（全局搜索）**：基於社區摘要的宏觀理解
- 支持混合搜索策略以獲得最佳結果

### 4. **可擴展架構**
- 支持大規模數據集（百萬級文檔）
- 並行處理能力
- 靈活的配置選項

### 5. **企業級功能**
- 數據索引和緩存機制
- 結果可解釋性（提供證據鏈）
- 支持多種數據源格式

## 安裝

### 基礎安裝

```bash
pip install graphrag
```

### 從源碼安裝

```bash
git clone https://github.com/microsoft/graphrag.git
cd graphrag
pip install -e .
```

### 環境配置

創建 `.env` 文件並配置 API 密鑰：

```env
GRAPHRAG_API_KEY=your_openai_api_key
GRAPHRAG_LLM_MODEL=gpt-4-turbo-preview
GRAPHRAG_EMBEDDING_MODEL=text-embedding-3-small
```

## 快速開始

### 1. 初始化項目

```bash
graphrag init --root ./ragtest
```

### 2. 準備數據

將文檔放入 `./ragtest/input` 目錄。

### 3. 構建索引

```bash
graphrag index --root ./ragtest
```

### 4. 執行查詢

```bash
# 全局搜索
graphrag query --root ./ragtest --method global "這個數據集的主要主題是什麼?"

# 本地搜索
graphrag query --root ./ragtest --method local "John Smith 是誰?"
```

## 使用案例

### 1. **企業知識管理**
- 自動構建企業文檔的知識圖譜
- 快速定位相關信息和專家
- 發現隱藏的知識關聯

### 2. **研究文獻分析**
- 分析大量學術論文
- 識別研究趨勢和主題
- 發現跨領域的研究機會

### 3. **情報分析**
- 從多源信息中提取實體和關係
- 構建事件時間線
- 識別關鍵人物和組織網絡

### 4. **客戶支持**
- 構建產品知識圖譜
- 提供精準的問題解答
- 自動關聯相關文檔

### 5. **合規和風險管理**
- 分析法規文件和政策
- 識別合規風險點
- 追蹤政策變更影響

## 與傳統 RAG 對比

| 特性 | 傳統 RAG | GraphRAG |
|------|---------|----------|
| **數據結構** | 向量嵌入（扁平） | 知識圖譜（結構化） |
| **查詢類型** | 語義相似度搜索 | 實體關係查詢 + 語義搜索 |
| **全局理解** | ❌ 困難 | ✅ 優秀（通過社區摘要） |
| **可解釋性** | ⚠️ 一般 | ✅ 強（提供證據鏈） |
| **複雜推理** | ❌ 有限 | ✅ 支持多跳推理 |
| **數據準備** | 簡單（直接切塊） | 複雜（需構建圖譜） |
| **成本** | 低 | 中高（需額外 LLM 調用） |
| **適用場景** | 簡單 QA | 複雜分析、探索性查詢 |

### 傳統 RAG 的優勢
- 實現簡單，快速上手
- 成本較低
- 適合簡單的事實性問答

### GraphRAG 的優勢
- 能回答需要全局理解的問題
- 支持複雜的多跳推理
- 提供更好的可解釋性
- 能發現數據中的隱藏模式

### 何時使用 GraphRAG？

**推薦使用 GraphRAG 的場景：**
- 需要理解整體趨勢和主題
- 需要分析實體之間的複雜關係
- 數據集較大且包含豐富的關聯信息
- 需要高度的結果可解釋性

**可能更適合傳統 RAG 的場景：**
- 簡單的事實性問答
- 成本預算有限
- 數據集較小且結構簡單
- 需要快速原型開發

## 工作流程

1. **文檔處理**
   - 將文檔分塊（chunks）
   - 為每個塊生成嵌入向量

2. **實體提取**
   - 使用 LLM 識別實體（人物、地點、組織等）
   - 提取實體屬性和描述

3. **關係抽取**
   - 識別實體之間的關係
   - 構建知識圖譜

4. **社區檢測**
   - 使用 Leiden 算法檢測社區
   - 為每個社區生成摘要

5. **查詢處理**
   - Local Search：基於實體和關係
   - Global Search：基於社區摘要
   - 生成最終回答

## 技術架構

```
GraphRAG
├── 數據輸入層
│   ├── 文檔加載器
│   ├── 文本分塊器
│   └── 預處理器
│
├── 圖譜構建層
│   ├── 實體提取器（LLM）
│   ├── 關係提取器（LLM）
│   ├── 屬性增強器
│   └── 圖譜存儲
│
├── 社區檢測層
│   ├── Leiden 算法
│   ├── 層次聚類
│   └── 摘要生成器（LLM）
│
├── 索引層
│   ├── 向量索引
│   ├── 圖譜索引
│   └── 社區索引
│
└── 查詢層
    ├── Local Search Engine
    ├── Global Search Engine
    ├── 混合搜索引擎
    └── 答案生成器（LLM）
```

## 配置選項

GraphRAG 提供豐富的配置選項，可在 `settings.yaml` 中自定義：

```yaml
# LLM 配置
llm:
  model: gpt-4-turbo-preview
  temperature: 0
  max_tokens: 4000

# 嵌入配置
embeddings:
  model: text-embedding-3-small
  batch_size: 16

# 分塊配置
chunks:
  size: 1200
  overlap: 100

# 實體提取配置
entity_extraction:
  max_gleanings: 1
  entity_types: [person, organization, location, event]

# 社區配置
community:
  algorithm: leiden
  max_cluster_size: 10
```

## 性能優化建議

1. **並行處理**：啟用多進程處理大規模數據集
2. **緩存策略**：緩存 LLM 響應以降低成本
3. **批處理**：批量處理嵌入生成請求
4. **增量更新**：支持增量索引以處理新文檔
5. **硬件加速**：使用 GPU 加速圖計算

## 限制與注意事項

1. **成本**：構建圖譜需要大量 LLM API 調用
2. **時間**：初始索引構建可能需要較長時間
3. **質量依賴**：結果質量高度依賴於 LLM 的提取能力
4. **語言支持**：主要優化為英文，其他語言效果可能有差異

## 資源

- **官方網站**：https://microsoft.github.io/graphrag/
- **GitHub**：https://github.com/microsoft/graphrag
- **論文**：[From Local to Global: A Graph RAG Approach](https://arxiv.org/abs/2404.16130)
- **文檔**：https://microsoft.github.io/graphrag/docs/
- **示例**：https://github.com/microsoft/graphrag/tree/main/examples

## 許可證

GraphRAG 採用 MIT 許可證開源。

## 貢獻

歡迎貢獻！請查看 [貢獻指南](https://github.com/microsoft/graphrag/blob/main/CONTRIBUTING.md)。

## 支持

- GitHub Issues：https://github.com/microsoft/graphrag/issues
- 討論區：https://github.com/microsoft/graphrag/discussions

---

**更新日期**：2025-12-31
**框架版本**：0.3.0+

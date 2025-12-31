# Txtai 語義搜索引擎完整範例

## 框架簡介

Txtai 是一個功能全面的開源語義搜索引擎，構建在 Transformers 和句子嵌入模型之上。它提供了強大的 AI 驅動搜索、問答、摘要和工作流功能，可以輕鬆整合到任何應用程序中。

### 核心特點

#### 1. 語義搜索 🔍
- 基於語義理解的搜索，而非關鍵詞匹配
- 支持多語言搜索
- 向量相似度計算
- 混合搜索（語義 + 關鍵詞）

```python
from txtai import Embeddings

# 創建嵌入索引
embeddings = Embeddings()
embeddings.index([(0, "AI is transforming technology", None)])

# 語義搜索
results = embeddings.search("artificial intelligence")
```

#### 2. 嵌入模型整合 🧠
- 支持 Hugging Face 所有句子轉換器模型
- 自定義嵌入模型
- 多模態嵌入（文本、圖像、音頻）
- GPU 加速支持

支持的模型：
- sentence-transformers (SBERT)
- OpenAI embeddings
- Cohere embeddings
- 自訂模型

#### 3. SQL 查詢接口 💾
- 使用 SQL 語法查詢嵌入數據
- 支持複雜查詢和聚合
- 與傳統數據庫思維一致
- 強大的過濾和排序功能

```python
# SQL 查詢示例
embeddings.search("SELECT id, text, score FROM txtai WHERE similar('AI technology')")
```

#### 4. 文檔摘要 📄
- 抽取式摘要
- 生成式摘要
- 多文檔摘要
- 自定義摘要長度

```python
from txtai import Summary

summary = Summary()
text = summary("Long document text here...")
```

#### 5. 問答系統 ❓
- 基於上下文的問答
- 支持多個文檔源
- 答案提取和生成
- 置信度評分

```python
from txtai import Extractor

extractor = Extractor(embeddings, "distilbert-base-cased-distilled-squad")
answer = extractor([("What is AI?", ["AI is artificial intelligence..."])])
```

#### 6. 工作流引擎 ⚙️
- 構建複雜的 NLP 流程
- 任務編排和自動化
- 可配置的處理管道
- 支持條件邏輯

```python
from txtai import Application

# 定義工作流
app = Application("""
embeddings:
    path: sentence-transformers/all-MiniLM-L6-v2
workflow:
    search:
        tasks:
            - action: embeddings
""")
```

#### 7. 圖分析 🕸️
- 知識圖譜構建
- 實體關係提取
- 圖遍歷和查詢
- 社交網絡分析

#### 8. 多模態支持 🎨
- 文本嵌入
- 圖像嵌入
- 音頻嵌入
- 跨模態搜索

```python
# 圖像搜索
embeddings = Embeddings({
    "content": True,
    "format": "clip"
})
```

## 安裝指南

### 基礎安裝
```bash
pip install txtai
```

### 完整安裝（包含所有功能）
```bash
# 安裝所有依賴
pip install txtai[all]

# 或分別安裝特定功能
pip install txtai[pipeline]    # NLP 管道
pip install txtai[graph]        # 圖分析
pip install txtai[similarity]   # 相似度計算
pip install txtai[vectors]      # 向量存儲
pip install txtai[scoring]      # 評分功能
```

### 開發環境設置
```bash
# 創建虛擬環境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安裝完整依賴
pip install txtai[all] sentence-transformers

# 安裝可選依賴
pip install transformers torch numpy pandas
```

## 快速開始

### 基本語義搜索

```python
from txtai import Embeddings

# 創建嵌入索引
embeddings = Embeddings()

# 添加文檔
data = [
    "Python is a programming language",
    "Java is used for enterprise applications",
    "JavaScript runs in browsers"
]

embeddings.index([(i, text, None) for i, text in enumerate(data)])

# 搜索
results = embeddings.search("coding language", 2)
for result in results:
    print(f"Score: {result['score']:.4f}, Text: {result['text']}")
```

### 持久化存儲

```python
# 保存索引
embeddings.save("index")

# 加載索引
embeddings = Embeddings()
embeddings.load("index")
```

### 問答系統

```python
from txtai import Embeddings, Extractor

# 創建嵌入和提取器
embeddings = Embeddings({"path": "sentence-transformers/nli-mpnet-base-v2"})
extractor = Extractor(embeddings, "distilbert-base-cased-distilled-squad")

# 索引數據
data = ["Paris is the capital of France", "The Eiffel Tower is in Paris"]
embeddings.index([(i, text, None) for i, text in enumerate(data)])

# 提問
answer = extractor([("What is the capital of France?", data)])
print(answer)
```

## 範例文件導覽

### 基礎篇

#### 01_快速開始.py
- Txtai 基本概念
- 創建第一個嵌入索引
- 簡單的語義搜索
- 結果處理和展示

#### 02_語義搜索.py
- 高級搜索功能
- 過濾和排序
- 批量搜索
- 搜索參數調優

#### 03_嵌入索引.py
- 不同的嵌入模型
- 索引配置選項
- 批量索引
- 索引優化技巧

#### 04_SQL查詢.py
- SQL 查詢語法
- 複雜查詢示例
- JOIN 操作
- 聚合和分組

### 進階篇

#### 05_文檔摘要.py
- 抽取式摘要
- 生成式摘要
- 多文檔摘要
- 自定義摘要策略

#### 06_問答系統.py
- 基於上下文的問答
- 多文檔問答
- 答案提取
- 置信度評估

#### 07_工作流.py
- 工作流定義
- 任務編排
- 數據處理管道
- 條件邏輯

#### 08_圖分析.py
- 知識圖譜構建
- 實體關係提取
- 圖查詢
- 可視化

### 高級篇

#### 09_多模態.py
- CLIP 模型整合
- 圖像搜索
- 跨模態搜索
- 多模態索引

#### 10_API服務.py
- RESTful API 構建
- FastAPI 整合
- 服務部署
- 性能優化

## 核心概念

### Embeddings（嵌入）

Embeddings 是 txtai 的核心類，用於創建和管理向量索引。

```python
from txtai import Embeddings

# 基本配置
embeddings = Embeddings()

# 高級配置
embeddings = Embeddings({
    "path": "sentence-transformers/all-MiniLM-L6-v2",  # 模型路徑
    "content": True,                                     # 存儲原始內容
    "scoring": {"method": "bm25"},                       # 評分方法
    "backend": "faiss",                                  # 向量存儲後端
})
```

### 索引數據格式

數據以元組列表的形式索引：`(id, text, metadata)`

```python
data = [
    (0, "First document", {"category": "A"}),
    (1, "Second document", {"category": "B"}),
]
embeddings.index(data)
```

### 搜索選項

```python
# 基本搜索
results = embeddings.search("query", limit=10)

# 帶過濾的搜索
results = embeddings.search(
    "query",
    limit=10,
    weights=0.5,  # BM25 權重
)

# SQL 搜索
results = embeddings.search(
    "SELECT * FROM txtai WHERE similar('query') AND category = 'A'"
)
```

### Pipeline（管道）

Pipeline 提供各種 NLP 任務的接口。

```python
from txtai import Summary, Labels, Similarity

# 摘要管道
summary = Summary()
text = summary("Long text here...")

# 標籤管道
labels = Labels()
result = labels("Text to classify", ["positive", "negative"])

# 相似度管道
similarity = Similarity()
score = similarity("text1", "text2")
```

### Application（應用）

Application 提供完整的配置驅動接口。

```python
from txtai import Application

# YAML 配置
config = """
embeddings:
    path: sentence-transformers/all-MiniLM-L6-v2

workflow:
    search:
        tasks:
            - action: embeddings
              select: text
"""

app = Application(config)
app.add([
    {"text": "Document 1"},
    {"text": "Document 2"}
])
app.index()

results = app.search("query")
```

## 最佳實踐

### 1. 模型選擇

根據需求選擇合適的模型：

```python
# 快速且輕量（推薦用於大多數場景）
embeddings = Embeddings({
    "path": "sentence-transformers/all-MiniLM-L6-v2"
})

# 多語言支持
embeddings = Embeddings({
    "path": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
})

# 高質量（但較慢）
embeddings = Embeddings({
    "path": "sentence-transformers/all-mpnet-base-v2"
})

# 領域特定（如法律、醫療）
embeddings = Embeddings({
    "path": "nlpaueb/legal-bert-base-uncased"
})
```

### 2. 索引優化

```python
# 批量索引（更高效）
def batch_index(embeddings, data, batch_size=1000):
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        embeddings.index(batch, update=True)

# 使用內容存儲
embeddings = Embeddings({
    "content": True,      # 存儲原始文本
    "objects": True,      # 存儲對象
    "functions": []       # 自定義函數
})
```

### 3. 性能調優

```python
# GPU 加速
embeddings = Embeddings({
    "path": "sentence-transformers/all-MiniLM-L6-v2",
    "gpu": True,
    "batch": 128  # GPU 批次大小
})

# 向量存儲後端選擇
embeddings = Embeddings({
    "backend": "faiss",     # 快速（推薦）
    # "backend": "annoy",   # 內存友好
    # "backend": "hnswlib", # 精確搜索
})
```

### 4. 混合搜索

結合語義搜索和關鍵詞搜索：

```python
embeddings = Embeddings({
    "scoring": {
        "method": "bm25",
        "terms": True
    }
})

# 調整權重（0-1，0 為純語義，1 為純 BM25）
results = embeddings.search("query", weights=0.5)
```

### 5. 內存管理

```python
# 延遲加載
embeddings = Embeddings()
embeddings.load("index", False)  # 不加載到內存

# 流式索引
def stream_documents():
    for doc in large_dataset:
        yield doc

embeddings.index(stream_documents())
```

## 高級功能

### 向量數據庫

Txtai 可以作為完整的向量數據庫使用：

```python
from txtai import Embeddings

embeddings = Embeddings({
    "path": "sentence-transformers/all-MiniLM-L6-v2",
    "content": True,
    "backend": "faiss",
    "scoring": {"method": "bm25"}
})

# CRUD 操作
embeddings.index(data)           # Create/Update
embeddings.search("query")       # Read
embeddings.delete([0, 1, 2])     # Delete
embeddings.reindex()             # 重建索引
```

### 雲端部署

```python
# 使用 txtai 的 API 服務器
# 配置文件: app.yml
"""
embeddings:
    path: sentence-transformers/all-MiniLM-L6-v2
    content: true

api:
    host: 0.0.0.0
    port: 8000
"""

# 啟動服務
# CONFIG=app.yml uvicorn "txtai.api:app"
```

### 自定義組件

```python
from txtai.pipeline import Pipeline

class CustomPipeline(Pipeline):
    def __call__(self, texts):
        # 自定義處理邏輯
        return [text.upper() for text in texts]

# 使用自定義管道
pipeline = CustomPipeline()
results = pipeline(["text1", "text2"])
```

## 實際應用場景

### 1. 文檔搜索引擎
- 企業知識庫搜索
- 法律文檔檢索
- 學術論文搜索
- 技術文檔查找

### 2. 推薦系統
- 內容推薦
- 產品推薦
- 相似文章推薦
- 用戶匹配

### 3. 客服系統
- FAQ 自動匹配
- 智能問答
- 工單分類
- 知識庫查詢

### 4. 內容分析
- 文本分類
- 情感分析
- 主題建模
- 實體識別

## 參考資源

### 官方文檔
- [Txtai 官網](https://neuml.github.io/txtai/)
- [API 文檔](https://neuml.github.io/txtai/api/)
- [GitHub 倉庫](https://github.com/neuml/txtai)

### 教程和示例
- [官方示例](https://github.com/neuml/txtai/tree/master/examples)
- [Hugging Face 集成](https://huggingface.co/neuml)
- [博客文章](https://neuml.hashnode.dev/)

### 社區
- [GitHub Discussions](https://github.com/neuml/txtai/discussions)
- [Twitter](https://twitter.com/neuml)

## 常見問題

### Q: Txtai 與 Elasticsearch 的區別？

**A:** Txtai 專注於語義搜索，使用向量嵌入；Elasticsearch 主要是關鍵詞搜索。Txtai 更適合需要理解語義的場景，且更輕量易用。

### Q: 如何選擇嵌入模型？

**A:**
- 英文：all-MiniLM-L6-v2（快速）、all-mpnet-base-v2（高質量）
- 多語言：paraphrase-multilingual-MiniLM-L12-v2
- 特定領域：選擇領域特定的 BERT 模型

### Q: 如何處理大規模數據？

**A:**
1. 使用批量索引
2. 選擇合適的後端（FAISS 用於大規模）
3. 考慮分片策略
4. 使用流式處理

### Q: 支持實時更新嗎？

**A:** 支持，使用 `update=True` 參數：
```python
embeddings.index(new_data, update=True)
```

## 性能基準

### 索引速度
- 10K 文檔：~10 秒
- 100K 文檔：~2 分鐘
- 1M 文檔：~20 分鐘

### 搜索速度
- 10K 索引：< 10ms
- 100K 索引：< 50ms
- 1M 索引：< 200ms

*基於 all-MiniLM-L6-v2 模型，CPU: Intel i7*

## 貢獻指南

歡迎貢獻新的範例或改進現有代碼！

1. Fork 本倉庫
2. 創建功能分支
3. 編寫清晰的中文註釋
4. 測試代碼
5. 提交 Pull Request

## 授權

本範例集採用 MIT 授權，可自由使用和修改。

## 更新日誌

- **2025-01**: 創建初始範例集
- 包含 10 個完整範例
- 涵蓋所有核心功能
- 完整繁體中文註釋

---

**開始探索** → 從 `01_快速開始.py` 開始你的 Txtai 之旅！

# Weaviate - 開源向量搜索引擎

## 簡介

Weaviate 是一個開源的向量數據庫和搜索引擎,專為存儲和檢索向量嵌入而設計。它結合了向量搜索、關鍵字搜索和結構化數據過濾,為構建 AI 驅動的應用提供完整的解決方案。Weaviate 支持多種 AI 模型,包括 OpenAI、Cohere、Hugging Face 等,並提供強大的 GraphQL 和 RESTful API。

Weaviate 特別適合構建語義搜索、推薦系統、問答系統、RAG（檢索增強生成）應用等需要智能數據檢索的場景。它原生支持向量化、分類和問答等 AI 模塊,大大簡化了 AI 應用的開發流程。

## 核心特點

### 1. 混合搜索能力
- **向量搜索**: 基於語義相似度的智能搜索
- **關鍵字搜索**: 傳統的 BM25 算法搜索
- **混合搜索**: 結合向量和關鍵字搜索,獲得最佳結果
- **過濾器**: 支持複雜的元數據過濾

### 2. 多模型支持
- **OpenAI**: GPT-4, text-embedding-3, DALL-E
- **Cohere**: 嵌入和重排序模型
- **Hugging Face**: 數千種開源模型
- **自定義模型**: 支持自定義向量化模型
- **多模態**: 支持文本、圖像等多種數據類型

### 3. 生成式搜索
- **RAG 整合**: 原生支持檢索增強生成
- **問答模塊**: 直接回答用戶問題
- **摘要生成**: 自動生成搜索結果摘要
- **引用追蹤**: 保留資料來源引用

### 4. 高性能架構
- **HNSW 索引**: 高效的近似最近鄰搜索
- **水平擴展**: 支持分片和複製
- **持久化存儲**: 數據持久化保存
- **實時更新**: 支持實時數據插入和更新

### 5. GraphQL API
- **靈活查詢**: 使用 GraphQL 進行複雜查詢
- **類型安全**: 強類型的查詢語言
- **關係查詢**: 支持跨對象引用查詢
- **批量操作**: 高效的批量數據操作

### 6. 多租戶支持
- **數據隔離**: 多個租戶共享基礎設施
- **資源管理**: 獨立的資源配額管理
- **安全性**: 租戶間數據完全隔離

## 安裝

### 使用 Docker（推薦）

**快速啟動:**
```bash
docker run -p 8080:8080 -p 50051:50051 semitechnologies/weaviate:latest
```

**使用 Docker Compose:**
```yaml
version: '3.4'
services:
  weaviate:
    image: semitechnologies/weaviate:latest
    ports:
      - "8080:8080"
      - "50051:50051"
    environment:
      QUERY_DEFAULTS_LIMIT: 25
      AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED: 'true'
      PERSISTENCE_DATA_PATH: '/var/lib/weaviate'
      DEFAULT_VECTORIZER_MODULE: 'text2vec-openai'
      ENABLE_MODULES: 'text2vec-openai,generative-openai'
      CLUSTER_HOSTNAME: 'node1'
    volumes:
      - weaviate_data:/var/lib/weaviate

volumes:
  weaviate_data:
```

### 使用 Kubernetes

```bash
kubectl apply -f https://weaviate.io/deployment/weaviate.yaml
```

### Weaviate Cloud Service（WCS）

訪問 https://console.weaviate.cloud 創建免費的雲端實例

### 安裝 Python 客戶端

```bash
pip install -r requirements.txt
```

## 系統要求

### 最小配置
- **CPU**: 2 核心
- **內存**: 4GB RAM
- **硬碟**: 10GB 可用空間
- **Python**: 3.8+

### 生產環境推薦
- **CPU**: 8+ 核心
- **內存**: 16GB+ RAM
- **硬碟**: SSD 存儲,至少 100GB
- **網絡**: 1Gbps+

## 核心概念

### Schema（模式）
Schema 定義了數據的結構,包括類（Classes）和屬性（Properties）:

```python
schema = {
    "class": "Article",
    "properties": [
        {
            "name": "title",
            "dataType": ["text"]
        },
        {
            "name": "content",
            "dataType": ["text"]
        },
        {
            "name": "author",
            "dataType": ["text"]
        },
        {
            "name": "publishDate",
            "dataType": ["date"]
        }
    ]
}
```

### 向量化模塊
Weaviate 支持多種向量化模塊:
- `text2vec-openai`: OpenAI 嵌入模型
- `text2vec-cohere`: Cohere 嵌入模型
- `text2vec-huggingface`: Hugging Face 模型
- `text2vec-transformers`: 本地 Transformers 模型
- `multi2vec-clip`: 多模態 CLIP 模型

### 搜索類型

**1. 向量搜索（Near Vector）:**
```python
result = client.query.get("Article", ["title", "content"]) \
    .with_near_vector({"vector": embedding}) \
    .with_limit(10) \
    .do()
```

**2. 語義搜索（Near Text）:**
```python
result = client.query.get("Article", ["title", "content"]) \
    .with_near_text({"concepts": ["AI and machine learning"]}) \
    .with_limit(10) \
    .do()
```

**3. 混合搜索:**
```python
result = client.query.get("Article", ["title", "content"]) \
    .with_hybrid(query="machine learning", alpha=0.5) \
    .with_limit(10) \
    .do()
```

## 使用案例

### 1. 語義搜索引擎
- **智能搜索**: 理解用戶意圖,返回語義相關結果
- **多語言支持**: 跨語言搜索能力
- **個性化**: 基於用戶歷史的個性化搜索

### 2. RAG 應用
- **問答系統**: 構建智能問答機器人
- **文檔助手**: 基於文檔的 AI 助手
- **知識庫**: 企業知識管理系統

### 3. 推薦系統
- **內容推薦**: 基於內容相似度的推薦
- **用戶畫像**: 構建和匹配用戶興趣
- **個性化推送**: 智能內容分發

### 4. 圖像搜索
- **以圖搜圖**: 基於視覺相似度搜索
- **多模態搜索**: 文本搜圖,圖搜文本
- **視覺問答**: 圖像理解和問答

### 5. 客戶支持
- **智能客服**: 自動回答客戶問題
- **工單分類**: 自動分類和路由工單
- **知識檢索**: 快速找到相關解決方案

### 6. 電商應用
- **產品搜索**: 智能產品發現
- **相似商品**: 找到相似產品
- **用戶評論分析**: 語義分析用戶反饋

## 示例文件說明

本目錄包含 10 個完整的示例文件,涵蓋 Weaviate 的各個方面:

1. **01_快速開始.py** - Weaviate 連接、基本配置和簡單查詢
2. **02_Schema設計.py** - Schema 創建、更新、刪除和最佳實踐
3. **03_數據導入.py** - 批量導入、單條插入、數據驗證
4. **04_向量搜索.py** - Near Vector、Near Text、Near Object 搜索
5. **05_混合搜索.py** - 向量+關鍵字混合搜索、權重調整
6. **06_過濾器.py** - Where 過濾器、複雜條件、地理位置過濾
7. **07_生成式搜索.py** - RAG、問答、摘要生成
8. **08_多租戶.py** - 多租戶配置、數據隔離、資源管理
9. **09_備份恢復.py** - 數據備份、恢復、遷移策略
10. **10_生產部署.py** - 生產配置、監控、性能優化

## 最佳實踐

### 1. Schema 設計
- 合理規劃 Class 和 Property 結構
- 選擇合適的向量化模塊
- 使用適當的數據類型
- 設置合理的索引策略

### 2. 性能優化
- 使用批量導入提高效率
- 合理設置 HNSW 參數（ef、efConstruction、maxConnections）
- 啟用緩存提升查詢速度
- 使用分片處理大規模數據

### 3. 搜索優化
- 混合搜索平衡精確度和召回率
- 使用過濾器縮小搜索範圍
- 設置合理的 limit 參數
- 啟用重排序提升結果質量

### 4. 安全性
- 啟用身份驗證和授權
- 使用 HTTPS 加密通信
- 定期備份數據
- 監控異常訪問

### 5. 多租戶策略
- 合理分配資源配額
- 使用租戶隔離保護數據
- 監控各租戶使用情況
- 規劃擴展策略

## 架構對比

### Weaviate vs 其他向量數據庫

| 特性 | Weaviate | Pinecone | Milvus | Qdrant |
|-----|----------|----------|--------|--------|
| 開源 | ✅ | ❌ | ✅ | ✅ |
| 雲服務 | ✅ | ✅ | ✅ | ✅ |
| GraphQL API | ✅ | ❌ | ❌ | ❌ |
| 混合搜索 | ✅ | ❌ | ✅ | ✅ |
| 生成式搜索 | ✅ | ❌ | ❌ | ❌ |
| 多租戶 | ✅ | ✅ | ✅ | ✅ |
| 自托管 | ✅ | ❌ | ✅ | ✅ |

## 性能指標

### 搜索延遲
- **小規模（<10萬向量）**: < 10ms
- **中規模（10萬-100萬）**: < 50ms
- **大規模（>100萬）**: < 100ms

### 吞吐量
- **寫入**: 10,000+ 對象/秒（批量）
- **查詢**: 1,000+ 查詢/秒
- **向量維度**: 支持 1-65535 維

## 相關資源

- **官方網站**: https://weaviate.io
- **GitHub**: https://github.com/weaviate/weaviate
- **官方文檔**: https://weaviate.io/developers/weaviate
- **Python 客戶端**: https://github.com/weaviate/weaviate-python-client
- **Discord 社群**: https://discord.gg/weaviate
- **Weaviate Cloud**: https://console.weaviate.cloud
- **部落格**: https://weaviate.io/blog
- **教學影片**: https://www.youtube.com/@Weaviate

## 系統架構

```
┌─────────────────────────────────────────────────┐
│              應用層                              │
│  Python SDK │ GraphQL │ REST API │ gRPC        │
└──────────────┬──────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────┐
│              Weaviate 核心                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ 查詢引擎 │  │ 索引管理 │  │ 向量化   │      │
│  └──────────┘  └──────────┘  └──────────┘      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ 過濾器   │  │ 生成模塊 │  │ 分類器   │      │
│  └──────────┘  └──────────┘  └──────────┘      │
└──────────────┬──────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────┐
│              存儲層                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ HNSW索引 │  │ 倒排索引 │  │ 對象存儲 │      │
│  └──────────┘  └──────────┘  └──────────┘      │
└──────────────┬──────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────┐
│          外部 AI 模型（可選）                     │
│  OpenAI │ Cohere │ Hugging Face │ 自定義       │
└─────────────────────────────────────────────────┘
```

## 版本信息

- **Weaviate**: 1.25+
- **Python 客戶端**: 4.0+
- **支持的 Python 版本**: 3.8+
- **GraphQL**: v1

## 授權

Weaviate 採用 BSD-3-Clause 授權。本示例代碼僅供學習參考使用。

---

**注意**: 使用 Weaviate 時,如果使用第三方 AI 模型（如 OpenAI、Cohere）,需要相應的 API 密鑰並遵守其使用條款。自托管時請確保有足夠的計算資源以支持向量搜索操作。

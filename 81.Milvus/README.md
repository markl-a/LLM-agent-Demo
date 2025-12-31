# Milvus - 雲原生向量數據庫

## 簡介

Milvus 是一個開源的雲原生向量數據庫,專為大規模向量數據的存儲、檢索和分析而設計。它支持在萬億級向量數據中進行毫秒級搜索,廣泛應用於 AI、機器學習和深度學習領域。Milvus 提供豐富的向量索引類型、靈活的部署方案以及與主流 AI 框架的無縫整合。

Milvus 由 Zilliz 公司開發,是 LF AI & Data Foundation 的畢業項目,擁有活躍的開源社區和企業級支持。它特別適合構建推薦系統、圖像/視頻搜索、自然語言處理、藥物發現等需要大規模向量檢索的應用。

## 核心特點

### 1. 高性能向量搜索
- **萬億級規模**: 支持萬億級向量數據
- **毫秒級延遲**: 在十億級數據中實現毫秒級搜索
- **多種索引**: FLAT、IVF_FLAT、IVF_SQ8、IVF_PQ、HNSW、ANNOY等
- **GPU 加速**: 支持 GPU 加速的索引構建和搜索

### 2. 豐富的索引類型
- **FLAT**: 精確搜索,適合小規模數據
- **IVF_FLAT**: 倒排文件索引,平衡精度和速度
- **IVF_SQ8**: 標量量化,減少內存使用
- **IVF_PQ**: 乘積量化,極致壓縮
- **HNSW**: 圖索引,高召回率
- **ANNOY**: 樹索引,適合靜態數據
- **DiskANN**: 基於磁盤的索引,支持超大規模

### 3. 雲原生架構
- **存算分離**: 計算和存儲獨立擴展
- **高可用**: 支持多副本和故障轉移
- **彈性伸縮**: 根據負載自動擴縮容
- **微服務**: 組件化設計,靈活部署

### 4. 多種部署方式
- **Milvus Lite**: 輕量級版本,適合開發和測試
- **Milvus Standalone**: 單機版,簡單部署
- **Milvus Cluster**: 集群版,生產環境
- **Zilliz Cloud**: 完全託管的雲服務

### 5. 豐富的功能
- **混合搜索**: 向量搜索 + 標量過濾
- **多向量搜索**: 支持多個向量字段
- **時間旅行**: 查詢歷史數據
- **動態 Schema**: 靈活的字段定義
- **分區**: 數據分區管理
- **索引構建**: 在線和離線索引構建

### 6. 生態整合
- **LangChain**: 原生支持 LangChain
- **LlamaIndex**: 無縫整合 LlamaIndex
- **Haystack**: 支持 Haystack 框架
- **Spark**: 與 Apache Spark 整合
- **PyTorch/TensorFlow**: 直接使用模型輸出

## 安裝

### 使用 Milvus Lite（推薦用於開發）

```bash
pip install pymilvus
```

Milvus Lite 會自動隨 pymilvus 安裝,無需額外配置。

### 使用 Docker Compose（Standalone）

**docker-compose.yml:**
```yaml
version: '3.5'

services:
  etcd:
    image: quay.io/coreos/etcd:v3.5.5
    environment:
      - ETCD_AUTO_COMPACTION_MODE=revision
      - ETCD_AUTO_COMPACTION_RETENTION=1000
      - ETCD_QUOTA_BACKEND_BYTES=4294967296
    volumes:
      - ${DOCKER_VOLUME_DIRECTORY:-.}/volumes/etcd:/etcd
    command: etcd -advertise-client-urls=http://127.0.0.1:2379 -listen-client-urls http://0.0.0.0:2379 --data-dir /etcd

  minio:
    image: minio/minio:RELEASE.2023-03-20T20-16-18Z
    environment:
      MINIO_ACCESS_KEY: minioadmin
      MINIO_SECRET_KEY: minioadmin
    volumes:
      - ${DOCKER_VOLUME_DIRECTORY:-.}/volumes/minio:/minio_data
    command: minio server /minio_data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 20s
      retries: 3

  standalone:
    image: milvusdb/milvus:v2.3.3
    command: ["milvus", "run", "standalone"]
    environment:
      ETCD_ENDPOINTS: etcd:2379
      MINIO_ADDRESS: minio:9000
    volumes:
      - ${DOCKER_VOLUME_DIRECTORY:-.}/volumes/milvus:/var/lib/milvus
    ports:
      - "19530:19530"
      - "9091:9091"
    depends_on:
      - "etcd"
      - "minio"

networks:
  default:
    name: milvus
```

**啟動:**
```bash
docker-compose up -d
```

### 使用 Helm（Kubernetes 集群）

```bash
helm repo add milvus https://milvus-io.github.io/milvus-helm/
helm install my-release milvus/milvus
```

### 使用 Zilliz Cloud

訪問 https://cloud.zilliz.com 創建免費試用帳號

### 安裝 Python SDK

```bash
pip install -r requirements.txt
```

## 系統要求

### 最小配置（Standalone）
- **CPU**: 4 核心
- **內存**: 8GB RAM
- **硬碟**: 50GB 可用空間
- **Python**: 3.8+

### 生產環境推薦（Cluster）
- **CPU**: 16+ 核心
- **內存**: 64GB+ RAM
- **硬碟**: SSD 存儲,至少 500GB
- **網絡**: 10Gbps+
- **GPU**: NVIDIA GPU (可選,用於加速)

## 核心概念

### Collection（集合）
Collection 是 Milvus 中的數據容器,類似於關係數據庫中的表:

```python
from pymilvus import Collection, FieldSchema, CollectionSchema, DataType

# 定義字段
fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=False),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=128),
    FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=200),
]

# 創建 Schema
schema = CollectionSchema(fields=fields, description="示例集合")

# 創建 Collection
collection = Collection(name="example", schema=schema)
```

### 索引類型

**1. FLAT（精確搜索）:**
```python
index_params = {
    "index_type": "FLAT",
    "metric_type": "L2"
}
```

**2. IVF_FLAT（倒排索引）:**
```python
index_params = {
    "index_type": "IVF_FLAT",
    "metric_type": "L2",
    "params": {"nlist": 1024}
}
```

**3. HNSW（圖索引）:**
```python
index_params = {
    "index_type": "HNSW",
    "metric_type": "L2",
    "params": {
        "M": 16,
        "efConstruction": 200
    }
}
```

### 距離度量

- **L2**: 歐幾里得距離（適合大多數場景）
- **IP**: 內積（適合歸一化向量）
- **COSINE**: 餘弦相似度
- **HAMMING**: 漢明距離（適合二進制向量）
- **JACCARD**: Jaccard 距離

### 分區（Partition）
分區用於數據隔離和性能優化:

```python
# 創建分區
collection.create_partition("partition_2023")

# 插入到特定分區
collection.insert(data, partition_name="partition_2023")

# 在特定分區搜索
collection.search(vectors, "embedding", params, partition_names=["partition_2023"])
```

## 使用案例

### 1. 圖像搜索
- **以圖搜圖**: 基於視覺特徵的相似圖片檢索
- **人臉識別**: 人臉特徵匹配
- **商品推薦**: 視覺相似商品推薦

### 2. 推薦系統
- **協同過濾**: 基於用戶/物品嵌入的推薦
- **內容推薦**: 基於內容相似度的推薦
- **實時推薦**: 毫秒級推薦響應

### 3. 自然語言處理
- **語義搜索**: 理解查詢意圖的智能搜索
- **問答系統**: RAG 應用
- **文檔去重**: 相似文檔檢測
- **文本分類**: 基於嵌入的分類

### 4. 視頻分析
- **視頻檢索**: 基於內容的視頻搜索
- **鏡頭檢測**: 相似鏡頭識別
- **版權保護**: 視頻指紋匹配

### 5. 音頻處理
- **音樂推薦**: 相似音樂檢索
- **語音識別**: 聲紋匹配
- **聲音分類**: 音頻特徵分類

### 6. 科研應用
- **藥物發現**: 分子結構相似性搜索
- **基因組學**: DNA 序列匹配
- **材料科學**: 材料屬性預測

## 示例文件說明

本目錄包含 10 個完整的示例文件,涵蓋 Milvus 的各個方面:

1. **01_快速開始.py** - Milvus 連接、集合創建和基本操作
2. **02_集合管理.py** - 集合創建、刪除、Schema 設計
3. **03_數據插入.py** - 單條插入、批量插入、數據驗證
4. **04_向量搜索.py** - 相似性搜索、參數調優、結果處理
5. **05_標量過濾.py** - 混合搜索、過濾條件、表達式查詢
6. **06_分區管理.py** - 分區創建、數據隔離、分區搜索
7. **07_索引優化.py** - 索引類型選擇、性能調優
8. **08_LangChain整合.py** - 與 LangChain 整合構建 RAG
9. **09_集群部署.py** - 集群部署、高可用配置
10. **10_性能調優.py** - 性能優化、監控、故障排查

## 最佳實踐

### 1. 索引選擇
- **小數據(<10萬)**: FLAT
- **中等數據(10萬-1000萬)**: IVF_FLAT 或 HNSW
- **大數據(>1000萬)**: IVF_PQ 或 DiskANN
- **高召回率需求**: HNSW
- **內存受限**: IVF_SQ8 或 IVF_PQ

### 2. 性能優化
- 合理設置 nprobe（IVF）或 ef（HNSW）
- 使用分區減小搜索範圍
- 批量插入提升吞吐量
- 適當的副本數提升查詢並發

### 3. 數據管理
- 合理規劃分區策略
- 定期壓縮和優化
- 使用時間旅行查詢歷史數據
- 實施數據備份策略

### 4. 安全性
- 啟用用戶認證和授權
- 使用 TLS 加密通信
- 網絡隔離和訪問控制
- 定期安全審計

## 性能指標

### 搜索性能
- **QPS**: 10,000+ 查詢/秒（單節點）
- **延遲**: <10ms（百萬級數據）
- **召回率**: >99%（適當參數配置）
- **規模**: 支持萬億級向量

### 寫入性能
- **插入**: 30,000+ 向量/秒（批量）
- **索引構建**: 1000萬向量約 10-30 分鐘（根據索引類型）

## 架構對比

### Milvus vs 其他向量數據庫

| 特性 | Milvus | Weaviate | Pinecone | Qdrant |
|-----|--------|----------|----------|--------|
| 開源 | ✅ | ✅ | ❌ | ✅ |
| 雲服務 | ✅ (Zilliz) | ✅ (WCS) | ✅ | ✅ |
| 最大規模 | 萬億級 | 十億級 | 十億級 | 十億級 |
| GPU 加速 | ✅ | ❌ | ❌ | ❌ |
| 存算分離 | ✅ | ❌ | ✅ | ❌ |
| 索引類型 | 10+ | 2 | 1 | 3 |
| 多語言 SDK | ✅ | ✅ | ✅ | ✅ |
| 標量過濾 | ✅ | ✅ | ✅ | ✅ |

## 相關資源

- **官方網站**: https://milvus.io
- **GitHub**: https://github.com/milvus-io/milvus
- **官方文檔**: https://milvus.io/docs
- **Python SDK**: https://github.com/milvus-io/pymilvus
- **Slack 社群**: https://milvus.io/slack
- **Zilliz Cloud**: https://cloud.zilliz.com
- **部落格**: https://milvus.io/blog
- **教學影片**: https://www.youtube.com/@MilvusVectorDatabase

## 系統架構

```
┌─────────────────────────────────────────────────┐
│              應用層                              │
│  Python SDK │ Go SDK │ Java SDK │ Node.js SDK  │
└──────────────┬──────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────┐
│          Milvus 訪問層                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │  Proxy   │  │  Proxy   │  │  Proxy   │      │
│  └──────────┘  └──────────┘  └──────────┘      │
└──────────────┬──────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────┐
│          協調服務（Coordinator）                 │
│  Root │ Query │ Data │ Index                   │
└──────────────┬──────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────┐
│          工作節點（Worker Nodes）                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │Query Node│  │Data Node │  │Index Node│      │
│  └──────────┘  └──────────┘  └──────────┘      │
└──────────────┬──────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────┐
│          存儲層                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ MinIO/S3 │  │   etcd   │  │  Pulsar  │      │
│  │(對象存儲)│  │ (元數據) │  │ (消息隊列)│      │
│  └──────────┘  └──────────┘  └──────────┘      │
└─────────────────────────────────────────────────┘
```

## 版本信息

- **Milvus**: 2.3+
- **PyMilvus**: 2.3+
- **支持的 Python 版本**: 3.8+
- **協議**: gRPC

## 授權

Milvus 採用 Apache License 2.0 授權。本示例代碼僅供學習參考使用。

---

**注意**: Milvus 適合大規模向量搜索場景。小規模應用可以使用 Milvus Lite,生產環境建議使用 Milvus Cluster 或 Zilliz Cloud 以獲得更好的性能和可靠性。

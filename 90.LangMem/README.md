# LangMem - Agent 記憶管理

## 簡介

LangMem 是 LangChain 的長期記憶擴展框架,為 AI Agent 提供持久化的記憶能力。它允許 Agent 在多次對話中保留和檢索信息,實現真正的上下文感知和個性化交互。LangMem 支持多種記憶類型、靈活的存儲後端以及高效的記憶檢索機制。

LangMem 專為構建需要長期記憶的智能 Agent 而設計,可以讓 Agent 記住用戶偏好、歷史對話、學習經驗等信息,從而提供更加智能和個性化的服務。它與 LangChain 無縫整合,可以輕鬆添加到現有的 LangChain 應用中。

## 核心特點

### 1. 多種記憶類型
- **短期記憶**: 對話期間的臨時信息存儲
- **長期記憶**: 跨會話的持久化信息存儲
- **語義記憶**: 基於語義相似度的知識存儲
- **情節記憶**: 時間序列的事件記錄
- **工作記憶**: 當前任務的活動信息

### 2. 靈活的存儲後端
- **Redis**: 高性能的內存數據庫
- **PostgreSQL**: 關係型數據庫存儲
- **MongoDB**: 文檔型數據庫
- **向量數據庫**: Milvus、Weaviate 等
- **本地文件**: JSON、SQLite 等輕量級存儲

### 3. 智能記憶檢索
- **相似度搜索**: 基於向量的語義搜索
- **時間過濾**: 按時間範圍檢索記憶
- **重要性排序**: 根據記憶重要性排序
- **記憶融合**: 多個記憶源的融合
- **自動摘要**: 長記憶的自動壓縮

### 4. 記憶管理
- **記憶壓縮**: 自動壓縮舊記憶節省空間
- **記憶遺忘**: 模擬人類的遺忘曲線
- **記憶更新**: 動態更新過時信息
- **記憶去重**: 避免重複記憶
- **記憶歸檔**: 歸檔不常用的記憶

### 5. 多 Agent 支持
- **獨立記憶**: 每個 Agent 獨立的記憶空間
- **共享記憶**: Agent 間的知識共享
- **記憶同步**: 分佈式環境下的記憶同步
- **訪問控制**: 記憶的讀寫權限管理
- **記憶隔離**: 不同租戶的記憶隔離

### 6. 生產級特性
- **高性能**: 毫秒級記憶檢索
- **可擴展**: 支持海量記憶存儲
- **容錯性**: 自動備份和恢復
- **監控**: 記憶使用情況監控
- **安全性**: 記憶加密和訪問控制

## 安裝

### 基礎安裝

```bash
pip install langmem
```

### 完整安裝（包含所有後端支持）

```bash
pip install langmem[all]
```

### 安裝特定後端

```bash
# Redis 後端
pip install langmem[redis]

# PostgreSQL 後端
pip install langmem[postgres]

# 向量數據庫後端
pip install langmem[vector]
```

### 從 requirements.txt 安裝

```bash
pip install -r requirements.txt
```

## 系統要求

### 最小配置
- **Python**: 3.8+
- **內存**: 512MB RAM
- **硬碟**: 100MB 可用空間

### 生產環境推薦
- **Python**: 3.10+
- **內存**: 4GB+ RAM
- **硬碟**: 10GB+ SSD 存儲
- **Redis**: 6.0+ (用於高性能記憶存儲)
- **PostgreSQL**: 13+ (用於持久化存儲)

## 核心概念

### 記憶類型

**1. 短期記憶（Short-term Memory）**
```python
from langmem import ShortTermMemory

memory = ShortTermMemory()
memory.add("用戶喜歡喝咖啡")
```

**2. 長期記憶（Long-term Memory）**
```python
from langmem import LongTermMemory

memory = LongTermMemory(backend="redis")
memory.add("用戶的生日是 1990-01-01")
```

**3. 語義記憶（Semantic Memory）**
```python
from langmem import SemanticMemory

memory = SemanticMemory(embedding_model="openai")
memory.add("Python 是一種編程語言")
results = memory.search("什麼是 Python?", k=5)
```

**4. 情節記憶（Episodic Memory）**
```python
from langmem import EpisodicMemory

memory = EpisodicMemory()
memory.add_episode({
    "timestamp": "2024-01-01 10:00:00",
    "event": "用戶登錄系統",
    "context": {"location": "台北"}
})
```

### 記憶檢索

**相似度搜索:**
```python
results = memory.search(
    query="用戶的偏好",
    k=10,
    similarity_threshold=0.7
)
```

**時間過濾:**
```python
from datetime import datetime, timedelta

results = memory.search(
    query="最近的活動",
    time_range=(
        datetime.now() - timedelta(days=7),
        datetime.now()
    )
)
```

**重要性排序:**
```python
results = memory.search(
    query="重要信息",
    sort_by="importance",
    limit=10
)
```

### 記憶壓縮

```python
from langmem import MemoryCompressor

compressor = MemoryCompressor(model="gpt-4")
compressed = compressor.compress(
    memories=old_memories,
    target_tokens=500
)
memory.add(compressed)
```

### 多 Agent 記憶

```python
from langmem import MultiAgentMemory

# 創建共享記憶
shared_memory = MultiAgentMemory(
    agent_id="agent_1",
    shared=True
)

# 創建獨立記憶
private_memory = MultiAgentMemory(
    agent_id="agent_1",
    shared=False
)
```

## 使用案例

### 1. 個性化助手
- **用戶偏好記憶**: 記住用戶的喜好和習慣
- **對話歷史**: 保留歷史對話上下文
- **任務記錄**: 追蹤待辦事項和已完成任務
- **學習能力**: 從用戶反饋中學習

### 2. 客戶服務 Agent
- **客戶檔案**: 記住客戶的基本信息
- **服務歷史**: 保留歷史服務記錄
- **問題追蹤**: 追蹤未解決的問題
- **知識庫**: 累積常見問題解答

### 3. 教育輔導 Agent
- **學習進度**: 記錄學生的學習進度
- **知識掌握**: 追蹤知識點掌握情況
- **個性化教學**: 根據學習記憶調整教學策略
- **錯誤分析**: 分析常見錯誤模式

### 4. 研究助手
- **文獻記憶**: 記住已閱讀的文獻
- **研究筆記**: 保存研究想法和發現
- **引用管理**: 管理引用和參考文獻
- **知識圖譜**: 構建知識關聯網絡

### 5. 遊戲 NPC
- **玩家互動**: 記住與玩家的互動歷史
- **世界狀態**: 追蹤遊戲世界的變化
- **劇情發展**: 根據歷史事件推進劇情
- **個性化對話**: 基於記憶的動態對話

### 6. 企業知識管理
- **知識沉澱**: 累積組織知識
- **經驗傳承**: 保留專家經驗
- **決策支持**: 基於歷史數據的決策建議
- **合規記錄**: 保留審計和合規記錄

## 示例文件說明

本目錄包含 10 個完整的示例文件,涵蓋 LangMem 的各個方面:

1. **01_快速開始.py** - LangMem 基礎配置和簡單記憶操作
2. **02_短期記憶.py** - 對話期間的臨時記憶管理
3. **03_長期記憶.py** - 持久化記憶存儲和檢索
4. **04_語義記憶.py** - 基於向量的語義搜索
5. **05_情節記憶.py** - 時間序列事件記錄
6. **06_記憶檢索.py** - 高級記憶檢索技巧
7. **07_記憶壓縮.py** - 記憶壓縮和摘要
8. **08_多Agent記憶.py** - 多 Agent 記憶管理
9. **09_持久化存儲.py** - Redis、PostgreSQL 等後端整合
10. **10_生產應用.py** - 完整的生產級應用示例

## 最佳實踐

### 1. 記憶類型選擇
- **對話上下文**: 使用短期記憶
- **用戶信息**: 使用長期記憶
- **知識檢索**: 使用語義記憶
- **事件追蹤**: 使用情節記憶

### 2. 存儲後端選擇
- **開發/測試**: 本地文件或內存
- **小規模應用**: SQLite 或 Redis
- **中規模應用**: PostgreSQL + Redis
- **大規模應用**: 向量數據庫 + PostgreSQL + Redis

### 3. 性能優化
- 定期壓縮舊記憶
- 使用緩存加速檢索
- 適當的索引策略
- 批量操作減少 I/O

### 4. 記憶管理
- 設置記憶過期時間
- 實施記憶重要性評分
- 定期清理無用記憶
- 備份重要記憶

### 5. 安全性
- 加密敏感記憶
- 實施訪問控制
- 審計記憶訪問
- 遵守隱私法規

## 架構對比

### LangMem vs 其他記憶框架

| 特性 | LangMem | Mem0 | Zep | LangChain Memory |
|-----|---------|------|-----|------------------|
| LangChain 整合 | ✅ 原生 | ⚠️ 需適配 | ✅ 支持 | ✅ 原生 |
| 多種記憶類型 | ✅ | ✅ | ⚠️ 有限 | ⚠️ 基礎 |
| 語義搜索 | ✅ | ✅ | ✅ | ⚠️ 需配置 |
| 記憶壓縮 | ✅ | ✅ | ✅ | ❌ |
| 多 Agent | ✅ | ✅ | ⚠️ 有限 | ❌ |
| 存儲後端 | ✅ 豐富 | ⚠️ 有限 | ✅ 豐富 | ⚠️ 基礎 |
| 開源 | ✅ | ✅ | ⚠️ 部分 | ✅ |
| 生產級 | ✅ | ✅ | ✅ | ⚠️ 基礎 |

## 相關資源

- **官方網站**: https://langmem.dev
- **GitHub**: https://github.com/langchain/langmem
- **官方文檔**: https://docs.langmem.dev
- **PyPI**: https://pypi.org/project/langmem
- **Discord**: https://discord.gg/langchain
- **教學**: https://docs.langmem.dev/tutorials
- **示例**: https://github.com/langchain/langmem-examples
- **部落格**: https://blog.langchain.dev/tag/memory

## 系統架構

```
┌─────────────────────────────────────────────────┐
│              應用層                              │
│     LangChain Agent │ Custom Application       │
└──────────────┬──────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────┐
│          LangMem 核心層                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │短期記憶  │  │長期記憶  │  │語義記憶  │      │
│  └──────────┘  └──────────┘  └──────────┘      │
│  ┌──────────┐  ┌──────────┐                    │
│  │情節記憶  │  │工作記憶  │                    │
│  └──────────┘  └──────────┘                    │
└──────────────┬──────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────┐
│          記憶管理層                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ 記憶檢索 │  │ 記憶壓縮 │  │ 記憶融合 │      │
│  └──────────┘  └──────────┘  └──────────┘      │
└──────────────┬──────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────┐
│          存儲層                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │  Redis   │  │PostgreSQL│  │  Milvus  │      │
│  └──────────┘  └──────────┘  └──────────┘      │
│  ┌──────────┐  ┌──────────┐                    │
│  │ MongoDB  │  │   File   │                    │
│  └──────────┘  └──────────┘                    │
└─────────────────────────────────────────────────┘
```

## 性能指標

### 記憶檢索性能
- **短期記憶**: <1ms
- **長期記憶**: <10ms (Redis), <50ms (PostgreSQL)
- **語義搜索**: <100ms (向量數據庫)
- **批量檢索**: 1000+ 記憶/秒

### 存儲容量
- **Redis**: 建議 <100萬 條記憶
- **PostgreSQL**: 支持億級記憶
- **向量數據庫**: 支持十億級記憶

## 版本信息

- **LangMem**: 0.1+
- **LangChain**: 0.1+
- **支持的 Python 版本**: 3.8+
- **Redis**: 6.0+ (可選)
- **PostgreSQL**: 13+ (可選)

## 授權

LangMem 採用 MIT License 授權。本示例代碼僅供學習參考使用。

---

**注意**: LangMem 是一個新興的記憶管理框架,API 可能會有變化。建議在生產環境使用前充分測試,並關注官方更新。對於簡單應用,可以使用 LangChain 內建的記憶功能;對於需要複雜記憶管理的應用,LangMem 提供了更強大的功能。

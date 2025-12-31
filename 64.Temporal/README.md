# Temporal - 可靠的分佈式工作流編排框架

## 簡介

Temporal 是由 Uber 開發的開源分佈式工作流編排平台，專為構建可靠、可擴展的長時間運行應用而設計。它通過將業務邏輯與底層基礎設施解耦，使開發者能夠專注於核心業務邏輯，而無需擔心重試、超時、錯誤處理等複雜問題。

Temporal 的核心理念是將複雜的分佈式系統問題（如狀態管理、故障恢復、重試邏輯）抽象化，讓開發者能夠用簡單的代碼編寫複雜的工作流。

### 主要特性

- **可靠性保證**：自動處理重試、超時和故障恢復
- **持久化執行**：工作流狀態自動持久化，進程重啟不影響執行
- **長時間運行**：支持運行數天、數月甚至數年的工作流
- **可見性**：完整的執行歷史和狀態追蹤
- **可擴展性**：水平擴展支持大規模並發執行

## 核心特點

### 1. **工作流即代碼（Workflow as Code）**
- 使用常規編程語言（Python、Go、Java 等）編寫工作流
- 無需 YAML 或 JSON 配置文件
- 充分利用語言的類型安全和 IDE 支持

### 2. **故障處理**
- 自動重試失敗的 Activity
- 可配置的重試策略（指數退避、最大嘗試次數等）
- 支援補償事務（Saga 模式）
- 超時控制（開始到關閉、執行、調度到開始等）

### 3. **狀態管理**
- 工作流狀態自動持久化到數據庫
- 支持暫停和恢復執行
- 進程崩潰後自動恢復
- 支持長時間休眠（Sleep 數天/數月）

### 4. **版本控制**
- 支持工作流代碼的版本升級
- 舊版本工作流實例可繼續運行
- 平滑遷移到新版本

### 5. **可觀測性**
- Web UI 查看工作流執行狀態
- 完整的執行歷史記錄
- 支持 Signal 和 Query 進行實時交互
- 內建指標和追蹤

## 安裝

### 安裝 Temporal Server

**使用 Docker Compose（推薦）：**

```bash
# 下載 docker-compose 配置
git clone https://github.com/temporalio/docker-compose.git
cd docker-compose

# 啟動服務
docker-compose up -d

# 查看 Web UI
# 訪問 http://localhost:8080
```

**使用 Temporal CLI：**

```bash
# 安裝 Temporal CLI
brew install temporal  # macOS
# 或下載二進制文件：https://github.com/temporalio/cli/releases

# 啟動本地開發服務器
temporal server start-dev
```

### 安裝 Python SDK

```bash
# 安裝依賴
pip install -r requirements.txt

# 或單獨安裝
pip install temporalio
```

## 核心概念

### Workflow（工作流）
- 定義業務流程的邏輯
- 必須是確定性的（相同輸入產生相同輸出）
- 自動處理持久化和故障恢復

### Activity（活動）
- 執行實際的業務操作（API 調用、數據庫操作等）
- 可以失敗和重試
- 不需要是確定性的

### Worker（工作器）
- 執行 Workflow 和 Activity 的進程
- 可以水平擴展
- 輪詢任務隊列並執行任務

### Task Queue（任務隊列）
- Workflow 和 Activity 的路由機制
- 實現負載均衡和任務分發

## 使用案例

### 1. **訂單處理系統**
```python
# 處理電商訂單：庫存檢查 → 支付 → 發貨 → 通知
@workflow.defn
class OrderWorkflow:
    @workflow.run
    async def run(self, order_id: str) -> str:
        # 檢查庫存
        await workflow.execute_activity(
            check_inventory, order_id,
            start_to_close_timeout=timedelta(seconds=30)
        )

        # 處理支付
        await workflow.execute_activity(
            process_payment, order_id,
            start_to_close_timeout=timedelta(minutes=5)
        )

        # 安排發貨
        await workflow.execute_activity(
            schedule_shipping, order_id,
            start_to_close_timeout=timedelta(minutes=10)
        )

        return "Order completed"
```

### 2. **數據管道編排**
- ETL 流程：提取 → 轉換 → 加載
- 多階段數據處理
- 失敗自動重試和告警

### 3. **微服務編排**
- Saga 分佈式事務
- 服務間協調
- 補償邏輯處理

### 4. **定時任務調度**
- Cron 任務調度
- 週期性數據同步
- 報表生成

### 5. **人機交互流程**
- 審批流程
- 通過 Signal 接收外部輸入
- 等待人工決策

## 與其他工作流框架對比

| 特性 | Temporal | Apache Airflow | Celery | AWS Step Functions |
|------|----------|----------------|--------|-------------------|
| **主要用途** | 通用工作流編排 | 數據管道調度 | 任務隊列 | AWS 服務編排 |
| **編程模型** | 代碼優先 | DAG 配置 | 任務裝飾器 | JSON 狀態機 |
| **長時間運行** | ✅ 優秀（年） | ⚠️ 有限（天） | ❌ 不適合 | ⚠️ 有限（1年） |
| **故障恢復** | ✅ 自動 | ⚠️ 需配置 | ⚠️ 需手動處理 | ✅ 自動 |
| **狀態持久化** | ✅ 內建 | ✅ 內建 | ❌ 需自行實現 | ✅ 內建 |
| **版本控制** | ✅ 原生支持 | ⚠️ 有限 | ❌ 不支持 | ⚠️ 有限 |
| **可觀測性** | ✅ Web UI + API | ✅ Web UI | ⚠️ 需集成 | ✅ AWS Console |
| **部署複雜度** | ⚠️ 中等 | ⚠️ 中等 | ✅ 簡單 | ✅ 託管服務 |
| **水平擴展** | ✅ 優秀 | ✅ 良好 | ✅ 良好 | ✅ 自動 |
| **多語言支持** | ✅ 多語言 | ✅ Python | ✅ Python | ❌ JSON only |
| **開源/閉源** | 開源 | 開源 | 開源 | 閉源（AWS） |
| **成本** | 免費（自託管） | 免費（自託管） | 免費 | 按使用付費 |

### 選擇建議

**選擇 Temporal 當：**
- 需要高可靠性的業務流程編排
- 工作流需要長時間運行（小時到年）
- 需要複雜的錯誤處理和重試邏輯
- 要求強一致性和故障恢復
- 需要人機交互（Signal/Query）

**選擇 Airflow 當：**
- 主要場景是數據管道和 ETL
- 需要豐富的調度功能（Cron、依賴管理）
- 團隊熟悉 Python 和 DAG 模型
- 需要大量預建連接器

**選擇 Celery 當：**
- 只需要簡單的異步任務隊列
- 不需要複雜的工作流編排
- 已有 Redis/RabbitMQ 基礎設施

**選擇 Step Functions 當：**
- 完全在 AWS 生態內
- 需要與 AWS 服務深度集成
- 願意付費使用託管服務

## 架構組件

### Server 端
- **Frontend Service**：處理 gRPC 請求
- **History Service**：管理工作流執行歷史
- **Matching Service**：任務隊列匹配
- **Worker Service**：內部後台任務

### 數據存儲
- **Cassandra / PostgreSQL / MySQL**：持久化存儲
- **Elasticsearch**（可選）：高級查詢和搜索

### Client 端
- **Worker**：執行工作流和活動
- **Client**：啟動和查詢工作流

## 快速開始

1. **啟動 Temporal Server**（見安裝部分）

2. **運行示例**：
```bash
# 啟動 Worker
python 01_快速開始.py

# 在另一個終端啟動工作流
python -c "from 01_快速開始 import run_workflow; import asyncio; asyncio.run(run_workflow())"
```

3. **查看 Web UI**：
   - 訪問 http://localhost:8080
   - 查看工作流執行狀態和歷史

## 示例文件說明

- `01_快速開始.py` - Temporal 基本概念和第一個工作流
- `02_Activity定義.py` - Activity 函數的定義和使用
- `03_工作流編排.py` - 複雜工作流編排（並行、串行、條件）
- `04_錯誤處理.py` - 重試策略、超時控制、補償邏輯
- `05_定時任務.py` - Cron 調度和定時執行
- `06_信號通信.py` - Signal 和 Query 實現人機交互
- `07_子工作流.py` - 子工作流調用和組合
- `08_長流程.py` - 長時間運行任務和休眠
- `09_版本控制.py` - 工作流版本管理和遷移
- `10_生產部署.py` - 生產環境部署配置和最佳實踐

## 學習資源

- **官方文檔**：https://docs.temporal.io/
- **GitHub**：https://github.com/temporalio/temporal
- **Python SDK**：https://github.com/temporalio/sdk-python
- **教程**：https://learn.temporal.io/
- **社區論壇**：https://community.temporal.io/
- **示例庫**：https://github.com/temporalio/samples-python

## 最佳實踐

1. **工作流設計**
   - 保持工作流邏輯簡潔，複雜邏輯放在 Activity 中
   - 避免在工作流中進行非確定性操作
   - 使用合適的超時設置

2. **Activity 設計**
   - Activity 應該是冪等的
   - 合理設置重試策略
   - 避免長時間阻塞操作

3. **錯誤處理**
   - 使用自動重試處理瞬時故障
   - 實現補償邏輯處理業務失敗
   - 記錄詳細的錯誤信息

4. **性能優化**
   - 合理配置 Worker 數量
   - 使用並行 Activity 提高吞吐量
   - 避免過大的工作流歷史

5. **監控和告警**
   - 監控工作流失敗率
   - 設置執行時間告警
   - 追蹤任務隊列延遲

## 注意事項

⚠️ **運行示例前請確保：**
1. Temporal Server 已啟動（本地或 Docker）
2. 已安裝所有依賴包
3. 配置好環境變量（如需要）
4. Worker 進程正在運行

⚠️ **工作流編程限制：**
- 不能使用隨機數生成器
- 不能使用當前時間（使用 workflow.now()）
- 不能進行網絡調用（應放在 Activity 中）
- 不能讀寫外部狀態（應使用工作流變量）

## License

本示例代碼採用 MIT License。Temporal 框架本身採用 MIT License。

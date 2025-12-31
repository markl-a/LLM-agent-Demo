# Prefect - 現代化數據工作流編排框架

## 簡介

Prefect 是新一代工作流編排框架，旨在解決數據工程和 AI 應用中複雜工作流的管理問題。它採用了"負反饋工程"（Negative Engineering）的設計理念，讓開發者專注於編寫業務邏輯，而不是擔心基礎設施問題。

Prefect 2.0 是對工作流編排的全新思考，摒棄了傳統 DAG（有向無環圖）框架的限制，提供了更靈活、更強大的工作流定義方式。它將 Python 函數轉換為可觀測、可重試、可調度的工作流任務。

**核心理念**：
- **代碼即工作流**：使用原生 Python 代碼定義工作流
- **動態性優先**：支持動態任務生成和條件分支
- **可觀測性內建**：自動追蹤所有執行狀態和日誌
- **本地優先**：先在本地開發測試，再部署到生產環境

## 核心特點

### 1. 簡潔的 API 設計

使用 `@task` 和 `@flow` 裝飾器即可將普通 Python 函數轉換為工作流：

```python
from prefect import task, flow

@task
def extract_data():
    return [1, 2, 3]

@task
def transform(data):
    return [x * 2 for x in data]

@flow
def etl_pipeline():
    data = extract_data()
    result = transform(data)
    return result
```

### 2. 動態工作流

不同於傳統 DAG 框架，Prefect 支持真正的動態工作流：

```python
@flow
def dynamic_workflow(n: int):
    results = []
    for i in range(n):  # 動態生成任務
        results.append(process_item(i))
    return results
```

### 3. 強大的任務編排

- **並行執行**：自動並行執行獨立任務
- **重試機制**：內建指數退避重試
- **超時控制**：任務級別的超時設置
- **結果緩存**：智能緩存任務結果

```python
@task(retries=3, retry_delay_seconds=60, timeout_seconds=300)
def resilient_task():
    # 任務會自動重試最多 3 次
    pass
```

### 4. 先進的調度系統

- **Cron 調度**：支持標準 Cron 表達式
- **Interval 調度**：基於時間間隔的調度
- **RRule 調度**：支持複雜的重複規則
- **事件驅動**：支持外部事件觸發

```python
# 每天凌晨 2 點執行
deployment = flow.deploy(
    schedule=CronSchedule(cron="0 2 * * *")
)
```

### 5. 完整的狀態管理

Prefect 追蹤所有執行狀態：
- `Pending`：等待執行
- `Running`：正在執行
- `Completed`：成功完成
- `Failed`：執行失敗
- `Cancelled`：已取消
- `Crashed`：意外崩潰

每個狀態都可以觸發自定義的處理邏輯。

### 6. 智能緩存機制

```python
@task(cache_key_fn=task_input_hash, cache_expiration=timedelta(hours=1))
def expensive_computation(x):
    # 相同輸入在 1 小時內會使用緩存結果
    return complex_calculation(x)
```

### 7. 靈活的通知系統

- **Email 通知**：任務失敗時發送郵件
- **Slack 通知**：集成 Slack webhook
- **自定義通知**：支持任意通知渠道
- **狀態鉤子**：基於狀態變化的回調

### 8. 現代化部署方式

```python
# 定義部署配置
flow.deploy(
    name="my-deployment",
    work_pool_name="my-pool",
    schedule=CronSchedule(cron="0 * * * *"),
    parameters={"param": "value"}
)
```

### 9. 豪華的監控面板

Prefect UI 提供：
- **實時執行監控**：查看所有運行中的任務
- **歷史記錄查詢**：完整的執行歷史
- **日誌聚合**：集中式日誌查看
- **性能分析**：任務執行時間統計
- **資源監控**：CPU、內存使用情況

### 10. 雲端和自托管選項

- **Prefect Cloud**：完全托管的 SaaS 服務
- **自托管服務器**：完全控制你的數據
- **混合部署**：靈活的部署架構

## 安裝

### 基本安裝

```bash
pip install prefect
```

### 完整安裝

```bash
pip install -r requirements.txt
```

### 啟動 Prefect 服務器

```bash
# 啟動本地服務器和 UI
prefect server start

# 或使用 Prefect Cloud
prefect cloud login
```

### 環境配置

創建 `.env` 文件：

```bash
# OpenAI API（用於 AI 任務）
OPENAI_API_KEY=your_openai_api_key

# Prefect Cloud（可選）
PREFECT_API_KEY=your_prefect_cloud_key
PREFECT_API_URL=https://api.prefect.cloud/api/accounts/[ACCOUNT_ID]/workspaces/[WORKSPACE_ID]

# 數據庫連接（可選）
DATABASE_URL=postgresql://user:password@localhost:5432/mydb

# 郵件通知（可選）
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_password
```

## 使用案例

### 1. 數據管道（ETL）

```python
from prefect import flow, task
import pandas as pd

@task
def extract():
    return pd.read_csv("data.csv")

@task
def transform(df):
    return df[df['value'] > 0]

@task
def load(df):
    df.to_sql('processed_data', con=engine)

@flow
def etl_pipeline():
    data = extract()
    cleaned = transform(data)
    load(cleaned)
```

### 2. 機器學習工作流

```python
@flow
def ml_pipeline():
    # 數據準備
    data = load_data()
    X_train, X_test = split_data(data)

    # 訓練模型
    model = train_model(X_train)

    # 評估模型
    metrics = evaluate_model(model, X_test)

    # 部署模型
    if metrics['accuracy'] > 0.9:
        deploy_model(model)
```

### 3. 網頁爬蟲和數據收集

```python
@flow
def web_scraping_pipeline(urls: list):
    results = []
    for url in urls:
        data = scrape_website.submit(url)  # 並行執行
        results.append(data)

    combined = combine_results(results)
    save_to_database(combined)
```

### 4. AI Agent 工作流

```python
@flow
def ai_agent_workflow(user_query: str):
    # 理解用戶意圖
    intent = analyze_intent(user_query)

    # 根據意圖執行不同任務
    if intent == "research":
        result = research_task(user_query)
    elif intent == "analysis":
        result = analysis_task(user_query)

    # 生成回應
    response = generate_response(result)
    return response
```

### 5. 定時報告生成

```python
@flow
def daily_report():
    # 收集數據
    sales_data = fetch_sales_data()
    user_data = fetch_user_data()

    # 生成報告
    report = create_report(sales_data, user_data)

    # 發送報告
    send_email(report)
```

## 與 Airflow 對比

| 特性 | Prefect 2.0 | Apache Airflow |
|------|-------------|----------------|
| **設計理念** | 代碼即工作流，動態優先 | DAG 定義，靜態優先 |
| **學習曲線** | ⭐⭐（簡單） | ⭐⭐⭐⭐（陡峭） |
| **動態工作流** | ✅ 原生支持 | ⚠️ 受限支持 |
| **Python 原生** | ✅ 完全原生 | ⚠️ 需要 DAG 文件 |
| **本地開發** | ✅ 優秀 | ⚠️ 需要完整環境 |
| **可觀測性** | ✅ 內建 | ⚠️ 需要額外配置 |
| **重試機制** | ✅ 靈活的重試策略 | ✅ 支持重試 |
| **參數化** | ✅ 原生 Python 參數 | ⚠️ 需要使用 Variables |
| **部署方式** | ✅ 簡單的部署 API | ⚠️ 需要複雜配置 |
| **UI 界面** | ✅ 現代化、響應式 | ✅ 功能強大但較舊 |
| **雲端選項** | ✅ Prefect Cloud（免費層） | ❌ 需自行部署或付費 |
| **社區支持** | ⭐⭐⭐ 快速增長 | ⭐⭐⭐⭐⭐ 成熟生態 |
| **企業功能** | ✅ RBAC、審計日誌 | ✅ 完整企業功能 |

### Prefect 的優勢

1. **更簡單**：無需學習複雜的 DAG 語法，使用原生 Python
2. **更靈活**：支持真正的動態工作流和條件邏輯
3. **更快速**：本地開發和測試更容易
4. **更現代**：採用最新的軟體工程實踐

### Airflow 的優勢

1. **更成熟**：經過多年生產環境驗證
2. **更多集成**：數百個預建的 Operators
3. **更大社區**：更多的教程和案例
4. **企業級**：在大型組織中廣泛採用

### 何時選擇 Prefect

- 新項目或重構現有工作流
- 需要動態工作流和複雜邏輯
- 團隊更熟悉純 Python 開發
- 需要快速原型和迭代
- 使用 AI/ML 工作流

### 何時選擇 Airflow

- 已有 Airflow 基礎設施
- 需要使用特定的 Airflow Operators
- 企業內部已標準化 Airflow
- 需要處理極大規模的 DAG（10000+ 任務）

## 項目結構

```
65.Prefect/
├── README.md                 # 項目說明文件
├── requirements.txt          # 依賴項目
├── 01_快速開始.py           # 基本 Flow 和 Task
├── 02_任務定義.py           # Task 裝飾器詳解
├── 03_參數傳遞.py           # 參數和結果處理
├── 04_並行執行.py           # 並發任務執行
├── 05_調度器.py             # 任務調度配置
├── 06_狀態管理.py           # State 狀態處理
├── 07_緩存機制.py           # 結果緩存策略
├── 08_通知告警.py           # 通知和告警配置
├── 09_部署配置.py           # Deployment 部署
└── 10_監控面板.py           # UI 和監控功能
```

## 核心概念

### Flow（流程）

Flow 是工作流的容器，定義了任務的執行順序和邏輯：

```python
@flow(name="my-flow", description="示例工作流")
def my_flow():
    result = my_task()
    return result
```

### Task（任務）

Task 是工作流中的最小執行單元：

```python
@task(
    name="my-task",
    retries=3,
    retry_delay_seconds=60,
    timeout_seconds=300
)
def my_task():
    # 任務邏輯
    pass
```

### Deployment（部署）

Deployment 將 Flow 與調度、基礎設施關聯：

```python
flow.deploy(
    name="production-deployment",
    work_pool_name="kubernetes-pool",
    schedule=CronSchedule(cron="0 0 * * *")
)
```

### Work Pool（工作池）

Work Pool 定義了任務執行的基礎設施：
- **Process**：本地進程執行
- **Docker**：Docker 容器執行
- **Kubernetes**：K8s 集群執行
- **Cloud Run**：Google Cloud Run
- **ECS**：AWS ECS

## 高級功能

### 1. 子流程（Subflows）

```python
@flow
def subflow():
    return "subflow result"

@flow
def parent_flow():
    result = subflow()  # 調用子流程
    return result
```

### 2. 任務依賴

```python
@flow
def pipeline():
    a = task_a()
    b = task_b()
    c = task_c(wait_for=[a, b])  # c 等待 a 和 b 完成
```

### 3. 映射（Mapping）

```python
@flow
def process_batch(items):
    # 對每個項目並行執行任務
    results = process_item.map(items)
    return results
```

### 4. 條件邏輯

```python
@flow
def conditional_flow():
    result = check_condition()

    if result:
        do_something()
    else:
        do_something_else()
```

### 5. 錯誤處理

```python
@task
def safe_task():
    try:
        risky_operation()
    except Exception as e:
        logger.error(f"Error: {e}")
        raise  # Prefect 會自動重試
```

## 最佳實踐

### 1. 任務粒度

- **太大**：難以重試和調試
- **太小**：過多開銷和複雜性
- **剛好**：一個邏輯單元

### 2. 冪等性

確保任務可以安全地重複執行：

```python
@task
def idempotent_task(user_id):
    # 使用 upsert 而不是 insert
    db.upsert(user_id, data)
```

### 3. 狀態管理

使用 Prefect 的狀態系統而不是自己管理：

```python
@task
def check_status():
    if not ready():
        return Paused()  # 暫停執行
    return Completed()
```

### 4. 日誌記錄

使用 Prefect 的 logger：

```python
@task
def logged_task():
    logger = get_run_logger()
    logger.info("開始處理")
    # ...
    logger.info("處理完成")
```

### 5. 資源管理

```python
@task
def resource_task():
    with acquire_resource() as resource:
        # 使用資源
        pass
    # 資源自動釋放
```

## 性能優化

### 1. 並行執行

```python
from prefect import flow
from prefect.task_runners import ConcurrentTaskRunner

@flow(task_runner=ConcurrentTaskRunner())
def parallel_flow():
    # 任務會並行執行
    results = [process.submit(i) for i in range(10)]
```

### 2. 緩存策略

```python
from prefect.tasks import task_input_hash

@task(
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(hours=24)
)
def cached_task(x):
    return expensive_operation(x)
```

### 3. 批處理

```python
@task
def batch_process(items, batch_size=100):
    for i in range(0, len(items), batch_size):
        batch = items[i:i+batch_size]
        process_batch(batch)
```

## 常見問題

### Q: Prefect vs Celery？

- **Prefect**：完整的工作流編排，有 UI、調度、狀態管理
- **Celery**：任務隊列，更低層次，需要自己構建編排邏輯

### Q: 如何處理長時間運行的任務？

使用心跳和檢查點：

```python
@task(timeout_seconds=3600)
def long_running_task():
    for i in range(1000):
        process_item(i)
        if i % 100 == 0:
            # 發送心跳
            pass
```

### Q: 如何處理敏感數據？

使用 Prefect Blocks 存儲敏感信息：

```python
from prefect.blocks.system import Secret

api_key = Secret.load("my-api-key")
```

### Q: 如何在生產環境部署？

1. 使用 Docker 容器化
2. 配置 Work Pool
3. 設置監控和告警
4. 使用 Prefect Cloud 或自托管服務器

## 相關資源

- **官方網站**：https://www.prefect.io
- **文檔**：https://docs.prefect.io
- **GitHub**：https://github.com/PrefectHQ/prefect
- **社區論壇**：https://discourse.prefect.io
- **Slack 社區**：https://prefect.io/slack
- **教程**：https://docs.prefect.io/tutorials
- **博客**：https://www.prefect.io/blog

## 社區和支持

- **Discord**：活躍的開發者社區
- **GitHub Discussions**：技術討論和問答
- **企業支持**：付費的企業級支持
- **培訓課程**：官方認證培訓

## 貢獻

歡迎貢獻！請查看示例文件了解如何使用 Prefect 的各種功能。

## 版本說明

本教程基於 **Prefect 2.14.0+** 版本。Prefect 2.0 是對 1.0 的完全重寫，兩者 API 不兼容。

## 許可證

Prefect 使用 Apache 2.0 許可證。Prefect Cloud 是商業產品，提供免費和付費計劃。

## 總結

Prefect 是現代化的工作流編排框架，特別適合：
- 數據工程團隊
- ML/AI 工作流
- 自動化任務
- 需要可觀測性的複雜工作流

它的設計理念是讓工作流編排變得簡單、直觀，同時保持強大和靈活。如果你正在尋找 Airflow 的替代品，或者開始一個新的工作流項目，Prefect 是一個值得考慮的選擇。

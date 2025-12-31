"""
LangSmith 生產監控 - Production Monitoring

這個示例展示如何：
1. 設置生產環境監控
2. 追蹤關鍵性能指標
3. 設置告警和通知
4. 處理生產問題
5. 性能優化
6. 事故響應流程

生產監控確保系統穩定可靠運行。
"""

import os
import time
from typing import Dict, Any, List
from datetime import datetime, timedelta
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnableConfig
from langsmith import Client
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.layout import Layout

console = Console()


def setup_environment():
    """配置環境"""
    load_dotenv()
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    # 生產環境使用專門的項目
    os.environ["LANGCHAIN_PROJECT"] = "production-monitoring"
    console.print("[green]✓ 環境配置完成[/green]")


def production_setup_guide():
    """示例 1：生產環境設置指南"""
    console.print(Panel("[bold cyan]示例 1：生產環境設置[/bold cyan]"))

    guide = """
[bold green]生產環境設置步驟：[/bold green]

[cyan]1. 環境分離[/cyan]
   創建不同的項目：
   - development: 開發環境
   - staging: 預發布環境
   - production: 生產環境

   ```python
   import os

   # 根據環境變量設置項目
   env = os.getenv("ENVIRONMENT", "development")
   os.environ["LANGCHAIN_PROJECT"] = f"myapp-{env}"
   ```

[cyan]2. 配置管理[/cyan]
   ```python
   # config.py
   import os

   class Config:
       LANGCHAIN_TRACING = os.getenv("LANGCHAIN_TRACING_V2", "true")
       LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT")
       LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")

       # 生產環境特定配置
       if os.getenv("ENVIRONMENT") == "production":
           # 採樣率（追蹤 10% 的請求以降低成本）
           TRACING_SAMPLE_RATE = 0.1
       else:
           TRACING_SAMPLE_RATE = 1.0
   ```

[cyan]3. 錯誤處理[/cyan]
   ```python
   from langsmith import traceable

   @traceable(name="production-handler")
   def handle_request(user_input):
       try:
           # 處理邏輯
           result = process(user_input)
           return {"status": "success", "result": result}

       except ValueError as e:
           # 業務異常
           return {"status": "error", "error": str(e)}

       except Exception as e:
           # 系統異常
           logger.error(f"Unexpected error: {e}")
           # 追蹤會自動記錄異常
           return {"status": "error", "error": "Internal error"}
   ```

[cyan]4. 性能優化[/cyan]
   - 使用連接池
   - 啟用緩存
   - 異步處理
   - 批量操作

[cyan]5. 安全考慮[/cyan]
   - 脫敏敏感數據
   - API Key 安全管理
   - 訪問控制
   - 數據保留策略
    """

    console.print(guide)


def key_metrics_monitoring():
    """示例 2：關鍵指標監控"""
    console.print(Panel("[bold cyan]示例 2：關鍵指標監控[/bold cyan]"))

    metrics_guide = """
[bold green]核心監控指標：[/bold green]

[cyan]1. 性能指標[/cyan]
   📊 延遲（Latency）
   - P50（中位數）
   - P95（95 百分位）
   - P99（99 百分位）
   - 最大延遲

   目標示例：
   - P50 < 500ms
   - P95 < 2s
   - P99 < 5s

   📊 吞吐量（Throughput）
   - 每秒請求數（RPS）
   - 每分鐘請求數（RPM）

   目標示例：
   - 峰值 RPS: 100
   - 平均 RPS: 50

[cyan]2. 可靠性指標[/cyan]
   📊 成功率
   - 成功請求比例
   - 目標：> 99.9%

   📊 錯誤率
   - 4xx 錯誤（客戶端錯誤）
   - 5xx 錯誤（服務端錯誤）
   - 目標：< 0.1%

   📊 超時率
   - 超時請求比例
   - 目標：< 1%

[cyan]3. 質量指標[/cyan]
   📊 用戶滿意度
   - 點讚/點踩比例
   - 用戶反饋分數

   📊 輸出質量
   - 自動評估分數
   - 人工評審分數

[cyan]4. 成本指標[/cyan]
   📊 Token 使用
   - 每日 token 使用量
   - 平均每請求 token 數

   📊 API 成本
   - 每日成本
   - 每請求成本
   - 成本趨勢

[cyan]5. 業務指標[/cyan]
   📊 用戶活躍度
   - DAU（日活躍用戶）
   - MAU（月活躍用戶）

   📊 功能使用
   - 各功能使用頻率
   - 熱門查詢類型
    """

    console.print(metrics_guide)

    # 創建監控儀表板示例
    console.print("\n[bold yellow]實時監控儀表板示例：[/bold yellow]\n")

    # 模擬指標數據
    metrics = {
        "性能": [
            ("P50 延遲", "342ms", "green"),
            ("P95 延遲", "1.2s", "green"),
            ("P99 延遲", "3.8s", "yellow"),
            ("吞吐量", "87 RPS", "green"),
        ],
        "可靠性": [
            ("成功率", "99.94%", "green"),
            ("錯誤率", "0.06%", "green"),
            ("超時率", "0.2%", "green"),
        ],
        "成本": [
            ("今日成本", "$12.34", "green"),
            ("Token 使用", "8.2M", "yellow"),
            ("平均成本", "$0.0014", "green"),
        ]
    }

    for category, items in metrics.items():
        table = Table(title=category, show_header=True, header_style="bold magenta")
        table.add_column("指標", style="cyan", width=20)
        table.add_column("當前值", style="white", width=15)
        table.add_column("狀態", style="green", width=10)

        for metric, value, status in items:
            status_color = status
            status_icon = "✓" if status == "green" else "⚠"
            table.add_row(metric, value, f"[{status_color}]{status_icon}[/{status_color}]")

        console.print(table)
        console.print()


def alerting_setup():
    """示例 3：告警設置"""
    console.print(Panel("[bold cyan]示例 3：告警系統設置[/bold cyan]"))

    example_code = '''
"""
告警系統實現示例
"""

import os
import requests
from datetime import datetime, timedelta
from langsmith import Client


class AlertManager:
    """告警管理器"""

    def __init__(self, webhook_url=None):
        self.webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")
        self.client = Client()
        self.thresholds = {
            "error_rate": 0.05,  # 5%
            "p99_latency": 5000,  # 5 秒
            "daily_cost": 100.0,  # $100
        }

    def check_error_rate(self, project_name="production"):
        """檢查錯誤率"""
        # 獲取最近 1 小時的 runs
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=1)

        runs = list(self.client.list_runs(
            project_name=project_name,
            start_time=start_time,
            end_time=end_time
        ))

        if not runs:
            return

        # 計算錯誤率
        total = len(runs)
        errors = sum(1 for run in runs if run.error is not None)
        error_rate = errors / total if total > 0 else 0

        if error_rate > self.thresholds["error_rate"]:
            self.send_alert(
                title="⚠️ 高錯誤率告警",
                message=f"錯誤率：{error_rate*100:.2f}% (閾值：{self.thresholds['error_rate']*100}%)",
                severity="high",
                details={
                    "total_runs": total,
                    "errors": errors,
                    "project": project_name
                }
            )

    def check_latency(self, project_name="production"):
        """檢查延遲"""
        # 獲取最近的 runs
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=5)

        runs = list(self.client.list_runs(
            project_name=project_name,
            start_time=start_time,
            end_time=end_time
        ))

        if not runs:
            return

        # 計算 P99 延遲
        latencies = []
        for run in runs:
            if run.end_time and run.start_time:
                latency = (run.end_time - run.start_time).total_seconds() * 1000
                latencies.append(latency)

        if latencies:
            latencies.sort()
            p99_index = int(len(latencies) * 0.99)
            p99_latency = latencies[p99_index]

            if p99_latency > self.thresholds["p99_latency"]:
                self.send_alert(
                    title="⚠️ 高延遲告警",
                    message=f"P99 延遲：{p99_latency:.0f}ms (閾值：{self.thresholds['p99_latency']}ms)",
                    severity="medium",
                    details={
                        "p99": f"{p99_latency:.0f}ms",
                        "project": project_name
                    }
                )

    def send_alert(self, title, message, severity="medium", details=None):
        """發送告警"""
        alert = {
            "title": title,
            "message": message,
            "severity": severity,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }

        print(f"🚨 告警：{title}")
        print(f"   {message}")

        # 發送到 Slack
        if self.webhook_url:
            self._send_to_slack(alert)

        # 也可以發送到其他渠道
        # - Email
        # - PagerDuty
        # - 企業微信
        # etc.

    def _send_to_slack(self, alert):
        """發送到 Slack"""
        color = {
            "low": "#36a64f",
            "medium": "#ff9900",
            "high": "#ff0000"
        }.get(alert["severity"], "#cccccc")

        payload = {
            "attachments": [{
                "color": color,
                "title": alert["title"],
                "text": alert["message"],
                "fields": [
                    {"title": k, "value": str(v), "short": True}
                    for k, v in alert["details"].items()
                ],
                "footer": "LangSmith 監控",
                "ts": int(datetime.now().timestamp())
            }]
        }

        try:
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
        except Exception as e:
            print(f"發送告警失敗：{e}")


# 使用示例
alert_manager = AlertManager()

# 定期檢查（可以用 cron 或調度器）
while True:
    alert_manager.check_error_rate()
    alert_manager.check_latency()
    time.sleep(300)  # 每 5 分鐘檢查一次
    '''

    from rich.syntax import Syntax
    syntax = Syntax(example_code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)


def incident_response():
    """示例 4：事故響應流程"""
    console.print(Panel("[bold cyan]示例 4：事故響應流程[/bold cyan]"))

    workflow = """
[bold green]生產事故響應流程：[/bold green]

[cyan]階段 1：檢測（Detection）[/cyan]
⏰ 0-5 分鐘

1. 監控系統發現異常
   - 高錯誤率告警
   - 高延遲告警
   - 成本異常告警

2. 自動通知值班人員
   - Slack 通知
   - 郵件告警
   - 電話告警（嚴重事故）

[cyan]階段 2：分類（Triage）[/cyan]
⏰ 5-15 分鐘

1. 評估影響範圍
   - 受影響的用戶數
   - 受影響的功能
   - 業務影響程度

2. 確定優先級
   - P0：系統完全不可用
   - P1：核心功能受影響
   - P2：次要功能受影響
   - P3：性能降低

3. 召集相關人員
   - P0/P1：立即召集團隊
   - P2/P3：正常工作時間處理

[cyan]階段 3：調查（Investigation）[/cyan]
⏰ 15-60 分鐘

1. 在 LangSmith 中分析
   - 查看錯誤 runs
   - 檢查追蹤詳情
   - 分析錯誤模式
   - 查看變更歷史

2. 收集信息
   ```python
   from langsmith import Client
   from datetime import datetime, timedelta

   client = Client()

   # 查找錯誤 runs
   end_time = datetime.now()
   start_time = end_time - timedelta(hours=1)

   error_runs = client.list_runs(
       project_name="production",
       filter='error != null',
       start_time=start_time,
       end_time=end_time
   )

   # 分析錯誤類型
   error_types = {}
   for run in error_runs:
       error_msg = str(run.error)
       error_types[error_msg] = error_types.get(error_msg, 0) + 1

   print("錯誤分布：")
   for error, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
       print(f"  {error}: {count}")
   ```

3. 確定根本原因
   - 代碼變更
   - 配置變更
   - 依賴服務問題
   - 數據問題
   - 外部 API 問題

[cyan]階段 4：緩解（Mitigation）[/cyan]
⏰ 即時

1. 快速修復選項
   - 回滾到上一版本
   - 切換到備用服務
   - 限流保護
   - 降級非核心功能

2. 執行修復
   ```bash
   # 回滾部署
   git revert <commit-hash>
   # 或
   kubectl rollout undo deployment/app

   # 更新配置
   kubectl set env deployment/app LANGCHAIN_PROJECT=production-v1

   # 重啟服務
   kubectl rollout restart deployment/app
   ```

3. 驗證修復
   - 檢查錯誤率
   - 檢查延遲
   - 小流量測試
   - 逐步放量

[cyan]階段 5：恢復（Recovery）[/cyan]
⏰ 60-120 分鐘

1. 確認系統穩定
   - 監控指標正常
   - 持續觀察 30 分鐘

2. 通知相關方
   - 內部團隊
   - 受影響用戶（如需要）

3. 更新狀態頁面

[cyan]階段 6：回顧（Post-Mortem）[/cyan]
⏰ 24-48 小時內

1. 編寫事故報告
   - 時間線
   - 根本原因
   - 影響範圍
   - 處理過程
   - 經驗教訓

2. 改進措施
   - 技術改進
   - 流程改進
   - 監控改進
   - 文檔更新

3. 分享學習
   - 團隊會議
   - 文檔記錄

[bold yellow]事故響應檢查清單：[/bold yellow]

檢測階段：
□ 收到告警通知
□ 確認異常是否真實
□ 記錄開始時間

分類階段：
□ 評估影響範圍
□ 確定優先級
□ 通知相關人員

調查階段：
□ 查看 LangSmith 追蹤
□ 檢查近期變更
□ 收集錯誤日誌
□ 確定根本原因

緩解階段：
□ 執行快速修復
□ 驗證修復效果
□ 監控系統狀態

恢復階段：
□ 確認系統穩定
□ 通知相關方
□ 更新狀態

回顧階段：
□ 編寫事故報告
□ 制定改進計劃
□ 更新文檔
    """

    console.print(workflow)


def performance_optimization():
    """示例 5：性能優化實踐"""
    console.print(Panel("[bold cyan]示例 5：性能優化實踐[/bold cyan]"))

    optimizations = """
[bold green]生產環境性能優化：[/bold green]

[cyan]1. 響應時間優化[/cyan]

📊 使用流式輸出
```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4o-mini",
    streaming=True  # 啟用流式輸出
)

# 用戶可以立即看到開始的輸出
for chunk in llm.stream("你好"):
    print(chunk.content, end="", flush=True)
```

📊 並行處理
```python
import asyncio
from langchain_openai import ChatOpenAI

async def process_batch(items):
    llm = ChatOpenAI(model="gpt-4o-mini")

    # 並行處理多個請求
    tasks = [llm.ainvoke(item) for item in items]
    results = await asyncio.gather(*tasks)

    return results

# 使用
items = ["問題1", "問題2", "問題3"]
results = asyncio.run(process_batch(items))
```

📊 緩存策略
```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=1000)
def get_cached_response(prompt_hash):
    \"\"\"緩存常見查詢\"\"\"
    llm = ChatOpenAI(model="gpt-4o-mini")
    # 實際應該從緩存數據庫讀取
    return llm.invoke(prompt_hash)

# 使用
prompt = "什麼是 AI?"
prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
response = get_cached_response(prompt_hash)
```

[cyan]2. 資源使用優化[/cyan]

📊 連接池
```python
from langchain_openai import ChatOpenAI

# 重用 LLM 實例
class LLMPool:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            max_retries=2
        )

    def invoke(self, prompt):
        return self.llm.invoke(prompt)

# 全局實例
llm_pool = LLMPool()
```

📊 批量處理
```python
# 不好：逐個處理
for item in items:
    result = llm.invoke(item)

# 好：批量處理
results = llm.batch(items)
```

[cyan]3. 成本優化[/cyan]

📊 智能模型選擇
```python
def select_model(query_complexity):
    \"\"\"根據複雜度選擇模型\"\"\"
    if query_complexity == "simple":
        return ChatOpenAI(model="gpt-3.5-turbo")
    elif query_complexity == "medium":
        return ChatOpenAI(model="gpt-4o-mini")
    else:
        return ChatOpenAI(model="gpt-4")

# 使用
query = "2+2=?"
model = select_model("simple")
result = model.invoke(query)
```

📊 輸出長度限制
```python
llm = ChatOpenAI(
    model="gpt-4o-mini",
    max_tokens=200  # 限制輸出長度
)

prompt = ChatPromptTemplate.from_template(
    "用不超過 50 字回答：{question}"  # 在提示中也限制
)
```

[cyan]4. 可靠性優化[/cyan]

📊 重試機制
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def reliable_invoke(llm, prompt):
    return llm.invoke(prompt)
```

📊 超時設置
```python
llm = ChatOpenAI(
    model="gpt-4o-mini",
    request_timeout=30  # 30 秒超時
)
```

📊 降級策略
```python
def invoke_with_fallback(prompt):
    try:
        # 嘗試主要服務
        result = primary_llm.invoke(prompt)
        return result
    except Exception as e:
        # 降級到備用服務
        logger.warning(f"Primary failed: {e}, using fallback")
        return fallback_llm.invoke(prompt)
```

[cyan]5. 監控優化[/cyan]

📊 採樣追蹤
```python
import random

def should_trace():
    return random.random() < 0.1  # 10% 採樣率

if should_trace():
    config = RunnableConfig(
        metadata={"sampled": True}
    )
else:
    # 不追蹤
    old_value = os.environ.get("LANGCHAIN_TRACING_V2")
    os.environ["LANGCHAIN_TRACING_V2"] = "false"
    config = None

result = chain.invoke(input, config=config)

# 恢復
if not should_trace() and old_value:
    os.environ["LANGCHAIN_TRACING_V2"] = old_value
```
    """

    console.print(optimizations)


def production_checklist():
    """生產環境檢查清單"""
    console.print(Panel("[bold cyan]生產環境檢查清單[/bold cyan]"))

    checklist = """
[bold green]生產部署檢查清單：[/bold green]

[cyan]部署前（Pre-Deployment）[/cyan]

□ 代碼和配置
  □ 代碼審查完成
  □ 所有測試通過
  □ 性能測試完成
  □ 安全掃描通過
  □ 環境變量正確配置

□ LangSmith 設置
  □ 生產項目已創建
  □ 追蹤正確配置
  □ 採樣率已設置
  □ 成本限制已配置

□ 監控和告警
  □ 監控儀表板設置
  □ 告警規則配置
  □ 通知渠道測試
  □ 值班排程確定

□ 備份和回滾
  □ 備份計劃就緒
  □ 回滾步驟文檔化
  □ 回滾測試完成

[cyan]部署中（During Deployment）[/cyan]

□ 執行部署
  □ 使用漸進式發布
  □ 金絲雀部署（5% → 25% → 100%）
  □ 監控關鍵指標
  □ 檢查錯誤日誌

□ 驗證
  □ 冒煙測試通過
  □ 端到端測試通過
  □ 性能指標正常
  □ 成本在預期範圍

[cyan]部署後（Post-Deployment）[/cyan]

□ 監控
  □ 持續監控 24 小時
  □ 檢查用戶反饋
  □ 分析追蹤數據
  □ 審查成本

□ 文檔
  □ 更新變更日誌
  □ 更新運維文檔
  □ 記錄已知問題
  □ 分享部署經驗

[cyan]持續運維（Ongoing）[/cyan]

□ 每日
  □ 檢查監控儀表板
  □ 審查錯誤日誌
  □ 檢查成本
  □ 處理告警

□ 每週
  □ 分析性能趨勢
  □ 審查失敗案例
  □ 更新測試數據集
  □ 團隊同步會議

□ 每月
  □ 性能優化
  □ 成本優化
  □ 安全審計
  □ 容量規劃

[bold yellow]緊急聯繫方式：[/bold yellow]

技術負責人：[待填寫]
值班工程師：[待填寫]
運維團隊：[待填寫]
Slack 頻道：#production-alerts
    """

    console.print(checklist)


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold green]LangSmith 生產監控[/bold green]",
        border_style="green"
    ))

    # 設置環境
    setup_environment()

    console.print("\n" + "="*60 + "\n")

    # 展示內容
    production_setup_guide()
    console.print("\n" + "="*60 + "\n")

    key_metrics_monitoring()
    console.print("\n" + "="*60 + "\n")

    alerting_setup()
    console.print("\n" + "="*60 + "\n")

    incident_response()
    console.print("\n" + "="*60 + "\n")

    performance_optimization()
    console.print("\n" + "="*60 + "\n")

    production_checklist()

    # 總結
    console.print(Panel("""
[bold green]生產監控總結[/bold green]

核心要素：

1. [cyan]監控指標[/cyan]
   - 性能：延遲、吞吐量
   - 可靠性：成功率、錯誤率
   - 質量：用戶滿意度
   - 成本：Token 使用、API 成本

2. [cyan]告警系統[/cyan]
   - 設置合理閾值
   - 多渠道通知
   - 分級響應
   - 避免告警疲勞

3. [cyan]事故響應[/cyan]
   - 檢測 → 分類 → 調查 → 緩解 → 恢復 → 回顧
   - 清晰的流程
   - 快速響應
   - 持續改進

4. [cyan]性能優化[/cyan]
   - 流式輸出
   - 並行處理
   - 緩存策略
   - 資源復用

5. [cyan]成本控制[/cyan]
   - 模型選擇
   - 輸出限制
   - 採樣追蹤
   - 定期審查

最佳實踐：

✓ 環境分離（dev/staging/prod）
✓ 全面監控和告警
✓ 文檔化流程
✓ 定期演練
✓ 持續優化
✓ 團隊協作

關鍵指標目標：

- 可用性：> 99.9%
- P95 延遲：< 2s
- 錯誤率：< 0.1%
- 成本：在預算內

下一步：

1. 設置生產環境項目
2. 配置監控和告警
3. 建立事故響應流程
4. 進行壓力測試
5. 制定優化計劃
6. 定期審查和改進

重要提示：

- 生產監控是持續過程
- 平衡功能、性能和成本
- 建立良好的運維文化
- 從事故中學習改進
- 保持與團隊的溝通

LangSmith 優勢：

✓ 完整的追蹤記錄
✓ 詳細的性能數據
✓ 成本透明化
✓ 便於問題定位
✓ 支持團隊協作
✓ 與 LangChain 深度集成

祝你的 LLM 應用穩定運行！🚀
    """, title="總結", border_style="green"))


if __name__ == "__main__":
    main()

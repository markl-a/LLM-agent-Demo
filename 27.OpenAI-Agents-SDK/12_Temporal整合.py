"""
OpenAI Agents SDK - Temporal 整合範例

展示如何使用 Temporal 實現持久化工作流
包含：長時間運行任務、工作流編排、錯誤恢復、定時任務
"""

import os
from datetime import timedelta
from openai_agents import Agent, tool, configure

print("""
="*80)
OpenAI Agents SDK + Temporal 整合
="*80)

# ============================================================================
# 什麼是 Temporal？
# ============================================================================

Temporal 是一個開源的工作流編排平台：

核心特性：
✓ 持久化執行：工作流可以運行數天、數月甚至數年
✓ 自動重試：失敗自動恢復
✓ 狀態管理：自動保存和恢復狀態
✓ 可觀測性：完整的執行歷史和追蹤
✓ 可擴展性：水平擴展支持

# ============================================================================
# 為什麼需要 Temporal？
# ============================================================================

傳統 Agent 系統的問題：
✗ 服務器重啟導致任務丟失
✗ 長時間任務難以管理
✗ 錯誤恢復需要手動處理
✗ 難以追蹤複雜工作流

Temporal + Agents SDK 的優勢：
✓ Agent 任務永不丟失
✓ 支持長時間運行（天/月）
✓ 自動錯誤恢復
✓ 完整的執行歷史
✓ 定時任務支持
✓ 並行工作流編排

# ============================================================================
# 使用場景
# ============================================================================

1. **長時間研究任務**
   - 多階段數據收集（數小時到數天）
   - 定期生成報告
   - 持續監控和分析

2. **客戶服務工作流**
   - 複雜的審批流程
   - 多步驟問題解決
   - 定期客戶回訪

3. **數據處理管道**
   - 大規模數據處理
   - ETL 工作流
   - 批量任務處理

4. **定時任務**
   - 每日報告生成
   - 定期系統檢查
   - 自動化運維任務

# ============================================================================
# 安裝
# ============================================================================

# 安裝 Temporal SDK
pip install openai-agents[temporal]

# 或單獨安裝
pip install temporalio

# 啟動 Temporal 服務（開發環境）
# Docker 方式：
docker run -d -p 7233:7233 temporalio/auto-setup:latest

# 或使用 Temporal CLI:
temporal server start-dev

# ============================================================================
# 基本概念
# ============================================================================

Workflow（工作流）:
  - 定義業務邏輯
  - 長時間運行的流程
  - 可以調用 Activities

Activity（活動）:
  - 實際執行的任務單元
  - 可以是 Agent 調用
  - 支持重試和超時

Worker（工作器）:
  - 執行 Workflows 和 Activities
  - 可以水平擴展

# ============================================================================
# 架構圖
# ============================================================================

    ┌─────────────┐
    │   Client    │ ← 啟動工作流
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │  Temporal   │ ← 編排和持久化
    │   Server    │
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │   Worker    │ ← 執行任務
    │  (Agent)    │
    └─────────────┘

""")


# ============================================================================
# 1. 基礎 Workflow
# ============================================================================

def basic_workflow_example():
    """基礎工作流示例（偽代碼）"""
    print("\n" + "="*60)
    print("範例 1: 基礎 Workflow")
    print("="*60)

    print("""
from temporalio import workflow, activity
from openai_agents import Agent, run

# 定義 Activity（Agent 任務）
@activity.defn
async def agent_task(query: str) -> str:
    agent = Agent(
        name="助手",
        model="gpt-4",
        instructions="使用繁體中文。"
    )

    response = run(
        agent=agent,
        messages=[{"role": "user", "content": query}]
    )

    return response.messages[-1]['content']


# 定義 Workflow
@workflow.defn
class AgentWorkflow:
    @workflow.run
    async def run(self, query: str) -> str:
        # 調用 Activity
        result = await workflow.execute_activity(
            agent_task,
            query,
            start_to_close_timeout=timedelta(minutes=5)
        )

        return result


# 客戶端代碼
async def main():
    # 連接 Temporal
    client = await Client.connect("localhost:7233")

    # 啟動 Workflow
    result = await client.execute_workflow(
        AgentWorkflow.run,
        "解釋量子計算",
        id="agent-workflow-1",
        task_queue="agent-tasks"
    )

    print(f"結果: {result}")
    """)


# ============================================================================
# 2. 多步驟工作流
# ============================================================================

def multi_step_workflow_example():
    """多步驟工作流示例"""
    print("\n" + "="*60)
    print("範例 2: 多步驟工作流")
    print("="*60)

    print("""
@workflow.defn
class ResearchWorkflow:
    '''研究工作流：收集 → 分析 → 報告'''

    @workflow.run
    async def run(self, topic: str) -> dict:
        # 步驟 1: 收集數據（可能需要1小時）
        workflow.logger.info(f"開始收集: {topic}")
        data = await workflow.execute_activity(
            collect_data,
            topic,
            start_to_close_timeout=timedelta(hours=1)
        )

        # 步驟 2: 分析數據（可能需要30分鐘）
        workflow.logger.info("開始分析")
        analysis = await workflow.execute_activity(
            analyze_data,
            data,
            start_to_close_timeout=timedelta(minutes=30)
        )

        # 步驟 3: 生成報告（可能需要15分鐘）
        workflow.logger.info("生成報告")
        report = await workflow.execute_activity(
            generate_report,
            analysis,
            start_to_close_timeout=timedelta(minutes=15)
        )

        return {
            "topic": topic,
            "status": "completed",
            "report": report
        }


# Activities (使用 Agents)
@activity.defn
async def collect_data(topic: str) -> dict:
    collector = Agent(
        name="數據收集器",
        model="gpt-4",
        tools=[search_papers, search_web]
    )
    # ... 收集邏輯
    return {"data": [...]}


@activity.defn
async def analyze_data(data: dict) -> dict:
    analyst = Agent(
        name="數據分析師",
        model="gpt-4",
        tools=[analyze, visualize]
    )
    # ... 分析邏輯
    return {"insights": [...]}


@activity.defn
async def generate_report(analysis: dict) -> str:
    reporter = Agent(
        name="報告生成器",
        model="gpt-4"
    )
    # ... 生成報告
    return "完整報告內容..."
    """)

    print("\n特點：")
    print("  • 每個步驟獨立執行")
    print("  • 失敗自動重試")
    print("  • 可以運行數小時")
    print("  • 服務器重啟不影響")


# ============================================================================
# 3. 並行工作流
# ============================================================================

def parallel_workflow_example():
    """並行工作流示例"""
    print("\n" + "="*60)
    print("範例 3: 並行執行")
    print("="*60)

    print("""
@workflow.defn
class ParallelAnalysisWorkflow:
    '''並行分析多個數據源'''

    @workflow.run
    async def run(self, sources: list) -> dict:
        # 並行執行多個 Activities
        tasks = [
            workflow.execute_activity(
                analyze_source,
                source,
                start_to_close_timeout=timedelta(minutes=10)
            )
            for source in sources
        ]

        # 等待所有任務完成
        results = await asyncio.gather(*tasks)

        # 匯總結果
        summary = await workflow.execute_activity(
            summarize_results,
            results,
            start_to_close_timeout=timedelta(minutes=5)
        )

        return {
            "sources": sources,
            "results": results,
            "summary": summary
        }


# 使用示例
result = await client.execute_workflow(
    ParallelAnalysisWorkflow.run,
    ["source1", "source2", "source3"],
    id="parallel-analysis-1",
    task_queue="analysis-tasks"
)
    """)

    print("\n優勢：")
    print("  • 顯著縮短總執行時間")
    print("  • 充分利用資源")
    print("  • 某個任務失敗不影響其他")


# ============================================================================
# 4. 錯誤處理和重試
# ============================================================================

def error_handling_example():
    """錯誤處理示例"""
    print("\n" + "="*60)
    print("範例 4: 錯誤處理和重試")
    print("="*60)

    print("""
from temporalio.common import RetryPolicy

# 配置重試策略
retry_policy = RetryPolicy(
    initial_interval=timedelta(seconds=1),
    maximum_interval=timedelta(seconds=60),
    maximum_attempts=5,
    backoff_coefficient=2.0
)

@workflow.defn
class RobustWorkflow:
    @workflow.run
    async def run(self, task: str) -> str:
        try:
            # 執行 Activity with 重試
            result = await workflow.execute_activity(
                risky_agent_task,
                task,
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=retry_policy  # 自動重試
            )

            return result

        except Exception as e:
            workflow.logger.error(f"任務失敗: {e}")

            # 嘗試備用方案
            result = await workflow.execute_activity(
                fallback_task,
                task,
                start_to_close_timeout=timedelta(minutes=2)
            )

            return result


@activity.defn
async def risky_agent_task(task: str) -> str:
    # 可能失敗的任務
    agent = Agent(model="gpt-4", ...)

    try:
        response = run(agent, ...)
        return response
    except Exception as e:
        # Activity 失敗，Temporal 會自動重試
        raise


@activity.defn
async def fallback_task(task: str) -> str:
    # 備用方案（使用更簡單的模型）
    agent = Agent(model="gpt-3.5-turbo", ...)
    return run(agent, ...)
    """)

    print("\n重試策略說明：")
    print("  • initial_interval: 首次重試間隔")
    print("  • maximum_interval: 最大重試間隔")
    print("  • maximum_attempts: 最多重試次數")
    print("  • backoff_coefficient: 退避係數（指數退避）")


# ============================================================================
# 5. 定時工作流
# ============================================================================

def scheduled_workflow_example():
    """定時工作流示例"""
    print("\n" + "="*60)
    print("範例 5: 定時任務")
    print("="*60)

    print("""
# 定時生成每日報告
@workflow.defn
class DailyReportWorkflow:
    @workflow.run
    async def run(self, date: str) -> str:
        # 收集今日數據
        data = await workflow.execute_activity(
            collect_daily_data,
            date,
            start_to_close_timeout=timedelta(hours=1)
        )

        # 生成報告
        report = await workflow.execute_activity(
            generate_daily_report,
            data,
            start_to_close_timeout=timedelta(minutes=30)
        )

        # 發送報告
        await workflow.execute_activity(
            send_report,
            report,
            start_to_close_timeout=timedelta(minutes=5)
        )

        return f"報告已生成: {date}"


# 使用 Temporal Schedules
from temporalio.client import Schedule, ScheduleActionStartWorkflow

# 創建每日定時任務
schedule = Schedule(
    action=ScheduleActionStartWorkflow(
        DailyReportWorkflow.run,
        args=["2024-01-01"],
        id="daily-report",
        task_queue="report-tasks"
    ),
    spec=ScheduleSpec(
        cron_expressions=["0 9 * * *"]  # 每天早上9點
    )
)

# 註冊定時任務
await client.create_schedule(
    "daily-report-schedule",
    schedule
)
    """)

    print("\n定時表達式示例：")
    print("  • '0 9 * * *'   - 每天 9:00")
    print("  • '0 */6 * * *' - 每 6 小時")
    print("  • '0 0 * * 0'   - 每週日 0:00")
    print("  • '0 0 1 * *'   - 每月 1 日 0:00")


# ============================================================================
# 6. 狀態查詢
# ============================================================================

def query_workflow_example():
    """工作流狀態查詢"""
    print("\n" + "="*60)
    print("範例 6: 查詢工作流狀態")
    print("="*60)

    print("""
@workflow.defn
class LongRunningWorkflow:
    def __init__(self):
        self._progress = 0
        self._status = "initializing"

    @workflow.run
    async def run(self, task: str) -> str:
        self._status = "running"

        # 步驟 1
        self._progress = 25
        await workflow.execute_activity(step1, ...)

        # 步驟 2
        self._progress = 50
        await workflow.execute_activity(step2, ...)

        # 步驟 3
        self._progress = 75
        await workflow.execute_activity(step3, ...)

        # 完成
        self._progress = 100
        self._status = "completed"
        return "success"

    @workflow.query
    def get_progress(self) -> int:
        '''查詢當前進度'''
        return self._progress

    @workflow.query
    def get_status(self) -> str:
        '''查詢當前狀態'''
        return self._status


# 客戶端查詢
handle = client.get_workflow_handle("workflow-id")

# 查詢進度（不中斷工作流）
progress = await handle.query(
    LongRunningWorkflow.get_progress
)
print(f"當前進度: {progress}%")

# 查詢狀態
status = await handle.query(
    LongRunningWorkflow.get_status
)
print(f"當前狀態: {status}")
    """)


# ============================================================================
# 7. 實際應用場景
# ============================================================================

def real_world_examples():
    """實際應用場景"""
    print("\n" + "="*60)
    print("範例 7: 實際應用場景")
    print("="*60)

    print("""
場景 1: 客戶服務工單系統
────────────────────────

@workflow.defn
class CustomerTicketWorkflow:
    '''處理客戶工單，可能需要數天'''

    @workflow.run
    async def run(self, ticket_id: str) -> dict:
        # 1. 自動分類和優先級
        classification = await workflow.execute_activity(
            classify_ticket, ticket_id
        )

        # 2. 分配給 Agent
        if classification['priority'] == 'high':
            # 高優先級，立即處理
            response = await workflow.execute_activity(
                handle_ticket_urgent, ticket_id
            )
        else:
            # 普通優先級，可能需要等待
            await workflow.sleep(timedelta(hours=1))
            response = await workflow.execute_activity(
                handle_ticket_normal, ticket_id
            )

        # 3. 等待客戶回復（可能數天）
        approved = await workflow.wait_condition(
            lambda: self._customer_approved,
            timeout=timedelta(days=7)
        )

        # 4. 關閉工單
        return {"ticket_id": ticket_id, "status": "closed"}


場景 2: 內容審核工作流
────────────────────────

@workflow.defn
class ContentModerationWorkflow:
    '''多級內容審核'''

    @workflow.run
    async def run(self, content_id: str) -> dict:
        # 第一級：AI 自動審核
        ai_result = await workflow.execute_activity(
            ai_moderate, content_id
        )

        if ai_result['confidence'] > 0.9:
            # 高置信度，直接通過/拒絕
            return ai_result

        # 第二級：人工審核
        # 等待人工審核（可能需要數小時）
        human_result = await workflow.wait_condition(
            lambda: self._human_review_complete,
            timeout=timedelta(hours=24)
        )

        return human_result


場景 3: 數據管道
────────────────────────

@workflow.defn
class DataPipelineWorkflow:
    '''ETL 數據管道'''

    @workflow.run
    async def run(self, batch_id: str) -> dict:
        # 並行處理多個數據源
        extract_tasks = [
            workflow.execute_activity(
                extract_data, source
            )
            for source in ["db1", "db2", "api1"]
        ]

        raw_data = await asyncio.gather(*extract_tasks)

        # 轉換
        transformed = await workflow.execute_activity(
            transform_data, raw_data
        )

        # 加載
        await workflow.execute_activity(
            load_data, transformed
        )

        return {"batch_id": batch_id, "status": "completed"}
    """)


# ============================================================================
# 8. 最佳實踐
# ============================================================================

def best_practices():
    """最佳實踐"""
    print("\n" + "="*60)
    print("範例 8: 最佳實踐")
    print("="*60)

    print("""
1. Workflow 設計原則
──────────────────

✓ 確定性（Deterministic）
  - Workflow 代碼必須是確定性的
  - 不要使用隨機數、當前時間
  - 使用 workflow.now() 而不是 datetime.now()

✗ 錯誤示例:
  import random
  if random.random() > 0.5:  # 非確定性！
      ...

✓ 正確示例:
  # 在 Activity 中使用隨機數
  result = await workflow.execute_activity(random_task, ...)


2. Activity 設計原則
──────────────────

✓ 冪等性（Idempotent）
  - Activity 可能被多次執行
  - 設計時確保重複執行不會產生副作用

✓ 超時設置
  - 總是設置合理的超時
  - start_to_close_timeout: 總執行時間
  - schedule_to_close_timeout: 包括排隊時間

✓ 重試策略
  - 為可能失敗的 Activity 配置重試
  - 設置最大重試次數
  - 使用指數退避


3. 錯誤處理
──────────────────

✓ 優雅降級
  - 準備備用方案
  - 不要讓整個工作流失敗

✓ 日誌記錄
  - 使用 workflow.logger
  - 記錄關鍵決策點

✓ 監控告警
  - 監控工作流執行時間
  - 設置失敗告警


4. 性能優化
──────────────────

✓ 並行執行
  - 使用 asyncio.gather 並行執行無依賴任務
  - 減少總執行時間

✓ 批量處理
  - 合併小任務
  - 減少 Activity 調用次數

✓ 緩存
  - 緩存常用數據
  - 減少重複計算


5. 測試策略
──────────────────

✓ 單元測試
  - 測試 Activities 獨立功能
  - 模擬各種錯誤情況

✓ 集成測試
  - 測試完整工作流
  - 使用 Temporal 測試框架

✓ 時間加速測試
  - 測試長時間運行的工作流
  - 使用時間跳躍功能
    """)


# ============================================================================
# 主程序
# ============================================================================

def main():
    """運行所有範例"""
    print("\n" + "="*60)
    print("Temporal 整合指南")
    print("="*60)

    basic_workflow_example()
    multi_step_workflow_example()
    parallel_workflow_example()
    error_handling_example()
    scheduled_workflow_example()
    query_workflow_example()
    real_world_examples()
    best_practices()

    print("\n" + "="*60)
    print("Temporal 整合指南完成！")
    print("="*60)

    print("""
總結：

Temporal + Agents SDK = 強大的持久化 Agent 系統

核心優勢：
✓ 永不丟失的 Agent 任務
✓ 支持長時間運行（天/月/年）
✓ 自動錯誤恢復和重試
✓ 完整的執行歷史和審計
✓ 定時任務和工作流編排
✓ 水平擴展和高可用

適用場景：
• 長時間研究和分析任務
• 複雜的業務工作流
• 需要高可靠性的自動化任務
• 大規模數據處理管道
• 定時報告和監控系統

下一步：
1. 安裝 Temporal Server
2. 實現第一個 Workflow
3. 添加錯誤處理和重試
4. 實施監控和告警
5. 優化性能和成本

相關資源：
• Temporal 文檔: https://docs.temporal.io
• Agents SDK 文檔: https://openai.com/docs/agents
• 示例代碼庫: https://github.com/temporalio/samples-python
    """)


if __name__ == "__main__":
    main()

"""
Temporal 快速開始 - 基本 Workflow

這個示例展示了 Temporal 的核心概念：
1. 定義 Workflow（工作流）
2. 定義 Activity（活動）
3. 啟動 Worker（工作器）
4. 執行工作流

Temporal 核心概念：
- Workflow: 定義業務邏輯的流程，必須是確定性的
- Activity: 執行實際操作的函數，可以失敗和重試
- Worker: 執行 Workflow 和 Activity 的進程
- Task Queue: 任務隊列，用於路由工作流和活動
"""

import asyncio
from datetime import timedelta
from typing import List

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker


# ============================================================
# Activity 定義 - 執行實際的業務操作
# ============================================================

@activity.defn
async def greet(name: str) -> str:
    """
    簡單的問候活動

    Activity 特點：
    - 可以進行網絡調用、數據庫操作等副作用操作
    - 自動處理重試和超時
    - 執行結果會被記錄在工作流歷史中
    """
    print(f"Activity: 正在問候 {name}")
    return f"Hello, {name}!"


@activity.defn
async def process_data(data: str) -> str:
    """
    數據處理活動

    模擬一些處理邏輯
    """
    print(f"Activity: 正在處理數據 {data}")
    await asyncio.sleep(1)  # 模擬耗時操作
    return f"Processed: {data.upper()}"


@activity.defn
async def send_notification(message: str) -> bool:
    """
    發送通知活動

    模擬發送通知（郵件、短信等）
    """
    print(f"Activity: 發送通知 - {message}")
    await asyncio.sleep(0.5)
    return True


# ============================================================
# Workflow 定義 - 定義業務流程邏輯
# ============================================================

@workflow.defn
class HelloWorkflow:
    """
    簡單的問候工作流

    Workflow 特點：
    - 必須是確定性的（相同輸入產生相同輸出）
    - 狀態自動持久化
    - 進程崩潰後可以恢復
    - 不能直接進行 I/O 操作（應使用 Activity）
    """

    @workflow.run
    async def run(self, name: str) -> str:
        """
        工作流入口函數

        Args:
            name: 要問候的名字

        Returns:
            問候消息
        """
        # 執行問候活動
        # start_to_close_timeout: 活動從開始到完成的最大時間
        greeting = await workflow.execute_activity(
            greet,
            name,
            start_to_close_timeout=timedelta(seconds=10),
        )

        return greeting


@workflow.defn
class DataProcessingWorkflow:
    """
    數據處理工作流 - 展示多個活動的串行執行
    """

    @workflow.run
    async def run(self, items: List[str]) -> dict:
        """
        處理多個數據項

        Args:
            items: 要處理的數據列表

        Returns:
            處理結果統計
        """
        results = []

        # 串行處理每個數據項
        for item in items:
            result = await workflow.execute_activity(
                process_data,
                item,
                start_to_close_timeout=timedelta(seconds=30),
            )
            results.append(result)

        # 發送完成通知
        notification_message = f"處理完成：共處理 {len(results)} 項數據"
        await workflow.execute_activity(
            send_notification,
            notification_message,
            start_to_close_timeout=timedelta(seconds=10),
        )

        return {
            "total": len(items),
            "processed": len(results),
            "results": results
        }


@workflow.defn
class ComplexWorkflow:
    """
    複雜工作流 - 展示條件邏輯和工作流狀態
    """

    @workflow.run
    async def run(self, user_name: str, should_notify: bool = True) -> dict:
        """
        包含條件邏輯的工作流

        Args:
            user_name: 用戶名
            should_notify: 是否發送通知

        Returns:
            執行結果
        """
        # 步驟 1: 問候用戶
        greeting = await workflow.execute_activity(
            greet,
            user_name,
            start_to_close_timeout=timedelta(seconds=10),
        )

        # 步驟 2: 處理用戶數據
        processed = await workflow.execute_activity(
            process_data,
            user_name,
            start_to_close_timeout=timedelta(seconds=30),
        )

        # 步驟 3: 條件性發送通知
        notification_sent = False
        if should_notify:
            notification_sent = await workflow.execute_activity(
                send_notification,
                f"{greeting} 數據已處理：{processed}",
                start_to_close_timeout=timedelta(seconds=10),
            )

        return {
            "greeting": greeting,
            "processed": processed,
            "notification_sent": notification_sent,
            "workflow_id": workflow.info().workflow_id
        }


# ============================================================
# Worker 配置和啟動
# ============================================================

async def run_worker():
    """
    啟動 Worker 來執行工作流和活動

    Worker 負責：
    - 從任務隊列拉取任務
    - 執行工作流和活動
    - 報告執行結果
    """
    # 連接到 Temporal Server
    client = await Client.connect("localhost:7233")

    print("=" * 60)
    print("🚀 Worker 啟動中...")
    print("=" * 60)
    print("連接信息：")
    print(f"  - Server: localhost:7233")
    print(f"  - Task Queue: hello-task-queue")
    print(f"  - Workflows: HelloWorkflow, DataProcessingWorkflow, ComplexWorkflow")
    print(f"  - Activities: greet, process_data, send_notification")
    print("=" * 60)
    print("等待任務中... (按 Ctrl+C 停止)\n")

    # 創建 Worker
    worker = Worker(
        client,
        task_queue="hello-task-queue",
        workflows=[HelloWorkflow, DataProcessingWorkflow, ComplexWorkflow],
        activities=[greet, process_data, send_notification],
    )

    # 運行 Worker（阻塞直到停止）
    await worker.run()


# ============================================================
# 客戶端 - 啟動工作流
# ============================================================

async def run_workflow():
    """
    客戶端：啟動和執行工作流
    """
    # 連接到 Temporal Server
    client = await Client.connect("localhost:7233")

    print("\n" + "=" * 60)
    print("📋 執行工作流示例")
    print("=" * 60 + "\n")

    # ========================================
    # 示例 1: 簡單問候工作流
    # ========================================
    print("【示例 1】簡單問候工作流")
    print("-" * 60)

    try:
        result1 = await client.execute_workflow(
            HelloWorkflow.run,
            "Alice",
            id="hello-workflow-1",
            task_queue="hello-task-queue",
        )
        print(f"✓ 結果: {result1}\n")
    except Exception as e:
        print(f"✗ 錯誤: {e}\n")

    # ========================================
    # 示例 2: 數據處理工作流
    # ========================================
    print("【示例 2】數據處理工作流")
    print("-" * 60)

    try:
        result2 = await client.execute_workflow(
            DataProcessingWorkflow.run,
            ["item1", "item2", "item3"],
            id="data-processing-workflow-1",
            task_queue="hello-task-queue",
        )
        print(f"✓ 處理結果:")
        print(f"  - 總數: {result2['total']}")
        print(f"  - 已處理: {result2['processed']}")
        print(f"  - 結果: {result2['results']}\n")
    except Exception as e:
        print(f"✗ 錯誤: {e}\n")

    # ========================================
    # 示例 3: 複雜工作流
    # ========================================
    print("【示例 3】複雜工作流（帶通知）")
    print("-" * 60)

    try:
        result3 = await client.execute_workflow(
            ComplexWorkflow.run,
            "Bob",
            True,  # should_notify
            id="complex-workflow-1",
            task_queue="hello-task-queue",
        )
        print(f"✓ 執行結果:")
        print(f"  - 問候: {result3['greeting']}")
        print(f"  - 處理結果: {result3['processed']}")
        print(f"  - 通知已發送: {result3['notification_sent']}")
        print(f"  - Workflow ID: {result3['workflow_id']}\n")
    except Exception as e:
        print(f"✗ 錯誤: {e}\n")

    # ========================================
    # 示例 4: 複雜工作流（不通知）
    # ========================================
    print("【示例 4】複雜工作流（不通知）")
    print("-" * 60)

    try:
        result4 = await client.execute_workflow(
            ComplexWorkflow.run,
            "Charlie",
            False,  # should_notify
            id="complex-workflow-2",
            task_queue="hello-task-queue",
        )
        print(f"✓ 執行結果:")
        print(f"  - 問候: {result4['greeting']}")
        print(f"  - 處理結果: {result4['processed']}")
        print(f"  - 通知已發送: {result4['notification_sent']}\n")
    except Exception as e:
        print(f"✗ 錯誤: {e}\n")

    print("=" * 60)
    print("✓ 所有示例執行完成")
    print("=" * 60)
    print("\n提示：")
    print("  - 訪問 http://localhost:8080 查看 Web UI")
    print("  - 在 UI 中可以看到工作流執行歷史和詳細信息")
    print("=" * 60 + "\n")


# ============================================================
# 主函數
# ============================================================

async def main():
    """
    主函數 - 選擇運行模式
    """
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "client":
        # 客戶端模式：執行工作流
        await run_workflow()
    else:
        # Worker 模式：啟動工作器
        await run_worker()


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║         Temporal 快速開始 - 基本 Workflow                     ║
╚══════════════════════════════════════════════════════════════╝

使用說明：
---------
1. 確保 Temporal Server 正在運行：
   docker-compose up -d
   或
   temporal server start-dev

2. 在一個終端啟動 Worker：
   python 01_快速開始.py

3. 在另一個終端執行工作流：
   python 01_快速開始.py client

4. 訪問 Web UI 查看執行情況：
   http://localhost:8080

提示：
-----
- Worker 需要持續運行來處理工作流
- 每個工作流需要唯一的 Workflow ID
- 工作流狀態會自動持久化
- 支持 Ctrl+C 優雅停止 Worker
    """)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Worker 已停止")

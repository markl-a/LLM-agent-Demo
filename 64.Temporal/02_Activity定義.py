"""
Temporal Activity 定義 - 深入了解 Activity

這個示例展示了：
1. Activity 的不同定義方式
2. Activity 配置（重試、超時等）
3. Activity 上下文信息獲取
4. 同步和異步 Activity
5. Activity 取消處理
6. Activity 心跳機制

Activity 是執行實際業務操作的地方，可以：
- 進行網絡調用
- 訪問數據庫
- 執行文件操作
- 調用外部 API
"""

import asyncio
import random
import time
from datetime import timedelta
from typing import Optional

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.common import RetryPolicy
from temporalio.exceptions import ApplicationError
from temporalio.worker import Worker


# ============================================================
# 基本 Activity 定義
# ============================================================

@activity.defn
async def simple_activity(name: str) -> str:
    """
    最簡單的 Activity 定義

    使用 @activity.defn 裝飾器標記為 Activity
    """
    return f"Hello from activity, {name}!"


@activity.defn(name="custom-activity-name")
async def activity_with_custom_name(value: int) -> int:
    """
    自定義 Activity 名稱

    在註冊時使用自定義名稱，而不是函數名
    """
    return value * 2


# ============================================================
# Activity 上下文信息
# ============================================================

@activity.defn
async def activity_with_context() -> dict:
    """
    獲取 Activity 執行上下文信息

    上下文包含：
    - Activity ID
    - Workflow ID
    - 任務隊列名稱
    - 重試次數
    - 等等
    """
    info = activity.info()

    return {
        "activity_id": info.activity_id,
        "activity_type": info.activity_type,
        "workflow_id": info.workflow_id,
        "workflow_run_id": info.workflow_run_id,
        "workflow_type": info.workflow_type,
        "task_queue": info.task_queue,
        "attempt": info.attempt,
        "is_local": info.is_local,
    }


# ============================================================
# 可能失敗的 Activity（用於測試重試）
# ============================================================

@activity.defn
async def unreliable_activity(success_rate: float = 0.5) -> str:
    """
    不可靠的 Activity - 隨機失敗

    用於測試重試機制

    Args:
        success_rate: 成功率（0.0 到 1.0）

    Returns:
        成功消息

    Raises:
        ApplicationError: 當操作失敗時
    """
    info = activity.info()
    attempt = info.attempt

    print(f"Activity 嘗試 #{attempt}")

    if random.random() > success_rate:
        print(f"  ✗ 嘗試 #{attempt} 失敗")
        raise ApplicationError(
            f"Activity 失敗（嘗試 #{attempt}）",
            non_retryable=False  # 允許重試
        )

    print(f"  ✓ 嘗試 #{attempt} 成功")
    return f"Success after {attempt} attempt(s)"


@activity.defn
async def activity_with_timeout(duration_seconds: int) -> str:
    """
    可能超時的 Activity

    用於測試超時設置
    """
    info = activity.info()
    print(f"Activity 將執行 {duration_seconds} 秒...")

    await asyncio.sleep(duration_seconds)

    return f"Completed after {duration_seconds} seconds (attempt {info.attempt})"


# ============================================================
# 長時間運行的 Activity（帶心跳）
# ============================================================

@activity.defn
async def long_running_activity(total_steps: int = 10) -> str:
    """
    長時間運行的 Activity - 使用心跳機制

    心跳（Heartbeat）用於：
    - 讓 Temporal 知道 Activity 還在運行
    - 更新進度信息
    - 快速檢測 Worker 崩潰

    Args:
        total_steps: 總步驟數

    Returns:
        完成消息
    """
    print(f"開始長時間運行的任務（共 {total_steps} 步）")

    for step in range(1, total_steps + 1):
        # 模擬工作
        await asyncio.sleep(1)

        # 發送心跳，報告進度
        # 如果 Activity 被取消，heartbeat() 會拋出 CancelledError
        activity.heartbeat(f"Step {step}/{total_steps}")

        print(f"  完成步驟 {step}/{total_steps}")

    return f"Completed all {total_steps} steps"


# ============================================================
# 可取消的 Activity
# ============================================================

@activity.defn
async def cancellable_activity(duration: int = 30) -> str:
    """
    可取消的 Activity

    處理取消請求，清理資源
    """
    print(f"Activity 開始（預計運行 {duration} 秒）")

    try:
        for i in range(duration):
            # 檢查是否被取消
            if activity.is_cancelled():
                print("  檢測到取消請求，正在清理...")
                # 執行清理操作
                await cleanup_resources()
                return "Activity cancelled and cleaned up"

            await asyncio.sleep(1)
            activity.heartbeat(f"Running: {i + 1}/{duration}")

        return f"Completed {duration} seconds"

    except asyncio.CancelledError:
        print("  Activity 被取消")
        await cleanup_resources()
        raise


async def cleanup_resources():
    """清理資源的輔助函數"""
    print("  清理資源中...")
    await asyncio.sleep(0.5)
    print("  資源清理完成")


# ============================================================
# 同步 Activity
# ============================================================

@activity.defn
def sync_activity(value: str) -> str:
    """
    同步 Activity（不使用 async）

    適用於：
    - CPU 密集型操作
    - 調用同步庫
    - 不需要異步 I/O 的場景
    """
    # 同步操作
    time.sleep(1)
    return f"Sync result: {value.upper()}"


# ============================================================
# 帶複雜參數的 Activity
# ============================================================

from pydantic import BaseModel


class UserData(BaseModel):
    """用戶數據模型"""
    user_id: str
    name: str
    email: str
    age: Optional[int] = None


class ProcessResult(BaseModel):
    """處理結果模型"""
    success: bool
    user_id: str
    message: str
    processing_time: float


@activity.defn
async def process_user_data(user: UserData) -> ProcessResult:
    """
    處理複雜數據類型的 Activity

    使用 Pydantic 模型進行類型驗證
    """
    start_time = time.time()

    print(f"處理用戶數據: {user.name} ({user.email})")

    # 模擬處理
    await asyncio.sleep(1)

    processing_time = time.time() - start_time

    return ProcessResult(
        success=True,
        user_id=user.user_id,
        message=f"用戶 {user.name} 處理完成",
        processing_time=processing_time
    )


# ============================================================
# API 調用 Activity
# ============================================================

@activity.defn
async def call_external_api(url: str) -> dict:
    """
    調用外部 API 的 Activity

    這是 Activity 的典型用途：
    - 進行網絡調用
    - 處理外部服務
    - 自動重試失敗的請求
    """
    info = activity.info()

    print(f"調用 API: {url} (嘗試 #{info.attempt})")

    # 模擬 API 調用
    await asyncio.sleep(0.5)

    # 模擬偶爾失敗
    if random.random() < 0.3 and info.attempt < 3:
        raise ApplicationError(
            f"API 調用失敗（嘗試 #{info.attempt}）",
            non_retryable=False
        )

    return {
        "status": "success",
        "url": url,
        "data": {"result": "API response data"},
        "attempt": info.attempt
    }


# ============================================================
# 數據庫操作 Activity
# ============================================================

@activity.defn
async def database_operation(operation: str, data: dict) -> dict:
    """
    數據庫操作 Activity

    在實際應用中，這裡會進行真實的數據庫操作
    """
    info = activity.info()

    print(f"數據庫操作: {operation}")
    print(f"  數據: {data}")
    print(f"  嘗試: #{info.attempt}")

    # 模擬數據庫操作
    await asyncio.sleep(0.3)

    # 模擬偶爾的數據庫連接失敗
    if random.random() < 0.2 and info.attempt < 2:
        raise ApplicationError(
            "數據庫連接失敗",
            non_retryable=False
        )

    return {
        "operation": operation,
        "success": True,
        "affected_rows": 1,
        "timestamp": time.time()
    }


# ============================================================
# Workflow 定義 - 使用各種 Activity
# ============================================================

@workflow.defn
class ActivityDemoWorkflow:
    """演示各種 Activity 的工作流"""

    @workflow.run
    async def run(self) -> dict:
        """執行各種 Activity 示例"""

        results = {}

        # 1. 簡單 Activity
        results["simple"] = await workflow.execute_activity(
            simple_activity,
            "World",
            start_to_close_timeout=timedelta(seconds=10),
        )

        # 2. 帶自定義名稱的 Activity
        results["custom_name"] = await workflow.execute_activity(
            "custom-activity-name",
            42,
            start_to_close_timeout=timedelta(seconds=10),
        )

        # 3. 獲取上下文信息
        results["context"] = await workflow.execute_activity(
            activity_with_context,
            start_to_close_timeout=timedelta(seconds=10),
        )

        # 4. 同步 Activity
        results["sync"] = await workflow.execute_activity(
            sync_activity,
            "test data",
            start_to_close_timeout=timedelta(seconds=10),
        )

        # 5. 處理複雜數據
        user = UserData(
            user_id="user123",
            name="Alice",
            email="alice@example.com",
            age=28
        )
        results["user_processing"] = await workflow.execute_activity(
            process_user_data,
            user,
            start_to_close_timeout=timedelta(seconds=10),
        )

        return results


@workflow.defn
class RetryDemoWorkflow:
    """演示重試機制的工作流"""

    @workflow.run
    async def run(self, success_rate: float = 0.3) -> dict:
        """
        測試不可靠的 Activity

        配置自定義重試策略
        """

        # 配置重試策略
        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=1),  # 初始重試間隔
            maximum_interval=timedelta(seconds=10),  # 最大重試間隔
            backoff_coefficient=2.0,  # 退避係數（指數退避）
            maximum_attempts=5,  # 最大嘗試次數
        )

        result = await workflow.execute_activity(
            unreliable_activity,
            success_rate,
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=retry_policy,
        )

        return {"result": result}


@workflow.defn
class LongRunningWorkflow:
    """演示長時間運行 Activity 的工作流"""

    @workflow.run
    async def run(self, steps: int = 10) -> str:
        """
        執行長時間運行的 Activity

        配置心跳超時
        """

        result = await workflow.execute_activity(
            long_running_activity,
            steps,
            start_to_close_timeout=timedelta(seconds=120),
            heartbeat_timeout=timedelta(seconds=5),  # 心跳超時
        )

        return result


@workflow.defn
class ApiCallWorkflow:
    """演示 API 調用的工作流"""

    @workflow.run
    async def run(self, urls: list) -> list:
        """並行調用多個 API"""

        # 創建所有 API 調用任務
        tasks = []
        for url in urls:
            task = workflow.execute_activity(
                call_external_api,
                url,
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=RetryPolicy(
                    maximum_attempts=3,
                    initial_interval=timedelta(seconds=1),
                ),
            )
            tasks.append(task)

        # 並行執行所有任務
        results = await asyncio.gather(*tasks)

        return results


# ============================================================
# Worker 和 Client
# ============================================================

async def run_worker():
    """啟動 Worker"""
    client = await Client.connect("localhost:7233")

    print("=" * 60)
    print("🚀 Activity Demo Worker 啟動中...")
    print("=" * 60)

    # 收集所有 Activity
    activities = [
        simple_activity,
        activity_with_custom_name,
        activity_with_context,
        unreliable_activity,
        activity_with_timeout,
        long_running_activity,
        cancellable_activity,
        sync_activity,
        process_user_data,
        call_external_api,
        database_operation,
    ]

    worker = Worker(
        client,
        task_queue="activity-demo-queue",
        workflows=[
            ActivityDemoWorkflow,
            RetryDemoWorkflow,
            LongRunningWorkflow,
            ApiCallWorkflow,
        ],
        activities=activities,
    )

    print(f"已註冊 {len(activities)} 個 Activities")
    print("等待任務中...\n")

    await worker.run()


async def run_client():
    """執行示例工作流"""
    client = await Client.connect("localhost:7233")

    print("\n" + "=" * 60)
    print("📋 Activity 示例演示")
    print("=" * 60 + "\n")

    # 示例 1: 基本 Activity
    print("【示例 1】基本 Activity 演示")
    print("-" * 60)
    try:
        result = await client.execute_workflow(
            ActivityDemoWorkflow.run,
            id="activity-demo-1",
            task_queue="activity-demo-queue",
        )
        print("✓ 執行成功:")
        for key, value in result.items():
            print(f"  {key}: {value}")
        print()
    except Exception as e:
        print(f"✗ 錯誤: {e}\n")

    # 示例 2: 重試機制
    print("【示例 2】重試機制演示（低成功率）")
    print("-" * 60)
    try:
        result = await client.execute_workflow(
            RetryDemoWorkflow.run,
            0.3,  # 30% 成功率
            id="retry-demo-1",
            task_queue="activity-demo-queue",
        )
        print(f"✓ {result}\n")
    except Exception as e:
        print(f"✗ 錯誤: {e}\n")

    # 示例 3: 長時間運行
    print("【示例 3】長時間運行 Activity（帶心跳）")
    print("-" * 60)
    try:
        result = await client.execute_workflow(
            LongRunningWorkflow.run,
            5,  # 5 步
            id="long-running-1",
            task_queue="activity-demo-queue",
        )
        print(f"✓ {result}\n")
    except Exception as e:
        print(f"✗ 錯誤: {e}\n")

    # 示例 4: 並行 API 調用
    print("【示例 4】並行 API 調用")
    print("-" * 60)
    try:
        urls = [
            "https://api.example.com/users",
            "https://api.example.com/posts",
            "https://api.example.com/comments",
        ]
        results = await client.execute_workflow(
            ApiCallWorkflow.run,
            urls,
            id="api-call-1",
            task_queue="activity-demo-queue",
        )
        print("✓ API 調用結果:")
        for i, result in enumerate(results):
            print(f"  API {i + 1}: {result['status']} (嘗試 {result['attempt']} 次)")
        print()
    except Exception as e:
        print(f"✗ 錯誤: {e}\n")

    print("=" * 60)


async def main():
    """主函數"""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "client":
        await run_client()
    else:
        await run_worker()


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║              Temporal Activity 定義與使用                      ║
╚══════════════════════════════════════════════════════════════╝

Activity 特點：
-------------
✓ 可以進行 I/O 操作（網絡、數據庫、文件）
✓ 自動重試機制
✓ 支持超時控制
✓ 心跳機制（長時間運行）
✓ 可取消
✓ 冪等性建議

使用方法：
---------
1. 啟動 Worker: python 02_Activity定義.py
2. 執行示例: python 02_Activity定義.py client
    """)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 程序已停止")

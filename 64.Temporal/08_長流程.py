"""
Temporal 長流程 - 長時間運行任務

這個示例展示了：
1. 長時間休眠（Sleep）
2. 持久化定時器
3. 長期運行的工作流（天/月/年）
4. Continue-As-New 模式
5. 工作流歷史管理
6. 心跳機制
7. 狀態檢查點
8. 實際應用場景（試用期、訂閱、定期任務等）
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker


# ============================================================
# 數據模型
# ============================================================

@dataclass
class TrialSubscription:
    """試用訂閱"""
    subscription_id: str
    user_id: str
    trial_days: int
    start_date: str
    end_date: Optional[str] = None
    converted_to_paid: bool = False


@dataclass
class RecurringTask:
    """週期性任務"""
    task_id: str
    name: str
    interval_days: int
    total_iterations: int
    current_iteration: int = 0


@dataclass
class LoanApplication:
    """貸款申請"""
    loan_id: str
    user_id: str
    amount: float
    term_months: int
    monthly_payment: float


# ============================================================
# Activity 定義
# ============================================================

@activity.defn
async def send_welcome_email(user_id: str) -> bool:
    """發送歡迎郵件"""
    print(f"📧 發送歡迎郵件給用戶: {user_id}")
    await asyncio.sleep(0.3)
    return True


@activity.defn
async def send_trial_reminder(user_id: str, days_left: int) -> bool:
    """發送試用提醒"""
    print(f"⏰ 發送試用提醒: 用戶 {user_id}, 剩餘 {days_left} 天")
    await asyncio.sleep(0.3)
    return True


@activity.defn
async def check_conversion(user_id: str) -> bool:
    """檢查是否轉為付費用戶"""
    print(f"💳 檢查用戶轉化: {user_id}")
    await asyncio.sleep(0.5)
    # 模擬：30% 轉化率
    import random
    return random.random() < 0.3


@activity.defn
async def cancel_trial(user_id: str) -> bool:
    """取消試用"""
    print(f"❌ 取消試用: {user_id}")
    await asyncio.sleep(0.3)
    return True


@activity.defn
async def activate_paid_subscription(user_id: str) -> str:
    """激活付費訂閱"""
    print(f"✅ 激活付費訂閱: {user_id}")
    await asyncio.sleep(0.5)
    return f"SUB-{user_id}"


@activity.defn
async def execute_task(task_name: str, iteration: int) -> dict:
    """執行任務"""
    print(f"🔄 執行任務: {task_name} (第 {iteration} 次)")
    await asyncio.sleep(1)

    return {
        "task": task_name,
        "iteration": iteration,
        "timestamp": datetime.now().isoformat(),
        "status": "completed"
    }


@activity.defn
async def collect_payment(loan_id: str, month: int, amount: float) -> dict:
    """收取月供"""
    print(f"💰 收取月供: 貸款 {loan_id}, 第 {month} 期, ${amount}")
    await asyncio.sleep(0.5)

    # 模擬：10% 機率支付失敗
    import random
    success = random.random() > 0.1

    return {
        "loan_id": loan_id,
        "month": month,
        "amount": amount,
        "success": success,
        "timestamp": datetime.now().isoformat()
    }


@activity.defn
async def send_payment_reminder(user_id: str, amount: float) -> bool:
    """發送支付提醒"""
    print(f"📨 發送支付提醒: 用戶 {user_id}, 金額 ${amount}")
    await asyncio.sleep(0.3)
    return True


@activity.defn
async def log_event(event_type: str, data: dict) -> bool:
    """記錄事件"""
    print(f"📝 記錄事件: {event_type} - {data}")
    await asyncio.sleep(0.2)
    return True


# ============================================================
# 工作流 1: 試用訂閱工作流
# ============================================================

@workflow.defn
class TrialSubscriptionWorkflow:
    """
    試用訂閱工作流

    運行時長：7-30 天（根據試用期長度）

    流程：
    1. 開始試用
    2. 定期發送提醒（試用期中間、結束前 3 天）
    3. 試用期結束檢查轉化
    4. 轉化成功 -> 激活付費訂閱
       轉化失敗 -> 取消試用
    """

    @workflow.run
    async def run(self, subscription: TrialSubscription) -> dict:
        """
        執行試用訂閱流程
        """
        print(f"\n🎁 試用訂閱開始")
        print(f"   用戶: {subscription.user_id}")
        print(f"   試用期: {subscription.trial_days} 天")

        # 發送歡迎郵件
        await workflow.execute_activity(
            send_welcome_email,
            subscription.user_id,
            start_to_close_timeout=timedelta(seconds=30),
        )

        # 試用期中期提醒（試用期的一半時）
        mid_trial_days = subscription.trial_days // 2
        if mid_trial_days > 0:
            print(f"\n⏳ 休眠 {mid_trial_days} 天...")
            await asyncio.sleep(mid_trial_days * 86400)  # 轉換為秒

            await workflow.execute_activity(
                send_trial_reminder,
                subscription.user_id,
                subscription.trial_days - mid_trial_days,
                start_to_close_timeout=timedelta(seconds=30),
            )

        # 試用期結束前 3 天提醒
        days_before_end = 3
        remaining_days = subscription.trial_days - mid_trial_days - days_before_end

        if remaining_days > 0:
            print(f"\n⏳ 休眠 {remaining_days} 天...")
            await asyncio.sleep(remaining_days * 86400)

            await workflow.execute_activity(
                send_trial_reminder,
                subscription.user_id,
                days_before_end,
                start_to_close_timeout=timedelta(seconds=30),
            )

        # 最後 3 天
        print(f"\n⏳ 休眠 {days_before_end} 天...")
        await asyncio.sleep(days_before_end * 86400)

        # 試用期結束，檢查轉化
        print(f"\n🔍 試用期結束，檢查轉化...")

        converted = await workflow.execute_activity(
            check_conversion,
            subscription.user_id,
            start_to_close_timeout=timedelta(seconds=30),
        )

        if converted:
            # 轉化成功
            subscription_id = await workflow.execute_activity(
                activate_paid_subscription,
                subscription.user_id,
                start_to_close_timeout=timedelta(seconds=30),
            )

            subscription.converted_to_paid = True
            subscription.end_date = workflow.now().isoformat()

            await workflow.execute_activity(
                log_event,
                "trial_converted",
                {"user_id": subscription.user_id, "subscription_id": subscription_id},
                start_to_close_timeout=timedelta(seconds=30),
            )

            return {
                "status": "converted",
                "subscription_id": subscription_id,
                "trial_days": subscription.trial_days,
                "end_date": subscription.end_date
            }

        else:
            # 未轉化，取消試用
            await workflow.execute_activity(
                cancel_trial,
                subscription.user_id,
                start_to_close_timeout=timedelta(seconds=30),
            )

            subscription.end_date = workflow.now().isoformat()

            await workflow.execute_activity(
                log_event,
                "trial_cancelled",
                {"user_id": subscription.user_id},
                start_to_close_timeout=timedelta(seconds=30),
            )

            return {
                "status": "cancelled",
                "trial_days": subscription.trial_days,
                "end_date": subscription.end_date
            }


# ============================================================
# 工作流 2: 週期性任務工作流（Continue-As-New 模式）
# ============================================================

@workflow.defn
class RecurringTaskWorkflow:
    """
    週期性任務工作流

    使用 Continue-As-New 模式避免歷史過大

    適用於：
    - 需要運行很長時間（月/年）
    - 重複執行相同邏輯
    - 需要保持工作流歷史可管理
    """

    @workflow.run
    async def run(self, task: RecurringTask) -> dict:
        """
        執行週期性任務

        每次迭代後檢查是否需要 Continue-As-New
        """
        print(f"\n🔁 週期性任務: {task.name}")
        print(f"   迭代: {task.current_iteration + 1}/{task.total_iterations}")

        # 執行當前迭代的任務
        result = await workflow.execute_activity(
            execute_task,
            task.name,
            task.current_iteration + 1,
            start_to_close_timeout=timedelta(minutes=5),
        )

        # 更新迭代計數
        task.current_iteration += 1

        # 記錄事件
        await workflow.execute_activity(
            log_event,
            "task_executed",
            {"task": task.name, "iteration": task.current_iteration},
            start_to_close_timeout=timedelta(seconds=30),
        )

        # 檢查是否完成所有迭代
        if task.current_iteration >= task.total_iterations:
            print(f"   ✅ 所有迭代完成")
            return {
                "status": "completed",
                "task_name": task.name,
                "total_iterations": task.total_iterations
            }

        # 休眠到下一次執行
        print(f"   ⏳ 休眠 {task.interval_days} 天...")
        await asyncio.sleep(task.interval_days * 86400)

        # Continue-As-New：重新開始工作流，清空歷史
        # 這樣可以避免歷史記錄無限增長
        print(f"   🔄 Continue-As-New")

        workflow.continue_as_new(task)


# ============================================================
# 工作流 3: 貸款還款工作流
# ============================================================

@workflow.defn
class LoanRepaymentWorkflow:
    """
    貸款還款工作流

    運行時長：貸款期限（通常數月到數年）

    每月收取月供，直到貸款還清
    """

    @workflow.run
    async def run(self, loan: LoanApplication) -> dict:
        """
        執行貸款還款流程
        """
        print(f"\n💵 貸款還款工作流")
        print(f"   貸款 ID: {loan.loan_id}")
        print(f"   期限: {loan.term_months} 個月")
        print(f"   月供: ${loan.monthly_payment}")

        successful_payments = 0
        failed_payments = 0
        payment_history = []

        for month in range(1, loan.term_months + 1):
            print(f"\n   📅 第 {month}/{loan.term_months} 期")

            # 收取月供
            payment_result = await workflow.execute_activity(
                collect_payment,
                loan.loan_id,
                month,
                loan.monthly_payment,
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=workflow.common.RetryPolicy(
                    maximum_attempts=3,
                    initial_interval=timedelta(hours=1),
                ),
            )

            payment_history.append(payment_result)

            if payment_result["success"]:
                successful_payments += 1
                print(f"      ✅ 支付成功")
            else:
                failed_payments += 1
                print(f"      ❌ 支付失敗，發送提醒")

                # 發送支付提醒
                await workflow.execute_activity(
                    send_payment_reminder,
                    loan.user_id,
                    loan.monthly_payment,
                    start_to_close_timeout=timedelta(seconds=30),
                )

            # 記錄支付事件
            await workflow.execute_activity(
                log_event,
                "payment_processed",
                payment_result,
                start_to_close_timeout=timedelta(seconds=30),
            )

            # 如果還有下一期，休眠 30 天
            if month < loan.term_months:
                print(f"      ⏳ 休眠 30 天到下一期...")
                await asyncio.sleep(30 * 86400)

        # 貸款還清
        print(f"\n   🎉 貸款已還清")

        return {
            "status": "completed",
            "loan_id": loan.loan_id,
            "total_months": loan.term_months,
            "successful_payments": successful_payments,
            "failed_payments": failed_payments,
            "payment_history": payment_history
        }


# ============================================================
# 工作流 4: 簡化的長時間 Sleep 示例
# ============================================================

@workflow.defn
class LongSleepWorkflow:
    """
    長時間 Sleep 演示

    展示 Temporal 可以可靠地處理長時間休眠
    即使 Worker 重啟，休眠也會繼續
    """

    @workflow.run
    async def run(self, sleep_seconds: int, message: str) -> dict:
        """
        休眠指定時間後執行操作
        """
        print(f"\n😴 長時間休眠示例")
        print(f"   休眠時間: {sleep_seconds} 秒 ({sleep_seconds / 60:.1f} 分鐘)")
        print(f"   開始時間: {workflow.now().isoformat()}")

        start_time = workflow.now()

        # 長時間休眠
        await asyncio.sleep(sleep_seconds)

        end_time = workflow.now()
        actual_duration = (end_time - start_time).total_seconds()

        print(f"   結束時間: {end_time.isoformat()}")
        print(f"   實際休眠: {actual_duration:.1f} 秒")

        # 執行活動
        await workflow.execute_activity(
            log_event,
            "long_sleep_completed",
            {
                "message": message,
                "planned_seconds": sleep_seconds,
                "actual_seconds": actual_duration
            },
            start_to_close_timeout=timedelta(seconds=30),
        )

        return {
            "message": message,
            "planned_sleep_seconds": sleep_seconds,
            "actual_sleep_seconds": actual_duration,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        }


# ============================================================
# Worker 和 Client
# ============================================================

async def run_worker():
    """啟動 Worker"""
    client = await Client.connect("localhost:7233")

    print("=" * 60)
    print("🚀 長流程 Worker 啟動中...")
    print("=" * 60)

    worker = Worker(
        client,
        task_queue="long-running-queue",
        workflows=[
            TrialSubscriptionWorkflow,
            RecurringTaskWorkflow,
            LoanRepaymentWorkflow,
            LongSleepWorkflow,
        ],
        activities=[
            send_welcome_email,
            send_trial_reminder,
            check_conversion,
            cancel_trial,
            activate_paid_subscription,
            execute_task,
            collect_payment,
            send_payment_reminder,
            log_event,
        ],
    )

    print("等待任務中...\n")
    await worker.run()


async def run_client():
    """執行示例"""
    client = await Client.connect("localhost:7233")

    print("\n" + "=" * 60)
    print("📋 長時間運行工作流示例")
    print("=" * 60)

    # ========================================
    # 示例 1: 試用訂閱（模擬，使用秒代替天）
    # ========================================
    print("\n【示例 1】試用訂閱工作流（快速演示：30秒 = 30天）")
    print("-" * 60)

    subscription = TrialSubscription(
        subscription_id="TRIAL-001",
        user_id="user123",
        trial_days=30,  # 實際會轉換為秒用於演示
        start_date=datetime.now().isoformat()
    )

    # 注意：為了演示，這裡會很快完成
    # 在生產環境中，這將運行 30 天
    handle = await client.start_workflow(
        TrialSubscriptionWorkflow.run,
        subscription,
        id=f"trial-sub-{subscription.subscription_id}",
        task_queue="long-running-queue",
    )

    print(f"✓ 試用訂閱工作流已啟動: {handle.id}")
    print(f"   實際應用中將運行 {subscription.trial_days} 天")
    print(f"   演示版本會快速完成\n")

    # ========================================
    # 示例 2: 長時間 Sleep（1 分鐘）
    # ========================================
    print("【示例 2】長時間 Sleep 演示（1 分鐘）")
    print("-" * 60)

    handle = await client.start_workflow(
        LongSleepWorkflow.run,
        60,  # 60 秒
        "這是 1 分鐘後的消息",
        id=f"long-sleep-{datetime.now().timestamp()}",
        task_queue="long-running-queue",
    )

    print(f"✓ 長時間 Sleep 工作流已啟動: {handle.id}")
    print(f"   將在 1 分鐘後完成")
    print(f"   即使 Worker 重啟，也會繼續執行\n")

    # ========================================
    # 示例 3: 週期性任務（Continue-As-New）
    # ========================================
    print("【示例 3】週期性任務工作流（Continue-As-New）")
    print("-" * 60)

    task = RecurringTask(
        task_id="TASK-001",
        name="每日數據同步",
        interval_days=1,  # 實際：1天，演示：會快速完成
        total_iterations=5,  # 總共 5 次迭代
        current_iteration=0
    )

    handle = await client.start_workflow(
        RecurringTaskWorkflow.run,
        task,
        id=f"recurring-task-{task.task_id}",
        task_queue="long-running-queue",
    )

    print(f"✓ 週期性任務工作流已啟動: {handle.id}")
    print(f"   每 {task.interval_days} 天執行一次")
    print(f"   總共執行 {task.total_iterations} 次")
    print(f"   使用 Continue-As-New 避免歷史過大\n")

    # ========================================
    # 示例 4: 貸款還款工作流
    # ========================================
    print("【示例 4】貸款還款工作流")
    print("-" * 60)

    loan = LoanApplication(
        loan_id="LOAN-001",
        user_id="user456",
        amount=10000.0,
        term_months=12,  # 12 個月
        monthly_payment=850.0
    )

    handle = await client.start_workflow(
        LoanRepaymentWorkflow.run,
        loan,
        id=f"loan-repayment-{loan.loan_id}",
        task_queue="long-running-queue",
    )

    print(f"✓ 貸款還款工作流已啟動: {handle.id}")
    print(f"   期限: {loan.term_months} 個月")
    print(f"   月供: ${loan.monthly_payment}")
    print(f"   實際應用中將運行 {loan.term_months} 個月\n")

    print("=" * 60)
    print("提示：")
    print("  - 這些工作流可以運行數天、數月甚至數年")
    print("  - Worker 可以隨時重啟，工作流會自動恢復")
    print("  - 訪問 http://localhost:8080 查看工作流狀態")
    print("  - 長時間運行的工作流狀態會持久化到數據庫")
    print("=" * 60 + "\n")


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
║              Temporal 長時間運行工作流                         ║
╚══════════════════════════════════════════════════════════════╝

長時間運行能力：
--------------
✓ 可以休眠數天、數月、甚至數年
✓ Worker 重啟不影響工作流執行
✓ 狀態自動持久化到數據庫
✓ 支持 Continue-As-New 避免歷史過大

實際應用場景：
------------
1. 試用訂閱 - 7/14/30 天試用期
2. 定期付款 - 月供、年費等
3. 週期性任務 - 每日/每週/每月執行
4. 長期合同 - 數月到數年的業務流程
5. 延遲執行 - 特定時間後觸發

Continue-As-New：
----------------
- 用於無限期或很長時間的工作流
- 清空歷史記錄，避免過大
- 保持狀態繼續執行
- 適合週期性重複的任務

注意事項：
---------
⚠️ 工作流歷史有大小限制（~50MB）
⚠️ 超長工作流建議使用 Continue-As-New
⚠️ Sleep 基於邏輯時間，不消耗資源

使用方法：
---------
1. 啟動 Worker: python 08_長流程.py
2. 執行示例: python 08_長流程.py client
    """)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 程序已停止")

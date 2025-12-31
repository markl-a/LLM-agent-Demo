"""
Temporal 定時任務 - Cron 調度

這個示例展示了：
1. Cron 工作流調度
2. 定時執行任務
3. 工作流 Sleep（延遲執行）
4. 定時器（Timer）
5. 週期性任務
6. 調度策略
7. 時區處理
8. 手動觸發 vs 自動調度
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional

from temporalio import activity, workflow
from temporalio.client import Client, Schedule, ScheduleActionStartWorkflow, ScheduleSpec, ScheduleIntervalSpec
from temporalio.worker import Worker


# ============================================================
# Activity 定義
# ============================================================

@activity.defn
async def generate_daily_report(date: str) -> dict:
    """
    生成日報

    每天定時執行
    """
    print(f"📊 生成日報: {date}")
    await asyncio.sleep(1)

    # 模擬報表生成
    report = {
        "date": date,
        "total_orders": 150,
        "total_revenue": 15000.0,
        "new_users": 25
    }

    print(f"  ✓ 報表生成完成: {report}")
    return report


@activity.defn
async def send_report(report: dict, recipients: list) -> bool:
    """
    發送報表

    發送郵件通知
    """
    print(f"📧 發送報表給: {', '.join(recipients)}")
    await asyncio.sleep(0.5)
    print(f"  ✓ 報表已發送")
    return True


@activity.defn
async def cleanup_old_data(days_old: int) -> dict:
    """
    清理舊數據

    定期清理任務
    """
    print(f"🧹 清理 {days_old} 天前的數據")
    await asyncio.sleep(1)

    result = {
        "deleted_records": 1500,
        "freed_space_mb": 250,
        "days_old": days_old
    }

    print(f"  ✓ 清理完成: 刪除 {result['deleted_records']} 條記錄")
    return result


@activity.defn
async def check_system_health() -> dict:
    """
    系統健康檢查

    定期監控
    """
    print(f"🏥 執行系統健康檢查")
    await asyncio.sleep(0.5)

    health = {
        "timestamp": datetime.now().isoformat(),
        "cpu_usage": 45.2,
        "memory_usage": 62.8,
        "disk_usage": 58.5,
        "status": "healthy"
    }

    print(f"  ✓ 系統狀態: {health['status']}")
    return health


@activity.defn
async def sync_external_data(source: str) -> dict:
    """
    同步外部數據

    定期數據同步
    """
    print(f"🔄 同步數據源: {source}")
    await asyncio.sleep(1.5)

    result = {
        "source": source,
        "records_synced": 500,
        "timestamp": datetime.now().isoformat()
    }

    print(f"  ✓ 同步完成: {result['records_synced']} 條記錄")
    return result


@activity.defn
async def backup_database() -> dict:
    """
    數據庫備份

    每日備份
    """
    print(f"💾 開始數據庫備份")
    await asyncio.sleep(2)

    result = {
        "backup_id": f"BACKUP-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "size_mb": 1024,
        "duration_seconds": 2,
        "status": "completed"
    }

    print(f"  ✓ 備份完成: {result['backup_id']}")
    return result


@activity.defn
async def send_reminder(user_id: str, message: str) -> bool:
    """
    發送提醒

    定時提醒任務
    """
    print(f"⏰ 發送提醒給用戶 {user_id}: {message}")
    await asyncio.sleep(0.3)
    return True


# ============================================================
# 工作流 1: 簡單定時任務
# ============================================================

@workflow.defn
class DailyReportWorkflow:
    """
    每日報表工作流

    每天固定時間執行
    """

    @workflow.run
    async def run(self) -> dict:
        """
        生成並發送日報
        """
        # 獲取當前日期
        current_date = workflow.now().strftime("%Y-%m-%d")

        print(f"\n📅 日報工作流: {current_date}")

        # 生成報表
        report = await workflow.execute_activity(
            generate_daily_report,
            current_date,
            start_to_close_timeout=timedelta(minutes=5),
        )

        # 發送報表
        recipients = ["manager@example.com", "team@example.com"]
        sent = await workflow.execute_activity(
            send_report,
            report,
            recipients,
            start_to_close_timeout=timedelta(minutes=2),
        )

        return {
            "date": current_date,
            "report": report,
            "sent": sent,
            "workflow_time": workflow.now().isoformat()
        }


# ============================================================
# 工作流 2: 週期性清理任務
# ============================================================

@workflow.defn
class CleanupWorkflow:
    """
    週期性清理工作流

    定期清理舊數據和日誌
    """

    @workflow.run
    async def run(self, days_to_keep: int = 30) -> dict:
        """
        執行清理任務
        """
        print(f"\n🧹 清理工作流: 保留 {days_to_keep} 天數據")

        # 清理舊數據
        cleanup_result = await workflow.execute_activity(
            cleanup_old_data,
            days_to_keep,
            start_to_close_timeout=timedelta(minutes=10),
        )

        # 執行數據庫備份（清理後）
        backup_result = await workflow.execute_activity(
            backup_database,
            start_to_close_timeout=timedelta(minutes=30),
        )

        return {
            "cleanup": cleanup_result,
            "backup": backup_result,
            "completed_at": workflow.now().isoformat()
        }


# ============================================================
# 工作流 3: 健康檢查工作流
# ============================================================

@workflow.defn
class HealthCheckWorkflow:
    """
    系統健康檢查工作流

    每 5 分鐘執行一次
    """

    @workflow.run
    async def run(self) -> dict:
        """
        執行健康檢查
        """
        print(f"\n🏥 健康檢查工作流")

        # 檢查系統健康
        health = await workflow.execute_activity(
            check_system_health,
            start_to_close_timeout=timedelta(seconds=30),
        )

        # 如果狀態不健康，發送告警
        if health["status"] != "healthy":
            await workflow.execute_activity(
                send_reminder,
                "admin",
                f"系統健康狀態異常: {health['status']}",
                start_to_close_timeout=timedelta(seconds=10),
            )

        return health


# ============================================================
# 工作流 4: 數據同步工作流
# ============================================================

@workflow.defn
class DataSyncWorkflow:
    """
    數據同步工作流

    每小時同步外部數據
    """

    @workflow.run
    async def run(self, sources: list) -> dict:
        """
        同步多個數據源
        """
        print(f"\n🔄 數據同步工作流: {len(sources)} 個數據源")

        results = []

        # 並行同步所有數據源
        tasks = [
            workflow.execute_activity(
                sync_external_data,
                source,
                start_to_close_timeout=timedelta(minutes=5),
            )
            for source in sources
        ]

        sync_results = await asyncio.gather(*tasks)
        results.extend(sync_results)

        total_records = sum(r["records_synced"] for r in results)

        return {
            "sources_synced": len(sources),
            "total_records": total_records,
            "results": results,
            "completed_at": workflow.now().isoformat()
        }


# ============================================================
# 工作流 5: 延遲執行工作流
# ============================================================

@workflow.defn
class DelayedTaskWorkflow:
    """
    延遲執行工作流

    演示工作流 Sleep
    """

    @workflow.run
    async def run(self, user_id: str, reminder_message: str, delay_minutes: int) -> dict:
        """
        延遲後發送提醒

        Args:
            user_id: 用戶 ID
            reminder_message: 提醒消息
            delay_minutes: 延遲分鐘數
        """
        print(f"\n⏰ 延遲任務: {delay_minutes} 分鐘後提醒用戶 {user_id}")

        # 工作流休眠（延遲執行）
        # 注意：即使 Worker 重啟，休眠也會繼續
        await asyncio.sleep(delay_minutes * 60)

        print(f"  ✓ 休眠結束，發送提醒")

        # 發送提醒
        sent = await workflow.execute_activity(
            send_reminder,
            user_id,
            reminder_message,
            start_to_close_timeout=timedelta(seconds=30),
        )

        return {
            "user_id": user_id,
            "reminder_sent": sent,
            "delay_minutes": delay_minutes,
            "sent_at": workflow.now().isoformat()
        }


# ============================================================
# 工作流 6: 複雜定時工作流（帶條件）
# ============================================================

@workflow.defn
class SmartScheduleWorkflow:
    """
    智能調度工作流

    根據條件決定是否執行任務
    """

    @workflow.run
    async def run(self) -> dict:
        """
        智能調度執行
        """
        current_time = workflow.now()
        current_hour = current_time.hour
        is_weekend = current_time.weekday() >= 5  # 5=週六, 6=週日

        print(f"\n🤖 智能調度: {current_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"  小時: {current_hour}, 週末: {is_weekend}")

        tasks_executed = []

        # 工作日上午 9 點：生成報表
        if not is_weekend and current_hour == 9:
            report = await workflow.execute_activity(
                generate_daily_report,
                current_time.strftime("%Y-%m-%d"),
                start_to_close_timeout=timedelta(minutes=5),
            )
            tasks_executed.append("daily_report")

        # 每天凌晨 2 點：備份數據庫
        if current_hour == 2:
            backup = await workflow.execute_activity(
                backup_database,
                start_to_close_timeout=timedelta(minutes=30),
            )
            tasks_executed.append("database_backup")

        # 每天凌晨 3 點：清理數據
        if current_hour == 3:
            cleanup = await workflow.execute_activity(
                cleanup_old_data,
                30,
                start_to_close_timeout=timedelta(minutes=10),
            )
            tasks_executed.append("data_cleanup")

        # 週日凌晨 4 點：完整系統維護
        if is_weekend and current_time.weekday() == 6 and current_hour == 4:
            # 執行完整維護
            tasks_executed.append("full_maintenance")

        return {
            "executed_at": current_time.isoformat(),
            "tasks_executed": tasks_executed,
            "is_weekend": is_weekend,
            "hour": current_hour
        }


# ============================================================
# Worker 和 Client
# ============================================================

async def run_worker():
    """啟動 Worker"""
    client = await Client.connect("localhost:7233")

    print("=" * 60)
    print("🚀 定時任務 Worker 啟動中...")
    print("=" * 60)

    worker = Worker(
        client,
        task_queue="scheduled-tasks-queue",
        workflows=[
            DailyReportWorkflow,
            CleanupWorkflow,
            HealthCheckWorkflow,
            DataSyncWorkflow,
            DelayedTaskWorkflow,
            SmartScheduleWorkflow,
        ],
        activities=[
            generate_daily_report,
            send_report,
            cleanup_old_data,
            check_system_health,
            sync_external_data,
            backup_database,
            send_reminder,
        ],
    )

    print("等待調度任務...\n")
    await worker.run()


async def run_client():
    """創建和管理調度"""
    client = await Client.connect("localhost:7233")

    print("\n" + "=" * 60)
    print("📋 定時任務調度示例")
    print("=" * 60)

    # ========================================
    # 示例 1: 創建每日報表調度（Cron）
    # ========================================
    print("\n【示例 1】創建每日報表調度")
    print("-" * 60)
    print("調度時間: 每天上午 9:00")

    try:
        # 創建調度
        schedule_handle = await client.create_schedule(
            "daily-report-schedule",
            Schedule(
                action=ScheduleActionStartWorkflow(
                    DailyReportWorkflow.run,
                    id="daily-report-workflow",
                    task_queue="scheduled-tasks-queue",
                ),
                spec=ScheduleSpec(
                    # Cron 表達式: 每天 9:00 AM
                    cron_expressions=["0 9 * * *"],
                    # 時區
                    timezone="Asia/Taipei",
                ),
            ),
        )
        print(f"✓ 調度已創建: daily-report-schedule")
        print(f"  下次執行: 每天 09:00 (台北時間)\n")

    except Exception as e:
        if "already exists" in str(e).lower():
            print(f"⚠️  調度已存在，跳過創建\n")
        else:
            print(f"✗ 創建失敗: {e}\n")

    # ========================================
    # 示例 2: 創建週期性健康檢查（每 5 分鐘）
    # ========================================
    print("【示例 2】創建週期性健康檢查")
    print("-" * 60)
    print("調度頻率: 每 5 分鐘")

    try:
        await client.create_schedule(
            "health-check-schedule",
            Schedule(
                action=ScheduleActionStartWorkflow(
                    HealthCheckWorkflow.run,
                    id="health-check-workflow",
                    task_queue="scheduled-tasks-queue",
                ),
                spec=ScheduleSpec(
                    # 每 5 分鐘執行一次
                    intervals=[ScheduleIntervalSpec(
                        every=timedelta(minutes=5)
                    )],
                ),
            ),
        )
        print(f"✓ 調度已創建: health-check-schedule")
        print(f"  執行頻率: 每 5 分鐘\n")

    except Exception as e:
        if "already exists" in str(e).lower():
            print(f"⚠️  調度已存在，跳過創建\n")
        else:
            print(f"✗ 創建失敗: {e}\n")

    # ========================================
    # 示例 3: 創建週末清理任務
    # ========================================
    print("【示例 3】創建週末清理任務")
    print("-" * 60)
    print("調度時間: 每週日凌晨 2:00")

    try:
        await client.create_schedule(
            "weekly-cleanup-schedule",
            Schedule(
                action=ScheduleActionStartWorkflow(
                    CleanupWorkflow.run,
                    30,  # 保留 30 天
                    id="weekly-cleanup-workflow",
                    task_queue="scheduled-tasks-queue",
                ),
                spec=ScheduleSpec(
                    # 每週日 2:00 AM
                    cron_expressions=["0 2 * * 0"],
                    timezone="Asia/Taipei",
                ),
            ),
        )
        print(f"✓ 調度已創建: weekly-cleanup-schedule")
        print(f"  執行時間: 每週日 02:00\n")

    except Exception as e:
        if "already exists" in str(e).lower():
            print(f"⚠️  調度已存在，跳過創建\n")
        else:
            print(f"✗ 創建失敗: {e}\n")

    # ========================================
    # 示例 4: 手動觸發工作流（非調度）
    # ========================================
    print("【示例 4】手動觸發工作流")
    print("-" * 60)

    result = await client.execute_workflow(
        DailyReportWorkflow.run,
        id="manual-daily-report-1",
        task_queue="scheduled-tasks-queue",
    )
    print(f"✓ 手動執行完成: {result['date']}\n")

    # ========================================
    # 示例 5: 延遲執行工作流
    # ========================================
    print("【示例 5】延遲執行工作流")
    print("-" * 60)
    print("延遲 1 分鐘後發送提醒")

    # 注意：這會啟動工作流但不等待完成
    handle = await client.start_workflow(
        DelayedTaskWorkflow.run,
        "user123",
        "您的會議將在 1 分鐘後開始",
        1,  # 延遲 1 分鐘
        id=f"delayed-reminder-{datetime.now().timestamp()}",
        task_queue="scheduled-tasks-queue",
    )
    print(f"✓ 延遲任務已啟動: {handle.id}")
    print(f"  1 分鐘後將發送提醒\n")

    # ========================================
    # 示例 6: 數據同步調度（每小時）
    # ========================================
    print("【示例 6】創建數據同步調度")
    print("-" * 60)
    print("調度頻率: 每小時")

    try:
        await client.create_schedule(
            "hourly-sync-schedule",
            Schedule(
                action=ScheduleActionStartWorkflow(
                    DataSyncWorkflow.run,
                    ["source1", "source2", "source3"],
                    id="hourly-sync-workflow",
                    task_queue="scheduled-tasks-queue",
                ),
                spec=ScheduleSpec(
                    # 每小時執行
                    cron_expressions=["0 * * * *"],
                ),
            ),
        )
        print(f"✓ 調度已創建: hourly-sync-schedule")
        print(f"  執行頻率: 每小時\n")

    except Exception as e:
        if "already exists" in str(e).lower():
            print(f"⚠️  調度已存在，跳過創建\n")
        else:
            print(f"✗ 創建失敗: {e}\n")

    # ========================================
    # 查看所有調度
    # ========================================
    print("【調度列表】")
    print("-" * 60)

    schedules = [
        "daily-report-schedule",
        "health-check-schedule",
        "weekly-cleanup-schedule",
        "hourly-sync-schedule",
    ]

    for schedule_id in schedules:
        try:
            handle = client.get_schedule_handle(schedule_id)
            desc = await handle.describe()
            print(f"📅 {schedule_id}")
            print(f"   狀態: {'運行中' if not desc.schedule.state.paused else '暫停'}")
        except Exception:
            pass

    print("\n" + "=" * 60)
    print("提示:")
    print("  - 訪問 http://localhost:8080 查看 Web UI")
    print("  - 在 UI 中可以查看和管理所有調度")
    print("  - 調度會持久化，Server 重啟後仍然有效")
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
║              Temporal 定時任務與調度                           ║
╚══════════════════════════════════════════════════════════════╝

調度類型：
---------
1. Cron 調度 - 使用 Cron 表達式（如: 0 9 * * *）
2. 間隔調度 - 固定時間間隔（如: 每 5 分鐘）
3. 延遲執行 - 工作流內 Sleep
4. 智能調度 - 根據條件執行

Cron 表達式格式：
---------------
分 時 日 月 週
0  9  *  *  *   # 每天 9:00
0  */2 * *  *   # 每 2 小時
0  2  *  *  0   # 每週日 2:00
0  0  1  *  *   # 每月 1 日 0:00

使用方法：
---------
1. 啟動 Worker: python 05_定時任務.py
2. 創建調度: python 05_定時任務.py client

管理調度：
---------
- Web UI: http://localhost:8080
- 可以暫停/恢復/刪除調度
- 查看執行歷史
    """)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 程序已停止")

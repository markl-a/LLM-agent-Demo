#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Prefect 調度器配置
===================

這個示例展示了 Prefect 的調度功能，包括：
1. Cron 調度
2. Interval 調度
3. RRule 調度
4. 部署（Deployment）配置
5. 調度管理
6. 動態調度
"""

from prefect import task, flow, get_run_logger
from prefect.server.schemas.schedules import (
    CronSchedule,
    IntervalSchedule,
    RRuleSchedule
)
from datetime import datetime, timedelta
from dateutil import rrule
import time


# ============================================================================
# 基本任務定義
# ============================================================================

@task
def daily_report_task() -> dict:
    """
    生成每日報告

    Returns:
        報告數據
    """
    logger = get_run_logger()
    logger.info("生成每日報告")

    report = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
        "metrics": {
            "tasks_completed": 150,
            "success_rate": 0.95,
            "avg_duration": 2.5
        }
    }

    logger.info(f"報告生成完成：{report['date']}")
    return report


@task
def data_sync_task(source: str, target: str) -> str:
    """
    數據同步任務

    Args:
        source: 源系統
        target: 目標系統

    Returns:
        同步狀態
    """
    logger = get_run_logger()
    logger.info(f"同步數據：{source} -> {target}")

    # 模擬同步
    time.sleep(1)

    message = f"✓ 數據已從 {source} 同步到 {target}"
    logger.info(message)
    return message


@task
def cleanup_task() -> str:
    """
    清理任務

    Returns:
        清理狀態
    """
    logger = get_run_logger()
    logger.info("執行清理任務")

    # 模擬清理
    time.sleep(0.5)

    message = "✓ 臨時文件已清理"
    logger.info(message)
    return message


# ============================================================================
# 工作流定義
# ============================================================================

@flow(name="每日報告工作流")
def daily_report_flow():
    """
    每日報告生成工作流
    """
    logger = get_run_logger()
    logger.info("=" * 60)
    logger.info("開始每日報告工作流")
    logger.info("=" * 60)

    report = daily_report_task()
    logger.info(f"報告已生成：{report}")

    return report


@flow(name="每小時數據同步")
def hourly_sync_flow(source: str = "Database", target: str = "Warehouse"):
    """
    每小時數據同步工作流

    Args:
        source: 源系統
        target: 目標系統
    """
    logger = get_run_logger()
    logger.info("=" * 60)
    logger.info("開始數據同步工作流")
    logger.info("=" * 60)

    status = data_sync_task(source, target)
    logger.info(status)

    return status


@flow(name="夜間維護工作流")
def nightly_maintenance_flow():
    """
    夜間維護工作流
    """
    logger = get_run_logger()
    logger.info("=" * 60)
    logger.info("開始夜間維護工作流")
    logger.info("=" * 60)

    # 執行清理
    cleanup_status = cleanup_task()

    # 執行數據同步
    sync_status = data_sync_task("Production", "Backup")

    logger.info("夜間維護完成")
    return {
        "cleanup": cleanup_status,
        "sync": sync_status
    }


# ============================================================================
# Cron 調度示例
# ============================================================================

def create_cron_schedule_examples():
    """
    創建 Cron 調度示例

    Cron 表達式格式：
    * * * * *
    │ │ │ │ │
    │ │ │ │ └─ 星期幾 (0-7, 0 和 7 都表示星期日)
    │ │ │ └─── 月份 (1-12)
    │ │ └───── 日期 (1-31)
    │ └─────── 小時 (0-23)
    └───────── 分鐘 (0-59)
    """
    logger = get_run_logger()
    logger.info("Cron 調度示例：")

    examples = {
        "每天凌晨 2 點": "0 2 * * *",
        "每小時整點": "0 * * * *",
        "每 30 分鐘": "*/30 * * * *",
        "工作日上午 9 點": "0 9 * * 1-5",
        "每週一上午 10 點": "0 10 * * 1",
        "每月 1 號上午 8 點": "0 8 1 * *",
        "每 15 分鐘": "*/15 * * * *",
        "每天中午 12 點": "0 12 * * *",
    }

    for description, cron_expr in examples.items():
        logger.info(f"  {description}: {cron_expr}")

    return examples


@flow(name="Cron 調度示例")
def cron_schedule_demo():
    """
    演示 Cron 調度的定義
    """
    logger = get_run_logger()
    logger.info("=" * 60)
    logger.info("Cron 調度配置示例")
    logger.info("=" * 60)

    # 創建 Cron 調度
    examples = create_cron_schedule_examples()

    logger.info("\n使用示例：")
    logger.info("""
    # 部署時指定 Cron 調度
    flow.deploy(
        name="daily-report",
        schedule=CronSchedule(cron="0 2 * * *", timezone="Asia/Taipei")
    )
    """)

    return examples


# ============================================================================
# Interval 調度示例
# ============================================================================

@flow(name="Interval 調度示例")
def interval_schedule_demo():
    """
    演示 Interval 調度的定義
    """
    logger = get_run_logger()
    logger.info("=" * 60)
    logger.info("Interval 調度配置示例")
    logger.info("=" * 60)

    logger.info("Interval 調度示例：")
    logger.info("  - 每 5 分鐘: IntervalSchedule(interval=timedelta(minutes=5))")
    logger.info("  - 每小時: IntervalSchedule(interval=timedelta(hours=1))")
    logger.info("  - 每天: IntervalSchedule(interval=timedelta(days=1))")
    logger.info("  - 每 30 秒: IntervalSchedule(interval=timedelta(seconds=30))")

    logger.info("\n使用示例：")
    logger.info("""
    # 部署時指定 Interval 調度
    flow.deploy(
        name="hourly-sync",
        schedule=IntervalSchedule(
            interval=timedelta(hours=1),
            anchor_date=datetime(2024, 1, 1, 0, 0, 0)  # 可選的錨點時間
        )
    )
    """)


# ============================================================================
# RRule 調度示例
# ============================================================================

@flow(name="RRule 調度示例")
def rrule_schedule_demo():
    """
    演示 RRule 調度的定義

    RRule 提供了更複雜和靈活的調度規則
    """
    logger = get_run_logger()
    logger.info("=" * 60)
    logger.info("RRule 調度配置示例")
    logger.info("=" * 60)

    logger.info("RRule 調度示例：")

    # 每個工作日
    logger.info("\n1. 每個工作日上午 9 點：")
    logger.info("   RRuleSchedule(")
    logger.info("       rrule='FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR;BYHOUR=9;BYMINUTE=0'")
    logger.info("   )")

    # 每月最後一天
    logger.info("\n2. 每月最後一天：")
    logger.info("   RRuleSchedule(")
    logger.info("       rrule='FREQ=MONTHLY;BYMONTHDAY=-1'")
    logger.info("   )")

    # 每季度第一天
    logger.info("\n3. 每季度第一天：")
    logger.info("   RRuleSchedule(")
    logger.info("       rrule='FREQ=MONTHLY;INTERVAL=3;BYMONTHDAY=1'")
    logger.info("   )")

    # 每週一和週五
    logger.info("\n4. 每週一和週五：")
    logger.info("   RRuleSchedule(")
    logger.info("       rrule='FREQ=WEEKLY;BYDAY=MO,FR'")
    logger.info("   )")

    logger.info("\n使用示例：")
    logger.info("""
    # 部署時指定 RRule 調度
    flow.deploy(
        name="weekly-report",
        schedule=RRuleSchedule(
            rrule='FREQ=WEEKLY;BYDAY=MO;BYHOUR=9;BYMINUTE=0',
            timezone='Asia/Taipei'
        )
    )
    """)


# ============================================================================
# 部署配置示例
# ============================================================================

@flow(name="可部署的工作流")
def deployable_flow(environment: str = "production"):
    """
    可部署的工作流示例

    Args:
        environment: 環境名稱
    """
    logger = get_run_logger()
    logger.info(f"在 {environment} 環境中執行工作流")

    # 執行任務
    report = daily_report_task()

    logger.info(f"工作流完成：{report}")
    return report


def create_deployment_examples():
    """
    創建部署配置示例

    注意：這些是示例代碼，實際部署需要 Prefect 服務器運行
    """
    print("\n" + "=" * 70)
    print("部署配置示例")
    print("=" * 70)

    examples = """
# 示例 1: 使用 Cron 調度部署
# 每天凌晨 2 點執行
deployable_flow.deploy(
    name="daily-production-report",
    schedule=CronSchedule(
        cron="0 2 * * *",
        timezone="Asia/Taipei"
    ),
    work_pool_name="default-agent-pool",
    parameters={"environment": "production"},
    tags=["production", "daily-report"]
)

# 示例 2: 使用 Interval 調度部署
# 每小時執行
hourly_sync_flow.deploy(
    name="hourly-data-sync",
    schedule=IntervalSchedule(
        interval=timedelta(hours=1)
    ),
    work_pool_name="default-agent-pool",
    parameters={
        "source": "Database",
        "target": "Warehouse"
    },
    tags=["sync", "hourly"]
)

# 示例 3: 使用 RRule 調度部署
# 每週一上午 9 點執行
nightly_maintenance_flow.deploy(
    name="weekly-maintenance",
    schedule=RRuleSchedule(
        rrule="FREQ=WEEKLY;BYDAY=MO;BYHOUR=9;BYMINUTE=0",
        timezone="Asia/Taipei"
    ),
    work_pool_name="maintenance-pool",
    tags=["maintenance", "weekly"]
)

# 示例 4: 多個調度
# 同一個工作流可以有多個部署，使用不同的調度
deployable_flow.deploy(
    name="hourly-dev-report",
    schedule=IntervalSchedule(interval=timedelta(hours=1)),
    work_pool_name="dev-pool",
    parameters={"environment": "development"},
    tags=["development", "hourly"]
)

deployable_flow.deploy(
    name="daily-staging-report",
    schedule=CronSchedule(cron="0 8 * * *"),
    work_pool_name="staging-pool",
    parameters={"environment": "staging"},
    tags=["staging", "daily"]
)

# 示例 5: 暫停調度
# 創建部署但不啟用調度
deployable_flow.deploy(
    name="manual-report",
    work_pool_name="default-agent-pool",
    parameters={"environment": "production"},
    tags=["manual"],
    # 不指定 schedule，需要手動觸發
)
    """

    print(examples)


# ============================================================================
# 調度管理命令
# ============================================================================

def show_schedule_management_commands():
    """
    顯示調度管理命令
    """
    print("\n" + "=" * 70)
    print("調度管理命令")
    print("=" * 70)

    commands = """
# 1. 查看所有部署
prefect deployment ls

# 2. 查看特定部署的詳情
prefect deployment inspect "flow-name/deployment-name"

# 3. 運行部署（手動觸發）
prefect deployment run "flow-name/deployment-name"

# 4. 暫停部署
prefect deployment pause "flow-name/deployment-name"

# 5. 恢復部署
prefect deployment resume "flow-name/deployment-name"

# 6. 刪除部署
prefect deployment delete "flow-name/deployment-name"

# 7. 創建部署（從 YAML）
prefect deployment apply deployment.yaml

# 8. 查看調度執行歷史
prefect flow-run ls --deployment-name "deployment-name"

# 9. 更新部署參數
prefect deployment set-schedule "flow-name/deployment-name" \\
    --cron "0 3 * * *"

# 10. 啟動 Work Pool Agent
prefect agent start --pool "default-agent-pool"
    """

    print(commands)


# ============================================================================
# 動態調度示例
# ============================================================================

@task
def check_condition() -> bool:
    """
    檢查是否需要執行任務

    Returns:
        是否需要執行
    """
    logger = get_run_logger()
    logger.info("檢查執行條件")

    # 模擬條件檢查（例如：檢查數據量）
    import random
    should_run = random.choice([True, False])

    logger.info(f"條件檢查結果：{'需要執行' if should_run else '跳過'}")
    return should_run


@flow(name="條件調度工作流")
def conditional_scheduled_flow():
    """
    根據條件決定是否執行的工作流
    """
    logger = get_run_logger()
    logger.info("=" * 60)
    logger.info("條件調度工作流")
    logger.info("=" * 60)

    # 檢查條件
    should_run = check_condition()

    if should_run:
        logger.info("條件滿足，執行任務")
        report = daily_report_task()
        logger.info(f"任務完成：{report}")
        return report
    else:
        logger.info("條件不滿足，跳過任務")
        return None


# ============================================================================
# 運行示例
# ============================================================================

def main():
    """
    主函數 - 運行所有示例
    """
    print("\n" + "=" * 70)
    print("Prefect 調度器配置")
    print("=" * 70)

    # 示例 1: 執行工作流
    print("\n【示例 1】執行每日報告工作流")
    print("-" * 70)
    daily_report_flow()

    print("\n【示例 2】執行數據同步工作流")
    print("-" * 70)
    hourly_sync_flow()

    print("\n【示例 3】執行夜間維護工作流")
    print("-" * 70)
    nightly_maintenance_flow()

    # 示例 2: Cron 調度
    print("\n【示例 4】Cron 調度配置")
    print("-" * 70)
    cron_schedule_demo()

    # 示例 3: Interval 調度
    print("\n【示例 5】Interval 調度配置")
    print("-" * 70)
    interval_schedule_demo()

    # 示例 4: RRule 調度
    print("\n【示例 6】RRule 調度配置")
    print("-" * 70)
    rrule_schedule_demo()

    # 示例 5: 條件調度
    print("\n【示例 7】條件調度工作流")
    print("-" * 70)
    conditional_scheduled_flow()

    # 部署示例
    create_deployment_examples()

    # 管理命令
    show_schedule_management_commands()

    # 使用說明
    print("\n" + "=" * 70)
    print("調度器總結")
    print("=" * 70)
    print("""
1. 調度類型：
   - CronSchedule: 使用 Cron 表達式
   - IntervalSchedule: 基於時間間隔
   - RRuleSchedule: 複雜的重複規則

2. 部署工作流：
   flow.deploy(
       name="deployment-name",
       schedule=CronSchedule(cron="0 2 * * *"),
       work_pool_name="pool-name",
       parameters={"key": "value"}
   )

3. 常用 Cron 表達式：
   - "0 * * * *"      每小時整點
   - "*/30 * * * *"   每 30 分鐘
   - "0 2 * * *"      每天凌晨 2 點
   - "0 9 * * 1-5"    工作日上午 9 點
   - "0 0 1 * *"      每月 1 號

4. 時區設置：
   - 使用 timezone 參數指定時區
   - 例如："Asia/Taipei", "UTC", "America/New_York"

5. 管理調度：
   - 使用 prefect deployment 命令管理
   - 可以暫停、恢復、刪除部署
   - 支持手動觸發

6. Work Pool：
   - 定義任務執行的基礎設施
   - 需要啟動 Agent 來執行任務
   - 支持 Process, Docker, Kubernetes 等

7. 最佳實踐：
   - 為不同環境創建不同的部署
   - 使用標籤組織部署
   - 設置合理的重試策略
   - 監控調度執行情況

8. 下一步：
   - 啟動 Prefect 服務器：prefect server start
   - 創建部署並測試調度
   - 查看 06_狀態管理.py 了解狀態處理
   - 查看 09_部署配置.py 了解更多部署選項
    """)

    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()

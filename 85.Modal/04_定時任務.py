"""
Modal 定時任務示例

本示例展示：
1. 定時執行函數（Cron）
2. 週期性任務
3. 任務調度策略
4. 實際應用案例
"""

import modal
from rich.console import Console
from rich.panel import Panel
from datetime import datetime

console = Console()

# 創建應用
app = modal.App("scheduled-tasks")


# 示例 1: 每小時執行一次
@app.function(schedule=modal.Period(hours=1))
def hourly_task():
    """每小時執行一次的任務"""
    current_time = datetime.now()
    print(f"[{current_time}] 每小時任務執行")
    print(f"當前時間: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # 模擬任務
    task_result = {
        "task": "hourly_task",
        "executed_at": current_time.isoformat(),
        "status": "success"
    }

    print(f"任務結果: {task_result}")
    return task_result


# 示例 2: 每天執行一次
@app.function(schedule=modal.Period(days=1))
def daily_task():
    """每天執行一次的任務"""
    print("執行每日任務...")
    print(f"執行時間: {datetime.now()}")

    # 模擬每日報告生成
    report = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "metrics": {
            "users": 1234,
            "revenue": 5678.90,
            "transactions": 456
        }
    }

    print(f"每日報告: {report}")
    return report


# 示例 3: 使用 Cron 表達式
@app.function(schedule=modal.Cron("0 9 * * *"))  # 每天早上 9 點（UTC）
def morning_task():
    """每天早上 9 點執行"""
    print("早安！執行晨間任務...")
    print(f"UTC 時間: {datetime.utcnow()}")

    # 模擬發送早報
    return {
        "task": "morning_report",
        "time": "09:00 UTC",
        "status": "sent"
    }


# 示例 4: 工作日任務
@app.function(schedule=modal.Cron("0 10 * * 1-5"))  # 週一到週五 10 點
def weekday_task():
    """只在工作日執行的任務"""
    print("工作日任務執行...")
    print(f"今天是: {datetime.now().strftime('%A')}")

    return {
        "task": "weekday_sync",
        "executed": datetime.now().isoformat()
    }


# 示例 5: 每週任務
@app.function(schedule=modal.Cron("0 0 * * 0"))  # 每週日午夜
def weekly_task():
    """每週執行一次的任務"""
    print("執行每週清理任務...")

    # 模擬清理操作
    cleaned = {
        "old_files": 123,
        "cache_cleared": "500 MB",
        "logs_archived": 45
    }

    print(f"清理結果: {cleaned}")
    return cleaned


# 示例 6: 每 15 分鐘執行
@app.function(schedule=modal.Period(minutes=15))
def frequent_task():
    """高頻執行的任務"""
    print("執行高頻監控任務...")

    # 模擬健康檢查
    health = {
        "timestamp": datetime.now().isoformat(),
        "services": {
            "api": "healthy",
            "database": "healthy",
            "cache": "healthy"
        }
    }

    print(f"健康狀態: {health}")
    return health


# 示例 7: 數據同步任務
@app.function(schedule=modal.Period(hours=6))
def data_sync_task():
    """每 6 小時同步數據"""
    print("開始數據同步...")

    # 模擬數據同步
    import time
    start = time.time()

    # 模擬處理
    time.sleep(2)

    elapsed = time.time() - start

    result = {
        "synced_records": 1000,
        "duration": f"{elapsed:.2f}s",
        "timestamp": datetime.now().isoformat()
    }

    print(f"同步完成: {result}")
    return result


# 示例 8: 備份任務
@app.function(schedule=modal.Cron("0 2 * * *"))  # 每天凌晨 2 點
def backup_task():
    """每日備份任務"""
    print("執行備份任務...")

    # 模擬備份
    backup_info = {
        "backup_time": datetime.now().isoformat(),
        "databases": ["users", "orders", "products"],
        "size": "2.5 GB",
        "location": "s3://backups/2024-01-15/"
    }

    print(f"備份完成: {backup_info}")
    return backup_info


# 手動觸發函數（用於測試）
@app.function()
def test_scheduled_function():
    """手動測試定時任務的邏輯"""
    print("手動執行定時任務邏輯...")

    # 調用定時任務的邏輯
    result = {
        "manual_test": True,
        "timestamp": datetime.now().isoformat(),
        "message": "這是手動測試，模擬定時任務執行"
    }

    print(f"測試結果: {result}")
    return result


@app.local_entrypoint()
def main():
    """本地入口（用於測試）"""
    console.print(Panel.fit(
        "[bold cyan]Modal 定時任務示例[/bold cyan]\n"
        "[dim]設置和管理定時任務[/dim]",
        border_style="cyan"
    ))

    console.print("\n[cyan]手動測試定時任務邏輯...[/cyan]")
    result = test_scheduled_function.remote()
    console.print(f"[green]結果: {result}[/green]")

    console.print("\n" + "="*60)
    console.print("[bold green]✓ 定時任務配置完成！[/bold green]")
    console.print("\n[yellow]注意:[/yellow]")
    console.print("  定時任務需要部署後才會自動執行")
    console.print("  使用 'modal deploy 04_定時任務.py' 部署")


def print_schedule_guide():
    """打印定時任務指南"""
    console.print("\n" + "="*60)
    console.print("[bold cyan]定時任務配置指南:[/bold cyan]")
    console.print("""
[green]1. Period（週期）:[/green]

@app.function(schedule=modal.Period(
    days=1,        # 天
    hours=1,       # 小時
    minutes=30,    # 分鐘
    seconds=30     # 秒
))

示例:
• modal.Period(hours=1) - 每小時
• modal.Period(days=1) - 每天
• modal.Period(minutes=15) - 每 15 分鐘

[green]2. Cron（表達式）:[/green]

@app.function(schedule=modal.Cron("分 時 日 月 週"))

格式:
┌─ 分鐘 (0-59)
│ ┌─ 小時 (0-23)
│ │ ┌─ 日期 (1-31)
│ │ │ ┌─ 月份 (1-12)
│ │ │ │ ┌─ 星期 (0-7, 0和7都是週日)
│ │ │ │ │
* * * * *

示例:
• "0 9 * * *" - 每天 9:00
• "*/15 * * * *" - 每 15 分鐘
• "0 0 * * 0" - 每週日午夜
• "0 2 * * 1-5" - 週一到週五 2:00
• "0 */6 * * *" - 每 6 小時

[green]3. 常用場景:[/green]

• 每小時: Period(hours=1)
• 每天午夜: Cron("0 0 * * *")
• 工作日: Cron("0 9 * * 1-5")
• 每週一: Cron("0 0 * * 1")
• 每月 1 號: Cron("0 0 1 * *")

[yellow]部署定時任務:[/yellow]

# 部署
modal deploy script.py

# 查看定時任務
modal app logs your-app-name

# 停止應用（包括定時任務）
modal app stop your-app-name

[yellow]最佳實踐:[/yellow]

✓ 使用 UTC 時間（避免時區問題）
✓ 添加錯誤處理和重試
✓ 記錄執行日誌
✓ 設置合理的超時
✓ 監控任務執行狀態
✓ 考慮冪等性（重複執行無副作用）
    """)
    console.print("="*60 + "\n")


def print_real_world_examples():
    """打印實際應用示例"""
    console.print("\n" + "="*60)
    console.print("[bold cyan]實際應用場景:[/bold cyan]")
    console.print("""
[green]1. 數據同步[/green]
# 每小時從外部 API 同步數據
@app.function(schedule=modal.Period(hours=1))
def sync_external_data():
    # 調用外部 API
    # 存儲到數據庫
    pass

[green]2. 報告生成[/green]
# 每天早上 8 點生成報告
@app.function(schedule=modal.Cron("0 8 * * *"))
def generate_daily_report():
    # 聚合數據
    # 生成 PDF
    # 發送郵件
    pass

[green]3. 清理任務[/green]
# 每天凌晨清理過期數據
@app.function(schedule=modal.Cron("0 2 * * *"))
def cleanup_expired_data():
    # 刪除舊記錄
    # 清理緩存
    # 歸檔日誌
    pass

[green]4. 健康檢查[/green]
# 每 5 分鐘檢查服務健康
@app.function(schedule=modal.Period(minutes=5))
def health_check():
    # 檢查服務狀態
    # 發送告警（如異常）
    pass

[green]5. 價格更新[/green]
# 每天更新價格數據
@app.function(schedule=modal.Cron("0 6 * * *"))
def update_prices():
    # 獲取最新價格
    # 更新數據庫
    # 通知訂閱用戶
    pass

[green]6. 備份[/green]
# 每天凌晨 3 點備份數據庫
@app.function(schedule=modal.Cron("0 3 * * *"))
def database_backup():
    # 導出數據
    # 上傳到 S3
    # 驗證備份
    pass
    """)
    console.print("="*60 + "\n")


if __name__ == "__main__":
    print_schedule_guide()
    print_real_world_examples()

    console.print("[yellow]部署定時任務:[/yellow]")
    console.print("  modal deploy 04_定時任務.py\n")

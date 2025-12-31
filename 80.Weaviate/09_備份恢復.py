"""
Weaviate 備份恢復示例

本示例展示：
1. 創建備份
2. 查看備份狀態
3. 恢復備份
4. 備份策略
"""

import weaviate
from weaviate.classes.config import Configure, Property, DataType
from weaviate.backup import BackupStorage
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import time
from datetime import datetime

console = Console()


def connect_client():
    """連接到 Weaviate"""
    try:
        client = weaviate.connect_to_local()
        console.print("[green]✓ 已連接到 Weaviate[/green]\n")
        return client
    except Exception as e:
        console.print(f"[red]✗ 連接失敗: {e}[/red]")
        return None


def setup_test_collection(client):
    """設置測試集合和數據"""
    console.print("[cyan]設置測試集合和數據...[/cyan]")

    try:
        # 創建集合
        if client.collections.exists("Document"):
            client.collections.delete("Document")

        client.collections.create(
            name="Document",
            properties=[
                Property(name="title", data_type=DataType.TEXT),
                Property(name="content", data_type=DataType.TEXT),
                Property(name="category", data_type=DataType.TEXT),
            ],
            vectorizer_config=Configure.Vectorizer.none()
        )

        # 插入測試數據
        documents = client.collections.get("Document")

        test_docs = [
            {"title": "文檔1", "content": "這是第一份重要文檔", "category": "技術"},
            {"title": "文檔2", "content": "這是第二份重要文檔", "category": "業務"},
            {"title": "文檔3", "content": "這是第三份重要文檔", "category": "技術"},
            {"title": "文檔4", "content": "這是第四份重要文檔", "category": "產品"},
            {"title": "文檔5", "content": "這是第五份重要文檔", "category": "業務"},
        ]

        with documents.batch.dynamic() as batch:
            for doc in test_docs:
                batch.add_object(properties=doc)

        console.print(f"[green]✓ 已創建集合並插入 {len(test_docs)} 條數據[/green]\n")

    except Exception as e:
        console.print(f"[red]✗ 設置失敗: {e}[/red]")


def create_backup(client):
    """創建備份"""
    console.print("[bold cyan]1. 創建備份[/bold cyan]")

    try:
        # 生成備份 ID (使用時間戳)
        backup_id = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        console.print(f"[yellow]正在創建備份: {backup_id}[/yellow]")

        # 創建備份
        # 注意: 實際備份需要配置備份後端 (filesystem, s3, gcs, azure)
        result = client.backup.create(
            backup_id=backup_id,
            backend="filesystem",  # 使用文件系統後端
            include_collections=["Document"],  # 指定要備份的集合
            wait_for_completion=True  # 等待備份完成
        )

        console.print(f"[green]✓ 備份創建成功[/green]")
        console.print(f"[dim]備份 ID: {backup_id}[/dim]")
        console.print(f"[dim]狀態: {result.status}[/dim]\n")

        return backup_id

    except Exception as e:
        console.print(f"[red]✗ 創建備份失敗: {e}[/red]")
        console.print("[yellow]提示: 確保 Weaviate 配置了備份後端[/yellow]\n")
        return None


def check_backup_status(client, backup_id):
    """檢查備份狀態"""
    console.print("[bold cyan]2. 檢查備份狀態[/bold cyan]")

    try:
        if not backup_id:
            console.print("[yellow]沒有可用的備份 ID[/yellow]\n")
            return

        console.print(f"[yellow]檢查備份狀態: {backup_id}[/yellow]")

        # 獲取備份狀態
        status = client.backup.get_create_status(
            backup_id=backup_id,
            backend="filesystem"
        )

        table = Table(title="備份狀態")
        table.add_column("項目", style="cyan")
        table.add_column("值", style="green")

        table.add_row("備份 ID", backup_id)
        table.add_row("狀態", status.status)

        if hasattr(status, 'path'):
            table.add_row("路徑", status.path)

        console.print(table)
        console.print()

    except Exception as e:
        console.print(f"[red]✗ 檢查狀態失敗: {e}[/red]\n")


def restore_backup(client, backup_id):
    """恢復備份"""
    console.print("[bold cyan]3. 恢復備份[/bold cyan]")

    try:
        if not backup_id:
            console.print("[yellow]沒有可用的備份 ID[/yellow]\n")
            return

        console.print(f"[yellow]準備恢復備份: {backup_id}[/yellow]")

        # 先刪除現有集合
        console.print("[yellow]刪除現有集合...[/yellow]")
        if client.collections.exists("Document"):
            client.collections.delete("Document")

        # 恢復備份
        console.print("[yellow]正在恢復備份...[/yellow]")

        result = client.backup.restore(
            backup_id=backup_id,
            backend="filesystem",
            include_collections=["Document"],
            wait_for_completion=True
        )

        console.print(f"[green]✓ 備份恢復成功[/green]")
        console.print(f"[dim]狀態: {result.status}[/dim]\n")

        # 驗證恢復的數據
        documents = client.collections.get("Document")
        count_result = documents.aggregate.over_all(total_count=True)

        console.print(f"[green]✓ 恢復了 {count_result.total_count} 條數據[/green]\n")

    except Exception as e:
        console.print(f"[red]✗ 恢復備份失敗: {e}[/red]\n")


def backup_multiple_collections(client):
    """備份多個集合"""
    console.print("[bold cyan]4. 備份多個集合[/bold cyan]")

    try:
        # 創建另一個測試集合
        if not client.collections.exists("Notes"):
            client.collections.create(
                name="Notes",
                properties=[
                    Property(name="text", data_type=DataType.TEXT),
                ],
                vectorizer_config=Configure.Vectorizer.none()
            )

            notes = client.collections.get("Notes")
            notes.data.insert({"text": "測試筆記"})

        backup_id = f"multi_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        console.print(f"[yellow]創建多集合備份: {backup_id}[/yellow]")

        # 備份多個集合
        result = client.backup.create(
            backup_id=backup_id,
            backend="filesystem",
            include_collections=["Document", "Notes"],  # 備份多個集合
            wait_for_completion=True
        )

        console.print(f"[green]✓ 多集合備份創建成功[/green]")
        console.print(f"[dim]包含集合: Document, Notes[/dim]\n")

        return backup_id

    except Exception as e:
        console.print(f"[red]✗ 多集合備份失敗: {e}[/red]\n")
        return None


def backup_configuration_example():
    """備份配置示例"""
    console.print("[bold cyan]5. 備份配置示例[/bold cyan]")

    console.print("[yellow]Docker Compose 配置示例:[/yellow]\n")

    docker_config = """
```yaml
version: '3.4'
services:
  weaviate:
    image: semitechnologies/weaviate:latest
    ports:
      - "8080:8080"
    environment:
      ENABLE_MODULES: 'backup-filesystem'
      BACKUP_FILESYSTEM_PATH: '/var/lib/weaviate/backups'
    volumes:
      - weaviate_data:/var/lib/weaviate
      - weaviate_backups:/var/lib/weaviate/backups

volumes:
  weaviate_data:
  weaviate_backups:
```
"""

    console.print(docker_config)

    console.print("\n[yellow]支持的備份後端:[/yellow]")
    backends = [
        ("filesystem", "本地文件系統,適合測試和小規模部署"),
        ("s3", "AWS S3,適合雲端生產環境"),
        ("gcs", "Google Cloud Storage,適合GCP環境"),
        ("azure", "Azure Blob Storage,適合Azure環境"),
    ]

    table = Table(title="備份後端")
    table.add_column("後端", style="cyan")
    table.add_column("說明", style="green")

    for backend, desc in backends:
        table.add_row(backend, desc)

    console.print(table)
    console.print()


def backup_strategies():
    """備份策略"""
    console.print("[bold cyan]6. 備份策略最佳實踐[/bold cyan]")

    strategies = [
        ("定期備份", "設置自動化的定期備份任務(每天/每週)"),
        ("版本管理", "保留多個備份版本,便於回滾到特定時間點"),
        ("異地備份", "將備份存儲在不同的地理位置或雲端"),
        ("備份驗證", "定期測試備份恢復流程,確保備份有效"),
        ("增量備份", "如果數據量大,考慮增量備份策略"),
        ("備份加密", "對敏感數據的備份進行加密"),
        ("保留策略", "定義備份保留時間,自動清理舊備份"),
        ("文檔記錄", "記錄備份時間、內容和恢復步驟"),
        ("監控告警", "監控備份任務,失敗時發送告警"),
        ("災難演練", "定期進行災難恢復演練"),
    ]

    table = Table(title="備份策略最佳實踐")
    table.add_column("策略", style="cyan", width=15)
    table.add_column("說明", style="green", width=45)

    for strategy, desc in strategies:
        table.add_row(strategy, desc)

    console.print(table)
    console.print()


def automated_backup_script():
    """自動化備份腳本示例"""
    console.print("[bold cyan]7. 自動化備份腳本示例[/bold cyan]")

    script = """
```python
#!/usr/bin/env python3
# 自動備份腳本 (可配合 cron 使用)

import weaviate
from datetime import datetime
import logging

# 配置日誌
logging.basicConfig(
    filename='/var/log/weaviate_backup.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def automated_backup():
    try:
        client = weaviate.connect_to_local()

        # 生成備份 ID
        backup_id = f"auto_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 創建備份
        result = client.backup.create(
            backup_id=backup_id,
            backend="s3",  # 使用 S3 後端
            include_collections=["Document", "Notes"],
            wait_for_completion=True
        )

        logging.info(f"備份成功: {backup_id}, 狀態: {result.status}")

        # 清理超過30天的舊備份
        cleanup_old_backups(client, days=30)

        client.close()

    except Exception as e:
        logging.error(f"備份失敗: {e}")
        # 發送告警郵件/通知
        send_alert(f"備份失敗: {e}")

if __name__ == "__main__":
    automated_backup()
```

Crontab 配置 (每天凌晨2點執行):
```bash
0 2 * * * /usr/bin/python3 /path/to/backup_script.py
```
"""

    console.print(script)


def disaster_recovery_plan():
    """災難恢復計劃"""
    console.print("[bold cyan]8. 災難恢復計劃[/bold cyan]")

    plan = [
        ("第1步", "識別災難", "檢測到數據丟失或損壞"),
        ("第2步", "評估影響", "確定受影響的集合和數據範圍"),
        ("第3步", "選擇備份", "選擇最近的有效備份點"),
        ("第4步", "停止服務", "暫停服務以防止數據不一致"),
        ("第5步", "恢復數據", "執行備份恢復操作"),
        ("第6步", "驗證數據", "檢查恢復的數據完整性"),
        ("第7步", "測試功能", "測試所有關鍵功能"),
        ("第8步", "恢復服務", "重新啟動服務"),
        ("第9步", "監控系統", "密切監控系統穩定性"),
        ("第10步", "事後分析", "分析原因並改進流程"),
    ]

    table = Table(title="災難恢復流程")
    table.add_column("步驟", style="cyan", width=10)
    table.add_column("階段", style="yellow", width=12)
    table.add_column("說明", style="green", width=35)

    for step, stage, desc in plan:
        table.add_row(step, stage, desc)

    console.print(table)


def cleanup(client):
    """清理資源"""
    try:
        console.print("\n[cyan]清理資源...[/cyan]")
        for collection in ["Document", "Notes"]:
            if client.collections.exists(collection):
                client.collections.delete(collection)
                console.print(f"[dim]✓ 已刪除 {collection} 集合[/dim]")
        client.close()
    except Exception as e:
        console.print(f"[red]清理失敗: {e}[/red]")


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Weaviate 備份恢復示例[/bold cyan]",
        border_style="cyan"
    ))

    client = connect_client()
    if not client:
        return

    backup_id = None

    try:
        # 設置測試集合
        setup_test_collection(client)

        # 1. 創建備份
        backup_id = create_backup(client)

        # 2. 檢查備份狀態
        check_backup_status(client, backup_id)

        # 3. 恢復備份
        restore_backup(client, backup_id)

        # 4. 多集合備份
        multi_backup_id = backup_multiple_collections(client)

        # 5. 備份配置
        backup_configuration_example()

        # 6. 備份策略
        backup_strategies()

        # 7. 自動化腳本
        automated_backup_script()

        # 8. 災難恢復計劃
        disaster_recovery_plan()

        console.print("\n" + "="*60)
        console.print("[bold green]✓ 備份恢復示例完成！[/bold green]")
        console.print("\n[yellow]注意:[/yellow]")
        console.print("  • 備份功能需要在 Weaviate 配置中啟用")
        console.print("  • 生產環境建議使用雲端備份後端 (S3/GCS/Azure)")
        console.print("  • 定期測試備份恢復流程")

    except Exception as e:
        console.print(f"[red]錯誤: {e}[/red]")
    finally:
        cleanup(client)


if __name__ == "__main__":
    main()

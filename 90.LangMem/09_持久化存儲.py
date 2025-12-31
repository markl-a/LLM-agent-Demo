"""
LangMem 持久化存儲示例

本示例展示:
1. Redis存儲整合
2. PostgreSQL存儲
3. 文件系統存儲
4. 存儲性能優化
"""

from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import RedisChatMessageHistory
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from datetime import datetime
from dotenv import load_dotenv
import os
import json
import time

console = Console()
load_dotenv()


def demonstrate_redis_storage():
    """演示Redis存儲"""
    try:
        console.print("\n[cyan]1. Redis存儲[/cyan]")
        console.print("[dim]高性能內存數據庫存儲[/dim]\n")

        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

        try:
            # 創建Redis記憶
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            console.print("[yellow]連接到Redis...[/yellow]")
            redis_history = RedisChatMessageHistory(
                session_id=session_id,
                url=redis_url,
                ttl=3600  # 1小時過期
            )

            memory = ConversationBufferMemory(
                chat_memory=redis_history,
                return_messages=True
            )

            # 添加測試數據
            console.print("[yellow]添加測試數據...[/yellow]")
            test_conversations = [
                ("用戶偏好設置完成", "好的,已保存您的偏好設置"),
                ("開始新任務", "任務已創建,ID: TASK-001"),
                ("查看進度", "當前任務進度: 50%"),
            ]

            for user_msg, ai_msg in test_conversations:
                memory.save_context({"input": user_msg}, {"output": ai_msg})

            # 顯示存儲信息
            table = Table(title="Redis存儲信息")
            table.add_column("屬性", style="cyan")
            table.add_column("值", style="green")

            table.add_row("Session ID", session_id)
            table.add_row("Redis URL", redis_url)
            table.add_row("TTL", "3600秒 (1小時)")
            table.add_row("對話數", str(len(test_conversations)))

            console.print(table)
            console.print()

            console.print("[green]✓ Redis存儲成功[/green]")
            console.print("[dim]優點: 高性能、支持TTL、持久化[/dim]\n")

            return memory

        except Exception as e:
            console.print(f"[yellow]⚠ Redis連接失敗: {e}[/yellow]")
            console.print("[dim]請確保Redis正在運行: docker run -d -p 6379:6379 redis[/dim]\n")
            return None

    except Exception as e:
        console.print(f"[red]✗ 演示失敗: {e}[/red]")
        return None


def demonstrate_file_storage():
    """演示文件存儲"""
    try:
        console.print("[cyan]2. 文件系統存儲[/cyan]")
        console.print("[dim]使用JSON文件持久化[/dim]\n")

        storage_dir = "persistent_memory"
        os.makedirs(storage_dir, exist_ok=True)

        # 創建記憶數據
        memory_data = {
            "session_id": f"file_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "created_at": datetime.now().isoformat(),
            "conversations": [
                {
                    "timestamp": datetime.now().isoformat(),
                    "user": "開始使用系統",
                    "assistant": "歡迎使用!",
                    "metadata": {"importance": 5}
                },
                {
                    "timestamp": datetime.now().isoformat(),
                    "user": "我需要幫助",
                    "assistant": "我可以幫您什麼?",
                    "metadata": {"importance": 7}
                }
            ],
            "metadata": {
                "total_messages": 4,
                "last_updated": datetime.now().isoformat()
            }
        }

        # 保存到文件
        file_path = os.path.join(storage_dir, f"{memory_data['session_id']}.json")

        console.print("[yellow]保存記憶到文件...[/yellow]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("寫入中...", total=None)

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(memory_data, f, ensure_ascii=False, indent=2)

            progress.update(task, completed=True)

        # 驗證文件
        file_size = os.path.getsize(file_path)

        table = Table(title="文件存儲信息")
        table.add_column("屬性", style="cyan")
        table.add_column("值", style="green")

        table.add_row("文件路徑", file_path)
        table.add_row("文件大小", f"{file_size} bytes")
        table.add_row("格式", "JSON")
        table.add_row("對話數", str(len(memory_data["conversations"])))

        console.print(table)
        console.print()

        # 測試讀取
        console.print("[yellow]測試讀取...[/yellow]")
        with open(file_path, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)

        console.print("[green]✓ 文件存儲和讀取成功[/green]")
        console.print("[dim]優點: 簡單、無依賴、易於調試[/dim]\n")

        return memory_data

    except Exception as e:
        console.print(f"[red]✗ 演示失敗: {e}[/red]")
        return None


def demonstrate_database_storage():
    """演示數據庫存儲"""
    try:
        console.print("[cyan]3. 數據庫存儲 (模擬)[/cyan]")
        console.print("[dim]使用關係型數據庫持久化[/dim]\n")

        # 模擬數據庫Schema
        console.print("[yellow]數據庫Schema設計:[/yellow]\n")

        schema = """
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_message TEXT,
    assistant_message TEXT,
    metadata JSONB
);

CREATE TABLE memory_metadata (
    session_id VARCHAR(255) PRIMARY KEY,
    created_at TIMESTAMP,
    last_updated TIMESTAMP,
    message_count INTEGER,
    tags TEXT[]
);

CREATE INDEX idx_session_id ON conversations(session_id);
CREATE INDEX idx_timestamp ON conversations(timestamp);
        """

        console.print(Panel(
            schema,
            border_style="green",
            title="PostgreSQL Schema"
        ))
        console.print()

        # 模擬插入操作
        console.print("[yellow]模擬數據操作:[/yellow]")

        operations = [
            "INSERT INTO conversations ...",
            "UPDATE memory_metadata ...",
            "SELECT * FROM conversations WHERE session_id = ...",
            "DELETE FROM conversations WHERE timestamp < ..."
        ]

        table = Table(title="數據庫操作")
        table.add_column("操作", style="cyan")
        table.add_column("描述", style="green")

        operation_desc = [
            "插入新對話",
            "更新元數據",
            "查詢會話歷史",
            "清理過期數據"
        ]

        for op, desc in zip(operations, operation_desc):
            table.add_row(op[:40] + "...", desc)

        console.print(table)
        console.print()

        console.print("[green]✓ 數據庫存儲設計完成[/green]")
        console.print("[dim]優點: 可靠、支持複雜查詢、事務保證[/dim]\n")

        return True

    except Exception as e:
        console.print(f"[red]✗ 演示失敗: {e}[/red]")
        return False


def demonstrate_storage_performance():
    """演示存儲性能"""
    try:
        console.print("[cyan]4. 存儲性能對比[/cyan]")
        console.print("[dim]不同存儲方案的性能比較[/dim]\n")

        # 性能數據 (模擬)
        performance_data = [
            {
                "storage": "Redis",
                "write": "< 1ms",
                "read": "< 1ms",
                "concurrency": "10000+ ops/s",
                "durability": "⚠️ 需配置"
            },
            {
                "storage": "PostgreSQL",
                "write": "5-10ms",
                "read": "5-10ms",
                "concurrency": "1000+ ops/s",
                "durability": "✅ 強"
            },
            {
                "storage": "File (JSON)",
                "write": "10-50ms",
                "read": "10-50ms",
                "concurrency": "100+ ops/s",
                "durability": "✅ 強"
            },
            {
                "storage": "SQLite",
                "write": "5-20ms",
                "read": "5-20ms",
                "concurrency": "500+ ops/s",
                "durability": "✅ 強"
            }
        ]

        table = Table(title="存儲性能對比")
        table.add_column("存儲方案", style="cyan")
        table.add_column("寫入延遲", style="yellow")
        table.add_column("讀取延遲", style="yellow")
        table.add_column("並發能力", style="green")
        table.add_column("持久性", style="magenta")

        for data in performance_data:
            table.add_row(
                data["storage"],
                data["write"],
                data["read"],
                data["concurrency"],
                data["durability"]
            )

        console.print(table)
        console.print()

        return True

    except Exception as e:
        console.print(f"[red]✗ 演示失敗: {e}[/red]")
        return False


def demonstrate_storage_optimization():
    """演示存儲優化"""
    try:
        console.print("[cyan]5. 存儲優化策略[/cyan]")
        console.print("[dim]提升存儲性能的最佳實踐[/dim]\n")

        optimizations = [
            {
                "策略": "批量寫入",
                "描述": "累積多條記憶後批量寫入",
                "性能提升": "3-5x"
            },
            {
                "策略": "異步寫入",
                "描述": "使用異步I/O不阻塞主流程",
                "性能提升": "顯著"
            },
            {
                "策略": "緩存層",
                "描述": "Redis作為PostgreSQL的緩存",
                "性能提升": "10x+"
            },
            {
                "策略": "數據壓縮",
                "描述": "壓縮歷史對話減少存儲",
                "性能提升": "50-70%空間"
            },
            {
                "策略": "分片存儲",
                "描述": "按時間或用戶分片",
                "性能提升": "線性擴展"
            }
        ]

        table = Table(title="存儲優化策略")
        table.add_column("策略", style="cyan")
        table.add_column("描述", style="green")
        table.add_column("性能提升", style="yellow")

        for opt in optimizations:
            table.add_row(opt["策略"], opt["描述"], opt["性能提升"])

        console.print(table)
        console.print()

        # 最佳實踐
        console.print("[yellow]最佳實踐建議:[/yellow]")
        console.print("  1. 開發環境: 使用文件存儲,簡單方便")
        console.print("  2. 測試環境: 使用SQLite,輕量級數據庫")
        console.print("  3. 生產環境: Redis + PostgreSQL組合")
        console.print("  4. 高並發: 優先使用Redis")
        console.print("  5. 數據分析: 使用PostgreSQL便於查詢\n")

        return True

    except Exception as e:
        console.print(f"[red]✗ 演示失敗: {e}[/red]")
        return False


def compare_storage_backends():
    """比較存儲後端"""
    try:
        console.print("[cyan]6. 存儲後端選擇指南[/cyan]\n")

        table = Table(title="存儲後端選擇")
        table.add_column("場景", style="cyan")
        table.add_column("推薦方案", style="green")
        table.add_column("原因", style="yellow")

        table.add_row(
            "個人項目/Demo",
            "File (JSON)",
            "簡單、無需配置"
        )
        table.add_row(
            "小型應用",
            "SQLite",
            "單文件、零配置"
        )
        table.add_row(
            "中型應用",
            "Redis",
            "高性能、易擴展"
        )
        table.add_row(
            "企業應用",
            "Redis + PostgreSQL",
            "性能 + 可靠性"
        )
        table.add_row(
            "海量數據",
            "分佈式數據庫",
            "可擴展性"
        )

        console.print(table)
        console.print()

    except Exception as e:
        console.print(f"[red]✗ 比較失敗: {e}[/red]")


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]LangMem 持久化存儲示例[/bold cyan]\n"
        "[dim]展示不同的持久化存儲方案[/dim]",
        border_style="cyan"
    ))

    # 演示各種存儲方案
    demonstrate_redis_storage()
    demonstrate_file_storage()
    demonstrate_database_storage()

    # 性能和優化
    demonstrate_storage_performance()
    demonstrate_storage_optimization()

    # 選擇指南
    compare_storage_backends()

    # 完成
    console.print("="*60)
    console.print("[bold green]✓ 持久化存儲示例完成！[/bold green]")
    console.print("\n[cyan]關鍵要點:[/cyan]")
    console.print("  • Redis: 高性能內存存儲")
    console.print("  • PostgreSQL: 可靠的關係型數據庫")
    console.print("  • File: 簡單的文件系統存儲")
    console.print("  • 組合方案: 發揮各自優勢")


if __name__ == "__main__":
    main()

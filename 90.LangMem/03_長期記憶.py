"""
LangMem 長期記憶示例

本示例展示:
1. 持久化記憶存儲
2. Redis 記憶後端
3. 文件記憶後端
4. 記憶的跨會話使用
"""

from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import (
    FileChatMessageHistory,
    RedisChatMessageHistory
)
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from dotenv import load_dotenv
import os
import json
from datetime import datetime

console = Console()
load_dotenv()


def demonstrate_file_memory():
    """演示文件記憶"""
    try:
        console.print("\n[cyan]1. 文件記憶 (File Memory)[/cyan]")
        console.print("[dim]使用 JSON 文件持久化記憶[/dim]\n")

        # 定義文件路徑
        history_file = "memory_history.json"

        # 創建文件記憶歷史
        file_history = FileChatMessageHistory(history_file)

        # 創建記憶
        memory = ConversationBufferMemory(
            chat_memory=file_history,
            return_messages=True
        )

        # 添加對話
        console.print("[yellow]添加對話到記憶...[/yellow]")
        memory.save_context(
            {"input": "我叫張三,住在台北"},
            {"output": "你好張三!很高興認識台北的朋友。"}
        )
        memory.save_context(
            {"input": "我是一名軟體工程師"},
            {"output": "很棒!軟體工程是個很有前景的職業。"}
        )

        # 顯示記憶
        memory_vars = memory.load_memory_variables({})
        history = memory_vars["history"]

        table = Table(title="文件記憶內容")
        table.add_column("角色", style="cyan")
        table.add_column("內容", style="green")

        for msg in history:
            role = "👤 用戶" if msg.type == "human" else "🤖 AI"
            table.add_row(role, msg.content)

        console.print(table)
        console.print(f"[green]✓ 記憶已保存到: {history_file}[/green]\n")

        # 演示跨會話加載
        console.print("[yellow]模擬新會話,加載記憶...[/yellow]")
        new_file_history = FileChatMessageHistory(history_file)
        new_memory = ConversationBufferMemory(
            chat_memory=new_file_history,
            return_messages=True
        )

        loaded_vars = new_memory.load_memory_variables({})
        loaded_history = loaded_vars["history"]

        console.print(f"[green]✓ 成功加載 {len(loaded_history)} 條記憶[/green]\n")

        return memory

    except Exception as e:
        console.print(f"[red]✗ 演示失敗: {e}[/red]")
        return None


def demonstrate_redis_memory():
    """演示 Redis 記憶"""
    try:
        console.print("[cyan]2. Redis 記憶 (Redis Memory)[/cyan]")
        console.print("[dim]使用 Redis 持久化記憶[/dim]\n")

        # 檢查 Redis 連接配置
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

        try:
            # 創建 Redis 記憶歷史
            session_id = f"user_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            redis_history = RedisChatMessageHistory(
                session_id=session_id,
                url=redis_url
            )

            # 創建記憶
            memory = ConversationBufferMemory(
                chat_memory=redis_history,
                return_messages=True
            )

            # 添加對話
            console.print("[yellow]添加對話到 Redis...[/yellow]")
            memory.save_context(
                {"input": "我最喜歡的程式語言是 Python"},
                {"output": "Python 是一個很棒的選擇!它簡潔且功能強大。"}
            )
            memory.save_context(
                {"input": "我正在學習機器學習"},
                {"output": "機器學習是個很有趣的領域!有什麼特別感興趣的主題嗎?"}
            )

            # 顯示記憶
            memory_vars = memory.load_memory_variables({})
            history = memory_vars["history"]

            table = Table(title=f"Redis 記憶內容 (Session: {session_id})")
            table.add_column("角色", style="cyan")
            table.add_column("內容", style="green")

            for msg in history:
                role = "👤 用戶" if msg.type == "human" else "🤖 AI"
                table.add_row(role, msg.content)

            console.print(table)
            console.print(f"[green]✓ 記憶已保存到 Redis[/green]")
            console.print(f"[dim]Session ID: {session_id}[/dim]\n")

            return memory

        except Exception as e:
            console.print(f"[yellow]⚠ Redis 連接失敗: {e}[/yellow]")
            console.print("[dim]請確保 Redis 正在運行: docker run -d -p 6379:6379 redis[/dim]\n")
            return None

    except Exception as e:
        console.print(f"[red]✗ 演示失敗: {e}[/red]")
        return None


def demonstrate_custom_memory_storage():
    """演示自定義記憶存儲"""
    try:
        console.print("[cyan]3. 自定義記憶存儲[/cyan]")
        console.print("[dim]創建自定義的記憶存儲格式[/dim]\n")

        # 自定義存儲路徑
        storage_dir = "custom_memory_storage"
        os.makedirs(storage_dir, exist_ok=True)

        # 創建記憶
        memory = ConversationBufferMemory(return_messages=True)

        # 添加對話
        conversations = [
            ("我的電子郵件是 zhangsan@example.com", "好的,已記錄您的郵箱。"),
            ("我的電話是 0912-345-678", "已記錄您的聯繫電話。"),
            ("我對 AI 和區塊鏈感興趣", "這兩個都是很前沿的技術領域!"),
        ]

        for user_msg, ai_msg in conversations:
            memory.save_context({"input": user_msg}, {"output": ai_msg})

        # 自定義保存格式
        memory_data = {
            "session_id": "custom_session_001",
            "created_at": datetime.now().isoformat(),
            "conversations": []
        }

        memory_vars = memory.load_memory_variables({})
        for msg in memory_vars["history"]:
            memory_data["conversations"].append({
                "role": msg.type,
                "content": msg.content,
                "timestamp": datetime.now().isoformat()
            })

        # 保存到文件
        file_path = os.path.join(storage_dir, "session_001.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(memory_data, f, ensure_ascii=False, indent=2)

        console.print(f"[green]✓ 自定義記憶已保存[/green]")
        console.print(f"[dim]路徑: {file_path}[/dim]")
        console.print(f"[dim]對話數: {len(memory_data['conversations'])}[/dim]\n")

        # 顯示保存的數據結構
        console.print("[yellow]保存的數據結構:[/yellow]")
        console.print(Panel(
            json.dumps(memory_data, ensure_ascii=False, indent=2)[:500] + "...",
            border_style="green"
        ))
        console.print()

        return memory

    except Exception as e:
        console.print(f"[red]✗ 演示失敗: {e}[/red]")
        return None


def demonstrate_memory_versioning():
    """演示記憶版本控制"""
    try:
        console.print("[cyan]4. 記憶版本控制[/cyan]")
        console.print("[dim]為記憶添加版本管理[/dim]\n")

        versions_dir = "memory_versions"
        os.makedirs(versions_dir, exist_ok=True)

        # 創建多個版本的記憶
        versions = [
            {
                "version": "v1",
                "conversations": [
                    ("你好", "你好!"),
                ]
            },
            {
                "version": "v2",
                "conversations": [
                    ("你好", "你好!"),
                    ("我叫張三", "很高興認識你,張三!"),
                ]
            },
            {
                "version": "v3",
                "conversations": [
                    ("你好", "你好!"),
                    ("我叫張三", "很高興認識你,張三!"),
                    ("我是工程師", "很棒的職業!"),
                ]
            },
        ]

        table = Table(title="記憶版本歷史")
        table.add_column("版本", style="cyan")
        table.add_column("對話數", style="yellow")
        table.add_column("時間戳", style="green")

        for version_data in versions:
            version = version_data["version"]
            timestamp = datetime.now().isoformat()

            # 保存版本
            file_path = os.path.join(versions_dir, f"memory_{version}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "version": version,
                    "timestamp": timestamp,
                    "data": version_data["conversations"]
                }, f, ensure_ascii=False, indent=2)

            table.add_row(
                version,
                str(len(version_data["conversations"])),
                timestamp[:19]
            )

        console.print(table)
        console.print(f"[green]✓ 已創建 {len(versions)} 個記憶版本[/green]\n")

    except Exception as e:
        console.print(f"[red]✗ 演示失敗: {e}[/red]")


def compare_storage_backends():
    """比較存儲後端"""
    try:
        console.print("[cyan]5. 存儲後端比較[/cyan]\n")

        table = Table(title="長期記憶存儲後端比較")
        table.add_column("後端", style="cyan")
        table.add_column("優點", style="green")
        table.add_column("缺點", style="red")
        table.add_column("適用場景", style="yellow")

        table.add_row(
            "File",
            "簡單、無依賴",
            "性能較低、並發問題",
            "開發測試、小規模應用"
        )
        table.add_row(
            "Redis",
            "高性能、支持過期",
            "需要部署 Redis",
            "生產環境、高並發"
        )
        table.add_row(
            "PostgreSQL",
            "可靠、支持查詢",
            "配置複雜",
            "企業應用、數據分析"
        )
        table.add_row(
            "MongoDB",
            "靈活 Schema、擴展性好",
            "需要專門維護",
            "大規模、複雜數據"
        )

        console.print(table)
        console.print()

    except Exception as e:
        console.print(f"[red]✗ 比較失敗: {e}[/red]")


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]LangMem 長期記憶示例[/bold cyan]\n"
        "[dim]展示持久化記憶存儲方案[/dim]",
        border_style="cyan"
    ))

    # 演示各種存儲方式
    demonstrate_file_memory()
    demonstrate_redis_memory()
    demonstrate_custom_memory_storage()
    demonstrate_memory_versioning()

    # 比較存儲後端
    compare_storage_backends()

    # 完成
    console.print("="*60)
    console.print("[bold green]✓ 長期記憶示例完成！[/bold green]")
    console.print("\n[cyan]關鍵要點:[/cyan]")
    console.print("  • 文件存儲: 適合開發和小規模應用")
    console.print("  • Redis: 適合生產環境的高性能存儲")
    console.print("  • 自定義格式: 靈活的數據結構設計")
    console.print("  • 版本控制: 追蹤記憶的變化歷史")


if __name__ == "__main__":
    main()

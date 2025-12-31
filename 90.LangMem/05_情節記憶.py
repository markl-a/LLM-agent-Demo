"""
LangMem 情節記憶示例

本示例展示:
1. 時間序列事件記錄
2. 事件檢索和過濾
3. 情節摘要生成
4. 時間線構建
"""

from langchain.memory import ConversationBufferMemory
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
from datetime import datetime, timedelta
import json
import os

console = Console()


class EpisodicMemory:
    """情節記憶類"""

    def __init__(self, storage_path="episodic_memory.json"):
        self.storage_path = storage_path
        self.episodes = []
        self.load()

    def add_episode(self, event, context=None, importance=5):
        """添加情節"""
        episode = {
            "id": len(self.episodes) + 1,
            "timestamp": datetime.now().isoformat(),
            "event": event,
            "context": context or {},
            "importance": importance
        }
        self.episodes.append(episode)
        self.save()
        return episode

    def get_episodes(self, start_time=None, end_time=None, min_importance=None):
        """檢索情節"""
        filtered = self.episodes

        if start_time:
            filtered = [e for e in filtered if datetime.fromisoformat(e["timestamp"]) >= start_time]

        if end_time:
            filtered = [e for e in filtered if datetime.fromisoformat(e["timestamp"]) <= end_time]

        if min_importance:
            filtered = [e for e in filtered if e["importance"] >= min_importance]

        return filtered

    def save(self):
        """保存到文件"""
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(self.episodes, f, ensure_ascii=False, indent=2)

    def load(self):
        """從文件加載"""
        if os.path.exists(self.storage_path):
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                self.episodes = json.load(f)


def demonstrate_episode_creation():
    """演示情節創建"""
    try:
        console.print("\n[cyan]1. 創建情節記憶[/cyan]")
        console.print("[dim]記錄時間序列事件[/dim]\n")

        memory = EpisodicMemory()

        # 創建不同類型的情節
        episodes_data = [
            {
                "event": "用戶首次登錄系統",
                "context": {"ip": "192.168.1.100", "device": "iPhone"},
                "importance": 8
            },
            {
                "event": "用戶查看產品目錄",
                "context": {"category": "電子產品", "duration": 120},
                "importance": 5
            },
            {
                "event": "用戶添加商品到購物車",
                "context": {"product": "筆記本電腦", "price": 30000},
                "importance": 7
            },
            {
                "event": "用戶完成支付",
                "context": {"amount": 30000, "method": "信用卡"},
                "importance": 9
            },
            {
                "event": "用戶聯繫客服",
                "context": {"topic": "配送時間", "duration": 300},
                "importance": 6
            }
        ]

        # 添加情節
        table = Table(title="創建的情節記憶")
        table.add_column("ID", style="cyan")
        table.add_column("時間", style="yellow")
        table.add_column("事件", style="green")
        table.add_column("重要性", style="magenta")

        for ep_data in episodes_data:
            episode = memory.add_episode(**ep_data)
            table.add_row(
                str(episode["id"]),
                episode["timestamp"][11:19],
                episode["event"],
                "⭐" * episode["importance"]
            )

        console.print(table)
        console.print(f"\n[green]✓ 成功創建 {len(episodes_data)} 個情節[/green]\n")

        return memory

    except Exception as e:
        console.print(f"[red]✗ 創建失敗: {e}[/red]")
        return None


def demonstrate_episode_retrieval(memory):
    """演示情節檢索"""
    try:
        console.print("[cyan]2. 情節檢索[/cyan]")
        console.print("[dim]按條件過濾情節[/dim]\n")

        # 檢索所有情節
        console.print("[yellow]所有情節:[/yellow]")
        all_episodes = memory.get_episodes()
        console.print(f"  總數: {len(all_episodes)} 個情節\n")

        # 按重要性過濾
        console.print("[yellow]高重要性情節 (≥7):[/yellow]")
        important_episodes = memory.get_episodes(min_importance=7)

        table = Table()
        table.add_column("ID", style="cyan")
        table.add_column("事件", style="green")
        table.add_column("重要性", style="magenta")

        for ep in important_episodes:
            table.add_row(
                str(ep["id"]),
                ep["event"],
                str(ep["importance"])
            )

        console.print(table)
        console.print()

        # 按時間範圍過濾
        console.print("[yellow]最近的情節:[/yellow]")
        recent_time = datetime.now() - timedelta(hours=1)
        recent_episodes = memory.get_episodes(start_time=recent_time)
        console.print(f"  過去 1 小時: {len(recent_episodes)} 個情節\n")

        return True

    except Exception as e:
        console.print(f"[red]✗ 檢索失敗: {e}[/red]")
        return False


def demonstrate_timeline_construction(memory):
    """演示時間線構建"""
    try:
        console.print("[cyan]3. 構建時間線[/cyan]")
        console.print("[dim]可視化事件時間序列[/dim]\n")

        episodes = memory.get_episodes()

        # 創建時間線樹
        tree = Tree("📅 [bold cyan]用戶活動時間線[/bold cyan]")

        for ep in episodes:
            timestamp = datetime.fromisoformat(ep["timestamp"])
            time_str = timestamp.strftime("%H:%M:%S")
            importance_stars = "⭐" * ep["importance"]

            branch = tree.add(
                f"[yellow]{time_str}[/yellow] - {ep['event']} {importance_stars}"
            )

            # 添加上下文信息
            if ep["context"]:
                for key, value in ep["context"].items():
                    branch.add(f"[dim]{key}: {value}[/dim]")

        console.print(tree)
        console.print()

        return True

    except Exception as e:
        console.print(f"[red]✗ 構建失敗: {e}[/red]")
        return False


def demonstrate_episode_summary(memory):
    """演示情節摘要"""
    try:
        console.print("[cyan]4. 情節摘要[/cyan]")
        console.print("[dim]生成事件摘要報告[/dim]\n")

        episodes = memory.get_episodes()

        # 統計信息
        total_episodes = len(episodes)
        avg_importance = sum(ep["importance"] for ep in episodes) / total_episodes if total_episodes > 0 else 0
        high_importance = len([ep for ep in episodes if ep["importance"] >= 7])

        # 創建摘要表格
        table = Table(title="情節摘要報告")
        table.add_column("統計項", style="cyan")
        table.add_column("值", style="green")

        table.add_row("總情節數", str(total_episodes))
        table.add_row("平均重要性", f"{avg_importance:.1f}")
        table.add_row("高重要性事件", str(high_importance))
        table.add_row("時間跨度", "今天")

        console.print(table)
        console.print()

        # 事件類型分布
        console.print("[yellow]關鍵事件:[/yellow]")
        important_events = memory.get_episodes(min_importance=8)
        for ep in important_events:
            console.print(f"  • {ep['event']} (重要性: {ep['importance']})")

        console.print()

        return True

    except Exception as e:
        console.print(f"[red]✗ 摘要失敗: {e}[/red]")
        return False


def demonstrate_episode_analysis(memory):
    """演示情節分析"""
    try:
        console.print("[cyan]5. 情節分析[/cyan]")
        console.print("[dim]分析事件模式和趨勢[/dim]\n")

        episodes = memory.get_episodes()

        # 分析事件頻率
        event_keywords = {}
        for ep in episodes:
            words = ep["event"].split()
            for word in words:
                if len(word) > 2:  # 只統計較長的詞
                    event_keywords[word] = event_keywords.get(word, 0) + 1

        # 顯示高頻詞
        console.print("[yellow]高頻關鍵詞:[/yellow]")
        sorted_keywords = sorted(event_keywords.items(), key=lambda x: x[1], reverse=True)[:5]

        table = Table()
        table.add_column("關鍵詞", style="cyan")
        table.add_column("出現次數", style="yellow")

        for keyword, count in sorted_keywords:
            table.add_row(keyword, str(count))

        console.print(table)
        console.print()

        # 分析用戶行為模式
        console.print("[yellow]行為模式分析:[/yellow]")
        console.print("  📊 用戶經歷了完整的購買流程")
        console.print("  📊 從瀏覽到購買的轉化率: 100%")
        console.print("  📊 購買後有售後諮詢行為")
        console.print()

        return True

    except Exception as e:
        console.print(f"[red]✗ 分析失敗: {e}[/red]")
        return False


def compare_episodic_memory():
    """比較情節記憶特點"""
    try:
        console.print("[cyan]6. 情節記憶特點[/cyan]\n")

        table = Table(title="情節記憶 vs 其他記憶類型")
        table.add_column("特性", style="cyan")
        table.add_column("情節記憶", style="green")
        table.add_column("語義記憶", style="yellow")

        table.add_row(
            "時間性",
            "✅ 強時間序列",
            "❌ 無時間概念"
        )
        table.add_row(
            "上下文",
            "✅ 豐富上下文",
            "⚠️ 僅內容本身"
        )
        table.add_row(
            "檢索方式",
            "時間、重要性",
            "語義相似度"
        )
        table.add_row(
            "適用場景",
            "用戶行為追蹤",
            "知識檢索"
        )

        console.print(table)
        console.print()

    except Exception as e:
        console.print(f"[red]✗ 比較失敗: {e}[/red]")


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]LangMem 情節記憶示例[/bold cyan]\n"
        "[dim]展示時間序列事件記錄和分析[/dim]",
        border_style="cyan"
    ))

    # 創建情節
    memory = demonstrate_episode_creation()
    if not memory:
        return

    # 檢索情節
    demonstrate_episode_retrieval(memory)

    # 構建時間線
    demonstrate_timeline_construction(memory)

    # 生成摘要
    demonstrate_episode_summary(memory)

    # 分析情節
    demonstrate_episode_analysis(memory)

    # 比較記憶類型
    compare_episodic_memory()

    # 完成
    console.print("="*60)
    console.print("[bold green]✓ 情節記憶示例完成！[/bold green]")
    console.print("\n[cyan]關鍵要點:[/cyan]")
    console.print("  • 時間序列: 記錄事件的發生順序")
    console.print("  • 上下文: 保存事件的完整上下文")
    console.print("  • 重要性: 評估事件的重要程度")
    console.print("  • 分析: 發現行為模式和趨勢")


if __name__ == "__main__":
    main()

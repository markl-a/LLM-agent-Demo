"""
LangMem 多Agent記憶示例

本示例展示:
1. 獨立Agent記憶
2. 共享記憶空間
3. 記憶同步機制
4. Agent間知識傳遞
"""

from langchain.memory import ConversationBufferMemory
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
from datetime import datetime
import json
import os

console = Console()


class AgentMemoryManager:
    """多Agent記憶管理器"""

    def __init__(self, storage_dir="agent_memories"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        self.agents = {}
        self.shared_memory = []

    def create_agent(self, agent_id, agent_type="assistant"):
        """創建Agent"""
        agent = {
            "id": agent_id,
            "type": agent_type,
            "created_at": datetime.now().isoformat(),
            "private_memory": [],
            "access_level": "standard"
        }
        self.agents[agent_id] = agent
        self._save_agent(agent_id)
        return agent

    def add_private_memory(self, agent_id, memory):
        """添加私有記憶"""
        if agent_id in self.agents:
            self.agents[agent_id]["private_memory"].append({
                "timestamp": datetime.now().isoformat(),
                "content": memory
            })
            self._save_agent(agent_id)

    def add_shared_memory(self, memory, author_id):
        """添加共享記憶"""
        self.shared_memory.append({
            "timestamp": datetime.now().isoformat(),
            "content": memory,
            "author": author_id
        })
        self._save_shared()

    def get_agent_memory(self, agent_id, include_shared=True):
        """獲取Agent記憶"""
        memories = []

        if agent_id in self.agents:
            memories.extend(self.agents[agent_id]["private_memory"])

        if include_shared:
            memories.extend(self.shared_memory)

        return sorted(memories, key=lambda x: x["timestamp"])

    def _save_agent(self, agent_id):
        """保存Agent數據"""
        file_path = os.path.join(self.storage_dir, f"{agent_id}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.agents[agent_id], f, ensure_ascii=False, indent=2)

    def _save_shared(self):
        """保存共享記憶"""
        file_path = os.path.join(self.storage_dir, "shared_memory.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.shared_memory, f, ensure_ascii=False, indent=2)


def demonstrate_independent_memories():
    """演示獨立記憶"""
    try:
        console.print("\n[cyan]1. 獨立Agent記憶[/cyan]")
        console.print("[dim]每個Agent擁有獨立的記憶空間[/dim]\n")

        manager = AgentMemoryManager()

        # 創建多個Agent
        agents = [
            {"id": "customer_service", "type": "客服Agent"},
            {"id": "sales", "type": "銷售Agent"},
            {"id": "technical_support", "type": "技術支援Agent"}
        ]

        console.print("[yellow]創建Agent...[/yellow]")
        for agent in agents:
            manager.create_agent(agent["id"], agent["type"])
            console.print(f"  ✓ {agent['type']} ({agent['id']})")

        console.print()

        # 為每個Agent添加私有記憶
        console.print("[yellow]添加私有記憶...[/yellow]")

        manager.add_private_memory("customer_service", "處理了客戶關於退貨的諮詢")
        manager.add_private_memory("customer_service", "客戶滿意度評分: 5/5")

        manager.add_private_memory("sales", "完成了一筆 50000 元的訂單")
        manager.add_private_memory("sales", "客戶對產品非常滿意")

        manager.add_private_memory("technical_support", "解決了數據庫連接問題")
        manager.add_private_memory("technical_support", "更新了系統文檔")

        # 顯示各Agent記憶
        table = Table(title="Agent私有記憶")
        table.add_column("Agent", style="cyan")
        table.add_column("記憶數", style="yellow")
        table.add_column("最新記憶", style="green")

        for agent_id, agent_data in manager.agents.items():
            memories = agent_data["private_memory"]
            latest = memories[-1]["content"] if memories else "無"
            table.add_row(
                agent_id,
                str(len(memories)),
                latest[:50] + "..." if len(latest) > 50 else latest
            )

        console.print(table)
        console.print()

        return manager

    except Exception as e:
        console.print(f"[red]✗ 演示失敗: {e}[/red]")
        return None


def demonstrate_shared_memory(manager):
    """演示共享記憶"""
    try:
        console.print("[cyan]2. 共享記憶空間[/cyan]")
        console.print("[dim]Agent間共享知識和經驗[/dim]\n")

        # 添加共享記憶
        console.print("[yellow]添加共享記憶...[/yellow]")

        shared_items = [
            ("customer_service", "客戶反映產品 A 的使用手冊不夠清晰"),
            ("technical_support", "產品 A 的常見問題已整理成文檔"),
            ("sales", "產品 A 本月銷量增長 30%"),
        ]

        for author_id, content in shared_items:
            manager.add_shared_memory(content, author_id)
            console.print(f"  ✓ [{author_id}] {content}")

        console.print()

        # 顯示共享記憶
        table = Table(title="共享記憶庫")
        table.add_column("時間", style="cyan")
        table.add_column("作者", style="yellow")
        table.add_column("內容", style="green")

        for mem in manager.shared_memory:
            timestamp = mem["timestamp"][11:19]
            table.add_row(
                timestamp,
                mem["author"],
                mem["content"]
            )

        console.print(table)
        console.print()

        return True

    except Exception as e:
        console.print(f"[red]✗ 演示失敗: {e}[/red]")
        return False


def demonstrate_memory_access(manager):
    """演示記憶訪問"""
    try:
        console.print("[cyan]3. Agent記憶訪問[/cyan]")
        console.print("[dim]查看Agent可訪問的所有記憶[/dim]\n")

        # 選擇一個Agent查看其記憶
        agent_id = "customer_service"

        console.print(f"[yellow]Agent: {agent_id} 的完整記憶:[/yellow]\n")

        # 獲取包含共享記憶的完整記憶
        all_memories = manager.get_agent_memory(agent_id, include_shared=True)

        tree = Tree(f"🧠 [bold cyan]{agent_id} 的記憶視圖[/bold cyan]")

        # 私有記憶分支
        private_branch = tree.add("🔒 [yellow]私有記憶[/yellow]")
        private_memories = manager.agents[agent_id]["private_memory"]
        for mem in private_memories:
            private_branch.add(f"[green]{mem['content']}[/green]")

        # 共享記憶分支
        shared_branch = tree.add("🌐 [yellow]共享記憶[/yellow]")
        for mem in manager.shared_memory:
            author = mem["author"]
            content = mem["content"]
            shared_branch.add(f"[dim][{author}][/dim] [green]{content}[/green]")

        console.print(tree)
        console.print()

        # 統計
        console.print(f"[green]✓ 總記憶數: {len(all_memories)}[/green]")
        console.print(f"[dim]私有: {len(private_memories)} | 共享: {len(manager.shared_memory)}[/dim]\n")

        return True

    except Exception as e:
        console.print(f"[red]✗ 演示失敗: {e}[/red]")
        return False


def demonstrate_memory_sync():
    """演示記憶同步"""
    try:
        console.print("[cyan]4. 記憶同步機制[/cyan]")
        console.print("[dim]多Agent環境下的記憶同步[/dim]\n")

        # 模擬分佈式環境
        console.print("[yellow]同步場景:[/yellow]\n")

        sync_steps = [
            "1. Agent A 學習到新知識",
            "2. 知識寫入共享記憶庫",
            "3. 觸發同步事件",
            "4. Agent B, C 接收同步通知",
            "5. Agents 拉取最新共享記憶",
            "6. 本地緩存更新"
        ]

        for step in sync_steps:
            console.print(f"  {step}")

        console.print()

        # 同步策略
        table = Table(title="記憶同步策略")
        table.add_column("策略", style="cyan")
        table.add_column("描述", style="green")
        table.add_column("適用場景", style="yellow")

        table.add_row(
            "實時同步",
            "立即廣播新記憶",
            "高一致性需求"
        )
        table.add_row(
            "定時同步",
            "按固定間隔同步",
            "降低網絡開銷"
        )
        table.add_row(
            "事件觸發",
            "特定事件時同步",
            "重要信息傳遞"
        )
        table.add_row(
            "按需拉取",
            "Agent主動請求",
            "分佈式環境"
        )

        console.print(table)
        console.print()

        return True

    except Exception as e:
        console.print(f"[red]✗ 演示失敗: {e}[/red]")
        return False


def demonstrate_knowledge_transfer():
    """演示知識傳遞"""
    try:
        console.print("[cyan]5. Agent間知識傳遞[/cyan]")
        console.print("[dim]不同Agent之間的專業知識共享[/dim]\n")

        # 知識傳遞場景
        scenarios = [
            {
                "from": "技術支援Agent",
                "to": "客服Agent",
                "knowledge": "產品 A 的常見技術問題解決方案",
                "benefit": "客服可以直接解答技術問題"
            },
            {
                "from": "銷售Agent",
                "to": "產品Agent",
                "knowledge": "客戶對產品功能的反饋",
                "benefit": "產品改進有數據支撐"
            },
            {
                "from": "客服Agent",
                "to": "營銷Agent",
                "knowledge": "用戶常見痛點和需求",
                "benefit": "營銷策略更精準"
            }
        ]

        table = Table(title="知識傳遞案例")
        table.add_column("來源", style="cyan")
        table.add_column("目標", style="yellow")
        table.add_column("知識", style="green")
        table.add_column("價值", style="magenta")

        for scenario in scenarios:
            table.add_row(
                scenario["from"],
                scenario["to"],
                scenario["knowledge"],
                scenario["benefit"]
            )

        console.print(table)
        console.print()

        # 知識傳遞效果
        console.print("[yellow]知識傳遞效果:[/yellow]")
        console.print("  📈 整體服務質量提升")
        console.print("  🔄 減少重複學習成本")
        console.print("  🤝 增強團隊協作")
        console.print("  💡 促進創新和改進\n")

        return True

    except Exception as e:
        console.print(f"[red]✗ 演示失敗: {e}[/red]")
        return False


def compare_memory_models():
    """比較記憶模型"""
    try:
        console.print("[cyan]6. 多Agent記憶模型比較[/cyan]\n")

        table = Table(title="記憶模型比較")
        table.add_column("模型", style="cyan")
        table.add_column("優點", style="green")
        table.add_column("缺點", style="red")

        table.add_row(
            "完全獨立",
            "隱私性好、無衝突",
            "無法共享知識"
        )
        table.add_row(
            "完全共享",
            "知識充分共享",
            "隱私問題、混亂"
        )
        table.add_row(
            "混合模式",
            "平衡隱私和共享",
            "管理複雜"
        )
        table.add_row(
            "層次化",
            "靈活控制訪問",
            "實現複雜"
        )

        console.print(table)
        console.print()

    except Exception as e:
        console.print(f"[red]✗ 比較失敗: {e}[/red]")


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]LangMem 多Agent記憶示例[/bold cyan]\n"
        "[dim]展示多Agent環境下的記憶管理[/dim]",
        border_style="cyan"
    ))

    # 演示獨立記憶
    manager = demonstrate_independent_memories()
    if not manager:
        return

    # 演示共享記憶
    demonstrate_shared_memory(manager)

    # 演示記憶訪問
    demonstrate_memory_access(manager)

    # 演示記憶同步
    demonstrate_memory_sync()

    # 演示知識傳遞
    demonstrate_knowledge_transfer()

    # 比較記憶模型
    compare_memory_models()

    # 完成
    console.print("="*60)
    console.print("[bold green]✓ 多Agent記憶示例完成！[/bold green]")
    console.print("\n[cyan]關鍵要點:[/cyan]")
    console.print("  • 獨立記憶: 保護Agent隱私")
    console.print("  • 共享記憶: 促進知識傳遞")
    console.print("  • 記憶同步: 保持一致性")
    console.print("  • 訪問控制: 靈活管理權限")


if __name__ == "__main__":
    main()

"""
Claude Code SDK 對話管理示例

本示例展示：
1. 對話歷史管理
2. 上下文窗口控制
3. 對話狀態保存和恢復
4. 對話摘要壓縮
"""

import os
import json
from anthropic import Anthropic
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import track
from dotenv import load_dotenv

console = Console()
load_dotenv()


class ConversationManager:
    """對話管理器"""

    def __init__(self, model="claude-3-5-sonnet-20241022", max_tokens=1024):
        self.client = Anthropic()
        self.model = model
        self.max_tokens = max_tokens
        self.messages = []
        self.total_input_tokens = 0
        self.total_output_tokens = 0

    def add_user_message(self, content):
        """添加用戶消息"""
        self.messages.append({
            "role": "user",
            "content": content
        })

    def add_assistant_message(self, content):
        """添加助手消息"""
        self.messages.append({
            "role": "assistant",
            "content": content
        })

    def send_message(self, user_message, system_prompt=None):
        """發送消息並獲取響應"""
        # 添加用戶消息
        self.add_user_message(user_message)

        # 構建請求參數
        params = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": self.messages
        }

        if system_prompt:
            params["system"] = system_prompt

        # 發送請求
        response = self.client.messages.create(**params)

        # 提取響應文本
        assistant_message = response.content[0].text

        # 添加助手響應到歷史
        self.add_assistant_message(assistant_message)

        # 更新 token 統計
        self.total_input_tokens += response.usage.input_tokens
        self.total_output_tokens += response.usage.output_tokens

        return assistant_message, response

    def get_conversation_length(self):
        """獲取對話長度（消息數量）"""
        return len(self.messages)

    def get_token_usage(self):
        """獲取 token 使用情況"""
        return {
            "input_tokens": self.total_input_tokens,
            "output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens
        }

    def clear_history(self):
        """清空對話歷史"""
        self.messages = []
        self.total_input_tokens = 0
        self.total_output_tokens = 0

    def save_conversation(self, filename):
        """保存對話到文件"""
        data = {
            "messages": self.messages,
            "token_usage": self.get_token_usage(),
            "model": self.model
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_conversation(self, filename):
        """從文件加載對話"""
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.messages = data["messages"]
        self.model = data.get("model", self.model)

        # 恢復 token 統計（如果有）
        if "token_usage" in data:
            self.total_input_tokens = data["token_usage"]["input_tokens"]
            self.total_output_tokens = data["token_usage"]["output_tokens"]

    def trim_history(self, max_messages=10):
        """修剪對話歷史，保留最近的消息"""
        if len(self.messages) > max_messages:
            removed_count = len(self.messages) - max_messages
            self.messages = self.messages[-max_messages:]
            return removed_count
        return 0

    def summarize_conversation(self):
        """使用 Claude 總結對話內容"""
        if len(self.messages) < 4:
            return None

        # 創建臨時消息列表用於總結
        summary_messages = [
            {
                "role": "user",
                "content": f"請總結以下對話的要點：\n\n{json.dumps(self.messages, ensure_ascii=False)}"
            }
        ]

        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            messages=summary_messages
        )

        return response.content[0].text


def demo_basic_conversation():
    """基本對話管理示例"""
    console.print("\n[bold cyan]1. 基本對話管理[/bold cyan]\n")

    manager = ConversationManager()

    # 多輪對話
    questions = [
        "什麼是機器學習？",
        "它和深度學習有什麼區別？",
        "可以給我一個實際應用的例子嗎？"
    ]

    for i, question in enumerate(questions, 1):
        console.print(f"[yellow]輪次 {i}：[/yellow]")
        console.print(f"[blue]用戶：[/blue] {question}")

        response, _ = manager.send_message(question)

        console.print(f"[green]Claude：[/green] {response[:150]}...\n")

    # 顯示統計
    usage = manager.get_token_usage()
    table = Table(title="對話統計")
    table.add_column("指標", style="cyan")
    table.add_column("值", style="yellow")

    table.add_row("消息數量", str(manager.get_conversation_length()))
    table.add_row("輸入 Tokens", str(usage["input_tokens"]))
    table.add_row("輸出 Tokens", str(usage["output_tokens"]))
    table.add_row("總 Tokens", str(usage["total_tokens"]))

    console.print(table)
    console.print()

    return manager


def demo_context_management(manager):
    """上下文管理示例"""
    console.print("[bold cyan]2. 上下文窗口管理[/bold cyan]\n")

    console.print(f"[yellow]當前消息數：{manager.get_conversation_length()}[/yellow]")

    # 修剪歷史
    removed = manager.trim_history(max_messages=4)

    if removed > 0:
        console.print(f"[green]✓ 已移除 {removed} 條舊消息[/green]")
        console.print(f"[yellow]剩餘消息數：{manager.get_conversation_length()}[/yellow]\n")


def demo_save_and_load():
    """保存和加載對話示例"""
    console.print("[bold cyan]3. 對話持久化[/bold cyan]\n")

    # 創建新對話
    manager = ConversationManager()

    console.print("[cyan]創建新對話...[/cyan]")
    manager.send_message("你好，我想學習 Python。")
    manager.send_message("從哪裡開始最好？")

    # 保存對話
    filename = "conversation_demo.json"
    manager.save_conversation(filename)
    console.print(f"[green]✓ 對話已保存到 {filename}[/green]\n")

    # 創建新管理器並加載
    console.print("[cyan]加載保存的對話...[/cyan]")
    new_manager = ConversationManager()
    new_manager.load_conversation(filename)

    console.print(f"[green]✓ 對話已加載[/green]")
    console.print(f"[yellow]恢復的消息數：{new_manager.get_conversation_length()}[/yellow]\n")

    # 繼續對話
    console.print("[cyan]繼續之前的對話...[/cyan]")
    response, _ = new_manager.send_message("謝謝！我現在想了解數據類型。")
    console.print(f"[green]Claude：[/green] {response[:150]}...\n")

    # 清理臨時文件
    import os
    if os.path.exists(filename):
        os.remove(filename)


def demo_conversation_summary():
    """對話摘要示例"""
    console.print("[bold cyan]4. 對話摘要[/bold cyan]\n")

    manager = ConversationManager()

    # 進行較長的對話
    dialogue = [
        ("什麼是 RESTful API？", "user"),
        ("RESTful API 是一種...", "assistant"),
        ("它的主要特點是什麼？", "user"),
        ("主要特點包括...", "assistant"),
        ("可以給我一個例子嗎？", "user"),
    ]

    console.print("[cyan]模擬長對話...[/cyan]")
    for content, role in track(dialogue, description="處理對話"):
        if role == "user":
            manager.add_user_message(content)
        else:
            manager.add_assistant_message(content)

    # 生成摘要
    console.print("\n[cyan]生成對話摘要...[/cyan]")
    summary = manager.summarize_conversation()

    if summary:
        console.print(Panel(summary, title="對話摘要", border_style="green"))
        console.print()


def demo_system_prompt_management():
    """系統提示詞管理示例"""
    console.print("[bold cyan]5. 系統提示詞管理[/bold cyan]\n")

    # 定義不同的系統角色
    roles = {
        "專業導師": "你是一位專業的 Python 編程導師，用簡潔專業的方式回答問題。",
        "友好助手": "你是一位友好親切的助手，用輕鬆活潑的語氣回答問題。",
        "技術專家": "你是一位嚴謹的技術專家，提供詳細的技術分析和建議。"
    }

    question = "什麼是裝飾器？"

    for role_name, system_prompt in roles.items():
        console.print(f"\n[yellow]角色：{role_name}[/yellow]")
        manager = ConversationManager()

        response, _ = manager.send_message(question, system_prompt=system_prompt)

        console.print(f"[green]回答：[/green] {response[:100]}...")


def demo_token_tracking():
    """Token 使用追蹤示例"""
    console.print("\n[bold cyan]6. Token 使用追蹤[/bold cyan]\n")

    manager = ConversationManager()

    # 發送不同長度的消息
    test_messages = [
        "Hi",
        "請用一句話解釋什麼是 Python。",
        "請詳細解釋 Python 的面向對象編程特性，包括類、對象、繼承、多態等概念。"
    ]

    table = Table(title="Token 使用分析")
    table.add_column("消息", style="cyan", width=40)
    table.add_column("輸入 Tokens", style="yellow")
    table.add_column("輸出 Tokens", style="green")

    for msg in test_messages:
        before_usage = manager.get_token_usage()
        manager.send_message(msg)
        after_usage = manager.get_token_usage()

        input_delta = after_usage["input_tokens"] - before_usage["input_tokens"]
        output_delta = after_usage["output_tokens"] - before_usage["output_tokens"]

        table.add_row(
            msg[:37] + "..." if len(msg) > 40 else msg,
            str(input_delta),
            str(output_delta)
        )

    console.print(table)
    console.print()


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Claude Code SDK 對話管理[/bold cyan]\n"
        "[dim]學習如何管理複雜的對話流程[/dim]",
        border_style="cyan"
    ))

    # 1. 基本對話管理
    manager = demo_basic_conversation()

    # 2. 上下文管理
    demo_context_management(manager)

    # 3. 保存和加載
    demo_save_and_load()

    # 4. 對話摘要
    demo_conversation_summary()

    # 5. 系統提示詞管理
    demo_system_prompt_management()

    # 6. Token 追蹤
    demo_token_tracking()

    # 完成
    console.print("="*60)
    console.print("[bold green]✓ 對話管理示例完成！[/bold green]")
    console.print("\n[cyan]關鍵要點：[/cyan]")
    console.print("  • 維護對話歷史以支持上下文理解")
    console.print("  • 控制上下文長度避免超出限制")
    console.print("  • 使用持久化保存重要對話")
    console.print("  • 追蹤 Token 使用優化成本")


if __name__ == "__main__":
    main()

"""
Claude Code SDK 多輪對話示例

本示例展示：
1. 複雜多輪對話流程
2. 對話狀態管理
3. 對話分支處理
4. 上下文理解優化
"""

import os
import json
from enum import Enum
from typing import List, Dict, Optional
from anthropic import Anthropic
from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree
from dotenv import load_dotenv

console = Console()
load_dotenv()


class ConversationState(Enum):
    """對話狀態"""
    INITIAL = "initial"
    COLLECTING_INFO = "collecting_info"
    PROCESSING = "processing"
    CONFIRMING = "confirming"
    COMPLETED = "completed"


class StatefulConversation:
    """有狀態的對話管理器"""

    def __init__(self):
        self.client = Anthropic()
        self.messages = []
        self.state = ConversationState.INITIAL
        self.user_data = {}

    def add_message(self, role: str, content: str):
        """添加消息"""
        self.messages.append({
            "role": role,
            "content": content
        })

    def send(self, user_input: str, system_prompt: Optional[str] = None) -> str:
        """發送消息並獲取響應"""
        self.add_message("user", user_input)

        params = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 1024,
            "messages": self.messages
        }

        if system_prompt:
            params["system"] = system_prompt

        response = self.client.messages.create(**params)
        assistant_message = response.content[0].text

        self.add_message("assistant", assistant_message)

        return assistant_message

    def update_state(self, new_state: ConversationState):
        """更新對話狀態"""
        self.state = new_state

    def save_user_data(self, key: str, value: any):
        """保存用戶數據"""
        self.user_data[key] = value


def demo_information_gathering():
    """信息收集對話示例"""
    console.print("\n[bold cyan]1. 信息收集對話[/bold cyan]\n")

    conv = StatefulConversation()

    system_prompt = """你是一個餐廳預訂助手。你需要收集以下信息：
1. 客戶姓名
2. 預訂日期
3. 預訂時間
4. 用餐人數

請一次詢問一個問題，態度友好。當收集完所有信息後，進行確認。"""

    # 開始對話
    response = conv.send("我想預訂餐廳", system_prompt)
    console.print(f"[green]助手：[/green] {response}\n")

    # 模擬用戶回答
    user_inputs = [
        "我叫李明",
        "明天晚上",
        "7點",
        "4個人",
        "對的，沒問題"
    ]

    for user_input in user_inputs:
        console.print(f"[blue]用戶：[/blue] {user_input}")
        response = conv.send(user_input, system_prompt)
        console.print(f"[green]助手：[/green] {response}\n")

        if "確認" in response or "完成" in response:
            break


def demo_contextual_conversation():
    """上下文理解對話示例"""
    console.print("[bold cyan]2. 上下文理解對話[/bold cyan]\n")

    conv = StatefulConversation()

    # 建立上下文
    exchanges = [
        ("我在學習 Python 編程", "建立主題"),
        ("字典和列表有什麼區別？", "具體問題"),
        ("那它們什麼時候用？", "代詞指代"),
        ("給我看個例子", "省略主語"),
        ("很好，那集合呢？", "關聯概念"),
    ]

    for user_input, note in exchanges:
        console.print(f"[blue]用戶：[/blue] {user_input} [dim]({note})[/dim]")
        response = conv.send(user_input)
        console.print(f"[green]助手：[/green] {response[:150]}...\n")


def demo_conversation_branching():
    """對話分支示例"""
    console.print("[bold cyan]3. 對話分支處理[/bold cyan]\n")

    # 主對話分支
    main_conv = StatefulConversation()

    console.print("[yellow]主分支：[/yellow]")
    response1 = main_conv.send("我想了解機器學習")
    console.print(f"[green]助手：[/green] {response1[:100]}...\n")

    # 保存當前狀態
    checkpoint_messages = main_conv.messages.copy()

    # 分支 A：深入監督學習
    console.print("[yellow]分支 A - 監督學習：[/yellow]")
    branch_a = StatefulConversation()
    branch_a.messages = checkpoint_messages.copy()

    response_a = branch_a.send("告訴我更多關於監督學習的內容")
    console.print(f"[green]助手：[/green] {response_a[:100]}...\n")

    # 分支 B：深入無監督學習
    console.print("[yellow]分支 B - 無監督學習：[/yellow]")
    branch_b = StatefulConversation()
    branch_b.messages = checkpoint_messages.copy()

    response_b = branch_b.send("無監督學習是什麼？")
    console.print(f"[green]助手：[/green] {response_b[:100]}...\n")


def demo_task_oriented_conversation():
    """任務導向對話示例"""
    console.print("[bold cyan]4. 任務導向對話[/bold cyan]\n")

    conv = StatefulConversation()

    system_prompt = """你是一個編程助手。用戶想要解決一個編程問題。
你需要：
1. 理解問題
2. 確認需求
3. 提供解決方案
4. 解釋代碼
"""

    # 問題描述
    console.print("[blue]用戶：[/blue] 我需要一個函數來檢查字符串是否是回文")
    response = conv.send("我需要一個函數來檢查字符串是否是回文", system_prompt)
    console.print(f"[green]助手：[/green] {response}\n")

    # 需求確認
    console.print("[blue]用戶：[/blue] 忽略大小寫和空格")
    response = conv.send("忽略大小寫和空格", system_prompt)
    console.print(f"[green]助手：[/green] {response}\n")

    # 測試請求
    console.print("[blue]用戶：[/blue] 可以加幾個測試用例嗎？")
    response = conv.send("可以加幾個測試用例嗎？", system_prompt)
    console.print(f"[green]助手：[/green] {response[:200]}...\n")


def demo_clarification_conversation():
    """澄清式對話示例"""
    console.print("[bold cyan]5. 澄清式對話[/bold cyan]\n")

    conv = StatefulConversation()

    system_prompt = """當用戶的請求不明確時，你應該提出澄清性問題，而不是假設。"""

    # 模糊請求
    exchanges = [
        ("幫我優化這段代碼", "需要澄清：什麼代碼？優化什麼方面？"),
        ("一個排序算法", "需要澄清：數據類型？數據規模？"),
        ("整數數組，大約1000個元素", "信息足夠，可以提供建議"),
    ]

    for user_input, expected_behavior in exchanges:
        console.print(f"[blue]用戶：[/blue] {user_input}")
        console.print(f"[dim]期望行為：{expected_behavior}[/dim]")

        response = conv.send(user_input, system_prompt)
        console.print(f"[green]助手：[/green] {response[:150]}...\n")


def demo_conversation_memory():
    """對話記憶示例"""
    console.print("[bold cyan]6. 對話記憶[/bold cyan]\n")

    conv = StatefulConversation()

    # 建立個人信息
    console.print("[yellow]建立用戶檔案：[/yellow]")
    profile_info = [
        ("我叫小明，是一名數據科學家", "姓名和職業"),
        ("我主要用 Python 和 R", "技能"),
        ("我在上海工作", "地點"),
    ]

    for info, category in profile_info:
        console.print(f"[blue]用戶：[/blue] {info} [dim]({category})[/dim]")
        response = conv.send(info)
        console.print(f"[green]助手：[/green] {response[:100]}...\n")

    # 測試記憶
    console.print("[yellow]測試記憶：[/yellow]")
    memory_tests = [
        "我叫什麼名字？",
        "我用什麼編程語言？",
        "基於我的背景，推薦一個適合我的課程",
    ]

    for question in memory_tests:
        console.print(f"[blue]用戶：[/blue] {question}")
        response = conv.send(question)
        console.print(f"[green]助手：[/green] {response[:150]}...\n")


def demo_error_recovery():
    """錯誤恢復對話示例"""
    console.print("[bold cyan]7. 錯誤恢復對話[/bold cyan]\n")

    conv = StatefulConversation()

    system_prompt = """當用戶表達不滿或指出錯誤時，你應該：
1. 承認錯誤
2. 道歉
3. 提供正確的信息或解決方案
"""

    # 錯誤場景
    console.print("[blue]用戶：[/blue] Python 是用 C++ 寫的嗎？")
    response = conv.send("Python 是用 C++ 寫的嗎？", system_prompt)
    console.print(f"[green]助手：[/green] {response[:100]}...\n")

    console.print("[blue]用戶：[/blue] 不對，CPython 是用 C 寫的，不是 C++")
    response = conv.send("不對，CPython 是用 C 寫的，不是 C++", system_prompt)
    console.print(f"[green]助手：[/green] {response[:150]}...\n")


def visualize_conversation_tree():
    """可視化對話樹"""
    console.print("\n[bold cyan]對話樹可視化[/bold cyan]\n")

    tree = Tree("[bold cyan]對話流程")

    # 主幹
    greeting = tree.add("[yellow]用戶：你好")
    greeting.add("[green]助手：你好！有什麼可以幫你的？")

    # 分支 1
    branch1 = tree.add("[yellow]用戶：我想學編程")
    response1 = branch1.add("[green]助手：很好！你想學什麼語言？")
    subbranch1a = response1.add("[yellow]選項 A：Python")
    subbranch1a.add("[green]推薦 Python 資源")
    subbranch1b = response1.add("[yellow]選項 B：JavaScript")
    subbranch1b.add("[green]推薦 JS 資源")

    # 分支 2
    branch2 = tree.add("[yellow]用戶：我有個 bug")
    branch2.add("[green]助手：請描述問題")

    console.print(tree)
    console.print()


def show_conversation_patterns():
    """展示對話模式"""
    console.print("[bold cyan]常見對話模式[/bold cyan]\n")

    patterns = {
        "信息收集": "逐步收集必要信息完成任務",
        "問答式": "用戶提問，助手回答",
        "指導式": "助手引導用戶完成流程",
        "協作式": "用戶和助手共同解決問題",
        "診斷式": "通過提問診斷問題",
        "教學式": "循序漸進教授知識",
    }

    for pattern, description in patterns.items():
        console.print(f"[cyan]• {pattern}：[/cyan]{description}")

    console.print()


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Claude Code SDK 多輪對話[/bold cyan]\n"
        "[dim]學習如何處理複雜的多輪對話場景[/dim]",
        border_style="cyan"
    ))

    # 1. 信息收集
    demo_information_gathering()

    # 2. 上下文理解
    demo_contextual_conversation()

    # 3. 對話分支
    demo_conversation_branching()

    # 4. 任務導向
    demo_task_oriented_conversation()

    # 5. 澄清對話
    demo_clarification_conversation()

    # 6. 對話記憶
    demo_conversation_memory()

    # 7. 錯誤恢復
    demo_error_recovery()

    # 可視化
    visualize_conversation_tree()

    # 對話模式
    show_conversation_patterns()

    # 完成
    console.print("="*60)
    console.print("[bold green]✓ 多輪對話示例完成！[/bold green]")
    console.print("\n[cyan]關鍵要點：[/cyan]")
    console.print("  • 維護對話上下文實現連貫交流")
    console.print("  • 使用狀態機管理複雜對話流程")
    console.print("  • 支持對話分支處理多種情況")
    console.print("  • 實現錯誤恢復提升用戶體驗")


if __name__ == "__main__":
    main()

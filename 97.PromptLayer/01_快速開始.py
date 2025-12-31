"""
PromptLayer 快速開始示例

本示例展示：
1. PromptLayer 配置
2. 基本請求追蹤
3. 查看請求歷史
4. Web 界面使用
"""

import os
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# 加載環境變量
load_dotenv()

console = Console()


def setup_promptlayer():
    """設置 PromptLayer"""
    console.print("\n[cyan]設置 PromptLayer[/cyan]\n")

    try:
        import promptlayer

        # 設置 API Key
        api_key = os.getenv("PROMPTLAYER_API_KEY")

        if not api_key:
            console.print("[red]✗ 未找到 PROMPTLAYER_API_KEY[/red]")
            console.print("\n[yellow]請按照以下步驟設置:[/yellow]")
            console.print("  1. 訪問 https://promptlayer.com")
            console.print("  2. 註冊賬號並登錄")
            console.print("  3. 在設置中獲取 API Key")
            console.print("  4. 設置環境變量: PROMPTLAYER_API_KEY=your_key")
            return None

        promptlayer.api_key = api_key
        console.print("[green]✓ PromptLayer 配置成功[/green]\n")

        return promptlayer

    except ImportError:
        console.print("[red]✗ PromptLayer 未安裝[/red]")
        console.print("[yellow]請運行: pip install promptlayer[/yellow]")
        return None


def basic_tracking_example(promptlayer):
    """基本追蹤示例"""
    console.print("[cyan]1. 基本請求追蹤[/cyan]\n")

    try:
        # 包裝 OpenAI 客戶端
        OpenAI = promptlayer.openai.OpenAI

        # 模擬配置（實際使用時需要真實的 OpenAI API Key）
        console.print("[yellow]示例: 使用 PromptLayer 包裝 OpenAI[/yellow]\n")

        code = """import promptlayer

# 設置 PromptLayer
promptlayer.api_key = "your-promptlayer-key"

# 包裝 OpenAI
OpenAI = promptlayer.openai.OpenAI
client = OpenAI(api_key="your-openai-key")

# 正常使用 OpenAI，自動追蹤
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "什麼是 PromptLayer？"}
    ],
    # PromptLayer 特定參數
    pl_tags=["tutorial", "quickstart"],  # 添加標籤
    return_pl_id=True  # 返回 PromptLayer 請求 ID
)

print(f"回答: {response.choices[0].message.content}")
print(f"PromptLayer ID: {response.pl_request_id}")
"""

        from rich.syntax import Syntax
        syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
        console.print(syntax)
        console.print()

        console.print("[green]✓ 所有請求都會自動記錄到 PromptLayer[/green]\n")

    except Exception as e:
        console.print(f"[red]✗ 示例失敗: {e}[/red]\n")


def show_features():
    """顯示主要功能"""
    console.print("[cyan]2. PromptLayer 主要功能[/cyan]\n")

    features = [
        ("請求追蹤", "自動記錄所有 LLM 請求", "所有請求和響應都被記錄"),
        ("標籤管理", "為請求添加標籤", "便於組織和搜索"),
        ("模板管理", "集中管理提示模板", "版本控制和重用"),
        ("評分系統", "對請求進行評分", "評估質量和效果"),
        ("成本分析", "追蹤 token 使用", "控制和優化成本"),
        ("團隊協作", "多人協作管理", "共享和權限控制"),
    ]

    table = Table(title="PromptLayer 功能一覽")
    table.add_column("功能", style="cyan", width=15)
    table.add_column("說明", style="yellow", width=20)
    table.add_column("用途", style="green", width=25)

    for feature, desc, purpose in features:
        table.add_row(feature, desc, purpose)

    console.print(table)
    console.print()


def show_web_interface():
    """展示 Web 界面功能"""
    console.print("[cyan]3. Web 界面功能[/cyan]\n")

    console.print("[yellow]訪問 Web 界面:[/yellow]")
    console.print("  https://www.promptlayer.com\n")

    features = """📊 儀表板
   • 請求總覽和統計
   • 實時活動監控
   • 成本追蹤圖表

🔍 請求搜索
   • 按標籤、時間、模型搜索
   • 查看完整的請求和響應
   • 過濾和排序功能

📝 模板管理
   • 創建和編輯模板
   • 版本歷史查看
   • 模板性能分析

⭐ 評分和評估
   • 手動評分請求
   • 評分統計分析
   • 評論和討論

💰 成本分析
   • Token 使用統計
   • 成本趨勢分析
   • 預算告警設置

👥 團隊管理
   • 成員管理
   • 權限設置
   • 項目隔離"""

    console.print(Panel(features, border_style="cyan"))
    console.print()


def show_request_tracking():
    """展示請求追蹤"""
    console.print("[cyan]4. 請求追蹤詳情[/cyan]\n")

    console.print("[yellow]每個請求記錄包含:[/yellow]\n")

    tracked_info = [
        ("基本信息", "模型、提示、響應"),
        ("時間信息", "請求時間、響應時間、延遲"),
        ("Token 信息", "輸入 tokens、輸出 tokens、總計"),
        ("成本信息", "根據 token 計算的成本"),
        ("元數據", "標籤、用戶 ID、會話 ID"),
        ("環境信息", "SDK 版本、Python 版本"),
    ]

    table = Table(title="請求追蹤信息")
    table.add_column("類別", style="cyan")
    table.add_column("包含內容", style="yellow")

    for category, content in tracked_info:
        table.add_row(category, content)

    console.print(table)
    console.print()


def show_integration_example():
    """展示整合示例"""
    console.print("[cyan]5. 完整整合示例[/cyan]\n")

    code = """import promptlayer
import os
from dotenv import load_dotenv

# 加載環境變量
load_dotenv()

# 配置 PromptLayer
promptlayer.api_key = os.getenv("PROMPTLAYER_API_KEY")

# 包裝 OpenAI
OpenAI = promptlayer.openai.OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def chat_with_tracking(user_message: str, user_id: str = None):
    \"\"\"帶追蹤的聊天函數\"\"\"

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "你是一個有幫助的助手"},
            {"role": "user", "content": user_message}
        ],
        temperature=0.7,
        max_tokens=500,

        # PromptLayer 參數
        pl_tags=["chat", "production"],
        return_pl_id=True,

        # 自定義元數據
        metadata={
            "user_id": user_id,
            "feature": "chat",
            "environment": "production"
        }
    )

    # 提取響應
    answer = response.choices[0].message.content
    request_id = response.pl_request_id

    print(f"答案: {answer}")
    print(f"PromptLayer ID: {request_id}")

    return answer, request_id


# 使用示例
answer, request_id = chat_with_tracking(
    "什麼是機器學習？",
    user_id="user_123"
)

# 可以稍後對請求評分
promptlayer.track.score(
    request_id=request_id,
    score=100,  # 0-100
    metadata={"evaluated_by": "user"}
)
"""

    from rich.syntax import Syntax
    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def show_cli_commands():
    """顯示 CLI 命令"""
    console.print("[cyan]6. PromptLayer CLI 命令[/cyan]\n")

    commands = [
        ("promptlayer auth", "配置 API Key"),
        ("promptlayer list", "列出最近的請求"),
        ("promptlayer get <id>", "查看特定請求詳情"),
        ("promptlayer templates", "列出所有模板"),
        ("promptlayer export", "導出數據"),
    ]

    table = Table(title="CLI 命令")
    table.add_column("命令", style="cyan")
    table.add_column("說明", style="yellow")

    for cmd, desc in commands:
        table.add_row(cmd, desc)

    console.print(table)
    console.print()


def show_next_steps():
    """顯示下一步"""
    console.print("="*60)
    console.print("[bold green]✓ 快速開始完成！[/bold green]\n")

    console.print("[cyan]下一步學習:[/cyan]")
    console.print("  1. 查看 02_請求追蹤.py - 深入了解請求追蹤")
    console.print("  2. 查看 03_提示模板.py - 學習模板管理")
    console.print("  3. 查看 05_AB測試.py - 進行 A/B 測試")
    console.print("  4. 查看 07_成本分析.py - 分析成本")
    console.print()

    console.print("[cyan]實踐建議:[/cyan]")
    console.print("  • 註冊 PromptLayer 賬號")
    console.print("  • 整合到現有項目")
    console.print("  • 查看 Web 界面")
    console.print("  • 嘗試評分和標籤功能")


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]PromptLayer 快速開始[/bold cyan]\n"
        "[dim]LLM 請求監控和管理平台[/dim]",
        border_style="cyan"
    ))

    # 1. 設置 PromptLayer
    promptlayer = setup_promptlayer()

    # 2. 基本追蹤示例
    if promptlayer:
        basic_tracking_example(promptlayer)

    # 3. 功能介紹
    show_features()

    # 4. Web 界面
    show_web_interface()

    # 5. 請求追蹤
    show_request_tracking()

    # 6. 整合示例
    show_integration_example()

    # 7. CLI 命令
    show_cli_commands()

    # 8. 下一步
    show_next_steps()


if __name__ == "__main__":
    main()

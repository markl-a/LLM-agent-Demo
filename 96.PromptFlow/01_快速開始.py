"""
PromptFlow 快速開始示例

本示例展示：
1. PromptFlow 環境設置
2. 創建簡單的 Flow
3. 運行和測試 Flow
4. 查看執行結果
"""

import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from dotenv import load_dotenv

# 加載環境變量
load_dotenv()

console = Console()


def check_environment():
    """檢查 PromptFlow 環境"""
    try:
        console.print("\n[cyan]檢查 PromptFlow 環境...[/cyan]")

        # 檢查 promptflow 安裝
        import promptflow
        from promptflow import tool

        table = Table(title="環境信息")
        table.add_column("組件", style="cyan")
        table.add_column("狀態", style="green")
        table.add_column("版本", style="yellow")

        table.add_row("PromptFlow", "✓ 已安裝", promptflow.__version__)

        # 檢查環境變量
        required_vars = ["AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_KEY"]
        for var in required_vars:
            status = "✓ 已設置" if os.getenv(var) else "✗ 未設置"
            table.add_row(var, status, "-")

        console.print(table)
        console.print()

        return True

    except ImportError as e:
        console.print(f"[red]✗ PromptFlow 未安裝: {e}[/red]")
        console.print("[yellow]請運行: pip install promptflow promptflow-tools[/yellow]")
        return False


def create_simple_tool():
    """創建簡單的工具函數"""
    console.print("[cyan]創建簡單的工具函數...[/cyan]")

    # 定義一個簡單的工具
    from promptflow import tool

    @tool
    def greeting_tool(name: str, language: str = "zh") -> str:
        """簡單的問候工具"""
        greetings = {
            "zh": f"你好，{name}！歡迎使用 PromptFlow！",
            "en": f"Hello, {name}! Welcome to PromptFlow!",
            "ja": f"こんにちは、{name}さん！PromptFlowへようこそ！"
        }
        return greetings.get(language, greetings["zh"])

    console.print("[green]✓ 工具函數創建成功[/green]\n")

    return greeting_tool


def test_tool(tool_func):
    """測試工具函數"""
    console.print("[cyan]測試工具函數...[/cyan]")

    # 測試不同的輸入
    test_cases = [
        {"name": "張三", "language": "zh"},
        {"name": "John", "language": "en"},
        {"name": "太郎", "language": "ja"},
    ]

    table = Table(title="工具測試結果")
    table.add_column("名稱", style="cyan")
    table.add_column("語言", style="yellow")
    table.add_column("輸出", style="green")

    for case in test_cases:
        result = tool_func(**case)
        table.add_row(case["name"], case["language"], result)

    console.print(table)
    console.print()


def create_flow_directory():
    """創建 Flow 目錄結構"""
    console.print("[cyan]創建 Flow 目錄...[/cyan]")

    # 創建基本的 Flow 目錄
    flow_dir = Path("./my_first_flow")
    flow_dir.mkdir(exist_ok=True)

    # 創建 flow.dag.yaml
    flow_config = """
# Flow 配置文件
$schema: https://azuremlschemas.azureedge.net/promptflow/latest/Flow.schema.json

inputs:
  question:
    type: string
    default: "什麼是 PromptFlow？"

outputs:
  answer:
    type: string
    reference: ${process_output.output}

nodes:
  # 節點 1: 處理輸入
  - name: process_input
    type: python
    source:
      type: code
      path: process_input.py
    inputs:
      question: ${inputs.question}

  # 節點 2: 生成回答
  - name: process_output
    type: python
    source:
      type: code
      path: process_output.py
    inputs:
      processed_question: ${process_input.output}
"""

    (flow_dir / "flow.dag.yaml").write_text(flow_config.strip())

    # 創建節點文件
    process_input_code = '''
from promptflow import tool

@tool
def process_input(question: str) -> str:
    """處理輸入問題"""
    return f"處理問題: {question}"
'''

    process_output_code = '''
from promptflow import tool

@tool
def process_output(processed_question: str) -> str:
    """生成回答"""
    return f"這是一個示例回答: {processed_question}"
'''

    (flow_dir / "process_input.py").write_text(process_input_code.strip())
    (flow_dir / "process_output.py").write_text(process_output_code.strip())

    console.print(f"[green]✓ Flow 目錄創建成功: {flow_dir}[/green]")

    # 顯示目錄結構
    console.print("\n[cyan]目錄結構:[/cyan]")
    console.print("my_first_flow/")
    console.print("  ├── flow.dag.yaml")
    console.print("  ├── process_input.py")
    console.print("  └── process_output.py")
    console.print()

    return flow_dir


def run_flow_example():
    """運行 Flow 示例（模擬）"""
    console.print("[cyan]模擬運行 Flow...[/cyan]")

    # 模擬 Flow 執行過程
    steps = [
        ("讀取 Flow 配置", "✓"),
        ("初始化節點", "✓"),
        ("執行 process_input 節點", "✓"),
        ("執行 process_output 節點", "✓"),
        ("返回結果", "✓"),
    ]

    table = Table(title="Flow 執行過程")
    table.add_column("步驟", style="cyan")
    table.add_column("狀態", style="green")

    for step, status in steps:
        table.add_row(step, status)

    console.print(table)
    console.print()

    # 模擬輸出結果
    console.print("[cyan]執行結果:[/cyan]")
    result_panel = Panel(
        "[green]這是一個示例回答: 處理問題: 什麼是 PromptFlow？[/green]",
        title="Flow 輸出",
        border_style="green"
    )
    console.print(result_panel)
    console.print()


def show_cli_commands():
    """顯示常用 CLI 命令"""
    console.print("[cyan]常用 PromptFlow CLI 命令:[/cyan]\n")

    commands = [
        ("pf --version", "查看版本"),
        ("pf flow init --flow my_flow", "創建新 Flow"),
        ("pf flow test --flow ./my_flow", "測試 Flow"),
        ("pf run create --flow ./my_flow --data ./data.jsonl", "批量運行"),
        ("pf flow serve --source ./my_flow --port 8080", "啟動服務"),
    ]

    table = Table(title="CLI 命令參考")
    table.add_column("命令", style="cyan")
    table.add_column("說明", style="yellow")

    for cmd, desc in commands:
        table.add_row(cmd, desc)

    console.print(table)
    console.print()


def show_next_steps():
    """顯示下一步建議"""
    console.print("="*60)
    console.print("[bold green]✓ 快速開始示例完成！[/bold green]\n")

    console.print("[cyan]下一步學習:[/cyan]")
    console.print("  1. 查看 02_流程設計.py - 學習 Flow 設計")
    console.print("  2. 查看 03_節點類型.py - 了解各種節點類型")
    console.print("  3. 查看 06_批量運行.py - 學習批量測試")
    console.print("  4. 查看 09_Azure整合.py - 整合 Azure 服務")
    console.print()

    console.print("[cyan]實踐建議:[/cyan]")
    console.print("  • 安裝 VS Code 的 PromptFlow 擴展")
    console.print("  • 嘗試創建自己的第一個 Flow")
    console.print("  • 探索官方示例庫")
    console.print("  • 加入 GitHub Discussions 社區")


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]PromptFlow 快速開始示例[/bold cyan]\n"
        "[dim]微軟的提示工程平台[/dim]",
        border_style="cyan"
    ))

    # 1. 檢查環境
    if not check_environment():
        console.print("[yellow]提示: 某些功能可能需要配置環境變量[/yellow]")

    # 2. 創建和測試工具
    tool_func = create_simple_tool()
    test_tool(tool_func)

    # 3. 創建 Flow 目錄
    flow_dir = create_flow_directory()

    # 4. 模擬運行 Flow
    run_flow_example()

    # 5. 顯示 CLI 命令
    show_cli_commands()

    # 6. 下一步建議
    show_next_steps()


if __name__ == "__main__":
    main()

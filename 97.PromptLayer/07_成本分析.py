"""
PromptLayer 成本分析示例

本示例展示：
1. Token 使用追蹤
2. 成本計算
3. 成本優化
4. 預算管理
"""

import os
from rich.console import Console
from rich.panel import Panel

console = Console()


def track_token_usage():
    """追蹤 Token 使用"""
    console.print("\n[cyan]1. Token 使用追蹤[/cyan]\n")

    info = """PromptLayer 自動記錄所有請求的 Token 使用：

記錄內容：
• prompt_tokens: 輸入 tokens
• completion_tokens: 輸出 tokens
• total_tokens: 總計 tokens
• model: 使用的模型
• timestamp: 請求時間

在 Web 界面查看：
• Dashboard → Cost Analytics
• 按時間、模型、用戶等維度查看
• 導出詳細報表"""

    console.print(Panel(info, border_style="cyan"))
    console.print()


def calculate_costs():
    """計算成本"""
    console.print("[cyan]2. 成本計算[/cyan]\n")

    from rich.syntax import Syntax
    code = """# 模型定價（2024年參考）
MODEL_PRICES = {
    "gpt-4": {
        "input": 0.03 / 1000,   # $0.03/1K tokens
        "output": 0.06 / 1000   # $0.06/1K tokens
    },
    "gpt-3.5-turbo": {
        "input": 0.0005 / 1000,  # $0.0005/1K tokens
        "output": 0.0015 / 1000  # $0.0015/1K tokens
    }
}

def calculate_request_cost(request):
    \"\"\"計算單個請求成本\"\"\"
    model = request['model']
    pricing = MODEL_PRICES.get(model, MODEL_PRICES['gpt-3.5-turbo'])
    
    input_cost = request['prompt_tokens'] * pricing['input']
    output_cost = request['completion_tokens'] * pricing['output']
    total_cost = input_cost + output_cost
    
    return total_cost

# 計算總成本
total_cost = sum(calculate_request_cost(req) for req in requests_data)
print(f"總成本: ${total_cost:.4f}")
"""

    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]PromptLayer 成本分析示例[/bold cyan]",
        border_style="cyan"
    ))

    track_token_usage()
    calculate_costs()

    console.print("="*60)
    console.print("[bold green]✓ 成本分析示例完成！[/bold green]\n")


if __name__ == "__main__":
    main()

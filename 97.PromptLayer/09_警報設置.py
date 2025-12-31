"""
PromptLayer 警報設置示例

本示例展示：
1. 設置成本警報
2. 異常檢測
3. 性能監控
4. 通知配置
"""

import os
from rich.console import Console
from rich.panel import Panel

console = Console()


def alert_types():
    """警報類型"""
    console.print("\n[cyan]警報類型[/cyan]\n")

    types = """PromptLayer 支持的警報類型：

1. 成本警報
   • 超出每日預算
   • 異常成本增長
   • 單次請求成本過高

2. 性能警報
   • 延遲過高
   • 錯誤率上升
   • 評分下降

3. 使用量警報
   • Token 使用激增
   • 請求頻率異常
   • 配額接近上限

4. 質量警報
   • 平均評分低於閾值
   • 負面反饋增加
   • 異常輸出檢測

配置方式：
• Web 界面: Settings → Alerts
• 通知渠道: Email, Slack, Webhook
• 靈活的閾值設置"""

    console.print(Panel(types, border_style="cyan"))
    console.print()


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]PromptLayer 警報設置示例[/bold cyan]",
        border_style="cyan"
    ))

    alert_types()

    console.print("="*60)
    console.print("[bold green]✓ 警報設置示例完成！[/bold green]\n")


if __name__ == "__main__":
    main()

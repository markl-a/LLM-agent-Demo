"""
PromptLayer 團隊協作示例

本示例展示：
1. 團隊管理
2. 權限控制
3. 項目隔離
4. 協作工作流
"""

import os
from rich.console import Console
from rich.panel import Panel

console = Console()


def team_features():
    """團隊功能"""
    console.print("\n[cyan]團隊協作功能[/cyan]\n")

    features = """PromptLayer 團隊功能（專業版/企業版）：

1. 成員管理
   • 邀請團隊成員
   • 角色分配（Admin/Member/Viewer）
   • 訪問控制

2. 項目隔離
   • 創建多個項目
   • 獨立的模板和數據
   • 跨項目協作

3. 共享儀表板
   • 團隊共享分析視圖
   • 實時數據更新
   • 自定義報表

4. 協作評估
   • 多人評分請求
   • 評論和討論
   • 共享洞察

5. 審計日誌
   • 追蹤團隊活動
   • 變更歷史
   • 合規審計"""

    console.print(Panel(features, border_style="cyan"))
    console.print()


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]PromptLayer 團隊協作示例[/bold cyan]",
        border_style="cyan"
    ))

    team_features()

    console.print("="*60)
    console.print("[bold green]✓ 團隊協作示例完成！[/bold green]\n")


if __name__ == "__main__":
    main()

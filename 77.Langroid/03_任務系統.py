"""
Langroid 任務系統 - Task 的使用

這個示例展示：
1. Task 的基本概念
2. 任務委託
3. 任務編排
4. 任務控制

Task 是 Langroid 組織 Agent 的關鍵抽象。
"""

import os
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

try:
    import langroid as lr
    import langroid.language_models as lm
    LANGROID_AVAILABLE = True
except ImportError:
    LANGROID_AVAILABLE = False

console = Console()
load_dotenv()


def task_basics_example():
    """任務基礎"""
    console.print(Panel("[bold cyan]任務基礎概念[/bold cyan]"))

    console.print("""
[yellow]Task 是什麼？[/yellow]

Task 將 Agent 包裝為可執行的單元：
- 提供運行環境
- 處理消息路由
- 管理對話流程
- 支持任務委託

[yellow]Task 基本用法：[/yellow]
    """)

    code = '''
# 創建 Agent
agent = lr.ChatAgent(config=lr.ChatAgentConfig(...))

# 創建 Task
task = lr.Task(
    agent,
    name="我的任務",
    interactive=False  # False: 單次運行, True: 交互模式
)

# 運行任務
result = task.run("用戶輸入")
print(result.content)

# 或者逐步運行
task.init("初始消息")
while not task.done():
    response = task.step()
    if response:
        print(response.content)
    '''

    console.print(Panel(code, border_style="blue"))


def task_delegation_example():
    """任務委託"""
    console.print(Panel("[bold cyan]任務委託[/bold cyan]"))

    console.print("""
[yellow]任務委託概念：[/yellow]

在 Langroid 中，一個 Agent 可以將子任務委託給其他 Agent：

1. 主 Agent 識別需要委託的子任務
2. 創建子 Task 並委託
3. 子 Agent 完成任務
4. 結果返回給主 Agent

[yellow]委託示例：[/yellow]
    """)

    delegation_code = '''
# 創建主 Agent
coordinator = lr.ChatAgent(
    config=lr.ChatAgentConfig(
        name="協調員",
        system_message="你負責協調任務，將專業問題委託給專家"
    )
)

# 創建專家 Agent
expert = lr.ChatAgent(
    config=lr.ChatAgentConfig(
        name="技術專家",
        system_message="你是技術專家，回答技術問題"
    )
)

# 創建任務
main_task = lr.Task(coordinator, name="主任務")
expert_task = lr.Task(expert, name="專家任務")

# 主任務可以委託給專家任務
# main_task.add_sub_task(expert_task)
    '''

    console.print(Panel(delegation_code, border_style="blue"))


def task_control_example():
    """任務控制"""
    console.print(Panel("[bold cyan]任務控制[/bold cyan]"))

    console.print("""
[yellow]任務控制選項：[/yellow]

1. [cyan]max_turns[/cyan]: 最大輪次
   - 限制對話輪數
   - 防止無限循環

2. [cyan]interactive[/cyan]: 交互模式
   - True: 命令行交互
   - False: 編程式調用

3. [cyan]done_if_no_response[/cyan]: 無響應時完成
   - 控制任務結束條件

4. [cyan]done_if_response[/cyan]: 有響應時完成
   - 收到特定響應後結束

[yellow]示例：[/yellow]
    ''')

    control_code = '''
task = lr.Task(
    agent,
    name="受控任務",
    max_turns=10,  # 最多 10 輪
    interactive=False,
    done_if_no_response=[lr.Entity.LLM],  # LLM 無響應時結束
)

# 運行
result = task.run("開始任務", turns=5)  # 最多5輪
    '''

    console.print(Panel(control_code, border_style="blue"))


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold green]Langroid 任務系統[/bold green]",
        border_style="green"
    ))

    task_basics_example()
    console.print("\n" + "="*60 + "\n")

    task_delegation_example()
    console.print("\n" + "="*60 + "\n")

    task_control_example()

    console.print(Panel("""
[bold green]任務系統完成！[/bold green]

關鍵要點：
1. Task 包裝 Agent 提供執行環境
2. 支持任務委託和編排
3. 靈活的控制選項
4. 可以創建複雜的任務層次

下一步：查看 04_工具使用.py
    """, title="總結", border_style="green"))


if __name__ == "__main__":
    main()

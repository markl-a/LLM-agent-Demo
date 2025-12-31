"""
Langroid 快速開始 - 基本使用

這個示例展示如何：
1. 配置 Langroid 和 LLM
2. 創建基本的 ChatAgent
3. 運行簡單任務
4. 處理對話

Langroid 提供簡潔優雅的 API 來構建 LLM 應用。
"""

import os
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

# Langroid 導入
try:
    import langroid as lr
    import langroid.language_models as lm
    LANGROID_AVAILABLE = True
except ImportError:
    LANGROID_AVAILABLE = False

console = Console()
load_dotenv()


# ============================================================================
# 示例 1：最簡單的 Agent
# ============================================================================

def simple_agent_example():
    """示例 1：最簡單的 Agent"""
    console.print(Panel("[bold cyan]示例 1：最簡單的 Agent[/bold cyan]"))

    if not LANGROID_AVAILABLE:
        console.print("[red]錯誤：請先安裝 Langroid: pip install langroid[/red]")
        return

    if not os.getenv("OPENAI_API_KEY"):
        console.print("[red]錯誤：請設置 OPENAI_API_KEY 環境變量[/red]")
        return

    try:
        console.print("\n[yellow]創建 ChatAgent...[/yellow]")

        # 配置語言模型
        llm_config = lm.OpenAIGPTConfig(
            chat_model="gpt-4o-mini",
            temperature=0.7
        )

        # 創建 Agent
        agent = lr.ChatAgent(
            config=lr.ChatAgentConfig(
                llm=llm_config,
                name="助手",
                system_message="你是一個友好的 AI 助手，用中文回答問題。"
            )
        )

        console.print("[green]✓ Agent 創建成功[/green]")

        # 直接與 Agent 對話
        console.print("\n[yellow]與 Agent 對話：[/yellow]")

        question = "請用一句話介紹什麼是 Langroid"
        console.print(f"\n[cyan]用戶：[/cyan]{question}")

        response = agent.llm_response(question)
        console.print(f"[green]助手：[/green]{response.content}")

    except Exception as e:
        console.print(f"[red]錯誤：{e}[/red]")


# ============================================================================
# 示例 2：使用 Task
# ============================================================================

def task_example():
    """示例 2：使用 Task"""
    console.print(Panel("[bold cyan]示例 2：使用 Task[/bold cyan]"))

    if not LANGROID_AVAILABLE or not os.getenv("OPENAI_API_KEY"):
        console.print("[yellow]跳過此示例（需要 Langroid 和 API Key）[/yellow]")
        return

    try:
        console.print("\n[yellow]創建 Task...[/yellow]")

        # 配置
        llm_config = lm.OpenAIGPTConfig(
            chat_model="gpt-4o-mini",
            temperature=0.7
        )

        # 創建 Agent
        agent = lr.ChatAgent(
            config=lr.ChatAgentConfig(
                llm=llm_config,
                name="助手",
                system_message="""
你是一個專業的技術講解員。
你的任務是用簡單易懂的方式解釋技術概念。
                """
            )
        )

        # 創建 Task（Task 包裝 Agent）
        task = lr.Task(
            agent,
            name="技術講解",
            interactive=False  # 非交互模式
        )

        console.print("[green]✓ Task 創建成功[/green]")

        # 運行 Task
        console.print("\n[yellow]運行 Task：[/yellow]")

        question = "請解釋什麼是向量數據庫"
        console.print(f"\n[cyan]問題：[/cyan]{question}")

        result = task.run(question)

        console.print(f"\n[green]回答：[/green]{result.content}")

    except Exception as e:
        console.print(f"[red]錯誤：{e}[/red]")


# ============================================================================
# 示例 3：多輪對話
# ============================================================================

def multi_turn_example():
    """示例 3：多輪對話"""
    console.print(Panel("[bold cyan]示例 3：多輪對話[/bold cyan]"))

    if not LANGROID_AVAILABLE or not os.getenv("OPENAI_API_KEY"):
        console.print("[yellow]跳過此示例[/yellow]")
        return

    try:
        # 配置
        llm_config = lm.OpenAIGPTConfig(
            chat_model="gpt-4o-mini",
            temperature=0.7
        )

        # 創建 Agent
        agent = lr.ChatAgent(
            config=lr.ChatAgentConfig(
                llm=llm_config,
                name="助手",
                system_message="你是一個有記憶的助手，記住之前的對話內容。"
            )
        )

        console.print("\n[yellow]多輪對話：[/yellow]\n")

        # 對話序列
        conversations = [
            "我的名字是張三",
            "我最喜歡的顏色是藍色",
            "我的名字是什麼？",
            "我最喜歡什麼顏色？"
        ]

        for i, msg in enumerate(conversations, 1):
            console.print(f"[cyan]用戶 ({i})：[/cyan]{msg}")

            response = agent.llm_response(msg)

            console.print(f"[green]助手 ({i})：[/green]{response.content}\n")

        console.print("[yellow]提示：Agent 記住了之前的對話內容[/yellow]")

    except Exception as e:
        console.print(f"[red]錯誤：{e}[/red]")


# ============================================================================
# 示例 4：配置選項
# ============================================================================

def configuration_example():
    """示例 4：配置選項"""
    console.print(Panel("[bold cyan]示例 4：配置選項[/bold cyan]"))

    console.print("""
[yellow]Langroid 配置選項：[/yellow]

1. [cyan]LLM 配置（OpenAIGPTConfig）[/cyan]
   - chat_model: 模型名稱（gpt-4, gpt-4o-mini 等）
   - temperature: 溫度（0-2）
   - max_tokens: 最大 token 數
   - timeout: 超時時間

2. [cyan]Agent 配置（ChatAgentConfig）[/cyan]
   - llm: LLM 配置對象
   - name: Agent 名稱
   - system_message: 系統消息
   - user_message: 用戶消息模板

3. [cyan]Task 配置[/cyan]
   - agent: Agent 對象
   - name: 任務名稱
   - interactive: 是否交互模式
   - max_turns: 最大輪次

[yellow]配置示例：[/yellow]
    """)

    config_code = '''
import langroid as lr
import langroid.language_models as lm

# LLM 配置
llm_config = lm.OpenAIGPTConfig(
    chat_model="gpt-4o-mini",
    temperature=0.7,
    max_tokens=500,
    timeout=30
)

# Agent 配置
agent_config = lr.ChatAgentConfig(
    llm=llm_config,
    name="我的 Agent",
    system_message="""
你是一個專業的助手。
用中文回答問題。
    """,
    max_context_tokens=4000
)

# 創建 Agent
agent = lr.ChatAgent(agent_config)

# 創建 Task
task = lr.Task(
    agent,
    name="我的任務",
    interactive=False,
    max_turns=10
)

# 運行
result = task.run("你好！")
    '''

    console.print(Panel(config_code, border_style="blue", title="完整配置"))


# ============================================================================
# 主函數
# ============================================================================

def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold green]Langroid 快速開始 - 基本使用[/bold green]",
        border_style="green"
    ))

    console.print("\n[bold]Langroid 核心概念：[/bold]")
    console.print("1. [cyan]ChatAgent[/cyan]: 封裝 LLM 的 Agent")
    console.print("2. [cyan]Task[/cyan]: 包裝 Agent 為可執行任務")
    console.print("3. [cyan]Config[/cyan]: 配置 LLM 和 Agent")
    console.print("4. [cyan]Message[/cyan]: 結構化的消息系統\n")

    # 運行示例
    simple_agent_example()
    console.print("\n" + "="*60 + "\n")

    task_example()
    console.print("\n" + "="*60 + "\n")

    multi_turn_example()
    console.print("\n" + "="*60 + "\n")

    configuration_example()

    # 總結
    console.print(Panel("""
[bold green]快速開始完成！[/bold green]

關鍵要點：
1. Langroid 使用 Agent 作為核心抽象
2. Task 包裝 Agent 提供執行環境
3. 配置簡潔直觀
4. 自動管理對話歷史
5. 支持多輪對話

Langroid 的優勢：
- 簡潔優雅的 API
- 面向對象的設計
- 類型安全（Pydantic）
- 原生多 Agent 支持
- 豐富的功能

基本流程：
1. 配置 LLM (OpenAIGPTConfig)
2. 創建 Agent (ChatAgent)
3. 創建 Task (Task)
4. 運行任務 (task.run())

下一步：
- 查看 02_Agent基礎.py 深入了解 Agent
- 查看 03_任務系統.py 學習任務組織
- 查看 04_工具使用.py 集成工具
- 訪問 https://langroid.github.io/langroid/
    """, title="總結", border_style="green"))


if __name__ == "__main__":
    main()

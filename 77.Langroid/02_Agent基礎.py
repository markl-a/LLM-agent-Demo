"""
Langroid Agent 基礎 - 深入理解 Agent

這個示例展示如何：
1. Agent 的生命週期
2. 自定義 Agent 行為
3. Agent 狀態管理
4. Agent 配置選項

掌握 Agent 是使用 Langroid 的關鍵。
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


# ============================================================================
# 示例 1：Agent 基本屬性
# ============================================================================

def agent_properties_example():
    """示例 1：Agent 基本屬性"""
    console.print(Panel("[bold cyan]示例 1：Agent 基本屬性[/bold cyan]"))

    if not LANGROID_AVAILABLE or not os.getenv("OPENAI_API_KEY"):
        console.print("[yellow]需要 Langroid 和 API Key[/yellow]")
        return

    # 創建 Agent
    llm_config = lm.OpenAIGPTConfig(chat_model="gpt-4o-mini")

    agent = lr.ChatAgent(
        config=lr.ChatAgentConfig(
            llm=llm_config,
            name="演示Agent",
            system_message="你是一個演示 Agent。"
        )
    )

    console.print("\n[yellow]Agent 屬性：[/yellow]")
    console.print(f"  名稱: {agent.config.name}")
    console.print(f"  模型: {agent.config.llm.chat_model}")
    console.print(f"  系統消息: {agent.config.system_message[:50]}...")


# ============================================================================
# 示例 2：自定義 Agent
# ============================================================================

def custom_agent_example():
    """示例 2：自定義 Agent"""
    console.print(Panel("[bold cyan]示例 2：自定義 Agent 類[/bold cyan]"))

    console.print("""
[yellow]自定義 Agent 示例：[/yellow]

可以繼承 ChatAgent 創建自定義 Agent：
    """)

    code = '''
class MyCustomAgent(lr.ChatAgent):
    """自定義 Agent"""

    def __init__(self, config: lr.ChatAgentConfig):
        super().__init__(config)
        self.custom_data = {}

    def process_message(self, message: str) -> str:
        """自定義消息處理"""
        # 前處理
        processed = message.upper()

        # 調用 LLM
        response = self.llm_response(processed)

        # 後處理
        return response.content.lower()

# 使用
agent = MyCustomAgent(
    config=lr.ChatAgentConfig(
        llm=lm.OpenAIGPTConfig(chat_model="gpt-4o-mini"),
        name="自定義Agent"
    )
)
    '''

    console.print(Panel(code, border_style="blue"))


# ============================================================================
# 示例 3：Agent 對話歷史
# ============================================================================

def conversation_history_example():
    """示例 3：Agent 對話歷史"""
    console.print(Panel("[bold cyan]示例 3：對話歷史管理[/bold cyan]"))

    if not LANGROID_AVAILABLE or not os.getenv("OPENAI_API_KEY"):
        console.print("[yellow]跳過此示例[/yellow]")
        return

    llm_config = lm.OpenAIGPTConfig(chat_model="gpt-4o-mini")

    agent = lr.ChatAgent(
        config=lr.ChatAgentConfig(
            llm=llm_config,
            name="歷史Agent"
        )
    )

    console.print("\n[yellow]對話並查看歷史：[/yellow]\n")

    messages = ["你好", "我叫張三", "我是誰？"]

    for msg in messages:
        console.print(f"[cyan]用戶：[/cyan]{msg}")
        response = agent.llm_response(msg)
        console.print(f"[green]Agent：[/green]{response.content}\n")

    # 查看歷史
    console.print("[yellow]對話歷史長度：[/yellow]", len(agent.message_history))


# ============================================================================
# 示例 4：Agent 配置深入
# ============================================================================

def agent_config_deep_dive():
    """示例 4：Agent 配置深入"""
    console.print(Panel("[bold cyan]示例 4：Agent 配置詳解[/bold cyan]"))

    console.print("""
[yellow]Agent 配置選項：[/yellow]

ChatAgentConfig 主要參數：

1. [cyan]llm[/cyan]: LLM 配置對象
   - 必需參數
   - 決定使用哪個模型

2. [cyan]name[/cyan]: Agent 名稱
   - 用於標識和日誌
   - 在多 Agent 系統中很重要

3. [cyan]system_message[/cyan]: 系統消息
   - 定義 Agent 的角色和行為
   - 相當於給 Agent 的指令

4. [cyan]user_message[/cyan]: 用戶消息模板
   - 可選的消息格式化

5. [cyan]max_context_tokens[/cyan]: 最大上下文 token
   - 控制對話歷史長度
   - 防止超出模型限制

6. [cyan]vecdb[/cyan]: 向量數據庫配置
   - 用於 RAG
   - 可選參數

[yellow]示例配置：[/yellow]
    """)

    example = '''
# 詳細配置
config = lr.ChatAgentConfig(
    llm=lm.OpenAIGPTConfig(
        chat_model="gpt-4o-mini",
        temperature=0.7,
        max_tokens=1000
    ),
    name="專業助手",
    system_message="""
你是一個專業的技術顧問。
你的職責是：
1. 提供準確的技術建議
2. 使用專業術語
3. 給出實用的解決方案
    """,
    max_context_tokens=4000,
)

agent = lr.ChatAgent(config)
    '''

    console.print(Panel(example, border_style="blue"))


# ============================================================================
# 主函數
# ============================================================================

def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold green]Langroid Agent 基礎[/bold green]",
        border_style="green"
    ))

    agent_properties_example()
    console.print("\n" + "="*60 + "\n")

    custom_agent_example()
    console.print("\n" + "="*60 + "\n")

    conversation_history_example()
    console.print("\n" + "="*60 + "\n")

    agent_config_deep_dive()

    console.print(Panel("""
[bold green]Agent 基礎完成！[/bold green]

關鍵要點：
1. Agent 封裝了 LLM 和對話邏輯
2. 可以繼承 ChatAgent 自定義行為
3. Agent 自動管理對話歷史
4. 豐富的配置選項

下一步：
- 查看 03_任務系統.py 學習 Task
- 查看 04_工具使用.py 集成工具
    """, title="總結", border_style="green"))


if __name__ == "__main__":
    main()

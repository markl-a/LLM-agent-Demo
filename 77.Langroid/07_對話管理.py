"""
Langroid 對話管理 - 複雜對話流程

這個示例展示：
1. 對話狀態管理
2. 上下文維護
3. 對話流程控制
4. 多輪對話策略

Langroid 提供強大的對話管理能力。
"""

from rich.console import Console
from rich.panel import Panel

console = Console()


def conversation_state():
    """對話狀態管理"""
    console.print(Panel("[bold cyan]對話狀態管理[/bold cyan]"))

    console.print("""
[yellow]Langroid 自動管理對話狀態：[/yellow]

- 對話歷史自動保存
- 上下文自動維護
- Token 限制自動處理

[yellow]訪問對話歷史：[/yellow]
    """)

    code = '''
import langroid as lr

# 創建 Agent
agent = lr.ChatAgent(config)

# 對話
agent.llm_response("我叫張三")
agent.llm_response("我喜歡編程")
agent.llm_response("我的名字是什麼？")  # Agent 會記住

# 查看歷史
history = agent.message_history
print(f"對話輪次: {len(history)}")

# 清除歷史
agent.clear_history()

# 導出/導入歷史
history_data = agent.export_history()
# 保存到文件...

# 恢復歷史
agent.import_history(history_data)
    '''

    console.print(Panel(code, border_style="blue"))


def context_management():
    """上下文管理"""
    console.print(Panel("[bold cyan]上下文管理[/bold cyan]"))

    console.print("""
[yellow]上下文窗口管理策略：[/yellow]

1. [cyan]自動截斷[/cyan]
   - 超出限制時自動截斷舊消息
   - 保留最近的對話

2. [cyan]摘要壓縮[/cyan]
   - 將舊對話總結
   - 保留關鍵信息

3. [cyan]選擇性保留[/cyan]
   - 保留重要消息
   - 刪除不重要的

[yellow]配置示例：[/yellow]
    """)

    context_code = '''
# 配置上下文管理
config = lr.ChatAgentConfig(
    llm=lr.language_models.OpenAIGPTConfig(
        chat_model="gpt-4o-mini",
    ),
    max_context_tokens=4000,  # 最大上下文 token
)

agent = lr.ChatAgent(config)

# Langroid 會自動：
# 1. 追蹤 token 使用
# 2. 超出限制時截斷
# 3. 保持對話連貫性
    '''

    console.print(Panel(context_code, border_style="blue"))


def conversation_flow():
    """對話流程控制"""
    console.print(Panel("[bold cyan]對話流程控制[/bold cyan]"))

    console.print("""
[yellow]控制對話流程：[/yellow]

使用 Task 的交互模式或編程模式：
    """)

    flow_code = '''
# 方式1：交互模式
task = lr.Task(agent, interactive=True)
task.run()  # 啟動命令行交互

# 方式2：編程控制
task = lr.Task(agent, interactive=False)

conversation_flow = [
    "你好",
    "我需要幫助",
    "請解釋 Python",
]

for user_msg in conversation_flow:
    response = task.run(user_msg)
    print(f"用戶: {user_msg}")
    print(f"助手: {response.content}")

# 方式3：條件控制
task = lr.Task(agent, interactive=False)

while True:
    user_input = get_user_input()

    if user_input.lower() == "退出":
        break

    response = task.run(user_input)

    if should_end_conversation(response):
        break

    display_response(response)
    '''

    console.print(Panel(flow_code, border_style="blue"))


def multi_turn_strategies():
    """多輪對話策略"""
    console.print(Panel("[bold cyan]多輪對話策略[/bold cyan]"))

    console.print("""
[yellow]多輪對話模式：[/yellow]

1. [cyan]信息收集[/cyan]
   - 逐步收集用戶信息
   - 填充表單或結構

2. [cyan]澄清確認[/cyan]
   - 對不確定的內容進行確認
   - 多輪澄清

3. [cyan]任務導向[/cyan]
   - 引導用戶完成特定任務
   - 步驟化流程

[yellow]信息收集示例：[/yellow]
    """)

    strategy_code = '''
class InformationGatherer(lr.ChatAgent):
    """信息收集 Agent"""

    def __init__(self, config):
        super().__init__(config)
        self.collected_info = {}
        self.questions = [
            ("name", "請問您的姓名？"),
            ("age", "您的年齡？"),
            ("email", "您的郵箱？"),
        ]
        self.current_question = 0

    def gather_information(self):
        """收集信息流程"""
        task = lr.Task(self, interactive=False)

        while self.current_question < len(self.questions):
            key, question = self.questions[self.current_question]

            # 詢問
            response = task.run(question)
            answer = response.content

            # 驗證
            if self.validate(key, answer):
                self.collected_info[key] = answer
                self.current_question += 1
            else:
                # 重新詢問
                task.run("請提供有效的信息")

        return self.collected_info

    def validate(self, key, value):
        """驗證輸入"""
        # 驗證邏輯...
        return True

# 使用
gatherer = InformationGatherer(config)
info = gatherer.gather_information()
    '''

    console.print(Panel(strategy_code, border_style="blue"))


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold green]Langroid 對話管理[/bold green]",
        border_style="green"
    ))

    conversation_state()
    console.print("\n" + "="*60 + "\n")

    context_management()
    console.print("\n" + "="*60 + "\n")

    conversation_flow()
    console.print("\n" + "="*60 + "\n")

    multi_turn_strategies()

    console.print(Panel("""
[bold green]對話管理完成！[/bold green]

關鍵要點：
1. 自動管理對話歷史
2. 智能的上下文管理
3. 靈活的流程控制
4. 多種多輪策略

對話管理最佳實踐：
- 設置合理的上下文限制
- 實現對話狀態持久化
- 處理對話超時
- 提供清晰的退出機制

下一步：查看 08_文檔處理.py
    """, title="總結", border_style="green"))


if __name__ == "__main__":
    main()

"""
Langroid 多 Agent - 多 Agent 協作

這個示例展示：
1. 多 Agent 架構
2. Agent 之間的通信
3. 任務委託
4. 協作模式

Langroid 專為多 Agent 系統設計。
"""

from rich.console import Console
from rich.panel import Panel

console = Console()


def multi_agent_basics():
    """多 Agent 基礎"""
    console.print(Panel("[bold cyan]多 Agent 基礎[/bold cyan]"))

    console.print("""
[yellow]多 Agent 架構模式：[/yellow]

1. [cyan]協調器模式[/cyan]
   - 一個主 Agent 協調多個專家 Agent
   - 主 Agent 負責任務分配

2. [cyan]管道模式[/cyan]
   - Agent 按順序處理
   - 每個 Agent 專注一個步驟

3. [cyan]團隊模式[/cyan]
   - 多個 Agent 協作
   - 共同完成複雜任務

[yellow]基本示例：[/yellow]
    """)

    code = '''
import langroid as lr
import langroid.language_models as lm

# 創建協調器 Agent
coordinator = lr.ChatAgent(
    config=lr.ChatAgentConfig(
        llm=lm.OpenAIGPTConfig(chat_model="gpt-4o-mini"),
        name="協調器",
        system_message="""
你是任務協調器。
分析任務並委託給合適的專家。
        """
    )
)

# 創建專家 Agents
tech_expert = lr.ChatAgent(
    config=lr.ChatAgentConfig(
        name="技術專家",
        system_message="你是技術專家，回答技術問題"
    )
)

business_expert = lr.ChatAgent(
    config=lr.ChatAgentConfig(
        name="商業專家",
        system_message="你是商業顧問，提供商業建議"
    )
)

# 創建任務
coord_task = lr.Task(coordinator, name="協調任務")
tech_task = lr.Task(tech_expert, name="技術任務")
business_task = lr.Task(business_expert, name="商業任務")

# 添加子任務
coord_task.add_sub_task(tech_task)
coord_task.add_sub_task(business_task)
    '''

    console.print(Panel(code, border_style="blue"))


def agent_communication():
    """Agent 通信"""
    console.print(Panel("[bold cyan]Agent 通信[/bold cyan]"))

    console.print("""
[yellow]Agent 之間的通信方式：[/yellow]

1. [cyan]任務委託[/cyan]
   - 主任務委託子任務
   - 自動消息路由

2. [cyan]消息傳遞[/cyan]
   - Agent 之間直接傳遞消息
   - 使用結構化消息

3. [cyan]共享狀態[/cyan]
   - 通過共享數據結構
   - 協作完成任務

[yellow]通信示例：[/yellow]
    """)

    comm_code = '''
# 定義消息類型
class TaskAssignment(lr.ToolMessage):
    """任務分配消息"""
    request: str = "task_assignment"
    purpose: str = "分配任務給專家"

    expert_type: str  # "tech" 或 "business"
    task_description: str

    def handle(self) -> str:
        # 路由到相應的專家
        if self.expert_type == "tech":
            return tech_task.run(self.task_description)
        elif self.expert_type == "business":
            return business_task.run(self.task_description)

# 協調器使用消息分配任務
coordinator.enable_message(TaskAssignment)

# 當協調器需要專家時，會發送 TaskAssignment 消息
    '''

    console.print(Panel(comm_code, border_style="blue"))


def collaboration_patterns():
    """協作模式"""
    console.print(Panel("[bold cyan]協作模式[/bold cyan]"))

    console.print("""
[yellow]常見協作模式：[/yellow]

1. [cyan]順序協作[/cyan]
   Agent A -> Agent B -> Agent C
   每個 Agent 處理一個步驟

2. [cyan]並行協作[/cyan]
   多個 Agent 同時處理不同方面
   結果匯總

3. [cyan]辯論模式[/cyan]
   多個 Agent 討論和辯論
   達成共識

4. [cyan]專家會議[/cyan]
   各領域專家提供意見
   協調器整合建議

[yellow]專家會議示例：[/yellow]
    """)

    pattern_code = '''
# 專家會議模式
class ExpertMeeting:
    """專家會議"""

    def __init__(self):
        self.coordinator = lr.ChatAgent(...)
        self.experts = {
            "tech": lr.ChatAgent(...),
            "business": lr.ChatAgent(...),
            "legal": lr.ChatAgent(...),
        }

    def consult(self, question: str) -> str:
        """諮詢所有專家"""
        opinions = {}

        # 收集每個專家的意見
        for name, expert in self.experts.items():
            task = lr.Task(expert, name=f"{name}_task")
            opinion = task.run(question)
            opinions[name] = opinion.content

        # 協調器整合意見
        summary_prompt = f"""
請整合以下專家意見：

{opinions}

給出綜合建議。
        """

        coord_task = lr.Task(self.coordinator)
        result = coord_task.run(summary_prompt)

        return result.content

# 使用
meeting = ExpertMeeting()
advice = meeting.consult("我們應該採用哪種技術棧？")
    '''

    console.print(Panel(pattern_code, border_style="blue"))


def multi_agent_example():
    """完整的多 Agent 示例"""
    console.print(Panel("[bold cyan]完整示例：研究助手[/bold cyan]"))

    console.print("""
[yellow]場景：多 Agent 研究系統[/yellow]

角色：
- 協調器：分析查詢，協調任務
- 搜索專家：查找相關資料
- 分析專家：分析和總結
- 寫作專家：撰寫報告

[yellow]實現：[/yellow]
    """)

    example_code = '''
class ResearchTeam:
    """研究團隊"""

    def __init__(self):
        # 創建各個 Agent
        self.coordinator = lr.ChatAgent(
            config=lr.ChatAgentConfig(
                name="協調器",
                system_message="分析研究問題，協調團隊"
            )
        )

        self.searcher = lr.ChatAgent(
            config=lr.ChatAgentConfig(
                name="搜索專家",
                system_message="查找和檢索相關資料"
            )
        )

        self.analyst = lr.ChatAgent(
            config=lr.ChatAgentConfig(
                name="分析專家",
                system_message="分析數據，提取洞察"
            )
        )

        self.writer = lr.ChatAgent(
            config=lr.ChatAgentConfig(
                name="寫作專家",
                system_message="撰寫清晰的研究報告"
            )
        )

    def research(self, topic: str) -> str:
        """執行研究"""
        # 1. 協調器規劃
        plan = lr.Task(self.coordinator).run(
            f"為主題 '{topic}' 制定研究計劃"
        )

        # 2. 搜索資料
        sources = lr.Task(self.searcher).run(
            f"查找關於 '{topic}' 的資料"
        )

        # 3. 分析
        insights = lr.Task(self.analyst).run(
            f"分析這些資料：{sources.content}"
        )

        # 4. 撰寫報告
        report = lr.Task(self.writer).run(
            f"基於以下分析撰寫報告：{insights.content}"
        )

        return report.content

# 使用
team = ResearchTeam()
report = team.research("量子計算的最新進展")
    '''

    console.print(Panel(example_code, border_style="blue"))


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold green]Langroid 多 Agent[/bold green]",
        border_style="green"
    ))

    multi_agent_basics()
    console.print("\n" + "="*60 + "\n")

    agent_communication()
    console.print("\n" + "="*60 + "\n")

    collaboration_patterns()
    console.print("\n" + "="*60 + "\n")

    multi_agent_example()

    console.print(Panel("""
[bold green]多 Agent 完成！[/bold green]

關鍵要點：
1. Langroid 原生支持多 Agent
2. 靈活的協作模式
3. 清晰的消息傳遞
4. 任務委託機制

多 Agent 設計原則：
- 明確每個 Agent 的角色
- 設計清晰的通信協議
- 避免循環依賴
- 實現錯誤處理

下一步：查看 07_對話管理.py
    """, title="總結", border_style="green"))


if __name__ == "__main__":
    main()

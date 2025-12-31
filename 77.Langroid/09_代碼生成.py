"""
Langroid 代碼生成 - 構建代碼生成助手

這個示例展示：
1. 代碼生成 Agent
2. 代碼審查
3. 代碼解釋
4. 完整的開發助手

使用 Langroid 構建智能代碼助手。
"""

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()


def code_generation_agent():
    """代碼生成 Agent"""
    console.print(Panel("[bold cyan]代碼生成 Agent[/bold cyan]"))

    console.print("""
[yellow]創建代碼生成 Agent：[/yellow]
    """)

    code = '''
import langroid as lr

# 創建代碼生成 Agent
code_agent = lr.ChatAgent(
    config=lr.ChatAgentConfig(
        llm=lr.language_models.OpenAIGPTConfig(
            chat_model="gpt-4o-mini",
            temperature=0.2  # 較低溫度，更確定性
        ),
        name="代碼生成器",
        system_message="""
你是專業的 Python 開發者。
當用戶描述需求時，生成清晰、高效的代碼。

代碼要求：
1. 遵循 PEP 8 規範
2. 包含完整的文檔字符串
3. 添加類型提示
4. 包含錯誤處理
5. 提供使用示例
        """
    )
)

# 使用
task = lr.Task(code_agent, interactive=False)

request = "寫一個函數，計算列表中數字的平均值"
response = task.run(request)

print(response.content)
    '''

    console.print(Panel(code, border_style="blue"))


def code_review_agent():
    """代碼審查 Agent"""
    console.print(Panel("[bold cyan]代碼審查 Agent[/bold cyan]"))

    console.print("""
[yellow]創建代碼審查 Agent：[/yellow]
    """)

    review_code = '''
# 代碼審查 Agent
reviewer = lr.ChatAgent(
    config=lr.ChatAgentConfig(
        name="代碼審查員",
        system_message="""
你是資深代碼審查員。
審查代碼並提供建議：

檢查要點：
1. 代碼正確性
2. 性能問題
3. 安全隱患
4. 代碼風格
5. 最佳實踐

提供：
- 發現的問題
- 改進建議
- 重構方案
        """
    )
)

# 使用
code_to_review = """
def calc_avg(numbers):
    sum = 0
    for num in numbers:
        sum += num
    return sum / len(numbers)
"""

review_task = lr.Task(reviewer, interactive=False)
review = review_task.run(
    f"請審查這段代碼：\\n```python\\n{code_to_review}\\n```"
)

print(review.content)
    '''

    console.print(Panel(review_code, border_style="blue"))


def code_explanation():
    """代碼解釋"""
    console.print(Panel("[bold cyan]代碼解釋 Agent[/bold cyan]"))

    console.print("""
[yellow]創建代碼解釋 Agent：[/yellow]
    """)

    explain_code = '''
# 代碼解釋 Agent
explainer = lr.ChatAgent(
    config=lr.ChatAgentConfig(
        name="代碼講解員",
        system_message="""
你是代碼教學專家。
用淺顯易懂的語言解釋代碼：

解釋包括：
1. 代碼整體功能
2. 逐行解釋關鍵部分
3. 使用的技術和概念
4. 為什麼這樣寫
5. 可能的改進方向
        """
    )
)

# 使用
complex_code = """
@lru_cache(maxsize=128)
def fibonacci(n: int) -> int:
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""

explain_task = lr.Task(explainer, interactive=False)
explanation = explain_task.run(
    f"請解釋這段代碼：\\n```python\\n{complex_code}\\n```"
)

print(explanation.content)
    '''

    console.print(Panel(explain_code, border_style="blue"))


def development_assistant():
    """完整的開發助手"""
    console.print(Panel("[bold cyan]完整的開發助手系統[/bold cyan]"))

    console.print("""
[yellow]多 Agent 開發助手：[/yellow]
    """)

    assistant_code = '''
class DevelopmentAssistant:
    """開發助手系統"""

    def __init__(self):
        # 代碼生成 Agent
        self.generator = lr.ChatAgent(
            config=lr.ChatAgentConfig(
                name="生成器",
                system_message="生成高質量 Python 代碼"
            )
        )

        # 代碼審查 Agent
        self.reviewer = lr.ChatAgent(
            config=lr.ChatAgentConfig(
                name="審查員",
                system_message="審查代碼，提供改進建議"
            )
        )

        # 測試生成 Agent
        self.tester = lr.ChatAgent(
            config=lr.ChatAgentConfig(
                name="測試員",
                system_message="為代碼生成單元測試"
            )
        )

        # 文檔生成 Agent
        self.documenter = lr.ChatAgent(
            config=lr.ChatAgentConfig(
                name="文檔員",
                system_message="生成代碼文檔和註釋"
            )
        )

    def develop_feature(self, requirement: str) -> dict:
        """完整開發流程"""
        results = {}

        # 1. 生成代碼
        gen_task = lr.Task(self.generator, interactive=False)
        code = gen_task.run(requirement)
        results['code'] = code.content

        # 2. 審查代碼
        review_task = lr.Task(self.reviewer, interactive=False)
        review = review_task.run(
            f"審查代碼：\\n{code.content}"
        )
        results['review'] = review.content

        # 3. 生成測試
        test_task = lr.Task(self.tester, interactive=False)
        tests = test_task.run(
            f"為代碼生成測試：\\n{code.content}"
        )
        results['tests'] = tests.content

        # 4. 生成文檔
        doc_task = lr.Task(self.documenter, interactive=False)
        docs = doc_task.run(
            f"為代碼生成文檔：\\n{code.content}"
        )
        results['docs'] = docs.content

        return results

# 使用
assistant = DevelopmentAssistant()
result = assistant.develop_feature(
    "實現一個 LRU 緩存類"
)

print("生成的代碼：")
print(result['code'])
print("\\n審查意見：")
print(result['review'])
print("\\n測試代碼：")
print(result['tests'])
print("\\n文檔：")
print(result['docs'])
    '''

    console.print(Panel(assistant_code, border_style="blue"))


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold green]Langroid 代碼生成[/bold green]",
        border_style="green"
    ))

    code_generation_agent()
    console.print("\n" + "="*60 + "\n")

    code_review_agent()
    console.print("\n" + "="*60 + "\n")

    code_explanation()
    console.print("\n" + "="*60 + "\n")

    development_assistant()

    console.print(Panel("""
[bold green]代碼生成完成！[/bold green]

關鍵要點：
1. 專業的代碼生成 Agent
2. 代碼審查和優化
3. 代碼解釋和教學
4. 完整的開發工作流

代碼助手應用：
- 代碼生成
- 代碼審查
- Bug 修復
- 重構建議
- 測試生成
- 文檔生成

最佳實踐：
- 使用較低溫度提高確定性
- 提供清晰的需求描述
- 多輪迭代優化
- 結合人工審查

下一步：查看 10_企業應用.py
    """, title="總結", border_style="green"))


if __name__ == "__main__":
    main()

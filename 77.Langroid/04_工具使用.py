"""
Langroid 工具使用 - 函數調用和工具集成

這個示例展示：
1. 定義工具
2. 綁定工具到 Agent
3. 工具調用流程
4. 結構化輸出

Langroid 提供優雅的工具調用機制。
"""

import os
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from pydantic import BaseModel, Field

try:
    import langroid as lr
    import langroid.language_models as lm
    LANGROID_AVAILABLE = True
except ImportError:
    LANGROID_AVAILABLE = False

console = Console()
load_dotenv()


# ============================================================================
# 示例 1：定義工具
# ============================================================================

def tool_definition_example():
    """示例 1：定義工具"""
    console.print(Panel("[bold cyan]示例 1：定義工具[/bold cyan]"))

    console.print("""
[yellow]在 Langroid 中定義工具：[/yellow]

使用 Pydantic 模型定義工具：
    """)

    code = '''
from pydantic import BaseModel, Field
import langroid as lr

# 定義工具
class CalculatorTool(lr.ToolMessage):
    """計算器工具"""

    request: str = "calculator"  # 工具名稱
    purpose: str = "進行數學計算"  # 工具用途

    operation: str = Field(..., description="運算類型: add, subtract, multiply, divide")
    x: float = Field(..., description="第一個數字")
    y: float = Field(..., description="第二個數字")

    def handle(self) -> str:
        """處理工具調用"""
        if self.operation == "add":
            result = self.x + self.y
        elif self.operation == "subtract":
            result = self.x - self.y
        elif self.operation == "multiply":
            result = self.x * self.y
        elif self.operation == "divide":
            result = self.x / self.y if self.y != 0 else "錯誤：除以零"
        else:
            result = "未知運算"

        return f"計算結果: {result}"

# 使用工具
tool = CalculatorTool(operation="add", x=5, y=3)
result = tool.handle()
print(result)  # 計算結果: 8.0
    '''

    console.print(Panel(code, border_style="blue"))


# ============================================================================
# 示例 2：綁定工具到 Agent
# ============================================================================

def tool_binding_example():
    """示例 2：綁定工具到 Agent"""
    console.print(Panel("[bold cyan]示例 2：綁定工具到 Agent[/bold cyan]"))

    console.print("""
[yellow]將工具綁定到 Agent：[/yellow]
    """)

    binding_code = '''
# 定義工具
class SearchTool(lr.ToolMessage):
    """搜索工具"""
    request: str = "search"
    purpose: str = "搜索信息"
    query: str = Field(..., description="搜索查詢")

    def handle(self) -> str:
        # 實際的搜索邏輯
        return f"搜索結果: {self.query}"

# 創建 Agent 配置
config = lr.ChatAgentConfig(
    llm=lm.OpenAIGPTConfig(chat_model="gpt-4o-mini"),
    system_message="""
你是一個助手，可以使用搜索工具。
當需要查找信息時，使用 search 工具。
    """
)

# 創建 Agent
agent = lr.ChatAgent(config)

# 啟用工具
agent.enable_message(SearchTool)

# 使用
task = lr.Task(agent, name="搜索任務")
result = task.run("請搜索 Python 教程")
    '''

    console.print(Panel(binding_code, border_style="blue"))


# ============================================================================
# 示例 3：結構化輸出
# ============================================================================

def structured_output_example():
    """示例 3：結構化輸出"""
    console.print(Panel("[bold cyan]示例 3：結構化輸出[/bold cyan]"))

    console.print("""
[yellow]使用 Pydantic 模型定義輸出結構：[/yellow]
    """)

    structured_code = '''
from pydantic import BaseModel

# 定義輸出結構
class UserInfo(BaseModel):
    """用戶信息"""
    name: str
    age: int
    email: str
    interests: list[str]

# 創建 Agent
agent = lr.ChatAgent(
    config=lr.ChatAgentConfig(
        llm=lm.OpenAIGPTConfig(chat_model="gpt-4o-mini"),
        system_message="從文本中提取用戶信息"
    )
)

# 啟用結構化輸出
agent.enable_message(UserInfo)

# 使用
text = "我叫張三，25歲，郵箱是 zhang@example.com，喜歡編程和閱讀"
result = agent.llm_response(text)

# result 會是 UserInfo 對象
user = result.content  # UserInfo 實例
print(f"姓名: {user.name}")
print(f"年齡: {user.age}")
    '''

    console.print(Panel(structured_code, border_style="blue"))


# ============================================================================
# 示例 4：多工具組合
# ============================================================================

def multi_tool_example():
    """示例 4：多工具組合"""
    console.print(Panel("[bold cyan]示例 4：多工具組合[/bold cyan]"))

    console.print("""
[yellow]Agent 可以使用多個工具：[/yellow]
    """)

    multi_code = '''
# 定義多個工具
class CalculatorTool(lr.ToolMessage):
    request: str = "calculator"
    # ... 計算器實現

class SearchTool(lr.ToolMessage):
    request: str = "search"
    # ... 搜索實現

class WeatherTool(lr.ToolMessage):
    request: str = "weather"
    # ... 天氣實現

# 創建 Agent
agent = lr.ChatAgent(config)

# 啟用多個工具
agent.enable_message(CalculatorTool)
agent.enable_message(SearchTool)
agent.enable_message(WeatherTool)

# Agent 會根據需要自動選擇合適的工具
task = lr.Task(agent, name="多工具任務")
result = task.run("計算 5+3，然後搜索結果的含義")
    '''

    console.print(Panel(multi_code, border_style="blue"))


# ============================================================================
# 主函數
# ============================================================================

def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold green]Langroid 工具使用[/bold green]",
        border_style="green"
    ))

    tool_definition_example()
    console.print("\n" + "="*60 + "\n")

    tool_binding_example()
    console.print("\n" + "="*60 + "\n")

    structured_output_example()
    console.print("\n" + "="*60 + "\n")

    multi_tool_example()

    console.print(Panel("""
[bold green]工具使用完成！[/bold green]

關鍵要點：
1. 使用 ToolMessage 定義工具
2. enable_message() 綁定工具
3. Pydantic 提供類型安全
4. 支持多工具組合
5. 自動解析和調用

Langroid 工具優勢：
- 優雅的定義方式
- 類型安全
- 自動解析
- 靈活組合

下一步：查看 05_向量存儲.py
    """, title="總結", border_style="green"))


if __name__ == "__main__":
    main()

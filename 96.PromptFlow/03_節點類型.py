"""
PromptFlow 節點類型示例

本示例展示：
1. Python 節點
2. LLM 節點
3. Prompt 節點
4. Tool 節點
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax

console = Console()


def show_python_node():
    """Python 節點示例"""
    console.print("\n[cyan]1. Python 節點[/cyan]\n")

    console.print("[yellow]用途:[/yellow] 執行自定義 Python 代碼，進行數據處理、轉換等操作\n")

    # 節點配置
    config = """nodes:
  - name: process_data
    type: python
    source:
      type: code
      path: process.py
    inputs:
      data: ${inputs.data}
      threshold: 0.5"""

    syntax = Syntax(config, "yaml", theme="monokai", line_numbers=True)
    console.print("[dim]配置示例:[/dim]")
    console.print(syntax)
    console.print()

    # Python 代碼
    code = """from promptflow import tool
from typing import List, Dict

@tool
def process_data(data: List[Dict], threshold: float) -> List[Dict]:
    \"\"\"過濾和處理數據\"\"\"
    # 過濾數據
    filtered = [item for item in data if item.get('score', 0) > threshold]

    # 添加處理標記
    for item in filtered:
        item['processed'] = True
        item['normalized_score'] = item['score'] / 100

    return filtered"""

    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print("[dim]Python 代碼 (process.py):[/dim]")
    console.print(syntax)
    console.print()


def show_llm_node():
    """LLM 節點示例"""
    console.print("[cyan]2. LLM 節點[/cyan]\n")

    console.print("[yellow]用途:[/yellow] 調用大型語言模型，進行文本生成、問答等任務\n")

    # 節點配置
    config = """nodes:
  - name: generate_answer
    type: llm
    source:
      type: code
      path: answer_prompt.jinja2
    inputs:
      question: ${inputs.question}
      context: ${retrieve_context.output}
    connection: azure_openai_connection
    api: chat
    deployment_name: gpt-4
    temperature: 0.7
    max_tokens: 500
    top_p: 0.95
    stop: ["\\n\\n"]"""

    syntax = Syntax(config, "yaml", theme="monokai", line_numbers=True)
    console.print("[dim]配置示例:[/dim]")
    console.print(syntax)
    console.print()

    # Prompt 模板
    template = """system:
你是一個專業的問答助手。請基於提供的上下文回答用戶問題。

規則：
1. 只使用上下文中的信息回答
2. 如果上下文不包含答案，請誠實說明
3. 回答要簡潔、準確

上下文：
{{ context }}

user:
{{ question }}"""

    syntax = Syntax(template, "jinja2", theme="monokai", line_numbers=True)
    console.print("[dim]Prompt 模板 (answer_prompt.jinja2):[/dim]")
    console.print(syntax)
    console.print()


def show_prompt_node():
    """Prompt 節點示例"""
    console.print("[cyan]3. Prompt 節點[/cyan]\n")

    console.print("[yellow]用途:[/yellow] 構建和格式化提示文本，不調用 LLM\n")

    # 節點配置
    config = """nodes:
  - name: build_prompt
    type: prompt
    source:
      type: code
      path: build_prompt.jinja2
    inputs:
      user_query: ${inputs.query}
      examples: ${load_examples.output}
      history: ${get_history.output}"""

    syntax = Syntax(config, "yaml", theme="monokai", line_numbers=True)
    console.print("[dim]配置示例:[/dim]")
    console.print(syntax)
    console.print()

    # Prompt 模板
    template = """{% if history %}
對話歷史：
{% for item in history %}
用戶: {{ item.user }}
助手: {{ item.assistant }}
{% endfor %}
{% endif %}

{% if examples %}
參考示例：
{% for example in examples %}
問題: {{ example.question }}
答案: {{ example.answer }}
{% endfor %}
{% endif %}

當前問題：
{{ user_query }}"""

    syntax = Syntax(template, "jinja2", theme="monokai", line_numbers=True)
    console.print("[dim]Prompt 模板 (build_prompt.jinja2):[/dim]")
    console.print(syntax)
    console.print()


def show_tool_node():
    """Tool 節點示例"""
    console.print("[cyan]4. Tool 節點[/cyan]\n")

    console.print("[yellow]用途:[/yellow] 調用內置或自定義工具，如搜索、計算等\n")

    # 內置工具配置
    config1 = """nodes:
  # 使用內置的向量搜索工具
  - name: search_docs
    type: python
    source:
      type: package
      tool: promptflow_vectordb.tool.vector_db_lookup.VectorDBLookup.search
    inputs:
      connection: weaviate_connection
      index_name: knowledge_base
      text: ${inputs.question}
      top_k: 3"""

    syntax = Syntax(config1, "yaml", theme="monokai", line_numbers=True)
    console.print("[dim]內置工具示例:[/dim]")
    console.print(syntax)
    console.print()

    # 自定義工具配置
    config2 = """nodes:
  # 自定義計算工具
  - name: calculate
    type: python
    source:
      type: code
      path: calculator.py
    inputs:
      expression: ${inputs.math_expression}"""

    syntax = Syntax(config2, "yaml", theme="monokai", line_numbers=True)
    console.print("[dim]自定義工具示例:[/dim]")
    console.print(syntax)
    console.print()

    # 工具代碼
    code = """from promptflow import tool
import math
import re

@tool
def calculate(expression: str) -> dict:
    \"\"\"安全的數學計算工具\"\"\"
    try:
        # 清理輸入
        expr = re.sub(r'[^0-9+\\-*/()\\s.]', '', expression)

        # 安全的計算環境
        allowed_names = {
            'sqrt': math.sqrt,
            'pow': math.pow,
            'abs': abs,
            'round': round,
        }

        # 計算結果
        result = eval(expr, {"__builtins__": {}}, allowed_names)

        return {
            "success": True,
            "result": result,
            "expression": expression
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "expression": expression
        }"""

    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print("[dim]工具代碼 (calculator.py):[/dim]")
    console.print(syntax)
    console.print()


def show_node_comparison():
    """節點類型對比"""
    console.print("[cyan]節點類型對比[/cyan]\n")

    table = Table(title="節點類型特性對比")
    table.add_column("節點類型", style="cyan")
    table.add_column("主要用途", style="yellow")
    table.add_column("輸入輸出", style="green")
    table.add_column("成本", style="magenta")

    table.add_row(
        "Python",
        "數據處理、邏輯運算",
        "靈活的類型",
        "無額外成本"
    )
    table.add_row(
        "LLM",
        "文本生成、理解",
        "文本輸入輸出",
        "按 token 計費"
    )
    table.add_row(
        "Prompt",
        "提示構建、格式化",
        "文本模板",
        "無額外成本"
    )
    table.add_row(
        "Tool",
        "專用功能調用",
        "依工具而定",
        "依工具而定"
    )

    console.print(table)
    console.print()


def show_advanced_features():
    """高級特性"""
    console.print("[cyan]節點高級特性[/cyan]\n")

    features = """1. 變體（Variants）
   - 為節點創建多個變體
   - 用於 A/B 測試
   - 配置示例：

nodes:
  - name: llm_node
    type: llm
    variants:
      variant_0:
        temperature: 0.7
      variant_1:
        temperature: 0.3

2. 激活條件（Activate When）
   - 條件執行節點
   - 動態流程控制
   - 配置示例：

nodes:
  - name: fallback_node
    type: python
    activate:
      when: ${main_node.output} is None
      is: true

3. 重試策略（Retry）
   - 自動重試失敗的節點
   - 指數退避
   - 配置示例：

nodes:
  - name: api_call
    type: python
    retry:
      max_retries: 3
      delay: 1
      backoff: 2

4. 超時控制（Timeout）
   - 設置節點執行超時
   - 防止長時間阻塞
   - 配置示例：

nodes:
  - name: long_running
    type: python
    timeout: 30  # 秒
"""

    console.print(Panel(features, border_style="cyan"))
    console.print()


def show_common_patterns():
    """常見使用模式"""
    console.print("[cyan]常見節點組合模式[/cyan]\n")

    patterns = [
        ("RAG 模式", "Prompt → Tool(Search) → LLM"),
        ("預處理模式", "Python(Clean) → Python(Transform) → LLM"),
        ("後處理模式", "LLM → Python(Parse) → Python(Validate)"),
        ("並行分析", "Input → [LLM1, LLM2, LLM3] → Python(Merge)"),
        ("多輪對話", "Python(History) → LLM → Python(Save)"),
        ("錯誤處理", "LLM → Python(Check) → Fallback(LLM2)"),
    ]

    table = Table(title="節點組合模式")
    table.add_column("模式名稱", style="cyan")
    table.add_column("節點流程", style="yellow")

    for pattern, flow in patterns:
        table.add_row(pattern, flow)

    console.print(table)
    console.print()


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]PromptFlow 節點類型示例[/bold cyan]\n"
        "[dim]了解各種節點類型及其用法[/dim]",
        border_style="cyan"
    ))

    # 1. Python 節點
    show_python_node()

    # 2. LLM 節點
    show_llm_node()

    # 3. Prompt 節點
    show_prompt_node()

    # 4. Tool 節點
    show_tool_node()

    # 5. 節點對比
    show_node_comparison()

    # 6. 高級特性
    show_advanced_features()

    # 7. 常見模式
    show_common_patterns()

    # 完成
    console.print("="*60)
    console.print("[bold green]✓ 節點類型示例完成！[/bold green]\n")
    console.print("[cyan]下一步:[/cyan]")
    console.print("  1. 查看 04_變量傳遞.py - 學習節點間數據傳遞")
    console.print("  2. 查看 05_條件分支.py - 學習條件邏輯")
    console.print("  3. 實踐: 組合不同節點類型創建複雜 Flow")


if __name__ == "__main__":
    main()

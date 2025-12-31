"""
PromptFlow 變量傳遞示例

本示例展示：
1. 輸入參數傳遞
2. 節點輸出引用
3. 對象字段訪問
4. 複雜數據結構
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.tree import Tree

console = Console()


def show_basic_reference():
    """基本引用語法"""
    console.print("\n[cyan]1. 基本變量引用[/cyan]\n")

    console.print("[yellow]引用語法:[/yellow] 使用 ${} 包裹變量路徑\n")

    examples = [
        ("${inputs.question}", "引用 Flow 的輸入參數 question"),
        ("${node1.output}", "引用 node1 節點的輸出"),
        ("${node2.output.field}", "引用 node2 輸出的 field 字段"),
        ("${node3.output[0]}", "引用 node3 輸出數組的第一個元素"),
    ]

    table = Table(title="引用語法示例")
    table.add_column("語法", style="cyan", no_wrap=True)
    table.add_column("說明", style="yellow")

    for syntax, desc in examples:
        table.add_row(syntax, desc)

    console.print(table)
    console.print()


def show_input_passing():
    """輸入參數傳遞"""
    console.print("[cyan]2. 輸入參數傳遞[/cyan]\n")

    config = """# Flow 配置
inputs:
  user_query:
    type: string
  temperature:
    type: number
    default: 0.7
  max_tokens:
    type: int
    default: 500

nodes:
  # 節點 1: 使用所有輸入參數
  - name: llm_call
    type: llm
    source:
      type: code
      path: prompt.jinja2
    inputs:
      # 直接引用輸入參數
      query: ${inputs.user_query}
      temp: ${inputs.temperature}
      tokens: ${inputs.max_tokens}"""

    syntax = Syntax(config, "yaml", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def show_node_output_passing():
    """節點輸出傳遞"""
    console.print("[cyan]3. 節點輸出傳遞（鏈式）[/cyan]\n")

    config = """nodes:
  # 節點 1: 預處理
  - name: preprocess
    type: python
    source:
      type: code
      path: preprocess.py
    inputs:
      text: ${inputs.raw_text}

  # 節點 2: 使用節點 1 的輸出
  - name: analyze
    type: python
    source:
      type: code
      path: analyze.py
    inputs:
      # 引用 preprocess 的輸出
      processed_text: ${preprocess.output}

  # 節點 3: 使用節點 2 的輸出
  - name: format_result
    type: python
    source:
      type: code
      path: format.py
    inputs:
      # 引用 analyze 的輸出
      analysis: ${analyze.output}"""

    syntax = Syntax(config, "yaml", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()

    # 顯示數據流
    console.print("[yellow]數據流向:[/yellow]")
    tree = Tree("📊 數據傳遞鏈")
    tree.add("inputs.raw_text → preprocess.output")
    tree.add("preprocess.output → analyze.output")
    tree.add("analyze.output → format_result.output")
    console.print(tree)
    console.print()


def show_parallel_passing():
    """並行節點數據傳遞"""
    console.print("[cyan]4. 並行節點數據傳遞[/cyan]\n")

    config = """nodes:
  # 並行處理多個任務
  - name: extract_entities
    type: python
    inputs:
      text: ${inputs.document}

  - name: sentiment_analysis
    type: python
    inputs:
      text: ${inputs.document}

  - name: summarize
    type: python
    inputs:
      text: ${inputs.document}

  # 合併所有結果
  - name: combine_results
    type: python
    inputs:
      # 引用多個並行節點的輸出
      entities: ${extract_entities.output}
      sentiment: ${sentiment_analysis.output}
      summary: ${summarize.output}"""

    syntax = Syntax(config, "yaml", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()

    # 顯示並行結構
    console.print("[yellow]並行數據流:[/yellow]")
    tree = Tree("📊 並行處理")
    input_node = tree.add("inputs.document")
    parallel = tree.add("⚡ 並行分發")
    parallel.add("extract_entities.output")
    parallel.add("sentiment_analysis.output")
    parallel.add("summarize.output")
    tree.add("combine_results (合併所有輸出)")
    console.print(tree)
    console.print()


def show_object_field_access():
    """對象字段訪問"""
    console.print("[cyan]5. 對象字段訪問[/cyan]\n")

    # Python 代碼示例
    code = """from promptflow import tool
from typing import Dict

@tool
def get_user_info(user_id: str) -> Dict:
    \"\"\"返回用戶信息對象\"\"\"
    return {
        "id": user_id,
        "name": "張三",
        "profile": {
            "age": 30,
            "city": "台北"
        },
        "tags": ["VIP", "活躍用戶"]
    }"""

    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print("[dim]節點返回對象:[/dim]")
    console.print(syntax)
    console.print()

    # 引用配置
    config = """nodes:
  - name: get_user
    type: python
    source:
      type: code
      path: get_user.py
    inputs:
      user_id: ${inputs.user_id}

  - name: process_user
    type: python
    inputs:
      # 訪問頂層字段
      user_name: ${get_user.output.name}
      # 訪問嵌套字段
      user_age: ${get_user.output.profile.age}
      user_city: ${get_user.output.profile.city}
      # 訪問數組元素
      first_tag: ${get_user.output.tags[0]}"""

    syntax = Syntax(config, "yaml", theme="monokai", line_numbers=True)
    console.print("[dim]字段訪問配置:[/dim]")
    console.print(syntax)
    console.print()


def show_complex_data_structures():
    """複雜數據結構"""
    console.print("[cyan]6. 複雜數據結構傳遞[/cyan]\n")

    # 返回列表的節點
    code1 = """from promptflow import tool
from typing import List, Dict

@tool
def search_documents(query: str, top_k: int = 3) -> List[Dict]:
    \"\"\"返回文檔列表\"\"\"
    return [
        {
            "id": 1,
            "title": "文檔 1",
            "score": 0.95,
            "content": "相關內容..."
        },
        {
            "id": 2,
            "title": "文檔 2",
            "score": 0.87,
            "content": "其他內容..."
        }
    ]"""

    syntax = Syntax(code1, "python", theme="monokai", line_numbers=True)
    console.print("[dim]返回列表的節點:[/dim]")
    console.print(syntax)
    console.print()

    # 處理列表的節點
    code2 = """from promptflow import tool
from typing import List, Dict

@tool
def process_results(docs: List[Dict]) -> str:
    \"\"\"處理文檔列表\"\"\"
    # 可以直接接收整個列表
    combined = "\\n\\n".join([
        f"{doc['title']}: {doc['content']}"
        for doc in docs
    ])
    return combined"""

    syntax = Syntax(code2, "python", theme="monokai", line_numbers=True)
    console.print("[dim]處理列表的節點:[/dim]")
    console.print(syntax)
    console.print()

    # Flow 配置
    config = """nodes:
  - name: search
    type: python
    source:
      type: code
      path: search.py
    inputs:
      query: ${inputs.question}
      top_k: 3

  - name: process
    type: python
    source:
      type: code
      path: process.py
    inputs:
      # 傳遞整個列表
      docs: ${search.output}"""

    syntax = Syntax(config, "yaml", theme="monokai", line_numbers=True)
    console.print("[dim]Flow 配置:[/dim]")
    console.print(syntax)
    console.print()


def show_default_values():
    """默認值和可選參數"""
    console.print("[cyan]7. 默認值和可選參數[/cyan]\n")

    config = """inputs:
  # 必需參數
  query:
    type: string

  # 可選參數（有默認值）
  language:
    type: string
    default: "zh-TW"

  temperature:
    type: number
    default: 0.7

  max_results:
    type: int
    default: 5

nodes:
  - name: process
    type: python
    inputs:
      # 使用輸入參數（如果用戶沒提供，使用默認值）
      query: ${inputs.query}
      lang: ${inputs.language}
      temp: ${inputs.temperature}
      limit: ${inputs.max_results}"""

    syntax = Syntax(config, "yaml", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def show_output_mapping():
    """輸出映射"""
    console.print("[cyan]8. Flow 輸出映射[/cyan]\n")

    config = """outputs:
  # 簡單輸出
  answer:
    type: string
    reference: ${llm_node.output}

  # 對象輸出
  result:
    type: object
    reference: ${process_node.output}

  # 映射多個字段
  summary:
    type: string
    reference: ${summarize.output.text}

  score:
    type: number
    reference: ${evaluate.output.score}

  metadata:
    type: object
    reference: ${evaluate.output.metadata}"""

    syntax = Syntax(config, "yaml", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def show_best_practices():
    """最佳實踐"""
    console.print("[cyan]變量傳遞最佳實踐[/cyan]\n")

    practices = """1. 類型一致性
   - 確保傳遞的數據類型與接收節點期望的類型一致
   - 使用 Python 類型註解明確定義

2. 避免過深嵌套
   - 限制對象嵌套層級，提高可讀性
   - 必要時在 Python 節點中展平結構

3. 明確命名
   - 使用描述性的變量名
   - 節點輸出字段名要有意義

4. 錯誤處理
   - 檢查可能為空的字段
   - 提供合理的默認值

5. 文檔註釋
   - 在節點函數中註釋輸入輸出類型
   - 在 Flow 配置中添加描述

示例：
@tool
def process_data(
    input_text: str,      # 必需參數
    max_length: int = 100  # 可選參數
) -> Dict[str, Any]:       # 明確返回類型
    \"\"\"
    處理文本數據

    Args:
        input_text: 輸入文本
        max_length: 最大長度

    Returns:
        包含處理結果的字典
    \"\"\"
    pass
"""

    console.print(Panel(practices, border_style="cyan"))
    console.print()


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]PromptFlow 變量傳遞示例[/bold cyan]\n"
        "[dim]學習節點間的數據傳遞[/dim]",
        border_style="cyan"
    ))

    # 1. 基本引用
    show_basic_reference()

    # 2. 輸入傳遞
    show_input_passing()

    # 3. 節點輸出傳遞
    show_node_output_passing()

    # 4. 並行傳遞
    show_parallel_passing()

    # 5. 對象字段訪問
    show_object_field_access()

    # 6. 複雜數據結構
    show_complex_data_structures()

    # 7. 默認值
    show_default_values()

    # 8. 輸出映射
    show_output_mapping()

    # 9. 最佳實踐
    show_best_practices()

    # 完成
    console.print("="*60)
    console.print("[bold green]✓ 變量傳遞示例完成！[/bold green]\n")
    console.print("[cyan]下一步:[/cyan]")
    console.print("  1. 查看 05_條件分支.py - 學習條件邏輯")
    console.print("  2. 查看 06_批量運行.py - 學習批量處理")
    console.print("  3. 實踐: 構建複雜的數據流 Flow")


if __name__ == "__main__":
    main()

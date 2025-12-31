"""
Claude Code SDK 代碼執行示例

本示例展示：
1. 代碼生成
2. 代碼執行（安全沙箱）
3. 代碼分析和優化
4. 交互式編程助手
"""

import os
import sys
import io
import traceback
from contextlib import redirect_stdout, redirect_stderr
from anthropic import Anthropic
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from dotenv import load_dotenv

console = Console()
load_dotenv()


def safe_execute_python(code: str, timeout: int = 5) -> dict:
    """安全執行 Python 代碼"""
    # 創建受限的全局命名空間
    safe_globals = {
        "__builtins__": {
            "print": print,
            "len": len,
            "range": range,
            "str": str,
            "int": int,
            "float": float,
            "list": list,
            "dict": dict,
            "set": set,
            "tuple": tuple,
            "sum": sum,
            "max": max,
            "min": min,
            "abs": abs,
            "round": round,
        }
    }

    # 捕獲輸出
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()

    result = {
        "success": False,
        "output": "",
        "error": "",
        "return_value": None
    }

    try:
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            # 執行代碼
            exec(code, safe_globals)

        result["success"] = True
        result["output"] = stdout_capture.getvalue()

    except Exception as e:
        result["success"] = False
        result["error"] = traceback.format_exc()

    return result


def demo_code_generation():
    """代碼生成示例"""
    console.print("\n[bold cyan]1. 代碼生成[/bold cyan]\n")

    client = Anthropic()

    # 請求代碼生成
    prompt = "寫一個 Python 函數，計算斐波那契數列的第 n 項"

    console.print(f"[yellow]需求：[/yellow] {prompt}\n")

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    response = message.content[0].text
    console.print(Panel(response, title="生成的代碼", border_style="green"))
    console.print()


def demo_code_execution():
    """代碼執行示例"""
    console.print("[bold cyan]2. 代碼執行[/bold cyan]\n")

    # 示例代碼
    code = """
# 計算前 10 個斐波那契數
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")
"""

    console.print("[yellow]執行代碼：[/yellow]")
    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, border_style="cyan"))

    # 執行
    console.print("\n[yellow]執行結果：[/yellow]")
    result = safe_execute_python(code)

    if result["success"]:
        console.print(Panel(result["output"], title="輸出", border_style="green"))
    else:
        console.print(Panel(result["error"], title="錯誤", border_style="red"))

    console.print()


def demo_code_debug():
    """代碼調試示例"""
    console.print("[bold cyan]3. 代碼調試[/bold cyan]\n")

    client = Anthropic()

    # 有 bug 的代碼
    buggy_code = """
def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)

# 測試
print(calculate_average([]))  # 這裡會出錯
"""

    console.print("[yellow]有問題的代碼：[/yellow]")
    syntax = Syntax(buggy_code, "python", theme="monokai")
    console.print(Panel(syntax, border_style="red"))

    # 執行並捕獲錯誤
    result = safe_execute_python(buggy_code)

    if not result["success"]:
        console.print("\n[red]執行錯誤：[/red]")
        console.print(Panel(result["error"][:200], border_style="red"))

        # 請求 Claude 修復
        debug_prompt = f"""
以下代碼執行時出現錯誤：

```python
{buggy_code}
```

錯誤信息：
```
{result["error"]}
```

請修復這個問題並解釋原因。
"""

        console.print("\n[yellow]請求 Claude 修復...[/yellow]\n")

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[{"role": "user", "content": debug_prompt}]
        )

        console.print(Panel(message.content[0].text, title="修復建議", border_style="green"))

    console.print()


def demo_code_optimization():
    """代碼優化示例"""
    console.print("[bold cyan]4. 代碼優化[/bold cyan]\n")

    client = Anthropic()

    # 低效代碼
    inefficient_code = """
def find_duplicates(lst):
    duplicates = []
    for i in range(len(lst)):
        for j in range(i+1, len(lst)):
            if lst[i] == lst[j] and lst[i] not in duplicates:
                duplicates.append(lst[i])
    return duplicates

# 測試
numbers = [1, 2, 3, 2, 4, 5, 3, 6]
print(find_duplicates(numbers))
"""

    console.print("[yellow]原始代碼（O(n²)）：[/yellow]")
    syntax = Syntax(inefficient_code, "python", theme="monokai")
    console.print(Panel(syntax, border_style="yellow"))

    # 請求優化
    optimize_prompt = f"""
請優化以下代碼的性能：

```python
{inefficient_code}
```

提供優化後的版本並解釋改進之處。
"""

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[{"role": "user", "content": optimize_prompt}]
    )

    console.print("\n[green]優化建議：[/green]")
    console.print(Panel(message.content[0].text, border_style="green"))
    console.print()


def demo_interactive_coding():
    """交互式編程示例"""
    console.print("[bold cyan]5. 交互式編程助手[/bold cyan]\n")

    client = Anthropic()

    # 模擬交互式編程會話
    conversation = [
        ("創建一個列表推導式，生成 1-10 的平方", "user"),
        ("", "assistant"),  # 會被填充
        ("現在過濾出偶數的平方", "user"),
        ("", "assistant"),  # 會被填充
    ]

    messages = []

    for i in range(0, len(conversation), 2):
        user_request, _ = conversation[i]

        console.print(f"[blue]開發者：[/blue] {user_request}")

        messages.append({"role": "user", "content": user_request})

        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=512,
            messages=messages
        )

        assistant_response = response.content[0].text
        messages.append({"role": "assistant", "content": assistant_response})

        console.print(f"[green]Claude：[/green] {assistant_response[:200]}...\n")


def demo_code_review():
    """代碼審查示例"""
    console.print("[bold cyan]6. 代碼審查[/bold cyan]\n")

    client = Anthropic()

    code_to_review = """
def process_data(data):
    result = []
    for i in data:
        if i > 0:
            result.append(i * 2)
    return result

def main():
    data = [1, -2, 3, -4, 5]
    output = process_data(data)
    print(output)

main()
"""

    review_aspects = [
        "代碼風格和可讀性",
        "性能問題",
        "潛在的 bug",
        "改進建議",
    ]

    console.print("[yellow]待審查的代碼：[/yellow]")
    syntax = Syntax(code_to_review, "python", theme="monokai")
    console.print(Panel(syntax, border_style="cyan"))

    review_prompt = f"""
請審查以下代碼，關注：
{', '.join(review_aspects)}

```python
{code_to_review}
```

提供詳細的審查報告。
"""

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[{"role": "user", "content": review_prompt}]
    )

    console.print("\n[green]審查報告：[/green]")
    console.print(Panel(message.content[0].text, border_style="green"))
    console.print()


def demo_test_generation():
    """測試生成示例"""
    console.print("[bold cyan]7. 測試用例生成[/bold cyan]\n")

    client = Anthropic()

    function_code = """
def is_palindrome(s):
    '''檢查字符串是否為回文'''
    s = s.lower().replace(' ', '')
    return s == s[::-1]
"""

    console.print("[yellow]目標函數：[/yellow]")
    syntax = Syntax(function_code, "python", theme="monokai")
    console.print(Panel(syntax, border_style="cyan"))

    test_prompt = f"""
為以下函數生成完整的單元測試（使用 pytest）：

```python
{function_code}
```

包括正常情況、邊界情況和異常情況的測試。
"""

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[{"role": "user", "content": test_prompt}]
    )

    console.print("\n[green]生成的測試：[/green]")
    console.print(Panel(message.content[0].text, border_style="green"))
    console.print()


def demo_code_explanation():
    """代碼解釋示例"""
    console.print("[bold cyan]8. 代碼解釋[/bold cyan]\n")

    client = Anthropic()

    complex_code = """
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)
"""

    console.print("[yellow]需要解釋的代碼：[/yellow]")
    syntax = Syntax(complex_code, "python", theme="monokai")
    console.print(Panel(syntax, border_style="cyan"))

    explain_prompt = f"""
請解釋以下代碼的工作原理，包括：
1. 算法思路
2. 每一步在做什麼
3. 時間複雜度

```python
{complex_code}
```
"""

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[{"role": "user", "content": explain_prompt}]
    )

    console.print("\n[green]代碼解釋：[/green]")
    console.print(Panel(message.content[0].text, border_style="green"))
    console.print()


def show_safety_notes():
    """安全注意事項"""
    console.print("[bold cyan]代碼執行安全注意事項[/bold cyan]\n")

    safety_tips = [
        ("限制權限", "只允許安全的內建函數"),
        ("沙箱環境", "使用隔離的執行環境"),
        ("超時控制", "設置執行時間限制"),
        ("資源限制", "限制內存和 CPU 使用"),
        ("輸入驗證", "驗證和清理用戶輸入"),
        ("審計日誌", "記錄所有代碼執行"),
    ]

    for tip, description in safety_tips:
        console.print(f"[red]⚠️  {tip}：[/red]{description}")

    console.print()


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Claude Code SDK 代碼執行[/bold cyan]\n"
        "[dim]學習如何使用 Claude 生成、執行和優化代碼[/dim]",
        border_style="cyan"
    ))

    # 1. 代碼生成
    demo_code_generation()

    # 2. 代碼執行
    demo_code_execution()

    # 3. 代碼調試
    demo_code_debug()

    # 4. 代碼優化
    demo_code_optimization()

    # 5. 交互式編程
    demo_interactive_coding()

    # 6. 代碼審查
    demo_code_review()

    # 7. 測試生成
    demo_test_generation()

    # 8. 代碼解釋
    demo_code_explanation()

    # 安全注意事項
    show_safety_notes()

    # 完成
    console.print("="*60)
    console.print("[bold green]✓ 代碼執行示例完成！[/bold green]")
    console.print("\n[cyan]關鍵要點：[/cyan]")
    console.print("  • Claude 可以生成高質量的代碼")
    console.print("  • 代碼執行必須在安全沙箱中進行")
    console.print("  • 可以用於調試、優化和審查代碼")
    console.print("  • 適合構建編程助手和教育工具")


if __name__ == "__main__":
    main()

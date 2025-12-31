"""
PromptFlow 條件分支示例

本示例展示：
1. 條件節點激活
2. Python 中的條件邏輯
3. 多分支處理
4. 錯誤處理和回退
"""

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.tree import Tree

console = Console()


def show_activate_config():
    """條件激活配置"""
    console.print("\n[cyan]1. 條件激活（Activate Config）[/cyan]\n")

    console.print("[yellow]功能:[/yellow] 根據條件決定是否執行節點\n")

    config = """nodes:
  # 主節點
  - name: main_process
    type: python
    source:
      type: code
      path: main.py
    inputs:
      data: ${inputs.data}

  # 回退節點（僅在主節點失敗時執行）
  - name: fallback_process
    type: python
    source:
      type: code
      path: fallback.py
    inputs:
      data: ${inputs.data}
    activate:
      when: ${main_process.output}
      is: null

  # 驗證節點（僅在主節點成功時執行）
  - name: validate
    type: python
    source:
      type: code
      path: validate.py
    inputs:
      result: ${main_process.output}
    activate:
      when: ${main_process.output}
      is_not: null"""

    syntax = Syntax(config, "yaml", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()

    # 顯示流程圖
    console.print("[yellow]執行流程:[/yellow]")
    tree = Tree("🔄 條件執行")
    tree.add("main_process 執行")
    branch = tree.add("判斷結果")
    success = branch.add("✓ 成功 (output 不為 null)")
    success.add("執行 validate 節點")
    fail = branch.add("✗ 失敗 (output 為 null)")
    fail.add("執行 fallback_process 節點")
    console.print(tree)
    console.print()


def show_python_conditions():
    """Python 中的條件邏輯"""
    console.print("[cyan]2. Python 節點中的條件邏輯[/cyan]\n")

    code = """from promptflow import tool
from typing import Dict, Any

@tool
def classify_and_route(text: str, threshold: float = 0.7) -> Dict[str, Any]:
    \"\"\"根據文本分類結果進行路由\"\"\"

    # 模擬分類
    score = len(text) / 100  # 簡化示例

    # 條件判斷
    if score >= threshold:
        return {
            "category": "high_quality",
            "score": score,
            "action": "direct_answer",
            "priority": "high"
        }
    elif score >= 0.5:
        return {
            "category": "medium_quality",
            "score": score,
            "action": "need_review",
            "priority": "medium"
        }
    else:
        return {
            "category": "low_quality",
            "score": score,
            "action": "need_improvement",
            "priority": "low"
        }


@tool
def route_based_on_category(classification: Dict[str, Any]) -> str:
    \"\"\"基於分類結果選擇處理方式\"\"\"

    category = classification.get("category")

    if category == "high_quality":
        return "使用 GPT-4 處理"
    elif category == "medium_quality":
        return "使用 GPT-3.5 處理"
    else:
        return "使用預定義模板回答"
"""

    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def show_multi_branch_flow():
    """多分支流程"""
    console.print("[cyan]3. 多分支處理流程[/cyan]\n")

    config = """nodes:
  # 分類節點
  - name: classify
    type: python
    source:
      type: code
      path: classify.py
    inputs:
      text: ${inputs.user_query}

  # 分支 1: 高質量處理
  - name: high_quality_process
    type: llm
    source:
      type: code
      path: gpt4_prompt.jinja2
    inputs:
      query: ${inputs.user_query}
    connection: azure_openai
    deployment_name: gpt-4
    activate:
      when: ${classify.output.category}
      is: "high_quality"

  # 分支 2: 中等質量處理
  - name: medium_quality_process
    type: llm
    source:
      type: code
      path: gpt35_prompt.jinja2
    inputs:
      query: ${inputs.user_query}
    connection: azure_openai
    deployment_name: gpt-35-turbo
    activate:
      when: ${classify.output.category}
      is: "medium_quality"

  # 分支 3: 低質量處理
  - name: low_quality_process
    type: python
    source:
      type: code
      path: template_response.py
    inputs:
      query: ${inputs.user_query}
    activate:
      when: ${classify.output.category}
      is: "low_quality"

  # 合併結果
  - name: merge_results
    type: python
    source:
      type: code
      path: merge.py
    inputs:
      high: ${high_quality_process.output}
      medium: ${medium_quality_process.output}
      low: ${low_quality_process.output}"""

    syntax = Syntax(config, "yaml", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()

    # 顯示分支結構
    console.print("[yellow]分支結構:[/yellow]")
    tree = Tree("🌳 多分支流程")
    tree.add("classify (分類)")
    branches = tree.add("🔀 根據 category 選擇分支")
    branches.add("high_quality → high_quality_process (GPT-4)")
    branches.add("medium_quality → medium_quality_process (GPT-3.5)")
    branches.add("low_quality → low_quality_process (模板)")
    tree.add("merge_results (合併結果)")
    console.print(tree)
    console.print()


def show_error_handling():
    """錯誤處理和回退"""
    console.print("[cyan]4. 錯誤處理和回退機制[/cyan]\n")

    code = """from promptflow import tool
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


@tool
def safe_api_call(endpoint: str, params: Dict) -> Optional[Dict]:
    \"\"\"帶錯誤處理的 API 調用\"\"\"
    try:
        # 模擬 API 調用
        result = call_external_api(endpoint, params)
        return {
            "success": True,
            "data": result
        }
    except TimeoutError:
        logger.warning("API 超時")
        return {
            "success": False,
            "error": "timeout"
        }
    except Exception as e:
        logger.error(f"API 調用失敗: {e}")
        return {
            "success": False,
            "error": "api_error"
        }


@tool
def fallback_handler(api_result: Dict) -> str:
    \"\"\"處理 API 失敗的回退邏輯\"\"\"
    if api_result.get("success"):
        return api_result["data"]

    error_type = api_result.get("error")

    # 根據錯誤類型選擇回退策略
    if error_type == "timeout":
        return "服務暫時繁忙，請稍後再試"
    elif error_type == "api_error":
        return "抱歉，服務暫時不可用"
    else:
        return "發生未知錯誤"
"""

    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def show_retry_pattern():
    """重試模式"""
    console.print("[cyan]5. 重試模式[/cyan]\n")

    code = """from promptflow import tool
import time
from typing import Optional

@tool
def retry_operation(
    operation: str,
    max_retries: int = 3,
    delay: float = 1.0
) -> Optional[dict]:
    \"\"\"帶重試的操作\"\"\"

    for attempt in range(max_retries):
        try:
            # 執行操作
            result = perform_operation(operation)
            return {
                "success": True,
                "result": result,
                "attempts": attempt + 1
            }
        except Exception as e:
            if attempt < max_retries - 1:
                # 指數退避
                wait_time = delay * (2 ** attempt)
                time.sleep(wait_time)
                continue
            else:
                # 最後一次嘗試失敗
                return {
                    "success": False,
                    "error": str(e),
                    "attempts": max_retries
                }

    return None
"""

    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def show_complex_conditions():
    """複雜條件判斷"""
    console.print("[cyan]6. 複雜條件判斷[/cyan]\n")

    code = """from promptflow import tool
from typing import Dict, List

@tool
def complex_routing(
    user_input: str,
    user_profile: Dict,
    context: List[Dict]
) -> Dict[str, str]:
    \"\"\"複雜的路由邏輯\"\"\"

    # 多因素判斷
    is_premium = user_profile.get("tier") == "premium"
    has_history = len(context) > 0
    is_complex_query = len(user_input.split()) > 10

    # 組合條件
    if is_premium and is_complex_query:
        return {
            "model": "gpt-4",
            "max_tokens": 2000,
            "temperature": 0.7,
            "priority": "high"
        }
    elif is_premium or is_complex_query:
        return {
            "model": "gpt-3.5-turbo-16k",
            "max_tokens": 1000,
            "temperature": 0.7,
            "priority": "medium"
        }
    elif has_history:
        return {
            "model": "gpt-3.5-turbo",
            "max_tokens": 500,
            "temperature": 0.5,
            "priority": "normal"
        }
    else:
        return {
            "model": "gpt-3.5-turbo",
            "max_tokens": 300,
            "temperature": 0.3,
            "priority": "normal"
        }
"""

    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def show_best_practices():
    """最佳實踐"""
    console.print("[cyan]條件分支最佳實踐[/cyan]\n")

    practices = """1. 明確的條件邏輯
   - 條件判斷要清晰易懂
   - 避免過於複雜的嵌套條件
   - 使用有意義的變量名

2. 完整的分支覆蓋
   - 確保所有可能的情況都有處理
   - 提供默認分支或回退機制
   - 處理邊界情況

3. 錯誤處理
   - 使用 try-except 捕獲異常
   - 提供有意義的錯誤信息
   - 實現優雅降級

4. 性能考慮
   - 避免不必要的節點執行
   - 使用條件激活減少計算
   - 優先判斷最常見的情況

5. 可測試性
   - 每個分支都要有測試用例
   - 使用明確的返回值類型
   - 記錄日誌便於調試

6. 文檔說明
   - 註釋複雜的條件邏輯
   - 說明每個分支的用途
   - 記錄決策樹
"""

    console.print(Panel(practices, border_style="cyan"))
    console.print()


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]PromptFlow 條件分支示例[/bold cyan]\n"
        "[dim]學習條件邏輯和流程控制[/dim]",
        border_style="cyan"
    ))

    # 1. 條件激活
    show_activate_config()

    # 2. Python 條件
    show_python_conditions()

    # 3. 多分支流程
    show_multi_branch_flow()

    # 4. 錯誤處理
    show_error_handling()

    # 5. 重試模式
    show_retry_pattern()

    # 6. 複雜條件
    show_complex_conditions()

    # 7. 最佳實踐
    show_best_practices()

    # 完成
    console.print("="*60)
    console.print("[bold green]✓ 條件分支示例完成！[/bold green]\n")
    console.print("[cyan]下一步:[/cyan]")
    console.print("  1. 查看 06_批量運行.py - 學習批量測試")
    console.print("  2. 查看 07_評估流程.py - 學習性能評估")
    console.print("  3. 實踐: 構建帶有複雜路由邏輯的 Flow")


if __name__ == "__main__":
    main()

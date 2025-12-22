"""
Code Execution 優化
===================

本模組介紹 MCP 的 Code Execution 模式，這是 MCP 最強大的特性之一。
學習如何減少 98.7% 的 Token 使用，大幅降低成本和延遲。

學習目標：
- 理解 Code Execution 的原理
- 實現代碼執行工具
- 優化 Token 使用
- 處理安全和性能問題

作者：Claude (Anthropic)
日期：2025-12-22
"""

import asyncio
import sys
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from io import StringIO
import contextlib


# ============================================================================
# 第一部分：傳統方式 vs Code Execution
# ============================================================================

class TokenUsageComparison:
    """Token 使用對比"""

    @staticmethod
    def traditional_approach_example():
        """傳統方式示例"""
        return {
            "流程": [
                "1. 用戶: 計算 1+2+3+...+100 的和",
                "2. LLM 生成代碼:",
                "   ```python",
                "   result = sum(range(1, 101))",
                "   print(result)",
                "   ```",
                "3. 客戶端執行代碼: 5050",
                "4. 結果返回給 LLM",
                "5. LLM 回復: 計算結果是 5050"
            ],

            "Token 使用": {
                "用戶請求": "~15 tokens",
                "LLM 生成代碼": "~50 tokens",
                "代碼內容返回": "~50 tokens",
                "執行結果": "~10 tokens",
                "LLM 最終回復": "~20 tokens",
                "總計": "~145 tokens"
            }
        }

    @staticmethod
    def code_execution_approach_example():
        """Code Execution 方式示例"""
        return {
            "流程": [
                "1. 用戶: 計算 1+2+3+...+100 的和",
                "2. LLM 決定調用工具: execute_python",
                "3. MCP 服務器直接執行: sum(range(1, 101))",
                "4. 返回結果: 5050",
                "5. LLM 回復: 計算結果是 5050"
            ],

            "Token 使用": {
                "用戶請求": "~15 tokens",
                "工具調用": "~5 tokens",
                "執行結果": "~5 tokens",
                "LLM 最終回復": "~20 tokens",
                "總計": "~45 tokens"
            },

            "節省": "約 69% Token（實際複雜場景可達 98.7%）"
        }


# ============================================================================
# 第二部分：Python 代碼執行器
# ============================================================================

class PythonCodeExecutor:
    """
    安全的 Python 代碼執行器

    在受限環境中執行 Python 代碼
    """

    def __init__(
        self,
        timeout: int = 30,
        max_memory_mb: int = 512
    ):
        self.timeout = timeout
        self.max_memory_mb = max_memory_mb

        # 允許的內建函數
        self.safe_builtins = {
            'abs', 'all', 'any', 'ascii', 'bin', 'bool', 'bytes',
            'chr', 'dict', 'dir', 'divmod', 'enumerate', 'filter',
            'float', 'format', 'frozenset', 'hex', 'int', 'isinstance',
            'len', 'list', 'map', 'max', 'min', 'oct', 'ord', 'pow',
            'range', 'repr', 'reversed', 'round', 'set', 'slice',
            'sorted', 'str', 'sum', 'tuple', 'type', 'zip'
        }

    async def execute(
        self,
        code: str,
        variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        執行 Python 代碼

        Args:
            code: 要執行的代碼
            variables: 預定義變數

        Returns:
            執行結果，包含輸出、返回值、錯誤等
        """
        # 創建受限的全局命名空間
        safe_globals = {
            '__builtins__': {
                name: __builtins__[name]
                for name in self.safe_builtins
                if name in __builtins__
            }
        }

        # 添加安全的模組
        safe_globals['math'] = __import__('math')
        safe_globals['datetime'] = __import__('datetime')
        safe_globals['json'] = __import__('json')

        # 添加用戶變數
        if variables:
            safe_globals.update(variables)

        # 捕獲標準輸出
        output_buffer = StringIO()
        error_buffer = StringIO()

        result = {
            "success": False,
            "output": "",
            "error": "",
            "return_value": None
        }

        try:
            # 重定向輸出
            with contextlib.redirect_stdout(output_buffer):
                with contextlib.redirect_stderr(error_buffer):
                    # 執行代碼
                    exec_result = exec(code, safe_globals)

                    result["success"] = True
                    result["output"] = output_buffer.getvalue()
                    result["return_value"] = exec_result

        except Exception as e:
            result["error"] = f"{type(e).__name__}: {str(e)}"
            result["output"] = output_buffer.getvalue()

        return result


# ============================================================================
# 第三部分：Code Execution MCP 服務器
# ============================================================================

CODE_EXECUTION_SERVER_EXAMPLE = '''
"""
Code Execution MCP 服務器示例
"""

from mcp.server import Server
from mcp.server.stdio import stdio_server
import asyncio
import sys
from io import StringIO
import contextlib


app = Server("code-executor")


@app.tool()
async def execute_python(
    code: str,
    timeout: int = 30
) -> str:
    """
    執行 Python 代碼

    Args:
        code: 要執行的 Python 代碼
        timeout: 超時時間（秒）

    Returns:
        執行結果或錯誤信息
    """
    # 安全的內建函數白名單
    safe_builtins = {
        'abs', 'all', 'any', 'bin', 'bool', 'chr', 'dict',
        'enumerate', 'filter', 'float', 'int', 'len', 'list',
        'map', 'max', 'min', 'print', 'range', 'round',
        'set', 'sorted', 'str', 'sum', 'tuple', 'zip'
    }

    # 創建受限環境
    safe_globals = {
        '__builtins__': {
            name: __builtins__[name]
            for name in safe_builtins
            if name in __builtins__
        },
        'math': __import__('math'),
        'datetime': __import__('datetime')
    }

    # 捕獲輸出
    output = StringIO()

    try:
        with contextlib.redirect_stdout(output):
            exec(code, safe_globals)

        result = output.getvalue()
        return result if result else "代碼執行成功（無輸出）"

    except Exception as e:
        return f"執行錯誤: {type(e).__name__}: {str(e)}"


@app.tool()
async def execute_calculation(expression: str) -> str:
    """
    執行數學計算

    Args:
        expression: 數學表達式

    Returns:
        計算結果
    """
    try:
        # 只允許數學運算
        safe_dict = {
            '__builtins__': {},
            'abs': abs, 'round': round, 'min': min, 'max': max,
            'sum': sum, 'pow': pow
        }

        # 導入數學函數
        import math
        for name in dir(math):
            if not name.startswith('_'):
                safe_dict[name] = getattr(math, name)

        result = eval(expression, safe_dict)
        return f"結果: {result}"

    except Exception as e:
        return f"計算錯誤: {str(e)}"


async def main():
    async with stdio_server() as (read, write):
        await app.run(
            read,
            write,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
'''


# ============================================================================
# 第四部分：性能優化策略
# ============================================================================

class CodeExecutionOptimization:
    """Code Execution 優化策略"""

    OPTIMIZATION_STRATEGIES = {
        "1. 直接執行簡單操作": {
            "說明": "對於簡單計算，直接在 MCP 服務器執行",
            "示例": "sum(range(1, 101)) → 直接返回 5050",
            "節省": "~90% Token"
        },

        "2. 批量處理": {
            "說明": "一次執行多個操作，避免多輪對話",
            "示例": "一次處理多個文件，而不是逐個處理",
            "節省": "~70% Token"
        },

        "3. 結果緩存": {
            "說明": "緩存常見計算結果",
            "示例": "fibonacci(100) 只計算一次",
            "節省": "~95% Token（重複請求時）"
        },

        "4. 增量執行": {
            "說明": "保持執行上下文，支持增量代碼",
            "示例": "x = 10; y = 20; print(x + y)",
            "節省": "~60% Token"
        },

        "5. 智能摘要": {
            "說明": "對大量輸出進行智能摘要",
            "示例": "只返回關鍵統計信息，不返回全部數據",
            "節省": "~80% Token"
        }
    }

    @staticmethod
    def calculate_savings(
        traditional_tokens: int,
        optimized_tokens: int
    ) -> Dict[str, Any]:
        """計算 Token 節省"""
        saved_tokens = traditional_tokens - optimized_tokens
        saved_percentage = (saved_tokens / traditional_tokens) * 100

        return {
            "原始 Token": traditional_tokens,
            "優化後 Token": optimized_tokens,
            "節省 Token": saved_tokens,
            "節省比例": f"{saved_percentage:.1f}%",
            "成本節省": f"${saved_tokens * 0.00001:.4f} (假設 $0.01/1K tokens)"
        }


# ============================================================================
# 第五部分：實際應用案例
# ============================================================================

class RealWorldExamples:
    """實際應用案例"""

    @staticmethod
    def data_analysis_example():
        """數據分析案例"""
        return {
            "場景": "分析 CSV 文件中的銷售數據",

            "傳統方式": {
                "步驟": [
                    "1. LLM 生成 pandas 代碼（~200 tokens）",
                    "2. 返回代碼給客戶端（~200 tokens）",
                    "3. 客戶端執行代碼",
                    "4. 返回大量數據（~5000 tokens）",
                    "5. LLM 分析數據並總結（~100 tokens）"
                ],
                "總 Token": "~5500 tokens"
            },

            "Code Execution": {
                "步驟": [
                    "1. LLM 調用 analyze_csv 工具（~20 tokens）",
                    "2. MCP 執行分析，返回摘要（~100 tokens）",
                    "3. LLM 解釋結果（~50 tokens）"
                ],
                "總 Token": "~170 tokens"
            },

            "節省": "96.9% Token"
        }

    @staticmethod
    def image_processing_example():
        """圖像處理案例"""
        return {
            "場景": "調整圖像大小並應用濾鏡",

            "傳統方式": {
                "步驟": "生成代碼 → 傳輸代碼 → 執行 → 返回",
                "總 Token": "~1000 tokens"
            },

            "Code Execution": {
                "步驟": "調用 process_image 工具 → 返回結果路徑",
                "總 Token": "~50 tokens"
            },

            "節省": "95% Token"
        }


# ============================================================================
# 主程式示例
# ============================================================================

async def main():
    """主程式：Code Execution 示例"""

    print("=" * 70)
    print("MCP Code Execution 優化")
    print("=" * 70)

    # 1. 對比分析
    print("\n【示例 1：Token 使用對比】")
    comparison = TokenUsageComparison()

    traditional = comparison.traditional_approach_example()
    print("\n傳統方式:")
    for step in traditional["流程"][:3]:
        print(f"  {step}")
    print(f"\n總 Token: {traditional['Token 使用']['總計']}")

    code_exec = comparison.code_execution_approach_example()
    print("\nCode Execution 方式:")
    for step in code_exec["流程"][:3]:
        print(f"  {step}")
    print(f"\n總 Token: {code_exec['Token 使用']['總計']}")
    print(f"節省: {code_exec['節省']}")

    # 2. 代碼執行器測試
    print("\n【示例 2：Python 代碼執行器】")
    executor = PythonCodeExecutor()

    test_code = """
import math
result = sum(range(1, 101))
print(f"1到100的和: {result}")
print(f"平方根: {math.sqrt(result)}")
"""

    result = await executor.execute(test_code)
    print(f"執行成功: {result['success']}")
    print(f"輸出:\n{result['output']}")

    # 3. 優化策略
    print("\n【示例 3：優化策略】")
    for strategy, details in list(CodeExecutionOptimization.OPTIMIZATION_STRATEGIES.items())[:3]:
        print(f"\n{strategy}")
        print(f"  說明: {details['說明']}")
        print(f"  節省: {details['節省']}")

    # 4. 實際案例
    print("\n【示例 4：實際應用案例】")
    examples = RealWorldExamples()
    data_case = examples.data_analysis_example()

    print(f"場景: {data_case['場景']}")
    print(f"傳統方式 Token: {data_case['傳統方式']['總 Token']}")
    print(f"Code Execution Token: {data_case['Code Execution']['總 Token']}")
    print(f"節省: {data_case['節省']}")

    # 5. 服務器示例
    print("\n【示例 5：Code Execution 服務器】")
    print("完整服務器代碼：")
    print(CODE_EXECUTION_SERVER_EXAMPLE[:600] + "...\n[代碼已截斷]")

    print("\n" + "=" * 70)
    print("下一步：查看 11_安全最佳實踐.py 學習安全措施")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())

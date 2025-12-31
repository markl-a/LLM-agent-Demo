"""
Google ADK - 函數調用範例

這個範例展示 Function Calling 功能：
- 基礎函數調用
- 複雜參數處理
- 函數鏈式調用
- 並行函數調用
- 錯誤處理和重試
"""

import os
import json
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime
import requests
from google_adk import Agent
from google_adk.models import GeminiPro
from google_adk.functions import (
    Function,
    FunctionRegistry,
    FunctionCall,
    FunctionResult
)


class FunctionCallingExample:
    """函數調用範例類"""

    def __init__(self, api_key: Optional[str] = None):
        """初始化函數調用範例"""
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("請設置 GOOGLE_API_KEY 環境變量")

    def example_1_basic_function_call(self):
        """範例 1: 基礎函數調用"""
        print("\n" + "="*60)
        print("範例 1: 基礎函數調用")
        print("="*60)

        # 定義函數
        def get_current_time(timezone: str = "UTC") -> Dict[str, str]:
            """
            獲取當前時間

            Args:
                timezone: 時區

            Returns:
                當前時間信息
            """
            now = datetime.now()
            return {
                "timezone": timezone,
                "time": now.strftime("%Y-%m-%d %H:%M:%S"),
                "timestamp": now.timestamp()
            }

        # 註冊函數
        function_def = Function(
            name="get_current_time",
            description="獲取指定時區的當前時間",
            parameters={
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "時區，如 UTC, Asia/Taipei"
                    }
                }
            },
            function=get_current_time
        )

        # 創建帶函數的 Agent
        agent = Agent(
            model=GeminiPro(),
            functions=[function_def],
            name="time-agent"
        )

        # 測試函數調用
        prompt = "現在台北是幾點？"
        print(f"\n問題: {prompt}")

        # 模擬函數調用
        result = get_current_time("Asia/Taipei")
        print(f"函數調用結果: {json.dumps(result, indent=2, ensure_ascii=False)}")

        """
        response = agent.run(prompt)
        print(f"Agent 回答: {response.content}")
        """

        return agent

    def example_2_multiple_functions(self):
        """範例 2: 多個函數調用"""
        print("\n" + "="*60)
        print("範例 2: 多個函數調用")
        print("="*60)

        # 定義多個實用函數
        def calculate(operation: str, a: float, b: float) -> float:
            """執行數學運算"""
            ops = {
                "add": lambda x, y: x + y,
                "subtract": lambda x, y: x - y,
                "multiply": lambda x, y: x * y,
                "divide": lambda x, y: x / y if y != 0 else float('inf')
            }
            return ops.get(operation, lambda x, y: 0)(a, b)

        def convert_currency(
            amount: float,
            from_currency: str,
            to_currency: str
        ) -> Dict[str, Any]:
            """貨幣轉換"""
            # 模擬匯率
            rates = {
                ("USD", "TWD"): 31.5,
                ("TWD", "USD"): 1/31.5,
                ("USD", "EUR"): 0.92,
                ("EUR", "USD"): 1/0.92
            }
            rate = rates.get((from_currency, to_currency), 1.0)
            return {
                "amount": amount,
                "from": from_currency,
                "to": to_currency,
                "rate": rate,
                "result": amount * rate
            }

        def get_weather(city: str) -> Dict[str, Any]:
            """獲取天氣"""
            # 模擬天氣數據
            return {
                "city": city,
                "temperature": 25,
                "condition": "晴天",
                "humidity": "60%"
            }

        # 註冊所有函數
        functions = [
            Function(
                name="calculate",
                description="執行數學運算",
                parameters={
                    "type": "object",
                    "properties": {
                        "operation": {"type": "string"},
                        "a": {"type": "number"},
                        "b": {"type": "number"}
                    },
                    "required": ["operation", "a", "b"]
                },
                function=calculate
            ),
            Function(
                name="convert_currency",
                description="貨幣轉換",
                parameters={
                    "type": "object",
                    "properties": {
                        "amount": {"type": "number"},
                        "from_currency": {"type": "string"},
                        "to_currency": {"type": "string"}
                    },
                    "required": ["amount", "from_currency", "to_currency"]
                },
                function=convert_currency
            ),
            Function(
                name="get_weather",
                description="獲取城市天氣",
                parameters={
                    "type": "object",
                    "properties": {
                        "city": {"type": "string"}
                    },
                    "required": ["city"]
                },
                function=get_weather
            )
        ]

        print("已註冊的函數:")
        for func in functions:
            print(f"  - {func.name}: {func.description}")

        # 創建 Agent
        agent = Agent(
            model=GeminiPro(),
            functions=functions,
            name="multi-function-agent"
        )

        print("\n✓ 多函數 Agent 創建完成")
        return agent

    def example_3_chained_function_calls(self):
        """範例 3: 函數鏈式調用"""
        print("\n" + "="*60)
        print("範例 3: 函數鏈式調用")
        print("="*60)

        # 定義可鏈接的函數
        def fetch_data(source: str) -> Dict[str, Any]:
            """獲取數據"""
            print(f"  步驟 1: 從 {source} 獲取數據")
            return {
                "source": source,
                "data": [1, 2, 3, 4, 5],
                "timestamp": datetime.now().isoformat()
            }

        def process_data(data: List[int]) -> Dict[str, Any]:
            """處理數據"""
            print(f"  步驟 2: 處理數據")
            return {
                "processed": True,
                "sum": sum(data),
                "average": sum(data) / len(data),
                "count": len(data)
            }

        def format_result(result: Dict[str, Any]) -> str:
            """格式化結果"""
            print(f"  步驟 3: 格式化結果")
            return f"總和: {result['sum']}, 平均: {result['average']:.2f}, 數量: {result['count']}"

        # 創建函數鏈
        from google_adk.functions import FunctionChain

        chain = FunctionChain(
            name="data_pipeline",
            functions=[fetch_data, process_data, format_result],
            description="數據處理流程"
        )

        print("函數鏈:")
        print("  fetch_data -> process_data -> format_result")

        # 執行鏈
        print("\n執行函數鏈:")
        result = fetch_data("database")
        processed = process_data(result["data"])
        formatted = format_result(processed)

        print(f"\n最終結果: {formatted}")

        return chain

    def example_4_parallel_function_calls(self):
        """範例 4: 並行函數調用"""
        print("\n" + "="*60)
        print("範例 4: 並行函數調用")
        print("="*60)

        import asyncio

        # 定義異步函數
        async def fetch_api_a(param: str) -> Dict[str, Any]:
            """調用 API A"""
            print(f"  調用 API A: {param}")
            await asyncio.sleep(0.5)
            return {"api": "A", "result": f"結果 A: {param}"}

        async def fetch_api_b(param: str) -> Dict[str, Any]:
            """調用 API B"""
            print(f"  調用 API B: {param}")
            await asyncio.sleep(0.3)
            return {"api": "B", "result": f"結果 B: {param}"}

        async def fetch_api_c(param: str) -> Dict[str, Any]:
            """調用 API C"""
            print(f"  調用 API C: {param}")
            await asyncio.sleep(0.4)
            return {"api": "C", "result": f"結果 C: {param}"}

        # 並行執行
        async def parallel_execution():
            print("\n並行調用多個 API:")
            results = await asyncio.gather(
                fetch_api_a("test"),
                fetch_api_b("test"),
                fetch_api_c("test")
            )
            return results

        # 運行並行任務
        """
        results = asyncio.run(parallel_execution())
        print("\n並行調用結果:")
        for result in results:
            print(f"  {result['api']}: {result['result']}")
        """

        print("✓ 並行函數調用配置完成")

    def example_5_function_with_validation(self):
        """範例 5: 帶驗證的函數調用"""
        print("\n" + "="*60)
        print("範例 5: 帶驗證的函數調用")
        print("="*60)

        from pydantic import BaseModel, Field, validator

        class EmailRequest(BaseModel):
            """郵件請求模型"""
            to: str = Field(..., description="收件人郵箱")
            subject: str = Field(..., description="郵件主題")
            body: str = Field(..., description="郵件正文")

            @validator('to')
            def validate_email(cls, v):
                if '@' not in v:
                    raise ValueError("無效的郵箱地址")
                return v

            @validator('subject')
            def validate_subject(cls, v):
                if len(v) < 3:
                    raise ValueError("主題至少需要 3 個字符")
                return v

        def send_email(to: str, subject: str, body: str) -> Dict[str, Any]:
            """
            發送郵件

            Args:
                to: 收件人
                subject: 主題
                body: 正文

            Returns:
                發送結果
            """
            # 驗證參數
            try:
                email_req = EmailRequest(to=to, subject=subject, body=body)
                print(f"✓ 參數驗證通過")
                print(f"  收件人: {email_req.to}")
                print(f"  主題: {email_req.subject}")

                # 模擬發送
                return {
                    "status": "sent",
                    "message_id": "msg-12345",
                    "timestamp": datetime.now().isoformat()
                }
            except ValueError as e:
                print(f"✗ 參數驗證失敗: {e}")
                return {"status": "error", "error": str(e)}

        # 測試驗證
        print("\n測試 1: 有效參數")
        result1 = send_email(
            to="user@example.com",
            subject="測試郵件",
            body="這是測試內容"
        )
        print(f"結果: {result1['status']}")

        print("\n測試 2: 無效郵箱")
        result2 = send_email(
            to="invalid-email",
            subject="測試",
            body="內容"
        )
        print(f"結果: {result2['status']}")

    def example_6_function_error_handling(self):
        """範例 6: 函數錯誤處理"""
        print("\n" + "="*60)
        print("範例 6: 函數錯誤處理")
        print("="*60)

        from google_adk.functions import FunctionError

        def risky_function(value: int) -> Dict[str, Any]:
            """
            可能失敗的函數

            Raises:
                FunctionError: 當值無效時
                ValueError: 當值超出範圍時
            """
            print(f"  執行函數，值: {value}")

            if value < 0:
                raise ValueError("值不能為負數")

            if value > 100:
                raise FunctionError("值超出允許範圍 (0-100)")

            return {"value": value, "result": value ** 2}

        # 包裝錯誤處理
        def safe_risky_function(value: int) -> Dict[str, Any]:
            """安全的函數調用"""
            try:
                return risky_function(value)
            except ValueError as e:
                print(f"  ✗ ValueError: {e}")
                return {"status": "error", "error": str(e)}
            except FunctionError as e:
                print(f"  ✗ FunctionError: {e}")
                return {"status": "error", "error": str(e)}
            except Exception as e:
                print(f"  ✗ 未知錯誤: {e}")
                return {"status": "error", "error": "未知錯誤"}

        # 測試錯誤處理
        test_values = [50, -5, 150]

        print("\n錯誤處理測試:")
        for val in test_values:
            print(f"\n測試值: {val}")
            result = safe_risky_function(val)
            print(f"結果: {json.dumps(result, ensure_ascii=False)}")

    def example_7_function_retry(self):
        """範例 7: 函數重試機制"""
        print("\n" + "="*60)
        print("範例 7: 函數重試機制")
        print("="*60)

        from google_adk.functions import retry

        # 模擬不穩定的函數
        attempt_count = {"value": 0}

        @retry(max_attempts=3, backoff_factor=2)
        def unstable_function(data: str) -> Dict[str, Any]:
            """
            不穩定的函數（模擬網絡請求）

            前兩次調用會失敗，第三次成功
            """
            attempt_count["value"] += 1
            print(f"  嘗試 {attempt_count['value']}/3")

            if attempt_count["value"] < 3:
                raise Exception("網絡錯誤")

            return {
                "status": "success",
                "data": data,
                "attempts": attempt_count["value"]
            }

        print("執行不穩定函數（自動重試）:")
        try:
            result = unstable_function("test")
            print(f"\n✓ 成功: {json.dumps(result, ensure_ascii=False)}")
        except Exception as e:
            print(f"\n✗ 最終失敗: {e}")

    def example_8_function_caching(self):
        """範例 8: 函數結果緩存"""
        print("\n" + "="*60)
        print("範例 8: 函數結果緩存")
        print("="*60)

        from functools import lru_cache
        import time

        @lru_cache(maxsize=128)
        def expensive_computation(n: int) -> int:
            """
            耗時計算（使用緩存）

            Args:
                n: 輸入值

            Returns:
                計算結果
            """
            print(f"  執行耗時計算: n={n}")
            time.sleep(1)  # 模擬耗時
            return n ** 2 + n ** 3

        print("測試函數緩存:")

        # 第一次調用（未緩存）
        print("\n第一次調用:")
        start = time.time()
        result1 = expensive_computation(10)
        elapsed1 = time.time() - start
        print(f"結果: {result1}, 耗時: {elapsed1:.2f}秒")

        # 第二次相同調用（已緩存）
        print("\n第二次調用（相同參數）:")
        start = time.time()
        result2 = expensive_computation(10)
        elapsed2 = time.time() - start
        print(f"結果: {result2}, 耗時: {elapsed2:.4f}秒")

        # 緩存統計
        cache_info = expensive_computation.cache_info()
        print(f"\n緩存統計:")
        print(f"  命中: {cache_info.hits}")
        print(f"  未命中: {cache_info.misses}")
        print(f"  緩存大小: {cache_info.currsize}")

    def example_9_function_composition(self):
        """範例 9: 函數組合"""
        print("\n" + "="*60)
        print("範例 9: 函數組合")
        print("="*60)

        # 定義簡單函數
        def add_ten(x: int) -> int:
            """加 10"""
            return x + 10

        def multiply_two(x: int) -> int:
            """乘 2"""
            return x * 2

        def square(x: int) -> int:
            """平方"""
            return x ** 2

        # 函數組合
        def compose(*functions):
            """組合多個函數"""
            def composed(x):
                for func in reversed(functions):
                    x = func(x)
                return x
            return composed

        # 創建組合函數
        combined = compose(square, multiply_two, add_ten)

        print("函數組合:")
        print("  add_ten -> multiply_two -> square")

        # 測試
        input_value = 5
        print(f"\n輸入: {input_value}")
        print(f"  add_ten({input_value}) = {add_ten(input_value)}")
        print(f"  multiply_two({add_ten(input_value)}) = {multiply_two(add_ten(input_value))}")
        print(f"  square({multiply_two(add_ten(input_value))}) = {combined(input_value)}")

    def example_10_dynamic_function_generation(self):
        """範例 10: 動態函數生成"""
        print("\n" + "="*60)
        print("範例 10: 動態函數生成")
        print("="*60)

        from google_adk.functions import FunctionFactory

        # 函數工廠
        factory = FunctionFactory()

        # 動態生成 CRUD 函數
        def create_crud_functions(resource_name: str):
            """為資源動態創建 CRUD 函數"""

            functions = {}

            # Create
            def create(data: Dict[str, Any]) -> Dict[str, Any]:
                return {
                    "action": "create",
                    "resource": resource_name,
                    "data": data,
                    "id": f"{resource_name}-123"
                }

            # Read
            def read(id: str) -> Dict[str, Any]:
                return {
                    "action": "read",
                    "resource": resource_name,
                    "id": id,
                    "data": {"name": "示例"}
                }

            # Update
            def update(id: str, data: Dict[str, Any]) -> Dict[str, Any]:
                return {
                    "action": "update",
                    "resource": resource_name,
                    "id": id,
                    "data": data
                }

            # Delete
            def delete(id: str) -> Dict[str, Any]:
                return {
                    "action": "delete",
                    "resource": resource_name,
                    "id": id
                }

            functions[f"create_{resource_name}"] = create
            functions[f"read_{resource_name}"] = read
            functions[f"update_{resource_name}"] = update
            functions[f"delete_{resource_name}"] = delete

            return functions

        # 為不同資源生成函數
        resources = ["user", "product", "order"]

        print("動態生成的函數:")
        for resource in resources:
            funcs = create_crud_functions(resource)
            print(f"\n{resource.upper()} CRUD 函數:")
            for func_name in funcs.keys():
                print(f"  - {func_name}")

        # 測試生成的函數
        user_funcs = create_crud_functions("user")
        result = user_funcs["create_user"]({"name": "張三", "age": 30})
        print(f"\n測試調用:")
        print(json.dumps(result, indent=2, ensure_ascii=False))


def main():
    """主函數"""
    print("="*60)
    print("Google ADK - 函數調用範例")
    print("="*60)

    # 檢查 API 密鑰
    if not os.getenv("GOOGLE_API_KEY"):
        print("\n⚠️  請先設置 GOOGLE_API_KEY 環境變量")
        print("export GOOGLE_API_KEY='your-api-key-here'")
        return

    # 創建範例實例
    example = FunctionCallingExample()

    try:
        # 運行所有範例
        example.example_1_basic_function_call()
        example.example_2_multiple_functions()
        example.example_3_chained_function_calls()
        example.example_4_parallel_function_calls()
        example.example_5_function_with_validation()
        example.example_6_function_error_handling()
        example.example_7_function_retry()
        example.example_8_function_caching()
        example.example_9_function_composition()
        example.example_10_dynamic_function_generation()

        print("\n" + "="*60)
        print("所有函數調用範例執行完成！")
        print("="*60)

    except Exception as e:
        print(f"\n❌ 執行錯誤: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

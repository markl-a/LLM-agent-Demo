"""
Google ADK - 工具定義範例

這個範例展示如何定義和使用自定義工具：
- 基礎工具定義
- 工具參數驗證
- 異步工具
- 工具組合
- 錯誤處理
"""

import os
import json
import asyncio
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime
import requests
from google_adk import Agent
from google_adk.models import GeminiPro
from google_adk.tools import Tool, ToolRegistry, ToolValidator


class ToolDefinitionExample:
    """工具定義範例類"""

    def __init__(self, api_key: Optional[str] = None):
        """初始化工具定義範例"""
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("請設置 GOOGLE_API_KEY 環境變量")

    def example_1_basic_tool(self):
        """範例 1: 基礎工具定義"""
        print("\n" + "="*60)
        print("範例 1: 基礎工具定義")
        print("="*60)

        # 定義簡單的計算器工具
        @Tool(
            name="calculator",
            description="執行基本數學運算"
        )
        def calculator(operation: str, a: float, b: float) -> float:
            """
            執行數學運算

            Args:
                operation: 運算類型 (add, subtract, multiply, divide)
                a: 第一個數字
                b: 第二個數字

            Returns:
                運算結果
            """
            operations = {
                "add": lambda x, y: x + y,
                "subtract": lambda x, y: x - y,
                "multiply": lambda x, y: x * y,
                "divide": lambda x, y: x / y if y != 0 else float('inf')
            }

            result = operations.get(operation, lambda x, y: 0)(a, b)
            print(f"計算: {a} {operation} {b} = {result}")
            return result

        # 創建帶工具的 Agent
        agent = Agent(
            model=GeminiPro(),
            tools=[calculator],
            name="calculator-agent"
        )

        # 測試工具使用
        prompt = "請幫我計算 15 加 27 等於多少？"
        print(f"\n問題: {prompt}")

        response = agent.run(prompt)
        print(f"回答: {response.content}")

        return agent

    def example_2_tool_with_validation(self):
        """範例 2: 帶參數驗證的工具"""
        print("\n" + "="*60)
        print("範例 2: 帶參數驗證的工具")
        print("="*60)

        from pydantic import BaseModel, Field, validator

        class WeatherQuery(BaseModel):
            """天氣查詢參數模型"""
            city: str = Field(..., description="城市名稱")
            unit: str = Field("celsius", description="溫度單位")

            @validator('city')
            def validate_city(cls, v):
                if not v or len(v) < 2:
                    raise ValueError("城市名稱至少需要 2 個字符")
                return v

            @validator('unit')
            def validate_unit(cls, v):
                if v not in ['celsius', 'fahrenheit']:
                    raise ValueError("溫度單位必須是 celsius 或 fahrenheit")
                return v

        @Tool(
            name="get_weather",
            description="獲取指定城市的天氣信息",
            parameters=WeatherQuery
        )
        def get_weather(city: str, unit: str = "celsius") -> Dict[str, Any]:
            """
            獲取天氣信息

            Args:
                city: 城市名稱
                unit: 溫度單位

            Returns:
                天氣信息字典
            """
            # 模擬天氣數據
            weather_data = {
                "city": city,
                "temperature": 25 if unit == "celsius" else 77,
                "unit": unit,
                "condition": "晴天",
                "humidity": "60%",
                "wind_speed": "15 km/h"
            }

            print(f"查詢天氣: {city} ({unit})")
            return weather_data

        # 創建 Agent
        agent = Agent(
            model=GeminiPro(),
            tools=[get_weather],
            name="weather-agent"
        )

        # 測試
        prompt = "台北現在的天氣如何？"
        print(f"\n問題: {prompt}")

        response = agent.run(prompt)
        print(f"回答: {response.content}")

        return agent

    def example_3_async_tools(self):
        """範例 3: 異步工具"""
        print("\n" + "="*60)
        print("範例 3: 異步工具")
        print("="*60)

        @Tool(
            name="fetch_data",
            description="異步獲取外部數據",
            is_async=True
        )
        async def fetch_data(url: str) -> Dict[str, Any]:
            """
            異步獲取數據

            Args:
                url: 數據源 URL

            Returns:
                獲取的數據
            """
            print(f"異步獲取數據: {url}")

            # 模擬異步請求
            await asyncio.sleep(1)

            return {
                "url": url,
                "status": "success",
                "data": {"message": "數據獲取成功"},
                "timestamp": datetime.now().isoformat()
            }

        @Tool(
            name="process_data",
            description="異步處理數據",
            is_async=True
        )
        async def process_data(data: Dict[str, Any]) -> Dict[str, Any]:
            """
            異步處理數據

            Args:
                data: 原始數據

            Returns:
                處理後的數據
            """
            print(f"異步處理數據")

            # 模擬處理時間
            await asyncio.sleep(0.5)

            return {
                "processed": True,
                "original_data": data,
                "result": "處理完成"
            }

        # 創建異步 Agent
        agent = Agent(
            model=GeminiPro(),
            tools=[fetch_data, process_data],
            name="async-agent",
            async_mode=True
        )

        print("✓ 異步工具配置完成")
        print("注意: 實際使用時需要在 async 環境中運行")

        return agent

    def example_4_tool_composition(self):
        """範例 4: 工具組合"""
        print("\n" + "="*60)
        print("範例 4: 工具組合")
        print("="*60)

        # 定義多個相關工具
        @Tool(name="search_database", description="搜索數據庫")
        def search_database(query: str) -> List[Dict[str, Any]]:
            """搜索數據庫"""
            print(f"搜索數據庫: {query}")
            return [
                {"id": 1, "title": "結果 1", "content": "內容 1"},
                {"id": 2, "title": "結果 2", "content": "內容 2"}
            ]

        @Tool(name="filter_results", description="過濾搜索結果")
        def filter_results(results: List[Dict], criteria: str) -> List[Dict]:
            """過濾結果"""
            print(f"過濾結果: {criteria}")
            # 簡單過濾邏輯
            return [r for r in results if criteria.lower() in r["title"].lower()]

        @Tool(name="format_output", description="格式化輸出")
        def format_output(data: List[Dict]) -> str:
            """格式化輸出"""
            print(f"格式化 {len(data)} 條結果")
            formatted = "\n".join([
                f"{i+1}. {item['title']}: {item['content']}"
                for i, item in enumerate(data)
            ])
            return formatted

        # 創建工具鏈
        from google_adk.tools import ToolChain

        search_chain = ToolChain(
            name="search_pipeline",
            tools=[search_database, filter_results, format_output],
            description="完整的搜索流程"
        )

        # 創建 Agent
        agent = Agent(
            model=GeminiPro(),
            tools=[search_chain],
            name="pipeline-agent"
        )

        print("✓ 工具鏈配置完成")
        print("  搜索 -> 過濾 -> 格式化")

        return agent

    def example_5_tool_registry(self):
        """範例 5: 工具註冊表"""
        print("\n" + "="*60)
        print("範例 5: 工具註冊表")
        print("="*60)

        # 創建工具註冊表
        registry = ToolRegistry()

        # 註冊多個工具
        @registry.register(
            name="translate",
            description="翻譯文本",
            category="language"
        )
        def translate(text: str, target_lang: str) -> str:
            """翻譯工具"""
            return f"[翻譯為{target_lang}] {text}"

        @registry.register(
            name="summarize",
            description="摘要文本",
            category="language"
        )
        def summarize(text: str, max_length: int = 100) -> str:
            """摘要工具"""
            return text[:max_length] + "..."

        @registry.register(
            name="sentiment_analysis",
            description="情感分析",
            category="analysis"
        )
        def sentiment_analysis(text: str) -> Dict[str, Any]:
            """情感分析工具"""
            return {
                "sentiment": "positive",
                "score": 0.85,
                "text": text
            }

        # 列出所有工具
        print("\n註冊的工具:")
        for tool_name, tool_info in registry.list_tools().items():
            print(f"  - {tool_name}: {tool_info['description']} ({tool_info['category']})")

        # 按類別獲取工具
        language_tools = registry.get_by_category("language")
        print(f"\n語言類工具: {len(language_tools)} 個")

        # 創建帶註冊表的 Agent
        agent = Agent(
            model=GeminiPro(),
            tool_registry=registry,
            name="registry-agent"
        )

        return agent

    def example_6_error_handling(self):
        """範例 6: 工具錯誤處理"""
        print("\n" + "="*60)
        print("範例 6: 工具錯誤處理")
        print("="*60)

        from google_adk.tools import ToolError, ToolTimeout

        @Tool(
            name="risky_operation",
            description="可能失敗的操作",
            timeout=5,  # 5 秒超時
            retry=3     # 重試 3 次
        )
        def risky_operation(input_data: str) -> str:
            """
            可能失敗的操作

            Raises:
                ToolError: 操作失敗時
                ToolTimeout: 操作超時時
            """
            print(f"執行風險操作: {input_data}")

            # 模擬可能的錯誤
            if input_data == "error":
                raise ToolError("操作失敗: 無效輸入")

            if input_data == "timeout":
                import time
                time.sleep(10)  # 模擬超時

            return f"操作成功: {input_data}"

        # 配置錯誤處理
        from google_adk.tools import ErrorHandler

        error_handler = ErrorHandler(
            on_error="retry",        # 錯誤時重試
            max_retries=3,           # 最大重試次數
            backoff_factor=2,        # 退避因子
            fallback_response="操作暫時不可用，請稍後再試"
        )

        @Tool(
            name="safe_operation",
            description="安全的操作",
            error_handler=error_handler
        )
        def safe_operation(data: str) -> str:
            """帶錯誤處理的安全操作"""
            try:
                result = risky_operation(data)
                return result
            except ToolError as e:
                print(f"工具錯誤: {e}")
                return error_handler.fallback_response
            except ToolTimeout as e:
                print(f"工具超時: {e}")
                return error_handler.fallback_response

        # 測試錯誤處理
        print("\n測試 1: 正常操作")
        result1 = safe_operation("normal")
        print(f"結果: {result1}")

        print("\n測試 2: 錯誤處理")
        result2 = safe_operation("error")
        print(f"結果: {result2}")

    def example_7_tool_permissions(self):
        """範例 7: 工具權限控制"""
        print("\n" + "="*60)
        print("範例 7: 工具權限控制")
        print("="*60)

        from google_adk.security import ToolPermission, PermissionChecker

        # 定義敏感操作工具
        @Tool(
            name="delete_data",
            description="刪除數據（需要管理員權限）",
            permissions=["admin", "delete"]
        )
        def delete_data(data_id: str, user_role: str) -> str:
            """刪除數據"""
            # 檢查權限
            checker = PermissionChecker()
            if not checker.has_permission(user_role, ["admin", "delete"]):
                raise PermissionError("權限不足: 需要管理員權限")

            print(f"刪除數據: {data_id}")
            return f"數據 {data_id} 已刪除"

        @Tool(
            name="read_data",
            description="讀取數據（需要讀取權限）",
            permissions=["read"]
        )
        def read_data(data_id: str, user_role: str) -> Dict[str, Any]:
            """讀取數據"""
            checker = PermissionChecker()
            if not checker.has_permission(user_role, ["read"]):
                raise PermissionError("權限不足: 需要讀取權限")

            print(f"讀取數據: {data_id}")
            return {
                "id": data_id,
                "content": "數據內容",
                "created_at": datetime.now().isoformat()
            }

        # 配置權限策略
        permission_policy = {
            "admin": ["read", "write", "delete"],
            "user": ["read", "write"],
            "guest": ["read"]
        }

        print("權限策略:")
        for role, perms in permission_policy.items():
            print(f"  {role}: {', '.join(perms)}")

        # 測試權限
        print("\n測試 1: 管理員讀取數據")
        try:
            result = read_data("data-1", "admin")
            print(f"✓ 成功: {result}")
        except PermissionError as e:
            print(f"✗ 失敗: {e}")

        print("\n測試 2: 訪客刪除數據")
        try:
            result = delete_data("data-1", "guest")
            print(f"✓ 成功: {result}")
        except PermissionError as e:
            print(f"✗ 失敗: {e}")

    def example_8_tool_caching(self):
        """範例 8: 工具結果緩存"""
        print("\n" + "="*60)
        print("範例 8: 工具結果緩存")
        print("="*60)

        from google_adk.cache import ToolCache

        # 創建緩存
        cache = ToolCache(
            backend="memory",  # 或 "redis"
            ttl=300,          # 5 分鐘
            max_size=100      # 最多緩存 100 個結果
        )

        @Tool(
            name="expensive_operation",
            description="耗時操作",
            cache=cache
        )
        def expensive_operation(param: str) -> str:
            """
            模擬耗時操作

            使用緩存來避免重複計算
            """
            print(f"執行耗時操作: {param}")
            import time
            time.sleep(2)  # 模擬耗時
            return f"結果: {param}"

        # 測試緩存
        print("\n第一次調用（未緩存）:")
        start = datetime.now()
        result1 = expensive_operation("test")
        elapsed1 = (datetime.now() - start).total_seconds()
        print(f"結果: {result1}")
        print(f"耗時: {elapsed1:.2f} 秒")

        print("\n第二次調用（已緩存）:")
        start = datetime.now()
        result2 = expensive_operation("test")
        elapsed2 = (datetime.now() - start).total_seconds()
        print(f"結果: {result2}")
        print(f"耗時: {elapsed2:.2f} 秒")

        # 緩存統計
        stats = cache.get_stats()
        print(f"\n緩存統計:")
        print(f"  命中率: {stats.get('hit_rate', 0):.2%}")
        print(f"  緩存大小: {stats.get('size', 0)}")

    def example_9_dynamic_tools(self):
        """範例 9: 動態工具生成"""
        print("\n" + "="*60)
        print("範例 9: 動態工具生成")
        print("="*60)

        from google_adk.tools import ToolFactory

        # 工具工廠
        factory = ToolFactory()

        # 動態創建 API 工具
        def create_api_tool(api_name: str, endpoint: str, method: str = "GET"):
            """動態創建 API 調用工具"""

            @Tool(
                name=f"call_{api_name}",
                description=f"調用 {api_name} API"
            )
            def api_tool(**kwargs) -> Dict[str, Any]:
                """API 調用工具"""
                print(f"調用 API: {api_name} ({method} {endpoint})")

                # 模擬 API 調用
                return {
                    "api": api_name,
                    "endpoint": endpoint,
                    "method": method,
                    "params": kwargs,
                    "response": {"status": "success"}
                }

            return api_tool

        # 創建多個 API 工具
        weather_tool = create_api_tool("weather", "/api/weather", "GET")
        user_tool = create_api_tool("user", "/api/users", "POST")
        data_tool = create_api_tool("data", "/api/data", "GET")

        print("動態生成的工具:")
        print("  - call_weather: 調用 weather API")
        print("  - call_user: 調用 user API")
        print("  - call_data: 調用 data API")

        # 使用工具
        result = weather_tool(city="台北")
        print(f"\n調用結果: {json.dumps(result, indent=2, ensure_ascii=False)}")

    def example_10_tool_monitoring(self):
        """範例 10: 工具監控和分析"""
        print("\n" + "="*60)
        print("範例 10: 工具監控和分析")
        print("="*60)

        from google_adk.monitoring import ToolMonitor

        # 創建監控器
        monitor = ToolMonitor(
            metrics=[
                "call_count",        # 調用次數
                "success_rate",      # 成功率
                "avg_latency",       # 平均延遲
                "error_count"        # 錯誤次數
            ]
        )

        @Tool(
            name="monitored_tool",
            description="被監控的工具",
            monitor=monitor
        )
        def monitored_tool(data: str) -> str:
            """被監控的工具"""
            print(f"執行工具: {data}")

            # 記錄開始時間
            start = datetime.now()

            # 執行操作
            result = f"處理結果: {data}"

            # 記錄指標
            latency = (datetime.now() - start).total_seconds()
            monitor.record("call_count", 1)
            monitor.record("avg_latency", latency)
            monitor.record("success_rate", 1.0)

            return result

        # 執行多次調用
        print("\n執行 10 次工具調用...")
        for i in range(10):
            monitored_tool(f"data-{i}")

        # 獲取統計信息
        stats = monitor.get_statistics()
        print("\n工具統計:")
        print(f"  總調用次數: {stats.get('call_count', 0)}")
        print(f"  成功率: {stats.get('success_rate', 0):.2%}")
        print(f"  平均延遲: {stats.get('avg_latency', 0):.3f} 秒")
        print(f"  錯誤次數: {stats.get('error_count', 0)}")


def main():
    """主函數"""
    print("="*60)
    print("Google ADK - 工具定義範例")
    print("="*60)

    # 檢查 API 密鑰
    if not os.getenv("GOOGLE_API_KEY"):
        print("\n⚠️  請先設置 GOOGLE_API_KEY 環境變量")
        print("export GOOGLE_API_KEY='your-api-key-here'")
        return

    # 創建範例實例
    example = ToolDefinitionExample()

    try:
        # 運行所有範例
        example.example_1_basic_tool()
        example.example_2_tool_with_validation()
        example.example_3_async_tools()
        example.example_4_tool_composition()
        example.example_5_tool_registry()
        example.example_6_error_handling()
        example.example_7_tool_permissions()
        example.example_8_tool_caching()
        example.example_9_dynamic_tools()
        example.example_10_tool_monitoring()

        print("\n" + "="*60)
        print("所有工具定義範例執行完成！")
        print("="*60)

    except Exception as e:
        print(f"\n❌ 執行錯誤: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

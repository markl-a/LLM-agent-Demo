"""
CAMEL-AI 工具整合

這個範例展示如何讓 Agent 使用外部工具：
1. Function Calling 工具
2. 搜尋引擎整合
3. 代碼執行工具
4. API 調用
5. 自定義工具開發

工具整合讓 Agent 能夠執行實際操作，大大擴展其能力。
"""

import os
from dotenv import load_dotenv
from colorama import init, Fore, Style
from typing import Callable, Dict, Any

init(autoreset=True)
load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    print(f"{Fore.RED}錯誤: 請設置 OPENAI_API_KEY{Style.RESET_ALL}")
    exit(1)


def example1_basic_function_tools():
    """範例1: 基礎函數工具"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例1: 基礎函數工具")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        from camel.toolkits import FunctionTool
        from camel.agents import ChatAgent
        from camel.messages import BaseMessage

        print(f"{Fore.YELLOW}定義工具函數...{Style.RESET_ALL}\n")

        # 定義工具函數
        def calculate_sum(a: float, b: float) -> float:
            """計算兩個數字的和"""
            return a + b

        def calculate_product(a: float, b: float) -> float:
            """計算兩個數字的乘積"""
            return a * b

        def get_current_time() -> str:
            """獲取當前時間"""
            from datetime import datetime
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 創建工具
        sum_tool = FunctionTool(calculate_sum)
        product_tool = FunctionTool(calculate_product)
        time_tool = FunctionTool(get_current_time)

        print(f"{Fore.CYAN}可用工具:{Style.RESET_ALL}")
        print(f"  1. calculate_sum - {calculate_sum.__doc__}")
        print(f"  2. calculate_product - {calculate_product.__doc__}")
        print(f"  3. get_current_time - {get_current_time.__doc__}\n")

        # 創建帶工具的 Agent
        agent_msg = BaseMessage.make_assistant_message(
            role_name="數學助手",
            content="你是一位數學助手，可以使用工具進行計算。"
        )

        agent = ChatAgent(
            system_message=agent_msg,
            model_type="gpt-3.5-turbo",
            tools=[sum_tool, product_tool, time_tool]
        )

        print(f"{Fore.YELLOW}測試工具使用...{Style.RESET_ALL}\n")

        # 測試用例
        test_queries = [
            "請計算 15 加 27",
            "42 乘以 8 等於多少？",
            "現在幾點了？"
        ]

        for query in test_queries:
            print(f"{Fore.BLUE}用戶:{Style.RESET_ALL} {query}")

            msg = BaseMessage.make_user_message(
                role_name="用戶",
                content=query
            )

            response = agent.step(msg)
            print(f"{Fore.GREEN}助手:{Style.RESET_ALL} {response.msg.content}\n")
            print(f"{Fore.MAGENTA}{'-'*60}{Style.RESET_ALL}\n")

    except ImportError:
        print(f"{Fore.YELLOW}注意: FunctionTool 可能需要最新版本的 CAMEL{Style.RESET_ALL}")
        print("這個範例展示了工具整合的概念。\n")
    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def example2_custom_tool_development():
    """範例2: 自定義工具開發"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例2: 開發自定義工具")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        print(f"{Fore.YELLOW}創建自定義工具類...{Style.RESET_ALL}\n")

        class WeatherTool:
            """天氣查詢工具（模擬）"""

            def __init__(self):
                # 模擬天氣數據
                self.weather_data = {
                    "台北": {"temp": 28, "condition": "晴天"},
                    "東京": {"temp": 25, "condition": "多雲"},
                    "紐約": {"temp": 20, "condition": "雨天"}
                }

            def get_weather(self, city: str) -> Dict[str, Any]:
                """獲取指定城市的天氣"""
                if city in self.weather_data:
                    return self.weather_data[city]
                return {"temp": None, "condition": "數據不可用"}

        class CurrencyTool:
            """貨幣轉換工具（模擬）"""

            def __init__(self):
                # 模擬匯率
                self.rates = {
                    ("USD", "TWD"): 31.5,
                    ("TWD", "USD"): 0.032,
                    ("USD", "JPY"): 150.0,
                    ("JPY", "USD"): 0.0067
                }

            def convert(self, amount: float, from_currency: str, to_currency: str) -> float:
                """轉換貨幣"""
                key = (from_currency, to_currency)
                if key in self.rates:
                    return amount * self.rates[key]
                return None

        # 創建工具實例
        weather_tool = WeatherTool()
        currency_tool = CurrencyTool()

        print(f"{Fore.CYAN}自定義工具:{Style.RESET_ALL}")
        print(f"  1. WeatherTool - 查詢天氣")
        print(f"  2. CurrencyTool - 貨幣轉換\n")

        # 測試工具
        print(f"{Fore.YELLOW}測試工具...{Style.RESET_ALL}\n")

        print(f"{Fore.GREEN}天氣查詢:{Style.RESET_ALL}")
        taipei_weather = weather_tool.get_weather("台北")
        print(f"  台北: {taipei_weather['temp']}°C, {taipei_weather['condition']}\n")

        print(f"{Fore.GREEN}貨幣轉換:{Style.RESET_ALL}")
        converted = currency_tool.convert(100, "USD", "TWD")
        print(f"  100 USD = {converted} TWD\n")

        # 在 Agent 中使用
        from camel.agents import ChatAgent
        from camel.messages import BaseMessage

        agent_msg = BaseMessage.make_assistant_message(
            role_name="助手",
            content="""你是一位旅遊助手。
你可以：
1. 查詢天氣（台北、東京、紐約）
2. 轉換貨幣（USD、TWD、JPY）

當用戶詢問時，使用這些工具提供信息。"""
        )

        agent = ChatAgent(
            system_message=agent_msg,
            model_type="gpt-3.5-turbo"
        )

        # 模擬工具調用（實際會通過 function calling）
        queries = [
            "台北今天天氣如何？",
            "100 美元可以換多少台幣？"
        ]

        for query in queries:
            print(f"{Fore.BLUE}用戶:{Style.RESET_ALL} {query}")

            msg = BaseMessage.make_user_message(
                role_name="用戶",
                content=query
            )

            response = agent.step(msg)
            print(f"{Fore.GREEN}助手:{Style.RESET_ALL} {response.msg.content}\n")
            print(f"{Fore.MAGENTA}{'-'*60}{Style.RESET_ALL}\n")

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def example3_search_tools():
    """範例3: 搜尋工具整合"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例3: 搜尋工具整合")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        print(f"{Fore.YELLOW}模擬搜尋工具...{Style.RESET_ALL}\n")

        class SearchTool:
            """搜尋引擎工具（模擬）"""

            def __init__(self):
                # 模擬搜尋結果數據庫
                self.knowledge_base = {
                    "CAMEL": "CAMEL (Communicative Agents for Mind Exploration) 是一個多 Agent 協作框架...",
                    "Python": "Python 是一種高級程式語言，廣泛應用於數據科學和 AI...",
                    "機器學習": "機器學習是人工智能的一個分支，使電腦能從數據中學習..."
                }

            def search(self, query: str) -> str:
                """搜尋知識"""
                # 簡單的關鍵字匹配
                for key, value in self.knowledge_base.items():
                    if key.lower() in query.lower():
                        return value
                return "未找到相關信息"

            def search_code(self, query: str) -> str:
                """搜尋代碼範例"""
                code_examples = {
                    "快速排序": """
def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)
""",
                    "二分搜尋": """
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
"""
                }

                for key, code in code_examples.items():
                    if key in query:
                        return code
                return "未找到相關代碼"

        # 創建搜尋工具
        search_tool = SearchTool()

        print(f"{Fore.CYAN}搜尋工具功能:{Style.RESET_ALL}")
        print(f"  1. search() - 搜尋知識")
        print(f"  2. search_code() - 搜尋代碼範例\n")

        # 測試搜尋
        print(f"{Fore.YELLOW}測試搜尋...{Style.RESET_ALL}\n")

        queries = [
            ("知識", "什麼是 CAMEL？"),
            ("代碼", "快速排序的實現")
        ]

        for search_type, query in queries:
            print(f"{Fore.CYAN}查詢 ({search_type}): {query}{Style.RESET_ALL}")

            if search_type == "知識":
                result = search_tool.search(query)
            else:
                result = search_tool.search_code(query)

            print(f"{Fore.GREEN}結果:{Style.RESET_ALL}")
            print(f"{result}\n")
            print(f"{Fore.MAGENTA}{'-'*60}{Style.RESET_ALL}\n")

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def example4_code_execution_tool():
    """範例4: 代碼執行工具"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例4: 代碼執行工具")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        print(f"{Fore.YELLOW}創建代碼執行環境...{Style.RESET_ALL}\n")

        class CodeExecutor:
            """安全的代碼執行工具"""

            def __init__(self):
                self.allowed_builtins = {
                    'print': print,
                    'len': len,
                    'range': range,
                    'sum': sum,
                    'max': max,
                    'min': min,
                    'abs': abs,
                }

            def execute_python(self, code: str) -> Dict[str, Any]:
                """執行 Python 代碼（受限環境）"""
                import io
                import sys

                # 捕獲輸出
                output = io.StringIO()
                old_stdout = sys.stdout
                sys.stdout = output

                try:
                    # 在受限環境中執行
                    exec_globals = {"__builtins__": self.allowed_builtins}
                    exec(code, exec_globals)

                    result = output.getvalue()
                    sys.stdout = old_stdout

                    return {
                        "success": True,
                        "output": result,
                        "error": None
                    }

                except Exception as e:
                    sys.stdout = old_stdout
                    return {
                        "success": False,
                        "output": None,
                        "error": str(e)
                    }

        # 創建執行器
        executor = CodeExecutor()

        print(f"{Fore.CYAN}代碼執行工具{Style.RESET_ALL}\n")

        # 測試代碼
        test_codes = [
            {
                "name": "計算列表和",
                "code": """
numbers = [1, 2, 3, 4, 5]
total = sum(numbers)
print(f"總和: {total}")
"""
            },
            {
                "name": "找出最大值",
                "code": """
values = [42, 15, 88, 23, 67]
maximum = max(values)
print(f"最大值: {maximum}")
"""
            }
        ]

        for test in test_codes:
            print(f"{Fore.YELLOW}執行: {test['name']}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}代碼:{Style.RESET_ALL}")
            print(test['code'])

            result = executor.execute_python(test['code'])

            if result['success']:
                print(f"{Fore.GREEN}執行成功！{Style.RESET_ALL}")
                print(f"輸出: {result['output']}")
            else:
                print(f"{Fore.RED}執行失敗！{Style.RESET_ALL}")
                print(f"錯誤: {result['error']}")

            print(f"{Fore.MAGENTA}{'-'*60}{Style.RESET_ALL}\n")

        print(f"{Fore.YELLOW}注意: 生產環境中應使用更安全的沙箱環境{Style.RESET_ALL}\n")

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def example5_tool_chaining():
    """範例5: 工具鏈接"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例5: 工具鏈接和組合")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        print(f"{Fore.YELLOW}創建工具鏈...{Style.RESET_ALL}\n")

        class DataProcessor:
            """數據處理工具鏈"""

            def fetch_data(self, source: str) -> list:
                """獲取數據"""
                # 模擬數據源
                data_sources = {
                    "sales": [100, 150, 200, 175, 225],
                    "visitors": [1000, 1200, 1100, 1300, 1250]
                }
                return data_sources.get(source, [])

            def analyze_data(self, data: list) -> dict:
                """分析數據"""
                if not data:
                    return {}

                return {
                    "count": len(data),
                    "sum": sum(data),
                    "average": sum(data) / len(data),
                    "max": max(data),
                    "min": min(data)
                }

            def generate_report(self, analysis: dict) -> str:
                """生成報告"""
                if not analysis:
                    return "無數據"

                report = f"""
數據分析報告
{'='*40}
數據點數量: {analysis['count']}
總和: {analysis['sum']}
平均值: {analysis['average']:.2f}
最大值: {analysis['max']}
最小值: {analysis['min']}
"""
                return report

            def process_pipeline(self, source: str) -> str:
                """完整的處理流程"""
                print(f"  步驟 1: 獲取數據...")
                data = self.fetch_data(source)
                print(f"    獲取了 {len(data)} 個數據點")

                print(f"  步驟 2: 分析數據...")
                analysis = self.analyze_data(data)
                print(f"    分析完成")

                print(f"  步驟 3: 生成報告...")
                report = self.generate_report(analysis)
                print(f"    報告生成完成")

                return report

        # 創建處理器
        processor = DataProcessor()

        print(f"{Fore.CYAN}工具鏈流程:{Style.RESET_ALL}")
        print(f"  數據獲取 → 數據分析 → 報告生成\n")

        # 執行工具鏈
        sources = ["sales", "visitors"]

        for source in sources:
            print(f"{Fore.GREEN}處理數據源: {source}{Style.RESET_ALL}\n")

            report = processor.process_pipeline(source)

            print(f"{Fore.CYAN}報告:{Style.RESET_ALL}")
            print(report)
            print(f"{Fore.MAGENTA}{'-'*60}{Style.RESET_ALL}\n")

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def example6_tool_selection():
    """範例6: 工具自動選擇"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例6: Agent 自動選擇工具")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        from camel.agents import ChatAgent
        from camel.messages import BaseMessage

        print(f"{Fore.YELLOW}創建多功能 Agent...{Style.RESET_ALL}\n")

        # 定義多個工具
        tools_info = """
可用工具：
1. calculate(a, b, operation) - 數學計算
2. search(query) - 搜尋信息
3. translate(text, target_lang) - 翻譯文字
4. weather(city) - 查詢天氣
"""

        agent_msg = BaseMessage.make_assistant_message(
            role_name="智能助手",
            content=f"""你是一位智能助手，可以使用多種工具。

{tools_info}

根據用戶的需求，選擇合適的工具來完成任務。
明確說明你會使用哪個工具以及為什麼。"""
        )

        agent = ChatAgent(
            system_message=agent_msg,
            model_type="gpt-3.5-turbo"
        )

        print(f"{Fore.CYAN}測試工具選擇...{Style.RESET_ALL}\n")

        # 不同類型的請求
        requests = [
            "請幫我計算 25 乘以 4",
            "查詢關於量子計算的信息",
            "把 'Hello World' 翻譯成中文",
            "台北今天天氣如何？"
        ]

        for request in requests:
            print(f"{Fore.BLUE}用戶:{Style.RESET_ALL} {request}")

            msg = BaseMessage.make_user_message(
                role_name="用戶",
                content=request
            )

            response = agent.step(msg)
            print(f"{Fore.GREEN}助手:{Style.RESET_ALL} {response.msg.content}\n")
            print(f"{Fore.MAGENTA}{'-'*60}{Style.RESET_ALL}\n")

        print(f"{Fore.CYAN}觀察:{Style.RESET_ALL}")
        print("Agent 能夠根據問題類型自動選擇合適的工具。")
        print("這展示了 Agent 的推理和決策能力。\n")

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def main():
    """主函數"""
    print(f"\n{Fore.GREEN}{'='*60}")
    print(f"  CAMEL-AI 工具整合範例")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    print(f"{Fore.YELLOW}關於工具整合:{Style.RESET_ALL}")
    print("工具整合讓 AI Agent 能夠執行實際操作：")
    print("1. 函數調用 - 執行特定功能")
    print("2. 外部 API - 訪問外部服務")
    print("3. 搜尋引擎 - 獲取最新信息")
    print("4. 代碼執行 - 運行程式代碼")
    print("5. 工具鏈 - 組合多個工具\n")

    try:
        example1_basic_function_tools()
        example2_custom_tool_development()
        example3_search_tools()
        example4_code_execution_tool()
        example5_tool_chaining()
        example6_tool_selection()

        print(f"\n{Fore.GREEN}{'='*60}")
        print(f"  所有範例執行完成！")
        print(f"{'='*60}{Style.RESET_ALL}\n")

        print(f"{Fore.CYAN}工具整合最佳實踐:{Style.RESET_ALL}")
        print("1. 明確定義工具的功能和參數")
        print("2. 實施適當的安全控制")
        print("3. 處理工具執行的錯誤")
        print("4. 提供清晰的工具文檔")
        print("5. 監控工具使用情況\n")

        print(f"{Fore.CYAN}下一步:{Style.RESET_ALL}")
        print("查看 07_知識檢索.py 學習 RAG 整合\n")

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}程序被用戶中斷{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}執行過程中發生錯誤: {e}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()

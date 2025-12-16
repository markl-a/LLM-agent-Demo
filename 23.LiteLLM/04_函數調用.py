"""
LiteLLM 函數調用範例
====================

這個範例展示如何使用 LiteLLM 的 Function Calling 功能：
1. 基本的函數調用
2. 定義和使用工具
3. 多個工具的使用
4. 強制函數調用
5. 並行函數調用
6. 實際應用場景

Function Calling 讓 LLM 能夠調用外部函數和 API，大幅擴展其能力。
"""

import os
from litellm import completion
import litellm
import json
from datetime import datetime
import random

# 設定日誌
litellm.set_verbose = False


# 定義一些示例函數
def get_current_weather(location: str, unit: str = "celsius") -> dict:
    """
    獲取指定地點的天氣資訊（模擬）

    Args:
        location: 城市名稱
        unit: 溫度單位 (celsius 或 fahrenheit)

    Returns:
        天氣資訊字典
    """
    # 模擬天氣數據
    weather_data = {
        "台北": {"temperature": 28, "condition": "晴天", "humidity": 65},
        "東京": {"temperature": 25, "condition": "多雲", "humidity": 70},
        "紐約": {"temperature": 22, "condition": "雨天", "humidity": 80},
        "倫敦": {"temperature": 18, "condition": "陰天", "humidity": 75},
    }

    city_weather = weather_data.get(location, {"temperature": 20, "condition": "未知", "humidity": 60})

    if unit == "fahrenheit":
        city_weather["temperature"] = city_weather["temperature"] * 9/5 + 32

    return {
        "location": location,
        "temperature": city_weather["temperature"],
        "unit": unit,
        "condition": city_weather["condition"],
        "humidity": city_weather["humidity"]
    }


def calculate(operation: str, num1: float, num2: float) -> float:
    """
    執行基本數學運算

    Args:
        operation: 運算類型 (add, subtract, multiply, divide)
        num1: 第一個數字
        num2: 第二個數字

    Returns:
        運算結果
    """
    operations = {
        "add": num1 + num2,
        "subtract": num1 - num2,
        "multiply": num1 * num2,
        "divide": num1 / num2 if num2 != 0 else "Error: Division by zero"
    }
    return operations.get(operation, "Error: Unknown operation")


def search_database(query: str, category: str = "all") -> list:
    """
    模擬資料庫搜尋

    Args:
        query: 搜尋關鍵字
        category: 搜尋類別

    Returns:
        搜尋結果列表
    """
    # 模擬資料庫
    database = {
        "products": ["筆記型電腦", "滑鼠", "鍵盤", "螢幕"],
        "users": ["張三", "李四", "王五"],
        "orders": ["訂單001", "訂單002", "訂單003"]
    }

    if category in database:
        results = [item for item in database[category] if query.lower() in item.lower()]
    else:
        results = []
        for items in database.values():
            results.extend([item for item in items if query.lower() in item.lower()])

    return results[:5]  # 返回前 5 個結果


def basic_function_calling():
    """基本的函數調用範例"""
    print("=" * 60)
    print("範例 1: 基本函數調用")
    print("=" * 60)

    # 定義可用的工具（函數）
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "獲取指定城市的當前天氣資訊",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "城市名稱，例如：台北、東京"
                        },
                        "unit": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"],
                            "description": "溫度單位"
                        }
                    },
                    "required": ["location"]
                }
            }
        }
    ]

    try:
        # 第一步：詢問 LLM
        response = completion(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "台北現在的天氣如何？"}],
            tools=tools,
            tool_choice="auto"  # 自動決定是否調用函數
        )

        # 檢查是否需要調用函數
        message = response.choices[0].message

        if message.tool_calls:
            print("\nLLM 決定調用函數:")
            tool_call = message.tool_calls[0]
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            print(f"  函數名稱: {function_name}")
            print(f"  參數: {function_args}")

            # 第二步：執行函數
            if function_name == "get_current_weather":
                function_response = get_current_weather(**function_args)
                print(f"  函數返回: {function_response}")

                # 第三步：將函數結果傳回 LLM
                second_response = completion(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "user", "content": "台北現在的天氣如何？"},
                        message,  # 包含 tool_calls 的訊息
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": function_name,
                            "content": json.dumps(function_response)
                        }
                    ],
                    tools=tools
                )

                # 獲取最終回應
                print(f"\n最終回應: {second_response.choices[0].message.content}")
        else:
            print(f"直接回應: {message.content}")

    except Exception as e:
        print(f"錯誤: {e}")


def multiple_tools():
    """使用多個工具的範例"""
    print("\n" + "=" * 60)
    print("範例 2: 使用多個工具")
    print("=" * 60)

    # 定義多個工具
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "獲取城市天氣",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "城市名稱"}
                    },
                    "required": ["location"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "calculate",
                "description": "執行數學運算",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "enum": ["add", "subtract", "multiply", "divide"],
                            "description": "運算類型"
                        },
                        "num1": {"type": "number", "description": "第一個數字"},
                        "num2": {"type": "number", "description": "第二個數字"}
                    },
                    "required": ["operation", "num1", "num2"]
                }
            }
        }
    ]

    # 可用的函數映射
    available_functions = {
        "get_current_weather": get_current_weather,
        "calculate": calculate
    }

    try:
        # 測試不同的查詢
        queries = [
            "東京的天氣如何？",
            "計算 25 乘以 4",
            "如果台北溫度是 28 度，紐約是 22 度，差幾度？"
        ]

        for query in queries:
            print(f"\n查詢: {query}")
            print("-" * 40)

            response = completion(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": query}],
                tools=tools,
                tool_choice="auto"
            )

            message = response.choices[0].message

            if message.tool_calls:
                # 執行所有被調用的函數
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    print(f"調用: {function_name}({function_args})")

                    # 執行函數
                    function_to_call = available_functions[function_name]
                    function_response = function_to_call(**function_args)

                    print(f"結果: {function_response}")
            else:
                print(f"回應: {message.content}")

    except Exception as e:
        print(f"錯誤: {e}")


def forced_function_call():
    """強制調用特定函數"""
    print("\n" + "=" * 60)
    print("範例 3: 強制函數調用")
    print("=" * 60)

    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_database",
                "description": "搜尋資料庫",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "搜尋關鍵字"},
                        "category": {
                            "type": "string",
                            "enum": ["products", "users", "orders", "all"],
                            "description": "搜尋類別"
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    ]

    try:
        # 強制調用特定函數
        response = completion(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "尋找所有產品"}],
            tools=tools,
            tool_choice={"type": "function", "function": {"name": "search_database"}}
        )

        message = response.choices[0].message

        if message.tool_calls:
            tool_call = message.tool_calls[0]
            function_args = json.loads(tool_call.function.arguments)

            print(f"被強制調用的函數: {tool_call.function.name}")
            print(f"參數: {function_args}")

            # 執行搜尋
            results = search_database(**function_args)
            print(f"搜尋結果: {results}")

    except Exception as e:
        print(f"錯誤: {e}")


def parallel_function_calls():
    """並行函數調用範例"""
    print("\n" + "=" * 60)
    print("範例 4: 並行函數調用")
    print("=" * 60)

    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "獲取城市天氣",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "城市名稱"}
                    },
                    "required": ["location"]
                }
            }
        }
    ]

    try:
        # 請求多個城市的天氣（應該並行調用）
        response = completion(
            model="gpt-4",  # GPT-4 更好地支援並行調用
            messages=[{"role": "user", "content": "告訴我台北、東京和紐約的天氣"}],
            tools=tools,
            tool_choice="auto"
        )

        message = response.choices[0].message

        if message.tool_calls:
            print(f"LLM 決定並行調用 {len(message.tool_calls)} 個函數:")

            tool_messages = [
                {"role": "user", "content": "告訴我台北、東京和紐約的天氣"},
                message
            ]

            # 執行所有函數調用
            for tool_call in message.tool_calls:
                function_args = json.loads(tool_call.function.arguments)
                print(f"\n調用: get_current_weather({function_args})")

                result = get_current_weather(**function_args)
                print(f"結果: {result}")

                # 添加工具回應
                tool_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": "get_current_weather",
                    "content": json.dumps(result)
                })

            # 獲取最終回應
            final_response = completion(
                model="gpt-4",
                messages=tool_messages,
                tools=tools
            )

            print(f"\n最終回應:\n{final_response.choices[0].message.content}")

    except Exception as e:
        print(f"錯誤: {e}")


def conversation_with_tools():
    """在對話中使用工具"""
    print("\n" + "=" * 60)
    print("範例 5: 對話中使用工具")
    print("=" * 60)

    tools = [
        {
            "type": "function",
            "function": {
                "name": "calculate",
                "description": "執行數學運算",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "enum": ["add", "subtract", "multiply", "divide"]
                        },
                        "num1": {"type": "number"},
                        "num2": {"type": "number"}
                    },
                    "required": ["operation", "num1", "num2"]
                }
            }
        }
    ]

    # 模擬多輪對話
    conversation = [
        {"role": "system", "content": "你是一個數學助手，幫助用戶進行計算。"}
    ]

    user_queries = [
        "計算 15 加 27",
        "然後乘以 3",
        "謝謝！"
    ]

    try:
        for query in user_queries:
            print(f"\n用戶: {query}")
            conversation.append({"role": "user", "content": query})

            response = completion(
                model="gpt-3.5-turbo",
                messages=conversation,
                tools=tools,
                tool_choice="auto"
            )

            message = response.choices[0].message

            if message.tool_calls:
                # 處理函數調用
                conversation.append(message)

                for tool_call in message.tool_calls:
                    function_args = json.loads(tool_call.function.arguments)
                    result = calculate(**function_args)

                    print(f"  [調用計算器: {function_args} = {result}]")

                    conversation.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": "calculate",
                        "content": json.dumps({"result": result})
                    })

                # 獲取最終回應
                final_response = completion(
                    model="gpt-3.5-turbo",
                    messages=conversation,
                    tools=tools
                )

                assistant_message = final_response.choices[0].message
                conversation.append(assistant_message)
                print(f"助手: {assistant_message.content}")
            else:
                conversation.append(message)
                print(f"助手: {message.content}")

    except Exception as e:
        print(f"錯誤: {e}")


def tool_with_error_handling():
    """帶錯誤處理的工具使用"""
    print("\n" + "=" * 60)
    print("範例 6: 帶錯誤處理的工具使用")
    print("=" * 60)

    tools = [
        {
            "type": "function",
            "function": {
                "name": "calculate",
                "description": "執行數學運算",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "operation": {"type": "string"},
                        "num1": {"type": "number"},
                        "num2": {"type": "number"}
                    },
                    "required": ["operation", "num1", "num2"]
                }
            }
        }
    ]

    try:
        # 測試除以零的情況
        response = completion(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "10 除以 0 等於多少？"}],
            tools=tools,
            tool_choice="auto"
        )

        message = response.choices[0].message

        if message.tool_calls:
            tool_call = message.tool_calls[0]
            function_args = json.loads(tool_call.function.arguments)

            print(f"調用: calculate({function_args})")

            try:
                result = calculate(**function_args)
                print(f"結果: {result}")

                # 將結果（包括錯誤）傳回 LLM
                final_response = completion(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "user", "content": "10 除以 0 等於多少？"},
                        message,
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": "calculate",
                            "content": json.dumps({"result": str(result)})
                        }
                    ],
                    tools=tools
                )

                print(f"\nLLM 回應: {final_response.choices[0].message.content}")

            except Exception as func_error:
                print(f"函數執行錯誤: {func_error}")

    except Exception as e:
        print(f"錯誤: {e}")


def real_world_example():
    """真實世界應用範例：訂餐系統"""
    print("\n" + "=" * 60)
    print("範例 7: 真實應用 - 訂餐系統")
    print("=" * 60)

    # 模擬餐廳系統的函數
    def check_menu(category: str = "all") -> list:
        """查看菜單"""
        menu = {
            "主餐": ["牛排", "雞排", "魚排"],
            "飲料": ["可樂", "果汁", "咖啡"],
            "甜點": ["蛋糕", "冰淇淋", "布丁"]
        }
        return menu.get(category, sum(menu.values(), []))

    def create_order(items: list, table_number: int) -> dict:
        """創建訂單"""
        order_id = f"ORDER-{random.randint(1000, 9999)}"
        return {
            "order_id": order_id,
            "items": items,
            "table": table_number,
            "status": "已確認",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    tools = [
        {
            "type": "function",
            "function": {
                "name": "check_menu",
                "description": "查看餐廳菜單",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "enum": ["主餐", "飲料", "甜點", "all"]
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_order",
                "description": "創建訂單",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "items": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "訂購的項目列表"
                        },
                        "table_number": {
                            "type": "integer",
                            "description": "桌號"
                        }
                    },
                    "required": ["items", "table_number"]
                }
            }
        }
    ]

    available_functions = {
        "check_menu": check_menu,
        "create_order": create_order
    }

    # 模擬客戶對話
    conversation = [
        {"role": "system", "content": "你是一個友善的餐廳服務員，幫助客人點餐。"}
    ]

    customer_requests = [
        "有什麼主餐？",
        "我要一份牛排和一杯可樂，桌號 5"
    ]

    try:
        for request in customer_requests:
            print(f"\n客人: {request}")
            conversation.append({"role": "user", "content": request})

            response = completion(
                model="gpt-3.5-turbo",
                messages=conversation,
                tools=tools,
                tool_choice="auto"
            )

            message = response.choices[0].message

            if message.tool_calls:
                conversation.append(message)

                for tool_call in message.tool_calls:
                    func_name = tool_call.function.name
                    func_args = json.loads(tool_call.function.arguments)

                    print(f"  [執行: {func_name}({func_args})]")

                    func = available_functions[func_name]
                    result = func(**func_args)

                    print(f"  [結果: {result}]")

                    conversation.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": func_name,
                        "content": json.dumps(result, ensure_ascii=False)
                    })

                # 獲取服務員的回應
                final_response = completion(
                    model="gpt-3.5-turbo",
                    messages=conversation,
                    tools=tools
                )

                assistant_msg = final_response.choices[0].message
                conversation.append(assistant_msg)
                print(f"服務員: {assistant_msg.content}")
            else:
                conversation.append(message)
                print(f"服務員: {message.content}")

    except Exception as e:
        print(f"錯誤: {e}")


def main():
    """主函數：運行所有範例"""
    print("\n" + "=" * 60)
    print("LiteLLM 函數調用範例")
    print("=" * 60)

    basic_function_calling()
    multiple_tools()
    forced_function_call()
    parallel_function_calls()
    conversation_with_tools()
    tool_with_error_handling()
    real_world_example()

    print("\n" + "=" * 60)
    print("所有範例執行完畢！")
    print("=" * 60)


if __name__ == "__main__":
    main()

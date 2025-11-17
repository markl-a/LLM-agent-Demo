"""
函數調用示例
展示如何讓 Agent 調用外部函數和工具
"""

import os
from dotenv import load_dotenv
from typing import Annotated
import autogen

load_dotenv()

config_list = [
    {
        "model": "gpt-4",
        "api_key": os.getenv("OPENAI_API_KEY")
    }
]

# 定義工具函數
def get_weather(city: Annotated[str, "城市名稱"]) -> str:
    """
    獲取城市天氣信息

    Args:
        city: 城市名稱

    Returns:
        天氣信息字符串
    """
    # 模擬天氣數據
    weather_data = {
        "北京": "晴天，溫度 25°C，空氣質量良好",
        "上海": "多雲，溫度 28°C，濕度較高",
        "深圳": "陰天，溫度 30°C，可能有雷陣雨",
        "杭州": "小雨，溫度 22°C，建議帶傘"
    }

    return weather_data.get(city, f"{city} 的天氣數據暫時無法獲取")

def calculate(
    operation: Annotated[str, "運算類型：add, subtract, multiply, divide"],
    a: Annotated[float, "第一個數字"],
    b: Annotated[float, "第二個數字"]
) -> float:
    """
    執行數學運算

    Args:
        operation: 運算類型
        a: 第一個數字
        b: 第二個數字

    Returns:
        計算結果
    """
    operations = {
        "add": lambda x, y: x + y,
        "subtract": lambda x, y: x - y,
        "multiply": lambda x, y: x * y,
        "divide": lambda x, y: x / y if y != 0 else float('inf')
    }

    if operation not in operations:
        return f"不支持的運算: {operation}"

    result = operations[operation](a, b)
    print(f"執行運算: {a} {operation} {b} = {result}")
    return result

def search_database(query: Annotated[str, "搜索查詢"]) -> str:
    """
    搜索數據庫

    Args:
        query: 搜索關鍵詞

    Returns:
        搜索結果
    """
    # 模擬數據庫
    database = {
        "產品A": {"價格": 99.99, "庫存": 100, "類別": "電子產品"},
        "產品B": {"價格": 199.99, "庫存": 50, "類別": "家電"},
        "產品C": {"價格": 49.99, "庫存": 200, "類別": "生活用品"},
    }

    results = []
    for product, info in database.items():
        if query.lower() in product.lower():
            results.append(f"{product}: {info}")

    return "\n".join(results) if results else f"未找到與 '{query}' 相關的結果"

def main():
    """運行函數調用示例"""

    # 創建支持函數調用的 Assistant
    assistant = autogen.AssistantAgent(
        name="助理",
        system_message="""你是一個智能助手，可以調用各種工具函數來幫助用戶。

        可用工具：
        1. get_weather - 查詢天氣
        2. calculate - 執行數學運算
        3. search_database - 搜索產品信息

        請根據用戶需求選擇合適的工具。
        """,
        llm_config={
            "config_list": config_list,
            "functions": [
                {
                    "name": "get_weather",
                    "description": "獲取指定城市的天氣信息",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city": {
                                "type": "string",
                                "description": "城市名稱，例如：北京、上海"
                            }
                        },
                        "required": ["city"]
                    }
                },
                {
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
                            "a": {"type": "number", "description": "第一個數字"},
                            "b": {"type": "number", "description": "第二個數字"}
                        },
                        "required": ["operation", "a", "b"]
                    }
                },
                {
                    "name": "search_database",
                    "description": "在數據庫中搜索產品",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "搜索關鍵詞"
                            }
                        },
                        "required": ["query"]
                    }
                }
            ]
        }
    )

    # 創建 User Proxy 並註冊函數
    user_proxy = autogen.UserProxyAgent(
        name="用戶",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        function_map={
            "get_weather": get_weather,
            "calculate": calculate,
            "search_database": search_database
        }
    )

    # 測試任務
    tasks = [
        "請幫我查詢北京和上海的天氣",
        "計算 123 加上 456 等於多少",
        "搜索產品A的信息",
        "請先查詢深圳的天氣，然後計算 50 乘以 20",
    ]

    for i, task in enumerate(tasks, 1):
        print(f"\n{'='*60}")
        print(f"任務 {i}: {task}")
        print('='*60)

        user_proxy.initiate_chat(
            assistant,
            message=task,
            clear_history=i > 1  # 清除之前的歷史
        )

if __name__ == "__main__":
    main()

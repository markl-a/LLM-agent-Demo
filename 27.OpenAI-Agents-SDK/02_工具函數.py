"""
OpenAI Agents SDK - 工具函數範例

展示如何定義和使用工具函數（Tools）
包含：基礎工具、類型驗證、錯誤處理、異步工具

與 Swarm 的主要區別：
1. 使用 @tool 裝飾器（自動生成 schema）
2. 強類型檢查
3. 更好的錯誤處理
"""

import os
from typing import Optional, List, Dict
from datetime import datetime
from openai_agents import Agent, tool, run, configure

# ============================================================================
# 1. 基礎工具函數
# ============================================================================

@tool
def get_current_time() -> str:
    """獲取當前時間

    Returns:
        格式化的當前時間字符串
    """
    return datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")


@tool
def calculate(expression: str) -> str:
    """計算數學表達式

    Args:
        expression: 數學表達式，例如 "2 + 3 * 4"

    Returns:
        計算結果字符串

    Example:
        >>> calculate("10 + 5")
        "15"
    """
    try:
        # 安全評估（僅允許數學運算）
        allowed_chars = set("0123456789+-*/() .")
        if not all(c in allowed_chars for c in expression):
            return "錯誤：表達式包含不允許的字符"

        result = eval(expression)
        return f"{result}"
    except Exception as e:
        return f"計算錯誤：{str(e)}"


# ============================================================================
# 2. 帶參數的工具
# ============================================================================

@tool
def search_database(
    query: str,
    category: Optional[str] = None,
    limit: int = 5
) -> Dict[str, any]:
    """搜索模擬數據庫

    Args:
        query: 搜索關鍵詞
        category: 可選的分類過濾（electronics, books, clothing）
        limit: 返回結果數量限制，默認 5

    Returns:
        包含搜索結果的字典

    Example:
        >>> search_database("laptop", category="electronics", limit=3)
        {"results": [...], "count": 3}
    """
    # 模擬數據
    mock_data = {
        "electronics": [
            {"id": 1, "name": "筆記本電腦", "price": 30000},
            {"id": 2, "name": "手機", "price": 15000},
            {"id": 3, "name": "平板", "price": 12000},
        ],
        "books": [
            {"id": 4, "name": "Python 編程", "price": 500},
            {"id": 5, "name": "AI 基礎", "price": 600},
        ],
        "clothing": [
            {"id": 6, "name": "T恤", "price": 300},
            {"id": 7, "name": "牛仔褲", "price": 800},
        ]
    }

    # 過濾數據
    results = []
    categories = [category] if category else mock_data.keys()

    for cat in categories:
        if cat in mock_data:
            for item in mock_data[cat]:
                if query.lower() in item["name"].lower():
                    results.append({**item, "category": cat})

    # 限制結果數量
    results = results[:limit]

    return {
        "query": query,
        "category": category,
        "count": len(results),
        "results": results
    }


@tool
def get_weather(
    city: str,
    unit: str = "celsius"
) -> Dict[str, any]:
    """獲取城市天氣（模擬）

    Args:
        city: 城市名稱
        unit: 溫度單位，"celsius" 或 "fahrenheit"

    Returns:
        天氣信息字典
    """
    # 模擬天氣數據
    mock_weather = {
        "台北": {"temp_c": 25, "condition": "晴天", "humidity": 60},
        "台中": {"temp_c": 28, "condition": "多雲", "humidity": 55},
        "高雄": {"temp_c": 30, "condition": "晴天", "humidity": 70},
    }

    if city not in mock_weather:
        return {"error": f"找不到 {city} 的天氣資料"}

    weather = mock_weather[city].copy()

    # 轉換溫度單位
    if unit == "fahrenheit":
        weather["temp_f"] = weather["temp_c"] * 9/5 + 32
        del weather["temp_c"]

    weather["city"] = city
    weather["unit"] = unit

    return weather


# ============================================================================
# 3. 複雜數據結構
# ============================================================================

@tool
def get_user_profile(user_id: str) -> Dict[str, any]:
    """獲取用戶檔案

    Args:
        user_id: 用戶 ID

    Returns:
        用戶檔案字典，包含姓名、郵箱、訂單歷史等
    """
    # 模擬用戶數據
    mock_users = {
        "U001": {
            "id": "U001",
            "name": "張小明",
            "email": "ming@example.com",
            "member_since": "2020-01-15",
            "orders": [
                {"id": "O001", "date": "2024-01-10", "total": 1500},
                {"id": "O002", "date": "2024-02-20", "total": 3000},
            ],
            "preferences": {
                "newsletter": True,
                "categories": ["electronics", "books"]
            }
        },
        "U002": {
            "id": "U002",
            "name": "李小華",
            "email": "hua@example.com",
            "member_since": "2021-06-01",
            "orders": [],
            "preferences": {
                "newsletter": False,
                "categories": ["clothing"]
            }
        }
    }

    if user_id not in mock_users:
        return {"error": f"用戶 {user_id} 不存在"}

    return mock_users[user_id]


# ============================================================================
# 4. 錯誤處理工具
# ============================================================================

@tool
def divide_numbers(a: float, b: float) -> str:
    """除法運算（展示錯誤處理）

    Args:
        a: 被除數
        b: 除數

    Returns:
        計算結果或錯誤消息
    """
    if b == 0:
        return "錯誤：除數不能為零"

    try:
        result = a / b
        return f"{a} ÷ {b} = {result}"
    except Exception as e:
        return f"計算錯誤：{str(e)}"


@tool
def validate_email(email: str) -> Dict[str, any]:
    """驗證郵箱地址

    Args:
        email: 郵箱地址

    Returns:
        驗證結果字典
    """
    import re

    # 簡單的郵箱正則
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    is_valid = bool(re.match(pattern, email))

    return {
        "email": email,
        "is_valid": is_valid,
        "message": "有效的郵箱地址" if is_valid else "無效的郵箱地址"
    }


# ============================================================================
# 5. 創建使用工具的 Agent
# ============================================================================

def create_time_agent():
    """創建能查詢時間的 Agent"""
    return Agent(
        name="時間助手",
        model="gpt-4",
        instructions="你可以告訴用戶當前時間。使用繁體中文回答。",
        tools=[get_current_time]
    )


def create_calculator_agent():
    """創建計算器 Agent"""
    return Agent(
        name="計算器",
        model="gpt-4",
        instructions="""你是一個計算器助手。
        當用戶要求計算時，使用 calculate 工具。
        使用繁體中文回答。""",
        tools=[calculate, divide_numbers]
    )


def create_search_agent():
    """創建搜索 Agent"""
    return Agent(
        name="搜索助手",
        model="gpt-4",
        instructions="""你是一個購物助手。
        當用戶搜索商品時，使用 search_database 工具。
        當用戶詢問天氣時，使用 get_weather 工具。
        使用繁體中文回答。""",
        tools=[search_database, get_weather]
    )


def create_multi_tool_agent():
    """創建多功能 Agent"""
    return Agent(
        name="多功能助手",
        model="gpt-4",
        instructions="""你是一個多功能助手，可以：
        1. 告訴時間
        2. 執行計算
        3. 搜索商品
        4. 查詢天氣
        5. 獲取用戶資料
        6. 驗證郵箱

        根據用戶需求選擇合適的工具。使用繁體中文回答。""",
        tools=[
            get_current_time,
            calculate,
            search_database,
            get_weather,
            get_user_profile,
            validate_email,
            divide_numbers
        ]
    )


# ============================================================================
# 6. 測試範例
# ============================================================================

def test_time_tool():
    """測試時間工具"""
    print("\n" + "="*60)
    print("範例 1: 時間查詢工具")
    print("="*60)

    agent = create_time_agent()
    messages = [{"role": "user", "content": "現在幾點？"}]

    response = run(agent=agent, messages=messages)

    print(f"\n用戶: {messages[0]['content']}")
    print(f"助手: {response.messages[-1]['content']}")

    # 檢查是否使用了工具
    for msg in response.messages:
        if msg.get("tool_calls"):
            print(f"\n[工具調用]")
            for tool_call in msg["tool_calls"]:
                print(f"  工具: {tool_call['function']['name']}")


def test_calculator_tool():
    """測試計算工具"""
    print("\n" + "="*60)
    print("範例 2: 計算器工具")
    print("="*60)

    agent = create_calculator_agent()

    test_cases = [
        "請計算 15 + 27",
        "100 除以 4 等於多少？",
        "5 除以 0 會怎樣？"  # 測試錯誤處理
    ]

    for question in test_cases:
        messages = [{"role": "user", "content": question}]
        response = run(agent=agent, messages=messages)

        print(f"\n用戶: {question}")
        print(f"助手: {response.messages[-1]['content']}")


def test_search_tool():
    """測試搜索工具"""
    print("\n" + "="*60)
    print("範例 3: 搜索工具")
    print("="*60)

    agent = create_search_agent()

    test_cases = [
        "幫我找電子產品",
        "台北的天氣如何？",
        "搜索書籍分類的商品"
    ]

    for question in test_cases:
        messages = [{"role": "user", "content": question}]
        response = run(agent=agent, messages=messages)

        print(f"\n用戶: {question}")
        print(f"助手: {response.messages[-1]['content']}")


def test_multi_tool():
    """測試多工具 Agent"""
    print("\n" + "="*60)
    print("範例 4: 多工具整合")
    print("="*60)

    agent = create_multi_tool_agent()

    # 複雜查詢
    question = "請幫我：1) 查詢用戶 U001 的資料，2) 驗證郵箱 test@example.com"

    messages = [{"role": "user", "content": question}]
    response = run(agent=agent, messages=messages)

    print(f"\n用戶: {question}")
    print(f"助手: {response.messages[-1]['content']}")

    # 統計工具使用
    tool_calls = []
    for msg in response.messages:
        if msg.get("tool_calls"):
            for tc in msg["tool_calls"]:
                tool_calls.append(tc['function']['name'])

    print(f"\n[使用的工具] {', '.join(tool_calls)}")


# ============================================================================
# 7. 工具調用細節分析
# ============================================================================

def analyze_tool_calls():
    """分析工具調用的詳細過程"""
    print("\n" + "="*60)
    print("範例 5: 工具調用細節分析")
    print("="*60)

    agent = create_calculator_agent()
    messages = [{"role": "user", "content": "計算 (10 + 5) * 3"}]

    response = run(agent=agent, messages=messages)

    print("\n完整對話流程：")
    for i, msg in enumerate(response.messages, 1):
        role = msg.get("role", "unknown")
        content = msg.get("content", "")

        print(f"\n步驟 {i}: {role}")

        if msg.get("tool_calls"):
            print("  [工具調用]")
            for tc in msg["tool_calls"]:
                func_name = tc['function']['name']
                func_args = tc['function']['arguments']
                print(f"    函數: {func_name}")
                print(f"    參數: {func_args}")

        elif role == "tool":
            print(f"  [工具結果] {content}")

        elif content:
            print(f"  {content}")


# ============================================================================
# 8. 與 Swarm 對比
# ============================================================================

def swarm_vs_agents_tools():
    """對比 Swarm 和 Agents SDK 的工具定義"""
    print("\n" + "="*60)
    print("範例 6: 工具定義對比")
    print("="*60)

    print("\n【Swarm 風格】")
    print("""
    def get_time():
        '''獲取當前時間'''
        return datetime.now().strftime("%H:%M:%S")

    agent = Agent(
        name="助手",
        functions=[get_time]  # 直接傳遞函數
    )
    """)

    print("\n【Agents SDK 風格】")
    print("""
    from openai_agents import tool

    @tool  # 使用裝飾器
    def get_time() -> str:  # 類型提示（必需）
        '''獲取當前時間

        Returns:
            格式化的時間字符串
        '''
        return datetime.now().strftime("%H:%M:%S")

    agent = Agent(
        name="助手",
        tools=[get_time]  # 使用 tools 參數
    )
    """)

    print("\n主要差異:")
    print("  1. Agents SDK 使用 @tool 裝飾器（自動生成 JSON Schema）")
    print("  2. 必須提供類型提示（Type Hints）")
    print("  3. 參數名稱從 'functions' 改為 'tools'")
    print("  4. 更好的文檔字符串支持（自動解析為工具描述）")
    print("  5. 更強的類型檢查和驗證")


# ============================================================================
# 主程序
# ============================================================================

def main():
    """運行所有範例"""
    print("="*60)
    print("OpenAI Agents SDK - 工具函數範例")
    print("="*60)

    # 配置環境
    configure(
        api_key=os.getenv("OPENAI_API_KEY"),
        timeout=60
    )
    print("✓ 環境配置完成")

    # 運行各個範例
    try:
        test_time_tool()
        test_calculator_tool()
        test_search_tool()
        test_multi_tool()
        analyze_tool_calls()
        swarm_vs_agents_tools()
    except Exception as e:
        print(f"\n錯誤: {e}")
        print("請確保已設置 OPENAI_API_KEY 環境變量")

    print("\n" + "="*60)
    print("所有範例運行完成！")
    print("="*60)

    # 總結
    print("\n工具函數最佳實踐：")
    print("  1. 使用 @tool 裝飾器")
    print("  2. 提供完整的類型提示")
    print("  3. 寫清晰的文檔字符串（包含 Args 和 Returns）")
    print("  4. 實現適當的錯誤處理")
    print("  5. 返回結構化數據（dict）而不是純文本")


if __name__ == "__main__":
    main()

"""
Code Agent 深入解析
==================

Code Agent 是 smolagents 的核心創新：
- 不輸出 JSON 工具調用
- 直接生成 Python 代碼
- 更強的推理和靈活性

本範例展示：
1. Code Agent 的工作原理
2. 與傳統 Tool Calling 的對比
3. 複雜邏輯處理能力
4. 代碼生成和執行流程
"""

from smolagents import CodeAgent, HfApiModel, tool
import json


# ============================================================================
# 自定義工具用於演示
# ============================================================================

@tool
def get_weather(city: str) -> dict:
    """
    獲取城市天氣（模擬數據）

    Args:
        city: 城市名稱

    Returns:
        包含天氣信息的字典
    """
    # 模擬天氣 API
    weather_data = {
        "台北": {"temp": 28, "condition": "晴天", "humidity": 65},
        "台中": {"temp": 30, "condition": "多雲", "humidity": 70},
        "高雄": {"temp": 32, "condition": "晴天", "humidity": 75},
    }
    return weather_data.get(city, {"temp": 25, "condition": "未知", "humidity": 60})


@tool
def get_stock_price(symbol: str) -> float:
    """
    獲取股票價格（模擬數據）

    Args:
        symbol: 股票代號

    Returns:
        股票價格
    """
    # 模擬股票數據
    stocks = {
        "AAPL": 175.23,
        "GOOGL": 142.56,
        "TSMC": 98.45,
        "NVDA": 495.78,
    }
    return stocks.get(symbol, 100.0)


@tool
def calculate(expression: str) -> float:
    """
    計算數學表達式

    Args:
        expression: 數學表達式字符串

    Returns:
        計算結果
    """
    try:
        # 安全評估數學表達式
        return eval(expression, {"__builtins__": {}}, {})
    except:
        return 0.0


# ============================================================================
# 範例 1: Code Agent 的基本工作原理
# ============================================================================

def example_1_how_code_agent_works():
    """展示 Code Agent 如何生成和執行代碼"""
    print("\n" + "="*70)
    print("範例 1: Code Agent 的工作原理")
    print("="*70)

    model = HfApiModel()
    tools = [get_weather, calculate]

    agent = CodeAgent(
        tools=tools,
        model=model,
        max_steps=5
    )

    print("\nCode Agent 的執行流程：")
    print("1. 接收任務: '查詢台北天氣並計算體感溫度'")
    print("2. LLM 生成 Python 代碼:")
    print("   ```python")
    print("   weather = get_weather('台北')")
    print("   feels_like = calculate(f\"{weather['temp']} + {weather['humidity']} * 0.1\")")
    print("   print(f'台北: {weather['temp']}°C, 體感 {feels_like}°C')")
    print("   ```")
    print("3. 在沙盒中執行代碼")
    print("4. 返回執行結果\n")

    result = agent.run(
        "查詢台北的天氣，並根據溫度和濕度計算體感溫度（溫度 + 濕度*0.1）"
    )

    print(f"\n結果: {result}")


# ============================================================================
# 範例 2: Code Agent vs Tool Calling 對比
# ============================================================================

def example_2_code_vs_tool_calling():
    """對比 Code Agent 和 Tool Calling 的差異"""
    print("\n" + "="*70)
    print("範例 2: Code Agent vs Tool Calling 對比")
    print("="*70)

    print("\n傳統 Tool Calling Agent:")
    print("---")
    print("步驟 1: 調用 get_weather('台北')")
    print("  → 返回: {'temp': 28, 'condition': '晴天', 'humidity': 65}")
    print("步驟 2: 調用 get_weather('台中')")
    print("  → 返回: {'temp': 30, 'condition': '多雲', 'humidity': 70}")
    print("步驟 3: 調用 get_weather('高雄')")
    print("  → 返回: {'temp': 32, 'condition': '晴天', 'humidity': 75}")
    print("步驟 4: LLM 整理結果")
    print("\n總共: 4 個步驟，3 次工具調用\n")

    print("\nCode Agent:")
    print("---")
    print("步驟 1: 生成並執行代碼:")
    print("```python")
    print("cities = ['台北', '台中', '高雄']")
    print("results = []")
    print("for city in cities:")
    print("    weather = get_weather(city)")
    print("    results.append(f\"{city}: {weather['temp']}°C, {weather['condition']}\")")
    print("print('\\n'.join(results))")
    print("```")
    print("\n總共: 1 個步驟！\n")

    # 實際執行 Code Agent
    model = HfApiModel()
    tools = [get_weather]

    agent = CodeAgent(
        tools=tools,
        model=model,
        max_steps=3
    )

    result = agent.run(
        "查詢台北、台中、高雄的天氣，用表格格式顯示"
    )

    print(f"Code Agent 結果:\n{result}")


# ============================================================================
# 範例 3: 複雜數據處理
# ============================================================================

def example_3_complex_data_processing():
    """展示 Code Agent 處理複雜數據的能力"""
    print("\n" + "="*70)
    print("範例 3: 複雜數據處理")
    print("="*70)

    model = HfApiModel()
    tools = [get_stock_price, calculate]

    agent = CodeAgent(
        tools=tools,
        model=model,
        max_steps=5
    )

    print("\nCode Agent 可以直接使用 Python 的數據處理能力：")
    print("- 列表推導式")
    print("- 字典操作")
    print("- 循環和條件判斷")
    print("- 數據排序和過濾\n")

    result = agent.run(
        "獲取 AAPL, GOOGL, TSMC, NVDA 的股價，"
        "計算總價值，找出最高和最低的股票，並按價格排序"
    )

    print(f"\n結果:\n{result}")


# ============================================================================
# 範例 4: 錯誤處理和重試
# ============================================================================

def example_4_error_handling():
    """Code Agent 可以編寫錯誤處理邏輯"""
    print("\n" + "="*70)
    print("範例 4: 錯誤處理和重試")
    print("="*70)

    @tool
    def unreliable_api(query: str) -> str:
        """
        一個不穩定的 API（模擬）

        Args:
            query: 查詢參數

        Returns:
            API 響應
        """
        import random
        if random.random() > 0.5:
            raise Exception("API 暫時不可用")
        return f"查詢 '{query}' 的結果"

    model = HfApiModel()
    tools = [unreliable_api]

    agent = CodeAgent(
        tools=tools,
        model=model,
        max_steps=8
    )

    print("\nCode Agent 可以生成包含 try-except 的代碼：")
    print("```python")
    print("max_retries = 3")
    print("for i in range(max_retries):")
    print("    try:")
    print("        result = unreliable_api('數據')")
    print("        print(f'成功: {result}')")
    print("        break")
    print("    except Exception as e:")
    print("        if i == max_retries - 1:")
    print("            print(f'失敗: {e}')")
    print("        else:")
    print("            print(f'重試 {i+1}/{max_retries}')")
    print("```\n")

    result = agent.run(
        "調用 unreliable_api，如果失敗則重試最多 3 次"
    )

    print(f"\n結果:\n{result}")


# ============================================================================
# 範例 5: 多步驟推理
# ============================================================================

def example_5_multi_step_reasoning():
    """Code Agent 的多步驟推理能力"""
    print("\n" + "="*70)
    print("範例 5: 多步驟推理")
    print("="*70)

    model = HfApiModel()
    tools = [get_weather, get_stock_price, calculate]

    agent = CodeAgent(
        tools=tools,
        model=model,
        max_steps=10
    )

    print("\nCode Agent 可以執行複雜的多步驟推理：")
    print("1. 獲取數據")
    print("2. 進行計算")
    print("3. 條件判斷")
    print("4. 格式化輸出\n")

    result = agent.run(
        "如果台北溫度超過 25 度，推薦買 TSMC 股票；"
        "否則推薦買 AAPL 股票。計算投資 10000 元可以買多少股。"
    )

    print(f"\n結果:\n{result}")


# ============================================================================
# 範例 6: 查看生成的代碼
# ============================================================================

def example_6_inspect_generated_code():
    """查看 Code Agent 生成的實際代碼"""
    print("\n" + "="*70)
    print("範例 6: 查看生成的代碼")
    print("="*70)

    model = HfApiModel()
    tools = [get_weather, calculate]

    # 創建 Agent
    agent = CodeAgent(
        tools=tools,
        model=model,
        max_steps=5
    )

    print("\n我們可以通過啟用詳細輸出來查看 Agent 生成的代碼：\n")

    # 運行並查看詳細輸出
    result = agent.run(
        "查詢台北和高雄的天氣，比較哪個城市更熱",
        verbose=2  # 最高詳細級別
    )

    print(f"\n最終結果:\n{result}")


# ============================================================================
# 範例 7: Code Agent 的優勢總結
# ============================================================================

def example_7_advantages_summary():
    """總結 Code Agent 的優勢"""
    print("\n" + "="*70)
    print("範例 7: Code Agent 優勢總結")
    print("="*70)

    print("\nCode Agent 的主要優勢：\n")

    advantages = [
        {
            "優勢": "更強的推理能力",
            "說明": "LLM 可以編寫完整的邏輯，而不是單步工具調用",
            "範例": "循環處理多個項目，而不是分別調用工具"
        },
        {
            "優勢": "更高的靈活性",
            "說明": "可以使用 Python 的全部功能",
            "範例": "列表推導、字典操作、條件判斷"
        },
        {
            "優勢": "更少的步驟",
            "說明": "一次生成完整解決方案，而不是多次往返",
            "範例": "處理 10 個城市天氣只需 1 步，而非 10 步"
        },
        {
            "優勢": "內建錯誤處理",
            "說明": "可以生成 try-except 代碼",
            "範例": "自動重試失敗的 API 調用"
        },
        {
            "優勢": "複雜數據處理",
            "說明": "可以使用 pandas、numpy 等庫",
            "範例": "數據分析、統計計算"
        },
    ]

    for i, adv in enumerate(advantages, 1):
        print(f"{i}. {adv['優勢']}")
        print(f"   說明: {adv['說明']}")
        print(f"   範例: {adv['範例']}\n")

    print("注意事項：")
    print("- Code Agent 需要在沙盒環境中運行以確保安全")
    print("- 對於簡單任務，Tool Calling Agent 可能更高效")
    print("- 選擇合適的 Agent 類型取決於任務複雜度")


# ============================================================================
# 主程式
# ============================================================================

def main():
    """運行所有範例"""
    print("\n" + "="*70)
    print("Code Agent 深入解析")
    print("="*70)

    examples = [
        ("範例 1: Code Agent 的工作原理", example_1_how_code_agent_works),
        ("範例 2: Code Agent vs Tool Calling", example_2_code_vs_tool_calling),
        ("範例 3: 複雜數據處理", example_3_complex_data_processing),
        ("範例 4: 錯誤處理和重試", example_4_error_handling),
        ("範例 5: 多步驟推理", example_5_multi_step_reasoning),
        ("範例 6: 查看生成的代碼", example_6_inspect_generated_code),
        ("範例 7: 優勢總結", example_7_advantages_summary),
    ]

    for name, func in examples:
        try:
            func()
        except Exception as e:
            print(f"\n{name} 執行失敗: {e}")

    print("\n" + "="*70)
    print("Code Agent 解析完成！")
    print("="*70)
    print("\n關鍵要點：")
    print("  - Code Agent 生成 Python 代碼，不是 JSON")
    print("  - 更強的推理和靈活性")
    print("  - 適合複雜任務和數據處理")
    print("  - 需要沙盒環境保證安全")
    print("\n下一步: 查看 03_ToolCallingAgent.py 了解傳統工具調用方式")


if __name__ == "__main__":
    main()

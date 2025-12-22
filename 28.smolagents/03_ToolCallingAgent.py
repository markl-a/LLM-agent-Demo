"""
ToolCallingAgent - 傳統工具調用 Agent
====================================

ToolCallingAgent 是更傳統的 Agent 類型：
- LLM 輸出 JSON 格式的工具調用
- 框架解析並執行工具
- 更可控、更安全

本範例展示：
1. ToolCallingAgent 的使用方法
2. 與 CodeAgent 的對比
3. 適用場景
4. 優缺點分析
"""

from smolagents import ToolCallingAgent, CodeAgent, HfApiModel, tool
import json
import time


# ============================================================================
# 準備測試工具
# ============================================================================

@tool
def search_database(query: str, limit: int = 5) -> list:
    """
    搜索數據庫

    Args:
        query: 搜索關鍵字
        limit: 返回結果數量限制

    Returns:
        搜索結果列表
    """
    # 模擬數據庫
    database = [
        {"id": 1, "title": "Python 教程", "category": "編程"},
        {"id": 2, "title": "機器學習入門", "category": "AI"},
        {"id": 3, "title": "Web 開發指南", "category": "編程"},
        {"id": 4, "title": "數據分析實戰", "category": "數據"},
        {"id": 5, "title": "深度學習基礎", "category": "AI"},
    ]

    results = [
        item for item in database
        if query.lower() in item["title"].lower() or query.lower() in item["category"].lower()
    ]

    return results[:limit]


@tool
def get_user_info(user_id: int) -> dict:
    """
    獲取用戶信息

    Args:
        user_id: 用戶 ID

    Returns:
        用戶信息字典
    """
    users = {
        1: {"name": "張三", "role": "開發者", "level": "高級"},
        2: {"name": "李四", "role": "設計師", "level": "中級"},
        3: {"name": "王五", "role": "產品經理", "level": "高級"},
    }
    return users.get(user_id, {"name": "未知", "role": "未知", "level": "未知"})


@tool
def send_notification(user_id: int, message: str) -> bool:
    """
    發送通知給用戶

    Args:
        user_id: 用戶 ID
        message: 通知內容

    Returns:
        是否成功發送
    """
    print(f"📧 發送通知給用戶 {user_id}: {message}")
    return True


# ============================================================================
# 範例 1: ToolCallingAgent 基本使用
# ============================================================================

def example_1_basic_tool_calling():
    """ToolCallingAgent 的基本使用"""
    print("\n" + "="*70)
    print("範例 1: ToolCallingAgent 基本使用")
    print("="*70)

    model = HfApiModel()
    tools = [search_database, get_user_info]

    # 創建 ToolCallingAgent
    agent = ToolCallingAgent(
        tools=tools,
        model=model,
        max_steps=10
    )

    print("\nToolCallingAgent 的執行流程：")
    print("1. 接收任務")
    print("2. LLM 決定調用哪個工具")
    print("3. 輸出 JSON 格式的工具調用")
    print("4. 框架解析 JSON 並執行工具")
    print("5. 將結果返回給 LLM")
    print("6. 重複 2-5 直到任務完成\n")

    result = agent.run(
        "搜索關於 'AI' 的內容，返回前 3 個結果"
    )

    print(f"\n結果:\n{result}")


# ============================================================================
# 範例 2: ToolCallingAgent vs CodeAgent 對比
# ============================================================================

def example_2_comparison():
    """對比兩種 Agent 的執行方式"""
    print("\n" + "="*70)
    print("範例 2: ToolCallingAgent vs CodeAgent 對比")
    print("="*70)

    model = HfApiModel()
    tools = [search_database]

    # 同一個任務
    task = "搜索 'Python' 相關內容，並統計結果數量"

    # ToolCallingAgent
    print("\n--- ToolCallingAgent 執行 ---")
    print("步驟 1: LLM 輸出")
    print('{"tool": "search_database", "arguments": {"query": "Python", "limit": 5}}')
    print("步驟 2: 執行工具")
    print("步驟 3: LLM 處理結果並統計數量\n")

    tool_agent = ToolCallingAgent(tools=tools, model=model, max_steps=5)
    result1 = tool_agent.run(task)
    print(f"結果: {result1}")

    # CodeAgent
    print("\n--- CodeAgent 執行 ---")
    print("步驟 1: LLM 生成代碼")
    print("```python")
    print("results = search_database('Python', limit=5)")
    print("count = len(results)")
    print("print(f'找到 {count} 個結果')")
    print("print(results)")
    print("```")
    print("步驟 2: 執行代碼\n")

    code_agent = CodeAgent(tools=tools, model=model, max_steps=3)
    result2 = code_agent.run(task)
    print(f"結果: {result2}")


# ============================================================================
# 範例 3: ToolCallingAgent 的優勢 - 可控性
# ============================================================================

def example_3_control_and_safety():
    """ToolCallingAgent 的可控性和安全性"""
    print("\n" + "="*70)
    print("範例 3: 可控性和安全性")
    print("="*70)

    model = HfApiModel()
    tools = [search_database, get_user_info, send_notification]

    agent = ToolCallingAgent(
        tools=tools,
        model=model,
        max_steps=10
    )

    print("\nToolCallingAgent 的安全優勢：")
    print("1. 只能調用預定義的工具")
    print("2. 工具調用參數類型檢查")
    print("3. 不執行任意代碼")
    print("4. 易於審計和監控")
    print("5. 可以設置權限控制\n")

    # 這個任務是安全的
    result = agent.run(
        "搜索 AI 相關內容，獲取用戶 1 的信息，"
        "然後發送通知告訴他搜索結果"
    )

    print(f"\n結果:\n{result}")

    print("\n注意：ToolCallingAgent 不會執行任何未定義的操作")


# ============================================================================
# 範例 4: 工具調用鏈的可視化
# ============================================================================

def example_4_tool_call_chain():
    """可視化工具調用鏈"""
    print("\n" + "="*70)
    print("範例 4: 工具調用鏈可視化")
    print("="*70)

    @tool
    def step_tracker(step_name: str, data: str) -> str:
        """
        追蹤執行步驟（用於演示）

        Args:
            step_name: 步驟名稱
            data: 步驟數據

        Returns:
            步驟確認
        """
        print(f"  └─ 執行步驟: {step_name}")
        print(f"     數據: {data}")
        return f"完成 {step_name}"

    model = HfApiModel()
    tools = [step_tracker]

    agent = ToolCallingAgent(
        tools=tools,
        model=model,
        max_steps=8
    )

    print("\n追蹤 Agent 的工具調用鏈：\n")

    result = agent.run(
        "執行以下步驟：1) 初始化數據 2) 處理數據 3) 保存結果",
        verbose=1  # 顯示中等詳細程度
    )

    print(f"\n最終結果: {result}")


# ============================================================================
# 範例 5: 適用場景分析
# ============================================================================

def example_5_use_cases():
    """分析兩種 Agent 的適用場景"""
    print("\n" + "="*70)
    print("範例 5: 適用場景分析")
    print("="*70)

    scenarios = [
        {
            "場景": "簡單的 CRUD 操作",
            "推薦": "ToolCallingAgent",
            "原因": "操作簡單、可預測，不需要複雜邏輯"
        },
        {
            "場景": "數據分析和統計",
            "推薦": "CodeAgent",
            "原因": "需要複雜的數據處理和計算"
        },
        {
            "場景": "生產環境的 API 調用",
            "推薦": "ToolCallingAgent",
            "原因": "更安全、可控，易於監控"
        },
        {
            "場景": "多步驟推理任務",
            "推薦": "CodeAgent",
            "原因": "可以編寫完整的邏輯流程"
        },
        {
            "場景": "受限環境（無沙盒）",
            "推薦": "ToolCallingAgent",
            "原因": "不執行任意代碼，更安全"
        },
        {
            "場景": "探索性數據分析",
            "推薦": "CodeAgent",
            "原因": "靈活性高，可以使用 pandas 等庫"
        },
    ]

    print("\n場景對比表：\n")
    for i, scenario in enumerate(scenarios, 1):
        print(f"{i}. {scenario['場景']}")
        print(f"   推薦: {scenario['推薦']}")
        print(f"   原因: {scenario['原因']}\n")


# ============================================================================
# 範例 6: 混合使用
# ============================================================================

def example_6_hybrid_approach():
    """混合使用兩種 Agent"""
    print("\n" + "="*70)
    print("範例 6: 混合使用策略")
    print("="*70)

    print("\n在實際應用中，可以根據任務特性選擇合適的 Agent：\n")

    model = HfApiModel()
    tools = [search_database, get_user_info]

    # 簡單任務用 ToolCallingAgent
    print("1. 簡單查詢任務 → ToolCallingAgent")
    tool_agent = ToolCallingAgent(tools=tools, model=model, max_steps=5)
    result1 = tool_agent.run("獲取用戶 1 的信息")
    print(f"   結果: {result1}\n")

    # 複雜任務用 CodeAgent
    print("2. 複雜分析任務 → CodeAgent")
    code_agent = CodeAgent(tools=tools, model=model, max_steps=5)
    result2 = code_agent.run(
        "搜索所有類別的內容，統計每個類別的數量，"
        "並找出最多的類別"
    )
    print(f"   結果: {result2}\n")

    print("混合策略的優勢：")
    print("  - 簡單任務快速執行")
    print("  - 複雜任務靈活處理")
    print("  - 平衡性能和安全性")


# ============================================================================
# 範例 7: 性能對比
# ============================================================================

def example_7_performance():
    """對比兩種 Agent 的性能"""
    print("\n" + "="*70)
    print("範例 7: 性能對比")
    print("="*70)

    model = HfApiModel()
    tools = [search_database]

    # 測試任務
    task = "搜索 'Python' 並返回結果"

    # ToolCallingAgent
    print("\n測試 ToolCallingAgent...")
    tool_agent = ToolCallingAgent(tools=tools, model=model, max_steps=5)
    start = time.time()
    result1 = tool_agent.run(task)
    time1 = time.time() - start

    # CodeAgent
    print("\n測試 CodeAgent...")
    code_agent = CodeAgent(tools=tools, model=model, max_steps=5)
    start = time.time()
    result2 = code_agent.run(task)
    time2 = time.time() - start

    print("\n性能對比：")
    print(f"  ToolCallingAgent: {time1:.2f} 秒")
    print(f"  CodeAgent: {time2:.2f} 秒")

    print("\n性能特點：")
    print("  - ToolCallingAgent: 簡單任務通常更快")
    print("  - CodeAgent: 複雜任務可能一步完成，總體更快")
    print("  - 實際性能取決於任務複雜度和模型能力")


# ============================================================================
# 主程式
# ============================================================================

def main():
    """運行所有範例"""
    print("\n" + "="*70)
    print("ToolCallingAgent - 傳統工具調用 Agent")
    print("="*70)

    examples = [
        ("範例 1: 基本使用", example_1_basic_tool_calling),
        ("範例 2: 對比分析", example_2_comparison),
        ("範例 3: 可控性和安全性", example_3_control_and_safety),
        ("範例 4: 工具調用鏈", example_4_tool_call_chain),
        ("範例 5: 適用場景", example_5_use_cases),
        ("範例 6: 混合使用", example_6_hybrid_approach),
        ("範例 7: 性能對比", example_7_performance),
    ]

    for name, func in examples:
        try:
            func()
        except Exception as e:
            print(f"\n{name} 執行失敗: {e}")

    print("\n" + "="*70)
    print("ToolCallingAgent 解析完成！")
    print("="*70)

    print("\n總結：")
    print("\nToolCallingAgent 優勢：")
    print("  ✓ 更可控、更安全")
    print("  ✓ 易於審計和監控")
    print("  ✓ 適合生產環境")
    print("  ✓ 簡單任務執行快")

    print("\nCodeAgent 優勢：")
    print("  ✓ 更靈活、更強大")
    print("  ✓ 複雜邏輯處理好")
    print("  ✓ 可使用完整 Python")
    print("  ✓ 多步驟任務效率高")

    print("\n選擇建議：")
    print("  - 生產環境、簡單任務 → ToolCallingAgent")
    print("  - 開發環境、複雜任務 → CodeAgent")
    print("  - 實際應用中可以混合使用")

    print("\n下一步: 查看 04_自定義工具.py 學習創建自己的工具")


if __name__ == "__main__":
    main()

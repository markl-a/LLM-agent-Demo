"""
smolagents 快速入門
==================

本範例展示如何使用 30 行代碼創建您的第一個 Agent。
smolagents 的設計理念就是極簡 - 核心代碼僅約 1000 行！

主要內容：
1. 基本的 Agent 創建
2. 使用內建工具
3. 執行簡單任務
4. 理解 Code Agent 的工作原理
"""

import os
from smolagents import CodeAgent, HfApiModel, DuckDuckGoSearchTool, VisitWebpageTool

# ============================================================================
# 範例 1: 最簡單的 30 行 Agent
# ============================================================================

def example_1_minimal_agent():
    """最簡單的 Agent - 只需要 30 行代碼！"""
    print("\n" + "="*70)
    print("範例 1: 最簡單的 30 行 Agent")
    print("="*70)

    # 步驟 1: 選擇模型（使用 Hugging Face 的免費推理 API）
    model = HfApiModel()

    # 步驟 2: 準備工具（使用內建的網頁搜索工具）
    tools = [DuckDuckGoSearchTool()]

    # 步驟 3: 創建 Agent（Code Agent 會生成並執行 Python 代碼）
    agent = CodeAgent(
        tools=tools,
        model=model,
        max_steps=10  # 最多執行 10 個步驟
    )

    # 步驟 4: 運行任務
    result = agent.run(
        "搜索 smolagents 框架的主要特點，用繁體中文回答"
    )

    print(f"\n結果:\n{result}")
    print("\n就這麼簡單！Agent 已經完成了搜索並整理了結果。")


# ============================================================================
# 範例 2: 使用多個工具
# ============================================================================

def example_2_multiple_tools():
    """使用多個工具的 Agent"""
    print("\n" + "="*70)
    print("範例 2: 使用多個工具")
    print("="*70)

    # 創建模型
    model = HfApiModel()

    # 準備多個工具
    tools = [
        DuckDuckGoSearchTool(),    # 搜索工具
        VisitWebpageTool(),        # 網頁訪問工具
    ]

    # 創建 Agent
    agent = CodeAgent(
        tools=tools,
        model=model,
        max_steps=15
    )

    # 運行更複雜的任務
    result = agent.run(
        "搜索 Hugging Face smolagents 的官方文檔，"
        "訪問第一個結果，並總結主要功能"
    )

    print(f"\n結果:\n{result}")


# ============================================================================
# 範例 3: 理解 Code Agent 的工作原理
# ============================================================================

def example_3_understanding_code_agent():
    """理解 Code Agent 如何工作"""
    print("\n" + "="*70)
    print("範例 3: 理解 Code Agent 的工作原理")
    print("="*70)

    model = HfApiModel()
    tools = [DuckDuckGoSearchTool()]

    # 創建 Agent，啟用詳細輸出
    agent = CodeAgent(
        tools=tools,
        model=model,
        max_steps=5
    )

    print("\nCode Agent 的工作流程：")
    print("1. 接收任務描述")
    print("2. LLM 生成 Python 代碼來解決任務")
    print("3. 在沙盒環境中執行代碼")
    print("4. 根據執行結果決定下一步")
    print("5. 重複步驟 2-4 直到任務完成\n")

    # 運行任務並觀察過程
    result = agent.run(
        "搜索今天的日期",
        verbose=2  # 最詳細的輸出級別
    )

    print(f"\n最終結果:\n{result}")

    print("\n注意：Code Agent 生成的是真正的 Python 代碼，不是 JSON！")
    print("這讓它能處理更複雜的邏輯和數據處理。")


# ============================================================================
# 範例 4: 使用環境變數配置
# ============================================================================

def example_4_with_api_key():
    """使用 OpenAI API（需要 API key）"""
    print("\n" + "="*70)
    print("範例 4: 使用 OpenAI API（可選）")
    print("="*70)

    # 檢查是否有 OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\n未設置 OPENAI_API_KEY，跳過此範例")
        print("如需使用 OpenAI，請設置環境變數：")
        print("  export OPENAI_API_KEY='your-api-key'")
        return

    from smolagents import OpenAIModel

    # 使用 OpenAI 模型
    model = OpenAIModel(model_id="gpt-4o-mini")

    tools = [DuckDuckGoSearchTool()]

    agent = CodeAgent(
        tools=tools,
        model=model,
        max_steps=10
    )

    result = agent.run("搜索 Python 3.13 的新特性")

    print(f"\n結果:\n{result}")


# ============================================================================
# 範例 5: 錯誤處理
# ============================================================================

def example_5_error_handling():
    """演示基本的錯誤處理"""
    print("\n" + "="*70)
    print("範例 5: 錯誤處理")
    print("="*70)

    model = HfApiModel()
    tools = [DuckDuckGoSearchTool()]

    agent = CodeAgent(
        tools=tools,
        model=model,
        max_steps=5
    )

    try:
        # 嘗試執行任務
        result = agent.run("這是一個可能失敗的任務")
        print(f"\n成功: {result}")

    except Exception as e:
        # 捕獲錯誤
        print(f"\n發生錯誤: {type(e).__name__}")
        print(f"錯誤訊息: {str(e)}")
        print("\n建議:")
        print("- 檢查網絡連接")
        print("- 確認 API 配額")
        print("- 簡化任務描述")


# ============================================================================
# 主程式
# ============================================================================

def main():
    """運行所有範例"""
    print("\n" + "="*70)
    print("smolagents 快速入門 - 從零到 Agent")
    print("="*70)

    print("\nsmolagents 是 Hugging Face 開發的極簡 Agent 框架")
    print("特點：")
    print("  - 核心代碼僅 ~1000 行")
    print("  - Code Agent 生成並執行 Python 代碼")
    print("  - 多模態支持（文本、圖像、音頻）")
    print("  - 沙盒執行保證安全")
    print("  - Hub 整合方便分享")

    # 運行各個範例
    try:
        example_1_minimal_agent()
    except Exception as e:
        print(f"\n範例 1 執行失敗: {e}")

    try:
        example_2_multiple_tools()
    except Exception as e:
        print(f"\n範例 2 執行失敗: {e}")

    try:
        example_3_understanding_code_agent()
    except Exception as e:
        print(f"\n範例 3 執行失敗: {e}")

    try:
        example_4_with_api_key()
    except Exception as e:
        print(f"\n範例 4 執行失敗: {e}")

    try:
        example_5_error_handling()
    except Exception as e:
        print(f"\n範例 5 執行失敗: {e}")

    print("\n" + "="*70)
    print("快速入門完成！")
    print("="*70)
    print("\n下一步:")
    print("  - 查看 02_CodeAgent.py 深入了解 Code Agent")
    print("  - 查看 04_自定義工具.py 學習創建自己的工具")
    print("  - 查看 README.md 了解所有功能")


if __name__ == "__main__":
    main()

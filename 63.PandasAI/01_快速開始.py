"""
PandasAI 快速開始示例

這個示例展示了如何使用 PandasAI 的基本功能：
1. 創建 DataFrame
2. 初始化 PandasAI Agent
3. 使用自然語言進行數據查詢
4. 處理不同類型的問題

作者：PandasAI 示例
日期：2025-12-31
"""

import os
import pandas as pd
from dotenv import load_dotenv

# 載入環境變量
load_dotenv()


def create_sample_dataframe():
    """
    創建示例數據集

    Returns:
        pd.DataFrame: 包含銷售數據的 DataFrame
    """
    data = {
        "產品名稱": ["筆記本電腦", "智能手機", "平板電腦", "智能手錶", "耳機"],
        "類別": ["電腦", "手機", "電腦", "配件", "配件"],
        "銷售數量": [150, 450, 200, 350, 600],
        "單價": [35000, 12000, 15000, 8000, 2500],
        "評分": [4.5, 4.3, 4.2, 4.6, 4.4]
    }

    df = pd.DataFrame(data)

    # 計算總銷售額
    df["總銷售額"] = df["銷售數量"] * df["單價"]

    return df


def basic_chat_example(agent):
    """
    基本對話示例

    Args:
        agent: PandasAI Agent 實例
    """
    print("\n" + "="*60)
    print("基本對話示例")
    print("="*60)

    questions = [
        "這個數據集有多少行？",
        "哪個產品的銷售數量最多？",
        "所有產品的平均評分是多少？",
        "總銷售額最高的產品是什麼？",
        "列出所有配件類別的產品"
    ]

    for i, question in enumerate(questions, 1):
        try:
            print(f"\n問題 {i}: {question}")
            response = agent.chat(question)
            print(f"回答: {response}")
        except Exception as e:
            print(f"錯誤: {str(e)}")


def calculation_example(agent):
    """
    計算示例

    Args:
        agent: PandasAI Agent 實例
    """
    print("\n" + "="*60)
    print("計算示例")
    print("="*60)

    questions = [
        "計算所有產品的總銷售額",
        "電腦類別的產品總銷售額是多少？",
        "平均單價是多少？",
        "銷售數量超過 300 的產品有哪些？"
    ]

    for i, question in enumerate(questions, 1):
        try:
            print(f"\n問題 {i}: {question}")
            response = agent.chat(question)
            print(f"回答: {response}")
        except Exception as e:
            print(f"錯誤: {str(e)}")


def comparison_example(agent):
    """
    比較分析示例

    Args:
        agent: PandasAI Agent 實例
    """
    print("\n" + "="*60)
    print("比較分析示例")
    print("="*60)

    questions = [
        "比較電腦和配件類別的平均評分",
        "哪個類別的總銷售額更高？",
        "評分最高和最低的產品分別是什麼？"
    ]

    for i, question in enumerate(questions, 1):
        try:
            print(f"\n問題 {i}: {question}")
            response = agent.chat(question)
            print(f"回答: {response}")
        except Exception as e:
            print(f"錯誤: {str(e)}")


def main():
    """
    主函數：演示 PandasAI 的基本使用
    """
    print("PandasAI 快速開始示例")
    print("="*60)

    # 檢查 API 密鑰
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("警告: 未找到 OPENAI_API_KEY 環境變量")
        print("請在 .env 文件中設置: OPENAI_API_KEY=your_api_key")
        print("\n使用示例數據集演示（不進行實際 API 調用）...")

        # 創建示例數據集並顯示
        df = create_sample_dataframe()
        print("\n示例數據集:")
        print(df)
        print(f"\n數據集形狀: {df.shape}")
        print(f"列名: {df.columns.tolist()}")

        return

    try:
        # 導入 PandasAI
        from pandasai import Agent

        # 創建示例數據集
        print("\n步驟 1: 創建示例數據集")
        df = create_sample_dataframe()
        print(df)

        # 初始化 Agent
        print("\n步驟 2: 初始化 PandasAI Agent")
        agent = Agent(df, config={
            "llm": {
                "api_key": api_key,
                "model": "gpt-3.5-turbo"
            },
            "verbose": False,
            "enable_cache": True
        })
        print("Agent 初始化成功！")

        # 運行示例
        print("\n步驟 3: 執行自然語言查詢")

        # 1. 基本對話示例
        basic_chat_example(agent)

        # 2. 計算示例
        calculation_example(agent)

        # 3. 比較分析示例
        comparison_example(agent)

        # 總結
        print("\n" + "="*60)
        print("總結")
        print("="*60)
        print("✓ 成功使用 PandasAI 進行自然語言數據查詢")
        print("✓ 展示了基本查詢、計算和比較分析功能")
        print("✓ PandasAI 可以理解中文問題並提供準確答案")

    except ImportError:
        print("\n錯誤: 未安裝 pandasai 庫")
        print("請運行: pip install pandasai")
    except Exception as e:
        print(f"\n發生錯誤: {str(e)}")
        print(f"錯誤類型: {type(e).__name__}")

        # 提供故障排除建議
        print("\n故障排除建議:")
        print("1. 確保已安裝所有依賴: pip install -r requirements.txt")
        print("2. 檢查 API 密鑰是否正確設置")
        print("3. 確保網絡連接正常")
        print("4. 檢查 API 配額是否充足")


if __name__ == "__main__":
    main()

"""
PandasAI 數據分析示例

這個示例展示了如何使用 PandasAI 進行自動數據分析：
1. 探索性數據分析（EDA）
2. 異常值檢測
3. 相關性分析
4. 趨勢分析
5. 數據洞察生成

作者：PandasAI 示例
日期：2025-12-31
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 載入環境變量
load_dotenv()


def create_analysis_dataframe():
    """
    創建用於分析的數據集

    Returns:
        pd.DataFrame: 包含客戶行為數據的 DataFrame
    """
    np.random.seed(42)

    # 生成日期範圍
    start_date = datetime(2024, 1, 1)
    n_records = 500

    # 生成客戶數據
    customer_ids = [f"C{str(i).zfill(4)}" for i in range(1, 101)]

    data = {
        "客戶ID": np.random.choice(customer_ids, n_records),
        "年齡": np.random.randint(18, 70, n_records),
        "購買次數": np.random.randint(1, 50, n_records),
        "總消費金額": np.random.randint(1000, 100000, n_records),
        "平均訂單金額": 0,  # 將在後面計算
        "會員等級": np.random.choice(["銅牌", "銀牌", "金牌", "白金"], n_records),
        "註冊天數": np.random.randint(30, 1000, n_records),
        "最後購買天數": np.random.randint(1, 90, n_records),
        "退貨率": np.random.uniform(0, 0.3, n_records),
        "客戶滿意度": np.random.randint(1, 6, n_records),
        "推薦意願": np.random.randint(0, 11, n_records)  # NPS 分數 0-10
    }

    df = pd.DataFrame(data)

    # 計算派生欄位
    df["平均訂單金額"] = (df["總消費金額"] / df["購買次數"]).round(2)
    df["客戶價值"] = df["總消費金額"] * (1 - df["退貨率"])
    df["活躍度"] = (df["購買次數"] / df["註冊天數"] * 30).round(2)  # 每月購買次數
    df["流失風險"] = df["最後購買天數"] > 60

    # 添加一些異常值
    df.loc[np.random.choice(df.index, 5), "總消費金額"] *= 10
    df.loc[np.random.choice(df.index, 3), "退貨率"] = 0.8

    return df


def exploratory_analysis(agent):
    """
    探索性數據分析示例

    Args:
        agent: PandasAI Agent 實例
    """
    print("\n" + "="*60)
    print("探索性數據分析（EDA）")
    print("="*60)

    queries = [
        "描述這個數據集的基本特徵",
        "數據集中有多少個唯一客戶？",
        "總消費金額的分佈是怎樣的？",
        "不同會員等級的客戶數量分佈",
        "找出數據中的缺失值"
    ]

    for i, query in enumerate(queries, 1):
        try:
            print(f"\n分析 {i}: {query}")
            response = agent.chat(query)
            print(f"結果: {response}")
        except Exception as e:
            print(f"錯誤: {str(e)}")


def outlier_detection(agent):
    """
    異常值檢測示例

    Args:
        agent: PandasAI Agent 實例
    """
    print("\n" + "="*60)
    print("異常值檢測")
    print("="*60)

    queries = [
        "找出總消費金額的異常值",
        "哪些客戶的退貨率異常高？",
        "識別購買次數的離群值",
        "找出客戶滿意度異常低的記錄",
        "檢測平均訂單金額的異常模式"
    ]

    for i, query in enumerate(queries, 1):
        try:
            print(f"\n檢測 {i}: {query}")
            response = agent.chat(query)
            print(f"結果: {response}")
        except Exception as e:
            print(f"錯誤: {str(e)}")


def correlation_analysis(agent):
    """
    相關性分析示例

    Args:
        agent: PandasAI Agent 實例
    """
    print("\n" + "="*60)
    print("相關性分析")
    print("="*60)

    queries = [
        "分析購買次數和總消費金額的相關性",
        "年齡與客戶滿意度有關聯嗎？",
        "退貨率和推薦意願之間的關係",
        "活躍度如何影響客戶價值？",
        "找出與客戶流失風險最相關的因素"
    ]

    for i, query in enumerate(queries, 1):
        try:
            print(f"\n分析 {i}: {query}")
            response = agent.chat(query)
            print(f"結果: {response}")
        except Exception as e:
            print(f"錯誤: {str(e)}")


def segmentation_analysis(agent):
    """
    客戶分群分析示例

    Args:
        agent: PandasAI Agent 實例
    """
    print("\n" + "="*60)
    print("客戶分群分析")
    print("="*60)

    queries = [
        "比較不同會員等級的平均消費金額",
        "分析各年齡段的購買行為差異",
        "高價值客戶的特徵是什麼？",
        "識別最有可能流失的客戶群體",
        "比較活躍客戶和非活躍客戶的差異"
    ]

    for i, query in enumerate(queries, 1):
        try:
            print(f"\n分析 {i}: {query}")
            response = agent.chat(query)
            print(f"結果: {response}")
        except Exception as e:
            print(f"錯誤: {str(e)}")


def trend_analysis(agent):
    """
    趨勢分析示例

    Args:
        agent: PandasAI Agent 實例
    """
    print("\n" + "="*60)
    print("趨勢分析")
    print("="*60)

    queries = [
        "隨著註冊天數增加，客戶行為如何變化？",
        "年齡和購買次數之間有什麼趨勢？",
        "客戶滿意度和推薦意願的趨勢關係",
        "退貨率如何影響客戶的後續購買？",
        "活躍度的變化趨勢分析"
    ]

    for i, query in enumerate(queries, 1):
        try:
            print(f"\n分析 {i}: {query}")
            response = agent.chat(query)
            print(f"結果: {response}")
        except Exception as e:
            print(f"錯誤: {str(e)}")


def insight_generation(agent):
    """
    數據洞察生成示例

    Args:
        agent: PandasAI Agent 實例
    """
    print("\n" + "="*60)
    print("數據洞察生成")
    print("="*60)

    queries = [
        "提供這個數據集的主要洞察",
        "識別提升客戶價值的關鍵因素",
        "給出降低客戶流失的建議",
        "分析並建議如何提高客戶滿意度",
        "總結最有價值的客戶特徵"
    ]

    for i, query in enumerate(queries, 1):
        try:
            print(f"\n洞察 {i}: {query}")
            response = agent.chat(query)
            print(f"結果: {response}")
        except Exception as e:
            print(f"錯誤: {str(e)}")


def predictive_questions(agent):
    """
    預測性問題示例

    Args:
        agent: PandasAI Agent 實例
    """
    print("\n" + "="*60)
    print("預測性問題")
    print("="*60)

    queries = [
        "基於當前數據，哪些客戶最可能流失？",
        "預測高價值客戶的特徵模式",
        "什麼因素最能預測客戶滿意度？",
        "如何識別潛在的白金會員候選人？",
        "預測哪些客戶會成為推薦者（NPS >= 9）"
    ]

    for i, query in enumerate(queries, 1):
        try:
            print(f"\n預測 {i}: {query}")
            response = agent.chat(query)
            print(f"結果: {response}")
        except Exception as e:
            print(f"錯誤: {str(e)}")


def main():
    """
    主函數：演示自動數據分析功能
    """
    print("PandasAI 數據分析示例")
    print("="*60)

    # 檢查 API 密鑰
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("警告: 未找到 OPENAI_API_KEY 環境變量")
        print("請在 .env 文件中設置: OPENAI_API_KEY=your_api_key")
        print("\n使用示例數據集演示（不進行實際 API 調用）...")

        # 創建示例數據集並顯示統計信息
        df = create_analysis_dataframe()
        print("\n示例數據集（前 10 行）:")
        print(df.head(10))
        print(f"\n數據集形狀: {df.shape}")
        print(f"\n數據統計:")
        print(df.describe())
        print(f"\n數據類型:")
        print(df.dtypes)

        return

    try:
        # 導入 PandasAI
        from pandasai import Agent

        # 創建示例數據集
        print("\n步驟 1: 創建分析數據集")
        df = create_analysis_dataframe()
        print(f"數據集大小: {df.shape}")
        print("\n數據集預覽（前 5 行）:")
        print(df.head())

        # 初始化 Agent
        print("\n步驟 2: 初始化 PandasAI Agent")
        agent = Agent(df, config={
            "llm": {
                "api_key": api_key,
                "model": "gpt-4"  # 使用 GPT-4 以獲得更好的分析能力
            },
            "verbose": False,
            "enable_cache": True,
            "max_retries": 3
        })
        print("Agent 初始化成功！")

        # 運行各種分析示例
        print("\n步驟 3: 執行自動數據分析")

        # 1. 探索性數據分析
        exploratory_analysis(agent)

        # 2. 異常值檢測
        outlier_detection(agent)

        # 3. 相關性分析
        correlation_analysis(agent)

        # 4. 客戶分群分析
        segmentation_analysis(agent)

        # 5. 趨勢分析
        trend_analysis(agent)

        # 6. 數據洞察生成
        insight_generation(agent)

        # 7. 預測性問題
        predictive_questions(agent)

        # 總結
        print("\n" + "="*60)
        print("數據分析功能總結")
        print("="*60)
        print("✓ 探索性分析：自動識別數據特徵和分佈")
        print("✓ 異常值檢測：發現數據中的離群值")
        print("✓ 相關性分析：識別變量之間的關係")
        print("✓ 分群分析：比較不同群體的特徵")
        print("✓ 趨勢分析：發現數據中的模式和趨勢")
        print("✓ 洞察生成：提供可操作的業務建議")
        print("✓ 預測性問題：基於數據進行預測")

        print("\n最佳實踐：")
        print("- 先進行探索性分析了解數據")
        print("- 檢查並處理異常值")
        print("- 使用具體的問題獲得精確的洞察")
        print("- 結合領域知識解釋分析結果")
        print("- 驗證 AI 生成的分析結論")

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
        print("3. 使用 GPT-4 模型以獲得更好的分析能力")
        print("4. 確保數據質量良好")
        print("5. 簡化分析問題，逐步深入")


if __name__ == "__main__":
    main()

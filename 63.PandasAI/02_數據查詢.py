"""
PandasAI 數據查詢示例

這個示例展示了如何使用 PandasAI 進行各種類型的自然語言數據查詢：
1. 過濾查詢
2. 聚合查詢
3. 排序查詢
4. 複雜條件查詢
5. 統計查詢

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


def create_sales_dataframe():
    """
    創建更複雜的銷售數據集

    Returns:
        pd.DataFrame: 包含詳細銷售數據的 DataFrame
    """
    # 設置隨機種子以保證可重現性
    np.random.seed(42)

    # 生成日期範圍
    start_date = datetime(2024, 1, 1)
    dates = [start_date + timedelta(days=x) for x in range(365)]

    # 產品列表
    products = ["筆記本電腦", "智能手機", "平板電腦", "智能手錶", "耳機", "鍵盤", "滑鼠", "顯示器"]
    categories = ["電腦", "手機", "電腦", "配件", "配件", "配件", "配件", "電腦"]
    regions = ["北部", "中部", "南部", "東部"]

    # 生成數據
    n_records = 1000
    data = {
        "訂單編號": [f"ORD{str(i).zfill(5)}" for i in range(1, n_records + 1)],
        "日期": np.random.choice(dates, n_records),
        "產品名稱": np.random.choice(products, n_records),
        "類別": [categories[products.index(p)] for p in np.random.choice(products, n_records)],
        "地區": np.random.choice(regions, n_records),
        "銷售數量": np.random.randint(1, 20, n_records),
        "單價": np.random.randint(500, 50000, n_records),
        "折扣": np.random.choice([0, 0.05, 0.1, 0.15, 0.2], n_records),
        "客戶滿意度": np.random.choice([1, 2, 3, 4, 5], n_records)
    }

    df = pd.DataFrame(data)

    # 計算派生欄位
    df["原始金額"] = df["銷售數量"] * df["單價"]
    df["折扣金額"] = df["原始金額"] * df["折扣"]
    df["實際金額"] = df["原始金額"] - df["折扣金額"]

    # 添加月份和季度
    df["月份"] = df["日期"].dt.month
    df["季度"] = df["日期"].dt.quarter
    df["星期幾"] = df["日期"].dt.day_name()

    return df


def filtering_queries(agent):
    """
    過濾查詢示例

    Args:
        agent: PandasAI Agent 實例
    """
    print("\n" + "="*60)
    print("過濾查詢示例")
    print("="*60)

    queries = [
        "顯示所有北部地區的訂單",
        "找出銷售數量大於 10 的訂單",
        "列出所有有折扣的訂單",
        "顯示客戶滿意度為 5 分的訂單數量",
        "找出折扣大於 10% 的訂單"
    ]

    for i, query in enumerate(queries, 1):
        try:
            print(f"\n查詢 {i}: {query}")
            response = agent.chat(query)
            print(f"結果: {response}")
        except Exception as e:
            print(f"錯誤: {str(e)}")


def aggregation_queries(agent):
    """
    聚合查詢示例

    Args:
        agent: PandasAI Agent 實例
    """
    print("\n" + "="*60)
    print("聚合查詢示例")
    print("="*60)

    queries = [
        "計算每個地區的總銷售額",
        "統計每個類別的訂單數量",
        "計算平均訂單金額",
        "找出每個產品的總銷售數量",
        "計算每個月的平均客戶滿意度"
    ]

    for i, query in enumerate(queries, 1):
        try:
            print(f"\n查詢 {i}: {query}")
            response = agent.chat(query)
            print(f"結果: {response}")
        except Exception as e:
            print(f"錯誤: {str(e)}")


def sorting_queries(agent):
    """
    排序查詢示例

    Args:
        agent: PandasAI Agent 實例
    """
    print("\n" + "="*60)
    print("排序查詢示例")
    print("="*60)

    queries = [
        "列出銷售額最高的前 5 個訂單",
        "找出客戶滿意度最低的 10 個訂單",
        "按銷售數量降序排列，顯示前 5 筆",
        "找出折扣最高的 3 個訂單",
        "列出實際金額最低的 5 個訂單"
    ]

    for i, query in enumerate(queries, 1):
        try:
            print(f"\n查詢 {i}: {query}")
            response = agent.chat(query)
            print(f"結果: {response}")
        except Exception as e:
            print(f"錯誤: {str(e)}")


def complex_queries(agent):
    """
    複雜條件查詢示例

    Args:
        agent: PandasAI Agent 實例
    """
    print("\n" + "="*60)
    print("複雜條件查詢示例")
    print("="*60)

    queries = [
        "找出北部地區且銷售額超過 10000 的訂單數量",
        "統計電腦類別中客戶滿意度為 5 分的訂單",
        "計算有折扣且銷售數量大於 5 的訂單總金額",
        "找出第一季度中南部地區的平均訂單金額",
        "列出沒有折扣但銷售額超過 20000 的訂單"
    ]

    for i, query in enumerate(queries, 1):
        try:
            print(f"\n查詢 {i}: {query}")
            response = agent.chat(query)
            print(f"結果: {response}")
        except Exception as e:
            print(f"錯誤: {str(e)}")


def statistical_queries(agent):
    """
    統計查詢示例

    Args:
        agent: PandasAI Agent 實例
    """
    print("\n" + "="*60)
    print("統計查詢示例")
    print("="*60)

    queries = [
        "計算銷售額的標準差",
        "找出客戶滿意度的中位數",
        "計算每個地區的銷售額變異數",
        "統計折扣的分位數（25%, 50%, 75%）",
        "計算銷售數量的最大值、最小值和平均值"
    ]

    for i, query in enumerate(queries, 1):
        try:
            print(f"\n查詢 {i}: {query}")
            response = agent.chat(query)
            print(f"結果: {response}")
        except Exception as e:
            print(f"錯誤: {str(e)}")


def time_based_queries(agent):
    """
    時間相關查詢示例

    Args:
        agent: PandasAI Agent 實例
    """
    print("\n" + "="*60)
    print("時間相關查詢示例")
    print("="*60)

    queries = [
        "計算每個月的總銷售額",
        "找出銷售額最高的季度",
        "統計每個星期幾的平均訂單數量",
        "比較第一季度和第二季度的銷售表現",
        "找出銷售額最高的月份"
    ]

    for i, query in enumerate(queries, 1):
        try:
            print(f"\n查詢 {i}: {query}")
            response = agent.chat(query)
            print(f"結果: {response}")
        except Exception as e:
            print(f"錯誤: {str(e)}")


def main():
    """
    主函數：演示各種類型的數據查詢
    """
    print("PandasAI 數據查詢示例")
    print("="*60)

    # 檢查 API 密鑰
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("警告: 未找到 OPENAI_API_KEY 環境變量")
        print("請在 .env 文件中設置: OPENAI_API_KEY=your_api_key")
        print("\n使用示例數據集演示（不進行實際 API 調用）...")

        # 創建示例數據集並顯示
        df = create_sales_dataframe()
        print("\n示例數據集（前 10 行）:")
        print(df.head(10))
        print(f"\n數據集形狀: {df.shape}")
        print(f"\n數據統計:")
        print(df.describe())

        return

    try:
        # 導入 PandasAI
        from pandasai import Agent

        # 創建示例數據集
        print("\n步驟 1: 創建示例數據集")
        df = create_sales_dataframe()
        print(f"數據集大小: {df.shape}")
        print("\n數據集預覽（前 5 行）:")
        print(df.head())

        # 初始化 Agent
        print("\n步驟 2: 初始化 PandasAI Agent")
        agent = Agent(df, config={
            "llm": {
                "api_key": api_key,
                "model": "gpt-3.5-turbo"
            },
            "verbose": False,
            "enable_cache": True,
            "max_retries": 3
        })
        print("Agent 初始化成功！")

        # 運行各種查詢示例
        print("\n步驟 3: 執行各種類型的數據查詢")

        # 1. 過濾查詢
        filtering_queries(agent)

        # 2. 聚合查詢
        aggregation_queries(agent)

        # 3. 排序查詢
        sorting_queries(agent)

        # 4. 複雜條件查詢
        complex_queries(agent)

        # 5. 統計查詢
        statistical_queries(agent)

        # 6. 時間相關查詢
        time_based_queries(agent)

        # 總結
        print("\n" + "="*60)
        print("查詢功能總結")
        print("="*60)
        print("✓ 過濾查詢：根據條件篩選數據")
        print("✓ 聚合查詢：計算總和、平均值、計數等")
        print("✓ 排序查詢：按指定欄位排序數據")
        print("✓ 複雜查詢：組合多個條件進行查詢")
        print("✓ 統計查詢：計算標準差、中位數等統計量")
        print("✓ 時間查詢：基於日期進行分析")

        print("\n提示：")
        print("- 使用明確、具體的問題可以獲得更準確的結果")
        print("- 可以使用中文或英文進行查詢")
        print("- 支援複雜的多條件查詢")
        print("- 結果會根據問題自動選擇合適的格式")

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
        print("5. 嘗試簡化查詢語句")


if __name__ == "__main__":
    main()

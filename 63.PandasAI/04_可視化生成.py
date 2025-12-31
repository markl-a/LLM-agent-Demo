"""
PandasAI 可視化生成示例

這個示例展示了如何使用 PandasAI 自動生成各種類型的圖表：
1. 柱狀圖
2. 折線圖
3. 散點圖
4. 餅圖
5. 箱型圖
6. 熱力圖

作者：PandasAI 示例
日期：2025-12-31
"""

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # 使用非交互式後端
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 載入環境變量
load_dotenv()

# 設置中文字體支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def create_visualization_dataframe():
    """
    創建用於可視化的數據集

    Returns:
        pd.DataFrame: 包含銷售和市場數據的 DataFrame
    """
    np.random.seed(42)

    # 生成日期範圍
    start_date = datetime(2024, 1, 1)
    dates = pd.date_range(start=start_date, periods=365, freq='D')

    # 生成趨勢數據
    trend = np.linspace(10000, 15000, 365)
    seasonal = 2000 * np.sin(2 * np.pi * np.arange(365) / 365)
    noise = np.random.normal(0, 500, 365)
    sales = trend + seasonal + noise

    data = {
        "日期": dates,
        "銷售額": sales,
        "訪客數": np.random.randint(100, 500, 365),
        "轉換率": np.random.uniform(0.02, 0.08, 365),
        "平均訂單金額": np.random.randint(200, 800, 365)
    }

    df = pd.DataFrame(data)

    # 添加派生欄位
    df["月份"] = df["日期"].dt.month
    df["季度"] = df["日期"].dt.quarter
    df["星期"] = df["日期"].dt.dayofweek
    df["訂單數"] = (df["訪客數"] * df["轉換率"]).astype(int)

    return df


def create_product_dataframe():
    """
    創建產品數據集

    Returns:
        pd.DataFrame: 包含產品信息的 DataFrame
    """
    data = {
        "產品類別": ["電子產品", "服飾", "食品", "家居", "運動", "美妝"],
        "銷售額": [350000, 280000, 420000, 190000, 230000, 310000],
        "利潤率": [0.25, 0.45, 0.15, 0.35, 0.30, 0.50],
        "庫存週轉率": [8, 12, 15, 6, 9, 10],
        "客戶滿意度": [4.5, 4.2, 4.7, 4.0, 4.4, 4.6]
    }

    return pd.DataFrame(data)


def bar_chart_examples(agent):
    """
    柱狀圖示例

    Args:
        agent: PandasAI Agent 實例
    """
    print("\n" + "="*60)
    print("柱狀圖生成示例")
    print("="*60)

    queries = [
        "畫一個顯示每個產品類別銷售額的柱狀圖",
        "創建一個比較不同類別客戶滿意度的柱狀圖",
        "繪製各類別利潤率的柱狀圖",
        "顯示庫存週轉率的水平柱狀圖"
    ]

    for i, query in enumerate(queries, 1):
        try:
            print(f"\n圖表 {i}: {query}")
            response = agent.chat(query)
            print(f"結果: {response}")
            print("圖表已生成（如果配置了保存路徑）")
        except Exception as e:
            print(f"錯誤: {str(e)}")


def line_chart_examples(agent):
    """
    折線圖示例

    Args:
        agent: PandasAI Agent 實例
    """
    print("\n" + "="*60)
    print("折線圖生成示例")
    print("="*60)

    queries = [
        "畫一個顯示銷售額隨時間變化的折線圖",
        "創建訪客數的趨勢圖",
        "繪製轉換率的時間序列圖",
        "顯示平均訂單金額的變化趨勢"
    ]

    for i, query in enumerate(queries, 1):
        try:
            print(f"\n圖表 {i}: {query}")
            response = agent.chat(query)
            print(f"結果: {response}")
            print("圖表已生成（如果配置了保存路徑）")
        except Exception as e:
            print(f"錯誤: {str(e)}")


def scatter_plot_examples(agent):
    """
    散點圖示例

    Args:
        agent: PandasAI Agent 實例
    """
    print("\n" + "="*60)
    print("散點圖生成示例")
    print("="*60)

    queries = [
        "創建訪客數和銷售額的散點圖",
        "畫一個顯示轉換率和平均訂單金額關係的散點圖",
        "繪製訂單數和銷售額的散點圖",
        "顯示利潤率和客戶滿意度的散點圖"
    ]

    for i, query in enumerate(queries, 1):
        try:
            print(f"\n圖表 {i}: {query}")
            response = agent.chat(query)
            print(f"結果: {response}")
            print("圖表已生成（如果配置了保存路徑）")
        except Exception as e:
            print(f"錯誤: {str(e)}")


def pie_chart_examples(agent):
    """
    餅圖示例

    Args:
        agent: PandasAI Agent 實例
    """
    print("\n" + "="*60)
    print("餅圖生成示例")
    print("="*60)

    queries = [
        "創建一個顯示各產品類別銷售額佔比的餅圖",
        "畫一個展示不同類別在總銷售中比例的餅圖",
        "繪製產品類別分佈的餅圖"
    ]

    for i, query in enumerate(queries, 1):
        try:
            print(f"\n圖表 {i}: {query}")
            response = agent.chat(query)
            print(f"結果: {response}")
            print("圖表已生成（如果配置了保存路徑）")
        except Exception as e:
            print(f"錯誤: {str(e)}")


def box_plot_examples(agent):
    """
    箱型圖示例

    Args:
        agent: PandasAI Agent 實例
    """
    print("\n" + "="*60)
    print("箱型圖生成示例")
    print("="*60)

    queries = [
        "創建銷售額的箱型圖",
        "畫一個顯示訪客數分佈的箱型圖",
        "繪製轉換率的箱型圖以識別異常值",
        "顯示平均訂單金額的箱型圖"
    ]

    for i, query in enumerate(queries, 1):
        try:
            print(f"\n圖表 {i}: {query}")
            response = agent.chat(query)
            print(f"結果: {response}")
            print("圖表已生成（如果配置了保存路徑）")
        except Exception as e:
            print(f"錯誤: {str(e)}")


def aggregated_visualizations(agent):
    """
    聚合可視化示例

    Args:
        agent: PandasAI Agent 實例
    """
    print("\n" + "="*60)
    print("聚合可視化示例")
    print("="*60)

    queries = [
        "畫一個顯示每月總銷售額的柱狀圖",
        "創建每季度平均訪客數的折線圖",
        "繪製每週平均轉換率的圖表",
        "顯示每月訂單數的趨勢圖"
    ]

    for i, query in enumerate(queries, 1):
        try:
            print(f"\n圖表 {i}: {query}")
            response = agent.chat(query)
            print(f"結果: {response}")
            print("圖表已生成（如果配置了保存路徑）")
        except Exception as e:
            print(f"錯誤: {str(e)}")


def comparison_visualizations(agent):
    """
    比較可視化示例

    Args:
        agent: PandasAI Agent 實例
    """
    print("\n" + "="*60)
    print("比較可視化示例")
    print("="*60)

    queries = [
        "創建一個比較各季度銷售額的分組柱狀圖",
        "畫一個顯示不同類別多個指標的雷達圖",
        "繪製各產品類別的多指標比較圖",
        "顯示銷售額和訪客數的雙軸折線圖"
    ]

    for i, query in enumerate(queries, 1):
        try:
            print(f"\n圖表 {i}: {query}")
            response = agent.chat(query)
            print(f"結果: {response}")
            print("圖表已生成（如果配置了保存路徑）")
        except Exception as e:
            print(f"錯誤: {str(e)}")


def main():
    """
    主函數：演示自動可視化生成功能
    """
    print("PandasAI 可視化生成示例")
    print("="*60)

    # 檢查 API 密鑰
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("警告: 未找到 OPENAI_API_KEY 環境變量")
        print("請在 .env 文件中設置: OPENAI_API_KEY=your_api_key")
        print("\n使用示例數據集演示（不進行實際 API 調用）...")

        # 創建示例數據集並顯示
        sales_df = create_visualization_dataframe()
        product_df = create_product_dataframe()

        print("\n銷售數據集（前 10 行）:")
        print(sales_df.head(10))

        print("\n產品數據集:")
        print(product_df)

        # 使用 matplotlib 創建示例圖表
        print("\n創建示例圖表...")
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))

        # 銷售額趨勢
        axes[0, 0].plot(sales_df["日期"][:30], sales_df["銷售額"][:30])
        axes[0, 0].set_title("銷售額趨勢（前30天）")
        axes[0, 0].tick_params(axis='x', rotation=45)

        # 產品類別銷售額
        axes[0, 1].bar(product_df["產品類別"], product_df["銷售額"])
        axes[0, 1].set_title("產品類別銷售額")
        axes[0, 1].tick_params(axis='x', rotation=45)

        # 訪客數和銷售額散點圖
        axes[1, 0].scatter(sales_df["訪客數"], sales_df["銷售額"], alpha=0.5)
        axes[1, 0].set_title("訪客數 vs 銷售額")
        axes[1, 0].set_xlabel("訪客數")
        axes[1, 0].set_ylabel("銷售額")

        # 產品類別佔比餅圖
        axes[1, 1].pie(product_df["銷售額"], labels=product_df["產品類別"], autopct='%1.1f%%')
        axes[1, 1].set_title("產品類別銷售佔比")

        plt.tight_layout()
        output_path = "/tmp/pandasai_demo_charts.png"
        plt.savefig(output_path)
        print(f"\n示例圖表已保存至: {output_path}")

        return

    try:
        # 導入 PandasAI
        from pandasai import Agent

        # 創建示例數據集
        print("\n步驟 1: 創建可視化數據集")
        sales_df = create_visualization_dataframe()
        print(f"銷售數據集大小: {sales_df.shape}")

        # 設置圖表保存路徑
        charts_dir = "/tmp/pandasai_charts"
        os.makedirs(charts_dir, exist_ok=True)

        # 初始化 Agent（使用銷售數據）
        print("\n步驟 2: 初始化 PandasAI Agent（銷售數據）")
        sales_agent = Agent(sales_df, config={
            "llm": {
                "api_key": api_key,
                "model": "gpt-4"
            },
            "verbose": False,
            "enable_cache": True,
            "save_charts": True,
            "save_charts_path": charts_dir
        })
        print("Sales Agent 初始化成功！")

        # 創建產品數據集和 Agent
        print("\n步驟 3: 初始化 PandasAI Agent（產品數據）")
        product_df = create_product_dataframe()
        product_agent = Agent(product_df, config={
            "llm": {
                "api_key": api_key,
                "model": "gpt-4"
            },
            "verbose": False,
            "enable_cache": True,
            "save_charts": True,
            "save_charts_path": charts_dir
        })
        print("Product Agent 初始化成功！")

        # 運行可視化示例
        print("\n步驟 4: 生成各種類型的圖表")
        print(f"圖表將保存在: {charts_dir}")

        # 1. 柱狀圖示例（使用產品數據）
        print("\n使用產品數據...")
        bar_chart_examples(product_agent)

        # 2. 折線圖示例（使用銷售數據）
        print("\n使用銷售數據...")
        line_chart_examples(sales_agent)

        # 3. 散點圖示例（使用銷售數據）
        scatter_plot_examples(sales_agent)

        # 4. 餅圖示例（使用產品數據）
        print("\n使用產品數據...")
        pie_chart_examples(product_agent)

        # 5. 箱型圖示例（使用銷售數據）
        print("\n使用銷售數據...")
        box_plot_examples(sales_agent)

        # 6. 聚合可視化（使用銷售數據）
        aggregated_visualizations(sales_agent)

        # 7. 比較可視化（使用產品數據）
        print("\n使用產品數據...")
        comparison_visualizations(product_agent)

        # 總結
        print("\n" + "="*60)
        print("可視化功能總結")
        print("="*60)
        print(f"✓ 圖表保存路徑: {charts_dir}")
        print("✓ 柱狀圖：比較不同類別的數值")
        print("✓ 折線圖：顯示時間序列趨勢")
        print("✓ 散點圖：探索變量之間的關係")
        print("✓ 餅圖：展示組成部分的佔比")
        print("✓ 箱型圖：顯示數據分佈和異常值")
        print("✓ 聚合圖表：展示匯總後的數據")
        print("✓ 比較圖表：多維度數據比較")

        print("\n可視化最佳實踐：")
        print("- 選擇合適的圖表類型展示數據")
        print("- 使用清晰的標題和標籤")
        print("- 確保顏色搭配合理")
        print("- 避免圖表過於複雜")
        print("- 驗證 AI 生成的圖表是否準確")

    except ImportError:
        print("\n錯誤: 未安裝 pandasai 庫")
        print("請運行: pip install pandasai matplotlib")
    except Exception as e:
        print(f"\n發生錯誤: {str(e)}")
        print(f"錯誤類型: {type(e).__name__}")

        # 提供故障排除建議
        print("\n故障排除建議:")
        print("1. 確保已安裝所有依賴: pip install -r requirements.txt")
        print("2. 檢查 API 密鑰是否正確設置")
        print("3. 確保有權限寫入圖表保存路徑")
        print("4. 使用具體的圖表描述")
        print("5. 檢查數據是否適合生成指定類型的圖表")


if __name__ == "__main__":
    main()

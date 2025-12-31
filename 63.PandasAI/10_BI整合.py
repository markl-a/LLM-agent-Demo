"""
PandasAI 商業智能（BI）整合示例

這個示例展示了如何將 PandasAI 與商業智能工具整合：
1. 生成 BI 報表
2. KPI 儀表板
3. 趨勢分析
4. 導出功能
5. 自動化報告

作者：PandasAI 示例
日期：2025-12-31
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dotenv import load_dotenv
import json

# 載入環境變量
load_dotenv()


def create_bi_dataframe():
    """
    創建 BI 分析數據集

    Returns:
        pd.DataFrame: 包含完整業務數據
    """
    np.random.seed(42)

    # 生成時間序列數據
    start_date = datetime(2024, 1, 1)
    dates = pd.date_range(start=start_date, periods=365, freq='D')

    n_records = 365

    data = {
        "日期": dates,
        "銷售額": np.random.randint(50000, 200000, n_records),
        "訂單數": np.random.randint(100, 500, n_records),
        "客戶數": np.random.randint(50, 300, n_records),
        "新客戶數": np.random.randint(10, 100, n_records),
        "退貨金額": np.random.randint(1000, 20000, n_records),
        "行銷費用": np.random.randint(10000, 50000, n_records),
        "客服請求": np.random.randint(20, 150, n_records)
    }

    df = pd.DataFrame(data)

    # 計算 KPI
    df["平均訂單金額"] = (df["銷售額"] / df["訂單數"]).round(2)
    df["轉換率"] = (df["訂單數"] / df["客戶數"] * 100).round(2)
    df["退貨率"] = (df["退貨金額"] / df["銷售額"] * 100).round(2)
    df["ROI"] = ((df["銷售額"] - df["行銷費用"]) / df["行銷費用"] * 100).round(2)
    df["客戶獲取成本"] = (df["行銷費用"] / df["新客戶數"]).round(2)

    # 添加時間維度
    df["年"] = df["日期"].dt.year
    df["月"] = df["日期"].dt.month
    df["季度"] = df["日期"].dt.quarter
    df["星期"] = df["日期"].dt.dayofweek
    df["週數"] = df["日期"].dt.isocalendar().week

    return df


def kpi_dashboard_example(api_key):
    """
    KPI 儀表板示例

    Args:
        api_key: OpenAI API 密鑰
    """
    print("\n" + "="*60)
    print("KPI 儀表板生成")
    print("="*60)

    try:
        from pandasai import Agent

        df = create_bi_dataframe()

        agent = Agent(df, config={
            "llm": {
                "api_key": api_key,
                "model": "gpt-4"
            },
            "verbose": False
        })

        print("\n生成關鍵績效指標（KPI）:")

        kpi_queries = [
            "總銷售額是多少？",
            "平均每日訂單數是多少？",
            "整體轉換率是多少？",
            "平均退貨率是多少？",
            "行銷 ROI 的平均值是多少？",
            "平均客戶獲取成本是多少？"
        ]

        kpis = {}
        for query in kpi_queries:
            try:
                print(f"\n{query}")
                response = agent.chat(query)
                print(f"  → {response}")
                kpis[query] = response
            except Exception as e:
                print(f"  錯誤: {str(e)}")

        # 保存 KPI 到文件
        kpi_file = "/tmp/kpi_dashboard.json"
        with open(kpi_file, 'w', encoding='utf-8') as f:
            json.dump(kpis, f, ensure_ascii=False, indent=2)
        print(f"\nKPI 已保存到: {kpi_file}")

    except Exception as e:
        print(f"錯誤: {str(e)}")


def trend_analysis_example(api_key):
    """
    趨勢分析示例

    Args:
        api_key: OpenAI API 密鑰
    """
    print("\n" + "="*60)
    print("趨勢分析")
    print("="*60)

    try:
        from pandasai import Agent

        df = create_bi_dataframe()

        agent = Agent(df, config={
            "llm": {
                "api_key": api_key,
                "model": "gpt-4"
            },
            "verbose": False
        })

        print("\n分析業務趨勢:")

        trend_queries = [
            "銷售額的月度趨勢如何？",
            "哪個季度的表現最好？",
            "訂單數是增長還是下降？",
            "客戶獲取成本的趨勢是什麼？",
            "ROI 隨時間如何變化？"
        ]

        for i, query in enumerate(trend_queries, 1):
            try:
                print(f"\n分析 {i}: {query}")
                response = agent.chat(query)
                print(f"結果: {response}")
            except Exception as e:
                print(f"錯誤: {str(e)}")

    except Exception as e:
        print(f"錯誤: {str(e)}")


def performance_report_example(api_key):
    """
    績效報告示例

    Args:
        api_key: OpenAI API 密鑰
    """
    print("\n" + "="*60)
    print("績效報告生成")
    print("="*60)

    try:
        from pandasai import Agent

        df = create_bi_dataframe()

        agent = Agent(df, config={
            "llm": {
                "api_key": api_key,
                "model": "gpt-4"
            },
            "verbose": False,
            "custom_prompts": {
                "format": """
                請以專業的商業報告格式回答：

                【執行摘要】
                - 關鍵發現
                - 重要指標

                【詳細分析】
                - 數據洞察
                - 趨勢說明

                【建議】
                - 行動項目
                - 預期影響
                """
            }
        })

        print("\n生成月度績效報告:")

        report_queries = [
            "生成整體業務表現摘要",
            "分析銷售和行銷效率",
            "評估客戶獲取策略的效果",
            "識別需要改進的領域"
        ]

        report_content = []
        for i, query in enumerate(report_queries, 1):
            try:
                print(f"\n報告章節 {i}: {query}")
                response = agent.chat(query)
                print(f"{response}\n")
                print("-" * 60)
                report_content.append(f"## {query}\n\n{response}\n\n")
            except Exception as e:
                print(f"錯誤: {str(e)}")

        # 保存報告
        report_file = "/tmp/performance_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# 月度績效報告\n\n")
            f.write(f"生成日期: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            for content in report_content:
                f.write(content)

        print(f"\n完整報告已保存到: {report_file}")

    except Exception as e:
        print(f"錯誤: {str(e)}")


def data_export_example(api_key):
    """
    數據導出示例

    Args:
        api_key: OpenAI API 密鑰
    """
    print("\n" + "="*60)
    print("數據導出功能")
    print("="*60)

    try:
        from pandasai import Agent

        df = create_bi_dataframe()

        # 計算月度匯總
        monthly_summary = df.groupby('月').agg({
            '銷售額': 'sum',
            '訂單數': 'sum',
            '客戶數': 'sum',
            '新客戶數': 'sum',
            '退貨金額': 'sum',
            '行銷費用': 'sum'
        }).reset_index()

        monthly_summary.columns = ['月份', '總銷售額', '總訂單數', '總客戶數',
                                   '新客戶總數', '總退貨金額', '總行銷費用']

        print("\n月度匯總數據:")
        print(monthly_summary)

        # 導出為多種格式
        export_dir = "/tmp/bi_exports"
        os.makedirs(export_dir, exist_ok=True)

        # 1. CSV 導出
        csv_file = os.path.join(export_dir, "monthly_summary.csv")
        monthly_summary.to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"\n✓ CSV 已導出: {csv_file}")

        # 2. Excel 導出
        excel_file = os.path.join(export_dir, "monthly_summary.xlsx")
        monthly_summary.to_excel(excel_file, index=False, sheet_name='月度匯總')
        print(f"✓ Excel 已導出: {excel_file}")

        # 3. JSON 導出
        json_file = os.path.join(export_dir, "monthly_summary.json")
        monthly_summary.to_json(json_file, orient='records',
                               force_ascii=False, indent=2)
        print(f"✓ JSON 已導出: {json_file}")

        # 4. HTML 導出
        html_file = os.path.join(export_dir, "monthly_summary.html")
        monthly_summary.to_html(html_file, index=False)
        print(f"✓ HTML 已導出: {html_file}")

        print(f"\n所有文件已導出到: {export_dir}")

    except Exception as e:
        print(f"錯誤: {str(e)}")


def automated_insights_example(api_key):
    """
    自動化洞察示例

    Args:
        api_key: OpenAI API 密鑰
    """
    print("\n" + "="*60)
    print("自動化洞察生成")
    print("="*60)

    try:
        from pandasai import Agent

        df = create_bi_dataframe()

        agent = Agent(df, config={
            "llm": {
                "api_key": api_key,
                "model": "gpt-4"
            },
            "verbose": False
        })

        print("\n生成自動化業務洞察:")

        insight_queries = [
            "識別銷售額的異常模式",
            "找出轉換率的關鍵驅動因素",
            "分析行銷 ROI 的優化機會",
            "預測下個月的業務趨勢",
            "提供三個最重要的行動建議"
        ]

        insights = []
        for i, query in enumerate(insight_queries, 1):
            try:
                print(f"\n洞察 {i}: {query}")
                response = agent.chat(query)
                print(f"結果: {response}")
                insights.append({
                    "query": query,
                    "insight": response,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                print(f"錯誤: {str(e)}")

        # 保存洞察
        insights_file = "/tmp/automated_insights.json"
        with open(insights_file, 'w', encoding='utf-8') as f:
            json.dump(insights, f, ensure_ascii=False, indent=2)
        print(f"\n洞察已保存到: {insights_file}")

    except Exception as e:
        print(f"錯誤: {str(e)}")


def bi_integration_guide():
    """
    BI 工具整合指南
    """
    print("\n" + "="*60)
    print("BI 工具整合指南")
    print("="*60)

    guide = """
與主流 BI 工具的整合方案：

1. Tableau 整合
   - 使用 PandasAI 生成分析結果
   - 導出為 CSV/Excel 格式
   - 在 Tableau 中導入數據
   - 創建互動式儀表板

2. Power BI 整合
   - 通過 Python 腳本整合 PandasAI
   - 使用 Power BI Python 視覺化
   - 自動化數據刷新
   - 發布到 Power BI Service

3. Google Data Studio 整合
   - 導出數據到 Google Sheets
   - 使用 Google Sheets 作為數據源
   - 創建自動更新的報表

4. Metabase 整合
   - 將分析結果存入數據庫
   - 配置 Metabase 連接
   - 創建 SQL 查詢
   - 設置定時刷新

5. Grafana 整合
   - 設置時間序列數據源
   - 配置儀表板面板
   - 添加告警規則

整合最佳實踐：
□ 定義清晰的數據管道
□ 自動化數據更新
□ 實施數據質量檢查
□ 設置監控和告警
□ 優化查詢性能
□ 確保數據安全
    """

    print(guide)


def automation_example():
    """
    自動化報告示例
    """
    print("\n" + "="*60)
    print("自動化報告示例")
    print("="*60)

    automation_code = """
# 自動化日報生成腳本示例

import schedule
import time
from datetime import datetime
from pandasai import Agent

def generate_daily_report():
    '''生成每日報告'''

    # 讀取數據
    df = load_latest_data()

    # 創建 Agent
    agent = Agent(df, config={
        "llm": {"api_key": os.getenv("OPENAI_API_KEY")}
    })

    # 生成報告
    report = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "total_sales": agent.chat("今日總銷售額"),
        "order_count": agent.chat("今日訂單數"),
        "top_products": agent.chat("今日銷售前5的產品"),
        "insights": agent.chat("今日業務洞察")
    }

    # 保存報告
    save_report(report)

    # 發送郵件通知
    send_email_notification(report)

# 設置定時任務（每天早上 9 點執行）
schedule.every().day.at("09:00").do(generate_daily_report)

# 週報（每週一早上 9 點）
schedule.every().monday.at("09:00").do(generate_weekly_report)

# 月報（每月 1 號早上 9 點）
schedule.every().month.at("09:00").do(generate_monthly_report)

while True:
    schedule.run_pending()
    time.sleep(60)
    """

    print(automation_code)


def main():
    """
    主函數：演示 BI 整合功能
    """
    print("PandasAI 商業智能整合示例")
    print("="*60)

    # 檢查 API 密鑰
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("警告: 未找到 OPENAI_API_KEY 環境變量")
        print("請在 .env 文件中設置: OPENAI_API_KEY=your_api_key")
        print("\n顯示 BI 整合指南...")

        # 創建示例數據
        df = create_bi_dataframe()
        print("\n示例數據（前 10 行）:")
        print(df.head(10))

        print("\n月度匯總:")
        monthly = df.groupby('月').agg({
            '銷售額': 'sum',
            '訂單數': 'sum'
        })
        print(monthly)

        # 顯示整合指南
        bi_integration_guide()
        automation_example()

        return

    try:
        # 1. KPI 儀表板
        kpi_dashboard_example(api_key)

        # 2. 趨勢分析
        trend_analysis_example(api_key)

        # 3. 績效報告
        performance_report_example(api_key)

        # 4. 數據導出
        data_export_example(api_key)

        # 5. 自動化洞察
        automated_insights_example(api_key)

        # 6. 整合指南
        bi_integration_guide()

        # 7. 自動化示例
        automation_example()

        # 總結
        print("\n" + "="*60)
        print("BI 整合功能總結")
        print("="*60)
        print("✓ KPI 儀表板：自動生成關鍵指標")
        print("✓ 趨勢分析：識別業務趨勢和模式")
        print("✓ 績效報告：生成專業分析報告")
        print("✓ 數據導出：支持多種格式導出")
        print("✓ 自動化洞察：AI 驅動的業務建議")
        print("✓ 工具整合：與主流 BI 工具對接")

        print("\n應用場景：")
        print("- 日常業務監控")
        print("- 定期績效報告")
        print("- 管理層儀表板")
        print("- 數據驅動決策")
        print("- 自動化報表生成")

        print("\n價值主張：")
        print("1. 降低 BI 實施門檻")
        print("2. 加速洞察生成")
        print("3. 提高決策效率")
        print("4. 減少人工分析時間")
        print("5. 實現自然語言查詢")

    except ImportError:
        print("\n錯誤: 未安裝必要的庫")
        print("請運行: pip install pandasai openpyxl schedule")
    except Exception as e:
        print(f"\n發生錯誤: {str(e)}")
        print(f"錯誤類型: {type(e).__name__}")

        # 提供故障排除建議
        print("\n故障排除建議:")
        print("1. 確保所有依賴已安裝")
        print("2. 檢查數據格式是否正確")
        print("3. 驗證 API 配額充足")
        print("4. 使用 GPT-4 以獲得更好的分析質量")
        print("5. 檢查文件導出權限")


if __name__ == "__main__":
    main()

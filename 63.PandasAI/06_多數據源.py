"""
PandasAI 多數據源整合示例

這個示例展示了如何使用 PandasAI 同時處理多個數據源：
1. 多個 DataFrame 整合
2. CSV + Excel 整合
3. 數據庫 + 文件整合
4. 跨數據源查詢
5. 數據源關聯分析

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
    創建銷售數據集

    Returns:
        pd.DataFrame: 銷售數據
    """
    np.random.seed(42)

    data = {
        "訂單編號": [f"ORD{str(i).zfill(4)}" for i in range(1, 51)],
        "客戶ID": [f"C{str(np.random.randint(1, 21)).zfill(3)}" for _ in range(50)],
        "產品ID": [f"P{str(np.random.randint(1, 11)).zfill(3)}" for _ in range(50)],
        "銷售數量": np.random.randint(1, 10, 50),
        "銷售金額": np.random.randint(1000, 50000, 50),
        "銷售日期": [datetime(2024, 1, 1) + timedelta(days=np.random.randint(0, 365)) for _ in range(50)]
    }

    return pd.DataFrame(data)


def create_customers_dataframe():
    """
    創建客戶數據集

    Returns:
        pd.DataFrame: 客戶數據
    """
    data = {
        "客戶ID": [f"C{str(i).zfill(3)}" for i in range(1, 21)],
        "客戶名稱": [f"客戶{i}" for i in range(1, 21)],
        "城市": np.random.choice(["台北", "台中", "高雄", "台南", "新竹"], 20),
        "會員等級": np.random.choice(["銅牌", "銀牌", "金牌", "白金"], 20),
        "註冊日期": [datetime(2023, 1, 1) + timedelta(days=np.random.randint(0, 365)) for _ in range(20)],
        "信用額度": np.random.randint(10000, 100000, 20)
    }

    return pd.DataFrame(data)


def create_products_dataframe():
    """
    創建產品數據集

    Returns:
        pd.DataFrame: 產品數據
    """
    data = {
        "產品ID": [f"P{str(i).zfill(3)}" for i in range(1, 11)],
        "產品名稱": ["筆記本電腦", "智能手機", "平板電腦", "智能手錶", "無線耳機",
                  "鍵盤", "滑鼠", "顯示器", "攝像頭", "音箱"],
        "類別": ["電腦", "手機", "電腦", "配件", "配件",
               "配件", "配件", "電腦", "配件", "配件"],
        "單價": [35000, 12000, 15000, 8000, 2500, 1500, 800, 8000, 1200, 3000],
        "成本": [25000, 8000, 10000, 5000, 1500, 1000, 500, 5500, 800, 2000],
        "庫存": [50, 100, 75, 120, 200, 150, 180, 60, 90, 110]
    }

    df = pd.DataFrame(data)
    df["利潤率"] = ((df["單價"] - df["成本"]) / df["單價"] * 100).round(2)

    return df


def create_inventory_dataframe():
    """
    創建庫存數據集

    Returns:
        pd.DataFrame: 庫存數據
    """
    data = {
        "產品ID": [f"P{str(i).zfill(3)}" for i in range(1, 11)],
        "倉庫位置": np.random.choice(["北部倉庫", "中部倉庫", "南部倉庫"], 10),
        "庫存數量": np.random.randint(10, 200, 10),
        "安全庫存": np.random.randint(20, 50, 10),
        "最後補貨日期": [datetime(2024, 1, 1) + timedelta(days=np.random.randint(0, 180)) for _ in range(10)]
    }

    return pd.DataFrame(data)


def save_sample_files():
    """
    保存示例文件（CSV 和 Excel）

    Returns:
        tuple: (CSV 文件路徑列表, Excel 文件路徑)
    """
    # 創建臨時目錄
    temp_dir = "/tmp/pandasai_data"
    os.makedirs(temp_dir, exist_ok=True)

    # 保存 CSV 文件
    sales_df = create_sales_dataframe()
    customers_df = create_customers_dataframe()

    sales_path = os.path.join(temp_dir, "sales.csv")
    customers_path = os.path.join(temp_dir, "customers.csv")

    sales_df.to_csv(sales_path, index=False, encoding='utf-8-sig')
    customers_df.to_csv(customers_path, index=False, encoding='utf-8-sig')

    # 保存 Excel 文件（多個工作表）
    excel_path = os.path.join(temp_dir, "products_inventory.xlsx")
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        create_products_dataframe().to_excel(writer, sheet_name='產品', index=False)
        create_inventory_dataframe().to_excel(writer, sheet_name='庫存', index=False)

    print(f"示例文件已保存到: {temp_dir}")
    print(f"- {sales_path}")
    print(f"- {customers_path}")
    print(f"- {excel_path}")

    return [sales_path, customers_path], excel_path


def multiple_dataframes_example(api_key):
    """
    多個 DataFrame 整合示例

    Args:
        api_key: OpenAI API 密鑰
    """
    print("\n" + "="*60)
    print("多個 DataFrame 整合示例")
    print("="*60)

    try:
        from pandasai import Agent

        # 創建多個數據集
        sales_df = create_sales_dataframe()
        customers_df = create_customers_dataframe()
        products_df = create_products_dataframe()

        print("\n數據集 1 - 銷售數據:")
        print(sales_df.head())

        print("\n數據集 2 - 客戶數據:")
        print(customers_df.head())

        print("\n數據集 3 - 產品數據:")
        print(products_df.head())

        # 創建 Agent（傳入多個 DataFrame）
        agent = Agent(
            [sales_df, customers_df, products_df],
            config={
                "llm": {
                    "api_key": api_key,
                    "model": "gpt-3.5-turbo"
                },
                "verbose": False,
                "enable_cache": True
            }
        )

        print("\n使用自然語言查詢多個數據源：")

        queries = [
            "總共有多少個客戶？",
            "哪個城市的客戶最多？",
            "有多少個產品類別？",
            "白金會員客戶有多少個？",
            "電腦類別的產品有哪些？",
            "統計每個會員等級的客戶數量",
            "哪個產品的利潤率最高？"
        ]

        for i, query in enumerate(queries, 1):
            try:
                print(f"\n查詢 {i}: {query}")
                response = agent.chat(query)
                print(f"回答: {response}")
            except Exception as e:
                print(f"錯誤: {str(e)}")

    except ImportError:
        print("錯誤: 未安裝 pandasai 庫")
    except Exception as e:
        print(f"錯誤: {str(e)}")


def cross_source_queries(api_key):
    """
    跨數據源查詢示例

    Args:
        api_key: OpenAI API 密鑰
    """
    print("\n" + "="*60)
    print("跨數據源查詢示例")
    print("="*60)

    try:
        from pandasai import Agent

        # 創建數據集
        sales_df = create_sales_dataframe()
        customers_df = create_customers_dataframe()
        products_df = create_products_dataframe()

        # 創建 Agent
        agent = Agent(
            [sales_df, customers_df, products_df],
            config={
                "llm": {
                    "api_key": api_key,
                    "model": "gpt-4"  # 使用 GPT-4 處理複雜查詢
                },
                "verbose": False
            }
        )

        print("\n執行跨數據源關聯查詢：")

        queries = [
            "台北的客戶總共購買了多少金額？",
            "金牌會員購買最多的產品是什麼？",
            "計算每個城市的平均訂單金額",
            "哪個類別的產品銷售額最高？",
            "白金會員主要購買哪些類別的產品？",
            "利潤率最高的產品銷售情況如何？"
        ]

        for i, query in enumerate(queries, 1):
            try:
                print(f"\n查詢 {i}: {query}")
                response = agent.chat(query)
                print(f"回答: {response}")
            except Exception as e:
                print(f"錯誤: {str(e)}")

    except Exception as e:
        print(f"錯誤: {str(e)}")


def file_integration_example(api_key):
    """
    CSV + Excel 文件整合示例

    Args:
        api_key: OpenAI API 密鑰
    """
    print("\n" + "="*60)
    print("CSV + Excel 文件整合示例")
    print("="*60)

    try:
        from pandasai import Agent

        # 保存示例文件
        csv_paths, excel_path = save_sample_files()

        # 讀取 CSV 文件
        sales_df = pd.read_csv(csv_paths[0])
        customers_df = pd.read_csv(csv_paths[1])

        # 讀取 Excel 文件
        products_df = pd.read_excel(excel_path, sheet_name='產品')
        inventory_df = pd.read_excel(excel_path, sheet_name='庫存')

        print("\n已讀取的數據集:")
        print(f"1. 銷售數據: {sales_df.shape}")
        print(f"2. 客戶數據: {customers_df.shape}")
        print(f"3. 產品數據: {products_df.shape}")
        print(f"4. 庫存數據: {inventory_df.shape}")

        # 創建 Agent
        agent = Agent(
            [sales_df, customers_df, products_df, inventory_df],
            config={
                "llm": {
                    "api_key": api_key,
                    "model": "gpt-4"
                },
                "verbose": False
            }
        )

        print("\n查詢整合後的數據：")

        queries = [
            "哪些產品的庫存低於安全庫存？",
            "北部倉庫存放了哪些產品？",
            "統計每個倉庫的總庫存價值",
            "哪些產品需要補貨？",
            "計算所有倉庫的總庫存數量"
        ]

        for i, query in enumerate(queries, 1):
            try:
                print(f"\n查詢 {i}: {query}")
                response = agent.chat(query)
                print(f"回答: {response}")
            except Exception as e:
                print(f"錯誤: {str(e)}")

    except Exception as e:
        print(f"錯誤: {str(e)}")


def data_relationship_analysis(api_key):
    """
    數據源關聯分析示例

    Args:
        api_key: OpenAI API 密鑰
    """
    print("\n" + "="*60)
    print("數據源關聯分析示例")
    print("="*60)

    try:
        from pandasai import Agent

        # 創建數據集
        sales_df = create_sales_dataframe()
        customers_df = create_customers_dataframe()
        products_df = create_products_dataframe()

        # 創建 Agent
        agent = Agent(
            [sales_df, customers_df, products_df],
            config={
                "llm": {
                    "api_key": api_key,
                    "model": "gpt-4"
                },
                "verbose": False
            }
        )

        print("\n執行數據關聯分析：")

        queries = [
            "分析不同會員等級的購買行為差異",
            "哪個城市對高利潤產品的需求最大？",
            "識別最有價值的客戶群體",
            "分析產品類別和客戶城市的關聯性",
            "提供提升銷售額的建議"
        ]

        for i, query in enumerate(queries, 1):
            try:
                print(f"\n分析 {i}: {query}")
                response = agent.chat(query)
                print(f"結果: {response}")
            except Exception as e:
                print(f"錯誤: {str(e)}")

    except Exception as e:
        print(f"錯誤: {str(e)}")


def main():
    """
    主函數：演示多數據源整合功能
    """
    print("PandasAI 多數據源整合示例")
    print("="*60)

    # 檢查 API 密鑰
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("警告: 未找到 OPENAI_API_KEY 環境變量")
        print("請在 .env 文件中設置: OPENAI_API_KEY=your_api_key")
        print("\n顯示示例數據集...")

        # 創建並顯示示例數據
        print("\n銷售數據:")
        print(create_sales_dataframe().head(10))

        print("\n客戶數據:")
        print(create_customers_dataframe().head(10))

        print("\n產品數據:")
        print(create_products_dataframe())

        print("\n庫存數據:")
        print(create_inventory_dataframe())

        # 保存示例文件
        print("\n保存示例文件...")
        save_sample_files()

        return

    try:
        # 1. 多個 DataFrame 整合示例
        multiple_dataframes_example(api_key)

        # 2. 跨數據源查詢示例
        cross_source_queries(api_key)

        # 3. CSV + Excel 文件整合示例
        file_integration_example(api_key)

        # 4. 數據源關聯分析示例
        data_relationship_analysis(api_key)

        # 總結
        print("\n" + "="*60)
        print("多數據源整合功能總結")
        print("="*60)
        print("✓ 多 DataFrame：同時處理多個數據集")
        print("✓ 跨源查詢：在多個數據源間進行關聯查詢")
        print("✓ 文件整合：整合 CSV、Excel 等不同格式")
        print("✓ 關聯分析：發現數據源之間的關係")
        print("✓ 智能推理：AI 自動識別數據關聯")

        print("\n最佳實踐：")
        print("- 確保數據源有共同的關聯鍵（如 ID）")
        print("- 為每個數據集提供清晰的列名")
        print("- 預處理數據以提高查詢準確性")
        print("- 使用 GPT-4 處理複雜的跨源查詢")
        print("- 驗證關聯查詢的結果")
        print("- 考慮數據量對性能的影響")

    except ImportError:
        print("\n錯誤: 未安裝必要的庫")
        print("請運行: pip install pandasai openpyxl")
    except Exception as e:
        print(f"\n發生錯誤: {str(e)}")
        print(f"錯誤類型: {type(e).__name__}")

        # 提供故障排除建議
        print("\n故障排除建議:")
        print("1. 確保所有數據集有正確的結構")
        print("2. 檢查數據集之間的關聯鍵")
        print("3. 使用更強大的模型（如 GPT-4）")
        print("4. 簡化查詢，逐步增加複雜度")
        print("5. 檢查數據類型匹配")


if __name__ == "__main__":
    main()

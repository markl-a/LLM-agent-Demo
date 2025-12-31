"""
PandasAI SQL 連接示例

這個示例展示了如何使用 PandasAI 連接和查詢 SQL 數據庫：
1. SQLite 連接
2. PostgreSQL 連接
3. MySQL 連接
4. 自然語言 SQL 查詢
5. 多表關聯查詢

作者：PandasAI 示例
日期：2025-12-31
"""

import os
import sqlite3
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# 載入環境變量
load_dotenv()


def create_sample_sqlite_db(db_path="/tmp/sample_store.db"):
    """
    創建示例 SQLite 數據庫

    Args:
        db_path: 數據庫文件路徑

    Returns:
        str: 數據庫文件路徑
    """
    # 刪除舊數據庫
    if os.path.exists(db_path):
        os.remove(db_path)

    # 創建連接
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 創建產品表
    cursor.execute("""
        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    """)

    # 創建客戶表
    cursor.execute("""
        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY,
            customer_name TEXT NOT NULL,
            email TEXT NOT NULL,
            city TEXT NOT NULL,
            join_date DATE NOT NULL
        )
    """)

    # 創建訂單表
    cursor.execute("""
        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            order_date DATE NOT NULL,
            total_amount REAL NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    """)

    # 插入示例數據
    products_data = [
        (1, "筆記本電腦", "電腦", 35000, 50),
        (2, "智能手機", "手機", 12000, 100),
        (3, "平板電腦", "電腦", 15000, 75),
        (4, "智能手錶", "配件", 8000, 120),
        (5, "無線耳機", "配件", 2500, 200),
        (6, "鍵盤", "配件", 1500, 150),
        (7, "滑鼠", "配件", 800, 180),
        (8, "顯示器", "電腦", 8000, 60)
    ]
    cursor.executemany("INSERT INTO products VALUES (?, ?, ?, ?, ?)", products_data)

    customers_data = [
        (1, "張三", "zhang@email.com", "台北", "2023-01-15"),
        (2, "李四", "li@email.com", "台中", "2023-02-20"),
        (3, "王五", "wang@email.com", "高雄", "2023-03-10"),
        (4, "趙六", "zhao@email.com", "台北", "2023-04-05"),
        (5, "陳七", "chen@email.com", "台南", "2023-05-12")
    ]
    cursor.executemany("INSERT INTO customers VALUES (?, ?, ?, ?, ?)", customers_data)

    orders_data = [
        (1, 1, 1, 1, "2024-01-10", 35000),
        (2, 2, 2, 2, "2024-01-15", 24000),
        (3, 1, 5, 3, "2024-01-20", 7500),
        (4, 3, 3, 1, "2024-02-05", 15000),
        (5, 4, 4, 2, "2024-02-10", 16000),
        (6, 2, 6, 1, "2024-02-15", 1500),
        (7, 5, 2, 1, "2024-03-01", 12000),
        (8, 3, 7, 2, "2024-03-05", 1600),
        (9, 1, 8, 1, "2024-03-10", 8000),
        (10, 4, 5, 4, "2024-03-15", 10000)
    ]
    cursor.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?)", orders_data)

    conn.commit()
    conn.close()

    print(f"示例 SQLite 數據庫已創建: {db_path}")
    return db_path


def sqlite_connection_example(api_key):
    """
    SQLite 連接示例

    Args:
        api_key: OpenAI API 密鑰
    """
    print("\n" + "="*60)
    print("SQLite 數據庫連接示例")
    print("="*60)

    try:
        from pandasai import Agent
        from pandasai.connectors import SqliteConnector

        # 創建示例數據庫
        db_path = create_sample_sqlite_db()

        # 創建連接器
        connector = SqliteConnector(
            config={
                "database": db_path,
                "table": "products"
            }
        )

        # 創建 Agent
        agent = Agent(connector, config={
            "llm": {
                "api_key": api_key,
                "model": "gpt-3.5-turbo"
            },
            "verbose": True
        })

        print("\n使用自然語言查詢產品表：")

        queries = [
            "有多少種產品？",
            "哪個類別的產品最多？",
            "列出價格超過 10000 的產品",
            "庫存最少的 3 個產品是什麼？",
            "計算所有產品的平均價格"
        ]

        for i, query in enumerate(queries, 1):
            try:
                print(f"\n查詢 {i}: {query}")
                response = agent.chat(query)
                print(f"回答: {response}")
            except Exception as e:
                print(f"錯誤: {str(e)}")

    except ImportError as e:
        print(f"導入錯誤: {str(e)}")
        print("請安裝: pip install pandasai")
    except Exception as e:
        print(f"錯誤: {str(e)}")


def sqlalchemy_connection_example(api_key):
    """
    使用 SQLAlchemy 連接示例

    Args:
        api_key: OpenAI API 密鑰
    """
    print("\n" + "="*60)
    print("SQLAlchemy 連接示例")
    print("="*60)

    try:
        from pandasai import Agent

        # 創建示例數據庫
        db_path = create_sample_sqlite_db()

        # 使用 SQLAlchemy 創建引擎
        engine = create_engine(f"sqlite:///{db_path}")

        # 直接使用 DataFrame
        # 讀取訂單數據
        df = pd.read_sql("SELECT * FROM orders", engine)

        print(f"\n從數據庫讀取的訂單數據（{len(df)} 行）:")
        print(df.head())

        # 創建 Agent
        agent = Agent(df, config={
            "llm": {
                "api_key": api_key,
                "model": "gpt-3.5-turbo"
            },
            "verbose": False
        })

        print("\n使用自然語言查詢訂單數據：")

        queries = [
            "總共有多少筆訂單？",
            "總銷售額是多少？",
            "哪個客戶的訂單數量最多？",
            "平均訂單金額是多少？",
            "找出金額最高的 3 筆訂單"
        ]

        for i, query in enumerate(queries, 1):
            try:
                print(f"\n查詢 {i}: {query}")
                response = agent.chat(query)
                print(f"回答: {response}")
            except Exception as e:
                print(f"錯誤: {str(e)}")

    except ImportError as e:
        print(f"導入錯誤: {str(e)}")
        print("請安裝: pip install sqlalchemy")
    except Exception as e:
        print(f"錯誤: {str(e)}")


def multi_table_query_example(api_key):
    """
    多表關聯查詢示例

    Args:
        api_key: OpenAI API 密鑰
    """
    print("\n" + "="*60)
    print("多表關聯查詢示例")
    print("="*60)

    try:
        from pandasai import Agent

        # 創建示例數據庫
        db_path = create_sample_sqlite_db()
        engine = create_engine(f"sqlite:///{db_path}")

        # 執行 JOIN 查詢
        join_query = """
            SELECT
                o.order_id,
                c.customer_name,
                c.city,
                p.product_name,
                p.category,
                o.quantity,
                o.total_amount,
                o.order_date
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            JOIN products p ON o.product_id = p.product_id
        """

        df = pd.read_sql(join_query, engine)

        print(f"\n關聯查詢結果（{len(df)} 行）:")
        print(df.head(10))

        # 創建 Agent
        agent = Agent(df, config={
            "llm": {
                "api_key": api_key,
                "model": "gpt-3.5-turbo"
            },
            "verbose": False
        })

        print("\n使用自然語言查詢關聯數據：")

        queries = [
            "哪個城市的總銷售額最高？",
            "張三購買了哪些產品？",
            "電腦類別的總銷售額是多少？",
            "列出每個客戶的購買次數和總金額",
            "哪個產品最受歡迎？"
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


def postgresql_connection_template():
    """
    PostgreSQL 連接配置模板
    """
    print("\n" + "="*60)
    print("PostgreSQL 連接配置模板")
    print("="*60)

    template = """
# PostgreSQL 連接示例

from pandasai import Agent
from pandasai.connectors import PostgreSQLConnector

# 方式 1: 使用 Connector
connector = PostgreSQLConnector(
    config={{
        "host": "localhost",
        "port": 5432,
        "database": "your_database",
        "username": "your_username",
        "password": "your_password",
        "table": "your_table"
    }}
)

agent = Agent(connector, config={{
    "llm": {{
        "api_key": "your_api_key",
        "model": "gpt-3.5-turbo"
    }}
}})

# 方式 2: 使用 SQLAlchemy
from sqlalchemy import create_engine
import pandas as pd

connection_string = "postgresql://username:password@localhost:5432/database"
engine = create_engine(connection_string)

df = pd.read_sql("SELECT * FROM your_table", engine)
agent = Agent(df)

# 查詢示例
response = agent.chat("數據集中有多少行？")
print(response)
"""

    print(template)


def mysql_connection_template():
    """
    MySQL 連接配置模板
    """
    print("\n" + "="*60)
    print("MySQL 連接配置模板")
    print("="*60)

    template = """
# MySQL 連接示例

from pandasai import Agent
from pandasai.connectors import MySQLConnector

# 方式 1: 使用 Connector
connector = MySQLConnector(
    config={{
        "host": "localhost",
        "port": 3306,
        "database": "your_database",
        "username": "your_username",
        "password": "your_password",
        "table": "your_table"
    }}
)

agent = Agent(connector, config={{
    "llm": {{
        "api_key": "your_api_key",
        "model": "gpt-3.5-turbo"
    }}
}})

# 方式 2: 使用 SQLAlchemy
from sqlalchemy import create_engine
import pandas as pd

connection_string = "mysql+pymysql://username:password@localhost:3306/database"
engine = create_engine(connection_string)

df = pd.read_sql("SELECT * FROM your_table", engine)
agent = Agent(df)

# 查詢示例
response = agent.chat("統計各類別的數量")
print(response)
"""

    print(template)


def main():
    """
    主函數：演示 SQL 數據庫連接功能
    """
    print("PandasAI SQL 連接示例")
    print("="*60)

    # 檢查 API 密鑰
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("警告: 未找到 OPENAI_API_KEY 環境變量")
        print("請在 .env 文件中設置: OPENAI_API_KEY=your_api_key")
        print("\n顯示示例數據庫和配置模板...")

        # 創建示例數據庫並顯示內容
        db_path = create_sample_sqlite_db()

        # 顯示表內容
        conn = sqlite3.connect(db_path)

        print("\n產品表:")
        print(pd.read_sql("SELECT * FROM products", conn))

        print("\n客戶表:")
        print(pd.read_sql("SELECT * FROM customers", conn))

        print("\n訂單表:")
        print(pd.read_sql("SELECT * FROM orders", conn))

        conn.close()

        # 顯示連接模板
        postgresql_connection_template()
        mysql_connection_template()

        return

    try:
        # 1. SQLite 連接示例
        sqlite_connection_example(api_key)

        # 2. SQLAlchemy 連接示例
        sqlalchemy_connection_example(api_key)

        # 3. 多表關聯查詢示例
        multi_table_query_example(api_key)

        # 4. 顯示其他數據庫連接模板
        postgresql_connection_template()
        mysql_connection_template()

        # 總結
        print("\n" + "="*60)
        print("SQL 連接功能總結")
        print("="*60)
        print("✓ SQLite：本地數據庫，適合測試和小型應用")
        print("✓ PostgreSQL：企業級關係數據庫")
        print("✓ MySQL：流行的開源數據庫")
        print("✓ SQLAlchemy：統一的數據庫接口")
        print("✓ 多表查詢：支持 JOIN 等複雜查詢")
        print("✓ 自然語言：使用日常語言查詢數據庫")

        print("\n最佳實踐：")
        print("- 使用環境變量存儲數據庫憑證")
        print("- 定期備份數據庫")
        print("- 使用只讀用戶以提高安全性")
        print("- 對大表使用分頁查詢")
        print("- 驗證 AI 生成的查詢結果")
        print("- 監控數據庫性能")

    except ImportError as e:
        print(f"\n導入錯誤: {str(e)}")
        print("請運行: pip install pandasai sqlalchemy")
    except Exception as e:
        print(f"\n發生錯誤: {str(e)}")
        print(f"錯誤類型: {type(e).__name__}")

        # 提供故障排除建議
        print("\n故障排除建議:")
        print("1. 確保已安裝數據庫驅動")
        print("2. 檢查數據庫連接參數")
        print("3. 確認數據庫服務正在運行")
        print("4. 驗證用戶權限")
        print("5. 檢查網絡連接和防火牆設置")


if __name__ == "__main__":
    main()

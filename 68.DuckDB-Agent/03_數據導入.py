"""
DuckDB-Agent 示例 03: 數據導入

展示 DuckDB 的數據導入功能：
1. CSV 文件導入
2. Parquet 文件導入和導出
3. JSON 數據處理
4. Pandas DataFrame 集成
5. 遠程數據源（HTTP/S3）
6. 批量數據導入
"""

import duckdb
import pandas as pd
from pathlib import Path
from rich.console import Console
from rich.table import Table
import json

console = Console()


def setup_sample_data():
    """創建示例數據文件"""
    try:
        console.print("\n[bold cyan]準備示例數據[/bold cyan]")

        # 創建數據目錄
        data_dir = Path("./data")
        data_dir.mkdir(parents=True, exist_ok=True)

        # 創建 CSV 文件
        csv_data = """id,name,age,city,salary
1,張三,28,北京,75000
2,李四,32,上海,85000
3,王五,25,深圳,68000
4,趙六,35,北京,92000
5,孫七,29,廣州,71000
6,周八,31,上海,88000
7,吳九,27,深圳,73000
8,鄭十,33,北京,95000"""

        csv_path = data_dir / "employees.csv"
        csv_path.write_text(csv_data, encoding='utf-8')
        console.print(f"   ✓ 創建 CSV: {csv_path}", style="green")

        # 創建 JSON 文件
        json_data = [
            {"product_id": 1, "name": "MacBook Pro", "price": 2499.00, "category": "laptop"},
            {"product_id": 2, "name": "iPhone 15", "price": 999.00, "category": "phone"},
            {"product_id": 3, "name": "iPad Air", "price": 599.00, "category": "tablet"},
            {"product_id": 4, "name": "AirPods Pro", "price": 249.00, "category": "audio"},
            {"product_id": 5, "name": "Apple Watch", "price": 399.00, "category": "wearable"}
        ]

        json_path = data_dir / "products.json"
        json_path.write_text(json.dumps(json_data, ensure_ascii=False, indent=2), encoding='utf-8')
        console.print(f"   ✓ 創建 JSON: {json_path}", style="green")

        # 創建 Pandas DataFrame 並保存為 Parquet
        df_sales = pd.DataFrame({
            'sale_id': range(1, 11),
            'product': ['MacBook', 'iPhone', 'iPad', 'MacBook', 'iPhone',
                       'AirPods', 'Watch', 'iPad', 'MacBook', 'iPhone'],
            'quantity': [1, 2, 1, 1, 3, 2, 1, 2, 1, 1],
            'amount': [2499.0, 1998.0, 599.0, 2499.0, 2997.0,
                      498.0, 399.0, 1198.0, 2499.0, 999.0],
            'sale_date': pd.date_range('2025-01-01', periods=10, freq='D')
        })

        parquet_path = data_dir / "sales.parquet"
        df_sales.to_parquet(parquet_path, index=False)
        console.print(f"   ✓ 創建 Parquet: {parquet_path}", style="green")

        return data_dir

    except Exception as e:
        console.print(f"[red]✗ 準備數據失敗: {e}[/red]")
        raise


def import_csv_data(con, data_dir):
    """導入 CSV 數據"""
    console.print("\n[bold cyan]1. CSV 數據導入[/bold cyan]")

    try:
        csv_path = data_dir / "employees.csv"

        # 方法 1: 直接查詢 CSV 文件
        console.print("\n   [yellow]方法 1: 直接查詢 CSV 文件[/yellow]")
        result = con.execute(f"""
            SELECT * FROM '{csv_path}'
            LIMIT 3
        """).fetchdf()
        console.print(result.to_string(index=False))

        # 方法 2: 導入到表中
        console.print("\n   [yellow]方法 2: 導入到表中[/yellow]")
        con.execute(f"""
            CREATE TABLE employees AS
            SELECT * FROM read_csv_auto('{csv_path}')
        """)
        count = con.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
        console.print(f"   ✓ 導入 {count} 條記錄到 employees 表", style="green")

        # 方法 3: 使用 COPY 命令
        console.print("\n   [yellow]方法 3: 使用 COPY 命令[/yellow]")
        con.execute("""
            CREATE TABLE employees_copy (
                id INTEGER,
                name VARCHAR,
                age INTEGER,
                city VARCHAR,
                salary DECIMAL(10, 2)
            )
        """)
        con.execute(f"COPY employees_copy FROM '{csv_path}' (HEADER)")
        count = con.execute("SELECT COUNT(*) FROM employees_copy").fetchone()[0]
        console.print(f"   ✓ COPY 導入 {count} 條記錄", style="green")

        # 查看導入的數據
        console.print("\n   [yellow]導入的數據統計:[/yellow]")
        stats = con.execute("""
            SELECT
                city,
                COUNT(*) as employee_count,
                AVG(salary) as avg_salary,
                MAX(salary) as max_salary
            FROM employees
            GROUP BY city
            ORDER BY avg_salary DESC
        """).fetchdf()
        console.print(stats.to_string(index=False))

    except Exception as e:
        console.print(f"[red]✗ CSV 導入失敗: {e}[/red]")
        raise


def import_parquet_data(con, data_dir):
    """導入和導出 Parquet 數據"""
    console.print("\n[bold cyan]2. Parquet 數據導入和導出[/bold cyan]")

    try:
        parquet_path = data_dir / "sales.parquet"

        # 直接查詢 Parquet 文件
        console.print("\n   [yellow]直接查詢 Parquet 文件:[/yellow]")
        result = con.execute(f"""
            SELECT
                product,
                COUNT(*) as sales_count,
                SUM(amount) as total_revenue
            FROM '{parquet_path}'
            GROUP BY product
            ORDER BY total_revenue DESC
        """).fetchdf()
        console.print(result.to_string(index=False))

        # 創建表並導入
        con.execute(f"""
            CREATE TABLE sales AS
            SELECT * FROM '{parquet_path}'
        """)
        console.print("\n   ✓ 創建 sales 表", style="green")

        # 導出為 Parquet
        export_path = data_dir / "sales_export.parquet"
        con.execute(f"""
            COPY (
                SELECT *
                FROM sales
                WHERE amount > 1000
            ) TO '{export_path}' (FORMAT PARQUET)
        """)
        console.print(f"   ✓ 導出高價值訂單到: {export_path}", style="green")

        # 查看導出文件的數據
        result = con.execute(f"SELECT COUNT(*) FROM '{export_path}'").fetchone()[0]
        console.print(f"   導出記錄數: {result}", style="yellow")

        # Parquet 元數據
        console.print("\n   [yellow]Parquet 文件信息:[/yellow]")
        metadata = con.execute(f"""
            SELECT
                COUNT(*) as row_count,
                COUNT(DISTINCT product) as unique_products,
                MIN(sale_date) as first_sale,
                MAX(sale_date) as last_sale
            FROM '{parquet_path}'
        """).fetchdf()
        console.print(metadata.to_string(index=False))

    except Exception as e:
        console.print(f"[red]✗ Parquet 操作失敗: {e}[/red]")
        raise


def import_json_data(con, data_dir):
    """導入 JSON 數據"""
    console.print("\n[bold cyan]3. JSON 數據導入[/bold cyan]")

    try:
        json_path = data_dir / "products.json"

        # 直接查詢 JSON 文件
        console.print("\n   [yellow]直接查詢 JSON 文件:[/yellow]")
        result = con.execute(f"""
            SELECT * FROM read_json_auto('{json_path}')
        """).fetchdf()
        console.print(result.to_string(index=False))

        # 創建表並導入
        con.execute(f"""
            CREATE TABLE products AS
            SELECT * FROM '{json_path}'
        """)
        console.print("\n   ✓ 創建 products 表", style="green")

        # JSON 數據分析
        console.print("\n   [yellow]按類別統計產品:[/yellow]")
        stats = con.execute("""
            SELECT
                category,
                COUNT(*) as product_count,
                AVG(price) as avg_price,
                SUM(price) as total_value
            FROM products
            GROUP BY category
            ORDER BY total_value DESC
        """).fetchdf()
        console.print(stats.to_string(index=False))

        # 導出為 JSON
        export_json_path = data_dir / "products_export.json"
        con.execute(f"""
            COPY (
                SELECT name, price, category
                FROM products
                WHERE price > 500
            ) TO '{export_json_path}' (FORMAT JSON, ARRAY true)
        """)
        console.print(f"\n   ✓ 導出高價產品到: {export_json_path}", style="green")

    except Exception as e:
        console.print(f"[red]✗ JSON 導入失敗: {e}[/red]")
        raise


def pandas_integration(con):
    """Pandas DataFrame 集成"""
    console.print("\n[bold cyan]4. Pandas DataFrame 集成[/bold cyan]")

    try:
        # 創建 Pandas DataFrame
        df = pd.DataFrame({
            'transaction_id': range(1, 6),
            'customer': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
            'amount': [1200.50, 850.00, 2100.75, 450.00, 1800.25],
            'payment_method': ['信用卡', '支付寶', '微信', '信用卡', '支付寶']
        })

        console.print("\n   [yellow]原始 Pandas DataFrame:[/yellow]")
        console.print(df.to_string(index=False))

        # 方法 1: 直接查詢 DataFrame (零拷貝)
        console.print("\n   [yellow]方法 1: 直接查詢 DataFrame[/yellow]")
        result = con.execute("""
            SELECT
                payment_method,
                COUNT(*) as transaction_count,
                SUM(amount) as total_amount
            FROM df
            GROUP BY payment_method
        """).fetchdf()
        console.print(result.to_string(index=False))

        # 方法 2: 註冊為視圖
        console.print("\n   [yellow]方法 2: 註冊為視圖[/yellow]")
        con.register('transactions_view', df)
        result = con.execute("""
            SELECT customer, amount
            FROM transactions_view
            WHERE amount > 1000
            ORDER BY amount DESC
        """).fetchdf()
        console.print(result.to_string(index=False))

        # 方法 3: 創建表
        console.print("\n   [yellow]方法 3: 創建表[/yellow]")
        con.execute("CREATE TABLE transactions AS SELECT * FROM df")
        count = con.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
        console.print(f"   ✓ 創建表，包含 {count} 條記錄", style="green")

        # 將查詢結果轉換為 DataFrame
        console.print("\n   [yellow]查詢結果轉 DataFrame:[/yellow]")
        result_df = con.execute("""
            SELECT
                customer,
                amount,
                amount * 1.1 as amount_with_tax
            FROM transactions
            ORDER BY amount DESC
        """).df()  # 或使用 .fetchdf()

        console.print(result_df.to_string(index=False))
        console.print(f"\n   結果類型: {type(result_df)}", style="yellow")

    except Exception as e:
        console.print(f"[red]✗ Pandas 集成失敗: {e}[/red]")
        raise


def remote_data_sources(con):
    """遠程數據源查詢"""
    console.print("\n[bold cyan]5. 遠程數據源（示例）[/bold cyan]")

    try:
        # 注意: 以下示例需要網絡連接和實際的遠程文件

        console.print("\n   [yellow]HTTP CSV 查詢示例:[/yellow]")
        console.print("""
        -- 查詢遠程 CSV 文件
        SELECT * FROM read_csv_auto('https://example.com/data.csv')
        LIMIT 10;
        """)

        console.print("\n   [yellow]S3 Parquet 查詢示例:[/yellow]")
        console.print("""
        -- 配置 S3 憑證
        CREATE SECRET (
            TYPE S3,
            KEY_ID 'your_access_key_id',
            SECRET 'your_secret_access_key',
            REGION 'us-east-1'
        );

        -- 查詢 S3 上的 Parquet 文件
        SELECT * FROM 's3://my-bucket/data/*.parquet'
        WHERE year = 2025;
        """)

        console.print("\n   [yellow]HTTP Parquet 直接查詢:[/yellow]")
        console.print("""
        -- 直接查詢遠程 Parquet 文件（只下載需要的列和行）
        SELECT product, SUM(sales)
        FROM 'https://example.com/sales.parquet'
        WHERE year = 2025
        GROUP BY product;
        """)

        console.print("\n   ✓ DuckDB 支持直接查詢遠程數據源", style="green")
        console.print("   ✓ 自動下載並緩存數據", style="green")
        console.print("   ✓ 謂詞下推優化（只下載需要的數據）", style="green")

    except Exception as e:
        console.print(f"[red]✗ 遠程數據源示例失敗: {e}[/red]")
        raise


def batch_import_operations(con, data_dir):
    """批量數據導入操作"""
    console.print("\n[bold cyan]6. 批量數據導入[/bold cyan]")

    try:
        # 創建多個 CSV 文件
        console.print("\n   [yellow]創建多個 CSV 文件:[/yellow]")
        for i in range(3):
            csv_data = f"""date,value,category
2025-01-{i+1:02d},100,A
2025-01-{i+1:02d},200,B
2025-01-{i+1:02d},150,C"""

            csv_path = data_dir / f"batch_{i+1}.csv"
            csv_path.write_text(csv_data, encoding='utf-8')
            console.print(f"   ✓ 創建: {csv_path.name}", style="green")

        # 使用通配符一次性查詢所有文件
        console.print("\n   [yellow]使用通配符查詢所有 CSV:[/yellow]")
        pattern = str(data_dir / "batch_*.csv")
        result = con.execute(f"""
            SELECT
                category,
                COUNT(*) as record_count,
                SUM(value) as total_value
            FROM '{pattern}'
            GROUP BY category
            ORDER BY category
        """).fetchdf()
        console.print(result.to_string(index=False))

        # 創建合併表
        console.print("\n   [yellow]創建合併表:[/yellow]")
        con.execute(f"""
            CREATE TABLE batch_data AS
            SELECT * FROM '{pattern}'
        """)
        count = con.execute("SELECT COUNT(*) FROM batch_data").fetchone()[0]
        console.print(f"   ✓ 合併導入 {count} 條記錄", style="green")

        # 查看數據分布
        console.print("\n   [yellow]數據分布:[/yellow]")
        distribution = con.execute("""
            SELECT
                date,
                COUNT(*) as records,
                SUM(value) as total
            FROM batch_data
            GROUP BY date
            ORDER BY date
        """).fetchdf()
        console.print(distribution.to_string(index=False))

    except Exception as e:
        console.print(f"[red]✗ 批量導入失敗: {e}[/red]")
        raise


def export_data_formats(con, data_dir):
    """導出各種數據格式"""
    console.print("\n[bold cyan]7. 數據導出[/bold cyan]")

    try:
        # 導出為 CSV
        csv_export = data_dir / "employees_export.csv"
        con.execute(f"""
            COPY (
                SELECT * FROM employees
                WHERE salary > 75000
                ORDER BY salary DESC
            ) TO '{csv_export}' (HEADER, DELIMITER ',')
        """)
        console.print(f"   ✓ 導出 CSV: {csv_export.name}", style="green")

        # 導出為 Parquet
        parquet_export = data_dir / "employees_export.parquet"
        con.execute(f"""
            COPY employees TO '{parquet_export}' (FORMAT PARQUET)
        """)
        console.print(f"   ✓ 導出 Parquet: {parquet_export.name}", style="green")

        # 導出為 JSON
        json_export = data_dir / "employees_export.json"
        con.execute(f"""
            COPY (
                SELECT name, city, salary
                FROM employees
                ORDER BY salary DESC
                LIMIT 5
            ) TO '{json_export}' (FORMAT JSON, ARRAY true)
        """)
        console.print(f"   ✓ 導出 JSON: {json_export.name}", style="green")

        # 查看導出的 JSON 內容
        console.print("\n   [yellow]導出的 JSON 內容:[/yellow]")
        if json_export.exists():
            content = json.loads(json_export.read_text(encoding='utf-8'))
            for item in content[:3]:
                console.print(f"   {item}")

    except Exception as e:
        console.print(f"[red]✗ 數據導出失敗: {e}[/red]")
        raise


def main():
    """主函數"""
    console.print("\n[bold magenta]═══════════════════════════════════════[/bold magenta]")
    console.print("[bold magenta]     DuckDB 數據導入示例     [/bold magenta]")
    console.print("[bold magenta]═══════════════════════════════════════[/bold magenta]")

    try:
        # 準備示例數據
        data_dir = setup_sample_data()

        # 創建數據庫連接
        con = duckdb.connect(':memory:')

        # 1. CSV 導入
        import_csv_data(con, data_dir)

        # 2. Parquet 導入和導出
        import_parquet_data(con, data_dir)

        # 3. JSON 導入
        import_json_data(con, data_dir)

        # 4. Pandas 集成
        pandas_integration(con)

        # 5. 遠程數據源
        remote_data_sources(con)

        # 6. 批量導入
        batch_import_operations(con, data_dir)

        # 7. 數據導出
        export_data_formats(con, data_dir)

        # 清理
        con.close()

        console.print("\n[bold green]✓ 所有數據導入示例執行成功！[/bold green]")
        console.print("\n[yellow]DuckDB 數據導入優勢:[/yellow]")
        console.print("  - 支持多種格式: CSV, Parquet, JSON, Excel")
        console.print("  - 零拷貝 Pandas/Arrow 集成")
        console.print("  - 直接查詢文件，無需先導入")
        console.print("  - 支持遠程數據源 (HTTP, S3)")
        console.print("  - 謂詞下推優化，只讀取需要的數據")
        console.print("  - 通配符支持，批量處理文件")

    except Exception as e:
        console.print(f"\n[bold red]✗ 執行失敗: {e}[/bold red]")
        raise


if __name__ == "__main__":
    main()

"""
DuckDB-Agent 示例 02: SQL 查詢

展示 DuckDB 的 SQL 查詢功能：
1. 標準 SQL 查詢（SELECT, WHERE, ORDER BY）
2. 聚合函數（COUNT, SUM, AVG, MIN, MAX）
3. 分組查詢（GROUP BY, HAVING）
4. 連接查詢（INNER JOIN, LEFT JOIN）
5. 子查詢和 CTE（WITH）
6. 高級查詢技巧
"""

import duckdb
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import pandas as pd

console = Console()


def setup_database():
    """設置測試數據庫"""
    try:
        con = duckdb.connect(':memory:')

        # 創建訂單表
        con.execute("""
            CREATE TABLE orders (
                order_id INTEGER PRIMARY KEY,
                customer_id INTEGER,
                product_name VARCHAR,
                quantity INTEGER,
                unit_price DECIMAL(10, 2),
                order_date DATE,
                status VARCHAR
            )
        """)

        # 插入訂單數據
        con.execute("""
            INSERT INTO orders VALUES
            (1, 101, 'MacBook Pro', 1, 2499.00, '2025-01-15', '已完成'),
            (2, 102, 'iPhone 15', 2, 999.00, '2025-01-16', '已完成'),
            (3, 101, 'AirPods Pro', 1, 249.00, '2025-01-17', '處理中'),
            (4, 103, 'iPad Air', 1, 599.00, '2025-01-18', '已完成'),
            (5, 102, 'Apple Watch', 1, 399.00, '2025-01-19', '已完成'),
            (6, 104, 'MacBook Air', 1, 1299.00, '2025-01-20', '已取消'),
            (7, 101, 'Magic Keyboard', 2, 99.00, '2025-01-21', '已完成'),
            (8, 105, 'Mac Mini', 1, 699.00, '2025-01-22', '處理中'),
            (9, 103, 'Studio Display', 1, 1599.00, '2025-01-23', '已完成'),
            (10, 102, 'AirTag 4-pack', 3, 99.00, '2025-01-24', '已完成')
        """)

        # 創建客戶表
        con.execute("""
            CREATE TABLE customers (
                customer_id INTEGER PRIMARY KEY,
                name VARCHAR,
                email VARCHAR,
                city VARCHAR,
                registration_date DATE
            )
        """)

        # 插入客戶數據
        con.execute("""
            INSERT INTO customers VALUES
            (101, '張三', 'zhangsan@email.com', '北京', '2024-06-15'),
            (102, '李四', 'lisi@email.com', '上海', '2024-07-20'),
            (103, '王五', 'wangwu@email.com', '深圳', '2024-08-10'),
            (104, '趙六', 'zhaoliu@email.com', '北京', '2024-09-05'),
            (105, '孫七', 'sunqi@email.com', '廣州', '2024-10-12')
        """)

        console.print("[green]✓ 測試數據庫設置完成[/green]")
        return con

    except Exception as e:
        console.print(f"[red]✗ 設置數據庫失敗: {e}[/red]")
        raise


def basic_select_queries(con):
    """基本 SELECT 查詢"""
    console.print("\n[bold cyan]1. 基本 SELECT 查詢[/bold cyan]")

    try:
        # 簡單查詢
        console.print("\n   [yellow]查詢所有訂單:[/yellow]")
        result = con.execute("""
            SELECT order_id, product_name, quantity, unit_price
            FROM orders
            LIMIT 5
        """).fetchdf()
        console.print(result.to_string(index=False))

        # WHERE 條件查詢
        console.print("\n   [yellow]查詢高價值訂單 (> $500):[/yellow]")
        result = con.execute("""
            SELECT
                order_id,
                product_name,
                quantity * unit_price as total_amount
            FROM orders
            WHERE quantity * unit_price > 500
            ORDER BY total_amount DESC
        """).fetchdf()
        console.print(result.to_string(index=False))

        # LIKE 模糊查詢
        console.print("\n   [yellow]查詢 Mac 相關產品:[/yellow]")
        result = con.execute("""
            SELECT product_name, unit_price
            FROM orders
            WHERE product_name LIKE '%Mac%'
        """).fetchdf()
        console.print(result.to_string(index=False))

    except Exception as e:
        console.print(f"[red]✗ 基本查詢失敗: {e}[/red]")
        raise


def aggregation_queries(con):
    """聚合查詢"""
    console.print("\n[bold cyan]2. 聚合函數查詢[/bold cyan]")

    try:
        # 基本聚合
        console.print("\n   [yellow]訂單統計:[/yellow]")
        result = con.execute("""
            SELECT
                COUNT(*) as total_orders,
                COUNT(DISTINCT customer_id) as unique_customers,
                SUM(quantity * unit_price) as total_revenue,
                AVG(quantity * unit_price) as avg_order_value,
                MIN(unit_price) as min_price,
                MAX(unit_price) as max_price
            FROM orders
            WHERE status = '已完成'
        """).fetchdf()
        console.print(result.to_string(index=False))

        # 字符串聚合
        console.print("\n   [yellow]產品列表聚合:[/yellow]")
        result = con.execute("""
            SELECT
                customer_id,
                STRING_AGG(product_name, ', ' ORDER BY order_date) as products,
                COUNT(*) as order_count
            FROM orders
            GROUP BY customer_id
            ORDER BY order_count DESC
        """).fetchdf()
        console.print(result.to_string(index=False))

    except Exception as e:
        console.print(f"[red]✗ 聚合查詢失敗: {e}[/red]")
        raise


def group_by_queries(con):
    """分組查詢"""
    console.print("\n[bold cyan]3. GROUP BY 分組查詢[/bold cyan]")

    try:
        # 按狀態分組
        console.print("\n   [yellow]按訂單狀態分組:[/yellow]")
        result = con.execute("""
            SELECT
                status,
                COUNT(*) as order_count,
                SUM(quantity * unit_price) as total_amount,
                AVG(quantity * unit_price) as avg_amount
            FROM orders
            GROUP BY status
            ORDER BY total_amount DESC
        """).fetchdf()
        console.print(result.to_string(index=False))

        # HAVING 子句
        console.print("\n   [yellow]高價值客戶 (總消費 > $1000):[/yellow]")
        result = con.execute("""
            SELECT
                customer_id,
                COUNT(*) as order_count,
                SUM(quantity * unit_price) as total_spent
            FROM orders
            WHERE status = '已完成'
            GROUP BY customer_id
            HAVING SUM(quantity * unit_price) > 1000
            ORDER BY total_spent DESC
        """).fetchdf()
        console.print(result.to_string(index=False))

        # 多列分組
        console.print("\n   [yellow]按客戶和狀態分組:[/yellow]")
        result = con.execute("""
            SELECT
                customer_id,
                status,
                COUNT(*) as order_count,
                SUM(quantity * unit_price) as total_amount
            FROM orders
            GROUP BY customer_id, status
            ORDER BY customer_id, status
        """).fetchdf()
        console.print(result.to_string(index=False))

    except Exception as e:
        console.print(f"[red]✗ 分組查詢失敗: {e}[/red]")
        raise


def join_queries(con):
    """連接查詢"""
    console.print("\n[bold cyan]4. JOIN 連接查詢[/bold cyan]")

    try:
        # INNER JOIN
        console.print("\n   [yellow]訂單與客戶信息（INNER JOIN）:[/yellow]")
        result = con.execute("""
            SELECT
                o.order_id,
                c.name,
                c.city,
                o.product_name,
                o.quantity * o.unit_price as total_amount
            FROM orders o
            INNER JOIN customers c ON o.customer_id = c.customer_id
            WHERE o.status = '已完成'
            ORDER BY total_amount DESC
            LIMIT 5
        """).fetchdf()
        console.print(result.to_string(index=False))

        # 聚合 JOIN
        console.print("\n   [yellow]每個客戶的訂單統計:[/yellow]")
        result = con.execute("""
            SELECT
                c.name,
                c.city,
                COUNT(o.order_id) as order_count,
                COALESCE(SUM(o.quantity * o.unit_price), 0) as total_spent
            FROM customers c
            LEFT JOIN orders o
                ON c.customer_id = o.customer_id
                AND o.status = '已完成'
            GROUP BY c.customer_id, c.name, c.city
            ORDER BY total_spent DESC
        """).fetchdf()
        console.print(result.to_string(index=False))

    except Exception as e:
        console.print(f"[red]✗ 連接查詢失敗: {e}[/red]")
        raise


def subquery_examples(con):
    """子查詢示例"""
    console.print("\n[bold cyan]5. 子查詢示例[/bold cyan]")

    try:
        # 標量子查詢
        console.print("\n   [yellow]高於平均訂單金額的訂單:[/yellow]")
        result = con.execute("""
            SELECT
                order_id,
                product_name,
                quantity * unit_price as amount
            FROM orders
            WHERE quantity * unit_price > (
                SELECT AVG(quantity * unit_price)
                FROM orders
            )
            ORDER BY amount DESC
        """).fetchdf()
        console.print(result.to_string(index=False))

        # IN 子查詢
        console.print("\n   [yellow]有多次購買的客戶:[/yellow]")
        result = con.execute("""
            SELECT
                customer_id,
                name,
                city
            FROM customers
            WHERE customer_id IN (
                SELECT customer_id
                FROM orders
                GROUP BY customer_id
                HAVING COUNT(*) > 1
            )
        """).fetchdf()
        console.print(result.to_string(index=False))

        # EXISTS 子查詢
        console.print("\n   [yellow]有已完成訂單的客戶:[/yellow]")
        result = con.execute("""
            SELECT
                c.name,
                c.email
            FROM customers c
            WHERE EXISTS (
                SELECT 1
                FROM orders o
                WHERE o.customer_id = c.customer_id
                AND o.status = '已完成'
            )
        """).fetchdf()
        console.print(result.to_string(index=False))

    except Exception as e:
        console.print(f"[red]✗ 子查詢失敗: {e}[/red]")
        raise


def cte_examples(con):
    """CTE（公用表表達式）示例"""
    console.print("\n[bold cyan]6. CTE（WITH 子句）示例[/bold cyan]")

    try:
        # 簡單 CTE
        console.print("\n   [yellow]使用 CTE 計算訂單總額:[/yellow]")
        result = con.execute("""
            WITH order_totals AS (
                SELECT
                    order_id,
                    customer_id,
                    quantity * unit_price as total_amount
                FROM orders
                WHERE status = '已完成'
            )
            SELECT
                c.name,
                COUNT(ot.order_id) as order_count,
                SUM(ot.total_amount) as total_spent
            FROM order_totals ot
            JOIN customers c ON ot.customer_id = c.customer_id
            GROUP BY c.customer_id, c.name
            ORDER BY total_spent DESC
        """).fetchdf()
        console.print(result.to_string(index=False))

        # 多個 CTE
        console.print("\n   [yellow]多個 CTE 組合查詢:[/yellow]")
        result = con.execute("""
            WITH
            completed_orders AS (
                SELECT *
                FROM orders
                WHERE status = '已完成'
            ),
            customer_stats AS (
                SELECT
                    customer_id,
                    COUNT(*) as order_count,
                    SUM(quantity * unit_price) as total_spent
                FROM completed_orders
                GROUP BY customer_id
            )
            SELECT
                c.name,
                c.city,
                cs.order_count,
                cs.total_spent,
                cs.total_spent / cs.order_count as avg_order_value
            FROM customer_stats cs
            JOIN customers c ON cs.customer_id = c.customer_id
            ORDER BY cs.total_spent DESC
        """).fetchdf()
        console.print(result.to_string(index=False))

    except Exception as e:
        console.print(f"[red]✗ CTE 查詢失敗: {e}[/red]")
        raise


def advanced_queries(con):
    """高級查詢技巧"""
    console.print("\n[bold cyan]7. 高級查詢技巧[/bold cyan]")

    try:
        # CASE WHEN
        console.print("\n   [yellow]使用 CASE 進行分類:[/yellow]")
        result = con.execute("""
            SELECT
                product_name,
                unit_price,
                CASE
                    WHEN unit_price < 100 THEN '低價'
                    WHEN unit_price < 500 THEN '中價'
                    WHEN unit_price < 1000 THEN '高價'
                    ELSE '奢侈品'
                END as price_category
            FROM orders
            GROUP BY product_name, unit_price
            ORDER BY unit_price DESC
        """).fetchdf()
        console.print(result.to_string(index=False))

        # UNION
        console.print("\n   [yellow]合併查詢結果:[/yellow]")
        result = con.execute("""
            SELECT 'high_value' as category, COUNT(*) as count
            FROM orders
            WHERE quantity * unit_price > 1000

            UNION ALL

            SELECT 'medium_value' as category, COUNT(*) as count
            FROM orders
            WHERE quantity * unit_price BETWEEN 100 AND 1000

            UNION ALL

            SELECT 'low_value' as category, COUNT(*) as count
            FROM orders
            WHERE quantity * unit_price < 100
        """).fetchdf()
        console.print(result.to_string(index=False))

        # DISTINCT ON (DuckDB 特性)
        console.print("\n   [yellow]每個客戶的最新訂單:[/yellow]")
        result = con.execute("""
            SELECT DISTINCT ON (customer_id)
                customer_id,
                product_name,
                order_date
            FROM orders
            ORDER BY customer_id, order_date DESC
        """).fetchdf()
        console.print(result.to_string(index=False))

    except Exception as e:
        console.print(f"[red]✗ 高級查詢失敗: {e}[/red]")
        raise


def main():
    """主函數"""
    console.print("\n[bold magenta]═══════════════════════════════════════[/bold magenta]")
    console.print("[bold magenta]      DuckDB SQL 查詢示例      [/bold magenta]")
    console.print("[bold magenta]═══════════════════════════════════════[/bold magenta]")

    try:
        # 設置數據庫
        con = setup_database()

        # 1. 基本查詢
        basic_select_queries(con)

        # 2. 聚合查詢
        aggregation_queries(con)

        # 3. 分組查詢
        group_by_queries(con)

        # 4. 連接查詢
        join_queries(con)

        # 5. 子查詢
        subquery_examples(con)

        # 6. CTE
        cte_examples(con)

        # 7. 高級查詢
        advanced_queries(con)

        # 清理
        con.close()

        console.print("\n[bold green]✓ 所有 SQL 查詢示例執行成功！[/bold green]")
        console.print("\n[yellow]DuckDB SQL 特性:[/yellow]")
        console.print("  - 完整的 SQL-92/99/2003 支持")
        console.print("  - DISTINCT ON 子句")
        console.print("  - STRING_AGG 等高級聚合函數")
        console.print("  - 豐富的日期時間函數")
        console.print("  - 正則表達式支持")

    except Exception as e:
        console.print(f"\n[bold red]✗ 執行失敗: {e}[/bold red]")
        raise


if __name__ == "__main__":
    main()

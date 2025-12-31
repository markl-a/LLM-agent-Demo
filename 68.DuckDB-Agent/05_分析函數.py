"""
DuckDB-Agent 示例 05: 分析函數

展示 DuckDB 的高級分析功能：
1. 窗口函數（Window Functions）
2. 排名函數（RANK, DENSE_RANK, ROW_NUMBER）
3. 聚合窗口函數
4. 移動平均和累計值
5. Lead/Lag 函數
6. 分區和排序
"""

import duckdb
from rich.console import Console
from rich.table import Table
import pandas as pd

console = Console()


def setup_database():
    """設置示例數據庫"""
    try:
        con = duckdb.connect(':memory:')

        # 創建銷售數據表
        con.execute("""
            CREATE TABLE daily_sales (
                sale_id INTEGER,
                product VARCHAR,
                category VARCHAR,
                amount DECIMAL(10, 2),
                sale_date DATE,
                region VARCHAR,
                sales_person VARCHAR
            )
        """)

        # 插入示例數據
        con.execute("""
            INSERT INTO daily_sales VALUES
            -- 第一周
            (1, 'MacBook Pro', '電腦', 2499.00, '2025-01-01', '華北', '張三'),
            (2, 'iPhone 15', '手機', 999.00, '2025-01-01', '華東', '李四'),
            (3, 'iPad Air', '平板', 599.00, '2025-01-02', '華北', '張三'),
            (4, 'MacBook Air', '電腦', 1299.00, '2025-01-02', '華南', '王五'),
            (5, 'iPhone 15', '手機', 999.00, '2025-01-03', '華東', '李四'),
            -- 第二周
            (6, 'AirPods Pro', '配件', 249.00, '2025-01-08', '華北', '張三'),
            (7, 'Apple Watch', '配件', 399.00, '2025-01-08', '華東', '李四'),
            (8, 'MacBook Pro', '電腦', 2499.00, '2025-01-09', '華南', '王五'),
            (9, 'iPad Pro', '平板', 1099.00, '2025-01-09', '華北', '張三'),
            (10, 'iPhone 15 Pro', '手機', 1199.00, '2025-01-10', '華東', '李四'),
            -- 第三周
            (11, 'Mac Mini', '電腦', 699.00, '2025-01-15', '華北', '張三'),
            (12, 'AirTag', '配件', 29.00, '2025-01-15', '華東', '李四'),
            (13, 'Magic Keyboard', '配件', 99.00, '2025-01-16', '華南', '王五'),
            (14, 'Studio Display', '配件', 1599.00, '2025-01-16', '華北', '張三'),
            (15, 'iPhone 15', '手機', 999.00, '2025-01-17', '華東', '李四'),
            -- 第四周
            (16, 'MacBook Pro', '電腦', 2499.00, '2025-01-22', '華南', '王五'),
            (17, 'iPad Air', '平板', 599.00, '2025-01-22', '華北', '張三'),
            (18, 'Apple Watch Ultra', '配件', 799.00, '2025-01-23', '華東', '李四'),
            (19, 'iPhone 15 Pro Max', '手機', 1399.00, '2025-01-23', '華南', '王五'),
            (20, 'MacBook Air', '電腦', 1299.00, '2025-01-24', '華北', '張三')
        """)

        console.print("[green]✓ 測試數據庫設置完成[/green]")
        return con

    except Exception as e:
        console.print(f"[red]✗ 設置數據庫失敗: {e}[/red]")
        raise


def demonstrate_ranking_functions(con):
    """展示排名函數"""
    console.print("\n[bold cyan]1. 排名函數（RANK, DENSE_RANK, ROW_NUMBER）[/bold cyan]")

    try:
        # ROW_NUMBER, RANK, DENSE_RANK 對比
        console.print("\n   [yellow]各區域銷售排名:[/yellow]")
        result = con.execute("""
            SELECT
                region,
                sales_person,
                amount,
                ROW_NUMBER() OVER (PARTITION BY region ORDER BY amount DESC) as row_num,
                RANK() OVER (PARTITION BY region ORDER BY amount DESC) as rank,
                DENSE_RANK() OVER (PARTITION BY region ORDER BY amount DESC) as dense_rank
            FROM daily_sales
            ORDER BY region, amount DESC
        """).fetchdf()
        console.print(result.head(12).to_string(index=False))

        # 獲取每個類別的前 3 名
        console.print("\n   [yellow]每個產品類別的銷售 TOP 3:[/yellow]")
        result = con.execute("""
            WITH ranked_sales AS (
                SELECT
                    category,
                    product,
                    amount,
                    RANK() OVER (PARTITION BY category ORDER BY amount DESC) as rank
                FROM daily_sales
            )
            SELECT
                category,
                product,
                amount,
                rank
            FROM ranked_sales
            WHERE rank <= 3
            ORDER BY category, rank
        """).fetchdf()
        console.print(result.to_string(index=False))

        # NTILE - 分成四分位
        console.print("\n   [yellow]銷售額四分位分組:[/yellow]")
        result = con.execute("""
            SELECT
                product,
                amount,
                NTILE(4) OVER (ORDER BY amount) as quartile
            FROM daily_sales
            ORDER BY amount DESC
            LIMIT 10
        """).fetchdf()
        console.print(result.to_string(index=False))

    except Exception as e:
        console.print(f"[red]✗ 排名函數示例失敗: {e}[/red]")
        raise


def demonstrate_aggregate_windows(con):
    """展示聚合窗口函數"""
    console.print("\n[bold cyan]2. 聚合窗口函數[/bold cyan]")

    try:
        # 計算每個銷售相對於類別平均的表現
        console.print("\n   [yellow]與類別平均值對比:[/yellow]")
        result = con.execute("""
            SELECT
                product,
                category,
                amount,
                AVG(amount) OVER (PARTITION BY category) as category_avg,
                amount - AVG(amount) OVER (PARTITION BY category) as diff_from_avg,
                ROUND(amount / AVG(amount) OVER (PARTITION BY category) * 100, 2) as pct_of_avg
            FROM daily_sales
            ORDER BY category, amount DESC
        """).fetchdf()
        console.print(result.head(12).to_string(index=False))

        # 計算區域銷售佔比
        console.print("\n   [yellow]區域銷售佔比:[/yellow]")
        result = con.execute("""
            SELECT
                region,
                sales_person,
                SUM(amount) as total_sales,
                SUM(SUM(amount)) OVER () as grand_total,
                ROUND(SUM(amount) / SUM(SUM(amount)) OVER () * 100, 2) as pct_of_total
            FROM daily_sales
            GROUP BY region, sales_person
            ORDER BY total_sales DESC
        """).fetchdf()
        console.print(result.to_string(index=False))

        # MIN, MAX 窗口函數
        console.print("\n   [yellow]每日銷售與極值對比:[/yellow]")
        result = con.execute("""
            SELECT
                sale_date,
                product,
                amount,
                MIN(amount) OVER (PARTITION BY sale_date) as daily_min,
                MAX(amount) OVER (PARTITION BY sale_date) as daily_max,
                AVG(amount) OVER (PARTITION BY sale_date) as daily_avg
            FROM daily_sales
            ORDER BY sale_date, amount DESC
        """).fetchdf()
        console.print(result.head(10).to_string(index=False))

    except Exception as e:
        console.print(f"[red]✗ 聚合窗口函數失敗: {e}[/red]")
        raise


def demonstrate_moving_calculations(con):
    """展示移動計算和累計值"""
    console.print("\n[bold cyan]3. 移動平均和累計值[/bold cyan]")

    try:
        # 按日期聚合數據
        con.execute("""
            CREATE TEMP TABLE daily_totals AS
            SELECT
                sale_date,
                SUM(amount) as daily_total
            FROM daily_sales
            GROUP BY sale_date
            ORDER BY sale_date
        """)

        # 移動平均（3 天）
        console.print("\n   [yellow]3 日移動平均:[/yellow]")
        result = con.execute("""
            SELECT
                sale_date,
                daily_total,
                AVG(daily_total) OVER (
                    ORDER BY sale_date
                    ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
                ) as moving_avg_3day,
                AVG(daily_total) OVER (
                    ORDER BY sale_date
                    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
                ) as moving_avg_7day
            FROM daily_totals
            ORDER BY sale_date
        """).fetchdf()
        console.print(result.to_string(index=False))

        # 累計銷售額
        console.print("\n   [yellow]累計銷售額:[/yellow]")
        result = con.execute("""
            SELECT
                sale_date,
                daily_total,
                SUM(daily_total) OVER (
                    ORDER BY sale_date
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                ) as cumulative_total,
                ROW_NUMBER() OVER (ORDER BY sale_date) as day_number
            FROM daily_totals
            ORDER BY sale_date
        """).fetchdf()
        console.print(result.to_string(index=False))

        # 按類別的累計銷售
        console.print("\n   [yellow]按類別累計銷售:[/yellow]")
        result = con.execute("""
            SELECT
                category,
                sale_date,
                amount,
                SUM(amount) OVER (
                    PARTITION BY category
                    ORDER BY sale_date
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                ) as category_cumulative
            FROM daily_sales
            ORDER BY category, sale_date
        """).fetchdf()
        console.print(result.head(15).to_string(index=False))

    except Exception as e:
        console.print(f"[red]✗ 移動計算示例失敗: {e}[/red]")
        raise


def demonstrate_lead_lag_functions(con):
    """展示 LEAD 和 LAG 函數"""
    console.print("\n[bold cyan]4. LEAD 和 LAG 函數[/bold cyan]")

    try:
        # LAG - 與前一天對比
        console.print("\n   [yellow]日銷售額變化趨勢:[/yellow]")
        result = con.execute("""
            WITH daily_totals AS (
                SELECT
                    sale_date,
                    SUM(amount) as daily_total
                FROM daily_sales
                GROUP BY sale_date
            )
            SELECT
                sale_date,
                daily_total,
                LAG(daily_total, 1) OVER (ORDER BY sale_date) as prev_day,
                daily_total - LAG(daily_total, 1) OVER (ORDER BY sale_date) as day_change,
                ROUND(
                    (daily_total - LAG(daily_total, 1) OVER (ORDER BY sale_date)) /
                    NULLIF(LAG(daily_total, 1) OVER (ORDER BY sale_date), 0) * 100,
                    2
                ) as pct_change
            FROM daily_totals
            ORDER BY sale_date
        """).fetchdf()
        console.print(result.to_string(index=False))

        # LEAD - 預測下一次銷售
        console.print("\n   [yellow]客戶購買間隔分析:[/yellow]")
        result = con.execute("""
            SELECT
                sales_person,
                sale_date,
                product,
                amount,
                LEAD(sale_date, 1) OVER (
                    PARTITION BY sales_person
                    ORDER BY sale_date
                ) as next_sale_date,
                LEAD(sale_date, 1) OVER (
                    PARTITION BY sales_person
                    ORDER BY sale_date
                ) - sale_date as days_to_next_sale
            FROM daily_sales
            ORDER BY sales_person, sale_date
        """).fetchdf()
        console.print(result.head(12).to_string(index=False))

        # FIRST_VALUE 和 LAST_VALUE
        console.print("\n   [yellow]首單和尾單對比:[/yellow]")
        result = con.execute("""
            SELECT DISTINCT
                sales_person,
                FIRST_VALUE(product) OVER (
                    PARTITION BY sales_person
                    ORDER BY sale_date
                    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
                ) as first_product,
                FIRST_VALUE(amount) OVER (
                    PARTITION BY sales_person
                    ORDER BY sale_date
                    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
                ) as first_amount,
                LAST_VALUE(product) OVER (
                    PARTITION BY sales_person
                    ORDER BY sale_date
                    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
                ) as last_product,
                LAST_VALUE(amount) OVER (
                    PARTITION BY sales_person
                    ORDER BY sale_date
                    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
                ) as last_amount
            FROM daily_sales
            ORDER BY sales_person
        """).fetchdf()
        console.print(result.to_string(index=False))

    except Exception as e:
        console.print(f"[red]✗ LEAD/LAG 函數失敗: {e}[/red]")
        raise


def demonstrate_complex_analytics(con):
    """展示複雜分析查詢"""
    console.print("\n[bold cyan]5. 複雜分析查詢[/bold cyan]")

    try:
        # 同比增長分析
        console.print("\n   [yellow]周同比增長分析:[/yellow]")
        result = con.execute("""
            WITH weekly_sales AS (
                SELECT
                    DATE_TRUNC('week', sale_date) as week,
                    SUM(amount) as weekly_total
                FROM daily_sales
                GROUP BY DATE_TRUNC('week', sale_date)
            )
            SELECT
                week,
                weekly_total,
                LAG(weekly_total, 1) OVER (ORDER BY week) as prev_week,
                weekly_total - LAG(weekly_total, 1) OVER (ORDER BY week) as week_change,
                ROUND(
                    (weekly_total - LAG(weekly_total, 1) OVER (ORDER BY week)) /
                    NULLIF(LAG(weekly_total, 1) OVER (ORDER BY week), 0) * 100,
                    2
                ) as pct_change
            FROM weekly_sales
            ORDER BY week
        """).fetchdf()
        console.print(result.to_string(index=False))

        # 銷售人員績效分析
        console.print("\n   [yellow]銷售人員績效排名:[/yellow]")
        result = con.execute("""
            WITH sales_metrics AS (
                SELECT
                    sales_person,
                    COUNT(*) as order_count,
                    SUM(amount) as total_sales,
                    AVG(amount) as avg_order_value,
                    MAX(amount) as max_sale
                FROM daily_sales
                GROUP BY sales_person
            )
            SELECT
                sales_person,
                order_count,
                total_sales,
                avg_order_value,
                max_sale,
                RANK() OVER (ORDER BY total_sales DESC) as sales_rank,
                RANK() OVER (ORDER BY avg_order_value DESC) as aov_rank,
                ROUND(total_sales / SUM(total_sales) OVER () * 100, 2) as pct_of_total
            FROM sales_metrics
            ORDER BY total_sales DESC
        """).fetchdf()
        console.print(result.to_string(index=False))

        # 產品類別貢獻度分析
        console.print("\n   [yellow]產品類別貢獻度分析:[/yellow]")
        result = con.execute("""
            SELECT
                category,
                COUNT(*) as sales_count,
                SUM(amount) as total_revenue,
                AVG(amount) as avg_sale,
                ROUND(SUM(amount) / SUM(SUM(amount)) OVER () * 100, 2) as revenue_pct,
                ROUND(COUNT(*) * 1.0 / SUM(COUNT(*)) OVER () * 100, 2) as count_pct,
                RANK() OVER (ORDER BY SUM(amount) DESC) as revenue_rank
            FROM daily_sales
            GROUP BY category
            ORDER BY total_revenue DESC
        """).fetchdf()
        console.print(result.to_string(index=False))

    except Exception as e:
        console.print(f"[red]✗ 複雜分析失敗: {e}[/red]")
        raise


def demonstrate_partition_strategies(con):
    """展示分區策略"""
    console.print("\n[bold cyan]6. 分區策略[/bold cyan]")

    try:
        # 無分區 vs 有分區
        console.print("\n   [yellow]全局排名 vs 分組排名:[/yellow]")
        result = con.execute("""
            SELECT
                category,
                product,
                amount,
                -- 全局排名
                RANK() OVER (ORDER BY amount DESC) as global_rank,
                -- 分類排名
                RANK() OVER (PARTITION BY category ORDER BY amount DESC) as category_rank,
                -- 分類內百分位
                PERCENT_RANK() OVER (PARTITION BY category ORDER BY amount) as category_percentile
            FROM daily_sales
            ORDER BY category, amount DESC
        """).fetchdf()
        console.print(result.head(15).to_string(index=False))

        # 多級分區
        console.print("\n   [yellow]多級分區分析:[/yellow]")
        result = con.execute("""
            SELECT
                region,
                category,
                product,
                amount,
                -- 區域內排名
                RANK() OVER (PARTITION BY region ORDER BY amount DESC) as region_rank,
                -- 區域+類別排名
                RANK() OVER (PARTITION BY region, category ORDER BY amount DESC) as region_category_rank,
                -- 區域內累計
                SUM(amount) OVER (
                    PARTITION BY region
                    ORDER BY sale_date
                ) as region_cumulative
            FROM daily_sales
            ORDER BY region, category, amount DESC
        """).fetchdf()
        console.print(result.head(15).to_string(index=False))

    except Exception as e:
        console.print(f"[red]✗ 分區策略示例失敗: {e}[/red]")
        raise


def main():
    """主函數"""
    console.print("\n[bold magenta]═══════════════════════════════════════[/bold magenta]")
    console.print("[bold magenta]    DuckDB 分析函數示例    [/bold magenta]")
    console.print("[bold magenta]═══════════════════════════════════════[/bold magenta]")

    try:
        # 設置數據庫
        con = setup_database()

        # 1. 排名函數
        demonstrate_ranking_functions(con)

        # 2. 聚合窗口函數
        demonstrate_aggregate_windows(con)

        # 3. 移動計算
        demonstrate_moving_calculations(con)

        # 4. LEAD/LAG 函數
        demonstrate_lead_lag_functions(con)

        # 5. 複雜分析
        demonstrate_complex_analytics(con)

        # 6. 分區策略
        demonstrate_partition_strategies(con)

        # 清理
        con.close()

        console.print("\n[bold green]✓ 所有分析函數示例執行成功！[/bold green]")
        console.print("\n[yellow]DuckDB 窗口函數特性:[/yellow]")
        console.print("  - 完整的窗口函數支持")
        console.print("  - RANK, DENSE_RANK, ROW_NUMBER")
        console.print("  - LEAD, LAG, FIRST_VALUE, LAST_VALUE")
        console.print("  - 靈活的 PARTITION BY 和 ORDER BY")
        console.print("  - ROWS/RANGE 窗口框架")
        console.print("  - 高性能並行執行")

    except Exception as e:
        console.print(f"\n[bold red]✗ 執行失敗: {e}[/bold red]")
        raise


if __name__ == "__main__":
    main()

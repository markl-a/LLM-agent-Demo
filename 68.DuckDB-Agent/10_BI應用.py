"""
DuckDB-Agent 示例 10: BI 應用

展示如何使用 DuckDB 構建商業智能應用：
1. 數據倉庫建模
2. KPI 指標計算
3. 多維分析
4. 趨勢分析
5. 儀表板數據準備
6. 實時數據刷新
"""

import duckdb
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import pandas as pd
from datetime import datetime, timedelta
import json
from pathlib import Path

console = Console()


def setup_data_warehouse(con):
    """設置數據倉庫模型"""
    console.print("\n[bold cyan]1. 數據倉庫建模[/bold cyan]")

    try:
        # 創建維度表 - 產品維度
        con.execute("""
            CREATE TABLE dim_products (
                product_id INTEGER PRIMARY KEY,
                product_name VARCHAR,
                category VARCHAR,
                subcategory VARCHAR,
                brand VARCHAR,
                unit_price DECIMAL(10, 2)
            )
        """)

        con.execute("""
            INSERT INTO dim_products VALUES
            (1, 'MacBook Pro 14', '電腦', '筆記本', 'Apple', 2499.00),
            (2, 'MacBook Air 13', '電腦', '筆記本', 'Apple', 1299.00),
            (3, 'iPhone 15', '手機', '智能手機', 'Apple', 999.00),
            (4, 'iPhone 15 Pro', '手機', '智能手機', 'Apple', 1199.00),
            (5, 'iPad Air', '平板', 'iPad', 'Apple', 599.00),
            (6, 'iPad Pro', '平板', 'iPad', 'Apple', 1099.00),
            (7, 'AirPods Pro', '配件', '音頻', 'Apple', 249.00),
            (8, 'Apple Watch', '配件', '智能穿戴', 'Apple', 399.00),
            (9, 'Magic Keyboard', '配件', '輸入設備', 'Apple', 99.00),
            (10, 'Studio Display', '配件', '顯示器', 'Apple', 1599.00)
        """)

        # 創建維度表 - 客戶維度
        con.execute("""
            CREATE TABLE dim_customers (
                customer_id INTEGER PRIMARY KEY,
                customer_name VARCHAR,
                customer_type VARCHAR,
                industry VARCHAR,
                region VARCHAR,
                city VARCHAR
            )
        """)

        con.execute("""
            INSERT INTO dim_customers VALUES
            (1, '科技公司A', '企業', '科技', '華北', '北京'),
            (2, '教育機構B', '機構', '教育', '華東', '上海'),
            (3, '零售店C', '零售', '零售', '華南', '深圳'),
            (4, '企業D', '企業', '製造', '華東', '杭州'),
            (5, '創業公司E', '企業', '科技', '華南', '廣州'),
            (6, '政府機構F', '機構', '政府', '華北', '北京'),
            (7, '醫療機構G', '機構', '醫療', '華南', '深圳'),
            (8, '金融公司H', '企業', '金融', '華東', '上海')
        """)

        # 創建時間維度
        con.execute("""
            CREATE TABLE dim_time AS
            SELECT
                CAST(date AS DATE) as date,
                YEAR(date) as year,
                QUARTER(date) as quarter,
                MONTH(date) as month,
                DAY(date) as day,
                DAYOFWEEK(date) as day_of_week,
                WEEK(date) as week_of_year,
                CASE WHEN DAYOFWEEK(date) IN (6, 7) THEN true ELSE false END as is_weekend
            FROM (
                SELECT (DATE '2025-01-01' + INTERVAL (d) DAY)::DATE as date
                FROM range(0, 365) t(d)
            )
        """)

        # 創建事實表 - 銷售事實
        con.execute("""
            CREATE TABLE fact_sales (
                sale_id INTEGER PRIMARY KEY,
                date DATE,
                product_id INTEGER,
                customer_id INTEGER,
                quantity INTEGER,
                unit_price DECIMAL(10, 2),
                discount_pct DECIMAL(5, 2),
                total_amount DECIMAL(10, 2),
                sales_rep VARCHAR
            )
        """)

        # 生成示例銷售數據
        con.execute("""
            INSERT INTO fact_sales
            SELECT
                row_number() OVER () as sale_id,
                DATE '2025-01-01' + (random() * 90)::INTEGER as date,
                (random() * 10 + 1)::INTEGER as product_id,
                (random() * 8 + 1)::INTEGER as customer_id,
                (random() * 10 + 1)::INTEGER as quantity,
                p.unit_price,
                CASE
                    WHEN random() < 0.3 THEN (random() * 20)::DECIMAL(5, 2)
                    ELSE 0
                END as discount_pct,
                0 as total_amount,  -- 將在下面計算
                ['張三', '李四', '王五', '趙六'][(random() * 4)::INTEGER] as sales_rep
            FROM range(500) t
            CROSS JOIN dim_products p
            WHERE p.product_id = (random() * 10 + 1)::INTEGER
            LIMIT 500
        """)

        # 更新總金額
        con.execute("""
            UPDATE fact_sales
            SET total_amount = quantity * unit_price * (1 - discount_pct / 100)
        """)

        console.print("   ✓ 數據倉庫模型創建完成", style="green")
        console.print("   - dim_products: 產品維度")
        console.print("   - dim_customers: 客戶維度")
        console.print("   - dim_time: 時間維度")
        console.print("   - fact_sales: 銷售事實表")

    except Exception as e:
        console.print(f"[red]✗ 數據倉庫建模失敗: {e}[/red]")
        raise


def calculate_kpis(con):
    """計算 KPI 指標"""
    console.print("\n[bold cyan]2. KPI 指標計算[/bold cyan]")

    try:
        # 核心 KPI
        console.print("\n   [yellow]核心業務指標:[/yellow]")

        kpi_query = """
            WITH current_period AS (
                SELECT
                    COUNT(DISTINCT sale_id) as total_orders,
                    COUNT(DISTINCT customer_id) as unique_customers,
                    SUM(total_amount) as total_revenue,
                    AVG(total_amount) as avg_order_value,
                    SUM(quantity) as total_units_sold
                FROM fact_sales
                WHERE date >= CURRENT_DATE - INTERVAL '30 days'
            ),
            previous_period AS (
                SELECT
                    SUM(total_amount) as prev_revenue
                FROM fact_sales
                WHERE date >= CURRENT_DATE - INTERVAL '60 days'
                AND date < CURRENT_DATE - INTERVAL '30 days'
            )
            SELECT
                cp.total_orders as "訂單數",
                cp.unique_customers as "客戶數",
                ROUND(cp.total_revenue, 2) as "總收入",
                ROUND(cp.avg_order_value, 2) as "平均訂單金額",
                cp.total_units_sold as "銷售數量",
                ROUND(cp.total_revenue / cp.unique_customers, 2) as "客均價值",
                ROUND((cp.total_revenue - pp.prev_revenue) / NULLIF(pp.prev_revenue, 0) * 100, 2) as "環比增長%"
            FROM current_period cp, previous_period pp
        """

        result = con.execute(kpi_query).fetchdf()
        console.print(result.to_string(index=False))

        # 產品 KPI
        console.print("\n   [yellow]產品績效指標:[/yellow]")

        product_kpi = """
            SELECT
                p.category as "產品類別",
                COUNT(f.sale_id) as "銷售筆數",
                SUM(f.quantity) as "銷售數量",
                ROUND(SUM(f.total_amount), 2) as "銷售額",
                ROUND(AVG(f.total_amount), 2) as "平均單價",
                ROUND(SUM(f.total_amount) / SUM(SUM(f.total_amount)) OVER () * 100, 2) as "收入佔比%"
            FROM fact_sales f
            JOIN dim_products p ON f.product_id = p.product_id
            GROUP BY p.category
            ORDER BY SUM(f.total_amount) DESC
        """

        result = con.execute(product_kpi).fetchdf()
        console.print(result.to_string(index=False))

        # 客戶 KPI
        console.print("\n   [yellow]客戶分析指標:[/yellow]")

        customer_kpi = """
            SELECT
                c.customer_type as "客戶類型",
                COUNT(DISTINCT f.customer_id) as "客戶數",
                COUNT(f.sale_id) as "訂單數",
                ROUND(AVG(f.total_amount), 2) as "平均訂單金額",
                ROUND(SUM(f.total_amount), 2) as "總消費額",
                ROUND(SUM(f.total_amount) / COUNT(DISTINCT f.customer_id), 2) as "客戶生命週期價值"
            FROM fact_sales f
            JOIN dim_customers c ON f.customer_id = c.customer_id
            GROUP BY c.customer_type
            ORDER BY SUM(f.total_amount) DESC
        """

        result = con.execute(customer_kpi).fetchdf()
        console.print(result.to_string(index=False))

    except Exception as e:
        console.print(f"[red]✗ KPI 計算失敗: {e}[/red]")
        raise


def multidimensional_analysis(con):
    """多維分析"""
    console.print("\n[bold cyan]3. 多維分析（OLAP）[/bold cyan]")

    try:
        # ROLLUP - 層級聚合
        console.print("\n   [yellow]ROLLUP 分析（區域→城市→總計）:[/yellow]")

        rollup_query = """
            SELECT
                c.region as "區域",
                c.city as "城市",
                COUNT(f.sale_id) as "訂單數",
                ROUND(SUM(f.total_amount), 2) as "銷售額"
            FROM fact_sales f
            JOIN dim_customers c ON f.customer_id = c.customer_id
            GROUP BY ROLLUP(c.region, c.city)
            ORDER BY c.region NULLS LAST, c.city NULLS LAST
        """

        result = con.execute(rollup_query).fetchdf()
        console.print(result.head(15).to_string(index=False))

        # CUBE - 多維度聚合
        console.print("\n   [yellow]CUBE 分析（所有維度組合）:[/yellow]")

        cube_query = """
            SELECT
                p.category as "類別",
                c.region as "區域",
                COUNT(f.sale_id) as "訂單數",
                ROUND(SUM(f.total_amount), 2) as "銷售額"
            FROM fact_sales f
            JOIN dim_products p ON f.product_id = p.product_id
            JOIN dim_customers c ON f.customer_id = c.customer_id
            GROUP BY CUBE(p.category, c.region)
            ORDER BY p.category NULLS LAST, c.region NULLS LAST
        """

        result = con.execute(cube_query).fetchdf()
        console.print(result.head(20).to_string(index=False))

        # 同環比分析
        console.print("\n   [yellow]同環比分析:[/yellow]")

        yoy_query = """
            WITH monthly_sales AS (
                SELECT
                    DATE_TRUNC('month', date) as month,
                    SUM(total_amount) as revenue
                FROM fact_sales
                GROUP BY month
            )
            SELECT
                month as "月份",
                ROUND(revenue, 2) as "當月收入",
                ROUND(LAG(revenue, 1) OVER (ORDER BY month), 2) as "上月收入",
                ROUND((revenue - LAG(revenue, 1) OVER (ORDER BY month)) /
                      NULLIF(LAG(revenue, 1) OVER (ORDER BY month), 0) * 100, 2) as "環比%"
            FROM monthly_sales
            ORDER BY month
        """

        result = con.execute(yoy_query).fetchdf()
        console.print(result.to_string(index=False))

    except Exception as e:
        console.print(f"[red]✗ 多維分析失敗: {e}[/red]")
        raise


def trend_analysis(con):
    """趨勢分析"""
    console.print("\n[bold cyan]4. 趨勢分析[/bold cyan]")

    try:
        # 時間序列趨勢
        console.print("\n   [yellow]日銷售趨勢（7日移動平均）:[/yellow]")

        trend_query = """
            WITH daily_sales AS (
                SELECT
                    date,
                    SUM(total_amount) as daily_revenue
                FROM fact_sales
                GROUP BY date
            )
            SELECT
                date as "日期",
                ROUND(daily_revenue, 2) as "當日收入",
                ROUND(AVG(daily_revenue) OVER (
                    ORDER BY date
                    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
                ), 2) as "7日均值",
                ROUND(daily_revenue - AVG(daily_revenue) OVER (
                    ORDER BY date
                    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
                ), 2) as "與均值差"
            FROM daily_sales
            ORDER BY date DESC
            LIMIT 15
        """

        result = con.execute(trend_query).fetchdf()
        console.print(result.to_string(index=False))

        # 週期性分析
        console.print("\n   [yellow]星期銷售模式:[/yellow]")

        weekday_pattern = """
            SELECT
                t.day_of_week as "星期",
                CASE t.day_of_week
                    WHEN 1 THEN '週一'
                    WHEN 2 THEN '週二'
                    WHEN 3 THEN '週三'
                    WHEN 4 THEN '週四'
                    WHEN 5 THEN '週五'
                    WHEN 6 THEN '週六'
                    WHEN 7 THEN '週日'
                END as "星期名稱",
                COUNT(f.sale_id) as "訂單數",
                ROUND(AVG(f.total_amount), 2) as "平均訂單額",
                ROUND(SUM(f.total_amount), 2) as "總銷售額"
            FROM fact_sales f
            JOIN dim_time t ON f.date = t.date
            GROUP BY t.day_of_week
            ORDER BY t.day_of_week
        """

        result = con.execute(weekday_pattern).fetchdf()
        console.print(result.to_string(index=False))

        # 增長趨勢
        console.print("\n   [yellow]累計增長趨勢:[/yellow]")

        growth_trend = """
            WITH daily_sales AS (
                SELECT
                    date,
                    SUM(total_amount) as revenue
                FROM fact_sales
                GROUP BY date
            )
            SELECT
                date as "日期",
                ROUND(revenue, 2) as "日收入",
                ROUND(SUM(revenue) OVER (ORDER BY date), 2) as "累計收入",
                ROW_NUMBER() OVER (ORDER BY date) as "天數"
            FROM daily_sales
            ORDER BY date DESC
            LIMIT 10
        """

        result = con.execute(growth_trend).fetchdf()
        console.print(result.to_string(index=False))

    except Exception as e:
        console.print(f"[red]✗ 趨勢分析失敗: {e}[/red]")
        raise


def dashboard_data_preparation(con):
    """儀表板數據準備"""
    console.print("\n[bold cyan]5. 儀表板數據準備[/bold cyan]")

    try:
        # 創建彙總視圖
        console.print("\n   [yellow]創建彙總視圖:[/yellow]")

        con.execute("""
            CREATE OR REPLACE VIEW v_sales_summary AS
            SELECT
                f.date,
                p.category,
                p.product_name,
                c.customer_name,
                c.region,
                f.quantity,
                f.total_amount,
                DATE_TRUNC('month', f.date) as month,
                DATE_TRUNC('week', f.date) as week
            FROM fact_sales f
            JOIN dim_products p ON f.product_id = p.product_id
            JOIN dim_customers c ON f.customer_id = c.customer_id
        """)

        console.print("   ✓ 創建 v_sales_summary 視圖", style="green")

        # 導出儀表板數據
        console.print("\n   [yellow]導出儀表板數據集:[/yellow]")

        # 1. 總覽卡片數據
        overview_data = con.execute("""
            SELECT
                COUNT(DISTINCT date) as days_in_period,
                COUNT(*) as total_orders,
                COUNT(DISTINCT customer_name) as unique_customers,
                SUM(total_amount) as total_revenue,
                AVG(total_amount) as avg_order_value
            FROM v_sales_summary
        """).fetchdf()

        # 2. 趨勢圖數據
        trend_data = con.execute("""
            SELECT
                date,
                SUM(total_amount) as revenue
            FROM v_sales_summary
            GROUP BY date
            ORDER BY date
        """).fetchdf()

        # 3. 類別分布數據
        category_data = con.execute("""
            SELECT
                category,
                SUM(total_amount) as revenue,
                COUNT(*) as order_count
            FROM v_sales_summary
            GROUP BY category
            ORDER BY revenue DESC
        """).fetchdf()

        # 4. 區域分布數據
        region_data = con.execute("""
            SELECT
                region,
                SUM(total_amount) as revenue,
                COUNT(DISTINCT customer_name) as customers
            FROM v_sales_summary
            GROUP BY region
            ORDER BY revenue DESC
        """).fetchdf()

        # 5. 熱銷產品
        top_products = con.execute("""
            SELECT
                product_name,
                SUM(quantity) as units_sold,
                SUM(total_amount) as revenue
            FROM v_sales_summary
            GROUP BY product_name
            ORDER BY revenue DESC
            LIMIT 10
        """).fetchdf()

        # 導出為 JSON
        dashboard_data = {
            'generated_at': datetime.now().isoformat(),
            'overview': overview_data.to_dict(orient='records')[0],
            'trend': trend_data.to_dict(orient='records'),
            'by_category': category_data.to_dict(orient='records'),
            'by_region': region_data.to_dict(orient='records'),
            'top_products': top_products.to_dict(orient='records')
        }

        # 保存到文件
        output_dir = Path("./dashboard_data")
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / "dashboard_data.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(dashboard_data, f, ensure_ascii=False, indent=2, default=str)

        console.print(f"\n   ✓ 儀表板數據已導出: {output_file}", style="green")

        # 顯示總覽數據
        console.print("\n   [yellow]總覽數據:[/yellow]")
        for key, value in dashboard_data['overview'].items():
            console.print(f"   {key}: {value}")

    except Exception as e:
        console.print(f"[red]✗ 儀表板數據準備失敗: {e}[/red]")
        raise


def realtime_refresh_simulation(con):
    """實時數據刷新模擬"""
    console.print("\n[bold cyan]6. 實時數據刷新（模擬）[/bold cyan]")

    try:
        console.print("\n   [yellow]數據刷新策略:[/yellow]")

        refresh_strategies = """
1. 增量更新策略
   - 只查詢最新數據
   - 使用時間戳過濾
   - 定期聚合到彙總表

2. 物化視圖
   - 創建預計算的聚合表
   - 定期刷新
   - 提高查詢性能

3. 實時指標
   - 使用視圖動態計算
   - 適合低延遲需求
   - 計算成本較高

示例代碼:

-- 增量更新
CREATE TABLE sales_summary_daily AS
SELECT
    date,
    category,
    SUM(total_amount) as revenue
FROM fact_sales
WHERE date = CURRENT_DATE
GROUP BY date, category;

-- 追加新數據
INSERT INTO sales_summary_daily
SELECT
    date,
    category,
    SUM(total_amount) as revenue
FROM fact_sales
WHERE date = CURRENT_DATE
AND sale_id > (SELECT MAX(last_processed_id) FROM etl_log)
GROUP BY date, category;

-- 實時視圖
CREATE OR REPLACE VIEW v_realtime_kpi AS
SELECT
    COUNT(*) as orders_today,
    SUM(total_amount) as revenue_today
FROM fact_sales
WHERE date = CURRENT_DATE;
"""

        console.print(Panel(refresh_strategies, title="數據刷新策略", border_style="cyan"))

        # 模擬增量更新
        console.print("\n   [yellow]模擬增量數據插入:[/yellow]")

        # 插入新數據
        new_sales = con.execute("""
            INSERT INTO fact_sales
            SELECT
                (SELECT MAX(sale_id) FROM fact_sales) + row_number() OVER () as sale_id,
                CURRENT_DATE as date,
                (random() * 10 + 1)::INTEGER as product_id,
                (random() * 8 + 1)::INTEGER as customer_id,
                (random() * 5 + 1)::INTEGER as quantity,
                100.00 as unit_price,
                0 as discount_pct,
                (random() * 5 + 1)::INTEGER * 100 as total_amount,
                '張三' as sales_rep
            FROM range(5)
            RETURNING sale_id
        """).fetchall()

        console.print(f"   ✓ 插入 {len(new_sales)} 條新記錄", style="green")

        # 查詢今日數據
        today_summary = con.execute("""
            SELECT
                COUNT(*) as "今日訂單",
                ROUND(SUM(total_amount), 2) as "今日收入",
                ROUND(AVG(total_amount), 2) as "平均訂單額"
            FROM fact_sales
            WHERE date = CURRENT_DATE
        """).fetchdf()

        console.print("\n   [yellow]今日實時數據:[/yellow]")
        console.print(today_summary.to_string(index=False))

    except Exception as e:
        console.print(f"[red]✗ 實時刷新模擬失敗: {e}[/red]")
        raise


def main():
    """主函數"""
    console.print("\n[bold magenta]═══════════════════════════════════════[/bold magenta]")
    console.print("[bold magenta]   DuckDB BI 應用示例   [/bold magenta]")
    console.print("[bold magenta]═══════════════════════════════════════[/bold magenta]")

    try:
        # 創建數據庫
        con = duckdb.connect(':memory:')

        # 1. 數據倉庫建模
        setup_data_warehouse(con)

        # 2. KPI 計算
        calculate_kpis(con)

        # 3. 多維分析
        multidimensional_analysis(con)

        # 4. 趨勢分析
        trend_analysis(con)

        # 5. 儀表板數據準備
        dashboard_data_preparation(con)

        # 6. 實時刷新
        realtime_refresh_simulation(con)

        # 清理
        con.close()

        console.print("\n[bold green]✓ BI 應用示例執行完成！[/bold green]")

        console.print("\n[yellow]DuckDB 在 BI 應用中的優勢:[/yellow]")
        console.print("  - 快速的 OLAP 查詢性能")
        console.print("  - 完整的 SQL 分析功能")
        console.print("  - 支持複雜的多維分析")
        console.print("  - 嵌入式架構，易於集成")
        console.print("  - 零配置，開箱即用")
        console.print("  - 支持大數據集（GB 級）")

        console.print("\n[yellow]適用場景:[/yellow]")
        console.print("  - 企業內部 BI 儀表板")
        console.print("  - 數據探索和分析工具")
        console.print("  - 嵌入式分析應用")
        console.print("  - 自助式商業智能")
        console.print("  - 報表生成系統")

    except Exception as e:
        console.print(f"\n[bold red]✗ 執行失敗: {e}[/bold red]")
        raise


if __name__ == "__main__":
    main()

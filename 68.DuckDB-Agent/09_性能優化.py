"""
DuckDB-Agent 示例 09: 性能優化

展示 DuckDB 的性能優化技巧：
1. 查詢優化基礎
2. 索引和分區策略
3. 並行處理配置
4. 內存管理
5. 查詢計劃分析
6. 最佳實踐
"""

import duckdb
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
import time
import pandas as pd
from pathlib import Path

console = Console()


def setup_test_database():
    """設置測試數據庫"""
    try:
        console.print("\n[bold cyan]準備性能測試數據[/bold cyan]")

        con = duckdb.connect(':memory:')

        # 創建大型測試表
        con.execute("""
            CREATE TABLE large_sales AS
            SELECT
                (random() * 1000000)::INTEGER as sale_id,
                (random() * 100)::INTEGER as product_id,
                (random() * 1000)::INTEGER as customer_id,
                (random() * 1000)::DECIMAL(10, 2) as amount,
                DATE '2024-01-01' + (random() * 365)::INTEGER as sale_date,
                ['電子', '服裝', '食品', '家居', '運動'][
                    (random() * 5)::INTEGER
                ] as category,
                ['華北', '華東', '華南', '華中', '西南'][
                    (random() * 5)::INTEGER
                ] as region
            FROM range(1000000)
        """)

        count = con.execute("SELECT COUNT(*) FROM large_sales").fetchone()[0]
        console.print(f"   ✓ 創建測試表，包含 {count:,} 條記錄", style="green")

        return con

    except Exception as e:
        console.print(f"[red]✗ 設置測試數據失敗: {e}[/red]")
        raise


def measure_query_time(con, query, description):
    """測量查詢執行時間"""
    console.print(f"\n   [yellow]{description}[/yellow]")

    start = time.time()
    result = con.execute(query).fetchall()
    elapsed = time.time() - start

    console.print(f"   執行時間: {elapsed:.4f} 秒", style="cyan")
    console.print(f"   結果行數: {len(result):,}", style="dim")

    return elapsed, result


def demonstrate_query_optimization(con):
    """展示查詢優化"""
    console.print("\n[bold cyan]1. 查詢優化技巧[/bold cyan]")

    try:
        # 優化前：使用 SELECT *
        console.print("\n   [yellow]❌ 低效查詢（SELECT *）:[/yellow]")
        bad_query = """
            SELECT *
            FROM large_sales
            WHERE amount > 500
            LIMIT 1000
        """
        time_bad, _ = measure_query_time(con, bad_query, "查詢所有列")

        # 優化後：只選擇需要的列
        console.print("\n   [yellow]✓ 優化查詢（指定列）:[/yellow]")
        good_query = """
            SELECT sale_id, amount, sale_date
            FROM large_sales
            WHERE amount > 500
            LIMIT 1000
        """
        time_good, _ = measure_query_time(con, good_query, "只查詢需要的列")

        speedup = time_bad / time_good if time_good > 0 else 0
        console.print(f"\n   ⚡ 性能提升: {speedup:.2f}x", style="bold green")

        # 使用過濾條件優化
        console.print("\n   [yellow]使用索引友好的過濾條件:[/yellow]")

        # 範圍查詢
        efficient_filter = """
            SELECT category, SUM(amount) as total
            FROM large_sales
            WHERE sale_date BETWEEN '2024-06-01' AND '2024-06-30'
            AND amount > 100
            GROUP BY category
        """
        measure_query_time(con, efficient_filter, "範圍查詢 + 數值過濾")

    except Exception as e:
        console.print(f"[red]✗ 查詢優化示例失敗: {e}[/red]")


def demonstrate_explain_analyze(con):
    """展示查詢計劃分析"""
    console.print("\n[bold cyan]2. 查詢計劃分析（EXPLAIN）[/bold cyan]")

    try:
        query = """
            SELECT
                category,
                region,
                COUNT(*) as sales_count,
                SUM(amount) as total_revenue,
                AVG(amount) as avg_amount
            FROM large_sales
            WHERE sale_date >= '2024-06-01'
            AND amount > 100
            GROUP BY category, region
            ORDER BY total_revenue DESC
        """

        # EXPLAIN - 查看查詢計劃
        console.print("\n   [yellow]EXPLAIN 查詢計劃:[/yellow]")
        explain_result = con.execute(f"EXPLAIN {query}").fetchall()

        for row in explain_result[:10]:  # 顯示前 10 行
            console.print(f"   {row[1]}", style="dim")

        # EXPLAIN ANALYZE - 查看實際執行統計
        console.print("\n   [yellow]EXPLAIN ANALYZE（實際執行）:[/yellow]")
        analyze_result = con.execute(f"EXPLAIN ANALYZE {query}").fetchall()

        for row in analyze_result[:15]:  # 顯示前 15 行
            console.print(f"   {row[1]}", style="cyan")

    except Exception as e:
        console.print(f"[red]✗ 查詢計劃分析失敗: {e}[/red]")


def demonstrate_parallel_processing(con):
    """展示並行處理"""
    console.print("\n[bold cyan]3. 並行處理配置[/bold cyan]")

    try:
        # 查看當前線程數
        threads = con.execute("SELECT current_setting('threads')").fetchone()[0]
        console.print(f"\n   當前線程數: {threads}", style="yellow")

        # 複雜聚合查詢
        complex_query = """
            SELECT
                region,
                category,
                DATE_TRUNC('month', sale_date) as month,
                COUNT(*) as order_count,
                SUM(amount) as revenue,
                AVG(amount) as avg_order_value,
                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY amount) as median_amount
            FROM large_sales
            GROUP BY region, category, DATE_TRUNC('month', sale_date)
            ORDER BY revenue DESC
        """

        # 單線程
        console.print("\n   [yellow]單線程執行:[/yellow]")
        con.execute("SET threads TO 1")
        time_single, _ = measure_query_time(con, complex_query, "使用 1 個線程")

        # 多線程
        console.print("\n   [yellow]多線程執行:[/yellow]")
        con.execute("SET threads TO 4")
        time_multi, _ = measure_query_time(con, complex_query, "使用 4 個線程")

        speedup = time_single / time_multi if time_multi > 0 else 0
        console.print(f"\n   ⚡ 並行加速: {speedup:.2f}x", style="bold green")

        # 恢復默認設置
        con.execute("RESET threads")

    except Exception as e:
        console.print(f"[red]✗ 並行處理示例失敗: {e}[/red]")


def demonstrate_memory_management(con):
    """展示內存管理"""
    console.print("\n[bold cyan]4. 內存管理[/bold cyan]")

    try:
        # 查看當前內存設置
        memory_limit = con.execute("SELECT current_setting('memory_limit')").fetchone()[0]
        console.print(f"\n   當前內存限制: {memory_limit}", style="yellow")

        # 查看內存使用情況
        console.print("\n   [yellow]內存使用統計:[/yellow]")
        memory_info = con.execute("""
            SELECT
                tag,
                size,
                count
            FROM duckdb_memory()
            ORDER BY size DESC
            LIMIT 10
        """).fetchdf()

        if len(memory_info) > 0:
            console.print(memory_info.to_string(index=False))

        # 設置內存限制
        console.print("\n   [yellow]設置內存限制:[/yellow]")
        console.print("""
        -- 設置內存限制為 1GB
        SET memory_limit = '1GB';

        -- 設置為系統內存的 80%
        SET memory_limit = '80%';

        -- 臨時表使用限制
        SET temp_directory = '/path/to/temp';
        """)

        # 溢出到磁盤
        console.print("\n   [yellow]大數據集處理（溢出到磁盤）:[/yellow]")
        console.print("""
        -- DuckDB 自動將超出內存的數據溢出到磁盤
        -- 無需額外配置，透明處理

        SELECT *
        FROM large_table
        ORDER BY column  -- 如果結果集太大，自動使用磁盤
        """)

    except Exception as e:
        console.print(f"[red]✗ 內存管理示例失敗: {e}[/red]")


def demonstrate_indexing_strategies(con):
    """展示索引策略"""
    console.print("\n[bold cyan]5. 索引和分區策略[/bold cyan]")

    try:
        # DuckDB 自動創建統計信息
        console.print("\n   [yellow]自動統計信息:[/yellow]")
        console.print("""
        DuckDB 自動維護列統計信息，用於查詢優化：
        - Min/Max 值
        - NULL 值數量
        - 唯一值數量（估計）
        - 數據分布直方圖

        無需手動創建索引！
        """)

        # 分區表
        console.print("\n   [yellow]創建分區表:[/yellow]")
        partition_example = """
        -- 按日期分區
        CREATE TABLE sales_partitioned AS
        SELECT *
        FROM large_sales
        PARTITION BY (DATE_TRUNC('month', sale_date))
        """
        console.print(Syntax(partition_example, "sql", theme="monokai"))

        # 列順序優化
        console.print("\n   [yellow]列順序優化建議:[/yellow]")
        console.print("""
        1. 將常用於過濾的列放在前面
        2. 將低基數列（少量唯一值）放在前面
        3. 按數據訪問模式組織列順序

        示例:
        CREATE TABLE optimized_sales (
            sale_date DATE,        -- 常用過濾條件
            region VARCHAR,        -- 低基數
            category VARCHAR,      -- 低基數
            amount DECIMAL,        -- 數值列
            sale_id INTEGER        -- 高基數，較少使用
        )
        """)

    except Exception as e:
        console.print(f"[red]✗ 索引策略示例失敗: {e}[/red]")


def demonstrate_data_format_optimization(con):
    """展示數據格式優化"""
    console.print("\n[bold cyan]6. 數據格式優化[/bold cyan]")

    try:
        data_dir = Path("./data")
        data_dir.mkdir(parents=True, exist_ok=True)

        # 導出為不同格式
        console.print("\n   [yellow]導出為不同格式並比較:[/yellow]")

        # CSV
        csv_path = data_dir / "test_data.csv"
        start = time.time()
        con.execute(f"""
            COPY (SELECT * FROM large_sales LIMIT 100000)
            TO '{csv_path}' (FORMAT CSV)
        """)
        csv_time = time.time() - start
        csv_size = csv_path.stat().st_size / (1024 * 1024)

        # Parquet
        parquet_path = data_dir / "test_data.parquet"
        start = time.time()
        con.execute(f"""
            COPY (SELECT * FROM large_sales LIMIT 100000)
            TO '{parquet_path}' (FORMAT PARQUET)
        """)
        parquet_time = time.time() - start
        parquet_size = parquet_path.stat().st_size / (1024 * 1024)

        # 比較結果
        table = Table(title="格式對比", show_header=True, header_style="bold magenta")
        table.add_column("格式", style="cyan")
        table.add_column("寫入時間", style="yellow")
        table.add_column("文件大小", style="green")
        table.add_column("壓縮率", style="blue")

        table.add_row(
            "CSV",
            f"{csv_time:.3f}s",
            f"{csv_size:.2f}MB",
            "1.0x"
        )
        table.add_row(
            "Parquet",
            f"{parquet_time:.3f}s",
            f"{parquet_size:.2f}MB",
            f"{csv_size/parquet_size:.2f}x"
        )

        console.print(table)

        # 讀取性能對比
        console.print("\n   [yellow]讀取性能對比:[/yellow]")

        # 讀取 CSV
        start = time.time()
        con.execute(f"SELECT COUNT(*) FROM '{csv_path}'").fetchone()
        csv_read_time = time.time() - start

        # 讀取 Parquet
        start = time.time()
        con.execute(f"SELECT COUNT(*) FROM '{parquet_path}'").fetchone()
        parquet_read_time = time.time() - start

        console.print(f"   CSV 讀取: {csv_read_time:.4f}s", style="yellow")
        console.print(f"   Parquet 讀取: {parquet_read_time:.4f}s", style="green")
        console.print(f"   加速: {csv_read_time/parquet_read_time:.2f}x", style="bold green")

    except Exception as e:
        console.print(f"[red]✗ 數據格式優化失敗: {e}[/red]")


def demonstrate_best_practices(con):
    """展示最佳實踐"""
    console.print("\n[bold cyan]7. 性能優化最佳實踐[/bold cyan]")

    best_practices = """
1. 查詢優化
   ✓ 只選擇需要的列，避免 SELECT *
   ✓ 使用 WHERE 過濾盡早減少數據量
   ✓ 使用 LIMIT 限制結果集大小
   ✓ 合理使用 GROUP BY 和聚合函數

2. 數據格式
   ✓ 優先使用 Parquet 格式（列式存儲）
   ✓ 啟用壓縮（Parquet 默認使用 Snappy）
   ✓ 避免過度嵌套的結構

3. 並行處理
   ✓ 利用多線程處理大型查詢
   ✓ 合理設置 threads 參數
   ✓ 批量處理優於逐條處理

4. 內存管理
   ✓ 根據數據集大小設置適當的 memory_limit
   ✓ 使用流式處理大型結果集
   ✓ 定期清理臨時表

5. 連接和子查詢
   ✓ 使用 JOIN 而非子查詢（在可能的情況下）
   ✓ 使用 CTE 提高可讀性和重用性
   ✓ 小表在 JOIN 的右側

6. 窗口函數
   ✓ 合理使用 PARTITION BY 減少計算量
   ✓ 窗口函數優於自連接
   ✓ 注意窗口框架的定義（ROWS vs RANGE）

7. 數據導入
   ✓ 批量導入優於逐條插入
   ✓ 使用 COPY 命令導入大量數據
   ✓ 考慮使用事務減少開銷

8. 查詢計劃
   ✓ 使用 EXPLAIN ANALYZE 分析慢查詢
   ✓ 檢查是否有全表掃描
   ✓ 驗證過濾條件是否生效

示例代碼:

-- 優化前
SELECT * FROM large_table WHERE YEAR(date_column) = 2024;

-- 優化後（使用範圍查詢）
SELECT id, name, value
FROM large_table
WHERE date_column >= '2024-01-01'
AND date_column < '2025-01-01';

-- 批量插入
INSERT INTO table_name
SELECT * FROM source_table;  -- 優於逐條 INSERT

-- 使用 CTE 提高可讀性
WITH monthly_sales AS (
    SELECT
        DATE_TRUNC('month', sale_date) as month,
        SUM(amount) as total
    FROM sales
    GROUP BY month
)
SELECT * FROM monthly_sales WHERE total > 10000;
"""

    console.print(Panel(best_practices, title="性能優化最佳實踐", border_style="green"))


def main():
    """主函數"""
    console.print("\n[bold magenta]═══════════════════════════════════════[/bold magenta]")
    console.print("[bold magenta]    DuckDB 性能優化示例    [/bold magenta]")
    console.print("[bold magenta]═══════════════════════════════════════[/bold magenta]")

    try:
        # 設置測試數據庫
        con = setup_test_database()

        # 1. 查詢優化
        demonstrate_query_optimization(con)

        # 2. 查詢計劃分析
        demonstrate_explain_analyze(con)

        # 3. 並行處理
        demonstrate_parallel_processing(con)

        # 4. 內存管理
        demonstrate_memory_management(con)

        # 5. 索引策略
        demonstrate_indexing_strategies(con)

        # 6. 數據格式優化
        demonstrate_data_format_optimization(con)

        # 7. 最佳實踐
        demonstrate_best_practices(con)

        # 清理
        con.close()

        console.print("\n[bold green]✓ 所有性能優化示例執行完成！[/bold green]")

        console.print("\n[yellow]關鍵要點:[/yellow]")
        console.print("  - DuckDB 自動優化大部分查詢")
        console.print("  - 使用 Parquet 格式獲得最佳性能")
        console.print("  - 合理利用並行處理能力")
        console.print("  - 使用 EXPLAIN ANALYZE 診斷性能問題")
        console.print("  - 只選擇需要的列和行")
        console.print("  - 遵循最佳實踐獲得最佳性能")

    except Exception as e:
        console.print(f"\n[bold red]✗ 執行失敗: {e}[/bold red]")
        raise


if __name__ == "__main__":
    main()

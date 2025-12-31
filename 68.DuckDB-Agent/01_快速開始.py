"""
DuckDB-Agent 示例 01: 快速開始

展示 DuckDB 的基礎操作：
1. 創建數據庫連接（內存和持久化）
2. 執行基本 SQL 查詢
3. 創建表和插入數據
4. 數據類型和約束
5. 事務處理
"""

import duckdb
from pathlib import Path
from rich import print as rprint
from rich.console import Console
from rich.table import Table

console = Console()


def create_in_memory_database():
    """創建內存數據庫連接"""
    try:
        console.print("\n[bold cyan]1. 創建內存數據庫[/bold cyan]")

        # 創建內存數據庫
        con = duckdb.connect(':memory:')

        # 執行簡單查詢
        result = con.execute("SELECT 'Hello DuckDB!' as message").fetchone()
        console.print(f"   查詢結果: {result[0]}", style="green")

        # 獲取版本信息
        version = con.execute("SELECT version()").fetchone()[0]
        console.print(f"   DuckDB 版本: {version}", style="yellow")

        return con

    except Exception as e:
        console.print(f"[red]✗ 創建內存數據庫失敗: {e}[/red]")
        raise


def create_persistent_database():
    """創建持久化數據庫"""
    try:
        console.print("\n[bold cyan]2. 創建持久化數據庫[/bold cyan]")

        # 創建數據目錄
        db_path = Path("./data/my_database.duckdb")
        db_path.parent.mkdir(parents=True, exist_ok=True)

        # 連接到持久化數據庫
        con = duckdb.connect(str(db_path))
        console.print(f"   數據庫文件: {db_path.absolute()}", style="green")

        # 檢查數據庫大小
        if db_path.exists():
            size_mb = db_path.stat().st_size / (1024 * 1024)
            console.print(f"   數據庫大小: {size_mb:.2f} MB", style="yellow")

        return con

    except Exception as e:
        console.print(f"[red]✗ 創建持久化數據庫失敗: {e}[/red]")
        raise


def create_and_populate_table(con):
    """創建表並插入數據"""
    try:
        console.print("\n[bold cyan]3. 創建表並插入數據[/bold cyan]")

        # 創建員工表
        con.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY,
                name VARCHAR NOT NULL,
                department VARCHAR,
                salary DECIMAL(10, 2),
                hire_date DATE,
                is_active BOOLEAN DEFAULT true
            )
        """)
        console.print("   ✓ 創建 employees 表", style="green")

        # 插入示例數據
        con.execute("""
            INSERT INTO employees VALUES
            (1, '張三', '工程部', 75000.00, '2022-01-15', true),
            (2, '李四', '市場部', 65000.00, '2022-03-20', true),
            (3, '王五', '工程部', 80000.00, '2021-11-10', true),
            (4, '趙六', '人力資源', 60000.00, '2023-02-01', true),
            (5, '孫七', '工程部', 85000.00, '2021-08-15', false)
        """)
        console.print("   ✓ 插入 5 條記錄", style="green")

        # 查詢數據
        result = con.execute("SELECT COUNT(*) FROM employees").fetchone()
        console.print(f"   當前記錄數: {result[0]}", style="yellow")

    except Exception as e:
        console.print(f"[red]✗ 創建表失敗: {e}[/red]")
        raise


def demonstrate_data_types(con):
    """展示 DuckDB 支持的數據類型"""
    try:
        console.print("\n[bold cyan]4. 數據類型示例[/bold cyan]")

        # 創建包含多種數據類型的表
        con.execute("""
            CREATE TABLE IF NOT EXISTS data_types_demo (
                -- 數值類型
                int_col INTEGER,
                bigint_col BIGINT,
                float_col FLOAT,
                double_col DOUBLE,
                decimal_col DECIMAL(18, 4),

                -- 字符串類型
                varchar_col VARCHAR,
                text_col TEXT,

                -- 時間類型
                date_col DATE,
                time_col TIME,
                timestamp_col TIMESTAMP,

                -- 布爾類型
                bool_col BOOLEAN,

                -- 複雜類型
                list_col INTEGER[],
                struct_col STRUCT(a INTEGER, b VARCHAR),
                json_col JSON
            )
        """)

        # 插入示例數據
        con.execute("""
            INSERT INTO data_types_demo VALUES (
                42,                                    -- INTEGER
                9223372036854775807,                   -- BIGINT
                3.14,                                  -- FLOAT
                2.718281828,                           -- DOUBLE
                12345.6789,                            -- DECIMAL
                'Hello',                               -- VARCHAR
                'DuckDB 支持中文',                      -- TEXT
                '2025-12-31',                          -- DATE
                '14:30:00',                            -- TIME
                '2025-12-31 14:30:00',                 -- TIMESTAMP
                true,                                  -- BOOLEAN
                [1, 2, 3, 4, 5],                       -- LIST
                {'a': 100, 'b': 'test'},               -- STRUCT
                '{"key": "value", "number": 123}'      -- JSON
            )
        """)

        console.print("   ✓ 支持的數據類型:", style="green")
        console.print("     - 數值: INTEGER, BIGINT, FLOAT, DOUBLE, DECIMAL")
        console.print("     - 字符串: VARCHAR, TEXT")
        console.print("     - 時間: DATE, TIME, TIMESTAMP")
        console.print("     - 布爾: BOOLEAN")
        console.print("     - 複雜: LIST, STRUCT, JSON, MAP")

    except Exception as e:
        console.print(f"[red]✗ 數據類型示例失敗: {e}[/red]")
        raise


def demonstrate_transactions(con):
    """展示事務處理"""
    try:
        console.print("\n[bold cyan]5. 事務處理[/bold cyan]")

        # 開始事務
        con.begin()
        console.print("   ✓ 開始事務", style="green")

        # 執行操作
        con.execute("""
            INSERT INTO employees VALUES
            (6, '周八', '財務部', 70000.00, '2023-05-10', true)
        """)
        console.print("   ✓ 插入新記錄", style="green")

        # 提交事務
        con.commit()
        console.print("   ✓ 提交事務", style="green")

        # 演示回滾
        con.begin()
        con.execute("""
            INSERT INTO employees VALUES
            (7, '吳九', '行政部', 55000.00, '2023-06-15', true)
        """)
        console.print("   ✓ 插入臨時記錄（將被回滾）", style="yellow")

        # 回滾事務
        con.rollback()
        console.print("   ✓ 回滾事務", style="green")

        # 驗證結果
        count = con.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
        console.print(f"   最終記錄數: {count}", style="yellow")

    except Exception as e:
        console.print(f"[red]✗ 事務處理失敗: {e}[/red]")
        con.rollback()
        raise


def display_query_results(con):
    """顯示查詢結果"""
    try:
        console.print("\n[bold cyan]6. 查詢結果展示[/bold cyan]")

        # 執行查詢
        result = con.execute("""
            SELECT
                name,
                department,
                salary,
                hire_date,
                CASE WHEN is_active THEN '在職' ELSE '離職' END as status
            FROM employees
            ORDER BY salary DESC
        """).fetchall()

        # 創建表格
        table = Table(title="員工信息", show_header=True, header_style="bold magenta")
        table.add_column("姓名", style="cyan")
        table.add_column("部門", style="green")
        table.add_column("薪資", style="yellow", justify="right")
        table.add_column("入職日期", style="blue")
        table.add_column("狀態", style="white")

        for row in result:
            table.add_row(
                row[0],
                row[1],
                f"${row[2]:,.2f}",
                str(row[3]),
                row[4]
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]✗ 顯示結果失敗: {e}[/red]")
        raise


def demonstrate_basic_queries(con):
    """展示基本查詢操作"""
    try:
        console.print("\n[bold cyan]7. 基本查詢操作[/bold cyan]")

        # 聚合查詢
        result = con.execute("""
            SELECT
                department,
                COUNT(*) as employee_count,
                AVG(salary) as avg_salary,
                MAX(salary) as max_salary
            FROM employees
            WHERE is_active = true
            GROUP BY department
            ORDER BY avg_salary DESC
        """).fetchdf()  # 返回 Pandas DataFrame

        console.print("\n   部門統計:")
        rprint(result.to_string(index=False))

        # DISTINCT 查詢
        departments = con.execute("""
            SELECT DISTINCT department
            FROM employees
            ORDER BY department
        """).fetchall()

        console.print(f"\n   部門列表: {[d[0] for d in departments]}", style="yellow")

    except Exception as e:
        console.print(f"[red]✗ 基本查詢失敗: {e}[/red]")
        raise


def demonstrate_connection_management():
    """展示連接管理"""
    try:
        console.print("\n[bold cyan]8. 連接管理[/bold cyan]")

        # 使用上下文管理器
        with duckdb.connect(':memory:') as con:
            con.execute("CREATE TABLE temp (id INTEGER, value VARCHAR)")
            con.execute("INSERT INTO temp VALUES (1, 'test')")
            result = con.execute("SELECT * FROM temp").fetchone()
            console.print(f"   上下文管理器查詢: {result}", style="green")

        console.print("   ✓ 連接自動關閉", style="green")

        # 多個獨立連接
        con1 = duckdb.connect(':memory:')
        con2 = duckdb.connect(':memory:')

        con1.execute("CREATE TABLE t1 (x INTEGER)")
        con1.execute("INSERT INTO t1 VALUES (1)")

        con2.execute("CREATE TABLE t2 (x INTEGER)")
        con2.execute("INSERT INTO t2 VALUES (2)")

        count1 = con1.execute("SELECT COUNT(*) FROM t1").fetchone()[0]
        count2 = con2.execute("SELECT COUNT(*) FROM t2").fetchone()[0]

        console.print(f"   連接 1 記錄數: {count1}", style="yellow")
        console.print(f"   連接 2 記錄數: {count2}", style="yellow")

        con1.close()
        con2.close()
        console.print("   ✓ 所有連接已關閉", style="green")

    except Exception as e:
        console.print(f"[red]✗ 連接管理示例失敗: {e}[/red]")
        raise


def main():
    """主函數"""
    console.print("\n[bold magenta]═══════════════════════════════════════[/bold magenta]")
    console.print("[bold magenta]    DuckDB-Agent 快速開始示例    [/bold magenta]")
    console.print("[bold magenta]═══════════════════════════════════════[/bold magenta]")

    try:
        # 1. 創建內存數據庫
        con_memory = create_in_memory_database()

        # 2. 創建持久化數據庫
        con_persistent = create_persistent_database()

        # 3. 創建表並插入數據
        create_and_populate_table(con_persistent)

        # 4. 展示數據類型
        demonstrate_data_types(con_persistent)

        # 5. 展示事務處理
        demonstrate_transactions(con_persistent)

        # 6. 顯示查詢結果
        display_query_results(con_persistent)

        # 7. 基本查詢操作
        demonstrate_basic_queries(con_persistent)

        # 8. 連接管理
        demonstrate_connection_management()

        # 清理
        con_memory.close()
        con_persistent.close()

        console.print("\n[bold green]✓ 所有示例執行成功！[/bold green]")
        console.print("\n[yellow]提示:[/yellow]")
        console.print("  - 內存數據庫適合臨時分析和測試")
        console.print("  - 持久化數據庫適合生產環境")
        console.print("  - DuckDB 是單線程寫入，但支持並行讀取")
        console.print("  - 支持豐富的數據類型，包括嵌套結構")

    except Exception as e:
        console.print(f"\n[bold red]✗ 執行失敗: {e}[/bold red]")
        raise


if __name__ == "__main__":
    main()

"""
DuckDB-Agent 示例 04: 自然語言查詢

展示如何使用 AI 將自然語言轉換為 SQL 查詢：
1. Text-to-SQL 基礎
2. 數據庫模式理解
3. 複雜查詢生成
4. 查詢驗證和優化
5. 錯誤處理和重試
6. 多輪對話查詢
"""

import duckdb
from openai import OpenAI
import os
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from dotenv import load_dotenv
import json

# 加載環境變量
load_dotenv()

console = Console()


def setup_database():
    """設置示例數據庫"""
    try:
        con = duckdb.connect(':memory:')

        # 創建銷售數據表
        con.execute("""
            CREATE TABLE sales (
                sale_id INTEGER PRIMARY KEY,
                product_name VARCHAR,
                category VARCHAR,
                quantity INTEGER,
                unit_price DECIMAL(10, 2),
                sale_date DATE,
                customer_name VARCHAR,
                region VARCHAR
            )
        """)

        # 插入示例數據
        con.execute("""
            INSERT INTO sales VALUES
            (1, 'MacBook Pro', '筆記本電腦', 2, 2499.00, '2025-01-15', '張三', '華北'),
            (2, 'iPhone 15', '手機', 5, 999.00, '2025-01-16', '李四', '華東'),
            (3, 'iPad Air', '平板電腦', 3, 599.00, '2025-01-17', '王五', '華南'),
            (4, 'AirPods Pro', '耳機', 10, 249.00, '2025-01-18', '趙六', '華北'),
            (5, 'Apple Watch', '智能手錶', 4, 399.00, '2025-01-19', '孫七', '華東'),
            (6, 'MacBook Air', '筆記本電腦', 3, 1299.00, '2025-01-20', '周八', '華南'),
            (7, 'Mac Mini', '台式機', 2, 699.00, '2025-01-21', '吳九', '華北'),
            (8, 'Studio Display', '顯示器', 1, 1599.00, '2025-01-22', '鄭十', '華東'),
            (9, 'Magic Keyboard', '鍵盤', 8, 99.00, '2025-01-23', '張三', '華南'),
            (10, 'iPhone 15 Pro', '手機', 3, 1199.00, '2025-01-24', '李四', '華北')
        """)

        console.print("[green]✓ 測試數據庫設置完成[/green]")
        return con

    except Exception as e:
        console.print(f"[red]✗ 設置數據庫失敗: {e}[/red]")
        raise


def get_database_schema(con):
    """獲取數據庫模式信息"""
    try:
        # 獲取表結構
        schema_info = con.execute("""
            SELECT
                column_name,
                data_type,
                is_nullable
            FROM information_schema.columns
            WHERE table_name = 'sales'
            ORDER BY ordinal_position
        """).fetchall()

        # 格式化模式信息
        schema_description = "表 'sales' 的結構:\n"
        for col in schema_info:
            schema_description += f"  - {col[0]} ({col[1]})\n"

        # 獲取示例數據
        sample_data = con.execute("SELECT * FROM sales LIMIT 3").fetchdf()

        schema_description += f"\n示例數據:\n{sample_data.to_string(index=False)}\n"

        # 獲取統計信息
        stats = con.execute("""
            SELECT
                COUNT(*) as total_records,
                COUNT(DISTINCT category) as categories,
                COUNT(DISTINCT region) as regions,
                MIN(sale_date) as first_sale,
                MAX(sale_date) as last_sale
            FROM sales
        """).fetchone()

        schema_description += f"\n數據統計:\n"
        schema_description += f"  - 總記錄數: {stats[0]}\n"
        schema_description += f"  - 產品類別: {stats[1]}\n"
        schema_description += f"  - 銷售區域: {stats[2]}\n"
        schema_description += f"  - 日期範圍: {stats[3]} 到 {stats[4]}\n"

        return schema_description

    except Exception as e:
        console.print(f"[red]✗ 獲取模式信息失敗: {e}[/red]")
        raise


def text_to_sql(client, user_query, schema_info):
    """將自然語言轉換為 SQL"""
    try:
        system_prompt = f"""你是一個專業的 SQL 生成助手。根據用戶的自然語言問題，生成對應的 DuckDB SQL 查詢。

數據庫模式信息:
{schema_info}

要求:
1. 只返回 SQL 查詢語句，不要包含其他解釋
2. 使用標準 SQL 語法
3. 確保查詢高效且正確
4. 如果需要聚合，使用適當的 GROUP BY
5. 適當使用 ORDER BY 和 LIMIT
6. 使用中文列別名方便理解結果
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            temperature=0
        )

        sql_query = response.choices[0].message.content.strip()

        # 清理 SQL（移除可能的 markdown 標記）
        if sql_query.startswith("```sql"):
            sql_query = sql_query[6:]
        if sql_query.startswith("```"):
            sql_query = sql_query[3:]
        if sql_query.endswith("```"):
            sql_query = sql_query[:-3]

        return sql_query.strip()

    except Exception as e:
        console.print(f"[red]✗ Text-to-SQL 轉換失敗: {e}[/red]")
        raise


def execute_natural_language_query(con, client, user_query, schema_info):
    """執行自然語言查詢"""
    try:
        console.print(f"\n[bold cyan]用戶問題:[/bold cyan] {user_query}")

        # 轉換為 SQL
        sql_query = text_to_sql(client, user_query, schema_info)

        # 顯示生成的 SQL
        console.print("\n[bold yellow]生成的 SQL:[/bold yellow]")
        syntax = Syntax(sql_query, "sql", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title="SQL Query", border_style="yellow"))

        # 執行查詢
        result = con.execute(sql_query).fetchdf()

        # 顯示結果
        console.print("\n[bold green]查詢結果:[/bold green]")
        if len(result) > 0:
            console.print(result.to_string(index=False))
            console.print(f"\n共 {len(result)} 條結果", style="dim")
        else:
            console.print("[yellow]沒有找到符合條件的數據[/yellow]")

        return result, sql_query

    except Exception as e:
        console.print(f"[red]✗ 執行查詢失敗: {e}[/red]")
        return None, None


def demonstrate_basic_queries(con, client, schema_info):
    """展示基本查詢"""
    console.print("\n[bold magenta]1. 基本自然語言查詢[/bold magenta]")

    queries = [
        "有多少個銷售記錄？",
        "列出所有產品類別",
        "找出銷售額最高的 5 個產品",
    ]

    for query in queries:
        execute_natural_language_query(con, client, query, schema_info)
        console.print("\n" + "─" * 80)


def demonstrate_aggregation_queries(con, client, schema_info):
    """展示聚合查詢"""
    console.print("\n[bold magenta]2. 聚合分析查詢[/bold magenta]")

    queries = [
        "每個產品類別的總銷售額是多少？",
        "哪個區域的銷售業績最好？",
        "計算每個產品的平均銷售價格",
    ]

    for query in queries:
        execute_natural_language_query(con, client, query, schema_info)
        console.print("\n" + "─" * 80)


def demonstrate_time_based_queries(con, client, schema_info):
    """展示時間相關查詢"""
    console.print("\n[bold magenta]3. 時間序列查詢[/bold magenta]")

    queries = [
        "過去一周的每日銷售額是多少？",
        "1月20日之後有哪些銷售記錄？",
        "銷售最早和最晚的日期分別是什麼？",
    ]

    for query in queries:
        execute_natural_language_query(con, client, query, schema_info)
        console.print("\n" + "─" * 80)


def demonstrate_complex_queries(con, client, schema_info):
    """展示複雜查詢"""
    console.print("\n[bold magenta]4. 複雜分析查詢[/bold magenta]")

    queries = [
        "找出銷售額超過 5000 元的客戶，並按金額排序",
        "哪個產品類別在華北地區賣得最好？",
        "計算每個區域的平均訂單金額，並找出高於整體平均的區域",
    ]

    for query in queries:
        execute_natural_language_query(con, client, query, schema_info)
        console.print("\n" + "─" * 80)


def demonstrate_query_with_explanation(con, client, schema_info):
    """展示帶解釋的查詢"""
    console.print("\n[bold magenta]5. 查詢結果解釋[/bold magenta]")

    try:
        user_query = "分析每個產品類別的銷售表現"

        console.print(f"\n[bold cyan]用戶問題:[/bold cyan] {user_query}")

        # 生成 SQL
        sql_query = text_to_sql(client, user_query, schema_info)

        # 執行查詢
        result = con.execute(sql_query).fetchdf()

        # 顯示 SQL 和結果
        console.print("\n[bold yellow]生成的 SQL:[/bold yellow]")
        syntax = Syntax(sql_query, "sql", theme="monokai")
        console.print(syntax)

        console.print("\n[bold green]查詢結果:[/bold green]")
        console.print(result.to_string(index=False))

        # 使用 AI 解釋結果
        explanation_prompt = f"""
根據以下查詢結果，用中文提供簡潔的分析和洞察:

查詢: {user_query}
結果:
{result.to_string(index=False)}

請提供:
1. 主要發現（2-3 點）
2. 關鍵洞察
3. 可能的建議
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": explanation_prompt}],
            temperature=0.3
        )

        explanation = response.choices[0].message.content

        console.print("\n[bold blue]AI 分析:[/bold blue]")
        console.print(Panel(explanation, border_style="blue"))

    except Exception as e:
        console.print(f"[red]✗ 查詢解釋失敗: {e}[/red]")
        raise


def demonstrate_error_handling(con, client, schema_info):
    """展示錯誤處理"""
    console.print("\n[bold magenta]6. 錯誤處理和重試[/bold magenta]")

    try:
        # 模糊或可能有問題的查詢
        user_query = "統計一下數據"

        console.print(f"\n[bold cyan]用戶問題（模糊）:[/bold cyan] {user_query}")

        # 第一次嘗試
        try:
            sql_query = text_to_sql(client, user_query, schema_info)
            console.print("\n[yellow]生成的 SQL (第一次嘗試):[/yellow]")
            console.print(sql_query)

            result = con.execute(sql_query).fetchdf()
            console.print("\n[green]✓ 查詢成功[/green]")
            console.print(result.to_string(index=False))

        except Exception as e:
            console.print(f"\n[red]✗ 第一次查詢失敗: {e}[/red]")

            # 重試：提供更多上下文
            retry_prompt = f"""
原始問題: {user_query}
錯誤信息: {str(e)}

請生成一個更明確的 SQL 查詢，提供有用的數據統計信息。
"""
            sql_query = text_to_sql(client, retry_prompt, schema_info)

            console.print("\n[yellow]生成的 SQL (重試):[/yellow]")
            console.print(sql_query)

            result = con.execute(sql_query).fetchdf()
            console.print("\n[green]✓ 重試成功[/green]")
            console.print(result.to_string(index=False))

    except Exception as e:
        console.print(f"[red]✗ 錯誤處理示例失敗: {e}[/red]")


def demonstrate_multi_turn_conversation(con, client, schema_info):
    """展示多輪對話查詢"""
    console.print("\n[bold magenta]7. 多輪對話查詢[/bold magenta]")

    try:
        conversation_history = []

        # 第一輪：基礎查詢
        query1 = "顯示所有產品類別的銷售情況"
        console.print(f"\n[bold cyan]第一輪:[/bold cyan] {query1}")

        result1, sql1 = execute_natural_language_query(con, client, query1, schema_info)
        conversation_history.append({
            "query": query1,
            "sql": sql1,
            "result": result1.to_string(index=False) if result1 is not None else ""
        })

        # 第二輪：深入分析
        query2 = "聚焦在銷售額最高的類別，顯示該類別的詳細銷售記錄"
        console.print(f"\n\n[bold cyan]第二輪:[/bold cyan] {query2}")

        # 構建包含上下文的提示
        context_prompt = f"""
之前的查詢:
{conversation_history[0]['query']}

SQL: {conversation_history[0]['sql']}

結果:
{conversation_history[0]['result']}

現在的問題: {query2}
"""

        result2, sql2 = execute_natural_language_query(con, client, context_prompt, schema_info)

        console.print("\n[green]✓ 多輪對話查詢完成[/green]")

    except Exception as e:
        console.print(f"[red]✗ 多輪對話失敗: {e}[/red]")


def main():
    """主函數"""
    console.print("\n[bold magenta]═══════════════════════════════════════[/bold magenta]")
    console.print("[bold magenta]   DuckDB 自然語言查詢示例   [/bold magenta]")
    console.print("[bold magenta]═══════════════════════════════════════[/bold magenta]")

    # 檢查 API Key
    if not os.getenv("OPENAI_API_KEY"):
        console.print("\n[bold red]錯誤: 請設置 OPENAI_API_KEY 環境變量[/bold red]")
        console.print("您可以在 .env 文件中設置: OPENAI_API_KEY=your_api_key")
        return

    try:
        # 設置數據庫
        con = setup_database()

        # 創建 OpenAI 客戶端
        client = OpenAI()

        # 獲取數據庫模式
        schema_info = get_database_schema(con)
        console.print("\n[bold green]數據庫模式信息:[/bold green]")
        console.print(schema_info)

        # 1. 基本查詢
        demonstrate_basic_queries(con, client, schema_info)

        # 2. 聚合查詢
        demonstrate_aggregation_queries(con, client, schema_info)

        # 3. 時間查詢
        demonstrate_time_based_queries(con, client, schema_info)

        # 4. 複雜查詢
        demonstrate_complex_queries(con, client, schema_info)

        # 5. 帶解釋的查詢
        demonstrate_query_with_explanation(con, client, schema_info)

        # 6. 錯誤處理
        demonstrate_error_handling(con, client, schema_info)

        # 7. 多輪對話
        demonstrate_multi_turn_conversation(con, client, schema_info)

        # 清理
        con.close()

        console.print("\n[bold green]✓ 所有自然語言查詢示例執行成功！[/bold green]")
        console.print("\n[yellow]Text-to-SQL 優勢:[/yellow]")
        console.print("  - 降低 SQL 學習門檻")
        console.print("  - 提高數據分析效率")
        console.print("  - 支持複雜查詢生成")
        console.print("  - 可以進行多輪對話")
        console.print("  - 自動優化查詢性能")

    except Exception as e:
        console.print(f"\n[bold red]✗ 執行失敗: {e}[/bold red]")
        raise


if __name__ == "__main__":
    main()

"""
DuckDB-Agent 示例 07: Agent 整合

展示完整的 LLM Agent 數據分析助手：
1. 智能數據分析 Agent
2. 自動化報表生成
3. 數據洞察發現
4. 異常檢測
5. 交互式對話分析
6. 完整工作流示例
"""

import duckdb
from openai import OpenAI
import os
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from dotenv import load_dotenv
import json
from datetime import datetime

load_dotenv()

console = Console()


class DuckDBAnalysisAgent:
    """DuckDB 數據分析 Agent"""

    def __init__(self, db_path=":memory:"):
        """初始化 Agent"""
        self.con = duckdb.connect(db_path)
        self.client = OpenAI()
        self.conversation_history = []
        self.schema_cache = {}

        console.print("[green]✓ DuckDB Analysis Agent 初始化成功[/green]")

    def load_sample_data(self):
        """加載示例數據"""
        try:
            # 創建銷售數據表
            self.con.execute("""
                CREATE TABLE sales_data (
                    order_id INTEGER,
                    order_date DATE,
                    customer_id INTEGER,
                    customer_name VARCHAR,
                    product_category VARCHAR,
                    product_name VARCHAR,
                    quantity INTEGER,
                    unit_price DECIMAL(10, 2),
                    total_amount DECIMAL(10, 2),
                    region VARCHAR,
                    sales_rep VARCHAR
                )
            """)

            # 插入示例數據
            self.con.execute("""
                INSERT INTO sales_data VALUES
                (1001, '2025-01-15', 1, '科技公司A', '電腦', 'MacBook Pro', 5, 2499.00, 12495.00, '華北', '張三'),
                (1002, '2025-01-16', 2, '教育機構B', '平板', 'iPad Air', 10, 599.00, 5990.00, '華東', '李四'),
                (1003, '2025-01-17', 1, '科技公司A', '手機', 'iPhone 15', 20, 999.00, 19980.00, '華北', '張三'),
                (1004, '2025-01-18', 3, '零售店C', '配件', 'AirPods Pro', 15, 249.00, 3735.00, '華南', '王五'),
                (1005, '2025-01-19', 4, '企業D', '電腦', 'MacBook Air', 8, 1299.00, 10392.00, '華東', '李四'),
                (1006, '2025-01-20', 2, '教育機構B', '配件', 'Apple Watch', 12, 399.00, 4788.00, '華東', '李四'),
                (1007, '2025-01-21', 5, '創業公司E', '電腦', 'Mac Mini', 3, 699.00, 2097.00, '華南', '王五'),
                (1008, '2025-01-22', 3, '零售店C', '手機', 'iPhone 15 Pro', 18, 1199.00, 21582.00, '華南', '王五'),
                (1009, '2025-01-23', 6, '政府機構F', '配件', 'Studio Display', 4, 1599.00, 6396.00, '華北', '張三'),
                (1010, '2025-01-24', 4, '企業D', '平板', 'iPad Pro', 6, 1099.00, 6594.00, '華東', '李四'),
                (1011, '2025-01-25', 1, '科技公司A', '配件', 'Magic Keyboard', 25, 99.00, 2475.00, '華北', '張三'),
                (1012, '2025-01-26', 7, '醫療機構G', '電腦', 'MacBook Pro', 10, 2499.00, 24990.00, '華南', '王五')
            """)

            console.print("[green]✓ 示例數據加載成功[/green]")

            # 獲取並緩存數據庫模式
            self._update_schema_cache()

        except Exception as e:
            console.print(f"[red]✗ 加載數據失敗: {e}[/red]")
            raise

    def _update_schema_cache(self):
        """更新數據庫模式緩存"""
        try:
            # 獲取表信息
            tables = self.con.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'main'
            """).fetchall()

            for table in tables:
                table_name = table[0]

                # 獲取列信息
                columns = self.con.execute(f"""
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_name = '{table_name}'
                """).fetchall()

                # 獲取示例數據
                sample = self.con.execute(f"""
                    SELECT * FROM {table_name} LIMIT 3
                """).fetchdf()

                self.schema_cache[table_name] = {
                    'columns': columns,
                    'sample': sample.to_string(index=False)
                }

        except Exception as e:
            console.print(f"[yellow]⚠ 更新模式緩存失敗: {e}[/yellow]")

    def get_schema_description(self):
        """獲取數據庫模式描述"""
        description = "數據庫結構:\n\n"

        for table_name, info in self.schema_cache.items():
            description += f"表: {table_name}\n"
            description += "列:\n"
            for col_name, col_type in info['columns']:
                description += f"  - {col_name} ({col_type})\n"
            description += f"\n示例數據:\n{info['sample']}\n\n"

        return description

    def generate_sql(self, user_question):
        """生成 SQL 查詢"""
        try:
            schema_desc = self.get_schema_description()

            system_prompt = f"""你是一個專業的數據分析 SQL 助手。
根據用戶問題生成 DuckDB SQL 查詢。

{schema_desc}

要求:
1. 只返回 SQL 語句，不要包含解釋
2. 使用中文列別名
3. 確保 SQL 語法正確
4. 適當使用聚合和分組
5. 添加 ORDER BY 使結果更有意義
"""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_question}
                ],
                temperature=0
            )

            sql = response.choices[0].message.content.strip()

            # 清理 SQL
            if sql.startswith("```sql"):
                sql = sql[6:]
            if sql.startswith("```"):
                sql = sql[3:]
            if sql.endswith("```"):
                sql = sql[:-3]

            return sql.strip()

        except Exception as e:
            console.print(f"[red]✗ SQL 生成失敗: {e}[/red]")
            raise

    def execute_query(self, sql):
        """執行 SQL 查詢"""
        try:
            result = self.con.execute(sql).fetchdf()
            return result
        except Exception as e:
            console.print(f"[red]✗ 查詢執行失敗: {e}[/red]")
            return None

    def analyze_results(self, question, sql, results):
        """分析查詢結果並生成洞察"""
        try:
            if results is None or len(results) == 0:
                return "沒有找到相關數據。"

            analysis_prompt = f"""
作為數據分析師，請分析以下查詢結果並提供洞察。

用戶問題: {question}

查詢結果:
{results.to_string(index=False)}

請提供:
1. 主要發現（2-3 點）
2. 數據洞察
3. 可能的建議或下一步行動

用中文回答，保持簡潔專業。
"""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": analysis_prompt}],
                temperature=0.3
            )

            return response.choices[0].message.content

        except Exception as e:
            console.print(f"[red]✗ 結果分析失敗: {e}[/red]")
            return "分析失敗"

    def chat(self, user_question):
        """交互式對話分析"""
        try:
            console.print(f"\n[bold cyan]問題:[/bold cyan] {user_question}")

            # 生成 SQL
            sql = self.generate_sql(user_question)

            console.print("\n[bold yellow]生成的 SQL:[/bold yellow]")
            syntax = Syntax(sql, "sql", theme="monokai", line_numbers=True)
            console.print(Panel(syntax, border_style="yellow"))

            # 執行查詢
            results = self.execute_query(sql)

            if results is not None and len(results) > 0:
                console.print("\n[bold green]查詢結果:[/bold green]")
                console.print(results.to_string(index=False))

                # 分析結果
                analysis = self.analyze_results(user_question, sql, results)

                console.print("\n[bold blue]AI 分析:[/bold blue]")
                console.print(Panel(analysis, border_style="blue"))

                # 保存到對話歷史
                self.conversation_history.append({
                    'question': user_question,
                    'sql': sql,
                    'results': results,
                    'analysis': analysis,
                    'timestamp': datetime.now().isoformat()
                })

                return {
                    'sql': sql,
                    'results': results,
                    'analysis': analysis
                }
            else:
                console.print("\n[yellow]沒有找到數據[/yellow]")
                return None

        except Exception as e:
            console.print(f"[red]✗ 對話失敗: {e}[/red]")
            return None

    def generate_report(self):
        """生成自動化報表"""
        console.print("\n[bold magenta]生成數據分析報表[/bold magenta]")

        try:
            # 定義報表問題
            report_questions = [
                "總銷售額是多少？",
                "哪個區域的銷售額最高？",
                "銷售業績最好的銷售代表是誰？",
                "哪個產品類別最受歡迎？",
                "平均訂單金額是多少？"
            ]

            report_data = []

            for question in report_questions:
                result = self.chat(question)
                if result:
                    report_data.append(result)
                console.print("\n" + "─" * 80)

            console.print("\n[bold green]✓ 報表生成完成[/bold green]")
            console.print(f"共分析 {len(report_data)} 個指標")

            return report_data

        except Exception as e:
            console.print(f"[red]✗ 報表生成失敗: {e}[/red]")
            return []

    def detect_anomalies(self):
        """檢測數據異常"""
        console.print("\n[bold magenta]執行異常檢測[/bold magenta]")

        try:
            # 查找異常訂單
            sql = """
                WITH stats AS (
                    SELECT
                        AVG(total_amount) as avg_amount,
                        STDDEV(total_amount) as stddev_amount
                    FROM sales_data
                )
                SELECT
                    s.order_id,
                    s.customer_name,
                    s.total_amount,
                    st.avg_amount,
                    (s.total_amount - st.avg_amount) / NULLIF(st.stddev_amount, 0) as z_score
                FROM sales_data s, stats st
                WHERE ABS((s.total_amount - st.avg_amount) / NULLIF(st.stddev_amount, 0)) > 1.5
                ORDER BY ABS((s.total_amount - st.avg_amount) / NULLIF(st.stddev_amount, 0)) DESC
            """

            console.print("\n[yellow]異常訂單檢測 SQL:[/yellow]")
            console.print(Syntax(sql, "sql", theme="monokai"))

            results = self.execute_query(sql)

            if results is not None and len(results) > 0:
                console.print("\n[bold red]發現異常訂單:[/bold red]")
                console.print(results.to_string(index=False))

                # AI 分析異常
                analysis = self.analyze_results(
                    "為什麼這些訂單被標記為異常？",
                    sql,
                    results
                )

                console.print("\n[bold blue]異常分析:[/bold blue]")
                console.print(Panel(analysis, border_style="red"))

            else:
                console.print("\n[green]✓ 未發現明顯異常[/green]")

        except Exception as e:
            console.print(f"[red]✗ 異常檢測失敗: {e}[/red]")

    def export_insights(self, filename="insights.json"):
        """導出分析洞察"""
        try:
            export_data = {
                'generated_at': datetime.now().isoformat(),
                'total_conversations': len(self.conversation_history),
                'conversations': self.conversation_history
            }

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2, default=str)

            console.print(f"\n[green]✓ 洞察已導出到: {filename}[/green]")

        except Exception as e:
            console.print(f"[red]✗ 導出失敗: {e}[/red]")

    def close(self):
        """關閉數據庫連接"""
        self.con.close()
        console.print("\n[green]✓ Agent 已關閉[/green]")


def demonstrate_interactive_analysis():
    """展示交互式分析"""
    console.print("\n[bold magenta]═══════════════════════════════════════[/bold magenta]")
    console.print("[bold magenta]  DuckDB Analysis Agent 演示  [/bold magenta]")
    console.print("[bold magenta]═══════════════════════════════════════[/bold magenta]")

    if not os.getenv("OPENAI_API_KEY"):
        console.print("\n[bold red]錯誤: 請設置 OPENAI_API_KEY 環境變量[/bold red]")
        return

    try:
        # 創建 Agent
        agent = DuckDBAnalysisAgent()

        # 加載數據
        console.print("\n[bold cyan]1. 加載示例數據[/bold cyan]")
        agent.load_sample_data()

        # 交互式查詢
        console.print("\n[bold cyan]2. 交互式數據分析[/bold cyan]")
        console.print("─" * 80)

        questions = [
            "過去一個月的銷售趨勢如何？",
            "哪個銷售代表的業績最好？",
            "最暢銷的產品是什麼？",
            "各區域的銷售額分布情況",
        ]

        for question in questions:
            agent.chat(question)
            console.print("\n" + "─" * 80)

        # 生成報表
        console.print("\n[bold cyan]3. 自動生成分析報表[/bold cyan]")
        console.print("─" * 80)
        agent.generate_report()

        # 異常檢測
        console.print("\n[bold cyan]4. 智能異常檢測[/bold cyan]")
        console.print("─" * 80)
        agent.detect_anomalies()

        # 導出洞察
        console.print("\n[bold cyan]5. 導出分析結果[/bold cyan]")
        agent.export_insights()

        # 清理
        agent.close()

        console.print("\n[bold green]✓ 所有 Agent 功能演示完成！[/bold green]")

        console.print("\n[yellow]DuckDB Agent 優勢:[/yellow]")
        console.print("  - 自然語言到 SQL 的智能轉換")
        console.print("  - 自動化數據洞察生成")
        console.print("  - 異常檢測和預警")
        console.print("  - 交互式對話分析")
        console.print("  - 自動化報表生成")
        console.print("  - 完整的分析工作流")

    except Exception as e:
        console.print(f"\n[bold red]✗ 演示失敗: {e}[/bold red]")
        raise


def main():
    """主函數"""
    demonstrate_interactive_analysis()


if __name__ == "__main__":
    main()

"""
Weaviate 過濾器示例

本示例展示：
1. 基本 Where 過濾器
2. 複合條件過濾
3. 數值範圍過濾
4. 文本匹配過濾
5. 日期過濾
"""

import weaviate
from weaviate.classes.config import Configure, Property, DataType
from weaviate.classes.query import Filter, MetadataQuery
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from datetime import datetime, timezone, timedelta

console = Console()


def setup_test_data(client):
    """設置測試數據"""
    console.print("[cyan]設置測試數據...[/cyan]")

    try:
        if client.collections.exists("Employee"):
            client.collections.delete("Employee")

        client.collections.create(
            name="Employee",
            properties=[
                Property(name="name", data_type=DataType.TEXT),
                Property(name="department", data_type=DataType.TEXT),
                Property(name="position", data_type=DataType.TEXT),
                Property(name="salary", data_type=DataType.NUMBER),
                Property(name="age", data_type=DataType.INT),
                Property(name="skills", data_type=DataType.TEXT_ARRAY),
                Property(name="hireDate", data_type=DataType.DATE),
                Property(name="isRemote", data_type=DataType.BOOL),
            ],
            vectorizer_config=Configure.Vectorizer.none()
        )

        employees = client.collections.get("Employee")

        # 創建測試數據
        base_date = datetime.now(timezone.utc)
        test_employees = [
            {
                "name": "張偉",
                "department": "工程",
                "position": "高級工程師",
                "salary": 120000,
                "age": 32,
                "skills": ["Python", "機器學習", "Docker"],
                "hireDate": (base_date - timedelta(days=730)).isoformat(),
                "isRemote": True
            },
            {
                "name": "李娜",
                "department": "產品",
                "position": "產品經理",
                "salary": 110000,
                "age": 29,
                "skills": ["產品設計", "數據分析", "用戶研究"],
                "hireDate": (base_date - timedelta(days=500)).isoformat(),
                "isRemote": False
            },
            {
                "name": "王強",
                "department": "工程",
                "position": "初級工程師",
                "salary": 80000,
                "age": 25,
                "skills": ["Java", "Spring Boot", "MySQL"],
                "hireDate": (base_date - timedelta(days=180)).isoformat(),
                "isRemote": True
            },
            {
                "name": "趙敏",
                "department": "設計",
                "position": "UI設計師",
                "salary": 90000,
                "age": 27,
                "skills": ["Figma", "UI設計", "動畫"],
                "hireDate": (base_date - timedelta(days=365)).isoformat(),
                "isRemote": False
            },
            {
                "name": "劉洋",
                "department": "工程",
                "position": "架構師",
                "salary": 150000,
                "age": 38,
                "skills": ["系統設計", "微服務", "Kubernetes"],
                "hireDate": (base_date - timedelta(days=1095)).isoformat(),
                "isRemote": True
            },
            {
                "name": "陳靜",
                "department": "市場",
                "position": "市場經理",
                "salary": 100000,
                "age": 31,
                "skills": ["市場策略", "品牌管理", "SEO"],
                "hireDate": (base_date - timedelta(days=600)).isoformat(),
                "isRemote": False
            },
        ]

        with employees.batch.dynamic() as batch:
            for emp in test_employees:
                batch.add_object(properties=emp)

        console.print(f"[green]✓ 已插入 {len(test_employees)} 名員工[/green]\n")

    except Exception as e:
        console.print(f"[red]✗ 設置失敗: {e}[/red]")


def basic_equal_filter(client):
    """基本相等過濾"""
    console.print("[bold cyan]1. 基本相等過濾[/bold cyan]")

    try:
        employees = client.collections.get("Employee")

        console.print("[yellow]過濾: department = '工程'[/yellow]\n")

        response = employees.query.fetch_objects(
            filters=Filter.by_property("department").equal("工程"),
            limit=10
        )

        table = Table(title="工程部門員工")
        table.add_column("姓名", style="cyan")
        table.add_column("職位", style="green")
        table.add_column("薪資", style="yellow")

        for obj in response.objects:
            table.add_row(
                obj.properties["name"],
                obj.properties["position"],
                f"${obj.properties['salary']:,}"
            )

        console.print(table)
        console.print()

    except Exception as e:
        console.print(f"[red]✗ 過濾失敗: {e}[/red]")


def numeric_range_filter(client):
    """數值範圍過濾"""
    console.print("[bold cyan]2. 數值範圍過濾[/bold cyan]")

    try:
        employees = client.collections.get("Employee")

        console.print("[yellow]過濾: salary >= 100000 AND salary <= 130000[/yellow]\n")

        response = employees.query.fetch_objects(
            filters=(
                Filter.by_property("salary").greater_or_equal(100000) &
                Filter.by_property("salary").less_or_equal(130000)
            ),
            limit=10
        )

        console.print("[bold]薪資在 $100,000 - $130,000 的員工:[/bold]")
        for obj in response.objects:
            console.print(f"  • {obj.properties['name']} - "
                         f"{obj.properties['position']} - "
                         f"${obj.properties['salary']:,}")

        console.print()

    except Exception as e:
        console.print(f"[red]✗ 過濾失敗: {e}[/red]")


def compound_and_filter(client):
    """複合 AND 過濾"""
    console.print("[bold cyan]3. 複合 AND 過濾[/bold cyan]")

    try:
        employees = client.collections.get("Employee")

        console.print("[yellow]過濾: department = '工程' AND isRemote = True[/yellow]\n")

        response = employees.query.fetch_objects(
            filters=(
                Filter.by_property("department").equal("工程") &
                Filter.by_property("isRemote").equal(True)
            ),
            limit=10
        )

        table = Table(title="遠程工程師")
        table.add_column("姓名", style="cyan")
        table.add_column("職位", style="green")
        table.add_column("年齡", style="yellow")

        for obj in response.objects:
            table.add_row(
                obj.properties["name"],
                obj.properties["position"],
                str(obj.properties["age"])
            )

        console.print(table)
        console.print()

    except Exception as e:
        console.print(f"[red]✗ 過濾失敗: {e}[/red]")


def compound_or_filter(client):
    """複合 OR 過濾"""
    console.print("[bold cyan]4. 複合 OR 過濾[/bold cyan]")

    try:
        employees = client.collections.get("Employee")

        console.print("[yellow]過濾: department = '工程' OR department = '產品'[/yellow]\n")

        response = employees.query.fetch_objects(
            filters=(
                Filter.by_property("department").equal("工程") |
                Filter.by_property("department").equal("產品")
            ),
            limit=10
        )

        console.print("[bold]工程或產品部門員工:[/bold]")
        for obj in response.objects:
            console.print(f"  • {obj.properties['name']} - "
                         f"{obj.properties['department']} - "
                         f"{obj.properties['position']}")

        console.print()

    except Exception as e:
        console.print(f"[red]✗ 過濾失敗: {e}[/red]")


def text_contains_filter(client):
    """文本包含過濾"""
    console.print("[bold cyan]5. 文本包含過濾[/bold cyan]")

    try:
        employees = client.collections.get("Employee")

        console.print("[yellow]過濾: position LIKE '%工程師%'[/yellow]\n")

        response = employees.query.fetch_objects(
            filters=Filter.by_property("position").like("*工程師*"),
            limit=10
        )

        console.print("[bold]所有工程師:[/bold]")
        for obj in response.objects:
            console.print(f"  • {obj.properties['name']} - {obj.properties['position']}")

        console.print()

    except Exception as e:
        console.print(f"[red]✗ 過濾失敗: {e}[/red]")


def array_contains_filter(client):
    """數組包含過濾"""
    console.print("[bold cyan]6. 數組包含過濾[/bold cyan]")

    try:
        employees = client.collections.get("Employee")

        console.print("[yellow]過濾: skills 包含 'Python'[/yellow]\n")

        response = employees.query.fetch_objects(
            filters=Filter.by_property("skills").contains_any(["Python"]),
            limit=10
        )

        table = Table(title="會 Python 的員工")
        table.add_column("姓名", style="cyan")
        table.add_column("職位", style="green")
        table.add_column("技能", style="yellow", width=30)

        for obj in response.objects:
            skills = ", ".join(obj.properties["skills"])
            table.add_row(
                obj.properties["name"],
                obj.properties["position"],
                skills
            )

        console.print(table)
        console.print()

    except Exception as e:
        console.print(f"[red]✗ 過濾失敗: {e}[/red]")


def date_filter(client):
    """日期過濾"""
    console.print("[bold cyan]7. 日期過濾[/bold cyan]")

    try:
        employees = client.collections.get("Employee")

        # 過濾一年內入職的員工
        one_year_ago = (datetime.now(timezone.utc) - timedelta(days=365)).isoformat()

        console.print(f"[yellow]過濾: hireDate > {one_year_ago[:10]}[/yellow]\n")

        response = employees.query.fetch_objects(
            filters=Filter.by_property("hireDate").greater_than(one_year_ago),
            limit=10
        )

        console.print("[bold]一年內入職的員工:[/bold]")
        for obj in response.objects:
            hire_date = obj.properties["hireDate"][:10]
            console.print(f"  • {obj.properties['name']} - 入職日期: {hire_date}")

        console.print()

    except Exception as e:
        console.print(f"[red]✗ 過濾失敗: {e}[/red]")


def complex_nested_filter(client):
    """複雜嵌套過濾"""
    console.print("[bold cyan]8. 複雜嵌套過濾[/bold cyan]")

    try:
        employees = client.collections.get("Employee")

        console.print("[yellow]過濾: (department='工程' AND salary>100000) OR (age<30)[/yellow]\n")

        response = employees.query.fetch_objects(
            filters=(
                (
                    Filter.by_property("department").equal("工程") &
                    Filter.by_property("salary").greater_than(100000)
                ) |
                Filter.by_property("age").less_than(30)
            ),
            limit=10
        )

        table = Table(title="符合條件的員工")
        table.add_column("姓名", style="cyan")
        table.add_column("部門", style="green")
        table.add_column("年齡", style="yellow")
        table.add_column("薪資", style="magenta")

        for obj in response.objects:
            table.add_row(
                obj.properties["name"],
                obj.properties["department"],
                str(obj.properties["age"]),
                f"${obj.properties['salary']:,}"
            )

        console.print(table)
        console.print()

    except Exception as e:
        console.print(f"[red]✗ 過濾失敗: {e}[/red]")


def filter_with_search(client):
    """過濾 + 搜索組合"""
    console.print("[bold cyan]9. 過濾 + 向量搜索組合[/bold cyan]")

    try:
        # 注意: 此示例需要啟用向量化器
        # 這裡展示概念，實際使用時需要配置向量化器

        employees = client.collections.get("Employee")

        console.print("[yellow]搜索遠程工作的高級職位[/yellow]\n")

        # 使用過濾器限制搜索範圍
        response = employees.query.fetch_objects(
            filters=(
                Filter.by_property("isRemote").equal(True) &
                Filter.by_property("position").like("*高級*")
            ),
            limit=10
        )

        if response.objects:
            console.print("[bold]結果:[/bold]")
            for obj in response.objects:
                console.print(f"  • {obj.properties['name']} - "
                             f"{obj.properties['position']} - "
                             f"遠程工作")
        else:
            console.print("[yellow]沒有找到符合條件的結果[/yellow]")

        console.print()

    except Exception as e:
        console.print(f"[red]✗ 搜索失敗: {e}[/red]")


def filter_best_practices():
    """過濾器最佳實踐"""
    console.print("[bold cyan]10. 過濾器最佳實踐[/bold cyan]")

    practices = [
        ("索引優化", "常用過濾字段設置 index_filterable=True"),
        ("數據類型", "使用正確的數據類型提升過濾性能"),
        ("複合條件", "先用過濾器縮小範圍,再做向量搜索"),
        ("文本匹配", "精確匹配用equal,模糊匹配用like"),
        ("數組查詢", "使用contains_any或contains_all"),
        ("日期範圍", "使用ISO格式,注意時區處理"),
        ("性能考慮", "過濾條件越具體,查詢越快"),
        ("布爾邏輯", "善用&(AND)和|(OR)組合條件"),
    ]

    table = Table(title="過濾器最佳實踐")
    table.add_column("主題", style="cyan", width=15)
    table.add_column("建議", style="green", width=45)

    for topic, advice in practices:
        table.add_row(topic, advice)

    console.print(table)


def cleanup(client):
    """清理資源"""
    try:
        if client.collections.exists("Employee"):
            client.collections.delete("Employee")
        client.close()
    except Exception as e:
        console.print(f"[red]清理失敗: {e}[/red]")


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Weaviate 過濾器示例[/bold cyan]",
        border_style="cyan"
    ))

    try:
        client = weaviate.connect_to_local()
        console.print("[green]✓ 已連接到 Weaviate[/green]\n")

        # 設置測試數據
        setup_test_data(client)

        # 執行各種過濾示例
        basic_equal_filter(client)
        numeric_range_filter(client)
        compound_and_filter(client)
        compound_or_filter(client)
        text_contains_filter(client)
        array_contains_filter(client)
        date_filter(client)
        complex_nested_filter(client)
        filter_with_search(client)
        filter_best_practices()

        console.print("="*60)
        console.print("[bold green]✓ 過濾器示例完成！[/bold green]")

    except Exception as e:
        console.print(f"[red]錯誤: {e}[/red]")
    finally:
        cleanup(client)


if __name__ == "__main__":
    main()

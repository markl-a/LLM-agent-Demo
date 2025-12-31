"""
Weaviate 多租戶示例

本示例展示：
1. 多租戶配置
2. 租戶創建和管理
3. 租戶數據隔離
4. 租戶級別操作
"""

import weaviate
from weaviate.classes.config import Configure, Property, DataType
from weaviate.classes.tenants import Tenant
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def connect_client():
    """連接到 Weaviate"""
    try:
        client = weaviate.connect_to_local()
        console.print("[green]✓ 已連接到 Weaviate[/green]\n")
        return client
    except Exception as e:
        console.print(f"[red]✗ 連接失敗: {e}[/red]")
        return None


def create_multi_tenant_collection(client):
    """創建多租戶集合"""
    console.print("[bold cyan]1. 創建多租戶集合[/bold cyan]")

    try:
        # 刪除已存在的集合
        if client.collections.exists("UserData"):
            client.collections.delete("UserData")

        # 創建啟用多租戶的集合
        client.collections.create(
            name="UserData",
            properties=[
                Property(name="username", data_type=DataType.TEXT),
                Property(name="email", data_type=DataType.TEXT),
                Property(name="data", data_type=DataType.TEXT),
                Property(name="createdAt", data_type=DataType.DATE),
            ],
            vectorizer_config=Configure.Vectorizer.text2vec_openai(),
            # 啟用多租戶
            multi_tenancy_config=Configure.multi_tenancy(enabled=True)
        )

        console.print("[green]✓ 多租戶集合創建成功[/green]")
        console.print("[dim]集合: UserData (多租戶已啟用)[/dim]\n")

    except Exception as e:
        console.print(f"[red]✗ 創建失敗: {e}[/red]")


def create_tenants(client):
    """創建租戶"""
    console.print("[bold cyan]2. 創建租戶[/bold cyan]")

    try:
        user_data = client.collections.get("UserData")

        # 創建多個租戶
        tenants = [
            Tenant(name="company_a"),
            Tenant(name="company_b"),
            Tenant(name="company_c"),
        ]

        user_data.tenants.create(tenants)

        console.print("[green]✓ 成功創建 3 個租戶[/green]")
        console.print("[dim]租戶: company_a, company_b, company_c[/dim]\n")

    except Exception as e:
        console.print(f"[red]✗ 創建租戶失敗: {e}[/red]")


def list_tenants(client):
    """列出所有租戶"""
    console.print("[bold cyan]3. 列出所有租戶[/bold cyan]")

    try:
        user_data = client.collections.get("UserData")

        # 獲取所有租戶
        tenants = user_data.tenants.get()

        table = Table(title="租戶列表")
        table.add_column("租戶名稱", style="cyan")
        table.add_column("狀態", style="green")

        for tenant in tenants:
            table.add_row(tenant.name, "活躍")

        console.print(table)
        console.print()

    except Exception as e:
        console.print(f"[red]✗ 列出租戶失敗: {e}[/red]")


def insert_tenant_data(client):
    """為不同租戶插入數據"""
    console.print("[bold cyan]4. 為不同租戶插入數據[/bold cyan]")

    try:
        from datetime import datetime, timezone

        # Company A 的數據
        console.print("[yellow]為 Company A 插入數據...[/yellow]")
        user_data_a = client.collections.get("UserData").with_tenant("company_a")

        company_a_data = [
            {
                "username": "alice",
                "email": "alice@companya.com",
                "data": "Company A 的用戶數據 - Alice的項目文檔",
                "createdAt": datetime.now(timezone.utc).isoformat()
            },
            {
                "username": "bob",
                "email": "bob@companya.com",
                "data": "Company A 的用戶數據 - Bob的會議記錄",
                "createdAt": datetime.now(timezone.utc).isoformat()
            },
        ]

        with user_data_a.batch.dynamic() as batch:
            for data in company_a_data:
                batch.add_object(properties=data)

        console.print(f"[green]✓ Company A: 插入 {len(company_a_data)} 條數據[/green]")

        # Company B 的數據
        console.print("[yellow]為 Company B 插入數據...[/yellow]")
        user_data_b = client.collections.get("UserData").with_tenant("company_b")

        company_b_data = [
            {
                "username": "charlie",
                "email": "charlie@companyb.com",
                "data": "Company B 的用戶數據 - Charlie的產品規劃",
                "createdAt": datetime.now(timezone.utc).isoformat()
            },
            {
                "username": "diana",
                "email": "diana@companyb.com",
                "data": "Company B 的用戶數據 - Diana的設計稿",
                "createdAt": datetime.now(timezone.utc).isoformat()
            },
        ]

        with user_data_b.batch.dynamic() as batch:
            for data in company_b_data:
                batch.add_object(properties=data)

        console.print(f"[green]✓ Company B: 插入 {len(company_b_data)} 條數據[/green]")

        # Company C 的數據
        console.print("[yellow]為 Company C 插入數據...[/yellow]")
        user_data_c = client.collections.get("UserData").with_tenant("company_c")

        company_c_data = [
            {
                "username": "eve",
                "email": "eve@companyc.com",
                "data": "Company C 的用戶數據 - Eve的銷售報告",
                "createdAt": datetime.now(timezone.utc).isoformat()
            },
        ]

        with user_data_c.batch.dynamic() as batch:
            for data in company_c_data:
                batch.add_object(properties=data)

        console.print(f"[green]✓ Company C: 插入 {len(company_c_data)} 條數據[/green]\n")

    except Exception as e:
        console.print(f"[red]✗ 插入數據失敗: {e}[/red]")


def query_tenant_data(client):
    """查詢特定租戶的數據"""
    console.print("[bold cyan]5. 查詢特定租戶的數據[/bold cyan]")

    try:
        # 查詢 Company A 的數據
        console.print("[yellow]查詢 Company A 的數據:[/yellow]")
        user_data_a = client.collections.get("UserData").with_tenant("company_a")

        response_a = user_data_a.query.fetch_objects(limit=10)

        table_a = Table(title="Company A 的數據")
        table_a.add_column("用戶名", style="cyan")
        table_a.add_column("郵箱", style="green")

        for obj in response_a.objects:
            table_a.add_row(
                obj.properties["username"],
                obj.properties["email"]
            )

        console.print(table_a)

        # 查詢 Company B 的數據
        console.print("\n[yellow]查詢 Company B 的數據:[/yellow]")
        user_data_b = client.collections.get("UserData").with_tenant("company_b")

        response_b = user_data_b.query.fetch_objects(limit=10)

        table_b = Table(title="Company B 的數據")
        table_b.add_column("用戶名", style="cyan")
        table_b.add_column("郵箱", style="green")

        for obj in response_b.objects:
            table_b.add_row(
                obj.properties["username"],
                obj.properties["email"]
            )

        console.print(table_b)
        console.print()

    except Exception as e:
        console.print(f"[red]✗ 查詢失敗: {e}[/red]")


def search_within_tenant(client):
    """在特定租戶內搜索"""
    console.print("[bold cyan]6. 在特定租戶內搜索[/bold cyan]")

    try:
        # 在 Company A 中搜索
        console.print("[yellow]在 Company A 中搜索 '項目':[/yellow]\n")
        user_data_a = client.collections.get("UserData").with_tenant("company_a")

        response = user_data_a.query.near_text(
            query="項目",
            limit=5
        )

        console.print("[bold]搜索結果:[/bold]")
        for i, obj in enumerate(response.objects, 1):
            console.print(f"{i}. {obj.properties['username']}: {obj.properties['data'][:50]}...")

        console.print()

    except Exception as e:
        console.print(f"[red]✗ 搜索失敗: {e}[/red]")


def tenant_statistics(client):
    """租戶統計信息"""
    console.print("[bold cyan]7. 租戶統計信息[/bold cyan]")

    try:
        tenants = ["company_a", "company_b", "company_c"]

        table = Table(title="各租戶統計")
        table.add_column("租戶", style="cyan")
        table.add_column("對象數量", style="green")

        for tenant_name in tenants:
            user_data = client.collections.get("UserData").with_tenant(tenant_name)

            # 獲取對象數量
            result = user_data.aggregate.over_all(total_count=True)
            count = result.total_count

            table.add_row(tenant_name, str(count))

        console.print(table)
        console.print()

    except Exception as e:
        console.print(f"[red]✗ 統計失敗: {e}[/red]")


def update_tenant_status(client):
    """更新租戶狀態"""
    console.print("[bold cyan]8. 更新租戶狀態[/bold cyan]")

    try:
        user_data = client.collections.get("UserData")

        # 停用租戶 (實際上是設置為 INACTIVE 狀態)
        console.print("[yellow]演示租戶狀態管理...[/yellow]")

        # 注意: 實際的租戶停用/激活API可能因版本而異
        # 這裡展示概念

        console.print("[green]✓ 租戶可以在需要時停用或重新激活[/green]")
        console.print("[dim]停用的租戶數據會被保留但不可訪問[/dim]\n")

    except Exception as e:
        console.print(f"[red]✗ 更新狀態失敗: {e}[/red]")


def delete_tenant(client):
    """刪除租戶"""
    console.print("[bold cyan]9. 刪除租戶[/bold cyan]")

    try:
        user_data = client.collections.get("UserData")

        # 刪除 Company C
        console.print("[yellow]刪除 Company C 租戶...[/yellow]")

        user_data.tenants.remove(["company_c"])

        console.print("[green]✓ Company C 租戶已刪除[/green]")
        console.print("[dim]該租戶的所有數據已被永久刪除[/dim]\n")

        # 驗證刪除
        remaining_tenants = user_data.tenants.get()
        console.print("[bold]剩餘租戶:[/bold]")
        for tenant in remaining_tenants:
            console.print(f"  • {tenant.name}")

        console.print()

    except Exception as e:
        console.print(f"[red]✗ 刪除租戶失敗: {e}[/red]")


def multi_tenancy_best_practices():
    """多租戶最佳實踐"""
    console.print("[bold cyan]10. 多租戶最佳實踐[/bold cyan]")

    practices = [
        ("租戶命名", "使用一致的命名規範,如公司ID或組織標識"),
        ("數據隔離", "確保絕對的數據隔離,防止跨租戶訪問"),
        ("資源配額", "為每個租戶設置合理的資源限制"),
        ("性能監控", "分別監控各租戶的性能和使用情況"),
        ("備份策略", "可以按租戶進行備份和恢復"),
        ("訪問控制", "實施嚴格的租戶級別訪問控制"),
        ("成本分攤", "追蹤各租戶的資源使用,便於成本分攤"),
        ("擴展規劃", "規劃租戶數量增長時的擴展策略"),
    ]

    table = Table(title="多租戶最佳實踐")
    table.add_column("主題", style="cyan", width=15)
    table.add_column("建議", style="green", width=45)

    for topic, advice in practices:
        table.add_row(topic, advice)

    console.print(table)


def cleanup(client):
    """清理資源"""
    try:
        console.print("\n[cyan]清理資源...[/cyan]")
        if client.collections.exists("UserData"):
            client.collections.delete("UserData")
            console.print("[dim]✓ 已刪除 UserData 集合[/dim]")
        client.close()
    except Exception as e:
        console.print(f"[red]清理失敗: {e}[/red]")


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Weaviate 多租戶示例[/bold cyan]",
        border_style="cyan"
    ))

    client = connect_client()
    if not client:
        return

    try:
        # 1. 創建多租戶集合
        create_multi_tenant_collection(client)

        # 2. 創建租戶
        create_tenants(client)

        # 3. 列出租戶
        list_tenants(client)

        # 4. 插入租戶數據
        insert_tenant_data(client)

        # 5. 查詢租戶數據
        query_tenant_data(client)

        # 6. 在租戶內搜索
        search_within_tenant(client)

        # 7. 租戶統計
        tenant_statistics(client)

        # 8. 更新租戶狀態
        update_tenant_status(client)

        # 9. 刪除租戶
        delete_tenant(client)

        # 10. 最佳實踐
        multi_tenancy_best_practices()

        console.print("="*60)
        console.print("[bold green]✓ 多租戶示例完成！[/bold green]")

    except Exception as e:
        console.print(f"[red]錯誤: {e}[/red]")
    finally:
        cleanup(client)


if __name__ == "__main__":
    main()

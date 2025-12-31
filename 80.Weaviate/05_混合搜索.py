"""
Weaviate 混合搜索示例

本示例展示：
1. 混合搜索基礎
2. Alpha 參數調整
3. BM25 關鍵字搜索
4. 混合搜索最佳實踐
"""

import weaviate
from weaviate.classes.config import Configure, Property, DataType
from weaviate.classes.query import MetadataQuery, HybridFusion
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def setup_test_data(client):
    """設置測試數據"""
    console.print("[cyan]設置測試數據...[/cyan]")

    try:
        if client.collections.exists("Product"):
            client.collections.delete("Product")

        client.collections.create(
            name="Product",
            properties=[
                Property(name="name", data_type=DataType.TEXT),
                Property(name="description", data_type=DataType.TEXT),
                Property(name="category", data_type=DataType.TEXT),
                Property(name="brand", data_type=DataType.TEXT),
                Property(name="price", data_type=DataType.NUMBER),
            ],
            vectorizer_config=Configure.Vectorizer.text2vec_openai(),
            inverted_index_config=Configure.inverted_index(
                bm25_b=0.75,
                bm25_k1=1.2
            )
        )

        products = client.collections.get("Product")

        test_products = [
            {
                "name": "iPhone 15 Pro",
                "description": "最新款蘋果智能手機,配備A17仿生芯片,鈦金屬設計,專業級相機系統",
                "category": "智能手機",
                "brand": "Apple",
                "price": 999
            },
            {
                "name": "MacBook Pro M3",
                "description": "強大的專業級筆記本電腦,搭載M3芯片,Retina顯示屏,適合創作者",
                "category": "筆記本電腦",
                "brand": "Apple",
                "price": 1999
            },
            {
                "name": "iPad Air",
                "description": "輕薄的平板電腦,支持Apple Pencil,適合工作和娛樂",
                "category": "平板電腦",
                "brand": "Apple",
                "price": 599
            },
            {
                "name": "Samsung Galaxy S24",
                "description": "三星旗艦手機,120Hz AMOLED屏幕,強大的相機系統,AI功能",
                "category": "智能手機",
                "brand": "Samsung",
                "price": 899
            },
            {
                "name": "Dell XPS 15",
                "description": "高性能Windows筆記本,InfinityEdge顯示屏,適合專業工作",
                "category": "筆記本電腦",
                "brand": "Dell",
                "price": 1499
            },
            {
                "name": "Sony WH-1000XM5",
                "description": "業界領先的降噪耳機,出色的音質,長達30小時續航",
                "category": "耳機",
                "brand": "Sony",
                "price": 399
            },
            {
                "name": "AirPods Pro",
                "description": "蘋果無線降噪耳機,主動降噪,空間音頻,無縫連接Apple設備",
                "category": "耳機",
                "brand": "Apple",
                "price": 249
            },
            {
                "name": "Kindle Paperwhite",
                "description": "電子書閱讀器,防水設計,可調節暖光,長達10週續航",
                "category": "電子閱讀器",
                "brand": "Amazon",
                "price": 139
            },
        ]

        with products.batch.dynamic() as batch:
            for product in test_products:
                batch.add_object(properties=product)

        console.print(f"[green]✓ 已插入 {len(test_products)} 個產品[/green]\n")

    except Exception as e:
        console.print(f"[red]✗ 設置失敗: {e}[/red]")


def basic_hybrid_search(client):
    """基本混合搜索"""
    console.print("[bold cyan]1. 基本混合搜索[/bold cyan]")

    try:
        products = client.collections.get("Product")

        query = "專業工作筆記本"
        console.print(f"[yellow]查詢: {query}[/yellow]\n")

        response = products.query.hybrid(
            query=query,
            limit=5,
            return_metadata=MetadataQuery(score=True)
        )

        table = Table(title="混合搜索結果")
        table.add_column("產品", style="cyan", width=20)
        table.add_column("品牌", style="green", width=10)
        table.add_column("分類", style="yellow", width=15)
        table.add_column("分數", style="magenta", width=10)

        for obj in response.objects:
            score = obj.metadata.score if obj.metadata.score else 0
            table.add_row(
                obj.properties["name"],
                obj.properties["brand"],
                obj.properties["category"],
                f"{score:.4f}"
            )

        console.print(table)
        console.print()

    except Exception as e:
        console.print(f"[red]✗ 搜索失敗: {e}[/red]")


def alpha_comparison(client):
    """Alpha 參數對比"""
    console.print("[bold cyan]2. Alpha 參數對比[/bold cyan]")
    console.print("[dim]Alpha=0: 純BM25, Alpha=0.5: 混合, Alpha=1: 純向量[/dim]\n")

    try:
        products = client.collections.get("Product")
        query = "Apple"

        alphas = [0.0, 0.5, 1.0]

        for alpha in alphas:
            console.print(f"[yellow]Alpha = {alpha}:[/yellow]")

            response = products.query.hybrid(
                query=query,
                alpha=alpha,
                limit=3,
                return_metadata=MetadataQuery(score=True)
            )

            for i, obj in enumerate(response.objects, 1):
                score = obj.metadata.score if obj.metadata.score else 0
                console.print(f"  {i}. {obj.properties['name']} (分數: {score:.4f})")

            console.print()

    except Exception as e:
        console.print(f"[red]✗ 搜索失敗: {e}[/red]")


def bm25_keyword_search(client):
    """BM25 關鍵字搜索"""
    console.print("[bold cyan]3. BM25 關鍵字搜索[/bold cyan]")

    try:
        products = client.collections.get("Product")

        query = "降噪耳機"
        console.print(f"[yellow]查詢: {query}[/yellow]\n")

        response = products.query.bm25(
            query=query,
            limit=5,
            return_metadata=MetadataQuery(score=True)
        )

        console.print("[bold]BM25 搜索結果:[/bold]")
        for i, obj in enumerate(response.objects, 1):
            score = obj.metadata.score if obj.metadata.score else 0
            console.print(f"{i}. [cyan]{obj.properties['name']}[/cyan]")
            console.print(f"   {obj.properties['description'][:60]}...")
            console.print(f"   BM25 分數: {score:.4f}\n")

    except Exception as e:
        console.print(f"[red]✗ 搜索失敗: {e}[/red]")


def hybrid_with_filters(client):
    """混合搜索 + 過濾器"""
    console.print("[bold cyan]4. 混合搜索 + 過濾器[/bold cyan]")

    try:
        products = client.collections.get("Product")
        from weaviate.classes.query import Filter

        query = "最新產品"
        console.print(f"[yellow]查詢: {query} (僅Apple品牌)[/yellow]\n")

        response = products.query.hybrid(
            query=query,
            alpha=0.5,
            limit=5,
            filters=Filter.by_property("brand").equal("Apple"),
            return_metadata=MetadataQuery(score=True)
        )

        table = Table(title="Apple 產品搜索結果")
        table.add_column("產品", style="cyan")
        table.add_column("分類", style="green")
        table.add_column("價格", style="yellow")
        table.add_column("分數", style="magenta")

        for obj in response.objects:
            score = obj.metadata.score if obj.metadata.score else 0
            table.add_row(
                obj.properties["name"],
                obj.properties["category"],
                f"${obj.properties['price']}",
                f"{score:.4f}"
            )

        console.print(table)
        console.print()

    except Exception as e:
        console.print(f"[red]✗ 搜索失敗: {e}[/red]")


def hybrid_fusion_comparison(client):
    """混合融合算法對比"""
    console.print("[bold cyan]5. 混合融合算法對比[/bold cyan]")

    try:
        products = client.collections.get("Product")
        query = "專業筆記本"

        # Ranked Fusion (默認)
        console.print("[yellow]Ranked Fusion (默認):[/yellow]")
        response_ranked = products.query.hybrid(
            query=query,
            fusion_type=HybridFusion.RANKED,
            limit=3,
            return_metadata=MetadataQuery(score=True)
        )

        for i, obj in enumerate(response_ranked.objects, 1):
            score = obj.metadata.score if obj.metadata.score else 0
            console.print(f"  {i}. {obj.properties['name']} (分數: {score:.4f})")

        console.print()

        # Relative Score Fusion
        console.print("[yellow]Relative Score Fusion:[/yellow]")
        response_relative = products.query.hybrid(
            query=query,
            fusion_type=HybridFusion.RELATIVE_SCORE,
            limit=3,
            return_metadata=MetadataQuery(score=True)
        )

        for i, obj in enumerate(response_relative.objects, 1):
            score = obj.metadata.score if obj.metadata.score else 0
            console.print(f"  {i}. {obj.properties['name']} (分數: {score:.4f})")

        console.print()

    except Exception as e:
        console.print(f"[red]✗ 搜索失敗: {e}[/red]")


def search_by_properties(client):
    """指定屬性搜索"""
    console.print("[bold cyan]6. 指定屬性搜索[/bold cyan]")

    try:
        products = client.collections.get("Product")

        query = "強大"
        console.print(f"[yellow]查詢: {query} (僅在description中搜索)[/yellow]\n")

        response = products.query.hybrid(
            query=query,
            query_properties=["description"],  # 只在描述中搜索
            limit=5,
            return_metadata=MetadataQuery(score=True)
        )

        for i, obj in enumerate(response.objects, 1):
            score = obj.metadata.score if obj.metadata.score else 0
            console.print(f"{i}. [cyan]{obj.properties['name']}[/cyan] (分數: {score:.4f})")
            console.print(f"   {obj.properties['description']}\n")

    except Exception as e:
        console.print(f"[red]✗ 搜索失敗: {e}[/red]")


def best_practices():
    """混合搜索最佳實踐"""
    console.print("[bold cyan]7. 混合搜索最佳實踐[/bold cyan]")

    practices = [
        ("Alpha 選擇", "0.5為平衡點,根據實際需求調整"),
        ("關鍵字查詢", "精確匹配用BM25(alpha=0)"),
        ("語義查詢", "概念性查詢用向量(alpha=1)"),
        ("混合場景", "結合精確和語義用混合(alpha=0.5)"),
        ("性能優化", "限制limit數量,使用過濾器減少搜索空間"),
        ("索引配置", "調整BM25參數(b, k1)優化關鍵字搜索"),
        ("融合算法", "大多數情況使用RANKED,特殊需求用RELATIVE_SCORE"),
    ]

    table = Table(title="混合搜索最佳實踐")
    table.add_column("場景", style="cyan", width=15)
    table.add_column("建議", style="green", width=45)

    for scenario, advice in practices:
        table.add_row(scenario, advice)

    console.print(table)


def cleanup(client):
    """清理資源"""
    try:
        if client.collections.exists("Product"):
            client.collections.delete("Product")
        client.close()
    except Exception as e:
        console.print(f"[red]清理失敗: {e}[/red]")


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Weaviate 混合搜索示例[/bold cyan]",
        border_style="cyan"
    ))

    try:
        client = weaviate.connect_to_local()
        console.print("[green]✓ 已連接到 Weaviate[/green]\n")

        # 設置測試數據
        setup_test_data(client)

        # 1. 基本混合搜索
        basic_hybrid_search(client)

        # 2. Alpha 參數對比
        alpha_comparison(client)

        # 3. BM25 搜索
        bm25_keyword_search(client)

        # 4. 混合搜索 + 過濾器
        hybrid_with_filters(client)

        # 5. 融合算法對比
        hybrid_fusion_comparison(client)

        # 6. 指定屬性搜索
        search_by_properties(client)

        # 7. 最佳實踐
        best_practices()

        console.print("\n" + "="*60)
        console.print("[bold green]✓ 混合搜索示例完成！[/bold green]")

    except Exception as e:
        console.print(f"[red]錯誤: {e}[/red]")
    finally:
        cleanup(client)


if __name__ == "__main__":
    main()

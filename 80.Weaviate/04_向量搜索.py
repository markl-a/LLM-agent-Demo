"""
Weaviate 向量搜索示例

本示例展示：
1. Near Text 語義搜索
2. Near Vector 向量搜索
3. Near Object 基於對象的搜索
4. 調整搜索參數
"""

import weaviate
from weaviate.classes.config import Configure, Property, DataType
from weaviate.classes.query import MetadataQuery
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import numpy as np

console = Console()


def connect_and_setup(client):
    """連接並設置測試數據"""
    console.print("[cyan]設置測試環境...[/cyan]")

    try:
        # 刪除已存在的集合
        if client.collections.exists("Article"):
            client.collections.delete("Article")

        # 創建集合
        client.collections.create(
            name="Article",
            properties=[
                Property(name="title", data_type=DataType.TEXT),
                Property(name="content", data_type=DataType.TEXT),
                Property(name="category", data_type=DataType.TEXT),
                Property(name="author", data_type=DataType.TEXT),
            ],
            vectorizer_config=Configure.Vectorizer.text2vec_openai()
        )

        # 插入測試數據
        articles = client.collections.get("Article")

        test_data = [
            {
                "title": "深度學習入門指南",
                "content": "深度學習是機器學習的一個分支,使用神經網絡來學習數據的表示。它在圖像識別、自然語言處理等領域取得了突破性進展。",
                "category": "AI",
                "author": "張三"
            },
            {
                "title": "Python 數據分析實戰",
                "content": "Python 是數據科學的首選語言,配合 Pandas、NumPy 等庫,可以高效地進行數據處理和分析。",
                "category": "編程",
                "author": "李四"
            },
            {
                "title": "機器學習算法詳解",
                "content": "機器學習包括監督學習、非監督學習和強化學習。常見算法有決策樹、隨機森林、支持向量機等。",
                "category": "AI",
                "author": "王五"
            },
            {
                "title": "Web 開發最佳實踐",
                "content": "現代 Web 開發需要掌握前端框架如 React、Vue,後端技術如 Node.js、Django,以及數據庫設計。",
                "category": "Web",
                "author": "趙六"
            },
            {
                "title": "自然語言處理技術",
                "content": "NLP 是 AI 的重要分支,涵蓋文本分類、情感分析、機器翻譯、問答系統等任務。Transformer 模型帶來了革命性變化。",
                "category": "AI",
                "author": "錢七"
            },
            {
                "title": "Docker 容器化部署",
                "content": "Docker 通過容器化技術,讓應用部署變得簡單。配合 Kubernetes 可以實現大規模容器編排。",
                "category": "DevOps",
                "author": "孫八"
            },
            {
                "title": "計算機視覺應用",
                "content": "計算機視覺使用深度學習處理圖像和視頻,應用於人臉識別、目標檢測、圖像分割等場景。",
                "category": "AI",
                "author": "周九"
            },
            {
                "title": "數據庫優化技巧",
                "content": "數據庫性能優化包括索引設計、查詢優化、分區策略等。合理使用緩存也能顯著提升性能。",
                "category": "數據庫",
                "author": "吳十"
            },
        ]

        with articles.batch.dynamic() as batch:
            for article in test_data:
                batch.add_object(properties=article)

        console.print(f"[green]✓ 已插入 {len(test_data)} 篇文章[/green]\n")

    except Exception as e:
        console.print(f"[red]✗ 設置失敗: {e}[/red]")


def near_text_search(client):
    """Near Text 語義搜索"""
    console.print("[bold cyan]1. Near Text 語義搜索[/bold cyan]")

    try:
        articles = client.collections.get("Article")

        # 搜索相關文章
        query = "學習人工智能和神經網絡"
        console.print(f"[yellow]查詢: {query}[/yellow]\n")

        response = articles.query.near_text(
            query=query,
            limit=3,
            return_metadata=MetadataQuery(distance=True)
        )

        # 顯示結果
        table = Table(title="搜索結果")
        table.add_column("標題", style="cyan", width=25)
        table.add_column("分類", style="green", width=10)
        table.add_column("距離", style="yellow", width=10)

        for obj in response.objects:
            distance = obj.metadata.distance if obj.metadata.distance else 0
            table.add_row(
                obj.properties["title"],
                obj.properties["category"],
                f"{distance:.4f}"
            )

        console.print(table)

        # 顯示最相關的內容
        if response.objects:
            best_match = response.objects[0]
            console.print(f"\n[bold]最相關文章:[/bold]")
            console.print(f"[cyan]{best_match.properties['title']}[/cyan]")
            console.print(f"{best_match.properties['content'][:100]}...\n")

    except Exception as e:
        console.print(f"[red]✗ 搜索失敗: {e}[/red]")


def near_vector_search(client):
    """Near Vector 向量搜索"""
    console.print("[bold cyan]2. Near Vector 向量搜索[/bold cyan]")

    try:
        articles = client.collections.get("Article")

        # 首先獲取一個文章的向量
        sample_response = articles.query.fetch_objects(
            limit=1,
            return_metadata=MetadataQuery(vector=True)
        )

        if not sample_response.objects:
            console.print("[yellow]沒有找到對象[/yellow]")
            return

        # 使用第一個對象的向量進行搜索
        sample_vector = sample_response.objects[0].vector["default"]

        console.print("[yellow]使用提取的向量進行搜索...[/yellow]\n")

        response = articles.query.near_vector(
            near_vector=sample_vector,
            limit=3,
            return_metadata=MetadataQuery(distance=True)
        )

        # 顯示結果
        for i, obj in enumerate(response.objects, 1):
            distance = obj.metadata.distance if obj.metadata.distance else 0
            console.print(f"[cyan]結果 {i}:[/cyan] {obj.properties['title']}")
            console.print(f"  距離: {distance:.4f}")
            console.print(f"  分類: {obj.properties['category']}\n")

    except Exception as e:
        console.print(f"[red]✗ 搜索失敗: {e}[/red]")


def near_object_search(client):
    """Near Object 基於對象的搜索"""
    console.print("[bold cyan]3. Near Object 搜索[/bold cyan]")

    try:
        articles = client.collections.get("Article")

        # 首先找到一個特定的文章
        initial_response = articles.query.fetch_objects(limit=1)

        if not initial_response.objects:
            console.print("[yellow]沒有找到對象[/yellow]")
            return

        # 獲取第一個對象的 UUID
        reference_uuid = initial_response.objects[0].uuid
        reference_title = initial_response.objects[0].properties["title"]

        console.print(f"[yellow]基於文章搜索相似內容:[/yellow]")
        console.print(f"[dim]參考文章: {reference_title}[/dim]\n")

        # 使用 near_object 搜索相似文章
        response = articles.query.near_object(
            near_object=reference_uuid,
            limit=4,  # 包括自己
            return_metadata=MetadataQuery(distance=True)
        )

        # 顯示結果（跳過第一個,因為它是自己）
        console.print("[bold]相似文章:[/bold]")
        for obj in response.objects[1:]:
            distance = obj.metadata.distance if obj.metadata.distance else 0
            console.print(f"  • {obj.properties['title']} (距離: {distance:.4f})")

    except Exception as e:
        console.print(f"[red]✗ 搜索失敗: {e}[/red]")


def search_with_certainty(client):
    """使用確定性閾值搜索"""
    console.print("\n[bold cyan]4. 使用確定性閾值搜索[/bold cyan]")

    try:
        articles = client.collections.get("Article")

        query = "機器學習"
        certainty = 0.7  # 只返回確定性 > 0.7 的結果

        console.print(f"[yellow]查詢: {query}[/yellow]")
        console.print(f"[yellow]最小確定性: {certainty}[/yellow]\n")

        response = articles.query.near_text(
            query=query,
            certainty=certainty,  # 設置確定性閾值
            limit=5,
            return_metadata=MetadataQuery(certainty=True, distance=True)
        )

        if not response.objects:
            console.print("[yellow]沒有找到符合條件的結果[/yellow]")
            return

        # 顯示結果
        table = Table(title=f"確定性 > {certainty} 的結果")
        table.add_column("標題", style="cyan")
        table.add_column("確定性", style="green")
        table.add_column("距離", style="yellow")

        for obj in response.objects:
            certainty_val = obj.metadata.certainty if obj.metadata.certainty else 0
            distance_val = obj.metadata.distance if obj.metadata.distance else 0
            table.add_row(
                obj.properties["title"],
                f"{certainty_val:.4f}",
                f"{distance_val:.4f}"
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]✗ 搜索失敗: {e}[/red]")


def search_with_filters(client):
    """結合過濾器的向量搜索"""
    console.print("\n[bold cyan]5. 結合過濾器的向量搜索[/bold cyan]")

    try:
        articles = client.collections.get("Article")
        from weaviate.classes.query import Filter

        query = "技術"
        console.print(f"[yellow]查詢: {query} (僅限 AI 分類)[/yellow]\n")

        response = articles.query.near_text(
            query=query,
            limit=5,
            filters=Filter.by_property("category").equal("AI"),  # 只搜索 AI 分類
            return_metadata=MetadataQuery(distance=True)
        )

        # 顯示結果
        console.print("[bold]AI 分類的搜索結果:[/bold]")
        for i, obj in enumerate(response.objects, 1):
            distance = obj.metadata.distance if obj.metadata.distance else 0
            console.print(f"{i}. {obj.properties['title']}")
            console.print(f"   分類: {obj.properties['category']}, 距離: {distance:.4f}")

    except Exception as e:
        console.print(f"[red]✗ 搜索失敗: {e}[/red]")


def multi_target_search(client):
    """多目標向量搜索"""
    console.print("\n[bold cyan]6. 多目標向量搜索[/bold cyan]")

    try:
        articles = client.collections.get("Article")

        # 搜索多個概念
        concepts = ["機器學習", "數據分析"]
        console.print(f"[yellow]搜索概念: {', '.join(concepts)}[/yellow]\n")

        response = articles.query.near_text(
            query=concepts,  # 可以傳入多個查詢
            limit=5,
            return_metadata=MetadataQuery(distance=True)
        )

        # 顯示結果
        for i, obj in enumerate(response.objects, 1):
            distance = obj.metadata.distance if obj.metadata.distance else 0
            console.print(f"{i}. [cyan]{obj.properties['title']}[/cyan]")
            console.print(f"   {obj.properties['content'][:80]}...")
            console.print(f"   距離: {distance:.4f}\n")

    except Exception as e:
        console.print(f"[red]✗ 搜索失敗: {e}[/red]")


def search_with_additional_properties(client):
    """返回額外屬性和元數據"""
    console.print("\n[bold cyan]7. 返回額外屬性和元數據[/bold cyan]")

    try:
        articles = client.collections.get("Article")

        response = articles.query.near_text(
            query="深度學習",
            limit=2,
            return_metadata=MetadataQuery(
                distance=True,
                certainty=True,
                creation_time=True,
                last_update_time=True
            )
        )

        # 顯示詳細信息
        for i, obj in enumerate(response.objects, 1):
            console.print(f"\n[bold cyan]結果 {i}:[/bold cyan]")
            console.print(f"標題: {obj.properties['title']}")
            console.print(f"作者: {obj.properties['author']}")

            if obj.metadata:
                console.print(f"\n[dim]元數據:[/dim]")
                if obj.metadata.distance:
                    console.print(f"  距離: {obj.metadata.distance:.4f}")
                if obj.metadata.certainty:
                    console.print(f"  確定性: {obj.metadata.certainty:.4f}")
                if obj.metadata.creation_time:
                    console.print(f"  創建時間: {obj.metadata.creation_time}")

    except Exception as e:
        console.print(f"[red]✗ 搜索失敗: {e}[/red]")


def cleanup(client):
    """清理資源"""
    try:
        if client.collections.exists("Article"):
            client.collections.delete("Article")
        client.close()
    except Exception as e:
        console.print(f"[red]清理失敗: {e}[/red]")


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Weaviate 向量搜索示例[/bold cyan]",
        border_style="cyan"
    ))

    try:
        client = weaviate.connect_to_local()
        console.print("[green]✓ 已連接到 Weaviate[/green]\n")

        # 設置測試數據
        connect_and_setup(client)

        # 1. Near Text 搜索
        near_text_search(client)
        console.print()

        # 2. Near Vector 搜索
        near_vector_search(client)
        console.print()

        # 3. Near Object 搜索
        near_object_search(client)

        # 4. 確定性閾值搜索
        search_with_certainty(client)

        # 5. 結合過濾器搜索
        search_with_filters(client)

        # 6. 多目標搜索
        multi_target_search(client)

        # 7. 額外屬性
        search_with_additional_properties(client)

        console.print("\n" + "="*60)
        console.print("[bold green]✓ 向量搜索示例完成！[/bold green]")

    except Exception as e:
        console.print(f"[red]錯誤: {e}[/red]")
    finally:
        cleanup(client)


if __name__ == "__main__":
    main()

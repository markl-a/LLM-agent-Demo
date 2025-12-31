"""
Weaviate 快速開始示例

本示例展示：
1. 連接 Weaviate 實例
2. 檢查服務狀態
3. 創建簡單的 Schema
4. 插入和查詢數據
"""

import weaviate
from weaviate.classes.init import Auth
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

console = Console()


def connect_to_weaviate():
    """連接到 Weaviate 實例"""
    try:
        console.print("\n[cyan]正在連接到 Weaviate...[/cyan]")

        # 方式 1: 連接到本地實例
        client = weaviate.connect_to_local(
            host="localhost",
            port=8080,
            grpc_port=50051
        )

        # 方式 2: 連接到 Weaviate Cloud Service (WCS)
        # wcs_url = os.getenv("WEAVIATE_URL")
        # wcs_api_key = os.getenv("WEAVIATE_API_KEY")
        # client = weaviate.connect_to_wcs(
        #     cluster_url=wcs_url,
        #     auth_credentials=Auth.api_key(wcs_api_key)
        # )

        # 方式 3: 自定義連接
        # client = weaviate.connect_to_custom(
        #     http_host="localhost",
        #     http_port=8080,
        #     grpc_host="localhost",
        #     grpc_port=50051,
        # )

        console.print("[green]✓ 成功連接到 Weaviate[/green]")
        return client

    except Exception as e:
        console.print(f"[red]✗ 連接失敗: {e}[/red]")
        console.print("\n[yellow]請確保 Weaviate 正在運行:[/yellow]")
        console.print("  docker run -p 8080:8080 -p 50051:50051 semitechnologies/weaviate:latest")
        return None


def check_service_status(client):
    """檢查 Weaviate 服務狀態"""
    try:
        console.print("\n[cyan]檢查服務狀態...[/cyan]")

        # 檢查是否就緒
        is_ready = client.is_ready()
        console.print(f"[green]✓ 服務就緒: {is_ready}[/green]")

        # 獲取元數據
        meta = client.get_meta()

        # 創建狀態表格
        table = Table(title="Weaviate 服務狀態")
        table.add_column("項目", style="cyan")
        table.add_column("值", style="green")

        table.add_row("版本", meta.get('version', 'N/A'))

        # 顯示已啟用的模塊
        modules = meta.get('modules', {})
        if modules:
            module_names = list(modules.keys())
            table.add_row("已啟用模塊", ", ".join(module_names[:3]))

        console.print(table)
        return True

    except Exception as e:
        console.print(f"[red]✗ 檢查狀態失敗: {e}[/red]")
        return False


def create_simple_schema(client):
    """創建簡單的 Schema"""
    try:
        console.print("\n[cyan]創建 Schema...[/cyan]")

        # 檢查集合是否已存在
        if client.collections.exists("Article"):
            console.print("[yellow]集合 'Article' 已存在,先刪除...[/yellow]")
            client.collections.delete("Article")

        # 創建集合
        from weaviate.classes.config import Configure, Property, DataType

        article_collection = client.collections.create(
            name="Article",
            description="新聞文章集合",
            properties=[
                Property(
                    name="title",
                    data_type=DataType.TEXT,
                    description="文章標題"
                ),
                Property(
                    name="content",
                    data_type=DataType.TEXT,
                    description="文章內容"
                ),
                Property(
                    name="author",
                    data_type=DataType.TEXT,
                    description="作者"
                ),
                Property(
                    name="category",
                    data_type=DataType.TEXT,
                    description="分類"
                ),
            ],
            # 配置向量化器（使用 OpenAI）
            vectorizer_config=Configure.Vectorizer.text2vec_openai(
                model="text-embedding-3-small"
            ),
        )

        console.print("[green]✓ Schema 創建成功[/green]")
        console.print(f"[dim]集合名稱: Article[/dim]")
        console.print(f"[dim]屬性: title, content, author, category[/dim]")

        return True

    except Exception as e:
        console.print(f"[red]✗ 創建 Schema 失敗: {e}[/red]")
        return False


def insert_sample_data(client):
    """插入示例數據"""
    try:
        console.print("\n[cyan]插入示例數據...[/cyan]")

        # 獲取集合
        articles = client.collections.get("Article")

        # 準備示例數據
        sample_articles = [
            {
                "title": "人工智能的未來",
                "content": "人工智能正在改變我們的生活方式,從自動駕駛到醫療診斷,AI 技術的應用越來越廣泛。",
                "author": "張三",
                "category": "科技"
            },
            {
                "title": "機器學習入門指南",
                "content": "機器學習是 AI 的一個重要分支,通過算法讓計算機從數據中學習模式。",
                "author": "李四",
                "category": "教育"
            },
            {
                "title": "深度學習的突破",
                "content": "深度學習在圖像識別、自然語言處理等領域取得了突破性進展。",
                "author": "王五",
                "category": "科技"
            },
            {
                "title": "Python 編程技巧",
                "content": "Python 是數據科學和 AI 開發的首選語言,簡潔而強大。",
                "author": "趙六",
                "category": "編程"
            },
        ]

        # 批量插入數據
        with articles.batch.dynamic() as batch:
            for article in sample_articles:
                batch.add_object(properties=article)

        console.print(f"[green]✓ 成功插入 {len(sample_articles)} 篇文章[/green]")

        return True

    except Exception as e:
        console.print(f"[red]✗ 插入數據失敗: {e}[/red]")
        return False


def query_data(client):
    """查詢數據"""
    try:
        console.print("\n[cyan]查詢數據...[/cyan]")

        # 獲取集合
        articles = client.collections.get("Article")

        # 1. 獲取所有文章
        console.print("\n[bold]1. 獲取所有文章:[/bold]")
        response = articles.query.fetch_objects(limit=5)

        table = Table(title="文章列表")
        table.add_column("標題", style="cyan")
        table.add_column("作者", style="green")
        table.add_column("分類", style="yellow")

        for obj in response.objects:
            table.add_row(
                obj.properties["title"],
                obj.properties["author"],
                obj.properties["category"]
            )

        console.print(table)

        # 2. 語義搜索
        console.print("\n[bold]2. 語義搜索 - '學習 AI':[/bold]")
        response = articles.query.near_text(
            query="學習 AI",
            limit=2
        )

        for i, obj in enumerate(response.objects, 1):
            console.print(f"\n[cyan]結果 {i}:[/cyan]")
            console.print(f"  標題: {obj.properties['title']}")
            console.print(f"  內容: {obj.properties['content'][:50]}...")
            console.print(f"  作者: {obj.properties['author']}")

        # 3. 帶過濾器的查詢
        console.print("\n[bold]3. 過濾查詢 - 分類='科技':[/bold]")
        from weaviate.classes.query import Filter

        response = articles.query.fetch_objects(
            filters=Filter.by_property("category").equal("科技"),
            limit=5
        )

        for obj in response.objects:
            console.print(f"  • {obj.properties['title']} - {obj.properties['author']}")

        return True

    except Exception as e:
        console.print(f"[red]✗ 查詢失敗: {e}[/red]")
        return False


def cleanup(client):
    """清理資源"""
    try:
        console.print("\n[cyan]清理資源...[/cyan]")

        # 刪除集合（可選）
        # if client.collections.exists("Article"):
        #     client.collections.delete("Article")
        #     console.print("[green]✓ 集合已刪除[/green]")

        # 關閉連接
        client.close()
        console.print("[green]✓ 連接已關閉[/green]")

    except Exception as e:
        console.print(f"[red]清理失敗: {e}[/red]")


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Weaviate 快速開始示例[/bold cyan]",
        border_style="cyan"
    ))

    # 1. 連接到 Weaviate
    client = connect_to_weaviate()
    if not client:
        return

    try:
        # 2. 檢查服務狀態
        if not check_service_status(client):
            return

        # 3. 創建 Schema
        if not create_simple_schema(client):
            return

        # 4. 插入示例數據
        if not insert_sample_data(client):
            return

        # 5. 查詢數據
        query_data(client)

        # 完成
        console.print("\n" + "="*60)
        console.print("[bold green]✓ 快速開始示例完成！[/bold green]")
        console.print("\n[cyan]下一步:[/cyan]")
        console.print("  1. 查看 02_Schema設計.py 學習 Schema 設計")
        console.print("  2. 查看 04_向量搜索.py 學習向量搜索")
        console.print("  3. 查看 07_生成式搜索.py 學習 RAG 應用")

    finally:
        # 清理
        cleanup(client)


if __name__ == "__main__":
    main()

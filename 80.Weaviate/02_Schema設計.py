"""
Weaviate Schema 設計示例

本示例展示：
1. Schema 基本概念
2. 創建複雜 Schema
3. 更新和修改 Schema
4. 最佳實踐
"""

import weaviate
from weaviate.classes.config import (
    Configure, Property, DataType,
    Tokenization, VectorDistances
)
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
import json

console = Console()


def connect_client():
    """連接到 Weaviate"""
    try:
        client = weaviate.connect_to_local()
        console.print("[green]✓ 已連接到 Weaviate[/green]")
        return client
    except Exception as e:
        console.print(f"[red]✗ 連接失敗: {e}[/red]")
        return None


def create_basic_schema(client):
    """創建基本 Schema"""
    console.print("\n[bold cyan]1. 創建基本 Schema[/bold cyan]")

    try:
        # 刪除已存在的集合
        if client.collections.exists("Product"):
            client.collections.delete("Product")

        # 創建產品集合
        products = client.collections.create(
            name="Product",
            description="電商產品集合",
            properties=[
                Property(
                    name="name",
                    data_type=DataType.TEXT,
                    description="產品名稱"
                ),
                Property(
                    name="description",
                    data_type=DataType.TEXT,
                    description="產品描述"
                ),
                Property(
                    name="price",
                    data_type=DataType.NUMBER,
                    description="價格"
                ),
                Property(
                    name="inStock",
                    data_type=DataType.BOOL,
                    description="是否有貨"
                ),
            ],
            vectorizer_config=Configure.Vectorizer.text2vec_openai()
        )

        console.print("[green]✓ 基本 Schema 創建成功[/green]")

        # 顯示 Schema 信息
        config = products.config.get()
        console.print(f"[dim]集合名稱: {config.name}[/dim]")
        console.print(f"[dim]屬性數量: {len(config.properties)}[/dim]")

    except Exception as e:
        console.print(f"[red]✗ 創建失敗: {e}[/red]")


def create_advanced_schema(client):
    """創建進階 Schema"""
    console.print("\n[bold cyan]2. 創建進階 Schema[/bold cyan]")

    try:
        # 刪除已存在的集合
        if client.collections.exists("BlogPost"):
            client.collections.delete("BlogPost")

        # 創建部落格文章集合（更複雜的配置）
        blog_post = client.collections.create(
            name="BlogPost",
            description="部落格文章集合",
            properties=[
                Property(
                    name="title",
                    data_type=DataType.TEXT,
                    description="文章標題",
                    tokenization=Tokenization.WORD,  # 詞級分詞
                    index_filterable=True,  # 可用於過濾
                    index_searchable=True   # 可用於搜索
                ),
                Property(
                    name="content",
                    data_type=DataType.TEXT,
                    description="文章內容",
                    tokenization=Tokenization.WORD
                ),
                Property(
                    name="tags",
                    data_type=DataType.TEXT_ARRAY,
                    description="標籤列表"
                ),
                Property(
                    name="publishDate",
                    data_type=DataType.DATE,
                    description="發布日期"
                ),
                Property(
                    name="viewCount",
                    data_type=DataType.INT,
                    description="瀏覽次數"
                ),
                Property(
                    name="rating",
                    data_type=DataType.NUMBER,
                    description="評分"
                ),
                Property(
                    name="isPublished",
                    data_type=DataType.BOOL,
                    description="是否已發布"
                ),
            ],
            # 配置向量化器
            vectorizer_config=Configure.Vectorizer.text2vec_openai(
                model="text-embedding-3-small",
                vectorize_collection_name=False  # 不向量化集合名稱
            ),
            # 配置向量索引（HNSW）
            vector_index_config=Configure.VectorIndex.hnsw(
                distance_metric=VectorDistances.COSINE,  # 餘弦相似度
                ef=-1,  # 動態 ef
                ef_construction=128,  # 構建參數
                max_connections=64,  # 每個節點最大連接數
            ),
            # 配置倒排索引
            inverted_index_config=Configure.inverted_index(
                bm25_b=0.75,  # BM25 參數 b
                bm25_k1=1.2,  # BM25 參數 k1
                index_null_state=True,  # 索引 null 值
                index_property_length=True,  # 索引屬性長度
                index_timestamps=True  # 索引時間戳
            ),
        )

        console.print("[green]✓ 進階 Schema 創建成功[/green]")

        # 顯示詳細配置
        config = blog_post.config.get()

        table = Table(title="BlogPost Schema 配置")
        table.add_column("配置項", style="cyan")
        table.add_column("值", style="green")

        table.add_row("集合名稱", config.name)
        table.add_row("向量化器", str(config.vectorizer_config))
        table.add_row("向量距離", str(config.vector_index_config.distance_metric))
        table.add_row("屬性數量", str(len(config.properties)))

        console.print(table)

    except Exception as e:
        console.print(f"[red]✗ 創建失敗: {e}[/red]")


def create_multi_vectorizer_schema(client):
    """創建多向量化器 Schema"""
    console.print("\n[bold cyan]3. 創建多向量化器 Schema[/bold cyan]")

    try:
        # 刪除已存在的集合
        if client.collections.exists("Document"):
            client.collections.delete("Document")

        # 創建文檔集合（命名向量）
        from weaviate.classes.config import Configure

        document = client.collections.create(
            name="Document",
            description="支持多向量的文檔集合",
            properties=[
                Property(
                    name="title",
                    data_type=DataType.TEXT,
                    description="文檔標題"
                ),
                Property(
                    name="content",
                    data_type=DataType.TEXT,
                    description="文檔內容"
                ),
                Property(
                    name="summary",
                    data_type=DataType.TEXT,
                    description="文檔摘要"
                ),
            ],
            # 配置多個命名向量
            vectorizer_config=[
                Configure.NamedVectors.text2vec_openai(
                    name="title_vector",
                    source_properties=["title"],
                    model="text-embedding-3-small"
                ),
                Configure.NamedVectors.text2vec_openai(
                    name="content_vector",
                    source_properties=["content"],
                    model="text-embedding-3-large"
                ),
            ]
        )

        console.print("[green]✓ 多向量化器 Schema 創建成功[/green]")
        console.print("[dim]配置了兩個向量: title_vector, content_vector[/dim]")

    except Exception as e:
        console.print(f"[red]✗ 創建失敗: {e}[/red]")


def create_reference_schema(client):
    """創建帶引用的 Schema"""
    console.print("\n[bold cyan]4. 創建帶引用的 Schema[/bold cyan]")

    try:
        # 刪除已存在的集合
        for collection_name in ["Author", "Book"]:
            if client.collections.exists(collection_name):
                client.collections.delete(collection_name)

        # 創建作者集合
        author = client.collections.create(
            name="Author",
            properties=[
                Property(name="name", data_type=DataType.TEXT),
                Property(name="bio", data_type=DataType.TEXT),
            ],
            vectorizer_config=Configure.Vectorizer.none()  # 不使用向量化
        )

        # 創建書籍集合（引用作者）
        from weaviate.classes.config import ReferenceProperty

        book = client.collections.create(
            name="Book",
            properties=[
                Property(name="title", data_type=DataType.TEXT),
                Property(name="isbn", data_type=DataType.TEXT),
                Property(name="publishYear", data_type=DataType.INT),
            ],
            references=[
                ReferenceProperty(
                    name="hasAuthor",
                    target_collection="Author"
                )
            ],
            vectorizer_config=Configure.Vectorizer.text2vec_openai()
        )

        console.print("[green]✓ 引用 Schema 創建成功[/green]")
        console.print("[dim]Book -> hasAuthor -> Author[/dim]")

        # 插入示例數據
        console.print("\n[yellow]插入示例數據...[/yellow]")

        # 插入作者
        authors_collection = client.collections.get("Author")
        author_uuid = authors_collection.data.insert({
            "name": "金庸",
            "bio": "著名武俠小說作家"
        })

        # 插入書籍並引用作者
        books_collection = client.collections.get("Book")
        books_collection.data.insert(
            properties={
                "title": "射鵰英雄傳",
                "isbn": "978-1234567890",
                "publishYear": 1957
            },
            references={
                "hasAuthor": author_uuid
            }
        )

        console.print("[green]✓ 示例數據插入成功[/green]")

    except Exception as e:
        console.print(f"[red]✗ 創建失敗: {e}[/red]")


def inspect_schema(client):
    """檢查 Schema"""
    console.print("\n[bold cyan]5. 檢查現有 Schema[/bold cyan]")

    try:
        # 獲取所有集合
        collections = client.collections.list_all()

        if not collections:
            console.print("[yellow]沒有找到任何集合[/yellow]")
            return

        # 創建樹狀結構顯示
        tree = Tree("[bold cyan]Weaviate Collections[/bold cyan]")

        for collection_name, config in collections.items():
            collection_node = tree.add(f"[green]{collection_name}[/green]")

            # 添加屬性
            props_node = collection_node.add("[yellow]Properties[/yellow]")
            for prop in config.properties:
                props_node.add(f"{prop.name} ({prop.data_type})")

            # 添加向量配置
            if config.vectorizer_config:
                collection_node.add(f"[blue]Vectorizer: {config.vectorizer_config}[/blue]")

        console.print(tree)

    except Exception as e:
        console.print(f"[red]✗ 檢查失敗: {e}[/red]")


def update_schema(client):
    """更新 Schema"""
    console.print("\n[bold cyan]6. 更新 Schema[/bold cyan]")

    try:
        if not client.collections.exists("Product"):
            console.print("[yellow]Product 集合不存在,跳過更新[/yellow]")
            return

        # 獲取集合
        products = client.collections.get("Product")

        # 添加新屬性
        console.print("[yellow]添加新屬性 'category'...[/yellow]")

        products.config.add_property(
            Property(
                name="category",
                data_type=DataType.TEXT,
                description="產品分類"
            )
        )

        console.print("[green]✓ 屬性添加成功[/green]")

        # 注意: Weaviate 不支持刪除屬性或修改現有屬性
        # 如需這些操作,需要重新創建集合

    except Exception as e:
        console.print(f"[red]✗ 更新失敗: {e}[/red]")


def schema_best_practices():
    """Schema 設計最佳實踐"""
    console.print("\n[bold cyan]7. Schema 設計最佳實踐[/bold cyan]")

    practices = [
        ("命名規範", "使用 PascalCase 命名集合,camelCase 命名屬性"),
        ("數據類型", "選擇合適的數據類型,避免使用 TEXT 存儲數字"),
        ("向量化", "只向量化需要搜索的字段,減少計算成本"),
        ("索引配置", "根據數據規模調整 HNSW 參數"),
        ("引用關係", "合理使用引用,避免過度嵌套"),
        ("性能考慮", "大規模數據考慮分片策略"),
        ("版本管理", "Schema 變更需要規劃遷移策略"),
    ]

    table = Table(title="Schema 設計最佳實踐")
    table.add_column("項目", style="cyan")
    table.add_column("建議", style="green")

    for practice, advice in practices:
        table.add_row(practice, advice)

    console.print(table)


def cleanup(client, keep_data=False):
    """清理資源"""
    try:
        if not keep_data:
            console.print("\n[cyan]清理測試數據...[/cyan]")
            for collection_name in ["Product", "BlogPost", "Document", "Author", "Book"]:
                if client.collections.exists(collection_name):
                    client.collections.delete(collection_name)
                    console.print(f"[dim]✓ 已刪除 {collection_name}[/dim]")

        client.close()
    except Exception as e:
        console.print(f"[red]清理失敗: {e}[/red]")


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Weaviate Schema 設計示例[/bold cyan]",
        border_style="cyan"
    ))

    client = connect_client()
    if not client:
        return

    try:
        # 1. 基本 Schema
        create_basic_schema(client)

        # 2. 進階 Schema
        create_advanced_schema(client)

        # 3. 多向量化器
        create_multi_vectorizer_schema(client)

        # 4. 引用關係
        create_reference_schema(client)

        # 5. 檢查 Schema
        inspect_schema(client)

        # 6. 更新 Schema
        update_schema(client)

        # 7. 最佳實踐
        schema_best_practices()

        console.print("\n" + "="*60)
        console.print("[bold green]✓ Schema 設計示例完成！[/bold green]")
        console.print("\n[cyan]下一步:[/cyan]")
        console.print("  1. 查看 03_數據導入.py 學習數據導入")
        console.print("  2. 查看 04_向量搜索.py 學習向量搜索")

    finally:
        cleanup(client, keep_data=True)


if __name__ == "__main__":
    main()

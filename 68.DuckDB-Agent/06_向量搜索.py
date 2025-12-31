"""
DuckDB-Agent 示例 06: 向量搜索

展示 DuckDB 的向量搜索功能：
1. 向量擴展安裝
2. 向量相似度計算
3. 語義搜索
4. 混合搜索（向量 + 關鍵詞）
5. 文檔嵌入和檢索
6. 實際應用場景
"""

import duckdb
from openai import OpenAI
import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from dotenv import load_dotenv
import json

load_dotenv()

console = Console()


def setup_vector_extension(con):
    """安裝和設置向量擴展"""
    try:
        console.print("\n[bold cyan]安裝向量擴展[/bold cyan]")

        # 安裝 VSS 擴展（向量相似度搜索）
        con.execute("INSTALL vss;")
        con.execute("LOAD vss;")

        console.print("   ✓ 向量擴展安裝成功", style="green")

        # 顯示擴展信息
        extensions = con.execute("""
            SELECT * FROM duckdb_extensions()
            WHERE extension_name = 'vss'
        """).fetchdf()

        if len(extensions) > 0:
            console.print(f"   擴展版本: {extensions['loaded'][0]}", style="yellow")

        return True

    except Exception as e:
        console.print(f"[yellow]⚠ 向量擴展安裝失敗: {e}[/yellow]")
        console.print("[yellow]繼續執行其他示例...[/yellow]")
        return False


def demonstrate_vector_basics(con):
    """展示向量基礎操作"""
    console.print("\n[bold cyan]1. 向量基礎操作[/bold cyan]")

    try:
        # 創建包含向量的表
        con.execute("""
            CREATE TABLE items (
                id INTEGER,
                name VARCHAR,
                description VARCHAR,
                embedding FLOAT[3]  -- 3 維向量示例
            )
        """)

        # 插入帶向量的數據
        con.execute("""
            INSERT INTO items VALUES
            (1, '蘋果', '新鮮的紅蘋果', [0.8, 0.2, 0.1]),
            (2, '香蕉', '黃色的香蕉', [0.3, 0.9, 0.2]),
            (3, '橙子', '多汁的橙子', [0.7, 0.3, 0.4]),
            (4, '葡萄', '紫色的葡萄', [0.2, 0.4, 0.8]),
            (5, '西瓜', '大西瓜', [0.5, 0.5, 0.5])
        """)

        console.print("   ✓ 創建向量數據表", style="green")

        # 查看數據
        result = con.execute("SELECT * FROM items").fetchdf()
        console.print("\n   [yellow]向量數據:[/yellow]")
        console.print(result.to_string(index=False))

    except Exception as e:
        console.print(f"[red]✗ 向量基礎操作失敗: {e}[/red]")
        raise


def demonstrate_similarity_search(con):
    """展示相似度搜索"""
    console.print("\n[bold cyan]2. 向量相似度搜索[/bold cyan]")

    try:
        # 定義查詢向量
        query_vector = [0.75, 0.25, 0.15]  # 類似蘋果的向量

        console.print(f"\n   [yellow]查詢向量:[/yellow] {query_vector}")

        # 計算歐幾里得距離
        console.print("\n   [yellow]歐幾里得距離（越小越相似）:[/yellow]")
        result = con.execute(f"""
            SELECT
                name,
                description,
                embedding,
                array_distance(embedding, {query_vector}::FLOAT[3]) as euclidean_distance
            FROM items
            ORDER BY euclidean_distance
            LIMIT 5
        """).fetchdf()
        console.print(result.to_string(index=False))

        # 計算餘弦相似度
        console.print("\n   [yellow]餘弦相似度（越大越相似）:[/yellow]")
        result = con.execute(f"""
            SELECT
                name,
                description,
                array_cosine_similarity(embedding, {query_vector}::FLOAT[3]) as cosine_similarity
            FROM items
            ORDER BY cosine_similarity DESC
            LIMIT 5
        """).fetchdf()
        console.print(result.to_string(index=False))

        # 內積
        console.print("\n   [yellow]向量內積:[/yellow]")
        result = con.execute(f"""
            SELECT
                name,
                array_inner_product(embedding, {query_vector}::FLOAT[3]) as inner_product
            FROM items
            ORDER BY inner_product DESC
            LIMIT 5
        """).fetchdf()
        console.print(result.to_string(index=False))

    except Exception as e:
        console.print(f"[red]✗ 相似度搜索失敗: {e}[/red]")
        raise


def create_document_embeddings(con, client):
    """創建文檔嵌入"""
    console.print("\n[bold cyan]3. 文檔嵌入和語義搜索[/bold cyan]")

    try:
        # 示例文檔
        documents = [
            {"id": 1, "title": "人工智能入門", "content": "人工智能是計算機科學的一個分支，致力於創建能夠模擬人類智能的系統。"},
            {"id": 2, "title": "機器學習基礎", "content": "機器學習是人工智能的核心技術，通過算法讓計算機從數據中學習。"},
            {"id": 3, "title": "深度學習簡介", "content": "深度學習使用神經網絡來處理複雜的數據模式，在圖像和語音識別中表現出色。"},
            {"id": 4, "title": "自然語言處理", "content": "NLP 使計算機能夠理解、解釋和生成人類語言，是 AI 的重要應用領域。"},
            {"id": 5, "title": "計算機視覺", "content": "計算機視覺讓機器能夠理解和分析視覺信息，應用於自動駕駛和醫療診斷。"},
        ]

        console.print("\n   [yellow]生成文檔嵌入...[/yellow]")

        # 創建表
        con.execute("""
            CREATE TABLE documents (
                id INTEGER,
                title VARCHAR,
                content VARCHAR,
                embedding FLOAT[]
            )
        """)

        # 為每個文檔生成嵌入
        for doc in documents:
            # 使用 OpenAI 生成嵌入
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=doc["content"]
            )

            embedding = response.data[0].embedding

            # 插入數據
            con.execute("""
                INSERT INTO documents (id, title, content, embedding)
                VALUES (?, ?, ?, ?)
            """, [doc["id"], doc["title"], doc["content"], embedding])

            console.print(f"   ✓ {doc['title']}", style="green")

        console.print("\n   ✓ 所有文檔嵌入生成完成", style="green")

        return True

    except Exception as e:
        console.print(f"[yellow]⚠ 文檔嵌入失敗: {e}[/yellow]")
        console.print("[yellow]請確保設置了 OPENAI_API_KEY 環境變量[/yellow]")
        return False


def semantic_search(con, client, query):
    """執行語義搜索"""
    try:
        console.print(f"\n   [yellow]查詢:[/yellow] {query}")

        # 生成查詢嵌入
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=query
        )

        query_embedding = response.data[0].embedding

        # 執行語義搜索
        result = con.execute("""
            SELECT
                title,
                content,
                array_cosine_similarity(embedding, ?::FLOAT[]) as similarity
            FROM documents
            ORDER BY similarity DESC
            LIMIT 3
        """, [query_embedding]).fetchdf()

        console.print("\n   [green]搜索結果:[/green]")
        for idx, row in result.iterrows():
            console.print(f"\n   [{idx + 1}] {row['title']} (相似度: {row['similarity']:.4f})")
            console.print(f"      {row['content']}")

    except Exception as e:
        console.print(f"[red]✗ 語義搜索失敗: {e}[/red]")


def demonstrate_hybrid_search(con):
    """展示混合搜索（向量 + 關鍵詞）"""
    console.print("\n[bold cyan]4. 混合搜索示例[/bold cyan]")

    try:
        # 假設我們有查詢嵌入
        query_vector = [0.1] * 1536  # 示例向量

        console.print("\n   [yellow]混合搜索（相似度 + 關鍵詞過濾）:[/yellow]")

        # 結合向量相似度和關鍵詞過濾
        result = con.execute(f"""
            SELECT
                title,
                content,
                array_cosine_similarity(embedding, {query_vector}::FLOAT[]) as similarity
            FROM documents
            WHERE content LIKE '%機器學習%' OR content LIKE '%深度學習%'
            ORDER BY similarity DESC
            LIMIT 3
        """).fetchdf()

        if len(result) > 0:
            console.print(result.to_string(index=False))
        else:
            console.print("   [yellow]沒有找到匹配的結果[/yellow]")

        # 加權混合（相似度 + 文本匹配分數）
        console.print("\n   [yellow]加權混合搜索:[/yellow]")
        console.print("""
        -- 示例：結合向量相似度和 BM25 文本搜索
        WITH vector_scores AS (
            SELECT
                id,
                title,
                array_cosine_similarity(embedding, query_embedding) as vector_score
            FROM documents
        ),
        text_scores AS (
            SELECT
                id,
                fts_score as text_score
            FROM documents_fts
            WHERE documents_fts MATCH 'query_text'
        )
        SELECT
            d.title,
            v.vector_score,
            t.text_score,
            (v.vector_score * 0.7 + t.text_score * 0.3) as combined_score
        FROM documents d
        JOIN vector_scores v ON d.id = v.id
        LEFT JOIN text_scores t ON d.id = t.id
        ORDER BY combined_score DESC
        LIMIT 10
        """)

    except Exception as e:
        console.print(f"[red]✗ 混合搜索示例失敗: {e}[/red]")


def demonstrate_vector_operations(con):
    """展示向量操作"""
    console.print("\n[bold cyan]5. 向量操作[/bold cyan]")

    try:
        # 向量運算
        console.print("\n   [yellow]向量基礎運算:[/yellow]")

        result = con.execute("""
            SELECT
                name,
                embedding,
                array_size(embedding) as vector_dim,
                -- 向量的模長
                SQRT(array_inner_product(embedding, embedding)) as magnitude
            FROM items
        """).fetchdf()
        console.print(result.to_string(index=False))

        # 向量標準化
        console.print("\n   [yellow]向量標準化:[/yellow]")
        con.execute("""
            CREATE TEMP TABLE normalized_items AS
            SELECT
                id,
                name,
                embedding,
                -- 標準化向量
                list_transform(
                    embedding,
                    x -> x / SQRT(array_inner_product(embedding, embedding))
                ) as normalized_embedding
            FROM items
        """)

        result = con.execute("""
            SELECT
                name,
                normalized_embedding,
                SQRT(array_inner_product(normalized_embedding, normalized_embedding)) as norm
            FROM normalized_items
            LIMIT 3
        """).fetchdf()
        console.print(result.to_string(index=False))

        # 向量聚合
        console.print("\n   [yellow]向量平均（質心）:[/yellow]")
        result = con.execute("""
            SELECT
                list_transform(
                    range(array_size(embedding)),
                    i -> AVG(embedding[i + 1])
                ) as centroid
            FROM items
        """).fetchdf()
        console.print(f"   質心: {result.iloc[0]['centroid']}")

    except Exception as e:
        console.print(f"[red]✗ 向量操作失敗: {e}[/red]")


def demonstrate_practical_applications(con):
    """展示實際應用場景"""
    console.print("\n[bold cyan]6. 實際應用場景[/bold cyan]")

    try:
        console.print("\n   [yellow]應用場景 1: 產品推薦[/yellow]")
        console.print("""
        -- 基於用戶興趣向量找到相似產品
        WITH user_profile AS (
            SELECT [0.8, 0.3, 0.5]::FLOAT[3] as interest_vector
        )
        SELECT
            p.product_name,
            p.category,
            array_cosine_similarity(p.embedding, up.interest_vector) as match_score
        FROM products p, user_profile up
        ORDER BY match_score DESC
        LIMIT 10
        """)

        console.print("\n   [yellow]應用場景 2: 文檔去重[/yellow]")
        console.print("""
        -- 找出相似度高於 0.95 的重複文檔
        SELECT
            d1.id as doc1_id,
            d2.id as doc2_id,
            d1.title,
            d2.title,
            array_cosine_similarity(d1.embedding, d2.embedding) as similarity
        FROM documents d1
        CROSS JOIN documents d2
        WHERE d1.id < d2.id
        AND array_cosine_similarity(d1.embedding, d2.embedding) > 0.95
        ORDER BY similarity DESC
        """)

        console.print("\n   [yellow]應用場景 3: 智能問答[/yellow]")
        console.print("""
        -- 找到與問題最相關的知識庫文章
        WITH question_embedding AS (
            SELECT get_embedding('用戶的問題') as qe
        )
        SELECT
            kb.title,
            kb.answer,
            array_cosine_similarity(kb.embedding, qe.qe) as relevance
        FROM knowledge_base kb, question_embedding qe
        WHERE relevance > 0.7
        ORDER BY relevance DESC
        LIMIT 5
        """)

        console.print("\n   [yellow]應用場景 4: 異常檢測[/yellow]")
        console.print("""
        -- 找出與正常模式差異大的數據點
        WITH normal_pattern AS (
            SELECT
                list_avg(embedding) as avg_embedding
            FROM normal_data
        )
        SELECT
            d.timestamp,
            d.value,
            array_distance(d.embedding, np.avg_embedding) as anomaly_score
        FROM data_points d, normal_pattern np
        WHERE anomaly_score > threshold
        ORDER BY anomaly_score DESC
        """)

        console.print("\n   ✓ 向量搜索應用廣泛", style="green")

    except Exception as e:
        console.print(f"[red]✗ 應用場景示例失敗: {e}[/red]")


def main():
    """主函數"""
    console.print("\n[bold magenta]═══════════════════════════════════════[/bold magenta]")
    console.print("[bold magenta]    DuckDB 向量搜索示例    [/bold magenta]")
    console.print("[bold magenta]═══════════════════════════════════════[/bold magenta]")

    try:
        # 創建數據庫連接
        con = duckdb.connect(':memory:')

        # 1. 安裝向量擴展
        vector_enabled = setup_vector_extension(con)

        # 2. 向量基礎操作
        demonstrate_vector_basics(con)

        # 3. 相似度搜索
        if vector_enabled:
            demonstrate_similarity_search(con)

        # 4. 文檔嵌入（需要 OpenAI API）
        if os.getenv("OPENAI_API_KEY"):
            client = OpenAI()

            if create_document_embeddings(con, client):
                # 執行語義搜索
                console.print("\n[bold cyan]語義搜索示例[/bold cyan]")
                semantic_search(con, client, "如何讓計算機理解語言？")
                semantic_search(con, client, "神經網絡是什麼？")

                # 5. 混合搜索
                demonstrate_hybrid_search(con)
        else:
            console.print("\n[yellow]⚠ 未設置 OPENAI_API_KEY，跳過文檔嵌入示例[/yellow]")

        # 6. 向量操作
        demonstrate_vector_operations(con)

        # 7. 實際應用
        demonstrate_practical_applications(con)

        # 清理
        con.close()

        console.print("\n[bold green]✓ 向量搜索示例執行完成！[/bold green]")
        console.print("\n[yellow]DuckDB 向量搜索優勢:[/yellow]")
        console.print("  - 原生向量數據類型支持")
        console.print("  - 多種距離度量（歐幾里得、餘弦、內積）")
        console.print("  - 與 SQL 無縫集成")
        console.print("  - 高性能向量計算")
        console.print("  - 適合中小規模向量搜索")
        console.print("\n[yellow]注意:[/yellow]")
        console.print("  - 對於大規模向量搜索（百萬級以上），建議使用專門的向量數據庫")
        console.print("  - DuckDB 適合需要結合結構化數據和向量搜索的場景")

    except Exception as e:
        console.print(f"\n[bold red]✗ 執行失敗: {e}[/bold red]")
        raise


if __name__ == "__main__":
    main()

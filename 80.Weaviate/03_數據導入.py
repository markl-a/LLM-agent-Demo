"""
Weaviate 數據導入示例

本示例展示：
1. 單條數據插入
2. 批量數據導入
3. 從文件導入數據
4. 數據驗證和錯誤處理
"""

import weaviate
from weaviate.classes.config import Configure, Property, DataType
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
import json
import pandas as pd
from datetime import datetime, timezone
import time

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


def setup_collection(client):
    """設置測試集合"""
    console.print("\n[cyan]設置測試集合...[/cyan]")

    try:
        # 刪除已存在的集合
        if client.collections.exists("Movie"):
            client.collections.delete("Movie")

        # 創建電影集合
        client.collections.create(
            name="Movie",
            description="電影數據集合",
            properties=[
                Property(name="title", data_type=DataType.TEXT, description="電影標題"),
                Property(name="director", data_type=DataType.TEXT, description="導演"),
                Property(name="genre", data_type=DataType.TEXT_ARRAY, description="類型"),
                Property(name="releaseYear", data_type=DataType.INT, description="上映年份"),
                Property(name="rating", data_type=DataType.NUMBER, description="評分"),
                Property(name="plot", data_type=DataType.TEXT, description="劇情簡介"),
                Property(name="duration", data_type=DataType.INT, description="時長(分鐘)"),
            ],
            vectorizer_config=Configure.Vectorizer.text2vec_openai(
                vectorize_collection_name=False
            )
        )

        console.print("[green]✓ 集合創建成功[/green]")
        return True

    except Exception as e:
        console.print(f"[red]✗ 設置失敗: {e}[/red]")
        return False


def insert_single_object(client):
    """插入單條數據"""
    console.print("\n[bold cyan]1. 插入單條數據[/bold cyan]")

    try:
        movies = client.collections.get("Movie")

        # 插入單部電影
        movie_data = {
            "title": "星際效應",
            "director": "克里斯多福·諾蘭",
            "genre": ["科幻", "冒險"],
            "releaseYear": 2014,
            "rating": 8.6,
            "plot": "一群探險家利用新發現的蟲洞,超越人類對於太空旅行的極限,開始在廣袤的宇宙中進行星際航行。",
            "duration": 169
        }

        uuid = movies.data.insert(properties=movie_data)

        console.print(f"[green]✓ 成功插入電影[/green]")
        console.print(f"[dim]UUID: {uuid}[/dim]")
        console.print(f"[dim]標題: {movie_data['title']}[/dim]")

        return uuid

    except Exception as e:
        console.print(f"[red]✗ 插入失敗: {e}[/red]")
        return None


def insert_with_custom_vector(client):
    """插入帶自定義向量的數據"""
    console.print("\n[bold cyan]2. 插入帶自定義向量的數據[/bold cyan]")

    try:
        movies = client.collections.get("Movie")

        # 模擬一個向量（實際應用中應該使用嵌入模型生成）
        import numpy as np
        custom_vector = np.random.rand(1536).tolist()  # OpenAI ada-002 是 1536 維

        movie_data = {
            "title": "盜夢空間",
            "director": "克里斯多福·諾蘭",
            "genre": ["科幻", "懸疑"],
            "releaseYear": 2010,
            "rating": 8.8,
            "plot": "一個技術高超的盜夢者,通過進入他人夢境竊取機密。",
            "duration": 148
        }

        uuid = movies.data.insert(
            properties=movie_data,
            vector=custom_vector  # 提供自定義向量
        )

        console.print(f"[green]✓ 成功插入帶自定義向量的電影[/green]")
        console.print(f"[dim]UUID: {uuid}[/dim]")

        return uuid

    except Exception as e:
        console.print(f"[red]✗ 插入失敗: {e}[/red]")
        return None


def batch_insert(client):
    """批量插入數據"""
    console.print("\n[bold cyan]3. 批量插入數據[/bold cyan]")

    try:
        movies = client.collections.get("Movie")

        # 準備批量數據
        movie_data = [
            {
                "title": "黑暗騎士",
                "director": "克里斯多福·諾蘭",
                "genre": ["動作", "犯罪", "劇情"],
                "releaseYear": 2008,
                "rating": 9.0,
                "plot": "蝙蝠俠、詹姆斯·戈登警長和哈維·丹特必須合作,打擊威脅整個城市的新威脅:小丑。",
                "duration": 152
            },
            {
                "title": "楚門的世界",
                "director": "彼得·威爾",
                "genre": ["劇情", "科幻"],
                "releaseYear": 1998,
                "rating": 8.2,
                "plot": "一個保險推銷員發現他的整個生活實際上是一個電視實境秀。",
                "duration": 103
            },
            {
                "title": "阿甘正傳",
                "director": "羅伯特·澤米吉斯",
                "genre": ["劇情", "愛情"],
                "releaseYear": 1994,
                "rating": 8.8,
                "plot": "智商只有75的阿甘,憑藉著誠實守信和善良,創造了不平凡的人生。",
                "duration": 142
            },
            {
                "title": "肖申克的救贖",
                "director": "法蘭克·達拉邦特",
                "genre": ["劇情"],
                "releaseYear": 1994,
                "rating": 9.3,
                "plot": "兩個監獄犯人建立起深厚的友誼,並尋找救贖和希望。",
                "duration": 142
            },
            {
                "title": "駭客任務",
                "director": "華卓斯基兄弟",
                "genre": ["動作", "科幻"],
                "releaseYear": 1999,
                "rating": 8.7,
                "plot": "一個電腦駭客發現現實世界實際上是由機器創造的模擬環境。",
                "duration": 136
            },
        ]

        start_time = time.time()

        # 使用批量插入（動態批處理）
        with movies.batch.dynamic() as batch:
            for movie in movie_data:
                batch.add_object(properties=movie)

        elapsed_time = time.time() - start_time

        console.print(f"[green]✓ 成功批量插入 {len(movie_data)} 部電影[/green]")
        console.print(f"[dim]耗時: {elapsed_time:.2f} 秒[/dim]")

        # 檢查批處理結果
        if movies.batch.failed_objects:
            console.print(f"[yellow]⚠ 失敗數量: {len(movies.batch.failed_objects)}[/yellow]")

        return len(movie_data)

    except Exception as e:
        console.print(f"[red]✗ 批量插入失敗: {e}[/red]")
        return 0


def batch_insert_with_progress(client):
    """帶進度條的批量插入"""
    console.print("\n[bold cyan]4. 帶進度條的批量插入[/bold cyan]")

    try:
        movies = client.collections.get("Movie")

        # 生成更多測試數據
        genres_list = [
            ["動作"], ["喜劇"], ["劇情"], ["科幻"], ["恐怖"],
            ["愛情"], ["冒險"], ["懸疑"], ["動畫"], ["紀錄片"]
        ]

        large_dataset = []
        for i in range(100):
            large_dataset.append({
                "title": f"測試電影 {i+1}",
                "director": f"導演 {i % 10}",
                "genre": genres_list[i % len(genres_list)],
                "releaseYear": 2000 + (i % 24),
                "rating": round(5.0 + (i % 5) * 0.5, 1),
                "plot": f"這是測試電影 {i+1} 的劇情簡介。",
                "duration": 90 + (i % 60)
            })

        # 使用進度條
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]插入數據...", total=len(large_dataset))

            with movies.batch.dynamic() as batch:
                for movie in large_dataset:
                    batch.add_object(properties=movie)
                    progress.update(task, advance=1)

        console.print(f"[green]✓ 成功插入 {len(large_dataset)} 條數據[/green]")

        return len(large_dataset)

    except Exception as e:
        console.print(f"[red]✗ 插入失敗: {e}[/red]")
        return 0


def import_from_json(client):
    """從 JSON 文件導入"""
    console.print("\n[bold cyan]5. 從 JSON 導入數據[/bold cyan]")

    try:
        # 創建示例 JSON 數據
        json_data = [
            {
                "title": "辛德勒的名單",
                "director": "史蒂芬·史匹柏",
                "genre": ["傳記", "劇情", "歷史"],
                "releaseYear": 1993,
                "rating": 9.0,
                "plot": "在波蘭,德國商人奧斯卡·辛德勒拯救了1000多名猶太難民。",
                "duration": 195
            },
            {
                "title": "教父",
                "director": "法蘭西斯·柯波拉",
                "genre": ["犯罪", "劇情"],
                "releaseYear": 1972,
                "rating": 9.2,
                "plot": "義大利黑手黨家族的權力和傳承故事。",
                "duration": 175
            },
        ]

        movies = client.collections.get("Movie")

        # 批量插入
        inserted_count = 0
        with movies.batch.dynamic() as batch:
            for movie in json_data:
                batch.add_object(properties=movie)
                inserted_count += 1

        console.print(f"[green]✓ 從 JSON 導入 {inserted_count} 條數據[/green]")

        return inserted_count

    except Exception as e:
        console.print(f"[red]✗ 導入失敗: {e}[/red]")
        return 0


def verify_data(client):
    """驗證數據"""
    console.print("\n[bold cyan]6. 驗證導入的數據[/bold cyan]")

    try:
        movies = client.collections.get("Movie")

        # 獲取總數
        result = movies.aggregate.over_all(total_count=True)
        total_count = result.total_count

        console.print(f"[green]✓ 總共有 {total_count} 部電影[/green]")

        # 獲取部分數據驗證
        response = movies.query.fetch_objects(limit=5)

        table = Table(title="前 5 部電影")
        table.add_column("標題", style="cyan")
        table.add_column("導演", style="green")
        table.add_column("年份", style="yellow")
        table.add_column("評分", style="magenta")

        for obj in response.objects:
            table.add_row(
                obj.properties["title"],
                obj.properties["director"],
                str(obj.properties.get("releaseYear", "N/A")),
                str(obj.properties.get("rating", "N/A"))
            )

        console.print(table)

        # 統計信息
        console.print("\n[bold]統計信息:[/bold]")

        # 按年份統計
        from weaviate.classes.aggregate import GroupByAggregate
        result = movies.aggregate.over_all(
            group_by=GroupByAggregate(prop="releaseYear")
        )

        year_stats = {}
        for group in result.groups:
            year = group.grouped_by.value
            count = group.total_count
            if year and count:
                year_stats[year] = count

        # 顯示前幾年
        sorted_years = sorted(year_stats.items(), key=lambda x: x[1], reverse=True)[:5]
        for year, count in sorted_years:
            console.print(f"  {year}: {count} 部")

        return total_count

    except Exception as e:
        console.print(f"[red]✗ 驗證失敗: {e}[/red]")
        return 0


def error_handling_example(client):
    """錯誤處理示例"""
    console.print("\n[bold cyan]7. 錯誤處理示例[/bold cyan]")

    try:
        movies = client.collections.get("Movie")

        # 嘗試插入無效數據
        invalid_data = [
            {"title": "有效電影", "director": "導演A", "releaseYear": 2020, "rating": 8.0},
            {"title": "無效電影1", "director": "導演B", "releaseYear": "不是數字", "rating": 8.0},  # 錯誤的數據類型
            {"title": "無效電影2"},  # 缺少必要字段
        ]

        success_count = 0
        error_count = 0

        with movies.batch.dynamic() as batch:
            for movie in invalid_data:
                try:
                    batch.add_object(properties=movie)
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    console.print(f"[yellow]⚠ 跳過無效數據: {movie.get('title', 'Unknown')}[/yellow]")

        console.print(f"[green]✓ 成功: {success_count}, 失敗: {error_count}[/green]")

        # 檢查批處理錯誤
        if movies.batch.failed_objects:
            console.print(f"\n[yellow]批處理失敗對象:[/yellow]")
            for failed in movies.batch.failed_objects:
                console.print(f"  錯誤: {failed.message}")

    except Exception as e:
        console.print(f"[red]✗ 錯誤處理示例失敗: {e}[/red]")


def cleanup(client):
    """清理資源"""
    try:
        console.print("\n[cyan]清理資源...[/cyan]")
        if client.collections.exists("Movie"):
            client.collections.delete("Movie")
            console.print("[dim]✓ 已刪除 Movie 集合[/dim]")
        client.close()
    except Exception as e:
        console.print(f"[red]清理失敗: {e}[/red]")


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Weaviate 數據導入示例[/bold cyan]",
        border_style="cyan"
    ))

    client = connect_client()
    if not client:
        return

    try:
        # 設置集合
        if not setup_collection(client):
            return

        # 1. 單條插入
        insert_single_object(client)

        # 2. 帶自定義向量插入
        insert_with_custom_vector(client)

        # 3. 批量插入
        batch_insert(client)

        # 4. 帶進度條的批量插入
        batch_insert_with_progress(client)

        # 5. 從 JSON 導入
        import_from_json(client)

        # 6. 驗證數據
        verify_data(client)

        # 7. 錯誤處理
        error_handling_example(client)

        console.print("\n" + "="*60)
        console.print("[bold green]✓ 數據導入示例完成！[/bold green]")
        console.print("\n[cyan]下一步:[/cyan]")
        console.print("  1. 查看 04_向量搜索.py 學習向量搜索")
        console.print("  2. 查看 05_混合搜索.py 學習混合搜索")

    finally:
        cleanup(client)


if __name__ == "__main__":
    main()

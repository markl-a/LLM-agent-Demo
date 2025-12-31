"""
LangMem 記憶檢索示例

本示例展示:
1. 多維度記憶檢索
2. 記憶排序和過濾
3. 記憶融合策略
4. 高級檢索技巧
"""

from langchain.memory import VectorStoreRetrieverMemory
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import json

console = Console()
load_dotenv()


def setup_advanced_memory():
    """設置高級記憶系統"""
    try:
        console.print("\n[cyan]1. 設置高級記憶系統[/cyan]")
        console.print("[dim]創建支持多維度檢索的記憶[/dim]\n")

        if not os.getenv("OPENAI_API_KEY"):
            console.print("[yellow]⚠ 需要 OPENAI_API_KEY[/yellow]\n")
            return None

        # 創建嵌入模型
        embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))

        # 準備記憶數據
        memories = [
            {"text": "用戶喜歡喝咖啡", "importance": 5, "category": "偏好"},
            {"text": "用戶是 Python 開發者", "importance": 8, "category": "技能"},
            {"text": "用戶住在台北", "importance": 6, "category": "個人信息"},
            {"text": "用戶正在學習 AI", "importance": 9, "category": "學習"},
            {"text": "用戶養了一隻貓", "importance": 4, "category": "生活"},
        ]

        # 創建向量存儲
        texts = [m["text"] for m in memories]
        metadatas = [{"importance": m["importance"], "category": m["category"]} for m in memories]

        vectorstore = FAISS.from_texts(
            texts,
            embeddings,
            metadatas=metadatas
        )

        console.print("[green]✓ 記憶系統設置完成[/green]")
        console.print(f"[dim]記憶數量: {len(memories)}[/dim]\n")

        return vectorstore, embeddings

    except Exception as e:
        console.print(f"[red]✗ 設置失敗: {e}[/red]")
        return None, None


def demonstrate_similarity_search(vectorstore):
    """演示相似度搜索"""
    try:
        console.print("[cyan]2. 相似度搜索[/cyan]")
        console.print("[dim]基於語義相似度檢索記憶[/dim]\n")

        queries = [
            "用戶的技術背景",
            "用戶的日常愛好",
            "用戶的居住地點"
        ]

        for query in queries:
            console.print(f"[yellow]查詢: {query}[/yellow]")

            # 執行搜索
            results = vectorstore.similarity_search_with_score(query, k=2)

            table = Table()
            table.add_column("排名", style="cyan")
            table.add_column("內容", style="green")
            table.add_column("分數", style="yellow")

            for idx, (doc, score) in enumerate(results, 1):
                table.add_row(
                    str(idx),
                    doc.page_content,
                    f"{score:.4f}"
                )

            console.print(table)
            console.print()

        return True

    except Exception as e:
        console.print(f"[red]✗ 搜索失敗: {e}[/red]")
        return False


def demonstrate_metadata_filtering(vectorstore):
    """演示元數據過濾"""
    try:
        console.print("[cyan]3. 元數據過濾[/cyan]")
        console.print("[dim]按元數據篩選記憶[/dim]\n")

        # 按重要性過濾
        console.print("[yellow]高重要性記憶 (importance >= 7):[/yellow]")

        # 使用 MMR 搜索 (Maximal Marginal Relevance)
        results = vectorstore.max_marginal_relevance_search(
            "所有記憶",
            k=5,
            fetch_k=10
        )

        table = Table()
        table.add_column("內容", style="green")
        table.add_column("分類", style="cyan")
        table.add_column("重要性", style="yellow")

        for doc in results:
            if doc.metadata.get("importance", 0) >= 7:
                table.add_row(
                    doc.page_content,
                    doc.metadata.get("category", "未分類"),
                    str(doc.metadata.get("importance", 0))
                )

        console.print(table)
        console.print()

        # 按分類過濾
        console.print("[yellow]按分類檢索:[/yellow]")
        categories = ["技能", "學習", "偏好"]

        for category in categories:
            results = vectorstore.similarity_search(
                category,
                k=5
            )

            matched = [r for r in results if r.metadata.get("category") == category]
            if matched:
                console.print(f"  📁 {category}: {len(matched)} 條記憶")

        console.print()

        return True

    except Exception as e:
        console.print(f"[red]✗ 過濾失敗: {e}[/red]")
        return False


def demonstrate_mmr_search(vectorstore):
    """演示 MMR 搜索"""
    try:
        console.print("[cyan]4. MMR 搜索 (多樣性)[/cyan]")
        console.print("[dim]平衡相關性和多樣性[/dim]\n")

        query = "用戶的信息"

        # 普通相似度搜索
        console.print("[yellow]普通相似度搜索:[/yellow]")
        normal_results = vectorstore.similarity_search(query, k=3)

        table1 = Table(title="相似度搜索結果")
        table1.add_column("排名", style="cyan")
        table1.add_column("內容", style="green")

        for idx, doc in enumerate(normal_results, 1):
            table1.add_row(str(idx), doc.page_content)

        console.print(table1)
        console.print()

        # MMR 搜索
        console.print("[yellow]MMR 搜索 (增加多樣性):[/yellow]")
        mmr_results = vectorstore.max_marginal_relevance_search(
            query,
            k=3,
            fetch_k=10
        )

        table2 = Table(title="MMR 搜索結果")
        table2.add_column("排名", style="cyan")
        table2.add_column("內容", style="green")

        for idx, doc in enumerate(mmr_results, 1):
            table2.add_row(str(idx), doc.page_content)

        console.print(table2)
        console.print("\n[dim]💡 MMR 搜索返回更多樣化的結果[/dim]\n")

        return True

    except Exception as e:
        console.print(f"[red]✗ MMR 搜索失敗: {e}[/red]")
        return False


def demonstrate_memory_fusion():
    """演示記憶融合"""
    try:
        console.print("[cyan]5. 記憶融合[/cyan]")
        console.print("[dim]合併多個記憶源的結果[/dim]\n")

        # 模擬不同記憶源
        memory_sources = {
            "短期記憶": [
                {"content": "用戶剛才問了關於 Python 的問題", "timestamp": "2分鐘前"},
                {"content": "用戶正在查看文檔", "timestamp": "5分鐘前"}
            ],
            "長期記憶": [
                {"content": "用戶是 Python 開發者", "importance": 8},
                {"content": "用戶喜歡函數式編程", "importance": 6}
            ],
            "情節記憶": [
                {"content": "上週完成了 LangChain 項目", "date": "上週"},
                {"content": "參加了 AI 技術分享會", "date": "上週"}
            ]
        }

        # 顯示融合策略
        console.print("[yellow]記憶融合策略:[/yellow]\n")

        for source, memories in memory_sources.items():
            console.print(f"[cyan]📚 {source}:[/cyan]")
            for mem in memories:
                content = mem["content"]
                meta = " | ".join([f"{k}: {v}" for k, v in mem.items() if k != "content"])
                console.print(f"  • {content}")
                if meta:
                    console.print(f"    [dim]{meta}[/dim]")
            console.print()

        # 融合結果
        console.print("[yellow]融合後的完整上下文:[/yellow]")
        console.print(Panel(
            "用戶是一位 Python 開發者,喜歡函數式編程。"
            "最近完成了 LangChain 項目並參加了 AI 技術分享會。"
            "當前正在查看文檔並詢問 Python 相關問題。",
            border_style="green",
            title="融合記憶"
        ))
        console.print()

        return True

    except Exception as e:
        console.print(f"[red]✗ 融合失敗: {e}[/red]")
        return False


def demonstrate_retrieval_strategies():
    """演示檢索策略"""
    try:
        console.print("[cyan]6. 檢索策略比較[/cyan]\n")

        table = Table(title="記憶檢索策略")
        table.add_column("策略", style="cyan")
        table.add_column("優點", style="green")
        table.add_column("適用場景", style="yellow")

        table.add_row(
            "相似度搜索",
            "精確匹配語義",
            "單一主題查詢"
        )
        table.add_row(
            "MMR 搜索",
            "結果多樣化",
            "探索性查詢"
        )
        table.add_row(
            "元數據過濾",
            "精確控制範圍",
            "分類檢索"
        )
        table.add_row(
            "混合搜索",
            "綜合多種因素",
            "複雜查詢需求"
        )
        table.add_row(
            "記憶融合",
            "完整上下文",
            "需要全局視角"
        )

        console.print(table)
        console.print()

        # 最佳實踐
        console.print("[yellow]最佳實踐:[/yellow]")
        console.print("  1. 根據查詢意圖選擇合適的檢索策略")
        console.print("  2. 設置合理的 k 值(返回結果數)")
        console.print("  3. 使用元數據過濾提高精確度")
        console.print("  4. 結合多種策略獲得最佳效果")
        console.print("  5. 定期評估檢索質量並調優\n")

        return True

    except Exception as e:
        console.print(f"[red]✗ 演示失敗: {e}[/red]")
        return False


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]LangMem 記憶檢索示例[/bold cyan]\n"
        "[dim]展示高級記憶檢索技術[/dim]",
        border_style="cyan"
    ))

    # 設置記憶系統
    result = setup_advanced_memory()
    if result[0] is None:
        console.print("[yellow]跳過演示: 需要 OpenAI API Key[/yellow]")
        return

    vectorstore, embeddings = result

    # 演示各種檢索方法
    demonstrate_similarity_search(vectorstore)
    demonstrate_metadata_filtering(vectorstore)
    demonstrate_mmr_search(vectorstore)
    demonstrate_memory_fusion()
    demonstrate_retrieval_strategies()

    # 完成
    console.print("="*60)
    console.print("[bold green]✓ 記憶檢索示例完成！[/bold green]")
    console.print("\n[cyan]關鍵要點:[/cyan]")
    console.print("  • 相似度搜索: 最基礎的語義檢索")
    console.print("  • 元數據過濾: 精確控制檢索範圍")
    console.print("  • MMR 搜索: 平衡相關性和多樣性")
    console.print("  • 記憶融合: 整合多個記憶源")


if __name__ == "__main__":
    main()

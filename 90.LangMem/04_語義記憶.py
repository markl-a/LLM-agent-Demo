"""
LangMem 語義記憶示例

本示例展示:
1. 向量記憶存儲
2. 語義相似度搜索
3. 知識庫構建
4. 智能記憶檢索
"""

from langchain.memory import VectorStoreRetrieverMemory
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from dotenv import load_dotenv
import os
import numpy as np

console = Console()
load_dotenv()


def create_vector_memory():
    """創建向量記憶"""
    try:
        console.print("\n[cyan]1. 創建向量記憶[/cyan]")
        console.print("[dim]使用向量數據庫存儲語義記憶[/dim]\n")

        # 檢查 API Key
        if not os.getenv("OPENAI_API_KEY"):
            console.print("[yellow]⚠ 需要 OPENAI_API_KEY[/yellow]\n")
            return None

        # 創建嵌入模型
        embeddings = OpenAIEmbeddings(
            api_key=os.getenv("OPENAI_API_KEY")
        )

        # 創建向量存儲
        vectorstore = FAISS.from_texts(
            ["初始化向量存儲"],
            embeddings
        )

        # 創建檢索器
        retriever = vectorstore.as_retriever(
            search_kwargs={"k": 3}
        )

        # 創建向量記憶
        memory = VectorStoreRetrieverMemory(
            retriever=retriever
        )

        console.print("[green]✓ 向量記憶創建成功[/green]\n")

        return memory, vectorstore, embeddings

    except Exception as e:
        console.print(f"[red]✗ 創建失敗: {e}[/red]")
        return None, None, None


def add_semantic_memories(memory):
    """添加語義記憶"""
    try:
        console.print("[cyan]2. 添加語義記憶[/cyan]")
        console.print("[dim]添加不同主題的記憶[/dim]\n")

        # 定義記憶內容
        memories = [
            "用戶喜歡喝咖啡,特別是美式咖啡",
            "用戶是一名 Python 開發者,擅長機器學習",
            "用戶住在台北市,經常去象山爬山",
            "用戶最喜歡的電影類型是科幻片",
            "用戶每天早上 7 點起床,晚上 11 點睡覺",
            "用戶喜歡閱讀技術書籍,尤其是 AI 相關的",
            "用戶的生日是 1990 年 1 月 1 日",
            "用戶正在學習 LangChain 框架",
            "用戶計劃明年去日本旅遊",
            "用戶養了一隻叫做 Max 的貓"
        ]

        # 添加記憶
        console.print("[yellow]添加記憶中...[/yellow]")
        for idx, mem in enumerate(memories, 1):
            memory.save_context(
                {"input": f"記錄 {idx}"},
                {"output": mem}
            )

        console.print(f"[green]✓ 成功添加 {len(memories)} 條語義記憶[/green]\n")

        # 顯示記憶列表
        table = Table(title="已添加的語義記憶")
        table.add_column("編號", style="cyan")
        table.add_column("內容", style="green")

        for idx, mem in enumerate(memories, 1):
            table.add_row(str(idx), mem)

        console.print(table)
        console.print()

        return True

    except Exception as e:
        console.print(f"[red]✗ 添加失敗: {e}[/red]")
        return False


def semantic_search(memory):
    """語義搜索"""
    try:
        console.print("[cyan]3. 語義搜索[/cyan]")
        console.print("[dim]基於語義相似度檢索記憶[/dim]\n")

        # 定義搜索查詢
        queries = [
            "用戶的飲品偏好是什麼?",
            "用戶的職業和技能",
            "用戶的興趣愛好",
            "用戶的寵物信息"
        ]

        for query in queries:
            console.print(f"[yellow]查詢: {query}[/yellow]")

            # 從記憶中檢索
            result = memory.load_memory_variables({"prompt": query})

            console.print(Panel(
                result.get("history", "無相關記憶"),
                title="檢索結果",
                border_style="green"
            ))
            console.print()

        return True

    except Exception as e:
        console.print(f"[red]✗ 搜索失敗: {e}[/red]")
        return False


def demonstrate_similarity_threshold(vectorstore, embeddings):
    """演示相似度閾值"""
    try:
        console.print("[cyan]4. 相似度閾值過濾[/cyan]")
        console.print("[dim]只返回高相似度的記憶[/dim]\n")

        query = "用戶的程式設計能力"

        # 搜索並顯示分數
        results = vectorstore.similarity_search_with_score(query, k=5)

        table = Table(title=f"搜索結果 (查詢: {query})")
        table.add_column("排名", style="cyan")
        table.add_column("內容", style="green")
        table.add_column("相似度分數", style="yellow")

        for idx, (doc, score) in enumerate(results, 1):
            table.add_row(
                str(idx),
                doc.page_content[:60] + "..." if len(doc.page_content) > 60 else doc.page_content,
                f"{score:.4f}"
            )

        console.print(table)
        console.print("[dim]💡 分數越低表示越相似 (L2 距離)[/dim]\n")

        return True

    except Exception as e:
        console.print(f"[red]✗ 演示失敗: {e}[/red]")
        return False


def build_knowledge_base(vectorstore, embeddings):
    """構建知識庫"""
    try:
        console.print("[cyan]5. 構建知識庫[/cyan]")
        console.print("[dim]創建結構化的知識記憶[/dim]\n")

        # 定義知識庫內容
        knowledge = {
            "個人信息": [
                "姓名: 張三",
                "年齡: 34 歲",
                "職業: 軟體工程師",
                "公司: ABC 科技公司"
            ],
            "技能": [
                "程式語言: Python, JavaScript, Go",
                "框架: Django, React, LangChain",
                "工具: Docker, Kubernetes, Git",
                "領域: AI, Web 開發, DevOps"
            ],
            "偏好": [
                "飲料: 咖啡 (美式)",
                "運動: 爬山, 跑步",
                "閱讀: 技術書籍, 科幻小說",
                "音樂: 古典音樂, 爵士樂"
            ],
            "計劃": [
                "短期: 學習 LangChain 和 AI Agent",
                "中期: 開發個人 AI 助手",
                "長期: 創業做 AI 產品"
            ]
        }

        # 添加到向量存儲
        all_texts = []
        all_metadatas = []

        for category, items in knowledge.items():
            for item in items:
                all_texts.append(f"[{category}] {item}")
                all_metadatas.append({"category": category})

        vectorstore.add_texts(all_texts, metadatas=all_metadatas)

        console.print(f"[green]✓ 知識庫構建完成[/green]")
        console.print(f"[dim]分類數: {len(knowledge)}[/dim]")
        console.print(f"[dim]知識條目: {len(all_texts)}[/dim]\n")

        # 顯示知識庫結構
        table = Table(title="知識庫結構")
        table.add_column("分類", style="cyan")
        table.add_column("條目數", style="yellow")

        for category, items in knowledge.items():
            table.add_row(category, str(len(items)))

        console.print(table)
        console.print()

        # 測試檢索
        console.print("[yellow]測試知識檢索:[/yellow]")
        test_query = "用戶的技術技能有哪些?"
        results = vectorstore.similarity_search(test_query, k=3)

        for idx, doc in enumerate(results, 1):
            console.print(f"  {idx}. {doc.page_content}")

        console.print()

        return True

    except Exception as e:
        console.print(f"[red]✗ 構建失敗: {e}[/red]")
        return False


def compare_semantic_vs_keyword():
    """比較語義搜索與關鍵字搜索"""
    try:
        console.print("[cyan]6. 語義搜索 vs 關鍵字搜索[/cyan]\n")

        table = Table(title="搜索方式比較")
        table.add_column("特性", style="cyan")
        table.add_column("語義搜索", style="green")
        table.add_column("關鍵字搜索", style="yellow")

        table.add_row(
            "理解意圖",
            "✅ 理解查詢語義",
            "❌ 只匹配字面"
        )
        table.add_row(
            "同義詞",
            "✅ 自動識別",
            "❌ 需要明確指定"
        )
        table.add_row(
            "多語言",
            "✅ 跨語言搜索",
            "❌ 語言限制"
        )
        table.add_row(
            "性能",
            "⚠️ 需要向量計算",
            "✅ 快速"
        )
        table.add_row(
            "成本",
            "⚠️ 需要嵌入模型",
            "✅ 低成本"
        )

        console.print(table)
        console.print()

    except Exception as e:
        console.print(f"[red]✗ 比較失敗: {e}[/red]")


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]LangMem 語義記憶示例[/bold cyan]\n"
        "[dim]展示基於向量的智能記憶檢索[/dim]",
        border_style="cyan"
    ))

    # 創建向量記憶
    result = create_vector_memory()
    if result[0] is None:
        console.print("[yellow]跳過演示: 需要 OpenAI API Key[/yellow]")
        return

    memory, vectorstore, embeddings = result

    # 添加語義記憶
    add_semantic_memories(memory)

    # 語義搜索
    semantic_search(memory)

    # 演示相似度閾值
    demonstrate_similarity_threshold(vectorstore, embeddings)

    # 構建知識庫
    build_knowledge_base(vectorstore, embeddings)

    # 比較搜索方式
    compare_semantic_vs_keyword()

    # 完成
    console.print("="*60)
    console.print("[bold green]✓ 語義記憶示例完成！[/bold green]")
    console.print("\n[cyan]關鍵要點:[/cyan]")
    console.print("  • 向量記憶: 基於語義理解而非字面匹配")
    console.print("  • 智能檢索: 自動找到相關記憶")
    console.print("  • 知識庫: 結構化的記憶組織")
    console.print("  • 相似度: 精確控制檢索質量")


if __name__ == "__main__":
    main()

"""
Weaviate 生成式搜索示例（RAG）

本示例展示：
1. 基本 RAG 問答
2. 生成式搜索配置
3. 單提示和分組提示
4. 引用和來源追蹤
"""

import weaviate
from weaviate.classes.config import Configure, Property, DataType
from weaviate.classes.query import MetadataQuery
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
import os
from dotenv import load_dotenv

load_dotenv()

console = Console()


def setup_knowledge_base(client):
    """設置知識庫"""
    console.print("[cyan]設置知識庫...[/cyan]")

    try:
        if client.collections.exists("KnowledgeBase"):
            client.collections.delete("KnowledgeBase")

        # 創建知識庫集合，配置生成式模塊
        client.collections.create(
            name="KnowledgeBase",
            properties=[
                Property(name="title", data_type=DataType.TEXT),
                Property(name="content", data_type=DataType.TEXT),
                Property(name="category", data_type=DataType.TEXT),
                Property(name="source", data_type=DataType.TEXT),
            ],
            vectorizer_config=Configure.Vectorizer.text2vec_openai(
                model="text-embedding-3-small"
            ),
            generative_config=Configure.Generative.openai(
                model="gpt-4o-mini"
            )
        )

        kb = client.collections.get("KnowledgeBase")

        # 插入知識文檔
        knowledge_docs = [
            {
                "title": "什麼是向量數據庫",
                "content": "向量數據庫是一種專門為存儲和檢索高維向量數據而設計的數據庫系統。它使用特殊的索引技術,如HNSW或IVF,來快速找到相似的向量。向量數據庫廣泛應用於語義搜索、推薦系統和RAG應用中。主要優勢包括快速的相似性搜索、可擴展性和與AI模型的無縫整合。",
                "category": "技術概念",
                "source": "技術文檔"
            },
            {
                "title": "RAG 工作原理",
                "content": "檢索增強生成(RAG)是一種結合信息檢索和文本生成的技術。工作流程分為三步:1)將用戶問題轉換為向量 2)在向量數據庫中檢索相關文檔 3)將檢索到的內容與問題一起發送給大語言模型生成答案。RAG的優勢在於能夠基於實時數據回答問題,減少幻覺,並能提供信息來源。",
                "category": "AI技術",
                "source": "研究論文"
            },
            {
                "title": "Weaviate 的特點",
                "content": "Weaviate是一個開源的向量數據庫,具有以下特點:支持多種向量化模塊(OpenAI、Cohere等)、提供GraphQL和RESTful API、原生支持混合搜索(向量+關鍵字)、內置生成式搜索功能、支持多租戶架構、可水平擴展。Weaviate特別適合構建AI驅動的搜索和問答系統。",
                "category": "產品介紹",
                "source": "官方文檔"
            },
            {
                "title": "語義搜索優勢",
                "content": "語義搜索不同於傳統的關鍵字搜索,它理解查詢的意圖和上下文。通過向量嵌入技術,語義搜索能夠找到意義相關但用詞不同的內容。例如,搜索'如何烹飪'可以找到'烹飪方法'、'料理技巧'等相關內容。這使得搜索更加智能和用戶友好。",
                "category": "技術概念",
                "source": "技術博客"
            },
            {
                "title": "向量嵌入技術",
                "content": "向量嵌入是將文本、圖像等數據轉換為數值向量的技術。這些向量捕捉了數據的語義信息,使得相似的內容在向量空間中距離較近。常用的嵌入模型包括OpenAI的text-embedding-3、Google的BERT、以及開源的Sentence Transformers。高質量的嵌入對於搜索準確性至關重要。",
                "category": "AI技術",
                "source": "研究論文"
            },
            {
                "title": "如何選擇向量數據庫",
                "content": "選擇向量數據庫時需要考慮多個因素:1)數據規模和查詢性能需求 2)是否需要混合搜索 3)是否支持所需的AI模型 4)部署方式(雲端或自托管) 5)價格和許可證 6)社區支持和文檔質量。Weaviate、Pinecone、Milvus、Qdrant各有特點,需要根據具體需求選擇。",
                "category": "技術指南",
                "source": "比較分析"
            },
            {
                "title": "生產環境部署建議",
                "content": "在生產環境部署向量數據庫時,需要注意以下幾點:1)使用SSD存儲提升性能 2)配置足夠的內存用於索引 3)設置備份和災難恢復策略 4)實施監控和告警 5)使用負載均衡和副本提高可用性 6)定期更新和維護索引 7)實施安全措施如加密和訪問控制。",
                "category": "運維指南",
                "source": "最佳實踐"
            },
        ]

        with kb.batch.dynamic() as batch:
            for doc in knowledge_docs:
                batch.add_object(properties=doc)

        console.print(f"[green]✓ 已插入 {len(knowledge_docs)} 篇知識文檔[/green]\n")

    except Exception as e:
        console.print(f"[red]✗ 設置失敗: {e}[/red]")


def basic_rag_qa(client):
    """基本 RAG 問答"""
    console.print("[bold cyan]1. 基本 RAG 問答[/bold cyan]")

    try:
        kb = client.collections.get("KnowledgeBase")

        question = "什麼是向量數據庫？它有什麼用？"
        console.print(f"[yellow]問題: {question}[/yellow]\n")

        response = kb.generate.near_text(
            query=question,
            limit=2,
            single_prompt="請根據以下內容回答問題。問題: {question} 內容: {content}"
        )

        # 顯示生成的答案
        if response.generated:
            console.print(Panel(
                Markdown(response.generated),
                title="[bold green]AI 回答[/bold green]",
                border_style="green"
            ))

        # 顯示引用來源
        console.print("\n[bold]引用來源:[/bold]")
        for i, obj in enumerate(response.objects, 1):
            console.print(f"{i}. {obj.properties['title']} ({obj.properties['source']})")

        console.print()

    except Exception as e:
        console.print(f"[red]✗ RAG 問答失敗: {e}[/red]")


def grouped_task_rag(client):
    """分組任務 RAG"""
    console.print("[bold cyan]2. 分組任務 RAG[/bold cyan]")

    try:
        kb = client.collections.get("KnowledgeBase")

        question = "向量數據庫的主要應用場景"
        console.print(f"[yellow]問題: {question}[/yellow]\n")

        response = kb.generate.near_text(
            query=question,
            limit=3,
            grouped_task="請總結這些文檔中提到的向量數據庫應用場景,用要點形式列出。"
        )

        # 顯示生成的總結
        if response.generated:
            console.print(Panel(
                Markdown(response.generated),
                title="[bold green]總結[/bold green]",
                border_style="green"
            ))

        console.print("\n[bold]基於以下文檔:[/bold]")
        for obj in response.objects:
            console.print(f"  • {obj.properties['title']}")

        console.print()

    except Exception as e:
        console.print(f"[red]✗ 分組任務失敗: {e}[/red]")


def single_prompt_per_object(client):
    """單個提示詞(每個對象)"""
    console.print("[bold cyan]3. 單個提示詞(每個對象)[/bold cyan]")

    try:
        kb = client.collections.get("KnowledgeBase")

        question = "AI技術"
        console.print(f"[yellow]搜索: {question}[/yellow]\n")

        response = kb.generate.near_text(
            query=question,
            limit=3,
            single_prompt="用一句話總結: {content}"
        )

        # 每個文檔都有自己的生成結果
        for i, obj in enumerate(response.objects, 1):
            console.print(f"[cyan]{i}. {obj.properties['title']}[/cyan]")
            if obj.generated:
                console.print(f"   摘要: {obj.generated}")
            console.print()

    except Exception as e:
        console.print(f"[red]✗ 生成失敗: {e}[/red]")


def rag_with_filters(client):
    """帶過濾器的 RAG"""
    console.print("[bold cyan]4. 帶過濾器的 RAG[/bold cyan]")

    try:
        kb = client.collections.get("KnowledgeBase")
        from weaviate.classes.query import Filter

        question = "部署建議"
        console.print(f"[yellow]問題: {question} (僅搜索'運維指南'分類)[/yellow]\n")

        response = kb.generate.near_text(
            query=question,
            limit=2,
            filters=Filter.by_property("category").equal("運維指南"),
            grouped_task="請總結生產環境部署的關鍵要點。"
        )

        if response.generated:
            console.print(Panel(
                Markdown(response.generated),
                title="[bold green]部署建議[/bold green]",
                border_style="green"
            ))

        console.print()

    except Exception as e:
        console.print(f"[red]✗ 帶過濾器的 RAG 失敗: {e}[/red]")


def multi_step_rag(client):
    """多步驟 RAG"""
    console.print("[bold cyan]5. 多步驟 RAG 流程[/bold cyan]")

    try:
        kb = client.collections.get("KnowledgeBase")

        # 步驟 1: 檢索相關文檔
        console.print("[yellow]步驟 1: 檢索相關文檔[/yellow]")
        question = "如何選擇和部署向量數據庫？"

        retrieval_response = kb.query.near_text(
            query=question,
            limit=3
        )

        console.print(f"找到 {len(retrieval_response.objects)} 篇相關文檔\n")

        # 步驟 2: 基於檢索結果生成答案
        console.print("[yellow]步驟 2: 生成綜合答案[/yellow]\n")

        generation_response = kb.generate.near_text(
            query=question,
            limit=3,
            grouped_task="""請基於這些文檔,回答: 如何選擇和部署向量數據庫？

            請包括:
            1. 選擇標準
            2. 部署建議
            3. 注意事項

            用清晰的要點形式呈現。"""
        )

        if generation_response.generated:
            console.print(Panel(
                Markdown(generation_response.generated),
                title="[bold green]綜合答案[/bold green]",
                border_style="green"
            ))

        # 步驟 3: 顯示來源
        console.print("\n[bold]參考來源:[/bold]")
        for i, obj in enumerate(generation_response.objects, 1):
            console.print(f"{i}. [{obj.properties['category']}] {obj.properties['title']}")

        console.print()

    except Exception as e:
        console.print(f"[red]✗ 多步驟 RAG 失敗: {e}[/red]")


def custom_prompt_templates(client):
    """自定義提示詞模板"""
    console.print("[bold cyan]6. 自定義提示詞模板[/bold cyan]")

    try:
        kb = client.collections.get("KnowledgeBase")

        question = "RAG技術"

        # 使用自定義提示詞模板
        custom_prompt = """你是一個技術專家。請基於以下內容回答問題。

問題: {question}

相關內容:
{content}

請用專業但易懂的語言回答,並在回答中標注關鍵概念。"""

        console.print("[yellow]使用自定義提示詞模板[/yellow]\n")

        response = kb.generate.near_text(
            query=question,
            limit=2,
            single_prompt=custom_prompt
        )

        if response.generated:
            console.print(Panel(
                Markdown(response.generated),
                title="[bold green]專家回答[/bold green]",
                border_style="green"
            ))

        console.print()

    except Exception as e:
        console.print(f"[red]✗ 自定義提示詞失敗: {e}[/red]")


def rag_best_practices():
    """RAG 最佳實踐"""
    console.print("[bold cyan]7. RAG 最佳實踐[/bold cyan]")

    practices = [
        ("文檔分塊", "合理分塊文檔,每塊包含完整的語義單元"),
        ("檢索數量", "通常檢索3-5篇文檔,平衡相關性和成本"),
        ("提示工程", "清晰的提示詞能顯著提升答案質量"),
        ("引用來源", "始終顯示來源,提升答案可信度"),
        ("過濾策略", "使用過濾器限定搜索範圍,提升準確性"),
        ("模型選擇", "根據需求選擇合適的LLM(成本vs質量)"),
        ("緩存機制", "緩存常見問題的答案,節省成本"),
        ("錯誤處理", "優雅處理沒有相關文檔的情況"),
    ]

    table = Table(title="RAG 最佳實踐")
    table.add_column("主題", style="cyan", width=15)
    table.add_column("建議", style="green", width=45)

    for topic, advice in practices:
        table.add_row(topic, advice)

    console.print(table)


def cleanup(client):
    """清理資源"""
    try:
        if client.collections.exists("KnowledgeBase"):
            client.collections.delete("KnowledgeBase")
        client.close()
    except Exception as e:
        console.print(f"[red]清理失敗: {e}[/red]")


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Weaviate 生成式搜索(RAG)示例[/bold cyan]",
        border_style="cyan"
    ))

    # 檢查 OpenAI API Key
    if not os.getenv("OPENAI_API_KEY"):
        console.print("[red]錯誤: 請設置 OPENAI_API_KEY 環境變數[/red]")
        console.print("[yellow]在 .env 文件中添加: OPENAI_API_KEY=your-key-here[/yellow]")
        return

    try:
        client = weaviate.connect_to_local()
        console.print("[green]✓ 已連接到 Weaviate[/green]\n")

        # 設置知識庫
        setup_knowledge_base(client)

        # 執行各種 RAG 示例
        basic_rag_qa(client)
        grouped_task_rag(client)
        single_prompt_per_object(client)
        rag_with_filters(client)
        multi_step_rag(client)
        custom_prompt_templates(client)
        rag_best_practices()

        console.print("="*60)
        console.print("[bold green]✓ 生成式搜索示例完成！[/bold green]")

    except Exception as e:
        console.print(f"[red]錯誤: {e}[/red]")
    finally:
        cleanup(client)


if __name__ == "__main__":
    main()

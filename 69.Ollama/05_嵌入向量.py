"""
Ollama 嵌入向量示例

本示例展示：
1. 文本嵌入生成
2. 相似度計算
3. 語義搜索
4. 文檔聚類
5. RAG 應用基礎
"""

import ollama
import numpy as np
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from typing import List, Tuple
import json

console = Console()


def generate_embedding(text, model='nomic-embed-text'):
    """生成文本嵌入向量"""
    try:
        response = ollama.embeddings(
            model=model,
            prompt=text
        )

        embedding = response['embedding']
        return embedding

    except Exception as e:
        console.print(f"[red]生成嵌入失敗: {e}[/red]")
        return None


def basic_embedding_demo(model='nomic-embed-text'):
    """基礎嵌入向量示例"""
    try:
        console.print("\n[bold cyan]基礎嵌入向量示例[/bold cyan]")
        console.print(f"[dim]使用模型: {model}[/dim]")

        # 示例文本
        text = "人工智能正在改變世界"

        console.print(f"\n[bold]文本:[/bold] {text}")

        # 生成嵌入
        embedding = generate_embedding(text, model)

        if embedding:
            # 顯示嵌入信息
            console.print(f"\n[green]✓ 嵌入向量已生成[/green]")
            console.print(f"[dim]維度: {len(embedding)}[/dim]")
            console.print(f"[dim]前 10 個值: {embedding[:10]}[/dim]")
            console.print(f"[dim]數據類型: {type(embedding[0])}[/dim]")

            # 統計信息
            embedding_array = np.array(embedding)
            console.print(f"\n[bold]統計信息:[/bold]")
            console.print(f"  最小值: {embedding_array.min():.4f}")
            console.print(f"  最大值: {embedding_array.max():.4f}")
            console.print(f"  平均值: {embedding_array.mean():.4f}")
            console.print(f"  標準差: {embedding_array.std():.4f}")

        return embedding

    except Exception as e:
        console.print(f"[red]基礎嵌入示例失敗: {e}[/red]")
        return None


def cosine_similarity(vec1, vec2):
    """計算餘弦相似度"""
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)

    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)

    similarity = dot_product / (norm1 * norm2)
    return similarity


def similarity_comparison(model='nomic-embed-text'):
    """文本相似度比較"""
    try:
        console.print("\n[bold cyan]文本相似度比較[/bold cyan]")

        # 定義文本對
        text_pairs = [
            ("機器學習是人工智能的一個分支", "深度學習是機器學習的子領域"),
            ("我喜歡吃蘋果", "蘋果公司生產手機"),
            ("今天天氣很好", "陽光明媚的一天"),
            ("Python 是一種編程語言", "貓是一種動物")
        ]

        # 創建結果表格
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("文本 1", style="cyan", width=30)
        table.add_column("文本 2", style="yellow", width=30)
        table.add_column("相似度", justify="right", style="green", width=10)

        for text1, text2 in text_pairs:
            # 生成嵌入
            emb1 = generate_embedding(text1, model)
            emb2 = generate_embedding(text2, model)

            if emb1 and emb2:
                # 計算相似度
                similarity = cosine_similarity(emb1, emb2)

                # 添加到表格
                table.add_row(
                    text1[:30],
                    text2[:30],
                    f"{similarity:.4f}"
                )

        console.print(table)

        console.print("\n[dim]相似度範圍: -1 到 1，越接近 1 表示越相似[/dim]")

    except Exception as e:
        console.print(f"[red]相似度比較失敗: {e}[/red]")


def semantic_search(query, documents, model='nomic-embed-text', top_k=3):
    """語義搜索"""
    try:
        console.print("\n[bold cyan]語義搜索示例[/bold cyan]")

        console.print(f"\n[bold]查詢:[/bold] {query}")

        # 生成查詢嵌入
        query_embedding = generate_embedding(query, model)

        if not query_embedding:
            return None

        # 生成所有文檔的嵌入並計算相似度
        similarities = []

        console.print("\n[dim]正在計算文檔相似度...[/dim]")

        for i, doc in enumerate(documents):
            doc_embedding = generate_embedding(doc, model)

            if doc_embedding:
                similarity = cosine_similarity(query_embedding, doc_embedding)
                similarities.append((i, doc, similarity))

        # 排序並獲取 top_k
        similarities.sort(key=lambda x: x[2], reverse=True)
        top_results = similarities[:top_k]

        # 顯示結果
        console.print(f"\n[bold green]Top {top_k} 搜索結果:[/bold green]")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("排名", justify="right", style="cyan", width=6)
        table.add_column("文檔", style="yellow", width=50)
        table.add_column("相似度", justify="right", style="green", width=10)

        for rank, (idx, doc, sim) in enumerate(top_results, 1):
            table.add_row(
                str(rank),
                doc[:50] + "..." if len(doc) > 50 else doc,
                f"{sim:.4f}"
            )

        console.print(table)

        return top_results

    except Exception as e:
        console.print(f"[red]語義搜索失敗: {e}[/red]")
        return None


def batch_embeddings(texts, model='nomic-embed-text'):
    """批量生成嵌入"""
    try:
        console.print("\n[bold cyan]批量嵌入生成[/bold cyan]")
        console.print(f"[dim]文本數量: {len(texts)}[/dim]")

        embeddings = []

        for i, text in enumerate(texts, 1):
            console.print(f"[dim]處理 {i}/{len(texts)}: {text[:30]}...[/dim]")

            embedding = generate_embedding(text, model)

            if embedding:
                embeddings.append(embedding)

        console.print(f"\n[green]✓ 已生成 {len(embeddings)} 個嵌入向量[/green]")

        return embeddings

    except Exception as e:
        console.print(f"[red]批量嵌入失敗: {e}[/red]")
        return None


def document_clustering(documents, model='nomic-embed-text', threshold=0.7):
    """文檔聚類（基於相似度）"""
    try:
        console.print("\n[bold cyan]文檔聚類示例[/bold cyan]")
        console.print(f"[dim]相似度閾值: {threshold}[/dim]")

        # 生成所有文檔的嵌入
        console.print("\n[dim]生成文檔嵌入...[/dim]")
        embeddings = batch_embeddings(documents, model)

        if not embeddings or len(embeddings) != len(documents):
            return None

        # 簡單聚類：找出相似的文檔對
        clusters = []

        console.print("\n[bold]相似文檔對（相似度 > {:.2f}）:[/bold]".format(threshold))

        for i in range(len(documents)):
            for j in range(i + 1, len(documents)):
                similarity = cosine_similarity(embeddings[i], embeddings[j])

                if similarity > threshold:
                    console.print(f"\n[yellow]相似度: {similarity:.4f}[/yellow]")
                    console.print(f"  文檔 {i+1}: {documents[i][:50]}...")
                    console.print(f"  文檔 {j+1}: {documents[j][:50]}...")
                    clusters.append((i, j, similarity))

        if not clusters:
            console.print("[dim]未找到相似度超過閾值的文檔對[/dim]")

        return clusters

    except Exception as e:
        console.print(f"[red]文檔聚類失敗: {e}[/red]")
        return None


def rag_example(model='nomic-embed-text', llm_model='llama3.2'):
    """RAG（檢索增強生成）示例"""
    try:
        console.print("\n[bold cyan]RAG 示例[/bold cyan]")

        # 知識庫文檔
        knowledge_base = [
            "Ollama 是一個本地運行大型語言模型的框架，支持 Llama、Mistral 等多種模型。",
            "Python 是一種高級編程語言，廣泛應用於 Web 開發、數據科學和人工智能。",
            "向量嵌入是將文本轉換為數值向量的過程，可用於相似度計算和語義搜索。",
            "RAG 技術結合了檢索和生成，先檢索相關文檔，再基於檢索結果生成答案。",
            "機器學習是人工智能的一個分支，通過數據訓練模型來完成特定任務。"
        ]

        # 用戶查詢
        query = "什麼是 RAG？它如何工作？"

        console.print(f"\n[bold]用戶問題:[/bold] {query}")

        # 步驟 1: 語義搜索找到相關文檔
        console.print("\n[bold yellow]步驟 1: 檢索相關文檔[/bold yellow]")

        query_embedding = generate_embedding(query, model)
        similarities = []

        for doc in knowledge_base:
            doc_embedding = generate_embedding(doc, model)
            if doc_embedding and query_embedding:
                sim = cosine_similarity(query_embedding, doc_embedding)
                similarities.append((doc, sim))

        # 獲取最相關的文檔
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_docs = similarities[:2]

        console.print("\n[green]檢索到的相關文檔:[/green]")
        for i, (doc, sim) in enumerate(top_docs, 1):
            console.print(f"  {i}. (相似度: {sim:.4f}) {doc}")

        # 步驟 2: 使用檢索到的文檔生成答案
        console.print("\n[bold yellow]步驟 2: 基於檢索結果生成答案[/bold yellow]")

        # 構建提示詞
        context = "\n".join([doc for doc, _ in top_docs])
        prompt = f"""基於以下背景信息回答問題。如果背景信息不包含答案，請說明。

背景信息:
{context}

問題: {query}

答案:"""

        console.print("\n[dim]生成答案中...[/dim]")

        # 生成答案
        response = ollama.chat(
            model=llm_model,
            messages=[
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
        )

        answer = response['message']['content']

        console.print(Panel(
            answer,
            title="[bold green]RAG 生成的答案[/bold green]",
            border_style="green"
        ))

        return answer

    except Exception as e:
        console.print(f"[red]RAG 示例失敗: {e}[/red]")
        return None


def compare_embedding_models():
    """比較不同嵌入模型"""
    try:
        console.print("\n[bold cyan]嵌入模型比較[/bold cyan]")

        models = ['nomic-embed-text', 'mxbai-embed-large', 'all-minilm']

        text = "人工智能正在改變世界"

        console.print(f"\n[bold]測試文本:[/bold] {text}")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("模型", style="cyan", width=25)
        table.add_column("維度", justify="right", style="yellow", width=10)
        table.add_column("狀態", style="green", width=15)

        for model in models:
            try:
                embedding = generate_embedding(text, model)

                if embedding:
                    table.add_row(
                        model,
                        str(len(embedding)),
                        "✓ 可用"
                    )
                else:
                    table.add_row(
                        model,
                        "-",
                        "✗ 失敗"
                    )

            except Exception as e:
                table.add_row(
                    model,
                    "-",
                    f"✗ 未安裝"
                )

        console.print(table)

        console.print("\n[dim]注意: 需要先下載模型[/dim]")
        console.print("[dim]下載命令: ollama pull <model-name>[/dim]")

    except Exception as e:
        console.print(f"[red]模型比較失敗: {e}[/red]")


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Ollama 嵌入向量示例[/bold cyan]",
        border_style="cyan"
    ))

    embed_model = 'nomic-embed-text'
    llm_model = 'llama3.2'

    console.print(f"\n[dim]嵌入模型: {embed_model}[/dim]")
    console.print(f"[dim]LLM 模型: {llm_model}[/dim]")
    console.print("[dim]確保已下載: ollama pull nomic-embed-text[/dim]")

    # 1. 基礎嵌入
    console.print("\n[bold]示例 1: 基礎嵌入生成[/bold]")
    basic_embedding_demo(embed_model)

    # 2. 相似度比較
    console.print("\n[bold]示例 2: 文本相似度比較[/bold]")
    similarity_comparison(embed_model)

    # 3. 語義搜索
    console.print("\n[bold]示例 3: 語義搜索[/bold]")
    documents = [
        "Python 是一種流行的編程語言，廣泛用於 AI 開發。",
        "機器學習模型需要大量數據進行訓練。",
        "深度學習是機器學習的一個子領域。",
        "自然語言處理用於理解和生成人類語言。",
        "計算機視覺使機器能夠理解圖像和視頻。",
        "強化學習通過試錯來學習最優策略。"
    ]
    semantic_search("如何訓練 AI 模型？", documents, embed_model, top_k=3)

    # 4. 文檔聚類
    console.print("\n[bold]示例 4: 文檔聚類[/bold]")
    cluster_docs = [
        "機器學習是 AI 的核心技術",
        "深度學習使用神經網絡",
        "Python 是編程語言",
        "Java 是另一種編程語言",
        "AI 包括機器學習和深度學習"
    ]
    document_clustering(cluster_docs, embed_model, threshold=0.5)

    # 5. RAG 示例
    console.print("\n[bold]示例 5: RAG（檢索增強生成）[/bold]")
    rag_example(embed_model, llm_model)

    # 6. 模型比較
    console.print("\n[bold]示例 6: 嵌入模型比較[/bold]")
    compare_embedding_models()

    # 完成
    console.print("\n" + "="*60)
    console.print("[bold green]✓ 嵌入向量示例完成！[/bold green]")
    console.print("\n[cyan]關鍵要點:[/cyan]")
    console.print("  1. 嵌入向量將文本轉換為數值表示")
    console.print("  2. 餘弦相似度用於測量文本相似性")
    console.print("  3. 語義搜索基於含義而非關鍵詞")
    console.print("  4. RAG 結合檢索和生成提升準確性")


if __name__ == "__main__":
    main()

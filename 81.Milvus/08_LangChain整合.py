"""
Milvus 與 LangChain 整合示例

本示例展示：
1. LangChain + Milvus 設置
2. 文檔向量化和存儲
3. RAG 問答系統
4. 語義搜索應用
"""

from pymilvus import connections, utility
from langchain_milvus import Milvus
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
import os
from dotenv import load_dotenv

load_dotenv()

console = Console()


def setup_milvus_connection():
    """設置 Milvus 連接"""
    console.print("[cyan]連接到 Milvus...[/cyan]")

    connections.connect(
        alias="default",
        host='localhost',
        port='19530'
    )

    console.print("[green]✓ Milvus 連接成功[/green]\n")


def create_knowledge_base():
    """創建知識庫"""
    console.print("[bold cyan]1. 創建知識庫[/bold cyan]")

    # 準備文檔
    documents = [
        "Milvus 是一個開源的向量數據庫,支持萬億級向量數據的存儲和檢索。",
        "Milvus 提供多種索引類型,包括 FLAT、IVF_FLAT、HNSW 等。",
        "LangChain 是一個用於開發基於語言模型的應用程序的框架。",
        "RAG（檢索增強生成）結合了信息檢索和文本生成,能夠基於實時數據回答問題。",
        "向量嵌入是將文本轉換為數值向量的技術,使得計算機能夠理解語義相似性。",
        "Milvus 支持分布式部署,可以水平擴展以處理大規模數據。",
        "語義搜索通過向量相似度匹配,能夠找到意義相關但用詞不同的內容。",
        "HNSW 是一種基於圖的索引,提供高召回率和快速搜索性能。",
    ]

    # 創建嵌入模型
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # 創建 Milvus 向量存儲
    collection_name = "langchain_demo"

    # 清理舊集合
    if utility.has_collection(collection_name):
        utility.drop_collection(collection_name)

    # 創建向量存儲
    vector_store = Milvus.from_texts(
        texts=documents,
        embedding=embeddings,
        collection_name=collection_name,
        connection_args={"host": "localhost", "port": "19530"}
    )

    console.print(f"[green]✓ 知識庫創建成功[/green]")
    console.print(f"[dim]集合名稱: {collection_name}[/dim]")
    console.print(f"[dim]文檔數量: {len(documents)}[/dim]\n")

    return vector_store


def semantic_search(vector_store):
    """語義搜索"""
    console.print("[bold cyan]2. 語義搜索[/bold cyan]")

    query = "如何進行大規模向量檢索？"
    console.print(f"[yellow]查詢: {query}[/yellow]\n")

    # 執行相似度搜索
    results = vector_store.similarity_search(query, k=3)

    console.print("[bold]搜索結果:[/bold]")
    for i, doc in enumerate(results, 1):
        console.print(f"{i}. {doc.page_content}\n")


def rag_qa_system(vector_store):
    """RAG 問答系統"""
    console.print("[bold cyan]3. RAG 問答系統[/bold cyan]")

    # 創建檢索器
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 2}
    )

    # 創建 LLM
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # 創建 QA 鏈
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True
    )

    # 問答示例
    questions = [
        "什麼是 Milvus？",
        "RAG 的作用是什麼？",
        "HNSW 索引有什麼特點？"
    ]

    for question in questions:
        console.print(f"\n[yellow]問題: {question}[/yellow]")

        result = qa_chain.invoke({"query": question})

        console.print(Panel(
            Markdown(result["result"]),
            title="[bold green]回答[/bold green]",
            border_style="green"
        ))

        console.print("[dim]來源文檔:[/dim]")
        for doc in result["source_documents"]:
            console.print(f"  • {doc.page_content[:60]}...")

    console.print()


def advanced_rag_example():
    """進階 RAG 示例"""
    console.print("[bold cyan]4. 進階 RAG 配置[/bold cyan]")

    # 示例代碼
    code = """
# 文檔分塊
from langchain.text_splitter import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    length_function=len
)

chunks = text_splitter.split_documents(documents)

# 創建向量存儲（帶元數據）
from langchain_milvus import Milvus
from langchain_openai import OpenAIEmbeddings

vector_store = Milvus.from_documents(
    documents=chunks,
    embedding=OpenAIEmbeddings(),
    collection_name="advanced_rag",
    connection_args={
        "host": "localhost",
        "port": "19530"
    },
    # Milvus 索引參數
    index_params={
        "index_type": "HNSW",
        "metric_type": "L2",
        "params": {"M": 8, "efConstruction": 64}
    },
    # 搜索參數
    search_params={
        "metric_type": "L2",
        "params": {"ef": 64}
    }
)

# 使用 MMR (Maximal Marginal Relevance) 檢索
retriever = vector_store.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 5, "fetch_k": 20, "lambda_mult": 0.5}
)

# 創建對話鏈
from langchain.chains import ConversationalRetrievalChain

qa = ConversationalRetrievalChain.from_llm(
    llm=ChatOpenAI(model="gpt-4o"),
    retriever=retriever,
    return_source_documents=True
)
"""

    console.print(code)


def langchain_best_practices():
    """LangChain + Milvus 最佳實踐"""
    console.print("[bold cyan]5. 最佳實踐[/bold cyan]")

    from rich.table import Table

    practices = [
        ("文檔分塊", "合理設置 chunk_size (通常 500-1000)"),
        ("嵌入模型", "選擇合適的嵌入模型 (quality vs cost)"),
        ("索引優化", "根據數據規模選擇索引類型"),
        ("檢索策略", "使用 MMR 提升結果多樣性"),
        ("元數據過濾", "利用元數據縮小搜索範圍"),
        ("緩存", "緩存常見查詢的嵌入向量"),
        ("批處理", "批量處理文檔提升效率"),
        ("監控", "監控搜索質量和性能"),
    ]

    table = Table(title="LangChain + Milvus 最佳實踐")
    table.add_column("主題", style="cyan", width=15)
    table.add_column("建議", style="green", width=40)

    for topic, advice in practices:
        table.add_row(topic, advice)

    console.print(table)


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Milvus 與 LangChain 整合示例[/bold cyan]",
        border_style="cyan"
    ))

    # 檢查 OpenAI API Key
    if not os.getenv("OPENAI_API_KEY"):
        console.print("[red]錯誤: 請設置 OPENAI_API_KEY 環境變數[/red]")
        console.print("[yellow]在 .env 文件中添加: OPENAI_API_KEY=your-key-here[/yellow]")
        return

    # 設置連接
    setup_milvus_connection()

    # 1. 創建知識庫
    vector_store = create_knowledge_base()

    # 2. 語義搜索
    semantic_search(vector_store)

    # 3. RAG 問答
    rag_qa_system(vector_store)

    # 4. 進階示例
    advanced_rag_example()

    # 5. 最佳實踐
    langchain_best_practices()

    console.print("\n" + "="*60)
    console.print("[bold green]✓ LangChain 整合示例完成！[/bold green]")

    # 清理
    if utility.has_collection("langchain_demo"):
        utility.drop_collection("langchain_demo")

    connections.disconnect("default")


if __name__ == "__main__":
    main()

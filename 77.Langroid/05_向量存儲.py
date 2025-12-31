"""
Langroid 向量存儲 - RAG 和語義搜索

這個示例展示：
1. 配置向量數據庫
2. 文檔索引
3. RAG 實現
4. 語義搜索

Langroid 內建向量存儲支持，輕鬆實現 RAG。
"""

from rich.console import Console
from rich.panel import Panel

console = Console()


def vector_store_basics():
    """向量存儲基礎"""
    console.print(Panel("[bold cyan]向量存儲基礎[/bold cyan]"))

    console.print("""
[yellow]Langroid 向量存儲：[/yellow]

Langroid 支持多種向量數據庫：
- ChromaDB（默認）
- Qdrant
- Weaviate
- LanceDB

[yellow]基本用法：[/yellow]
    """)

    code = '''
import langroid as lr
from langroid.vector_store import QdrantDBConfig

# 配置向量數據庫
vector_config = QdrantDBConfig(
    collection_name="my_docs",
    storage_path=".qdrant",  # 本地存儲
)

# 創建 Agent 配置（帶向量存儲）
agent_config = lr.ChatAgentConfig(
    llm=lr.language_models.OpenAIGPTConfig(
        chat_model="gpt-4o-mini"
    ),
    vecdb=vector_config,
    system_message="你可以檢索文檔回答問題"
)

# 創建 Agent
agent = lr.ChatAgent(agent_config)

# 添加文檔
documents = [
    "Python 是一種高級編程語言",
    "JavaScript 用於 Web 開發",
    "Rust 是一種系統編程語言"
]

for doc in documents:
    agent.vecdb.add_documents([doc])

# 搜索
results = agent.vecdb.similar_texts("編程語言", k=2)
    '''

    console.print(Panel(code, border_style="blue"))


def rag_implementation():
    """RAG 實現"""
    console.print(Panel("[bold cyan]RAG 實現[/bold cyan]"))

    console.print("""
[yellow]RAG（檢索增強生成）流程：[/yellow]

1. 將知識庫文檔索引到向量數據庫
2. 用戶提問時，檢索相關文檔
3. 將相關文檔作為上下文傳遞給 LLM
4. LLM 基於檢索到的信息回答問題

[yellow]Langroid RAG 示例：[/yellow]
    """)

    rag_code = '''
# 創建帶 RAG 的 Agent
class RAGAgent(lr.ChatAgent):
    """RAG Agent"""

    def llm_response(self, message: str):
        # 1. 檢索相關文檔
        relevant_docs = self.vecdb.similar_texts(message, k=3)

        # 2. 構建上下文
        context = "\\n\\n".join([
            f"文檔 {i+1}: {doc}"
            for i, doc in enumerate(relevant_docs)
        ])

        # 3. 組合消息
        enhanced_message = f"""
基於以下文檔回答問題：

{context}

問題：{message}
        """

        # 4. 調用 LLM
        return super().llm_response(enhanced_message)

# 使用
agent = RAGAgent(config)

# 添加知識庫
knowledge_base = [
    "Langroid 是一個 Python 框架...",
    "Langroid 支持多 Agent...",
    # 更多文檔
]

for doc in knowledge_base:
    agent.vecdb.add_documents([doc])

# 查詢
response = agent.llm_response("Langroid 有什麼特點？")
    '''

    console.print(Panel(rag_code, border_style="blue"))


def semantic_search():
    """語義搜索"""
    console.print(Panel("[bold cyan]語義搜索[/bold cyan]"))

    console.print("""
[yellow]語義搜索示例：[/yellow]

向量數據庫支持語義搜索，而不僅僅是關鍵詞匹配：
    """)

    search_code = '''
# 配置
config = lr.ChatAgentConfig(
    vecdb=QdrantDBConfig(collection_name="search_demo")
)

agent = lr.ChatAgent(config)

# 索引文檔
docs = [
    "機器學習是人工智能的一個分支",
    "深度學習使用神經網絡",
    "Python 是數據科學的首選語言",
    "TensorFlow 是深度學習框架",
]

agent.vecdb.add_documents(docs)

# 語義搜索（不需要精確匹配）
query = "AI 和神經網絡"
results = agent.vecdb.similar_texts(query, k=2)

# 結果會包含語義相關的文檔：
# "深度學習使用神經網絡"
# "機器學習是人工智能的一個分支"
    '''

    console.print(Panel(search_code, border_style="blue"))


def vector_store_config():
    """向量存儲配置"""
    console.print(Panel("[bold cyan]向量存儲配置[/bold cyan]"))

    console.print("""
[yellow]向量存儲配置選項：[/yellow]

1. [cyan]嵌入模型[/cyan]
   - OpenAI embeddings (默認)
   - HuggingFace embeddings
   - 自定義嵌入模型

2. [cyan]存儲配置[/cyan]
   - 本地存儲
   - 雲端存儲
   - 內存存儲

3. [cyan]檢索參數[/cyan]
   - k: 返回文檔數
   - score_threshold: 相似度閾值
   - filter: 元數據過濾

[yellow]配置示例：[/yellow]
    """)

    config_code = '''
from langroid.vector_store import QdrantDBConfig
from langroid.embedding_models import OpenAIEmbeddingsConfig

# 嵌入配置
embedding_config = OpenAIEmbeddingsConfig(
    model="text-embedding-3-small",
    dims=1536
)

# 向量數據庫配置
vecdb_config = QdrantDBConfig(
    collection_name="my_collection",
    storage_path=".qdrant_data",
    embedding=embedding_config,
)

# 使用
agent_config = lr.ChatAgentConfig(
    vecdb=vecdb_config,
    # 其他配置...
)
    '''

    console.print(Panel(config_code, border_style="blue"))


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold green]Langroid 向量存儲[/bold green]",
        border_style="green"
    ))

    vector_store_basics()
    console.print("\n" + "="*60 + "\n")

    rag_implementation()
    console.print("\n" + "="*60 + "\n")

    semantic_search()
    console.print("\n" + "="*60 + "\n")

    vector_store_config()

    console.print(Panel("""
[bold green]向量存儲完成！[/bold green]

關鍵要點：
1. Langroid 內建向量存儲支持
2. 輕鬆實現 RAG
3. 支持多種向量數據庫
4. 語義搜索而非關鍵詞匹配

RAG 最佳實踐：
- 合理分塊文檔
- 選擇合適的嵌入模型
- 優化檢索參數
- 實現重排序

下一步：查看 06_多Agent.py
    """, title="總結", border_style="green"))


if __name__ == "__main__":
    main()

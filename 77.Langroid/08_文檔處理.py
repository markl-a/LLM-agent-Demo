"""
Langroid 文檔處理 - 處理各種文檔

這個示例展示：
1. PDF 處理
2. 文本文檔處理
3. 文檔分塊策略
4. 文檔問答系統

Langroid 提供豐富的文檔處理能力。
"""

from rich.console import Console
from rich.panel import Panel

console = Console()


def document_loading():
    """文檔加載"""
    console.print(Panel("[bold cyan]文檔加載[/bold cyan]"))

    console.print("""
[yellow]Langroid 支持多種文檔格式：[/yellow]

- PDF
- Word (.docx)
- 純文本 (.txt)
- Markdown (.md)
- HTML

[yellow]加載文檔示例：[/yellow]
    """)

    code = '''
from langroid.parsing.parser import Parser

# 創建解析器
parser = Parser()

# 加載 PDF
pdf_docs = parser.get_doc_chunks("document.pdf")

# 加載文本文件
txt_docs = parser.get_doc_chunks("document.txt")

# 加載目錄中的所有文檔
all_docs = parser.get_doc_chunks("./documents/")

# 文檔分塊參數
docs = parser.get_doc_chunks(
    "document.pdf",
    chunk_size=500,  # 每塊大小
    chunk_overlap=50,  # 重疊大小
)
    '''

    console.print(Panel(code, border_style="blue"))


def document_qa():
    """文檔問答系統"""
    console.print(Panel("[bold cyan]文檔問答系統[/bold cyan]"))

    console.print("""
[yellow]構建文檔問答系統：[/yellow]

結合向量存儲和 Agent：
    """)

    qa_code = '''
import langroid as lr
from langroid.parsing.parser import Parser
from langroid.vector_store import QdrantDBConfig

# 1. 加載文檔
parser = Parser()
documents = parser.get_doc_chunks("knowledge_base.pdf")

# 2. 配置向量存儲
vecdb_config = QdrantDBConfig(
    collection_name="doc_qa",
    storage_path=".qdrant"
)

# 3. 創建 Agent
agent = lr.ChatAgent(
    config=lr.ChatAgentConfig(
        llm=lr.language_models.OpenAIGPTConfig(
            chat_model="gpt-4o-mini"
        ),
        vecdb=vecdb_config,
        system_message="""
你是文檔問答助手。
基於提供的文檔回答問題。
如果文檔中沒有相關信息，請說明。
        """
    )
)

# 4. 索引文檔
for doc in documents:
    agent.vecdb.add_documents([doc])

# 5. 問答
task = lr.Task(agent, interactive=False)

questions = [
    "文檔的主要內容是什麼？",
    "關於X的部分在哪裡？",
    "文檔提到了哪些關鍵點？"
]

for q in questions:
    answer = task.run(q)
    print(f"Q: {q}")
    print(f"A: {answer.content}\\n")
    '''

    console.print(Panel(qa_code, border_style="blue"))


def chunking_strategies():
    """分塊策略"""
    console.print(Panel("[bold cyan]文檔分塊策略[/bold cyan]"))

    console.print("""
[yellow]文檔分塊的重要性：[/yellow]

- 適應模型的上下文限制
- 提高檢索準確性
- 優化處理效率

[yellow]分塊策略：[/yellow]

1. [cyan]固定大小分塊[/cyan]
   - 簡單直接
   - 可能切斷語義

2. [cyan]語義分塊[/cyan]
   - 按段落或章節
   - 保持語義完整

3. [cyan]重疊分塊[/cyan]
   - 塊之間有重疊
   - 避免信息丟失

[yellow]分塊配置：[/yellow]
    """)

    chunk_code = '''
from langroid.parsing.parser import Parser, ParsingConfig

# 配置分塊參數
config = ParsingConfig(
    chunk_size=500,  # 每塊字符數
    chunk_overlap=50,  # 重疊字符數
    separators=["\\n\\n", "\\n", ". "],  # 分隔符優先級
)

parser = Parser(config)

# 使用配置
docs = parser.get_doc_chunks("document.pdf")

# 每個文檔塊包含：
# - 內容 (content)
# - 元數據 (metadata)
# - 來源信息 (source)

for doc in docs:
    print(f"內容: {doc.content[:100]}...")
    print(f"來源: {doc.metadata.get('source')}")
    print(f"頁碼: {doc.metadata.get('page')}")
    '''

    console.print(Panel(chunk_code, border_style="blue"))


def advanced_doc_processing():
    """高級文檔處理"""
    console.print(Panel("[bold cyan]高級文檔處理[/bold cyan]"))

    console.print("""
[yellow]高級文檔處理技巧：[/yellow]

1. [cyan]元數據提取[/cyan]
   - 提取標題、作者等
   - 用於過濾和檢索

2. [cyan]文檔結構分析[/cyan]
   - 識別章節結構
   - 提取目錄

3. [cyan]多文檔整合[/cyan]
   - 合併多個文檔
   - 跨文檔檢索

4. [cyan]文檔總結[/cyan]
   - 生成文檔摘要
   - 提取關鍵信息

[yellow]文檔總結示例：[/yellow]
    """)

    advanced_code = '''
class DocumentSummarizer:
    """文檔總結器"""

    def __init__(self):
        self.agent = lr.ChatAgent(
            config=lr.ChatAgentConfig(
                system_message="你是專業的文檔總結專家"
            )
        )

    def summarize_document(self, doc_path: str) -> str:
        """總結文檔"""
        # 1. 加載文檔
        parser = Parser()
        chunks = parser.get_doc_chunks(doc_path)

        # 2. 總結每個分塊
        chunk_summaries = []
        task = lr.Task(self.agent, interactive=False)

        for chunk in chunks:
            summary = task.run(
                f"總結以下內容（100字內）：\\n{chunk.content}"
            )
            chunk_summaries.append(summary.content)

        # 3. 整合總結
        combined = "\\n\\n".join(chunk_summaries)
        final_summary = task.run(
            f"整合以下總結為完整摘要：\\n{combined}"
        )

        return final_summary.content

# 使用
summarizer = DocumentSummarizer()
summary = summarizer.summarize_document("long_document.pdf")
    '''

    console.print(Panel(advanced_code, border_style="blue"))


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold green]Langroid 文檔處理[/bold green]",
        border_style="green"
    ))

    document_loading()
    console.print("\n" + "="*60 + "\n")

    document_qa()
    console.print("\n" + "="*60 + "\n")

    chunking_strategies()
    console.print("\n" + "="*60 + "\n")

    advanced_doc_processing()

    console.print(Panel("""
[bold green]文檔處理完成！[/bold green]

關鍵要點：
1. 支持多種文檔格式
2. 靈活的分塊策略
3. 結合向量存儲實現 RAG
4. 高級處理功能

文檔處理最佳實踐：
- 選擇合適的分塊大小
- 使用重疊避免信息丟失
- 保留文檔元數據
- 實現增量索引

下一步：查看 09_代碼生成.py
    """, title="總結", border_style="green"))


if __name__ == "__main__":
    main()

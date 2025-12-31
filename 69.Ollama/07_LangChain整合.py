"""
Ollama 與 LangChain 整合示例

本示例展示：
1. LangChain Ollama 基礎配置
2. 鏈式調用
3. Prompt 模板
4. 記憶功能
5. RAG 應用
"""

from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table

console = Console()


def basic_langchain_ollama(model_name='llama3.2'):
    """基礎 LangChain Ollama 使用"""
    try:
        console.print("\n[bold cyan]基礎 LangChain Ollama[/bold cyan]")

        # 初始化 Ollama LLM
        llm = OllamaLLM(
            model=model_name,
            temperature=0.7
        )

        console.print(f"[dim]模型: {model_name}[/dim]")

        # 簡單調用
        question = "用一句話解釋什麼是量子計算"
        console.print(f"\n[bold]問題:[/bold] {question}")

        response = llm.invoke(question)

        console.print(Panel(
            Markdown(response),
            title="[bold green]LLM 響應[/bold green]",
            border_style="green"
        ))

        return response

    except Exception as e:
        console.print(f"[red]基礎使用失敗: {e}[/red]")
        return None


def prompt_template_example(model_name='llama3.2'):
    """Prompt 模板示例"""
    try:
        console.print("\n[bold cyan]Prompt 模板示例[/bold cyan]")

        # 創建 LLM
        llm = OllamaLLM(model=model_name)

        # 創建 Prompt 模板
        template = """你是一位專業的 {role}。

任務: {task}

要求:
1. 回答要專業且詳細
2. 使用適當的專業術語
3. 提供實用的建議

請開始回答:"""

        prompt = PromptTemplate(
            input_variables=["role", "task"],
            template=template
        )

        # 創建鏈
        chain = prompt | llm | StrOutputParser()

        # 示例 1: Python 導師
        console.print("\n[bold yellow]示例 1: Python 導師[/bold yellow]")

        result1 = chain.invoke({
            "role": "Python 編程導師",
            "task": "解釋列表推導式的優勢"
        })

        console.print(Panel(
            Markdown(result1),
            title="[bold green]Python 導師的回答[/bold green]",
            border_style="green"
        ))

        # 示例 2: 數據科學家
        console.print("\n[bold yellow]示例 2: 數據科學家[/bold yellow]")

        result2 = chain.invoke({
            "role": "資深數據科學家",
            "task": "說明如何選擇合適的機器學習算法"
        })

        console.print(Panel(
            Markdown(result2),
            title="[bold green]數據科學家的回答[/bold green]",
            border_style="green"
        ))

        return chain

    except Exception as e:
        console.print(f"[red]Prompt 模板示例失敗: {e}[/red]")
        return None


def chat_with_memory(model_name='llama3.2'):
    """帶記憶的對話鏈"""
    try:
        console.print("\n[bold cyan]帶記憶的對話鏈[/bold cyan]")

        # 創建 LLM
        llm = OllamaLLM(
            model=model_name,
            temperature=0.7
        )

        # 創建記憶
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

        # 創建 Prompt 模板
        template = """你是一個友好的 AI 助手。請基於對話歷史回答問題。

對話歷史:
{chat_history}

當前問題: {question}

回答:"""

        prompt = PromptTemplate(
            input_variables=["chat_history", "question"],
            template=template
        )

        # 創建鏈
        chain = LLMChain(
            llm=llm,
            prompt=prompt,
            memory=memory,
            verbose=False
        )

        # 多輪對話
        questions = [
            "我叫張三，我想學習 AI",
            "我應該從哪裡開始？",
            "你還記得我的名字嗎？"
        ]

        for i, question in enumerate(questions, 1):
            console.print(f"\n[bold yellow]第 {i} 輪對話[/bold yellow]")
            console.print(f"[bold]用戶:[/bold] {question}")

            response = chain.invoke({"question": question})
            answer = response.get('text', '')

            console.print(Panel(
                Markdown(answer),
                title=f"[bold green]助手 (第{i}輪)[/bold green]",
                border_style="green"
            ))

        # 顯示記憶內容
        console.print("\n[dim]對話記憶已保存，AI 可以記住之前的對話內容[/dim]")

        return chain

    except Exception as e:
        console.print(f"[red]記憶對話失敗: {e}[/red]")
        return None


def rag_with_langchain(model_name='llama3.2', embed_model='nomic-embed-text'):
    """使用 LangChain 實現 RAG"""
    try:
        console.print("\n[bold cyan]LangChain RAG 示例[/bold cyan]")

        # 模擬文檔數據庫
        documents = [
            "Ollama 是一個本地運行大型語言模型的框架，支持多種開源模型。",
            "LangChain 是一個用於構建 LLM 應用的框架，提供鏈式調用和組件化功能。",
            "RAG（檢索增強生成）結合了信息檢索和文本生成，可以提升回答準確性。",
            "向量嵌入可以將文本轉換為數值向量，用於語義相似度計算。",
            "Python 是 AI 開發中最流行的編程語言，擁有豐富的機器學習庫。"
        ]

        console.print(f"\n[dim]知識庫文檔數: {len(documents)}[/dim]")

        # 創建嵌入模型
        console.print("[dim]初始化嵌入模型...[/dim]")
        embeddings = OllamaEmbeddings(model=embed_model)

        # 為每個文檔生成嵌入
        console.print("[dim]生成文檔嵌入...[/dim]")
        doc_embeddings = []
        for doc in documents:
            emb = embeddings.embed_query(doc)
            doc_embeddings.append(emb)

        console.print(f"[green]✓ 已生成 {len(doc_embeddings)} 個文檔嵌入[/green]")

        # 用戶查詢
        query = "什麼是 RAG？"
        console.print(f"\n[bold]查詢:[/bold] {query}")

        # 生成查詢嵌入
        query_embedding = embeddings.embed_query(query)

        # 計算相似度（簡單實現）
        import numpy as np

        def cosine_similarity(vec1, vec2):
            return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

        # 找到最相關的文檔
        similarities = [
            (doc, cosine_similarity(query_embedding, doc_emb))
            for doc, doc_emb in zip(documents, doc_embeddings)
        ]
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_docs = similarities[:2]

        console.print("\n[green]檢索到的相關文檔:[/green]")
        for i, (doc, sim) in enumerate(top_docs, 1):
            console.print(f"  {i}. (相似度: {sim:.4f}) {doc}")

        # 創建 RAG 鏈
        llm = OllamaLLM(model=model_name)

        # 構建提示詞
        context = "\n".join([doc for doc, _ in top_docs])

        template = """基於以下背景信息回答問題。如果背景信息不包含答案，請誠實地說不知道。

背景信息:
{context}

問題: {question}

回答:"""

        prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=template
        )

        # 創建並執行鏈
        chain = (
            {"context": lambda x: context, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

        console.print("\n[dim]生成答案中...[/dim]")
        answer = chain.invoke(query)

        console.print(Panel(
            Markdown(answer),
            title="[bold green]RAG 生成的答案[/bold green]",
            border_style="green"
        ))

        return answer

    except Exception as e:
        console.print(f"[red]RAG 示例失敗: {e}[/red]")
        console.print(f"[yellow]提示: 確保已安裝 numpy 和下載嵌入模型[/yellow]")
        return None


def sequential_chain_example(model_name='llama3.2'):
    """順序鏈示例"""
    try:
        console.print("\n[bold cyan]順序鏈示例[/bold cyan]")
        console.print("[dim]第一個鏈生成想法，第二個鏈評估想法[/dim]")

        llm = OllamaLLM(model=model_name)

        # 第一個鏈：生成想法
        idea_template = """請為以下主題提出一個創新的想法:

主題: {topic}

想法:"""

        idea_prompt = PromptTemplate(
            input_variables=["topic"],
            template=idea_template
        )

        idea_chain = idea_prompt | llm | StrOutputParser()

        # 第二個鏈：評估想法
        evaluate_template = """請評估以下想法的可行性和創新性:

想法: {idea}

評估（包括優點、缺點和建議）:"""

        evaluate_prompt = PromptTemplate(
            input_variables=["idea"],
            template=evaluate_template
        )

        evaluate_chain = evaluate_prompt | llm | StrOutputParser()

        # 執行順序鏈
        topic = "使用 AI 改善在線教育"

        console.print(f"\n[bold]主題:[/bold] {topic}")

        # 步驟 1: 生成想法
        console.print("\n[bold yellow]步驟 1: 生成想法[/bold yellow]")
        idea = idea_chain.invoke({"topic": topic})

        console.print(Panel(
            Markdown(idea),
            title="[bold green]生成的想法[/bold green]",
            border_style="green"
        ))

        # 步驟 2: 評估想法
        console.print("\n[bold yellow]步驟 2: 評估想法[/bold yellow]")
        evaluation = evaluate_chain.invoke({"idea": idea})

        console.print(Panel(
            Markdown(evaluation),
            title="[bold green]評估結果[/bold green]",
            border_style="green"
        ))

        return {"idea": idea, "evaluation": evaluation}

    except Exception as e:
        console.print(f"[red]順序鏈示例失敗: {e}[/red]")
        return None


def output_parser_example(model_name='llama3.2'):
    """輸出解析器示例"""
    try:
        console.print("\n[bold cyan]輸出解析器示例[/bold cyan]")

        llm = OllamaLLM(model=model_name, temperature=0.1)

        # 使用 JSON 格式輸出
        template = """請從以下文本中提取信息，並以 JSON 格式返回。
只返回 JSON，不要其他內容。

文本: {text}

要提取的信息:
- name: 姓名
- age: 年齡
- occupation: 職業
- hobbies: 愛好（數組）

JSON:"""

        prompt = PromptTemplate(
            input_variables=["text"],
            template=template
        )

        chain = prompt | llm | StrOutputParser()

        # 示例文本
        text = "李四今年28歲，是一名軟件工程師，平時喜歡攝影、登山和閱讀。"

        console.print(f"\n[bold]輸入文本:[/bold] {text}")

        result = chain.invoke({"text": text})

        console.print("\n[bold green]提取的結構化數據:[/bold green]")

        try:
            import json
            parsed = json.loads(result)
            console.print(Panel(
                json.dumps(parsed, indent=2, ensure_ascii=False),
                border_style="green"
            ))
        except:
            # 如果不是有效 JSON，直接顯示
            console.print(Panel(result, border_style="yellow"))

        return result

    except Exception as e:
        console.print(f"[red]輸出解析器示例失敗: {e}[/red]")
        return None


def compare_configurations(model_name='llama3.2'):
    """比較不同的配置"""
    try:
        console.print("\n[bold cyan]配置比較[/bold cyan]")

        configurations = [
            {"temperature": 0.0, "name": "確定性（Temperature=0.0）"},
            {"temperature": 0.5, "name": "平衡（Temperature=0.5）"},
            {"temperature": 1.0, "name": "創造性（Temperature=1.0）"}
        ]

        question = "描述一個未來城市的一天"

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("配置", style="cyan", width=25)
        table.add_column("響應預覽", style="yellow", width=50)

        for config in configurations:
            llm = OllamaLLM(
                model=model_name,
                temperature=config["temperature"]
            )

            response = llm.invoke(question)

            # 只顯示前 100 個字符
            preview = response[:100] + "..." if len(response) > 100 else response

            table.add_row(config["name"], preview)

        console.print(f"\n[bold]問題:[/bold] {question}\n")
        console.print(table)

        console.print("\n[dim]不同溫度產生不同風格的輸出[/dim]")

    except Exception as e:
        console.print(f"[red]配置比較失敗: {e}[/red]")


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Ollama LangChain 整合示例[/bold cyan]",
        border_style="cyan"
    ))

    model_name = 'llama3.2'
    embed_model = 'nomic-embed-text'

    console.print(f"\n[dim]LLM 模型: {model_name}[/dim]")
    console.print(f"[dim]嵌入模型: {embed_model}[/dim]")

    # 1. 基礎使用
    console.print("\n[bold]示例 1: 基礎 LangChain Ollama[/bold]")
    basic_langchain_ollama(model_name)

    # 2. Prompt 模板
    console.print("\n[bold]示例 2: Prompt 模板[/bold]")
    prompt_template_example(model_name)

    # 3. 帶記憶的對話
    console.print("\n[bold]示例 3: 帶記憶的對話[/bold]")
    chat_with_memory(model_name)

    # 4. RAG 示例
    console.print("\n[bold]示例 4: RAG（檢索增強生成）[/bold]")
    rag_with_langchain(model_name, embed_model)

    # 5. 順序鏈
    console.print("\n[bold]示例 5: 順序鏈[/bold]")
    sequential_chain_example(model_name)

    # 6. 輸出解析器
    console.print("\n[bold]示例 6: 輸出解析器[/bold]")
    output_parser_example(model_name)

    # 7. 配置比較
    console.print("\n[bold]示例 7: 配置比較[/bold]")
    compare_configurations(model_name)

    # 完成
    console.print("\n" + "="*60)
    console.print("[bold green]✓ LangChain 整合示例完成！[/bold green]")
    console.print("\n[cyan]關鍵要點:[/cyan]")
    console.print("  1. LangChain 提供高級抽象和組件化")
    console.print("  2. Prompt 模板使代碼更可維護")
    console.print("  3. 記憶功能支持上下文對話")
    console.print("  4. 鏈式調用實現複雜工作流")
    console.print("  5. RAG 提升回答準確性")


if __name__ == "__main__":
    main()

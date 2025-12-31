"""
CAMEL-AI 知識檢索 (RAG)

這個範例展示如何整合檢索增強生成 (RAG)：
1. 向量數據庫整合
2. 文檔嵌入和檢索
3. 知識庫構建
4. 上下文增強回答
5. Hybrid Search

RAG 讓 Agent 能夠訪問外部知識，提供更準確的回答。
"""

import os
from dotenv import load_dotenv
from colorama import init, Fore, Style
from typing import List, Dict, Any

init(autoreset=True)
load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    print(f"{Fore.RED}錯誤: 請設置 OPENAI_API_KEY{Style.RESET_ALL}")
    exit(1)


def example1_simple_knowledge_base():
    """範例1: 簡單知識庫"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例1: 構建簡單知識庫")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        print(f"{Fore.YELLOW}創建知識庫...{Style.RESET_ALL}\n")

        class SimpleKnowledgeBase:
            """簡單的知識庫實現"""

            def __init__(self):
                self.documents = []

            def add_document(self, doc_id: str, content: str, metadata: dict = None):
                """添加文檔"""
                self.documents.append({
                    "id": doc_id,
                    "content": content,
                    "metadata": metadata or {}
                })

            def search(self, query: str, top_k: int = 3) -> List[Dict]:
                """簡單的關鍵字搜尋"""
                results = []

                for doc in self.documents:
                    # 計算相關性（簡單的關鍵字匹配）
                    query_words = set(query.lower().split())
                    doc_words = set(doc["content"].lower().split())
                    overlap = len(query_words & doc_words)

                    if overlap > 0:
                        results.append({
                            "document": doc,
                            "score": overlap
                        })

                # 排序並返回前 k 個
                results.sort(key=lambda x: x["score"], reverse=True)
                return results[:top_k]

        # 創建知識庫
        kb = SimpleKnowledgeBase()

        # 添加文檔
        documents = [
            {
                "id": "doc1",
                "content": "CAMEL 是一個多 Agent 協作框架，專注於角色扮演和任務分解。",
                "metadata": {"category": "框架介紹"}
            },
            {
                "id": "doc2",
                "content": "Python 是一種高級程式語言，廣泛應用於 AI 和數據科學領域。",
                "metadata": {"category": "程式語言"}
            },
            {
                "id": "doc3",
                "content": "RAG (檢索增強生成) 結合了檢索和生成，提供更準確的回答。",
                "metadata": {"category": "AI 技術"}
            },
            {
                "id": "doc4",
                "content": "向量數據庫用於存儲和檢索高維向量，支持相似度搜尋。",
                "metadata": {"category": "數據庫"}
            }
        ]

        print(f"{Fore.CYAN}添加文檔到知識庫...{Style.RESET_ALL}\n")

        for doc in documents:
            kb.add_document(doc["id"], doc["content"], doc["metadata"])
            print(f"  ✓ {doc['id']}: {doc['content'][:50]}...")

        print(f"\n{Fore.GREEN}知識庫已創建，共 {len(kb.documents)} 個文檔{Style.RESET_ALL}\n")

        # 測試檢索
        print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}\n")

        queries = [
            "什麼是 CAMEL？",
            "告訴我關於 RAG 的信息",
            "Python 的應用"
        ]

        for query in queries:
            print(f"{Fore.YELLOW}查詢:{Style.RESET_ALL} {query}\n")

            results = kb.search(query)

            print(f"{Fore.CYAN}檢索結果:{Style.RESET_ALL}")
            for i, result in enumerate(results, 1):
                doc = result["document"]
                score = result["score"]
                print(f"  {i}. [相關性: {score}] {doc['content']}")

            print(f"\n{Fore.MAGENTA}{'-'*60}{Style.RESET_ALL}\n")

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def example2_vector_embeddings():
    """範例2: 向量嵌入檢索"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例2: 使用向量嵌入進行檢索")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        print(f"{Fore.YELLOW}創建向量檢索系統...{Style.RESET_ALL}\n")

        class VectorRetriever:
            """向量檢索器（模擬）"""

            def __init__(self):
                self.documents = []
                self.embeddings = []

            def _mock_embedding(self, text: str) -> List[float]:
                """模擬嵌入（實際應使用真實的嵌入模型）"""
                # 簡單的特徵向量：[長度, 單詞數, 數字數]
                import re
                return [
                    len(text) / 100.0,
                    len(text.split()) / 20.0,
                    len(re.findall(r'\d', text)) / 10.0
                ]

            def add_text(self, text: str, metadata: dict = None):
                """添加文本"""
                embedding = self._mock_embedding(text)
                self.documents.append({
                    "text": text,
                    "metadata": metadata or {},
                    "embedding": embedding
                })

            def similarity(self, vec1: List[float], vec2: List[float]) -> float:
                """計算餘弦相似度"""
                import math

                dot_product = sum(a * b for a, b in zip(vec1, vec2))
                magnitude1 = math.sqrt(sum(a * a for a in vec1))
                magnitude2 = math.sqrt(sum(b * b for b in vec2))

                if magnitude1 == 0 or magnitude2 == 0:
                    return 0.0

                return dot_product / (magnitude1 * magnitude2)

            def retrieve(self, query: str, top_k: int = 3) -> List[Dict]:
                """檢索相似文檔"""
                query_embedding = self._mock_embedding(query)

                results = []
                for doc in self.documents:
                    sim = self.similarity(query_embedding, doc["embedding"])
                    results.append({
                        "text": doc["text"],
                        "metadata": doc["metadata"],
                        "similarity": sim
                    })

                results.sort(key=lambda x: x["similarity"], reverse=True)
                return results[:top_k]

        # 創建檢索器
        retriever = VectorRetriever()

        # 添加知識
        knowledge_items = [
            "CAMEL 框架支持多 Agent 角色扮演，用於研究 AI 協作。",
            "向量數據庫如 ChromaDB 和 Pinecone 支持語義搜尋。",
            "檢索增強生成 (RAG) 提高了 LLM 回答的準確性和時效性。",
            "嵌入模型將文本轉換為高維向量表示。",
            "語義搜尋比關鍵字搜尋能更好地理解用戶意圖。"
        ]

        print(f"{Fore.CYAN}添加知識到向量庫...{Style.RESET_ALL}\n")

        for item in knowledge_items:
            retriever.add_text(item)
            print(f"  ✓ {item[:60]}...")

        print(f"\n{Fore.GREEN}向量庫已創建{Style.RESET_ALL}\n")

        # 測試檢索
        print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}\n")

        queries = [
            "如何進行語義搜尋？",
            "CAMEL 的主要功能",
            "什麼是嵌入？"
        ]

        for query in queries:
            print(f"{Fore.YELLOW}查詢:{Style.RESET_ALL} {query}\n")

            results = retriever.retrieve(query)

            print(f"{Fore.CYAN}檢索結果:{Style.RESET_ALL}")
            for i, result in enumerate(results, 1):
                print(f"  {i}. [相似度: {result['similarity']:.3f}]")
                print(f"     {result['text']}")

            print(f"\n{Fore.MAGENTA}{'-'*60}{Style.RESET_ALL}\n")

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def example3_rag_pipeline():
    """範例3: 完整的 RAG 流程"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例3: 完整的 RAG 流程")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        from camel.agents import ChatAgent
        from camel.messages import BaseMessage

        print(f"{Fore.YELLOW}構建 RAG 系統...{Style.RESET_ALL}\n")

        class RAGSystem:
            """RAG 系統"""

            def __init__(self, agent: ChatAgent):
                self.agent = agent
                self.knowledge_base = []

            def add_knowledge(self, text: str, source: str = None):
                """添加知識"""
                self.knowledge_base.append({
                    "text": text,
                    "source": source
                })

            def retrieve_context(self, query: str, top_k: int = 3) -> str:
                """檢索相關上下文"""
                # 簡單的關鍵字匹配
                query_words = set(query.lower().split())

                scored_docs = []
                for doc in self.knowledge_base:
                    doc_words = set(doc["text"].lower().split())
                    score = len(query_words & doc_words)
                    if score > 0:
                        scored_docs.append((score, doc))

                scored_docs.sort(reverse=True)

                # 組合上下文
                context_parts = []
                for score, doc in scored_docs[:top_k]:
                    context_parts.append(doc["text"])

                return "\n\n".join(context_parts)

            def answer(self, query: str) -> str:
                """使用 RAG 回答問題"""
                # 1. 檢索相關上下文
                context = self.retrieve_context(query)

                # 2. 構建增強提示
                enhanced_prompt = f"""基於以下背景知識回答問題：

背景知識：
{context}

問題：{query}

請基於提供的背景知識回答，如果背景知識不足，請說明。"""

                # 3. 生成回答
                msg = BaseMessage.make_user_message(
                    role_name="用戶",
                    content=enhanced_prompt
                )

                response = self.agent.step(msg)
                return response.msg.content

        # 創建 Agent
        agent_msg = BaseMessage.make_assistant_message(
            role_name="知識助手",
            content="你是一位知識助手，基於提供的背景知識回答問題。"
        )

        agent = ChatAgent(
            system_message=agent_msg,
            model_type="gpt-3.5-turbo"
        )

        # 創建 RAG 系統
        rag = RAGSystem(agent)

        # 添加知識
        knowledge = [
            {
                "text": "CAMEL 框架由研究團隊開發，發表於 2023 年。主要用於研究多 Agent 協作。",
                "source": "CAMEL 論文"
            },
            {
                "text": "角色扮演是 CAMEL 的核心機制，允許 AI Agent 扮演特定角色完成任務。",
                "source": "CAMEL 文檔"
            },
            {
                "text": "Task Specifier 用於將模糊任務轉換為具體的可執行任務描述。",
                "source": "CAMEL 教程"
            }
        ]

        print(f"{Fore.CYAN}添加知識到系統...{Style.RESET_ALL}\n")

        for item in knowledge:
            rag.add_knowledge(item["text"], item["source"])
            print(f"  ✓ 來源: {item['source']}")
            print(f"    {item['text'][:60]}...\n")

        # 測試 RAG 問答
        print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}\n")

        questions = [
            "CAMEL 是什麼時候發表的？",
            "CAMEL 的核心機制是什麼？",
            "Task Specifier 的作用是什麼？"
        ]

        for question in questions:
            print(f"{Fore.YELLOW}問題:{Style.RESET_ALL} {question}\n")

            answer = rag.answer(question)

            print(f"{Fore.GREEN}回答:{Style.RESET_ALL}")
            print(f"{answer}\n")
            print(f"{Fore.MAGENTA}{'-'*60}{Style.RESET_ALL}\n")

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def example4_document_chunking():
    """範例4: 文檔分塊策略"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例4: 文檔分塊策略")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        print(f"{Fore.YELLOW}演示不同的分塊策略...{Style.RESET_ALL}\n")

        class DocumentChunker:
            """文檔分塊工具"""

            @staticmethod
            def chunk_by_sentences(text: str, chunk_size: int = 3) -> List[str]:
                """按句子分塊"""
                import re
                sentences = re.split(r'[。！？.!?]\s*', text)
                sentences = [s.strip() for s in sentences if s.strip()]

                chunks = []
                for i in range(0, len(sentences), chunk_size):
                    chunk = '。'.join(sentences[i:i+chunk_size]) + '。'
                    chunks.append(chunk)

                return chunks

            @staticmethod
            def chunk_by_words(text: str, chunk_size: int = 50, overlap: int = 10) -> List[str]:
                """按詞數分塊（帶重疊）"""
                words = text.split()
                chunks = []

                for i in range(0, len(words), chunk_size - overlap):
                    chunk_words = words[i:i+chunk_size]
                    if chunk_words:
                        chunks.append(' '.join(chunk_words))

                return chunks

            @staticmethod
            def chunk_by_paragraphs(text: str) -> List[str]:
                """按段落分塊"""
                paragraphs = text.split('\n\n')
                return [p.strip() for p in paragraphs if p.strip()]

        # 測試文本
        sample_text = """CAMEL 是一個創新的多 Agent 框架。它專注於角色扮演和協作研究。
該框架允許研究者探索 AI Agent 的自主協作能力。

CAMEL 支持多種任務類型。包括代碼生成、創意寫作和問題解決。
每個 Agent 可以扮演特定的角色，如程式設計師、產品經理等。

框架的核心組件包括 RolePlaying 類和各種 Agent 類型。
通過這些組件，可以構建複雜的多 Agent 系統。"""

        chunker = DocumentChunker()

        print(f"{Fore.CYAN}原始文本:{Style.RESET_ALL}")
        print(f"{sample_text}\n")
        print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}\n")

        # 測試不同策略
        print(f"{Fore.GREEN}策略 1: 按句子分塊{Style.RESET_ALL}\n")
        sentence_chunks = chunker.chunk_by_sentences(sample_text, chunk_size=2)
        for i, chunk in enumerate(sentence_chunks, 1):
            print(f"  塊 {i}: {chunk}\n")

        print(f"{Fore.GREEN}策略 2: 按詞數分塊（帶重疊）{Style.RESET_ALL}\n")
        word_chunks = chunker.chunk_by_words(sample_text, chunk_size=20, overlap=5)
        for i, chunk in enumerate(word_chunks, 1):
            print(f"  塊 {i}: {chunk[:50]}...\n")

        print(f"{Fore.GREEN}策略 3: 按段落分塊{Style.RESET_ALL}\n")
        para_chunks = chunker.chunk_by_paragraphs(sample_text)
        for i, chunk in enumerate(para_chunks, 1):
            print(f"  塊 {i}: {chunk[:50]}...\n")

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def example5_hybrid_search():
    """範例5: 混合搜尋"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例5: 混合搜尋（關鍵字 + 語義）")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        print(f"{Fore.YELLOW}創建混合搜尋系統...{Style.RESET_ALL}\n")

        class HybridSearch:
            """混合搜尋引擎"""

            def __init__(self):
                self.documents = []

            def add_document(self, text: str, metadata: dict = None):
                """添加文檔"""
                self.documents.append({
                    "text": text,
                    "metadata": metadata or {}
                })

            def keyword_search(self, query: str) -> List[Dict]:
                """關鍵字搜尋"""
                query_words = set(query.lower().split())
                results = []

                for doc in self.documents:
                    doc_words = set(doc["text"].lower().split())
                    score = len(query_words & doc_words)
                    if score > 0:
                        results.append({
                            "document": doc,
                            "keyword_score": score,
                            "semantic_score": 0
                        })

                return results

            def semantic_search(self, query: str) -> List[Dict]:
                """語義搜尋（模擬）"""
                # 模擬語義相似度
                results = []
                for doc in self.documents:
                    # 簡單的相似度計算
                    sim = len(set(query.lower()) & set(doc["text"].lower())) / 100
                    results.append({
                        "document": doc,
                        "keyword_score": 0,
                        "semantic_score": sim
                    })

                return results

            def hybrid_search(self, query: str, alpha: float = 0.5, top_k: int = 3) -> List[Dict]:
                """混合搜尋（alpha 控制權重）"""
                keyword_results = self.keyword_search(query)
                semantic_results = self.semantic_search(query)

                # 合併結果
                doc_scores = {}
                for result in keyword_results:
                    doc_id = id(result["document"])
                    if doc_id not in doc_scores:
                        doc_scores[doc_id] = {
                            "document": result["document"],
                            "keyword_score": 0,
                            "semantic_score": 0
                        }
                    doc_scores[doc_id]["keyword_score"] = result["keyword_score"]

                for result in semantic_results:
                    doc_id = id(result["document"])
                    if doc_id not in doc_scores:
                        doc_scores[doc_id] = {
                            "document": result["document"],
                            "keyword_score": 0,
                            "semantic_score": 0
                        }
                    doc_scores[doc_id]["semantic_score"] = result["semantic_score"]

                # 計算混合分數
                final_results = []
                for doc_id, scores in doc_scores.items():
                    hybrid_score = (
                        alpha * scores["keyword_score"] +
                        (1 - alpha) * scores["semantic_score"] * 100
                    )
                    final_results.append({
                        "document": scores["document"],
                        "hybrid_score": hybrid_score,
                        "keyword_score": scores["keyword_score"],
                        "semantic_score": scores["semantic_score"]
                    })

                # 排序
                final_results.sort(key=lambda x: x["hybrid_score"], reverse=True)
                return final_results[:top_k]

        # 創建搜尋引擎
        search = HybridSearch()

        # 添加文檔
        docs = [
            "CAMEL 框架用於多 Agent 協作研究",
            "Python 是流行的程式語言",
            "向量數據庫支持語義搜尋",
            "機器學習模型需要大量數據訓練"
        ]

        print(f"{Fore.CYAN}添加文檔...{Style.RESET_ALL}\n")
        for doc in docs:
            search.add_document(doc)
            print(f"  ✓ {doc}")

        print(f"\n{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}\n")

        # 測試混合搜尋
        query = "多 Agent 協作"

        print(f"{Fore.YELLOW}查詢:{Style.RESET_ALL} {query}\n")

        results = search.hybrid_search(query, alpha=0.5)

        print(f"{Fore.CYAN}混合搜尋結果:{Style.RESET_ALL}\n")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['document']['text']}")
            print(f"     混合分數: {result['hybrid_score']:.2f}")
            print(f"     (關鍵字: {result['keyword_score']}, "
                  f"語義: {result['semantic_score']:.3f})\n")

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def main():
    """主函數"""
    print(f"\n{Fore.GREEN}{'='*60}")
    print(f"  CAMEL-AI 知識檢索 (RAG) 範例")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    print(f"{Fore.YELLOW}關於 RAG:{Style.RESET_ALL}")
    print("檢索增強生成 (RAG) 結合了檢索和生成：")
    print("1. 知識庫 - 存儲外部知識")
    print("2. 檢索 - 找到相關信息")
    print("3. 增強 - 將檢索結果加入提示")
    print("4. 生成 - 基於增強提示生成回答\n")

    try:
        example1_simple_knowledge_base()
        example2_vector_embeddings()
        example3_rag_pipeline()
        example4_document_chunking()
        example5_hybrid_search()

        print(f"\n{Fore.GREEN}{'='*60}")
        print(f"  所有範例執行完成！")
        print(f"{'='*60}{Style.RESET_ALL}\n")

        print(f"{Fore.CYAN}RAG 最佳實踐:{Style.RESET_ALL}")
        print("1. 適當的文檔分塊策略")
        print("2. 高質量的嵌入模型")
        print("3. 有效的檢索算法")
        print("4. 上下文長度管理")
        print("5. 定期更新知識庫\n")

        print(f"{Fore.CYAN}下一步:{Style.RESET_ALL}")
        print("查看 08_代碼生成.py 學習代碼生成應用\n")

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}程序被用戶中斷{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}執行過程中發生錯誤: {e}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()

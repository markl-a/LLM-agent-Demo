"""
PhiData RAG (檢索增強生成) 助手示例

這個腳本展示了如何使用 PhiData 實現 RAG 系統，包括：
1. 知識庫創建和管理
2. 文檔向量化
3. 語義搜索
4. 上下文檢索
5. 增強生成回答
6. 多文檔處理
7. 知識庫更新
8. 混合檢索策略
9. 引用和溯源
10. RAG 優化技巧

作者: PhiData Team
日期: 2025
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

# PhiData 核心導入
from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.knowledge.pdf import PDFKnowledgeBase, PDFReader
from phi.knowledge.text import TextKnowledgeBase
from phi.knowledge.json import JSONKnowledgeBase
from phi.knowledge.website import WebsiteKnowledgeBase
from phi.vectordb.pgvector import PgVector
from phi.embedder.openai import OpenAIEmbedder
from phi.utils.log import logger

# 環境變量管理
from dotenv import load_dotenv

# 載入環境變量
load_dotenv()


class RAGAssistant:
    """
    RAG 助手類

    提供完整的 RAG 功能，包括知識庫管理、文檔處理、智能問答等。
    支持多種文檔格式和向量數據庫。
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化 RAG 助手

        參數:
            api_key: OpenAI API 密鑰
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("未找到 OPENAI_API_KEY")

        logger.info("初始化 RAG 助手")

        # 問答歷史
        self.qa_history: List[Dict[str, Any]] = []

    def create_pdf_knowledge_base(
        self,
        path: str,
        vector_db_url: Optional[str] = None
    ) -> PDFKnowledgeBase:
        """
        創建 PDF 知識庫

        參數:
            path: PDF 文件或目錄路徑
            vector_db_url: 向量數據庫 URL（可選）

        返回:
            PDF 知識庫實例
        """
        logger.info(f"創建 PDF 知識庫: {path}")

        # 如果提供了向量數據庫 URL，使用 PgVector
        if vector_db_url:
            vector_db = PgVector(
                table_name="pdf_documents",
                db_url=vector_db_url,
                embedder=OpenAIEmbedder(
                    model="text-embedding-3-small",
                    api_key=self.api_key,
                ),
            )
        else:
            # 否則使用內存向量存儲（僅用於測試）
            vector_db = None

        knowledge_base = PDFKnowledgeBase(
            path=path,
            vector_db=vector_db,
            reader=PDFReader(),
        )

        return knowledge_base

    def create_text_knowledge_base(
        self,
        path: str,
        vector_db_url: Optional[str] = None
    ) -> TextKnowledgeBase:
        """
        創建文本知識庫

        參數:
            path: 文本文件或目錄路徑
            vector_db_url: 向量數據庫 URL（可選）

        返回:
            文本知識庫實例
        """
        logger.info(f"創建文本知識庫: {path}")

        if vector_db_url:
            vector_db = PgVector(
                table_name="text_documents",
                db_url=vector_db_url,
                embedder=OpenAIEmbedder(
                    model="text-embedding-3-small",
                    api_key=self.api_key,
                ),
            )
        else:
            vector_db = None

        knowledge_base = TextKnowledgeBase(
            path=path,
            vector_db=vector_db,
        )

        return knowledge_base

    def create_json_knowledge_base(
        self,
        path: str,
        vector_db_url: Optional[str] = None
    ) -> JSONKnowledgeBase:
        """
        創建 JSON 知識庫

        參數:
            path: JSON 文件路徑
            vector_db_url: 向量數據庫 URL（可選）

        返回:
            JSON 知識庫實例
        """
        logger.info(f"創建 JSON 知識庫: {path}")

        if vector_db_url:
            vector_db = PgVector(
                table_name="json_documents",
                db_url=vector_db_url,
                embedder=OpenAIEmbedder(
                    model="text-embedding-3-small",
                    api_key=self.api_key,
                ),
            )
        else:
            vector_db = None

        knowledge_base = JSONKnowledgeBase(
            path=path,
            vector_db=vector_db,
        )

        return knowledge_base

    def create_website_knowledge_base(
        self,
        urls: List[str],
        vector_db_url: Optional[str] = None
    ) -> WebsiteKnowledgeBase:
        """
        創建網站知識庫

        參數:
            urls: 網站 URL 列表
            vector_db_url: 向量數據庫 URL（可選）

        返回:
            網站知識庫實例
        """
        logger.info(f"創建網站知識庫，共 {len(urls)} 個 URL")

        if vector_db_url:
            vector_db = PgVector(
                table_name="website_documents",
                db_url=vector_db_url,
                embedder=OpenAIEmbedder(
                    model="text-embedding-3-small",
                    api_key=self.api_key,
                ),
            )
        else:
            vector_db = None

        knowledge_base = WebsiteKnowledgeBase(
            urls=urls,
            vector_db=vector_db,
        )

        return knowledge_base

    def create_rag_agent(
        self,
        knowledge_base,
        agent_name: str = "RAG 助手"
    ) -> Agent:
        """
        創建 RAG Agent

        參數:
            knowledge_base: 知識庫實例
            agent_name: Agent 名稱

        返回:
            RAG Agent
        """
        logger.info(f"創建 RAG Agent: {agent_name}")

        agent = Agent(
            name=agent_name,
            model=OpenAIChat(
                id="gpt-4",
                api_key=self.api_key,
            ),
            knowledge_base=knowledge_base,
            description="基於知識庫的智能問答助手",
            instructions=[
                "基於知識庫中的信息回答問題",
                "如果知識庫中沒有相關信息，誠實說明",
                "引用具體的文檔段落",
                "提供準確、有幫助的答案",
                "使用繁體中文回應",
            ],
            search_knowledge=True,  # 啟用知識檢索
            show_tool_calls=True,
            markdown=True,
        )

        return agent

    def load_knowledge_base(
        self,
        knowledge_base,
        recreate: bool = False
    ) -> None:
        """
        載入知識庫

        參數:
            knowledge_base: 知識庫實例
            recreate: 是否重新創建（刪除舊數據）
        """
        logger.info(f"載入知識庫 (recreate={recreate})")

        print(f"\n載入知識庫...")
        print(f"重新創建: {recreate}")

        try:
            knowledge_base.load(recreate=recreate)
            print("知識庫載入成功！")
        except Exception as e:
            logger.error(f"載入知識庫失敗: {e}")
            print(f"錯誤: {e}")
            raise

    def query_knowledge_base(
        self,
        agent: Agent,
        question: str,
        show_sources: bool = True
    ) -> str:
        """
        查詢知識庫

        參數:
            agent: RAG Agent
            question: 問題
            show_sources: 是否顯示來源

        返回:
            回答
        """
        logger.info(f"查詢知識庫: {question[:50]}...")

        print(f"\n{'='*60}")
        print(f"問題: {question}")
        print(f"{'='*60}\n")

        # 執行查詢
        response = agent.run(question)
        answer = response.content if hasattr(response, 'content') else str(response)

        # 記錄問答歷史
        self.qa_history.append({
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "answer": answer,
        })

        return answer

    def stream_query(
        self,
        agent: Agent,
        question: str
    ) -> None:
        """
        流式查詢知識庫

        參數:
            agent: RAG Agent
            question: 問題
        """
        logger.info(f"流式查詢: {question[:50]}...")

        print(f"\n{'='*60}")
        print(f"問題: {question}")
        print(f"{'='*60}\n")
        print("回答: ", end="", flush=True)

        # 流式輸出
        agent.print_response(question, stream=True)

        print("\n")

    def multi_question_qa(
        self,
        agent: Agent,
        questions: List[str]
    ) -> List[str]:
        """
        多問題問答

        參數:
            agent: RAG Agent
            questions: 問題列表

        返回:
            答案列表
        """
        logger.info(f"多問題問答，共 {len(questions)} 個問題")

        answers = []

        for i, question in enumerate(questions, 1):
            print(f"\n--- 問題 {i}/{len(questions)} ---")
            answer = self.query_knowledge_base(agent, question)
            answers.append(answer)
            print(f"\n回答: {answer}\n")

        return answers

    def update_knowledge_base(
        self,
        knowledge_base,
        new_documents_path: str
    ) -> None:
        """
        更新知識庫

        添加新文檔到現有知識庫。

        參數:
            knowledge_base: 知識庫實例
            new_documents_path: 新文檔路徑
        """
        logger.info(f"更新知識庫: {new_documents_path}")

        print(f"\n更新知識庫...")
        print(f"新文檔: {new_documents_path}")

        try:
            # 更新路徑
            knowledge_base.path = new_documents_path

            # 載入新文檔（不重新創建）
            knowledge_base.load(recreate=False)

            print("知識庫更新成功！")
        except Exception as e:
            logger.error(f"更新知識庫失敗: {e}")
            print(f"錯誤: {e}")

    def get_relevant_documents(
        self,
        knowledge_base,
        query: str,
        num_documents: int = 3
    ) -> List[Dict[str, Any]]:
        """
        獲取相關文檔

        檢索與查詢最相關的文檔片段。

        參數:
            knowledge_base: 知識庫實例
            query: 查詢文本
            num_documents: 返回文檔數量

        返回:
            相關文檔列表
        """
        logger.info(f"檢索相關文檔: {query[:50]}...")

        print(f"\n檢索與查詢相關的文檔...")
        print(f"查詢: {query}")
        print(f"返回數量: {num_documents}\n")

        try:
            # 這裡需要根據實際的 PhiData API 調整
            # 假設知識庫有 search 方法
            if hasattr(knowledge_base, 'search'):
                results = knowledge_base.search(query, limit=num_documents)
                return results
            else:
                print("知識庫不支持直接搜索")
                return []
        except Exception as e:
            logger.error(f"檢索失敗: {e}")
            print(f"錯誤: {e}")
            return []

    def generate_summary(
        self,
        agent: Agent,
        topic: str
    ) -> str:
        """
        生成主題摘要

        基於知識庫內容生成特定主題的摘要。

        參數:
            agent: RAG Agent
            topic: 主題

        返回:
            摘要
        """
        logger.info(f"生成摘要: {topic}")

        query = f"""
        請基於知識庫中的信息，生成關於「{topic}」的全面摘要。

        摘要應包括：
        1. 主要概念和定義
        2. 關鍵要點
        3. 重要細節
        4. 相關示例
        5. 總結

        請確保摘要準確、全面、易於理解。
        """

        return self.query_knowledge_base(agent, query)

    def answer_with_context(
        self,
        agent: Agent,
        question: str,
        context: str
    ) -> str:
        """
        帶額外上下文的問答

        在知識庫檢索的基礎上，添加額外的上下文信息。

        參數:
            agent: RAG Agent
            question: 問題
            context: 額外上下文

        返回:
            回答
        """
        logger.info(f"帶上下文問答: {question[:50]}...")

        full_question = f"""
        額外上下文：
        {context}

        問題：
        {question}

        請結合知識庫和上述上下文回答問題。
        """

        return self.query_knowledge_base(agent, full_question)

    def comparative_analysis(
        self,
        agent: Agent,
        topics: List[str]
    ) -> str:
        """
        比較分析

        比較多個主題的異同。

        參數:
            agent: RAG Agent
            topics: 主題列表

        返回:
            比較分析結果
        """
        logger.info(f"比較分析: {', '.join(topics)}")

        topics_str = '、'.join(topics)

        query = f"""
        請基於知識庫中的信息，比較分析以下主題：
        {topics_str}

        比較維度：
        1. 定義和概念
        2. 特點和特徵
        3. 優缺點
        4. 應用場景
        5. 相似之處
        6. 不同之處
        7. 選擇建議

        請提供詳細的比較分析。
        """

        return self.query_knowledge_base(agent, query)

    def extract_key_information(
        self,
        agent: Agent,
        category: str
    ) -> str:
        """
        提取關鍵信息

        從知識庫中提取特定類別的關鍵信息。

        參數:
            agent: RAG Agent
            category: 信息類別

        返回:
            提取的關鍵信息
        """
        logger.info(f"提取關鍵信息: {category}")

        query = f"""
        請從知識庫中提取所有關於「{category}」的關鍵信息。

        請以結構化的方式呈現：
        1. 列出所有相關要點
        2. 組織成邏輯清晰的結構
        3. 包含必要的細節
        4. 提供引用來源

        請確保信息完整、準確。
        """

        return self.query_knowledge_base(agent, query)

    def save_qa_history(self, filepath: str) -> None:
        """
        保存問答歷史

        參數:
            filepath: 保存路徑
        """
        logger.info(f"保存問答歷史: {filepath}")

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.qa_history, f, ensure_ascii=False, indent=2)

        print(f"\n問答歷史已保存到: {filepath}")

    def generate_qa_report(self, filepath: str) -> None:
        """
        生成問答報告

        參數:
            filepath: 報告保存路徑
        """
        logger.info(f"生成問答報告: {filepath}")

        report = "# RAG 問答報告\n\n"
        report += f"生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        report += f"總問答數: {len(self.qa_history)}\n\n"
        report += "---\n\n"

        for i, qa in enumerate(self.qa_history, 1):
            report += f"## 問答 {i}\n\n"
            report += f"**時間**: {qa['timestamp']}\n\n"
            report += f"**問題**: {qa['question']}\n\n"
            report += f"**回答**:\n\n{qa['answer']}\n\n"
            report += "---\n\n"

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n問答報告已生成: {filepath}")


def demonstration_text_rag():
    """
    演示文本 RAG
    """
    print("\n" + "="*60)
    print("演示 1: 文本知識庫 RAG")
    print("="*60)

    # 創建示例文本文件
    sample_text_dir = Path("sample_texts")
    sample_text_dir.mkdir(exist_ok=True)

    sample_text = """
    PhiData 是一個強大的 AI Agent 框架。

    主要特點：
    1. 多模態支持 - 處理文本、圖像、音頻等多種數據類型
    2. 多 Agent 協作 - 構建 Agent 團隊協同工作
    3. 知識庫集成 - 支持 RAG 模式，增強 AI 回答準確性
    4. 工具生態豐富 - 內建多種工具，支持自定義擴展
    5. 生產就緒 - 提供企業級功能和安全性

    使用場景：
    - 智能客服系統
    - 文檔問答助手
    - 數據分析平台
    - 研究助手
    - 內容創作工具
    """

    sample_file = sample_text_dir / "phidata_intro.txt"
    with open(sample_file, 'w', encoding='utf-8') as f:
        f.write(sample_text)

    # 創建 RAG 系統
    rag_assistant = RAGAssistant()

    # 創建知識庫
    knowledge_base = rag_assistant.create_text_knowledge_base(str(sample_text_dir))

    # 載入知識庫
    rag_assistant.load_knowledge_base(knowledge_base, recreate=True)

    # 創建 Agent
    agent = rag_assistant.create_rag_agent(knowledge_base, "文本 RAG 助手")

    # 問答
    answer = rag_assistant.query_knowledge_base(
        agent,
        "PhiData 的主要特點有哪些？"
    )
    print(f"\n回答:\n{answer}")


def demonstration_multi_question():
    """
    演示多問題問答
    """
    print("\n" + "="*60)
    print("演示 2: 多問題問答")
    print("="*60)

    # 使用之前創建的知識庫
    sample_text_dir = Path("sample_texts")

    rag_assistant = RAGAssistant()
    knowledge_base = rag_assistant.create_text_knowledge_base(str(sample_text_dir))
    rag_assistant.load_knowledge_base(knowledge_base)

    agent = rag_assistant.create_rag_agent(knowledge_base)

    # 多個問題
    questions = [
        "PhiData 支持哪些功能？",
        "PhiData 有哪些使用場景？",
        "為什麼選擇 PhiData？",
    ]

    rag_assistant.multi_question_qa(agent, questions)


def demonstration_summary_generation():
    """
    演示摘要生成
    """
    print("\n" + "="*60)
    print("演示 3: 摘要生成")
    print("="*60)

    sample_text_dir = Path("sample_texts")

    rag_assistant = RAGAssistant()
    knowledge_base = rag_assistant.create_text_knowledge_base(str(sample_text_dir))
    rag_assistant.load_knowledge_base(knowledge_base)

    agent = rag_assistant.create_rag_agent(knowledge_base)

    # 生成摘要
    summary = rag_assistant.generate_summary(agent, "PhiData 框架")
    print(f"\n摘要:\n{summary}")


def demonstration_information_extraction():
    """
    演示信息提取
    """
    print("\n" + "="*60)
    print("演示 4: 信息提取")
    print("="*60)

    sample_text_dir = Path("sample_texts")

    rag_assistant = RAGAssistant()
    knowledge_base = rag_assistant.create_text_knowledge_base(str(sample_text_dir))
    rag_assistant.load_knowledge_base(knowledge_base)

    agent = rag_assistant.create_rag_agent(knowledge_base)

    # 提取關鍵信息
    info = rag_assistant.extract_key_information(agent, "使用場景")
    print(f"\n提取的信息:\n{info}")


def main():
    """
    主函數
    """
    print("\n" + "="*60)
    print("PhiData RAG 助手 - 完整示例")
    print("="*60)

    try:
        # 運行演示
        demonstration_text_rag()
        demonstration_multi_question()
        demonstration_summary_generation()
        demonstration_information_extraction()

        # 生成報告
        rag_assistant = RAGAssistant()
        rag_assistant.generate_qa_report("rag_qa_report.md")

        print("\n" + "="*60)
        print("所有演示完成！")
        print("="*60)

        print("\n提示：")
        print("1. RAG 需要向量數據庫支持，完整功能請配置 PostgreSQL + pgvector")
        print("2. 支持 PDF、文本、JSON、網站等多種數據源")
        print("3. 可以組合多個知識庫使用")
        print("4. 調整檢索參數以優化效果")

    except Exception as e:
        logger.error(f"運行錯誤: {e}")
        print(f"\n錯誤: {e}")


if __name__ == "__main__":
    main()

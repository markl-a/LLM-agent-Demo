"""
Haystack RAG 基礎教程
演示如何使用 Haystack 構建完整的 RAG（檢索增強生成）系統

功能包括：
1. Document Store 初始化
2. 文檔加載和預處理
3. 向量嵌入和索引
4. Pipeline 構建
5. 檢索和生成
"""

import os
from typing import List, Dict
import logging
from pathlib import Path

# Haystack 核心導入
from haystack import Document, Pipeline
from haystack.document_stores import InMemoryDocumentStore
from haystack.nodes import (
    PreProcessor,
    EmbeddingRetriever,
    BM25Retriever,
    PromptNode,
    PromptTemplate,
    AnswerParser,
    JoinDocuments
)

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HaystackRAGDemo:
    """Haystack RAG 演示類"""

    def __init__(self, openai_api_key: str = None):
        """
        初始化 RAG 系統

        Args:
            openai_api_key: OpenAI API 密鑰
        """
        self.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("未設置 OPENAI_API_KEY，生成功能將不可用")

        self.document_store = None
        self.preprocessor = None
        self.retriever = None
        self.generator = None
        self.pipeline = None

    def setup_document_store(self):
        """設置文檔存儲"""
        logger.info("初始化 Document Store...")

        # 創建內存文檔存儲
        self.document_store = InMemoryDocumentStore(
            use_bm25=True,              # 啟用 BM25 算法
            embedding_dim=384,          # 嵌入維度
            similarity="cosine",        # 餘弦相似度
            return_embedding=True
        )

        logger.info("Document Store 初始化完成")
        return self.document_store

    def setup_preprocessor(self):
        """設置文檔預處理器"""
        logger.info("初始化 PreProcessor...")

        self.preprocessor = PreProcessor(
            clean_empty_lines=True,              # 清理空行
            clean_whitespace=True,               # 清理空白
            clean_header_footer=True,            # 清理頁眉頁腳
            split_by="word",                     # 按詞分割
            split_length=200,                    # 每塊 200 詞
            split_overlap=20,                    # 重疊 20 詞
            split_respect_sentence_boundary=True # 尊重句子邊界
        )

        logger.info("PreProcessor 初始化完成")
        return self.preprocessor

    def load_documents(self, texts: List[str]) -> List[Document]:
        """
        加載和處理文檔

        Args:
            texts: 文本列表

        Returns:
            處理後的文檔列表
        """
        logger.info(f"加載 {len(texts)} 個文檔...")

        # 創建文檔對象
        documents = []
        for idx, text in enumerate(texts):
            doc = Document(
                content=text,
                meta={
                    "doc_id": f"doc_{idx}",
                    "source": "demo",
                    "index": idx
                }
            )
            documents.append(doc)

        # 預處理文檔
        if self.preprocessor is None:
            self.setup_preprocessor()

        processed_docs = self.preprocessor.process(documents)
        logger.info(f"文檔處理完成，共 {len(processed_docs)} 個文檔塊")

        # 寫入文檔存儲
        self.document_store.write_documents(processed_docs)
        logger.info("文檔已寫入 Document Store")

        return processed_docs

    def setup_retriever(self, retriever_type: str = "embedding"):
        """
        設置檢索器

        Args:
            retriever_type: 檢索器類型 ('embedding' 或 'bm25')
        """
        logger.info(f"初始化 {retriever_type} Retriever...")

        if retriever_type == "embedding":
            # 密集向量檢索器
            self.retriever = EmbeddingRetriever(
                document_store=self.document_store,
                embedding_model="sentence-transformers/all-MiniLM-L6-v2",
                model_format="sentence_transformers",
                top_k=5,
                use_gpu=False
            )

            # 更新文檔嵌入
            logger.info("更新文檔嵌入...")
            self.document_store.update_embeddings(
                retriever=self.retriever,
                batch_size=10
            )
            logger.info("文檔嵌入更新完成")

        elif retriever_type == "bm25":
            # 稀疏檢索器（基於關鍵詞）
            self.retriever = BM25Retriever(
                document_store=self.document_store,
                top_k=5
            )

        else:
            raise ValueError(f"不支持的檢索器類型: {retriever_type}")

        logger.info("Retriever 初始化完成")
        return self.retriever

    def setup_generator(self):
        """設置生成器"""
        if not self.api_key:
            logger.warning("跳過生成器設置（未提供 API 密鑰）")
            return None

        logger.info("初始化 Generator...")

        # 創建提示模板
        prompt_template = PromptTemplate(
            name="rag-qa",
            prompt_text="""
請根據以下上下文回答問題。

上下文：
{join(documents, delimiter=new_line, pattern='- $content')}

問題：{query}

指示：
1. 僅基於提供的上下文回答
2. 如果上下文中沒有答案，請說"我不知道"
3. 保持回答簡潔準確
4. 如果可能，引用相關來源

回答：
            """.strip()
        )

        # 創建生成節點
        self.generator = PromptNode(
            model_name_or_path="gpt-3.5-turbo",
            api_key=self.api_key,
            default_prompt_template=prompt_template,
            max_length=500,
            temperature=0.7
        )

        logger.info("Generator 初始化完成")
        return self.generator

    def build_pipeline(self, pipeline_type: str = "retrieval"):
        """
        構建 Pipeline

        Args:
            pipeline_type: Pipeline 類型 ('retrieval' 或 'rag')
        """
        logger.info(f"構建 {pipeline_type} Pipeline...")

        self.pipeline = Pipeline()

        if pipeline_type == "retrieval":
            # 僅檢索 Pipeline
            self.pipeline.add_node(
                component=self.retriever,
                name="Retriever",
                inputs=["Query"]
            )

        elif pipeline_type == "rag":
            # 完整 RAG Pipeline
            if self.generator is None:
                self.setup_generator()

            self.pipeline.add_node(
                component=self.retriever,
                name="Retriever",
                inputs=["Query"]
            )
            self.pipeline.add_node(
                component=self.generator,
                name="Generator",
                inputs=["Retriever"]
            )

        elif pipeline_type == "hybrid":
            # 混合檢索 Pipeline
            # 同時使用 BM25 和嵌入檢索
            bm25_retriever = BM25Retriever(
                document_store=self.document_store,
                top_k=5
            )

            join_documents = JoinDocuments(
                join_mode="merge",
                top_k_join=5
            )

            self.pipeline.add_node(
                component=bm25_retriever,
                name="BM25Retriever",
                inputs=["Query"]
            )
            self.pipeline.add_node(
                component=self.retriever,
                name="EmbeddingRetriever",
                inputs=["Query"]
            )
            self.pipeline.add_node(
                component=join_documents,
                name="JoinDocuments",
                inputs=["BM25Retriever", "EmbeddingRetriever"]
            )

            if self.generator:
                self.pipeline.add_node(
                    component=self.generator,
                    name="Generator",
                    inputs=["JoinDocuments"]
                )

        else:
            raise ValueError(f"不支持的 Pipeline 類型: {pipeline_type}")

        logger.info("Pipeline 構建完成")
        return self.pipeline

    def query(self, question: str, top_k: int = 3) -> Dict:
        """
        執行查詢

        Args:
            question: 問題
            top_k: 返回結果數量

        Returns:
            查詢結果
        """
        logger.info(f"執行查詢: {question}")

        if self.pipeline is None:
            raise ValueError("Pipeline 未初始化，請先調用 build_pipeline()")

        # 運行 Pipeline
        result = self.pipeline.run(
            query=question,
            params={
                "Retriever": {"top_k": top_k}
            }
        )

        return result

    def print_results(self, result: Dict):
        """打印查詢結果"""
        print("\n" + "=" * 80)
        print("查詢結果")
        print("=" * 80)

        # 打印檢索的文檔
        if "documents" in result:
            print("\n檢索到的文檔：")
            for idx, doc in enumerate(result["documents"], 1):
                print(f"\n[文檔 {idx}]")
                print(f"內容: {doc.content[:200]}...")
                print(f"分數: {doc.score:.4f}")
                if doc.meta:
                    print(f"元數據: {doc.meta}")

        # 打印生成的答案
        if "results" in result and result["results"]:
            print("\n生成的答案：")
            for answer in result["results"]:
                print(f"\n{answer}")

        print("\n" + "=" * 80)


def main():
    """主函數：演示完整的 RAG 流程"""

    print("Haystack RAG 基礎教程")
    print("=" * 80)

    # 初始化 RAG 系統
    rag = HaystackRAGDemo()

    # 1. 設置 Document Store
    rag.setup_document_store()

    # 2. 準備示例文檔
    sample_texts = [
        """
        Haystack 是由 deepset 開發的開源 NLP 框架，專注於構建基於大型語言模型的
        搜索和問答系統。它提供了完整的文檔處理、索引、檢索和生成功能。
        """,
        """
        RAG（檢索增強生成）是一種結合信息檢索和文本生成的技術。它首先從知識庫中
        檢索相關文檔，然後基於這些文檔生成答案，從而提高回答的準確性和可靠性。
        """,
        """
        Haystack 的核心組件包括 Document Store（文檔存儲）、Retriever（檢索器）、
        Reader（閱讀器）和 Generator（生成器）。這些組件可以靈活組合成 Pipeline。
        """,
        """
        Document Store 支持多種後端，包括 Elasticsearch、Weaviate、Pinecone 和
        FAISS。選擇合適的後端取決於應用規模和性能要求。
        """,
        """
        Haystack 提供了豐富的預處理功能，包括文檔清理、分塊和向量化。合理的
        文檔預處理對於提高檢索質量至關重要。
        """
    ]

    # 3. 加載和處理文檔
    rag.load_documents(sample_texts)

    # 4. 設置檢索器
    rag.setup_retriever(retriever_type="embedding")

    # 5. 構建檢索 Pipeline
    rag.build_pipeline(pipeline_type="retrieval")

    # 6. 執行查詢
    questions = [
        "什麼是 Haystack？",
        "RAG 的核心思想是什麼？",
        "Haystack 支持哪些 Document Store？"
    ]

    for question in questions:
        print(f"\n問題: {question}")
        result = rag.query(question, top_k=3)
        rag.print_results(result)

    print("\n演示完成！")


if __name__ == "__main__":
    main()

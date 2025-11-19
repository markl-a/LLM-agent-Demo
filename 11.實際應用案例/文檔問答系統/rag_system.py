#!/usr/bin/env python3
"""
RAG 系統核心模組

提供文檔索引、檢索和問答功能的核心實現。
"""

import os
import yaml
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import logging

# 配置日誌
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)

try:
    from llama_index.core import (
        VectorStoreIndex,
        SimpleDirectoryReader,
        StorageContext,
        load_index_from_storage,
        Settings,
    )
    from llama_index.core.node_parser import SentenceSplitter
    from llama_index.core.query_engine import RetrieverQueryEngine
    from llama_index.core.retrievers import VectorIndexRetriever
    from llama_index.llms.openai import OpenAI
    from llama_index.llms.gemini import Gemini
    from llama_index.embeddings.openai import OpenAIEmbedding
    from llama_index.embeddings.gemini import GeminiEmbedding
    from llama_index.vector_stores.chroma import ChromaVectorStore
    import chromadb
except ImportError as e:
    logger.error(f"導入錯誤: {e}")
    logger.error("請安裝所需依賴: pip install -r requirements.txt")
    raise


@dataclass
class QueryResult:
    """查詢結果"""

    question: str
    answer: str
    sources: List[Dict[str, Any]]
    response_time: float
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class DocumentQASystem:
    """文檔問答系統 - RAG 核心類"""

    def __init__(self, config_path: str = "config.yaml"):
        """
        初始化問答系統

        Args:
            config_path: 配置文件路徑
        """
        self.config = self._load_config(config_path)
        self.index: Optional[VectorStoreIndex] = None
        self.query_engine = None

        # 初始化 LLM 和嵌入模型
        self._setup_llm()
        self._setup_embeddings()

        logger.info("文檔問答系統初始化完成")

    def _load_config(self, config_path: str) -> Dict:
        """載入配置文件"""
        if not Path(config_path).exists():
            logger.warning(f"配置文件不存在: {config_path}，使用默認配置")
            return self._get_default_config()

        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        logger.info(f"已載入配置: {config_path}")
        return config

    def _get_default_config(self) -> Dict:
        """獲取默認配置"""
        return {
            "llm": {
                "provider": "openai",
                "model": "gpt-4o-mini",
                "temperature": 0.3,
                "max_tokens": 1000,
            },
            "embeddings": {"provider": "openai", "model": "text-embedding-3-small"},
            "vectorstore": {
                "type": "chroma",
                "persist_directory": "./vectorstore",
                "collection_name": "documents",
            },
            "retrieval": {"top_k": 5, "score_threshold": 0.7},
            "document_processing": {"chunk_size": 1000, "chunk_overlap": 200},
        }

    def _setup_llm(self):
        """設置 LLM"""
        llm_config = self.config["llm"]
        provider = llm_config["provider"].lower()

        if provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("未設置 OPENAI_API_KEY")

            Settings.llm = OpenAI(
                model=llm_config["model"],
                temperature=llm_config["temperature"],
                max_tokens=llm_config["max_tokens"],
                api_key=api_key,
            )
            logger.info(f"使用 OpenAI LLM: {llm_config['model']}")

        elif provider == "google":
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("未設置 GOOGLE_API_KEY")

            Settings.llm = Gemini(
                model=llm_config["model"],
                temperature=llm_config["temperature"],
                max_tokens=llm_config["max_tokens"],
                api_key=api_key,
            )
            logger.info(f"使用 Google Gemini LLM: {llm_config['model']}")

        else:
            raise ValueError(f"不支援的 LLM 提供商: {provider}")

    def _setup_embeddings(self):
        """設置嵌入模型"""
        embed_config = self.config["embeddings"]
        provider = embed_config["provider"].lower()

        if provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("未設置 OPENAI_API_KEY")

            Settings.embed_model = OpenAIEmbedding(
                model=embed_config["model"], api_key=api_key
            )
            logger.info(f"使用 OpenAI 嵌入: {embed_config['model']}")

        elif provider == "google":
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("未設置 GOOGLE_API_KEY")

            Settings.embed_model = GeminiEmbedding(
                model_name=embed_config.get("model", "models/embedding-001"), api_key=api_key
            )
            logger.info(f"使用 Google 嵌入: {embed_config.get('model', 'models/embedding-001')}")

        else:
            raise ValueError(f"不支援的嵌入提供商: {provider}")

    def index_documents(
        self, data_dir: str, show_progress: bool = True, force_reindex: bool = False
    ) -> None:
        """
        索引文檔目錄

        Args:
            data_dir: 文檔目錄路徑
            show_progress: 是否顯示進度
            force_reindex: 是否強制重新索引
        """
        persist_dir = self.config["vectorstore"]["persist_directory"]

        # 檢查是否已有索引
        if Path(persist_dir).exists() and not force_reindex:
            logger.warning(f"索引已存在: {persist_dir}")
            logger.warning("使用 force_reindex=True 強制重新索引")
            return

        logger.info(f"開始索引文檔: {data_dir}")

        try:
            # 加載文檔
            reader = SimpleDirectoryReader(
                data_dir, recursive=True, required_exts=self._get_supported_extensions()
            )
            documents = reader.load_data(show_progress=show_progress)

            logger.info(f"已加載 {len(documents)} 個文檔")

            # 創建文本分割器
            doc_config = self.config["document_processing"]
            text_splitter = SentenceSplitter(
                chunk_size=doc_config["chunk_size"], chunk_overlap=doc_config["chunk_overlap"]
            )

            # 設置轉換
            Settings.text_splitter = text_splitter

            # 創建向量存儲
            vector_store = self._create_vector_store()

            # 創建存儲上下文
            storage_context = StorageContext.from_defaults(vector_store=vector_store)

            # 創建索引
            logger.info("正在創建索引...")
            self.index = VectorStoreIndex.from_documents(
                documents,
                storage_context=storage_context,
                show_progress=show_progress,
            )

            # 持久化
            logger.info(f"正在保存索引到: {persist_dir}")
            self.index.storage_context.persist(persist_dir=persist_dir)

            logger.info("✅ 索引創建完成")

        except Exception as e:
            logger.error(f"索引失敗: {e}")
            raise

    def _create_vector_store(self):
        """創建向量存儲"""
        vs_config = self.config["vectorstore"]
        vs_type = vs_config["type"].lower()

        if vs_type == "chroma":
            # 創建 Chroma 客戶端
            db = chromadb.PersistentClient(path=vs_config["persist_directory"])

            # 獲取或創建集合
            collection = db.get_or_create_collection(name=vs_config["collection_name"])

            # 創建向量存儲
            vector_store = ChromaVectorStore(chroma_collection=collection)

            return vector_store
        else:
            raise ValueError(f"不支援的向量存儲類型: {vs_type}")

    def load_index(self) -> None:
        """載入已存在的索引"""
        persist_dir = self.config["vectorstore"]["persist_directory"]

        if not Path(persist_dir).exists():
            raise FileNotFoundError(
                f"索引目錄不存在: {persist_dir}\n" "請先使用 index_documents() 創建索引"
            )

        logger.info(f"載入索引: {persist_dir}")

        try:
            # 創建向量存儲
            vector_store = self._create_vector_store()

            # 創建存儲上下文
            storage_context = StorageContext.from_defaults(
                vector_store=vector_store, persist_dir=persist_dir
            )

            # 載入索引
            self.index = load_index_from_storage(storage_context)

            # 創建查詢引擎
            self._create_query_engine()

            logger.info("✅ 索引載入完成")

        except Exception as e:
            logger.error(f"載入索引失敗: {e}")
            raise

    def _create_query_engine(self):
        """創建查詢引擎"""
        if self.index is None:
            raise ValueError("索引未初始化，請先載入或創建索引")

        retrieval_config = self.config["retrieval"]

        # 創建檢索器
        retriever = VectorIndexRetriever(
            index=self.index, similarity_top_k=retrieval_config["top_k"]
        )

        # 創建查詢引擎
        self.query_engine = RetrieverQueryEngine(retriever=retriever)

    def query(
        self, question: str, verbose: bool = True, return_sources: bool = True
    ) -> QueryResult:
        """
        查詢問題

        Args:
            question: 用戶問題
            verbose: 是否顯示詳細信息
            return_sources: 是否返回來源

        Returns:
            QueryResult 實例
        """
        import time

        start_time = time.time()

        # 確保索引已載入
        if self.index is None:
            self.load_index()

        # 確保查詢引擎已創建
        if self.query_engine is None:
            self._create_query_engine()

        if verbose:
            logger.info(f"問題: {question}")

        try:
            # 執行查詢
            response = self.query_engine.query(question)

            # 提取來源
            sources = []
            if return_sources and hasattr(response, "source_nodes"):
                for node in response.source_nodes:
                    source_info = {
                        "file_name": node.node.metadata.get("file_name", "未知"),
                        "file_path": node.node.metadata.get("file_path", ""),
                        "score": float(node.score) if hasattr(node, "score") else 0.0,
                        "text_preview": node.node.text[:200] + "..."
                        if len(node.node.text) > 200
                        else node.node.text,
                    }
                    sources.append(source_info)

            response_time = time.time() - start_time

            result = QueryResult(
                question=question,
                answer=str(response.response),
                sources=sources,
                response_time=response_time,
                metadata={"model": self.config["llm"]["model"]},
            )

            if verbose:
                logger.info(f"答案: {result.answer}")
                logger.info(f"響應時間: {result.response_time:.2f}s")
                if sources:
                    logger.info(f"來源數量: {len(sources)}")

            return result

        except Exception as e:
            logger.error(f"查詢失敗: {e}")
            raise

    def _get_supported_extensions(self) -> List[str]:
        """獲取支援的文件擴展名"""
        return self.config["document_processing"].get(
            "supported_extensions",
            [".txt", ".md", ".pdf", ".docx", ".xlsx", ".csv"],
        )

    def get_stats(self) -> Dict[str, Any]:
        """獲取系統統計信息"""
        if self.index is None:
            return {"status": "未初始化"}

        stats = {
            "status": "已就緒",
            "config": {
                "llm_model": self.config["llm"]["model"],
                "embedding_model": self.config["embeddings"]["model"],
                "chunk_size": self.config["document_processing"]["chunk_size"],
                "top_k": self.config["retrieval"]["top_k"],
            },
            "vectorstore": {
                "type": self.config["vectorstore"]["type"],
                "persist_directory": self.config["vectorstore"]["persist_directory"],
            },
        }

        return stats


def main():
    """測試函數"""
    from dotenv import load_dotenv

    load_dotenv()

    # 創建問答系統
    qa_system = DocumentQASystem()

    # 測試配置
    stats = qa_system.get_stats()
    print("\n系統配置:")
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()

"""
Flowise 向量存儲範例
==================

本範例展示如何在 Flowise 中使用向量存儲進行 RAG。

支持的向量存儲：
1. Pinecone
2. Chroma
3. Qdrant
4. Weaviate
5. Faiss（本地）

安裝依賴：
pip install requests chromadb pinecone-client qdrant-client
"""

import os
import json
import requests
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

# ============================================================
# 配置
# ============================================================

FLOWISE_API_URL = os.getenv("FLOWISE_API_URL", "http://localhost:3000")
FLOWISE_API_KEY = os.getenv("FLOWISE_API_KEY", "")


# ============================================================
# 向量存儲配置
# ============================================================

@dataclass
class VectorStoreConfig:
    """向量存儲配置"""
    type: str  # pinecone, chroma, qdrant, weaviate, faiss
    name: str
    embedding_model: str = "text-embedding-ada-002"
    dimension: int = 1536

    # 連接配置
    api_key: str = ""
    environment: str = ""  # for Pinecone
    host: str = ""
    port: int = 0
    collection_name: str = "default"


# ============================================================
# Flowise 向量存儲節點配置
# ============================================================

PINECONE_CONFIG = '''
{
    "nodes": [
        {
            "id": "pinecone_0",
            "type": "Pinecone",
            "data": {
                "label": "Pinecone",
                "name": "pinecone",
                "inputs": {
                    "index": "my-index",
                    "namespace": "default"
                },
                "credential": {
                    "pineconeApiKey": "{{PINECONE_API_KEY}}",
                    "pineconeEnvironment": "us-east-1"
                }
            }
        },
        {
            "id": "openAIEmbeddings_0",
            "type": "OpenAIEmbeddings",
            "data": {
                "label": "OpenAI Embeddings",
                "name": "openAIEmbeddings",
                "inputs": {
                    "modelName": "text-embedding-ada-002"
                }
            }
        }
    ],
    "edges": [
        {
            "source": "openAIEmbeddings_0",
            "target": "pinecone_0"
        }
    ]
}
'''

CHROMA_CONFIG = '''
{
    "nodes": [
        {
            "id": "chroma_0",
            "type": "Chroma",
            "data": {
                "label": "Chroma",
                "name": "chroma",
                "inputs": {
                    "collectionName": "my-collection"
                },
                "credential": {
                    "chromaURL": "http://localhost:8000"
                }
            }
        }
    ]
}
'''

QDRANT_CONFIG = '''
{
    "nodes": [
        {
            "id": "qdrant_0",
            "type": "Qdrant",
            "data": {
                "label": "Qdrant",
                "name": "qdrant",
                "inputs": {
                    "collectionName": "my-collection",
                    "contentPayloadKey": "content",
                    "metadataPayloadKey": "metadata"
                },
                "credential": {
                    "qdrantUrl": "http://localhost:6333",
                    "qdrantApiKey": ""
                }
            }
        }
    ]
}
'''

FAISS_CONFIG = '''
{
    "nodes": [
        {
            "id": "faiss_0",
            "type": "Faiss",
            "data": {
                "label": "Faiss",
                "name": "faiss",
                "inputs": {
                    "basePath": "./vector_store"
                }
            }
        }
    ]
}
'''


# ============================================================
# 向量存儲客戶端
# ============================================================

class VectorStoreClient:
    """
    向量存儲客戶端

    統一的向量存儲操作接口
    """

    def __init__(self, config: VectorStoreConfig):
        self.config = config

    def add_documents(
        self,
        documents: List[Dict[str, Any]],
        embeddings: Optional[List[List[float]]] = None
    ) -> Dict[str, Any]:
        """
        添加文檔到向量存儲

        Args:
            documents: 文檔列表
            embeddings: 可選的預計算嵌入向量

        Returns:
            添加結果
        """
        # 這裡應該根據 config.type 調用對應的向量存儲 API
        return {
            "status": "success",
            "added": len(documents),
            "store_type": self.config.type
        }

    def search(
        self,
        query: str,
        top_k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        搜索相似文檔

        Args:
            query: 查詢文本
            top_k: 返回數量
            filter: 過濾條件

        Returns:
            搜索結果
        """
        # 模擬搜索結果
        return [
            {
                "content": f"相關文檔 {i}",
                "score": 0.9 - i * 0.1,
                "metadata": {"source": f"doc_{i}"}
            }
            for i in range(min(top_k, 5))
        ]

    def delete(
        self,
        ids: Optional[List[str]] = None,
        filter: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        刪除文檔

        Args:
            ids: 文檔 ID 列表
            filter: 過濾條件

        Returns:
            刪除結果
        """
        return {
            "status": "success",
            "deleted": len(ids) if ids else 0
        }


# ============================================================
# RAG 配置
# ============================================================

RAG_CHATFLOW_CONFIG = '''
{
    "nodes": [
        {
            "id": "chatOpenAI_0",
            "type": "ChatOpenAI",
            "data": {
                "label": "ChatOpenAI",
                "name": "chatOpenAI",
                "inputs": {
                    "modelName": "gpt-4",
                    "temperature": 0.7,
                    "maxTokens": 2000
                }
            }
        },
        {
            "id": "openAIEmbeddings_0",
            "type": "OpenAIEmbeddings",
            "data": {
                "label": "OpenAI Embeddings",
                "name": "openAIEmbeddings",
                "inputs": {
                    "modelName": "text-embedding-ada-002"
                }
            }
        },
        {
            "id": "pinecone_0",
            "type": "Pinecone",
            "data": {
                "label": "Pinecone",
                "name": "pinecone",
                "inputs": {
                    "index": "my-index",
                    "topK": 5
                }
            }
        },
        {
            "id": "conversationalRetrievalQA_0",
            "type": "ConversationalRetrievalQAChain",
            "data": {
                "label": "Conversational Retrieval QA",
                "name": "conversationalRetrievalQA",
                "inputs": {
                    "returnSourceDocuments": true
                }
            }
        }
    ],
    "edges": [
        {
            "source": "openAIEmbeddings_0",
            "target": "pinecone_0"
        },
        {
            "source": "pinecone_0",
            "target": "conversationalRetrievalQA_0"
        },
        {
            "source": "chatOpenAI_0",
            "target": "conversationalRetrievalQA_0"
        }
    ]
}
'''


# ============================================================
# 使用範例
# ============================================================

def example_pinecone_setup():
    """
    範例 1: Pinecone 設置

    展示如何配置 Pinecone 向量存儲
    """
    print("=" * 50)
    print("範例 1: Pinecone 設置")
    print("=" * 50)

    config = VectorStoreConfig(
        type="pinecone",
        name="my-pinecone",
        embedding_model="text-embedding-ada-002",
        api_key=os.getenv("PINECONE_API_KEY", ""),
        environment="us-east-1",
        collection_name="my-index"
    )

    print("Pinecone 配置:")
    print(f"  類型: {config.type}")
    print(f"  索引: {config.collection_name}")
    print(f"  環境: {config.environment}")

    print("\nFlowise 節點配置:")
    print(PINECONE_CONFIG)


def example_chroma_setup():
    """
    範例 2: Chroma 設置

    展示如何配置本地 Chroma 向量存儲
    """
    print("\n" + "=" * 50)
    print("範例 2: Chroma 設置")
    print("=" * 50)

    config = VectorStoreConfig(
        type="chroma",
        name="my-chroma",
        host="localhost",
        port=8000,
        collection_name="my-collection"
    )

    print("Chroma 配置:")
    print(f"  類型: {config.type}")
    print(f"  主機: {config.host}:{config.port}")
    print(f"  集合: {config.collection_name}")

    print("\nFlowise 節點配置:")
    print(CHROMA_CONFIG)


def example_qdrant_setup():
    """
    範例 3: Qdrant 設置

    展示如何配置 Qdrant 向量存儲
    """
    print("\n" + "=" * 50)
    print("範例 3: Qdrant 設置")
    print("=" * 50)

    print("Qdrant 配置:")
    print(QDRANT_CONFIG)


def example_faiss_local():
    """
    範例 4: Faiss 本地存儲

    展示如何使用本地 Faiss 向量存儲
    """
    print("\n" + "=" * 50)
    print("範例 4: Faiss 本地存儲")
    print("=" * 50)

    print("Faiss 本地配置:")
    print(FAISS_CONFIG)

    print("\n使用說明:")
    print("  - Faiss 適合開發和測試環境")
    print("  - 數據存儲在本地文件系統")
    print("  - 重啟服務後數據會保留")


def example_add_documents():
    """
    範例 5: 添加文檔

    展示如何向向量存儲添加文檔
    """
    print("\n" + "=" * 50)
    print("範例 5: 添加文檔")
    print("=" * 50)

    config = VectorStoreConfig(
        type="chroma",
        name="test",
        collection_name="test-collection"
    )

    client = VectorStoreClient(config)

    # 準備文檔
    documents = [
        {"content": "Python 是一種高級編程語言", "metadata": {"source": "wiki", "category": "programming"}},
        {"content": "機器學習是人工智能的一個分支", "metadata": {"source": "textbook", "category": "ai"}},
        {"content": "深度學習使用多層神經網絡", "metadata": {"source": "paper", "category": "ai"}},
    ]

    # 添加文檔
    result = client.add_documents(documents)
    print(f"添加結果: {result}")


def example_search():
    """
    範例 6: 搜索文檔

    展示如何搜索向量存儲
    """
    print("\n" + "=" * 50)
    print("範例 6: 搜索文檔")
    print("=" * 50)

    config = VectorStoreConfig(
        type="chroma",
        name="test",
        collection_name="test-collection"
    )

    client = VectorStoreClient(config)

    # 搜索
    results = client.search(
        query="什麼是機器學習？",
        top_k=3
    )

    print("搜索結果:")
    for i, doc in enumerate(results, 1):
        print(f"  {i}. 分數: {doc['score']:.3f}")
        print(f"     內容: {doc['content']}")


def example_rag_chatflow():
    """
    範例 7: RAG Chatflow

    展示完整的 RAG 聊天流程配置
    """
    print("\n" + "=" * 50)
    print("範例 7: RAG Chatflow")
    print("=" * 50)

    print("RAG Chatflow 配置:")
    print(RAG_CHATFLOW_CONFIG[:1000] + "...")

    print("\n流程說明:")
    print("  1. 用戶輸入問題")
    print("  2. 使用 OpenAI Embeddings 將問題向量化")
    print("  3. 在 Pinecone 中搜索相關文檔")
    print("  4. 將文檔和問題傳給 ChatOpenAI")
    print("  5. 生成回答並返回來源文檔")


# ============================================================
# 主程序
# ============================================================

if __name__ == "__main__":
    print("Flowise 向量存儲範例")
    print()

    example_pinecone_setup()
    example_chroma_setup()
    example_qdrant_setup()
    example_faiss_local()
    example_add_documents()
    example_search()
    example_rag_chatflow()

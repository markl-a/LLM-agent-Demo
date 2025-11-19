#!/usr/bin/env python3
"""Haystack - 多種檢索器示例"""

from haystack import Document
from haystack.components.retrievers import InMemoryBM25Retriever, InMemoryEmbeddingRetriever
from haystack.document_stores.in_memory import InMemoryDocumentStore

# 創建文檔存儲
doc_store = InMemoryDocumentStore()

# 添加文檔
docs = [
    Document(content="Python 是一種高級編程語言"),
    Document(content="JavaScript 用於網頁開發"),
    Document(content="Rust 專注於系統編程和安全性"),
]
doc_store.write_documents(docs)

# 示例 1: BM25 檢索器
print("示例 1: BM25 關鍵詞檢索")
bm25 = InMemoryBM25Retriever(document_store=doc_store)
results = bm25.run(query="編程語言", top_k=2)
for doc in results["documents"]:
    print(f"  - {doc.content[:50]}...")

# 示例 2: 嵌入檢索器
print("\n示例 2: 語義嵌入檢索")
# embedding_retriever = InMemoryEmbeddingRetriever(document_store=doc_store)
# results = embedding_retriever.run(query="什麼語言適合系統開發", top_k=2)

print("\n✅ 多種檢索器示例完成")

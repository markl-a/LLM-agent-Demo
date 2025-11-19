#!/usr/bin/env python3
"""Haystack - 文檔存儲示例"""

from haystack import Document
from haystack.document_stores.in_memory import InMemoryDocumentStore

# 內存存儲
store = InMemoryDocumentStore()

# 寫入文檔
docs = [
    Document(content="文檔 1", meta={"category": "tech"}),
    Document(content="文檔 2", meta={"category": "business"}),
]
store.write_documents(docs)

# 過濾查詢
results = store.filter_documents(filters={"field": "meta.category", "operator": "==", "value": "tech"})
print(f"✅ 找到 {len(results)} 個技術文檔")

print("\n📊 支持的存儲後端：")
print("  - InMemory (開發測試)")
print("  - Elasticsearch (生產環境)")
print("  - Weaviate (向量搜索)")
print("  - Pinecone (雲端向量庫)")

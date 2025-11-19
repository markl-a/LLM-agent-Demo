#!/usr/bin/env python3
"""Haystack - Ranker 重排序示例"""

from haystack import Document
from haystack.components.rankers import TransformersSimilarityRanker

# 創建 Ranker
ranker = TransformersSimilarityRanker(model="cross-encoder/ms-marco-MiniLM-L-6-v2")

# 文檔列表
docs = [
    Document(content="Python 是編程語言"),
    Document(content="JavaScript 用於前端"),
    Document(content="Rust 系統編程語言"),
]

# 重排序
query = "最適合系統編程的語言"
# result = ranker.run(query=query, documents=docs)

print("✅ Ranker 重排序器已初始化")
print(f"📝 查詢: {query}")
print("🔄 可提升檢索結果相關性")

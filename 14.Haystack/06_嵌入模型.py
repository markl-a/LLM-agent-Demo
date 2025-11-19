#!/usr/bin/env python3
"""Haystack - 嵌入模型示例"""

from haystack.components.embedders import SentenceTransformersTextEmbedder, SentenceTransformersDocumentEmbedder

# 文本嵌入
text_embedder = SentenceTransformersTextEmbedder(model="sentence-transformers/all-MiniLM-L6-v2")
# result = text_embedder.run(text="AI 技術發展迅速")
print("✅ 文本嵌入器已初始化")

# 文檔嵌入
doc_embedder = SentenceTransformersDocumentEmbedder(model="sentence-transformers/all-MiniLM-L6-v2")
print("✅ 文檔嵌入器已初始化")

print("\n📊 支持多種嵌入模型：")
print("  - SentenceTransformers")
print("  - OpenAI Embeddings")
print("  - Cohere Embeddings")

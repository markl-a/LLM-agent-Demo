#!/usr/bin/env python3
"""Haystack - Pipeline 構建示例"""

from haystack import Pipeline, Document
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.retrievers import InMemoryBM25Retriever

# 創建 RAG Pipeline
def create_rag_pipeline():
    doc_store = InMemoryDocumentStore()
    doc_store.write_documents([
        Document(content="AI 是人工智能的簡稱"),
        Document(content="機器學習是 AI 的子集"),
    ])

    pipeline = Pipeline()
    pipeline.add_component("retriever", InMemoryBM25Retriever(document_store=doc_store))
    pipeline.add_component("prompt_builder", PromptBuilder(template="根據: {{documents}}\n回答: {{question}}"))
    pipeline.add_component("llm", OpenAIGenerator(model="gpt-4o-mini"))

    pipeline.connect("retriever", "prompt_builder.documents")
    pipeline.connect("prompt_builder", "llm")

    return pipeline

print("✅ RAG Pipeline 已構建")
print("📋 組件: retriever -> prompt_builder -> llm")

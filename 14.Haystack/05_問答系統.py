#!/usr/bin/env python3
"""Haystack - 問答系統示例"""

from haystack import Pipeline
from haystack.components.generators import OpenAIGenerator
from haystack.components.builders import AnswerBuilder, PromptBuilder

def create_qa_pipeline():
    pipeline = Pipeline()

    pipeline.add_component("prompt_builder", PromptBuilder(
        template="問題: {{question}}\n請用繁體中文簡潔回答。"
    ))
    pipeline.add_component("llm", OpenAIGenerator(model="gpt-4o-mini"))
    pipeline.add_component("answer_builder", AnswerBuilder())

    pipeline.connect("prompt_builder", "llm")
    pipeline.connect("llm.replies", "answer_builder.replies")

    return pipeline

# 使用示例
if __name__ == "__main__":
    print("✅ 問答系統 Pipeline 已創建")
    print("💬 可處理任意問題並生成回答")

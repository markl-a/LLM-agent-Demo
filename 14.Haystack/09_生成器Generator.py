#!/usr/bin/env python3
"""Haystack - 生成器 Generator 示例"""

from haystack.components.generators import OpenAIGenerator, HuggingFaceLocalGenerator

# OpenAI Generator
openai_gen = OpenAIGenerator(
    api_key="your-key",
    model="gpt-4o-mini",
    generation_kwargs={"temperature": 0.7, "max_tokens": 500}
)

print("✅ OpenAI Generator 已初始化")

# HuggingFace Local Generator
# hf_gen = HuggingFaceLocalGenerator(model="google/flan-t5-base")
# print("✅ HuggingFace Generator 已初始化")

print("\n📊 支持的生成器:")
print("  - OpenAI (GPT-4, GPT-3.5)")
print("  - Anthropic (Claude)")
print("  - Cohere")
print("  - HuggingFace (本地模型)")

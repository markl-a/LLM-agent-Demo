#!/usr/bin/env python3
"""Haystack - 流式處理示例"""
from haystack.components.generators import OpenAIGenerator

generator = OpenAIGenerator(
    model="gpt-4o-mini",
    streaming_callback=lambda chunk: print(chunk.content, end="", flush=True)
)

print("✅ 支持流式生成")
print("🔄 實時輸出 token")

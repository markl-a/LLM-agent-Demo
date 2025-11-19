#!/usr/bin/env python3
"""Haystack - 提示詞管理示例"""
from haystack.components.builders import PromptBuilder

# 基本提示詞
basic_prompt = PromptBuilder(template="問題: {{question}}")

# 帶上下文的提示詞
rag_prompt = PromptBuilder(template="""
上下文: {{documents}}

問題: {{question}}

請基於上下文回答。
""")

# Few-shot 提示詞
fewshot_prompt = PromptBuilder(template="""
範例1: {{example1}}
範例2: {{example2}}

現在處理: {{input}}
""")

print("✅ 提示詞模板已創建")
print("📝 支持變量插值、條件邏輯")

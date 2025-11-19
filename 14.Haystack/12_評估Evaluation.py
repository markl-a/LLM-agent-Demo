#!/usr/bin/env python3
"""Haystack - 評估 Evaluation 示例"""
from haystack.components.evaluators import SASEvaluator, FaithfulnessEvaluator

# 語義相似度評估
sas = SASEvaluator()
print("✅ 語義相似度評估器")

# 忠實度評估
faithfulness = FaithfulnessEvaluator()
print("✅ 忠實度評估器")

print("\n📊 評估指標:")
print("  - 語義相似度 (SAS)")
print("  - 忠實度 (Faithfulness)")
print("  - 相關性 (Relevance)")

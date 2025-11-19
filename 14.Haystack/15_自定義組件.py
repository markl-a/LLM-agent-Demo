#!/usr/bin/env python3
"""Haystack - 自定義組件示例"""
from haystack import component
from typing import List

@component
class CustomFilter:
    """自定義文檔過濾器"""

    @component.output_types(filtered_docs=List[str])
    def run(self, documents: List[str], min_length: int = 10):
        filtered = [doc for doc in documents if len(doc) >= min_length]
        return {"filtered_docs": filtered}

# 使用自定義組件
filter_component = CustomFilter()
result = filter_component.run(documents=["短文本", "這是一個較長的文本內容"], min_length=10)
print(f"✅ 過濾後: {len(result['filtered_docs'])} 個文檔")

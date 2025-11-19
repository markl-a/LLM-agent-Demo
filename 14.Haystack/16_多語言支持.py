#!/usr/bin/env python3
"""Haystack - 多語言支持示例"""
from haystack.components.preprocessors import DocumentLanguageClassifier

classifier = DocumentLanguageClassifier()
print("✅ 語言分類器 - 自動檢測文檔語言")

print("\n🌍 支持語言:")
print("  - 繁體中文")
print("  - 英文")
print("  - 日文")
print("  - 韓文")
print("  - 100+ 語言")

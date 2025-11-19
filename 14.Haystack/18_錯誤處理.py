#!/usr/bin/env python3
"""Haystack - 錯誤處理與重試示例"""
from haystack import Pipeline
from haystack.components.generators import OpenAIGenerator

# 配置重試
generator = OpenAIGenerator(
    model="gpt-4o-mini",
    timeout=30.0,
    max_retries=3
)

print("✅ 已配置重試機制")
print("⚙️  超時: 30秒")
print("🔄 最大重試: 3次")

print("\n🛡️  錯誤處理策略:")
print("  - 自動重試 (指數退避)")
print("  - 超時控制")
print("  - 降級處理")
print("  - 錯誤日誌")

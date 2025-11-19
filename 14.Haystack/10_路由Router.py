#!/usr/bin/env python3
"""Haystack - 路由 Router 示例"""

from haystack import Pipeline
from haystack.components.routers import ConditionalRouter, FileTypeRouter

# 條件路由
routes = [
    {"condition": "{{query|length > 100}}", "output": "{{query}}", "output_name": "long_query"},
    {"condition": "{{query|length <= 100}}", "output": "{{query}}", "output_name": "short_query"}
]
router = ConditionalRouter(routes=routes)
print("✅ 條件路由器已創建 - 根據查詢長度分流")

# 文件類型路由
file_router = FileTypeRouter(mime_types=["text/plain", "application/pdf", "text/html"])
print("✅ 文件類型路由器 - 根據文件類型分流")

print("\n🔀 路由功能:")
print("  - 條件分支")
print("  - 文件類型分流")
print("  - 自定義路由邏輯")

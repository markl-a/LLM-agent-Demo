#!/usr/bin/env python3
"""OpenAI Swarm - 性能優化"""

class Cache:
    def __init__(self):
        self.data = {}

    def get(self, key):
        return self.data.get(key)

    def set(self, key, value):
        self.data[key] = value

cache = Cache()
cache.set("user_123_profile", {"name": "張三", "plan": "專業版"})

print("✅ 緩存優化:")
print("  - 緩存用戶信息")
print("  - 減少 API 調用")
print("  - 提升響應速度")

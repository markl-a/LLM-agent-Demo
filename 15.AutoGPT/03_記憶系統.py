#!/usr/bin/env python3
"""AutoGPT - 記憶系統示例"""

class AgentMemory:
    """Agent 記憶系統"""

    def __init__(self):
        self.short_term = []  # 短期記憶
        self.long_term = {}   # 長期記憶
        self.working = []     # 工作記憶

    def add_short_term(self, info: str):
        """添加短期記憶"""
        self.short_term.append(info)
        if len(self.short_term) > 10:  # 限制大小
            self.short_term.pop(0)

    def add_long_term(self, key: str, value: str):
        """添加長期記憶"""
        self.long_term[key] = value

    def recall(self, query: str):
        """檢索記憶"""
        results = []
        for item in self.short_term:
            if query in item:
                results.append(item)
        return results

# 使用示例
memory = AgentMemory()
memory.add_short_term("用戶喜歡 Python")
memory.add_long_term("preferred_language", "Python")

print("✅ 記憶系統已初始化")
print(f"📝 短期記憶: {len(memory.short_term)} 條")
print(f"📚 長期記憶: {len(memory.long_term)} 條")

#!/usr/bin/env python3
"""AutoGPT - 知識獲取"""

class KnowledgeBase:
    def __init__(self):
        self.knowledge = {}

    def learn(self, topic: str, info: str):
        if topic not in self.knowledge:
            self.knowledge[topic] = []
        self.knowledge[topic].append(info)
        print(f"📚 學到: {topic} - {info[:50]}...")

    def recall(self, topic: str):
        return self.knowledge.get(topic, [])

kb = KnowledgeBase()
kb.learn("Python", "Python 是動態類型語言")
kb.learn("Python", "Python 有豐富的標準庫")

facts = kb.recall("Python")
print(f"\n✅ 知識庫包含 {len(facts)} 條 Python 相關知識")

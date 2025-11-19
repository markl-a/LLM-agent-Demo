#!/usr/bin/env python3
"""AutoGPT - 優先級管理"""
import heapq

class PriorityQueue:
    def __init__(self):
        self.heap = []

    def add(self, task: str, priority: int):
        heapq.heappush(self.heap, (priority, task))
        print(f"➕ 添加任務: {task} (優先級: {priority})")

    def get_next(self):
        if self.heap:
            priority, task = heapq.heappop(self.heap)
            return task
        return None

pq = PriorityQueue()
pq.add("寫報告", 3)
pq.add("修復Bug", 1)  # 最高優先級
pq.add("開會", 2)

print("\n執行順序:")
while pq.heap:
    print(f"  → {pq.get_next()}")

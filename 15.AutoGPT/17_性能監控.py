#!/usr/bin/env python3
"""AutoGPT - 性能監控"""
import time

class PerformanceMonitor:
    def __init__(self):
        self.metrics = []

    def track(self, name: str, duration: float):
        self.metrics.append({"name": name, "duration": duration})

    def report(self):
        print("📊 性能報告:")
        for m in self.metrics:
            print(f"  {m['name']}: {m['duration']:.3f}秒")

monitor = PerformanceMonitor()

start = time.time()
time.sleep(0.1)  # 模擬任務
monitor.track("Task1", time.time() - start)

monitor.report()
print("✅ 性能監控完成")

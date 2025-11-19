#!/usr/bin/env python3
"""OpenAI Swarm - 監控儀表板"""

class Dashboard:
    def __init__(self):
        self.metrics = {
            "total_requests": 0,
            "agent_transfers": 0,
            "avg_response_time": 0.0,
            "error_count": 0
        }

    def update(self, metric: str, value):
        self.metrics[metric] = value

    def display(self):
        print("📊 Swarm 監控儀表板")
        print("=" * 40)
        for key, value in self.metrics.items():
            print(f"  {key}: {value}")

dashboard = Dashboard()
dashboard.update("total_requests", 1234)
dashboard.update("agent_transfers", 456)
dashboard.display()

print("\n✅ 實時監控就緒")

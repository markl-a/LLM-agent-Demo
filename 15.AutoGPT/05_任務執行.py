#!/usr/bin/env python3
"""AutoGPT - 任務執行示例"""

class TaskExecutor:
    def __init__(self):
        self.tasks = []
        self.completed = []

    def add_task(self, task: str):
        self.tasks.append({"name": task, "status": "pending"})

    def execute_next(self):
        if self.tasks:
            task = self.tasks.pop(0)
            print(f"⚙️  執行: {task['name']}")
            task["status"] = "completed"
            self.completed.append(task)
            return task
        return None

executor = TaskExecutor()
executor.add_task("收集數據")
executor.add_task("分析數據")
executor.add_task("生成報告")

while executor.tasks:
    executor.execute_next()

print(f"\n✅ 完成 {len(executor.completed)} 個任務")

#!/usr/bin/env python3
"""OpenAI Swarm - 並發 Agent"""
import asyncio

async def agent_task(name: str, duration: float):
    print(f"🚀 {name} 開始")
    await asyncio.sleep(duration)
    print(f"✅ {name} 完成")

async def run_parallel():
    await asyncio.gather(
        agent_task("Agent A", 0.1),
        agent_task("Agent B", 0.1),
        agent_task("Agent C", 0.1)
    )

# asyncio.run(run_parallel())
print("⚡ 支持並發執行多個 Agent")

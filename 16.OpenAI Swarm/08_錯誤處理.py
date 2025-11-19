#!/usr/bin/env python3
"""OpenAI Swarm - 錯誤處理"""

class ErrorHandler:
    def handle(self, error: Exception, agent_name: str):
        print(f"❌ Agent '{agent_name}' 錯誤: {error}")
        print("🔄 嘗試恢復或轉接到備用 Agent")

handler = ErrorHandler()
try:
    raise ValueError("API 調用失敗")
except Exception as e:
    handler.handle(e, "主 Agent")

print("✅ 錯誤處理機制已配置")

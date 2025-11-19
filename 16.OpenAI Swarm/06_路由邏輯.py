#!/usr/bin/env python3
"""OpenAI Swarm - 路由邏輯示例"""

class Router:
    def route(self, user_message: str) -> str:
        """根據用戶消息路由到合適的 Agent"""
        message_lower = user_message.lower()

        if any(word in message_lower for word in ["購買", "價格", "訂單"]):
            return "銷售 Agent"
        elif any(word in message_lower for word in ["問題", "故障", "幫助"]):
            return "技術支持 Agent"
        elif any(word in message_lower for word in ["退款", "退貨"]):
            return "售後 Agent"
        else:
            return "通用 Agent"

router = Router()
messages = ["我想購買產品", "遇到技術問題", "想要退款"]

for msg in messages:
    agent = router.route(msg)
    print(f"💬 '{msg}' → {agent}")

print("\n✅ 智能路由完成")

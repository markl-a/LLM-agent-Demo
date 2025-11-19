#!/usr/bin/env python3
"""LangFlow - 聊天記憶示例

展示如何在 LangFlow 中添加對話記憶功能
"""

import json


def create_chat_with_memory_flow():
    return {
        "name": "Chat with Memory",
        "description": "帶記憶的聊天機器人",
        "data": {
            "nodes": [
                {"id": "input", "type": "ChatInput", "position": {"x": 100, "y": 200}},
                {"id": "memory", "type": "ConversationBufferMemory", "data": {"memory_key": "chat_history"}, "position": {"x": 300, "y": 100}},
                {"id": "llm", "type": "ChatOpenAI", "data": {"model_name": "gpt-4o-mini"}, "position": {"x": 300, "y": 200}},
                {"id": "chain", "type": "ConversationChain", "position": {"x": 500, "y": 200}},
                {"id": "output", "type": "ChatOutput", "position": {"x": 700, "y": 200}},
            ],
            "edges": [
                {"source": "input", "target": "chain"},
                {"source": "memory", "target": "chain"},
                {"source": "llm", "target": "chain"},
                {"source": "chain", "target": "output"},
            ],
        },
    }


if __name__ == "__main__":
    flow = create_chat_with_memory_flow()
    with open("chat_with_memory_flow.json", "w", encoding="utf-8") as f:
        json.dump(flow, f, indent=2, ensure_ascii=False)
    print("✅ 已創建: chat_with_memory_flow.json")
    print("💭 支持多輪對話記憶功能")

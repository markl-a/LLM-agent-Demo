#!/usr/bin/env python3
"""LangFlow - Web搜索集成"""
import json

flow = {
    "name": "Web Search RAG",
    "data": {
        "nodes": [
            {"id": "input", "type": "ChatInput", "position": {"x": 100, "y": 100}},
            {"id": "search", "type": "GoogleSearchAPI", "data": {"k": 3}, "position": {"x": 300, "y": 100}},
            {"id": "llm", "type": "ChatOpenAI", "position": {"x": 500, "y": 100}},
            {"id": "output", "type": "ChatOutput", "position": {"x": 700, "y": 100}},
        ],
        "edges": [{"source": "input", "target": "search"}, {"source": "search", "target": "llm"}, {"source": "llm", "target": "output"}],
    },
}

if __name__ == "__main__":
    with open("web_search_flow.json", "w") as f:
        json.dump(flow, f, indent=2)
    print("✅ Web搜索 Flow - 實時網絡信息檢索")

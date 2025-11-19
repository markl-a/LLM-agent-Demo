#!/usr/bin/env python3
"""LangFlow - API 集成示例 - 展示如何集成外部 API"""
import json

def create_api_integration_flow():
    return {
        "name": "API Integration",
        "data": {
            "nodes": [
                {"id": "input", "type": "ChatInput", "position": {"x": 100, "y": 100}},
                {"id": "api", "type": "APIRequest", "data": {"endpoint": "https://api.example.com", "method": "GET"}, "position": {"x": 300, "y": 100}},
                {"id": "llm", "type": "ChatOpenAI", "position": {"x": 500, "y": 100}},
                {"id": "output", "type": "ChatOutput", "position": {"x": 700, "y": 100}},
            ],
            "edges": [
                {"source": "input", "target": "api"},
                {"source": "api", "target": "llm"},
                {"source": "llm", "target": "output"},
            ],
        },
    }

if __name__ == "__main__":
    flow = create_api_integration_flow()
    with open("api_integration_flow.json", "w") as f:
        json.dump(flow, f, indent=2)
    print("✅ API 集成 Flow 已創建")

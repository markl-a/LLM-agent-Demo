#!/usr/bin/env python3
"""LangFlow - 流式輸出示例"""

import requests
import json


def stream_flow_response(flow_id: str, inputs: dict):
    """流式調用 Flow API"""
    url = f"http://localhost:7860/api/v1/process/{flow_id}/stream"

    with requests.post(url, json={"inputs": inputs}, stream=True) as response:
        for chunk in response.iter_content(chunk_size=None):
            if chunk:
                print(chunk.decode(), end="", flush=True)


def create_streaming_flow():
    """創建支持流式輸出的 Flow"""
    return {
        "name": "Streaming Chat",
        "data": {
            "nodes": [
                {"id": "input", "type": "ChatInput", "position": {"x": 100, "y": 100}},
                {"id": "llm", "type": "ChatOpenAI", "data": {"streaming": True}, "position": {"x": 300, "y": 100}},
                {"id": "output", "type": "ChatOutput", "position": {"x": 500, "y": 100}},
            ],
            "edges": [
                {"source": "input", "target": "llm"},
                {"source": "llm", "target": "output"},
            ],
        },
    }


if __name__ == "__main__":
    flow = create_streaming_flow()
    with open("streaming_flow.json", "w") as f:
        json.dump(flow, f, indent=2)
    print("✅ 流式輸出 Flow 已創建")
    print("🔄 支持實時流式響應")

#!/usr/bin/env python3
"""LangFlow - 多模態示例 (圖像+文本)"""
import json

def create_multimodal_flow():
    return {
        "name": "Image Analysis",
        "data": {
            "nodes": [
                {"id": "image", "type": "ImageInput", "position": {"x": 100, "y": 100}},
                {"id": "text", "type": "TextInput", "position": {"x": 100, "y": 200}},
                {"id": "llm", "type": "ChatOpenAI", "data": {"model_name": "gpt-4o"}, "position": {"x": 300, "y": 150}},
                {"id": "output", "type": "ChatOutput", "position": {"x": 500, "y": 150}},
            ],
            "edges": [
                {"source": "image", "target": "llm"},
                {"source": "text", "target": "llm"},
                {"source": "llm", "target": "output"},
            ],
        },
    }

if __name__ == "__main__":
    flow = create_multimodal_flow()
    with open("multimodal_flow.json", "w") as f:
        json.dump(flow, f, indent=2)
    print("✅ 多模態 Flow 已創建 - 支持圖像分析")

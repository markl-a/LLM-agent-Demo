#!/usr/bin/env python3
"""LangFlow - 錯誤處理與監控"""
import json

def create_error_handling_flow():
    return {
        "name": "Flow with Error Handling",
        "data": {
            "nodes": [
                {"id": "input", "type": "ChatInput", "position": {"x": 100, "y": 100}},
                {"id": "try", "type": "TryExcept", "position": {"x": 300, "y": 100}},
                {"id": "llm", "type": "ChatOpenAI", "position": {"x": 500, "y": 100}},
                {"id": "fallback", "type": "TextOutput", "data": {"text": "抱歉，服務暫時不可用"}, "position": {"x": 500, "y": 200}},
                {"id": "output", "type": "ChatOutput", "position": {"x": 700, "y": 100}},
            ],
            "edges": [
                {"source": "input", "target": "try"},
                {"source": "try", "target": "llm", "label": "success"},
                {"source": "try", "target": "fallback", "label": "error"},
                {"source": "llm", "target": "output"},
                {"source": "fallback", "target": "output"},
            ],
        },
    }

if __name__ == "__main__":
    flow = create_error_handling_flow()
    with open("error_handling_flow.json", "w") as f:
        json.dump(flow, f, indent=2)
    print("✅ 錯誤處理 Flow 已創建")
    print("🛡️  包含容錯和降級機制")

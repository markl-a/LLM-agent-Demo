#!/usr/bin/env python3
"""LangFlow - 多模型比較"""
import json

def create_model_comparison_flow():
    return {
        "name": "Model Comparison",
        "data": {
            "nodes": [
                {"id": "input", "type": "ChatInput", "position": {"x": 100, "y": 200}},
                {"id": "gpt4", "type": "ChatOpenAI", "data": {"model_name": "gpt-4o-mini"}, "position": {"x": 300, "y": 100}},
                {"id": "claude", "type": "ChatAnthropic", "data": {"model_name": "claude-3-5-sonnet-20241022"}, "position": {"x": 300, "y": 200}},
                {"id": "gemini", "type": "ChatGoogleGenerativeAI", "data": {"model_name": "gemini-2.0-flash-exp"}, "position": {"x": 300, "y": 300}},
                {"id": "compare", "type": "CompareOutputs", "position": {"x": 500, "y": 200}},
                {"id": "output", "type": "ChatOutput", "position": {"x": 700, "y": 200}},
            ],
            "edges": [
                {"source": "input", "target": "gpt4"},
                {"source": "input", "target": "claude"},
                {"source": "input", "target": "gemini"},
                {"source": "gpt4", "target": "compare"},
                {"source": "claude", "target": "compare"},
                {"source": "gemini", "target": "compare"},
                {"source": "compare", "target": "output"},
            ],
        },
    }

if __name__ == "__main__":
    flow = create_model_comparison_flow()
    with open("model_comparison_flow.json", "w") as f:
        json.dump(flow, f, indent=2)
    print("✅ 模型比較 Flow 已創建")
    print("🔬 同時比較 GPT-4, Claude, Gemini")

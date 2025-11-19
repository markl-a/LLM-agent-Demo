#!/usr/bin/env python3
"""LangFlow - 情感分析與分類"""
import json

flow = {
    "name": "Sentiment Analysis",
    "data": {
        "nodes": [
            {"id": "input", "type": "TextInput", "position": {"x": 100, "y": 100}},
            {"id": "prompt", "type": "PromptTemplate", "data": {"template": "分析情感(正面/負面/中性): {text}"}, "position": {"x": 200, "y": 100}},
            {"id": "llm", "type": "ChatOpenAI", "position": {"x": 300, "y": 100}},
            {"id": "parser", "type": "OutputParser", "position": {"x": 400, "y": 100}},
            {"id": "output", "type": "TextOutput", "position": {"x": 500, "y": 100}},
        ],
        "edges": [{"source": "input", "target": "prompt"}, {"source": "prompt", "target": "llm"}, {"source": "llm", "target": "parser"}, {"source": "parser", "target": "output"}],
    },
}

if __name__ == "__main__":
    with open("sentiment_analysis_flow.json", "w") as f:
        json.dump(flow, f, indent=2)
    print("✅ 情感分析 Flow")

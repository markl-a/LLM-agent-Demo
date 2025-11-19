#!/usr/bin/env python3
"""LangFlow - 多語言翻譯服務"""
import json

flow = {
    "name": "Translation Service",
    "data": {
        "nodes": [
            {"id": "input", "type": "TextInput", "position": {"x": 100, "y": 100}},
            {"id": "detect", "type": "LanguageDetector", "position": {"x": 200, "y": 100}},
            {"id": "translate", "type": "TranslationChain", "data": {"target_lang": "en"}, "position": {"x": 300, "y": 100}},
            {"id": "llm", "type": "ChatOpenAI", "position": {"x": 400, "y": 100}},
            {"id": "output", "type": "TextOutput", "position": {"x": 500, "y": 100}},
        ],
        "edges": [{"source": "input", "target": "detect"}, {"source": "detect", "target": "translate"}, {"source": "translate", "target": "llm"}, {"source": "llm", "target": "output"}],
    },
}

if __name__ == "__main__":
    with open("translation_flow.json", "w") as f:
        json.dump(flow, f, indent=2)
    print("✅ 翻譯服務 Flow - 多語言翻譯")

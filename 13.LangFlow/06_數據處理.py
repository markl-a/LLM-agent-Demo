#!/usr/bin/env python3
"""LangFlow - 數據處理示例"""

import json

def create_csv_processing_flow():
    return {
        "name": "CSV Data Processing",
        "data": {
            "nodes": [
                {"id": "csv", "type": "CSVLoader", "data": {"file_path": "data.csv"}, "position": {"x": 100, "y": 100}},
                {"id": "llm", "type": "ChatOpenAI", "position": {"x": 300, "y": 100}},
                {"id": "prompt", "type": "PromptTemplate", "data": {"template": "分析數據: {data}"}, "position": {"x": 200, "y": 100}},
                {"id": "output", "type": "TextOutput", "position": {"x": 400, "y": 100}},
            ],
            "edges": [
                {"source": "csv", "target": "prompt"},
                {"source": "prompt", "target": "llm"},
                {"source": "llm", "target": "output"},
            ],
        },
    }

if __name__ == "__main__":
    flow = create_csv_processing_flow()
    with open("csv_processing_flow.json", "w") as f:
        json.dump(flow, f, indent=2)
    print("✅ CSV 數據處理 Flow 已創建")

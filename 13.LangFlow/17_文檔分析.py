#!/usr/bin/env python3
"""LangFlow - 文檔分析與摘要"""
import json

flow = {
    "name": "Document Analysis",
    "data": {
        "nodes": [
            {"id": "upload", "type": "FileUpload", "position": {"x": 100, "y": 100}},
            {"id": "loader", "type": "PDFLoader", "position": {"x": 200, "y": 100}},
            {"id": "splitter", "type": "TextSplitter", "position": {"x": 300, "y": 100}},
            {"id": "summarize", "type": "MapReduce", "position": {"x": 400, "y": 100}},
            {"id": "llm", "type": "ChatOpenAI", "position": {"x": 500, "y": 100}},
            {"id": "output", "type": "TextOutput", "position": {"x": 600, "y": 100}},
        ],
        "edges": [{"source": "upload", "target": "loader"}, {"source": "loader", "target": "splitter"}, {"source": "splitter", "target": "summarize"}, {"source": "summarize", "target": "llm"}, {"source": "llm", "target": "output"}],
    },
}

if __name__ == "__main__":
    with open("document_analysis_flow.json", "w") as f:
        json.dump(flow, f, indent=2)
    print("✅ 文檔分析 Flow - PDF摘要與分析")

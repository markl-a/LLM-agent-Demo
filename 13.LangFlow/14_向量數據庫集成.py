#!/usr/bin/env python3
"""LangFlow - 向量數據庫集成"""
import json

flows = {
    "chroma": {
        "name": "Chroma Vector Store",
        "data": {"nodes": [
            {"id": "docs", "type": "DocumentLoader", "position": {"x": 100, "y": 100}},
            {"id": "embed", "type": "OpenAIEmbeddings", "position": {"x": 300, "y": 100}},
            {"id": "chroma", "type": "Chroma", "data": {"collection_name": "docs"}, "position": {"x": 500, "y": 100}},
        ], "edges": [{"source": "docs", "target": "embed"}, {"source": "embed", "target": "chroma"}]}
    },
    "pinecone": {
        "name": "Pinecone Vector Store",
        "data": {"nodes": [
            {"id": "docs", "type": "DocumentLoader", "position": {"x": 100, "y": 100}},
            {"id": "embed", "type": "OpenAIEmbeddings", "position": {"x": 300, "y": 100}},
            {"id": "pinecone", "type": "Pinecone", "data": {"index_name": "langflow"}, "position": {"x": 500, "y": 100}},
        ], "edges": [{"source": "docs", "target": "embed"}, {"source": "embed", "target": "pinecone"}]}
    },
}

if __name__ == "__main__":
    for name, flow in flows.items():
        filename = f"{name}_flow.json"
        with open(filename, "w") as f:
            json.dump(flow, f, indent=2)
        print(f"✅ {filename}")
    print("🗄️  支持多種向量數據庫")

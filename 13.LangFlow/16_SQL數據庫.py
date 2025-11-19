#!/usr/bin/env python3
"""LangFlow - SQL數據庫查詢"""
import json

flow = {
    "name": "SQL Database Query",
    "data": {
        "nodes": [
            {"id": "input", "type": "ChatInput", "position": {"x": 100, "y": 100}},
            {"id": "sql", "type": "SQLDatabase", "data": {"uri": "sqlite:///data.db"}, "position": {"x": 300, "y": 100}},
            {"id": "agent", "type": "SQLAgent", "position": {"x": 500, "y": 100}},
            {"id": "output", "type": "ChatOutput", "position": {"x": 700, "y": 100}},
        ],
        "edges": [{"source": "input", "target": "agent"}, {"source": "sql", "target": "agent"}, {"source": "agent", "target": "output"}],
    },
}

if __name__ == "__main__":
    with open("sql_database_flow.json", "w") as f:
        json.dump(flow, f, indent=2)
    print("✅ SQL數據庫 Flow - 自然語言查詢數據庫")

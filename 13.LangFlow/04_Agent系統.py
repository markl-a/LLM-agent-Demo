#!/usr/bin/env python3
"""
LangFlow - Agent 系統示例

展示如何在 LangFlow 中創建 AI Agent
"""

import json


def create_agent_with_tools_flow():
    """創建帶工具的 Agent Flow"""
    return {
        "name": "Agent with Tools",
        "description": "能使用工具的 AI Agent",
        "data": {
            "nodes": [
                {"id": "input", "type": "ChatInput", "position": {"x": 100, "y": 200}},
                {
                    "id": "agent",
                    "type": "AgentExecutor",
                    "data": {
                        "agent_type": "openai-functions",
                        "max_iterations": 5,
                    },
                    "position": {"x": 400, "y": 200},
                },
                # 工具
                {"id": "search", "type": "SerpAPITool", "position": {"x": 400, "y": 100}},
                {"id": "calculator", "type": "CalculatorTool", "position": {"x": 400, "y": 300}},
                {"id": "python", "type": "PythonREPL", "position": {"x": 400, "y": 400}},
                # LLM
                {"id": "llm", "type": "ChatOpenAI", "data": {"model_name": "gpt-4o-mini"}, "position": {"x": 250, "y": 200}},
                {"id": "output", "type": "ChatOutput", "position": {"x": 700, "y": 200}},
            ],
            "edges": [
                {"source": "input", "target": "agent"},
                {"source": "llm", "target": "agent"},
                {"source": "search", "target": "agent"},
                {"source": "calculator", "target": "agent"},
                {"source": "python", "target": "agent"},
                {"source": "agent", "target": "output"},
            ],
        },
    }


def main():
    """主函數"""
    print("\n🤖 LangFlow - Agent 系統示例\n")

    agent_flow = create_agent_with_tools_flow()

    with open("agent_with_tools_flow.json", "w", encoding="utf-8") as f:
        json.dump(agent_flow, f, indent=2, ensure_ascii=False)

    print("✅ Agent Flow 已創建: agent_with_tools_flow.json")
    print("\n🔧 Agent 可用工具:")
    print("  - 搜索工具 (SerpAPI)")
    print("  - 計算器")
    print("  - Python REPL")
    print("\n💡 Agent 會自動選擇合適的工具來完成任務")


if __name__ == "__main__":
    main()

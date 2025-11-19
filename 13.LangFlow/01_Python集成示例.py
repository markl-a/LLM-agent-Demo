#!/usr/bin/env python3
"""
LangFlow Python 集成示例

本示例展示如何在 Python 代碼中使用 LangFlow：
1. 通過 API 調用 LangFlow 流程
2. 加載和運行導出的流程
3. 動態創建流程組件
"""

import requests
import json
from typing import Dict, Any

# LangFlow 配置
LANGFLOW_URL = "http://localhost:7860"
API_ENDPOINT = f"{LANGFLOW_URL}/api/v1/process"


def call_langflow_api(flow_id: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    調用 LangFlow API

    Args:
        flow_id: 流程 ID
        inputs: 輸入數據

    Returns:
        API 響應
    """
    url = f"{API_ENDPOINT}/{flow_id}"

    payload = {"inputs": inputs}

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()

        return response.json()

    except requests.exceptions.ConnectionError:
        print(f"❌ 無法連接到 LangFlow ({LANGFLOW_URL})")
        print("   請確保 LangFlow 正在運行：langflow run")
        return None

    except requests.exceptions.HTTPError as e:
        print(f"❌ API 請求失敗: {e}")
        return None


def example_1_simple_qa():
    """示例 1: 簡單問答"""
    print("\n" + "=" * 60)
    print("示例 1: 通過 API 調用 LangFlow 問答流程")
    print("=" * 60)

    # 注意：這裡的 flow_id 需要替換為你實際創建的流程 ID
    flow_id = "your-flow-id-here"

    # 輸入
    inputs = {"question": "什麼是 LangFlow?"}

    print(f"📝 問題: {inputs['question']}")
    print(f"🔄 調用流程 ID: {flow_id}")

    # 調用 API
    result = call_langflow_api(flow_id, inputs)

    if result:
        print(f"✅ 回答: {result.get('outputs', {}).get('answer', 'N/A')}")
    else:
        print("⚠️  請先在 LangFlow 界面創建流程，並將 flow_id 替換為實際 ID")


def example_2_document_qa():
    """示例 2: 文檔問答"""
    print("\n" + "=" * 60)
    print("示例 2: 文檔問答流程")
    print("=" * 60)

    flow_id = "doc-qa-flow-id"

    # 輸入文檔和問題
    inputs = {
        "document": "LangFlow 是一個視覺化的 AI 應用構建平台...",
        "question": "LangFlow 的主要特點是什麼?",
    }

    print(f"📄 文檔: {inputs['document'][:50]}...")
    print(f"💬 問題: {inputs['question']}")

    result = call_langflow_api(flow_id, inputs)

    if result:
        print(f"🤖 回答: {result.get('outputs', {}).get('answer', 'N/A')}")
        print(f"📚 來源: {result.get('outputs', {}).get('sources', [])}")


def example_3_chat_with_memory():
    """示例 3: 帶記憶的對話"""
    print("\n" + "=" * 60)
    print("示例 3: 帶記憶的多輪對話")
    print("=" * 60)

    flow_id = "chat-memory-flow-id"

    # 模擬多輪對話
    conversations = [
        "我叫張三",
        "我喜歡吃披薩",
        "你還記得我叫什麼名字嗎?",
        "我喜歡吃什麼?",
    ]

    session_id = "test-session-123"

    for message in conversations:
        print(f"\n💬 用戶: {message}")

        inputs = {"message": message, "session_id": session_id}

        result = call_langflow_api(flow_id, inputs)

        if result:
            response = result.get("outputs", {}).get("response", "N/A")
            print(f"🤖 Assistant: {response}")


def example_4_agent_with_tools():
    """示例 4: Agent 使用工具"""
    print("\n" + "=" * 60)
    print("示例 4: Agent 使用工具執行任務")
    print("=" * 60)

    flow_id = "agent-tools-flow-id"

    tasks = [
        "今天台北的天氣如何?",
        "計算 15 的平方根",
        "搜索關於 AI 的最新新聞",
    ]

    for task in tasks:
        print(f"\n📋 任務: {task}")

        inputs = {"task": task}

        result = call_langflow_api(flow_id, inputs)

        if result:
            response = result.get("outputs", {}).get("result", "N/A")
            tools_used = result.get("outputs", {}).get("tools_used", [])

            print(f"✅ 結果: {response}")
            print(f"🔧 使用的工具: {', '.join(tools_used)}")


def create_flow_programmatically():
    """示例 5: 程序化創建流程（高級）"""
    print("\n" + "=" * 60)
    print("示例 5: 程序化創建 LangFlow 流程")
    print("=" * 60)

    # 定義流程結構
    flow_definition = {
        "name": "Simple RAG Flow",
        "description": "A simple RAG flow created programmatically",
        "data": {
            "nodes": [
                {
                    "id": "1",
                    "type": "ChatOpenAI",
                    "data": {"model_name": "gpt-4o-mini", "temperature": 0.7},
                },
                {
                    "id": "2",
                    "type": "PromptTemplate",
                    "data": {
                        "template": "回答問題: {question}\n\n上下文: {context}"
                    },
                },
                {"id": "3", "type": "ChatOutput", "data": {}},
            ],
            "edges": [
                {"source": "2", "target": "1"},
                {"source": "1", "target": "3"},
            ],
        },
    }

    print("📝 流程定義:")
    print(json.dumps(flow_definition, indent=2, ensure_ascii=False))

    # 注意：實際創建流程需要調用 LangFlow 的 API
    # 這裡僅展示流程定義的結構
    print("\n💡 提示: 使用 LangFlow 界面或 API 來創建此流程")


def export_and_share_flow():
    """示例 6: 導出和分享流程"""
    print("\n" + "=" * 60)
    print("示例 6: 導出和分享流程")
    print("=" * 60)

    # 流程可以導出為 JSON 文件
    flow_export_path = "my_awesome_flow.json"

    print(f"📦 導出流程到: {flow_export_path}")
    print("   可以分享給其他開發者或導入到其他 LangFlow 實例")

    # 示例導出數據結構
    export_data = {
        "version": "1.0",
        "flow_name": "My Awesome Flow",
        "components": [
            # ... 組件定義
        ],
        "connections": [
            # ... 連接定義
        ],
    }

    print("\n✅ 導出的流程可以:")
    print("   - 在其他 LangFlow 實例中導入")
    print("   - 作為模板分享給團隊")
    print("   - 版本控制（Git）")
    print("   - 部署到生產環境")


def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("🎨 LangFlow Python 集成示例")
    print("=" * 60)
    print(f"\n📍 LangFlow URL: {LANGFLOW_URL}")
    print("💡 確保 LangFlow 正在運行：langflow run\n")

    try:
        # 運行示例
        example_1_simple_qa()
        # example_2_document_qa()
        # example_3_chat_with_memory()
        # example_4_agent_with_tools()
        create_flow_programmatically()
        export_and_share_flow()

    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        import traceback

        traceback.print_exc()

    print("\n" + "=" * 60)
    print("📚 更多信息:")
    print("   - LangFlow 文檔: https://docs.langflow.org/")
    print("   - GitHub: https://github.com/logspace-ai/langflow")
    print("   - 視頻教程: https://www.youtube.com/@langflow")
    print("=" * 60)


if __name__ == "__main__":
    main()

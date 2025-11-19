#!/usr/bin/env python3
"""
LangFlow - 基礎 Flow 創建示例

本示例展示：
1. 簡單的 LLM Flow
2. 提示詞模板 Flow
3. 鏈式 Flow
4. 條件分支 Flow
"""

import requests
import json
from typing import Dict, Any, Optional


# LangFlow 配置
LANGFLOW_URL = "http://localhost:7860"
API_ENDPOINT = f"{LANGFLOW_URL}/api/v1"


def create_simple_llm_flow() -> Dict[str, Any]:
    """創建簡單的 LLM Flow"""
    flow = {
        "name": "Simple LLM Flow",
        "description": "基本的 LLM 調用流程",
        "data": {
            "nodes": [
                {
                    "id": "input-1",
                    "type": "ChatInput",
                    "data": {
                        "input_value": "",
                        "sender": "User",
                    },
                    "position": {"x": 100, "y": 100},
                },
                {
                    "id": "llm-1",
                    "type": "ChatOpenAI",
                    "data": {
                        "model_name": "gpt-4o-mini",
                        "temperature": 0.7,
                        "max_tokens": 256,
                    },
                    "position": {"x": 400, "y": 100},
                },
                {
                    "id": "output-1",
                    "type": "ChatOutput",
                    "data": {},
                    "position": {"x": 700, "y": 100},
                },
            ],
            "edges": [
                {
                    "id": "e1",
                    "source": "input-1",
                    "target": "llm-1",
                    "sourceHandle": "output",
                    "targetHandle": "input",
                },
                {
                    "id": "e2",
                    "source": "llm-1",
                    "target": "output-1",
                    "sourceHandle": "output",
                    "targetHandle": "input",
                },
            ],
        },
    }
    return flow


def create_prompt_template_flow() -> Dict[str, Any]:
    """創建帶提示詞模板的 Flow"""
    flow = {
        "name": "Prompt Template Flow",
        "description": "使用提示詞模板的流程",
        "data": {
            "nodes": [
                {
                    "id": "input-1",
                    "type": "ChatInput",
                    "data": {},
                    "position": {"x": 100, "y": 100},
                },
                {
                    "id": "prompt-1",
                    "type": "PromptTemplate",
                    "data": {
                        "template": """你是一個專業的{role}。

請用{style}的方式回答以下問題：

問題：{question}

回答：""",
                        "input_variables": ["role", "style", "question"],
                    },
                    "position": {"x": 400, "y": 100},
                },
                {
                    "id": "llm-1",
                    "type": "ChatOpenAI",
                    "data": {
                        "model_name": "gpt-4o-mini",
                        "temperature": 0.7,
                    },
                    "position": {"x": 700, "y": 100},
                },
                {
                    "id": "output-1",
                    "type": "ChatOutput",
                    "data": {},
                    "position": {"x": 1000, "y": 100},
                },
            ],
            "edges": [
                {"source": "input-1", "target": "prompt-1"},
                {"source": "prompt-1", "target": "llm-1"},
                {"source": "llm-1", "target": "output-1"},
            ],
        },
    }
    return flow


def create_chain_flow() -> Dict[str, Any]:
    """創建鏈式處理 Flow"""
    flow = {
        "name": "Chain Flow",
        "description": "多步驟鏈式處理",
        "data": {
            "nodes": [
                {
                    "id": "input-1",
                    "type": "TextInput",
                    "data": {
                        "input_value": "",
                    },
                    "position": {"x": 100, "y": 100},
                },
                # 步驟 1: 生成大綱
                {
                    "id": "llm-1",
                    "type": "ChatOpenAI",
                    "data": {
                        "model_name": "gpt-4o-mini",
                        "system_message": "生成文章大綱",
                    },
                    "position": {"x": 300, "y": 100},
                },
                # 步驟 2: 擴展內容
                {
                    "id": "llm-2",
                    "type": "ChatOpenAI",
                    "data": {
                        "model_name": "gpt-4o-mini",
                        "system_message": "根據大綱擴展成完整文章",
                    },
                    "position": {"x": 500, "y": 100},
                },
                # 步驟 3: 潤色
                {
                    "id": "llm-3",
                    "type": "ChatOpenAI",
                    "data": {
                        "model_name": "gpt-4o-mini",
                        "system_message": "潤色文章，提升質量",
                    },
                    "position": {"x": 700, "y": 100},
                },
                {
                    "id": "output-1",
                    "type": "TextOutput",
                    "data": {},
                    "position": {"x": 900, "y": 100},
                },
            ],
            "edges": [
                {"source": "input-1", "target": "llm-1"},
                {"source": "llm-1", "target": "llm-2"},
                {"source": "llm-2", "target": "llm-3"},
                {"source": "llm-3", "target": "output-1"},
            ],
        },
    }
    return flow


def save_flow_to_file(flow: Dict[str, Any], filename: str):
    """保存 Flow 到文件"""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(flow, f, indent=2, ensure_ascii=False)
    print(f"✅ Flow 已保存到: {filename}")


def example_1_simple_llm():
    """示例 1: 簡單 LLM Flow"""
    print("\n" + "=" * 60)
    print("示例 1: 簡單 LLM Flow")
    print("=" * 60)

    flow = create_simple_llm_flow()
    print(f"\n📝 Flow 名稱: {flow['name']}")
    print(f"📄 描述: {flow['description']}")
    print(f"🔢 節點數: {len(flow['data']['nodes'])}")
    print(f"🔗 連接數: {len(flow['data']['edges'])}")

    # 保存 Flow
    save_flow_to_file(flow, "simple_llm_flow.json")

    print("\n💡 使用方法:")
    print("   1. 在 LangFlow 界面點擊 'Import'")
    print("   2. 選擇 simple_llm_flow.json")
    print("   3. 配置 OpenAI API Key")
    print("   4. 點擊 'Run' 開始使用")


def example_2_prompt_template():
    """示例 2: 提示詞模板 Flow"""
    print("\n" + "=" * 60)
    print("示例 2: 提示詞模板 Flow")
    print("=" * 60)

    flow = create_prompt_template_flow()
    print(f"\n📝 Flow 名稱: {flow['name']}")
    print(f"📄 描述: {flow['description']}")

    # 保存 Flow
    save_flow_to_file(flow, "prompt_template_flow.json")

    print("\n💡 提示詞模板變量:")
    print("   - role: 角色（如：老師、工程師）")
    print("   - style: 風格（如：簡潔、詳細）")
    print("   - question: 用戶問題")


def example_3_chain_processing():
    """示例 3: 鏈式處理 Flow"""
    print("\n" + "=" * 60)
    print("示例 3: 鏈式處理 Flow")
    print("=" * 60)

    flow = create_chain_flow()
    print(f"\n📝 Flow 名稱: {flow['name']}")
    print(f"📄 描述: {flow['description']}")

    # 保存 Flow
    save_flow_to_file(flow, "chain_flow.json")

    print("\n🔗 處理步驟:")
    print("   1. 輸入主題")
    print("   2. LLM 生成大綱")
    print("   3. LLM 擴展內容")
    print("   4. LLM 潤色文章")
    print("   5. 輸出最終結果")


def example_4_flow_structure():
    """示例 4: Flow 結構說明"""
    print("\n" + "=" * 60)
    print("示例 4: Flow 結構說明")
    print("=" * 60)

    print("""
📋 LangFlow Flow 結構：

{
    "name": "Flow 名稱",
    "description": "Flow 描述",
    "data": {
        "nodes": [
            {
                "id": "唯一標識",
                "type": "組件類型",
                "data": { /* 組件配置 */ },
                "position": {"x": 100, "y": 100}
            }
        ],
        "edges": [
            {
                "source": "源節點ID",
                "target": "目標節點ID"
            }
        ]
    }
}

🔧 常用組件類型：
- ChatInput: 對話輸入
- ChatOutput: 對話輸出
- TextInput: 文本輸入
- TextOutput: 文本輸出
- ChatOpenAI: OpenAI 聊天模型
- PromptTemplate: 提示詞模板
- Memory: 記憶組件
- VectorStore: 向量存儲

💡 提示：
- 每個節點必須有唯一的 ID
- edges 定義節點之間的數據流
- position 決定節點在界面上的位置
""")


def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("🎨 LangFlow - 基礎 Flow 創建示例")
    print("=" * 60)
    print("\n💡 注意：這些示例生成 JSON 配置文件，可以導入到 LangFlow 界面使用")

    try:
        example_1_simple_llm()
        example_2_prompt_template()
        example_3_chain_processing()
        example_4_flow_structure()

    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("✅ 所有示例運行完成")
    print("📦 生成的 Flow 文件可直接導入到 LangFlow")
    print("=" * 60)


if __name__ == "__main__":
    main()

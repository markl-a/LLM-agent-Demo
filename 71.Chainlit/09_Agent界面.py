"""
Chainlit Agent 界面示例

本示例展示：
1. Agent 對話界面
2. 工具調用展示
3. 思考過程可視化
4. 多 Agent 協作
5. ReAct 模式實現

運行方式：
    chainlit run 09_Agent界面.py -w

環境變量：
    需要設置 OPENAI_API_KEY
"""

import chainlit as cl
from openai import AsyncOpenAI
import json
import os
from dotenv import load_dotenv
from typing import List, Dict, Optional
import asyncio
from datetime import datetime

# 載入環境變量
load_dotenv()

# 初始化 OpenAI 客戶端
client: Optional[AsyncOpenAI] = None


def init_client():
    """初始化 OpenAI 客戶端"""
    global client
    api_key = os.getenv("OPENAI_API_KEY")

    if api_key:
        client = AsyncOpenAI(api_key=api_key)
        print("✅ OpenAI 客戶端已初始化")
    else:
        print("⚠️ 警告: 未設置 OPENAI_API_KEY")
        client = None


# ==================== 工具定義 ====================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "獲取指定城市的當前天氣",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "城市名稱，例如：台北、東京"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "溫度單位"
                    }
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "在網路上搜索信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索關鍵詞"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "執行數學計算",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "數學表達式，例如：2+2, 10*5"
                    }
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_user_info",
            "description": "獲取用戶信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "用戶 ID"
                    }
                },
                "required": ["user_id"]
            }
        }
    }
]


# ==================== 工具執行函數 ====================

async def execute_tool(tool_name: str, arguments: dict) -> str:
    """
    執行工具函數

    Args:
        tool_name: 工具名稱
        arguments: 工具參數

    Returns:
        執行結果
    """
    try:
        if tool_name == "get_current_weather":
            location = arguments.get("location", "未知")
            unit = arguments.get("unit", "celsius")

            # 模擬天氣數據
            weather_data = {
                "台北": {"temp": 25, "condition": "多雲"},
                "東京": {"temp": 18, "condition": "晴天"},
                "紐約": {"temp": 15, "condition": "陰天"},
            }

            data = weather_data.get(location, {"temp": 20, "condition": "晴天"})

            if unit == "fahrenheit":
                data["temp"] = data["temp"] * 9/5 + 32

            return json.dumps({
                "location": location,
                "temperature": data["temp"],
                "condition": data["condition"],
                "unit": unit
            }, ensure_ascii=False)

        elif tool_name == "search_web":
            query = arguments.get("query", "")

            # 模擬搜索結果
            return json.dumps({
                "query": query,
                "results": [
                    f"關於 {query} 的搜索結果 1",
                    f"關於 {query} 的搜索結果 2",
                    f"關於 {query} 的搜索結果 3"
                ],
                "count": 3
            }, ensure_ascii=False)

        elif tool_name == "calculate":
            expression = arguments.get("expression", "")

            try:
                result = eval(expression)
                return json.dumps({
                    "expression": expression,
                    "result": result
                })
            except Exception as e:
                return json.dumps({
                    "error": f"計算錯誤: {str(e)}"
                })

        elif tool_name == "get_user_info":
            user_id = arguments.get("user_id", "")

            # 模擬用戶數據
            users = {
                "001": {"name": "張三", "email": "zhang@example.com", "role": "admin"},
                "002": {"name": "李四", "email": "li@example.com", "role": "user"},
            }

            user = users.get(user_id, {"error": "用戶不存在"})
            return json.dumps(user, ensure_ascii=False)

        else:
            return json.dumps({"error": f"未知工具: {tool_name}"})

    except Exception as e:
        return json.dumps({"error": str(e)})


# ==================== 會話初始化 ====================

@cl.on_chat_start
async def on_chat_start():
    """初始化聊天會話"""
    try:
        # 初始化客戶端
        init_client()

        # 初始化消息歷史
        cl.user_session.set("messages", [])

        # 發送歡迎消息
        welcome = """
# 🤖 Agent 界面示例

歡迎！這個示例展示了如何構建一個完整的 Agent 界面。

## ✨ Agent 特點

- 🧠 **智能推理** - ReAct 模式（推理 + 行動）
- 🔧 **工具調用** - 可視化工具使用過程
- 💭 **思考過程** - 展示 Agent 的推理步驟
- 🎯 **多步驟執行** - 支持複雜任務分解

## 🛠️ 可用工具

1. **天氣查詢** - 獲取城市天氣信息
2. **網路搜索** - 搜索網路資料
3. **計算器** - 執行數學運算
4. **用戶查詢** - 獲取用戶信息

## 💡 試試這些

- "台北今天天氣如何？"
- "搜索 AI 的最新發展"
- "計算 (123 + 456) * 2"
- "查詢用戶 001 的信息"
- "先查台北天氣，再算溫度的華氏度"

**開始提問吧！** 你會看到 Agent 的完整思考過程 🚀
        """

        await cl.Message(content=welcome, author="系統").send()

        if not client:
            await cl.Message(
                content="""
⚠️ **提醒**: 未設置 OPENAI_API_KEY

部分功能將使用模擬模式。要啟用完整功能，請設置：
```bash
export OPENAI_API_KEY="your-key-here"
```
                """
            ).send()

        print("✅ Agent 界面已初始化")

    except Exception as e:
        error_msg = f"❌ 初始化失敗: {str(e)}"
        print(error_msg)
        await cl.Message(content=error_msg).send()


# ==================== 消息處理 ====================

@cl.on_message
async def on_message(message: cl.Message):
    """處理用戶消息"""
    try:
        if client:
            await process_with_openai(message.content)
        else:
            await process_mock_agent(message.content)

    except Exception as e:
        error_msg = f"❌ 處理失敗: {str(e)}"
        print(error_msg)
        await cl.Message(content=error_msg).send()


# ==================== OpenAI Agent 處理 ====================

async def process_with_openai(user_input: str):
    """
    使用 OpenAI API 處理 Agent 請求

    Args:
        user_input: 用戶輸入
    """
    try:
        # 獲取消息歷史
        messages = cl.user_session.get("messages", [])

        # 添加用戶消息
        messages.append({
            "role": "user",
            "content": user_input
        })

        # Agent 主循環
        max_iterations = 5
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            # 調用 LLM
            async with cl.Step(name=f"🤔 思考（第 {iteration} 輪）") as think_step:
                response = await client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    tools=TOOLS,
                    tool_choice="auto"
                )

                assistant_message = response.choices[0].message

                # 記錄 LLM 響應
                think_step.output = f"決策: {'使用工具' if assistant_message.tool_calls else '直接回答'}"

            # 檢查是否需要調用工具
            if assistant_message.tool_calls:
                # 有工具調用
                messages.append(assistant_message.model_dump())

                # 執行所有工具調用
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)

                    # 展示工具調用
                    async with cl.Step(name=f"🔧 使用工具: {tool_name}") as tool_step:
                        tool_step.input = json.dumps(tool_args, ensure_ascii=False, indent=2)

                        # 執行工具
                        tool_result = await execute_tool(tool_name, tool_args)

                        tool_step.output = tool_result

                        # 添加工具結果到消息
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": tool_result
                        })

                # 繼續循環，讓 LLM 處理工具結果
                continue

            else:
                # 沒有工具調用，直接回答
                final_response = assistant_message.content

                # 發送最終回答
                msg = cl.Message(content="", author="AI Agent")
                await msg.send()

                for char in final_response:
                    await msg.stream_token(char)
                    await asyncio.sleep(0.01)

                await msg.update()

                # 添加到歷史
                messages.append({
                    "role": "assistant",
                    "content": final_response
                })

                cl.user_session.set("messages", messages)

                print(f"✅ Agent 完成（{iteration} 輪）")
                break

        else:
            # 達到最大迭代次數
            await cl.Message(
                content="⚠️ 達到最大思考次數，任務可能太複雜。"
            ).send()

    except Exception as e:
        await cl.Message(content=f"❌ 處理錯誤: {str(e)}").send()


# ==================== 模擬 Agent 處理 ====================

async def process_mock_agent(user_input: str):
    """
    模擬 Agent 處理（無 API Key 時使用）

    Args:
        user_input: 用戶輸入
    """
    try:
        # 步驟 1: 理解問題
        async with cl.Step(name="🤔 理解問題") as step:
            await asyncio.sleep(0.5)
            step.output = f"分析用戶請求：{user_input[:50]}..."

        # 步驟 2: 選擇工具
        async with cl.Step(name="🎯 選擇工具") as step:
            await asyncio.sleep(0.5)

            # 簡單的關鍵詞匹配
            if "天氣" in user_input or "weather" in user_input.lower():
                tool_name = "get_current_weather"
                tool_args = {"location": "台北"}
            elif "搜索" in user_input or "search" in user_input.lower():
                tool_name = "search_web"
                tool_args = {"query": "AI"}
            elif "計算" in user_input or "calculate" in user_input.lower():
                tool_name = "calculate"
                tool_args = {"expression": "2+2"}
            else:
                tool_name = None
                tool_args = {}

            if tool_name:
                step.output = f"選擇工具: {tool_name}"
            else:
                step.output = "無需使用工具，直接回答"

        # 步驟 3: 執行工具（如果需要）
        if tool_name:
            async with cl.Step(name=f"🔧 執行: {tool_name}") as step:
                step.input = json.dumps(tool_args, ensure_ascii=False)
                await asyncio.sleep(0.8)

                result = await execute_tool(tool_name, tool_args)
                step.output = result

        # 步驟 4: 生成回答
        async with cl.Step(name="💬 生成回答") as step:
            await asyncio.sleep(0.5)

            if tool_name:
                response = f"""基於工具 {tool_name} 的結果，我可以告訴你：

這是一個模擬的 Agent 回答。實際使用時，Agent 會根據工具返回的數據生成更智能的回答。

要啟用完整功能，請設置 OPENAI_API_KEY。

你的問題：{user_input}
使用的工具：{tool_name}
"""
            else:
                response = f"""我收到了你的問題：{user_input}

這是一個模擬的回答。要獲得智能的 Agent 響應，請設置 OPENAI_API_KEY。

💡 提示：試試包含「天氣」、「搜索」或「計算」的問題，查看 Agent 如何使用工具！
"""

            step.output = "回答已生成"

        # 發送最終回答
        await cl.Message(content=response, author="模擬 Agent").send()

    except Exception as e:
        await cl.Message(content=f"❌ 模擬處理錯誤: {str(e)}").send()


# ==================== 主函數 ====================

def main():
    """主函數"""
    print("""
╔══════════════════════════════════════════╗
║   Chainlit Agent 界面示例                ║
╚══════════════════════════════════════════╝

運行命令：
    chainlit run 09_Agent界面.py -w

環境變量：
    export OPENAI_API_KEY="your-key-here"

功能特點：
✅ ReAct 模式 Agent
✅ 工具調用可視化
✅ 思考過程展示
✅ 多步驟執行追蹤
✅ 模擬模式（無需 API Key）

可用工具：
🌤️ 天氣查詢
🔍 網路搜索
🔢 計算器
👤 用戶查詢

Agent 能力：
- 自主選擇合適的工具
- 多輪推理和行動
- 複雜任務分解
- 結果整合和呈現

試試這些：
- "台北今天天氣如何？"
- "搜索 AI 的最新發展"
- "計算 (123 + 456) * 2"

訪問 http://localhost:8000 體驗智能 Agent！
    """)


if __name__ == "__main__":
    main()

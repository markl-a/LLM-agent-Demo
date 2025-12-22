"""
與 OpenAI 整合
==============

本模組展示如何將 MCP 與 OpenAI API 整合。
學習如何在自己的應用中使用 MCP 標準化工具調用。

學習目標：
- 理解 OpenAI Function Calling 與 MCP 的關係
- 實現 MCP 到 OpenAI 格式的轉換
- 構建完整的整合示例
- 處理流式響應和多輪對話

作者：Claude (Anthropic)
日期：2025-12-22
"""

import asyncio
import json
from typing import Any, Dict, List, Optional
from dataclasses import dataclass


# ============================================================================
# 第一部分：MCP 與 OpenAI Function Calling 對比
# ============================================================================

class MCPvsOpenAIComparison:
    """MCP 與 OpenAI Function Calling 對比"""

    @staticmethod
    def show_comparison():
        """展示兩者的區別和聯繫"""
        return {
            "相似之處": [
                "都支持工具/函數調用",
                "都使用 JSON Schema 定義參數",
                "都支持多輪對話",
                "都返回結構化結果"
            ],

            "MCP 優勢": [
                "開放標準，支持多個 LLM 提供商",
                "統一的服務器-客戶端架構",
                "內建資源和提示模板支持",
                "更豐富的生態系統"
            ],

            "OpenAI Function Calling": [
                "OpenAI 專有功能",
                "深度整合到 ChatGPT 和 API",
                "簡單直接的 API",
                "廣泛的文檔和示例"
            ],

            "最佳實踐": [
                "使用 MCP 定義工具，提高可移植性",
                "實現適配器轉換 MCP 到 OpenAI 格式",
                "在應用層整合兩者優勢",
                "保持工具定義的一致性"
            ]
        }


# ============================================================================
# 第二部分：格式轉換器
# ============================================================================

class MCPToOpenAIConverter:
    """MCP 工具定義轉換為 OpenAI Function 格式"""

    @staticmethod
    def convert_tool_to_function(mcp_tool: Dict[str, Any]) -> Dict[str, Any]:
        """
        將 MCP 工具轉換為 OpenAI Function

        Args:
            mcp_tool: MCP 工具定義

        Returns:
            OpenAI Function 定義
        """
        return {
            "type": "function",
            "function": {
                "name": mcp_tool["name"],
                "description": mcp_tool["description"],
                "parameters": mcp_tool["inputSchema"]
            }
        }

    @staticmethod
    def convert_tools_batch(mcp_tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """批量轉換工具"""
        return [
            MCPToOpenAIConverter.convert_tool_to_function(tool)
            for tool in mcp_tools
        ]

    @staticmethod
    def create_openai_tool_call_response(
        tool_name: str,
        tool_result: str,
        tool_call_id: str
    ) -> Dict[str, Any]:
        """創建 OpenAI 工具調用響應消息"""
        return {
            "role": "tool",
            "tool_call_id": tool_call_id,
            "name": tool_name,
            "content": tool_result
        }


# ============================================================================
# 第三部分：MCP + OpenAI 整合客戶端
# ============================================================================

class MCPOpenAIClient:
    """
    整合 MCP 和 OpenAI 的客戶端

    使用 MCP 服務器提供工具，通過 OpenAI API 進行對話
    """

    def __init__(
        self,
        openai_api_key: str,
        mcp_server_command: str,
        mcp_server_args: List[str]
    ):
        self.api_key = openai_api_key
        self.mcp_command = mcp_server_command
        self.mcp_args = mcp_server_args

        self.mcp_tools: List[Dict[str, Any]] = []
        self.openai_functions: List[Dict[str, Any]] = []

    async def initialize(self):
        """初始化：連接 MCP 服務器並獲取工具"""
        print("【初始化 MCP + OpenAI 整合】")

        # 1. 連接 MCP 服務器
        print("1. 連接 MCP 服務器...")
        # 實際實現會使用 mcp.ClientSession
        # 這裡模擬獲取工具列表

        self.mcp_tools = [
            {
                "name": "search_files",
                "description": "在目錄中搜索文件",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "directory": {"type": "string"},
                        "pattern": {"type": "string"}
                    },
                    "required": ["directory", "pattern"]
                }
            },
            {
                "name": "read_file",
                "description": "讀取文件內容",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"}
                    },
                    "required": ["path"]
                }
            }
        ]

        # 2. 轉換為 OpenAI 格式
        print("2. 轉換工具格式...")
        converter = MCPToOpenAIConverter()
        self.openai_functions = converter.convert_tools_batch(self.mcp_tools)

        print(f"✓ 已載入 {len(self.mcp_tools)} 個工具")

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4-turbo-preview"
    ) -> str:
        """
        與 OpenAI 對話，自動處理工具調用

        Args:
            messages: 對話歷史
            model: 使用的模型

        Returns:
            助手的響應
        """
        print(f"\n【調用 OpenAI API】")
        print(f"模型: {model}")
        print(f"消息數: {len(messages)}")

        # 模擬 OpenAI API 調用
        # 實際實現會使用 openai.ChatCompletion.create()

        # 模擬助手決定調用工具
        tool_calls = [
            {
                "id": "call_123",
                "type": "function",
                "function": {
                    "name": "search_files",
                    "arguments": json.dumps({
                        "directory": "/home/user",
                        "pattern": "*.py"
                    })
                }
            }
        ]

        # 調用 MCP 工具
        for tool_call in tool_calls:
            function_name = tool_call["function"]["name"]
            arguments = json.loads(tool_call["function"]["arguments"])

            print(f"\n調用工具: {function_name}")
            print(f"參數: {json.dumps(arguments, ensure_ascii=False)}")

            # 通過 MCP 執行工具
            result = await self._call_mcp_tool(function_name, arguments)

            # 添加工具響應到消息
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "name": function_name,
                "content": result
            })

        # 模擬最終響應
        return "根據搜索結果，找到了以下 Python 文件..."

    async def _call_mcp_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> str:
        """調用 MCP 工具"""
        # 實際實現會通過 MCP 客戶端調用
        # 這裡模擬執行結果

        await asyncio.sleep(0.3)  # 模擬執行時間

        return f"工具 {tool_name} 執行結果（模擬）"


# ============================================================================
# 第四部分：完整示例應用
# ============================================================================

# 真實的 OpenAI + MCP 整合代碼
REAL_INTEGRATION_EXAMPLE = '''
"""
真實的 OpenAI + MCP 整合示例
"""

import asyncio
from openai import AsyncOpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPPoweredChatbot:
    """使用 MCP 工具的 OpenAI 聊天機器人"""

    def __init__(self, openai_api_key: str, mcp_server_path: str):
        self.client = AsyncOpenAI(api_key=openai_api_key)
        self.server_path = mcp_server_path
        self.session = None
        self.tools_openai_format = []

    async def initialize_mcp(self):
        """初始化 MCP 連接"""
        server_params = StdioServerParameters(
            command="python",
            args=[self.server_path]
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                self.session = session

                # 初始化
                await session.initialize()

                # 獲取工具列表
                tools_list = await session.list_tools()

                # 轉換為 OpenAI 格式
                for tool in tools_list:
                    self.tools_openai_format.append({
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": tool.inputSchema
                        }
                    })

    async def chat(self, user_message: str) -> str:
        """處理用戶消息"""
        messages = [{"role": "user", "content": user_message}]

        while True:
            # 調用 OpenAI
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages,
                tools=self.tools_openai_format
            )

            message = response.choices[0].message

            # 如果沒有工具調用，返回響應
            if not message.tool_calls:
                return message.content

            # 處理工具調用
            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)

                # 通過 MCP 執行工具
                result = await self.session.call_tool(
                    function_name,
                    arguments=arguments
                )

                # 添加工具響應
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": result.content[0].text
                })


async def main():
    bot = MCPPoweredChatbot(
        openai_api_key="your-api-key",
        mcp_server_path="/path/to/server.py"
    )

    await bot.initialize_mcp()

    response = await bot.chat("請搜索我的項目文件")
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
'''


# ============================================================================
# 第五部分：多 LLM 支持
# ============================================================================

class MultiLLMAdapter:
    """
    多 LLM 提供商適配器

    統一的接口支持 OpenAI、Anthropic、Google 等
    """

    def __init__(self, mcp_tools: List[Dict[str, Any]]):
        self.mcp_tools = mcp_tools

    def to_openai_format(self) -> List[Dict[str, Any]]:
        """轉換為 OpenAI 格式"""
        converter = MCPToOpenAIConverter()
        return converter.convert_tools_batch(self.mcp_tools)

    def to_anthropic_format(self) -> List[Dict[str, Any]]:
        """轉換為 Anthropic (Claude) 格式"""
        # Claude 使用類似的格式，但有細微差異
        return [
            {
                "name": tool["name"],
                "description": tool["description"],
                "input_schema": tool["inputSchema"]
            }
            for tool in self.mcp_tools
        ]

    def to_google_format(self) -> List[Dict[str, Any]]:
        """轉換為 Google (Gemini) 格式"""
        # Gemini 的 Function Calling 格式
        return [
            {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["inputSchema"]
            }
            for tool in self.mcp_tools
        ]


# ============================================================================
# 主程式示例
# ============================================================================

async def main():
    """主程式：OpenAI + MCP 整合示例"""

    print("=" * 70)
    print("OpenAI + MCP 整合示例")
    print("=" * 70)

    # 1. 格式對比
    print("\n【示例 1：MCP vs OpenAI Function Calling】")
    comparison = MCPvsOpenAIComparison()
    comp_data = comparison.show_comparison()

    for category, items in list(comp_data.items())[:2]:
        print(f"\n{category}:")
        for item in items:
            print(f"  • {item}")

    # 2. 格式轉換
    print("\n【示例 2：格式轉換】")
    mcp_tool = {
        "name": "calculate",
        "description": "執行數學計算",
        "inputSchema": {
            "type": "object",
            "properties": {
                "expression": {"type": "string"}
            },
            "required": ["expression"]
        }
    }

    converter = MCPToOpenAIConverter()
    openai_func = converter.convert_tool_to_function(mcp_tool)

    print("MCP 格式:")
    print(json.dumps(mcp_tool, indent=2, ensure_ascii=False))

    print("\nOpenAI 格式:")
    print(json.dumps(openai_func, indent=2, ensure_ascii=False))

    # 3. 整合客戶端
    print("\n【示例 3：整合客戶端】")
    client = MCPOpenAIClient(
        openai_api_key="sk-...",
        mcp_server_command="python",
        mcp_server_args=["server.py"]
    )

    await client.initialize()

    # 4. 多 LLM 支持
    print("\n【示例 4：多 LLM 提供商支持】")
    adapter = MultiLLMAdapter(client.mcp_tools)

    print("支持的格式:")
    print("  • OpenAI: ✓")
    print("  • Anthropic (Claude): ✓")
    print("  • Google (Gemini): ✓")

    # 5. 真實實現
    print("\n【示例 5：真實整合代碼】")
    print("完整示例代碼：")
    print(REAL_INTEGRATION_EXAMPLE[:500] + "...\n[代碼已截斷]")

    print("\n" + "=" * 70)
    print("下一步：查看 10_代碼執行優化.py 學習 Code Execution")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())

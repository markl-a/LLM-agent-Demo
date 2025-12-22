"""
創建 MCP 客戶端
===============

本模組展示如何創建 MCP 客戶端來連接和使用 MCP 服務器。
學習客戶端的初始化、工具調用、資源訪問等操作。

學習目標：
- 連接到 MCP 服務器
- 調用服務器提供的工具
- 處理服務器響應
- 實現重試和錯誤處理

作者：Claude (Anthropic)
日期：2025-12-22
"""

import asyncio
import json
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


# ============================================================================
# 第一部分：基本客戶端
# ============================================================================

class TransportType(Enum):
    """傳輸類型"""
    STDIO = "stdio"  # 標準輸入輸出
    HTTP_SSE = "http_sse"  # HTTP Server-Sent Events
    WEBSOCKET = "websocket"  # WebSocket


@dataclass
class ServerInfo:
    """服務器資訊"""
    name: str
    version: str
    capabilities: Dict[str, Any]


class SimpleMCPClient:
    """
    簡單的 MCP 客戶端

    用於理解客戶端的基本結構和工作流程
    """

    def __init__(self, server_name: str = "example-server"):
        self.server_name = server_name
        self.connected = False
        self.server_info: Optional[ServerInfo] = None
        self.available_tools: List[Dict[str, Any]] = []

    async def connect(self) -> bool:
        """連接到服務器"""
        print(f"正在連接到服務器: {self.server_name}...")

        # 模擬連接過程
        await asyncio.sleep(0.5)

        # 模擬初始化響應
        self.server_info = ServerInfo(
            name=self.server_name,
            version="1.0.0",
            capabilities={
                "tools": True,
                "resources": False,
                "prompts": False
            }
        )

        self.connected = True
        print("✓ 已成功連接到服務器")
        return True

    async def list_tools(self) -> List[Dict[str, Any]]:
        """列出可用工具"""
        if not self.connected:
            raise RuntimeError("未連接到服務器")

        # 模擬工具列表
        self.available_tools = [
            {
                "name": "hello",
                "description": "向用戶問好"
            },
            {
                "name": "echo",
                "description": "回聲測試"
            }
        ]

        return self.available_tools

    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> str:
        """調用工具"""
        if not self.connected:
            raise RuntimeError("未連接到服務器")

        print(f"調用工具: {tool_name}")
        print(f"參數: {json.dumps(arguments, ensure_ascii=False, indent=2)}")

        # 模擬工具調用
        await asyncio.sleep(0.3)

        # 模擬響應
        return f"工具 {tool_name} 執行成功"

    async def disconnect(self):
        """斷開連接"""
        if self.connected:
            print("正在斷開連接...")
            await asyncio.sleep(0.2)
            self.connected = False
            print("✓ 已斷開連接")


# ============================================================================
# 第二部分：完整的 MCP 客戶端
# ============================================================================

class MCPClient:
    """
    功能完整的 MCP 客戶端

    支持完整的 MCP 協議特性
    """

    def __init__(
        self,
        command: str,
        args: List[str],
        env: Optional[Dict[str, str]] = None
    ):
        """
        初始化客戶端

        Args:
            command: 服務器命令（如 "python"）
            args: 命令參數（如 ["server.py"]）
            env: 環境變數
        """
        self.command = command
        self.args = args
        self.env = env or {}
        self.server_info: Optional[ServerInfo] = None
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.resources: Dict[str, Dict[str, Any]] = {}
        self.prompts: Dict[str, Dict[str, Any]] = {}

    async def initialize(self) -> ServerInfo:
        """
        初始化連接

        執行 MCP 握手協議
        """
        print("【初始化階段】")
        print(f"命令: {self.command} {' '.join(self.args)}")

        # 1. 發送初始化請求
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "1.0.0",
                "capabilities": {
                    "tools": {},
                    "resources": {},
                    "prompts": {}
                },
                "clientInfo": {
                    "name": "python-mcp-client",
                    "version": "1.0.0"
                }
            }
        }

        print("發送初始化請求...")
        # 實際實現中會通過傳輸層發送

        # 2. 接收服務器響應
        await asyncio.sleep(0.3)

        # 模擬服務器響應
        server_response = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "protocolVersion": "1.0.0",
                "capabilities": {
                    "tools": {"listChanged": True},
                    "resources": {"subscribe": True},
                    "prompts": {"listChanged": True}
                },
                "serverInfo": {
                    "name": "example-server",
                    "version": "1.0.0"
                }
            }
        }

        self.server_info = ServerInfo(
            name=server_response["result"]["serverInfo"]["name"],
            version=server_response["result"]["serverInfo"]["version"],
            capabilities=server_response["result"]["capabilities"]
        )

        print(f"✓ 服務器: {self.server_info.name} v{self.server_info.version}")
        print(f"✓ 支持的功能: {list(self.server_info.capabilities.keys())}")

        return self.server_info

    async def discover_tools(self) -> Dict[str, Dict[str, Any]]:
        """發現可用工具"""
        print("\n【發現工具】")

        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }

        await asyncio.sleep(0.2)

        # 模擬工具列表響應
        tools_list = [
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
            },
            {
                "name": "write_file",
                "description": "寫入文件",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "content": {"type": "string"}
                    },
                    "required": ["path", "content"]
                }
            }
        ]

        for tool in tools_list:
            self.tools[tool["name"]] = tool
            print(f"  ✓ {tool['name']}: {tool['description']}")

        return self.tools

    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        timeout: int = 30
    ) -> Any:
        """
        調用工具

        Args:
            tool_name: 工具名稱
            arguments: 工具參數
            timeout: 超時時間（秒）

        Returns:
            工具執行結果
        """
        if tool_name not in self.tools:
            raise ValueError(f"工具不存在: {tool_name}")

        print(f"\n【調用工具: {tool_name}】")
        print(f"參數: {json.dumps(arguments, ensure_ascii=False, indent=2)}")

        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }

        # 模擬工具執行
        await asyncio.sleep(0.5)

        # 模擬響應
        response = {
            "jsonrpc": "2.0",
            "id": 3,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": f"工具 {tool_name} 執行完成"
                    }
                ]
            }
        }

        result = response["result"]["content"][0]["text"]
        print(f"結果: {result}")

        return result

    async def get_resource(self, uri: str) -> str:
        """獲取資源"""
        print(f"\n【獲取資源: {uri}】")

        request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "resources/read",
            "params": {
                "uri": uri
            }
        }

        await asyncio.sleep(0.3)

        # 模擬資源內容
        return f"資源 {uri} 的內容"

    async def close(self):
        """關閉連接"""
        print("\n【關閉連接】")
        await asyncio.sleep(0.1)
        print("✓ 連接已關閉")


# ============================================================================
# 第三部分：帶重試機制的客戶端
# ============================================================================

class RobustMCPClient(MCPClient):
    """
    帶重試和錯誤處理的健壯客戶端
    """

    def __init__(
        self,
        command: str,
        args: List[str],
        env: Optional[Dict[str, str]] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        super().__init__(command, args, env)
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    async def call_tool_with_retry(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Any:
        """帶重試的工具調用"""
        for attempt in range(self.max_retries):
            try:
                print(f"嘗試 {attempt + 1}/{self.max_retries}...")
                result = await self.call_tool(tool_name, arguments)
                return result

            except Exception as e:
                print(f"✗ 錯誤: {e}")

                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    print(f"等待 {wait_time} 秒後重試...")
                    await asyncio.sleep(wait_time)
                else:
                    print("已達到最大重試次數")
                    raise


# ============================================================================
# 第四部分：真實客戶端實現（使用官方 SDK）
# ============================================================================

REAL_CLIENT_EXAMPLE = '''
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def use_mcp_server():
    """使用 MCP 服務器的真實示例"""

    # 配置服務器參數
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"],
        env={"LOG_LEVEL": "INFO"}
    )

    # 連接到服務器
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            # 初始化
            await session.initialize()

            # 列出工具
            tools = await session.list_tools()
            print(f"可用工具: {[t.name for t in tools]}")

            # 調用工具
            result = await session.call_tool(
                "read_file",
                arguments={"path": "/tmp/test.txt"}
            )

            print(f"結果: {result.content}")
'''


# ============================================================================
# 主程式示例
# ============================================================================

async def main():
    """主程式：測試各種客戶端"""

    print("=" * 70)
    print("MCP 客戶端創建示例")
    print("=" * 70)

    # 1. 簡單客戶端
    print("\n【示例 1：簡單客戶端】")
    simple_client = SimpleMCPClient("demo-server")

    await simple_client.connect()
    tools = await simple_client.list_tools()
    print(f"可用工具: {[t['name'] for t in tools]}")

    result = await simple_client.call_tool("hello", {"name": "開發者"})
    print(f"結果: {result}")

    await simple_client.disconnect()

    # 2. 完整客戶端
    print("\n" + "=" * 70)
    print("【示例 2：完整 MCP 客戶端】")

    client = MCPClient(
        command="python",
        args=["server.py"],
        env={"DEBUG": "true"}
    )

    # 初始化
    server_info = await client.initialize()

    # 發現工具
    tools = await client.discover_tools()

    # 調用工具
    await client.call_tool(
        "read_file",
        {"path": "/tmp/example.txt"}
    )

    # 關閉
    await client.close()

    # 3. 健壯客戶端
    print("\n" + "=" * 70)
    print("【示例 3：帶重試機制的客戶端】")

    robust_client = RobustMCPClient(
        command="python",
        args=["server.py"],
        max_retries=3
    )

    await robust_client.initialize()
    await robust_client.discover_tools()

    # 帶重試的工具調用
    try:
        await robust_client.call_tool_with_retry(
            "write_file",
            {"path": "/tmp/test.txt", "content": "Hello MCP!"}
        )
    except Exception as e:
        print(f"調用失敗: {e}")

    await robust_client.close()

    # 4. 真實實現示例
    print("\n" + "=" * 70)
    print("【示例 4：真實客戶端實現（官方 SDK）】")
    print(REAL_CLIENT_EXAMPLE)

    print("\n" + "=" * 70)
    print("下一步：查看 05_工具定義.py 學習如何定義工具")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())

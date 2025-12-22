"""
創建 MCP 服務器
===============

本模組展示如何從零開始構建一個自定義的 MCP 服務器。
學習服務器的基本結構、工具定義、錯誤處理等核心概念。

學習目標：
- 理解 MCP 服務器的生命週期
- 實現基本的工具函數
- 處理客戶端請求
- 實現錯誤處理和日誌記錄

作者：Claude (Anthropic)
日期：2025-12-22
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


# 模擬 MCP SDK（實際使用時從 mcp 包導入）
# from mcp.server import Server
# from mcp.server.stdio import stdio_server
# from mcp.types import Tool, TextContent


# ============================================================================
# 第一部分：簡單的 MCP 服務器
# ============================================================================

class SimpleMCPServer:
    """
    最簡單的 MCP 服務器示例

    這個服務器只提供一個工具：hello
    """

    def __init__(self, name: str = "simple-server"):
        self.name = name
        self.tools: List[Dict[str, Any]] = []
        self.setup_tools()

    def setup_tools(self):
        """設置可用的工具"""
        self.tools.append({
            "name": "hello",
            "description": "向指定的人問好",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "要問好的人名"
                    }
                },
                "required": ["name"]
            }
        })

    async def handle_hello(self, name: str) -> str:
        """處理 hello 工具調用"""
        return f"你好，{name}！歡迎使用 MCP 服務器。"

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """調用工具"""
        if tool_name == "hello":
            return await self.handle_hello(arguments.get("name", "訪客"))
        else:
            raise ValueError(f"未知的工具: {tool_name}")

    def list_tools(self) -> List[Dict[str, Any]]:
        """列出所有可用工具"""
        return self.tools


# ============================================================================
# 第二部分：功能完整的 MCP 服務器
# ============================================================================

class FileSystemServer:
    """
    文件系統操作服務器

    提供文件讀取、寫入、列表等功能
    """

    def __init__(self, allowed_directories: List[str]):
        self.name = "filesystem-server"
        self.allowed_directories = allowed_directories
        self.logger = self._setup_logger()
        self.tools = self._define_tools()

    def _setup_logger(self) -> logging.Logger:
        """配置日誌記錄器"""
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.INFO)

        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def _define_tools(self) -> List[Dict[str, Any]]:
        """定義所有工具"""
        return [
            {
                "name": "read_file",
                "description": "讀取文件內容",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "文件路徑"},
                        "encoding": {
                            "type": "string",
                            "enum": ["utf-8", "ascii"],
                            "default": "utf-8"
                        }
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
                        "path": {"type": "string", "description": "文件路徑"},
                        "content": {"type": "string", "description": "文件內容"},
                        "encoding": {"type": "string", "default": "utf-8"}
                    },
                    "required": ["path", "content"]
                }
            },
            {
                "name": "list_directory",
                "description": "列出目錄內容",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "目錄路徑"}
                    },
                    "required": ["path"]
                }
            }
        ]

    def _is_path_allowed(self, path: str) -> bool:
        """檢查路徑是否在允許的目錄中"""
        import os
        abs_path = os.path.abspath(path)

        for allowed_dir in self.allowed_directories:
            if abs_path.startswith(os.path.abspath(allowed_dir)):
                return True

        return False

    async def read_file(self, path: str, encoding: str = "utf-8") -> str:
        """讀取文件"""
        if not self._is_path_allowed(path):
            raise PermissionError(f"不允許訪問路徑: {path}")

        self.logger.info(f"讀取文件: {path}")

        try:
            with open(path, 'r', encoding=encoding) as f:
                content = f.read()
            return content
        except FileNotFoundError:
            raise FileNotFoundError(f"文件不存在: {path}")
        except Exception as e:
            self.logger.error(f"讀取文件失敗: {e}")
            raise

    async def write_file(self, path: str, content: str, encoding: str = "utf-8") -> str:
        """寫入文件"""
        if not self._is_path_allowed(path):
            raise PermissionError(f"不允許訪問路徑: {path}")

        self.logger.info(f"寫入文件: {path}")

        try:
            with open(path, 'w', encoding=encoding) as f:
                f.write(content)
            return f"成功寫入 {len(content)} 個字符到 {path}"
        except Exception as e:
            self.logger.error(f"寫入文件失敗: {e}")
            raise

    async def list_directory(self, path: str) -> List[str]:
        """列出目錄內容"""
        import os

        if not self._is_path_allowed(path):
            raise PermissionError(f"不允許訪問路徑: {path}")

        self.logger.info(f"列出目錄: {path}")

        try:
            entries = os.listdir(path)
            return sorted(entries)
        except FileNotFoundError:
            raise FileNotFoundError(f"目錄不存在: {path}")
        except Exception as e:
            self.logger.error(f"列出目錄失敗: {e}")
            raise

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """調用工具"""
        if tool_name == "read_file":
            return await self.read_file(
                arguments["path"],
                arguments.get("encoding", "utf-8")
            )
        elif tool_name == "write_file":
            return await self.write_file(
                arguments["path"],
                arguments["content"],
                arguments.get("encoding", "utf-8")
            )
        elif tool_name == "list_directory":
            result = await self.list_directory(arguments["path"])
            return "\n".join(result)
        else:
            raise ValueError(f"未知的工具: {tool_name}")


# ============================================================================
# 第三部分：使用裝飾器的現代 MCP 服務器
# ============================================================================

class ModernMCPServer:
    """
    使用裝飾器模式的現代 MCP 服務器

    這是推薦的實現方式，代碼更簡潔優雅
    """

    def __init__(self, name: str = "modern-server"):
        self.name = name
        self.tools_registry: Dict[str, callable] = {}
        self.tools_metadata: List[Dict[str, Any]] = []

    def tool(self, description: str, input_schema: Dict[str, Any]):
        """
        工具裝飾器

        用法：
        @server.tool(
            description="計算兩數之和",
            input_schema={...}
        )
        async def add(a: int, b: int) -> int:
            return a + b
        """
        def decorator(func):
            tool_name = func.__name__

            # 註冊工具函數
            self.tools_registry[tool_name] = func

            # 保存工具元數據
            self.tools_metadata.append({
                "name": tool_name,
                "description": description,
                "inputSchema": input_schema
            })

            return func

        return decorator

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """調用工具"""
        if tool_name not in self.tools_registry:
            raise ValueError(f"未知的工具: {tool_name}")

        func = self.tools_registry[tool_name]
        return await func(**arguments)

    def list_tools(self) -> List[Dict[str, Any]]:
        """列出所有工具"""
        return self.tools_metadata


# 使用示例
def create_calculator_server() -> ModernMCPServer:
    """創建計算器服務器"""
    server = ModernMCPServer("calculator-server")

    @server.tool(
        description="計算兩個數的和",
        input_schema={
            "type": "object",
            "properties": {
                "a": {"type": "number"},
                "b": {"type": "number"}
            },
            "required": ["a", "b"]
        }
    )
    async def add(a: float, b: float) -> float:
        """加法"""
        return a + b

    @server.tool(
        description="計算兩個數的差",
        input_schema={
            "type": "object",
            "properties": {
                "a": {"type": "number"},
                "b": {"type": "number"}
            },
            "required": ["a", "b"]
        }
    )
    async def subtract(a: float, b: float) -> float:
        """減法"""
        return a - b

    @server.tool(
        description="計算兩個數的積",
        input_schema={
            "type": "object",
            "properties": {
                "a": {"type": "number"},
                "b": {"type": "number"}
            },
            "required": ["a", "b"]
        }
    )
    async def multiply(a: float, b: float) -> float:
        """乘法"""
        return a * b

    @server.tool(
        description="計算兩個數的商",
        input_schema={
            "type": "object",
            "properties": {
                "a": {"type": "number"},
                "b": {"type": "number"}
            },
            "required": ["a", "b"]
        }
    )
    async def divide(a: float, b: float) -> float:
        """除法"""
        if b == 0:
            raise ValueError("除數不能為零")
        return a / b

    return server


# ============================================================================
# 第四部分：真實的 MCP 服務器實現（使用官方 SDK）
# ============================================================================

# 真實實現示例（需要安裝 mcp 包）
REAL_SERVER_EXAMPLE = '''
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import asyncio

# 創建服務器實例
app = Server("my-mcp-server")

# 使用裝飾器定義工具
@app.tool()
async def get_current_time() -> str:
    """獲取當前時間"""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@app.tool()
async def calculate_sum(numbers: list[float]) -> float:
    """計算數字列表的總和"""
    return sum(numbers)

@app.tool()
async def reverse_string(text: str) -> str:
    """反轉字符串"""
    return text[::-1]

# 運行服務器
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
'''


# ============================================================================
# 主程式示例
# ============================================================================

async def main():
    """主程式：測試各種服務器實現"""

    print("=" * 70)
    print("MCP 服務器創建示例")
    print("=" * 70)

    # 1. 簡單服務器
    print("\n【示例 1：簡單 MCP 服務器】")
    simple_server = SimpleMCPServer()
    print(f"服務器名稱: {simple_server.name}")
    print(f"可用工具: {[t['name'] for t in simple_server.list_tools()]}")

    result = await simple_server.call_tool("hello", {"name": "開發者"})
    print(f"調用結果: {result}")

    # 2. 文件系統服務器
    print("\n【示例 2：文件系統服務器】")
    fs_server = FileSystemServer(allowed_directories=["/tmp"])
    print(f"服務器名稱: {fs_server.name}")
    print(f"可用工具: {[t['name'] for t in fs_server.tools]}")
    print(f"允許的目錄: {fs_server.allowed_directories}")

    # 3. 現代服務器（裝飾器模式）
    print("\n【示例 3：現代 MCP 服務器（計算器）】")
    calc_server = create_calculator_server()
    print(f"服務器名稱: {calc_server.name}")
    print(f"可用工具: {[t['name'] for t in calc_server.list_tools()]}")

    # 測試計算
    add_result = await calc_server.call_tool("add", {"a": 10, "b": 5})
    print(f"10 + 5 = {add_result}")

    multiply_result = await calc_server.call_tool("multiply", {"a": 10, "b": 5})
    print(f"10 × 5 = {multiply_result}")

    # 4. 展示真實實現代碼
    print("\n【示例 4：真實 MCP 服務器實現（使用官方 SDK）】")
    print("代碼示例：")
    print(REAL_SERVER_EXAMPLE)

    print("\n" + "=" * 70)
    print("下一步：查看 04_創建MCP客戶端.py 學習如何連接服務器")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())

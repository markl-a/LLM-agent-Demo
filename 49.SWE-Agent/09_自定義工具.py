#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SWE-Agent 自定義工具範例
========================

這個範例展示如何為 SWE-Agent 創建和集成自定義工具：
1. 工具定義和註冊
2. 命令行工具包裝
3. API 工具集成
4. 數據庫工具
5. 文件系統工具
6. 工具鏈組合

自定義工具讓 Agent 能夠訪問項目特定的功能和資源。

作者: SWE-Agent 團隊
日期: 2025-12-31
"""

import os
import subprocess
import json
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import inspect
from enum import Enum

# SWE-Agent
from sweagent.tools import Tool, ToolRegistry
from sweagent.agent import SWEAgent

from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax


class ToolCategory(Enum):
    """工具類別"""
    FILE_SYSTEM = "file_system"
    CODE_ANALYSIS = "code_analysis"
    DATABASE = "database"
    API = "api"
    BUILD = "build"
    TEST = "test"
    GIT = "git"
    CUSTOM = "custom"


@dataclass
class ToolParameter:
    """
    工具參數定義
    """
    name: str
    type: type
    description: str
    required: bool = True
    default: Any = None


@dataclass
class ToolMetadata:
    """
    工具元數據
    """
    name: str
    description: str
    category: ToolCategory
    parameters: List[ToolParameter]
    returns: str
    examples: List[str] = field(default_factory=list)


class BaseTool(ABC):
    """
    工具基類

    所有自定義工具都應繼承此類
    """

    def __init__(self):
        """初始化工具"""
        self.console = Console()
        self.metadata = self._define_metadata()

    @abstractmethod
    def _define_metadata(self) -> ToolMetadata:
        """
        定義工具元數據

        Returns:
            工具元數據
        """
        pass

    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """
        執行工具

        Args:
            **kwargs: 工具參數

        Returns:
            執行結果
        """
        pass

    def validate_parameters(self, **kwargs) -> bool:
        """
        驗證參數

        Args:
            **kwargs: 參數字典

        Returns:
            是否有效
        """
        for param in self.metadata.parameters:
            if param.required and param.name not in kwargs:
                raise ValueError(f"缺少必需參數: {param.name}")

            if param.name in kwargs:
                value = kwargs[param.name]
                if not isinstance(value, param.type):
                    raise TypeError(
                        f"參數 {param.name} 類型錯誤: "
                        f"期望 {param.type}, 得到 {type(value)}"
                    )

        return True

    def get_signature(self) -> str:
        """獲取工具簽名"""
        params = []
        for param in self.metadata.parameters:
            param_str = f"{param.name}: {param.type.__name__}"
            if not param.required:
                param_str += f" = {param.default}"
            params.append(param_str)

        return f"{self.metadata.name}({', '.join(params)})"


class FileSearchTool(BaseTool):
    """
    文件搜索工具

    在代碼庫中搜索文件
    """

    def _define_metadata(self) -> ToolMetadata:
        """定義元數據"""
        return ToolMetadata(
            name="file_search",
            description="在代碼庫中搜索匹配模式的文件",
            category=ToolCategory.FILE_SYSTEM,
            parameters=[
                ToolParameter(
                    name="pattern",
                    type=str,
                    description="搜索模式（支持通配符）"
                ),
                ToolParameter(
                    name="path",
                    type=str,
                    description="搜索路徑",
                    required=False,
                    default="."
                )
            ],
            returns="匹配的文件路徑列表",
            examples=[
                "file_search(pattern='*.py', path='src')",
                "file_search(pattern='test_*.py')"
            ]
        )

    def execute(self, pattern: str, path: str = ".") -> List[str]:
        """
        執行文件搜索

        Args:
            pattern: 搜索模式
            path: 搜索路徑

        Returns:
            匹配的文件列表
        """
        self.validate_parameters(pattern=pattern, path=path)

        from pathlib import Path

        search_path = Path(path)
        matches = list(search_path.rglob(pattern))

        result = [str(m) for m in matches]

        logger.info(f"文件搜索 '{pattern}' 在 '{path}': 找到 {len(result)} 個匹配")

        return result


class CodeGrepTool(BaseTool):
    """
    代碼搜索工具

    在代碼中搜索文本模式
    """

    def _define_metadata(self) -> ToolMetadata:
        """定義元數據"""
        return ToolMetadata(
            name="code_grep",
            description="在代碼中搜索文本模式",
            category=ToolCategory.CODE_ANALYSIS,
            parameters=[
                ToolParameter(
                    name="pattern",
                    type=str,
                    description="搜索模式（正則表達式）"
                ),
                ToolParameter(
                    name="file_pattern",
                    type=str,
                    description="文件模式",
                    required=False,
                    default="*.py"
                ),
                ToolParameter(
                    name="context_lines",
                    type=int,
                    description="上下文行數",
                    required=False,
                    default=2
                )
            ],
            returns="搜索結果列表",
            examples=[
                "code_grep(pattern='def calculate', file_pattern='*.py')",
                "code_grep(pattern='TODO', context_lines=1)"
            ]
        )

    def execute(
        self,
        pattern: str,
        file_pattern: str = "*.py",
        context_lines: int = 2
    ) -> List[Dict]:
        """
        執行代碼搜索

        Args:
            pattern: 搜索模式
            file_pattern: 文件模式
            context_lines: 上下文行數

        Returns:
            搜索結果
        """
        self.validate_parameters(
            pattern=pattern,
            file_pattern=file_pattern,
            context_lines=context_lines
        )

        # 使用 ripgrep 或 grep
        try:
            cmd = [
                "rg",
                "--json",
                f"-C{context_lines}",
                pattern,
                "-g",
                file_pattern
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )

            matches = []
            for line in result.stdout.split('\n'):
                if line:
                    try:
                        data = json.loads(line)
                        if data.get("type") == "match":
                            matches.append({
                                "file": data["data"]["path"]["text"],
                                "line": data["data"]["line_number"],
                                "content": data["data"]["lines"]["text"]
                            })
                    except:
                        pass

            logger.info(f"代碼搜索 '{pattern}': 找到 {len(matches)} 個匹配")

            return matches

        except FileNotFoundError:
            logger.warning("ripgrep 未安裝，使用 Python 實現")
            return self._python_grep(pattern, file_pattern)

    def _python_grep(self, pattern: str, file_pattern: str) -> List[Dict]:
        """Python 實現的 grep"""
        import re
        from pathlib import Path

        matches = []
        regex = re.compile(pattern)

        for file_path in Path(".").rglob(file_pattern):
            try:
                content = file_path.read_text(encoding='utf-8')
                lines = content.split('\n')

                for i, line in enumerate(lines, 1):
                    if regex.search(line):
                        matches.append({
                            "file": str(file_path),
                            "line": i,
                            "content": line
                        })
            except:
                pass

        return matches


class DatabaseQueryTool(BaseTool):
    """
    數據庫查詢工具

    執行數據庫查詢
    """

    def __init__(self, connection_string: str):
        """
        初始化

        Args:
            connection_string: 數據庫連接字符串
        """
        self.connection_string = connection_string
        super().__init__()

    def _define_metadata(self) -> ToolMetadata:
        """定義元數據"""
        return ToolMetadata(
            name="db_query",
            description="執行數據庫查詢",
            category=ToolCategory.DATABASE,
            parameters=[
                ToolParameter(
                    name="query",
                    type=str,
                    description="SQL 查詢語句"
                ),
                ToolParameter(
                    name="params",
                    type=dict,
                    description="查詢參數",
                    required=False,
                    default={}
                )
            ],
            returns="查詢結果",
            examples=[
                "db_query(query='SELECT * FROM users WHERE id = :id', params={'id': 1})"
            ]
        )

    def execute(self, query: str, params: Dict = None) -> List[Dict]:
        """
        執行查詢

        Args:
            query: SQL 查詢
            params: 查詢參數

        Returns:
            查詢結果
        """
        self.validate_parameters(query=query)

        try:
            from sqlalchemy import create_engine, text

            engine = create_engine(self.connection_string)

            with engine.connect() as conn:
                result = conn.execute(text(query), params or {})
                rows = result.fetchall()

                # 轉換為字典列表
                columns = result.keys()
                results = [dict(zip(columns, row)) for row in rows]

            logger.info(f"數據庫查詢執行成功: {len(results)} 行")

            return results

        except Exception as e:
            logger.error(f"數據庫查詢失敗: {e}")
            raise


class APICallTool(BaseTool):
    """
    API 調用工具

    調用外部 API
    """

    def _define_metadata(self) -> ToolMetadata:
        """定義元數據"""
        return ToolMetadata(
            name="api_call",
            description="調用外部 API",
            category=ToolCategory.API,
            parameters=[
                ToolParameter(
                    name="url",
                    type=str,
                    description="API URL"
                ),
                ToolParameter(
                    name="method",
                    type=str,
                    description="HTTP 方法",
                    required=False,
                    default="GET"
                ),
                ToolParameter(
                    name="headers",
                    type=dict,
                    description="請求頭",
                    required=False,
                    default={}
                ),
                ToolParameter(
                    name="data",
                    type=dict,
                    description="請求數據",
                    required=False,
                    default={}
                )
            ],
            returns="API 響應",
            examples=[
                "api_call(url='https://api.github.com/users/octocat')",
                "api_call(url='https://api.example.com/data', method='POST', data={'key': 'value'})"
            ]
        )

    def execute(
        self,
        url: str,
        method: str = "GET",
        headers: Dict = None,
        data: Dict = None
    ) -> Dict:
        """
        執行 API 調用

        Args:
            url: API URL
            method: HTTP 方法
            headers: 請求頭
            data: 請求數據

        Returns:
            API 響應
        """
        self.validate_parameters(url=url, method=method)

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers or {},
                json=data
            )

            response.raise_for_status()

            result = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "data": response.json() if response.content else None
            }

            logger.info(f"API 調用成功: {method} {url}")

            return result

        except Exception as e:
            logger.error(f"API 調用失敗: {e}")
            raise


class GitOperationTool(BaseTool):
    """
    Git 操作工具

    執行 Git 命令
    """

    def _define_metadata(self) -> ToolMetadata:
        """定義元數據"""
        return ToolMetadata(
            name="git_operation",
            description="執行 Git 操作",
            category=ToolCategory.GIT,
            parameters=[
                ToolParameter(
                    name="operation",
                    type=str,
                    description="Git 操作（status, diff, log, etc.）"
                ),
                ToolParameter(
                    name="args",
                    type=list,
                    description="操作參數",
                    required=False,
                    default=[]
                )
            ],
            returns="操作結果",
            examples=[
                "git_operation(operation='status')",
                "git_operation(operation='log', args=['--oneline', '-5'])"
            ]
        )

    def execute(self, operation: str, args: List[str] = None) -> str:
        """
        執行 Git 操作

        Args:
            operation: Git 操作
            args: 參數列表

        Returns:
            操作輸出
        """
        self.validate_parameters(operation=operation)

        cmd = ["git", operation] + (args or [])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            logger.info(f"Git 操作執行成功: {operation}")

            return result.stdout

        except subprocess.CalledProcessError as e:
            logger.error(f"Git 操作失敗: {e}")
            return e.stderr


class CustomToolRegistry:
    """
    自定義工具註冊表

    管理所有自定義工具
    """

    def __init__(self):
        """初始化註冊表"""
        self.tools: Dict[str, BaseTool] = {}
        self.console = Console()

        logger.info("工具註冊表初始化")

    def register(self, tool: BaseTool):
        """
        註冊工具

        Args:
            tool: 工具實例
        """
        tool_name = tool.metadata.name

        if tool_name in self.tools:
            logger.warning(f"工具 '{tool_name}' 已存在，將被覆蓋")

        self.tools[tool_name] = tool

        self.console.print(f"[green]✓ 工具已註冊: {tool_name}[/green]")

        logger.info(f"工具註冊: {tool_name}")

    def unregister(self, tool_name: str):
        """
        取消註冊工具

        Args:
            tool_name: 工具名稱
        """
        if tool_name in self.tools:
            del self.tools[tool_name]
            self.console.print(f"[yellow]工具已取消註冊: {tool_name}[/yellow]")
        else:
            logger.warning(f"工具不存在: {tool_name}")

    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """
        獲取工具

        Args:
            tool_name: 工具名稱

        Returns:
            工具實例
        """
        return self.tools.get(tool_name)

    def list_tools(self) -> List[str]:
        """
        列出所有工具

        Returns:
            工具名稱列表
        """
        return list(self.tools.keys())

    def display_tools(self):
        """顯示所有工具"""
        table = Table(title="已註冊的工具")
        table.add_column("名稱", style="cyan")
        table.add_column("類別", style="magenta")
        table.add_column("描述")

        for tool_name, tool in self.tools.items():
            table.add_row(
                tool_name,
                tool.metadata.category.value,
                tool.metadata.description
            )

        self.console.print(table)

    def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """
        執行工具

        Args:
            tool_name: 工具名稱
            **kwargs: 工具參數

        Returns:
            執行結果
        """
        tool = self.get_tool(tool_name)

        if not tool:
            raise ValueError(f"工具不存在: {tool_name}")

        return tool.execute(**kwargs)


class ToolBuilder:
    """
    工具構建器

    幫助快速創建簡單工具
    """

    @staticmethod
    def from_function(
        func: Callable,
        name: str,
        description: str,
        category: ToolCategory = ToolCategory.CUSTOM
    ) -> BaseTool:
        """
        從函數創建工具

        Args:
            func: 函數
            name: 工具名稱
            description: 工具描述
            category: 工具類別

        Returns:
            工具實例
        """

        # 檢查函數簽名
        sig = inspect.signature(func)

        parameters = []
        for param_name, param in sig.parameters.items():
            param_type = param.annotation if param.annotation != inspect.Parameter.empty else str

            parameters.append(ToolParameter(
                name=param_name,
                type=param_type,
                description=f"參數 {param_name}",
                required=param.default == inspect.Parameter.empty,
                default=param.default if param.default != inspect.Parameter.empty else None
            ))

        # 創建工具類
        class FunctionTool(BaseTool):
            def _define_metadata(self) -> ToolMetadata:
                return ToolMetadata(
                    name=name,
                    description=description,
                    category=category,
                    parameters=parameters,
                    returns="函數返回值"
                )

            def execute(self, **kwargs) -> Any:
                self.validate_parameters(**kwargs)
                return func(**kwargs)

        return FunctionTool()


class ToolChain:
    """
    工具鏈

    組合多個工具形成工作流
    """

    def __init__(self, name: str):
        """
        初始化

        Args:
            name: 工具鏈名稱
        """
        self.name = name
        self.steps: List[Tuple[str, Dict]] = []
        self.console = Console()

    def add_step(self, tool_name: str, params: Dict):
        """
        添加步驟

        Args:
            tool_name: 工具名稱
            params: 工具參數
        """
        self.steps.append((tool_name, params))

    def execute(self, registry: CustomToolRegistry) -> List[Any]:
        """
        執行工具鏈

        Args:
            registry: 工具註冊表

        Returns:
            每個步驟的結果
        """
        self.console.print(f"[bold]執行工具鏈: {self.name}[/bold]")

        results = []

        for i, (tool_name, params) in enumerate(self.steps, 1):
            self.console.print(f"\n步驟 {i}: {tool_name}")

            result = registry.execute_tool(tool_name, **params)
            results.append(result)

            self.console.print(f"[green]✓ 步驟 {i} 完成[/green]")

        self.console.print(f"\n[bold green]工具鏈 '{self.name}' 執行完成[/bold green]")

        return results


def main():
    """主函數"""
    console = Console()

    console.print(Panel(
        "[bold]SWE-Agent 自定義工具範例[/bold]\n\n"
        "展示如何創建和使用自定義工具",
        border_style="green"
    ))

    # 1. 創建工具註冊表
    console.print("\n[bold cyan]1. 創建工具註冊表[/bold cyan]")
    registry = CustomToolRegistry()

    # 2. 註冊內置工具
    console.print("\n[bold cyan]2. 註冊工具[/bold cyan]")

    file_search = FileSearchTool()
    registry.register(file_search)

    code_grep = CodeGrepTool()
    registry.register(code_grep)

    git_tool = GitOperationTool()
    registry.register(git_tool)

    # 3. 從函數創建工具
    console.print("\n[bold cyan]3. 從函數創建工具[/bold cyan]")

    def calculate_sum(numbers: List[int]) -> int:
        """計算數字總和"""
        return sum(numbers)

    sum_tool = ToolBuilder.from_function(
        calculate_sum,
        name="calculate_sum",
        description="計算數字列表的總和"
    )
    registry.register(sum_tool)

    # 4. 顯示所有工具
    console.print("\n[bold cyan]4. 所有工具[/bold cyan]")
    registry.display_tools()

    # 5. 執行工具
    console.print("\n[bold cyan]5. 執行工具[/bold cyan]")

    # 執行文件搜索
    files = registry.execute_tool("file_search", pattern="*.py", path=".")
    console.print(f"找到 {len(files)} 個 Python 文件")

    # 執行求和
    total = registry.execute_tool("calculate_sum", numbers=[1, 2, 3, 4, 5])
    console.print(f"總和: {total}")

    # 6. 創建工具鏈
    console.print("\n[bold cyan]6. 工具鏈[/bold cyan]")

    chain = ToolChain("分析代碼庫")
    chain.add_step("file_search", {"pattern": "*.py"})
    chain.add_step("git_operation", {"operation": "status"})

    results = chain.execute(registry)


if __name__ == "__main__":
    main()

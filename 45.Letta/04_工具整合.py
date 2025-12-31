"""
Letta 工具整合系統

本模組展示如何為 Letta Agent 集成各種工具和功能：
1. 自定義工具定義
2. 函數調用機制
3. 外部 API 集成
4. 數據庫操作工具
5. 文件系統工具
6. 網絡請求工具

讓 Agent 能夠執行實際的操作，而不僅僅是對話。

作者：Letta 框架示例
日期：2025-01
"""

import os
import json
import time
import requests
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import inspect


@dataclass
class ToolDefinition:
    """工具定義"""
    name: str
    description: str
    parameters: Dict[str, Any]
    function: Callable
    category: str = "general"
    requires_confirmation: bool = False
    is_async: bool = False


@dataclass
class ToolExecutionResult:
    """工具執行結果"""
    tool_name: str
    success: bool
    result: Any
    error: Optional[str] = None
    execution_time: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class BaseTool(ABC):
    """
    工具基類

    所有自定義工具都應該繼承這個類。
    """

    def __init__(self, name: str, description: str):
        """
        初始化工具

        參數:
            name: 工具名稱
            description: 工具描述
        """
        self.name = name
        self.description = description

    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """
        執行工具

        參數:
            **kwargs: 工具參數

        返回:
            執行結果
        """
        pass

    def get_parameters_schema(self) -> Dict[str, Any]:
        """
        獲取參數模式

        返回:
            JSON Schema 格式的參數定義
        """
        # 使用 inspect 自動生成參數模式
        sig = inspect.signature(self.execute)
        parameters = {}

        for param_name, param in sig.parameters.items():
            if param_name == 'kwargs':
                continue

            param_type = "string"  # 默認類型
            if param.annotation != inspect.Parameter.empty:
                if param.annotation == int:
                    param_type = "integer"
                elif param.annotation == float:
                    param_type = "number"
                elif param.annotation == bool:
                    param_type = "boolean"

            parameters[param_name] = {
                "type": param_type,
                "description": f"參數 {param_name}"
            }

        return parameters


class SearchTool(BaseTool):
    """
    網絡搜索工具

    允許 Agent 搜索網絡信息。
    """

    def __init__(self):
        super().__init__(
            name="search_web",
            description="在網絡上搜索信息"
        )

    def execute(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """
        執行搜索

        參數:
            query: 搜索查詢
            num_results: 結果數量

        返回:
            搜索結果
        """
        print(f"\n[搜索工具] 搜索: '{query}'")

        # 模擬搜索結果
        # 在實際應用中，這裡會調用真實的搜索 API
        results = [
            {
                "title": f"搜索結果 {i+1} - {query}",
                "url": f"https://example.com/result{i+1}",
                "snippet": f"這是關於 {query} 的相關內容..."
            }
            for i in range(num_results)
        ]

        print(f"✓ 找到 {len(results)} 個結果")

        return {
            "query": query,
            "results": results,
            "count": len(results)
        }


class CalculatorTool(BaseTool):
    """
    計算器工具

    執行數學計算。
    """

    def __init__(self):
        super().__init__(
            name="calculator",
            description="執行數學計算"
        )

    def execute(self, expression: str) -> Dict[str, Any]:
        """
        執行計算

        參數:
            expression: 數學表達式

        返回:
            計算結果
        """
        print(f"\n[計算器] 計算: {expression}")

        try:
            # 安全的計算（只允許基本運算）
            # 在生產環境中應該使用更安全的方法
            allowed_chars = set("0123456789+-*/.()")
            if not all(c in allowed_chars or c.isspace() for c in expression):
                raise ValueError("表達式包含不允許的字符")

            result = eval(expression, {"__builtins__": {}}, {})
            print(f"✓ 結果: {result}")

            return {
                "expression": expression,
                "result": result,
                "success": True
            }

        except Exception as e:
            print(f"✗ 錯誤: {str(e)}")
            return {
                "expression": expression,
                "result": None,
                "success": False,
                "error": str(e)
            }


class WeatherTool(BaseTool):
    """
    天氣查詢工具

    查詢天氣信息。
    """

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(
            name="get_weather",
            description="查詢指定城市的天氣信息"
        )
        self.api_key = api_key

    def execute(self, city: str, units: str = "metric") -> Dict[str, Any]:
        """
        查詢天氣

        參數:
            city: 城市名稱
            units: 單位（metric/imperial）

        返回:
            天氣信息
        """
        print(f"\n[天氣工具] 查詢城市: {city}")

        # 模擬天氣數據
        # 在實際應用中，這裡會調用天氣 API
        weather_data = {
            "city": city,
            "temperature": 22,
            "description": "晴天",
            "humidity": 65,
            "wind_speed": 15,
            "units": units
        }

        print(f"✓ {city} 的天氣: {weather_data['temperature']}°C, {weather_data['description']}")

        return weather_data


class DatabaseTool(BaseTool):
    """
    數據庫操作工具

    執行數據庫查詢和操作。
    """

    def __init__(self, connection_string: str = "sqlite:///:memory:"):
        super().__init__(
            name="database_query",
            description="執行數據庫查詢"
        )
        self.connection_string = connection_string

    def execute(self, query: str, params: Optional[List] = None) -> Dict[str, Any]:
        """
        執行查詢

        參數:
            query: SQL 查詢
            params: 查詢參數

        返回:
            查詢結果
        """
        print(f"\n[數據庫工具] 執行查詢: {query}")

        # 模擬數據庫查詢
        # 在實際應用中，這裡會執行真實的數據庫操作
        results = [
            {"id": 1, "name": "項目 A", "status": "進行中"},
            {"id": 2, "name": "項目 B", "status": "已完成"}
        ]

        print(f"✓ 返回 {len(results)} 條記錄")

        return {
            "query": query,
            "results": results,
            "row_count": len(results)
        }


class FileSystemTool(BaseTool):
    """
    文件系統工具

    讀寫文件和目錄操作。
    """

    def __init__(self, base_path: str = "./"):
        super().__init__(
            name="file_operations",
            description="執行文件系統操作"
        )
        self.base_path = base_path

    def execute(self, operation: str, path: str, content: Optional[str] = None) -> Dict[str, Any]:
        """
        執行文件操作

        參數:
            operation: 操作類型（read/write/list）
            path: 文件路徑
            content: 寫入的內容（可選）

        返回:
            操作結果
        """
        print(f"\n[文件系統工具] 操作: {operation} on {path}")

        if operation == "read":
            # 模擬讀取文件
            return {
                "operation": "read",
                "path": path,
                "content": "模擬的文件內容",
                "success": True
            }

        elif operation == "write":
            # 模擬寫入文件
            return {
                "operation": "write",
                "path": path,
                "bytes_written": len(content) if content else 0,
                "success": True
            }

        elif operation == "list":
            # 模擬列出目錄
            return {
                "operation": "list",
                "path": path,
                "files": ["file1.txt", "file2.py", "folder1/"],
                "success": True
            }

        else:
            return {
                "operation": operation,
                "success": False,
                "error": f"不支持的操作: {operation}"
            }


class EmailTool(BaseTool):
    """
    郵件發送工具

    發送電子郵件。
    """

    def __init__(self, smtp_config: Optional[Dict] = None):
        super().__init__(
            name="send_email",
            description="發送電子郵件"
        )
        self.smtp_config = smtp_config or {}

    def execute(self, to: str, subject: str, body: str,
               attachments: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        發送郵件

        參數:
            to: 收件人
            subject: 主題
            body: 郵件內容
            attachments: 附件列表

        返回:
            發送結果
        """
        print(f"\n[郵件工具] 發送郵件到: {to}")
        print(f"  主題: {subject}")

        # 模擬發送郵件
        return {
            "to": to,
            "subject": subject,
            "body": body,
            "attachments": attachments or [],
            "sent": True,
            "message_id": f"msg_{int(time.time())}"
        }


class ToolRegistry:
    """
    工具註冊表

    管理所有可用的工具。
    """

    def __init__(self):
        """初始化工具註冊表"""
        self.tools: Dict[str, BaseTool] = {}
        self.execution_history: List[ToolExecutionResult] = []

        print("工具註冊表初始化完成")

    def register_tool(self, tool: BaseTool) -> None:
        """
        註冊工具

        參數:
            tool: 工具實例
        """
        self.tools[tool.name] = tool
        print(f"[註冊工具] {tool.name}: {tool.description}")

    def unregister_tool(self, tool_name: str) -> None:
        """
        取消註冊工具

        參數:
            tool_name: 工具名稱
        """
        if tool_name in self.tools:
            del self.tools[tool_name]
            print(f"[取消註冊] {tool_name}")

    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """
        獲取工具

        參數:
            tool_name: 工具名稱

        返回:
            工具實例
        """
        return self.tools.get(tool_name)

    def list_tools(self) -> List[Dict[str, str]]:
        """
        列出所有工具

        返回:
            工具信息列表
        """
        tools_info = [
            {
                "name": tool.name,
                "description": tool.description
            }
            for tool in self.tools.values()
        ]

        print(f"\n[可用工具] 共 {len(tools_info)} 個:")
        for info in tools_info:
            print(f"  - {info['name']}: {info['description']}")

        return tools_info

    def execute_tool(self, tool_name: str, **kwargs) -> ToolExecutionResult:
        """
        執行工具

        參數:
            tool_name: 工具名稱
            **kwargs: 工具參數

        返回:
            執行結果
        """
        start_time = time.time()

        if tool_name not in self.tools:
            result = ToolExecutionResult(
                tool_name=tool_name,
                success=False,
                result=None,
                error=f"工具 '{tool_name}' 不存在"
            )
            self.execution_history.append(result)
            return result

        tool = self.tools[tool_name]

        try:
            result_data = tool.execute(**kwargs)
            execution_time = time.time() - start_time

            result = ToolExecutionResult(
                tool_name=tool_name,
                success=True,
                result=result_data,
                execution_time=execution_time
            )

            print(f"\n✓ 工具執行成功 (耗時: {execution_time:.3f}s)")

        except Exception as e:
            execution_time = time.time() - start_time

            result = ToolExecutionResult(
                tool_name=tool_name,
                success=False,
                result=None,
                error=str(e),
                execution_time=execution_time
            )

            print(f"\n✗ 工具執行失敗: {str(e)}")

        self.execution_history.append(result)
        return result

    def get_execution_history(self, limit: Optional[int] = None) -> List[ToolExecutionResult]:
        """
        獲取執行歷史

        參數:
            limit: 限制返回數量

        返回:
            執行歷史列表
        """
        history = self.execution_history[-limit:] if limit else self.execution_history

        print(f"\n[執行歷史] 最近 {len(history)} 次執行:")
        for h in history:
            status = "✓" if h.success else "✗"
            print(f"  {status} {h.tool_name} - {h.timestamp}")

        return history

    def get_statistics(self) -> Dict[str, Any]:
        """
        獲取統計信息

        返回:
            統計數據
        """
        total_executions = len(self.execution_history)
        successful_executions = sum(1 for h in self.execution_history if h.success)
        failed_executions = total_executions - successful_executions

        tool_usage = {}
        for h in self.execution_history:
            tool_usage[h.tool_name] = tool_usage.get(h.tool_name, 0) + 1

        stats = {
            "total_executions": total_executions,
            "successful": successful_executions,
            "failed": failed_executions,
            "success_rate": successful_executions / total_executions if total_executions > 0 else 0,
            "tool_usage": tool_usage
        }

        print(f"\n[統計信息]")
        print(f"  總執行次數: {stats['total_executions']}")
        print(f"  成功: {stats['successful']}, 失敗: {stats['failed']}")
        print(f"  成功率: {stats['success_rate']:.1%}")
        print(f"  工具使用統計: {stats['tool_usage']}")

        return stats


class ToolEnabledAgent:
    """
    帶工具能力的 Agent

    這個 Agent 可以調用註冊的工具來完成任務。
    """

    def __init__(self, agent_id: str, tool_registry: ToolRegistry):
        """
        初始化 Agent

        參數:
            agent_id: Agent ID
            tool_registry: 工具註冊表
        """
        self.agent_id = agent_id
        self.tool_registry = tool_registry
        self.conversation_history = []

        print(f"\n[Agent 初始化] ID: {agent_id}")
        print(f"可用工具: {len(tool_registry.tools)} 個")

    def process_message(self, message: str) -> str:
        """
        處理用戶消息

        參數:
            message: 用戶消息

        返回:
            Agent 響應
        """
        print(f"\n[用戶] {message}")

        # 記錄對話
        self.conversation_history.append({
            "role": "user",
            "content": message
        })

        # 分析消息，決定是否需要使用工具
        response = self._analyze_and_respond(message)

        # 記錄響應
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })

        print(f"[Agent] {response}")

        return response

    def _analyze_and_respond(self, message: str) -> str:
        """分析消息並生成響應"""
        message_lower = message.lower()

        # 簡單的關鍵詞匹配來決定使用哪個工具
        if "搜索" in message or "查找" in message:
            # 提取搜索查詢
            query = message.replace("搜索", "").replace("查找", "").strip()
            result = self.tool_registry.execute_tool("search_web", query=query)
            if result.success:
                return f"我為您搜索了 '{query}'，找到了 {result.result['count']} 個相關結果。"

        elif "計算" in message or "等於" in message:
            # 提取表達式
            for word in ["計算", "等於", "是"]:
                message = message.replace(word, "")
            expression = message.strip()
            result = self.tool_registry.execute_tool("calculator", expression=expression)
            if result.success and result.result['success']:
                return f"計算結果：{expression} = {result.result['result']}"

        elif "天氣" in message:
            # 提取城市名
            words = message.split()
            city = "台北"  # 默認城市
            for word in words:
                if word not in ["查詢", "天氣", "的"]:
                    city = word
                    break
            result = self.tool_registry.execute_tool("get_weather", city=city)
            if result.success:
                w = result.result
                return f"{w['city']}的天氣：{w['temperature']}°C，{w['description']}"

        elif "發送郵件" in message or "郵件" in message:
            result = self.tool_registry.execute_tool(
                "send_email",
                to="user@example.com",
                subject="來自 Agent 的郵件",
                body=message
            )
            if result.success:
                return "郵件已發送成功！"

        # 默認響應
        return "我理解了。我有以下工具可以幫助您：搜索、計算、查詢天氣、發送郵件等。"


def demonstrate_basic_tools():
    """演示基本工具使用"""
    print("\n" + "=" * 60)
    print("基本工具演示")
    print("=" * 60)

    registry = ToolRegistry()

    # 註冊工具
    registry.register_tool(SearchTool())
    registry.register_tool(CalculatorTool())
    registry.register_tool(WeatherTool())

    # 列出工具
    registry.list_tools()

    # 執行工具
    registry.execute_tool("search_web", query="Python 教程", num_results=3)
    registry.execute_tool("calculator", expression="100 * 25 + 50")
    registry.execute_tool("get_weather", city="台北")

    # 查看歷史
    registry.get_execution_history()


def demonstrate_advanced_tools():
    """演示高級工具"""
    print("\n" + "=" * 60)
    print("高級工具演示")
    print("=" * 60)

    registry = ToolRegistry()

    # 註冊高級工具
    registry.register_tool(DatabaseTool())
    registry.register_tool(FileSystemTool())
    registry.register_tool(EmailTool())

    # 執行工具
    registry.execute_tool(
        "database_query",
        query="SELECT * FROM projects WHERE status = 'active'"
    )

    registry.execute_tool(
        "file_operations",
        operation="list",
        path="./documents"
    )

    registry.execute_tool(
        "send_email",
        to="manager@company.com",
        subject="項目進度報告",
        body="本週項目進展順利。"
    )

    # 統計信息
    registry.get_statistics()


def demonstrate_tool_enabled_agent():
    """演示帶工具的 Agent"""
    print("\n" + "=" * 60)
    print("工具驅動 Agent 演示")
    print("=" * 60)

    # 創建工具註冊表並註冊工具
    registry = ToolRegistry()
    registry.register_tool(SearchTool())
    registry.register_tool(CalculatorTool())
    registry.register_tool(WeatherTool())
    registry.register_tool(EmailTool())

    # 創建 Agent
    agent = ToolEnabledAgent("agent_001", registry)

    # 與 Agent 對話
    agent.process_message("搜索 Letta 框架教程")
    time.sleep(1)
    agent.process_message("計算 256 * 1024")
    time.sleep(1)
    agent.process_message("查詢台北的天氣")
    time.sleep(1)
    agent.process_message("幫我發送一封郵件")


def demonstrate_custom_tool():
    """演示自定義工具"""
    print("\n" + "=" * 60)
    print("自定義工具演示")
    print("=" * 60)

    class TranslationTool(BaseTool):
        """翻譯工具"""

        def __init__(self):
            super().__init__(
                name="translate",
                description="翻譯文本"
            )

        def execute(self, text: str, target_lang: str = "en") -> Dict[str, Any]:
            # 模擬翻譯
            translations = {
                "en": "Hello, World!",
                "ja": "こんにちは、世界！",
                "ko": "안녕하세요, 세계!"
            }

            return {
                "original": text,
                "translated": translations.get(target_lang, text),
                "target_language": target_lang
            }

    # 註冊自定義工具
    registry = ToolRegistry()
    registry.register_tool(TranslationTool())

    # 使用自定義工具
    result = registry.execute_tool(
        "translate",
        text="你好，世界！",
        target_lang="en"
    )

    print(f"\n翻譯結果: {result.result}")


def main():
    """主函數：運行所有演示"""
    print("\n" + "=" * 70)
    print(" " * 20 + "Letta 工具整合系統")
    print("=" * 70)

    # 基本工具演示
    demonstrate_basic_tools()

    # 高級工具演示
    demonstrate_advanced_tools()

    # 工具驅動 Agent
    demonstrate_tool_enabled_agent()

    # 自定義工具
    demonstrate_custom_tool()

    print("\n" + "=" * 70)
    print("工具整合演示完成！")
    print("=" * 70)
    print("\n關鍵要點：")
    print("  1. 工具讓 Agent 能夠執行實際操作")
    print("  2. 工具註冊表統一管理所有工具")
    print("  3. 支持自定義工具擴展功能")
    print("  4. 執行歷史幫助追蹤和調試")
    print("  5. Agent 可以智能地選擇合適的工具")
    print("\n下一步：查看 05_知識庫.py")
    print("=" * 70)


if __name__ == "__main__":
    main()

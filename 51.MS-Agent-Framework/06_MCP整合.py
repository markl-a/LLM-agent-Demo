"""
Microsoft Agent Framework - MCP 整合

這個檔案展示如何整合 Model Context Protocol (MCP)。
MCP 是 Anthropic 提出的標準化協議,用於連接 AI 模型和外部工具。

主要內容:
1. MCP 協議介紹
2. MCP 伺服器設定
3. MCP 客戶端整合
4. 標準化工具定義
5. 資源提供者
6. 提示詞模板
7. 安全性考量
8. 實際應用案例

作者: Microsoft Agent Framework Team
日期: 2025-12-31
版本: 1.0.0
"""

import os
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from dotenv import load_dotenv

# Agent Framework 核心模組
from agent_framework import Agent, AgentThread
from agent_framework.models import OpenAIModel

# MCP 相關模組
from agent_framework.mcp import (
    MCPClient,
    MCPServer,
    MCPTool,
    MCPResource,
    MCPPrompt,
)

# ============================================================================
# 1. MCP 協議介紹
# ============================================================================

def explain_mcp_protocol():
    """
    解釋 MCP 協議的概念和優勢

    Model Context Protocol (MCP) 是一個開放標準,
    讓 AI 應用能夠以一致的方式連接到各種資料源和工具。
    """
    print("="*70)
    print("Model Context Protocol (MCP) 介紹")
    print("="*70)

    print("\n📚 MCP 核心概念:")

    concepts = [
        ("1. 標準化介面", "統一的協議定義,所有工具遵循相同規範"),
        ("2. 工具發現", "自動發現和列舉可用的工具和資源"),
        ("3. 類型安全", "強類型定義,確保參數正確性"),
        ("4. 互操作性", "不同系統之間無縫整合"),
        ("5. 可擴展性", "易於添加新的工具和資源"),
    ]

    for title, description in concepts:
        print(f"\n   {title}")
        print(f"      {description}")

    print("\n🎯 MCP 的三大核心組件:")
    print("\n   1. Tools (工具)")
    print("      - 可執行的函數")
    print("      - 有明確的輸入/輸出定義")
    print("      - 例如: 搜尋引擎、計算器、資料庫查詢")

    print("\n   2. Resources (資源)")
    print("      - 可存取的資料源")
    print("      - 結構化或非結構化資料")
    print("      - 例如: 文件、資料庫、API 端點")

    print("\n   3. Prompts (提示詞)")
    print("      - 預定義的提示詞模板")
    print("      - 可參數化")
    print("      - 例如: 常用任務的提示詞")


# ============================================================================
# 2. MCP 工具定義
# ============================================================================

class MCPToolDefinition:
    """
    MCP 工具定義範例

    展示如何按照 MCP 標準定義工具
    """

    @staticmethod
    def define_weather_tool() -> Dict[str, Any]:
        """
        定義天氣查詢工具

        符合 MCP 標準的工具定義包含:
        - name: 工具名稱
        - description: 工具描述
        - inputSchema: JSON Schema 格式的參數定義
        """
        return {
            "name": "get_weather",
            "description": "獲取指定城市的天氣資訊",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名稱,如 '台北' 或 '高雄'"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "default": "celsius",
                        "description": "溫度單位"
                    },
                    "include_forecast": {
                        "type": "boolean",
                        "default": False,
                        "description": "是否包含天氣預報"
                    }
                },
                "required": ["city"]
            }
        }

    @staticmethod
    def define_calculator_tool() -> Dict[str, Any]:
        """定義計算器工具"""
        return {
            "name": "calculate",
            "description": "執行數學計算",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "數學表達式,如 '2 + 3 * 4'"
                    },
                    "precision": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 10,
                        "default": 2,
                        "description": "小數點精度"
                    }
                },
                "required": ["expression"]
            }
        }

    @staticmethod
    def define_database_query_tool() -> Dict[str, Any]:
        """定義資料庫查詢工具"""
        return {
            "name": "query_database",
            "description": "查詢資料庫並返回結果",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "table": {
                        "type": "string",
                        "description": "資料表名稱"
                    },
                    "filters": {
                        "type": "object",
                        "description": "篩選條件"
                    },
                    "limit": {
                        "type": "integer",
                        "default": 10,
                        "description": "返回記錄數上限"
                    }
                },
                "required": ["table"]
            }
        }


# ============================================================================
# 3. MCP 資源定義
# ============================================================================

class MCPResourceDefinition:
    """MCP 資源定義範例"""

    @staticmethod
    def define_document_resource() -> Dict[str, Any]:
        """
        定義文件資源

        資源定義包含:
        - uri: 資源的唯一識別符
        - name: 資源名稱
        - description: 資源描述
        - mimeType: 資料類型
        """
        return {
            "uri": "doc://knowledge-base/ai-agents",
            "name": "AI Agents 知識庫",
            "description": "包含 AI Agent 相關文件和範例",
            "mimeType": "application/json",
            "metadata": {
                "category": "documentation",
                "language": "zh-TW",
                "last_updated": "2025-12-31"
            }
        }

    @staticmethod
    def define_api_resource() -> Dict[str, Any]:
        """定義 API 資源"""
        return {
            "uri": "api://weather-service/v1",
            "name": "天氣服務 API",
            "description": "提供即時天氣資訊",
            "mimeType": "application/json",
            "metadata": {
                "rate_limit": "100/hour",
                "authentication": "api_key"
            }
        }


# ============================================================================
# 4. MCP 伺服器實作
# ============================================================================

class CustomMCPServer:
    """
    自定義 MCP 伺服器

    實作 MCP 協議的伺服器端,提供工具和資源
    """

    def __init__(self, name: str):
        """
        初始化 MCP 伺服器

        Args:
            name: 伺服器名稱
        """
        self.name = name
        self.tools: Dict[str, MCPTool] = {}
        self.resources: Dict[str, MCPResource] = {}
        self.prompts: Dict[str, MCPPrompt] = {}

    def register_tool(
        self,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        handler: callable
    ):
        """
        註冊工具

        Args:
            name: 工具名稱
            description: 工具描述
            input_schema: 輸入參數 schema
            handler: 處理函數
        """
        tool = MCPTool(
            name=name,
            description=description,
            inputSchema=input_schema,
            handler=handler
        )
        self.tools[name] = tool

        print(f"✅ 註冊工具: {name}")

    def register_resource(
        self,
        uri: str,
        name: str,
        description: str,
        provider: callable
    ):
        """
        註冊資源

        Args:
            uri: 資源 URI
            name: 資源名稱
            description: 資源描述
            provider: 資源提供函數
        """
        resource = MCPResource(
            uri=uri,
            name=name,
            description=description,
            provider=provider
        )
        self.resources[uri] = resource

        print(f"✅ 註冊資源: {uri}")

    def register_prompt(
        self,
        name: str,
        description: str,
        template: str,
        arguments: List[Dict[str, Any]]
    ):
        """
        註冊提示詞模板

        Args:
            name: 提示詞名稱
            description: 描述
            template: 模板內容
            arguments: 參數定義
        """
        prompt = MCPPrompt(
            name=name,
            description=description,
            template=template,
            arguments=arguments
        )
        self.prompts[name] = prompt

        print(f"✅ 註冊提示詞: {name}")

    def list_tools(self) -> List[Dict[str, Any]]:
        """列出所有可用工具"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.inputSchema
            }
            for tool in self.tools.values()
        ]

    def list_resources(self) -> List[Dict[str, Any]]:
        """列出所有可用資源"""
        return [
            {
                "uri": resource.uri,
                "name": resource.name,
                "description": resource.description
            }
            for resource in self.resources.values()
        ]

    def execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        執行工具

        Args:
            tool_name: 工具名稱
            arguments: 參數

        Returns:
            執行結果
        """
        if tool_name not in self.tools:
            raise ValueError(f"工具不存在: {tool_name}")

        tool = self.tools[tool_name]

        # 驗證參數 (簡化版)
        # 實際應該使用 JSON Schema 驗證

        # 執行工具
        result = tool.handler(**arguments)

        return {
            "tool": tool_name,
            "result": result,
            "success": True
        }


# ============================================================================
# 5. MCP 客戶端實作
# ============================================================================

class CustomMCPClient:
    """
    自定義 MCP 客戶端

    連接到 MCP 伺服器並使用其提供的工具和資源
    """

    def __init__(self, server_url: str):
        """
        初始化 MCP 客戶端

        Args:
            server_url: MCP 伺服器地址
        """
        self.server_url = server_url
        self.available_tools: List[Dict[str, Any]] = []
        self.available_resources: List[Dict[str, Any]] = []

    def connect(self, server: CustomMCPServer):
        """
        連接到 MCP 伺服器

        Args:
            server: MCP 伺服器實例
        """
        print(f"\n🔌 連接到 MCP 伺服器: {server.name}")

        # 發現工具
        self.available_tools = server.list_tools()
        print(f"   發現 {len(self.available_tools)} 個工具:")
        for tool in self.available_tools:
            print(f"      - {tool['name']}: {tool['description']}")

        # 發現資源
        self.available_resources = server.list_resources()
        print(f"   發現 {len(self.available_resources)} 個資源:")
        for resource in self.available_resources:
            print(f"      - {resource['uri']}: {resource['name']}")

        # 儲存伺服器引用 (用於執行工具)
        self.server = server

    def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Any:
        """
        調用工具

        Args:
            tool_name: 工具名稱
            arguments: 參數

        Returns:
            工具執行結果
        """
        print(f"\n⚙️  調用工具: {tool_name}")
        print(f"   參數: {arguments}")

        result = self.server.execute_tool(tool_name, arguments)

        print(f"   ✅ 執行成功")

        return result["result"]

    def get_resource(self, uri: str) -> Any:
        """
        獲取資源

        Args:
            uri: 資源 URI

        Returns:
            資源內容
        """
        print(f"\n📄 獲取資源: {uri}")

        if uri not in self.server.resources:
            raise ValueError(f"資源不存在: {uri}")

        resource = self.server.resources[uri]
        content = resource.provider()

        print(f"   ✅ 獲取成功")

        return content


# ============================================================================
# 6. 與 Agent Framework 整合
# ============================================================================

def integrate_mcp_with_agent():
    """
    示範如何將 MCP 整合到 Agent Framework
    """
    print("\n" + "="*70)
    print("🎯 MCP 與 Agent Framework 整合")
    print("="*70)

    load_dotenv()
    model = OpenAIModel(
        model=os.getenv("OPENAI_MODEL", "gpt-4"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    # 1. 創建 MCP 伺服器
    mcp_server = CustomMCPServer(name="my_tools_server")

    # 2. 註冊工具
    def weather_handler(city: str, unit: str = "celsius") -> str:
        """天氣查詢處理函數"""
        temp = {"台北": 25, "高雄": 28}.get(city, 22)
        if unit == "fahrenheit":
            temp = temp * 9/5 + 32
        return f"{city}的溫度是 {temp}°{'F' if unit == 'fahrenheit' else 'C'}"

    mcp_server.register_tool(
        name="get_weather",
        description="獲取城市天氣",
        input_schema=MCPToolDefinition.define_weather_tool()["inputSchema"],
        handler=weather_handler
    )

    def calc_handler(expression: str, precision: int = 2) -> float:
        """計算處理函數"""
        try:
            result = eval(expression, {"__builtins__": {}}, {})
            return round(result, precision)
        except Exception as e:
            return f"計算錯誤: {str(e)}"

    mcp_server.register_tool(
        name="calculate",
        description="執行數學計算",
        input_schema=MCPToolDefinition.define_calculator_tool()["inputSchema"],
        handler=calc_handler
    )

    # 3. 創建 MCP 客戶端並連接
    mcp_client = CustomMCPClient(server_url="localhost:8000")
    mcp_client.connect(mcp_server)

    # 4. 創建使用 MCP 工具的 Agent
    agent = Agent(
        name="mcp_agent",
        model=model,
        instructions="""
        你是一個整合了 MCP 工具的助手。
        你可以使用以下工具:
        - get_weather: 查詢天氣
        - calculate: 數學計算

        適時使用這些工具來回答問題。
        """,
        tools=[
            lambda city, unit="celsius": mcp_client.call_tool(
                "get_weather",
                {"city": city, "unit": unit}
            ),
            lambda expression, precision=2: mcp_client.call_tool(
                "calculate",
                {"expression": expression, "precision": precision}
            ),
        ]
    )

    # 5. 測試整合
    thread = AgentThread()

    test_queries = [
        "台北今天天氣如何?",
        "幫我計算 15 * 23 + 100",
    ]

    for query in test_queries:
        print(f"\n👤 用戶: {query}")
        # response = agent.run(thread=thread, messages=query)
        # print(f"🤖 助手: {response.content}")

        # 直接測試 MCP 調用
        if "天氣" in query:
            result = mcp_client.call_tool("get_weather", {"city": "台北"})
            print(f"🤖 助手: {result}")
        elif "計算" in query:
            result = mcp_client.call_tool("calculate", {"expression": "15 * 23 + 100"})
            print(f"🤖 助手: 計算結果是 {result}")


# ============================================================================
# 7. 實際應用案例: 企業資料存取
# ============================================================================

def demonstrate_enterprise_mcp_integration():
    """
    示範企業級 MCP 整合

    連接到企業內部系統和資料源
    """
    print("\n" + "="*70)
    print("🎯 企業級 MCP 整合案例")
    print("="*70)

    # 創建企業 MCP 伺服器
    enterprise_server = CustomMCPServer(name="enterprise_data_server")

    # 註冊企業資料庫工具
    def query_crm(customer_id: str) -> Dict[str, Any]:
        """查詢 CRM 系統"""
        # 模擬資料庫查詢
        return {
            "customer_id": customer_id,
            "name": "測試公司",
            "industry": "科技",
            "status": "活躍"
        }

    enterprise_server.register_tool(
        name="query_crm",
        description="查詢 CRM 客戶資料",
        input_schema={
            "type": "object",
            "properties": {
                "customer_id": {"type": "string"}
            },
            "required": ["customer_id"]
        },
        handler=query_crm
    )

    # 註冊文件資源
    def provide_policy_document() -> str:
        """提供政策文件"""
        return "企業政策文件內容..."

    enterprise_server.register_resource(
        uri="doc://policies/privacy",
        name="隱私政策",
        description="公司隱私政策文件",
        provider=provide_policy_document
    )

    # 註冊提示詞模板
    enterprise_server.register_prompt(
        name="customer_analysis",
        description="客戶分析提示詞",
        template="分析以下客戶資料並提供洞察:\n{customer_data}",
        arguments=[
            {
                "name": "customer_data",
                "description": "客戶資料 JSON",
                "type": "string"
            }
        ]
    )

    print("\n✅ 企業 MCP 伺服器設定完成")
    print(f"   工具數: {len(enterprise_server.tools)}")
    print(f"   資源數: {len(enterprise_server.resources)}")
    print(f"   提示詞數: {len(enterprise_server.prompts)}")


# ============================================================================
# 8. 安全性考量
# ============================================================================

def discuss_mcp_security():
    """討論 MCP 整合的安全性考量"""
    print("\n" + "="*70)
    print("🔒 MCP 安全性考量")
    print("="*70)

    security_topics = [
        ("1. 認證和授權", [
            "使用 API 金鑰或 OAuth 認證",
            "實施細粒度的權限控制",
            "定期輪換憑證"
        ]),
        ("2. 輸入驗證", [
            "嚴格驗證所有輸入參數",
            "使用 JSON Schema 強制類型檢查",
            "防止 SQL 注入和命令注入"
        ]),
        ("3. 速率限制", [
            "實施 API 調用速率限制",
            "防止濫用和 DoS 攻擊",
            "監控異常使用模式"
        ]),
        ("4. 資料隱私", [
            "加密傳輸中的敏感資料",
            "遵循最小權限原則",
            "記錄所有資料存取操作"
        ]),
        ("5. 錯誤處理", [
            "不洩漏系統內部資訊",
            "提供通用的錯誤訊息",
            "記錄詳細錯誤以供審計"
        ]),
    ]

    for topic, points in security_topics:
        print(f"\n   {topic}")
        for point in points:
            print(f"      - {point}")


# ============================================================================
# 9. 主程式
# ============================================================================

def main():
    """主程式"""
    print("="*70)
    print("Microsoft Agent Framework - MCP 整合")
    print("="*70)

    # 1. 解釋 MCP 協議
    explain_mcp_protocol()

    # 2. 示範工具定義
    print("\n" + "="*70)
    print("🎯 MCP 工具定義範例")
    print("="*70)

    weather_tool = MCPToolDefinition.define_weather_tool()
    print(f"\n✅ 天氣工具定義:")
    print(f"   名稱: {weather_tool['name']}")
    print(f"   描述: {weather_tool['description']}")
    print(f"   參數: {list(weather_tool['inputSchema']['properties'].keys())}")

    # 3. 整合示範
    integrate_mcp_with_agent()

    # 4. 企業案例
    demonstrate_enterprise_mcp_integration()

    # 5. 安全性討論
    discuss_mcp_security()

    print("\n" + "="*70)
    print("✅ MCP 整合示範完成!")
    print("="*70)

    print("\n💡 關鍵要點:")
    print("   1. MCP 提供標準化的工具整合介面")
    print("   2. 支援工具、資源、提示詞三種類型")
    print("   3. 強類型定義確保安全性")
    print("   4. 易於擴展和維護")
    print("   5. 適合企業級系統整合")

    print("\n📚 下一步:")
    print("   查看 07_Azure部署.py 學習 Azure 部署")


if __name__ == "__main__":
    main()

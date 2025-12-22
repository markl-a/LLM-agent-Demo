"""
Model Context Protocol (MCP) 概述
====================================

本模組介紹 MCP 協議的核心概念、設計理念和架構組成。

MCP 是什麼？
-----------
Model Context Protocol (MCP) 是由 Anthropic 開發的開放標準協議，
旨在標準化大型語言模型 (LLM) 與外部工具、數據源之間的連接方式。

核心理念：
- 🔌 就像 USB-C 統一了設備充電接口
- 🌐 MCP 統一了 AI 應用與工具的互操作方式
- 🤝 一次編寫，多處使用 (Write Once, Use Everywhere)

作者：Claude (Anthropic)
日期：2025-12-22
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum


# ============================================================================
# 第一部分：MCP 架構組件
# ============================================================================

class MCPRole(Enum):
    """MCP 通信中的角色定義"""
    CLIENT = "client"  # 客戶端（主機應用，如 Claude Desktop）
    SERVER = "server"  # 服務器（工具提供者）


@dataclass
class MCPCapability:
    """MCP 能力定義"""
    name: str
    description: str
    enabled: bool = True


class MCPArchitecture:
    """
    MCP 架構示意

    架構圖：
    ┌─────────────────────────────────────────────────┐
    │              MCP 生態系統                        │
    ├─────────────────────────────────────────────────┤
    │                                                  │
    │  ┌──────────────┐         ┌──────────────┐     │
    │  │  MCP Client  │ ◄─────► │  MCP Server  │     │
    │  │   (主機)     │   MCP   │   (工具)     │     │
    │  │              │ Protocol│              │     │
    │  └──────────────┘         └──────────────┘     │
    │         │                         │             │
    │         ▼                         ▼             │
    │  ┌──────────────┐         ┌──────────────┐     │
    │  │ LLM 提供商   │         │   工具實現    │     │
    │  │ - Claude     │         │ - 文件系統    │     │
    │  │ - GPT-4      │         │ - 數據庫      │     │
    │  │ - Gemini     │         │ - API 整合    │     │
    │  └──────────────┘         └──────────────┘     │
    │                                                  │
    └─────────────────────────────────────────────────┘
    """

    def __init__(self):
        self.components = {
            "client": "負責發起請求和接收響應的主機應用",
            "server": "提供工具、資源和提示的服務端",
            "protocol": "基於 JSON-RPC 2.0 的通信協議",
            "transport": "支持 stdio、HTTP/SSE、WebSocket"
        }

    def describe_flow(self) -> str:
        """描述 MCP 通信流程"""
        return """
        MCP 通信流程：

        1. 初始化階段
           Client → Server: 發送初始化請求 (initialize)
           Server → Client: 返回服務器能力 (capabilities)

        2. 能力協商
           - 客戶端和服務器交換支持的功能
           - 建立通信參數（版本、編碼等）

        3. 操作階段
           Client → Server: 調用工具 (tools/call)
           Client → Server: 請求資源 (resources/read)
           Client → Server: 獲取提示 (prompts/get)

        4. 響應處理
           Server → Client: 返回執行結果
           Server → Client: 可選的進度更新

        5. 清理階段
           - 關閉連接
           - 釋放資源
        """


# ============================================================================
# 第二部分：MCP 三大核心功能
# ============================================================================

class MCPTools:
    """
    工具 (Tools)

    MCP 服務器可以向客戶端公開可調用的工具。
    工具是 LLM 可以執行特定任務的函數。
    """

    @staticmethod
    def example_tool_definition() -> Dict[str, Any]:
        """工具定義示例"""
        return {
            "name": "read_file",
            "description": "讀取指定路徑的文件內容",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "文件的絕對或相對路徑"
                    },
                    "encoding": {
                        "type": "string",
                        "enum": ["utf-8", "ascii", "latin-1"],
                        "default": "utf-8",
                        "description": "文件編碼格式"
                    }
                },
                "required": ["path"]
            }
        }

    @staticmethod
    def tool_categories() -> List[str]:
        """常見的工具類別"""
        return [
            "文件操作 (read, write, delete)",
            "數據查詢 (SQL, NoSQL)",
            "API 調用 (REST, GraphQL)",
            "代碼執行 (Python, JavaScript)",
            "系統命令 (shell, git)",
            "數據轉換 (JSON, XML, CSV)"
        ]


class MCPResources:
    """
    資源 (Resources)

    服務器可以提供結構化的數據資源，供客戶端訪問。
    資源使用 URI 標識，支持文件、數據庫記錄、API 端點等。
    """

    @staticmethod
    def example_resource_definition() -> Dict[str, Any]:
        """資源定義示例"""
        return {
            "uri": "file:///project/README.md",
            "name": "專案說明文件",
            "description": "包含專案的詳細說明和使用指南",
            "mimeType": "text/markdown",
            "metadata": {
                "size": 4096,
                "lastModified": "2025-12-22T10:00:00Z",
                "author": "開發團隊"
            }
        }

    @staticmethod
    def resource_uri_schemes() -> Dict[str, str]:
        """支持的 URI 方案"""
        return {
            "file://": "本地文件系統",
            "http://": "HTTP 資源",
            "https://": "安全 HTTP 資源",
            "db://": "數據庫連接",
            "s3://": "AWS S3 對象",
            "custom://": "自定義方案"
        }


class MCPPrompts:
    """
    提示模板 (Prompts)

    預定義的提示模板，包含參數化的指令。
    允許服務器提供專業領域的提示詞。
    """

    @staticmethod
    def example_prompt_definition() -> Dict[str, Any]:
        """提示模板定義示例"""
        return {
            "name": "code_review",
            "description": "代碼審查提示模板",
            "arguments": [
                {
                    "name": "language",
                    "description": "程式語言",
                    "required": True
                },
                {
                    "name": "focus",
                    "description": "審查重點",
                    "required": False,
                    "default": "all"
                }
            ],
            "template": """
            請審查以下 {language} 代碼：

            審查重點：{focus}

            請檢查：
            1. 代碼質量和可讀性
            2. 潛在的 bug 和安全問題
            3. 性能優化機會
            4. 最佳實踐遵循情況
            """
        }


# ============================================================================
# 第三部分：MCP vs 傳統方案對比
# ============================================================================

class ComparisonAnalysis:
    """MCP 與傳統方案的對比分析"""

    @staticmethod
    def traditional_approach() -> Dict[str, List[str]]:
        """傳統方案的問題"""
        return {
            "問題": [
                "每個 LLM 提供商需要自己的適配器",
                "工具開發者需要支持多個 API 格式",
                "缺乏統一的安全和權限模型",
                "重複的整合代碼和維護成本",
                "難以在不同應用間共享工具"
            ],
            "限制": [
                "供應商鎖定 (Vendor Lock-in)",
                "可擴展性差",
                "互操作性低",
                "開發效率低"
            ]
        }

    @staticmethod
    def mcp_advantages() -> Dict[str, List[str]]:
        """MCP 的優勢"""
        return {
            "標準化": [
                "統一的協議規範",
                "一致的工具定義格式",
                "標準化的錯誤處理"
            ],
            "互操作性": [
                "跨 LLM 提供商使用",
                "工具可在多個應用間共享",
                "生態系統快速增長"
            ],
            "開發效率": [
                "編寫一次，到處使用",
                "豐富的官方和社區工具庫",
                "完善的 SDK 和文檔"
            ],
            "性能優化": [
                "Code Execution 減少 98.7% Token",
                "降低成本和延遲",
                "更精確的工具執行"
            ]
        }


# ============================================================================
# 第四部分：MCP 生態系統
# ============================================================================

class MCPEcosystem:
    """MCP 生態系統概覽"""

    def __init__(self):
        self.supporters = {
            "LLM 提供商": ["Anthropic", "OpenAI", "Google", "Microsoft", "AWS"],
            "開發工具": ["Sourcegraph Cody", "Zed", "Replit", "Cursor"],
            "基礎設施": ["Linux Foundation", "Agentic AI Foundation"]
        }

        self.statistics = {
            "月下載量": "97M+",
            "官方服務器": "50+",
            "社區服務器": "100+",
            "支持語言": ["Python", "TypeScript", "Rust", "Go"]
        }

    def get_popular_servers(self) -> Dict[str, List[str]]:
        """獲取熱門 MCP 服務器"""
        return {
            "開發工具": [
                "@modelcontextprotocol/server-filesystem",
                "@modelcontextprotocol/server-git",
                "@modelcontextprotocol/server-github"
            ],
            "數據庫": [
                "@modelcontextprotocol/server-postgres",
                "@modelcontextprotocol/server-sqlite",
                "@modelcontextprotocol/server-mongodb"
            ],
            "生產力": [
                "@modelcontextprotocol/server-google-drive",
                "@modelcontextprotocol/server-slack",
                "@modelcontextprotocol/server-notion"
            ],
            "自動化": [
                "@modelcontextprotocol/server-puppeteer",
                "@modelcontextprotocol/server-selenium"
            ]
        }


# ============================================================================
# 第五部分：實際應用場景
# ============================================================================

class UseCases:
    """MCP 的實際應用場景"""

    @staticmethod
    def enterprise_scenarios() -> List[Dict[str, str]]:
        """企業級應用場景"""
        return [
            {
                "場景": "智能客服系統",
                "描述": "LLM 通過 MCP 訪問客戶數據庫、訂單系統、知識庫",
                "價值": "提供個性化、準確的客戶支持"
            },
            {
                "場景": "代碼助手",
                "描述": "IDE 中的 AI 助手通過 MCP 訪問 Git、CI/CD、文檔",
                "價值": "提高開發效率，自動化重複任務"
            },
            {
                "場景": "數據分析助手",
                "描述": "LLM 通過 MCP 連接數據倉庫、BI 工具、報表系統",
                "價值": "自然語言查詢和分析數據"
            },
            {
                "場景": "運維自動化",
                "描述": "AI 運維助手通過 MCP 管理基礎設施、監控系統",
                "價值": "智能告警、自動修復、容量規劃"
            }
        ]

    @staticmethod
    def developer_scenarios() -> List[Dict[str, str]]:
        """開發者應用場景"""
        return [
            {
                "場景": "個人知識管理",
                "描述": "AI 助手通過 MCP 訪問筆記、文檔、書籤",
                "價值": "智能檢索和總結個人知識庫"
            },
            {
                "場景": "自動化測試",
                "描述": "LLM 通過 MCP 執行測試、生成測試用例",
                "價值": "提高測試覆蓋率和質量"
            },
            {
                "場景": "文檔生成",
                "描述": "AI 通過 MCP 分析代碼庫，生成文檔",
                "價值": "保持文檔與代碼同步"
            }
        ]


# ============================================================================
# 主程式示例
# ============================================================================

def main():
    """主程式：展示 MCP 概念"""

    print("=" * 70)
    print("Model Context Protocol (MCP) 概述")
    print("=" * 70)

    # 1. 展示架構
    print("\n【MCP 架構】")
    arch = MCPArchitecture()
    for component, desc in arch.components.items():
        print(f"  • {component}: {desc}")

    # 2. 核心功能示例
    print("\n【核心功能】")
    print("  1. Tools (工具)")
    tool = MCPTools.example_tool_definition()
    print(f"     示例工具: {tool['name']} - {tool['description']}")

    print("\n  2. Resources (資源)")
    resource = MCPResources.example_resource_definition()
    print(f"     示例資源: {resource['uri']}")

    print("\n  3. Prompts (提示)")
    prompt = MCPPrompts.example_prompt_definition()
    print(f"     示例提示: {prompt['name']} - {prompt['description']}")

    # 3. 優勢對比
    print("\n【MCP 優勢】")
    advantages = ComparisonAnalysis.mcp_advantages()
    for category, items in advantages.items():
        print(f"  {category}:")
        for item in items:
            print(f"    ✓ {item}")

    # 4. 生態系統
    print("\n【生態系統】")
    ecosystem = MCPEcosystem()
    print(f"  • 月下載量: {ecosystem.statistics['月下載量']}")
    print(f"  • 官方服務器: {ecosystem.statistics['官方服務器']}")
    print(f"  • 社區服務器: {ecosystem.statistics['社區服務器']}")

    # 5. 應用場景
    print("\n【應用場景】")
    use_cases = UseCases()
    scenarios = use_cases.enterprise_scenarios()[:2]
    for scenario in scenarios:
        print(f"  • {scenario['場景']}")
        print(f"    {scenario['描述']}")

    print("\n" + "=" * 70)
    print("下一步：查看 02_安裝配置.py 學習如何安裝 MCP SDK")
    print("=" * 70)


if __name__ == "__main__":
    main()

"""
Claude Code SDK MCP 整合示例

本示例展示：
1. Model Context Protocol (MCP) 介紹
2. MCP 服務器連接
3. MCP 工具使用
4. 自定義 MCP 服務器
"""

import os
import json
from typing import List, Dict, Any
from anthropic import Anthropic
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
from dotenv import load_dotenv

console = Console()
load_dotenv()


def explain_mcp():
    """解釋 MCP 協議"""
    console.print("\n[bold cyan]什麼是 MCP (Model Context Protocol)?[/bold cyan]\n")

    explanation = """
MCP 是 Anthropic 推出的開放協議，用於標準化 AI 模型與外部工具、數據源的連接。

核心概念：
• 服務器：提供工具和資源的服務
• 客戶端：連接到服務器的 AI 應用
• 工具：服務器提供的功能
• 資源：服務器提供的數據源
• 提示詞：預定義的提示詞模板

優勢：
✓ 標準化的接口
✓ 可重用的組件
✓ 豐富的生態系統
✓ 簡化整合流程
"""

    console.print(Panel(explanation, border_style="cyan"))
    console.print()


def show_mcp_architecture():
    """展示 MCP 架構"""
    console.print("[bold cyan]MCP 架構[/bold cyan]\n")

    tree = Tree("[bold cyan]MCP 生態系統")

    # Claude 應用
    claude = tree.add("[yellow]Claude 應用")
    claude.add("🤖 Claude Agent")
    claude.add("💬 對話管理")

    # MCP 客戶端
    client = tree.add("[green]MCP 客戶端")
    client.add("📡 連接管理")
    client.add("🔄 協議轉換")

    # MCP 服務器
    servers = tree.add("[blue]MCP 服務器")

    # 服務器類型
    official = servers.add("官方服務器")
    official.add("📂 文件系統服務器")
    official.add("🗄️  數據庫服務器")
    official.add("🌐 Web 搜索服務器")

    community = servers.add("社區服務器")
    community.add("📧 郵件服務器")
    community.add("📅 日曆服務器")
    community.add("🔔 通知服務器")

    custom = servers.add("自定義服務器")
    custom.add("💼 企業系統整合")
    custom.add("🛠️  專用工具")

    console.print(tree)
    console.print()


def demo_mcp_tools():
    """MCP 工具示例"""
    console.print("[bold cyan]1. MCP 工具使用[/bold cyan]\n")

    # 模擬 MCP 工具定義
    mcp_tools = [
        {
            "name": "filesystem_read",
            "description": "讀取文件系統中的文件",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "文件路徑"}
                },
                "required": ["path"]
            }
        },
        {
            "name": "filesystem_write",
            "description": "寫入文件到文件系統",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "文件路徑"},
                    "content": {"type": "string", "description": "文件內容"}
                },
                "required": ["path", "content"]
            }
        },
        {
            "name": "database_query",
            "description": "查詢數據庫",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "SQL 查詢"}
                },
                "required": ["query"]
            }
        }
    ]

    table = Table(title="MCP 工具示例")
    table.add_column("工具名稱", style="cyan")
    table.add_column("描述", style="green")

    for tool in mcp_tools:
        table.add_row(tool["name"], tool["description"])

    console.print(table)
    console.print()


def demo_mcp_resources():
    """MCP 資源示例"""
    console.print("[bold cyan]2. MCP 資源[/bold cyan]\n")

    resources = [
        {
            "uri": "file:///project/README.md",
            "name": "項目說明",
            "description": "項目的 README 文件",
            "mimeType": "text/markdown"
        },
        {
            "uri": "database://users",
            "name": "用戶數據",
            "description": "用戶數據庫表",
            "mimeType": "application/json"
        },
        {
            "uri": "api://weather/current",
            "name": "實時天氣",
            "description": "當前天氣數據",
            "mimeType": "application/json"
        }
    ]

    console.print("[yellow]可用資源：[/yellow]\n")

    for resource in resources:
        console.print(f"[cyan]• {resource['name']}[/cyan]")
        console.print(f"  URI: {resource['uri']}")
        console.print(f"  類型: {resource['mimeType']}")
        console.print(f"  {resource['description']}\n")


def demo_mcp_prompts():
    """MCP 提示詞模板"""
    console.print("[bold cyan]3. MCP 提示詞模板[/bold cyan]\n")

    prompts = [
        {
            "name": "code_review",
            "description": "代碼審查提示詞",
            "template": "請審查以下代碼，關注代碼質量、性能和安全性：\n\n{code}"
        },
        {
            "name": "bug_analysis",
            "description": "Bug 分析提示詞",
            "template": "分析以下錯誤信息並提供解決方案：\n\n錯誤：{error}\n上下文：{context}"
        },
        {
            "name": "documentation",
            "description": "文檔生成提示詞",
            "template": "為以下代碼生成清晰的文檔：\n\n{code}"
        }
    ]

    for prompt in prompts:
        console.print(Panel(
            f"[yellow]名稱：[/yellow]{prompt['name']}\n"
            f"[yellow]描述：[/yellow]{prompt['description']}\n\n"
            f"[green]模板：[/green]\n{prompt['template']}",
            border_style="cyan"
        ))


def demo_custom_mcp_server():
    """自定義 MCP 服務器示例"""
    console.print("\n[bold cyan]4. 自定義 MCP 服務器[/bold cyan]\n")

    server_code = '''
# 自定義 MCP 服務器示例
from mcp.server import Server
from mcp.types import Tool, Resource

class CustomMCPServer(Server):
    """自定義 MCP 服務器"""

    def __init__(self):
        super().__init__("custom-server", "1.0.0")

    async def list_tools(self):
        """列出可用工具"""
        return [
            Tool(
                name="custom_tool",
                description="自定義工具",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "param": {"type": "string"}
                    }
                }
            )
        ]

    async def call_tool(self, name: str, arguments: dict):
        """執行工具"""
        if name == "custom_tool":
            return {"result": f"處理: {arguments['param']}"}

    async def list_resources(self):
        """列出可用資源"""
        return [
            Resource(
                uri="custom://data",
                name="自定義數據",
                mimeType="application/json"
            )
        ]

    async def read_resource(self, uri: str):
        """讀取資源"""
        if uri == "custom://data":
            return {"data": "自定義數據內容"}

# 啟動服務器
if __name__ == "__main__":
    server = CustomMCPServer()
    server.run()
'''

    console.print(Panel(
        server_code,
        title="自定義 MCP 服務器代碼",
        border_style="green"
    ))
    console.print()


def demo_mcp_integration():
    """MCP 整合示例"""
    console.print("[bold cyan]5. MCP 整合到 Claude 應用[/bold cyan]\n")

    integration_code = '''
from anthropic import Anthropic
from mcp import MCPClient

# 連接到 MCP 服務器
mcp_client = MCPClient()
await mcp_client.connect("filesystem-server")

# 獲取 MCP 工具
mcp_tools = await mcp_client.list_tools()

# 轉換為 Claude 工具格式
claude_tools = [
    {
        "name": tool.name,
        "description": tool.description,
        "input_schema": tool.inputSchema
    }
    for tool in mcp_tools
]

# 使用 Claude 與 MCP 工具
client = Anthropic()

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    tools=claude_tools,
    messages=[
        {
            "role": "user",
            "content": "讀取 config.json 文件"
        }
    ]
)

# 處理工具調用
if response.stop_reason == "tool_use":
    for block in response.content:
        if block.type == "tool_use":
            # 使用 MCP 客戶端執行工具
            result = await mcp_client.call_tool(
                block.name,
                block.input
            )
'''

    console.print(Panel(
        integration_code,
        title="MCP 整合代碼",
        border_style="cyan"
    ))
    console.print()


def show_mcp_ecosystem():
    """MCP 生態系統"""
    console.print("[bold cyan]6. MCP 生態系統[/bold cyan]\n")

    ecosystem = {
        "官方服務器": [
            "filesystem - 文件系統操作",
            "sqlite - SQLite 數據庫",
            "postgres - PostgreSQL 數據庫",
            "brave-search - Brave 搜索引擎",
            "github - GitHub API",
        ],
        "社區服務器": [
            "google-drive - Google Drive 整合",
            "slack - Slack 整合",
            "jira - Jira 項目管理",
            "notion - Notion 文檔",
            "aws - AWS 服務",
        ],
        "工具類型": [
            "數據訪問工具",
            "外部 API 調用",
            "文件操作",
            "數據庫查詢",
            "通知和提醒",
        ]
    }

    for category, items in ecosystem.items():
        console.print(f"\n[yellow]{category}：[/yellow]")
        for item in items:
            console.print(f"  [green]• {item}[/green]")

    console.print()


def show_mcp_benefits():
    """MCP 優勢"""
    console.print("[bold cyan]7. MCP 的優勢[/bold cyan]\n")

    benefits = [
        ("標準化", "統一的接口，減少整合成本"),
        ("可重用性", "一次開發，多處使用"),
        ("生態系統", "豐富的社區貢獻服務器"),
        ("安全性", "內建權限和安全控制"),
        ("可擴展", "輕鬆添加新功能"),
        ("互操作性", "不同工具間無縫協作"),
    ]

    for benefit, description in benefits:
        console.print(f"[green]✓ {benefit}：[/green]{description}")

    console.print()


def show_getting_started():
    """開始使用 MCP"""
    console.print("[bold cyan]8. 開始使用 MCP[/bold cyan]\n")

    steps = [
        ("安裝 MCP SDK", "pip install mcp"),
        ("選擇服務器", "從官方或社區選擇需要的服務器"),
        ("配置連接", "設置服務器連接參數"),
        ("整合到應用", "將 MCP 工具整合到 Claude 應用"),
        ("測試驗證", "測試工具調用是否正常"),
    ]

    for i, (step, description) in enumerate(steps, 1):
        console.print(f"[cyan]{i}. {step}[/cyan]")
        console.print(f"   [dim]{description}[/dim]\n")


def show_resources():
    """相關資源"""
    console.print("[bold cyan]相關資源[/bold cyan]\n")

    resources = [
        ("MCP 官網", "https://modelcontextprotocol.io"),
        ("MCP 規範", "https://spec.modelcontextprotocol.io"),
        ("MCP GitHub", "https://github.com/modelcontextprotocol"),
        ("服務器列表", "https://github.com/modelcontextprotocol/servers"),
        ("開發文檔", "https://modelcontextprotocol.io/docs"),
    ]

    for name, url in resources:
        console.print(f"[cyan]• {name}：[/cyan][blue]{url}[/blue]")

    console.print()


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Claude Code SDK MCP 整合[/bold cyan]\n"
        "[dim]學習如何使用 Model Context Protocol 擴展 Claude 能力[/dim]",
        border_style="cyan"
    ))

    # MCP 介紹
    explain_mcp()

    # 架構展示
    show_mcp_architecture()

    # 1. 工具示例
    demo_mcp_tools()

    # 2. 資源示例
    demo_mcp_resources()

    # 3. 提示詞模板
    demo_mcp_prompts()

    # 4. 自定義服務器
    demo_custom_mcp_server()

    # 5. 整合示例
    demo_mcp_integration()

    # 6. 生態系統
    show_mcp_ecosystem()

    # 7. 優勢
    show_mcp_benefits()

    # 8. 開始使用
    show_getting_started()

    # 相關資源
    show_resources()

    # 完成
    console.print("="*60)
    console.print("[bold green]✓ MCP 整合示例完成！[/bold green]")
    console.print("\n[cyan]關鍵要點：[/cyan]")
    console.print("  • MCP 是連接 AI 和工具的標準協議")
    console.print("  • 豐富的社區貢獻服務器可直接使用")
    console.print("  • 可以創建自定義 MCP 服務器")
    console.print("  • 簡化 Claude 應用的工具整合")


if __name__ == "__main__":
    main()

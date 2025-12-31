#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Composio MCP 協議支援範例
=========================

本範例展示 Composio 的 Model Context Protocol (MCP) 支援，包括：
1. MCP 協議概述
2. MCP 伺服器設置
3. 工具暴露和發現
4. 資源管理
5. 提示詞模板
6. 客戶端整合
7. 實際應用場景

MCP 是 Anthropic 提出的標準協議，用於 AI 模型訪問外部工具和資源。

作者: Composio 團隊
日期: 2025-01-01
"""

import os
import sys
import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 導入必要的套件
try:
    from composio import Composio, App
    from composio.client.exceptions import ComposioException
except ImportError as e:
    print("錯誤：請先安裝 Composio SDK")
    print("執行: pip install composio-core")
    sys.exit(1)


class MCPServerManager:
    """
    MCP 伺服器管理器

    管理 Composio MCP 伺服器的啟動、配置和運行
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化 MCP 伺服器管理器

        Args:
            api_key: Composio API 金鑰
        """
        print("=" * 70)
        print("初始化 MCP 伺服器管理器")
        print("=" * 70)

        self.api_key = api_key or os.getenv("COMPOSIO_API_KEY")

        try:
            # 初始化 Composio 客戶端
            self.client = Composio(api_key=self.api_key)
            print("✓ Composio 客戶端初始化成功")

        except Exception as e:
            print(f"✗ 初始化失敗: {e}")
            raise

    def get_server_info(self) -> Dict[str, Any]:
        """
        獲取 MCP 伺服器資訊

        Returns:
            伺服器資訊
        """
        print("\n" + "=" * 70)
        print("MCP 伺服器資訊")
        print("=" * 70)

        server_info = {
            "protocol": "MCP (Model Context Protocol)",
            "version": "1.0",
            "provider": "Composio",
            "capabilities": [
                "工具發現和執行",
                "資源訪問",
                "提示詞模板",
                "多應用整合",
                "認證管理"
            ],
            "supported_apps": [
                "GitHub", "Slack", "Gmail", "Google Drive",
                "Notion", "Jira", "Salesforce", "更多..."
            ]
        }

        print(f"\n協議: {server_info['protocol']}")
        print(f"版本: {server_info['version']}")
        print(f"提供者: {server_info['provider']}")

        print("\n功能:")
        for capability in server_info['capabilities']:
            print(f"  • {capability}")

        print(f"\n支援的應用: {len(server_info['supported_apps'])}+")

        return server_info

    def list_available_tools(self, app_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        列出可用的 MCP 工具

        Args:
            app_name: 過濾特定應用（可選）

        Returns:
            工具列表
        """
        print("\n" + "=" * 70)
        if app_name:
            print(f"列出 {app_name} 的 MCP 工具")
        else:
            print("列出所有 MCP 工具")
        print("=" * 70)

        try:
            # 獲取工具
            if app_name:
                actions = self.client.actions.get(apps=[app_name])
            else:
                # 獲取熱門應用的工具
                actions = self.client.actions.get(apps=["github", "slack"])

            tools = []
            for action in actions[:20]:  # 限制顯示數量
                tool_info = {
                    "name": action.name,
                    "description": action.description,
                    "app": action.appName if hasattr(action, 'appName') else 'unknown',
                    "parameters": action.parameters if hasattr(action, 'parameters') else {}
                }
                tools.append(tool_info)

            print(f"\n找到 {len(tools)} 個工具:")
            print("-" * 70)

            for i, tool in enumerate(tools[:10], 1):
                print(f"{i}. {tool['name']}")
                print(f"   應用: {tool['app']}")
                print(f"   描述: {tool['description'][:60]}...")
                print()

            return tools

        except Exception as e:
            print(f"✗ 列出工具失敗: {e}")
            return []

    def get_tool_schema(self, tool_name: str) -> Dict[str, Any]:
        """
        獲取工具的 MCP Schema

        Args:
            tool_name: 工具名稱

        Returns:
            工具 Schema
        """
        print("\n" + "=" * 70)
        print(f"獲取工具 Schema: {tool_name}")
        print("=" * 70)

        try:
            # 獲取工具詳情
            actions = self.client.actions.get(actions=[tool_name])

            if not actions:
                print(f"✗ 工具 '{tool_name}' 不存在")
                return {}

            action = actions[0]

            # 構建 MCP Schema
            schema = {
                "name": action.name,
                "description": action.description,
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }

            # 添加參數
            if hasattr(action, 'parameters'):
                for param_name, param_info in action.parameters.items():
                    schema["inputSchema"]["properties"][param_name] = {
                        "type": param_info.get("type", "string"),
                        "description": param_info.get("description", "")
                    }

                    if param_info.get("required", False):
                        schema["inputSchema"]["required"].append(param_name)

            print(f"\nSchema:")
            print(json.dumps(schema, indent=2, ensure_ascii=False))

            return schema

        except Exception as e:
            print(f"✗ 獲取 Schema 失敗: {e}")
            return {}


class MCPResourceManager:
    """
    MCP 資源管理器

    管理 MCP 協議中的資源訪問
    """

    def __init__(self, client: Composio):
        """
        初始化資源管理器

        Args:
            client: Composio 客戶端
        """
        self.client = client
        print("\n資源管理器初始化成功")

    def list_resources(self, app_name: str) -> List[Dict[str, Any]]:
        """
        列出應用的可用資源

        Args:
            app_name: 應用名稱

        Returns:
            資源列表
        """
        print("\n" + "=" * 70)
        print(f"列出 {app_name} 的資源")
        print("=" * 70)

        # 模擬資源列表（實際實現依賴於具體應用）
        resource_templates = {
            "github": [
                {
                    "uri": "github://repositories",
                    "name": "GitHub 倉庫",
                    "description": "訪問用戶的 GitHub 倉庫",
                    "mimeType": "application/json"
                },
                {
                    "uri": "github://issues",
                    "name": "Issues",
                    "description": "訪問倉庫的 Issues",
                    "mimeType": "application/json"
                },
                {
                    "uri": "github://pull-requests",
                    "name": "Pull Requests",
                    "description": "訪問倉庫的 Pull Requests",
                    "mimeType": "application/json"
                }
            ],
            "slack": [
                {
                    "uri": "slack://channels",
                    "name": "Slack 頻道",
                    "description": "訪問工作區的頻道",
                    "mimeType": "application/json"
                },
                {
                    "uri": "slack://messages",
                    "name": "訊息",
                    "description": "訪問頻道訊息",
                    "mimeType": "application/json"
                }
            ]
        }

        resources = resource_templates.get(app_name, [])

        print(f"\n找到 {len(resources)} 個資源:")
        print("-" * 70)

        for i, resource in enumerate(resources, 1):
            print(f"{i}. {resource['name']}")
            print(f"   URI: {resource['uri']}")
            print(f"   描述: {resource['description']}")
            print()

        return resources

    def read_resource(self, resource_uri: str) -> Dict[str, Any]:
        """
        讀取資源內容

        Args:
            resource_uri: 資源 URI

        Returns:
            資源內容
        """
        print("\n" + "=" * 70)
        print(f"讀取資源: {resource_uri}")
        print("=" * 70)

        # 模擬資源讀取
        # 實際實現需要解析 URI 並調用相應的 API

        mock_data = {
            "uri": resource_uri,
            "mimeType": "application/json",
            "content": {
                "message": "這是資源內容",
                "timestamp": datetime.now().isoformat()
            }
        }

        print("\n資源內容:")
        print(json.dumps(mock_data, indent=2, ensure_ascii=False))

        return mock_data


class MCPPromptManager:
    """
    MCP 提示詞管理器

    管理 MCP 協議中的提示詞模板
    """

    def __init__(self):
        """初始化提示詞管理器"""
        print("\n提示詞管理器初始化成功")

        # 預定義的提示詞模板
        self.prompts = {
            "github_review": {
                "name": "github_review",
                "description": "GitHub 代碼審查提示詞",
                "arguments": [
                    {
                        "name": "repo",
                        "description": "倉庫名稱",
                        "required": True
                    },
                    {
                        "name": "pr_number",
                        "description": "Pull Request 編號",
                        "required": True
                    }
                ],
                "template": """請審查 GitHub 倉庫 {{repo}} 的 Pull Request #{{pr_number}}。

審查重點：
1. 代碼質量和可讀性
2. 潛在的 Bug 和安全問題
3. 性能考量
4. 測試覆蓋率
5. 文檔完整性

請提供詳細的反饋和建議。"""
            },
            "slack_summary": {
                "name": "slack_summary",
                "description": "Slack 對話摘要提示詞",
                "arguments": [
                    {
                        "name": "channel",
                        "description": "頻道名稱",
                        "required": True
                    },
                    {
                        "name": "time_range",
                        "description": "時間範圍",
                        "required": False
                    }
                ],
                "template": """請總結 Slack 頻道 {{channel}} {{#if time_range}}在{{time_range}}期間{{/if}}的對話。

摘要應包括：
1. 主要討論主題
2. 重要決定
3. 待辦事項
4. 關鍵問題

請以條列方式呈現。"""
            },
            "task_planning": {
                "name": "task_planning",
                "description": "任務規劃提示詞",
                "arguments": [
                    {
                        "name": "goal",
                        "description": "目標描述",
                        "required": True
                    }
                ],
                "template": """請為以下目標制定詳細的執行計劃：

目標：{{goal}}

計劃應包括：
1. 任務分解
2. 執行步驟
3. 所需資源
4. 時間估算
5. 風險評估

請使用 Composio 工具來執行必要的操作。"""
            }
        }

    def list_prompts(self) -> List[Dict[str, Any]]:
        """
        列出所有提示詞模板

        Returns:
            提示詞列表
        """
        print("\n" + "=" * 70)
        print("可用的提示詞模板")
        print("=" * 70)

        prompt_list = []
        for prompt_id, prompt in self.prompts.items():
            prompt_list.append({
                "name": prompt["name"],
                "description": prompt["description"],
                "arguments": prompt["arguments"]
            })

        for i, prompt in enumerate(prompt_list, 1):
            print(f"\n{i}. {prompt['name']}")
            print(f"   描述: {prompt['description']}")
            print(f"   參數: {len(prompt['arguments'])} 個")

        return prompt_list

    def get_prompt(self, prompt_name: str, arguments: Dict[str, str]) -> str:
        """
        獲取填充後的提示詞

        Args:
            prompt_name: 提示詞名稱
            arguments: 參數值

        Returns:
            填充後的提示詞
        """
        print("\n" + "=" * 70)
        print(f"獲取提示詞: {prompt_name}")
        print("=" * 70)

        if prompt_name not in self.prompts:
            print(f"✗ 提示詞 '{prompt_name}' 不存在")
            return ""

        prompt = self.prompts[prompt_name]
        template = prompt["template"]

        # 簡單的模板填充（實際實現可使用 Jinja2）
        filled_prompt = template
        for key, value in arguments.items():
            filled_prompt = filled_prompt.replace(f"{{{{{key}}}}}", value)

        print(f"\n填充後的提示詞:")
        print("-" * 70)
        print(filled_prompt)

        return filled_prompt


class MCPClientExample:
    """
    MCP 客戶端範例

    展示如何作為 MCP 客戶端使用 Composio
    """

    def __init__(self):
        """初始化客戶端"""
        print("\n" + "=" * 70)
        print("初始化 MCP 客戶端")
        print("=" * 70)

        self.server = MCPServerManager()
        self.resources = MCPResourceManager(self.server.client)
        self.prompts = MCPPromptManager()

    def discover_capabilities(self):
        """
        發現伺服器能力
        """
        print("\n" + "=" * 70)
        print("發現 MCP 伺服器能力")
        print("=" * 70)

        # 獲取伺服器資訊
        server_info = self.server.get_server_info()

        # 列出工具
        tools = self.server.list_available_tools()

        # 列出資源
        github_resources = self.resources.list_resources("github")

        # 列出提示詞
        prompts = self.prompts.list_prompts()

        return {
            "server_info": server_info,
            "tools_count": len(tools),
            "resources_count": len(github_resources),
            "prompts_count": len(prompts)
        }

    def execute_workflow(self, workflow_name: str):
        """
        執行預定義的工作流程

        Args:
            workflow_name: 工作流程名稱
        """
        print("\n" + "=" * 70)
        print(f"執行工作流程: {workflow_name}")
        print("=" * 70)

        workflows = {
            "code_review": self._code_review_workflow,
            "slack_digest": self._slack_digest_workflow,
            "task_automation": self._task_automation_workflow
        }

        if workflow_name in workflows:
            workflows[workflow_name]()
        else:
            print(f"✗ 工作流程 '{workflow_name}' 不存在")

    def _code_review_workflow(self):
        """代碼審查工作流程"""
        print("\n執行代碼審查工作流程")
        print("-" * 70)

        steps = [
            "1. 獲取 GitHub PR 詳情",
            "2. 使用提示詞模板生成審查指引",
            "3. 分析代碼變更",
            "4. 生成審查評論",
            "5. 發布評論到 PR",
            "6. 在 Slack 通知團隊"
        ]

        for step in steps:
            print(f"  {step}")

    def _slack_digest_workflow(self):
        """Slack 摘要工作流程"""
        print("\n執行 Slack 摘要工作流程")
        print("-" * 70)

        steps = [
            "1. 讀取 Slack 頻道訊息",
            "2. 使用提示詞模板生成摘要指引",
            "3. 分析對話內容",
            "4. 生成摘要報告",
            "5. 發布到指定頻道"
        ]

        for step in steps:
            print(f"  {step}")

    def _task_automation_workflow(self):
        """任務自動化工作流程"""
        print("\n執行任務自動化工作流程")
        print("-" * 70)

        steps = [
            "1. 接收任務描述",
            "2. 使用規劃提示詞",
            "3. 分解任務步驟",
            "4. 調用相應的工具",
            "5. 執行任務",
            "6. 報告結果"
        ]

        for step in steps:
            print(f"  {step}")


def demo_mcp_protocol():
    """
    演示 MCP 協議
    """
    print("\n" + "=" * 80)
    print("MCP 協議概述")
    print("=" * 80)

    print("""
Model Context Protocol (MCP) 是什麼？
--------------------------------------
MCP 是由 Anthropic 提出的開放標準協議，用於：

1. 工具發現和執行
   - AI 模型可以發現可用的工具
   - 了解工具的功能和參數
   - 執行工具並獲取結果

2. 資源訪問
   - 訪問外部數據源
   - 讀取文件和數據庫
   - 獲取 API 資源

3. 提示詞模板
   - 預定義的提示詞模板
   - 參數化的提示詞
   - 上下文感知的提示詞

4. 標準化通訊
   - 統一的協議格式
   - 跨平台兼容
   - 易於整合

Composio 與 MCP
--------------
Composio 完全支援 MCP 協議，提供：

• 250+ 應用的 MCP 整合
• 10,000+ 工具的標準化訪問
• 統一的認證管理
• 資源和提示詞管理
• 與主流 AI 框架的整合
    """)


def demo_use_cases():
    """
    演示使用場景
    """
    print("\n" + "=" * 80)
    print("MCP 使用場景")
    print("=" * 80)

    use_cases = [
        ("AI 開發助手", [
            "代碼審查和建議",
            "自動化測試生成",
            "文檔自動生成",
            "Bug 追蹤和修復"
        ]),
        ("團隊協作", [
            "會議摘要生成",
            "任務自動分配",
            "進度追蹤和報告",
            "知識庫管理"
        ]),
        ("數據分析", [
            "自動數據收集",
            "報告生成",
            "異常檢測",
            "預測分析"
        ]),
        ("客戶服務", [
            "自動回覆",
            "工單管理",
            "知識庫查詢",
            "客戶反饋分析"
        ])
    ]

    for use_case, examples in use_cases:
        print(f"\n{use_case}:")
        for example in examples:
            print(f"  • {example}")


def main():
    """
    主函數
    """
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║              Composio MCP 協議支援範例                           ║
    ║                                                                  ║
    ║              標準化的 AI 工具整合協議                            ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)

    # 演示 MCP 協議
    demo_mcp_protocol()

    # 創建客戶端範例
    client = MCPClientExample()

    # 發現能力
    capabilities = client.discover_capabilities()

    # 演示工作流程
    print("\n" + "=" * 80)
    print("預定義工作流程")
    print("=" * 80)

    workflows = ["code_review", "slack_digest", "task_automation"]
    for workflow in workflows:
        client.execute_workflow(workflow)

    # 演示使用場景
    demo_use_cases()

    print("\n" + "=" * 80)
    print("更多資源:")
    print("  • MCP 規範: https://spec.modelcontextprotocol.io")
    print("  • Composio MCP: https://docs.composio.dev/mcp")
    print("  • GitHub: https://github.com/ComposioHQ/composio")
    print("=" * 80)


if __name__ == "__main__":
    main()

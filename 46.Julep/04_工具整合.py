"""
Julep 工具整合示例

這個模塊展示了 Julep 平台與 Composio 的工具整合功能。
支持 90+ 第三方應用整合，包括 GitHub、Slack、Gmail 等。

主要功能：
1. Composio 工具整合
2. 自定義工具定義
3. 工具鏈調用
4. API 包裝
5. 第三方服務整合
6. 工具權限管理

作者：Julep 示例
日期：2025-12-31
"""

import json
import time
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import hashlib


class ToolCategory(Enum):
    """工具分類枚舉"""
    COMMUNICATION = "communication"  # 通訊工具
    DEVELOPMENT = "development"  # 開發工具
    PRODUCTIVITY = "productivity"  # 生產力工具
    DATA = "data"  # 數據工具
    AI = "ai"  # AI 工具
    CUSTOM = "custom"  # 自定義工具


@dataclass
class ToolParameter:
    """工具參數定義"""
    name: str
    type: str
    description: str
    required: bool = True
    default: Optional[Any] = None
    enum: Optional[List[Any]] = None

    def to_schema(self) -> Dict[str, Any]:
        """轉換為 JSON Schema 格式"""
        schema = {
            "type": self.type,
            "description": self.description
        }
        if self.enum:
            schema["enum"] = self.enum
        if self.default is not None:
            schema["default"] = self.default
        return schema


class Tool:
    """工具類

    定義一個可被 AI Agent 調用的工具。
    """

    def __init__(
        self,
        name: str,
        description: str,
        category: ToolCategory,
        parameters: List[ToolParameter],
        function: Callable,
        requires_auth: bool = False
    ):
        """初始化工具

        Args:
            name: 工具名稱
            description: 工具描述
            category: 工具分類
            parameters: 參數列表
            function: 執行函數
            requires_auth: 是否需要認證
        """
        self.name = name
        self.description = description
        self.category = category
        self.parameters = parameters
        self.function = function
        self.requires_auth = requires_auth
        self.call_count = 0
        self.last_called = None

    def get_schema(self) -> Dict[str, Any]:
        """獲取工具的 OpenAI 函數調用格式 schema"""
        required_params = [p.name for p in self.parameters if p.required]
        properties = {p.name: p.to_schema() for p in self.parameters}

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required_params
                }
            }
        }

    def execute(self, **kwargs) -> Any:
        """執行工具

        Args:
            **kwargs: 工具參數

        Returns:
            執行結果
        """
        # 驗證必需參數
        required_params = {p.name for p in self.parameters if p.required}
        provided_params = set(kwargs.keys())

        missing_params = required_params - provided_params
        if missing_params:
            raise ValueError(f"缺少必需參數: {missing_params}")

        # 更新統計信息
        self.call_count += 1
        self.last_called = datetime.now()

        # 執行工具函數
        print(f"[TOOL] 執行工具: {self.name}")
        result = self.function(**kwargs)
        print(f"[TOOL] 執行完成")

        return result

    def __repr__(self) -> str:
        return f"Tool(name={self.name}, category={self.category.value})"


class ToolRegistry:
    """工具註冊中心

    管理所有可用的工具。
    """

    def __init__(self):
        """初始化註冊中心"""
        self.tools: Dict[str, Tool] = {}
        self.auth_tokens: Dict[str, str] = {}

    def register(self, tool: Tool):
        """註冊工具

        Args:
            tool: 工具對象
        """
        self.tools[tool.name] = tool
        print(f"[INFO] 註冊工具: {tool.name} ({tool.category.value})")

    def unregister(self, tool_name: str):
        """註銷工具"""
        if tool_name in self.tools:
            del self.tools[tool_name]
            print(f"[INFO] 註銷工具: {tool_name}")

    def get_tool(self, name: str) -> Optional[Tool]:
        """獲取工具"""
        return self.tools.get(name)

    def list_tools(self, category: Optional[ToolCategory] = None) -> List[Tool]:
        """列出工具

        Args:
            category: 按分類篩選（可選）

        Returns:
            工具列表
        """
        if category:
            return [t for t in self.tools.values() if t.category == category]
        return list(self.tools.values())

    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """獲取所有工具的 schema"""
        return [tool.get_schema() for tool in self.tools.values()]

    def set_auth_token(self, service: str, token: str):
        """設置服務認證令牌

        Args:
            service: 服務名稱
            token: 認證令牌
        """
        self.auth_tokens[service] = token
        print(f"[INFO] 設置 {service} 認證令牌")

    def get_auth_token(self, service: str) -> Optional[str]:
        """獲取服務認證令牌"""
        return self.auth_tokens.get(service)


class ComposioIntegration:
    """Composio 整合類

    模擬與 Composio 平台的整合。
    """

    def __init__(self, api_key: str):
        """初始化 Composio 整合

        Args:
            api_key: Composio API 金鑰
        """
        self.api_key = api_key
        self.connected_apps: Dict[str, bool] = {}

    def connect_app(self, app_name: str, credentials: Dict[str, str]) -> bool:
        """連接應用

        Args:
            app_name: 應用名稱
            credentials: 認證信息

        Returns:
            是否成功連接
        """
        print(f"[COMPOSIO] 連接應用: {app_name}")
        time.sleep(0.5)  # 模擬 API 調用

        # 模擬連接成功
        self.connected_apps[app_name] = True
        print(f"[SUCCESS] {app_name} 連接成功")
        return True

    def get_app_actions(self, app_name: str) -> List[str]:
        """獲取應用可用動作

        Args:
            app_name: 應用名稱

        Returns:
            動作列表
        """
        # 模擬不同應用的動作
        app_actions = {
            "github": ["create_issue", "create_pr", "list_repos", "star_repo"],
            "slack": ["send_message", "create_channel", "list_users"],
            "gmail": ["send_email", "read_emails", "create_draft"],
            "notion": ["create_page", "update_page", "search_pages"],
            "trello": ["create_card", "move_card", "add_comment"]
        }
        return app_actions.get(app_name, [])

    def execute_action(
        self,
        app_name: str,
        action: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """執行應用動作

        Args:
            app_name: 應用名稱
            action: 動作名稱
            params: 參數

        Returns:
            執行結果
        """
        if app_name not in self.connected_apps:
            raise ValueError(f"應用未連接: {app_name}")

        print(f"[COMPOSIO] 執行動作: {app_name}.{action}")
        print(f"[COMPOSIO] 參數: {params}")

        time.sleep(0.3)  # 模擬 API 調用

        # 模擬成功結果
        result = {
            "success": True,
            "action": action,
            "app": app_name,
            "result": f"成功執行 {action}",
            "timestamp": datetime.now().isoformat()
        }

        print(f"[SUCCESS] 動作執行完成")
        return result


class ToolFactory:
    """工具工廠

    用於創建各種預定義的工具。
    """

    @staticmethod
    def create_github_tools(composio: ComposioIntegration) -> List[Tool]:
        """創建 GitHub 工具集"""
        tools = []

        # 創建 Issue 工具
        create_issue_tool = Tool(
            name="github_create_issue",
            description="在 GitHub 倉庫中創建新 Issue",
            category=ToolCategory.DEVELOPMENT,
            parameters=[
                ToolParameter("repo", "string", "倉庫名稱（格式：owner/repo）"),
                ToolParameter("title", "string", "Issue 標題"),
                ToolParameter("body", "string", "Issue 內容", required=False),
                ToolParameter("labels", "array", "標籤列表", required=False)
            ],
            function=lambda **kwargs: composio.execute_action("github", "create_issue", kwargs),
            requires_auth=True
        )
        tools.append(create_issue_tool)

        # 創建 PR 工具
        create_pr_tool = Tool(
            name="github_create_pr",
            description="創建 Pull Request",
            category=ToolCategory.DEVELOPMENT,
            parameters=[
                ToolParameter("repo", "string", "倉庫名稱"),
                ToolParameter("title", "string", "PR 標題"),
                ToolParameter("head", "string", "源分支"),
                ToolParameter("base", "string", "目標分支"),
                ToolParameter("body", "string", "PR 描述", required=False)
            ],
            function=lambda **kwargs: composio.execute_action("github", "create_pr", kwargs),
            requires_auth=True
        )
        tools.append(create_pr_tool)

        return tools

    @staticmethod
    def create_slack_tools(composio: ComposioIntegration) -> List[Tool]:
        """創建 Slack 工具集"""
        tools = []

        # 發送消息工具
        send_message_tool = Tool(
            name="slack_send_message",
            description="發送 Slack 消息",
            category=ToolCategory.COMMUNICATION,
            parameters=[
                ToolParameter("channel", "string", "頻道名稱或 ID"),
                ToolParameter("text", "string", "消息內容"),
                ToolParameter("thread_ts", "string", "線程時間戳（回復用）", required=False)
            ],
            function=lambda **kwargs: composio.execute_action("slack", "send_message", kwargs),
            requires_auth=True
        )
        tools.append(send_message_tool)

        return tools

    @staticmethod
    def create_custom_tools() -> List[Tool]:
        """創建自定義工具集"""
        tools = []

        # 文本處理工具
        def process_text(text: str, operation: str) -> str:
            """文本處理函數"""
            operations = {
                "uppercase": text.upper(),
                "lowercase": text.lower(),
                "reverse": text[::-1],
                "word_count": str(len(text.split()))
            }
            return operations.get(operation, text)

        text_tool = Tool(
            name="text_processor",
            description="處理文本（大寫、小寫、反轉、計數）",
            category=ToolCategory.CUSTOM,
            parameters=[
                ToolParameter("text", "string", "要處理的文本"),
                ToolParameter(
                    "operation",
                    "string",
                    "操作類型",
                    enum=["uppercase", "lowercase", "reverse", "word_count"]
                )
            ],
            function=process_text
        )
        tools.append(text_tool)

        # 數據轉換工具
        def convert_data(data: str, from_format: str, to_format: str) -> str:
            """數據格式轉換"""
            print(f"  轉換數據: {from_format} -> {to_format}")
            # 簡化的轉換邏輯
            if from_format == "json" and to_format == "yaml":
                obj = json.loads(data)
                return f"# YAML 格式\n{json.dumps(obj, indent=2)}"
            return data

        convert_tool = Tool(
            name="data_converter",
            description="轉換數據格式（JSON、YAML、XML）",
            category=ToolCategory.DATA,
            parameters=[
                ToolParameter("data", "string", "要轉換的數據"),
                ToolParameter("from_format", "string", "源格式"),
                ToolParameter("to_format", "string", "目標格式")
            ],
            function=convert_data
        )
        tools.append(convert_tool)

        # 哈希計算工具
        def calculate_hash(text: str, algorithm: str = "sha256") -> str:
            """計算哈希值"""
            if algorithm == "sha256":
                return hashlib.sha256(text.encode()).hexdigest()
            elif algorithm == "md5":
                return hashlib.md5(text.encode()).hexdigest()
            else:
                raise ValueError(f"不支持的算法: {algorithm}")

        hash_tool = Tool(
            name="hash_calculator",
            description="計算文本的哈希值",
            category=ToolCategory.CUSTOM,
            parameters=[
                ToolParameter("text", "string", "要計算哈希的文本"),
                ToolParameter(
                    "algorithm",
                    "string",
                    "哈希算法",
                    required=False,
                    default="sha256",
                    enum=["sha256", "md5"]
                )
            ],
            function=calculate_hash
        )
        tools.append(hash_tool)

        return tools


class ToolChain:
    """工具鏈

    將多個工具串聯執行。
    """

    def __init__(self, name: str):
        """初始化工具鏈"""
        self.name = name
        self.steps: List[Dict[str, Any]] = []

    def add_step(self, tool: Tool, params: Dict[str, Any]):
        """添加步驟

        Args:
            tool: 工具對象
            params: 參數（可以使用 "$prev" 引用上一步的輸出）
        """
        self.steps.append({
            "tool": tool,
            "params": params
        })

    def execute(self, initial_input: Optional[Any] = None) -> Any:
        """執行工具鏈

        Args:
            initial_input: 初始輸入

        Returns:
            最終輸出
        """
        print(f"\n{'='*60}")
        print(f"執行工具鏈: {self.name}")
        print(f"{'='*60}")

        result = initial_input

        for i, step in enumerate(self.steps, 1):
            tool = step["tool"]
            params = step["params"].copy()

            # 替換 $prev 為上一步的結果
            for key, value in params.items():
                if value == "$prev":
                    params[key] = result

            print(f"\n步驟 {i}: {tool.name}")
            result = tool.execute(**params)
            print(f"輸出: {result}")

        print(f"\n{'='*60}")
        print(f"工具鏈執行完成")
        print(f"{'='*60}")

        return result


def demo_tool_registry():
    """工具註冊示例"""
    print("\n" + "="*60)
    print("示例 1: 工具註冊和管理")
    print("="*60)

    registry = ToolRegistry()

    # 創建並註冊自定義工具
    custom_tools = ToolFactory.create_custom_tools()
    for tool in custom_tools:
        registry.register(tool)

    # 列出所有工具
    print(f"\n註冊的工具總數: {len(registry.tools)}")
    print("\n工具列表:")
    for tool in registry.list_tools():
        print(f"  - {tool.name} ({tool.category.value})")
        print(f"    {tool.description}")

    # 獲取工具 schema
    print("\n工具 Schema 示例:")
    schema = registry.get_tool("text_processor").get_schema()
    print(json.dumps(schema, indent=2, ensure_ascii=False))


def demo_composio_integration():
    """Composio 整合示例"""
    print("\n" + "="*60)
    print("示例 2: Composio 應用整合")
    print("="*60)

    # 初始化 Composio
    composio = ComposioIntegration(api_key="demo_key")

    # 連接 GitHub
    composio.connect_app("github", {"token": "github_token_123"})

    # 獲取可用動作
    actions = composio.get_app_actions("github")
    print(f"\nGitHub 可用動作: {actions}")

    # 創建 GitHub 工具
    github_tools = ToolFactory.create_github_tools(composio)

    # 創建註冊中心並註冊工具
    registry = ToolRegistry()
    for tool in github_tools:
        registry.register(tool)

    # 使用工具創建 Issue
    print("\n執行 GitHub 操作:")
    create_issue_tool = registry.get_tool("github_create_issue")
    result = create_issue_tool.execute(
        repo="username/my-repo",
        title="修復登錄錯誤",
        body="用戶報告無法登錄系統",
        labels=["bug", "高優先級"]
    )

    print(f"\n結果: {json.dumps(result, indent=2, ensure_ascii=False)}")


def demo_tool_chain():
    """工具鏈示例"""
    print("\n" + "="*60)
    print("示例 3: 工具鏈執行")
    print("="*60)

    # 創建工具
    registry = ToolRegistry()
    custom_tools = ToolFactory.create_custom_tools()
    for tool in custom_tools:
        registry.register(tool)

    # 創建工具鏈
    chain = ToolChain("文本處理鏈")

    # 添加處理步驟
    text_tool = registry.get_tool("text_processor")
    hash_tool = registry.get_tool("hash_calculator")

    chain.add_step(text_tool, {"text": "Hello World", "operation": "uppercase"})
    chain.add_step(hash_tool, {"text": "$prev", "algorithm": "sha256"})

    # 執行工具鏈
    final_result = chain.execute()

    print(f"\n最終結果: {final_result}")


def demo_multi_app_workflow():
    """多應用工作流示例"""
    print("\n" + "="*60)
    print("示例 4: 多應用協作工作流")
    print("="*60)

    # 初始化
    composio = ComposioIntegration(api_key="demo_key")
    registry = ToolRegistry()

    # 連接多個應用
    composio.connect_app("github", {"token": "github_token"})
    composio.connect_app("slack", {"token": "slack_token"})

    # 創建並註冊工具
    github_tools = ToolFactory.create_github_tools(composio)
    slack_tools = ToolFactory.create_slack_tools(composio)

    for tool in github_tools + slack_tools:
        registry.register(tool)

    # 模擬工作流：創建 PR 並通知 Slack
    print("\n工作流: 創建 PR -> 發送 Slack 通知")

    # 步驟 1: 創建 PR
    pr_tool = registry.get_tool("github_create_pr")
    pr_result = pr_tool.execute(
        repo="myorg/myapp",
        title="添加新功能",
        head="feature-branch",
        base="main",
        body="實現了用戶請求的新功能"
    )

    # 步驟 2: 發送 Slack 通知
    slack_tool = registry.get_tool("slack_send_message")
    slack_result = slack_tool.execute(
        channel="#dev-team",
        text=f"新 PR 已創建: 添加新功能\n請查看並審核"
    )

    print("\n工作流執行完成！")
    print(f"PR 狀態: {pr_result.get('success')}")
    print(f"通知狀態: {slack_result.get('success')}")


def main():
    """主函數"""
    print("="*60)
    print("Julep 工具整合示例")
    print("="*60)

    try:
        demo_tool_registry()
        demo_composio_integration()
        demo_tool_chain()
        demo_multi_app_workflow()

        print("\n" + "="*60)
        print("所有示例執行完成！")
        print("="*60)

    except Exception as e:
        print(f"\n[ERROR] 執行出錯: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

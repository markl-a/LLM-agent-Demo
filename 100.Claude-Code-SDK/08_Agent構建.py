"""
Claude Code SDK Agent 構建示例

本示例展示：
1. 完整 Agent 架構
2. 任務規劃和執行
3. 工具整合
4. 自主決策流程
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Optional
from anthropic import Anthropic
from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree
from rich.progress import Progress, SpinnerColumn, TextColumn
from dotenv import load_dotenv

console = Console()
load_dotenv()


class Tool:
    """工具基類"""

    def __init__(self, name: str, description: str, parameters: dict):
        self.name = name
        self.description = description
        self.parameters = parameters

    def to_schema(self):
        """轉換為 Claude 工具 schema"""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.parameters
        }

    def execute(self, **kwargs):
        """執行工具（子類實現）"""
        raise NotImplementedError


class SearchTool(Tool):
    """搜索工具"""

    def __init__(self):
        super().__init__(
            name="search",
            description="搜索互聯網獲取信息",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索查詢"}
                },
                "required": ["query"]
            }
        )

    def execute(self, query: str):
        """模擬搜索"""
        return {
            "results": [
                f"關於 '{query}' 的搜索結果 1",
                f"關於 '{query}' 的搜索結果 2",
                f"關於 '{query}' 的搜索結果 3"
            ]
        }


class CalculatorTool(Tool):
    """計算器工具"""

    def __init__(self):
        super().__init__(
            name="calculator",
            description="執行數學計算",
            parameters={
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "數學表達式"}
                },
                "required": ["expression"]
            }
        )

    def execute(self, expression: str):
        """執行計算"""
        try:
            result = eval(expression, {"__builtins__": {}}, {})
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class FileTool(Tool):
    """文件操作工具"""

    def __init__(self):
        super().__init__(
            name="file_operations",
            description="讀取或寫入文件",
            parameters={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["read", "write"],
                        "description": "操作類型"
                    },
                    "filename": {"type": "string", "description": "文件名"},
                    "content": {"type": "string", "description": "文件內容（寫入時需要）"}
                },
                "required": ["operation", "filename"]
            }
        )

    def execute(self, operation: str, filename: str, content: str = ""):
        """執行文件操作"""
        if operation == "read":
            return {"content": f"模擬讀取 {filename} 的內容"}
        elif operation == "write":
            return {"status": f"已寫入內容到 {filename}"}


class Agent:
    """Claude Agent"""

    def __init__(self, name: str, role: str, tools: List[Tool] = None):
        self.name = name
        self.role = role
        self.client = Anthropic()
        self.tools = tools or []
        self.messages = []
        self.execution_log = []

    def add_tool(self, tool: Tool):
        """添加工具"""
        self.tools.append(tool)

    def get_tool_schemas(self):
        """獲取所有工具的 schema"""
        return [tool.to_schema() for tool in self.tools]

    def execute_tool(self, tool_name: str, tool_input: dict):
        """執行工具"""
        for tool in self.tools:
            if tool.name == tool_name:
                console.print(f"[cyan]🔧 執行工具: {tool_name}[/cyan]")
                console.print(f"[dim]輸入: {json.dumps(tool_input, ensure_ascii=False)}[/dim]")

                result = tool.execute(**tool_input)

                console.print(f"[green]✓ 結果: {json.dumps(result, ensure_ascii=False)[:100]}...[/green]\n")

                self.execution_log.append({
                    "tool": tool_name,
                    "input": tool_input,
                    "output": result,
                    "timestamp": datetime.now().isoformat()
                })

                return result

        return {"error": f"未找到工具: {tool_name}"}

    def run(self, task: str, max_iterations: int = 10):
        """運行 Agent 完成任務"""
        console.print(Panel.fit(
            f"[bold cyan]Agent: {self.name}[/bold cyan]\n"
            f"[dim]角色: {self.role}[/dim]\n"
            f"[yellow]任務: {task}[/yellow]",
            border_style="cyan"
        ))

        # 系統提示詞
        system_prompt = f"""你是 {self.name}，一個 {self.role}。

你的任務是: {task}

你可以使用以下工具來完成任務。請分析任務，制定計劃，然後逐步執行。
當你完成任務後，提供最終答案。"""

        # 初始消息
        self.messages = [
            {
                "role": "user",
                "content": f"請完成以下任務: {task}"
            }
        ]

        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            console.print(f"\n[bold blue]━━━ 迭代 {iteration} ━━━[/bold blue]\n")

            # 調用 Claude
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2048,
                system=system_prompt,
                tools=self.get_tool_schemas(),
                messages=self.messages
            )

            # 處理響應
            if response.stop_reason == "tool_use":
                # 需要使用工具
                self.messages.append({"role": "assistant", "content": response.content})

                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        result = self.execute_tool(block.name, block.input)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(result, ensure_ascii=False)
                        })

                self.messages.append({"role": "user", "content": tool_results})

            elif response.stop_reason == "end_turn":
                # 任務完成
                final_response = None
                for block in response.content:
                    if hasattr(block, "text"):
                        final_response = block.text
                        break

                if final_response:
                    console.print(Panel(
                        final_response,
                        title="[bold green]任務完成[/bold green]",
                        border_style="green"
                    ))

                return {
                    "success": True,
                    "response": final_response,
                    "iterations": iteration,
                    "execution_log": self.execution_log
                }

            else:
                console.print(f"[yellow]停止原因: {response.stop_reason}[/yellow]")
                break

        return {
            "success": False,
            "error": "超過最大迭代次數",
            "iterations": iteration,
            "execution_log": self.execution_log
        }


def demo_simple_agent():
    """簡單 Agent 示例"""
    console.print("\n[bold cyan]1. 簡單任務 Agent[/bold cyan]\n")

    # 創建 Agent
    agent = Agent(
        name="助手",
        role="通用助手"
    )

    # 添加工具
    agent.add_tool(CalculatorTool())
    agent.add_tool(SearchTool())

    # 執行任務
    result = agent.run("計算 123 * 456 的結果，然後搜索關於這個數字的有趣事實")

    console.print(f"\n[cyan]執行了 {result['iterations']} 次迭代[/cyan]")


def demo_research_agent():
    """研究 Agent 示例"""
    console.print("\n[bold cyan]2. 研究 Agent[/bold cyan]\n")

    agent = Agent(
        name="研究員",
        role="專業研究助手"
    )

    agent.add_tool(SearchTool())
    agent.add_tool(FileTool())

    task = "研究'量子計算'的基本概念，並將摘要保存到文件"

    result = agent.run(task)


def demo_planning_agent():
    """規劃 Agent 示例"""
    console.print("\n[bold cyan]3. 任務規劃 Agent[/bold cyan]\n")

    client = Anthropic()

    task = "組織一個技術分享會"

    # 規劃階段
    planning_prompt = f"""
任務: {task}

請制定詳細的執行計劃，包括：
1. 需要完成的步驟
2. 每個步驟的優先級
3. 所需資源
4. 時間估算

以結構化的方式輸出計劃。
"""

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2048,
        messages=[{"role": "user", "content": planning_prompt}]
    )

    plan = response.content[0].text

    console.print(Panel(plan, title="執行計劃", border_style="cyan"))
    console.print()


def demo_multi_tool_agent():
    """多工具協作 Agent"""
    console.print("\n[bold cyan]4. 多工具協作 Agent[/bold cyan]\n")

    agent = Agent(
        name="數據分析師",
        role="數據分析專家"
    )

    # 添加多個工具
    agent.add_tool(SearchTool())
    agent.add_tool(CalculatorTool())
    agent.add_tool(FileTool())

    task = "分析 2024 年 AI 領域的投資趨勢，計算平均投資額，並保存報告"

    result = agent.run(task, max_iterations=8)


def demo_reasoning_agent():
    """推理 Agent 示例"""
    console.print("\n[bold cyan]5. 推理決策 Agent[/bold cyan]\n")

    client = Anthropic()

    problem = """
你有 8 個外觀相同的球，其中一個的重量與其他 7 個不同（可能更重或更輕）。
你有一個天平，最多可以使用 2 次。請找出那個特殊的球。
"""

    reasoning_prompt = f"""
問題: {problem}

請：
1. 分析問題
2. 制定策略
3. 逐步推理
4. 給出答案

用清晰的邏輯展示你的思考過程。
"""

    with Progress(
        SpinnerColumn(),
        TextColumn("[cyan]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("思考中...", total=None)

        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2048,
            messages=[{"role": "user", "content": reasoning_prompt}]
        )

        progress.update(task, description="[green]完成")

    console.print(Panel(
        response.content[0].text,
        title="推理過程",
        border_style="green"
    ))
    console.print()


def demo_agent_architecture():
    """Agent 架構可視化"""
    console.print("\n[bold cyan]6. Agent 架構[/bold cyan]\n")

    tree = Tree("[bold cyan]Claude Agent 架構")

    # 核心組件
    core = tree.add("[yellow]核心組件")
    core.add("🧠 Claude 模型（決策中心）")
    core.add("💬 對話管理器")
    core.add("📋 任務規劃器")

    # 工具層
    tools = tree.add("[green]工具層")
    tools.add("🔧 內建工具")
    tools.add("🔌 自定義工具")
    tools.add("🌐 外部 API")

    # 記憶層
    memory = tree.add("[blue]記憶層")
    memory.add("💾 短期記憶（對話歷史）")
    memory.add("🗄️  長期記憶（向量數據庫）")
    memory.add("📊 執行日誌")

    # 執行層
    execution = tree.add("[magenta]執行層")
    execution.add("⚙️  工具執行器")
    execution.add("🔄 錯誤處理")
    execution.add("📈 監控和日誌")

    console.print(tree)
    console.print()


def show_agent_patterns():
    """Agent 設計模式"""
    console.print("[bold cyan]Agent 設計模式[/bold cyan]\n")

    patterns = [
        ("ReAct", "推理（Reasoning）+ 行動（Acting）", "適合複雜問題求解"),
        ("規劃執行", "先規劃再執行", "適合多步驟任務"),
        ("工具鏈", "鏈式工具調用", "適合數據處理流程"),
        ("自主循環", "持續運行直到完成", "適合自主任務"),
        ("人在回路", "關鍵決策需要人工確認", "適合高風險操作"),
        ("多 Agent", "多個 Agent 協作", "適合複雜系統"),
    ]

    for pattern, description, use_case in patterns:
        console.print(f"[cyan]• {pattern}：[/cyan]{description}")
        console.print(f"  [dim]{use_case}[/dim]\n")


def show_best_practices():
    """最佳實踐"""
    console.print("[bold cyan]Agent 構建最佳實踐[/bold cyan]\n")

    practices = [
        ("明確角色", "給 Agent 清晰的角色定義和職責"),
        ("工具設計", "工具應該功能單一、文檔清晰"),
        ("錯誤處理", "優雅處理工具執行失敗"),
        ("迭代限制", "設置最大迭代次數防止無限循環"),
        ("日誌記錄", "記錄所有決策和執行過程"),
        ("人工監督", "關鍵操作需要人工確認"),
        ("性能優化", "緩存常用結果，減少 API 調用"),
    ]

    for practice, description in practices:
        console.print(f"[green]✓ {practice}：[/green]{description}")

    console.print()


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Claude Code SDK Agent 構建[/bold cyan]\n"
        "[dim]學習如何構建完整的自主 Agent 系統[/dim]",
        border_style="cyan"
    ))

    # 1. 簡單 Agent
    demo_simple_agent()

    # 2. 研究 Agent
    demo_research_agent()

    # 3. 規劃 Agent
    demo_planning_agent()

    # 4. 多工具 Agent
    demo_multi_tool_agent()

    # 5. 推理 Agent
    demo_reasoning_agent()

    # 6. 架構展示
    demo_agent_architecture()

    # 設計模式
    show_agent_patterns()

    # 最佳實踐
    show_best_practices()

    # 完成
    console.print("="*60)
    console.print("[bold green]✓ Agent 構建示例完成！[/bold green]")
    console.print("\n[cyan]關鍵要點：[/cyan]")
    console.print("  • Agent 是具有自主性的 AI 系統")
    console.print("  • 工具擴展 Agent 的能力邊界")
    console.print("  • 任務規劃是 Agent 的核心能力")
    console.print("  • 迭代執行實現複雜任務")


if __name__ == "__main__":
    main()

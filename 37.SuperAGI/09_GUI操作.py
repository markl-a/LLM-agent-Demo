"""
SuperAGI GUI 操作示例

這個示例展示了如何:
1. 通過 Web 界面管理 Agent
2. 可視化配置和監控
3. 創建儀表板
4. 生成可視化報告
5. 實時監控系統狀態

SuperAGI 的 GUI 是其企業級特性的重要組成部分。
"""

import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field


# ==================== GUI 組件定義 ====================

@dataclass
class DashboardWidget:
    """儀表板組件"""
    widget_id: str
    widget_type: str  # chart, stat, table, log
    title: str
    data: Any
    config: Dict = field(default_factory=dict)


class Dashboard:
    """
    儀表板

    管理和顯示各種可視化組件
    """

    def __init__(self, dashboard_id: str, title: str):
        """
        初始化儀表板

        參數:
            dashboard_id: 儀表板 ID
            title: 標題
        """
        self.dashboard_id = dashboard_id
        self.title = title
        self.widgets: List[DashboardWidget] = []
        self.layout = "grid"

    def add_widget(self, widget: DashboardWidget):
        """添加組件"""
        self.widgets.append(widget)
        print(f"📊 添加組件: {widget.title}")

    def render(self) -> str:
        """渲染儀表板"""
        output = f"\n{'=' * 80}\n"
        output += f"📊 {self.title}\n"
        output += f"{'=' * 80}\n\n"

        for widget in self.widgets:
            output += self._render_widget(widget)
            output += "\n" + "-" * 80 + "\n\n"

        return output

    def _render_widget(self, widget: DashboardWidget) -> str:
        """渲染單個組件"""
        output = f"▶ {widget.title} ({widget.widget_type})\n\n"

        if widget.widget_type == "stat":
            output += self._render_stat(widget.data)
        elif widget.widget_type == "chart":
            output += self._render_chart(widget.data)
        elif widget.widget_type == "table":
            output += self._render_table(widget.data)
        elif widget.widget_type == "log":
            output += self._render_log(widget.data)

        return output

    def _render_stat(self, data: Dict) -> str:
        """渲染統計數據"""
        output = ""
        for key, value in data.items():
            output += f"  {key}: {value}\n"
        return output

    def _render_chart(self, data: Dict) -> str:
        """渲染圖表（文本模式）"""
        chart_type = data.get("type", "bar")
        values = data.get("values", [])

        output = f"  類型: {chart_type}\n"
        output += f"  數據點: {len(values)}\n"

        if chart_type == "bar":
            for label, value in values:
                bar = "█" * int(value / 10)
                output += f"  {label:15s} {bar} {value}\n"

        return output

    def _render_table(self, data: List[Dict]) -> str:
        """渲染表格"""
        if not data:
            return "  (空表格)\n"

        # 獲取列名
        columns = list(data[0].keys())

        # 表頭
        output = "  "
        for col in columns:
            output += f"{col:15s} "
        output += "\n  " + "-" * (15 * len(columns)) + "\n"

        # 數據行
        for row in data:
            output += "  "
            for col in columns:
                value = str(row.get(col, ""))[:14]
                output += f"{value:15s} "
            output += "\n"

        return output

    def _render_log(self, data: List[str]) -> str:
        """渲染日誌"""
        output = ""
        for line in data[-10:]:  # 顯示最後10行
            output += f"  {line}\n"
        return output


# ==================== Agent 管理界面 ====================

class AgentManagementUI:
    """
    Agent 管理界面

    提供 Agent 的創建、配置和管理功能
    """

    def __init__(self):
        """初始化管理界面"""
        self.agents: Dict[str, Dict] = {}

    def create_agent_form(self) -> Dict:
        """創建 Agent 表單"""
        form = {
            "title": "創建新 Agent",
            "fields": [
                {
                    "name": "agent_name",
                    "label": "Agent 名稱",
                    "type": "text",
                    "required": True
                },
                {
                    "name": "description",
                    "label": "描述",
                    "type": "textarea",
                    "required": True
                },
                {
                    "name": "role",
                    "label": "角色",
                    "type": "select",
                    "options": ["researcher", "analyst", "writer", "developer"],
                    "required": True
                },
                {
                    "name": "goals",
                    "label": "目標",
                    "type": "list",
                    "required": True
                },
                {
                    "name": "tools",
                    "label": "工具",
                    "type": "multiselect",
                    "options": [
                        "GoogleSearchTool",
                        "FileReadTool",
                        "FileWriteTool",
                        "DataAnalysisTool"
                    ],
                    "required": False
                },
                {
                    "name": "max_iterations",
                    "label": "最大迭代次數",
                    "type": "number",
                    "default": 25,
                    "min": 1,
                    "max": 100
                },
                {
                    "name": "budget",
                    "label": "預算 (USD)",
                    "type": "number",
                    "default": 10.0,
                    "min": 0.1,
                    "max": 1000.0
                }
            ],
            "actions": [
                {"label": "創建", "action": "submit"},
                {"label": "取消", "action": "cancel"}
            ]
        }

        return form

    def display_agent_list(self) -> str:
        """顯示 Agent 列表"""
        output = "\n" + "=" * 80 + "\n"
        output += "Agent 列表\n"
        output += "=" * 80 + "\n\n"

        if not self.agents:
            output += "  (沒有 Agent)\n"
        else:
            # 表頭
            output += f"{'ID':15s} {'名稱':20s} {'狀態':10s} {'任務':8s} {'進度':8s}\n"
            output += "-" * 80 + "\n"

            # 數據行
            for agent_id, agent in self.agents.items():
                output += f"{agent_id:15s} "
                output += f"{agent['name']:20s} "
                output += f"{agent['status']:10s} "
                output += f"{agent['tasks']:8s} "
                output += f"{agent['progress']:8s}\n"

        return output

    def display_agent_details(self, agent_id: str) -> str:
        """顯示 Agent 詳情"""
        if agent_id not in self.agents:
            return f"❌ Agent {agent_id} 不存在"

        agent = self.agents[agent_id]

        output = "\n" + "=" * 80 + "\n"
        output += f"Agent 詳情: {agent['name']}\n"
        output += "=" * 80 + "\n\n"

        sections = [
            ("基本信息", {
                "ID": agent_id,
                "名稱": agent['name'],
                "描述": agent['description'],
                "狀態": agent['status']
            }),
            ("配置", {
                "角色": agent['role'],
                "最大迭代": agent['max_iterations'],
                "預算": f"${agent['budget']}",
                "工具": ", ".join(agent['tools'])
            }),
            ("執行統計", {
                "已執行任務": agent['completed_tasks'],
                "失敗任務": agent['failed_tasks'],
                "總成本": f"${agent['total_cost']:.2f}",
                "平均執行時間": f"{agent['avg_execution_time']}s"
            })
        ]

        for title, data in sections:
            output += f"▶ {title}\n"
            for key, value in data.items():
                output += f"  {key:20s}: {value}\n"
            output += "\n"

        return output


# ==================== 監控界面 ====================

class MonitoringUI:
    """
    監控界面

    實時監控系統狀態和性能
    """

    def __init__(self):
        """初始化監控界面"""
        self.metrics: List[Dict] = []

    def create_monitoring_dashboard(self) -> Dashboard:
        """創建監控儀表板"""
        dashboard = Dashboard("monitoring", "系統監控")

        # 系統概覽
        dashboard.add_widget(DashboardWidget(
            widget_id="system_overview",
            widget_type="stat",
            title="系統概覽",
            data={
                "活躍 Agents": 12,
                "運行任務": 45,
                "今日 API 調用": 1250,
                "今日成本": "$23.45"
            }
        ))

        # 性能圖表
        dashboard.add_widget(DashboardWidget(
            widget_id="performance_chart",
            widget_type="chart",
            title="API 調用趨勢",
            data={
                "type": "bar",
                "values": [
                    ("00:00", 50),
                    ("04:00", 30),
                    ("08:00", 120),
                    ("12:00", 200),
                    ("16:00", 150),
                    ("20:00", 80)
                ]
            }
        ))

        # Agent 狀態表
        dashboard.add_widget(DashboardWidget(
            widget_id="agent_status",
            widget_type="table",
            title="Agent 狀態",
            data=[
                {"Agent": "DataBot", "狀態": "運行中", "任務": "3/5", "CPU": "45%"},
                {"Agent": "ResearchAI", "狀態": "等待中", "任務": "0/3", "CPU": "0%"},
                {"Agent": "CodeGen", "狀態": "完成", "任務": "5/5", "CPU": "2%"}
            ]
        ))

        # 系統日誌
        dashboard.add_widget(DashboardWidget(
            widget_id="system_log",
            widget_type="log",
            title="系統日誌",
            data=[
                "[14:23:45] INFO: Agent DataBot started",
                "[14:23:52] INFO: Task completed successfully",
                "[14:24:01] WARNING: API rate limit approaching",
                "[14:24:15] INFO: Memory consolidation completed",
                "[14:24:30] ERROR: Tool execution failed: timeout"
            ]
        ))

        return dashboard

    def create_cost_dashboard(self) -> Dashboard:
        """創建成本分析儀表板"""
        dashboard = Dashboard("cost_analysis", "成本分析")

        # 成本概覽
        dashboard.add_widget(DashboardWidget(
            widget_id="cost_overview",
            widget_type="stat",
            title="成本概覽",
            data={
                "今日成本": "$23.45",
                "本週成本": "$156.78",
                "本月成本": "$678.90",
                "預算使用率": "67.9%"
            }
        ))

        # 成本分解
        dashboard.add_widget(DashboardWidget(
            widget_id="cost_breakdown",
            widget_type="chart",
            title="成本分解",
            data={
                "type": "bar",
                "values": [
                    ("LLM API", 180),
                    ("工具執行", 50),
                    ("存儲", 20),
                    ("網絡", 10),
                    ("其他", 5)
                ]
            }
        ))

        return dashboard


# ==================== 配置界面 ====================

class ConfigurationUI:
    """
    配置界面

    管理系統配置
    """

    def __init__(self):
        """初始化配置界面"""
        self.config: Dict = {}

    def display_config_form(self) -> Dict:
        """顯示配置表單"""
        return {
            "title": "系統配置",
            "sections": [
                {
                    "title": "API 設置",
                    "fields": [
                        {
                            "name": "openai_api_key",
                            "label": "OpenAI API Key",
                            "type": "password"
                        },
                        {
                            "name": "api_base_url",
                            "label": "API Base URL",
                            "type": "text",
                            "default": "https://api.openai.com/v1"
                        }
                    ]
                },
                {
                    "title": "默認設置",
                    "fields": [
                        {
                            "name": "default_model",
                            "label": "默認模型",
                            "type": "select",
                            "options": ["gpt-4", "gpt-3.5-turbo"]
                        },
                        {
                            "name": "default_max_iterations",
                            "label": "默認最大迭代",
                            "type": "number",
                            "default": 25
                        },
                        {
                            "name": "default_budget",
                            "label": "默認預算",
                            "type": "number",
                            "default": 10.0
                        }
                    ]
                },
                {
                    "title": "資源限制",
                    "fields": [
                        {
                            "name": "max_agents_per_user",
                            "label": "每用戶最大 Agents",
                            "type": "number",
                            "default": 10
                        },
                        {
                            "name": "api_rate_limit",
                            "label": "API 調用限額 (每分鐘)",
                            "type": "number",
                            "default": 100
                        }
                    ]
                }
            ]
        }

    def display_settings(self) -> str:
        """顯示當前設置"""
        form = self.display_config_form()

        output = "\n" + "=" * 80 + "\n"
        output += "系統設置\n"
        output += "=" * 80 + "\n\n"

        for section in form["sections"]:
            output += f"▶ {section['title']}\n"

            for field in section["fields"]:
                value = self.config.get(field["name"], field.get("default", ""))
                if field["type"] == "password":
                    value = "*" * 10

                output += f"  {field['label']:30s}: {value}\n"

            output += "\n"

        return output


# ==================== 報告生成器 ====================

class ReportGenerator:
    """
    報告生成器

    生成各種可視化報告
    """

    def __init__(self):
        """初始化報告生成器"""
        pass

    def generate_execution_report(
        self,
        agent_id: str,
        execution_data: Dict
    ) -> str:
        """生成執行報告"""
        report = "\n" + "=" * 80 + "\n"
        report += f"Agent 執行報告\n"
        report += "=" * 80 + "\n\n"

        report += f"Agent ID: {agent_id}\n"
        report += f"執行時間: {execution_data.get('execution_time', 0)}s\n"
        report += f"狀態: {execution_data.get('status', 'unknown')}\n\n"

        report += "▶ 任務執行\n"
        tasks = execution_data.get('tasks', [])
        report += f"  總任務: {len(tasks)}\n"
        report += f"  完成: {sum(1 for t in tasks if t['status'] == 'completed')}\n"
        report += f"  失敗: {sum(1 for t in tasks if t['status'] == 'failed')}\n\n"

        report += "▶ 資源使用\n"
        report += f"  API 調用: {execution_data.get('api_calls', 0)}\n"
        report += f"  Tokens: {execution_data.get('tokens', 0)}\n"
        report += f"  成本: ${execution_data.get('cost', 0):.4f}\n\n"

        report += "▶ 性能指標\n"
        report += f"  平均響應時間: {execution_data.get('avg_response_time', 0):.2f}s\n"
        report += f"  成功率: {execution_data.get('success_rate', 0):.1%}\n"

        return report

    def generate_analytics_report(self, period: str = "daily") -> str:
        """生成分析報告"""
        report = "\n" + "=" * 80 + "\n"
        report += f"分析報告 ({period})\n"
        report += "=" * 80 + "\n\n"

        report += "▶ 使用統計\n"
        report += f"  活躍用戶: 25\n"
        report += f"  創建的 Agents: 45\n"
        report += f"  執行的任務: 230\n"
        report += f"  API 調用: 1,250\n\n"

        report += "▶ 成本分析\n"
        report += f"  總成本: $156.78\n"
        report += f"  平均每 Agent: $3.48\n"
        report += f"  平均每任務: $0.68\n\n"

        report += "▶ 性能指標\n"
        report += f"  平均執行時間: 45.2s\n"
        report += f"  成功率: 94.3%\n"
        report += f"  錯誤率: 5.7%\n"

        return report


# ==================== 示例場景 ====================

def example_1_dashboard():
    """示例 1: 儀表板"""
    print("\n" + "=" * 60)
    print("示例 1: 創建和顯示儀表板")
    print("=" * 60)

    # 創建監控儀表板
    monitoring = MonitoringUI()
    dashboard = monitoring.create_monitoring_dashboard()

    # 顯示儀表板
    print(dashboard.render())


def example_2_agent_management():
    """示例 2: Agent 管理界面"""
    print("\n" + "=" * 60)
    print("示例 2: Agent 管理界面")
    print("=" * 60)

    ui = AgentManagementUI()

    # 模擬一些 Agents
    ui.agents = {
        "agent_1": {
            "name": "DataBot",
            "description": "數據處理 Agent",
            "status": "running",
            "role": "analyst",
            "tasks": "3/5",
            "progress": "60%",
            "max_iterations": 25,
            "budget": 10.0,
            "tools": ["FileReadTool", "DataAnalysisTool"],
            "completed_tasks": 42,
            "failed_tasks": 3,
            "total_cost": 8.45,
            "avg_execution_time": 45.2
        },
        "agent_2": {
            "name": "ResearchAI",
            "description": "研究助手",
            "status": "idle",
            "role": "researcher",
            "tasks": "0/3",
            "progress": "0%",
            "max_iterations": 20,
            "budget": 5.0,
            "tools": ["GoogleSearchTool", "WebScraperTool"],
            "completed_tasks": 15,
            "failed_tasks": 1,
            "total_cost": 3.21,
            "avg_execution_time": 32.1
        }
    }

    # 顯示 Agent 列表
    print(ui.display_agent_list())

    # 顯示 Agent 詳情
    print(ui.display_agent_details("agent_1"))


def example_3_cost_dashboard():
    """示例 3: 成本分析儀表板"""
    print("\n" + "=" * 60)
    print("示例 3: 成本分析儀表板")
    print("=" * 60)

    monitoring = MonitoringUI()
    dashboard = monitoring.create_cost_dashboard()

    print(dashboard.render())


def example_4_configuration():
    """示例 4: 配置界面"""
    print("\n" + "=" * 60)
    print("示例 4: 配置界面")
    print("=" * 60)

    config_ui = ConfigurationUI()

    # 設置一些配置
    config_ui.config = {
        "openai_api_key": "sk-xxxxxxxxxxxxx",
        "api_base_url": "https://api.openai.com/v1",
        "default_model": "gpt-4",
        "default_max_iterations": 25,
        "default_budget": 10.0,
        "max_agents_per_user": 10,
        "api_rate_limit": 100
    }

    # 顯示配置
    print(config_ui.display_settings())


def example_5_reports():
    """示例 5: 報告生成"""
    print("\n" + "=" * 60)
    print("示例 5: 報告生成")
    print("=" * 60)

    generator = ReportGenerator()

    # 生成執行報告
    execution_data = {
        "execution_time": 145.3,
        "status": "completed",
        "tasks": [
            {"id": "t1", "status": "completed"},
            {"id": "t2", "status": "completed"},
            {"id": "t3", "status": "failed"}
        ],
        "api_calls": 15,
        "tokens": 5420,
        "cost": 0.245,
        "avg_response_time": 2.3,
        "success_rate": 0.867
    }

    print(generator.generate_execution_report("agent_123", execution_data))

    # 生成分析報告
    print(generator.generate_analytics_report("weekly"))


# ==================== 主函數 ====================

def main():
    """主函數"""
    print("\n" + "🖥️  " * 20)
    print("SuperAGI GUI 操作教程")
    print("🖥️  " * 20)

    try:
        # 示例 1: 儀表板
        example_1_dashboard()

        # 示例 2: Agent 管理
        example_2_agent_management()

        # 示例 3: 成本分析
        example_3_cost_dashboard()

        # 示例 4: 配置
        example_4_configuration()

        # 示例 5: 報告
        example_5_reports()

        print("\n" + "=" * 60)
        print("✅ 所有 GUI 操作示例執行完成！")
        print("=" * 60)

        print("""
        GUI 使用最佳實踐:

        1. 使用儀表板集中顯示關鍵指標
        2. 實時更新監控數據
        3. 提供直觀的可視化圖表
        4. 設計清晰的導航結構
        5. 實現響應式布局
        6. 添加搜索和過濾功能
        7. 提供批量操作選項
        8. 定期生成分析報告

        實際使用 SuperAGI GUI:
        1. 啟動服務: python run.py
        2. 訪問: http://localhost:8000
        3. 登錄並開始使用
        """)

    except Exception as e:
        print(f"\n❌ 執行出錯: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

"""
Magentic-One 架構概述
===================================

本範例展示 Magentic-One 的整體架構、核心組件和工作原理。

Magentic-One 是一個模組化的多 Agent 系統，由以下核心組件組成：
1. Orchestrator - 中央協調者
2. WebSurfer - 網頁瀏覽 Agent
3. FileSurfer - 文件操作 Agent
4. Coder - 代碼生成 Agent
5. ComputerTerminal - 終端執行 Agent
"""

import os
from typing import Dict, List, Any
import json
from datetime import datetime


class MagenticOneArchitecture:
    """Magentic-One 架構示範類別"""

    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化 Magentic-One 架構

        Args:
            config: 配置字典
        """
        self.config = config or self._default_config()
        self.agents = {}
        self.orchestrator = None
        self.task_history = []

    def _default_config(self) -> Dict[str, Any]:
        """返回默認配置"""
        return {
            "llm_config": {
                "model": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 2000
            },
            "orchestrator": {
                "max_rounds": 30,
                "timeout": 600,
                "planning_strategy": "hierarchical"
            },
            "agents": {
                "web_surfer": {
                    "enabled": True,
                    "headless": True,
                    "timeout": 30
                },
                "file_surfer": {
                    "enabled": True,
                    "work_dir": "./workspace",
                    "max_file_size": 100 * 1024 * 1024  # 100MB
                },
                "coder": {
                    "enabled": True,
                    "use_docker": True,
                    "allowed_languages": ["python", "javascript", "bash"]
                },
                "terminal": {
                    "enabled": False,  # 默認禁用以提高安全性
                    "allowed_commands": ["ls", "pwd", "echo"]
                }
            }
        }

    def initialize_agents(self):
        """初始化所有 Agent"""
        print("初始化 Magentic-One Agent 系統...")

        # 1. 初始化 Orchestrator（核心協調者）
        self.orchestrator = OrchestratorAgent(
            name="Orchestrator",
            config=self.config["orchestrator"],
            llm_config=self.config["llm_config"]
        )
        print(f"✓ {self.orchestrator.name} 已初始化")

        # 2. 初始化專門化 Agents
        agent_configs = self.config["agents"]

        if agent_configs["web_surfer"]["enabled"]:
            self.agents["web_surfer"] = WebSurferAgent(
                name="WebSurfer",
                config=agent_configs["web_surfer"],
                llm_config=self.config["llm_config"]
            )
            print(f"✓ {self.agents['web_surfer'].name} 已初始化")

        if agent_configs["file_surfer"]["enabled"]:
            self.agents["file_surfer"] = FileSurferAgent(
                name="FileSurfer",
                config=agent_configs["file_surfer"],
                llm_config=self.config["llm_config"]
            )
            print(f"✓ {self.agents['file_surfer'].name} 已初始化")

        if agent_configs["coder"]["enabled"]:
            self.agents["coder"] = CoderAgent(
                name="Coder",
                config=agent_configs["coder"],
                llm_config=self.config["llm_config"]
            )
            print(f"✓ {self.agents['coder'].name} 已初始化")

        if agent_configs["terminal"]["enabled"]:
            self.agents["terminal"] = TerminalAgent(
                name="Terminal",
                config=agent_configs["terminal"],
                llm_config=self.config["llm_config"]
            )
            print(f"✓ {self.agents['terminal'].name} 已初始化")

        # 3. 將 Agents 註冊到 Orchestrator
        self.orchestrator.register_agents(self.agents)
        print(f"\n總共初始化了 {len(self.agents)} 個專門化 Agent")

    def execute_task(self, task: str) -> Dict[str, Any]:
        """
        執行任務

        Args:
            task: 任務描述

        Returns:
            執行結果
        """
        print(f"\n{'='*60}")
        print(f"開始執行任務: {task}")
        print(f"{'='*60}\n")

        # 記錄任務開始時間
        start_time = datetime.now()

        # 1. Orchestrator 分析任務
        print("階段 1: 任務分析")
        task_plan = self.orchestrator.analyze_task(task)
        print(f"任務已分解為 {len(task_plan['steps'])} 個步驟")

        # 2. 顯示執行計劃
        print("\n階段 2: 執行計劃")
        for i, step in enumerate(task_plan['steps'], 1):
            print(f"  步驟 {i}: {step['description']}")
            print(f"    指派給: {step['agent']}")

        # 3. 執行任務
        print("\n階段 3: 任務執行")
        results = []
        for i, step in enumerate(task_plan['steps'], 1):
            print(f"\n執行步驟 {i}/{len(task_plan['steps'])}: {step['description']}")

            agent_name = step['agent']
            if agent_name in self.agents:
                agent = self.agents[agent_name]
                result = agent.execute(step['action'])
                results.append({
                    'step': i,
                    'agent': agent_name,
                    'result': result
                })
                print(f"✓ 步驟 {i} 完成")
            else:
                print(f"✗ Agent '{agent_name}' 不可用")

        # 4. 整合結果
        print("\n階段 4: 結果整合")
        final_result = self.orchestrator.integrate_results(results)

        # 記錄任務結束時間
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # 5. 生成任務報告
        task_report = {
            'task': task,
            'status': 'completed',
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration': duration,
            'steps_executed': len(results),
            'results': final_result
        }

        self.task_history.append(task_report)

        print(f"\n{'='*60}")
        print(f"任務完成！總耗時: {duration:.2f} 秒")
        print(f"{'='*60}\n")

        return task_report

    def get_system_status(self) -> Dict[str, Any]:
        """獲取系統狀態"""
        return {
            'orchestrator': self.orchestrator.get_status() if self.orchestrator else None,
            'agents': {
                name: agent.get_status()
                for name, agent in self.agents.items()
            },
            'tasks_completed': len(self.task_history)
        }


class BaseAgent:
    """Agent 基礎類別"""

    def __init__(self, name: str, config: Dict, llm_config: Dict):
        self.name = name
        self.config = config
        self.llm_config = llm_config
        self.task_count = 0

    def execute(self, action: Dict) -> Any:
        """執行操作（子類需實現）"""
        raise NotImplementedError

    def get_status(self) -> Dict:
        """獲取 Agent 狀態"""
        return {
            'name': self.name,
            'tasks_completed': self.task_count,
            'status': 'active'
        }


class OrchestratorAgent(BaseAgent):
    """協調者 Agent - 負責任務規劃和協調"""

    def __init__(self, name: str, config: Dict, llm_config: Dict):
        super().__init__(name, config, llm_config)
        self.registered_agents = {}
        self.current_plan = None

    def register_agents(self, agents: Dict[str, BaseAgent]):
        """註冊可用的 Agents"""
        self.registered_agents = agents

    def analyze_task(self, task: str) -> Dict:
        """分析並分解任務"""
        # 這裡簡化處理，實際會使用 LLM 進行智能分析
        print(f"{self.name}: 正在分析任務...")

        # 示例：根據關鍵字判斷需要哪些 Agent
        steps = []

        if any(keyword in task.lower() for keyword in ['搜索', '查找', '網頁', 'search']):
            steps.append({
                'description': '網頁搜索和信息提取',
                'agent': 'web_surfer',
                'action': {'type': 'search', 'query': task}
            })

        if any(keyword in task.lower() for keyword in ['文件', '讀取', '保存', 'file']):
            steps.append({
                'description': '文件操作',
                'agent': 'file_surfer',
                'action': {'type': 'file_operation', 'task': task}
            })

        if any(keyword in task.lower() for keyword in ['代碼', '編程', 'code', 'program']):
            steps.append({
                'description': '代碼生成',
                'agent': 'coder',
                'action': {'type': 'generate_code', 'requirement': task}
            })

        self.current_plan = {
            'task': task,
            'steps': steps,
            'created_at': datetime.now().isoformat()
        }

        return self.current_plan

    def integrate_results(self, results: List[Dict]) -> Dict:
        """整合各 Agent 的執行結果"""
        print(f"{self.name}: 正在整合結果...")

        integrated = {
            'summary': f'成功執行了 {len(results)} 個步驟',
            'details': results,
            'status': 'success'
        }

        return integrated


class WebSurferAgent(BaseAgent):
    """網頁瀏覽 Agent"""

    def execute(self, action: Dict) -> Dict:
        """執行網頁瀏覽操作"""
        self.task_count += 1
        print(f"  {self.name}: 執行 {action['type']} 操作")

        # 模擬網頁瀏覽
        return {
            'status': 'success',
            'data': f"已完成網頁搜索: {action.get('query', 'N/A')}"
        }


class FileSurferAgent(BaseAgent):
    """文件操作 Agent"""

    def execute(self, action: Dict) -> Dict:
        """執行文件操作"""
        self.task_count += 1
        print(f"  {self.name}: 執行 {action['type']} 操作")

        # 模擬文件操作
        return {
            'status': 'success',
            'data': f"已完成文件操作: {action.get('task', 'N/A')}"
        }


class CoderAgent(BaseAgent):
    """代碼生成 Agent"""

    def execute(self, action: Dict) -> Dict:
        """執行代碼生成"""
        self.task_count += 1
        print(f"  {self.name}: 執行 {action['type']} 操作")

        # 模擬代碼生成
        return {
            'status': 'success',
            'code': f"# 生成的代碼: {action.get('requirement', 'N/A')}"
        }


class TerminalAgent(BaseAgent):
    """終端執行 Agent"""

    def execute(self, action: Dict) -> Dict:
        """執行終端命令"""
        self.task_count += 1
        print(f"  {self.name}: 執行 {action['type']} 操作")

        # 模擬終端執行
        return {
            'status': 'success',
            'output': f"命令執行完成: {action.get('command', 'N/A')}"
        }


def demo_basic_architecture():
    """示範基礎架構"""
    print("=" * 60)
    print("範例 1: Magentic-One 基礎架構")
    print("=" * 60)

    # 創建 Magentic-One 系統
    magentic = MagenticOneArchitecture()

    # 初始化 Agents
    magentic.initialize_agents()

    # 查看系統狀態
    print("\n系統狀態:")
    status = magentic.get_system_status()
    print(json.dumps(status, indent=2, ensure_ascii=False))


def demo_task_execution():
    """示範任務執行"""
    print("\n" + "=" * 60)
    print("範例 2: 任務執行流程")
    print("=" * 60)

    # 創建系統
    magentic = MagenticOneArchitecture()
    magentic.initialize_agents()

    # 執行任務
    task = "搜索 Python 最新版本信息，生成代碼範例，並保存到文件"
    result = magentic.execute_task(task)

    # 顯示結果
    print("\n任務執行結果:")
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))


def demo_custom_configuration():
    """示範自定義配置"""
    print("\n" + "=" * 60)
    print("範例 3: 自定義配置")
    print("=" * 60)

    # 自定義配置
    custom_config = {
        "llm_config": {
            "model": "gpt-4-turbo",
            "temperature": 0.5,
            "max_tokens": 3000
        },
        "orchestrator": {
            "max_rounds": 50,
            "timeout": 900,
            "planning_strategy": "parallel"
        },
        "agents": {
            "web_surfer": {
                "enabled": True,
                "headless": False,  # 顯示瀏覽器
                "timeout": 60
            },
            "file_surfer": {
                "enabled": True,
                "work_dir": "/tmp/workspace",
                "max_file_size": 50 * 1024 * 1024
            },
            "coder": {
                "enabled": True,
                "use_docker": True,
                "allowed_languages": ["python", "javascript"]
            },
            "terminal": {
                "enabled": True,  # 啟用終端
                "allowed_commands": ["ls", "pwd", "cat", "grep"]
            }
        }
    }

    # 使用自定義配置創建系統
    magentic = MagenticOneArchitecture(config=custom_config)
    magentic.initialize_agents()

    print("\n自定義配置已應用")
    print(f"已啟用 Agent 數量: {len(magentic.agents)}")


def demo_architecture_diagram():
    """顯示架構圖"""
    print("\n" + "=" * 60)
    print("Magentic-One 架構圖")
    print("=" * 60)

    diagram = """

    ┌─────────────────────────────────────────────────────────┐
    │                      User Task                          │
    └────────────────────┬────────────────────────────────────┘
                         │
                         ▼
    ┌─────────────────────────────────────────────────────────┐
    │                   Orchestrator                          │
    │  • 任務分析和分解                                         │
    │  • 制定執行計劃                                           │
    │  • 分配子任務                                            │
    │  • 監控和協調                                            │
    │  • 結果整合                                              │
    └─────┬───────┬───────┬───────┬───────────────────────────┘
          │       │       │       │
    ┌─────▼──┐ ┌──▼────┐ ┌▼─────┐ ┌▼────────────┐
    │ Web    │ │ File  │ │Coder │ │ Computer    │
    │ Surfer │ │Surfer │ │      │ │ Terminal    │
    └────────┘ └───────┘ └──────┘ └─────────────┘

    WebSurfer (網頁瀏覽器):
    • 網頁導航和搜索
    • 信息提取
    • 表單交互
    • 內容截圖

    FileSurfer (文件瀏覽器):
    • 文件讀寫
    • 目錄操作
    • 格式轉換
    • 內容搜索

    Coder (編碼者):
    • 代碼生成
    • 代碼執行
    • 調試和優化
    • 測試創建

    ComputerTerminal (終端):
    • 系統命令執行
    • 腳本運行
    • 環境管理
    • 進程控制

    協作模式:
    1. 順序執行: Task → A1 → A2 → A3 → Result
    2. 並行執行: Task → [A1, A2, A3] → Merge → Result
    3. 迭代執行: Task → A1 ⇄ A2 ⇄ A3 → Result
    """

    print(diagram)


if __name__ == "__main__":
    # 運行所有示範
    demo_basic_architecture()
    demo_task_execution()
    demo_custom_configuration()
    demo_architecture_diagram()

    print("\n" + "=" * 60)
    print("架構概述完成！")
    print("=" * 60)

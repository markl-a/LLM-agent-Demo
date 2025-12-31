#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SWE-Agent 快速開始範例
=====================

這個範例展示了如何使用 SWE-Agent 框架的基本功能：
1. 初始化 Agent
2. 配置 LLM 模型
3. 創建執行環境
4. 解決簡單的程式碼問題
5. 查看結果和日誌

SWE-Agent 是專為軟體工程任務設計的 AI Agent，能夠自動解決 GitHub Issues、
修復 Bug、生成測試等。這個範例會帶你完成第一個 SWE-Agent 任務。

作者: SWE-Agent 團隊
日期: 2025-12-31
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
import json
from datetime import datetime

# SWE-Agent 核心導入
try:
    from sweagent import SWEAgent
    from sweagent.environment import DockerEnvironment, LocalEnvironment
    from sweagent.task import Task, TaskResult
    from sweagent.config import AgentConfig, EnvironmentConfig
    from sweagent.models import OpenAIModel, AnthropicModel
except ImportError:
    print("請先安裝 SWE-Agent: pip install sweagent")
    sys.exit(1)

# 日誌和顯示
from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.syntax import Syntax


class QuickStartGuide:
    """
    快速開始指南類

    這個類封裝了 SWE-Agent 的基本使用流程，幫助新用戶快速上手。
    提供了多個簡單的範例，從最基礎的配置到執行第一個任務。
    """

    def __init__(self):
        """初始化快速開始指南"""
        self.console = Console()
        self.results = []

        # 配置日誌
        logger.remove()
        logger.add(
            "logs/quickstart_{time}.log",
            rotation="1 day",
            retention="7 days",
            level="INFO"
        )
        logger.add(sys.stdout, level="INFO")

    def print_welcome(self):
        """顯示歡迎信息"""
        welcome_text = """
        🤖 歡迎使用 SWE-Agent！

        SWE-Agent 是一個強大的軟體工程 AI Agent 框架，
        專門設計用於自動化軟體開發任務。

        本快速開始指南將帶你：
        ✓ 配置你的第一個 Agent
        ✓ 創建執行環境
        ✓ 運行簡單的程式碼任務
        ✓ 理解結果輸出
        """

        self.console.print(Panel(
            welcome_text,
            title="SWE-Agent 快速開始",
            border_style="green"
        ))

    def check_prerequisites(self) -> bool:
        """
        檢查前置條件

        Returns:
            bool: 是否所有前置條件都滿足
        """
        self.console.print("\n[bold]檢查前置條件...[/bold]")

        checks = {
            "Python 版本": sys.version_info >= (3, 8),
            "Docker 可用": self._check_docker(),
            "API 金鑰配置": self._check_api_keys(),
            "網路連接": self._check_network()
        }

        table = Table(title="前置條件檢查")
        table.add_column("項目", style="cyan")
        table.add_column("狀態", style="magenta")

        for check, result in checks.items():
            status = "✓ 通過" if result else "✗ 失敗"
            style = "green" if result else "red"
            table.add_row(check, f"[{style}]{status}[/{style}]")

        self.console.print(table)

        return all(checks.values())

    def _check_docker(self) -> bool:
        """檢查 Docker 是否可用"""
        try:
            import docker
            client = docker.from_env()
            client.ping()
            return True
        except Exception as e:
            logger.warning(f"Docker 檢查失敗: {e}")
            return False

    def _check_api_keys(self) -> bool:
        """檢查 API 金鑰是否配置"""
        return bool(
            os.getenv("OPENAI_API_KEY") or
            os.getenv("ANTHROPIC_API_KEY")
        )

    def _check_network(self) -> bool:
        """檢查網路連接"""
        try:
            import requests
            response = requests.get("https://api.openai.com", timeout=5)
            return True
        except:
            return False

    def example1_basic_initialization(self):
        """
        範例 1: 基本初始化

        展示如何創建和配置一個基本的 SWE-Agent 實例。
        這是使用 SWE-Agent 的第一步。
        """
        self.console.print("\n[bold cyan]範例 1: 基本初始化[/bold cyan]")

        try:
            # 配置 Agent
            config = AgentConfig(
                model_name="gpt-4",  # 使用 GPT-4 模型
                api_key=os.getenv("OPENAI_API_KEY"),
                temperature=0.2,  # 較低的溫度使輸出更確定
                max_iterations=10,  # 限制最大迭代次數
                verbose=True  # 啟用詳細輸出
            )

            # 創建 Agent 實例
            agent = SWEAgent(config=config)

            self.console.print("[green]✓ Agent 初始化成功！[/green]")
            self.console.print(f"  模型: {config.model_name}")
            self.console.print(f"  溫度: {config.temperature}")
            self.console.print(f"  最大迭代: {config.max_iterations}")

            logger.info("Agent 初始化成功")
            return agent

        except Exception as e:
            self.console.print(f"[red]✗ 初始化失敗: {e}[/red]")
            logger.error(f"Agent 初始化失敗: {e}")
            return None

    def example2_create_environment(self):
        """
        範例 2: 創建執行環境

        SWE-Agent 需要一個執行環境來運行程式碼。
        這個範例展示如何創建 Docker 和本地環境。
        """
        self.console.print("\n[bold cyan]範例 2: 創建執行環境[/bold cyan]")

        # 方式 1: Docker 環境（推薦）
        try:
            docker_config = EnvironmentConfig(
                type="docker",
                image="python:3.9-slim",
                workspace="/workspace",
                timeout=300
            )

            docker_env = DockerEnvironment(config=docker_config)

            self.console.print("[green]✓ Docker 環境創建成功[/green]")
            self.console.print(f"  映像: {docker_config.image}")
            self.console.print(f"  工作目錄: {docker_config.workspace}")

        except Exception as e:
            self.console.print(f"[yellow]⚠ Docker 環境創建失敗: {e}[/yellow]")
            docker_env = None

        # 方式 2: 本地環境（用於測試）
        try:
            local_config = EnvironmentConfig(
                type="local",
                workspace="/tmp/swe-agent-workspace",
                timeout=60
            )

            local_env = LocalEnvironment(config=local_config)

            self.console.print("[green]✓ 本地環境創建成功[/green]")
            self.console.print(f"  工作目錄: {local_config.workspace}")

        except Exception as e:
            self.console.print(f"[red]✗ 本地環境創建失敗: {e}[/red]")
            local_env = None

        return docker_env or local_env

    def example3_simple_task(self, agent: SWEAgent, environment):
        """
        範例 3: 執行簡單任務

        展示如何定義和執行一個簡單的程式碼修復任務。

        Args:
            agent: SWE-Agent 實例
            environment: 執行環境
        """
        self.console.print("\n[bold cyan]範例 3: 執行簡單任務[/bold cyan]")

        if not agent or not environment:
            self.console.print("[red]需要先創建 Agent 和環境[/red]")
            return None

        # 創建一個簡單的任務：修復 Python 語法錯誤
        task_description = """
        修復以下 Python 程式碼中的語法錯誤：

        ```python
        def calculate_sum(numbers)
            total = 0
            for num in numbers:
                total += num
            return total
        ```

        錯誤：缺少冒號
        """

        task = Task(
            description=task_description,
            task_type="bug_fix",
            priority="high",
            expected_files=["fix.py"]
        )

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task_progress = progress.add_task(
                    "執行任務中...",
                    total=None
                )

                # 執行任務
                result = agent.run_task(task, environment)

                progress.update(task_progress, completed=True)

            # 顯示結果
            self._display_task_result(result)

            return result

        except Exception as e:
            self.console.print(f"[red]✗ 任務執行失敗: {e}[/red]")
            logger.error(f"任務執行失敗: {e}")
            return None

    def example4_code_search(self, agent: SWEAgent):
        """
        範例 4: 程式碼搜索

        展示如何使用 Agent 的程式碼搜索功能來定位相關檔案。
        """
        self.console.print("\n[bold cyan]範例 4: 程式碼搜索[/bold cyan]")

        if not agent:
            return None

        # 搜索包含特定函數的檔案
        search_query = {
            "pattern": "def calculate_*",
            "file_types": [".py"],
            "max_results": 10
        }

        try:
            results = agent.search_code(
                pattern=search_query["pattern"],
                file_types=search_query["file_types"]
            )

            self.console.print(f"[green]找到 {len(results)} 個匹配結果[/green]")

            for i, result in enumerate(results[:5], 1):
                self.console.print(f"\n  {i}. {result['file']}")
                self.console.print(f"     行 {result['line']}: {result['content']}")

            return results

        except Exception as e:
            self.console.print(f"[red]搜索失敗: {e}[/red]")
            return None

    def example5_with_tests(self, agent: SWEAgent, environment):
        """
        範例 5: 帶測試的任務

        展示如何創建包含測試驗證的任務。
        """
        self.console.print("\n[bold cyan]範例 5: 帶測試的任務[/bold cyan]")

        # 定義帶測試的任務
        task = Task(
            description="實現一個計算列表平均值的函數",
            test_command="pytest test_average.py",
            test_file_content="""
import pytest
from solution import calculate_average

def test_average():
    assert calculate_average([1, 2, 3, 4, 5]) == 3.0
    assert calculate_average([10, 20]) == 15.0
    assert calculate_average([5]) == 5.0

def test_empty_list():
    with pytest.raises(ValueError):
        calculate_average([])
"""
        )

        try:
            result = agent.run_task_with_tests(task, environment)

            self.console.print(f"\n測試結果:")
            self.console.print(f"  通過: {result.tests_passed}")
            self.console.print(f"  失敗: {result.tests_failed}")
            self.console.print(f"  總計: {result.tests_total}")

            if result.tests_passed == result.tests_total:
                self.console.print("[green]✓ 所有測試通過！[/green]")
            else:
                self.console.print("[yellow]⚠ 部分測試失敗[/yellow]")

            return result

        except Exception as e:
            self.console.print(f"[red]執行失敗: {e}[/red]")
            return None

    def _display_task_result(self, result: TaskResult):
        """
        顯示任務執行結果

        Args:
            result: 任務結果對象
        """
        # 創建結果面板
        result_info = f"""
        狀態: {result.status}
        耗時: {result.duration:.2f} 秒
        迭代次數: {result.iterations}
        修改的檔案: {len(result.modified_files)}
        """

        self.console.print(Panel(
            result_info,
            title="任務結果",
            border_style="green" if result.status == "success" else "red"
        ))

        # 顯示生成的程式碼
        if result.generated_code:
            self.console.print("\n[bold]生成的程式碼:[/bold]")
            syntax = Syntax(
                result.generated_code,
                "python",
                theme="monokai",
                line_numbers=True
            )
            self.console.print(syntax)

    def save_results(self):
        """保存所有範例的執行結果"""
        output_dir = Path("outputs/quickstart")
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

        self.console.print(f"\n[green]結果已保存到: {output_file}[/green]")

    def run_all_examples(self):
        """運行所有範例"""
        self.print_welcome()

        # 檢查前置條件
        if not self.check_prerequisites():
            self.console.print("\n[red]請先滿足所有前置條件[/red]")
            return

        # 範例 1: 初始化
        agent = self.example1_basic_initialization()

        # 範例 2: 創建環境
        environment = self.example2_create_environment()

        # 範例 3: 簡單任務
        if agent and environment:
            result3 = self.example3_simple_task(agent, environment)
            if result3:
                self.results.append({
                    "example": "simple_task",
                    "result": result3.to_dict()
                })

        # 範例 4: 程式碼搜索
        if agent:
            result4 = self.example4_code_search(agent)

        # 範例 5: 帶測試的任務
        if agent and environment:
            result5 = self.example5_with_tests(agent, environment)
            if result5:
                self.results.append({
                    "example": "with_tests",
                    "result": result5.to_dict()
                })

        # 保存結果
        self.save_results()

        # 顯示總結
        self._display_summary()

    def _display_summary(self):
        """顯示執行總結"""
        summary_text = f"""
        🎉 快速開始完成！

        你已經成功：
        ✓ 初始化了 SWE-Agent
        ✓ 創建了執行環境
        ✓ 運行了多個範例任務
        ✓ 理解了基本工作流程

        執行的範例數: {len(self.results)}

        下一步：
        • 查看更多進階範例
        • 嘗試解決真實的 GitHub Issues
        • 自定義工具和命令
        • 整合到你的 CI/CD 流程
        """

        self.console.print(Panel(
            summary_text,
            title="總結",
            border_style="blue"
        ))


def main():
    """主函數"""
    # 創建快速開始指南實例
    guide = QuickStartGuide()

    # 運行所有範例
    guide.run_all_examples()

    print("\n" + "="*60)
    print("快速開始完成！")
    print("查看其他範例檔案以學習更多進階功能。")
    print("="*60)


if __name__ == "__main__":
    main()

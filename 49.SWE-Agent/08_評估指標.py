#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SWE-Agent 評估指標範例
======================

這個範例展示如何評估 SWE-Agent 的性能：
1. SWE-bench 基準測試
2. 解決率計算
3. 成本分析
4. 時間效率評估
5. 代碼質量指標
6. A/B 測試對比

評估指標幫助我們了解 Agent 的表現，並持續改進。

作者: SWE-Agent 團隊
日期: 2025-12-31
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

# 數據處理
import pandas as pd
import numpy as np

# SWE-Agent
from sweagent import SWEAgent
from sweagent.evaluation import SWEBenchEvaluator
from sweagent.metrics import MetricsCollector

from loguru import logger
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, track
from rich.chart import Chart


@dataclass
class TaskMetrics:
    """
    單個任務的指標
    """
    task_id: str
    issue_number: int
    repo: str

    # 結果
    solved: bool
    status: str  # success, partial, failed

    # 時間指標
    start_time: datetime
    end_time: datetime
    duration_seconds: float

    # 成本指標
    input_tokens: int
    output_tokens: int
    total_cost: float

    # 質量指標
    iterations: int
    tests_passed: int
    tests_failed: int
    code_quality_score: Optional[float] = None

    # 錯誤信息
    error_type: Optional[str] = None
    error_message: Optional[str] = None

    def to_dict(self) -> Dict:
        """轉換為字典"""
        data = asdict(self)
        data['start_time'] = self.start_time.isoformat()
        data['end_time'] = self.end_time.isoformat()
        return data


@dataclass
class BenchmarkResults:
    """
    基準測試結果
    """
    benchmark_name: str
    total_tasks: int
    tasks: List[TaskMetrics]

    # 聚合指標
    solve_rate: float = 0.0
    avg_duration: float = 0.0
    avg_cost: float = 0.0
    avg_iterations: float = 0.0

    # 成本統計
    total_cost: float = 0.0
    total_tokens: int = 0

    # 時間統計
    total_time: float = 0.0
    min_time: float = 0.0
    max_time: float = 0.0

    def __post_init__(self):
        """計算聚合指標"""
        if self.tasks:
            # 解決率
            solved = sum(1 for t in self.tasks if t.solved)
            self.solve_rate = (solved / len(self.tasks)) * 100

            # 平均值
            self.avg_duration = statistics.mean(t.duration_seconds for t in self.tasks)
            self.avg_cost = statistics.mean(t.total_cost for t in self.tasks)
            self.avg_iterations = statistics.mean(t.iterations for t in self.tasks)

            # 總計
            self.total_cost = sum(t.total_cost for t in self.tasks)
            self.total_tokens = sum(t.input_tokens + t.output_tokens for t in self.tasks)
            self.total_time = sum(t.duration_seconds for t in self.tasks)

            # 最小最大
            self.min_time = min(t.duration_seconds for t in self.tasks)
            self.max_time = max(t.duration_seconds for t in self.tasks)


class SWEBenchRunner:
    """
    SWE-bench 基準測試運行器

    運行標準的 SWE-bench 評估
    """

    def __init__(self, agent: SWEAgent):
        """
        初始化

        Args:
            agent: SWE-Agent 實例
        """
        self.agent = agent
        self.console = Console()

        logger.info("SWE-bench 運行器初始化")

    def load_dataset(
        self,
        dataset_name: str = "swe-bench-lite"
    ) -> List[Dict]:
        """
        加載測試數據集

        Args:
            dataset_name: 數據集名稱

        Returns:
            測試實例列表
        """
        self.console.print(f"[bold]加載數據集: {dataset_name}[/bold]")

        # 實際應該從 SWE-bench 數據集加載
        # 這裡使用示例數據

        examples = [
            {
                "instance_id": "django-12345",
                "repo": "django/django",
                "issue_number": 12345,
                "problem_statement": "Fix memory leak in ORM",
                "test_patch": "...",
                "base_commit": "abc123"
            },
            # 更多測試實例...
        ]

        self.console.print(f"加載了 {len(examples)} 個測試實例")

        return examples

    def run_benchmark(
        self,
        dataset_name: str = "swe-bench-lite",
        num_instances: Optional[int] = None
    ) -> BenchmarkResults:
        """
        運行基準測試

        Args:
            dataset_name: 數據集名稱
            num_instances: 運行的實例數（None 表示全部）

        Returns:
            基準測試結果
        """
        self.console.print(Panel(
            f"[bold]開始 {dataset_name} 基準測試[/bold]",
            border_style="green"
        ))

        # 加載數據集
        dataset = self.load_dataset(dataset_name)

        if num_instances:
            dataset = dataset[:num_instances]

        # 運行每個實例
        task_metrics = []

        with Progress(console=self.console) as progress:
            task = progress.add_task(
                "[cyan]評估中...",
                total=len(dataset)
            )

            for instance in dataset:
                metrics = self._run_instance(instance)
                task_metrics.append(metrics)

                progress.update(task, advance=1)

        # 創建結果
        results = BenchmarkResults(
            benchmark_name=dataset_name,
            total_tasks=len(dataset),
            tasks=task_metrics
        )

        self._display_results(results)

        return results

    def _run_instance(self, instance: Dict) -> TaskMetrics:
        """
        運行單個測試實例

        Args:
            instance: 測試實例

        Returns:
            任務指標
        """
        instance_id = instance["instance_id"]

        self.console.print(f"\n[bold]運行實例: {instance_id}[/bold]")

        start_time = datetime.now()

        try:
            # 使用 Agent 解決問題
            result = self.agent.solve_issue(
                repo=instance["repo"],
                issue_number=instance["issue_number"]
            )

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # 創建指標
            metrics = TaskMetrics(
                task_id=instance_id,
                issue_number=instance["issue_number"],
                repo=instance["repo"],
                solved=result.success,
                status="success" if result.success else "failed",
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration,
                input_tokens=result.usage.get("input_tokens", 0),
                output_tokens=result.usage.get("output_tokens", 0),
                total_cost=result.cost,
                iterations=result.iterations,
                tests_passed=result.tests_passed,
                tests_failed=result.tests_failed
            )

        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            logger.error(f"實例執行失敗 {instance_id}: {e}")

            metrics = TaskMetrics(
                task_id=instance_id,
                issue_number=instance["issue_number"],
                repo=instance["repo"],
                solved=False,
                status="error",
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration,
                input_tokens=0,
                output_tokens=0,
                total_cost=0,
                iterations=0,
                tests_passed=0,
                tests_failed=0,
                error_type=type(e).__name__,
                error_message=str(e)
            )

        return metrics

    def _display_results(self, results: BenchmarkResults):
        """顯示結果"""
        # 摘要表格
        table = Table(title="基準測試結果摘要")
        table.add_column("指標", style="cyan")
        table.add_column("值", style="magenta")

        table.add_row("數據集", results.benchmark_name)
        table.add_row("總任務數", str(results.total_tasks))
        table.add_row("解決率", f"{results.solve_rate:.2f}%")
        table.add_row("平均耗時", f"{results.avg_duration:.2f} 秒")
        table.add_row("平均成本", f"${results.avg_cost:.4f}")
        table.add_row("總成本", f"${results.total_cost:.2f}")
        table.add_row("總 Tokens", f"{results.total_tokens:,}")

        self.console.print(table)


class CostAnalyzer:
    """
    成本分析器

    分析 Agent 運行的成本
    """

    # 模型價格（每 1000 tokens）
    MODEL_PRICES = {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
        "claude-3-opus": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet": {"input": 0.003, "output": 0.015},
        "claude-3-5-sonnet": {"input": 0.003, "output": 0.015},
    }

    def __init__(self):
        """初始化"""
        self.console = Console()

    def calculate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """
        計算成本

        Args:
            model: 模型名稱
            input_tokens: 輸入 tokens
            output_tokens: 輸出 tokens

        Returns:
            總成本（美元）
        """
        if model not in self.MODEL_PRICES:
            logger.warning(f"未知模型: {model}")
            return 0.0

        prices = self.MODEL_PRICES[model]

        input_cost = (input_tokens / 1000) * prices["input"]
        output_cost = (output_tokens / 1000) * prices["output"]

        return input_cost + output_cost

    def analyze_cost_distribution(
        self,
        tasks: List[TaskMetrics]
    ) -> Dict:
        """
        分析成本分布

        Args:
            tasks: 任務指標列表

        Returns:
            成本分析
        """
        self.console.print("[bold]成本分布分析[/bold]")

        costs = [t.total_cost for t in tasks]

        analysis = {
            "total": sum(costs),
            "mean": statistics.mean(costs),
            "median": statistics.median(costs),
            "std": statistics.stdev(costs) if len(costs) > 1 else 0,
            "min": min(costs),
            "max": max(costs),
            "percentiles": {
                "25": np.percentile(costs, 25),
                "50": np.percentile(costs, 50),
                "75": np.percentile(costs, 75),
                "90": np.percentile(costs, 90)
            }
        }

        self._display_cost_analysis(analysis)

        return analysis

    def _display_cost_analysis(self, analysis: Dict):
        """顯示成本分析"""
        table = Table(title="成本分析")
        table.add_column("統計量", style="cyan")
        table.add_column("值（美元）", style="magenta")

        table.add_row("總計", f"${analysis['total']:.2f}")
        table.add_row("平均", f"${analysis['mean']:.4f}")
        table.add_row("中位數", f"${analysis['median']:.4f}")
        table.add_row("標準差", f"${analysis['std']:.4f}")
        table.add_row("最小", f"${analysis['min']:.4f}")
        table.add_row("最大", f"${analysis['max']:.4f}")

        self.console.print(table)

        self.console.print("\n[bold]百分位數:[/bold]")
        for p, value in analysis['percentiles'].items():
            self.console.print(f"  P{p}: ${value:.4f}")


class PerformanceTracker:
    """
    性能追蹤器

    追蹤和記錄 Agent 的性能指標
    """

    def __init__(self, output_dir: str = "metrics"):
        """
        初始化

        Args:
            output_dir: 輸出目錄
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.console = Console()

        self.metrics_history = []

        logger.info(f"性能追蹤器初始化: {output_dir}")

    def record_task(self, metrics: TaskMetrics):
        """
        記錄任務指標

        Args:
            metrics: 任務指標
        """
        self.metrics_history.append(metrics)

        # 保存到文件
        self._save_metrics()

    def _save_metrics(self):
        """保存指標到文件"""
        output_file = self.output_dir / f"metrics_{datetime.now().strftime('%Y%m%d')}.jsonl"

        with open(output_file, 'a') as f:
            for metrics in self.metrics_history:
                f.write(json.dumps(metrics.to_dict()) + '\n')

    def generate_report(self) -> Dict:
        """
        生成性能報告

        Returns:
            報告數據
        """
        if not self.metrics_history:
            return {}

        report = {
            "period": {
                "start": min(m.start_time for m in self.metrics_history),
                "end": max(m.end_time for m in self.metrics_history)
            },
            "total_tasks": len(self.metrics_history),
            "solved_tasks": sum(1 for m in self.metrics_history if m.solved),
            "solve_rate": (sum(1 for m in self.metrics_history if m.solved) / len(self.metrics_history)) * 100,
            "performance": {
                "avg_duration": statistics.mean(m.duration_seconds for m in self.metrics_history),
                "avg_iterations": statistics.mean(m.iterations for m in self.metrics_history),
                "avg_cost": statistics.mean(m.total_cost for m in self.metrics_history)
            },
            "trends": self._calculate_trends()
        }

        self._display_report(report)

        return report

    def _calculate_trends(self) -> Dict:
        """計算趨勢"""
        # 按時間排序
        sorted_metrics = sorted(self.metrics_history, key=lambda m: m.start_time)

        # 計算移動平均
        window_size = min(10, len(sorted_metrics))

        solve_rates = []
        avg_durations = []

        for i in range(len(sorted_metrics) - window_size + 1):
            window = sorted_metrics[i:i + window_size]

            solve_rate = (sum(1 for m in window if m.solved) / window_size) * 100
            solve_rates.append(solve_rate)

            avg_duration = statistics.mean(m.duration_seconds for m in window)
            avg_durations.append(avg_duration)

        return {
            "solve_rate_trend": solve_rates,
            "duration_trend": avg_durations
        }

    def _display_report(self, report: Dict):
        """顯示報告"""
        self.console.print(Panel(
            f"""
            [bold]性能報告[/bold]

            總任務數: {report['total_tasks']}
            解決數: {report['solved_tasks']}
            解決率: {report['solve_rate']:.2f}%

            平均耗時: {report['performance']['avg_duration']:.2f} 秒
            平均迭代: {report['performance']['avg_iterations']:.1f}
            平均成本: ${report['performance']['avg_cost']:.4f}
            """,
            border_style="blue"
        ))


class ABTestComparer:
    """
    A/B 測試對比器

    對比不同配置的 Agent 性能
    """

    def __init__(self):
        """初始化"""
        self.console = Console()

    def compare_agents(
        self,
        agent_a_results: BenchmarkResults,
        agent_b_results: BenchmarkResults,
        agent_a_name: str = "Agent A",
        agent_b_name: str = "Agent B"
    ) -> Dict:
        """
        對比兩個 Agent

        Args:
            agent_a_results: Agent A 結果
            agent_b_results: Agent B 結果
            agent_a_name: Agent A 名稱
            agent_b_name: Agent B 名稱

        Returns:
            對比結果
        """
        self.console.print(Panel(
            f"[bold]A/B 測試對比: {agent_a_name} vs {agent_b_name}[/bold]",
            border_style="green"
        ))

        comparison = {
            "agent_a": {
                "name": agent_a_name,
                "solve_rate": agent_a_results.solve_rate,
                "avg_duration": agent_a_results.avg_duration,
                "avg_cost": agent_a_results.avg_cost
            },
            "agent_b": {
                "name": agent_b_name,
                "solve_rate": agent_b_results.solve_rate,
                "avg_duration": agent_b_results.avg_duration,
                "avg_cost": agent_b_results.avg_cost
            },
            "differences": {
                "solve_rate": agent_b_results.solve_rate - agent_a_results.solve_rate,
                "avg_duration": agent_b_results.avg_duration - agent_a_results.avg_duration,
                "avg_cost": agent_b_results.avg_cost - agent_a_results.avg_cost
            }
        }

        self._display_comparison(comparison)

        return comparison

    def _display_comparison(self, comparison: Dict):
        """顯示對比"""
        table = Table(title="A/B 測試對比")
        table.add_column("指標", style="cyan")
        table.add_column(comparison["agent_a"]["name"], style="magenta")
        table.add_column(comparison["agent_b"]["name"], style="magenta")
        table.add_column("差異", style="yellow")

        # 解決率
        table.add_row(
            "解決率",
            f"{comparison['agent_a']['solve_rate']:.2f}%",
            f"{comparison['agent_b']['solve_rate']:.2f}%",
            f"{comparison['differences']['solve_rate']:+.2f}%"
        )

        # 平均時間
        table.add_row(
            "平均時間",
            f"{comparison['agent_a']['avg_duration']:.2f}s",
            f"{comparison['agent_b']['avg_duration']:.2f}s",
            f"{comparison['differences']['avg_duration']:+.2f}s"
        )

        # 平均成本
        table.add_row(
            "平均成本",
            f"${comparison['agent_a']['avg_cost']:.4f}",
            f"${comparison['agent_b']['avg_cost']:.4f}",
            f"${comparison['differences']['avg_cost']:+.4f}"
        )

        self.console.print(table)

        # 建議
        if comparison['differences']['solve_rate'] > 0:
            winner = comparison["agent_b"]["name"]
        elif comparison['differences']['solve_rate'] < 0:
            winner = comparison["agent_a"]["name"]
        else:
            winner = "平局"

        self.console.print(f"\n[bold]勝者（基於解決率）: {winner}[/bold]")


def main():
    """主函數"""
    console = Console()

    console.print(Panel(
        "[bold]SWE-Agent 評估指標範例[/bold]\n\n"
        "展示如何評估和追蹤 Agent 性能",
        border_style="green"
    ))

    # 示例：創建 Agent
    from sweagent import SWEAgent

    agent = SWEAgent(model="gpt-4")

    # 1. 運行基準測試
    console.print("\n[bold cyan]1. SWE-bench 基準測試[/bold cyan]")
    runner = SWEBenchRunner(agent)
    results = runner.run_benchmark(dataset_name="swe-bench-lite", num_instances=5)

    # 2. 成本分析
    console.print("\n[bold cyan]2. 成本分析[/bold cyan]")
    cost_analyzer = CostAnalyzer()
    cost_analysis = cost_analyzer.analyze_cost_distribution(results.tasks)

    # 3. 性能追蹤
    console.print("\n[bold cyan]3. 性能追蹤[/bold cyan]")
    tracker = PerformanceTracker()

    for task_metrics in results.tasks:
        tracker.record_task(task_metrics)

    report = tracker.generate_report()

    # 4. A/B 測試（示例）
    console.print("\n[bold cyan]4. A/B 測試[/bold cyan]")
    # 需要兩組結果進行對比
    # comparer = ABTestComparer()
    # comparison = comparer.compare_agents(results_a, results_b)


if __name__ == "__main__":
    main()

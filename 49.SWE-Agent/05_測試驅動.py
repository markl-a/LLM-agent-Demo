#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SWE-Agent 測試驅動修復範例
===========================

這個範例展示如何使用測試驅動的方法進行 Bug 修復：
1. 測試執行和結果解析
2. 失敗測試分析
3. 測試引導的修復生成
4. 覆蓋率分析
5. 回歸測試防護
6. 測試優先級排序

測試驅動方法能確保修復不會破壞現有功能，
並且新的修復能通過所有測試用例。

作者: SWE-Agent 團隊
日期: 2025-12-31
"""

import os
import sys
import subprocess
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import xml.etree.ElementTree as ET

# 測試框架
try:
    import pytest
    import unittest
    import coverage
except ImportError:
    print("請安裝: pip install pytest coverage")

# SWE-Agent
from sweagent.testing import TestRunner, TestAnalyzer
from sweagent.coverage import CoverageAnalyzer

from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, track
from rich.tree import Tree


class TestStatus(Enum):
    """測試狀態枚舉"""
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    SKIPPED = "skipped"
    XFAIL = "xfail"


@dataclass
class TestResult:
    """
    測試結果數據結構
    """
    test_name: str
    test_file: str
    status: TestStatus
    duration: float
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    assertion_error: Optional[str] = None
    line_number: Optional[int] = None


@dataclass
class TestSuite:
    """
    測試套件
    """
    name: str
    tests: List[TestResult]
    total_time: float
    summary: Dict[str, int] = field(default_factory=dict)

    def __post_init__(self):
        """計算摘要"""
        self.summary = {
            "total": len(self.tests),
            "passed": sum(1 for t in self.tests if t.status == TestStatus.PASSED),
            "failed": sum(1 for t in self.tests if t.status == TestStatus.FAILED),
            "error": sum(1 for t in self.tests if t.status == TestStatus.ERROR),
            "skipped": sum(1 for t in self.tests if t.status == TestStatus.SKIPPED)
        }


class TestRunnerEngine:
    """
    測試運行引擎

    負責執行測試並收集結果
    """

    def __init__(self, repo_path: str):
        """
        初始化測試運行器

        Args:
            repo_path: 代碼庫路徑
        """
        self.repo_path = Path(repo_path)
        self.console = Console()

        logger.info(f"測試運行器初始化: {repo_path}")

    def discover_tests(self) -> List[str]:
        """
        發現所有測試文件

        Returns:
            測試文件列表
        """
        self.console.print("[bold]發現測試文件...[/bold]")

        test_files = []

        # pytest 測試文件模式
        patterns = [
            "**/test_*.py",
            "**/*_test.py",
            "**/tests.py"
        ]

        for pattern in patterns:
            test_files.extend(self.repo_path.rglob(pattern))

        # 排除虛擬環境等
        exclude_dirs = {'venv', 'env', '.tox', '__pycache__'}
        test_files = [
            f for f in test_files
            if not any(exc in f.parts for exc in exclude_dirs)
        ]

        self.console.print(f"發現 {len(test_files)} 個測試文件")

        return [str(f) for f in test_files]

    def run_tests(
        self,
        test_paths: Optional[List[str]] = None,
        verbose: bool = True
    ) -> TestSuite:
        """
        運行測試

        Args:
            test_paths: 測試文件路徑列表（None 表示全部）
            verbose: 是否詳細輸出

        Returns:
            測試套件結果
        """
        self.console.print("[bold]運行測試...[/bold]")

        start_time = datetime.now()

        # 準備 pytest 參數
        args = [
            "-v" if verbose else "",
            "--tb=short",
            "--junit-xml=test_results.xml",
            "--json-report",
            "--json-report-file=test_results.json"
        ]

        if test_paths:
            args.extend(test_paths)

        args = [arg for arg in args if arg]

        # 運行 pytest
        try:
            result = pytest.main(args)

            # 解析結果
            test_results = self._parse_test_results()

            total_time = (datetime.now() - start_time).total_seconds()

            suite = TestSuite(
                name="All Tests",
                tests=test_results,
                total_time=total_time
            )

            self._display_test_summary(suite)

            return suite

        except Exception as e:
            logger.error(f"運行測試失敗: {e}")
            return TestSuite(name="Failed", tests=[], total_time=0)

    def run_specific_test(
        self,
        test_file: str,
        test_name: str
    ) -> Optional[TestResult]:
        """
        運行特定測試

        Args:
            test_file: 測試文件
            test_name: 測試名稱

        Returns:
            測試結果
        """
        test_path = f"{test_file}::{test_name}"
        self.console.print(f"[bold]運行測試: {test_path}[/bold]")

        args = [
            test_path,
            "-v",
            "--tb=short",
            "--json-report",
            "--json-report-file=single_test.json"
        ]

        result = pytest.main(args)

        # 解析單個測試結果
        try:
            with open("single_test.json", 'r') as f:
                data = json.load(f)
                tests = data.get("tests", [])
                if tests:
                    return self._parse_test_item(tests[0])
        except:
            pass

        return None

    def _parse_test_results(self) -> List[TestResult]:
        """
        解析測試結果

        Returns:
            測試結果列表
        """
        results = []

        # 從 JSON 報告解析
        try:
            with open("test_results.json", 'r') as f:
                data = json.load(f)

                for test_data in data.get("tests", []):
                    result = self._parse_test_item(test_data)
                    results.append(result)

        except Exception as e:
            logger.warning(f"解析測試結果失敗: {e}")

        return results

    def _parse_test_item(self, test_data: Dict) -> TestResult:
        """解析單個測試項"""
        # 確定狀態
        outcome = test_data.get("outcome", "unknown")
        status_map = {
            "passed": TestStatus.PASSED,
            "failed": TestStatus.FAILED,
            "error": TestStatus.ERROR,
            "skipped": TestStatus.SKIPPED,
            "xfail": TestStatus.XFAIL
        }
        status = status_map.get(outcome, TestStatus.ERROR)

        # 提取錯誤信息
        error_message = None
        stack_trace = None
        assertion_error = None

        if "call" in test_data and "longrepr" in test_data["call"]:
            longrepr = test_data["call"]["longrepr"]
            if isinstance(longrepr, str):
                stack_trace = longrepr
                # 嘗試提取斷言錯誤
                assertion_match = re.search(r"AssertionError: (.+)", longrepr)
                if assertion_match:
                    assertion_error = assertion_match.group(1)
            error_message = test_data["call"].get("crash", {}).get("message")

        return TestResult(
            test_name=test_data.get("nodeid", "unknown"),
            test_file=test_data.get("location", ["unknown"])[0],
            status=status,
            duration=test_data.get("duration", 0.0),
            error_message=error_message,
            stack_trace=stack_trace,
            assertion_error=assertion_error,
            line_number=test_data.get("location", [None, None])[1]
        )

    def _display_test_summary(self, suite: TestSuite):
        """顯示測試摘要"""
        table = Table(title="測試摘要")
        table.add_column("狀態", style="cyan")
        table.add_column("數量", style="magenta")
        table.add_column("百分比")

        total = suite.summary["total"]

        for status, count in suite.summary.items():
            if status == "total":
                continue

            percentage = (count / total * 100) if total > 0 else 0

            # 選擇顏色
            if status == "passed":
                style = "green"
            elif status in ["failed", "error"]:
                style = "red"
            else:
                style = "yellow"

            table.add_row(
                status.upper(),
                f"[{style}]{count}[/{style}]",
                f"{percentage:.1f}%"
            )

        table.add_row("TOTAL", str(total), "100%", style="bold")

        self.console.print(table)
        self.console.print(f"\n總耗時: {suite.total_time:.2f} 秒")


class FailureAnalyzer:
    """
    失敗分析器

    深度分析失敗的測試，提取有用的調試信息
    """

    def __init__(self):
        """初始化分析器"""
        self.console = Console()

    def analyze_failure(self, test_result: TestResult) -> Dict:
        """
        分析測試失敗

        Args:
            test_result: 測試結果

        Returns:
            分析結果
        """
        self.console.print(f"\n[bold]分析失敗測試: {test_result.test_name}[/bold]")

        analysis = {
            "test_name": test_result.test_name,
            "failure_type": self._classify_failure(test_result),
            "root_cause": self._identify_root_cause(test_result),
            "affected_code": self._find_affected_code(test_result),
            "suggestions": self._generate_suggestions(test_result)
        }

        self._display_analysis(analysis)

        return analysis

    def _classify_failure(self, result: TestResult) -> str:
        """
        分類失敗類型

        Args:
            result: 測試結果

        Returns:
            失敗類型
        """
        if not result.error_message and not result.stack_trace:
            return "unknown"

        error_text = (result.error_message or "") + (result.stack_trace or "")

        # 常見失敗模式
        patterns = {
            "assertion": r"AssertionError",
            "attribute": r"AttributeError",
            "type": r"TypeError",
            "value": r"ValueError",
            "key": r"KeyError",
            "index": r"IndexError",
            "import": r"ImportError|ModuleNotFoundError",
            "timeout": r"TimeoutError",
            "connection": r"ConnectionError"
        }

        for failure_type, pattern in patterns.items():
            if re.search(pattern, error_text):
                return failure_type

        return "other"

    def _identify_root_cause(self, result: TestResult) -> str:
        """
        識別根本原因

        Args:
            result: 測試結果

        Returns:
            根本原因描述
        """
        if result.assertion_error:
            return f"斷言失敗: {result.assertion_error}"

        if result.error_message:
            return result.error_message

        return "未知原因"

    def _find_affected_code(self, result: TestResult) -> List[str]:
        """
        查找受影響的代碼

        Args:
            result: 測試結果

        Returns:
            受影響的文件/函數列表
        """
        affected = []

        if result.stack_trace:
            # 從堆疊追蹤中提取文件和函數
            pattern = r'File "([^"]+)", line (\d+), in (\w+)'
            matches = re.findall(pattern, result.stack_trace)

            for file_path, line_num, func_name in matches:
                # 排除測試文件本身
                if "test_" not in file_path:
                    affected.append(f"{file_path}:{line_num} ({func_name})")

        return affected

    def _generate_suggestions(self, result: TestResult) -> List[str]:
        """
        生成修復建議

        Args:
            result: 測試結果

        Returns:
            建議列表
        """
        suggestions = []

        failure_type = self._classify_failure(result)

        suggestion_map = {
            "assertion": [
                "檢查實際值和預期值的差異",
                "驗證測試數據是否正確",
                "確認函數邏輯是否符合預期"
            ],
            "attribute": [
                "檢查對象是否正確初始化",
                "驗證屬性名稱拼寫",
                "確認對象類型是否正確"
            ],
            "type": [
                "檢查函數參數類型",
                "添加類型轉換",
                "驗證輸入數據格式"
            ],
            "import": [
                "確認模塊已安裝",
                "檢查導入路徑",
                "驗證依賴版本"
            ]
        }

        suggestions = suggestion_map.get(failure_type, ["需要進一步調查"])

        return suggestions

    def _display_analysis(self, analysis: Dict):
        """顯示分析結果"""
        self.console.print("\n[bold cyan]失敗分析:[/bold cyan]")

        self.console.print(f"  失敗類型: [yellow]{analysis['failure_type']}[/yellow]")
        self.console.print(f"  根本原因: [red]{analysis['root_cause']}[/red]")

        if analysis['affected_code']:
            self.console.print("\n  受影響的代碼:")
            for code in analysis['affected_code']:
                self.console.print(f"    • {code}")

        if analysis['suggestions']:
            self.console.print("\n  修復建議:")
            for suggestion in analysis['suggestions']:
                self.console.print(f"    • {suggestion}")


class TestDrivenFixer:
    """
    測試驅動修復器

    使用測試結果引導修復過程
    """

    def __init__(self, repo_path: str, model: str = "gpt-4"):
        """
        初始化修復器

        Args:
            repo_path: 代碼庫路徑
            model: LLM 模型
        """
        self.repo_path = Path(repo_path)
        self.model = model
        self.console = Console()

        self.runner = TestRunnerEngine(repo_path)
        self.analyzer = FailureAnalyzer()

        logger.info("測試驅動修復器初始化完成")

    def fix_with_tests(
        self,
        test_file: Optional[str] = None,
        max_iterations: int = 5
    ) -> Dict:
        """
        使用測試驅動修復

        Args:
            test_file: 特定測試文件（None 表示全部）
            max_iterations: 最大迭代次數

        Returns:
            修復結果
        """
        self.console.print(Panel(
            "[bold]開始測試驅動修復[/bold]",
            border_style="green"
        ))

        result = {
            "iterations": [],
            "final_status": "unknown",
            "fixes_applied": 0
        }

        for iteration in range(1, max_iterations + 1):
            self.console.print(f"\n[bold cyan]迭代 {iteration}/{max_iterations}[/bold cyan]")

            # 1. 運行測試
            test_paths = [test_file] if test_file else None
            suite = self.runner.run_tests(test_paths, verbose=False)

            # 2. 檢查是否所有測試通過
            if suite.summary["failed"] == 0 and suite.summary["error"] == 0:
                self.console.print("[green]✓ 所有測試通過！[/green]")
                result["final_status"] = "success"
                break

            # 3. 分析失敗測試
            failed_tests = [
                t for t in suite.tests
                if t.status in [TestStatus.FAILED, TestStatus.ERROR]
            ]

            self.console.print(f"發現 {len(failed_tests)} 個失敗測試")

            # 4. 優先處理第一個失敗測試
            target_test = failed_tests[0]
            analysis = self.analyzer.analyze_failure(target_test)

            # 5. 生成修復
            fix = self._generate_fix(target_test, analysis)

            if fix:
                # 6. 應用修復
                self._apply_fix(fix)
                result["fixes_applied"] += 1

                result["iterations"].append({
                    "iteration": iteration,
                    "test": target_test.test_name,
                    "fix_applied": True
                })
            else:
                result["iterations"].append({
                    "iteration": iteration,
                    "test": target_test.test_name,
                    "fix_applied": False
                })
                break

        # 最終測試
        self.console.print("\n[bold]最終測試...[/bold]")
        final_suite = self.runner.run_tests(test_paths, verbose=True)

        if final_suite.summary["failed"] == 0 and final_suite.summary["error"] == 0:
            result["final_status"] = "success"
        else:
            result["final_status"] = "partial"

        self._display_fix_summary(result)

        return result

    def _generate_fix(self, test: TestResult, analysis: Dict) -> Optional[Dict]:
        """
        生成修復

        Args:
            test: 測試結果
            analysis: 失敗分析

        Returns:
            修復建議
        """
        self.console.print("\n[bold]生成修復方案...[/bold]")

        # 這裡應該使用 LLM 生成實際的修復代碼
        # 示例實現

        fix = {
            "file": analysis["affected_code"][0] if analysis["affected_code"] else None,
            "changes": [],
            "description": f"修復 {test.test_name}"
        }

        # TODO: 實際的 LLM 修復生成邏輯

        return fix

    def _apply_fix(self, fix: Dict):
        """
        應用修復

        Args:
            fix: 修復數據
        """
        self.console.print(f"[yellow]應用修復: {fix['description']}[/yellow]")

        # TODO: 實際應用修復到文件

    def _display_fix_summary(self, result: Dict):
        """顯示修復摘要"""
        summary = f"""
        迭代次數: {len(result['iterations'])}
        應用的修復: {result['fixes_applied']}
        最終狀態: {result['final_status']}
        """

        self.console.print(Panel(
            summary,
            title="修復摘要",
            border_style="blue"
        ))


class CoverageAnalyzerEngine:
    """
    覆蓋率分析引擎

    分析測試覆蓋率，識別未測試的代碼
    """

    def __init__(self, repo_path: str):
        """初始化覆蓋率分析器"""
        self.repo_path = Path(repo_path)
        self.console = Console()

    def analyze_coverage(self, test_paths: Optional[List[str]] = None) -> Dict:
        """
        分析測試覆蓋率

        Args:
            test_paths: 測試路徑

        Returns:
            覆蓋率報告
        """
        self.console.print("[bold]分析測試覆蓋率...[/bold]")

        # 使用 coverage.py 運行測試
        cov = coverage.Coverage()
        cov.start()

        # 運行測試
        pytest_args = test_paths or [str(self.repo_path / "tests")]
        pytest.main(pytest_args + ["-q"])

        cov.stop()
        cov.save()

        # 生成報告
        total_coverage = cov.report()

        # 獲取詳細數據
        coverage_data = {}
        for filename in cov.get_data().measured_files():
            analysis = cov.analysis(filename)
            coverage_data[filename] = {
                "executed": len(analysis[1]),
                "missing": len(analysis[2]),
                "total": len(analysis[1]) + len(analysis[2])
            }

        report = {
            "total_coverage": total_coverage,
            "files": coverage_data
        }

        self._display_coverage_report(report)

        return report

    def _display_coverage_report(self, report: Dict):
        """顯示覆蓋率報告"""
        table = Table(title=f"覆蓋率報告 ({report['total_coverage']:.1f}%)")
        table.add_column("文件", style="cyan")
        table.add_column("覆蓋率", style="magenta")
        table.add_column("缺失行數")

        for filename, data in list(report["files"].items())[:10]:
            coverage_pct = (data["executed"] / data["total"] * 100) if data["total"] > 0 else 0

            style = "green" if coverage_pct >= 80 else "yellow" if coverage_pct >= 60 else "red"

            table.add_row(
                Path(filename).name,
                f"[{style}]{coverage_pct:.1f}%[/{style}]",
                str(data["missing"])
            )

        self.console.print(table)


def main():
    """主函數"""
    console = Console()

    console.print(Panel(
        "[bold]SWE-Agent 測試驅動修復範例[/bold]\n\n"
        "展示測試驅動的 Bug 修復流程",
        border_style="green"
    ))

    # 示例代碼庫路徑
    repo_path = "/path/to/your/repo"

    # 1. 發現和運行測試
    console.print("\n[bold cyan]1. 運行測試[/bold cyan]")
    runner = TestRunnerEngine(repo_path)
    suite = runner.run_tests()

    # 2. 分析失敗測試
    if suite.summary["failed"] > 0:
        console.print("\n[bold cyan]2. 分析失敗測試[/bold cyan]")

        failed_tests = [
            t for t in suite.tests
            if t.status == TestStatus.FAILED
        ]

        analyzer = FailureAnalyzer()
        for test in failed_tests[:3]:  # 分析前3個
            analyzer.analyze_failure(test)

    # 3. 測試驅動修復
    console.print("\n[bold cyan]3. 測試驅動修復[/bold cyan]")
    fixer = TestDrivenFixer(repo_path)
    result = fixer.fix_with_tests(max_iterations=3)

    # 4. 覆蓋率分析
    console.print("\n[bold cyan]4. 覆蓋率分析[/bold cyan]")
    coverage_analyzer = CoverageAnalyzerEngine(repo_path)
    coverage_report = coverage_analyzer.analyze_coverage()


if __name__ == "__main__":
    main()

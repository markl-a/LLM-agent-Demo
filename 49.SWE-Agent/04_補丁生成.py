#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SWE-Agent 補丁生成範例
=====================

這個範例展示如何使用 SWE-Agent 生成和應用程式碼補丁：
1. 分析問題並生成修復補丁
2. 差異格式化（unified diff, git diff）
3. 補丁驗證和預檢
4. 補丁應用和回滾
5. 多文件補丁管理
6. 增量補丁生成

補丁生成是 SWE-Agent 核心功能之一，能夠將 AI 的修復建議
轉換為可應用的程式碼變更。

作者: SWE-Agent 團隊
日期: 2025-12-31
"""

import os
import difflib
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json
import tempfile
import shutil

# Git 操作
try:
    from git import Repo, GitCommandError
except ImportError:
    print("請安裝: pip install gitpython")

# SWE-Agent
from sweagent.patch import PatchGenerator, PatchApplier
from sweagent.validation import PatchValidator

from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn


@dataclass
class FileChange:
    """
    文件變更記錄
    """
    file_path: str
    original_content: str
    modified_content: str
    change_type: str  # modify, create, delete
    line_changes: List[Tuple[int, str, str]] = field(default_factory=list)


@dataclass
class Patch:
    """
    補丁數據結構
    """
    patch_id: str
    description: str
    files_changed: List[FileChange]
    created_at: datetime
    author: str
    diff_content: str
    metadata: Dict = field(default_factory=dict)

    def to_unified_diff(self) -> str:
        """轉換為 unified diff 格式"""
        return self.diff_content

    def to_dict(self) -> Dict:
        """轉換為字典"""
        return {
            "patch_id": self.patch_id,
            "description": self.description,
            "files_changed": len(self.files_changed),
            "created_at": self.created_at.isoformat(),
            "author": self.author,
            "metadata": self.metadata
        }


class SmartPatchGenerator:
    """
    智能補丁生成器

    使用 LLM 理解問題並生成精確的程式碼補丁
    """

    def __init__(
        self,
        repo_path: str,
        model: str = "gpt-4"
    ):
        """
        初始化補丁生成器

        Args:
            repo_path: 代碼庫路徑
            model: LLM 模型
        """
        self.repo_path = Path(repo_path)
        self.model = model
        self.console = Console()

        # 初始化 Git repo
        try:
            self.repo = Repo(repo_path)
        except:
            self.repo = None
            logger.warning("不是 Git 儲存庫")

        logger.info(f"補丁生成器初始化: {repo_path}")

    def generate_patch_from_issue(
        self,
        issue_description: str,
        related_files: List[str]
    ) -> Optional[Patch]:
        """
        從 Issue 描述生成補丁

        Args:
            issue_description: Issue 描述
            related_files: 相關文件列表

        Returns:
            生成的補丁
        """
        self.console.print("[bold]生成補丁中...[/bold]")

        # 1. 分析問題
        analysis = self._analyze_issue(issue_description, related_files)

        # 2. 生成修復建議
        fixes = self._generate_fixes(analysis)

        # 3. 應用修復並生成補丁
        patch = self._create_patch_from_fixes(fixes)

        if patch:
            self.console.print("[green]✓ 補丁生成成功[/green]")

        return patch

    def _analyze_issue(
        self,
        description: str,
        files: List[str]
    ) -> Dict:
        """
        分析 Issue 並確定修復策略

        Args:
            description: Issue 描述
            files: 相關文件

        Returns:
            分析結果
        """
        self.console.print("  [cyan]分析問題...[/cyan]")

        # 讀取相關文件內容
        file_contents = {}
        for file_path in files:
            try:
                full_path = self.repo_path / file_path
                if full_path.exists():
                    content = full_path.read_text(encoding='utf-8')
                    file_contents[file_path] = content
            except Exception as e:
                logger.warning(f"讀取文件失敗 {file_path}: {e}")

        analysis = {
            "description": description,
            "affected_files": file_contents,
            "problem_type": self._classify_problem(description),
            "suggested_approach": self._suggest_approach(description)
        }

        return analysis

    def _classify_problem(self, description: str) -> str:
        """
        分類問題類型

        Args:
            description: 問題描述

        Returns:
            問題類型
        """
        # 簡化的問題分類
        keywords = {
            "bug": ["error", "exception", "crash", "fail", "broken"],
            "performance": ["slow", "performance", "optimize", "speed"],
            "feature": ["add", "new", "feature", "implement"],
            "refactor": ["refactor", "clean", "improve", "restructure"]
        }

        desc_lower = description.lower()

        for problem_type, kws in keywords.items():
            if any(kw in desc_lower for kw in kws):
                return problem_type

        return "unknown"

    def _suggest_approach(self, description: str) -> str:
        """建議修復方法"""
        # 這裡應該使用 LLM 生成修復建議
        return "待實現"

    def _generate_fixes(self, analysis: Dict) -> List[FileChange]:
        """
        生成修復變更

        Args:
            analysis: 問題分析

        Returns:
            文件變更列表
        """
        self.console.print("  [cyan]生成修復方案...[/cyan]")

        fixes = []

        # 這裡應該使用 LLM 生成實際的程式碼修復
        # 示例：簡單的文本替換
        for file_path, original_content in analysis["affected_files"].items():
            # TODO: 使用 LLM 生成修復後的內容
            modified_content = original_content  # 臨時

            if modified_content != original_content:
                change = FileChange(
                    file_path=file_path,
                    original_content=original_content,
                    modified_content=modified_content,
                    change_type="modify"
                )
                fixes.append(change)

        return fixes

    def _create_patch_from_fixes(
        self,
        fixes: List[FileChange]
    ) -> Optional[Patch]:
        """
        從修復變更創建補丁

        Args:
            fixes: 文件變更列表

        Returns:
            補丁對象
        """
        if not fixes:
            return None

        # 生成 unified diff
        diff_lines = []

        for fix in fixes:
            diff = self._generate_unified_diff(
                fix.file_path,
                fix.original_content,
                fix.modified_content
            )
            diff_lines.append(diff)

        diff_content = "\n".join(diff_lines)

        patch = Patch(
            patch_id=self._generate_patch_id(),
            description="AI 生成的修復補丁",
            files_changed=fixes,
            created_at=datetime.now(),
            author="SWE-Agent",
            diff_content=diff_content
        )

        return patch

    def _generate_unified_diff(
        self,
        file_path: str,
        original: str,
        modified: str
    ) -> str:
        """
        生成 unified diff 格式

        Args:
            file_path: 文件路徑
            original: 原始內容
            modified: 修改後內容

        Returns:
            unified diff 字符串
        """
        original_lines = original.splitlines(keepends=True)
        modified_lines = modified.splitlines(keepends=True)

        diff = difflib.unified_diff(
            original_lines,
            modified_lines,
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
            lineterm=''
        )

        return ''.join(diff)

    def _generate_patch_id(self) -> str:
        """生成補丁 ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"patch_{timestamp}"

    def create_minimal_patch(
        self,
        file_path: str,
        target_function: str,
        fix_code: str
    ) -> Optional[Patch]:
        """
        創建最小化補丁

        只修改特定函數，而不是整個文件

        Args:
            file_path: 文件路徑
            target_function: 目標函數名
            fix_code: 修復後的函數代碼

        Returns:
            補丁對象
        """
        self.console.print(f"[bold]為 {target_function} 創建最小化補丁[/bold]")

        try:
            full_path = self.repo_path / file_path
            original_content = full_path.read_text(encoding='utf-8')

            # 替換目標函數
            modified_content = self._replace_function(
                original_content,
                target_function,
                fix_code
            )

            # 創建補丁
            change = FileChange(
                file_path=file_path,
                original_content=original_content,
                modified_content=modified_content,
                change_type="modify"
            )

            diff = self._generate_unified_diff(
                file_path,
                original_content,
                modified_content
            )

            patch = Patch(
                patch_id=self._generate_patch_id(),
                description=f"修復 {target_function} 函數",
                files_changed=[change],
                created_at=datetime.now(),
                author="SWE-Agent",
                diff_content=diff,
                metadata={"target_function": target_function}
            )

            return patch

        except Exception as e:
            logger.error(f"創建補丁失敗: {e}")
            return None

    def _replace_function(
        self,
        content: str,
        function_name: str,
        new_code: str
    ) -> str:
        """
        替換函數定義

        Args:
            content: 文件內容
            function_name: 函數名
            new_code: 新的函數代碼

        Returns:
            修改後的內容
        """
        import ast

        try:
            tree = ast.parse(content)
            lines = content.split('\n')

            # 找到目標函數
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == function_name:
                    # 找到函數的結束行
                    start_line = node.lineno - 1
                    end_line = node.end_lineno

                    # 替換函數
                    new_lines = (
                        lines[:start_line] +
                        [new_code] +
                        lines[end_line:]
                    )

                    return '\n'.join(new_lines)

            # 如果沒找到函數，返回原內容
            return content

        except:
            return content


class PatchValidatorEngine:
    """
    補丁驗證引擎

    驗證補丁的正確性和安全性
    """

    def __init__(self, repo_path: str):
        """初始化驗證器"""
        self.repo_path = Path(repo_path)
        self.console = Console()

    def validate_patch(self, patch: Patch) -> Dict[str, any]:
        """
        驗證補丁

        Args:
            patch: 補丁對象

        Returns:
            驗證結果
        """
        self.console.print("[bold]驗證補丁...[/bold]")

        results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "checks": {}
        }

        # 1. 語法檢查
        syntax_check = self._check_syntax(patch)
        results["checks"]["syntax"] = syntax_check
        if not syntax_check["passed"]:
            results["valid"] = False
            results["errors"].extend(syntax_check["errors"])

        # 2. 衝突檢查
        conflict_check = self._check_conflicts(patch)
        results["checks"]["conflicts"] = conflict_check
        if not conflict_check["passed"]:
            results["valid"] = False
            results["errors"].extend(conflict_check["errors"])

        # 3. 安全檢查
        security_check = self._check_security(patch)
        results["checks"]["security"] = security_check
        if security_check["issues"]:
            results["warnings"].extend(security_check["issues"])

        # 4. 風格檢查
        style_check = self._check_style(patch)
        results["checks"]["style"] = style_check

        self._display_validation_results(results)

        return results

    def _check_syntax(self, patch: Patch) -> Dict:
        """檢查語法"""
        self.console.print("  [cyan]檢查語法...[/cyan]")

        result = {
            "passed": True,
            "errors": []
        }

        for change in patch.files_changed:
            if change.file_path.endswith('.py'):
                # 檢查 Python 語法
                try:
                    compile(change.modified_content, change.file_path, 'exec')
                except SyntaxError as e:
                    result["passed"] = False
                    result["errors"].append(f"{change.file_path}: {e}")

        return result

    def _check_conflicts(self, patch: Patch) -> Dict:
        """檢查衝突"""
        self.console.print("  [cyan]檢查衝突...[/cyan]")

        result = {
            "passed": True,
            "errors": []
        }

        # 檢查文件是否存在
        for change in patch.files_changed:
            file_path = self.repo_path / change.file_path

            if change.change_type == "modify" and not file_path.exists():
                result["passed"] = False
                result["errors"].append(f"文件不存在: {change.file_path}")

            elif change.change_type == "create" and file_path.exists():
                result["passed"] = False
                result["errors"].append(f"文件已存在: {change.file_path}")

        return result

    def _check_security(self, patch: Patch) -> Dict:
        """安全檢查"""
        self.console.print("  [cyan]安全檢查...[/cyan]")

        result = {
            "passed": True,
            "issues": []
        }

        # 檢查危險操作
        dangerous_patterns = [
            r'eval\(',
            r'exec\(',
            r'__import__\(',
            r'os\.system\(',
            r'subprocess\.call\('
        ]

        import re

        for change in patch.files_changed:
            for pattern in dangerous_patterns:
                if re.search(pattern, change.modified_content):
                    result["issues"].append(
                        f"{change.file_path}: 發現潛在危險操作 {pattern}"
                    )

        return result

    def _check_style(self, patch: Patch) -> Dict:
        """風格檢查"""
        result = {
            "passed": True,
            "issues": []
        }

        # 簡化的風格檢查
        for change in patch.files_changed:
            if change.file_path.endswith('.py'):
                # 檢查行長度
                lines = change.modified_content.split('\n')
                for i, line in enumerate(lines, 1):
                    if len(line) > 100:
                        result["issues"].append(
                            f"{change.file_path}:{i}: 行過長 ({len(line)} 字符)"
                        )

        return result

    def _display_validation_results(self, results: Dict):
        """顯示驗證結果"""
        # 創建結果表格
        table = Table(title="驗證結果")
        table.add_column("檢查項", style="cyan")
        table.add_column("狀態", style="magenta")
        table.add_column("詳情")

        for check_name, check_result in results["checks"].items():
            passed = check_result.get("passed", True)
            status = "✓ 通過" if passed else "✗ 失敗"
            style = "green" if passed else "red"

            details = ""
            if "errors" in check_result and check_result["errors"]:
                details = f"{len(check_result['errors'])} 個錯誤"
            elif "issues" in check_result and check_result["issues"]:
                details = f"{len(check_result['issues'])} 個問題"

            table.add_row(
                check_name,
                f"[{style}]{status}[/{style}]",
                details
            )

        self.console.print(table)


class PatchApplierEngine:
    """
    補丁應用引擎

    負責將補丁應用到代碼庫
    """

    def __init__(self, repo_path: str):
        """初始化應用器"""
        self.repo_path = Path(repo_path)
        self.console = Console()

        try:
            self.repo = Repo(repo_path)
        except:
            self.repo = None

    def apply_patch(
        self,
        patch: Patch,
        dry_run: bool = False
    ) -> Dict[str, any]:
        """
        應用補丁

        Args:
            patch: 補丁對象
            dry_run: 是否為乾跑（不實際修改文件）

        Returns:
            應用結果
        """
        mode = "乾跑模式" if dry_run else "應用補丁"
        self.console.print(f"[bold]{mode}...[/bold]")

        result = {
            "success": True,
            "applied_files": [],
            "failed_files": [],
            "backup_created": False
        }

        # 創建備份（如果不是乾跑）
        if not dry_run:
            backup_path = self._create_backup()
            result["backup_path"] = backup_path
            result["backup_created"] = True

        # 應用每個文件的變更
        for change in patch.files_changed:
            try:
                if not dry_run:
                    self._apply_file_change(change)

                result["applied_files"].append(change.file_path)
                self.console.print(f"  [green]✓[/green] {change.file_path}")

            except Exception as e:
                result["success"] = False
                result["failed_files"].append(change.file_path)
                self.console.print(f"  [red]✗[/red] {change.file_path}: {e}")

        # 如果有失敗且不是乾跑，回滾
        if not result["success"] and not dry_run and result["backup_created"]:
            self.console.print("[yellow]應用失敗，正在回滾...[/yellow]")
            self._restore_backup(result["backup_path"])

        return result

    def _apply_file_change(self, change: FileChange):
        """應用單個文件變更"""
        file_path = self.repo_path / change.file_path

        if change.change_type == "modify":
            file_path.write_text(change.modified_content, encoding='utf-8')

        elif change.change_type == "create":
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(change.modified_content, encoding='utf-8')

        elif change.change_type == "delete":
            file_path.unlink()

    def _create_backup(self) -> Path:
        """創建備份"""
        backup_dir = Path(tempfile.mkdtemp(prefix="swe_agent_backup_"))
        shutil.copytree(self.repo_path, backup_dir / "repo", symlinks=True)
        logger.info(f"備份已創建: {backup_dir}")
        return backup_dir

    def _restore_backup(self, backup_path: Path):
        """恢復備份"""
        shutil.rmtree(self.repo_path)
        shutil.copytree(backup_path / "repo", self.repo_path, symlinks=True)
        logger.info("已從備份恢復")

    def commit_patch(
        self,
        patch: Patch,
        commit_message: Optional[str] = None
    ) -> bool:
        """
        提交補丁到 Git

        Args:
            patch: 補丁對象
            commit_message: 提交訊息

        Returns:
            是否成功
        """
        if not self.repo:
            self.console.print("[yellow]不是 Git 儲存庫[/yellow]")
            return False

        try:
            # 添加變更的文件
            for change in patch.files_changed:
                self.repo.index.add([change.file_path])

            # 提交
            message = commit_message or patch.description
            self.repo.index.commit(message)

            self.console.print("[green]✓ 補丁已提交到 Git[/green]")
            return True

        except GitCommandError as e:
            self.console.print(f"[red]提交失敗: {e}[/red]")
            return False


def main():
    """主函數"""
    console = Console()

    console.print(Panel(
        "[bold]SWE-Agent 補丁生成範例[/bold]\n\n"
        "展示補丁生成、驗證和應用流程",
        border_style="green"
    ))

    # 示例代碼庫路徑
    repo_path = "/path/to/your/repo"

    # 1. 生成補丁
    console.print("\n[bold cyan]1. 生成補丁[/bold cyan]")
    generator = SmartPatchGenerator(repo_path)

    patch = generator.generate_patch_from_issue(
        issue_description="修復 calculate_sum 函數的除零錯誤",
        related_files=["utils.py"]
    )

    if patch:
        # 顯示補丁
        console.print("\n[bold]生成的補丁:[/bold]")
        syntax = Syntax(patch.diff_content, "diff", theme="monokai")
        console.print(syntax)

        # 2. 驗證補丁
        console.print("\n[bold cyan]2. 驗證補丁[/bold cyan]")
        validator = PatchValidatorEngine(repo_path)
        validation = validator.validate_patch(patch)

        # 3. 應用補丁
        if validation["valid"]:
            console.print("\n[bold cyan]3. 應用補丁[/bold cyan]")
            applier = PatchApplierEngine(repo_path)

            # 先乾跑
            dry_result = applier.apply_patch(patch, dry_run=True)

            if dry_result["success"]:
                # 實際應用
                result = applier.apply_patch(patch, dry_run=False)

                if result["success"]:
                    # 提交到 Git
                    applier.commit_patch(patch)


if __name__ == "__main__":
    main()

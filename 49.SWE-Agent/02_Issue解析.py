#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SWE-Agent Issue 解析範例
=======================

這個範例展示如何使用 SWE-Agent 解析和處理 GitHub Issues：
1. 從 GitHub 獲取 Issue
2. 解析 Issue 描述和內容
3. 提取關鍵資訊（問題類型、優先級、相關檔案等）
4. 分析重現步驟
5. 識別相關代碼區域
6. 生成初步診斷

Issue 解析是 SWE-Agent 工作流程的第一步，準確的解析能夠
顯著提升後續修復的成功率。

作者: SWE-Agent 團隊
日期: 2025-12-31
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

# GitHub API
try:
    from github import Github, Issue as GithubIssue
    import requests
except ImportError:
    print("請安裝: pip install PyGithub requests")

# SWE-Agent
from sweagent import SWEAgent
from sweagent.parsers import IssueParser
from sweagent.analyzers import IssueAnalyzer

# NLP 處理
try:
    import openai
    from anthropic import Anthropic
except ImportError:
    print("請安裝 LLM 客戶端庫")

from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown


class IssueType(Enum):
    """Issue 類型枚舉"""
    BUG = "bug"
    FEATURE = "feature"
    ENHANCEMENT = "enhancement"
    DOCUMENTATION = "documentation"
    PERFORMANCE = "performance"
    SECURITY = "security"
    QUESTION = "question"
    UNKNOWN = "unknown"


class Priority(Enum):
    """優先級枚舉"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


@dataclass
class ParsedIssue:
    """
    解析後的 Issue 數據結構

    包含從原始 Issue 中提取的所有結構化資訊
    """
    # 基本資訊
    number: int
    title: str
    body: str
    url: str
    created_at: datetime
    updated_at: datetime
    state: str

    # 分類資訊
    issue_type: IssueType
    priority: Priority
    labels: List[str]

    # 內容分析
    problem_description: str
    reproduction_steps: List[str]
    expected_behavior: str
    actual_behavior: str
    error_messages: List[str]

    # 環境資訊
    environment_info: Dict[str, str]
    affected_versions: List[str]

    # 相關資源
    related_files: List[str]
    related_functions: List[str]
    stack_traces: List[str]
    code_snippets: List[Dict[str, str]]

    # 元數據
    author: str
    assignees: List[str]
    comments_count: int

    def to_dict(self) -> Dict:
        """轉換為字典"""
        return asdict(self)


class GitHubIssueParser:
    """
    GitHub Issue 解析器

    負責從 GitHub API 獲取 Issue 並進行初步解析
    """

    def __init__(self, github_token: Optional[str] = None):
        """
        初始化解析器

        Args:
            github_token: GitHub API token
        """
        self.token = github_token or os.getenv("GITHUB_TOKEN")
        self.github = Github(self.token) if self.token else None
        self.console = Console()

        logger.info("GitHub Issue Parser 初始化完成")

    def fetch_issue(
        self,
        repo: str,
        issue_number: int
    ) -> Optional[GithubIssue]:
        """
        從 GitHub 獲取 Issue

        Args:
            repo: 儲存庫名稱 (格式: owner/repo)
            issue_number: Issue 編號

        Returns:
            GitHub Issue 對象
        """
        try:
            repository = self.github.get_repo(repo)
            issue = repository.get_issue(issue_number)

            logger.info(f"成功獲取 Issue #{issue_number} from {repo}")
            return issue

        except Exception as e:
            logger.error(f"獲取 Issue 失敗: {e}")
            return None

    def fetch_from_url(self, issue_url: str) -> Optional[GithubIssue]:
        """
        從 URL 獲取 Issue

        Args:
            issue_url: Issue URL

        Returns:
            GitHub Issue 對象
        """
        # 解析 URL: https://github.com/owner/repo/issues/123
        pattern = r"github\.com/([^/]+)/([^/]+)/issues/(\d+)"
        match = re.search(pattern, issue_url)

        if not match:
            logger.error(f"無效的 Issue URL: {issue_url}")
            return None

        owner, repo, number = match.groups()
        return self.fetch_issue(f"{owner}/{repo}", int(number))

    def parse_basic_info(self, issue: GithubIssue) -> Dict:
        """
        解析基本資訊

        Args:
            issue: GitHub Issue 對象

        Returns:
            基本資訊字典
        """
        return {
            "number": issue.number,
            "title": issue.title,
            "body": issue.body or "",
            "url": issue.html_url,
            "created_at": issue.created_at,
            "updated_at": issue.updated_at,
            "state": issue.state,
            "author": issue.user.login,
            "assignees": [a.login for a in issue.assignees],
            "labels": [label.name for label in issue.labels],
            "comments_count": issue.comments
        }

    def extract_code_blocks(self, text: str) -> List[Dict[str, str]]:
        """
        提取代碼區塊

        Args:
            text: Issue 文本

        Returns:
            代碼區塊列表
        """
        # 匹配 Markdown 代碼區塊
        pattern = r"```(\w+)?\n(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)

        code_blocks = []
        for language, code in matches:
            code_blocks.append({
                "language": language or "text",
                "code": code.strip()
            })

        return code_blocks

    def extract_file_paths(self, text: str) -> List[str]:
        """
        提取檔案路徑

        Args:
            text: Issue 文本

        Returns:
            檔案路徑列表
        """
        # 常見的檔案路徑模式
        patterns = [
            r'`([a-zA-Z0-9_/\-\.]+\.(py|js|java|go|rb|cpp|h|tsx|jsx))`',
            r'File "([^"]+)"',
            r'at ([a-zA-Z0-9_/\-\.]+:\d+)'
        ]

        file_paths = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    file_paths.append(match[0])
                else:
                    file_paths.append(match)

        return list(set(file_paths))

    def extract_stack_traces(self, text: str) -> List[str]:
        """
        提取堆疊追蹤

        Args:
            text: Issue 文本

        Returns:
            堆疊追蹤列表
        """
        stack_traces = []

        # Python 堆疊追蹤
        python_pattern = r"Traceback \(most recent call last\):.*?(?=\n\n|\Z)"
        python_traces = re.findall(python_pattern, text, re.DOTALL)
        stack_traces.extend(python_traces)

        # JavaScript 堆疊追蹤
        js_pattern = r"Error:.*?at .*?(?=\n\n|\Z)"
        js_traces = re.findall(js_pattern, text, re.DOTALL)
        stack_traces.extend(js_traces)

        return stack_traces

    def extract_error_messages(self, text: str) -> List[str]:
        """
        提取錯誤訊息

        Args:
            text: Issue 文本

        Returns:
            錯誤訊息列表
        """
        error_patterns = [
            r"Error: (.+)",
            r"Exception: (.+)",
            r"ERROR: (.+)",
            r"FATAL: (.+)",
            r"Failed to (.+)"
        ]

        errors = []
        for pattern in error_patterns:
            matches = re.findall(pattern, text)
            errors.extend(matches)

        return list(set(errors))


class SemanticIssueAnalyzer:
    """
    語義 Issue 分析器

    使用 LLM 進行深度語義分析，提取高層次的資訊
    """

    def __init__(self, model: str = "gpt-4"):
        """
        初始化分析器

        Args:
            model: 使用的 LLM 模型
        """
        self.model = model
        self.console = Console()

        # 初始化 LLM 客戶端
        if "gpt" in model:
            self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        elif "claude" in model:
            self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        logger.info(f"語義分析器初始化完成 (模型: {model})")

    def classify_issue_type(self, issue_text: str) -> IssueType:
        """
        分類 Issue 類型

        Args:
            issue_text: Issue 文本

        Returns:
            Issue 類型
        """
        prompt = f"""
        分析以下 GitHub Issue 並判斷其類型。

        Issue 內容:
        {issue_text[:1000]}

        可能的類型：
        - bug: 程式錯誤或異常行為
        - feature: 新功能請求
        - enhancement: 現有功能改進
        - documentation: 文檔相關
        - performance: 性能問題
        - security: 安全問題
        - question: 問題諮詢

        只回答類型名稱，不要其他內容。
        """

        try:
            response = self._call_llm(prompt)
            type_str = response.strip().lower()

            # 映射到枚舉
            type_mapping = {
                "bug": IssueType.BUG,
                "feature": IssueType.FEATURE,
                "enhancement": IssueType.ENHANCEMENT,
                "documentation": IssueType.DOCUMENTATION,
                "performance": IssueType.PERFORMANCE,
                "security": IssueType.SECURITY,
                "question": IssueType.QUESTION
            }

            return type_mapping.get(type_str, IssueType.UNKNOWN)

        except Exception as e:
            logger.error(f"Issue 類型分類失敗: {e}")
            return IssueType.UNKNOWN

    def determine_priority(
        self,
        issue_text: str,
        labels: List[str]
    ) -> Priority:
        """
        判斷優先級

        Args:
            issue_text: Issue 文本
            labels: Issue 標籤

        Returns:
            優先級
        """
        # 首先從標籤判斷
        label_priority = {
            "critical": Priority.CRITICAL,
            "high": Priority.HIGH,
            "medium": Priority.MEDIUM,
            "low": Priority.LOW
        }

        for label in labels:
            label_lower = label.lower()
            for key, priority in label_priority.items():
                if key in label_lower:
                    return priority

        # 使用 LLM 判斷
        prompt = f"""
        分析以下 Issue 的優先級。

        Issue 內容:
        {issue_text[:1000]}

        考慮因素：
        - 是否影響生產環境
        - 影響範圍
        - 用戶體驗影響
        - 安全風險

        優先級：critical, high, medium, low
        只回答優先級，不要其他內容。
        """

        try:
            response = self._call_llm(prompt)
            priority_str = response.strip().lower()

            priority_mapping = {
                "critical": Priority.CRITICAL,
                "high": Priority.HIGH,
                "medium": Priority.MEDIUM,
                "low": Priority.LOW
            }

            return priority_mapping.get(priority_str, Priority.UNKNOWN)

        except Exception as e:
            logger.error(f"優先級判斷失敗: {e}")
            return Priority.UNKNOWN

    def extract_reproduction_steps(self, issue_text: str) -> List[str]:
        """
        提取重現步驟

        Args:
            issue_text: Issue 文本

        Returns:
            重現步驟列表
        """
        prompt = f"""
        從以下 Issue 中提取問題重現步驟。

        Issue 內容:
        {issue_text}

        請以編號列表形式返回步驟，每行一個步驟。
        如果沒有明確的重現步驟，請分析並推斷可能的步驟。
        """

        try:
            response = self._call_llm(prompt)

            # 解析步驟
            lines = response.strip().split('\n')
            steps = []

            for line in lines:
                # 移除編號前綴 (1., -, *, 等)
                step = re.sub(r'^\s*[\d\-\*\.]+\s*', '', line).strip()
                if step:
                    steps.append(step)

            return steps

        except Exception as e:
            logger.error(f"提取重現步驟失敗: {e}")
            return []

    def identify_related_components(
        self,
        issue_text: str,
        repo_structure: Optional[Dict] = None
    ) -> Dict[str, List[str]]:
        """
        識別相關組件

        Args:
            issue_text: Issue 文本
            repo_structure: 儲存庫結構

        Returns:
            相關組件字典（檔案、函數、模組等）
        """
        prompt = f"""
        分析以下 Issue 並識別可能相關的代碼組件。

        Issue 內容:
        {issue_text}

        請列出：
        1. 可能相關的檔案或模組
        2. 可能相關的函數或類別
        3. 可能涉及的系統組件

        以 JSON 格式返回。
        """

        try:
            response = self._call_llm(prompt)

            # 嘗試解析 JSON
            try:
                components = json.loads(response)
            except:
                # 如果不是 JSON，嘗試結構化解析
                components = self._parse_components_text(response)

            return components

        except Exception as e:
            logger.error(f"識別相關組件失敗: {e}")
            return {}

    def _call_llm(self, prompt: str) -> str:
        """
        調用 LLM

        Args:
            prompt: 提示詞

        Returns:
            LLM 回應
        """
        if "gpt" in self.model:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            return response.choices[0].message.content

        elif "claude" in self.model:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text

    def _parse_components_text(self, text: str) -> Dict[str, List[str]]:
        """解析組件文本"""
        components = {
            "files": [],
            "functions": [],
            "modules": []
        }

        # 簡單的文本解析邏輯
        lines = text.split('\n')
        current_category = None

        for line in lines:
            line = line.strip()
            if "file" in line.lower():
                current_category = "files"
            elif "function" in line.lower() or "class" in line.lower():
                current_category = "functions"
            elif "module" in line.lower() or "component" in line.lower():
                current_category = "modules"
            elif line and current_category:
                # 移除列表標記
                item = re.sub(r'^\s*[\d\-\*\.]+\s*', '', line).strip()
                if item:
                    components[current_category].append(item)

        return components


class IssueParsingPipeline:
    """
    完整的 Issue 解析管道

    整合語法解析和語義分析，生成完整的 ParsedIssue 對象
    """

    def __init__(
        self,
        github_token: Optional[str] = None,
        llm_model: str = "gpt-4"
    ):
        """初始化解析管道"""
        self.parser = GitHubIssueParser(github_token)
        self.analyzer = SemanticIssueAnalyzer(llm_model)
        self.console = Console()

        logger.info("Issue 解析管道初始化完成")

    def parse_issue(
        self,
        repo: str,
        issue_number: int
    ) -> Optional[ParsedIssue]:
        """
        完整解析一個 Issue

        Args:
            repo: 儲存庫名稱
            issue_number: Issue 編號

        Returns:
            ParsedIssue 對象
        """
        self.console.print(f"\n[bold]解析 Issue #{issue_number}...[/bold]")

        # 1. 獲取 Issue
        issue = self.parser.fetch_issue(repo, issue_number)
        if not issue:
            return None

        # 2. 基本解析
        basic_info = self.parser.parse_basic_info(issue)

        # 3. 提取結構化資訊
        code_blocks = self.parser.extract_code_blocks(basic_info["body"])
        file_paths = self.parser.extract_file_paths(basic_info["body"])
        stack_traces = self.parser.extract_stack_traces(basic_info["body"])
        errors = self.parser.extract_error_messages(basic_info["body"])

        # 4. 語義分析
        issue_type = self.analyzer.classify_issue_type(basic_info["body"])
        priority = self.analyzer.determine_priority(
            basic_info["body"],
            basic_info["labels"]
        )
        reproduction_steps = self.analyzer.extract_reproduction_steps(
            basic_info["body"]
        )
        components = self.analyzer.identify_related_components(
            basic_info["body"]
        )

        # 5. 構建 ParsedIssue
        parsed_issue = ParsedIssue(
            # 基本資訊
            number=basic_info["number"],
            title=basic_info["title"],
            body=basic_info["body"],
            url=basic_info["url"],
            created_at=basic_info["created_at"],
            updated_at=basic_info["updated_at"],
            state=basic_info["state"],

            # 分類
            issue_type=issue_type,
            priority=priority,
            labels=basic_info["labels"],

            # 內容分析
            problem_description=basic_info["title"],
            reproduction_steps=reproduction_steps,
            expected_behavior="",
            actual_behavior="",
            error_messages=errors,

            # 環境
            environment_info={},
            affected_versions=[],

            # 相關資源
            related_files=file_paths,
            related_functions=components.get("functions", []),
            stack_traces=stack_traces,
            code_snippets=code_blocks,

            # 元數據
            author=basic_info["author"],
            assignees=basic_info["assignees"],
            comments_count=basic_info["comments_count"]
        )

        self._display_parsed_issue(parsed_issue)

        return parsed_issue

    def _display_parsed_issue(self, parsed: ParsedIssue):
        """顯示解析結果"""
        # 基本資訊表格
        table = Table(title="Issue 解析結果")
        table.add_column("屬性", style="cyan")
        table.add_column("值", style="magenta")

        table.add_row("編號", f"#{parsed.number}")
        table.add_row("標題", parsed.title)
        table.add_row("類型", parsed.issue_type.value)
        table.add_row("優先級", parsed.priority.value)
        table.add_row("狀態", parsed.state)
        table.add_row("作者", parsed.author)

        self.console.print(table)

        # 相關檔案
        if parsed.related_files:
            self.console.print(f"\n[bold]相關檔案 ({len(parsed.related_files)}):[/bold]")
            for file in parsed.related_files[:5]:
                self.console.print(f"  • {file}")

        # 重現步驟
        if parsed.reproduction_steps:
            self.console.print(f"\n[bold]重現步驟:[/bold]")
            for i, step in enumerate(parsed.reproduction_steps, 1):
                self.console.print(f"  {i}. {step}")


def main():
    """主函數"""
    console = Console()

    console.print(Panel(
        "[bold]SWE-Agent Issue 解析範例[/bold]\n\n"
        "這個範例展示如何解析和分析 GitHub Issues",
        border_style="green"
    ))

    # 創建解析管道
    pipeline = IssueParsingPipeline(
        llm_model="gpt-4"
    )

    # 範例：解析一個 Issue
    # 請替換為實際的 repo 和 issue number
    repo = "django/django"
    issue_number = 12345

    parsed = pipeline.parse_issue(repo, issue_number)

    if parsed:
        # 保存結果
        output_dir = Path("outputs/parsed_issues")
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / f"issue_{issue_number}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(parsed.to_dict(), f, ensure_ascii=False, indent=2, default=str)

        console.print(f"\n[green]解析結果已保存: {output_file}[/green]")


if __name__ == "__main__":
    main()

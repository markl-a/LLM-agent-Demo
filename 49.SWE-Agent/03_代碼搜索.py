#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SWE-Agent 代碼搜索範例
=====================

這個範例展示如何使用 SWE-Agent 進行智能代碼搜索：
1. 語義代碼搜索
2. 符號搜索（函數、類別、變量）
3. 依賴關係追蹤
4. 調用鏈分析
5. 相似代碼查找
6. 交叉引用搜索

代碼搜索是定位問題根源的關鍵步驟，SWE-Agent 提供了
多種強大的搜索工具來幫助快速定位相關代碼。

作者: SWE-Agent 團隊
日期: 2025-12-31
"""

import os
import ast
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from collections import defaultdict
import json

# 代碼分析工具
try:
    from tree_sitter import Language, Parser
    import astroid
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name
    from pygments.formatters import TerminalFormatter
except ImportError:
    print("請安裝: pip install tree-sitter astroid pygments")

# SWE-Agent
from sweagent.search import CodeSearchEngine
from sweagent.indexing import CodeIndexer
from sweagent.analysis import DependencyAnalyzer

from loguru import logger
from rich.console import Console
from rich.tree import Tree
from rich.table import Table
from rich.syntax import Syntax
from rich.panel import Panel


@dataclass
class SearchResult:
    """
    搜索結果數據結構
    """
    file_path: str
    line_number: int
    column: int
    context: str
    matched_text: str
    score: float
    symbol_type: Optional[str] = None
    symbol_name: Optional[str] = None


@dataclass
class Symbol:
    """
    符號定義
    """
    name: str
    type: str  # function, class, variable, import
    file_path: str
    line_number: int
    signature: Optional[str] = None
    docstring: Optional[str] = None
    scope: Optional[str] = None


class SemanticCodeSearcher:
    """
    語義代碼搜索器

    使用向量嵌入和語義相似度進行代碼搜索
    """

    def __init__(self, repo_path: str, use_embeddings: bool = True):
        """
        初始化搜索器

        Args:
            repo_path: 代碼庫路徑
            use_embeddings: 是否使用向量嵌入
        """
        self.repo_path = Path(repo_path)
        self.use_embeddings = use_embeddings
        self.console = Console()

        # 初始化索引
        self.indexer = CodeIndexer(repo_path)
        self.index = None

        logger.info(f"語義搜索器初始化: {repo_path}")

    def build_index(self):
        """
        構建代碼索引

        包括：
        1. 文件索引
        2. 符號索引
        3. 語義索引（如果啟用）
        """
        self.console.print("[bold]構建代碼索引...[/bold]")

        # 掃描所有代碼文件
        code_files = self._discover_code_files()
        self.console.print(f"發現 {len(code_files)} 個代碼文件")

        # 構建索引
        self.index = {
            "files": {},
            "symbols": defaultdict(list),
            "imports": defaultdict(list),
            "embeddings": {} if self.use_embeddings else None
        }

        for file_path in code_files:
            self._index_file(file_path)

        self.console.print("[green]✓ 索引構建完成[/green]")

    def _discover_code_files(self) -> List[Path]:
        """
        發現所有代碼文件
        """
        extensions = {'.py', '.js', '.java', '.go', '.rb', '.cpp', '.h', '.tsx', '.jsx'}
        code_files = []

        for ext in extensions:
            code_files.extend(self.repo_path.rglob(f"*{ext}"))

        # 排除常見的忽略目錄
        exclude_dirs = {'node_modules', 'venv', '.git', '__pycache__', 'build', 'dist'}

        filtered_files = []
        for file in code_files:
            if not any(exc in file.parts for exc in exclude_dirs):
                filtered_files.append(file)

        return filtered_files

    def _index_file(self, file_path: Path):
        """
        索引單個文件
        """
        try:
            content = file_path.read_text(encoding='utf-8')

            # 基本文件信息
            self.index["files"][str(file_path)] = {
                "size": len(content),
                "lines": content.count('\n') + 1,
                "language": self._detect_language(file_path)
            }

            # 根據語言解析符號
            if file_path.suffix == '.py':
                self._index_python_file(file_path, content)
            elif file_path.suffix in {'.js', '.jsx', '.ts', '.tsx'}:
                self._index_javascript_file(file_path, content)

        except Exception as e:
            logger.warning(f"索引文件失敗 {file_path}: {e}")

    def _index_python_file(self, file_path: Path, content: str):
        """索引 Python 文件"""
        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                # 函數定義
                if isinstance(node, ast.FunctionDef):
                    symbol = Symbol(
                        name=node.name,
                        type="function",
                        file_path=str(file_path),
                        line_number=node.lineno,
                        signature=self._get_function_signature(node),
                        docstring=ast.get_docstring(node)
                    )
                    self.index["symbols"][node.name].append(symbol)

                # 類定義
                elif isinstance(node, ast.ClassDef):
                    symbol = Symbol(
                        name=node.name,
                        type="class",
                        file_path=str(file_path),
                        line_number=node.lineno,
                        docstring=ast.get_docstring(node)
                    )
                    self.index["symbols"][node.name].append(symbol)

                # 導入
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        self.index["imports"][str(file_path)].append({
                            "module": alias.name,
                            "alias": alias.asname,
                            "line": node.lineno
                        })

        except Exception as e:
            logger.warning(f"解析 Python 文件失敗: {e}")

    def _index_javascript_file(self, file_path: Path, content: str):
        """索引 JavaScript 文件"""
        # 簡化的 JavaScript 解析（實際應使用 tree-sitter）
        # 查找函數定義
        function_pattern = r'function\s+(\w+)\s*\([^)]*\)'
        for match in re.finditer(function_pattern, content):
            line_num = content[:match.start()].count('\n') + 1
            symbol = Symbol(
                name=match.group(1),
                type="function",
                file_path=str(file_path),
                line_number=line_num
            )
            self.index["symbols"][match.group(1)].append(symbol)

        # 查找類定義
        class_pattern = r'class\s+(\w+)'
        for match in re.finditer(class_pattern, content):
            line_num = content[:match.start()].count('\n') + 1
            symbol = Symbol(
                name=match.group(1),
                type="class",
                file_path=str(file_path),
                line_number=line_num
            )
            self.index["symbols"][match.group(1)].append(symbol)

    def search_by_name(self, query: str) -> List[SearchResult]:
        """
        按名稱搜索符號

        Args:
            query: 搜索查詢

        Returns:
            搜索結果列表
        """
        results = []

        for symbol_name, symbols in self.index["symbols"].items():
            if query.lower() in symbol_name.lower():
                for symbol in symbols:
                    # 讀取上下文
                    context = self._get_context(symbol.file_path, symbol.line_number)

                    result = SearchResult(
                        file_path=symbol.file_path,
                        line_number=symbol.line_number,
                        column=0,
                        context=context,
                        matched_text=symbol_name,
                        score=self._calculate_similarity(query, symbol_name),
                        symbol_type=symbol.type,
                        symbol_name=symbol_name
                    )
                    results.append(result)

        # 按相關性排序
        results.sort(key=lambda x: x.score, reverse=True)

        return results

    def search_by_pattern(self, pattern: str) -> List[SearchResult]:
        """
        按正則表達式搜索

        Args:
            pattern: 正則表達式

        Returns:
            搜索結果列表
        """
        results = []
        regex = re.compile(pattern, re.IGNORECASE)

        for file_path in self.index["files"].keys():
            try:
                content = Path(file_path).read_text(encoding='utf-8')
                lines = content.split('\n')

                for line_num, line in enumerate(lines, 1):
                    matches = regex.finditer(line)
                    for match in matches:
                        result = SearchResult(
                            file_path=file_path,
                            line_number=line_num,
                            column=match.start(),
                            context=self._get_context(file_path, line_num, 2),
                            matched_text=match.group(),
                            score=1.0
                        )
                        results.append(result)

            except Exception as e:
                logger.warning(f"搜索文件失敗 {file_path}: {e}")

        return results

    def search_semantically(self, query: str, top_k: int = 10) -> List[SearchResult]:
        """
        語義搜索

        使用代碼嵌入進行語義相似度搜索

        Args:
            query: 自然語言查詢
            top_k: 返回前 k 個結果

        Returns:
            搜索結果列表
        """
        if not self.use_embeddings:
            self.console.print("[yellow]語義搜索未啟用[/yellow]")
            return []

        # 這裡應該使用實際的嵌入模型
        # 示例實現
        self.console.print(f"[bold]執行語義搜索: {query}[/bold]")

        # TODO: 實現實際的語義搜索邏輯
        # 1. 將查詢編碼為向量
        # 2. 計算與代碼片段的相似度
        # 3. 返回最相關的結果

        return []

    def _get_context(
        self,
        file_path: str,
        line_number: int,
        context_lines: int = 3
    ) -> str:
        """
        獲取代碼上下文

        Args:
            file_path: 文件路徑
            line_number: 行號
            context_lines: 上下文行數

        Returns:
            上下文字符串
        """
        try:
            content = Path(file_path).read_text(encoding='utf-8')
            lines = content.split('\n')

            start = max(0, line_number - context_lines - 1)
            end = min(len(lines), line_number + context_lines)

            context = '\n'.join(lines[start:end])
            return context

        except Exception as e:
            logger.warning(f"獲取上下文失敗: {e}")
            return ""

    def _calculate_similarity(self, query: str, text: str) -> float:
        """
        計算相似度分數

        Args:
            query: 查詢字符串
            text: 目標字符串

        Returns:
            相似度分數 (0-1)
        """
        query = query.lower()
        text = text.lower()

        # 完全匹配
        if query == text:
            return 1.0

        # 包含匹配
        if query in text:
            return 0.8

        # 開頭匹配
        if text.startswith(query):
            return 0.6

        # 子序列匹配
        if all(c in text for c in query):
            return 0.4

        return 0.0

    def _get_function_signature(self, node: ast.FunctionDef) -> str:
        """獲取函數簽名"""
        args = []
        for arg in node.args.args:
            args.append(arg.arg)

        return f"{node.name}({', '.join(args)})"

    def _detect_language(self, file_path: Path) -> str:
        """檢測編程語言"""
        ext_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.go': 'go',
            '.rb': 'ruby',
            '.cpp': 'cpp',
            '.h': 'cpp'
        }
        return ext_map.get(file_path.suffix, 'unknown')


class DependencyGraphBuilder:
    """
    依賴關係圖構建器

    構建代碼之間的依賴關係圖，用於追蹤調用鏈和影響範圍
    """

    def __init__(self, repo_path: str):
        """初始化"""
        self.repo_path = Path(repo_path)
        self.graph = defaultdict(set)
        self.reverse_graph = defaultdict(set)
        self.console = Console()

    def build_dependency_graph(self):
        """構建依賴關係圖"""
        self.console.print("[bold]構建依賴關係圖...[/bold]")

        python_files = list(self.repo_path.rglob("*.py"))

        for file_path in python_files:
            self._analyze_file_dependencies(file_path)

        self.console.print(f"[green]✓ 分析了 {len(python_files)} 個文件[/green]")

    def _analyze_file_dependencies(self, file_path: Path):
        """分析文件依賴"""
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content)

            current_module = self._path_to_module(file_path)

            # 分析導入
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.graph[current_module].add(alias.name)
                        self.reverse_graph[alias.name].add(current_module)

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        self.graph[current_module].add(node.module)
                        self.reverse_graph[node.module].add(current_module)

        except Exception as e:
            logger.warning(f"分析依賴失敗 {file_path}: {e}")

    def find_dependencies(self, module: str) -> Set[str]:
        """
        查找模塊的所有依賴

        Args:
            module: 模塊名稱

        Returns:
            依賴集合
        """
        return self.graph.get(module, set())

    def find_dependents(self, module: str) -> Set[str]:
        """
        查找依賴於指定模塊的所有模塊

        Args:
            module: 模塊名稱

        Returns:
            依賴者集合
        """
        return self.reverse_graph.get(module, set())

    def find_impact_scope(self, module: str, max_depth: int = 3) -> Set[str]:
        """
        查找變更影響範圍

        Args:
            module: 模塊名稱
            max_depth: 最大深度

        Returns:
            影響範圍集合
        """
        impact = set()
        to_visit = [(module, 0)]
        visited = set()

        while to_visit:
            current, depth = to_visit.pop(0)

            if current in visited or depth > max_depth:
                continue

            visited.add(current)
            impact.add(current)

            # 添加直接依賴者
            for dependent in self.find_dependents(current):
                to_visit.append((dependent, depth + 1))

        return impact

    def visualize_dependencies(self, module: str, max_depth: int = 2):
        """
        可視化依賴關係

        Args:
            module: 模塊名稱
            max_depth: 最大深度
        """
        tree = Tree(f"[bold cyan]{module}[/bold cyan]")

        self._build_dependency_tree(tree, module, max_depth, set())

        self.console.print(tree)

    def _build_dependency_tree(
        self,
        tree: Tree,
        module: str,
        max_depth: int,
        visited: Set[str]
    ):
        """遞歸構建依賴樹"""
        if max_depth <= 0 or module in visited:
            return

        visited.add(module)
        dependencies = self.find_dependencies(module)

        for dep in dependencies:
            branch = tree.add(f"[green]{dep}[/green]")
            self._build_dependency_tree(branch, dep, max_depth - 1, visited)

    def _path_to_module(self, file_path: Path) -> str:
        """將文件路徑轉換為模塊名"""
        relative = file_path.relative_to(self.repo_path)
        module = str(relative).replace('/', '.').replace('\\', '.')
        if module.endswith('.py'):
            module = module[:-3]
        return module


class CallGraphAnalyzer:
    """
    調用圖分析器

    分析函數和方法之間的調用關係
    """

    def __init__(self, repo_path: str):
        """初始化"""
        self.repo_path = Path(repo_path)
        self.call_graph = defaultdict(set)
        self.console = Console()

    def build_call_graph(self):
        """構建調用圖"""
        self.console.print("[bold]構建調用圖...[/bold]")

        python_files = list(self.repo_path.rglob("*.py"))

        for file_path in python_files:
            self._analyze_file_calls(file_path)

        self.console.print("[green]✓ 調用圖構建完成[/green]")

    def _analyze_file_calls(self, file_path: Path):
        """分析文件中的函數調用"""
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content)

            current_function = None

            for node in ast.walk(tree):
                # 進入函數定義
                if isinstance(node, ast.FunctionDef):
                    current_function = f"{file_path.stem}.{node.name}"

                # 記錄函數調用
                elif isinstance(node, ast.Call) and current_function:
                    if isinstance(node.func, ast.Name):
                        called = node.func.id
                        self.call_graph[current_function].add(called)

        except Exception as e:
            logger.warning(f"分析調用失敗 {file_path}: {e}")

    def find_call_chain(
        self,
        start_function: str,
        end_function: str,
        max_depth: int = 5
    ) -> List[List[str]]:
        """
        查找調用鏈

        Args:
            start_function: 起始函數
            end_function: 結束函數
            max_depth: 最大深度

        Returns:
            調用鏈列表
        """
        chains = []

        def dfs(current: str, path: List[str], depth: int):
            if depth > max_depth:
                return

            if current == end_function:
                chains.append(path + [current])
                return

            for called in self.call_graph.get(current, []):
                if called not in path:  # 避免循環
                    dfs(called, path + [current], depth + 1)

        dfs(start_function, [], 0)

        return chains

    def display_call_chains(self, chains: List[List[str]]):
        """顯示調用鏈"""
        if not chains:
            self.console.print("[yellow]未找到調用鏈[/yellow]")
            return

        self.console.print(f"\n[bold]找到 {len(chains)} 條調用鏈:[/bold]\n")

        for i, chain in enumerate(chains, 1):
            self.console.print(f"鏈 {i}:")
            for j, func in enumerate(chain):
                indent = "  " * j
                arrow = "→ " if j < len(chain) - 1 else ""
                self.console.print(f"{indent}{arrow}{func}")
            self.console.print()


def main():
    """主函數"""
    console = Console()

    console.print(Panel(
        "[bold]SWE-Agent 代碼搜索範例[/bold]\n\n"
        "展示各種代碼搜索和分析功能",
        border_style="green"
    ))

    # 示例代碼庫路徑
    repo_path = "/path/to/your/repo"

    # 1. 語義搜索
    console.print("\n[bold cyan]1. 語義代碼搜索[/bold cyan]")
    searcher = SemanticCodeSearcher(repo_path)
    searcher.build_index()

    # 按名稱搜索
    results = searcher.search_by_name("calculate")
    console.print(f"找到 {len(results)} 個結果")

    # 2. 依賴關係分析
    console.print("\n[bold cyan]2. 依賴關係分析[/bold cyan]")
    dep_builder = DependencyGraphBuilder(repo_path)
    dep_builder.build_dependency_graph()

    # 可視化依賴
    dep_builder.visualize_dependencies("myapp.utils", max_depth=2)

    # 3. 調用圖分析
    console.print("\n[bold cyan]3. 調用圖分析[/bold cyan]")
    call_analyzer = CallGraphAnalyzer(repo_path)
    call_analyzer.build_call_graph()

    # 查找調用鏈
    chains = call_analyzer.find_call_chain("main", "process_data")
    call_analyzer.display_call_chains(chains)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SWE-Agent 多語言支援範例
========================

這個範例展示如何使用 SWE-Agent 處理多種程式語言的代碼庫：
1. 語言檢測和識別
2. 多語言 AST 解析
3. 跨語言依賴分析
4. 語言特定的工具選擇
5. 混合語言項目處理
6. 語言遷移輔助

SWE-Agent 支援 Python、JavaScript、TypeScript、Java、Go、
Ruby、C++ 等多種主流程式語言。

作者: SWE-Agent 團隊
日期: 2025-12-31
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import subprocess

# 多語言解析工具
try:
    import tree_sitter
    from tree_sitter import Language, Parser
    import astroid  # Python
    import esprima  # JavaScript
except ImportError:
    print("請安裝: pip install tree-sitter astroid esprima")

from loguru import logger
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich.syntax import Syntax


class ProgrammingLanguage(Enum):
    """程式語言枚舉"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    GO = "go"
    RUBY = "ruby"
    CPP = "cpp"
    C = "c"
    RUST = "rust"
    PHP = "php"
    UNKNOWN = "unknown"


@dataclass
class LanguageConfig:
    """
    語言配置
    """
    language: ProgrammingLanguage
    extensions: List[str]
    comment_styles: Dict[str, str]
    build_command: Optional[str] = None
    test_command: Optional[str] = None
    lint_command: Optional[str] = None
    format_command: Optional[str] = None


@dataclass
class CodeElement:
    """
    代碼元素（跨語言通用）
    """
    element_type: str  # function, class, variable, import
    name: str
    language: ProgrammingLanguage
    file_path: str
    line_number: int
    signature: Optional[str] = None
    docstring: Optional[str] = None
    modifiers: List[str] = field(default_factory=list)
    children: List['CodeElement'] = field(default_factory=list)


class LanguageDetector:
    """
    語言檢測器

    自動檢測文件的程式語言
    """

    # 語言配置映射
    LANGUAGE_CONFIGS = {
        ProgrammingLanguage.PYTHON: LanguageConfig(
            language=ProgrammingLanguage.PYTHON,
            extensions=['.py', '.pyw'],
            comment_styles={'line': '#', 'block_start': '"""', 'block_end': '"""'},
            build_command="python setup.py build",
            test_command="pytest",
            lint_command="pylint",
            format_command="black"
        ),
        ProgrammingLanguage.JAVASCRIPT: LanguageConfig(
            language=ProgrammingLanguage.JAVASCRIPT,
            extensions=['.js', '.jsx', '.mjs'],
            comment_styles={'line': '//', 'block_start': '/*', 'block_end': '*/'},
            build_command="npm run build",
            test_command="npm test",
            lint_command="eslint",
            format_command="prettier"
        ),
        ProgrammingLanguage.TYPESCRIPT: LanguageConfig(
            language=ProgrammingLanguage.TYPESCRIPT,
            extensions=['.ts', '.tsx'],
            comment_styles={'line': '//', 'block_start': '/*', 'block_end': '*/'},
            build_command="tsc",
            test_command="npm test",
            lint_command="eslint",
            format_command="prettier"
        ),
        ProgrammingLanguage.JAVA: LanguageConfig(
            language=ProgrammingLanguage.JAVA,
            extensions=['.java'],
            comment_styles={'line': '//', 'block_start': '/*', 'block_end': '*/'},
            build_command="mvn compile",
            test_command="mvn test",
            lint_command="checkstyle",
            format_command="google-java-format"
        ),
        ProgrammingLanguage.GO: LanguageConfig(
            language=ProgrammingLanguage.GO,
            extensions=['.go'],
            comment_styles={'line': '//', 'block_start': '/*', 'block_end': '*/'},
            build_command="go build",
            test_command="go test",
            lint_command="golint",
            format_command="gofmt"
        ),
        ProgrammingLanguage.RUBY: LanguageConfig(
            language=ProgrammingLanguage.RUBY,
            extensions=['.rb'],
            comment_styles={'line': '#', 'block_start': '=begin', 'block_end': '=end'},
            build_command=None,
            test_command="rspec",
            lint_command="rubocop",
            format_command="rubocop --auto-correct"
        ),
        ProgrammingLanguage.CPP: LanguageConfig(
            language=ProgrammingLanguage.CPP,
            extensions=['.cpp', '.cc', '.cxx', '.hpp', '.h'],
            comment_styles={'line': '//', 'block_start': '/*', 'block_end': '*/'},
            build_command="cmake --build .",
            test_command="ctest",
            lint_command="clang-tidy",
            format_command="clang-format"
        ),
        ProgrammingLanguage.RUST: LanguageConfig(
            language=ProgrammingLanguage.RUST,
            extensions=['.rs'],
            comment_styles={'line': '//', 'block_start': '/*', 'block_end': '*/'},
            build_command="cargo build",
            test_command="cargo test",
            lint_command="cargo clippy",
            format_command="cargo fmt"
        )
    }

    def __init__(self):
        """初始化語言檢測器"""
        self.console = Console()

        # 構建擴展名到語言的映射
        self.ext_to_lang = {}
        for lang_config in self.LANGUAGE_CONFIGS.values():
            for ext in lang_config.extensions:
                self.ext_to_lang[ext] = lang_config.language

    def detect_language(self, file_path: Path) -> ProgrammingLanguage:
        """
        檢測文件語言

        Args:
            file_path: 文件路徑

        Returns:
            程式語言
        """
        # 首先通過擴展名檢測
        suffix = file_path.suffix.lower()
        if suffix in self.ext_to_lang:
            return self.ext_to_lang[suffix]

        # 通過文件內容檢測
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            return self._detect_by_content(content)
        except:
            return ProgrammingLanguage.UNKNOWN

    def _detect_by_content(self, content: str) -> ProgrammingLanguage:
        """通過內容檢測語言"""
        # 檢查 shebang
        if content.startswith('#!'):
            first_line = content.split('\n')[0]
            if 'python' in first_line:
                return ProgrammingLanguage.PYTHON
            elif 'node' in first_line or 'javascript' in first_line:
                return ProgrammingLanguage.JAVASCRIPT
            elif 'ruby' in first_line:
                return ProgrammingLanguage.RUBY

        # 語言特徵模式
        patterns = {
            ProgrammingLanguage.PYTHON: [r'\bdef\s+\w+\(', r'\bclass\s+\w+:', r'\bimport\s+\w+'],
            ProgrammingLanguage.JAVASCRIPT: [r'\bfunction\s+\w+\(', r'\bconst\s+\w+\s*=', r'\blet\s+\w+\s*='],
            ProgrammingLanguage.JAVA: [r'\bpublic\s+class\s+\w+', r'\bprivate\s+\w+\s+\w+\('],
            ProgrammingLanguage.GO: [r'\bfunc\s+\w+\(', r'\bpackage\s+\w+'],
            ProgrammingLanguage.RUST: [r'\bfn\s+\w+\(', r'\buse\s+\w+'],
        }

        scores = {}
        for lang, lang_patterns in patterns.items():
            score = sum(1 for p in lang_patterns if re.search(p, content))
            scores[lang] = score

        if scores:
            best_match = max(scores.items(), key=lambda x: x[1])
            if best_match[1] > 0:
                return best_match[0]

        return ProgrammingLanguage.UNKNOWN

    def get_config(self, language: ProgrammingLanguage) -> Optional[LanguageConfig]:
        """
        獲取語言配置

        Args:
            language: 程式語言

        Returns:
            語言配置
        """
        return self.LANGUAGE_CONFIGS.get(language)


class LanguageParser(ABC):
    """
    語言解析器抽象基類
    """

    @abstractmethod
    def parse_file(self, file_path: Path) -> List[CodeElement]:
        """
        解析文件

        Args:
            file_path: 文件路徑

        Returns:
            代碼元素列表
        """
        pass

    @abstractmethod
    def extract_functions(self, file_path: Path) -> List[CodeElement]:
        """提取函數"""
        pass

    @abstractmethod
    def extract_classes(self, file_path: Path) -> List[CodeElement]:
        """提取類"""
        pass


class PythonParser(LanguageParser):
    """
    Python 解析器
    """

    def __init__(self):
        """初始化"""
        self.console = Console()

    def parse_file(self, file_path: Path) -> List[CodeElement]:
        """解析 Python 文件"""
        elements = []

        try:
            content = file_path.read_text(encoding='utf-8')
            import ast
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    element = CodeElement(
                        element_type="function",
                        name=node.name,
                        language=ProgrammingLanguage.PYTHON,
                        file_path=str(file_path),
                        line_number=node.lineno,
                        signature=self._get_function_signature(node),
                        docstring=ast.get_docstring(node)
                    )
                    elements.append(element)

                elif isinstance(node, ast.ClassDef):
                    element = CodeElement(
                        element_type="class",
                        name=node.name,
                        language=ProgrammingLanguage.PYTHON,
                        file_path=str(file_path),
                        line_number=node.lineno,
                        docstring=ast.get_docstring(node)
                    )

                    # 提取類的方法
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            method = CodeElement(
                                element_type="method",
                                name=item.name,
                                language=ProgrammingLanguage.PYTHON,
                                file_path=str(file_path),
                                line_number=item.lineno,
                                signature=self._get_function_signature(item)
                            )
                            element.children.append(method)

                    elements.append(element)

        except Exception as e:
            logger.warning(f"解析 Python 文件失敗 {file_path}: {e}")

        return elements

    def extract_functions(self, file_path: Path) -> List[CodeElement]:
        """提取函數"""
        elements = self.parse_file(file_path)
        return [e for e in elements if e.element_type == "function"]

    def extract_classes(self, file_path: Path) -> List[CodeElement]:
        """提取類"""
        elements = self.parse_file(file_path)
        return [e for e in elements if e.element_type == "class"]

    def _get_function_signature(self, node) -> str:
        """獲取函數簽名"""
        import ast
        args = []
        for arg in node.args.args:
            args.append(arg.arg)
        return f"{node.name}({', '.join(args)})"


class JavaScriptParser(LanguageParser):
    """
    JavaScript/TypeScript 解析器
    """

    def __init__(self):
        """初始化"""
        self.console = Console()

    def parse_file(self, file_path: Path) -> List[CodeElement]:
        """解析 JavaScript 文件"""
        elements = []

        try:
            content = file_path.read_text(encoding='utf-8')

            # 使用正則表達式提取（簡化版本）
            # 實際應該使用 esprima 或 tree-sitter

            # 提取函數
            function_pattern = r'function\s+(\w+)\s*\(([^)]*)\)'
            for match in re.finditer(function_pattern, content):
                line_num = content[:match.start()].count('\n') + 1
                element = CodeElement(
                    element_type="function",
                    name=match.group(1),
                    language=ProgrammingLanguage.JAVASCRIPT,
                    file_path=str(file_path),
                    line_number=line_num,
                    signature=f"{match.group(1)}({match.group(2)})"
                )
                elements.append(element)

            # 提取箭頭函數
            arrow_pattern = r'const\s+(\w+)\s*=\s*\(([^)]*)\)\s*=>'
            for match in re.finditer(arrow_pattern, content):
                line_num = content[:match.start()].count('\n') + 1
                element = CodeElement(
                    element_type="function",
                    name=match.group(1),
                    language=ProgrammingLanguage.JAVASCRIPT,
                    file_path=str(file_path),
                    line_number=line_num,
                    signature=f"{match.group(1)}({match.group(2)})"
                )
                elements.append(element)

            # 提取類
            class_pattern = r'class\s+(\w+)'
            for match in re.finditer(class_pattern, content):
                line_num = content[:match.start()].count('\n') + 1
                element = CodeElement(
                    element_type="class",
                    name=match.group(1),
                    language=ProgrammingLanguage.JAVASCRIPT,
                    file_path=str(file_path),
                    line_number=line_num
                )
                elements.append(element)

        except Exception as e:
            logger.warning(f"解析 JavaScript 文件失敗 {file_path}: {e}")

        return elements

    def extract_functions(self, file_path: Path) -> List[CodeElement]:
        """提取函數"""
        elements = self.parse_file(file_path)
        return [e for e in elements if e.element_type == "function"]

    def extract_classes(self, file_path: Path) -> List[CodeElement]:
        """提取類"""
        elements = self.parse_file(file_path)
        return [e for e in elements if e.element_type == "class"]


class MultiLanguageCodebase:
    """
    多語言代碼庫管理器

    處理包含多種程式語言的代碼庫
    """

    def __init__(self, repo_path: str):
        """
        初始化

        Args:
            repo_path: 代碼庫路徑
        """
        self.repo_path = Path(repo_path)
        self.console = Console()

        self.detector = LanguageDetector()
        self.parsers = {
            ProgrammingLanguage.PYTHON: PythonParser(),
            ProgrammingLanguage.JAVASCRIPT: JavaScriptParser(),
            ProgrammingLanguage.TYPESCRIPT: JavaScriptParser(),
        }

        self.language_stats = {}
        self.file_map = {}

        logger.info(f"多語言代碼庫管理器初始化: {repo_path}")

    def analyze_languages(self) -> Dict[ProgrammingLanguage, int]:
        """
        分析代碼庫中的語言分布

        Returns:
            語言統計
        """
        self.console.print("[bold]分析語言分布...[/bold]")

        language_counts = {}

        # 掃描所有代碼文件
        code_extensions = {
            '.py', '.js', '.jsx', '.ts', '.tsx',
            '.java', '.go', '.rb', '.cpp', '.c', '.h', '.rs'
        }

        for file_path in self.repo_path.rglob("*"):
            if file_path.suffix in code_extensions:
                lang = self.detector.detect_language(file_path)

                if lang not in language_counts:
                    language_counts[lang] = 0

                language_counts[lang] += 1
                self.file_map[str(file_path)] = lang

        self.language_stats = language_counts

        self._display_language_stats()

        return language_counts

    def _display_language_stats(self):
        """顯示語言統計"""
        table = Table(title="語言分布")
        table.add_column("語言", style="cyan")
        table.add_column("文件數", style="magenta")
        table.add_column("百分比")

        total = sum(self.language_stats.values())

        for lang, count in sorted(
            self.language_stats.items(),
            key=lambda x: x[1],
            reverse=True
        ):
            percentage = (count / total * 100) if total > 0 else 0

            table.add_row(
                lang.value,
                str(count),
                f"{percentage:.1f}%"
            )

        self.console.print(table)

    def parse_all_files(self) -> Dict[str, List[CodeElement]]:
        """
        解析所有文件

        Returns:
            文件到代碼元素的映射
        """
        self.console.print("[bold]解析所有文件...[/bold]")

        all_elements = {}

        for file_path_str, lang in self.file_map.items():
            file_path = Path(file_path_str)

            # 獲取對應的解析器
            parser = self.parsers.get(lang)

            if parser:
                try:
                    elements = parser.parse_file(file_path)
                    all_elements[file_path_str] = elements
                except Exception as e:
                    logger.warning(f"解析文件失敗 {file_path}: {e}")

        self.console.print(f"成功解析 {len(all_elements)} 個文件")

        return all_elements

    def find_cross_language_dependencies(self) -> List[Tuple[str, str]]:
        """
        查找跨語言依賴

        Returns:
            依賴關係列表
        """
        self.console.print("[bold]查找跨語言依賴...[/bold]")

        dependencies = []

        # 例如：Python 調用 JavaScript（通過 subprocess）
        # JavaScript 調用 Python API 等

        # 簡化實現：查找 subprocess 調用、HTTP 請求等

        for file_path_str, lang in self.file_map.items():
            if lang == ProgrammingLanguage.PYTHON:
                try:
                    content = Path(file_path_str).read_text(encoding='utf-8')

                    # 查找 subprocess 調用
                    if 'subprocess' in content:
                        # 提取被調用的命令
                        patterns = [
                            r'subprocess\.call\(["\']([^"\']+)',
                            r'subprocess\.run\(["\']([^"\']+)'
                        ]

                        for pattern in patterns:
                            matches = re.findall(pattern, content)
                            for match in matches:
                                if match.endswith('.js') or match.endswith('.sh'):
                                    dependencies.append((file_path_str, match))

                except Exception as e:
                    logger.warning(f"分析依賴失敗: {e}")

        self.console.print(f"發現 {len(dependencies)} 個跨語言依賴")

        return dependencies

    def run_language_specific_tools(
        self,
        language: ProgrammingLanguage,
        tool_type: str
    ) -> Dict:
        """
        運行語言特定工具

        Args:
            language: 程式語言
            tool_type: 工具類型 (test, lint, format, build)

        Returns:
            執行結果
        """
        config = self.detector.get_config(language)

        if not config:
            self.console.print(f"[yellow]不支援的語言: {language}[/yellow]")
            return {"success": False, "error": "unsupported language"}

        command = getattr(config, f"{tool_type}_command", None)

        if not command:
            self.console.print(f"[yellow]未配置 {tool_type} 命令[/yellow]")
            return {"success": False, "error": "command not configured"}

        self.console.print(f"[bold]運行 {language.value} {tool_type}: {command}[/bold]")

        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=300
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }

        except Exception as e:
            logger.error(f"運行工具失敗: {e}")
            return {"success": False, "error": str(e)}


class LanguageMigrationHelper:
    """
    語言遷移輔助器

    幫助將代碼從一種語言遷移到另一種語言
    """

    def __init__(self, model: str = "gpt-4"):
        """初始化"""
        self.model = model
        self.console = Console()

    def translate_code(
        self,
        source_code: str,
        from_lang: ProgrammingLanguage,
        to_lang: ProgrammingLanguage
    ) -> Optional[str]:
        """
        翻譯代碼

        Args:
            source_code: 源代碼
            from_lang: 源語言
            to_lang: 目標語言

        Returns:
            翻譯後的代碼
        """
        self.console.print(
            f"[bold]翻譯代碼: {from_lang.value} → {to_lang.value}[/bold]"
        )

        # 這裡應該使用 LLM 進行代碼翻譯
        # 示例實現

        prompt = f"""
        將以下 {from_lang.value} 代碼翻譯為 {to_lang.value}：

        ```{from_lang.value}
        {source_code}
        ```

        只返回翻譯後的代碼，不要其他說明。
        """

        # TODO: 實際的 LLM 調用

        return None

    def suggest_migration_strategy(
        self,
        repo_path: str,
        target_lang: ProgrammingLanguage
    ) -> Dict:
        """
        建議遷移策略

        Args:
            repo_path: 代碼庫路徑
            target_lang: 目標語言

        Returns:
            遷移策略
        """
        strategy = {
            "target_language": target_lang.value,
            "phases": [],
            "estimated_effort": "unknown",
            "risks": []
        }

        # 分析現有代碼庫
        codebase = MultiLanguageCodebase(repo_path)
        codebase.analyze_languages()

        # 建議分階段遷移
        # TODO: 實現實際的策略生成邏輯

        return strategy


def main():
    """主函數"""
    console = Console()

    console.print(Panel(
        "[bold]SWE-Agent 多語言支援範例[/bold]\n\n"
        "展示處理多語言代碼庫的能力",
        border_style="green"
    ))

    # 示例代碼庫路徑
    repo_path = "/path/to/your/repo"

    # 1. 分析語言分布
    console.print("\n[bold cyan]1. 語言分析[/bold cyan]")
    codebase = MultiLanguageCodebase(repo_path)
    lang_stats = codebase.analyze_languages()

    # 2. 解析所有文件
    console.print("\n[bold cyan]2. 解析代碼[/bold cyan]")
    elements = codebase.parse_all_files()

    # 3. 查找跨語言依賴
    console.print("\n[bold cyan]3. 跨語言依賴分析[/bold cyan]")
    dependencies = codebase.find_cross_language_dependencies()

    # 4. 運行語言特定工具
    console.print("\n[bold cyan]4. 運行測試[/bold cyan]")
    test_result = codebase.run_language_specific_tools(
        ProgrammingLanguage.PYTHON,
        "test"
    )


if __name__ == "__main__":
    main()

"""
Continue AI 編程助手 - 上下文提供者

這個文件展示了如何創建和使用上下文提供者。
上下文提供者負責收集和提供相關的代碼上下文,幫助 AI 更好地理解問題。

主要內容:
1. 上下文提供者基類
2. 文件上下文提供者
3. Git 上下文提供者
4. 終端輸出上下文提供者
5. 文檔搜索上下文提供者
6. 代碼庫搜索上下文提供者
7. 依賴分析上下文提供者
8. 自定義上下文提供者

Author: Continue Team
Date: 2025
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
import os
import re
import subprocess
from datetime import datetime


# =====================================================
# 第一部分: 上下文類型定義
# =====================================================

class ContextType(Enum):
    """
    上下文類型枚舉
    """
    FILE = "file"  # 文件內容
    DIRECTORY = "directory"  # 目錄結構
    GIT = "git"  # Git 歷史和狀態
    TERMINAL = "terminal"  # 終端輸出
    DOCUMENTATION = "documentation"  # 文檔
    CODEBASE = "codebase"  # 代碼庫搜索
    DEPENDENCIES = "dependencies"  # 依賴關係
    SYMBOLS = "symbols"  # 符號定義
    REFERENCES = "references"  # 引用關係
    CUSTOM = "custom"  # 自定義


class ContextPriority(Enum):
    """
    上下文優先級
    """
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class ContextItem:
    """
    上下文項

    表示一個具體的上下文信息片段
    """
    type: ContextType  # 上下文類型
    content: str  # 內容
    source: str  # 來源
    priority: ContextPriority = ContextPriority.MEDIUM  # 優先級
    metadata: Dict[str, Any] = field(default_factory=dict)  # 元數據
    timestamp: datetime = field(default_factory=datetime.now)  # 時間戳

    def __str__(self) -> str:
        """字符串表示"""
        return f"[{self.type.value}] {self.source}: {self.content[:100]}..."


@dataclass
class Context:
    """
    上下文集合

    包含多個上下文項的集合
    """
    items: List[ContextItem] = field(default_factory=list)
    max_tokens: int = 4000  # 最大 token 數

    def add_item(self, item: ContextItem):
        """
        添加上下文項

        Args:
            item: 上下文項
        """
        self.items.append(item)

    def get_items_by_type(self, context_type: ContextType) -> List[ContextItem]:
        """
        按類型獲取上下文項

        Args:
            context_type: 上下文類型

        Returns:
            上下文項列表
        """
        return [item for item in self.items if item.type == context_type]

    def get_items_by_priority(self, min_priority: ContextPriority) -> List[ContextItem]:
        """
        按優先級過濾上下文項

        Args:
            min_priority: 最小優先級

        Returns:
            上下文項列表
        """
        return [item for item in self.items if item.priority.value >= min_priority.value]

    def sort_by_priority(self):
        """
        按優先級排序
        """
        self.items.sort(key=lambda x: x.priority.value, reverse=True)

    def truncate_to_fit(self):
        """
        截斷以適應 token 限制
        """
        # 簡化版本,實際需要計算 token 數
        total_chars = sum(len(item.content) for item in self.items)
        if total_chars > self.max_tokens * 4:  # 粗略估算
            # 保留高優先級項目
            self.sort_by_priority()
            # 這裡需要更複雜的邏輯來智能截斷

    def to_string(self) -> str:
        """
        轉換為字符串格式

        Returns:
            格式化的上下文字符串
        """
        self.sort_by_priority()
        result = "=== 上下文信息 ===\n\n"

        for item in self.items:
            result += f"[{item.type.value}] {item.source}\n"
            result += f"{item.content}\n\n"

        return result


# =====================================================
# 第二部分: 上下文提供者基類
# =====================================================

class ContextProvider(ABC):
    """
    上下文提供者抽象基類

    所有上下文提供者都應繼承此類
    """

    def __init__(self, name: str, context_type: ContextType):
        """
        初始化上下文提供者

        Args:
            name: 提供者名稱
            context_type: 提供的上下文類型
        """
        self.name = name
        self.context_type = context_type
        self.enabled = True

    @abstractmethod
    def provide(self, query: str, **kwargs) -> List[ContextItem]:
        """
        提供上下文

        Args:
            query: 用戶查詢
            **kwargs: 額外參數

        Returns:
            上下文項列表
        """
        pass

    def enable(self):
        """啟用提供者"""
        self.enabled = True

    def disable(self):
        """禁用提供者"""
        self.enabled = False

    def is_enabled(self) -> bool:
        """
        檢查是否啟用

        Returns:
            是否啟用
        """
        return self.enabled


# =====================================================
# 第三部分: 文件上下文提供者
# =====================================================

class FileContextProvider(ContextProvider):
    """
    文件上下文提供者

    提供當前文件和相關文件的上下文
    """

    def __init__(self, workspace_root: str):
        """
        初始化文件上下文提供者

        Args:
            workspace_root: 工作區根目錄
        """
        super().__init__("文件上下文", ContextType.FILE)
        self.workspace_root = Path(workspace_root)
        self.max_file_size = 100_000  # 最大文件大小(字節)
        self.file_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.go'}

    def provide(self, query: str, **kwargs) -> List[ContextItem]:
        """
        提供文件上下文

        Args:
            query: 查詢
            **kwargs: 可選參數
                - current_file: 當前文件路徑
                - related_files: 相關文件列表

        Returns:
            上下文項列表
        """
        items = []

        # 獲取當前文件
        current_file = kwargs.get('current_file')
        if current_file:
            item = self._read_file(current_file, ContextPriority.HIGH)
            if item:
                items.append(item)

        # 獲取相關文件
        related_files = kwargs.get('related_files', [])
        for file_path in related_files:
            item = self._read_file(file_path, ContextPriority.MEDIUM)
            if item:
                items.append(item)

        # 自動查找相關文件
        auto_files = self._find_related_files(query, current_file)
        for file_path in auto_files:
            if str(file_path) not in [str(current_file)] + related_files:
                item = self._read_file(file_path, ContextPriority.LOW)
                if item:
                    items.append(item)

        return items

    def _read_file(self, file_path: str, priority: ContextPriority) -> Optional[ContextItem]:
        """
        讀取文件內容

        Args:
            file_path: 文件路徑
            priority: 優先級

        Returns:
            上下文項或 None
        """
        try:
            path = Path(file_path)

            # 檢查文件大小
            if path.stat().st_size > self.max_file_size:
                return None

            # 讀取內容
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            return ContextItem(
                type=ContextType.FILE,
                content=content,
                source=str(path.relative_to(self.workspace_root)),
                priority=priority,
                metadata={
                    'size': path.stat().st_size,
                    'extension': path.suffix
                }
            )
        except Exception as e:
            print(f"讀取文件失敗 {file_path}: {e}")
            return None

    def _find_related_files(self, query: str, current_file: Optional[str]) -> List[Path]:
        """
        查找相關文件

        Args:
            query: 查詢
            current_file: 當前文件

        Returns:
            相關文件路徑列表
        """
        related = []

        if not current_file:
            return related

        current_path = Path(current_file)

        # 查找同目錄下的相關文件
        if current_path.exists():
            parent_dir = current_path.parent

            # 查找導入的文件
            imports = self._extract_imports(current_path)
            for imp in imports:
                related_path = self._resolve_import(imp, parent_dir)
                if related_path and related_path.exists():
                    related.append(related_path)

        return related[:5]  # 限制數量

    def _extract_imports(self, file_path: Path) -> List[str]:
        """
        提取導入語句

        Args:
            file_path: 文件路徑

        Returns:
            導入列表
        """
        imports = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Python imports
            if file_path.suffix == '.py':
                # import xxx
                imports.extend(re.findall(r'import\s+(\w+)', content))
                # from xxx import yyy
                imports.extend(re.findall(r'from\s+(\w+)\s+import', content))

            # JavaScript/TypeScript imports
            elif file_path.suffix in {'.js', '.ts', '.jsx', '.tsx'}:
                # import ... from '...'
                imports.extend(re.findall(r"from\s+['\"](.+?)['\"]", content))

        except Exception as e:
            print(f"提取導入失敗: {e}")

        return imports

    def _resolve_import(self, import_name: str, base_dir: Path) -> Optional[Path]:
        """
        解析導入路徑

        Args:
            import_name: 導入名稱
            base_dir: 基礎目錄

        Returns:
            解析後的路徑
        """
        # 簡化版本,實際需要更複雜的邏輯
        for ext in self.file_extensions:
            path = base_dir / f"{import_name}{ext}"
            if path.exists():
                return path

        return None


class DirectoryContextProvider(ContextProvider):
    """
    目錄結構上下文提供者

    提供項目的目錄結構信息
    """

    def __init__(self, workspace_root: str):
        """
        初始化目錄上下文提供者

        Args:
            workspace_root: 工作區根目錄
        """
        super().__init__("目錄結構", ContextType.DIRECTORY)
        self.workspace_root = Path(workspace_root)
        self.ignore_patterns = {
            '__pycache__', 'node_modules', '.git', '.venv',
            'venv', 'build', 'dist', '.idea'
        }

    def provide(self, query: str, **kwargs) -> List[ContextItem]:
        """
        提供目錄結構上下文

        Args:
            query: 查詢
            **kwargs: 額外參數

        Returns:
            上下文項列表
        """
        max_depth = kwargs.get('max_depth', 3)
        tree = self._generate_tree(self.workspace_root, max_depth)

        return [
            ContextItem(
                type=ContextType.DIRECTORY,
                content=tree,
                source="項目結構",
                priority=ContextPriority.MEDIUM,
                metadata={'max_depth': max_depth}
            )
        ]

    def _generate_tree(self, root: Path, max_depth: int, current_depth: int = 0) -> str:
        """
        生成目錄樹

        Args:
            root: 根目錄
            max_depth: 最大深度
            current_depth: 當前深度

        Returns:
            目錄樹字符串
        """
        if current_depth >= max_depth:
            return ""

        lines = []
        indent = "  " * current_depth

        try:
            for item in sorted(root.iterdir()):
                # 跳過忽略的目錄
                if item.name in self.ignore_patterns:
                    continue

                if item.is_dir():
                    lines.append(f"{indent}📁 {item.name}/")
                    lines.append(self._generate_tree(item, max_depth, current_depth + 1))
                else:
                    lines.append(f"{indent}📄 {item.name}")

        except PermissionError:
            pass

        return "\n".join(lines)


# =====================================================
# 第四部分: Git 上下文提供者
# =====================================================

class GitContextProvider(ContextProvider):
    """
    Git 上下文提供者

    提供 Git 歷史、狀態和變更信息
    """

    def __init__(self, workspace_root: str):
        """
        初始化 Git 上下文提供者

        Args:
            workspace_root: 工作區根目錄
        """
        super().__init__("Git 上下文", ContextType.GIT)
        self.workspace_root = workspace_root

    def provide(self, query: str, **kwargs) -> List[ContextItem]:
        """
        提供 Git 上下文

        Args:
            query: 查詢
            **kwargs: 額外參數

        Returns:
            上下文項列表
        """
        items = []

        # Git 狀態
        status = self._get_git_status()
        if status:
            items.append(ContextItem(
                type=ContextType.GIT,
                content=status,
                source="Git 狀態",
                priority=ContextPriority.MEDIUM
            ))

        # 最近提交
        recent_commits = self._get_recent_commits(5)
        if recent_commits:
            items.append(ContextItem(
                type=ContextType.GIT,
                content=recent_commits,
                source="最近提交",
                priority=ContextPriority.LOW
            ))

        # 當前分支
        branch = self._get_current_branch()
        if branch:
            items.append(ContextItem(
                type=ContextType.GIT,
                content=f"當前分支: {branch}",
                source="分支信息",
                priority=ContextPriority.LOW
            ))

        return items

    def _run_git_command(self, command: List[str]) -> Optional[str]:
        """
        運行 Git 命令

        Args:
            command: Git 命令列表

        Returns:
            命令輸出
        """
        try:
            result = subprocess.run(
                ['git'] + command,
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.strip() if result.returncode == 0 else None
        except Exception as e:
            print(f"Git 命令執行失敗: {e}")
            return None

    def _get_git_status(self) -> Optional[str]:
        """獲取 Git 狀態"""
        return self._run_git_command(['status', '--short'])

    def _get_recent_commits(self, count: int) -> Optional[str]:
        """
        獲取最近的提交

        Args:
            count: 提交數量

        Returns:
            提交歷史
        """
        return self._run_git_command([
            'log',
            f'-{count}',
            '--oneline',
            '--decorate'
        ])

    def _get_current_branch(self) -> Optional[str]:
        """獲取當前分支"""
        return self._run_git_command(['branch', '--show-current'])

    def _get_file_history(self, file_path: str, count: int = 5) -> Optional[str]:
        """
        獲取文件歷史

        Args:
            file_path: 文件路徑
            count: 歷史記錄數量

        Returns:
            文件歷史
        """
        return self._run_git_command([
            'log',
            f'-{count}',
            '--oneline',
            '--',
            file_path
        ])


# =====================================================
# 第五部分: 終端輸出上下文提供者
# =====================================================

class TerminalContextProvider(ContextProvider):
    """
    終端輸出上下文提供者

    提供最近的終端命令和輸出
    """

    def __init__(self, max_lines: int = 100):
        """
        初始化終端上下文提供者

        Args:
            max_lines: 最大行數
        """
        super().__init__("終端輸出", ContextType.TERMINAL)
        self.max_lines = max_lines
        self.command_history: List[Dict[str, str]] = []

    def provide(self, query: str, **kwargs) -> List[ContextItem]:
        """
        提供終端上下文

        Args:
            query: 查詢
            **kwargs: 額外參數

        Returns:
            上下文項列表
        """
        items = []

        # 獲取最近的命令和輸出
        recent_commands = self.command_history[-5:]  # 最近 5 條命令

        for cmd_info in recent_commands:
            content = f"命令: {cmd_info['command']}\n"
            content += f"輸出:\n{cmd_info['output']}"

            items.append(ContextItem(
                type=ContextType.TERMINAL,
                content=content,
                source="終端",
                priority=ContextPriority.MEDIUM,
                metadata={'command': cmd_info['command']}
            ))

        return items

    def add_command(self, command: str, output: str):
        """
        添加命令歷史

        Args:
            command: 命令
            output: 輸出
        """
        self.command_history.append({
            'command': command,
            'output': output[:1000],  # 限制輸出長度
            'timestamp': datetime.now()
        })

        # 保持歷史記錄在限制內
        if len(self.command_history) > 50:
            self.command_history = self.command_history[-50:]


# =====================================================
# 第六部分: 代碼庫搜索上下文提供者
# =====================================================

class CodebaseSearchProvider(ContextProvider):
    """
    代碼庫搜索上下文提供者

    在代碼庫中搜索相關代碼片段
    """

    def __init__(self, workspace_root: str):
        """
        初始化代碼庫搜索提供者

        Args:
            workspace_root: 工作區根目錄
        """
        super().__init__("代碼庫搜索", ContextType.CODEBASE)
        self.workspace_root = Path(workspace_root)

    def provide(self, query: str, **kwargs) -> List[ContextItem]:
        """
        提供代碼庫搜索上下文

        Args:
            query: 查詢
            **kwargs: 額外參數

        Returns:
            上下文項列表
        """
        items = []

        # 提取查詢中的關鍵詞
        keywords = self._extract_keywords(query)

        # 在代碼庫中搜索
        for keyword in keywords:
            results = self._search_keyword(keyword)
            items.extend(results)

        return items[:10]  # 限制結果數量

    def _extract_keywords(self, query: str) -> List[str]:
        """
        從查詢中提取關鍵詞

        Args:
            query: 查詢

        Returns:
            關鍵詞列表
        """
        # 簡單實現:提取長度 > 3 的單詞
        words = re.findall(r'\b\w{4,}\b', query)
        return words[:5]  # 限制數量

    def _search_keyword(self, keyword: str) -> List[ContextItem]:
        """
        搜索關鍵詞

        Args:
            keyword: 關鍵詞

        Returns:
            上下文項列表
        """
        items = []

        # 這裡應該使用更高效的搜索工具,如 ripgrep
        # 簡化版本僅作示例
        try:
            for py_file in self.workspace_root.rglob("*.py"):
                if self._should_skip(py_file):
                    continue

                matches = self._search_in_file(py_file, keyword)
                items.extend(matches)

        except Exception as e:
            print(f"搜索失敗: {e}")

        return items

    def _should_skip(self, path: Path) -> bool:
        """
        是否應該跳過此路徑

        Args:
            path: 文件路徑

        Returns:
            是否跳過
        """
        skip_dirs = {'__pycache__', 'node_modules', '.git', 'venv'}
        return any(skip_dir in path.parts for skip_dir in skip_dirs)

    def _search_in_file(self, file_path: Path, keyword: str) -> List[ContextItem]:
        """
        在文件中搜索

        Args:
            file_path: 文件路徑
            keyword: 關鍵詞

        Returns:
            匹配的上下文項
        """
        items = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            for i, line in enumerate(lines):
                if keyword.lower() in line.lower():
                    # 獲取上下文(前後各 2 行)
                    start = max(0, i - 2)
                    end = min(len(lines), i + 3)
                    context_lines = lines[start:end]

                    content = f"文件: {file_path.name}\n"
                    content += f"行 {i + 1}:\n"
                    content += "".join(context_lines)

                    items.append(ContextItem(
                        type=ContextType.CODEBASE,
                        content=content,
                        source=str(file_path.relative_to(self.workspace_root)),
                        priority=ContextPriority.LOW,
                        metadata={'line_number': i + 1}
                    ))

        except Exception as e:
            pass

        return items


# =====================================================
# 第七部分: 上下文管理器
# =====================================================

class ContextManager:
    """
    上下文管理器

    協調多個上下文提供者,收集和管理上下文
    """

    def __init__(self, workspace_root: str):
        """
        初始化上下文管理器

        Args:
            workspace_root: 工作區根目錄
        """
        self.workspace_root = workspace_root
        self.providers: List[ContextProvider] = []
        self._setup_default_providers()

    def _setup_default_providers(self):
        """設置默認提供者"""
        self.providers = [
            FileContextProvider(self.workspace_root),
            DirectoryContextProvider(self.workspace_root),
            GitContextProvider(self.workspace_root),
            TerminalContextProvider(),
            CodebaseSearchProvider(self.workspace_root)
        ]

    def add_provider(self, provider: ContextProvider):
        """
        添加提供者

        Args:
            provider: 上下文提供者
        """
        self.providers.append(provider)

    def collect_context(self, query: str, **kwargs) -> Context:
        """
        收集上下文

        Args:
            query: 用戶查詢
            **kwargs: 額外參數

        Returns:
            上下文對象
        """
        context = Context()

        # 從所有啟用的提供者收集上下文
        for provider in self.providers:
            if provider.is_enabled():
                try:
                    items = provider.provide(query, **kwargs)
                    for item in items:
                        context.add_item(item)
                except Exception as e:
                    print(f"提供者 {provider.name} 失敗: {e}")

        # 優化上下文
        context.truncate_to_fit()

        return context


# =====================================================
# 第八部分: 使用示例
# =====================================================

def basic_context_example():
    """
    基本上下文使用示例
    """
    print("=" * 60)
    print("示例 1: 基本上下文收集")
    print("=" * 60)

    # 創建上下文管理器
    manager = ContextManager("/path/to/workspace")

    # 收集上下文
    context = manager.collect_context(
        "如何優化 Python 代碼?",
        current_file="/path/to/workspace/main.py"
    )

    # 顯示上下文
    print(context.to_string())


def main():
    """
    主函數
    """
    print("Continue - 上下文提供者\n")
    basic_context_example()


if __name__ == "__main__":
    main()

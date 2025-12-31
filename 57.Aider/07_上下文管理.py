"""
Aider 上下文管理
================

本範例展示 Aider 的上下文管理功能，包括：
- Repository Map
- Token 優化
- 文件選擇策略
- 增量上下文更新
- 大型代碼庫處理

作者：AI Agent Demo
日期：2025-12-31
"""

from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import ast


class ContextStrategy(Enum):
    """上下文策略"""
    MINIMAL = "minimal"        # 最小上下文
    BALANCED = "balanced"      # 平衡模式
    COMPREHENSIVE = "comprehensive"  # 全面上下文
    CUSTOM = "custom"          # 自定義


@dataclass
class FileContext:
    """
    文件上下文

    表示單個文件的上下文資訊。
    """
    path: Path
    size: int
    token_count: int
    priority: int = 0
    dependencies: Set[Path] = field(default_factory=set)
    dependents: Set[Path] = field(default_factory=set)

    def __str__(self) -> str:
        return f"{self.path.name} ({self.token_count} tokens, priority: {self.priority})"


class RepositoryMap:
    """
    Repository Map

    Aider 的核心功能之一，生成代碼庫的結構地圖，
    幫助 AI 理解項目結構而不需要讀取所有文件內容。
    """

    def __init__(self, project_root: Path):
        """
        初始化 Repository Map

        Args:
            project_root: 專案根目錄
        """
        self.project_root = project_root
        self.file_tree: Dict[str, any] = {}
        self.symbols: Dict[str, List[str]] = {}

    def generate_map(self) -> Dict:
        """
        生成 repository map

        Returns:
            包含專案結構和符號資訊的字典
        """
        print("\n生成 Repository Map...")

        # 掃描目錄結構
        self._scan_directory(self.project_root)

        # 提取符號
        self._extract_symbols()

        map_data = {
            "tree": self.file_tree,
            "symbols": self.symbols,
            "stats": self._calculate_stats()
        }

        return map_data

    def _scan_directory(self, directory: Path, prefix: str = "") -> Dict:
        """
        遞迴掃描目錄

        Args:
            directory: 要掃描的目錄
            prefix: 路徑前綴

        Returns:
            目錄結構字典
        """
        structure = {}

        try:
            for item in sorted(directory.iterdir()):
                # 跳過隱藏文件和常見的忽略目錄
                if item.name.startswith('.') or item.name in ['node_modules', '__pycache__', 'venv']:
                    continue

                if item.is_dir():
                    structure[item.name] = self._scan_directory(item, f"{prefix}{item.name}/")
                else:
                    # 只記錄源代碼文件
                    if item.suffix in ['.py', '.js', '.ts', '.java', '.go', '.rs']:
                        structure[item.name] = {
                            "type": "file",
                            "size": item.stat().st_size,
                            "extension": item.suffix
                        }

        except PermissionError:
            pass

        self.file_tree = structure
        return structure

    def _extract_symbols(self) -> None:
        """
        從 Python 文件中提取符號（類、函數等）
        """
        python_files = list(self.project_root.rglob("*.py"))

        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())

                symbols = []

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        symbols.append(f"class {node.name}")
                    elif isinstance(node, ast.FunctionDef):
                        if not node.name.startswith('_'):  # 跳過私有方法
                            symbols.append(f"def {node.name}")

                if symbols:
                    rel_path = file_path.relative_to(self.project_root)
                    self.symbols[str(rel_path)] = symbols

            except Exception:
                pass

    def _calculate_stats(self) -> Dict:
        """
        計算統計資訊

        Returns:
            統計字典
        """
        return {
            "total_files": len(self.symbols),
            "total_symbols": sum(len(syms) for syms in self.symbols.values()),
            "languages": self._detect_languages()
        }

    def _detect_languages(self) -> List[str]:
        """
        檢測專案使用的程式語言

        Returns:
            語言列表
        """
        languages = set()

        def scan(tree: Dict):
            for key, value in tree.items():
                if isinstance(value, dict):
                    if "extension" in value:
                        ext_to_lang = {
                            '.py': 'Python',
                            '.js': 'JavaScript',
                            '.ts': 'TypeScript',
                            '.java': 'Java',
                            '.go': 'Go',
                            '.rs': 'Rust'
                        }
                        lang = ext_to_lang.get(value["extension"])
                        if lang:
                            languages.add(lang)
                    else:
                        scan(value)

        scan(self.file_tree)
        return list(languages)

    def print_map(self, max_depth: int = 3) -> None:
        """
        打印 repository map

        Args:
            max_depth: 最大顯示深度
        """
        print("\n" + "=" * 60)
        print("Repository Map")
        print("=" * 60)

        def print_tree(tree: Dict, depth: int = 0, prefix: str = ""):
            if depth >= max_depth:
                return

            items = list(tree.items())
            for i, (name, value) in enumerate(items):
                is_last = i == len(items) - 1
                connector = "└── " if is_last else "├── "

                if isinstance(value, dict) and "type" in value:
                    # 文件
                    size_kb = value["size"] / 1024
                    print(f"{prefix}{connector}{name} ({size_kb:.1f} KB)")
                else:
                    # 目錄
                    print(f"{prefix}{connector}{name}/")
                    new_prefix = prefix + ("    " if is_last else "│   ")
                    print_tree(value, depth + 1, new_prefix)

        print_tree(self.file_tree)

        # 打印符號統計
        print("\n符號統計:")
        for file_path, symbols in list(self.symbols.items())[:5]:
            print(f"\n{file_path}:")
            for symbol in symbols[:10]:
                print(f"  - {symbol}")
            if len(symbols) > 10:
                print(f"  ... 還有 {len(symbols) - 10} 個")


class ContextManager:
    """
    上下文管理器

    智能管理發送給 AI 的上下文，優化 Token 使用。
    """

    def __init__(
        self,
        project_root: Path,
        max_tokens: int = 4000,
        strategy: ContextStrategy = ContextStrategy.BALANCED
    ):
        """
        初始化上下文管理器

        Args:
            project_root: 專案根目錄
            max_tokens: 最大 token 數量
            strategy: 上下文策略
        """
        self.project_root = project_root
        self.max_tokens = max_tokens
        self.strategy = strategy
        self.file_contexts: Dict[Path, FileContext] = {}
        self.active_files: Set[Path] = set()

    def add_file(self, file_path: Path) -> bool:
        """
        添加文件到上下文

        Args:
            file_path: 文件路徑

        Returns:
            是否成功添加
        """
        if not file_path.exists():
            print(f"✗ 文件不存在: {file_path}")
            return False

        # 估算 token 數量
        token_count = self._estimate_tokens(file_path)

        # 檢查是否超過限制
        current_tokens = self.get_total_tokens()

        if current_tokens + token_count > self.max_tokens:
            print(f"✗ 添加 {file_path.name} 會超過 token 限制")
            print(f"  當前: {current_tokens}, 文件: {token_count}, 限制: {self.max_tokens}")

            # 嘗試移除低優先級文件
            if not self._make_room(token_count):
                return False

        # 添加文件
        context = FileContext(
            path=file_path,
            size=file_path.stat().st_size,
            token_count=token_count
        )

        self.file_contexts[file_path] = context
        self.active_files.add(file_path)

        print(f"✓ 添加 {file_path.name} ({token_count} tokens)")
        return True

    def _estimate_tokens(self, file_path: Path) -> int:
        """
        估算文件的 token 數量

        簡化的估算：大約 1 token = 4 字符

        Args:
            file_path: 文件路徑

        Returns:
            估算的 token 數量
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 簡化估算：4 字符 ≈ 1 token
            return len(content) // 4

        except Exception:
            return 0

    def get_total_tokens(self) -> int:
        """
        獲取當前總 token 數

        Returns:
            總 token 數
        """
        return sum(
            ctx.token_count
            for path, ctx in self.file_contexts.items()
            if path in self.active_files
        )

    def _make_room(self, needed_tokens: int) -> bool:
        """
        為新文件騰出空間

        移除低優先級的文件以騰出空間。

        Args:
            needed_tokens: 需要的 token 數量

        Returns:
            是否成功騰出空間
        """
        # 按優先級排序
        sorted_files = sorted(
            [(path, ctx) for path, ctx in self.file_contexts.items()
             if path in self.active_files],
            key=lambda x: x[1].priority
        )

        freed_tokens = 0

        for file_path, context in sorted_files:
            if freed_tokens >= needed_tokens:
                break

            self.active_files.remove(file_path)
            freed_tokens += context.token_count
            print(f"  移除 {file_path.name} 以騰出空間")

        return freed_tokens >= needed_tokens

    def remove_file(self, file_path: Path) -> bool:
        """
        從上下文中移除文件

        Args:
            file_path: 文件路徑

        Returns:
            是否成功移除
        """
        if file_path in self.active_files:
            self.active_files.remove(file_path)
            print(f"✓ 移除 {file_path.name}")
            return True

        print(f"✗ 文件不在上下文中: {file_path.name}")
        return False

    def set_priority(self, file_path: Path, priority: int) -> None:
        """
        設置文件優先級

        優先級越高，文件越不容易被移除。

        Args:
            file_path: 文件路徑
            priority: 優先級（0-10）
        """
        if file_path in self.file_contexts:
            self.file_contexts[file_path].priority = priority
            print(f"✓ 設置 {file_path.name} 優先級為 {priority}")

    def auto_select_files(
        self,
        target_file: Path,
        max_files: int = 5
    ) -> List[Path]:
        """
        自動選擇相關文件

        基於依賴關係和文件類型智能選擇相關文件。

        Args:
            target_file: 目標文件
            max_files: 最多選擇的文件數

        Returns:
            相關文件列表
        """
        print(f"\n自動選擇與 {target_file.name} 相關的文件...")

        related_files = set()

        # 1. 添加目標文件
        related_files.add(target_file)

        # 2. 查找測試文件
        test_file = self._find_test_file(target_file)
        if test_file:
            related_files.add(test_file)
            print(f"  找到測試文件: {test_file.name}")

        # 3. 查找同目錄的相關文件
        sibling_files = self._find_sibling_files(target_file)
        for f in sibling_files[:max_files - len(related_files)]:
            related_files.add(f)
            print(f"  找到相關文件: {f.name}")

        return list(related_files)[:max_files]

    def _find_test_file(self, file_path: Path) -> Optional[Path]:
        """
        查找對應的測試文件

        Args:
            file_path: 源文件路徑

        Returns:
            測試文件路徑，如果找不到則返回 None
        """
        # 嘗試多個可能的測試文件位置
        possible_paths = [
            file_path.parent / f"test_{file_path.name}",
            self.project_root / "tests" / f"test_{file_path.name}",
            self.project_root / "test" / f"test_{file_path.name}",
        ]

        for test_path in possible_paths:
            if test_path.exists():
                return test_path

        return None

    def _find_sibling_files(self, file_path: Path) -> List[Path]:
        """
        查找同目錄的相關文件

        Args:
            file_path: 文件路徑

        Returns:
            相關文件列表
        """
        sibling_files = []

        if file_path.parent.exists():
            for sibling in file_path.parent.iterdir():
                if (sibling.is_file() and
                    sibling.suffix == file_path.suffix and
                    sibling != file_path and
                    not sibling.name.startswith('test_')):
                    sibling_files.append(sibling)

        return sibling_files

    def print_status(self) -> None:
        """打印當前上下文狀態"""
        print("\n" + "=" * 60)
        print("上下文狀態")
        print("=" * 60)

        total_tokens = self.get_total_tokens()
        usage_percent = (total_tokens / self.max_tokens) * 100

        print(f"\nToken 使用: {total_tokens} / {self.max_tokens} ({usage_percent:.1f}%)")
        print(f"策略: {self.strategy.value}")
        print(f"活躍文件: {len(self.active_files)}")

        print("\n文件列表:")
        for file_path in self.active_files:
            context = self.file_contexts[file_path]
            print(f"  {context}")


def demonstrate_context_management():
    """
    演示上下文管理

    展示如何使用 Aider 的上下文管理功能。
    """
    print("\n" + "=" * 60)
    print("Aider 上下文管理演示")
    print("=" * 60)

    print("""
## 1. Repository Map

Repository Map 是 Aider 的核心功能，它生成代碼庫的結構概覽，
讓 AI 能夠理解專案結構而不需要讀取所有文件。

### 啟用 Repository Map

```bash
# 使用默認設置（1024 tokens）
aider

# 自定義 map tokens
aider --map-tokens 2048

# 完全禁用 repository map
aider --no-map
```

### Repository Map 的內容

```
project/
├── src/
│   ├── main.py
│   │   - class Application
│   │   - def main()
│   ├── models.py
│   │   - class User
│   │   - class Product
│   └── utils.py
│       - def validate_email()
│       - def hash_password()
└── tests/
    ├── test_models.py
    └── test_utils.py
```

### 優勢

✓ 讓 AI 了解專案結構
✓ 節省 tokens
✓ 自動發現相關文件
✓ 更好的上下文理解

## 2. 手動管理文件

### 添加文件到會話

```bash
$ aider

> /add src/models.py
Added src/models.py

> /add src/utils.py tests/test_utils.py
Added src/utils.py
Added tests/test_utils.py
```

### 移除文件

```bash
> /drop src/utils.py
Removed src/utils.py
```

### 查看當前文件

```bash
> /ls
Files in chat:
- src/models.py (450 tokens)
- tests/test_utils.py (320 tokens)
Total: 770 tokens / 4000 max
```

## 3. 自動文件選擇

Aider 可以自動選擇相關文件：

```bash
$ aider --auto-select

> 請修改 User 類

# Aider 自動添加：
# - src/models.py (包含 User 類)
# - tests/test_models.py (User 類的測試)
# - src/database.py (User 類使用的數據庫模組)
```

## 4. Token 優化策略

### 最小上下文

```bash
aider --context minimal
```

只包含當前正在修改的文件。

### 平衡模式（默認）

```bash
aider --context balanced
```

包含當前文件和直接依賴。

### 全面上下文

```bash
aider --context comprehensive
```

包含所有相關文件和依賴。

## 5. 增量更新

Aider 智能地管理上下文更新：

```
初始請求: 修改 User 類
上下文: models.py (100%)

後續請求: 添加驗證
上下文: models.py (70%) + utils.py (30%)
- 保留核心上下文
- 添加新相關文件

再次請求: 生成測試
上下文: models.py (40%) + tests/test_models.py (60%)
- 降低源文件優先級
- 提高測試文件優先級
```

## 6. 大型代碼庫處理

對於大型專案（1000+ 文件）：

```bash
# 使用大的 repository map
aider --map-tokens 4096

# 啟用智能文件過濾
aider --auto-select --smart-context

# 只關注特定目錄
aider src/auth/*.py
```

## 7. 上下文警告

當接近 token 限制時：

```
⚠️  Warning: Approaching token limit (3800/4000)
Consider removing less relevant files with /drop
```

## 8. 配置文件

創建 `.aider.context.yml`：

```yaml
context:
  # 最大 tokens
  max_tokens: 4000

  # Repository map tokens
  map_tokens: 1024

  # 策略
  strategy: balanced

  # 自動選擇相關文件
  auto_select: true

  # 最多自動添加的文件數
  max_auto_files: 5

  # 文件優先級規則
  priority_rules:
    - pattern: "test_*.py"
      priority: 8
    - pattern: "*_test.py"
      priority: 8
    - pattern: "models.py"
      priority: 9
    - pattern: "*.md"
      priority: 2
```
    """)


def main():
    """
    主函數

    運行上下文管理演示。
    """
    # 創建示例目錄
    demo_root = Path("./aider_context_demo")
    demo_root.mkdir(exist_ok=True)

    # 演示 Repository Map
    print("\n演示 Repository Map")
    repo_map = RepositoryMap(demo_root)

    # 創建一些示例文件
    (demo_root / "main.py").write_text("def main(): pass")
    (demo_root / "utils.py").write_text("def helper(): pass")

    map_data = repo_map.generate_map()
    repo_map.print_map()

    # 演示上下文管理
    print("\n\n演示上下文管理")
    context_mgr = ContextManager(demo_root, max_tokens=1000)

    # 添加文件
    context_mgr.add_file(demo_root / "main.py")
    context_mgr.add_file(demo_root / "utils.py")

    # 顯示狀態
    context_mgr.print_status()

    # 演示文檔
    demonstrate_context_management()


if __name__ == "__main__":
    main()

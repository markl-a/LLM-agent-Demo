"""
Aider 多文件編輯功能
====================

本範例展示 Aider 的多文件編輯能力，包括：
- 跨文件重構
- 協調多個文件的修改
- 依賴追蹤和更新
- 批量操作

作者：AI Agent Demo
日期：2025-12-31
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import ast
import re


class FileChangeType(Enum):
    """文件變更類型"""
    CREATE = "create"          # 創建新文件
    MODIFY = "modify"          # 修改現有文件
    DELETE = "delete"          # 刪除文件
    RENAME = "rename"          # 重命名文件
    REFACTOR = "refactor"      # 重構


@dataclass
class FileChange:
    """
    文件變更記錄

    記錄單個文件的變更資訊，包括變更類型、路徑、內容等。
    """
    file_path: Path
    change_type: FileChangeType
    old_content: Optional[str] = None
    new_content: Optional[str] = None
    description: str = ""
    dependencies: Set[Path] = field(default_factory=set)

    def __str__(self) -> str:
        """返回變更的字符串表示"""
        return f"{self.change_type.value}: {self.file_path} - {self.description}"


class MultiFileEditor:
    """
    多文件編輯器

    管理和協調多個文件的編輯操作，確保變更的一致性。
    這個類模擬了 Aider 如何處理跨文件的編輯任務。
    """

    def __init__(self, project_root: Path):
        """
        初始化多文件編輯器

        Args:
            project_root: 專案根目錄
        """
        self.project_root = project_root
        self.changes: List[FileChange] = []
        self.file_dependencies: Dict[Path, Set[Path]] = {}

    def analyze_dependencies(self, files: List[Path]) -> Dict[Path, Set[Path]]:
        """
        分析文件之間的依賴關係

        對於 Python 文件，分析 import 語句來確定依賴。
        這有助於在重構時確保所有相關文件都被更新。

        Args:
            files: 要分析的文件列表

        Returns:
            依賴關係字典，key 是文件路徑，value 是它依賴的文件集合
        """
        print("\n分析文件依賴關係...")

        dependencies = {}

        for file_path in files:
            if file_path.suffix == '.py':
                deps = self._analyze_python_imports(file_path)
                dependencies[file_path] = deps
                print(f"  {file_path.name}: {len(deps)} 個依賴")

        self.file_dependencies = dependencies
        return dependencies

    def _analyze_python_imports(self, file_path: Path) -> Set[Path]:
        """
        分析 Python 文件的 import 語句

        Args:
            file_path: Python 文件路徑

        Returns:
            該文件依賴的其他文件路徑集合
        """
        dependencies = set()

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        # 嘗試將模組名轉換為文件路徑
                        module_path = self._module_to_path(alias.name)
                        if module_path and module_path.exists():
                            dependencies.add(module_path)

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module_path = self._module_to_path(node.module)
                        if module_path and module_path.exists():
                            dependencies.add(module_path)

        except (SyntaxError, FileNotFoundError) as e:
            print(f"    警告: 無法分析 {file_path}: {e}")

        return dependencies

    def _module_to_path(self, module_name: str) -> Optional[Path]:
        """
        將模組名轉換為文件路徑

        Args:
            module_name: 模組名（如 'package.module'）

        Returns:
            對應的文件路徑，如果無法解析則返回 None
        """
        # 將 . 替換為路徑分隔符
        rel_path = module_name.replace('.', os.sep) + '.py'
        full_path = self.project_root / rel_path

        if full_path.exists():
            return full_path

        # 嘗試作為包
        package_path = self.project_root / module_name.replace('.', os.sep) / '__init__.py'
        if package_path.exists():
            return package_path

        return None

    def plan_refactoring(
        self,
        target: str,
        replacement: str,
        files: List[Path]
    ) -> List[FileChange]:
        """
        規劃重構操作

        分析需要重構的文件，生成變更計劃。
        例如重命名函數、類、變數等。

        Args:
            target: 要重構的目標（函數名、類名等）
            replacement: 替換後的名稱
            files: 涉及的文件列表

        Returns:
            變更列表
        """
        print(f"\n規劃重構: {target} -> {replacement}")
        print(f"涉及 {len(files)} 個文件")

        changes = []

        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    old_content = f.read()

                # 檢查文件是否包含目標
                if target not in old_content:
                    print(f"  跳過 {file_path.name} (不包含 '{target}')")
                    continue

                # 執行替換
                new_content = self._smart_replace(old_content, target, replacement)

                # 創建變更記錄
                change = FileChange(
                    file_path=file_path,
                    change_type=FileChangeType.REFACTOR,
                    old_content=old_content,
                    new_content=new_content,
                    description=f"重構: {target} -> {replacement}"
                )

                changes.append(change)
                print(f"  ✓ {file_path.name}: 找到 {old_content.count(target)} 處")

            except Exception as e:
                print(f"  ✗ 處理 {file_path.name} 時出錯: {e}")

        self.changes.extend(changes)
        return changes

    def _smart_replace(self, content: str, target: str, replacement: str) -> str:
        """
        智能替換

        只替換完整的標識符，避免部分匹配。
        例如，替換 'user' 時不會影響 'username'。

        Args:
            content: 原始內容
            target: 目標字符串
            replacement: 替換字符串

        Returns:
            替換後的內容
        """
        # 使用正則表達式確保只匹配完整的單詞
        pattern = r'\b' + re.escape(target) + r'\b'
        return re.sub(pattern, replacement, content)

    def coordinate_changes(self, base_files: List[Path]) -> List[FileChange]:
        """
        協調多文件變更

        當修改一個文件時，自動識別並更新相關的其他文件。
        例如，修改 API 時更新對應的測試文件。

        Args:
            base_files: 基礎文件列表

        Returns:
            協調後的變更列表
        """
        print("\n協調多文件變更...")

        coordinated_changes = []

        for file_path in base_files:
            # 找到相關文件
            related_files = self._find_related_files(file_path)

            print(f"\n{file_path.name}:")
            print(f"  找到 {len(related_files)} 個相關文件")

            for related_file in related_files:
                print(f"    - {related_file.name}")

        return coordinated_changes

    def _find_related_files(self, file_path: Path) -> List[Path]:
        """
        找到與給定文件相關的其他文件

        相關文件可能包括：
        - 對應的測試文件
        - 依賴此文件的其他文件
        - 此文件依賴的其他文件

        Args:
            file_path: 目標文件路徑

        Returns:
            相關文件列表
        """
        related = []

        # 尋找測試文件
        if not file_path.name.startswith('test_'):
            test_file = file_path.parent / f"test_{file_path.name}"
            if test_file.exists():
                related.append(test_file)

            # 在 tests 目錄中尋找
            tests_dir = self.project_root / 'tests'
            if tests_dir.exists():
                test_file = tests_dir / f"test_{file_path.name}"
                if test_file.exists():
                    related.append(test_file)

        # 從依賴關係中找相關文件
        if file_path in self.file_dependencies:
            related.extend(self.file_dependencies[file_path])

        # 找依賴此文件的文件
        for other_file, deps in self.file_dependencies.items():
            if file_path in deps:
                related.append(other_file)

        return list(set(related))  # 去重

    def create_module_structure(
        self,
        module_name: str,
        components: List[str]
    ) -> List[FileChange]:
        """
        創建模組結構

        創建一個新的 Python 模組，包含多個組件文件。

        Args:
            module_name: 模組名稱
            components: 組件列表（如 ['models', 'views', 'controllers']）

        Returns:
            創建的文件變更列表
        """
        print(f"\n創建模組結構: {module_name}")

        changes = []
        module_dir = self.project_root / module_name
        module_dir.mkdir(exist_ok=True)

        # 創建 __init__.py
        init_file = module_dir / '__init__.py'
        init_content = f'"""\n{module_name} 模組\n"""\n\n'

        # 導入所有組件
        for component in components:
            init_content += f"from .{component} import *\n"

        change = FileChange(
            file_path=init_file,
            change_type=FileChangeType.CREATE,
            new_content=init_content,
            description=f"創建 {module_name} 模組初始化文件"
        )
        changes.append(change)

        # 創建各個組件文件
        for component in components:
            component_file = module_dir / f"{component}.py"
            component_content = self._generate_component_template(
                module_name,
                component
            )

            change = FileChange(
                file_path=component_file,
                change_type=FileChangeType.CREATE,
                new_content=component_content,
                description=f"創建 {component} 組件"
            )
            changes.append(change)

        self.changes.extend(changes)
        print(f"✓ 創建了 {len(changes)} 個文件")

        return changes

    def _generate_component_template(
        self,
        module_name: str,
        component: str
    ) -> str:
        """
        生成組件模板

        Args:
            module_name: 模組名稱
            component: 組件名稱

        Returns:
            組件文件內容
        """
        return f'''"""
{module_name}.{component}

{component.capitalize()} 組件
"""

from typing import Any, Optional


class {component.capitalize()}:
    """
    {component.capitalize()} 類
    """

    def __init__(self):
        """初始化 {component}"""
        pass

    def process(self, data: Any) -> Any:
        """
        處理數據

        Args:
            data: 輸入數據

        Returns:
            處理後的數據
        """
        raise NotImplementedError("需要實現 process 方法")


# 示例函數
def example_function() -> None:
    """示例函數"""
    print("{component} 組件已載入")


if __name__ == "__main__":
    example_function()
'''

    def batch_update(
        self,
        pattern: str,
        replacement: str,
        file_pattern: str = "*.py"
    ) -> List[FileChange]:
        """
        批量更新文件

        在所有匹配的文件中執行模式替換。

        Args:
            pattern: 要搜尋的模式（正則表達式）
            replacement: 替換字符串
            file_pattern: 文件匹配模式

        Returns:
            變更列表
        """
        print(f"\n批量更新:")
        print(f"  模式: {pattern}")
        print(f"  替換: {replacement}")
        print(f"  文件: {file_pattern}")

        changes = []
        files = list(self.project_root.rglob(file_pattern))

        print(f"\n找到 {len(files)} 個文件")

        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    old_content = f.read()

                # 執行正則替換
                new_content = re.sub(pattern, replacement, old_content)

                if new_content != old_content:
                    change = FileChange(
                        file_path=file_path,
                        change_type=FileChangeType.MODIFY,
                        old_content=old_content,
                        new_content=new_content,
                        description=f"批量更新: {pattern}"
                    )
                    changes.append(change)
                    print(f"  ✓ {file_path.name}")

            except Exception as e:
                print(f"  ✗ {file_path.name}: {e}")

        self.changes.extend(changes)
        print(f"\n完成: {len(changes)} 個文件被修改")

        return changes

    def generate_diff(self, change: FileChange) -> str:
        """
        生成變更的 diff

        Args:
            change: 文件變更

        Returns:
            diff 字符串
        """
        if change.old_content is None or change.new_content is None:
            return f"新文件: {change.file_path}"

        # 簡化的 diff 生成
        old_lines = change.old_content.splitlines()
        new_lines = change.new_content.splitlines()

        diff_lines = [f"--- {change.file_path}"]
        diff_lines.append(f"+++ {change.file_path}")

        # 這裡應該使用 difflib，但為了簡化只顯示統計
        diff_lines.append(f"@@ -{len(old_lines)} +{len(new_lines)} @@")

        return '\n'.join(diff_lines)

    def apply_changes(self, dry_run: bool = False) -> int:
        """
        應用所有變更

        Args:
            dry_run: 如果為 True，只顯示變更不實際應用

        Returns:
            應用的變更數量
        """
        if dry_run:
            print("\n[DRY RUN] 預覽變更:")
        else:
            print("\n應用變更:")

        applied = 0

        for change in self.changes:
            if dry_run:
                print(f"\n  {change}")
                print(self.generate_diff(change))
            else:
                try:
                    if change.change_type == FileChangeType.CREATE:
                        change.file_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(change.file_path, 'w', encoding='utf-8') as f:
                            f.write(change.new_content or "")

                    elif change.change_type == FileChangeType.MODIFY:
                        with open(change.file_path, 'w', encoding='utf-8') as f:
                            f.write(change.new_content or "")

                    elif change.change_type == FileChangeType.DELETE:
                        change.file_path.unlink()

                    print(f"  ✓ {change}")
                    applied += 1

                except Exception as e:
                    print(f"  ✗ {change}: {e}")

        return applied

    def rollback_changes(self) -> int:
        """
        回滾所有變更

        將文件恢復到變更前的狀態。

        Returns:
            回滾的文件數量
        """
        print("\n回滾變更...")

        rolled_back = 0

        for change in reversed(self.changes):
            try:
                if change.old_content is not None:
                    with open(change.file_path, 'w', encoding='utf-8') as f:
                        f.write(change.old_content)
                    print(f"  ✓ 回滾 {change.file_path.name}")
                    rolled_back += 1
                elif change.change_type == FileChangeType.CREATE:
                    change.file_path.unlink()
                    print(f"  ✓ 刪除 {change.file_path.name}")
                    rolled_back += 1

            except Exception as e:
                print(f"  ✗ 回滾失敗 {change.file_path.name}: {e}")

        self.changes.clear()
        return rolled_back


class AiderMultiFileDemo:
    """
    Aider 多文件編輯演示

    展示如何使用 Aider 處理複雜的多文件編輯任務。
    """

    @staticmethod
    def demo_refactoring():
        """
        演示重構操作

        展示如何使用 Aider 進行跨文件重構。
        """
        print("\n" + "=" * 60)
        print("演示 1: 跨文件重構")
        print("=" * 60)

        print("""
場景: 重命名一個在多個文件中使用的類

Aider 命令示例:
--------------

$ aider src/models.py src/views.py src/controllers.py tests/test_models.py

> 請將 UserModel 類重命名為 User，並更新所有引用此類的地方

Aider 會:
1. 分析所有文件中 UserModel 的使用
2. 在每個文件中執行智能重命名
3. 更新 import 語句
4. 更新文檔字符串中的引用
5. 確保測試文件也被更新

變更預覽:
--------

src/models.py:
- class UserModel:
+ class User:

src/views.py:
- from models import UserModel
+ from models import User
- user = UserModel()
+ user = User()

tests/test_models.py:
- def test_user_model():
+ def test_user():
-     user = UserModel()
+     user = User()

提交:
----

> /commit 重構: UserModel -> User

        """)

    @staticmethod
    def demo_coordinated_changes():
        """
        演示協調變更

        展示 Aider 如何協調多個相關文件的修改。
        """
        print("\n" + "=" * 60)
        print("演示 2: 協調多文件變更")
        print("=" * 60)

        print("""
場景: 為 API 添加新的端點，需要同時更新多個層

Aider 命令示例:
--------------

$ aider src/routes.py src/controllers.py src/models.py tests/test_api.py

> 請添加一個新的 API 端點 /api/users/{id}/posts，返回特定用戶的所有文章。
> 需要包括路由、控制器方法、資料庫查詢和測試。

Aider 會協調修改:
1. src/routes.py - 添加新路由
2. src/controllers.py - 實現控制器方法
3. src/models.py - 添加查詢方法（如果需要）
4. tests/test_api.py - 添加測試案例

變更預覽:
--------

src/routes.py:
+ @app.route('/api/users/<int:id>/posts')
+ def get_user_posts(id):
+     return controller.get_user_posts(id)

src/controllers.py:
+ def get_user_posts(user_id):
+     user = User.query.get_or_404(user_id)
+     posts = user.get_posts()
+     return jsonify([post.to_dict() for post in posts])

src/models.py:
+ class User:
+     def get_posts(self):
+         return Post.query.filter_by(user_id=self.id).all()

tests/test_api.py:
+ def test_get_user_posts():
+     response = client.get('/api/users/1/posts')
+     assert response.status_code == 200

        """)

    @staticmethod
    def demo_module_creation():
        """
        演示模組創建

        展示如何使用 Aider 創建整個模組結構。
        """
        print("\n" + "=" * 60)
        print("演示 3: 創建模組結構")
        print("=" * 60)

        print("""
場景: 創建一個新的功能模組，包含完整的 MVC 結構

Aider 命令示例:
--------------

$ aider

> 請創建一個 'authentication' 模組，包含以下結構：
> - models.py: User 和 Session 模型
> - views.py: 登入、登出、註冊視圖
> - controllers.py: 認證邏輯
> - __init__.py: 模組初始化
> - tests/: 對應的測試文件

Aider 會創建:
-------------

authentication/
├── __init__.py
├── models.py
├── views.py
├── controllers.py
└── tests/
    ├── test_models.py
    ├── test_views.py
    └── test_controllers.py

每個文件都包含:
- 適當的導入語句
- 基礎類和函數結構
- 文檔字符串
- 類型註解

        """)


def main():
    """
    主函數

    運行多文件編輯演示。
    """
    print("=" * 60)
    print("Aider 多文件編輯功能演示")
    print("=" * 60)

    # 創建演示項目
    demo_project = Path("./aider_multifile_demo")
    demo_project.mkdir(exist_ok=True)

    # 創建多文件編輯器
    editor = MultiFileEditor(demo_project)

    # 演示 1: 創建模組結構
    print("\n### 演示: 創建模組結構")
    changes = editor.create_module_structure(
        "authentication",
        ["models", "views", "controllers"]
    )

    # 預覽變更
    editor.apply_changes(dry_run=True)

    # 詢問是否應用
    apply = input("\n是否應用這些變更? (y/n): ").lower() == 'y'
    if apply:
        editor.apply_changes()

    # 演示 2: 分析依賴
    print("\n### 演示: 分析文件依賴")
    py_files = list(demo_project.rglob("*.py"))
    if py_files:
        editor.analyze_dependencies(py_files)

    # 演示 3: 重構
    print("\n### 演示: 重構操作")
    if py_files:
        editor.plan_refactoring("example_function", "demo_function", py_files)

    # 運行其他演示
    demo = AiderMultiFileDemo()
    demo.demo_refactoring()
    demo.demo_coordinated_changes()
    demo.demo_module_creation()


if __name__ == "__main__":
    main()

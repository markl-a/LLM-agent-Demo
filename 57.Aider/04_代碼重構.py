"""
Aider 代碼重構模式
==================

本範例展示使用 Aider 進行代碼重構的各種模式和最佳實踐，包括：
- SOLID 原則應用
- 設計模式重構
- 性能優化
- 代碼異味消除
- 架構改進

作者：AI Agent Demo
日期：2025-12-31
"""

from typing import Any, Dict, List, Optional, Protocol, TypeVar, Generic
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import re
import ast


class RefactoringType(Enum):
    """重構類型"""
    EXTRACT_METHOD = "extract_method"              # 提取方法
    EXTRACT_CLASS = "extract_class"                # 提取類
    RENAME = "rename"                              # 重命名
    MOVE_METHOD = "move_method"                    # 移動方法
    INTRODUCE_PARAMETER = "introduce_parameter"    # 引入參數
    REMOVE_PARAMETER = "remove_parameter"          # 移除參數
    INLINE_METHOD = "inline_method"                # 內聯方法
    REPLACE_CONDITIONAL = "replace_conditional"    # 替換條件邏輯
    INTRODUCE_DESIGN_PATTERN = "introduce_pattern" # 引入設計模式


class CodeSmell(Enum):
    """代碼異味類型"""
    LONG_METHOD = "long_method"                    # 過長方法
    LARGE_CLASS = "large_class"                    # 過大類
    DUPLICATE_CODE = "duplicate_code"              # 重複代碼
    DEAD_CODE = "dead_code"                        # 死代碼
    MAGIC_NUMBERS = "magic_numbers"                # 魔術數字
    DEEP_NESTING = "deep_nesting"                  # 深層嵌套
    TIGHT_COUPLING = "tight_coupling"              # 緊耦合
    GOD_OBJECT = "god_object"                      # 上帝對象


@dataclass
class RefactoringTask:
    """
    重構任務

    描述一個具體的重構操作。
    """
    type: RefactoringType
    target: str
    description: str
    files: List[Path]
    priority: int = 1  # 1-5，5 最高

    def __str__(self) -> str:
        return f"{self.type.value}: {self.description}"


class RefactoringAnalyzer:
    """
    重構分析器

    分析代碼並識別需要重構的地方。
    """

    def __init__(self, project_root: Path):
        """
        初始化分析器

        Args:
            project_root: 專案根目錄
        """
        self.project_root = project_root
        self.code_smells: List[Tuple[CodeSmell, str, Path]] = []

    def analyze_file(self, file_path: Path) -> List[CodeSmell]:
        """
        分析單個文件

        檢測代碼異味和重構機會。

        Args:
            file_path: 要分析的文件路徑

        Returns:
            發現的代碼異味列表
        """
        smells = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            # 檢查各種代碼異味
            smells.extend(self._check_long_methods(tree, file_path))
            smells.extend(self._check_large_classes(tree, file_path))
            smells.extend(self._check_magic_numbers(tree, file_path))
            smells.extend(self._check_deep_nesting(tree, file_path))

        except Exception as e:
            print(f"分析 {file_path} 時出錯: {e}")

        return smells

    def _check_long_methods(
        self,
        tree: ast.AST,
        file_path: Path
    ) -> List[Tuple[CodeSmell, str, Path]]:
        """
        檢查過長的方法

        一般認為超過 50 行的方法應該考慮拆分。
        """
        smells = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 計算方法行數
                if hasattr(node, 'end_lineno') and hasattr(node, 'lineno'):
                    lines = node.end_lineno - node.lineno

                    if lines > 50:
                        smells.append((
                            CodeSmell.LONG_METHOD,
                            f"方法 '{node.name}' 有 {lines} 行",
                            file_path
                        ))

        return smells

    def _check_large_classes(
        self,
        tree: ast.AST,
        file_path: Path
    ) -> List[Tuple[CodeSmell, str, Path]]:
        """
        檢查過大的類

        類的方法數超過 20 個可能需要拆分。
        """
        smells = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # 計算方法數
                methods = [
                    n for n in node.body
                    if isinstance(n, ast.FunctionDef)
                ]

                if len(methods) > 20:
                    smells.append((
                        CodeSmell.LARGE_CLASS,
                        f"類 '{node.name}' 有 {len(methods)} 個方法",
                        file_path
                    ))

        return smells

    def _check_magic_numbers(
        self,
        tree: ast.AST,
        file_path: Path
    ) -> List[Tuple[CodeSmell, str, Path]]:
        """
        檢查魔術數字

        未命名的常數應該提取為常量。
        """
        smells = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Num):
                # 忽略常見的數字 0, 1, -1
                if node.n not in [0, 1, -1]:
                    smells.append((
                        CodeSmell.MAGIC_NUMBERS,
                        f"發現魔術數字: {node.n}",
                        file_path
                    ))

        return smells

    def _check_deep_nesting(
        self,
        tree: ast.AST,
        file_path: Path
    ) -> List[Tuple[CodeSmell, str, Path]]:
        """
        檢查深層嵌套

        嵌套層級超過 4 層會降低可讀性。
        """
        smells = []

        def check_nesting(node: ast.AST, depth: int = 0):
            if depth > 4:
                smells.append((
                    CodeSmell.DEEP_NESTING,
                    f"嵌套深度達到 {depth} 層",
                    file_path
                ))

            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.If, ast.For, ast.While, ast.With)):
                    check_nesting(child, depth + 1)
                else:
                    check_nesting(child, depth)

        check_nesting(tree)
        return smells

    def generate_refactoring_plan(
        self,
        files: List[Path]
    ) -> List[RefactoringTask]:
        """
        生成重構計劃

        基於分析結果生成具體的重構任務。

        Args:
            files: 要分析的文件列表

        Returns:
            重構任務列表
        """
        print("\n生成重構計劃...")

        tasks = []
        all_smells = []

        for file_path in files:
            smells = self.analyze_file(file_path)
            all_smells.extend([(smell, desc, file_path) for smell, desc, _ in smells])

        # 根據代碼異味生成任務
        for smell, description, file_path in all_smells:
            if smell == CodeSmell.LONG_METHOD:
                task = RefactoringTask(
                    type=RefactoringType.EXTRACT_METHOD,
                    target=file_path.name,
                    description=f"{description} - 考慮拆分為多個小方法",
                    files=[file_path],
                    priority=3
                )
                tasks.append(task)

            elif smell == CodeSmell.LARGE_CLASS:
                task = RefactoringTask(
                    type=RefactoringType.EXTRACT_CLASS,
                    target=file_path.name,
                    description=f"{description} - 考慮拆分為多個類",
                    files=[file_path],
                    priority=4
                )
                tasks.append(task)

            elif smell == CodeSmell.MAGIC_NUMBERS:
                task = RefactoringTask(
                    type=RefactoringType.INTRODUCE_PARAMETER,
                    target=file_path.name,
                    description=f"{description} - 提取為命名常量",
                    files=[file_path],
                    priority=2
                )
                tasks.append(task)

        # 按優先級排序
        tasks.sort(key=lambda t: t.priority, reverse=True)

        return tasks


class SOLIDRefactoring:
    """
    SOLID 原則重構

    展示如何使用 Aider 應用 SOLID 原則重構代碼。
    """

    @staticmethod
    def demonstrate_single_responsibility():
        """
        單一職責原則 (SRP)

        展示如何將違反 SRP 的類重構為遵守 SRP 的設計。
        """
        print("\n" + "=" * 60)
        print("單一職責原則 (Single Responsibility Principle)")
        print("=" * 60)

        print("""
## 重構前：違反 SRP 的類

```python
class User:
    def __init__(self, username, email):
        self.username = username
        self.email = email

    def save(self):
        # 數據庫操作
        pass

    def send_email(self, message):
        # 郵件發送
        pass

    def generate_report(self):
        # 報表生成
        pass
```

問題：User 類承擔了太多職責
- 用戶數據管理
- 數據持久化
- 郵件發送
- 報表生成

## 使用 Aider 重構

$ aider user.py

> 請重構 User 類以遵循單一職責原則。
> 將數據持久化、郵件發送和報表生成分離到獨立的類。

## 重構後：遵守 SRP

```python
# user.py
class User:
    \"\"\"用戶實體 - 只負責用戶數據\"\"\"
    def __init__(self, username, email):
        self.username = username
        self.email = email

# user_repository.py
class UserRepository:
    \"\"\"用戶倉儲 - 負責數據持久化\"\"\"
    def save(self, user: User):
        # 數據庫操作
        pass

    def find(self, user_id: int) -> User:
        # 查詢操作
        pass

# email_service.py
class EmailService:
    \"\"\"郵件服務 - 負責郵件發送\"\"\"
    def send_to_user(self, user: User, message: str):
        # 郵件發送
        pass

# user_report_generator.py
class UserReportGenerator:
    \"\"\"報表生成器 - 負責生成用戶報表\"\"\"
    def generate(self, user: User) -> str:
        # 報表生成
        pass
```

優點：
- 每個類只有一個變更的理由
- 更容易測試
- 更容易維護和擴展
        """)

    @staticmethod
    def demonstrate_open_closed():
        """
        開放封閉原則 (OCP)

        展示如何使用繼承和多態替代條件邏輯。
        """
        print("\n" + "=" * 60)
        print("開放封閉原則 (Open-Closed Principle)")
        print("=" * 60)

        print("""
## 重構前：違反 OCP

```python
class PaymentProcessor:
    def process(self, payment_type, amount):
        if payment_type == "credit_card":
            # 處理信用卡支付
            pass
        elif payment_type == "paypal":
            # 處理 PayPal 支付
            pass
        elif payment_type == "bitcoin":
            # 處理比特幣支付
            pass
        # 添加新支付方式需要修改此方法
```

問題：添加新支付方式需要修改現有代碼

## 使用 Aider 重構

$ aider payment.py

> 請重構 PaymentProcessor 以遵循開放封閉原則。
> 使用策略模式，使其對擴展開放，對修改封閉。

## 重構後：遵守 OCP

```python
from abc import ABC, abstractmethod

class PaymentMethod(ABC):
    \"\"\"支付方式抽象基類\"\"\"
    @abstractmethod
    def process(self, amount: float) -> bool:
        pass

class CreditCardPayment(PaymentMethod):
    def process(self, amount: float) -> bool:
        # 處理信用卡支付
        return True

class PayPalPayment(PaymentMethod):
    def process(self, amount: float) -> bool:
        # 處理 PayPal 支付
        return True

class BitcoinPayment(PaymentMethod):
    def process(self, amount: float) -> bool:
        # 處理比特幣支付
        return True

class PaymentProcessor:
    def __init__(self, payment_method: PaymentMethod):
        self.payment_method = payment_method

    def process(self, amount: float) -> bool:
        return self.payment_method.process(amount)

# 使用
processor = PaymentProcessor(CreditCardPayment())
processor.process(100.0)

# 添加新支付方式不需要修改現有代碼
class ApplePayPayment(PaymentMethod):
    def process(self, amount: float) -> bool:
        # 處理 Apple Pay 支付
        return True
```

優點：
- 添加新功能不需要修改現有代碼
- 降低引入 bug 的風險
- 更好的可擴展性
        """)

    @staticmethod
    def demonstrate_dependency_inversion():
        """
        依賴反轉原則 (DIP)

        展示如何通過依賴注入實現解耦。
        """
        print("\n" + "=" * 60)
        print("依賴反轉原則 (Dependency Inversion Principle)")
        print("=" * 60)

        print("""
## 重構前：違反 DIP

```python
class MySQLDatabase:
    def connect(self):
        pass

    def query(self, sql):
        pass

class UserService:
    def __init__(self):
        self.db = MySQLDatabase()  # 直接依賴具體實現

    def get_user(self, user_id):
        return self.db.query(f"SELECT * FROM users WHERE id={user_id}")
```

問題：
- UserService 直接依賴 MySQLDatabase
- 難以切換到其他數據庫
- 難以進行單元測試

## 使用 Aider 重構

$ aider user_service.py database.py

> 請重構代碼以遵循依賴反轉原則。
> 引入數據庫抽象層和依賴注入。

## 重構後：遵守 DIP

```python
from abc import ABC, abstractmethod
from typing import Protocol

class Database(Protocol):
    \"\"\"數據庫協議\"\"\"
    def connect(self) -> None: ...
    def query(self, sql: str) -> Any: ...

class MySQLDatabase:
    \"\"\"MySQL 實現\"\"\"
    def connect(self) -> None:
        pass

    def query(self, sql: str) -> Any:
        pass

class PostgreSQLDatabase:
    \"\"\"PostgreSQL 實現\"\"\"
    def connect(self) -> None:
        pass

    def query(self, sql: str) -> Any:
        pass

class UserService:
    def __init__(self, database: Database):
        \"\"\"依賴注入數據庫\"\"\"
        self.db = database

    def get_user(self, user_id: int):
        return self.db.query(f"SELECT * FROM users WHERE id={user_id}")

# 使用
mysql_db = MySQLDatabase()
user_service = UserService(mysql_db)

# 輕鬆切換到 PostgreSQL
postgres_db = PostgreSQLDatabase()
user_service = UserService(postgres_db)

# 測試時使用 Mock
class MockDatabase:
    def connect(self): pass
    def query(self, sql): return {"id": 1, "name": "Test"}

test_service = UserService(MockDatabase())
```

優點：
- 高層模組不依賴低層模組
- 容易替換實現
- 便於測試
        """)


class DesignPatternRefactoring:
    """
    設計模式重構

    展示如何使用 Aider 引入設計模式改善代碼。
    """

    @staticmethod
    def demonstrate_strategy_pattern():
        """
        策略模式

        將算法封裝成獨立的策略類。
        """
        print("\n" + "=" * 60)
        print("引入策略模式")
        print("=" * 60)

        print("""
## 場景：不同的排序算法

重構前：
```python
class DataProcessor:
    def sort_data(self, data, algorithm):
        if algorithm == "bubble":
            # 氣泡排序實現
            pass
        elif algorithm == "quick":
            # 快速排序實現
            pass
        elif algorithm == "merge":
            # 合併排序實現
            pass
```

使用 Aider：
$ aider data_processor.py

> 請使用策略模式重構 sort_data 方法，
> 將不同的排序算法封裝為獨立的策略類。

重構後：
```python
from abc import ABC, abstractmethod
from typing import List

class SortStrategy(ABC):
    @abstractmethod
    def sort(self, data: List) -> List:
        pass

class BubbleSort(SortStrategy):
    def sort(self, data: List) -> List:
        # 氣泡排序實現
        return sorted(data)

class QuickSort(SortStrategy):
    def sort(self, data: List) -> List:
        # 快速排序實現
        return sorted(data)

class MergeSort(SortStrategy):
    def sort(self, data: List) -> List:
        # 合併排序實現
        return sorted(data)

class DataProcessor:
    def __init__(self, strategy: SortStrategy):
        self.strategy = strategy

    def sort_data(self, data: List) -> List:
        return self.strategy.sort(data)

# 使用
processor = DataProcessor(QuickSort())
sorted_data = processor.sort_data([3, 1, 4, 1, 5, 9])
```
        """)

    @staticmethod
    def demonstrate_factory_pattern():
        """
        工廠模式

        使用工廠方法創建對象。
        """
        print("\n" + "=" * 60)
        print("引入工廠模式")
        print("=" * 60)

        print("""
## 場景：創建不同類型的文檔

重構前：
```python
def create_document(doc_type):
    if doc_type == "pdf":
        return PDFDocument()
    elif doc_type == "word":
        return WordDocument()
    elif doc_type == "excel":
        return ExcelDocument()
```

使用 Aider：
$ aider document.py

> 請使用工廠模式重構文檔創建邏輯，
> 使代碼更容易擴展和維護。

重構後：
```python
from abc import ABC, abstractmethod

class Document(ABC):
    @abstractmethod
    def create(self): pass

    @abstractmethod
    def save(self): pass

class PDFDocument(Document):
    def create(self): pass
    def save(self): pass

class WordDocument(Document):
    def create(self): pass
    def save(self): pass

class DocumentFactory:
    _creators = {
        "pdf": PDFDocument,
        "word": WordDocument,
        "excel": ExcelDocument,
    }

    @classmethod
    def create_document(cls, doc_type: str) -> Document:
        creator = cls._creators.get(doc_type)
        if not creator:
            raise ValueError(f"Unknown document type: {doc_type}")
        return creator()

    @classmethod
    def register(cls, doc_type: str, creator):
        cls._creators[doc_type] = creator

# 使用
doc = DocumentFactory.create_document("pdf")

# 註冊新類型
DocumentFactory.register("markdown", MarkdownDocument)
```
        """)


class PerformanceRefactoring:
    """
    性能優化重構

    展示如何使用 Aider 進行性能優化。
    """

    @staticmethod
    def demonstrate_caching():
        """
        引入緩存優化
        """
        print("\n" + "=" * 60)
        print("性能優化：引入緩存")
        print("=" * 60)

        print("""
## 場景：頻繁的數據庫查詢

重構前：
```python
class UserService:
    def get_user(self, user_id):
        # 每次都查詢數據庫
        return database.query(f"SELECT * FROM users WHERE id={user_id}")
```

使用 Aider：
$ aider user_service.py

> 請為 get_user 方法添加緩存，
> 減少數據庫查詢次數以提升性能。

重構後：
```python
from functools import lru_cache
from typing import Dict, Optional

class UserService:
    def __init__(self):
        self._cache: Dict[int, User] = {}

    def get_user(self, user_id: int) -> Optional[User]:
        # 先檢查緩存
        if user_id in self._cache:
            return self._cache[user_id]

        # 緩存未命中，查詢數據庫
        user = database.query(f"SELECT * FROM users WHERE id={user_id}")

        # 更新緩存
        if user:
            self._cache[user_id] = user

        return user

    def invalidate_cache(self, user_id: int):
        \"\"\"使緩存失效\"\"\"
        if user_id in self._cache:
            del self._cache[user_id]

# 或使用裝飾器
class UserService:
    @lru_cache(maxsize=128)
    def get_user(self, user_id: int) -> Optional[User]:
        return database.query(f"SELECT * FROM users WHERE id={user_id}")
```
        """)


def main():
    """
    主函數

    運行代碼重構演示。
    """
    print("=" * 60)
    print("Aider 代碼重構演示")
    print("=" * 60)

    # SOLID 原則演示
    solid = SOLIDRefactoring()
    solid.demonstrate_single_responsibility()
    solid.demonstrate_open_closed()
    solid.demonstrate_dependency_inversion()

    # 設計模式演示
    patterns = DesignPatternRefactoring()
    patterns.demonstrate_strategy_pattern()
    patterns.demonstrate_factory_pattern()

    # 性能優化演示
    performance = PerformanceRefactoring()
    performance.demonstrate_caching()

    print("\n" + "=" * 60)
    print("重構最佳實踐")
    print("=" * 60)

    print("""
1. 始終在重構前確保有完整的測試覆蓋
2. 小步前進，每次只做一個重構
3. 每個重構後運行測試
4. 頻繁提交，便於回滾
5. 使用 Aider 的 /diff 命令審查變更
6. 讓 AI 解釋重構的理由和好處
7. 不要在添加新功能的同時重構
8. 保持重構的範圍可控
    """)


if __name__ == "__main__":
    main()

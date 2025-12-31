"""
Aider 測試生成功能
==================

本範例展示如何使用 Aider 自動生成測試代碼，包括：
- 單元測試生成
- 集成測試
- 測試驅動開發 (TDD)
- 測試覆蓋率提升
- 邊界條件測試

作者：AI Agent Demo
日期：2025-12-31
"""

import unittest
from typing import List, Any, Callable, Optional
from dataclasses import dataclass
from pathlib import Path
from enum import Enum
import inspect
import ast


class TestType(Enum):
    """測試類型"""
    UNIT = "unit"              # 單元測試
    INTEGRATION = "integration"  # 集成測試
    E2E = "e2e"               # 端到端測試
    PERFORMANCE = "performance"  # 性能測試


@dataclass
class TestCase:
    """
    測試用例

    表示一個測試案例的結構。
    """
    name: str
    description: str
    test_type: TestType
    inputs: List[Any]
    expected_output: Any
    should_raise: Optional[Exception] = None

    def __str__(self) -> str:
        return f"{self.name}: {self.description}"


class AiderTestGenerator:
    """
    Aider 測試生成器

    展示如何使用 Aider 生成各種類型的測試。
    """

    @staticmethod
    def demonstrate_basic_unit_test():
        """
        基本單元測試生成

        展示如何為簡單函數生成單元測試。
        """
        print("\n" + "=" * 60)
        print("演示 1: 基本單元測試生成")
        print("=" * 60)

        print("""
## 場景：為計算器函數生成測試

### 原始代碼 (calculator.py)

```python
def add(a: int, b: int) -> int:
    \"\"\"
    加法函數

    Args:
        a: 第一個數字
        b: 第二個數字

    Returns:
        兩數之和
    \"\"\"
    return a + b


def divide(a: float, b: float) -> float:
    \"\"\"
    除法函數

    Args:
        a: 被除數
        b: 除數

    Returns:
        商

    Raises:
        ValueError: 當除數為 0 時
    \"\"\"
    if b == 0:
        raise ValueError("除數不能為 0")
    return a / b
```

### 使用 Aider 生成測試

```bash
$ aider calculator.py tests/test_calculator.py

> 請為 calculator.py 中的所有函數生成全面的單元測試，
> 包括正常情況、邊界條件和錯誤處理。
```

### Aider 生成的測試 (test_calculator.py)

```python
import unittest
from calculator import add, divide


class TestCalculator(unittest.TestCase):
    \"\"\"計算器函數測試\"\"\"

    def test_add_positive_numbers(self):
        \"\"\"測試：加法 - 正數\"\"\"
        self.assertEqual(add(2, 3), 5)
        self.assertEqual(add(100, 200), 300)

    def test_add_negative_numbers(self):
        \"\"\"測試：加法 - 負數\"\"\"
        self.assertEqual(add(-5, -3), -8)
        self.assertEqual(add(-10, 5), -5)

    def test_add_zero(self):
        \"\"\"測試：加法 - 包含零\"\"\"
        self.assertEqual(add(0, 0), 0)
        self.assertEqual(add(5, 0), 5)
        self.assertEqual(add(0, 5), 5)

    def test_add_large_numbers(self):
        \"\"\"測試：加法 - 大數字\"\"\"
        self.assertEqual(add(1000000, 2000000), 3000000)

    def test_divide_positive_numbers(self):
        \"\"\"測試：除法 - 正數\"\"\"
        self.assertEqual(divide(10, 2), 5.0)
        self.assertEqual(divide(9, 3), 3.0)

    def test_divide_negative_numbers(self):
        \"\"\"測試：除法 - 負數\"\"\"
        self.assertEqual(divide(-10, 2), -5.0)
        self.assertEqual(divide(10, -2), -5.0)
        self.assertEqual(divide(-10, -2), 5.0)

    def test_divide_with_decimal(self):
        \"\"\"測試：除法 - 小數結果\"\"\"
        self.assertAlmostEqual(divide(10, 3), 3.333, places=3)

    def test_divide_by_zero(self):
        \"\"\"測試：除法 - 除以零應拋出異常\"\"\"
        with self.assertRaises(ValueError) as context:
            divide(10, 0)
        self.assertEqual(str(context.exception), "除數不能為 0")


if __name__ == '__main__':
    unittest.main()
```

### 測試覆蓋

Aider 自動生成了：
✓ 正常情況測試
✓ 邊界條件測試（零、負數、大數字）
✓ 異常處理測試
✓ 小數精度測試
        """)

    @staticmethod
    def demonstrate_class_testing():
        """
        類的測試生成

        展示如何為類生成測試，包括狀態測試和方法測試。
        """
        print("\n" + "=" * 60)
        print("演示 2: 類的測試生成")
        print("=" * 60)

        print("""
## 場景：為購物車類生成測試

### 原始代碼 (shopping_cart.py)

```python
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class Product:
    id: int
    name: str
    price: float


class ShoppingCart:
    \"\"\"購物車類\"\"\"

    def __init__(self):
        self.items: Dict[int, tuple[Product, int]] = {}

    def add_item(self, product: Product, quantity: int = 1):
        \"\"\"添加商品到購物車\"\"\"
        if quantity <= 0:
            raise ValueError("數量必須大於 0")

        if product.id in self.items:
            current_product, current_qty = self.items[product.id]
            self.items[product.id] = (current_product, current_qty + quantity)
        else:
            self.items[product.id] = (product, quantity)

    def remove_item(self, product_id: int):
        \"\"\"從購物車移除商品\"\"\"
        if product_id in self.items:
            del self.items[product_id]

    def get_total(self) -> float:
        \"\"\"計算總金額\"\"\"
        total = 0
        for product, quantity in self.items.values():
            total += product.price * quantity
        return total

    def is_empty(self) -> bool:
        \"\"\"檢查購物車是否為空\"\"\"
        return len(self.items) == 0
```

### 使用 Aider 生成測試

```bash
$ aider shopping_cart.py tests/test_shopping_cart.py

> 請為 ShoppingCart 類生成完整的測試套件，
> 包括所有方法的測試和狀態變化的測試。
```

### Aider 生成的測試 (test_shopping_cart.py)

```python
import unittest
from shopping_cart import ShoppingCart, Product


class TestShoppingCart(unittest.TestCase):
    \"\"\"購物車測試\"\"\"

    def setUp(self):
        \"\"\"每個測試前的設置\"\"\"
        self.cart = ShoppingCart()
        self.product1 = Product(1, "筆記本電腦", 30000)
        self.product2 = Product(2, "滑鼠", 500)
        self.product3 = Product(3, "鍵盤", 1500)

    def test_cart_initially_empty(self):
        \"\"\"測試：新購物車應該是空的\"\"\"
        self.assertTrue(self.cart.is_empty())
        self.assertEqual(self.cart.get_total(), 0)

    def test_add_single_item(self):
        \"\"\"測試：添加單個商品\"\"\"
        self.cart.add_item(self.product1)

        self.assertFalse(self.cart.is_empty())
        self.assertEqual(len(self.cart.items), 1)
        self.assertEqual(self.cart.get_total(), 30000)

    def test_add_multiple_items(self):
        \"\"\"測試：添加多個不同商品\"\"\"
        self.cart.add_item(self.product1)
        self.cart.add_item(self.product2)
        self.cart.add_item(self.product3)

        self.assertEqual(len(self.cart.items), 3)
        self.assertEqual(self.cart.get_total(), 32000)

    def test_add_same_item_multiple_times(self):
        \"\"\"測試：多次添加同一商品\"\"\"
        self.cart.add_item(self.product1, 2)
        self.cart.add_item(self.product1, 1)

        self.assertEqual(len(self.cart.items), 1)
        product, quantity = self.cart.items[self.product1.id]
        self.assertEqual(quantity, 3)
        self.assertEqual(self.cart.get_total(), 90000)

    def test_add_item_with_zero_quantity(self):
        \"\"\"測試：添加數量為 0 的商品應拋出異常\"\"\"
        with self.assertRaises(ValueError):
            self.cart.add_item(self.product1, 0)

    def test_add_item_with_negative_quantity(self):
        \"\"\"測試：添加負數數量應拋出異常\"\"\"
        with self.assertRaises(ValueError):
            self.cart.add_item(self.product1, -1)

    def test_remove_existing_item(self):
        \"\"\"測試：移除存在的商品\"\"\"
        self.cart.add_item(self.product1)
        self.cart.add_item(self.product2)

        self.cart.remove_item(self.product1.id)

        self.assertEqual(len(self.cart.items), 1)
        self.assertNotIn(self.product1.id, self.cart.items)
        self.assertEqual(self.cart.get_total(), 500)

    def test_remove_nonexistent_item(self):
        \"\"\"測試：移除不存在的商品不應報錯\"\"\"
        self.cart.add_item(self.product1)

        # 應該不會拋出異常
        self.cart.remove_item(999)

        self.assertEqual(len(self.cart.items), 1)

    def test_total_with_multiple_quantities(self):
        \"\"\"測試：計算多個商品和數量的總額\"\"\"
        self.cart.add_item(self.product1, 2)  # 60000
        self.cart.add_item(self.product2, 3)  # 1500
        self.cart.add_item(self.product3, 1)  # 1500

        self.assertEqual(self.cart.get_total(), 63000)

    def test_clear_cart_by_removing_all_items(self):
        \"\"\"測試：移除所有商品後購物車應為空\"\"\"
        self.cart.add_item(self.product1)
        self.cart.add_item(self.product2)

        self.cart.remove_item(self.product1.id)
        self.cart.remove_item(self.product2.id)

        self.assertTrue(self.cart.is_empty())
        self.assertEqual(self.cart.get_total(), 0)


if __name__ == '__main__':
    unittest.main()
```

### 測試特點

Aider 生成的測試包括：
✓ setUp 方法準備測試數據
✓ 初始狀態測試
✓ 單一操作測試
✓ 組合操作測試
✓ 邊界條件測試
✓ 異常情況測試
✓ 狀態轉換測試
        """)

    @staticmethod
    def demonstrate_tdd_workflow():
        """
        測試驅動開發 (TDD) 工作流程

        展示如何使用 Aider 進行 TDD。
        """
        print("\n" + "=" * 60)
        print("演示 3: 測試驅動開發 (TDD)")
        print("=" * 60)

        print("""
## TDD 工作流程

測試驅動開發遵循 Red-Green-Refactor 循環：
1. Red: 寫失敗的測試
2. Green: 寫最少的代碼讓測試通過
3. Refactor: 重構代碼

### 步驟 1: 編寫測試 (Red)

```bash
$ aider tests/test_user_validator.py

> 我想實現一個用戶驗證器。
> 請先為它編寫測試，要求：
> 1. 驗證用戶名（3-20 字符，只能包含字母數字和下劃線）
> 2. 驗證郵箱格式
> 3. 驗證密碼強度（至少 8 字符，包含大小寫字母和數字）
```

#### Aider 生成的測試

```python
import unittest
from user_validator import UserValidator


class TestUserValidator(unittest.TestCase):
    def setUp(self):
        self.validator = UserValidator()

    # 用戶名測試
    def test_valid_username(self):
        self.assertTrue(self.validator.validate_username("john_doe"))
        self.assertTrue(self.validator.validate_username("user123"))

    def test_username_too_short(self):
        self.assertFalse(self.validator.validate_username("ab"))

    def test_username_too_long(self):
        self.assertFalse(
            self.validator.validate_username("a" * 21)
        )

    def test_username_invalid_characters(self):
        self.assertFalse(self.validator.validate_username("john-doe"))
        self.assertFalse(self.validator.validate_username("john.doe"))
        self.assertFalse(self.validator.validate_username("john doe"))

    # 郵箱測試
    def test_valid_email(self):
        self.assertTrue(
            self.validator.validate_email("user@example.com")
        )
        self.assertTrue(
            self.validator.validate_email("test.user@domain.co.uk")
        )

    def test_invalid_email_format(self):
        self.assertFalse(self.validator.validate_email("invalid"))
        self.assertFalse(self.validator.validate_email("@example.com"))
        self.assertFalse(self.validator.validate_email("user@"))

    # 密碼測試
    def test_valid_password(self):
        self.assertTrue(
            self.validator.validate_password("Password123")
        )

    def test_password_too_short(self):
        self.assertFalse(self.validator.validate_password("Pass1"))

    def test_password_no_uppercase(self):
        self.assertFalse(
            self.validator.validate_password("password123")
        )

    def test_password_no_lowercase(self):
        self.assertFalse(
            self.validator.validate_password("PASSWORD123")
        )

    def test_password_no_digit(self):
        self.assertFalse(
            self.validator.validate_password("Password")
        )
```

### 步驟 2: 實現代碼 (Green)

```bash
$ aider user_validator.py tests/test_user_validator.py

> 現在請實現 UserValidator 類，
> 讓所有測試通過。
```

#### Aider 生成的實現

```python
import re


class UserValidator:
    \"\"\"用戶輸入驗證器\"\"\"

    @staticmethod
    def validate_username(username: str) -> bool:
        \"\"\"
        驗證用戶名

        規則：
        - 3-20 字符
        - 只能包含字母、數字和下劃線
        \"\"\"
        if not username or len(username) < 3 or len(username) > 20:
            return False

        pattern = r'^[a-zA-Z0-9_]+$'
        return bool(re.match(pattern, username))

    @staticmethod
    def validate_email(email: str) -> bool:
        \"\"\"
        驗證郵箱格式
        \"\"\"
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_password(password: str) -> bool:
        \"\"\"
        驗證密碼強度

        規則：
        - 至少 8 字符
        - 包含大寫字母
        - 包含小寫字母
        - 包含數字
        \"\"\"
        if not password or len(password) < 8:
            return False

        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)

        return has_upper and has_lower and has_digit
```

### 步驟 3: 重構 (Refactor)

```bash
> 測試都通過了！請重構代碼以提高可讀性和可維護性。
```

#### Aider 重構後的代碼

```python
import re
from typing import Pattern


class ValidationRule:
    \"\"\"驗證規則基類\"\"\"

    def __init__(self, pattern: str, min_length: int = 0, max_length: int = float('inf')):
        self.pattern: Pattern = re.compile(pattern)
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, value: str) -> bool:
        if not value:
            return False

        if not (self.min_length <= len(value) <= self.max_length):
            return False

        return bool(self.pattern.match(value))


class UserValidator:
    \"\"\"用戶輸入驗證器\"\"\"

    # 定義驗證規則
    USERNAME_RULE = ValidationRule(
        pattern=r'^[a-zA-Z0-9_]+$',
        min_length=3,
        max_length=20
    )

    EMAIL_RULE = ValidationRule(
        pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )

    @classmethod
    def validate_username(cls, username: str) -> bool:
        return cls.USERNAME_RULE.validate(username)

    @classmethod
    def validate_email(cls, email: str) -> bool:
        return cls.EMAIL_RULE.validate(email)

    @staticmethod
    def validate_password(password: str) -> bool:
        if not password or len(password) < 8:
            return False

        checks = [
            any(c.isupper() for c in password),  # 大寫
            any(c.islower() for c in password),  # 小寫
            any(c.isdigit() for c in password),  # 數字
        ]

        return all(checks)
```

### TDD 的優勢

✓ 確保代碼符合需求
✓ 高測試覆蓋率
✓ 更好的代碼設計
✓ 重構更安全
✓ 文檔化需求
        """)

    @staticmethod
    def demonstrate_integration_testing():
        """
        集成測試生成

        展示如何生成測試多個組件交互的集成測試。
        """
        print("\n" + "=" * 60)
        print("演示 4: 集成測試")
        print("=" * 60)

        print("""
## 場景：測試 API 端點

### 使用 Aider 生成集成測試

```bash
$ aider api/routes.py tests/test_integration.py

> 請為 API 路由生成集成測試，
> 測試從 HTTP 請求到數據庫的完整流程。
```

### Aider 生成的集成測試

```python
import unittest
import json
from app import create_app
from database import db
from models import User


class TestAPIIntegration(unittest.TestCase):
    \"\"\"API 集成測試\"\"\"

    @classmethod
    def setUpClass(cls):
        \"\"\"設置測試應用\"\"\"
        cls.app = create_app('testing')
        cls.client = cls.app.test_client()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.create_all()

    @classmethod
    def tearDownClass(cls):
        \"\"\"清理\"\"\"
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    def setUp(self):
        \"\"\"每個測試前清空數據庫\"\"\"
        db.session.query(User).delete()
        db.session.commit()

    def test_create_user(self):
        \"\"\"測試：創建用戶\"\"\"
        response = self.client.post(
            '/api/users',
            data=json.dumps({
                'username': 'testuser',
                'email': 'test@example.com'
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('id', data)
        self.assertEqual(data['username'], 'testuser')

        # 驗證數據庫中確實創建了用戶
        user = User.query.filter_by(username='testuser').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'test@example.com')

    def test_get_user(self):
        \"\"\"測試：獲取用戶\"\"\"
        # 先創建用戶
        user = User(username='testuser', email='test@example.com')
        db.session.add(user)
        db.session.commit()

        # 獲取用戶
        response = self.client.get(f'/api/users/{user.id}')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['username'], 'testuser')

    def test_update_user(self):
        \"\"\"測試：更新用戶\"\"\"
        user = User(username='testuser', email='test@example.com')
        db.session.add(user)
        db.session.commit()

        response = self.client.put(
            f'/api/users/{user.id}',
            data=json.dumps({'email': 'new@example.com'}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)

        # 驗證數據庫已更新
        user = User.query.get(user.id)
        self.assertEqual(user.email, 'new@example.com')

    def test_delete_user(self):
        \"\"\"測試：刪除用戶\"\"\"
        user = User(username='testuser', email='test@example.com')
        db.session.add(user)
        db.session.commit()
        user_id = user.id

        response = self.client.delete(f'/api/users/{user_id}')

        self.assertEqual(response.status_code, 204)

        # 驗證數據庫中已刪除
        user = User.query.get(user_id)
        self.assertIsNone(user)

    def test_list_users(self):
        \"\"\"測試：列出所有用戶\"\"\"
        # 創建多個用戶
        for i in range(3):
            user = User(
                username=f'user{i}',
                email=f'user{i}@example.com'
            )
            db.session.add(user)
        db.session.commit()

        response = self.client.get('/api/users')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 3)
```
        """)


def main():
    """
    主函數

    運行測試生成演示。
    """
    print("=" * 60)
    print("Aider 測試生成演示")
    print("=" * 60)

    generator = AiderTestGenerator()

    # 演示各種測試生成
    generator.demonstrate_basic_unit_test()
    generator.demonstrate_class_testing()
    generator.demonstrate_tdd_workflow()
    generator.demonstrate_integration_testing()

    print("\n" + "=" * 60)
    print("測試生成最佳實踐")
    print("=" * 60)

    print("""
1. 使用描述性的測試名稱
   ✓ test_add_item_to_cart_increases_total
   ✗ test1

2. 每個測試只測一個行為
   - 保持測試簡單和專注
   - 避免在一個測試中測試多個功能

3. 遵循 AAA 模式
   - Arrange: 準備測試數據
   - Act: 執行被測試的操作
   - Assert: 驗證結果

4. 測試邊界條件
   - 空值、零、負數
   - 最小值、最大值
   - 第一個、最後一個

5. 使用 Aider 的提示
   > 請為這個函數生成測試，包括邊界條件和錯誤情況

6. 測試異常處理
   - 使用 assertRaises
   - 驗證異常訊息

7. 保持測試獨立
   - 每個測試都應該能獨立運行
   - 不依賴其他測試的執行順序

8. 使用 setUp 和 tearDown
   - 避免重複的測試準備代碼
   - 確保測試後清理

9. 追求高覆蓋率
   > 請檢查測試覆蓋率並為未覆蓋的代碼添加測試

10. 持續更新測試
    - 代碼變更時更新測試
    - 發現 bug 時添加測試
    """)


if __name__ == "__main__":
    main()

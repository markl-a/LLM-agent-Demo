"""
Cline 測試生成示例

展示如何使用 Cline 自動生成測試：
1. 生成單元測試
2. 生成集成測試
3. 生成端到端測試
4. 生成測試數據
5. 生成 Mock 對象
6. 測試覆蓋率分析

自動化測試生成可以提高代碼質量和測試覆蓋率。
"""

import os
from typing import Dict, List, Any, Optional
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


class ClineTestGenerator:
    """Cline 測試生成器"""

    def __init__(self, api_key: Optional[str] = None):
        """初始化測試生成器"""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("需要提供 ANTHROPIC_API_KEY")

        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-3-5-sonnet-20241022"

    def _call_claude(self, prompt: str, system: str = None) -> str:
        """調用 Claude API"""
        messages = [{"role": "user", "content": prompt}]

        kwargs = {
            "model": self.model,
            "max_tokens": 4096,
            "messages": messages
        }

        if system:
            kwargs["system"] = system

        response = self.client.messages.create(**kwargs)
        return response.content[0].text

    def generate_unit_tests(
        self,
        code: str,
        framework: str = "pytest",
        coverage_target: int = 90
    ) -> str:
        """
        生成單元測試

        Args:
            code: 要測試的代碼
            framework: 測試框架
            coverage_target: 目標覆蓋率

        Returns:
            生成的測試代碼
        """
        prompt = f"""
        請為以下代碼生成 {framework} 單元測試：

        ```
        {code}
        ```

        要求:
        1. 目標覆蓋率: {coverage_target}%
        2. 測試所有公共方法
        3. 包含正常情況測試
        4. 包含邊界情況測試
        5. 包含異常情況測試
        6. 使用清晰的測試名稱
        7. 添加測試文檔

        請返回完整的測試代碼。
        """

        system = "你是一個專業的測試工程師，擅長編寫全面的測試用例。"

        return self._call_claude(prompt, system)

    def generate_integration_tests(
        self,
        components: List[str],
        framework: str = "pytest"
    ) -> str:
        """
        生成集成測試

        Args:
            components: 要集成測試的組件列表
            framework: 測試框架

        Returns:
            生成的集成測試代碼
        """
        components_str = "\n".join(f"- {c}" for c in components)

        prompt = f"""
        請為以下組件生成 {framework} 集成測試：

        組件:
        {components_str}

        要求:
        1. 測試組件之間的交互
        2. 測試數據流
        3. 測試錯誤傳播
        4. 使用適當的測試數據
        5. 包含設置和清理代碼
        6. 測試並發情況（如果適用）

        請返回完整的集成測試代碼。
        """

        return self._call_claude(prompt)

    def generate_e2e_tests(
        self,
        user_story: str,
        technology: str = "playwright"
    ) -> str:
        """
        生成端到端測試

        Args:
            user_story: 用戶故事
            technology: 測試工具

        Returns:
            生成的 E2E 測試代碼
        """
        prompt = f"""
        請為以下用戶故事生成 {technology} 端到端測試：

        用戶故事:
        {user_story}

        要求:
        1. 模擬真實用戶行為
        2. 測試完整的用戶流程
        3. 添加適當的等待和斷言
        4. 處理異步操作
        5. 截圖和錯誤報告
        6. 清晰的測試步驟

        請返回完整的 E2E 測試代碼。
        """

        return self._call_claude(prompt)

    def generate_test_data(
        self,
        schema: Dict[str, Any],
        count: int = 10
    ) -> str:
        """
        生成測試數據

        Args:
            schema: 數據模式
            count: 生成數量

        Returns:
            生成的測試數據代碼
        """
        import json
        schema_str = json.dumps(schema, indent=2, ensure_ascii=False)

        prompt = f"""
        請基於以下數據模式生成 {count} 條測試數據：

        數據模式:
        {schema_str}

        要求:
        1. 生成真實的測試數據
        2. 包含各種情況（正常、邊界、異常）
        3. 數據應該多樣化
        4. 遵循數據約束
        5. 返回 Python 代碼（列表或生成器）

        請返回生成測試數據的代碼。
        """

        return self._call_claude(prompt)

    def generate_mocks(
        self,
        interface: str,
        framework: str = "unittest.mock"
    ) -> str:
        """
        生成 Mock 對象

        Args:
            interface: 要 Mock 的接口
            framework: Mock 框架

        Returns:
            生成的 Mock 代碼
        """
        prompt = f"""
        請為以下接口生成 {framework} Mock 對象：

        ```
        {interface}
        ```

        要求:
        1. Mock 所有方法
        2. 提供合理的返回值
        3. 支持不同的測試場景
        4. 添加使用示例
        5. 包含配置說明

        請返回完整的 Mock 代碼。
        """

        return self._call_claude(prompt)

    def generate_fixtures(
        self,
        test_type: str,
        framework: str = "pytest"
    ) -> str:
        """
        生成測試 Fixtures

        Args:
            test_type: 測試類型描述
            framework: 測試框架

        Returns:
            生成的 Fixture 代碼
        """
        prompt = f"""
        請為 {test_type} 生成 {framework} fixtures：

        要求:
        1. 包含常用的 fixtures
        2. 設置和清理邏輯
        3. 參數化 fixtures（如果適用）
        4. 作用域設置
        5. 依賴管理
        6. 添加文檔

        請返回完整的 fixtures 代碼。
        """

        return self._call_claude(prompt)

    def generate_test_suite(
        self,
        project_description: str,
        test_types: List[str]
    ) -> str:
        """
        生成完整測試套件

        Args:
            project_description: 項目描述
            test_types: 測試類型列表

        Returns:
            測試套件結構和代碼
        """
        test_types_str = "\n".join(f"- {t}" for t in test_types)

        prompt = f"""
        請為以下項目生成完整的測試套件：

        項目描述:
        {project_description}

        需要的測試類型:
        {test_types_str}

        要求:
        1. 組織測試目錄結構
        2. 生成測試配置文件
        3. 創建基礎測試類
        4. 設置 CI/CD 配置
        5. 添加測試文檔

        請返回測試套件的結構和關鍵代碼。
        """

        return self._call_claude(prompt)


def example_generate_unit_tests():
    """示例 1: 生成單元測試"""
    print("=" * 60)
    print("示例 1: 生成單元測試")
    print("=" * 60)

    generator = ClineTestGenerator()

    # 要測試的代碼
    source_code = """
class ShoppingCart:
    def __init__(self):
        self.items = []

    def add_item(self, product_id: str, quantity: int, price: float):
        '''添加商品到購物車'''
        if quantity <= 0:
            raise ValueError("數量必須大於 0")
        if price < 0:
            raise ValueError("價格不能為負數")

        self.items.append({
            'product_id': product_id,
            'quantity': quantity,
            'price': price
        })

    def remove_item(self, product_id: str):
        '''從購物車移除商品'''
        self.items = [item for item in self.items if item['product_id'] != product_id]

    def get_total(self) -> float:
        '''計算總價'''
        return sum(item['quantity'] * item['price'] for item in self.items)

    def apply_discount(self, discount_percent: float) -> float:
        '''應用折扣'''
        if discount_percent < 0 or discount_percent > 100:
            raise ValueError("折扣百分比必須在 0-100 之間")
        return self.get_total() * (1 - discount_percent / 100)
    """

    print("\n要測試的代碼:")
    print(source_code)

    test_code = generator.generate_unit_tests(
        code=source_code,
        framework="pytest",
        coverage_target=95
    )

    print("\n生成的測試代碼:")
    print(test_code)


def example_generate_integration_tests():
    """示例 2: 生成集成測試"""
    print("\n" + "=" * 60)
    print("示例 2: 生成集成測試")
    print("=" * 60)

    generator = ClineTestGenerator()

    components = [
        "UserService - 用戶管理服務",
        "AuthService - 認證服務",
        "EmailService - 郵件發送服務",
        "Database - 數據庫層"
    ]

    print("\n要測試的組件:")
    for comp in components:
        print(f"  - {comp}")

    test_code = generator.generate_integration_tests(
        components=components,
        framework="pytest"
    )

    print("\n生成的集成測試:")
    print(test_code)


def example_generate_e2e_tests():
    """示例 3: 生成端到端測試"""
    print("\n" + "=" * 60)
    print("示例 3: 生成端到端測試")
    print("=" * 60)

    generator = ClineTestGenerator()

    user_story = """
    作為一個用戶，我想要：
    1. 註冊新賬戶
    2. 登錄系統
    3. 瀏覽產品列表
    4. 將產品添加到購物車
    5. 查看購物車
    6. 完成結賬
    7. 退出登錄
    """

    print("\n用戶故事:")
    print(user_story)

    test_code = generator.generate_e2e_tests(
        user_story=user_story,
        technology="playwright"
    )

    print("\n生成的 E2E 測試:")
    print(test_code)


def example_generate_test_data():
    """示例 4: 生成測試數據"""
    print("\n" + "=" * 60)
    print("示例 4: 生成測試數據")
    print("=" * 60)

    generator = ClineTestGenerator()

    # 數據模式
    schema = {
        "user": {
            "id": "UUID",
            "username": "string (3-50 字符，唯一)",
            "email": "string (有效的郵箱格式)",
            "age": "integer (18-100)",
            "is_active": "boolean",
            "created_at": "datetime",
            "tags": "list of strings"
        }
    }

    print("\n數據模式:")
    import json
    print(json.dumps(schema, indent=2, ensure_ascii=False))

    data_code = generator.generate_test_data(schema=schema, count=20)

    print("\n生成的測試數據代碼:")
    print(data_code)


def example_generate_mocks():
    """示例 5: 生成 Mock 對象"""
    print("\n" + "=" * 60)
    print("示例 5: 生成 Mock 對象")
    print("=" * 60)

    generator = ClineTestGenerator()

    # 要 Mock 的接口
    interface = """
class PaymentGateway:
    def process_payment(self, amount: float, card_number: str) -> dict:
        '''處理支付'''
        pass

    def refund(self, transaction_id: str, amount: float) -> dict:
        '''退款'''
        pass

    def get_transaction_status(self, transaction_id: str) -> str:
        '''獲取交易狀態'''
        pass
    """

    print("\n要 Mock 的接口:")
    print(interface)

    mock_code = generator.generate_mocks(
        interface=interface,
        framework="unittest.mock"
    )

    print("\n生成的 Mock 代碼:")
    print(mock_code)


def example_generate_fixtures():
    """示例 6: 生成測試 Fixtures"""
    print("\n" + "=" * 60)
    print("示例 6: 生成測試 Fixtures")
    print("=" * 60)

    generator = ClineTestGenerator()

    test_type = "FastAPI 應用的數據庫測試"

    print(f"\n測試類型: {test_type}")

    fixtures_code = generator.generate_fixtures(
        test_type=test_type,
        framework="pytest"
    )

    print("\n生成的 Fixtures:")
    print(fixtures_code)


def example_generate_test_suite():
    """示例 7: 生成完整測試套件"""
    print("\n" + "=" * 60)
    print("示例 7: 生成完整測試套件")
    print("=" * 60)

    generator = ClineTestGenerator()

    project_desc = """
    電子商務 API 項目
    - FastAPI 框架
    - PostgreSQL 數據庫
    - Redis 緩存
    - 包含用戶、產品、訂單模塊
    """

    test_types = [
        "單元測試",
        "集成測試",
        "API 測試",
        "性能測試",
        "安全測試"
    ]

    print("\n項目描述:")
    print(project_desc)
    print("\n測試類型:")
    for t in test_types:
        print(f"  - {t}")

    suite_code = generator.generate_test_suite(
        project_description=project_desc,
        test_types=test_types
    )

    print("\n生成的測試套件:")
    print(suite_code)


def example_comprehensive_testing():
    """示例 8: 綜合測試生成"""
    print("\n" + "=" * 60)
    print("示例 8: 為完整功能生成測試")
    print("=" * 60)

    generator = ClineTestGenerator()

    # 一個完整的功能實現
    feature_code = """
from typing import Optional
from datetime import datetime

class BlogPost:
    def __init__(self, title: str, content: str, author_id: int):
        self.id: Optional[int] = None
        self.title = title
        self.content = content
        self.author_id = author_id
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.published = False
        self.view_count = 0

    def publish(self):
        if not self.title or not self.content:
            raise ValueError("標題和內容不能為空")
        self.published = True

    def increment_views(self):
        self.view_count += 1

    def update(self, title: Optional[str] = None, content: Optional[str] = None):
        if title:
            self.title = title
        if content:
            self.content = content
        self.updated_at = datetime.now()
    """

    print("\n要測試的功能:")
    print(feature_code)

    # 生成單元測試
    print("\n正在生成單元測試...")
    unit_tests = generator.generate_unit_tests(feature_code, coverage_target=100)
    print("單元測試（前 500 字符）:")
    print(unit_tests[:500] + "...")

    # 生成測試數據
    print("\n正在生成測試數據...")
    test_data_schema = {
        "blog_post": {
            "title": "string (1-200 字符)",
            "content": "string (1-10000 字符)",
            "author_id": "integer (1-1000000)"
        }
    }
    test_data = generator.generate_test_data(test_data_schema, count=10)
    print("測試數據（前 500 字符）:")
    print(test_data[:500] + "...")


def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("Cline 測試生成示例")
    print("=" * 60)

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\n⚠️  警告: 未設置 ANTHROPIC_API_KEY")
        return

    try:
        # 運行示例（注釋以節省 API 調用）
        # example_generate_unit_tests()
        # example_generate_integration_tests()
        # example_generate_e2e_tests()
        # example_generate_test_data()
        # example_generate_mocks()
        # example_generate_fixtures()
        # example_generate_test_suite()
        # example_comprehensive_testing()

        print("\n✅ 測試生成示例已準備就緒")
        print("\n💡 提示:")
        print("1. 使用 generate_unit_tests() 快速生成單元測試")
        print("2. 使用 generate_integration_tests() 測試組件交互")
        print("3. 使用 generate_e2e_tests() 測試用戶流程")
        print("4. 使用 generate_test_data() 創建測試數據")
        print("5. 使用 generate_mocks() 隔離依賴")

        print("\n📊 測試最佳實踐:")
        print("- 目標覆蓋率: 80% 以上")
        print("- 測試金字塔: 70% 單元測試, 20% 集成測試, 10% E2E 測試")
        print("- 保持測試簡單和專注")
        print("- 使用描述性的測試名稱")

    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

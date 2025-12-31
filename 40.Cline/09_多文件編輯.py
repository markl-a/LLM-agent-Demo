"""
Cline 多文件編輯示例

展示如何使用 Cline 跨文件進行編輯：
1. 批量重命名
2. 跨文件重構
3. 統一代碼風格
4. 更新導入語句
5. 遷移 API
6. 全局查找替換

多文件編輯是 Cline 的強大功能之一。
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


class ClineMultiFileEditor:
    """Cline 多文件編輯器"""

    def __init__(self, api_key: Optional[str] = None):
        """初始化多文件編輯器"""
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

    def plan_refactoring(
        self,
        files: Dict[str, str],
        refactoring_goal: str
    ) -> Dict[str, Any]:
        """
        規劃跨文件重構

        Args:
            files: 文件名到內容的映射
            refactoring_goal: 重構目標

        Returns:
            重構計劃
        """
        files_summary = "\n".join(
            f"文件: {name}\n內容長度: {len(content)} 字符"
            for name, content in files.items()
        )

        prompt = f"""
        請規劃以下跨文件重構：

        重構目標: {refactoring_goal}

        涉及的文件:
        {files_summary}

        請提供:
        1. 重構步驟
        2. 每個文件的修改點
        3. 需要注意的依賴關係
        4. 可能的風險
        5. 測試建議

        請以結構化格式返回重構計劃。
        """

        response = self._call_claude(prompt)

        return {
            "goal": refactoring_goal,
            "plan": response,
            "affected_files": list(files.keys())
        }

    def rename_across_files(
        self,
        files: Dict[str, str],
        old_name: str,
        new_name: str,
        rename_type: str = "variable"
    ) -> Dict[str, str]:
        """
        跨文件重命名

        Args:
            files: 文件名到內容的映射
            old_name: 舊名稱
            new_name: 新名稱
            rename_type: 重命名類型（variable, function, class）

        Returns:
            更新後的文件內容
        """
        import json
        files_str = json.dumps(
            {name: content[:500] for name, content in files.items()},
            indent=2,
            ensure_ascii=False
        )

        prompt = f"""
        請在以下文件中將 {rename_type} 從 "{old_name}" 重命名為 "{new_name}"：

        文件（部分內容）:
        {files_str}

        要求:
        1. 更新定義和所有引用
        2. 保持代碼功能不變
        3. 更新註釋和文檔
        4. 考慮作用域和上下文

        請返回每個文件的完整更新內容。
        """

        response = self._call_claude(prompt)

        # 這裡簡化處理，實際應用中需要解析響應
        return {"plan": response}

    def update_imports(
        self,
        files: Dict[str, str],
        old_module: str,
        new_module: str
    ) -> Dict[str, str]:
        """
        更新導入語句

        Args:
            files: 文件名到內容的映射
            old_module: 舊模塊名
            new_module: 新模塊名

        Returns:
            更新後的文件內容
        """
        prompt = f"""
        請更新以下文件中的導入語句：

        從: {old_module}
        到: {new_module}

        文件數量: {len(files)}

        要求:
        1. 更新所有 import 語句
        2. 更新 from ... import 語句
        3. 保持導入的內容不變
        4. 維護代碼格式

        請為每個文件提供更新後的導入部分。
        """

        response = self._call_claude(prompt)

        return {"update_plan": response}

    def migrate_api(
        self,
        files: Dict[str, str],
        old_api: str,
        new_api: str,
        migration_guide: str
    ) -> Dict[str, Any]:
        """
        遷移 API 使用

        Args:
            files: 文件名到內容的映射
            old_api: 舊 API 描述
            new_api: 新 API 描述
            migration_guide: 遷移指南

        Returns:
            遷移計劃和更新
        """
        prompt = f"""
        請規劃將以下文件從舊 API 遷移到新 API：

        舊 API: {old_api}
        新 API: {new_api}

        遷移指南:
        {migration_guide}

        文件數量: {len(files)}

        要求:
        1. 識別所有使用舊 API 的地方
        2. 提供新 API 的替代代碼
        3. 處理棄用的功能
        4. 添加必要的錯誤處理
        5. 更新相關註釋

        請提供詳細的遷移計劃。
        """

        response = self._call_claude(prompt)

        return {
            "old_api": old_api,
            "new_api": new_api,
            "migration_plan": response
        }

    def unify_code_style(
        self,
        files: Dict[str, str],
        style_guide: str
    ) -> Dict[str, str]:
        """
        統一代碼風格

        Args:
            files: 文件名到內容的映射
            style_guide: 代碼風格指南

        Returns:
            格式化後的文件內容
        """
        prompt = f"""
        請統一以下文件的代碼風格：

        風格指南:
        {style_guide}

        文件數量: {len(files)}

        要求:
        1. 統一縮進
        2. 統一命名約定
        3. 統一導入順序
        4. 統一註釋風格
        5. 保持功能不變

        請提供格式化建議。
        """

        response = self._call_claude(prompt)

        return {"formatting_plan": response}

    def extract_common_code(
        self,
        files: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        提取公共代碼

        Args:
            files: 文件名到內容的映射

        Returns:
            提取計劃和新文件內容
        """
        import json
        files_summary = json.dumps(
            {name: content[:1000] for name, content in files.items()},
            indent=2,
            ensure_ascii=False
        )

        prompt = f"""
        請分析以下文件，找出重複的代碼並提取為公共模塊：

        文件（部分內容）:
        {files_summary}

        要求:
        1. 識別重複的代碼模式
        2. 設計公共模塊結構
        3. 提供提取後的代碼
        4. 更新原文件以使用公共代碼
        5. 確保不破壞現有功能

        請提供詳細的提取計劃。
        """

        response = self._call_claude(prompt)

        return {
            "common_code_plan": response,
            "new_module_name": "common_utils.py"
        }

    def synchronize_changes(
        self,
        base_file: str,
        base_content: str,
        related_files: Dict[str, str],
        change_description: str
    ) -> Dict[str, str]:
        """
        同步相關文件的修改

        Args:
            base_file: 基礎文件名
            base_content: 基礎文件內容
            related_files: 相關文件
            change_description: 變更描述

        Returns:
            需要同步的修改
        """
        prompt = f"""
        基礎文件 {base_file} 發生了以下變更：

        變更描述:
        {change_description}

        基礎文件內容（部分）:
        {base_content[:1000]}

        相關文件數量: {len(related_files)}

        請分析哪些相關文件需要同步修改，並提供修改方案。

        要求:
        1. 識別受影響的文件
        2. 提供同步修改建議
        3. 確保一致性
        4. 處理依賴關係
        """

        response = self._call_claude(prompt)

        return {"sync_plan": response}


def example_plan_refactoring():
    """示例 1: 規劃跨文件重構"""
    print("=" * 60)
    print("示例 1: 規劃跨文件重構")
    print("=" * 60)

    editor = ClineMultiFileEditor()

    # 模擬多個文件
    files = {
        "user_service.py": """
class UserService:
    def get_user(self, user_id):
        # 直接訪問數據庫
        return db.query(User).filter(User.id == user_id).first()

    def create_user(self, data):
        user = User(**data)
        db.add(user)
        db.commit()
        return user
        """,
        "product_service.py": """
class ProductService:
    def get_product(self, product_id):
        # 直接訪問數據庫
        return db.query(Product).filter(Product.id == product_id).first()

    def create_product(self, data):
        product = Product(**data)
        db.add(product)
        db.commit()
        return product
        """,
        "order_service.py": """
class OrderService:
    def get_order(self, order_id):
        # 直接訪問數據庫
        return db.query(Order).filter(Order.id == order_id).first()

    def create_order(self, data):
        order = Order(**data)
        db.add(order)
        db.commit()
        return order
        """
    }

    goal = "提取公共的數據庫訪問邏輯到基礎服務類，實現代碼復用"

    print(f"\n重構目標: {goal}")
    print(f"\n涉及文件: {list(files.keys())}")

    plan = editor.plan_refactoring(files, goal)

    print("\n重構計劃:")
    print(plan["plan"])


def example_rename_across_files():
    """示例 2: 跨文件重命名"""
    print("\n" + "=" * 60)
    print("示例 2: 跨文件重命名")
    print("=" * 60)

    editor = ClineMultiFileEditor()

    files = {
        "models.py": """
class UserModel:
    def __init__(self, name):
        self.name = name
        """,
        "services.py": """
from models import UserModel

def create_user(name):
    return UserModel(name)
        """,
        "views.py": """
from services import create_user
from models import UserModel

def user_view():
    user = create_user("John")
    isinstance(user, UserModel)
        """
    }

    print("\n要重命名: UserModel -> User")
    print(f"涉及文件: {list(files.keys())}")

    result = editor.rename_across_files(
        files=files,
        old_name="UserModel",
        new_name="User",
        rename_type="class"
    )

    print("\n重命名計劃:")
    print(result["plan"])


def example_update_imports():
    """示例 3: 更新導入語句"""
    print("\n" + "=" * 60)
    print("示例 3: 批量更新導入語句")
    print("=" * 60)

    editor = ClineMultiFileEditor()

    files = {
        "api/routes.py": """
from utils.auth import authenticate
from utils.validation import validate_input
        """,
        "api/handlers.py": """
from utils.auth import get_current_user
from utils.validation import ValidationError
        """,
        "api/middleware.py": """
from utils.auth import verify_token
        """
    }

    print("\n遷移: utils -> core.utils")
    print(f"涉及文件: {list(files.keys())}")

    result = editor.update_imports(
        files=files,
        old_module="utils",
        new_module="core.utils"
    )

    print("\n更新計劃:")
    print(result["update_plan"])


def example_migrate_api():
    """示例 4: API 遷移"""
    print("\n" + "=" * 60)
    print("示例 4: 遷移到新 API")
    print("=" * 60)

    editor = ClineMultiFileEditor()

    files = {
        "service1.py": "# 使用舊 API 的代碼",
        "service2.py": "# 使用舊 API 的代碼",
        "service3.py": "# 使用舊 API 的代碼"
    }

    old_api = """
    舊 API:
    - client.send(data)
    - client.receive()
    - client.close()
    """

    new_api = """
    新 API:
    - async with client.session() as session:
    -     await session.send(data)
    -     result = await session.receive()
    """

    migration_guide = """
    1. 所有操作都需要改為異步
    2. 使用 context manager 管理會話
    3. 添加適當的錯誤處理
    """

    print(f"\n從舊 API 遷移到新 API")
    print(f"涉及文件: {list(files.keys())}")

    result = editor.migrate_api(
        files=files,
        old_api=old_api,
        new_api=new_api,
        migration_guide=migration_guide
    )

    print("\n遷移計劃:")
    print(result["migration_plan"])


def example_unify_code_style():
    """示例 5: 統一代碼風格"""
    print("\n" + "=" * 60)
    print("示例 5: 統一代碼風格")
    print("=" * 60)

    editor = ClineMultiFileEditor()

    files = {
        "module1.py": """
def myFunction(inputData):
    result=inputData*2
    return result
        """,
        "module2.py": """
def my_other_function( input_data ):
    result = input_data * 2
    return result
        """,
        "module3.py": """
def AnotherFunction(InputData):
    Result=InputData*2
    return Result
        """
    }

    style_guide = """
    - 函數名使用 snake_case
    - 變量名使用 snake_case
    - 運算符兩側有空格
    - 參數列表括號內無空格
    - 使用 4 空格縮進
    """

    print(f"\n統一代碼風格")
    print(f"涉及文件: {list(files.keys())}")
    print(f"\n風格指南:\n{style_guide}")

    result = editor.unify_code_style(files, style_guide)

    print("\n格式化計劃:")
    print(result["formatting_plan"])


def example_extract_common_code():
    """示例 6: 提取公共代碼"""
    print("\n" + "=" * 60)
    print("示例 6: 提取公共代碼")
    print("=" * 60)

    editor = ClineMultiFileEditor()

    files = {
        "handler1.py": """
def handle_request1(data):
    # 驗證數據
    if not data:
        raise ValueError("Data is empty")
    if not isinstance(data, dict):
        raise TypeError("Data must be dict")

    # 處理數據
    result = process(data)
    return result
        """,
        "handler2.py": """
def handle_request2(data):
    # 驗證數據
    if not data:
        raise ValueError("Data is empty")
    if not isinstance(data, dict):
        raise TypeError("Data must be dict")

    # 處理數據（稍有不同）
    result = process_v2(data)
    return result
        """,
        "handler3.py": """
def handle_request3(data):
    # 驗證數據
    if not data:
        raise ValueError("Data is empty")
    if not isinstance(data, dict):
        raise TypeError("Data must be dict")

    # 處理數據（又有不同）
    result = process_v3(data)
    return result
        """
    }

    print(f"\n提取公共代碼")
    print(f"涉及文件: {list(files.keys())}")

    result = editor.extract_common_code(files)

    print("\n提取計劃:")
    print(result["common_code_plan"])
    print(f"\n建議的公共模塊: {result['new_module_name']}")


def example_synchronize_changes():
    """示例 7: 同步相關文件修改"""
    print("\n" + "=" * 60)
    print("示例 7: 同步相關文件修改")
    print("=" * 60)

    editor = ClineMultiFileEditor()

    base_file = "models/user.py"
    base_content = """
class User:
    def __init__(self, username, email, age):
        self.username = username
        self.email = email
        self.age = age  # 新增字段
    """

    related_files = {
        "serializers/user_serializer.py": "# 用戶序列化器",
        "views/user_views.py": "# 用戶視圖",
        "tests/test_user.py": "# 用戶測試",
        "migrations/001_user.py": "# 數據庫遷移"
    }

    change_description = "在 User 模型中添加了 age 字段"

    print(f"\n基礎文件: {base_file}")
    print(f"變更: {change_description}")
    print(f"相關文件: {list(related_files.keys())}")

    result = editor.synchronize_changes(
        base_file=base_file,
        base_content=base_content,
        related_files=related_files,
        change_description=change_description
    )

    print("\n同步計劃:")
    print(result["sync_plan"])


def example_comprehensive_refactoring():
    """示例 8: 綜合重構示例"""
    print("\n" + "=" * 60)
    print("示例 8: 綜合重構項目")
    print("=" * 60)

    editor = ClineMultiFileEditor()

    print("\n場景: 將單體應用重構為模塊化架構")
    print("\n步驟:")
    print("1. ✓ 分析現有代碼結構")
    print("2. ✓ 識別功能模塊")
    print("3. ✓ 提取公共邏輯")
    print("4. ✓ 重組文件結構")
    print("5. ✓ 更新所有導入")
    print("6. ✓ 統一代碼風格")
    print("7. ✓ 更新測試")
    print("8. ✓ 更新文檔")

    print("\n預期結果:")
    print("- 更好的代碼組織")
    print("- 減少代碼重複")
    print("- 提高可維護性")
    print("- 更容易測試")


def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("Cline 多文件編輯示例")
    print("=" * 60)

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\n⚠️  警告: 未設置 ANTHROPIC_API_KEY")
        return

    try:
        # 運行示例（注釋以節省 API 調用）
        # example_plan_refactoring()
        # example_rename_across_files()
        # example_update_imports()
        # example_migrate_api()
        # example_unify_code_style()
        # example_extract_common_code()
        # example_synchronize_changes()
        # example_comprehensive_refactoring()

        print("\n✅ 多文件編輯示例已準備就緒")
        print("\n💡 提示:")
        print("1. 使用 plan_refactoring() 規劃大型重構")
        print("2. 使用 rename_across_files() 安全地重命名")
        print("3. 使用 update_imports() 批量更新導入")
        print("4. 使用 extract_common_code() 消除重複")
        print("5. 使用 synchronize_changes() 保持一致性")

        print("\n⚠️  最佳實踐:")
        print("- 在重構前創建備份")
        print("- 使用版本控制")
        print("- 一次專注於一個重構目標")
        print("- 在每步後運行測試")
        print("- 審查所有自動生成的修改")

    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

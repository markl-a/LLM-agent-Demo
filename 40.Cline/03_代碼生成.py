"""
Cline 代碼生成示例

展示如何使用 Cline 自動生成代碼：
1. 生成完整的類和函數
2. 生成 API 端點
3. 生成數據模型
4. 生成配置文件
5. 從規範生成代碼

這可以大大提高開發效率。
"""

import os
from typing import Dict, List, Any, Optional
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


class ClineCodeGenerator:
    """Cline 代碼生成器"""

    def __init__(self, api_key: Optional[str] = None):
        """初始化代碼生成器"""
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

    def generate_class(
        self,
        class_name: str,
        description: str,
        language: str = "python",
        features: List[str] = None
    ) -> str:
        """
        生成類定義

        Args:
            class_name: 類名
            description: 類的功能描述
            language: 編程語言
            features: 需要的功能列表

        Returns:
            生成的類代碼
        """
        features_str = "\n".join(f"- {f}" for f in (features or []))

        prompt = f"""
        請用 {language} 生成一個名為 {class_name} 的類。

        功能描述: {description}

        需要的功能:
        {features_str if features_str else "- 基本功能即可"}

        要求:
        1. 包含完整的文檔字符串
        2. 添加類型提示（如果語言支持）
        3. 實現錯誤處理
        4. 遵循最佳實踐
        5. 添加使用示例

        請只返回代碼，不要有額外的解釋。
        """

        system = f"你是一個專業的 {language} 開發者，擅長編寫清晰、高質量的代碼。"

        return self._call_claude(prompt, system)

    def generate_api_endpoint(
        self,
        endpoint: str,
        method: str,
        framework: str,
        description: str,
        parameters: Dict[str, str] = None
    ) -> str:
        """
        生成 API 端點

        Args:
            endpoint: 端點路徑
            method: HTTP 方法
            framework: Web 框架
            description: 端點功能描述
            parameters: 參數說明

        Returns:
            生成的端點代碼
        """
        params_str = ""
        if parameters:
            params_str = "\n".join(f"- {k}: {v}" for k, v in parameters.items())

        prompt = f"""
        請使用 {framework} 框架生成一個 API 端點。

        端點: {method} {endpoint}
        功能: {description}

        參數:
        {params_str if params_str else "無參數"}

        要求:
        1. 包含請求驗證
        2. 添加錯誤處理
        3. 返回適當的 HTTP 狀態碼
        4. 添加 API 文檔註釋
        5. 包含使用示例

        請返回完整的端點實現代碼。
        """

        return self._call_claude(prompt)

    def generate_data_model(
        self,
        model_name: str,
        fields: Dict[str, str],
        orm: str = "sqlalchemy",
        validations: Dict[str, List[str]] = None
    ) -> str:
        """
        生成數據模型

        Args:
            model_name: 模型名稱
            fields: 字段定義 {字段名: 類型}
            orm: ORM 框架
            validations: 驗證規則

        Returns:
            生成的模型代碼
        """
        fields_str = "\n".join(f"- {k}: {v}" for k, v in fields.items())

        validations_str = ""
        if validations:
            validations_str = "\n驗證規則:\n"
            for field, rules in validations.items():
                validations_str += f"- {field}: {', '.join(rules)}\n"

        prompt = f"""
        請使用 {orm} 生成一個數據模型。

        模型名: {model_name}

        字段:
        {fields_str}

        {validations_str}

        要求:
        1. 包含適當的索引
        2. 添加關系定義（如果適用）
        3. 實現數據驗證
        4. 添加序列化方法
        5. 包含文檔字符串

        請返回完整的模型定義。
        """

        return self._call_claude(prompt)

    def generate_from_spec(
        self,
        spec: str,
        spec_type: str = "openapi",
        language: str = "python"
    ) -> str:
        """
        從規範生成代碼

        Args:
            spec: API 規範（OpenAPI, GraphQL 等）
            spec_type: 規範類型
            language: 目標語言

        Returns:
            生成的代碼
        """
        prompt = f"""
        請根據以下 {spec_type} 規範生成 {language} 代碼：

        {spec}

        要求:
        1. 生成完整的實現
        2. 包含類型定義
        3. 添加錯誤處理
        4. 實現所有端點/操作
        5. 添加文檔

        請返回完整的代碼實現。
        """

        return self._call_claude(prompt)

    def generate_config_file(
        self,
        config_type: str,
        project_type: str,
        options: Dict[str, Any] = None
    ) -> str:
        """
        生成配置文件

        Args:
            config_type: 配置類型（docker, ci, env 等）
            project_type: 項目類型
            options: 配置選項

        Returns:
            生成的配置文件內容
        """
        options_str = ""
        if options:
            import json
            options_str = json.dumps(options, indent=2, ensure_ascii=False)

        prompt = f"""
        請生成一個 {config_type} 配置文件，用於 {project_type} 項目。

        配置選項:
        {options_str if options_str else "使用默認配置"}

        要求:
        1. 遵循最佳實踐
        2. 添加詳細註釋
        3. 包含必要的優化
        4. 考慮安全性
        5. 易於維護

        請返回完整的配置文件內容。
        """

        return self._call_claude(prompt)

    def generate_test(
        self,
        code: str,
        test_framework: str = "pytest",
        coverage_target: int = 80
    ) -> str:
        """
        生成測試代碼

        Args:
            code: 要測試的代碼
            test_framework: 測試框架
            coverage_target: 覆蓋率目標

        Returns:
            生成的測試代碼
        """
        prompt = f"""
        請為以下代碼生成 {test_framework} 測試：

        ```
        {code}
        ```

        要求:
        1. 覆蓋率達到 {coverage_target}%
        2. 包含單元測試
        3. 包含邊界情況測試
        4. 包含錯誤情況測試
        5. 添加清晰的測試描述

        請返回完整的測試代碼。
        """

        return self._call_claude(prompt)

    def generate_from_template(
        self,
        template_name: str,
        variables: Dict[str, str]
    ) -> str:
        """
        從模板生成代碼

        Args:
            template_name: 模板名稱
            variables: 模板變量

        Returns:
            生成的代碼
        """
        import json
        variables_str = json.dumps(variables, indent=2, ensure_ascii=False)

        prompt = f"""
        請使用 {template_name} 模板生成代碼。

        模板變量:
        {variables_str}

        請生成完整的代碼，包含所有必要的文件和配置。
        """

        return self._call_claude(prompt)


def example_generate_class():
    """示例 1: 生成類定義"""
    print("=" * 60)
    print("示例 1: 生成類定義")
    print("=" * 60)

    generator = ClineCodeGenerator()

    code = generator.generate_class(
        class_name="UserManager",
        description="用戶管理類，處理用戶的創建、更新、刪除和查詢",
        language="python",
        features=[
            "創建新用戶",
            "更新用戶信息",
            "刪除用戶",
            "按 ID 查詢用戶",
            "列出所有用戶（支持分頁）",
            "用戶驗證"
        ]
    )

    print("\n生成的代碼:")
    print(code)


def example_generate_api():
    """示例 2: 生成 API 端點"""
    print("\n" + "=" * 60)
    print("示例 2: 生成 API 端點")
    print("=" * 60)

    generator = ClineCodeGenerator()

    code = generator.generate_api_endpoint(
        endpoint="/api/v1/users/{user_id}",
        method="GET",
        framework="FastAPI",
        description="獲取用戶詳情",
        parameters={
            "user_id": "用戶 ID（路徑參數）",
            "include_posts": "是否包含用戶的帖子（查詢參數，可選）"
        }
    )

    print("\n生成的 API 端點:")
    print(code)


def example_generate_model():
    """示例 3: 生成數據模型"""
    print("\n" + "=" * 60)
    print("示例 3: 生成數據模型")
    print("=" * 60)

    generator = ClineCodeGenerator()

    code = generator.generate_data_model(
        model_name="Product",
        fields={
            "id": "Integer (主鍵)",
            "name": "String (最大 200 字符)",
            "description": "Text",
            "price": "Decimal",
            "stock": "Integer",
            "category_id": "Integer (外鍵)",
            "created_at": "DateTime",
            "updated_at": "DateTime"
        },
        orm="sqlalchemy",
        validations={
            "name": ["必填", "唯一"],
            "price": ["必填", "大於 0"],
            "stock": ["必填", "大於等於 0"]
        }
    )

    print("\n生成的數據模型:")
    print(code)


def example_generate_from_openapi():
    """示例 4: 從 OpenAPI 規範生成代碼"""
    print("\n" + "=" * 60)
    print("示例 4: 從 OpenAPI 規範生成代碼")
    print("=" * 60)

    generator = ClineCodeGenerator()

    openapi_spec = """
    openapi: 3.0.0
    info:
      title: Todo API
      version: 1.0.0
    paths:
      /todos:
        get:
          summary: 獲取待辦事項列表
          responses:
            '200':
              description: 成功
        post:
          summary: 創建待辦事項
          requestBody:
            required: true
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    title:
                      type: string
                    completed:
                      type: boolean
          responses:
            '201':
              description: 創建成功
    """

    code = generator.generate_from_spec(
        spec=openapi_spec,
        spec_type="openapi",
        language="python"
    )

    print("\n生成的代碼:")
    print(code)


def example_generate_config():
    """示例 5: 生成配置文件"""
    print("\n" + "=" * 60)
    print("示例 5: 生成配置文件")
    print("=" * 60)

    generator = ClineCodeGenerator()

    config = generator.generate_config_file(
        config_type="dockerfile",
        project_type="FastAPI Python 應用",
        options={
            "python_version": "3.11",
            "port": 8000,
            "use_gunicorn": True,
            "workers": 4
        }
    )

    print("\n生成的 Dockerfile:")
    print(config)


def example_generate_test():
    """示例 6: 生成測試代碼"""
    print("\n" + "=" * 60)
    print("示例 6: 生成測試代碼")
    print("=" * 60)

    generator = ClineCodeGenerator()

    source_code = """
    def calculate_discount(price: float, discount_percent: float) -> float:
        '''計算折扣後的價格'''
        if price < 0:
            raise ValueError("價格不能為負數")
        if discount_percent < 0 or discount_percent > 100:
            raise ValueError("折扣百分比必須在 0-100 之間")

        discount_amount = price * (discount_percent / 100)
        return price - discount_amount
    """

    test_code = generator.generate_test(
        code=source_code,
        test_framework="pytest",
        coverage_target=100
    )

    print("\n生成的測試代碼:")
    print(test_code)


def example_batch_generation():
    """示例 7: 批量生成代碼"""
    print("\n" + "=" * 60)
    print("示例 7: 批量生成 CRUD 操作")
    print("=" * 60)

    generator = ClineCodeGenerator()

    # 定義實體
    entities = ["User", "Post", "Comment"]

    for entity in entities:
        print(f"\n--- 生成 {entity} CRUD 操作 ---")

        code = generator.generate_class(
            class_name=f"{entity}Service",
            description=f"{entity} 的 CRUD 服務類",
            language="python",
            features=[
                f"創建 {entity}",
                f"更新 {entity}",
                f"刪除 {entity}",
                f"查詢 {entity}",
                f"列出所有 {entity}"
            ]
        )

        # 只顯示前 300 字符
        print(code[:300] + "...")


def example_interactive_generation():
    """示例 8: 交互式代碼生成"""
    print("\n" + "=" * 60)
    print("示例 8: 交互式代碼生成")
    print("=" * 60)

    generator = ClineCodeGenerator()

    # 模擬交互式對話
    print("\n用戶: 我需要一個 Python 函數來驗證密碼強度")
    code1 = generator.generate_class(
        class_name="PasswordValidator",
        description="密碼強度驗證器",
        language="python",
        features=["檢查密碼長度", "檢查字符類型", "計算密碼強度分數"]
    )
    print("\n生成的代碼:")
    print(code1[:300] + "...")

    print("\n\n用戶: 請為這個驗證器添加自定義規則功能")
    # 在實際應用中，這裡會基於之前的代碼進行修改
    print("Cline: 好的，我會添加自定義規則功能...")


def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("Cline 代碼生成示例")
    print("=" * 60)

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\n⚠️  警告: 未設置 ANTHROPIC_API_KEY")
        return

    try:
        # 運行示例（注釋以節省 API 調用）
        # example_generate_class()
        # example_generate_api()
        # example_generate_model()
        # example_generate_from_openapi()
        # example_generate_config()
        # example_generate_test()
        # example_batch_generation()
        # example_interactive_generation()

        print("\n✅ 代碼生成示例已準備就緒")
        print("\n💡 提示:")
        print("1. 使用 generate_class() 生成完整的類")
        print("2. 使用 generate_api_endpoint() 快速創建 API")
        print("3. 使用 generate_data_model() 生成數據模型")
        print("4. 使用 generate_from_spec() 從規範生成代碼")
        print("5. 使用 generate_test() 自動生成測試")

    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

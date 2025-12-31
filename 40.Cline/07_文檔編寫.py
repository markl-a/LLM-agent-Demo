"""
Cline 文檔編寫示例

展示如何使用 Cline 自動生成文檔：
1. 生成 API 文檔
2. 生成代碼文檔（docstrings）
3. 生成 README 文件
4. 生成用戶指南
5. 生成開發者文檔
6. 生成變更日誌

自動化文檔生成確保文檔與代碼保持同步。
"""

import os
from typing import Dict, List, Any, Optional
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


class ClineDocGenerator:
    """Cline 文檔生成器"""

    def __init__(self, api_key: Optional[str] = None):
        """初始化文檔生成器"""
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

    def generate_api_docs(
        self,
        code: str,
        format: str = "openapi"
    ) -> str:
        """
        生成 API 文檔

        Args:
            code: API 代碼
            format: 文檔格式（openapi, markdown, html）

        Returns:
            生成的 API 文檔
        """
        prompt = f"""
        請為以下 API 代碼生成 {format} 格式的文檔：

        ```
        {code}
        ```

        要求:
        1. 包含所有端點
        2. 列出請求參數
        3. 說明響應格式
        4. 添加示例請求和響應
        5. 列出錯誤碼
        6. 包含認證說明

        請返回完整的 API 文檔。
        """

        system = "你是一個專業的技術文檔編寫專家，擅長創建清晰、全面的 API 文檔。"

        return self._call_claude(prompt, system)

    def generate_docstrings(
        self,
        code: str,
        style: str = "google"
    ) -> str:
        """
        生成代碼文檔字符串

        Args:
            code: 源代碼
            style: 文檔風格（google, numpy, sphinx）

        Returns:
            添加了文檔字符串的代碼
        """
        prompt = f"""
        請為以下代碼添加 {style} 風格的文檔字符串：

        ```
        {code}
        ```

        要求:
        1. 為所有類添加文檔
        2. 為所有公共方法添加文檔
        3. 說明參數類型和用途
        4. 說明返回值
        5. 列出可能的異常
        6. 添加使用示例

        請返回添加了完整文檔的代碼。
        """

        return self._call_claude(prompt)

    def generate_readme(
        self,
        project_name: str,
        project_description: str,
        features: List[str] = None,
        tech_stack: List[str] = None
    ) -> str:
        """
        生成 README 文件

        Args:
            project_name: 項目名稱
            project_description: 項目描述
            features: 功能列表
            tech_stack: 技術棧

        Returns:
            生成的 README 內容
        """
        features_str = "\n".join(f"- {f}" for f in (features or []))
        tech_str = "\n".join(f"- {t}" for t in (tech_stack or []))

        prompt = f"""
        請為以下項目生成專業的 README.md：

        項目名稱: {project_name}
        項目描述: {project_description}

        主要功能:
        {features_str if features_str else "待補充"}

        技術棧:
        {tech_str if tech_str else "待補充"}

        請包含以下部分:
        1. 項目標題和徽章
        2. 項目簡介
        3. 功能特性
        4. 技術棧
        5. 快速開始
        6. 安裝說明
        7. 使用示例
        8. API 文檔鏈接
        9. 配置說明
        10. 貢獻指南
        11. 許可證
        12. 聯繫方式

        請使用 Markdown 格式，並包含適當的代碼示例。
        """

        return self._call_claude(prompt)

    def generate_user_guide(
        self,
        product_name: str,
        target_audience: str,
        main_features: List[Dict[str, str]]
    ) -> str:
        """
        生成用戶指南

        Args:
            product_name: 產品名稱
            target_audience: 目標受眾
            main_features: 主要功能列表

        Returns:
            生成的用戶指南
        """
        import json
        features_str = json.dumps(main_features, indent=2, ensure_ascii=False)

        prompt = f"""
        請為 {product_name} 生成用戶指南：

        目標受眾: {target_audience}

        主要功能:
        {features_str}

        要求:
        1. 使用簡單易懂的語言
        2. 包含步驟說明
        3. 添加截圖說明（標註位置）
        4. 包含常見問題解答
        5. 提供故障排除指南
        6. 添加快速參考

        請使用 Markdown 格式。
        """

        return self._call_claude(prompt)

    def generate_dev_docs(
        self,
        project_structure: Dict[str, Any],
        architecture: str
    ) -> str:
        """
        生成開發者文檔

        Args:
            project_structure: 項目結構
            architecture: 架構說明

        Returns:
            生成的開發者文檔
        """
        import json
        structure_str = json.dumps(project_structure, indent=2, ensure_ascii=False)

        prompt = f"""
        請生成開發者文檔：

        項目結構:
        {structure_str}

        架構說明:
        {architecture}

        請包含:
        1. 架構概覽
        2. 項目結構說明
        3. 開發環境設置
        4. 編碼規範
        5. 代碼組織
        6. 測試指南
        7. 調試技巧
        8. 部署流程
        9. 性能優化建議
        10. 常見問題

        請使用 Markdown 格式。
        """

        return self._call_claude(prompt)

    def generate_changelog(
        self,
        version: str,
        changes: Dict[str, List[str]]
    ) -> str:
        """
        生成變更日誌

        Args:
            version: 版本號
            changes: 變更內容（按類別分組）

        Returns:
            生成的變更日誌
        """
        import json
        changes_str = json.dumps(changes, indent=2, ensure_ascii=False)

        prompt = f"""
        請為版本 {version} 生成變更日誌（CHANGELOG.md）：

        變更內容:
        {changes_str}

        要求:
        1. 遵循 Keep a Changelog 格式
        2. 分類變更（Added, Changed, Deprecated, Removed, Fixed, Security）
        3. 使用清晰的描述
        4. 包含相關的 PR 或 Issue 編號（用占位符）
        5. 突出重要變更

        請使用 Markdown 格式。
        """

        return self._call_claude(prompt)

    def generate_tutorial(
        self,
        topic: str,
        difficulty: str,
        prerequisites: List[str] = None
    ) -> str:
        """
        生成教程

        Args:
            topic: 教程主題
            difficulty: 難度級別
            prerequisites: 先決條件

        Returns:
            生成的教程
        """
        prereq_str = "\n".join(f"- {p}" for p in (prerequisites or []))

        prompt = f"""
        請生成一個關於 "{topic}" 的教程：

        難度級別: {difficulty}

        先決條件:
        {prereq_str if prereq_str else "無特殊要求"}

        要求:
        1. 清晰的學習目標
        2. 循序漸進的步驟
        3. 實際代碼示例
        4. 解釋重要概念
        5. 包含練習題
        6. 提供參考資源

        請使用 Markdown 格式，並包含完整的代碼示例。
        """

        return self._call_claude(prompt)

    def generate_inline_comments(
        self,
        code: str,
        verbosity: str = "medium"
    ) -> str:
        """
        生成行內註釋

        Args:
            code: 源代碼
            verbosity: 註釋詳細程度（low, medium, high）

        Returns:
            添加註釋後的代碼
        """
        prompt = f"""
        請為以下代碼添加行內註釋：

        ```
        {code}
        ```

        註釋詳細程度: {verbosity}

        要求:
        1. 解釋複雜邏輯
        2. 說明關鍵變量
        3. 標註重要決策
        4. 警告潛在問題
        5. 不要過度註釋明顯的代碼

        請返回添加了註釋的代碼。
        """

        return self._call_claude(prompt)


def example_generate_api_docs():
    """示例 1: 生成 API 文檔"""
    print("=" * 60)
    print("示例 1: 生成 API 文檔")
    print("=" * 60)

    generator = ClineDocGenerator()

    # API 代碼
    api_code = """
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    username: str
    email: str
    full_name: str = None

@app.post("/users/", status_code=201)
async def create_user(user: User):
    return {"id": 1, **user.dict()}

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    if user_id == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user_id, "username": "testuser"}

@app.put("/users/{user_id}")
async def update_user(user_id: int, user: User):
    return {"id": user_id, **user.dict()}

@app.delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: int):
    pass
    """

    print("\nAPI 代碼:")
    print(api_code)

    docs = generator.generate_api_docs(api_code, format="markdown")

    print("\n生成的 API 文檔:")
    print(docs)


def example_generate_docstrings():
    """示例 2: 生成文檔字符串"""
    print("\n" + "=" * 60)
    print("示例 2: 生成文檔字符串")
    print("=" * 60)

    generator = ClineDocGenerator()

    # 缺少文檔的代碼
    undocumented_code = """
class DataProcessor:
    def __init__(self, config):
        self.config = config
        self.cache = {}

    def process(self, data, options=None):
        if not data:
            raise ValueError("Data cannot be empty")

        result = []
        for item in data:
            processed = self._transform(item, options)
            if processed:
                result.append(processed)

        return result

    def _transform(self, item, options):
        if item in self.cache:
            return self.cache[item]

        transformed = item.upper()
        if options and options.get('reverse'):
            transformed = transformed[::-1]

        self.cache[item] = transformed
        return transformed

    def clear_cache(self):
        self.cache.clear()
    """

    print("\n原始代碼（無文檔）:")
    print(undocumented_code)

    documented_code = generator.generate_docstrings(
        code=undocumented_code,
        style="google"
    )

    print("\n添加文檔後的代碼:")
    print(documented_code)


def example_generate_readme():
    """示例 3: 生成 README"""
    print("\n" + "=" * 60)
    print("示例 3: 生成 README 文件")
    print("=" * 60)

    generator = ClineDocGenerator()

    readme = generator.generate_readme(
        project_name="FastAPI E-Commerce API",
        project_description="一個現代化的電子商務 RESTful API，支持產品管理、訂單處理和用戶認證",
        features=[
            "用戶註冊和認證（JWT）",
            "產品 CRUD 操作",
            "購物車管理",
            "訂單處理",
            "支付集成",
            "郵件通知"
        ],
        tech_stack=[
            "FastAPI",
            "PostgreSQL",
            "Redis",
            "Docker",
            "Pytest"
        ]
    )

    print("\n生成的 README:")
    print(readme)


def example_generate_user_guide():
    """示例 4: 生成用戶指南"""
    print("\n" + "=" * 60)
    print("示例 4: 生成用戶指南")
    print("=" * 60)

    generator = ClineDocGenerator()

    features = [
        {
            "name": "創建項目",
            "description": "如何創建和配置新項目"
        },
        {
            "name": "添加成員",
            "description": "邀請團隊成員並分配權限"
        },
        {
            "name": "任務管理",
            "description": "創建、分配和追蹤任務"
        }
    ]

    guide = generator.generate_user_guide(
        product_name="TaskManager Pro",
        target_audience="項目經理和團隊領導",
        main_features=features
    )

    print("\n生成的用戶指南:")
    print(guide)


def example_generate_dev_docs():
    """示例 5: 生成開發者文檔"""
    print("\n" + "=" * 60)
    print("示例 5: 生成開發者文檔")
    print("=" * 60)

    generator = ClineDocGenerator()

    project_structure = {
        "src/": {
            "api/": "API 路由和端點",
            "models/": "數據模型",
            "services/": "業務邏輯",
            "utils/": "工具函數"
        },
        "tests/": "測試文件",
        "docs/": "文檔"
    }

    architecture = """
    採用三層架構：
    - API 層：處理 HTTP 請求
    - 服務層：實現業務邏輯
    - 數據層：數據庫訪問

    使用依賴注入模式和倉儲模式。
    """

    docs = generator.generate_dev_docs(
        project_structure=project_structure,
        architecture=architecture
    )

    print("\n生成的開發者文檔:")
    print(docs)


def example_generate_changelog():
    """示例 6: 生成變更日誌"""
    print("\n" + "=" * 60)
    print("示例 6: 生成變更日誌")
    print("=" * 60)

    generator = ClineDocGenerator()

    changes = {
        "Added": [
            "用戶個人資料頁面",
            "郵件通知功能",
            "數據導出功能"
        ],
        "Changed": [
            "改進登錄頁面 UI",
            "優化數據庫查詢性能"
        ],
        "Fixed": [
            "修復購物車計算錯誤",
            "修復文件上傳失敗的問題"
        ],
        "Security": [
            "修復 XSS 漏洞",
            "更新依賴包以修復安全問題"
        ]
    }

    changelog = generator.generate_changelog(
        version="2.0.0",
        changes=changes
    )

    print("\n生成的變更日誌:")
    print(changelog)


def example_generate_tutorial():
    """示例 7: 生成教程"""
    print("\n" + "=" * 60)
    print("示例 7: 生成教程")
    print("=" * 60)

    generator = ClineDocGenerator()

    tutorial = generator.generate_tutorial(
        topic="使用 FastAPI 構建 RESTful API",
        difficulty="中級",
        prerequisites=[
            "Python 基礎知識",
            "HTTP 協議基本了解",
            "基本的數據庫知識"
        ]
    )

    print("\n生成的教程:")
    print(tutorial)


def example_generate_inline_comments():
    """示例 8: 生成行內註釋"""
    print("\n" + "=" * 60)
    print("示例 8: 生成行內註釋")
    print("=" * 60)

    generator = ClineDocGenerator()

    # 缺少註釋的複雜代碼
    complex_code = """
def calculate_score(data, weights, threshold=0.5):
    normalized = [(x - min(data)) / (max(data) - min(data)) for x in data]
    weighted = [n * w for n, w in zip(normalized, weights)]
    score = sum(weighted) / len(weighted)

    if score > threshold:
        adjusted = score * 1.2
        if adjusted > 1.0:
            adjusted = 1.0
    else:
        adjusted = score * 0.8

    return round(adjusted, 3)
    """

    print("\n原始代碼（無註釋）:")
    print(complex_code)

    commented_code = generator.generate_inline_comments(
        code=complex_code,
        verbosity="high"
    )

    print("\n添加註釋後的代碼:")
    print(commented_code)


def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("Cline 文檔編寫示例")
    print("=" * 60)

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\n⚠️  警告: 未設置 ANTHROPIC_API_KEY")
        return

    try:
        # 運行示例（注釋以節省 API 調用）
        # example_generate_api_docs()
        # example_generate_docstrings()
        # example_generate_readme()
        # example_generate_user_guide()
        # example_generate_dev_docs()
        # example_generate_changelog()
        # example_generate_tutorial()
        # example_generate_inline_comments()

        print("\n✅ 文檔生成示例已準備就緒")
        print("\n💡 提示:")
        print("1. 使用 generate_api_docs() 創建 API 文檔")
        print("2. 使用 generate_docstrings() 添加代碼文檔")
        print("3. 使用 generate_readme() 快速創建 README")
        print("4. 使用 generate_user_guide() 編寫用戶指南")
        print("5. 使用 generate_changelog() 維護變更日誌")

        print("\n📚 文檔最佳實踐:")
        print("- 保持文檔與代碼同步")
        print("- 使用清晰簡潔的語言")
        print("- 提供實際的代碼示例")
        print("- 定期更新和審查文檔")

    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

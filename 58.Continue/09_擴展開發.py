"""
Continue AI 編程助手 - 擴展開發

這個文件展示了如何開發 Continue 擴展。
包括自定義命令、上下文提供者、UI 組件等。

主要內容:
1. 擴展架構
2. 自定義命令開發
3. 上下文提供者開發
4. UI 擴展
5. 事件處理
6. 擴展配置
7. 擴展發布

Author: Continue Team
Date: 2025
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path


# =====================================================
# 第一部分: 擴展架構定義
# =====================================================

class ExtensionType(Enum):
    """
    擴展類型
    """
    COMMAND = "command"  # 命令擴展
    CONTEXT_PROVIDER = "context_provider"  # 上下文提供者
    UI_COMPONENT = "ui_component"  # UI 組件
    MODEL_PROVIDER = "model_provider"  # 模型提供者
    TOOL = "tool"  # 工具
    THEME = "theme"  # 主題


@dataclass
class ExtensionMetadata:
    """
    擴展元數據
    """
    name: str
    version: str
    author: str
    description: str
    extension_type: ExtensionType
    dependencies: List[str] = field(default_factory=list)
    homepage: str = ""
    repository: str = ""
    license: str = "MIT"

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "type": self.extension_type.value,
            "dependencies": self.dependencies,
            "homepage": self.homepage,
            "repository": self.repository,
            "license": self.license
        }


class ExtensionContext:
    """
    擴展上下文

    提供給擴展的 API 和資源訪問
    """

    def __init__(self):
        """初始化擴展上下文"""
        self.workspace_root: Optional[Path] = None
        self.config: Dict[str, Any] = {}
        self.commands: Dict[str, Callable] = {}
        self.events: Dict[str, List[Callable]] = {}

    def get_config(self, key: str, default: Any = None) -> Any:
        """
        獲取配置

        Args:
            key: 配置鍵
            default: 默認值

        Returns:
            配置值
        """
        return self.config.get(key, default)

    def set_config(self, key: str, value: Any):
        """
        設置配置

        Args:
            key: 配置鍵
            value: 配置值
        """
        self.config[key] = value

    def register_command(self, name: str, handler: Callable):
        """
        註冊命令

        Args:
            name: 命令名稱
            handler: 命令處理函數
        """
        self.commands[name] = handler
        print(f"命令 '{name}' 已註冊")

    def emit_event(self, event_name: str, data: Any = None):
        """
        觸發事件

        Args:
            event_name: 事件名稱
            data: 事件數據
        """
        if event_name in self.events:
            for handler in self.events[event_name]:
                handler(data)

    def on_event(self, event_name: str, handler: Callable):
        """
        監聽事件

        Args:
            event_name: 事件名稱
            handler: 事件處理函數
        """
        if event_name not in self.events:
            self.events[event_name] = []
        self.events[event_name].append(handler)


# =====================================================
# 第二部分: 擴展基類
# =====================================================

class Extension(ABC):
    """
    擴展抽象基類

    所有擴展都應繼承此類
    """

    def __init__(self, metadata: ExtensionMetadata):
        """
        初始化擴展

        Args:
            metadata: 擴展元數據
        """
        self.metadata = metadata
        self.context: Optional[ExtensionContext] = None
        self.enabled = False

    @abstractmethod
    def activate(self, context: ExtensionContext):
        """
        激活擴展

        Args:
            context: 擴展上下文
        """
        pass

    @abstractmethod
    def deactivate(self):
        """
        停用擴展
        """
        pass

    def get_metadata(self) -> ExtensionMetadata:
        """
        獲取元數據

        Returns:
            擴展元數據
        """
        return self.metadata


# =====================================================
# 第三部分: 自定義命令擴展示例
# =====================================================

class CodeFormatterExtension(Extension):
    """
    代碼格式化擴展

    提供自動代碼格式化功能
    """

    def __init__(self):
        metadata = ExtensionMetadata(
            name="code-formatter",
            version="1.0.0",
            author="Continue Team",
            description="自動代碼格式化擴展",
            extension_type=ExtensionType.COMMAND,
            dependencies=["black", "prettier"]
        )
        super().__init__(metadata)

    def activate(self, context: ExtensionContext):
        """激活擴展"""
        self.context = context
        self.enabled = True

        # 註冊命令
        context.register_command("format", self.format_code)
        context.register_command("format-python", self.format_python)
        context.register_command("format-javascript", self.format_javascript)

        # 監聽事件
        context.on_event("file-saved", self.on_file_saved)

        print(f"擴展 '{self.metadata.name}' 已激活")

    def deactivate(self):
        """停用擴展"""
        self.enabled = False
        print(f"擴展 '{self.metadata.name}' 已停用")

    def format_code(self, code: str, language: str) -> str:
        """
        格式化代碼

        Args:
            code: 代碼
            language: 語言

        Returns:
            格式化後的代碼
        """
        if language == "python":
            return self.format_python(code)
        elif language in ["javascript", "typescript"]:
            return self.format_javascript(code)
        else:
            return code

    def format_python(self, code: str) -> str:
        """
        格式化 Python 代碼

        Args:
            code: Python 代碼

        Returns:
            格式化後的代碼
        """
        # 這裡應該調用 black
        print("使用 Black 格式化 Python 代碼...")
        formatted = code  # 實際應該使用 black.format_str(code)
        return formatted

    def format_javascript(self, code: str) -> str:
        """
        格式化 JavaScript 代碼

        Args:
            code: JavaScript 代碼

        Returns:
            格式化後的代碼
        """
        # 這裡應該調用 prettier
        print("使用 Prettier 格式化 JavaScript 代碼...")
        formatted = code  # 實際應該使用 prettier
        return formatted

    def on_file_saved(self, data: Dict[str, Any]):
        """
        文件保存事件處理

        Args:
            data: 事件數據
        """
        auto_format = self.context.get_config("auto_format_on_save", False)

        if auto_format:
            print("自動格式化保存的文件...")
            # 執行格式化


class SnippetLibraryExtension(Extension):
    """
    代碼片段庫擴展

    管理和插入常用代碼片段
    """

    def __init__(self):
        metadata = ExtensionMetadata(
            name="snippet-library",
            version="1.0.0",
            author="Continue Team",
            description="代碼片段管理擴展",
            extension_type=ExtensionType.TOOL
        )
        super().__init__(metadata)
        self.snippets: Dict[str, str] = {}

    def activate(self, context: ExtensionContext):
        """激活擴展"""
        self.context = context
        self.enabled = True

        # 註冊命令
        context.register_command("snippet-insert", self.insert_snippet)
        context.register_command("snippet-list", self.list_snippets)
        context.register_command("snippet-add", self.add_snippet)

        # 加載預定義片段
        self._load_default_snippets()

        print(f"擴展 '{self.metadata.name}' 已激活")

    def deactivate(self):
        """停用擴展"""
        self.enabled = False

    def _load_default_snippets(self):
        """加載默認代碼片段"""
        self.snippets = {
            "py-class": """class ClassName:
    '''類描述'''

    def __init__(self):
        '''初始化'''
        pass
""",
            "py-function": """def function_name():
    '''函數描述'''
    pass
""",
            "py-main": """def main():
    '''主函數'''
    pass


if __name__ == "__main__":
    main()
""",
            "js-function": """function functionName() {
    // 函數實現
}
""",
            "js-async": """async function asyncFunction() {
    try {
        // 異步操作
    } catch (error) {
        console.error(error);
    }
}
"""
        }

    def insert_snippet(self, snippet_name: str) -> Optional[str]:
        """
        插入代碼片段

        Args:
            snippet_name: 片段名稱

        Returns:
            片段內容
        """
        if snippet_name in self.snippets:
            return self.snippets[snippet_name]
        else:
            print(f"未找到片段: {snippet_name}")
            return None

    def list_snippets(self) -> List[str]:
        """
        列出所有片段

        Returns:
            片段名稱列表
        """
        return list(self.snippets.keys())

    def add_snippet(self, name: str, content: str):
        """
        添加片段

        Args:
            name: 片段名稱
            content: 片段內容
        """
        self.snippets[name] = content
        print(f"片段 '{name}' 已添加")


# =====================================================
# 第四部分: 上下文提供者擴展示例
# =====================================================

class DatabaseSchemaProvider(Extension):
    """
    數據庫架構提供者

    提供數據庫表結構作為上下文
    """

    def __init__(self):
        metadata = ExtensionMetadata(
            name="database-schema-provider",
            version="1.0.0",
            author="Continue Team",
            description="提供數據庫架構上下文",
            extension_type=ExtensionType.CONTEXT_PROVIDER
        )
        super().__init__(metadata)
        self.schemas: Dict[str, Any] = {}

    def activate(self, context: ExtensionContext):
        """激活擴展"""
        self.context = context
        self.enabled = True

        # 註冊命令
        context.register_command("db-load-schema", self.load_schema)
        context.register_command("db-get-table", self.get_table_info)

        print(f"擴展 '{self.metadata.name}' 已激活")

    def deactivate(self):
        """停用擴展"""
        self.enabled = False

    def load_schema(self, connection_string: str) -> bool:
        """
        加載數據庫架構

        Args:
            connection_string: 數據庫連接字符串

        Returns:
            是否加載成功
        """
        print(f"正在加載數據庫架構: {connection_string}")

        # 這裡應該實際連接數據庫並讀取架構
        # 模擬架構數據
        self.schemas = {
            "users": {
                "columns": [
                    {"name": "id", "type": "INTEGER", "primary_key": True},
                    {"name": "username", "type": "VARCHAR(50)", "nullable": False},
                    {"name": "email", "type": "VARCHAR(100)", "nullable": False},
                    {"name": "created_at", "type": "TIMESTAMP", "nullable": False}
                ],
                "indexes": ["username", "email"]
            },
            "posts": {
                "columns": [
                    {"name": "id", "type": "INTEGER", "primary_key": True},
                    {"name": "user_id", "type": "INTEGER", "foreign_key": "users.id"},
                    {"name": "title", "type": "VARCHAR(200)", "nullable": False},
                    {"name": "content", "type": "TEXT", "nullable": True},
                    {"name": "created_at", "type": "TIMESTAMP", "nullable": False}
                ]
            }
        }

        print(f"已加載 {len(self.schemas)} 個表的架構")
        return True

    def get_table_info(self, table_name: str) -> Optional[Dict[str, Any]]:
        """
        獲取表信息

        Args:
            table_name: 表名

        Returns:
            表信息
        """
        return self.schemas.get(table_name)

    def provide_context(self, query: str) -> str:
        """
        提供上下文

        Args:
            query: 查詢

        Returns:
            上下文字符串
        """
        context = "數據庫架構:\n\n"

        for table_name, schema in self.schemas.items():
            context += f"表: {table_name}\n"
            for col in schema["columns"]:
                context += f"  - {col['name']} ({col['type']})\n"
            context += "\n"

        return context


class APIDocumentationProvider(Extension):
    """
    API 文檔提供者

    提供 API 文檔作為上下文
    """

    def __init__(self):
        metadata = ExtensionMetadata(
            name="api-documentation-provider",
            version="1.0.0",
            author="Continue Team",
            description="提供 API 文檔上下文",
            extension_type=ExtensionType.CONTEXT_PROVIDER
        )
        super().__init__(metadata)
        self.api_docs: Dict[str, Any] = {}

    def activate(self, context: ExtensionContext):
        """激活擴展"""
        self.context = context
        self.enabled = True

        context.register_command("api-load-docs", self.load_documentation)
        context.register_command("api-search", self.search_api)

        print(f"擴展 '{self.metadata.name}' 已激活")

    def deactivate(self):
        """停用擴展"""
        self.enabled = False

    def load_documentation(self, api_spec_file: str) -> bool:
        """
        加載 API 文檔

        Args:
            api_spec_file: API 規範文件路徑(如 OpenAPI/Swagger)

        Returns:
            是否加載成功
        """
        print(f"正在加載 API 文檔: {api_spec_file}")

        # 這裡應該解析 OpenAPI/Swagger 文件
        # 模擬 API 文檔
        self.api_docs = {
            "endpoints": [
                {
                    "path": "/api/users",
                    "method": "GET",
                    "description": "獲取用戶列表",
                    "parameters": [
                        {"name": "page", "type": "integer", "required": False},
                        {"name": "limit", "type": "integer", "required": False}
                    ],
                    "response": {
                        "200": {
                            "description": "成功",
                            "schema": "User[]"
                        }
                    }
                },
                {
                    "path": "/api/users/{id}",
                    "method": "GET",
                    "description": "獲取指定用戶",
                    "parameters": [
                        {"name": "id", "type": "integer", "required": True}
                    ]
                }
            ]
        }

        print(f"已加載 {len(self.api_docs['endpoints'])} 個 API 端點")
        return True

    def search_api(self, keyword: str) -> List[Dict[str, Any]]:
        """
        搜索 API

        Args:
            keyword: 關鍵詞

        Returns:
            匹配的 API 列表
        """
        results = []

        for endpoint in self.api_docs.get("endpoints", []):
            if keyword.lower() in endpoint["path"].lower() or \
               keyword.lower() in endpoint["description"].lower():
                results.append(endpoint)

        return results


# =====================================================
# 第五部分: UI 擴展示例
# =====================================================

class CodeMetricsPanel(Extension):
    """
    代碼指標面板

    顯示代碼質量指標的 UI 面板
    """

    def __init__(self):
        metadata = ExtensionMetadata(
            name="code-metrics-panel",
            version="1.0.0",
            author="Continue Team",
            description="代碼質量指標面板",
            extension_type=ExtensionType.UI_COMPONENT
        )
        super().__init__(metadata)
        self.metrics: Dict[str, Any] = {}

    def activate(self, context: ExtensionContext):
        """激活擴展"""
        self.context = context
        self.enabled = True

        # 註冊命令
        context.register_command("metrics-show", self.show_metrics)
        context.register_command("metrics-calculate", self.calculate_metrics)

        # 監聽事件
        context.on_event("file-opened", self.on_file_opened)

        print(f"擴展 '{self.metadata.name}' 已激活")

    def deactivate(self):
        """停用擴展"""
        self.enabled = False

    def calculate_metrics(self, code: str) -> Dict[str, Any]:
        """
        計算代碼指標

        Args:
            code: 代碼

        Returns:
            指標數據
        """
        lines = code.split('\n')
        total_lines = len(lines)
        code_lines = sum(1 for line in lines if line.strip() and not line.strip().startswith('#'))
        comment_lines = sum(1 for line in lines if line.strip().startswith('#'))

        self.metrics = {
            "total_lines": total_lines,
            "code_lines": code_lines,
            "comment_lines": comment_lines,
            "comment_ratio": comment_lines / code_lines if code_lines > 0 else 0,
            "complexity": self._calculate_complexity(code)
        }

        return self.metrics

    def _calculate_complexity(self, code: str) -> int:
        """
        計算循環複雜度(簡化版)

        Args:
            code: 代碼

        Returns:
            複雜度分數
        """
        # 簡化計算:統計決策點
        keywords = ['if', 'elif', 'else', 'for', 'while', 'try', 'except']
        complexity = 1  # 基礎複雜度

        for keyword in keywords:
            complexity += code.count(f' {keyword} ')

        return complexity

    def show_metrics(self) -> str:
        """
        顯示指標

        Returns:
            格式化的指標文本
        """
        if not self.metrics:
            return "尚未計算指標"

        output = "=== 代碼指標 ===\n\n"
        output += f"總行數: {self.metrics['total_lines']}\n"
        output += f"代碼行數: {self.metrics['code_lines']}\n"
        output += f"註釋行數: {self.metrics['comment_lines']}\n"
        output += f"註釋比例: {self.metrics['comment_ratio']:.2%}\n"
        output += f"循環複雜度: {self.metrics['complexity']}\n"

        return output

    def on_file_opened(self, data: Dict[str, Any]):
        """
        文件打開事件處理

        Args:
            data: 事件數據
        """
        auto_calculate = self.context.get_config("auto_calculate_metrics", True)

        if auto_calculate and "content" in data:
            self.calculate_metrics(data["content"])


# =====================================================
# 第六部分: 擴展管理器
# =====================================================

class ExtensionManager:
    """
    擴展管理器

    管理所有擴展的生命週期
    """

    def __init__(self):
        """初始化擴展管理器"""
        self.extensions: Dict[str, Extension] = {}
        self.context = ExtensionContext()

    def register_extension(self, extension: Extension) -> bool:
        """
        註冊擴展

        Args:
            extension: 擴展實例

        Returns:
            是否註冊成功
        """
        name = extension.metadata.name

        if name in self.extensions:
            print(f"擴展 '{name}' 已存在")
            return False

        self.extensions[name] = extension
        print(f"擴展 '{name}' 已註冊")
        return True

    def activate_extension(self, name: str) -> bool:
        """
        激活擴展

        Args:
            name: 擴展名稱

        Returns:
            是否激活成功
        """
        if name not in self.extensions:
            print(f"未找到擴展: {name}")
            return False

        extension = self.extensions[name]

        if extension.enabled:
            print(f"擴展 '{name}' 已經激活")
            return True

        try:
            extension.activate(self.context)
            return True
        except Exception as e:
            print(f"激活擴展 '{name}' 失敗: {e}")
            return False

    def deactivate_extension(self, name: str) -> bool:
        """
        停用擴展

        Args:
            name: 擴展名稱

        Returns:
            是否停用成功
        """
        if name not in self.extensions:
            return False

        extension = self.extensions[name]

        if not extension.enabled:
            return True

        try:
            extension.deactivate()
            return True
        except Exception as e:
            print(f"停用擴展 '{name}' 失敗: {e}")
            return False

    def list_extensions(self) -> List[str]:
        """
        列出所有擴展

        Returns:
            擴展名稱列表
        """
        return list(self.extensions.keys())

    def get_extension_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        獲取擴展信息

        Args:
            name: 擴展名稱

        Returns:
            擴展信息
        """
        if name not in self.extensions:
            return None

        extension = self.extensions[name]
        metadata = extension.metadata

        return {
            "name": metadata.name,
            "version": metadata.version,
            "author": metadata.author,
            "description": metadata.description,
            "type": metadata.extension_type.value,
            "enabled": extension.enabled,
            "dependencies": metadata.dependencies
        }


# =====================================================
# 第七部分: 使用示例
# =====================================================

def extension_management_example():
    """
    擴展管理示例
    """
    print("=" * 60)
    print("示例 1: 擴展管理")
    print("=" * 60)

    # 創建擴展管理器
    manager = ExtensionManager()

    # 註冊擴展
    formatter = CodeFormatterExtension()
    snippets = SnippetLibraryExtension()
    metrics = CodeMetricsPanel()

    manager.register_extension(formatter)
    manager.register_extension(snippets)
    manager.register_extension(metrics)

    # 列出擴展
    print("\n已註冊的擴展:")
    for name in manager.list_extensions():
        info = manager.get_extension_info(name)
        print(f"  - {name} ({info['type']}): {info['description']}")

    # 激活擴展
    print("\n激活擴展:")
    manager.activate_extension("code-formatter")
    manager.activate_extension("snippet-library")
    manager.activate_extension("code-metrics-panel")


def snippet_extension_example():
    """
    代碼片段擴展示例
    """
    print("\n" + "=" * 60)
    print("示例 2: 代碼片段擴展")
    print("=" * 60)

    # 創建和激活擴展
    extension = SnippetLibraryExtension()
    context = ExtensionContext()
    extension.activate(context)

    # 列出片段
    print("\n可用片段:")
    for snippet_name in extension.list_snippets():
        print(f"  - {snippet_name}")

    # 插入片段
    print("\n插入 Python 類片段:")
    code = extension.insert_snippet("py-class")
    print(code)


def context_provider_example():
    """
    上下文提供者擴展示例
    """
    print("\n" + "=" * 60)
    print("示例 3: 上下文提供者")
    print("=" * 60)

    # 創建數據庫架構提供者
    db_provider = DatabaseSchemaProvider()
    context = ExtensionContext()
    db_provider.activate(context)

    # 加載架構
    db_provider.load_schema("postgresql://localhost/mydb")

    # 提供上下文
    print("\n數據庫上下文:")
    print(db_provider.provide_context(""))


def main():
    """
    主函數
    """
    print("Continue - 擴展開發\n")

    extension_management_example()
    snippet_extension_example()
    context_provider_example()

    print("\n" + "=" * 60)
    print("所有示例運行完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()

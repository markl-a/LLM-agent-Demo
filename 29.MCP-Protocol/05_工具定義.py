"""
MCP 工具定義
============

本模組深入探討如何定義和實現高質量的 MCP 工具。
學習工具設計原則、參數驗證、錯誤處理等最佳實踐。

學習目標：
- 理解工具的結構和 JSON Schema
- 實現參數驗證
- 處理各種數據類型
- 設計易用的工具 API

作者：Claude (Anthropic)
日期：2025-12-22
"""

from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
import json


# ============================================================================
# 第一部分：工具定義基礎
# ============================================================================

class ToolCategory(Enum):
    """工具類別"""
    FILE_SYSTEM = "文件系統"
    DATABASE = "數據庫"
    API = "API 調用"
    COMPUTATION = "計算"
    DATA_TRANSFORM = "數據轉換"
    SYSTEM = "系統操作"


@dataclass
class ToolDefinition:
    """工具定義結構"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    category: ToolCategory
    examples: Optional[List[Dict[str, Any]]] = None


class ToolBuilder:
    """工具建構器"""

    @staticmethod
    def create_tool(
        name: str,
        description: str,
        properties: Dict[str, Dict[str, Any]],
        required: List[str],
        category: ToolCategory = ToolCategory.COMPUTATION
    ) -> ToolDefinition:
        """
        創建工具定義

        Args:
            name: 工具名稱（snake_case）
            description: 工具描述（清晰說明用途）
            properties: 參數定義
            required: 必需參數列表
            category: 工具類別

        Returns:
            完整的工具定義
        """
        input_schema = {
            "type": "object",
            "properties": properties,
            "required": required
        }

        return ToolDefinition(
            name=name,
            description=description,
            input_schema=input_schema,
            category=category
        )


# ============================================================================
# 第二部分：常見工具模式
# ============================================================================

class CommonToolPatterns:
    """常見工具模式集合"""

    @staticmethod
    def string_operation_tool() -> ToolDefinition:
        """字符串操作工具"""
        return ToolBuilder.create_tool(
            name="transform_string",
            description="對字符串執行各種轉換操作",
            properties={
                "text": {
                    "type": "string",
                    "description": "要轉換的文本"
                },
                "operation": {
                    "type": "string",
                    "enum": ["uppercase", "lowercase", "reverse", "capitalize"],
                    "description": "轉換操作類型"
                }
            },
            required=["text", "operation"],
            category=ToolCategory.DATA_TRANSFORM
        )

    @staticmethod
    def file_operation_tool() -> ToolDefinition:
        """文件操作工具"""
        return ToolBuilder.create_tool(
            name="manage_file",
            description="執行文件操作（讀取、寫入、刪除）",
            properties={
                "path": {
                    "type": "string",
                    "description": "文件路徑"
                },
                "action": {
                    "type": "string",
                    "enum": ["read", "write", "delete"],
                    "description": "操作類型"
                },
                "content": {
                    "type": "string",
                    "description": "寫入時的文件內容"
                },
                "encoding": {
                    "type": "string",
                    "enum": ["utf-8", "ascii", "latin-1"],
                    "default": "utf-8",
                    "description": "文件編碼"
                }
            },
            required=["path", "action"],
            category=ToolCategory.FILE_SYSTEM
        )

    @staticmethod
    def database_query_tool() -> ToolDefinition:
        """數據庫查詢工具"""
        return ToolBuilder.create_tool(
            name="execute_sql",
            description="執行 SQL 查詢並返回結果",
            properties={
                "database": {
                    "type": "string",
                    "description": "數據庫名稱"
                },
                "query": {
                    "type": "string",
                    "description": "SQL 查詢語句"
                },
                "parameters": {
                    "type": "array",
                    "items": {
                        "type": ["string", "number", "boolean", "null"]
                    },
                    "description": "查詢參數（用於參數化查詢）"
                },
                "timeout": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 300,
                    "default": 30,
                    "description": "查詢超時時間（秒）"
                }
            },
            required=["database", "query"],
            category=ToolCategory.DATABASE
        )

    @staticmethod
    def api_request_tool() -> ToolDefinition:
        """API 請求工具"""
        return ToolBuilder.create_tool(
            name="http_request",
            description="發送 HTTP 請求到指定的 API 端點",
            properties={
                "url": {
                    "type": "string",
                    "format": "uri",
                    "description": "API 端點 URL"
                },
                "method": {
                    "type": "string",
                    "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"],
                    "default": "GET",
                    "description": "HTTP 方法"
                },
                "headers": {
                    "type": "object",
                    "additionalProperties": {"type": "string"},
                    "description": "請求頭"
                },
                "body": {
                    "type": "object",
                    "description": "請求體（JSON）"
                },
                "timeout": {
                    "type": "number",
                    "default": 30,
                    "description": "請求超時時間（秒）"
                }
            },
            required=["url"],
            category=ToolCategory.API
        )

    @staticmethod
    def calculation_tool() -> ToolDefinition:
        """計算工具"""
        return ToolBuilder.create_tool(
            name="calculate",
            description="執行數學計算",
            properties={
                "expression": {
                    "type": "string",
                    "description": "數學表達式（如 '2 + 2 * 3'）"
                },
                "precision": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 10,
                    "default": 2,
                    "description": "結果精度（小數位數）"
                }
            },
            required=["expression"],
            category=ToolCategory.COMPUTATION
        )


# ============================================================================
# 第三部分：進階工具定義
# ============================================================================

class AdvancedToolPatterns:
    """進階工具模式"""

    @staticmethod
    def batch_operation_tool() -> ToolDefinition:
        """批量操作工具"""
        return ToolBuilder.create_tool(
            name="batch_process",
            description="對多個項目執行批量處理",
            properties={
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "data": {"type": "object"}
                        },
                        "required": ["id"]
                    },
                    "minItems": 1,
                    "maxItems": 100,
                    "description": "要處理的項目列表"
                },
                "operation": {
                    "type": "string",
                    "description": "要執行的操作"
                },
                "parallel": {
                    "type": "boolean",
                    "default": True,
                    "description": "是否並行處理"
                },
                "max_workers": {
                    "type": "number",
                    "minimum": 1,
                    "maximum": 10,
                    "default": 5,
                    "description": "最大並行工作線程數"
                }
            },
            required=["items", "operation"],
            category=ToolCategory.COMPUTATION
        )

    @staticmethod
    def streaming_tool() -> ToolDefinition:
        """流式處理工具"""
        return ToolBuilder.create_tool(
            name="process_stream",
            description="處理流式數據（如日誌、事件流）",
            properties={
                "source": {
                    "type": "string",
                    "description": "數據源（文件路徑或 URL）"
                },
                "filter": {
                    "type": "object",
                    "properties": {
                        "pattern": {"type": "string"},
                        "fields": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "description": "過濾條件"
                },
                "limit": {
                    "type": "number",
                    "minimum": 1,
                    "default": 1000,
                    "description": "最大處理記錄數"
                }
            },
            required=["source"],
            category=ToolCategory.DATA_TRANSFORM
        )

    @staticmethod
    def conditional_tool() -> ToolDefinition:
        """條件執行工具"""
        return ToolBuilder.create_tool(
            name="conditional_execute",
            description="根據條件執行不同的操作",
            properties={
                "condition": {
                    "type": "object",
                    "properties": {
                        "field": {"type": "string"},
                        "operator": {
                            "type": "string",
                            "enum": ["==", "!=", ">", "<", ">=", "<=", "contains"]
                        },
                        "value": {
                            "type": ["string", "number", "boolean"]
                        }
                    },
                    "required": ["field", "operator", "value"],
                    "description": "判斷條件"
                },
                "if_true": {
                    "type": "object",
                    "description": "條件為真時執行的操作"
                },
                "if_false": {
                    "type": "object",
                    "description": "條件為假時執行的操作"
                }
            },
            required=["condition", "if_true"],
            category=ToolCategory.COMPUTATION
        )


# ============================================================================
# 第四部分：工具實現示例
# ============================================================================

class ToolImplementation:
    """工具實現示例"""

    @staticmethod
    async def implement_string_transform(text: str, operation: str) -> str:
        """
        實現字符串轉換工具

        這展示瞭如何實現一個簡單的工具函數
        """
        # 1. 參數驗證
        if not text:
            raise ValueError("文本不能為空")

        valid_operations = ["uppercase", "lowercase", "reverse", "capitalize"]
        if operation not in valid_operations:
            raise ValueError(f"無效的操作: {operation}")

        # 2. 執行操作
        if operation == "uppercase":
            result = text.upper()
        elif operation == "lowercase":
            result = text.lower()
        elif operation == "reverse":
            result = text[::-1]
        elif operation == "capitalize":
            result = text.capitalize()
        else:
            result = text

        # 3. 返回結果
        return result

    @staticmethod
    async def implement_calculation(expression: str, precision: int = 2) -> float:
        """
        實現計算工具

        展示如何處理更複雜的邏輯
        """
        # 1. 安全檢查
        # 禁止危險的操作
        dangerous_keywords = ["import", "exec", "eval", "__"]
        for keyword in dangerous_keywords:
            if keyword in expression:
                raise ValueError(f"表達式包含禁止的關鍵字: {keyword}")

        # 2. 執行計算（安全的方式）
        try:
            # 只允許數學運算
            allowed_chars = set("0123456789+-*/().^ ")
            if not all(c in allowed_chars for c in expression):
                raise ValueError("表達式包含無效字符")

            # 使用安全的評估方式
            result = eval(expression, {"__builtins__": {}}, {})

            # 3. 格式化結果
            return round(float(result), precision)

        except Exception as e:
            raise ValueError(f"計算錯誤: {e}")


# ============================================================================
# 第五部分：工具設計最佳實踐
# ============================================================================

class ToolDesignGuidelines:
    """工具設計指南"""

    BEST_PRACTICES = {
        "命名": [
            "使用描述性的動詞+名詞組合（如 read_file, execute_query）",
            "使用 snake_case 命名風格",
            "避免縮寫，除非是廣為人知的（如 HTTP, SQL）"
        ],

        "描述": [
            "清晰說明工具的用途和功能",
            "包含使用場景和限制",
            "提供簡單的使用示例"
        ],

        "參數設計": [
            "只包含必要的參數",
            "為可選參數提供合理的默認值",
            "使用 enum 限制可選值範圍",
            "添加詳細的參數描述"
        ],

        "錯誤處理": [
            "驗證所有輸入參數",
            "提供有幫助的錯誤消息",
            "使用適當的異常類型",
            "記錄錯誤詳情用於調試"
        ],

        "性能": [
            "設置合理的超時時間",
            "對大量數據進行分頁或流式處理",
            "緩存頻繁訪問的數據",
            "避免阻塞操作"
        ],

        "安全": [
            "驗證和清理用戶輸入",
            "限制資源訪問範圍",
            "避免執行任意代碼",
            "記錄敏感操作"
        ]
    }

    @staticmethod
    def validate_tool_definition(tool: ToolDefinition) -> List[str]:
        """驗證工具定義，返回問題列表"""
        issues = []

        # 檢查名稱
        if not tool.name:
            issues.append("工具名稱不能為空")
        elif not tool.name.islower():
            issues.append("工具名稱應使用小寫")

        # 檢查描述
        if not tool.description:
            issues.append("缺少工具描述")
        elif len(tool.description) < 10:
            issues.append("工具描述過於簡短")

        # 檢查輸入模式
        if "properties" not in tool.input_schema:
            issues.append("缺少參數定義")

        return issues


# ============================================================================
# 主程式示例
# ============================================================================

def main():
    """主程式：展示工具定義"""

    print("=" * 70)
    print("MCP 工具定義示例")
    print("=" * 70)

    # 1. 基本工具
    print("\n【示例 1：基本工具模式】")
    patterns = CommonToolPatterns()

    string_tool = patterns.string_operation_tool()
    print(f"工具名稱: {string_tool.name}")
    print(f"描述: {string_tool.description}")
    print(f"參數: {json.dumps(string_tool.input_schema, indent=2, ensure_ascii=False)}")

    # 2. 各類工具示例
    print("\n【示例 2：各類工具】")
    tools = [
        patterns.file_operation_tool(),
        patterns.database_query_tool(),
        patterns.api_request_tool(),
        patterns.calculation_tool()
    ]

    for tool in tools:
        print(f"  • {tool.name} ({tool.category.value})")
        print(f"    {tool.description}")

    # 3. 進階工具
    print("\n【示例 3：進階工具模式】")
    advanced = AdvancedToolPatterns()

    batch_tool = advanced.batch_operation_tool()
    print(f"工具: {batch_tool.name}")
    print(f"類別: {batch_tool.category.value}")

    # 4. 工具驗證
    print("\n【示例 4：工具定義驗證】")
    issues = ToolDesignGuidelines.validate_tool_definition(string_tool)
    if issues:
        print("發現問題:")
        for issue in issues:
            print(f"  ✗ {issue}")
    else:
        print("✓ 工具定義符合規範")

    # 5. 最佳實踐
    print("\n【示例 5：設計最佳實踐】")
    for category, practices in ToolDesignGuidelines.BEST_PRACTICES.items():
        print(f"\n{category}:")
        for practice in practices:
            print(f"  • {practice}")

    print("\n" + "=" * 70)
    print("下一步：查看 06_資源管理.py 學習 MCP 資源")
    print("=" * 70)


if __name__ == "__main__":
    main()

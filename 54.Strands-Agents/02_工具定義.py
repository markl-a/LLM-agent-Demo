"""
Strands Agents 工具定義與註冊示例

這個示例展示了如何在 Strands Agents 中定義和使用工具（Tools）：
1. 使用裝飾器定義工具
2. 複雜參數類型和驗證
3. 工具的元數據和描述
4. 動態工具註冊和管理
5. 工具執行的錯誤處理
6. 非同步工具的實現
7. 工具組合和鏈式調用

工具是 Agent 與外部系統交互的主要方式，
良好的工具定義是構建強大 Agent 的關鍵。

作者: Strands Agents Team
日期: 2025-01
"""

import os
import sys
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import inspect
from functools import wraps

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# 工具參數定義
# ============================================================================

class ParameterType(Enum):
    """參數類型枚舉"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"


@dataclass
class ToolParameter:
    """
    工具參數定義

    用於描述工具函數的參數規格，包括類型、描述、是否必需等。
    這些資訊會被傳遞給 LLM，幫助它正確調用工具。

    Attributes:
        name: 參數名稱
        type: 參數類型
        description: 參數描述
        required: 是否必需
        default: 預設值
        enum: 可選值列表
        min_value: 最小值（數值類型）
        max_value: 最大值（數值類型）
        pattern: 正則表達式模式（字符串類型）
    """
    name: str
    type: ParameterType
    description: str
    required: bool = True
    default: Any = None
    enum: Optional[List[Any]] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    pattern: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        result = {
            "name": self.name,
            "type": self.type.value,
            "description": self.description,
            "required": self.required
        }

        if self.default is not None:
            result["default"] = self.default
        if self.enum is not None:
            result["enum"] = self.enum
        if self.min_value is not None:
            result["min_value"] = self.min_value
        if self.max_value is not None:
            result["max_value"] = self.max_value
        if self.pattern is not None:
            result["pattern"] = self.pattern

        return result


@dataclass
class ToolDefinition:
    """
    工具定義

    完整描述一個工具的元數據和執行邏輯。

    Attributes:
        name: 工具名稱
        description: 工具描述
        function: 執行函數
        parameters: 參數列表
        returns: 返回值描述
        examples: 使用示例
        category: 工具分類
        version: 版本號
    """
    name: str
    description: str
    function: Callable
    parameters: List[ToolParameter] = field(default_factory=list)
    returns: str = "執行結果"
    examples: List[str] = field(default_factory=list)
    category: str = "general"
    version: str = "1.0.0"

    def to_schema(self) -> Dict[str, Any]:
        """
        轉換為 OpenAI Function Calling 格式的 schema

        Returns:
            Dict: 工具的 JSON Schema 定義
        """
        properties = {}
        required = []

        for param in self.parameters:
            properties[param.name] = {
                "type": param.type.value,
                "description": param.description
            }

            if param.enum:
                properties[param.name]["enum"] = param.enum
            if param.min_value is not None:
                properties[param.name]["minimum"] = param.min_value
            if param.max_value is not None:
                properties[param.name]["maximum"] = param.max_value
            if param.pattern:
                properties[param.name]["pattern"] = param.pattern

            if param.required:
                required.append(param.name)

        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }


# ============================================================================
# 工具裝飾器
# ============================================================================

class ToolRegistry:
    """
    工具註冊表

    管理所有註冊的工具，提供註冊、查詢和調用功能。
    """
    def __init__(self):
        self.tools: Dict[str, ToolDefinition] = {}

    def register(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        parameters: Optional[List[ToolParameter]] = None,
        category: str = "general"
    ):
        """
        工具註冊裝飾器

        使用方式:
        @registry.register(
            name="my_tool",
            description="我的工具",
            parameters=[...]
        )
        def my_tool(arg1, arg2):
            ...

        Args:
            name: 工具名稱，默認使用函數名
            description: 工具描述，默認使用函數的 docstring
            parameters: 參數定義列表
            category: 工具分類
        """
        def decorator(func: Callable) -> Callable:
            tool_name = name or func.__name__
            tool_description = description or func.__doc__ or "無描述"

            # 從函數簽名自動推斷參數（如果未提供）
            tool_parameters = parameters or self._infer_parameters(func)

            # 創建工具定義
            tool_def = ToolDefinition(
                name=tool_name,
                description=tool_description,
                function=func,
                parameters=tool_parameters,
                category=category
            )

            # 註冊工具
            self.tools[tool_name] = tool_def
            logger.info(f"註冊工具: {tool_name} (分類: {category})")

            @wraps(func)
            def wrapper(*args, **kwargs):
                logger.debug(f"執行工具: {tool_name}")
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    logger.error(f"工具執行錯誤 {tool_name}: {str(e)}")
                    raise

            return wrapper

        return decorator

    def _infer_parameters(self, func: Callable) -> List[ToolParameter]:
        """
        從函數簽名推斷參數定義

        Args:
            func: 函數對象

        Returns:
            List[ToolParameter]: 參數列表
        """
        parameters = []
        sig = inspect.signature(func)

        for param_name, param in sig.parameters.items():
            # 跳過 self 和 cls
            if param_name in ('self', 'cls'):
                continue

            # 推斷類型
            param_type = ParameterType.STRING  # 默認
            if param.annotation != inspect.Parameter.empty:
                if param.annotation == int:
                    param_type = ParameterType.INTEGER
                elif param.annotation == float:
                    param_type = ParameterType.FLOAT
                elif param.annotation == bool:
                    param_type = ParameterType.BOOLEAN
                elif param.annotation == list:
                    param_type = ParameterType.ARRAY
                elif param.annotation == dict:
                    param_type = ParameterType.OBJECT

            # 判斷是否必需
            required = param.default == inspect.Parameter.empty

            parameters.append(ToolParameter(
                name=param_name,
                type=param_type,
                description=f"參數 {param_name}",
                required=required,
                default=None if required else param.default
            ))

        return parameters

    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        """獲取工具定義"""
        return self.tools.get(name)

    def list_tools(self, category: Optional[str] = None) -> List[str]:
        """列出所有工具名稱"""
        if category:
            return [
                name for name, tool in self.tools.items()
                if tool.category == category
            ]
        return list(self.tools.keys())

    def get_schemas(self) -> List[Dict[str, Any]]:
        """獲取所有工具的 schema"""
        return [tool.to_schema() for tool in self.tools.values()]


# 創建全局註冊表
registry = ToolRegistry()


# ============================================================================
# 示例工具定義
# ============================================================================

@registry.register(
    name="search_database",
    description="在資料庫中搜索資料",
    parameters=[
        ToolParameter(
            name="query",
            type=ParameterType.STRING,
            description="搜索查詢字符串",
            required=True
        ),
        ToolParameter(
            name="limit",
            type=ParameterType.INTEGER,
            description="返回結果的最大數量",
            required=False,
            default=10,
            min_value=1,
            max_value=100
        ),
        ToolParameter(
            name="filters",
            type=ParameterType.OBJECT,
            description="篩選條件",
            required=False
        )
    ],
    category="database"
)
def search_database(
    query: str,
    limit: int = 10,
    filters: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    搜索資料庫

    這是一個模擬的資料庫搜索工具，展示如何定義複雜參數。

    Args:
        query: 搜索查詢
        limit: 結果數量限制
        filters: 篩選條件

    Returns:
        Dict: 搜索結果
    """
    logger.info(f"搜索資料庫: query={query}, limit={limit}, filters={filters}")

    # 模擬搜索結果
    results = [
        {"id": i, "title": f"結果 {i}", "content": f"包含 '{query}' 的內容"}
        for i in range(1, min(limit + 1, 6))
    ]

    return {
        "query": query,
        "total": len(results),
        "results": results,
        "filters_applied": filters or {}
    }


@registry.register(
    name="send_email",
    description="發送電子郵件",
    parameters=[
        ToolParameter(
            name="to",
            type=ParameterType.STRING,
            description="收件人郵箱地址",
            required=True,
            pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$'
        ),
        ToolParameter(
            name="subject",
            type=ParameterType.STRING,
            description="郵件主題",
            required=True
        ),
        ToolParameter(
            name="body",
            type=ParameterType.STRING,
            description="郵件內容",
            required=True
        ),
        ToolParameter(
            name="priority",
            type=ParameterType.STRING,
            description="優先級",
            required=False,
            default="normal",
            enum=["low", "normal", "high", "urgent"]
        )
    ],
    category="communication"
)
def send_email(
    to: str,
    subject: str,
    body: str,
    priority: str = "normal"
) -> Dict[str, Any]:
    """
    發送郵件

    Args:
        to: 收件人
        subject: 主題
        body: 內容
        priority: 優先級

    Returns:
        Dict: 發送結果
    """
    logger.info(f"發送郵件到 {to}: {subject}")

    # 模擬郵件發送
    return {
        "status": "sent",
        "to": to,
        "subject": subject,
        "message_id": f"msg_{datetime.now().timestamp()}",
        "priority": priority
    }


@registry.register(
    name="analyze_sentiment",
    description="分析文本情感傾向",
    parameters=[
        ToolParameter(
            name="text",
            type=ParameterType.STRING,
            description="要分析的文本",
            required=True
        ),
        ToolParameter(
            name="language",
            type=ParameterType.STRING,
            description="文本語言",
            required=False,
            default="zh",
            enum=["zh", "en", "ja", "ko"]
        )
    ],
    category="nlp"
)
def analyze_sentiment(text: str, language: str = "zh") -> Dict[str, Any]:
    """
    情感分析

    分析文本的情感傾向（正面、負面、中性）。

    Args:
        text: 輸入文本
        language: 語言代碼

    Returns:
        Dict: 分析結果
    """
    logger.info(f"分析情感: {text[:50]}...")

    # 簡單的關鍵字情感分析（實際應使用 ML 模型）
    positive_words = ["好", "棒", "優秀", "喜歡", "滿意", "高興"]
    negative_words = ["壞", "差", "糟糕", "討厭", "失望", "難過"]

    positive_count = sum(1 for word in positive_words if word in text)
    negative_count = sum(1 for word in negative_words if word in text)

    if positive_count > negative_count:
        sentiment = "positive"
        score = 0.7 + (positive_count * 0.1)
    elif negative_count > positive_count:
        sentiment = "negative"
        score = 0.3 - (negative_count * 0.1)
    else:
        sentiment = "neutral"
        score = 0.5

    return {
        "text": text,
        "language": language,
        "sentiment": sentiment,
        "score": max(0.0, min(1.0, score)),
        "details": {
            "positive_indicators": positive_count,
            "negative_indicators": negative_count
        }
    }


# ============================================================================
# 非同步工具
# ============================================================================

class AsyncToolRegistry:
    """
    非同步工具註冊表

    支援非同步工具的註冊和執行
    """
    def __init__(self):
        self.tools: Dict[str, ToolDefinition] = {}

    def register_async(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        parameters: Optional[List[ToolParameter]] = None
    ):
        """非同步工具註冊裝飾器"""
        def decorator(func: Callable) -> Callable:
            tool_name = name or func.__name__
            tool_description = description or func.__doc__ or "無描述"

            tool_def = ToolDefinition(
                name=tool_name,
                description=tool_description,
                function=func,
                parameters=parameters or []
            )

            self.tools[tool_name] = tool_def
            logger.info(f"註冊非同步工具: {tool_name}")

            @wraps(func)
            async def wrapper(*args, **kwargs):
                logger.debug(f"執行非同步工具: {tool_name}")
                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception as e:
                    logger.error(f"非同步工具執行錯誤 {tool_name}: {str(e)}")
                    raise

            return wrapper

        return decorator


# 創建非同步註冊表
async_registry = AsyncToolRegistry()


@async_registry.register_async(
    name="fetch_url",
    description="非同步獲取 URL 內容",
    parameters=[
        ToolParameter(
            name="url",
            type=ParameterType.STRING,
            description="要獲取的 URL",
            required=True
        ),
        ToolParameter(
            name="timeout",
            type=ParameterType.INTEGER,
            description="超時時間（秒）",
            required=False,
            default=30
        )
    ]
)
async def fetch_url(url: str, timeout: int = 30) -> Dict[str, Any]:
    """
    非同步 URL 獲取

    Args:
        url: URL 地址
        timeout: 超時時間

    Returns:
        Dict: 響應內容
    """
    logger.info(f"獲取 URL: {url}")

    # 模擬非同步 HTTP 請求
    await asyncio.sleep(0.5)  # 模擬網絡延遲

    return {
        "url": url,
        "status": 200,
        "content": f"這是 {url} 的內容",
        "headers": {
            "content-type": "text/html",
            "content-length": "1234"
        }
    }


# ============================================================================
# 工具執行器
# ============================================================================

class ToolExecutor:
    """
    工具執行器

    負責驗證參數並執行工具
    """
    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def execute(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Any:
        """
        執行工具

        Args:
            tool_name: 工具名稱
            arguments: 參數字典

        Returns:
            Any: 執行結果

        Raises:
            ValueError: 工具不存在或參數無效
        """
        # 獲取工具定義
        tool = self.registry.get_tool(tool_name)
        if not tool:
            raise ValueError(f"工具不存在: {tool_name}")

        # 驗證參數
        validated_args = self._validate_arguments(tool, arguments)

        # 執行工具
        logger.info(f"執行工具: {tool_name}")
        result = tool.function(**validated_args)

        return result

    def _validate_arguments(
        self,
        tool: ToolDefinition,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        驗證和處理參數

        Args:
            tool: 工具定義
            arguments: 輸入參數

        Returns:
            Dict: 驗證後的參數

        Raises:
            ValueError: 參數驗證失敗
        """
        validated = {}

        for param in tool.parameters:
            value = arguments.get(param.name)

            # 檢查必需參數
            if param.required and value is None:
                raise ValueError(f"缺少必需參數: {param.name}")

            # 使用預設值
            if value is None and param.default is not None:
                value = param.default

            # 類型驗證和轉換
            if value is not None:
                # 枚舉驗證
                if param.enum and value not in param.enum:
                    raise ValueError(
                        f"參數 {param.name} 的值必須是 {param.enum} 之一"
                    )

                # 數值範圍驗證
                if param.type in (ParameterType.INTEGER, ParameterType.FLOAT):
                    if param.min_value is not None and value < param.min_value:
                        raise ValueError(
                            f"參數 {param.name} 不能小於 {param.min_value}"
                        )
                    if param.max_value is not None and value > param.max_value:
                        raise ValueError(
                            f"參數 {param.name} 不能大於 {param.max_value}"
                        )

                validated[param.name] = value

        return validated


# ============================================================================
# 示例和測試
# ============================================================================

def demonstrate_tool_registration():
    """演示工具註冊"""
    print("\n" + "="*60)
    print("示例 1: 工具註冊和元數據")
    print("="*60 + "\n")

    # 列出所有註冊的工具
    tools = registry.list_tools()
    print(f"已註冊的工具數量: {len(tools)}")
    print(f"工具列表: {', '.join(tools)}\n")

    # 顯示工具詳情
    for tool_name in tools:
        tool = registry.get_tool(tool_name)
        print(f"工具: {tool.name}")
        print(f"  描述: {tool.description}")
        print(f"  分類: {tool.category}")
        print(f"  參數數量: {len(tool.parameters)}")
        print()


def demonstrate_tool_execution():
    """演示工具執行"""
    print("\n" + "="*60)
    print("示例 2: 工具執行")
    print("="*60 + "\n")

    executor = ToolExecutor(registry)

    # 測試資料庫搜索
    print("執行資料庫搜索:")
    result = executor.execute("search_database", {
        "query": "Strands Agents",
        "limit": 5
    })
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # 測試郵件發送
    print("\n執行郵件發送:")
    result = executor.execute("send_email", {
        "to": "user@example.com",
        "subject": "測試郵件",
        "body": "這是一封測試郵件",
        "priority": "high"
    })
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # 測試情感分析
    print("\n執行情感分析:")
    result = executor.execute("analyze_sentiment", {
        "text": "這個產品真的很棒，我非常喜歡！"
    })
    print(json.dumps(result, indent=2, ensure_ascii=False))


def demonstrate_parameter_validation():
    """演示參數驗證"""
    print("\n" + "="*60)
    print("示例 3: 參數驗證")
    print("="*60 + "\n")

    executor = ToolExecutor(registry)

    # 測試缺少必需參數
    print("測試缺少必需參數:")
    try:
        executor.execute("search_database", {})
    except ValueError as e:
        print(f"錯誤（預期）: {e}\n")

    # 測試參數範圍驗證
    print("測試參數範圍:")
    try:
        executor.execute("search_database", {
            "query": "test",
            "limit": 200  # 超過最大值 100
        })
    except ValueError as e:
        print(f"錯誤（預期）: {e}\n")

    # 測試枚舉驗證
    print("測試枚舉驗證:")
    try:
        executor.execute("send_email", {
            "to": "test@example.com",
            "subject": "測試",
            "body": "內容",
            "priority": "invalid"  # 無效的優先級
        })
    except ValueError as e:
        print(f"錯誤（預期）: {e}\n")


def demonstrate_tool_schemas():
    """演示工具 Schema 生成"""
    print("\n" + "="*60)
    print("示例 4: 工具 Schema")
    print("="*60 + "\n")

    schemas = registry.get_schemas()
    print(f"生成了 {len(schemas)} 個工具的 Schema\n")

    # 顯示第一個工具的 schema
    if schemas:
        print("示例 Schema (search_database):")
        print(json.dumps(schemas[0], indent=2, ensure_ascii=False))


async def demonstrate_async_tools():
    """演示非同步工具"""
    print("\n" + "="*60)
    print("示例 5: 非同步工具")
    print("="*60 + "\n")

    print("執行非同步 URL 獲取:")
    result = await fetch_url("https://example.com", timeout=10)
    print(json.dumps(result, indent=2, ensure_ascii=False))


def main():
    """主函數"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "工具定義與註冊示例" + " "*20 + "║")
    print("╚" + "="*58 + "╝")

    try:
        # 執行同步示例
        demonstrate_tool_registration()
        demonstrate_tool_execution()
        demonstrate_parameter_validation()
        demonstrate_tool_schemas()

        # 執行非同步示例
        asyncio.run(demonstrate_async_tools())

        print("\n" + "="*60)
        print("所有示例執行完成！")
        print("="*60)

    except Exception as e:
        logger.error(f"執行錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

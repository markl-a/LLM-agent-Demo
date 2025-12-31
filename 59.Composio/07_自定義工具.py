#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Composio 自定義工具範例
=======================

本範例展示如何創建和使用自定義工具，包括：
1. 基礎自定義工具創建
2. 工具參數定義和驗證
3. 錯誤處理和異常管理
4. 工具測試和除錯
5. 工具註冊和部署
6. 與 LangChain/CrewAI 整合
7. 實際應用場景

自定義工具讓您可以擴展 Composio 的功能，整合任何 API 或服務。

作者: Composio 團隊
日期: 2025-01-01
"""

import os
import sys
import json
import time
import requests
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 導入 Composio SDK
try:
    from composio import action, Composio
    from composio.client.exceptions import ComposioException
except ImportError as e:
    print("錯誤：請先安裝 Composio SDK")
    print("執行: pip install composio-core")
    sys.exit(1)


# ============================================================================
# 基礎自定義工具範例
# ============================================================================

class WeatherParams(BaseModel):
    """天氣查詢參數"""
    city: str = Field(..., description="城市名稱")
    units: str = Field(
        default="metric",
        description="溫度單位（metric=攝氏，imperial=華氏）"
    )

    @validator('city')
    def validate_city(cls, v):
        """驗證城市名稱"""
        if not v or len(v.strip()) == 0:
            raise ValueError("城市名稱不能為空")
        return v.strip()


@action(toolname="weather_tool")
def get_weather(params: WeatherParams) -> dict:
    """
    獲取城市天氣資訊

    這是一個簡單的自定義工具示例，展示如何：
    1. 定義參數模型
    2. 實現工具邏輯
    3. 返回結構化結果

    Args:
        params: 天氣查詢參數

    Returns:
        天氣資訊字典
    """
    print(f"\n查詢 {params.city} 的天氣...")

    # 模擬 API 調用（實際使用時替換為真實 API）
    # 例如：OpenWeatherMap API
    weather_data = {
        "city": params.city,
        "temperature": 25,
        "humidity": 65,
        "conditions": "晴天",
        "wind_speed": 10,
        "units": params.units,
        "timestamp": datetime.now().isoformat()
    }

    return {
        "success": True,
        "data": weather_data,
        "message": f"成功獲取 {params.city} 的天氣資訊"
    }


# ============================================================================
# 進階自定義工具 - 數據庫操作
# ============================================================================

class DatabaseQueryParams(BaseModel):
    """數據庫查詢參數"""
    query: str = Field(..., description="SQL 查詢語句")
    database: str = Field(default="default", description="數據庫名稱")
    limit: int = Field(default=100, description="結果數量限制")

    @validator('query')
    def validate_query(cls, v):
        """驗證查詢語句"""
        # 基本的 SQL 注入防護
        dangerous_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER']
        query_upper = v.upper()

        for keyword in dangerous_keywords:
            if keyword in query_upper:
                raise ValueError(f"查詢包含危險的關鍵字: {keyword}")

        return v


@action(toolname="database_tool")
def execute_database_query(params: DatabaseQueryParams) -> dict:
    """
    執行數據庫查詢

    安全地執行只讀數據庫查詢

    Args:
        params: 查詢參數

    Returns:
        查詢結果
    """
    print(f"\n執行數據庫查詢: {params.database}")
    print(f"查詢語句: {params.query[:100]}...")

    # 模擬數據庫查詢
    # 實際使用時連接真實數據庫
    mock_results = [
        {"id": 1, "name": "用戶A", "email": "usera@example.com"},
        {"id": 2, "name": "用戶B", "email": "userb@example.com"},
        {"id": 3, "name": "用戶C", "email": "userc@example.com"}
    ]

    return {
        "success": True,
        "data": {
            "rows": mock_results[:params.limit],
            "count": len(mock_results),
            "database": params.database
        },
        "message": "查詢執行成功"
    }


# ============================================================================
# API 整合工具
# ============================================================================

class APIRequestParams(BaseModel):
    """API 請求參數"""
    url: str = Field(..., description="API URL")
    method: str = Field(default="GET", description="HTTP 方法")
    headers: Optional[Dict[str, str]] = Field(
        default=None,
        description="請求標頭"
    )
    body: Optional[Dict[str, Any]] = Field(
        default=None,
        description="請求主體"
    )
    timeout: int = Field(default=30, description="超時時間（秒）")

    @validator('method')
    def validate_method(cls, v):
        """驗證 HTTP 方法"""
        allowed_methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
        v_upper = v.upper()

        if v_upper not in allowed_methods:
            raise ValueError(f"不支援的 HTTP 方法: {v}")

        return v_upper

    @validator('url')
    def validate_url(cls, v):
        """驗證 URL"""
        if not v.startswith(('http://', 'https://')):
            raise ValueError("URL 必須以 http:// 或 https:// 開頭")
        return v


@action(toolname="api_request_tool")
def make_api_request(params: APIRequestParams) -> dict:
    """
    執行 HTTP API 請求

    這是一個通用的 API 請求工具，可以調用任何 RESTful API

    Args:
        params: API 請求參數

    Returns:
        API 響應
    """
    print(f"\n執行 API 請求: {params.method} {params.url}")

    try:
        # 準備請求參數
        request_kwargs = {
            'method': params.method,
            'url': params.url,
            'timeout': params.timeout
        }

        if params.headers:
            request_kwargs['headers'] = params.headers

        if params.body and params.method in ['POST', 'PUT', 'PATCH']:
            request_kwargs['json'] = params.body

        # 執行請求
        response = requests.request(**request_kwargs)

        # 處理響應
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            response_data = response.text

        return {
            "success": response.ok,
            "status_code": response.status_code,
            "data": response_data,
            "headers": dict(response.headers),
            "message": f"請求完成，狀態碼: {response.status_code}"
        }

    except requests.Timeout:
        return {
            "success": False,
            "error": "請求超時",
            "message": f"請求在 {params.timeout} 秒後超時"
        }
    except requests.RequestException as e:
        return {
            "success": False,
            "error": str(e),
            "message": "請求失敗"
        }


# ============================================================================
# 文件處理工具
# ============================================================================

class FileOperationParams(BaseModel):
    """文件操作參數"""
    operation: str = Field(..., description="操作類型（read/write/delete）")
    file_path: str = Field(..., description="文件路徑")
    content: Optional[str] = Field(default=None, description="寫入的內容")
    encoding: str = Field(default="utf-8", description="文件編碼")

    @validator('operation')
    def validate_operation(cls, v):
        """驗證操作類型"""
        allowed_ops = ['read', 'write', 'delete', 'append']
        if v.lower() not in allowed_ops:
            raise ValueError(f"不支援的操作: {v}")
        return v.lower()


@action(toolname="file_tool")
def handle_file_operation(params: FileOperationParams) -> dict:
    """
    處理文件操作

    支援讀取、寫入和刪除文件

    Args:
        params: 文件操作參數

    Returns:
        操作結果
    """
    print(f"\n執行文件操作: {params.operation} - {params.file_path}")

    try:
        if params.operation == 'read':
            # 讀取文件
            with open(params.file_path, 'r', encoding=params.encoding) as f:
                content = f.read()

            return {
                "success": True,
                "data": {
                    "content": content,
                    "size": len(content),
                    "path": params.file_path
                },
                "message": "文件讀取成功"
            }

        elif params.operation == 'write':
            # 寫入文件
            if params.content is None:
                raise ValueError("寫入操作需要提供內容")

            with open(params.file_path, 'w', encoding=params.encoding) as f:
                f.write(params.content)

            return {
                "success": True,
                "data": {
                    "path": params.file_path,
                    "size": len(params.content)
                },
                "message": "文件寫入成功"
            }

        elif params.operation == 'append':
            # 追加到文件
            if params.content is None:
                raise ValueError("追加操作需要提供內容")

            with open(params.file_path, 'a', encoding=params.encoding) as f:
                f.write(params.content)

            return {
                "success": True,
                "data": {"path": params.file_path},
                "message": "內容追加成功"
            }

        elif params.operation == 'delete':
            # 刪除文件
            if os.path.exists(params.file_path):
                os.remove(params.file_path)
                return {
                    "success": True,
                    "message": "文件刪除成功"
                }
            else:
                return {
                    "success": False,
                    "error": "文件不存在",
                    "message": f"文件 {params.file_path} 不存在"
                }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"文件操作失敗: {e}"
        }


# ============================================================================
# 數據轉換工具
# ============================================================================

class DataTransformParams(BaseModel):
    """數據轉換參數"""
    data: Any = Field(..., description="要轉換的數據")
    from_format: str = Field(..., description="源格式（json/csv/xml）")
    to_format: str = Field(..., description="目標格式（json/csv/xml）")

    @validator('from_format', 'to_format')
    def validate_format(cls, v):
        """驗證格式"""
        allowed_formats = ['json', 'csv', 'xml', 'yaml']
        if v.lower() not in allowed_formats:
            raise ValueError(f"不支援的格式: {v}")
        return v.lower()


@action(toolname="data_transform_tool")
def transform_data(params: DataTransformParams) -> dict:
    """
    轉換數據格式

    支援在不同數據格式之間轉換

    Args:
        params: 轉換參數

    Returns:
        轉換結果
    """
    print(f"\n轉換數據: {params.from_format} -> {params.to_format}")

    try:
        # 簡化的轉換邏輯（實際實現需要更完整）
        if params.from_format == 'json' and params.to_format == 'json':
            # JSON to JSON（驗證）
            if isinstance(params.data, str):
                data = json.loads(params.data)
            else:
                data = params.data

            result = json.dumps(data, indent=2, ensure_ascii=False)

        elif params.from_format == 'json' and params.to_format == 'csv':
            # JSON to CSV
            if isinstance(params.data, str):
                data = json.loads(params.data)
            else:
                data = params.data

            # 簡單的 CSV 轉換
            if isinstance(data, list) and len(data) > 0:
                headers = list(data[0].keys())
                csv_lines = [','.join(headers)]

                for row in data:
                    csv_lines.append(','.join(str(row.get(h, '')) for h in headers))

                result = '\n'.join(csv_lines)
            else:
                result = ""

        else:
            # 其他轉換...
            result = str(params.data)

        return {
            "success": True,
            "data": {
                "result": result,
                "from_format": params.from_format,
                "to_format": params.to_format
            },
            "message": "數據轉換成功"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"數據轉換失敗: {e}"
        }


# ============================================================================
# 工具測試和使用範例
# ============================================================================

class CustomToolManager:
    """
    自定義工具管理器

    管理和測試自定義工具
    """

    def __init__(self):
        """初始化工具管理器"""
        print("=" * 70)
        print("初始化自定義工具管理器")
        print("=" * 70)

        self.tools = {
            "weather": get_weather,
            "database": execute_database_query,
            "api_request": make_api_request,
            "file": handle_file_operation,
            "data_transform": transform_data
        }

    def list_tools(self):
        """列出所有自定義工具"""
        print("\n" + "=" * 70)
        print("可用的自定義工具")
        print("=" * 70)

        for i, (name, func) in enumerate(self.tools.items(), 1):
            print(f"\n{i}. {name}")
            print(f"   函數: {func.__name__}")
            print(f"   描述: {func.__doc__.strip().split(chr(10))[0] if func.__doc__ else '無描述'}")

    def test_tool(self, tool_name: str, params: dict):
        """
        測試工具

        Args:
            tool_name: 工具名稱
            params: 測試參數
        """
        print("\n" + "=" * 70)
        print(f"測試工具: {tool_name}")
        print("=" * 70)

        if tool_name not in self.tools:
            print(f"✗ 工具 '{tool_name}' 不存在")
            return

        tool_func = self.tools[tool_name]

        try:
            # 執行工具
            print(f"\n參數: {json.dumps(params, indent=2, ensure_ascii=False)}")
            result = tool_func(params)

            print(f"\n結果:")
            print(json.dumps(result, indent=2, ensure_ascii=False))

        except Exception as e:
            print(f"\n✗ 測試失敗: {e}")


def demo_tool_creation():
    """
    演示工具創建過程
    """
    print("\n" + "=" * 80)
    print("自定義工具創建指南")
    print("=" * 80)

    steps = [
        ("1. 定義參數模型", """
使用 Pydantic BaseModel 定義工具參數：

class MyToolParams(BaseModel):
    param1: str = Field(..., description="參數描述")
    param2: int = Field(default=10, description="可選參數")

    @validator('param1')
    def validate_param1(cls, v):
        # 參數驗證邏輯
        return v
        """),

        ("2. 實現工具函數", """
使用 @action 裝飾器標記工具函數：

@action(toolname="my_tool")
def my_tool(params: MyToolParams) -> dict:
    '''工具描述'''
    # 實現工具邏輯
    result = do_something(params)

    return {
        "success": True,
        "data": result,
        "message": "操作成功"
    }
        """),

        ("3. 錯誤處理", """
實施完善的錯誤處理：

try:
    # 工具邏輯
    result = risky_operation()
    return {"success": True, "data": result}
except SpecificException as e:
    return {"success": False, "error": str(e)}
        """),

        ("4. 測試工具", """
在集成前充分測試：

# 單元測試
def test_my_tool():
    params = MyToolParams(param1="test")
    result = my_tool(params)
    assert result["success"] == True
        """),

        ("5. 文檔編寫", """
提供清晰的文檔：

- 工具用途和功能
- 參數說明
- 返回值格式
- 使用範例
- 錯誤處理
        """)
    ]

    for step, code in steps:
        print(f"\n{step}")
        print("-" * 80)
        print(code)


def demo_best_practices():
    """
    演示最佳實踐
    """
    print("\n" + "=" * 80)
    print("自定義工具最佳實踐")
    print("=" * 80)

    practices = [
        ("1. 參數驗證", [
            "使用 Pydantic 模型驗證參數",
            "提供清晰的錯誤訊息",
            "實施安全檢查（如 SQL 注入防護）",
            "設置合理的預設值"
        ]),
        ("2. 錯誤處理", [
            "捕獲所有可能的異常",
            "返回統一的錯誤格式",
            "記錄錯誤詳情",
            "提供恢復建議"
        ]),
        ("3. 性能優化", [
            "實施超時機制",
            "使用快取減少重複調用",
            "批次處理大量數據",
            "異步執行長時間操作"
        ]),
        ("4. 安全性", [
            "驗證輸入數據",
            "限制文件系統訪問",
            "使用環境變數存儲敏感資訊",
            "實施速率限制"
        ]),
        ("5. 可維護性", [
            "編寫清晰的文檔",
            "使用有意義的命名",
            "保持函數簡潔",
            "添加日誌記錄"
        ])
    ]

    for title, items in practices:
        print(f"\n{title}")
        print("-" * 80)
        for item in items:
            print(f"  • {item}")


def main():
    """
    主函數
    """
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║              Composio 自定義工具範例                             ║
    ║                                                                  ║
    ║              擴展 Composio 功能的無限可能                        ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)

    # 創建工具管理器
    manager = CustomToolManager()

    # 列出工具
    manager.list_tools()

    # 演示工具創建
    demo_tool_creation()

    # 演示最佳實踐
    demo_best_practices()

    # 測試範例
    print("\n" + "=" * 80)
    print("工具測試範例")
    print("=" * 80)

    print("\n範例 1: 天氣查詢工具")
    print("-" * 80)
    print("""
manager.test_tool("weather", {
    "city": "台北",
    "units": "metric"
})
    """)

    print("\n範例 2: API 請求工具")
    print("-" * 80)
    print("""
manager.test_tool("api_request", {
    "url": "https://api.example.com/data",
    "method": "GET"
})
    """)

    print("\n" + "=" * 80)
    print("下一步:")
    print("  1. 實現您自己的自定義工具")
    print("  2. 測試工具功能")
    print("  3. 整合到 LangChain 或 CrewAI")
    print("  4. 部署到生產環境")
    print("=" * 80)


if __name__ == "__main__":
    main()

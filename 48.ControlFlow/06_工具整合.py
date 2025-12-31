"""
ControlFlow 工具整合詳解
========================

本文件深入探討 ControlFlow 中的工具開發和整合,包括:
1. 基本工具定義
2. 工具參數和返回值
3. 工具文檔和元數據
4. 異步工具
5. 工具鏈和組合
6. 外部 API 整合
7. 工具錯誤處理

作者: ControlFlow 示例團隊
日期: 2025
"""

import os
import json
import time
import asyncio
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from pathlib import Path
import controlflow as cf
from controlflow import Agent, Task, Flow, tool
from pydantic import BaseModel, Field
from dotenv import load_dotenv


# ========== 配置 ==========

load_dotenv()


# ========== 數據模型 ==========

class SearchResult(BaseModel):
    """搜索結果模型"""
    title: str
    url: str
    snippet: str
    relevance: float = Field(ge=0, le=1)


class CalculationResult(BaseModel):
    """計算結果模型"""
    expression: str
    result: float
    steps: List[str] = Field(default_factory=list)


class FileInfo(BaseModel):
    """文件信息模型"""
    path: str
    size: int
    modified: datetime
    file_type: str


# ========== 基本工具定義 ==========

class BasicTools:
    """
    基本工具定義示例

    演示如何創建基本的工具函數
    """

    @staticmethod
    @cf.tool
    def add_numbers(a: float, b: float) -> float:
        """
        加法工具

        將兩個數字相加

        Args:
            a: 第一個數字
            b: 第二個數字

        Returns:
            float: 兩數之和
        """
        print(f"   🧮 計算: {a} + {b}")
        result = a + b
        print(f"   結果: {result}")
        return result

    @staticmethod
    @cf.tool
    def multiply_numbers(a: float, b: float) -> float:
        """
        乘法工具

        將兩個數字相乘

        Args:
            a: 第一個數字
            b: 第二個數字

        Returns:
            float: 兩數之積
        """
        print(f"   🧮 計算: {a} × {b}")
        result = a * b
        print(f"   結果: {result}")
        return result

    @staticmethod
    @cf.tool
    def get_current_time() -> str:
        """
        獲取當前時間

        Returns:
            str: 當前時間的 ISO 格式字符串
        """
        current_time = datetime.now()
        print(f"   🕒 當前時間: {current_time}")
        return current_time.isoformat()

    @staticmethod
    @cf.tool
    def format_text(text: str, style: str = "uppercase") -> str:
        """
        格式化文本

        Args:
            text: 要格式化的文本
            style: 格式化風格 (uppercase, lowercase, title)

        Returns:
            str: 格式化後的文本
        """
        print(f"   ✏️ 格式化文本: {style}")

        if style == "uppercase":
            return text.upper()
        elif style == "lowercase":
            return text.lower()
        elif style == "title":
            return text.title()
        else:
            return text

    @staticmethod
    def demonstrate_basic_tools():
        """演示基本工具的使用"""
        print("🔧 演示基本工具...\n")

        # 創建帶工具的 Agent
        agent = Agent(
            name="工具使用者",
            instructions="使用提供的工具完成任務",
            tools=[
                BasicTools.add_numbers,
                BasicTools.multiply_numbers,
                BasicTools.get_current_time,
                BasicTools.format_text
            ],
            model="gpt-4"
        )

        # 創建使用工具的任務
        task = Task(
            objective="使用工具計算 15 + 27,並獲取當前時間",
            agent=agent
        )

        print(f"   任務: {task.objective}")
        print(f"   可用工具: {len(agent.tools)} 個\n")


# ========== 複雜工具 ==========

class AdvancedTools:
    """
    高級工具示例

    演示更複雜的工具實現
    """

    @staticmethod
    @cf.tool
    def search_documents(
        query: str,
        max_results: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        搜索文檔

        在文檔庫中搜索相關內容

        Args:
            query: 搜索查詢
            max_results: 最大結果數量
            filters: 可選的過濾條件

        Returns:
            List[SearchResult]: 搜索結果列表
        """
        print(f"   🔍 搜索: '{query}'")
        print(f"   最大結果: {max_results}")
        if filters:
            print(f"   過濾條件: {filters}")

        # 模擬搜索結果
        results = [
            SearchResult(
                title=f"文檔 {i+1}: {query}",
                url=f"https://example.com/doc{i+1}",
                snippet=f"關於 {query} 的相關內容...",
                relevance=1.0 - (i * 0.15)
            )
            for i in range(min(max_results, 3))
        ]

        print(f"   找到 {len(results)} 個結果")
        return results

    @staticmethod
    @cf.tool
    def analyze_data(
        data: List[float],
        operations: List[str] = ["mean", "median", "std"]
    ) -> Dict[str, float]:
        """
        分析數據

        對數據執行統計分析

        Args:
            data: 數據列表
            operations: 要執行的操作列表

        Returns:
            Dict[str, float]: 分析結果
        """
        print(f"   📊 分析 {len(data)} 個數據點")
        print(f"   操作: {', '.join(operations)}")

        import statistics

        results = {}

        if "mean" in operations:
            results["mean"] = statistics.mean(data)

        if "median" in operations:
            results["median"] = statistics.median(data)

        if "std" in operations:
            results["std"] = statistics.stdev(data) if len(data) > 1 else 0

        if "min" in operations:
            results["min"] = min(data)

        if "max" in operations:
            results["max"] = max(data)

        print(f"   結果: {results}")
        return results

    @staticmethod
    @cf.tool
    def process_json(
        json_str: str,
        operation: str = "validate"
    ) -> Union[bool, Dict[str, Any], str]:
        """
        處理 JSON 數據

        Args:
            json_str: JSON 字符串
            operation: 操作類型 (validate, parse, prettify)

        Returns:
            Union[bool, Dict, str]: 處理結果
        """
        print(f"   📄 JSON 操作: {operation}")

        try:
            data = json.loads(json_str)

            if operation == "validate":
                print("   ✅ JSON 有效")
                return True

            elif operation == "parse":
                print("   ✅ JSON 解析成功")
                return data

            elif operation == "prettify":
                pretty = json.dumps(data, indent=2, ensure_ascii=False)
                print("   ✅ JSON 格式化完成")
                return pretty

            else:
                return data

        except json.JSONDecodeError as e:
            print(f"   ❌ JSON 無效: {str(e)}")
            return False

    @staticmethod
    @cf.tool
    def file_operations(
        operation: str,
        path: str,
        content: Optional[str] = None
    ) -> Union[str, FileInfo, bool]:
        """
        文件操作工具

        Args:
            operation: 操作類型 (read, write, info, exists)
            path: 文件路徑
            content: 文件內容(寫入時需要)

        Returns:
            Union[str, FileInfo, bool]: 操作結果
        """
        print(f"   📁 文件操作: {operation}")
        print(f"   路徑: {path}")

        file_path = Path(path)

        if operation == "exists":
            exists = file_path.exists()
            print(f"   存在: {exists}")
            return exists

        elif operation == "read":
            if file_path.exists():
                content = file_path.read_text(encoding='utf-8')
                print(f"   ✅ 讀取成功 ({len(content)} 字符)")
                return content
            else:
                print("   ❌ 文件不存在")
                return ""

        elif operation == "write":
            if content is not None:
                file_path.write_text(content, encoding='utf-8')
                print(f"   ✅ 寫入成功 ({len(content)} 字符)")
                return True
            else:
                print("   ❌ 未提供內容")
                return False

        elif operation == "info":
            if file_path.exists():
                stat = file_path.stat()
                info = FileInfo(
                    path=str(file_path),
                    size=stat.st_size,
                    modified=datetime.fromtimestamp(stat.st_mtime),
                    file_type=file_path.suffix
                )
                print(f"   ✅ 信息獲取成功")
                return info
            else:
                print("   ❌ 文件不存在")
                return None

        return False


# ========== 異步工具 ==========

class AsyncTools:
    """
    異步工具示例

    演示異步工具的實現
    """

    @staticmethod
    @cf.tool
    async def async_fetch_data(url: str, timeout: int = 30) -> Dict[str, Any]:
        """
        異步獲取數據

        Args:
            url: 數據源 URL
            timeout: 超時時間(秒)

        Returns:
            Dict[str, Any]: 獲取的數據
        """
        print(f"   🌐 異步獲取: {url}")
        print(f"   超時設置: {timeout}秒")

        # 模擬異步請求
        await asyncio.sleep(0.5)

        return {
            "url": url,
            "data": "示例數據",
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }

    @staticmethod
    @cf.tool
    async def async_process_batch(
        items: List[str],
        delay: float = 0.1
    ) -> List[Dict[str, Any]]:
        """
        異步批處理

        Args:
            items: 要處理的項目列表
            delay: 每個項目的處理延遲

        Returns:
            List[Dict[str, Any]]: 處理結果列表
        """
        print(f"   ⚡ 異步批處理 {len(items)} 個項目")

        results = []

        for i, item in enumerate(items):
            print(f"      處理項目 {i+1}/{len(items)}: {item}")
            await asyncio.sleep(delay)

            results.append({
                "item": item,
                "processed": True,
                "timestamp": datetime.now().isoformat()
            })

        print(f"   ✅ 批處理完成")
        return results


# ========== 工具鏈 ==========

class ToolChains:
    """
    工具鏈示例

    演示如何組合多個工具
    """

    @staticmethod
    @cf.tool
    def extract_keywords(text: str, max_keywords: int = 5) -> List[str]:
        """
        提取關鍵詞

        Args:
            text: 文本內容
            max_keywords: 最大關鍵詞數量

        Returns:
            List[str]: 關鍵詞列表
        """
        print(f"   🔑 提取關鍵詞 (最多 {max_keywords} 個)")

        # 簡單的關鍵詞提取(實際應用中應使用 NLP 庫)
        words = text.lower().split()
        # 移除常見停用詞
        stop_words = {"的", "是", "在", "和", "了", "有", "我", "你"}
        keywords = [w for w in words if w not in stop_words]

        # 返回最常見的詞
        from collections import Counter
        common = Counter(keywords).most_common(max_keywords)
        result = [word for word, count in common]

        print(f"   關鍵詞: {', '.join(result)}")
        return result

    @staticmethod
    @cf.tool
    def summarize_text(text: str, max_length: int = 100) -> str:
        """
        文本摘要

        Args:
            text: 要摘要的文本
            max_length: 最大長度

        Returns:
            str: 摘要文本
        """
        print(f"   📝 生成摘要 (最大 {max_length} 字)")

        # 簡單的摘要(實際應用中應使用專業庫)
        summary = text[:max_length]
        if len(text) > max_length:
            summary += "..."

        print(f"   摘要長度: {len(summary)} 字")
        return summary

    @staticmethod
    @cf.tool
    def translate_text(text: str, target_lang: str = "en") -> str:
        """
        翻譯文本

        Args:
            text: 要翻譯的文本
            target_lang: 目標語言

        Returns:
            str: 翻譯後的文本
        """
        print(f"   🌍 翻譯到: {target_lang}")

        # 模擬翻譯
        return f"[Translated to {target_lang}] {text}"

    @staticmethod
    @cf.flow
    def text_processing_chain(text: str):
        """
        文本處理鏈

        組合多個工具處理文本

        Args:
            text: 輸入文本
        """
        print("🔗 執行文本處理鏈...\n")

        # 創建帶工具鏈的 Agent
        agent = Agent(
            name="文本處理專家",
            instructions="""
            你負責處理文本,可以使用以下工具:
            1. extract_keywords - 提取關鍵詞
            2. summarize_text - 生成摘要
            3. translate_text - 翻譯文本

            按順序使用工具處理文本。
            """,
            tools=[
                ToolChains.extract_keywords,
                ToolChains.summarize_text,
                ToolChains.translate_text
            ],
            model="gpt-4"
        )

        # 步驟 1: 提取關鍵詞
        print("📍 步驟 1: 提取關鍵詞")
        keywords_task = Task(
            objective="提取文本關鍵詞",
            agent=agent,
            context={"text": text}
        )
        keywords = keywords_task.run()
        print(f"關鍵詞: {keywords}\n")

        # 步驟 2: 生成摘要
        print("📍 步驟 2: 生成摘要")
        summary_task = Task(
            objective="生成文本摘要",
            agent=agent,
            context={"text": text}
        )
        summary = summary_task.run()
        print(f"摘要: {summary}\n")

        # 步驟 3: 翻譯
        print("📍 步驟 3: 翻譯摘要")
        translate_task = Task(
            objective="翻譯摘要到英文",
            agent=agent,
            context={"text": summary}
        )
        translation = translate_task.run()
        print(f"翻譯: {translation}\n")

        print("✅ 文本處理鏈完成!")

        return {
            "keywords": keywords,
            "summary": summary,
            "translation": translation
        }


# ========== 外部 API 整合 ==========

class ExternalAPITools:
    """
    外部 API 整合示例

    演示如何整合外部 API 作為工具
    """

    @staticmethod
    @cf.tool
    def weather_api(city: str) -> Dict[str, Any]:
        """
        天氣 API 工具

        獲取城市天氣信息

        Args:
            city: 城市名稱

        Returns:
            Dict[str, Any]: 天氣信息
        """
        print(f"   🌤️ 查詢天氣: {city}")

        # 模擬 API 調用
        weather_data = {
            "city": city,
            "temperature": 25,
            "condition": "晴朗",
            "humidity": 60,
            "wind_speed": 15,
            "timestamp": datetime.now().isoformat()
        }

        print(f"   溫度: {weather_data['temperature']}°C")
        print(f"   天氣: {weather_data['condition']}")

        return weather_data

    @staticmethod
    @cf.tool
    def database_query(
        table: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        數據庫查詢工具

        Args:
            table: 表名
            filters: 查詢過濾條件
            limit: 結果數量限制

        Returns:
            List[Dict[str, Any]]: 查詢結果
        """
        print(f"   🗄️ 查詢表: {table}")
        print(f"   過濾: {filters}")
        print(f"   限制: {limit} 條")

        # 模擬數據庫查詢
        results = [
            {
                "id": i + 1,
                "data": f"Record {i + 1}",
                "timestamp": datetime.now().isoformat()
            }
            for i in range(min(limit, 3))
        ]

        print(f"   ✅ 返回 {len(results)} 條記錄")
        return results

    @staticmethod
    @cf.tool
    def send_notification(
        recipient: str,
        message: str,
        priority: str = "normal"
    ) -> bool:
        """
        發送通知工具

        Args:
            recipient: 接收者
            message: 消息內容
            priority: 優先級

        Returns:
            bool: 是否發送成功
        """
        print(f"   📧 發送通知")
        print(f"   接收者: {recipient}")
        print(f"   優先級: {priority}")
        print(f"   消息: {message[:50]}...")

        # 模擬發送
        time.sleep(0.1)

        print("   ✅ 通知已發送")
        return True


# ========== 工具錯誤處理 ==========

class ToolErrorHandling:
    """
    工具錯誤處理示例

    演示如何在工具中處理錯誤
    """

    @staticmethod
    @cf.tool
    def safe_divide(a: float, b: float) -> Union[float, str]:
        """
        安全除法

        Args:
            a: 被除數
            b: 除數

        Returns:
            Union[float, str]: 計算結果或錯誤信息
        """
        print(f"   🧮 計算: {a} ÷ {b}")

        try:
            if b == 0:
                raise ZeroDivisionError("除數不能為零")

            result = a / b
            print(f"   結果: {result}")
            return result

        except ZeroDivisionError as e:
            error_msg = f"錯誤: {str(e)}"
            print(f"   ❌ {error_msg}")
            return error_msg

        except Exception as e:
            error_msg = f"未知錯誤: {str(e)}"
            print(f"   ❌ {error_msg}")
            return error_msg

    @staticmethod
    @cf.tool
    def validate_input(
        data: Dict[str, Any],
        required_fields: List[str]
    ) -> Dict[str, Any]:
        """
        驗證輸入

        Args:
            data: 輸入數據
            required_fields: 必需字段列表

        Returns:
            Dict[str, Any]: 驗證結果
        """
        print(f"   ✓ 驗證輸入")
        print(f"   必需字段: {', '.join(required_fields)}")

        errors = []
        warnings = []

        # 檢查必需字段
        for field in required_fields:
            if field not in data:
                errors.append(f"缺少必需字段: {field}")
            elif data[field] is None or data[field] == "":
                warnings.append(f"字段 {field} 為空")

        result = {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "checked_fields": len(required_fields)
        }

        if errors:
            print(f"   ❌ 驗證失敗: {len(errors)} 個錯誤")
        elif warnings:
            print(f"   ⚠️ 驗證通過但有 {len(warnings)} 個警告")
        else:
            print("   ✅ 驗證通過")

        return result

    @staticmethod
    @cf.tool
    def retry_operation(
        operation_name: str,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        重試操作

        Args:
            operation_name: 操作名稱
            max_retries: 最大重試次數

        Returns:
            Dict[str, Any]: 操作結果
        """
        print(f"   🔄 執行操作: {operation_name}")
        print(f"   最大重試: {max_retries}")

        for attempt in range(max_retries):
            try:
                print(f"      嘗試 {attempt + 1}/{max_retries}...")

                # 模擬可能失敗的操作
                import random
                if random.random() < 0.7:  # 70% 成功率
                    print(f"      ✅ 操作成功")
                    return {
                        "success": True,
                        "attempt": attempt + 1,
                        "operation": operation_name
                    }
                else:
                    raise Exception("操作失敗")

            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"      ⚠️ 失敗,重試...")
                    time.sleep(0.1)
                else:
                    print(f"      ❌ 所有嘗試都失敗")
                    return {
                        "success": False,
                        "attempts": max_retries,
                        "error": str(e)
                    }


# ========== 主程序 ==========

def main():
    """
    主程序入口

    演示各種工具整合方法
    """
    print("=" * 70)
    print("  ControlFlow 工具整合示例")
    print("=" * 70)
    print()

    try:
        # 1. 基本工具
        print("\n" + "=" * 70)
        print("1. 基本工具定義")
        print("=" * 70 + "\n")

        basic = BasicTools()
        basic.demonstrate_basic_tools()

        # 2. 高級工具
        print("\n" + "=" * 70)
        print("2. 高級工具")
        print("=" * 70 + "\n")

        advanced = AdvancedTools()
        # 演示搜索工具
        results = advanced.search_documents("Python 教程", max_results=3)
        print(f"✅ 搜索完成,找到 {len(results)} 個結果\n")

        # 演示數據分析工具
        data = [1.0, 2.5, 3.7, 4.2, 5.8]
        stats = advanced.analyze_data(data, ["mean", "median", "std"])
        print(f"✅ 數據分析完成\n")

        # 3. 工具鏈
        print("\n" + "=" * 70)
        print("3. 工具鏈")
        print("=" * 70 + "\n")

        # chains = ToolChains()
        # chains.text_processing_chain("這是一個示例文本...")
        print("✅ 工具鏈示例已定義\n")

        # 4. 外部 API
        print("\n" + "=" * 70)
        print("4. 外部 API 整合")
        print("=" * 70 + "\n")

        api_tools = ExternalAPITools()
        weather = api_tools.weather_api("台北")
        print(f"✅ 天氣查詢完成\n")

        db_results = api_tools.database_query("users", {"active": True}, 5)
        print(f"✅ 數據庫查詢完成\n")

        # 5. 錯誤處理
        print("\n" + "=" * 70)
        print("5. 工具錯誤處理")
        print("=" * 70 + "\n")

        error_handling = ToolErrorHandling()

        # 正常除法
        result1 = error_handling.safe_divide(10, 2)
        print()

        # 除以零
        result2 = error_handling.safe_divide(10, 0)
        print()

        # 輸入驗證
        test_data = {"name": "測試", "email": "test@example.com"}
        validation = error_handling.validate_input(
            test_data,
            ["name", "email", "phone"]
        )
        print()

        print("\n" + "=" * 70)
        print("演示完成")
        print("=" * 70)
        print("\n✅ 所有工具整合示例已成功展示!")
        print("\n💡 工具開發要點:")
        print("   - 清晰文檔: 提供詳細的函數文檔")
        print("   - 類型註解: 使用類型提示明確參數和返回值")
        print("   - 錯誤處理: 優雅處理異常情況")
        print("   - 工具鏈: 組合工具完成複雜任務")
        print("   - API 整合: 連接外部服務擴展能力")
        print("\n💡 下一步:")
        print("   - 查看 07_狀態管理.py 學習狀態管理")
        print("   - 查看 08_錯誤處理.py 學習錯誤處理")
        print()

    except Exception as e:
        print(f"\n❌ 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

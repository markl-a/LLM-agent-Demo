"""
SuperAGI 自定義工具開發示例

這個示例展示了如何:
1. 創建自定義工具
2. 工具參數驗證
3. 工具錯誤處理
4. 工具測試
5. 工具註冊和使用

學習如何擴展 SuperAGI 的工具生態系統。
"""

import os
import json
import time
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from datetime import datetime
from pydantic import BaseModel, Field, validator


# ==================== 工具基類和輸入模型 ====================

class ToolInput(BaseModel):
    """工具輸入基類"""
    pass


class BaseTool(ABC):
    """工具基類"""

    name: str = "base_tool"
    description: str = "Base tool description"
    args_schema: type[ToolInput] = ToolInput

    def __init__(self):
        self.execution_count = 0
        self.total_cost = 0.0
        self.errors = []

    @abstractmethod
    def _execute(self, **kwargs) -> Dict[str, Any]:
        """執行工具邏輯（需要子類實現）"""
        pass

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        執行工具（帶驗證和錯誤處理）

        返回:
            執行結果
        """
        try:
            # 驗證輸入
            validated_input = self.args_schema(**kwargs)

            # 執行工具
            start_time = time.time()
            result = self._execute(**kwargs)
            execution_time = time.time() - start_time

            # 更新統計
            self.execution_count += 1
            if "cost" in result:
                self.total_cost += result["cost"]

            # 添加元數據
            result["execution_time"] = execution_time
            result["tool_name"] = self.name

            return result

        except Exception as e:
            self.errors.append({
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "kwargs": kwargs
            })

            return {
                "success": False,
                "error": str(e),
                "tool_name": self.name
            }

    def get_stats(self) -> Dict:
        """獲取工具統計"""
        return {
            "name": self.name,
            "executions": self.execution_count,
            "total_cost": self.total_cost,
            "error_count": len(self.errors),
            "success_rate": (
                (self.execution_count - len(self.errors)) / self.execution_count
                if self.execution_count > 0 else 0
            )
        }


# ==================== 示例 1: 簡單的自定義工具 ====================

class WeatherToolInput(ToolInput):
    """天氣工具輸入"""
    city: str = Field(..., description="城市名稱", min_length=1)
    units: str = Field("celsius", description="溫度單位 (celsius/fahrenheit)")

    @validator("units")
    def validate_units(cls, v):
        if v not in ["celsius", "fahrenheit"]:
            raise ValueError("units 必須是 celsius 或 fahrenheit")
        return v


class WeatherTool(BaseTool):
    """
    天氣查詢工具

    功能: 查詢指定城市的天氣信息
    """

    name = "WeatherTool"
    description = "查詢城市天氣信息"
    args_schema = WeatherToolInput

    def _execute(self, city: str, units: str = "celsius") -> Dict[str, Any]:
        """
        查詢天氣

        參數:
            city: 城市名稱
            units: 溫度單位

        返回:
            天氣信息
        """
        print(f"\n🌤️  查詢天氣: {city}")

        # 模擬 API 調用
        temperature = 25 if units == "celsius" else 77
        weather_data = {
            "city": city,
            "temperature": temperature,
            "units": units,
            "condition": "晴天",
            "humidity": 65,
            "wind_speed": 10
        }

        return {
            "success": True,
            "data": weather_data,
            "cost": 0.01
        }


# ==================== 示例 2: 帶複雜邏輯的工具 ====================

class SentimentAnalysisInput(ToolInput):
    """情感分析工具輸入"""
    text: str = Field(..., description="要分析的文本", min_length=1, max_length=5000)
    language: str = Field("auto", description="文本語言")
    detail_level: str = Field("basic", description="分析詳細程度 (basic/detailed)")


class SentimentAnalysisTool(BaseTool):
    """
    情感分析工具

    功能: 分析文本的情感傾向
    """

    name = "SentimentAnalysisTool"
    description = "分析文本情感傾向（正面/負面/中性）"
    args_schema = SentimentAnalysisInput

    def __init__(self):
        super().__init__()
        # 簡單的情感詞典
        self.positive_words = {"好", "棒", "優秀", "喜歡", "開心", "滿意"}
        self.negative_words = {"壞", "差", "糟糕", "討厭", "難過", "失望"}

    def _execute(
        self,
        text: str,
        language: str = "auto",
        detail_level: str = "basic"
    ) -> Dict[str, Any]:
        """
        執行情感分析

        參數:
            text: 要分析的文本
            language: 語言
            detail_level: 詳細程度

        返回:
            分析結果
        """
        print(f"\n😊 情感分析: {text[:50]}...")

        # 計算情感分數
        positive_count = sum(1 for word in self.positive_words if word in text)
        negative_count = sum(1 for word in self.negative_words if word in text)

        # 判斷情感
        if positive_count > negative_count:
            sentiment = "positive"
            score = 0.5 + (positive_count / (len(text) + 1)) * 0.5
        elif negative_count > positive_count:
            sentiment = "negative"
            score = 0.5 - (negative_count / (len(text) + 1)) * 0.5
        else:
            sentiment = "neutral"
            score = 0.5

        result = {
            "success": True,
            "sentiment": sentiment,
            "score": score,
            "confidence": abs(score - 0.5) * 2,
            "cost": 0.02
        }

        # 詳細分析
        if detail_level == "detailed":
            result["details"] = {
                "positive_indicators": positive_count,
                "negative_indicators": negative_count,
                "text_length": len(text),
                "language": language
            }

        return result


# ==================== 示例 3: 異步工具 ====================

class EmailToolInput(ToolInput):
    """郵件工具輸入"""
    to: str = Field(..., description="收件人郵箱")
    subject: str = Field(..., description="郵件主題")
    body: str = Field(..., description="郵件正文")
    attachments: Optional[List[str]] = Field(None, description="附件列表")

    @validator("to")
    def validate_email(cls, v):
        if "@" not in v:
            raise ValueError("無效的郵箱地址")
        return v


class EmailSenderTool(BaseTool):
    """
    郵件發送工具

    功能: 發送郵件
    """

    name = "EmailSenderTool"
    description = "發送郵件"
    args_schema = EmailToolInput

    def __init__(self):
        super().__init__()
        self.sent_emails = []

    def _execute(
        self,
        to: str,
        subject: str,
        body: str,
        attachments: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        發送郵件

        參數:
            to: 收件人
            subject: 主題
            body: 正文
            attachments: 附件

        返回:
            發送結果
        """
        print(f"\n📧 發送郵件到: {to}")
        print(f"   主題: {subject}")

        # 模擬發送過程
        time.sleep(0.5)

        email_id = f"email_{len(self.sent_emails) + 1}"

        email_record = {
            "id": email_id,
            "to": to,
            "subject": subject,
            "body": body,
            "attachments": attachments or [],
            "sent_at": datetime.now().isoformat(),
            "status": "sent"
        }

        self.sent_emails.append(email_record)

        return {
            "success": True,
            "email_id": email_id,
            "status": "sent",
            "cost": 0.005
        }

    def get_sent_emails(self) -> List[Dict]:
        """獲取已發送郵件列表"""
        return self.sent_emails


# ==================== 示例 4: 有狀態的工具 ====================

class DatabaseToolInput(ToolInput):
    """數據庫工具輸入"""
    operation: str = Field(..., description="操作類型 (query/insert/update/delete)")
    table: str = Field(..., description="表名")
    data: Optional[Dict] = Field(None, description="數據")
    conditions: Optional[Dict] = Field(None, description="查詢條件")


class DatabaseTool(BaseTool):
    """
    數據庫操作工具

    功能: 執行數據庫操作
    """

    name = "DatabaseTool"
    description = "執行數據庫 CRUD 操作"
    args_schema = DatabaseToolInput

    def __init__(self):
        super().__init__()
        # 模擬數據庫
        self.database = {
            "users": [
                {"id": 1, "name": "Alice", "age": 30},
                {"id": 2, "name": "Bob", "age": 25}
            ],
            "products": [
                {"id": 1, "name": "Product A", "price": 100},
                {"id": 2, "name": "Product B", "price": 200}
            ]
        }

    def _execute(
        self,
        operation: str,
        table: str,
        data: Optional[Dict] = None,
        conditions: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        執行數據庫操作

        參數:
            operation: 操作類型
            table: 表名
            data: 數據
            conditions: 條件

        返回:
            操作結果
        """
        print(f"\n🗄️  數據庫操作: {operation} on {table}")

        if table not in self.database:
            return {
                "success": False,
                "error": f"表 {table} 不存在",
                "cost": 0.001
            }

        if operation == "query":
            result = self._query(table, conditions)
        elif operation == "insert":
            result = self._insert(table, data)
        elif operation == "update":
            result = self._update(table, data, conditions)
        elif operation == "delete":
            result = self._delete(table, conditions)
        else:
            return {
                "success": False,
                "error": f"不支持的操作: {operation}",
                "cost": 0.001
            }

        result["cost"] = 0.01
        return result

    def _query(self, table: str, conditions: Optional[Dict]) -> Dict:
        """查詢數據"""
        records = self.database[table]

        if conditions:
            records = [
                r for r in records
                if all(r.get(k) == v for k, v in conditions.items())
            ]

        return {
            "success": True,
            "operation": "query",
            "results": records,
            "count": len(records)
        }

    def _insert(self, table: str, data: Dict) -> Dict:
        """插入數據"""
        if not data:
            return {"success": False, "error": "沒有數據"}

        new_id = max([r.get("id", 0) for r in self.database[table]]) + 1
        data["id"] = new_id

        self.database[table].append(data)

        return {
            "success": True,
            "operation": "insert",
            "inserted_id": new_id
        }

    def _update(self, table: str, data: Dict, conditions: Dict) -> Dict:
        """更新數據"""
        updated_count = 0

        for record in self.database[table]:
            if all(record.get(k) == v for k, v in conditions.items()):
                record.update(data)
                updated_count += 1

        return {
            "success": True,
            "operation": "update",
            "updated_count": updated_count
        }

    def _delete(self, table: str, conditions: Dict) -> Dict:
        """刪除數據"""
        original_count = len(self.database[table])

        self.database[table] = [
            r for r in self.database[table]
            if not all(r.get(k) == v for k, v in conditions.items())
        ]

        deleted_count = original_count - len(self.database[table])

        return {
            "success": True,
            "operation": "delete",
            "deleted_count": deleted_count
        }


# ==================== 示例 5: 組合工具 ====================

class ReportGeneratorInput(ToolInput):
    """報告生成器輸入"""
    title: str = Field(..., description="報告標題")
    data: Dict = Field(..., description="報告數據")
    format: str = Field("markdown", description="輸出格式 (markdown/html/pdf)")


class ReportGeneratorTool(BaseTool):
    """
    報告生成工具

    功能: 生成格式化報告
    """

    name = "ReportGeneratorTool"
    description = "生成格式化的報告文檔"
    args_schema = ReportGeneratorInput

    def _execute(
        self,
        title: str,
        data: Dict,
        format: str = "markdown"
    ) -> Dict[str, Any]:
        """
        生成報告

        參數:
            title: 報告標題
            data: 報告數據
            format: 輸出格式

        返回:
            生成的報告
        """
        print(f"\n📄 生成報告: {title}")

        if format == "markdown":
            report = self._generate_markdown(title, data)
        elif format == "html":
            report = self._generate_html(title, data)
        elif format == "pdf":
            report = self._generate_pdf(title, data)
        else:
            return {
                "success": False,
                "error": f"不支持的格式: {format}"
            }

        return {
            "success": True,
            "title": title,
            "format": format,
            "content": report,
            "size": len(report),
            "cost": 0.03
        }

    def _generate_markdown(self, title: str, data: Dict) -> str:
        """生成 Markdown 報告"""
        report = f"# {title}\n\n"
        report += f"生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        report += "## 數據概覽\n\n"

        for key, value in data.items():
            report += f"- **{key}**: {value}\n"

        report += "\n## 詳細分析\n\n"
        report += "（此處可添加詳細分析內容）\n"

        return report

    def _generate_html(self, title: str, data: Dict) -> str:
        """生成 HTML 報告"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <p>生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <table>
        <tr><th>項目</th><th>值</th></tr>
"""
        for key, value in data.items():
            html += f"        <tr><td>{key}</td><td>{value}</td></tr>\n"

        html += """
    </table>
</body>
</html>
"""
        return html

    def _generate_pdf(self, title: str, data: Dict) -> str:
        """生成 PDF 報告（模擬）"""
        return f"PDF報告: {title} (模擬生成)"


# ==================== 工具註冊系統 ====================

class ToolRegistry:
    """工具註冊表"""

    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool):
        """註冊工具"""
        self.tools[tool.name] = tool
        print(f"✅ 註冊工具: {tool.name} - {tool.description}")

    def get(self, name: str) -> Optional[BaseTool]:
        """獲取工具"""
        return self.tools.get(name)

    def list_all(self):
        """列出所有工具"""
        print("\n=== 已註冊工具 ===")
        for name, tool in self.tools.items():
            stats = tool.get_stats()
            print(f"\n📦 {name}")
            print(f"   描述: {tool.description}")
            print(f"   執行次數: {stats['executions']}")
            print(f"   成功率: {stats['success_rate']:.2%}")
            print(f"   總成本: ${stats['total_cost']:.4f}")


# ==================== 示例場景 ====================

def example_1_simple_tool():
    """示例 1: 簡單工具使用"""
    print("\n" + "=" * 60)
    print("示例 1: 簡單的自定義工具")
    print("=" * 60)

    # 創建工具
    weather_tool = WeatherTool()

    # 使用工具
    result1 = weather_tool.execute(city="台北", units="celsius")
    print(f"\n結果 1: {json.dumps(result1, ensure_ascii=False, indent=2)}")

    result2 = weather_tool.execute(city="紐約", units="fahrenheit")
    print(f"\n結果 2: {json.dumps(result2, ensure_ascii=False, indent=2)}")

    # 顯示統計
    print(f"\n工具統計: {weather_tool.get_stats()}")


def example_2_validation():
    """示例 2: 輸入驗證"""
    print("\n" + "=" * 60)
    print("示例 2: 輸入驗證示例")
    print("=" * 60)

    weather_tool = WeatherTool()

    # 正確的輸入
    print("\n✅ 正確輸入:")
    result = weather_tool.execute(city="東京", units="celsius")
    print(f"結果: {result.get('success')}")

    # 錯誤的單位
    print("\n❌ 錯誤輸入 (無效單位):")
    result = weather_tool.execute(city="東京", units="kelvin")
    print(f"錯誤: {result.get('error')}")


def example_3_sentiment_analysis():
    """示例 3: 情感分析工具"""
    print("\n" + "=" * 60)
    print("示例 3: 情感分析工具")
    print("=" * 60)

    tool = SentimentAnalysisTool()

    # 測試不同文本
    texts = [
        "這個產品真的很好用，我很喜歡！",
        "太糟糕了，完全不滿意。",
        "還可以，沒有特別的感覺。"
    ]

    for text in texts:
        result = tool.execute(text=text, detail_level="detailed")
        print(f"\n文本: {text}")
        print(f"情感: {result['sentiment']}")
        print(f"分數: {result['score']:.2f}")
        print(f"置信度: {result['confidence']:.2%}")


def example_4_database_operations():
    """示例 4: 數據庫操作"""
    print("\n" + "=" * 60)
    print("示例 4: 數據庫操作工具")
    print("=" * 60)

    db_tool = DatabaseTool()

    # 查詢
    print("\n1. 查詢所有用戶:")
    result = db_tool.execute(operation="query", table="users")
    print(f"找到 {result['count']} 個用戶")
    print(json.dumps(result['results'], ensure_ascii=False, indent=2))

    # 插入
    print("\n2. 插入新用戶:")
    result = db_tool.execute(
        operation="insert",
        table="users",
        data={"name": "Charlie", "age": 35}
    )
    print(f"插入成功，ID: {result['inserted_id']}")

    # 更新
    print("\n3. 更新用戶:")
    result = db_tool.execute(
        operation="update",
        table="users",
        data={"age": 26},
        conditions={"name": "Bob"}
    )
    print(f"更新了 {result['updated_count']} 條記錄")

    # 查詢驗證
    print("\n4. 驗證更新:")
    result = db_tool.execute(
        operation="query",
        table="users",
        conditions={"name": "Bob"}
    )
    print(json.dumps(result['results'], ensure_ascii=False, indent=2))


def example_5_report_generation():
    """示例 5: 報告生成"""
    print("\n" + "=" * 60)
    print("示例 5: 報告生成工具")
    print("=" * 60)

    tool = ReportGeneratorTool()

    # 準備數據
    data = {
        "總用戶數": 1000,
        "活躍用戶": 750,
        "新增用戶": 50,
        "收入": "$10,000"
    }

    # 生成 Markdown 報告
    print("\n生成 Markdown 報告:")
    result = tool.execute(
        title="月度運營報告",
        data=data,
        format="markdown"
    )
    print(result["content"])

    # 生成 HTML 報告
    print("\n生成 HTML 報告:")
    result = tool.execute(
        title="月度運營報告",
        data=data,
        format="html"
    )
    print(f"HTML 大小: {result['size']} 字節")


def example_6_tool_registry():
    """示例 6: 工具註冊系統"""
    print("\n" + "=" * 60)
    print("示例 6: 工具註冊和管理")
    print("=" * 60)

    # 創建註冊表
    registry = ToolRegistry()

    # 註冊所有工具
    registry.register(WeatherTool())
    registry.register(SentimentAnalysisTool())
    registry.register(EmailSenderTool())
    registry.register(DatabaseTool())
    registry.register(ReportGeneratorTool())

    # 使用註冊的工具
    print("\n使用註冊的工具:")

    weather = registry.get("WeatherTool")
    weather.execute(city="上海")

    sentiment = registry.get("SentimentAnalysisTool")
    sentiment.execute(text="這個工具很棒！")

    # 列出所有工具
    registry.list_all()


# ==================== 主函數 ====================

def main():
    """主函數"""
    print("\n" + "🛠️  " * 20)
    print("SuperAGI 自定義工具開發教程")
    print("🛠️  " * 20)

    try:
        # 示例 1: 簡單工具
        example_1_simple_tool()

        # 示例 2: 輸入驗證
        example_2_validation()

        # 示例 3: 情感分析
        example_3_sentiment_analysis()

        # 示例 4: 數據庫操作
        example_4_database_operations()

        # 示例 5: 報告生成
        example_5_report_generation()

        # 示例 6: 工具註冊
        example_6_tool_registry()

        print("\n" + "=" * 60)
        print("✅ 所有自定義工具示例執行完成！")
        print("=" * 60)

        print("""
        工具開發最佳實踐:

        1. 使用 Pydantic 驗證輸入
        2. 實現完善的錯誤處理
        3. 記錄執行統計
        4. 提供清晰的文檔
        5. 測試各種場景
        6. 控制執行成本
        """)

    except Exception as e:
        print(f"\n❌ 執行出錯: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

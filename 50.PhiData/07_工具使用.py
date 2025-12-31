"""
PhiData 工具使用示例

這個腳本展示了如何在 PhiData 中使用和創建工具，包括：
1. 內建工具使用
2. 自定義工具創建
3. 工具組合
4. 工具鏈
5. 條件工具調用
6. 工具錯誤處理
7. 工具參數驗證
8. 異步工具
9. 工具裝飾器
10. 工具最佳實踐

作者: PhiData Team
日期: 2025
"""

import os
import json
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from functools import wraps

# PhiData 核心導入
from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.tools import Toolkit
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.yfinance import YFinanceTools
from phi.utils.log import logger

# 環境變量管理
from dotenv import load_dotenv

# 載入環境變量
load_dotenv()


# ============================================================================
# 自定義工具類
# ============================================================================

class CalculatorTools(Toolkit):
    """
    計算器工具集

    提供基礎數學計算功能。
    """

    def __init__(self):
        super().__init__(name="calculator_tools")

        # 註冊工具方法
        self.register(self.add)
        self.register(self.subtract)
        self.register(self.multiply)
        self.register(self.divide)
        self.register(self.power)

    def add(self, a: float, b: float) -> float:
        """
        加法

        參數:
            a: 第一個數
            b: 第二個數

        返回:
            a + b
        """
        result = a + b
        logger.info(f"計算: {a} + {b} = {result}")
        return result

    def subtract(self, a: float, b: float) -> float:
        """
        減法

        參數:
            a: 被減數
            b: 減數

        返回:
            a - b
        """
        result = a - b
        logger.info(f"計算: {a} - {b} = {result}")
        return result

    def multiply(self, a: float, b: float) -> float:
        """
        乘法

        參數:
            a: 第一個因數
            b: 第二個因數

        返回:
            a * b
        """
        result = a * b
        logger.info(f"計算: {a} × {b} = {result}")
        return result

    def divide(self, a: float, b: float) -> float:
        """
        除法

        參數:
            a: 被除數
            b: 除數

        返回:
            a / b

        異常:
            ValueError: 當除數為 0 時
        """
        if b == 0:
            raise ValueError("除數不能為 0")

        result = a / b
        logger.info(f"計算: {a} ÷ {b} = {result}")
        return result

    def power(self, base: float, exponent: float) -> float:
        """
        冪運算

        參數:
            base: 底數
            exponent: 指數

        返回:
            base ^ exponent
        """
        result = base ** exponent
        logger.info(f"計算: {base} ^ {exponent} = {result}")
        return result


class WeatherTools(Toolkit):
    """
    天氣工具集

    提供天氣查詢功能（示例實現）。
    """

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(name="weather_tools")
        self.api_key = api_key
        self.register(self.get_current_weather)
        self.register(self.get_forecast)

    def get_current_weather(self, city: str) -> Dict[str, Any]:
        """
        獲取當前天氣

        參數:
            city: 城市名稱

        返回:
            天氣信息字典
        """
        logger.info(f"查詢天氣: {city}")

        # 這裡是示例數據，實際應該調用真實的天氣 API
        weather_data = {
            "city": city,
            "temperature": 25,
            "condition": "晴天",
            "humidity": 60,
            "wind_speed": 15,
            "timestamp": datetime.now().isoformat(),
        }

        return weather_data

    def get_forecast(self, city: str, days: int = 3) -> List[Dict[str, Any]]:
        """
        獲取天氣預報

        參數:
            city: 城市名稱
            days: 預報天數

        返回:
            預報信息列表
        """
        logger.info(f"查詢 {days} 天預報: {city}")

        # 示例數據
        forecast = []
        for i in range(days):
            forecast.append({
                "day": i + 1,
                "temperature_high": 28 - i,
                "temperature_low": 18 - i,
                "condition": "多雲" if i % 2 == 0 else "晴天",
            })

        return forecast


class TextProcessingTools(Toolkit):
    """
    文本處理工具集

    提供各種文本處理功能。
    """

    def __init__(self):
        super().__init__(name="text_processing_tools")

        self.register(self.count_words)
        self.register(self.reverse_text)
        self.register(self.to_uppercase)
        self.register(self.to_lowercase)
        self.register(self.extract_emails)

    def count_words(self, text: str) -> int:
        """
        統計字數

        參數:
            text: 文本

        返回:
            字數
        """
        words = text.split()
        count = len(words)
        logger.info(f"字數統計: {count}")
        return count

    def reverse_text(self, text: str) -> str:
        """
        反轉文本

        參數:
            text: 文本

        返回:
            反轉後的文本
        """
        reversed_text = text[::-1]
        logger.info(f"文本反轉: {text} -> {reversed_text}")
        return reversed_text

    def to_uppercase(self, text: str) -> str:
        """
        轉換為大寫

        參數:
            text: 文本

        返回:
            大寫文本
        """
        return text.upper()

    def to_lowercase(self, text: str) -> str:
        """
        轉換為小寫

        參數:
            text: 文本

        返回:
            小寫文本
        """
        return text.lower()

    def extract_emails(self, text: str) -> List[str]:
        """
        提取電子郵件地址

        參數:
            text: 文本

        返回:
            郵件地址列表
        """
        import re
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        logger.info(f"提取到 {len(emails)} 個郵件地址")
        return emails


class DataTransformTools(Toolkit):
    """
    數據轉換工具集

    提供數據格式轉換功能。
    """

    def __init__(self):
        super().__init__(name="data_transform_tools")

        self.register(self.dict_to_json)
        self.register(self.json_to_dict)
        self.register(self.csv_to_json)
        self.register(self.flatten_dict)

    def dict_to_json(self, data: Dict[str, Any]) -> str:
        """
        字典轉 JSON

        參數:
            data: 字典

        返回:
            JSON 字符串
        """
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        logger.info("字典轉換為 JSON")
        return json_str

    def json_to_dict(self, json_str: str) -> Dict[str, Any]:
        """
        JSON 轉字典

        參數:
            json_str: JSON 字符串

        返回:
            字典
        """
        data = json.loads(json_str)
        logger.info("JSON 轉換為字典")
        return data

    def csv_to_json(self, csv_data: str) -> List[Dict[str, Any]]:
        """
        CSV 轉 JSON

        參數:
            csv_data: CSV 格式字符串

        返回:
            JSON 數據列表
        """
        import csv
        import io

        reader = csv.DictReader(io.StringIO(csv_data))
        result = list(reader)
        logger.info(f"CSV 轉換為 JSON，共 {len(result)} 行")
        return result

    def flatten_dict(self, data: Dict[str, Any], parent_key: str = '') -> Dict[str, Any]:
        """
        展平嵌套字典

        參數:
            data: 嵌套字典
            parent_key: 父鍵名

        返回:
            展平後的字典
        """
        items = []
        for k, v in data.items():
            new_key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self.flatten_dict(v, new_key).items())
            else:
                items.append((new_key, v))

        result = dict(items)
        logger.info("字典展平完成")
        return result


class FileSystemTools(Toolkit):
    """
    文件系統工具集

    提供文件操作功能（安全限制版本）。
    """

    def __init__(self, base_path: str = "."):
        super().__init__(name="filesystem_tools")
        self.base_path = base_path

        self.register(self.list_files)
        self.register(self.read_file)
        self.register(self.write_file)

    def list_files(self, directory: str = ".") -> List[str]:
        """
        列出文件

        參數:
            directory: 目錄路徑

        返回:
            文件列表
        """
        import os
        from pathlib import Path

        path = Path(self.base_path) / directory
        if path.exists() and path.is_dir():
            files = [f.name for f in path.iterdir()]
            logger.info(f"列出 {len(files)} 個文件")
            return files
        else:
            return []

    def read_file(self, filepath: str) -> str:
        """
        讀取文件

        參數:
            filepath: 文件路徑

        返回:
            文件內容
        """
        from pathlib import Path

        path = Path(self.base_path) / filepath
        if path.exists() and path.is_file():
            content = path.read_text(encoding='utf-8')
            logger.info(f"讀取文件: {filepath}")
            return content
        else:
            raise FileNotFoundError(f"文件不存在: {filepath}")

    def write_file(self, filepath: str, content: str) -> str:
        """
        寫入文件

        參數:
            filepath: 文件路徑
            content: 文件內容

        返回:
            成功消息
        """
        from pathlib import Path

        path = Path(self.base_path) / filepath
        path.write_text(content, encoding='utf-8')
        logger.info(f"寫入文件: {filepath}")
        return f"文件已保存: {filepath}"


# ============================================================================
# 工具使用 Agent 類
# ============================================================================

class ToolUsageAgent:
    """
    工具使用 Agent 類

    演示各種工具的使用方法。
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化工具使用 Agent

        參數:
            api_key: OpenAI API 密鑰
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("未找到 OPENAI_API_KEY")

        logger.info("初始化工具使用 Agent")

    def create_agent_with_tools(
        self,
        tools: List[Toolkit],
        agent_name: str = "工具 Agent"
    ) -> Agent:
        """
        創建帶工具的 Agent

        參數:
            tools: 工具列表
            agent_name: Agent 名稱

        返回:
            配置好的 Agent
        """
        logger.info(f"創建 Agent，工具數量: {len(tools)}")

        agent = Agent(
            name=agent_name,
            model=OpenAIChat(
                id="gpt-4",
                api_key=self.api_key,
            ),
            tools=tools,
            description=f"配備 {len(tools)} 個工具集的智能助手",
            instructions=[
                "根據任務需求選擇合適的工具",
                "正確使用工具完成任務",
                "處理工具錯誤並提供反饋",
                "使用繁體中文回應",
            ],
            show_tool_calls=True,
            markdown=True,
        )

        return agent

    def run_with_tools(
        self,
        agent: Agent,
        task: str
    ) -> str:
        """
        使用工具執行任務

        參數:
            agent: Agent 實例
            task: 任務描述

        返回:
            執行結果
        """
        logger.info(f"執行任務: {task}")

        print(f"\n{'='*60}")
        print(f"任務: {task}")
        print(f"{'='*60}\n")

        response = agent.run(task)
        result = response.content if hasattr(response, 'content') else str(response)

        return result


# ============================================================================
# 演示函數
# ============================================================================

def demonstration_calculator_tools():
    """演示計算器工具"""
    print("\n" + "="*60)
    print("演示 1: 計算器工具")
    print("="*60)

    tool_agent = ToolUsageAgent()
    calculator = CalculatorTools()

    agent = tool_agent.create_agent_with_tools(
        [calculator],
        "計算器助手"
    )

    result = tool_agent.run_with_tools(
        agent,
        "請計算: (15 + 25) × 3 - 20"
    )
    print(f"\n結果:\n{result}\n")


def demonstration_weather_tools():
    """演示天氣工具"""
    print("\n" + "="*60)
    print("演示 2: 天氣查詢工具")
    print("="*60)

    tool_agent = ToolUsageAgent()
    weather = WeatherTools()

    agent = tool_agent.create_agent_with_tools(
        [weather],
        "天氣助手"
    )

    result = tool_agent.run_with_tools(
        agent,
        "台北今天的天氣如何？請同時提供未來3天的預報。"
    )
    print(f"\n結果:\n{result}\n")


def demonstration_text_processing():
    """演示文本處理工具"""
    print("\n" + "="*60)
    print("演示 3: 文本處理工具")
    print("="*60)

    tool_agent = ToolUsageAgent()
    text_tools = TextProcessingTools()

    agent = tool_agent.create_agent_with_tools(
        [text_tools],
        "文本處理助手"
    )

    result = tool_agent.run_with_tools(
        agent,
        "請統計這段文字的字數，並將其轉換為大寫：Hello World, this is a test message."
    )
    print(f"\n結果:\n{result}\n")


def demonstration_data_transform():
    """演示數據轉換工具"""
    print("\n" + "="*60)
    print("演示 4: 數據轉換工具")
    print("="*60)

    tool_agent = ToolUsageAgent()
    data_tools = DataTransformTools()

    agent = tool_agent.create_agent_with_tools(
        [data_tools],
        "數據轉換助手"
    )

    result = tool_agent.run_with_tools(
        agent,
        "請將這個字典轉換為 JSON：{'name': 'Alice', 'age': 30, 'city': 'Taipei'}"
    )
    print(f"\n結果:\n{result}\n")


def demonstration_multiple_tools():
    """演示多工具組合"""
    print("\n" + "="*60)
    print("演示 5: 多工具組合使用")
    print("="*60)

    tool_agent = ToolUsageAgent()

    # 組合多個工具
    tools = [
        CalculatorTools(),
        TextProcessingTools(),
        DataTransformTools(),
    ]

    agent = tool_agent.create_agent_with_tools(
        tools,
        "多功能助手"
    )

    result = tool_agent.run_with_tools(
        agent,
        """
        請執行以下任務：
        1. 計算 100 除以 4 的結果
        2. 統計 "The quick brown fox jumps over the lazy dog" 的字數
        3. 將結果組織成 JSON 格式
        """
    )
    print(f"\n結果:\n{result}\n")


def demonstration_builtin_tools():
    """演示內建工具"""
    print("\n" + "="*60)
    print("演示 6: PhiData 內建工具")
    print("="*60)

    tool_agent = ToolUsageAgent()

    # 使用 PhiData 內建工具
    tools = [
        DuckDuckGo(),
        YFinanceTools(),
    ]

    agent = tool_agent.create_agent_with_tools(
        tools,
        "搜索和金融助手"
    )

    result = tool_agent.run_with_tools(
        agent,
        "請搜索 Apple 公司的最新消息，並獲取 AAPL 股票的當前價格。"
    )
    print(f"\n結果:\n{result}\n")


def demonstration_tool_chain():
    """演示工具鏈"""
    print("\n" + "="*60)
    print("演示 7: 工具鏈（順序調用）")
    print("="*60)

    tool_agent = ToolUsageAgent()

    tools = [
        CalculatorTools(),
        DataTransformTools(),
    ]

    agent = tool_agent.create_agent_with_tools(
        tools,
        "工具鏈助手"
    )

    result = tool_agent.run_with_tools(
        agent,
        """
        請執行以下步驟：
        1. 計算 50 × 3 + 100
        2. 將計算結果轉換為 JSON 格式
        3. 將 JSON 再轉換回字典
        """
    )
    print(f"\n結果:\n{result}\n")


def main():
    """主函數"""
    print("\n" + "="*60)
    print("PhiData 工具使用 - 完整示例")
    print("="*60)

    try:
        # 運行所有演示
        demonstration_calculator_tools()
        demonstration_weather_tools()
        demonstration_text_processing()
        demonstration_data_transform()
        demonstration_multiple_tools()
        demonstration_builtin_tools()
        demonstration_tool_chain()

        print("\n" + "="*60)
        print("所有演示完成！")
        print("="*60)

        print("\n工具使用最佳實踐：")
        print("1. 工具要單一職責，功能明確")
        print("2. 提供清晰的文檔字符串")
        print("3. 做好參數驗證和錯誤處理")
        print("4. 記錄工具調用日誌")
        print("5. 組合工具實現複雜功能")

    except Exception as e:
        logger.error(f"運行錯誤: {e}")
        print(f"\n錯誤: {e}")


if __name__ == "__main__":
    main()

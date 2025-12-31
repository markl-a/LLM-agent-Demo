"""
Strands Agents 快速開始示例

這個示例展示了如何快速上手 Strands Agents 框架，包括：
1. 基本的 Agent 創建和配置
2. 簡單的工具定義和使用
3. 與 Agent 進行對話交互
4. 基礎的錯誤處理

Strands Agents 是 AWS 推出的企業級 AI Agent SDK，
已在 Amazon Q Developer 等服務中得到生產環境驗證。

作者: Strands Agents Team
日期: 2025-01
"""

import os
import sys
from typing import Dict, Any, List, Optional
import json
from datetime import datetime
import logging

# 配置日誌系統
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('strands_agent.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


def setup_environment():
    """
    設置環境變數和 AWS 憑證

    確保以下環境變數已設置：
    - AWS_ACCESS_KEY_ID: AWS 訪問密鑰 ID
    - AWS_SECRET_ACCESS_KEY: AWS 秘密訪問密鑰
    - AWS_DEFAULT_REGION: AWS 區域（如 us-east-1）
    """
    required_vars = [
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'AWS_DEFAULT_REGION'
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        logger.warning(f"缺少環境變數: {', '.join(missing_vars)}")
        logger.info("使用預設配置繼續執行...")

        # 設置預設值用於示例（實際使用時應配置真實憑證）
        os.environ.setdefault('AWS_DEFAULT_REGION', 'us-east-1')
    else:
        logger.info("環境變數配置完成")


def create_simple_tools():
    """
    創建簡單的工具函數集合

    工具（Tools）是 Agent 可以調用的函數，用於執行特定任務。
    每個工具都需要明確的描述和參數定義，以便 LLM 理解如何使用。

    Returns:
        List[callable]: 工具函數列表
    """

    def get_current_time() -> str:
        """
        獲取當前時間

        這是一個最簡單的工具示例，不需要任何參數。
        Agent 可以調用此工具來獲取當前的日期和時間。

        Returns:
            str: 格式化的當前時間字符串
        """
        now = datetime.now()
        return now.strftime("%Y年%m月%d日 %H:%M:%S")


    def calculate(expression: str) -> str:
        """
        執行數學計算

        接收一個數學表達式字符串，計算並返回結果。

        Args:
            expression: 數學表達式，如 "2 + 2" 或 "10 * 5"

        Returns:
            str: 計算結果

        注意：實際生產環境中應該使用更安全的表達式求值方法
        """
        try:
            # 使用 eval 進行計算（僅用於示例，生產環境應使用更安全的方法）
            result = eval(expression)
            return f"計算結果: {result}"
        except Exception as e:
            return f"計算錯誤: {str(e)}"


    def search_knowledge(query: str) -> str:
        """
        搜索知識庫

        模擬一個知識庫搜索功能。在實際應用中，
        這可能會連接到向量資料庫或搜索引擎。

        Args:
            query: 搜索查詢字符串

        Returns:
            str: 搜索結果
        """
        # 模擬知識庫數據
        knowledge_base = {
            "strands agents": "Strands Agents 是 AWS 推出的開源 AI Agent SDK，用於構建企業級智能代理。",
            "aws bedrock": "Amazon Bedrock 是一個完全託管的服務，提供來自領先 AI 公司的基礎模型。",
            "lambda": "AWS Lambda 是一個無服務器計算服務，讓您無需管理服務器即可運行代碼。"
        }

        # 簡單的關鍵字匹配
        query_lower = query.lower()
        for key, value in knowledge_base.items():
            if key in query_lower:
                return f"找到相關資訊: {value}"

        return f"未找到關於 '{query}' 的資訊"


    def get_weather(city: str) -> str:
        """
        獲取天氣資訊

        模擬天氣查詢功能。實際應用中會調用真實的天氣 API。

        Args:
            city: 城市名稱

        Returns:
            str: 天氣資訊
        """
        # 模擬天氣數據
        weather_data = {
            "台北": {"temperature": 25, "condition": "多雲", "humidity": 70},
            "台中": {"temperature": 28, "condition": "晴朗", "humidity": 65},
            "高雄": {"temperature": 30, "condition": "晴朗", "humidity": 75},
            "台南": {"temperature": 29, "condition": "多雲", "humidity": 68}
        }

        if city in weather_data:
            data = weather_data[city]
            return f"{city}的天氣: {data['condition']}, 溫度 {data['temperature']}°C, 濕度 {data['humidity']}%"
        else:
            return f"抱歉，暫無 {city} 的天氣資訊"

    # 返回所有工具函數
    return [get_current_time, calculate, search_knowledge, get_weather]


class SimpleAgent:
    """
    簡化版的 Agent 類別

    這是一個教學用的簡化實現，展示 Agent 的核心概念。
    實際使用時應該使用 Strands Agents 框架提供的完整 Agent 類別。

    Attributes:
        name: Agent 的名稱
        system_prompt: 系統提示詞，定義 Agent 的角色和行為
        tools: 可用的工具列表
        conversation_history: 對話歷史記錄
    """

    def __init__(
        self,
        name: str,
        system_prompt: str,
        tools: Optional[List[callable]] = None
    ):
        """
        初始化 Agent

        Args:
            name: Agent 名稱
            system_prompt: 系統提示詞
            tools: 工具函數列表
        """
        self.name = name
        self.system_prompt = system_prompt
        self.tools = tools or []
        self.conversation_history = []

        logger.info(f"創建 Agent: {name}")
        logger.info(f"可用工具數量: {len(self.tools)}")


    def add_tool(self, tool: callable):
        """
        添加工具到 Agent

        Args:
            tool: 工具函數
        """
        self.tools.append(tool)
        logger.info(f"添加工具: {tool.__name__}")


    def run(self, user_input: str) -> str:
        """
        執行 Agent 處理用戶輸入

        這是一個簡化的實現，展示基本流程：
        1. 接收用戶輸入
        2. 分析是否需要調用工具
        3. 調用相應的工具
        4. 生成響應

        Args:
            user_input: 用戶輸入的文本

        Returns:
            str: Agent 的響應
        """
        logger.info(f"接收用戶輸入: {user_input}")

        # 添加到對話歷史
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })

        # 簡單的工具匹配邏輯（實際實現會使用 LLM 來決定）
        response = self._process_with_tools(user_input)

        # 添加響應到歷史
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })

        return response


    def _process_with_tools(self, user_input: str) -> str:
        """
        處理用戶輸入並調用相應的工具

        這是一個簡化的實現，使用關鍵字匹配來決定調用哪個工具。
        實際的 Strands Agents 會使用 LLM 來智能決策。

        Args:
            user_input: 用戶輸入

        Returns:
            str: 處理結果
        """
        user_input_lower = user_input.lower()

        # 遍歷所有工具，嘗試匹配和調用
        for tool in self.tools:
            tool_name = tool.__name__

            # 簡單的關鍵字匹配
            if "時間" in user_input and tool_name == "get_current_time":
                result = tool()
                return f"根據您的請求，{result}"

            elif "計算" in user_input and tool_name == "calculate":
                # 嘗試提取計算表達式
                if "+" in user_input or "-" in user_input or "*" in user_input or "/" in user_input:
                    # 簡單提取（實際應使用更複雜的解析）
                    import re
                    match = re.search(r'[\d\+\-\*/\(\)\s]+', user_input)
                    if match:
                        expression = match.group(0).strip()
                        result = tool(expression)
                        return result

            elif "搜索" in user_input or "查詢" in user_input and tool_name == "search_knowledge":
                # 提取搜索關鍵字
                query = user_input.replace("搜索", "").replace("查詢", "").strip()
                result = tool(query)
                return result

            elif "天氣" in user_input and tool_name == "get_weather":
                # 提取城市名稱
                cities = ["台北", "台中", "高雄", "台南"]
                for city in cities:
                    if city in user_input:
                        result = tool(city)
                        return result

        # 如果沒有匹配的工具，返回默認響應
        return f"我是 {self.name}，收到您的訊息：{user_input}。我會盡力協助您！"


    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        獲取對話歷史

        Returns:
            List[Dict]: 對話歷史列表
        """
        return self.conversation_history


    def clear_history(self):
        """清空對話歷史"""
        self.conversation_history = []
        logger.info("已清空對話歷史")


def demonstrate_basic_usage():
    """
    演示基本使用方法

    展示如何創建和使用一個簡單的 Agent
    """
    print("\n" + "="*60)
    print("示例 1: 基本 Agent 創建和使用")
    print("="*60 + "\n")

    # 創建工具
    tools = create_simple_tools()

    # 創建 Agent
    agent = SimpleAgent(
        name="助手小明",
        system_prompt="你是一個友善且樂於助人的 AI 助手，可以協助用戶完成各種任務。",
        tools=tools
    )

    # 進行對話
    test_queries = [
        "現在幾點？",
        "計算 123 + 456",
        "搜索 Strands Agents",
        "台北的天氣如何？"
    ]

    for query in test_queries:
        print(f"用戶: {query}")
        response = agent.run(query)
        print(f"Agent: {response}\n")


def demonstrate_tool_registration():
    """
    演示動態工具註冊

    展示如何在運行時添加新的工具到 Agent
    """
    print("\n" + "="*60)
    print("示例 2: 動態工具註冊")
    print("="*60 + "\n")

    # 創建 Agent（初始沒有工具）
    agent = SimpleAgent(
        name="靈活助手",
        system_prompt="我可以學習新技能！"
    )

    # 動態添加工具
    def translate(text: str, target_lang: str = "英文") -> str:
        """翻譯文本（模擬）"""
        translations = {
            "你好": "Hello",
            "謝謝": "Thank you",
            "再見": "Goodbye"
        }
        return translations.get(text, f"[翻譯成{target_lang}]: {text}")

    agent.add_tool(translate)

    print(f"已添加翻譯工具")
    print(f"當前工具數量: {len(agent.tools)}\n")


def demonstrate_conversation_flow():
    """
    演示多輪對話流程

    展示如何維護對話上下文和歷史記錄
    """
    print("\n" + "="*60)
    print("示例 3: 多輪對話流程")
    print("="*60 + "\n")

    tools = create_simple_tools()
    agent = SimpleAgent(
        name="對話助手",
        system_prompt="你是一個專注於持續對話的助手。",
        tools=tools
    )

    # 模擬多輪對話
    conversations = [
        "你好，請告訴我現在的時間",
        "謝謝！請幫我搜索 AWS Bedrock",
        "很好，那台北的天氣呢？"
    ]

    for i, message in enumerate(conversations, 1):
        print(f"第 {i} 輪對話")
        print(f"用戶: {message}")
        response = agent.run(message)
        print(f"Agent: {response}\n")

    # 顯示對話歷史
    print("\n對話歷史記錄:")
    print("-" * 60)
    history = agent.get_conversation_history()
    for entry in history:
        role = "用戶" if entry["role"] == "user" else "助手"
        print(f"{role}: {entry['content']}")


def demonstrate_error_handling():
    """
    演示錯誤處理

    展示如何處理各種異常情況
    """
    print("\n" + "="*60)
    print("示例 4: 錯誤處理")
    print("="*60 + "\n")

    def risky_operation(value: int) -> str:
        """可能會失敗的操作"""
        if value < 0:
            raise ValueError("數值不能為負數")
        if value > 100:
            raise ValueError("數值不能大於 100")
        return f"處理成功: {value}"

    agent = SimpleAgent(
        name="錯誤處理示範",
        system_prompt="我會妥善處理錯誤。",
        tools=[risky_operation]
    )

    print("測試正常情況:")
    try:
        result = risky_operation(50)
        print(f"結果: {result}\n")
    except Exception as e:
        print(f"錯誤: {str(e)}\n")

    print("測試異常情況:")
    try:
        result = risky_operation(-10)
        print(f"結果: {result}\n")
    except Exception as e:
        print(f"捕獲錯誤: {str(e)}\n")


def main():
    """
    主函數 - 執行所有示例

    這個函數會依序執行所有的示例代碼，
    展示 Strands Agents 的各種基礎功能。
    """
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*10 + "Strands Agents 快速開始示例" + " "*18 + "║")
    print("║" + " "*58 + "║")
    print("║" + "  AWS 企業級 AI Agent SDK - 生產環境驗證" + " "*15 + "║")
    print("╚" + "="*58 + "╝")

    try:
        # 設置環境
        setup_environment()

        # 執行各個示例
        demonstrate_basic_usage()
        demonstrate_tool_registration()
        demonstrate_conversation_flow()
        demonstrate_error_handling()

        print("\n" + "="*60)
        print("所有示例執行完成！")
        print("="*60)

        print("\n下一步:")
        print("  1. 查看 02_工具定義.py 學習更高級的工具定義")
        print("  2. 查看 03_對話記憶.py 了解記憶管理")
        print("  3. 查看 04_Bedrock整合.py 學習 AWS Bedrock 集成")
        print("  4. 閱讀 README.md 獲取完整文檔")

    except Exception as e:
        logger.error(f"執行過程中出現錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    # 執行主程序
    exit_code = main()
    sys.exit(exit_code)

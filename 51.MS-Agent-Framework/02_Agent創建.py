"""
Microsoft Agent Framework - Agent 創建和配置

這個檔案深入探討如何創建和配置各種類型的 Agent。
包含進階配置選項、自定義行為、工具整合等。

主要內容:
1. 基礎 Agent 配置
2. 工具和函數定義
3. 系統提示詞設計
4. Agent 個性化設定
5. 進階配置選項
6. 工具參數驗證
7. 自定義工具類別
8. Agent 模板和最佳實踐

作者: Microsoft Agent Framework Team
日期: 2025-12-31
版本: 1.0.0
"""

import os
from typing import List, Dict, Any, Optional, Callable, Annotated
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv

# Agent Framework 核心模組
from agent_framework import Agent, AgentThread
from agent_framework.models import OpenAIModel
from agent_framework.tools import Tool, FunctionTool, ToolParameter
from agent_framework.responses import ResponseFormat, JSONResponseFormat

# ============================================================================
# 1. 工具參數定義 (使用 Pydantic)
# ============================================================================

class WeatherUnit(str, Enum):
    """溫度單位枚舉"""
    CELSIUS = "celsius"
    FAHRENHEIT = "fahrenheit"
    KELVIN = "kelvin"


class WeatherRequest(BaseModel):
    """
    天氣查詢請求參數

    使用 Pydantic 模型定義工具參數可以提供:
    - 自動類型驗證
    - 詳細的錯誤訊息
    - API 文檔生成
    - IDE 自動完成支援
    """
    location: Annotated[str, Field(
        description="城市或地區名稱,如 '台北' 或 '台北市信義區'",
        min_length=1,
        max_length=100
    )]

    unit: Annotated[WeatherUnit, Field(
        default=WeatherUnit.CELSIUS,
        description="溫度單位: celsius(攝氏), fahrenheit(華氏), 或 kelvin(克氏)"
    )]

    include_forecast: Annotated[bool, Field(
        default=False,
        description="是否包含未來天氣預報"
    )]

    @validator('location')
    def validate_location(cls, v):
        """驗證位置名稱"""
        if v.strip() == "":
            raise ValueError("位置名稱不能為空白")
        return v.strip()


class CalculationRequest(BaseModel):
    """計算請求參數"""
    expression: Annotated[str, Field(
        description="要計算的數學表達式,如 '2 + 3 * 4'",
        min_length=1
    )]

    precision: Annotated[int, Field(
        default=2,
        ge=0,
        le=10,
        description="小數點精度 (0-10)"
    )]


class SearchRequest(BaseModel):
    """搜尋請求參數"""
    query: Annotated[str, Field(
        description="搜尋關鍵字",
        min_length=1,
        max_length=200
    )]

    max_results: Annotated[int, Field(
        default=5,
        ge=1,
        le=20,
        description="最大結果數量 (1-20)"
    )]

    search_type: Annotated[str, Field(
        default="general",
        description="搜尋類型: general(一般), technical(技術), news(新聞)"
    )]


# ============================================================================
# 2. 高級工具函數實作
# ============================================================================

class WeatherService:
    """
    天氣服務類別

    將工具函數封裝在類別中可以:
    - 維護狀態和配置
    - 共享資源 (如 API 客戶端)
    - 更好的代碼組織
    """

    def __init__(self, api_key: Optional[str] = None):
        """初始化天氣服務"""
        self.api_key = api_key
        self.cache = {}  # 簡單的快取機制

    def get_weather(self, request: WeatherRequest) -> Dict[str, Any]:
        """
        獲取天氣資訊

        Args:
            request: 天氣查詢請求

        Returns:
            包含天氣資訊的字典
        """
        # 檢查快取
        cache_key = f"{request.location}_{request.unit}"
        if cache_key in self.cache:
            print(f"  ℹ️  從快取讀取 {request.location} 的天氣")
            return self.cache[cache_key]

        # 模擬天氣資料
        weather_data = {
            "台北": {"temp": 25, "condition": "晴天", "humidity": 65, "wind": 12},
            "高雄": {"temp": 28, "condition": "多雲", "humidity": 70, "wind": 15},
            "台中": {"temp": 26, "condition": "陰天", "humidity": 60, "wind": 10},
            "台南": {"temp": 27, "condition": "晴天", "humidity": 68, "wind": 13},
            "新竹": {"temp": 24, "condition": "多雲", "humidity": 62, "wind": 18},
        }

        base_data = weather_data.get(
            request.location,
            {"temp": 22, "condition": "未知", "humidity": 50, "wind": 10}
        )

        # 溫度單位轉換
        temp = base_data["temp"]
        if request.unit == WeatherUnit.FAHRENHEIT:
            temp = temp * 9/5 + 32
        elif request.unit == WeatherUnit.KELVIN:
            temp = temp + 273.15

        result = {
            "location": request.location,
            "temperature": round(temp, 2),
            "unit": request.unit.value,
            "condition": base_data["condition"],
            "humidity": base_data["humidity"],
            "wind_speed": base_data["wind"],
            "timestamp": datetime.now().isoformat(),
        }

        # 添加預報資訊
        if request.include_forecast:
            result["forecast"] = self._generate_forecast(request.location)

        # 更新快取
        self.cache[cache_key] = result

        return result

    def _generate_forecast(self, location: str) -> List[Dict[str, Any]]:
        """生成未來天氣預報 (模擬)"""
        return [
            {"day": "明天", "temp": 26, "condition": "晴天"},
            {"day": "後天", "temp": 24, "condition": "多雲"},
            {"day": "大後天", "temp": 25, "condition": "晴天"},
        ]


class CalculatorService:
    """計算服務類別"""

    ALLOWED_OPERATIONS = {
        'abs', 'round', 'min', 'max', 'sum',
        'pow', 'sqrt', 'sin', 'cos', 'tan',
        'log', 'exp', 'floor', 'ceil'
    }

    def calculate(self, request: CalculationRequest) -> Dict[str, Any]:
        """
        執行數學計算

        Args:
            request: 計算請求

        Returns:
            計算結果
        """
        try:
            # 安全的計算環境
            import math

            # 建立安全的命名空間
            safe_namespace = {
                '__builtins__': {},
                'abs': abs, 'round': round, 'min': min, 'max': max, 'sum': sum,
                'pow': pow, 'sqrt': math.sqrt, 'pi': math.pi, 'e': math.e,
                'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
                'log': math.log, 'exp': math.exp,
                'floor': math.floor, 'ceil': math.ceil,
            }

            # 執行計算
            result = eval(request.expression, safe_namespace, {})

            # 格式化結果
            if isinstance(result, float):
                result = round(result, request.precision)

            return {
                "expression": request.expression,
                "result": result,
                "precision": request.precision,
                "timestamp": datetime.now().isoformat(),
            }

        except ZeroDivisionError:
            return {
                "error": "除以零錯誤",
                "expression": request.expression,
            }
        except Exception as e:
            return {
                "error": f"計算錯誤: {str(e)}",
                "expression": request.expression,
            }


class KnowledgeBase:
    """知識庫服務"""

    def __init__(self):
        """初始化知識庫"""
        self.knowledge = {
            "agent framework": {
                "title": "Microsoft Agent Framework",
                "description": "AutoGen 和 Semantic Kernel 的統一框架",
                "category": "技術",
                "tags": ["AI", "Agent", "Microsoft"],
            },
            "mcp": {
                "title": "Model Context Protocol",
                "description": "Anthropic 提出的標準化工具整合協議",
                "category": "技術",
                "tags": ["Protocol", "AI", "Anthropic"],
            },
            "autogen": {
                "title": "AutoGen",
                "description": "微軟研究院開發的多 Agent 對話框架",
                "category": "技術",
                "tags": ["AI", "Agent", "Microsoft"],
            },
            "semantic kernel": {
                "title": "Semantic Kernel",
                "description": "微軟的企業級 LLM 整合框架",
                "category": "技術",
                "tags": ["AI", "LLM", "Microsoft"],
            },
        }

    def search(self, request: SearchRequest) -> Dict[str, Any]:
        """
        搜尋知識庫

        Args:
            request: 搜尋請求

        Returns:
            搜尋結果
        """
        query_lower = request.query.lower()
        results = []

        # 搜尋匹配項目
        for key, value in self.knowledge.items():
            if (query_lower in key or
                query_lower in value["title"].lower() or
                query_lower in value["description"].lower()):

                results.append({
                    "keyword": key,
                    "title": value["title"],
                    "description": value["description"],
                    "category": value["category"],
                    "tags": value["tags"],
                })

                if len(results) >= request.max_results:
                    break

        return {
            "query": request.query,
            "total_results": len(results),
            "results": results,
            "search_type": request.search_type,
        }


# ============================================================================
# 3. Agent 配置類別
# ============================================================================

class AgentConfig(BaseModel):
    """
    Agent 配置模型

    統一管理 Agent 的各種配置參數
    """
    name: str = Field(description="Agent 名稱")
    role: str = Field(description="Agent 角色")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2000, ge=100, le=8000)
    enable_tools: bool = Field(default=True)
    enable_memory: bool = Field(default=True)
    language: str = Field(default="zh-TW")
    personality: Optional[str] = None


# ============================================================================
# 4. Agent 工廠類別
# ============================================================================

class AgentFactory:
    """
    Agent 工廠類別

    提供統一的 Agent 創建介面,封裝複雜的配置邏輯
    """

    def __init__(self, model: OpenAIModel):
        """初始化工廠"""
        self.model = model
        self.weather_service = WeatherService()
        self.calculator_service = CalculatorService()
        self.knowledge_base = KnowledgeBase()

    def create_general_assistant(
        self,
        name: str = "assistant",
        config: Optional[AgentConfig] = None
    ) -> Agent:
        """
        創建通用助手 Agent

        這是一個多功能的 Agent,可以處理各種常見任務。

        Args:
            name: Agent 名稱
            config: 配置物件

        Returns:
            配置好的 Agent
        """
        if config is None:
            config = AgentConfig(
                name=name,
                role="通用助手",
                temperature=0.7,
            )

        # 定義系統提示詞
        instructions = f"""
        你是 {config.name},一個{config.role}。

        你的能力包括:
        1. 查詢天氣資訊
        2. 執行數學計算
        3. 搜尋知識庫
        4. 回答一般問題

        請遵循以下原則:
        - 使用{config.language}回應
        - 保持友善和專業的態度
        - 適時使用提供的工具
        - 提供清晰、準確的資訊
        - 如果不確定,誠實告知

        {f'個性特點: {config.personality}' if config.personality else ''}
        """

        # 創建工具列表
        tools = []
        if config.enable_tools:
            tools = [
                self.weather_service.get_weather,
                self.calculator_service.calculate,
                self.knowledge_base.search,
            ]

        # 創建 Agent
        agent = Agent(
            name=config.name,
            model=self.model,
            instructions=instructions.strip(),
            tools=tools,
        )

        return agent

    def create_weather_expert(self, name: str = "weather_expert") -> Agent:
        """
        創建天氣專家 Agent

        專門處理天氣相關查詢的 Agent

        Args:
            name: Agent 名稱

        Returns:
            專門的天氣 Agent
        """
        instructions = """
        你是一位專業的氣象專家,專門提供天氣資訊和氣象分析。

        你的專長:
        - 提供準確的天氣資訊
        - 解釋天氣現象
        - 給予天氣相關建議 (如穿衣、出行等)
        - 分析氣象趨勢

        回應時請:
        - 使用專業但易懂的語言
        - 提供實用的建議
        - 必要時說明天氣變化的原因
        - 使用繁體中文
        """

        agent = Agent(
            name=name,
            model=self.model,
            instructions=instructions.strip(),
            tools=[
                self.weather_service.get_weather,
                self.calculator_service.calculate,  # 用於溫度換算等
            ],
        )

        return agent

    def create_math_tutor(self, name: str = "math_tutor") -> Agent:
        """
        創建數學教師 Agent

        專門輔導數學問題的 Agent

        Args:
            name: Agent 名稱

        Returns:
            數學教師 Agent
        """
        instructions = """
        你是一位親切的數學教師,專門幫助學生理解和解決數學問題。

        教學原則:
        - 先理解學生的問題
        - 提供清晰的解題步驟
        - 解釋每個步驟的原理
        - 鼓勵學生思考
        - 使用簡單易懂的語言

        教學風格:
        - 有耐心,不厭其煩
        - 適度鼓勵和讚美
        - 使用生活化的例子
        - 確保學生真正理解

        使用繁體中文教學。
        """

        agent = Agent(
            name=name,
            model=self.model,
            instructions=instructions.strip(),
            tools=[self.calculator_service.calculate],
        )

        return agent

    def create_knowledge_librarian(self, name: str = "librarian") -> Agent:
        """
        創建知識管理員 Agent

        專門管理和檢索知識的 Agent

        Args:
            name: Agent 名稱

        Returns:
            知識管理員 Agent
        """
        instructions = """
        你是一位專業的知識管理員,擅長組織和檢索資訊。

        你的職責:
        - 幫助用戶找到所需資訊
        - 提供準確的知識回答
        - 整理和歸納資訊
        - 建議相關的知識主題

        工作方式:
        - 仔細理解用戶需求
        - 搜尋相關知識
        - 組織並呈現結果
        - 提供額外的相關資訊

        使用繁體中文,以專業但友善的方式回應。
        """

        agent = Agent(
            name=name,
            model=self.model,
            instructions=instructions.strip(),
            tools=[self.knowledge_base.search],
        )

        return agent


# ============================================================================
# 5. 測試和示範
# ============================================================================

def demonstrate_agent_creation():
    """示範各種 Agent 的創建和使用"""
    print("="*70)
    print("Microsoft Agent Framework - Agent 創建和配置")
    print("="*70)

    # 載入環境變數
    load_dotenv()

    # 創建模型
    model = OpenAIModel(
        model=os.getenv("OPENAI_MODEL", "gpt-4"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    # 創建工廠
    factory = AgentFactory(model)

    # ========================================================================
    # 範例 1: 通用助手
    # ========================================================================
    print("\n" + "="*70)
    print("🎯 範例 1: 通用助手")
    print("="*70)

    general_config = AgentConfig(
        name="小智",
        role="AI 助手",
        temperature=0.7,
        personality="友善、耐心、專業"
    )

    assistant = factory.create_general_assistant(config=general_config)
    thread1 = AgentThread()

    test_queries = [
        "台北今天天氣如何?",
        "幫我計算 123 * 456",
        "什麼是 MCP 協議?",
    ]

    for query in test_queries:
        print(f"\n👤 用戶: {query}")
        response = assistant.run(thread=thread1, messages=query)
        print(f"🤖 {assistant.name}: {response.content}")

    # ========================================================================
    # 範例 2: 專業天氣專家
    # ========================================================================
    print("\n" + "="*70)
    print("🎯 範例 2: 天氣專家")
    print("="*70)

    weather_expert = factory.create_weather_expert()
    thread2 = AgentThread()

    weather_queries = [
        "台北和高雄今天的天氣有什麼不同?",
        "我明天要去台中,建議穿什麼衣服?",
    ]

    for query in weather_queries:
        print(f"\n👤 用戶: {query}")
        response = weather_expert.run(thread=thread2, messages=query)
        print(f"🤖 {weather_expert.name}: {response.content}")

    # ========================================================================
    # 範例 3: 數學教師
    # ========================================================================
    print("\n" + "="*70)
    print("🎯 範例 3: 數學教師")
    print("="*70)

    math_tutor = factory.create_math_tutor()
    thread3 = AgentThread()

    math_queries = [
        "什麼是畢達哥拉斯定理?",
        "幫我計算三角形面積,底是 10,高是 5",
    ]

    for query in math_queries:
        print(f"\n👤 學生: {query}")
        response = math_tutor.run(thread=thread3, messages=query)
        print(f"🤖 {math_tutor.name}: {response.content}")

    # ========================================================================
    # 範例 4: 知識管理員
    # ========================================================================
    print("\n" + "="*70)
    print("🎯 範例 4: 知識管理員")
    print("="*70)

    librarian = factory.create_knowledge_librarian()
    thread4 = AgentThread()

    knowledge_queries = [
        "搜尋關於 Agent Framework 的資訊",
        "Microsoft 有哪些 AI 相關的框架?",
    ]

    for query in knowledge_queries:
        print(f"\n👤 用戶: {query}")
        response = librarian.run(thread=thread4, messages=query)
        print(f"🤖 {librarian.name}: {response.content}")


# ============================================================================
# 6. 進階配置示範
# ============================================================================

def demonstrate_advanced_configuration():
    """示範進階配置選項"""
    print("\n" + "="*70)
    print("🎯 進階配置示範")
    print("="*70)

    load_dotenv()

    model = OpenAIModel(
        model=os.getenv("OPENAI_MODEL", "gpt-4"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    # 自定義回應格式
    weather_service = WeatherService()

    # 創建具有結構化輸出的 Agent
    structured_agent = Agent(
        name="structured_assistant",
        model=model,
        instructions="你是一個提供結構化資訊的助手",
        tools=[weather_service.get_weather],
        # response_format=JSONResponseFormat()  # 要求 JSON 格式輸出
    )

    print("\n✅ 創建了具有結構化輸出的 Agent")
    print(f"   Agent: {structured_agent.name}")


# ============================================================================
# 7. 主程式
# ============================================================================

def main():
    """主程式"""
    demonstrate_agent_creation()
    demonstrate_advanced_configuration()

    print("\n" + "="*70)
    print("✅ Agent 創建示範完成!")
    print("="*70)

    print("\n💡 關鍵要點:")
    print("   1. 使用 Pydantic 定義工具參數,提供類型安全")
    print("   2. 封裝工具函數到服務類別,便於維護")
    print("   3. 使用工廠模式創建 Agent,提高複用性")
    print("   4. 針對不同場景創建專門的 Agent")
    print("   5. 透過配置物件統一管理 Agent 參數")

    print("\n📚 下一步:")
    print("   查看 03_多Agent編排.py 學習多 Agent 協作")


if __name__ == "__main__":
    main()

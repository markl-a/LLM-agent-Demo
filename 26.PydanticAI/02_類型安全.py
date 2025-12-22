"""
Pydantic AI - 類型安全範例

本範例展示：
1. 完整的類型提示
2. Pydantic 模型驗證
3. 泛型類型支持
4. 類型安全的工具定義
5. IDE 自動補全支持

Pydantic AI 的類型安全是其最大特色之一
"""

import asyncio
from typing import Optional, Literal, Annotated, TypedDict
from dataclasses import dataclass
from pydantic import BaseModel, Field, field_validator
from pydantic_ai import Agent, RunContext


# ============================================================================
# 範例 1: 基本類型提示
# ============================================================================

def example_1_basic_types():
    """展示基本的類型提示用法"""
    print("\n" + "="*60)
    print("範例 1: 基本類型提示")
    print("="*60)

    # Agent 泛型：Agent[DepsType, ResultType]
    # - DepsType: 依賴注入的類型
    # - ResultType: 返回結果的類型

    # 無依賴，返回字符串
    agent_simple: Agent[None, str] = Agent('openai:gpt-4')

    result = agent_simple.run_sync('Say hello')
    # IDE 知道 result.data 是 str 類型
    message: str = result.data
    print(f"回應（{type(message).__name__}）：{message}")


# ============================================================================
# 範例 2: Pydantic 模型作為結果類型
# ============================================================================

class UserProfile(BaseModel):
    """用戶資料模型"""
    name: str = Field(description="用戶姓名")
    age: int = Field(ge=0, le=150, description="年齡，0-150 之間")
    email: str = Field(pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$', description="電子郵件")
    hobbies: list[str] = Field(default_factory=list, description="興趣愛好")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """驗證姓名不為空"""
        if not v.strip():
            raise ValueError('姓名不能為空')
        return v.strip()


def example_2_pydantic_result():
    """使用 Pydantic 模型作為結果類型"""
    print("\n" + "="*60)
    print("範例 2: Pydantic 模型結果類型")
    print("="*60)

    # 指定結果類型為 UserProfile
    agent: Agent[None, UserProfile] = Agent(
        'openai:gpt-4',
        result_type=UserProfile,
    )

    prompt = """
    從這段文字提取用戶資料：
    "張小明今年 28 歲，email 是 ming@example.com，喜歡游泳和閱讀"
    """

    result = agent.run_sync(prompt)

    # result.data 自動驗證並解析為 UserProfile 類型
    profile: UserProfile = result.data

    # IDE 提供完整的自動補全
    print(f"姓名：{profile.name}")
    print(f"年齡：{profile.age}")
    print(f"Email：{profile.email}")
    print(f"興趣：{', '.join(profile.hobbies)}")


# ============================================================================
# 範例 3: 複雜的嵌套模型
# ============================================================================

class Address(BaseModel):
    """地址模型"""
    street: str
    city: str
    country: str
    postal_code: Optional[str] = None


class Company(BaseModel):
    """公司模型"""
    name: str
    industry: str
    employees: int = Field(gt=0)
    address: Address


class PersonProfile(BaseModel):
    """完整的個人檔案"""
    name: str
    age: int
    company: Optional[Company] = None
    skills: list[str] = Field(default_factory=list)


async def example_3_nested_models():
    """處理複雜的嵌套 Pydantic 模型"""
    print("\n" + "="*60)
    print("範例 3: 嵌套 Pydantic 模型")
    print("="*60)

    agent: Agent[None, PersonProfile] = Agent(
        'openai:gpt-4',
        result_type=PersonProfile,
    )

    prompt = """
    提取人物資訊：
    "李小華，35 歲，在位於台北市信義路的科技公司 TechCorp 工作，
    該公司有 500 名員工，主要業務是軟體開發。
    李小華擅長 Python、JavaScript 和機器學習。"
    """

    result = await agent.run(prompt)
    person: PersonProfile = result.data

    print(f"姓名：{person.name}")
    print(f"年齡：{person.age}")

    if person.company:
        print(f"公司：{person.company.name}")
        print(f"產業：{person.company.industry}")
        print(f"員工數：{person.company.employees}")
        print(f"地址：{person.company.address.city}, {person.company.address.street}")

    print(f"技能：{', '.join(person.skills)}")


# ============================================================================
# 範例 4: 類型安全的依賴注入
# ============================================================================

@dataclass
class DatabaseConfig:
    """數據庫配置"""
    host: str
    port: int
    username: str
    password: str

    def get_connection_string(self) -> str:
        """獲取連接字符串"""
        return f"postgresql://{self.username}:***@{self.host}:{self.port}"


class QueryResult(BaseModel):
    """查詢結果"""
    query: str
    result_count: int
    execution_time_ms: float


def example_4_typed_dependencies():
    """使用類型安全的依賴注入"""
    print("\n" + "="*60)
    print("範例 4: 類型安全的依賴注入")
    print("="*60)

    # 指定依賴類型為 DatabaseConfig，結果類型為 QueryResult
    agent: Agent[DatabaseConfig, QueryResult] = Agent(
        'openai:gpt-4',
        deps_type=DatabaseConfig,
        result_type=QueryResult,
    )

    @agent.tool
    def execute_query(
        ctx: RunContext[DatabaseConfig],  # 類型提示依賴
        sql: str
    ) -> str:
        """執行 SQL 查詢（模擬）"""
        # IDE 知道 ctx.deps 是 DatabaseConfig 類型
        db_config: DatabaseConfig = ctx.deps

        print(f"  連接到：{db_config.get_connection_string()}")
        print(f"  執行查詢：{sql}")

        # 模擬查詢結果
        return f"找到 42 條記錄，耗時 15.3ms"

    # 創建依賴實例
    db_config = DatabaseConfig(
        host='localhost',
        port=5432,
        username='admin',
        password='secret'
    )

    result = agent.run_sync(
        '查詢所有活躍用戶',
        deps=db_config
    )

    # result.data 是 QueryResult 類型
    query_result: QueryResult = result.data
    print(f"\n查詢：{query_result.query}")
    print(f"結果數：{query_result.result_count}")
    print(f"執行時間：{query_result.execution_time_ms}ms")


# ============================================================================
# 範例 5: Literal 類型限制
# ============================================================================

class WeatherQuery(BaseModel):
    """天氣查詢"""
    city: str
    units: Literal["celsius", "fahrenheit"] = "celsius"
    include_forecast: bool = False


class WeatherData(BaseModel):
    """天氣數據"""
    temperature: float
    condition: Literal["sunny", "cloudy", "rainy", "snowy"]
    humidity: int = Field(ge=0, le=100)
    units: Literal["celsius", "fahrenheit"]


async def example_5_literal_types():
    """使用 Literal 類型限制選項"""
    print("\n" + "="*60)
    print("範例 5: Literal 類型限制")
    print("="*60)

    agent: Agent[None, WeatherData] = Agent(
        'openai:gpt-4',
        result_type=WeatherData,
    )

    # Literal 確保值只能是特定的幾個選項
    result = await agent.run(
        '台北現在的天氣：25 度，晴天，濕度 60%'
    )

    weather: WeatherData = result.data

    # IDE 知道 condition 只能是四個值之一
    print(f"溫度：{weather.temperature}°{weather.units.upper()}")
    print(f"天氣：{weather.condition}")
    print(f"濕度：{weather.humidity}%")


# ============================================================================
# 範例 6: Annotated 類型增強
# ============================================================================

class ProductInfo(BaseModel):
    """產品信息"""
    name: Annotated[str, Field(min_length=1, max_length=100)]
    price: Annotated[float, Field(gt=0, description="價格必須大於 0")]
    stock: Annotated[int, Field(ge=0, description="庫存不能為負")]
    rating: Annotated[float, Field(ge=0, le=5, description="評分 0-5")]
    categories: Annotated[
        list[str],
        Field(min_length=1, description="至少一個分類")
    ]


def example_6_annotated_types():
    """使用 Annotated 增強類型提示"""
    print("\n" + "="*60)
    print("範例 6: Annotated 類型增強")
    print("="*60)

    agent: Agent[None, ProductInfo] = Agent(
        'openai:gpt-4',
        result_type=ProductInfo,
    )

    prompt = """
    提取產品資訊：
    "iPhone 15 Pro，售價 33900 元，庫存 150 件，
    評分 4.5 星，分類：電子產品、智慧型手機"
    """

    result = agent.run_sync(prompt)
    product: ProductInfo = result.data

    print(f"產品：{product.name}")
    print(f"價格：${product.price:,.2f}")
    print(f"庫存：{product.stock} 件")
    print(f"評分：{'⭐' * int(product.rating)} ({product.rating}/5)")
    print(f"分類：{' > '.join(product.categories)}")


# ============================================================================
# 範例 7: Optional 和 Union 類型
# ============================================================================

class ContactInfo(BaseModel):
    """聯絡資訊"""
    email: Optional[str] = None
    phone: Optional[str] = None
    preferred_contact: Literal["email", "phone", "none"] = "none"

    @field_validator('email', 'phone')
    @classmethod
    def at_least_one_contact(cls, v, info):
        """確保至少有一種聯絡方式"""
        return v


class Person(BaseModel):
    """人物"""
    name: str
    contact: Optional[ContactInfo] = None


async def example_7_optional_types():
    """處理 Optional 類型"""
    print("\n" + "="*60)
    print("範例 7: Optional 類型")
    print("="*60)

    agent: Agent[None, Person] = Agent(
        'openai:gpt-4',
        result_type=Person,
    )

    # 有聯絡資訊
    result1 = await agent.run(
        '王小明，email: wang@example.com'
    )
    person1: Person = result1.data

    print(f"姓名：{person1.name}")
    if person1.contact:
        print(f"Email：{person1.contact.email or '無'}")
        print(f"電話：{person1.contact.phone or '無'}")

    # 沒有聯絡資訊
    result2 = await agent.run('李小華')
    person2: Person = result2.data

    print(f"\n姓名：{person2.name}")
    print(f"聯絡資訊：{'有' if person2.contact else '無'}")


# ============================================================================
# 範例 8: 類型安全的工具函數
# ============================================================================

@dataclass
class AppContext:
    """應用程式上下文"""
    user_id: int
    session_id: str
    permissions: set[str]


class CalculationResult(BaseModel):
    """計算結果"""
    operation: str
    result: float
    steps: list[str]


def example_8_typed_tools():
    """創建類型安全的工具函數"""
    print("\n" + "="*60)
    print("範例 8: 類型安全的工具")
    print("="*60)

    agent: Agent[AppContext, CalculationResult] = Agent(
        'openai:gpt-4',
        deps_type=AppContext,
        result_type=CalculationResult,
    )

    @agent.tool
    def calculate(
        ctx: RunContext[AppContext],
        operation: Literal["add", "subtract", "multiply", "divide"],
        a: Annotated[float, Field(description="第一個數字")],
        b: Annotated[float, Field(description="第二個數字")],
    ) -> dict[str, float | str]:
        """
        執行數學運算

        完整的類型提示確保：
        - IDE 自動補全
        - 編譯時類型檢查
        - 運行時驗證
        """
        # IDE 知道 ctx.deps 是 AppContext
        print(f"  用戶 {ctx.deps.user_id} 執行計算")

        # operation 只能是四個值之一
        operations = {
            "add": a + b,
            "subtract": a - b,
            "multiply": a * b,
            "divide": a / b if b != 0 else float('inf'),
        }

        result = operations[operation]
        return {
            "result": result,
            "operation": f"{a} {operation} {b}",
        }

    # 創建上下文
    context = AppContext(
        user_id=123,
        session_id="abc-def",
        permissions={"read", "write", "calculate"}
    )

    result = agent.run_sync(
        '計算 15 乘以 7',
        deps=context
    )

    calc_result: CalculationResult = result.data
    print(f"\n操作：{calc_result.operation}")
    print(f"結果：{calc_result.result}")


# ============================================================================
# 範例 9: 泛型類型參數
# ============================================================================

from typing import TypeVar, Generic

T = TypeVar('T')


class Response(BaseModel, Generic[T]):
    """泛型響應包裝器"""
    success: bool
    data: T
    message: str = ""


class UserData(BaseModel):
    """用戶數據"""
    username: str
    score: int


async def example_9_generic_types():
    """使用泛型類型"""
    print("\n" + "="*60)
    print("範例 9: 泛型類型")
    print("="*60)

    # Response[UserData] 是具體化的泛型類型
    agent: Agent[None, Response[UserData]] = Agent(
        'openai:gpt-4',
        result_type=Response[UserData],
    )

    result = await agent.run(
        '創建用戶資料：用戶名 alice，分數 95'
    )

    # IDE 知道這是 Response[UserData] 類型
    response: Response[UserData] = result.data

    print(f"成功：{response.success}")
    print(f"用戶名：{response.data.username}")
    print(f"分數：{response.data.score}")


# ============================================================================
# 主程式
# ============================================================================

async def main():
    """運行所有範例"""
    print("\n" + "🔒 " + "="*58)
    print("Pydantic AI - 類型安全範例")
    print("="*60)

    example_1_basic_types()
    example_2_pydantic_result()
    await example_3_nested_models()
    example_4_typed_dependencies()
    await example_5_literal_types()
    example_6_annotated_types()
    await example_7_optional_types()
    example_8_typed_tools()
    await example_9_generic_types()

    print("\n" + "="*60)
    print("✓ 類型安全範例完成！")
    print("💡 提示：使用支持類型檢查的 IDE（如 PyCharm、VSCode）")
    print("   可以獲得最佳的開發體驗")
    print("="*60)


if __name__ == '__main__':
    import os
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  請設置 OPENAI_API_KEY 環境變量")
    else:
        asyncio.run(main())

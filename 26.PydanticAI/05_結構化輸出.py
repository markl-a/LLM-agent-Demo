"""
Pydantic AI - 結構化輸出範例

本範例展示：
1. Pydantic 模型作為輸出
2. 嵌套模型結構
3. 列表和字典輸出
4. 複雜驗證規則
5. 自定義序列化

結構化輸出是 Pydantic AI 的核心優勢
"""

import asyncio
from typing import Optional, Literal, Annotated
from datetime import datetime, date
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_ai import Agent


# ============================================================================
# 範例 1: 簡單結構化輸出
# ============================================================================

class WeatherInfo(BaseModel):
    """天氣信息"""
    city: str
    temperature: float
    condition: str
    humidity: int = Field(ge=0, le=100)


def example_1_simple_output():
    """最簡單的結構化輸出"""
    print("\n" + "="*60)
    print("範例 1: 簡單結構化輸出")
    print("="*60)

    # 指定結果類型
    agent: Agent[None, WeatherInfo] = Agent(
        'openai:gpt-4',
        result_type=WeatherInfo,
    )

    result = agent.run_sync(
        '台北現在 28 度，晴天，濕度 65%'
    )

    # 自動解析為 WeatherInfo 對象
    weather: WeatherInfo = result.data

    print(f"城市：{weather.city}")
    print(f"溫度：{weather.temperature}°C")
    print(f"天氣：{weather.condition}")
    print(f"濕度：{weather.humidity}%")


# ============================================================================
# 範例 2: 嵌套模型
# ============================================================================

class Author(BaseModel):
    """作者信息"""
    name: str
    email: Optional[str] = None
    bio: Optional[str] = None


class Tag(BaseModel):
    """標籤"""
    name: str
    color: str = "#000000"


class Article(BaseModel):
    """文章"""
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=10)
    author: Author
    tags: list[Tag] = Field(default_factory=list)
    published_at: Optional[datetime] = None
    view_count: int = Field(ge=0, default=0)

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """驗證標題"""
        if v.strip() != v:
            v = v.strip()
        if not v:
            raise ValueError('標題不能為空')
        return v


async def example_2_nested_models():
    """嵌套的 Pydantic 模型"""
    print("\n" + "="*60)
    print("範例 2: 嵌套模型")
    print("="*60)

    agent: Agent[None, Article] = Agent(
        'openai:gpt-4',
        result_type=Article,
    )

    prompt = """
    創建一篇關於 AI 的文章：
    - 標題：Pydantic AI 入門指南
    - 作者：張小明（email: ming@example.com）
    - 內容：Pydantic AI 是一個強大的 AI Agent 框架...
    - 標籤：AI（藍色）、Python（黃色）
    - 瀏覽次數：1250
    """

    result = await agent.run(prompt)
    article: Article = result.data

    print(f"標題：{article.title}")
    print(f"作者：{article.author.name} ({article.author.email})")
    print(f"內容：{article.content[:50]}...")
    print(f"標籤：{', '.join(tag.name for tag in article.tags)}")
    print(f"瀏覽：{article.view_count}")


# ============================================================================
# 範例 3: 列表輸出
# ============================================================================

class Product(BaseModel):
    """產品"""
    name: str
    price: float = Field(gt=0)
    category: str
    in_stock: bool = True


class ProductList(BaseModel):
    """產品列表"""
    products: list[Product]
    total_count: int
    average_price: float


def example_3_list_output():
    """輸出列表結構"""
    print("\n" + "="*60)
    print("範例 3: 列表輸出")
    print("="*60)

    agent: Agent[None, ProductList] = Agent(
        'openai:gpt-4',
        result_type=ProductList,
    )

    prompt = """
    從這段文字提取產品列表：
    1. iPhone 15 - 33900 元 - 電子產品 - 有貨
    2. MacBook Pro - 59900 元 - 電子產品 - 有貨
    3. AirPods - 7490 元 - 配件 - 缺貨
    計算總數和平均價格。
    """

    result = agent.run_sync(prompt)
    product_list: ProductList = result.data

    print(f"總產品數：{product_list.total_count}")
    print(f"平均價格：${product_list.average_price:,.2f}\n")

    for i, product in enumerate(product_list.products, 1):
        status = "✓ 有貨" if product.in_stock else "✗ 缺貨"
        print(f"{i}. {product.name} - ${product.price:,.0f} - {status}")


# ============================================================================
# 範例 4: Enum 枚舉類型
# ============================================================================

class Priority(str, Enum):
    """優先級"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Status(str, Enum):
    """狀態"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"


class Task(BaseModel):
    """任務"""
    title: str
    description: str
    priority: Priority
    status: Status = Status.TODO
    assignee: Optional[str] = None
    due_date: Optional[date] = None


async def example_4_enum_output():
    """使用 Enum 枚舉類型"""
    print("\n" + "="*60)
    print("範例 4: Enum 枚舉類型")
    print("="*60)

    agent: Agent[None, Task] = Agent(
        'openai:gpt-4',
        result_type=Task,
    )

    result = await agent.run(
        '創建任務：修復登入 Bug，高優先級，分配給 Alice，12月25日前完成'
    )

    task: Task = result.data

    # Enum 提供類型安全
    priority_colors = {
        Priority.LOW: "🟢",
        Priority.MEDIUM: "🟡",
        Priority.HIGH: "🟠",
        Priority.URGENT: "🔴",
    }

    print(f"任務：{task.title}")
    print(f"描述：{task.description}")
    print(f"優先級：{priority_colors[task.priority]} {task.priority.value}")
    print(f"狀態：{task.status.value}")
    print(f"負責人：{task.assignee}")
    print(f"截止日期：{task.due_date}")


# ============================================================================
# 範例 5: 複雜驗證規則
# ============================================================================

class UserRegistration(BaseModel):
    """用戶註冊"""
    username: str = Field(min_length=3, max_length=20, pattern=r'^[a-zA-Z0-9_]+$')
    email: str = Field(pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    password: str = Field(min_length=8)
    age: int = Field(ge=18, le=120)
    phone: Optional[str] = Field(None, pattern=r'^\d{10}$')

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """驗證用戶名"""
        forbidden = ['admin', 'root', 'system']
        if v.lower() in forbidden:
            raise ValueError(f'用戶名 {v} 不可用')
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """驗證密碼強度"""
        if not any(c.isupper() for c in v):
            raise ValueError('密碼必須包含大寫字母')
        if not any(c.islower() for c in v):
            raise ValueError('密碼必須包含小寫字母')
        if not any(c.isdigit() for c in v):
            raise ValueError('密碼必須包含數字')
        return v

    @model_validator(mode='after')
    def validate_model(self) -> 'UserRegistration':
        """模型級驗證"""
        # 用戶名不能包含在 email 中（避免洩漏）
        if self.username.lower() in self.email.lower():
            raise ValueError('用戶名不應該出現在 email 中')
        return self


def example_5_validation_rules():
    """複雜的驗證規則"""
    print("\n" + "="*60)
    print("範例 5: 複雜驗證規則")
    print("="*60)

    agent: Agent[None, UserRegistration] = Agent(
        'openai:gpt-4',
        result_type=UserRegistration,
    )

    prompt = """
    創建用戶註冊信息：
    - 用戶名：alice2024
    - Email：contact@example.com
    - 密碼：SecurePass123
    - 年齡：25
    - 電話：0912345678
    """

    result = agent.run_sync(prompt)
    registration: UserRegistration = result.data

    print(f"✓ 註冊成功")
    print(f"用戶名：{registration.username}")
    print(f"Email：{registration.email}")
    print(f"年齡：{registration.age}")
    print(f"電話：{registration.phone or '未提供'}")


# ============================================================================
# 範例 6: 字典和動態字段
# ============================================================================

class MetricValue(BaseModel):
    """指標值"""
    value: float
    unit: str
    timestamp: datetime = Field(default_factory=datetime.now)


class PerformanceReport(BaseModel):
    """性能報告"""
    report_id: str
    metrics: dict[str, MetricValue]
    summary: str
    recommendations: list[str] = Field(default_factory=list)


async def example_6_dict_output():
    """使用字典和動態字段"""
    print("\n" + "="*60)
    print("範例 6: 字典輸出")
    print("="*60)

    agent: Agent[None, PerformanceReport] = Agent(
        'openai:gpt-4',
        result_type=PerformanceReport,
    )

    prompt = """
    生成性能報告（ID: RPT-001）：
    - CPU 使用率：75%
    - 內存使用：4.2 GB
    - 響應時間：150 ms
    總結：系統運行正常，建議增加內存配置
    """

    result = await agent.run(prompt)
    report: PerformanceReport = result.data

    print(f"報告 ID：{report.report_id}")
    print(f"\n指標：")
    for name, metric in report.metrics.items():
        print(f"  {name}: {metric.value} {metric.unit}")

    print(f"\n總結：{report.summary}")

    if report.recommendations:
        print(f"\n建議：")
        for rec in report.recommendations:
            print(f"  - {rec}")


# ============================================================================
# 範例 7: 條件字段
# ============================================================================

class PaymentMethod(str, Enum):
    """支付方式"""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"


class Payment(BaseModel):
    """支付信息"""
    amount: float = Field(gt=0)
    currency: str = "TWD"
    method: PaymentMethod

    # 條件字段：僅當支付方式是信用卡時需要
    card_number: Optional[str] = Field(None, pattern=r'^\d{16}$')
    card_holder: Optional[str] = None

    # 條件字段：僅當支付方式是 PayPal 時需要
    paypal_email: Optional[str] = None

    # 條件字段：僅當支付方式是銀行轉賬時需要
    bank_account: Optional[str] = None

    @model_validator(mode='after')
    def validate_payment_details(self) -> 'Payment':
        """驗證支付詳情"""
        if self.method in (PaymentMethod.CREDIT_CARD, PaymentMethod.DEBIT_CARD):
            if not self.card_number or not self.card_holder:
                raise ValueError('信用卡支付需要卡號和持卡人')

        if self.method == PaymentMethod.PAYPAL:
            if not self.paypal_email:
                raise ValueError('PayPal 支付需要 email')

        if self.method == PaymentMethod.BANK_TRANSFER:
            if not self.bank_account:
                raise ValueError('銀行轉賬需要帳號')

        return self


def example_7_conditional_fields():
    """條件字段處理"""
    print("\n" + "="*60)
    print("範例 7: 條件字段")
    print("="*60)

    agent: Agent[None, Payment] = Agent(
        'openai:gpt-4',
        result_type=Payment,
    )

    # 信用卡支付
    result1 = agent.run_sync(
        '創建支付：1000 元，信用卡，卡號 1234567890123456，持卡人 張小明'
    )
    payment1: Payment = result1.data

    print(f"支付方式：{payment1.method.value}")
    print(f"金額：{payment1.amount} {payment1.currency}")
    print(f"卡號：****{payment1.card_number[-4:]}")
    print(f"持卡人：{payment1.card_holder}")


# ============================================================================
# 範例 8: 計算字段
# ============================================================================

class OrderItem(BaseModel):
    """訂單項目"""
    product_name: str
    quantity: int = Field(gt=0)
    unit_price: float = Field(gt=0)

    @property
    def subtotal(self) -> float:
        """小計"""
        return self.quantity * self.unit_price


class Order(BaseModel):
    """訂單"""
    order_id: str
    items: list[OrderItem]
    discount_percent: float = Field(ge=0, le=100, default=0)

    @property
    def subtotal(self) -> float:
        """小計總額"""
        return sum(item.subtotal for item in self.items)

    @property
    def discount_amount(self) -> float:
        """折扣金額"""
        return self.subtotal * (self.discount_percent / 100)

    @property
    def total(self) -> float:
        """總金額"""
        return self.subtotal - self.discount_amount


async def example_8_computed_fields():
    """使用計算字段"""
    print("\n" + "="*60)
    print("範例 8: 計算字段")
    print("="*60)

    agent: Agent[None, Order] = Agent(
        'openai:gpt-4',
        result_type=Order,
    )

    prompt = """
    創建訂單 ORD-001：
    1. iPhone 15 - 2 個 - 單價 33900
    2. AirPods - 1 個 - 單價 7490
    折扣 10%
    """

    result = await agent.run(prompt)
    order: Order = result.data

    print(f"訂單號：{order.order_id}")
    print(f"\n項目：")
    for item in order.items:
        print(f"  {item.product_name} x{item.quantity} = ${item.subtotal:,.0f}")

    print(f"\n小計：${order.subtotal:,.0f}")
    print(f"折扣（{order.discount_percent}%）：-${order.discount_amount:,.0f}")
    print(f"總計：${order.total:,.0f}")


# ============================================================================
# 主程式
# ============================================================================

async def main():
    """運行所有範例"""
    print("\n" + "📋 " + "="*58)
    print("Pydantic AI - 結構化輸出範例")
    print("="*60)

    example_1_simple_output()
    await example_2_nested_models()
    example_3_list_output()
    await example_4_enum_output()
    example_5_validation_rules()
    await example_6_dict_output()
    example_7_conditional_fields()
    await example_8_computed_fields()

    print("\n" + "="*60)
    print("✓ 結構化輸出範例完成！")
    print("💡 結構化輸出的優勢：")
    print("   1. 類型安全，避免錯誤")
    print("   2. 自動驗證，確保數據質量")
    print("   3. 清晰的數據結構")
    print("   4. 易於序列化和傳輸")
    print("="*60)


if __name__ == '__main__':
    import os
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  請設置 OPENAI_API_KEY 環境變量")
    else:
        asyncio.run(main())

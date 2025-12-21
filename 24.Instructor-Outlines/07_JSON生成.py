"""
Instructor/Outlines JSON 生成範例
================================

本範例展示如何使用 Instructor 和 Outlines 生成結構化 JSON。

功能：
1. Pydantic 模型約束
2. 嵌套結構生成
3. 列表和可選字段
4. 複雜數據提取

安裝依賴：
pip install instructor outlines pydantic
"""

import instructor
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional, Union
from enum import Enum
from datetime import date, datetime

# ============================================================
# 1. 基礎 JSON 生成 (Instructor)
# ============================================================

INSTRUCTOR_JSON_EXAMPLE = '''
import instructor
from openai import OpenAI
from pydantic import BaseModel

# 啟用 instructor
client = instructor.from_openai(OpenAI())

# 定義輸出模型
class UserInfo(BaseModel):
    name: str
    age: int
    email: str

# 調用 API
user = client.chat.completions.create(
    model="gpt-3.5-turbo",
    response_model=UserInfo,
    messages=[
        {"role": "user", "content": "生成一個名為 John 的用戶資料"}
    ]
)

print(user.name)   # John
print(user.age)    # 25
print(user.email)  # john@example.com
'''


# ============================================================
# 2. Outlines JSON 生成
# ============================================================

OUTLINES_JSON_EXAMPLE = '''
import outlines
from pydantic import BaseModel
from typing import List

model = outlines.models.transformers("mistralai/Mistral-7B-v0.1")

class Product(BaseModel):
    name: str
    price: float
    category: str
    tags: List[str]

generator = outlines.generate.json(model, Product)

product = generator("生成一個電子產品的資料：")
print(product.model_dump_json(indent=2))
'''


# ============================================================
# 3. 複雜嵌套結構
# ============================================================

class Address(BaseModel):
    """地址模型"""
    street: str = Field(description="街道")
    city: str = Field(description="城市")
    country: str = Field(description="國家")
    postal_code: str = Field(description="郵遞區號")


class ContactInfo(BaseModel):
    """聯繫信息"""
    email: str = Field(description="電子郵件")
    phone: Optional[str] = Field(None, description="電話號碼")
    address: Address = Field(description="地址")


class Company(BaseModel):
    """公司模型"""
    name: str = Field(description="公司名稱")
    industry: str = Field(description="行業")
    founded_year: int = Field(description="成立年份")
    contact: ContactInfo = Field(description="聯繫方式")
    employees: int = Field(ge=1, description="員工人數")


class Person(BaseModel):
    """人員完整信息"""
    first_name: str = Field(description="名")
    last_name: str = Field(description="姓")
    birth_date: date = Field(description="出生日期")
    contact: ContactInfo = Field(description="聯繫方式")
    company: Optional[Company] = Field(None, description="所屬公司")
    skills: List[str] = Field(default_factory=list, description="技能")


NESTED_JSON_EXAMPLE = '''
import instructor
from openai import OpenAI

client = instructor.from_openai(OpenAI())

# 生成嵌套結構
company = client.chat.completions.create(
    model="gpt-4",
    response_model=Company,
    messages=[
        {"role": "user", "content": "生成一個科技公司的完整資料"}
    ]
)

print(company.model_dump_json(indent=2))
'''


# ============================================================
# 4. 列表生成
# ============================================================

class Task(BaseModel):
    """任務模型"""
    id: int = Field(description="任務ID")
    title: str = Field(description="標題")
    description: str = Field(description="描述")
    priority: str = Field(description="優先級: high/medium/low")
    completed: bool = Field(default=False, description="是否完成")


class TaskList(BaseModel):
    """任務列表"""
    project_name: str = Field(description="專案名稱")
    tasks: List[Task] = Field(description="任務列表")


class ExtractedEntities(BaseModel):
    """提取的實體"""
    people: List[str] = Field(default_factory=list, description="人名")
    organizations: List[str] = Field(default_factory=list, description="組織名")
    locations: List[str] = Field(default_factory=list, description="地點")
    dates: List[str] = Field(default_factory=list, description="日期")


LIST_GENERATION_EXAMPLE = '''
import instructor
from openai import OpenAI
from typing import List
from pydantic import BaseModel

client = instructor.from_openai(OpenAI())

# 生成任務列表
task_list = client.chat.completions.create(
    model="gpt-3.5-turbo",
    response_model=TaskList,
    messages=[
        {"role": "user", "content": "為網站開發專案創建 5 個任務"}
    ]
)

for task in task_list.tasks:
    print(f"[{task.priority}] {task.title}")
'''


# ============================================================
# 5. 枚舉和聯合類型
# ============================================================

class Priority(str, Enum):
    """優先級枚舉"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Status(str, Enum):
    """狀態枚舉"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskWithEnum(BaseModel):
    """帶枚舉的任務"""
    title: str
    priority: Priority
    status: Status
    assignee: Optional[str] = None


class TextContent(BaseModel):
    """文本內容"""
    type: str = "text"
    text: str


class ImageContent(BaseModel):
    """圖片內容"""
    type: str = "image"
    url: str
    alt_text: Optional[str] = None


class Message(BaseModel):
    """消息（聯合類型）"""
    sender: str
    content: Union[TextContent, ImageContent]
    timestamp: datetime


ENUM_EXAMPLE = '''
import instructor
from openai import OpenAI
from enum import Enum
from pydantic import BaseModel

class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

class SentimentAnalysis(BaseModel):
    text: str
    sentiment: Sentiment
    confidence: float

client = instructor.from_openai(OpenAI())

result = client.chat.completions.create(
    model="gpt-3.5-turbo",
    response_model=SentimentAnalysis,
    messages=[
        {"role": "user", "content": "分析: '這個產品非常棒！'"}
    ]
)

print(f"情感: {result.sentiment.value}")
print(f"置信度: {result.confidence}")
'''


# ============================================================
# 6. 帶驗證的模型
# ============================================================

class ValidatedUser(BaseModel):
    """帶驗證的用戶模型"""
    username: str = Field(min_length=3, max_length=20)
    email: str
    age: int = Field(ge=0, le=150)
    website: Optional[str] = None

    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('無效的電子郵件格式')
        return v

    @validator('website')
    def validate_website(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError('網址必須以 http:// 或 https:// 開頭')
        return v


class ProductReview(BaseModel):
    """產品評論"""
    product_name: str
    rating: int = Field(ge=1, le=5, description="評分 1-5")
    review_text: str = Field(min_length=10)
    pros: List[str] = Field(min_items=1)
    cons: List[str] = Field(default_factory=list)
    recommend: bool


VALIDATION_EXAMPLE = '''
import instructor
from openai import OpenAI
from pydantic import BaseModel, Field, validator

class Score(BaseModel):
    value: int = Field(ge=0, le=100)
    category: str

    @validator('category')
    def validate_category(cls, v):
        valid = ['技術', '溝通', '領導力', '創新']
        if v not in valid:
            raise ValueError(f'類別必須是 {valid} 之一')
        return v

client = instructor.from_openai(OpenAI())

# Instructor 會自動重試直到生成有效數據
score = client.chat.completions.create(
    model="gpt-3.5-turbo",
    response_model=Score,
    max_retries=3,
    messages=[
        {"role": "user", "content": "評估技術能力"}
    ]
)
'''


# ============================================================
# 7. 數據提取
# ============================================================

class Invoice(BaseModel):
    """發票信息"""
    invoice_number: str
    date: str
    vendor: str
    items: List[Dict[str, Any]]
    subtotal: float
    tax: float
    total: float


class ResumeInfo(BaseModel):
    """簡歷信息"""
    name: str
    email: Optional[str]
    phone: Optional[str]
    education: List[Dict[str, str]]
    experience: List[Dict[str, str]]
    skills: List[str]


EXTRACTION_EXAMPLE = '''
import instructor
from openai import OpenAI

client = instructor.from_openai(OpenAI())

# 從文本提取發票信息
invoice_text = """
發票號碼: INV-2024-001
日期: 2024-03-15
廠商: ABC 科技有限公司

商品明細:
- 筆記型電腦 x1  $35,000
- 滑鼠 x2        $600

小計: $35,600
稅額: $1,780
總計: $37,380
"""

invoice = client.chat.completions.create(
    model="gpt-3.5-turbo",
    response_model=Invoice,
    messages=[
        {"role": "user", "content": f"從以下文本提取發票信息:\\n\\n{invoice_text}"}
    ]
)

print(f"發票號: {invoice.invoice_number}")
print(f"總金額: ${invoice.total}")
'''


# ============================================================
# 8. 多語言支持
# ============================================================

class MultilingualContent(BaseModel):
    """多語言內容"""
    original_text: str
    detected_language: str
    translations: Dict[str, str]
    keywords: List[str]


MULTILINGUAL_EXAMPLE = '''
import instructor
from openai import OpenAI

client = instructor.from_openai(OpenAI())

content = client.chat.completions.create(
    model="gpt-4",
    response_model=MultilingualContent,
    messages=[
        {"role": "user", "content": """
        分析以下文本，檢測語言並翻譯成英文和日文：
        "人工智能正在改變世界"
        """}
    ]
)

print(f"原文: {content.original_text}")
print(f"語言: {content.detected_language}")
for lang, text in content.translations.items():
    print(f"{lang}: {text}")
'''


# ============================================================
# 使用範例
# ============================================================

def example_basic():
    """範例 1: 基礎 JSON"""
    print("=" * 50)
    print("範例 1: Instructor 基礎 JSON 生成")
    print("=" * 50)
    print(INSTRUCTOR_JSON_EXAMPLE)


def example_outlines():
    """範例 2: Outlines JSON"""
    print("\n" + "=" * 50)
    print("範例 2: Outlines JSON 生成")
    print("=" * 50)
    print(OUTLINES_JSON_EXAMPLE)


def example_nested():
    """範例 3: 嵌套結構"""
    print("\n" + "=" * 50)
    print("範例 3: 嵌套 JSON 結構")
    print("=" * 50)
    print(NESTED_JSON_EXAMPLE)

    print("\n定義的模型結構:")
    print(Company.model_json_schema())


def example_list():
    """範例 4: 列表生成"""
    print("\n" + "=" * 50)
    print("範例 4: 列表 JSON 生成")
    print("=" * 50)
    print(LIST_GENERATION_EXAMPLE)


def example_enum():
    """範例 5: 枚舉類型"""
    print("\n" + "=" * 50)
    print("範例 5: 枚舉和聯合類型")
    print("=" * 50)
    print(ENUM_EXAMPLE)


def example_validation():
    """範例 6: 帶驗證"""
    print("\n" + "=" * 50)
    print("範例 6: 帶驗證的模型")
    print("=" * 50)
    print(VALIDATION_EXAMPLE)


def example_extraction():
    """範例 7: 數據提取"""
    print("\n" + "=" * 50)
    print("範例 7: 結構化數據提取")
    print("=" * 50)
    print(EXTRACTION_EXAMPLE)


def example_multilingual():
    """範例 8: 多語言"""
    print("\n" + "=" * 50)
    print("範例 8: 多語言內容")
    print("=" * 50)
    print(MULTILINGUAL_EXAMPLE)


if __name__ == "__main__":
    print("Instructor/Outlines JSON 生成範例\n")
    example_basic()
    example_outlines()
    example_nested()
    example_list()
    example_enum()
    example_validation()
    example_extraction()
    example_multilingual()

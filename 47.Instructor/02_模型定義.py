"""
Instructor 模型定義示例

這個模塊深入探討如何定義各種複雜的 Pydantic 模型用於數據提取。
涵蓋了從簡單到複雜的各種模型定義技巧。

主要內容：
1. 基礎字段類型和約束
2. 嵌套模型定義
3. 枚舉和字面值類型
4. 可選字段和默認值
5. 字段描述和元數據
6. 複雜類型（Union、泛型等）

作者: Instructor 示例
日期: 2025-01-01
"""

import os
from datetime import datetime, date
from typing import Optional, List, Dict, Union, Literal, Annotated
from enum import Enum
from pydantic import (
    BaseModel,
    Field,
    EmailStr,
    HttpUrl,
    constr,
    conint,
    confloat,
    field_validator,
    model_validator
)
import instructor
from openai import OpenAI


# ============================================================================
# 枚舉類型定義
# ============================================================================

class Priority(str, Enum):
    """任務優先級枚舉"""
    LOW = "低"
    MEDIUM = "中"
    HIGH = "高"
    URGENT = "緊急"


class Status(str, Enum):
    """任務狀態枚舉"""
    TODO = "待辦"
    IN_PROGRESS = "進行中"
    REVIEW = "審核中"
    DONE = "已完成"
    CANCELLED = "已取消"


class Department(str, Enum):
    """部門枚舉"""
    ENGINEERING = "工程部"
    SALES = "銷售部"
    MARKETING = "市場部"
    HR = "人力資源部"
    FINANCE = "財務部"


class Sentiment(str, Enum):
    """情感枚舉"""
    POSITIVE = "正面"
    NEGATIVE = "負面"
    NEUTRAL = "中性"


# ============================================================================
# 基礎字段類型示例
# ============================================================================

class PersonalInfo(BaseModel):
    """個人信息模型 - 展示各種基礎字段類型

    這個模型展示了如何使用 Pydantic 的各種字段類型和約束。
    """
    # 字符串字段
    name: str = Field(
        description="姓名",
        min_length=2,
        max_length=50
    )

    # 整數字段（帶範圍約束）
    age: int = Field(
        description="年齡",
        ge=0,  # 大於等於 0
        le=150  # 小於等於 150
    )

    # 浮點數字段
    height: float = Field(
        description="身高（米）",
        gt=0,  # 大於 0
        lt=3.0  # 小於 3.0
    )

    # 布爾字段
    is_active: bool = Field(
        default=True,
        description="是否活躍"
    )

    # 郵箱字段（自動驗證格式）
    email: EmailStr = Field(
        description="電子郵件地址"
    )

    # 可選字段
    phone: Optional[str] = Field(
        default=None,
        description="電話號碼"
    )

    # 日期字段
    birth_date: Optional[date] = Field(
        default=None,
        description="出生日期"
    )


class ConstrainedTypes(BaseModel):
    """受約束的類型示例

    展示如何使用 Pydantic 的約束類型。
    """
    # 受約束的字符串（長度限制）
    username: constr(min_length=3, max_length=20) = Field(
        description="用戶名（3-20個字符）"
    )

    # 受約束的字符串（正則表達式）
    postal_code: constr(pattern=r'^\d{5}(-\d{4})?$') = Field(
        description="郵政編碼（美國格式）"
    )

    # 受約束的整數
    rating: conint(ge=1, le=5) = Field(
        description="評分（1-5星）"
    )

    # 受約束的浮點數
    percentage: confloat(ge=0.0, le=100.0) = Field(
        description="百分比（0-100）"
    )

    # URL 字段
    website: HttpUrl = Field(
        description="網站 URL"
    )


# ============================================================================
# 嵌套模型定義
# ============================================================================

class Address(BaseModel):
    """地址模型"""
    street: str = Field(description="街道地址")
    city: str = Field(description="城市")
    state: str = Field(description="州/省")
    country: str = Field(description="國家")
    postal_code: str = Field(description="郵政編碼")

    def full_address(self) -> str:
        """獲取完整地址字符串"""
        return f"{self.street}, {self.city}, {self.state} {self.postal_code}, {self.country}"


class Company(BaseModel):
    """公司信息模型"""
    name: str = Field(description="公司名稱")
    industry: str = Field(description="所屬行業")
    employee_count: int = Field(description="員工數量", ge=1)
    website: Optional[HttpUrl] = Field(default=None, description="公司網站")
    address: Address = Field(description="公司地址")


class Employee(BaseModel):
    """員工信息模型 - 嵌套模型示例"""
    name: str = Field(description="員工姓名")
    employee_id: str = Field(description="員工ID")
    email: EmailStr = Field(description="電子郵件")
    department: Department = Field(description="所屬部門")
    position: str = Field(description="職位")
    salary: float = Field(description="年薪（美元）", gt=0)
    hire_date: date = Field(description="入職日期")
    manager: Optional['Employee'] = Field(
        default=None,
        description="直屬經理"
    )
    company: Company = Field(description="所屬公司")

    class Config:
        """配置：支持自引用"""
        # Pydantic v2 中自動支持，無需特殊配置


class TeamProject(BaseModel):
    """團隊項目模型 - 多層嵌套示例"""
    project_name: str = Field(description="項目名稱")
    description: str = Field(description="項目描述")
    team_lead: Employee = Field(description="項目負責人")
    team_members: List[Employee] = Field(
        description="團隊成員列表",
        min_length=1
    )
    start_date: date = Field(description="開始日期")
    end_date: Optional[date] = Field(default=None, description="結束日期")
    budget: float = Field(description="項目預算（美元）", gt=0)


# ============================================================================
# 集合類型模型
# ============================================================================

class Task(BaseModel):
    """任務模型"""
    title: str = Field(description="任務標題")
    description: str = Field(description="任務描述")
    priority: Priority = Field(description="優先級")
    status: Status = Field(default=Status.TODO, description="當前狀態")
    assignee: str = Field(description="負責人")
    tags: List[str] = Field(
        default_factory=list,
        description="任務標籤"
    )
    due_date: Optional[date] = Field(default=None, description="截止日期")


class TaskList(BaseModel):
    """任務列表模型 - 展示列表類型"""
    project_name: str = Field(description="項目名稱")
    tasks: List[Task] = Field(
        description="任務列表",
        min_length=1
    )
    total_tasks: int = Field(description="總任務數")

    @model_validator(mode='after')
    def validate_task_count(self):
        """驗證任務數量是否匹配"""
        if len(self.tasks) != self.total_tasks:
            raise ValueError(
                f"任務數量不匹配：聲明 {self.total_tasks}，實際 {len(self.tasks)}"
            )
        return self


class KeyValueData(BaseModel):
    """鍵值對數據模型 - 展示字典類型"""
    name: str = Field(description="數據集名稱")
    metadata: Dict[str, str] = Field(
        description="元數據鍵值對"
    )
    metrics: Dict[str, float] = Field(
        description="指標數據"
    )
    settings: Dict[str, Union[str, int, bool]] = Field(
        description="配置設置"
    )


# ============================================================================
# Union 和可選類型
# ============================================================================

class TextContent(BaseModel):
    """文本內容"""
    type: Literal["text"] = "text"
    content: str = Field(description="文本內容")


class ImageContent(BaseModel):
    """圖片內容"""
    type: Literal["image"] = "image"
    url: HttpUrl = Field(description="圖片 URL")
    alt_text: Optional[str] = Field(default=None, description="替代文本")


class VideoContent(BaseModel):
    """視頻內容"""
    type: Literal["video"] = "video"
    url: HttpUrl = Field(description="視頻 URL")
    duration: int = Field(description="時長（秒）", gt=0)


class MediaPost(BaseModel):
    """媒體帖子 - 展示 Union 類型

    一個帖子可以包含文本、圖片或視頻內容。
    """
    title: str = Field(description="帖子標題")
    author: str = Field(description="作者")
    content: Union[TextContent, ImageContent, VideoContent] = Field(
        description="帖子內容（可以是文本、圖片或視頻）"
    )
    created_at: datetime = Field(description="創建時間")
    likes: int = Field(default=0, description="點讚數", ge=0)


# ============================================================================
# 複雜業務模型示例
# ============================================================================

class ProductFeature(BaseModel):
    """產品特性"""
    name: str = Field(description="特性名稱")
    description: str = Field(description="特性描述")
    is_premium: bool = Field(default=False, description="是否為高級特性")


class PricingTier(BaseModel):
    """定價層級"""
    name: str = Field(description="層級名稱")
    price: float = Field(description="月費（美元）", ge=0)
    features: List[str] = Field(description="包含的特性列表")
    max_users: int = Field(description="最大用戶數", gt=0)


class SaaSProduct(BaseModel):
    """SaaS 產品模型 - 複雜業務模型示例"""
    product_name: str = Field(description="產品名稱")
    tagline: str = Field(description="產品標語")
    description: str = Field(description="產品描述")
    features: List[ProductFeature] = Field(
        description="產品特性列表",
        min_length=1
    )
    pricing_tiers: List[PricingTier] = Field(
        description="定價方案",
        min_length=1
    )
    target_audience: List[str] = Field(
        description="目標用戶群體"
    )
    tech_stack: List[str] = Field(
        description="技術棧"
    )
    competitors: List[str] = Field(
        default_factory=list,
        description="競爭對手"
    )


class Review(BaseModel):
    """評論模型"""
    reviewer_name: str = Field(description="評論者姓名")
    rating: conint(ge=1, le=5) = Field(description="評分（1-5星）")
    sentiment: Sentiment = Field(description="情感傾向")
    title: str = Field(description="評論標題")
    content: str = Field(description="評論內容")
    pros: List[str] = Field(description="優點列表")
    cons: List[str] = Field(description="缺點列表")
    verified_purchase: bool = Field(
        default=False,
        description="是否為認證購買"
    )
    helpful_count: int = Field(
        default=0,
        description="有用計數",
        ge=0
    )


# ============================================================================
# 使用示例函數
# ============================================================================

def setup_client():
    """設置 Instructor 客戶端"""
    api_key = os.getenv("OPENAI_API_KEY", "sk-placeholder")
    openai_client = OpenAI(api_key=api_key)
    return instructor.from_openai(openai_client)


def extract_personal_info(client, text: str):
    """提取個人信息示例"""
    print(f"\n{'='*60}")
    print("提取個人信息（基礎字段類型）")
    print(f"{'='*60}")

    person = client.chat.completions.create(
        model="gpt-4",
        response_model=PersonalInfo,
        messages=[
            {"role": "user", "content": f"提取個人信息：\n{text}"}
        ]
    )

    print(f"姓名: {person.name}")
    print(f"年齡: {person.age}")
    print(f"身高: {person.height}m")
    print(f"郵箱: {person.email}")
    print(f"電話: {person.phone or '未提供'}")

    return person


def extract_employee_info(client, text: str):
    """提取員工信息示例（嵌套模型）"""
    print(f"\n{'='*60}")
    print("提取員工信息（嵌套模型）")
    print(f"{'='*60}")

    employee = client.chat.completions.create(
        model="gpt-4",
        response_model=Employee,
        messages=[
            {"role": "user", "content": f"提取員工信息：\n{text}"}
        ]
    )

    print(f"姓名: {employee.name}")
    print(f"職位: {employee.position}")
    print(f"部門: {employee.department.value}")
    print(f"公司: {employee.company.name}")
    print(f"公司地址: {employee.company.address.full_address()}")

    return employee


def extract_task_list(client, text: str):
    """提取任務列表示例（集合類型）"""
    print(f"\n{'='*60}")
    print("提取任務列表（集合類型）")
    print(f"{'='*60}")

    task_list = client.chat.completions.create(
        model="gpt-4",
        response_model=TaskList,
        messages=[
            {"role": "user", "content": f"提取任務列表：\n{text}"}
        ]
    )

    print(f"項目: {task_list.project_name}")
    print(f"總任務數: {task_list.total_tasks}")
    print("\n任務詳情:")
    for i, task in enumerate(task_list.tasks, 1):
        print(f"\n  {i}. {task.title}")
        print(f"     優先級: {task.priority.value}")
        print(f"     狀態: {task.status.value}")
        print(f"     負責人: {task.assignee}")

    return task_list


def extract_media_post(client, text: str):
    """提取媒體帖子示例（Union 類型）"""
    print(f"\n{'='*60}")
    print("提取媒體帖子（Union 類型）")
    print(f"{'='*60}")

    post = client.chat.completions.create(
        model="gpt-4",
        response_model=MediaPost,
        messages=[
            {"role": "user", "content": f"提取帖子信息：\n{text}"}
        ]
    )

    print(f"標題: {post.title}")
    print(f"作者: {post.author}")
    print(f"內容類型: {post.content.type}")
    print(f"點讚數: {post.likes}")

    return post


def extract_product_review(client, text: str):
    """提取產品評論示例（複雜模型）"""
    print(f"\n{'='*60}")
    print("提取產品評論（複雜模型）")
    print(f"{'='*60}")

    review = client.chat.completions.create(
        model="gpt-4",
        response_model=Review,
        messages=[
            {"role": "user", "content": f"提取評論信息：\n{text}"}
        ]
    )

    print(f"評論者: {review.reviewer_name}")
    print(f"評分: {'⭐' * review.rating}")
    print(f"情感: {review.sentiment.value}")
    print(f"標題: {review.title}")
    print(f"\n優點:")
    for pro in review.pros:
        print(f"  + {pro}")
    print(f"\n缺點:")
    for con in review.cons:
        print(f"  - {con}")

    return review


def extract_saas_product(client, text: str):
    """提取 SaaS 產品信息（複雜業務模型）"""
    print(f"\n{'='*60}")
    print("提取 SaaS 產品信息（複雜業務模型）")
    print(f"{'='*60}")

    product = client.chat.completions.create(
        model="gpt-4",
        response_model=SaaSProduct,
        messages=[
            {"role": "user", "content": f"提取產品信息：\n{text}"}
        ]
    )

    print(f"產品: {product.product_name}")
    print(f"標語: {product.tagline}")
    print(f"\n特性數量: {len(product.features)}")
    print(f"定價方案: {len(product.pricing_tiers)} 個層級")
    print(f"目標用戶: {', '.join(product.target_audience)}")

    return product


# ============================================================================
# 主程序
# ============================================================================

def main():
    """主函數 - 運行所有示例"""
    print("="*60)
    print("Instructor 模型定義示例")
    print("="*60)

    client = setup_client()

    # 示例 1: 基礎字段類型
    person_text = """
    姓名：張小明
    年齡：28歲
    身高：1.75米
    郵箱：zhangxiaoming@email.com
    電話：138-0000-1234
    出生日期：1996-05-15
    """
    extract_personal_info(client, person_text)

    # 示例 2: 嵌套模型
    employee_text = """
    員工：李工程師
    員工ID：EMP001
    郵箱：li.engineer@techcorp.com
    部門：工程部
    職位：高級軟件工程師
    年薪：$120,000
    入職日期：2020-03-15

    公司：科技創新公司
    行業：軟件開發
    員工數：500人
    網站：https://techcorp.com
    地址：中關村大街1號，北京，北京市，100000，中國
    """
    extract_employee_info(client, employee_text)

    # 示例 3: 集合類型
    tasks_text = """
    項目：網站重構項目

    任務1：設計新UI界面
    描述：創建現代化的用戶界面
    優先級：高
    負責人：設計師小王
    標籤：設計, UI/UX
    截止日期：2025-02-01

    任務2：後端API開發
    描述：開發RESTful API
    優先級：緊急
    狀態：進行中
    負責人：工程師小李
    標籤：後端, API
    截止日期：2025-01-25

    總共2個任務
    """
    extract_task_list(client, tasks_text)

    # 示例 4: Union 類型
    media_text = """
    標題：人工智能的未來
    作者：科技評論員
    創建時間：2025-01-15 10:30:00
    點讚數：156

    這是一篇關於人工智能發展趨勢的文章。
    文章探討了AI技術在各個領域的應用前景。
    """
    extract_media_post(client, media_text)

    # 示例 5: 複雜模型
    review_text = """
    評論者：科技愛好者小張
    評分：5星

    標題：非常好用的產品！

    這個產品真的很棒。界面設計優秀，功能強大且易用。
    客服響應迅速，技術支持專業。

    優點：
    - 界面簡潔美觀
    - 功能強大完整
    - 性能穩定可靠
    - 客服服務優質

    缺點：
    - 價格稍微偏高
    - 學習曲線略陡

    已認證購買
    128人認為有用
    """
    extract_product_review(client, review_text)

    print("\n" + "="*60)
    print("所有示例運行完成！")
    print("="*60)
    print("\n模型定義要點總結:")
    print("1. 使用明確的字段類型和約束")
    print("2. 添加詳細的字段描述")
    print("3. 合理使用嵌套模型組織數據")
    print("4. 利用枚舉類型限制選項")
    print("5. 使用 Union 類型處理多種可能")


if __name__ == "__main__":
    main()

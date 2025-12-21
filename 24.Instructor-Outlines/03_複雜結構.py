"""
複雜結構範例
==============

本範例展示如何使用 Instructor 處理複雜的嵌套資料結構：
1. 嵌套 Pydantic 模型
2. 列表和字典結構
3. 可選欄位和預設值
4. 遞迴結構
5. 組合模型
6. 真實世界的複雜案例

學習如何建模和提取複雜的結構化資料。
"""

from typing import List, Dict, Optional, Union, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
import instructor

# ============================================================================
# 範例 1：基本嵌套結構
# ============================================================================

def example_nested_models():
    """展示基本的嵌套模型結構"""
    print("=" * 60)
    print("範例 1：基本嵌套結構")
    print("=" * 60)

    try:
        from openai import OpenAI

        # 定義地址模型
        class Address(BaseModel):
            """地址資訊"""
            street: str = Field(description="街道地址")
            city: str = Field(description="城市")
            postal_code: str = Field(description="郵遞區號")
            country: str = Field(default="台灣", description="國家")

        # 定義公司模型
        class Company(BaseModel):
            """公司資訊"""
            name: str = Field(description="公司名稱")
            industry: str = Field(description="產業類別")
            employee_count: int = Field(description="員工人數")
            address: Address = Field(description="公司地址")

        # 定義員工模型（包含公司資訊）
        class Employee(BaseModel):
            """員工資訊"""
            name: str = Field(description="員工姓名")
            position: str = Field(description="職位")
            salary: float = Field(description="薪資")
            company: Company = Field(description="所屬公司")
            home_address: Optional[Address] = Field(None, description="家庭地址")

        client = instructor.from_openai(OpenAI())

        employee = client.chat.completions.create(
            model="gpt-3.5-turbo",
            response_model=Employee,
            messages=[
                {
                    "role": "user",
                    "content": """
                    員工資訊：
                    王大明是台積電的資深工程師，月薪 12 萬元。
                    台積電是半導體產業的公司，有 7 萬名員工，
                    公司地址在新竹市力行路 8 號，郵遞區號 300。
                    """
                }
            ]
        )

        print("\n✅ 提取的員工資訊：")
        print(f"姓名：{employee.name}")
        print(f"職位：{employee.position}")
        print(f"薪資：NT$ {employee.salary:,.0f}")
        print(f"\n公司資訊：")
        print(f"  名稱：{employee.company.name}")
        print(f"  產業：{employee.company.industry}")
        print(f"  員工數：{employee.company.employee_count:,}")
        print(f"  地址：{employee.company.address.city}{employee.company.address.street}")

    except Exception as e:
        print(f"❌ 錯誤：{e}")


# ============================================================================
# 範例 2：列表嵌套
# ============================================================================

def example_list_nesting():
    """展示包含列表的複雜結構"""
    print("\n" + "=" * 60)
    print("範例 2：列表嵌套")
    print("=" * 60)

    try:
        from openai import OpenAI

        # 定義課程模型
        class Course(BaseModel):
            """課程資訊"""
            code: str = Field(description="課程代碼")
            name: str = Field(description="課程名稱")
            credits: int = Field(description="學分數")
            grade: Optional[float] = Field(None, description="成績")

        # 定義學期模型
        class Semester(BaseModel):
            """學期資訊"""
            year: int = Field(description="學年度")
            term: str = Field(description="學期（上學期/下學期）")
            courses: List[Course] = Field(description="修課列表")

            def calculate_gpa(self) -> float:
                """計算 GPA"""
                total_points = sum(
                    c.grade * c.credits
                    for c in self.courses
                    if c.grade is not None
                )
                total_credits = sum(
                    c.credits
                    for c in self.courses
                    if c.grade is not None
                )
                return total_points / total_credits if total_credits > 0 else 0.0

        # 定義學生模型
        class Student(BaseModel):
            """學生資訊"""
            student_id: str = Field(description="學號")
            name: str = Field(description="姓名")
            major: str = Field(description="主修")
            semesters: List[Semester] = Field(description="歷年學期成績")

        client = instructor.from_openai(OpenAI())

        student = client.chat.completions.create(
            model="gpt-3.5-turbo",
            response_model=Student,
            messages=[
                {
                    "role": "user",
                    "content": """
                    學生：王小明，學號 A12345678，資工系

                    113 學年上學期：
                    - CS101 程式設計 3 學分，成績 85
                    - MA201 微積分 4 學分，成績 78
                    - EN101 英文 2 學分，成績 90

                    113 學年下學期：
                    - CS102 資料結構 3 學分，成績 88
                    - CS201 演算法 3 學分，成績 92
                    """
                }
            ]
        )

        print("\n✅ 學生成績單：")
        print(f"學號：{student.student_id}")
        print(f"姓名：{student.name}")
        print(f"主修：{student.major}\n")

        for semester in student.semesters:
            print(f"📚 {semester.year} 學年度 {semester.term}：")
            for course in semester.courses:
                grade_str = f"{course.grade:.1f}" if course.grade else "未評分"
                print(f"  - {course.code} {course.name} ({course.credits} 學分)：{grade_str}")
            gpa = semester.calculate_gpa()
            print(f"  GPA：{gpa:.2f}\n")

    except Exception as e:
        print(f"❌ 錯誤：{e}")


# ============================================================================
# 範例 3：字典和動態欄位
# ============================================================================

def example_dict_fields():
    """展示使用字典處理動態欄位"""
    print("\n" + "=" * 60)
    print("範例 3：字典和動態欄位")
    print("=" * 60)

    try:
        from openai import OpenAI

        class Product(BaseModel):
            """產品資訊"""
            name: str = Field(description="產品名稱")
            category: str = Field(description="產品類別")
            price: float = Field(description="價格")
            # 使用字典處理動態屬性
            specifications: Dict[str, Any] = Field(
                description="產品規格（鍵值對）"
            )
            # 多語言支援
            descriptions: Dict[str, str] = Field(
                description="多語言描述"
            )
            # 庫存資訊（按倉庫）
            inventory: Dict[str, int] = Field(
                description="各倉庫庫存數量"
            )

        client = instructor.from_openai(OpenAI())

        product = client.chat.completions.create(
            model="gpt-3.5-turbo",
            response_model=Product,
            messages=[
                {
                    "role": "user",
                    "content": """
                    產品：iPhone 15 Pro
                    類別：智慧型手機
                    價格：36900 元

                    規格：
                    - 螢幕：6.1 吋
                    - 處理器：A17 Pro
                    - 記憶體：8GB
                    - 儲存空間：256GB
                    - 顏色：鈦金屬藍

                    描述：
                    - 繁體中文：全新設計的專業級智慧型手機
                    - 英文：Professional smartphone with innovative design
                    - 日文：革新的なデザインのプロフェッショナルスマートフォン

                    庫存：
                    - 台北倉：50 台
                    - 台中倉：30 台
                    - 高雄倉：25 台
                    """
                }
            ]
        )

        print("\n✅ 產品資訊：")
        print(f"名稱：{product.name}")
        print(f"類別：{product.category}")
        print(f"價格：NT$ {product.price:,.0f}")

        print(f"\n規格：")
        for key, value in product.specifications.items():
            print(f"  - {key}：{value}")

        print(f"\n多語言描述：")
        for lang, desc in product.descriptions.items():
            print(f"  - {lang}：{desc}")

        print(f"\n庫存分布：")
        total_stock = 0
        for warehouse, stock in product.inventory.items():
            print(f"  - {warehouse}：{stock} 台")
            total_stock += stock
        print(f"  總計：{total_stock} 台")

    except Exception as e:
        print(f"❌ 錯誤：{e}")


# ============================================================================
# 範例 4：使用 Enum 和 Union
# ============================================================================

def example_enum_union():
    """使用枚舉和聯合型別"""
    print("\n" + "=" * 60)
    print("範例 4：Enum 和 Union")
    print("=" * 60)

    try:
        from openai import OpenAI

        # 定義枚舉
        class OrderStatus(str, Enum):
            """訂單狀態"""
            PENDING = "pending"
            PROCESSING = "processing"
            SHIPPED = "shipped"
            DELIVERED = "delivered"
            CANCELLED = "cancelled"

        class PaymentMethod(str, Enum):
            """付款方式"""
            CREDIT_CARD = "credit_card"
            DEBIT_CARD = "debit_card"
            PAYPAL = "paypal"
            CASH = "cash"

        # 定義付款資訊（不同付款方式）
        class CreditCardPayment(BaseModel):
            """信用卡付款"""
            method: str = Field(default="credit_card")
            card_number: str = Field(description="卡號（遮罩）")
            expiry: str = Field(description="有效期限")

        class PayPalPayment(BaseModel):
            """PayPal 付款"""
            method: str = Field(default="paypal")
            email: str = Field(description="PayPal 帳號")

        class CashPayment(BaseModel):
            """現金付款"""
            method: str = Field(default="cash")
            amount: float = Field(description="金額")

        # 定義訂單項目
        class OrderItem(BaseModel):
            """訂單項目"""
            product_name: str = Field(description="產品名稱")
            quantity: int = Field(description="數量")
            unit_price: float = Field(description="單價")

        # 定義訂單
        class Order(BaseModel):
            """訂單"""
            order_id: str = Field(description="訂單編號")
            customer_name: str = Field(description="客戶姓名")
            status: OrderStatus = Field(description="訂單狀態")
            items: List[OrderItem] = Field(description="訂單項目")
            payment: Union[CreditCardPayment, PayPalPayment, CashPayment] = Field(
                description="付款資訊"
            )

            def calculate_total(self) -> float:
                """計算總金額"""
                return sum(item.quantity * item.unit_price for item in self.items)

        client = instructor.from_openai(OpenAI())

        order = client.chat.completions.create(
            model="gpt-3.5-turbo",
            response_model=Order,
            messages=[
                {
                    "role": "user",
                    "content": """
                    訂單編號：ORD-2025-001
                    客戶：李小華
                    狀態：已出貨

                    訂單內容：
                    - MacBook Pro x 1 台，單價 72900 元
                    - AirPods Pro x 2 個，單價 7490 元

                    付款方式：信用卡，卡號 **** **** **** 1234，有效期 12/26
                    """
                }
            ]
        )

        print("\n✅ 訂單資訊：")
        print(f"訂單編號：{order.order_id}")
        print(f"客戶：{order.customer_name}")
        print(f"狀態：{order.status.value}")

        print(f"\n訂單項目：")
        for item in order.items:
            subtotal = item.quantity * item.unit_price
            print(f"  - {item.product_name} x {item.quantity}")
            print(f"    單價：NT$ {item.unit_price:,.0f}，小計：NT$ {subtotal:,.0f}")

        total = order.calculate_total()
        print(f"\n總金額：NT$ {total:,.0f}")

        print(f"\n付款方式：", end="")
        if isinstance(order.payment, CreditCardPayment):
            print(f"信用卡 {order.payment.card_number}")
        elif isinstance(order.payment, PayPalPayment):
            print(f"PayPal ({order.payment.email})")
        elif isinstance(order.payment, CashPayment):
            print(f"現金 NT$ {order.payment.amount:,.0f}")

    except Exception as e:
        print(f"❌ 錯誤：{e}")


# ============================================================================
# 範例 5：遞迴結構（樹狀結構）
# ============================================================================

def example_recursive_structure():
    """展示遞迴的樹狀結構"""
    print("\n" + "=" * 60)
    print("範例 5：遞迴結構（組織架構）")
    print("=" * 60)

    try:
        from openai import OpenAI

        # 定義組織節點（遞迴結構）
        class OrgNode(BaseModel):
            """組織節點"""
            name: str = Field(description="部門或人員名稱")
            role: str = Field(description="職位或部門類型")
            direct_reports: List['OrgNode'] = Field(
                default=[],
                description="直接下屬"
            )

            def count_total_employees(self) -> int:
                """計算此節點下的總人數"""
                count = 1  # 自己
                for report in self.direct_reports:
                    count += report.count_total_employees()
                return count

            def print_tree(self, level: int = 0):
                """印出組織樹"""
                indent = "  " * level
                print(f"{indent}{'└─ ' if level > 0 else ''}{self.name} ({self.role})")
                for report in self.direct_reports:
                    report.print_tree(level + 1)

        # 需要更新模型引用
        OrgNode.model_rebuild()

        client = instructor.from_openai(OpenAI())

        org = client.chat.completions.create(
            model="gpt-3.5-turbo",
            response_model=OrgNode,
            messages=[
                {
                    "role": "user",
                    "content": """
                    提取組織架構：

                    總經理 王大明
                    ├─ 技術長 李小華
                    │  ├─ 前端主管 陳小明
                    │  │  ├─ 前端工程師 張三
                    │  │  └─ 前端工程師 李四
                    │  └─ 後端主管 林小美
                    │     ├─ 後端工程師 王五
                    │     └─ 後端工程師 趙六
                    └─ 營運長 周小強
                       ├─ 行銷經理 吳七
                       └─ 業務經理 鄭八
                    """
                }
            ]
        )

        print("\n✅ 組織架構：")
        org.print_tree()
        print(f"\n總人數：{org.count_total_employees()} 人")

    except Exception as e:
        print(f"❌ 錯誤：{e}")


# ============================================================================
# 範例 6：真實案例 - 部落格文章
# ============================================================================

def example_blog_post():
    """真實案例：複雜的部落格文章結構"""
    print("\n" + "=" * 60)
    print("範例 6：真實案例 - 部落格文章")
    print("=" * 60)

    try:
        from openai import OpenAI

        # 定義作者
        class Author(BaseModel):
            """作者資訊"""
            name: str = Field(description="作者姓名")
            bio: str = Field(description="作者簡介")
            email: str = Field(description="聯絡 Email")

        # 定義留言
        class Comment(BaseModel):
            """留言"""
            author: str = Field(description="留言者")
            content: str = Field(description="留言內容")
            likes: int = Field(default=0, description="按讚數")

        # 定義標籤
        class Tag(BaseModel):
            """標籤"""
            name: str = Field(description="標籤名稱")
            color: str = Field(description="標籤顏色")

        # 定義文章區塊
        class ContentBlock(BaseModel):
            """內容區塊"""
            type: str = Field(description="區塊類型（text/image/code）")
            content: str = Field(description="區塊內容")
            caption: Optional[str] = Field(None, description="說明文字")

        # 定義部落格文章
        class BlogPost(BaseModel):
            """部落格文章"""
            title: str = Field(description="文章標題")
            author: Author = Field(description="作者")
            published_date: str = Field(description="發布日期")
            tags: List[Tag] = Field(description="標籤列表")
            content_blocks: List[ContentBlock] = Field(description="內容區塊")
            comments: List[Comment] = Field(default=[], description="留言列表")
            views: int = Field(default=0, description="瀏覽次數")
            likes: int = Field(default=0, description="按讚數")

        client = instructor.from_openai(OpenAI())

        blog_post = client.chat.completions.create(
            model="gpt-4o-mini",
            response_model=BlogPost,
            messages=[
                {
                    "role": "user",
                    "content": """
                    提取文章資訊：

                    標題：Python 非同步程式設計完全指南
                    作者：張工程師，Python 專家，擅長後端開發，email: zhang@example.com
                    發布日期：2025-12-15
                    瀏覽：1250 次，讚：95 個

                    標籤：
                    - Python（藍色）
                    - 非同步（綠色）
                    - 教學（橙色）

                    內容：
                    1. 文字段落：非同步程式設計是現代 Python 開發的重要技能...
                    2. 程式碼範例：async def main(): await asyncio.sleep(1)
                    3. 圖片：架構圖，說明：非同步執行流程

                    留言：
                    - 王小明：寫得很清楚，謝謝分享！（5 讚）
                    - 李小華：能再多一些實例嗎？（3 讚）
                    """
                }
            ]
        )

        print("\n✅ 部落格文章：")
        print(f"📰 {blog_post.title}")
        print(f"✍️  作者：{blog_post.author.name} ({blog_post.author.email})")
        print(f"   {blog_post.author.bio}")
        print(f"📅 發布：{blog_post.published_date}")
        print(f"📊 瀏覽：{blog_post.views} 次，讚：{blog_post.likes} 個")

        print(f"\n🏷️  標籤：", end="")
        print(", ".join([f"{tag.name}({tag.color})" for tag in blog_post.tags]))

        print(f"\n📝 內容：")
        for i, block in enumerate(blog_post.content_blocks, 1):
            print(f"  {i}. [{block.type}] {block.content[:50]}...")
            if block.caption:
                print(f"     說明：{block.caption}")

        print(f"\n💬 留言 ({len(blog_post.comments)} 則)：")
        for comment in blog_post.comments:
            print(f"  - {comment.author}：{comment.content}")
            print(f"    👍 {comment.likes}")

    except Exception as e:
        print(f"❌ 錯誤：{e}")


# ============================================================================
# 主程式
# ============================================================================

def main():
    """執行所有範例"""
    print("\n" + "🎯" * 30)
    print("複雜結構範例")
    print("🎯" * 30)

    print("\n📝 關於複雜結構")
    print("-" * 60)
    print("學習如何使用 Instructor 處理真實世界的複雜資料：")
    print("\n結構類型：")
    print("✅ 嵌套模型（模型中包含其他模型）")
    print("✅ 列表和集合（處理多個相關物件）")
    print("✅ 字典和動態欄位（靈活的鍵值對）")
    print("✅ 枚舉和聯合型別（多種可能的型別）")
    print("✅ 遞迴結構（樹狀或圖狀資料）")
    print("✅ 真實案例（結合多種結構）")
    print("-" * 60)

    # 執行所有範例
    example_nested_models()
    example_list_nesting()
    example_dict_fields()
    example_enum_union()
    example_recursive_structure()
    example_blog_post()

    print("\n" + "=" * 60)
    print("✅ 所有複雜結構範例執行完畢！")
    print("=" * 60)
    print("\n💡 設計複雜結構的技巧：")
    print("1. 由上而下設計：從最外層模型開始")
    print("2. 單一職責：每個模型專注於一個概念")
    print("3. 適當抽象：提取共同特徵為基礎模型")
    print("4. 使用型別提示：增強代碼可讀性")
    print("5. 文件化：為每個欄位添加 description")


if __name__ == "__main__":
    main()

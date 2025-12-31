"""
Instructor 列表提取示例

這個模塊專注於從文本中提取各種類型的列表和可迭代數據。
展示了處理動態長度列表、批量提取和集合操作的技巧。

主要內容：
1. 簡單列表提取
2. 結構化對象列表
3. 動態長度列表
4. 嵌套列表結構
5. 批量數據處理
6. 列表去重和過濾

作者: Instructor 示例
日期: 2025-01-01
"""

import os
from typing import List, Optional, Set, Dict
from datetime import date
from pydantic import BaseModel, Field, field_validator
import instructor
from openai import OpenAI


# ============================================================================
# 簡單列表模型
# ============================================================================

class KeywordList(BaseModel):
    """關鍵詞列表模型"""
    topic: str = Field(description="主題")
    keywords: List[str] = Field(
        description="關鍵詞列表",
        min_length=3,
        max_length=20
    )

    @field_validator('keywords')
    @classmethod
    def remove_duplicates(cls, v: List[str]) -> List[str]:
        """移除重複的關鍵詞"""
        seen = set()
        unique = []
        for keyword in v:
            keyword_lower = keyword.lower()
            if keyword_lower not in seen:
                seen.add(keyword_lower)
                unique.append(keyword)
        return unique


class FeatureList(BaseModel):
    """功能特性列表"""
    product_name: str = Field(description="產品名稱")
    features: List[str] = Field(
        description="功能特性列表",
        min_length=1
    )
    pros: List[str] = Field(
        description="優點列表",
        min_length=1
    )
    cons: List[str] = Field(
        default_factory=list,
        description="缺點列表"
    )


class StepByStepGuide(BaseModel):
    """步驟指南列表"""
    title: str = Field(description="指南標題")
    steps: List[str] = Field(
        description="步驟列表（按順序）",
        min_length=2
    )
    tips: List[str] = Field(
        default_factory=list,
        description="提示列表"
    )


# ============================================================================
# 結構化對象列表
# ============================================================================

class ContactInfo(BaseModel):
    """聯繫信息"""
    name: str = Field(description="姓名")
    email: str = Field(description="郵箱")
    phone: Optional[str] = Field(default=None, description="電話")
    company: Optional[str] = Field(default=None, description="公司")


class ContactList(BaseModel):
    """聯繫人列表"""
    source: str = Field(description="來源（會議、活動等）")
    contacts: List[ContactInfo] = Field(
        description="聯繫人列表",
        min_length=1
    )
    total_count: int = Field(description="總數")

    @field_validator('total_count')
    @classmethod
    def validate_count(cls, v: int, info) -> int:
        """驗證總數是否匹配"""
        if 'contacts' in info.data:
            actual = len(info.data['contacts'])
            if v != actual:
                raise ValueError(f'總數不匹配：聲明{v}，實際{actual}')
        return v


class BookInfo(BaseModel):
    """書籍信息"""
    title: str = Field(description="書名")
    author: str = Field(description="作者")
    isbn: Optional[str] = Field(default=None, description="ISBN")
    publication_year: int = Field(description="出版年份")
    genre: str = Field(description="類型")
    rating: Optional[float] = Field(
        default=None,
        description="評分（0-5）",
        ge=0,
        le=5
    )


class BookList(BaseModel):
    """書籍列表"""
    category: str = Field(description="分類")
    books: List[BookInfo] = Field(
        description="書籍列表",
        min_length=1
    )


class Event(BaseModel):
    """事件信息"""
    title: str = Field(description="事件標題")
    date: date = Field(description="日期")
    location: str = Field(description="地點")
    description: str = Field(description="描述")
    participants: List[str] = Field(
        default_factory=list,
        description="參與者列表"
    )


class Timeline(BaseModel):
    """時間線 - 事件列表"""
    subject: str = Field(description="主題")
    events: List[Event] = Field(
        description="事件列表（按時間順序）",
        min_length=1
    )

    @field_validator('events')
    @classmethod
    def sort_by_date(cls, v: List[Event]) -> List[Event]:
        """按日期排序"""
        return sorted(v, key=lambda e: e.date)


# ============================================================================
# 分類和標籤列表
# ============================================================================

class TaggedItem(BaseModel):
    """帶標籤的項目"""
    title: str = Field(description="標題")
    content: str = Field(description="內容")
    tags: List[str] = Field(description="標籤列表")
    category: str = Field(description="主類別")


class TaggedItemList(BaseModel):
    """帶標籤的項目列表"""
    collection_name: str = Field(description="集合名稱")
    items: List[TaggedItem] = Field(description="項目列表")

    def get_all_tags(self) -> Set[str]:
        """獲取所有唯一標籤"""
        tags = set()
        for item in self.items:
            tags.update(item.tags)
        return tags

    def get_items_by_tag(self, tag: str) -> List[TaggedItem]:
        """根據標籤獲取項目"""
        return [item for item in self.items if tag in item.tags]

    def get_tag_frequency(self) -> Dict[str, int]:
        """獲取標籤頻率"""
        freq = {}
        for item in self.items:
            for tag in item.tags:
                freq[tag] = freq.get(tag, 0) + 1
        return freq


# ============================================================================
# 表格數據列表
# ============================================================================

class EmployeeRecord(BaseModel):
    """員工記錄"""
    employee_id: str = Field(description="員工ID")
    name: str = Field(description="姓名")
    department: str = Field(description="部門")
    position: str = Field(description="職位")
    salary: float = Field(description="薪資", gt=0)
    hire_date: date = Field(description="入職日期")


class EmployeeTable(BaseModel):
    """員工表格"""
    company: str = Field(description="公司名稱")
    records: List[EmployeeRecord] = Field(
        description="員工記錄列表",
        min_length=1
    )

    def get_department_stats(self) -> Dict[str, int]:
        """獲取部門統計"""
        stats = {}
        for record in self.records:
            dept = record.department
            stats[dept] = stats.get(dept, 0) + 1
        return stats

    def get_average_salary(self) -> float:
        """計算平均薪資"""
        if not self.records:
            return 0.0
        return sum(r.salary for r in self.records) / len(self.records)


class Transaction(BaseModel):
    """交易記錄"""
    transaction_id: str = Field(description="交易ID")
    date: date = Field(description="交易日期")
    amount: float = Field(description="金額")
    category: str = Field(description="類別")
    description: str = Field(description="描述")
    merchant: str = Field(description="商家")


class TransactionList(BaseModel):
    """交易列表"""
    account_holder: str = Field(description="賬戶持有人")
    account_number: str = Field(description="賬號")
    transactions: List[Transaction] = Field(
        description="交易記錄列表",
        min_length=1
    )

    def get_total_amount(self) -> float:
        """計算總金額"""
        return sum(t.amount for t in self.transactions)

    def get_category_breakdown(self) -> Dict[str, float]:
        """按類別統計金額"""
        breakdown = {}
        for t in self.transactions:
            breakdown[t.category] = breakdown.get(t.category, 0) + t.amount
        return breakdown


# ============================================================================
# 多級列表結構
# ============================================================================

class MenuItem(BaseModel):
    """菜單項"""
    name: str = Field(description="菜品名稱")
    description: str = Field(description="描述")
    price: float = Field(description="價格", gt=0)
    ingredients: List[str] = Field(description="食材列表")
    allergens: List[str] = Field(
        default_factory=list,
        description="過敏原列表"
    )


class MenuSection(BaseModel):
    """菜單分類"""
    section_name: str = Field(description="分類名稱")
    items: List[MenuItem] = Field(
        description="菜品列表",
        min_length=1
    )


class RestaurantMenu(BaseModel):
    """餐廳菜單"""
    restaurant_name: str = Field(description="餐廳名稱")
    sections: List[MenuSection] = Field(
        description="菜單分類列表",
        min_length=1
    )

    def get_total_items(self) -> int:
        """獲取總菜品數"""
        return sum(len(section.items) for section in self.sections)

    def get_price_range(self) -> tuple:
        """獲取價格範圍"""
        all_prices = [
            item.price
            for section in self.sections
            for item in section.items
        ]
        if not all_prices:
            return (0, 0)
        return (min(all_prices), max(all_prices))


# ============================================================================
# 批量提取模型
# ============================================================================

class QuestionAnswer(BaseModel):
    """問答對"""
    question: str = Field(description="問題")
    answer: str = Field(description="答案")
    category: Optional[str] = Field(default=None, description="類別")


class FAQ(BaseModel):
    """常見問題列表"""
    topic: str = Field(description="主題")
    qa_pairs: List[QuestionAnswer] = Field(
        description="問答對列表",
        min_length=3
    )


class Requirement(BaseModel):
    """需求項"""
    requirement_id: str = Field(description="需求ID")
    title: str = Field(description="需求標題")
    description: str = Field(description="需求描述")
    priority: str = Field(description="優先級")
    status: str = Field(description="狀態")
    assignee: Optional[str] = Field(default=None, description="負責人")


class RequirementsList(BaseModel):
    """需求列表"""
    project: str = Field(description="項目名稱")
    requirements: List[Requirement] = Field(
        description="需求列表",
        min_length=1
    )

    def get_by_priority(self, priority: str) -> List[Requirement]:
        """根據優先級過濾"""
        return [r for r in self.requirements if r.priority == priority]

    def get_by_status(self, status: str) -> List[Requirement]:
        """根據狀態過濾"""
        return [r for r in self.requirements if r.status == status]


# ============================================================================
# 輔助函數
# ============================================================================

def setup_client():
    """設置 Instructor 客戶端"""
    api_key = os.getenv("OPENAI_API_KEY", "sk-placeholder")
    openai_client = OpenAI(api_key=api_key)
    return instructor.from_openai(openai_client)


def extract_keywords(client):
    """提取關鍵詞列表"""
    print(f"\n{'='*60}")
    print("提取關鍵詞列表")
    print(f"{'='*60}")

    text = """
    這篇文章討論了人工智能在醫療領域的應用。
    主要涉及機器學習、深度學習、神經網絡、診斷系統、
    醫療影像、預測模型、個性化治療、藥物研發等主題。
    """

    keywords = client.chat.completions.create(
        model="gpt-4",
        response_model=KeywordList,
        messages=[
            {"role": "user", "content": f"提取關鍵詞：\n{text}"}
        ]
    )

    print(f"\n主題: {keywords.topic}")
    print(f"關鍵詞數量: {len(keywords.keywords)}")
    print(f"關鍵詞: {', '.join(keywords.keywords)}")

    return keywords


def extract_contacts(client):
    """提取聯繫人列表"""
    print(f"\n{'='*60}")
    print("提取聯繫人列表")
    print(f"{'='*60}")

    text = """
    在科技大會上認識的聯繫人：

    1. 張工程師
       郵箱：zhang@techcorp.com
       電話：138-0000-1111
       公司：科技公司A

    2. 李經理
       郵箱：li@innovate.com
       公司：創新公司B

    3. 王總監
       郵箱：wang@startup.io
       電話：139-0000-2222
       公司：創業公司C

    總共3位聯繫人
    """

    contacts = client.chat.completions.create(
        model="gpt-4",
        response_model=ContactList,
        messages=[
            {"role": "user", "content": f"提取聯繫人列表：\n{text}"}
        ]
    )

    print(f"\n來源: {contacts.source}")
    print(f"聯繫人數: {contacts.total_count}")
    print("\n詳情:")
    for i, contact in enumerate(contacts.contacts, 1):
        print(f"  {i}. {contact.name}")
        print(f"     郵箱: {contact.email}")
        if contact.phone:
            print(f"     電話: {contact.phone}")
        if contact.company:
            print(f"     公司: {contact.company}")
        print()

    return contacts


def extract_book_list(client):
    """提取書籍列表"""
    print(f"\n{'='*60}")
    print("提取書籍列表")
    print(f"{'='*60}")

    text = """
    推薦書單：人工智能入門

    1. 《深度學習》
       作者：Ian Goodfellow
       出版年份：2016
       類型：技術
       評分：4.5

    2. 《機器學習實戰》
       作者：Peter Harrington
       出版年份：2012
       類型：教程
       ISBN：978-1617290183
       評分：4.2

    3. 《Python機器學習》
       作者：Sebastian Raschka
       出版年份：2015
       類型：教程
       評分：4.3
    """

    books = client.chat.completions.create(
        model="gpt-4",
        response_model=BookList,
        messages=[
            {"role": "user", "content": f"提取書籍列表：\n{text}"}
        ]
    )

    print(f"\n分類: {books.category}")
    print(f"書籍數: {len(books.books)}")
    print("\n書單:")
    for i, book in enumerate(books.books, 1):
        print(f"  {i}. 《{book.title}》")
        print(f"     作者: {book.author}")
        print(f"     年份: {book.publication_year}")
        if book.rating:
            print(f"     評分: {book.rating}/5.0")
        print()

    return books


def extract_timeline(client):
    """提取時間線"""
    print(f"\n{'='*60}")
    print("提取時間線（事件列表）")
    print(f"{'='*60}")

    text = """
    人工智能發展歷程：

    1. 1956年：達特茅斯會議，人工智能誕生
       地點：美國達特茅斯學院
       參與者：John McCarthy, Marvin Minsky

    2. 1997年：深藍擊敗國際象棋冠軍
       地點：紐約
       描述：IBM的深藍計算機戰勝卡斯帕羅夫

    3. 2012年：AlexNet贏得ImageNet競賽
       地點：多倫多大學
       描述：深度學習在圖像識別領域取得突破

    4. 2016年：AlphaGo擊敗李世石
       地點：首爾
       描述：人工智能在圍棋領域超越人類
    """

    timeline = client.chat.completions.create(
        model="gpt-4",
        response_model=Timeline,
        messages=[
            {"role": "user", "content": f"提取時間線：\n{text}"}
        ]
    )

    print(f"\n主題: {timeline.subject}")
    print(f"事件數: {len(timeline.events)}")
    print("\n時間線:")
    for event in timeline.events:
        print(f"  • {event.date}: {event.title}")
        print(f"    地點: {event.location}")
        print(f"    {event.description}")
        print()

    return timeline


def extract_tagged_items(client):
    """提取帶標籤的項目列表"""
    print(f"\n{'='*60}")
    print("提取帶標籤的項目列表")
    print(f"{'='*60}")

    text = """
    技術文章集合：

    1. 《深度學習入門》
       內容：介紹深度學習基礎概念
       標籤：深度學習, 教程, 初學者
       類別：教育

    2. 《TensorFlow實戰》
       內容：使用TensorFlow構建神經網絡
       標籤：TensorFlow, 深度學習, 實戰
       類別：技術

    3. 《機器學習算法詳解》
       內容：詳細講解常見ML算法
       標籤：機器學習, 算法, 教程
       類別：教育
    """

    items = client.chat.completions.create(
        model="gpt-4",
        response_model=TaggedItemList,
        messages=[
            {"role": "user", "content": f"提取文章列表：\n{text}"}
        ]
    )

    print(f"\n集合: {items.collection_name}")
    print(f"項目數: {len(items.items)}")
    print(f"所有標籤: {', '.join(items.get_all_tags())}")

    print("\n標籤頻率:")
    for tag, count in sorted(
        items.get_tag_frequency().items(),
        key=lambda x: x[1],
        reverse=True
    ):
        print(f"  {tag}: {count}次")

    return items


def extract_employee_table(client):
    """提取員工表格"""
    print(f"\n{'='*60}")
    print("提取員工表格數據")
    print(f"{'='*60}")

    text = """
    公司：科技創新有限公司

    員工記錄：

    ID: EMP001, 姓名：張三, 部門：工程部, 職位：高級工程師,
    薪資：$120,000, 入職：2020-03-15

    ID: EMP002, 姓名：李四, 部門：產品部, 職位：產品經理,
    薪資：$110,000, 入職：2019-07-01

    ID: EMP003, 姓名：王五, 部門：工程部, 職位：工程師,
    薪資：$90,000, 入職：2021-01-10

    ID: EMP004, 姓名：趙六, 部門：設計部, 職位：UI設計師,
    薪資：$95,000, 入職：2020-11-20
    """

    table = client.chat.completions.create(
        model="gpt-4",
        response_model=EmployeeTable,
        messages=[
            {"role": "user", "content": f"提取員工表格：\n{text}"}
        ]
    )

    print(f"\n公司: {table.company}")
    print(f"員工數: {len(table.records)}")
    print(f"平均薪資: ${table.get_average_salary():,.2f}")

    print("\n部門統計:")
    for dept, count in table.get_department_stats().items():
        print(f"  {dept}: {count}人")

    return table


def extract_menu(client):
    """提取餐廳菜單（多級列表）"""
    print(f"\n{'='*60}")
    print("提取餐廳菜單（多級列表）")
    print(f"{'='*60}")

    text = """
    餐廳：美味中餐館

    開胃菜：

    1. 涼拌黃瓜
       描述：清爽開胃
       價格：$6
       食材：黃瓜, 大蒜, 香油

    2. 春卷
       描述：香脆可口
       價格：$8
       食材：豬肉, 蔬菜, 春卷皮

    主菜：

    1. 宮保雞丁
       描述：經典川菜
       價格：$18
       食材：雞肉, 花生, 辣椒
       過敏原：花生

    2. 糖醋排骨
       描述：酸甜可口
       價格：$22
       食材：豬排骨, 醋, 糖
    """

    menu = client.chat.completions.create(
        model="gpt-4",
        response_model=RestaurantMenu,
        messages=[
            {"role": "user", "content": f"提取菜單：\n{text}"}
        ]
    )

    print(f"\n餐廳: {menu.restaurant_name}")
    print(f"總菜品數: {menu.get_total_items()}")
    price_range = menu.get_price_range()
    print(f"價格範圍: ${price_range[0]}-${price_range[1]}")

    print("\n菜單:")
    for section in menu.sections:
        print(f"\n  【{section.section_name}】")
        for item in section.items:
            print(f"    • {item.name} - ${item.price}")
            print(f"      {item.description}")

    return menu


# ============================================================================
# 主程序
# ============================================================================

def main():
    """主函數 - 運行所有列表提取示例"""
    print("="*60)
    print("Instructor 列表提取示例")
    print("="*60)

    client = setup_client()

    # 簡單列表
    extract_keywords(client)

    # 結構化對象列表
    extract_contacts(client)
    extract_book_list(client)
    extract_timeline(client)

    # 標籤列表
    extract_tagged_items(client)

    # 表格數據
    extract_employee_table(client)

    # 多級列表
    extract_menu(client)

    print("\n" + "="*60)
    print("列表提取要點總結")
    print("="*60)
    print("""
1. 列表定義：
   - 使用 List[Type] 定義列表類型
   - 設置 min_length 和 max_length
   - 提供清晰的字段描述

2. 列表驗證：
   - 使用 @field_validator 驗證列表內容
   - 去重、排序、過濾
   - 驗證列表長度和內容

3. 結構化列表：
   - 定義列表元素的 Pydantic 模型
   - 嵌套模型組合
   - 提供聚合和查詢方法

4. 批量處理：
   - 一次提取多個對象
   - 統計和分析方法
   - 按條件過濾和分組

5. 最佳實踐：
   - 明確列表的業務含義
   - 提供有用的輔助方法
   - 處理空列表情況
   - 考慮列表順序
   - 添加計數驗證
    """)


if __name__ == "__main__":
    main()

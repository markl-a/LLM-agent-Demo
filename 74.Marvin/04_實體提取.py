"""
Marvin 實體提取示例

本示例展示：
1. marvin.extract() 的使用
2. Pydantic 模型定義
3. 從文本提取實體
4. 列表提取
5. 嵌套結構提取

運行方式：
    python 04_實體提取.py
"""

import os
import marvin
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, date


# ==================== 簡單實體提取 ====================

class Person(BaseModel):
    """人物信息"""
    name: str = Field(description="姓名")
    age: int = Field(description="年齡")
    occupation: str = Field(description="職業")


class Contact(BaseModel):
    """聯繫信息"""
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


def example_simple_extraction():
    """示例 1: 簡單實體提取"""
    print("\n" + "="*60)
    print("示例 1: 簡單實體提取")
    print("="*60)

    try:
        # 提取人物信息
        text1 = "張三今年30歲，是一名軟件工程師。"
        person = marvin.extract(text1, target=Person)

        print(f"從文本提取人物信息:")
        print(f"  文本: {text1}")
        print(f"  姓名: {person.name}")
        print(f"  年齡: {person.age}")
        print(f"  職業: {person.occupation}\n")

        # 提取聯繫信息
        text2 = """
        請聯繫李四，他的郵箱是 lisi@example.com，
        電話是 138-1234-5678，地址是北京市朝陽區某某街道123號。
        """
        contact = marvin.extract(text2, target=Contact)

        print(f"從文本提取聯繫信息:")
        print(f"  姓名: {contact.name}")
        print(f"  郵箱: {contact.email}")
        print(f"  電話: {contact.phone}")
        print(f"  地址: {contact.address}\n")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 列表提取 ====================

class Product(BaseModel):
    """產品信息"""
    name: str
    price: float
    quantity: int


class Task(BaseModel):
    """任務信息"""
    title: str
    priority: str
    deadline: Optional[str] = None


def example_list_extraction():
    """示例 2: 列表提取"""
    print("\n" + "="*60)
    print("示例 2: 列表提取")
    print("="*60)

    try:
        # 提取產品列表
        text1 = """
        購物清單：
        1. iPhone 15 Pro - 8999元 - 1台
        2. AirPods Pro - 1999元 - 2副
        3. MacBook Air - 9499元 - 1台
        """

        products = marvin.extract(text1, target=List[Product])

        print(f"提取的產品列表:")
        for i, product in enumerate(products, 1):
            print(f"  {i}. {product.name}")
            print(f"     價格: ¥{product.price}")
            print(f"     數量: {product.quantity}")

        total = sum(p.price * p.quantity for p in products)
        print(f"\n  總計: ¥{total:.2f}\n")

        # 提取任務列表
        text2 = """
        本週任務：
        - 完成項目文檔（高優先級，週五前）
        - 代碼review（中優先級）
        - 優化性能（低優先級，下週一）
        """

        tasks = marvin.extract(text2, target=List[Task])

        print(f"提取的任務列表:")
        for i, task in enumerate(tasks, 1):
            print(f"  {i}. {task.title}")
            print(f"     優先級: {task.priority}")
            if task.deadline:
                print(f"     截止: {task.deadline}")
            print()

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 嵌套結構提取 ====================

class Address(BaseModel):
    """地址信息"""
    street: str
    city: str
    country: str
    postal_code: Optional[str] = None


class Company(BaseModel):
    """公司信息"""
    name: str
    industry: str
    employees: int
    address: Address


class Author(BaseModel):
    """作者信息"""
    name: str
    email: str


class Article(BaseModel):
    """文章信息"""
    title: str
    author: Author
    published_date: str
    tags: List[str]
    summary: str


def example_nested_extraction():
    """示例 3: 嵌套結構提取"""
    print("\n" + "="*60)
    print("示例 3: 嵌套結構提取")
    print("="*60)

    try:
        # 提取公司信息（包含地址）
        text1 = """
        科技創新公司是一家專注於人工智能的企業，擁有約500名員工。
        公司位於中國北京市海淀區中關村大街1號，郵編100000。
        """

        company = marvin.extract(text1, target=Company)

        print(f"提取的公司信息:")
        print(f"  名稱: {company.name}")
        print(f"  行業: {company.industry}")
        print(f"  員工: {company.employees} 人")
        print(f"  地址:")
        print(f"    街道: {company.address.street}")
        print(f"    城市: {company.address.city}")
        print(f"    國家: {company.address.country}")
        if company.address.postal_code:
            print(f"    郵編: {company.address.postal_code}")
        print()

        # 提取文章信息（包含作者）
        text2 = """
        標題：深度學習的未來發展
        作者：王教授（wangjiaoshou@university.edu）
        發布日期：2025年1月15日
        標籤：人工智能、深度學習、機器學習
        摘要：本文探討了深度學習技術的最新進展和未來發展方向...
        """

        article = marvin.extract(text2, target=Article)

        print(f"提取的文章信息:")
        print(f"  標題: {article.title}")
        print(f"  作者: {article.author.name}")
        print(f"  郵箱: {article.author.email}")
        print(f"  發布: {article.published_date}")
        print(f"  標籤: {', '.join(article.tags)}")
        print(f"  摘要: {article.summary}\n")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 複雜數據提取 ====================

class Ingredient(BaseModel):
    """食材"""
    name: str
    amount: str


class Recipe(BaseModel):
    """食譜"""
    name: str
    cuisine: str
    prep_time: str
    cook_time: str
    servings: int
    ingredients: List[Ingredient]
    instructions: List[str]


class Transaction(BaseModel):
    """交易記錄"""
    date: str
    merchant: str
    amount: float
    category: str
    payment_method: str


def example_complex_extraction():
    """示例 4: 複雜數據提取"""
    print("\n" + "="*60)
    print("示例 4: 複雜數據提取")
    print("="*60)

    try:
        # 提取食譜
        text1 = """
        番茄炒蛋（中式家常菜）

        準備時間：5分鐘
        烹飪時間：10分鐘
        份量：2人份

        食材：
        - 番茄 2個
        - 雞蛋 3個
        - 鹽 適量
        - 糖 1茶匙
        - 蔥花 少許

        步驟：
        1. 番茄切塊，雞蛋打散
        2. 熱鍋炒雞蛋，盛出
        3. 炒番茄至軟爛
        4. 加入雞蛋，調味
        5. 撒上蔥花即可
        """

        recipe = marvin.extract(text1, target=Recipe)

        print(f"提取的食譜:")
        print(f"  名稱: {recipe.name}")
        print(f"  菜系: {recipe.cuisine}")
        print(f"  準備時間: {recipe.prep_time}")
        print(f"  烹飪時間: {recipe.cook_time}")
        print(f"  份量: {recipe.servings} 人份")
        print(f"\n  食材:")
        for ingredient in recipe.ingredients:
            print(f"    - {ingredient.name}: {ingredient.amount}")
        print(f"\n  步驟:")
        for i, instruction in enumerate(recipe.instructions, 1):
            print(f"    {i}. {instruction}")
        print()

        # 提取交易記錄
        text2 = """
        2025年1月15日在星巴克消費了45.5元，使用信用卡支付。
        這是一筆餐飲類消費。
        """

        transaction = marvin.extract(text2, target=Transaction)

        print(f"提取的交易記錄:")
        print(f"  日期: {transaction.date}")
        print(f"  商戶: {transaction.merchant}")
        print(f"  金額: ¥{transaction.amount}")
        print(f"  類別: {transaction.category}")
        print(f"  支付: {transaction.payment_method}\n")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 實體關係提取 ====================

class Relationship(BaseModel):
    """關係"""
    person1: str
    person2: str
    relationship_type: str


class Event(BaseModel):
    """事件"""
    name: str
    date: str
    location: str
    participants: List[str]
    description: str


def example_relationship_extraction():
    """示例 5: 實體關係提取"""
    print("\n" + "="*60)
    print("示例 5: 實體關係提取")
    print("="*60)

    try:
        # 提取人物關係
        text1 = """
        張三是李四的經理，李四是王五的同事。
        王五和趙六是大學同學。
        """

        relationships = marvin.extract(text1, target=List[Relationship])

        print(f"提取的人物關係:")
        for rel in relationships:
            print(f"  {rel.person1} - {rel.relationship_type} - {rel.person2}")
        print()

        # 提取事件信息
        text2 = """
        2025年技術峰會將於3月20日在上海國際會議中心舉行。
        主講嘉賓包括張教授、李博士和王總。
        本次峰會將探討人工智能的最新發展。
        """

        event = marvin.extract(text2, target=Event)

        print(f"提取的事件信息:")
        print(f"  名稱: {event.name}")
        print(f"  日期: {event.date}")
        print(f"  地點: {event.location}")
        print(f"  參與者: {', '.join(event.participants)}")
        print(f"  描述: {event.description}\n")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 多語言提取 ====================

class MovieInfo(BaseModel):
    """電影信息"""
    title: str
    director: str
    year: int
    genre: List[str]
    rating: Optional[float] = None


def example_multilingual_extraction():
    """示例 6: 多語言提取"""
    print("\n" + "="*60)
    print("示例 6: 多語言提取")
    print("="*60)

    try:
        # 中文文本
        text1 = """
        《流浪地球2》是郭帆導演的科幻電影，2023年上映。
        類型包括科幻、災難、動作。評分8.3分。
        """

        movie1 = marvin.extract(text1, target=MovieInfo)
        print(f"中文提取:")
        print(f"  片名: {movie1.title}")
        print(f"  導演: {movie1.director}")
        print(f"  年份: {movie1.year}")
        print(f"  類型: {', '.join(movie1.genre)}")
        print(f"  評分: {movie1.rating}\n")

        # 英文文本
        text2 = """
        "Inception" is a science fiction film directed by Christopher Nolan,
        released in 2010. Genres include sci-fi, thriller, and action.
        It has a rating of 8.8.
        """

        movie2 = marvin.extract(text2, target=MovieInfo)
        print(f"英文提取:")
        print(f"  Title: {movie2.title}")
        print(f"  Director: {movie2.director}")
        print(f"  Year: {movie2.year}")
        print(f"  Genre: {', '.join(movie2.genre)}")
        print(f"  Rating: {movie2.rating}\n")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 批量提取 ====================

class NewsItem(BaseModel):
    """新聞條目"""
    headline: str
    category: str
    date: str
    source: str


def example_batch_extraction():
    """示例 7: 批量提取"""
    print("\n" + "="*60)
    print("示例 7: 批量提取")
    print("="*60)

    try:
        text = """
        今日新聞：

        1. AI技術突破：DeepMind發布最新研究成果
           來源：科技日報，2025年1月15日

        2. 股市收盤：上證指數上漲2.5%
           來源：財經週刊，2025年1月15日

        3. 體育快訊：NBA總決賽第七場今晚開打
           來源：體育新聞網，2025年1月15日
        """

        news_items = marvin.extract(text, target=List[NewsItem])

        print(f"提取的新聞列表:\n")
        for i, item in enumerate(news_items, 1):
            print(f"{i}. {item.headline}")
            print(f"   分類: {item.category}")
            print(f"   日期: {item.date}")
            print(f"   來源: {item.source}\n")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 主函數 ====================

def main():
    """主函數"""
    print("""
╔══════════════════════════════════════════╗
║        Marvin 實體提取示例                ║
╚══════════════════════════════════════════╝

marvin.extract() 功能:
✅ 從文本提取結構化數據
✅ Pydantic 模型支持
✅ 列表和嵌套結構
✅ 多語言支持
✅ 批量處理
    """)

    # 檢查環境
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 請設置 OPENAI_API_KEY 環境變量")
        return

    # 配置 Marvin
    marvin.settings.openai.api_key = os.getenv("OPENAI_API_KEY")

    # 運行示例
    example_simple_extraction()
    example_list_extraction()
    example_nested_extraction()
    example_complex_extraction()
    example_relationship_extraction()
    example_multilingual_extraction()
    example_batch_extraction()

    print("\n" + "="*60)
    print("✅ 所有示例運行完成！")
    print("="*60)


if __name__ == "__main__":
    main()

"""
Guardrails AI - 結構化輸出示例
展示如何驗證 JSON schema 和結構化數據
"""

import os
import json
from typing import List
from pydantic import BaseModel, Field
from guardrails import Guard
from guardrails.hub import ValidChoices
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")


# 定義 Pydantic 模型
class Person(BaseModel):
    """個人信息模型"""
    name: str = Field(description="姓名")
    age: int = Field(description="年齡", ge=0, le=150)
    email: str = Field(description="電子郵件")
    occupation: str = Field(description="職業")


class Product(BaseModel):
    """產品信息模型"""
    product_id: str = Field(description="產品 ID")
    name: str = Field(description="產品名稱")
    price: float = Field(description="價格", gt=0)
    category: str = Field(description="類別")
    in_stock: bool = Field(description="是否有貨")


class Article(BaseModel):
    """文章模型"""
    title: str = Field(description="標題", min_length=5, max_length=100)
    author: str = Field(description="作者")
    summary: str = Field(description="摘要", min_length=20, max_length=200)
    tags: List[str] = Field(description="標籤", min_items=1, max_items=5)
    word_count: int = Field(description="字數", gt=0)


def simple_json_validation():
    """
    簡單的 JSON 驗證
    """
    print("=" * 60)
    print("簡單 JSON 驗證示例")
    print("=" * 60)

    # 使用 Pydantic 模型創建 Guard
    guard = Guard.from_pydantic(
        output_class=Person,
        prompt="生成一個虛構人物的信息"
    )

    try:
        result = guard(
            llm_api=openai.chat.completions.create,
            model="gpt-3.5-turbo",
            max_tokens=200,
        )

        print(f"\n驗證通過的輸出:")
        print(json.dumps(result.validated_output, indent=2, ensure_ascii=False))

        # 訪問結構化數據
        person = result.validated_output
        print(f"\n結構化訪問:")
        print(f"姓名: {person['name']}")
        print(f"年齡: {person['age']}")
        print(f"郵箱: {person['email']}")
        print(f"職業: {person['occupation']}")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def product_schema_validation():
    """
    產品 schema 驗證
    """
    print("\n" + "=" * 60)
    print("產品 Schema 驗證示例")
    print("=" * 60)

    guard = Guard.from_pydantic(
        output_class=Product,
        prompt="生成一個電子產品的詳細信息"
    )

    try:
        result = guard(
            llm_api=openai.chat.completions.create,
            model="gpt-3.5-turbo",
            max_tokens=250,
        )

        print(f"\n產品信息:")
        print(json.dumps(result.validated_output, indent=2, ensure_ascii=False))

        # 驗證數據類型
        product = result.validated_output
        print(f"\n數據類型驗證:")
        print(f"價格類型: {type(product['price'])} - {product['price']}")
        print(f"庫存類型: {type(product['in_stock'])} - {product['in_stock']}")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def nested_structure_validation():
    """
    嵌套結構驗證
    """
    print("\n" + "=" * 60)
    print("嵌套結構驗證示例")
    print("=" * 60)

    class Address(BaseModel):
        """地址模型"""
        street: str
        city: str
        country: str
        postal_code: str

    class Employee(BaseModel):
        """員工模型（包含嵌套的地址）"""
        name: str
        employee_id: str
        department: str
        address: Address
        skills: List[str] = Field(min_items=2, max_items=5)

    guard = Guard.from_pydantic(
        output_class=Employee,
        prompt="生成一個員工的完整信息，包括地址和技能"
    )

    try:
        result = guard(
            llm_api=openai.chat.completions.create,
            model="gpt-3.5-turbo",
            max_tokens=300,
        )

        print(f"\n員工信息（嵌套結構）:")
        print(json.dumps(result.validated_output, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def list_of_objects_validation():
    """
    對象列表驗證
    """
    print("\n" + "=" * 60)
    print("對象列表驗證示例")
    print("=" * 60)

    class Book(BaseModel):
        """書籍模型"""
        title: str
        author: str
        year: int = Field(ge=1000, le=2100)
        rating: float = Field(ge=0, le=5)

    class BookList(BaseModel):
        """書籍列表"""
        books: List[Book] = Field(min_items=3, max_items=5)

    guard = Guard.from_pydantic(
        output_class=BookList,
        prompt="生成 3-5 本書的列表，包括書名、作者、年份和評分"
    )

    try:
        result = guard(
            llm_api=openai.chat.completions.create,
            model="gpt-3.5-turbo",
            max_tokens=500,
        )

        print(f"\n書籍列表:")
        books = result.validated_output['books']
        print(f"共 {len(books)} 本書:")
        for i, book in enumerate(books, 1):
            print(f"\n{i}. {book['title']}")
            print(f"   作者: {book['author']}")
            print(f"   年份: {book['year']}")
            print(f"   評分: {book['rating']}/5.0")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def article_with_constraints():
    """
    帶約束條件的文章驗證
    """
    print("\n" + "=" * 60)
    print("帶約束條件的文章驗證示例")
    print("=" * 60)

    guard = Guard.from_pydantic(
        output_class=Article,
        prompt="生成一篇關於人工智能的文章元數據"
    )

    try:
        result = guard(
            llm_api=openai.chat.completions.create,
            model="gpt-3.5-turbo",
            max_tokens=300,
        )

        print(f"\n文章元數據:")
        article = result.validated_output
        print(f"標題: {article['title']}")
        print(f"作者: {article['author']}")
        print(f"摘要: {article['summary']}")
        print(f"標籤: {', '.join(article['tags'])}")
        print(f"字數: {article['word_count']}")

        # 驗證約束條件
        print(f"\n約束驗證:")
        print(f"✅ 標題長度: {len(article['title'])} (5-100)")
        print(f"✅ 摘要長度: {len(article['summary'])} (20-200)")
        print(f"✅ 標籤數量: {len(article['tags'])} (1-5)")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def json_with_enum_validation():
    """
    帶枚舉值的 JSON 驗證
    """
    print("\n" + "=" * 60)
    print("枚舉值驗證示例")
    print("=" * 60)

    from enum import Enum

    class Priority(str, Enum):
        """優先級枚舉"""
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"
        URGENT = "urgent"

    class Status(str, Enum):
        """狀態枚舉"""
        TODO = "todo"
        IN_PROGRESS = "in_progress"
        DONE = "done"

    class Task(BaseModel):
        """任務模型"""
        title: str
        description: str
        priority: Priority
        status: Status
        assignee: str

    guard = Guard.from_pydantic(
        output_class=Task,
        prompt="生成一個項目任務，包括優先級（low/medium/high/urgent）和狀態（todo/in_progress/done）"
    )

    try:
        result = guard(
            llm_api=openai.chat.completions.create,
            model="gpt-3.5-turbo",
            max_tokens=200,
        )

        print(f"\n任務信息:")
        task = result.validated_output
        print(f"標題: {task['title']}")
        print(f"描述: {task['description']}")
        print(f"優先級: {task['priority']}")
        print(f"狀態: {task['status']}")
        print(f"負責人: {task['assignee']}")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def custom_json_schema():
    """
    自定義 JSON Schema
    """
    print("\n" + "=" * 60)
    print("自定義 JSON Schema 示例")
    print("=" * 60)

    # 定義自定義 schema
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string", "minLength": 2},
            "age": {"type": "integer", "minimum": 0, "maximum": 120},
            "hobbies": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 1,
                "maxItems": 5
            },
            "is_student": {"type": "boolean"}
        },
        "required": ["name", "age", "hobbies"]
    }

    guard = Guard.from_dict(schema)

    prompt = "生成一個人的信息，包含姓名、年齡、愛好列表和是否是學生"

    try:
        result = guard(
            llm_api=openai.chat.completions.create,
            prompt=prompt,
            model="gpt-3.5-turbo",
            max_tokens=200,
        )

        print(f"\n根據自定義 Schema 生成的數據:")
        print(json.dumps(result.validated_output, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def main():
    """
    主函數：運行所有結構化輸出示例
    """
    print("\n🛡️  Guardrails AI - 結構化輸出驗證")
    print("=" * 60)

    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  警告: 未設置 OPENAI_API_KEY 環境變量")
        return

    # 運行各種結構化驗證示例
    simple_json_validation()
    product_schema_validation()
    nested_structure_validation()
    list_of_objects_validation()
    article_with_constraints()
    json_with_enum_validation()
    custom_json_schema()

    print("\n" + "=" * 60)
    print("✅ 所有結構化輸出示例執行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()

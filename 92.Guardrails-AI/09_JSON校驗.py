"""
Guardrails AI - JSON 校驗示例
展示如何嚴格驗證 JSON 格式和結構
"""

import os
import json
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from guardrails import Guard
from guardrails.hub import ValidJson
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")


def basic_json_validation():
    """
    基本 JSON 格式驗證
    """
    print("=" * 60)
    print("基本 JSON 格式驗證示例")
    print("=" * 60)

    # 使用 ValidJson 驗證器
    guard = Guard().use(
        ValidJson(on_fail="exception")
    )

    prompt = "生成一個包含 name 和 age 字段的 JSON 對象"

    print(f"\n提示: {prompt}")

    try:
        result = guard(
            llm_api=openai.chat.completions.create,
            prompt=prompt,
            model="gpt-3.5-turbo",
            max_tokens=100,
        )

        print(f"\n輸出: {result.validated_output}")

        # 驗證是否為有效 JSON
        try:
            parsed = json.loads(result.validated_output)
            print(f"✅ JSON 格式有效")
            print(f"解析結果: {json.dumps(parsed, indent=2, ensure_ascii=False)}")
        except json.JSONDecodeError:
            print(f"❌ JSON 格式無效")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def strict_schema_validation():
    """
    嚴格的 JSON Schema 驗證
    """
    print("\n" + "=" * 60)
    print("嚴格 Schema 驗證示例")
    print("=" * 60)

    class UserProfile(BaseModel):
        """用戶資料模型"""
        username: str = Field(min_length=3, max_length=20)
        email: str = Field(pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
        age: int = Field(ge=18, le=100)
        is_active: bool = Field(default=True)

    guard = Guard.from_pydantic(
        output_class=UserProfile,
        prompt="生成一個用戶資料的 JSON"
    )

    print("\nSchema 要求:")
    print("- username: 3-20 字符")
    print("- email: 有效的郵箱格式")
    print("- age: 18-100 之間")
    print("- is_active: 布爾值")

    try:
        result = guard(
            llm_api=openai.chat.completions.create,
            model="gpt-3.5-turbo",
            max_tokens=150,
        )

        print(f"\n✅ Schema 驗證通過")
        print(f"輸出:")
        print(json.dumps(result.validated_output, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"❌ Schema 驗證失敗: {str(e)}")


def nested_json_validation():
    """
    嵌套 JSON 結構驗證
    """
    print("\n" + "=" * 60)
    print("嵌套 JSON 驗證示例")
    print("=" * 60)

    class Address(BaseModel):
        """地址模型"""
        street: str
        city: str
        country: str
        postal_code: str = Field(pattern=r'^\d{5,6}$')

    class Contact(BaseModel):
        """聯繫方式模型"""
        phone: str
        email: str

    class Company(BaseModel):
        """公司模型（嵌套結構）"""
        name: str = Field(min_length=2)
        address: Address
        contact: Contact
        employee_count: int = Field(gt=0)
        founded_year: int = Field(ge=1800, le=2024)

    guard = Guard.from_pydantic(
        output_class=Company,
        prompt="生成一個公司的完整信息 JSON，包含地址和聯繫方式"
    )

    try:
        result = guard(
            llm_api=openai.chat.completions.create,
            model="gpt-3.5-turbo",
            max_tokens=300,
        )

        print(f"\n✅ 嵌套結構驗證通過")
        print(f"輸出:")
        print(json.dumps(result.validated_output, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"❌ 驗證失敗: {str(e)}")


def array_validation():
    """
    JSON 數組驗證
    """
    print("\n" + "=" * 60)
    print("JSON 數組驗證示例")
    print("=" * 60)

    class Item(BaseModel):
        """商品模型"""
        id: int
        name: str
        price: float = Field(gt=0)
        quantity: int = Field(ge=0)

    class Inventory(BaseModel):
        """庫存模型"""
        items: List[Item] = Field(min_items=2, max_items=5)
        total_value: float = Field(gt=0)

        @validator('total_value')
        def validate_total(cls, v, values):
            """驗證總價值"""
            if 'items' in values:
                calculated_total = sum(
                    item.price * item.quantity
                    for item in values['items']
                )
                if abs(v - calculated_total) > 0.01:
                    raise ValueError("Total value doesn't match items")
            return v

    guard = Guard.from_pydantic(
        output_class=Inventory,
        prompt="生成包含 2-5 個商品的庫存 JSON，包含 items 數組和 total_value"
    )

    try:
        result = guard(
            llm_api=openai.chat.completions.create,
            model="gpt-3.5-turbo",
            max_tokens=400,
        )

        print(f"\n✅ 數組驗證通過")
        print(f"輸出:")
        print(json.dumps(result.validated_output, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"❌ 驗證失敗: {str(e)}")


def optional_fields_validation():
    """
    可選字段驗證
    """
    print("\n" + "=" * 60)
    print("可選字段驗證示例")
    print("=" * 60)

    class BlogPost(BaseModel):
        """博客文章模型"""
        title: str = Field(min_length=5)
        content: str = Field(min_length=20)
        author: str
        tags: Optional[List[str]] = None
        views: Optional[int] = Field(default=0, ge=0)
        is_published: bool = Field(default=False)

    guard = Guard.from_pydantic(
        output_class=BlogPost,
        prompt="生成一篇博客文章的 JSON，tags 和 views 字段可選"
    )

    try:
        result = guard(
            llm_api=openai.chat.completions.create,
            model="gpt-3.5-turbo",
            max_tokens=300,
        )

        print(f"\n✅ 可選字段驗證通過")
        print(f"輸出:")
        print(json.dumps(result.validated_output, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"❌ 驗證失敗: {str(e)}")


def enum_validation():
    """
    枚舉值驗證
    """
    print("\n" + "=" * 60)
    print("枚舉值驗證示例")
    print("=" * 60)

    from enum import Enum

    class OrderStatus(str, Enum):
        """訂單狀態枚舉"""
        PENDING = "pending"
        PROCESSING = "processing"
        SHIPPED = "shipped"
        DELIVERED = "delivered"
        CANCELLED = "cancelled"

    class PaymentMethod(str, Enum):
        """支付方式枚舉"""
        CREDIT_CARD = "credit_card"
        DEBIT_CARD = "debit_card"
        PAYPAL = "paypal"
        CASH = "cash"

    class Order(BaseModel):
        """訂單模型"""
        order_id: str
        status: OrderStatus
        payment_method: PaymentMethod
        amount: float = Field(gt=0)

    guard = Guard.from_pydantic(
        output_class=Order,
        prompt="生成一個訂單 JSON，status 必須是 pending/processing/shipped/delivered/cancelled 之一，payment_method 必須是 credit_card/debit_card/paypal/cash 之一"
    )

    try:
        result = guard(
            llm_api=openai.chat.completions.create,
            model="gpt-3.5-turbo",
            max_tokens=200,
        )

        print(f"\n✅ 枚舉值驗證通過")
        print(f"輸出:")
        print(json.dumps(result.validated_output, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"❌ 驗證失敗: {str(e)}")


def complex_validation_rules():
    """
    複雜驗證規則
    """
    print("\n" + "=" * 60)
    print("複雜驗證規則示例")
    print("=" * 60)

    class Event(BaseModel):
        """事件模型"""
        event_id: str = Field(pattern=r'^EVT-\d{6}$')
        title: str = Field(min_length=5, max_length=100)
        start_date: str = Field(pattern=r'^\d{4}-\d{2}-\d{2}$')
        end_date: str = Field(pattern=r'^\d{4}-\d{2}-\d{2}$')
        attendees: List[str] = Field(min_items=1, max_items=100)
        budget: float = Field(gt=0, le=1000000)

        @validator('end_date')
        def validate_dates(cls, v, values):
            """驗證結束日期晚於開始日期"""
            if 'start_date' in values:
                if v < values['start_date']:
                    raise ValueError("End date must be after start date")
            return v

    guard = Guard.from_pydantic(
        output_class=Event,
        prompt="生成一個活動 JSON，event_id 格式為 EVT-XXXXXX，日期格式為 YYYY-MM-DD"
    )

    try:
        result = guard(
            llm_api=openai.chat.completions.create,
            model="gpt-3.5-turbo",
            max_tokens=300,
        )

        print(f"\n✅ 複雜驗證通過")
        print(f"輸出:")
        print(json.dumps(result.validated_output, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"❌ 驗證失敗: {str(e)}")


def custom_json_parser():
    """
    自定義 JSON 解析器
    """
    print("\n" + "=" * 60)
    print("自定義 JSON 解析器示例")
    print("=" * 60)

    def safe_json_parse(text):
        """
        安全的 JSON 解析，處理常見問題
        """
        # 移除可能的 markdown 代碼塊標記
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]

        text = text.strip()

        try:
            return json.loads(text), None
        except json.JSONDecodeError as e:
            return None, str(e)

    prompt = "生成一個包含 name, age, city 字段的 JSON"

    print(f"\n提示: {prompt}")

    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
        )

        text = response.choices[0].message.content

        print(f"\n原始輸出: {text}")

        parsed, error = safe_json_parse(text)

        if parsed:
            print(f"\n✅ JSON 解析成功")
            print(f"解析結果:")
            print(json.dumps(parsed, indent=2, ensure_ascii=False))
        else:
            print(f"\n❌ JSON 解析失敗: {error}")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def json_repair():
    """
    JSON 修復
    """
    print("\n" + "=" * 60)
    print("JSON 修復示例")
    print("=" * 60)

    def repair_json(text):
        """
        嘗試修復常見的 JSON 錯誤
        """
        # 移除多餘的逗號
        import re
        text = re.sub(r',\s*}', '}', text)
        text = re.sub(r',\s*]', ']', text)

        # 移除註釋
        text = re.sub(r'//.*?\n', '\n', text)

        # 嘗試解析
        try:
            return json.loads(text), True
        except json.JSONDecodeError:
            return text, False

    malformed_json = '{"name": "John", "age": 30, "city": "New York",}'

    print(f"\n格式錯誤的 JSON: {malformed_json}")

    repaired, success = repair_json(malformed_json)

    if success:
        print(f"\n✅ JSON 修復成功")
        print(f"修復後:")
        print(json.dumps(repaired, indent=2, ensure_ascii=False))
    else:
        print(f"\n❌ JSON 修復失敗")


def main():
    """
    主函數：運行所有 JSON 校驗示例
    """
    print("\n🛡️  Guardrails AI - JSON 校驗")
    print("=" * 60)

    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  警告: 未設置 OPENAI_API_KEY 環境變量")
        return

    # 運行各種 JSON 驗證示例
    basic_json_validation()
    strict_schema_validation()
    nested_json_validation()
    array_validation()
    optional_fields_validation()
    enum_validation()
    complex_validation_rules()
    custom_json_parser()
    json_repair()

    print("\n" + "=" * 60)
    print("✅ 所有 JSON 校驗示例執行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()

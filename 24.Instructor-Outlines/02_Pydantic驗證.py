"""
Pydantic 驗證範例
==================

本範例展示如何在 Instructor 中使用 Pydantic 的強大驗證功能：
1. 欄位約束（字串長度、數值範圍等）
2. 自訂驗證器
3. 正則表達式驗證
4. 複雜驗證邏輯
5. 驗證錯誤處理

Pydantic 提供了強大的資料驗證功能，確保 LLM 輸出符合您的需求。
"""

import re
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, model_validator, EmailStr, HttpUrl
import instructor

# ============================================================================
# 範例 1：基本欄位約束
# ============================================================================

def example_field_constraints():
    """展示各種欄位約束的使用"""
    print("=" * 60)
    print("範例 1：基本欄位約束")
    print("=" * 60)

    try:
        from openai import OpenAI

        class ValidatedUser(BaseModel):
            """帶有多種約束的使用者模型"""

            # 字串長度約束
            username: str = Field(
                min_length=3,
                max_length=20,
                description="使用者名稱（3-20 字元）"
            )

            # 數值範圍約束
            age: int = Field(
                ge=0,  # greater than or equal
                le=150,  # less than or equal
                description="年齡（0-150）"
            )

            # 正浮點數約束
            salary: float = Field(
                gt=0,  # greater than
                description="薪資（必須大於 0）"
            )

            # Email 驗證（使用 Pydantic 的特殊型別）
            email: EmailStr = Field(description="電子郵件地址")

            # 可選欄位
            website: Optional[HttpUrl] = Field(
                None,
                description="個人網站（可選）"
            )

        client = instructor.from_openai(OpenAI())

        # 測試驗證
        user = client.chat.completions.create(
            model="gpt-3.5-turbo",
            response_model=ValidatedUser,
            messages=[
                {
                    "role": "user",
                    "content": """
                    提取使用者資訊：
                    張小明，使用者名稱是 xiaoming123，今年 28 歲，
                    月薪 50000 元，email 是 xiaoming@example.com，
                    個人網站 https://xiaoming.dev
                    """
                }
            ]
        )

        print("\n✅ 驗證通過的使用者資訊：")
        print(f"使用者名稱：{user.username}")
        print(f"年齡：{user.age}")
        print(f"薪資：${user.salary:,.2f}")
        print(f"Email：{user.email}")
        print(f"網站：{user.website}")

    except Exception as e:
        print(f"❌ 錯誤：{e}")


# ============================================================================
# 範例 2：自訂驗證器
# ============================================================================

def example_custom_validators():
    """使用自訂驗證器進行複雜驗證"""
    print("\n" + "=" * 60)
    print("範例 2：自訂驗證器")
    print("=" * 60)

    try:
        from openai import OpenAI

        class PhoneContact(BaseModel):
            """帶有自訂驗證的聯絡人模型"""
            name: str = Field(description="聯絡人姓名")
            phone: str = Field(description="電話號碼")
            country_code: str = Field(default="+886", description="國碼")

            @field_validator('name')
            @classmethod
            def validate_name(cls, v: str) -> str:
                """驗證姓名不能包含數字"""
                if any(char.isdigit() for char in v):
                    raise ValueError("姓名不能包含數字")
                if len(v) < 2:
                    raise ValueError("姓名至少需要 2 個字元")
                return v.strip()

            @field_validator('phone')
            @classmethod
            def validate_phone(cls, v: str) -> str:
                """驗證台灣手機號碼格式"""
                # 移除空格和破折號
                phone = re.sub(r'[\s\-]', '', v)

                # 檢查台灣手機號碼格式（09 開頭，共 10 碼）
                if not re.match(r'^09\d{8}$', phone):
                    raise ValueError("請提供有效的台灣手機號碼（09XXXXXXXX）")

                return phone

            @field_validator('country_code')
            @classmethod
            def validate_country_code(cls, v: str) -> str:
                """驗證國碼格式"""
                if not v.startswith('+'):
                    raise ValueError("國碼必須以 + 開頭")
                return v

        client = instructor.from_openai(OpenAI())

        contact = client.chat.completions.create(
            model="gpt-3.5-turbo",
            response_model=PhoneContact,
            messages=[
                {
                    "role": "user",
                    "content": "聯絡人：王小華，電話 0912-345-678"
                }
            ]
        )

        print("\n✅ 驗證通過的聯絡人：")
        print(f"姓名：{contact.name}")
        print(f"電話：{contact.phone}")
        print(f"完整號碼：{contact.country_code}-{contact.phone}")

    except Exception as e:
        print(f"❌ 錯誤：{e}")


# ============================================================================
# 範例 3：模型級驗證器
# ============================================================================

def example_model_validators():
    """使用模型級驗證器驗證多個欄位之間的關係"""
    print("\n" + "=" * 60)
    print("範例 3：模型級驗證器")
    print("=" * 60)

    try:
        from openai import OpenAI

        class DateRange(BaseModel):
            """日期範圍模型，確保結束日期在開始日期之後"""
            event_name: str = Field(description="活動名稱")
            start_date: str = Field(description="開始日期（YYYY-MM-DD）")
            end_date: str = Field(description="結束日期（YYYY-MM-DD）")

            @field_validator('start_date', 'end_date')
            @classmethod
            def validate_date_format(cls, v: str) -> str:
                """驗證日期格式"""
                try:
                    datetime.strptime(v, '%Y-%m-%d')
                    return v
                except ValueError:
                    raise ValueError(f"日期格式必須是 YYYY-MM-DD，收到：{v}")

            @model_validator(mode='after')
            def validate_date_range(self):
                """驗證日期範圍邏輯"""
                start = datetime.strptime(self.start_date, '%Y-%m-%d')
                end = datetime.strptime(self.end_date, '%Y-%m-%d')

                if end < start:
                    raise ValueError("結束日期必須在開始日期之後或相同")

                # 檢查活動時間是否過長（例如：不超過 1 年）
                if (end - start).days > 365:
                    raise ValueError("活動時間不能超過 1 年")

                return self

        client = instructor.from_openai(OpenAI())

        event = client.chat.completions.create(
            model="gpt-3.5-turbo",
            response_model=DateRange,
            messages=[
                {
                    "role": "user",
                    "content": "提取：2025 年春季展覽會從 2025-03-01 到 2025-03-15"
                }
            ]
        )

        print("\n✅ 驗證通過的活動資訊：")
        print(f"活動名稱：{event.event_name}")
        print(f"開始日期：{event.start_date}")
        print(f"結束日期：{event.end_date}")

        # 計算活動天數
        start = datetime.strptime(event.start_date, '%Y-%m-%d')
        end = datetime.strptime(event.end_date, '%Y-%m-%d')
        days = (end - start).days + 1
        print(f"活動天數：{days} 天")

    except Exception as e:
        print(f"❌ 錯誤：{e}")


# ============================================================================
# 範例 4：正則表達式驗證
# ============================================================================

def example_regex_validation():
    """使用正則表達式進行格式驗證"""
    print("\n" + "=" * 60)
    print("範例 4：正則表達式驗證")
    print("=" * 60)

    try:
        from openai import OpenAI
        from pydantic import field_validator

        class IdentityCard(BaseModel):
            """身分證資料模型"""
            name: str = Field(description="姓名")
            id_number: str = Field(description="身分證字號")
            issue_date: str = Field(description="發證日期")

            @field_validator('id_number')
            @classmethod
            def validate_id_number(cls, v: str) -> str:
                """驗證台灣身分證字號格式（第一碼英文，後面 9 碼數字）"""
                pattern = r'^[A-Z][12]\d{8}$'
                if not re.match(pattern, v.upper()):
                    raise ValueError(
                        "身分證字號格式錯誤，應為 1 個英文字母 + 1 個數字(1或2) + 8 個數字"
                    )
                return v.upper()

            @field_validator('issue_date')
            @classmethod
            def validate_issue_date(cls, v: str) -> str:
                """驗證日期格式"""
                # 支援民國年和西元年兩種格式
                pattern_roc = r'^\d{3}/\d{2}/\d{2}$'  # 民國年 XXX/MM/DD
                pattern_ad = r'^\d{4}-\d{2}-\d{2}$'   # 西元年 YYYY-MM-DD

                if not (re.match(pattern_roc, v) or re.match(pattern_ad, v)):
                    raise ValueError(
                        "日期格式錯誤，應為 XXX/MM/DD（民國年）或 YYYY-MM-DD（西元年）"
                    )
                return v

        client = instructor.from_openai(OpenAI())

        id_card = client.chat.completions.create(
            model="gpt-3.5-turbo",
            response_model=IdentityCard,
            messages=[
                {
                    "role": "user",
                    "content": "身分證資料：王小明，字號 A123456789，發證日期 110/05/20"
                }
            ]
        )

        print("\n✅ 驗證通過的身分證資料：")
        print(f"姓名：{id_card.name}")
        print(f"身分證字號：{id_card.id_number}")
        print(f"發證日期：{id_card.issue_date}")

    except Exception as e:
        print(f"❌ 錯誤：{e}")


# ============================================================================
# 範例 5：列表驗證
# ============================================================================

def example_list_validation():
    """驗證列表中的每個元素"""
    print("\n" + "=" * 60)
    print("範例 5：列表驗證")
    print("=" * 60)

    try:
        from openai import OpenAI

        class GradeRecord(BaseModel):
            """成績紀錄"""
            subject: str = Field(description="科目名稱")
            score: int = Field(ge=0, le=100, description="分數（0-100）")

            @field_validator('subject')
            @classmethod
            def validate_subject(cls, v: str) -> str:
                """驗證科目名稱"""
                allowed_subjects = ['數學', '英文', '國文', '物理', '化學', '生物']
                if v not in allowed_subjects:
                    raise ValueError(f"科目必須是以下之一：{', '.join(allowed_subjects)}")
                return v

        class StudentReport(BaseModel):
            """學生成績單"""
            student_name: str = Field(description="學生姓名")
            grades: List[GradeRecord] = Field(description="成績列表")

            @field_validator('grades')
            @classmethod
            def validate_grades(cls, v: List[GradeRecord]) -> List[GradeRecord]:
                """驗證成績列表"""
                if len(v) == 0:
                    raise ValueError("至少需要一個成績紀錄")
                if len(v) > 10:
                    raise ValueError("成績紀錄不能超過 10 個")

                # 檢查是否有重複科目
                subjects = [grade.subject for grade in v]
                if len(subjects) != len(set(subjects)):
                    raise ValueError("不能有重複的科目")

                return v

            @model_validator(mode='after')
            def calculate_average(self):
                """計算平均分數"""
                if self.grades:
                    avg = sum(g.score for g in self.grades) / len(self.grades)
                    print(f"  （平均分數：{avg:.1f}）")
                return self

        client = instructor.from_openai(OpenAI())

        report = client.chat.completions.create(
            model="gpt-3.5-turbo",
            response_model=StudentReport,
            messages=[
                {
                    "role": "user",
                    "content": """
                    提取學生成績：
                    學生：王小明
                    數學 85 分、英文 92 分、國文 78 分、物理 88 分
                    """
                }
            ]
        )

        print("\n✅ 驗證通過的成績單：")
        print(f"學生：{report.student_name}")
        print("成績：")
        for grade in report.grades:
            print(f"  - {grade.subject}：{grade.score} 分")

    except Exception as e:
        print(f"❌ 錯誤：{e}")


# ============================================================================
# 範例 6：條件驗證
# ============================================================================

def example_conditional_validation():
    """根據條件進行不同的驗證"""
    print("\n" + "=" * 60)
    print("範例 6：條件驗證")
    print("=" * 60)

    try:
        from openai import OpenAI
        from typing import Literal

        class ShippingInfo(BaseModel):
            """運送資訊"""
            recipient: str = Field(description="收件人")
            shipping_method: Literal["standard", "express", "overnight"] = Field(
                description="運送方式"
            )
            address: str = Field(description="地址")
            phone: str = Field(description="聯絡電話")
            delivery_time: Optional[str] = Field(None, description="指定送達時間")

            @model_validator(mode='after')
            def validate_delivery_requirements(self):
                """根據運送方式驗證額外要求"""
                # 如果是隔夜配送，必須提供送達時間
                if self.shipping_method == "overnight" and not self.delivery_time:
                    raise ValueError("隔夜配送必須指定送達時間")

                # 快遞和隔夜配送需要手機號碼
                if self.shipping_method in ["express", "overnight"]:
                    if not re.match(r'^09\d{8}$', re.sub(r'[\s\-]', '', self.phone)):
                        raise ValueError("快遞服務需要提供有效的手機號碼")

                return self

        client = instructor.from_openai(OpenAI())

        shipping = client.chat.completions.create(
            model="gpt-3.5-turbo",
            response_model=ShippingInfo,
            messages=[
                {
                    "role": "user",
                    "content": """
                    運送資訊：
                    收件人：李小華
                    使用快遞方式
                    地址：台北市信義區信義路五段 7 號
                    電話：0912-345-678
                    """
                }
            ]
        )

        print("\n✅ 驗證通過的運送資訊：")
        print(f"收件人：{shipping.recipient}")
        print(f"運送方式：{shipping.shipping_method}")
        print(f"地址：{shipping.address}")
        print(f"電話：{shipping.phone}")
        if shipping.delivery_time:
            print(f"送達時間：{shipping.delivery_time}")

    except Exception as e:
        print(f"❌ 錯誤：{e}")


# ============================================================================
# 主程式
# ============================================================================

def main():
    """執行所有範例"""
    print("\n" + "🎯" * 30)
    print("Pydantic 驗證範例")
    print("🎯" * 30)

    print("\n📝 關於 Pydantic 驗證")
    print("-" * 60)
    print("Pydantic 提供強大的資料驗證功能，確保 LLM 輸出符合您的要求：")
    print("\n驗證類型：")
    print("✅ 欄位約束（長度、範圍、格式等）")
    print("✅ 自訂驗證器（複雜邏輯）")
    print("✅ 模型級驗證（多欄位關係）")
    print("✅ 正則表達式驗證")
    print("✅ 列表和集合驗證")
    print("✅ 條件驗證")
    print("-" * 60)

    # 執行所有範例
    example_field_constraints()
    example_custom_validators()
    example_model_validators()
    example_regex_validation()
    example_list_validation()
    example_conditional_validation()

    print("\n" + "=" * 60)
    print("✅ 所有驗證範例執行完畢！")
    print("=" * 60)
    print("\n💡 驗證最佳實踐：")
    print("1. 盡可能使用 Pydantic 內建的欄位約束")
    print("2. 為複雜邏輯編寫自訂驗證器")
    print("3. 提供清晰的錯誤訊息")
    print("4. 使用型別提示增強 IDE 支援")
    print("5. 結合 Instructor 的重試機制處理驗證錯誤")


if __name__ == "__main__":
    main()

"""
Instructor 驗證和重試機制示例

這個模塊展示了 Instructor 的核心功能之一：自動驗證和智能重試。
當 LLM 輸出不符合預期時，Instructor 會自動重試直到獲得有效結果。

主要內容：
1. 字段級驗證器
2. 模型級驗證器
3. 自定義驗證邏輯
4. 重試配置和策略
5. 驗證錯誤處理
6. 複雜驗證場景

作者: Instructor 示例
日期: 2025-01-01
"""

import os
from typing import List, Optional
from datetime import datetime, date
from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
    EmailStr,
    ValidationError
)
import instructor
from openai import OpenAI


# ============================================================================
# 字段級驗證示例
# ============================================================================

class ValidatedUser(BaseModel):
    """帶驗證的用戶模型

    展示如何使用 field_validator 進行字段級驗證。
    """
    name: str = Field(description="用戶姓名")
    age: int = Field(description="年齡", ge=0, le=150)
    email: EmailStr = Field(description="電子郵件")
    username: str = Field(description="用戶名（3-20個字符，只能包含字母、數字和下劃線）")
    password: str = Field(description="密碼（至少8個字符）")

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """驗證用戶名格式

        規則：
        - 3-20個字符
        - 只能包含字母、數字和下劃線
        - 必須以字母開頭
        """
        if len(v) < 3 or len(v) > 20:
            raise ValueError('用戶名必須是3-20個字符')

        if not v[0].isalpha():
            raise ValueError('用戶名必須以字母開頭')

        if not all(c.isalnum() or c == '_' for c in v):
            raise ValueError('用戶名只能包含字母、數字和下劃線')

        return v.lower()  # 轉換為小寫

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """驗證密碼強度

        規則：
        - 至少8個字符
        - 必須包含大寫字母
        - 必須包含小寫字母
        - 必須包含數字
        """
        if len(v) < 8:
            raise ValueError('密碼必須至少8個字符')

        if not any(c.isupper() for c in v):
            raise ValueError('密碼必須包含至少一個大寫字母')

        if not any(c.islower() for c in v):
            raise ValueError('密碼必須包含至少一個小寫字母')

        if not any(c.isdigit() for c in v):
            raise ValueError('密碼必須包含至少一個數字')

        return v


class PriceModel(BaseModel):
    """價格模型 - 數值範圍驗證"""
    product_name: str = Field(description="產品名稱")
    original_price: float = Field(description="原價", gt=0)
    sale_price: float = Field(description="售價", gt=0)
    discount_percentage: float = Field(description="折扣百分比", ge=0, le=100)

    @field_validator('sale_price')
    @classmethod
    def validate_sale_price(cls, v: float, info) -> float:
        """驗證售價必須低於或等於原價"""
        # 在 Pydantic v2 中，使用 info.data 訪問其他字段
        if 'original_price' in info.data and v > info.data['original_price']:
            raise ValueError('售價不能高於原價')
        return v

    @field_validator('discount_percentage')
    @classmethod
    def validate_discount(cls, v: float, info) -> float:
        """驗證折扣百分比的計算是否正確"""
        if 'original_price' in info.data and 'sale_price' in info.data:
            expected_discount = (
                (info.data['original_price'] - info.data['sale_price'])
                / info.data['original_price'] * 100
            )
            # 允許1%的誤差
            if abs(v - expected_discount) > 1:
                raise ValueError(
                    f'折扣百分比不正確：應該約為 {expected_discount:.1f}%'
                )
        return v


class DateRange(BaseModel):
    """日期範圍模型 - 日期邏輯驗證"""
    event_name: str = Field(description="活動名稱")
    start_date: date = Field(description="開始日期")
    end_date: date = Field(description="結束日期")
    registration_deadline: date = Field(description="報名截止日期")

    @field_validator('end_date')
    @classmethod
    def validate_end_date(cls, v: date, info) -> date:
        """驗證結束日期必須在開始日期之後"""
        if 'start_date' in info.data and v < info.data['start_date']:
            raise ValueError('結束日期必須在開始日期之後或相同')
        return v

    @field_validator('registration_deadline')
    @classmethod
    def validate_deadline(cls, v: date, info) -> date:
        """驗證報名截止日期必須在活動開始前"""
        if 'start_date' in info.data and v > info.data['start_date']:
            raise ValueError('報名截止日期必須在活動開始日期之前或相同')
        return v


# ============================================================================
# 模型級驗證示例
# ============================================================================

class BankAccount(BaseModel):
    """銀行賬戶模型 - 模型級驗證示例"""
    account_holder: str = Field(description="賬戶持有人")
    account_number: str = Field(description="賬號")
    balance: float = Field(description="餘額")
    credit_limit: float = Field(description="信用額度", ge=0)
    available_balance: float = Field(description="可用餘額")

    @model_validator(mode='after')
    def validate_available_balance(self):
        """驗證可用餘額的計算"""
        expected_available = self.balance + self.credit_limit
        if abs(self.available_balance - expected_available) > 0.01:
            raise ValueError(
                f'可用餘額計算錯誤：應為 {expected_available:.2f}'
            )
        return self


class Triangle(BaseModel):
    """三角形模型 - 複雜數學驗證"""
    side_a: float = Field(description="邊長 A", gt=0)
    side_b: float = Field(description="邊長 B", gt=0)
    side_c: float = Field(description="邊長 C", gt=0)

    @model_validator(mode='after')
    def validate_triangle_inequality(self):
        """驗證三角形不等式

        任意兩邊之和必須大於第三邊
        """
        if self.side_a + self.side_b <= self.side_c:
            raise ValueError('邊長 A + B 必須大於 C')
        if self.side_a + self.side_c <= self.side_b:
            raise ValueError('邊長 A + C 必須大於 B')
        if self.side_b + self.side_c <= self.side_a:
            raise ValueError('邊長 B + C 必須大於 A')
        return self


class TeamAssignment(BaseModel):
    """團隊分配模型 - 列表驗證"""
    team_name: str = Field(description="團隊名稱")
    team_lead: str = Field(description="團隊負責人")
    members: List[str] = Field(description="團隊成員", min_length=1)
    max_size: int = Field(description="最大團隊規模", gt=0)

    @model_validator(mode='after')
    def validate_team_composition(self):
        """驗證團隊組成"""
        # 檢查團隊負責人是否在成員列表中
        if self.team_lead not in self.members:
            raise ValueError('團隊負責人必須是團隊成員之一')

        # 檢查團隊規模
        if len(self.members) > self.max_size:
            raise ValueError(
                f'團隊人數 ({len(self.members)}) 超過最大規模 ({self.max_size})'
            )

        # 檢查是否有重複成員
        if len(self.members) != len(set(self.members)):
            raise ValueError('團隊成員列表中存在重複')

        return self


# ============================================================================
# 自定義驗證邏輯
# ============================================================================

class PhoneNumber(BaseModel):
    """電話號碼模型 - 格式驗證"""
    country_code: str = Field(description="國家代碼")
    number: str = Field(description="電話號碼")

    @field_validator('country_code')
    @classmethod
    def validate_country_code(cls, v: str) -> str:
        """驗證國家代碼格式"""
        # 移除可能的 + 號
        v = v.lstrip('+')

        if not v.isdigit():
            raise ValueError('國家代碼只能包含數字')

        if len(v) < 1 or len(v) > 3:
            raise ValueError('國家代碼必須是1-3位數字')

        return f'+{v}'

    @field_validator('number')
    @classmethod
    def validate_number(cls, v: str) -> str:
        """驗證電話號碼格式"""
        # 移除常見分隔符
        cleaned = v.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')

        if not cleaned.isdigit():
            raise ValueError('電話號碼只能包含數字')

        if len(cleaned) < 7 or len(cleaned) > 15:
            raise ValueError('電話號碼必須是7-15位數字')

        return cleaned


class CreditCard(BaseModel):
    """信用卡模型 - Luhn 算法驗證"""
    card_number: str = Field(description="卡號（16位數字）")
    cardholder_name: str = Field(description="持卡人姓名")
    expiry_month: int = Field(description="到期月份", ge=1, le=12)
    expiry_year: int = Field(description="到期年份", ge=2025)
    cvv: str = Field(description="CVV安全碼（3位數字）")

    @field_validator('card_number')
    @classmethod
    def validate_card_number(cls, v: str) -> str:
        """使用 Luhn 算法驗證卡號"""
        # 移除空格和破折號
        v = v.replace(' ', '').replace('-', '')

        # 檢查長度
        if len(v) != 16:
            raise ValueError('卡號必須是16位數字')

        # 檢查是否全為數字
        if not v.isdigit():
            raise ValueError('卡號只能包含數字')

        # Luhn 算法驗證
        def luhn_check(card_num: str) -> bool:
            digits = [int(d) for d in card_num]
            checksum = 0
            for i, digit in enumerate(reversed(digits)):
                if i % 2 == 1:
                    digit *= 2
                    if digit > 9:
                        digit -= 9
                checksum += digit
            return checksum % 10 == 0

        if not luhn_check(v):
            raise ValueError('無效的卡號（未通過 Luhn 驗證）')

        return v

    @field_validator('cvv')
    @classmethod
    def validate_cvv(cls, v: str) -> str:
        """驗證 CVV"""
        if not v.isdigit() or len(v) != 3:
            raise ValueError('CVV 必須是3位數字')
        return v

    @model_validator(mode='after')
    def validate_expiry_date(self):
        """驗證到期日期未過期"""
        current_date = datetime.now()
        expiry_date = datetime(self.expiry_year, self.expiry_month, 1)

        if expiry_date < current_date:
            raise ValueError('信用卡已過期')

        return self


class EmailList(BaseModel):
    """郵件列表模型 - 列表元素驗證"""
    subject: str = Field(description="主題")
    recipients: List[EmailStr] = Field(
        description="收件人列表",
        min_length=1,
        max_length=100
    )
    cc: List[EmailStr] = Field(
        default_factory=list,
        description="抄送列表"
    )
    bcc: List[EmailStr] = Field(
        default_factory=list,
        description="密送列表"
    )

    @model_validator(mode='after')
    def validate_no_duplicate_recipients(self):
        """驗證收件人無重複"""
        all_recipients = self.recipients + self.cc + self.bcc
        if len(all_recipients) != len(set(all_recipients)):
            raise ValueError('收件人列表中存在重複的郵箱地址')
        return self


# ============================================================================
# 重試配置示例
# ============================================================================

class StrictDataModel(BaseModel):
    """嚴格數據模型 - 用於測試重試機制"""
    value: int = Field(description="數值（必須是質數）")
    description: str = Field(description="描述（必須包含'質數'兩個字）")

    @field_validator('value')
    @classmethod
    def validate_prime(cls, v: int) -> int:
        """驗證是否為質數"""
        if v < 2:
            raise ValueError('質數必須大於1')

        for i in range(2, int(v ** 0.5) + 1):
            if v % i == 0:
                raise ValueError(f'{v} 不是質數')

        return v

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: str) -> str:
        """驗證描述必須包含'質數'"""
        if '質數' not in v:
            raise ValueError('描述必須包含"質數"兩個字')
        return v


# ============================================================================
# 輔助函數
# ============================================================================

def setup_client():
    """設置 Instructor 客戶端"""
    api_key = os.getenv("OPENAI_API_KEY", "sk-placeholder")
    openai_client = OpenAI(api_key=api_key)
    return instructor.from_openai(openai_client)


def demonstrate_field_validation(client):
    """演示字段級驗證"""
    print(f"\n{'='*60}")
    print("字段級驗證示例")
    print(f"{'='*60}")

    text = """
    創建一個用戶賬戶：
    姓名：張三
    年齡：25歲
    郵箱：zhangsan@example.com
    用戶名：zhang_san_123
    密碼：SecurePass123
    """

    try:
        user = client.chat.completions.create(
            model="gpt-4",
            response_model=ValidatedUser,
            max_retries=3,  # 最多重試3次
            messages=[
                {"role": "user", "content": f"提取用戶信息：\n{text}"}
            ]
        )

        print(f"✓ 驗證通過")
        print(f"  用戶名: {user.username}")
        print(f"  郵箱: {user.email}")
        print(f"  密碼長度: {len(user.password)} 個字符")

    except Exception as e:
        print(f"✗ 驗證失敗: {str(e)}")


def demonstrate_model_validation(client):
    """演示模型級驗證"""
    print(f"\n{'='*60}")
    print("模型級驗證示例")
    print(f"{'='*60}")

    text = """
    銀行賬戶信息：
    持有人：李四
    賬號：1234567890
    當前餘額：$5,000
    信用額度：$2,000
    可用餘額應該是餘額加信用額度
    """

    try:
        account = client.chat.completions.create(
            model="gpt-4",
            response_model=BankAccount,
            max_retries=3,
            messages=[
                {"role": "user", "content": f"提取賬戶信息：\n{text}"}
            ]
        )

        print(f"✓ 驗證通過")
        print(f"  賬戶持有人: {account.account_holder}")
        print(f"  餘額: ${account.balance:,.2f}")
        print(f"  信用額度: ${account.credit_limit:,.2f}")
        print(f"  可用餘額: ${account.available_balance:,.2f}")

    except Exception as e:
        print(f"✗ 驗證失敗: {str(e)}")


def demonstrate_date_validation(client):
    """演示日期驗證"""
    print(f"\n{'='*60}")
    print("日期邏輯驗證示例")
    print(f"{'='*60}")

    text = """
    活動：技術研討會
    開始日期：2025-03-15
    結束日期：2025-03-17
    報名截止：2025-03-10
    """

    try:
        event = client.chat.completions.create(
            model="gpt-4",
            response_model=DateRange,
            max_retries=3,
            messages=[
                {"role": "user", "content": f"提取活動信息：\n{text}"}
            ]
        )

        print(f"✓ 驗證通過")
        print(f"  活動: {event.event_name}")
        print(f"  時間: {event.start_date} 至 {event.end_date}")
        print(f"  報名截止: {event.registration_deadline}")

    except Exception as e:
        print(f"✗ 驗證失敗: {str(e)}")


def demonstrate_complex_validation(client):
    """演示複雜驗證邏輯"""
    print(f"\n{'='*60}")
    print("複雜驗證邏輯示例（三角形）")
    print(f"{'='*60}")

    text = """
    一個三角形的三條邊：
    邊 A: 3 米
    邊 B: 4 米
    邊 C: 5 米
    """

    try:
        triangle = client.chat.completions.create(
            model="gpt-4",
            response_model=Triangle,
            max_retries=3,
            messages=[
                {"role": "user", "content": f"提取三角形信息：\n{text}"}
            ]
        )

        print(f"✓ 驗證通過（符合三角形不等式）")
        print(f"  邊長: {triangle.side_a}, {triangle.side_b}, {triangle.side_c}")

    except Exception as e:
        print(f"✗ 驗證失敗: {str(e)}")


def demonstrate_retry_with_feedback(client):
    """演示帶反饋的重試機制"""
    print(f"\n{'='*60}")
    print("重試機制示例（質數驗證）")
    print(f"{'='*60}")

    text = "給我一個大於10的質數及其描述"

    try:
        result = client.chat.completions.create(
            model="gpt-4",
            response_model=StrictDataModel,
            max_retries=5,  # 更多重試次數
            messages=[
                {
                    "role": "system",
                    "content": "你是一個數學助手。當被要求提供質數時，確保數字真的是質數。"
                },
                {"role": "user", "content": text}
            ]
        )

        print(f"✓ 成功獲得有效結果")
        print(f"  質數: {result.value}")
        print(f"  描述: {result.description}")

    except Exception as e:
        print(f"✗ 達到最大重試次數仍失敗: {str(e)}")


def demonstrate_list_validation(client):
    """演示列表驗證"""
    print(f"\n{'='*60}")
    print("列表驗證示例（團隊分配）")
    print(f"{'='*60}")

    text = """
    團隊：前端開發組
    團隊負責人：李工程師
    團隊成員：李工程師、張設計師、王開發、趙測試
    最大團隊規模：5人
    """

    try:
        team = client.chat.completions.create(
            model="gpt-4",
            response_model=TeamAssignment,
            max_retries=3,
            messages=[
                {"role": "user", "content": f"提取團隊信息：\n{text}"}
            ]
        )

        print(f"✓ 驗證通過")
        print(f"  團隊: {team.team_name}")
        print(f"  負責人: {team.team_lead}")
        print(f"  成員數: {len(team.members)}")
        print(f"  成員: {', '.join(team.members)}")

    except Exception as e:
        print(f"✗ 驗證失敗: {str(e)}")


# ============================================================================
# 主程序
# ============================================================================

def main():
    """主函數 - 運行所有驗證示例"""
    print("="*60)
    print("Instructor 驗證和重試機制示例")
    print("="*60)

    client = setup_client()

    # 運行各種驗證示例
    demonstrate_field_validation(client)
    demonstrate_model_validation(client)
    demonstrate_date_validation(client)
    demonstrate_complex_validation(client)
    demonstrate_list_validation(client)
    demonstrate_retry_with_feedback(client)

    print("\n" + "="*60)
    print("驗證機制要點總結")
    print("="*60)
    print("""
1. 字段級驗證（@field_validator）：
   - 驗證單個字段的值
   - 可以訪問其他字段的值
   - 可以轉換和規範化數據

2. 模型級驗證（@model_validator）：
   - 驗證多個字段之間的關係
   - 在所有字段驗證完成後執行
   - 適合複雜的業務邏輯驗證

3. 自動重試機制：
   - 使用 max_retries 參數控制重試次數
   - 驗證失敗時自動重試
   - 將驗證錯誤反饋給 LLM

4. 最佳實踐：
   - 提供清晰的錯誤消息
   - 合理設置重試次數
   - 在描述中說明驗證規則
   - 使用適當的驗證粒度
    """)


if __name__ == "__main__":
    main()

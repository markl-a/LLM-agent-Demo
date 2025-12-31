"""
Instructor 自定義驗證示例

這個模塊深入探討如何創建自定義驗證器和約束條件。
展示了複雜業務邏輯驗證、跨字段驗證和自定義錯誤消息的技巧。

主要內容：
1. 自定義字段驗證器
2. 複雜業務規則驗證
3. 跨字段依賴驗證
4. 自定義錯誤消息
5. 條件驗證
6. 驗證器組合和復用

作者: Instructor 示例
日期: 2025-01-01
"""

import os
import re
from typing import List, Optional, Any
from datetime import datetime, date, timedelta
from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
    ValidationError
)
import instructor
from openai import OpenAI


# ============================================================================
# 自定義字段驗證器
# ============================================================================

class EmailValidator(BaseModel):
    """郵箱驗證器示例"""
    email: str = Field(description="電子郵件地址")

    @field_validator('email')
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        """驗證郵箱格式

        自定義驗證規則：
        1. 必須包含 @ 符號
        2. @ 前後都要有內容
        3. 域名部分必須包含 .
        4. 不能包含空格
        """
        # 移除首尾空格
        v = v.strip()

        # 檢查空格
        if ' ' in v:
            raise ValueError('郵箱地址不能包含空格')

        # 檢查 @ 符號
        if '@' not in v:
            raise ValueError('郵箱地址必須包含 @ 符號')

        # 分割用戶名和域名
        parts = v.split('@')
        if len(parts) != 2:
            raise ValueError('郵箱地址格式不正確（只能有一個@符號）')

        username, domain = parts

        # 驗證用戶名
        if not username:
            raise ValueError('郵箱用戶名不能為空')

        if len(username) < 2:
            raise ValueError('郵箱用戶名至少需要2個字符')

        # 驗證域名
        if not domain:
            raise ValueError('郵箱域名不能為空')

        if '.' not in domain:
            raise ValueError('郵箱域名必須包含 . 符號')

        # 驗證域名格式
        domain_parts = domain.split('.')
        if any(not part for part in domain_parts):
            raise ValueError('郵箱域名格式不正確')

        # 轉換為小寫
        return v.lower()


class URLValidator(BaseModel):
    """URL 驗證器"""
    url: str = Field(description="網址")

    @field_validator('url')
    @classmethod
    def validate_url_format(cls, v: str) -> str:
        """驗證 URL 格式"""
        v = v.strip()

        # 檢查協議
        if not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('URL 必須以 http:// 或 https:// 開頭')

        # 檢查是否有域名
        if v in ['http://', 'https://']:
            raise ValueError('URL 必須包含域名')

        # 檢查域名部分
        protocol_end = v.find('://') + 3
        domain_part = v[protocol_end:].split('/')[0]

        if not domain_part:
            raise ValueError('URL 必須包含有效的域名')

        if '.' not in domain_part:
            raise ValueError('域名必須包含 . 符號')

        return v


class PhoneValidator(BaseModel):
    """電話號碼驗證器"""
    phone: str = Field(description="電話號碼")
    country_code: str = Field(default="+86", description="國家代碼")

    @field_validator('phone')
    @classmethod
    def validate_phone_number(cls, v: str) -> str:
        """驗證電話號碼格式"""
        # 移除常見分隔符
        cleaned = re.sub(r'[\s\-\(\)]', '', v)

        # 檢查是否只包含數字和可能的前導 +
        if not re.match(r'^\+?\d+$', cleaned):
            raise ValueError('電話號碼只能包含數字')

        # 移除前導 +
        if cleaned.startswith('+'):
            cleaned = cleaned[1:]

        # 檢查長度（中國手機號）
        if len(cleaned) != 11:
            raise ValueError('電話號碼必須是11位數字')

        # 檢查是否以1開頭
        if not cleaned.startswith('1'):
            raise ValueError('中國手機號必須以1開頭')

        return cleaned

    @model_validator(mode='after')
    def format_full_number(self):
        """格式化完整號碼"""
        # 格式化為 +86 138-0000-0000
        phone = self.phone
        formatted = f"{phone[:3]}-{phone[3:7]}-{phone[7:]}"
        self.phone = formatted
        return self


# ============================================================================
# 業務規則驗證
# ============================================================================

class OrderItem(BaseModel):
    """訂單項"""
    product_id: str = Field(description="產品ID")
    quantity: int = Field(description="數量", gt=0)
    unit_price: float = Field(description="單價", gt=0)
    discount: float = Field(default=0, description="折扣（0-1之間）", ge=0, le=1)

    @field_validator('discount')
    @classmethod
    def validate_discount(cls, v: float) -> float:
        """驗證折扣合理性"""
        # 折扣不能超過50%（業務規則）
        if v > 0.5:
            raise ValueError('折扣不能超過50%')
        return v

    def get_subtotal(self) -> float:
        """計算小計"""
        return self.quantity * self.unit_price * (1 - self.discount)


class Order(BaseModel):
    """訂單模型 - 複雜業務驗證"""
    order_id: str = Field(description="訂單ID")
    customer_id: str = Field(description="客戶ID")
    items: List[OrderItem] = Field(description="訂單項列表", min_length=1)
    shipping_fee: float = Field(description="運費", ge=0)
    tax_rate: float = Field(description="稅率", ge=0, le=1)
    total_amount: float = Field(description="總金額", gt=0)

    @model_validator(mode='after')
    def validate_total_amount(self):
        """驗證總金額計算是否正確"""
        # 計算預期總金額
        subtotal = sum(item.get_subtotal() for item in self.items)
        expected_total = subtotal + self.shipping_fee
        expected_total = expected_total * (1 + self.tax_rate)

        # 允許0.01的誤差（浮點數精度）
        if abs(self.total_amount - expected_total) > 0.01:
            raise ValueError(
                f'總金額不正確：期望 ${expected_total:.2f}，實際 ${self.total_amount:.2f}'
            )

        return self

    @model_validator(mode='after')
    def validate_free_shipping(self):
        """驗證免運費規則"""
        # 業務規則：訂單金額超過$100免運費
        subtotal = sum(item.get_subtotal() for item in self.items)

        if subtotal >= 100 and self.shipping_fee > 0:
            raise ValueError('訂單金額超過$100應該免運費')

        return self


class Appointment(BaseModel):
    """預約模型 - 時間驗證"""
    appointment_id: str = Field(description="預約ID")
    customer_name: str = Field(description="客戶姓名")
    appointment_date: date = Field(description="預約日期")
    start_time: str = Field(description="開始時間（HH:MM格式）")
    end_time: str = Field(description="結束時間（HH:MM格式）")
    service_type: str = Field(description="服務類型")

    @field_validator('start_time', 'end_time')
    @classmethod
    def validate_time_format(cls, v: str) -> str:
        """驗證時間格式"""
        if not re.match(r'^\d{2}:\d{2}$', v):
            raise ValueError('時間格式必須是 HH:MM')

        hour, minute = map(int, v.split(':'))

        if hour < 0 or hour > 23:
            raise ValueError('小時必須在 0-23 之間')

        if minute < 0 or minute > 59:
            raise ValueError('分鐘必須在 0-59 之間')

        return v

    @model_validator(mode='after')
    def validate_appointment(self):
        """驗證預約規則"""
        # 1. 預約日期不能是過去
        if self.appointment_date < date.today():
            raise ValueError('預約日期不能是過去的日期')

        # 2. 結束時間必須晚於開始時間
        start_hour, start_min = map(int, self.start_time.split(':'))
        end_hour, end_min = map(int, self.end_time.split(':'))

        start_minutes = start_hour * 60 + start_min
        end_minutes = end_hour * 60 + end_min

        if end_minutes <= start_minutes:
            raise ValueError('結束時間必須晚於開始時間')

        # 3. 預約時長至少30分鐘
        duration = end_minutes - start_minutes
        if duration < 30:
            raise ValueError('預約時長至少需要30分鐘')

        # 4. 營業時間檢查（9:00-18:00）
        if start_hour < 9 or end_hour > 18:
            raise ValueError('預約時間必須在營業時間內（9:00-18:00）')

        return self


# ============================================================================
# 跨字段依賴驗證
# ============================================================================

class PasswordChange(BaseModel):
    """密碼修改模型 - 跨字段驗證"""
    old_password: str = Field(description="舊密碼")
    new_password: str = Field(description="新密碼")
    confirm_password: str = Field(description="確認密碼")

    @field_validator('new_password')
    @classmethod
    def validate_password_strength(cls, v: str, info) -> str:
        """驗證密碼強度"""
        if len(v) < 8:
            raise ValueError('密碼長度至少8個字符')

        if not any(c.isupper() for c in v):
            raise ValueError('密碼必須包含至少一個大寫字母')

        if not any(c.islower() for c in v):
            raise ValueError('密碼必須包含至少一個小寫字母')

        if not any(c.isdigit() for c in v):
            raise ValueError('密碼必須包含至少一個數字')

        if not any(c in '!@#$%^&*()_+-=' for c in v):
            raise ValueError('密碼必須包含至少一個特殊字符')

        # 檢查是否與舊密碼相同
        if 'old_password' in info.data and v == info.data['old_password']:
            raise ValueError('新密碼不能與舊密碼相同')

        return v

    @model_validator(mode='after')
    def validate_password_match(self):
        """驗證兩次密碼輸入是否一致"""
        if self.new_password != self.confirm_password:
            raise ValueError('兩次輸入的密碼不一致')
        return self


class DateRange(BaseModel):
    """日期範圍模型 - 相互依賴驗證"""
    start_date: date = Field(description="開始日期")
    end_date: date = Field(description="結束日期")
    max_days: int = Field(default=365, description="最大天數限制")

    @model_validator(mode='after')
    def validate_date_range(self):
        """驗證日期範圍"""
        # 1. 結束日期必須在開始日期之後
        if self.end_date <= self.start_date:
            raise ValueError('結束日期必須在開始日期之後')

        # 2. 日期範圍不能超過最大天數
        delta = (self.end_date - self.start_date).days
        if delta > self.max_days:
            raise ValueError(f'日期範圍不能超過 {self.max_days} 天')

        # 3. 開始日期不能是未來（業務規則）
        if self.start_date > date.today():
            raise ValueError('開始日期不能是未來日期')

        return self


class BudgetAllocation(BaseModel):
    """預算分配模型 - 總和驗證"""
    total_budget: float = Field(description="總預算", gt=0)
    marketing: float = Field(description="市場營銷預算", ge=0)
    development: float = Field(description="研發預算", ge=0)
    operations: float = Field(description="運營預算", ge=0)
    reserve: float = Field(description="儲備金", ge=0)

    @model_validator(mode='after')
    def validate_budget_allocation(self):
        """驗證預算分配"""
        # 1. 各項預算之和必須等於總預算
        allocated = (
            self.marketing +
            self.development +
            self.operations +
            self.reserve
        )

        if abs(allocated - self.total_budget) > 0.01:
            raise ValueError(
                f'預算分配總和（${allocated:.2f}）必須等於總預算（${self.total_budget:.2f}）'
            )

        # 2. 儲備金至少佔10%（業務規則）
        min_reserve = self.total_budget * 0.1
        if self.reserve < min_reserve:
            raise ValueError(f'儲備金至少需要 ${min_reserve:.2f}（總預算的10%）')

        # 3. 研發預算不能超過50%
        max_development = self.total_budget * 0.5
        if self.development > max_development:
            raise ValueError(f'研發預算不能超過 ${max_development:.2f}（總預算的50%）')

        return self


# ============================================================================
# 條件驗證
# ============================================================================

class ShippingAddress(BaseModel):
    """配送地址模型 - 條件驗證"""
    recipient_name: str = Field(description="收件人姓名")
    phone: str = Field(description="聯繫電話")
    country: str = Field(description="國家")
    province: str = Field(description="省/州")
    city: str = Field(description="城市")
    street: str = Field(description="街道地址")
    postal_code: str = Field(description="郵政編碼")
    is_international: bool = Field(default=False, description="是否國際配送")

    @field_validator('postal_code')
    @classmethod
    def validate_postal_code(cls, v: str, info) -> str:
        """根據國家驗證郵政編碼格式"""
        if 'country' not in info.data:
            return v

        country = info.data['country']

        # 中國郵政編碼：6位數字
        if country == '中國':
            if not re.match(r'^\d{6}$', v):
                raise ValueError('中國郵政編碼必須是6位數字')

        # 美國郵政編碼：5位數字或5+4格式
        elif country == '美國':
            if not re.match(r'^\d{5}(-\d{4})?$', v):
                raise ValueError('美國郵政編碼格式不正確')

        return v

    @model_validator(mode='after')
    def validate_international_shipping(self):
        """驗證國際配送規則"""
        # 如果是國際配送，需要額外信息
        if self.is_international and self.country == '中國':
            raise ValueError('國內地址不應標記為國際配送')

        return self


class PaymentMethod(BaseModel):
    """支付方式模型 - 條件驗證"""
    payment_type: str = Field(description="支付類型：credit_card, bank_transfer, paypal")
    amount: float = Field(description="金額", gt=0)

    # 信用卡相關（條件性必填）
    card_number: Optional[str] = Field(default=None, description="卡號")
    card_holder: Optional[str] = Field(default=None, description="持卡人")
    expiry_date: Optional[str] = Field(default=None, description="到期日期（MM/YY）")
    cvv: Optional[str] = Field(default=None, description="CVV")

    # 銀行轉賬相關（條件性必填）
    bank_name: Optional[str] = Field(default=None, description="銀行名稱")
    account_number: Optional[str] = Field(default=None, description="賬號")

    # PayPal 相關（條件性必填）
    paypal_email: Optional[str] = Field(default=None, description="PayPal郵箱")

    @model_validator(mode='after')
    def validate_payment_details(self):
        """根據支付類型驗證必要字段"""
        if self.payment_type == 'credit_card':
            # 信用卡支付需要卡信息
            if not all([self.card_number, self.card_holder, self.expiry_date, self.cvv]):
                raise ValueError('信用卡支付需要提供完整的卡信息')

            # 驗證卡號（簡單檢查）
            if not re.match(r'^\d{16}$', self.card_number.replace(' ', '')):
                raise ValueError('信用卡號必須是16位數字')

            # 驗證CVV
            if not re.match(r'^\d{3,4}$', self.cvv):
                raise ValueError('CVV必須是3或4位數字')

        elif self.payment_type == 'bank_transfer':
            # 銀行轉賬需要銀行信息
            if not all([self.bank_name, self.account_number]):
                raise ValueError('銀行轉賬需要提供銀行名稱和賬號')

        elif self.payment_type == 'paypal':
            # PayPal 需要郵箱
            if not self.paypal_email:
                raise ValueError('PayPal支付需要提供PayPal郵箱')

            # 驗證郵箱格式
            if '@' not in self.paypal_email:
                raise ValueError('PayPal郵箱格式不正確')

        else:
            raise ValueError(f'不支持的支付類型: {self.payment_type}')

        return self


# ============================================================================
# 自定義錯誤消息
# ============================================================================

class UserRegistration(BaseModel):
    """用戶註冊模型 - 自定義錯誤消息"""
    username: str = Field(description="用戶名（3-20個字符）")
    password: str = Field(description="密碼（至少8個字符）")
    email: str = Field(description="電子郵件")
    age: int = Field(description="年齡", ge=18)
    terms_accepted: bool = Field(description="是否接受條款")

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """驗證用戶名 - 提供詳細錯誤消息"""
        if len(v) < 3:
            raise ValueError(
                '用戶名太短：用戶名至少需要3個字符。'
                '請選擇一個更長的用戶名。'
            )

        if len(v) > 20:
            raise ValueError(
                f'用戶名太長：用戶名最多20個字符，您的用戶名有{len(v)}個字符。'
                '請縮短用戶名。'
            )

        if not v[0].isalpha():
            raise ValueError(
                '用戶名格式錯誤：用戶名必須以字母開頭。'
                f'您的用戶名以 "{v[0]}" 開頭，這是不允許的。'
            )

        if not all(c.isalnum() or c == '_' for c in v):
            invalid_chars = [c for c in v if not (c.isalnum() or c == '_')]
            raise ValueError(
                f'用戶名包含無效字符：{", ".join(set(invalid_chars))}。'
                '用戶名只能包含字母、數字和下劃線。'
            )

        return v.lower()

    @field_validator('age')
    @classmethod
    def validate_age(cls, v: int) -> int:
        """驗證年齡 - 提供友好的錯誤消息"""
        if v < 18:
            raise ValueError(
                f'年齡限制：您必須年滿18歲才能註冊。'
                f'您當前的年齡是{v}歲，還需要等待{18-v}年。'
            )

        if v > 120:
            raise ValueError(
                f'年齡異常：您輸入的年齡是{v}歲，這似乎不太合理。'
                '請檢查並輸入正確的年齡。'
            )

        return v

    @model_validator(mode='after')
    def validate_terms(self):
        """驗證條款接受"""
        if not self.terms_accepted:
            raise ValueError(
                '必須接受服務條款：為了完成註冊，'
                '您必須閱讀並接受我們的服務條款和隱私政策。'
            )
        return self


# ============================================================================
# 輔助函數和測試
# ============================================================================

def setup_client():
    """設置 Instructor 客戶端"""
    api_key = os.getenv("OPENAI_API_KEY", "sk-placeholder")
    openai_client = OpenAI(api_key=api_key)
    return instructor.from_openai(openai_client)


def test_email_validation(client):
    """測試郵箱驗證"""
    print(f"\n{'='*60}")
    print("測試郵箱驗證")
    print(f"{'='*60}")

    test_cases = [
        "請驗證這個郵箱：zhang.san@company.com",
        "郵箱地址：invalid@",
        "我的郵箱是 test @ example.com"
    ]

    for text in test_cases:
        print(f"\n輸入: {text}")
        try:
            result = client.chat.completions.create(
                model="gpt-4",
                response_model=EmailValidator,
                max_retries=2,
                messages=[
                    {"role": "user", "content": text}
                ]
            )
            print(f"  ✓ 有效郵箱: {result.email}")
        except Exception as e:
            print(f"  ✗ 驗證失敗: {str(e)[:100]}")


def test_order_validation(client):
    """測試訂單驗證"""
    print(f"\n{'='*60}")
    print("測試訂單驗證（複雜業務規則）")
    print(f"{'='*60}")

    text = """
    訂單ID: ORD-12345
    客戶ID: CUST-001

    訂單項：
    1. 產品 PROD-A，數量2，單價$50，折扣10%
    2. 產品 PROD-B，數量1，單價$30，無折扣

    運費：$0（訂單超過$100免運費）
    稅率：10%
    總金額：$143（(2*50*0.9 + 30) * 1.1）
    """

    try:
        order = client.chat.completions.create(
            model="gpt-4",
            response_model=Order,
            max_retries=3,
            messages=[
                {"role": "user", "content": f"提取訂單信息：\n{text}"}
            ]
        )

        print(f"\n✓ 訂單驗證通過")
        print(f"  訂單ID: {order.order_id}")
        print(f"  項目數: {len(order.items)}")
        print(f"  總金額: ${order.total_amount:.2f}")

    except Exception as e:
        print(f"\n✗ 訂單驗證失敗: {str(e)}")


def test_appointment_validation(client):
    """測試預約驗證"""
    print(f"\n{'='*60}")
    print("測試預約驗證（時間規則）")
    print(f"{'='*60}")

    text = """
    預約ID: APT-001
    客戶：張三
    日期：2025-02-15
    時間：10:00 到 11:30
    服務：咨詢服務
    """

    try:
        appointment = client.chat.completions.create(
            model="gpt-4",
            response_model=Appointment,
            max_retries=3,
            messages=[
                {"role": "user", "content": f"提取預約信息：\n{text}"}
            ]
        )

        print(f"\n✓ 預約驗證通過")
        print(f"  客戶: {appointment.customer_name}")
        print(f"  日期: {appointment.appointment_date}")
        print(f"  時間: {appointment.start_time} - {appointment.end_time}")

    except Exception as e:
        print(f"\n✗ 預約驗證失敗: {str(e)}")


# ============================================================================
# 主程序
# ============================================================================

def main():
    """主函數 - 運行所有自定義驗證示例"""
    print("="*60)
    print("Instructor 自定義驗證示例")
    print("="*60)

    client = setup_client()

    # 測試各種驗證
    test_email_validation(client)
    test_order_validation(client)
    test_appointment_validation(client)

    print("\n" + "="*60)
    print("自定義驗證要點總結")
    print("="*60)
    print("""
1. 字段級驗證（@field_validator）：
   - 驗證單個字段的格式和內容
   - 可以訪問其他字段值（通過 info.data）
   - 可以轉換和規範化數據
   - 提供清晰的錯誤消息

2. 模型級驗證（@model_validator）：
   - 驗證多個字段之間的關係
   - 實現複雜的業務規則
   - 在所有字段驗證完成後執行
   - mode='after' 表示在字段驗證之後

3. 跨字段驗證：
   - 使用 info.data 訪問其他字段
   - 在模型驗證器中檢查字段關係
   - 確保數據一致性

4. 條件驗證：
   - 根據某個字段值驗證其他字段
   - 使用 Optional 字段配合驗證器
   - 實現動態驗證規則

5. 錯誤消息最佳實踐：
   - 描述具體的問題
   - 提供解決方案
   - 包含相關的數值信息
   - 使用友好的語言

6. 驗證器設計原則：
   - 單一職責：每個驗證器專注一個規則
   - 可復用：將通用驗證邏輯提取為獨立驗證器
   - 性能考慮：避免在驗證器中執行耗時操作
   - 完整性：考慮邊界情況和異常輸入
    """)


if __name__ == "__main__":
    main()

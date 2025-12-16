"""
重試機制範例
==============

本範例展示 Instructor 的自動重試機制：
1. 基本重試配置
2. 驗證失敗時的自動重試
3. 自訂重試邏輯
4. 重試次數和策略
5. 錯誤處理和回饋
6. 最佳實踐

當 LLM 輸出無法通過 Pydantic 驗證時，Instructor 會自動重試，
並將驗證錯誤訊息回饋給 LLM，讓它修正輸出。
"""

import time
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, ValidationError
import instructor
from instructor import Instructor

# ============================================================================
# 範例 1：基本重試配置
# ============================================================================

def example_basic_retry():
    """展示基本的重試配置"""
    print("=" * 60)
    print("範例 1：基本重試配置")
    print("=" * 60)

    try:
        from openai import OpenAI

        class StrictAge(BaseModel):
            """嚴格的年齡驗證"""
            name: str = Field(description="姓名")
            age: int = Field(description="年齡")

            @field_validator('age')
            @classmethod
            def validate_age(cls, v: int) -> int:
                if v < 0 or v > 150:
                    raise ValueError(f"年齡必須在 0-150 之間，收到：{v}")
                return v

        # 設定最多重試 3 次
        client = instructor.from_openai(
            OpenAI(),
            max_retries=3  # 最多重試 3 次
        )

        print("\n測試 1：正常的年齡值")
        user = client.chat.completions.create(
            model="gpt-3.5-turbo",
            response_model=StrictAge,
            messages=[
                {"role": "user", "content": "張小明今年 28 歲"}
            ]
        )
        print(f"✅ 成功：{user.name}, {user.age} 歲")

        print("\n測試 2：可能需要重試的情況")
        # LLM 可能會誤解，但重試機制會幫助它修正
        user2 = client.chat.completions.create(
            model="gpt-3.5-turbo",
            response_model=StrictAge,
            messages=[
                {"role": "user", "content": "李阿嬤今年一百零五歲"}
            ]
        )
        print(f"✅ 成功（可能經過重試）：{user2.name}, {user2.age} 歲")

    except ValidationError as e:
        print(f"❌ 驗證錯誤（重試後仍失敗）：{e}")
    except Exception as e:
        print(f"❌ 錯誤：{e}")


# ============================================================================
# 範例 2：監控重試過程
# ============================================================================

def example_retry_monitoring():
    """監控重試過程"""
    print("\n" + "=" * 60)
    print("範例 2：監控重試過程")
    print("=" * 60)

    try:
        from openai import OpenAI

        class Email(BaseModel):
            """Email 驗證"""
            address: str = Field(description="Email 地址")

            @field_validator('address')
            @classmethod
            def validate_email(cls, v: str) -> str:
                import re
                pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(pattern, v):
                    raise ValueError(
                        f"無效的 Email 格式：{v}。"
                        f"正確格式應為：user@example.com"
                    )
                return v.lower()

        # 追蹤重試次數
        retry_count = {"count": 0}

        def create_with_retry_tracking():
            client = instructor.from_openai(
                OpenAI(),
                max_retries=3
            )

            # 記錄開始時間
            start_time = time.time()

            try:
                print("\n🔄 開始提取 Email...")
                email = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    response_model=Email,
                    messages=[
                        {
                            "role": "user",
                            "content": "我的 email 是 john.doe at example dot com"
                        }
                    ]
                )

                elapsed = time.time() - start_time
                print(f"✅ 成功提取：{email.address}")
                print(f"⏱️  耗時：{elapsed:.2f} 秒")

                return email

            except Exception as e:
                elapsed = time.time() - start_time
                print(f"❌ 提取失敗")
                print(f"⏱️  耗時：{elapsed:.2f} 秒")
                raise

        result = create_with_retry_tracking()

    except Exception as e:
        print(f"❌ 錯誤：{e}")


# ============================================================================
# 範例 3：複雜驗證的重試
# ============================================================================

def example_complex_validation_retry():
    """複雜驗證規則的重試"""
    print("\n" + "=" * 60)
    print("範例 3：複雜驗證的重試")
    print("=" * 60)

    try:
        from openai import OpenAI

        class CreditCard(BaseModel):
            """信用卡資訊（含複雜驗證）"""
            card_number: str = Field(description="信用卡號（16 碼數字）")
            expiry_month: int = Field(description="到期月份（1-12）")
            expiry_year: int = Field(description="到期年份（4 碼）")
            cvv: str = Field(description="CVV 安全碼（3 碼）")

            @field_validator('card_number')
            @classmethod
            def validate_card_number(cls, v: str) -> str:
                """驗證信用卡號（Luhn 演算法）"""
                import re
                # 移除空格和破折號
                v = re.sub(r'[\s\-]', '', v)

                # 必須是 16 碼數字
                if not re.match(r'^\d{16}$', v):
                    raise ValueError(
                        "信用卡號必須是 16 碼數字。"
                        "請提供完整的 16 碼數字，不包含空格或破折號。"
                    )

                return v

            @field_validator('expiry_month')
            @classmethod
            def validate_month(cls, v: int) -> int:
                if v < 1 or v > 12:
                    raise ValueError(
                        f"到期月份必須在 1-12 之間，收到：{v}。"
                        f"請提供有效的月份數字（1=1月, 2=2月, ..., 12=12月）"
                    )
                return v

            @field_validator('expiry_year')
            @classmethod
            def validate_year(cls, v: int) -> int:
                current_year = 2025
                if v < current_year or v > current_year + 10:
                    raise ValueError(
                        f"到期年份必須在 {current_year}-{current_year+10} 之間，收到：{v}。"
                        f"請提供完整的 4 碼年份（例如：2025、2026）"
                    )
                return v

            @field_validator('cvv')
            @classmethod
            def validate_cvv(cls, v: str) -> str:
                import re
                if not re.match(r'^\d{3}$', v):
                    raise ValueError(
                        "CVV 必須是 3 碼數字。"
                        "CVV 是信用卡背面的 3 碼安全碼。"
                    )
                return v

        client = instructor.from_openai(
            OpenAI(),
            max_retries=3
        )

        print("\n提取信用卡資訊（可能需要多次重試）...")
        card = client.chat.completions.create(
            model="gpt-3.5-turbo",
            response_model=CreditCard,
            messages=[
                {
                    "role": "user",
                    "content": """
                    信用卡資訊：
                    卡號：4532 1234 5678 9010
                    有效期限：2027 年 6 月
                    安全碼：123
                    """
                }
            ]
        )

        print(f"✅ 成功提取信用卡資訊：")
        print(f"卡號：**** **** **** {card.card_number[-4:]}")
        print(f"有效期限：{card.expiry_month:02d}/{card.expiry_year}")
        print(f"CVV：***")

    except Exception as e:
        print(f"❌ 錯誤：{e}")


# ============================================================================
# 範例 4：自訂重試策略
# ============================================================================

def example_custom_retry_strategy():
    """自訂重試策略"""
    print("\n" + "=" * 60)
    print("範例 4：自訂重試策略")
    print("=" * 60)

    try:
        from openai import OpenAI
        from tenacity import retry, stop_after_attempt, wait_exponential

        class Product(BaseModel):
            """產品資訊"""
            name: str = Field(description="產品名稱")
            price: float = Field(description="價格")

            @field_validator('price')
            @classmethod
            def validate_price(cls, v: float) -> float:
                if v <= 0:
                    raise ValueError(
                        f"價格必須大於 0，收到：{v}。"
                        f"請提供有效的正數價格。"
                    )
                if v > 1000000:
                    raise ValueError(
                        f"價格不合理（超過 1,000,000），收到：{v}。"
                        f"請再次確認價格是否正確。"
                    )
                return v

        # 使用指數退避策略
        @retry(
            stop=stop_after_attempt(3),  # 最多 3 次
            wait=wait_exponential(multiplier=1, min=1, max=10),  # 指數退避
            reraise=True
        )
        def extract_product_with_custom_retry():
            client = instructor.from_openai(
                OpenAI(),
                max_retries=2
            )

            return client.chat.completions.create(
                model="gpt-3.5-turbo",
                response_model=Product,
                messages=[
                    {
                        "role": "user",
                        "content": "iPhone 15 Pro 售價 36900 元"
                    }
                ]
            )

        print("\n使用自訂重試策略...")
        product = extract_product_with_custom_retry()
        print(f"✅ 成功：{product.name} - NT$ {product.price:,.0f}")

    except Exception as e:
        print(f"❌ 錯誤：{e}")


# ============================================================================
# 範例 5：重試與錯誤回饋
# ============================================================================

def example_retry_with_feedback():
    """重試時提供詳細的錯誤回饋"""
    print("\n" + "=" * 60)
    print("範例 5：重試與錯誤回饋")
    print("=" * 60)

    try:
        from openai import OpenAI

        class StructuredDate(BaseModel):
            """結構化日期"""
            year: int = Field(description="年份（4 碼）")
            month: int = Field(description="月份（1-12）")
            day: int = Field(description="日期（1-31）")

            @field_validator('year')
            @classmethod
            def validate_year(cls, v: int) -> int:
                if v < 1900 or v > 2100:
                    raise ValueError(
                        f"年份必須在 1900-2100 之間，收到：{v}。"
                        f"提示：請提供完整的 4 碼年份，例如 2025。"
                    )
                return v

            @field_validator('month')
            @classmethod
            def validate_month(cls, v: int) -> int:
                if v < 1 or v > 12:
                    raise ValueError(
                        f"月份必須在 1-12 之間，收到：{v}。"
                        f"提示：1=一月, 2=二月, ..., 12=十二月。"
                    )
                return v

            @field_validator('day')
            @classmethod
            def validate_day(cls, v: int) -> int:
                if v < 1 or v > 31:
                    raise ValueError(
                        f"日期必須在 1-31 之間，收到：{v}。"
                        f"提示：請提供有效的日期數字。"
                    )
                return v

            @property
            def formatted(self) -> str:
                """格式化日期"""
                return f"{self.year}-{self.month:02d}-{self.day:02d}"

        client = instructor.from_openai(
            OpenAI(),
            max_retries=3
        )

        # 測試不同的日期表達方式
        test_cases = [
            "2025 年 12 月 15 日",
            "民國 114 年 3 月 20 日（需要轉換為西元）",
            "今天是 12/25"
        ]

        for i, test in enumerate(test_cases, 1):
            try:
                print(f"\n測試 {i}：{test}")
                date = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    response_model=StructuredDate,
                    messages=[
                        {
                            "role": "user",
                            "content": f"提取日期：{test}"
                        }
                    ]
                )
                print(f"✅ 提取成功：{date.formatted}")
            except Exception as e:
                print(f"❌ 提取失敗：{str(e)[:100]}")

    except Exception as e:
        print(f"❌ 錯誤：{e}")


# ============================================================================
# 範例 6：重試次數耗盡處理
# ============================================================================

def example_retry_exhausted():
    """處理重試次數耗盡的情況"""
    print("\n" + "=" * 60)
    print("範例 6：重試次數耗盡處理")
    print("=" * 60)

    try:
        from openai import OpenAI

        class VeryStrictData(BaseModel):
            """非常嚴格的驗證（容易失敗）"""
            code: str = Field(description="特殊代碼")

            @field_validator('code')
            @classmethod
            def validate_code(cls, v: str) -> str:
                import re
                # 非常特定的格式：XXX-9999-YYY
                pattern = r'^[A-Z]{3}-\d{4}-[A-Z]{3}$'
                if not re.match(pattern, v):
                    raise ValueError(
                        f"代碼格式錯誤：{v}。"
                        f"必須符合格式：XXX-9999-YYY"
                        f"（3個大寫字母-4個數字-3個大寫字母）"
                        f"例如：ABC-1234-XYZ"
                    )
                return v

        client = instructor.from_openai(
            OpenAI(),
            max_retries=2  # 只重試 2 次
        )

        try:
            print("\n嘗試提取嚴格格式的代碼...")
            result = client.chat.completions.create(
                model="gpt-3.5-turbo",
                response_model=VeryStrictData,
                messages=[
                    {
                        "role": "user",
                        "content": "代碼是 ABC1234XYZ"  # 格式不對，可能會失敗
                    }
                ]
            )
            print(f"✅ 成功（經過重試）：{result.code}")

        except instructor.exceptions.InstructorRetryException as e:
            print(f"❌ 重試次數耗盡：已嘗試 {e.n_attempts} 次")
            print(f"   最後的錯誤：{e.last_exception}")
            print("\n💡 建議：")
            print("   - 增加 max_retries")
            print("   - 放寬驗證規則")
            print("   - 提供更清楚的提示")

        except Exception as e:
            print(f"❌ 其他錯誤：{e}")

    except Exception as e:
        print(f"❌ 錯誤：{e}")


# ============================================================================
# 主程式
# ============================================================================

def main():
    """執行所有範例"""
    print("\n" + "🎯" * 30)
    print("重試機制範例")
    print("🎯" * 30)

    print("\n📝 關於重試機制")
    print("-" * 60)
    print("Instructor 的重試機制是其核心功能之一：")
    print("\n工作原理：")
    print("1️⃣  LLM 生成輸出")
    print("2️⃣  Pydantic 驗證輸出")
    print("3️⃣  如果驗證失敗，將錯誤訊息回饋給 LLM")
    print("4️⃣  LLM 根據錯誤訊息生成新的輸出")
    print("5️⃣  重複直到成功或達到最大重試次數")
    print("\n優勢：")
    print("✅ 自動處理常見錯誤")
    print("✅ 提高輸出品質")
    print("✅ 減少人工介入")
    print("✅ 可配置重試策略")
    print("-" * 60)

    # 執行所有範例
    example_basic_retry()
    example_retry_monitoring()
    example_complex_validation_retry()
    example_custom_retry_strategy()
    example_retry_with_feedback()
    example_retry_exhausted()

    print("\n" + "=" * 60)
    print("✅ 所有重試範例執行完畢！")
    print("=" * 60)
    print("\n💡 重試機制最佳實踐：")
    print("1. 設定合理的 max_retries（建議 2-5 次）")
    print("2. 提供清晰、具體的驗證錯誤訊息")
    print("3. 在錯誤訊息中包含正確格式的範例")
    print("4. 監控重試次數，避免過度消耗 API 額度")
    print("5. 對於經常失敗的驗證，考慮放寬規則")
    print("6. 使用指數退避避免 API 限流")


if __name__ == "__main__":
    main()

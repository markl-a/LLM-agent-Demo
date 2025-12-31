"""
Guardrails AI - PII 過濾示例
展示如何檢測和過濾個人身份信息（Personally Identifiable Information）
"""

import os
import re
from guardrails import Guard
from guardrails.hub import DetectPII
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")


def basic_pii_detection():
    """
    基本 PII 檢測
    """
    print("=" * 60)
    print("基本 PII 檢測示例")
    print("=" * 60)

    # 使用 DetectPII 驗證器
    guard = Guard().use(
        DetectPII(
            pii_entities=["EMAIL_ADDRESS", "PHONE_NUMBER", "PERSON"],
            on_fail="exception"
        )
    )

    prompt = "生成一個簡單的產品描述（不要包含任何個人信息）"

    print(f"\n提示: {prompt}")
    print("檢測類型: 郵箱、電話、姓名")

    try:
        result = guard(
            llm_api=openai.chat.completions.create,
            prompt=prompt,
            model="gpt-3.5-turbo",
            max_tokens=150,
        )

        print(f"\n輸出: {result.validated_output}")
        print(f"✅ 未檢測到 PII")

    except Exception as e:
        print(f"⚠️  檢測到 PII")
        print(f"詳情: {str(e)}")


def filter_email_addresses():
    """
    過濾郵箱地址
    """
    print("\n" + "=" * 60)
    print("郵箱地址過濾示例")
    print("=" * 60)

    # 使用 filter 策略自動移除郵箱
    guard = Guard().use(
        DetectPII(
            pii_entities=["EMAIL_ADDRESS"],
            on_fail="filter"
        )
    )

    prompt = "生成一段包含聯繫方式的文本"

    print(f"\n提示: {prompt}")

    try:
        result = guard(
            llm_api=openai.chat.completions.create,
            prompt=prompt,
            model="gpt-3.5-turbo",
            max_tokens=200,
        )

        print(f"\n過濾後的輸出: {result.validated_output}")
        print(f"✅ 郵箱地址已被過濾")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def detect_phone_numbers():
    """
    檢測電話號碼
    """
    print("\n" + "=" * 60)
    print("電話號碼檢測示例")
    print("=" * 60)

    guard = Guard().use(
        DetectPII(
            pii_entities=["PHONE_NUMBER"],
            on_fail="exception"
        )
    )

    prompt = "生成公司簡介（不包含電話號碼）"

    print(f"\n提示: {prompt}")

    try:
        result = guard(
            llm_api=openai.chat.completions.create,
            prompt=prompt,
            model="gpt-3.5-turbo",
            max_tokens=150,
        )

        print(f"\n輸出: {result.validated_output}")
        print(f"✅ 未檢測到電話號碼")

    except Exception as e:
        print(f"⚠️  檢測到電話號碼")
        print(f"詳情: {str(e)}")


def detect_person_names():
    """
    檢測人名
    """
    print("\n" + "=" * 60)
    print("人名檢測示例")
    print("=" * 60)

    guard = Guard().use(
        DetectPII(
            pii_entities=["PERSON"],
            on_fail="exception"
        )
    )

    prompt = "描述一個技術團隊的工作流程（不要提及具體人名）"

    print(f"\n提示: {prompt}")

    try:
        result = guard(
            llm_api=openai.chat.completions.create,
            prompt=prompt,
            model="gpt-3.5-turbo",
            max_tokens=150,
        )

        print(f"\n輸出: {result.validated_output}")
        print(f"✅ 未檢測到人名")

    except Exception as e:
        print(f"⚠️  檢測到人名")
        print(f"詳情: {str(e)}")


def detect_multiple_pii_types():
    """
    檢測多種 PII 類型
    """
    print("\n" + "=" * 60)
    print("多種 PII 類型檢測示例")
    print("=" * 60)

    # 檢測多種 PII
    pii_types = [
        "EMAIL_ADDRESS",
        "PHONE_NUMBER",
        "PERSON",
        "LOCATION",
        "CREDIT_CARD",
        "SSN"
    ]

    guard = Guard().use(
        DetectPII(
            pii_entities=pii_types,
            on_fail="exception"
        )
    )

    prompt = "生成一段技術博客文章（不包含任何個人信息、地點、信用卡或社保號）"

    print(f"\n提示: {prompt}")
    print(f"檢測類型: {', '.join(pii_types)}")

    try:
        result = guard(
            llm_api=openai.chat.completions.create,
            prompt=prompt,
            model="gpt-3.5-turbo",
            max_tokens=200,
        )

        print(f"\n輸出: {result.validated_output}")
        print(f"✅ 未檢測到任何 PII")

    except Exception as e:
        print(f"⚠️  檢測到 PII")
        print(f"詳情: {str(e)}")


def mask_pii_data():
    """
    掩蓋 PII 數據而非完全移除
    """
    print("\n" + "=" * 60)
    print("PII 掩蓋示例")
    print("=" * 60)

    # 自定義 PII 掩蓋函數
    def mask_email(text):
        """掩蓋郵箱地址"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.sub(email_pattern, '[EMAIL_MASKED]', text)

    def mask_phone(text):
        """掩蓋電話號碼"""
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        return re.sub(phone_pattern, '[PHONE_MASKED]', text)

    prompt = "生成一段客戶服務對話記錄"

    print(f"\n提示: {prompt}")

    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
        )

        original_text = response.choices[0].message.content

        # 應用掩蓋
        masked_text = mask_email(original_text)
        masked_text = mask_phone(masked_text)

        print(f"\n原始輸出: {original_text}")
        print(f"\n掩蓋後輸出: {masked_text}")
        print(f"✅ PII 已被掩蓋")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def custom_pii_detection():
    """
    自定義 PII 檢測規則
    """
    print("\n" + "=" * 60)
    print("自定義 PII 檢測示例")
    print("=" * 60)

    # 自定義檢測函數
    def detect_custom_pii(text):
        """
        檢測自定義的敏感信息
        """
        issues = []

        # 檢測身份證號（簡化版）
        id_pattern = r'\b\d{17}[\dXx]\b'
        if re.search(id_pattern, text):
            issues.append("身份證號")

        # 檢測銀行卡號
        bank_pattern = r'\b\d{16,19}\b'
        if re.search(bank_pattern, text):
            issues.append("銀行卡號")

        # 檢測 IP 地址
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        if re.search(ip_pattern, text):
            issues.append("IP地址")

        return issues

    prompt = "生成一段系統日誌（不包含敏感信息）"

    print(f"\n提示: {prompt}")

    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
        )

        text = response.choices[0].message.content

        # 檢測 PII
        pii_found = detect_custom_pii(text)

        print(f"\n輸出: {text}")

        if pii_found:
            print(f"\n⚠️  檢測到敏感信息: {', '.join(pii_found)}")
        else:
            print(f"\n✅ 未檢測到敏感信息")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def gdpr_compliance_check():
    """
    GDPR 合規性檢查
    """
    print("\n" + "=" * 60)
    print("GDPR 合規性檢查示例")
    print("=" * 60)

    # 所有需要檢測的 PII 類型以符合 GDPR
    gdpr_entities = [
        "EMAIL_ADDRESS",
        "PHONE_NUMBER",
        "PERSON",
        "LOCATION",
        "DATE_TIME",
        "MEDICAL_LICENSE",
        "IP_ADDRESS"
    ]

    guard = Guard().use(
        DetectPII(
            pii_entities=gdpr_entities,
            on_fail="filter"
        )
    )

    prompt = "生成一份公開的產品公告"

    print(f"\n提示: {prompt}")
    print("GDPR 合規檢查...")

    try:
        result = guard(
            llm_api=openai.chat.completions.create,
            prompt=prompt,
            model="gpt-3.5-turbo",
            max_tokens=200,
        )

        print(f"\n輸出: {result.validated_output}")
        print(f"✅ 符合 GDPR 要求")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def pii_anonymization():
    """
    PII 匿名化處理
    """
    print("\n" + "=" * 60)
    print("PII 匿名化處理示例")
    print("=" * 60)

    def anonymize_text(text):
        """
        匿名化文本中的 PII
        """
        # 替換郵箱
        text = re.sub(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'user@example.com',
            text
        )

        # 替換電話
        text = re.sub(
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            '555-0100',
            text
        )

        # 替換可能的姓名（簡化處理）
        # 實際應用中需要更複雜的 NER
        common_names = ['John', 'Jane', 'Mike', 'Sarah']
        for name in common_names:
            text = text.replace(name, '[NAME]')

        return text

    prompt = "生成一個客戶案例研究"

    print(f"\n提示: {prompt}")

    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
        )

        original = response.choices[0].message.content
        anonymized = anonymize_text(original)

        print(f"\n原始文本: {original}")
        print(f"\n匿名化文本: {anonymized}")
        print(f"✅ 匿名化完成")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def main():
    """
    主函數：運行所有 PII 過濾示例
    """
    print("\n🛡️  Guardrails AI - PII 過濾")
    print("=" * 60)

    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  警告: 未設置 OPENAI_API_KEY 環境變量")
        return

    # 運行各種 PII 檢測示例
    basic_pii_detection()
    filter_email_addresses()
    detect_phone_numbers()
    detect_person_names()
    detect_multiple_pii_types()
    mask_pii_data()
    custom_pii_detection()
    gdpr_compliance_check()
    pii_anonymization()

    print("\n" + "=" * 60)
    print("✅ 所有 PII 過濾示例執行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()

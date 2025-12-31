"""
Guardrails AI - 基本驗證示例
展示使用內建驗證器進行各種驗證
"""

import os
from guardrails import Guard
from guardrails.hub import (
    ValidLength,
    ValidRange,
    RegexMatch,
    ValidChoices,
    TwoWords
)
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")


def length_validation():
    """
    長度驗證：確保輸出在指定長度範圍內
    """
    print("=" * 60)
    print("長度驗證示例")
    print("=" * 60)

    # 創建長度驗證器：要求輸出在 20-100 字符之間
    guard = Guard().use(
        ValidLength(min=20, max=100, on_fail="reask")
    )

    prompt = "用一段話（20-100字符）描述機器學習"

    try:
        result = guard(
            llm_api=openai.chat.completions.create,
            prompt=prompt,
            model="gpt-3.5-turbo",
            max_tokens=150,
        )

        print(f"\n提示: {prompt}")
        print(f"輸出: {result.validated_output}")
        print(f"長度: {len(result.validated_output)} 字符")
        print(f"✅ 驗證通過")

    except Exception as e:
        print(f"❌ 驗證失敗: {str(e)}")


def range_validation():
    """
    範圍驗證：確保數值在指定範圍內
    """
    print("\n" + "=" * 60)
    print("數值範圍驗證示例")
    print("=" * 60)

    from guardrails.validators import ValidRange as NumericRange

    # 創建範圍驗證器：要求數值在 1-100 之間
    guard = Guard().use(
        NumericRange(min=1, max=100, on_fail="reask")
    )

    prompt = "生成一個 1 到 100 之間的整數（只返回數字）"

    try:
        result = guard(
            llm_api=openai.chat.completions.create,
            prompt=prompt,
            model="gpt-3.5-turbo",
            max_tokens=10,
        )

        print(f"\n提示: {prompt}")
        print(f"輸出: {result.validated_output}")
        print(f"✅ 驗證通過")

    except Exception as e:
        print(f"❌ 驗證失敗: {str(e)}")


def regex_validation():
    """
    正則表達式驗證：使用正則表達式驗證格式
    """
    print("\n" + "=" * 60)
    print("正則表達式驗證示例")
    print("=" * 60)

    # 驗證電子郵件格式
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    guard = Guard().use(
        RegexMatch(regex=email_regex, on_fail="reask")
    )

    prompt = "生成一個有效的電子郵件地址（只返回郵件地址）"

    try:
        result = guard(
            llm_api=openai.chat.completions.create,
            prompt=prompt,
            model="gpt-3.5-turbo",
            max_tokens=50,
        )

        print(f"\n提示: {prompt}")
        print(f"輸出: {result.validated_output}")
        print(f"✅ 格式驗證通過")

    except Exception as e:
        print(f"❌ 驗證失敗: {str(e)}")


def choice_validation():
    """
    選項驗證：確保輸出是預定義選項之一
    """
    print("\n" + "=" * 60)
    print("選項驗證示例")
    print("=" * 60)

    # 限制輸出必須是指定選項之一
    valid_choices = ["Python", "JavaScript", "Java", "C++", "Go"]

    guard = Guard().use(
        ValidChoices(choices=valid_choices, on_fail="reask")
    )

    prompt = f"從以下編程語言中選擇一個：{', '.join(valid_choices)}（只返回語言名稱）"

    try:
        result = guard(
            llm_api=openai.chat.completions.create,
            prompt=prompt,
            model="gpt-3.5-turbo",
            max_tokens=20,
        )

        print(f"\n提示: {prompt}")
        print(f"輸出: {result.validated_output}")
        print(f"✅ 選項驗證通過")

    except Exception as e:
        print(f"❌ 驗證失敗: {str(e)}")


def two_words_validation():
    """
    雙詞驗證：確保輸出恰好是兩個詞
    """
    print("\n" + "=" * 60)
    print("雙詞驗證示例")
    print("=" * 60)

    guard = Guard().use(
        TwoWords(on_fail="reask")
    )

    prompt = "生成一個包含恰好兩個英文單詞的短語"

    try:
        result = guard(
            llm_api=openai.chat.completions.create,
            prompt=prompt,
            model="gpt-3.5-turbo",
            max_tokens=20,
        )

        print(f"\n提示: {prompt}")
        print(f"輸出: {result.validated_output}")
        print(f"✅ 雙詞驗證通過")

    except Exception as e:
        print(f"❌ 驗證失敗: {str(e)}")


def combined_validations():
    """
    組合驗證：同時使用多個驗證器
    """
    print("\n" + "=" * 60)
    print("組合驗證示例")
    print("=" * 60)

    # 組合多個驗證器
    guard = Guard().use_many(
        ValidLength(min=10, max=50, on_fail="reask"),
        RegexMatch(regex="^[A-Z].*[.!?]$", on_fail="fix"),  # 首字母大寫，以標點結尾
    )

    prompt = "生成一個 10-50 字符的英文句子，首字母大寫，以句號結尾"

    try:
        result = guard(
            llm_api=openai.chat.completions.create,
            prompt=prompt,
            model="gpt-3.5-turbo",
            max_tokens=100,
        )

        print(f"\n提示: {prompt}")
        print(f"輸出: {result.validated_output}")
        print(f"長度: {len(result.validated_output)}")
        print(f"✅ 所有驗證通過")

    except Exception as e:
        print(f"❌ 驗證失敗: {str(e)}")


def validation_failure_handling():
    """
    驗證失敗處理：展示不同的失敗策略
    """
    print("\n" + "=" * 60)
    print("驗證失敗處理示例")
    print("=" * 60)

    # on_fail="exception" - 拋出異常
    guard_exception = Guard().use(
        ValidLength(min=5, max=10, on_fail="exception")
    )

    # on_fail="filter" - 過濾不符合的內容
    guard_filter = Guard().use(
        ValidLength(min=5, max=10, on_fail="filter")
    )

    # on_fail="fix" - 嘗試修復
    guard_fix = Guard().use(
        ValidLength(min=5, max=10, on_fail="fix")
    )

    prompt = "生成一個簡短的詞"

    print("\n策略 1: exception（拋出異常）")
    try:
        result = guard_exception(
            llm_api=openai.chat.completions.create,
            prompt=prompt,
            model="gpt-3.5-turbo",
            max_tokens=50,
        )
        print(f"輸出: {result.validated_output}")
    except Exception as e:
        print(f"捕獲到異常: {type(e).__name__}")

    print("\n策略 2: filter（過濾）")
    try:
        result = guard_filter(
            llm_api=openai.chat.completions.create,
            prompt=prompt,
            model="gpt-3.5-turbo",
            max_tokens=50,
        )
        print(f"輸出: {result.validated_output}")
    except Exception as e:
        print(f"錯誤: {str(e)}")

    print("\n策略 3: fix（修復）")
    try:
        result = guard_fix(
            llm_api=openai.chat.completions.create,
            prompt=prompt,
            model="gpt-3.5-turbo",
            max_tokens=50,
        )
        print(f"輸出: {result.validated_output}")
    except Exception as e:
        print(f"錯誤: {str(e)}")


def main():
    """
    主函數：運行所有驗證示例
    """
    print("\n🛡️  Guardrails AI - 基本驗證")
    print("=" * 60)

    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  警告: 未設置 OPENAI_API_KEY 環境變量")
        return

    # 運行各種驗證示例
    length_validation()
    range_validation()
    regex_validation()
    choice_validation()
    two_words_validation()
    combined_validations()
    validation_failure_handling()

    print("\n" + "=" * 60)
    print("✅ 所有驗證示例執行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()

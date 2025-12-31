"""
Guardrails AI - 自定義驗證器示例
展示如何創建和使用自定義驗證規則
"""

import os
import re
from typing import Any, Dict, Optional
from guardrails import Guard
from guardrails.validator_base import (
    Validator,
    register_validator,
    ValidationResult
)
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")


@register_validator(name="contains_keyword", data_type="string")
class ContainsKeyword(Validator):
    """
    自定義驗證器：確保文本包含指定關鍵詞
    """

    def __init__(self, keyword: str, case_sensitive: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.keyword = keyword
        self.case_sensitive = case_sensitive

    def validate(self, value: Any, metadata: Dict = None) -> ValidationResult:
        """
        驗證文本是否包含關鍵詞
        """
        if not isinstance(value, str):
            return ValidationResult(
                outcome="fail",
                error_message="Value must be a string"
            )

        text = value if self.case_sensitive else value.lower()
        keyword = self.keyword if self.case_sensitive else self.keyword.lower()

        if keyword in text:
            return ValidationResult(outcome="pass")
        else:
            return ValidationResult(
                outcome="fail",
                error_message=f"Text must contain the keyword '{self.keyword}'"
            )


@register_validator(name="no_profanity", data_type="string")
class NoProfanity(Validator):
    """
    自定義驗證器：檢查是否包含不當詞彙
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 簡化的不當詞彙列表（實際應用中應使用更完整的列表）
        self.profanity_list = ["bad_word1", "bad_word2", "offensive"]

    def validate(self, value: Any, metadata: Dict = None) -> ValidationResult:
        """
        驗證文本是否包含不當詞彙
        """
        if not isinstance(value, str):
            return ValidationResult(outcome="fail")

        text_lower = value.lower()

        for word in self.profanity_list:
            if word in text_lower:
                return ValidationResult(
                    outcome="fail",
                    error_message=f"Text contains inappropriate content: {word}"
                )

        return ValidationResult(outcome="pass")


@register_validator(name="word_count_range", data_type="string")
class WordCountRange(Validator):
    """
    自定義驗證器：驗證詞數在指定範圍內
    """

    def __init__(self, min_words: int = 0, max_words: int = 1000, **kwargs):
        super().__init__(**kwargs)
        self.min_words = min_words
        self.max_words = max_words

    def validate(self, value: Any, metadata: Dict = None) -> ValidationResult:
        """
        驗證詞數是否在範圍內
        """
        if not isinstance(value, str):
            return ValidationResult(outcome="fail")

        words = value.split()
        word_count = len(words)

        if self.min_words <= word_count <= self.max_words:
            return ValidationResult(outcome="pass")
        else:
            return ValidationResult(
                outcome="fail",
                error_message=f"Word count {word_count} is not in range [{self.min_words}, {self.max_words}]"
            )


@register_validator(name="valid_url", data_type="string")
class ValidURL(Validator):
    """
    自定義驗證器：驗證是否為有效的 URL
    """

    def __init__(self, require_https: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.require_https = require_https

    def validate(self, value: Any, metadata: Dict = None) -> ValidationResult:
        """
        驗證 URL 格式
        """
        if not isinstance(value, str):
            return ValidationResult(outcome="fail")

        # 簡化的 URL 正則表達式
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'

        if not re.match(url_pattern, value):
            return ValidationResult(
                outcome="fail",
                error_message="Invalid URL format"
            )

        if self.require_https and not value.startswith("https://"):
            return ValidationResult(
                outcome="fail",
                error_message="URL must use HTTPS"
            )

        return ValidationResult(outcome="pass")


@register_validator(name="sentiment_check", data_type="string")
class SentimentCheck(Validator):
    """
    自定義驗證器：簡單的情感檢查
    """

    def __init__(self, required_sentiment: str = "positive", **kwargs):
        super().__init__(**kwargs)
        self.required_sentiment = required_sentiment
        self.positive_words = ["good", "great", "excellent", "wonderful", "amazing"]
        self.negative_words = ["bad", "terrible", "awful", "horrible", "poor"]

    def validate(self, value: Any, metadata: Dict = None) -> ValidationResult:
        """
        驗證文本情感
        """
        if not isinstance(value, str):
            return ValidationResult(outcome="fail")

        text_lower = value.lower()

        positive_count = sum(1 for word in self.positive_words if word in text_lower)
        negative_count = sum(1 for word in self.negative_words if word in text_lower)

        if self.required_sentiment == "positive":
            if positive_count > negative_count:
                return ValidationResult(outcome="pass")
            else:
                return ValidationResult(
                    outcome="fail",
                    error_message="Text does not have positive sentiment"
                )
        elif self.required_sentiment == "negative":
            if negative_count > positive_count:
                return ValidationResult(outcome="pass")
            else:
                return ValidationResult(
                    outcome="fail",
                    error_message="Text does not have negative sentiment"
                )

        return ValidationResult(outcome="pass")


def test_keyword_validator():
    """
    測試關鍵詞驗證器
    """
    print("=" * 60)
    print("關鍵詞驗證器測試")
    print("=" * 60)

    guard = Guard().use(
        ContainsKeyword(keyword="Python", case_sensitive=False, on_fail="reask")
    )

    prompt = "寫一段關於編程語言的文字，必須提到 Python"

    try:
        result = guard(
            llm_api=openai.chat.completions.create,
            prompt=prompt,
            model="gpt-3.5-turbo",
            max_tokens=100,
        )

        print(f"\n提示: {prompt}")
        print(f"輸出: {result.validated_output}")
        print(f"✅ 關鍵詞驗證通過")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def test_profanity_validator():
    """
    測試不當詞彙驗證器
    """
    print("\n" + "=" * 60)
    print("不當詞彙驗證器測試")
    print("=" * 60)

    guard = Guard().use(
        NoProfanity(on_fail="exception")
    )

    prompt = "寫一段專業且禮貌的產品描述"

    try:
        result = guard(
            llm_api=openai.chat.completions.create,
            prompt=prompt,
            model="gpt-3.5-turbo",
            max_tokens=100,
        )

        print(f"\n提示: {prompt}")
        print(f"輸出: {result.validated_output}")
        print(f"✅ 內容安全驗證通過")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def test_word_count_validator():
    """
    測試詞數驗證器
    """
    print("\n" + "=" * 60)
    print("詞數驗證器測試")
    print("=" * 60)

    guard = Guard().use(
        WordCountRange(min_words=10, max_words=30, on_fail="reask")
    )

    prompt = "寫一段 10-30 個英文單詞的簡短介紹"

    try:
        result = guard(
            llm_api=openai.chat.completions.create,
            prompt=prompt,
            model="gpt-3.5-turbo",
            max_tokens=150,
        )

        word_count = len(result.validated_output.split())
        print(f"\n提示: {prompt}")
        print(f"輸出: {result.validated_output}")
        print(f"詞數: {word_count}")
        print(f"✅ 詞數驗證通過")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def test_url_validator():
    """
    測試 URL 驗證器
    """
    print("\n" + "=" * 60)
    print("URL 驗證器測試")
    print("=" * 60)

    guard = Guard().use(
        ValidURL(require_https=True, on_fail="reask")
    )

    prompt = "生成一個 HTTPS 網址（只返回網址）"

    try:
        result = guard(
            llm_api=openai.chat.completions.create,
            prompt=prompt,
            model="gpt-3.5-turbo",
            max_tokens=50,
        )

        print(f"\n提示: {prompt}")
        print(f"輸出: {result.validated_output}")
        print(f"✅ URL 驗證通過")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def test_sentiment_validator():
    """
    測試情感驗證器
    """
    print("\n" + "=" * 60)
    print("情感驗證器測試")
    print("=" * 60)

    guard = Guard().use(
        SentimentCheck(required_sentiment="positive", on_fail="reask")
    )

    prompt = "寫一段積極正面的產品評論"

    try:
        result = guard(
            llm_api=openai.chat.completions.create,
            prompt=prompt,
            model="gpt-3.5-turbo",
            max_tokens=100,
        )

        print(f"\n提示: {prompt}")
        print(f"輸出: {result.validated_output}")
        print(f"✅ 情感驗證通過")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def test_multiple_custom_validators():
    """
    測試組合多個自定義驗證器
    """
    print("\n" + "=" * 60)
    print("組合自定義驗證器測試")
    print("=" * 60)

    guard = Guard().use_many(
        WordCountRange(min_words=15, max_words=40, on_fail="reask"),
        ContainsKeyword(keyword="AI", case_sensitive=False, on_fail="reask"),
        NoProfanity(on_fail="exception"),
        SentimentCheck(required_sentiment="positive", on_fail="reask")
    )

    prompt = "寫一段 15-40 個詞的積極文字，描述 AI 技術的優勢"

    try:
        result = guard(
            llm_api=openai.chat.completions.create,
            prompt=prompt,
            model="gpt-3.5-turbo",
            max_tokens=200,
        )

        word_count = len(result.validated_output.split())
        print(f"\n提示: {prompt}")
        print(f"輸出: {result.validated_output}")
        print(f"詞數: {word_count}")
        print(f"✅ 所有自定義驗證器通過")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def main():
    """
    主函數：運行所有自定義驗證器示例
    """
    print("\n🛡️  Guardrails AI - 自定義驗證器")
    print("=" * 60)

    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  警告: 未設置 OPENAI_API_KEY 環境變量")
        return

    # 運行各種自定義驗證器示例
    test_keyword_validator()
    test_profanity_validator()
    test_word_count_validator()
    test_url_validator()
    test_sentiment_validator()
    test_multiple_custom_validators()

    print("\n" + "=" * 60)
    print("✅ 所有自定義驗證器示例執行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()

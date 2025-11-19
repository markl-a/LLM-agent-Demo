"""驗證器模組的單元測試"""

import pytest

try:
    from src.llm_agent_demo.utils.validators import (
        ValidationError,
        validate_api_key,
        validate_openai_api_key,
        validate_anthropic_api_key,
        validate_model_name,
        validate_temperature,
        validate_max_tokens,
        validate_top_k,
        validate_chunk_size,
        validate_file_path,
        validate_url,
        validate_email,
        validate_language_code,
    )

    VALIDATORS_AVAILABLE = True
except ImportError:
    VALIDATORS_AVAILABLE = False
    pytest.skip("驗證器模組未安裝", allow_module_level=True)


@pytest.mark.unit
class TestValidateApiKey:
    """測試 API 金鑰驗證"""

    def test_valid_api_key(self):
        """測試有效的 API 金鑰"""
        key = "sk-1234567890abcdef1234567890"
        result = validate_api_key(key)
        assert result == key

    def test_none_api_key(self):
        """測試 None 金鑰"""
        with pytest.raises(ValidationError, match="API 金鑰不能為空"):
            validate_api_key(None)

    def test_empty_api_key(self):
        """測試空字符串金鑰"""
        with pytest.raises(ValidationError, match="API 金鑰不能為空"):
            validate_api_key("")

    def test_whitespace_api_key(self):
        """測試只包含空白的金鑰"""
        with pytest.raises(ValidationError, match="不能只包含空白字符"):
            validate_api_key("   ")

    def test_short_api_key(self):
        """測試過短的金鑰"""
        with pytest.raises(ValidationError, match="長度過短"):
            validate_api_key("short")

    def test_api_key_with_spaces(self):
        """測試包含空格的金鑰"""
        with pytest.raises(ValidationError, match="包含無效字符"):
            validate_api_key("sk-1234567890abcdef 1234567890")


@pytest.mark.unit
class TestValidateOpenAIApiKey:
    """測試 OpenAI API 金鑰驗證"""

    def test_valid_openai_key(self):
        """測試有效的 OpenAI 金鑰"""
        key = "sk-1234567890abcdef1234567890abcdef"
        result = validate_openai_api_key(key)
        assert result == key

    def test_valid_openai_proj_key(self):
        """測試有效的 OpenAI 項目金鑰"""
        key = "sk-proj-1234567890abcdef1234567890abcdef"
        result = validate_openai_api_key(key)
        assert result == key

    def test_invalid_prefix(self):
        """測試無效的前綴"""
        with pytest.raises(ValidationError, match="必須以 'sk-' 或 'sk-proj-' 開頭"):
            validate_openai_api_key("invalid-1234567890abcdef1234567890")


@pytest.mark.unit
class TestValidateAnthropicApiKey:
    """測試 Anthropic API 金鑰驗證"""

    def test_valid_anthropic_key(self):
        """測試有效的 Anthropic 金鑰"""
        key = "sk-ant-1234567890abcdef1234567890"
        result = validate_anthropic_api_key(key)
        assert result == key

    def test_invalid_prefix(self):
        """測試無效的前綴"""
        with pytest.raises(ValidationError, match="必須以 'sk-ant-' 開頭"):
            validate_anthropic_api_key("sk-1234567890abcdef1234567890")


@pytest.mark.unit
class TestValidateModelName:
    """測試模型名稱驗證"""

    def test_valid_model_name(self):
        """測試有效的模型名稱"""
        model = "gpt-4o-mini"
        result = validate_model_name(model)
        assert result == model

    def test_empty_model_name(self):
        """測試空模型名稱"""
        with pytest.raises(ValidationError, match="模型名稱不能為空"):
            validate_model_name("")

    def test_model_in_valid_list(self):
        """測試有效列表中的模型"""
        valid_models = ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]
        result = validate_model_name("gpt-4o", valid_models)
        assert result == "gpt-4o"

    def test_model_not_in_valid_list(self):
        """測試不在有效列表中的模型"""
        valid_models = ["gpt-4o", "gpt-4o-mini"]
        with pytest.raises(ValidationError, match="無效的模型名稱"):
            validate_model_name("invalid-model", valid_models)


@pytest.mark.unit
class TestValidateTemperature:
    """測試溫度驗證"""

    @pytest.mark.parametrize("temp", [0.0, 0.5, 1.0, 1.5, 2.0])
    def test_valid_temperatures(self, temp):
        """測試有效的溫度值"""
        result = validate_temperature(temp)
        assert result == temp

    @pytest.mark.parametrize("temp", [-0.1, 2.1, 3.0])
    def test_invalid_temperatures(self, temp):
        """測試無效的溫度值"""
        with pytest.raises(ValidationError, match="必須在 0.0 到 2.0 之間"):
            validate_temperature(temp)

    def test_temperature_type_error(self):
        """測試錯誤的溫度類型"""
        with pytest.raises(ValidationError, match="溫度必須是數字"):
            validate_temperature("invalid")


@pytest.mark.unit
class TestValidateMaxTokens:
    """測試最大 Token 數驗證"""

    def test_valid_max_tokens(self):
        """測試有效的最大 Token 數"""
        result = validate_max_tokens(1000)
        assert result == 1000

    def test_zero_max_tokens(self):
        """測試零 Token"""
        with pytest.raises(ValidationError, match="必須大於 0"):
            validate_max_tokens(0)

    def test_negative_max_tokens(self):
        """測試負數 Token"""
        with pytest.raises(ValidationError, match="必須大於 0"):
            validate_max_tokens(-100)

    def test_too_large_max_tokens(self):
        """測試過大的 Token 數"""
        with pytest.raises(ValidationError, match="過大"):
            validate_max_tokens(300000)

    def test_max_tokens_type_error(self):
        """測試錯誤的類型"""
        with pytest.raises(ValidationError, match="必須是整數"):
            validate_max_tokens(100.5)


@pytest.mark.unit
class TestValidateTopK:
    """測試 Top-K 驗證"""

    def test_valid_top_k(self):
        """測試有效的 Top-K"""
        result = validate_top_k(5)
        assert result == 5

    def test_zero_top_k(self):
        """測試零值"""
        with pytest.raises(ValidationError, match="必須大於 0"):
            validate_top_k(0)

    def test_too_large_top_k(self):
        """測試過大的值"""
        with pytest.raises(ValidationError, match="過大"):
            validate_top_k(150)


@pytest.mark.unit
class TestValidateChunkSize:
    """測試分塊大小驗證"""

    def test_valid_chunk_size(self):
        """測試有效的分塊參數"""
        size, overlap = validate_chunk_size(1000, 200)
        assert size == 1000
        assert overlap == 200

    def test_zero_chunk_size(self):
        """測試零分塊大小"""
        with pytest.raises(ValidationError, match="分塊大小必須大於 0"):
            validate_chunk_size(0, 100)

    def test_negative_overlap(self):
        """測試負重疊"""
        with pytest.raises(ValidationError, match="不能為負數"):
            validate_chunk_size(1000, -10)

    def test_overlap_larger_than_size(self):
        """測試重疊大於分塊大小"""
        with pytest.raises(ValidationError, match="必須小於分塊大小"):
            validate_chunk_size(1000, 1000)


@pytest.mark.unit
class TestValidateUrl:
    """測試 URL 驗證"""

    @pytest.mark.parametrize(
        "url",
        [
            "https://example.com",
            "http://example.com",
            "https://www.example.com/path",
            "https://example.com:8080",
            "http://localhost:3000",
            "https://api.example.com/v1/endpoint",
        ],
    )
    def test_valid_urls(self, url):
        """測試有效的 URL"""
        result = validate_url(url)
        assert result == url

    @pytest.mark.parametrize(
        "url", ["not-a-url", "ftp://example.com", "example.com", "https://", ""]
    )
    def test_invalid_urls(self, url):
        """測試無效的 URL"""
        with pytest.raises(ValidationError):
            validate_url(url)


@pytest.mark.unit
class TestValidateEmail:
    """測試電子郵件驗證"""

    @pytest.mark.parametrize(
        "email",
        [
            "user@example.com",
            "test.user@example.com",
            "user+tag@example.co.uk",
            "test_user@example.org",
        ],
    )
    def test_valid_emails(self, email):
        """測試有效的電子郵件"""
        result = validate_email(email)
        assert result == email.lower()

    @pytest.mark.parametrize(
        "email", ["invalid", "user@", "@example.com", "user @example.com", ""]
    )
    def test_invalid_emails(self, email):
        """測試無效的電子郵件"""
        with pytest.raises(ValidationError):
            validate_email(email)


@pytest.mark.unit
class TestValidateLanguageCode:
    """測試語言代碼驗證"""

    @pytest.mark.parametrize(
        "code", ["en", "zh", "ja", "ko", "fr", "de", "es", "it", "pt", "ru"]
    )
    def test_valid_language_codes(self, code):
        """測試有效的語言代碼"""
        result = validate_language_code(code)
        assert result == code.lower()

    @pytest.mark.parametrize("code", ["invalid", "zz", "eng", ""])
    def test_invalid_language_codes(self, code):
        """測試無效的語言代碼"""
        with pytest.raises(ValidationError):
            validate_language_code(code)

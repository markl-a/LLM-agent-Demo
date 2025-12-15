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
        # 安全性相關驗證函數
        sanitize_user_input,
        validate_user_query,
        validate_url_safe,
        escape_for_html,
        mask_sensitive_data,
    )
    from src.llm_agent_demo.utils.exceptions import APIKeyError

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
        with pytest.raises(APIKeyError, match="金鑰不能為空"):
            validate_api_key(None)

    def test_empty_api_key(self):
        """測試空字符串金鑰"""
        with pytest.raises(APIKeyError, match="金鑰不能為空"):
            validate_api_key("")

    def test_whitespace_api_key(self):
        """測試只包含空白的金鑰"""
        with pytest.raises(APIKeyError, match="只包含空白字符"):
            validate_api_key("   ")

    def test_short_api_key(self):
        """測試過短的金鑰"""
        with pytest.raises(APIKeyError, match="長度過短"):
            validate_api_key("short")

    def test_api_key_with_spaces(self):
        """測試包含空格的金鑰"""
        with pytest.raises(APIKeyError, match="無效字符"):
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
        with pytest.raises(APIKeyError, match="必須以 'sk-' 或 'sk-proj-' 開頭"):
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
        with pytest.raises(APIKeyError, match="必須以 'sk-ant-' 開頭"):
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


# ============================================================================
# 安全性相關驗證函數測試
# ============================================================================


@pytest.mark.unit
class TestSanitizeUserInput:
    """測試用戶輸入清理函數"""

    def test_normal_input(self):
        """測試正常輸入"""
        text = "這是一個正常的輸入"
        result = sanitize_user_input(text)
        assert result == text

    def test_none_input(self):
        """測試 None 輸入"""
        result = sanitize_user_input(None)
        assert result == ""

    def test_non_string_input(self):
        """測試非字符串輸入"""
        with pytest.raises(ValidationError, match="輸入必須是字符串"):
            sanitize_user_input(123)

    @pytest.mark.parametrize(
        "text,expected",
        [
            # HTML 標籤應該被轉義
            ("<script>alert('xss')</script>", "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;"),
            # 特殊字符應該被轉義
            ("<div>test</div>", "&lt;div&gt;test&lt;/div&gt;"),
            # & 符號應該被轉義
            ("AT&T", "AT&amp;T"),
            # 引號應該被轉義
            ('He said "Hello"', "He said &quot;Hello&quot;"),
        ],
    )
    def test_html_escape(self, text, expected):
        """測試 HTML 轉義功能"""
        result = sanitize_user_input(text, strip_html=True)
        assert result == expected

    def test_length_limit(self):
        """測試長度限制"""
        long_text = "a" * 10001
        with pytest.raises(ValidationError, match="輸入過長"):
            sanitize_user_input(long_text, max_length=10000)

    def test_custom_length_limit(self):
        """測試自定義長度限制"""
        text = "a" * 100
        result = sanitize_user_input(text, max_length=500)
        assert len(result) <= 100

        with pytest.raises(ValidationError, match="輸入過長"):
            sanitize_user_input(text, max_length=50)

    def test_newlines_allowed(self):
        """測試允許換行符"""
        text = "第一行\n第二行\r\n第三行"
        result = sanitize_user_input(text, allow_newlines=True, strip_html=False)
        # 應該保留換行符但移除多餘空格
        assert "第一行" in result
        assert "第二行" in result
        assert "第三行" in result

    def test_newlines_not_allowed(self):
        """測試不允許換行符"""
        text = "第一行\n第二行\r\n第三行"
        result = sanitize_user_input(text, allow_newlines=False, strip_html=False)
        # 換行符應該被移除
        assert "\n" not in result
        assert "\r" not in result

    def test_control_characters_removed(self):
        """測試控制字符被移除"""
        # ASCII 控制字符 (0-31, 除了 \t, \n, \r)
        text = "test\x00\x01\x02control\x1fchars"
        result = sanitize_user_input(text, strip_html=False)
        # 控制字符應該被移除
        assert "\x00" not in result
        assert "\x01" not in result
        assert "testcontrolchars" in result

    def test_whitespace_normalization(self):
        """測試空白字符正規化"""
        text = "多個    空格    測試"
        result = sanitize_user_input(text, strip_html=False)
        # 多餘的空格應該被合併為單個空格
        assert "多個 空格 測試" == result

    def test_strip_html_false(self):
        """測試不轉義 HTML"""
        text = "<div>test</div>"
        result = sanitize_user_input(text, strip_html=False)
        # 當 strip_html=False 時，HTML 不應該被轉義（但多餘空格會被移除）
        assert "<div>test</div>" == result


@pytest.mark.unit
class TestValidateUserQuery:
    """測試用戶查詢驗證函數"""

    def test_valid_query(self):
        """測試有效的查詢"""
        query = "這是一個正常的查詢"
        result = validate_user_query(query)
        assert result == query

    def test_empty_query(self):
        """測試空查詢"""
        with pytest.raises(ValidationError, match="查詢不能為空"):
            validate_user_query("")

    def test_whitespace_query(self):
        """測試只包含空白的查詢"""
        with pytest.raises(ValidationError, match="查詢過短"):
            validate_user_query("   ")

    def test_query_too_short(self):
        """測試查詢過短"""
        with pytest.raises(ValidationError, match="查詢過短"):
            validate_user_query("a", min_length=5)

    def test_query_too_long(self):
        """測試查詢過長"""
        long_query = "a" * 2001
        with pytest.raises(ValidationError, match="查詢過長"):
            validate_user_query(long_query, max_length=2000)

    def test_custom_length_limits(self):
        """測試自定義長度限制"""
        query = "測試查詢"
        result = validate_user_query(query, min_length=3, max_length=100)
        assert result == query

    @pytest.mark.parametrize(
        "query,pattern_desc",
        [
            # XSS 攻擊模式
            ("<script>alert('xss')</script>", "script 標籤"),
            ("<SCRIPT>alert('XSS')</SCRIPT>", "script 標籤"),
            ("javascript:alert('xss')", "javascript: 協議"),
            ("JAVASCRIPT:alert('XSS')", "javascript: 協議"),
            ("<img onload=alert('xss')>", "事件處理器"),
            ("<div onclick=malicious()>", "事件處理器"),
            # SQL 注入模式
            ("SELECT * FROM users --", "SQL 註釋"),
            ("1' OR '1'='1' --", "SQL 註釋"),
            ("'; DROP TABLE users;", "SQL DROP 語句"),
            ("1; DELETE FROM users;", "SQL DELETE 語句"),
            ("1 UNION SELECT * FROM passwords", "SQL UNION 語句"),
            ("admin' UNION SELECT null--", "SQL UNION 語句"),
        ],
    )
    def test_suspicious_patterns(self, query, pattern_desc):
        """測試檢測可疑模式"""
        with pytest.raises(ValidationError, match="查詢包含可疑內容"):
            validate_user_query(query, check_suspicious=True)

    def test_suspicious_check_disabled(self):
        """測試禁用可疑檢查"""
        # 當 check_suspicious=False 時，可疑內容應該被允許
        query = "<script>test</script>"
        result = validate_user_query(query, check_suspicious=False)
        assert result == query

    @pytest.mark.parametrize(
        "query",
        [
            "如何使用 Python 腳本？",  # 包含「腳本」但不是攻擊
            "JavaScript 教程",  # 包含 JavaScript 但不是攻擊
            "如何刪除文件？",  # 包含「刪除」但不是 SQL
            "數據庫聯合查詢",  # 包含「聯合」但不是攻擊
        ],
    )
    def test_false_positives_allowed(self, query):
        """測試正常內容不被誤判（假陽性測試）"""
        # 這些查詢包含關鍵字但不是攻擊模式
        result = validate_user_query(query, check_suspicious=True)
        assert result == query


@pytest.mark.unit
class TestValidateUrlSafe:
    """測試安全 URL 驗證函數"""

    @pytest.mark.parametrize(
        "url",
        [
            "https://example.com",
            "http://example.com",
            "https://api.example.com/v1/users",
            "https://example.com:8080/path",
            "http://localhost:3000",
            "https://example.com/api?key=value",
        ],
    )
    def test_valid_urls(self, url):
        """測試有效的 URL"""
        result = validate_url_safe(url)
        assert result == url

    def test_empty_url(self):
        """測試空 URL"""
        with pytest.raises(ValidationError, match="URL 不能為空"):
            validate_url_safe("")

    def test_missing_scheme(self):
        """測試缺少協議"""
        with pytest.raises(ValidationError, match="URL 必須包含協議"):
            validate_url_safe("example.com/path")

    def test_invalid_scheme(self):
        """測試無效的協議"""
        with pytest.raises(ValidationError, match="不支援的 URL 協議"):
            validate_url_safe("ftp://example.com")

    def test_custom_allowed_schemes(self):
        """測試自定義允許的協議"""
        # 默認不允許 ftp
        with pytest.raises(ValidationError, match="不支援的 URL 協議"):
            validate_url_safe("ftp://example.com")

        # 自定義允許 ftp
        result = validate_url_safe("ftp://example.com", allowed_schemes=["ftp"])
        assert result == "ftp://example.com"

    def test_missing_host(self):
        """測試缺少主機名"""
        with pytest.raises(ValidationError, match="URL 必須包含主機名"):
            validate_url_safe("https://")

    @pytest.mark.parametrize(
        "url",
        [
            "https://example.com/../etc/passwd",
            "https://example.com/path/../../../secret",
            "http://localhost:8000/api/../../../admin",
        ],
    )
    def test_path_traversal_detection(self, url):
        """測試路徑遍歷檢測"""
        with pytest.raises(ValidationError, match="URL 路徑包含可疑的目錄遍歷模式"):
            validate_url_safe(url)

    @pytest.mark.parametrize(
        "url",
        [
            'https://example.com/api?param=<script>',
            'https://example.com?name="><script>alert(1)</script>',
            "https://example.com?data='malicious'",
        ],
    )
    def test_suspicious_query_params(self, url):
        """測試可疑的查詢參數 - 實現只記錄警告不拋出異常"""
        # 根據實際實現，這些 URL 會觸發警告但不會拋出異常
        # 因為實現中只對鍵名拋出異常，對參數值只記錄警告
        result = validate_url_safe(url)
        assert result == url  # 應該返回原 URL（只警告不阻止）

    def test_valid_query_params(self):
        """測試有效的查詢參數"""
        url = "https://api.example.com/search?q=python&limit=10&offset=0"
        result = validate_url_safe(url)
        assert result == url


@pytest.mark.unit
class TestEscapeForHtml:
    """測試 HTML 轉義函數"""

    def test_normal_text(self):
        """測試正常文本"""
        text = "這是正常的文本"
        result = escape_for_html(text)
        assert result == text

    def test_none_input(self):
        """測試 None 輸入"""
        result = escape_for_html(None)
        assert result == ""

    @pytest.mark.parametrize(
        "text,expected",
        [
            # 基本 HTML 字符
            ("<", "&lt;"),
            (">", "&gt;"),
            ("&", "&amp;"),
            ('"', "&quot;"),
            ("'", "&#x27;"),
            # 組合測試
            ("<script>", "&lt;script&gt;"),
            ("AT&T", "AT&amp;T"),
            ("<div class=\"test\">", "&lt;div class=&quot;test&quot;&gt;"),
            ("1 < 2 & 3 > 2", "1 &lt; 2 &amp; 3 &gt; 2"),
        ],
    )
    def test_html_special_characters(self, text, expected):
        """測試 HTML 特殊字符轉義"""
        result = escape_for_html(text)
        assert result == expected

    def test_xss_prevention(self):
        """測試防止 XSS 攻擊"""
        # 測試包含 < 和 > 的危險輸入
        dangerous_with_tags = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<iframe src=\"javascript:alert('XSS')\">",
        ]

        for dangerous in dangerous_with_tags:
            result = escape_for_html(dangerous)
            # 確保沒有原始的 < 或 > 標籤
            assert "<" not in result
            assert ">" not in result
            # 確保被轉義
            assert "&lt;" in result or "&gt;" in result

        # 測試不包含 < > 的危險輸入（如引號注入）
        quote_injection = "';alert('XSS');//"
        result = escape_for_html(quote_injection)
        # 確保引號被轉義
        assert "'" not in result or "&#x27;" in result

    def test_numeric_input(self):
        """測試數字輸入"""
        result = escape_for_html(12345)
        assert result == "12345"

    def test_unicode_text(self):
        """測試 Unicode 文本"""
        text = "你好世界 🌍 こんにちは"
        result = escape_for_html(text)
        # Unicode 字符應該保持不變
        assert result == text


@pytest.mark.unit
class TestMaskSensitiveData:
    """測試敏感數據遮蔽函數"""

    def test_normal_masking(self):
        """測試正常遮蔽"""
        data = "sk-1234567890abcdef"
        result = mask_sensitive_data(data)
        assert result == "sk-1***************"
        assert result.startswith("sk-1")
        assert "*" in result

    def test_custom_visible_chars(self):
        """測試自定義可見字符數"""
        data = "sk-1234567890abcdef"
        # 顯示前 6 個字符
        result = mask_sensitive_data(data, visible_chars=6)
        assert result == "sk-123*************"
        assert result.startswith("sk-123")

        # 顯示前 10 個字符
        result = mask_sensitive_data(data, visible_chars=10)
        assert result == "sk-1234567*********"

    def test_empty_string(self):
        """測試空字符串"""
        result = mask_sensitive_data("")
        assert result == ""

    def test_short_string(self):
        """測試短字符串（短於可見字符數）"""
        data = "abc"
        result = mask_sensitive_data(data, visible_chars=4)
        # 當字符串短於可見字符數時，全部遮蔽
        assert result == "***"
        assert len(result) == len(data)

    def test_exactly_visible_length(self):
        """測試恰好等於可見長度的字符串"""
        data = "test"
        result = mask_sensitive_data(data, visible_chars=4)
        # 當長度恰好等於可見字符數時，全部遮蔽
        assert result == "****"

    @pytest.mark.parametrize(
        "data,visible,expected_prefix",
        [
            ("sk-ant-1234567890", 4, "sk-a"),
            ("sk-proj-abcdefghij", 8, "sk-proj-"),
            ("password123456", 3, "pas"),
            ("token_abc_def_ghi", 10, "token_abc_"),
        ],
    )
    def test_various_data_types(self, data, visible, expected_prefix):
        """測試各種數據類型的遮蔽"""
        result = mask_sensitive_data(data, visible_chars=visible)
        assert result.startswith(expected_prefix)
        assert "*" in result
        assert len(result) == len(data)

    def test_preserves_length(self):
        """測試遮蔽後長度保持不變"""
        test_cases = [
            "short",
            "medium_length_string",
            "very_long_string_with_many_characters_1234567890",
        ]

        for data in test_cases:
            result = mask_sensitive_data(data)
            assert len(result) == len(data)

    def test_api_key_masking(self):
        """測試 API 金鑰遮蔽"""
        # OpenAI API 金鑰 (35 個字符)
        openai_key = "sk-1234567890abcdef1234567890abcdef"
        result = mask_sensitive_data(openai_key)
        assert result.startswith("sk-1")
        assert len(result) == len(openai_key)
        assert result.count("*") == len(openai_key) - 4
        assert result == "sk-1*******************************"

        # Anthropic API 金鑰 (23 個字符)
        anthropic_key = "sk-ant-1234567890abcdef"
        result = mask_sensitive_data(anthropic_key, visible_chars=7)
        assert result.startswith("sk-ant-")
        assert "*" in result
        assert len(result) == len(anthropic_key)

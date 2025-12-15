"""驗證器模組 - 提供各種輸入驗證功能"""

import re
import html
import logging
from typing import Optional, List
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """驗證錯誤異常"""

    pass


def validate_api_key(api_key: Optional[str], provider: str = "API") -> str:
    """
    驗證 API 金鑰

    Args:
        api_key: API 金鑰
        provider: 提供商名稱（用於錯誤訊息）

    Returns:
        驗證後的 API 金鑰

    Raises:
        ValidationError: 如果 API 金鑰無效
    """
    if not api_key:
        raise ValidationError(f"{provider} API 金鑰不能為空")

    api_key = api_key.strip()

    if not api_key:
        raise ValidationError(f"{provider} API 金鑰不能只包含空白字符")

    # 檢查最小長度（大多數 API 金鑰至少 20 個字符）
    if len(api_key) < 20:
        raise ValidationError(f"{provider} API 金鑰長度過短（至少需要 20 個字符）")

    # 檢查是否包含可疑字符
    if any(char in api_key for char in [" ", "\t", "\n", "\r"]):
        raise ValidationError(f"{provider} API 金鑰包含無效字符（空格或換行符）")

    return api_key


def validate_openai_api_key(api_key: Optional[str]) -> str:
    """
    驗證 OpenAI API 金鑰

    OpenAI API 金鑰格式: sk-... 或 sk-proj-...

    Args:
        api_key: OpenAI API 金鑰

    Returns:
        驗證後的 API 金鑰

    Raises:
        ValidationError: 如果 API 金鑰無效
    """
    api_key = validate_api_key(api_key, "OpenAI")

    # 檢查前綴
    if not (api_key.startswith("sk-") or api_key.startswith("sk-proj-")):
        raise ValidationError("OpenAI API 金鑰必須以 'sk-' 或 'sk-proj-' 開頭")

    return api_key


def validate_anthropic_api_key(api_key: Optional[str]) -> str:
    """
    驗證 Anthropic API 金鑰

    Anthropic API 金鑰格式: sk-ant-...

    Args:
        api_key: Anthropic API 金鑰

    Returns:
        驗證後的 API 金鑰

    Raises:
        ValidationError: 如果 API 金鑰無效
    """
    api_key = validate_api_key(api_key, "Anthropic")

    # 檢查前綴
    if not api_key.startswith("sk-ant-"):
        raise ValidationError("Anthropic API 金鑰必須以 'sk-ant-' 開頭")

    return api_key


def validate_model_name(model: str, valid_models: Optional[List[str]] = None) -> str:
    """
    驗證模型名稱

    Args:
        model: 模型名稱
        valid_models: 有效模型列表（可選）

    Returns:
        驗證後的模型名稱

    Raises:
        ValidationError: 如果模型名稱無效
    """
    if not model:
        raise ValidationError("模型名稱不能為空")

    model = model.strip()

    if not model:
        raise ValidationError("模型名稱不能只包含空白字符")

    # 如果提供了有效模型列表，檢查是否在列表中
    if valid_models and model not in valid_models:
        raise ValidationError(
            f"無效的模型名稱: {model}. 有效的模型: {', '.join(valid_models)}"
        )

    return model


def validate_temperature(temperature: float) -> float:
    """
    驗證溫度參數

    Args:
        temperature: 溫度值（0.0 到 2.0）

    Returns:
        驗證後的溫度值

    Raises:
        ValidationError: 如果溫度值無效
    """
    if not isinstance(temperature, (int, float)):
        raise ValidationError("溫度必須是數字")

    if not 0.0 <= temperature <= 2.0:
        raise ValidationError("溫度必須在 0.0 到 2.0 之間")

    return float(temperature)


def validate_max_tokens(max_tokens: int) -> int:
    """
    驗證最大 token 數

    Args:
        max_tokens: 最大 token 數

    Returns:
        驗證後的最大 token 數

    Raises:
        ValidationError: 如果最大 token 數無效
    """
    if not isinstance(max_tokens, int):
        raise ValidationError("最大 token 數必須是整數")

    if max_tokens <= 0:
        raise ValidationError("最大 token 數必須大於 0")

    if max_tokens > 200000:  # 設定一個合理的上限
        raise ValidationError("最大 token 數過大（超過 200,000）")

    return max_tokens


def validate_top_k(top_k: int) -> int:
    """
    驗證 Top-K 參數（用於檢索）

    Args:
        top_k: Top-K 值

    Returns:
        驗證後的 Top-K 值

    Raises:
        ValidationError: 如果 Top-K 值無效
    """
    if not isinstance(top_k, int):
        raise ValidationError("Top-K 必須是整數")

    if top_k <= 0:
        raise ValidationError("Top-K 必須大於 0")

    if top_k > 100:
        raise ValidationError("Top-K 過大（建議不超過 100）")

    return top_k


def validate_chunk_size(chunk_size: int, chunk_overlap: int) -> tuple[int, int]:
    """
    驗證分塊參數

    Args:
        chunk_size: 分塊大小
        chunk_overlap: 分塊重疊大小

    Returns:
        驗證後的 (chunk_size, chunk_overlap) 元組

    Raises:
        ValidationError: 如果分塊參數無效
    """
    if not isinstance(chunk_size, int):
        raise ValidationError("分塊大小必須是整數")

    if not isinstance(chunk_overlap, int):
        raise ValidationError("分塊重疊大小必須是整數")

    if chunk_size <= 0:
        raise ValidationError("分塊大小必須大於 0")

    if chunk_overlap < 0:
        raise ValidationError("分塊重疊大小不能為負數")

    if chunk_overlap >= chunk_size:
        raise ValidationError("分塊重疊大小必須小於分塊大小")

    return chunk_size, chunk_overlap


def validate_file_path(file_path: str, must_exist: bool = False) -> str:
    """
    驗證文件路徑

    Args:
        file_path: 文件路徑
        must_exist: 是否要求文件必須存在

    Returns:
        驗證後的文件路徑

    Raises:
        ValidationError: 如果文件路徑無效
    """
    import os

    if not file_path:
        raise ValidationError("文件路徑不能為空")

    file_path = file_path.strip()

    if not file_path:
        raise ValidationError("文件路徑不能只包含空白字符")

    if must_exist and not os.path.exists(file_path):
        raise ValidationError(f"文件不存在: {file_path}")

    return file_path


def validate_url(url: str) -> str:
    """
    驗證 URL

    Args:
        url: URL 字符串

    Returns:
        驗證後的 URL

    Raises:
        ValidationError: 如果 URL 無效
    """
    if not url:
        raise ValidationError("URL 不能為空")

    url = url.strip()

    if not url:
        raise ValidationError("URL 不能只包含空白字符")

    # 簡單的 URL 格式檢查
    url_pattern = re.compile(
        r"^https?://"  # http:// 或 https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # 域名
        r"localhost|"  # localhost
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # IP 地址
        r"(?::\d+)?"  # 可選端口
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )

    if not url_pattern.match(url):
        raise ValidationError(f"無效的 URL 格式: {url}")

    return url


def validate_email(email: str) -> str:
    """
    驗證電子郵件地址

    Args:
        email: 電子郵件地址

    Returns:
        驗證後的電子郵件地址

    Raises:
        ValidationError: 如果電子郵件地址無效
    """
    if not email:
        raise ValidationError("電子郵件地址不能為空")

    email = email.strip().lower()

    if not email:
        raise ValidationError("電子郵件地址不能只包含空白字符")

    # 簡單的電子郵件格式檢查
    email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    if not email_pattern.match(email):
        raise ValidationError(f"無效的電子郵件格式: {email}")

    return email


def validate_language_code(language_code: str) -> str:
    """
    驗證語言代碼（ISO 639-1）

    Args:
        language_code: 語言代碼（如 'en', 'zh', 'ja'）

    Returns:
        驗證後的語言代碼

    Raises:
        ValidationError: 如果語言代碼無效
    """
    if not language_code:
        raise ValidationError("語言代碼不能為空")

    language_code = language_code.strip().lower()

    if not language_code:
        raise ValidationError("語言代碼不能只包含空白字符")

    # 常見的 ISO 639-1 語言代碼
    valid_language_codes = {
        "en",
        "zh",
        "ja",
        "ko",
        "fr",
        "de",
        "es",
        "it",
        "pt",
        "ru",
        "ar",
        "hi",
        "th",
        "vi",
    }

    if language_code not in valid_language_codes:
        raise ValidationError(
            f"不支援的語言代碼: {language_code}. "
            f"支援的語言: {', '.join(sorted(valid_language_codes))}"
        )

    return language_code


# ============================================================================
# 安全性相關驗證函數
# ============================================================================


def sanitize_user_input(
    text: str,
    max_length: int = 10000,
    allow_newlines: bool = True,
    strip_html: bool = True,
) -> str:
    """
    清理和驗證用戶輸入，防止注入攻擊

    Args:
        text: 用戶輸入的文本
        max_length: 最大允許長度（默認 10000 字符）
        allow_newlines: 是否允許換行符（默認 True）
        strip_html: 是否移除 HTML 標籤（默認 True）

    Returns:
        清理後的安全文本

    Raises:
        ValidationError: 如果輸入無效或包含可疑內容
    """
    if text is None:
        return ""

    if not isinstance(text, str):
        raise ValidationError("輸入必須是字符串")

    # 長度檢查
    if len(text) > max_length:
        raise ValidationError(f"輸入過長（最多 {max_length} 字符，實際 {len(text)} 字符）")

    # 移除控制字符（保留換行符和製表符）
    allowed_control_chars = {"\n", "\r", "\t"} if allow_newlines else {"\t"}
    text = "".join(
        char for char in text if ord(char) >= 32 or char in allowed_control_chars
    )

    # HTML 轉義（防止 XSS）
    if strip_html:
        text = html.escape(text)

    # 移除多餘的空格
    text = " ".join(text.split())

    return text


def validate_user_query(
    query: str,
    min_length: int = 1,
    max_length: int = 2000,
    check_suspicious: bool = True,
) -> str:
    """
    驗證用戶查詢輸入

    Args:
        query: 用戶查詢字符串
        min_length: 最小長度（默認 1）
        max_length: 最大長度（默認 2000）
        check_suspicious: 是否檢查可疑模式（默認 True）

    Returns:
        驗證後的查詢字符串

    Raises:
        ValidationError: 如果查詢無效
    """
    if not query:
        raise ValidationError("查詢不能為空")

    query = query.strip()

    if len(query) < min_length:
        raise ValidationError(f"查詢過短（最少 {min_length} 字符）")

    if len(query) > max_length:
        raise ValidationError(f"查詢過長（最多 {max_length} 字符）")

    # 檢查可疑的注入模式
    if check_suspicious:
        suspicious_patterns = [
            (r"<script", "檢測到可疑的 script 標籤"),
            (r"javascript:", "檢測到可疑的 javascript: 協議"),
            (r"on\w+\s*=", "檢測到可疑的事件處理器"),
            (r"--\s*$", "檢測到可疑的 SQL 註釋"),
            (r";\s*DROP\s+TABLE", "檢測到可疑的 SQL DROP 語句"),
            (r";\s*DELETE\s+FROM", "檢測到可疑的 SQL DELETE 語句"),
            (r"UNION\s+SELECT", "檢測到可疑的 SQL UNION 語句"),
        ]

        for pattern, message in suspicious_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                logger.warning(f"檢測到可疑查詢: {message}, 查詢: {query[:100]}...")
                raise ValidationError(f"查詢包含可疑內容: {message}")

    return query


def validate_url_safe(url: str, allowed_schemes: Optional[List[str]] = None) -> str:
    """
    安全的 URL 驗證，檢查路徑遍歷和其他攻擊

    Args:
        url: URL 字符串
        allowed_schemes: 允許的協議列表（默認 ['http', 'https']）

    Returns:
        驗證後的安全 URL

    Raises:
        ValidationError: 如果 URL 無效或不安全
    """
    if allowed_schemes is None:
        allowed_schemes = ["http", "https"]

    if not url:
        raise ValidationError("URL 不能為空")

    url = url.strip()

    try:
        parsed = urlparse(url)
    except Exception as e:
        raise ValidationError(f"URL 解析失敗: {e}")

    # 檢查協議
    if not parsed.scheme:
        raise ValidationError("URL 必須包含協議（如 http:// 或 https://）")

    if parsed.scheme.lower() not in allowed_schemes:
        raise ValidationError(
            f"不支援的 URL 協議: {parsed.scheme}. "
            f"允許的協議: {', '.join(allowed_schemes)}"
        )

    # 檢查主機名
    if not parsed.netloc:
        raise ValidationError("URL 必須包含主機名")

    # 檢查路徑遍歷攻擊
    if ".." in parsed.path:
        raise ValidationError("URL 路徑包含可疑的目錄遍歷模式 (..)")

    # 檢查查詢參數中的危險模式
    if parsed.query:
        try:
            query_params = parse_qs(parsed.query)
            for key, values in query_params.items():
                # 檢查鍵名
                if any(char in key for char in ["<", ">", '"', "'"]):
                    raise ValidationError(f"URL 查詢參數包含無效字符: {key}")
                # 檢查值
                for value in values:
                    if any(char in value for char in ["<", ">", '"', "'"]):
                        logger.warning(f"URL 參數值包含可疑字符: {key}={value[:50]}...")
        except ValidationError:
            raise
        except Exception as e:
            logger.warning(f"URL 查詢參數解析警告: {e}")

    return url


def escape_for_html(text: str) -> str:
    """
    將文本轉義為安全的 HTML 內容

    Args:
        text: 要轉義的文本

    Returns:
        HTML 安全的文本
    """
    if text is None:
        return ""
    return html.escape(str(text))


def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
    """
    遮蔽敏感數據（如 API 密鑰）

    Args:
        data: 要遮蔽的數據
        visible_chars: 顯示的前幾個字符（默認 4）

    Returns:
        遮蔽後的字符串（例如：sk-a***）
    """
    if not data:
        return ""

    if len(data) <= visible_chars:
        return "*" * len(data)

    return data[:visible_chars] + "*" * (len(data) - visible_chars)

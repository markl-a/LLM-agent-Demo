"""自定義異常模組 - 定義專案中使用的所有自定義異常類別"""

import logging
from typing import Optional, Any, Dict

logger = logging.getLogger(__name__)


# ============================================================================
# 基礎異常類別
# ============================================================================


class LLMAgentError(Exception):
    """
    LLM Agent 基礎異常類別

    所有自定義異常的基類，提供統一的異常處理介面。
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        初始化異常

        Args:
            message: 錯誤訊息
            error_code: 錯誤代碼（可選）
            details: 額外的錯誤詳情（可選）
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}

    def __str__(self) -> str:
        """返回友好的錯誤訊息"""
        base_msg = f"[{self.error_code}] {self.message}"
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{base_msg} ({details_str})"
        return base_msg

    def to_dict(self) -> Dict[str, Any]:
        """將異常轉換為字典格式，便於日誌記錄"""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
        }


# ============================================================================
# 配置相關異常
# ============================================================================


class ConfigurationError(LLMAgentError):
    """配置錯誤 - 當配置無效或缺失時拋出"""

    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs):
        details = kwargs.pop("details", {})
        if config_key:
            details["config_key"] = config_key
        kwargs["details"] = details
        super().__init__(message, **kwargs)


class APIKeyError(ConfigurationError):
    """API 金鑰錯誤 - 當 API 金鑰無效或缺失時拋出"""

    def __init__(self, provider: str, message: Optional[str] = None, **kwargs):
        msg = message or f"{provider} API 金鑰無效或未設定"
        details = kwargs.pop("details", {})
        details["provider"] = provider
        kwargs["details"] = details
        super().__init__(msg, **kwargs)


# ============================================================================
# 驗證相關異常
# ============================================================================


class ValidationError(LLMAgentError):
    """驗證錯誤 - 當輸入驗證失敗時拋出"""

    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        invalid_value: Optional[Any] = None,
        **kwargs,
    ):
        details = kwargs.pop("details", {})
        if field_name:
            details["field_name"] = field_name
        if invalid_value is not None:
            # 安全地轉換值為字符串（避免洩露敏感信息）
            details["invalid_value"] = self._safe_value_repr(invalid_value)
        kwargs["details"] = details
        super().__init__(message, **kwargs)

    @staticmethod
    def _safe_value_repr(value: Any, max_length: int = 50) -> str:
        """安全地表示值，避免洩露敏感信息"""
        value_str = str(value)
        if len(value_str) > max_length:
            return f"{value_str[:max_length]}...[truncated]"
        return value_str


# ============================================================================
# API 相關異常
# ============================================================================


class APIError(LLMAgentError):
    """API 錯誤基類"""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        provider: Optional[str] = None,
        **kwargs,
    ):
        details = kwargs.pop("details", {})
        if status_code:
            details["status_code"] = status_code
        if provider:
            details["provider"] = provider
        kwargs["details"] = details
        super().__init__(message, **kwargs)


class RateLimitError(APIError):
    """速率限制錯誤 - 當達到 API 速率限制時拋出"""

    def __init__(
        self,
        message: str,
        provider: str = "API",
        retry_after: Optional[float] = None,
        **kwargs,
    ):
        self.retry_after = retry_after
        if retry_after and "retry_after" not in message.lower():
            message += f"，請在 {retry_after:.1f} 秒後重試"
        details = kwargs.pop("details", {})
        details["provider"] = provider
        if retry_after:
            details["retry_after"] = retry_after
        kwargs["details"] = details
        super().__init__(message, provider=provider, status_code=429, **kwargs)


class AuthenticationError(APIError):
    """認證錯誤 - 當 API 認證失敗時拋出"""

    def __init__(self, provider: str, message: Optional[str] = None, **kwargs):
        msg = message or f"{provider} API 認證失敗，請檢查 API 金鑰"
        super().__init__(msg, provider=provider, status_code=401, **kwargs)


class QuotaExceededError(APIError):
    """配額超出錯誤 - 當 API 配額用盡時拋出"""

    def __init__(self, provider: str, message: Optional[str] = None, **kwargs):
        msg = message or f"{provider} API 配額已用盡"
        super().__init__(msg, provider=provider, status_code=429, **kwargs)


class ModelNotFoundError(APIError):
    """模型未找到錯誤 - 當請求的模型不存在時拋出"""

    def __init__(self, model_name: str, provider: str, message: Optional[str] = None, **kwargs):
        msg = message or f"模型 '{model_name}' 在 {provider} 中不存在或無法訪問"
        details = kwargs.get("details", {})
        details["model_name"] = model_name
        super().__init__(msg, provider=provider, status_code=404, details=details, **kwargs)


# ============================================================================
# 網絡相關異常
# ============================================================================


class NetworkError(LLMAgentError):
    """網絡錯誤 - 當網絡請求失敗時拋出"""

    def __init__(
        self,
        message: str,
        url: Optional[str] = None,
        timeout: Optional[float] = None,
        **kwargs,
    ):
        details = kwargs.get("details", {})
        if url:
            details["url"] = url
        if timeout:
            details["timeout"] = timeout
        super().__init__(message, details=details, **kwargs)


class TimeoutError(NetworkError):
    """超時錯誤 - 當請求超時時拋出"""

    def __init__(self, timeout: float, url: Optional[str] = None, message: Optional[str] = None, **kwargs):
        msg = message or f"請求超時（{timeout}秒）"
        super().__init__(msg, url=url, timeout=timeout, **kwargs)


class ConnectionError(NetworkError):
    """連接錯誤 - 當無法建立連接時拋出"""

    def __init__(self, url: Optional[str] = None, message: Optional[str] = None, **kwargs):
        msg = message or "無法建立網絡連接"
        super().__init__(msg, url=url, **kwargs)


# ============================================================================
# 重試相關異常
# ============================================================================


class RetryError(LLMAgentError):
    """重試錯誤 - 當重試配置無效或重試失敗時拋出"""

    def __init__(
        self,
        message: str,
        max_retries: Optional[int] = None,
        attempts: Optional[int] = None,
        **kwargs,
    ):
        details = kwargs.pop("details", {})
        if max_retries is not None:
            details["max_retries"] = max_retries
        if attempts is not None:
            details["attempts"] = attempts
        kwargs["details"] = details
        super().__init__(message, **kwargs)


class MaxRetriesExceededError(RetryError):
    """最大重試次數超出錯誤 - 當達到最大重試次數時拋出"""

    def __init__(
        self,
        max_retries: int,
        operation: str,
        last_error: Optional[Exception] = None,
        **kwargs,
    ):
        message = f"操作 '{operation}' 在 {max_retries} 次重試後仍然失敗"
        details = kwargs.pop("details", {})
        details["operation"] = operation
        if last_error:
            details["last_error"] = str(last_error)
            details["last_error_type"] = type(last_error).__name__
        kwargs["details"] = details
        super().__init__(message, max_retries=max_retries, attempts=max_retries, **kwargs)


# ============================================================================
# 數據處理相關異常
# ============================================================================


class DataError(LLMAgentError):
    """數據錯誤 - 當數據處理失敗時拋出"""

    pass


class FileNotFoundError(DataError):
    """文件未找到錯誤 - 當文件不存在時拋出"""

    def __init__(self, file_path: str, message: Optional[str] = None, **kwargs):
        msg = message or f"文件不存在: {file_path}"
        details = kwargs.get("details", {})
        details["file_path"] = file_path
        super().__init__(msg, details=details, **kwargs)


class FileReadError(DataError):
    """文件讀取錯誤 - 當文件讀取失敗時拋出"""

    def __init__(self, file_path: str, reason: Optional[str] = None, **kwargs):
        msg = f"無法讀取文件: {file_path}"
        if reason:
            msg += f" ({reason})"
        details = kwargs.get("details", {})
        details["file_path"] = file_path
        if reason:
            details["reason"] = reason
        super().__init__(msg, details=details, **kwargs)


class FileWriteError(DataError):
    """文件寫入錯誤 - 當文件寫入失敗時拋出"""

    def __init__(self, file_path: str, reason: Optional[str] = None, **kwargs):
        msg = f"無法寫入文件: {file_path}"
        if reason:
            msg += f" ({reason})"
        details = kwargs.get("details", {})
        details["file_path"] = file_path
        if reason:
            details["reason"] = reason
        super().__init__(msg, details=details, **kwargs)


class InvalidDataError(DataError):
    """無效數據錯誤 - 當數據格式無效時拋出"""

    def __init__(self, message: str, data_type: Optional[str] = None, **kwargs):
        details = kwargs.get("details", {})
        if data_type:
            details["data_type"] = data_type
        super().__init__(message, details=details, **kwargs)


# ============================================================================
# 成本追蹤相關異常
# ============================================================================


class CostTrackingError(LLMAgentError):
    """成本追蹤錯誤 - 當成本追蹤失敗時拋出"""

    pass


class PricingNotFoundError(CostTrackingError):
    """定價未找到錯誤 - 當模型定價不存在時拋出"""

    def __init__(self, model_name: str, message: Optional[str] = None, **kwargs):
        msg = message or f"無法找到模型 '{model_name}' 的定價信息"
        details = kwargs.get("details", {})
        details["model_name"] = model_name
        super().__init__(msg, details=details, **kwargs)


# ============================================================================
# 向量數據庫相關異常
# ============================================================================


class VectorStoreError(LLMAgentError):
    """向量數據庫錯誤基類"""

    def __init__(self, message: str, store_type: Optional[str] = None, **kwargs):
        details = kwargs.get("details", {})
        if store_type:
            details["store_type"] = store_type
        super().__init__(message, details=details, **kwargs)


class EmbeddingError(VectorStoreError):
    """嵌入錯誤 - 當文本嵌入失敗時拋出"""

    def __init__(self, message: str, text_length: Optional[int] = None, **kwargs):
        details = kwargs.get("details", {})
        if text_length is not None:
            details["text_length"] = text_length
        super().__init__(message, details=details, **kwargs)


# ============================================================================
# Agent 相關異常
# ============================================================================


class AgentError(LLMAgentError):
    """Agent 錯誤基類"""

    def __init__(self, message: str, agent_type: Optional[str] = None, **kwargs):
        details = kwargs.get("details", {})
        if agent_type:
            details["agent_type"] = agent_type
        super().__init__(message, details=details, **kwargs)


class AgentExecutionError(AgentError):
    """Agent 執行錯誤 - 當 Agent 執行失敗時拋出"""

    pass


class ToolExecutionError(AgentError):
    """工具執行錯誤 - 當工具執行失敗時拋出"""

    def __init__(self, tool_name: str, reason: Optional[str] = None, **kwargs):
        msg = f"工具 '{tool_name}' 執行失敗"
        if reason:
            msg += f": {reason}"
        details = kwargs.get("details", {})
        details["tool_name"] = tool_name
        if reason:
            details["reason"] = reason
        super().__init__(msg, details=details, **kwargs)


# ============================================================================
# 便利函數
# ============================================================================


def handle_exception(
    exc: Exception,
    logger_instance: Optional[logging.Logger] = None,
    re_raise: bool = True,
    default_message: str = "發生未知錯誤",
) -> Optional[LLMAgentError]:
    """
    統一的異常處理函數

    Args:
        exc: 捕獲的異常
        logger_instance: 日誌記錄器（可選）
        re_raise: 是否重新拋出異常（默認 True）
        default_message: 默認錯誤訊息

    Returns:
        轉換後的 LLMAgentError（如果 re_raise=False）

    Raises:
        LLMAgentError: 如果 re_raise=True
    """
    log = logger_instance or logger

    # 如果已經是我們的自定義異常，直接處理
    if isinstance(exc, LLMAgentError):
        log.error(f"異常: {exc}", extra={"error_details": exc.to_dict()})
        if re_raise:
            raise exc
        return exc

    # 將標準異常轉換為自定義異常
    error_mapping = {
        ValueError: ValidationError,
        TypeError: ValidationError,
        KeyError: ConfigurationError,
        FileNotFoundError: FileNotFoundError,
        PermissionError: FileReadError,
        IOError: DataError,
        OSError: DataError,
    }

    error_class = error_mapping.get(type(exc), LLMAgentError)
    custom_error = error_class(
        message=str(exc) or default_message,
        details={"original_error": type(exc).__name__},
    )

    log.error(f"異常: {custom_error}", extra={"error_details": custom_error.to_dict()}, exc_info=True)

    if re_raise:
        raise custom_error from exc
    return custom_error


def wrap_exception(
    func_name: str,
    exc: Exception,
    error_class: type = LLMAgentError,
    **kwargs,
) -> LLMAgentError:
    """
    包裝異常並添加上下文信息

    Args:
        func_name: 函數名稱
        exc: 原始異常
        error_class: 目標異常類別
        **kwargs: 額外的參數傳遞給異常類別

    Returns:
        包裝後的異常
    """
    message = f"函數 '{func_name}' 執行失敗: {str(exc)}"
    details = kwargs.get("details", {})
    details["function"] = func_name
    details["original_error"] = type(exc).__name__
    details["original_message"] = str(exc)

    return error_class(message, details=details, **{k: v for k, v in kwargs.items() if k != "details"})

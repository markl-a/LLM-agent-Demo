"""工具模組 - 提供通用工具函數"""

from .config import Settings, get_settings
from .cost_tracker import CostTracker, TokenCounter
from .logger import get_logger, setup_logging
from .retry import (
    RetryContext,
    retry_on_network_error,
    retry_on_rate_limit,
    retry_with_exponential_backoff,
)
from .validators import validate_api_key, validate_model_name, validate_user_query
from .exceptions import (
    # 基礎異常
    LLMAgentError,
    # 配置相關
    ConfigurationError,
    APIKeyError,
    # 驗證相關
    ValidationError,
    # API 相關
    APIError,
    RateLimitError,
    AuthenticationError,
    QuotaExceededError,
    ModelNotFoundError,
    # 網絡相關
    NetworkError,
    TimeoutError,
    ConnectionError,
    # 重試相關
    RetryError,
    MaxRetriesExceededError,
    # 數據相關
    DataError,
    FileNotFoundError,
    FileReadError,
    FileWriteError,
    InvalidDataError,
    # 成本追蹤相關
    CostTrackingError,
    PricingNotFoundError,
    # 向量數據庫相關
    VectorStoreError,
    EmbeddingError,
    # Agent 相關
    AgentError,
    AgentExecutionError,
    ToolExecutionError,
    # 工具函數
    handle_exception,
    wrap_exception,
)

__all__ = [
    # 配置
    "Settings",
    "get_settings",
    # 日誌
    "get_logger",
    "setup_logging",
    # 成本追蹤
    "CostTracker",
    "TokenCounter",
    # 重試機制
    "retry_with_exponential_backoff",
    "retry_on_rate_limit",
    "retry_on_network_error",
    "RetryContext",
    # 驗證器
    "validate_api_key",
    "validate_model_name",
    "validate_user_query",
    # 異常類別 - 基礎
    "LLMAgentError",
    # 異常類別 - 配置
    "ConfigurationError",
    "APIKeyError",
    # 異常類別 - 驗證
    "ValidationError",
    # 異常類別 - API
    "APIError",
    "RateLimitError",
    "AuthenticationError",
    "QuotaExceededError",
    "ModelNotFoundError",
    # 異常類別 - 網絡
    "NetworkError",
    "TimeoutError",
    "ConnectionError",
    # 異常類別 - 重試
    "RetryError",
    "MaxRetriesExceededError",
    # 異常類別 - 數據
    "DataError",
    "FileNotFoundError",
    "FileReadError",
    "FileWriteError",
    "InvalidDataError",
    # 異常類別 - 成本追蹤
    "CostTrackingError",
    "PricingNotFoundError",
    # 異常類別 - 向量數據庫
    "VectorStoreError",
    "EmbeddingError",
    # 異常類別 - Agent
    "AgentError",
    "AgentExecutionError",
    "ToolExecutionError",
    # 異常處理工具
    "handle_exception",
    "wrap_exception",
]

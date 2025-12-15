"""工具模組 - 提供通用工具函數"""

from .config import Settings, get_settings
from .cost_tracker import CostTracker, TokenCounter
from .logger import get_logger, setup_logging
from .rate_limiter import (
    GlobalRateLimiter,
    RateLimiter,
    RateLimitStrategy,
    SlidingWindow,
    TokenBucket,
    get_global_limiter,
    rate_limit,
)
from .retry import (
    RetryContext,
    retry_on_network_error,
    retry_on_rate_limit,
    retry_with_exponential_backoff,
)
from .validators import validate_api_key, validate_model_name, validate_user_query
from .templates import (
    PromptTemplate,
    TemplateLoader,
    create_template,
    load_template,
)
from .metrics import (
    APICall,
    APICallTracker,
    Counter,
    Gauge,
    Histogram,
    MetricsCollector,
    create_standard_metrics,
    get_metrics_collector,
    track_api_call,
    track_latency,
)
from .events import (
    EventEmitter,
    Event,
    EventListener,
    EventStats,
    EventType,
    EventPriority,
    get_global_emitter,
    set_global_emitter,
    event_handler,
    emit_event,
    emit,
    emit_async,
    on,
    on_async,
    off,
)
from .serialization import (
    # JSON 編碼器
    EnhancedJSONEncoder,
    json_decode_hook,
    # JSON 序列化
    serialize_json,
    deserialize_json,
    save_json,
    load_json,
    # YAML 序列化
    serialize_yaml,
    deserialize_yaml,
    save_yaml,
    load_yaml,
    # 壓縮
    compress_data,
    decompress_data,
    # 類型安全序列化
    serialize_with_type,
    deserialize_with_type,
    # 便捷函數
    to_json_string,
    from_json_string,
    get_size_info,
)
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
    # 速率限制
    "RateLimiter",
    "TokenBucket",
    "SlidingWindow",
    "GlobalRateLimiter",
    "RateLimitStrategy",
    "rate_limit",
    "get_global_limiter",
    # 重試機制
    "retry_with_exponential_backoff",
    "retry_on_rate_limit",
    "retry_on_network_error",
    "RetryContext",
    # 驗證器
    "validate_api_key",
    "validate_model_name",
    "validate_user_query",
    # 模板引擎
    "PromptTemplate",
    "TemplateLoader",
    "create_template",
    "load_template",
    # 監控指標
    "Counter",
    "Gauge",
    "Histogram",
    "MetricsCollector",
    "APICall",
    "APICallTracker",
    "track_latency",
    "track_api_call",
    "get_metrics_collector",
    "create_standard_metrics",
    # 事件系統 - 核心類
    "EventEmitter",
    "Event",
    "EventListener",
    "EventStats",
    # 事件系統 - 枚舉
    "EventType",
    "EventPriority",
    # 事件系統 - 全局實例
    "get_global_emitter",
    "set_global_emitter",
    # 事件系統 - 裝飾器
    "event_handler",
    "emit_event",
    # 事件系統 - 便捷函數
    "emit",
    "emit_async",
    "on",
    "on_async",
    "off",
    # 序列化 - JSON 編碼器
    "EnhancedJSONEncoder",
    "json_decode_hook",
    # 序列化 - JSON
    "serialize_json",
    "deserialize_json",
    "save_json",
    "load_json",
    # 序列化 - YAML
    "serialize_yaml",
    "deserialize_yaml",
    "save_yaml",
    "load_yaml",
    # 序列化 - 壓縮
    "compress_data",
    "decompress_data",
    # 序列化 - 類型安全
    "serialize_with_type",
    "deserialize_with_type",
    # 序列化 - 便捷函數
    "to_json_string",
    "from_json_string",
    "get_size_info",
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

"""
LLM Agent Demo - 多框架 LLM Agent 開發教學庫

本模組提供了多個主流 LLM Agent 框架的實用工具和範例實現。

支援的框架：
- LangChain: 建立 RAG、Agent 和鏈式應用
- LlamaIndex: 高效的索引和查詢引擎
- AutoGen: 多 Agent 對話系統
- CrewAI: 團隊協作式 AI Agent
- MetaGPT: 軟體開發 Agent 系統

主要功能：
- 向量存儲和檢索
- RAG（檢索增強生成）
- Agent 工具和鏈
- 成本追蹤和監控
- 配置管理
"""

__version__ = "2.0.0"
__author__ = "markl-a"
__license__ = "MIT"

from typing import Optional

# ==================== 核心工具導出 ====================
# 可選導入，避免強制依賴
try:
    # 配置管理
    from .utils.config import (
        Settings,
        get_settings,
        reload_settings,
        get_openai_config,
        get_anthropic_config,
        get_google_config,
        get_groq_config,
    )

    # 日誌管理
    from .utils.logger import (
        get_logger,
        setup_logging,
        get_app_logger,
    )

    # 成本追蹤
    from .utils.cost_tracker import (
        CostTracker,
        TokenCounter,
        TokenUsage,
    )

    # 重試機制
    from .utils.retry import (
        retry_with_exponential_backoff,
        retry_on_rate_limit,
        retry_on_network_error,
        RetryContext,
    )

    # 驗證器
    from .utils.validators import (
        validate_api_key,
        validate_openai_api_key,
        validate_anthropic_api_key,
        validate_model_name,
        validate_temperature,
        validate_max_tokens,
        validate_user_query,
        sanitize_user_input,
        ValidationError,
    )

except ImportError as e:
    # 如果導入失敗，設置為 None
    Settings = None
    get_settings = None
    reload_settings = None
    get_openai_config = None
    get_anthropic_config = None
    get_google_config = None
    get_groq_config = None
    get_logger = None
    setup_logging = None
    get_app_logger = None
    CostTracker = None
    TokenCounter = None
    TokenUsage = None
    retry_with_exponential_backoff = None
    retry_on_rate_limit = None
    retry_on_network_error = None
    RetryContext = None
    validate_api_key = None
    validate_openai_api_key = None
    validate_anthropic_api_key = None
    validate_model_name = None
    validate_temperature = None
    validate_max_tokens = None
    validate_user_query = None
    sanitize_user_input = None
    ValidationError = None

# ==================== LangChain 工具導出 ====================
# 可選導入 LangChain 相關功能
try:
    from .langchain import (
        create_chat_model,
        create_embeddings,
        create_vector_store,
        RAGConfig,
        SYSTEM_PROMPTS,
    )
except ImportError:
    create_chat_model = None
    create_embeddings = None
    create_vector_store = None
    RAGConfig = None
    SYSTEM_PROMPTS = None

# ==================== 公開 API ====================
__all__ = [
    # 版本信息
    "__version__",
    "__author__",
    "__license__",

    # 配置管理
    "Settings",
    "get_settings",
    "reload_settings",
    "get_openai_config",
    "get_anthropic_config",
    "get_google_config",
    "get_groq_config",

    # 日誌管理
    "get_logger",
    "setup_logging",
    "get_app_logger",

    # 成本追蹤
    "CostTracker",
    "TokenCounter",
    "TokenUsage",

    # 重試機制
    "retry_with_exponential_backoff",
    "retry_on_rate_limit",
    "retry_on_network_error",
    "RetryContext",

    # 驗證器
    "validate_api_key",
    "validate_openai_api_key",
    "validate_anthropic_api_key",
    "validate_model_name",
    "validate_temperature",
    "validate_max_tokens",
    "validate_user_query",
    "sanitize_user_input",
    "ValidationError",

    # LangChain 工具
    "create_chat_model",
    "create_embeddings",
    "create_vector_store",
    "RAGConfig",
    "SYSTEM_PROMPTS",
]

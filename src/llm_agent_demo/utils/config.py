"""配置管理模組 - 使用 Pydantic Settings 管理環境變數和配置"""

import os
from functools import lru_cache
from typing import Optional, Dict, Any
from pathlib import Path

try:
    from pydantic import Field, field_validator
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError:
    # 如果 pydantic-settings 未安裝，提供向後兼容
    from pydantic import BaseSettings, Field, validator as field_validator

    class SettingsConfigDict:
        """向後兼容的配置字典"""

        pass


class Settings(BaseSettings):
    """
    應用程式配置設定

    所有配置都可以通過環境變數設定，環境變數會覆蓋 .env 文件中的值。
    """

    # ============= LLM 提供商設定 =============
    openai_api_key: Optional[str] = Field(None, description="OpenAI API 金鑰")
    openai_api_base: Optional[str] = Field(
        "https://api.openai.com/v1", description="OpenAI API 基礎 URL"
    )
    openai_model: str = Field("gpt-4o-mini", description="預設 OpenAI 模型")

    anthropic_api_key: Optional[str] = Field(None, description="Anthropic API 金鑰")
    anthropic_model: str = Field("claude-3-5-sonnet-20241022", description="預設 Anthropic 模型")

    google_api_key: Optional[str] = Field(None, description="Google Gemini API 金鑰")
    google_model: str = Field("gemini-2.0-flash-exp", description="預設 Google 模型")

    groq_api_key: Optional[str] = Field(None, description="Groq API 金鑰")
    groq_model: str = Field("llama-3.3-70b-versatile", description="預設 Groq 模型")

    # ============= 向量數據庫設定 =============
    chroma_persist_directory: str = Field("./chroma_db", description="Chroma 持久化目錄")
    pinecone_api_key: Optional[str] = Field(None, description="Pinecone API 金鑰")
    pinecone_environment: Optional[str] = Field(None, description="Pinecone 環境")
    qdrant_url: Optional[str] = Field("http://localhost:6333", description="Qdrant URL")
    qdrant_api_key: Optional[str] = Field(None, description="Qdrant API 金鑰")

    # ============= 搜索和工具設定 =============
    serper_api_key: Optional[str] = Field(None, description="Serper API 金鑰（Google 搜索）")
    tavily_api_key: Optional[str] = Field(None, description="Tavily API 金鑰（AI 搜索）")

    # ============= 監控設定 =============
    langsmith_api_key: Optional[str] = Field(None, description="LangSmith API 金鑰")
    langsmith_project: str = Field("llm-agent-demo", description="LangSmith 專案名稱")
    langsmith_tracing: bool = Field(False, description="是否啟用 LangSmith 追蹤")

    # ============= 應用程式設定 =============
    app_env: str = Field("development", description="應用環境（development/production）")
    debug: bool = Field(False, description="除錯模式")
    log_level: str = Field("INFO", description="日誌級別")
    max_retries: int = Field(3, description="API 請求最大重試次數")
    timeout: int = Field(30, description="API 請求超時時間（秒）")

    # ============= RAG 設定 =============
    chunk_size: int = Field(1000, description="文檔分塊大小")
    chunk_overlap: int = Field(200, description="分塊重疊大小")
    top_k: int = Field(5, description="檢索返回的文檔數量")
    embedding_model: str = Field("text-embedding-3-small", description="嵌入模型")

    # ============= 成本控制設定 =============
    max_tokens: int = Field(4000, description="最大輸出 token 數")
    temperature: float = Field(0.7, description="生成溫度")
    enable_cost_tracking: bool = Field(True, description="是否啟用成本追蹤")

    # Pydantic v2 配置
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # 忽略額外的環境變數
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """驗證日誌級別"""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v = v.upper()
        if v not in valid_levels:
            raise ValueError(f"log_level 必須是以下之一: {valid_levels}")
        return v

    @field_validator("app_env")
    @classmethod
    def validate_app_env(cls, v: str) -> str:
        """驗證應用環境"""
        valid_envs = {"development", "staging", "production"}
        v = v.lower()
        if v not in valid_envs:
            raise ValueError(f"app_env 必須是以下之一: {valid_envs}")
        return v

    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        """驗證溫度參數"""
        if not 0.0 <= v <= 2.0:
            raise ValueError("temperature 必須在 0.0 到 2.0 之間")
        return v

    def get_llm_config(self, provider: str = "openai") -> Dict[str, Any]:
        """
        獲取特定 LLM 提供商的配置

        Args:
            provider: LLM 提供商名稱（openai, anthropic, google, groq）

        Returns:
            配置字典

        Raises:
            ValueError: 如果提供商不支援或缺少 API 金鑰
        """
        provider = provider.lower()
        configs = {
            "openai": {
                "api_key": self.openai_api_key,
                "model": self.openai_model,
                "api_base": self.openai_api_base,
            },
            "anthropic": {
                "api_key": self.anthropic_api_key,
                "model": self.anthropic_model,
            },
            "google": {
                "api_key": self.google_api_key,
                "model": self.google_model,
            },
            "groq": {
                "api_key": self.groq_api_key,
                "model": self.groq_model,
            },
        }

        if provider not in configs:
            raise ValueError(
                f"不支援的 LLM 提供商: {provider}。支援的提供商: {list(configs.keys())}"
            )

        config = configs[provider]
        if not config["api_key"]:
            raise ValueError(f"{provider.upper()} API 金鑰未設定")

        return config

    def is_production(self) -> bool:
        """檢查是否為生產環境"""
        return self.app_env == "production"

    def is_development(self) -> bool:
        """檢查是否為開發環境"""
        return self.app_env == "development"


@lru_cache()
def get_settings() -> Settings:
    """
    獲取應用程式設定單例

    使用 lru_cache 確保設定只被載入一次。

    Returns:
        Settings 實例
    """
    return Settings()


def reload_settings() -> Settings:
    """
    重新載入設定（清除快取）

    在測試或需要動態更新配置時使用。

    Returns:
        新的 Settings 實例
    """
    get_settings.cache_clear()
    return get_settings()


# 便利函數
def get_openai_config() -> Dict[str, Any]:
    """獲取 OpenAI 配置"""
    return get_settings().get_llm_config("openai")


def get_anthropic_config() -> Dict[str, Any]:
    """獲取 Anthropic 配置"""
    return get_settings().get_llm_config("anthropic")


def get_google_config() -> Dict[str, Any]:
    """獲取 Google 配置"""
    return get_settings().get_llm_config("google")


def get_groq_config() -> Dict[str, Any]:
    """獲取 Groq 配置"""
    return get_settings().get_llm_config("groq")

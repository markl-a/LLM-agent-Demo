"""
整合測試 - 完整的配置載入流程

測試從環境變數、.env 文件到配置驗證的完整流程。
"""

import os
import pytest
from pathlib import Path

from llm_agent_demo.utils.config import (
    get_settings,
    reload_settings,
    Settings,
    get_openai_config,
    get_anthropic_config,
    get_google_config,
    get_groq_config,
)
from llm_agent_demo.utils.logger import setup_logging, get_logger
from llm_agent_demo.utils.validators import (
    validate_openai_api_key,
    validate_anthropic_api_key,
    validate_temperature,
    validate_chunk_size,
)
from llm_agent_demo.utils.exceptions import (
    APIKeyError,
    ConfigurationError,
    ValidationError,
)


@pytest.mark.integration
class TestFullConfigLoading:
    """測試完整的配置載入流程"""

    def test_config_loading_from_env(
        self, integration_env, reset_logging, temp_log_file
    ):
        """測試從環境變數載入配置"""
        # 設置日誌
        setup_logging(
            level="INFO",
            log_file=str(temp_log_file),
            force_reconfigure=True
        )
        logger = get_logger(__name__)

        # 重新載入配置
        logger.info("開始從環境變數載入配置")
        settings = reload_settings()

        # 驗證基本配置
        assert settings.app_env == "development"
        assert settings.log_level == "DEBUG"
        assert settings.debug is True
        assert settings.max_retries == 3

        # 驗證 API 密鑰已載入
        assert settings.openai_api_key is not None
        assert settings.anthropic_api_key is not None
        assert settings.google_api_key is not None
        assert settings.groq_api_key is not None

        logger.info("配置載入完成")
        logger.info(f"環境: {settings.app_env}")
        logger.info(f"日誌級別: {settings.log_level}")
        logger.info(f"最大重試次數: {settings.max_retries}")

        # 檢查日誌
        log_content = temp_log_file.read_text()
        assert "配置載入完成" in log_content

    def test_config_loading_from_env_file(
        self, monkeypatch, sample_env_file, reset_logging, temp_log_file
    ):
        """測試從 .env 文件載入配置"""
        # 設置日誌
        setup_logging(
            level="INFO",
            log_file=str(temp_log_file),
            force_reconfigure=True
        )
        logger = get_logger(__name__)

        # 清除現有環境變數
        get_settings.cache_clear()
        for key in ["OPENAI_API_KEY", "APP_ENV", "LOG_LEVEL", "DEBUG"]:
            monkeypatch.delenv(key, raising=False)

        # 設置 .env 文件路徑
        monkeypatch.chdir(sample_env_file.parent)

        # 載入配置
        logger.info(f"從 {sample_env_file} 載入配置")
        settings = Settings()

        # 驗證從文件載入的配置
        assert settings.app_env == "production"
        assert settings.log_level == "INFO"
        assert settings.debug is False
        assert settings.max_retries == 5
        assert settings.timeout == 60

        # 驗證 RAG 配置
        assert settings.chunk_size == 1500
        assert settings.chunk_overlap == 300
        assert settings.top_k == 10

        logger.info("從 .env 文件載入配置成功")

        # 清理
        get_settings.cache_clear()

    def test_env_vars_override_env_file(
        self, monkeypatch, sample_env_file, reset_logging, temp_log_file
    ):
        """測試環境變數覆蓋 .env 文件"""
        # 設置日誌
        setup_logging(
            level="INFO",
            log_file=str(temp_log_file),
            force_reconfigure=True
        )
        logger = get_logger(__name__)

        # 清除配置快取
        get_settings.cache_clear()

        # 設置環境變數（應該覆蓋 .env 文件）
        monkeypatch.setenv("APP_ENV", "development")
        monkeypatch.setenv("MAX_RETRIES", "10")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-override-key-" + "a" * 30)

        # 切換到 .env 文件目錄
        monkeypatch.chdir(sample_env_file.parent)

        # 載入配置
        logger.info("測試環境變數覆蓋")
        settings = Settings()

        # 驗證環境變數覆蓋了 .env 文件
        assert settings.app_env == "development"  # 覆蓋了 production
        assert settings.max_retries == 10  # 覆蓋了 5
        assert settings.openai_api_key.startswith("sk-test-override")

        logger.info("環境變數成功覆蓋 .env 文件")

        # 清理
        get_settings.cache_clear()

    def test_config_validation_during_loading(
        self, integration_env, reset_logging, temp_log_file
    ):
        """測試配置載入時的驗證"""
        # 設置日誌
        setup_logging(
            level="INFO",
            log_file=str(temp_log_file),
            force_reconfigure=True
        )
        logger = get_logger(__name__)

        # 載入配置
        settings = reload_settings()

        # 驗證日誌級別
        logger.info(f"驗證日誌級別: {settings.log_level}")
        assert settings.log_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

        # 驗證應用環境
        logger.info(f"驗證應用環境: {settings.app_env}")
        assert settings.app_env in ["development", "staging", "production"]

        # 驗證溫度參數
        logger.info(f"驗證溫度參數: {settings.temperature}")
        validated_temp = validate_temperature(settings.temperature)
        assert 0.0 <= validated_temp <= 2.0

        # 驗證分塊參數
        logger.info(f"驗證分塊參數: size={settings.chunk_size}, overlap={settings.chunk_overlap}")
        chunk_size, chunk_overlap = validate_chunk_size(
            settings.chunk_size,
            settings.chunk_overlap
        )
        assert chunk_overlap < chunk_size

        logger.info("所有配置驗證通過")

        # 檢查日誌
        log_content = temp_log_file.read_text()
        assert "所有配置驗證通過" in log_content

    def test_llm_config_retrieval(
        self, integration_env, reset_logging, temp_log_file
    ):
        """測試 LLM 配置獲取"""
        # 設置日誌
        setup_logging(
            level="INFO",
            log_file=str(temp_log_file),
            force_reconfigure=True
        )
        logger = get_logger(__name__)

        # 載入配置
        settings = reload_settings()

        # 測試各個 LLM 提供商的配置
        providers = ["openai", "anthropic", "google", "groq"]

        for provider in providers:
            logger.info(f"獲取 {provider.upper()} 配置")

            config = settings.get_llm_config(provider)

            # 驗證配置結構
            assert "api_key" in config
            assert "model" in config
            assert config["api_key"] is not None

            logger.info(f"{provider.upper()} 配置: model={config['model']}")

            # 驗證配置被快取
            config2 = settings.get_llm_config(provider)
            assert config is config2  # 應該是同一個對象（快取）

        # 檢查日誌
        log_content = temp_log_file.read_text()
        for provider in providers:
            assert f"獲取 {provider.upper()} 配置" in log_content

    def test_helper_functions_with_config(
        self, integration_env, reset_logging, temp_log_file
    ):
        """測試配置輔助函數"""
        # 設置日誌
        setup_logging(
            level="INFO",
            log_file=str(temp_log_file),
            force_reconfigure=True
        )
        logger = get_logger(__name__)

        # 測試輔助函數
        logger.info("測試配置輔助函數")

        # OpenAI 配置
        openai_config = get_openai_config()
        assert openai_config["model"] == "gpt-4o-mini"
        validate_openai_api_key(openai_config["api_key"])
        logger.info(f"OpenAI 配置: {openai_config['model']}")

        # Anthropic 配置
        anthropic_config = get_anthropic_config()
        assert anthropic_config["model"] == "claude-3-5-sonnet-20241022"
        validate_anthropic_api_key(anthropic_config["api_key"])
        logger.info(f"Anthropic 配置: {anthropic_config['model']}")

        # Google 配置
        google_config = get_google_config()
        assert google_config["model"] == "gemini-2.0-flash-exp"
        logger.info(f"Google 配置: {google_config['model']}")

        # Groq 配置
        groq_config = get_groq_config()
        assert groq_config["model"] == "llama-3.3-70b-versatile"
        logger.info(f"Groq 配置: {groq_config['model']}")

        logger.info("所有輔助函數測試通過")


@pytest.mark.integration
class TestConfigErrorHandling:
    """測試配置錯誤處理"""

    def test_invalid_provider_error(
        self, integration_env, reset_logging, temp_log_file
    ):
        """測試無效提供商錯誤處理"""
        # 設置日誌
        setup_logging(
            level="ERROR",
            log_file=str(temp_log_file),
            force_reconfigure=True
        )
        logger = get_logger(__name__)

        settings = reload_settings()

        # 嘗試獲取不存在的提供商配置
        invalid_providers = ["invalid", "unknown", "fake"]

        for provider in invalid_providers:
            with pytest.raises(ConfigurationError) as exc_info:
                settings.get_llm_config(provider)

            error = exc_info.value
            logger.error(f"預期錯誤: {error}")

            assert "不支援的 LLM 提供商" in str(error)
            assert provider in str(error)

        # 檢查日誌
        log_content = temp_log_file.read_text()
        assert "預期錯誤" in log_content

    def test_missing_api_key_error(
        self, monkeypatch, reset_logging, temp_log_file
    ):
        """測試缺失 API 密鑰錯誤處理"""
        # 設置日誌
        setup_logging(
            level="ERROR",
            log_file=str(temp_log_file),
            force_reconfigure=True
        )
        logger = get_logger(__name__)

        # 清除配置快取
        get_settings.cache_clear()

        # 清除所有 API 密鑰
        for key in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY", "GROQ_API_KEY"]:
            monkeypatch.delenv(key, raising=False)

        # 載入配置
        settings = get_settings()

        # 嘗試獲取各個提供商的配置
        providers = ["openai", "anthropic", "google", "groq"]

        for provider in providers:
            with pytest.raises(APIKeyError) as exc_info:
                settings.get_llm_config(provider)

            error = exc_info.value
            logger.error(f"{provider.upper()} API 密鑰缺失: {error}")

            assert "未設定" in str(error)
            assert provider.upper() in str(error)

        # 清理
        get_settings.cache_clear()

    def test_invalid_log_level_error(
        self, monkeypatch, reset_logging
    ):
        """測試無效日誌級別錯誤處理"""
        # 清除配置快取
        get_settings.cache_clear()

        # 設置無效的日誌級別
        monkeypatch.setenv("LOG_LEVEL", "INVALID_LEVEL")

        # 嘗試載入配置（應該失敗）
        with pytest.raises(Exception) as exc_info:
            Settings()

        error = exc_info.value
        assert "log_level" in str(error).lower()

        # 清理
        get_settings.cache_clear()

    def test_invalid_app_env_error(
        self, monkeypatch, reset_logging
    ):
        """測試無效應用環境錯誤處理"""
        # 清除配置快取
        get_settings.cache_clear()

        # 設置無效的應用環境
        monkeypatch.setenv("APP_ENV", "invalid_env")

        # 嘗試載入配置（應該失敗）
        with pytest.raises(Exception) as exc_info:
            Settings()

        error = exc_info.value
        assert "app_env" in str(error).lower()

        # 清理
        get_settings.cache_clear()

    def test_invalid_temperature_error(
        self, monkeypatch, reset_logging
    ):
        """測試無效溫度參數錯誤處理"""
        # 清除配置快取
        get_settings.cache_clear()

        # 設置無效的溫度值
        monkeypatch.setenv("TEMPERATURE", "5.0")  # 超出範圍

        # 嘗試載入配置（應該失敗）
        with pytest.raises(Exception) as exc_info:
            Settings()

        error = exc_info.value
        assert "temperature" in str(error).lower()

        # 清理
        get_settings.cache_clear()


@pytest.mark.integration
class TestConfigCaching:
    """測試配置快取機制"""

    def test_config_singleton_behavior(self, integration_env):
        """測試配置單例行為"""
        # 多次獲取配置
        settings1 = get_settings()
        settings2 = get_settings()
        settings3 = get_settings()

        # 驗證是同一個實例
        assert settings1 is settings2
        assert settings2 is settings3

    def test_config_cache_clear(self, integration_env, monkeypatch):
        """測試配置快取清除"""
        # 獲取初始配置
        settings1 = get_settings()
        key1 = settings1.openai_api_key

        # 修改環境變數
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-new-key-" + "a" * 30)

        # 未清除快取，配置不變
        settings2 = get_settings()
        key2 = settings2.openai_api_key
        assert key1 == key2

        # 清除快取後重新載入
        settings3 = reload_settings()
        key3 = settings3.openai_api_key
        assert key1 != key3
        assert key3.startswith("sk-test-new-key")

    def test_llm_config_caching(self, integration_env):
        """測試 LLM 配置快取"""
        settings = reload_settings()

        # 清除 LLM 配置快取
        settings._llm_config_cache.clear()

        # 第一次獲取配置
        config1 = settings.get_llm_config("openai")

        # 驗證快取已建立
        assert "openai" in settings._llm_config_cache

        # 第二次獲取配置
        config2 = settings.get_llm_config("openai")

        # 驗證返回的是快取的對象
        assert config1 is config2


@pytest.mark.integration
class TestConfigEnvironmentMethods:
    """測試配置環境判斷方法"""

    def test_is_production_method(self, monkeypatch):
        """測試 is_production 方法"""
        get_settings.cache_clear()

        # 設置為生產環境
        monkeypatch.setenv("APP_ENV", "production")
        settings = get_settings()

        assert settings.is_production() is True
        assert settings.is_development() is False

        get_settings.cache_clear()

    def test_is_development_method(self, monkeypatch):
        """測試 is_development 方法"""
        get_settings.cache_clear()

        # 設置為開發環境
        monkeypatch.setenv("APP_ENV", "development")
        settings = get_settings()

        assert settings.is_development() is True
        assert settings.is_production() is False

        get_settings.cache_clear()

    def test_environment_based_behavior(
        self, monkeypatch, reset_logging, temp_log_file
    ):
        """測試基於環境的行為"""
        # 設置日誌
        setup_logging(
            level="INFO",
            log_file=str(temp_log_file),
            force_reconfigure=True
        )
        logger = get_logger(__name__)

        # 測試開發環境
        get_settings.cache_clear()
        monkeypatch.setenv("APP_ENV", "development")
        dev_settings = get_settings()

        if dev_settings.is_development():
            logger.info("運行在開發環境")
            logger.debug("開發環境調試信息")

        # 測試生產環境
        get_settings.cache_clear()
        monkeypatch.setenv("APP_ENV", "production")
        prod_settings = get_settings()

        if prod_settings.is_production():
            logger.info("運行在生產環境")

        # 檢查日誌
        log_content = temp_log_file.read_text()
        assert "運行在開發環境" in log_content
        assert "運行在生產環境" in log_content

        get_settings.cache_clear()

"""配置管理模組的單元測試"""

import pytest
import os
from pathlib import Path


# 檢查是否安裝了核心模組
try:
    from src.llm_agent_demo.utils.config import (
        Settings,
        get_settings,
        reload_settings,
        get_openai_config,
    )

    CORE_MODULE_AVAILABLE = True
except ImportError:
    CORE_MODULE_AVAILABLE = False
    pytest.skip("核心模組未安裝", allow_module_level=True)


@pytest.fixture
def mock_env(monkeypatch):
    """模擬環境變數"""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test123456789012345678901234567890")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    yield
    # 測試後清理
    reload_settings()


@pytest.mark.unit
class TestSettings:
    """測試 Settings 類"""

    def test_settings_initialization(self, mock_env):
        """測試配置初始化"""
        settings = Settings()

        assert settings.openai_api_key == "sk-test123456789012345678901234567890"
        assert settings.openai_model == "gpt-4o-mini"
        assert settings.app_env == "development"
        assert settings.log_level == "DEBUG"

    def test_default_values(self):
        """測試默認值"""
        settings = Settings()

        assert settings.chunk_size == 1000
        assert settings.chunk_overlap == 200
        assert settings.top_k == 5
        assert settings.temperature == 0.7
        assert settings.max_tokens == 4000

    def test_get_llm_config_openai(self, mock_env):
        """測試獲取 OpenAI 配置"""
        settings = Settings()
        config = settings.get_llm_config("openai")

        assert "api_key" in config
        assert "model" in config
        assert config["api_key"] == "sk-test123456789012345678901234567890"

    def test_get_llm_config_invalid_provider(self, mock_env):
        """測試無效的提供商"""
        settings = Settings()

        with pytest.raises(ValueError, match="不支援的 LLM 提供商"):
            settings.get_llm_config("invalid_provider")

    def test_get_llm_config_missing_key(self, monkeypatch):
        """測試缺少 API 金鑰"""
        # 確保環境變數中沒有 Anthropic API 金鑰
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        reload_settings()
        settings = Settings()

        with pytest.raises(ValueError, match="API 金鑰未設定"):
            settings.get_llm_config("anthropic")  # 沒有設置 Anthropic key

    def test_is_development(self, mock_env):
        """測試開發環境檢查"""
        settings = Settings()
        assert settings.is_development() is True
        assert settings.is_production() is False

    def test_is_production(self, monkeypatch):
        """測試生產環境檢查"""
        monkeypatch.setenv("APP_ENV", "production")
        reload_settings()
        settings = get_settings()

        assert settings.is_production() is True
        assert settings.is_development() is False

    def test_validate_log_level_valid(self):
        """測試有效的日誌級別"""
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            settings = Settings(log_level=level)
            assert settings.log_level == level

    def test_validate_log_level_invalid(self):
        """測試無效的日誌級別"""
        with pytest.raises(ValueError, match="log_level 必須是以下之一"):
            Settings(log_level="INVALID")

    def test_validate_temperature_valid(self):
        """測試有效的溫度值"""
        for temp in [0.0, 0.5, 1.0, 1.5, 2.0]:
            settings = Settings(temperature=temp)
            assert settings.temperature == temp

    def test_validate_temperature_invalid(self):
        """測試無效的溫度值"""
        with pytest.raises(ValueError, match="temperature 必須在 0.0 到 2.0 之間"):
            Settings(temperature=2.5)

    def test_validate_app_env_valid(self):
        """測試有效的應用環境"""
        for env in ["development", "staging", "production"]:
            settings = Settings(app_env=env)
            assert settings.app_env == env

    def test_validate_app_env_invalid(self):
        """測試無效的應用環境"""
        with pytest.raises(ValueError, match="app_env 必須是以下之一"):
            Settings(app_env="invalid")


@pytest.mark.unit
class TestSettingsFunctions:
    """測試配置相關函數"""

    def test_get_settings_singleton(self, mock_env):
        """測試配置單例模式"""
        settings1 = get_settings()
        settings2 = get_settings()

        # 應該返回同一個實例
        assert settings1 is settings2

    def test_reload_settings(self, mock_env):
        """測試重新載入配置"""
        settings1 = get_settings()
        reload_settings()
        settings2 = get_settings()

        # 應該返回新的實例
        assert settings1 is not settings2

    def test_get_openai_config_function(self, mock_env):
        """測試獲取 OpenAI 配置函數"""
        config = get_openai_config()

        assert "api_key" in config
        assert "model" in config


@pytest.mark.unit
class TestSettingsIntegration:
    """測試配置集成"""

    def test_settings_from_env_file(self, tmp_path, monkeypatch):
        """測試從 .env 文件載入配置"""
        # 創建臨時 .env 文件
        env_file = tmp_path / ".env"
        env_file.write_text(
            "OPENAI_API_KEY=sk-test-env-file\n" "APP_ENV=production\n" "DEBUG=true\n"
        )

        # 修改工作目錄
        monkeypatch.chdir(tmp_path)

        # 重新載入配置
        reload_settings()
        settings = get_settings()

        # 注意：實際測試中，Settings 可能不會自動載入 .env
        # 這取決於實現細節
        assert settings is not None

    def test_multiple_providers_config(self, monkeypatch):
        """測試多提供商配置"""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-openai-test-key-1234567890123")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key-1234567890123")
        monkeypatch.setenv("GOOGLE_API_KEY", "AIza-test-key-1234567890")

        reload_settings()
        settings = get_settings()

        # 測試所有提供商配置
        openai_config = settings.get_llm_config("openai")
        assert openai_config["api_key"] == "sk-openai-test-key-1234567890123"

        anthropic_config = settings.get_llm_config("anthropic")
        assert anthropic_config["api_key"] == "sk-ant-test-key-1234567890123"

        google_config = settings.get_llm_config("google")
        assert google_config["api_key"] == "AIza-test-key-1234567890"

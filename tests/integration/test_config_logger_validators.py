"""
整合測試 - Config + Logger + Validators 協同工作

測試配置管理、日誌系統和驗證器之間的整合。
"""

import logging
import pytest
from pathlib import Path

from llm_agent_demo.utils.config import get_settings, reload_settings
from llm_agent_demo.utils.logger import (
    setup_logging,
    get_logger,
    log_execution_time,
    StructuredLogger,
)
from llm_agent_demo.utils.validators import (
    validate_openai_api_key,
    validate_anthropic_api_key,
    validate_model_name,
    validate_temperature,
    validate_max_tokens,
    validate_user_query,
    sanitize_user_input,
)
from llm_agent_demo.utils.exceptions import (
    APIKeyError,
    ValidationError,
    ConfigurationError,
)


@pytest.mark.integration
class TestConfigLoggerValidatorsIntegration:
    """測試 Config、Logger 和 Validators 的整合"""

    def test_config_loading_with_logging(self, integration_env, reset_logging, temp_log_file):
        """測試配置載入時的日誌記錄"""
        # 設置日誌
        setup_logging(
            level="DEBUG",
            log_file=str(temp_log_file),
            force_reconfigure=True
        )
        logger = get_logger(__name__)

        # 載入配置
        logger.info("開始載入配置")
        settings = reload_settings()

        # 驗證配置已載入
        assert settings is not None
        logger.info(f"配置載入完成: app_env={settings.app_env}")

        # 檢查日誌文件是否記錄了這些操作
        log_content = temp_log_file.read_text()
        assert "開始載入配置" in log_content
        assert "配置載入完成" in log_content

    def test_validator_integration_with_config(self, config_with_validators):
        """測試驗證器與配置的整合"""
        settings = config_with_validators

        # 驗證 OpenAI API 密鑰
        validated_key = validate_openai_api_key(settings.openai_api_key)
        assert validated_key == settings.openai_api_key

        # 驗證 Anthropic API 密鑰
        validated_key = validate_anthropic_api_key(settings.anthropic_api_key)
        assert validated_key == settings.anthropic_api_key

        # 驗證溫度參數
        validated_temp = validate_temperature(settings.temperature)
        assert validated_temp == settings.temperature

        # 驗證最大 tokens
        validated_tokens = validate_max_tokens(settings.max_tokens)
        assert validated_tokens == settings.max_tokens

    def test_config_validation_with_logging(
        self, integration_env, reset_logging, temp_log_file
    ):
        """測試配置驗證過程中的日誌記錄"""
        # 設置日誌
        setup_logging(
            level="INFO",
            log_file=str(temp_log_file),
            force_reconfigure=True
        )
        logger = get_logger(__name__)

        # 載入配置
        settings = reload_settings()

        # 驗證並記錄每個 API 密鑰
        for provider in ["openai", "anthropic", "google", "groq"]:
            try:
                config = settings.get_llm_config(provider)
                logger.info(f"成功獲取 {provider.upper()} 配置")
                assert config["api_key"] is not None
            except (APIKeyError, ConfigurationError) as e:
                logger.error(f"獲取 {provider.upper()} 配置失敗: {e}")
                raise

        # 檢查日誌
        log_content = temp_log_file.read_text()
        assert "成功獲取 OPENAI 配置" in log_content

    def test_invalid_config_handling_with_logging(
        self, monkeypatch, reset_logging, temp_log_file
    ):
        """測試無效配置的處理和日誌記錄"""
        # 設置日誌
        setup_logging(
            level="ERROR",
            log_file=str(temp_log_file),
            force_reconfigure=True
        )
        logger = get_logger(__name__)

        # 清除配置快取
        get_settings.cache_clear()

        # 設置無效的 log_level
        monkeypatch.setenv("LOG_LEVEL", "INVALID_LEVEL")

        # 嘗試載入配置
        try:
            from llm_agent_demo.utils.config import Settings
            settings = Settings()
            pytest.fail("應該拋出 ValidationError")
        except Exception as e:
            logger.error(f"配置驗證失敗: {e}")
            # 檢查是否是預期的錯誤
            assert "log_level" in str(e).lower()

        # 清理
        get_settings.cache_clear()

    def test_structured_logging_with_validated_data(
        self, config_with_validators, reset_logging, temp_log_file
    ):
        """測試結構化日誌記錄驗證後的數據"""
        # 設置 JSON 格式日誌
        setup_logging(
            level="INFO",
            log_file=str(temp_log_file),
            json_format=True,
            force_reconfigure=True
        )

        # 創建結構化日誌記錄器
        structured_logger = StructuredLogger(__name__)

        # 記錄配置驗證事件
        settings = config_with_validators

        structured_logger.log_event(
            "config_validated",
            level="INFO",
            message="配置驗證成功",
            app_env=settings.app_env,
            log_level=settings.log_level,
            max_retries=settings.max_retries,
        )

        # 驗證並記錄模型配置
        openai_config = settings.get_llm_config("openai")
        validated_model = validate_model_name(
            openai_config["model"],
            valid_models=["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]
        )

        structured_logger.log_event(
            "model_validated",
            level="INFO",
            model=validated_model,
            provider="openai",
        )

        # 檢查日誌文件包含 JSON 格式的記錄
        log_content = temp_log_file.read_text()
        assert "config_validated" in log_content
        assert "model_validated" in log_content
        assert settings.app_env in log_content

    def test_input_sanitization_with_logging(
        self, reset_logging, temp_log_file
    ):
        """測試輸入清理與日誌記錄"""
        # 設置日誌
        setup_logging(
            level="WARNING",
            log_file=str(temp_log_file),
            force_reconfigure=True
        )
        logger = get_logger(__name__)

        # 測試安全的輸入
        safe_input = "這是一個安全的查詢"
        validated = validate_user_query(safe_input)
        assert validated == safe_input

        # 測試可疑的輸入
        suspicious_input = "<script>alert('xss')</script>"
        try:
            validate_user_query(suspicious_input, check_suspicious=True)
            pytest.fail("應該拋出 ValidationError")
        except ValidationError as e:
            logger.warning(f"檢測到可疑輸入: {e}")
            assert "可疑" in str(e)

        # 檢查日誌記錄了警告
        log_content = temp_log_file.read_text()
        assert "可疑" in log_content

    def test_log_execution_time_with_validation(
        self, reset_logging, temp_log_file
    ):
        """測試執行時間記錄與數據驗證"""
        # 設置日誌
        setup_logging(
            level="INFO",
            log_file=str(temp_log_file),
            force_reconfigure=True
        )
        logger = get_logger(__name__)

        # 使用日誌上下文管理器執行驗證操作
        with log_execution_time(logger, "API密鑰批量驗證"):
            test_keys = [
                "sk-test-key-" + "a" * 30,
                "sk-ant-test-key-" + "b" * 30,
            ]

            # 驗證第一個密鑰
            validated1 = validate_openai_api_key(test_keys[0])
            assert validated1 == test_keys[0]

            # 驗證第二個密鑰
            validated2 = validate_anthropic_api_key(test_keys[1])
            assert validated2 == test_keys[1]

        # 檢查日誌記錄了執行時間
        log_content = temp_log_file.read_text()
        assert "開始執行: API密鑰批量驗證" in log_content
        assert "執行完成: API密鑰批量驗證" in log_content
        assert "耗時" in log_content

    def test_config_reload_with_validation_logging(
        self, monkeypatch, reset_logging, temp_log_file
    ):
        """測試配置重載時的驗證和日誌記錄"""
        # 設置日誌
        setup_logging(
            level="DEBUG",
            log_file=str(temp_log_file),
            force_reconfigure=True
        )
        logger = get_logger(__name__)

        # 第一次載入配置
        logger.info("首次載入配置")
        get_settings.cache_clear()
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-first-" + "a" * 30)
        settings1 = get_settings()
        key1 = settings1.openai_api_key

        # 重新載入配置
        logger.info("重新載入配置")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-second-" + "b" * 30)
        settings2 = reload_settings()
        key2 = settings2.openai_api_key

        # 驗證配置已更新
        assert key1 != key2
        logger.info(f"配置已更新: {key1[:15]}... -> {key2[:15]}...")

        # 驗證新的 API 密鑰
        validated_key = validate_openai_api_key(key2)
        assert validated_key == key2

        # 檢查日誌
        log_content = temp_log_file.read_text()
        assert "首次載入配置" in log_content
        assert "重新載入配置" in log_content
        assert "配置已更新" in log_content


@pytest.mark.integration
class TestConfigValidationErrorHandling:
    """測試配置驗證錯誤處理"""

    def test_invalid_temperature_with_logging(
        self, integration_env, reset_logging, temp_log_file
    ):
        """測試無效溫度參數的處理"""
        # 設置日誌
        setup_logging(
            level="ERROR",
            log_file=str(temp_log_file),
            force_reconfigure=True
        )
        logger = get_logger(__name__)

        # 測試無效的溫度值
        invalid_temps = [-0.1, 2.5, 10.0]

        for temp in invalid_temps:
            try:
                validate_temperature(temp)
                pytest.fail(f"應該拋出 ValidationError for temperature={temp}")
            except ValidationError as e:
                logger.error(f"溫度驗證失敗: {temp}, 錯誤: {e}")
                assert "溫度" in str(e)

        # 檢查日誌記錄了所有錯誤
        log_content = temp_log_file.read_text()
        assert log_content.count("溫度驗證失敗") == len(invalid_temps)

    def test_invalid_api_key_format_with_logging(
        self, reset_logging, temp_log_file
    ):
        """測試無效 API 密鑰格式的處理"""
        # 設置日誌
        setup_logging(
            level="ERROR",
            log_file=str(temp_log_file),
            force_reconfigure=True
        )
        logger = get_logger(__name__)

        # 測試各種無效的 API 密鑰
        invalid_keys = [
            ("", "空字符串"),
            ("   ", "空白字符"),
            ("short", "長度過短"),
            ("wrong-prefix-" + "a" * 30, "錯誤前綴"),
            ("sk-test-key with spaces", "包含空格"),
        ]

        for key, description in invalid_keys:
            try:
                validate_openai_api_key(key)
                pytest.fail(f"應該拋出 APIKeyError for {description}")
            except APIKeyError as e:
                logger.error(f"API密鑰驗證失敗 ({description}): {e}")

        # 檢查日誌
        log_content = temp_log_file.read_text()
        assert "API密鑰驗證失敗" in log_content

    def test_missing_api_key_with_config_and_logging(
        self, monkeypatch, reset_logging, temp_log_file
    ):
        """測試缺失 API 密鑰時的配置和日誌處理"""
        # 設置日誌
        setup_logging(
            level="ERROR",
            log_file=str(temp_log_file),
            force_reconfigure=True
        )
        logger = get_logger(__name__)

        # 清除配置快取
        get_settings.cache_clear()

        # 清除 API 密鑰環境變數
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        # 載入配置
        settings = get_settings()

        # 嘗試獲取 OpenAI 配置（應該失敗）
        try:
            settings.get_llm_config("openai")
            pytest.fail("應該拋出 APIKeyError")
        except APIKeyError as e:
            logger.error(f"獲取配置失敗: {e}")
            assert "OpenAI" in str(e)
            assert "未設定" in str(e)

        # 檢查日誌
        log_content = temp_log_file.read_text()
        assert "獲取配置失敗" in log_content

        # 清理
        get_settings.cache_clear()


@pytest.mark.integration
class TestInputSanitizationIntegration:
    """測試輸入清理整合"""

    def test_user_query_sanitization_workflow(
        self, reset_logging, temp_log_file
    ):
        """測試用戶查詢清理的完整工作流程"""
        # 設置日誌
        setup_logging(
            level="INFO",
            log_file=str(temp_log_file),
            enable_filter=True,  # 啟用敏感信息過濾
            force_reconfigure=True
        )
        logger = get_logger(__name__)

        # 測試用例
        test_cases = [
            ("正常的查詢文本", True, "正常查詢"),
            ("包含<b>HTML</b>標籤的文本", True, "HTML標籤"),
            ("<script>alert('xss')</script>", False, "XSS攻擊"),
            ("SELECT * FROM users; DROP TABLE users;--", False, "SQL注入"),
        ]

        for query, should_pass, description in test_cases:
            logger.info(f"測試 {description}: {query[:50]}...")

            if should_pass:
                # 清理輸入
                sanitized = sanitize_user_input(query, strip_html=True)
                assert sanitized is not None
                logger.info(f"{description} 清理成功")

                # 驗證查詢（不檢查可疑模式以允許 HTML）
                try:
                    validated = validate_user_query(sanitized, check_suspicious=False)
                    assert validated is not None
                except ValidationError as e:
                    logger.warning(f"{description} 驗證警告: {e}")
            else:
                # 應該被檢測為可疑輸入
                try:
                    validate_user_query(query, check_suspicious=True)
                    pytest.fail(f"{description} 應該被檢測為可疑輸入")
                except ValidationError as e:
                    logger.warning(f"{description} 被正確攔截: {e}")

        # 檢查日誌
        log_content = temp_log_file.read_text()
        assert "清理成功" in log_content
        assert "被正確攔截" in log_content

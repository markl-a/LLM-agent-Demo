"""
整合測試專用 fixtures

提供整合測試所需的 fixtures，用於測試多個模組之間的協同工作。
"""

import os
import tempfile
from pathlib import Path
from typing import Dict

import pytest


@pytest.fixture
def integration_env(monkeypatch):
    """
    設置整合測試環境變數

    提供完整的測試環境配置，包括所有必要的 API 密鑰和配置參數。
    """
    # 清除現有的配置快取
    from llm_agent_demo.utils.config import get_settings
    get_settings.cache_clear()

    # 設置測試 API 密鑰
    test_keys = {
        "OPENAI_API_KEY": "sk-test-openai-key-1234567890abcdefghijklmnop",
        "ANTHROPIC_API_KEY": "sk-ant-test-anthropic-key-1234567890abcdefghijklmnop",
        "GOOGLE_API_KEY": "test-google-key-1234567890abcdefghijklmnop",
        "GROQ_API_KEY": "gsk-test-groq-key-1234567890abcdefghijklmnop",
    }

    for key, value in test_keys.items():
        monkeypatch.setenv(key, value)

    # 設置應用配置
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("ENABLE_COST_TRACKING", "true")
    monkeypatch.setenv("MAX_RETRIES", "3")
    monkeypatch.setenv("TIMEOUT", "30")

    yield test_keys

    # 清理
    get_settings.cache_clear()


@pytest.fixture
def temp_log_file():
    """
    創建臨時日誌文件

    Returns:
        Path: 臨時日誌文件路徑
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
        log_path = Path(f.name)

    yield log_path

    # 清理
    if log_path.exists():
        log_path.unlink()


@pytest.fixture
def temp_cost_tracker_file():
    """
    創建臨時成本追蹤文件

    Returns:
        Path: 臨時成本追蹤文件路徑
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        tracker_path = Path(f.name)

    yield tracker_path

    # 清理
    if tracker_path.exists():
        tracker_path.unlink()


@pytest.fixture
def temp_config_dir():
    """
    創建臨時配置目錄

    Returns:
        Path: 臨時配置目錄路徑
    """
    temp_dir = Path(tempfile.mkdtemp())

    yield temp_dir

    # 清理
    import shutil
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


@pytest.fixture
def sample_env_file(temp_config_dir):
    """
    創建示例 .env 文件

    Args:
        temp_config_dir: 臨時配置目錄

    Returns:
        Path: .env 文件路徑
    """
    env_file = temp_config_dir / ".env"

    env_content = """
# LLM API 配置
OPENAI_API_KEY=sk-test-openai-key-from-env-file
ANTHROPIC_API_KEY=sk-ant-test-anthropic-key-from-env-file
GOOGLE_API_KEY=test-google-key-from-env-file

# 應用配置
APP_ENV=production
LOG_LEVEL=INFO
DEBUG=false
MAX_RETRIES=5
TIMEOUT=60

# RAG 配置
CHUNK_SIZE=1500
CHUNK_OVERLAP=300
TOP_K=10

# 成本追蹤
ENABLE_COST_TRACKING=true
"""

    env_file.write_text(env_content.strip())

    yield env_file

    # 清理由 fixture 自動處理


@pytest.fixture
def mock_api_responses():
    """
    模擬 API 響應數據

    Returns:
        Dict: 包含各種模擬 API 響應的字典
    """
    return {
        "success_response": {
            "id": "chatcmpl-123",
            "object": "chat.completion",
            "created": 1677652288,
            "model": "gpt-4o-mini",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Hello! How can I help you today?"
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 9,
                "total_tokens": 19
            }
        },
        "rate_limit_response": {
            "error": {
                "message": "Rate limit exceeded",
                "type": "rate_limit_error",
                "code": "rate_limit_exceeded"
            }
        },
        "network_error": "Connection timeout"
    }


@pytest.fixture
def reset_logging():
    """
    重置日誌系統

    確保每個測試開始前日誌系統處於乾淨狀態。
    """
    import logging

    # 保存當前狀態
    root_logger = logging.getLogger()
    original_level = root_logger.level
    original_handlers = root_logger.handlers.copy()

    # 清除所有 handlers
    root_logger.handlers.clear()

    yield

    # 恢復原始狀態
    root_logger.setLevel(original_level)
    root_logger.handlers.clear()
    for handler in original_handlers:
        root_logger.addHandler(handler)


@pytest.fixture
def config_with_validators(integration_env):
    """
    提供已驗證的配置對象

    Returns:
        Settings: 配置對象
    """
    from llm_agent_demo.utils.config import get_settings, reload_settings
    from llm_agent_demo.utils.validators import validate_openai_api_key

    # 重新載入配置
    settings = reload_settings()

    # 驗證關鍵 API 密鑰
    validate_openai_api_key(settings.openai_api_key)

    return settings


@pytest.fixture
def logger_with_config(reset_logging, temp_log_file):
    """
    提供已配置的日誌記錄器

    Args:
        reset_logging: 重置日誌系統
        temp_log_file: 臨時日誌文件

    Returns:
        Logger: 配置好的日誌記錄器
    """
    from llm_agent_demo.utils.logger import setup_logging, get_logger

    setup_logging(
        level="DEBUG",
        log_file=str(temp_log_file),
        colorize=True,
        force_reconfigure=True
    )

    return get_logger(__name__)


@pytest.fixture
def cost_tracker_with_file(temp_cost_tracker_file):
    """
    提供帶持久化的成本追蹤器

    Args:
        temp_cost_tracker_file: 臨時成本追蹤文件

    Returns:
        CostTracker: 成本追蹤器實例
    """
    from llm_agent_demo.utils.cost_tracker import CostTracker

    tracker = CostTracker(
        save_path=str(temp_cost_tracker_file),
        auto_save_interval=5
    )

    return tracker

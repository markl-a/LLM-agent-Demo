"""
Pytest 配置文件

提供測試夾具 (fixtures) 和共享的測試工具。
"""

import os
import sys
from pathlib import Path

import pytest

# 將專案根目錄添加到 Python 路徑
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))


@pytest.fixture
def project_root():
    """返回專案根目錄路徑"""
    return ROOT_DIR


@pytest.fixture
def sample_data_dir(project_root):
    """返回測試數據目錄路徑"""
    return project_root / "tests" / "data"


@pytest.fixture
def mock_api_key():
    """提供模擬的 API Key"""
    return "sk-test-mock-api-key-12345"


@pytest.fixture(autouse=True)
def env_setup(monkeypatch, mock_api_key):
    """
    自動設置測試環境變數

    這個 fixture 會在每個測試前自動執行，設置必要的環境變數。
    """
    # 設置模擬的 API Keys
    monkeypatch.setenv("OPENAI_API_KEY", mock_api_key)
    monkeypatch.setenv("GOOGLE_API_KEY", mock_api_key)
    monkeypatch.setenv("ANTHROPIC_API_KEY", mock_api_key)
    monkeypatch.setenv("GROQ_API_KEY", mock_api_key)

    # 設置測試模式標誌
    monkeypatch.setenv("TESTING", "true")

    yield

    # 測試後的清理（如果需要的話）


@pytest.fixture
def skip_if_no_api_key():
    """如果沒有真實 API Key，則跳過測試"""
    real_api_key = os.getenv("OPENAI_API_KEY", "")
    if not real_api_key or real_api_key.startswith("sk-test"):
        pytest.skip("需要真實的 API Key 才能運行此測試")


# 自定義 Pytest 鉤子
def pytest_configure(config):
    """Pytest 配置鉤子"""
    config.addinivalue_line(
        "markers", "unit: 標記為單元測試"
    )
    config.addinivalue_line(
        "markers", "integration: 標記為整合測試"
    )
    config.addinivalue_line(
        "markers", "slow: 標記為慢速測試"
    )
    config.addinivalue_line(
        "markers", "requires_api_key: 標記為需要 API Key 的測試"
    )

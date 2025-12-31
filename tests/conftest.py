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


@pytest.fixture
def test_dirs(project_root):
    """返回測試相關目錄路徑"""
    return {
        'root': project_root,
        'tests': project_root / 'tests',
        'src': project_root / 'src',
        'examples': project_root / 'examples',
        'logs': project_root / 'logs',
    }


@pytest.fixture
def temp_log_file(tmp_path):
    """創建臨時日誌文件"""
    log_file = tmp_path / "test.log"
    yield log_file
    # 清理：測試後刪除日誌文件
    if log_file.exists():
        log_file.unlink()


@pytest.fixture
def framework_dirs(project_root):
    """返回所有框架目錄列表"""
    import re
    framework_dirs = []
    for item in project_root.iterdir():
        if item.is_dir() and re.match(r'^\d+\.', item.name):
            framework_dirs.append(item)
    return sorted(framework_dirs, key=lambda x: x.name)


@pytest.fixture
def example_files(project_root):
    """返回所有示例 Python 文件"""
    examples_dir = project_root / 'examples'
    if not examples_dir.exists():
        return []
    return list(examples_dir.glob('**/*.py'))


@pytest.fixture(scope='session')
def session_temp_dir(tmp_path_factory):
    """創建會話級別的臨時目錄"""
    return tmp_path_factory.mktemp('session')


@pytest.fixture
def clean_environment(monkeypatch):
    """提供乾淨的環境變數（清除所有 API keys）"""
    # 清除常見的 API key 環境變數
    api_key_vars = [
        'OPENAI_API_KEY',
        'GOOGLE_API_KEY',
        'ANTHROPIC_API_KEY',
        'GROQ_API_KEY',
        'AZURE_OPENAI_API_KEY',
        'HUGGINGFACE_API_KEY',
    ]
    for var in api_key_vars:
        monkeypatch.delenv(var, raising=False)
    yield


@pytest.fixture
def captured_logs(caplog):
    """捕獲日誌輸出的 fixture"""
    import logging
    caplog.set_level(logging.DEBUG)
    return caplog


@pytest.fixture(autouse=True)
def ensure_log_dir(project_root):
    """確保日誌目錄存在"""
    log_dir = project_root / 'logs'
    log_dir.mkdir(exist_ok=True)
    yield log_dir


@pytest.fixture
def mock_framework_file(tmp_path):
    """創建模擬的框架文件用於測試"""
    def _create_mock_file(filename: str, content: str = "# Mock file\nprint('Hello')"):
        file_path = tmp_path / filename
        file_path.write_text(content, encoding='utf-8')
        return file_path
    return _create_mock_file


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

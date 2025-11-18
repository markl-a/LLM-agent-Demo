"""
基礎測試範例

這些測試展示如何編寫簡單的測試案例。
"""

import os
from pathlib import Path

import pytest


@pytest.mark.unit
def test_python_version():
    """測試 Python 版本符合要求"""
    import sys

    assert sys.version_info >= (3, 9), "需要 Python 3.9 或更高版本"


@pytest.mark.unit
def test_project_root_exists(project_root):
    """測試專案根目錄存在"""
    assert project_root.exists(), "專案根目錄應該存在"
    assert project_root.is_dir(), "專案根目錄應該是一個目錄"


@pytest.mark.unit
def test_readme_exists(project_root):
    """測試 README.md 文件存在"""
    readme = project_root / "README.md"
    assert readme.exists(), "README.md 應該存在"
    assert readme.is_file(), "README.md 應該是一個文件"


@pytest.mark.unit
def test_requirements_file_exists(project_root):
    """測試 requirements.txt 文件存在"""
    requirements = project_root / "requirements.txt"
    assert requirements.exists(), "requirements.txt 應該存在"


@pytest.mark.unit
def test_dockerfile_exists(project_root):
    """測試 Dockerfile 存在"""
    dockerfile = project_root / "Dockerfile"
    assert dockerfile.exists(), "Dockerfile 應該存在"


@pytest.mark.unit
def test_docker_compose_exists(project_root):
    """測試 docker-compose.yml 存在"""
    docker_compose = project_root / "docker-compose.yml"
    assert docker_compose.exists(), "docker-compose.yml 應該存在"


@pytest.mark.unit
def test_env_example_exists(project_root):
    """測試 .env.example 文件存在"""
    env_example = project_root / ".env.example"
    assert env_example.exists(), ".env.example 應該存在"


@pytest.mark.unit
def test_gitignore_exists(project_root):
    """測試 .gitignore 文件存在"""
    gitignore = project_root / ".gitignore"
    assert gitignore.exists(), ".gitignore 應該存在"


@pytest.mark.unit
def test_pyproject_toml_exists(project_root):
    """測試 pyproject.toml 文件存在"""
    pyproject = project_root / "pyproject.toml"
    assert pyproject.exists(), "pyproject.toml 應該存在"


@pytest.mark.unit
def test_main_directories_exist(project_root):
    """測試主要目錄存在"""
    expected_dirs = [
        "1.LangchainDemos",
        "2.Multi_modal_RAG",
        "3.程式碼解析",
        "6.LlamaIndex",
        "7.AutoGen",
        "8.CrewAI",
        "9.MetaGPT",
        "tests",
    ]

    for dir_name in expected_dirs:
        dir_path = project_root / dir_name
        assert dir_path.exists(), f"{dir_name} 目錄應該存在"
        assert dir_path.is_dir(), f"{dir_name} 應該是一個目錄"


@pytest.mark.unit
def test_mock_api_key_fixture(mock_api_key):
    """測試 mock_api_key fixture 正常工作"""
    assert mock_api_key is not None
    assert isinstance(mock_api_key, str)
    assert len(mock_api_key) > 0


@pytest.mark.unit
def test_env_setup_fixture():
    """測試環境變數設置 fixture 正常工作"""
    assert os.getenv("TESTING") == "true"
    assert os.getenv("OPENAI_API_KEY") is not None


@pytest.mark.unit
@pytest.mark.parametrize(
    "input_text,expected_length",
    [
        ("hello", 5),
        ("world", 5),
        ("", 0),
        ("LLM Agent Demo", 14),
    ],
)
def test_string_length(input_text, expected_length):
    """測試字串長度計算（參數化測試範例）"""
    assert len(input_text) == expected_length


@pytest.mark.unit
def test_import_core_libraries():
    """測試核心庫可以正常導入"""
    try:
        import langchain  # noqa: F401
        import pytest  # noqa: F401

        # 如果成功導入，測試通過
        assert True
    except ImportError as e:
        pytest.fail(f"無法導入核心庫: {e}")


@pytest.mark.unit
def test_path_operations():
    """測試路徑操作工具函數"""
    test_path = Path("/tmp/test")
    assert isinstance(test_path, Path)
    assert str(test_path) == "/tmp/test"

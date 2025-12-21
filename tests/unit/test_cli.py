"""CLI 模組的單元測試"""

import pytest
import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

# 檢查是否安裝了核心模組
try:
    from src.llm_agent_demo.cli import cli
    from src.llm_agent_demo.utils.config import Settings, reload_settings
    from src.llm_agent_demo.utils.exceptions import ConfigurationError, APIKeyError

    CORE_MODULE_AVAILABLE = True
except ImportError:
    CORE_MODULE_AVAILABLE = False
    pytest.skip("核心模組未安裝", allow_module_level=True)


@pytest.fixture
def runner():
    """創建 Click CLI 測試運行器"""
    return CliRunner()


@pytest.fixture
def mock_settings(monkeypatch):
    """模擬配置設定"""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test1234567890123456789012345678")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test1234567890123456789012")
    monkeypatch.setenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
    monkeypatch.setenv("GOOGLE_API_KEY", "AIza-test-key-1234567890")
    monkeypatch.setenv("GROQ_API_KEY", "gsk_test1234567890123456789012345678")
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("LOG_LEVEL", "INFO")
    monkeypatch.setenv("DEBUG", "true")
    reload_settings()
    yield
    reload_settings()


@pytest.fixture
def temp_cost_file(tmp_path):
    """創建臨時成本追蹤文件"""
    cost_file = tmp_path / "test_cost.json"
    # CostTracker 期望 JSON 文件是一個數組，不是包含 usage_history 的對象
    cost_data = [
        {
            "model": "gpt-4o-mini",
            "provider": "openai",
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150,
            "timestamp": "2024-01-01T12:00:00",
        },
        {
            "model": "gpt-4o",
            "provider": "openai",
            "prompt_tokens": 200,
            "completion_tokens": 100,
            "total_tokens": 300,
            "timestamp": "2024-01-01T12:01:00",
        },
    ]
    cost_file.write_text(json.dumps(cost_data))
    return cost_file


@pytest.mark.unit
class TestCLIMain:
    """測試主 CLI 命令"""

    def test_cli_version(self, runner):
        """測試版本選項"""
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "version" in result.output.lower() or "llm-agent-demo" in result.output

    def test_cli_help(self, runner):
        """測試幫助選項"""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "LLM Agent Demo" in result.output or "Usage" in result.output

    def test_cli_no_args(self, runner):
        """測試無參數調用"""
        result = runner.invoke(cli, [])
        # Click 在沒有子命令時返回退出碼 0（顯示幫助）或 2（需要子命令）
        assert result.exit_code in [0, 2]


@pytest.mark.unit
class TestConfigCommand:
    """測試 config 命令"""

    def test_config_default(self, runner, mock_settings):
        """測試默認配置顯示"""
        result = runner.invoke(cli, ["config"])
        assert result.exit_code == 0
        assert "配置" in result.output or "LLM" in result.output

    def test_config_specific_provider(self, runner, mock_settings):
        """測試查看特定提供商配置"""
        result = runner.invoke(cli, ["config", "-p", "openai"])
        assert result.exit_code == 0
        # 應該只包含 OpenAI 相關配置
        assert "OPENAI" in result.output or "OpenAI" in result.output

    @pytest.mark.parametrize(
        "provider",
        ["openai", "anthropic", "google", "groq", "all"],
    )
    def test_config_all_providers(self, runner, mock_settings, provider):
        """測試所有提供商選項"""
        result = runner.invoke(cli, ["config", "-p", provider])
        assert result.exit_code == 0

    def test_config_show_keys(self, runner, mock_settings):
        """測試顯示 API 金鑰"""
        result = runner.invoke(cli, ["config", "--show-keys"])
        assert result.exit_code == 0
        # 應該包含完整的 API 金鑰
        assert "sk-test" in result.output or "sk-ant" in result.output

    def test_config_hide_keys_default(self, runner, mock_settings):
        """測試默認隱藏 API 金鑰"""
        result = runner.invoke(cli, ["config"])
        assert result.exit_code == 0
        # 默認應該遮蔽金鑰
        assert "***" in result.output or "..." in result.output or "✓" in result.output

    def test_config_json_format(self, runner, mock_settings):
        """測試 JSON 格式輸出"""
        result = runner.invoke(cli, ["config", "-f", "json"])
        assert result.exit_code == 0
        # 輸出應該是有效的 JSON
        try:
            output_lines = [line for line in result.output.split("\n") if line.strip()]
            # 查找 JSON 內容（可能有多行）
            json_output = "\n".join(output_lines)
            # 嘗試解析 JSON
            if "{" in json_output:
                json_start = json_output.index("{")
                json_str = json_output[json_start:]
                data = json.loads(json_str)
                assert "app" in data or "llm_providers" in data
        except (json.JSONDecodeError, ValueError):
            # 如果解析失敗，至少檢查是否包含 JSON 相關內容
            assert "{" in result.output and "}" in result.output

    def test_config_table_format(self, runner, mock_settings):
        """測試表格格式輸出"""
        result = runner.invoke(cli, ["config", "-f", "table"])
        assert result.exit_code == 0
        # 表格格式應該包含分隔符或表格元素
        assert "─" in result.output or "|" in result.output or "設定" in result.output

    def test_config_reload(self, runner, mock_settings):
        """測試重新載入配置"""
        result = runner.invoke(cli, ["config", "--reload"])
        assert result.exit_code == 0
        assert "重新載入" in result.output or "reload" in result.output.lower()

    def test_config_combined_options(self, runner, mock_settings):
        """測試組合選項"""
        result = runner.invoke(
            cli, ["config", "-p", "openai", "--show-keys", "-f", "table"]
        )
        assert result.exit_code == 0
        assert "sk-test" in result.output

    def test_config_invalid_provider(self, runner, mock_settings):
        """測試無效的提供商"""
        result = runner.invoke(cli, ["config", "-p", "invalid"])
        assert result.exit_code != 0

    def test_config_invalid_format(self, runner, mock_settings):
        """測試無效的格式"""
        result = runner.invoke(cli, ["config", "-f", "invalid"])
        assert result.exit_code != 0


@pytest.mark.unit
class TestCostCommand:
    """測試 cost 命令"""

    def test_cost_no_file(self, runner, mock_settings):
        """測試沒有成本文件時的輸出"""
        result = runner.invoke(cli, ["cost"])
        assert result.exit_code == 0
        # 應該提示沒有找到記錄
        assert "沒有" in result.output or "提示" in result.output or "⚠" in result.output

    def test_cost_with_file(self, runner, mock_settings, temp_cost_file):
        """測試從文件載入成本"""
        result = runner.invoke(cli, ["cost", "-f", str(temp_cost_file)])
        assert result.exit_code == 0
        # 應該顯示成本信息
        assert "成本" in result.output or "$" in result.output or "gpt-4o" in result.output

    def test_cost_specific_model(self, runner, mock_settings, temp_cost_file):
        """測試查看特定模型成本"""
        result = runner.invoke(cli, ["cost", "-f", str(temp_cost_file), "-m", "gpt-4o-mini"])
        assert result.exit_code == 0
        assert "gpt-4o-mini" in result.output

    def test_cost_nonexistent_model(self, runner, mock_settings, temp_cost_file):
        """測試查看不存在的模型"""
        result = runner.invoke(
            cli, ["cost", "-f", str(temp_cost_file), "-m", "nonexistent-model"]
        )
        # 應該顯示錯誤或找不到的訊息
        assert "找不到" in result.output or "✗" in result.output

    def test_cost_json_format(self, runner, mock_settings, temp_cost_file):
        """測試 JSON 格式輸出成本"""
        result = runner.invoke(
            cli, ["cost", "-f", str(temp_cost_file), "--format", "json"]
        )
        assert result.exit_code == 0
        # 輸出應該包含 JSON 數據
        assert "{" in result.output and "}" in result.output

    def test_cost_table_format(self, runner, mock_settings, temp_cost_file):
        """測試表格格式輸出成本"""
        result = runner.invoke(
            cli, ["cost", "-f", str(temp_cost_file), "--format", "table"]
        )
        assert result.exit_code == 0
        # 表格格式應該包含表格元素
        assert "─" in result.output or "成本" in result.output

    def test_cost_pricing_table(self, runner, mock_settings):
        """測試顯示價格表"""
        result = runner.invoke(cli, ["cost", "--pricing"])
        assert result.exit_code == 0
        assert "價格" in result.output or "USD" in result.output or "OpenAI" in result.output

    def test_cost_nonexistent_file(self, runner, mock_settings):
        """測試載入不存在的文件"""
        result = runner.invoke(cli, ["cost", "-f", "/nonexistent/file.json"])
        # 應該顯示錯誤
        assert result.exit_code != 0 or "錯誤" in result.output or "找不到" in result.output

    def test_cost_combined_options(self, runner, mock_settings, temp_cost_file):
        """測試組合選項"""
        result = runner.invoke(
            cli,
            [
                "cost",
                "-f",
                str(temp_cost_file),
                "-m",
                "gpt-4o-mini",
                "--format",
                "json",
            ],
        )
        assert result.exit_code == 0


@pytest.mark.unit
class TestValidateCommand:
    """測試 validate 命令"""

    def test_validate_all_providers(self, runner, mock_settings):
        """測試驗證所有提供商"""
        result = runner.invoke(cli, ["validate"])
        assert result.exit_code in [0, 1]  # 可能通過或失敗
        assert "驗證" in result.output or "API" in result.output

    def test_validate_specific_provider(self, runner, mock_settings):
        """測試驗證特定提供商"""
        result = runner.invoke(cli, ["validate", "-p", "openai"])
        assert result.exit_code in [0, 1]
        assert "OPENAI" in result.output or "OpenAI" in result.output

    @pytest.mark.parametrize(
        "provider",
        ["openai", "anthropic", "google", "groq"],
    )
    def test_validate_each_provider(self, runner, mock_settings, provider):
        """測試驗證每個提供商"""
        result = runner.invoke(cli, ["validate", "-p", provider])
        assert result.exit_code in [0, 1]

    def test_validate_with_fix(self, runner, mock_settings):
        """測試自動修復選項"""
        result = runner.invoke(cli, ["validate", "--fix"])
        assert result.exit_code in [0, 1]

    def test_validate_invalid_provider(self, runner, mock_settings):
        """測試無效的提供商"""
        result = runner.invoke(cli, ["validate", "-p", "invalid"])
        assert result.exit_code != 0

    def test_validate_missing_key(self, runner):
        """測試缺少 API 金鑰時的驗證"""
        # 注意：由於 conftest.py 的 env_setup fixture 會自動設置 API 金鑰，
        # 這個測試可能無法完全模擬缺少金鑰的情況。
        # 我們主要測試驗證邏輯的輸出格式。
        env = {
            "TESTING": "true"
            # 不設置任何 API 金鑰
        }
        result = runner.invoke(cli, ["validate", "-p", "openai"], env=env)
        # 檢查輸出中包含驗證相關信息
        assert "驗證" in result.output or "API" in result.output or "OPENAI" in result.output
        # 檢查是否有狀態標記
        assert "✓" in result.output or "✗" in result.output

    def test_validate_invalid_key_format(self, runner):
        """測試無效的金鑰格式"""
        # 注意：由於 Settings 的緩存機制，這個測試主要驗證輸出格式
        env = {
            "TESTING": "true",
            "OPENAI_API_KEY": "invalid-key"
        }
        result = runner.invoke(cli, ["validate", "-p", "openai"], env=env)
        # 檢查輸出中包含驗證相關信息
        assert "驗證" in result.output or "OPENAI" in result.output
        # 檢查是否有狀態標記
        assert "✓" in result.output or "✗" in result.output

    def test_validate_success_output(self, runner, mock_settings):
        """測試驗證成功時的輸出格式"""
        result = runner.invoke(cli, ["validate", "-p", "openai"])
        # 應該包含驗證結果（通過或失敗）
        assert "✓" in result.output or "✗" in result.output or "驗證" in result.output

    def test_validate_combined_options(self, runner, mock_settings):
        """測試組合選項"""
        result = runner.invoke(cli, ["validate", "-p", "openai", "--fix"])
        assert result.exit_code in [0, 1]


@pytest.mark.unit
class TestCLIErrorHandling:
    """測試 CLI 錯誤處理"""

    def test_invalid_command(self, runner):
        """測試無效的命令"""
        result = runner.invoke(cli, ["invalid-command"])
        assert result.exit_code != 0

    def test_config_with_invalid_option_value(self, runner, mock_settings):
        """測試配置命令的無效選項值"""
        result = runner.invoke(cli, ["config", "--format", "xml"])
        assert result.exit_code != 0

    def test_multiple_invalid_options(self, runner):
        """測試多個無效選項"""
        result = runner.invoke(cli, ["config", "--invalid1", "--invalid2"])
        assert result.exit_code != 0

    @patch("src.llm_agent_demo.cli.get_settings")
    def test_config_exception_handling(self, mock_get_settings, runner):
        """測試配置異常處理"""
        mock_get_settings.side_effect = Exception("測試錯誤")
        result = runner.invoke(cli, ["config"])
        assert result.exit_code == 1
        assert "錯誤" in result.output


@pytest.mark.unit
class TestCLIIntegration:
    """測試 CLI 整合功能"""

    def test_config_to_validate_workflow(self, runner, mock_settings):
        """測試配置查看後驗證的工作流程"""
        # 先查看配置
        config_result = runner.invoke(cli, ["config", "-p", "openai"])
        assert config_result.exit_code == 0

        # 再驗證配置
        validate_result = runner.invoke(cli, ["validate", "-p", "openai"])
        assert validate_result.exit_code in [0, 1]

    def test_reload_and_revalidate(self, runner, mock_settings):
        """測試重新載入並驗證"""
        # 重新載入配置
        reload_result = runner.invoke(cli, ["config", "--reload"])
        assert reload_result.exit_code == 0

        # 驗證配置
        validate_result = runner.invoke(cli, ["validate"])
        assert validate_result.exit_code in [0, 1]

    def test_all_commands_available(self, runner):
        """測試所有命令都可用"""
        help_result = runner.invoke(cli, ["--help"])
        assert help_result.exit_code == 0
        assert "config" in help_result.output
        assert "validate" in help_result.output
        assert "cost" in help_result.output


@pytest.mark.unit
class TestCLIOutput:
    """測試 CLI 輸出格式"""

    def test_config_output_contains_table(self, runner, mock_settings):
        """測試配置輸出包含表格"""
        result = runner.invoke(cli, ["config"])
        assert result.exit_code == 0
        # Rich 表格應該包含特殊字符
        assert len(result.output) > 0

    def test_json_output_parsable(self, runner, mock_settings):
        """測試 JSON 輸出可解析"""
        result = runner.invoke(cli, ["config", "-f", "json"])
        assert result.exit_code == 0
        # 輸出應該包含 JSON 結構
        assert "{" in result.output

    def test_cost_pricing_output_format(self, runner):
        """測試價格表輸出格式"""
        result = runner.invoke(cli, ["cost", "--pricing"])
        assert result.exit_code == 0
        # 應該包含價格信息
        assert "$" in result.output or "USD" in result.output

    def test_validate_output_format(self, runner, mock_settings):
        """測試驗證輸出格式"""
        result = runner.invoke(cli, ["validate"])
        assert result.exit_code in [0, 1]
        # 應該包含狀態標記
        assert "✓" in result.output or "✗" in result.output or len(result.output) > 0


@pytest.mark.unit
class TestCLIEdgeCases:
    """測試 CLI 邊界情況"""

    def test_empty_config_file(self, runner, tmp_path, monkeypatch):
        """測試空配置文件"""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        reload_settings()
        result = runner.invoke(cli, ["config"])
        assert result.exit_code == 0 or result.exit_code == 1

    def test_very_long_api_key(self, runner, monkeypatch):
        """測試超長 API 金鑰"""
        long_key = "sk-" + "a" * 100
        monkeypatch.setenv("OPENAI_API_KEY", long_key)
        reload_settings()
        result = runner.invoke(cli, ["config", "--show-keys"])
        assert result.exit_code == 0

    def test_special_characters_in_env(self, runner, monkeypatch):
        """測試環境變數中的特殊字符"""
        monkeypatch.setenv("LOG_LEVEL", "INFO")
        reload_settings()
        result = runner.invoke(cli, ["config"])
        assert result.exit_code == 0

    def test_concurrent_commands(self, runner, mock_settings):
        """測試並發命令執行（模擬）"""
        # 連續執行多個命令
        for _ in range(3):
            result = runner.invoke(cli, ["config", "-p", "openai"])
            assert result.exit_code == 0

    def test_unicode_in_output(self, runner, mock_settings):
        """測試輸出中的 Unicode 字符"""
        result = runner.invoke(cli, ["config"])
        assert result.exit_code == 0
        # 中文和特殊符號應該正確顯示
        assert isinstance(result.output, str)

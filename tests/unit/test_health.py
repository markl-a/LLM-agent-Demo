"""健康檢查模組測試

測試 health.py 模組的功能：
- HealthStatus 和 CheckStatus 枚舉
- CheckResult 和 HealthCheckResult 數據類
- HealthChecker 類的各種檢查方法
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from llm_agent_demo.utils.health import (
    HealthStatus,
    CheckStatus,
    CheckResult,
    HealthCheckResult,
    HealthChecker,
    run_health_check,
)


class TestHealthStatus:
    """測試 HealthStatus 枚舉"""

    def test_healthy_status(self):
        """測試健康狀態"""
        assert HealthStatus.HEALTHY.value == "healthy"

    def test_degraded_status(self):
        """測試降級狀態"""
        assert HealthStatus.DEGRADED.value == "degraded"

    def test_unhealthy_status(self):
        """測試不健康狀態"""
        assert HealthStatus.UNHEALTHY.value == "unhealthy"


class TestCheckStatus:
    """測試 CheckStatus 枚舉"""

    def test_pass_status(self):
        """測試通過狀態"""
        assert CheckStatus.PASS.value == "pass"

    def test_fail_status(self):
        """測試失敗狀態"""
        assert CheckStatus.FAIL.value == "fail"

    def test_warn_status(self):
        """測試警告狀態"""
        assert CheckStatus.WARN.value == "warn"

    def test_skip_status(self):
        """測試跳過狀態"""
        assert CheckStatus.SKIP.value == "skip"


class TestCheckResult:
    """測試 CheckResult 數據類"""

    def test_create_check_result(self):
        """測試創建檢查結果"""
        result = CheckResult(
            name="test_check",
            status=CheckStatus.PASS,
            message="檢查通過",
            duration_ms=10.5,
        )
        assert result.name == "test_check"
        assert result.status == CheckStatus.PASS
        assert result.message == "檢查通過"
        assert result.duration_ms == 10.5

    def test_is_passing_with_pass_status(self):
        """測試 is_passing 方法 - 通過狀態"""
        result = CheckResult(
            name="test",
            status=CheckStatus.PASS,
            message="ok",
            duration_ms=1.0,
        )
        assert result.is_passing() is True

    def test_is_passing_with_warn_status(self):
        """測試 is_passing 方法 - 警告狀態也算通過"""
        result = CheckResult(
            name="test",
            status=CheckStatus.WARN,
            message="warning",
            duration_ms=1.0,
        )
        assert result.is_passing() is True

    def test_is_passing_with_fail_status(self):
        """測試 is_passing 方法 - 失敗狀態"""
        result = CheckResult(
            name="test",
            status=CheckStatus.FAIL,
            message="failed",
            duration_ms=1.0,
        )
        assert result.is_passing() is False

    def test_to_dict(self):
        """測試轉換為字典"""
        result = CheckResult(
            name="api_check",
            status=CheckStatus.PASS,
            message="API 連接正常",
            duration_ms=25.3,
            critical=True,
            details={"endpoint": "https://api.example.com"},
        )
        result_dict = result.to_dict()

        assert result_dict["name"] == "api_check"
        assert result_dict["status"] == "pass"
        assert result_dict["message"] == "API 連接正常"
        assert result_dict["duration_ms"] == 25.3
        assert result_dict["critical"] is True
        assert result_dict["details"]["endpoint"] == "https://api.example.com"

    def test_to_dict_with_error(self):
        """測試帶錯誤的字典轉換"""
        error = ValueError("測試錯誤")
        result = CheckResult(
            name="error_check",
            status=CheckStatus.FAIL,
            message="檢查失敗",
            duration_ms=5.0,
            error=error,
        )
        result_dict = result.to_dict()

        assert "error" in result_dict
        assert result_dict["error"]["type"] == "ValueError"
        assert result_dict["error"]["message"] == "測試錯誤"


class TestHealthCheckResult:
    """測試 HealthCheckResult 數據類"""

    def test_create_health_check_result(self):
        """測試創建健康檢查結果"""
        checks = [
            CheckResult("check1", CheckStatus.PASS, "ok", 10.0),
            CheckResult("check2", CheckStatus.FAIL, "failed", 20.0),
            CheckResult("check3", CheckStatus.WARN, "warning", 15.0),
        ]
        result = HealthCheckResult(
            status=HealthStatus.DEGRADED,
            timestamp=datetime.now(),
            checks=checks,
            total_duration_ms=45.0,
        )

        assert result.status == HealthStatus.DEGRADED
        assert len(result.checks) == 3
        assert result.total_duration_ms == 45.0

    def test_passed_checks_count(self):
        """測試通過檢查計數"""
        checks = [
            CheckResult("check1", CheckStatus.PASS, "ok", 10.0),
            CheckResult("check2", CheckStatus.PASS, "ok", 10.0),
            CheckResult("check3", CheckStatus.FAIL, "failed", 10.0),
        ]
        result = HealthCheckResult(
            status=HealthStatus.DEGRADED,
            timestamp=datetime.now(),
            checks=checks,
            total_duration_ms=30.0,
        )

        assert result.passed_checks == 2

    def test_failed_checks_count(self):
        """測試失敗檢查計數"""
        checks = [
            CheckResult("check1", CheckStatus.PASS, "ok", 10.0),
            CheckResult("check2", CheckStatus.FAIL, "failed", 10.0),
            CheckResult("check3", CheckStatus.FAIL, "failed", 10.0),
        ]
        result = HealthCheckResult(
            status=HealthStatus.UNHEALTHY,
            timestamp=datetime.now(),
            checks=checks,
            total_duration_ms=30.0,
        )

        assert result.failed_checks == 2

    def test_warned_checks_count(self):
        """測試警告檢查計數"""
        checks = [
            CheckResult("check1", CheckStatus.WARN, "warning", 10.0),
            CheckResult("check2", CheckStatus.WARN, "warning", 10.0),
            CheckResult("check3", CheckStatus.PASS, "ok", 10.0),
        ]
        result = HealthCheckResult(
            status=HealthStatus.HEALTHY,
            timestamp=datetime.now(),
            checks=checks,
            total_duration_ms=30.0,
        )

        assert result.warned_checks == 2

    def test_total_checks_count(self):
        """測試總檢查計數"""
        checks = [
            CheckResult("check1", CheckStatus.PASS, "ok", 10.0),
            CheckResult("check2", CheckStatus.FAIL, "failed", 10.0),
            CheckResult("check3", CheckStatus.WARN, "warning", 10.0),
            CheckResult("check4", CheckStatus.SKIP, "skipped", 0.0),
        ]
        result = HealthCheckResult(
            status=HealthStatus.DEGRADED,
            timestamp=datetime.now(),
            checks=checks,
            total_duration_ms=30.0,
        )

        assert result.total_checks == 4

    def test_get_failed_critical_checks(self):
        """測試獲取失敗的關鍵檢查"""
        checks = [
            CheckResult("check1", CheckStatus.PASS, "ok", 10.0, critical=True),
            CheckResult("check2", CheckStatus.FAIL, "failed", 10.0, critical=True),
            CheckResult("check3", CheckStatus.FAIL, "failed", 10.0, critical=False),
        ]
        result = HealthCheckResult(
            status=HealthStatus.UNHEALTHY,
            timestamp=datetime.now(),
            checks=checks,
            total_duration_ms=30.0,
        )

        failed_critical = result.get_failed_critical_checks()
        assert len(failed_critical) == 1
        assert failed_critical[0].name == "check2"

    def test_get_summary(self):
        """測試獲取檢查摘要"""
        checks = [
            CheckResult("check1", CheckStatus.PASS, "ok", 10.0),
            CheckResult("check2", CheckStatus.FAIL, "failed", 10.0),
        ]
        result = HealthCheckResult(
            status=HealthStatus.DEGRADED,
            timestamp=datetime.now(),
            checks=checks,
            total_duration_ms=20.0,
        )

        summary = result.get_summary()
        assert "健康檢查摘要" in summary
        assert "DEGRADED" in summary
        assert "1 通過" in summary
        assert "1 失敗" in summary


class TestHealthChecker:
    """測試 HealthChecker 類"""

    @pytest.fixture
    def checker(self):
        """創建 HealthChecker 實例"""
        return HealthChecker()

    def test_checker_initialization(self, checker):
        """測試 HealthChecker 初始化"""
        assert checker is not None

    @patch("llm_agent_demo.utils.health.get_settings")
    def test_check_config(self, mock_settings, checker):
        """測試配置檢查"""
        mock_settings.return_value = MagicMock()
        result = checker.check_config()

        assert result.name == "config"
        assert result.status in [CheckStatus.PASS, CheckStatus.FAIL, CheckStatus.WARN]

    def test_check_network_connectivity(self, checker):
        """測試網絡連通性檢查"""
        result = checker.check_network()

        assert result.name == "network"
        assert result.status in [CheckStatus.PASS, CheckStatus.FAIL, CheckStatus.WARN]
        assert result.duration_ms >= 0


class TestRunHealthCheck:
    """測試 run_health_check 函數"""

    @patch("llm_agent_demo.utils.health.HealthChecker")
    def test_run_health_check(self, mock_checker_class):
        """測試運行健康檢查"""
        mock_checker = MagicMock()
        mock_checker.check_all.return_value = HealthCheckResult(
            status=HealthStatus.HEALTHY,
            timestamp=datetime.now(),
            checks=[],
            total_duration_ms=10.0,
        )
        mock_checker_class.return_value = mock_checker

        result = run_health_check()

        assert result.status == HealthStatus.HEALTHY
        mock_checker.check_all.assert_called_once()

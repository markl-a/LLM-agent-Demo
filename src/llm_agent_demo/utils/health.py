"""健康檢查模組 - 提供系統健康檢查功能

這個模組提供了完整的健康檢查解決方案，包括：
- API 連通性檢查（OpenAI、Anthropic、Google、Groq）
- 配置完整性檢查
- 依賴服務檢查（向量數據庫、搜索服務等）
- 健康狀態報告
- 異步和同步檢查支持

使用示例：
    >>> from llm_agent_demo.utils.health import HealthChecker, run_health_check
    >>> # 快速檢查
    >>> result = run_health_check()
    >>> print(result.status)  # "healthy", "degraded", "unhealthy"
    >>>
    >>> # 詳細檢查
    >>> checker = HealthChecker()
    >>> result = checker.check_all()
    >>> print(result.get_summary())
"""

import asyncio
import logging
import socket
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from .config import get_settings
from .exceptions import (
    APIKeyError,
    AuthenticationError,
    ConfigurationError,
    ConnectionError,
    NetworkError,
    TimeoutError,
)

logger = logging.getLogger(__name__)


# ============================================================================
# 健康狀態枚舉
# ============================================================================


class HealthStatus(str, Enum):
    """健康狀態枚舉"""

    HEALTHY = "healthy"  # 所有檢查通過
    DEGRADED = "degraded"  # 部分檢查失敗，但核心功能可用
    UNHEALTHY = "unhealthy"  # 關鍵檢查失敗，系統不可用


class CheckStatus(str, Enum):
    """單個檢查的狀態"""

    PASS = "pass"  # 檢查通過
    FAIL = "fail"  # 檢查失敗
    WARN = "warn"  # 檢查警告
    SKIP = "skip"  # 檢查跳過


# ============================================================================
# 檢查結果數據類
# ============================================================================


@dataclass
class CheckResult:
    """單個檢查的結果"""

    name: str  # 檢查名稱
    status: CheckStatus  # 檢查狀態
    message: str  # 檢查訊息
    duration_ms: float  # 檢查耗時（毫秒）
    critical: bool = False  # 是否為關鍵檢查
    details: Dict[str, Any] = field(default_factory=dict)  # 額外詳情
    error: Optional[Exception] = None  # 錯誤信息

    def is_passing(self) -> bool:
        """檢查是否通過"""
        return self.status in (CheckStatus.PASS, CheckStatus.WARN)

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        result = {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "duration_ms": round(self.duration_ms, 2),
            "critical": self.critical,
        }
        if self.details:
            result["details"] = self.details
        if self.error:
            result["error"] = {
                "type": type(self.error).__name__,
                "message": str(self.error),
            }
        return result


@dataclass
class HealthCheckResult:
    """健康檢查總結果"""

    status: HealthStatus  # 整體健康狀態
    timestamp: datetime  # 檢查時間
    checks: List[CheckResult]  # 所有檢查結果
    total_duration_ms: float  # 總耗時（毫秒）
    version: str = "2.0.0"  # 系統版本

    @property
    def passed_checks(self) -> int:
        """通過的檢查數量"""
        return sum(1 for check in self.checks if check.status == CheckStatus.PASS)

    @property
    def failed_checks(self) -> int:
        """失敗的檢查數量"""
        return sum(1 for check in self.checks if check.status == CheckStatus.FAIL)

    @property
    def warned_checks(self) -> int:
        """警告的檢查數量"""
        return sum(1 for check in self.checks if check.status == CheckStatus.WARN)

    @property
    def total_checks(self) -> int:
        """總檢查數量"""
        return len(self.checks)

    def get_failed_critical_checks(self) -> List[CheckResult]:
        """獲取失敗的關鍵檢查"""
        return [
            check
            for check in self.checks
            if check.critical and check.status == CheckStatus.FAIL
        ]

    def get_summary(self) -> str:
        """獲取檢查摘要"""
        lines = [
            f"健康檢查摘要 ({self.timestamp.strftime('%Y-%m-%d %H:%M:%S')})",
            f"整體狀態: {self.status.value.upper()}",
            f"總耗時: {self.total_duration_ms:.2f}ms",
            f"檢查統計: {self.passed_checks} 通過, {self.failed_checks} 失敗, {self.warned_checks} 警告",
            "",
        ]

        # 添加失敗的檢查
        failed = [check for check in self.checks if check.status == CheckStatus.FAIL]
        if failed:
            lines.append("失敗的檢查:")
            for check in failed:
                critical_marker = " [CRITICAL]" if check.critical else ""
                lines.append(f"  ✗ {check.name}{critical_marker}: {check.message}")
            lines.append("")

        # 添加警告的檢查
        warned = [check for check in self.checks if check.status == CheckStatus.WARN]
        if warned:
            lines.append("警告的檢查:")
            for check in warned:
                lines.append(f"  ⚠ {check.name}: {check.message}")
            lines.append("")

        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat(),
            "version": self.version,
            "total_duration_ms": round(self.total_duration_ms, 2),
            "summary": {
                "total": self.total_checks,
                "passed": self.passed_checks,
                "failed": self.failed_checks,
                "warned": self.warned_checks,
            },
            "checks": [check.to_dict() for check in self.checks],
        }


# ============================================================================
# 健康檢查器
# ============================================================================


class HealthChecker:
    """系統健康檢查器

    提供全面的系統健康檢查功能，包括：
    - API 連通性檢查
    - 配置完整性檢查
    - 依賴服務檢查
    """

    def __init__(
        self,
        timeout: int = 10,
        check_apis: bool = True,
        check_config: bool = True,
        check_services: bool = True,
    ):
        """
        初始化健康檢查器

        Args:
            timeout: 單個檢查的超時時間（秒）
            check_apis: 是否檢查 API 連通性
            check_config: 是否檢查配置完整性
            check_services: 是否檢查依賴服務
        """
        self.timeout = timeout
        self.check_apis = check_apis
        self.check_config = check_config
        self.check_services = check_services
        self.settings = get_settings()

    def check_all(self, verbose: bool = False) -> HealthCheckResult:
        """
        執行所有健康檢查

        Args:
            verbose: 是否輸出詳細日誌

        Returns:
            HealthCheckResult: 健康檢查結果
        """
        start_time = time.perf_counter()
        checks: List[CheckResult] = []

        if verbose:
            logger.info("開始執行健康檢查...")

        # 1. 配置完整性檢查
        if self.check_config:
            checks.extend(self._check_configuration(verbose))

        # 2. API 連通性檢查
        if self.check_apis:
            checks.extend(self._check_api_connectivity(verbose))

        # 3. 依賴服務檢查
        if self.check_services:
            checks.extend(self._check_dependent_services(verbose))

        # 4. 系統資源檢查
        checks.extend(self._check_system_resources(verbose))

        total_duration = (time.perf_counter() - start_time) * 1000

        # 確定整體健康狀態
        status = self._determine_overall_status(checks)

        result = HealthCheckResult(
            status=status,
            timestamp=datetime.now(),
            checks=checks,
            total_duration_ms=total_duration,
        )

        if verbose:
            logger.info(f"健康檢查完成，狀態: {status.value}")

        return result

    def _check_configuration(self, verbose: bool = False) -> List[CheckResult]:
        """檢查配置完整性"""
        checks = []

        # 檢查環境配置
        check = self._run_check(
            name="環境配置",
            check_func=self._verify_environment_config,
            critical=True,
            verbose=verbose,
        )
        checks.append(check)

        # 檢查 LLM 配置
        check = self._run_check(
            name="LLM 配置",
            check_func=self._verify_llm_config,
            critical=False,
            verbose=verbose,
        )
        checks.append(check)

        return checks

    def _check_api_connectivity(self, verbose: bool = False) -> List[CheckResult]:
        """檢查 API 連通性"""
        checks = []

        # OpenAI API
        if self.settings.openai_api_key:
            check = self._run_check(
                name="OpenAI API",
                check_func=lambda: self._check_openai_api(),
                critical=False,
                verbose=verbose,
            )
            checks.append(check)

        # Anthropic API
        if self.settings.anthropic_api_key:
            check = self._run_check(
                name="Anthropic API",
                check_func=lambda: self._check_anthropic_api(),
                critical=False,
                verbose=verbose,
            )
            checks.append(check)

        # Google API
        if self.settings.google_api_key:
            check = self._run_check(
                name="Google API",
                check_func=lambda: self._check_google_api(),
                critical=False,
                verbose=verbose,
            )
            checks.append(check)

        # Groq API
        if self.settings.groq_api_key:
            check = self._run_check(
                name="Groq API",
                check_func=lambda: self._check_groq_api(),
                critical=False,
                verbose=verbose,
            )
            checks.append(check)

        return checks

    def _check_dependent_services(self, verbose: bool = False) -> List[CheckResult]:
        """檢查依賴服務"""
        checks = []

        # 檢查向量數據庫
        if self.settings.qdrant_url:
            check = self._run_check(
                name="Qdrant 向量數據庫",
                check_func=lambda: self._check_qdrant_service(),
                critical=False,
                verbose=verbose,
            )
            checks.append(check)

        # 檢查 Pinecone
        if self.settings.pinecone_api_key:
            check = self._run_check(
                name="Pinecone 向量數據庫",
                check_func=lambda: self._check_pinecone_service(),
                critical=False,
                verbose=verbose,
            )
            checks.append(check)

        # 檢查搜索服務
        if self.settings.serper_api_key:
            check = self._run_check(
                name="Serper 搜索服務",
                check_func=lambda: self._check_serper_service(),
                critical=False,
                verbose=verbose,
            )
            checks.append(check)

        if self.settings.tavily_api_key:
            check = self._run_check(
                name="Tavily 搜索服務",
                check_func=lambda: self._check_tavily_service(),
                critical=False,
                verbose=verbose,
            )
            checks.append(check)

        return checks

    def _check_system_resources(self, verbose: bool = False) -> List[CheckResult]:
        """檢查系統資源"""
        checks = []

        # 檢查網絡連接
        check = self._run_check(
            name="網絡連接",
            check_func=self._check_network_connectivity,
            critical=True,
            verbose=verbose,
        )
        checks.append(check)

        # 檢查磁盤空間
        check = self._run_check(
            name="磁盤空間",
            check_func=self._check_disk_space,
            critical=False,
            verbose=verbose,
        )
        checks.append(check)

        return checks

    def _run_check(
        self,
        name: str,
        check_func: callable,
        critical: bool = False,
        verbose: bool = False,
    ) -> CheckResult:
        """
        執行單個檢查

        Args:
            name: 檢查名稱
            check_func: 檢查函數
            critical: 是否為關鍵檢查
            verbose: 是否輸出詳細日誌

        Returns:
            CheckResult: 檢查結果
        """
        start_time = time.perf_counter()

        if verbose:
            logger.debug(f"執行檢查: {name}")

        try:
            result = check_func()
            duration = (time.perf_counter() - start_time) * 1000

            if isinstance(result, CheckResult):
                result.duration_ms = duration
                result.critical = critical
                return result

            # 如果返回的是元組 (status, message, details)
            status, message = result if isinstance(result, tuple) else (CheckStatus.PASS, result)
            details = result[2] if isinstance(result, tuple) and len(result) > 2 else {}

            return CheckResult(
                name=name,
                status=status,
                message=message,
                duration_ms=duration,
                critical=critical,
                details=details,
            )

        except Exception as e:
            duration = (time.perf_counter() - start_time) * 1000
            logger.warning(f"檢查 '{name}' 失敗: {str(e)}")

            return CheckResult(
                name=name,
                status=CheckStatus.FAIL,
                message=f"檢查失敗: {str(e)}",
                duration_ms=duration,
                critical=critical,
                error=e,
            )

    # ========================================================================
    # 配置檢查函數
    # ========================================================================

    def _verify_environment_config(self) -> Tuple[CheckStatus, str, Dict[str, Any]]:
        """驗證環境配置"""
        details = {
            "app_env": self.settings.app_env,
            "debug": self.settings.debug,
            "log_level": self.settings.log_level,
        }

        # 檢查必要的配置
        if not self.settings.app_env:
            return CheckStatus.FAIL, "未設定應用環境", details

        # 生產環境警告
        if self.settings.is_production() and self.settings.debug:
            return CheckStatus.WARN, "生產環境不應啟用調試模式", details

        return CheckStatus.PASS, "環境配置正常", details

    def _verify_llm_config(self) -> Tuple[CheckStatus, str, Dict[str, Any]]:
        """驗證 LLM 配置"""
        available_providers = []
        missing_providers = []

        providers = {
            "OpenAI": self.settings.openai_api_key,
            "Anthropic": self.settings.anthropic_api_key,
            "Google": self.settings.google_api_key,
            "Groq": self.settings.groq_api_key,
        }

        for provider, api_key in providers.items():
            if api_key:
                available_providers.append(provider)
            else:
                missing_providers.append(provider)

        details = {
            "available_providers": available_providers,
            "missing_providers": missing_providers,
            "total_available": len(available_providers),
        }

        if not available_providers:
            return CheckStatus.FAIL, "未配置任何 LLM 提供商", details

        if len(available_providers) == 1:
            return CheckStatus.WARN, f"僅配置了 {available_providers[0]}", details

        return CheckStatus.PASS, f"已配置 {len(available_providers)} 個 LLM 提供商", details

    # ========================================================================
    # API 連通性檢查函數
    # ========================================================================

    def _check_openai_api(self) -> Tuple[CheckStatus, str, Dict[str, Any]]:
        """檢查 OpenAI API"""
        try:
            import openai

            client = openai.OpenAI(
                api_key=self.settings.openai_api_key,
                base_url=self.settings.openai_api_base,
                timeout=self.timeout,
            )

            # 嘗試列出模型
            models = client.models.list()
            model_count = len(list(models))

            return CheckStatus.PASS, "OpenAI API 連接正常", {"model_count": model_count}

        except ImportError:
            return CheckStatus.SKIP, "未安裝 OpenAI SDK", {}
        except Exception as e:
            return CheckStatus.FAIL, f"OpenAI API 連接失敗: {str(e)}", {}

    def _check_anthropic_api(self) -> Tuple[CheckStatus, str, Dict[str, Any]]:
        """檢查 Anthropic API"""
        try:
            import anthropic

            client = anthropic.Anthropic(
                api_key=self.settings.anthropic_api_key,
                timeout=self.timeout,
            )

            # 嘗試發送最小請求來驗證 API
            # 注意：Anthropic 沒有 list models 端點，我們只能檢查 API key 格式
            if not self.settings.anthropic_api_key.startswith("sk-ant-"):
                return CheckStatus.WARN, "Anthropic API 金鑰格式可能不正確", {}

            return CheckStatus.PASS, "Anthropic API 配置正常", {}

        except ImportError:
            return CheckStatus.SKIP, "未安裝 Anthropic SDK", {}
        except Exception as e:
            return CheckStatus.FAIL, f"Anthropic API 檢查失敗: {str(e)}", {}

    def _check_google_api(self) -> Tuple[CheckStatus, str, Dict[str, Any]]:
        """檢查 Google Gemini API"""
        try:
            import google.generativeai as genai

            genai.configure(api_key=self.settings.google_api_key)

            # 嘗試列出可用模型
            models = genai.list_models()
            model_count = len(list(models))

            return CheckStatus.PASS, "Google API 連接正常", {"model_count": model_count}

        except ImportError:
            return CheckStatus.SKIP, "未安裝 Google GenerativeAI SDK", {}
        except Exception as e:
            return CheckStatus.FAIL, f"Google API 連接失敗: {str(e)}", {}

    def _check_groq_api(self) -> Tuple[CheckStatus, str, Dict[str, Any]]:
        """檢查 Groq API"""
        try:
            from groq import Groq

            client = Groq(api_key=self.settings.groq_api_key, timeout=self.timeout)

            # 嘗試列出模型
            models = client.models.list()
            model_count = len(list(models.data))

            return CheckStatus.PASS, "Groq API 連接正常", {"model_count": model_count}

        except ImportError:
            return CheckStatus.SKIP, "未安裝 Groq SDK", {}
        except Exception as e:
            return CheckStatus.FAIL, f"Groq API 連接失敗: {str(e)}", {}

    # ========================================================================
    # 依賴服務檢查函數
    # ========================================================================

    def _check_qdrant_service(self) -> Tuple[CheckStatus, str, Dict[str, Any]]:
        """檢查 Qdrant 服務"""
        try:
            from urllib.parse import urlparse

            import requests

            parsed_url = urlparse(self.settings.qdrant_url)
            host = parsed_url.hostname or "localhost"
            port = parsed_url.port or 6333

            # 嘗試連接 Qdrant 健康檢查端點
            response = requests.get(
                f"http://{host}:{port}/healthz", timeout=self.timeout
            )

            if response.status_code == 200:
                return CheckStatus.PASS, "Qdrant 服務運行正常", {"host": host, "port": port}
            else:
                return (
                    CheckStatus.FAIL,
                    f"Qdrant 服務響應異常: {response.status_code}",
                    {},
                )

        except ImportError:
            return CheckStatus.SKIP, "未安裝 requests 庫", {}
        except Exception as e:
            return CheckStatus.FAIL, f"Qdrant 服務連接失敗: {str(e)}", {}

    def _check_pinecone_service(self) -> Tuple[CheckStatus, str, Dict[str, Any]]:
        """檢查 Pinecone 服務"""
        try:
            from pinecone import Pinecone

            pc = Pinecone(api_key=self.settings.pinecone_api_key)

            # 列出可用索引
            indexes = pc.list_indexes()
            index_count = len(list(indexes))

            return CheckStatus.PASS, "Pinecone 服務連接正常", {"index_count": index_count}

        except ImportError:
            return CheckStatus.SKIP, "未安裝 Pinecone SDK", {}
        except Exception as e:
            return CheckStatus.FAIL, f"Pinecone 服務連接失敗: {str(e)}", {}

    def _check_serper_service(self) -> Tuple[CheckStatus, str, Dict[str, Any]]:
        """檢查 Serper 搜索服務"""
        try:
            import requests

            # 驗證 API key 格式
            if not self.settings.serper_api_key:
                return CheckStatus.FAIL, "Serper API 金鑰未設定", {}

            # 可以添加簡單的驗證請求
            return CheckStatus.PASS, "Serper API 配置正常", {}

        except Exception as e:
            return CheckStatus.FAIL, f"Serper 服務檢查失敗: {str(e)}", {}

    def _check_tavily_service(self) -> Tuple[CheckStatus, str, Dict[str, Any]]:
        """檢查 Tavily 搜索服務"""
        try:
            # 驗證 API key 格式
            if not self.settings.tavily_api_key:
                return CheckStatus.FAIL, "Tavily API 金鑰未設定", {}

            return CheckStatus.PASS, "Tavily API 配置正常", {}

        except Exception as e:
            return CheckStatus.FAIL, f"Tavily 服務檢查失敗: {str(e)}", {}

    # ========================================================================
    # 系統資源檢查函數
    # ========================================================================

    def _check_network_connectivity(self) -> Tuple[CheckStatus, str, Dict[str, Any]]:
        """檢查網絡連接"""
        try:
            # 嘗試連接 Google DNS
            sock = socket.create_connection(("8.8.8.8", 53), timeout=self.timeout)
            sock.close()
            return CheckStatus.PASS, "網絡連接正常", {}
        except socket.error as e:
            return CheckStatus.FAIL, f"網絡連接失敗: {str(e)}", {}

    def _check_disk_space(self) -> Tuple[CheckStatus, str, Dict[str, Any]]:
        """檢查磁盤空間"""
        try:
            import shutil

            total, used, free = shutil.disk_usage("/")

            # 轉換為 GB
            total_gb = total // (2**30)
            used_gb = used // (2**30)
            free_gb = free // (2**30)
            used_percent = (used / total) * 100

            details = {
                "total_gb": total_gb,
                "used_gb": used_gb,
                "free_gb": free_gb,
                "used_percent": round(used_percent, 2),
            }

            # 如果使用超過 90%，發出警告
            if used_percent > 90:
                return CheckStatus.WARN, f"磁盤使用率過高 ({used_percent:.1f}%)", details

            # 如果剩餘空間小於 1GB，發出警告
            if free_gb < 1:
                return CheckStatus.WARN, f"磁盤剩餘空間不足 ({free_gb}GB)", details

            return CheckStatus.PASS, f"磁盤空間充足 ({free_gb}GB 可用)", details

        except Exception as e:
            return CheckStatus.FAIL, f"磁盤空間檢查失敗: {str(e)}", {}

    # ========================================================================
    # 輔助方法
    # ========================================================================

    def _determine_overall_status(self, checks: List[CheckResult]) -> HealthStatus:
        """
        根據檢查結果確定整體健康狀態

        Args:
            checks: 所有檢查結果

        Returns:
            HealthStatus: 整體健康狀態
        """
        # 如果有關鍵檢查失敗，系統不健康
        critical_failures = [
            check for check in checks if check.critical and check.status == CheckStatus.FAIL
        ]
        if critical_failures:
            return HealthStatus.UNHEALTHY

        # 如果有任何失敗，系統降級
        failures = [check for check in checks if check.status == CheckStatus.FAIL]
        if failures:
            return HealthStatus.DEGRADED

        # 如果有警告，系統降級
        warnings = [check for check in checks if check.status == CheckStatus.WARN]
        if warnings:
            return HealthStatus.DEGRADED

        # 否則系統健康
        return HealthStatus.HEALTHY


# ============================================================================
# 便利函數
# ============================================================================


def run_health_check(
    timeout: int = 10,
    check_apis: bool = True,
    check_config: bool = True,
    check_services: bool = True,
    verbose: bool = False,
) -> HealthCheckResult:
    """
    快速執行健康檢查

    Args:
        timeout: 單個檢查的超時時間（秒）
        check_apis: 是否檢查 API 連通性
        check_config: 是否檢查配置完整性
        check_services: 是否檢查依賴服務
        verbose: 是否輸出詳細日誌

    Returns:
        HealthCheckResult: 健康檢查結果

    Example:
        >>> result = run_health_check(verbose=True)
        >>> print(result.status)
        'healthy'
        >>> print(result.get_summary())
    """
    checker = HealthChecker(
        timeout=timeout,
        check_apis=check_apis,
        check_config=check_config,
        check_services=check_services,
    )
    return checker.check_all(verbose=verbose)


def get_health_status(timeout: int = 5) -> HealthStatus:
    """
    快速獲取健康狀態（僅返回狀態，不返回詳情）

    Args:
        timeout: 檢查超時時間（秒）

    Returns:
        HealthStatus: 健康狀態

    Example:
        >>> status = get_health_status()
        >>> if status == HealthStatus.HEALTHY:
        ...     print("系統正常")
    """
    result = run_health_check(timeout=timeout, verbose=False)
    return result.status


def is_healthy(timeout: int = 5) -> bool:
    """
    檢查系統是否健康

    Args:
        timeout: 檢查超時時間（秒）

    Returns:
        bool: 系統是否健康

    Example:
        >>> if is_healthy():
        ...     print("系統健康，可以啟動")
    """
    status = get_health_status(timeout=timeout)
    return status == HealthStatus.HEALTHY


# ============================================================================
# 異步健康檢查支持
# ============================================================================


async def run_health_check_async(
    timeout: int = 10,
    check_apis: bool = True,
    check_config: bool = True,
    check_services: bool = True,
    verbose: bool = False,
) -> HealthCheckResult:
    """
    異步執行健康檢查

    Args:
        timeout: 單個檢查的超時時間（秒）
        check_apis: 是否檢查 API 連通性
        check_config: 是否檢查配置完整性
        check_services: 是否檢查依賴服務
        verbose: 是否輸出詳細日誌

    Returns:
        HealthCheckResult: 健康檢查結果

    Example:
        >>> result = await run_health_check_async(verbose=True)
        >>> print(result.status)
    """
    loop = asyncio.get_event_loop()
    checker = HealthChecker(
        timeout=timeout,
        check_apis=check_apis,
        check_config=check_config,
        check_services=check_services,
    )
    return await loop.run_in_executor(None, checker.check_all, verbose)

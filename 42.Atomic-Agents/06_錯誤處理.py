"""
Atomic Agents 錯誤處理
======================

本文件展示如何在 Atomic Agents 中實現健壯的錯誤處理。
良好的錯誤處理對於生產環境至關重要。

主要內容：
1. 異常層次結構
2. 錯誤捕獲和處理
3. 重試機制
4. 降級策略
5. 錯誤日誌
6. 錯誤恢復

作者：Atomic Agents 團隊
日期：2025-12-31
"""

from typing import Any, Dict, List, Optional, Callable, TypeVar, Generic
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum
import time
import traceback
from functools import wraps
from dataclasses import dataclass


# ============================================================================
# 第一部分：異常層次結構
# ============================================================================

class AgentError(Exception):
    """Agent 基礎異常"""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            'error_type': self.__class__.__name__,
            'message': self.message,
            'error_code': self.error_code,
            'details': self.details,
            'timestamp': self.timestamp.isoformat()
        }


class ValidationError(AgentError):
    """驗證錯誤"""
    pass


class ConfigurationError(AgentError):
    """配置錯誤"""
    pass


class ExecutionError(AgentError):
    """執行錯誤"""
    pass


class TimeoutError(AgentError):
    """超時錯誤"""
    pass


class RateLimitError(AgentError):
    """速率限制錯誤"""
    pass


class ModelError(AgentError):
    """模型錯誤"""
    pass


class ToolError(AgentError):
    """工具錯誤"""
    pass


# ============================================================================
# 第二部分：錯誤處理模型
# ============================================================================

class ErrorSeverity(str, Enum):
    """錯誤嚴重程度"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorRecord(BaseModel):
    """錯誤記錄"""
    id: str = Field(..., description="錯誤 ID")
    error_type: str = Field(..., description="錯誤類型")
    message: str = Field(..., description="錯誤消息")
    severity: ErrorSeverity = Field(..., description="嚴重程度")
    timestamp: datetime = Field(default_factory=datetime.now)
    stack_trace: Optional[str] = Field(None, description="堆棧追蹤")
    context: Dict[str, Any] = Field(default_factory=dict)
    resolved: bool = Field(default=False, description="是否已解決")


class ErrorHandler:
    """
    錯誤處理器

    統一處理和記錄錯誤。
    """

    def __init__(self):
        self.error_records: List[ErrorRecord] = []
        self.error_callbacks: Dict[type, Callable] = {}

    def register_handler(
        self,
        error_type: type,
        handler: Callable
    ) -> None:
        """
        註冊錯誤處理函數

        Args:
            error_type: 錯誤類型
            handler: 處理函數
        """
        self.error_callbacks[error_type] = handler

    def handle_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        severity: ErrorSeverity = ErrorSeverity.ERROR
    ) -> ErrorRecord:
        """
        處理錯誤

        Args:
            error: 異常對象
            context: 上下文信息
            severity: 嚴重程度

        Returns:
            錯誤記錄
        """
        # 創建錯誤記錄
        record = ErrorRecord(
            id=f"err_{len(self.error_records)}",
            error_type=error.__class__.__name__,
            message=str(error),
            severity=severity,
            stack_trace=traceback.format_exc(),
            context=context or {}
        )

        self.error_records.append(record)

        # 打印錯誤
        self._log_error(record)

        # 調用註冊的處理器
        for error_type, handler in self.error_callbacks.items():
            if isinstance(error, error_type):
                try:
                    handler(error, record)
                except Exception as e:
                    print(f"錯誤處理器失敗: {str(e)}")

        return record

    def _log_error(self, record: ErrorRecord) -> None:
        """記錄錯誤"""
        print(f"\n{'='*60}")
        print(f"[{record.severity.value.upper()}] {record.error_type}")
        print(f"{'='*60}")
        print(f"消息: {record.message}")
        print(f"時間: {record.timestamp}")
        if record.context:
            print(f"上下文: {record.context}")
        print(f"{'='*60}\n")

    def get_errors(
        self,
        severity: Optional[ErrorSeverity] = None,
        resolved: Optional[bool] = None
    ) -> List[ErrorRecord]:
        """獲取錯誤記錄"""
        records = self.error_records

        if severity:
            records = [r for r in records if r.severity == severity]

        if resolved is not None:
            records = [r for r in records if r.resolved == resolved]

        return records

    def clear_errors(self) -> None:
        """清空錯誤記錄"""
        self.error_records.clear()


# ============================================================================
# 第三部分：重試機制
# ============================================================================

@dataclass
class RetryConfig:
    """重試配置"""
    max_attempts: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    backoff_factor: float = 2.0
    retry_on: tuple = (Exception,)
    retry_if: Optional[Callable[[Exception], bool]] = None


class RetryStrategy:
    """重試策略"""

    def __init__(self, config: RetryConfig):
        self.config = config

    def should_retry(self, error: Exception, attempt: int) -> bool:
        """
        判斷是否應該重試

        Args:
            error: 錯誤
            attempt: 當前嘗試次數

        Returns:
            是否應該重試
        """
        # 檢查嘗試次數
        if attempt >= self.config.max_attempts:
            return False

        # 檢查錯誤類型
        if not isinstance(error, self.config.retry_on):
            return False

        # 自定義條件
        if self.config.retry_if and not self.config.retry_if(error):
            return False

        return True

    def get_delay(self, attempt: int) -> float:
        """
        計算重試延遲

        Args:
            attempt: 當前嘗試次數

        Returns:
            延遲時間（秒）
        """
        delay = self.config.initial_delay * (self.config.backoff_factor ** (attempt - 1))
        return min(delay, self.config.max_delay)


def with_retry(config: Optional[RetryConfig] = None):
    """
    重試裝飾器

    Args:
        config: 重試配置

    Returns:
        裝飾器函數
    """
    if config is None:
        config = RetryConfig()

    strategy = RetryStrategy(config)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            last_error = None

            while True:
                attempt += 1

                try:
                    return func(*args, **kwargs)

                except Exception as e:
                    last_error = e

                    if not strategy.should_retry(e, attempt):
                        print(f"\n最大重試次數已達到，放棄重試")
                        raise

                    delay = strategy.get_delay(attempt)
                    print(f"\n嘗試 {attempt}/{config.max_attempts} 失敗: {str(e)}")
                    print(f"等待 {delay:.1f} 秒後重試...")
                    time.sleep(delay)

            raise last_error

        return wrapper

    return decorator


# ============================================================================
# 第四部分：降級策略
# ============================================================================

class FallbackStrategy:
    """
    降級策略

    當主要操作失敗時提供備選方案。
    """

    def __init__(self):
        self.fallbacks: List[Callable] = []

    def add_fallback(self, fallback: Callable) -> 'FallbackStrategy':
        """添加降級選項"""
        self.fallbacks.append(fallback)
        return self

    def execute(self, *args, **kwargs) -> Any:
        """
        執行帶降級的操作

        Returns:
            操作結果
        """
        for i, fallback in enumerate(self.fallbacks):
            try:
                print(f"\n嘗試選項 {i + 1}...")
                result = fallback(*args, **kwargs)
                if i > 0:
                    print(f"使用降級選項 {i + 1} 成功")
                return result

            except Exception as e:
                print(f"選項 {i + 1} 失敗: {str(e)}")
                if i == len(self.fallbacks) - 1:
                    raise


def with_fallback(*fallback_funcs):
    """
    降級裝飾器

    Args:
        fallback_funcs: 降級函數列表

    Returns:
        裝飾器
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 首先嘗試原始函數
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"主要操作失敗: {str(e)}")

                # 嘗試降級函數
                for i, fallback in enumerate(fallback_funcs, 1):
                    try:
                        print(f"嘗試降級選項 {i}...")
                        return fallback(*args, **kwargs)
                    except Exception as fb_error:
                        print(f"降級選項 {i} 失敗: {str(fb_error)}")

                # 所有選項都失敗
                raise

        return wrapper

    return decorator


# ============================================================================
# 第五部分：斷路器模式
# ============================================================================

class CircuitState(str, Enum):
    """斷路器狀態"""
    CLOSED = "closed"      # 正常
    OPEN = "open"          # 斷開
    HALF_OPEN = "half_open"  # 半開


class CircuitBreaker:
    """
    斷路器

    防止級聯失敗。
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = CircuitState.CLOSED

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        通過斷路器調用函數

        Args:
            func: 要調用的函數
            *args, **kwargs: 函數參數

        Returns:
            函數結果
        """
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise ExecutionError(
                    "斷路器處於打開狀態",
                    error_code="CIRCUIT_OPEN"
                )

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result

        except self.expected_exception as e:
            self._on_failure()
            raise

    def _should_attempt_reset(self) -> bool:
        """判斷是否應該嘗試重置"""
        if not self.last_failure_time:
            return False

        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return elapsed >= self.recovery_timeout

    def _on_success(self) -> None:
        """成功時的處理"""
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def _on_failure(self) -> None:
        """失敗時的處理"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            print(f"\n斷路器已打開（失敗次數: {self.failure_count}）")

    def reset(self) -> None:
        """重置斷路器"""
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED


# ============================================================================
# 第六部分：安全執行包裝器
# ============================================================================

class SafeExecutor:
    """
    安全執行器

    提供多層錯誤處理保護。
    """

    def __init__(
        self,
        error_handler: Optional[ErrorHandler] = None,
        retry_config: Optional[RetryConfig] = None,
        circuit_breaker: Optional[CircuitBreaker] = None
    ):
        self.error_handler = error_handler or ErrorHandler()
        self.retry_config = retry_config
        self.circuit_breaker = circuit_breaker

    def execute(
        self,
        func: Callable,
        *args,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Any:
        """
        安全執行函數

        Args:
            func: 要執行的函數
            context: 上下文信息
            *args, **kwargs: 函數參數

        Returns:
            執行結果
        """
        # 應用重試邏輯
        if self.retry_config:
            func = with_retry(self.retry_config)(func)

        # 應用斷路器
        if self.circuit_breaker:
            original_func = func

            def wrapped(*args, **kwargs):
                return self.circuit_breaker.call(original_func, *args, **kwargs)

            func = wrapped

        # 執行並處理錯誤
        try:
            return func(*args, **kwargs)

        except Exception as e:
            self.error_handler.handle_error(
                e,
                context=context,
                severity=ErrorSeverity.ERROR
            )
            raise


# ============================================================================
# 第七部分：錯誤恢復策略
# ============================================================================

class RecoveryAction(BaseModel):
    """恢復動作"""
    name: str = Field(..., description="動作名稱")
    description: str = Field(..., description="描述")
    action: Any = Field(..., description="恢復函數")

    class Config:
        arbitrary_types_allowed = True


class ErrorRecovery:
    """
    錯誤恢復管理器

    管理錯誤恢復策略。
    """

    def __init__(self):
        self.recovery_actions: Dict[type, List[RecoveryAction]] = {}

    def register_recovery(
        self,
        error_type: type,
        action: RecoveryAction
    ) -> None:
        """註冊恢復動作"""
        if error_type not in self.recovery_actions:
            self.recovery_actions[error_type] = []
        self.recovery_actions[error_type].append(action)

    def recover(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        嘗試從錯誤中恢復

        Args:
            error: 錯誤
            context: 上下文

        Returns:
            是否成功恢復
        """
        error_type = type(error)
        actions = self.recovery_actions.get(error_type, [])

        if not actions:
            print(f"沒有為 {error_type.__name__} 註冊的恢復動作")
            return False

        for action in actions:
            try:
                print(f"\n嘗試恢復動作: {action.name}")
                action.action(error, context)
                print(f"恢復成功: {action.name}")
                return True

            except Exception as e:
                print(f"恢復動作失敗: {str(e)}")

        return False


# ============================================================================
# 第八部分：使用示例
# ============================================================================

def example_error_hierarchy():
    """錯誤層次結構示例"""
    print("\n" + "="*60)
    print("示例 1: 錯誤層次結構")
    print("="*60)

    try:
        raise ValidationError(
            "輸入驗證失敗",
            error_code="VAL_001",
            details={'field': 'email', 'value': 'invalid'}
        )
    except AgentError as e:
        print(f"\n捕獲到錯誤:")
        print(f"  類型: {e.__class__.__name__}")
        print(f"  消息: {e.message}")
        print(f"  錯誤碼: {e.error_code}")
        print(f"  詳情: {e.details}")


def example_error_handler():
    """錯誤處理器示例"""
    print("\n" + "="*60)
    print("示例 2: 錯誤處理器")
    print("="*60)

    handler = ErrorHandler()

    # 註冊自定義處理器
    def handle_validation_error(error: ValidationError, record: ErrorRecord):
        print(f"自定義處理: {record.message}")

    handler.register_handler(ValidationError, handle_validation_error)

    # 處理錯誤
    try:
        raise ValidationError("測試錯誤")
    except Exception as e:
        handler.handle_error(
            e,
            context={'operation': 'test'},
            severity=ErrorSeverity.WARNING
        )

    # 查看錯誤記錄
    errors = handler.get_errors()
    print(f"\n記錄的錯誤數: {len(errors)}")


def example_retry_mechanism():
    """重試機制示例"""
    print("\n" + "="*60)
    print("示例 3: 重試機制")
    print("="*60)

    attempt_count = 0

    @with_retry(RetryConfig(max_attempts=3, initial_delay=0.5))
    def unstable_operation():
        nonlocal attempt_count
        attempt_count += 1
        print(f"執行操作（第 {attempt_count} 次）")

        if attempt_count < 3:
            raise RateLimitError("速率限制")

        return "成功"

    try:
        result = unstable_operation()
        print(f"\n最終結果: {result}")
    except Exception as e:
        print(f"\n操作失敗: {str(e)}")


def example_fallback_strategy():
    """降級策略示例"""
    print("\n" + "="*60)
    print("示例 4: 降級策略")
    print("="*60)

    def primary_service():
        raise ModelError("主要服務不可用")

    def backup_service():
        print("使用備份服務")
        return "備份結果"

    def cache_service():
        print("使用緩存")
        return "緩存結果"

    @with_fallback(backup_service, cache_service)
    def get_data():
        return primary_service()

    result = get_data()
    print(f"\n最終結果: {result}")


def example_circuit_breaker():
    """斷路器示例"""
    print("\n" + "="*60)
    print("示例 5: 斷路器模式")
    print("="*60)

    breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=5.0)

    def failing_operation():
        raise ExecutionError("操作失敗")

    # 模擬多次失敗
    for i in range(5):
        try:
            breaker.call(failing_operation)
        except Exception as e:
            print(f"嘗試 {i+1}: {e.message if isinstance(e, AgentError) else str(e)}")

    print(f"\n斷路器狀態: {breaker.state}")


def example_safe_executor():
    """安全執行器示例"""
    print("\n" + "="*60)
    print("示例 6: 安全執行器")
    print("="*60)

    executor = SafeExecutor(
        retry_config=RetryConfig(max_attempts=2, initial_delay=0.5)
    )

    count = 0

    def risky_operation():
        nonlocal count
        count += 1
        if count < 2:
            raise ToolError("工具執行失敗")
        return "成功"

    try:
        result = executor.execute(
            risky_operation,
            context={'operation': 'test'}
        )
        print(f"\n執行結果: {result}")
    except Exception as e:
        print(f"\n執行失敗: {str(e)}")


def main():
    """主函數"""
    print("\n" + "="*60)
    print("Atomic Agents 錯誤處理")
    print("="*60)

    # 運行示例
    example_error_hierarchy()
    example_error_handler()
    example_retry_mechanism()
    example_fallback_strategy()
    example_circuit_breaker()
    example_safe_executor()

    print("\n" + "="*60)
    print("所有示例運行完成！")
    print("="*60)


if __name__ == "__main__":
    main()

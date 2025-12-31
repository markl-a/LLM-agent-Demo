"""
Agent-S 錯誤恢復模組

此模組展示 Agent-S 的錯誤處理和恢復能力：
1. 錯誤檢測 - 及時發現執行過程中的錯誤
2. 錯誤分類 - 將錯誤分類為可恢復和不可恢復
3. 恢復策略 - 根據錯誤類型選擇恢復策略
4. 降級處理 - 在無法完全恢復時提供降級方案

Agent-S 使用多種策略來確保任務的魯棒性。
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Callable
from enum import Enum
from datetime import datetime
import time
import random


class ErrorType(Enum):
    """錯誤類型"""
    NETWORK_ERROR = "網絡錯誤"
    TIMEOUT = "超時"
    RESOURCE_NOT_FOUND = "資源未找到"
    PERMISSION_DENIED = "權限拒絕"
    INVALID_INPUT = "無效輸入"
    APPLICATION_ERROR = "應用程序錯誤"
    SYSTEM_ERROR = "系統錯誤"
    UNKNOWN = "未知錯誤"


class ErrorSeverity(Enum):
    """錯誤嚴重程度"""
    LOW = "低"
    MEDIUM = "中"
    HIGH = "高"
    CRITICAL = "嚴重"


class RecoveryStrategy(Enum):
    """恢復策略"""
    RETRY = "重試"
    ROLLBACK = "回滾"
    SKIP = "跳過"
    ALTERNATIVE = "替代方案"
    MANUAL_INTERVENTION = "人工介入"
    ABORT = "中止"


@dataclass
class ErrorInfo:
    """錯誤信息"""
    error_id: str
    error_type: ErrorType
    severity: ErrorSeverity
    message: str
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    stack_trace: Optional[str] = None

    def is_recoverable(self) -> bool:
        """判斷是否可恢復"""
        # 嚴重錯誤通常不可恢復
        if self.severity == ErrorSeverity.CRITICAL:
            return False

        # 某些類型的錯誤可以重試
        recoverable_types = [
            ErrorType.NETWORK_ERROR,
            ErrorType.TIMEOUT,
            ErrorType.RESOURCE_NOT_FOUND
        ]

        return self.error_type in recoverable_types


@dataclass
class RecoveryAction:
    """恢復操作"""
    action_id: str
    strategy: RecoveryStrategy
    description: str
    executor: Callable
    params: Dict[str, Any] = field(default_factory=dict)
    max_attempts: int = 3
    attempt_count: int = 0

    def execute(self, context: Dict[str, Any]) -> bool:
        """執行恢復操作"""
        self.attempt_count += 1

        print(f"\n執行恢復操作: {self.description}")
        print(f"策略: {self.strategy.value}")
        print(f"嘗試: {self.attempt_count}/{self.max_attempts}")

        try:
            result = self.executor(context, **self.params)
            return result
        except Exception as e:
            print(f"恢復失敗: {e}")
            return False


class ErrorDetector:
    """
    錯誤檢測器

    檢測和分類執行過程中的錯誤
    """

    def __init__(self):
        self.detected_errors: List[ErrorInfo] = []

    def detect(self, exception: Exception, context: Dict[str, Any]) -> ErrorInfo:
        """檢測並分類錯誤"""
        print(f"\n檢測到錯誤: {exception}")

        # 分析錯誤類型
        error_type = self._classify_error(exception)
        severity = self._assess_severity(error_type, context)

        error_info = ErrorInfo(
            error_id=f"ERR_{len(self.detected_errors) + 1}",
            error_type=error_type,
            severity=severity,
            message=str(exception),
            context=context.copy()
        )

        self.detected_errors.append(error_info)

        print(f"錯誤類型: {error_type.value}")
        print(f"嚴重程度: {severity.value}")
        print(f"可恢復: {'是' if error_info.is_recoverable() else '否'}")

        return error_info

    def _classify_error(self, exception: Exception) -> ErrorType:
        """分類錯誤"""
        error_msg = str(exception).lower()

        if "network" in error_msg or "connection" in error_msg:
            return ErrorType.NETWORK_ERROR
        elif "timeout" in error_msg:
            return ErrorType.TIMEOUT
        elif "not found" in error_msg:
            return ErrorType.RESOURCE_NOT_FOUND
        elif "permission" in error_msg or "denied" in error_msg:
            return ErrorType.PERMISSION_DENIED
        elif "invalid" in error_msg:
            return ErrorType.INVALID_INPUT
        else:
            return ErrorType.UNKNOWN

    def _assess_severity(self, error_type: ErrorType, context: Dict[str, Any]) -> ErrorSeverity:
        """評估錯誤嚴重程度"""
        # 某些錯誤類型天生更嚴重
        if error_type in [ErrorType.SYSTEM_ERROR, ErrorType.PERMISSION_DENIED]:
            return ErrorSeverity.HIGH

        # 考慮上下文
        if context.get("critical_operation"):
            return ErrorSeverity.HIGH

        if error_type in [ErrorType.NETWORK_ERROR, ErrorType.TIMEOUT]:
            return ErrorSeverity.MEDIUM

        return ErrorSeverity.LOW


class RecoveryPlanner:
    """
    恢復規劃器

    根據錯誤類型制定恢復計劃
    """

    def __init__(self):
        self.recovery_rules: Dict[ErrorType, List[RecoveryStrategy]] = {
            ErrorType.NETWORK_ERROR: [
                RecoveryStrategy.RETRY,
                RecoveryStrategy.ALTERNATIVE
            ],
            ErrorType.TIMEOUT: [
                RecoveryStrategy.RETRY,
                RecoveryStrategy.SKIP
            ],
            ErrorType.RESOURCE_NOT_FOUND: [
                RecoveryStrategy.ALTERNATIVE,
                RecoveryStrategy.SKIP
            ],
            ErrorType.PERMISSION_DENIED: [
                RecoveryStrategy.MANUAL_INTERVENTION,
                RecoveryStrategy.ABORT
            ],
            ErrorType.INVALID_INPUT: [
                RecoveryStrategy.ROLLBACK,
                RecoveryStrategy.MANUAL_INTERVENTION
            ],
        }

    def plan_recovery(self, error: ErrorInfo) -> List[RecoveryAction]:
        """制定恢復計劃"""
        print(f"\n制定恢復計劃: {error.error_id}")

        if not error.is_recoverable():
            print("錯誤不可恢復")
            return [self._create_abort_action()]

        # 獲取適用的恢復策略
        strategies = self.recovery_rules.get(error.error_type, [RecoveryStrategy.RETRY])

        actions = []
        for strategy in strategies:
            action = self._create_recovery_action(strategy, error)
            if action:
                actions.append(action)

        print(f"生成 {len(actions)} 個恢復操作")
        for i, action in enumerate(actions, 1):
            print(f"  {i}. {action.strategy.value}: {action.description}")

        return actions

    def _create_recovery_action(self, strategy: RecoveryStrategy, error: ErrorInfo) -> Optional[RecoveryAction]:
        """創建恢復操作"""
        if strategy == RecoveryStrategy.RETRY:
            return RecoveryAction(
                action_id=f"recovery_{error.error_id}_retry",
                strategy=strategy,
                description="重試失敗的操作",
                executor=self._retry_executor,
                params={"delay": 1.0, "backoff": 2.0}
            )

        elif strategy == RecoveryStrategy.ROLLBACK:
            return RecoveryAction(
                action_id=f"recovery_{error.error_id}_rollback",
                strategy=strategy,
                description="回滾到之前的狀態",
                executor=self._rollback_executor
            )

        elif strategy == RecoveryStrategy.SKIP:
            return RecoveryAction(
                action_id=f"recovery_{error.error_id}_skip",
                strategy=strategy,
                description="跳過當前操作",
                executor=self._skip_executor
            )

        elif strategy == RecoveryStrategy.ALTERNATIVE:
            return RecoveryAction(
                action_id=f"recovery_{error.error_id}_alt",
                strategy=strategy,
                description="使用替代方案",
                executor=self._alternative_executor
            )

        return None

    def _create_abort_action(self) -> RecoveryAction:
        """創建中止操作"""
        return RecoveryAction(
            action_id="abort",
            strategy=RecoveryStrategy.ABORT,
            description="中止任務執行",
            executor=lambda ctx: False
        )

    # ========== 恢復執行器 ==========

    def _retry_executor(self, context: Dict[str, Any], delay: float = 1.0, backoff: float = 2.0) -> bool:
        """重試執行器"""
        print(f"  等待 {delay:.1f} 秒後重試...")
        time.sleep(delay)

        # 模擬重試（這裡簡單返回成功）
        success = random.random() > 0.3  # 70% 成功率

        if success:
            print("  ✓ 重試成功")
        else:
            print("  ✗ 重試失敗")

        return success

    def _rollback_executor(self, context: Dict[str, Any]) -> bool:
        """回滾執行器"""
        print("  執行回滾...")
        time.sleep(0.3)

        # 模擬回滾操作
        if "checkpoint" in context:
            print(f"  恢復到檢查點: {context['checkpoint']}")
            return True

        print("  沒有可用的檢查點")
        return False

    def _skip_executor(self, context: Dict[str, Any]) -> bool:
        """跳過執行器"""
        print("  跳過當前操作")
        context["skipped"] = True
        return True

    def _alternative_executor(self, context: Dict[str, Any]) -> bool:
        """替代方案執行器"""
        print("  嘗試替代方案...")
        time.sleep(0.2)

        # 模擬使用替代方法
        alternative_available = random.random() > 0.4  # 60% 有替代方案

        if alternative_available:
            print("  ✓ 使用替代方案成功")
            return True
        else:
            print("  ✗ 沒有可用的替代方案")
            return False


class ResilientExecutor:
    """
    魯棒執行器

    集成錯誤檢測和恢復功能的執行器
    """

    def __init__(self):
        self.detector = ErrorDetector()
        self.planner = RecoveryPlanner()
        self.execution_log: List[Dict[str, Any]] = []

    def execute_with_recovery(self, operation: Callable, context: Dict[str, Any], operation_name: str = "操作") -> Any:
        """
        執行操作並處理錯誤

        Args:
            operation: 要執行的操作
            context: 執行上下文
            operation_name: 操作名稱

        Returns:
            操作結果
        """
        print(f"\n{'='*60}")
        print(f"執行: {operation_name}")
        print(f"{'='*60}")

        attempt = 0
        max_attempts = 3

        while attempt < max_attempts:
            attempt += 1
            print(f"\n嘗試 {attempt}/{max_attempts}")

            try:
                # 執行操作
                result = operation(context)

                # 記錄成功
                self._log_execution(operation_name, True, attempt)

                print(f"\n✓ {operation_name} 執行成功")
                return result

            except Exception as e:
                # 檢測錯誤
                error = self.detector.detect(e, context)

                # 記錄失敗
                self._log_execution(operation_name, False, attempt, error)

                # 制定恢復計劃
                recovery_actions = self.planner.plan_recovery(error)

                # 執行恢復操作
                recovered = False
                for action in recovery_actions:
                    if action.strategy == RecoveryStrategy.ABORT:
                        print(f"\n❌ {operation_name} 失敗，無法恢復")
                        raise

                    if action.execute(context):
                        recovered = True
                        break

                if not recovered:
                    if attempt >= max_attempts:
                        print(f"\n❌ {operation_name} 失敗，已達最大重試次數")
                        raise

                    print(f"\n恢復失敗，準備下一次嘗試...")

        raise Exception(f"{operation_name} 失敗")

    def _log_execution(self, operation_name: str, success: bool, attempt: int, error: Optional[ErrorInfo] = None):
        """記錄執行歷史"""
        log_entry = {
            "operation": operation_name,
            "success": success,
            "attempt": attempt,
            "timestamp": datetime.now().isoformat()
        }

        if error:
            log_entry["error"] = {
                "type": error.error_type.value,
                "severity": error.severity.value,
                "message": error.message
            }

        self.execution_log.append(log_entry)

    def get_statistics(self) -> Dict[str, Any]:
        """獲取執行統計"""
        total = len(self.execution_log)
        if total == 0:
            return {}

        successful = sum(1 for log in self.execution_log if log["success"])
        failed = total - successful

        errors_by_type = {}
        for log in self.execution_log:
            if "error" in log:
                error_type = log["error"]["type"]
                errors_by_type[error_type] = errors_by_type.get(error_type, 0) + 1

        return {
            "總執行次數": total,
            "成功次數": successful,
            "失敗次數": failed,
            "成功率": f"{successful/total:.1%}",
            "錯誤分布": errors_by_type
        }


class CircuitBreaker:
    """
    斷路器

    防止持續失敗的操作浪費資源
    """

    def __init__(self, failure_threshold: int = 5, timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def call(self, operation: Callable, *args, **kwargs) -> Any:
        """通過斷路器調用操作"""
        if self.state == "OPEN":
            # 檢查是否應該嘗試恢復
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
                print("斷路器進入半開狀態，嘗試恢復")
            else:
                raise Exception("斷路器已打開，拒絕執行")

        try:
            result = operation(*args, **kwargs)

            # 成功則重置
            if self.state == "HALF_OPEN":
                self._reset()
                print("斷路器已重置")

            return result

        except Exception as e:
            self._record_failure()
            raise

    def _record_failure(self):
        """記錄失敗"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            print(f"⚠️  斷路器已打開（失敗次數: {self.failure_count}）")

    def _should_attempt_reset(self) -> bool:
        """檢查是否應該嘗試重置"""
        if not self.last_failure_time:
            return True

        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return elapsed >= self.timeout

    def _reset(self):
        """重置斷路器"""
        self.failure_count = 0
        self.state = "CLOSED"
        self.last_failure_time = None


# ========== 模擬操作（用於演示）==========

def 不穩定的網絡操作(context: Dict[str, Any]) -> str:
    """模擬不穩定的網絡操作"""
    print("  執行網絡請求...")
    time.sleep(0.2)

    # 30% 概率失敗
    if random.random() < 0.3:
        raise Exception("Network connection failed")

    return "數據已下載"


def 可能超時的操作(context: Dict[str, Any]) -> str:
    """模擬可能超時的操作"""
    print("  執行耗時操作...")
    time.sleep(0.3)

    # 40% 概率超時
    if random.random() < 0.4:
        raise Exception("Operation timeout")

    return "操作完成"


def 資源查找操作(context: Dict[str, Any]) -> str:
    """模擬資源查找"""
    print("  查找資源...")
    time.sleep(0.2)

    # 50% 概率找不到
    if random.random() < 0.5:
        raise Exception("Resource not found")

    return "資源已找到"


def 示例1_基本錯誤恢復():
    """示例：基本錯誤檢測和恢復"""
    print("\n" + "="*60)
    print("示例 1: 基本錯誤恢復")
    print("="*60)

    executor = ResilientExecutor()
    context = {}

    # 執行不穩定的操作
    try:
        result = executor.execute_with_recovery(
            不穩定的網絡操作,
            context,
            "網絡請求"
        )
        print(f"\n最終結果: {result}")
    except Exception as e:
        print(f"\n最終失敗: {e}")

    return executor


def 示例2_多次重試():
    """示例：多次重試機制"""
    print("\n" + "="*60)
    print("示例 2: 多次重試")
    print("="*60)

    executor = ResilientExecutor()
    context = {}

    try:
        result = executor.execute_with_recovery(
            可能超時的操作,
            context,
            "耗時操作"
        )
        print(f"\n最終結果: {result}")
    except Exception as e:
        print(f"\n最終失敗: {e}")

    return executor


def 示例3_替代方案():
    """示例：使用替代方案"""
    print("\n" + "="*60)
    print("示例 3: 替代方案")
    print("="*60)

    executor = ResilientExecutor()
    context = {}

    try:
        result = executor.execute_with_recovery(
            資源查找操作,
            context,
            "資源查找"
        )
        print(f"\n最終結果: {result}")
    except Exception as e:
        print(f"\n最終失敗: {e}")

    return executor


def 示例4_斷路器():
    """示例：使用斷路器"""
    print("\n" + "="*60)
    print("示例 4: 斷路器模式")
    print("="*60)

    breaker = CircuitBreaker(failure_threshold=3, timeout=2.0)

    def 總是失敗的操作():
        raise Exception("Operation failed")

    # 多次調用直到斷路器打開
    for i in range(6):
        print(f"\n嘗試 {i+1}:")
        try:
            breaker.call(總是失敗的操作)
        except Exception as e:
            print(f"  錯誤: {e}")

        time.sleep(0.3)

    print(f"\n斷路器狀態: {breaker.state}")
    print(f"失敗次數: {breaker.failure_count}")

    return breaker


def 示例5_執行統計():
    """示例：查看執行統計"""
    print("\n" + "="*60)
    print("示例 5: 執行統計")
    print("="*60)

    executor = ResilientExecutor()
    context = {}

    # 執行多個操作
    operations = [
        (不穩定的網絡操作, "網絡請求1"),
        (可能超時的操作, "耗時操作1"),
        (資源查找操作, "資源查找1"),
        (不穩定的網絡操作, "網絡請求2"),
    ]

    for operation, name in operations:
        try:
            executor.execute_with_recovery(operation, context, name)
        except:
            pass  # 忽略失敗

    # 顯示統計
    print("\n" + "="*60)
    print("執行統計")
    print("="*60)

    stats = executor.get_statistics()
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"\n{key}:")
            for k, v in value.items():
                print(f"  {k}: {v}")
        else:
            print(f"{key}: {value}")

    return executor


if __name__ == "__main__":
    print("Agent-S 錯誤恢復演示\n")

    示例1_基本錯誤恢復()
    示例2_多次重試()
    示例3_替代方案()
    示例4_斷路器()
    示例5_執行統計()

    print("\n所有示例執行完成！")

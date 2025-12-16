"""
LangChain 錯誤恢復範例
=====================

本範例展示如何在 LangChain 中處理錯誤和實現恢復機制。

錯誤處理類型：
1. 重試機制
2. 回退策略
3. 斷路器
4. 錯誤日誌

安裝依賴：
pip install langchain langchain-openai tenacity
"""

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass, field
from functools import wraps
import time
from datetime import datetime
import random

# ============================================================
# 1. 基本重試機制
# ============================================================

def retry_with_exponential_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0
):
    """指數退避重試裝飾器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        delay = min(base_delay * (2 ** attempt), max_delay)
                        delay += random.uniform(0, delay * 0.1)  # 抖動
                        print(f"重試 {attempt + 1}/{max_retries}，等待 {delay:.2f}s")
                        time.sleep(delay)

            raise last_exception

        return wrapper
    return decorator


RETRY_EXAMPLE = '''
from langchain_openai import ChatOpenAI

@retry_with_exponential_backoff(max_retries=3)
def call_llm(prompt: str) -> str:
    llm = ChatOpenAI()
    return llm.invoke(prompt).content

# 使用
try:
    result = call_llm("Hello!")
except Exception as e:
    print(f"最終失敗: {e}")
'''


# ============================================================
# 2. LangChain 內置重試
# ============================================================

LANGCHAIN_RETRY_EXAMPLE = '''
from langchain_openai import ChatOpenAI

# 方法 1: 使用 with_retry
llm = ChatOpenAI().with_retry(
    stop_after_attempt=3,
    wait_exponential_jitter=True
)

# 方法 2: 配置重試
llm = ChatOpenAI(
    max_retries=3,
    request_timeout=30
)

# 使用
response = llm.invoke("Hello!")
'''


# ============================================================
# 3. 回退策略
# ============================================================

@dataclass
class FallbackConfig:
    """回退配置"""
    primary: Callable
    fallbacks: List[Callable]
    max_retries: int = 2


class FallbackHandler:
    """回退處理器"""

    def __init__(self, config: FallbackConfig):
        self.config = config
        self.failure_counts: Dict[str, int] = {}

    def execute(self, *args, **kwargs) -> Any:
        """執行並處理回退"""
        all_handlers = [self.config.primary] + self.config.fallbacks

        for i, handler in enumerate(all_handlers):
            handler_name = handler.__name__ if hasattr(handler, '__name__') else f"handler_{i}"

            for attempt in range(self.config.max_retries):
                try:
                    result = handler(*args, **kwargs)
                    self.failure_counts[handler_name] = 0
                    return result
                except Exception as e:
                    self.failure_counts[handler_name] = self.failure_counts.get(handler_name, 0) + 1
                    print(f"{handler_name} 失敗 (嘗試 {attempt + 1}): {e}")

            print(f"切換到下一個處理器")

        raise Exception("所有處理器都失敗了")


FALLBACK_EXAMPLE = '''
# 回退策略使用

def primary_handler(text):
    # 主處理器
    llm = ChatOpenAI(model="gpt-4")
    return llm.invoke(text).content

def fallback_handler_1(text):
    # 回退處理器 1
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    return llm.invoke(text).content

def fallback_handler_2(text):
    # 回退處理器 2 (本地模型)
    return f"[本地處理] {text}"

config = FallbackConfig(
    primary=primary_handler,
    fallbacks=[fallback_handler_1, fallback_handler_2],
    max_retries=2
)

handler = FallbackHandler(config)
result = handler.execute("Hello!")
'''


# ============================================================
# 4. 斷路器模式
# ============================================================

@dataclass
class CircuitBreakerState:
    """斷路器狀態"""
    failure_count: int = 0
    last_failure_time: Optional[float] = None
    state: str = "closed"  # closed, open, half_open


class CircuitBreaker:
    """斷路器"""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        half_open_requests: int = 3
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_requests = half_open_requests
        self.state = CircuitBreakerState()

    def _should_attempt(self) -> bool:
        """檢查是否應該嘗試"""
        if self.state.state == "closed":
            return True

        if self.state.state == "open":
            # 檢查是否應該進入半開狀態
            if self.state.last_failure_time:
                elapsed = time.time() - self.state.last_failure_time
                if elapsed >= self.recovery_timeout:
                    self.state.state = "half_open"
                    self.state.failure_count = 0
                    return True
            return False

        if self.state.state == "half_open":
            return self.state.failure_count < self.half_open_requests

        return False

    def _record_success(self):
        """記錄成功"""
        if self.state.state == "half_open":
            self.state.state = "closed"
        self.state.failure_count = 0

    def _record_failure(self):
        """記錄失敗"""
        self.state.failure_count += 1
        self.state.last_failure_time = time.time()

        if self.state.failure_count >= self.failure_threshold:
            self.state.state = "open"

    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """執行並處理斷路"""
        if not self._should_attempt():
            raise Exception(f"斷路器開啟，狀態: {self.state.state}")

        try:
            result = func(*args, **kwargs)
            self._record_success()
            return result
        except Exception as e:
            self._record_failure()
            raise


CIRCUIT_BREAKER_EXAMPLE = '''
# 斷路器使用

breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=30.0
)

def call_api(text):
    llm = ChatOpenAI()
    return llm.invoke(text).content

# 使用斷路器
try:
    result = breaker.execute(call_api, "Hello!")
except Exception as e:
    print(f"調用失敗: {e}")
    print(f"斷路器狀態: {breaker.state.state}")
'''


# ============================================================
# 5. 錯誤日誌和監控
# ============================================================

@dataclass
class ErrorEvent:
    """錯誤事件"""
    timestamp: datetime
    error_type: str
    error_message: str
    context: Dict[str, Any]
    recovered: bool = False


class ErrorMonitor:
    """錯誤監控器"""

    def __init__(self, max_events: int = 1000):
        self.events: List[ErrorEvent] = []
        self.max_events = max_events

    def log_error(
        self,
        error: Exception,
        context: Dict[str, Any] = None,
        recovered: bool = False
    ):
        """記錄錯誤"""
        event = ErrorEvent(
            timestamp=datetime.now(),
            error_type=type(error).__name__,
            error_message=str(error),
            context=context or {},
            recovered=recovered
        )

        self.events.append(event)

        # 限制事件數量
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events:]

    def get_stats(self) -> Dict[str, Any]:
        """獲取統計信息"""
        if not self.events:
            return {"total_errors": 0}

        by_type = {}
        recovered_count = 0

        for event in self.events:
            by_type[event.error_type] = by_type.get(event.error_type, 0) + 1
            if event.recovered:
                recovered_count += 1

        return {
            "total_errors": len(self.events),
            "by_type": by_type,
            "recovered": recovered_count,
            "recovery_rate": recovered_count / len(self.events) if self.events else 0
        }


# ============================================================
# 6. 組合錯誤處理
# ============================================================

class ResilientExecutor:
    """彈性執行器"""

    def __init__(
        self,
        max_retries: int = 3,
        fallback_handlers: List[Callable] = None,
        circuit_breaker: CircuitBreaker = None
    ):
        self.max_retries = max_retries
        self.fallback_handlers = fallback_handlers or []
        self.circuit_breaker = circuit_breaker or CircuitBreaker()
        self.monitor = ErrorMonitor()

    def execute(self, primary_handler: Callable, *args, **kwargs) -> Any:
        """彈性執行"""
        all_handlers = [primary_handler] + self.fallback_handlers

        for handler in all_handlers:
            for attempt in range(self.max_retries):
                try:
                    # 使用斷路器
                    result = self.circuit_breaker.execute(handler, *args, **kwargs)
                    return result

                except Exception as e:
                    self.monitor.log_error(
                        error=e,
                        context={
                            "handler": handler.__name__ if hasattr(handler, '__name__') else str(handler),
                            "attempt": attempt + 1,
                            "args": str(args)[:100]
                        },
                        recovered=False
                    )

                    if attempt < self.max_retries - 1:
                        time.sleep(1 * (attempt + 1))

        raise Exception("所有嘗試都失敗了")

    def get_status(self) -> Dict[str, Any]:
        """獲取狀態"""
        return {
            "circuit_breaker": self.circuit_breaker.state.state,
            "error_stats": self.monitor.get_stats()
        }


RESILIENT_EXAMPLE = '''
# 組合錯誤處理

executor = ResilientExecutor(
    max_retries=3,
    fallback_handlers=[fallback_handler_1, fallback_handler_2]
)

try:
    result = executor.execute(primary_handler, "Hello!")
except Exception as e:
    print(f"最終失敗: {e}")

# 查看狀態
status = executor.get_status()
print(f"斷路器狀態: {status['circuit_breaker']}")
print(f"錯誤統計: {status['error_stats']}")
'''


# ============================================================
# 7. LangChain 回退鏈
# ============================================================

LANGCHAIN_FALLBACK_EXAMPLE = '''
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableWithFallbacks

# 主模型
primary = ChatOpenAI(model="gpt-4")

# 回退模型
fallback = ChatOpenAI(model="gpt-3.5-turbo")

# 創建帶回退的鏈
chain = primary.with_fallbacks([fallback])

# 使用
response = chain.invoke("Hello!")
'''


# ============================================================
# 使用範例
# ============================================================

def example_basic_retry():
    """範例 1: 基本重試"""
    print("=" * 50)
    print("範例 1: 基本重試機制")
    print("=" * 50)
    print(RETRY_EXAMPLE)


def example_langchain_retry():
    """範例 2: LangChain 重試"""
    print("\n" + "=" * 50)
    print("範例 2: LangChain 內置重試")
    print("=" * 50)
    print(LANGCHAIN_RETRY_EXAMPLE)


def example_fallback():
    """範例 3: 回退策略"""
    print("\n" + "=" * 50)
    print("範例 3: 回退策略")
    print("=" * 50)
    print(FALLBACK_EXAMPLE)


def example_circuit_breaker():
    """範例 4: 斷路器"""
    print("\n" + "=" * 50)
    print("範例 4: 斷路器模式")
    print("=" * 50)
    print(CIRCUIT_BREAKER_EXAMPLE)


def example_monitoring():
    """範例 5: 錯誤監控"""
    print("\n" + "=" * 50)
    print("範例 5: 錯誤監控")
    print("=" * 50)

    monitor = ErrorMonitor()

    # 模擬錯誤
    monitor.log_error(ValueError("測試錯誤 1"), {"action": "test"}, recovered=True)
    monitor.log_error(TimeoutError("超時"), {"action": "api_call"}, recovered=False)
    monitor.log_error(ValueError("測試錯誤 2"), {"action": "test"}, recovered=True)

    stats = monitor.get_stats()
    print(f"錯誤統計: {stats}")


def example_resilient():
    """範例 6: 彈性執行器"""
    print("\n" + "=" * 50)
    print("範例 6: 組合錯誤處理")
    print("=" * 50)
    print(RESILIENT_EXAMPLE)


def example_langchain_fallback():
    """範例 7: LangChain 回退鏈"""
    print("\n" + "=" * 50)
    print("範例 7: LangChain 回退鏈")
    print("=" * 50)
    print(LANGCHAIN_FALLBACK_EXAMPLE)


if __name__ == "__main__":
    print("LangChain 錯誤恢復範例\n")
    example_basic_retry()
    example_langchain_retry()
    example_fallback()
    example_circuit_breaker()
    example_monitoring()
    example_resilient()
    example_langchain_fallback()

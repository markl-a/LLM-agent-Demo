"""
LiteLLM 錯誤處理範例
===================

本範例展示如何在 LiteLLM 中處理各種錯誤。

錯誤類型：
1. API 錯誤
2. 速率限制
3. 超時錯誤
4. 模型錯誤

安裝依賴：
pip install litellm tenacity
"""

import litellm
from litellm import completion
from litellm.exceptions import (
    AuthenticationError,
    RateLimitError,
    ServiceUnavailableError,
    Timeout,
    APIError,
    BadRequestError,
    ContextWindowExceededError
)
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
import time
import random
from functools import wraps

# ============================================================
# 1. 基本錯誤處理
# ============================================================

def basic_error_handling():
    """基本錯誤處理示例"""
    try:
        response = completion(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}]
        )
        return response
    except AuthenticationError as e:
        print(f"認證錯誤: {e}")
        # 處理 API 密鑰問題
    except RateLimitError as e:
        print(f"速率限制: {e}")
        # 等待後重試
    except Timeout as e:
        print(f"請求超時: {e}")
        # 重試或使用備用模型
    except ServiceUnavailableError as e:
        print(f"服務不可用: {e}")
        # 切換到備用服務
    except BadRequestError as e:
        print(f"錯誤請求: {e}")
        # 檢查請求參數
    except ContextWindowExceededError as e:
        print(f"上下文超出限制: {e}")
        # 減少輸入長度
    except APIError as e:
        print(f"API 錯誤: {e}")
        # 通用 API 錯誤處理
    except Exception as e:
        print(f"未知錯誤: {e}")


# ============================================================
# 2. 重試機制
# ============================================================

def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0
):
    """帶指數退避的重試裝飾器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (RateLimitError, ServiceUnavailableError, Timeout) as e:
                    last_exception = e

                    if attempt < max_retries - 1:
                        # 計算延遲時間
                        delay = min(
                            base_delay * (exponential_base ** attempt),
                            max_delay
                        )
                        # 添加抖動
                        delay = delay * (0.5 + random.random())

                        print(f"嘗試 {attempt + 1} 失敗，{delay:.2f} 秒後重試...")
                        time.sleep(delay)

            raise last_exception

        return wrapper
    return decorator


@retry_with_backoff(max_retries=3, base_delay=1.0)
def completion_with_retry(model: str, messages: List[Dict], **kwargs):
    """帶重試的完成調用"""
    return completion(model=model, messages=messages, **kwargs)


# ============================================================
# 3. 錯誤回退策略
# ============================================================

@dataclass
class FallbackConfig:
    """回退配置"""
    primary_model: str
    fallback_models: List[str]
    max_retries: int = 2


class FallbackHandler:
    """回退處理器"""

    def __init__(self, config: FallbackConfig):
        self.config = config
        self.model_failures: Dict[str, int] = {}

    def _should_skip_model(self, model: str) -> bool:
        """檢查是否應跳過模型"""
        failures = self.model_failures.get(model, 0)
        return failures >= 3  # 連續失敗 3 次則跳過

    def _record_failure(self, model: str):
        """記錄失敗"""
        self.model_failures[model] = self.model_failures.get(model, 0) + 1

    def _record_success(self, model: str):
        """記錄成功"""
        self.model_failures[model] = 0

    def completion(self, messages: List[Dict], **kwargs) -> Any:
        """帶回退的完成調用"""
        all_models = [self.config.primary_model] + self.config.fallback_models
        last_error = None

        for model in all_models:
            if self._should_skip_model(model):
                print(f"跳過模型 {model}（連續失敗過多）")
                continue

            for attempt in range(self.config.max_retries):
                try:
                    response = completion(
                        model=model,
                        messages=messages,
                        **kwargs
                    )
                    self._record_success(model)
                    return response, model
                except (RateLimitError, ServiceUnavailableError, Timeout) as e:
                    last_error = e
                    print(f"模型 {model} 嘗試 {attempt + 1} 失敗: {e}")
                    time.sleep(1 * (attempt + 1))
                except Exception as e:
                    last_error = e
                    self._record_failure(model)
                    break  # 其他錯誤直接切換模型

        raise Exception(f"所有模型都失敗了。最後錯誤: {last_error}")


# ============================================================
# 4. 速率限制處理
# ============================================================

class RateLimiter:
    """速率限制器"""

    def __init__(
        self,
        requests_per_minute: int = 60,
        tokens_per_minute: int = 90000
    ):
        self.rpm = requests_per_minute
        self.tpm = tokens_per_minute
        self.request_times: List[float] = []
        self.token_counts: List[tuple] = []  # (timestamp, count)

    def _clean_old_entries(self):
        """清理舊條目"""
        now = time.time()
        cutoff = now - 60  # 1 分鐘窗口

        self.request_times = [t for t in self.request_times if t > cutoff]
        self.token_counts = [(t, c) for t, c in self.token_counts if t > cutoff]

    def can_make_request(self, estimated_tokens: int = 1000) -> bool:
        """檢查是否可以發送請求"""
        self._clean_old_entries()

        # 檢查 RPM
        if len(self.request_times) >= self.rpm:
            return False

        # 檢查 TPM
        current_tokens = sum(c for _, c in self.token_counts)
        if current_tokens + estimated_tokens > self.tpm:
            return False

        return True

    def wait_if_needed(self, estimated_tokens: int = 1000):
        """必要時等待"""
        while not self.can_make_request(estimated_tokens):
            self._clean_old_entries()
            if self.request_times:
                # 等待最舊的請求過期
                wait_time = 60 - (time.time() - self.request_times[0])
                if wait_time > 0:
                    print(f"速率限制，等待 {wait_time:.2f} 秒...")
                    time.sleep(wait_time)
            else:
                time.sleep(1)

    def record_request(self, tokens_used: int):
        """記錄請求"""
        now = time.time()
        self.request_times.append(now)
        self.token_counts.append((now, tokens_used))


class RateLimitedClient:
    """帶速率限制的客戶端"""

    def __init__(self, rpm: int = 60, tpm: int = 90000):
        self.limiter = RateLimiter(rpm, tpm)

    def completion(
        self,
        model: str,
        messages: List[Dict],
        estimated_tokens: int = 1000,
        **kwargs
    ):
        """帶速率限制的完成調用"""
        self.limiter.wait_if_needed(estimated_tokens)

        response = completion(model=model, messages=messages, **kwargs)

        # 記錄使用的 tokens
        tokens_used = response.usage.total_tokens if response.usage else estimated_tokens
        self.limiter.record_request(tokens_used)

        return response


# ============================================================
# 5. 錯誤日誌和監控
# ============================================================

@dataclass
class ErrorEvent:
    """錯誤事件"""
    timestamp: float
    model: str
    error_type: str
    error_message: str
    request_id: Optional[str] = None


class ErrorMonitor:
    """錯誤監控器"""

    def __init__(self, max_events: int = 1000):
        self.events: List[ErrorEvent] = []
        self.max_events = max_events

    def log_error(
        self,
        model: str,
        error: Exception,
        request_id: Optional[str] = None
    ):
        """記錄錯誤"""
        event = ErrorEvent(
            timestamp=time.time(),
            model=model,
            error_type=type(error).__name__,
            error_message=str(error),
            request_id=request_id
        )

        self.events.append(event)

        # 限制事件數量
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events:]

    def get_error_stats(self) -> Dict[str, Any]:
        """獲取錯誤統計"""
        if not self.events:
            return {"total_errors": 0}

        by_type = {}
        by_model = {}

        for event in self.events:
            by_type[event.error_type] = by_type.get(event.error_type, 0) + 1
            by_model[event.model] = by_model.get(event.model, 0) + 1

        return {
            "total_errors": len(self.events),
            "by_type": by_type,
            "by_model": by_model,
            "recent_errors": len([e for e in self.events if time.time() - e.timestamp < 300])
        }

    def get_recent_errors(self, minutes: int = 5) -> List[ErrorEvent]:
        """獲取最近的錯誤"""
        cutoff = time.time() - (minutes * 60)
        return [e for e in self.events if e.timestamp > cutoff]


# ============================================================
# 6. 綜合錯誤處理客戶端
# ============================================================

class RobustLLMClient:
    """健壯的 LLM 客戶端"""

    def __init__(
        self,
        primary_model: str = "gpt-3.5-turbo",
        fallback_models: List[str] = None,
        rpm: int = 60,
        tpm: int = 90000
    ):
        self.fallback_handler = FallbackHandler(
            FallbackConfig(
                primary_model=primary_model,
                fallback_models=fallback_models or []
            )
        )
        self.rate_limiter = RateLimiter(rpm, tpm)
        self.error_monitor = ErrorMonitor()

    def completion(self, messages: List[Dict], **kwargs) -> Any:
        """健壯的完成調用"""
        # 速率限制
        self.rate_limiter.wait_if_needed()

        try:
            response, model_used = self.fallback_handler.completion(
                messages=messages,
                **kwargs
            )

            # 記錄使用
            tokens = response.usage.total_tokens if response.usage else 1000
            self.rate_limiter.record_request(tokens)

            return response

        except Exception as e:
            self.error_monitor.log_error(
                model=kwargs.get('model', 'unknown'),
                error=e
            )
            raise

    def get_stats(self) -> Dict[str, Any]:
        """獲取統計信息"""
        return {
            "errors": self.error_monitor.get_error_stats(),
            "model_failures": self.fallback_handler.model_failures
        }


# ============================================================
# 使用範例
# ============================================================

def example_basic_handling():
    """範例 1: 基本錯誤處理"""
    print("=" * 50)
    print("範例 1: 基本錯誤處理")
    print("=" * 50)

    print("""
try:
    response = completion(model="gpt-3.5-turbo", messages=[...])
except AuthenticationError:
    # API 密鑰問題
    pass
except RateLimitError:
    # 達到速率限制
    pass
except Timeout:
    # 請求超時
    pass
except ContextWindowExceededError:
    # 輸入過長
    pass
except APIError as e:
    # 其他 API 錯誤
    print(f"錯誤: {e}")
""")


def example_retry():
    """範例 2: 重試機制"""
    print("\n" + "=" * 50)
    print("範例 2: 重試機制")
    print("=" * 50)

    print("""
@retry_with_backoff(max_retries=3, base_delay=1.0)
def completion_with_retry(model, messages, **kwargs):
    return completion(model=model, messages=messages, **kwargs)

# 使用
response = completion_with_retry(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello"}]
)
""")


def example_fallback():
    """範例 3: 回退策略"""
    print("\n" + "=" * 50)
    print("範例 3: 回退策略")
    print("=" * 50)

    config = FallbackConfig(
        primary_model="gpt-4",
        fallback_models=["gpt-3.5-turbo", "claude-3-sonnet"],
        max_retries=2
    )

    handler = FallbackHandler(config)
    print(f"主模型: {config.primary_model}")
    print(f"備用模型: {config.fallback_models}")


def example_rate_limiting():
    """範例 4: 速率限制"""
    print("\n" + "=" * 50)
    print("範例 4: 速率限制")
    print("=" * 50)

    limiter = RateLimiter(requests_per_minute=60, tokens_per_minute=90000)

    # 模擬請求
    for i in range(5):
        if limiter.can_make_request(1000):
            print(f"請求 {i+1}: 可以發送")
            limiter.record_request(1000)
        else:
            print(f"請求 {i+1}: 需要等待")


def example_error_monitor():
    """範例 5: 錯誤監控"""
    print("\n" + "=" * 50)
    print("範例 5: 錯誤監控")
    print("=" * 50)

    monitor = ErrorMonitor()

    # 模擬錯誤
    monitor.log_error("gpt-4", RateLimitError("Rate limit exceeded"))
    monitor.log_error("gpt-3.5-turbo", Timeout("Request timed out"))
    monitor.log_error("gpt-4", RateLimitError("Rate limit exceeded"))

    stats = monitor.get_error_stats()
    print(f"錯誤統計: {stats}")


def example_robust_client():
    """範例 6: 健壯客戶端"""
    print("\n" + "=" * 50)
    print("範例 6: 健壯客戶端")
    print("=" * 50)

    client = RobustLLMClient(
        primary_model="gpt-4",
        fallback_models=["gpt-3.5-turbo", "claude-3-haiku"],
        rpm=60,
        tpm=90000
    )

    print("健壯客戶端配置:")
    print("  - 主模型: gpt-4")
    print("  - 備用模型: gpt-3.5-turbo, claude-3-haiku")
    print("  - RPM: 60")
    print("  - TPM: 90000")


if __name__ == "__main__":
    print("LiteLLM 錯誤處理範例\n")
    example_basic_handling()
    example_retry()
    example_fallback()
    example_rate_limiting()
    example_error_monitor()
    example_robust_client()

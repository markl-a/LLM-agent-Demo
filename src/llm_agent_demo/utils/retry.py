"""重試機制模組 - 提供指數退避重試功能"""

import functools
import logging
import time
from typing import Any, Callable, Optional, Tuple, Type, TypeVar

# 定義泛型類型變量用於裝飾器
F = TypeVar("F", bound=Callable[..., Any])

from .exceptions import (
    RetryError,
    MaxRetriesExceededError,
    ValidationError,
    handle_exception,
    wrap_exception,
)

logger = logging.getLogger(__name__)

# ============================================================================
# 效能優化：快取導入的異常類型
# ============================================================================
_cached_rate_limit_exceptions: Optional[Tuple[Type[Exception], ...]] = None
_cached_network_exceptions: Optional[Tuple[Type[Exception], ...]] = None


def retry_with_exponential_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    exponential_base: float = 2.0,
    max_delay: float = 60.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable[[Exception, int], None]] = None,
):
    """
    指數退避重試裝飾器

    當函數因指定的異常失敗時，會使用指數退避策略自動重試。

    Args:
        max_retries: 最大重試次數（必須 >= 0）
        initial_delay: 初始延遲時間（秒，必須 > 0）
        exponential_base: 指數基數（必須 > 1）
        max_delay: 最大延遲時間（秒，必須 > initial_delay）
        exceptions: 需要重試的異常類型元組
        on_retry: 重試時的回調函數，接收 (exception, retry_count) 參數

    Returns:
        裝飾器函數

    Raises:
        ValidationError: 如果參數無效

    使用示例:
        @retry_with_exponential_backoff(max_retries=3, initial_delay=1.0)
        def call_api():
            # API 調用代碼
            pass
    """
    # 參數驗證
    if not isinstance(max_retries, int) or max_retries < 0:
        raise ValidationError(
            "max_retries 必須是非負整數",
            field_name="max_retries",
            invalid_value=max_retries,
        )

    if not isinstance(initial_delay, (int, float)) or initial_delay <= 0:
        raise ValidationError(
            "initial_delay 必須是正數",
            field_name="initial_delay",
            invalid_value=initial_delay,
        )

    if not isinstance(exponential_base, (int, float)) or exponential_base <= 1:
        raise ValidationError(
            "exponential_base 必須大於 1",
            field_name="exponential_base",
            invalid_value=exponential_base,
        )

    if not isinstance(max_delay, (int, float)) or max_delay <= initial_delay:
        raise ValidationError(
            "max_delay 必須大於 initial_delay",
            field_name="max_delay",
            invalid_value=max_delay,
            details={"initial_delay": initial_delay},
        )

    if not isinstance(exceptions, tuple) or not exceptions:
        raise ValidationError(
            "exceptions 必須是非空的異常類型元組",
            field_name="exceptions",
            invalid_value=type(exceptions).__name__,
        )

    if on_retry is not None and not callable(on_retry):
        raise ValidationError(
            "on_retry 必須是可調用對象或 None",
            field_name="on_retry",
            invalid_value=type(on_retry).__name__,
        )

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            delay = initial_delay
            last_exception = None
            func_name = func.__name__

            for retry_count in range(max_retries + 1):
                try:
                    result = func(*args, **kwargs)

                    # 如果之前有重試，記錄成功信息
                    if retry_count > 0:
                        logger.info(
                            f"函數 '{func_name}' 在第 {retry_count + 1} 次嘗試後成功執行"
                        )

                    return result

                except exceptions as e:
                    last_exception = e

                    if retry_count == max_retries:
                        error_msg = (
                            f"函數 '{func_name}' 在 {max_retries} 次重試後仍然失敗。"
                            f"最後的錯誤: {type(e).__name__}: {str(e)}"
                        )
                        logger.error(error_msg)

                        # 拋出自定義的 MaxRetriesExceededError
                        raise MaxRetriesExceededError(
                            max_retries=max_retries,
                            operation=func_name,
                            last_error=e,
                        ) from e

                    # 調用回調函數
                    if on_retry:
                        try:
                            on_retry(e, retry_count + 1)
                        except Exception as callback_error:
                            logger.warning(
                                f"重試回調函數執行失敗: {callback_error}",
                                exc_info=True,
                            )
                    else:
                        logger.warning(
                            f"函數 '{func_name}' 失敗 "
                            f"(嘗試 {retry_count + 1}/{max_retries + 1}): "
                            f"{type(e).__name__}: {str(e)}. "
                            f"將在 {delay:.2f} 秒後重試..."
                        )

                    # 等待
                    try:
                        time.sleep(delay)
                    except KeyboardInterrupt:
                        logger.info("接收到中斷信號，停止重試")
                        raise

                    # 計算下次延遲（指數退避）
                    delay = min(delay * exponential_base, max_delay)

                except Exception as e:
                    # 捕獲不在重試列表中的異常
                    logger.error(
                        f"函數 '{func_name}' 拋出了不可重試的異常: "
                        f"{type(e).__name__}: {str(e)}",
                        exc_info=True,
                    )
                    raise

            # 不應該到達這裡，但以防萬一
            if last_exception:
                raise MaxRetriesExceededError(
                    max_retries=max_retries,
                    operation=func_name,
                    last_error=last_exception,
                ) from last_exception

        return wrapper

    return decorator


def _get_rate_limit_exceptions() -> Tuple[Type[Exception], ...]:
    """
    獲取速率限制異常類型（帶快取優化）

    Returns:
        速率限制異常類型元組
    """
    global _cached_rate_limit_exceptions

    if _cached_rate_limit_exceptions is not None:
        return _cached_rate_limit_exceptions

    # 常見的速率限制異常
    rate_limit_exceptions = [Exception]  # 基礎異常，實際使用時應該更具體

    # 嘗試導入具體的異常類型
    try:
        from openai import RateLimitError as OpenAIRateLimitError
        rate_limit_exceptions.append(OpenAIRateLimitError)
    except ImportError:
        logger.debug("未找到 openai 包，跳過 OpenAI RateLimitError")
        pass

    try:
        from anthropic import RateLimitError as AnthropicRateLimitError
        rate_limit_exceptions.append(AnthropicRateLimitError)
    except ImportError:
        logger.debug("未找到 anthropic 包，跳過 Anthropic RateLimitError")
        pass

    _cached_rate_limit_exceptions = tuple(rate_limit_exceptions)
    logger.debug(f"快取速率限制異常類型: {len(_cached_rate_limit_exceptions)} 種")
    return _cached_rate_limit_exceptions


def retry_on_rate_limit(
    max_retries: int = 5, initial_delay: float = 1.0, exponential_base: float = 2.0
):
    """
    專門用於處理 API 速率限制的重試裝飾器

    Args:
        max_retries: 最大重試次數
        initial_delay: 初始延遲時間（秒）
        exponential_base: 指數基數

    Returns:
        裝飾器函數
    """

    def on_retry_callback(exception: Exception, retry_count: int):
        """重試回調，提供更詳細的速率限制信息"""
        logger.warning(
            f"遇到速率限制錯誤 (嘗試 {retry_count}/{max_retries}): {exception}. "
            f"建議降低請求頻率或升級 API 方案。"
        )

    # 使用快取的異常類型（效能優化）
    rate_limit_exceptions = _get_rate_limit_exceptions()

    return retry_with_exponential_backoff(
        max_retries=max_retries,
        initial_delay=initial_delay,
        exponential_base=exponential_base,
        max_delay=300.0,  # 最多等待 5 分鐘
        exceptions=rate_limit_exceptions,
        on_retry=on_retry_callback,
    )


def _get_network_exceptions() -> Tuple[Type[Exception], ...]:
    """
    獲取網絡異常類型（帶快取優化）

    Returns:
        網絡異常類型元組
    """
    global _cached_network_exceptions

    if _cached_network_exceptions is not None:
        return _cached_network_exceptions

    import socket
    from urllib.error import URLError

    network_exceptions = [
        ConnectionError,
        TimeoutError,
        socket.timeout,
        URLError,
    ]

    # 嘗試導入 requests 異常
    try:
        import requests
        network_exceptions.extend([
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
        ])
    except ImportError:
        logger.debug("未找到 requests 包，跳過 requests 異常")
        pass

    # 嘗試導入 httpx 異常
    try:
        import httpx
        network_exceptions.extend([
            httpx.ConnectError,
            httpx.TimeoutException,
        ])
    except ImportError:
        logger.debug("未找到 httpx 包，跳過 httpx 異常")
        pass

    _cached_network_exceptions = tuple(network_exceptions)
    logger.debug(f"快取網絡異常類型: {len(_cached_network_exceptions)} 種")
    return _cached_network_exceptions


def retry_on_network_error(max_retries: int = 3, initial_delay: float = 0.5):
    """
    專門用於處理網絡錯誤的重試裝飾器

    Args:
        max_retries: 最大重試次數
        initial_delay: 初始延遲時間（秒）

    Returns:
        裝飾器函數
    """

    def on_retry_callback(exception: Exception, retry_count: int):
        """重試回調"""
        logger.warning(
            f"網絡錯誤 (嘗試 {retry_count}/{max_retries}): {exception}. " f"檢查網絡連接..."
        )

    # 使用快取的異常類型（效能優化）
    network_exceptions = _get_network_exceptions()

    return retry_with_exponential_backoff(
        max_retries=max_retries,
        initial_delay=initial_delay,
        exponential_base=2.0,
        max_delay=30.0,
        exceptions=network_exceptions,
        on_retry=on_retry_callback,
    )


class RetryContext:
    """
    重試上下文管理器 - 用於更靈活的重試控制

    使用示例:
        retry_ctx = RetryContext(max_retries=3, initial_delay=1.0)

        for attempt in retry_ctx:
            try:
                result = call_api()
                retry_ctx.mark_success()  # 標記成功
                break  # 成功，退出重試
            except Exception as e:
                retry_ctx.handle_exception(e)

        # 檢查是否成功
        if retry_ctx.succeeded:
            print(f"成功！結果: {result}")
        else:
            print(f"失敗！最後的錯誤: {retry_ctx.last_exception}")
    """

    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        exponential_base: float = 2.0,
        max_delay: float = 60.0,
    ):
        """
        初始化重試上下文

        Args:
            max_retries: 最大重試次數（必須 >= 0）
            initial_delay: 初始延遲時間（秒，必須 > 0）
            exponential_base: 指數基數（必須 > 1）
            max_delay: 最大延遲時間（秒，必須 > initial_delay）

        Raises:
            ValidationError: 如果參數無效
        """
        # 參數驗證
        if not isinstance(max_retries, int) or max_retries < 0:
            raise ValidationError(
                "max_retries 必須是非負整數",
                field_name="max_retries",
                invalid_value=max_retries,
            )

        if not isinstance(initial_delay, (int, float)) or initial_delay <= 0:
            raise ValidationError(
                "initial_delay 必須是正數",
                field_name="initial_delay",
                invalid_value=initial_delay,
            )

        if not isinstance(exponential_base, (int, float)) or exponential_base <= 1:
            raise ValidationError(
                "exponential_base 必須大於 1",
                field_name="exponential_base",
                invalid_value=exponential_base,
            )

        if not isinstance(max_delay, (int, float)) or max_delay <= initial_delay:
            raise ValidationError(
                "max_delay 必須大於 initial_delay",
                field_name="max_delay",
                invalid_value=max_delay,
                details={"initial_delay": initial_delay},
            )

        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.exponential_base = exponential_base
        self.max_delay = max_delay

        self.current_retry = 0
        self.delay = initial_delay
        self.last_exception: Optional[Exception] = None
        self.succeeded = False

    def __iter__(self) -> "RetryContext":
        """迭代器初始化

        Returns:
            RetryContext: 返回自身以支持迭代協議
        """
        self.current_retry = 0
        self.delay = self.initial_delay
        return self

    def __next__(self) -> int:
        """獲取下一次重試

        Returns:
            int: 當前嘗試次數（從 0 開始）

        Raises:
            StopIteration: 當達到最大重試次數時
        """
        if self.current_retry > self.max_retries:
            raise StopIteration

        attempt = self.current_retry
        self.current_retry += 1

        return attempt

    def handle_exception(self, exception: Exception) -> None:
        """
        處理異常

        Args:
            exception: 捕獲的異常

        Raises:
            MaxRetriesExceededError: 如果已達到最大重試次數
        """
        self.last_exception = exception

        if self.current_retry > self.max_retries:
            error_msg = (
                f"達到最大重試次數 ({self.max_retries})，放棄重試。"
                f"最後的錯誤: {type(exception).__name__}: {str(exception)}"
            )
            logger.error(error_msg)

            raise MaxRetriesExceededError(
                max_retries=self.max_retries,
                operation="RetryContext",
                last_error=exception,
            ) from exception

        logger.warning(
            f"重試 {self.current_retry}/{self.max_retries} 失敗: "
            f"{type(exception).__name__}: {str(exception)}. "
            f"將在 {self.delay:.2f} 秒後重試..."
        )

        try:
            time.sleep(self.delay)
        except KeyboardInterrupt:
            logger.info("接收到中斷信號，停止重試")
            raise

        self.delay = min(self.delay * self.exponential_base, self.max_delay)

    def mark_success(self) -> None:
        """標記為成功"""
        self.succeeded = True

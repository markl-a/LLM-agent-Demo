"""非同步工具模組 - 提供非同步操作的支援"""

import asyncio
import functools
import logging
from typing import (
    Any,
    Callable,
    Coroutine,
    Optional,
    Tuple,
    Type,
    TypeVar,
    List,
    Iterable,
    AsyncIterator,
)
from collections.abc import Awaitable

# 定義泛型類型變量用於裝飾器
T = TypeVar("T")
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


def async_retry_with_exponential_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    exponential_base: float = 2.0,
    max_delay: float = 60.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable[[Exception, int], Awaitable[None]]] = None,
):
    """
    非同步指數退避重試裝飾器

    當非同步函數因指定的異常失敗時，會使用指數退避策略自動重試。

    Args:
        max_retries: 最大重試次數（必須 >= 0）
        initial_delay: 初始延遲時間（秒，必須 > 0）
        exponential_base: 指數基數（必須 > 1）
        max_delay: 最大延遲時間（秒，必須 > initial_delay）
        exceptions: 需要重試的異常類型元組
        on_retry: 重試時的非同步回調函數，接收 (exception, retry_count) 參數

    Returns:
        裝飾器函數

    Raises:
        ValidationError: 如果參數無效

    使用示例:
        @async_retry_with_exponential_backoff(max_retries=3, initial_delay=1.0)
        async def call_api():
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

    def decorator(func: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            delay = initial_delay
            last_exception = None
            func_name = func.__name__

            for retry_count in range(max_retries + 1):
                try:
                    result = await func(*args, **kwargs)

                    # 如果之前有重試，記錄成功信息
                    if retry_count > 0:
                        logger.info(
                            f"非同步函數 '{func_name}' 在第 {retry_count + 1} 次嘗試後成功執行"
                        )

                    return result

                except exceptions as e:
                    last_exception = e

                    if retry_count == max_retries:
                        error_msg = (
                            f"非同步函數 '{func_name}' 在 {max_retries} 次重試後仍然失敗。"
                            f"最後的錯誤: {type(e).__name__}: {str(e)}"
                        )
                        logger.error(error_msg)

                        # 拋出自定義的 MaxRetriesExceededError
                        raise MaxRetriesExceededError(
                            max_retries=max_retries,
                            operation=func_name,
                            last_error=e,
                        ) from e

                    # 調用非同步回調函數
                    if on_retry:
                        try:
                            if asyncio.iscoroutinefunction(on_retry):
                                await on_retry(e, retry_count + 1)
                            else:
                                on_retry(e, retry_count + 1)
                        except Exception as callback_error:
                            logger.warning(
                                f"重試回調函數執行失敗: {callback_error}",
                                exc_info=True,
                            )
                    else:
                        logger.warning(
                            f"非同步函數 '{func_name}' 失敗 "
                            f"(嘗試 {retry_count + 1}/{max_retries + 1}): "
                            f"{type(e).__name__}: {str(e)}. "
                            f"將在 {delay:.2f} 秒後重試..."
                        )

                    # 等待（非同步）
                    try:
                        await asyncio.sleep(delay)
                    except asyncio.CancelledError:
                        logger.info("接收到取消信號，停止重試")
                        raise

                    # 計算下次延遲（指數退避）
                    delay = min(delay * exponential_base, max_delay)

                except Exception as e:
                    # 捕獲不在重試列表中的異常
                    logger.error(
                        f"非同步函數 '{func_name}' 拋出了不可重試的異常: "
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

    try:
        from anthropic import RateLimitError as AnthropicRateLimitError

        rate_limit_exceptions.append(AnthropicRateLimitError)
    except ImportError:
        logger.debug("未找到 anthropic 包，跳過 Anthropic RateLimitError")

    _cached_rate_limit_exceptions = tuple(rate_limit_exceptions)
    logger.debug(f"快取速率限制異常類型: {len(_cached_rate_limit_exceptions)} 種")
    return _cached_rate_limit_exceptions


def async_retry_on_rate_limit(
    max_retries: int = 5, initial_delay: float = 1.0, exponential_base: float = 2.0
):
    """
    非同步專門用於處理 API 速率限制的重試裝飾器

    Args:
        max_retries: 最大重試次數
        initial_delay: 初始延遲時間（秒）
        exponential_base: 指數基數

    Returns:
        裝飾器函數
    """

    async def on_retry_callback(exception: Exception, retry_count: int):
        """重試回調，提供更詳細的速率限制信息"""
        logger.warning(
            f"遇到速率限制錯誤 (嘗試 {retry_count}/{max_retries}): {exception}. "
            f"建議降低請求頻率或升級 API 方案。"
        )

    # 使用快取的異常類型（效能優化）
    rate_limit_exceptions = _get_rate_limit_exceptions()

    return async_retry_with_exponential_backoff(
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

    # 嘗試導入 aiohttp 異常
    try:
        import aiohttp

        network_exceptions.extend([
            aiohttp.ClientError,
            aiohttp.ClientConnectionError,
            aiohttp.ClientTimeout,
        ])
    except ImportError:
        logger.debug("未找到 aiohttp 包，跳過 aiohttp 異常")

    # 嘗試導入 httpx 異常
    try:
        import httpx

        network_exceptions.extend([
            httpx.ConnectError,
            httpx.TimeoutException,
        ])
    except ImportError:
        logger.debug("未找到 httpx 包，跳過 httpx 異常")

    _cached_network_exceptions = tuple(network_exceptions)
    logger.debug(f"快取網絡異常類型: {len(_cached_network_exceptions)} 種")
    return _cached_network_exceptions


def async_retry_on_network_error(max_retries: int = 3, initial_delay: float = 0.5):
    """
    非同步專門用於處理網絡錯誤的重試裝飾器

    Args:
        max_retries: 最大重試次數
        initial_delay: 初始延遲時間（秒）

    Returns:
        裝飾器函數
    """

    async def on_retry_callback(exception: Exception, retry_count: int):
        """重試回調"""
        logger.warning(
            f"網絡錯誤 (嘗試 {retry_count}/{max_retries}): {exception}. " f"檢查網絡連接..."
        )

    # 使用快取的異常類型（效能優化）
    network_exceptions = _get_network_exceptions()

    return async_retry_with_exponential_backoff(
        max_retries=max_retries,
        initial_delay=initial_delay,
        exponential_base=2.0,
        max_delay=30.0,
        exceptions=network_exceptions,
        on_retry=on_retry_callback,
    )


class AsyncRetryContext:
    """
    非同步重試上下文管理器 - 用於更靈活的重試控制

    使用示例:
        async with AsyncRetryContext(max_retries=3, initial_delay=1.0) as retry_ctx:
            for attempt in retry_ctx:
                try:
                    result = await call_api()
                    retry_ctx.mark_success()  # 標記成功
                    break  # 成功，退出重試
                except Exception as e:
                    await retry_ctx.handle_exception(e)

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
        初始化非同步重試上下文

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

    async def __aenter__(self) -> "AsyncRetryContext":
        """異步上下文管理器入口"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """異步上下文管理器出口"""
        # 如果有未處理的異常且未標記成功，記錄錯誤
        if exc_type is not None and not self.succeeded:
            logger.error(
                f"非同步重試上下文退出時存在異常: {exc_type.__name__}: {exc_val}"
            )
        return False  # 不抑制異常

    def __iter__(self) -> "AsyncRetryContext":
        """迭代器初始化

        Returns:
            AsyncRetryContext: 返回自身以支持迭代協議
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

    async def handle_exception(self, exception: Exception) -> None:
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
                operation="AsyncRetryContext",
                last_error=exception,
            ) from exception

        logger.warning(
            f"重試 {self.current_retry}/{self.max_retries} 失敗: "
            f"{type(exception).__name__}: {str(exception)}. "
            f"將在 {self.delay:.2f} 秒後重試..."
        )

        try:
            await asyncio.sleep(self.delay)
        except asyncio.CancelledError:
            logger.info("接收到取消信號，停止重試")
            raise

        self.delay = min(self.delay * self.exponential_base, self.max_delay)

    def mark_success(self) -> None:
        """標記為成功"""
        self.succeeded = True


# ============================================================================
# 非同步批量處理工具
# ============================================================================


async def async_batch_process(
    items: Iterable[T],
    process_func: Callable[[T], Awaitable[Any]],
    batch_size: int = 10,
    max_concurrent: int = 5,
    show_progress: bool = False,
) -> List[Any]:
    """
    非同步批量處理項目

    Args:
        items: 要處理的項目可迭代對象
        process_func: 處理單個項目的非同步函數
        batch_size: 每批處理的項目數量
        max_concurrent: 最大並發數
        show_progress: 是否顯示進度（需要 tqdm）

    Returns:
        處理結果列表

    使用示例:
        async def process_item(item):
            return await api_call(item)

        results = await async_batch_process(
            items=[1, 2, 3, 4, 5],
            process_func=process_item,
            batch_size=2,
            max_concurrent=3
        )
    """
    if not isinstance(batch_size, int) or batch_size <= 0:
        raise ValidationError(
            "batch_size 必須是正整數",
            field_name="batch_size",
            invalid_value=batch_size,
        )

    if not isinstance(max_concurrent, int) or max_concurrent <= 0:
        raise ValidationError(
            "max_concurrent 必須是正整數",
            field_name="max_concurrent",
            invalid_value=max_concurrent,
        )

    # 轉換為列表以便處理
    items_list = list(items)
    total_items = len(items_list)

    if total_items == 0:
        return []

    # 嘗試導入 tqdm（進度條）
    progress_bar = None
    if show_progress:
        try:
            from tqdm.asyncio import tqdm

            progress_bar = tqdm(total=total_items, desc="批量處理")
        except ImportError:
            logger.warning("未安裝 tqdm，無法顯示進度條")

    results = []
    semaphore = asyncio.Semaphore(max_concurrent)

    async def process_with_semaphore(item):
        """使用信號量控制並發的處理函數"""
        async with semaphore:
            try:
                result = await process_func(item)
                if progress_bar:
                    progress_bar.update(1)
                return result
            except Exception as e:
                logger.error(f"處理項目時發生錯誤: {e}", exc_info=True)
                if progress_bar:
                    progress_bar.update(1)
                raise

    # 分批處理
    for i in range(0, total_items, batch_size):
        batch = items_list[i : i + batch_size]
        batch_tasks = [process_with_semaphore(item) for item in batch]

        try:
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            results.extend(batch_results)
        except Exception as e:
            logger.error(f"批量處理時發生錯誤: {e}", exc_info=True)
            raise

    if progress_bar:
        progress_bar.close()

    return results


async def async_gather_with_limit(
    *coroutines: Coroutine,
    limit: int = 10,
    return_exceptions: bool = False,
) -> List[Any]:
    """
    限制並發數量的 asyncio.gather

    Args:
        *coroutines: 協程對象
        limit: 最大並發數
        return_exceptions: 是否返回異常而不是拋出

    Returns:
        結果列表

    使用示例:
        results = await async_gather_with_limit(
            api_call_1(),
            api_call_2(),
            api_call_3(),
            limit=2
        )
    """
    if not isinstance(limit, int) or limit <= 0:
        raise ValidationError(
            "limit 必須是正整數", field_name="limit", invalid_value=limit
        )

    semaphore = asyncio.Semaphore(limit)

    async def run_with_semaphore(coro):
        """使用信號量控制並發"""
        async with semaphore:
            return await coro

    tasks = [run_with_semaphore(coro) for coro in coroutines]
    return await asyncio.gather(*tasks, return_exceptions=return_exceptions)


async def async_retry_iterator(
    async_func: Callable[[], AsyncIterator[T]],
    max_retries: int = 3,
    initial_delay: float = 1.0,
    exponential_base: float = 2.0,
) -> AsyncIterator[T]:
    """
    非同步迭代器重試包裝器

    當異步迭代器失敗時自動重試。

    Args:
        async_func: 返回異步迭代器的函數
        max_retries: 最大重試次數
        initial_delay: 初始延遲時間（秒）
        exponential_base: 指數基數

    Yields:
        迭代器產生的項目

    使用示例:
        async def stream_data():
            async for item in api_stream():
                yield item

        async for item in async_retry_iterator(stream_data, max_retries=3):
            process(item)
    """
    delay = initial_delay
    last_exception = None

    for retry_count in range(max_retries + 1):
        try:
            async for item in async_func():
                yield item
            return  # 成功完成

        except Exception as e:
            last_exception = e

            if retry_count == max_retries:
                error_msg = (
                    f"非同步迭代器在 {max_retries} 次重試後仍然失敗。"
                    f"最後的錯誤: {type(e).__name__}: {str(e)}"
                )
                logger.error(error_msg)
                raise MaxRetriesExceededError(
                    max_retries=max_retries,
                    operation="async_retry_iterator",
                    last_error=e,
                ) from e

            logger.warning(
                f"非同步迭代器失敗 (嘗試 {retry_count + 1}/{max_retries + 1}): "
                f"{type(e).__name__}: {str(e)}. "
                f"將在 {delay:.2f} 秒後重試..."
            )

            try:
                await asyncio.sleep(delay)
            except asyncio.CancelledError:
                logger.info("接收到取消信號，停止重試")
                raise

            delay = min(delay * exponential_base, 60.0)


# ============================================================================
# 非同步超時控制
# ============================================================================


async def async_timeout(
    coro: Coroutine[Any, Any, T], timeout_seconds: float, operation_name: str = "操作"
) -> T:
    """
    為協程添加超時控制

    Args:
        coro: 協程對象
        timeout_seconds: 超時時間（秒）
        operation_name: 操作名稱（用於日誌）

    Returns:
        協程的返回值

    Raises:
        TimeoutError: 如果超時

    使用示例:
        result = await async_timeout(
            long_running_operation(),
            timeout_seconds=30.0,
            operation_name="API調用"
        )
    """
    if not isinstance(timeout_seconds, (int, float)) or timeout_seconds <= 0:
        raise ValidationError(
            "timeout_seconds 必須是正數",
            field_name="timeout_seconds",
            invalid_value=timeout_seconds,
        )

    try:
        return await asyncio.wait_for(coro, timeout=timeout_seconds)
    except asyncio.TimeoutError:
        error_msg = f"{operation_name} 超時（{timeout_seconds}秒）"
        logger.error(error_msg)
        from .exceptions import TimeoutError as CustomTimeoutError

        raise CustomTimeoutError(timeout=timeout_seconds) from None


# ============================================================================
# 非同步上下文管理器工具
# ============================================================================


class AsyncResourcePool:
    """
    非同步資源池 - 管理可重用的異步資源

    使用示例:
        pool = AsyncResourcePool(
            create_func=create_connection,
            destroy_func=close_connection,
            max_size=10
        )

        async with pool.acquire() as conn:
            await conn.execute(query)
    """

    def __init__(
        self,
        create_func: Callable[[], Awaitable[T]],
        destroy_func: Optional[Callable[[T], Awaitable[None]]] = None,
        max_size: int = 10,
    ):
        """
        初始化資源池

        Args:
            create_func: 創建資源的異步函數
            destroy_func: 銷毀資源的異步函數（可選）
            max_size: 資源池最大大小
        """
        if not callable(create_func):
            raise ValidationError(
                "create_func 必須是可調用對象",
                field_name="create_func",
                invalid_value=type(create_func).__name__,
            )

        if destroy_func is not None and not callable(destroy_func):
            raise ValidationError(
                "destroy_func 必須是可調用對象或 None",
                field_name="destroy_func",
                invalid_value=type(destroy_func).__name__,
            )

        if not isinstance(max_size, int) or max_size <= 0:
            raise ValidationError(
                "max_size 必須是正整數",
                field_name="max_size",
                invalid_value=max_size,
            )

        self._create_func = create_func
        self._destroy_func = destroy_func
        self._max_size = max_size
        self._pool: List[T] = []
        self._in_use: int = 0
        self._lock = asyncio.Lock()

    async def acquire(self) -> T:
        """
        獲取資源

        Returns:
            資源對象
        """
        async with self._lock:
            # 如果池中有可用資源，直接返回
            if self._pool:
                resource = self._pool.pop()
                self._in_use += 1
                logger.debug(f"從池中獲取資源，當前使用: {self._in_use}")
                return resource

            # 如果未達到最大大小，創建新資源
            if self._in_use < self._max_size:
                resource = await self._create_func()
                self._in_use += 1
                logger.debug(f"創建新資源，當前使用: {self._in_use}")
                return resource

        # 等待資源可用
        logger.debug("資源池已滿，等待資源釋放...")
        while True:
            await asyncio.sleep(0.1)
            async with self._lock:
                if self._pool:
                    resource = self._pool.pop()
                    self._in_use += 1
                    return resource

    async def release(self, resource: T) -> None:
        """
        釋放資源

        Args:
            resource: 要釋放的資源
        """
        async with self._lock:
            self._pool.append(resource)
            self._in_use -= 1
            logger.debug(f"釋放資源到池中，當前使用: {self._in_use}")

    async def close(self) -> None:
        """關閉資源池並清理所有資源"""
        async with self._lock:
            if self._destroy_func:
                for resource in self._pool:
                    try:
                        await self._destroy_func(resource)
                    except Exception as e:
                        logger.error(f"銷毀資源時發生錯誤: {e}", exc_info=True)

            self._pool.clear()
            self._in_use = 0
            logger.info("資源池已關閉")

    def acquire_context(self):
        """返回上下文管理器以便使用 async with"""
        return _ResourceContextManager(self)


class _ResourceContextManager:
    """資源上下文管理器內部類"""

    def __init__(self, pool: AsyncResourcePool):
        self._pool = pool
        self._resource: Optional[Any] = None

    async def __aenter__(self):
        self._resource = await self._pool.acquire()
        return self._resource

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._resource is not None:
            await self._pool.release(self._resource)
        return False


# ============================================================================
# 便利函數
# ============================================================================


def run_async(coro: Coroutine[Any, Any, T]) -> T:
    """
    在同步上下文中運行異步協程

    這是一個便利函數，用於在同步代碼中調用異步函數。

    Args:
        coro: 協程對象

    Returns:
        協程的返回值

    使用示例:
        result = run_async(async_function())
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # 如果事件循環已經在運行，創建新任務
            logger.warning("事件循環已在運行，將創建新任務")
            return asyncio.ensure_future(coro)
        else:
            return loop.run_until_complete(coro)
    except RuntimeError:
        # 沒有事件循環，創建新的
        return asyncio.run(coro)


async def async_wrap_sync_func(
    func: Callable[..., T], *args, **kwargs
) -> T:
    """
    將同步函數包裝為異步函數

    Args:
        func: 同步函數
        *args: 位置參數
        **kwargs: 關鍵字參數

    Returns:
        函數的返回值

    使用示例:
        result = await async_wrap_sync_func(sync_function, arg1, arg2)
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, functools.partial(func, *args, **kwargs))

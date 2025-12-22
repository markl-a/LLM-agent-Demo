"""非同步工具模組的單元測試"""

import asyncio
import time
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# 檢查是否安裝了核心模組
try:
    from src.llm_agent_demo.utils.async_utils import (
        async_retry_with_exponential_backoff,
        async_retry_on_rate_limit,
        async_retry_on_network_error,
        AsyncRetryContext,
        async_batch_process,
        async_gather_with_limit,
        async_retry_iterator,
        async_timeout,
        AsyncResourcePool,
        run_async,
        async_wrap_sync_func,
    )
    from src.llm_agent_demo.utils.exceptions import (
        MaxRetriesExceededError,
        ValidationError,
        TimeoutError as CustomTimeoutError,
    )

    CORE_MODULE_AVAILABLE = True
except ImportError:
    CORE_MODULE_AVAILABLE = False
    pytest.skip("核心模組未安裝", allow_module_level=True)


@pytest.mark.unit
@pytest.mark.asyncio
class TestAsyncRetryWithExponentialBackoff:
    """測試異步重試裝飾器"""

    async def test_successful_call_no_retry(self):
        """測試成功調用不重試"""
        call_count = 0

        @async_retry_with_exponential_backoff(max_retries=3, initial_delay=0.01)
        async def successful_func():
            nonlocal call_count
            call_count += 1
            return "success"

        result = await successful_func()
        assert result == "success"
        assert call_count == 1

    async def test_retry_on_failure_then_success(self):
        """測試失敗後重試直到成功"""
        call_count = 0

        @async_retry_with_exponential_backoff(max_retries=3, initial_delay=0.01)
        async def fail_twice_then_succeed():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("模擬失敗")
            return "success"

        result = await fail_twice_then_succeed()
        assert result == "success"
        assert call_count == 3

    async def test_max_retries_exceeded(self):
        """測試超過最大重試次數"""
        call_count = 0

        @async_retry_with_exponential_backoff(max_retries=2, initial_delay=0.01)
        async def always_fail():
            nonlocal call_count
            call_count += 1
            raise ValueError("總是失敗")

        with pytest.raises(MaxRetriesExceededError) as exc_info:
            await always_fail()

        assert call_count == 3  # 1 次初始 + 2 次重試
        assert exc_info.value.details["max_retries"] == 2
        assert "always_fail" in str(exc_info.value)

    async def test_only_retry_specified_exceptions(self):
        """測試只重試指定的異常"""
        call_count = 0

        @async_retry_with_exponential_backoff(
            max_retries=3, initial_delay=0.01, exceptions=(ValueError,)
        )
        async def raise_type_error():
            nonlocal call_count
            call_count += 1
            raise TypeError("不應該重試")

        with pytest.raises(TypeError, match="不應該重試"):
            await raise_type_error()

        assert call_count == 1  # TypeError 不在重試列表中

    async def test_on_retry_async_callback(self):
        """測試異步重試回調函數"""
        retry_counts = []

        async def on_retry(exception, retry_count):
            await asyncio.sleep(0.001)  # 模擬異步操作
            retry_counts.append(retry_count)

        @async_retry_with_exponential_backoff(
            max_retries=2, initial_delay=0.01, on_retry=on_retry
        )
        async def fail_twice():
            if len(retry_counts) < 2:
                raise ValueError("失敗")
            return "success"

        result = await fail_twice()
        assert result == "success"
        assert retry_counts == [1, 2]

    async def test_on_retry_sync_callback(self):
        """測試同步重試回調函數"""
        retry_counts = []

        def on_retry(exception, retry_count):
            retry_counts.append(retry_count)

        @async_retry_with_exponential_backoff(
            max_retries=2, initial_delay=0.01, on_retry=on_retry
        )
        async def fail_once():
            if len(retry_counts) < 1:
                raise ValueError("失敗")
            return "success"

        result = await fail_once()
        assert result == "success"
        assert retry_counts == [1]

    async def test_exponential_delay(self):
        """測試指數延遲增長"""
        start_times = []

        @async_retry_with_exponential_backoff(
            max_retries=3, initial_delay=0.05, exponential_base=2.0, max_delay=1.0
        )
        async def record_times():
            start_times.append(time.time())
            if len(start_times) < 3:
                raise ValueError("失敗")
            return "success"

        await record_times()

        # 檢查延遲是否大致符合指數增長
        if len(start_times) >= 2:
            delay1 = start_times[1] - start_times[0]
            assert delay1 >= 0.04  # 約 0.05 秒

        if len(start_times) >= 3:
            delay2 = start_times[2] - start_times[1]
            assert delay2 >= 0.08  # 約 0.1 秒 (0.05 * 2)

    async def test_max_delay_cap(self):
        """測試最大延遲上限"""
        start_times = []

        @async_retry_with_exponential_backoff(
            max_retries=5, initial_delay=0.01, exponential_base=10.0, max_delay=0.05
        )
        async def track_delays():
            start_times.append(time.time())
            if len(start_times) < 4:
                raise ValueError("失敗")
            return "success"

        await track_delays()

        # 計算每次重試之間的延遲
        for i in range(1, len(start_times)):
            delay = start_times[i] - start_times[i-1]
            # 延遲應該不超過 max_delay + 一些容錯空間
            assert delay <= 0.1  # max_delay=0.05，留一些誤差空間

    async def test_preserves_function_metadata(self):
        """測試保留函數元數據"""

        @async_retry_with_exponential_backoff(max_retries=1, initial_delay=0.01)
        async def my_async_function():
            """這是一個測試函數"""
            return "result"

        assert my_async_function.__name__ == "my_async_function"
        assert my_async_function.__doc__ == "這是一個測試函數"

    async def test_with_function_arguments(self):
        """測試帶參數的函數"""

        @async_retry_with_exponential_backoff(max_retries=1, initial_delay=0.01)
        async def func_with_args(a, b, c=None):
            return a + b + (c or 0)

        assert await func_with_args(1, 2) == 3
        assert await func_with_args(1, 2, c=3) == 6

    async def test_cancellation_during_retry(self):
        """測試重試期間的取消操作"""
        call_count = 0

        @async_retry_with_exponential_backoff(max_retries=5, initial_delay=0.5)
        async def slow_retry():
            nonlocal call_count
            call_count += 1
            raise ValueError("失敗")

        async def run_and_cancel():
            task = asyncio.create_task(slow_retry())
            await asyncio.sleep(0.1)  # 讓第一次嘗試完成
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                return "cancelled"

        result = await run_and_cancel()
        assert result == "cancelled"
        assert call_count >= 1  # 至少嘗試了一次

    async def test_invalid_max_retries(self):
        """測試無效的 max_retries 參數"""
        with pytest.raises(ValidationError, match="max_retries 必須是非負整數"):
            async_retry_with_exponential_backoff(max_retries=-1)

        with pytest.raises(ValidationError):
            async_retry_with_exponential_backoff(max_retries="invalid")

    async def test_invalid_initial_delay(self):
        """測試無效的 initial_delay 參數"""
        with pytest.raises(ValidationError, match="initial_delay 必須是正數"):
            async_retry_with_exponential_backoff(initial_delay=0)

        with pytest.raises(ValidationError):
            async_retry_with_exponential_backoff(initial_delay=-1)

    async def test_invalid_exponential_base(self):
        """測試無效的 exponential_base 參數"""
        with pytest.raises(ValidationError, match="exponential_base 必須大於 1"):
            async_retry_with_exponential_backoff(exponential_base=1)

        with pytest.raises(ValidationError):
            async_retry_with_exponential_backoff(exponential_base=0.5)

    async def test_invalid_max_delay(self):
        """測試無效的 max_delay 參數"""
        with pytest.raises(ValidationError, match="max_delay 必須大於 initial_delay"):
            async_retry_with_exponential_backoff(initial_delay=10, max_delay=5)

    async def test_invalid_exceptions(self):
        """測試無效的 exceptions 參數"""
        with pytest.raises(ValidationError, match="exceptions 必須是非空的異常類型元組"):
            async_retry_with_exponential_backoff(exceptions=[])

        with pytest.raises(ValidationError):
            async_retry_with_exponential_backoff(exceptions="invalid")

    async def test_invalid_on_retry(self):
        """測試無效的 on_retry 參數"""
        with pytest.raises(ValidationError, match="on_retry 必須是可調用對象或 None"):
            async_retry_with_exponential_backoff(on_retry="invalid")


@pytest.mark.unit
@pytest.mark.asyncio
class TestAsyncRetryOnRateLimit:
    """測試速率限制重試裝飾器"""

    async def test_retry_on_rate_limit_error(self):
        """測試速率限制錯誤重試"""
        call_count = 0

        @async_retry_on_rate_limit(max_retries=2, initial_delay=0.01)
        async def fail_then_succeed():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise Exception("Rate limit exceeded")
            return "success"

        result = await fail_then_succeed()
        assert result == "success"
        assert call_count == 2


@pytest.mark.unit
@pytest.mark.asyncio
class TestAsyncRetryOnNetworkError:
    """測試網絡錯誤重試裝飾器"""

    async def test_retry_on_connection_error(self):
        """測試連接錯誤重試"""
        call_count = 0

        @async_retry_on_network_error(max_retries=2, initial_delay=0.01)
        async def fail_then_succeed():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ConnectionError("連接失敗")
            return "success"

        result = await fail_then_succeed()
        assert result == "success"
        assert call_count == 2

    async def test_retry_on_timeout_error(self):
        """測試超時錯誤重試"""
        call_count = 0

        @async_retry_on_network_error(max_retries=2, initial_delay=0.01)
        async def timeout_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise TimeoutError("請求超時")
            return "success"

        result = await timeout_func()
        assert result == "success"
        assert call_count == 2


@pytest.mark.unit
@pytest.mark.asyncio
class TestAsyncRetryContext:
    """測試異步重試上下文管理器"""

    async def test_successful_first_attempt(self):
        """測試第一次嘗試成功"""
        async with AsyncRetryContext(max_retries=3, initial_delay=0.01) as retry_ctx:
            for attempt in retry_ctx:
                result = "success"
                retry_ctx.mark_success()
                break

        assert retry_ctx.succeeded is True
        assert retry_ctx.last_exception is None

    async def test_retry_until_success(self):
        """測試重試直到成功"""
        attempt_count = 0

        async with AsyncRetryContext(max_retries=3, initial_delay=0.01) as retry_ctx:
            for attempt in retry_ctx:
                attempt_count += 1
                try:
                    if attempt_count < 3:
                        raise ValueError("模擬失敗")
                    result = "success"
                    retry_ctx.mark_success()
                    break
                except ValueError as e:
                    await retry_ctx.handle_exception(e)

        assert retry_ctx.succeeded is True
        assert attempt_count == 3

    async def test_max_retries_exceeded_context(self):
        """測試上下文管理器超過最大重試"""
        async with AsyncRetryContext(max_retries=2, initial_delay=0.01) as retry_ctx:
            with pytest.raises(MaxRetriesExceededError):
                for attempt in retry_ctx:
                    try:
                        raise ValueError("總是失敗")
                    except ValueError as e:
                        await retry_ctx.handle_exception(e)

        assert retry_ctx.succeeded is False
        assert retry_ctx.last_exception is not None

    async def test_context_iteration(self):
        """測試上下文迭代"""
        async with AsyncRetryContext(max_retries=2, initial_delay=0.01) as retry_ctx:
            attempts = list(retry_ctx)
            assert attempts == [0, 1, 2]

    async def test_context_exponential_delay(self):
        """測試上下文指數延遲"""
        start_times = []

        async with AsyncRetryContext(
            max_retries=2, initial_delay=0.05, exponential_base=2.0, max_delay=1.0
        ) as retry_ctx:
            for attempt in retry_ctx:
                start_times.append(time.time())
                try:
                    if len(start_times) < 3:
                        raise ValueError("失敗")
                    retry_ctx.mark_success()
                    break
                except ValueError as e:
                    await retry_ctx.handle_exception(e)

        # 檢查延遲
        if len(start_times) >= 2:
            delay1 = start_times[1] - start_times[0]
            assert delay1 >= 0.04

    async def test_context_invalid_parameters(self):
        """測試上下文無效參數"""
        with pytest.raises(ValidationError):
            AsyncRetryContext(max_retries=-1)

        with pytest.raises(ValidationError):
            AsyncRetryContext(initial_delay=0)

        with pytest.raises(ValidationError):
            AsyncRetryContext(exponential_base=1)

        with pytest.raises(ValidationError):
            AsyncRetryContext(initial_delay=10, max_delay=5)


@pytest.mark.unit
@pytest.mark.asyncio
class TestAsyncBatchProcess:
    """測試異步批量處理"""

    async def test_batch_process_success(self):
        """測試批量處理成功"""
        async def process_item(item):
            await asyncio.sleep(0.01)
            return item * 2

        items = [1, 2, 3, 4, 5]
        results = await async_batch_process(
            items=items,
            process_func=process_item,
            batch_size=2,
            max_concurrent=3
        )

        assert results == [2, 4, 6, 8, 10]

    async def test_batch_process_empty_list(self):
        """測試空列表"""
        async def process_item(item):
            return item

        results = await async_batch_process(
            items=[],
            process_func=process_item,
            batch_size=2,
            max_concurrent=3
        )

        assert results == []

    async def test_batch_process_with_exceptions(self):
        """測試批量處理中的異常"""
        call_count = 0

        async def process_item(item):
            nonlocal call_count
            call_count += 1
            if item == 3:
                raise ValueError(f"處理項目 {item} 失敗")
            return item * 2

        items = [1, 2, 3, 4, 5]
        results = await async_batch_process(
            items=items,
            process_func=process_item,
            batch_size=2,
            max_concurrent=3
        )

        # return_exceptions=True，所以異常會作為結果返回
        assert len(results) == 5
        assert results[0] == 2
        assert results[1] == 4
        assert isinstance(results[2], ValueError)
        assert results[3] == 8
        assert results[4] == 10

    async def test_batch_process_concurrency_limit(self):
        """測試並發限制"""
        active_count = 0
        max_active = 0

        async def process_item(item):
            nonlocal active_count, max_active
            active_count += 1
            max_active = max(max_active, active_count)
            await asyncio.sleep(0.05)
            active_count -= 1
            return item

        items = list(range(10))
        await async_batch_process(
            items=items,
            process_func=process_item,
            batch_size=10,
            max_concurrent=3
        )

        # 最大並發數應該不超過 3
        assert max_active <= 3

    async def test_batch_process_invalid_batch_size(self):
        """測試無效的 batch_size"""
        async def process_item(item):
            return item

        with pytest.raises(ValidationError, match="batch_size 必須是正整數"):
            await async_batch_process(
                items=[1, 2, 3],
                process_func=process_item,
                batch_size=0
            )

    async def test_batch_process_invalid_max_concurrent(self):
        """測試無效的 max_concurrent"""
        async def process_item(item):
            return item

        with pytest.raises(ValidationError, match="max_concurrent 必須是正整數"):
            await async_batch_process(
                items=[1, 2, 3],
                process_func=process_item,
                max_concurrent=-1
            )


@pytest.mark.unit
@pytest.mark.asyncio
class TestAsyncGatherWithLimit:
    """測試限制並發的 gather"""

    async def test_gather_with_limit_success(self):
        """測試限制並發成功"""
        async def task(n):
            await asyncio.sleep(0.01)
            return n * 2

        results = await async_gather_with_limit(
            task(1), task(2), task(3), task(4),
            limit=2
        )

        assert results == [2, 4, 6, 8]

    async def test_gather_with_limit_respects_limit(self):
        """測試遵守並發限制"""
        active_count = 0
        max_active = 0

        async def task(n):
            nonlocal active_count, max_active
            active_count += 1
            max_active = max(max_active, active_count)
            await asyncio.sleep(0.05)
            active_count -= 1
            return n

        await async_gather_with_limit(
            task(1), task(2), task(3), task(4), task(5),
            limit=2
        )

        # 最大並發數應該不超過 2
        assert max_active <= 2

    async def test_gather_with_limit_return_exceptions(self):
        """測試返回異常"""
        async def task(n):
            if n == 2:
                raise ValueError(f"Error in task {n}")
            return n

        results = await async_gather_with_limit(
            task(1), task(2), task(3),
            limit=2,
            return_exceptions=True
        )

        assert len(results) == 3
        assert results[0] == 1
        assert isinstance(results[1], ValueError)
        assert results[2] == 3

    async def test_gather_with_limit_propagates_exception(self):
        """測試異常傳播"""
        async def task(n):
            if n == 2:
                raise ValueError(f"Error in task {n}")
            return n

        with pytest.raises(ValueError):
            await async_gather_with_limit(
                task(1), task(2), task(3),
                limit=2,
                return_exceptions=False
            )

    async def test_gather_invalid_limit(self):
        """測試無效的 limit 參數"""
        async def task(n):
            return n

        with pytest.raises(ValidationError, match="limit 必須是正整數"):
            await async_gather_with_limit(task(1), limit=0)


@pytest.mark.unit
@pytest.mark.asyncio
class TestAsyncRetryIterator:
    """測試異步迭代器重試包裝器"""

    async def test_retry_iterator_success(self):
        """測試迭代器成功"""
        async def stream_data():
            for i in range(5):
                await asyncio.sleep(0.01)
                yield i

        results = []
        async for item in async_retry_iterator(stream_data, max_retries=2):
            results.append(item)

        assert results == [0, 1, 2, 3, 4]

    async def test_retry_iterator_with_failure_then_success(self):
        """測試迭代器失敗後成功"""
        attempt_count = 0

        async def stream_data():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 2:
                raise ValueError("第一次失敗")
            for i in range(3):
                yield i

        results = []
        async for item in async_retry_iterator(
            stream_data, max_retries=3, initial_delay=0.01
        ):
            results.append(item)

        assert results == [0, 1, 2]
        assert attempt_count == 2

    async def test_retry_iterator_max_retries_exceeded(self):
        """測試迭代器超過最大重試"""
        async def always_fail():
            raise ValueError("總是失敗")
            yield  # 這行永遠不會執行

        with pytest.raises(MaxRetriesExceededError):
            async for item in async_retry_iterator(
                always_fail, max_retries=2, initial_delay=0.01
            ):
                pass


@pytest.mark.unit
@pytest.mark.asyncio
class TestAsyncTimeout:
    """測試異步超時控制"""

    async def test_timeout_success(self):
        """測試在超時前完成"""
        async def quick_task():
            await asyncio.sleep(0.01)
            return "success"

        result = await async_timeout(
            quick_task(),
            timeout_seconds=1.0,
            operation_name="快速任務"
        )

        assert result == "success"

    async def test_timeout_exceeded(self):
        """測試超時"""
        async def slow_task():
            await asyncio.sleep(1.0)
            return "這不應該返回"

        with pytest.raises(CustomTimeoutError) as exc_info:
            await async_timeout(
                slow_task(),
                timeout_seconds=0.05,
                operation_name="慢速任務"
            )

        assert exc_info.value.details["timeout"] == 0.05

    async def test_timeout_invalid_timeout_seconds(self):
        """測試無效的 timeout_seconds"""
        async def task():
            return "result"

        with pytest.raises(ValidationError, match="timeout_seconds 必須是正數"):
            await async_timeout(task(), timeout_seconds=0)

        with pytest.raises(ValidationError):
            await async_timeout(task(), timeout_seconds=-1)


@pytest.mark.unit
@pytest.mark.asyncio
class TestAsyncResourcePool:
    """測試異步資源池"""

    async def test_resource_pool_basic(self):
        """測試資源池基本功能"""
        created_count = 0

        async def create_resource():
            nonlocal created_count
            created_count += 1
            return f"resource_{created_count}"

        pool = AsyncResourcePool(
            create_func=create_resource,
            max_size=3
        )

        # 獲取資源
        async with pool.acquire_context() as resource1:
            assert resource1 == "resource_1"

        async with pool.acquire_context() as resource2:
            # 應該重用已釋放的資源
            assert resource2 == "resource_1"

        await pool.close()

    async def test_resource_pool_multiple_resources(self):
        """測試多個資源"""
        created_count = 0

        async def create_resource():
            nonlocal created_count
            created_count += 1
            return f"resource_{created_count}"

        pool = AsyncResourcePool(
            create_func=create_resource,
            max_size=3
        )

        # 同時獲取多個資源
        async with pool.acquire_context() as r1:
            async with pool.acquire_context() as r2:
                assert r1 != r2
                assert created_count == 2

        await pool.close()

    async def test_resource_pool_with_destroy_func(self):
        """測試帶銷毀函數的資源池"""
        created = []
        destroyed = []

        async def create_resource():
            resource = f"resource_{len(created)}"
            created.append(resource)
            return resource

        async def destroy_resource(resource):
            destroyed.append(resource)

        pool = AsyncResourcePool(
            create_func=create_resource,
            destroy_func=destroy_resource,
            max_size=2
        )

        async with pool.acquire_context() as r1:
            pass

        await pool.close()

        assert len(created) == 1
        assert len(destroyed) == 1
        assert created[0] == destroyed[0]

    async def test_resource_pool_max_size(self):
        """測試資源池最大大小"""
        created_count = 0

        async def create_resource():
            nonlocal created_count
            created_count += 1
            await asyncio.sleep(0.01)
            return f"resource_{created_count}"

        pool = AsyncResourcePool(
            create_func=create_resource,
            max_size=2
        )

        # 同時請求 3 個資源，但最多只創建 2 個
        resources = []

        async def acquire_and_release():
            async with pool.acquire_context() as r:
                resources.append(r)
                await asyncio.sleep(0.05)

        # 啟動任務但不等待全部完成
        task1 = asyncio.create_task(acquire_and_release())
        task2 = asyncio.create_task(acquire_and_release())

        await task1
        await task2

        # 最多只創建 max_size 個資源
        assert created_count <= 2

        await pool.close()

    async def test_resource_pool_invalid_create_func(self):
        """測試無效的 create_func"""
        with pytest.raises(ValidationError, match="create_func 必須是可調用對象"):
            AsyncResourcePool(create_func="invalid")

    async def test_resource_pool_invalid_destroy_func(self):
        """測試無效的 destroy_func"""
        async def create():
            return "resource"

        with pytest.raises(ValidationError, match="destroy_func 必須是可調用對象或 None"):
            AsyncResourcePool(create_func=create, destroy_func="invalid")

    async def test_resource_pool_invalid_max_size(self):
        """測試無效的 max_size"""
        async def create():
            return "resource"

        with pytest.raises(ValidationError, match="max_size 必須是正整數"):
            AsyncResourcePool(create_func=create, max_size=0)


@pytest.mark.unit
class TestRunAsync:
    """測試 run_async 便利函數"""

    def test_run_async_simple(self):
        """測試簡單的異步函數運行"""
        async def simple_async_func():
            await asyncio.sleep(0.01)
            return "result"

        result = run_async(simple_async_func())
        assert result == "result"

    def test_run_async_with_exception(self):
        """測試異步函數拋出異常"""
        async def failing_async_func():
            raise ValueError("測試異常")

        with pytest.raises(ValueError, match="測試異常"):
            run_async(failing_async_func())


@pytest.mark.unit
@pytest.mark.asyncio
class TestAsyncWrapSyncFunc:
    """測試同步函數異步包裝"""

    async def test_wrap_sync_func_simple(self):
        """測試包裝簡單的同步函數"""
        def sync_func(a, b):
            return a + b

        result = await async_wrap_sync_func(sync_func, 1, 2)
        assert result == 3

    async def test_wrap_sync_func_with_kwargs(self):
        """測試包裝帶關鍵字參數的同步函數"""
        def sync_func(a, b, c=0):
            return a + b + c

        result = await async_wrap_sync_func(sync_func, 1, 2, c=3)
        assert result == 6

    async def test_wrap_sync_func_with_sleep(self):
        """測試包裝會阻塞的同步函數"""
        def blocking_func():
            time.sleep(0.1)
            return "done"

        start = time.time()
        result = await async_wrap_sync_func(blocking_func)
        elapsed = time.time() - start

        assert result == "done"
        assert elapsed >= 0.09  # 應該至少花費 0.1 秒

    async def test_wrap_sync_func_with_exception(self):
        """測試包裝會拋出異常的同步函數"""
        def failing_func():
            raise ValueError("同步異常")

        with pytest.raises(ValueError, match="同步異常"):
            await async_wrap_sync_func(failing_func)


@pytest.mark.unit
@pytest.mark.asyncio
class TestAsyncUtilsIntegration:
    """測試異步工具的整合場景"""

    async def test_retry_with_timeout(self):
        """測試重試與超時結合"""
        call_count = 0

        @async_retry_with_exponential_backoff(max_retries=3, initial_delay=0.01)
        async def slow_task():
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.05)
            if call_count < 2:
                raise ValueError("失敗")
            return "success"

        # 帶超時的重試
        result = await async_timeout(
            slow_task(),
            timeout_seconds=1.0,
            operation_name="慢速重試任務"
        )

        assert result == "success"
        assert call_count == 2

    async def test_batch_process_with_retry(self):
        """測試批量處理與重試結合"""
        failed_items = {2, 4}
        retry_counts = {}

        @async_retry_with_exponential_backoff(max_retries=2, initial_delay=0.01)
        async def process_with_retry(item):
            retry_counts[item] = retry_counts.get(item, 0) + 1
            if item in failed_items and retry_counts[item] < 2:
                raise ValueError(f"項目 {item} 失敗")
            return item * 2

        items = [1, 2, 3, 4, 5]
        results = await async_batch_process(
            items=items,
            process_func=process_with_retry,
            batch_size=2,
            max_concurrent=3
        )

        assert results == [2, 4, 6, 8, 10]
        # 失敗的項目應該被重試
        assert retry_counts[2] >= 2
        assert retry_counts[4] >= 2

    async def test_resource_pool_with_retry(self):
        """測試資源池與重試結合"""
        created_count = 0
        call_count = 0

        async def create_connection():
            nonlocal created_count
            created_count += 1
            return {"id": created_count, "status": "connected"}

        pool = AsyncResourcePool(create_func=create_connection, max_size=2)

        @async_retry_with_exponential_backoff(max_retries=2, initial_delay=0.01)
        async def use_resource():
            nonlocal call_count
            call_count += 1
            async with pool.acquire_context() as conn:
                # 第一次和第二次失敗，第三次成功
                if call_count < 3:
                    raise ValueError("操作失敗")
                return conn["id"]

        result = await use_resource()
        assert result in [1, 2]
        assert call_count == 3  # 應該重試了 2 次

        await pool.close()

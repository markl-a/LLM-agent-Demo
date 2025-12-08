"""重試機制模組的單元測試"""

import time
import pytest

# 檢查是否安裝了核心模組
try:
    from src.llm_agent_demo.utils.retry import (
        retry_with_exponential_backoff,
        retry_on_network_error,
        RetryContext,
    )

    CORE_MODULE_AVAILABLE = True
except ImportError:
    CORE_MODULE_AVAILABLE = False
    pytest.skip("核心模組未安裝", allow_module_level=True)


@pytest.mark.unit
class TestRetryWithExponentialBackoff:
    """測試指數退避重試裝飾器"""

    def test_successful_call_no_retry(self):
        """測試成功調用不重試"""
        call_count = 0

        @retry_with_exponential_backoff(max_retries=3, initial_delay=0.01)
        def successful_func():
            nonlocal call_count
            call_count += 1
            return "success"

        result = successful_func()
        assert result == "success"
        assert call_count == 1

    def test_retry_on_failure_then_success(self):
        """測試失敗後重試直到成功"""
        call_count = 0

        @retry_with_exponential_backoff(max_retries=3, initial_delay=0.01)
        def fail_twice_then_succeed():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("模擬失敗")
            return "success"

        result = fail_twice_then_succeed()
        assert result == "success"
        assert call_count == 3

    def test_max_retries_exceeded(self):
        """測試超過最大重試次數"""
        call_count = 0

        @retry_with_exponential_backoff(max_retries=2, initial_delay=0.01)
        def always_fail():
            nonlocal call_count
            call_count += 1
            raise ValueError("總是失敗")

        with pytest.raises(ValueError, match="總是失敗"):
            always_fail()

        # max_retries=2 意味著最多嘗試 3 次 (1 + 2 重試)
        assert call_count == 3

    def test_only_retry_specified_exceptions(self):
        """測試只重試指定的異常"""
        call_count = 0

        @retry_with_exponential_backoff(
            max_retries=3, initial_delay=0.01, exceptions=(ValueError,)
        )
        def raise_type_error():
            nonlocal call_count
            call_count += 1
            raise TypeError("不應該重試")

        with pytest.raises(TypeError, match="不應該重試"):
            raise_type_error()

        # TypeError 不在重試列表中，所以只調用一次
        assert call_count == 1

    def test_on_retry_callback(self):
        """測試重試回調函數"""
        retry_counts = []

        def on_retry(exception, retry_count):
            retry_counts.append(retry_count)

        @retry_with_exponential_backoff(
            max_retries=2, initial_delay=0.01, on_retry=on_retry
        )
        def fail_twice():
            if len(retry_counts) < 2:
                raise ValueError("失敗")
            return "success"

        result = fail_twice()
        assert result == "success"
        assert retry_counts == [1, 2]

    def test_exponential_delay(self):
        """測試指數延遲增長"""
        start_times = []

        @retry_with_exponential_backoff(
            max_retries=3, initial_delay=0.05, exponential_base=2.0, max_delay=1.0
        )
        def record_times():
            start_times.append(time.time())
            if len(start_times) < 3:
                raise ValueError("失敗")
            return "success"

        record_times()

        # 檢查延遲是否大致符合指數增長
        # 第一次延遲約 0.05 秒，第二次約 0.1 秒
        if len(start_times) >= 2:
            delay1 = start_times[1] - start_times[0]
            assert delay1 >= 0.04  # 允許一些誤差

        if len(start_times) >= 3:
            delay2 = start_times[2] - start_times[1]
            assert delay2 >= 0.08  # 應該約為 0.1 秒


@pytest.mark.unit
class TestRetryContext:
    """測試重試上下文管理器"""

    def test_successful_first_attempt(self):
        """測試第一次嘗試成功"""
        retry_ctx = RetryContext(max_retries=3, initial_delay=0.01)

        for attempt in retry_ctx:
            result = "success"
            retry_ctx.mark_success()
            break

        assert retry_ctx.succeeded is True
        assert retry_ctx.last_exception is None

    def test_retry_until_success(self):
        """測試重試直到成功"""
        retry_ctx = RetryContext(max_retries=3, initial_delay=0.01)
        attempt_count = 0

        for attempt in retry_ctx:
            attempt_count += 1
            try:
                if attempt_count < 2:
                    raise ValueError("模擬失敗")
                result = "success"
                retry_ctx.mark_success()
                break
            except ValueError as e:
                retry_ctx.handle_exception(e)

        assert retry_ctx.succeeded is True
        assert attempt_count == 2

    def test_max_retries_exceeded_context(self):
        """測試上下文管理器超過最大重試"""
        retry_ctx = RetryContext(max_retries=2, initial_delay=0.01)

        with pytest.raises(ValueError, match="總是失敗"):
            for attempt in retry_ctx:
                try:
                    raise ValueError("總是失敗")
                except ValueError as e:
                    retry_ctx.handle_exception(e)

        assert retry_ctx.succeeded is False
        assert retry_ctx.last_exception is not None

    def test_context_iteration(self):
        """測試上下文迭代"""
        retry_ctx = RetryContext(max_retries=2, initial_delay=0.01)
        attempts = list(retry_ctx)

        # 應該生成 0, 1, 2 (初次 + 2 次重試)
        assert attempts == [0, 1, 2]


@pytest.mark.unit
class TestRetryOnNetworkError:
    """測試網絡錯誤重試裝飾器"""

    def test_retry_on_connection_error(self):
        """測試連接錯誤重試"""
        call_count = 0

        @retry_on_network_error(max_retries=2, initial_delay=0.01)
        def fail_then_succeed():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ConnectionError("連接失敗")
            return "success"

        result = fail_then_succeed()
        assert result == "success"
        assert call_count == 2

    def test_retry_on_timeout_error(self):
        """測試超時錯誤重試"""
        call_count = 0

        @retry_on_network_error(max_retries=2, initial_delay=0.01)
        def timeout_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise TimeoutError("請求超時")
            return "success"

        result = timeout_func()
        assert result == "success"
        assert call_count == 2


@pytest.mark.unit
class TestRetryPreservesFunctionMetadata:
    """測試重試裝飾器保留函數元數據"""

    def test_preserves_function_name(self):
        """測試保留函數名稱"""

        @retry_with_exponential_backoff(max_retries=1, initial_delay=0.01)
        def my_function():
            """這是一個測試函數"""
            return "result"

        assert my_function.__name__ == "my_function"
        assert my_function.__doc__ == "這是一個測試函數"

    def test_preserves_function_with_args(self):
        """測試帶參數的函數"""

        @retry_with_exponential_backoff(max_retries=1, initial_delay=0.01)
        def func_with_args(a, b, c=None):
            return a + b + (c or 0)

        assert func_with_args(1, 2) == 3
        assert func_with_args(1, 2, c=3) == 6

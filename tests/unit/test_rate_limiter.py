"""速率限制模組的單元測試"""

import time
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from llm_agent_demo.utils.exceptions import RateLimitError
from llm_agent_demo.utils.rate_limiter import (
    GlobalRateLimiter,
    RateLimiter,
    RateLimitStrategy,
    SlidingWindow,
    TokenBucket,
    get_global_limiter,
    rate_limit,
)


class TestTokenBucket:
    """測試令牌桶實現"""

    def test_initialization(self):
        """測試令牌桶初始化"""
        bucket = TokenBucket(capacity=10.0, refill_rate=1.0)

        assert bucket.capacity == 10.0
        assert bucket.refill_rate == 1.0
        assert bucket.tokens == 10.0  # 初始時桶是滿的

    def test_consume_success(self):
        """測試成功消費令牌"""
        bucket = TokenBucket(capacity=10.0, refill_rate=1.0)

        # 消費 3 個令牌
        assert bucket.consume(3.0) is True
        assert bucket.tokens == pytest.approx(7.0, rel=1e-3)

        # 再消費 2 個令牌
        assert bucket.consume(2.0) is True
        assert bucket.tokens == pytest.approx(5.0, rel=1e-3)

    def test_consume_failure(self):
        """測試令牌不足時無法消費"""
        bucket = TokenBucket(capacity=10.0, refill_rate=1.0)

        # 消費 8 個令牌
        assert bucket.consume(8.0) is True
        assert bucket.tokens == pytest.approx(2.0, rel=1e-3)

        # 嘗試消費 5 個令牌（不足）
        assert bucket.consume(5.0) is False
        assert bucket.tokens == pytest.approx(2.0, rel=1e-3)  # 令牌數不變

    def test_refill(self):
        """測試令牌補充"""
        bucket = TokenBucket(capacity=10.0, refill_rate=2.0)  # 每秒補充 2 個令牌

        # 消費 8 個令牌
        bucket.consume(8.0)
        assert bucket.tokens == 2.0

        # 等待 1 秒，應該補充 2 個令牌
        time.sleep(1.1)
        bucket._refill()
        assert bucket.tokens >= 3.9  # 允許一點誤差

    def test_refill_not_exceed_capacity(self):
        """測試令牌補充不會超過容量"""
        bucket = TokenBucket(capacity=10.0, refill_rate=5.0)

        # 消費 3 個令牌
        bucket.consume(3.0)
        assert bucket.tokens == 7.0

        # 等待足夠長時間
        time.sleep(2.0)
        bucket._refill()

        # 令牌數不應超過容量
        assert bucket.tokens <= 10.0

    def test_get_wait_time(self):
        """測試獲取等待時間"""
        bucket = TokenBucket(capacity=10.0, refill_rate=2.0)

        # 消費 9 個令牌
        bucket.consume(9.0)
        assert bucket.tokens == 1.0

        # 需要 5 個令牌，需要等待 (5-1)/2 = 2 秒
        wait_time = bucket.get_wait_time(5.0)
        assert abs(wait_time - 2.0) < 0.1

    def test_reset(self):
        """測試重置令牌桶"""
        bucket = TokenBucket(capacity=10.0, refill_rate=1.0)

        # 消費一些令牌
        bucket.consume(7.0)
        assert bucket.tokens == 3.0

        # 重置
        bucket.reset()
        assert bucket.tokens == 10.0

    def test_thread_safety(self):
        """測試線程安全性"""
        import threading

        bucket = TokenBucket(capacity=100.0, refill_rate=10.0)
        results = []

        def consume_tokens():
            for _ in range(10):
                result = bucket.consume(1.0)
                results.append(result)
                time.sleep(0.01)

        # 創建多個線程同時消費
        threads = [threading.Thread(target=consume_tokens) for _ in range(5)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # 檢查總共成功消費的令牌數不超過容量
        successful_consumes = sum(1 for r in results if r)
        assert successful_consumes <= 100


class TestSlidingWindow:
    """測試滑動窗口實現"""

    def test_initialization(self):
        """測試滑動窗口初始化"""
        window = SlidingWindow(max_requests=10, window_seconds=60.0)

        assert window.max_requests == 10
        assert window.window_seconds == 60.0
        assert len(window.requests) == 0

    def test_allow_request_success(self):
        """測試成功允許請求"""
        window = SlidingWindow(max_requests=3, window_seconds=60.0)

        assert window.allow_request() is True
        assert window.allow_request() is True
        assert window.allow_request() is True
        assert len(window.requests) == 3

    def test_allow_request_failure(self):
        """測試達到限制後拒絕請求"""
        window = SlidingWindow(max_requests=3, window_seconds=60.0)

        # 前 3 個請求成功
        for _ in range(3):
            assert window.allow_request() is True

        # 第 4 個請求失敗
        assert window.allow_request() is False
        assert len(window.requests) == 3

    def test_clean_old_requests(self):
        """測試清除過期請求"""
        window = SlidingWindow(max_requests=3, window_seconds=1.0)

        # 添加 3 個請求
        for _ in range(3):
            window.allow_request()

        assert len(window.requests) == 3
        assert window.allow_request() is False

        # 等待窗口過期
        time.sleep(1.1)

        # 舊請求應該被清除，新請求應該成功
        assert window.allow_request() is True
        assert len(window.requests) == 1

    def test_get_current_count(self):
        """測試獲取當前請求數"""
        window = SlidingWindow(max_requests=5, window_seconds=60.0)

        assert window.get_current_count() == 0

        window.allow_request()
        window.allow_request()
        assert window.get_current_count() == 2

    def test_get_wait_time(self):
        """測試獲取等待時間"""
        window = SlidingWindow(max_requests=2, window_seconds=2.0)

        # 添加 2 個請求
        window.allow_request()
        time.sleep(0.5)
        window.allow_request()

        # 獲取等待時間（應該等待直到第一個請求過期）
        wait_time = window.get_wait_time()
        assert 1.0 < wait_time < 2.0

    def test_reset(self):
        """測試重置滑動窗口"""
        window = SlidingWindow(max_requests=3, window_seconds=60.0)

        # 添加一些請求
        window.allow_request()
        window.allow_request()
        assert len(window.requests) == 2

        # 重置
        window.reset()
        assert len(window.requests) == 0


class TestRateLimiter:
    """測試速率限制器"""

    def test_initialization_token_bucket(self):
        """測試使用令牌桶策略初始化"""
        limiter = RateLimiter(
            max_calls=10,
            window_seconds=60,
            strategy=RateLimitStrategy.TOKEN_BUCKET,
        )

        assert limiter.max_calls == 10
        assert limiter.window_seconds == 60
        assert limiter.strategy == RateLimitStrategy.TOKEN_BUCKET

    def test_initialization_sliding_window(self):
        """測試使用滑動窗口策略初始化"""
        limiter = RateLimiter(
            max_calls=10,
            window_seconds=60,
            strategy=RateLimitStrategy.SLIDING_WINDOW,
        )

        assert limiter.strategy == RateLimitStrategy.SLIDING_WINDOW

    def test_initialization_with_string_strategy(self):
        """測試使用字符串指定策略"""
        limiter = RateLimiter(max_calls=10, window_seconds=60, strategy="token_bucket")

        assert limiter.strategy == RateLimitStrategy.TOKEN_BUCKET

    def test_allow_request_different_identifiers(self):
        """測試不同標識符獨立限制"""
        limiter = RateLimiter(max_calls=2, window_seconds=60, strategy="sliding_window")

        # user1 的請求
        assert limiter.allow_request("user1") is True
        assert limiter.allow_request("user1") is True
        assert limiter.allow_request("user1") is False

        # user2 的請求應該不受影響
        assert limiter.allow_request("user2") is True
        assert limiter.allow_request("user2") is True

    def test_allow_request_with_raise_on_limit(self):
        """測試達到限制時拋出異常"""
        limiter = RateLimiter(max_calls=1, window_seconds=60, strategy="sliding_window")

        # 第一個請求成功
        assert limiter.allow_request("user1", raise_on_limit=True) is True

        # 第二個請求應該拋出異常
        with pytest.raises(RateLimitError) as exc_info:
            limiter.allow_request("user1", raise_on_limit=True)

        assert "Rate limit exceeded" in str(exc_info.value)
        assert exc_info.value.retry_after is not None

    def test_get_status_token_bucket(self):
        """測試獲取令牌桶狀態"""
        limiter = RateLimiter(max_calls=10, window_seconds=60, strategy="token_bucket")

        limiter.allow_request("user1", tokens=3)

        status = limiter.get_status("user1")
        assert status["identifier"] == "user1"
        assert status["strategy"] == "token_bucket"
        assert status["max_calls"] == 10
        assert status["available_tokens"] == pytest.approx(7.0, rel=1e-3)
        assert status["capacity"] == 10.0

    def test_get_status_sliding_window(self):
        """測試獲取滑動窗口狀態"""
        limiter = RateLimiter(max_calls=5, window_seconds=60, strategy="sliding_window")

        limiter.allow_request("user1")
        limiter.allow_request("user1")

        status = limiter.get_status("user1")
        assert status["identifier"] == "user1"
        assert status["strategy"] == "sliding_window"
        assert status["current_requests"] == 2
        assert status["remaining_requests"] == 3

    def test_reset_specific_identifier(self):
        """測試重置特定標識符"""
        limiter = RateLimiter(max_calls=2, window_seconds=60, strategy="sliding_window")

        # 達到限制
        limiter.allow_request("user1")
        limiter.allow_request("user1")
        assert limiter.allow_request("user1") is False

        # 重置
        limiter.reset("user1")

        # 現在應該可以再次請求
        assert limiter.allow_request("user1") is True

    def test_reset_all_identifiers(self):
        """測試重置所有標識符"""
        limiter = RateLimiter(max_calls=1, window_seconds=60, strategy="sliding_window")

        limiter.allow_request("user1")
        limiter.allow_request("user2")

        # 重置所有
        limiter.reset()

        # 兩個用戶都應該可以再次請求
        assert limiter.allow_request("user1") is True
        assert limiter.allow_request("user2") is True

    def test_cleanup_expired(self):
        """測試清理過期的限制器"""
        limiter = RateLimiter(max_calls=10, window_seconds=60, strategy="token_bucket")

        # 創建一些限制器
        limiter.allow_request("user1")
        limiter.allow_request("user2")
        limiter.allow_request("user3")

        # 確認有 3 個限制器
        assert len(limiter._limiters) == 3

        # 清理（使用較長的過期時間，確保沒有被清理）
        cleaned = limiter.cleanup_expired(inactive_seconds=3600)
        assert cleaned == 0  # 沒有過期的
        assert len(limiter._limiters) == 3

        # 使用較短的過期時間測試
        cleaned = limiter.cleanup_expired(inactive_seconds=0)
        # 所有的都應該被視為"過期"（因為 inactive_seconds=0）
        assert cleaned >= 0


class TestRateLimitDecorator:
    """測試速率限制裝飾器"""

    def test_decorator_basic(self):
        """測試基本的裝飾器功能"""

        @rate_limit(max_calls=2, window_seconds=60, raise_on_limit=False)
        def my_function():
            return "success"

        # 前兩次調用成功
        assert my_function() == "success"
        assert my_function() == "success"

        # 第三次調用返回 None（達到限制）
        assert my_function() is None

    def test_decorator_with_identifier(self):
        """測試使用標識符的裝飾器"""

        @rate_limit(
            max_calls=2,
            window_seconds=60,
            identifier_key="user_id",
            raise_on_limit=False,
        )
        def api_call(user_id: str, data: str):
            return f"Processed: {data}"

        # user1 的調用
        assert api_call(user_id="user1", data="data1") == "Processed: data1"
        assert api_call(user_id="user1", data="data2") == "Processed: data2"
        assert api_call(user_id="user1", data="data3") is None

        # user2 的調用不受影響
        assert api_call(user_id="user2", data="data1") == "Processed: data1"

    def test_decorator_with_raise_on_limit(self):
        """測試裝飾器在達到限制時拋出異常"""

        @rate_limit(max_calls=1, window_seconds=60, raise_on_limit=True)
        def my_function():
            return "success"

        # 第一次調用成功
        assert my_function() == "success"

        # 第二次調用拋出異常
        with pytest.raises(RateLimitError):
            my_function()

    def test_decorator_with_tokens(self):
        """測試裝飾器使用令牌"""

        @rate_limit(
            max_calls=10,
            window_seconds=60,
            strategy="token_bucket",
            tokens_key="cost",
            raise_on_limit=False,
        )
        def expensive_operation(cost: float):
            return f"Operation with cost {cost}"

        # 消費 7 個令牌
        assert expensive_operation(cost=7.0) == "Operation with cost 7.0"

        # 嘗試再消費 5 個令牌（不足）
        assert expensive_operation(cost=5.0) is None

        # 消費 2 個令牌（成功）
        assert expensive_operation(cost=2.0) == "Operation with cost 2.0"

    def test_decorator_sliding_window_strategy(self):
        """測試裝飾器使用滑動窗口策略"""

        @rate_limit(
            max_calls=3,
            window_seconds=1,
            strategy="sliding_window",
            raise_on_limit=False,
        )
        def my_function():
            return "success"

        # 前 3 次成功
        for _ in range(3):
            assert my_function() == "success"

        # 第 4 次失敗
        assert my_function() is None

        # 等待窗口過期
        time.sleep(1.1)

        # 現在應該可以再次調用
        assert my_function() == "success"


class TestGlobalRateLimiter:
    """測試全局速率限制器"""

    def test_add_and_get_limiter(self):
        """測試添加和獲取限制器"""
        global_limiter = GlobalRateLimiter()

        # 添加限制器
        limiter = global_limiter.add_limiter(
            "api_v1",
            max_calls=10,
            window_seconds=60,
        )

        assert limiter is not None
        assert limiter.max_calls == 10

        # 獲取限制器
        retrieved = global_limiter.get_limiter("api_v1")
        assert retrieved is limiter

    def test_allow_request(self):
        """測試全局限制器的請求允許"""
        global_limiter = GlobalRateLimiter()

        global_limiter.add_limiter("api_v1", max_calls=2, window_seconds=60)

        # 前兩次請求成功
        assert global_limiter.allow_request("api_v1", "user1") is True
        assert global_limiter.allow_request("api_v1", "user1") is True

        # 第三次請求失敗
        assert global_limiter.allow_request("api_v1", "user1") is False

    def test_allow_request_unknown_limiter(self):
        """測試未知限制器默認允許請求"""
        global_limiter = GlobalRateLimiter()

        # 未配置的限制器應該允許請求
        assert global_limiter.allow_request("unknown", "user1") is True

    def test_get_status(self):
        """測試獲取狀態"""
        global_limiter = GlobalRateLimiter()

        global_limiter.add_limiter(
            "api_v1",
            max_calls=5,
            window_seconds=60,
            strategy="sliding_window",
        )

        global_limiter.allow_request("api_v1", "user1")

        status = global_limiter.get_status("api_v1", "user1")
        assert status is not None
        assert status["current_requests"] == 1

    def test_reset_specific_limiter(self):
        """測試重置特定限制器"""
        global_limiter = GlobalRateLimiter()

        global_limiter.add_limiter("api_v1", max_calls=1, window_seconds=60)

        # 達到限制
        global_limiter.allow_request("api_v1", "user1")
        assert global_limiter.allow_request("api_v1", "user1") is False

        # 重置
        global_limiter.reset("api_v1", "user1")

        # 現在應該可以再次請求
        assert global_limiter.allow_request("api_v1", "user1") is True

    def test_reset_all_limiters(self):
        """測試重置所有限制器"""
        global_limiter = GlobalRateLimiter()

        global_limiter.add_limiter("api_v1", max_calls=1, window_seconds=60)
        global_limiter.add_limiter("api_v2", max_calls=1, window_seconds=60)

        # 兩個 API 都達到限制
        global_limiter.allow_request("api_v1", "user1")
        global_limiter.allow_request("api_v2", "user1")

        # 重置所有
        global_limiter.reset()

        # 兩個都應該可以再次請求
        assert global_limiter.allow_request("api_v1", "user1") is True
        assert global_limiter.allow_request("api_v2", "user1") is True

    def test_get_global_limiter(self):
        """測試獲取全局限制器實例"""
        limiter1 = get_global_limiter()
        limiter2 = get_global_limiter()

        # 應該是同一個實例
        assert limiter1 is limiter2
        assert isinstance(limiter1, GlobalRateLimiter)


class TestEdgeCases:
    """測試邊緣情況"""

    def test_zero_window_seconds(self):
        """測試零窗口時間"""
        # 這應該導致非常高的補充速率
        limiter = RateLimiter(max_calls=10, window_seconds=0.1, strategy="token_bucket")

        # 應該能夠快速恢復
        for _ in range(10):
            limiter.allow_request("user1")

        time.sleep(0.2)

        # 令牌應該已經補充
        assert limiter.allow_request("user1") is True

    def test_fractional_tokens(self):
        """測試小數令牌"""
        bucket = TokenBucket(capacity=10.0, refill_rate=1.0)

        # 消費小數令牌
        assert bucket.consume(0.5) is True
        assert bucket.consume(0.3) is True
        assert bucket.tokens == pytest.approx(9.2, 0.01)

    def test_concurrent_access(self):
        """測試並發訪問"""
        import threading

        limiter = RateLimiter(max_calls=100, window_seconds=60, strategy="sliding_window")
        success_count = [0]
        lock = threading.Lock()

        def make_requests():
            for _ in range(20):
                if limiter.allow_request("user1"):
                    with lock:
                        success_count[0] += 1

        # 創建多個線程
        threads = [threading.Thread(target=make_requests) for _ in range(10)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # 成功的請求數不應超過限制
        assert success_count[0] <= 100

"""
整合測試 - CostTracker + Retry 協同工作

測試成本追蹤器與重試機制的整合，模擬實際 API 調用場景。
"""

import time
import pytest
from pathlib import Path

from llm_agent_demo.utils.cost_tracker import CostTracker, TokenCounter, PRICING
from llm_agent_demo.utils.retry import (
    retry_with_exponential_backoff,
    retry_on_rate_limit,
    retry_on_network_error,
    RetryContext,
)
from llm_agent_demo.utils.logger import setup_logging, get_logger
from llm_agent_demo.utils.exceptions import (
    MaxRetriesExceededError,
    ValidationError,
)


@pytest.mark.integration
class TestCostTrackerRetryIntegration:
    """測試 CostTracker 與 Retry 的整合"""

    def test_cost_tracking_with_retry_success(
        self, cost_tracker_with_file, reset_logging, temp_log_file
    ):
        """測試成功重試後的成本追蹤"""
        # 設置日誌
        setup_logging(
            level="INFO",
            log_file=str(temp_log_file),
            force_reconfigure=True
        )
        logger = get_logger(__name__)

        tracker = cost_tracker_with_file

        # 模擬 API 調用計數器
        call_count = {"count": 0}

        @retry_with_exponential_backoff(
            max_retries=3,
            initial_delay=0.1,
            exponential_base=2.0,
        )
        def mock_api_call():
            """模擬可能失敗的 API 調用"""
            call_count["count"] += 1
            logger.info(f"API 調用嘗試 #{call_count['count']}")

            # 前兩次調用失敗
            if call_count["count"] < 3:
                raise ConnectionError("模擬網絡錯誤")

            # 第三次成功
            logger.info("API 調用成功")
            return {
                "usage": {
                    "prompt_tokens": 100,
                    "completion_tokens": 50,
                    "total_tokens": 150,
                }
            }

        # 執行帶重試的 API 調用
        response = mock_api_call()

        # 記錄使用情況
        usage = tracker.track_usage(
            prompt_tokens=response["usage"]["prompt_tokens"],
            completion_tokens=response["usage"]["completion_tokens"],
            model="gpt-4o-mini",
            provider="openai",
        )

        # 驗證
        assert call_count["count"] == 3  # 重試了2次，第3次成功
        assert usage.total_tokens == 150
        assert tracker.get_total_cost() > 0

        # 檢查日誌
        log_content = temp_log_file.read_text()
        assert "API 調用嘗試" in log_content
        assert "API 調用成功" in log_content

    def test_cost_tracking_with_retry_failure(
        self, cost_tracker_with_file, reset_logging, temp_log_file
    ):
        """測試重試失敗時的成本追蹤"""
        # 設置日誌
        setup_logging(
            level="ERROR",
            log_file=str(temp_log_file),
            force_reconfigure=True
        )
        logger = get_logger(__name__)

        tracker = cost_tracker_with_file

        # 記錄初始統計
        initial_requests = len(tracker.usage_history)

        # 模擬總是失敗的 API 調用
        @retry_with_exponential_backoff(
            max_retries=2,
            initial_delay=0.1,
        )
        def failing_api_call():
            """總是失敗的 API 調用"""
            logger.error("API 調用失敗")
            raise ConnectionError("持續的網絡錯誤")

        # 執行並捕獲異常
        with pytest.raises(MaxRetriesExceededError):
            failing_api_call()

        # 驗證：沒有記錄任何成本（因為調用失敗了）
        assert len(tracker.usage_history) == initial_requests

        # 檢查日誌
        log_content = temp_log_file.read_text()
        assert "API 調用失敗" in log_content

    def test_multiple_retries_with_cost_accumulation(
        self, cost_tracker_with_file, reset_logging, temp_log_file
    ):
        """測試多次重試與成本累積"""
        # 設置日誌
        setup_logging(
            level="INFO",
            log_file=str(temp_log_file),
            force_reconfigure=True
        )
        logger = get_logger(__name__)

        tracker = cost_tracker_with_file

        # 模擬多個 API 調用，每個都可能需要重試
        results = []

        for i in range(3):
            attempt_count = {"count": 0}

            @retry_with_exponential_backoff(
                max_retries=2,
                initial_delay=0.05,
            )
            def api_call_with_retry():
                attempt_count["count"] += 1
                logger.info(f"請求 #{i+1}, 嘗試 #{attempt_count['count']}")

                # 每個請求第一次失敗，第二次成功
                if attempt_count["count"] < 2:
                    raise ConnectionError("暫時性錯誤")

                return {
                    "usage": {
                        "prompt_tokens": 50 * (i + 1),
                        "completion_tokens": 25 * (i + 1),
                    }
                }

            # 執行調用
            response = api_call_with_retry()
            results.append(response)

            # 記錄成本
            tracker.track_usage(
                prompt_tokens=response["usage"]["prompt_tokens"],
                completion_tokens=response["usage"]["completion_tokens"],
                model="gpt-4o-mini",
                provider="openai",
            )

        # 驗證
        assert len(results) == 3
        assert len(tracker.usage_history) == 3

        # 計算預期的總 tokens
        expected_prompt = 50 + 100 + 150  # 50*1 + 50*2 + 50*3
        expected_completion = 25 + 50 + 75  # 25*1 + 25*2 + 25*3

        total_tokens = tracker.get_total_tokens()
        assert total_tokens["prompt_tokens"] == expected_prompt
        assert total_tokens["completion_tokens"] == expected_completion

    def test_retry_context_with_cost_tracking(
        self, cost_tracker_with_file, reset_logging, temp_log_file
    ):
        """測試使用 RetryContext 進行成本追蹤"""
        # 設置日誌
        setup_logging(
            level="INFO",
            log_file=str(temp_log_file),
            force_reconfigure=True
        )
        logger = get_logger(__name__)

        tracker = cost_tracker_with_file

        # 使用 RetryContext
        retry_ctx = RetryContext(
            max_retries=3,
            initial_delay=0.05,
            exponential_base=2.0,
        )

        attempt_count = 0
        result = None

        for attempt in retry_ctx:
            try:
                attempt_count += 1
                logger.info(f"嘗試 #{attempt_count}")

                # 前兩次失敗
                if attempt_count < 3:
                    raise ValueError("模擬錯誤")

                # 成功
                result = {
                    "usage": {
                        "prompt_tokens": 200,
                        "completion_tokens": 100,
                    }
                }

                retry_ctx.mark_success()
                break

            except ValueError as e:
                retry_ctx.handle_exception(e)

        # 驗證成功
        assert retry_ctx.succeeded
        assert result is not None

        # 記錄成本
        tracker.track_usage(
            prompt_tokens=result["usage"]["prompt_tokens"],
            completion_tokens=result["usage"]["completion_tokens"],
            model="gpt-4o-mini",
            provider="openai",
        )

        # 驗證成本記錄
        summary = tracker.get_summary()
        assert summary["total_requests"] >= 1

    def test_rate_limit_retry_with_cost_tracking(
        self, cost_tracker_with_file, reset_logging, temp_log_file
    ):
        """測試速率限制重試與成本追蹤"""
        # 設置日誌
        setup_logging(
            level="WARNING",
            log_file=str(temp_log_file),
            force_reconfigure=True
        )
        logger = get_logger(__name__)

        tracker = cost_tracker_with_file

        rate_limit_count = {"count": 0}

        @retry_with_exponential_backoff(
            max_retries=2,
            initial_delay=0.1,
            exceptions=(Exception,),  # 捕獲所有異常進行測試
        )
        def api_call_with_rate_limit():
            """模擬速率限制的 API 調用"""
            rate_limit_count["count"] += 1

            # 第一次觸發速率限制
            if rate_limit_count["count"] == 1:
                logger.warning("遇到速率限制")
                raise Exception("Rate limit exceeded")

            # 第二次成功
            logger.info("API 調用成功")
            return {
                "usage": {
                    "prompt_tokens": 150,
                    "completion_tokens": 75,
                }
            }

        # 執行調用
        response = api_call_with_rate_limit()

        # 記錄成本
        tracker.track_usage(
            prompt_tokens=response["usage"]["prompt_tokens"],
            completion_tokens=response["usage"]["completion_tokens"],
            model="gpt-4o-mini",
            provider="openai",
        )

        # 驗證
        assert rate_limit_count["count"] == 2
        assert tracker.get_total_cost() > 0

        # 檢查日誌
        log_content = temp_log_file.read_text()
        assert "遇到速率限制" in log_content


@pytest.mark.integration
class TestCostTrackerPersistenceWithRetry:
    """測試成本追蹤器持久化與重試的整合"""

    def test_cost_persistence_across_retries(
        self, temp_cost_tracker_file, reset_logging, temp_log_file
    ):
        """測試跨重試的成本持久化"""
        # 設置日誌
        setup_logging(
            level="INFO",
            log_file=str(temp_log_file),
            force_reconfigure=True
        )
        logger = get_logger(__name__)

        # 創建第一個追蹤器實例
        tracker1 = CostTracker(
            save_path=str(temp_cost_tracker_file),
            auto_save_interval=1  # 每次都保存
        )

        # 模擬帶重試的 API 調用
        @retry_with_exponential_backoff(max_retries=2, initial_delay=0.05)
        def api_call_1():
            raise ConnectionError("First call error")

        @retry_with_exponential_backoff(max_retries=2, initial_delay=0.05)
        def api_call_2():
            return {"usage": {"prompt_tokens": 100, "completion_tokens": 50}}

        # 第一個調用失敗
        try:
            api_call_1()
        except MaxRetriesExceededError:
            logger.info("第一個調用失敗（預期）")

        # 第二個調用成功
        response2 = api_call_2()
        tracker1.track_usage(
            prompt_tokens=response2["usage"]["prompt_tokens"],
            completion_tokens=response2["usage"]["completion_tokens"],
            model="gpt-4o-mini",
            provider="openai",
        )

        # 獲取第一個追蹤器的統計
        summary1 = tracker1.get_summary()
        total_cost1 = tracker1.get_total_cost()

        # 創建第二個追蹤器實例（從文件載入）
        tracker2 = CostTracker(save_path=str(temp_cost_tracker_file))

        # 驗證數據持久化
        summary2 = tracker2.get_summary()
        total_cost2 = tracker2.get_total_cost()

        assert summary1["total_requests"] == summary2["total_requests"]
        assert total_cost1 == total_cost2
        assert len(tracker2.usage_history) == 1

    def test_auto_save_during_retry_operations(
        self, temp_cost_tracker_file, reset_logging, temp_log_file
    ):
        """測試重試操作期間的自動保存"""
        # 設置日誌
        setup_logging(
            level="INFO",
            log_file=str(temp_log_file),
            force_reconfigure=True
        )
        logger = get_logger(__name__)

        # 創建追蹤器，設置較小的自動保存間隔
        tracker = CostTracker(
            save_path=str(temp_cost_tracker_file),
            auto_save_interval=2  # 每2次記錄保存一次
        )

        # 執行多次帶重試的操作
        for i in range(5):
            attempt_count = {"count": 0}

            @retry_with_exponential_backoff(max_retries=1, initial_delay=0.05)
            def api_call():
                attempt_count["count"] += 1
                if attempt_count["count"] < 2:
                    raise ConnectionError("Temporary error")
                return {
                    "usage": {
                        "prompt_tokens": 10 * (i + 1),
                        "completion_tokens": 5 * (i + 1),
                    }
                }

            response = api_call()
            tracker.track_usage(
                prompt_tokens=response["usage"]["prompt_tokens"],
                completion_tokens=response["usage"]["completion_tokens"],
                model="gpt-4o-mini",
                provider="openai",
            )

            logger.info(f"記錄 #{i+1} 完成")

        # 驗證文件已保存
        assert temp_cost_tracker_file.exists()

        # 從文件載入並驗證
        new_tracker = CostTracker(save_path=str(temp_cost_tracker_file))
        assert len(new_tracker.usage_history) == 5


@pytest.mark.integration
class TestTokenEstimationWithRetry:
    """測試 Token 估算與重試的整合"""

    def test_token_estimation_before_api_call(
        self, cost_tracker_with_file, reset_logging, temp_log_file
    ):
        """測試在 API 調用前進行 token 估算"""
        # 設置日誌
        setup_logging(
            level="INFO",
            log_file=str(temp_log_file),
            force_reconfigure=True
        )
        logger = get_logger(__name__)

        tracker = cost_tracker_with_file

        # 模擬用戶輸入
        user_input = "請幫我分析這篇文章的主要觀點和論證邏輯"

        # 估算 tokens
        estimated_tokens = TokenCounter.estimate_tokens(user_input)
        logger.info(f"估算 prompt tokens: {estimated_tokens}")

        # 模擬帶重試的 API 調用
        @retry_with_exponential_backoff(max_retries=2, initial_delay=0.05)
        def api_call():
            # 模擬第一次失敗
            if not hasattr(api_call, "called"):
                api_call.called = True
                raise ConnectionError("Network error")

            # 第二次成功，返回實際 token 使用
            return {
                "usage": {
                    "prompt_tokens": 15,  # 實際值
                    "completion_tokens": 50,
                }
            }

        response = api_call()

        # 記錄實際使用
        tracker.track_usage(
            prompt_tokens=response["usage"]["prompt_tokens"],
            completion_tokens=response["usage"]["completion_tokens"],
            model="gpt-4o-mini",
            provider="openai",
        )

        # 驗證估算值與實際值的接近程度
        actual_tokens = response["usage"]["prompt_tokens"]
        logger.info(f"實際 prompt tokens: {actual_tokens}")
        logger.info(f"估算誤差: {abs(estimated_tokens - actual_tokens)}")

        # 檢查日誌
        log_content = temp_log_file.read_text()
        assert "估算 prompt tokens" in log_content
        assert "實際 prompt tokens" in log_content

    def test_cost_calculation_with_cached_pricing(
        self, cost_tracker_with_file
    ):
        """測試使用快取價格進行成本計算"""
        tracker = cost_tracker_with_file

        # 記錄多次使用同一模型
        for i in range(10):
            tracker.track_usage(
                prompt_tokens=100,
                completion_tokens=50,
                model="gpt-4o-mini",
                provider="openai",
            )

        # 驗證快取的成本計算
        summary = tracker.get_summary()

        # 手動計算預期成本
        pricing = PRICING["gpt-4o-mini"]
        expected_cost = 10 * (
            (100 / 1000) * pricing["prompt"] +
            (50 / 1000) * pricing["completion"]
        )

        assert abs(summary["total_cost"] - expected_cost) < 0.0001

    def test_retry_with_different_models(
        self, cost_tracker_with_file, reset_logging, temp_log_file
    ):
        """測試對不同模型進行重試並追蹤成本"""
        # 設置日誌
        setup_logging(
            level="INFO",
            log_file=str(temp_log_file),
            force_reconfigure=True
        )
        logger = get_logger(__name__)

        tracker = cost_tracker_with_file

        # 測試不同的模型
        models = [
            ("gpt-4o-mini", "openai", 100, 50),
            ("claude-3-5-haiku-20241022", "anthropic", 150, 75),
            ("gemini-2.0-flash-exp", "google", 200, 100),
        ]

        for model, provider, prompt_tokens, completion_tokens in models:
            attempt_count = {"count": 0}

            @retry_with_exponential_backoff(max_retries=1, initial_delay=0.05)
            def api_call():
                attempt_count["count"] += 1
                if attempt_count["count"] < 2:
                    raise ConnectionError("Temporary error")

                return {
                    "usage": {
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                    }
                }

            response = api_call()
            tracker.track_usage(
                prompt_tokens=response["usage"]["prompt_tokens"],
                completion_tokens=response["usage"]["completion_tokens"],
                model=model,
                provider=provider,
            )

            logger.info(f"記錄 {model} 使用情況")

        # 驗證按模型統計
        summary = tracker.get_summary()
        assert len(summary["models"]) == 3

        # 檢查每個模型都有記錄
        for model, _, _, _ in models:
            assert model in summary["models"]
            assert summary["models"][model]["count"] == 1

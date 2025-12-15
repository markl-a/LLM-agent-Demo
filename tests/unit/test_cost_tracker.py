"""cost_tracker 模組的單元測試"""

import json
import pytest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, mock_open
import tempfile
import os

from llm_agent_demo.utils.cost_tracker import (
    TokenUsage,
    TokenCounter,
    CostTracker,
    PRICING,
)


class TestTokenUsage:
    """測試 TokenUsage dataclass"""

    def test_token_usage_initialization(self):
        """測試 TokenUsage 初始化"""
        usage = TokenUsage(
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            model="gpt-4o",
            provider="openai",
        )

        assert usage.prompt_tokens == 100
        assert usage.completion_tokens == 50
        assert usage.total_tokens == 150
        assert usage.model == "gpt-4o"
        assert usage.provider == "openai"
        assert isinstance(usage.timestamp, datetime)

    def test_token_usage_default_values(self):
        """測試 TokenUsage 預設值"""
        usage = TokenUsage(
            prompt_tokens=100, completion_tokens=50, total_tokens=150
        )

        assert usage.model == ""
        assert usage.provider == ""
        assert isinstance(usage.timestamp, datetime)

    def test_token_usage_to_dict(self):
        """測試 TokenUsage.to_dict() 方法"""
        timestamp = datetime.now()
        usage = TokenUsage(
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            timestamp=timestamp,
            model="gpt-4o",
            provider="openai",
        )

        result = usage.to_dict()

        assert result["prompt_tokens"] == 100
        assert result["completion_tokens"] == 50
        assert result["total_tokens"] == 150
        assert result["timestamp"] == timestamp.isoformat()
        assert result["model"] == "gpt-4o"
        assert result["provider"] == "openai"

    def test_token_usage_to_dict_empty_strings(self):
        """測試 TokenUsage.to_dict() 處理空字串"""
        usage = TokenUsage(
            prompt_tokens=100, completion_tokens=50, total_tokens=150
        )

        result = usage.to_dict()

        assert result["model"] == ""
        assert result["provider"] == ""


class TestTokenCounter:
    """測試 TokenCounter 類"""

    def test_estimate_tokens_empty_string(self):
        """測試空字串的 token 估算"""
        assert TokenCounter.estimate_tokens("") == 0

    def test_estimate_tokens_english_text(self):
        """測試英文文本的 token 估算"""
        # "Hello World" 約 11 個字符，估計約 11/4 = 2.75 -> 2 tokens
        text = "Hello World"
        result = TokenCounter.estimate_tokens(text)
        assert result > 0
        assert isinstance(result, int)

    def test_estimate_tokens_chinese_text(self):
        """測試中文文本的 token 估算"""
        # "你好世界" 4 個中文字符，估計約 4/1.5 = 2.67 -> 2 tokens
        text = "你好世界"
        result = TokenCounter.estimate_tokens(text)
        assert result > 0
        assert isinstance(result, int)

    def test_estimate_tokens_mixed_text(self):
        """測試混合中英文的 token 估算"""
        text = "Hello 世界"
        result = TokenCounter.estimate_tokens(text)
        assert result > 0
        assert isinstance(result, int)

    def test_estimate_tokens_minimum_value(self):
        """測試最小 token 值為 1"""
        # 即使是很短的文本，也至少返回 1
        text = "a"
        result = TokenCounter.estimate_tokens(text)
        assert result >= 1

    def test_estimate_tokens_long_english_text(self):
        """測試長英文文本"""
        text = "This is a longer text to test token estimation." * 10
        result = TokenCounter.estimate_tokens(text)
        # 約 49 * 10 = 490 字符，約 490/4 = 122 tokens
        assert result > 100
        assert result < 200

    def test_estimate_tokens_long_chinese_text(self):
        """測試長中文文本"""
        text = "這是一段較長的中文文本用於測試" * 10
        result = TokenCounter.estimate_tokens(text)
        # 約 15 * 10 = 150 字符，約 150/1.5 = 100 tokens
        assert result > 50
        assert result < 150

    def test_estimate_tokens_with_special_characters(self):
        """測試包含特殊字符的文本"""
        text = "Hello! @#$ 世界 123"
        result = TokenCounter.estimate_tokens(text)
        assert result > 0


class TestCostTracker:
    """測試 CostTracker 類"""

    def test_cost_tracker_initialization_without_path(self):
        """測試不帶保存路徑的初始化"""
        tracker = CostTracker()

        assert tracker.usage_history == []
        assert tracker.save_path is None

    def test_cost_tracker_initialization_with_nonexistent_path(self):
        """測試帶不存在路徑的初始化"""
        tracker = CostTracker(save_path="/tmp/nonexistent_file.json")

        assert tracker.usage_history == []
        assert tracker.save_path == "/tmp/nonexistent_file.json"

    def test_track_usage_basic(self):
        """測試基本的使用記錄"""
        tracker = CostTracker()
        usage = tracker.track_usage(
            prompt_tokens=100,
            completion_tokens=50,
            model="gpt-4o",
            provider="openai",
        )

        assert len(tracker.usage_history) == 1
        assert usage.prompt_tokens == 100
        assert usage.completion_tokens == 50
        assert usage.total_tokens == 150
        assert usage.model == "gpt-4o"
        assert usage.provider == "openai"

    def test_track_usage_multiple_records(self):
        """測試多次記錄"""
        tracker = CostTracker()

        tracker.track_usage(100, 50, "gpt-4o", "openai")
        tracker.track_usage(200, 100, "claude-3-5-sonnet-20241022", "anthropic")
        tracker.track_usage(150, 75, "gpt-3.5-turbo", "openai")

        assert len(tracker.usage_history) == 3

    def test_track_usage_without_model(self):
        """測試不指定模型的記錄"""
        tracker = CostTracker()
        usage = tracker.track_usage(prompt_tokens=100, completion_tokens=50)

        assert usage.model == ""
        assert usage.provider == ""

    def test_calculate_cost_gpt4o(self):
        """測試 GPT-4o 的成本計算"""
        tracker = CostTracker()
        usage = TokenUsage(
            prompt_tokens=1000,
            completion_tokens=500,
            total_tokens=1500,
            model="gpt-4o",
        )

        cost = tracker.calculate_cost(usage)

        # prompt: 1000/1000 * 0.0025 = 0.0025
        # completion: 500/1000 * 0.01 = 0.005
        # total: 0.0075
        assert cost == pytest.approx(0.0075, rel=1e-6)

    def test_calculate_cost_claude_sonnet(self):
        """測試 Claude Sonnet 的成本計算"""
        tracker = CostTracker()
        usage = TokenUsage(
            prompt_tokens=2000,
            completion_tokens=1000,
            total_tokens=3000,
            model="claude-3-5-sonnet-20241022",
        )

        cost = tracker.calculate_cost(usage)

        # prompt: 2000/1000 * 0.003 = 0.006
        # completion: 1000/1000 * 0.015 = 0.015
        # total: 0.021
        assert cost == pytest.approx(0.021, rel=1e-6)

    def test_calculate_cost_case_insensitive(self):
        """測試成本計算的大小寫不敏感"""
        tracker = CostTracker()
        usage = TokenUsage(
            prompt_tokens=1000,
            completion_tokens=500,
            total_tokens=1500,
            model="GPT-4O",  # 大寫
        )

        cost = tracker.calculate_cost(usage)

        assert cost == pytest.approx(0.0075, rel=1e-6)

    def test_calculate_cost_partial_match(self):
        """測試成本計算的部分匹配"""
        tracker = CostTracker()
        usage = TokenUsage(
            prompt_tokens=1000,
            completion_tokens=500,
            total_tokens=1500,
            model="gpt-4-0125-preview",  # 應該匹配 gpt-4
        )

        cost = tracker.calculate_cost(usage)

        # 應該使用 gpt-4 的價格
        # prompt: 1000/1000 * 0.03 = 0.03
        # completion: 500/1000 * 0.06 = 0.03
        # total: 0.06
        assert cost == pytest.approx(0.06, rel=1e-6)

    def test_calculate_cost_unknown_model(self):
        """測試未知模型的成本計算"""
        tracker = CostTracker()
        usage = TokenUsage(
            prompt_tokens=1000,
            completion_tokens=500,
            total_tokens=1500,
            model="unknown-model-xyz",
        )

        cost = tracker.calculate_cost(usage)

        # 未知模型應該返回 0
        assert cost == 0.0

    def test_calculate_cost_free_model(self):
        """測試免費模型的成本計算"""
        tracker = CostTracker()
        usage = TokenUsage(
            prompt_tokens=1000,
            completion_tokens=500,
            total_tokens=1500,
            model="gemini-2.0-flash-exp",
        )

        cost = tracker.calculate_cost(usage)

        # 免費模型成本為 0
        assert cost == 0.0

    def test_get_total_cost_empty(self):
        """測試空歷史記錄的總成本"""
        tracker = CostTracker()
        total_cost = tracker.get_total_cost()

        assert total_cost == 0.0

    def test_get_total_cost_single_usage(self):
        """測試單次使用的總成本"""
        tracker = CostTracker()
        tracker.track_usage(1000, 500, "gpt-4o")

        total_cost = tracker.get_total_cost()

        assert total_cost == pytest.approx(0.0075, rel=1e-6)

    def test_get_total_cost_multiple_usages(self):
        """測試多次使用的總成本"""
        tracker = CostTracker()
        tracker.track_usage(1000, 500, "gpt-4o")
        tracker.track_usage(2000, 1000, "claude-3-5-sonnet-20241022")
        tracker.track_usage(1000, 500, "gpt-3.5-turbo")

        total_cost = tracker.get_total_cost()

        # gpt-4o: 0.0075 (1000/1000*0.0025 + 500/1000*0.01)
        # claude-3-5-sonnet: 0.021 (2000/1000*0.003 + 1000/1000*0.015)
        # gpt-3.5-turbo: 0.00125 (1000/1000*0.0005 + 500/1000*0.0015)
        expected = 0.0075 + 0.021 + 0.00125
        assert total_cost == pytest.approx(expected, rel=1e-6)

    def test_get_total_cost_with_time_filter(self):
        """測試帶時間篩選的總成本"""
        tracker = CostTracker()

        # 創建不同時間的使用記錄
        now = datetime.now()
        old_usage = TokenUsage(1000, 500, 1500, now - timedelta(days=2), "gpt-4o")
        recent_usage = TokenUsage(1000, 500, 1500, now - timedelta(hours=1), "gpt-4o")
        future_usage = TokenUsage(1000, 500, 1500, now + timedelta(days=1), "gpt-4o")

        tracker.usage_history = [old_usage, recent_usage, future_usage]

        # 測試 start_time 篩選
        total_cost = tracker.get_total_cost(start_time=now - timedelta(days=1))
        assert total_cost == pytest.approx(0.015, rel=1e-6)  # 2 次使用

        # 測試 end_time 篩選
        total_cost = tracker.get_total_cost(end_time=now)
        assert total_cost == pytest.approx(0.015, rel=1e-6)  # 2 次使用

        # 測試同時使用 start_time 和 end_time
        total_cost = tracker.get_total_cost(
            start_time=now - timedelta(days=1), end_time=now
        )
        assert total_cost == pytest.approx(0.0075, rel=1e-6)  # 1 次使用

    def test_get_total_tokens_empty(self):
        """測試空歷史記錄的總 token"""
        tracker = CostTracker()
        total_tokens = tracker.get_total_tokens()

        assert total_tokens["prompt_tokens"] == 0
        assert total_tokens["completion_tokens"] == 0
        assert total_tokens["total_tokens"] == 0

    def test_get_total_tokens_single_usage(self):
        """測試單次使用的總 token"""
        tracker = CostTracker()
        tracker.track_usage(1000, 500, "gpt-4o")

        total_tokens = tracker.get_total_tokens()

        assert total_tokens["prompt_tokens"] == 1000
        assert total_tokens["completion_tokens"] == 500
        assert total_tokens["total_tokens"] == 1500

    def test_get_total_tokens_multiple_usages(self):
        """測試多次使用的總 token"""
        tracker = CostTracker()
        tracker.track_usage(1000, 500, "gpt-4o")
        tracker.track_usage(2000, 1000, "claude-3-5-sonnet-20241022")
        tracker.track_usage(1500, 750, "gpt-3.5-turbo")

        total_tokens = tracker.get_total_tokens()

        assert total_tokens["prompt_tokens"] == 4500
        assert total_tokens["completion_tokens"] == 2250
        assert total_tokens["total_tokens"] == 6750

    def test_get_total_tokens_with_time_filter(self):
        """測試帶時間篩選的總 token"""
        tracker = CostTracker()

        now = datetime.now()
        old_usage = TokenUsage(1000, 500, 1500, now - timedelta(days=2), "gpt-4o")
        recent_usage = TokenUsage(2000, 1000, 3000, now - timedelta(hours=1), "gpt-4o")

        tracker.usage_history = [old_usage, recent_usage]

        # 只統計最近的
        total_tokens = tracker.get_total_tokens(start_time=now - timedelta(days=1))

        assert total_tokens["prompt_tokens"] == 2000
        assert total_tokens["completion_tokens"] == 1000
        assert total_tokens["total_tokens"] == 3000

    def test_get_summary_empty(self):
        """測試空歷史記錄的摘要"""
        tracker = CostTracker()
        summary = tracker.get_summary()

        assert summary["total_requests"] == 0
        assert summary["total_cost"] == 0.0
        assert summary["total_tokens"]["total_tokens"] == 0
        assert summary["models"] == {}

    def test_get_summary_single_model(self):
        """測試單一模型的摘要"""
        tracker = CostTracker()
        tracker.track_usage(1000, 500, "gpt-4o")

        summary = tracker.get_summary()

        assert summary["total_requests"] == 1
        assert summary["total_cost"] == pytest.approx(0.0075, rel=1e-6)
        assert summary["total_tokens"]["total_tokens"] == 1500
        assert "gpt-4o" in summary["models"]
        assert summary["models"]["gpt-4o"]["count"] == 1
        assert summary["models"]["gpt-4o"]["tokens"] == 1500
        assert summary["models"]["gpt-4o"]["cost"] == pytest.approx(0.0075, rel=1e-6)

    def test_get_summary_multiple_models(self):
        """測試多模型的摘要"""
        tracker = CostTracker()
        tracker.track_usage(1000, 500, "gpt-4o")
        tracker.track_usage(2000, 1000, "gpt-4o")
        tracker.track_usage(1000, 500, "claude-3-5-sonnet-20241022")

        summary = tracker.get_summary()

        assert summary["total_requests"] == 3
        assert "gpt-4o" in summary["models"]
        assert "claude-3-5-sonnet-20241022" in summary["models"]
        assert summary["models"]["gpt-4o"]["count"] == 2
        assert summary["models"]["gpt-4o"]["tokens"] == 4500
        assert summary["models"]["claude-3-5-sonnet-20241022"]["count"] == 1

    def test_get_summary_unknown_model(self):
        """測試未知模型的摘要"""
        tracker = CostTracker()
        tracker.track_usage(1000, 500, "")

        summary = tracker.get_summary()

        assert "unknown" in summary["models"]
        assert summary["models"]["unknown"]["count"] == 1

    def test_save_history_without_path(self):
        """測試沒有保存路徑時的保存操作"""
        tracker = CostTracker()
        tracker.track_usage(1000, 500, "gpt-4o")

        # 不應該拋出異常
        tracker.save_history()

    def test_save_history_with_path(self):
        """測試保存歷史記錄"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / "test_history.json"

            # 使用 auto_save_interval=1 以便每次記錄後立即保存
            tracker = CostTracker(save_path=str(temp_path), auto_save_interval=1)
            tracker.track_usage(1000, 500, "gpt-4o", "openai")

            # 驗證文件已創建並包含正確的數據
            assert temp_path.exists()

            with open(temp_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            assert len(data) == 1
            assert data[0]["prompt_tokens"] == 1000
            assert data[0]["completion_tokens"] == 500
            assert data[0]["model"] == "gpt-4o"
            assert data[0]["provider"] == "openai"

    def test_save_history_creates_directory(self):
        """測試保存時創建目錄"""
        with tempfile.TemporaryDirectory() as temp_dir:
            save_path = Path(temp_dir) / "subdir" / "data.json"

            # 使用 auto_save_interval=1 以便每次記錄後立即保存
            tracker = CostTracker(save_path=str(save_path), auto_save_interval=1)
            tracker.track_usage(1000, 500, "gpt-4o")

            assert save_path.exists()
            assert save_path.parent.exists()

    def test_load_history_without_path(self):
        """測試沒有保存路徑時的載入操作"""
        tracker = CostTracker()

        # 不應該拋出異常
        tracker.load_history()

        assert tracker.usage_history == []

    def test_load_history_with_nonexistent_file(self):
        """測試載入不存在的文件"""
        tracker = CostTracker(save_path="/tmp/nonexistent_file.json")

        # 不應該拋出異常
        tracker.load_history()

        assert tracker.usage_history == []

    def test_load_history_with_existing_file(self):
        """測試載入已存在的歷史記錄"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / "test_history.json"

            # 創建並保存數據（使用 auto_save_interval=1 以便每次記錄後立即保存）
            tracker1 = CostTracker(save_path=str(temp_path), auto_save_interval=1)
            tracker1.track_usage(1000, 500, "gpt-4o", "openai")
            tracker1.track_usage(2000, 1000, "claude-3-5-sonnet-20241022", "anthropic")

            # 創建新的追蹤器並載入
            tracker2 = CostTracker(save_path=str(temp_path))

            assert len(tracker2.usage_history) == 2
            assert tracker2.usage_history[0].prompt_tokens == 1000
            assert tracker2.usage_history[0].model == "gpt-4o"
            assert tracker2.usage_history[1].prompt_tokens == 2000
            assert tracker2.usage_history[1].model == "claude-3-5-sonnet-20241022"

    def test_save_and_load_preserves_timestamp(self):
        """測試保存和載入保留時間戳"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / "test_history.json"

            tracker1 = CostTracker(save_path=str(temp_path))
            original_time = datetime.now()
            tracker1.track_usage(1000, 500, "gpt-4o")
            tracker1.usage_history[0].timestamp = original_time
            tracker1.save_history()

            tracker2 = CostTracker(save_path=str(temp_path))

            # 時間應該保持一致（允許微小的精度損失）
            loaded_time = tracker2.usage_history[0].timestamp
            assert abs((loaded_time - original_time).total_seconds()) < 1

    def test_reset_without_path(self):
        """測試重置操作（無保存路徑）"""
        tracker = CostTracker()
        tracker.track_usage(1000, 500, "gpt-4o")

        tracker.reset()

        assert tracker.usage_history == []

    def test_reset_with_path(self):
        """測試重置操作（有保存路徑）"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / "test_history.json"

            # 使用 auto_save_interval=1 以便每次記錄後立即保存
            tracker = CostTracker(save_path=str(temp_path), auto_save_interval=1)
            tracker.track_usage(1000, 500, "gpt-4o")

            assert temp_path.exists()

            tracker.reset()

            assert tracker.usage_history == []
            assert not temp_path.exists()

    def test_print_summary(self, capsys):
        """測試打印摘要"""
        tracker = CostTracker()
        tracker.track_usage(1000, 500, "gpt-4o", "openai")
        tracker.track_usage(2000, 1000, "claude-3-5-sonnet-20241022", "anthropic")

        tracker.print_summary()

        captured = capsys.readouterr()
        output = captured.out

        # 驗證輸出包含關鍵信息
        assert "LLM API 使用摘要" in output
        assert "總請求次數: 2" in output
        assert "gpt-4o" in output
        assert "claude-3-5-sonnet-20241022" in output

    def test_print_summary_empty(self, capsys):
        """測試打印空摘要"""
        tracker = CostTracker()

        tracker.print_summary()

        captured = capsys.readouterr()
        output = captured.out

        assert "LLM API 使用摘要" in output
        assert "總請求次數: 0" in output

    def test_track_usage_auto_save(self):
        """測試自動保存功能"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / "test_history.json"

            # 使用 auto_save_interval=1 以便每次記錄後立即保存
            tracker = CostTracker(save_path=str(temp_path), auto_save_interval=1)

            # 每次 track_usage 都應該自動保存
            tracker.track_usage(1000, 500, "gpt-4o")

            # 立即檢查文件
            with open(temp_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            assert len(data) == 1

            # 再追蹤一次
            tracker.track_usage(2000, 1000, "claude-3-5-sonnet-20241022")

            with open(temp_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            assert len(data) == 2

    def test_embedding_model_cost(self):
        """測試嵌入模型的成本計算"""
        tracker = CostTracker()
        usage = TokenUsage(
            prompt_tokens=1000,
            completion_tokens=0,
            total_tokens=1000,
            model="text-embedding-3-small",
        )

        cost = tracker.calculate_cost(usage)

        # 嵌入模型只有輸入成本
        # 1000/1000 * 0.00002 = 0.00002
        assert cost == pytest.approx(0.00002, rel=1e-6)

    def test_concurrent_models_tracking(self):
        """測試同時追蹤多個模型"""
        tracker = CostTracker()

        # 添加各種模型的使用記錄
        tracker.track_usage(1000, 500, "gpt-4o")
        tracker.track_usage(1000, 500, "gpt-4o-mini")
        tracker.track_usage(1000, 500, "claude-3-5-sonnet-20241022")
        tracker.track_usage(1000, 500, "gemini-1.5-pro")
        tracker.track_usage(1000, 500, "llama-3.3-70b-versatile")

        summary = tracker.get_summary()

        assert summary["total_requests"] == 5
        assert len(summary["models"]) == 5
        assert all(
            model in summary["models"]
            for model in [
                "gpt-4o",
                "gpt-4o-mini",
                "claude-3-5-sonnet-20241022",
                "gemini-1.5-pro",
                "llama-3.3-70b-versatile",
            ]
        )


class TestPricingData:
    """測試價格數據"""

    def test_pricing_structure(self):
        """測試價格表結構"""
        for model, pricing in PRICING.items():
            assert "prompt" in pricing
            assert "completion" in pricing
            assert isinstance(pricing["prompt"], (int, float))
            assert isinstance(pricing["completion"], (int, float))
            assert pricing["prompt"] >= 0
            assert pricing["completion"] >= 0

    def test_all_major_models_present(self):
        """測試主要模型都在價格表中"""
        expected_models = [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-3.5-turbo",
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "gemini-1.5-pro",
            "gemini-1.5-flash",
        ]

        for model in expected_models:
            assert model in PRICING, f"模型 {model} 不在價格表中"


class TestEdgeCases:
    """測試邊界情況"""

    def test_zero_tokens(self):
        """測試零 token 的情況"""
        tracker = CostTracker()
        usage = tracker.track_usage(0, 0, "gpt-4o")

        assert usage.total_tokens == 0

        cost = tracker.calculate_cost(usage)
        assert cost == 0.0

    def test_large_token_count(self):
        """測試大量 token"""
        tracker = CostTracker()
        usage = tracker.track_usage(1000000, 500000, "gpt-4o")

        cost = tracker.calculate_cost(usage)

        # 應該能正確處理大數字
        assert cost > 0
        assert cost == pytest.approx(1000000 / 1000 * 0.0025 + 500000 / 1000 * 0.01)

    def test_negative_tokens_handling(self):
        """測試負數 token（雖然不應該發生）"""
        tracker = CostTracker()

        # 即使傳入負數，系統也應該能處理
        usage = TokenUsage(
            prompt_tokens=-100, completion_tokens=-50, total_tokens=-150, model="gpt-4o"
        )

        cost = tracker.calculate_cost(usage)

        # 成本可能為負數，但不應該拋出異常
        assert isinstance(cost, float)

    def test_malformed_json_handling(self):
        """測試載入損壞的 JSON 文件"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / "malformed.json"

            # 寫入無效的 JSON
            with open(temp_path, "w") as f:
                f.write("{ invalid json }")

            # 應該拋出 JSON 解析錯誤
            with pytest.raises(json.JSONDecodeError):
                tracker = CostTracker(save_path=str(temp_path))

    def test_missing_fields_in_loaded_data(self):
        """測試載入缺少欄位的數據"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / "missing_fields.json"

            # 寫入缺少 model 和 provider 欄位的數據
            with open(temp_path, "w") as f:
                json.dump(
                    [
                        {
                            "prompt_tokens": 1000,
                            "completion_tokens": 500,
                            "total_tokens": 1500,
                            "timestamp": datetime.now().isoformat(),
                        }
                    ],
                    f,
                )

            tracker = CostTracker(save_path=str(temp_path))

            # 應該能正常載入，使用預設值
            assert len(tracker.usage_history) == 1
            assert tracker.usage_history[0].model == ""
            assert tracker.usage_history[0].provider == ""

    def test_unicode_in_model_names(self):
        """測試模型名稱中的 Unicode 字符"""
        tracker = CostTracker()
        usage = tracker.track_usage(1000, 500, "模型-測試", "提供商")

        assert usage.model == "模型-測試"
        assert usage.provider == "提供商"

        summary = tracker.get_summary()
        assert "模型-測試" in summary["models"]

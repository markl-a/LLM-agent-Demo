"""成本追蹤模組 - 追蹤和計算 LLM API 使用成本"""

from typing import Dict, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path


@dataclass
class TokenUsage:
    """Token 使用記錄"""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    timestamp: datetime = field(default_factory=datetime.now)
    model: str = ""
    provider: str = ""

    def to_dict(self) -> Dict:
        """轉換為字典"""
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "timestamp": self.timestamp.isoformat(),
            "model": self.model,
            "provider": self.provider,
        }


# 價格表（美元/1K tokens）- 2025年1月價格
PRICING = {
    # OpenAI GPT-4 系列
    "gpt-4o": {"prompt": 0.0025, "completion": 0.01},
    "gpt-4o-mini": {"prompt": 0.00015, "completion": 0.0006},
    "gpt-4-turbo": {"prompt": 0.01, "completion": 0.03},
    "gpt-4": {"prompt": 0.03, "completion": 0.06},
    # OpenAI GPT-3.5 系列
    "gpt-3.5-turbo": {"prompt": 0.0005, "completion": 0.0015},
    "gpt-3.5-turbo-16k": {"prompt": 0.003, "completion": 0.004},
    # Anthropic Claude 系列
    "claude-3-5-sonnet-20241022": {"prompt": 0.003, "completion": 0.015},
    "claude-3-5-haiku-20241022": {"prompt": 0.001, "completion": 0.005},
    "claude-3-opus-20240229": {"prompt": 0.015, "completion": 0.075},
    "claude-3-sonnet-20240229": {"prompt": 0.003, "completion": 0.015},
    "claude-3-haiku-20240307": {"prompt": 0.00025, "completion": 0.00125},
    # Google Gemini 系列
    "gemini-2.0-flash-exp": {"prompt": 0.0, "completion": 0.0},  # 免費（有限額）
    "gemini-1.5-pro": {"prompt": 0.00125, "completion": 0.005},
    "gemini-1.5-flash": {"prompt": 0.000075, "completion": 0.0003},
    # Groq (使用 Meta Llama)
    "llama-3.3-70b-versatile": {"prompt": 0.00059, "completion": 0.00079},
    "llama-3.1-70b-versatile": {"prompt": 0.00059, "completion": 0.00079},
    "mixtral-8x7b": {"prompt": 0.00024, "completion": 0.00024},
    # 嵌入模型
    "text-embedding-3-small": {"prompt": 0.00002, "completion": 0.0},
    "text-embedding-3-large": {"prompt": 0.00013, "completion": 0.0},
    "text-embedding-ada-002": {"prompt": 0.0001, "completion": 0.0},
}


class TokenCounter:
    """Token 計數器 - 簡單的 token 估算"""

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """
        估算文本的 token 數量（粗略估計）

        使用簡單的規則：英文約 4 個字符 = 1 token，中文約 1.5 字符 = 1 token

        Args:
            text: 要估算的文本

        Returns:
            估算的 token 數量
        """
        if not text:
            return 0

        # 計算中文字符數
        chinese_chars = sum(1 for char in text if "\u4e00" <= char <= "\u9fff")

        # 計算其他字符數
        other_chars = len(text) - chinese_chars

        # 估算 token 數
        estimated_tokens = int(chinese_chars / 1.5 + other_chars / 4)

        return max(estimated_tokens, 1)


class CostTracker:
    """成本追蹤器"""

    def __init__(self, save_path: Optional[str] = None):
        """
        初始化成本追蹤器

        Args:
            save_path: 保存使用記錄的文件路徑
        """
        self.usage_history: List[TokenUsage] = []
        self.save_path = save_path

        # 如果指定了保存路徑且文件存在，載入歷史記錄
        if save_path and Path(save_path).exists():
            self.load_history()

    def track_usage(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        model: str = "",
        provider: str = "",
    ) -> TokenUsage:
        """
        記錄一次 API 使用

        Args:
            prompt_tokens: 輸入 token 數
            completion_tokens: 輸出 token 數
            model: 模型名稱
            provider: 提供商名稱

        Returns:
            TokenUsage 實例
        """
        usage = TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            model=model,
            provider=provider,
        )

        self.usage_history.append(usage)

        # 自動保存
        if self.save_path:
            self.save_history()

        return usage

    def calculate_cost(self, usage: TokenUsage) -> float:
        """
        計算單次使用的成本

        Args:
            usage: Token 使用記錄

        Returns:
            成本（美元）
        """
        model_name = usage.model.lower()

        # 嘗試精確匹配
        if model_name in PRICING:
            pricing = PRICING[model_name]
        else:
            # 嘗試部分匹配（例如 gpt-4-0125-preview 匹配 gpt-4）
            pricing = None
            for key in PRICING:
                if key in model_name:
                    pricing = PRICING[key]
                    break

            if not pricing:
                # 無法找到價格，返回 0
                return 0.0

        # 計算成本
        prompt_cost = (usage.prompt_tokens / 1000) * pricing["prompt"]
        completion_cost = (usage.completion_tokens / 1000) * pricing["completion"]

        return prompt_cost + completion_cost

    def get_total_cost(
        self, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None
    ) -> float:
        """
        獲取總成本

        Args:
            start_time: 開始時間（可選）
            end_time: 結束時間（可選）

        Returns:
            總成本（美元）
        """
        filtered_usage = self.usage_history

        if start_time:
            filtered_usage = [u for u in filtered_usage if u.timestamp >= start_time]

        if end_time:
            filtered_usage = [u for u in filtered_usage if u.timestamp <= end_time]

        return sum(self.calculate_cost(usage) for usage in filtered_usage)

    def get_total_tokens(
        self, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None
    ) -> Dict[str, int]:
        """
        獲取總 token 使用量

        Args:
            start_time: 開始時間（可選）
            end_time: 結束時間（可選）

        Returns:
            包含 prompt_tokens, completion_tokens, total_tokens 的字典
        """
        filtered_usage = self.usage_history

        if start_time:
            filtered_usage = [u for u in filtered_usage if u.timestamp >= start_time]

        if end_time:
            filtered_usage = [u for u in filtered_usage if u.timestamp <= end_time]

        total_prompt = sum(u.prompt_tokens for u in filtered_usage)
        total_completion = sum(u.completion_tokens for u in filtered_usage)

        return {
            "prompt_tokens": total_prompt,
            "completion_tokens": total_completion,
            "total_tokens": total_prompt + total_completion,
        }

    def get_summary(self) -> Dict:
        """
        獲取使用摘要

        Returns:
            包含成本和 token 使用統計的字典
        """
        total_cost = self.get_total_cost()
        total_tokens = self.get_total_tokens()

        # 按模型統計
        model_stats = {}
        for usage in self.usage_history:
            model = usage.model or "unknown"
            if model not in model_stats:
                model_stats[model] = {
                    "count": 0,
                    "tokens": 0,
                    "cost": 0.0,
                }

            model_stats[model]["count"] += 1
            model_stats[model]["tokens"] += usage.total_tokens
            model_stats[model]["cost"] += self.calculate_cost(usage)

        return {
            "total_requests": len(self.usage_history),
            "total_cost": round(total_cost, 6),
            "total_tokens": total_tokens,
            "models": model_stats,
        }

    def save_history(self) -> None:
        """保存使用歷史到文件"""
        if not self.save_path:
            return

        save_path = Path(self.save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)

        data = [usage.to_dict() for usage in self.usage_history]

        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_history(self) -> None:
        """從文件載入使用歷史"""
        if not self.save_path or not Path(self.save_path).exists():
            return

        with open(self.save_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.usage_history = []
        for item in data:
            usage = TokenUsage(
                prompt_tokens=item["prompt_tokens"],
                completion_tokens=item["completion_tokens"],
                total_tokens=item["total_tokens"],
                timestamp=datetime.fromisoformat(item["timestamp"]),
                model=item.get("model", ""),
                provider=item.get("provider", ""),
            )
            self.usage_history.append(usage)

    def reset(self) -> None:
        """重置追蹤器（清除所有歷史記錄）"""
        self.usage_history.clear()
        if self.save_path and Path(self.save_path).exists():
            Path(self.save_path).unlink()

    def print_summary(self) -> None:
        """打印使用摘要"""
        summary = self.get_summary()

        print("=" * 60)
        print("LLM API 使用摘要")
        print("=" * 60)
        print(f"總請求次數: {summary['total_requests']}")
        print(f"總 Token 數: {summary['total_tokens']['total_tokens']:,}")
        print(f"  - 輸入: {summary['total_tokens']['prompt_tokens']:,}")
        print(f"  - 輸出: {summary['total_tokens']['completion_tokens']:,}")
        print(f"總成本: ${summary['total_cost']:.6f}")
        print("\n" + "=" * 60)
        print("按模型統計:")
        print("=" * 60)

        for model, stats in summary["models"].items():
            print(f"\n{model}:")
            print(f"  請求次數: {stats['count']}")
            print(f"  Token 數: {stats['tokens']:,}")
            print(f"  成本: ${stats['cost']:.6f}")

        print("=" * 60)

"""
Helicone 路由管理與故障轉移
==========================

本文件展示如何使用 Helicone 實現智能路由、負載均衡和故障轉移。
這些功能對於構建高可用的 AI 應用至關重要。

主要內容:
1. 基本路由配置
2. 模型故障轉移
3. 負載均衡策略
4. 成本優化路由
5. 性能優化路由
6. A/B 測試路由
7. 自定義路由邏輯

作者: Helicone Team
日期: 2025-12-31
"""

import os
import sys
import time
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
import json
from dotenv import load_dotenv

try:
    import openai
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import track
    import pandas as pd
except ImportError as e:
    print(f"❌ 缺少必要的依賴: {e}")
    print("請運行: pip install openai rich pandas")
    sys.exit(1)


class RoutingStrategy(Enum):
    """路由策略"""
    ROUND_ROBIN = "round_robin"      # 輪詢
    LEAST_COST = "least_cost"        # 最低成本
    LEAST_LATENCY = "least_latency"  # 最低延遲
    WEIGHTED = "weighted"            # 加權分配
    RANDOM = "random"                # 隨機
    FAILOVER = "failover"            # 故障轉移


class ModelTier(Enum):
    """模型等級"""
    PREMIUM = "premium"    # 高級模型 (GPT-4, Claude Opus)
    STANDARD = "standard"  # 標準模型 (GPT-3.5, Claude Sonnet)
    ECONOMY = "economy"    # 經濟模型 (GPT-3.5-turbo)


@dataclass
class ModelConfig:
    """模型配置"""
    name: str
    provider: str
    tier: ModelTier
    cost_per_1k_input: float
    cost_per_1k_output: float
    avg_latency_ms: float
    max_tokens: int
    availability: float = 0.99
    weight: float = 1.0


@dataclass
class RouteResult:
    """路由結果"""
    selected_model: str
    strategy: str
    reason: str
    estimated_cost: float
    estimated_latency: float
    alternatives: List[str]


class HeliconeRouter:
    """
    Helicone 智能路由器

    實現多種路由策略,根據不同的需求自動選擇最合適的模型。
    """

    def __init__(self):
        """初始化路由器"""
        load_dotenv()

        # API 配置
        self.helicone_api_key = os.getenv("HELICONE_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.helicone_base_url = "https://oai.helicone.ai/v1"

        # 初始化客戶端
        self.client = openai.OpenAI(
            api_key=self.openai_api_key,
            base_url=self.helicone_base_url,
            default_headers={
                "Helicone-Auth": f"Bearer {self.helicone_api_key}"
            }
        )

        self.console = Console()

        # 定義可用模型
        self.available_models = self._initialize_models()

        # 路由歷史
        self.routing_history: List[Dict] = []

        # 輪詢計數器
        self.round_robin_counter = 0

        self.console.print("✅ [green]智能路由器已初始化[/green]")
        self._display_available_models()

    def _initialize_models(self) -> Dict[str, ModelConfig]:
        """
        初始化可用模型配置

        包含每個模型的詳細信息,用於路由決策。
        """
        return {
            "gpt-4": ModelConfig(
                name="gpt-4",
                provider="openai",
                tier=ModelTier.PREMIUM,
                cost_per_1k_input=0.03,
                cost_per_1k_output=0.06,
                avg_latency_ms=2000,
                max_tokens=8192,
                availability=0.99,
                weight=1.0
            ),
            "gpt-4-turbo": ModelConfig(
                name="gpt-4-turbo-preview",
                provider="openai",
                tier=ModelTier.PREMIUM,
                cost_per_1k_input=0.01,
                cost_per_1k_output=0.03,
                avg_latency_ms=1500,
                max_tokens=128000,
                availability=0.98,
                weight=2.0
            ),
            "gpt-3.5-turbo": ModelConfig(
                name="gpt-3.5-turbo",
                provider="openai",
                tier=ModelTier.STANDARD,
                cost_per_1k_input=0.0005,
                cost_per_1k_output=0.0015,
                avg_latency_ms=800,
                max_tokens=4096,
                availability=0.995,
                weight=3.0
            ),
            "gpt-3.5-turbo-16k": ModelConfig(
                name="gpt-3.5-turbo-16k",
                provider="openai",
                tier=ModelTier.STANDARD,
                cost_per_1k_input=0.001,
                cost_per_1k_output=0.002,
                avg_latency_ms=1000,
                max_tokens=16384,
                availability=0.99,
                weight=2.0
            ),
        }

    def _display_available_models(self):
        """顯示可用模型"""
        self.console.print("\n[bold cyan]📋 可用模型[/bold cyan]")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("模型", style="cyan")
        table.add_column("等級", style="yellow")
        table.add_column("輸入成本", justify="right")
        table.add_column("輸出成本", justify="right")
        table.add_column("延遲", justify="right")
        table.add_column("可用性", justify="right")

        for model in self.available_models.values():
            table.add_row(
                model.name,
                model.tier.value,
                f"${model.cost_per_1k_input}/1K",
                f"${model.cost_per_1k_output}/1K",
                f"{model.avg_latency_ms}ms",
                f"{model.availability*100:.1f}%"
            )

        self.console.print(table)

    def select_model(
        self,
        strategy: RoutingStrategy,
        prompt: str,
        estimated_tokens: int = 500,
        tier_preference: Optional[ModelTier] = None,
        excluded_models: List[str] = None
    ) -> RouteResult:
        """
        根據策略選擇模型

        這是路由的核心邏輯,根據不同的策略選擇最合適的模型。
        """
        excluded_models = excluded_models or []

        # 過濾可用模型
        candidates = {
            name: config for name, config in self.available_models.items()
            if name not in excluded_models
        }

        # 如果指定了等級偏好,進一步過濾
        if tier_preference:
            candidates = {
                name: config for name, config in candidates.items()
                if config.tier == tier_preference
            }

        if not candidates:
            raise ValueError("沒有可用的模型")

        # 根據策略選擇模型
        if strategy == RoutingStrategy.LEAST_COST:
            selected = self._select_least_cost(candidates, estimated_tokens)
            reason = "選擇成本最低的模型"

        elif strategy == RoutingStrategy.LEAST_LATENCY:
            selected = self._select_least_latency(candidates)
            reason = "選擇延遲最低的模型"

        elif strategy == RoutingStrategy.ROUND_ROBIN:
            selected = self._select_round_robin(candidates)
            reason = f"輪詢選擇 (輪次 {self.round_robin_counter})"

        elif strategy == RoutingStrategy.WEIGHTED:
            selected = self._select_weighted(candidates)
            reason = "基於權重隨機選擇"

        elif strategy == RoutingStrategy.RANDOM:
            selected = random.choice(list(candidates.keys()))
            reason = "隨機選擇"

        elif strategy == RoutingStrategy.FAILOVER:
            selected = self._select_failover(candidates)
            reason = "故障轉移: 選擇可用性最高的模型"

        else:
            selected = list(candidates.keys())[0]
            reason = "默認選擇"

        # 計算預估
        model_config = self.available_models[selected]
        estimated_cost = (
            (estimated_tokens / 2 / 1000) * model_config.cost_per_1k_input +
            (estimated_tokens / 2 / 1000) * model_config.cost_per_1k_output
        )

        # 構建結果
        result = RouteResult(
            selected_model=selected,
            strategy=strategy.value,
            reason=reason,
            estimated_cost=estimated_cost,
            estimated_latency=model_config.avg_latency_ms,
            alternatives=list(candidates.keys())
        )

        return result

    def _select_least_cost(self, candidates: Dict[str, ModelConfig], tokens: int) -> str:
        """選擇成本最低的模型"""
        min_cost = float('inf')
        selected = None

        for name, config in candidates.items():
            # 假設輸入輸出各佔一半
            cost = (
                (tokens / 2 / 1000) * config.cost_per_1k_input +
                (tokens / 2 / 1000) * config.cost_per_1k_output
            )
            if cost < min_cost:
                min_cost = cost
                selected = name

        return selected

    def _select_least_latency(self, candidates: Dict[str, ModelConfig]) -> str:
        """選擇延遲最低的模型"""
        return min(candidates.items(), key=lambda x: x[1].avg_latency_ms)[0]

    def _select_round_robin(self, candidates: Dict[str, ModelConfig]) -> str:
        """輪詢選擇"""
        candidate_list = list(candidates.keys())
        selected = candidate_list[self.round_robin_counter % len(candidate_list)]
        self.round_robin_counter += 1
        return selected

    def _select_weighted(self, candidates: Dict[str, ModelConfig]) -> str:
        """加權隨機選擇"""
        models = list(candidates.keys())
        weights = [candidates[m].weight for m in models]
        return random.choices(models, weights=weights, k=1)[0]

    def _select_failover(self, candidates: Dict[str, ModelConfig]) -> str:
        """選擇可用性最高的模型"""
        return max(candidates.items(), key=lambda x: x[1].availability)[0]

    def route_and_execute(
        self,
        prompt: str,
        strategy: RoutingStrategy,
        **kwargs
    ) -> Dict:
        """
        路由並執行請求

        結合路由決策和實際 API 調用。
        """
        start_time = time.time()

        try:
            # 第一步: 路由決策
            route_result = self.select_model(
                strategy=strategy,
                prompt=prompt,
                estimated_tokens=kwargs.get("max_tokens", 500)
            )

            self.console.print(
                f"\n🎯 [cyan]路由決策[/cyan]: {route_result.selected_model}"
            )
            self.console.print(f"   策略: {route_result.strategy}")
            self.console.print(f"   原因: {route_result.reason}")
            self.console.print(f"   預估成本: ${route_result.estimated_cost:.6f}")

            # 第二步: 執行請求
            response = self.client.chat.completions.create(
                model=route_result.selected_model,
                messages=[{"role": "user", "content": prompt}],
                extra_headers={
                    "Helicone-Property-RoutingStrategy": strategy.value,
                    "Helicone-Property-SelectedModel": route_result.selected_model,
                    "Helicone-Property-Reason": route_result.reason
                },
                **kwargs
            )

            end_time = time.time()
            actual_latency = (end_time - start_time) * 1000  # 轉換為毫秒

            # 計算實際成本
            model_config = self.available_models[route_result.selected_model]
            actual_cost = (
                (response.usage.prompt_tokens / 1000) * model_config.cost_per_1k_input +
                (response.usage.completion_tokens / 1000) * model_config.cost_per_1k_output
            )

            # 記錄結果
            result = {
                "timestamp": datetime.now().isoformat(),
                "prompt": prompt,
                "response": response.choices[0].message.content,
                "model": response.model,
                "strategy": strategy.value,
                "route_result": route_result,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "performance": {
                    "actual_latency_ms": actual_latency,
                    "estimated_latency_ms": route_result.estimated_latency,
                    "latency_diff_ms": actual_latency - route_result.estimated_latency
                },
                "cost": {
                    "actual_cost_usd": actual_cost,
                    "estimated_cost_usd": route_result.estimated_cost,
                    "cost_diff_usd": actual_cost - route_result.estimated_cost
                },
                "success": True
            }

            self.routing_history.append(result)

            return result

        except Exception as e:
            self.console.print(f"❌ [red]請求失敗: {str(e)}[/red]")

            error_result = {
                "timestamp": datetime.now().isoformat(),
                "prompt": prompt,
                "strategy": strategy.value,
                "error": str(e),
                "success": False
            }

            self.routing_history.append(error_result)
            return error_result

    def implement_failover(
        self,
        prompt: str,
        preferred_model: str,
        fallback_models: List[str],
        **kwargs
    ) -> Dict:
        """
        實現故障轉移

        如果首選模型失敗,自動嘗試備用模型。
        """
        self.console.print(f"\n🔄 [cyan]故障轉移策略[/cyan]")
        self.console.print(f"   首選: {preferred_model}")
        self.console.print(f"   備用: {', '.join(fallback_models)}")

        # 構建嘗試列表
        models_to_try = [preferred_model] + fallback_models

        for i, model in enumerate(models_to_try):
            try:
                self.console.print(f"\n嘗試 {i+1}/{len(models_to_try)}: {model}")

                response = self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    extra_headers={
                        "Helicone-Property-FailoverAttempt": str(i+1),
                        "Helicone-Property-TargetModel": model,
                        "Helicone-Property-PreferredModel": preferred_model
                    },
                    **kwargs
                )

                self.console.print(f"✅ [green]成功使用 {model}[/green]")

                return {
                    "success": True,
                    "model_used": model,
                    "attempt_number": i + 1,
                    "response": response.choices[0].message.content,
                    "usage": response.usage
                }

            except Exception as e:
                self.console.print(f"❌ [yellow]{model} 失敗: {str(e)}[/yellow]")

                if i == len(models_to_try) - 1:
                    # 所有模型都失敗了
                    return {
                        "success": False,
                        "error": "所有模型都失敗了",
                        "attempts": len(models_to_try)
                    }

                # 繼續嘗試下一個模型
                continue

    def ab_test_models(
        self,
        prompt: str,
        model_a: str,
        model_b: str,
        split_ratio: float = 0.5,
        **kwargs
    ) -> Dict:
        """
        A/B 測試兩個模型

        根據分割比例隨機選擇模型,用於比較性能。
        """
        # 隨機選擇
        use_model_a = random.random() < split_ratio
        selected_model = model_a if use_model_a else model_b
        variant = "A" if use_model_a else "B"

        self.console.print(f"\n🔬 [cyan]A/B 測試[/cyan]: 變體 {variant} ({selected_model})")

        try:
            response = self.client.chat.completions.create(
                model=selected_model,
                messages=[{"role": "user", "content": prompt}],
                extra_headers={
                    "Helicone-Property-ABTest": "model-comparison",
                    "Helicone-Property-Variant": variant,
                    "Helicone-Property-ModelA": model_a,
                    "Helicone-Property-ModelB": model_b,
                    "Helicone-Property-SplitRatio": str(split_ratio)
                },
                **kwargs
            )

            return {
                "success": True,
                "variant": variant,
                "model": selected_model,
                "response": response.choices[0].message.content,
                "usage": response.usage
            }

        except Exception as e:
            return {
                "success": False,
                "variant": variant,
                "model": selected_model,
                "error": str(e)
            }

    def analyze_routing_performance(self):
        """分析路由性能"""
        if not self.routing_history:
            self.console.print("⚠️  [yellow]沒有路由歷史[/yellow]")
            return

        self.console.print("\n[bold cyan]📊 路由性能分析[/bold cyan]")
        self.console.print("=" * 80)

        # 按策略統計
        strategy_stats = {}
        for record in self.routing_history:
            if not record["success"]:
                continue

            strategy = record["strategy"]
            if strategy not in strategy_stats:
                strategy_stats[strategy] = {
                    "count": 0,
                    "total_cost": 0,
                    "total_latency": 0,
                    "models_used": set()
                }

            strategy_stats[strategy]["count"] += 1
            strategy_stats[strategy]["total_cost"] += record["cost"]["actual_cost_usd"]
            strategy_stats[strategy]["total_latency"] += record["performance"]["actual_latency_ms"]
            strategy_stats[strategy]["models_used"].add(record["model"])

        # 創建表格
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("策略", style="cyan")
        table.add_column("請求數", justify="right")
        table.add_column("總成本", justify="right")
        table.add_column("平均延遲", justify="right")
        table.add_column("使用模型數", justify="right")

        for strategy, stats in strategy_stats.items():
            avg_latency = stats["total_latency"] / stats["count"]
            table.add_row(
                strategy,
                str(stats["count"]),
                f"${stats['total_cost']:.6f}",
                f"{avg_latency:.0f}ms",
                str(len(stats["models_used"]))
            )

        self.console.print(table)


def demo_routing_strategies():
    """演示不同的路由策略"""
    console = Console()
    router = HeliconeRouter()

    test_prompt = "解釋量子計算的基本概念,用簡單的語言。"

    strategies = [
        RoutingStrategy.LEAST_COST,
        RoutingStrategy.LEAST_LATENCY,
        RoutingStrategy.ROUND_ROBIN,
        RoutingStrategy.WEIGHTED,
    ]

    console.print("\n[bold]測試不同路由策略[/bold]\n")

    for strategy in strategies:
        console.print(f"\n{'='*80}")
        console.print(f"策略: [bold cyan]{strategy.value}[/bold cyan]")
        console.print('='*80)

        result = router.route_and_execute(
            prompt=test_prompt,
            strategy=strategy,
            max_tokens=200
        )

        if result["success"]:
            console.print(f"\n✅ 成功")
            console.print(f"   模型: {result['model']}")
            console.print(f"   成本: ${result['cost']['actual_cost_usd']:.6f}")
            console.print(f"   延遲: {result['performance']['actual_latency_ms']:.0f}ms")

        time.sleep(1)


def demo_failover():
    """演示故障轉移"""
    console = Console()
    router = HeliconeRouter()

    console.print("\n[bold]測試故障轉移[/bold]\n")

    result = router.implement_failover(
        prompt="什麼是深度學習?",
        preferred_model="gpt-4",
        fallback_models=["gpt-4-turbo-preview", "gpt-3.5-turbo"],
        max_tokens=100
    )

    console.print(f"\n結果: {json.dumps(result, indent=2, ensure_ascii=False)}")


def demo_ab_testing():
    """演示 A/B 測試"""
    console = Console()
    router = HeliconeRouter()

    console.print("\n[bold]A/B 測試: GPT-4 vs GPT-3.5[/bold]\n")

    # 運行多次測試
    for i in range(5):
        console.print(f"\n測試 {i+1}/5")
        result = router.ab_test_models(
            prompt=f"生成一個創意的產品名稱 (測試 {i+1})",
            model_a="gpt-4",
            model_b="gpt-3.5-turbo",
            split_ratio=0.5,
            max_tokens=50
        )

        if result["success"]:
            console.print(f"   變體: {result['variant']}")
            console.print(f"   響應: {result['response'][:100]}...")

        time.sleep(0.5)


def main():
    """主函數"""
    console = Console()
    console.print("[bold green]🎯 Helicone 路由管理演示[/bold green]\n")

    try:
        # 演示 1: 不同路由策略
        demo_routing_strategies()

        # 演示 2: 故障轉移
        demo_failover()

        # 演示 3: A/B 測試
        demo_ab_testing()

        # 分析性能
        router = HeliconeRouter()
        router.analyze_routing_performance()

        console.print("\n✅ [green]演示完成![/green]")

    except Exception as e:
        console.print(f"\n❌ [red]錯誤: {str(e)}[/red]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

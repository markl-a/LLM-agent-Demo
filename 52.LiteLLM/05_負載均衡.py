"""
LiteLLM 負載均衡範例

這個檔案展示如何使用 LiteLLM 實現負載均衡和容錯：
1. 基本的負載均衡配置
2. 不同的路由策略
3. 故障轉移（Fallback）
4. 重試機制
5. 健康檢查
6. 流量分配
7. 延遲追蹤
8. 多區域部署
9. A/B 測試
10. 動態路由

負載均衡對於提高系統可用性和效能至關重要。
"""

import os
from typing import List, Dict, Any, Optional
import yaml
import time
import random
from datetime import datetime
from litellm import completion
from dataclasses import dataclass
import statistics


# ============================================================================
# 資料類別定義
# ============================================================================

@dataclass
class ModelEndpoint:
    """模型端點配置"""
    model_name: str
    provider: str
    api_key: str
    region: Optional[str] = None
    priority: int = 1
    weight: float = 1.0
    max_requests_per_minute: Optional[int] = None


@dataclass
class RequestMetrics:
    """請求指標"""
    model: str
    latency: float
    tokens: int
    success: bool
    timestamp: str
    error: Optional[str] = None


# ============================================================================
# 第一部分：基本負載均衡配置
# ============================================================================

def create_load_balancing_config():
    """
    建立負載均衡配置檔案

    這個配置示範如何設定多個相同模型的端點進行負載均衡。
    """
    print("=" * 80)
    print("建立負載均衡配置")
    print("=" * 80)

    config = {
        "model_list": [
            # GPT-4 的三個端點
            {
                "model_name": "gpt-4",
                "litellm_params": {
                    "model": "gpt-4o",
                    "api_key": "os.environ/OPENAI_API_KEY_1"
                },
                "model_info": {
                    "id": "gpt-4-endpoint-1",
                    "region": "us-east-1"
                }
            },
            {
                "model_name": "gpt-4",
                "litellm_params": {
                    "model": "gpt-4o",
                    "api_key": "os.environ/OPENAI_API_KEY_2"
                },
                "model_info": {
                    "id": "gpt-4-endpoint-2",
                    "region": "us-west-1"
                }
            },
            {
                "model_name": "gpt-4",
                "litellm_params": {
                    "model": "azure/gpt-4",
                    "api_base": "os.environ/AZURE_API_BASE",
                    "api_key": "os.environ/AZURE_API_KEY",
                    "api_version": "2024-02-01"
                },
                "model_info": {
                    "id": "gpt-4-azure",
                    "region": "eastus"
                }
            }
        ],

        "router_settings": {
            # 路由策略：
            # - simple-shuffle: 隨機選擇
            # - least-busy: 選擇最不忙碌的端點
            # - usage-based-routing: 基於使用量
            # - latency-based-routing: 基於延遲
            "routing_strategy": "least-busy",

            # 允許的連續失敗次數
            "allowed_fails": 3,

            # 失敗後的冷卻時間（秒）
            "cooldown_time": 60,

            # 重試設定
            "num_retries": 2,
            "retry_delay": 1,

            # 超時設定
            "timeout": 60
        }
    }

    config_path = "litellm_load_balancing.yaml"
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

    print(f"✓ 配置檔案已建立：{config_path}\n")
    print("配置說明：")
    print("  - GPT-4 有 3 個端點（2 個 OpenAI + 1 個 Azure）")
    print("  - 使用 least-busy 策略")
    print("  - 失敗 3 次後進入冷卻期")
    print("  - 自動重試 2 次")

    return config_path


def create_weighted_routing_config():
    """
    建立加權路由配置

    可以為不同的端點設定不同的權重，控制流量分配。
    """
    print("\n" + "=" * 80)
    print("建立加權路由配置")
    print("=" * 80)

    config = {
        "model_list": [
            # 主要端點（70% 流量）
            {
                "model_name": "gpt-4",
                "litellm_params": {
                    "model": "gpt-4o",
                    "api_key": "os.environ/OPENAI_API_KEY_1"
                },
                "model_info": {
                    "id": "primary-endpoint",
                    "weight": 0.7
                }
            },
            # 次要端點（20% 流量）
            {
                "model_name": "gpt-4",
                "litellm_params": {
                    "model": "gpt-4o",
                    "api_key": "os.environ/OPENAI_API_KEY_2"
                },
                "model_info": {
                    "id": "secondary-endpoint",
                    "weight": 0.2
                }
            },
            # 備用端點（10% 流量）
            {
                "model_name": "gpt-4",
                "litellm_params": {
                    "model": "azure/gpt-4",
                    "api_base": "os.environ/AZURE_API_BASE",
                    "api_key": "os.environ/AZURE_API_KEY"
                },
                "model_info": {
                    "id": "backup-endpoint",
                    "weight": 0.1
                }
            }
        ],

        "router_settings": {
            "routing_strategy": "usage-based-routing"
        }
    }

    config_path = "litellm_weighted_routing.yaml"
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

    print(f"✓ 配置檔案已建立：{config_path}\n")
    print("流量分配：")
    print("  - 主要端點：70%")
    print("  - 次要端點：20%")
    print("  - 備用端點：10%")

    return config_path


# ============================================================================
# 第二部分：故障轉移（Fallback）
# ============================================================================

def fallback_example():
    """
    故障轉移範例

    當主要模型失敗時，自動切換到備用模型。
    """
    print("\n" + "=" * 80)
    print("故障轉移範例")
    print("=" * 80)

    # 定義主要模型和備用模型列表
    primary_model = "gpt-4o"
    fallback_models = ["gpt-4-turbo", "claude-3-5-sonnet-20241022", "gpt-3.5-turbo"]

    prompt = "解釋什麼是負載均衡"

    print(f"\n主要模型：{primary_model}")
    print(f"備用模型：{', '.join(fallback_models)}\n")

    try:
        # 使用 LiteLLM 的 fallback 參數
        response = completion(
            model=primary_model,
            messages=[{"role": "user", "content": prompt}],
            fallbacks=fallback_models,
            max_tokens=200
        )

        # 檢查實際使用的模型
        used_model = response.model
        print(f"✓ 請求成功")
        print(f"使用的模型：{used_model}")
        print(f"\n回應：{response.choices[0].message.content[:200]}...")

        if used_model != primary_model:
            print(f"\n⚠️ 注意：使用了備用模型（主要模型可能失敗）")

    except Exception as e:
        print(f"✗ 所有模型都失敗了：{e}")


def multi_tier_fallback():
    """
    多層次故障轉移

    根據不同的失敗情況，選擇不同的備用策略。
    """
    print("\n" + "=" * 80)
    print("多層次故障轉移")
    print("=" * 80)

    fallback_tiers = {
        "tier_1": {
            "name": "高品質模型",
            "models": ["gpt-4o", "claude-3-5-sonnet-20241022"]
        },
        "tier_2": {
            "name": "平衡型模型",
            "models": ["gpt-4-turbo", "claude-3-sonnet-20240229"]
        },
        "tier_3": {
            "name": "經濟型模型",
            "models": ["gpt-3.5-turbo", "claude-3-haiku-20240307"]
        }
    }

    prompt = "寫一個 Python 函數來計算斐波那契數列"

    print("\n故障轉移層級：")
    for tier_name, tier_info in fallback_tiers.items():
        print(f"  {tier_name}: {tier_info['name']}")
        print(f"    模型：{', '.join(tier_info['models'])}")

    # 嘗試從第一層開始
    for tier_name, tier_info in fallback_tiers.items():
        print(f"\n嘗試 {tier_name} ({tier_info['name']})...")

        for model in tier_info["models"]:
            try:
                print(f"  嘗試模型：{model}")

                response = completion(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=300,
                    timeout=10
                )

                print(f"  ✓ 成功！使用模型：{model}")
                print(f"\n回應預覽：")
                print(response.choices[0].message.content[:200] + "...")
                return  # 成功，退出

            except Exception as e:
                print(f"  ✗ 失敗：{str(e)[:100]}")
                continue

    print("\n✗ 所有層級的模型都失敗了")


# ============================================================================
# 第三部分：智慧路由器
# ============================================================================

class SmartRouter:
    """智慧路由器"""

    def __init__(self):
        self.endpoints = []
        self.metrics: List[RequestMetrics] = []
        self.endpoint_health = {}

    def add_endpoint(self, endpoint: ModelEndpoint):
        """新增端點"""
        self.endpoints.append(endpoint)
        self.endpoint_health[endpoint.model_name] = {
            "healthy": True,
            "consecutive_failures": 0,
            "last_failure_time": None,
            "total_requests": 0,
            "successful_requests": 0
        }

    def select_endpoint(self, strategy: str = "least-busy") -> Optional[ModelEndpoint]:
        """
        選擇端點

        Args:
            strategy: 路由策略
                - random: 隨機選擇
                - round-robin: 輪詢
                - least-busy: 選擇最不忙碌的
                - lowest-latency: 選擇延遲最低的
                - weighted: 加權隨機

        Returns:
            選中的端點
        """
        # 過濾健康的端點
        healthy_endpoints = [
            ep for ep in self.endpoints
            if self.endpoint_health[ep.model_name]["healthy"]
        ]

        if not healthy_endpoints:
            print("⚠️ 沒有健康的端點可用")
            return None

        if strategy == "random":
            return random.choice(healthy_endpoints)

        elif strategy == "weighted":
            # 加權隨機選擇
            total_weight = sum(ep.weight for ep in healthy_endpoints)
            rand = random.uniform(0, total_weight)
            cumulative = 0

            for ep in healthy_endpoints:
                cumulative += ep.weight
                if rand <= cumulative:
                    return ep

            return healthy_endpoints[-1]

        elif strategy == "least-busy":
            # 選擇請求最少的端點
            return min(
                healthy_endpoints,
                key=lambda ep: self.endpoint_health[ep.model_name]["total_requests"]
            )

        elif strategy == "lowest-latency":
            # 選擇平均延遲最低的端點
            latencies = {}
            for ep in healthy_endpoints:
                ep_metrics = [
                    m for m in self.metrics[-100:]  # 最近 100 個請求
                    if m.model == ep.model_name and m.success
                ]
                if ep_metrics:
                    latencies[ep.model_name] = statistics.mean(
                        m.latency for m in ep_metrics
                    )
                else:
                    latencies[ep.model_name] = 0

            return min(healthy_endpoints, key=lambda ep: latencies.get(ep.model_name, float('inf')))

        else:
            return healthy_endpoints[0]

    def record_request(self, metric: RequestMetrics):
        """記錄請求指標"""
        self.metrics.append(metric)

        # 更新端點健康狀態
        health = self.endpoint_health[metric.model]
        health["total_requests"] += 1

        if metric.success:
            health["successful_requests"] += 1
            health["consecutive_failures"] = 0
        else:
            health["consecutive_failures"] += 1
            health["last_failure_time"] = datetime.now()

            # 如果連續失敗超過閾值，標記為不健康
            if health["consecutive_failures"] >= 3:
                health["healthy"] = False
                print(f"⚠️ 端點 {metric.model} 被標記為不健康")

    def check_and_restore_endpoints(self):
        """檢查並恢復不健康的端點"""
        current_time = datetime.now()

        for model_name, health in self.endpoint_health.items():
            if not health["healthy"] and health["last_failure_time"]:
                # 如果冷卻時間已過（例如 60 秒），嘗試恢復
                time_since_failure = (current_time - health["last_failure_time"]).total_seconds()

                if time_since_failure > 60:
                    print(f"🔄 嘗試恢復端點：{model_name}")
                    health["healthy"] = True
                    health["consecutive_failures"] = 0

    def get_statistics(self) -> Dict[str, Any]:
        """取得統計資訊"""
        total_requests = len(self.metrics)
        successful_requests = sum(1 for m in self.metrics if m.success)
        failed_requests = total_requests - successful_requests

        # 按模型統計
        model_stats = {}
        for ep in self.endpoints:
            ep_metrics = [m for m in self.metrics if m.model == ep.model_name]
            successful = [m for m in ep_metrics if m.success]

            if ep_metrics:
                avg_latency = statistics.mean(m.latency for m in ep_metrics)
                success_rate = len(successful) / len(ep_metrics)
            else:
                avg_latency = 0
                success_rate = 0

            model_stats[ep.model_name] = {
                "total_requests": len(ep_metrics),
                "successful_requests": len(successful),
                "success_rate": success_rate,
                "average_latency": avg_latency,
                "healthy": self.endpoint_health[ep.model_name]["healthy"]
            }

        return {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": successful_requests / total_requests if total_requests > 0 else 0,
            "by_model": model_stats
        }


def smart_router_example():
    """智慧路由器範例"""
    print("\n" + "=" * 80)
    print("智慧路由器範例")
    print("=" * 80)

    # 建立路由器
    router = SmartRouter()

    # 新增端點
    endpoints = [
        ModelEndpoint("gpt-4o", "openai", "key-1", "us-east", priority=1, weight=0.5),
        ModelEndpoint("gpt-4-turbo", "openai", "key-2", "us-west", priority=2, weight=0.3),
        ModelEndpoint("claude-3-5-sonnet-20241022", "anthropic", "key-3", "us", priority=2, weight=0.2)
    ]

    for ep in endpoints:
        router.add_endpoint(ep)
        print(f"✓ 新增端點：{ep.model_name} (權重: {ep.weight})")

    # 測試不同的路由策略
    strategies = ["random", "weighted", "least-busy"]

    for strategy in strategies:
        print(f"\n測試策略：{strategy}")
        print("-" * 40)

        # 模擬 10 個請求
        for i in range(10):
            endpoint = router.select_endpoint(strategy)
            if endpoint:
                # 模擬請求
                latency = random.uniform(0.5, 2.0)
                success = random.random() > 0.1  # 90% 成功率

                metric = RequestMetrics(
                    model=endpoint.model_name,
                    latency=latency,
                    tokens=random.randint(100, 500),
                    success=success,
                    timestamp=datetime.now().isoformat(),
                    error=None if success else "模擬錯誤"
                )

                router.record_request(metric)

                status = "✓" if success else "✗"
                print(f"  請求 {i + 1}: {status} {endpoint.model_name} ({latency:.2f}s)")

    # 顯示統計
    print("\n" + "=" * 80)
    print("統計資訊")
    print("=" * 80)

    stats = router.get_statistics()

    print(f"\n總覽：")
    print(f"  總請求數：{stats['total_requests']}")
    print(f"  成功請求：{stats['successful_requests']}")
    print(f"  失敗請求：{stats['failed_requests']}")
    print(f"  成功率：{stats['success_rate'] * 100:.1f}%")

    print(f"\n按模型統計：")
    for model, model_stat in stats["by_model"].items():
        health_status = "✓ 健康" if model_stat["healthy"] else "✗ 不健康"
        print(f"\n  {model} ({health_status})：")
        print(f"    請求數：{model_stat['total_requests']}")
        print(f"    成功率：{model_stat['success_rate'] * 100:.1f}%")
        print(f"    平均延遲：{model_stat['average_latency']:.2f}s")


# ============================================================================
# 第四部分：延遲追蹤和優化
# ============================================================================

class LatencyTracker:
    """延遲追蹤器"""

    def __init__(self):
        self.latencies: Dict[str, List[float]] = defaultdict(list)

    def record_latency(self, model: str, latency: float):
        """記錄延遲"""
        self.latencies[model].append(latency)

        # 只保留最近 1000 個記錄
        if len(self.latencies[model]) > 1000:
            self.latencies[model] = self.latencies[model][-1000:]

    def get_statistics(self, model: str) -> Dict[str, float]:
        """取得延遲統計"""
        if model not in self.latencies or not self.latencies[model]:
            return {}

        latencies = self.latencies[model]

        return {
            "min": min(latencies),
            "max": max(latencies),
            "mean": statistics.mean(latencies),
            "median": statistics.median(latencies),
            "p95": self._percentile(latencies, 95),
            "p99": self._percentile(latencies, 99),
            "sample_count": len(latencies)
        }

    def _percentile(self, data: List[float], percentile: int) -> float:
        """計算百分位數"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * (percentile / 100))
        return sorted_data[min(index, len(sorted_data) - 1)]

    def compare_models(self) -> List[Tuple[str, float]]:
        """比較所有模型的平均延遲"""
        comparisons = []

        for model in self.latencies:
            stats = self.get_statistics(model)
            if stats:
                comparisons.append((model, stats["mean"]))

        return sorted(comparisons, key=lambda x: x[1])


def latency_tracking_example():
    """延遲追蹤範例"""
    print("\n" + "=" * 80)
    print("延遲追蹤範例")
    print("=" * 80)

    tracker = LatencyTracker()

    # 模擬不同模型的請求
    models = ["gpt-4o", "gpt-3.5-turbo", "claude-3-5-sonnet-20241022"]

    print("\n模擬 100 個請求...")

    for _ in range(100):
        for model in models:
            # 模擬不同模型的延遲特性
            if "gpt-3.5" in model:
                latency = random.gauss(1.0, 0.3)  # 平均 1 秒
            elif "gpt-4" in model:
                latency = random.gauss(2.0, 0.5)  # 平均 2 秒
            else:
                latency = random.gauss(1.5, 0.4)  # 平均 1.5 秒

            latency = max(0.1, latency)  # 確保非負
            tracker.record_latency(model, latency)

    # 顯示統計
    print("\n延遲統計：")
    print("-" * 80)

    for model in models:
        stats = tracker.get_statistics(model)
        print(f"\n{model}：")
        print(f"  平均：{stats['mean']:.3f}s")
        print(f"  中位數：{stats['median']:.3f}s")
        print(f"  P95：{stats['p95']:.3f}s")
        print(f"  P99：{stats['p99']:.3f}s")
        print(f"  最小：{stats['min']:.3f}s")
        print(f"  最大：{stats['max']:.3f}s")
        print(f"  樣本數：{stats['sample_count']}")

    # 模型比較
    print("\n" + "=" * 80)
    print("模型延遲排名（由快到慢）")
    print("=" * 80)

    rankings = tracker.compare_models()
    for i, (model, avg_latency) in enumerate(rankings, 1):
        print(f"{i}. {model}: {avg_latency:.3f}s")


# ============================================================================
# 第五部分：A/B 測試
# ============================================================================

class ABTestRouter:
    """A/B 測試路由器"""

    def __init__(self, model_a: str, model_b: str, split_ratio: float = 0.5):
        """
        初始化 A/B 測試路由器

        Args:
            model_a: A 組模型
            model_b: B 組模型
            split_ratio: A 組的流量比例（0-1）
        """
        self.model_a = model_a
        self.model_b = model_b
        self.split_ratio = split_ratio
        self.metrics_a = []
        self.metrics_b = []

    def route_request(self) -> str:
        """根據分流比例路由請求"""
        if random.random() < self.split_ratio:
            return self.model_a
        else:
            return self.model_b

    def record_result(self, model: str, success: bool, latency: float, cost: float):
        """記錄測試結果"""
        metric = {
            "success": success,
            "latency": latency,
            "cost": cost,
            "timestamp": datetime.now().isoformat()
        }

        if model == self.model_a:
            self.metrics_a.append(metric)
        else:
            self.metrics_b.append(metric)

    def get_comparison(self) -> Dict[str, Any]:
        """取得 A/B 測試比較結果"""
        def calculate_metrics(metrics):
            if not metrics:
                return {}

            successful = [m for m in metrics if m["success"]]
            return {
                "total_requests": len(metrics),
                "successful_requests": len(successful),
                "success_rate": len(successful) / len(metrics),
                "average_latency": statistics.mean(m["latency"] for m in metrics),
                "average_cost": statistics.mean(m["cost"] for m in metrics),
                "total_cost": sum(m["cost"] for m in metrics)
            }

        return {
            "model_a": {
                "name": self.model_a,
                "metrics": calculate_metrics(self.metrics_a)
            },
            "model_b": {
                "name": self.model_b,
                "metrics": calculate_metrics(self.metrics_b)
            }
        }


def ab_test_example():
    """A/B 測試範例"""
    print("\n" + "=" * 80)
    print("A/B 測試範例")
    print("=" * 80)

    # 建立 A/B 測試：比較 GPT-4 和 Claude
    router = ABTestRouter(
        model_a="gpt-4o",
        model_b="claude-3-5-sonnet-20241022",
        split_ratio=0.5  # 50/50 分流
    )

    print(f"\nA/B 測試配置：")
    print(f"  A 組：{router.model_a}")
    print(f"  B 組：{router.model_b}")
    print(f"  分流比例：{router.split_ratio * 100:.0f}% / {(1 - router.split_ratio) * 100:.0f}%")

    # 模擬 200 個請求
    print(f"\n模擬 200 個請求...")

    for i in range(200):
        model = router.route_request()

        # 模擬不同模型的表現
        if "gpt-4" in model:
            success = random.random() > 0.05  # 95% 成功率
            latency = random.gauss(2.0, 0.5)
            cost = 0.006
        else:  # Claude
            success = random.random() > 0.03  # 97% 成功率
            latency = random.gauss(1.8, 0.4)
            cost = 0.005

        router.record_result(model, success, max(0.1, latency), cost)

    # 顯示比較結果
    print("\n" + "=" * 80)
    print("A/B 測試結果")
    print("=" * 80)

    comparison = router.get_comparison()

    for variant in ["model_a", "model_b"]:
        variant_data = comparison[variant]
        metrics = variant_data["metrics"]

        print(f"\n{variant.upper()}：{variant_data['name']}")
        print("-" * 40)
        print(f"  請求數：{metrics['total_requests']}")
        print(f"  成功率：{metrics['success_rate'] * 100:.2f}%")
        print(f"  平均延遲：{metrics['average_latency']:.3f}s")
        print(f"  平均成本：${metrics['average_cost']:.6f}")
        print(f"  總成本：${metrics['total_cost']:.4f}")

    # 建議
    print("\n" + "=" * 80)
    print("建議")
    print("=" * 80)

    a_metrics = comparison["model_a"]["metrics"]
    b_metrics = comparison["model_b"]["metrics"]

    print("\n比較分析：")

    # 成功率比較
    if a_metrics["success_rate"] > b_metrics["success_rate"]:
        diff = (a_metrics["success_rate"] - b_metrics["success_rate"]) * 100
        print(f"  ✓ {router.model_a} 的成功率高 {diff:.2f}%")
    else:
        diff = (b_metrics["success_rate"] - a_metrics["success_rate"]) * 100
        print(f"  ✓ {router.model_b} 的成功率高 {diff:.2f}%")

    # 延遲比較
    if a_metrics["average_latency"] < b_metrics["average_latency"]:
        diff = b_metrics["average_latency"] - a_metrics["average_latency"]
        print(f"  ✓ {router.model_a} 的延遲低 {diff:.3f}s")
    else:
        diff = a_metrics["average_latency"] - b_metrics["average_latency"]
        print(f"  ✓ {router.model_b} 的延遲低 {diff:.3f}s")

    # 成本比較
    if a_metrics["total_cost"] < b_metrics["total_cost"]:
        savings = b_metrics["total_cost"] - a_metrics["total_cost"]
        percent = (savings / b_metrics["total_cost"]) * 100
        print(f"  ✓ {router.model_a} 可節省成本 ${savings:.4f} ({percent:.1f}%)")
    else:
        savings = a_metrics["total_cost"] - b_metrics["total_cost"]
        percent = (savings / a_metrics["total_cost"]) * 100
        print(f"  ✓ {router.model_b} 可節省成本 ${savings:.4f} ({percent:.1f}%)")


# ============================================================================
# 主程式
# ============================================================================

def main():
    """主程式"""
    print("\n")
    print("=" * 80)
    print("LiteLLM 負載均衡完整教學")
    print("=" * 80)
    print()

    # 建立配置檔案
    create_load_balancing_config()
    create_weighted_routing_config()

    # 故障轉移範例
    # fallback_example()
    # multi_tier_fallback()

    # 智慧路由
    smart_router_example()

    # 延遲追蹤
    latency_tracking_example()

    # A/B 測試
    ab_test_example()

    print("\n" + "=" * 80)
    print("教學完成！")
    print("=" * 80)
    print("\n重點回顧：")
    print("1. 負載均衡提高系統可用性和效能")
    print("2. 故障轉移確保服務連續性")
    print("3. 智慧路由根據多種因素選擇最佳端點")
    print("4. 延遲追蹤幫助優化效能")
    print("5. A/B 測試支援資料驅動的決策")
    print()


if __name__ == "__main__":
    main()

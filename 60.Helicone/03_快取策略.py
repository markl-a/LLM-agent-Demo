"""
Helicone 快取策略
=================

本文件展示如何使用 Helicone 的快取功能來節省成本和提高性能。
智能快取可以減少 50-90% 的 API 調用成本。

主要內容:
1. 精確快取 (Exact Caching)
2. 語義快取 (Semantic Caching)
3. 快取配置和 TTL
4. 快取命中率分析
5. 成本節省計算
6. 快取失效策略
7. 最佳實踐

作者: Helicone Team
日期: 2025-12-31
"""

import os
import sys
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
from dotenv import load_dotenv

try:
    import openai
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    import matplotlib.pyplot as plt
    import pandas as pd
except ImportError as e:
    print(f"❌ 缺少必要的依賴: {e}")
    print("請運行: pip install openai rich matplotlib pandas")
    sys.exit(1)


class CacheType(Enum):
    """快取類型"""
    EXACT = "exact"          # 精確匹配快取
    SEMANTIC = "semantic"    # 語義相似快取
    BUCKET = "bucket"        # 分桶快取


@dataclass
class CacheConfig:
    """快取配置"""
    enabled: bool = True
    cache_type: CacheType = CacheType.EXACT
    ttl_seconds: int = 3600  # 1 小時
    bucket_max_size: int = 100
    semantic_threshold: float = 0.95


@dataclass
class CacheStats:
    """快取統計信息"""
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    cost_saved_usd: float = 0.0
    time_saved_seconds: float = 0.0

    @property
    def hit_rate(self) -> float:
        """計算快取命中率"""
        if self.total_requests == 0:
            return 0.0
        return (self.cache_hits / self.total_requests) * 100

    @property
    def miss_rate(self) -> float:
        """計算快取未命中率"""
        return 100 - self.hit_rate


class HeliconeCacheManager:
    """
    Helicone 快取管理器

    這個類提供了完整的快取管理功能:
    - 配置不同類型的快取
    - 追蹤快取性能
    - 分析成本節省
    - 優化快取策略
    """

    def __init__(self):
        """初始化快取管理器"""
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

        # Rich console
        self.console = Console()

        # 快取統計
        self.stats = CacheStats()

        # 請求歷史
        self.request_history: List[Dict] = []

        self.console.print("✅ [green]快取管理器已初始化[/green]")

    def _build_cache_headers(self, config: CacheConfig) -> Dict[str, str]:
        """
        構建快取相關的 headers

        Helicone 使用特殊的 headers 來控制快取行為。
        """
        headers = {
            "Helicone-Cache-Enabled": str(config.enabled).lower()
        }

        if config.enabled:
            # 基本快取配置
            headers["Helicone-Cache-Bucket-Max-Size"] = str(config.bucket_max_size)

            # 語義快取配置
            if config.cache_type == CacheType.SEMANTIC:
                headers["Helicone-Cache-Semantic-Enabled"] = "true"
                headers["Helicone-Cache-Semantic-Threshold"] = str(config.semantic_threshold)

            # TTL 配置
            if config.ttl_seconds > 0:
                headers["Helicone-Cache-TTL"] = str(config.ttl_seconds)

        return headers

    def request_with_cache(
        self,
        prompt: str,
        config: CacheConfig,
        model: str = "gpt-3.5-turbo",
        **kwargs
    ) -> Tuple[Dict, bool]:
        """
        發送帶快取的請求

        返回: (響應數據, 是否命中快取)
        """
        start_time = time.time()

        try:
            # 構建 headers
            cache_headers = self._build_cache_headers(config)

            # 添加追蹤 headers
            cache_headers.update({
                "Helicone-Property-CacheType": config.cache_type.value,
                "Helicone-Property-Timestamp": datetime.now().isoformat()
            })

            # 發送請求
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                extra_headers=cache_headers,
                **kwargs
            )

            end_time = time.time()
            duration = end_time - start_time

            # 檢查是否命中快取
            # 注意: Helicone 會在響應 headers 中標記快取命中
            # 這裡我們通過響應時間來推測 (快取響應通常 < 100ms)
            cache_hit = duration < 0.1

            # 計算成本
            cost = self._calculate_cost(response)

            # 記錄統計
            self.stats.total_requests += 1
            if cache_hit:
                self.stats.cache_hits += 1
                self.stats.cost_saved_usd += cost["total_cost_usd"]
                self.stats.time_saved_seconds += duration
            else:
                self.stats.cache_misses += 1

            # 構建結果
            result = {
                "prompt": prompt,
                "response": response.choices[0].message.content,
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "cost": cost,
                "duration": duration,
                "cache_hit": cache_hit,
                "cache_config": {
                    "type": config.cache_type.value,
                    "ttl": config.ttl_seconds
                },
                "timestamp": datetime.now().isoformat()
            }

            self.request_history.append(result)

            return result, cache_hit

        except Exception as e:
            self.console.print(f"❌ [red]請求失敗: {str(e)}[/red]")
            return None, False

    def _calculate_cost(self, response) -> Dict[str, float]:
        """計算請求成本"""
        # 簡化的成本計算 (GPT-3.5-Turbo 價格)
        input_cost = (response.usage.prompt_tokens / 1000) * 0.0005
        output_cost = (response.usage.completion_tokens / 1000) * 0.0015
        total_cost = input_cost + output_cost

        return {
            "input_cost_usd": input_cost,
            "output_cost_usd": output_cost,
            "total_cost_usd": total_cost
        }

    def test_exact_caching(self, iterations: int = 5):
        """
        測試精確快取

        精確快取會緩存完全相同的請求。
        第二次及之後的相同請求會直接從快取返回。
        """
        self.console.print("\n[bold cyan]📦 測試精確快取 (Exact Caching)[/bold cyan]")
        self.console.print("=" * 80)

        # 配置精確快取
        config = CacheConfig(
            enabled=True,
            cache_type=CacheType.EXACT,
            ttl_seconds=3600,  # 1 小時
            bucket_max_size=100
        )

        # 測試提示詞
        test_prompt = "什麼是機器學習?用一句話回答。"

        self.console.print(f"🔄 將發送相同的請求 {iterations} 次")
        self.console.print(f"📝 提示詞: {test_prompt}\n")

        results = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task(f"發送請求...", total=iterations)

            for i in range(iterations):
                progress.update(task, description=f"請求 {i+1}/{iterations}")

                result, cache_hit = self.request_with_cache(
                    prompt=test_prompt,
                    config=config,
                    max_tokens=100
                )

                if result:
                    results.append(result)
                    status = "🎯 快取命中" if cache_hit else "📡 API 調用"
                    self.console.print(
                        f"{status} - 耗時: {result['duration']:.3f}s - "
                        f"成本: ${result['cost']['total_cost_usd']:.6f}"
                    )

                progress.advance(task)
                time.sleep(0.5)  # 避免速率限制

        # 分析結果
        self._analyze_cache_performance(results, "精確快取")

    def test_semantic_caching(self):
        """
        測試語義快取

        語義快取會識別語義相似的請求,
        即使措辭不同也可能命中快取。
        """
        self.console.print("\n[bold cyan]🧠 測試語義快取 (Semantic Caching)[/bold cyan]")
        self.console.print("=" * 80)

        # 配置語義快取
        config = CacheConfig(
            enabled=True,
            cache_type=CacheType.SEMANTIC,
            ttl_seconds=3600,
            semantic_threshold=0.90  # 90% 相似度閾值
        )

        # 語義相似的提示詞
        similar_prompts = [
            "什麼是人工智能?",
            "請解釋 AI 是什麼?",
            "人工智能的定義是什麼?",
            "AI 代表什麼意思?",
            "解釋一下人工智能的概念",
        ]

        self.console.print("📝 測試語義相似的提示詞:\n")

        results = []
        for i, prompt in enumerate(similar_prompts, 1):
            self.console.print(f"{i}. {prompt}")

            result, cache_hit = self.request_with_cache(
                prompt=prompt,
                config=config,
                max_tokens=100
            )

            if result:
                results.append(result)

            time.sleep(0.5)

        # 分析結果
        self._analyze_cache_performance(results, "語義快取")

    def test_different_ttl(self):
        """
        測試不同的 TTL (Time To Live) 設置

        TTL 控制快取的有效期。
        較短的 TTL 適合動態內容,較長的 TTL 適合靜態內容。
        """
        self.console.print("\n[bold cyan]⏰ 測試不同 TTL 設置[/bold cyan]")
        self.console.print("=" * 80)

        ttl_configs = [
            60,      # 1 分鐘
            300,     # 5 分鐘
            3600,    # 1 小時
            86400,   # 1 天
        ]

        self.console.print("測試不同的快取過期時間:\n")

        for ttl in ttl_configs:
            config = CacheConfig(
                enabled=True,
                cache_type=CacheType.EXACT,
                ttl_seconds=ttl
            )

            # 格式化 TTL 顯示
            if ttl < 60:
                ttl_str = f"{ttl} 秒"
            elif ttl < 3600:
                ttl_str = f"{ttl // 60} 分鐘"
            elif ttl < 86400:
                ttl_str = f"{ttl // 3600} 小時"
            else:
                ttl_str = f"{ttl // 86400} 天"

            self.console.print(f"📦 TTL: {ttl_str}")

            result, cache_hit = self.request_with_cache(
                prompt=f"測試 TTL {ttl} 秒的快取",
                config=config,
                max_tokens=50
            )

            if result:
                self.console.print(f"   ✅ 配置成功\n")

    def _analyze_cache_performance(self, results: List[Dict], test_name: str):
        """
        分析快取性能

        計算和顯示快取相關的統計信息:
        - 命中率
        - 成本節省
        - 時間節省
        """
        if not results:
            return

        self.console.print(f"\n[bold]📊 {test_name} 性能分析[/bold]")
        self.console.print("-" * 80)

        # 統計
        total_requests = len(results)
        cache_hits = sum(1 for r in results if r["cache_hit"])
        cache_misses = total_requests - cache_hits
        hit_rate = (cache_hits / total_requests) * 100 if total_requests > 0 else 0

        # 成本計算
        total_cost = sum(r["cost"]["total_cost_usd"] for r in results)
        cached_requests_cost = sum(
            r["cost"]["total_cost_usd"] for r in results if not r["cache_hit"]
        )
        cost_saved = total_cost - cached_requests_cost

        # 時間計算
        avg_api_time = sum(r["duration"] for r in results if not r["cache_hit"]) / max(cache_misses, 1)
        avg_cache_time = sum(r["duration"] for r in results if r["cache_hit"]) / max(cache_hits, 1)
        time_saved = cache_hits * (avg_api_time - avg_cache_time)

        # 創建統計表格
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("指標", style="cyan")
        table.add_column("數值", style="green")

        table.add_row("總請求數", str(total_requests))
        table.add_row("快取命中", f"{cache_hits} ({hit_rate:.1f}%)")
        table.add_row("快取未命中", f"{cache_misses} ({100-hit_rate:.1f}%)")
        table.add_row("", "")
        table.add_row("總成本", f"${total_cost:.6f}")
        table.add_row("實際成本", f"${cached_requests_cost:.6f}")
        table.add_row("節省成本", f"${cost_saved:.6f}")
        table.add_row("節省比例", f"{(cost_saved/total_cost*100) if total_cost > 0 else 0:.1f}%")
        table.add_row("", "")
        table.add_row("平均 API 時間", f"{avg_api_time:.3f}s")
        table.add_row("平均快取時間", f"{avg_cache_time:.3f}s")
        table.add_row("節省時間", f"{time_saved:.3f}s")

        self.console.print(table)

    def compare_cache_strategies(self):
        """
        比較不同快取策略

        對比啟用和未啟用快取的性能差異。
        """
        self.console.print("\n[bold cyan]⚖️  比較快取策略[/bold cyan]")
        self.console.print("=" * 80)

        test_prompts = [
            "什麼是深度學習?",
            "解釋神經網絡的工作原理",
            "什麼是深度學習?",  # 重複
            "機器學習和深度學習的區別",
            "什麼是深度學習?",  # 重複
        ]

        # 策略 1: 不使用快取
        self.console.print("\n1️⃣  不使用快取")
        config_no_cache = CacheConfig(enabled=False)

        no_cache_results = []
        for prompt in test_prompts:
            result, _ = self.request_with_cache(
                prompt=prompt,
                config=config_no_cache,
                max_tokens=100
            )
            if result:
                no_cache_results.append(result)
            time.sleep(0.5)

        # 策略 2: 使用精確快取
        self.console.print("\n2️⃣  使用精確快取")
        config_with_cache = CacheConfig(
            enabled=True,
            cache_type=CacheType.EXACT,
            ttl_seconds=3600
        )

        cache_results = []
        for prompt in test_prompts:
            result, cache_hit = self.request_with_cache(
                prompt=prompt,
                config=config_with_cache,
                max_tokens=100
            )
            if result:
                cache_results.append(result)
                status = "🎯" if cache_hit else "📡"
                self.console.print(f"{status} {prompt[:50]}...")
            time.sleep(0.5)

        # 對比分析
        self._compare_results(no_cache_results, cache_results)

    def _compare_results(self, no_cache: List[Dict], with_cache: List[Dict]):
        """對比兩組結果"""
        self.console.print("\n[bold]📊 策略對比[/bold]")

        # 計算統計
        no_cache_cost = sum(r["cost"]["total_cost_usd"] for r in no_cache)
        no_cache_time = sum(r["duration"] for r in no_cache)

        with_cache_cost = sum(
            r["cost"]["total_cost_usd"] for r in with_cache if not r["cache_hit"]
        )
        with_cache_time = sum(r["duration"] for r in with_cache)

        cache_hits = sum(1 for r in with_cache if r["cache_hit"])

        # 創建對比表格
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("指標", style="cyan")
        table.add_column("無快取", style="yellow")
        table.add_column("有快取", style="green")
        table.add_column("改善", style="bold green")

        table.add_row(
            "總成本 (USD)",
            f"${no_cache_cost:.6f}",
            f"${with_cache_cost:.6f}",
            f"-{((no_cache_cost - with_cache_cost) / no_cache_cost * 100):.1f}%"
        )
        table.add_row(
            "總時間 (秒)",
            f"{no_cache_time:.3f}",
            f"{with_cache_time:.3f}",
            f"-{((no_cache_time - with_cache_time) / no_cache_time * 100):.1f}%"
        )
        table.add_row(
            "快取命中",
            "0",
            str(cache_hits),
            f"+{cache_hits}"
        )

        self.console.print(table)

    def visualize_cache_stats(self):
        """
        可視化快取統計

        生成圖表展示快取性能。
        """
        if not self.request_history:
            self.console.print("⚠️  [yellow]沒有數據可視化[/yellow]")
            return

        self.console.print("\n[bold cyan]📈 生成快取性能圖表[/bold cyan]")

        # 創建子圖
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Helicone 快取性能分析', fontsize=16, fontweight='bold')

        # 1. 快取命中率餅圖
        cache_hits = sum(1 for r in self.request_history if r["cache_hit"])
        cache_misses = len(self.request_history) - cache_hits

        axes[0, 0].pie(
            [cache_hits, cache_misses],
            labels=['快取命中', '快取未命中'],
            autopct='%1.1f%%',
            colors=['#4CAF50', '#FF9800']
        )
        axes[0, 0].set_title('快取命中率')

        # 2. 成本對比條形圖
        no_cache_cost = sum(r["cost"]["total_cost_usd"] for r in self.request_history)
        actual_cost = sum(
            r["cost"]["total_cost_usd"] for r in self.request_history if not r["cache_hit"]
        )

        axes[0, 1].bar(
            ['無快取成本', '實際成本', '節省成本'],
            [no_cache_cost, actual_cost, no_cache_cost - actual_cost],
            color=['#FF5722', '#2196F3', '#4CAF50']
        )
        axes[0, 1].set_title('成本對比')
        axes[0, 1].set_ylabel('成本 (USD)')

        # 3. 響應時間對比
        api_times = [r["duration"] for r in self.request_history if not r["cache_hit"]]
        cache_times = [r["duration"] for r in self.request_history if r["cache_hit"]]

        if api_times and cache_times:
            axes[1, 0].boxplot(
                [api_times, cache_times],
                labels=['API 調用', '快取響應']
            )
            axes[1, 0].set_title('響應時間分布')
            axes[1, 0].set_ylabel('時間 (秒)')

        # 4. 時間序列
        timestamps = [i for i in range(len(self.request_history))]
        colors = ['green' if r["cache_hit"] else 'orange' for r in self.request_history]

        axes[1, 1].scatter(timestamps, [r["duration"] for r in self.request_history], c=colors)
        axes[1, 1].set_title('請求時間序列')
        axes[1, 1].set_xlabel('請求序號')
        axes[1, 1].set_ylabel('響應時間 (秒)')
        axes[1, 1].legend(['快取命中', '快取未命中'])

        plt.tight_layout()
        plt.savefig('cache_performance.png', dpi=300, bbox_inches='tight')
        self.console.print("✅ [green]圖表已保存為 cache_performance.png[/green]")

    def get_cache_recommendations(self) -> List[str]:
        """
        基於歷史數據提供快取優化建議
        """
        recommendations = []

        if self.stats.total_requests == 0:
            return ["暫無足夠數據提供建議"]

        hit_rate = self.stats.hit_rate

        if hit_rate < 20:
            recommendations.append(
                "⚠️  快取命中率低於 20%。建議:\n"
                "   - 檢查是否有重複查詢\n"
                "   - 考慮使用語義快取\n"
                "   - 增加 TTL 時間"
            )
        elif hit_rate < 50:
            recommendations.append(
                "💡 快取命中率中等。建議:\n"
                "   - 分析查詢模式,識別常見問題\n"
                "   - 預熱常用查詢的快取\n"
                "   - 調整語義快取閾值"
            )
        else:
            recommendations.append(
                "✅ 快取命中率良好 (>50%)。繼續保持!"
            )

        # 成本分析
        if self.stats.cost_saved_usd > 10:
            recommendations.append(
                f"💰 已節省 ${self.stats.cost_saved_usd:.2f}。快取策略效果顯著!"
            )

        return recommendations


def main():
    """主函數"""
    console = Console()
    console.print("[bold green]🎯 Helicone 快取策略演示[/bold green]\n")

    try:
        # 初始化管理器
        manager = HeliconeCacheManager()

        # 測試 1: 精確快取
        manager.test_exact_caching(iterations=3)

        # 測試 2: 語義快取
        # manager.test_semantic_caching()

        # 測試 3: 不同 TTL
        manager.test_different_ttl()

        # 測試 4: 策略對比
        manager.compare_cache_strategies()

        # 顯示總體統計
        console.print("\n[bold cyan]📊 總體快取統計[/bold cyan]")
        console.print("=" * 80)
        console.print(f"總請求數: {manager.stats.total_requests}")
        console.print(f"快取命中: {manager.stats.cache_hits} ({manager.stats.hit_rate:.1f}%)")
        console.print(f"快取未命中: {manager.stats.cache_misses} ({manager.stats.miss_rate:.1f}%)")
        console.print(f"節省成本: ${manager.stats.cost_saved_usd:.6f}")
        console.print(f"節省時間: {manager.stats.time_saved_seconds:.3f}s")

        # 獲取建議
        console.print("\n[bold cyan]💡 優化建議[/bold cyan]")
        console.print("=" * 80)
        for rec in manager.get_cache_recommendations():
            console.print(rec)

        # 生成可視化
        # manager.visualize_cache_stats()

        console.print("\n✅ [green]演示完成![/green]")

    except Exception as e:
        console.print(f"\n❌ [red]錯誤: {str(e)}[/red]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

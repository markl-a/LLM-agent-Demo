"""
Claude Code SDK 生產部署示例

本示例展示：
1. 生產環境配置
2. 錯誤處理和重試
3. 監控和日誌
4. 性能優化
5. 安全最佳實踐
"""

import os
import time
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from anthropic import Anthropic, APIError, RateLimitError, APIConnectionError
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.logging import RichHandler
from dotenv import load_dotenv
import functools

console = Console()
load_dotenv()


# ==================== 日誌配置 ====================

def setup_logging():
    """配置生產級日誌"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            RichHandler(console=console, rich_tracebacks=True),
            logging.FileHandler("claude_app.log", encoding="utf-8")
        ]
    )
    return logging.getLogger(__name__)


logger = setup_logging()


# ==================== 錯誤處理和重試 ====================

def retry_with_exponential_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    exponential_base: float = 2.0,
    jitter: bool = True
):
    """指數退避重試裝飾器"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)

                except RateLimitError as e:
                    if attempt == max_retries - 1:
                        raise

                    logger.warning(f"速率限制，重試 {attempt + 1}/{max_retries}")
                    time.sleep(delay)
                    delay *= exponential_base

                    if jitter:
                        import random
                        delay *= (0.5 + random.random())

                except APIConnectionError as e:
                    if attempt == max_retries - 1:
                        raise

                    logger.warning(f"連接錯誤，重試 {attempt + 1}/{max_retries}")
                    time.sleep(delay)
                    delay *= exponential_base

                except APIError as e:
                    logger.error(f"API 錯誤: {e}")
                    raise

            raise Exception(f"重試 {max_retries} 次後仍然失敗")

        return wrapper
    return decorator


# ==================== 生產級客戶端 ====================

class ProductionClaudeClient:
    """生產級 Claude 客戶端"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: int = 60,
        max_retries: int = 3
    ):
        self.client = Anthropic(api_key=api_key)
        self.timeout = timeout
        self.max_retries = max_retries

        # 統計數據
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_tokens": 0,
            "total_cost": 0.0
        }

        logger.info("生產級 Claude 客戶端已初始化")

    @retry_with_exponential_backoff(max_retries=3)
    def create_message(
        self,
        messages: list,
        model: str = "claude-3-5-sonnet-20241022",
        max_tokens: int = 1024,
        **kwargs
    ) -> Dict[str, Any]:
        """創建消息（帶重試和監控）"""
        start_time = time.time()
        self.stats["total_requests"] += 1

        try:
            logger.info(f"發送請求到 Claude ({model})")

            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=messages,
                **kwargs
            )

            # 更新統計
            self.stats["successful_requests"] += 1
            self.stats["total_tokens"] += response.usage.input_tokens + response.usage.output_tokens

            # 計算成本（示例價格）
            cost = self._calculate_cost(response.usage, model)
            self.stats["total_cost"] += cost

            duration = time.time() - start_time

            logger.info(
                f"請求成功 - "
                f"耗時: {duration:.2f}s, "
                f"Tokens: {response.usage.input_tokens + response.usage.output_tokens}, "
                f"成本: ${cost:.4f}"
            )

            return {
                "response": response,
                "duration": duration,
                "cost": cost
            }

        except Exception as e:
            self.stats["failed_requests"] += 1
            logger.error(f"請求失敗: {e}")
            raise

    def _calculate_cost(self, usage, model: str) -> float:
        """計算 API 調用成本"""
        # 示例價格（實際價格請查閱官方文檔）
        pricing = {
            "claude-3-5-sonnet-20241022": {
                "input": 0.003 / 1000,   # $3 per MTok
                "output": 0.015 / 1000   # $15 per MTok
            },
            "claude-3-opus-20240229": {
                "input": 0.015 / 1000,   # $15 per MTok
                "output": 0.075 / 1000   # $75 per MTok
            },
            "claude-3-haiku-20240307": {
                "input": 0.00025 / 1000, # $0.25 per MTok
                "output": 0.00125 / 1000 # $1.25 per MTok
            }
        }

        price = pricing.get(model, pricing["claude-3-5-sonnet-20241022"])

        cost = (
            usage.input_tokens * price["input"] +
            usage.output_tokens * price["output"]
        )

        return cost

    def get_stats(self) -> Dict[str, Any]:
        """獲取統計數據"""
        success_rate = (
            self.stats["successful_requests"] / self.stats["total_requests"] * 100
            if self.stats["total_requests"] > 0 else 0
        )

        return {
            **self.stats,
            "success_rate": success_rate
        }


# ==================== 監控和指標 ====================

class MetricsCollector:
    """指標收集器"""

    def __init__(self):
        self.metrics = {
            "requests": [],
            "errors": [],
            "latencies": []
        }

    def record_request(self, duration: float, tokens: int, cost: float):
        """記錄請求"""
        self.metrics["requests"].append({
            "timestamp": datetime.now().isoformat(),
            "duration": duration,
            "tokens": tokens,
            "cost": cost
        })

    def record_error(self, error_type: str, message: str):
        """記錄錯誤"""
        self.metrics["errors"].append({
            "timestamp": datetime.now().isoformat(),
            "type": error_type,
            "message": message
        })

    def get_summary(self) -> Dict[str, Any]:
        """獲取指標摘要"""
        if not self.metrics["requests"]:
            return {"message": "沒有數據"}

        durations = [r["duration"] for r in self.metrics["requests"]]
        costs = [r["cost"] for r in self.metrics["requests"]]

        return {
            "total_requests": len(self.metrics["requests"]),
            "total_errors": len(self.metrics["errors"]),
            "avg_latency": sum(durations) / len(durations),
            "max_latency": max(durations),
            "total_cost": sum(costs)
        }


# ==================== 示例演示 ====================

def demo_production_client():
    """生產客戶端示例"""
    console.print("\n[bold cyan]1. 生產級客戶端[/bold cyan]\n")

    client = ProductionClaudeClient()

    # 發送請求
    messages = [
        {"role": "user", "content": "Hello, Claude!"}
    ]

    result = client.create_message(messages)

    console.print("[green]✓ 請求成功[/green]")
    console.print(f"[yellow]耗時：{result['duration']:.2f}s[/yellow]")
    console.print(f"[yellow]成本：${result['cost']:.4f}[/yellow]\n")

    # 顯示統計
    stats = client.get_stats()

    table = Table(title="客戶端統計")
    table.add_column("指標", style="cyan")
    table.add_column("值", style="yellow")

    table.add_row("總請求數", str(stats["total_requests"]))
    table.add_row("成功請求", str(stats["successful_requests"]))
    table.add_row("失敗請求", str(stats["failed_requests"]))
    table.add_row("成功率", f"{stats['success_rate']:.1f}%")
    table.add_row("總 Tokens", str(stats["total_tokens"]))
    table.add_row("總成本", f"${stats['total_cost']:.4f}")

    console.print(table)
    console.print()


def demo_error_handling():
    """錯誤處理示例"""
    console.print("[bold cyan]2. 錯誤處理[/bold cyan]\n")

    client = ProductionClaudeClient()

    # 模擬不同的錯誤場景
    error_scenarios = [
        ("無效模型", {"messages": [{"role": "user", "content": "test"}], "model": "invalid-model"}),
        ("超長輸入", {"messages": [{"role": "user", "content": "x" * 1000000}]}),
    ]

    for scenario_name, params in error_scenarios:
        console.print(f"[yellow]測試場景：{scenario_name}[/yellow]")

        try:
            client.create_message(**params)
        except Exception as e:
            console.print(f"[red]✓ 捕獲錯誤：{type(e).__name__}[/red]")
            logger.error(f"場景 '{scenario_name}' 錯誤：{e}")

        console.print()


def demo_monitoring():
    """監控示例"""
    console.print("[bold cyan]3. 監控和指標[/bold cyan]\n")

    metrics = MetricsCollector()

    # 模擬記錄
    metrics.record_request(1.2, 500, 0.015)
    metrics.record_request(0.8, 300, 0.009)
    metrics.record_request(1.5, 700, 0.021)
    metrics.record_error("RateLimitError", "Too many requests")

    summary = metrics.get_summary()

    console.print("[green]指標摘要：[/green]")
    for key, value in summary.items():
        console.print(f"  [cyan]{key}：[/cyan]{value}")

    console.print()


def demo_caching():
    """緩存策略示例"""
    console.print("[bold cyan]4. 緩存策略[/bold cyan]\n")

    cache_example = '''
from functools import lru_cache
import hashlib

class CachedClaudeClient:
    """帶緩存的客戶端"""

    def __init__(self):
        self.client = Anthropic()
        self.cache = {}

    def _get_cache_key(self, messages, model):
        """生成緩存鍵"""
        content = json.dumps(messages) + model
        return hashlib.md5(content.encode()).hexdigest()

    def create_message(self, messages, model, **kwargs):
        """帶緩存的消息創建"""
        cache_key = self._get_cache_key(messages, model)

        # 檢查緩存
        if cache_key in self.cache:
            logger.info("從緩存返回")
            return self.cache[cache_key]

        # 調用 API
        response = self.client.messages.create(
            messages=messages,
            model=model,
            **kwargs
        )

        # 存入緩存
        self.cache[cache_key] = response
        return response
'''

    console.print(Panel(cache_example, title="緩存實現", border_style="green"))
    console.print()


def demo_rate_limiting():
    """速率限制示例"""
    console.print("[bold cyan]5. 速率限制[/bold cyan]\n")

    rate_limit_example = '''
import asyncio
from asyncio import Semaphore

class RateLimitedClient:
    """限速客戶端"""

    def __init__(self, max_concurrent=5, requests_per_minute=50):
        self.client = Anthropic()
        self.semaphore = Semaphore(max_concurrent)
        self.requests_per_minute = requests_per_minute
        self.request_times = []

    async def create_message(self, messages, **kwargs):
        """限速的消息創建"""
        async with self.semaphore:
            # 檢查速率限制
            await self._wait_for_rate_limit()

            # 調用 API
            response = self.client.messages.create(
                messages=messages,
                **kwargs
            )

            self.request_times.append(time.time())
            return response

    async def _wait_for_rate_limit(self):
        """等待直到可以發送請求"""
        now = time.time()
        # 移除 1 分鐘前的記錄
        self.request_times = [
            t for t in self.request_times
            if now - t < 60
        ]

        if len(self.request_times) >= self.requests_per_minute:
            sleep_time = 60 - (now - self.request_times[0])
            await asyncio.sleep(sleep_time)
'''

    console.print(Panel(rate_limit_example, title="速率限制實現", border_style="green"))
    console.print()


def show_security_best_practices():
    """安全最佳實踐"""
    console.print("[bold cyan]6. 安全最佳實踐[/bold cyan]\n")

    practices = [
        ("API Key 管理", "使用環境變量或密鑰管理服務，絕不硬編碼"),
        ("輸入驗證", "驗證和清理所有用戶輸入"),
        ("輸出過濾", "檢查和過濾 AI 生成的內容"),
        ("訪問控制", "實施適當的認證和授權"),
        ("審計日誌", "記錄所有 API 調用和敏感操作"),
        ("錯誤處理", "不要暴露敏感錯誤信息給用戶"),
        ("HTTPS", "始終使用加密連接"),
        ("定期更新", "保持 SDK 和依賴更新"),
    ]

    for practice, description in practices:
        console.print(f"[green]✓ {practice}：[/green]{description}")

    console.print()


def show_deployment_checklist():
    """部署檢查清單"""
    console.print("[bold cyan]7. 部署檢查清單[/bold cyan]\n")

    checklist = [
        "✅ 配置生產級日誌",
        "✅ 實施錯誤處理和重試機制",
        "✅ 設置監控和告警",
        "✅ 配置速率限制",
        "✅ 實施緩存策略",
        "✅ 安全配置（API Key、HTTPS 等）",
        "✅ 性能測試和負載測試",
        "✅ 準備災難恢復計劃",
        "✅ 文檔和運維手冊",
        "✅ 監控儀表板",
    ]

    for item in checklist:
        console.print(f"  {item}")

    console.print()


def show_performance_tips():
    """性能優化建議"""
    console.print("[bold cyan]8. 性能優化建議[/bold cyan]\n")

    tips = [
        ("批量處理", "合併多個小請求為一個大請求"),
        ("異步處理", "使用異步 I/O 提升並發"),
        ("流式輸出", "對長響應使用流式處理"),
        ("緩存結果", "緩存常見查詢的結果"),
        ("選擇合適模型", "根據任務選擇性價比最優的模型"),
        ("控制 Token", "優化提示詞減少 Token 使用"),
        ("連接池", "復用 HTTP 連接"),
        ("CDN", "使用 CDN 加速靜態資源"),
    ]

    for tip, description in tips:
        console.print(f"[cyan]• {tip}：[/cyan]{description}")

    console.print()


def show_cost_optimization():
    """成本優化策略"""
    console.print("[bold cyan]9. 成本優化策略[/bold cyan]\n")

    strategies = [
        ("模型選擇", "簡單任務使用 Haiku，複雜任務用 Sonnet"),
        ("提示詞優化", "精簡提示詞減少輸入 Token"),
        ("緩存", "緩存相同查詢避免重複調用"),
        ("批處理", "批量處理減少請求次數"),
        ("Token 限制", "設置合理的 max_tokens"),
        ("監控", "跟蹤使用情況及時發現異常"),
        ("預算告警", "設置成本告警閾值"),
    ]

    for strategy, description in strategies:
        console.print(f"[yellow]💰 {strategy}：[/yellow]{description}")

    console.print()


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Claude Code SDK 生產部署[/bold cyan]\n"
        "[dim]學習如何在生產環境中部署和運維 Claude 應用[/dim]",
        border_style="cyan"
    ))

    # 1. 生產客戶端
    demo_production_client()

    # 2. 錯誤處理
    demo_error_handling()

    # 3. 監控
    demo_monitoring()

    # 4. 緩存
    demo_caching()

    # 5. 速率限制
    demo_rate_limiting()

    # 6. 安全實踐
    show_security_best_practices()

    # 7. 部署清單
    show_deployment_checklist()

    # 8. 性能優化
    show_performance_tips()

    # 9. 成本優化
    show_cost_optimization()

    # 完成
    console.print("="*60)
    console.print("[bold green]✓ 生產部署示例完成！[/bold green]")
    console.print("\n[cyan]關鍵要點：[/cyan]")
    console.print("  • 實施完善的錯誤處理和重試機制")
    console.print("  • 建立全面的監控和日誌系統")
    console.print("  • 注重安全性和成本控制")
    console.print("  • 持續優化性能和用戶體驗")


if __name__ == "__main__":
    main()

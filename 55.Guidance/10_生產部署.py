#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Guidance 生產部署示例
====================================================

本模塊展示如何將 Guidance 應用部署到生產環境:
1. 生產環境配置
2. 錯誤處理和日誌
3. 性能優化
4. 監控和告警
5. 緩存策略
6. 限流和熔斷
7. 高可用架構
8. 安全性考慮
9. Docker 容器化
10. 最佳實踐總結

這是一個完整的生產級實現示例，涵蓋了實際部署中
需要考慮的各個方面。

作者: Guidance 示例團隊
日期: 2025-01-01
"""

import os
import sys
import logging
import time
import json
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from functools import wraps
from collections import deque
import hashlib
import threading
from dataclasses import dataclass, asdict

try:
    from guidance import models, gen, select
    import guidance
except ImportError:
    print("錯誤: 請先安裝 guidance 庫")
    sys.exit(1)


# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('guidance_production.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


@dataclass
class ProductionConfig:
    """生產環境配置"""
    model_name: str = "gpt-4"
    api_key: Optional[str] = None
    max_retries: int = 3
    timeout: int = 30
    cache_enabled: bool = True
    cache_ttl: int = 3600
    rate_limit: int = 100  # 每分鐘請求數
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60
    monitoring_enabled: bool = True
    log_level: str = "INFO"


class CircuitBreaker:
    """熔斷器"""

    def __init__(self, threshold: int = 5, timeout: int = 60):
        """
        初始化熔斷器

        Args:
            threshold: 失敗次數閾值
            timeout: 熔斷超時時間（秒）
        """
        self.threshold = threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.lock = threading.Lock()

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        通過熔斷器調用函數

        Args:
            func: 要調用的函數
            *args, **kwargs: 函數參數

        Returns:
            函數返回值

        Raises:
            Exception: 熔斷器開啟時拋出異常
        """
        with self.lock:
            if self.state == "OPEN":
                if self._should_attempt_reset():
                    self.state = "HALF_OPEN"
                    logger.info("熔斷器進入半開狀態")
                else:
                    raise Exception("熔斷器開啟，拒絕請求")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result

        except Exception as e:
            self._on_failure()
            raise

    def _should_attempt_reset(self) -> bool:
        """判斷是否應該嘗試重置"""
        if self.last_failure_time is None:
            return True

        return (datetime.now() - self.last_failure_time).seconds >= self.timeout

    def _on_success(self):
        """成功時的處理"""
        with self.lock:
            self.failures = 0
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                logger.info("熔斷器關閉")

    def _on_failure(self):
        """失敗時的處理"""
        with self.lock:
            self.failures += 1
            self.last_failure_time = datetime.now()

            if self.failures >= self.threshold:
                self.state = "OPEN"
                logger.warning(f"熔斷器開啟 (失敗次數: {self.failures})")


class RateLimiter:
    """限流器"""

    def __init__(self, max_requests: int, time_window: int = 60):
        """
        初始化限流器

        Args:
            max_requests: 時間窗口內最大請求數
            time_window: 時間窗口（秒）
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = deque()
        self.lock = threading.Lock()

    def allow_request(self) -> bool:
        """
        檢查是否允許請求

        Returns:
            是否允許
        """
        with self.lock:
            now = datetime.now()

            # 移除過期的請求記錄
            while self.requests and (now - self.requests[0]).seconds >= self.time_window:
                self.requests.popleft()

            # 檢查是否超過限制
            if len(self.requests) >= self.max_requests:
                return False

            # 記錄新請求
            self.requests.append(now)
            return True


class CacheManager:
    """緩存管理器"""

    def __init__(self, ttl: int = 3600):
        """
        初始化緩存管理器

        Args:
            ttl: 緩存生存時間（秒）
        """
        self.ttl = ttl
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        """獲取緩存"""
        with self.lock:
            if key not in self.cache:
                return None

            entry = self.cache[key]

            # 檢查是否過期
            if (datetime.now() - entry["timestamp"]).seconds >= self.ttl:
                del self.cache[key]
                return None

            return entry["value"]

    def set(self, key: str, value: Any):
        """設置緩存"""
        with self.lock:
            self.cache[key] = {
                "value": value,
                "timestamp": datetime.now()
            }

    def clear(self):
        """清空緩存"""
        with self.lock:
            self.cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        """獲取緩存統計"""
        with self.lock:
            return {
                "size": len(self.cache),
                "ttl": self.ttl
            }


class PerformanceMonitor:
    """性能監控器"""

    def __init__(self):
        """初始化性能監控器"""
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_latency": 0.0,
            "cache_hits": 0,
            "cache_misses": 0
        }
        self.lock = threading.Lock()

    def record_request(self, success: bool, latency: float, cache_hit: bool):
        """
        記錄請求

        Args:
            success: 是否成功
            latency: 延遲（秒）
            cache_hit: 是否命中緩存
        """
        with self.lock:
            self.metrics["total_requests"] += 1

            if success:
                self.metrics["successful_requests"] += 1
            else:
                self.metrics["failed_requests"] += 1

            self.metrics["total_latency"] += latency

            if cache_hit:
                self.metrics["cache_hits"] += 1
            else:
                self.metrics["cache_misses"] += 1

    def get_metrics(self) -> Dict[str, Any]:
        """獲取性能指標"""
        with self.lock:
            total = self.metrics["total_requests"]

            if total == 0:
                return self.metrics.copy()

            return {
                **self.metrics,
                "success_rate": self.metrics["successful_requests"] / total * 100,
                "failure_rate": self.metrics["failed_requests"] / total * 100,
                "avg_latency": self.metrics["total_latency"] / total,
                "cache_hit_rate": self.metrics["cache_hits"] / total * 100 if total > 0 else 0
            }

    def reset(self):
        """重置指標"""
        with self.lock:
            for key in self.metrics:
                self.metrics[key] = 0 if isinstance(self.metrics[key], int) else 0.0


class ProductionGuidance:
    """
    生產級 Guidance 包裝器

    整合了錯誤處理、緩存、限流、監控等生產環境必需功能。
    """

    def __init__(self, config: ProductionConfig):
        """
        初始化生產級 Guidance

        Args:
            config: 生產環境配置
        """
        self.config = config
        self.cache = CacheManager(ttl=config.cache_ttl) if config.cache_enabled else None
        self.rate_limiter = RateLimiter(max_requests=config.rate_limit)
        self.circuit_breaker = CircuitBreaker(
            threshold=config.circuit_breaker_threshold,
            timeout=config.circuit_breaker_timeout
        )
        self.monitor = PerformanceMonitor() if config.monitoring_enabled else None

        # 設置日誌級別
        logger.setLevel(config.log_level)

        logger.info("生產級 Guidance 初始化完成")
        logger.info(f"配置: {asdict(config)}")

    def _get_cache_key(self, prompt: str, **kwargs) -> str:
        """生成緩存鍵"""
        key_data = f"{prompt}:{json.dumps(kwargs, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """
        帶重試的執行

        Args:
            func: 要執行的函數
            *args, **kwargs: 函數參數

        Returns:
            函數返回值
        """
        last_exception = None

        for attempt in range(self.config.max_retries):
            try:
                return func(*args, **kwargs)

            except Exception as e:
                last_exception = e
                logger.warning(f"執行失敗 (嘗試 {attempt + 1}/{self.config.max_retries}): {str(e)}")

                if attempt < self.config.max_retries - 1:
                    wait_time = 2 ** attempt  # 指數退避
                    logger.info(f"等待 {wait_time}s 後重試...")
                    time.sleep(wait_time)

        raise last_exception

    def generate(self, prompt: str, max_tokens: int = 100, **kwargs) -> str:
        """
        生成文本（生產級）

        Args:
            prompt: 提示詞
            max_tokens: 最大 token 數
            **kwargs: 其他參數

        Returns:
            生成的文本

        Raises:
            Exception: 生成失敗時拋出異常
        """
        start_time = time.time()
        cache_hit = False

        try:
            # 檢查限流
            if not self.rate_limiter.allow_request():
                raise Exception("請求超過限流閾值")

            # 檢查緩存
            if self.cache:
                cache_key = self._get_cache_key(prompt, max_tokens=max_tokens, **kwargs)
                cached_result = self.cache.get(cache_key)

                if cached_result is not None:
                    cache_hit = True
                    logger.info(f"緩存命中: {cache_key[:16]}...")

                    if self.monitor:
                        latency = time.time() - start_time
                        self.monitor.record_request(True, latency, True)

                    return cached_result

            # 實際生成
            def _generate():
                lm = models.OpenAI(
                    model=self.config.model_name,
                    api_key=self.config.api_key,
                    **kwargs
                )

                lm += prompt
                lm += gen(name="result", max_tokens=max_tokens)

                return lm["result"]

            # 通過熔斷器執行
            result = self.circuit_breaker.call(
                self._execute_with_retry,
                _generate
            )

            # 緩存結果
            if self.cache:
                self.cache.set(cache_key, result)

            # 記錄指標
            if self.monitor:
                latency = time.time() - start_time
                self.monitor.record_request(True, latency, cache_hit)

            logger.info(f"生成成功 (耗時: {time.time() - start_time:.2f}s)")
            return result

        except Exception as e:
            # 記錄錯誤
            logger.error(f"生成失敗: {str(e)}", exc_info=True)

            if self.monitor:
                latency = time.time() - start_time
                self.monitor.record_request(False, latency, cache_hit)

            raise

    def select(self, prompt: str, options: List[str], **kwargs) -> str:
        """
        選擇（生產級）

        Args:
            prompt: 提示詞
            options: 選項列表
            **kwargs: 其他參數

        Returns:
            選擇的選項
        """
        start_time = time.time()
        cache_hit = False

        try:
            # 檢查限流
            if not self.rate_limiter.allow_request():
                raise Exception("請求超過限流閾值")

            # 檢查緩存
            if self.cache:
                cache_key = self._get_cache_key(prompt, options=options, **kwargs)
                cached_result = self.cache.get(cache_key)

                if cached_result is not None:
                    cache_hit = True
                    logger.info(f"緩存命中: {cache_key[:16]}...")

                    if self.monitor:
                        latency = time.time() - start_time
                        self.monitor.record_request(True, latency, True)

                    return cached_result

            # 實際選擇
            def _select():
                lm = models.OpenAI(
                    model=self.config.model_name,
                    api_key=self.config.api_key,
                    **kwargs
                )

                lm += prompt
                lm += select(options, name="selection")

                return lm["selection"]

            # 通過熔斷器執行
            result = self.circuit_breaker.call(
                self._execute_with_retry,
                _select
            )

            # 緩存結果
            if self.cache:
                self.cache.set(cache_key, result)

            # 記錄指標
            if self.monitor:
                latency = time.time() - start_time
                self.monitor.record_request(True, latency, cache_hit)

            logger.info(f"選擇成功: {result}")
            return result

        except Exception as e:
            logger.error(f"選擇失敗: {str(e)}", exc_info=True)

            if self.monitor:
                latency = time.time() - start_time
                self.monitor.record_request(False, latency, cache_hit)

            raise

    def get_metrics(self) -> Optional[Dict[str, Any]]:
        """獲取性能指標"""
        if self.monitor:
            return self.monitor.get_metrics()
        return None

    def get_cache_stats(self) -> Optional[Dict[str, Any]]:
        """獲取緩存統計"""
        if self.cache:
            return self.cache.get_stats()
        return None

    def reset_metrics(self):
        """重置性能指標"""
        if self.monitor:
            self.monitor.reset()


def example_production_usage():
    """
    示例: 生產環境使用

    演示如何在生產環境中使用 Guidance。
    """
    print(f"\n{'='*60}")
    print("生產環境使用示例")
    print(f"{'='*60}\n")

    # 創建配置
    config = ProductionConfig(
        model_name="gpt-4",
        api_key=os.getenv("OPENAI_API_KEY"),
        max_retries=3,
        cache_enabled=True,
        cache_ttl=3600,
        rate_limit=100,
        monitoring_enabled=True,
        log_level="INFO"
    )

    # 初始化生產級 Guidance
    guidance_prod = ProductionGuidance(config)

    print("配置:")
    print(json.dumps(asdict(config), indent=2))
    print()

    # 示例 1: 文本生成
    print("示例 1: 文本生成")
    try:
        result = guidance_prod.generate(
            "用一句話解釋機器學習: ",
            max_tokens=80
        )
        print(f"結果: {result}\n")
    except Exception as e:
        print(f"錯誤: {str(e)}\n")

    # 示例 2: 選擇
    print("示例 2: 選擇")
    try:
        result = guidance_prod.select(
            "Python 是動態類型語言嗎? ",
            options=["是", "否"]
        )
        print(f"選擇: {result}\n")
    except Exception as e:
        print(f"錯誤: {str(e)}\n")

    # 示例 3: 緩存測試
    print("示例 3: 緩存測試（重複請求）")
    for i in range(3):
        start = time.time()
        try:
            result = guidance_prod.generate(
                "解釋深度學習: ",
                max_tokens=60
            )
            elapsed = time.time() - start
            print(f"  請求 {i+1}: 耗時 {elapsed:.3f}s")
        except Exception as e:
            print(f"  請求 {i+1} 失敗: {str(e)}")
    print()

    # 獲取指標
    print("性能指標:")
    metrics = guidance_prod.get_metrics()
    if metrics:
        print(json.dumps(metrics, indent=2))
    print()

    print("緩存統計:")
    cache_stats = guidance_prod.get_cache_stats()
    if cache_stats:
        print(json.dumps(cache_stats, indent=2))
    print()


def example_docker_deployment():
    """
    示例: Docker 部署

    展示 Docker 容器化部署配置。
    """
    print(f"\n{'='*60}")
    print("Docker 部署示例")
    print(f"{'='*60}\n")

    dockerfile = """
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安裝依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用代碼
COPY . .

# 環境變量
ENV PYTHONUNBUFFERED=1
ENV OPENAI_API_KEY=""

# 暴露端口
EXPOSE 8000

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# 啟動應用
CMD ["python", "app.py"]
"""

    docker_compose = """
# docker-compose.yml
version: '3.8'

services:
  guidance-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - LOG_LEVEL=INFO
      - CACHE_ENABLED=true
      - RATE_LIMIT=100
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    restart: unless-stopped

volumes:
  redis_data:
  prometheus_data:
"""

    print("Dockerfile:")
    print(dockerfile)
    print("\ndocker-compose.yml:")
    print(docker_compose)
    print()


def example_best_practices():
    """
    示例: 最佳實踐

    總結生產部署的最佳實踐。
    """
    print(f"\n{'='*60}")
    print("生產部署最佳實踐")
    print(f"{'='*60}\n")

    best_practices = {
        "1. 錯誤處理": [
            "實現全面的異常捕獲",
            "使用重試機制（指數退避）",
            "記錄詳細的錯誤日誌",
            "提供友好的錯誤消息"
        ],
        "2. 性能優化": [
            "啟用結果緩存",
            "實施請求限流",
            "使用連接池",
            "優化批量處理",
            "監控和調優參數"
        ],
        "3. 可靠性": [
            "實現熔斷器模式",
            "設置合理的超時",
            "準備降級方案",
            "實現健康檢查",
            "定期備份數據"
        ],
        "4. 監控告警": [
            "記錄關鍵指標（延遲、錯誤率等）",
            "設置告警閾值",
            "使用日誌聚合工具",
            "定期審查指標",
            "建立儀表板"
        ],
        "5. 安全性": [
            "保護 API 密鑰",
            "使用環境變量",
            "限制訪問權限",
            "實施請求驗證",
            "加密敏感數據"
        ],
        "6. 可擴展性": [
            "使用負載均衡",
            "支持水平擴展",
            "實現無狀態設計",
            "使用消息隊列",
            "準備彈性伸縮"
        ],
        "7. 測試": [
            "編寫單元測試",
            "進行集成測試",
            "執行壓力測試",
            "模擬故障場景",
            "持續集成/部署"
        ],
        "8. 文檔": [
            "編寫 API 文檔",
            "記錄部署流程",
            "維護變更日誌",
            "提供使用示例",
            "建立故障排查指南"
        ]
    }

    for category, practices in best_practices.items():
        print(f"\n{category}:")
        for practice in practices:
            print(f"  ✓ {practice}")

    print()


def example_monitoring_dashboard():
    """
    示例: 監控儀表板

    展示如何構建監控儀表板。
    """
    print(f"\n{'='*60}")
    print("監控儀表板示例")
    print(f"{'='*60}\n")

    prometheus_config = """
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'guidance-api'
    static_configs:
      - targets: ['guidance-api:8000']
    metrics_path: '/metrics'
"""

    grafana_dashboard = """
{
  "dashboard": {
    "title": "Guidance Production Metrics",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "rate(guidance_requests_total[5m])"
          }
        ]
      },
      {
        "title": "Success Rate",
        "targets": [
          {
            "expr": "guidance_requests_success / guidance_requests_total * 100"
          }
        ]
      },
      {
        "title": "Average Latency",
        "targets": [
          {
            "expr": "guidance_latency_seconds_sum / guidance_latency_seconds_count"
          }
        ]
      },
      {
        "title": "Cache Hit Rate",
        "targets": [
          {
            "expr": "guidance_cache_hits / guidance_cache_total * 100"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(guidance_errors_total[5m])"
          }
        ]
      }
    ]
  }
}
"""

    print("Prometheus 配置:")
    print(prometheus_config)
    print("\nGrafana 儀表板 JSON:")
    print(grafana_dashboard)
    print()


def main():
    """主函數"""
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║         Guidance 框架 - 生產部署示例                       ║
    ║                                                            ║
    ║  完整的生產級部署方案                                      ║
    ║  包括錯誤處理、監控、緩存、限流等                          ║
    ╚════════════════════════════════════════════════════════════╝
    """)

    print("\n目錄:")
    print("  1. 生產環境使用示例")
    print("  2. Docker 部署配置")
    print("  3. 最佳實踐總結")
    print("  4. 監控儀表板配置")
    print()

    # 運行示例
    if os.getenv("OPENAI_API_KEY"):
        example_production_usage()
    else:
        print("⚠️  未設置 OPENAI_API_KEY，跳過生產環境示例\n")

    example_docker_deployment()
    example_best_practices()
    example_monitoring_dashboard()

    print(f"\n{'='*60}")
    print("生產部署總結")
    print(f"{'='*60}\n")

    print("關鍵要點:")
    key_points = [
        "1. 使用生產級配置（重試、超時、限流等）",
        "2. 實現全面的錯誤處理和日誌記錄",
        "3. 啟用緩存和性能優化",
        "4. 設置監控和告警系統",
        "5. 使用容器化部署（Docker）",
        "6. 實施熔斷器和降級策略",
        "7. 定期審查和優化性能",
        "8. 保持文檔更新和團隊培訓"
    ]

    for point in key_points:
        print(f"  {point}")

    print("\n✓ 所有生產部署示例展示完成!")
    print("\n建議:")
    print("  - 根據實際需求調整配置參數")
    print("  - 在測試環境充分驗證")
    print("  - 建立完善的監控體系")
    print("  - 準備應急預案和回滾方案")
    print()


if __name__ == "__main__":
    main()

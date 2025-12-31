#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Composio 生產部署範例
=====================

本範例展示如何將 Composio 應用部署到生產環境，包括：
1. 環境配置
2. 錯誤處理和日誌
3. 性能優化
4. 安全最佳實踐
5. 監控和告警
6. 擴展性設計
7. 部署架構

將 AI Agent 應用安全、可靠地部署到生產環境的完整指南。

作者: Composio 團隊
日期: 2025-01-01
"""

import os
import sys
import json
import logging
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from functools import wraps
from dataclasses import dataclass, asdict
import hashlib
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 導入 Composio SDK
try:
    from composio import Composio, App
    from composio.client.exceptions import ComposioException
except ImportError as e:
    print("錯誤：請先安裝 Composio SDK")
    print("執行: pip install composio-core")
    sys.exit(1)


# ============================================================================
# 日誌配置
# ============================================================================

def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    """
    配置日誌系統

    Args:
        log_level: 日誌級別
        log_file: 日誌文件路徑（可選）
    """
    # 日誌格式
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # 基礎配置
    handlers = [logging.StreamHandler()]

    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=handlers
    )

    return logging.getLogger(__name__)


# 初始化日誌
logger = setup_logging(
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    log_file=os.getenv("LOG_FILE")
)


# ============================================================================
# 配置管理
# ============================================================================

@dataclass
class ProductionConfig:
    """
    生產環境配置
    """
    # API 配置
    composio_api_key: str
    openai_api_key: Optional[str] = None

    # 應用配置
    app_name: str = "composio-production"
    environment: str = "production"
    debug: bool = False

    # 性能配置
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout: int = 30
    rate_limit: int = 100  # 每分鐘請求數

    # 快取配置
    cache_enabled: bool = True
    cache_ttl: int = 300  # 秒

    # 安全配置
    enable_ssl: bool = True
    verify_ssl: bool = True

    # 監控配置
    enable_metrics: bool = True
    metrics_port: int = 9090

    @classmethod
    def from_env(cls) -> 'ProductionConfig':
        """從環境變數載入配置"""
        return cls(
            composio_api_key=os.getenv("COMPOSIO_API_KEY", ""),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            app_name=os.getenv("APP_NAME", "composio-production"),
            environment=os.getenv("ENVIRONMENT", "production"),
            debug=os.getenv("DEBUG", "false").lower() == "true",
            max_retries=int(os.getenv("MAX_RETRIES", "3")),
            timeout=int(os.getenv("TIMEOUT", "30")),
            rate_limit=int(os.getenv("RATE_LIMIT", "100")),
            cache_enabled=os.getenv("CACHE_ENABLED", "true").lower() == "true",
            cache_ttl=int(os.getenv("CACHE_TTL", "300"))
        )

    def validate(self):
        """驗證配置"""
        errors = []

        if not self.composio_api_key:
            errors.append("COMPOSIO_API_KEY 未設置")

        if self.environment == "production" and self.debug:
            errors.append("生產環境不應啟用 DEBUG 模式")

        if self.max_retries < 0:
            errors.append("MAX_RETRIES 必須為正數")

        if errors:
            raise ValueError(f"配置驗證失敗: {', '.join(errors)}")


# ============================================================================
# 錯誤處理和重試
# ============================================================================

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """
    重試裝飾器

    Args:
        max_retries: 最大重試次數
        delay: 重試延遲（秒）
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            f"函數 {func.__name__} 執行失敗（嘗試 {attempt + 1}/{max_retries + 1}）: {e}"
                        )
                        time.sleep(delay * (2 ** attempt))  # 指數退避
                    else:
                        logger.error(
                            f"函數 {func.__name__} 在 {max_retries + 1} 次嘗試後仍失敗"
                        )

            raise last_exception

        return wrapper
    return decorator


class ErrorHandler:
    """
    錯誤處理器
    """

    @staticmethod
    def handle_composio_error(error: Exception) -> Dict[str, Any]:
        """
        處理 Composio 錯誤

        Args:
            error: 異常對象

        Returns:
            錯誤響應
        """
        logger.error(f"Composio 錯誤: {error}", exc_info=True)

        if isinstance(error, ComposioException):
            return {
                "success": False,
                "error": "composio_error",
                "message": str(error),
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "error": "internal_error",
                "message": "內部錯誤，請稍後重試",
                "timestamp": datetime.now().isoformat()
            }

    @staticmethod
    def handle_validation_error(error: Exception) -> Dict[str, Any]:
        """處理驗證錯誤"""
        logger.warning(f"驗證錯誤: {error}")

        return {
            "success": False,
            "error": "validation_error",
            "message": str(error),
            "timestamp": datetime.now().isoformat()
        }


# ============================================================================
# 快取管理
# ============================================================================

class SimpleCache:
    """
    簡單的記憶體快取
    """

    def __init__(self, ttl: int = 300):
        """
        初始化快取

        Args:
            ttl: 快取生存時間（秒）
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl

    def get(self, key: str) -> Optional[Any]:
        """
        獲取快取值

        Args:
            key: 快取鍵

        Returns:
            快取值或 None
        """
        if key not in self.cache:
            return None

        entry = self.cache[key]
        if time.time() - entry['timestamp'] > self.ttl:
            # 過期
            del self.cache[key]
            return None

        logger.debug(f"快取命中: {key}")
        return entry['value']

    def set(self, key: str, value: Any):
        """
        設置快取值

        Args:
            key: 快取鍵
            value: 快取值
        """
        self.cache[key] = {
            'value': value,
            'timestamp': time.time()
        }
        logger.debug(f"快取設置: {key}")

    def clear(self):
        """清空快取"""
        self.cache.clear()
        logger.info("快取已清空")

    def cleanup(self):
        """清理過期快取"""
        now = time.time()
        expired_keys = [
            key for key, entry in self.cache.items()
            if now - entry['timestamp'] > self.ttl
        ]

        for key in expired_keys:
            del self.cache[key]

        if expired_keys:
            logger.info(f"清理了 {len(expired_keys)} 個過期快取項")


# ============================================================================
# 速率限制
# ============================================================================

class RateLimiter:
    """
    速率限制器
    """

    def __init__(self, max_requests: int = 100, window: int = 60):
        """
        初始化速率限制器

        Args:
            max_requests: 最大請求數
            window: 時間窗口（秒）
        """
        self.max_requests = max_requests
        self.window = window
        self.requests: Dict[str, List[float]] = {}

    def is_allowed(self, identifier: str) -> bool:
        """
        檢查是否允許請求

        Args:
            identifier: 標識符（如用戶 ID）

        Returns:
            是否允許
        """
        now = time.time()

        # 初始化或清理舊請求
        if identifier not in self.requests:
            self.requests[identifier] = []

        # 移除窗口外的請求
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if now - req_time < self.window
        ]

        # 檢查是否超過限制
        if len(self.requests[identifier]) >= self.max_requests:
            logger.warning(f"速率限制觸發: {identifier}")
            return False

        # 記錄新請求
        self.requests[identifier].append(now)
        return True


# ============================================================================
# 指標收集
# ============================================================================

class MetricsCollector:
    """
    指標收集器
    """

    def __init__(self):
        """初始化指標收集器"""
        self.metrics: Dict[str, Any] = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_latency": 0.0,
            "cache_hits": 0,
            "cache_misses": 0
        }

    def record_request(self, success: bool, latency: float):
        """
        記錄請求

        Args:
            success: 是否成功
            latency: 延遲（秒）
        """
        self.metrics["total_requests"] += 1
        if success:
            self.metrics["successful_requests"] += 1
        else:
            self.metrics["failed_requests"] += 1

        self.metrics["total_latency"] += latency

    def record_cache_hit(self):
        """記錄快取命中"""
        self.metrics["cache_hits"] += 1

    def record_cache_miss(self):
        """記錄快取未命中"""
        self.metrics["cache_misses"] += 1

    def get_metrics(self) -> Dict[str, Any]:
        """獲取指標"""
        total = self.metrics["total_requests"]

        metrics = dict(self.metrics)

        if total > 0:
            metrics["success_rate"] = self.metrics["successful_requests"] / total
            metrics["average_latency"] = self.metrics["total_latency"] / total

            cache_total = self.metrics["cache_hits"] + self.metrics["cache_misses"]
            if cache_total > 0:
                metrics["cache_hit_rate"] = self.metrics["cache_hits"] / cache_total

        return metrics

    def reset(self):
        """重置指標"""
        for key in self.metrics:
            if isinstance(self.metrics[key], int):
                self.metrics[key] = 0
            else:
                self.metrics[key] = 0.0


# ============================================================================
# 生產級 Composio 客戶端
# ============================================================================

class ProductionComposioClient:
    """
    生產級 Composio 客戶端

    包含錯誤處理、重試、快取、監控等生產功能
    """

    def __init__(self, config: ProductionConfig):
        """
        初始化客戶端

        Args:
            config: 生產配置
        """
        logger.info("初始化生產級 Composio 客戶端")

        # 驗證配置
        config.validate()

        self.config = config
        self.client = Composio(api_key=config.composio_api_key)

        # 初始化組件
        self.cache = SimpleCache(ttl=config.cache_ttl) if config.cache_enabled else None
        self.rate_limiter = RateLimiter(max_requests=config.rate_limit)
        self.metrics = MetricsCollector() if config.enable_metrics else None
        self.error_handler = ErrorHandler()

        logger.info(f"客戶端初始化完成（環境: {config.environment}）")

    @retry_on_failure(max_retries=3, delay=1.0)
    def execute_action(self, entity_id: str, action: str, params: Dict[str, Any],
                      user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        執行動作（生產版本）

        Args:
            entity_id: 實體 ID
            action: 動作名稱
            params: 參數
            user_id: 用戶 ID（用於速率限制）

        Returns:
            執行結果
        """
        start_time = time.time()

        try:
            # 速率限制檢查
            if user_id and not self.rate_limiter.is_allowed(user_id):
                raise Exception("速率限制：請求過於頻繁")

            # 生成快取鍵
            cache_key = None
            if self.cache:
                cache_key = self._generate_cache_key(entity_id, action, params)
                cached_result = self.cache.get(cache_key)

                if cached_result:
                    if self.metrics:
                        self.metrics.record_cache_hit()
                    logger.debug(f"使用快取結果: {action}")
                    return cached_result

                if self.metrics:
                    self.metrics.record_cache_miss()

            # 執行動作
            logger.info(f"執行動作: {action} (實體: {entity_id})")

            entity = self.client.get_entity(id=entity_id)
            result = entity.execute(action=action, params=params)

            # 快取結果
            if self.cache and cache_key:
                self.cache.set(cache_key, result)

            # 記錄成功
            latency = time.time() - start_time
            if self.metrics:
                self.metrics.record_request(success=True, latency=latency)

            logger.info(f"動作執行成功: {action} (耗時: {latency:.2f}s)")

            return {
                "success": True,
                "data": result,
                "latency": latency
            }

        except Exception as e:
            # 記錄失敗
            latency = time.time() - start_time
            if self.metrics:
                self.metrics.record_request(success=False, latency=latency)

            logger.error(f"動作執行失敗: {action} - {e}")

            return self.error_handler.handle_composio_error(e)

    def get_metrics(self) -> Dict[str, Any]:
        """獲取性能指標"""
        if not self.metrics:
            return {}

        return self.metrics.get_metrics()

    def health_check(self) -> Dict[str, Any]:
        """
        健康檢查

        Returns:
            健康狀態
        """
        try:
            # 測試 API 連接
            _ = self.client.apps.get()

            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "environment": self.config.environment
            }

        except Exception as e:
            logger.error(f"健康檢查失敗: {e}")

            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _generate_cache_key(self, entity_id: str, action: str,
                          params: Dict[str, Any]) -> str:
        """
        生成快取鍵

        Args:
            entity_id: 實體 ID
            action: 動作名稱
            params: 參數

        Returns:
            快取鍵
        """
        key_data = f"{entity_id}:{action}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()


# ============================================================================
# 部署指南和最佳實踐
# ============================================================================

def print_deployment_guide():
    """
    印出部署指南
    """
    print("\n" + "=" * 80)
    print("生產部署指南")
    print("=" * 80)

    guide = [
        ("1. 環境準備", [
            "設置環境變數（COMPOSIO_API_KEY 等）",
            "配置日誌系統",
            "設置監控和告警",
            "準備數據庫（如需要）"
        ]),
        ("2. 安全配置", [
            "使用 HTTPS",
            "啟用 SSL 驗證",
            "實施 API 金鑰輪換",
            "設置防火牆規則",
            "使用密鑰管理服務"
        ]),
        ("3. 性能優化", [
            "啟用快取",
            "配置連接池",
            "使用 CDN",
            "實施負載均衡",
            "優化數據庫查詢"
        ]),
        ("4. 可靠性", [
            "實施重試邏輯",
            "設置超時時間",
            "健康檢查端點",
            "優雅關閉",
            "災難恢復計劃"
        ]),
        ("5. 監控", [
            "收集性能指標",
            "設置告警規則",
            "日誌聚合",
            "追蹤錯誤率",
            "監控資源使用"
        ]),
        ("6. 擴展性", [
            "水平擴展設計",
            "無狀態架構",
            "使用訊息佇列",
            "實施快取層",
            "數據庫分片"
        ])
    ]

    for title, items in guide:
        print(f"\n{title}")
        print("-" * 80)
        for item in items:
            print(f"  • {item}")


def print_architecture():
    """
    印出推薦架構
    """
    print("\n" + "=" * 80)
    print("推薦的生產架構")
    print("=" * 80)

    print("""
┌─────────────────────────────────────────────────────────────┐
│                        負載均衡器                            │
│                     (Nginx / ALB)                           │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
┌─────────────▼─────────┐         ┌──────────▼──────────┐
│   應用伺服器 1         │         │   應用伺服器 2       │
│  (Composio Client)    │         │  (Composio Client)  │
└─────────────┬─────────┘         └──────────┬──────────┘
              │                               │
              └───────────────┬───────────────┘
                              │
              ┌───────────────▼───────────────┐
              │                               │
    ┌─────────▼─────────┐         ┌──────────▼──────────┐
    │   Redis 快取       │         │   PostgreSQL        │
    │   (Session/Cache)  │         │   (數據持久化)      │
    └───────────────────┘         └─────────────────────┘

外部服務：
  • Composio API
  • OpenAI API
  • GitHub / Slack / 其他整合

監控系統：
  • Prometheus (指標)
  • Grafana (視覺化)
  • ELK Stack (日誌)
  • Sentry (錯誤追蹤)
    """)


def main():
    """
    主函數
    """
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║              Composio 生產部署範例                               ║
    ║                                                                  ║
    ║              企業級 AI Agent 應用部署指南                        ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)

    # 印出部署指南
    print_deployment_guide()

    # 印出架構
    print_architecture()

    # 演示生產客戶端
    print("\n" + "=" * 80)
    print("生產客戶端使用範例")
    print("=" * 80)

    print("""
# 載入配置
config = ProductionConfig.from_env()

# 創建客戶端
client = ProductionComposioClient(config)

# 執行動作
result = client.execute_action(
    entity_id="user_123",
    action="GITHUB_LIST_REPOS",
    params={},
    user_id="user_123"
)

# 檢查健康狀態
health = client.health_check()

# 獲取指標
metrics = client.get_metrics()
    """)

    print("\n" + "=" * 80)
    print("環境變數配置範例")
    print("=" * 80)

    print("""
# .env 文件
COMPOSIO_API_KEY=your-api-key
OPENAI_API_KEY=your-openai-key
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
LOG_FILE=/var/log/composio-app.log
MAX_RETRIES=3
TIMEOUT=30
RATE_LIMIT=100
CACHE_ENABLED=true
CACHE_TTL=300
    """)

    print("\n" + "=" * 80)
    print("Docker 部署範例")
    print("=" * 80)

    print("""
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "app.py"]

# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - COMPOSIO_API_KEY=${COMPOSIO_API_KEY}
      - ENVIRONMENT=production
    restart: always

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    """)

    print("\n" + "=" * 80)
    print("下一步:")
    print("  1. 設置環境變數")
    print("  2. 配置監控系統")
    print("  3. 實施 CI/CD 流程")
    print("  4. 進行負載測試")
    print("  5. 準備上線檢查清單")
    print("=" * 80)


if __name__ == "__main__":
    main()

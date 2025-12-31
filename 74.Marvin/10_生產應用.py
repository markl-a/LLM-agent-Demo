"""
Marvin 生產應用示例

本示例展示：
1. 錯誤處理和重試
2. 日誌記錄
3. 性能監控
4. 緩存策略
5. 部署最佳實踐

運行方式：
    python 10_生產應用.py
"""

import os
import logging
import time
from functools import wraps
from typing import Optional, Any
import marvin
from pydantic import BaseModel


# ==================== 日誌配置 ====================

def setup_logging():
    """配置日誌系統"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('marvin_app.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


logger = setup_logging()


# ==================== 錯誤處理和重試 ====================

def retry_on_error(max_retries=3, delay=1):
    """重試裝飾器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries):
                try:
                    logger.info(f"嘗試 {attempt + 1}/{max_retries}: {func.__name__}")
                    result = await func(*args, **kwargs)
                    logger.info(f"成功: {func.__name__}")
                    return result

                except Exception as e:
                    last_exception = e
                    logger.warning(
                        f"失敗 (嘗試 {attempt + 1}/{max_retries}): {str(e)}"
                    )

                    if attempt < max_retries - 1:
                        wait_time = delay * (2 ** attempt)  # 指數退避
                        logger.info(f"等待 {wait_time} 秒後重試...")
                        time.sleep(wait_time)

            logger.error(f"所有重試都失敗: {func.__name__}")
            raise last_exception

        return wrapper
    return decorator


def example_error_handling():
    """示例 1: 錯誤處理和重試"""
    print("\n" + "="*60)
    print("示例 1: 錯誤處理和重試")
    print("="*60)

    try:
        print("錯誤處理示例:\n")

        @retry_on_error(max_retries=3, delay=1)
        @marvin.fn
        async def robust_function(text: str) -> str:
            """帶重試機制的健壯函數"""
            return "處理結果"

        print("示例代碼:")
        print("""
        import asyncio
        from tenacity import retry, stop_after_attempt, wait_exponential

        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=1, max=10)
        )
        @marvin.fn
        async def api_call(data: str) -> str:
            '''帶智能重試的 API 調用'''

        try:
            result = await api_call("data")
            logger.info(f"成功: {result}")
        except Exception as e:
            logger.error(f"失敗: {e}")
            # 實施降級策略
            result = fallback_function(data)
        """)

        print("\n錯誤處理策略:")
        print("  🔄 自動重試")
        print("  ⏰ 指數退避")
        print("  📝 詳細日誌")
        print("  🛡️ 降級方案")
        print("  ⚠️ 錯誤監控\n")

    except Exception as e:
        logger.error(f"示例錯誤: {e}")


# ==================== 性能監控 ====================

class PerformanceMonitor:
    """性能監控器"""

    def __init__(self):
        self.metrics = []

    def track(self, func):
        """追蹤函數性能"""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            start_mem = 0  # 簡化，實際應使用 psutil

            try:
                result = await func(*args, **kwargs)
                success = True
                error = None
            except Exception as e:
                success = False
                error = str(e)
                raise
            finally:
                duration = time.time() - start_time

                metric = {
                    'function': func.__name__,
                    'duration': duration,
                    'success': success,
                    'error': error,
                    'timestamp': time.time()
                }
                self.metrics.append(metric)

                logger.info(
                    f"性能: {func.__name__} - "
                    f"{duration:.2f}s - "
                    f"{'成功' if success else '失敗'}"
                )

            return result
        return wrapper

    def get_stats(self):
        """獲取統計信息"""
        if not self.metrics:
            return {}

        durations = [m['duration'] for m in self.metrics]
        success_count = sum(1 for m in self.metrics if m['success'])

        return {
            'total_calls': len(self.metrics),
            'success_rate': success_count / len(self.metrics),
            'avg_duration': sum(durations) / len(durations),
            'min_duration': min(durations),
            'max_duration': max(durations)
        }


monitor = PerformanceMonitor()


def example_monitoring():
    """示例 2: 性能監控"""
    print("\n" + "="*60)
    print("示例 2: 性能監控")
    print("="*60)

    print("性能監控示例:\n")

    print("示例代碼:")
    print("""
    from prometheus_client import Counter, Histogram
    import time

    # Prometheus 指標
    request_counter = Counter('marvin_requests_total', 'Total requests')
    request_duration = Histogram('marvin_request_duration_seconds', 'Request duration')

    @marvin.fn
    async def monitored_function(text: str) -> str:
        '''被監控的函數'''
        request_counter.inc()

        start = time.time()
        try:
            result = await original_function(text)
            return result
        finally:
            duration = time.time() - start
            request_duration.observe(duration)

    # 定期報告
    def report_metrics():
        stats = monitor.get_stats()
        logger.info(f"統計: {stats}")

        # 發送到監控系統
        send_to_datadog(stats)
        send_to_cloudwatch(stats)
    """)

    print("\n監控指標:")
    print("  ⏱️ 響應時間")
    print("  📊 成功率")
    print("  🔢 調用次數")
    print("  💾 內存使用")
    print("  🌐 API 調用成本")
    print("  ⚠️ 錯誤率\n")


# ==================== 緩存策略 ====================

class CacheManager:
    """緩存管理器"""

    def __init__(self, ttl=3600):
        self.cache = {}
        self.ttl = ttl

    def get(self, key: str) -> Optional[Any]:
        """獲取緩存"""
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                logger.info(f"緩存命中: {key}")
                return value
            else:
                logger.info(f"緩存過期: {key}")
                del self.cache[key]
        return None

    def set(self, key: str, value: Any):
        """設置緩存"""
        self.cache[key] = (value, time.time())
        logger.info(f"緩存設置: {key}")

    def clear(self):
        """清除所有緩存"""
        self.cache.clear()
        logger.info("緩存已清除")


cache = CacheManager(ttl=3600)


def example_caching():
    """示例 3: 緩存策略"""
    print("\n" + "="*60)
    print("示例 3: 緩存策略")
    print("="*60)

    print("緩存策略示例:\n")

    print("示例代碼:")
    print("""
    import hashlib
    import redis

    # Redis 緩存
    redis_client = redis.Redis(host='localhost', port=6379, db=0)

    def cache_key(func_name: str, *args, **kwargs) -> str:
        '''生成緩存鍵'''
        key_data = f"{func_name}:{args}:{kwargs}"
        return hashlib.md5(key_data.encode()).hexdigest()

    @marvin.fn
    async def cached_function(text: str) -> str:
        '''帶緩存的函數'''
        key = cache_key('cached_function', text)

        # 嘗試從緩存獲取
        cached = redis_client.get(key)
        if cached:
            logger.info(f"緩存命中: {key}")
            return cached.decode()

        # 執行函數
        result = await original_function(text)

        # 存入緩存
        redis_client.setex(key, 3600, result)  # 1小時過期
        logger.info(f"緩存設置: {key}")

        return result

    # 使用 functools.lru_cache
    from functools import lru_cache

    @lru_cache(maxsize=128)
    def memory_cache(text: str) -> str:
        '''內存緩存'''
        return expensive_operation(text)
    """)

    print("\n緩存策略:")
    print("  💾 內存緩存（快速）")
    print("  🗄️ Redis 緩存（分布式）")
    print("  ⏰ TTL 過期策略")
    print("  🔑 智能鍵生成")
    print("  🔄 緩存失效策略\n")


# ==================== 配置管理 ====================

class Config:
    """生產環境配置"""

    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("MARVIN_MODEL", "gpt-3.5-turbo")
        self.temperature = float(os.getenv("MARVIN_TEMPERATURE", "0.7"))
        self.max_retries = int(os.getenv("MARVIN_MAX_RETRIES", "3"))
        self.timeout = int(os.getenv("MARVIN_TIMEOUT", "30"))
        self.cache_ttl = int(os.getenv("CACHE_TTL", "3600"))
        self.log_level = os.getenv("LOG_LEVEL", "INFO")

    def validate(self):
        """驗證配置"""
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY 未設置")

        if self.temperature < 0 or self.temperature > 2:
            raise ValueError("temperature 必須在 0-2 之間")

        logger.info("配置驗證通過")


def example_configuration():
    """示例 4: 配置管理"""
    print("\n" + "="*60)
    print("示例 4: 配置管理")
    print("="*60)

    print("配置管理示例:\n")

    print("示例代碼:")
    print("""
    # config.py
    from pydantic import BaseSettings

    class Settings(BaseSettings):
        openai_api_key: str
        model: str = "gpt-3.5-turbo"
        temperature: float = 0.7
        max_retries: int = 3
        cache_enabled: bool = True

        class Config:
            env_file = ".env"
            env_file_encoding = "utf-8"

    settings = Settings()

    # 在應用中使用
    marvin.settings.openai.api_key = settings.openai_api_key
    marvin.settings.llm_model = settings.model
    marvin.settings.llm_temperature = settings.temperature

    # 環境特定配置
    if os.getenv("ENVIRONMENT") == "production":
        # 生產環境配置
        marvin.settings.log_level = "WARNING"
        marvin.settings.cache_enabled = True
    else:
        # 開發環境配置
        marvin.settings.log_level = "DEBUG"
        marvin.settings.cache_enabled = False
    """)

    print("\n配置最佳實踐:")
    print("  🔐 使用環境變量")
    print("  📝 配置驗證")
    print("  🌍 環境特定配置")
    print("  🔒 敏感信息保護")
    print("  📋 配置文檔化\n")


# ==================== 部署示例 ====================

def example_deployment():
    """示例 5: 部署最佳實踐"""
    print("\n" + "="*60)
    print("示例 5: 部署最佳實踐")
    print("="*60)

    print("部署示例:\n")

    print("1. Docker 部署:")
    print("""
    # Dockerfile
    FROM python:3.11-slim

    WORKDIR /app

    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt

    COPY . .

    ENV OPENAI_API_KEY=''
    ENV MARVIN_MODEL='gpt-3.5-turbo'

    CMD ["python", "app.py"]
    """)

    print("\n2. Kubernetes 部署:")
    print("""
    # deployment.yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: marvin-app
    spec:
      replicas: 3
      template:
        spec:
          containers:
          - name: app
            image: marvin-app:latest
            env:
            - name: OPENAI_API_KEY
              valueFrom:
                secretKeyRef:
                  name: api-secrets
                  key: openai-key
    """)

    print("\n3. 健康檢查:")
    print("""
    from fastapi import FastAPI

    app = FastAPI()

    @app.get("/health")
    async def health_check():
        # 檢查依賴服務
        try:
            # 測試 Marvin
            result = await test_marvin_function()
            return {"status": "healthy", "marvin": "ok"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    """)

    print("\n部署檢查清單:")
    print("  ✅ 環境變量配置")
    print("  ✅ 密鑰管理")
    print("  ✅ 日誌收集")
    print("  ✅ 監控告警")
    print("  ✅ 健康檢查")
    print("  ✅ 自動擴展")
    print("  ✅ 備份恢復\n")


# ==================== 生產應用示例 ====================

class ProductionApp:
    """生產級應用示例"""

    def __init__(self, config: Config):
        self.config = config
        self.monitor = PerformanceMonitor()
        self.cache = CacheManager(ttl=config.cache_ttl)

        # 配置 Marvin
        marvin.settings.openai.api_key = config.openai_api_key
        marvin.settings.llm_model = config.model
        marvin.settings.llm_temperature = config.temperature

    @retry_on_error(max_retries=3)
    async def process(self, data: str) -> dict:
        """處理數據"""
        # 檢查緩存
        cache_key = f"process:{data}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        # 執行處理
        start = time.time()

        @marvin.fn
        async def analyze(text: str) -> str:
            """分析文本"""

        result = await analyze(data)

        # 記錄性能
        duration = time.time() - start
        logger.info(f"處理完成: {duration:.2f}s")

        # 緩存結果
        self.cache.set(cache_key, result)

        return {
            "result": result,
            "duration": duration,
            "cached": False
        }


def example_production_app():
    """示例 6: 完整生產應用"""
    print("\n" + "="*60)
    print("示例 6: 完整生產應用")
    print("="*60)

    print("生產級應用架構:\n")

    print("目錄結構:")
    print("""
    marvin_app/
    ├── app/
    │   ├── __init__.py
    │   ├── main.py          # 應用入口
    │   ├── config.py        # 配置管理
    │   ├── models.py        # 數據模型
    │   ├── services.py      # Marvin 服務
    │   └── utils.py         # 工具函數
    ├── tests/
    │   ├── test_services.py
    │   └── test_utils.py
    ├── .env                 # 環境變量
    ├── requirements.txt
    ├── Dockerfile
    └── docker-compose.yml
    """)

    print("\n核心組件:")
    print("  🎯 API 服務層")
    print("  🧠 Marvin 處理層")
    print("  💾 緩存層")
    print("  📝 日誌系統")
    print("  📊 監控系統")
    print("  🔄 隊列系統")
    print("  🛡️ 錯誤處理\n")


# ==================== 主函數 ====================

def main():
    """主函數"""
    print("""
╔══════════════════════════════════════════╗
║      Marvin 生產應用最佳實踐              ║
╚══════════════════════════════════════════╝

生產級特性:
✅ 錯誤處理和重試
✅ 性能監控
✅ 緩存策略
✅ 配置管理
✅ 日誌系統
✅ 部署方案
    """)

    # 運行示例
    example_error_handling()
    example_monitoring()
    example_caching()
    example_configuration()
    example_deployment()
    example_production_app()

    print("\n" + "="*60)
    print("✅ 所有示例演示完成！")
    print("="*60)
    print("\n💡 生產部署提示:")
    print("   1. 充分測試")
    print("   2. 監控告警")
    print("   3. 日誌收集")
    print("   4. 錯誤追蹤")
    print("   5. 性能優化")
    print("   6. 安全加固")


if __name__ == "__main__":
    main()

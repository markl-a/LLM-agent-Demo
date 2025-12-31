"""
Guardrails AI - 生產部署示例
展示生產環境中的完整配置、監控和最佳實踐
"""

import os
import time
import json
import logging
from typing import Dict, Any, List
from datetime import datetime
from guardrails import Guard
from guardrails.hub import ValidLength, DetectPII, ToxicLanguage
from pydantic import BaseModel, Field
import openai

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('guardrails_production.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")


class ProductionGuard:
    """
    生產級 Guard 封裝
    """

    def __init__(self, name: str):
        self.name = name
        self.metrics = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "total_latency": 0.0,
            "validation_failures": 0
        }
        logger.info(f"Initialized ProductionGuard: {name}")

    def record_call(self, success: bool, latency: float, validation_passed: bool):
        """記錄調用指標"""
        self.metrics["total_calls"] += 1
        self.metrics["total_latency"] += latency

        if success:
            self.metrics["successful_calls"] += 1
        else:
            self.metrics["failed_calls"] += 1

        if not validation_passed:
            self.metrics["validation_failures"] += 1

    def get_metrics(self) -> Dict[str, Any]:
        """獲取指標"""
        avg_latency = (
            self.metrics["total_latency"] / self.metrics["total_calls"]
            if self.metrics["total_calls"] > 0 else 0
        )

        return {
            **self.metrics,
            "average_latency": avg_latency,
            "success_rate": (
                self.metrics["successful_calls"] / self.metrics["total_calls"]
                if self.metrics["total_calls"] > 0 else 0
            )
        }


def production_configuration():
    """
    生產環境配置示例
    """
    print("=" * 60)
    print("生產環境配置示例")
    print("=" * 60)

    # 創建生產級 Guard
    class ProductResponse(BaseModel):
        """產品響應模型"""
        content: str = Field(min_length=10, max_length=500)
        category: str
        confidence: float = Field(ge=0, le=1)

    guard = Guard.from_pydantic(
        output_class=ProductResponse,
        prompt="生成產品相關回應"
    )

    # 添加多層驗證
    guard = guard.use_many(
        ValidLength(min=10, max=500, on_fail="reask"),
        DetectPII(pii_entities=["EMAIL_ADDRESS", "PHONE_NUMBER"], on_fail="filter"),
        ToxicLanguage(threshold=0.3, on_fail="exception")
    )

    prod_guard = ProductionGuard("product_response")

    prompt = "生成一個關於產品特性的回應"

    print(f"\n提示: {prompt}")

    start_time = time.time()
    success = False
    validation_passed = False

    try:
        result = guard(
            llm_api=openai.chat.completions.create,
            prompt=prompt,
            model="gpt-3.5-turbo",
            max_tokens=300,
            num_reasks=2
        )

        latency = time.time() - start_time
        success = True
        validation_passed = result.validation_passed if hasattr(result, 'validation_passed') else True

        print(f"\n✅ 生產調用成功")
        print(f"延遲: {latency:.3f} 秒")
        print(f"輸出: {result.validated_output}")

        logger.info(f"Successful guard call - latency: {latency:.3f}s")

    except Exception as e:
        latency = time.time() - start_time
        print(f"\n❌ 調用失敗: {str(e)}")
        logger.error(f"Guard call failed: {str(e)}")

    finally:
        prod_guard.record_call(success, latency, validation_passed)

    # 顯示指標
    metrics = prod_guard.get_metrics()
    print(f"\n📊 指標:")
    print(f"  總調用數: {metrics['total_calls']}")
    print(f"  成功率: {metrics['success_rate']:.2%}")
    print(f"  平均延遲: {metrics['average_latency']:.3f}s")


def error_handling_strategy():
    """
    錯誤處理策略
    """
    print("\n" + "=" * 60)
    print("錯誤處理策略示例")
    print("=" * 60)

    class ErrorHandler:
        """錯誤處理器"""

        @staticmethod
        def handle_validation_error(error: Exception, context: Dict):
            """處理驗證錯誤"""
            logger.error(f"Validation error: {str(error)}, context: {context}")

            return {
                "status": "error",
                "error_type": "validation",
                "message": str(error),
                "timestamp": datetime.now().isoformat()
            }

        @staticmethod
        def handle_api_error(error: Exception, context: Dict):
            """處理 API 錯誤"""
            logger.error(f"API error: {str(error)}, context: {context}")

            return {
                "status": "error",
                "error_type": "api",
                "message": str(error),
                "timestamp": datetime.now().isoformat()
            }

        @staticmethod
        def handle_timeout(context: Dict):
            """處理超時"""
            logger.warning(f"Timeout occurred, context: {context}")

            return {
                "status": "error",
                "error_type": "timeout",
                "message": "Request timed out",
                "timestamp": datetime.now().isoformat()
            }

    handler = ErrorHandler()
    guard = Guard().use(ValidLength(min=50, max=100, on_fail="exception"))

    prompt = "生成一個簡短的句子"
    context = {"prompt": prompt, "user_id": "test_user"}

    try:
        result = guard(
            llm_api=openai.chat.completions.create,
            prompt=prompt,
            model="gpt-3.5-turbo",
            max_tokens=50,
        )

        print(f"✅ 成功: {result.validated_output}")

    except Exception as e:
        error_response = handler.handle_validation_error(e, context)
        print(f"\n❌ 錯誤處理:")
        print(json.dumps(error_response, indent=2, ensure_ascii=False))


def rate_limiting():
    """
    速率限制
    """
    print("\n" + "=" * 60)
    print("速率限制示例")
    print("=" * 60)

    class RateLimiter:
        """速率限制器"""

        def __init__(self, max_requests: int, time_window: int):
            self.max_requests = max_requests
            self.time_window = time_window
            self.requests: List[float] = []

        def is_allowed(self) -> bool:
            """檢查是否允許請求"""
            now = time.time()

            # 清理過期的請求記錄
            self.requests = [
                req_time for req_time in self.requests
                if now - req_time < self.time_window
            ]

            # 檢查是否超過限制
            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return True
            else:
                return False

        def get_wait_time(self) -> float:
            """獲取需要等待的時間"""
            if not self.requests:
                return 0

            oldest_request = min(self.requests)
            wait_time = self.time_window - (time.time() - oldest_request)
            return max(0, wait_time)

    # 每 10 秒最多 3 個請求
    limiter = RateLimiter(max_requests=3, time_window=10)

    print("\n速率限制: 每 10 秒最多 3 個請求")

    for i in range(5):
        if limiter.is_allowed():
            print(f"✅ 請求 {i + 1} 被允許")
        else:
            wait_time = limiter.get_wait_time()
            print(f"⚠️  請求 {i + 1} 被限制，需等待 {wait_time:.1f} 秒")


def caching_strategy():
    """
    緩存策略
    """
    print("\n" + "=" * 60)
    print("緩存策略示例")
    print("=" * 60)

    class ResponseCache:
        """響應緩存"""

        def __init__(self, ttl: int = 300):
            self.cache: Dict[str, Dict] = {}
            self.ttl = ttl

        def get(self, key: str) -> Any:
            """獲取緩存"""
            if key in self.cache:
                entry = self.cache[key]
                if time.time() - entry['timestamp'] < self.ttl:
                    logger.info(f"Cache hit for key: {key}")
                    return entry['value']
                else:
                    # 過期，刪除
                    del self.cache[key]

            logger.info(f"Cache miss for key: {key}")
            return None

        def set(self, key: str, value: Any):
            """設置緩存"""
            self.cache[key] = {
                'value': value,
                'timestamp': time.time()
            }
            logger.info(f"Cached value for key: {key}")

        def clear(self):
            """清空緩存"""
            self.cache.clear()
            logger.info("Cache cleared")

    cache = ResponseCache(ttl=60)

    # 模擬緩存使用
    cache_key = "test_prompt_response"

    # 第一次請求（緩存未命中）
    cached_response = cache.get(cache_key)
    if cached_response is None:
        print("🔍 緩存未命中，調用 API...")
        response = "這是一個模擬的 API 響應"
        cache.set(cache_key, response)
    else:
        print("✅ 使用緩存響應")
        response = cached_response

    print(f"響應: {response}")

    # 第二次請求（緩存命中）
    cached_response = cache.get(cache_key)
    if cached_response is not None:
        print("\n✅ 緩存命中！")
        print(f"響應: {cached_response}")


def monitoring_and_alerting():
    """
    監控和告警
    """
    print("\n" + "=" * 60)
    print("監控和告警示例")
    print("=" * 60)

    class MonitoringSystem:
        """監控系統"""

        def __init__(self):
            self.thresholds = {
                "error_rate": 0.05,  # 5%
                "avg_latency": 2.0,  # 2 秒
                "validation_failure_rate": 0.1  # 10%
            }

        def check_metrics(self, metrics: Dict) -> List[str]:
            """檢查指標並生成告警"""
            alerts = []

            # 檢查錯誤率
            error_rate = 1 - metrics.get('success_rate', 1)
            if error_rate > self.thresholds['error_rate']:
                alerts.append(
                    f"⚠️  高錯誤率: {error_rate:.2%} (閾值: {self.thresholds['error_rate']:.2%})"
                )

            # 檢查平均延遲
            avg_latency = metrics.get('average_latency', 0)
            if avg_latency > self.thresholds['avg_latency']:
                alerts.append(
                    f"⚠️  高延遲: {avg_latency:.3f}s (閾值: {self.thresholds['avg_latency']}s)"
                )

            # 檢查驗證失敗率
            validation_failure_rate = (
                metrics.get('validation_failures', 0) / metrics.get('total_calls', 1)
            )
            if validation_failure_rate > self.thresholds['validation_failure_rate']:
                alerts.append(
                    f"⚠️  高驗證失敗率: {validation_failure_rate:.2%} (閾值: {self.thresholds['validation_failure_rate']:.2%})"
                )

            return alerts

    monitoring = MonitoringSystem()

    # 模擬指標
    test_metrics = {
        "total_calls": 100,
        "successful_calls": 92,
        "failed_calls": 8,
        "average_latency": 1.5,
        "validation_failures": 15,
        "success_rate": 0.92
    }

    print("\n📊 檢查指標:")
    alerts = monitoring.check_metrics(test_metrics)

    if alerts:
        print("\n告警:")
        for alert in alerts:
            print(f"  {alert}")
            logger.warning(alert)
    else:
        print("✅ 所有指標正常")


def circuit_breaker():
    """
    斷路器模式
    """
    print("\n" + "=" * 60)
    print("斷路器模式示例")
    print("=" * 60)

    class CircuitBreaker:
        """斷路器"""

        def __init__(self, failure_threshold: int = 5, timeout: int = 60):
            self.failure_threshold = failure_threshold
            self.timeout = timeout
            self.failure_count = 0
            self.last_failure_time = None
            self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

        def call(self, func, *args, **kwargs):
            """通過斷路器調用函數"""
            if self.state == "OPEN":
                # 檢查是否可以進入半開狀態
                if time.time() - self.last_failure_time > self.timeout:
                    self.state = "HALF_OPEN"
                    logger.info("Circuit breaker entering HALF_OPEN state")
                else:
                    raise Exception("Circuit breaker is OPEN")

            try:
                result = func(*args, **kwargs)

                # 成功，重置計數器
                if self.state == "HALF_OPEN":
                    self.state = "CLOSED"
                    logger.info("Circuit breaker returned to CLOSED state")

                self.failure_count = 0
                return result

            except Exception as e:
                self.failure_count += 1
                self.last_failure_time = time.time()

                if self.failure_count >= self.failure_threshold:
                    self.state = "OPEN"
                    logger.warning("Circuit breaker switched to OPEN state")

                raise e

        def get_state(self) -> str:
            """獲取斷路器狀態"""
            return self.state

    breaker = CircuitBreaker(failure_threshold=3, timeout=10)

    def mock_api_call():
        """模擬 API 調用"""
        # 這裡可以替換為實際的 Guard 調用
        import random
        if random.random() < 0.3:  # 30% 失敗率
            raise Exception("API call failed")
        return "Success"

    print("\n執行多次調用...")
    for i in range(10):
        try:
            result = breaker.call(mock_api_call)
            print(f"調用 {i + 1}: ✅ {result} (狀態: {breaker.get_state()})")
        except Exception as e:
            print(f"調用 {i + 1}: ❌ {str(e)} (狀態: {breaker.get_state()})")

        time.sleep(0.1)


def production_best_practices():
    """
    生產環境最佳實踐總結
    """
    print("\n" + "=" * 60)
    print("生產環境最佳實踐")
    print("=" * 60)

    best_practices = [
        "1. 多層驗證：使用多個驗證器組合確保輸出質量",
        "2. 錯誤處理：實現完善的錯誤處理和降級策略",
        "3. 速率限制：防止 API 過度使用和成本超支",
        "4. 緩存：對相似請求使用緩存減少延遲和成本",
        "5. 監控告警：實時監控關鍵指標並設置告警",
        "6. 日誌記錄：詳細記錄所有調用和錯誤",
        "7. 斷路器：使用斷路器模式防止級聯故障",
        "8. 重試策略：合理配置重試次數避免浪費",
        "9. 超時設置：為所有請求設置合理的超時時間",
        "10. 版本管理：對 Guard 配置進行版本控制"
    ]

    print("\n最佳實踐清單:")
    for practice in best_practices:
        print(f"  ✓ {practice}")

    print("\n" + "=" * 60)


def main():
    """
    主函數：運行所有生產部署示例
    """
    print("\n🛡️  Guardrails AI - 生產部署")
    print("=" * 60)

    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  警告: 未設置 OPENAI_API_KEY 環境變量")
        return

    # 運行各種生產部署示例
    production_configuration()
    error_handling_strategy()
    rate_limiting()
    caching_strategy()
    monitoring_and_alerting()
    circuit_breaker()
    production_best_practices()

    print("\n" + "=" * 60)
    print("✅ 所有生產部署示例執行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()

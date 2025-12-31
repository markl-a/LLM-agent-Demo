"""
NeMo Guardrails - 企業部署示例
展示生產環境的完整配置和最佳實踐
"""

import os
import logging
import time
from datetime import datetime
from typing import Dict, Any
from nemoguardrails import RailsConfig, LLMRails
from nemoguardrails.actions import action

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nemo_guardrails_production.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")


def production_configuration():
    """
    生產環境完整配置
    """
    print("=" * 60)
    print("生產環境配置示例")
    print("=" * 60)

    config_yaml = """
    models:
      - type: main
        engine: openai
        model: gpt-3.5-turbo
        parameters:
          temperature: 0.7
          max_tokens: 500

    instructions:
      - type: general
        content: |
          You are a professional programming assistant.
          - Provide accurate, helpful information
          - Be concise and clear
          - Always verify facts
          - Maintain professional tone

    rails:
      input:
        flows:
          - check jailbreak
          - detect sensitive info
          - validate input

      output:
        flows:
          - self check output
          - check toxicity
          - verify facts

      dialog:
        flows:
          - maintain context
          - handle errors
    """

    colang_content = """
    # 輸入護欄
    define user attempt jailbreak
      "ignore instructions"
      "bypass rules"

    define bot refuse jailbreak
      "I cannot process that request."

    define flow check jailbreak
      user attempt jailbreak
      bot refuse jailbreak
      stop

    # 輸出護欄
    define flow self check output
      bot ...
      $allowed = execute self_check_output
      if not $allowed
        bot provide safe response
        stop

    define bot provide safe response
      "I apologize, but I need to rephrase my response."

    # 對話流程
    define flow maintain context
      user ...
      bot ...
    """

    try:
        config = RailsConfig.from_content(
            config=config_yaml,
            colang_content=colang_content
        )

        rails = LLMRails(config)

        test_input = "Explain Python best practices"

        print("\n測試生產配置:")
        print("-" * 60)

        start_time = time.time()

        print(f"\n👤 用戶: {test_input}")

        response = rails.generate(messages=[{
            "role": "user",
            "content": test_input
        }])

        latency = time.time() - start_time

        print(f"🤖 助手: {response['content']}")
        print(f"\n⏱️  延遲: {latency:.3f} 秒")

        logger.info(f"Production request completed - latency: {latency:.3f}s")

        print("\n" + "-" * 60)
        print("✅ 生產配置測試完成")

    except Exception as e:
        logger.error(f"Production error: {str(e)}")
        print(f"❌ 錯誤: {str(e)}")


def monitoring_and_logging():
    """
    監控和日誌記錄
    """
    print("\n" + "=" * 60)
    print("監控和日誌記錄示例")
    print("=" * 60)

    @action(name="log_interaction")
    async def log_interaction(context: dict):
        """記錄交互日誌"""
        user_message = context.get("user_message", "")
        timestamp = datetime.now().isoformat()

        log_entry = {
            "timestamp": timestamp,
            "user_message": user_message[:100],  # 限制長度
            "session_id": context.get("session_id", "unknown")
        }

        logger.info(f"Interaction logged: {log_entry}")
        return True

    config_yaml = """
    models:
      - type: main
        engine: openai
        model: gpt-3.5-turbo

    rails:
      dialog:
        flows:
          - log all interactions
    """

    colang_content = """
    define flow log all interactions
      user ...
      execute log_interaction
      bot ...
    """

    try:
        config = RailsConfig.from_content(
            config=config_yaml,
            colang_content=colang_content
        )

        rails = LLMRails(config)
        rails.register_action(log_interaction)

        test_inputs = [
            "What is Python?",
            "How do I learn it?",
            "Show me an example"
        ]

        print("\n測試監控和日誌:")
        print("-" * 60)

        for user_input in test_inputs:
            print(f"\n👤 用戶: {user_input}")

            response = rails.generate(messages=[{
                "role": "user",
                "content": user_input
            }])

            print(f"🤖 助手: {response['content']}")

        print("\n" + "-" * 60)
        print("✅ 監控測試完成")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def rate_limiting():
    """
    速率限制
    """
    print("\n" + "=" * 60)
    print("速率限制示例")
    print("=" * 60)

    class RateLimiter:
        def __init__(self, max_requests: int, time_window: int):
            self.max_requests = max_requests
            self.time_window = time_window
            self.requests = []

        def is_allowed(self) -> bool:
            now = time.time()
            self.requests = [t for t in self.requests if now - t < self.time_window]

            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return True

            return False

    limiter = RateLimiter(max_requests=3, time_window=5)

    config_yaml = """
    models:
      - type: main
        engine: openai
        model: gpt-3.5-turbo
    """

    colang_content = """
    define flow
      user ...
      bot ...
    """

    try:
        config = RailsConfig.from_content(
            config=config_yaml,
            colang_content=colang_content
        )

        rails = LLMRails(config)

        print("\n測試速率限制 (5秒內最多3個請求):")
        print("-" * 60)

        for i in range(5):
            if limiter.is_allowed():
                print(f"\n✅ 請求 {i+1} 被允許")

                response = rails.generate(messages=[{
                    "role": "user",
                    "content": "Quick question"
                }])

            else:
                print(f"\n⚠️  請求 {i+1} 被限流")

        print("\n" + "-" * 60)
        print("✅ 速率限制測試完成")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def error_handling():
    """
    錯誤處理
    """
    print("\n" + "=" * 60)
    print("錯誤處理示例")
    print("=" * 60)

    @action(name="handle_error")
    async def handle_error(context: dict):
        """處理錯誤"""
        error_type = context.get("error_type", "unknown")

        error_responses = {
            "rate_limit": "Service is busy. Please try again later.",
            "timeout": "Request timed out. Please try a simpler question.",
            "invalid_input": "I couldn't understand that. Please rephrase.",
            "unknown": "An error occurred. Please try again."
        }

        logger.error(f"Error handled: {error_type}")
        return error_responses.get(error_type, error_responses["unknown"])

    config_yaml = """
    models:
      - type: main
        engine: openai
        model: gpt-3.5-turbo

    rails:
      dialog:
        flows:
          - handle errors gracefully
    """

    colang_content = """
    define flow handle errors gracefully
      user ...
      bot ...
    """

    try:
        config = RailsConfig.from_content(
            config=config_yaml,
            colang_content=colang_content
        )

        rails = LLMRails(config)
        rails.register_action(handle_error)

        test_input = "What is Python?"

        print("\n測試錯誤處理:")
        print("-" * 60)

        print(f"\n👤 用戶: {test_input}")

        try:
            response = rails.generate(messages=[{
                "role": "user",
                "content": test_input
            }])

            print(f"🤖 助手: {response['content']}")

        except Exception as e:
            error_msg = handle_error({"error_type": "unknown"})
            print(f"🤖 助手: {error_msg}")
            logger.error(f"Request failed: {str(e)}")

        print("\n" + "-" * 60)
        print("✅ 錯誤處理測試完成")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def caching_strategy():
    """
    緩存策略
    """
    print("\n" + "=" * 60)
    print("緩存策略示例")
    print("=" * 60)

    class ResponseCache:
        def __init__(self, ttl: int = 300):
            self.cache = {}
            self.ttl = ttl

        def get(self, key: str):
            if key in self.cache:
                entry = self.cache[key]
                if time.time() - entry['timestamp'] < self.ttl:
                    logger.info(f"Cache hit: {key}")
                    return entry['value']
                else:
                    del self.cache[key]

            logger.info(f"Cache miss: {key}")
            return None

        def set(self, key: str, value: Any):
            self.cache[key] = {
                'value': value,
                'timestamp': time.time()
            }
            logger.info(f"Cached: {key}")

    cache = ResponseCache(ttl=60)

    config_yaml = """
    models:
      - type: main
        engine: openai
        model: gpt-3.5-turbo
    """

    colang_content = """
    define flow
      user ...
      bot ...
    """

    try:
        config = RailsConfig.from_content(
            config=config_yaml,
            colang_content=colang_content
        )

        rails = LLMRails(config)

        test_input = "What is Python?"
        cache_key = f"response_{hash(test_input)}"

        print("\n測試緩存策略:")
        print("-" * 60)

        # 第一次請求
        cached_response = cache.get(cache_key)

        if cached_response is None:
            print(f"\n🔍 緩存未命中，調用 LLM...")
            print(f"👤 用戶: {test_input}")

            response = rails.generate(messages=[{
                "role": "user",
                "content": test_input
            }])

            cache.set(cache_key, response['content'])
            print(f"🤖 助手: {response['content']}")

        # 第二次請求（應該命中緩存）
        print(f"\n🔍 第二次請求...")
        cached_response = cache.get(cache_key)

        if cached_response:
            print(f"✅ 緩存命中！")
            print(f"🤖 助手: {cached_response}")

        print("\n" + "-" * 60)
        print("✅ 緩存策略測試完成")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def metrics_collection():
    """
    指標收集
    """
    print("\n" + "=" * 60)
    print("指標收集示例")
    print("=" * 60)

    class MetricsCollector:
        def __init__(self):
            self.metrics = {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "total_latency": 0.0
            }

        def record_request(self, success: bool, latency: float):
            self.metrics["total_requests"] += 1
            self.metrics["total_latency"] += latency

            if success:
                self.metrics["successful_requests"] += 1
            else:
                self.metrics["failed_requests"] += 1

        def get_metrics(self) -> Dict[str, Any]:
            avg_latency = (
                self.metrics["total_latency"] / self.metrics["total_requests"]
                if self.metrics["total_requests"] > 0 else 0
            )

            return {
                **self.metrics,
                "average_latency": avg_latency,
                "success_rate": (
                    self.metrics["successful_requests"] / self.metrics["total_requests"]
                    if self.metrics["total_requests"] > 0 else 0
                )
            }

    collector = MetricsCollector()

    config_yaml = """
    models:
      - type: main
        engine: openai
        model: gpt-3.5-turbo
    """

    colang_content = """
    define flow
      user ...
      bot ...
    """

    try:
        config = RailsConfig.from_content(
            config=config_yaml,
            colang_content=colang_content
        )

        rails = LLMRails(config)

        test_inputs = [
            "What is Python?",
            "Explain variables",
            "How do functions work?"
        ]

        print("\n測試指標收集:")
        print("-" * 60)

        for user_input in test_inputs:
            start_time = time.time()

            try:
                print(f"\n👤 用戶: {user_input}")

                response = rails.generate(messages=[{
                    "role": "user",
                    "content": user_input
                }])

                latency = time.time() - start_time
                collector.record_request(True, latency)

                print(f"🤖 助手: {response['content'][:100]}...")

            except Exception as e:
                latency = time.time() - start_time
                collector.record_request(False, latency)
                print(f"❌ 錯誤: {str(e)}")

        # 顯示指標
        metrics = collector.get_metrics()

        print("\n" + "-" * 60)
        print("\n📊 指標統計:")
        print(f"  總請求數: {metrics['total_requests']}")
        print(f"  成功請求: {metrics['successful_requests']}")
        print(f"  失敗請求: {metrics['failed_requests']}")
        print(f"  成功率: {metrics['success_rate']:.2%}")
        print(f"  平均延遲: {metrics['average_latency']:.3f} 秒")

        print("\n" + "-" * 60)
        print("✅ 指標收集測試完成")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def main():
    """
    主函數：運行所有企業部署示例
    """
    print("\n🛡️  NeMo Guardrails - 企業部署")
    print("=" * 60)

    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  警告: 未設置 OPENAI_API_KEY 環境變量")
        return

    # 運行各種企業部署示例
    production_configuration()
    monitoring_and_logging()
    rate_limiting()
    error_handling()
    caching_strategy()
    metrics_collection()

    print("\n" + "=" * 60)
    print("✅ 所有企業部署示例執行完成！")
    print("\n生產環境最佳實踐:")
    print("  1. 完整的配置管理")
    print("  2. 詳細的日誌記錄")
    print("  3. 速率限制保護")
    print("  4. 優雅的錯誤處理")
    print("  5. 響應緩存優化")
    print("  6. 全面的指標收集")
    print("  7. 安全性護欄")
    print("  8. 性能監控")
    print("=" * 60)


if __name__ == "__main__":
    main()

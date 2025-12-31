"""
Instructor 生產部署最佳實踐

這個模塊展示了在生產環境中使用 Instructor 的最佳實踐。
包括錯誤處理、性能優化、監控、日誌記錄和安全性考慮。

主要內容：
1. 錯誤處理和重試策略
2. 性能優化技巧
3. 日誌和監控
4. 緩存策略
5. 安全性考慮
6. 生產環境配置

作者: Instructor 示例
日期: 2025-01-01
"""

import os
import json
import time
import hashlib
import logging
from typing import List, Optional, Dict, Any, Callable
from datetime import datetime, timedelta
from functools import wraps
from pydantic import BaseModel, Field, ValidationError
import instructor
from openai import OpenAI
from anthropic import Anthropic


# ============================================================================
# 配置和日誌設置
# ============================================================================

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('instructor_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class Config:
    """應用配置類"""

    # API配置
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

    # 模型配置
    DEFAULT_MODEL = "gpt-4"
    FALLBACK_MODEL = "gpt-3.5-turbo"

    # 重試配置
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # 秒
    EXPONENTIAL_BACKOFF = True

    # 性能配置
    ENABLE_CACHE = True
    CACHE_TTL = 3600  # 秒
    REQUEST_TIMEOUT = 30  # 秒

    # 安全配置
    ENABLE_RATE_LIMITING = True
    MAX_REQUESTS_PER_MINUTE = 60

    # 監控配置
    ENABLE_METRICS = True
    ENABLE_DETAILED_LOGGING = True


# ============================================================================
# 數據模型
# ============================================================================

class ExtractionRequest(BaseModel):
    """提取請求模型"""
    request_id: str = Field(description="請求ID")
    text: str = Field(description="要提取的文本")
    model_type: str = Field(description="模型類型")
    timestamp: datetime = Field(default_factory=datetime.now)


class ExtractionResponse(BaseModel):
    """提取響應模型"""
    request_id: str = Field(description="請求ID")
    data: Dict[str, Any] = Field(description="提取的數據")
    success: bool = Field(description="是否成功")
    error_message: Optional[str] = Field(default=None, description="錯誤消息")
    processing_time: float = Field(description="處理時間（秒）")
    model_used: str = Field(description="使用的模型")
    tokens_used: Optional[int] = Field(default=None, description="使用的token數")


class BusinessEntity(BaseModel):
    """業務實體示例"""
    entity_id: str = Field(description="實體ID")
    name: str = Field(description="名稱")
    category: str = Field(description="類別")
    attributes: Dict[str, Any] = Field(
        default_factory=dict,
        description="屬性"
    )


# ============================================================================
# 簡單內存緩存實現
# ============================================================================

class SimpleCache:
    """簡單的內存緩存"""

    def __init__(self, ttl: int = 3600):
        self.cache: Dict[str, tuple] = {}
        self.ttl = ttl
        logger.info(f"緩存初始化，TTL: {ttl}秒")

    def _generate_key(self, *args, **kwargs) -> str:
        """生成緩存鍵"""
        key_str = json.dumps({
            'args': args,
            'kwargs': kwargs
        }, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """獲取緩存"""
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                logger.debug(f"緩存命中: {key}")
                return value
            else:
                # 過期，刪除
                del self.cache[key]
                logger.debug(f"緩存過期: {key}")
        return None

    def set(self, key: str, value: Any):
        """設置緩存"""
        self.cache[key] = (value, time.time())
        logger.debug(f"緩存設置: {key}")

    def clear(self):
        """清空緩存"""
        self.cache.clear()
        logger.info("緩存已清空")

    def get_stats(self) -> Dict[str, int]:
        """獲取緩存統計"""
        return {
            'total_items': len(self.cache),
            'valid_items': sum(
                1 for _, (_, ts) in self.cache.items()
                if time.time() - ts < self.ttl
            )
        }


# 全局緩存實例
cache = SimpleCache(ttl=Config.CACHE_TTL) if Config.ENABLE_CACHE else None


# ============================================================================
# 裝飾器：緩存
# ============================================================================

def with_cache(func: Callable) -> Callable:
    """緩存裝飾器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not Config.ENABLE_CACHE or cache is None:
            return func(*args, **kwargs)

        # 生成緩存鍵
        cache_key = cache._generate_key(*args, **kwargs)

        # 嘗試從緩存獲取
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            logger.info(f"使用緩存結果: {func.__name__}")
            return cached_result

        # 執行函數
        result = func(*args, **kwargs)

        # 保存到緩存
        cache.set(cache_key, result)

        return result

    return wrapper


# ============================================================================
# 裝飾器：重試邏輯
# ============================================================================

def with_retry(
    max_retries: int = Config.MAX_RETRIES,
    delay: float = Config.RETRY_DELAY,
    exponential_backoff: bool = Config.EXPONENTIAL_BACKOFF
):
    """重試裝飾器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)

                except ValidationError as e:
                    # 驗證錯誤，記錄並重試
                    logger.warning(
                        f"驗證錯誤 (嘗試 {attempt + 1}/{max_retries}): {str(e)}"
                    )
                    last_exception = e

                except Exception as e:
                    # 其他錯誤
                    logger.error(
                        f"執行錯誤 (嘗試 {attempt + 1}/{max_retries}): {str(e)}"
                    )
                    last_exception = e

                # 計算延遲時間
                if attempt < max_retries - 1:
                    if exponential_backoff:
                        wait_time = delay * (2 ** attempt)
                    else:
                        wait_time = delay

                    logger.info(f"等待 {wait_time:.1f} 秒後重試...")
                    time.sleep(wait_time)

            # 所有重試都失敗
            logger.error(f"所有重試失敗: {func.__name__}")
            raise last_exception

        return wrapper
    return decorator


# ============================================================================
# 裝飾器：性能監控
# ============================================================================

def with_metrics(func: Callable) -> Callable:
    """性能監控裝飾器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not Config.ENABLE_METRICS:
            return func(*args, **kwargs)

        start_time = time.time()
        success = False
        error = None

        try:
            result = func(*args, **kwargs)
            success = True
            return result

        except Exception as e:
            error = e
            raise

        finally:
            duration = time.time() - start_time

            # 記錄指標
            logger.info(
                f"指標 - 函數: {func.__name__}, "
                f"耗時: {duration:.2f}s, "
                f"成功: {success}"
            )

            if error:
                logger.error(f"錯誤: {str(error)}")

    return wrapper


# ============================================================================
# 生產級客戶端封裝
# ============================================================================

class ProductionClient:
    """生產級 Instructor 客戶端"""

    def __init__(
        self,
        provider: str = "openai",
        model: str = Config.DEFAULT_MODEL
    ):
        """初始化客戶端

        Args:
            provider: 提供商（openai 或 anthropic）
            model: 模型名稱
        """
        self.provider = provider
        self.model = model
        self.client = None
        self.request_count = 0
        self.last_request_time = None

        self._initialize_client()

        logger.info(
            f"客戶端初始化完成 - 提供商: {provider}, 模型: {model}"
        )

    def _initialize_client(self):
        """初始化 API 客戶端"""
        try:
            if self.provider == "openai":
                api_key = Config.OPENAI_API_KEY
                if not api_key:
                    raise ValueError("OPENAI_API_KEY 未設置")

                base_client = OpenAI(
                    api_key=api_key,
                    timeout=Config.REQUEST_TIMEOUT
                )
                self.client = instructor.from_openai(base_client)

            elif self.provider == "anthropic":
                api_key = Config.ANTHROPIC_API_KEY
                if not api_key:
                    raise ValueError("ANTHROPIC_API_KEY 未設置")

                base_client = Anthropic(
                    api_key=api_key,
                    timeout=Config.REQUEST_TIMEOUT
                )
                self.client = instructor.from_anthropic(base_client)

            else:
                raise ValueError(f"不支持的提供商: {self.provider}")

        except Exception as e:
            logger.error(f"客戶端初始化失敗: {str(e)}")
            raise

    def _check_rate_limit(self):
        """檢查速率限制"""
        if not Config.ENABLE_RATE_LIMITING:
            return

        current_time = time.time()

        # 重置計數器（每分鐘）
        if (self.last_request_time is None or
            current_time - self.last_request_time > 60):
            self.request_count = 0
            self.last_request_time = current_time

        # 檢查是否超過限制
        if self.request_count >= Config.MAX_REQUESTS_PER_MINUTE:
            wait_time = 60 - (current_time - self.last_request_time)
            logger.warning(f"達到速率限制，等待 {wait_time:.1f} 秒")
            time.sleep(wait_time)
            self.request_count = 0
            self.last_request_time = time.time()

        self.request_count += 1

    @with_metrics
    @with_retry(max_retries=Config.MAX_RETRIES)
    @with_cache
    def extract(
        self,
        response_model: type[BaseModel],
        messages: List[Dict[str, str]],
        **kwargs
    ) -> Any:
        """提取數據

        Args:
            response_model: Pydantic 模型類
            messages: 消息列表
            **kwargs: 其他參數

        Returns:
            提取的數據對象
        """
        # 檢查速率限制
        self._check_rate_limit()

        # 記錄請求
        if Config.ENABLE_DETAILED_LOGGING:
            logger.debug(f"提取請求 - 模型: {response_model.__name__}")

        try:
            # 根據提供商調用不同的 API
            if self.provider == "openai":
                result = self.client.chat.completions.create(
                    model=self.model,
                    response_model=response_model,
                    messages=messages,
                    **kwargs
                )
            else:  # anthropic
                # Anthropic 需要 max_tokens
                if 'max_tokens' not in kwargs:
                    kwargs['max_tokens'] = 1024

                result = self.client.messages.create(
                    model=self.model,
                    response_model=response_model,
                    messages=messages,
                    **kwargs
                )

            logger.info(f"提取成功 - 模型: {response_model.__name__}")
            return result

        except Exception as e:
            logger.error(f"提取失敗: {str(e)}")
            raise

    def extract_with_fallback(
        self,
        response_model: type[BaseModel],
        messages: List[Dict[str, str]],
        **kwargs
    ) -> Any:
        """帶回退的提取

        如果主模型失敗，自動切換到回退模型。

        Args:
            response_model: Pydantic 模型類
            messages: 消息列表
            **kwargs: 其他參數

        Returns:
            提取的數據對象
        """
        try:
            # 嘗試主模型
            return self.extract(response_model, messages, **kwargs)

        except Exception as e:
            logger.warning(f"主模型失敗，切換到回退模型: {str(e)}")

            # 切換到回退模型
            original_model = self.model
            self.model = Config.FALLBACK_MODEL

            try:
                result = self.extract(response_model, messages, **kwargs)
                logger.info("回退模型成功")
                return result

            finally:
                # 恢復原模型
                self.model = original_model

    def batch_extract(
        self,
        response_model: type[BaseModel],
        texts: List[str],
        **kwargs
    ) -> List[Any]:
        """批量提取

        Args:
            response_model: Pydantic 模型類
            texts: 文本列表
            **kwargs: 其他參數

        Returns:
            提取結果列表
        """
        results = []
        failed_count = 0

        logger.info(f"開始批量提取 - 數量: {len(texts)}")

        for i, text in enumerate(texts):
            try:
                messages = [
                    {"role": "user", "content": text}
                ]
                result = self.extract(response_model, messages, **kwargs)
                results.append(result)

                if (i + 1) % 10 == 0:
                    logger.info(f"批量進度: {i + 1}/{len(texts)}")

            except Exception as e:
                logger.error(f"批量提取失敗 (索引 {i}): {str(e)}")
                failed_count += 1
                results.append(None)

        logger.info(
            f"批量提取完成 - 成功: {len(texts) - failed_count}, "
            f"失敗: {failed_count}"
        )

        return results

    def get_stats(self) -> Dict[str, Any]:
        """獲取統計信息"""
        stats = {
            'provider': self.provider,
            'model': self.model,
            'request_count': self.request_count,
        }

        if cache:
            stats['cache'] = cache.get_stats()

        return stats


# ============================================================================
# 錯誤處理和恢復
# ============================================================================

class ExtractionError(Exception):
    """提取錯誤基類"""
    pass


class ValidationFailedError(ExtractionError):
    """驗證失敗錯誤"""
    pass


class RateLimitError(ExtractionError):
    """速率限制錯誤"""
    pass


def safe_extract(
    client: ProductionClient,
    response_model: type[BaseModel],
    text: str,
    default_value: Optional[Any] = None
) -> tuple[Optional[Any], Optional[str]]:
    """安全的提取函數

    Args:
        client: 客戶端實例
        response_model: 模型類
        text: 文本
        default_value: 默認值

    Returns:
        (結果, 錯誤消息) 元組
    """
    try:
        messages = [{"role": "user", "content": text}]
        result = client.extract(response_model, messages)
        return result, None

    except ValidationError as e:
        error_msg = f"驗證錯誤: {str(e)}"
        logger.error(error_msg)
        return default_value, error_msg

    except Exception as e:
        error_msg = f"提取錯誤: {str(e)}"
        logger.error(error_msg)
        return default_value, error_msg


# ============================================================================
# 示例和測試
# ============================================================================

def demo_production_usage():
    """演示生產環境使用"""
    print(f"\n{'='*60}")
    print("生產環境使用示例")
    print(f"{'='*60}")

    # 初始化客戶端
    client = ProductionClient(provider="openai", model="gpt-4")

    # 單次提取
    text = "提取：張三，28歲，工程師，郵箱：zhang@example.com"
    print(f"\n1. 單次提取:")
    print(f"   輸入: {text}")

    result, error = safe_extract(
        client,
        BusinessEntity,
        f"從以下文本提取業務實體：{text}"
    )

    if result:
        print(f"   ✓ 成功: {result.name}")
    else:
        print(f"   ✗ 失敗: {error}")

    # 批量提取
    texts = [
        "實體A：科技公司，類別：企業",
        "實體B：創新產品，類別：產品",
        "實體C：市場部門，類別：部門"
    ]

    print(f"\n2. 批量提取:")
    print(f"   數量: {len(texts)}")

    # 注意：在實際使用中不要在演示中真正調用批量提取
    # results = client.batch_extract(BusinessEntity, texts)
    # print(f"   完成: {sum(1 for r in results if r is not None)}/{len(texts)}")

    # 統計信息
    print(f"\n3. 統計信息:")
    stats = client.get_stats()
    print(f"   提供商: {stats['provider']}")
    print(f"   模型: {stats['model']}")
    print(f"   請求數: {stats['request_count']}")

    if 'cache' in stats:
        print(f"   緩存項: {stats['cache']['valid_items']}")


def demo_error_handling():
    """演示錯誤處理"""
    print(f"\n{'='*60}")
    print("錯誤處理示例")
    print(f"{'='*60}")

    client = ProductionClient()

    # 測試不同的錯誤場景
    print("\n處理無效輸入:")
    result, error = safe_extract(
        client,
        BusinessEntity,
        "這是一段無關的文本"
    )

    if error:
        print(f"  ✓ 錯誤已捕獲: {error[:50]}...")
    else:
        print(f"  結果: {result}")


def demo_performance_optimization():
    """演示性能優化"""
    print(f"\n{'='*60}")
    print("性能優化示例")
    print(f"{'='*60}")

    client = ProductionClient()

    text = "提取實體：測試公司，類別：企業"

    # 第一次請求（無緩存）
    print("\n第一次請求（無緩存）:")
    start = time.time()
    result1, _ = safe_extract(client, BusinessEntity, text)
    duration1 = time.time() - start
    print(f"  耗時: {duration1:.2f}秒")

    # 第二次請求（使用緩存）
    if Config.ENABLE_CACHE:
        print("\n第二次請求（使用緩存）:")
        start = time.time()
        result2, _ = safe_extract(client, BusinessEntity, text)
        duration2 = time.time() - start
        print(f"  耗時: {duration2:.2f}秒")
        print(f"  提速: {(duration1 - duration2) / duration1 * 100:.1f}%")


# ============================================================================
# 主程序
# ============================================================================

def main():
    """主函數 - 運行生產部署示例"""
    print("="*60)
    print("Instructor 生產部署最佳實踐")
    print("="*60)

    # 演示各種場景
    demo_production_usage()
    demo_error_handling()
    demo_performance_optimization()

    print("\n" + "="*60)
    print("生產部署要點總結")
    print("="*60)
    print("""
1. 配置管理：
   - 使用環境變量管理 API 密鑰
   - 集中配置管理
   - 區分開發和生產環境

2. 錯誤處理：
   - 實現重試機制
   - 指數退避策略
   - 優雅降級
   - 詳細錯誤日誌

3. 性能優化：
   - 啟用緩存機制
   - 批量處理
   - 合理設置超時
   - 選擇合適的模型

4. 監控和日誌：
   - 結構化日誌記錄
   - 性能指標追蹤
   - 錯誤率監控
   - 成本追蹤

5. 安全性：
   - API 密鑰保護
   - 速率限制
   - 輸入驗證
   - 敏感數據處理

6. 可靠性：
   - 回退機制
   - 健康檢查
   - 優雅關閉
   - 故障恢復

7. 擴展性：
   - 客戶端池化
   - 負載均衡
   - 異步處理
   - 隊列機制

8. 成本優化：
   - 模型選擇策略
   - 緩存復用
   - 批量處理
   - token 使用優化

9. 部署檢查清單：
   ✓ 環境變量配置
   ✓ 日誌系統設置
   ✓ 錯誤處理完善
   ✓ 監控告警配置
   ✓ 性能測試通過
   ✓ 安全審計完成
   ✓ 文檔更新完整
   ✓ 備份恢復方案

10. 持續改進：
    - 監控關鍵指標
    - 定期性能優化
    - 收集用戶反饋
    - 更新最佳實踐
    """)

    print("\n✓ 所有生產部署示例運行完成！")


if __name__ == "__main__":
    main()

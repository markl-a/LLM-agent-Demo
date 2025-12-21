"""
Dify 進階技巧範例
================

本範例展示 Dify 的進階使用技巧和最佳實踐。

進階技巧包括：
1. 自定義提示詞工程
2. 上下文管理優化
3. 錯誤處理和重試
4. 性能優化
5. 安全最佳實踐
6. 多租戶支持

安裝依賴：
pip install requests tenacity cachetools
"""

import os
import json
import time
import hashlib
import requests
from typing import Dict, Any, Optional, List, Callable, TypeVar
from dataclasses import dataclass
from functools import wraps
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# ============================================================
# 配置
# ============================================================

DIFY_API_KEY = os.getenv("DIFY_API_KEY", "app-xxxxxxxxxxxxxxxx")
DIFY_BASE_URL = os.getenv("DIFY_BASE_URL", "https://api.dify.ai/v1")

logger = logging.getLogger(__name__)

T = TypeVar('T')


# ============================================================
# 提示詞工程
# ============================================================

class PromptTemplate:
    """
    提示詞模板

    支持變數替換和驗證
    """

    def __init__(self, template: str, required_vars: Optional[List[str]] = None):
        self.template = template
        self.required_vars = required_vars or []

    def render(self, **kwargs) -> str:
        """
        渲染模板

        Args:
            **kwargs: 變數值

        Returns:
            渲染後的提示詞
        """
        # 驗證必需變數
        missing = [v for v in self.required_vars if v not in kwargs]
        if missing:
            raise ValueError(f"缺少必需變數: {missing}")

        result = self.template
        for key, value in kwargs.items():
            result = result.replace(f"{{{{{key}}}}}", str(value))

        return result


class PromptLibrary:
    """
    提示詞庫

    管理和組織提示詞模板
    """

    def __init__(self):
        self.templates: Dict[str, PromptTemplate] = {}

    def register(
        self,
        name: str,
        template: str,
        required_vars: Optional[List[str]] = None
    ):
        """註冊模板"""
        self.templates[name] = PromptTemplate(template, required_vars)

    def get(self, name: str) -> Optional[PromptTemplate]:
        """獲取模板"""
        return self.templates.get(name)

    def render(self, name: str, **kwargs) -> str:
        """渲染指定模板"""
        template = self.get(name)
        if not template:
            raise ValueError(f"模板不存在: {name}")
        return template.render(**kwargs)


# ============================================================
# 上下文管理
# ============================================================

class ConversationContext:
    """
    對話上下文管理

    管理對話歷史和上下文窗口
    """

    def __init__(
        self,
        max_messages: int = 20,
        max_tokens: int = 4000
    ):
        self.max_messages = max_messages
        self.max_tokens = max_tokens
        self.messages: List[Dict[str, str]] = []
        self.metadata: Dict[str, Any] = {}

    def add_message(self, role: str, content: str):
        """添加消息"""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

        # 修剪歷史
        self._trim_history()

    def _trim_history(self):
        """修剪歷史以符合限制"""
        # 按消息數量修剪
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]

        # 按 token 數量修剪（簡化估算）
        total_tokens = sum(len(m['content']) // 4 for m in self.messages)
        while total_tokens > self.max_tokens and len(self.messages) > 1:
            self.messages.pop(0)
            total_tokens = sum(len(m['content']) // 4 for m in self.messages)

    def get_context_summary(self) -> str:
        """獲取上下文摘要"""
        if len(self.messages) <= 3:
            return ""

        # 簡單的上下文壓縮
        older_messages = self.messages[:-3]
        summary_parts = []

        for msg in older_messages:
            if msg['role'] == 'user':
                summary_parts.append(f"用戶問：{msg['content'][:50]}...")

        return "之前的對話摘要：" + "；".join(summary_parts)

    def clear(self):
        """清除上下文"""
        self.messages.clear()
        self.metadata.clear()


# ============================================================
# 錯誤處理和重試
# ============================================================

class RetryConfig:
    """重試配置"""
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 30.0
    exponential_base: float = 2.0


def with_retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    exceptions: tuple = (requests.exceptions.RequestException,)
):
    """
    重試裝飾器

    Args:
        max_retries: 最大重試次數
        base_delay: 基礎延遲（秒）
        exceptions: 需要重試的異常類型
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        delay = base_delay * (2 ** attempt)
                        logger.warning(
                            f"嘗試 {attempt + 1}/{max_retries + 1} 失敗: {e}. "
                            f"等待 {delay:.1f}s 後重試..."
                        )
                        time.sleep(delay)

            raise last_exception

        return wrapper
    return decorator


class CircuitBreaker:
    """
    熔斷器

    防止級聯故障
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "closed"  # closed, open, half-open

    def record_success(self):
        """記錄成功"""
        self.failures = 0
        self.state = "closed"

    def record_failure(self):
        """記錄失敗"""
        self.failures += 1
        self.last_failure_time = datetime.now()

        if self.failures >= self.failure_threshold:
            self.state = "open"
            logger.warning("熔斷器已開啟")

    def can_execute(self) -> bool:
        """檢查是否可以執行"""
        if self.state == "closed":
            return True

        if self.state == "open":
            # 檢查是否可以嘗試恢復
            if self.last_failure_time:
                elapsed = (datetime.now() - self.last_failure_time).total_seconds()
                if elapsed >= self.recovery_timeout:
                    self.state = "half-open"
                    return True
            return False

        # half-open 狀態
        return True


# ============================================================
# 緩存系統
# ============================================================

class ResponseCache:
    """
    響應緩存

    緩存相似查詢的響應
    """

    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.ttl = timedelta(seconds=ttl_seconds)

    def _generate_key(self, query: str, inputs: Optional[Dict] = None) -> str:
        """生成緩存鍵"""
        data = f"{query}:{json.dumps(inputs or {}, sort_keys=True)}"
        return hashlib.md5(data.encode()).hexdigest()

    def get(
        self,
        query: str,
        inputs: Optional[Dict] = None
    ) -> Optional[str]:
        """獲取緩存"""
        key = self._generate_key(query, inputs)
        entry = self.cache.get(key)

        if entry:
            if datetime.now() - entry['timestamp'] < self.ttl:
                return entry['response']
            else:
                del self.cache[key]

        return None

    def set(
        self,
        query: str,
        response: str,
        inputs: Optional[Dict] = None
    ):
        """設置緩存"""
        # 清理過期緩存
        self._cleanup()

        # 檢查大小限制
        if len(self.cache) >= self.max_size:
            oldest_key = min(
                self.cache.keys(),
                key=lambda k: self.cache[k]['timestamp']
            )
            del self.cache[oldest_key]

        key = self._generate_key(query, inputs)
        self.cache[key] = {
            'response': response,
            'timestamp': datetime.now()
        }

    def _cleanup(self):
        """清理過期緩存"""
        now = datetime.now()
        expired = [
            k for k, v in self.cache.items()
            if now - v['timestamp'] >= self.ttl
        ]
        for k in expired:
            del self.cache[k]


# ============================================================
# 並行處理
# ============================================================

class ParallelProcessor:
    """
    並行處理器

    支持並行執行多個請求
    """

    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers

    def process_batch(
        self,
        items: List[Dict[str, Any]],
        processor: Callable[[Dict[str, Any]], Any]
    ) -> List[Dict[str, Any]]:
        """
        批量並行處理

        Args:
            items: 待處理項目列表
            processor: 處理函數

        Returns:
            處理結果列表
        """
        results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_item = {
                executor.submit(processor, item): i
                for i, item in enumerate(items)
            }

            for future in as_completed(future_to_item):
                index = future_to_item[future]
                try:
                    result = future.result()
                    results.append({
                        'index': index,
                        'status': 'success',
                        'result': result
                    })
                except Exception as e:
                    results.append({
                        'index': index,
                        'status': 'error',
                        'error': str(e)
                    })

        # 按原始順序排序
        results.sort(key=lambda x: x['index'])
        return results


# ============================================================
# 安全工具
# ============================================================

class InputSanitizer:
    """
    輸入淨化器

    過濾和驗證用戶輸入
    """

    @staticmethod
    def sanitize_query(query: str, max_length: int = 10000) -> str:
        """
        淨化查詢文本

        Args:
            query: 原始查詢
            max_length: 最大長度

        Returns:
            淨化後的查詢
        """
        # 移除控制字符
        sanitized = ''.join(c for c in query if c.isprintable() or c in '\n\t')

        # 限制長度
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]

        return sanitized.strip()

    @staticmethod
    def validate_user_id(user_id: str) -> bool:
        """驗證用戶 ID"""
        if not user_id:
            return False
        if len(user_id) > 100:
            return False
        # 只允許字母、數字、下劃線、連字符
        return all(c.isalnum() or c in '_-' for c in user_id)


class RateLimiter:
    """
    速率限制器

    限制 API 調用頻率
    """

    def __init__(
        self,
        calls_per_minute: int = 60,
        calls_per_day: int = 10000
    ):
        self.calls_per_minute = calls_per_minute
        self.calls_per_day = calls_per_day
        self.minute_calls: List[datetime] = []
        self.day_calls: List[datetime] = []

    def check_limit(self) -> bool:
        """檢查是否超過限制"""
        now = datetime.now()

        # 清理過期記錄
        minute_ago = now - timedelta(minutes=1)
        day_ago = now - timedelta(days=1)

        self.minute_calls = [t for t in self.minute_calls if t > minute_ago]
        self.day_calls = [t for t in self.day_calls if t > day_ago]

        # 檢查限制
        if len(self.minute_calls) >= self.calls_per_minute:
            return False
        if len(self.day_calls) >= self.calls_per_day:
            return False

        return True

    def record_call(self):
        """記錄調用"""
        now = datetime.now()
        self.minute_calls.append(now)
        self.day_calls.append(now)


# ============================================================
# 增強型客戶端
# ============================================================

class EnhancedDifyClient:
    """
    增強型 Dify 客戶端

    整合所有進階功能
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.dify.ai/v1"
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # 初始化組件
        self.cache = ResponseCache()
        self.circuit_breaker = CircuitBreaker()
        self.rate_limiter = RateLimiter()
        self.sanitizer = InputSanitizer()
        self.contexts: Dict[str, ConversationContext] = {}

    def get_context(self, user: str) -> ConversationContext:
        """獲取或創建用戶上下文"""
        if user not in self.contexts:
            self.contexts[user] = ConversationContext()
        return self.contexts[user]

    @with_retry(max_retries=3, base_delay=1.0)
    def chat(
        self,
        query: str,
        user: str,
        conversation_id: Optional[str] = None,
        inputs: Optional[Dict[str, Any]] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        發送對話請求（帶增強功能）

        Args:
            query: 用戶查詢
            user: 用戶標識
            conversation_id: 對話 ID
            inputs: 變數輸入
            use_cache: 是否使用緩存

        Returns:
            對話響應
        """
        # 驗證輸入
        if not self.sanitizer.validate_user_id(user):
            raise ValueError("無效的用戶 ID")

        query = self.sanitizer.sanitize_query(query)

        # 檢查速率限制
        if not self.rate_limiter.check_limit():
            raise Exception("超過速率限制")

        # 檢查熔斷器
        if not self.circuit_breaker.can_execute():
            raise Exception("服務暫時不可用（熔斷器開啟）")

        # 檢查緩存
        if use_cache and not conversation_id:
            cached = self.cache.get(query, inputs)
            if cached:
                return {"answer": cached, "from_cache": True}

        # 發送請求
        url = f"{self.base_url}/chat-messages"

        payload = {
            "query": query,
            "user": user,
            "response_mode": "blocking",
            "inputs": inputs or {}
        }

        if conversation_id:
            payload["conversation_id"] = conversation_id

        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()

            result = response.json()

            # 記錄成功
            self.circuit_breaker.record_success()
            self.rate_limiter.record_call()

            # 更新緩存
            if use_cache and not conversation_id:
                self.cache.set(query, result.get('answer', ''), inputs)

            # 更新上下文
            context = self.get_context(user)
            context.add_message("user", query)
            context.add_message("assistant", result.get('answer', ''))

            return result

        except requests.exceptions.RequestException as e:
            self.circuit_breaker.record_failure()
            raise


# ============================================================
# 使用範例
# ============================================================

def example_prompt_engineering():
    """
    範例 1: 提示詞工程

    展示如何使用提示詞模板
    """
    print("=" * 50)
    print("範例 1: 提示詞工程")
    print("=" * 50)

    library = PromptLibrary()

    # 註冊模板
    library.register(
        "summarize",
        """請用{{language}}總結以下內容，長度控制在{{max_words}}字以內：

{{content}}

總結：""",
        required_vars=["content", "language", "max_words"]
    )

    library.register(
        "translate",
        """請將以下{{source_lang}}文本翻譯成{{target_lang}}：

{{text}}

翻譯：""",
        required_vars=["text", "source_lang", "target_lang"]
    )

    # 使用模板
    prompt = library.render(
        "summarize",
        content="這是一段很長的內容...",
        language="繁體中文",
        max_words=100
    )

    print("生成的提示詞:")
    print(prompt)


def example_context_management():
    """
    範例 2: 上下文管理

    展示如何管理對話上下文
    """
    print("\n" + "=" * 50)
    print("範例 2: 上下文管理")
    print("=" * 50)

    context = ConversationContext(max_messages=10, max_tokens=2000)

    # 模擬對話
    conversation = [
        ("user", "你好，我想了解 Python"),
        ("assistant", "你好！Python 是一種流行的編程語言..."),
        ("user", "它有什麼特點？"),
        ("assistant", "Python 有以下特點：1. 簡潔易讀..."),
        ("user", "能給個例子嗎？"),
    ]

    for role, content in conversation:
        context.add_message(role, content)

    print(f"當前消息數: {len(context.messages)}")
    print(f"上下文摘要: {context.get_context_summary()}")


def example_retry_and_circuit_breaker():
    """
    範例 3: 重試和熔斷

    展示錯誤處理機制
    """
    print("\n" + "=" * 50)
    print("範例 3: 重試和熔斷")
    print("=" * 50)

    circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=10)

    # 模擬失敗
    for i in range(5):
        if circuit_breaker.can_execute():
            print(f"嘗試 {i + 1}: 可以執行")
            circuit_breaker.record_failure()
            print(f"  狀態: {circuit_breaker.state}, 失敗次數: {circuit_breaker.failures}")
        else:
            print(f"嘗試 {i + 1}: 熔斷器開啟，跳過")


def example_caching():
    """
    範例 4: 緩存系統

    展示響應緩存
    """
    print("\n" + "=" * 50)
    print("範例 4: 緩存系統")
    print("=" * 50)

    cache = ResponseCache(ttl_seconds=60)

    # 設置緩存
    cache.set("什麼是 AI？", "AI 是人工智能的縮寫...")

    # 獲取緩存
    result = cache.get("什麼是 AI？")
    print(f"緩存命中: {result is not None}")
    print(f"緩存內容: {result}")

    # 不存在的緩存
    result2 = cache.get("其他問題")
    print(f"緩存未命中: {result2 is None}")


def example_parallel_processing():
    """
    範例 5: 並行處理

    展示批量並行處理
    """
    print("\n" + "=" * 50)
    print("範例 5: 並行處理")
    print("=" * 50)

    processor = ParallelProcessor(max_workers=3)

    # 模擬處理函數
    def process_item(item: Dict[str, Any]) -> str:
        time.sleep(0.5)  # 模擬處理延遲
        return f"處理完成: {item['text']}"

    items = [
        {"text": "項目 1"},
        {"text": "項目 2"},
        {"text": "項目 3"},
    ]

    print("開始並行處理...")
    start = time.time()
    results = processor.process_batch(items, process_item)
    elapsed = time.time() - start

    print(f"處理完成，耗時: {elapsed:.2f}s")
    for r in results:
        print(f"  {r['index']}: {r['status']} - {r.get('result', r.get('error'))}")


def example_security():
    """
    範例 6: 安全最佳實踐

    展示輸入驗證和速率限制
    """
    print("\n" + "=" * 50)
    print("範例 6: 安全最佳實踐")
    print("=" * 50)

    sanitizer = InputSanitizer()
    limiter = RateLimiter(calls_per_minute=5, calls_per_day=100)

    # 輸入淨化
    dirty_input = "正常文本\x00\x01\x02非法字符"
    clean_input = sanitizer.sanitize_query(dirty_input)
    print(f"淨化前: {repr(dirty_input)}")
    print(f"淨化後: {repr(clean_input)}")

    # 用戶 ID 驗證
    print(f"\n驗證 'user123': {sanitizer.validate_user_id('user123')}")
    print(f"驗證 'user@123': {sanitizer.validate_user_id('user@123')}")

    # 速率限制
    print("\n測試速率限制:")
    for i in range(7):
        if limiter.check_limit():
            limiter.record_call()
            print(f"  請求 {i + 1}: 允許")
        else:
            print(f"  請求 {i + 1}: 被限制")


def example_enhanced_client():
    """
    範例 7: 增強型客戶端

    展示整合所有功能的客戶端
    """
    print("\n" + "=" * 50)
    print("範例 7: 增強型客戶端")
    print("=" * 50)

    client = EnhancedDifyClient(
        api_key=DIFY_API_KEY,
        base_url=DIFY_BASE_URL
    )

    print("增強型客戶端功能:")
    print("  - 自動重試")
    print("  - 熔斷器保護")
    print("  - 響應緩存")
    print("  - 速率限制")
    print("  - 輸入淨化")
    print("  - 上下文管理")

    # 模擬使用
    try:
        # result = client.chat(
        #     query="你好",
        #     user="user-001",
        #     use_cache=True
        # )
        # print(f"\n回覆: {result.get('answer')}")
        print("\n（模擬）請求已發送")
    except Exception as e:
        print(f"錯誤: {e}")


# ============================================================
# 主程序
# ============================================================

if __name__ == "__main__":
    print("Dify 進階技巧範例")
    print("請確保已設置相關環境變數")
    print()

    example_prompt_engineering()
    example_context_management()
    example_retry_and_circuit_breaker()
    example_caching()
    example_parallel_processing()
    example_security()
    example_enhanced_client()

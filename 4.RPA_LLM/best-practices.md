# RPA + LLM 最佳實踐與設計模式

## 目錄

1. [設計原則](#設計原則)
2. [常見模式](#常見模式)
3. [錯誤處理](#錯誤處理)
4. [性能優化](#性能優化)
5. [安全最佳實踐](#安全最佳實踐)
6. [成本優化](#成本優化)
7. [常見反模式](#常見反模式)

---

## 設計原則

### 1. 單一職責原則 (SRP)

每個模組應該只有一個改變的理由。

**✅ 好的設計**：
```python
class InvoiceExtractor:
    """只負責提取發票數據"""
    async def extract(self, text: str) -> dict:
        pass

class InvoiceValidator:
    """只負責驗證發票數據"""
    async def validate(self, data: dict) -> bool:
        pass

class InvoiceSaver:
    """只負責保存發票數據"""
    async def save(self, data: dict):
        pass
```

**❌ 不好的設計**：
```python
class InvoiceProcessor:
    """職責過多，難以維護"""
    async def process_everything(self, text: str):
        # 提取
        # 驗證
        # 保存
        # 發送郵件
        # 更新資料庫
        # ...
        pass
```

### 2. 依賴注入 (DI)

通過參數傳入依賴，而不是在類內部創建。

**✅ 好的設計**：
```python
class WorkflowExecutor:
    def __init__(self, llm: BaseLLM, logger: Logger):
        self.llm = llm  # 注入依賴
        self.logger = logger

    async def execute(self, task: str):
        result = await self.llm.generate(task)
        self.logger.info(f"Task completed: {task}")
        return result

# 使用
llm = get_llm("openai")
logger = setup_logger("workflow")
executor = WorkflowExecutor(llm, logger)
```

**❌ 不好的設計**：
```python
class WorkflowExecutor:
    def __init__(self):
        self.llm = OpenAILLM()  # 硬編碼依賴
        self.logger = logging.getLogger()

    async def execute(self, task: str):
        # 難以測試和替換
        pass
```

### 3. 配置外部化

所有配置應該在代碼外部，便於管理和修改。

**✅ 好的設計**：
```python
# config/settings.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    llm_provider: str = "openai"
    llm_model: str = "gpt-4"
    max_retries: int = 3
    timeout: int = 30

    class Config:
        env_file = ".env"

settings = Settings()
```

**❌ 不好的設計**：
```python
# 硬編碼在代碼中
LLM_PROVIDER = "openai"
MAX_RETRIES = 3
API_KEY = "sk-xxx"  # 極度危險！
```

---

## 常見模式

### 1. 策略模式 - LLM 提供者切換

```python
from abc import ABC, abstractmethod

class LLMStrategy(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        pass

class OpenAIStrategy(LLMStrategy):
    async def generate(self, prompt: str) -> str:
        # OpenAI 實現
        pass

class ClaudeStrategy(LLMStrategy):
    async def generate(self, prompt: str) -> str:
        # Claude 實現
        pass

class LLMContext:
    def __init__(self, strategy: LLMStrategy):
        self.strategy = strategy

    async def execute(self, prompt: str) -> str:
        return await self.strategy.generate(prompt)

# 使用
context = LLMContext(OpenAIStrategy())
result = await context.execute("Hello")

# 切換策略
context.strategy = ClaudeStrategy()
result = await context.execute("Hello")
```

### 2. 責任鏈模式 - 數據處理管道

```python
from abc import ABC, abstractmethod
from typing import Optional

class DataHandler(ABC):
    def __init__(self):
        self.next_handler: Optional[DataHandler] = None

    def set_next(self, handler: 'DataHandler'):
        self.next_handler = handler
        return handler

    @abstractmethod
    async def handle(self, data: dict) -> dict:
        pass

    async def process(self, data: dict) -> dict:
        result = await self.handle(data)
        if self.next_handler:
            return await self.next_handler.process(result)
        return result

class ExtractHandler(DataHandler):
    async def handle(self, data: dict) -> dict:
        # 提取邏輯
        data['extracted'] = True
        return data

class ValidateHandler(DataHandler):
    async def handle(self, data: dict) -> dict:
        # 驗證邏輯
        data['validated'] = True
        return data

class TransformHandler(DataHandler):
    async def handle(self, data: dict) -> dict:
        # 轉換邏輯
        data['transformed'] = True
        return data

# 構建處理鏈
extract = ExtractHandler()
validate = ValidateHandler()
transform = TransformHandler()

extract.set_next(validate).set_next(transform)

# 執行
result = await extract.process({'raw_data': '...'})
```

### 3. 觀察者模式 - 事件通知

```python
from typing import List, Callable
import asyncio

class EventEmitter:
    def __init__(self):
        self.listeners: dict[str, List[Callable]] = {}

    def on(self, event: str, callback: Callable):
        """註冊事件監聽器"""
        if event not in self.listeners:
            self.listeners[event] = []
        self.listeners[event].append(callback)

    async def emit(self, event: str, data: any):
        """觸發事件"""
        if event in self.listeners:
            await asyncio.gather(*[
                callback(data)
                for callback in self.listeners[event]
            ])

# 使用
emitter = EventEmitter()

async def log_event(data):
    print(f"Logged: {data}")

async def send_notification(data):
    print(f"Notification sent: {data}")

emitter.on("task_completed", log_event)
emitter.on("task_completed", send_notification)

await emitter.emit("task_completed", {"task_id": "123"})
```

### 4. 重試模式 - 增強可靠性

```python
import asyncio
from functools import wraps
from typing import TypeVar, Callable

T = TypeVar('T')

def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """重試裝飾器"""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            current_delay = delay

            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts - 1:
                        raise

                    print(f"Attempt {attempt + 1} failed: {e}")
                    print(f"Retrying in {current_delay}s...")

                    await asyncio.sleep(current_delay)
                    current_delay *= backoff

        return wrapper
    return decorator

# 使用
@retry(max_attempts=5, delay=1.0, backoff=2.0)
async def call_llm(prompt: str) -> str:
    # 可能失敗的 LLM 調用
    return await llm.generate(prompt)
```

### 5. 緩存模式 - 減少重複調用

```python
import hashlib
import json
from typing import Optional
import redis

class LLMCache:
    def __init__(self, redis_client: redis.Redis, ttl: int = 3600):
        self.redis = redis_client
        self.ttl = ttl

    def _generate_key(self, prompt: str, model: str) -> str:
        """生成緩存鍵"""
        content = f"{model}:{prompt}"
        return hashlib.sha256(content.encode()).hexdigest()

    async def get(self, prompt: str, model: str) -> Optional[str]:
        """獲取緩存"""
        key = self._generate_key(prompt, model)
        value = self.redis.get(key)
        return value.decode() if value else None

    async def set(self, prompt: str, model: str, response: str):
        """設置緩存"""
        key = self._generate_key(prompt, model)
        self.redis.setex(key, self.ttl, response)

class CachedLLM:
    def __init__(self, llm: BaseLLM, cache: LLMCache):
        self.llm = llm
        self.cache = cache

    async def generate(self, prompt: str) -> str:
        # 檢查緩存
        cached = await self.cache.get(prompt, self.llm.model)
        if cached:
            print("Cache hit!")
            return cached

        # 調用 LLM
        response = await self.llm.generate(prompt)

        # 保存到緩存
        await self.cache.set(prompt, self.llm.model, response)

        return response
```

---

## 錯誤處理

### 1. 分層錯誤處理

```python
class RPAError(Exception):
    """RPA 基礎異常"""
    pass

class NetworkError(RPAError):
    """網路相關錯誤"""
    pass

class ValidationError(RPAError):
    """驗證錯誤"""
    pass

class LLMError(RPAError):
    """LLM 相關錯誤"""
    pass

async def process_invoice(file_path: str):
    try:
        # 讀取文件
        try:
            text = extract_pdf(file_path)
        except FileNotFoundError:
            raise ValidationError(f"File not found: {file_path}")

        # 調用 LLM
        try:
            data = await llm.extract(text)
        except Exception as e:
            raise LLMError(f"LLM extraction failed: {e}")

        # 保存結果
        try:
            save_to_database(data)
        except Exception as e:
            raise NetworkError(f"Database save failed: {e}")

    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        # 通知用戶檢查文件
    except LLMError as e:
        logger.error(f"LLM error: {e}")
        # 嘗試備用 LLM
    except NetworkError as e:
        logger.error(f"Network error: {e}")
        # 重試或隊列處理
    except RPAError as e:
        logger.error(f"RPA error: {e}")
        # 通用處理
```

### 2. 優雅降級

```python
class RobustLLM:
    def __init__(self, primary: BaseLLM, fallback: BaseLLM):
        self.primary = primary
        self.fallback = fallback

    async def generate(self, prompt: str) -> str:
        try:
            return await self.primary.generate(prompt)
        except Exception as e:
            logger.warning(f"Primary LLM failed: {e}, using fallback")
            try:
                return await self.fallback.generate(prompt)
            except Exception as e2:
                logger.error(f"Fallback also failed: {e2}")
                # 返回默認值或重新拋出
                raise

# 使用
llm = RobustLLM(
    primary=OpenAILLM(),
    fallback=ClaudeLLM()
)
```

### 3. 斷路器模式

```python
import time
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"  # 正常
    OPEN = "open"  # 斷開
    HALF_OPEN = "half_open"  # 半開

class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: float = 60.0,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    async def call(self, func: Callable, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = await func(*args, **kwargs)

            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                self.failure_count = 0

            return result

        except self.expected_exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN

            raise

# 使用
breaker = CircuitBreaker(failure_threshold=3, timeout=30.0)

async def protected_llm_call(prompt: str):
    return await breaker.call(llm.generate, prompt)
```

---

## 性能優化

### 1. 並發處理

```python
import asyncio
from typing import List

async def process_batch(items: List[str]) -> List[dict]:
    """並發處理多個項目"""
    tasks = [process_item(item) for item in items]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # 處理結果和異常
    successful = []
    failed = []

    for item, result in zip(items, results):
        if isinstance(result, Exception):
            failed.append({"item": item, "error": str(result)})
        else:
            successful.append(result)

    return {"successful": successful, "failed": failed}
```

### 2. 批次處理

```python
async def batch_llm_calls(prompts: List[str], batch_size: int = 10):
    """分批處理 LLM 請求"""
    results = []

    for i in range(0, len(prompts), batch_size):
        batch = prompts[i:i + batch_size]

        # 並發處理批次
        batch_results = await asyncio.gather(*[
            llm.generate(prompt)
            for prompt in batch
        ])

        results.extend(batch_results)

        # 批次間延遲，避免限流
        if i + batch_size < len(prompts):
            await asyncio.sleep(1)

    return results
```

### 3. 連接池

```python
from playwright.async_api import async_playwright
import asyncio

class BrowserPool:
    def __init__(self, size: int = 5):
        self.size = size
        self.browsers = asyncio.Queue(maxsize=size)

    async def initialize(self):
        """初始化瀏覽器池"""
        playwright = await async_playwright().start()

        for _ in range(self.size):
            browser = await playwright.chromium.launch()
            await self.browsers.put(browser)

    async def acquire(self):
        """獲取瀏覽器"""
        return await self.browsers.get()

    async def release(self, browser):
        """釋放瀏覽器"""
        await self.browsers.put(browser)

    async def close_all(self):
        """關閉所有瀏覽器"""
        while not self.browsers.empty():
            browser = await self.browsers.get()
            await browser.close()

# 使用
pool = BrowserPool(size=3)
await pool.initialize()

browser = await pool.acquire()
try:
    page = await browser.new_page()
    # 使用頁面
finally:
    await pool.release(browser)
```

---

## 安全最佳實踐

### 1. 密鑰管理

```python
from cryptography.fernet import Fernet
import os

class SecretManager:
    def __init__(self):
        # 從環境變數讀取加密密鑰
        key = os.getenv("ENCRYPTION_KEY")
        if not key:
            raise ValueError("ENCRYPTION_KEY not set")

        self.cipher = Fernet(key.encode())

    def encrypt(self, data: str) -> str:
        """加密敏感數據"""
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt(self, encrypted: str) -> str:
        """解密數據"""
        return self.cipher.decrypt(encrypted.encode()).decode()

# ❌ 不要這樣
API_KEY = "sk-12345"  # 硬編碼

# ✅ 應該這樣
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("API key not configured")
```

### 2. 輸入驗證

```python
from pydantic import BaseModel, validator, ValidationError

class InvoiceData(BaseModel):
    invoice_number: str
    amount: float
    date: str

    @validator('amount')
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v

    @validator('invoice_number')
    def invoice_number_format(cls, v):
        if not v.startswith('INV-'):
            raise ValueError('Invalid invoice number format')
        return v

# 使用
try:
    invoice = InvoiceData(
        invoice_number="INV-001",
        amount=100.0,
        date="2024-01-01"
    )
except ValidationError as e:
    print(f"Validation error: {e}")
```

### 3. Prompt 注入防護

```python
def sanitize_prompt(user_input: str) -> str:
    """清理用戶輸入，防止 Prompt 注入"""
    # 移除可能的注入指令
    dangerous_patterns = [
        "ignore previous instructions",
        "disregard all",
        "forget everything",
        "system:",
        "assistant:",
    ]

    cleaned = user_input
    for pattern in dangerous_patterns:
        cleaned = cleaned.replace(pattern, "")

    # 限制長度
    max_length = 1000
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length]

    return cleaned

# 使用
user_input = request.get("query")
safe_input = sanitize_prompt(user_input)

prompt = f"Process this user query: {safe_input}"
```

---

## 成本優化

### 1. Token 計數與優化

```python
import tiktoken

class CostOptimizedLLM:
    def __init__(self, llm: BaseLLM):
        self.llm = llm
        self.encoding = tiktoken.encoding_for_model("gpt-4")

    def count_tokens(self, text: str) -> int:
        """計算 Token 數量"""
        return len(self.encoding.encode(text))

    async def generate_with_budget(
        self,
        prompt: str,
        max_cost_usd: float = 0.01
    ) -> str:
        """在預算內生成"""
        tokens = self.count_tokens(prompt)

        # GPT-4 價格：$0.03/1K tokens
        estimated_cost = (tokens / 1000) * 0.03

        if estimated_cost > max_cost_usd:
            raise ValueError(f"Estimated cost ${estimated_cost:.4f} exceeds budget")

        return await self.llm.generate(prompt)

    async def compress_prompt(self, prompt: str, target_tokens: int) -> str:
        """壓縮 Prompt"""
        current_tokens = self.count_tokens(prompt)

        if current_tokens <= target_tokens:
            return prompt

        # 使用 LLM 壓縮
        compression_prompt = f"""
Compress the following text to approximately {target_tokens} tokens
while keeping the key information:

{prompt}

Compressed version:
"""

        return await self.llm.generate(compression_prompt)
```

### 2. 智能模型選擇

```python
class AdaptiveLLM:
    def __init__(self):
        self.gpt4 = OpenAILLM(model="gpt-4")  # 強大但昂貴
        self.gpt35 = OpenAILLM(model="gpt-3.5-turbo")  # 便宜

    async def generate(self, prompt: str, complexity: str = "auto") -> str:
        """根據複雜度選擇模型"""

        if complexity == "auto":
            complexity = await self._assess_complexity(prompt)

        if complexity == "high":
            return await self.gpt4.generate(prompt)
        else:
            return await self.gpt35.generate(prompt)

    async def _assess_complexity(self, prompt: str) -> str:
        """評估任務複雜度"""
        # 簡單規則
        if len(prompt) > 1000:
            return "high"

        keywords = ["analyze", "complex", "detailed", "explain"]
        if any(kw in prompt.lower() for kw in keywords):
            return "high"

        return "low"
```

---

## 常見反模式

### ❌ 1. 過度使用 LLM

```python
# 不要對簡單任務使用 LLM
result = await llm.generate("Add 2 + 2")  # 浪費！

# 應該直接計算
result = 2 + 2
```

### ❌ 2. 忽略錯誤處理

```python
# 危險！
async def process():
    data = await llm.generate(prompt)  # 可能失敗
    save_to_db(data)  # 可能失敗

# 正確做法
async def process():
    try:
        data = await llm.generate(prompt)
    except Exception as e:
        logger.error(f"LLM failed: {e}")
        return None

    try:
        save_to_db(data)
    except Exception as e:
        logger.error(f"DB save failed: {e}")
        # 重試或隊列處理
```

### ❌ 3. 同步阻塞

```python
# 不要在異步代碼中使用同步調用
async def bad_example():
    result = llm.generate_sync(prompt)  # 阻塞整個事件循環！

# 應該
async def good_example():
    result = await llm.generate(prompt)  # 非阻塞
```

### ❌ 4. 硬編碼配置

```python
# 不要
API_KEY = "sk-12345"
MAX_RETRIES = 3

# 應該
API_KEY = os.getenv("API_KEY")
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
```

---

## 總結檢查清單

### 代碼質量 ✅

- [ ] 遵循單一職責原則
- [ ] 使用依賴注入
- [ ] 配置外部化
- [ ] 添加類型註解
- [ ] 編寫文檔字符串

### 錯誤處理 ✅

- [ ] 分層異常設計
- [ ] 實現重試機制
- [ ] 添加日誌記錄
- [ ] 優雅降級
- [ ] 斷路器保護

### 性能 ✅

- [ ] 使用異步 I/O
- [ ] 並發處理
- [ ] 實現緩存
- [ ] 連接池管理
- [ ] 批次處理

### 安全 ✅

- [ ] 密鑰加密存儲
- [ ] 輸入驗證
- [ ] Prompt 注入防護
- [ ] 最小權限原則
- [ ] 定期安全審計

### 成本 ✅

- [ ] Token 計數
- [ ] 模型選擇策略
- [ ] Prompt 優化
- [ ] 緩存重用
- [ ] 預算控制

---

下一步閱讀：
- [use-cases.md](./use-cases.md) - 實際應用案例
- [architecture.md](./architecture.md) - 系統架構設計
- [tutorial-part3-advanced.md](./tutorial-part3-advanced.md) - 進階技巧
